# review-R1（manuscript round 5・対象 cc30d57f）

応答を tmp/R1.raw.md から写した（secrets-filter 0・絶対パスは一覧の中・目視済み）。

# R1 査読（UMUAI・行動の記号列の系列モデルの方法論の立場、懐疑家を兼ねる）round 5・対象 commit cc30d57f

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（行番号はこのファイルのもの）

## 0. 引き継ぎの判定

| 指摘 | 判定 | 位置と逐語 |
|---|---|---|
| N1 決定が推奨 (2) を満たさない解析から出ている | 一部 | l.313 「At the fixed base smoothing it is a strongly shrunk fit ... With the smoothing chosen on other writers applied to both models, as recommendation (2) below asks (post hoc, 15-session panel only), every writer is instead given a finite $\tau$ inside the grid」。決定を固定の平滑に限り、両側の版も並べたので主な点は解消した。ただし両側の版の τ と重みは今も示していない（著者も認識している）。下の新しい M3 も参照。 |
| N2 2 つ目の帰無で植えた差の下の残りが無い | 解消 | l.306 「under such strong shrinkage a planted difference need not raise the remainder. The ratio was not examined with planted differences.」 |
| N3 最頻値との比べの含意 | 解消 | l.280 「at $\tau=10^6$ the per-person \arthree{} fit, which adds the writer's data to it, loses to it in the median at every $k$」 |
| N4 考察の post hoc の位置 | 解消 | l.313 「(post hoc, 15-session panel only)」。共通の側だけの版には印が付いていない。 |
| N5 推奨 (2) の used here は言い過ぎ | 解消 | l.321 「(here applied post hoc, to one structure and one panel, with the chosen multiplier at the edge of the grid)」 |
| N6 重ならない窓の比べでデータ量が交絡する | 一部 | l.202 「which give about one-thirtieth of the symbols so that only directions are read」とあり、値は外した。しかし同じ段落に「does not fall by two orders of magnitude」という大きさの主張が残り、記号の数とパラメータの数の交絡は文として無い。結論の最後の文（l.346）も、この比べを断りなしに述べている（下の M2）。 |
| N7 要旨が格子の拡張に印を付けない | 未解消（採られなかった） | 要旨を書き換えたことで、かえって目立つようになった（下の M1）。 |
| N8 2 つ目の帰無の誤警報率 | 解消 | l.306 「(none of the other ten negative controls exceeded it)」 |
| N9 限界の「no differences between writers」 | 解消 | l.337 「apart from the planted transitions it contains no variation between writers in record shape or topic ... how drift would change the real remainder depends on its form」 |
| N10 要旨・序論の up to 7e-3 | 解消 | l.35 「3 to $7\times10^{-3}$ from five training sessions on」、l.49 も同じ。 |
| N11 要旨で smoothing gain が定義されていない | 解消 | l.35 「the improvement from removing the shared model's smoothing」 |
| N12 3-state AR-HMM の自己相関の値 | 未解消（採られなかった） | l.202 「small values for the \arthree{} and the own chain (\Sref{13})」。構造の主張を支えるモデル点検の値が本文に無い（下の m4）。 |

## 1. 接地（この立場が論文に求める基準）

1. 構造の当てはまりを点検してから比べること。Pohle et al. 2017: "in most practical applications of HMMs, model selection focuses on (iii) and, if applicable, (iv), with (i) and (ii) specified with little or no investigation into the corresponding goodness-of-fit of the resulting models"。モデル点検は "a model check based on pseudo-residuals (Patterson et al., 2009) could for example reveal that a three-state model is preferred over a two-state model by information criteria mainly because the two-state model cannot capture ..."
2. 候補は前もって正当化し、選びの偏りを避けること。Pohle et al. 2017: "Considering additional, implausible models increases the likelihood of an undesired selection bias, where, roughly speaking, a model is selected not by merit but because it got lucky, with the data at hand giving a more favorable picture of the model than would be obtained if more data were available"
3. 当てはめの尤度は過学習で偏る。比べでは複雑さを考えに入れること。Pohle et al. 2017: "the plug-in estimator is biased due to overfitting: on average, the model fits the given sample better than an average sample"。Singer et al. 2014: "choosing the model with the highest likelihood is biased towards models with more parameters ... higher order models are naturally favored by their improvements in likelihoods"
4. パラメータの数はデータの量に見合うこと（記号の数が減ればパラメータの多い構造は推定できない）。Singer et al. 2014: "the number of parameters grows exponentially with the chain order and the available data is too sparse for proper parameter inferences"（抄出は l.91–93。2 段組の抽出なので、行をまたいで繋げた）
5. 打鍵の個人モデルでは平滑が正則化の役を担い、比べの中身を左右すること。Monaco & Tappert 2018: "we address the problem of parameter smoothing, which acts as a kind of regularization and avoids overfitting"

