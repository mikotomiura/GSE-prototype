# 設計（採用版） — ハイブリッド: v2 背骨 + v1 薄テスト層

> **採用経緯**: `/reimagine` プロセスで v1（基盤先行）と v2（介入価値駆動）を独立生成。
> 比較（`comparison.md`）の結果、**v2 のリプレイ CLI 背骨を採用しつつ、v1 の薄いテスト層と Lv3 Phase 4 を保持するハイブリッド**を選択。
> v1/v2 の原案は `design_v1.md` / `design_v2.md` として参考保管。

---

## 実装アプローチ（4 原則）

### 原則 A — Replay-as-Truth
**セッションリプレイ CLI をテスト基盤の中心に据える**。ゴールデン NDJSON → engine 再実行 → `Feat` 出力の byte-equal 比較が、ユニットテスト・統合テスト・回帰テスト・GT 評価・パラメータチューニングの **5 役を 1 ツールで兼ねる**。

### 原則 B — Minimal Unit Test Layer
リプレイ CLI の「純粋性」を守るための最小限のユニットテストだけ書く:
- `phi()` — 境界値
- `FeatureExtractor::calculate_features()` — 既知入力 → 期待特徴量
- `make_silence_observation()` — 沈黙秒数 → 期待値
- 遷移行列・放出行列のスナップショット（意図しないドリフト検出）

**E2E テスト・フロントエンドテスト・統合テストは書かない**（費用対効果が合わない）。

### 原則 C — Intervention-Value-Driven Ordering
Phase 優先順位は「介入判断の precision を測れる状態に最短で到達する」ことから逆算する。
- Phase 0: リプレイ CLI（測定基盤）
- Phase 1: GT（測定軸）
- Phase 2: Synthetic Friction 再設計（指標を動かす）
- Phase 3: LR 判断ゲート
- Phase 4: Lv3（介入の幅を広げる）

### 原則 D — Keep What Works, Rename What's Confusing
「沈黙の二重パス」は統一リファクタしない（新バグリスク > 保守利益）。**3 状態機構（Typing / Transition / Silence）として明示的にコメントリネーム + `docs/architecture.md` 追記**のみ。
パラメータ外部化も却下。`// TUNE:` マーカー統一で見通しを確保。

---

## 元ロードマップ 8 項目 + 欠落項目の最終判定

| # | 項目 | 判定 | 配置 |
|---|------|------|------|
| ① | Synthetic Friction 案B | ⚠️ 条件付き採用（閾値は φ 正規化後で GT 校正） | Phase 2a |
| ② | Ground Truth プロトコル | ✅ 採用（リアルタイム GT のみ先行、遡及は保留） | Phase 1 |
| ③ | 訓練/評価時系列分割 | ✅ 採用（`hmm_version` をメタに追加） | Phase 0 |
| ④ | Stage 2 LR | ⚠️ 条件付き採用（**入れない選択肢を対等**に扱う判断ゲート） | Phase 3 |
| ⑤ | Stage 3 XGBoost | ❌ 却下（データ不足・Rust デプロイ不可） | スコープ外 |
| ⑥ | Windows IME 追加特徴量 | ⚠️ 条件付き採用（シャドーモード。Windows のみ。macOS 保留） | Phase 2b |
| ⑦ | Lv3 Thought Scaffold | ✅ 採用（Phase 2 Go 達成後にのみ着手） | Phase 4 |
| ⑧ | Stuck 回復時間計測 | ✅ 採用（GT ログに `recovered_at` を同梱。独立タスク不要） | Phase 1 |
| A | テスト基盤 | ✅ 薄層採用 | Phase 0 |
| B | パラメータ外部化 | ❌ 却下（`// TUNE:` マーカーで代替） | — |
| C | セッションリプレイ CLI | ✅ 採用（最重要） | Phase 0 |
| D | 沈黙パスの二重構造 | ⚠️ 統一せず、リネーム + ドキュメント化 | Phase 0 |
| E | Lv1/Lv2 既存挙動の保護 | ✅ 採用（ゴールデンスナップショット差分で防衛） | Phase 0 |

---

## Phase 構造と依存関係

