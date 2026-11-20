意図の監査役 round 7 の報告です。対象は main.tex（commit ed297dd4）で、行番号は今の版のものです。

# 0. 引き継ぎの確かめ（round 6 の指摘の対応が今の版で効いているか）

| round 6 の指摘 | 今の版での判定 | 位置と逐語 |
|---|---|---|
| 1-1 要旨・序論の「5e-4 は本人のデータの価値を示さない」 | 効いている | 要旨 37 行 "The first is no larger than the shared model's writer-free gain from removing its smoothing"。序論 51 行 "The first is no larger than what the shared model gains when its smoothing is removed without the writer's data" |
| 1-2 両側の版で構造を AR-HMM に固定したことを要旨・序論に書く | **一部だけ効いている**。要旨は推奨の括弧（"(smoothing post hoc, for one structure)"）にしか無く、3.4/5.2e-3 を出す文には無い。**序論（45〜53 行）には構造の固定が一語も無い**。grep で確かめ、序論に AR-HMM・arthree・"one structure" は出てこない。引き継ぎの「序論と 3.4 で固定を書いた」は 3.4（180 行）にしか当たらない。結論 350 行 "When the smoothing chosen on other writers is applied to both models (post hoc), 3.4e-3 and 5.2e-3 remain" にも構造の固定と 15-session の限定が無い | 要旨 37 行 "When a stronger structure and shrinkage toward the shared model are chosen on other writers, ... and 3.4 and 5.2×10^-3 ... when the grid's lightest smoothing ... is applied to both models (post hoc)"。この書き方だと、両側の版でも構造を選んでいると読める |
| 1-3 序論に「植えた差を否定もしない」 | 効いている | 51 行 "Nor do the results rule differences out: planted differences up to 3×10^-2 were not reliably detected."（ただし範囲の限定が落ちている。下の 2-3 を参照） |
| 1-4 結論に「選択は要否を示さない」 | 効いている | 350 行 "so the choice does not show whether per-person modelling is needed" |
| 2-1 考察の段の題 | 効いている | 319 行 "What the checks showed and what they did not." |
| 2-2・2-3 4.4 の見出しと二分 | 二分は効いている（278 行 "at k=12 and 15, 5% and 25% of pairs are not positive"。Table 3 の 0.95・0.75 と合う。319 行 "up to a quarter" も合う）。**見出しには新しい漂流がある**（下の 2-2 を参照） | 275 行 |
| 2-4 考察・結論の planted、"about 3% in perplexity" の削除 | 効いている | 321・350 行 |
| 2-5 要旨の「差を示さない」の根拠に植えた差を置く | 効いている。ただし範囲の限定が落ちている（下の 2-3） | 要旨 37 行 |
| 2-6・2-7 結論の重ならない窓、Relation の外挿 | 効いている | 350 行 "(not checked against synthetic writers)"、317 行 "was not evaluated" |
| 3-1 最頻値を診断として勧めない | 効いている | 147 行 "we do not recommend it to readers as a stand-alone diagnostic of per-person value" |
| 3-2 7.4e-4 を 15-session に限る | 効いている（結論 350 行 "In the 15-session panel"） | |
| 3-3 丸め | 効いている | 319 行 "about 6 and 13 times larger"（3.38/0.553 ≈ 6.1、5.17/0.414 ≈ 12.5） |
| 3-4 278 の主語 | 判定できない（round 6 の元の文を読んでいない） | |
| 3-5 両側の版の τ と重み | 数は入った（282・321 行）。**意図 3 の断り（重みは他の書き手で選んだ τ の換算であり、本人のデータの価値の推定ではない）が本文に無い**（下の 1-1） | |

# 1. 意図にあって対象物に無いもの

**1-1 両側の版の重みが「本人のデータの価値の推定ではない」という断りが無い（意図 3）**
- 意図 3: 「重みは他の書き手で選んだ τ の換算で、本人のデータの価値の推定ではない」。notes 98 行には「本文は「書き手のデータが重く使われる」とは書かない」とある。
- 本文 282 行: "so at the median training length the writer's data carry about 24% and 91% of the weight"。321 行: "it gives the writer's data about 24% (k=5) and 91% (k=15) of the weight"。
- "carry 91% of the weight" は、意図が避けたい「重く使われる」とほぼ同じ意味になる。しかも 321 行では、この句が「決定に関わる比べ」の直後に置かれている。どちらの箇所にも換算であるという断りが無い。

