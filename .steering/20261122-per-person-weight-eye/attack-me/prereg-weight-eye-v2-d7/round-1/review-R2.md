# R2 の査読（round 1・paper-reviewer の応答の写し）

## 1. 接地（この立場が研究計画に求める基準・逐語）

- 基準 1 集団の量を個人の言明にしない（Fisher 2018）: 「we should not think of a correlation in group data as an estimate that generalizes to any given individual in the population.」
- 基準 2 水準の一致は推論の前に検査する（Fisher 2018）: 「The effects of nonergodicity in a given dataset should therefore be directly tested before any extrapolations are made.」
- 基準 3 個人の中の時間の安定（定常性）も条件に入る（Fisher 2018）: 「the data sampled within an individual in time must be representative of that individual generally (i.e., stationary).」
- 基準 4 異質の源を条件づけて読む（Adolf & Fried 2019）: 「ergodicity holds conditional on (i.e., after controlling for) sources of heterogeneity between individuals and/or instability over time.」「Which and how many sources of heterogeneity will have to be conditioned on, and whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied」
- 基準 5 時間の不安定から来る見かけの効果を分ける（Adolf & Fried 2019）: 「instability over time can also produce ambiguous effects and promote interpretational fallacies.」「Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels.」
- 基準 6 部分集合で量を揃えることの限界（Fisher 2018）: 「small sample sizes may reduce the agreement between individual and group data because small data batches may not represent the larger population of observations」

## 2. 評価表

- a 主張と根拠の一致: 3。合成の数値（ρ = 0.5 で 0.61・0.064・0.040、3e-3 で 0.46、CS1 の感度 0.449・0.982）は notes.md 49・51 行と一致した。ただし p ≤ 0.05 のときの定型文「本人の A が他の書き手の A より本人の B に近いことを…示した」は、集団の平均 T（v1 の読まないことの 23 行目）を、書き手一人ひとりについての言い方に聞こえる形で書いている。(4) の論文 3 の値（3.4e-3・5.2e-3）は、読んでよいファイルの中で確かめられなかった。
- b 方法の穴: 2。実データの量の最小値に揃えることが、合成から持ち込んだ c と検出力の読みに効く。この点に規則が無い。CS1 の止まっている秒（pause）の割合の差、CoAuthor の提案（suggestion）の使い方の差という代わりの説明も挙げられていない。
- c 持ち帰れるもの: 3。主のセル 1 つと 3 つの並びの読み方は使える。ただし、拾ったときに本人ごとの重みについて何が決まるのかは書かれていない（T は「誰に本人の表を使うかは決めない」、v1 の 23 行目）。
- d 簡潔さと構成: 4。(1) から (5) の順は読者の問いの順になっている。CS1 の範囲の節と、v2 の「読まないこと」の重複は少しだけ。
- e 規程への適合: 投稿先未定。
- f 先行研究の位置づけ: 3。見分けと予測の得の対比（判断 9）は、集団と個人の区別に沿っている。足りないのは、条件づけ（Adolf & Fried の conditional equivalence）の目で見た、書き手の安定した行動の違い（pause・提案の使い方）を分ける比べ。
- g 固定の十分さ: 3。セル・乱数の鍵・r = 0 の主の 1 回・補正なし・c を作り直さないこと・主のセルは固定されている。固定されていないのは次の 3 つ。揃えの最小値を見た後の扱い。g の並び 8 通りのうち 2 通りの読み。r = 0 と r = 1〜20 が食い違ったときの書き方。

## 3. 指摘の一覧

