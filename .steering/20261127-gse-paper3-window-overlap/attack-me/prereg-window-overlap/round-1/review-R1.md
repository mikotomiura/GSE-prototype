# 査読 R1（行動の記号列の系列モデルの方法論・paper-reviewer / opus）
stage: prereg。対象: experiments/20261127-window-overlap-dose/conditions.md

## 1. 接地
- G1 Pohle 2017（949–952 行）"the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions (Markov property and/or conditional independence assumption)."
- G2 Pohle 2017（93–94 行）"how additional states in an HMM can capture neglected structure in the data, leading standard information criteria to often overestimate the true number of hidden states"・（990–991 行）"the additional states merely mop up some structure missing in the model"
- G3 Singer 2014（295–301 行）"Using the log-likelihoods of the specific order models is not enough, as we will always get a better fit to our training data using higher order Markov chains ... the number of parameters increases exponentially with k which may result in overfitting"・（89–92 行）"It is difficult to make plausible statements about the appropriate Markov chain order having insufficient data but a vast amount of states"
- G4 Monaco & Tappert 2018（779–786 行）"It is important for statistical models and their implementations to be consistent ... consistency of the POHMM implementation under several different scenarios is validated in this section using computational methods."・（814–816 行）"scenario 4 simply demonstrates the inability of the HMM to capture the dependence on event types, and results should indicate biased estimates."
- G5 Singer 2014（91–92 行）"All evaluation approaches would favor a zero or first order because the number of parameters grows exponentially with the chain order and the available data is too sparse"

## 2. 評価表
- a 2: 型 1 の「強い比べの残りは沿わなかった」が R の「減る」「定まらない」にも当たる。R は歩みで比べる構造が替わる（u で ar3・n で hmm3）。D に r1 の本人らしさ。共変を媒介として持ち込む。
- b 2: 重なりか量かの交絡を外す列（重なりを保って量を減らす列）が無い。τ を歩みごとに選ぶので N/(N+τ) はそろわない。読みの規則が仕組みを当てられるかの陽性・陰性の対照が無い。
- c 3: 用量の段と列 B は S13 から一歩進むが、どの型でも仕組みについて言えることが弱い。
- d 3: 3 文書を読む必要。D5 の優先順位が無い所。
- e 4: 固定・乱数・端の門・変異はそろう。機械をまたいだ門が外れたときの次の手が無い。実データの位相の欠けを数える門が無い。
- f 3: Pohle の G5 の当て方が向きの読み違え。残差（model check）を運べない従属の確かめに使っていない。
- g 3: m = 0 の語の優先・構造の選びの語が平らでも当たる・307 行の位置・「大きく超える」と「止めて原因を調べる」の後が未定。

## 3. 指摘
- [major] 量の交絡を外す列が無く、問いの動機に答えられない
  - 位置: 7 行「縮みが重なりによるのか量によるのかを分けられない」・29 行「どちらも単独では交絡を外さない」
  - 理由: 列 A は重なりと量が一緒に動き、列 B は重複で数を保つだけ。Singer "having insufficient data but a vast amount of states"。重なりを 29/30 に保ち量だけを列 A の s に合わせる列（u の各セッションの連続した先頭 1/s・またはセッションの間引き）で、列 A(s) と列 C(s) の比べが作れる。
  - 解消: 列 C を足し、A と C の差を量をそろえた重なりの効きとして読む型を事前に決める。足さないなら問いを「歩みと記号の数を同時に変えたときの形の記述」に狭め、7 行の動機と型 1 の語を外す。
  - 自信: 高
- [major] R は比べる構造が入れ替わり、型 1 の「残りは沿わなかった」と合わない
  - 位置: 70・98・111 行・S13 notes 88 行
  - 理由: s = 30 で R ≈ G、s = 1 で R ≈ 6e−4。構造の入れ替わりで「減る」になりやすく、それでも型 1 を満たし「沿わなかった」と書かれる。Pohle の G2。
  - 解消: (i) 構造を固定した強い比べ（本人 ar3（τ 他人）− 共有 ar3・D3 の行にある）を主の R に、ジョイントの R は記述に。(ii) 型 1 の R の条件を「沿わない」に限り、「減る」「定まらない」に別の型と書き方。(iii) 歩みごとの選ばれた構造の人数を R の読みの前提に。
  - 自信: 高
- [major] D に r1 の本人らしさとデータの量の効きが混ざる
  - 位置: 73 行
  - 理由: D = (r1 − 共有 ar1) + (共有 ar1 − 共有 hmm3)。前の項は本人らしさと量に依る平滑の効き（Singer G3・G5）。S13 の n で C2a が逆になったのも区別できない。
  - 解消: 主の D を共有どうしの差（共有 ar1 − 共有 hmm3、または共有 ar3 − 共有 hmm3）にし、r1 − 共有 hmm3 は副に。または名を「本人の連鎖に負ける量」に変える。
  - 自信: 高
