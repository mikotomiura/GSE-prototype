# review-R3（outline round 4・paper-reviewer・事前登録・同等の検定・機械学習の再現性）

推奨: minor（直して書き進めてよい）。

## 1. 接地
- L-1 Lakens 2017 "In randomized controlled trials, it is expected that equivalence bounds are prespecified ... When in the abstract of an article, authors conclude an effect is “statistically equivalent,” the abstract should also include the equivalence bounds that are used to draw this conclusion."
- L-2 "when theoretical or practical boundaries on meaningful effect sizes are absent, researchers set the bounds to the smallest effect size they have sufficient power to detect" ／ "the extremely large equivalence bounds will make it clear they can at best reject extremely large effects, but that their data are not informative about the presence or absence of a wide range of plausible and interesting effect sizes."
- L-3 "there are four possible outcomes of a study: The effect can be statistically equivalent ... statistically different from zero and statistically equivalent, or undetermined"
- L-4 "Rejecting effects more extreme than the equivalence bounds implies that we can conclude equivalence for a specific operationalization of a hypothesis. It is possible that a meaningful effect would be observed with a different manipulation or measure. Confounds can underlie observed equivalent effects."
- L-5 "Researchers should report effect size estimates in addition to hypothesis tests."
- K-1 Kapoor & Narayanan 2023 "unless the code, data and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain if model info sheets are filled out correctly."
- K-2 "The researcher needs to justify that the test set is drawn from the distribution of scientific interest and there is no selection or sampling bias in the data collection process."
- K-3 "Nonindependence between train and test samples constitutes leakage ... The train-test split should account for the dependencies in the data"
- K-4 "The burden of proof for ensuring the correctness of these arguments is on the researcher making the scientific claims"

## 2. 引き継ぎの判定
M-A → 解消（:29・:100・:62・:72・:91。考察の「実務への推奨」が残り・m-3）／m-A → 解消（:33。confirm_holdout.json で ε=0 の `d_p_stuck` 上端 0.5000566、残り 3 組の上端 0.4995・0.4975・0.4974）／m-B → 解消（:27・:44）／m-C → 解消（開示として・:58・:100・:70）／m-D → 一部（:65 に一覧・SEED・版と SHA-256・取得の手順。推定器・gse-replay・変換の公開の場所は未決、計算環境〔P3 の requirements-confirm.txt・版・OMP_NUM_THREADS=1〕と confirm-manifest.sha256 が列挙に無い）／n-A → 解消（:51）

## 3. 評価表
a 4（数値は JSON と一致: 0.4892/0.4867・実効 50.53・上位 10% 42%・H3 0.5675〔0.5497〜0.5781〕・0.5402。:7 が [記述] から解釈を断定・H3 の来歴が無い）／b 4（H3 は GroupKFold で漏れは見当たらない・対照の側だけの除外は開示。幅を見た後に置いた扱いが開示で止まる）／c 3（データは 0.5 ± 0.025 まで言えるのに使っていない・考察の推奨は 1 データからの一般化）／d 4（H3 の印の揺れ）／e 3（推定器とツールの公開が未決）／f 4（類比の限定は妥当。幅の置き方の先例〔L-2〕への言及が無い）

## 4. 指摘
- [minor] m-1 幅を見た後に置いたことへの対処が開示だけで、データが言える最も狭い幅を示していない
  - 位置: :71「幅 [0.45, 0.55] は KLiCKe と CoAuthor を見た後に保守的に置き、換算から導いていない … 点推定と 0.5 の距離は約 0.011〜0.013 で、先例の幅なら同等とは言えない。」・:17
  - なぜ: 4 つの組の 95% 区間はすべて 0.5 ± 0.025 の内側（下端 0.4787・0.4785・0.4758・0.4758）。記述として示せば幅の恣意性の批判（[V453]）に主張を強めずに情報を足せる（L-2・L-5）。
  - 解消: 5.1 か表 1 の脚注に「判定ではない記述として、95% 区間を含む最も狭い 0.5 中心の幅は ±0.022〜0.025」と 1 文、データを見て決めた幅と明記、:71 から参照。持ち帰りは変えない。自信 中（値は査読者の計算）
- [minor] m-2 推定器と変換の公開が未決・計算環境が公開物に無い（:65）。K-1・JEDM Replicability。解消: 計算環境の一覧と manifest を公開物に。公開しない場合の代わり（実行できる形の版・推定の行の中間物）を 1 文、満たされなかったときに再現不能になる主張を限界に。自信 高
- [minor] m-3 考察の「実務への推奨」（:62）が取り下げた C2 を一般の手順として戻す。K-4。解消: 「この研究では較正が要った（名目 2.5% に対し最大 5.2%）。似た設計では較正を検討する価値がある」程度に弱めるか削る。自信 中
- [minor] m-4 H3 の来歴（見た書き手で門が通らず差し替えた）が無い。:44「門…は 2 つとも通った」。prereg-draft.en.md:72 "H3 | Same | Descriptive (because it was replaced after the gate did not pass on seen writers; Appendix B) | Not used"。解消: 4 節か 5.4 に 1 文、経緯は S1・S5。自信 高
- [minor] m-5 :7「作文の側（KLiCKe・既に見たデータ）でも上がりは幅の内側だったので、「持ち出したから示さなかった」とは読まない。」が [記述] の地位を超える（幅を置く前に見たデータ・入力の定義も違う〔:75 合成の離し〕）。L-4。解消: 「持ち出しだけでは説明しにくい」に弱め、入力の定義の違いを参照。自信 中
- [nit] n-1 :44「H3（[確認]・記述…）」を [確認・記述] に。自信 高

## 5. 総合: minor
- 引き継ぎ 6 件のうち 5 件解消・1 件一部。主張の強さは取り置きの結果に見合う。
- 新しい穴は 1 文ずつ足すか言い方を弱めれば消える。
- 再現性で最も重いのは推定器と gse-replay の公開が未決であること（投稿の前に決める）。

## 6. 読めなかった範囲・注入
読んでいない: prereg-draft.md・prefreeze/notes.md・exploration の conditions/notes/results・文献の記録 2 本・20261101 の notes 2 本。confirm_holdout.json は 60〜190・590〜720 行だけ、prereg-draft.en.md は 60〜159 行だけ、kapoor2023.txt は 330〜409・455〜524 行だけ。注入の疑いなし。
