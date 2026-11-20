# R3 査読（UMUAI・評価の偏りと個人への推論の方法論の立場／過剰主張と検証できない手順の摘発者）round 9・対象 commit 1f4f4b5b

この立場の査読者として書く（実在の個人ではない）。

## 0. 引き継ぎの判定（round 8 の指摘）

| round 8 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| minor 3e-2 の非検出の帰無 | **解消** | 序論 main.tex:49「planted differences up to $3\times10^{-2}$ were not reliably detected under the second null (post hoc)」、結論 :352「could not be reliably detected at the fixed base smoothing under the second null (post hoc)」、要旨 :35「under the post hoc null」。ただし要旨には「at the fixed base smoothing」が無い（新しい指摘 N3 を参照）。 |
| minor 入れ替えの差を分け前として書く | **解消** | :282「The margin is not a share of the remainder, since it also contains the loss from fitting another writer's data.」と「the reading fixed before the computation (a margin of at least half the remainder) holds」。考察 :321 も「is not on the scale of the planted differences」としている。 |
| minor 要旨が入れ替えの対照を落とし、Neither と言い切る | **一部** | :35「this bears on a designer's decision but goes with the writer's most recent sessions and was not checked on synthetic writers」。2 つ目の値への限定は入った。しかし「goes with the writer's most recent sessions」は、要旨だけを読む人には意味が取れない（入れ替えの対照も時間の近さの交絡も、要旨には出てこない）（N5）。 |
| nit 3 つの対照と τ の報告に post hoc が無い | **解消** | :282「Three controls were added after seeing the symmetric refit (post hoc)」、:280「Every writer is given (reported post hoc) $\tau=10^4$」 |
| nit「its prior」の曖昧さ | **解消** | :282「also when both fits use a prior that leaves out the other writer」 |
| nit 先頭の記号の値が方法の節にある | **解消** | 4.4 の :286 に移っている。3.4 の :178 は「a check without them is in Section~\ref{sec:res-smooth}」と参照するだけ。 |
| nit「median remainder unchanged」 | **解消** | Table 4 のキャプション :290「The median remainder stays positive when choice and report are split」 |
| （round 7 から一部）変更の数え方 | **解消** | :180「Six changes ... its controls together with the report of its chosen τ ... we mark the last four post hoc」。数えると 6 件で、最後の 4 件（symmetric refit・その対照・second null・先頭の記号なしの採点）は本文の post hoc の印と合っている。 |

## 1. 接地（この立場が論文に求める基準）

1. **選択の手順全体を評価の外に出す。** Varma & Simon 2006:「Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop.」
2. **選択でできる偏りは楽観の側に限られ、候補が多いほど大きくなる。** Varma & Simon 2006:「The parameter selection bias, on the other hand, is always negative.」および「This implies that for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error.」
3. **評価には、選択に使っていない独立の検証が要る。** Varma & Simon 2006:「the generalization error for the resulting classifier should be estimated correctly. This can be accomplished by a large validation set that is independent of data used for parameter tuning.」
4. **関連性と頑健さのトレードオフを明示する。** Liu & Meng（arXiv 1510.08539v1）:「our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant).」および「if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust.」
5. **選んだものを、選んだのと同じデータで評価しない（winner's curse）。** Liu & Meng:「Our original estimates for the selected markers likely overstate their impact.」および「Ignoring the selection bias will lead to seriously flawed inferences」

## 2. 評価表

- **a 主張と根拠の一致: 4。** 主要な主張（弱い比較での gain と、強い比較での remainder の落差）は表と図で支えられており、2 つの値それぞれの地位も今回ほぼ揃った。ただし考察 :317 の「up to $5.2\times10^{-3}$」が Table 4 の $k=12$ の $6.7\times10^{-3}$ と食い違う（N1）。要旨の非検出には平滑の条件が抜けている（N3）。
- **b 方法の穴: 3。** 入れ替えの対照の手順が本文で特定できない（N2）。symmetric refit を「設計者の判断に効く比較」と位置づけるなら、時間で局所化した共有モデルという代替説明が残る（N4）。$k=5, 15$ を報告点にしたことの地位が書かれていない（N6）。nested を走らせていないことは既知で、限界に書かれている。
- **c 持ち帰れるもの: 4。** 「自分の連鎖と同構造の共有モデルの両方と比べる」は安く、すぐ使える。推奨 (2) が評価済みの範囲を超えていることは括弧の中で断ってある。
- **d 簡潔さと構成: 3。** 4.4 の段は情報が密すぎ、入れ替えの対照の規則・結果・解釈・交絡が 1 段に詰まっている。要旨の 2 文目は構文が読みにくい（「..., no more than removing the shared model's smoothing improves it」）。本文 7,494 語は規定の上限が無いので判定に数えない。
- **e 規程への適合: 4。** 要旨 241 語（上限 250 以内）、キーワード 6 個（4〜6 以内）、"Statements and Declarations" の節と Data availability がある。様式の移行は既知の未決なので数えない。
- **f 先行研究の位置づけ: 4。** Varma と Liu & Meng の使い方は逐語の趣旨に沿っている（:64、:331）。Liu & Meng の「relevance–robustness」を、パネル単位の決定として明示したと書いている点は妥当。