```
Phase 0: Replay & Guard  (2-3週)
   │
   ├──→ Phase 1: Ground Truth  (2週)
   │        │
   │        └──→ Phase 2a: Synthetic Friction 再設計  (1-1.5週)
   │                 │
   │                 └──→ Phase 3: LR 判断ゲート  (2週)
   │                          │
   └──→ Phase 2b: IME Shadow Features  (1週・2a と並列可)
                                            │
                                            └──→ Phase 4: Lv3 Scaffold + Feedback  (1-1.5週)
                                                     (Phase 2 Go 達成が前提)
```

**並列化**:
- Phase 0 完了後、Phase 1 と Phase 2b を並列で着手可
- Phase 2a は Phase 1 完了後。Phase 2b は GT を待たない

**合計見込み**: 7〜9 週（Phase 4 含む）

---

## 変更対象ファイル一覧

### 修正するファイル
- `src-tauri/src/analysis/engine.rs` — `// TUNE:` マーカー整理、ユニットテスト追加、`VERSION` 定数、Phase 3 で `lr_score()` メソッド + ラグバッファ追加
- `src-tauri/src/analysis/features.rs` — ユニットテスト追加、Phase 2a で沈黙ゲート挿入、Phase 0 で `TypingPath/TransitionPath/SilencePath` コメントリネーム
- `src-tauri/src/lib.rs` — 分析ループを `step()` 関数に抽出、`record_user_label` コマンド追加、Phase 2a で `last_active_features` 追加、沈黙 3 状態の明示コメント
- `src-tauri/src/logger.rs` — `LogEntry::UserLabel`, `LogEntry::ImeShadow` 追加、`hmm_version` をメタに追加
- `src-tauri/src/input/hook.rs` — Phase 2b で IME 用 Atomic 追加
- `src-tauri/src/input/hook_windows.rs` — Phase 2b で矢印キー / ESC カウント、`IME_SHOW` 時刻記録
- `src-tauri/src/input/ime_windows.rs` — Phase 2b で composition 時刻記録
- `src/components/Dashboard.tsx` — GT 3 択ボタン、回復時間表示、Phase 4 でフィードバック 2 択
- `src/App.tsx` — Phase 4 で Lv3 トリガーロジック
- `docs/architecture.md` — 沈黙 3 状態機構の明示セクション追加

### 新規作成するファイル
- `src-tauri/src/bin/replay.rs` — セッションリプレイ CLI
- `src-tauri/src/analysis/loop_step.rs` — 分析ループを純粋関数 `step()` として切り出し
- `src-tauri/tests/fixtures/flow.ndjson` / `incubation.ndjson` / `stuck.ndjson` — ゴールデン入力
- `src-tauri/tests/snapshots/flow.json` / `incubation.json` / `stuck.json` — ゴールデン期待出力
- `justfile`（または `xtask/`）— `just snapshot` / `just replay` コマンド
- `ml/train_lr.py` — Phase 3 の LR 学習スクリプト
- `ml/export_weights.py` — Phase 3 の Rust 定数エクスポート
- `src/components/ThoughtScaffold.tsx` — Phase 4 の Lv3 UI

### 削除するファイル
なし

---

## Phase 0 詳細設計: Replay & Guard

### 0.1 分析ループの純粋関数化

現状の `lib.rs:494-690` の分析スレッド本体は `Instant::now()` と `input::hook::IME_OPEN` グローバルに結合している。これを純粋関数として切り出す:

```rust
// 新規 src-tauri/src/analysis/loop_step.rs
pub struct AnalysisState {
    pub extractor: FeatureExtractor,
    pub last_event_time_ms: u64,      // Instant ではなく ms
    pub next_engine_update_ms: u64,
    pub presses_since_silence: u32,
    pub was_paused: bool,
    pub pressed_keys: HashSet<u32>,   // Windows リピート検出用
}

pub enum LoopInput {
    Key(InputEvent),
    ImeState { on: bool, active: bool },
}

pub struct StepOutput {
    pub log_entries: Vec<LogEntry>,
    pub feat: Option<FeatSnapshot>,   // Feat 相当のレコード（リプレイ比較用）
}

pub fn step(
    state: &mut AnalysisState,
    engine: &CognitiveStateEngine,
    input: Option<LoopInput>,
    now_ms: u64,
    ime_open: bool,
) -> StepOutput { ... }
```

プロダクション側の `lib.rs` は `step()` を `Instant::now().as_ms()` と `IME_OPEN.load()` を渡して呼ぶだけの薄いラッパーに書き換える。リプレイ側は NDJSON の `t` をそのまま渡す。

