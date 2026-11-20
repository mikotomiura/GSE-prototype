意図の監査役の報告（round 10・stage manuscript・対象 commit c87c7d63 の main.tex）

読んだもの: brief-audit.md、context-B.md、context-A.md、carryover-audit.md、main.tex（全文）、decisions.md の判断 20〜43、experiments/20261113-null-from-shared/notes.md（全文）、experiments/20261112-selection-split-and-smoothing/notes.md の末尾の 3 節（49 行目から最後まで）。
読んでいないもの: references.bib、figdata の CSV 5 つ、kit/symbols/README.md、selection の notes.md の 1〜48 行（指定の範囲の外）。このため Figure 2 の値と本文の値の照合、参考文献の照合はしていません。

## 0. 引き継ぎの確かめ（round 9 の指摘に対する今の版の対応）

- 1-1（入れ替えの対照が要旨にも序論にも無い）: 著者の方針どおり。要旨は "its source (the writer, closeness in time or the amount of data) was not separated" と書き、入れ替えの対照は 4.4・考察・結論にある。残る問題は下の 2-5 に書いた。
- 1-2（要旨の post hoc の印）: 効いている。要旨の "(post hoc)" は 2 つ目の帰無・両側の当て直し・推奨の 3 か所にある。ただし残りと平滑の効きの「比」には印が無い（下の 2-1）。
- 1-3（結論の交絡にデータの量）: 効いている。"whether this reflects the writer, closeness in time or the amount of data was not separated"。
- 1-4（要旨の「必要だが満たせなかったもの」）: 著者の方針どおり入っていない。推奨 (3)(4) は考察にだけある。
- 2-1（要旨の goes with）: 効いている。
- 2-2（2 つ目の帰無の初出の post hoc・強い縮みは 2 つ目の帰無だけ）: 効いている。3.6 は "The second null (post hoc)"、考察は "synthetic writers of the second null (post hoc), with and without planted differences, were given similarly strong shrinkage"。
- 2-3（要旨の検出の平滑）: 効いている。"at the fixed base smoothing, planted differences up to 3×10^-2 were not reliably detected under the post hoc null"。
- 2-4（predicted state を休止の予測へ）: 効いている。"times hints by the predicted probability that the next seconds are a pause"。
- 2-5（4.3 の見出し）: 効いている。"... below 10^-3 at the fixed base smoothing in the 15-session panel"。
- 3-1（考察の up to）: 効いている。"up to 0.19 nats per symbol"、"with up to 6.7×10^-3 at k=12"。
- 3-2: 2-2 と同じく効いている。

## 1. 意図にあって対象物に無いもの

1-1 要旨と序論に、5×10^-4 の範囲（20 session 以上の書き手・15-session パネル）が無い
- 意図（context-B の 1）: 「固定の平滑・重なる窓・20 session 以上の書き手で約 5×10^-4」。
- 要旨: "With a stronger structure and shrinkage chosen on other writers, about $5\times10^{-4}$ remains at five and fifteen training sessions at the fixed base smoothing"。序論: "With a stronger structure and shrinkage chosen on other writers, the remainder at five and fifteen training sessions depends on the smoothing: about $5\times10^{-4}$ ..."。
- どちらも直前の主語は "In CoAuthor" だけで、パネルを書いていない。30-session パネルの残り（"+1.1×10^-3 at k=30 ... with an interval spanning zero"）は平滑の効き 7.4×10^-4 を超えるので、範囲を書かないと、序論の "The first is no larger than the shared model's own improvement" が CoAuthor の全体に読める。結論は "in the 15-session panel" と書いているので、本文の中でもそろっていない。

1-2 「出力は推定ではなく群ごとの決定」が本文で一度もはっきり書かれていない
- 意図（context-B の 3）: 「プロトコルの出力は推定ではなく群ごとの決定で、記号化に依る」。
- 本文で最も近い文は、考察の "the protocol makes this trade explicit by deciding for a panel"、限界の "The choice uses one objective for a whole panel"、4.4 の "these checks guard the reading and do not estimate a per-person difference"。どれも「出力は推定ではない」という使う側への持ち帰りとしては書かれていない。"What the protocol returns" の段は、固定の平滑で示さないことと両側の版の値を並べるだけになっている。

1-3 先頭の記号を除いた採点（post hoc）が要旨・序論・結論のどれにも無い
- 意図（context-B の 1）: 「系列の先頭の記号を採点から除いても、この 4 つの値はほぼ変わらない（post hoc）」が持ち帰りの 1 に入っている。
- 本文では 4.4 だけ: "Scoring without the first symbol of each held-out sequence (post hoc) ... leaves the remainder ... at $5.4\times10^{-4}$ and $4.3\times10^{-4}$ ... and $3.4\times10^{-3}$ and $5.2\times10^{-3}$ in the symmetric refit"。語数の判断なら構いませんが、持ち帰りに挙げたものが本文の 1 か所にしか無いことは、意図と合っていません。

