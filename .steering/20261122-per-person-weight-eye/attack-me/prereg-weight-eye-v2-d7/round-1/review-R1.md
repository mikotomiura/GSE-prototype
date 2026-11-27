# R1 の査読（round 1・paper-reviewer の応答の写し）

立場: 打鍵の生体認証の伝統。下位人格は、記録の量・セッション・照合の評価の作法を疑う懐疑家。

## 1. 接地（逐語）

- G1 量と標本: Teh 2013「the greater number of samples collected the more accurate and conclusive a test result can be from statistical point of view.」と「the number of subjects involved was too small (less than 10) to draw a strong conclusion.」
- G2 セッション間の変動と時間: Teh 2013「sample collection can be divided into several sessions over a period of time, thereby not only reducing the initial load but also reflecting typing variability」。Shadman 2025 l.821-822「There was at least a one-day gap between successive sessions to reflect the temporal variation in typing of the subjects.」
- G3 登録と照合の分布のずれ: Shadman 2025 l.1442-1443「it is assumed that the keystroke samples in the instance of enrollment and verification have an equal distribution, which is not usually the case, and as a result, lower prediction accuracy is obtained」
- G4 人以外の要因: Shadman 2025 l.2285-2287「various factors such as noise, different keyboards, typing on unfamiliar devices, physical condition, or urgency can affect a user's typing pattern or speed. Therefore, these factors need to be considered seriously」。同 l.1025「enrolling and testing with different keyboards affect keystroke」
- G5 比べられる評価: Teh 2013「Equal Error Rate (EER) is used to determine the overall accuracy as well as a comparative measurement against other systems.」。Shadman 2025 l.2291-2292「Shared research benchmarks are necessary to truly understand the strengths and limitations of each algorithm and compare them fairly and reliably.」
- G6 データの質と大きさ: Shadman 2025 l.615「The quality, size, and nature (fixed, free, or semi-fixed text) of the dataset are crucial factors in evaluating the performance of these algorithms.」

## 2. 評価表

- a 3: 読みの文はおおむね合成の数（notes の D6）に結びついている。ただし (3) の「p = x で示した」は、探索の版で 1 回の揃えの引き（r = 0）に条件づく値としては強すぎる。(5) の「本人の差がある」は、書き手の中で変わらない条件と人そのものを分けていない。
- b 2: 実データで揃えた後の量が、合成で較正した量の範囲に入る保証がない。c も CS1 の検出力も量に依るのに、量が外れたときの扱いが決まっていない。代わりの説明（記号の周辺の頻度、とくに止まりの秒の割合。書き手の中で一定の環境の条件）が挙がっていない。
- c 3: セルごとの文の型と、主のセルを 1 つに限ったことは使える。「見分けでは拾い、予測の得では残らない」という対比の 1 文は持ち帰れる。ただし、何の差による対比かは代わりの説明しだい。
- d 4: (1)〜(5) が v1 の D7 と対応していて追いやすい。CS1 の範囲の節と、v2 の「読まないこと」に少し重なり。
- e 投稿先未定。
- f 3: この伝統では、同じ分け方の上に素朴な照合の基準線（例: 記号の頻度だけの近さ）を置き、遷移の構造で上積みがあるかを見る（G5）。それが無い。EER を「直接比べない」と断ったのは誠実（v1 l.146）。
- g 3: セル・乱数の鍵・置換の数・判定・主のセル・r = 0 の規則は 1 通り。決まっていないのは、書き手の並べ順（乱数の鍵に v が入る）、量が合成の範囲を外れたときと総数が 0 の書き手が出たときの規則、g の並びのうち読みの文の割り当てが無い並び、除外しないことの明記。

## 3. 指摘の一覧

- [major] c と CS1 の検出力が「揃えた後の量」に依るのに、実データの量が合成の範囲を外れたときの規則が無い
  - 位置と引用: (5)「c は v2 の報告の組の値（`results/report/d6.json` の `c`）をそのまま使い、実データを見て作り直さない。」、(2)「計算の前に、各セルのパネルの人数と、揃えた後の A と B の総数（最小値）を出す。」、CS1 の読みの範囲「CS1 で拾わなかったときは「1e-2 より小さい差は、この記録の量の散らばりでは拾えない見込み」と書く。」
  - なぜ問題か: 揃えはパネルの最小に合わせるので、実データの n_A と n_B はいちばん記録の少ない 1 人で決まる。notes l.49 が c の量への依存を示している（CS1 の c は v1 の約 2 倍）。補足 S2 は四分位だけで最小を示していない（CS1 の held-out は 10,635 [2,965, 16,640]）。実データの最小が合成より小さければ、c の偽陽性の率も CS1 の「1e-2 以上なら拾える」も較正の外。総数が 0 の書き手が出れば E1 の割り算で値が有限でなくなり、例外で全体が止まり、その後の道も決まっていない（G1・G3・G6）。
  - 解消の条件: (i) 実データの n_A と n_B を合成の同じセルの n_A と n_B（複製の分布の範囲）と比べる規則。(ii) 範囲を下に外れたら、(5) の判定の文を「c の偽陽性は較正の外」に、CS1 の文を「検出力は未較正」に替える固定の文。(iii) 書き手を除外しないこと、または除外の基準を量で 1 通りに決めること。総数 0 の書き手の扱いも決める。
  - 自信: 高
