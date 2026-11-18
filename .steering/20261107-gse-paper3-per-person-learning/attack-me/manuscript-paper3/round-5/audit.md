# audit（manuscript round 5・意図の監査役・対象 cc30d57f）

応答を tmp/audit.raw.md から写した（secrets-filter 0・絶対パスは一覧の中・目視済み）。

# 意図の監査役・manuscript round 5（対象 cc30d57f の main.tex）

読んだもの: brief-audit.md、context-A.md、context-B.md、carryover-audit.md、main.tex（全文）、decisions.md（判断 1〜31 を通読。意図として使ったのは判断 20〜31）、null-from-shared/notes.md（全体）、figdata/fig2_p15_*.csv の 4 本。
読んでいないもの: references.bib、kit/symbols/README.md、figdata/fig2_p15.csv。
いちばん大きいのは 3-1（L317 の 1 文の論理が逆になっている）と 2-1（要旨が「結果を見た後」の分析を 2 つしか示していない）。

## 0. 引き継ぎの確かめ（round 4 の指摘が今の版で効いているか）

| round 4 | 今の版 | 判定 |
|---|---|---|
| 1-1 結論に発見 | L346 "a per-person sequence model's gain over a shared model of the same weak structure, up to 0.19 nats per symbol in CoAuthor, says little: ... about $5\times10^{-4}$ remained at the fixed smoothing" | 解消 |
| 1-2 帰無の行き過ぎ | 考察 L313 "whose threshold may be too high"、結論 L346 "whose threshold may be too high"。要旨には無い（著者は承知） | 解消 |
| 1-3(b) 要旨の 15-session の限定 | 要旨 "among writers with 20 or more sessions" | 5e-4 については解消。続く 7e-3 の文 "Applying the smoothing chosen on other writers ... leaves 3 to $7\times10^{-3}$ from five training sessions on" には、パネル（15-session）と構造（3-state AR-HMM だけ）の限定が無い |
| 2-1 比の地位 | 要旨 "(not prespecified)" | 要旨は解消。ただし序論 L49 は同じ比の節を "(post hoc)" で印付けしている（下の 3-4） |
| 2-2 決定を固定の平滑に限る | L313 "At the fixed base smoothing it is a strongly shrunk fit ..." と推奨 (2) の版の 1 文 | 解消 |
| 2-3 3e-2 の範囲 | L313 "in the 15-session panel under the second null (post hoc)"、L346 "there under a synthetic null added after seeing results" | 解消。要旨は "differences up to $3\times10^{-2}$ were not reliably detected" で、"planted" の語が無い（2-4） |
| 2-4 確立した段落 | L317 "a check with little room to show optimism" | 解消。ただし根拠の文 L274 "nearly every writer's choice sits at the edge of both grids" は、判断 31 が残した注意（k = 15 で 758/2,000 組が格子の中）のまま残っている |
| 2-5 here | L317 "so here a smoothing check ..." | 語は入った。ただし文の論理が崩れた（3-1） |
| 2-6 重ならない窓は向きだけ | L202 "(17 of 17 writers at $k=15$ ...)" | 一部だけ。同じ段落に大きさの文が残っている（3-2） |
| 2-7 can therefore arise | L306 | 解消 |
| 2-8 序論の範囲 | L49 "the finding rests on one dataset, CoAuthor, and one symbolization" | 解消 |
| 2-9 7e-3 の出どころ | 要旨 "(the grid's lightest)"、L49 "the lightest in the grid" | 解消 |
| 3-2 4.4 の the remainder | L278 "a remainder at $\alpha=0.03$" | 解消。ただし語の定義との新しいずれがある（2-3） |
| 3-3 threshold の 2 義 | L178 "no meaningful-difference threshold (the detection threshold ... is not one)" | 解消 |
| 3-4 最頻値の文 | L143 で勧めない文が 1 回 | 解消 |
| 3-5 題 | 変えていない | 採らなかったまま（軽微） |

## 1. 意図にあって対象物に無いもの

