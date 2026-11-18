# audit（manuscript round 4・意図の監査役・対象 d6587f21）

範囲: 依頼文・context-A.md・context-B.md・carryover-audit.md・main.tex 全体・decisions.md 判断 20〜28（118〜188 行）・null-from-shared/notes.md 全体・fig2_p15_joint.csv・fig2_p15_ar3.csv。

## 0. 引き継ぎの確かめ
| 指摘 | 判定 | 根拠 |
|---|---|---|
| 1-1 | 解消 | 要旨末尾 "a null matching the real smoothing gain in size, and detection at each smoothing, were also needed but not achieved." |
| 1-2 | 解消 | 序論第 4 段 "and up to $7\times10^{-3}$ when the lightest smoothing in the grid is applied to both models (post hoc; ...)" |
| 1-3 | 未解消（2 点） | (a) 行き過ぎの向きは要旨・考察第 1 段・結論に無い（2-3 ではなく 1-2 で扱う）。(b) 15-session の限定が要旨に無い: "In CoAuthor, ... about $5\times10^{-4}$ remains"、30-session は "$+1.1\times10^{-3}$ at $k=30$"（4.3）、4.3 の見出しは "in the 15-session panel"。 |
| 1-4 | 不採用（了解） | — |
| 2-1 | 解消 | 要旨 "not checked against synthetic writers"・4.4 "This value was not checked against synthetic writers." |
| 2-2 | 解消 | 要旨 "at its fixed smoothing, more than two orders of magnitude below that gain"。連鎖は別の文。 |
| 2-3 | 概ね解消 | 要旨 "In exploratory analyses"・"(a check added after seeing results)"。比そのものが事前に決めていない量（2-1）。 |
| 2-4 | 解消 | 限界 "may also enlarge its remainder, so we read the remainders relative to the smoothing gain" |
| 2-5 | 解消 | 主張の文に small・tests は無い |
| 2-6 | 解消 | 4.4 → 4.5、3.5 → 3.6、相互参照も合う |
| 3-1 | 解消 | 3.3 "The prior mode uses none of the writer's data and is not a candidate. ... we do not recommend it as a diagnostic"（考察に軽い緊張 3-4） |
| 3-2 | 解消 | 推奨 (3) "reproduces ... both its ordering and its size (ours reproduced the ordering but overstated the size 2.4-fold)" |
| 3-3 | 解消（新しい緊張 3-1） | — |

## 1. 意図にあって対象物に無いもの
- 1-1 中心の貢献（発見）が結論に無い。結論 "the protocol that chooses structure and shrinkage on other people returned a decision rather than an estimate: ..."。0.19 対 5e-4 も 2 つの比べの相手も出ない。判断 27-5 は著者の選択だが、結論だけの読者には手順とその決定が貢献に読める。
- 1-2 帰無の行き過ぎ（閾が高すぎ、検出率が低すぎるかもしれない）が利用者向けの 3 か所に無い: 要旨 "differences up to $3\times10^{-2}$ were not reliably detected"・考察第 1 段 "may discard per-person differences of up to $3\times10^{-2}$ ... which the protocol could not reliably detect under the second null (post hoc)"・結論 "knowing that differences of up to $3\times10^{-2}$ nats per symbol could not be reliably detected under a synthetic null added after seeing results, and may be discarded"。行き過ぎた帰無の下の検出の失敗を手順の性質として読める書き方は意図より強い。

