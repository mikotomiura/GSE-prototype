# 文献カード: 共通へ縮める 1 人ごとの推定の先例 —— 多水準 HMM・話者適応の MAP・部分的なプール・入力の言語モデルの個人化

- **トピック**: per-person-shrinkage-prior-art
- **日付**: 2026-11-07
- **作業記録**: `.steering/20261107-gse-paper3-per-person-learning/`（論文 3・attack-me outline round 1 の後・判断 12）
- **用途**: 論文 3 の関連研究と新規性の文の根拠（gate 判定ではない）。結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。

## 動機

前ラウンド（`20261107-per-person-gain-comparison-baselines.md`）の `_index.md` の行は、やり残しを次のように名指しした: 「Pardos & Heffernan 2010・Yudelson 2016 EDM・Chung ほか 2013（分散の 0 への張り付き）・Aarts & Haslbeck 2025（多水準 HMM）・Garcés-Manzanera 2026（L2 打鍵の HMM）の本文、[V501] の Chrome での照合、[V507] の雑誌版」。加えて attack-me outline round 1 の verdict の直す順 8 が、関連研究に「多水準 HMM と階層／経験ベイズの部分的なプール」を置き、「多水準 HMM（Aarts & Haslbeck 2025）は読んでから確定」と求めた。R2 はキーボードの言語モデルの個人化（全体と個人の補間）を挙げた。論文 3 の手法は、1 人ごとの HMM・AR(1)-HMM の母数を、対象の人を除いた共通のモデルの期待度数を中心にした集中度 τ の Dirichlet で MAP-EM 推定し、τ を他の人の後のセッションの予測で選ぶ（`experiments/20261104-coauthor-ml-improve/conditions.md` の推定の節）。この形が、どの系統の何に当たるかを確かめる。

## 検証状態

- 下位の問い 4 つ（(a) 多水準・混合 HMM と話者適応の MAP、(b) 階層モデル・経験ベイズの部分的なプールと分散 0 への張り付き、(c) 入力の言語モデルの個人化、(d) 反証と前ラウンドのやり残し）を、Sonnet のサブエージェント 4 本で並列に探した。
- 新規に登録: 24 件（[V510]〜[V533]）。既登録で番号だけ挙げたもの: [V386]・[V387]・[V497]〜[V509]（特に [V387]・[V501]・[V503]・[V504]・[V505]・[V507]・[V508]・[V509]）、[V98]、[P226]。
- 一次の照合: 本文を取れた 20 件は、サブエージェントが持ち帰った逐語の引用を、メインが原本の全文（ACL Anthology・ISCA archive・PsyArXiv/OSF・arXiv・bioRxiv・著者のページ・Europe PMC・EDM の proceedings）から抜いた文字列で照合した（照合した引用は全件一致。不一致に見えたものは段組・ハイフン・OCR の空白の崩れで、本文の文は同じ）。[V501] Ferrari はメインが Chrome で大学のリポジトリの PDF を取り、本文で照合した（下のカード 6）。抄録だけのもの: [V516] Altman 2007・[V531] Pardos & Heffernan 2010。本文未読で書誌だけ確かめたもの: [V510] Gauvain & Lee 1994（会議版 [V511]・[V512] で照合）・[V513] Reynolds ほか 2000（式は [V514] の再掲で確かめた）。[V507] Stoye の雑誌版は今回も取れず、arXiv 版で照合した。→ この 5 件と [V520] の雑誌版相当は、同じ日の後で著者のページ・研究室のサイト・保存版・オープンアクセスの雑誌版から本文を取り、メインが照合した（末尾の「追加の照合」）。
- claim 14 件を抽出し、3 票（内的妥当性・外への広げ・頑健さ）で判定した。確定 6・留保つき確定 5・判定不能 1。否決 2 件と、登録しなかった候補を末尾の否決リストへ。

## 要点（下位の問いごとの温度）

