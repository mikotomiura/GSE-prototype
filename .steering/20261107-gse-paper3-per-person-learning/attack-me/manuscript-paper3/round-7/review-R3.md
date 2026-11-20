# R3（評価の偏りと個人への推論の方法論の立場）round 7 の査読：Per-person sequence models of keystroke behaviour（commit ed297dd4）

**結論は minor revision。** round 6 の 9 件は 6 件が解消、2 件が一部（N-2・N-4）、未解消は 0 件。新しい指摘は major 1 件・minor 5 件・nit 1 件。major は、post hoc で足した書き手のデータを使わない対照が、比べたい条件と合っていないこと（新規 1）。

## 0. 引き継ぎの判定

- **N-1：解消。** 4.4（main.tex:282）に対照が入った。「The prior mode built from the refitted shared model, which uses none of the writer's data, gains only $+2.5\times10^{-5}$ ... the chosen fit beats it by $+3.3\times10^{-3}$ at $k=5$ and $+7.9\times10^{-3}$ at $k=15$」。地位も同じ所に「These control values were added after seeing the symmetric refit.」「These values were not checked against synthetic writers.」と書かれている。ただし、この対照が比べたい条件と合っているかは別の問題として新規 1 に挙げる。
- **N-2：一部。**
  - 序論（:51）は 2 つの値を 1 組で出し、「the second is the comparison that bears on a designer's decision」と書いた。考察（:321）も「The comparison that bears on the decision applies the same smoothing to both models.」と書いた。
  - 要旨（:37）と結論（:350）は 2 つの値を並べただけで、どちらが決定に関わるかを書いていない。要旨は「... 3.4 and $5.2\times10^{-3}$ ... (post hoc), 30 to 55 times below it.」で止まる。新規 5 で扱う。
- **N-3：解消。** :37「(smoothing post hoc, for one structure)」。
- **N-4：一部。**
  - 両側の当て直しと第 2 の帰無には (post hoc) が付いた。格子の拡張も「Candidate grids were extended after seeing results.」の 1 文にまとまった。
  - 要旨の「planted differences up to $3\times10^{-2}$ were not reliably detected」には地位の印も平滑の条件も無い。この文が成り立つのは post hoc の第 2 の帰無の下で、固定の平滑の場合だけである。新規 4 で扱う。
- **N-5：解消。** :341「this reading assumes that the remainder scales with the smoothing effect, which was not checked」。
- **N-6：解消。** :193「with the generator's base smoothing lightened」、:310「multiplied by 0.03」。α を 2 つの意味に使わなくなった。
- **N-7：解消。**
  - 結論 :350「with non-overlapping windows, which also give far fewer symbols ... (not checked against synthetic writers)」。
  - 考察 :317「a direction that may also reflect the smaller amount of data」。
- **N-8：解消。** :319「about 6 and 13 times larger」。検算では 3.4e-3/5.5e-4 = 6.2、5.2e-3/4.1e-4 = 12.7。
- **N-9：解消。** :37 と :51 が「at five and fifteen training sessions」の値になった。

## 1. 接地（この立場が求める基準）

1. **選んだ後の推定は偏る。調整の手順はすべて評価の外で繰り返す。**
   - Varma & Simon 2006（varma.txt:12）："using CV to compute an error estimate for a classifier that has itself been tuned using CV gives a significantly biased estimate of the true error. Proper use of CV ... requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
2. **評価のデータを選択に使わない。**
   - Varma & Simon 2006（varma.txt:37）："Thus the test set is used in the selection of the classifier parameters, which is problematic."
3. **候補が多いほど、最小値を選ぶと偏りやすい。**
   - Varma & Simon 2006（varma.txt:105）："for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
4. **個人への推論では、対照は目的の個人と関連があり、かつ頑健でなければならない。**
   - Liu & Meng（liumeng.txt:26-28）："how to make the right relevance robustness trade-off: if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
5. **模型の解像度はデータの解像度に合わせる。柔らかすぎる模型は観測の癖を拾う。**
   - Liu & Meng（liumeng.txt:446-448）："Highly flexible models tend to "overfit" the data ... Our choice of model resolution, R, should be compatible with the "data resolution.""

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 中心の主張（弱い比べの利得は、他の書き手で選んだ強い比べの残りより 30〜400 倍大きい）は、Table 2・3 と検算で支えられる。弱いのは要旨・結論で、post hoc の対照（2.5e-5）を、強い比べの残り 3.4〜5.2e-3 と対になるものとして書いている点（新規 1）。 |
| b 方法の穴 | 3 | 漏れ・格子の端・入れ子にしていないことは限界に書かれている。新しい穴は、軽い平滑で書き手のデータを使わない対照が、選ばれた τ（10^3〜10^4）の条件と合っていないこと（新規 1）。 |
| c 持ち帰れるもの | 4 | 「自分の連鎖と同じ構造の共有の両方と比べる」は明快で安く使える。ただ、決定に関わるとした比べ（5.2e-3）を設計者がどう読むかが閉じていない（新規 5）。 |
| d 簡潔さと構成 | 3 | 要旨は 247 語のうち数値の対が 5 組ほどある。想定読者（統計の訓練を前提にしない）には、地位の印が混じった数値の列が重い。4.4 の見出しは長く、地位の印の位置も誤っている（新規 2）。 |
| e 規程への適合 | 4 | 測った値によると、要旨 247 語は 150〜250 語に収まり、キーワード 6 個は 4〜6 個に収まる。"Statements and Declarations" の見出しと Data availability もある。本文の語数に規定は無く、7,502 語は問題にならない。前文に \PENDING の名残がある（新規 7）。 |
| f 先行研究の位置づけ | 4 | Varma・Cawley・Liu & Meng を選択の偏りと個人への推論の位置づけに正しく使っている（:66、:329）。「we do not claim the parts as new」も適切。Uto の評価の設計は既知の未決。 |

