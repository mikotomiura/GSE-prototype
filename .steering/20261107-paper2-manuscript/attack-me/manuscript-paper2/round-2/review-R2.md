# manuscript round 2・論文 2（JEDM）・査読者の報告（立場: 教育データの検出と予測のモデルの評価の実務。批判的な下位人格は「で、読者は何に使えるのか」と問う実務家）

## 1. 接地（文献からの逐語）

2 本の文献から基準を逐語で抜き出せたので、査読に入った。

- G1（Gardner & Brooks 2018, Notes for Practice）: "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2（Gardner & Brooks 2018, §3.1）: 平均で選ぶ方法は "naïvely assumes that any differences observed must be due to genuine differences ... and that these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant."
  - 求めるもの: 統計で区別できることと、実務で意味のある大きさであることは別に示す。
- G3（Gardner & Brooks 2018, §3.2）: 評価の手続きが扱うべき点として "accurate estimation of statistical parameters in the presence of correlated data ... including the standard error"
  - 求めるもの: 区間の作り方そのものの妥当性。
- P1（Pelánek 2015, §7）: "Many papers which propose or evaluate student models lack any discussion of the specific purpose of described models. Such discussion or specific arguments for a particular choice of metric should become standard part of papers"
- P2（Pelánek 2015, §6.3）: "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."
- P3（Pelánek 2015, §4.2）: "Stability of parameters should get more attention and be studied for example with bootstraping experiments"
  - 求めるもの: 再標本は、推定量の揺れを正しく写すように作る。

## 2. 引き継ぎの判定（10 件）

| # | 判定 | 理由 |
|---|---|---|
| 1 | 一部 | 休止の系統（36 通り）は足された。しかし休止の向きの入れ替わりは、次の 2 つに支えられている。<br>・2 秒と 5 秒の固定の閾値で正になった 3 通り。どれも +0.05 前後で、著者自身の基準（\|ρ\|<0.1）では無視できる大きさ。<br>・本人の分位の 18 通り。これは仕組みの上で押下の率に比例する（下の新しい指摘 2）。<br>停滞の向きの入れ替わりは、今も W 15 秒（先例の無い値）の組だけにある。 |
| 2 | 一部 | 規則は数で書かれた（90% 以上の通りで区間が同じ側なら向きを書く）。しかし下流の帰結は計算していない。規則も大きさを見ず、格子の組み方に依る（新しい指摘 4）。 |
| 3 | 一部 | θ を推定し直す二段の区間は作られた。しかし 3 つの問題が残る。<br>・区間が点の値に対してずれ、ある比では点の値が区間の外に出た。<br>・正の通りが 10 から 14 に増えた。これは事前の読み方が想定しなかった向きである。<br>・逆転の数を、基準の比の 1 からの距離と並べていない。<br>（新しい指摘 1） |
| 4 | 一部 | CS1 の 2 版の比べを先に書き、限界に交絡を書いた。しかし抄録はなお、記録の方式も課題も違う組（CS1 2019 と KLiCKe）の逆転を "beyond sampling variation for most definitions" として見出しに置いている（新しい指摘 3）。 |
| 5 | 一部 | 作文の長さでの調整を計算し、抄録に並べた。しかし抄録の速さの調整（[E]）に、探索の印が無い。 |
| 6 | 一部 | 考察では「動いたものの種類が違う」に直した。しかし抄録・序論・結果の見出し・結論では "as much as" という大きさの比べが新たに入った（新しい指摘 6）。 |
| 7 | 解消 | 方法 3.1 の段落と S8 で、共有するものと新しいものを分けて書いた。 |
| 8 | 未解消 | DOI と、条件の英訳はどちらも投稿の前に回されている（著者も未解決と認めている）。 |
| 9 | 解消 | 地位の印を S1 の表に置き、序論の段落を箇条にまとめた。 |
| 10 | 解消 | "a lower interval meaning faster typing" と書いた（results.tex:124）。 |

## 3. 評価表 a〜f

読んでよいファイルの中に、a〜f の項目名の定義は無かった。下の解釈で付けた。

