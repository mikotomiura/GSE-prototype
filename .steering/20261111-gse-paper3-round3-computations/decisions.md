# 判断の記録

## 判断 1（2026-11-11）計算 3 の最頻値の置き方
- 決定: 列と候補の両方（研究者が AskUserQuestion で選んだ）。
- 理由: 候補に入れると R1 の言う混入（最頻値と共通の差が本人の上積みに見える）を手順の中で断て、列にすると分解と同じ量が主の表に出る。「本人 − 共通」の列も残して前の表と比べられるようにする。
- 却下案: 候補だけ・列だけ。

## 判断 2（2026-11-11・結果の前）計算 1 は CoAuthor の 20 複製だけ
- 決定: 分解は CoAuthor の複製（用量 13・構造 5・分布 2）に当て、CS1 の 7 複製には当てない。
- 理由: 実データの CS1 は 2 段で全員に τ = ∞ が選ばれ、mode の notes で分解を読んでいない（a = −b）。T1 の食い違いは CoAuthor の文。時間も約 3.5 時間に収まる。
- 却下案: CS1 も入れる（+7 本・約 8 時間・読みに使わない）。

## 判断 3（2026-11-11・結果の前）計算 2 は run_synth.py を変えない
- 決定: 足す 6 本は新しい `run_add.py`（`run_synth` を読み込む）で回す。
- 理由: 計算 1 が `run_synth.py` のハッシュを照らしているため。生成と当てはめのコードが前の 27 本と同じであることも、ファイルが変わらないことで示せる。code_hash は `scripts/*.py` 全体なので、ファイルが増えて変わる（条件の追記に書いた）。
- 却下案: `run_synth.py` の `plan()` に足す（最初に書いたが、計算 1 のハッシュが外れるので戻した）。

## 判断 4（2026-11-11・結果の前）計算 3 の D5 の「k の半分を超える」の分母
- 決定: 分母は、∞ が半分を超える書き手に選ばれた k を除いた k の数（`readings` の `counted`）。除いた後に k が 0 なら「全 k で ∞」。
- 理由: 条件の D5 は「∞ が…選ばれた k は…形の数に入れない」と書くので、数に入れない k を分母にも入れない読みに揃える。結果を見る前にコードで固定した。

## 判断 5（2026-11-11）計算の間に入れた外枠の直し（結果に依らないもの）
- 入れた所: T10（擬似残差は 5 × 5 の格子の 2 つの順序の軸の周辺で作り、長い削除の記号は除く。一次: `experiments/20261107-unsmoothed-residual-check/conditions.md` の擬似残差の節と `scripts/residual.py`）。T9（3.4 の解析の状態に後の確かめを 3 つ: 平滑の無い記号と擬似残差・構造の補い・感度の合成）。T8（データの声明を「code availability に挙げたコードで」に限り、code availability に S13・S14・S15 のコードを足す）。監査役 2-D（陰性対照の "below the CoAuthor remainder" を外す）・3-A（限界の ar3 の上端の文を原の記号化に限る）・3-B（限界の「閾値」に S15 の検出の規則を足す）。R2 m3（Aalbers の要約を本文の数値に合わせる。一次: 本文の「for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models」「for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline」「the median person-specific MAE for each idiographic model was slightly >0.8」）。R2 n1（分け方が場面しだいを Saeb と Little の両方に）。
- 論文の外: 論文 3 の requirement.md の範囲と受け入れ条件を、判断 11・17・21・24 で加えた試験に合わせた（監査役 3-4）。context-B は round 4 の依頼の準備で書き直す（3-D・3-E）。
- 残す: T1・T2・T3・T5〜T7・M3・2-B・最頻値・選びの目的と情報の経路は、計算の結果がそろってからまとめて直す。
