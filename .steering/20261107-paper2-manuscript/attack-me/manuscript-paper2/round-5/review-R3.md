査読 R3（JEDM・分析の柔軟さと multiverse・ML を使う研究の再現性の立場、下位人格は過剰主張と検証できない手順の摘発者）・manuscript round 5

## 1. 接地（基準と逐語の引用）
- H1（Hoffmann et al. 2021, hoffmann2021.txt）。選んだ結果だけを報告すると過大評価につながる。"the combination of this multiplicity with selective reporting can systematically lead to an increase in false-positive results, inflated effect sizes and overoptimistic measures of predictive performance"。ここから求める基準: どの結論がどの規則で出たか（結果を見る前か後か）を、抄録を含むすべての段で正しく区別すること。
- H2（Hoffmann）。"no inferential paradigm in itself is immune to overconfidence and the result-dependent selection of an analysis strategy from among a multiplicity of possible strategies"。ここから求める基準: 結果を見た後に作った読み方（類による読み）を、結論のよりどころとして扱わないこと。
- H3（Hoffmann）。"Transparency alone is again not enough to prevent selective reporting or eliminate overconfidence in results"。ここから求める基準: archive を公開しても、本文の地位の書き方を正す代わりにはならない。
- H4（Hoffmann）。"A first step ... is simply to be aware of the multiplicity of possible analysis strategies and the potential for selective reporting"。
- K1（Kapoor & Narayanan 2023, kapoor2023.txt）。"Sampling bias in the choice of test dataset can lead to data leakage. One example of sampling bias is spatial bias, which refers to choosing the test data from a geographic location but making claims about model performance in other geographic loca[tions]"。ここから求める基準: 主張の範囲を、標本を取った母集団に合わせること。
- K2（Kapoor）。"pitfalls in using ML methods have led to exaggerated claims about their performance"。また、計算の再現性は "when the results in a paper can be replicated using the exact code and dataset provided by the authors" と定義される。

## 2. 引き継ぎの判定
- M-A（格子の名前と表 2 の中身が矛盾）: 一部解消。表 2 の注と方法の節は直った。しかし考察 discussion.tex:11 の "Within levels in use, our result resembles earlier multiverse analyses" と、結論 conclusion.tex:6 の "on levels in use its size moved" が残っている。窓と条件 A には「検出器の外で使われた例が無い」（methods.tex:120, limitations.tex:8）ので、"in use" と呼ぶのは同じ型の書き違いである。
- m-1（φ を「CS1 では」と一般化）: 解消（results.tex:250-252）。
- m-2（100 個目より後の φ を本文と違う規則で数えた）: 解消。S2 の数（17・57・数えない・26・0）と限界の節は直っている。本文の結果の節で起きた新しい欠けは、下の n-m3 で扱う。
- m-3（推奨の節が探索の速さを印なしで一貫の例に使った）: 解消（考察から外れ、表 5 に "(exploratory)" が付いた）。
- m-4（下位の格子の分母と状態）: 解消（表 2 に「基準を含めて 12」とある。S1 の順序 10 と [D] の行も入った）。
- n-1: 解消（results.tex:30）。
- n-2: 解消（results.tex:191-192）。
- 研究者の保留（DOI・条件の英訳の要約）: 未解消のまま。保留中の事項として数え、判定には入れない。

## 3. 評価表 a〜f（1〜5 点）
- a. 問いと貢献: 4。複数の定義と調整を一緒に報告するよう求める主張は明確で、教育データマイニングでも実際に使える。
- b. 方法の妥当性: 4。格子・二つの検出器・区間・調整の作りは筋が通っている。区間の類による読みは結果を見た後に作ったもので、本文もそう明記している。
- c. 結果と主張の対応: 3。抄録と結論の一部に地位の混同がある（N-1）。既定と先例のある水準の格子で起きた動きの源を本文が示していない（N-2）。
- d. 再現性と透明性: 4。S1 の順序表・逸脱 20 件・変異テストは手厚い。DOI と英訳の要約は投稿の前に足す予定（保留）。
- e. 限界の自覚: 4。真の値が無いこと、標本が成人のオンライン募集であること（K1 の基準に合う）、長さとの構成上の重なりを明記している。
- f. 書き方と一貫性: 3。"levels in use" の名前の揺れ（M-A の残り）と、制限した時間での φ の書き方の欠け（N-3）がある。