| 項目 | 点 | 所見 |
|---|---|---|
| a. 問いと貢献 | 4 | 定義の揺れが、得点との関連・データの間の比・書き手の中の構造の 3 つにどう効くかを並べる設計は、JEDM の "comparative analyses" に合う。手続きを一般化の単位にした（"What generalises is the procedure"）のも適切。 |
| b. 方法の妥当性 | 2 | 本文の数を置き換えた二段の区間に、自分で認めたずれがあり、検証していない（G3・P3）。本人の分位の休止の 18 通りは、押下の率と仕組みの上で重なる。著者はこの理由で、押下の率を共変量から外している。 |
| c. 主張と証拠の対応 | 2 | 次の 4 つがある。<br>・「向きが変わる」は、無視できる大きさの中での符号の入れ替わりに依る。<br>・抄録の比の逆転は、著者が「弱い」と呼んだのと同じ組のものである。<br>・長さの調整は「uniform, and positive」と書かれているが、自分の 90% の規則を満たさない。<br>・φ の逆転は、基準の点の値自体が 1.5 をまたぐ区間で数えている。 |
| d. 実務への有用性 | 2 | 規則は在る。しかし大きさの帯が無く、格子の決め方も無いので、実務家が別のデータで同じ判定を再現できない。下流の帰結も無い（P1・P2）。 |
| e. 再現性 | 3 | 条件を先にコミットし、変異の検査と陽性の対照を付けた点は強い。DOI が未記入で、条件は日本語。S1 の地位の印に書き違いが 1 つある（新しい指摘 5）。 |
| f. 書き方と構成 | 3 | 簡潔で、限界も正直に書いている。ただし改訂で入った "as much as" と、区間の種類の混在（一段と二段）が読み手を誤らせる。 |

## 4. 新しい指摘（重い順）

### [major] N1. 本文の数を置き換えた二段の区間が、点の値からずれる推定量になっている。見出しの数（正が 14）はそれに依る

- **位置と引用**
  - supplement.tex:142–146: "The two-stage intervals were about as wide as the one-stage ones ... but shifted ... the CS1 2019 to KLiCKe ratio interval [0.807, 0.861] no longer contained the point value 0.865. We read the shift as the effect of drawing early intervals from the whole unit, where the causal rule uses only the intervals so far; we did not test it."
  - supplement.tex:146–147: "With the one-stage intervals, 10 definitions had a positive score interval instead of 14"
  - 条件（conditions-round5.md:43）: 「点の値は元の θ のまま」
  - 条件（conditions-round5.md:51）の読み方は、正の通りが「10 から減って 1 以上なら」と「0 になれば」の場合だけを書いている。
- **なぜ問題か**
  - 内側の引き直しは、単位の全部の間隔から θ の道筋を作る。点の値は、因果に累積した θ で作る。二つは別の推定量なので、percentile の区間は点の値の揺れを写さない。その結果、点の値が区間の外に出る。
  - 「向きが変わる」の数（14）と、比の逆転の数は、この区間で数え直されている。正が増えた場合は、事前の読み方に無い。
  - G3: "accurate estimation of statistical parameters in the presence of correlated data ... including the standard error"
  - P3: 再標本は、パラメータの安定性を見るために使うものである。
- **解消の条件**
  - 内側でも因果の規則を保つ引き直しにする。例: 単位の中の「その時点までの間隔」から引く、またはブロックで引く。
  - それができなければ、一段と二段の両方の数を本文に並べ、見出しの主張を両方で成り立つ数（正が 10 以上）で書く。
  - 正が増えた場合が事前の読み方に無かったことを、S1 の departures に書く。
- **自信**: 高

### [major] N2. 休止の系統の「向きの入れ替わり」は、大半が押下の率をなぞる定義から来る

- **位置と引用**
  - results.tex:28–30: "With a writer quantile it was positive for all 18 definitions ($+0.58$ to $+0.67$): a quantile threshold counts a fixed share of each writer's intervals, so its rate follows the writer's rate of key presses."
  - results.tex:30–31: "Over the 36 definitions, intervals were negative for 7, positive for 21 ... so by the same criterion the direction changed."
  - 押下の率を外した理由（supplement.tex:62–64）: 押下の率は "divides presses by a time that contains the stalls themselves"
- **なぜ問題か**
  - 単位の分位で数える休止の率は、ほぼ「分位の割合 × 押下の率」で決まる。押下の率と得点の相関は 0.62（supplement.tex:165）。だからこれは休止の構成概念を測っておらず、押下の率と同じものを数え直している。
  - 正の 21 通りのうち 18 通りがこれである。固定の閾値だけで見ると、正は 3 通り（+0.045・+0.049 と 5 秒の 1 通り）で、どれも著者の基準で "negligible"。
  - G2: 統計で区別できることと "practically significant" は別に示す。
