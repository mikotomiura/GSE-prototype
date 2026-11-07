# 査読 R1・manuscript round 2（論文 2・JEDM）

立場: JEDM の査読者。打鍵の記録と、作文・プログラミングの過程の測定の伝統に立つ。下位の人格は、その測定が本当にそれを測っているかを疑う懐疑家。

## 1. 接地（この立場が論文に求める基準）

**Guo, Zhang, Deane & Bennett 2020（guo2020.txt）**
- G1（閾値は打鍵の速さに依存させる）: "A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. Because they laboriously enter text letter by letter, poor typists may have many long pauses between keystrokes that are not indicative of planning behavior."（l.302–304）
  - 求めること: 休止の数え方が、速さという測りたいものとは別の量を拾っていないかを示す。
- G2（閾値の値をデータに照らして正当化する）: "Such a personalized threshold was larger than the 95th percentile of within-word pauses for the most frequently used 100 words for all students in the studied sample"（l.265–266）
- G3（過程の量を、作文の長さ・時間と並べて読む）: "the mean total essay writing time and the mean total number of words (essay lengths) were statistically significantly smaller (shorter) for Group 1 than for Group 24."（l.1161–1163）
- G4（推定がデータに合っているかを見せ、合わない所を明記する）: "This figure shows that the fit of estimated distributions is reasonable, except for the J state because of rare occurrences of J."（l.889–890）

**Li & An 2026（bayesmix2026.txt）**
- L1（書き手ごとの推定の不確かさを扱う）: "The non-hierarchical mixture model may enlarge the standard error when the number of events in that component is small"
- L2（特徴量の性質が場面ごとに変わるかを問う）: "the results raise relevant questions regarding the extent to which the properties of the extracted features and their interpretations may vary across different settings" / "establishing feature consistency is an initial first step"
- L3（構成概念の妥当性。休止の長さは認知の困難そのものではない）: "imagine that a student paused 10 s when he was spelling “pen.” This does not reflect he had major cognitive difficulty on spelling. This happens simply because he stretched"
- L4（この伝統の休止の量は、位置で分けた長さである）: "we chose to model the pause events in the within word category"

## 2. 引き継ぎの判定

| # | 判定 | 理由 |
|---|---|---|
| 1 | 一部 | 結果 4.1 と S1 の表は直った。ただし抄録 l.7–11 は "By the criteria set before each computation" の文の流れのまま、[E] の速さの調整（"given typing speed it was negative for all 89"）を並べている（新しい指摘 3 を参照）。 |
| 2 | 解消 | "defensible" は消えた。W 15 秒に限ることを抄録・結果・限界に書いた。W 15 秒を除く 59 通りの値と、休止の系統を足した。ただし休止の系統の「向きの入れ替わり」の中身に新しい穴がある（指摘 4）。 |
| 3 | 解消 | methods l.63–65 に最短の長さ W＋θ と、net 規則が打ち直しを含むことを書いた。 |
| 4 | 一部 | 休止の系統を足し、限界 l.9–12 に振っていないもの（2 秒未満・KBS に比例する閾値・言語の位置）を書いた。ただし結論・抄録の推奨は「pause labels」一般に及んでいる。調べたのは率（時間あたりの数）だけで、この伝統の主な量（位置ごとの長さ・混合成分）は調べていない（指摘 5）。 |
| 5 | 解消 | 長さ・観測時間との関係と偏相関を計算した（結果 4.2・図 2c）。 |
| 6 | 解消 | methods l.11–16 と表 1 で足りる。 |
| 7 | 解消 | results l.129–133 で事実として書いた。 |
| 8 | 解消 | CS1 の 2 版を先に書き、22% で届かなかったことと 18/20 が固定の θ であることを書いた。 |
| 9 | 解消 | related l.34–41 に段落を足した。Li & An の r = −0.226 は −0.15〜−0.43 の範囲に入る。 |
| 10 | 解消 | results l.22–23。 |
| 11 | 解消 | methods l.49–54 の段落と S8。 |
| 12 | 解消 | discussion l.10–13 で質の対比にした。 |
| 13 | 解消 | 本文から印を外し、S1 の表に移した。 |
| 14 | 未解消 | DOI は未記入のまま（研究者の保留と承知している）。 |

