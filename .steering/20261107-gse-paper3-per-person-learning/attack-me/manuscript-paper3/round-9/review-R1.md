## 査読 R1・round 9（UMUAI の査読者。立場は行動の記号列の系列モデル（HMM・マルコフ連鎖）の方法論。対象は main.tex @1f4f4b5b）

この立場の査読者として書く。実在の個人ではない。

### 0. 引き継ぎの判定（round 8 の指摘）

| round 8 の指摘 | 判定 | 今の版の位置と逐語 |
|---|---|---|
| minor 1 入れ替えの対照の「more than half」 | 解消 | 4.4（main.tex:282）「The margin exceeds the whole remainder, so the reading fixed before the computation (a margin of at least half the remainder) holds」「The margin is not a share of the remainder, since it also contains the loss from fitting another writer's data」。序論・考察（:319）・結論（:352）も「the writer's own sessions predict better than another writer's under the same τ」にそろっている。時間の近さと記号数の交絡の断りも :282 にある |
| minor 2 植えた差の未検出に帰無が無い | 解消 | :49「under the second null (post hoc)」、:352「under the second null (post hoc)」、要旨「under the post hoc null」 |
| minor 3 要旨の倍率 | 解消（nit が 1 つ残る） | 要旨から倍率が消えた。序論 :49 の「over two orders of magnitude」は固定の平滑どうしの比で、0.188/5.5e-4 ≈ 340 なので正しい。ただし考察 :321「about 6 and 13 times larger at k=5 and 15 (not prespecified)」は、平滑の違う値どうしの比（3.4e-3/5.5e-4、5.2e-3/4.1e-4）である。平滑の効きを述べる文脈なので許容はできるが、引き継ぎの「序論・考察に 2 つ目の値の倍率は残していない」とは食い違う（下の nit 4） |
| minor 4 要旨の Neither の根拠 | 解消 | 要旨「goes with the writer's most recent sessions and was not checked on synthetic writers」（言い回しの分かりにくさは nit 3） |
| minor 5 EM の基準と始点 | 一部 | :137「keeps the one with the higher MAP objective on the training symbols, and the shared model is fitted from ten starting points and refitted without each target writer from that solution」と、限界 :344「run from two starting points」で、基準と始点は書かれた。ただし「ten starting points」の当てはめにどのデータを使ったのかが書かれていない（下の minor 3） |
| nit 6 remainder の定義と両側の版 | 解消 | :178「we also call remainder the same difference in the symmetric refit (Section~\ref{sec:checks-method}), which keeps that structure and chooses only $\tau$」 |
| nit 7 Pohle の交差検証 | 解消 | :70 と :342「information criteria, and asymptotically cross-validated likelihood」。Pohle の「Given the asymptotic equivalence of AIC and cross-validated likelihood (Stone, 1977)」に沿っている |
| nit 8 3 つの対照の post hoc | 解消 | :282「Three controls were added after seeing the symmetric refit (post hoc)」。:180 の 6 つの変更の列挙とも合う |
| nit 9 表 2 の 16 of 17 | 解消 | :256「$3\times10^5$ (16 of 17)」 |

### 1. 接地（この立場が論文に求める基準・逐語）

