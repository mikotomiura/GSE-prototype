# 設計 v2 — adaptive-baseline

## 確定済みプロダクト判断（ユーザー合意・固定）

1. 保持単位 = IME context（coding / writing）
2. バンドモデル = 比例維持 `φ=(x−β)/(κ·β)` + κ 微調
3. 永続化 = セッション内のみ

## 設計の中心思想（v2 の立脚点）

要件は β を「**ローリング窓の低位パーセンタイル / trimmed mean** で推定し、`p_stuck < GATE`
の**流暢サンプルのみ**から更新」と明記している。これを素直に実装する。さらに GSE の
再現性規約（`engine.rs` の数値挙動変更は `HMM_VERSION` bump + ゴールデン更新）を踏まえ、
**β を HMM エンジンの内部状態にせず、エンジンを `(features, β) → probs` の純関数に保つ**
ことを最優先とする。β の所有・学習はエンジン外（オーケストレーション層）に置く。

→ 2 つの責務を明確に分離する:
- **`CognitiveStateEngine`**: 純粋な推論器。β を「引数で受け取る」。自分では持たない。
- **`ContextBaseline`（新規）**: β の学習器。流暢サンプルを溜め、頑健統計で β を出す。

これは「β をエンジンに `Arc<Mutex>` で抱えさせ、`update()` 内の副作用で自己学習させる」
という素朴案を**意図的に採らない**。理由は (a) エンジンが自分の事前信念で自分の入力基準を
書き換える自己参照ループになり、テスト・再現が難しい (b) 純関数なら β を外から固定注入して
golden を取れる、の 2 点。

## 実装アプローチ

### 1. エンジンの純関数化（β の注入）
`calculate_latent_axes(&self, features, ime_open)` を
`calculate_latent_axes(features, beta: &BetaSet)` に変更（β を引数化、ime_open による
分岐は呼び出し側で β を選んで渡すことに置換）。`update()` / `update_silence()` も
`beta: &BetaSet` を受け取る。エンジンは β を保持しない。

```rust
pub struct BetaSet { pub f1: f64, pub f3: f64, pub f4: f64, pub f5: f64, pub f6: f64 }
```

### 2. ContextBaseline（新規 `analysis/baseline.rs`）— 頑健窓推定器
context ごとに、**受理した流暢サンプルの特徴量**を保持する有界リングバッファを持つ。

```rust
pub struct ContextBaseline {
    coding: FluentWindow,   // 各特徴量ごとの固定長リングバッファ
    writing: FluentWindow,
}
```

- β = バッファ上の **低位パーセンタイル（F1 等の "遅さ" 指標は p40 付近）または 20% trimmed mean**。
  「流暢時の中心〜やや速い側」を原点に取ることで、流暢時 φ≈0 を実現。
- 苦闘の遅い打鍵はそもそも受理されず（下記ゲート）、受理後も**窓のパーセンタイル**が
  外れ値（裾）を構造的に捨てるため、EWMA より汚染に強い（EWMA は受理した全値を積分する）。
- バッファ未充填（warmup）時は **母集団 prior 定数**を β として返す → 起動直後は現状と同一挙動。
- セッション内のみ。`reset()` でバッファを空（=prior）に戻す。

### 3. 受理ゲート（汚染対策の本体）— オーケストレーション層に置く
β 学習は `loop_step.rs` 側で、**確定後の報告状態**を使って判定する（エンジン内部の
事前信念ではなく、そのステップで実際に出力した p_stuck という最大情報量の信号を使う）:

```
受理条件 = (TypingPath である: 実打鍵かつ silence でない)
         ∧ (reported p_stuck < GATE)
         ∧ (直近 N ステップ連続で流暢: デバウンス)
```

- **silence / transition 経路は学習しない**（沈黙は流暢サンプルでない）。
- **デバウンス（N 連続流暢）**: 苦闘の合間の一瞬の凪で基準を学ばないための追加防御
  （v1 にない anti-contamination の上積み）。
- 受理されたステップの生特徴量だけが `ContextBaseline` のバッファに push される。

### 4. κ / 感度レンジ
比例モデル `κ·β` 維持（ユーザー決定）。初版 κ=2.0 据え置き。β が本人値へ動くと飽和点
`β(1+κ)` も本人比で動くため、本人比のレンジは保たれる。オフライン検証で過剰鈍化が
見えた場合のみ κ を調整（`phi` を κ 引数化しておき将来 context 別 κ も可能にする）。

## 変更対象

### 新規作成
- `src-tauri/src/analysis/baseline.rs` — `BetaSet` / `FluentWindow` / `ContextBaseline`
  （push・パーセンタイル算出・prior フォールバック・reset）。純粋ロジックで単体テスト容易。

### 修正
- `src-tauri/src/analysis/engine.rs`
  - `calculate_latent_axes` / `update` / `update_silence` を `beta: &BetaSet` 引数化。
  - β 関連の母集団定数は prior として `baseline.rs` へ移設（エンジンからは消す）。
  - `HMM_VERSION` bump（数値挙動変化）。
- `src-tauri/src/analysis/loop_step.rs`
  - 状態構造体に `ContextBaseline` を保持。各経路で context 別 β を取得しエンジンへ注入。
  - TypingPath で受理ゲート（p_stuck<GATE＋デバウンス）を評価し、流暢サンプルを push。
