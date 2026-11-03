# 環境

- macOS（Apple Silicon）・python3 3.14（標準ライブラリだけ・`-I` で実行）。
- 中間は `gse-replay`（SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`・p1-episode 1.2.0 の既定・極 baseline）で作る（停滞の分解と同じ）。
- 検出器と集計は `experiments/20261103-stall-candidates-c1c2c6/candidates.py` を読み込んで使う（変えない）。14 日の値は同じ実験の `results/candidates.json`。
- 乱数: `SEED`（H4a の副の並べ替えと H5 のブートストラップ）。
- 再現: `bash run.sh`（O1 の稼働中・10 分以内に更新されたファイルがあるとき・条件・コード・依存のファイルに未コミットの変更があるとき・`results/` に前の回の結果があるとき・前の回と入力が違うときは止まる。`started.py` が最初の 1 回の記録を受け持つ。判定に使うのは最初の 1 回だけ）。陽性対照 `python3 -I confirm.py --selftest`、変異 `python3 -I mutants.py`（40 種・無限ループになる変異は 60 秒で時間切れを赤と数える）。