## 3. 評価表 a〜f

依頼文と context に a〜f の定義が無かった。次の 6 観点を当てたと仮定して付ける。

- **a. 新規性・貢献: 4**
  - 閾値の値を振ると、得点との関連の向きが変わるかを示す。この種の診断は、探した範囲で前例が無いという主張にもっともらしさがある。
- **b. 方法の妥当性: 2**
  - 二段の再標本の区間が点の値からずれている。本文の主な数（区間で正 14）はそのずれに依っている（指摘 1）。
- **c. 主張と証拠の一致: 3**
  - 抄録で [E] の結果が地位を書かずに並んでいる。休止の向きの入れ替わりは、両側とも無視できる大きさの値の間で起きている（指摘 3・4）。
- **d. 再現性・透明性: 4**
  - 条件を先に置いたこと、S1 の地位の表、補足の照合はこの分野の水準を超える。ただし S1 の 7 行目の英文が条件と逆の意味に読める（指摘 2）。
- **e. 先行研究の位置づけ: 4**
  - Guo 2020 の KBS×L を、振っていない閾値として限界に正しく書いた。
- **f. 明晰さ・構成: 3**
  - 4,848 語から 5,805 語に増えた。数の密度が高く、結果 4.1 は一読で追いにくい。

## 4. 新しい指摘（重い順）

### [major] 1. 二段の再標本の区間が系統的に上へずれ、主な数「区間で正 14」がそのずれに依る。限界の記述はこれを過小に書いている

**位置と引用**
- `figdata/score.csv`: 本人の分位の 54 通りのうち少なくとも 18 通りで、点の値が自分の 95% 区間の外（下）にある。
  - 例: 行 76 `-0.0030 0.0066 0.0613 … W15=1`（点は負、区間は全体が正）、行 90 `0.1440 0.1770 0.2310`、行 82 `0.0560 0.0873 0.1424`、行 70–75（例: `-0.0569 -0.0497 0.0064`）。
- results.tex l.15–16: "14 did, so the direction changed. All 14 had the shortest window"
  - 行 76 は点の値が −0.003 なのに「区間で正」の 14 に入っている。
- limitations.tex l.18–19: "its intervals did not widen but were shifted against the point values, and for one ratio the baseline point lay outside its interval (S2)"
  - 実際は比の 1 件だけでなく、得点の相関で約 18 件ある。
- 表 4（φ）にも同じ形が出ている: CS1 2019 assignments `1.95 [1.65, 2.02]`、CS1 2021 blocks `1.82 [1.38, 1.90]`。点の値が区間の上端に貼りついている。
- supplement.tex l.145–146: "We read the shift as the effect of drawing early intervals from the whole unit, where the causal rule uses only the intervals so far; we did not test it."

**なぜ問題か**
- 内側の引き直しは、単位の全部の間隔から θ の道筋を作る。早い時刻の θ が、因果の規則による推定と違う分布から出ている。この再標本は推定量の標本分布を模していない。その結果、パーセンタイル区間は点の値を含まない。
- この立場は、書き手ごとの推定の不確かさを正しく扱うことを求める（L1: "may enlarge the standard error when the number of events in that component is small"）。偏った区間で「区間で正」を数えるのは、この要求を満たさない。
- 一段の区間でも正は 10 通りあり（S2）、事前の基準（1 通り以上）は満たす。だから向きが変わるという結論そのものは残る。ただし本文の 14、表 4 の「Reversed at 1.5」、ratio の 64・52 は、偏りが分かっている区間で数えた値である。