## 3. 指摘の一覧（重い順）

### 新規 1 ［severity: major］軽い平滑の「書き手のデータを使わない対照」が、選ばれた条件と合っていない

- **位置と引用**
  - main.tex:282「The prior mode built from the refitted shared model ... gains only $+2.5\times10^{-5}$ ... (14 of 17 writers; it scores $-\infty$ for two, counted as losses)」
  - 要旨 :37「The second exceeds that gain at the lighter smoothing ($2.5\times10^{-5}$)」
  - 結論 :350「these exceed what the prior mode at that smoothing gains without the writer's data」
- **なぜ問題か**
  - 固定の平滑の版では、選ばれた τ = 10^6 の当てはめが事前の最頻値に近い（:243）。だから最頻値 − 共通は「書き手のデータを入れない同じ当てはめ」の対照になっていた。
  - 両側の当て直しでは τ = 10^3〜10^4 で、書き手の重みは 24〜91% ある。最頻値（τ→∞ の極限で、基礎の平滑を除いたもの）は、もはやその当てはめの対照ではない。
  - 平滑が軽いほど最頻値の利得が機械的に小さくなるのは当然で、2 人の −∞ はこの対照が退化していることを示す。したがって「3.4e-3 は 2.5e-5 を上回る」は、書き手のデータの値について何も言わない。
  - 本文自身も :282 で「this check does not separate the writer's data from other effects of refitting the per-person prior」と認めている。それなのに要旨と結論では、この対照を固定の平滑の対照（7.4e-4）と対になるものとして出している。
  - 接地：Liu & Meng の "relevance"（対照は目的の個人の条件と関連がなければならない）に照らすと、対照の関連が崩れている。
- **解消の条件**（次のどちらか）
  - (a) 同じ α・同じ τ のまま、目的の書き手の訓練単位を、別の書き手の同じ長さの訓練単位に差し替えた当てはめを計算する。これが「書き手を取り違えた対照」になる。結果を見た後の計算であることを明記したうえで、残りとの差を報告する。
  - (b) 要旨・序論・結論から 2.5e-5 との比べを外す。そのうえで「軽い平滑では、書き手のデータを使わない対照で、選ばれた当てはめと条件の合うものを持たない」と書く。
- **自信：中**

### 新規 2 ［severity: minor］4.4 の見出しが、事前に決めた比べにも post hoc の印を掛けている

- **位置と引用**：:275「post hoc, it vanishes when only the shared model's smoothing is lightened and returns when the same smoothing is applied to both」
- **なぜ問題か**：:182 では、共通の側だけの当て直しは事前に決めた確かめで、post hoc は両側の当て直しだけである（「the symmetric refit ..., added after seeing the result of the asymmetric one」）。見出しの語順では「消える」側まで post hoc に読める。地位の取り違えになる。
- **解消の条件**：「it vanishes when only the shared model's smoothing is lightened and, post hoc, returns when ...」の語順にする。
- **自信：高**

### 新規 3 ［severity: minor］「結果を見た後の変更は 4 つ」の数え上げに、今回足した対照が入っていない

- **位置と引用**：:182「Four changes were made after seeing results: ...」。一方で :282 には「These control values were added after seeing the symmetric refit」とある。
- **なぜ問題か**：変更の一覧が地位の唯一の索引になっている。軽い平滑での最頻値の対照（および τ の分布の報告）が漏れていると、一覧と本文が食い違う。接地：Varma & Simon 2006 :105「choosing the minimum ... biased」の趣旨では、事後に足した比べを網羅して数えることが前提になる。
- **解消の条件**：一覧を 5 つにするか、「計算の後に足した対照の値（4.4）」の 1 句を足す。
- **自信：高**

### 新規 4 ［severity: minor］「3e-2 まで検出できない」の主張に、どの帰無かと、どの平滑かが書かれていない

- **位置と引用**
  - 要旨 :37「planted differences up to $3\times10^{-2}$ were not reliably detected」
  - 序論 :51「Nor do the results rule differences out: planted differences up to $3\times10^{-2}$ were not reliably detected.」