| 下位の問い | 温度 | 一言 |
|---|---|---|
| 論文 3 の τ の MAP は、多水準 HMM の特殊な場合か | **否決（0-3）** | Aarts & Haslbeck の多水準 HMM は多項ロジットの切片に正規の集団分布を置き、集団の分散を階層ベイズで推定する（[V515]）。共役の Dirichlet で共通へ縮める形とは別物。τ = 0 と τ = ∞ の両端を含む点が似るだけ |
| では何に当たるか | 確定 | 音声の話者適応の MAP（[V510]〜[V512]）の離散 HMM 版。話者に依らないモデルを中心にした Dirichlet を π と A の各行に置き、重みが大きいと適応がわずかになる。relevance factor（[V513]・[V514]）が τ に当たる |
| 縮小の強さ（集中度）の選び方の先例 | 確定（留保つき） | 話者適応は、集団の学習データからの推定か、固定の慣習（τ = 16 など）・経験的な調整で、他の話者の予測で選ばない（[V511]・[V514]・[V533]）。多水準 HMM は集団の分散を推定する（[V515]）。入力の言語モデルの個人化は、補間の重みを**他の利用者**で選び、**同じ利用者の後の時点**で測る（[V525]・[V526]・[V527]・[V528]） |
| 分散 0（完全なプール）への張り付きの読み方 | 確定（留保つき） | 集団が少ないと最尤の分散は 0 に張り付きやすく、点推定の欠点・事前に考えにくいときの不安定さと読む（[V519]〜[V521]）。ただしどれも周辺尤度の点推定の話で、他の人の予測で選んで τ = ∞ が最良になった論文 3 の結果をそのまま説明しない |
| 予測の対象（既存の単位の将来か、新しい単位か） | 確定 | 階層モデルでは、既存のグループの新しいデータと、新しいグループのデータで、予測分布も評価も別になる（[V522]・[V523]） |
| 共通の構造を良くすると個人化の上積みが消える、を直接測った研究 | **判定不能（0 件）** | 見つからなかった。最も近いのは、強い背景モデル（12-gram）では cache の効きが小さいという著者の推測（[V526]）で、測定ではない |
| 人の行動の記号列で HMM を 1 次のマルコフと比べた研究 | 確定（前ラウンドの 0 件を直す） | 同じデータの中の比べ（DIC と事後予測の検査）なら Shirley ほか 2010 がある（[V517]・飲酒の日の列）。保持した後の時点の予測の尤度で比べた研究は、今回も見つからなかった |

→ 論文 3 で新しいと書けるのは、さらに狭まる。(1) τ の MAP そのもの（話者適応の MAP の離散版）、(2) 個人に寄せる強さを他の人で選ぶこと（入力の言語モデルの個人化の標準の流儀）、(3) 同じ人の後の時点で測ること（同上）は、どれも先例がある。残るのは、**比べの相手（同じ構造の共通のモデル）の構造を替えると、1 人ごとの上積みが消えることを示した点**と、**HMM を本人の 1 次のマルコフと、保持した後の時点の予測で比べた点**で、どちらも「今回の探索では見つからなかった」水準に留まる。

---

### カード 1: 論文 3 の τ の MAP は、話者適応の MAP の離散 HMM 版に当たる **[検証済 3-0 / 2-1]** [V510] [V511] [V512] [V513] [V514] [V533]

