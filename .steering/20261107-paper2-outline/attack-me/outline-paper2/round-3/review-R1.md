# review-R1（outline round 3）
接地: Guo ら 2020（280-285）"A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. …"・(223-228) "KBS was defined for each writer as his or her within-word median time … Used KBS ×L as the threshold"・(476-478) "We first a conducted 4-state vs. 3-state Semi-Markov model comparison …"・(1049-1052) "we used relatively simple heuristics …"・Li & An 2026 "establishing feature consistency is an initial first step …"・"imagine that a student paused 10 s when he was spelling “pen.” …"・"Pause events are classified according to the linguistic context (i.e., text boundaries, Medimorec and Risko, 2017 )."
carryover: 2 件の major は解消（読み方を守り「支持されない」と書いた点を評価）。「逆の結論」は一部（4 倍）・信頼性の列は一部・Guo ら 2020 は置き場は解消。
評価表: a 2・b 3・c 3・d 4・e 4・f 3。
指摘:
- [major] M1 押下の率の固定は交絡の調整か、停滞そのものを引いているか（分母の共有・停滞の時間が押下の時間を削る部分と全体）。固定 θ の P1 中央値 −0.37 はこれでも起こる。過剰な調整でも縮む。0.62 は制限時間の作文では産出量（長さ）と総合評価の関連に近く「流暢さ」の名は当たらない（Guo らの速さは語の中の速さ）。解消: 量の名を「産出の率」に・「交絡」をやめる・限界 6 に分母の共有と部分全体と媒介・推奨 1 を弱める。計算を足すなら停滞を除いた時間を分母にした押下の率か語の中の間隔の中央値で固定し直す。自信 中
- [major] M2 偏相関の符号は止まりの条件の軸でほぼ決まる（文字だけの 45 通りはすべて区間で正・例 W30_q0.99_ins_replay 0.0745 [0.048, 0.102]・正味ではほとんど負か 0 を含む）。削除を停滞に数えると推敲を拾う読み。解消: C1 と 4.1 に軸ごとの内訳を [記述] で・考察で推敲の解釈を可能性に・推奨に止まりの条件を構成概念の選択として明示。自信 高
- [major] M3 いちばん強い主張の機構の半分が事後の [記述] の 0.93 に乗る。0.62 が一定なので ρ ≈ 0.62·P1 + 偏相関の項で 0.93 はほぼ代数で決まる。2 つの塊だけでも高い相関が出る。解消: 「連動した〔記述〕」に弱め「決まる」をやめる・強さを分ける・族の中の値を並べる・式の関係を 1 文。自信 中
- [minor] m1 「4 倍」は基準を分母にした比（他の点を分母にすればいくらでも大きい）・「無視できる」の物差しの不一致。解消: ρ の単位で範囲と幅・標本の区間の幅と並べる・目安を 1 つ置く。自信 高
- [minor] m2 Guo ら 2020 の個人化は KBS×L で本人の分位とは別の操作。解消: 3.3 で区別・限界 2 に KBS×L の族は振っていない。自信 高
- [minor] m3 休止の言語上の位置で分ける答えが柱 2 に無い。解消: 1 文と振らなかった理由。自信 中
- [nit] n1 C4 の「Guo ら 2018 は未登録」を引くか決める。自信 高
総合: major。
読めなかった範囲: 条件 2 つ・results の多く・カード 3 枚・接地の後半。注入なし。
