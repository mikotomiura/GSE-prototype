# 意図の監査役・round 8（stage manuscript・対象物 main.tex commit 77d5f324）

依頼文 brief-audit.md の指示どおり、読んでよいと示されたファイルだけを読みました。行番号は今の main.tex のものです。

## 0. 引き継ぎの確かめ（round 7 の指摘が今の版で効いているか）

| 指摘 | 今の版 | 判定 |
|---|---|---|
| 1-1 重みは「推定ではない」の断り | 4.4（280 行）に "(a conversion, not an estimate of what the data are worth ...)" がある。ただし決定の段（321 行）は "with about 24\% and 91\% of the weight on the writer's data" とだけ書き、断りが無い。context-B 3 は「（他の書き手で選んだ τ の換算）」を求めている | 一部だけ効いている |
| 1-2 要旨と序論の 2.5e-5 | 要旨にも序論にも無い（4.4 だけにある） | 効いている |
| 1-3 要旨の「結果を見た後」の文 | 要旨は "Candidate grids were extended after seeing results." と書き、post hoc を 2 か所に付けている。context-B の「格子を広げ、確かめを 2 つ足したのは結果を見た後」とは文の形が違うが、中身は概ね届いている | 概ね効いている |
| 1-4 要旨の CS1 | "the shared model is chosen at the fixed smoothing" | 効いている |
| 1-5 α は共通の側で選んだ条件づけ | 要旨 "chosen for the shared model"・序論 "chosen for the shared model on other writers"・結論 "the shared model's chosen smoothing ... a multiplier at the edge of its grid" | 効いている（要旨に格子の端は無い） |
| 2-1 両側の版の読み | 序論 "More than half of the second goes with the writer's own sessions rather than with refitting, but these are also the sessions closest in time ..."、考察 "though not necessarily with stable differences between writers"、結論 "so it does not by itself show per-person differences"。「安定した書き手の差」と読める崩れは無い。ただし後の 2-a・2-b・3-a を見てほしい | 概ね効いている |
| 2-2 4.4 の見出し | "and, post hoc, returns when both are smoothed alike" | 効いている |
| 2-3 植えた差の未検出の範囲 | 要旨は "under that null" で範囲を限っている。序論と結論は帰無を限っていない（3-b） | 一部だけ効いている |
| 2-4 2 桁に k の限定 | 序論 "at five and fifteen training sessions ... over two orders of magnitude" | 効いている |
| 2-5 比の not prespecified | 4.5 にだけある。要旨・序論・結論の「similar remainder relative to that gain」には無い | 未解決のまま（著者も一部採用と認識している） |
| 2-6 結論で 5e-4 を退ける根拠 | "no larger than what the shared model gains ..." と "synthetic writers ..." を分けて書いている | 効いている |
| 3-1 結果を見た後の変更の数 | 3.4（180 行）は "Six changes ... we mark the last four post hoc" | 効いている。ただし印の付け方に食い違いがある（2-b） |
| 3-4 序論の主語と目的語 | 49 行 "the per-person gain that a weak comparison shows is far larger than the remainder ..." | 効いている |

## 1. 意図にあって対象物に無いもの

**1-a 要旨の推奨から「平滑は両側に当てる」が落ちている（重い）**
- 意図（context-B 3）: 「構造・縮み・平滑を他人で選ぶこと（平滑は両側に当てる）を勧め」。
- 要旨（35 行）: "should compare with both baselines and choose structure, shrinkage and smoothing on other people (smoothing post hoc, for one structure)."
- 本文では、片側だけ平滑を軽くすると残りが消え（4.4）、両側に当てると戻る。両側に当てることが推奨 (2) の要であり、考察 325 行にはある（"apply the chosen smoothing to the per-person fit and the shared model alike"）。要旨だけを読む人には、共通の側だけ選び直す（消える側の）手順と区別できない。