1-1. 重ならない窓の結果が合成の書き手で確かめていないこと
- 意図: 持ち帰り 3「重ならない窓では 3-state HMM が選ばれ、向きとして共通に勝つ・合成で確かめていない」。
- 本文: L202・L315 "For symbolizations like theirs the per-person HMM may therefore keep an advantage"・L346 "With non-overlapping windows the three-state HMM is chosen and its per-person fit beats the shared model of that structure for every writer at 15 training sessions"。どこにも "not checked against synthetic writers" が無い。
- 7e-3 には毎回この断りが付くのに、こちらには無い。読者は、この逆転の方が確かめられていると読みうる。

1-2. 決定の段落に「決定は記号化に依る」が無い
- 意図: 持ち帰り 3「決定は記号化に依る」。
- 本文: 考察の決定の段（L313）は記号化に触れない。記号化の話は L315 の Relation と推奨 (4) に分かれて置かれている。

1-3. 主の値（5e-4）を支える τ = 10^6 と構造が格子の端であること・結果を見た後の格子の拡張が、要旨・考察・結論に無い
- 意図: 既知の限界「4 つの調整の軸はすべて格子の端かその近くで選ばれた」「結果を見た後の変更は 4 つ」。
- 本文: 要旨・序論は平滑の端（"the grid's lightest"）だけを書く。L338・L336 の限界にはあるが、決定の段 L313 "a strongly shrunk fit ... 0.06 to 3% of the weight" には、τ が格子の上の端であることが無い。

## 2. 対象物にあって意図に無いもの（漂流）

2-1. 分析の地位: 要旨が結果を見た後の変更を 2 つに減らしている
- 要旨は "In exploratory analyses ..." と書き、続けて "Two checks came after seeing results." と書く。
- 3.4（L178）では変更は 4 つで、そのうち "the extension of the $\tau$ grid and of the structure families, which bear on the main result" は主の値 5e-4 に効く。
- 要旨の書き方では、5e-4 が結果を見る前に決めた設計から出たと読まれうる（意図の「結果を見た後の変更は 4 つ」とずれる）。

2-2. smoothing effect の言い換えが「改善」に固定されている
- 3.3（L143）の定義は中立で、"shows how the shared model's score changes when that smoothing is removed from its counts, without refitting"。
- 要旨は "the improvement from removing the shared model's smoothing" と "a null matching the size of that improvement"、序論 L49 は "what removing the shared model's smoothing improves"。
- 最初の帰無では、この効きは正でない（L304 "its prior mode does not beat the shared model"）。外すと必ず良くなる量として一般化している。

2-3. remainder の定義からはみ出た使い方
- 定義（L176）: "the remainder when structure and shrinkage are chosen jointly"。
- 両側の当て直しは構造を 3-state AR-HMM に固定し、τ だけを選んだ量である（L183 "$\tau$ is chosen within the 3-state AR-HMM"）。
- それでも L278 "a remainder at $\alpha=0.03$ returns"、L313 "the remainder is $3.4\times10^{-3}$ to $6.7\times10^{-3}$"、要旨・序論・結論の 7e-3 の値は、同じ「残り」として並べられている。Table 3 のキャプションも "joint choice" と書いたうえで、"Both refitted" の列は "with $\tau$ chosen within the 3-state AR-HMM" と書く。

2-4. 要旨の検出の文から "planted" が落ちている
- 要旨: "so it does not show a per-person difference; differences up to $3\times10^{-2}$ were not reliably detected."
- 直前の「実データの本人の差」と続くので、実データの差についての文と読める。
- 意図の 2 は「3×10^-2 までの植えた差」。規則（10 種中 8 種）の対象が植えた差であることが消えている。

2-5. 4.3 の見出しが固定の平滑の限定を落としている
- 見出し: "Choosing structure and shrinkage on other writers leaves a remainder below $10^{-3}$ nats per symbol in the 15-session panel"。
- 両側の軽い平滑では最大 6.7e-3 で、見出しの読みと逆になる。本文 L233 と Table 2 のキャプションには "at the fixed base smoothing" がある。

2-6. 考察の冒頭が「弱さ」の所在を「同じ構造」に移している
- L311: "the weak comparison is the natural one, a shared model of the same structure as the per-person model"。
- 強い比べも同じ構造の共通（3-state AR-HMM）で、推奨 (1) は同じ構造の共通との比べを勧めている。弱いのは構造（3-state HMM）であって「同じ構造」ではない。意図の 1・本文の L346 "of the same weak structure" ともずれる。