- **G1 尤度の比べは複雑さを割り引く（Singer et al. 2014）**: 「methods are necessary that balance the goodness-of-fit against the number of model parameters」。理由は「higher order Markov chains have exponentially more parameters than lower order models (potential overfitting), they are always a better fit for the data」。
- **G2 独立の検証の集合で予測を評価する（Singer et al. 2014）**: 「The basic idea is to estimate the parameters on a training set and validate the results on an independent testing set.」 先験の数（平滑）が無いと予測できない点にも触れている: 「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible.」
- **G3 候補のモデルは事前に決め、最小と最大を置く（Pohle et al. 2017）**: 「Step 1 decide a priori on the candidate models, in particular the minimum and the maximum number of states that seem plausible」。もっともらしくない候補を足すと選びの偏りが出る: 「a model is selected not by merit but because it got lucky」。
- **G4 残差でモデルを点検する（Pohle et al. 2017）**: 「Step 3 use model checking methods, in particular residual analyses, but potentially also simulation-based checks, to obtain a more detailed picture of the fitted models」。
- **G5 決め手が無いときは複数のモデルを報告する（Pohle et al. 2017）**: 「Step 6 in cases where there seems to be no strong reason to prefer one particular model over another ... results for each of these models should be reported.」
- **G6 平滑は過学習を抑える正則化であり、まばらなデータへの代替になる（Monaco & Tappert 2018）**: 「First, it acts as a kind of regularization to avoid overfitting ... Second, parameter smoothing provides superior estimates in case of missing or infrequent data.」 平滑の向きは頻度に依存する: 「bias parameters that depend on event types with low frequency toward the marginals」。

### 2. 評価表

- **a 主張と根拠の一致: 4。** 主な主張（弱い比べの gain が 0.19 で、強い比べの remainder が 5e-4、両側の版で 3.4〜5.2e-3）は、表 2・表 3・図 2 の値と照合して合う。重みの換算も合う（9673/(9673+3e5)=3%、9673/10673=91%、9673/39673=24%）。ただし数値の取り違えが 2 か所ある（考察の「up to 5.2e-3」と 4.3 の見出しの「below 10^-3」）。結論は、非重なり窓の結果を断りを落として使っている。
- **b 方法の穴: 4。** 選びを他の書き手で行い、帰無を 2 つ置き、入れ替えの対照を置き、限界も厚い。G2 と G6 の観点でよく守られている。残るのは 3 点: 10 始点の共有モデルのデータが不明、入れ替えの対照の規則の検出力の性格、選びがすべて格子の端にあること（G3。限界にあり既知）。
- **c 持ち帰れるもの: 3。** 推奨（1）（2）は具体的である。ただし（2）は事後の、1 構造・1 パネル・格子の端の結果から出ている。読者が「平滑を他人で選んで両側に当てる」を一般の手順として持ち帰るには根拠が細い（本文に断りはある）。
- **d 簡潔さと構成: 3。** 断りが文ごとに重なり、想定読者（統計の専門の訓練を前提にしない HCI・教育工学の読者）には要旨と序論 :49 が読みにくい。例えば要旨の「no more than removing the shared model's smoothing improves it」「a similar relative remainder」「goes with the writer's most recent sessions」は、本文を読む前には意味が取れない。
- **e 規程への適合: 4。** 要旨は 241 語（規程は 150〜250 語）、キーワードは 6 個（規程は 4〜6 個）、Statements and Declarations の節があり、Data availability がある。語数 7,494 には規程の上限が無い。様式の移行は既知の未決。
- **f 先行研究の位置づけ: 4。** Pohle・Singer・Monaco・Berchtold & Raftery への言及は、接地の逐語と矛盾しない。Pohle の言い換えは今回で正しくなった。Singer が示す「抽象の水準で次数が変わる」という論点が、記号化への依存（:204）と結び付けられていない点は惜しいが、必須ではない。

### 3. 指摘の一覧（重い順）

- **[severity: minor] 考察の「up to 5.2×10^-3」が表 3 と結果の文に矛盾する**
  - 位置と引用: main.tex:317 Discussion 第 1 段「and up to $5.2\times10^{-3}$, about 0.5\% more probability per symbol, in the symmetric refit, post hoc」。:280「$3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$」、表 3 の k=12 は「$+6.7$e$-3$ (0.88)」。
  - なぜ問題か: 両側の版の中央値の最大は k=12 の 6.7e-3 である。「up to」と書くと最大が 5.2e-3 と読める。要旨と結論は「k=5 と 15」と限っているので正しいが、考察だけが限りなしの「up to」になっている。
  - 解消の条件: 「at k=5 and 15, $3.4\times10^{-3}$ and $5.2\times10^{-3}$」と k を限る。
  - 自信: 高