1-4 「比は差のある場合で見ていない」が本文に無い
- 意図（context-B の既知の限界）: 「2 つ目の帰無で植えた差の書き手も大半が τ = 10^6 に選ばれ、強い縮みの下では植えた差が残りを上げるとは限らない。比は差のある場合で見ていない」。
- 4.5 には前半だけがある: "synthetic writers were mostly given $\tau=10^6$, as in the real panel, and under such strong shrinkage a planted difference need not raise the remainder"。後半（残りと平滑の効きの比を、植えた差のある複製では見ていない）は、4.5 にも限界にも無い。比を読みの根拠にしている（下の 2-1）ので、主張に響きます。

1-5 両側の版について「否定もしない」が要旨と序論に無い
- 意図（context-B の 2）: 「安定した書き手の差を示すとは読まない（示さないとも言えない）」。
- 要旨の "Neither value shows a per-person difference; at the fixed base smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected" は、否定しない側を固定の平滑についてだけ書いている。両側の版の「示さないとも言えない」に当たる文は、考察の "though not necessarily because of stable differences between writers" だけにある。

## 2. 対象物にあって意図に無いもの（漂流・範囲を超えた言い方）

2-1 残りと平滑の効きの比の地位（not prespecified）が、要旨・序論・結論で消えている
- 意図（context-B の 2）: 「平滑の効きに対して同程度の残りを残した（比は not prespecified）」。
- 4.5 は印を付けている: "(0.75 and 0.56 at $k=5$ and 15; ratios of medians; not prespecified)"。
- 要旨: "synthetic writers without per-person differences (post hoc) left a similar remainder relative to that improvement"。序論: "synthetic writers without per-person differences (post hoc) left a remainder of similar size relative to that effect"。結論: "synthetic writers without per-person differences (post hoc) left a remainder of similar size relative to that effect"。
- 3 か所とも (post hoc) は帰無に付いているだけで、比べの量（比）が事前に決めた読みではないことが落ちている。5×10^-4 が「本人の差を示さない」根拠の片方はこの比なので、地位の区別が要旨の水準で消えている。なお、事前に決めた規則での結果（"the real panel is not detected at $k=5$ or 15"、4.5）は要旨にも序論にも無く、要旨は事前に決めていない比だけで「示さない」を支えている形になっている。

2-2 両側の版が決定に関わる理由（「固定の平滑では本人の当てはめが実質的に軽く平滑される」）が、序論では事実として書かれているのに、結果の節に裏付けが無い
- 序論: "whereas at the fixed base smoothing the strongly shrunk per-person fit is effectively less smoothed than the shared model it is compared with"。
- 意図（context-B の 1）はこの理由を挙げているので、それ自体は意図の中です。ただし結果の節（4.3・4.4）にこの文は無く、4.3 は "The chosen fit is then close to the shared model's prior mode, so the remainder may reflect how the shared model is smoothed" と may で書いている。意図の資料（null-from-shared/notes.md の所見 2）も「τ = 10^6 の本人の当てはめは ... 基の擬似度数の重みだけが薄まる ... 共通の基の平滑を薄めた効きと合う（... 推測）」と推測の印を付けている。決定に関わる比べを選ぶ理由が、本文では may の読みから断定へ強まっている。序論の 1 句を may の水準にそろえるか、4.3 で断定の根拠を示すかが要る。

2-3 要旨の推奨が、3 つを他人で一緒に選ぶように読める
- 要旨: "should compare with both baselines and choose structure, shrinkage and, applied to both models, smoothing on other people (post hoc, one structure)"。
- 考察の推奨 (2): "choose the smoothing on other people for the shared model, apply it to the per-person fit and the shared model alike and choose shrinkage given it (here done post hoc, for one structure and one panel, with the chosen multiplier at the edge of the grid; choosing all three jointly was not tried)"。
- 要旨は 3 つを並べるだけで、選ぶ順（平滑は共通のために選び、それを与えて縮みを選ぶ）と「3 つを一緒に選ぶことは試していない」が落ちている。round 9 で推奨 (2) の選ぶ順を直したが、要旨には届いていない。また "(post hoc, one structure)" が推奨全体に掛かるのか平滑の部分だけに掛かるのかが読めず、推奨そのものが post hoc と読める。

2-4 序論の "applied to both models alike" が、方法の断りと合わない
- 序論: "because there the smoothing is itself chosen on other writers and applied to both models alike"。
- 3.5: "Because $\alpha$ is chosen for the shared model, the symmetric refit is conditional on that choice, and the same prior counts weigh differently against a writer's few symbols and the other writers' many"。
- 意図（context-B の 2）も「α は共通の側で選んだ格子の端の値に条件づく」としている。序論の理由の句は、平滑が本人の側のために選ばれたものではないこと、同じ値でも効き方が違うことを落として "alike" と言い切っている。決定に関わる理由として書いた句なので、限定が要ります。

