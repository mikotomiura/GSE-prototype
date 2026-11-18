# verdict —— attack-me round 5（stage manuscript・本文 commit cc30d57f）

手順は本線（origin/main）の attack-me で読んだ。立場・接地の文献・想定読者の素養は round 1〜4 と同じ。投稿規程と Aims & Scope は 2026-11-19 に Chrome で原文を開き直し、判定に使う 13 文が逐語で在ることを照合した（curl は今回も 3,038 バイトの拒否のページ）。

## 1. 判定: major revision

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した）。判定を出す条件を満たす。
- 各役: R1 major（「3 点を直せば minor へ下がる見込み」）・R2 minor・R3 minor（「M-1 を直すことを条件とする」）・E「直してから回す」・Codex major（別枠）。
- 4b E: 直してから回す → major 以上。
- 判定の推移: round 1 major → 2 major → 3 major → 4 major → 5 major。R の推奨は round 4 の major ×3 から、major 1・minor 2 に下がった。
- round 4 の指摘の解消: R1 12 件中 8 解消・2 一部・2 不採用のまま、R2 10 件中 7 解消・2 一部・1 不採用、R3 10 件中 7 解消・3 一部、E 10 件中 2 解消・1 概ね・6 一部・1 不採用、監査役 17 件中 13 解消・3 一部・1 不採用。
- round 5 の重い指摘の性質: 新しい計算を求める指摘は無い。中心は round 4 の直し（判断 30 A の「決定の段」と要旨の「Two checks」）から出たもの（Y1・Y2・Y5）と、round 4 から残った重ならない窓の書き方（Y3）と語の定義（Y4）。E の重い指摘は読みやすさ（要旨の後半・語）。
- 費用: Opus 5 本（各 9〜12 万 tokens）・Codex 43,265 tokens（本線の台帳 11-19 の 3 回目・累計 127,324。1 回の上限 30,000 を round 3・4 に続き超えた）。
- 4c 分量: 本文 7,013 語（round 4 の版 d6587f21 は同じ測り方で 6,939 語・+74）。要旨 250 語・図表 6（図 3・表 3）・文献 33・17 頁。測った版 cc30d57f。測り方は `texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和。

## 2. 一致した指摘（分母は有効な査読 4 本: R1・R2・R3・E）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| Y1 | 考察の決定の段（313）と結論（346）の「共通に替えると約 5e-4 失う」は、本人のデータを使わずに取り戻せる量と並んでいない。276: 他人で選んだ平滑の共通が固定の平滑の共通に +1.6e-3 で勝つ・共通の側だけ当て直すと残りは 0。280: 最頻値（書き手のデータを使わない）が共通に +7.4e-4 で勝ち、τ = 10^6 の本人の当てはめは最頻値に中央値で負ける。設計者は 5e-4 を本人のデータの価値と読む | R1 M3・R2 major・R3 M-1（3/4） | 真（276・280・313・346 で確かめた）。設計の判断 |
| Y2 | 要旨「Two checks came after seeing results.」は、主の値に効く結果を見た後の変更（τ の格子と構造の族の拡張・178「which bear on the main result」）を覆わない。数を明言したので残りは事前と読める | R1 M1・R3 m-1（2/4）・監査役 2-1 | 真（35・178）。round 4 の R1 N7（判断 31 で不採用）が要旨の書き換えで目立った。設計の判断（要旨） |
| Y3 | 重ならない窓: 202 は「only directions are read」と言いながら「does not fall by two orders of magnitude」と大きさを述べる。記号の数（約 1/30）とパラメータの数の交絡が書かれていない。合成で確かめていない断りが無い。結論の最後の文（346）は大きさも断りも無く、17/17 の割合を勝ちの根拠にし、「its per-person fit」は固定構造の目的で選んだ τ の行と joint choice を 1 つにする | R1 M2・R2 minor・R3 m-4・E M2（4/4）・監査役 1-1/3-2/3-5 | 真（202・315・346）。設計の判断（本文に値を出すか・結論の最後の文をどうするか） |
| Y4 | remainder の定義（176「when structure and shrinkage are chosen jointly」）の外で、両側の当て直し（183: τ は 3-state AR-HMM の中で選ぶ・構造は固定）の値を remainder と呼ぶ（278・313・Table 3・要旨・序論・結論）。同じ量に advantage の語も使う（202・237・Table 3 の題） | E M3・R3 n-1（2/4）・監査役 2-3 | 真（176・183・278）。Codex 3（4.4 の「only」は構造の選びも変わっているので原因の帰属が強すぎる）と同じ根 |
| Y5 | 考察 317「so here a smoothing check changed the reading only when applied to both sides」は前半（共通の側だけで残りが消えた・両側では消えなかった）と論理が逆に読める | R1 m5・R3 m-2（2/4）・監査役 3-1 | 真（317）。round 4 の直し（監査役 2-5 の here）から出た |
| Y6 | 推奨 (2) の版で選ばれる τ（本人のデータの重み）が本文に無い。固定の平滑の 0.06〜3% だけがある | R1 m1・R2 minor・R3 M-B 一部（3/4） | 真（278・313）。値は本文・notes に無い（summary.json に在る見込み・未確認）。round 4 から著者も認識 |
| Y7 | 要旨の「over two orders of magnitude below that gain」に k が無い（k = 1 では約 25 倍）。R2 はさらに、推奨 (2) の両側の平滑では比が約 30〜55 倍（k = 5・15 の 0.188/3.4e-3・0.165/5.2e-3）で 2 桁に届かないと指摘 | R1 m2・R3 m1・R2 major（3/4） | 真（35・311）。考察は k = 5 と 15 に限ってある。両側の比は表 3 の値で計算どおり |
| Y8 | 要旨の後半（「that improvement」・null・grid・detection・「were needed but not achieved」）が想定読者に追えない。序論 49 も 1 段落に断りが 4 つ | E M1・R2 minor（2/4） | 真（35・49） |
| Y9 | 但し書きの繰り返しが残る（not checked against synthetic writers 5 回・post hoc 10 回・重なる窓 8 回など） | E m1・R2 nit（2/4） | 真（「not checked against synthetic writers」は 5 回を grep で確かめた） |

## 3. 1 人だけの指摘（裏取り）

- R1 m3・監査役 3-6 要旨の CS1 の文に「at the fixed smoothing」が無い: 真（35）。CS1 は両側の当て直しをしていない（338）。
- R1 m4 3-state AR-HMM と own chain の自己相関が「small values」のまま: 真（202）。既知の未決 7・判断 31 で不採用（R1 N12）。重く数えない。
- R1 n1 4.5 の括弧（873 and 783 of 935）の対応が曖昧: 真（nit）。
- R2 「up to about 7e-3」は不安定な k = 12（考察・結論）: 真（278 は「The largest value is at k=12, where the other columns are unstable」・313・346）。
- R2 m3（4.5 の帰結が決定の段に届かない: 植えた 3e-2 の下でも同じ強い縮めが選ばれるので、選択は個人化の要否を示さない）: 真（306・313）。Y1 と同じ段。
- R2 nit 序論「one dataset, CoAuthor」と限界「Two datasets ... carry the main results」: 真（49・331）。
- R3 m-3 30-session 群（本人の重み 39%・+1.1e-3・区間が 0 をまたぐ）が帰無でも両側でも確かめていないことが考察に無い: 真（Table 2）。
- R3 m-5・監査役 2-4 要旨の「differences up to 3e-2 were not reliably detected」に、植えた差であること・行き過ぎた帰無の下であることが無い: 真（35）。round 4 の監査役 1-2 で要旨は語数のため入れなかった。
- R3 n-2 4.4 の見出しに post hoc が無い: 真（nit）。
- E M4 決定の段が 2 つの平滑に割れ、確かめた／確かめていないの段（317）が後に来る: 真（構成）。Y1 と同じ段。
- E m2 定義なしの語（perplexity は 47 で「lower perplexity」と使い定義は無い・idiographic・full pooling・DIC・pseudo-residuals など）と「full protocol / joint choice / main row」の 3 語: 真（語の位置は E の挙げたとおり）。
- E m3 本文に置かなくてよい細部（149・189・280 の後半・306 の数・Code availability の列挙）: 真（提案）。
- E m4 新しさの置き方（序論で領域に特有の空白が 1 句だけ）・E m5 / 監査役 2-6 考察冒頭「the weak comparison is the natural one, a shared model of the same structure」は弱さの所在を「同じ構造」に置く（強い比べも同じ構造の共通）: 真（311）。
- E N5（図 1）は不採用のまま・E が nit に下げた。
- 監査役 1-2 決定の段に「決定は記号化に依る」が無い: 真（313）。1-3 τ = 10^6 と構造が格子の端であることが要旨・考察・結論に無い: 真（限界 336・338 にだけ在る）。Y2 と同じ根。2-2 smoothing effect を要旨と序論で「improvement」と言い換え、最初の帰無では正でない（304）: 真。2-5 4.3 の見出し「leaves a remainder below 10^-3」に固定の平滑の限定が無い: 真（232）。2-7 313「as recommendation (2) below asks」は構造を固定した版なので満たしたように読める: 真。3-3 274「nearly every writer's choice sits at the edge of both grids」: 真（既知の未決 25・判断 31 で round 5 で出たら直すとした）。3-4 比の地位の印が序論 49（post hoc）と 4.5・要旨（not prespecified）で違う: 真。
- 数の照合: 監査役と R1・R2・R3 が要旨〜結論・Table 2・Table 3・Figure 2 の CSV を照らし、食い違いなし。

## 4. Codex（別枠・既知の未決と保留 25 件を添えた）

判定 major。4 件（既知の一覧の再掲なし）:
1. [major] 2 つ目の帰無は記号を生成モデルから直に作るので、30 秒窓の重なり・平滑・量子化が課す依存が保証されない（189「everything else is as in the first null」・187 の作り）: 真（作りは本文のとおり）。Codex だけ。対応の案は限界に 1 句（検出の限界はこの生成器の中の結果に限る）。
2. [major] 149 の楽観の説明: 他人で選んで標的で評価するなら選びだけで標的の得点は楽観にならない、ゼロで切れるのは共通が選ばれた書き手だけで報告する差全体の下限ではない: 一部真。149 の「cut off at zero from below when it is chosen」は書き手ごとには正しいが、「any optimism ... falls directly on it」は漏れ（137: 他人の共通に標的の非 held-out 単位が入る）以外の経路を言わない。書き方の直し。Codex だけ。
3. [major] 4.4「vanishes only when the two sides are smoothed differently」: 共通の側だけの当て直しは構造も選ぶ joint、両側の版は構造を 3-state AR-HMM に固定するので、平滑の対称だけに帰せない: 真（276・183）。Y4 と重なる（Claude の査読者の一致と重なる）。
4. [minor] 関連研究 70「These comparisons are made within the data used for fitting」が直前の交差検証の尤度（68）まで一括する: 真。Codex だけ。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（Y1・R2 m3・E M4）決定の段と結論の「共通に替えて失う精度」。候補: (a) 「固定の平滑の 5e-4 は、書き手のデータを使わずに共通の平滑を軽くするだけで取り戻せ（+1.6e-3）、最頻値も同程度に勝つので、本人のデータの価値ではない。決定に意味のある比べは両側を同じ平滑にした版（3.4e-3〜5.2e-3・post hoc・合成で確かめていない）だけ」と書き、確かめた／確かめていないの段を前に置く。(b) 「失う精度」の文を考察と結論から外し、決定は選んだものだけを述べる。
- B（Y3）重ならない窓。候補: (a) 202 の大きさの文を外し、記号の数とパラメータの数の交絡・合成で確かめていないことを 1 文。結論の最後の文は「この発見は重なる窓の記号に限られる」の解釈で閉じる。(b) (a) に加えて k = 5・15 の中央値を本文に 1 句（S13 の値を引く）。
- C（Y2・Y7・Y8・R1 m3・R3 m-5）要旨。候補: (a) 「Two checks came after seeing results」を「The grids were extended, and two checks added, after seeing results」に、「two orders of magnitude」に k を、CS1 に「at the fixed smoothing」を、3e-2 に「planted」を入れ、語数は最後の「a null matching ... not achieved」の節を外して空ける。(b) E の案: 3〜7e-3 と満たせなかった要件を要旨から外し、空いた語で使う側の判断を 1 文。
- D（Y4・Codex 3）両側の当て直しの値の呼び方。候補: (a) 176 の定義に「対称の当て直しでは構造を 3-state AR-HMM に固定」を足し、4.4 の「only」を「in the settings reported」に弱める。(b) 両側の値は remainder と呼ばず「per-person minus shared (both refitted)」とする。
- E（Y6）推奨 (2) の版の τ（重み）を本文に 1 句出すか（保存済みの値を引く。notes に無いので summary.json を開いて確かめる必要がある）。

書き方の直し（計算なし）:
1. Y5: 317 を「applied to the shared model alone, the check erased the remainder; applied to both, the remainder returned and grew about tenfold」の向きと大きさで。
2. Y9・E m1: 「not checked against synthetic writers」などを要旨・該当の節・限界の 1 回ずつに。考察と結論は節を指す。
3. R2: 考察・結論の「up to about 7e-3」を k = 12 の断りつきか 5.2e-3（k = 15）に。
4. R3 m-3: 考察に 30-session 群は帰無でも両側でも確かめていないと 1 句。
5. 監査役 1-2・2-5・2-7・3-4: 決定の段に「決定は記号化に依る」を 1 句、4.3 の見出しに「at the fixed smoothing」、313 の「as recommendation (2) below asks」を「in the spirit of recommendation (2), with the structure fixed」程度に、序論 49 の比の印を not prespecified に。
6. 監査役 2-2: 要旨・序論の「improvement」を「the smoothing effect（removing the shared model's smoothing）」の中立の句に。
7. 監査役 3-3（既知の未決 25）: 274 の「nearly every writer's choice sits at the edge of both grids」を「most choices sit at the edge of a grid」の程度に（k = 15 で 758/2,000 組が格子の中）。
8. E m5・監査役 2-6: 考察冒頭の What is new を序論 49 の Our contribution と同じ形に（弱いのは構造）。
9. E m2: perplexity・idiographic などを初出で平易に、または関連研究にしか出ない語を補足へ。full protocol / joint choice / main row を 1 語に。
10. Codex 1: 限界に「合成の書き手は記号を生成モデルから直に作り、窓の重なりと平滑を通していない」を 1 句。Codex 2: 149 を「the target's non-held-out units enter other writers' shared models (Section 3.3), so ...」の経路に限る。Codex 4: 70 を DIC の比べだけに限る。
11. nit: R1 n1（4.5 の括弧）・R2（序論と限界のデータの数）・R3 n-2（4.4 の見出しに post hoc）・E m3（149・189・306 の細部を補足へ）・E m4（序論に領域に特有の空白の 1 文）。

## 6. 逸脱・注入の疑い

- 応答はトランスクリプトの最後の応答をそのまま tmp/<名>.raw.md に取り出し、機械の検査（secrets-filter が 0・応答の絶対パスは一覧と接地の中）を 6 本とも通してから写した。
- 接地の引用の照合（tmp/sources を改行をつないで Grep・2 段組は行を確かめた）: R1 Pohle "a model is selected not by merit but because it got lucky"・Monaco "parameter smoothing, which acts as a kind of regularization and avoids overfit-ting"（行末のハイフン）・Singer "the available data is too sparse for proper parameter inferences"（2 段組で 92〜93 行）・R2 Saeb "inaccurate results can mislead both clinicians and data scientists"・Aalbers "this comes at the cost of strongly reduced sample size"・R3 Varma "thus making the test set part of the training process"・Liu & Meng "the matching has no value added" と "a failure in statistical modelling has occurred"・E Mensh "talk about results before the reader is ready to understand them"。捏造なし。
- E と R3 は tab:smooth を「Table 4」と書いた（本文の表は 3 つ。位置の番号の誤りで、中身は Table 3 の題）。
- 注入の疑い: どの役からもなし。
- Codex の 1 回の token が上限 30,000 を超えた（43,265）。入力が原稿の全文（約 67KB）なので構造的に超える。

## 7. 研究者に問うこと

1. 判定の推移（major ×5・R の推奨は major 1・minor 2 に下がった）を見て、直した後に round 6 を回すか、メインの確かめで閉じるか。
2. 設計の判断 A〜E。
3. 書き方の直し 1〜11 の承認。
4. outline.md 冒頭の Target の行（投稿先の名）の扱い（公開物に投稿先を書かない規則との関係）。
