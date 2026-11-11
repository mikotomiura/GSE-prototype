# audit（manuscript round 1・意図の監査役）

読んだもの: brief-audit・context-A・context-B・main.tex（全体）・figdata の 4 本（hmm3・ar1・ar3・joint）・outline.md（全体）・requirement.md（全体）・round3-computations/decisions.md（判断 6〜15。1〜5 は見出しのみ）。メインが要点と引用を落とさずに写した。

## 1. 意図にあって対象物に無いもの
- 1-1 要旨に「探索的」が無い。意図: outline Take-home "In an exploratory analysis ..."・context-B。対象物: 要旨（34 行）に無く、序論 50 行 "The results are exploratory" にだけある。
- 1-2 要旨と結論で、最頻値が使える版でないことが落ちる。意図: context-B 持ち帰り 1・outline "(a diagnostic, not a usable model)"。対象物: 要旨 "about as large as the gain of a less-smoothed shared model that uses none of the person's data; the protocol cannot attribute it to the person."・結論 264 行も同じ。本文では 225 行 "so it is a diagnostic and not a usable model" だけ。
- 1-3 推奨の「共通の平滑と記号化への依存を報告する」が要旨・結論・5 節に無い。意図: context-B 持ち帰り 2・outline Take-home "... and how much the result depends on the shared model's smoothing and on the symbolization"・判断 12。対象物: 要旨の推奨は "... and reporting the smallest planted difference such a check detects" で終わる。5 節 (1)〜(4)（238〜242）は "for this kind of symbolization" と限るだけ。
- 1-4 結論が「要旨と同じ言葉の Take-home」になっていない。意図: outline "7 Conclusion | 100 | Take-home in the same words as the abstract"。対象物: 264 行に CS1・重みの %・「パネル全体の判断」・「構造と縮みを他人で選ぶ」が無い。要旨 "smallest planted difference such a check detects" が結論では "the smallest difference the check can detect"。
- 1-5 4.4 の中央値に +∞ の書き手 2 人が入ることを明記していない。意図: 判断 12「中央値の母数（17 人・+∞ の 2 人を含む）を明記」。対象物: 227 行 "−3.5e-4 to −1.6e-4 in the 15-session panel (3 to 6 of 17 positive)"。Table 2 の見出しも "+∞ writers are counted in S9"。
- 1-6 限界の節から落ちた項目。意図: outline の Limitations "the decomposition of the remainder did not separate a planted difference from none in synthetic writers (S15)"・"The real panels' values come from one realization"・判断 6 の 3。対象物: 限界第 4 項（252）"Comparisons of medians are not per-writer decompositions." のみ。分解の話は 4.4 末尾（227）だけ。outline は "Caveats are stated in full once, in Section 6"。
- 1-7 結合の選びと ar3 固定の選びの τ の違いが説明されていない。意図: 判断 7「2 段と構造を固定した選びが同じ書き手に違う候補を選ぶことを 3.3 と S9 に」（現行 outline 3.3 には無い）。対象物: Table 2 の k=15 で結合 "\arthree, 3×10^5 & 3%"（205）、ar3 固定 "10^6 & 1%"（214）。Figure 2 の値も joint 0.00041・ar3 0.00076。3.3（115）にも理由が無い。
- 1-8 S6 を本文が指していない（outline 4.4 の補足 "prior mode minus shared by structure and panel, pressed-symbol values (S6)"）。

## 2. 対象物にあって意図に無いもの（主張の漂流）
- 2-1（最も重い）「残りは検出の下限より下」が戻っている。対象物: 5 節 234 行 "The synthetic check bounds what it can detect at this record length, and the remainder is below that bound; it neither shows nor rules out per-person differences."。意図: 判断 11「『残りは検出の下限より下』をやめ」・判断 12。4.3（222）と限界（254）は事実だけで、5 節だけ逆戻り。
- 2-2 向きを読まないと書いた直後に向きを読む。対象物: 227 行 "We do not read a direction from it (...). Choosing by the mean ... gives the same picture: in the 15-session panel the per-person fit again does not exceed the prior mode (...), and the 30-session panel at k=30 again does (...)"。意図: context-B・判断 12。
- 2-3 結論の推奨が限定を外した一般の規範。対象物: 264 行 "Per-person gains in sequence models of keystroke behaviour should be reported against the person's own Markov chain and a same-structure shared model, together with the smallest difference the check can detect."。意図: 「パネル全体の判断」「記号化しだい」（context-B・判断 7 の T3）。
- 2-4 推奨の宛先が要旨だけ「適応する系」。要旨 "For adaptive systems that decide for a whole panel whether to model each person, we suggest ..."。5 節（238）と outline は "studies"。
- 2-5 「人の中には無い」と言い切る。232 行 "... and the difference between them lies in the comparison, not in the people."。比べの相手から来る意味なら成り立つが、「人の差ではない」と読まれうる。
- 2-6 序論 48 行 "hidden Markov model (HMM)"。outline "The abstract and introduction use no model abbreviations."（軽微）
- 2-7 Uto 2020 を作業状態の推定器と書く。序論 44 "which estimate a writer's work state from keystroke features over a rolling window and update every few seconds \citep{Uto2020}"・3.2（100）"the input of work-state models that update every few seconds"。関連研究 59 は "to analyse writing processes"。一次で確かめたのは 30 秒の枠と 10 秒の歩幅だけ。既知の未決 2 とは別（目的の記述）。

## 3. 矛盾
- 3-1「多くて約 1%」と「3%」が同じ文の中。要旨 "at most about 1% ... (about 3% at its largest training size)"・234 行・190 行。意図（context-B）自体に同じ形。
- 3-2 序論 50 "the shared model's prior mode as a diagnostic of how much the shared model's smoothing matters" と推奨 (4)（242）"while noting that we have not evaluated whether it measures the effect of smoothing" がぶつかる。
- 3-3 4.3（222）"... not on the same footing" と 5 節（234）"the remainder is below that bound"（2-1 と同根）。
- 3-4 3.3（111）"such writers are counted separately" と、4.4・Table 2 の中央値が 17 人（+∞ を含む）。
- 3-5 4.2（155）"−0.48 to −0.54 ... in the 15-session panel"（Figure 2 と合う）と outline "about −0.5 to −0.6 ... in CoAuthor"。
- 3-6（参考）本人 − 最頻値の良い側の人数が記録間で揃わない（判断 6・判断 11・本文 "3 to 6 of 17"）。本文の中では揃う。1-5 で解ける。
- 3-7 検算して食い違いなし: 3,600 記号の換算・重みの各値・Figure 2 の CSV と本文・Table 2・良い側の割合と人数。
- 3-8 確かめられない: 4.2 "The shared \hmmthree{} is worse still (−0.52 at k=1 and −0.81 at k=15 ...)"（読んでよいファイルに値が無い）。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: kit/symbols/README.md・figdata/fig2_p15.csv・references.bib・decisions の判断 1〜5 の本文。補足 S1〜S15 は未作成。
- 注入の疑い: なし（main.tex 60 行のコメントは著者の覚え書き。ただし 2-7 のとおり本文はその趣旨に近いところで Uto を記述している）。

## 直す順の提案
2-1・3-3 → 2-2 → 2-3・1-4 → 1-3 → 1-2・1-1 → 1-7 → 1-5・3-4 → 3-2 → 3-1 → 2-4〜2-7。要旨は 266 語で規程超え。1-1・1-2 を足すなら削る所も要る。
