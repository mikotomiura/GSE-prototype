## 査読 R2（UMUAI・個人化した行動のモデルの実務の立場）round 9・stage manuscript・対象 commit 1f4f4b5b

### 0. 引き継ぎの判定（round 8 の指摘）

| round 8 | 判定 | 位置と逐語 |
|---|---|---|
| minor 1 「more than half」の算出と、入れ替えが不一致の罰を含むこと | 解消 | main.tex:282 「the reading fixed before the computation (a margin of at least half the remainder) holds」「The margin is not a share of the remainder, since it also contains the loss from fitting another writer's data」「another writer's $k$ sessions may hold a different number of symbols, which changes the weight $\tau$ leaves them」 |
| minor 2 入れ替えの差と植えた差の桁 | 解消 | main.tex:321 「The margin of the swap control, up to $2.5\times10^{-2}$, is not on the scale of the planted differences, since it includes the loss from fitting another writer's data.」 |
| minor 3 決定の段の冒頭が無条件・費用の目安 | 一部 | 冒頭の限定と場面の例は入った（main.tex:319 「the protocol does not show here, at the fixed base smoothing, that a per-person model is worth its cost」「A writing assistant that times hints by a writer's predicted state ... whether a difference of this size changes its decisions was not measured」）。費用の目安（人ごとに保存する母数の数〔3.3 節に 2,033 とある〕、k 単位を待つ時間〔1 単位は約 11 分〕）を決定の段に結び付けていない。加えて、足した例が新しい矛盾を生んだ（下の指摘 2）。 |
| minor 4 入れ替えの対照を推奨に入れる | 解消 | main.tex:331 「is a cheap candidate check of whether a per-person fit draws on the person's own data, although here it did not separate the person from closeness in time or from the amount of data」 |
| nit 5 「left the median remainder unchanged」 | 解消 | main.tex:321 「left the median difference from choosing on the reported half at zero」 |
| nit 6 結果が方法の節にある | 解消 | main.tex:286（4.4 節）に値を移した。3.4 節（main.tex:178）は 「a check without them is in Section~\ref{sec:res-smooth}」の参照だけ |
| nit 7 Saeb の days | 解消 | main.tex:45 「record-wise splits that mix a person's records」、main.tex:57 「splits that mix a person's records across training and test」 |
| nit 8 fixed smoothing の揺れ | 解消（名残が 1 つ） | 「fixed smoothing」は grep で 0 件。ただし main.tex:180 に未定義の呼び名が残る: 「added after seeing the result of the asymmetric one」（下の指摘 9） |

### 1. 接地（この立場が論文に求める基準・逐語）

1. 評価の分け方は使う場面に合わせる。Saeb et al. 2017: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
2. 人ごとのモデルなら時間で分ける。Saeb et al. 2017: "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times."
3. 選び方（ハイパーパラメータ）が評価のデータを使わない。Saeb et al. 2017: "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
4. 素朴な人ごとの基準と比べる。Aalbers et al. 2023: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model. This "naive" baseline model always predicts an individual's average level of stress."
5. 精度を人ごとに評価して、人による違いを示す。Aalbers et al. 2023: "We evaluated model accuracy on a person-to-person basis in out-of-sample observations." および "MAE varied from individual to individual, but for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline."
6. 使う側が読める単位で効きを言う。Aalbers et al. 2023: "it allows us to make statements such as "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale)."" と、実用の結論 "Although performance should be improved to make clinical application feasible"

### 2. 評価表

- **a 主張と根拠の一致: 4** 中心の発見（弱い比較での利得 0.19 と、強い比較での残り 5e-4）は表 2・図 2・figdata（fig2_p15_joint.csv は表 2 の値と一致）で支えられている。入れ替えの対照の読みは、計算の前に決めた規則と交絡の断りで適切に限られた。残るずれは 2 つ。要旨では、検出の限界がどちらの値に掛かるかが曖昧なこと（指摘 1）。決定の段の例が、隠れ状態を読まないという限界と食い違うこと（指摘 2）。
- **b 方法の穴: 3** 選択が他の書き手で行われ、時間で分けていて、評価の単位が選択に入らない（接地 2・3 を満たす）。ただし、決定に関わる対称の再当てはめは、α が格子の端にあり、合成の書き手で確かめておらず、構造を 1 つに固定している（著者も認識）。さらに、本文の中でその値に区間が無い（指摘 3）。
- **c 持ち帰れるもの: 3** 「自分の一次マルコフ連鎖を並べて当てる」は安く、使う側がそのまま使える（main.tex:317 「fitting the person's own first-order chain alongside is a cheap check」）。一方、決定に関わる値「0.3 to 0.5% more probability per symbol」を、使う側の費用（保存・待ち時間）や下流の決定に結び付ける目安が無い。推奨 (2) の α を何で選ぶかも書かれていない（指摘 4）。
- **d 簡潔さと構成: 3** 本文は 7,494 語で、前の版より 231 語増えた。4.4 節の入れ替えの段（main.tex:282）は 1 段に 8 文を詰めていて、実務の読者には重い。後足しの印（post hoc・not prespecified・reported post hoc）が 1 文に重なる箇所もある。
- **e 規程への適合: 4** 要旨 241 語（規程 "150 to 250 words"）、キーワード 6 個（"4 to 6 keywords"）、"Statements and Declarations" の見出しの下に Data availability・Ethics・Consent があり、規程に合う。本文の語数に上限は無い。Springer の様式への移行は既知の未決なので判定に数えない。
- **f 先行研究の位置づけ: 4** Aalbers・DeMasi・Saeb・Little・LiuMeng・Fowler/Shao/Adhikary と、「部品は新しくない」という断り（main.tex:51）が適切。Uto 2020 の窓（10 秒の歩み）が本文の 2 つの記号化の間にあることを明示しているのも良い（main.tex:323）。