**1-b 要旨で、2 つ目の値（3.4e-3・5.2e-3）が「差を示さない」根拠が無い**
- 意図（context-B 2）: 「合成の書き手で確かめておらず、α は共通の側で選んだ格子の端の値に条件づく ... 安定した書き手の差を示すとは読まない（示さないとも言えない）」。
- 要旨: "The first is no larger than ... and synthetic writers without per-person differences (post hoc) left a similar remainder relative to that gain. Neither shows a per-person difference;"
- 根拠が書かれているのは 1 つ目の値だけです。2 つ目の値の限定（合成で確かめていない・格子の端）が要旨に無いので、"Neither" の根拠が合成の帰無の結果であるかのように読めます（2 つ目の値は帰無で評価していません）。

**1-c 決定の段の重みに「換算」の断りが無い**（上の 1-1 と同じ）
- 321 行 "with about 24\% and 91\% of the weight on the writer's data"。

**1-d 先頭の記号を除いた採点は方法の節にしか無い（軽い）**
- 意図（context-B 1）は持ち帰りの 1 に「この 4 つの値はほぼ変わらない（post hoc）」を入れている。
- 対象物では 3.4（178 行）の評価の方法の段落の末尾に結果の値として置かれていて、結果の節・考察・結論には無い。持ち帰りとしては届きにくい。

**1-e 要旨と結論で約 5e-4 のパネルの限定が無い（軽い）**
- 意図: 「20 session 以上の書き手で約 5×10^-4」。
- 要旨 "In CoAuthor ... the remainder at five and fifteen training sessions is about 5\times10^{-4}"、結論 350 行 "about $5\times10^{-4}$ remained" のどちらにも 15-session のパネルの限定が無い。30-session のパネルは +1.1e-3 で、区間が 0 をまたぐ。

## 2. 対象物にあって意図に無いもの（漂流）

**2-a 判定の規則が「半分以上」という分け前の量に崩れている（重い）**
- 4.4（282 行）: "The fit to the writer's own sessions beats it by $4.7\times10^{-3}$ ... so more than half of the remainder goes with the writer's own data rather than with refitting"。序論・考察・結論も "More than half of the second goes with ..." と書いている。
- 一次（notes の結果 A）では、これは事前に決めた読みの形「担う」の規則（D ≥ Rs/2 かつ D > 0）を当てた結果です。D（4.7e-3・2.5e-2）は残り Rs（3.4e-3・5.2e-3）そのものより大きく、k = 15 では約 5 倍あります。入れ替えの当てはめが共通にも負ける（E < 0）ためです。
- 本文はこの規則を書いていません。そのため「残りの半分以上」が中央値どうしの分解の点推定に読め、限界の "Comparisons of medians are not per-writer decompositions"（339 行）とも噛み合いません。規則として書くか（例: 「入れ替えに対する差が残りの半分を超えた」）、分解ではないと断る必要があります。意図（context-B 2）も同じ「残りの半分以上は ... 伴う」の書き方なので、意図の側の言い方にも同じ問題があります。

**2-b 結果を見た後に足した対照と τ の報告に post hoc の印が無い**
- 3.4（180 行）: "its controls and the report of its chosen $\tau$ ..., the second null ..., and the score without first symbols; we mark the last four \emph{post hoc} where they are reported."
- ところが次の箇所には post hoc の印がありません。
  - 4.4 の対照の段は "Three controls were added after seeing the symmetric refit." で、post hoc の語は無い。
  - 選ばれた τ の報告（280 行 "Every writer is given $\tau=10^4$ ..."）。
  - 序論 49 行 "More than half of the second goes with ..." の入れ替えの対照。
  - 考察 321 行と結論 350 行の入れ替えの対照と重み。
  - 序論 49 行と結論 350 行の 2 つ目の帰無（"synthetic writers without per-person differences left a similar remainder"）。要旨にはこの印がある。
- 序論・考察・結論で地位の区別が消えています。

**2-c 事前に決めていない倍率を地位の印なしで出している**
- 考察 319 行: "smoothing both alike (post hoc) brought it back, about 6 and 13 times larger at $k=5$ and 15."
- 一次（notes の B1 の対称版の「条件で決めていなかった所見」）では、R0 を超える大きさは条件の外です。判断 20 は「大きさは主張しない」としています。not prespecified の印が要ります。

