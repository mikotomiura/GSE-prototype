# R2 の応答（データを公開・管理する側・round 4・commit bf0d2450）

総合: major（直せば minor 以下の見込み・新しい計算は要らない）。

## 1. 接地
- B1 Borgman l.192–195 "Good stewardship means releasing some kinds of data and preventing the release of other kinds of data. The same data may fall into either category, depending on the time, purpose, or entity requesting access."
- B2 Borgman l.2341–2344 "Maintaining provenance records is essential, lest data collections be separated from information about origins; licensing and ownership; applicable regulations; records of notice, consent, and acceptable uses"
- B3 Borgman l.2420–2422 "Anonymity, which is fundamental to most methods of privacy protection, has become extremely difficult to sustain as methods of re-identifying individuals become more sophisticated. Notice and informed consent remain necessary but are far from sufficient"
- H1 Hanisch l.2233–2235 "the evaluations should also consider an attacker that actively tries to reverse the anonymization and knows the anonymization technique and its parameters." / l.2447–2448 "most anonymization techniques are only evaluated rudimentarily with the assumption of a weak attacker."
- H2 Hanisch l.170–172 "We shall employ the term utility to quantify the degree of functionality maintained concerning a service for which the behavioral biometric data is intended." / l.348–351 "… preserved to the extent that the received service (e.g., a personalized recommendation) is still meaningful and effective."
- H3 Hanisch l.2432–2433 "an anonymization method should also work on a small group size with high data quality" / l.74–77 "the efficacy of randomized, perturbative anonymization also must be critically reviewed, as the dependencies might be used to infer the identifiable information"

## 2. 評価表
a 3（見出しの「4 倍以内」は 500 人の値で、全員では R4(4) が 0.65% [0.47, 0.87]・支配は登録の攻撃者だけ）／b 4（探索は R3-u に当てていない・全員の結果を見出しに戻していない）／c 3（探索の後の前線が本文から読めない・効用の軸が得点との関係の変化を隠す）／d 3（「four times chance … though not exploratory」の組が 7 か所・§8 冒頭と結論がほぼ同文・抄録 348 語）／e 4（12 頁内・必須の節あり・倫理審査なしの危険は残るが手当ては厚い）／f 4（SDC は技法の名だけでリスクの測り方に結び付けていない）。

## 3. 引き継ぎ
1 一部（見出しはまだ閾値・全員で崩れる）／2 解消（discussion.tex l.74–77）／3 一部（§8.3 の R7 の文そのものに条件が無い・探索の攻撃者も抑制を戻すものではない）／4 解消（文言・帰結の扱いは弱い）／5 解消（results.tex l.139–140）／6 一部（リスクの測り方への対応が無い）／7 一部（探索で繰り返しが増えた）／8 解消。

## 4. 指摘
- [major] 1 見出しの「4 倍以内」が全員（4,992 人）の結果で成り立たず、本文から辿れない
  - 位置: abstract.tex l.13–15 "only segment values coarsened to four or more brought the full-text attackers, with their main penalty, within four times chance at $N = 1{,}000$"・同じ主張 introduction.tex l.48–49・discussion.tex l.10–11・conclusion.tex l.6–8・results.tex l.153–154 "Only R4(4) and R4(8) brought the strongest attacker within four times $1/N$"。対する値 generated/all-writers.tex l.12 "R4(4) & … & 0.65 [0.47, 0.87] & A2 (89) & 0.35"。appendix-results.tex l.220–222 "Of the gains over A0 that Section~\ref{sec:results} reports, one changes: on R4(8) at $N = 10$" は R4(4) に触れない。全員では R0 も 99.9%。
  - 理由: 全員で R4(4) は 6.5 倍・下限 4.7 倍。付録は読まれない。Hanisch "must be improved to give a good assessment of the privacy protection" (l.125–126)。
  - 解消: 閾値でなく値で書く（例 "R4(4) and R4(8) left 0.35% and 0.14% (500 writers; 0.65% and 0.15% for all writers)"）。最低限 §7.2 に全員の R4(4) の値を 1 句、付録 E の "one changes" を直す。
  - 自信: 高
- [major] 2 図 1・表 4・支配関係が登録の攻撃者だけで、探索の後にどちらの前線で読むか分からない
  - 位置: results.tex l.128–131 図 1 の注 "No form evaluated brought matching near chance while computing the process measures. … attackers with $\lambda = 8$"・l.143–146 "The forms that no other form dominates are R0 and R1, R3, the three levels of suppression and R4(8). … R7(0.25) dominates R3-u, with a lower accuracy (14.3\% against 36.0\%)"・explore-strongest.tex l.6, 8, 9（R4(8) 2.4・R7(0.25) 62.3・R7(0.5) 2.2）・appendix-exploratory.tex l.69 "A2 on R3, R4($w$) and R7($p$)"。
  - 理由: 探索の値では R4(8)（2.4%・ρ 0）は R7(0.5)（2.2%・ρ 0.70）に支配され、R7(0.25)（62.3%）は R3-u（36.0%・探索なし）を支配しない。公開する側の答え「強めた攻撃者で前線の下端に残ったのは R7(0.5) だけ（ただし一致は 1.6% の書き手に集中）」が本文に無い。Borgman B1。
  - 解消: 図 1 に探索の攻撃者での位置を別の印で重ねる（表 25 に座標あり）。§7.3 の支配の文を「登録の攻撃者で」と限り、探索の下での前線を 1 文。R3-u に探索を当てていないことを §7.2 に 1 句。
  - 自信: 高
