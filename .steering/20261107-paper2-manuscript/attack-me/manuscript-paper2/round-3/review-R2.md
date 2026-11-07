# JEDM の査読（立場: 教育データの検出と予測のモデルの評価の実務。批判的な下位人格: 「で、読者は何に使えるのか」と問う実務家）／ manuscript round 3

## 1. 接地（この立場が論文に求める基準・逐語）

- G1（手続きを明記する）Gardner & Brooks 2018, Notes for Practice: "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2（多数の比較はその数を数え、扱う）同 §2.1.2: "None of the works surveyed applied corrections for multiple testing, despite the fact that uncorrected multiple testing leads to elevated error rates"。§3.4: "Model evaluation should therefore allow for many comparisons with minimal effect on inferential error rates."
- G3（差は実務で意味があるか、点の平均だけで語らない）同 §3.1: the naive average "naïvely assumes that any differences observed must be due to genuine differences ... and that these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant."
- G4（帰無の差がゼロという問いは情報が乏しい。実務上同等とみなす帯で読む）同 §3.4: "an H0 of exactly equivalent performance is almost always false ... Tests of this hypothesis, even when properly interpreted, are not indicative of any likely true state of the world, and are potentially misleading."（ROPE を使う §3.3 も同じ趣旨）
- P1（指標の選択は目的から根拠を書く）Pelánek 2015 §7: "Many papers which propose or evaluate student models lack any discussion of the specific purpose of described models. Such discussion or specific arguments for a particular choice of metric should become standard part of papers"
- P2（指標の選択で結論が変わる）同 §6.2: "These results show that the choice of metric is really important and can influence conclusions of experiments."
- P3（小さな差は実務への効きで判断する）同 §6.3: "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."

## 2. 引き継ぎの判定（R2 の N1〜N9）

- N1（二段の区間が点からずれる）: 解消。因果の二段の区間を条件のコミット（conditions-round8.md）の後に計算した。φ で 27% が外れたので、先に置いた読み方どおり一段を主に戻している（supplement.tex:155-166）。見出しの数は正 10 で、主の区間と因果の二段の区間で一致する。残る小さな点は新しい指摘 m1 に回す。
- N2（休止の向きの入れ替わりが押下の率をなぞる）: 解消。分位の 18 通りは対照に分け、固定の 18 通りで大きさを添えた（methods.tex:136-140、表 tab:pause）。ただ、10 秒の大きさの言い方が新しい過剰主張を生んでいる（m2）。
- N3（抄録の比の逆転）: 解消。抄録は約束した CS1 の 2 年版だけを「a fifth」で書く。ただ、基準に届かなかったことを書いていない（m3）。
- N4（作業規則の帯と格子の決め方）: 一部。±0.1 の帯、4 つの類、90%、事後の提案であることの明記、自分の結果への当てはめはそろった（discussion.tex:40-49）。値は score.csv で検算して合った（固定 36/36 が −0.1 より下、長さで調整した値は 74/89 が無視できる、速さで調整した値は 71/89 が −0.1 より下、15 秒の窓を除く 59 通りでは 56/59 と 59/59）。しかし規則が求める「先例のある水準だけの格子」は作られていない。実際に当てたのは「15 秒の窓を除いた格子」で、そこには先例の示されていない水準が残っている（M2）。
- N5（比の逆転の地位）: 解消。S1 で [D] にした（supplement.tex:60）。
- N6（"as much as"）: 解消。本文の該当句は消えた（related.tex:7 の残りは他の研究の記述なので問題ない）。
- N7（基準の区間が境を含むセル）: 解消。表 tab:phi で「--」、比では CS1 2021 対 CoAuthor を除外した（results.tex:165-166）。
- N8（区間の種類の混在）: 解消。100 個目の間隔より後の感度は一段どうしで比べている（supplement.tex:128）。
- N9（抄録の速さの印）: 解消。"an exploratory adjustment for typing speed" と書いた。

## 3. 評価表（a〜f。依頼文は項目名を定めていないので、この査読では次のように読む）