2-5 要旨の "its source ... was not separated or checked on synthetic writers" の言い方
- 要旨: "this bears on a designer's decision, but its source (the writer, closeness in time or the amount of data) was not separated or checked on synthetic writers"。
- 合成の書き手で確かめていないのは「値」であって「源」ではないので、文の組み方がずれている。また、要旨は入れ替えの対照に触れないので、"was not separated" は「分ける試みをしていない」と読める。本文（4.4）では、入れ替えの対照が「事前を k 単位で作り直しただけで残りが出る」ことを除いたうえで、残りの源を分けていない。要旨のこの句は、本文がしたことを過小に伝えています（1-1 で著者が入れないと決めた点とは別に、文の組み方の問題として挙げます）。

2-6 "far larger" の比べの相手が序論と考察で一致していない
- 序論: "the per-person \emph{gain} that a weak comparison shows is far larger than the \emph{remainder} ..."、続けて 5×10^-4 にだけ "over two orders of magnitude below the gain" を付けている。
- 考察: "is far larger than the remainder ... (about $5\times10^{-4}$ ..., and $3.4\times10^{-3}$ and $5.2\times10^{-3}$ ...)"。
- 両側の版では、利得との比は約 55 倍（0.188 / 3.4×10^-3）と約 32 倍（0.165 / 5.2×10^-3）で、1.5 桁ほどです。考察は 2 つの値を "far larger" の一つの括弧に入れており、「2 桁以上」が両方の値に掛かるように読まれうる。意図（context-B の 1）が「2 桁以上」を付けているのは 5×10^-4 の側だけです。

## 3. 意図どうしの矛盾・対象物の中の矛盾

3-1 範囲の不一致（1-1 と同じ根）
- 要旨と序論は 5×10^-4 をパネルの限定なしで書き、結論と 4.3 の見出しは 15-session パネルに限っている。結論 "the remainder in the 15-session panel depends on the smoothing" に対し、要旨 "about $5\times10^{-4}$ remains at five and fifteen training sessions at the fixed base smoothing"。

3-2 方法の定義と序論の理由の句（2-4 と同じ根）
- 3.5 の "the same prior counts weigh differently" と、序論の "applied to both models alike"。

3-3 重みの "24%" が 2 つの別の量に使われている（矛盾ではなく、読み違いの危険）
- 4.2: "At $k=15$, where the writer's data carry 24\% of the weight, it also beats the shared \arone{} by $+0.002$"（1-state AR-HMM・固定の平滑・k = 15）。
- 4.4 と考察: "about 24\% and 91\% of the weight on the writer's data"（3-state AR-HMM・両側の版・k = 5）。
- どちらも本文の値として正しいが、決定の段の 24% を 4.2 の行と取り違える読みが起こりうる。

照らした数（食い違いは無かった）: 表 2 の結合の選択の行（4.8e-4・5.5e-4・4.1e-4・1.1e-3）と 4.3 の範囲（4.1e-4 から 7.2e-4）。表 3 の両側の版（5.2e-4 から 6.7e-3）と selection の notes の Rs（+5.2e-4・+1.25e-3・+2.05e-3・+3.38e-3・+4.32e-3・+6.67e-3・+5.17e-3）。入れ替えの対照 D（4.73e-3・2.53e-2）と E（−1.68e-3・−1.73e-2）と 4.4 の値。先頭の記号を除いた値（5.37e-4・4.29e-4・3.45e-3・5.21e-3）と 4.4 の丸め。選ばれた τ と重み（10^4 で 0.24、10^3 で 0.91）。比（5.53e-4 ÷ 7.378e-4 ≈ 0.75、4.14e-4 ÷ 7.378e-4 ≈ 0.56）。2 つ目の帰無の閾（1.82e-3・1.83e-3）と本文の "rose to $1.8\times10^{-3}$"、陰性対照の範囲 1.1e-3〜1.8e-3。結果の後の変更が 6 つ・post hoc の印が後ろの 4 つ、という 3.4 の数え方は、context-B の 6 項目と合っている。

## 4. 位置と逐語

各項目の中に、節（要旨・序論・3.4〜3.6・4.2〜4.5・考察・限界・結論）と逐語を書きました。行番号（main.tex @ c87c7d63）の目安は次のとおりです。
- 要旨: 35 行
- 序論の貢献の段: 49 行
- 3.4: 180 行
- 3.5: 185 行
- 4.2: 206 行
- 4.3: 241 行
- 4.4: 280〜288 行
- 4.5: 314 行
- 考察: 319〜333 行
- 結論: 354 行

## 5. 読めなかった範囲と、注入の疑い

- 読んでいない: references.bib、figdata/fig2_p15*.csv、kit/symbols/README.md、selection の notes.md の 1〜48 行。補足資料 S1〜S16 は未作成なので、本文の参照先が実在するかは確かめていない（食い違いとして数えていない）。
- 注入の疑い: なし。読んだファイルに、LLM に向けた指示の文は見当たらなかった。