1. **どんなもの？** 話者に依らない HMM を、少量の話者のデータで話者ごとの HMM に適応させる MAP 推定（[V511]・[V512]、雑誌版は [V510]）。話者照合の GMM-UBM で、全体のモデル（UBM）の平均を relevance factor で話者へ寄せる適応（[V513]・式は [V514] の再掲）。relevance factor を経験的に調整する慣習と、それを発話の長さに合わせて変える案（[V533]）。
2. **先行研究と比べてどこがすごい？** [V511] の逐語: "a Dirichlet density can also be used for the initial probability vector π and for each row of the transition probability matrix A"。[V512] の逐語: "speaker adaptation may be viewed as adjusting speaker-independent models to form speaker-specific ones, using the available prior information and a small amount of speaker-specific adaptation data"、"When this weight is large, the prior density is sharply peaked around the values of the SI HMM parameters and these values will be modified only slightly by the adaptation process"。[V514] の逐語（Reynolds の方式の再掲）: "αm … is calculated via a relevance factor τ"、"for our experiments an τ = 16 received good results"。[V533] の逐語: "such mismatch can be compensated partly by empirically adjusting the relevance factor (RF), which controls the degree of adaptation"。
3. **技術や手法の肝はどこ？** 事前分布の中心を全体（話者に依らない）のモデルに置き、集中度（重み・relevance factor）で本人のデータとの釣り合いを決める。論文 3 の擬似度数 = 基 + τ × 共通の期待度数の割合は、この形の離散の場合と同じ。[V511] の逐語 "as Q → ∞, the MAP reestimation formulas approach the ML ones" の Q は観測の列の数で、データが増えると本人だけの推定に近づく、という意味（τ → 0 の話ではない）。
4. **どうやって有効だと検証した？** 単語誤り率・話者照合の誤り率。集中度は、[V511] の逐語 "the prior density parameters were estimated along with the estimation of the SI model parameters"（集団の学習データから推定）、[V514] は固定の値。他の話者の後の時点の予測で選ぶ手続きは、読んだ本文には無い。[V512] は "a common value for all the HMMs was estimated. This is clearly too strong a constraint" と自ら書く。[V512] の話者ごとの表では、適応で話者に依らないモデルより悪くなる話者がいる（サブエージェントの読み・数値はメイン未照合）。
5. **議論はあるか？** 留保（1 票・頑健さ）: 雑誌版 [V510] と Reynolds の原典 [V513] の本文は、この時点では未読で、形の同一は会議版と再掲で確かめた（後で両方の本文で照合した・末尾の「追加の照合」）。[V511] の多くの実験は "the transition probabilities are assumed fixed and known" で、遷移に事前分布を置いた実証は少ない。論文 3 の外枠で「新しい推定法」とは書けない。「話者適応の MAP（[V510]）を記号列の HMM に当てた」と書く。
6. **次に読むべき論文は？** [V510] と [V513] の本文。relevance factor の選び方を比べた研究（Interspeech 2012 の "Effect of relevance factor of maximum a posteriori adaptation for GMM-SVM"・doi:10.21437/interspeech.2012-551・未読）。

### カード 2: 多水準 HMM は集団の分散を階層ベイズで推定し、評価は母数の回復。混合 HMM の効きは小さく、大きな標本が要る **[検証済 3-0 / 2-1]** [V515] [V516] [V518]

1. **どんなもの？** 心理の時系列の多水準 HMM の数値実験とチュートリアル（[V515]・PsyArXiv v2）。経時のデータへの混合 HMM（[V516]・GLMM の枠組み）。動物の遠隔測定で、HMM に個体のランダム効果を入れる価値を確かめた研究（[V518]）。
2. **先行研究と比べてどこがすごい？** [V515] の逐語: "we only need to specify prior distributions on the group-level parameters, since the estimated group-level distributions take on the role of priors for the subject-level parameters"、"the hierarchical priors imply a regularization on the subject-level parameters, which to some extent shrinks the parameters towards the group-level means"、事前の強さは "K0 denotes the number of hypothetical subjects on which the prior mean vector … is based"。[V518] の逐語: "I generally found mixed HMMs did not improve state assignment relative to standard HMMs. Reliable estimation of random effects required larger sample sizes than are often feasible in telemetry studies"。
3. **技術や手法の肝はどこ？** 個人の母数を集団の分布から引く。縮小の強さは集団の分散で、データから推定する（固定でも他の人の予測で選ぶのでもない）。
4. **どうやって有効だと検証した？** [V515] はシミュレーションでの母数の回復（被験者 15〜120 人）と事後予測の検査。本文に "out-of-sample" は 0 回（メインが全文で数えた）。[V518] はシミュレーションの状態の割り当てと AICc。[V516] はシミュレーションと実データの例で、予測の評価は無い（後で本文で照合・末尾の「追加の照合」）。[V515] は "the dimensions of the integral … make fitting these methods largely intractable for more complex models" と評する（サブエージェントの読み・メイン未照合）。
5. **議論はあるか？** 留保（[V518] に 1 票・外への広げ）: 動物の移動で、評価は状態の割り当て。人の後の時点の予測の尤度で、個人の分布つきと共通のモデルを比べた研究は、この系統の中にも見つからなかった。論文 3 の「1 人ごとの上積みは小さい」と同じ向きの傍証として [V518] を引ける。
6. **次に読むべき論文は？** [V516] の本文。Aarts の R パッケージ mHMMbayes の文書（書誌未確認）。