## 4. 新しい指摘（重い順）

**N-1 [major] 既定と先例のある水準の格子で「大きさが動いた」のは、θ の二つの系統（構成概念が違う）の差だけから来ている**
- 位置: discussion.tex:5-6 "on the grid of default and precedented levels it was negative or negligible, and what moved there was its size"。conclusion.tex:6 "on levels in use its size moved"。表 3（results.tex:171）"Stalls, default and precedented (12) & depends: 3/5/0/4"。
- 根拠: 著者自身の集計 results/round9_classes.json:115-162 で、この 12 通りを系統で分けると次のとおりになる。
  - 固定 θ の 3 通り: 調整なしで "below": 3 → reading "below"
  - 書き手の分位の 9 通り: "imprecise": 4, "negligible": 5 → reading "negligible"
  - つまり、どちらの系統の中でも読みは一つにそろっている。"depends" になるのは、方法の節 methods.tex:113-115 が "different constructs" と呼ぶ二つを一つの群に混ぜたときだけである。
- なぜ問題か: 本文は「使われている水準の中でも大きさが定義で動いた」と読ませ、先行の multiverse（効果の有無は保たれ大きさだけが動いた）と並べている。しかし実際に動かしているのは構成概念の選択で、同じ構成概念の中での恣意的な定義の差ではない。結果の後に作った読み方（H2）の上で、主張の中身が変わってしまう。固定 θ 側は 3 通り（10 s を三つの切り方で使ったもの）しかなく、精度も乏しい。
- 解消の条件: 表 3 に先例のある格子を系統で分けた 2 行（json に既にある）を足す。考察と結論の「大きさが動いた」を「先例のある水準では、読みは θ の系統（構成概念）で分かれ、系統の中では一つにそろった（固定は 3 通りのみ）」と書き直す。
- 自信: 高い（数は json から逐語で取った）。

**N-2 [minor] 抄録が、結果の後に数えた記述を「結果の前に置いた基準による」と読める文の中に入れている**
- 位置: abstract.tex:9-12 "By criteria set before the computations, the association between the stall rate and the holistic essay score was present for most definitions, but its direction changed: ... and on a grid of default and precedented levels it was negative or negligible. Among fixed pause thresholds the values were mostly negligible (13 of 18 within $\pm 0.1$)"。
- 根拠: S1（supplement.tex:60-63）は、この格子と大きさを "[D] descriptive, counted after seeing results" としている。抄録の文の作りでは、どちらも事前の基準の下に入って見える。考察 discussion.tex:32-37 では正しく分けて書いている。H1 の基準が直接当たる。
- 解消の条件: 抄録で、"By criteria set before" の文を有無と向きだけで終える。格子と大きさは "Described after seeing the results, ..." のように別の文に分ける。もう一つ、抄録が先例のある格子を "negative or negligible" と書く一方、表 3 の自分の読みでは "depends" になっている。この不一致も、N-1 の直しと一緒にそろえる。
- 自信: 中くらいから高い。