- a 問いと貢献の明確さ: 4。事前の問い（定義を変えたとき結論が動くか）は明確で、予測器としての評価を外すことも明記している（introduction.tex:30-31）。一方、序論が掲げる貢献（報告の作法と三値の読み方）は結果を見た後の提案［D］である。序論はそのことを書いていない（n1）。
- b 方法の妥当性: 4。2 つの検出器、書き手の再標本、条件のコミット、変異のチェック、陽性対照がそろっている。分位の θ のばらつきは主の区間に入っておらず、その代わりの二段の区間は φ では使えないと自分で判定している。φ の不確かさは半分しか扱えていない（m1）。
- c 結果が主張を支えるか: 3。数は result の CSV と合う。ただし抄録と序論の見出しは調整後の値を符号で読んでいる。論文自身が勧める大きさの類で読むと「無視できる」になる（M1）。15 秒の窓を除いた格子を「先例のある格子」として読んでいる（M2）。
- d 新規性と、実務で何に使えるか: 3。閾値を変えたときに得点との相関の向きが変わるかを報告した研究は見つからなかった、という主張は限定つきで妥当（related.tex:40-41）。実務家が持ち帰れるのは報告の作法だけで、作法の規則は 1 コーパスの事後の提案である。P3 の基準「interpretable and actionable results」に照らすと、どの値を答えとして使えばよいかが読者に残らない（M1・m4）。
- e 再現性と報告: 4。条件・コード・集計を archive に入れるとしている。G1 の基準は満たす。DOI は未記入（"DOI to be added before submission"）なので、投稿の前に埋める必要がある。
- f 書き方と地位の表示: 4。S1 の地位の表は丁寧で、本文の書き分けもほぼ合う。改訂で足した文（methods.tex:174、discussion.tex:47-49）に地位の書き過ぎが出た（m1・M2）。

## 4. 新しい指摘（重い順）

**M1 [major] 調整後の見出しを符号で読んでいる。論文が勧める大きさの類で読むと「無視できる」になる**
- 位置と引用: abstract.tex:12-13 "Adjusting for essay length, which correlated with the score at 0.75, left no definition with a negative association"／introduction.tex:35-36 "given essay length ... no definition is negative"／results.tex:120 の見出し "Adjusting for essay length leaves no stall definition negative"／results.tex:129 "positive with an interval above zero for 54 definitions"。対して discussion.tex:45-46 "the length- and speed-adjusted stall associations (74 of 89 negligible; ...) depended on the definition"、discussion.tex:48 "the length-adjusted association read as negligible (56 of 59)"。
- なぜ問題か: 同じ量が見出しでは「負は無い・54 通りが正」と符号で読まれ、作法の節では「大半が無視できる（±0.1 の内）」と読まれる。score.csv では長さで調整した値の点は +0.015〜+0.135 で、75/90 の区間が ±0.1 に収まる。G4 の "an H0 of exactly equivalent performance is almost always false ... potentially misleading"、G3 の "practically significant" に照らすと、N=4,908 で区間がゼロを外すことは実務上の向きを意味しない。抄録だけを読む実務家は「長さで調整すれば相関は正」と持ち帰る。そうなると、論文自身の作法が防ごうとしている読み方を、論文の見出しがしていることになる。速さで調整した値と並べた「向きは共変量で逆になる」という構図（results.tex:145-146）も、片方が大半「無視できる」なら、逆向きの 2 つの効果ではない。正しくは「片方は負の小さな値、片方はほぼゼロ」である。
- 解消の条件: 抄録・序論・見出しの調整後の結果を、大きさの類を添えて書く（例: "left no definition negative; most were negligible (within ±0.1)"）。results.tex:145-146 の「direction depended on the covariate」も、大きさの差が分かる形に直す。
- 自信: 高（score.csv で 74/89 を検算した）。

