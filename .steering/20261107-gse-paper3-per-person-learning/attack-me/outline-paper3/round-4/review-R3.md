# R3 の査読（UMUAI・方法論と再現性・下位人格は過剰主張と検証できない手順の摘発者）・round 4・stage outline

## 1. 接地
1 Varma & Simon 2006 "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
2 同 "Since selection of classifier parameters that minimize CV error estimates is a kind of training, it should be included as part of the classifier training algorithm."
3 同 "Using these "null" datasets, we selected classifier parameter values that minimized the CV error estimate."・"Performance of the optimized classifiers on the independent test set was no better than chance."
4 同 "This implies that for large K , there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
5 Liu & Meng（liumeng.txt l.1726-1732）"we predict each individual's response using the remaining n − 1 individuals ... The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
6 同（l.990-991）"Ignoring the selection bias will lead to seriously flawed inferences"
注: liumeng.txt は arXiv:1510.08539v1（2015）で、外枠が引く Annual Review 2016 の版ではない（指摘 I）。

## 2. 評価表
- a 2: Take-home の「prior mode を上回らない」は 15-session の 1 パネルに支えられ、30-session の k = 30 で逆、CS1 は構成上ゼロ（B）。
- b 2: 選んだ候補に、同じ候補集合の prior mode が大半の書き手で勝つ＝選びの目的関数が予測を選べていない（A）。新しい比べは合成で確かめられておらず、合成はこの点で実データと逆（C）。
- c 3: 3 つの相手の勧めは持ち帰れるが、上の欠陥と、確率ゼロのモデルを割り当てうる仕様が残る（D）。
- d 2: 外枠 5112 語。4.3 の欄が 1,300 語に収まる見込みが薄い（F）。
- e 4: 宣言とデータの声明は計画にある。要旨と keywords は段の上で欠陥にしない。プレプリントの方針は未読。照合できない文が 1 つ（G）。
- f 3: 関連研究と新規性は補われたが、Uto 2020 の評価設計が未確認（Open items）。

## 3. 引き継ぎの判定
1 A 解消（C1 の "The synthetic detection rule is defined across seeds and is not applied to the one real panel."・置き換えた先に新しい穴）／2 B 解消（開示として）／3 C 解消（l.63）／4 C2 一部（Uto が Open items）／5 D 一部（余裕が小さい・E）／6 E 解消／7 F 一部（F）／8 G 一部（H）／9 H 解消。

## 4. 指摘
- [major] A. 選ぶ候補に、同じ候補集合の prior mode が大半の書き手で勝つ。選びの目的関数が予測の良さを選んでいない
  - 位置と引用: C1（l.13）「the mode is chosen for at most 1 of 17 writers ... but the chosen per-person model does not beat the prior mode: per-person minus mode is −3.5e-4 to −1.6e-4 (positive for 2 to 6 of 17 writers)」／3.3（l.33）「The objective is this median of differences; it is neither the target writer's predictive accuracy nor the per-person gain over the shared model」
  - なぜ問題か: prior mode は候補に入っているのに、11〜15 人で予測が劣る候補が選ばれる。目的関数（他人の per-person − chain の中央値）が held-out の予測を順位づけない。それでいて 5 節でこの選び方を勧める（Varma & Simon "Since selection of classifier parameters ... is a kind of training, it should be included as part of the classifier training algorithm."）。C1 の貢献（評価のプロトコル）の信用を削る。
  - 解消の条件: (i) 目的関数を「他人の held-out の nats per symbol の中央値（候補ごと）」にした選びを感度として出し、Take-home が成り立つか示す、または (ii) per-person − chain の中央値を目的にする理由を本文で示し、prior mode に負ける選びが起きることを C1 の限界として 5 節の勧めに明記する。
  - 自信: 高
- [major] B. Take-home の「prior mode を上回らない」は 1 パネルの結果で、データが最も多いセルでは逆
  - 位置と引用: Take-home（l.7）「the chosen per-person model does not beat the shared model's prior mode, which uses none of the person's data」／C1（l.13）「In the 30-session panel at k = 30 ... per-person minus mode is +5.4e-4 (7 of 9 positive); both are reported as values only」／4.3（l.50）「CS1: the mode is chosen for every writer, so per-person minus mode is zero by construction」
  - なぜ問題か: 30-session では k = 1〜20 で負、k = 30 で正（7/9）。「個人のデータが増えると追いつくか」は cold-start の問い（LiKamWa 2013 の約 30 日）そのもので、values only で済ませると結論が逆になりうる。
  - 解消の条件: Take-home と要旨を「15-session のパネルで、k ≤ 15 では」に限り、30-session の k = 30 の逆転を同じ段落で 1 文（限界の "longer records may change the picture" だけでは足りない）。
  - 自信: 高
