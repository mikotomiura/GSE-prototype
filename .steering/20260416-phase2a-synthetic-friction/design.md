# 設計 v2: 比例キャリーフォワード方式 (Proportional Friction Carry-Forward)

## 核心のアイデア: 閾値ゲートではなく、直前文脈の比例反映

現行の `make_silence_observation()` と TransitionPath の摩擦フロアは **時間ベースのランプ関数** で、沈黙前の実際の摩擦状態を一切参照しない。結果、思考中の生産的沈黙も Stuck 方向へ一律に引きずられる。

v2 では **沈黙に入る直前のタイピング特徴量を「文脈」として保存し、沈黙中の合成特徴量に比例反映** する。

- 直前にクリーンなタイピング (F3≈0, F6≈0) → 沈黙中の摩擦も≈0 → HMM は Inc/Flow に留まる
- 直前に修正が多い (F3 高) → 沈黙中の摩擦も高い → HMM は自然に Stuck 方向へ移動
- **新しい閾値定数は不要**。既存の F3/F6 値を直接使う

### ユーザー観察の反映: 「タイポ ≠ Stuck」

Windows ラベリングで判明した「CorrRate 高い + AvgFT 正常 = タイポ Flow」パターン。
v2 ではこれが自然に解決される:
- F3 (CorrRate) が高くても、φ(F1, β) が低い (正常な打鍵速度) なら X 軸 (Friction) は上がりきらない
- 沈黙に入っても、キャリーフォワードされる F3/F6 が φ 正規化後に見ると「流れの中のタイポ」レベルに収まる
- 結果として HMM observation は Stuck 領域に入らない

## 実装アプローチ

### 変更 1: `AnalysisState` に `pre_silence_features` を追加

`loop_step.rs` の `AnalysisState` に:

```rust
/// 沈黙開始直前の features スナップショット。
/// TypingPath → TransitionPath/SilencePath 遷移時にキャプチャ。
pub pre_silence_features: Option<Features>,
```

キャプチャタイミング: TypingPath (f1 > 0 && silence < 2s) を通るたびに上書き保存。
これにより「最後にアクティブにタイピングしていた時の特徴量」が常に最新状態で保持される。

```rust
// TypingPath 内
state.pre_silence_features = Some(features.clone());
```

### 変更 2: `make_silence_observation()` を文脈対応に

シグネチャ変更:

```rust
pub fn make_silence_observation(
    &self,
    silence_secs: f64,
    pre_silence: Option<&Features>,
) -> Option<Features>
```

摩擦フロアを「時間ベースのランプ」から「直前文脈の比例反映 + 時間減衰」に変更:

```rust
// 直前文脈がある場合: F3/F6 を比例キャリーフォワード
// 文脈なし (セッション冒頭等): 現行と同じ時間ベースランプにフォールバック
let (f3_synthetic, f6_synthetic) = match pre_silence {
    Some(ctx) => {
        // 直前の実測値をそのまま使い、時間とともに緩やかに増幅
        // 摩擦が高かった → 高い値がキャリーフォワード
        // 摩擦が低かった → 低い値がキャリーフォワード (≈0)
        let time_scale = ((silence_secs - 2.0) / 30.0).clamp(0.0, 1.0);
        let f3 = ctx.f3_correction_rate + time_scale * (1.0 - ctx.f3_correction_rate) * ctx.f3_correction_rate;
        let f6 = ctx.f6_pause_after_del_rate + time_scale * (1.0 - ctx.f6_pause_after_del_rate) * ctx.f6_pause_after_del_rate;
        (f3.clamp(0.0, 1.0), f6.clamp(0.0, 1.0))
    },
    None => {
        // フォールバック: 現行の時間ベースランプ (互換性維持)
        let f6_fb = if silence_secs >= 10.0 {
            (((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)).max(0.15)
        } else {
            ((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)
        };
        let f3_fb = if silence_secs >= 10.0 {
            (((silence_secs - 15.0) / 50.0).clamp(0.0, 1.0)).max(0.20)
        } else {
            ((silence_secs - 15.0) / 50.0).clamp(0.0, 1.0)
        };
        (f3_fb, f6_fb)
    },
};
```

**比例増幅の式**: `ctx_val + time_scale × (1.0 - ctx_val) × ctx_val`
- ctx_val = 0.0 → 0.0 (摩擦なし → 沈黙中も摩擦なし)
- ctx_val = 0.5 → 0.5 + 0.25×time → 最大 0.75 (中程度 → 緩やかに増加)
- ctx_val = 1.0 → 1.0 (最大摩擦 → そのまま維持)
- time_scale は 2s で 0.0、32s で 1.0 (30 秒かけて最大増幅)

### 変更 3: TransitionPath の摩擦フロアも文脈対応に

`loop_step.rs` の TransitionPath (L298-307) にも同じ原理を適用:

```rust
// TransitionPath 用: 既存 features に文脈ベースのフロアを適用
if silence_secs >= 8.0 {
    if let Some(ctx) = &state.pre_silence_features {
        let time_scale = ((silence_secs - 8.0) / 30.0).clamp(0.0, 1.0);
        let f6_floor = ctx.f6_pause_after_del_rate * time_scale;
        let f3_floor = ctx.f3_correction_rate * time_scale;
        features.f6_pause_after_del_rate = features.f6_pause_after_del_rate.max(f6_floor);
        features.f3_correction_rate = features.f3_correction_rate.max(f3_floor);
    } else {
        // フォールバック: 現行ロジック
        // ...
    }
}
```

