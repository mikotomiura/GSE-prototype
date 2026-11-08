# JEDM 査読（manuscript round 5・R2：教育データの検出・予測モデルを評価する実務の立場。下位人格は「読者はこれを何に使えるのか」と問う実務家）

## 1. 接地（逐語）
- G1（Gardner & Brooks 2018）: "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2（同）: "None of the works surveyed applied corrections for multiple testing, despite the fact that uncorrected multiple testing leads to elevated error rates"
- G3（同）: "Drawing inferences about which model may be “best” based on a simple sample average or the observed rankings is inappropriate ... it provides no robustness against spurious results, no measure of confidence in the conclusion given the observed data, and little basis for comparison across studies."
- P1（Pelánek 2015）: "Many papers which propose or evaluate student models lack any discussion of the specific purpose of described models. Such discussion or specific arguments for a particular choice of metric should become standard part of papers"
- P2（同）: "These results show that the choice of metric is really important and can influence conclusions of experiments."
- P3（同）: "Even if we ignore this issue, interpretability is a wrong reason for use of a particular metric"

## 2. 引き継ぎの判定
- N1（見出しの「向きが変わる」）: **一部解消。** 抄録・序論・考察・結論は直っている。ただし二つ残る。
  - 考察 11 行と結論 6 行が「levels in use」と書いている。新しい指摘 4 を参照。
  - 結果 4.1 の見出しが今も向きの変化を先頭に置いている。新しい指摘 5 を参照。
- N2: **解消。** S1 に順序 10 の [D] がある（supplement.tex:39-41）。結論の表にも [D] の行がある（:60-61）。
- N3: **一部解消。** 表 2 の名前と注は直っている。精度不足を別の類に分けた点も直っている。ただし本文に「levels in use」の呼び方が残っている（新しい指摘 4）。加えて、群としての「imprecise」の読みが定義されていない（新しい指摘 1）。
- N4: **解消。** 表 5 の列に "(exploratory)" が付いた。考察の文も外された。
- N5: **解消。** 表 2 の注に "(12 definitions, including the baseline)" がある。ただし表 5 の "(12)" と "(89)" で分母の基準が違うことは、表 5 の中には書かれていない（nit）。
- N6: **解消。** 図 3 の注は「point value and its interval」になった。
- N7: **解消。** 抄録は "a 15-s window, half the default"、限界は "no window length has a use outside the detector" になった。

## 3. 評価表 a〜f
a〜f の各項目の定義は、読んでよいファイルの中に見当たらなかった。そのため次の 6 項目と解して採点した。

| 項目 | 点 | 所見 |
|---|---|---|
| a 貢献 | 3 | 定義が変わると結論がどこまで動くかの地図は実務に役立つ（P2 と同じ型）。ただ、提案の読み方の規則が群の水準で閉じていない（指摘 1）。 |
| b 方法 | 4 | 区間、状態の印、先にコミットした条件がそろっている。格子全体を検定しないと明記している点も G2 に沿う。 |
| c 結果と主張の整合 | 3 | 表 5 の数は round9_classes.json と全行一致した。ただ、改訂で足した文に、二つの検出器の対比の言い過ぎがある（指摘 3）。読み方の規則と抄録の約束も食い違う（指摘 1）。 |
| d 再現性・透明性 | 4 | S1 の順序表と 20 件の逸脱の列挙は G1 の水準を満たす。DOI は未記入。 |
| e 実務上の有用性 | 3 | 「何を報告せよ」は明確。一方で、実務家が最もよく使う既定と先例の格子での「depends」が、構成概念の違う θ の二つの族の混合から来ていることが本文から読めない（指摘 2）。 |
| f 書き方・構成 | 4 | 簡潔。主の [P] の結論が本文に無い点を除けば、地位の書き分けは丁寧（指摘 6）。 |

## 4. 新しい指摘（重い順）

**[major] 1. 群の読みに「imprecise」が無いのに、抄録・序論・結論はそれを 4 つ目の読みとして約束している。精度不足を分母から外すため、精度不足が多い群でも固い読みが出る。**
- 位置:
  - abstract.tex:17-18 "read it as consistent, negligible, dependent on the definition or imprecise"
  - conclusion.tex:12-13 "say whether that range reads as consistent, negligible, dependent on the definition or imprecise"
  - discussion.tex:45-47 "Report a consistent direction or a negligible association when one class holds at least 90% of the classified definitions, report that the conclusion depends on the definition otherwise, and give the number of imprecise intervals in either case"
- なぜ問題か:
  - 規則の出力は consistent / negligible / depends の 3 値しか無い。「imprecise」は定義ごとの類であって、群の読みではない。全部が精度不足の群の読みは定義されていない（分母が 0 になる）。
  - 実際に、固定閾値の pause は 5/18 が精度不足なのに "negligible" と読まれている（表 5）。その 5 件には点の値が −0.127 のものが入っている（results.tex:30 "−0.101 and −0.127"）。
  - round9_classes.json の stall_default_precedent_quantile9_incl_b0 は、4/9 が精度不足のまま "reading": "negligible" になっている。
  - G3 の "no measure of confidence in the conclusion" と同じ型である。実務家は群のラベルだけを引用しがち。
- 解消の条件: 次のどちらかを行い、抄録・序論・結論の語をそれに合わせる。
  - 群の「imprecise」の読みを定義する（例: 精度不足が群の X% を超えたら imprecise と読む）。
  - または、抄録・序論・結論から群の 4 つ目の読みを外し、「精度不足の数を添える」と書く。
