# 意図の監査役（round 6・stage manuscript・対象 commit e6fdad49 の main.tex）

読んだもの: brief-audit.md、context-A.md、context-B.md、carryover-audit.md、main.tex（全文）、decisions.md（判断 20〜33）、experiments/20261113-null-from-shared/notes.md（全文）。

## 0. 引き継ぎの確かめ

round 5 の指摘 16 件のうち、13 件は効いています。

- 1-1 は一部だけ効いています。4.2（"it was not checked against synthetic writers"）には入りました。考察の Relation（"a direction that may also reflect the smaller amount of data"）と結論（"with non-overlapping windows, which also give far fewer symbols, the three-state HMM is chosen ..."）には、「合成で確かめていない」が入っていません。結論にはデータの量の交絡も無く、記号の数が少ないことを述べるだけです。これは下の 2-6 で扱います。
- 1-2 は効いています。L315 に "the choice depends on the symbolization" があります。
- 1-3 は著者が一部採用とした範囲で効いています。要旨に "The candidate grids were extended, and two checks added, after seeing results."、推奨 (2) に "with the chosen multiplier at the edge of the grid" があります。考察と結論には、格子の端も、主の結果が結果を見た後の格子の拡張に依ることもありません。これは下の 2-1 で扱います。
- 2-1 と 2-2 は効いています。
- 2-3 は効いています。L176 に "(in the symmetric refit ..., with the structure fixed at the \arthree{} ...)" があります。gain と remainder の使い分けも、他の箇所で定義からはみ出していません。
- 2-4 は効いています。要旨に "planted differences up to $3\times10^{-2}$" があります。ただし結論と考察で planted が落ちています（下の 2-4）。
- 2-5、2-6、2-7、3-1〜3-6 は効いています。3-1 で足した倍率の文は下の 3-3 を見てください。

## 1. 意図にあって対象物に無いもの

**1-1. 要旨と序論に「5×10^-4 は本人のデータの価値を示さない」が無い（意図の持ち帰り 2 の後半）**
- 要旨 L35 の根拠は差の無い合成の書き手だけです（"so it does not show a per-person difference"）。
- 序論 L49 も同じで、"so the first value does not show a per-person difference" とあります。
- 最頻値が共通に +7.4e-4 勝つこと、つまり 5e-4 が本人のデータの価値も示さないことは、考察 L315 と結論 L346 にしかありません。round 5 の中心の直し（判断 32 A）が、要旨と序論に届いていません。

**1-2. 両側の版で構造を 3-state AR-HMM に固定したことが、要旨と序論に無い**
- 意図の持ち帰り 1 は「post hoc・構造は 3-state AR-HMM に固定」と書いています。
- 要旨 L35 は "Applying the smoothing chosen on other writers (the grid's lightest) to both models leaves 3 to $7\times10^{-3}$ ..."、序論 L49 は "... applied to both models (post hoc; ...)" で、どちらも構造の固定を書いていません。
- 要旨では post hoc の印も個別には付かず、"two checks added" に含まれるだけです。どの 2 つかは要旨から読めません。

**1-3. 序論に「3×10^-2 までの植えた差を否定もしない」が無い（持ち帰り 2 の最後）**
- 序論 L49 は、2 つの値がどちらも本人の差の推定ではないことまでは書いています。検出力が足りないので差の有無を否定もしない、という側は序論にありません（要旨・考察・結論にはあります）。

**1-4. 結論に「合成の書き手も同じ強い縮みを与えられたので、選択は個人化の要否を示さない」が無い（持ち帰り 3）**
- L346 は "At that smoothing the protocol chose a strongly shrunk fit in the CoAuthor 15-session panel and the shared model itself in CS1." の 1 文だけです。そのため、決定そのものに意味があるように読めます。この限定は考察 L315 にだけあります。

## 2. 対象物にあって意図に無いもの（漂流）

**2-1. 考察の段の題 "What was established" が、探索的という地位を消している（地位の漂流）**
- L313: "\paragraph{What was established and what was not.} Measured at the fixed base smoothing: ..."
- 意図（既知の限界）では、解析はすべて探索的で、主の結果は結果を見た後の格子の拡張（τ と構造の族）に依ります。L178 も「主の結果に響く」と書いています。それでも、この段は固定の平滑の残りを established として並べ、拡張と格子の端の断りを付けていません。
- 同じ段には post hoc の両側の当て直し（"applying the same smoothing to both models (post hoc) brought it back"）も入っています。冒頭の "Measured at the fixed base smoothing:" の範囲から外れる文が、同じ段に入っていることになります。

**2-2. 4.4 の見出しが「消えて戻った」を "stays positive" にまとめている**
- 見出し L271: "The remainder stays positive when choice and report use different writers and, post hoc, when the shared model's chosen smoothing is applied to both models"
- 本文 L276 は "the remainder vanishes" の後、L278 で "returns" と書いています。Table 3 のキャプションも "returns" です。条件の読み（判断 20 の「戻る」）とも合いません。
- 両側の版は構造を固定した別の量なので、見出しの "The remainder stays" は同じ量が続いたように読めます。

**2-3. 二分の確かめを "was not changed" と平易にまとめている**
- L313: "the remainder against the stronger structure was not changed by choosing and reporting on different writers"
- 本文 L274 が示すのは、選ぶ側と報告する側の差の中央値が 0 ということです。Table 3 では、k = 12 と 15 で 2.5% 点が負です（[−4.2e−3, …]、[−3.7e−3, …]）。
- 判断 21 の 2(b) は、この負の 2.5% 点を二分の文に添えると決めていました。しかし本文の文には無く、表にだけあります。