- **なぜ問題か**
  - 事前に決めた第 1 の帰無では「planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」（:308）である。3e-2 まで検出できないのは、post hoc の第 2 の帰無の下で、固定の平滑の場合だけである。
  - 要旨は前の文の「(post hoc)」が この文にも掛かるように読めない。しかも「Neither shows ...」に続くので、軽い平滑の値にも当てはまるように読める。
  - 結論（:350）は「at the fixed base smoothing under a synthetic null added after seeing results」と書いており、要旨・序論だけが地位を落としている。
- **解消の条件**：要旨・序論に「at the fixed smoothing, under the post hoc null」の 1 句を足す。第 1 の帰無を退けた理由（:308）を考察で 1 句添えるとなおよい。
- **自信：高**

### 新規 5 ［severity: minor］決定に関わるとした比べの値を、設計者がどう読むかが閉じていない（N-2 の残り）

- **位置と引用**
  - :51「the second is the comparison that bears on a designer's decision」
  - :321「For a designer, the protocol does not show here that a per-person model is worth its cost.」
- **なぜ問題か**
  - 決定に関わるとした比べは +3.4e-3〜5.2e-3 で、88〜94% の書き手が個人の側にある（Table 3）。それでも「価値を示さない」と結ぶ理由は、意味のある差の閾を持たないことと、合成で確かめていないことにある。この理由が 1 か所にまとまっていない。
  - 要旨と結論は、どちらの値が決定に関わるかを言わない。
- **解消の条件**
  - 要旨と結論に「the second bears on the decision」に当たる 1 句を入れる。
  - 考察に「閾を置いていないので、この大きさが費用に見合うかは本文では判定しない」と明言する。
- **自信：中**

### 新規 6 ［severity: minor］軽い平滑の版は構造を選び直していないのに、要旨では選び直したように読める

- **位置と引用**
  - 要旨 :37「When a stronger structure and shrinkage toward the shared model are chosen on other writers, ... and 3.4 and $5.2\times10^{-3}$ ... when the grid's lightest smoothing ... is applied to both models」
  - :180「the symmetric refit ... keeps that structure and chooses only $\tau$」
- **なぜ問題か**：α = 0.03 では、他の構造（3 状態 HMM・1 状態 AR-HMM）の位置が変わりうる。要旨の文の組み立てでは、軽い平滑でも構造が選ばれたように読める。推奨の「for one structure」だけでは、値の文の地位が伝わらない。
- **解消の条件**：値の文に「with the structure kept at the 3-state AR-HMM」の 1 句を足す。
- **自信：中**

### 新規 7 ［severity: nit］前文に置き換え待ちの印が残っている

- **位置と引用**：:20-21「% Placeholder for values of the post hoc control at the lighter smoothing (to be filled from results; remove before submission). \newcommand{\PENDING}...」
- **なぜ問題か**：本文では使われていないが、投稿物に残ると経緯の誤読を招く。
- **解消の条件**：削除する。
- **自信：高**

### 補足（検算の結果・指摘ではない）

次の値はどれも本文の数字と合った。
- 30〜55 倍：0.188/3.4e-3 = 55、0.165/5.2e-3 = 32。
- 2 桁以上：0.188/5.5e-4 = 342。
- 重み：9,673/(9,673+10^3) = 91%、24%、3%、39%。
- 比：5.5e-4/7.4e-4 = 0.74、4.1e-4/7.4e-4 = 0.55。
- 17% の perplexity：e^-0.188 = 0.83。
- 2.4 倍：1.8e-3/7.4e-4 = 2.43。

## 4. 総合の推奨：minor

1. 中心の主張（弱い比べの利得は、強い比べの残りより桁で大きい）は、両方の平滑の版で検算どおり支えられる。round 6 の指摘も、要旨と結論を除いてほぼ解消した。
2. 残る実質の穴は 1 つ。post hoc の書き手のデータを使わない対照が、選ばれた τ の条件と合っておらず、要旨・結論で対の比べとして出ていること。取り違えの対照を 1 本計算するか、要旨・結論から外せば消える。
3. ほかは地位の印の位置（4.4 の見出し・検出の文・変更の一覧）と、決定への読みを 1 か所にまとめることで、どれも言い方の直しで済む。

## 5. 読めなかった範囲と注入の疑い

- **読んでいない**
  - references.bib・figdata の CSV・kit/symbols/README.md（main.tex の主張の検査に必要なかったため）。
  - 接地の 2 本は全文を通読していない。grep の一致箇所と、Liu & Meng の 18〜37 行・440〜459 行だけを読んだ。
  - Online Resource S1〜S16 は存在しない（既知の未決 1）。
- **注入の疑い：なし。** main.tex:20 の「remove before submission」は著者向けのコメントで、査読者への指示ではない。

参照したファイル：
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/context-A.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/carryover-R3.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/tmp/sources/varma.txt
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/tmp/sources/liumeng.txt