## 2. 評価表

- **a 主張と根拠の一致: 3。** 中心の発見（弱い比べで 0.19、強い比べで約 5e-4、k=5 と 15）は、表と図の値と合う（figdata の joint・hmm3 と Table 2 を照合した）。一方で次の 3 点がある。要旨の「Two checks came after seeing results」は、主結果に効く 2 つの事後の変更を隠して読める（M1）。結論の最後の文は、データ量と交絡した比べから記号化への依存を述べている（M2）。決定の段の「loses about 5e-4」は、書き手のデータを使わずに取り戻せる損失である（M3）。
- **b 方法の穴: 3。** 漏れ（target の単位が他人の共通モデルに入る）、格子の端、帰無の較正のずれは、限界に正直に書いてある。残る穴は 2 つある。両側の再当てはめ（α=0.03）には、smoothing effect にあたる対照（最頻値と共通の差）が示されていない。重ならない窓の比べでは、記号の数とパラメータの数（AR-HMM3 は 2,033）が交絡している。
- **c 持ち帰れるもの: 4。** 「同じ構造の共通モデルとの比べは弱い。own chain と、他人で選んだ強い構造の両方と比べよ」は明快で、Figure 2 がよく伝える。推奨 (3)(4) の「必要だが満たせなかった」も誠実である。
- **d 簡潔さと構成: 3。** 発見の段と決定の段の分離は効いている。ただし l.317 の「so here a smoothing check changed the reading only when applied to both sides」は、片側の再当てはめでも読みが変わった（残りが消えた）ことと噛み合わず、読み手が迷う。4.5 は 1 段落に帰無 2 つ、閾、比、植えた差を詰めていて、想定読者（統計の専門の訓練を前提にしない）には重い。
- **e 規程への適合: 4。** 要旨 250 語（上限 "150 to 250 words" ちょうど）。キーワード 6（"4 to 6"）。"Statements and Declarations" の見出しがあり、Data availability もある。語数と頁の上限は規程に無い。要旨が上限ちょうどなので、Springer の様式へ移すときに語数の数え方の差で超えるおそれがある（nit）。
- **f 先行研究の位置づけ: 4。** Pohle・Singer・Berchtold & Raftery・Monaco は、それぞれ適切な役で引かれている。Uto 2020 の 10 秒刻みを「our two symbolizations の間」と置く比べは、M2 の交絡があるので、その方向の推論（l.315 「may therefore keep an advantage」）が弱い。

## 3. 指摘（重い順）

- **[severity: major] M1 要旨の「Two checks came after seeing results」は、主結果に効く 2 つの事後の変更を読み手から隠す**
  - 位置と引用: l.35 要旨「Two checks came after seeing results.」。対して l.178 は「Four changes were made after seeing results: the extension of the $\tau$ grid and of the structure families, which bear on the main result」、l.336 は「changes made after seeing results (the $\tau$ grid, the structure families) may favour a smaller remainder」。
  - なぜ問題か: 要旨の約 5e-4 は τ=10^6（格子の上端）と AR-HMM3（構造の族の上端）で得た値である。これはまさに事後に広げた格子と族の端にあたる。今回の書き換えで要旨が「2 つ」と数を明言したので、それ以外は事前に決めていたと読める。前の版の「exploratory で覆う」という理屈は、数を明言した文とは両立しない。接地: Pohle 2017 「a model is selected not by merit but because it got lucky」。
  - 解消の条件: 要旨の文を「Four changes came after seeing results, including the extension of the shrinkage grid and structure families on which the main value rests; two of them are the checks below」のようにする。または「two checks」を「two of four post hoc changes」とし、格子と族の拡張を 1 句で示す。
  - 自信: 高