- **解消の条件**
  - 本人の分位の休止を「押下の率の対照」として分けて示す。
  - 休止の向きの主張は固定の閾値の 18 通りだけで書き、正の値が無視できる大きさであることを抄録にも書く。
- **自信**: 高

### [major] N3. 抄録の見出しにある比の逆転は、著者が順位の比べで「弱い」と呼んだのと同じ近い組であり、二段の区間が点の値を外した組でもある

- **位置と引用**
  - abstract.tex:11–12: "The ratio of stall rates between a programming course and the essay corpus reversed beyond sampling variation for most definitions"
  - results.tex:151–152: "this is a weak result, because the baseline rates of CS1 2019 and KLiCKe are close and their swap alone accounts for 11 of the 80."
  - results.tex:157: "CS1 2019 against KLiCKe (baseline ratio 0.86) reversed for 64"
  - 先にコミットした組は届いていない（results.tex:155–156）: "20 of 89 definitions (22%) reversed the ratio, below the 25%"
- **なぜ問題か**
  - 基準の比が 0.86 なので、1 をまたぐのに要る動きは小さい。順位の比べでは弱さの理由として挙げた近さが、比の逆転の見出しでは消えている。
  - この組の基準の区間 [0.807, 0.861] は、点の値 0.865 を含まない（N1）。
  - 先にコミットした組（CS1 の 2 版）は基準に届いていない。それなのに、コミットしていない組が抄録の見出しに立っている。
  - 加えて、この組は記録の方式と課題の両方が違う。
- **解消の条件**
  - 抄録は、先にコミットした組の結果（22%・基準未満）を先に書く。
  - 逆転の数を、基準の比の 1 からの距離と並べる。
  - 「most」は、近い組であることと交絡の注記をつけて結果の節に移す。
- **自信**: 高

### [major] N4. 勧める規則が、大きさの帯も格子の決め方も持たず、著者自身の結果にも当てられていない

- **位置と引用**
  - discussion.tex:40–42: "report a direction only if the intervals of at least 90% of the definitions examined lie on the same side of zero ... in our grid this held for the fixed stall thresholds and not for the writer-quantile stall thresholds or the pause family."
  - results.tex:139–140: "By the reading set before the computation, adjusting for length makes the direction uniform, and positive."
  - 長さの調整の実際（results.tex:136–137）は、54 通りで正、35 通りで 0 を含む（61%）。round5_length.json では中央値が +0.043、最大が +0.135。
  - methods.tex:106: proportions "describe this grid, not a sample of possible definitions"
- **なぜ問題か**
  - 長さで調整した値は、著者の 90% の規則では「向きを書かない」に当たる。しかも著者の大きさの基準では、ほぼすべてが無視できる。それでも本文は "uniform, and positive" と書く。
  - 規則は「調べた通りの割合」で決まる。何を格子に入れるかで結論が変わる（例: 先例の無い W 15 秒を入れるか）が、格子の決め方は "its range in prior practice and around the default" だけで、それに著者自身の W 15 秒が反する。
  - 実務家は、別のデータで同じ判定を再現できない。
  - P1・P2（"interpretable and actionable"）。G2（practically significant）。
- **解消の条件**
  - 規則に等価の帯（例: \|ρ\|<0.1 は「関連なし」）を入れ、3 値で判定する（向きあり／無視できる／定義に依る）。
  - 格子の作り方を規則の一部として書く（先例のある値だけで作る格子と、外側を足した格子の両方で判定する）。
  - 長さの調整の文は、規則に合わせて書き直す（「負は無く、大きさは無視できる」）。
- **自信**: 高

### [minor] N5. 比の逆転の結論の地位を [A] としているが、定義に照らすと [A] に当たらない

- **位置と引用**
  - supplement.tex:54: "Rate ratios reverse beyond sampling variation (criterion set after seeing reversed point values) & [A]"
  - [A] の定義（supplement.tex:38–39）: "quantity and criterion committed before that quantity was seen"
- **なぜ問題か**: 基準（25%）は、逆転した点の値の数を見た後に置かれた（methods.tex:181–183）。区間の数は見ていなくても、点の値の数は区間の数を強く予告する。この結論は [A] ではなく、[D] か、新しい印に当たる。G1（評価の手続きを明確に書く）。
- **解消の条件**: 地位を書き直すか、[A] の定義に「点の値を見た後」の下位の印を足す。
- **自信**: 中〜高