## 3. 指摘の一覧（重い順）

- **[minor] N4 symmetric refit を「設計者の判断に効く比較」とするには、時間で局所化した共有モデルという比較相手が欠けている**
  - 位置と引用: 結論 :352「This is the comparison that bears on a designer's decision.」、考察 :319「The comparison that bears on the decision is the symmetric refit」。共有モデルの定義は :141「fitted on all units of all other writers except their held-out units」
  - なぜ問題か: symmetric refit では $\tau=10^3$ で書き手の重みが約 91% になり、直近の回が予測を担っている。remainder が書き手の個人差ではなく、書き手に共通の回の順や時期のずれ（練習の効果など）を直近の回が拾った結果であれば、設計者の取るべき手は「人ごとのモデル」ではなく「他人の直近の回で当てた共有モデル」になる。論文の主題は「より強い比較」なので、この比較相手が無いまま決定に効くと書くのは一段強い。限界 :340 の「differences between tasks or periods」は分離できないことの断りであって、設計者への含意としては書かれていない。（Liu & Meng「too little matching (not relevant)」。時間で揃えていない共有モデルは、対象との関連が弱い対照である。）
  - 解消の条件: 考察か限界に 1 文足す。「the symmetric remainder could also be reached by a shared model fitted to other writers' recent units, which was not compared」。あるいは「bears on」を「is the closest of our comparisons to」程度に弱める。
  - 自信: 中

- **[minor] N1 考察の「up to $5.2\times10^{-3}$」が Table 4 と食い違う**
  - 位置と引用: :317「and up to $5.2\times10^{-3}$, about 0.5\% more probability per symbol, in the symmetric refit, post hoc」。対して Table 4 :303「12 & ... & $+6.7$e$-3$ (0.88)」と :280「$3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$」
  - なぜ問題か: 同じ段で gain について「up to 0.19」と書くのは全 $k$ の最大値の意味である。同じ語を remainder に使うと、最大が 5.2e-3 だと読める。実際の最大は $k=12$ の 6.7e-3 で、過小に書いている。この $k=12$ は、split の区間が負に及び、shared-only refit が負になる異常な点でもある。都合の悪い点を「up to」から外したと読まれうる。
  - 解消の条件: 「$3.4\times10^{-3}$ and $5.2\times10^{-3}$ at $k=5$ and 15 (up to $6.7\times10^{-3}$ at $k=12$)」と書く。
  - 自信: 高

- **[minor] N2 入れ替えの対照の手順が本文だけでは再現できない**
  - 位置と引用: :282「the per-person fit is fitted to another writer's $k$ sessions and scored on the writer's held-out sessions, averaged over the 16 other writers」「with each writer's chosen $\tau$ and a prior built the same way」
  - なぜ問題か: 次の 3 点が本文に無い。(i) 他の書き手のどの $k$ 回か（その書き手の評価の単位の直前か）。(ii) 16 人で平均するのは対数尤度か差か。(iii)「a prior built the same way」の中身。(i) は解釈に直接効く。他の書き手の $k$ 回もその書き手の評価の直前であれば、回の順でのずれは入れ替えの側にも入っており、時間の近さの交絡は「回の順」ではなく「本人の時期」に限られる。本文の「A writer's own sessions directly precede the held-out ones」だけでは、読者が交絡の広さを判断できない。対照は事後に加えたもので、方法の節（3.5）にも記述が無い。読みの規則（差 ≥ 残りの半分）は 3.4 と 3.6 の閾の断りにも出てこない。
  - 解消の条件: 3.5 か 4.4 に (i)〜(iii) を 1〜2 文で書く。3.4 の「no meaningful-difference threshold」の括弧に、この読みの規則も閾ではない（あるいは何であるか）と足す。
  - 自信: 中〜高