- `src-tauri/src/analysis/features.rs`
  - `phi` を κ 引数化（任意）。パーセンタイル / trimmed mean ヘルパは baseline.rs に置く。

## 既存パターンとの整合性
- 「エンジンは純粋、状態はオーケストレーション層が持つ」方向に寄せる。既存の
  `state.extractor` / `state.pre_silence_features`（loop_step）と同じ「state がサブ状態を所有」型。
- `Arc<Mutex>` はエンジンに増やさない（むしろ β を外出しして純化）。
- `// TUNE:` マーカー（GATE, N, percentile, α/κ）を集約。

## テスト戦略
- **baseline.rs 単体**（純ロジック・OS 非依存）:
  (1) prior フォールバック (空窓→母集団定数)。(2) 流暢サンプル投入で β が目標へ収束。
  (3) パーセンタイルが裾外れ値を捨てる。(4) reset で prior 復帰。
- **loop_step 受理ゲート**: 高 p_stuck では push されない / デバウンス未満では push されない /
  silence・transition では push されない。
- **engine 純関数**: 同一 (features, β) で決定的。β を prior 固定すると現行 golden と一致。
- **回帰**: warmup 前（窓未充填）は現状と bit 一致に近い。
- **オフライン**: `gse-replay --metrics --json` で遅い人/速い人の before/after。
- ゴールデン更新 + HMM_VERSION 整合。

## 影響範囲
- 再現性: HMM_VERSION bump、`engine.rs` スナップショット + gse-replay ゴールデン更新。
- 関数シグネチャ変更（calculate_latent_axes/update/update_silence）→ 呼び出し側 loop_step 改修必須。
- OS 依存なし（analysis 層に閉じる）。schema 不変（β を診断ログに出すなら別途反映）。

## ロールバック計画
- `ContextBaseline` を常に prior 返却モードにする flag で旧挙動へ即時復帰（純関数化により
  β=prior 固定＝完全な旧挙動を保証しやすい）。HMM_VERSION revert + ゴールデン revert。

## Plan 確定パラメータ（2026-06-07）

前提: エンジン更新は **1Hz ゲート**駆動（`lib.rs:752-770` の `next_engine_update_ms`）。
よって 1 update ≈ 1 秒。窓長・デバウンスはこの 1Hz 基準で実時間換算する。

| パラメータ | 確定値 | 根拠 |
|---|---|---|
| 窓容量 `W` | context ごと **256** 受理サンプル | 流暢 ≈4.3 分ぶんの本人分布。リング上書き |
| warmup 最小数 `W_min` | **32**（≈流暢 32 秒） | これ未満は prior 返却 |
| warmup ブレンド | `β = lerp(prior, learned, min(1, n/W_min))` | 充填途中の段差を防ぐ滑らか移行 |
| GATE（受理上限 p_stuck） | **0.40** | NUDGE 閾値 0.60 に安全マージン。介入域に入る前に学習停止 |
| デバウンス `N` | **連続 5** 流暢 update（≈5 秒） | 苦闘の合間の一瞬の凪で学習しない |
| 推定統計（friction系 F1/F3/F5/F6） | 窓の **p60** | わずかに中央値上。流暢→φ≈0 で偽 friction を抑制しつつ感度維持 |
| 推定統計（engagement系 F4: burst長） | 窓の **p35** | F4 は高いほど良い指標。本人比で「普段以下」を friction 扱いしないため下側に置く |
| β への追加 EWMA | **なし**（窓自体が平滑化） | `(1.0−α)` 浮動小数の再現性フットガン（engine.rs:18-24）を回避 |
| `κ` | **2.0 据え置き** | 比例モデル維持（ユーザー決定）。過剰鈍化が出たら調整。phi は κ 引数化のみ実施 |
| 診断ログ | β を `UpdateDiagnostics` に追加（**in-memory のみ**）。NDJSON schema は**変更しない** | schema/CI drift 回避。offline は replay 側で β を再計算 |

### 重要な補正（requirement の「低位パーセンタイル」表現を是正）
requirement は一律「低位パーセンタイル」と書いたが、特徴量には**向きがある**:
- **friction 方向**（高いほど苦闘: F1,F3,F5,F6）→ β は流暢分布の**上側 (p60)**。
  そうしないと「流暢時 φ≈0」が成立せず、是正したい原点バイアスが残る。
- **engagement 方向**（高いほど良い: F4）→ β は**下側 (p35)**。
これは decisions.md に design decision として明記する。

### 要較正（次セッションの実検証 / codex review 対象）
上記は妥当な初期値。`gse-replay --metrics --json` の before/after と実セッションで
`W`,`GATE`,`N`,`p60/p35` を較正する。特に p60/p35 の向き別パーセンタイルは
codex review で「軸セマンティクスとの整合」を重点的に叩く。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2（再生成案）
- 根拠: 要件忠実（窓パーセンタイル/流暢サンプル限定をそのまま実装）、再現性規約との相性
  （エンジン純関数化 → β=prior 注入で旧 golden と一致保証）、汚染耐性の厚さ（窓裾破棄＋
  デバウンス）、自己参照ループの排除。warmup の prior 流用と κ 据え置きは v1 から踏襲（ハイブリッド要素）。
