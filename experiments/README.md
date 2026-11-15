# experiments/ — 科学的実験ログのルート

このディレクトリは GSE の**科学的実験**を記録する（`.steering/` の実装作業記録とは別系統）。
規約の単一真実源は `docs/experiment-tracking.md`。発火層は `reproducibility-discipline` skill。

## 使い方

各実験は `experiments/<YYYYMMDD>-<exp-name>/` に隔離し、`docs/experiment-tracking.md` の
ディレクトリ規約（config / SEED / data.md / env.md / run.sh / results/ / metrics.json / notes.md）に従う。

## GSE での代表的な実験種別

- **較正スモーク** — criterion label（ランダムプローブ）と二軸出力の妥当性（C-index ゲート、H1/H2）
- **HMM チューニング / ablation** — 閾値・α・β の感度（HMM_VERSION を固定）
- **アウトカム指標の閾値感度** — v0.4 自力回復率・AI 依存度の閾値変化に対する頑健性（H3）

## 注意

- NDJSON 生ログ・キーストローク内容はコミットしない（data-privacy SSOT）。入力は gse-dataset の
  commit hash で `data.md` に固定参照する。
- 共有は集計 JSON のみ（`metrics.json` / `*.calib.json` / `cohort.json`）。
- 各実験の `notes.md` は必ず `docs/research-positioning.md` §4.1 の仮説（または事前登録の項目番号）と
  `docs/preregistration-v0.3.md` の PreReg 番号にリンクする。
