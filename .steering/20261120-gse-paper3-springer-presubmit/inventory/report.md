# 公開前の棚卸し（論文 per-person-learning・S8 の 13 ディレクトリ）

対象: /Users/johnd/GSE-prototype-paper3/experiments/ の 13 ディレクトリ（worktree の HEAD 2130838f）。全 739 ファイル（__pycache__ を除く）。一覧は inventory.csv。

## (a) S8 の項目とディレクトリ
| S8 | ディレクトリ | 主なスクリプト |
|---|---|---|
| 解析 1 本人 hmm3 vs 共通 vs 連鎖 | 20261103-coauthor-per-person | perperson.py, hmm.py, build_obs.py |
| 解析 2 構造と τ≤1e4（CoAuthor・CS1） | 20261104-coauthor-ml-improve | ml.py, hmm2.py, hmm_b.py, data.py, logit.py, build_cs1_obs.py |
| 解析 3 τ 拡張と同時の選び | 20261104-timeseries-tau-extend | ml.py, hmm2.py, data.py |
| 解析 4 最頻値と平滑の効果 | 20261106-tau-mode-candidate | ml.py, hmm2.py |
| 確かめ 1 平滑なし等の記号化と擬似残差 (S13) | 20261107-unsmoothed-residual-check | build_variants.py, fit.py, residual.py |
| 確かめ 2 構造の補い (S12) | 見つからない（13 の中に無い。origin/main に experiments/20261107-structure-deficit-test があるが中身は未確認） | - |
| 確かめ 3 感度の合成・第 1 の帰無 (S10) | 20261110-per-person-sensitivity | synth.py, run_synth.py, analysis.py, run_add.py |
| 確かめ 4 合成への最頻値の分解 (S10) | 20261111-sensitivity-mode-decomposition | decomp.py, run_decomp.py |
| 確かめ 5 種 10・誤警報率 (S10) | 20261112-sensitivity-ten-seeds | ten.py |
| 確かめ 6 最頻値を候補に (S6) | 20261111-mode-in-selection | sel.py |
| 確かめ 7 平均で選ぶ (S6) | 20261111-objective-and-pause | obj.py |
| 確かめ 8 休止の割合 (S6) | 20261111-objective-and-pause | obj.py |
| 確かめ 9 書き手の二分 (S9) | 20261112-selection-split-and-smoothing | ab.py（計算 A） |
| 確かめ 10 平滑の確かめ一式 (S9) | 同上 | 基の平滑・共通だけの当て直し=compute.py+ab.py（B1）、連鎖の加える値=compute.py+ab.py（B2）、対称版=sym.py、対照=ctrl.py、入れ替え=r7.py の A |
| 確かめ 11 第 2 の帰無 (S10) | 20261113-null-from-shared | fit_m0.py, null.py |
| 確かめ 12 先頭の記号を除く (S4) | 20261112-selection-split-and-smoothing | r7.py の B |
| （前処理）CS1 の 30% 取り置きと変換 | 20261104-cs1-landscape | make_holdout_cs1.py, build_cs1.py（analyze_cs1.py は記述の俯瞰で S8 外） |