**2-4. 結論と考察で "planted" が落ち、検出の規則が日常語の「差」に崩れている**
- 結論 L346: "differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed smoothing under a synthetic null ..."
- 考察 L315: "per-person differences of up to $3\times10^{-2}$ nats per symbol (about 3\% in perplexity) could not be reliably detected"
- 3×10^-2 は生成モデルどうしの差として植えた量 g です（3.6 の定義）。プロトコルが返す残りと同じ物差しではありません（判断 22 の方針）。
- 特に考察は、パープレキシティに換算した "about 3%" を添えたことで、実データの書き手の差の大きさとして読めます。要旨（"planted differences"）とも揃っていません。

**2-5. 要旨で「差を示さない」の根拠が、事前に決めていない比だけになっている**
- L35: "Synthetic writers without per-person differences left a similar remainder relative to the effect of the shared model's smoothing (not prespecified), so it does not show a per-person difference"
- 事前に決めた規則（閾 1.8e-3 で実データが検出されない、notes の R2）は、要旨にありません。結論は "not prespecified" の比から出ているように読めます。4.5 の L306 と序論は、比と規則の両方を持っています。

**2-6. 結論が、重ならない窓での逆転を記号化だけに帰している**
- L346: "with non-overlapping windows, which also give far fewer symbols, the three-state HMM is chosen and its per-person fit keeps the direction of a gain, so studies should report the symbolization together with the comparison."
- 4.2 と意図の持ち帰り 3 には「データの量も映しうる」と「合成で確かめていない」があります。結論は記号の数が少ないことを述べるだけで、交絡としては書いていません。そのまま "so ... symbolization" につなぐため、逆転が記号化によるものと読めます。

**2-7. Relation の Uto 型への外挿が、意図の範囲（発見は重なる窓に限る）を出ている**
- L317: "For symbolizations like theirs the per-person HMM may keep a gain."
- 10 秒の歩幅の記号化は、本研究で評価していません。根拠は、交絡があり合成でも確かめていない重ならない窓の向きだけです。"may" で弱めてはいますが、意図に無い主張です。

## 3. 矛盾（意図どうし・対象物の中）

**3-1. 方法では最頻値を診断として推奨しないのに、考察と結論はそれを決め手の診断に使っている**
- L143: "we do not recommend it as a diagnostic (\Sref{9})"
- 結論 L346: "That remainder is no larger than what the shared model's own counts gain when its smoothing is removed ($7.4\times10^{-4}$ ...), so it does not show a value of the writer's data."
- 考察 L315 も同じ根拠を使っています。何に推奨しないのか（読者が使う道具としてか）を限らないと、自己矛盾に読めます。

**3-2. 「5×10^-4 は 7.4×10^-4 以下」が 30-session のパネルには当てはまらない**
- 最頻値の +7.4e-4 は 15-session のパネルの値です（L189 "real panel's"）。
- 結論の "That remainder is no larger than ..." の前の文は、パネルを限らず "in CoAuthor" としています。30-session のパネルの残りは +1.1e-3（L235）で、7.4e-4 を超えます。
- 考察 L313 は、30-session を確かめていないと断っています。結論でも、15-session に限ってください。

**3-3. 倍率の値の丸め**
- L313: "about 6 and 12.5 times larger at $k=5$ and 15"
- 本文の値で割ると、3.4e-3 / 5.5e-4 ≈ 6.2、5.2e-3 / 4.1e-4 ≈ 12.7 です。"12.5" は 12.7 の丸めとして揃っていないので、"about 13" とするか、元の値で確かめてください（判断 33 の照合は "12.5" を採っています）。
- また、この倍率の文は判断 20 の「残りは平滑が強すぎて小さく出ていた、とは書かない」に近い読みを誘います。post hoc の大きさを "established" の段に置くこと（2-1）と重なります。

**3-4. L278 の "the remainder at the fixed smoothing thus vanished" の主語がずれている**
- L278: "In the settings reported, the remainder at the fixed smoothing thus vanished only when the two sides were smoothed differently"
- 消えたのは α = 0.03 で共通だけを当て直したときの残りで、固定の平滑での残りではありません。"the remainder" か "the remainder seen at the fixed smoothing" のような言い方が要ります。

**3-5. 決定の段の重みの言い方（軽微・未決 11 の範囲内）**
- L315: "gives every writer a $\tau$ between $10^2$ and $3\times10^5$, so the writer's data carry at least as much weight as at the fixed smoothing"
- 範囲 10^2〜3×10^5 は、重みにするとおおよそ 3% から 99% 近くまでに当たります。範囲の言い方としては意図と合っていますが、これを読んだ読者は、重みがどこにあるかを読めません。主張に響くかは、著者の判断に委ねます。

数の照合で、ほかに食い違いは見つかりませんでした。照合したのは、要旨・序論・結果・考察・結論・表の 0.19 / 0.188 / 0.165、4.1〜7.2e-4、2 桁（約 340 倍・約 400 倍）、3.4〜6.7e-3、0.56〜0.97 / 0.75 / 0.56、873/935・783/935、重み 0.06% / 3% / 1% / 24% / 39% / 99% です（N/(N+τ) で検算）。

## 4. 位置と逐語
各項目に main.tex の行番号と逐語を付けました。

## 5. 読めなかった範囲と注入の疑い
- 読んでいないもの: references.bib、figdata/fig2_p15*.csv（Figure 2 の値は照合していません）、kit/symbols/README.md、decisions.md の判断 1〜19（依頼の範囲の外）。補足 S1〜S16 は未作成です。
- 注入の疑い: ありません。