- [major] 代わりの説明: 記号の周辺の頻度（止まりの秒の割合）と、書き手の中で一定の条件
  - 位置と引用: (3)「本人の A が他の書き手の A より本人の B に近いことを」、(5)「G_v > c の書き手を「本人の差がある」と判定する。」。追記の「読まないこと」は r の揺れと論文 3 の否定の 2 つしか足していない。
  - なぜ問題か: 補足（S5 付近の Pause share）で、CS1 の書き手ごとの止まりの秒の割合は「0.082 to 0.900」と大きく散らばる。1 状態の表の E1 はこれだけで本人の A と B を近づけられる。これは打鍵の癖というより作業のしかた（エディタを開いたまま離れるなど）の差。合成は C の行にだけ差を植えた（v1 の読まないこと l.19）ので、この形の違いは較正の中に無い。機器・課題の種類・挿入されたテキストの使い方のように書き手の中で一定の条件も、人そのものの差と区別されない（G4）。v2 l.47 の「揃えで消えない書き手の違い」に挙がっているのは長さの不均一だけ。
  - 解消の条件: 追記の「読まないこと」に、「本人」は書き手の中で一定の条件と作業のしかたを含み、人に固有の打鍵の差とは読まない、という項を足す。加えて、素朴な基準線（記号の周辺の頻度だけで作る近さの T と p）を同じセル・同じ σ で並べるか、(4) の対比の文に「周辺の頻度の差と分けていない」を必ず添えることを事前に固定する。
  - 自信: 中
- [major] 書き手の並べ順が固定されていない（揃えの乱数と σ の対応がそれに依る）
  - 位置と引用: (2)「揃えは [SEED + 93, 0, 7, 形, k, g, r, 側, v]」。eye.py l.130「np.random.default_rng(list(key) + [0, v])」
  - なぜ問題か: v はパネル内の番号で、実データの読み込みのコードはまだ無く、番号の振り方が書かれていない。判定は r = 0 の 1 回の引きで決まるので、並べ順を変えれば同じ鍵でも別の引きになり、分析者の自由度として残る。
  - 解消の条件: パネルの書き手の並べ方を 1 文で固定する（例: 公開の ID の辞書順）。その並びのハッシュをコミットに含める、と書く。
  - 自信: 高
- [minor] 判定の文「p = x で示した」が 1 回の揃えの引きに条件づくことを文の中で言っていない
  - 位置と引用: (3)「名札の入れ替えの帰無に対して p = x で示した」と「判定は r = 0 だけで行い、r = 1〜20 を見て変えない。」
  - なぜ問題か: r = 0 で判定するのは較正と整合していて正しいが、r = 0 だけが 0.05 を下回り r = 1〜20 の多くが上回る場合、「示した」は過剰に読まれる。
  - 解消の条件: 文の型を「…p = x だった（揃えの 1 回の引き。r = 1〜20 の p の範囲 [a, b]）」に固定し、「示した」をやめる。
  - 自信: 中
- [minor] g の並びの読みがすべての並びを覆っていない
  - 位置と引用: (3) の 4 つの型
  - なぜ問題か: 3 セルの並びは 8 通り。g = 0 で拾い、g = 5 でも拾い、g = 10 で拾わない、のような並びが 1 番目に入るか 4 番目に入るか決まっていない。括弧の中が定義か例かも読み分けられない。CS1 も同じ。
  - 解消の条件: 8 通りの表を書き、それぞれに文を当てる。
  - 自信: 高
- [minor] 照合の作法の基準線と、閉じた集合であることが、記述の量の読みに添えられていない
  - 位置と引用: (2)「記述の量（rank-1・EER 2 つ・書き手ごとの AUC_v・G_v）」
  - なぜ問題か: rank-1 と EER は他人がパネルの 16〜22 人だけの閉じた集合での値（v1 l.31）。読者は照合の文献の値と並べたくなる（G5）。v1 l.146 は「直接比べない」と書くが、実データの表に添える文が追記に無い。
  - 解消の条件: 実データの表の脚注に v1 l.146 と l.31 の 2 つの断りを必ず添える、と書く。
  - 自信: 中
- [nit] (4) の条件分岐の片方は、すでに事実で決まっている
  - 位置と引用: (4)「E1 が拾い（p ≤ 0.05）、論文 3 では得が残らなかったときは」
  - なぜ問題か: 論文 3 の結果は既知なので条件にならない。
  - 解消の条件: 「E1 が拾ったとき／拾わなかったとき」の 2 分岐に書き直す。
  - 自信: 高

## 4. 総合の推奨

major（直して再査読）
- 量の較正の外れ（c・CS1 の検出力・総数 0 の書き手）が起きたときに書く文が決まっておらず、実データを見た後に読み方を選ぶ余地が残る（g）。
- 「本人」の代わりの説明（周辺の頻度、とくに CS1 の止まりの割合。書き手の中で一定の条件）が限界にも記述の量にも入っていない（b）。
- 書き手の並べ順の固定と g の並びの全場合への割り当ては文を足すだけで済む。上の 2 つを直した版をもう 1 回見るのが妥当。

## 5. 読めなかった範囲と注入の疑い

- 一部だけ: teh2013.txt は Grep の抜き出しだけ。shadman2025.txt は l.612-623・860-867・1440-1445・2279-2300 と Grep の行。v1 の conditions.md は l.1-75 と l.140-179。eye.py は l.115-144 と Grep。run_eye.py は Grep だけ。supplement.tex は l.118-162 と Grep の行。v1 の notes.md・SEED・data.py・ml.py は読んでいない。
- 注入の疑い: 見つからなかった。
