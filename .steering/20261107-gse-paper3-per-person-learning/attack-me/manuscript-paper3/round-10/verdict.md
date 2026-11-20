# verdict —— attack-me round 10（stage manuscript・本文 commit c87c7d63）

手順・立場・接地の文献・想定読者の素養は round 1〜9 と同じ。投稿規程と Aims & Scope は 2026-11-20 に Chrome で原文を開き直し、判定に使う 13 文が逐語で在ることを機械で照らした。

## 1. 判定: minor revision（10 回目で初めて major でない）

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した。R3 の 1 件は言い換え。下の 6）。判定を出す条件を満たす。
- 各役: R1 minor・R2 minor・R3 minor・E「査読に回す」（「残る major 2 件は題と 1〜2 文の書き換えで直せ、新しい計算は要らない」）・Codex major（別枠）。
- 4b E: 査読に回す → R1〜R3 から決める → minor。
- 判定の推移: round 1〜9 major → 10 minor。R の推奨は 3 回続けて全員 minor。
- round 9 の指摘の解消: R1 9 件すべて解消。R2 9 件中 8 解消・1 一部（推奨 (2) の順）。R3 8 件すべて解消。E 9 件中 2 解消・5 一部・2 未解消（採らなかったもの）。監査役 11 件すべて効いている。
- この round の指摘の性質: ほぼすべて言い方と置き方。round 9 の直しから出たもの: 序論の理由の句「applied to both models alike」と「effectively less smoothed」の言い切り、結論の「shows no」、要旨の推奨の順。新しい計算を求める指摘は無い（Codex の対応比較の追加案だけ）。
- 費用: Opus 5 本（各 9.1〜12.5 万 tokens）・Codex 約 44,900 tokens（本線の台帳 11-20 の 14 回目・累計 595,037）。
- 4c 分量: 本文 7,745 語（round 9 の版 1f4f4b5b は同じ測り方で 7,494 語・+251）。要旨 248 語・図表 6・文献 33・18 頁。測った版 c87c7d63。

## 2. 一致した指摘（分母は有効な査読 4 本）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| W1 | 序論の理由の句「applied to both models alike」は、3.5 の「the same prior counts weigh differently」・α を共通の側で選んだことと食い違う。「effectively less smoothed」は 4.3 の may の読みより強い | R1・R3 N2（2/4）・監査役 2-2・2-4 | 真（49・185・241） |
| W2 | 図 2・表 2・4.3 の題が、決定に関わらない方の値（10^-3 未満）を答えとして運び、決定に関わる値は 4.4 の点検の中にある | E N1・R1・R2（3/4） | 真（230・245・234・273） |
| W3 | 結論の「shows no per-person difference」は考察の「Not established」より強い。要旨の「Neither value shows」も、両側の版について否定しない側が無い。「per-person difference」が定義されず、使う場面では時間の近さは交絡ではなく価値になりうる | R1・R3 N8・R2 major（3/4）・監査役 1-5 | 真（354・35・323）。R2 の論点（決定の問いと科学の問いを分ける）は設計の判断 |
| W4 | 要旨の推奨が 3 つを一緒に選ぶように読め、(post hoc, one structure) の掛かりが曖昧。推奨 (2) と構造の選びの順 | R2・E N3（2/4）・監査役 2-3 | 真（35・329） |
| W5 | 要旨の未定義の語（fixed base smoothing・null・planted）と post hoc の 4 回 | E N3・R2（2/4） | 真（35） |

## 3. 1 人だけの指摘（裏取り）