- **[severity: minor] 4.3 の見出しの「below 10^-3」が同じ節の 30 セッションのパネルの値と合わない**
  - 位置と引用: :234 見出し「Choosing structure and shrinkage on other writers leaves a remainder below $10^{-3}$ at the fixed base smoothing」。同じ節の :237「$+1.1\times10^{-3}$ at $k=30$ in the 30-session panel」。
  - なぜ問題か: 見出しはパネルを限っていないが、節の中に 10^-3 を超える値がある（区間はゼロをまたぐ）。表 2 のキャプションは「in the 15-session panel」と限っているので、見出しだけが言い過ぎになっている。
  - 解消の条件: 見出しに「in the 15-session panel」を足す。
  - 自信: 高

- **[severity: minor] 共有モデルの「ten starting points」の当てはめにどのデータを使ったかが書かれていない**
  - 位置と引用: :137「the shared model is fitted from ten starting points and refitted without each target writer from that solution」
  - なぜ問題か: 書き手 w を除く共有モデルは、10 始点の解から EM を始めている。その解が w の訓練の単位を含むなら、比べの相手の局所解の選択が w のデータに引かれている（w の記録の中の EM の盆地の選択）。held-out の単位を含むなら、図 2 の「The target writer's held-out units enter no fit and no choice」と矛盾する。どちらの向きでも、remainder の比べの相手の独立性に関わる。:141 の「all units of all other writers except their held-out units」は除いた後の当て直しについての文であり、始点の解のデータは特定されない。10 始点のうちどれを採るか（目的関数が最も高いものか）も明示されていない。
  - 解消の条件: 10 始点の当てはめのデータ（例: 「all writers' non-held-out units」）と採る基準を 1 句で書く。w の訓練の単位を含むなら、その向きを限界の EM の文（:344）に 1 句で足す。
  - 自信: 中

- **[severity: minor] 結論が、非重なり窓の結果の断りを落として推奨の根拠にしている**
  - 位置と引用: :352「With non-overlapping windows the direction of a per-person gain returned, so studies should report the symbolization together with the comparison.」。本文 :204 には「with so few symbols this may reflect the amount of data as well as the symbolization, and it was not checked against synthetic writers」とあり、値は本文に無い（補足 S13）。
  - なぜ問題か: この結果は主張の範囲（記号化への依存）を決める反例側の結果である。結論はそれを記号化の効果として読み、推奨に使っているが、本文では値が示されず、データの量の交絡も断られている。本文だけでは支えられず、補足に送ってよい種類の内容ではない。G5 の観点では、別の記号化で HMM3 が選ばれるなら、その結果も本文で対等に報告すべきである。
  - 解消の条件: 結論に「which may reflect the amount of data」の 1 句を戻す。非重なり窓の remainder（または gain）の中央値を少なくとも 1 つ、本文の :204 に出す。
  - 自信: 中

- **[severity: minor] 入れ替えの対照の事前の規則は、入れ替えた当てはめが共有モデルに負ければ自動的に満たされる。何を除けたかを正確に書くべき**
  - 位置と引用: :282「The margin exceeds the whole remainder, so the reading fixed before the computation (a margin of at least half the remainder) holds: the remainder does not come from refitting the prior on $k$ sessions alone.」と「the swapped fit loses even to the shared model ($-1.7\times10^{-3}$ and $-1.7\times10^{-2}$)」
  - なぜ問題か: 結論（「先験を k セッションで当て直すだけでは remainder は出ない」）は支えられている。ただしこの規則が除けるのは、「誰のデータでも同じ程度に効く」という対立仮説だけである。margin は他人のデータの害を含むので、規則を超えた幅（全体を超えたこと）を、追加の証拠の強さとして読ませてはならない。本文は「not a share」と断ってはいる。しかし「holds」の直後に「for every writer」が続くので、強い支持に読める。測っているものと主張の対応（懐疑家の観点）の問題である。
  - 解消の条件: 「the rule excludes only that any writer's k sessions would yield the remainder」のように、規則が除いた対立仮説を 1 句で名指す。
  - 自信: 中

