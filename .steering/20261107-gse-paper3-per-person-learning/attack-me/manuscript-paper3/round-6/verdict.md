# verdict —— attack-me round 6（stage manuscript・本文 commit e6fdad49）

手順は本線（origin/main）の attack-me で読んだ。立場・接地の文献・想定読者の素養は round 1〜5 と同じ。投稿規程と Aims & Scope は 2026-11-19 に Chrome で原文を開き直し、判定に使う 13 文がページの本文に逐語で在ることを機械で照らした。

## 1. 判定: major revision

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した）。判定を出す条件を満たす。
- 各役: R1 minor・R2 major（「文の直しで閉じうる」）・R3 minor（「N-1 と N-2 は投稿前に必ず直す。直さなければ major に相当」）・E「直してから回す」・Codex major（別枠）。
- 4b E: 直してから回す → major 以上。
- 判定の推移: round 1〜5 major → 6 major（6 回続けて major）。R の推奨は round 4 major ×3 → round 5 major 1・minor 2 → round 6 major 1・minor 2（R1 が major から minor へ、R2 が minor から major へ）。
- round 5 の指摘の解消: R1 10 件中 8 解消・1 一部・1 不採用のまま、R2 9 件中 5 解消・4 一部（うち 1 は解消で残りを新しい指摘に回した）、R3 8 件中 6 解消・2 一部、E 11 件中 5 解消・5 一部・1 不採用、監査役 16 件中 13 効いている・3 一部。
- round 6 の重い指摘の性質: 新しい計算を必須とする指摘は無い（R1・R2・R3 は「文の直しでも閉じる」とし、計算は選択肢の 1 つとして挙げた）。中心は round 5 の直し（判断 32 A: 決定に関わる比べを両側の版とした）から出たもの（Z1・Z2）。Codex は新しい穴を 2 つ（平滑の選択の非対称・系列の境界）挙げた。
- 費用: Opus 5 本（各 9.1〜12.6 万 tokens）・Codex 43,511 tokens（本線の台帳 11-19 の 4 回目・累計 170,835。1 回の上限 30,000 を超えた。入力が原稿の全文で構造的に超える）。
- 4c 分量: 本文 7,219 語（round 5 の版 cc30d57f は同じ測り方で 7,013 語・+206）。要旨 248 語・図表 6（図 3・表 3）・文献 33・18 頁。測った版 e6fdad49。測り方は `texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和。

## 2. 一致した指摘（分母は有効な査読 4 本: R1・R2・R3・E）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| Z1 | 決定の段（315）と結論（346）は、両側の当て直しの残り（3.4e-3・5.2e-3）を「The comparison that bears on the decision」として出すが、5e-4 を退けたのと同じ対照（同じ平滑での書き手のデータを使わない比べ）も合成の書き手も当てていない。4.4（278）の「this check does not separate the writer's data from other effects of refitting」「not checked against synthetic writers」が決定の段・結論に届いていない | R1 major・R2 N1 major・R3 N-1 major（3/4）・E M-A の一部 | 真（278・315・346）。注: 最頻値は基底の平滑を外した共通の数え上げなので α に依らない。α = 0.03 での対照は「最頻値 − 共通（α = 0.03）」になる。R1 の「第 2 の帰無も α = 0.03 で平滑の効き 1.8e-3」は生成器の倍率と解析の倍率を混ぜた推論（R3 N-6 の指摘どおり）で、その部分は偽陽性。指摘の核は真。設計の判断 |
| Z2 | 見出しの数（要旨・序論・考察冒頭・結論の 5e-4 と「2 桁」）が、考察自身が決定に関わらないとした平滑の値。両側の版では 0.188/3.4e-3 ≈ 55 倍・0.165/5.2e-3 ≈ 32 倍で 2 桁に届かない | R2（引き継ぎ 一部）・R3 N-2 major・E M-A major（3/4） | 真（35・49・311・346・表 3）。設計の判断 |
| Z3 | 二分の確かめの言い方: 4.4 の見出し「The remainder stays positive」と考察「was not changed by choosing and reporting on different writers」が、表 3 の k = 12・15（2.5% 点が −4.2e-3・−3.7e-3、正の割合 0.75）と、共通だけの当て直しで消えた結果（276）に合わない | R1 minor・R2 N4・E m-E（3/4）・監査役 2-2/2-3・Codex 3 | 真（271・274・313・表 3 の 297〜298 行） |
| Z4 | 要旨の地位の印: どの 2 つの確かめが事後かが要旨から読めず、要旨の 2 つの結論（似た残り・検出できない）が事後の第 2 の帰無に依ること、両側の版が post hoc であることに印が無い | R1 minor・R3 N-4（2/4）・監査役 1-2 | 真（35・178） |
| Z5 | 要旨の推奨の文が、本文の推奨 (2) の但し書き（post hoc・1 構造・1 パネル・格子の端）と (3)(4) が満たせていないことを落とし、無条件の should になっている | R2 N5・R3 N-3（2/4） | 真（35・321） |
| Z6 | 両側の版の τ（10^2〜3×10^5）では重みが約 3% から 99% 近くまでにわたり、設計者が読めない。k = 5・15 の τ か重みの中央値を本文に 1 句 | R1 minor・R2 N3（2/4）・監査役 3-5 | 真（278・315）。判断 32 E で「格子の中」まで・書き手ごとは開かない、と決めた点。中央値（集計値）を出すかは設計の判断 |
| Z7 | 「about 6 and 12.5 times」: 5.2e-3/4.1e-4 ≈ 12.7 で 12.5 は丸めが合わない | R2 N7・R3 N-8（2/4）・監査役 3-3 | 真（313）。「about 6 and 13」に |
| Z8 | 要旨と序論の「3 to 7×10^-3 from five training sessions on」の上端は不安定と断った k = 12 の値で、考察・結論（3.4e-3〜5.2e-3・k = 5 と 15）と範囲が合わない | R2（引き継ぎ 一部）・R3 N-9（2/4） | 真（35・49・278・346）。判断 32 で要旨に残すと決めた点。今回は結論と食い違う形になった。設計の判断 |
| Z9 | 要旨と序論第 4 段（約 300〜330 語・括弧の挿入 6 か所）の密度。但し書きの繰り返し（post hoc 約 20 か所・does not show 6 か所・重なる窓に限る 5 か所・2.4 倍 3 か所） | E M-C・m-A・R2 N6（2/4） | 真（35・49） |
| Z10 | 3.4 の remainder の定義の括弧（176）: 同時に選ぶと構造を固定するが 1 文に並び、symmetric refit は後で定義。構造を AR3 に選ぶのは固定の平滑での事実で、α = 0.03 では選び直していない | R1 nit・E m-C（2/4） | 真（176） |

## 3. 1 人だけの指摘（裏取り）

- R1 remainder は構造しだい: 1 次の連鎖の行（shrinkage-only）は固定の平滑で k = 15 に共通の AR1 に +0.002（重み 24%）: 真（204）。考察に「残りは選ばれた構造の値」と 1 文が対応の案。
- R1 m4 の続き（AR3 と own chain の自己相関の値）: 真。既知の未決 7・判断 31 で不採用。重く数えない。
- R1 は表 3 を「Table 4」と書いた（位置の番号の誤り・中身は表 3）。
- R2 N2 使う場面の記述: 3.3「A new writer's later units are predicted after k of the writer's units」（137）と序論「cold start for every newcomer」（43）は、実際の分け方（20 session 以上の書き手の、ホールドアウトの直前の k 単位）と合わない: 真。
- R3 N-5 比で合成と実データを並べる読みは、残りが平滑の効きに比例することを仮定: 真（306・337）。限界に 1 句。
- R3 N-6 α を解析の倍率と第 2 の帰無の生成器の倍率の 2 つに使う（306「The second null (post hoc) used the multiplier α=0.03」）: 真。
- R3 N-7・監査役 2-6 結論の重ならない窓の文に「合成で確かめていない」とデータの量の交絡が無い: 真（346）。
- E M-B 一般の UMUAI 読者への橋（滑らせた窓で特徴を作る適応系一般で同じ弱い比べが生じうること）が無い: 真（提案）。足す案で語数が増える。設計の判断。
- E m-B 定義なしの語（cell・first/second null・full pooling・double chain・backoff・record-wise・Dirichlet・lag-1 autocorrelation・nats・e 表記）と 1 概念 2 語（共通だけの当て直し 4 語・両側 4 語・fixed / fixed base / base smoothing・own chain 3 語・joint choice / joint objective・143 の advantage）: 真（位置は E のとおり）。
- E m-D 本文に置かなくてよい細部（149・187 の検出の規則の細部・189・306 の数・237・206・限界 337〜338）: 真（提案）。
- E m-F 考察で Relation が決定と推奨の間に挟まる・315 は約 230 語で数を 8 つ運ぶ: 真（構成）。
- E n1 Figure 2 の題と軸に gain / remainder の語が無い: 真（nit）。
- 監査役 1-1 要旨と序論に「5e-4 は本人のデータの価値も示さない」が無い（考察と結論にだけ）: 真（35・49）。
- 監査役 1-3 序論に「3e-2 までの植えた差を否定もしない」が無い: 真（49）。1-4 結論に「植えた差の有無にかかわらず同じ強い縮み → 選択は要否を示さない」が無い: 真（346）。
- 監査役 2-1 考察の段の題「What was established」が探索的という地位を消し、post hoc の両側の版を同じ段に入れている: 真（313）。
- 監査役 2-4 考察と結論で planted が落ち、考察の「about 3% in perplexity」が実データの差の大きさに読める: 真（315・346）。
- 監査役 2-5 要旨の「差を示さない」の根拠が事前に決めていない比だけ（事前の規則〔閾で検出されない〕が要旨に無い）: 真（35）。
- 監査役 2-7 考察 Relation「For symbolizations like theirs the per-person HMM may keep a gain」は評価していない記号化への外挿: 真（317）。
- 監査役 3-1 3.3 は最頻値を「we do not recommend it as a diagnostic」とするのに、考察と結論はそれを決め手に使う: 真（143・315・346）。
- 監査役 3-2 結論の「That remainder is no larger than ... 7.4e-4」は 15-session の値で、30-session の残り 1.1e-3 は超える。結論はパネルを限っていない: 真（235・346）。
- 監査役 3-4 278「the remainder at the fixed smoothing thus vanished」の主語のずれ: 真（nit）。
- 数の照合: R1・R2・R3・監査役が要旨〜結論・表 2・表 3・Figure 2 の CSV を照らし、食い違いは Z7 の丸めだけ。

## 4. Codex（別枠・既知の未決と保留 26 件を添えた）

判定 major。3 件（既知の一覧の再掲なし）:
1. [major] 平滑の選択は非対称のまま: α は共通だけの目的（183「by the other writers' median of how much the shared model with α beats the one with α=1」）で選び、その後に本人の τ を選ぶ。同じ α を当てても選択の非対称は消えず、標本量の違う両側で同じ擬似カウントは同じ正則化の強さではない: 真（183）。Codex だけ。Z1 と同じ段（決定に関わる比べ）。対応の案は「共通の側で選んだ α に条件づけた比べ」と明記。
2. [major] 系列の境界: 176「Each held-out unit is scored as its own sequence」だが、CS1 の課題は作業の区切り（110・30 分以上の間）を含み、区切りで状態・直前の記号をリセットするか、先頭の記号の採点と初期分布が本文に無い: 真（本文に無い。キットの README は重ならない窓の記号化が区切りの中で作られることだけを書く）。Codex だけ。対応の案は 3.4 に 1 文（コードで確かめてから書く）。
3. [minor] 二分の「不変」: Z3 と同じ（Claude の査読者の一致と重なる）。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（Z1・Codex 1）決定の段と結論の両側の版の値。候補: (a) 計算する: 「最頻値 − 共通（α = 0.03）」の中央値（書き手のデータを使わない対照）を、保存済みの当てはめの held-out の尤度から出し（条件を先にコミット・書き手ごとの値は開かない）、決定の段に並べる。(b) 計算しない: 決定の段と結論に「この値も、同じ平滑での書き手のデータを使わない比べにも合成の書き手にも掛けていない・α は共通の側で選んだものに条件づく。書き手のデータの価値を示すかは未決」と 1 句。「bears on the decision」は決定に関わる比べの形の意味に限る。
- B（Z2・E M-A）見出しの数。候補: (a) 要旨・序論・考察冒頭・結論で、固定の平滑の 5e-4（2 桁以上）と両側の版の 3.4〜5.2e-3（約 30〜55 倍）を 1 組で出し、どちらが決定に関わるかを同じ所で言う。(b) 見出しを構造に置く（「弱い比べで 0.19、強い比べではそのおよそ 1/30 以下で、どの平滑でも書き手の差の証拠にならない」）。
- C（Z6）両側の版の τ か重みの中央値（k = 5・15 の集計値）を本文に 1 句出すか、「格子の中」の範囲のままか（判断 32 E の見直し）。
- D（Z8）要旨と序論の「3 to 7×10^-3 from five training sessions on」を、考察と結論に合わせて「3.4 and 5.2×10^-3 at five and fifteen training sessions」にするか（判断 32 の保留の見直し）。
- E（E M-B）一般の UMUAI 読者への橋の 1〜2 文を足すか（語数が増える。足すなら同じ節で削る）。
- F（Codex 2）系列の境界の扱い（区切りでのリセット・先頭の記号・初期分布）をコードで確かめて 3.4 に 1 文。

書き方の直し（計算なし）:
1. Z3: 4.4 の見出しを「The median remainder stays positive when choice and report use different writers; post hoc, it vanishes when only the shared model's smoothing is lightened and returns when the same smoothing is applied to both」の程度に。考察「was not changed」を「the median difference from choosing on the reported half was 0, though at k = 12 and 15 a quarter of the pairs were not positive」の程度に。
2. Z4・監査役 1-2: 要旨の「two checks added」の 2 つを名指すか、第 2 の帰無の文と両側の版の文に (post hoc) を付け、前の文は格子の拡張に縮める。
3. Z5: 要旨の推奨に「(the last applied here post hoc, to one structure)」を足すか should を本文の強さに。
4. Z7: 「about 6 and 13 times」。
5. Z9・E m-D・E m-F: 序論第 4 段を 2 段に割り、地位の説明は 3.4 に任せる。考察の Relation を発見の段の直後へ、決定の段の最初の文に設計者への答えを。細部（187 の検出の規則の細部・189・306 の数・237・206）を補足へ。2.4 倍の注記は限界の 1 か所に寄せる。
6. Z10: 176 の括弧を外して 2 文に（「joint choice picks at the fixed smoothing」）。
7. R1: 考察の確かめた段に「残りは選ばれた構造の値で、1 次の連鎖を固定すると k = 15 で 2e-3（帰無なし）」を 1 文。
8. R2 N2: 3.3 の Use case と序論の cold start を「多く書く書き手の、ホールドアウトの直前の k 単位を使えるとき」に直し、新しい人の cold start には直接答えないと 1 句。
9. R3 N-5・N-6: 限界に「比で読むのは残りが平滑の効きに比例すると仮定し、確かめていない」を 1 句。第 2 の帰無の生成器の倍率を別の書き方（the generator's smoothing multiplied by 0.03）に。
10. R3 N-7・監査役 2-6・2-7: 結論の重ならない窓の文に「(not checked against synthetic writers)」と交絡を、考察 Relation の「For symbolizations like theirs ... may keep a gain」を外すか「was not evaluated」に。
11. 監査役 1-1・1-3・1-4・2-1・2-4・3-1・3-2・3-4: 要旨と序論に「本人のデータの価値も示さない」の根拠を 1 句（語数に応じて）、序論に「否定もしない」、結論に選択は要否を示さない、考察の段の題を「What the checks showed and what they did not」程度に、考察と結論の 3e-2 に planted を戻し「about 3% in perplexity」を外す、3.3 の最頻値の「not recommend as a diagnostic」の範囲（読者が単独で使う道具としては勧めない）を限る、結論の 7.4e-4 の比べを 15-session に限る、278 の主語。
12. E m-B・n1: 1 概念 1 語にそろえる（shared-only refit / symmetric refit・fixed base smoothing・own chain）。cell・first/second null・nats を初出で定義、関連研究にしか出ない専門語は削る。Figure 2 の題に gain / remainder。

## 6. 逸脱・注入の疑い

- 依頼文は brief-*.md に保存し、起動の文では「このファイルを Read してその指示に従う」とだけ渡した（round 5 までは依頼文を起動の文に直に書いた見込み。中身は同じ）。
- 応答は SubagentHandback の本文をトランスクリプトから機械で取り出して tmp/<名>.raw.md に置き、機械の検査（secrets-filter が 6 本とも 0・応答の絶対パスは一覧と依頼文・引き継ぎの中）を通してから写した。
- 接地の引用の照合（tmp/sources を改行をつないで grep・2 段組は行で確かめた）: R1 Pohle "results for each of these models should be reported"・Monaco "bias parameters that depend on event types with low frequency toward the marginals"・Singer "sparse for proper parameter inferences"（2 段組で 93 行）・R3 Varma "choosing the minimum resampled error will give a biased estimate of the true error"・Liu & Meng "internal controls are usually of lower quality than external controls"・E Mensh "the abstract must convey the entire message of the paper"・"Resist the temptation to use a different word to refer to the"（2 段組で 159 行）。R2 の Saeb・Aalbers の引用は round 5 と同じ文。捏造なし。
- 注入の疑い: どの役からもなし。
- Codex の 1 回の token が上限 30,000 を超えた（43,511）。

## 7. 研究者に問うこと

1. 設計の判断 A〜F。
2. 書き方の直し 1〜12 の承認。
3. 直した後に round 7 を回すか（判定は 6 回続けて major。ただし R の推奨は minor 2・major 1 で、重い指摘は round 5 の直しから出た決定の段の書き方に集まっている）。

## 8. 研究者の採否（2026-11-19・AskUserQuestion）

A〜F・直し 1〜12・round 7 を回す、のすべてで推奨案を選んだ。中身は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 34。
