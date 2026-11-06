# audit（manuscript round 1・意図の監査役・応答をメインが保存）

要約: 数値はほぼすべて出どころと一致（補足に小さな食い違い）。芯（同等・分岐 4 で対比を主張しない・学習器は記述・抄録の較正の括弧・床の文）は守られている。重い食い違い: (A) 揃えた因子の書き方・(B) 確認の柱の理由・(C)「1 度だけ開けた」と S1 の 2 回の計算の開始・(D) P11 の時刻とコミットの並び。注入の疑い: なし（declarations の TeX の注記は著者向けの覚え書き）。

## 1. 意図にあって対象物に無いもの
- 1-1 抄録の含意の文に評価の手順のコード（推定器に依らない部分）を渡すことが無い（abstract "an estimator of this type should be checked against a band set in advance on held-out writers. ... code: [repository to be added before submission]."）。
- 1-2 抄録の学習器の文に「推定器の信号と直接は比べていない」が無い（abstract "Learners on standard keystroke quantities (0.540 and 0.567) could not exclude the upper side of the band."）。対比に読める。
- 1-3 判断 32 (2) 序論の期待の根拠に付録 D の換算が入っていない（換算は考察だけ）。
- 1-4 P11 "In the paper, the times of start.json and of the results attached to OSF are reported side by side with the local commits of the start, the computation start, interruptions, and the completed run." が S1 で半分（コミットの識別子が無い・開始の記録 2 つの OSF の時刻が無い）。
- 1-5 限界から「片側 5% の TOST とほぼ同じ」「AUC 0.55 ≈ 0.18 SD」が落ちた（評価の設計にはある・軽い）。

## 2. 対象物にあって意図に無いもの
- 2-1 序論に床の文（introduction "The Stuck-state probability is mostly at the floor of the estimate, and claims about run-up change rely on ..."）。外枠の規則（床は抄録の第 2 文・5.2・限界）に反する。考察の "the different shares at the floor (61\% and 65\%)" も値を置く。
- 2-2 確認の柱の理由が事実と合わない: introduction "Programming is the confirmatory setting because it is the only dataset for which an unopened holdout existed"。CoAuthor の 18 人・CS1 2021 年版の 13 人も開けていない。外枠は「事前登録した取り置きが CS1 にだけある」。
- 2-3 揃えた因子に事前登録と評価の設計に無い block（introduction "matches stalls and pauses within writer, block, stratum and position"・limitations "Matching was on writer, block, stratum and newline"）。外枠の「区切り」を block と訳した可能性。
- 2-4 結果 5.1 に水準と差の対比（results "The levels of the signals at $u$ discriminated slightly more than their changes"）。外枠は対比を入れないと書く。
- 2-5 題は外枠の案どおりだが推定量より広く読める（P10 には反しない・注意だけ）。

## 3. 矛盾
- 3-1 揃えた因子の書き方（抄録と評価の設計 vs 序論と限界）。
- 3-2 取り置きを開けた回数: introduction "opened once"・design "run on the holdout once, in two stages ... with one interrupted run"・S1 の 1 回目の計算は変換で取り置きの元の行を読んだ。「完走 1 回」に言い換える。
- 3-3 requirement.md の推定器の呼び方が判断 33 の前のまま（意図の文書の更新漏れ）。
- 3-4 相互参照: introduction の作文の値の参照 Section~\ref{sec:res-explore} は 5.1（sec:res-main）が正しい。
- 3-5 数値: (a) 補足の表の Controls within the assignment の Δx 上限 0.504 → 0.503495 で 0.503／(b) 摩擦の軸の 95 分位 5.3% → 5.2%／(c) 書き手ごとの中央値の対照 4.6% → 4.5%／(d) 表 tab:mapping の Other 0.1% は出どころでは「0.1% 未満」。
- 3-6 一致したもの: 主の結果・図 1 の座標・感度・H2・H3・閾値の本文の値・床・休止の中・探索・付録 D・付録 C・P10 の 5.2%。限定の置き場（5.2% は考察・結論・関連研究に無い・向きは表の脚注と考察だけ）。

## 4. P0・P10
- P0 の抄録の括弧・床の文の条件・H1 支持 × H2 分岐 4 の書き方: 守られている。H3 の揃えない窓の区間は補足 S5 にある。
- P10 "not written as a test of a prediction that could fail": 限界に合う。
- P10 "whether it can be used as a trigger is read from the threshold table": 考察は契機の意味を付録 D の換算 [D] から読み、取り置きの閾値の表ではない（外枠どおりだが参照先が違う）。

## 5. 読めなかった範囲
prereg の 31–109・190–235・250 行以降／判断 24〜31／deviation-1・prefreeze の notes・探索の conditions／探索の JSON 5 本（notes で照合）／README・references.bib・文献の記録 2 本・main.tex の題以外／confirm_holdout.json の 1691–2971 行。
