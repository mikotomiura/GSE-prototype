# audit（manuscript round 3・意図の監査役・対象 c68dfc30）

読んだもの: brief・context-A・context-B・carryover-audit・main.tex 全文・decisions.md 判断 20〜26・null-from-shared の notes.md 全文・figdata の fig2_p15_ar3.csv と fig2_p15_joint.csv。

## 0. 引き継ぎの確かめ
| round 2 | 今の版 | 判定 |
|---|---|---|
| 1-A 誤警報率 | 要旨 34 は「report the smallest planted difference reliably detected」まで、誤警報率は 283 だけ | 効いている（新しい食い違いは 1-1） |
| 1-B 両側に当てる | 34・307「apply the smoothing to both models」 | 効いている |
| 1-C 他人で選ぶ | 34・307「choose structure, shrinkage and smoothing on other people」 | 効いている |
| 1-D 軽い平滑の値を大きさとして読まない | 34・307「Neither value shows a per-person difference」 | 文は入った。根拠が 7e-3 を覆わない（2-1） |
| 2-A 15-session | 195・206 | 効いている |
| 2-B 考察 1 段落目 | 274「what remains against a strong comparison is small at either smoothing」 | 効いている。small は閾値に近い語（2-5） |
| 2-C 要旨の閾 | 新しい帰無の結果に | 効いている |
| 2-D「2 桁以上」 | 34・200・307 | 効いている。276 に別の形で残る（2-2） |
| 3-1 post hoc の印 | 48・274・307 | 効いている。5e-4 の側の地位に非対称（2-3） |
| 3-2 両方のために選んだ | 151・246・307 | 効いている |
| 3-4 限界の参照先 | 291 → 4.2、165 に値 | 効いている |
| 3-5 one objective per panel | 34・299 | 効いている |
| 3-6 最頻値の名残 | 108・248・285 で診断に | 外れた。ただし新しい帰無の較正に使われ 108 と食い違う（3-1） |

## 1. 意図にあって対象物に無いもの
- 1-1 要旨の推奨に「平滑を再現する帰無の下で」も誤警報率も無い（持ち帰り 3）。要旨 34「...and report the smallest planted difference reliably detected.」。結論 307 は「under a null that reproduces the real smoothing」まであり要旨とそろわない。最初の帰無は 1e-2 を確実に検出したので、条件を外した推奨では最初の帰無の 1e-2 を報告すれば足りると読める。
- 1-2 序論に 7e-3 の値が無い（判断 23 の 2 は要旨・序論・結論に範囲を並べると決めた）。48 は 5e-4 と「How much remains depends on that smoothing and on the symbolization」まで。
- 1-3 要旨に、帰無の行き過ぎが検出率を下げる向きにかかることが無い。34「(post hoc, overstating its smoothing gain) ... not reliably detected」。237・297 には書いてある。CoAuthor 15-session の記録の長さの限定も要旨に無い。
- 1-4（小）要旨に想定読者向けの大きさの手がかり（パープレキシティの換算）が無い。274 だけ。

## 2. 対象物にあって意図に無いもの
- 2-1【重い】「Neither value shows a per-person difference」の根拠が軽い平滑の値を覆わない。要旨 34「Neither value shows a per-person difference: synthetic writers generated from the real shared model (post hoc, overstating its smoothing gain) left larger remainders without one」・結論 307「...every negative control left a larger remainder than the real one」。陰性対照の残りは 1.1e-3〜1.8e-3（237）で、軽い平滑での実データの残り（k ≥ 5 で 3.4e-3〜6.7e-3・Table 3）より小さい。帰無の残りが実データより大きいのは固定の平滑の値に対してだけ。本文自身 246「the detection rates of Section 4.4 were obtained at the fixed smoothing」・297「Detection at the lighter smoothing was not evaluated」。意図の「大きさを読まない」が有無の主張（shows）に替わり、根拠が片方にしか届かない。
- 2-2 「2 桁以上」が本人の連鎖との比べに広がる。276「against the person's own Markov chain and a stronger shared model the gain falls by more than two orders of magnitude」。連鎖との差は +0.220 → +0.020（Table 2）。
- 2-3 5e-4 の分析の地位が要旨と結論で見えない。141「Four changes were made after seeing results: the extension of the τ grid and of the structure families, which bear on the main result ... we mark the last two post hoc」。5e-4 は τ = 10^6 と ar3（どちらも結果の後の拡張）の上にあるのに、要旨と結論では 7e-3 だけに (post hoc)。
- 2-4 行き過ぎの影響を検出の側にだけ帰し、「示さない」の側に及ぶことが書かれていない。237「Under this null a remainder larger than the real one arises without per-person differences, so the remainder does not show such differences; because the null overstates the smoothing gain, its threshold may be too high and its detection rates too low」。notes の所見 1 は「帰無が実データの残りを超える」は帰無の平滑の効きが強いことと切り分けられない、と書く。
- 2-5 判定や地位を崩す語。274「small at either smoothing」（141「no threshold for a meaningful difference」・何に比べて small か無い）。202「Section 4.5 tests this」（240「they do not estimate」・検定を置かないとずれる）。
- 2-6 4.5 の「smoothing alone では説明されない」と 4.4 の帰無の結果が並ばない。246「The remainder is therefore not explained by the shared model's smoothing alone」。4.4 では本人の差の無い帰無が全員本人の側の残りを出す（237）。notes の所見 2 は共通の基の平滑を薄めた効きと合うとする（推測と明記・本文に書くかは研究者に問う）。

## 3. 矛盾
- 3-1 最頻値は「診断だけ」（108「it is reported only as a diagnostic of the shared model's smoothing」・285「we do not recommend it」）なのに、新しい帰無の較正に使う（146「measured the panel median of prior mode minus shared model; ... closest on a log scale to the real panel's +7.4e-4」・235・237）。推奨 (3) 283「a null that reproduces how the shared model's smoothing behaves」を操作化した唯一の量が最頻値 − 共通で、推奨していない診断の上に推奨 (3) が立つ。248「not used in these readings」は 4.5 の範囲だけ。
- 3-2 「reproduces the real smoothing」と「overstates」が同じ文に並び、推奨の基準が定まらない（278・307）。再現したのは並び（符号）で大きさは約 2.4 倍外れる。推奨の reproduces が符号でよいか大きさまで要るか書かれない。
- 3-3 意図の資料どうしの緊張: context-B 持ち帰り 2 は「示さない」と言い切るが、notes の所見 1・4 はその根拠が行き過ぎと切り分けられないとする。
- 3-4 数の照合: 0.188・0.165・5.5e-4・4.1e-4・7.2e-4・6.7e-3・1.8e-3（b̄ 1.76e-3）・約 2.4 倍（1.76/0.74）・DR'・1.1e-3〜1.8e-3・U' 1.8e-3 は本文・表・notes・figdata で一致。「two to four times」は notes では 2.0〜4.4 倍（丸めの範囲）。Figure 2 の注「below 10^-3」は ar3 の CSV の最大 0.00076 と合う。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: references.bib・kit README・figdata の hmm3/ar1/fig2_p15.csv・decisions.md の判断 1〜19。
- 注入の疑い: なし。