**注意点**:
- `engine.register_keystroke(is_backspace)` は `Arc<Mutex<>>` 経由の内部状態なので、`step()` は `engine: &CognitiveStateEngine` を借用すれば機能する
- `IME_OPEN` グローバルは引数化するだけで参照元は他にもある（IME ポーリングスレッド等）のでグローバル自体は残す
- `Instant` から `u64 ms` への変換は `Instant` の基準時刻をセッション開始時に固定し、差分を ms で持つ設計にする

### 0.2 リプレイ CLI

```
gse-replay <session.ndjson> [--snapshot <golden.json>] [--metrics] [--scatter]
```

動作:
1. NDJSON をタイムスタンプ順に読み込み
2. `Key` / `ImeState` / `UserLabel`（Phase 1 以降）をイベント列化
3. 新しい `AnalysisState` + `CognitiveStateEngine::new()` を作成
4. 1 秒刻みの仮想時刻で `step()` を繰り返し呼ぶ
5. 出力される `FeatSnapshot` 列を JSON として出力
6. `--snapshot` 指定時は byte-equal（f64 は 1e-9 以内）比較
7. `--metrics` 指定時は `UserLabel` と突き合わせて混同行列を出力

### 0.3 ゴールデンスナップショット 3 件

`tests/fixtures/` 配下:
- `flow.ndjson` — 既存セッションログから Flow 主体の 10 分を切り出し
- `incubation.ndjson` — Incubation 主体
- `stuck.ndjson` — Stuck 主体（バックスペース連打を含む）

`tests/snapshots/` 配下に初回実行で生成した `FeatSnapshot` 列の JSON を配置。以降、`cargo test` でこのスナップショットと byte-equal 比較する。

### 0.4 薄ユニットテスト層

```rust
// features.rs 内 #[cfg(test)]
#[test] fn phi_at_baseline_returns_zero() { assert_eq!(phi(0.06, 0.06), 0.0); }
#[test] fn phi_at_triple_baseline_clamps_to_one() { assert_eq!(phi(0.18, 0.06), 1.0); }
#[test] fn phi_with_zero_beta_returns_zero() { assert_eq!(phi(1.0, 0.0), 0.0); }
#[test] fn silence_below_2s_returns_none() { assert!(extractor.make_silence_observation(1.9).is_none()); }
#[test] fn silence_at_10s_f6_floor() {
    let f = extractor.make_silence_observation(10.0).unwrap();
    assert!((f.f6_pause_after_del_rate - 0.15).abs() < 1e-9);
    assert_eq!(f.f3_correction_rate, 0.0); // F3 は 15s から
}
// ... 8-12 本程度
```

```rust
// engine.rs 内 #[cfg(test)]
#[test] fn transition_matrix_snapshot() {
    let e = CognitiveStateEngine::new();
    // 遷移行列の 9 要素を serde_json でシリアライズし固定値と比較
}
#[test] fn emission_matrix_snapshot() { ... }
```

### 0.5 `hmm_version` 追加

```rust
// engine.rs
pub const HMM_VERSION: &str = "0.2.0";  // エンジン挙動を変えたら bump
```

`logger.rs` の meta エントリに `"hmm_version"` フィールドを追加:

```json
{"type":"meta","session_start":1712345678901,"hmm_version":"0.2.0"}
```

### 0.6 沈黙 3 状態の明示コメント + ドキュメント

`lib.rs:649-682` の 3 分岐にそれぞれラベルコメント:
- `// === TypingPath: バッファに実データあり + silence < 2s ===`
- `// === TransitionPath: バッファに実データあり + 沈黙 2s 以上 ===`
- `// === SilencePath: バッファ空 + 沈黙 2s 以上 ===`

`features.rs:230` のコメントも更新。`docs/architecture.md` に「沈黙 3 状態機構」セクションを追加し、各パスの閾値・α 値・設計意図を表で記載。

### Phase 0 Go/No-Go

- [ ] `cargo run --bin gse-replay tests/fixtures/flow.ndjson --snapshot tests/snapshots/flow.json` が一致
- [ ] `cargo test` で 10 本以上のユニットテストが PASS
- [ ] メタログに `hmm_version` が記録される
- [ ] `analysis/` が `Tauri` / `input::hook::IME_OPEN` グローバルに直接依存しない（loop_step.rs 経由で引数化）
- [ ] `docs/architecture.md` に沈黙 3 状態セクションがある