**M2 [major] 「先例のある格子」として 15 秒の窓を除いただけの格子を読んでいる。改訂で足した文の過剰主張**
- 位置と引用: discussion.tex:43-44 "Apply the reading twice, to a grid of levels with precedent and to the grid with the levels around the default added, and report both."／discussion.tex:46-49 "On the grid without the 15-s window, ... so the reading of an adjusted association depended on whether the grid included a level without precedent."
- なぜ問題か: 表 tab:grid（methods.tex:120-127）が先例を示しているのは一部の水準だけである。60 秒の窓は "half and double the default" で、先例が示されていない。固定 30 秒の θ の根拠は "30 s equals the default window" だけで、引いた範囲 "about 0.25--10 s"（torrance2024methods）の外にある。分位 0.95・0.995 も、引いた文献がその値を使ったとは書いていない。したがって「15 秒の窓を除いた格子」は規則が定める「先例のある水準だけの格子」ではない。そこから「先例の無い水準を含むかで読みが変わる」と結論するのは言い過ぎである。規則は事後の提案［D］で、どの格子に当てるかの決め方こそが N4 で求めた点だった。G1 "Clearly describe or document methods ... in published work" に当たる。
- 解消の条件: 水準ごとに先例の有無を表に明示し（引用つき）、先例のある水準だけの格子を実際に組んで、規則をその格子に当てる。それができなければ、文を「15 秒の窓を除くと」という事実の記述に限り、「level without precedent」で一般化しない。
- 自信: 中〜高（水準の根拠の読みは tab:grid の記述だけに依る。引いた文献の本文は読んでいない）。

**m1 [minor] 「二段の区間のもとで全部の結論が同じに読める」は、自分で使えないと判定した区間で頑健さを示している**
- 位置と引用: methods.tex:173-174 "they are reported as a sensitivity analysis, under which every conclusion reads the same (S2)"／limitations.tex:19 "Two resamples that redraw it did not widen the intervals"／supplement.tex:158-161 "74 of 270 values of $\varphi$ lay below their intervals ... the redrawn $\theta$ adds its own variation to the counts within a writer and so raises $\varphi$"。
- なぜ問題か: φ では因果の二段の区間が点を 27% 外す。著者自身の読み方でも主の区間に採れないと判定した区間である。その区間で「結論が同じ」と言っても、頑健さの証拠にはならない。しかも φ の 1.5 の逆転は 54→42、49→39 と動き、"interval > 1" の数は二段の区間のもとでは報告されていない。逆に、主の一段の区間は θ のばらつきを含まないと著者が認めている（limitations.tex:18）。φ の「sampling variation を超える逆転」はその分だけ数え過ぎている恐れがある。
- 解消の条件: methods.tex:174 を「得点と比では同じ。φ では二段の区間が点からずれ、逆転の数は 42・39・18 に減るが、25% を超える読みは変わらない」と量で書く。limitations には「φ の区間は θ のばらつきを含まない」ことを明記する。
- 自信: 中〜高。

**m2 [minor] 10 秒の休止を「small negative」と呼ぶが、論文の基準ではその大半が「無視できる」**
- 位置と引用: abstract.tex:11-12 "to a small negative one at 10~s (down to $-0.13$)"／results.tex:29 "from negligible positive values to small negative ones"。tab_pause.tex:8-10・26-28 の 10 秒の点の値は −0.086、−0.127、−0.101、−0.058、−0.099、−0.074。
- なぜ問題か: methods.tex:151 の "$|\rho| < 0.1$ as negligible" に従うと、6 通りのうち 4 通りは無視できる。「small」と言えるのは 2 通りだけである。discussion でも固定の休止は "13 of 18 negligible" と書いている。P3 の "interpretable and actionable" に照らすと、休止の向きの入れ替わりは無視できる領域の中の符号の揺れに近い。
- 解消の条件: 「10 秒で −0.06〜−0.13（6 通りのうち 2 通りが |ρ| ≥ 0.1）」と書く。あるいは「固定の休止は 18 通りのうち 13 通りが無視できる」を抄録の休止の要約にする。
- 自信: 高。