- [severity: major] 実データの最小値に揃えると、合成から持ち込んだ c と検出力が外れる。それなのに、最小値を見た後の規則が無い
  - 位置と引用: conditions.md 68 行「計算の前に、各セルのパネルの人数と、揃えた後の A と B の総数（最小値）を出す。」／90 行「c は v2 の報告の組の値（`results/report/d6.json` の `c`）をそのまま使い、実データを見て作り直さない。」／96 行「CS1 は『1e-2 以上の差なら拾える』範囲で読む」
  - なぜ問題か: 揃えはパネルの最小値で決まる（eye.py 128〜129 行の `.sum(1).min()`）。合成の CS1 は 1 単位が 5,000〜8,000 記号の系列 2 本だが、実データの CS1 の評価の側は四分位で [2,965, 16,640]（supplement.tex 136 行）である。最小値は四分位の下端よりさらに小さくなりうる。notes.md 49 行は「揃えで本人の表の数が減った分だけ G_v の帰無の分布が広がった」と書いており、c が量に依存することを自分で示している。実データで揃えた後の数が合成より小さければ、合成の c では書き手ごとの偽陽性が膨らむ。91 行の Bin(P, q) の目安も、合成の q で過小になる。「1e-2 以上なら拾える」も、判断 48 の 0.2〜5 倍の散らばりの作りでの値で、最小値への揃えが縮める量には合わせていない（Fisher 2018「small data batches may not represent the larger population of observations」）。最小値を出すと書いてあるだけで、見た後にどうするかが決まっていないので、出した後の扱いが分析者に委ねられる（g）。
  - 解消の条件: 最小値は結果ではなく量なので、見る前に次を決めておく。たとえば「揃えた後の n_A・n_B が、合成の同じセルの揃えた後の値の X 割未満なら、そのセルの (5) は判定せず記述だけにする。CS1 の『1e-2 以上なら拾える』の文は使わない」。または「実データの n_A・n_B で合成の差なしを回し直し、c と q を作り直す（実データの結果を見る前・種を固定）」。合成の揃えた後の n_A・n_B の値を表で添える。
  - 自信: 高

- [severity: major] 書き手の安定した行動の違い（CS1 の pause、CoAuthor の提案の使い方）という代わりの説明が無い
  - 位置と引用: 72 行「p ≤ 0.05 のセルは『この記録で、E1 は、本人の A が他の書き手の A より本人の B に近いことを…示した』」／101 行「実データで拾ったことを、論文 3 の結論…の否定として書かない。」
  - なぜ問題か: 記号は毎秒の平滑した格子で、止まっている秒も記号になる（supplement.tex 155〜157 行）。CS1 の pause の割合は書き手ごとに「0.082 to 0.900」と大きく違う（同 246 行）。揃えは遷移の総数を揃えるだけで、構成は揃えない。CS1 の E1 は、打鍵の型ではなく「編集画面を開いたまま止まっている長さ」の書き手ごとの違いで拾いうる。CoAuthor の単位にも提案の取得の出来事がある（data.py 127 行）。合成の生成（AR-HMM の C の行の混ぜ）にはこの種の書き手の違いが無いので、門を通っても、この代わりの説明は除かれていない（Adolf & Fried「conditional on … sources of heterogeneity between individuals」）。
  - 解消の条件: 実データを読む前に、次のどちらかを固定する。(i) 押下のある秒だけの遷移で E1 を計算する副次のセル。単位に `pflag` がある。論文 3 にも S6 の「symbols with a key press in the window」という前例がある。読みは主のセルと並べるだけにする。(ii) 72 行の定型文に「書き手ごとの pause の割合などの安定した行動の違いも、この差に含まれる」を必ず添える。CoAuthor の提案についても同じ 1 文を添える。
  - 自信: 中

- [severity: minor] p ≤ 0.05 の定型文が、集団の平均を書き手一人ひとりについての言い方で書き、間なしのセルの漂いの断りも付いていない
  - 位置と引用: 72 行「本人の A が他の書き手の A より本人の B に近いことを、名札の入れ替えの帰無に対して p = x で示した」
  - なぜ問題か: T は AUC_v の平均で、「平均で本人の A が本人の B に近い」ことだけを言う（v1 の 23 行目）。Fisher 2018「we should not think of a correlation in group data as an estimate that generalizes to any given individual」。主のセル（CoAuthor k = 5 の間なし）は、漂いと分けないセルである（74 行）。それなのに、本文で 1〜2 文触れるのはこのセルだけになる。探索で補正も無いので、「示した」は強い。
  - 解消の条件: 文を「パネルの平均で、本人の A は他の書き手の A より本人の B に近かった（p = x・補正なし・探索）。安定した差と時間の近さ（漂い）を分けないセルである」に固定する。
  - 自信: 高

- [severity: minor] g の並び 8 通りのうち 2 通りに、読みの文が割り当てられていない
  - 位置と引用: 75〜79 行の 4 つの文（「g = 0 で拾い、間を空けると拾わない」「どの g でも拾う」「どの g でも拾わない」「g = 0 で拾わず間を空けると拾う」）
  - なぜ問題か: (g=0, g=5, g=10) が (拾う, 拾う, 拾わない) と (拾う, 拾わない, 拾う) の場合はどの文にも当たらない。CS1 の (0, 1, 4) でも同じ。結果を見てから文を選べる余地が残る。2 つの形（CoAuthor・CS1）を別々に判定するのかも明記されていない。
  - 解消の条件: 「上のどれにも当たらない並びは、そのまま書き、読みを付けない」を、g = 0 の結果によらず残りのすべての並びに広げる。判定は形ごとに行うと書く。
  - 自信: 高