### カード 3: 分散 0（完全なプール）は、集団が少ないとき最尤の点推定に出やすく、欠点・不安定さとして読まれる **[検証済 2-1]** [V519] [V520] [V521] [V524]

1. **どんなもの？** 階層モデルの分散の事前分布の論考（[V519]）。分散の推定が 0 になるのを罰則つき尤度で避ける推定（[V520]）。多水準の正規モデルの縮小推定（[V521]）。野球の打率で Stein の推定を同じ選手の残りの季節で確かめた古典（[V524]）。
2. **先行研究と比べてどこがすごい？** [V520] の逐語: "Group-level variance estimates of zero often arise when fitting multilevel or hierarchical linear models, especially when the number of groups is small. For situations where zero variances are implausible a priori, we propose a maximum penalized likelihood approach to avoid such boundary estimates"。[V521] の逐語: "A flaw of the MLE is that ÂMLE = 0 occurs commonly. This not only dictates full shrinkage"。[V519] の逐語: "in a hierarchical model the data can never rule out a group-level variance of zero"。[V524] の逐語: "The problem is to predict each player's batting average over the remainder of the season"、"Stein's estimators achieve uniformly lower aggregate risk than the MLE but permit considerably increased risk to individual components"。
3. **技術や手法の肝はどこ？** 縮小の強さを周辺尤度で推定すると、境界（完全なプール）に張り付くことがある。それを避ける事前分布・罰則を置く。
4. **どうやって有効だと検証した？** [V520] はシミュレーションと例。[V524] は同じ選手の後の時点の打率で、本人だけの推定（MLE）と縮めた推定を比べた。縮小の係数は同じ全員のデータから 1 つ推定し、他の単位で選んでいない。
5. **議論はあるか？** 留保（1 票・外への広げ）: どれも分散成分の点推定が 0 になる話で、論文 3 の CS1 で「他の人の予測で選ぶと全員で τ = ∞（共通のモデル）が選ばれた」結果は、周辺尤度の境界推定ではない。予測で選んで ∞ が最良なら、データの示す答えである可能性が残る。向きの注意: [V519] の σα は集団の分散で、σα = ∞ はプールしない側、σα = 0 が完全なプール。論文 3 の τ は集中度で向きが逆（τ = ∞ が完全なプール）。外枠で「boundary」「pooled limit」を使うときに、どちらの向きかを明記する。[V520] は 8 頁の著者版（Gelman のページ）で照合し、後で 25 頁の版（雑誌の 685–709 頁の組版）でも抄録の逐語を照合した。
6. **次に読むべき論文は？** Morris 1983 JASA（parametric empirical Bayes・doi:10.1080/01621459.1983.10477920・未読）、Gelman & Hill 2007（未読）。

### カード 4: 予測の対象が「既存の単位の将来」か「新しい単位」かで、予測分布と評価が分かれる **[検証済 3-0]** [V522] [V523]

