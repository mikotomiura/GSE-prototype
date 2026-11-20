# verdict —— attack-me round 8（stage manuscript・本文 commit 77d5f324）

手順は本線の attack-me で読んだ。立場・接地の文献・想定読者の素養は round 1〜7 と同じ。投稿規程と Aims & Scope は 2026-11-20 に Chrome で原文を開き直し、判定に使う 13 文がページの本文に逐語で在ることを機械で照らした（curl は拒否のページ。"preprint" の語はページに無い）。

## 1. 判定: major revision

- 有効な査読: R1・R2・R3・E の 4 本（全員が接地の文献から基準を逐語で抜き出した）。判定を出す条件を満たす。
- 各役: R1 minor・R2 minor・R3 minor・E「直してから回す」（「語の統一とこの段の組み直しは計算を足さずに済む」）・Codex major（別枠）。
- 4b E: 直してから回す → major 以上。R の 3 人がそろって minor になったのは初めて。
- 判定の推移: round 1〜7 major → 8 major（8 回続けて major）。R の推奨は round 7 major 1・minor 2 → round 8 minor 3。
- round 7 の指摘の解消: R1 9 件中 7 解消・1 一部（N3）・1 未解消（不採用の N5）＋参考の EM は一部。R2 11 件中 9 解消・2 一部（M1・m5）。R3 8 件中 5 解消・2 一部（新規 3・4）＋先頭の記号は解消。E 10 件中 2 解消・7 一部・1 未解消（見出し）。監査役 13 件中 9 効いている・3 一部・1 未解決（2-5）。
- この round の重い指摘の性質: 中心は、round 7 の計算 A（入れ替えの対照）の本文での読み方（Y1）。数は正しいが、「残りの半分以上」が分け前に読め、事前に決めた読みの規則（差 ≥ 残りの半分）として書かれていない。ほかは書き方（帰無の限定・post hoc の印・語の統一・要旨の密度）。round 7 の直しと round 8 の前の削りから出たもの: Y1・Y4・Y5・Y6（carryover で直したと書いた言い方そのもの）・E の gain の後退。
- 費用: Opus 5 本（各 9.4〜12.5 万 tokens）・Codex 約 43,700 tokens（本線の台帳 11-20 の 12 回目・累計 505,853）。
- 4c 分量: 本文 7,263 語（round 7 の版 ed297dd4 は同じ測り方で 7,502 語・−239）。要旨 248 語・図表 6・文献 33・18 頁。測った版 77d5f324。測り方は `texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和。

## 2. 一致した指摘（分母は有効な査読 4 本: R1・R2・R3・E）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| Y1 | 入れ替えの対照の「more than half of the remainder goes with the writer's own data rather than with refitting」は、示した数から導けない（自身 − 入れ替え 4.7e-3・2.5e-2 は残り 3.4e-3・5.2e-3 より大きく、入れ替えは共通にも負ける）。差は分け前ではなく「自分のデータが助ける分」と「他人のデータが害する分」の和で、限界の「中央値は分解ではない」と噛み合わない。序論・決定の段・結論にも同じ句 | R1 1・R2 1・R3 2・E 1（4/4）・監査役 2-a・Codex major | 真（49・282・321・350）。数は notes の結果 A と合う。「半分以上」は条件で先に決めた読みの規則（D ≥ Rs/2）の当てはめで、本文が規則を書いていない |
| Y2 | 序論と結論の「planted differences up to 3e-2 were not reliably detected」にどの帰無かが無い（第 1 の帰無では 1e-2 が検出された・308） | R1 2・R3 1（2/4）・監査役 3-b | 真（49・350。要旨は "under that null" で限っている）。round 8 の前の削りで結論から帰無の句が落ちた |
| Y3 | 要旨の「Neither shows a per-person difference」の根拠が 1 つ目の値にしか無い。2 つ目の値（両側の版）の限定（時間の近さ・合成で確かめていない）が要旨に無い | R1 4・R3 3（2/4）・監査役 1-b | 真（35） |
| Y4 | 3.4 は「we mark the last four post hoc where they are reported」と約束するが、4.4 の 3 つの対照・選ばれた τ・序論と考察と結論の入れ替えの対照に post hoc の印が無い | R1 8・R3 nit（2/4）・監査役 2-b | 真（180・280・282・49・321・350） |
| Y5 | 先頭の記号を除いた採点の結果（4 つの値）が方法の節（3.4）に置かれている | R2 6・R3 nit・E 6（3/4）・監査役 1-d | 真（178） |
| Y6 | 考察の「left the median remainder unchanged」が Table 3 の k = 15（4.1e-4 と 7.4e-4）と見かけで食い違う。変わらないのは「報告した半分で選んだ場合との差の中央値」 | R2 5・R3 nit（2/4）・監査役 3-a | 真（319・276）。round 7 の m2 の直しの言い方そのもの |
| Y7 | 「also when its prior leaves out the other writer as well」の its がどちらの当てはめか読めない | R3 nit・E 8（2/4） | 真（282） |
| Y8 | 語の揺れ: 主の平滑が "fixed smoothing" / "smoothing of the main analysis" / "fixed base smoothing"、両側の版が "lightest smoothing ... applied to both" / "smoothed alike" / "symmetric refit"。要旨で gain が平滑の効き（"the shared model's gain ... from removing its smoothing"）にも使われる | E 2・E 4・R2 8（2/4） | 真（35・49・273・280・321・350） |

## 3. 1 人だけの指摘（裏取り）

- R1 3: 要旨・序論の「30 to 55 times below it」は、α = 1 の \hmmthree の利得を α = 0.03 の残りで割っている（平滑の違う 2 つの値の比）: 真（35・49・315）。
- R1 5: EM の「keeps the better start」の基準（学習の記号での MAP の目的関数）と共通のモデル自身の始点が無い: 真（137）。
- R1 6: remainder の定義（同時の選択）を、構造を固定した両側の版にも使っている: 真（178）。
- R1 7: Pohle 2017 は交差検証を実装しておらず（"we did not implement the latter"・tmp/sources で確かめた）、「cross-validated likelihood with them, tend to choose too many states」は言い過ぎ: 真（70・340）。
- R1 9: Table 2 の k = 15 の τ に「16 of 17」が無い: 真（256）。
- R2 2: 入れ替えの差（k = 15 で 2.5e-2）と、検出できなかった植えた差（3e-2）が同じ桁なのに、つないでいない: 真（提案）。
- R2 3: 決定の段の冒頭「the protocol does not show here that a per-person model is worth its cost」に固定の平滑の限定が無い: 真（321）。費用の目安（\arthree は 2,033 母数・待つ記号数）: 提案。
- R2 4: 入れ替えの対照を推奨に入れていない: 真（提案・設計の判断）。
- R2 7: 「record-wise splits that mix a person's days」は Saeb の定義（"regardless of which subjects they belong to"・tmp/sources で確かめた）と合わない: 真（45・57）。
- E 3: 要旨の 4〜6 文目の照応（the first / the second / that null）と未定義の語: 真。
- E 5: 但し書きの繰り返し（合成で確かめていない 6 か所・格子の端 5 か所・時間の近さ 4 か所）: 真。
- E 7: 序論の貢献の段に入れ替えの対照の文が入り重くなった: 真（49）。
- E 9: 具体的な適応の場面が一度も出ない: 真（提案）。
- E 10: 考察の段の順（決定の段が 4 段目）: 真（提案）。
- E 11: 4.3 と 4.4 の見出しが長い: 真（nit）。
- E 12: 要旨に文献の穴の文が無い: 真（nit）。
- 監査役 1-a: 要旨の推奨から「平滑は両側に当てる」が落ちている（"smoothing post hoc, for one structure"）: 真（35）。本文の推奨 (2) にはある。
- 監査役 1-c: 決定の段の重み 24%・91% に「換算」の断りが無い: 真（321）。
- 監査役 1-e: 要旨と結論の約 5e-4 に 15-session のパネルの限定が無い: 真（35・350）。
- 監査役 2-c: 考察の「about 6 and 13 times larger」は条件の外（not prespecified の印が無い）: 真（319）。
- 監査役 2-d: 「so a lighter smoothing may give more」は条件の読みの向きへ寄る: 真（280）。
- 監査役 2-e: 考察の冒頭の「0.05% to 0.5%」が地位の違う 2 つの値を幅として並べる: 真（315）。
- 監査役 3-d・3-e: 6 つの数え方のあいまいさ・context-B の括弧の項目数（メインの資料）: 真（軽い）。

## 4. Codex（別枠・既知の未決と保留 31 件を添えた）

判定 major。3 件（既知の一覧の再掲なし）:
- 入れ替えの対照から割合を帰属できない（Y1 と重なる）。
- 同じ k 単位・同じ τ でも、セッションの長さが違えば記号数と実効の重み N/(N + τ) が変わる。入れ替えは履歴の本人性だけでなくデータの量と縮みの強さも変える（Codex だけ）: 真。条件は「v の学習の k 単位」で、記号数はそろえていない（conditions.md の A）。時間の近さとは別の交絡。
- 共通の AR-HMM も直前の記号と状態の濾過で履歴に応じて予測を変えるので、比べは「個人の情報の利用」全般ではなく、本人の履歴でパラメータを適応させる追加の価値（Codex だけ）: 真（概念の限定・序論 43・49）。

## 5. 直す順（案）

設計の判断が要るもの（研究者に問う）:
- A（Codex）入れ替えの記号数の交絡: (a) 本文に交絡として 1 句書く（計算しない）。(b) 組ごとの記号数の比と D の関係を計算する（HP Z2・post hoc がまた増える）。
- B（R2 4）入れ替えの対照を推奨に入れるか: (a) 入れない（1 パネル・post hoc・時間の近さを分けない）。考察で「点検の候補」として 1 句。(b) 推奨に 1 行足す。

書き方の直し（計算なし）:
1. Y1: 入れ替えの対照の読みを、事前に決めた規則として書く。「自分の回で当てた当てはめは、同じ τ と同じ作りの事前で他の書き手の回に当てたものに、残り全体を超える差で勝つ（事前に決めた読みの規則 = 差 ≥ 残りの半分 を満たす）。入れ替えは共通にも負けるので、差は分け前ではなく、他人のデータの害を含む」。序論・決定の段・結論は「the writer's own sessions predict better than another writer's under the same τ」程度にそろえる。
2. Y2: 序論と結論に「under the second null (post hoc)」。
3. Y3・監査役 1-a・1-e・E 2・E 3・R1 3: 要旨を組み直す。2 つの値を別々の文にし、それぞれの限定（5e-4: 15-session・帰無と平滑の効き / 両側: 構造固定・post hoc・時間の近さ・合成なし）を置く。平滑の効きを gain と呼ばない。倍率は「at the fixed smoothing」の値どうしだけにするか外す。推奨に「applied to both」。
4. Y4: 3 つの対照・τ の報告・序論と考察と結論の入れ替えに post hoc。
5. Y5: 先頭の記号の 4 つの値を 4.4 へ 1 文で移す（3.4 は手続きと参照だけ）。
6. Y6: 「left the median difference from choosing on the reported half at zero」。
7. Y7: 「also when both fits use a prior that leaves out the other writer」。
8. Y8: 主の平滑を "fixed base smoothing"、両側の版を "symmetric refit" に統一（要旨は初出で言い換え 1 回）。gain は \hmmthree の per-person − shared だけ。
9. R1 5: 「keeps the start with the higher MAP objective on the training symbols」と共通の始点。
10. R1 6: remainder の定義に「also in the symmetric refit, whose structure is the jointly chosen one」。
11. R1 7: Pohle の 2 か所を「information criteria, and asymptotically cross-validated likelihood」に。
12. R1 9: Table 2 に「(16 of 17)」。
13. R2 3: 決定の段の冒頭に「At the fixed base smoothing」。
14. R2 7: Saeb の 2 か所を「a person's records」に。
15. 監査役 1-c・2-c・2-d・2-e: 決定の段の重みに「(a conversion)」、6・13 倍に not prespecified、「a lighter smoothing may give more」を「values beyond the grid edge are unknown」に、考察の冒頭の幅を 2 つの値に分ける。
16. R2 2・E 7・E 5: 序論から入れ替えの文を外し（4.4・考察へ）、考察の確かめた段に「入れ替えの差は植えた g と同じ尺度ではない」を 1 句。繰り返しの但し書きは限界と結果に 1 回ずつ。
17. Codex 3: 序論に「the shared model also conditions on the writer's recent symbols; the question is the added value of fitting parameters to the writer」を 1 句。
18. E 9・E 10・E 11・E 12: 考察で適応の場面の例を 1 文（測っていないと書く）・決定の段を 2 段目へ・見出しを短く・要旨の穴（語数が許せば）。
19. メインの資料: context-B の「残りの半分以上」の言い方と変更の括弧の項目数（次の round）。

## 6. 逸脱・注入の疑い

- 依頼文は brief-*.md に保存し、起動の文では「このファイルを Read してその指示に従う」とだけ渡した。
- 応答は SubagentHandback の入力をトランスクリプトから機械で取り出して tmp/<名>.raw.md に置き、機械の検査（secrets-filter が 6 本とも 0・応答の絶対パスは一覧・依頼文・引き継ぎの中）を通してから写した。
- 接地の引用の照合（tmp/sources を改行と空白をつないで照らした）: R1 Monaco "plagued by overfitting and poor generalization, especially when the sample size is small"・Pohle "we did not implement the latter"、R2 Saeb "regardless of which subjects they belong to"・Aalbers "We evaluated model accuracy on a person-to-person basis in out-of-sample observations"、R3 Varma "choosing the minimum resampled error will give a biased estimate"・Liu & Meng "intestable assumption"、E Mensh "Resist the temptation to use a different word to refer to the ... same concept"（頁の区切りをまたぐ）。捏造なし。
- 注入の疑い: どの役からもなし。
- Codex の 1 回の token が上限 30,000 を超えた（約 43,700。入力が原稿の全文で構造的に超える・round 6・7 と同じ）。

## 7. 研究者に問うこと

1. 設計の判断 A・B。
2. 書き方の直し 1〜19 の承認。
3. 直した後に round 9 を回すか（判定は 8 回続けて major。ただし R の 3 人は初めてそろって minor で、E の理由は書き方だけ）。