---

## Phase 1 詳細設計: Ground Truth

### 1.1 LogEntry 拡張

```rust
pub enum LogEntry {
    // 既存...
    UserLabel {
        timestamp: u64,
        label: UserLabel,           // Flow | Incubation | Stuck
        recovered_at: Option<u64>,  // Stuck ラベルのみ、自動補完
    },
}
```

NDJSON 出力:
```json
{"type":"user_label","t":1712345678901,"label":"stuck","recovered_at":1712345700123}
```

### 1.2 Tauri コマンド

```rust
#[tauri::command]
fn record_user_label(label: String, timestamp: u64) -> Result<(), String> {
    // LogEntry::UserLabel を送信
}
```

### 1.3 Dashboard GT ボタン UI

3 択ボタン（Flow / Incubation / Stuck）を Dashboard 下部に配置。5 秒ホールドで記録。**ホールド開始時に `engine.set_paused(true)`、離すか記録確定時に `engine.set_paused(false)`** を呼び、ホールド中の沈黙が HMM に影響しないようにする。

`engine.set_paused` は既存の IME ポーズ機構と同じフラグ。既に `lib.rs` で参照済みのため Tauri コマンド経由で露出させる（新規 `set_engine_paused(bool)` コマンド）。

### 1.4 Stuck 回復時間の自動補完

分析スレッドに `pending_stuck_label: Option<(u64, /* label_ts */)>` を追加。Stuck ラベルが送られたら記録開始。`p_flow > 0.5` が連続 10 秒続いたら `recovered_at` を記録してログに追記（後出しの `Feat` とは別の `UserLabel` 更新エントリ）。

**実装の簡便化**: 最初は「Stuck ラベル後、次の `p_flow > 0.5` 到達時刻」を単純に記録する（10 秒継続要件は Phase 2 で調整）。

### 1.5 `gse-replay --metrics`

出力:
```
Stuck Labels: 42
HMM p_stuck > 0.6 intervals: 58
True Positives: 35
False Positives: 23
False Negatives: 7
Precision: 0.603
Recall: 0.833
Median Detection Lead/Lag: +4.2s (HMM detects 4.2s after user)
Stuck Recovery Time (median): 34.0s
```

### Phase 1 Go/No-Go

- [ ] 10 セッション以上の GT 付きログが存在
- [ ] `gse-replay --metrics` で precision/recall と回復時間中央値が算出される
- [ ] ベースライン数値が `.steering/20260414-improvement-roadmap/baseline_metrics.md` に記録されている
- [ ] 5 秒ホールド中の HMM pause が実機確認済み

---

## Phase 2a 詳細設計: Synthetic Friction 再設計

### 2a.1 散布図分析

`gse-replay --scatter <session.ndjson>` で、`UserLabel` 付きセッションの「沈黙開始前 5 秒の平均 F3/F6（φ 正規化後）」と「その沈黙のラベル」をプロット用 CSV として出力。

### 2a.2 `last_active_features` の追加

`lib.rs` 分析スレッド（step 関数化後）に:

```rust
// silence_secs が 0 → 正値に遷移する瞬間の features を保存
if prev_silence_secs < 2.0 && silence_secs >= 2.0 {
    state.last_active_features = Some(features.clone());
}
```

### 2a.3 文脈条件ゲート

`lib.rs` の TransitionPath / SilencePath 内で:

```rust
let apply_friction = state.last_active_features.as_ref().map_or(false, |laf| {
    let phi_f3 = phi(laf.f3_correction_rate, beta_f3);
    let phi_f6 = phi(laf.f6_pause_after_del_rate, beta_f6);
    phi_f3 >= THRESHOLD_PHI_F3 || phi_f6 >= THRESHOLD_PHI_F6
});

if apply_friction {
    // 既存の F6/F3 フロア適用
} else {
    // フロア適用せず、実測値または 0 で update_silence
}
```

**初期閾値**: `THRESHOLD_PHI_F3 = 0.30` / `THRESHOLD_PHI_F6 = 0.20`（GT データで校正）

**閾値は φ 正規化後の値で判定**（生の F3/F6 ではない）ため、β_coding / β_writing で自動的に適切にスケールする。

### 2a.4 回帰テストと校正