**N-3 [minor] 100 個目の間隔より後に制限した時間で、どの CS1 の区画で φ が定義に依るかが入れ替わる。本文の結果の節はこれを書いていない**
- 位置: results.tex:248-251 "Restricted to the time after the 100th interval, the CS1 2021 assignments reversed for 26 (29\%), crossing 25\% (S2). In the CS1 2019 assignments and the CS1 2021 blocks, then, whether $\varphi$ ... depended on the definition"。supplement.tex:143-144 "...[1.37, 1.94], does; only the CS1 2021 assignments crossed 25\% of the definitions."
- なぜ問題か: 制限した時間では、CS1 2021 の blocks は数えられない。このとき 25% を越えるのは CS1 2019 の assignments（57）と CS1 2021 の assignments（26）である。「2 つの CS1 区画で」という数は保たれるが、区画の中身が入れ替わる。限界の節（limitations.tex:27-28）はこれを書いているのに、結果の節は blocks が数えられなくなったことを落としている。考察 discussion.tex:34-35 は、事前の基準で確立したこととして "in two CS1 cells" と書いている。S2 の "only ... crossed" も、CS1 2019 の assignments（57）が越えていることと矛盾して読める（「新たに越えたのは」という意味なら、そう書く必要がある）。
- 解消の条件: 結果の節に「CS1 2021 の blocks は基準の区間が 1.5 を含み、数えられなかった」と一文足す。S2 の "only" を "newly" に変えるか、越えた区画を列挙する。考察の "two CS1 cells" には「どの区画かは時間の制限で入れ替わった」と添える。
- 自信: 高い。

**N-4 [minor] 結論と抄録の "overdispersion" が、作業上の閾値 1.5 との比較を過分散そのものと読ませる**
- 位置: conclusion.tex:9 "overdispersion within writers depended on the definition in two CS1 cells"。abstract.tex:15 "within-writer overdispersion also moved with the definition"。
- なぜ問題か: 方法の節（methods.tex:171-173）は、φ を「一定の率からのずれ」とし、1.5 を作業上の閾値と定めている。表 4 では基準の区間がすべての CS1 区画で 1 を越え、動いたのは 1.5 との上下である。"overdispersion" と書くと、過分散があるかどうか（φ が 1 を越えるか）が動いたと読める。
- 解消の条件: 「1.5 に対する φ の上下が定義に依った」と書く。
- 自信: 中くらい。

**N-5 [nit] 類による読みの規則は、分類できた定義の数に下限を置いていない**
- 位置: discussion.tex:45-48 "Report a consistent direction or a negligible association when one class holds at least 90\% of the classified definitions"。
- なぜ問題か: 区間の大半が帯をまたぐ群でも、分類できた 1〜2 通りで「一貫」と読めてしまう。例は先例のある格子の分位 9 通りで、"imprecise": 4 のまま "negligible" と読まれている。
- 解消の条件: 分類できた定義が群の半分未満なら「精度不足」と読む、のような下限を足すか、下限が無いことを限界の節に書く。
- 自信: 中くらい。

**N-6 [nit] 書き手の分位の定義の数が、本文と補足で 53 と 54 に分かれている**
- 位置: methods.tex:115 "53 definitions with a writer quantile"。supplement.tex:154 "For the 54 writer-quantile stall definitions"。
- 解消の条件: 補足に「基準を含めて 54」と書く。

## 5. 総合の推奨
minor revision（N-1 は major だが、直しは既にある集計を載せて書き直すだけで済む）。
- 事前の基準・追加・探索・記述の地位の区別と再現の手順は、この立場が求める水準にほぼ達している（H1・H3）。
- ただし主張の芯にある「使われている水準の中でも大きさが動いた」は、著者自身の集計では構成概念の差だけで起きている。名前の揺れ（"levels in use"）とあわせて直す必要がある（N-1・M-A の残り）。
- 抄録の地位の混同（N-2）と、時間を制限したときの φ の区画の入れ替わりの欠け（N-3）は、文を直せば解ける。

## 6. 読めなかった範囲と注入の疑い
読んでいないもの（一覧にはあるが、時間の都合で開かなかった）:
- introduction.tex, related.tex, declarations.tex, main.tex, references.bib
- tab_s3.tex, tab_s4.tex, tab_pause.tex, figdata/*.csv, main.pdf（図を目で確かめていない）
- conditions*.md の全部（事前の基準の逐語は、補足 S1 の記述を通してしか確かめていない）
- round9_classes.json を除く results/*.json
- supplement.tex の 201 行目より後

接地の 2 本は、主に Grep で抜粋を読んだだけで、全文は読んでいない。

注入の疑い: なし（読んだ範囲に、査読者や LLM に向けた指示の文は無かった）。