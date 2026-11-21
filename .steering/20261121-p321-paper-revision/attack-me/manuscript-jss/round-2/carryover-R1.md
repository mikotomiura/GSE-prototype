# carryover-R1 — あなた（R1）の round 1 の指摘と、その後（attack-me・stage `manuscript`・round 2）

round 1 で読んだのは、同じ論文の前の版（EMSE に投稿した版）である。行番号は前の版のもので、いまの原稿とは合わない。いまの原稿では、下の「対応」に書いた節を探して判定すること。
round 1 の総合の推奨: major revision。

判定のしかた: 各指摘について「解消 / 部分的に解消 / 未解消 / この版では確かめられない」と理由（いまの原稿の位置と逐語）を書く。再掲は求めない。

| # | round 1 の指摘（要約） | 裏取り | 研究者の採否 | 著者の対応（いまの原稿で見る場所） |
|---|---|---|---|---|
| M1 | 分子の差の大半は帰結が不明の単位（DF3 = 後で戻る・DF5・D2 の研究期間の終わり）なのに、全定義で「未解決」と数えている | 真 | 採る（主の定義は変えず、打ち切りとしての感度分析と区間を足す） | §5.4 Analyses added after the first version（打ち切り・区間 [A, U]・クラスタ・長さ・P1TA）／ RQ1 の "How much of the difference rests on DF3" ／ §8 Internal validity |
| M2 | 吟味する概念 unaided resolution を、指標そのもので定義している（概念と指標が一致してしまう） | 真 | 採る（名前と用語をそろえる） | 名前を U（unconsulted share）・A（unaided-resolution share）・A\|R に替えた。§3.1 Definitions に r_i・c_i が何を記録しているかを足し、§3.4 Constructs and indicators の冒頭に「unaided resolution は、観察した単位の中で記録された相談なしに解決したことの略記」と書いた |
| M3 | D2 の相談と解決の指標を、原典のコーディングの意味から見て転用してよいか（選択的なコーディング・P1TA） | 真 | 採る | §4.2（配信者の選択的なコーディングと P1TA の逐語）／ §5.4 の P1TA の感度分析 ／ §8 Construct validity |
| M4 | 成果コード（DF1〜DF5）と相談のコードに、コードごとの一致度が無い | 真（原典の κ は episode と activity の 2 つだけ） | 採る（改訂の範囲に含めた） | ⚠️ メインの記録では、この指摘に専用の対応を書いた記録が見つからない。§4.1 は原典の κ（0.75・0.84）を報告し、§8 に単一コーダーの限界がある。解消したかをあなたが判定すること |
| M5 | 「相談なし＝自力で解決」と読む誤用の実例が無い（藁人形の危険） | 真 | 採る（探して、無ければ主張を予防的な報告の推奨に絞る） | 実例は見つからなかった → 主張を絞った（序論）。⚠️ 検索の範囲を書く §2.5 は、記録付きの検索のやり直しの途中で**この round の対象外**。序論と §7 の主張の強さだけを見ること |
| m1 | D1 の 4 つの相談の定義は入れ子で、広げる方向にしか動かない | 真 | 採る | 入れ子であることの注（§4.1 の段落 "Consultation"） |
| m2 | 二値の相談の指標は単位の長さに依存する | 真 | 採る | 長さで重みをつけた版（§5.4 Duration・RQ2 の "Duration (added analysis)"） |
| m3 | D2 の本文中の相談を拾う作業が網羅的に記録されておらず、独立なコーディングでもない | 真 | 採る | §5 の小節 "Use of large language models"（版・日付・渡したもの・再現率は不明と書いた）／ §8 Reliability |
| m4 | 脅威の節が形をなぞるだけで、構成ごとの脅威の向きが無い | 真（評価の判断） | 採る | §8 Construct validity を構成ごとの段落（Consultation〔definition / underrepresentation〕・Resolution〔definition and bias〕）に分けた |
| m5 | 貢献 (i) の「厳密な分解」は会計上の恒等式 | 真 | 採る | 序論の貢献の並べ替え・序論と §3.3 で "accounting identity" / "an identity … not an additional analysis" と明記 |
| m6 | 声明の置き場所（EMSE の規程） | 真 | 出し先が替わったので、JSS の形（文献表の前の声明・生成 AI の申告の節）にした | `declarations.tex` |
| n1 | κ を百分率で書いている | 真 | 採る | §4.1 で 0.75・0.84 にした |

round 1 の後に著者が足したもの（新しい穴が無いかを見る）: b/(a+b)（未解決の単位のうち相談が無かった割合）・DF3 の寄与を同じ分母で示した値・leave-one-developer-out・CR2 の補助の区間・2×2 表（RQ1）・§7 "Beyond these two datasets"・D1 の 2 つ目の実装による数え直し（`audit/independent-recount/`）・派生表 `results/d1_episodes.csv`。
