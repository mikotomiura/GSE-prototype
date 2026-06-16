# 設計 v1（退避版） — adaptive-baseline (A+C, 比例維持, セッション内, IME context 単位)

## 確定済み設計判断（ユーザー合意）

1. **保持単位**: IME context 単位（`coding` / `writing` の 2 系統を状態変数化）。
   新規のタスク境界検出は実装しない（既存 `ime_open` を代理に使う）。
2. **バンドモデル**: 比例維持 `φ=(x−β)/(κ·β)` + κ 微調。固定バンド化はしない。
3. **永続化**: セッション内のみ。プロセス再起動で母集団 prior から再 warmup。

## 実装アプローチ

`need = p_stuck` も HMM も触らず、`calculate_latent_axes` が `phi` に渡す **β を
「ハードコード定数」から「context ごとの状態変数」へ昇格**させる。状態変数は
**苦闘サンプルを除外した流暢サンプルのみ**から **遅い EWMA** で更新する。

### A: 緩やか適応（EWMA）
context ごとに β ベクトル `{f1,f3,f4,f5,f6}` を保持し、各 update で:

```
β_ctx ← α_slow · x_step + (1 − α_slow) · β_ctx     (gate を通過した時のみ)
```

- `α_slow ≈ 0.02–0.05`（axes EWMA の 0.3 よりはるかに遅い。Plan で実測較正）。
- `x_step` は当該ステップの特徴量（F1 は既に 30s 窓中央値なのでステップ内では頑健）。

### C: 頑健統計 + 更新ゲート（汚染対策の本体）
- **更新ゲート**: `update()` 冒頭で取得できる *取り込み前* の Stuck 確率
  `old_probs[2]`（`engine.rs:405`）を信号に、`old_probs[2] >= GATE` の時は β を更新しない。
  → 苦闘中の遅い打鍵が基準を汚染しない（鶏卵問題の回避：β は「流暢」と既に
  信じている時のみ学習する）。`GATE` 初期値 0.50 程度（Plan で較正）。
- **データ実在ゲート**: silence 合成特徴 (f1=2000) では更新しない。`update_silence()`
  経路は β を一切更新しない（沈黙は流暢サンプルでない）。
- **外れ値クランプ**: `x_step` を `[β/η, β·η]`（例 η=3）にクランプしてから EWMA に入れ、
  単発スパイクの影響を抑える（ステップ内中央値の上にさらに頑健化）。

### warmup / cold-start
- β 初期値 = 現状の母集団定数（coding=150ms 等）を **prior** として流用 → 起動直後の
  挙動は現状と同一。これにより回帰リスクを最小化しつつ徐々に本人値へ収束。
- warmup 中（更新回数が閾値未満）は α を通常より速めても良いが、初版は固定 α_slow で単純化。

### κ 再調整
- β が母集団値から動くと飽和点 `β·(1+κ)` がズレ、感度レンジが変化（requirement 参照）。
- 初版は **κ=2.0 維持**（比例モデルなので本人比レンジは保たれる）。β 適応の効果を
  オフライン検証で確認後、必要なら κ を調整。κ は `phi` の `const` から `calculate_latent_axes`
  が渡す引数化を検討（context 別 κ を将来可能にするため）。初版は据え置き可。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/engine.rs`
  - `CognitiveStateEngine` に `adaptive_beta: Arc<Mutex<BetaState>>` フィールド追加
    （`BetaState { coding: BetaSet, writing: BetaSet }`、`BetaSet{f1,f3,f4,f5,f6}`）。
  - `new()` で母集団定数を初期値に設定。`reset()` で母集団定数へ戻す。
  - `calculate_latent_axes`: ハードコード定数の代わりに `adaptive_beta` から context 別 β を読む。
  - `update()`: 冒頭の `old_probs[2]` を gate に、データ実在・外れ値クランプを経て β を EWMA 更新。
  - `HMM_VERSION` を **bump**（phi 入力の数値挙動が変わる → ゴールデン更新が必要）。
- `src-tauri/src/analysis/features.rs`
  - `phi` の κ 引数化（任意・初版見送り可）。β 更新ヘルパ（クランプ＋EWMA）を追加する場合はここ。

### 新規作成するファイル
- なし（engine.rs 内の小構造体で収まる見込み）。必要なら `analysis/baseline.rs` に分離。

## 影響範囲
- **再現性 / ゴールデン**: `HMM_VERSION` bump 必須。`engine.rs` の `#[cfg(test)] tests`
  スナップショット、`gse-replay` のゴールデンスナップショットを更新（development-guidelines §10）。
- **スレッドモデル**: `Arc<Mutex<>>` 追加のみ。フックコールバックは触らない（制約4遵守）。
- **OS 依存**: analysis 層に閉じる（制約：analysis で OS API 禁止を遵守）。
- **schema**: NDJSON schema は変えない（β は内部状態。診断ログに出すなら別途 schema 反映）。
  → 初版は `UpdateDiagnostics` に β を追加するか要検討（出すなら emit_schema/CI drift 対応）。

## 既存パターンとの整合性
- `axes_ewma` / `display_probs` と同じ `Arc<Mutex<>>` + ポイズニング対策パターンを踏襲。
- EWMA リテラル `(1.0 - α)` 問題（engine.rs:18-24）に注意：α_slow も定数抽出せずリテラル維持か、
  再現性への影響を decisions.md に明記。
- `// TUNE:` マーカーで全チューニング点を列挙可能に保つ。

## テスト戦略
- **単体**: (1) gate が効く＝高 p_stuck サンプルで β が動かない。(2) 流暢サンプル連続で
  β が目標値へ収束。(3) silence では更新されない。(4) 外れ値クランプ。(5) reset で prior 復帰。
- **回帰**: 起動直後（warmup 前）は現状と bit 一致に近いこと（prior = 旧定数）。
- **オフライン検証**: 合成または実セッションで「遅いが流暢な人」の friction 底上げが減ること、
  「速い人」の検出漏れが改善することを `gse-replay --metrics --json` の before/after で比較。
- ゴールデンスナップショット更新と HMM_VERSION 整合。

## ロールバック計画
- β 適応は `calculate_latent_axes` の読み出し元差し替えが中心。`adaptive_beta` を常に prior
  固定にする feature flag / 定数で旧挙動へ即時復帰可能にする（初版に組み込むか要検討）。
- HMM_VERSION を戻し、ゴールデンを旧版へ revert。

## Plan で確定する残パラメータ
- `α_slow`、`GATE`、外れ値クランプ係数 η、warmup 更新回数閾値、κ 据え置き可否。
- 診断ログ（β）を出すか（schema/CI 影響）。
- ロールバック feature flag を初版に入れるか。
