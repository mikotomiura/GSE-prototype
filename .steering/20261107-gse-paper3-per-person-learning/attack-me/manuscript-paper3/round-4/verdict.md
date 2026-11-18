# verdict —— attack-me round 4（stage manuscript・本文 commit d6587f21）

手順は本線（origin/main）の attack-me で読んだ。立場・接地の文献・想定読者の素養は round 3 と同じ。投稿規程と Aims & Scope は 2026-11-19 に Chrome で原文を開き、判定に使う 13 文が逐語で在ることを照合した（curl は今回も 3,038 バイトの拒否のページ）。

## 1. 判定: major revision

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した）。判定を出す条件を満たす。
- 各役: R1 major（「minor との境目」）・R2 major（「決定を限定すれば minor 相当」）・R3 major（「直しは書き方と既存の値の提示で足りる」）・E「直してから回す」・Codex major（別枠）。
- 4b E: 直してから回す → major 以上。
- 判定の推移: round 1 major → round 2 major → round 3 major → round 4 major。round 3 の指摘の解消: R1 は 10 件中 8 件解消・1 件一部（M2）・1 件不採用（n2）、R2 は 10 件中 6 件解消・3 件一部・1 件ほぼ解消、R3 は 7 件中 5 件解消・2 件一部、E は 11 件中 5 件解消・6 件一部、監査役は 13 件中 11 件解消。
- round 4 の重い指摘の性質: 中心は 1 つ（下の Y1: 考察と結論で使う側に渡す「決定」と「費用を省ける」が、プロトコルが実際に選んだものと、論文自身の推奨 (2) と合わない）。round 3 の直し（判断 27 の 5: 考察の第 1 段落に使う側の決定・結論をそれに絞る）から出た指摘で、4 系統（R1・R2・R3・Codex）と監査役が独立に挙げた。ほかは語（gain の 3 義・smoothing gain が未定義）と繰り返しで、読みやすさの観点。新しい計算を求める指摘は無く、R1 N2 だけが既存の値の提示を求める。
- 費用: Opus 5 本（各 9〜12 万 tokens）・Codex 42,536 tokens（本線の台帳 11-19 の 2 回目・累計 84,059。1 回の上限 30,000 を round 3 に続き超えた）。
- 4c 分量: 本文 6,939 語（round 3 の版 c68dfc30 は同じ測り方で 6,739 語・+200）。要旨 250 語・図表 6（図 3・表 3）・文献 33。測った版 d6587f21。測り方は `texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和。

## 2. 一致した指摘（分母は有効な査読 4 本: R1・R2・R3・E）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| Y1 | 考察第 1 段（311）と結論（345）の「決定」と「save the cost of per-person models」が合わない。(a) CoAuthor で選ばれたのは τ = 10^6 / 3×10^5 の本人の当てはめ（239）で、τ = ∞ ではないので、本人のデータ・保存・cold start は省けない。(b) 決定は固定の平滑の下のもので、推奨 (2)（319: 平滑も他人で選び両側に当てる）に従った版では全員に格子の中の有限の τ が与えられ（278）、残りは 3.4e-3〜6.7e-3。推奨どおりの決定（重み）は本文に無い。(c) CS1 は両側の当て直しで確かめていない（限界 336）。「close to giving every writer the same model」の same model は最頻値に近く、最頻値は候補でなく勧めない（143） | R1 N1・R2 major・R3 M-A/M-B（3/4）・監査役 2-2/3-1・Codex 3 | 真（239・278・311・319・336・345 で確かめた）。両側の当て直しで選ばれた τ は「7 つの k すべてで 17 人とも格子の中・τ = ∞ は 0 人」（`experiments/20261112-selection-split-and-smoothing/notes.md` 65 行）。τ の値と重みの換算は notes に無い（summary.json に集計がある見込み・未確認）。設計の判断 |
| Y2 | 「gain」が定義（176: 構造を 3-state HMM に固定したときの 本人 − 同じ構造の共通）のほかに、連鎖との差（235「Against the own chain it gains +0.220」）と平滑の差（smoothing gain・本文に 6 回）に使われる。smoothing gain は要旨（35 に 2 回）から出るが本文に定義の文が無い（143 は「its gain over the shared model」とだけ書く） | E N2・N3・R1 N11・R3 n1・R2 d（4/4） | 真（35・49・143・176・235・303・306・321・335） |
| Y3 | 推奨 (2) を「used here」（317）と書くが、平滑を両側に当てたのは post hoc の 1 構造・1 パネル（336）で、選んだ α = 0.03 は格子の端（276） | R1 N5・R3 m5（2/4）・E N8 | 真（3/4 に数える。E N8 も同じ） |
| Y4 | 但し書き（合成で確かめていない 7 回・推定ではない 5 回・重なる窓に限る 5 回・post hoc 10 回以上）の繰り返しで主文が埋もれる | E N4・R2 nit（2/4）・R1 d・R3 d（評価表の所見） | 真（E の数えた位置で確かめた） |
| Y5 | 要旨・序論の「up to 7e-3」は不安定な k = 12 の値（278）で断りが無い | R1 N10・R2 minor（2/4） | 真 |
| Y6 | 2 つ目の帰無の誤警報率が本文に無い（推奨 (3) で報告を求めている） | R1 N8・R3 n2（2/4） | 真。値は在る: FA' = 0（10 種・k = 5・15。`experiments/20261113-null-from-shared/notes.md` 28〜33 行） |
| Y7 | 図の番号と初出の順が逆: 序論 47 が Figure~\ref{fig:scheme}（配置で Figure 2）を先に引き、Figure 1（fig:example）の初出は 75 | E N9・R2 minor（2/4） | 真（ref と label の行で確かめた）。Springer の規程の逐語は context-A に無い（規程の要件としては未照合。読者の順として指摘は真） |
| Y8 | 要旨の推奨が範囲（重なる窓）を外し、重ならない窓での逆転が要旨に無い。序論 49 の「the positive instance」は未定義 | E N1・R2 minor（2/4）・監査役 2-8 | 真。判断 27 で研究者は「要旨に逆転を入れない」を選んだ（既知の保留）。範囲の句を推奨に 3〜4 語足す案は保留と別 |
| Y9 | 4.4 の「positive for at least 13 of 17 writers」（278）と Table 3 の割合を、Table 2 と同じ断り無しに読む | R2 minor（1/4）・— | 真（1 人。下の §3 にも置く） |

## 3. 1 人だけの指摘（裏取り）

- R1 N2 2 つ目の帰無で、植えた差の下の残り・τ・比が無く、検出の失敗が閾の高さか強い縮みかを区別できない: 真。値は notes に在る（56 行: 植えた差の書き手も k = 5 で 935 人中 873 人が τ = 10^6、3e-2 の段で残りの中央値がむしろ下がる種があり「植えた差の行の混ぜが帰無の平滑の効きを打ち消す向きに働くことがある」、DR' の低さは U' の高さによる）。R3 m4（比の弁別力）・Codex 2 と同じ根。設計の判断（本文に 1〜2 文足すか、限界に 1 句か）。
- R1 N3 最頻値との比べの含意（固定の平滑では書き手のデータを加えた分が中央値で負）: 真（280）。書き方。
- R1 N4 考察 315「Post hoc, lightening the smoothing of the shared model alone ...」は共通の側だけの版まで post hoc に読ませる。178 では post hoc は対称の版だけ: 真。直す。
- R1 N6 重ならない窓の比べでデータ量（記号 1/30）が交絡し、+0.043〜+0.096 を gain と呼ぶのは 176 の定義と合わない（同時に選んだので remainder）: 真（202）。
- R1 N7 要旨が 5e-4 の前提の格子の拡張（post hoc でなく「結果を見た後の変更」・178）を印していない: 真。ただし 178 は格子の拡張に post hoc の印を付けない規則（「we mark the last two post hoc」）。要旨冒頭の exploratory で覆うと読むかは書き方の判断。
- R1 N9 限界 335「no differences between writers」が何の差か曖昧: 真（nit）。R1 N12 自己相関の値: 書き方（nit・既知の未決 7 に近い）。
- R2 writer split の言い過ぎ（315「does not come from」と 274「leaves little room for optimism to show」）: 真。監査役 2-4 も同じ（実質 1/4＋監査役）。
- R2 使う側への翻訳（尤度比の 1 句）: 真（提案）。R2 Table 3 の題の主語のねじれ: 真（nit）。R2 ユーザーモデルの文献の位置づけ: 確かめられない（文献を挙げていない）。
- R3 m1「2 桁」は最大の利得（k = 5）と比べている。k = 1 では HMM3 の +0.012 と残り約 4.8e-4 で約 25 倍: 真（195・274）。要旨の「that gain」は 0.19 を指すので文としては正しいが、同じ k どうしでない。
- R3 m2 α = 0.03 側の「smoothing alone では説明されない」（278）は分母（α = 0.03 での最頻値の利得）を欠く: 真（本文に値が無い）。監査役 3-2（4.4 と 4.5 の「the remainder」の衝突）と同じ箇所。
- R3 m3 4.5 の判定が生の閾（1.8e-3）で、限界の「比で読む」と食い違う: 真（306・335）。
- R3 n3 Figure 1 の例は 3-state HMM の場面: 真（nit）。
- E N5 Figure 1 に中心の仕組み（強い構造で利得が残りに縮む）が無い: 真（提案・図の範囲は判断 27 の 4 で研究者が決めた）。E N6 3.6 の 187・189 が初見で追えない・seeds/negative controls/threshold が未定義: 真。E N7 本文に置かなくてよい細部（274・280 の後半・336・限界の後半）: 真。E N10 考察が「決定」で始まり、序論の貢献（発見）と 1 つにならない・新しさの宣言が 313 の中ほど: 真。監査役 1-1（発見が結論に無い）と同じ根。
- 監査役 1-2 3e-2 の但し書きに行き過ぎ（閾が高すぎるかもしれない）が要旨・考察第 1 段・結論に無い: 真。2-1 要旨で比の地位（not prespecified・中央値どうし）が落ち、事前の規則の結果（検出されない）は要旨に無い: 真。2-3 3e-2 の但し書きが CS1 の決定に広がる（2 つ目の帰無は CoAuthor 15-session だけ）: 真（311・345）。Y1 と同じ段落。2-5「informative only when applied to both sides」は 1 回の確かめからの一般化: 真。2-6 重ならない窓の向きだけの規則を大きさ（0.04〜0.10）に崩す: 真（202「so that only directions are read」）。2-7 4.5「arises」→「can arise」: 真。2-9 7e-3 が他人で選んだ値であることが要旨・序論で消える: 真。3-3「no threshold」（178）と陰性対照の threshold が同じ語: 真。3-4 考察の最頻値の 1 文の緊張・3-5 表題の「what remains of the gain」と定義のずれ: 真（軽微）。1-3(b) 要旨に 15-session の限定が無い（30-session は +1.1e-3）: 真。
- E の 1 文（要旨と序論だけから）: 言えた（「弱い共有モデルに対する利得を、1 人ずつのモデルを作る根拠にしてはいけない」）。迷った点は貢献が発見・手順・推奨のどれか、と要旨後半の値の多さ。

## 4. Codex（別枠・既知の未決と保留 20 件を添えた）

判定 major。4 件:
1. [major] 149「In the joint choice the same holds for the reported per-person minus own-chain difference.」: 同時の選びで共通そのものが選ばれると、報告する 本人 − own chain は 共通 − own chain でゼロにならない（ゼロで切れるのは構造を固定した行だけ）。また他人で選んだ候補は標的では負になりうる: 真（149 の前文「the reported difference is cut off at zero from below when it is chosen」を joint にも「same holds」で及ぼしている）。Codex だけ。直す（1 文）。
2. [major] 比の類似は帰無の移しを保証しない（中央値どうしの比は分布や分母との共変動を隠す）: 真。R1 N2・R3 m4 と重なる（Claude の査読者の一致と重なる）。
3. [major] 小さい本人の重みから「個人モデル不要」への飛躍（重み 3% は費用 3% ではない）: 真。Y1 と重なる。
4. [minor] 限界 335「drift would lower the real remainder」は向きを断定するが、最近の本人の履歴が将来に近ければ利得は増えうる: 真（本文に根拠の文が無い）。Codex だけ。
既知の一覧と重なる再掲なし。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（Y1・監査役 1-1・E N10）考察第 1 段と結論の「決定」をどう書くか。候補: (a) 決定を「固定の平滑での出力」と限り、推奨 (2) の版（両側の当て直し）では全員に格子の中の τ が与えられ残りが 3.4e-3〜6.7e-3 になると 1 文並べ、「費用を省ける」を「共通に替えたとき失う精度は固定の平滑で約 5e-4、両側の軽い平滑で最大約 7e-3（合成で確かめていない）」に替える。CS1 は「固定の平滑で共通そのもの」。考察の冒頭は発見（313 の What is new）に、結論にも発見の 1 文を戻す。(b) 「決定」の枠を考察と結論から外し、発見と推奨に戻す。
- B（R1 N2・R3 m4・Codex 2）2 つ目の帰無の植えた差の下での振る舞い（τ が上の端に張り付く・3e-2 の段で残りが下がる種がある・比の弁別は見ていない）を、本文に 1〜2 文で書くか、限界に 1 句か。
- C（Y8）要旨の推奨に「for overlapping-window symbols」を足すか（逆転そのものは入れない保留のまま）。語は 2 つの post hoc の括弧を 1 つにまとめて空ける。

書き方の直し（計算なし）:
1. Y2・E N3: gain は定義の 1 義に。連鎖との差は「per-person minus own chain」、平滑の差は別の語（例 smoothing effect / the prior mode's advantage）にして 3.3 の Prior mode の段落で 1 回定義。要旨は平易な句に。first generator / first null、per-person fit / model、group / panel、AR(1)-HMM を 1 語に。
2. Y3・Y5・Y6: (2) に「applied post hoc, to one structure and one panel; the chosen multiplier sat at the grid edge」。要旨・序論の 7e-3 を「3 to 7×10^-3」か範囲に。4.5 に「(0 of the other ten negative controls exceeded it)」。
3. Y4・E N7: 但し書きを要旨・該当の結果の節・限界の 1 回ずつに。表の題は節を指す。274・280 の後半・336 の細部を補足へ。限界を主張に響く項目に絞る。
4. Y7・E N9: 序論の図の参照を外すか Figure 1 にする（図の順の入れ替え）。Table 2 の「15-s.」を語に。Figure 3 (b) の題を own chain に。
5. R1 N4: 315 の post hoc の位置を「applying it to both models (post hoc) did not」に。
6. R3 m3: 4.5 の判定に比の尺度の 1 句（閾は比で約 1.0、実データ 0.55〜0.97）。
7. R3 m1: 「2 桁」に k の範囲（k = 5 と 15）を添えるか同じ k どうしで。
8. R3 m2・監査役 3-2: 278 の「not explained by the shared model's smoothing alone」を「vanishes only when the two sides are smoothed differently」の程度に弱め、4.4 と 4.5 の「the remainder」がどの値かを限る。
9. Codex 1: 149 の joint の 1 文を、ゼロで切れるのは構造を固定した行だけと直す。Codex 4: drift の向きを「depends on its form」に。
10. 監査役 2-1・1-2・2-3・2-5・2-6・2-7・2-9・3-3・1-3(b): 要旨の比に not prespecified の印、3e-2 の但し書きに「閾が高すぎるかもしれない」を考察か結論で 1 句、3e-2 を CS1 の決定から切る、「only」を外す、重ならない窓は向きで書く、「arises」→「can arise」、7e-3 は他人で選んだ平滑と 1 語、threshold の語の衝突（3.4 は meaningful-difference threshold と限る）、要旨に 15-session。
11. R2・監査役 2-4: 315 の writer split を「was not changed by ..., a check with little room to show optimism」に。R1 N3・N6・N9、R2 の Table 3 の題・尤度比の 1 句、R3 n3、E N5・N6 は書き方の nit。

## 6. 逸脱・注入の疑い

- 応答はメインが要点と逐語・解消の条件を落とさずに写した（round 3 と同じ扱い）。機械の検査（secrets-filter が 0・応答の絶対パスは一覧・接地・引き継ぎ・context-B の資料の中）は 6 本とも通った。
- 接地の引用の照合（tmp/sources を改行をつないで Grep）: R1 Pohle "heterogeneity between individuals"・Singer "lower order models are nested within higher order" と "random navigational"（どちらも PDF の 2 段組の抽出で行が交互になり、逐語の連続では一致しないが語の並びは原文に在る）・R2 Saeb "should mimic the relationship between the training set" と Aalbers "89.3% (200/224)"・R3 Varma "Another violation of the principle is to do any kind of classifier parameter selection outside the CV loop" と Liu & Meng "too much matching"・E Mensh "Only the central idea of the paper should be touched upon multiple times"。捏造なし。
- 注入の疑い: どの役からもなし。
- Codex の 1 回の token が上限 30,000 を超えた（42,536）。入力が原稿の全文（約 65KB）なので、次の round も同じ程度になる。

## 7. 研究者に問うこと

1. 判定の推移（major が 4 回続いた）を見て、round 5 を回すか（Step 5 の基準では major は直して回す）。
2. 設計の判断 A〜C。
3. 書き方の直し 1〜11 の承認。
