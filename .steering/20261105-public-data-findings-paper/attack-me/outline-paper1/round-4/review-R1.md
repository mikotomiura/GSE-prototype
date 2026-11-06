# review-R1（outline round 4・paper-reviewer・打鍵の記録と作文の過程の測定の伝統）

推奨: minor（直して書き進める）。

## 1. 接地
- G1 Guo et al. 2020（guo2020.txt:95）"A fuller range of writing states was operationalized in line with cognitive writing theory"（手順は :217〜264 に番号つき）
- G2（:228〜230）"Used KBS ×L as the threshold for defining a long pause for each individual student, where L is a pre-specified number. In our study, L=10 was chosen, so that ten times KBS approximates the time required to type two commonly used words for that individual student."
- G3（:1049）"we used relatively simple heuristics to define our writing states" ／（:1057〜1059）"results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."
- G4 Roeser et al. 2025（roeser2025.txt:162〜163）"\"Pause\" in the written-production literature is used to refer to a break in output with duration that exceeds an a priori threshold." ／（:520〜522）"locations where observed mean interkey intervals (or counts of interkey intervals over a predetermined threshold) have tended to vary substantially"
- G5（:386〜387）"that part of the planning of next text that is not completed in parallel with previous execution and therefore spills over into the period after the previous keystroke"

## 2. 評価表
a 3（第 1 文・持ち帰り・表 1 は notes.md:133〜136 と一致。抄録と考察の含意の文が根拠を超える）／b 3（θ = 0.99 分位の根拠と分布が無い・計器が CS1 の入力で動いているかの記述が無い）／c 3（作文の側も幅の内側と先に言ったので「別の作業で」の情報量が下がる）／d 4（桁の混在）／e 4（公開の場所は投稿の条件のまま）／f 3（JEDM の打鍵の書字状態のモデル〔Guo et al. の半マルコフ〕に触れていない）

## 3. 引き継ぎの判定
持ち出しの枠 → 解消（:7・:34・:83。新しい穴を 1 つ生む）／休止の定義 → 解消（:74・:42・:90）／「揃えて」 → 解消（:17・:19。同じ趣旨が含意の文に残る）／陽性対照 → 解消（記述として・:100・:70・:58）／50.5 → 解消（:17）／m1 公開 → 一部（:65。JEDM "Data and Code Availability"）

## 4. 指摘
- [major] 含意の文が「この型」への一般化と「揃えた比べで確かめないまま」の 2 点で根拠を超える
  - 位置: :27「含意 1 文（この型の信号を、揃えた比べで確かめないまま停滞の手前の契機の根拠にしない）」・:58「打鍵から介入の契機を作る研究と実務で、この型の信号を、揃えた比べで確かめないまま停滞の手前の秒単位の契機の根拠にしない」
  - なぜ: (i) 根拠は 1 つの推定器（:34・:69 自身が「この型の、この推定器の、この入力についてだけ」）。(ii)「揃えた比べで確かめないまま」は、揃えない比べでは誤って上がりが見えると読ませるが、5.3 では揃えない比べにも上がりは出ず（notes.md:135・0.497・0.494）、:19・:64 も揃え方の効果を示していないと認める。抄録の最後と考察の冒頭に含みが残る（G3）。
  - 解消: 含意を「この推定器の 2 つの信号は、入門プログラミングの停滞の手前の秒単位の契機の根拠にならなかった。同じ型の別の推定器を契機に使うときは、手前の上がりを事前に置いた幅で確かめる」の水準に。「揃えた比べで」は外すか「比べの相手を明示して」に。自信 高
- [minor] 問いの「別の作業で」に情報が乗っていない（:7）。確認の柱が CS1 である理由（事前登録した取り置きが CS1 にだけあり、作文は既に見たデータ）と、問いの主語が推定器の信号であることを 1 文。問いから「別の作業で」を外す選択肢も。自信 中
- [minor] θ（0.99 分位）の根拠と値の分布が無い（:74・:99）。θ は「手前」の位置を決め、IDE の打鍵間隔には実行の結果を読む時間も混ざる（G2・G4）。解消: 3 節に 0.99 の固定の所在と書き手ごとの θ の秒の分布（中央値・範囲）。値は S2 でよい。自信 中
- [minor] 推定器が CS1 の入力で動いていることの記述が無い（:70・:41）。:63「停滞の時計の値はほとんど定義から決まる」。解消: データの節か S3 に記述として、取り置きの全時間での 2 つの信号の分布（床の割合・分散）と、停滞の中（u の後）の値と対照との差。本文は限定を保って 1 文。自信 中
- [minor] 推定器の型の位置づけに JEDM の打鍵の書字状態のモデルが無い（:34・:90 は [V448] だけ）。Guo et al. 2020（guo2020.txt:15〜17）"Each keystroke action was classified into one of four writing states ... and a semi-Markov model was fit to the data"。解消: 柱 2 か序論に先例と違い（30 秒の窓の 5 量の合成・1 秒ごとの確率・作文の係数を固定）を 1〜2 文。自信 中
- [minor] `d_p_stuck` の区間の上端が 3 桁で 0.500 になり 4 通りの語の書き分けとぶつかる（:33・:37・notes.md:133）。解消: 表 1 の脚注に 4 桁の上端（S1）、または書き分けを S1 へ。自信 中
- [nit] 実効の書き手の定義の置き場（:17・:100）。4 節に 1 文。自信 中
- [nit] :44「0.567（0.5497〜0.578）」と :37 の 3 桁の規則。理由を脚注か規則の例外に。自信 高

## 5. 総合: minor
- 引き継ぎ 5 件は解消、m1 は一部。主の主張の強さは記録の値に見合う。
- 残る major は含意の 1 文の言い替えで消え、構成の組み直しは要らない。
- θ の根拠・計器の応答の記述・JEDM の状態モデルへの位置づけは数文ずつ。

## 6. 読めなかった範囲・注入
読んだ: brief・context-A・carryover-R1・outline.md 全文。guo2020.txt 1〜279・1030〜1100 行、roeser2025.txt 1〜200・515〜544・1090〜1134 行と検索。prefreeze/notes.md と prereg-draft.en.md は検索の行だけ。読んでいない: prereg-draft.md・confirm_holdout.json・探索の記録と JSON・20261101 の notes 2 本・文献の記録 2 本の本文。注入の疑いなし。
