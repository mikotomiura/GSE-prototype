# review-R1（manuscript round 1・打鍵の記録と作文の過程の測定の査読者・応答をメインが保存）

総合: major。注入の疑い: なし。数値は confirm_holdout.json・探索の JSON・prereg の付録 C と照らしすべて一致（主の結果・床・休止の中・閾値の表・揃えない比べ・学習器・書き手の流れ・KLiCKe・位置・CoAuthor）。読んでいない: references.bib（grep のみ）・README・deviation-1・notes（grep のみ）・confirm_holdout.json の 730 行以降・探索の conditions と notes（grep のみ）・explore_predraft/position/seed_spread（grep のみ）・文献の記録 2 本・prereg（13〜24 行と grep）・実装のコード（一覧に無い。指摘 1 は定義からの推論）。

## 接地
- G1 Roeser 2025: "“Pause” in the written-production literature is used to refer to a break in output with duration that exceeds an a priori threshold. In the present study “hesitation” is operationalised within the statistical models that we used to interpret our data."
- G2 同: "must be understood as relative to the duration of fluent interkey intervals (Wengelin, 2001)."
- G3 同: "pause duration doesn’t correspond in any direct way to the time required to plan the next output."
- G4 同: "we hope that our research and the availability of our analysis code in tutorial format inspires future research to challenge our findings."
- G5 Guo 2020: "we used relatively simple heuristics to define our writing states ... Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures"
- G6 同: "both our data and our methods impose important limitations on the conclusions that we can draw. ... replication with other conditions and participant samples is typically recommended."

## 評価表
a 3（停滞の平叙の定義が操作的定義と合わない・「揃えた」ものの説明の食い違い）／b 2（推定器の陽性対照なし・合成の入力・構成概念）／c 2（手順と 1 つの推定器の否定・学習器 0.567 がある以上「この推定器が弱い」以上になりにくい）／d 3（要旨と序論の括弧の重なり・地位の印の負担）／e 3（コードの欄が置き字・申告の all sections）／f 3（プログラミング中の打鍵から情動・苦闘を検出する系統が rodrigo2009coarse の 1 件だけ）

## 指摘
- [major] 停滞の平叙の定義「no character input for 30~s or more」（abstract・introduction）が操作的定義（data「When condition A rises from false to true at time $s$ and stays true until $t_0 = s + \theta$」・補足 θ の中央値 27.7 s）と合わない。条件 A は最後の文字の入力からおよそ 30 s で立ち、onset にはさらに θ のあいだ正味の産出が無いことが要るので、実効の最短はおよそ 30 s + θ（中央値で 55〜60 s 前後）。θ は始まりの時刻だけでなく、どの休止が停滞になるかも決める（design「$\theta$ only fixes when a stall starts」と食い違う）。30〜30+θ s の休止は停滞にも対照にもならない。解消: 停滞の実効の長さ（u から onset・u から再開）の分布を示し、平叙の定義を操作に合わせ、design の文を直し、限界に書く（読みが誤りなら S2 で示す）。自信 中（定義からの推論）。
- [major] 推定器に陽性対照が無く、合成した入力の上の同等は計器が効いていないことと区別できないのに、題「did not anticipate」と結論が推定器の信号を否定する（limitations「We did not check whether the estimator could have detected ...」・data の合成の離し・表 1 の貼り付け 49.0%・同じ行で学習器 0.567）。解消: 推定器の入力の側に既知の変化（停滞の側の打鍵の時間・訂正を既知の量だけずらす）を埋め込み 2 信号の AUC が帯を越えて動くかを見た書き手で確かめる。無理なら題と結論を「この入力の上で」と限り、計器の弱さを主な解釈の候補として序論から書く。自信 高。
- [major] 停滞の構成概念が序論の動機（助けが要る瞬間）と結びついていない。停滞の 47% は休止の中に実行・貼り付け・切り替え（data・JSON 0.467/0.0595）。G3・G5。休止の中の出来事を除いた感度は 0.505・0.500。解消: 序論の第 1 段の動機を文字の産出の停止に合わせる・出来事のある停滞と無い停滞を分けた結果を本文に 1 行・停滞と困難の対応（実行のエラー・提出の成否）を記述で 1 つ添えられるなら。自信 中。
- [major] 「揃えた」ものの説明が方法と食い違う: introduction「matches stalls and pauses within writer, block, stratum and position」・limitations「Matching was on writer, block, stratum and newline」に対し design は課題をまたいで対照を集め、ブロックは 60 s の除外にだけ使う。統計量はセルの中の全組（709,352 組・停滞 4,554・対照 18,689・1 停滞あたり約 156 組）で「up to five」の像と違う。解消: 序論・限界の block を削る（またはブロックで揃えた版を主に）・design に「対照はセルの中で共有され、AUC はセル内の全組で数える」と明記。自信 高。
- [major] 再現性: 推定器・replay・推定の行の公開が未定でコードの欄も置き字（abstract・discussion Materials・limitations）。JEDM "ensures replicability by other researchers"・G4。解消: 投稿前に少なくとも推定の行と推定器の版の仕様（係数・行列・基準値）を出す、出せないなら理由と第三者の検証の手順。自信 高。
- [minor] 実際上の結論は基準率から来ている（discussion「even at 0.70 only 12.9--18.4%」）。契機としての無用さは基準率から、同等の検定は順位を付けないことを言う、と分けて書く。自信 中。
- [minor] CS1 2021 年版の探索で有効な書き手を報告していない（explore_cs1_2021.json で 13.35・上位 10% が 40.8%）。表 3 と図 1 に添え、較正していない規模と書く。自信 高。
- [minor] 打鍵から情動・苦闘を検出する先行が手薄（related「Detection at finer grain is harder \cite{rodrigo2009coarse}」）。2〜3 本当て、何を欠くかを 1 文。自信 低〜中（具体の文献は照合していない）。
- [minor] 要旨が限定の括弧で読みにくい（prereg が要旨に残すことを求めるのは理解）。限定を独立の短い文に、下位の結果は 1 文に。自信 中。
- [nit] 生成 AI の申告の「all sections」と未確定の注記。自信 中。