### 3. 指摘の一覧（重い順）

- [severity: minor] 要旨で、検出できなかったという記述がどちらの値に掛かるかが曖昧（書き換えた部分）
  - 位置と引用: main.tex:35（要旨）「Neither value shows a per-person difference; under the post hoc null, planted differences up to $3\times10^{-2}$ were not reliably detected.」
  - なぜ問題か: この文は 2 つの値（固定の基の平滑の約 5e-4 と、対称の再当てはめの 3.4e-3・5.2e-3）の直後にある。そのため、検出の限界が両方に掛かると読める。実際の検出の較正は固定の基の平滑だけで行われている（main.tex:343 「The synthetic check calibrates detection at the fixed base smoothing only」、main.tex:49 序論では「at the fixed base smoothing」と限っている）。要旨しか読まない実務家が、決定に関わる値についても検出の力が測られたと誤って受け取る。
  - 解消の条件: 要旨のこの句に「at the fixed base smoothing」を足す（序論 main.tex:49・結論 main.tex:352 と同じ限定にする）。
  - 自信: 高

- [severity: minor] 決定の段に足した適応の場面の例が、「隠れ状態を読まない」という限界と食い違う（書き換えた部分）
  - 位置と引用: main.tex:319 「A writing assistant that times hints by a writer's predicted state, for example, would act on such probabilities」。対して main.tex:339 「Hidden states are not named and are not read as cognitive or affective states」
  - なぜ問題か: 本文が予測するのは次の秒の記号（30 秒の打鍵のリズム）であり、「state」ではない。論文は隠れ状態に意味を与えないと明言している。それなのに、例の中心が「writer's predicted state」になっている。使う側は「この模型で状態を推して介入の時機を決められる」と持ち帰りかねない。これは限界の節と矛盾する。さらに、1 記号あたりの平均の対数尤度は、時機の決定に効く特定の遷移（たとえば打鍵から休止に移るところ）での差を平均の中に隠しうる。この例が成り立つには、どの記号での差かが要る。
  - 解消の条件: 例を記号の水準に書き換える。たとえば「times hints by the predicted probability that the next seconds are a pause」。あるいは「predicted state」に、状態は解釈しない、という断りを添える。
  - 自信: 高

- [severity: minor] 「決定に関わる」とした値に、本文の中で不確かさが無い
  - 位置と引用: main.tex:319 「The comparison that bears on the decision is the symmetric refit ... It leaves $3.4\times10^{-3}$ at $k=5$ and $5.2\times10^{-3}$ at $k=15$」。Table 3（main.tex:298–304）の Symmetric refit の列は、中央値と割合だけで区間が無い。Split の列には区間がある。
  - なぜ問題か: 使う側が決定に使う数字に、ばらつきの手掛かりが本文に無い。区間は固定の基の平滑の行（表 2）と分割の列にはある。一方、論文自身が決定に関わるとする列だけに区間が無い。k=12 では 0.88、k=1 では 0.71 の割合で、人による差がありそうなだけに目立つ。接地 5（Aalbers: 人ごとの評価と、その違いを示す）に照らすと、これは補足へ送ってよい値ではない。
  - 解消の条件: Table 3 の対称の再当てはめの列（少なくとも k=5 と 15）に、表 2 と同じ条件付きの 95% ブートストラップ区間を添える。新しい当てはめは要らない（書き手を再標本化するだけ）。
  - 自信: 中（区間が S16 にあるかどうかは読めない）

- [severity: minor] 推奨 (2) の平滑を何の目的で選ぶかが書かれておらず、使う側が再現できない
  - 位置と引用: main.tex:327 「(2) choose structure, shrinkage and smoothing on other people, with the shared model itself among the candidates, and apply the chosen smoothing to the per-person fit and the shared model alike (here the smoothing was chosen for the shared model and shrinkage then chosen given it ...)」。要旨 main.tex:35 「choose structure, shrinkage and smoothing on other people, applying the smoothing to both models」
  - なぜ問題か: 本文で行ったのは、α を共通の模型の目的（共通の模型の当たり）で選び、そのあとで τ を選ぶ 2 段の手順である（main.tex:185 「Because $\alpha$ is chosen for the shared model, the symmetric refit is conditional on that choice」）。推奨の本文は「structure, shrinkage and smoothing を他の人で選ぶ」と 3 つを並べていて、同時に選ぶとも読める。どちらで選ぶかで結果が変わりうる（α は格子の端）。それにもかかわらず、推奨は手順を特定していない。
  - 解消の条件: 推奨 (2) の本文を、実際に行った順序と目的（"choose the smoothing by the shared model's accuracy on other people, then shrinkage given it"）で書く。同時に選ぶことは試していないと 1 句で断る。
  - 自信: 中

