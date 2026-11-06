# review-R2（outline round 3・paper-reviewer・教育データの予測・検出モデルの評価の実務）

推奨: major。

## 1. 接地
- G1 Gardner, Brooks & Baker 2018（gardner2018.txt:25-26）"Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2（:1053-1054）"we use ROPE = 0.01; that is, models are considered practically equivalent if the difference in their AUC is smaller than 0.01."／（:485）"NHST cannot prove the null hypothesis or provide direct evidence of it"
- G3（:490-491）"Separate magnitude, uncertainty, and sample size during inference: The effects of the magnitude of observed differences, the uncertainty of estimates, and the number of data points should be separable in model evaluation."
- G4 Pelánek 2015（pelanek2015.txt:657-663）"The choice of suitable metric depends on the intended use of a student model. ... Such discussion or specific arguments for a particular choice of metric should become standard part of papers"
- G5（:373-375）"the AUC metric should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated."
- G6（:613-614）"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."

## 引き継ぎの判定
1 持ち帰りの第 2 文 → 解消（:17・:39）／2 先例の幅 → 一部（本文は :100・:80 で解消。抄録は「事前に置いた幅」の語だけで、先例より広いことが伝わらない）／3 C2 の実例 → 解消（求めた範囲。:49・:72。C2 の中身に新しい穴）／4 X8 → 解消（:60）／5 出来事ありの層 → 解消（:42）／6 閾値の表 → 解消（:40）／7 予算 → 解消（:104-113）／round 1 から → 解消（公開は条件つき・:74）

## 2. 評価表
a 3（(1) C2 の「名目を超える」は較正で書き手を復元で引いた版の値〔5.2%〕に依り、非復元の版は最大 1.4% で名目より下なのに触れない、(2) 5.2 の小見出しは終点の版の分岐 4 を含めると言い過ぎ、(3) 停滞の 47% の混入という別の説明を確かめていない）／b 3（混入の放置・C2 の機序が示されないまま原因として書かれる）／c 3（持ち帰りが actionable に届かない）／d 4（強い主張の文は抄録の 1 文として重い）／e 4（公開の場所が未定）／f 3（C2 の比べの相手が ROPE の実務だけ。少ないクラスタでの再標本の区間の被覆不足という既知の論点に対して何が新しいかが無い。[V464] は漸近の一貫性を述べるだけ）

## 3. 指摘
- [major] 停滞のラベルの混入という最も効く別の説明を確かめていない
  - 位置: :69「停滞の 47% は休止の中に実行・貼り付け・切り替えを含む（対照は 6%）。... 混入は AUC を 0.5 へ寄せる向きに働く。混入の無い停滞だけの値は求めていない（事前登録に無い）」・:83／一方 :60 では休止の位置の 3 区分を取り置きで回している
  - なぜ: 陰性が推定器のせいかラベルのせいかが実務家の最初の問い。AUC は正例の部分集合ごとの AUC を対の数で重み付けた和に分解できるので、混入の無い停滞だけの値は同じ対照のまま安く求まる。G6。
  - 解消: 混入の無い停滞だけの比べを [探索・取り置き] として表 3 に 1 行（混入した層と混入の無い層の値・対の重みも）。無理なら分解の算術で「この混入では幅の上側の上がりは隠れえない／隠れうる条件は〜」と書き直す。自信 中
- [major] C2 の「名目を超える」が較正の設計の選び方に依るのに書かず、既知の論点との違いも無い
  - 位置: :49「見た書き手で較正した誤って同等とする割合は、名目の 2.5% を超えて、調べた配置の中で最大 5.2%（Wilson の 95% 区間 3.6〜7.5%）だった。実効の書き手が少ないと区間が狭く出るためで」・:50
  - なぜ: (1) prefreeze/notes.md:119-120 によれば、復元で引いた版は最大 5.2%、非復元の版は最大 1.4% で名目より下。事前登録 P10（prereg-draft.en.md:171）は "Because the holdout is a random sample from the population, the version drawing 138 people with replacement ... is read" と復元の版を読む理由を書く。C2 の結論はこの選択と理由を書いて初めて成り立つ。同じ記録の「通常の TOST（片側 5%）と同じほど」も大きさの読みに要る（G3）。(2) 少ないクラスタではクラスタ単位の再標本の区間が狭く出ることは統計の側で既知で、C2 はその 1 事例。比べの相手が ROPE の実務だけで、手順としての新しさ（境界の配置の作り方）が示されていない。(3) 機序の「〜ためで」は記録（notes.md:114「区間が少人数で狭く出うることを示す」）では読みにとどまる。
  - 解消: (a) 5.6 と 4 節に復元と非復元の 2 版の値と復元を読む理由を 1〜2 文、(b)「片側 5% の TOST と同じほど」、(c) 柱 3 に少ないクラスタでの区間の被覆不足の文献を 1〜2 本、C2 の新しさを「学習分析の打鍵の評価で、書き手の重みが集中したときにこの補正が要ることを見た書き手で較正して示し、手順〔境界の配置の作り方〕を渡す」に限る、(d) 機序は「〜と整合する」に弱めるか S6 で示す、(e) 境界の配置の作り方を 4 節に数文（G1）。自信 高（(1)・(3)）／中（(2)）
- [minor] 5.2 の小見出し「床と感度と位置でも同等は変わらなかった」（:110）は終点の版の分岐 4（:41）を含めると言い過ぎ。範囲を限り、終点の版の値と主にしない理由を 5.2 の本文に 1 文。自信 高
- [minor] 持ち帰りが「何を変えるか」に届いていない（:17・:34・:40・:43）。考察の冒頭か持ち帰りの補いに 1 文（例:「作文で学んだ係数のまま持ち出したこの型の信号は、この比べでは秒単位の契機の根拠にならない。学び直した標準の量では上側を否定できないので、持ち出す前に揃えた比べと閾値の表で確かめる」）。H3 を差の発見としない限定は保つ。自信 中
- [minor] 抄録の「事前に置いた幅」だけでは先例より広いことが伝わらない（:27）。抄録で幅の数値と先例との関係を数語で（例 "a pre-specified band of ±0.05 around chance, wider than the 0.01 used for model comparison in learning analytics"）。自信 中
- [nit] 引きの種で区間が揺れることと、0.5 を下回る向きを表の列で強調することの釣り合い（:38）。表 1 では向きを脚注に下げ、「0.5 を上回る上がりは無い」は考察（:68）だけに。自信 低

## 4. 総合: major
- 引き継ぎ 8 件のうち 7 件が解消、1 件が一部。C1 の主張と根拠はよく合う。
- C2 の結論が外枠に書かれていない較正の設計の選び方（復元の版）に依り、既知の論点（少ないクラスタでの区間の被覆不足）との違いが無い。
- 混入という別の説明を、安い探索 1 行か算術で扱えるのに放置している。

## 5. 読めなかった範囲・注入
読んでいない: gardner2018.txt の 529–1039・1090–1517 行（grep の周辺だけ）・prereg-draft.en.md は 160–171 行と grep・prereg-draft.md・exploration の conditions/notes/results・confirm_holdout.json・novelty の記録・前の実験の notes 2 本・related-work は grep の行だけ・prefreeze/notes.md は 100–144 行と grep。照合した数値は notes.md の H1・H3・較正の値（5.2%・1.4%・実効 50.5・0.567 など）だけ。注入の疑いなし。