1. **どんなもの？** 潜在変数のモデルの比べで、条件つきの尤度と周辺の尤度の違いを整理した研究（[V522]）。ベイズのモデルの予測の情報量規準の総説（[V523]）。
2. **先行研究と比べてどこがすごい？** [V522] の逐語: "The conditional/marginal distinction corresponds to whether the model should be predictive for the clusters that are in the data or for new clusters"、"marginal WAIC corresponds to leave-one-cluster out (LOcO) cross-validation, whereas conditional WAIC corresponds to leave-one-unit out (LOuO)"。[V523] の逐語: "new data from existing groups"、"new data from a new group"。
3. **技術や手法の肝はどこ？** 同じ人の将来を当てる（条件つき）か、新しい人を当てる（周辺）かを、評価の前に決める。
4. **どうやって有効だと検証した？** 理論と例。
5. **議論はあるか？** 論文 3 は、評価は対象の人の将来（既存の単位の将来）で、τ と構造の選択は他の人の将来の予測の差の中央値で行う。選ぶ側も既存の単位の将来の予測で、新しい単位の予測（[V505] の他の n − 1 人で当てて本人を予測する形）とは違う。外枠でこの区別を 1 文で書ける。
6. **次に読むべき論文は？** 縮小の強さそのものを leave-one-group-out の予測で選ぶ統計の手続き（今回は見つからなかった）。

### カード 5: 入力の言語モデルの個人化は、補間の重みを他の利用者で選び、同じ利用者の後の時点で測る。効きは小さいが残る **[検証済 3-0 / 2-1]** [V525] [V526] [V527] [V528] [V529]

1. **どんなもの？** タッチスクリーンの入力で、背景の言語モデルと本人の cache を補間した研究（[V525]・Enron のメール）。その再現と、より強い背景（12-gram）・PPM・RNN の組み合わせ（[V526]）。本人の文の量ごとに個人化の方法を比べた研究（[V527]）。補間の重みの選び方を比べた研究（[V528]）。連合学習の全体モデルを本人のデータで微調整した研究（[V529]）。
2. **先行研究と比べてどこがすごい？** [V525] の逐語: "we found the optimal λ value to be 0.8"（λ は背景の重み・開発用の利用者で選んだ）、"each Enron user typing his or her test set in chronological order"。単語誤り率は背景だけで 5.7%、個人化で 4.6%（本文の表）。[V526] の逐語: 重みは "keystroke savings on six users"（開発用）で選び、"We suspect this is due to the 12-gram LM conditioning on more previous text"（cache の効きが [V525] より小さかった理由の推測）。12-gram の背景より keystroke savings が 4.3 ポイント増えた。[V527] の逐語: "none of the models are the best performing model for every amount of text from the user"。[V528] は α を全員で一定にすると perplexity の改善は利用者の 67.3%・平均 2.5%（本文の数値）、時間で分けた評価（逐語 "the data from 2016 as training data"）。[V529] の逐語: "in chronological order at the 9 : 1 ratio"、改善は "2.32%, 2.12%, and 2.12%"。
3. **技術や手法の肝はどこ？** 全体と本人のモデルの線形の補間（または微調整）。重みは少数の他の利用者（5〜45 人）で選んで固定するのが多い。
4. **どうやって有効だと検証した？** 時間で分けた同じ利用者の後の時点（[V525]・[V526]・[V528]・[V529]）。[V527] は本人の文を学習と保持に分け、時間順かは未確認。
5. **議論はあるか？** 留保（[V529] に 1 票・頑健さ）: [V529] は正解率で尤度ではない。反証の側: 強い背景でも上積みは残る（[V526] は 12-gram でも 4.3 ポイント。flat start で 44 人中 37 人が改善はサブエージェントの読み・メイン未照合）。[V528] では約 2〜3 割の利用者が悪化する。論文 3 への含み: 「τ を他の人で選び、同じ人の後の時点で測る」は、この系統の標準の流儀で、論文 3 の新規性に数えない。「共通の構造を良くすると上積みが消える」は、[V526] が推測として書くだけで、6-gram と 12-gram で個人化の差分を並べた表は無い（判定不能・0 件の直接の測定）。
6. **次に読むべき論文は？** Chen ほか（Smart Compose の補間・[V528] が引く）、Kuhn & De Mori 1990（cache の言語モデル）、Bellegarda 2004（言語モデルの適応の総説）。どれも未取得。

