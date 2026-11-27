# 査読 R3（評価の偏りと個人への推論の方法論・paper-reviewer / opus）
stage: prereg。対象: experiments/20261127-window-overlap-dose/conditions.md（158 行）

## 1. 接地
- 基準 1（選びの段もすべて評価の輪の内に）。Varma & Simon 2006: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- 基準 2（選びを足すと偏りが足される）。Varma & Simon 2006: "when additional parameter selection is being done, the variance of the estimates results in an additional parameter selection bias ... The parameter selection bias, on the other hand, is always negative."
- 基準 3（選んだ後の値は膨らむ）。Liu & Meng: "Our original estimates for the selected markers likely overstate their impact. Bias induced by selection is commonly referred to as 'winner's curse'", "we should restrict attention to controls where the same markers are selected as in our actual study; without this matching step, our inference ignores selection bias."
- 基準 4（対照は問いの構造を運べる解像度で）。Liu & Meng: "This model completely ignores the spatial properties of our image ... algorithms which exploit such smoothness properties will perform poorly on our controls even if they perform well on our actual image."
- 基準 5（個人への推論は対照の選びに依る）。Liu & Meng: "some clinical trial patients are better controls for you than others", "if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."

## 2. 評価表
- a 2: 型 1 の名「仕組みが測れた」。歩みと予測の先の長さを分けず（27 行）、量の交絡も外れないと自ら書く（29 行）のに、331 行の仕組みを「測った事実」として書き直す（111 行）。主張が根拠を越える。
- b 2: (i) 打鍵そのものが続く性質でも同じ形が出る (ii) D = G − C2a の恒等式で D と G は機械的に一緒に動く (iii) R の「同じ構造」が歩みとともに替わる (iv) 列 B の位相はほぼ重複し、N の意味が変わる。手当ても限界も無い。
- c 3: 9 組の値の表と図は型によらず残る。
- d 3: 読みの分岐が多く、型の優先の順が一意に読めない。
- e 4: SHA-256・乱数の流れ・端の再現の門・変異は強い。本文の行の番号が今の main.tex と合わない。「大きく超える」は 1 通りでない。
- f 3: G5 と Uto2020 に限って向きだけを書くのは適切。
- g 3: 割れ・定まらない・欠けのときの型、114 行の分岐と型 1〜4 の優先、R が「増える」でなければ型 1 に入る既定が未確定。

## 3. 指摘
- [major] R の「同じ構造」が歩みとともに替わり、既知の値から型 1 に寄る
  - 位置: 70 行「R（残り）= ジョイント（他人）− 同じ構造の共有」・98 行・S13 notes 88 行「n は CoAuthor k = 5・15 で hmm3（全員）」・128 行「k = 15 では C2a と C2b が同じ 0.1403」
  - 理由: n ではジョイントが hmm3 を選び R ≈ G。歩み 1 では ar3 で R は 10^-3 程度。構造の切り替えだけで R が動き、「R が増えるでない」が成り立ちやすい。Liu & Meng "without this matching step, our inference ignores selection bias"。
  - 解消: 構造を固定した R（例 全歩みで ar3 の R_ar3）を主に読む。または構造が替わるときは R の語を「構造が替わる」として型の判定から外すと事前に書く。
  - 自信: 高
- [major] 開示が足りない。端の R・D と列 B の端は一部わかっている
  - 位置: 21・22・43 行
  - 理由: (1) 列 B の Q(1) は既知の u で、m と差に入る (2) 列 B の s = 30 の位相 0 は n と同じ (3) 端の R は C2a・C2b・選ばれた構造から導ける (4) D の端の向きも既知の値から読める（u で約 +0.70、n で約 −0.26）。区切りを既知の値を知って置けた。基準 3。
  - 解消: 開示を直し（数を添える）、区切りがこれらを見てから置かれたことを限界に書く。できれば読みに使う端を既知でない量（例 列 B の s = 5 と s = 30）に移す。
  - 自信: 高