1. Phase 0 のゴールデンスナップショットを新パラメータで再実行 → 差分確認
2. Phase 1 の GT 付き全セッションで `gse-replay --metrics` → precision 低下がないことを確認
3. 差分を `.steering/20260414-improvement-roadmap/phase2a_results.md` に記録

### Phase 2a Go/No-Go

- [ ] Stuck precision が変更前から **低下していない**（同等または改善）
- [ ] 思考中沈黙（Incubation ラベル）の Stuck 誤検出率が減少
- [ ] ゴールデンスナップショットの差分が意図通り（承認記録あり）
- [ ] 閾値を定数として記録し、根拠となる GT データを `.steering/` に添付

---

## Phase 2b 詳細設計: IME Shadow Features（並列トラック）

**Windows のみ**。macOS は明示的に保留（TCC・dispatch_sync 制約）。

### 2b.1 Composition Dwell Time

`hook.rs` に:
```rust
pub static IME_COMPOSITION_START_MS: AtomicU64 = AtomicU64::new(0);
```

`hook_windows.rs` の WinEvent コールバック内で:
- `EVENT_OBJECT_IME_SHOW` 受信時 → 現在時刻を store
- `EVENT_OBJECT_IME_HIDE` 受信時 → 差分を計算してログ送信

### 2b.2 Candidate Navigation Count

`hook.rs` に:
```rust
pub static IME_CANDIDATE_NAV_COUNT: AtomicU32 = AtomicU32::new(0);
```

`hook_windows.rs` の `LowLevelKeyboardProc` 内で、`IME_ACTIVE.load() == true` かつ矢印キー（VK_UP/DOWN/LEFT/RIGHT）なら counter をインクリメント。

### 2b.3 Abandon Rate

同様に `IME_ABANDON_COUNT`（ESC 押下 during `IME_ACTIVE`）。

### 2b.4 LogEntry::ImeShadow

```rust
pub enum LogEntry {
    // ...
    ImeShadow {
        timestamp: u64,
        dwell_ms: u64,
        candidate_nav_count: u32,
        abandon: bool,
    },
}
```

IME_HIDE 時に 1 エントリ送信。

### 2b.5 HMM 統合は行わない

**重要**: Phase 2b はログのみ。HMM の X/Y 軸や放出行列には一切触らない。分布分析は Phase 3 前半（IME 特徴量の分布が LR の特徴量として価値があるか判断）。

### Phase 2b Go/No-Go

- [ ] Windows で 5 セッション以上の `ImeShadow` ログが取得されている
- [ ] HMM の既存出力に差分がない（Phase 0 ゴールデン再実行で一致）
- [ ] macOS ビルドが壊れていない（`#[cfg(target_os = "windows")]` 分離）

---

## Phase 3 詳細設計: LR 判断ゲート

**重要方針**: Phase 3 は「LR を入れる Phase」ではなく **「LR を入れるべきかデータで判断する Phase」**。「入れない」という決定も正当な成果。

### 3.1 Python 学習パイプライン

`ml/train_lr.py`:
- GT 付き NDJSON を読み込み
- 特徴量: `[phi(f1), phi(f3), phi(f4), phi(f5), phi(f6), delta_ewma_x_t5, delta_ewma_y_t5]` + Phase 2b の IME シャドー特徴量（オプション）
- ラベル: `UserLabel.label`（3 クラス）
- 時系列 80/20 分割
- L2 正則化強め（C=0.1）
- Leave-One-Session-Out CV で F1 スコア算出

### 3.2 ラグ特徴量バッファ

`engine.rs` に:
```rust
pub struct CognitiveStateEngine {
    // 既存...
    axes_history: Arc<Mutex<VecDeque<(f64, f64)>>>,  // 容量 5
}
```

`update()` 内で `push_back` + `len() > 5` なら `pop_front`。

### 3.3 LR スコアリング

```rust
// engine.rs 末尾
// TUNE: LR weights (exported from ml/train_lr.py on YYYY-MM-DD)
const LR_W: [f64; 7] = [ /* 7 係数 */ ];
const LR_B: f64 = /* バイアス */;

impl CognitiveStateEngine {
    pub fn lr_score(&self, features: &Features, delta_x: f64, delta_y: f64) -> f64 {
        let x = [
            phi(features.f1, BETA_F1),
            phi(features.f3, BETA_F3),
            // ...
            delta_x,
            delta_y,
        ];
        let z: f64 = LR_W.iter().zip(x.iter()).map(|(w, xi)| w * xi).sum::<f64>() + LR_B;
        1.0 / (1.0 + (-z).exp())
    }
}
```