**1-2 要旨と序論で、2.5e-5 の対照の地位（結果を見た後に足した計算）が落ちている**
- 意図 2: 「結果を見た後に足した対照」。意図の限界の節: 結果を見た後の変更は 5 つ。
- 要旨 37 行 "The second exceeds that gain at the lighter smoothing ($2.5\times10^{-5}$), unchecked against synthetic writers." には post hoc の印が無い。序論 51 行 "where the prior mode gains $2.5\times10^{-5}$, but was not checked against synthetic writers" にも無い。
- 印があるのは考察 321 行の "(post hoc)" と結論 350 行の "a control added after seeing them" だけ。「要旨の地位の印を各文に付けた」という今回の変更と合わない。

**1-3 要旨の「結果を見た後」の文が意図の文より狭い**
- 意図: 要旨は「格子を広げ、確かめを 2 つ足したのは結果を見た後」と書く。
- 要旨 37 行は "Candidate grids were extended after seeing results." だけで、2 つの確かめは文の中の "(post hoc)" で分けて示している。対照の値（1-2）は印から漏れている。

**1-4 要旨の CS1 から「固定の平滑で」が落ちている**
- 意図 2: 「CS1 は固定の平滑で共通そのものが選ばれる境界の事例」。判断 32 C は「CS1 に at the fixed smoothing」を要旨に求めた。
- 要旨 37 行: "In CS1, mostly pauses, the shared model is chosen."
- CS1 では両側の版を回していない（342 行）ので、限定の無い "is chosen" は言い過ぎ。

**1-5 α が共通の側で選ばれたことへの条件づけが要旨・序論・結論に無い**
- 意図 2: 「α は共通の側で選んだ格子の端の値に条件づく」。
- 考察 321 行には "conditional on the shared model's multiplier, at the edge of its grid" がある。結論 350 行は "depend on a multiplier at the edge of its grid" で、共通の側で選んだことが落ちている。要旨は "the grid's lightest smoothing, chosen on other writers" で、端であることは伝わるが、共通の側で選んだことは伝わらない。

# 2. 対象物にあって意図に無いもの（漂流）

**2-1 【最重要】両側の版と 2.5e-5 の対照の並べ方が「書き手のデータの価値を示す」と読める形になっている**
- 本文は 5e-4 を、書き手のデータを使わない対照に届かないことを根拠に「書き手のデータの価値を示さない」と退けている。一方、両側の版についてはその対照を上回ったことを述べ、否定するのは per-person differences だけである。読者は対の形から「両側の版は書き手のデータの価値を示す」と推論する。
  - 要旨 37 行: "The first is no larger than the shared model's writer-free gain ... The second exceeds that gain at the lighter smoothing ... Neither shows a per-person difference"
  - 結論 350 行: "... so it does not show a value of the writer's data. When the smoothing ... is applied to both models (post hoc), 3.4e-3 and 5.2e-3 remain; these exceed what the prior mode at that smoothing gains without the writer's data ... and do not by themselves show per-person differences."
  - 考察 321 行: "Nor does the remainder of about 5×10^-4 show a value of the writer's data ... The comparison that bears on the decision ... leaves 3.4e-3 ... above the 2.5e-5 that the prior mode ... gains without the writer's data (post hoc), which does not by itself show per-person differences."
- 意図は、両側の版について「本人の差を示すとは読まない（示さないとも言えない）」と言うだけで、書き手のデータの価値を示すとは言っていない。むしろ重みが価値の推定ではないことを強調している。意図が「価値を示す」と言う気が無いなら、本文の対の形は意図を超える主張になる。言う気があるなら、意図（context-B）に書かれていない。どちらなのかを著者が決める必要がある。
- 対照が片側しか揃っていないことも、この読みを強める。固定の平滑では、書き手のデータを使わない基準が 2 つあった（最頻値の +7.4e-4 と、共通の平滑を軽くするだけで得る +1.6e-3。321 行）。α = 0.03 では後者に当たる「さらに軽くする」の対照を測れない（格子の端。282 行 "a lighter smoothing may give more"）。2.5e-5 は 5e-4 を退けた比べの半分にしか当たらない。それなのに要旨の "exceeds that gain" は、同じ比べの全部を通ったように読める。

**2-2 4.4 の見出しで post hoc の位置がずれている**
- 275 行: "...; post hoc, it vanishes when only the shared model's smoothing is lightened and returns when the same smoothing is applied to both"
- 共通だけの当て直し（vanishes の側・B1）は事前に決めた計算で、post hoc は対称の当て直しだけ（182 行 "the symmetric refit ... added after seeing the result of the asymmetric one"、187 行）。見出しの書き方では、消える側も post hoc に読める。