- **[severity: nit 1] 要旨の 2 文目以降が想定読者に読めない**
  - 位置と引用: 要旨「no more than removing the shared model's smoothing improves it; synthetic writers without per-person differences (post hoc) left a similar relative remainder」
  - なぜ問題か: 「relative」が何に対してなのか（平滑の効きに対して）が要旨の中で決まらない。カンマでつないだ文で主語も追いにくい。
  - 解消の条件: 「a remainder of similar size relative to that smoothing improvement」と書き、文を切る。
  - 自信: 中

- **[severity: nit 2] 事後に足した対照に「計算の前に決めた読み」がある点が読み手を迷わせる**
  - 位置と引用: :282「Three controls were added after seeing the symmetric refit (post hoc)」と、同じ段の「the reading fixed before the computation」
  - なぜ問題か: :180 の規則（対照の追加は事後だが、各条件はその計算の前に記録した）を読めば整合する。しかし 4.4 だけを読むと矛盾に見える。
  - 解消の条件: 「the reading, committed before this control was computed」とする。
  - 自信: 中

- **[severity: nit 3] 要旨の「goes with the writer's most recent sessions」が意味の取りにくい言い回しである**
  - 位置と引用: 要旨「this bears on a designer's decision but goes with the writer's most recent sessions」
  - なぜ問題か: 「時間の近さと交絡している」という意味が、この言い回しからは伝わらない。
  - 解消の条件: 「but may reflect the closeness in time of the writer's most recent sessions」のように書く。
  - 自信: 中

- **[severity: nit 4] 考察の「6 and 13 times」は、平滑の違う 2 つの値の比である**
  - 位置と引用: :321「about 6 and 13 times larger at k=5 and 15 (not prespecified)」
  - なぜ問題か: 平滑の依存の大きさを示す文なので、誤りではない。ただし要旨から倍率を外した方針と揃っておらず、両側の版の効果量の印象を強める。
  - 解消の条件: 倍率を外し、2 つの値を並べるだけにする。残すなら「a ratio across smoothings」と断る。
  - 自信: 低

（既知の未決 1〜15、すなわち格子の端・第 2 の帰無の大きさ・合成の書き手での未確認・残差の図・語数は、判定に数えていない。そのうえで、主張に響く非重なり窓の件だけを上の minor として挙げた。）

### 4. 総合の推奨: minor

- round 8 の 9 件のうち 8 件は解消、1 件（EM の始点のデータ）は一部である。今回の書き換えは、要旨・序論・結論の主張を値と矛盾させていない。
- 新しく見つけた穴は書き方の範囲に収まる: 数値の取り違え 2 か所、始点のデータの特定、結論の断りの欠落、入れ替えの規則が除いたものの明示。新しい計算は要らない。
- 方法の骨格（他人での選び・2 つの帰無・3 つの対照・残差の点検）は G2・G4・G6 の基準を満たしている。格子の端（G3）は限界に正直に書かれている。

### 5. 読めなかった範囲と注入の疑い

- **読んでいない:** /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib、figdata のうち fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15.csv、/Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md。このため、参考文献の書誌の正しさと記号化のキットの記述は判定していない。
- **一部だけ読んだ:** 図 2 の値は fig2_p15_joint.csv と fig2_p15_ar1.csv で照合し、本文と一致した。
- **抜粋だけ読んだ:** 接地の本文 3 本（monaco.txt・pohle.txt・singer.txt）は、Grep と関係する箇所の抜粋だけで、全文は読んでいない。
- **読んだもの:** main.tex は全文、context-A.md と carryover-R1.md は全文。
- **注入の疑い:** なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。