### 変更 4: replay.rs の `step()` 呼び出し対応

replay.rs は `loop_step::step()` を呼ぶだけなので、`AnalysisState` の構造体変更に自動追従。
`pre_silence_features` の初期値は `None`。

## 変更対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `src-tauri/src/analysis/loop_step.rs` | `AnalysisState` に `pre_silence_features` 追加。TypingPath でキャプチャ。TransitionPath の摩擦フロアを文脈ベースに変更 |
| `src-tauri/src/analysis/features.rs` | `make_silence_observation()` のシグネチャ変更 + 文脈比例ロジック |
| `src-tauri/src/analysis/engine.rs` | 変更なし (閾値定数の追加不要) |
| `src-tauri/src/lib.rs` | 変更なし (loop_step が内部で処理) |
| `src-tauri/src/bin/replay.rs` | 変更なし (step() 呼び出しは同じ) |

## 既存パターンとの整合性

- `Features` 構造体は変更なし (フィールド追加なし)
- `AnalysisState` への `Option<Features>` フィールド追加は既存の `last_event_time_ms` 等と同パターン
- `make_silence_observation()` のシグネチャ変更は caller が 2 箇所のみ (loop_step.rs:310, engine tests)
- emission_matrix / transition_matrix は一切変更しない (ml-workflow 規約準拠)
- engine.rs に新定数を追加しない → ONNX 化 (Phase 3) との境界に影響なし

## テスト戦略

1. **ユニットテスト追加** (`features.rs`):
   - `make_silence_observation(10s, Some(clean_features))` → F3/F6 ≈ 0
   - `make_silence_observation(10s, Some(high_friction_features))` → F3/F6 ≈ 高い値
   - `make_silence_observation(10s, None)` → 現行と同一 (フォールバック互換)
   - 境界: silence_secs = 2.0, 8.0, 32.0 での値確認

2. **ゴールデンスナップショット再生成**:
   - `tests/snapshots/` の既存テスト → 期待値更新 (diff を steering に記録)
   - 変更理由: 沈黙中の observation が文脈依存になるため数値が変わる

3. **GT 回帰テスト**:
   - 全 10 セッション (Mac 5 + Win 5) で `gse-replay --segments` を実行
   - Stuck precision ≥ 0.77 (現行値) を維持
   - Inc→Flow 誤判定率の改善を確認

4. **NaN/Inf 耐性**:
   - `pre_silence` の F3/F6 が NaN/Inf の場合のガード (TryFrom で既に弾かれるが防御的に)

## v1 との主要な差異

| 観点 | v1 | v2 |
|------|----|----|
| アプローチ | φ 閾値による **二値ゲート** (apply / don't apply) | 直前文脈の **比例キャリーフォワード** |
| 新定数 | `THRESHOLD_PHI_F3`, `THRESHOLD_PHI_F6` (GT 校正が必要) | **なし** (既存の F3/F6 値を直接使用) |
| 変更ファイル数 | 4 (features, loop_step, engine, replay --scatter) | **2** (features, loop_step) |
| 閾値の脆弱性 | 閾値前後で不連続な振る舞い (0.29→0.30 で突然切り替わる) | **連続的**: F3=0.01 は微小、F3=0.50 は中程度 |
| 「タイポ≠Stuck」対応 | 閾値以下なら OK だが、重いタイポは Stuck と誤分類 | F3 が高くても比例反映なので自然にスケール |
| フォールバック | なし (文脈必須) | セッション冒頭の文脈なし時は現行ロジックにフォールバック |
| ONNX 化への影響 | engine.rs に定数追加 → ONNX 化時に考慮必要 | engine.rs 変更なし → ONNX 化に影響なし |

## リスク

1. **比例増幅式のチューニング**: `time_scale` の係数 (30 秒) が適切かは GT で確認が必要。ただし不適切でも連続的に振る舞うので閾値のような崖落ちリスクはない
2. **フォールバックパスの残存**: 文脈なし時に現行ロジックが残るため、セッション冒頭 (初回 TypingPath 前) の短い沈黙では旧動作。実運用上問題ないが、テストで明示確認が必要
3. **TransitionPath と SilencePath の一貫性**: 両者で同じ比例原理を使うが、具体的な time_scale や onset が異なる可能性。統一するか分離するかを実装時に決定

## 深掘り分析: F3 φ飽和と F6 弁別力

φ(F3, β_coding_F3≈0.05) は F3=0.10 で 0.5、F3≥0.25 で 1.0 に飽和する。
つまり **F3 の比例キャリーフォワードは φ 飽和域では差を出せない**。

「タイポ≠Stuck」を真に弁別するのは **F6 (pause-after-delete rate)**:
- タイポ Flow: 削除→即再入力 → F6 ≈ 0.00 → キャリーフォワード ≈ 0.00
- 本当の Stuck: 削除→停止 → F6 > 0.20 → キャリーフォワード ≈ 0.20+

X 軸で F6 の重みは 0.25。F6=0 vs F6=0.30 で X 軸に 0.25×φ(0.30) の差が出る。
これが比例キャリーフォワードの核心的な弁別メカニズム。

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: v2 (比例キャリーフォワード)
- 根拠: (1) 新定数ゼロで n=10 データへの過学習リスク回避 (2) 連続関数で閾値の崖なし (3) engine.rs 変更なし=ONNX 化パスがクリーン (4) F6 弁別力でタイポ≠Stuck を自然解決 (5) --scatter は defer (別タスク)