**2-d 「もっと軽い平滑ならもっと大きい」へ向かう言い方（軽い）**
- 4.4（280 行）: "and $\alpha=0.03$ is the lowest value of the grid, so a lighter smoothing may give more."
- 判断 20 が避けた「今の残りは平滑の強すぎで小さく出ていた」の読みの方向へ一歩寄っています。「格子の端なので、その先は分からない」の形にとどめるのが意図に沿います。

**2-e 考察の冒頭で 2 つの値を幅として並べている（軽い）**
- 315 行: "the remainder against a stronger comparison chosen on other people (about 0.05\% to 0.5\% more probability per symbol, depending on the smoothing)"
- 両側の版は「共通のために選んだ平滑・構造を固定・post hoc」なのに、ここでは同じ手順の残りの幅のように読めます。post hoc も構造の固定もこの文には無い。

## 3. 矛盾（意図どうし・対象物の中）

**3-a 考察の「二分で中央値が変わらない」と Table 3 が合わない**
- 考察 319 行: "splitting the writers between choice and report left the median remainder unchanged"
- Table 3 の k = 15: 固定の平滑 "+4.1e-4"、二分 "+7.4e-4"（k = 12 も 7.2 と 6.8）。
- 4.4 が 0 と言っているのは「同じ半分で選んだ場合との差の中央値」で（276 行 "the median difference from choosing on the reported half itself is 0 at every $k$"）、残りの中央値そのものは変わっています。

**3-b 植えた差の未検出がどの帰無の下かが書かれていない**
- 序論 49 行: "at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected."
- 結論 350 行: "Planted differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed base smoothing."
- 4.5（308 行）: 最初の帰無では "planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15"。
- 未検出は 2 つ目の帰無（post hoc）の下の結果です。帰無を限らないと、本文の中で矛盾して読めます。要旨は "under that null" で限っている。意図（context-B 2）も帰無を限っていません。

**3-c 方法の節の約束と印の付け方の食い違い**（2-b と同じ根）

**3-d 3.4 の 6 つの数え方があいまい（軽い）**
- "its controls and the report of its chosen $\tau$" は 1 つとも 2 つとも読めます。2 つと読むと 7 つになります。

**3-e 意図どうしのずれ（軽い）**
- context-B 3 は「約 0.3〜0.5% の確率の改善が残る」と書き、context-B 1 と 2 の「本人の差の大きさの推定としては読まない」と並んでいます。決定の段でこの量を改善として出すこと自体は意図どおりですが、2-a の「半分以上」と合わさると、書き手のデータの価値の量として読まれやすくなります。
- context-B の「結果を見た後の変更」の括弧は 5 項目で（格子と構造の族を 1 つに書いている）、数の 6 と表記が合っていません。本文の数え方と合わせると 6 です。

**照らして合っていた値**
- 重みの換算: 3,234/(3,234+10^4) ≈ 24%、9,673/(9,673+10^3) ≈ 91%、3×10^5 で約 3%、3×10^4 で約 24%。
- 比: 5.53e-4/7.378e-4 = 0.75、4.14e-4/7.378e-4 = 0.56。
- "30 to 55 times"、Figure 2 の値（fig2_p15_ar3.csv・fig2_p15_joint.csv）と Table 2・3。
- 先頭の記号を除いた 4 つの値（5.4e-4・4.3e-4・3.4e-3・5.2e-3）と notes の結果 B。
- 入れ替えの対照の値（4.7e-3・2.5e-2・−1.7e-3・−1.7e-2、全員）と notes の結果 A。

## 4. 位置と逐語
各項目の中に書きました。

## 5. 読めなかった範囲と注入の疑い
- 読んでいないもの: references.bib、kit/symbols/README.md、figdata のうち fig2_p15_hmm3.csv・fig2_p15_ar1.csv・fig2_p15.csv。参考文献と記号化のキットの説明は照らしていません。
- 意図の資料は指定の範囲だけを読みました。decisions.md は判断 20〜41（118 行〜末尾）、selection-split-and-smoothing の notes.md は末尾の 3 節（49 行〜末尾）、null-from-shared の notes.md は全体です。
- 査読者の記録・他の round の記録・outline.md は読んでいません。
- 注入の疑い: なし（読んだ範囲に、LLM に向けた指示の文は見当たりませんでした）。