- [severity: minor] 決定の段に、使う側の費用の目安がまだ無い（引き継ぎ 3 の残り）
  - 位置と引用: main.tex:319 「whether such a value is worth a per-person model's data and storage is left to the designer's costs」
  - なぜ問題か: 費用の側の量は本文の別の箇所に散っている。人ごとの母数は 3.3 節の「2,033 free parameters」、データの側は 1 単位が約 11 分（main.tex:112）で、k=5 は約 55 分、k=15 は約 2.75 時間の打鍵にあたる。決定の段がこれらを 1 文で結んでいないため、使う側は効き（0.3〜0.5%）と費用を並べられない。接地 6（Aalbers の、読める単位で言うこと）に照らすと、効きの側だけが翻訳されている。
  - 解消の条件: 決定の段に 1 文足す。例:「at $k=5$ and 15 this needs about one and three hours of a writer's typing and 2,033 stored parameters per writer」。
  - 自信: 中

- [severity: nit] 要旨の「goes with the writer's most recent sessions」が実務の読者に通じない（書き換えた部分）
  - 位置と引用: main.tex:35 「this bears on a designer's decision but goes with the writer's most recent sessions and was not checked on synthetic writers」
  - なぜ問題か: 意図は「時間の近さと交絡している（入れ替えの対照が書き手と時間の近さを分けない）」ことだと思われる。しかし「goes with」は意味が定まらず、「最近の回を使う場面にだけ当てはまる」とも読める。
  - 解消の条件: 「may reflect closeness in time to the held-out sessions as well as the writer」のように、何が交絡するかを書く。
  - 自信: 中

- [severity: nit] 4.4 節の入れ替えの段が 1 段に詰まりすぎている
  - 位置と引用: main.tex:282（「Three controls were added after seeing the symmetric refit (post hoc).」から「None of the values at $\alpha=0.03$ was checked against synthetic writers.」まで）
  - なぜ問題か: 3 つの対照、計算の前に決めた規則、2 つの交絡、合成の書き手での未確認を 1 段に入れている。冗長に厳しい実務の読者は、ここで何が確かめられて何が確かめられていないかを取り出しにくい。
  - 解消の条件: 事前の対照 2 つ（prior mode）と入れ替えの対照で段を分ける。入れ替えの段は、規則 → 結果 → 交絡 の 3 文に寄せる。
  - 自信: 中

- [severity: nit] 「reported post hoc」と「post hoc」の重なり
  - 位置と引用: main.tex:280 「Every writer is given (reported post hoc) $\tau=10^4$ at $k=5$」
  - なぜ問題か: 段の冒頭で「In the symmetric refit (post hoc)」と既に印が付いているので、括弧の挿入で文が切れる。3.4 節（main.tex:180）は「its controls together with the report of its chosen $\tau$」を後足しとして挙げており、意味は通る。それでも 1 文の中の印が多い。
  - 解消の条件: 「The chosen $\tau$ (reported post hoc) is $10^4$ ...」のように文の主語へ寄せる。
  - 自信: 低

- [severity: nit] 未定義の呼び名「asymmetric one」
  - 位置と引用: main.tex:180 「the symmetric refit of Section~\ref{sec:checks-method}, added after seeing the result of the asymmetric one」
  - なぜ問題か: 本文が定義した呼び名は「shared-only refit」（main.tex:185）である。呼び名を統一した直しの名残。
  - 解消の条件: 「the shared-only refit」に置き換える。
  - 自信: 高

### 4. 総合の推奨: minor

- 中心の発見（弱い比較での利得と、強い比較での残りの桁の差）は表・図・figdata で支えられている。round 8 の 8 件は 7 件が解消し、1 件が一部の解消。
- 今回書き換えた要旨と決定の段に、限定の抜け（検出の限界の範囲）と、限界の節と食い違う例（予測した状態）が入った。どちらも 1 句の直しで消える。
- 使う側が持ち帰れるもの（自分の連鎖を並べること）は残った。決定に関わる値には区間と費用の目安が無く、推奨 (2) の手順が特定されていない。この 3 点を足せば実務の読者に足りる。

### 5. 読めなかった範囲と注入の疑い

- 読んだもの: brief-R2.md、context-A.md、carryover-R2.md、接地の 2 本（aalbers.txt・saeb.txt の全文）、main.tex の全文、figdata の fig2_p15_joint.csv と fig2_p15_ar1.csv。
- 読んでいない: references.bib、figdata の fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15.csv、kit/symbols/README.md。参考文献の書誌の誤りと、図 2 の HMM・AR-HMM の 3 状態の系列の値は確かめていない。補足資料 S1〜S16 は未作成なので読めない（指摘 3 の区間が S16 にあるかは不明）。
- 注入の疑い: なし（接地の 2 本と対象物に、査読者や LLM に向けた指示は見当たらなかった）。