- [major] 操作の門（M）が運べない従属を確かめていない。残差は読みに使わない
  - 位置: 74・76・96 行
  - 理由: M は作り上ほぼ確実に減り、門としてほとんど落ちない。M は記号の従属でモデルが運べない従属ではない（Pohle G1）。M は k に依らず「2 セルで同じ語」が 2 回の確かめにならない。
  - 解消: 共有 hmm3 の擬似残差の遅れ 1（zx・zy）を第 2 の門か仕組みの量に入れ語を決める。M は「作りの確かめ」と呼び直し、k に依らないと書く。
  - 自信: 中
- [major] 読みの規則が仕組みを当てられるかの模擬（陽性・陰性）が無い
  - 位置: V2 表・146 行
  - 理由: 対照は配管だけ。仕組みが無くても量と構造の入れ替わりだけで型 1 が出うる。Monaco & Tappert "scenario 4 ... results should indicate biased estimates"。
  - 解消: 合成で (i) 書き手の差が無く重なりの従属だけの世界、(ii) 書き手の差があり重なりの無い世界を作り、型が (i) で型 1、(ii) で型 3 か「沿わない」を返すことを門に。重すぎるなら限界に書き型 1 の語を弱める。
  - 自信: 中
- [major] 開示が端の知識を少なく見積もる
  - 位置: 20・21 行
  - 理由: (i) 列 B の s = 1 は u で m は Q(1) を使う (ii) 列 B の s = 30 の位相 0 は n、他の 29 位相はほぼ同じ写し (iii) D の端は既知の G と C2a から出る（u ≈ 0.70・n ≈ −0.26）、R の端の符号も既知の選ばれた構造からほぼ決まる。
  - 解消: (i)〜(iii) を書き、既知の端から型がどこまで予想できるかを予想として凍結し、予想と実際を並べる。
  - 自信: 高
- [minor] τ を歩みごとに選ぶので N/(N+τ) はそろわない（29・69 行・notes 89 行）。解消: 29 行を直し、τ 固定の行（例 10^4・10^5）の G を副に、選ばれた τ の人数を歩みごとに。自信: 高
- [minor] Pohle の G5 を当てる向きが合っていない（107 行）。従属が強いとき ar が選ばれるのは指定がデータに合う向きで、埋め合わせとは違う。解消: 文を外すか「選びはデータの構造に従った（埋め合わせとは別の現象）」と書く。自信: 中
- [minor] 構造の選びの語が平らでも当たる。m = 0 の語の優先が無い。ここだけ「4 組すべて」（106・88・90 行）。解消: 端の差の条件（例 割合(1) − 割合(30) ≥ 0.5）・判定の順（m = 0 → 沿わない → 増える/減る → 定まらない）・P-READ に入れる。自信: 高
- [minor] 機械をまたいだ門が外れたときの道が無い（120・130 行）。解消: 次の手を 1 つ（例 HP Z2 で回し直す・許容は変えない）、Mac の numpy の版を事前に。自信: 中
- [minor] 実データで位相の行の欠けを数える門が無い（44・139 行）。解消: 位相を合わせた行の数が t − t0 ≥ 1,000·s の行の数と一致することを V1 に。自信: 中
- [minor] 型 1 の持ち込みで共変を仕組みとして貢献に上げる（111 行）。解消: 「仕組みと合う形を測った」に弱めるか、書き手ごと・歩みごとの D と G の対応を足す。自信: 中
- [nit] 307 行の位置がファイルと合わない（今の main.tex 331 行）。解消: 節の名と逐語で。自信: 高
- [nit] 「大きく超える」に数が無い（119 行）。自信: 高
- [nit] 切れ端（900 記号）の効きが歩みで変わる（54・43 行）。解消: 限界に 1 文。自信: 低

## 4. 総合: major
- 問いの動機（重なりか量か）を外す列が無いのに、型 1 の語は「仕組みが測れた」。
- R は構造が入れ替わり、D は r1 の本人らしさを含む。既知の端から型がある程度予想できる。
- 量の定義の差し替え・量をそろえた列か問いを狭める選択・開示の書き足しで再査読に耐える。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: monaco.txt 1117 行以降・pohle.txt の大半・singer.txt 705 行以降・tau-extend conditions.md・kit README・S13 scripts・main/supplement の指した節以外。SHA-256 は照らしていない。
- 注入の疑い: なし。
