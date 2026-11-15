# review-R2（応用・実務家・paper-reviewer・opus）—— round 2

## 接地
Horvitz ら "balance the context-sensitive costs of deferring alerts with the cost of interruption"・"A design that overlays a graphical notification … is more costly than an alert that appears and disappears autonomously"・"A correlation coefficient of 0.9 was found between the user tagged criticality and the automated assignment"。Hart ら "45% of the studies used a cross-validation that overestimated the capabilities of the models."・"Omitting the participant identifier resulted in a reduction in the predictive performance of both models."・"it was suitable for modeling the states of the participants idiographically."・"at least 10 to 20 measurement points."

## carryover の判定
1 一部（採る案の閾値・頻度・割付の比が無く、退けた案との区別が読めない）／2 解消（別の行と齟齬・F）／3 一部（尖りが一般形のまま・1 人ごとの予測の計画が無い）／4 解消（新しい問題・C）／5 一部（道具の入力と出力が無い）／6 一部（差の列が先行との差になっていない）／7 一部（採る案の中断の回数が無い）／8 解消／9 一部（1 人あたりの申告の数が無い）／10 解消。

## 評価表
a 3／b 3／c 3／d 4／e 3／f 3。

## 指摘
- [major] A 尖り（§1「どちらもそのままでは成り立たなかった。用意した推定器では…」）が「人をまたぐ評価に限る」（§3）を落としている。Hart らは人をまたぐ評価が失敗し 1 人ごとなら効くことを示しており、この研究の未検査の箇所を指す。§4 の 3 名は対応の検査で、予測の 1 人ごと版にならない。解消: 尖りに「人をまたぐ評価で」、1 人ごとの予測を「これから」に置くか確かめられない理由を書く、§5 の差に Hart との関係。自信 高。
- [major] B 無作為の割付で比べるアウトカムが書かれず、§6（系の効果・身体回帰・再開の速さを主張しない）と緊張する。採る規則（停滞の始まりからの経過時間）と退けた規則（止まりの長さ・停滞の時計）の区別が読めず、採る案の頻度が無い。解消: 割付で比べる量と §6 に当たらない理由・採る規則の閾値と 1 時間あたりの回数・停滞の始まりの定義。自信 中。
- [major] C 定義しだいの所の根拠が足した文で弱まった（長さで調整すると負の定義が無くなる＝長さの交絡で説明されうる・逆転は見た後の基準）。§2「結論が動く」がこれより強い。解消: 「調整前の向きが定義で変わる」に限る・§2 を「定義によっては結論が動きうる（調整と事後の基準の限定つき）」に・事前の基準で動いた結論があれば先に。自信 中。
- [major] D 尖りの手順の先行が未調査で、差の列が「自分のしたこと」になっている（Horvitz・Hart も使う前に確かめている）。解消: 手順の先行を 1 ラウンド探す・差の列を「先行は X を示した／この研究は Y」の形に。自信 中。
- [minor] E 公開の道具の入力と出力が無い。最小の入力と出力を 1〜2 行・GSE のアプリが地図のどの出力で何を変えたかを 1 例。自信 中。
- [minor] F 「停滞について読める所は今は無い」と学習器の 0.54〜0.57 が並び、「未確定」の扱いが無い。解消: 「事前登録した検査の中には無い。探索で帯の端に届く学習器がある」。自信 中。
- [minor] G 3 名の 1 人あたりの申告の数が無い。自信 中。
- [minor] H 帯を凍結した時点が、見ていない書き手を開く前か後か読めない。自信 低。
- [nit] I 尖りの漏れの文に限定が無い。自信 高。

## 総合: major
表は大きく良くなった。残る major は A・B・C・D。A〜C は文面と計画の直しで閉じられ、D は 1 ラウンドの文献調査が要る。

## 読めなかった範囲
hart2022 の後半（参考文献と推定）・§7 のパス。注入の疑いは無い。