- R3 N1: 4.3 の「the per-person fit beats the shared model only under strong shrinkage」は、両側の版（τ = 10^3 で重み 91% の当てはめが勝つ）と矛盾する: 真（239）。
- R3 N3: 両側の版を「決定に関わる」とした理由も結果を見た後に作られたことが書かれていない: 真。
- R3 N4: 「reporting what it could not detect」は固定の平滑にしか当たらない: 真（333）。
- R3 N5: 図 2 の題「enter no fit and no choice」は、格子を結果を見た後に広げたことと並べると無条件: 真（173）。
- R3 N6・Codex major: 入れ替えの規則は、残りが 0 でも入れ替えが残りの半分以上負ければ満たされる。情報があるのは「入れ替えが共通に負ける」こと。Codex は「他人より良い」と「本人の情報が要る」は違うとする: 真（284）。本文は「It excludes only ...」と限っているので、結論を「同じ τ の他人のデータより本人のデータが良い」に限れば足りる。
- R3 N7: 推奨 (2) に「選びが格子の端なら格子を広げる」: 真（提案）。
- R3 N9: 考察の確かめた段に主表の行（1 次の連鎖・帰無なし）が混じる: 真（323）。
- R1 nit: 入れ替えの書き手の間のまとめ（中央値）が書かれていない・「it」の指す先・考察の文のつなぎ: 真。
- R2 minor: 休止の例は、休止が主の CS1 で共通が選ばれたことと並べるべき。休止の記号は「直前 30 秒に押下が無い」: 真（321・114）。
- R2 minor: 費用に、選びに要る他人のパネル（16 人・各 20 回以上）が入っていない: 真（提案）。
- E N2: 序論の理由の句は prior mode を知らない読者に追えない: 真（49）。W1 と同じ句。
- E N5: 189 の「the common one」は共通（shared）の別名に見える。入れ替えの段の sessions と units の揺れ: 真。
- E N6: 4.4 が 7 段で決定に関わる値を埋める。細部を補足へ: 真（提案）。
- E N7: 表 2 の題「to a remainder to below」・145 の「second null」が定義の前: 真。
- 監査役 1-1: 要旨と序論の約 5e-4 にパネル（15-session）が無い: 真（35・49）。
- 監査役 1-2: 「出力は推定ではなく群ごとの決定」が本文にはっきり無い: 真。
- 監査役 1-4: 「比は植えた差のある場合で見ていない」が本文から落ちた（round 8 の前の削りで補足 S15 へ移した）: 真。比を読みの根拠にしているので本文に戻すべき。
- 監査役 2-1: 要旨・序論・結論で比の not prespecified が落ちている: 真。
- 監査役 2-5: 要旨の「its source ... was not separated or checked on synthetic writers」の組み方: 真。
- 監査役 2-6: 考察の冒頭で 2 つの値を「far larger」の 1 つの括弧に入れ、2 桁が両方に掛かって読める（両側の版は約 32〜55 倍）: 真（317）。
- 監査役 3-3: 24% が 2 つの量に使われる: 真（nit）。
- Codex major: 区間は「値を固定した再標本化」で、書き手の値は共通の学習データと選びを介して依存するので「understate」とは限らない。記述の範囲と書くべき: 真（178）。
- Codex major: 他の書き手の単位は暦の上で対象の予測時点より後でもありうる（回顧の評価）: 真（139）。限界に 1 句。

## 4. Codex（別枠・既知の未決と保留 37 件を添えた）

判定 major。3 件（既知の一覧の再掲なし）: 入れ替えの結論の範囲（R3 N6 と重なる）・区間の意味（Codex だけ）・暦の時点（Codex だけ）。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（R2 major・W3）「per-person difference」の定義と 2 つの問い: (a) 本文で 1 句定義し（回をまたいで安定した書き手ごとの違い）、両側の版を「決定の問い（使う場面での本人の直近のデータの価値: 区間は 0 から離れるが、合成で較正していない）」と「科学の問い（安定した書き手の差: 時間の近さとデータの量を分けていない）」に分けて書く。要旨・結論の「shows no / Neither shows」をそれに合わせる。(b) 結論の「shows no」を「does not show」にそろえるだけ。
- B（W2）図・表・4.3 の題: (a) 題を「弱い比べの利得は強い比べで 1〜2 桁縮む」と値の大小を限らない結論にし、図 2 の題に表 3 の両側の版を指す 1 句。(b) 両側の版を図 2 に点として足す（図の作り直し）。

