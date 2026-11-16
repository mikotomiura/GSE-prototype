# 設計

## アプローチ

- 論文 1 の確認と探索 X11 のコードを書き換えずに読み込み、停滞の onset だけを定義ごとに差し替える（`experiments/20261116-r1-definition-check/scripts/defcheck.py`）。
- onset の作り方: P1 は論文 1 の `cross_theta_writers`、P2〜P4 は論文 1 が replay を回し直した中間、N1〜N4 は論文 2 の `core.detect` を論文 1 の課題の単位に当てる。
- 検出器の妥当性は、`core.detect` が B0 と P2〜P4 の設定で replay の onset と 438 課題の全てで一致すること（K1）で確かめ、W と θ を 1 段ずらす変異で K1 が赤になることを見る（K4）。
- 主の定義で X11 と論文 1 の値を 1e-12 で再現すること（K2・K3）を、新しい値を読む前の門にする。

## 変更対象

- 新規: `experiments/20261116-r1-definition-check/`（conditions.md・SEED・data.md・env.md・run.sh・scripts/defcheck.py・results/・notes.md）
- 既存のファイルは変えない。

## テスト戦略

- 門 K1〜K5 と変異（conditions.md §K）。試しの走り（`DEFCHECK_ONLY`）は実験の dir の外に書く。
- 完了時に code-reviewer と /cross-review（Codex にはスクリプトと条件だけを渡し、結果の値・中間は渡さない）。