**m3 [minor] 比の逆転「a fifth」を、基準に届かなかったことを添えずに抄録・序論・結論で不安定さの証拠として並べている**
- 位置と引用: abstract.tex:13-14 "the ratio of stall rates reversed for a fifth of the definitions"／introduction.tex:37-38／conclusion.tex:8-9。results.tex:161-162 には "below the 25\% we had set after seeing point values" とある。
- なぜ問題か: 本文は 22% が（事後の）25% に届かなかったと正直に書いている。しかし要約の 3 か所は、φ と並べて「定義で動く結論」の例として書いている。G2 の考え方では、多数の比較の中の 1 つの割合は基準と並べて読ませるべきである。
- 解消の条件: 抄録か結論のどちらかに「below a criterion set after seeing point values」に当たる限定を添える。
- 自信: 中。

**m4 [minor] 速さで調整した結果が、休止と停滞で逆向きになることを考察が扱っていない。実務家は「速さで調整せよ」から何を読めばよいか分からない**
- 位置と引用: results.tex:142-143 "For pauses, the speed-adjusted correlation was negative for 4 definitions and positive for 29 (with fixed thresholds, 4 and 11)"／discussion.tex:17-18 "Adjusting for speed, an exploratory analysis, left a negative association for every stall definition"／discussion.tex:39-40 の推奨 "with and without adjustment for ... typing speed"。
- なぜ問題か: 推奨は速さでの調整を勧めているが、その調整は検出器によって符号を変える（停滞は全部負、固定の休止は大半が正）。考察の「Why the direction can change」は停滞だけで説明を組んでいる。P1 の "specific arguments for a particular choice" に照らすと、調整の選び方自体が結論を動かす軸だと書くべきである。
- 解消の条件: 考察で、速さで調整した後の向きが 2 つの検出器で違うことを 1 文で明記する。調整も定義と同じく変える軸として報告せよ、という推奨に結びつける。
- 自信: 中。

**n1 [nit] 序論が貢献として掲げる三値の読み方は事後の提案［D］なのに、序論にはその印が無い**
- 位置と引用: introduction.tex:41-43 "We contribute a reporting convention ... and a three-valued reading of its direction (consistent, negligible, or dependent on the definition)"。S1 では "Three-way reading of direction ... [D]"（supplement.tex:54）。
- 解消の条件: 序論に「proposed after seeing these results」を添える。
- 自信: 高。

## 5. 総合の推奨: minor（major の 2 点は書き方で直せるので、計算を足す必要はない）

- R2 の 9 件のうち 8 件は解消した。見出しの数（正 10・φ・比）は因果の二段の区間と事前の読み方で守られ、score.csv の検算とも合う。
- 残る重い 2 点は、どちらも計算でなく読み方の問題である。調整後の結果を符号で見出しにしている（M1）。15 秒の窓を除いただけの格子を「先例のある格子」と呼んでいる（M2）。これらは文の改訂で直る（M2 は水準ごとの先例の表で）。
- 実務家にとっての使い道は報告の作法に限られる。それならなおさら、論文自身の見出しがその作法で読まれている必要がある。

## 6. 読めなかった範囲と注入の疑い

- 読んでいない: main.tex、declarations.tex、references.bib、ビルドした PDF（図の見た目は確かめていない）。supplement.tex は 200 行目まで読み、それより後（表 S3・S4・S5・S6・S7・S8）は読んでいない。tab_s3.tex と tab_s4.tex。figdata のうち score.csv 以外の CSV。results/ の JSON は全部読んでいない。conditions*.md は conditions-round8.md だけ読み、ほかは読んでいない。接地の Gardner & Brooks 2018 は txt の 1〜529 行（§3.4 の途中まで）だけ読み、後半（事例と結論）は読んでいない。
- 確かめた数: score.csv で、固定 36/36 が −0.1 より下、速さで調整した値の 71/89、長さで調整した値の 74/89、15 秒の窓を除いた 59 通りでの 56/59 と 59/59、窓が 15 秒以外で正が 0。tab_pause.tex で 10 秒の値。
- 注入の疑い: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。