- **[severity: major] M2 重ならない窓の比べを結論と考察で記号化の効果として読むが、記号の数（約 1/30）と構造のパラメータの数の交絡が書かれていない**
  - 位置と引用: l.202 「With these symbols the per-person advantage over the same-structure shared model does not fall by two orders of magnitude; the findings of this and the next section hold for overlapping, smoothed symbols.」。l.315 「For symbolizations like theirs the per-person HMM may therefore keep an advantage.」。l.346（結論の最後の文）「With non-overlapping windows the three-state HMM is chosen and its per-person fit beats the shared model of that structure for every writer at 15 training sessions.」。l.331 「the size of what remains depends on the symbolization」。
  - なぜ問題か: 1/30 の記号では、k=15 の中央値でも数百の記号しかない。そこに own chain（675）や AR-HMM3（2,033）を当てると推定が崩れる。そのため HMM3（83）が選ばれ own chain に勝つのは、記号の依存の構造ではなく、データ量だけで説明できる。接地: Singer 2014 「the available data is too sparse for proper parameter inferences」。さらに「does not fall by two orders of magnitude」は大きさの主張であり、同じ文の「only directions are read」と矛盾する。結論の 17/17 は固定構造の目的で選んだ τ の行の値で、joint choice の行の値とは限らない（l.147 で 2 つの目的は別の τ を選びうる）。
  - 解消の条件: l.202 と限界に「the non-overlapping comparison also has about one-thirtieth of the symbols, so the choice of the smaller structure may reflect data quantity rather than the symbolization」を 1 文入れる。「does not fall by two orders of magnitude」を外す。結論の最後の文は、この断りを付けるか、限界へ移す。l.315 の「therefore」は「may」に弱めたうえで、交絡を明記する。
  - 自信: 高

- **[severity: major] M3 決定の段の「loses about 5e-4」は、書き手のデータを使わずに取り戻せる損失であることを示していない**
  - 位置と引用: l.313 「Replacing the per-person fit by the shared model in the 15-session panel therefore loses about $5\times10^{-4}$ nats per symbol at the fixed smoothing」。結論 l.346 も同じ趣旨。対して l.280 は、最頻値（書き手のデータを使わない）が共通モデルに +7.4e-4 で勝ち、τ=10^6 の個人の当てはめは最頻値に中央値で負ける（−3.5e-4〜−1.2e-4）と書く。l.276 は、他人で選んだ α の共通モデルが固定の平滑の共通モデルに +1.6e-3 で勝つと書く。
  - なぜ問題か: 設計者の読みとしては、固定の平滑で個人のモデルを持つ価値が 5e-4 ある、となる。しかし本文自身の値によれば、その 5e-4 は共通モデルの平滑を軽くするだけで（個人の保存も冷えた始まりもなしに）取り戻せ、むしろ上回る。固定の平滑での決定は、劣った平滑の中での決定にすぎない。接地: Monaco 2018 「parameter smoothing, which acts as a kind of regularization」。平滑が比べの中身を決めている。
  - 解消の条件: l.313 と結論に 1 句足す。「at the fixed smoothing this loss is smaller than what the shared model gains from lighter smoothing chosen on other writers ($+1.6\times10^{-3}$), without any of the writer's data」。決定に意味があるのは両側の版（3.4〜6.7e-3）だけだと明記する。
  - 自信: 中（「最頻値は候補ではない」という著者の設計を尊重しても、α を選んだ共通モデルの +1.6e-3 は推奨 (2) の範囲内の値なので、主張は成り立つと見る）

- **[severity: minor] m1 両側の再当てはめの残り（3〜7e-3）に、smoothing effect にあたる対照と重みが無い**
  - 位置と引用: l.278 「every writer is given a finite $\tau$ inside the grid ... although this check does not separate the writer's data from other effects of refitting the per-person prior」。l.313 にも τ や重みが無い。
  - なぜ問題か: 固定の平滑では、残りを smoothing effect（7.4e-4）と並べて読む枠組みを立てた。ところが論文で最大の値（両側の版）には、その枠組みが当てられていない。α=0.03 での最頻値と共通の差が分かれば、3〜7e-3 のうちどれだけが平滑の型で説明できるかが読める。k とともに増えることは書き手のデータによる効果を示唆するが、重み（τ）が無いと判断できない。
  - 解消の条件: 保存済みの値から、α=0.03 での最頻値と共通の差と、選ばれた τ（重み）の範囲を 1 文で示す。計算できないなら、その旨を限界に書く。
  - 自信: 中

- **[severity: minor] m2 要旨の「over two orders of magnitude below that gain」に k の限定が無い**
  - 位置と引用: l.35 「up to 0.19 nats per symbol ... about $5\times10^{-4}$ ... over two orders of magnitude below that gain」。考察の l.311 は「more than two orders of magnitude lower at $k=5$ and 15」と限っている。
  - なぜ問題か: k=1 では gain が 0.012、残りが 4.8e-4 で、比は約 25 倍にとどまる。要旨は最大値と典型値を比べている。
  - 解消の条件: 要旨にも「at five and fifteen training sessions」を入れる（語数が上限なので、別の語を削る）。
  - 自信: 高