### 3.4 シャドーモード統合

`lib.rs` で `lr_score` を呼び、`LogEntry::Feat` に `lr_stuck: f64` フィールドを追加（後方互換のため optional フィールドとして）。**介入判断には使わない**（HMM 単独で動作）。

### 3.5 Go/No-Go 判定

`gse-replay --metrics --lr` で:
- HMM 単独の precision/recall
- HMM AND LR（`p_stuck > 0.6 AND lr_stuck > 0.6`）の precision/recall

**Go 条件**:
- precision が 5% 以上改善
- recall が 3% 以上悪化していない

**No-Go 時**: LR を介入判断から外し、シャドーログのみ継続。`.steering/20260414-improvement-roadmap/phase3_lr_decision.md` に「入れない判断」を記録して Phase 3 を閉じる。これは失敗ではなく正当な成果。

### Phase 3 Go/No-Go

- [ ] GT 付きセッションが 50 件以上ある（不足なら Phase 1 へ戻る）
- [ ] Go または No-Go の明示的な判定文書が存在
- [ ] LR シャドースコアがログに記録されている

---

## Phase 4 詳細設計: Lv3 Thought Scaffold + Feedback

**前提条件**: Phase 2a で Stuck precision の改善が確認されていること（介入判断の精度が上がる前に介入種類を増やさない）。

### 4.1 ThoughtScaffold.tsx

```tsx
const QUESTIONS = [
    "何に困っていますか？",
    "別の角度からはどう見えますか？",
    // ... 20 問
];
// Wall 解除後に 10 秒間表示、ランダム選択
```

`App.tsx` の Wall 解除イベント（`sensor-accelerometer: "move"`）受信後に 10 秒間表示。

### 4.2 フィードバック収集

Lv1 Nudge / Lv2 Wall / Lv3 Scaffold 発動後に「助かった / 邪魔だった」の 2 択ボタンを 30 秒間表示。

```rust
pub enum LogEntry {
    // ...
    InterventionFeedback {
        timestamp: u64,
        intervention: String,  // "nudge" | "wall" | "scaffold"
        helpful: bool,
    },
}
```

### Phase 4 Go/No-Go

- [ ] Phase 2a で Stuck precision 改善が確認されている
- [ ] Lv3 がユーザーテスト 3 セッションで動作確認済み
- [ ] フィードバックログが収集できている

---

## 既存パターンとの整合性

- **`#[cfg(target_os = "windows")]`**: Phase 2b の IME 追加特徴量は既存のプラットフォーム分岐パターンに従う
- **`LogEntry` enum の追加**: 既存の `Feat` / `ImeState` 同様、enum バリアント追加で後方互換を保つ
- **`AtomicU64 / AtomicU32` in hook.rs**: 既存の `IME_OPEN` / `IME_ACTIVE` と同じ場所・同じパターン
- **CLAUDE.md 制約 (3)**: フックコールバックでは Atomic 操作のみ（Phase 2b の counter 増加はこれに準拠）
- **`tracing`**: `println!` は使わず `tracing::info!` / `debug!` のみ

---

## テスト戦略

### 単体テスト（Phase 0 で導入）
- `features.rs`: phi 境界値 / 既知入力 → 期待特徴量 / silence observation の秒数別挙動（10 本程度）
- `engine.rs`: 遷移・放出行列のスナップショット / ペナルティビン遷移 / `register_keystroke` の BS ストリーク（5 本程度）

### 統合テスト（Phase 0 で導入、リプレイが実質これを兼ねる）
- ゴールデン NDJSON 3 件 → `FeatSnapshot` 出力の byte-equal（1e-9 許容）
- Phase 2a / 3 の変更前後で同一ゴールデンに対する差分を明示的に承認

### E2E テスト / フロントエンドテスト
**作らない**。UI 変更は手動確認。

### 回帰保護
Phase 1 以降の全変更は `cargo test` でスナップショット比較が PASS することが必須。変更意図がある場合はスナップショットを更新 + `.steering/` に根拠を記録。

---

## ロールバック計画

### Phase 0
- テスト追加と関数抽出のみで既存挙動を変えない設計
- `step()` 関数化により挙動が変わった場合、変更直前の commit に revert 可能
- ゴールデンスナップショットは純粋化前に取得しておき、前後で一致することを確認