### カード 6: やり残しの照合 —— Yudelson 2016・Ferrari 2020・Stoye 2025・Pardos & Heffernan 2010 **[検証済 3-0 / 2-1]** [V530] [V501] [V507] [V531]

1. **どんなもの？** 知識追跡の学習者の母数を階層ベイズで入れた研究（[V530]・336 人・30 技能）。活動認識の個人化の 3 方式（[V501]）。自己回帰の HMM（[V507]）。学習者ごとの事前の習得の確率の知識追跡（[V531]）。
2. **先行研究と比べてどこがすごい？** [V530] の逐語: "in both the weight of the per-skill parameters (Wk) are two to three times smaller than that of per-student parameters (Wu)"、"One explanation for that could be possible over-fitting"、正則化については "While we did not specifically check or prove this"。[V501]（メインが Chrome で大学のリポジトリの PDF を取り、本文で照合）の逐語: "it is quite clear that the hybrid strategy works better than the subject-independent one, the improvement is of about 3%"、"apart from UniMiB-SHAR, the subject-dependent strategy achieves an average accuracy of about 35% lower than both subject-independent and hybrid strategies"。[V507]（arXiv 版）の逐語: "the forecasting performance, which we did not investigate here"、"should not be reduced to a naive comparison of AIC or BIC"。[V531] は抄録だけ: "we achieved lower prediction error in 33 of the 42 problem sets evaluated"。
3. **技術や手法の肝はどこ？** [V530] は学習者の初期値と学習の速さを正規の集団分布から引く階層ベイズ。[V531] は初期の習得の確率だけを学習者ごとにする。
4. **どうやって有効だと検証した？** [V530] は "3-fold item-stratified cross-validation"（項目で層化）で、同じ人の後の時点ではない。[V501] の数値は AdaBoost の第 1 群の実験の文。[V507] は予測を評価していない。
5. **議論はあるか？** 留保（[V531] に 1 票・頑健さ）: この時点では本文未読で、比べの相手と分割は不明だった（後で本文で照合: 相手は標準の知識追跡、分割は同じ問題セットの最後の問いの予測・末尾の「追加の照合」）。[V530] は前ラウンドのカード 3（[V387]・学習の速さの個人化が効く）と同じ系統の後継で、学習者の母数の重みが大きいことを過学習の可能性と並べて書く。[V501] は provisional から active に上げる。[V507] は雑誌版を今回も取れなかった（Springer が curl を拒む）。
6. **次に読むべき論文は？** [V531] の本文、[V507] の雑誌版。

### カード 7: HMM を 1 次のマルコフと比べた先例は、同じデータの中の比べならある **[検証済 2-1]** [V517] [V532]

1. **どんなもの？** アルコール依存の治療の試験で、日々の飲酒の列に HMM を当て、1 次のマルコフと比べた研究（[V517]）。活動認識で人ごとのモデルと人に依らないモデルを、人に依る評価と依らない評価の両方で比べた研究（[V532]・8 データ・4 学習器）。
2. **先行研究と比べてどこがすごい？** [V517] の逐語: "The first-order Markov model is nested within an HMM with M or more hidden states"、"The Markov model has a higher estimated effective number of parameters, pD, and also has a higher DIC, which is an estimate of a model's out of sample prediction error"、ただし "we ultimately don't rely on it as a formal model selection criterion"。[V532] の逐語（Europe PMC の全文）: "PSMs outperform PIMs by 43.5% in terms of their subject-dependent performances, whereas PIMs outperform PSMs by 55.9%"。
3. **技術や手法の肝はどこ？** [V517] は 1 次のマルコフを HMM の入れ子として比べる。[V532] は評価の分け方で勝ち負けが逆転することを同じ表で示す。
4. **どうやって有効だと検証した？** [V517] は DIC と事後予測の検査で、保持した後の時点の尤度ではない。1 人ごとのモデルでもない（集団の母数にランダム効果）。
5. **議論はあるか？** 留保（[V517] に 1 票・外への広げ）: 飲酒の日の列で、打鍵の 1 Hz の記号列ではない。前ラウンドの要点表の「人の行動の記号列で、HMM を 1 次のマルコフと予測の尤度で比べた研究: 判定不能（0 件）」は、「同じデータの中の比べ（DIC）は [V517] がある。保持した後の時点の予測の尤度で比べた研究は 0 件」と読み替える。論文 3 の C2 は [V517] を先例に挙げ、違いを「後の時点の予測で、本人の 1 次のマルコフと比べた」に限る。[V532] は前ラウンドのカード 1（評価の分割で効きが変わる）の補強。
6. **次に読むべき論文は？** 臨床の EMA で HMM と 1 次のマルコフを保持したデータで比べた研究（今回は EMA の検索が 1 回だけで、網羅が足りない）。