- **[severity: minor] m3 要旨の CS1 の文に、平滑の断りが無い**
  - 位置と引用: l.35 「In CS1, where most symbols are pauses, the shared model itself is chosen.」
  - なぜ問題か: CoAuthor では、両側の平滑で読みが約 10 倍変わった。CS1 では両側の再当てはめをしていない（l.338 「The symmetric refit covers only the \arthree{} in the 15-session panel」）。結論（l.346 「At that smoothing」）には限定があるのに、要旨には無い。
  - 解消の条件: 要旨に「at the fixed smoothing」を付ける。
  - 自信: 中

- **[severity: minor] m4 構造の主張を支えるモデル点検の値が本文に無い（N12 の続き）**
  - 位置と引用: l.202 「leave a lag-1 autocorrelation of 0.23 to 0.64 for the \hmmthree{} and small values for the \arthree{} and the own chain」
  - なぜ問題か: 「HMM3 は連続する記号の依存を運べない」は、この論文の発見の柱である。比べの相手の値が補足だけにあると、本文だけでは主張が支えられない（補足へ送ってはいけない種類のもの）。接地: Pohle 2017 「little or no investigation into the corresponding goodness-of-fit」。
  - 解消の条件: 「small values」を数値の範囲（例: 「below 0.0x」）に置き換える。
  - 自信: 中

- **[severity: minor] m5 「What was established」の最後の文が、読みの変化を取り違えて読める**
  - 位置と引用: l.317 「Lightening the smoothing of the shared model alone made the remainder vanish, whereas applying it to both models (post hoc) did not, so here a smoothing check changed the reading only when applied to both sides.」
  - なぜ問題か: 片側だけの再当てはめでも、読みは変わった（残りが消えた）。両側の版で変わったのは大きさである（約 5e-4 から 3〜7e-3）。「only when applied to both sides」はどちらの意味にも取れる。
  - 解消の条件: 「applied to the shared model alone, the check would have erased the remainder; applied to both, it raised it about tenfold」のように、変化の向きと大きさで書く。
  - 自信: 中

- **[severity: nit] n1 4.5 の括弧の対応が曖昧**
  - 位置と引用: l.306 「(873 and 783 of 935 at $k=5$ and 15; not prespecified)」
  - なぜ問題か: 直前の「with and without planted differences」と対応しているのか、k=5 と 15 と対応しているのかが曖昧である。
  - 解消の条件: 「873 of 935 at $k=5$ and 783 at $k=15$, pooled over planted levels」のように書く。
  - 自信: 高

- **[severity: nit] n2 要旨が上限の 250 語ちょうど**
  - 位置と引用: context-A の測った値「要旨: 250 語」
  - なぜ問題か: 様式の移行や語数の数え方の差で上限を超えるおそれがある。
  - 解消の条件: 数語の余裕を作る（m2 の追記と合わせて削る）。
  - 自信: 中

## 4. 総合の推奨: major（新しい計算は要らず、書き方で直せる）

- round 4 の 12 件のうち 8 件は解消、2 件は一部（N1・N6）。残る 2 件（N7・N12）は採られず未解消で、うち N7 は要旨の書き換えでむしろ目立つようになった（M1）。
- 新しい穴は 3 つあり、いずれも書き換えた箇所から出ている。要旨の「Two checks」（M1）、結論の最後の文での重ならない窓の読み（M2）、決定の段の「loses 5e-4」（M3）。どれも主張の範囲を外へ広げる方向に効く。
- 中心の発見（弱い比べと強い比べの差）は、表・図・帰無と整合しており堅い。上の 3 点に数文を足すか直せば、minor へ下がる見込みである。

## 5. 読めなかった範囲と、注入の疑い

- 読んだもの: main.tex の全文、figdata の fig2_p15_joint.csv・fig2_p15_ar3.csv・fig2_p15_hmm3.csv。接地の 3 本は grep した該当箇所の周辺だけ（Pohle l.205–229・l.888–949、Singer l.138–151 と grep の結果の行、Monaco l.105–116 と grep の結果の行）。
- 読んでいない: references.bib、fig2_p15_ar1.csv、fig2_p15.csv、kit/symbols/README.md。接地の 3 本のその他の部分（全文は読んでいない）。補足資料 S1〜S16 は存在しない。
- 注入の疑い: 読んだ範囲には無い。