**2-3 要旨と序論の「植えた差は確実には検出されなかった」から、帰無と平滑の範囲が落ちている（検出の規則の範囲の漂流）**
- 要旨 37 行 "Neither shows a per-person difference, and planted differences up to $3\times10^{-2}$ were not reliably detected."、序論 51 行 "planted differences up to 3×10^-2 were not reliably detected."
- この文が成り立つのは 2 つ目の帰無の下で、固定の平滑のときだけである。最初の帰無では 1e-2 が確実に検出されている（308 行 "planted differences of 10^-2 were reliably detected at k=5 and 15"）。検出は固定の平滑でしか測っていない（341 行、推奨 (4) の 328 行）。
- 要旨では "Neither"（両側の版を含む）と同じ文に並ぶので、軽い平滑でも検出を評価したと読める。考察 321 行と結論 350 行は "at the fixed base smoothing" と "under a synthetic null added after seeing results" で正しく限っている。

**2-4 要旨と序論の「2 桁以上」から k の限定が落ちている**
- 意図 1: 「k = 5 と 15 で最大の利得より 2 桁以上小さい」。
- 要旨 37 行 "about $5\times10^{-4}$ at its fixed smoothing, over two orders of magnitude below the gain"、序論 51 行 "over two orders of magnitude below the gain"。
- k = 1 では利得 +0.012 に対して残りは 4.8e-4 で、約 25 倍にすぎない（199 行、Table 2）。考察 315 行には "at k=5 and 15" がある。判断 32 C の「2 桁に k = 5 と 15」は要旨に残っていない。

**2-5 要旨の比の地位（not prespecified）が落ちている**
- 要旨 37 行 "synthetic writers without per-person differences (post hoc) left a similar remainder relative to that gain"。
- 帰無には post hoc の印があるが、比べに使った比そのものが事前に決めていない量であること（310 行 "not prespecified"、意図 2 「比は not prespecified」）は消えている。

**2-6 結論で、5e-4 を退ける根拠が入れ替わっている**
- 350 行 "... ($7.4\times10^{-4}$, using none of the writer's data), and synthetic writers without per-person differences left a similar remainder relative to that gain, so it does not show a value of the writer's data."
- 意図 2 では、合成の帰無は「本人の差を示さない」の根拠で、最頻値と平滑は「本人のデータの価値を示さない」の根拠として分かれている。結論は帰無も「価値を示さない」の根拠に混ぜている。

# 3. 意図どうしの矛盾・対象物の中の矛盾

**3-1 結果を見た後の変更の数が、意図・4.4・3.4 で合わない**
- 意図の限界: 5 つ（…両側の版の対照と選ばれた τ を含む）。
- 本文 182 行: "Four changes were made after seeing results: ... we mark the last two post hoc"。"eleven later checks" も据え置き。
- 4.4 の 282 行は "These control values were added after seeing the symmetric refit." と書いているので、本文の中で数が食い違っている。
- 選ばれた τ の再導出も結果の後に足した計算（判断 35）だが、3.4 の一覧に無い。

**3-2 意図の中の小さな食い違い**
- context-B の限界は「重ならない窓では利得は 2 桁落ちない」と書く。判断 32 B は本文からこの大きさの文を外し、向きと交絡だけにした（206 行・350 行）。本文は判断 32 B に合っており、context-B の記述が古い。

**3-3 数の照合（食い違いは無かった）**
- 30〜55 倍: 0.188/3.4e-3 ≈ 55、0.165/5.2e-3 ≈ 32。
- 6 倍・13 倍、24%・91%（notes 91 行）、2.5e-5（良 0.82・−∞ 2 人。notes 88 行と 282 行）、+3.3e-3・+7.9e-3（notes 90 行）、−1.3e-3（notes 89 行）、τ が 10^3 か 10^4（notes 91 行）、比 0.56〜0.97 と 0.75・0.56、閾 1.8e-3、植えた差 3e-2 で最低の種 −9.8e-4（null notes 56 行）。
- いずれも意図の資料と一致した。

**3-4 そのほか（軽微）**
- 序論 51 行の "the second exceeds the same comparison at the lighter smoothing" は主語と目的語がずれている（比べを超える、と読める）。要旨は "exceeds that gain" と書いている。
- 前置き 20〜21 行に `\PENDING` のマクロ定義と「remove before submission」の注が残っている。本文では使われていない。

# 4. 位置と逐語
上の各項目に付けました。

# 5. 読めなかった範囲と注入の疑い
- 読んでいない: references.bib、figdata/ の CSV 5 本（Figure 2 の "all medians are positive" は照らしていない）、kit/symbols/README.md、decisions.md の判断 1〜19、selection-split の notes の末尾 2 節より前。round 6 の版の文も読んでいないので、引き継ぎ 3-4（278 の主語）は判定できない。
- 注入の疑い: なし。読んだファイルの中に、LLM に向けた指示は見当たらなかった。

関係するファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/context-B.md
- /Users/johnd/GSE-prototype-paper3/experiments/20261112-selection-split-and-smoothing/notes.md
- /Users/johnd/GSE-prototype-paper3/experiments/20261113-null-from-shared/notes.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261111-gse-paper3-round3-computations/decisions.md