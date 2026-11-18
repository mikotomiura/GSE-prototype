# 引き継ぎ（意図の監査役・round 2 → round 3）

round 2 の版は commit 9a4c1d34、今回の版は c68dfc30。行番号は今の main.tex で確かめてください。

| round 2 の指摘 | 著者の採否と対応 |
|---|---|
| 1-A 推奨の誤警報率が要旨と結論に無い | 要旨と結論の推奨は「report the smallest planted difference reliably detected」まで（誤警報率は考察の推奨 (3) だけ） |
| 1-B 要旨の推奨に「平滑は両側に当てる」が無い | 要旨・結論に「apply the smoothing to both models」 |
| 1-C 要旨と結論に「構造と縮みは他人で選ぶ」が無い | 要旨・結論に「choose structure, shrinkage and smoothing on other people」 |
| 1-D 軽い平滑での値を大きさとして読まない、が要旨と結論に無い | 要旨・結論は「Neither value shows a per-person difference」に替えた |
| 2-A 4.3 の見出しと Table 2 の注が 30-session と合わない | 15-session に限った |
| 2-B 考察 1 段落目が平滑しだいの大きさから設計の含意を引く | 「what remains against a strong comparison is small at either smoothing」に替えた |
| 2-C 要旨の閾に CoAuthor の記録の長さの限定が無い | 要旨の感度の文を新しい帰無の結果に替えた |
| 2-D「2 桁以上」は k = 1 では成り立たない | 「more than two orders of magnitude below that largest gain」に |
| 3-1 post hoc の印が序論・考察・結論で落ちる | 印を付けた |
| 3-2「両方のために選んだ」に読める | 「chosen for the shared model ... applied to both models」に |
| 3-4 限界 1 項目目の参照先に記号化の値が無い | 4.2 に重ならない窓の値を入れ、参照を 4.2 に |
| 3-5 one decision per panel と書き手ごとの選び | 「one objective per panel」に |
| 3-6 最頻値の古い読みの名残 | 最頻値の診断を補足へ移した |

round 2 の後、著者は「実データの共通のモデルそのものから合成の書き手を作る帰無（post hoc）」を足し、要旨・序論・3.5・4.4・考察・限界・結論の読みを替えた（意図は context-B.md の改訂版）。

今回は、上の対応が今の版で効いているかを確かめ、そのうえで改訂された意図と対象物の食い違いを探してください。