- [major] 3 効用の軸（10 指標の中央値の順位相関）では、得点との関係が損なわれることが読めない
  - 位置: results.tex l.117–121 "it does not cover … the prediction of scores"・discussion.tex l.70–71 "suppressing a quarter of the presses left 14.3\%, with a median correlation of 0.81"・utility-score.tex l.4（平均ポーズと得点の相関 R0 −0.11 → R7(0.25) −0.36 → R7(0.5) −0.50）・utility-r0.tex l.3, 10（R-burst 0.18–0.28・挿入の割合 0.11–0.20、R2 以降すべて）。
  - 理由: 過程のデータの主な使い道は質との関係。R7(0.25) の 0.81 は平均ポーズと得点の関係が 3 倍強になることを隠す。対処が「近似を明示」だけ。中央値なので 2 指標がすべての形で失われても軸に出ない。Hanisch H2。
  - 解消: 表 4 に「得点との相関の R0 からの最大のずれ」か「ρ ≥ 0.8 の指標の数」の列、または §8.3 の R7(0.25) の文に "(the mean pause then correlated with the score at −0.36 against −0.11 in R0)" を 1 句し §7.3 と統合。図 1 の縦軸の名に "agreement with R0"。
  - 自信: 中（列の並びは見出しを読まずに推定）
- [minor] 4 一致が得点の高い書き手に偏ることが持ち帰りに無い
  - 位置: results.tex l.194–195 "accuracy differed by score band on R3-u and on several coarse forms"・explore-band.tex（R7(0.25) N = 1,000 低 9.5・高 22.2、R4(8) N = 10 低 4.8・高 29.5）。
  - 解消: §8.3 Setting に 1 句（"on R7(0.25) and the coarse forms at $N = 10$ the top third by score was matched more often (exploratory)"）。§7.6 の文は消してよい。
  - 自信: 中
- [minor] 5 SDC との対応が技法の名だけで、リスクの測り方に結び付いていない
  - 位置: discussion.tex l.61–65 "R1 to R3-u recode the keys globally … R4 releases only a variable derived from each log … R7 suppresses presses at random, not, as local suppression does"
  - 解消: 対応の文の前に 1 文（"In these terms, the closed-world accuracy is a record-linkage measure of identity disclosure risk with the text as the external file"）。
  - 自信: 中（当てはめの正しさは低・ハンドブックは読めない）
- [minor] 6 探索を入れた後の但し書きの重複
  - 位置: discussion.tex l.7–15 と conclusion.tex l.4–10 がほぼ同文・results.tex l.88–91 と discussion.tex l.66–69 が同趣旨（"below 40\%"）・related.tex l.46–47 の重複。
  - 解消: §8 冒頭を 2 文に・§7.2 末の C2 の段を表 4 の参照と 1 文に・related の後ろの 1 文を消す。
  - 自信: 高
- [minor] 7 抄録 348 語の入れ子の但し書き
  - 位置: abstract.tex l.12–17。"main penalty" が未定義・登録と探索の 2 系統が 1 段に。
  - 解消: 閾値の語を消し、探索は "stronger attackers tried afterwards raised these forms to 48–62\%" の 1 文に。ENJA は 1 文に。250 語前後。
  - 自信: 中
- [minor] 8 R3-u の低い値が強めた攻撃者を当てていない値であることが §8.3 で読めない
  - 位置: discussion.tex l.67–69 "only merging the separators, coarsening the segment values or suppressing at least a quarter of the presses brought the strongest attacker below 40\%, and of the coarsened and suppressed forms only R4(8) and R7(0.5) stayed there against the exploratory attackers"
  - 解消: "(R3-u was not run against them)" を 1 句。
  - 自信: 高
- [nit] 9 introduction.tex l.48–50 "though not exploratory attackers tried after these results" の否定の対象が曖昧 → 1 の書き直しで消える。
- [nit] 10 ai-use.tex l.10 "(\S\ref{sec:data:checks})" が付録（appendix-checks.tex l.8）を指す → data.tex の点検の段を指す。自信 中。

## 5. 推奨: major
見出しの主張が論文自身の全員の結果で崩れ、本文から辿れない。探索の後の前線が図表・§8.3 から読めず、効用の軸が質との関係の崩れを隠す。どれも新しい計算なしで直せる。

## 6. 読めなかった範囲・注入の疑い
接地の本文は grep の周辺だけ。付録の多く・generated の多く（windows・negative・open-world ほか）・事前登録・ハンドブックは読んでいない。utility の表の列の並びは推定。一覧の外の outline.md の 1 行が grep の結果に出たが根拠に使っていない。注入の疑い: なし（borgman の "(DO NOT DELETE)" は組版の残り）。