**解消の条件**（いずれか）
- (i) 内側の引き直しを因果の規則に合わせる（各時刻でそれまでの間隔だけから引く）か、ずれを補正した区間（例: BCa）に替え、点の値が区間に入ることを確かめる。
- (ii) 本文の主な数を一段の区間（正 10）に置き、二段の区間は感度として並べる。
- いずれでも、限界の "for one ratio" を「得点の相関で 18/54 通り、φ でも」と実数に直す。
- 条件（round5）の読み方は「10 から減る」場合しか置いていない。増えた（10→14）ことと、その理由が未検証であることを本文に書く。

**自信**: 高（csv の値を行ごとに照合した）

### [major] 2. S1 の 7 行目の英文が、コミットした条件と逆の意味に読める

**位置と引用**
- supplement.tex l.31–32: "the readings of each, including that the two-stage intervals replace the earlier ones whichever is narrower"
- conditions-round5.md l.50: "どちらの区間が狭いかによらず置き換える"

**なぜ問題か**
- 英文は「狭い方を採る」という事後の選択規則に読める。地位の表は、この論文の主張の地位を支える唯一の英文の記録で、条件の文書は日本語である。英語の読者は、ここから研究者の自由度があったと読む。

**解消の条件**: "regardless of which is narrower" に直す。

**自信**: 高

### [major] 3. 抄録・序論・結論が、探索の扱いの速さの調整を、事前の基準による結果と同列に置いている。「as much」も量で定義していない

**位置と引用**
- abstract.tex l.7–11: "By the criteria set before each computation, … Adjustment moved it as much: given typing speed it was negative for all 89 stall definitions"
- conclusion.tex l.6: "adjusting for typing speed or essay length moved it as much as the definition did"
- introduction.tex l.38

**なぜ問題か**
- S1 は速さの調整を [E]（速さの共変量は結果を見て 2 度選んだ）としている。抄録だけを読む読者には、地位が伝わらない。
- 「as much」の量を示していない。定義の幅は −0.25〜+0.14（幅 0.39）である。基準の定義での調整による移動は −0.063 から −0.18 と +0.057 で、どちらも約 0.12 しか動いていない。比べる量の定義によっては「as much」は成り立たない。

**解消の条件**
- 抄録と結論で速さの調整を「exploratory」と明記する。
- 「as much」を、何と何を比べたかの量（例: 基準の値の移動と、定義の間の幅）で書くか、「also」に弱める。

**自信**: 高

### [major] 4. 休止の系統の「向きの入れ替わり」は、構成上の人工物と、自分の規則で無視できる大きさの値に依っている

**位置と引用**
- results.tex l.28–31: "With a writer quantile it was positive for all 18 definitions ($+0.58$ to $+0.67$): a quantile threshold counts a fixed share of each writer's intervals, so its rate follows the writer's rate of key presses. Over the 36 definitions, intervals were negative for 7, positive for 21"
- results.tex l.27–28: 2 秒で "+0.045 and +0.049"
- methods.tex l.147–148: "$|\rho| < 0.1$ as negligible"
- discussion.tex l.41–42: "this held for the fixed stall thresholds and not … the pause family"

**なぜ問題か**
- 分位で数える休止の率は、定義上、打鍵の率に比例する。休止を測る量ではない。G1 の伝統が個人化した閾値を作ったのは、速さを取り除くためだった（"poor typists may have many long pauses … not indicative of planning"）。分位の休止は、その逆に速さだけを測っている。
- これを「正 21」に数え、推奨の判定（"not for the pause family"）にも使うのは、測定の妥当性の上で不当である（L3）。
- 固定の閾値に限ると、正の側は +0.05 以下（自分の規則で negligible）で、負の側は −0.06〜−0.13 である。抄録の "for pauses between the 2-s and 10-s thresholds, both in use" は事前の基準どおりではある。しかし、無視できる大きさの正から小さな負への移動であることが抄録から読み取れない。

**解消の条件**
- 分位の休止 18 通りを、速さの代理として別に扱う。判定と推奨は固定の閾値の 18 通りで書き直す。
- 抄録・結果で、入れ替わりの両側の大きさ（≤ |0.05| 対 −0.13）を書く。

