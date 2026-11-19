査読の報告（R1・行動の記号列の系列モデルの方法論の立場、懐疑家の下位人格。round 6、対象の版は commit e6fdad49、main.tex）

# 0. 引き継ぎの判定（round 5 の指摘）

- **M1（要旨が事後の変更を隠す）: 解消。** 要旨に「The candidate grids were extended, and two checks added, after seeing results.」とある。3.5 節の「Four changes were made after seeing results: the extension of the τ grid and of the structure families … the symmetric refit … and the second null」と数が合う。ただし、どの 2 つの確かめが事後かを要旨は名指ししていない。これは新しい指摘 m-2 に回す。
- **M2（重ならない窓で記号の数とパラメータの数が交絡する）: 解消。** 4.2 節に「With one-thirtieth of the symbols, structures with many parameters (2,033 for the 3-state AR-HMM, 83 for the 3-state HMM) are also harder to estimate, so this reversal may reflect the amount of data as well as the symbolization; it was not checked against synthetic writers.」とある。考察の Relation の「a direction that may also reflect the smaller amount of data」、結論の「which also give far fewer symbols」でも揃っている。大きさの文は消えていた。
- **M3（約 5e-4 は書き手のデータを使わずに取り戻せる）: 解消。** 考察に「Nor does the remainder of about 5×10^-4 at that smoothing show a value of the writer's data: the prior mode … beats the shared model by 7.4×10^-4, and lightening the shared model's smoothing alone gains 1.6×10^-3」とあり、結論の「so it does not show a value of the writer's data」とも合う。
- **m1（両側の当て直しの残り 3〜7e-3 に重みと対照が無い）: 一部。** 重みは 4.4 節の「every writer is given a τ between 10^2 and 3×10^5, inside the grid and no larger than at the fixed smoothing」で足された。対照は無いままである。さらに今回、この比べを決定の段で「The comparison that bears on the decision」と格上げしたので、対照が無いことの重みが増えた（新しい指摘 M-1）。
- **m2（要旨の two orders に k が無い）: 解消。**「at five and fifteen training sessions」とある。
- **m3（要旨の CS1 の文に平滑の断りが無い）: 解消。**「the shared model itself is chosen at the fixed smoothing」とある。
- **m4（残差の自己相関の値）: 未解消（著者は採らなかった。既知の未決 7）。** 4.2 節は今も「small values for the 3-state AR-HMM and the own chain (S13)」のままで、数が無い。判定には数えない。ただし下の接地（Pohle の Step 3）から見ると、本文に 1 句の値があるのが望ましい。
- **m5（What was established の最後の文の論理）: 解消。**「Lightening the smoothing of the shared model alone made the remainder vanish; applying the same smoothing to both models (post hoc) brought it back, about 6 and 12.5 times larger at k=5 and 15.」とある。表で検算した: 3.4e-3/5.5e-4≈6.2、5.2e-3/4.1e-4≈12.7。
- **n1（括弧の対応）: 解消。**「873 of 935 at k = 5 and 783 of 935 at k = 15」とある。
- **n2（要旨が上限ちょうど）: 解消。** 248 語（context-A の測った値）。

# 1. 接地（この立場が論文に求める基準）

1. **当てはめの点検を、選ぶ根拠に含める。** Pohle et al. 2017（pohle.txt l.870–871）は「Step 3 use model checking methods, in particular residual analyses, but potentially also simulation-based checks, to obtain a more detailed picture of the fitted models, and to validate or」と書く。l.935–936 は「The main purpose of this step … is model validation, i.e. the assessment if any given candidate model adequately represents the data-generating process.」と書く。
2. **決め手が無いなら、複数の候補の結果を出す。** Pohle（l.880–882）は「Step 6 in cases where there seems to be no strong reason to prefer one particular model over another … results for each of these models should be reported.」と書く。
3. **情報量規準や交差検証の尤度は、状態を多く選びがち。** Pohle（l.60）は「selection criteria, and especially the AIC, often lead to the selection of much larger numbers of」と書く。l.324 は「Given the asymptotic equivalence of AIC and cross-validated likelihood」と書く。
4. **データが疎だと、パラメータの多い構造は推定できない。だから比べはデータ量と交絡する。** Singer et al. 2014（singer.txt l.86–93）は「It is difficult to make plausible statements about the appropriate Markov chain order having insufficient data but a vast amount of states … because the number of parameters grows exponentially with the chain order and the available data is too sparse for proper parameter inferences.」と書く。
5. **平滑は過学習を避ける正則化であり、低頻度の文脈を周辺へ寄せる。** Monaco & Tappert 2018（monaco.txt l.721–724）は「The purpose of parameter smoothing is twofold. First, it acts as a kind of regularization to avoid overfitting … Second, parameter smoothing provides superior estimates in case of missing or infrequent data.」と書く。l.730–731 は「The effect is to bias parameters that depend on event types with low frequency toward the marginals」と書く。私の読み: 平滑の当て方そのものが比べの差を作りうるので、平滑を揃えた比べと、平滑だけの効きの対照が要る。