- [major] D と G は恒等式でつながり、「ともに増える」は独立の支えにならない
  - 位置: 73 行「D = G − C2a」・98 行
  - 理由: C2a が歩みに依らなければ D と G の増えは同じもの。D は本人の r1 を含み、構造の不足と本人らしさが混ざる。構造の不足だけなら共有の 1 次の連鎖 − 共有 hmm3 が要る。書き手の水準で D と G が一緒に動くかも見ていない（基準 5）。
  - 解消: 共有 r1 − 共有 hmm3 で定義し直すか副の量として足す。型 1 の条件に C2a の語を入れる。書き手の水準で D と G が一緒に動く割合を記述として並べる。
  - 自信: 中
- [major] 重なりと、打鍵が続く性質を分けないので、331 行の「overlapping windows」の仕組みは確かめられない
  - 位置: 27 行・111 行・main.tex 331 行 "features computed over overlapping windows make consecutive inputs dependent"
  - 理由: 歩みを長くすると予測の先も 1 秒から 30 秒に伸びる。窓が重ならなくても振る舞いが 1 秒先では続き 30 秒先では続かないだけで同じ形になりうる。基準 4。
  - 解消: (a) 歩みを固定して窓の長さを変える比べを足す、または (b) どの型でも 331 行の「overlapping windows」を「歩み（重なりと予測の先の長さ）」に書き換え、窓の作りの寄与と振る舞いの持続を分けていないと残す規則を D5 に入れる。
  - 自信: 高
- [major] 量の交絡がどちらの列でも外れないと認めながら、主の読みを列 B だけで決める
  - 位置: 29 行・94〜100 行
  - 理由: 「挟む」なら両側が同じ形のときだけ量によらないと読める。列 B の s = 30 はほぼ同じ 30 本で、N を u と同じ量として受け取るが中身は n とほぼ同じ。縮みが弱いぶん過学習で G が下がる向きに偏りうる。
  - 解消: 型 1 に列 A でも G・D が「増える」を足す（端は既知と添える）か、型 1 の名を「列 B で歩みに沿った」に弱め量の交絡が残ると型の文に含める。
  - 自信: 中
- [major] 型の分岐が、割れ・定まらない・欠けのときに 1 通りに決まらない
  - 位置: 82 行・98〜101 行・114 行
  - 理由: G が割れたとき型 3 か型なしか不明。R が割れ・定まらないと「増えるでない」として型 1 を支える既定。114 行と型 1〜4 の優先も無い。
  - 解消: 優先の順（操作の門 → 主の量の割れ・定まらない・欠け → 型 1〜4）を書く。型 1 の R の条件を「沿わない」の肯定の語にする。R が割れ・定まらないときの型を足す。P-READ に組を入れる。
  - 自信: 高
- [minor] 構造の選びの語が、変わらない場合も「沿う」と読む（106 行）。解消: 少なくとも 1 組で >、かつ両端の差 ≥ 1 人。自信: 高
- [minor] 区間と書き手の割合を読みに使わないので、17 人の中央値の揺れで語が決まる（78・88 行）。解消: 再標本ごとに語を当て直し同じ語の割合を記述として並べる。自信: 中
- [minor] M は門として弱い（96 行）。遅れ 1 の相互情報量は先の長さとともに下がるのが普通。列 A の長い歩みでは組が約 100 で plug-in の偏りが大きい。解消: 門が弱いことを限界に書き、列 A の M は Miller–Madow を主に。自信: 中
- [nit] 本文の行の番号が合わない（7 行「307 行」は今の main.tex で `\setlength{\tabcolsep}{4pt}`、文は 331 行）。解消: 逐語と節で引き main.tex の commit を記す。自信: 高
- [nit] 「8 時間を大きく超える」が 1 通りでない（119 行）。解消: 数で（例 10 時間）。自信: 高

## 4. 総合: major
- R の構造の切り替えと D = G − C2a の恒等式で、既知の端から型 1 が出やすい。開示がその既知さを落とす。
- 重なりと予測の先の長さ・振る舞いの持続を分けず、331 行の仕組みを「測った」と書ける設計でない。量の交絡も列 B だけでは外れない。
- 割れ・定まらない・欠けのときの型の優先が未定で、R が既定で型 1 を支える。

## 5. 読めなかった範囲と注入の疑い
- 読まなかった: SEED、kit README、tau-extend conditions.md、scripts 4 本、main.tex・supplement.tex の他の部分、liumeng.txt の一部。SHA-256 は照らしていない。
- 注入の疑い: なし。