### [minor] N6. "as much as" が、測っていない大きさの比べとして改訂で入った

- **位置と引用**
  - abstract.tex:10: "Adjustment moved it as much"
  - results.tex:119 の見出し: "Adjustment moves the association as much as the definition"
  - conclusion.tex:6: "moved it as much as the definition did"
- **なぜ問題か**: 定義による揺れと調整による揺れを、同じ尺度で比べた計算は無い。前の round の指摘 6 で考察から外した型が、別の場所に戻っている。
- **解消の条件**: 「調整でも向きが揃い、揃う向きは共変量で逆になる」のように、質の対比で書く。
- **自信**: 高

### [minor] N7. φ の「1.5 での逆転」を、基準の点の値自体が 1.5 をまたぐ区間に対して数えている

- **位置と引用**
  - Table tab:phi（results.tex:229–231）: CS1 2019 blocks "1.44 [1.34, 1.52]"、CS1 2021 blocks "1.82 [1.38, 1.90]"
  - 列 "Reversed at 1.5": 16 と 54
- **なぜ問題か**: 基準の区間が 1.5 を含むので、基準の結論（1.5 の上か下か）が定まっていない。そこからの「逆転」は定義されない。とくに CS1 2021 blocks の 54 は、Limitations の "unchanged except one" にも関わる。
- **解消の条件**: 基準の区間が閾値を含むセルは「基準が未定」と書き、逆転の数を出さないか、片側への移動の数として言い換える。
- **自信**: 中

### [minor] N8. 区間の種類が混ざったまま比べている

- **位置と引用**
  - methods.tex:170–171: "The pause family's quantile and the adjusted correlations keep the threshold fixed."
  - results.tex:138: "The 14 definitions that were positive without adjustment stayed positive."
  - results.tex:161–163: 100 個目の間隔より後に限った数（一段の区間・S2 で明記）を、本文の二段の数と並べている。
- **なぜ問題か**: 14 は二段、調整した値は一段で数えている。100 個目より後の数（22・66・53・8・2）は一段で数え、比べる相手（20・64・52・9・0）は二段で数えている。違いのどこまでが区間の作り方によるのか、読み手には分からない。
- **解消の条件**: 比べるときは区間の種類をそろえるか、どの区間かを本文に書く。
- **自信**: 高

### [nit] N9. 抄録の速さの調整に、探索の印が無い

- **位置と引用**: abstract.tex:10: "given typing speed it was negative for all 89 stall definitions"
- **解消の条件**: "(exploratory)" を添える。
- **自信**: 高

## 5. 総合の推奨: major

- 改訂で足した 4 つの計算は、問いに正面から答えている。条件を先にコミットした手続きも、JEDM の replicability の基準に照らして強い。
- しかし本文の数を置き換えた二段の区間には自認のずれがあり（N1）、抄録の 2 つの見出し（休止の向きの入れ替わり・比の逆転）は、仕組みの上で率をなぞる定義と近い組に依る（N2・N3）。
- 実務家に渡す規則には大きさの帯も格子の決め方も無く、著者自身の長さの調整にも当てられていない（N4）。いずれも計算か書き直しで解ける。

## 6. 読めなかった範囲と、注入の疑い

### 読んでいない
- gardner2018.txt の 530 行目以降。第 4 節の実験、第 5 節以降、結論にあたる部分。
- main.tex と references.bib。
- main.pdf。図は tex のソースだけで見た。
- appendix の tab_s3.tex・tab_s4.tex・tab_pause.tex。
- figdata の 5 つの CSV。
- conditions.md・conditions-length90.md・conditions-round1〜4.md。
- results の JSON。round5_length.json の一部（55〜139 行）だけを読み、本文の 54/35/0 と 59/0 が一致することを確かめた。
- conditions-round5.md は 36〜80 行だけ、conditions-round7.md は grep の行だけを読んだ。
- tmp/sources の jedm_aims.txt と jedm_submissions.txt は読んでいない。

### 評価表の項目名
a〜f の項目名の定義は、読んでよいファイルの中に見つからなかった。上の解釈で付けた。

### 注入の疑い
無し。読んだ範囲の接地の本文・原稿・条件の中に、査読者や LLM に向けた指示は見つからなかった。declarations.tex:3 の "% The wording below follows the journal's required sentence." は著者向けのコメントで、指示ではないと判断した。