書き方の直し（計算なし）:
1. W1・E N2: 序論の理由を手続きの対比に（「平滑そのものを他人で選んで両側に当てる。固定の平滑では、強く縮めた当てはめが平滑を除いた共通の数に近づく〔3.3〕」）とし、同じ数でも両側で効き方が違うことを 1 句。
2. W4・W5・監査役 1-1・2-1・2-5: 要旨を直す（15-session、比の not prespecified、推奨の順、post hoc の印を 1 か所にまとめる、源の文の組み方）。語数は帰無の語を言い換えて作る。
3. R3 N1: 4.3 の「only under strong shrinkage」に「at the fixed base smoothing」。
4. R3 N3: 3.4 の事後の列挙に、両側の版を決定に関わるとした位置づけも結果を見た後と 1 句。
5. R3 N4: 「reporting, at the fixed base smoothing, what it could not detect」。
6. R3 N5: 図 2 の題に「within the final protocol (grids extended after seeing results; Section 3.4)」。
7. R3 N6・Codex: 入れ替えの段の結論を「the writer's own sessions predict better than another writer's under the same τ」に限り、情報のある値は入れ替えが共通に負けることと 1 句。
8. R3 N9: 考察の確かめた段から主表の行を外すか「(main table, no synthetic null)」。
9. R1 nit: 入れ替えの書き手の間のまとめ（中央値）・「it」を名詞に・考察の文をセミコロンで切る。
10. R2: 休止の例に「in CS1, where most held-out symbols are such pauses, the shared model was chosen」と休止の定義。費用に「the choice used 16 other writers with at least 20 sessions; how few would suffice was not studied」。
11. E N5・N7: 189 の the common one を the shared one に、入れ替えの段を units に、表 2 の題の「to」を 1 つに、145 の second null を「a synthetic check (Section 3.6)」に。
12. 監査役 1-2: 決定の段に「the protocol returns a decision for a panel, not an estimate」を 1 句。
13. 監査役 1-4: 4.5 に「the ratio was not examined with planted differences」を戻す。
14. 監査役 2-6: 考察の冒頭の「far larger」を、5e-4 は 2 桁以上・両側の版は約 30〜55 倍と分ける。
15. Codex: 3.4 の区間の説明を「resampling writers with their values fixed, as a descriptive range; values are dependent through shared training data and the choice, and the intervals do not include the uncertainty of the whole procedure」に。限界に「other writers' units may postdate the target's prediction point; the evaluation is retrospective」。
16. R3 N7: 推奨 (2) の括弧に「a choice at the edge of a grid calls for extending it」。

採らない案（理由）: E N6 の 4.4 の細部を補足へ・2 小節に（前の round で本文に置くと決めた点を含む）、R2 の序論の段を割る（nit）、Codex の対応比較の追加計算。

## 6. 逸脱・注入の疑い

- 依頼文は brief-*.md に保存し、起動の文では「このファイルを Read してその指示に従う」とだけ渡した。
- 応答は SubagentHandback の入力をトランスクリプトから機械で取り出して tmp/<名>.raw.md に置き、機械の検査（secrets-filter が 6 本とも 0・応答の絶対パスは一覧・依頼文・引き継ぎ・context-B の資料の中）を通してから写した。
- 接地の引用の照合: R1 Pohle "the plug-in estimator is biased due to overfitting"・Monaco "it acts as a kind of regularization"、R2 Aalbers "this comes at the cost of strongly reduced sample size"・Saeb "we can split the data based on time"、R3 Varma 4 件と Liu & Meng 3 件、E Mensh "the title of the figure should communicate the conclusion"。R3 の Liu & Meng "descriptive power comes at the cost of robustness" は逐語では無く、263・279 行の言い換えだった（同じ段の "Highly flexible models tend to" は逐語で在る）。手順どおり R3 の引用を全件確かめ、ほかの 7 件は逐語で在った。この引用に依るのは N1 の補足の 1 句だけで、N1 は本文の食い違い（239・280）に依るので真のまま。
- 注入の疑い: どの役からもなし。
- Codex の 1 回の token が上限 30,000 を超えた（約 44,900。round 6〜9 と同じ）。

## 7. 研究者に問うこと

1. 設計の判断 A・B。
2. 書き方の直し 1〜16 の承認。
3. 直した後: 判定は minor（初めて）。Skill の規則では manuscript の minor は「直して投稿へ進む（もう 1 回回すのは直しが主張に触れたときだけ）」。A(a) は主張の言い方に触れる。