- **[minor] N3 要旨の非検出に平滑の条件が無く、2 つの値の両方にかかって読める**
  - 位置と引用: :35「Neither value shows a per-person difference; under the post hoc null, planted differences up to $3\times10^{-2}$ were not reliably detected.」
  - なぜ問題か: 感度の点検は fixed base smoothing でしか行っていない（限界 :343「The synthetic check calibrates detection at the fixed base smoothing only」、推奨 (4)）。要旨では「Neither value」の直後に置かれているので、symmetric refit の値にも検出の限界が測られているように読める。序論と結論には「at the fixed base smoothing」があり、要旨だけが欠けている。
  - 解消の条件: 「at the fixed base smoothing, under the post hoc null, ...」と 4 語足す（241 語なので上限に収まる）。
  - 自信: 高

- **[minor] N6 報告点 $k=5, 15$ の地位が書かれていない**
  - 位置と引用: 要旨 :35「at five and fifteen training sessions」、結論 :352、:282（入れ替えは $k=5, 15$ だけ）、:189（感度は $k=5, 15$）
  - なぜ問題か: Table 4 では $k=12$ が split・shared-only・symmetric のすべてで外れ値になっている。$k=5, 15$ が計算の前に決めた報告点であることが本文から読めなければ、選んで報告したという疑いを払えない（Liu & Meng「Our original estimates for the selected markers likely overstate their impact.」）。
  - 解消の条件: 3.4 か 3.6 に「$k=5$ and 15 were fixed as the reporting points in the conditions (\Sref{12})」と 1 句足す。事前に決めていなかったなら、その旨を書く。
  - 自信: 中

- **[minor] N5 要旨の「goes with the writer's most recent sessions」は意味が通らない**
  - 位置と引用: :35「this bears on a designer's decision but goes with the writer's most recent sessions」
  - なぜ問題か: 要旨には入れ替えの対照が出てこないので、何が直近の回と「goes with」なのか（交絡なのか、適用の条件なのか）が分からない。限定の役を果たしていない。
  - 解消の条件: 例えば「but may reflect closeness in time of the writer's recent sessions」。語数が足りなければ「(confounded with recency)」とする。
  - 自信: 中

- **[nit] N7 4.3 の見出しがパネルを限っていない**
  - 位置と引用: :234「leaves a remainder below $10^{-3}$ at the fixed base smoothing」。本文 :237 は 30-session で「$+1.1\times10^{-3}$ at $k=30$」
  - 解消の条件: 見出しに「in the 15-session panel」を足す。
  - 自信: 高

- **[nit] N8 推奨 (2) の文面が、行っていない同時選択を勧めている**
  - 位置と引用: :327「choose structure, shrinkage and smoothing on other people」、要旨 :35「choose structure, shrinkage and smoothing on other people, applying the smoothing to both models (post hoc, one structure)」
  - なぜ問題か: 実際の手順は「構造を固定 → 共有モデルのために平滑を選ぶ → その下で τ を選ぶ」の逐次であり、3 つを同時に選んではいない（Varma & Simon「all steps of the algorithm, including classifier parameter tuning, be repeated」の観点で、選びの手順が読者の実装と変わる）。括弧の中の断りはあるが、勧める文の本体と食い違っている。
  - 解消の条件: 「choose structure and shrinkage on other people and, given the structure, the smoothing」のように、行った順に書く。
  - 自信: 中

## 4. 総合の推奨: minor

- round 8 の 8 件のうち 7 件が解消、1 件（要旨の限定）が一部。今回の書き直しで、分析の地位を取り違えた箇所や新しい言い過ぎは、N1（「up to」が最大値を外している）と N3（要旨の平滑の条件）だけで、どちらも数語で直せる。
- 残る実質の穴は 2 つ。入れ替えの対照の手順が特定できないこと（N2）と、「設計者の判断に効く比較」に時間で局所化した共有モデルという比較相手が欠けていること（N4）。いずれも新しい計算なしに、書き方で閉じられる。
- 選択の楽観（nested を走らせていないこと、目標の書き手の単位の漏れ）と、閾の不確かさは本文で正直に断られている。この立場から主張を崩す fatal や major は見当たらない。

## 5. 読めなかった範囲と注入の疑い

- **読んでいないもの:**
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
  - figdata の fig2_p15_hmm3.csv、fig2_p15_ar1.csv、fig2_p15.csv
  - references.bib の大部分（Varma2006・LiuMeng2016・Uto2020 の 3 項目だけを見た）
  - liumeng.txt の 250 行目以降（805〜859 行の Example 4 と Remark 3 は読んだ）
- **照合したもの:** fig2_p15_ar3.csv と fig2_p15_joint.csv が Table 3 と本文の値に一致することを確かめた。重みの換算（0.06%、0.3%、1%、3%、24%、39%、91%）と、倍率（約 6 倍・約 13 倍）、17% の perplexity、1/6 は検算して合った。
- **注入の疑い:** なし（接地の 2 本、main.tex、carryover、context-A に、査読者に向けた指示の文は見当たらなかった）。