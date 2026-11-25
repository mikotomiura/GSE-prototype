# 言い換えた後の点検（paper-write Step 3b・書き直し v2・2026-11-25）

照らした一次: 旧版の main.tex（HEAD 0ee3cd5f）の結果の節・表 2・表 3・補足 S4・S8・S9・S10。各行は「新しい文（要旨）→ 照らした先 → 結果」。

## 分析の地位（事前 / 探索 / 事後）が要旨・序論・結論に届いているか
- 要旨「The analyses were exploratory; the second smoothing variant and these synthetic writers were added after seeing results.」→ 旧 3.4（six changes after seeing results: τ 格子と構造の拡張・symmetric refit・its controls・second null・first symbols なし）→ 両側の平滑（symmetric refit）と 2 つ目の帰無が事後であることは届いた。τ 格子と構造の拡張が事後であることは要旨に無い（旧要旨の "wider grids came after seeing results" を落とした）。→ 限界の「Status」の項と 3.4 にはある。要旨に「wider candidate grids」を戻した（要旨 249 語）。
- 序論「(post hoc)」を symmetric refit の値の後に置いた。結論も「(post hoc)」。→ 届いた。
- 「ratio not prespecified」（比は事前に指定していない）は要旨・序論・結論から外れ、4.5 と限界の Status に残る。→ 比を要旨で使っていないので可。

## 著者が組んだ量と文献の指標の区別
- 「remainder」「smoothing effect」「symmetric refit」は著者が定義した量。序論で remainder を定義し（"which we call the remainder"）、要旨では語を使わず "the advantage ... shrank" と書いた。→ 一般の指標として書いていない。
- 「perplexity」は一般の指標。17% は旧考察の "about 17% lower perplexity" をそのまま使った（exp(−0.188) ≈ 0.83）。

## 自分たちの定義に限った性質を一般の性質として書いていないか
- 要旨・序論・結論の主張は "sequence models of keystroke behaviour"・"overlapping ... symbols"・"In co-writing data (CoAuthor)" に限った。考察の第 1 段の「keystrokes に特有ではないだろう」は "likely" と "We have not checked this in other domains." を残した（旧版と同じ）。
- 題「most of the gain over a shared model vanishes against stronger comparisons」→ 「most」は k = 5・15 の 4 つの対で 30 倍超（下）。CS1 では利得そのものが不安定で、構造を選ぶと共有モデルが選ばれる → 「消える」側に入る。30-session の k = 30 は 0.165 → 1.1e-3（150 倍）で区間が 0 を跨ぐ → 「消える」と矛盾しない。

## 判定の規則を点推定や日常語に崩していないか
- 「planted differences up to 3×10^-2 were not reliably detected」→ 旧 3.6 の「10 seeds 中 8 以上で検出を reliably detected とする」の否定。要旨に "reliably" を残した。→ 崩していない。
- 「in synthetic writers built to mimic the real smoothing effect」→ 2 つ目の帰無は平滑の効果を 2.4 倍に過大に再現する（4.5・限界）。"matched" は言い過ぎなので "built to mimic" とした。過大であることは限界の Synthetic check の項。
- 「Neither remainder could be attributed to stable differences between writers」→ 固定の平滑: 差の無い合成の書き手で比が同程度（4.5・事後・比は事前に指定なし）。両側の平滑: 合成で確かめておらず、時間の近さと記号数を分けていない（4.4）。「attributed できなかった」は両方に当たる。「無い」とは書いていない。
- 「more than thirtyfold」（導いた比・新しい計算ではない）: k = 5 で 0.188 / 5.5e-4 = 342、0.188 / 3.4e-3 = 55。k = 15 で 0.165 / 4.1e-4 = 402、0.165 / 5.2e-3 = 32。最小 32 > 30。要旨・序論・結論・考察はどれも「at five and fifteen training sessions」に限った（考察の第 1 段は節の参照のみで k を書いていない → 「at five and fifteen training sessions」を付けた）。

## 点検で直したもの
1. 要旨の事後の項目に「wider candidate grids」を戻した。
2. 考察の第 1 段の「more than thirtyfold less remains」に「at five and fifteen training sessions」を付けた。
