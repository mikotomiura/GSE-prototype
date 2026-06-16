# HANDOFF — 次セッション向け（codex review 実行）

## 状況
- 設計フェーズ完了。**実装は未着手**（コードは 1 行も書いていない）。
- v2 設計を採用済み。残パラメータも確定済み（`design.md` の「Plan 確定パラメータ」）。
- **codex はレート制限中**（2026-06-07 時点）。制限解除後に review を実行すること。
  関連: project memory `project_ci_exhausted`（GitHub Actions も枯渇、ローカル検証で代替）。

## 次セッションでやること（順番）
1. **codex review を design に対して実行**（下記「レビュー対象」「重点」を渡す）。
2. 指摘を `decisions.md` / `design.md` に反映。
3. 反映後に実装着手（`tasklist.md` の「実装」セクション）。

## レビュー対象ファイル（.steering/20260607-gse-v2-adaptive-baseline/）
- `requirement.md` — 背景・ゴール・スコープ・受け入れ条件
- `design.md` — **v2 採用版**（実装アプローチ + Plan 確定パラメータ）
- `decisions.md` — D-1〜D-6 の設計判断と根拠
- `design-comparison.md` — v1 vs v2 比較（棄却した v1 の理解用）
- `design-v1.md` — 棄却案（参考）

## codex review の重点（叩いてほしい順）
1. **D-3 の向き別パーセンタイル（friction=p60 / engagement F4=p35）が軸セマンティクスと
   整合するか**。φ=(x−β)/(κβ) と X(friction)/Y(engagement) の重み式
   （engine.rs:336-339）に照らし、各特徴量で「流暢時 φ≈0/望ましい寄与」が成立するか検算。
   ← 本設計で最も自信のない箇所。要件の「低位パーセンタイル」を是正した判断なので重点。
2. **D-1 エンジン純関数化の妥当性**: `calculate_latent_axes/update/update_silence` の
   シグネチャ変更が loop_step / lib.rs 呼出側に与える影響、`Clone` な engine 設計との整合。
3. **D-4 受理ゲートの信号選択**: 「確定後 report p_stuck」vs「取り込み前 old_probs」。
   1 step ラグ・収束安定性・苦闘汚染回避のトレードオフ。
4. **GATE=0.40 / N=5 / W=256 / W_min=32** の初期値が 1Hz 駆動下で妥当か（過学習/過鈍化）。
5. **再現性**: HMM_VERSION bump とゴールデン更新の運用（development-guidelines §10）に漏れがないか。
6. **汚染シナリオの抜け**: 「タスク冒頭が苦闘」「苦闘→短い凪→苦闘」で β が汚染されないか、
   デバウンス N=5 と GATE で本当に防げるか反例を探す。

## 参照すべき実コード（レビュー時のグラウンディング）
- `src-tauri/src/analysis/engine.rs:291-342`（calculate_latent_axes / β 定数）
- `src-tauri/src/analysis/engine.rs:348-472`（update 本体・old_probs・hysteresis）
- `src-tauri/src/analysis/features.rs:40-49`（phi）
- `src-tauri/src/analysis/loop_step.rs:294-344`（経路分岐 TypingPath/Transition/Silence）
- `src-tauri/src/lib.rs:752-770`（1Hz ゲート駆動）

## 注意
- 実装着手後は /reimagine 不可。codex review で大幅な設計変更が出たら、実装前に design を直す。
- analysis 層に OS 依存を持ち込まない（CLAUDE.md 制約）。