## 追加の照合（2026-11-07・本文を取れなかった 6 件と Garcés-Manzanera 2026）

前の照合で本文を取れなかった文献を、著者の個人のページ・研究室のサイト・保存版・オープンアクセスの雑誌版の順に探し直した（サブエージェント 2 本が探し、curl が拒まれたものはメインが Chrome で開いた。海賊版の置き場は使っていない）。どれもメインが本文の文字列で照合した。原本は repo に入れていない。

| 文献 | 取れた版 | 照合した内容 |
|---|---|---|
| [V510] Gauvain & Lee 1994 | 雑誌版の走査 PDF（国立台湾大学の音声の研究室のサイト・9 頁・OCR） | 逐語 "a Dirichlet density can be used for the initial probability vector π and for each row of the transition probability matrix A"。事前の母数は既知とするか、経験ベイズで "the prior parameters are estimated directly from data"。カード 1 の芯（話者に依らないモデルを中心にした Dirichlet を π と A の各行に置く）は雑誌版でも同じ |
| [V513] Reynolds ほか 2000 | CiteSeerX の全文（23 頁・誌名と頁つき） | 式 (14) の適応の係数 α = n / (n + r)、r は "a fixed relevance factor"。"The relevance factor is a way of controlling how much new data should be observed in a mixture before the new parameters begin replacing the old parameters"。[V514] の再掲と同じ形 |
| [V516] Altman 2007 | 著者の SFU の個人ページの改訂稿（10 頁・Internet Archive の 2017-08-09 の保存版・Chrome） | 逐語 "I define the models using the framework of generalized linear mixed models"。推定は尤度の直接の最大化（準ニュートン）で、変量効果の積分は数値積分か Monte Carlo EM。検証はシミュレーションと実データの例で、"predict" は本文に 0 回（予測の評価は無い） |
| [V520] Chung ほか 2013 | Gelman の個人ページの 25 頁の版（Psychometrika の 685–709 頁の組版） | カード 3 の抄録の逐語は 25 頁の版でも同じ |
| [V531] Pardos & Heffernan 2010 | Pardos の MIT の個人ページの全文（12 頁・Google Scholar の別の版から辿った） | 相手は標準の知識追跡で、"predicting student responses better than standard knowledge tracing in 33 out of the 42 problem sets"。分割は、各問題セットの最後の問いを除いた応答で当てはめ、最後の問いを予測する（同じ系列の中の予測で、同じ人の後のセッションではない） |
| [V507] Stoye ほか 2025 | 雑誌版（オープンアクセス・Version of record 2025-07-07・Chrome） | カード 6 の逐語 2 つ（"the forecasting performance, which we did not investigate here"・"should not be reduced to a naive comparison of AIC or BIC"）は雑誌版にもある。巻頁はまだ無い |
| [V534] Garcés-Manzanera 2026（新規） | 雑誌版（オープンアクセス・CC BY-NC 4.0・Chrome） | 第二言語の打鍵を 1 秒の窓にまとめ、対角共分散のガウスの HMM（K = 3）を "fitted separately to each writing session"（100 セッション）。"Markov chain"・"first-order"・"log-likelihood"・"cross-validat" は本文に 0 回で、1 次のマルコフとの比べと予測の尤度の評価は無い。"held-out" は推定に使わなかった特徴（文の境界など）の意味。K は BIC だけで決めず、K = 4 が全 100 セッションで BIC が低かったと書く |

