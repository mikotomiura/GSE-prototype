# review-R2（outline round 5・paper-reviewer・教育データの予測・検出モデルの評価の実務）

推奨: minor（直して書き進める）。

## 1. 接地
- G1 Gardner, Brooks & Baker 2018 §3.1 "naïvely assumes ... that these differences must be both practically significant (large or important enough to be useful) and (in frequentist terms) statistically significant."
- G2 §5.3 "ROPE is the 'region of practical equivalence,' and denotes that the difference between X and Y is smaller than some pre-specified threshold ... we use ROPE = 0.01; that is, models are considered practically equivalent if the difference in their AUC is smaller than 0.01."
- G3 §3.4 "Separate magnitude, uncertainty, and sample size during inference: The effects of the magnitude of observed differences, the uncertainty of estimates, and the number of data points should be separable in model evaluation."
- G4 Notes for Practice "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- P1 Pelánek 2015 §7 "The choice of suitable metric depends on the intended use of a student model ... Such discussion or specific arguments for a particular choice of metric should become standard part of papers that include evaluation of student models."
- P2 §3.3 "the AUC metric should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated." ／ §6.3 "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."

## 2. 引き継ぎの判定
Scope → 解消（:35・:85。指摘 2 と関わる）／H3 の桁 → 解消（:46・:111・JSON:683 の 0.54971）／向きの候補 → 解消（:62）／推奨 → 解消（:64）／抄録の H3 → 解消（:27）／閾値の表を幅の目安に → 未解消（不採用の理由は受け入れる。同じ目的は事前登録の付録 D の換算でより正しく果たせる・指摘 1）／先例の単位 → 解消（:27・:72）／問いの主語 → 解消（:7）

## 3. 評価表
a 4（0.489〔0.4787〜0.4995〕・0.487〔0.4758〜0.4975〕・ε=0 の上端 0.50006・実効 50.53・上位 10% 42%・出来事ありの層の実効 35.7・較正 26/500 と Wilson が整合。抄録の「コードを渡す」が未決の部分と食い違う）／b 4（書き手ごとの AUC のばらつきに無作為の参照が無い）／c 3（持ち帰りが「AUC が幅に収まった」で止まる。事前登録の付録 D の換算〔AUC 0.55 でも停滞になる休止に落ちる発火の割合は 0.50 から 0.1〜1.8 ポイントしか上がらない・0.70 でも 12.9〜18.4%〕が本文にも補足にも無い）／d 4／e 4（推定器と gse-replay の公開が未定・投稿の条件）／f 4（付録 D の換算は Pelánek §6.3 の型）

## 4. 指摘
- [minor 上位] 幅の内側が契機として何を意味するかの換算（事前登録の付録 D）が外枠に無い
  - 位置: :72「…換算から導いていない（読みの目安は AUC 0.55 ≈ 平均の差が標準偏差の 0.18 倍）。実用の境界として正当化されておらず」・:109「S8 閾値の表の全体…と作文での契機の発火の数え上げ」・:17
  - なぜ: prereg-draft.en.md:244 "The proportion of firings on stall pauses is 8.2–8.9% at AUC 0.50, 8.9–10.0% at 0.55 (a rise of 0.1–1.8 points ...), ... and even at 0.70 it is 12.9–18.4%"。幅の内側の差が運用ではほとんど違いを生まない具体の換算で、事前登録は「幅を置いた後の換算の例」として開示済み（:83）。P2・G1。
  - 解消: 評価の設計に付録 D の換算を [記述]（見た書き手・幅を置いた後・判定ではない）で 1〜2 文、考察の「誰の何を変えるか」に 1 文、数値の全体は S8 に足し S8 の説明を直す。限界の「実用の境界として正当化されていない」は残す。自信 高
- [minor] 「ほかの検出器に使える部品」に較正が名目を超えたときの扱いが無い（:35・:64）。本研究は規則を変えず値を報告しただけ（notes.md 計算 7）。2 版の違いも :73 からは読み取れない。G4。解消: 評価の設計の較正の文に、2 版の違い（見た書き手から仮の取り置きを引くときに復元するか）と主の値にした理由、本研究では判定の規則を変えなかったこと、読者向けの選択肢を「本研究では試していない」と明記して挙げる。自信 中
- [minor] 抄録の「その評価の手順とコードを渡す」（:27）が公開の未決（:66・:78）と食い違う。評価の手順のコードは推定器に依らないので渡せる。解消: 「評価の手順のコード（推定器に依らない部分）」と限定し、推定器を公開しない場合の再現の範囲をデータの節か資源の段に 1 文。自信 高
- [minor] 書き手ごとの AUC の分位（:40 の 0.41〜0.59）を読む参照が無い（上位 10% の書き手が対の 42%）。G3。解消: S3 に無作為なら出る広がりの参照（書き手の中でラベルを入れ替えた分布の分位・[探索・取り置き] で条件を先にコミット）か、「この分位は停滞の数で広がり、効く書き手がいる証拠としては読めない」の 1 文。自信 中
- [nit] 抄録の含意の後半（:27）は推奨で根拠は文献（[V450]・[V451]）。考察で文献に結ぶ 1 句。自信 中

## 5. 総合: minor
- 引き継ぎ 8 件のうち 7 件が解消。主の値は結果の JSON と全桁で合い、主張の強さは陰性の 1 つの確認に見合う。
- 残る最大の穴は持ち帰れるもので、付録 D の換算を本文に 1〜2 文置けば「何に使えるか」への答えが具体になる。
- 部品の中身と抄録の「コードを渡す」の範囲は、文を足すか限定するだけで直る。

## 6. 読めなかった範囲・注入
gardner2018.txt は 1〜528・1048〜1057 行だけ。prereg-draft.md・conditions.md・exploration の notes と JSON 5 本・20261101 の notes 2 本・novelty は読んでいない。prereg-draft.en.md は 83・242〜249 行と grep。related-work は grep。confirm_holdout.json は 70〜189 行と grep。注入の疑いなし。