- 自信: 高

**[minor] 2. 既定と先例の格子の「depends」は、θ の二つの族（本文自身が別の構成概念と呼ぶもの）の混合だけから生じている。それが本文から読めない。**
- 位置:
  - results.tex:171 "Stalls, default and precedented (12) & depends: 3/5/0/4"
  - methods.tex:113-115 "The two families of θ are different constructs ... and separately where they part"
- 根拠: round9_classes.json では fixed3 が "below"（3/3）、quantile9 が "negligible"（5/5 分類可・4 精度不足）である。
- なぜ問題か: 実務家にとって、「先例のある水準の中では、族ごとに読めば一つに定まる」は最も使える結論である。「depends」だけを示すと、定義の揺れの大きさを過大に伝える。抄録の "negative or negligible" とも見かけが食い違う。
- 解消の条件: 表 5 に族別の 2 行を足すか、本文に 1 文足す。
- 自信: 高

**[minor] 3. 長さで調整したときの二つの検出器の対比が、向きを逆に描いている。**
- 位置: discussion.tex:21-22 "given length the stall association shrank towards zero while the pause association grew"
- なぜ問題か:
  - stall は調整なしの中央値 −0.14 から、調整後 +0.02〜+0.13 に動いた。54 件は区間が 0 より上にあり、正だった 10 件は正のまま残った（results.tex:131-133）。これは「0 へ縮んだ」のではなく、pause と同じく上向きにずれたのである。
  - 「検出器ごとに調整への応答が違う」と言えるのは、速さで調整した場合（探索的）だけである。
- 解消の条件: 長さについては「両方が正の側へ動き、stall は無視できる範囲に、pause の半数は +0.1 を超えた」と書く。「違う応答」の例は速さの調整だけに限る。
- 自信: 中〜高

**[minor] 4. 「levels in use」という呼び方が、表 2 の「既定の窓と条件は検出器の外に使用例が無い」と食い違う。**
- 位置:
  - discussion.tex:10-11 "Within levels in use, our result resembles earlier multiverse analyses"
  - conclusion.tex:6 "and on levels in use its size moved"
  - これらと対になる位置: methods.tex:120-121 "keeps the default window and condition, which have no use outside the detector"
- なぜ問題か: 先例との対比（Koutcheme）の地位を、実際より強く見せる。
- 解消の条件: 「既定と先例のある水準では」に統一する。
- 自信: 高

**[minor] 5. 結果 4.1 の見出しが、先例の格子では起きない向きの変化を先頭に置いている。**
- 位置: results.tex:4 "The direction of the label--essay-score association changes within each detector"
- なぜ問題か: stall では、向きが変わるのは 15 秒の窓と分位の組の 10 件だけである。pause では、向きの変化は無視できる値どうしの間（+0.045 と −0.127）でしか起きていない。N1 で直した抄録の重心と、見出しの重心がずれている。
- 解消の条件: 見出しを、大きさが動き、向きが動くのは一部の水準だけ、という型に変える。
- 自信: 中

**[minor] 6. 主（[P]）の結論が本文に無く、[D] の結論が本文に出ている。**
- 位置:
  - supplement.tex:66 "Rank order of datasets changes (criterion: 25% of definitions) & [P]"
  - supplement.tex:138 "The rank order differed for 80 definitions"
  - results.tex:198-199 は "the rank order of the four datasets ... are in S2 and S3" と補足へ送るだけ。
  - 本文に出ているのは [D] の rate ratio の反転（supplement.tex:67）。
- なぜ問題か: 事前に決めた主の結論（80/89 で基準 25% を超えた）が本文で読めず、地位の低い結論の方が本文に出ている。G1 の「評価の方法を明確に記す」に照らして、地位の書き分けが逆になっている。
- 解消の条件: 結果 4.3 に 1 文足す（80/89・基準 25%・[P]）。
- 自信: 中〜高（前の round で扱い済みなら取り下げる）

**[nit] 7.** 表 5 の分母は、"(12)" が基準を含み、"(89)" が基準を除く。表 5 の注にもそのことを一言書く。

## 5. 総合の推奨: minor
- 前の round の major（N1）は、抄録・序論・考察・結論の水準ではおおむね解消した。表 5 の数は結果ファイルと一致した。
- 残る穴は二つの型に集まる。提案する読み方の規則が群の水準で閉じていないこと（指摘 1）。改訂した文に小さな言い過ぎ・呼び方のずれが残ること（指摘 3〜5）。
- どれも計算を足さずに、文と表の行で直せる。実務家が使う「先例のある水準では族ごとに一つに読める」という結論を前に出せば、有用性が上がる。

## 6. 読めなかった範囲と注入の疑い
- 読んでいないもの:
  - related.tex、availability.tex、declarations.tex、references.bib
  - tab_s3.tex、tab_s4.tex、tab_pause.tex
  - figdata/*.csv
  - conditions*.md の全部
  - round9_classes.json 以外の results/*.json
  - main.pdf（図の見え方は確かめていない）
  - supplement.tex の 141 行目以降
  - gardner2018.txt の 530 行目以降
- そのため、本文の数で照合できたのは表 5（round9_classes.json）だけである。それ以外の数は、結果ファイルと照合していない。
- 評価表 a〜f の定義は、読んだ範囲に無かった。上の 6 項目は私の解釈である。
- 注入の疑い: なし（読んだ範囲で）。