還元: カード 1・3 の結論は変わらない。カード 6 の [V531] は、比べの相手が弱い（標準の知識追跡）同じ系列の中の予測で、論文 3 の「同じ構造の共通を相手に置き、同じ人の後のセッションで測る」とは評価の形が違う。カード 7 の「人の行動の記号列で HMM を 1 次のマルコフと保持した後の時点の予測で比べた研究: 0 件」は、打鍵の HMM の [V534] を加えても変わらない（[V534] は比べを持たない）。[V507]・[V510]・[V513]・[V516]・[V531] は provisional から active に上げた。

---

## 論文 3 への還元（外枠の C1〜C3・verdict の直す順 8）

- 3.3 の手法の文: 1 人ごとの MAP は「話者適応の MAP（[V510]・[V511]）を離散の記号列の HMM・AR(1)-HMM に当てたもの」と書く。多水準 HMM（[V515]）は関連研究に置き、「集団の分散を階層ベイズで推定する点が違う。τ は推定せず、他の人の予測で選ぶ」と 1 文で差を書く。「論文 3 の MAP は多水準 HMM の特殊な場合」とは書かない。
- C3: 「他の人で選ぶ」「同じ人の後の時点で測る」は入力の言語モデルの個人化の流儀（[V525]・[V526]・[V528]）で、新規性に数えない。C3 は「既出の原理と流儀を、系列のモデルの 1 人ごとの評価に当て、同じ構造の共通のモデルを相手に置き、格子に τ = ∞ を入れた組」と書く。τ = ∞ の向き（完全なプール）と、周辺尤度の境界推定（[V520]・[V521]）との違いを 1 文で書く。
- C1: 「共通の構造を良くすると上積みが消える」を直接測った研究は 0 件（[V526] の推測が最も近い）。効きが小さいが残る報告（[V525]〜[V529]）と、効きが小さい・大きな標本が要る報告（[V518]・[V530]）の間に置く。
- C2（根拠の段）: [V517] を先例に挙げ、違いを「保持した後の時点の予測で本人の 1 次のマルコフと比べた」に限る。
- 予測の対象の区別（[V522]・[V523]）を 3.4 に 1 文で書く。

## research-positioning.md への還元

還元しない。論文 3 は GSE の主張の根拠にしない（ADR-047 D2・D6、引き継ぎの「守ること」）。§3 / §4 は変えない。

## 否決リスト

- 「論文 3 の τ の MAP は多水準 HMM（Aarts & Haslbeck 2025）の特殊な場合」: 0-3 で否決。[V515] は多項ロジットの切片に正規・逆ウィシャートの集団分布を置き、集団の分散を推定する。共役の Dirichlet を共通の期待度数に中心化する形とは別物（上のカード 1・2）。
- 「Gauvain & Lee の Q → ∞ は τ → 0 に当たる」（サブエージェントの読み）: 0-3 で否決。Q は観測の列の数で、データが増えると ML に近づくという意味。
- 登録しなかった候補: Hard ほか 2018 arXiv:1811.03604（全体のモデルの連合学習で、個人化の評価ではない）、Do & Gatica-Perez 2013（書誌未確認・本文未読）、Meegahapola 2024 の博士論文（本文未読）、Ferrari ほか arXiv:2009.00268 と 2022 JRIE（本文未照合）、de Haan-Rietdijk ほか 2016（HMM ではなく閾値の自己回帰）、Morris 1983・Gelman & Hill 2007・Efron & Morris 1973（本文未読）。