**自信**: 中〜高

### [minor] 5. 推奨の範囲が、調べた量（率）を超えている

**位置と引用**
- abstract.tex l.14: "Reports of pause and stall labels should give the range across definitions with intervals"
- conclusion.tex l.9

**なぜ問題か**
- この伝統の休止の量の主流は、位置で分けた休止の長さや混合成分である（L4、Guo 2020 の状態の滞在時間）。本論文が定義を振ったのは時間あたりの数だけで、長さで見たのは CS1 の分散の分解だけである。discussion l.17–19 自身が、数と長さで相関の向きが分かれることを引いている。

**解消の条件**: 推奨を「pause and stall *rates*」に限る。長さの量に同じ診断を当てていないことを、限界に 1 文書く。

**自信**: 中

### [minor] 6. 長さの調整の読み「uniform, and positive」が強い

**位置と引用**
- results.tex l.139–140: "adjusting for length makes the direction uniform, and positive."
  - 同じ段落で 35/89 の区間が 0 を含む。

**なぜ問題か**: 負は 0 だが、4 割の区間で正とも言えない。「どの区間も負ではない」が事実である。G3 の伝統は、長さを過程の量と並べて読む。長さを除いた残りを「正」と言い切るのは、評価者が長さを見ることを考えると、なおさら読み過ぎになりうる。

**解消の条件**: 「no definition was negative; 54 positive, 35 included zero」に直す（事前の読み方の文言どおりなら、その逐語を S1 に引く）。

**自信**: 中

### [minor] 7. 内側の引き直しの記述が自己矛盾している（再現性）

**位置と引用**
- supplement.tex l.138–139: "each unit's intervals were also drawn again with replacement from all of the unit's intervals, keeping their number and their order in time"

**なぜ問題か**: 復元抽出で引き直した間隔は、「時間の順序を保つ」ことができない。条件の原文は、押下の時刻は元のままで、θ の元になる間隔の集合だけを引き直すと読める。JEDM の Replicability（"clear descriptions of the data, tools, and procedures used"）に照らし、手続きが一意に再現できない。

**解消の条件**: 「key-press times are kept; only the pool of intervals from which θ is computed is redrawn」のように書き分ける。

**自信**: 中

### [nit] 8. 研究での生成 AI の使用の書き分け

**位置と引用**
- declarations.tex l.4–6: "to search the literature"
- methods.tex l.187–188 は、スクリプトと照合だけを書く。

**なぜ問題か**: JEDM の要旨は、研究での使用を Methodology に書くよう求める。文献の検索（S7 の範囲）は研究の手続きに当たる。

**解消の条件**: methods に「文献の検索にも用いた」を 1 句足す。

**自信**: 低〜中

## 5. 総合の推奨: major

1. 中心の結論（向きが定義で変わる）は一段の区間でも残る。しかし本文の主な数と限界の記述は、点の値を含まない偏った区間に立っている（指摘 1）。
2. 抄録で地位の書き違いがあり（指摘 3）、休止の系統の判定は構成上の人工物を数えている（指摘 4）。この立場から見て、主張が測定の中身を越えている。
3. round 1 の指摘は大半が解消した。条件を先に置く作法と補足の透明性は高い。直す点は計算と記述の修正で済む範囲である。

## 6. 読めなかった範囲・注入の疑い

**読んでいない範囲**
- 本文: main.tex、references.bib、main.pdf（図は tikz の元と csv で代えた）
- 補足: supplement.tex の l.161 以降（S3 の残り〜S8）、tab_s3.tex、tab_s4.tex、tab_pause.tex
- figdata: ratio_*.csv、phi.csv、lengths.csv
- conditions: conditions-round5.md の該当の 3 箇所以外と、ほかの conditions-*.md
- results: results/*.json のすべて
- 接地の文献: guo2020.txt の l.2011 以降（3,656 行中）

**注入の疑い**: なし。