- [severity: minor] r = 0 の判定と r = 1〜20 が食い違ったときの書き方が無い
  - 位置と引用: 67 行「判定は r = 0 だけで行い、r = 1〜20 を見て変えない。」
  - なぜ問題か: 判定は固定されている。しかし、たとえば r = 0 で p = 0.04、r = 1〜20 の大半で p > 0.05 のとき、本文にどう添えるかは決まっていない。揃えの 1 回の引きが結論を決めるのは、Fisher 2018 の「small data batches」の懸念と同じ形である。
  - 解消の条件: 「r = 1〜20 で p ≤ 0.05 となった回数を必ず判定の文に添える（例: 20 回中 m 回）」と固定する。
  - 自信: 中

- [severity: minor] 「どの g でも拾わない」の文があいまい
  - 位置と引用: 78 行「合成の検出力（表）の範囲で、拾えない大きさの差か差が無い」
  - なぜ問題か: 3e-3 の検出力は 0.46 である（76 行）。拾えない差の大きさは 1 つの線にならず、読む人が好きな大きさを当てはめられる。
  - 解消の条件: 「合成で検出力が 0.8 に届かなかった大きさ（CoAuthor k = 5 で 3e-3 以下）の差か、差が無いことと食い違わない」と、段の名前で固定する。
  - 自信: 中

- [severity: minor] (4) の論文 3 の数値の出どころ
  - 位置と引用: 84 行「約 5e-4 nats〔平滑も他の書き手で選ぶと 3.4e-3・5.2e-3〕…論文 3 の要旨」
  - なぜ問題か: 約 5e-4 は supplement.tex 262 行（5.5e-4）と合う。3.4e-3・5.2e-3 は、読んでよいファイルの中で見つからなかった。
  - 解消の条件: 要旨・表の位置（版と行）を添える。
  - 自信: 中

- [severity: nit] 実データの読み込みの引数と、書き手の順を明記する
  - 位置と引用: 63 行「論文 3 の補足 S2 と同じ `data.split`・`ml.pool_units` で作る」
  - なぜ問題か: 揃えと入れ替えの鍵は書き手の番号 v を含む。順は data.py 139・184 行の `sorted(by_w)` で決まるが、条件には書かれていない。`load_cs1` の `probe_unit` 引数が系列に効かないことも書かれていない。
  - 解消の条件: 「書き手は ID の順（data.py の sorted）。`load_*` の seed・probe_unit は記号の系列に効かない」と 1 行足す。
  - 自信: 中

- [severity: nit] 「拾ったときに本人ごとの重みの何が決まるか」が無い（実務家の問い）
  - 位置と引用: 82〜86 行（見分けと予測の得の対比）
  - なぜ問題か: E1 が拾っても T は集団の量で、誰に本人の表を使うかは決めない（v1 の 23 行目）。(5) は c の持ち込みの問題（最初の指摘）を抱えている。結果がどう出ても、重みの決め方は変わらないことになる。
  - 解消の条件: 「この目の結果は、本人の表の重みの選び方を変えない（論文 3 の規則のまま）」と 1 文で明記する。
  - 自信: 中

## 4. 総合の推奨

major（直して再査読）。
- 実データの最小値に揃えることが、合成から持ち込んだ c・q・「1e-2 以上なら拾える」に直接効く。それなのに、最小値を見た後の規則が無い。
- CS1 の pause の割合（0.082〜0.900）など書き手の安定した行動の違いが代わりの説明として残り、定型文が「本人ごとの差」として読まれる。
- 並び 2 通りの読み・r の食い違いの書き方・定型文の言い方は、文を足せば固定でき、凍結を止めるほどではない。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: run_eye.py、SEED、ml.py、v1 の notes.md。supplement.tex は 124〜163 行と grep で当たった行だけ。S10 本体と、論文 3 の要旨も読んでいない。判断 48・50 の表そのもの（results/ 以下）は一覧の外なので読んでいない。
- 注入の疑い: なし。