### Phase 1
- `LogEntry::UserLabel` の追加は後方互換（既存パーサは未知 type を無視）
- GT ボタン UI は Dashboard の追加コンポーネントのみ、外すのは容易

### Phase 2a
- 文脈条件ゲートは `apply_friction = true` デフォルトに設定すれば旧挙動に戻る
- 定数 `THRESHOLD_PHI_F3` / `THRESHOLD_PHI_F6` をいじるだけで挙動調整可能
- 悪化した場合は即 revert

### Phase 2b
- Windows 限定の追加ログのみ。HMM には触らないので影響ゼロ
- ロールバックは該当コミットの revert のみ

### Phase 3
- シャドーモード前提。介入判断に使うのは Go 判定後のみ
- No-Go なら介入判断からは外す（ログ出力だけ残す選択も可）

### Phase 4
- 追加コンポーネントのみ。`App.tsx` のトリガーフラグを false にすれば無効化

---

## 未解決事項（Phase 進行中に判断）

1. **遡及ラベリング UI を Phase 1.5 で追加するか** — Phase 1 完了時点で GT 収集量を見て判断
2. **IME 追加特徴量を HMM の X/Y 軸に統合するか** — Phase 3 の LR 分布分析結果で判断
3. **`hmm_version` の更新タイミング規約** — Phase 0 完了時に `CONTRIBUTING.md` に明文化
4. **ゴールデンスナップショット更新の承認プロセス** — 開発者セルフレビュー（単一ユーザー前提）。`.steering/` への記録で代替

## 実装で判明した事実（Phase 0 診断テスト層サイクル）

### 2026-04-14 追記

1. **EWMA α 系定数は抽出しない方針を確定**
   - 当初計画では `EWMA_ALPHA_NORMAL = 0.3` などをモジュール定数化する予定だった
   - 実装時に IEEE 754 の `1.0 - 0.3 ≠ 0.7`（bit パターンが異なる）ことを確認
   - 定数化すると compute 経路で ULP レベルの浮動小数点結果が変わり、既存セッションログ再現性が損なわれる
   - 方針: `// TUNE:` マーカーコメントでの列挙可能性のみを確保、compute 経路のリテラルは維持
   - 詳細は `decisions.md` の新規判断 11 を参照

2. **Skill ドキュメント (`hmm-analysis`) と実コードのドリフト発見**
   - Skill: `obs = y_bin * 5 + x_bin` ⚠️ 実コード: `x_bin * 5 + y_bin`
   - Skill: 通常 EWMA α=0.15 ⚠️ 実コード: α=0.3
   - Skill: ヒステリシス α=0.3 ⚠️ 実コード: α=0.40 / 0.60
   - 本サイクルでは修正しない（Skill 更新は本ロードマップ外）
   - 別タスク（Skill メンテナンスサイクル）で修正すべき

3. **`analysis/` は既に Tauri / logger 依存ゼロを確認**
   - P0-3 ゴール「`analysis/` に `Tauri` / `input::hook` グローバル直接依存がないこと」は既に達成済み
   - ただし `lib.rs:643` の `input::hook::IME_OPEN.load()` への依存は `lib.rs` 側 → `engine.rs` への `ime_open: bool` 引数渡しで既に分離済み
   - Phase 0 の次サイクル（loop step 抽出）ではこの分離を維持する

4. **code-reviewer MEDIUM 指摘（繰越分）**
   - M1: テスト用 `pub(crate)` アクセサ追加（現状 `transitions` などに直接アクセス）
   - M2: `calculate_features` の F4 / F6 / cutoff / 2000ms FT キャップのカバレッジ
   - M3: `update()` / `update_silence()` の挙動テスト（penalty→Stuck / IME ガード / silence α 境界）
   - ユーザー承認でいずれも次サイクルへ繰越済み
   - M3 は loop step 純粋化後に書く方が `Instant` / グローバル依存を避けられるため合理的

---

## 関連ドキュメント

- `GSE_改善分析_開発ロードマップ.md` — 元ロードマップ
- `design_v1.md` / `design_v2.md` / `comparison.md` — /reimagine の過程
- `docs/architecture.md` — 既存 HMM / フック / 沈黙パスの詳細（Phase 0 で 3 状態セクション追記）
- `docs/development-guidelines.md` — テスト方針（Phase 0 完了時に薄テスト層の方針を追記）
