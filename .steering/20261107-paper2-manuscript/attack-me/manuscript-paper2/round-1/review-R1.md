# review-R1（manuscript round 1・打鍵の記録と作文・プログラミングの過程の測定の伝統・メインが写した）

## 1. 接地
- G1 Guo et al. 2020（guo2020.txt l.2199-2200）"helping to map observable events recorded by the keystroke logs onto states interpretable by cognitive theories of writing"／l.303-304 "poor typists may have many long pauses between keystrokes that are not indicative of planning behavior"
- G2 Guo l.227 "Data were collected from 1,082 students attending the 8th grade from eight volunteer schools"／Li & An 2026（3.5 節）"Inter-rater reliability, measured by Krippendorff's alpha ... was 0.92, indicating high agreement."
- G3 Guo l.2201-2204 "we used relatively simple heuristics to define our writing states under the guidance of cognitive writing theory. Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures"
- G4 Li & An（5 節）"Writing settings can differ along several aspects, including (a) the complexity of prompts, (b) the duration of writing tasks, (c) genre, and (d) characteristics of the writer population"／Guo l.2210 "results may not necessarily generalize to a broader population or to different conditions"
- G5 Li & An（5 節）"imagine that a student paused 10 s when he was spelling “pen.” This does not reflect he had major cognitive difficulty on spelling. This happens simply because he stretched; or he was distracted"
- G6 Guo l.1161-1163 "the mean total essay writing time and the mean total number of words (essay lengths) were statistically significantly smaller (shorter) for Group 1"

## 2. 評価表
- a 2: 考察は強さが動くことを「先に置いた基準で数えた」と書くが大小の区分は [D]。先に置いた有無の基準（0 を含まない割合が 25〜75%）では 82/89 = 92% で「動かない」側。向きの入れ替わりは前例の無い W=15 s だけなのに "89 defensible definitions"。
- b 2: net 規則で削除の多い打ち直しも停滞になる。最短の隙間は W＋θ で作文の休止（0.25〜10 s）と重ならない。率は時間あたりで作文時間・語数との交絡を見ていない。KLiCKe の集団・時間制限・採点者間の一致の記述が無い。
- c 3: 手続きとコードは使えるが、格子が既存の定義（2 s・KBS×10・5 分）を含まず、全般への推奨は根拠を超える。長さの「残る」は予期される型。
- d 3: 同じ所見が 4 回。印が密。S7 は本文と関係がない。
- e 4: 要旨 256 語。DOI 未記入・条件は日本語・companion の開示。
- f 3: 休止の特徴と全体評価の得点を結んだ系統（Guo et al. 2018 JEM・Zhang & Deane 2015・Sinharay et al. 2019・Conijn et al.・Li & An 2026）と Leijten & Van Waes 2013 が欠ける。