# 2. 評価表

- **a 主張と根拠の一致: 3。** round 5 の言い過ぎは要旨・考察・結論で閉じられた。ただし決定の段が、両側の当て直しの値（3.4e-3・5.2e-3）を「the comparison that bears on the decision」として示している。固定の平滑のときに自分で使った対照（prior mode と共有モデルの差）を、この比べには当てていない（M-1）。
- **b 方法の穴: 3。** 対称の当て直しは 1 構造・1 パネル・格子の端（α=0.03）で行われ、null も対照も無い。選ばれた τ は 10^2〜3×10^5 と、書き手の重みで数 % から 9 割台までにわたるが、その分布が見えない。構造・τ・α・own chain の平滑の 4 つがどれも格子の端かその近くにある（限界に明記はある）。
- **c 持ち帰れるもの: 4。**「同じ弱い構造の共有モデルとの比べは、本人の 1 次の連鎖と並べないと誤読する」という持ち帰りは明快で、Figure 2 の (a)(b) の対比がよく効いている。
- **d 簡潔さと構成: 3。** 考察の 3 段の順序は良くなった。ただし 4.4 節の第 4 段落（l.278）と決定の段（l.315）は、但し書きを 1 文に何重にも入れている。系列モデルの訓練を前提にしない想定読者には重い。考察の冒頭の段は序論の第 4 段落と大きく重なる。
- **e 規程への適合: 4。** 要旨は 248 語（上限 250）、キーワードは 6、Statements and Declarations の見出しがあり、Data availability もある。語数の上限は規程に無い。様式の移行と補足の欠如は既知の未決なので数えない。
- **f 先行研究の位置づけ: 4。** Pohle・Singer・Berchtold & Raftery・Shirley による位置づけは適切である。ただ、平滑の当て方で比べが動くという本論文の中心の現象を、Monaco の頻度依存の平滑（拡張として挙げているだけ）とつなぐ 1 文があってもよい。

# 3. 指摘の一覧（重い順）

- **[severity: major] 決定の段が、対照の無い事後の比べを「決定に関わる比べ」と格上げしている**
  - 位置と引用: 考察「What the protocol returns」（main.tex l.315）の「The comparison that bears on the decision applies the smoothing chosen on other writers to both models. Done post hoc … leaves a remainder of 3.4×10^-3 at k=5 and 5.2×10^-3 at k=15.」。序論 l.49 と要旨の末尾の推奨も同じ比べに依っている。
  - なぜ問題か: 固定の平滑の段で、論文は「remainder ≤ smoothing effect（7.4e-4）だから書き手のデータの価値を示さない」という論理を使った。その論理を α=0.03 の比べには当てていない。α=0.03 での prior mode と共有モデルの差（平滑の効き）は本文に無い。限界にある「this check does not separate the writer's data from other effects of refitting the per-person prior」は 4.4 節にしかなく、決定の段は値だけを置いている。さらに α=0.03 は格子の端で、第 2 の null も α=0.03 で平滑の効きが 1.8e-3 あった。だから α=0.03 では平滑だけで数 e-3 の差が出うることを、論文自身のデータが示唆している（接地 5: Monaco「bias parameters … toward the marginals」）。
  - 解消の条件: 次の 2 つのどちらかでよい。(i) 決定の段で、この比べを「平滑を揃えるという比べ方の要件」として述べ、値は「書き手のデータの価値を示すかは、同じ平滑での prior mode の対照も null も無いので未確認」と同じ段で閉じる。(ii) α=0.03 での平滑の効き（prior mode と共有モデルの差、書き手のデータを使わない）を既存の当てはめから 1 値足す。
  - 自信: 中〜高

- **[severity: minor] 4.4 節の見出しの「stays positive」が、書き手を分けた確かめの k=12・15 の分布と合わない**
  - 位置と引用: 4.4 節の見出し「The remainder stays positive when choice and report use different writers」。Table 4 の k=12 は「+6.8e-4 [−4.2e-3, 8.2e-4] (0.95)」、k=15 は「+7.4e-4 [−3.7e-3, 9.1e-4] (0.75)」。
  - なぜ問題か: k=15 では 4 分の 1 の組が 0 以下で、2.5% 点は残りの約 5 倍の大きさの負の値である。言えるのは「中央値は正のまま」までである。
  - 解消の条件: 見出しを「the median remainder stays positive」とし、k=12・15 では組の分布が負に伸びることを本文で 1 句断る。
  - 自信: 高

- **[severity: minor] 要旨の検出の結論が、事後の null によることを示していない（事前に決めた null は逆の結果だった）**
  - 位置と引用: 要旨「Synthetic writers without per-person differences left a similar remainder … ; planted differences up to 3×10^-2 were not reliably detected.」。4.5 節「Under the first null … planted differences of 10^-2 were reliably detected at k=5 and 15」。
  - なぜ問題か: 要旨の 2 つの結論（似た remainder・検出できない）はどちらも第 2 の null（事後・平滑の効きを 2.4 倍に過大に再現）によっている。事前に決めた第 1 の null は 10^-2 を確実に検出した。第 1 の null を読みに使わない理由は本文にあるが、要旨の「two checks added after seeing results」がこの null を指すと読者には分からない。
  - 解消の条件: 要旨の該当の文に「(a null added after seeing results)」の類の 1 句を入れる。
  - 自信: 中

