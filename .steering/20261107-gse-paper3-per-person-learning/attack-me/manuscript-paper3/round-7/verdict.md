# verdict —— attack-me round 7（stage manuscript・本文 commit ed297dd4）

手順は本線（origin/main）の attack-me で読んだ。立場・接地の文献・想定読者の素養は round 1〜6 と同じ。投稿規程と Aims & Scope は 2026-11-20 に Chrome で原文を開き直し、判定に使う 13 文がページの本文に逐語で在ることを機械で照らした（"preprint" の語はページに無い）。

## 1. 判定: major revision

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した）。判定を出す条件を満たす。
- 各役: R1 major・R2 minor・R3 minor・E「直してから回す」（「直す量は小さい」「新しい計算は要らない」）・Codex major（別枠）。
- 4b E: 直してから回す → major 以上。
- 判定の推移: round 1〜6 major → 7 major（7 回続けて major）。R の推奨は round 5 major 1・minor 2 → round 6 major 1・minor 2 → round 7 major 1・minor 2（R1 が minor から major へ、R2 が major から minor へ。R3 は minor のまま）。
- round 6 の指摘の解消: R1 7 件中 4 解消・2 一部・1 未解消（不採用の m4）、R2 8 件中 5 解消・3 一部、R3 9 件中 7 解消・2 一部、E 10 件中 4 解消・6 一部（m-E は不採用）、監査役 14 件中 11 効いている・2 一部・1 判定できない。
- round 7 の重い指摘の性質: 中心は round 6 の直しで足した対照（同じ平滑の最頻値 2.5e-5）の扱い（Y1）。要旨の詰め（判断 36）で落ちた限定（CS1 の固定の平滑・2 桁の k・構造の固定・not prespecified）を監査役が拾った。新しい計算の要否は役で分かれる（R1・R3・R2 は計算か書き換えのどちらかで閉じる、E は計算不要）。
- 費用: Opus 5 本（各 8.9〜12.1 万 tokens）・Codex 約 44,000 tokens（本線の台帳 11-20 の 7 回目・累計 299,859）。
- 4c 分量: 本文 7,502 語（round 6 の版 e6fdad49 は同じ測り方で 7,219 語・+283）。要旨 247 語・図表 6・文献 33・18 頁。測った版 ed297dd4。測り方は `texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和。

## 2. 一致した指摘（分母は有効な査読 4 本: R1・R2・R3・E）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| Y1 | 足した対照（同じ平滑の最頻値・+2.5e-5）は τ → ∞ の極限で、選ばれた当てはめ（τ = 10^3〜10^4・本人の重み 24〜91%）と事前の重みが合わない。書き手のデータの寄与と、事前を作り直したことの寄与を分けない。282 は自分でそう書くのに、要旨・序論・決定の段・結論は「2.5e-5 を超えた」を書き手のデータを使わない対照に勝ったと読ませる。−∞ の 2 人は対照の退化 | R1 N1 major・R3 新規 1 major・R2 M1 major（入れ替えの対照）（3/4）・監査役 2-1 | 真（37・51・282・321・350）。条件（判断 35）は最頻値を「τ → ∞ の行き先」として主に置いた。対照が選ばれた τ に合わないのは設計の結果。設計の判断 |
| Y2 | 要旨の「3.4 and $5.2\times10^{-3}$」で 3.4 に桁が無い | E major・R1 N8・R2 m5（3/4） | 真（37）。round 6 の D から |
| Y3 | 要旨と序論の「planted differences up to 3e-2 were not reliably detected」に、事後の第 2 の帰無・固定の平滑の限定が無い（第 1 の帰無では 1e-2 が検出された・308） | R1 N3・R2 m7・R3 新規 4（3/4）・監査役 2-3 | 真（37・51） |
| Y4 | 設計者が決定に関わる比べの値（3.4〜5.2e-3・正の書き手 88〜94%）から何を結論するかが閉じていない。要旨と結論はどちらの値が決定に関わるかを言わない | R1 N2 major・R3 新規 5・R2 m3・E M2 major（4/4） | 真（37・51・321・350） |
| Y5 | 系列の境界: 先頭の記号を初期分布から採点するが、AR-HMM と own chain の先頭の分布が本文に無い。1 セッション約 660 記号で先頭 1 記号の差 0.33 nats が約 5e-4 に当たり、残りと同じ桁 | R1 N4 major・R2 m1（2/4）・Codex major | 真（180。補足 S3 の予定の文には「per-state first-symbol distribution (AR-HMM)」「the writer's first-symbol frequencies for the own chain」があるが本文に無い）。桁の見積もりは査読者の推論で、実の大きさは未測定。設計の判断 |
| Y6 | 4.4 の見出しで post hoc が、事前に決めた共通だけの当て直し（vanishes）にも掛かって読める。k = 12 は消えるのでなく負 | R1 N6・R3 新規 2（2/4）・監査役 2-2 | 真（275・182） |
| Y7 | 要旨の両側の版の文で構造を固定したことが読めない（構造も選び直したように読める） | R3 新規 6（1/4）・監査役 1-2 | 真（37）。序論にも無い |
| Y8 | \PENDING のマクロと注が残る | E・R1 N9・R2 n2・R3 新規 7（4/4・nit） | 真（20〜21） |
| Y9 | 要旨・決定の段の密度と但し書きの繰り返し（合成で確かめていない 8 か所・格子の端 5 か所）、282 の 1 段の詰め込み | E minor ×2・R2 m5（2/4） | 真 |

## 3. 1 人だけの指摘（裏取り）

- R2 M2 major・Codex: 結論 350「The protocol chose a strongly shrunk fit」に固定の平滑の限定が無く、決定に関わる版（重み 91%）と逆の像: 真（350）。
- R3 新規 3・監査役 3-1: 182「Four changes were made after seeing results」に今回の対照と τ の報告が入っていない: 真（182・282）。
- 監査役 1-1: 重み 24%・91% に「他の書き手で選んだ τ の換算で、価値の推定ではない」の断りが無い（"carry 91% of the weight"）: 真（282・321）。
- 監査役 1-4: 要旨の CS1 から「固定の平滑で」が落ちた: 真（37。判断 36 の詰めより前から無い）。
- 監査役 1-5: α は共通の側で選んだことが結論と要旨に無い: 真（350・37）。
- 監査役 2-4: 要旨と序論の「two orders of magnitude」に k = 5・15 の限定が無い（k = 1 は約 25 倍）: 真（37・51）。
- 監査役 2-5: 要旨から比の not prespecified が落ちた: 真（判断 36 の詰めで外した）。
- 監査役 2-6: 結論が合成の帰無を「価値を示さない」の根拠に混ぜる: 真（350）。
- 監査役 3-2: context-B の限界の「重ならない窓では利得は 2 桁落ちない」は古い: 真（メインの資料の誤り。本文は正しい）。
- 監査役 3-4: 序論「the second exceeds the same comparison」の主語と目的語のずれ: 真（51）。
- E: cell が 3 つの意味（記号の格子・数え上げのます・panel × k）、gain が最頻値にも使われる: 真（109・143・180・51・282・321）。序論で prior mode と fixed base smoothing が未定義: 真（51）。−∞ の説明が無い・Dirichlet・percentile bootstrap: 真。見出しが長い（275 は 37 語）: 真（nit）。
- E M2 の後半・R1: 決定に関わる比べを見せる図が無い: 真（提案）。
- R1 N5: AR3 と own chain の lag-1 自己相関の値（既知の未決 7・23）: 真。重く数えない。
- R1 N7: 319「The remainder is a value of the chosen structure」は 1 次の連鎖の行に定義した語を使う: 真。
- R2 m2: 考察 319「left the median remainder unchanged」は表 3 の k = 15（Fixed +4.1e-4・Split +7.4e-4）と見かけが合わない。278「pairs are not positive」の主語: 真。
- R2 m4: 推奨 (2) の平滑の選び方（共通の目的で α → τ の 2 段）が読めない: 真（325）。
- R2 m6: 180 は IQR を報告すると言うが表 2・3 に無い: 真（180）。
- R2 n1・Codex: 考察 315「is not specific to keystrokes」「makes any per-person fit look good」の断定、47・204「cannot carry the dependence」は「今の推定の条件で依存を捉えなかった」に限るべき: 真（47・204・315）。
- Codex（major）: 平滑を変えると EM の到達解も変わる。足した対照は当て直しをしないので、局所解・停止の精度による差を統制しない。初期化・再始動・収束の判定を本文で要約すべき: 真（139 は「initialization are in S3」だけ）。Codex だけ。

## 4. Codex（別枠・既知の未決と保留 27 件を添えた）

判定 major。4 件（既知の一覧の再掲なし）: EM の到達解の差（Codex だけ）・系列の境界（Y5 と重なる）・「cannot carry」の言い過ぎ（R2 n1 と重なる）・結論の strongly shrunk（R2 M2 と重なる）。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（Y1）対照: (a) 計算する。同じ α・同じ τ の選びの規則で、対象の書き手の k 単位を別の書き手の同じ長さの k 単位に置き換えた当てはめ（入れ替えの対照）を、対象の書き手の残りで採点する。条件を先にコミットし、HP Z2 で回す。(b) 計算しない。要旨・序論・決定の段・結論から「2.5e-5 を超える」を外し、4.4 に「この対照は選ばれた当てはめと事前の重みが合わず、書き手のデータの寄与を分けない」と書く。
- B（Y5）系列の境界: (a) 先頭の記号を除いた残り（固定の平滑と両側の版・k = 5・15）を計算して 1 文。A(a) と同じ HP Z2 の回に載せられるか確かめる。(b) 本文で先頭の分布を 1 句定義し、先頭の記号の割合（約 1/660）と、未測定であることを限界に書く。
- C（Codex）EM の到達解: (a) 本文に初期化・再始動・収束の判定を 1 文で要約し、限界に 1 句。(b) 再始動の間の残りの変動を計算する。

書き方の直し（計算なし・A〜C の答えに依らない）:
1. Y2: 要旨を「$3.4\times10^{-3}$ and $5.2\times10^{-3}$」に。
2. Y3: 要旨と序論の植えた差の文に「at the fixed smoothing, under the post hoc null」程度の限定。
3. Y4・E M2: 要旨と結論で「the second bears on the decision」を言い、決定の段に「意味のある差の閾を置かないので、この大きさ（約 0.3〜0.5% の perplexity）が費用に見合うかは判定しない」を 1 文。
4. Y6: 4.4 の見出しを「... vanishes (except at k = 12) when only the shared model's smoothing is lightened and, post hoc, returns when ...」の語順にし、短くする。
5. Y7・監査役 1-4・1-5・2-4・2-5: 要旨の両側の版の文に構造の固定、CS1 に固定の平滑、2 桁に k = 5・15、比に not prespecified、α は共通の側で選んだこと。語数は A(b) なら 2.5e-5 の文を外して作る。
6. Y8: \PENDING を消す。
7. R2 M2・Codex: 結論の strongly shrunk に「At the fixed base smoothing」、両側の版の重みと合成で走らせていないことを並べる。
8. R3 新規 3: 182 の一覧を 5 つに。
9. 監査役 1-1: 重みに「他の書き手で選んだ τ の換算」の 1 句。
10. 監査役 2-6: 結論で、帰無は「差を示さない」、最頻値と平滑は「価値を示さない」の根拠に分ける。
11. E: cell を panel × k だけに（数え上げは entry・記号の格子は square）、gain を定義どおりに限る（最頻値は beats ... by）。序論で prior mode と fixed base smoothing を言い換える。−∞ に 1 句。282 を 2 段に割り、−∞ の扱いと「中央値は足せない」は補足へ。
12. R1 N7・R2 m2・m4・m6・n1・Codex の言い過ぎ: 319 の語、二分の言い方、推奨 (2) の選び方、IQR は「in S7」に限る、「is not specific」「cannot carry」を限る。
13. メインの資料: context-B の古い限界の文を直す（次の round）。

## 6. 逸脱・注入の疑い

- 依頼文は brief-*.md に保存し、起動の文では「このファイルを Read してその指示に従う」とだけ渡した。
- 応答は SubagentHandback の入力をトランスクリプトから機械で取り出して tmp/<名>.raw.md に置き、機械の検査（secrets-filter が 6 本とも 0・応答の絶対パスは一覧・依頼文・引き継ぎ・context-B の資料の中）を通してから写した。
- 接地の引用の照合（tmp/sources を改行と空白をつないで照らした）: R1 Monaco "the effect of parameter smoothing is diminished"・Pohle "additional states may be able to capture"、R2 Saeb "Subject identification, which we know to be relatively easy"・Aalbers "naive" baseline、R3 Varma "choosing the minimum resampled error will give a biased estimate"・Liu & Meng "relevance robust-ness trade-off"（行をまたぐハイフンで 26〜27 行）、E Mensh "Focus on a single message"。捏造なし。
- 注入の疑い: どの役からもなし（4 役が main.tex 20 行の注を著者の作業メモと判断した）。
- Codex の 1 回の token が上限 30,000 を超えた（約 44,000。入力が原稿の全文で構造的に超える・round 6 と同じ）。

## 7. 研究者に問うこと

1. 設計の判断 A〜C。
2. 書き方の直し 1〜13 の承認。
3. 直した後に round 8 を回すか（判定は 7 回続けて major。R の推奨は minor 2・major 1 のまま）。