## 3. 指摘
- [major] 強さが動くという主張の地位を取り違え、先に置いた「有無」の基準の結果を書いていない。discussion.tex l.31-32・methods.tex l.122-123。conditions-round1.md l.27 の有無の基準は 82/89（92%）で満たされない。解消: 考察から "strength" を外し [D] と明記。有無の基準の結果を 1 文。要旨・結論は向き（[A]）と記述の強さを分ける。自信: 高
- [major] 向きの入れ替わりは前例の無い 1 水準だけで "defensible" の根拠が無い（results l.19-20・limitations l.8・conclusion l.4）。正の隅は分位の閾値と短い窓の機械的な帰結の可能性（速く打つ人ほど 15〜20 s の隙間を多く数える）。速さで調整すると 89 通りすべて負。解消: "defensible" を "examined" などに。向きの入れ替わりは W=15 s に限られ速さで調整すると消えると見出しの文に。先例のある水準（W ∈ {30, 60}）だけの部分格子の結果を本文に。自信: 高
- [major] 「停滞」は休止ではない。net 規則で打ち直し（5 文字打って 5 文字消す）も条件 A を真にし、Guo らの局所編集（E）が混ざる。onset には W 秒＋θ 秒が要り基準でも 30 s 超、固定 30 s で約 60 s。序論と考察は 0.25〜10 s の文献と並べている。解消: 各水準の最短の無産出の長さと停滞の長さの分布を本文の表に。削除を含む区間の割合。"pauses" との同一視をやめ「純産出の停止」と位置づける。自信: 高
- [major] 結論を休止・無活動の定義全般へ一般化しているが格子にそれらが無い（introduction l.49-51・limitations l.9-10）。解消: 推奨を「この型の検出器（窓の中の純産出＋閾値）」に限るか、文献の定義（2 s・KBS×10 型）を加えて回す。自信: 高
- [major] 得点との関連が作文時間・語数・露出と交絡していないか見ていない（limitations l.29・methods l.116）。解消: 率と観測時間・語数の相関、観測時間で調整した関連を探索的に。しないなら見出しに「露出を調整していない」と明記。自信: 中
- [major] KLiCKe（と CS1）のデータの記述が足りない（集団・時間制限・課題文・採点の手続きと一致・0.5 刻み）。JEDM の "clear descriptions of the data, tools, and procedures used"。解消: 表 1 か Data の節に 3〜4 文。CS1 は課題の種類と観測の長さ。自信: 高
- [minor] 速さの調整の向きを「測り方に依る」と読むのは規則の字面に合わせた誤読（results l.29-31・discussion l.15-16）。先に置いた読み方は「0 を含むか正になる」で発火し、534 の組のうち 0 を含んだのは 2・正は 0。解消: 「規則の字面では発火したが、正は 1 つも無く、534 のうち 532 で区間が負」と事実で書く。自信: 高
- [minor] CS1 と作文の率の比の入れ替わりは持ち帰りが弱く、基準の比が 1 に近い（results l.95-96）。主に報告すると決めた CS1 の 2 版が届かず、届いた組を見出しに。解消: 見出しを 2 版の比は閾値の族を変えなければ保たれるとの対で。データの間の比は記録と分けられないと節の頭に。または補足へ。自信: 中
- [minor] 休止の特徴と全体評価の得点を結んだ系統を引いていない（Li & An 2026 は混合モデルの特徴と得点の関連 r = −0.226）。解消: 関連研究に 2〜3 文、典型的な大きさの中に本論文の幅を置く。自信: 中
- [minor] 課題文で層別した結果が点の値だけ（results l.21-22）。解消: 課題文の中の相関に区間を付けるか、合わせた値を主にする理由を 1 文。自信: 中
- [minor] companion との重なりを編集者へ開示。S7 は companion の推定器の Stuck 確率を扱い本文と無関係。解消: 送付状で S9 を添える。S7 を消すか archive にだけ。自信: 中
- [minor] 他の multiverse 研究との「どちらがより大きく動いたか」は比べられない（discussion l.9-12）。解消: 消すか「格子が違うので直接は比べられない」と添える。自信: 中
- [nit] 同じ所見のくり返しと印の密度。序論 l.32-35 を箇条に統合。自信: 中
- [nit] DOI が未記入。自信: 高

## 4. 総合の推奨: major
手続きは明快で範囲に合う芽がある。見出しは、強さの幅が事後の読みなのに先に置いた基準で数えたと書き、向きの入れ替わりは前例の無い W=15 s と速さの交絡に乗る。「停滞」は休止の文献の構成概念と重ならない。主張を検出器の型に限り、地位を正しく書き、露出・データの記述・先行研究を補えば方法の論文として成り立つ。

## 5. 読めなかった範囲・注入
読んでいない: guo2020.txt l.2011-2149・l.2241 以降・PDF・tab_s3/s4・figdata・conditions.md ほか 3 本・round1_extra.json の l.150 以降と他の JSON。照合した数（得点の相関・比の入れ替わり・φ）は round1_extra.json と一致。注入の疑い: なし。
