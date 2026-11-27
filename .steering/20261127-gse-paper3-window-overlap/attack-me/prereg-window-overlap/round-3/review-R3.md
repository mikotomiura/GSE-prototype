# 査読 R3 round 3（評価の偏りと個人への推論の方法論・paper-reviewer / opus）

## 1. 接地
- V-a Varma & Simon 2006 "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- V-b "The CV error estimate for the classifier with the optimal parameters was found to be a substantially biased estimate of the true error"
- V-c "Since the bias is caused by the variability in the estimates of prediction error for different values of the tuning parameters it is a general phenomenon."
- L-a Liu & Meng 2016 "if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."
- L-b "Creating reliable controls hinges on identifying the appropriate decomposition of the data into replicating subunits"
- L-c "With this greater descriptive power comes the danger that our pattern captures features of the observed pixels that do not generalize (artifacts)."

## carryover の判定
- M1: 解消（40・241・152 行）。同じ型の問題が R_ar3 の語に移った（M-A）
- M2: 位置は解消（54・167 行）。区間の広がりは限界 240 行だけで語と文に入っていない（M-B）
- M3・m1・m2・τ・m3・nit: 解消

## 2. 評価表
- a 3: 型 1 の「仕組みと合う形」は R_ar3 の語が床でほぼ決まること（M-A）と本人の当てはめが従属を運ばない既知の値（M-C）をかぶったまま Discussion へ。
- b 2: 列 C と A は区間の広がりと実効の情報量も違う。hmm3 と ar3 では τ の選びと目盛りが違う。
- c 3: 境の歩みと図はどの型でも使える。仕組みは「形」まで。
- d 3: 文が密。
- e 4: 1 人抜きで τ を当て直すかが無い（m-2）。
- f 3: 従属の強い列で数をそろえても実効の標本はそろわない点の位置づけが無い。
- g 4: 残る余地は φ の上限（m-1）と 1 人抜きの手順だけ。

## 3. 指摘
- [major] M-A R_ar3 の語「小さい」は R_ar3 の目盛りの床でほぼ決まる
  - 位置: 141 行「|stay_R(30)| < stay_G(30) / 4」・33 行（ジョイントの残り 5.8e-4 / 8.0e-4）・41 行・82 行
  - 理由: 歩み 1 ではジョイントが ar3 を 16 / 13 人に選び、ジョイントの残りが R_ar3 にほぼ重なる。R_ar3(A1) は開示の値から 1e-3 未満と見込め、41 行の「見ていない」と食い違う。本人 ar3 は τ で強く縮められ（main.tex 335 行 "0.06 to 3\% of the weight on the writer's data"）どの列でも 1e-3 程度に張りつくと見込める。stay_G(30)/4 は 1e-2 程度。仕組みと関係なく「小さい」になり型 1 がほぼ自動で出る。hmm3 と ar3 で τ が違い「構造を固定すると差が消える」と「ar3 の方が強く縮められる」を分けられない。V-b・L-a。
  - 解消: (1) R_ar3 の語を目盛りに依らない形（stay_R(30)/shrink_R(30) か A1 の値に対する比・G の φ と同じ形）にする、または (2) 構造の比べの主を τ = 10,000 の固定の行に移しデータの重みをそろえる。開示に「R_ar3(A1) はジョイントの残りから約 1e-3 未満と見込める」と書き 41 行を直す。可能なら「同じ程度」が出うる合成の組を P-READ に。
  - 自信: 高
- [major] M-B 列 C と列 A の差は区間の広がりと実効の情報量の差でもあるのに、語と文は「歩みに沿う」
  - 位置: 53・128・186・240 行
  - 理由: C30 は約 107 秒の連続した区間で、強く従属した 1 Hz の記号なので、同じ数でも実効の標本は小さくセッションの多様さも狭い。評価も 2 分ほどの区間。stay_G は歩みと広がり・実効の情報量の合計。C′ は位置だけ。型の名と Discussion の文に「歩み」だけが残る。型 3 の「記号の数に沿う」も数と広がりの合計。L-b。
  - 解消: 18 行と同じ形の規則を足す（「歩み（と、散った行か連続した区間か）」）。型 3 の名を「列 C でも同じ程度に縮む」のように列の名で。19 行の手順の全体の差に「区間の広がり・実効の情報量」を名で。列 C の区間の秒の長さの中央値を記述として出す。
  - 自信: 高
- [major] M-C 型 1 の Discussion の文は、既に支えられていないと分かっている環を書かない
  - 位置: 37 行（本人 hmm3 の残差の自己相関は共有と同じ程度）・241・186 行・main.tex 331 行 "a shared model whose structure misses that dependence makes a per-person fit look good"
  - 理由: 仕組みは「本人の当てはめが共有の運べない従属を運ぶので良く見える」環を含む。歩み 1 の本人 hmm3 は共有と同じ程度の自己相関を残し、この環は既知の値の上で支えられない。型 1 で「仕組みと合う形」だけを書けば過剰。
  - 解消: 型 1・2・2′ の文に固定の句「本人の当てはめが共有の運べない従属を運ぶかは、残差では支えられなかった（歩み 1 で本人と共有の自己相関が同じ程度）」を足すか、本人と共有の ρ_h の差を必ず添える句に。
  - 自信: 中
- [minor] m-1 φ に上限が無い（128・124 行）。φ ≫ 1 は G_C30 > G_A1 で歩みでは説明できず広がりの効き。shrink_G(30) は 0.059（k = 15）と小さく比は揺れやすい（V-c）。解消: 例 φ(30) > 1.5 で「列 C が列 A1 を超える」の別の語、P-READ に。開示に閾値を G の単位で（stay_G(30) が k = 5 で約 0.049、k = 15 で約 0.03 以上）。自信: 中
- [minor] m-2 1 人抜きが選びの段を繰り返すかが無い（110・109 行）。V-a。解消: 「中央値と語だけを取り直す（選びと当てはめは繰り返さない）」と明記し限界に。区間にも同じ注。自信: 中
- [minor] m-3 作りの確かめの M が短い列で偏る（97・223 行）。A30・C30 の組は数百ほどで 26 × 26 に Miller–Madow でも偏りが残る。陽性対照は 20,000 組だけ。解消: 判定 (i)・(ii) を M − M_shuf で取るか、実データの組の数の中央値と同じ規模の合成を P-MI に。自信: 中
- [nit] 区間の乱数 [SEED + 4, c, s] の s は冗長（害は無い）。自信: 高

## 4. 総合: major
- 固定の十分さは高く round 2 の 8 件はすべて手当てされた。
- 型を分ける R_ar3 の語が目盛りの床と τ の違いからほぼ決まり、型 1 が既知の値から見込める（M-A）。
- 列 C が歩みと区間の広がりを分けないのに語と文が「歩み」に帰す（M-B）。M-C は句の追加で済む。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: liumeng.txt 401 行以降・SEED・S13 conditions.md・tau-extend conditions.md・kit README・S13 scripts・main.tex の挙げた行以外・supplement.tex。SHA-256 は照らしていない。
- 注入の疑い: 無し。