- **[severity: minor] 両側の当て直しで選ばれた τ の幅が広すぎて、重みの読みが付かない**
  - 位置と引用: 4.4 節 l.278「every writer is given a τ between 10^2 and 3×10^5」。考察の「so the writer's data carry at least as much weight as at the fixed smoothing」。
  - なぜ問題か: 訓練の記号の中央値（k=5 で数千）で見ると、τ=10^2 は書き手の重みが 9 割を超え、3×10^5 なら数 % である。「at least as much」は正しいが、3〜7e-3 が書き手の重みの大きい少数から来るのか、全員に薄く広がるのかで読みが全く変わる。既知の未決 11 は「本文に出さない」としている。だが中央値 1 つ（または k=5・15 の重みの中央値）は主張を支える最小の情報で、補足に送るべきものではない。
  - 解消の条件: k=5・15 の選ばれた τ の中央値（または重みの中央値）を 1 句で本文に入れる。
  - 自信: 中

- **[severity: minor] remainder は構造しだいで、1 次の連鎖の行では固定の平滑でも大きい**
  - 位置と引用: Table 2「Ar1 vs. own chain, 15-session, 15 … +0.002 (0.82)」。4.2 節「it also beats the shared 1-state AR-HMM by +0.002; no synthetic null was run for this row」。
  - なぜ問題か: 同じ固定の平滑で、書き手の重み 24% の 1 次の連鎖の残りは 2e-3 ある。見出しの「about 5×10^-4」（AR3、重み 3%）の約 5 倍で、第 2 の null の閾 1.8e-3 も超える（その null はこの行に当てていないが）。joint choice は own chain との差で構造を選ぶので、本人の差を最もよく拾う構造を選ぶとは限らない。要旨と結論の「about 5×10^-4 remained」は選ばれた構造の値であり、「強い比べに対して残るもの」の一般的な大きさとは読めない（接地 2: Pohle Step 6）。
  - 解消の条件: 考察の「What was established」に、remainder は選ばれた構造の値であり、1 次の連鎖を固定すると k=15 で 2e-3 になる（null 未確認）ことを 1 文置く。
  - 自信: 中

- **[severity: minor] AR3 が「強い比べ」として適合しているかの根拠が、本文では語だけ（m4 の継続）**
  - 位置と引用: 4.2 節「small values for the 3-state AR-HMM and the own chain (S13)」。
  - なぜ問題か: 論文の中心の論理は「HMM3 は連続する記号の依存を運べないが、AR3 は運べる」である。その根拠の一方だけが数で、もう一方は「small」という語だけになっている（接地 1: Pohle Step 3「to validate」）。既知の未決 7 で判定には数えないが、主張に効く。
  - 解消の条件: AR3 と own chain のラグ 1 の自己相関の範囲を 1 句、本文に入れる。
  - 自信: 中

- **[severity: nit] 3.4 節の remainder の定義の括弧が、α=0.03 でも joint choice が AR3 を選ぶかのように読める**
  - 位置と引用: l.176「(in the symmetric refit …, with the structure fixed at the 3-state AR-HMM, which the joint choice picks in every cell of that panel)」
  - なぜ問題か: AR3 を選ぶという事実は固定の平滑でのものである。α=0.03 では構造を選び直していない（限界にはその旨がある）。
  - 解消の条件: 「which the joint choice picks at the fixed smoothing in every cell」とする。
  - 自信: 高

# 4. 総合の推奨: minor

- round 5 の 3 つの major（要旨の事後の変更・重ならない窓の交絡・5e-4 の価値の読み）は、書き方の直しで閉じられた。今回の書き換えで数の矛盾は見つからなかった（Figure 2 の csv・Table 2・Table 4・本文の値を照合した）。
- 残る major は 1 つで、決定の段が対照の無い事後の比べを格上げしたことによる言い過ぎである。決定の段の 1 段落の書き方で消える。
- ほかの指摘は、見出しの言い方・要旨の 1 句・本文に 1 句の値を入れること、で済む。

# 5. 読めなかった範囲と注入の疑い

- **読んでいない:** references.bib、kit/symbols/README.md。figdata は fig2_p15.csv と fig2_p15_ar1.csv だけを読み、fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15_joint.csv は読んでいない。接地の 3 本の本文は通読しておらず、grep で当たった前後と指定の範囲だけを読んだ（pohle.txt・singer.txt・monaco.txt）。
- **注入の疑い:** 無し（読んだ範囲には、査読者や LLM に向けた指示は見当たらなかった）。

関係するファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-6/brief-R1.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-6/carryover-R1.md