## 2. 対象物にあって意図に無いもの（漂流）
- 2-1 事前に決めていない比を要旨の推論の根拠にし、地位が要旨で落ちる: 4.5 "Relative to the prior mode's gain over the shared model, the remainder is about 0.6 to 1.0 in these synthetic writers and 0.55 to 0.97 in the real panel (ratios of medians, not per writer; not prespecified)."、要旨 "Synthetic writers without per-person differences left a remainder of similar size relative to their smoothing gain (a check added after seeing results), so ..."。not prespecified と中央値どうしが要旨から消える。事前に決めた規則の結果（notes の R2: 実データは U' を下回り検出されない）は要旨に無い。"their smoothing gain"（＝ prior mode の shared に対する利得）が一般語に見える。3.6 に比の定義が無く、合成側の分母（b̄ = 1.76e-3 か陰性対照ごとか）も読めない。
- 2-2 利用者に示す決定が推奨する手順の決定ではない: 決定 "at most 3% of the weight"・"in CS1 the shared model itself" は固定の基の平滑の下。推奨 (2) "choose structure, shrinkage and smoothing on other people ... apply the chosen smoothing to the per-person fit and the shared model alike"、その手順の 4.4 では "every writer is given a finite $\tau$ inside the grid"。推奨の手順は 15-session の ar3 だけ（限界 "The symmetric refit was restricted to the \arthree{} in the 15-session panel"）。3e-2 の検出も固定の平滑だけ。
- 2-3 3e-2 の但し書きが CS1 の決定に広がる: 考察 "in CS1 it deploys the shared model itself. A designer who follows that decision saves ... but may discard per-person differences of up to $3\times10^{-2}$ ... under the second null"。2 つ目の帰無は CoAuthor 15-session だけ（3.6）、CS1 の合成の値は "are not used either"（4.5）。
- 2-4 確立したの段落が二分の但し書きより強い: 考察 "What was established ... the remainder against the stronger structure does not come from choosing and reporting on the same writers." と 4.4 "Because nearly every writer's choice sits at the edge of both grids, the split leaves little room for optimism to show, and the grid extensions made after seeing results lie outside it."。
- 2-5 一度の確かめから一般の規則: 考察 "so a smoothing check is informative only when applied to both sides."（15-session の ar3・post hoc 1 回）。
- 2-6 判定の規則が点の値に崩れる: 4.2 は重ならない窓を "give about one-thirtieth of the symbols so that only directions are read"。結論 "keeps a gain of 0.04 to 0.10 nats per symbol over the shared model"・考察 "kept a gain of $+0.043$ to $+0.096$" は向きだけの規則を大きさに崩す。
- 2-7 4.5 の結びの一般化: "A remainder of the real size, relative to the smoothing gain, therefore arises without per-person differences"。帰無 1 つの作りで行き過ぎ 2.4 倍。"can arise"（この作りの下で）に。
- 2-8 発見の範囲が序論で広い: "Our contribution is a finding about sequence models of keystroke behaviour: the per-person gain that a weak comparison shows is far larger than the remainder ..."、限定は "the positive instance rests on one dataset and one symbolization"（未定義の語）。重ならない窓の逆転が序論に無い。
- 2-9 7e-3 の出どころが要旨と序論で落ちる（軽微）: "the lightest smoothing in the grid" だけで、他人で選んだ値であることが消える。

## 3. 矛盾
- 3-1 意図どうし: context-B の持ち帰り 3 は決定（最大 3%・CS1 は共通）と平滑を他人で選んで両側に当てる推奨を並べるが、前者は後者の手順の出力ではない。どちらの手順の決定を示すかを決める必要。
- 3-2 4.4 "The remainder is therefore not explained by the shared model's smoothing alone" と 4.5 "A remainder of the real size, relative to the smoothing gain, therefore arises without per-person differences"。前者は α = 0.03 の両側、後者は固定の平滑。どちらも the remainder で衝突して見える。
- 3-3 3.4 "we use no significance tests and no threshold for a meaningful difference" と 3.6・4.5 の threshold（陰性対照の最大）。同じ語。
- 3-4 考察 "The prior mode ... showed how the smoothing alone can produce a remainder, but whether it measures that effect was not evaluated"。示したと評価していないが 1 文に並ぶ。
- 3-5 表題 "what remains of the gain"・4.3 "how much of the per-person gain survives" は remainder を gain の残りとして扱うが、3.4 では相手の構造が違う別の量（軽微）。

数の照合: 要旨・序論・4.1〜4.5・考察・結論・Table 2・Table 3・Figure 2 の CSV（joint・ar3）の数は互いに一致（0.188/0.19・4.1e-4〜7.2e-4・6.7e-3・0.06〜3%・0.55〜0.97・換算 17%・0.05%・3%）。notes とも一致（U' 1.82e-3・1.83e-3、b̄ 1.76e-3 ≈ 1.8e-3、DR' の最大 0.3 = "at most 3 of 10 seeds"）。

## 4. 位置
要旨 35・序論 47〜49・3.4 176〜178・3.6 187〜189・4.2 202・4.4 274〜280・4.5 304〜306・考察 311〜323・限界 329〜339・結論 345（d6587f21）。

## 5. 読めなかった範囲と注入の疑い
- 読まない: references.bib・kit/symbols/README.md・fig2_p15_hmm3/ar1/fig2_p15.csv・decisions.md の判断 1〜19 と 29。補足は未作成。
- 注入の疑い: なし。