- [major] C. 新しい比べ（prior mode）は合成で確かめられておらず、合成の書き手はこの点で実データと逆
  - 位置と引用: 4.3 の補足欄（l.50）「in these synthetic writers the prior mode was worse than the shared model in every cell, unlike the real data; values only」／冒頭（l.3）「the shared model's prior mode placed among the comparison models and the candidates, recomputed from stored per-writer values without new fits」
  - なぜ問題か: 決め手が「per-person が mode を上回らない」に変わったのに、埋めた差（1e-2・3e-2）で per-person − mode が正になるかの報告が無い（Varma & Simon は "null" と "non null" の両方で確かめた: "With "null" and "non null" (with differential expression between the classes) data, we also tested a nested CV procedure"）。合成では mode が shared より常に悪く、実データでは良い。S15 の感度の結論を実データへ移すことにも疑いがかかる。
  - 解消の条件: S15 の合成で、埋めた段ごとに per-person − mode の中央値と正の割合を報告する（保存した値から再計算できるなら条件を先にコミットして）。食い違いの理由を 1 文、感度の結論をどこまで実データへ移せるかを限界に。
  - 自信: 中
- [minor] D. 勧める手順が held-out に確率ゼロを与えるモデルを割り当てうる。prior mode の定義も曖昧
  - 位置と引用: 3.3（l.31）「the normalized expected counts of the shared model ... differs from the shared parameters by the smoothing of the prior」／5 節（l.51）「noting that a prior mode with zero-probability cells can be assigned to a writer whose data it gives zero probability」／限界（l.68）
  - なぜ問題か: 平滑で異なると書きながら確率ゼロが出る。−∞ を出しうる候補をそのまま勧める。"positive for 2 to 6 of 17" の数え方が追えない。
  - 解消の条件: mode の式（Dirichlet の超パラメータと tau の関係・ゼロが出る条件）を 3.3 か S3 に。勧めの中で「ゼロのセルは候補から除くか平滑する」と手順を決める。
  - 自信: 中
- [minor] E. CS1 の「1e-3 以上の差は無いことと整合」の余裕が小さい
  - 位置と引用: 4.3 の補足欄（l.50）「at 1e-3 tau = 10^6 was chosen for every writer and 87% and 100% of writers were positive, and up to 78% of writers were positive in the negative control」
  - なぜ問題か: 規則 80% に対し陰性対照 78%・検出側 87%・種は段ごとに 2 本（Varma & Simon "For SVM with optimal parameters the estimated error rate was less than 30% on 38% of "null" data-sets"）。
  - 解消の条件: 「2 種とも規則を満たした（陰性対照の最大 78%）」と値で書き、整合の主張を弱める。または種を増やす。
  - 自信: 中
- [minor] F. 4.3 の本文欄が 1,300 語に収まらない見込み（l.50・外枠 5112 語）。解消: 4.3 を「選びの結果」と「prior mode との比べ」の 2 小節に分ける。合成と記号化の文は 6 節への参照 1 文。自信: 中
- [minor] G. 「公開の記号化が元の記号を再現する」は読者が確かめられない
  - 位置と引用: Statements（l.54）「a statement that the public symbolization reproduces the original symbols for every CoAuthor session ... (match counts only)」／kit/symbols/README.md l.78「That comparison used the raw datasets and is not part of this kit.」
  - 解消の条件: 元の記号の列のハッシュ（記録ごとの SHA-256）を補足に載せるか、この文を落とす。
  - 自信: 中
- [nit] H. 後の確かめの数が冒頭（l.3「four sequentially designed analyses and three later checks」）と 3.4（l.47「four later checks」）で違う。自信: 高
- [nit] I. Liu & Meng の版（l.15「Liu and Meng 2016」）。接地の本文は arXiv:1510.08539v1。引く版の本文で逐語を照合する。自信: 中

## 5. 総合の推奨: major
引き継ぎの major A は解消したが、置き換えた決め手でプロトコル自身が候補集合の中の劣る候補を選ぶことが露わになった（A）。Take-home は 1 パネルに支えられ最も多いセルで逆転する（B）。新しい比べの検出力が合成で示されず、合成と実データがこの点で食い違う（C）。

## 6. 読めなかった範囲・注入の疑い
読んでいない: liumeng.txt の l.1025〜1699 と l.1760〜2013（"relevance"・"leave-one-out" は全文を grep）。補足 S1〜S15 とコード。規程は context-A の抜粋だけ。注入の疑い: なし。読んだファイル: round-4 の brief-R3.md・context-A.md・carryover-R3.md、outline.md、kit/symbols/README.md、round-1/tmp/sources/varma.txt・liumeng.txt（一部）。
