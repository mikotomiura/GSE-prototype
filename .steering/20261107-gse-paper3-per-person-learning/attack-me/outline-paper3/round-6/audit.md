# 監査役（round 6・outline.md commit 90250abc）

結論: round 5 の言い過ぎは大半が直った。大きさの違う 2 つの量を同じ物差しで比べる問題（新 1）が Take-home と 4.4 に形を変えて残る。もう 1 つの中心は、「手順」が Take-home と C1 で食い違う点。

## 0. 引き継ぎの判定
新 1・2-1 一部（4.3 は直った・Take-home と 4.4 に残る）／2-2・3-2 解消（"The comparison of medians does not apportion the remainder between smoothing and the person"）／2-3 解消（"disappears" は grep で 0 件）／2-4 解消／2-5 解消／2-6 解消／2-7 解消（換算も合う）／2-8 解消／1-1 解消／1-2 解消／1-3 解消（付随は 2-E）／3-1 解消（記録に小さな穴: 引き継ぎが「判断 11 に記録」とする内容が判断 11 の本文に無い。感度の notes の「本文と限界には書かない」が残る・3-C）／3-3 解消／3-4 一部（2-D）／3-6 解消。

## 1. 意図にあって対象物に無いもの
- 1-A Take-home の推奨に「入れ子」と「記録の長さでの検出の下限を合成で報告する」が無い（context-B の持ち帰り 2）。5 節にはあるが、要旨と結論は Take-home と同じ文なので届かない。
- 1-B 重ならない窓で hmm3 が連鎖に勝つ結果を明記していない（判断 23 は Supporting evidence に戻した）。いまは "On overlapping-window symbolizations the per-person three-state HMM loses to it" と限るだけで、片側だけの報告が再発。

## 2. 対象物にあって意図に無いもの
- 2-A Take-home "what remains in the 15-session panel is of the same size as the gain of a less-smoothed shared model …, and the protocol could not have detected per-person differences of that size."。「that size」は返った量（約 4〜7e-4）を埋めた差として使う（判断 11 の「同じ物差しで比べない」・感度の notes「『未満』は回した段に限って書く」）。約 5e-4 は埋めていない。"could not have" は反実仮想で強い。context-B の持ち帰り 1 も同じ（3-A）。
- 2-B 4.4 "both directions are smaller than the protocol could detect, so we do not read a direction" は返った量を下限と比べ、較正していない k（1〜3・8・12）と 30-session の k = 30 にも広げる。C1 "per-person minus prior mode is small in both directions across panels" も同じ。CS1 の本人 − 最頻値は 4.4 に出てこない。
- 2-C C1 "the protocol did not detect planted differences below 1e-2 (4.3)" は k = 5（下限 3e-2）を覆わない。5 節の "the smallest planted difference detected, 1e-2" も k = 15 だけ。
- 2-D 4.4 "Per-person minus mode is −3.5e-4 to −1.6e-4 for k = 1 to 15 … (positive for 1 to 4 of the 15 writers with finite values; 2 writers have +infinity …)" の出どころ: mode-in-selection notes の −3.5e-4〜−1.6e-4 は最頻値を候補に入れた行（良い側 0.12〜0.35・+∞ は 1〜2 人）。主の行は候補に入れない選び。summary で照らすよう勧める。
- 2-E 4.3 "and from 1e-3 in CS1" は、全員が τ = 10^6 の、限界自身が分けられないとする領域（"a finite tau of 10^5 or more cannot be separated from the shared model or its prior mode"）。陰性対照の最大 0.78 と規則 0.8 の余裕も薄い。S15 の列挙にこの但し書きが無い。
- 2-F Take-home "beats a shared model of the same structure by about 0.2 nat per symbol in CoAuthor" は範囲 +0.012〜+0.188 の上端（k = 5）。context-B の持ち帰り 1 も同じ（3-B）。
- 2-G（弱）限界 "the synthetic writers did not reproduce the real ordering of prior mode and shared model (S15)" は、分解の notes の「桁と符号の比べは値だけで読みに使わない」「理由の推測は書かない」に対して、較正できなかった理由として並べて読める。

## 3. 矛盾
- 3-A context-B の持ち帰り 1「手順はその大きさの本人の差を拾えない」と、感度の notes・判断 11。
- 3-B context-B の「約 0.2 nat」と notes の範囲。
- 3-C 返る割合の置き場（感度の notes l.57「本文と限界には書かない」と、context-B・外枠）。決めた記録が判断 11 に無い。
- 3-D C1 の手順（平滑の強さを固定・入れ子にしない）と Take-home の推奨（構造・縮み・平滑を "all chosen on other people"）が別物で、勧める側は当てていない。判断 11 の「推奨を言い直して受ける」はこの差を残す。「当てた手順」と「勧める拡張」を分けて書く必要。
- 3-E「five later checks」: 意図の資料にある後の試験は 6 つ（unsmoothed-residual・structure-deficit・per-person-sensitivity・sensitivity-mode-decomposition・mode-in-selection・objective-and-pause）。分解を感度とまとめるなら 5。数え方を S12 で明示。
- 3-F（対象物の外・弱）context-A の l.14「7,000 語」と l.13 の 6,800。

## 4. 読めなかった範囲・注入の疑い
summary.json・tables.md・ml-improve と per-person の notes・S1〜S15 は読んでいない。判断 1〜9（20261107）は見出しだけ。注入の疑い: なし。