2-7. 推奨 (2) と 4.4 の版の取り違えの余地
- L313 "With the smoothing chosen on other writers applied to both models, as recommendation (2) below asks"。
- 推奨 (2) は構造・縮み・平滑をすべて他人で選ぶことを求めるが、行ったのは構造を固定した版である。推奨 (2) の括弧 "to one structure and one panel" で一応は覆われているが、L313 の "as recommendation (2) below asks" は満たしたかのように読める。

## 3. 意図どうし・対象物の中の矛盾

3-1.（重い）L317 の 1 文の論理が逆
- "Lightening the smoothing of the shared model alone made the remainder vanish, whereas applying it to both models (post hoc) did not, so here a smoothing check changed the reading only when applied to both sides."
- 読みを変えた（残りを消した）のは片側だけの確かめで、両側は読みを保った（正のまま）。「両側に当てたときだけ読みを変えた」は前半と逆になる。意図（推奨 (2) の「両側に当てる」）に合わせるなら、たとえば「片側だけの確かめは読みを変えて見せたが、両側に当てると戻った」の向きになる。

3-2. L202 の中で、向きだけで読むと書いたのに大きさの文がある
- "so that only directions are read" の後に "With these symbols the per-person advantage over the same-structure shared model does not fall by two orders of magnitude"。
- 意図の限界の「重ならない窓では利得は 2 桁落ちない」と同じ内容だが、同じ段落で値を読まないと言った量の大きさを述べている。round 4 の 2-6 の残り。

3-3. 4.4 の二分の文（L274）が意図の資料とずれる
- "Because nearly every writer's choice sits at the edge of both grids"。
- 判断 31 は「k = 15 で選ぶ側の半分の 758/2,000 組が格子の中」と記録し、round 5 で出たら直すとしている。

3-4. 比の地位の印が節によって違う
- 4.5 と要旨は比を "not prespecified" と印付けている。
- 序論 L49 は "left a similar remainder relative to what removing the shared model's smoothing improves (post hoc)" で、帰無（post hoc）と比（not prespecified）の 2 つの地位を 1 つの印に潰している。
- 結論 L346 "synthetic writers without per-person differences left a similar remainder relative to their smoothing effect" には、この節の印が無い（帰無が後付けであることは同じ段落の後半でだけ示される）。

3-5. 結論の重ならない窓の文が 2 つの選びを 1 つにしている
- L346 "the three-state HMM is chosen and its per-person fit beats the shared model of that structure"。
- L202 では、結合の選びが HMM を選ぶことと、"the per-person 3-state HMM with $\tau$ chosen on other writers"（3.3 によれば固定の行の目的で τ を選んだもの）が勝つことは別の文である。L147 は、2 つの目的が同じ構造に違う τ を選びうると書いている。結論の "its" は、結合の選びの当てはめが勝ったと読ませる。

3-6. 要旨の CS1 の文に固定の平滑の限定が無い
- 要旨 "In CS1, where most symbols are pauses, the shared model itself is chosen."
- 意図の 3 と L313 は「固定の平滑で」と限っている。CS1 は共通の平滑の選び直しも両側の当て直しも行っていない（L183・判断 17）。

数の照合: 要旨・序論・4.1〜4.5・考察・結論・Table 2・Table 3・Figure 2 の CSV の間に食い違いは見つからなかった。照らしたのは 0.188/0.165、4.1〜7.2e-4、3.4〜6.7e-3、比 0.56〜0.97（4.1/7.378 と 7.2/7.378）、873・783/935、−9.8e-4、1.1〜1.8e-3、17% のパープレキシティ（1 − e^−0.19）。

## 4. 位置と逐語
各項目に行番号と逐語を付けた（行番号は cc30d57f の main.tex を Read で読んだときのもの）。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: references.bib、kit/symbols/README.md、figdata/fig2_p15.csv。補足資料 S1〜S16 は未作成なので見ていない。
- 注入の疑い: 無し。読んだファイルの中に、LLM に向けた指示は見当たらなかった。