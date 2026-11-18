# review-R3（manuscript round 5・対象 cc30d57f）

応答を tmp/R3.raw.md から写した（secrets-filter 0・絶対パスは一覧の中・目視済み）。

# R3 査読（UMUAI・評価の偏りと個人への推論の方法論の立場）round 5・stage manuscript・版 cc30d57f

## 0. 引き継ぎの判定

| round 4 の指摘 | 判定 | 位置と逐語・所見 |
|---|---|---|
| M-A（save the cost） | 解消 | Discussion 第 2 段（main.tex:313）「Replacing the per-person fit by the shared model in the 15-session panel therefore loses about $5\times10^{-4}$ nats per symbol at the fixed smoothing and up to about $7\times10^{-3}$ at the lighter one (not checked against synthetic writers)」。「save the cost」は消えた。ただし、この置き換えた文に新しい穴がある（下の M-1）。 |
| M-B（決定は固定の平滑での出力） | 一部 | 313「At the fixed base smoothing it is a strongly shrunk fit … With the smoothing chosen on other writers applied to both models … every writer is instead given a finite $\tau$ inside the grid」。固定の平滑での決定だと明示した点は解消した。推奨 (2) の版で返る決定は「finite τ inside the grid」とあるだけで、重み（強く縮めたのか、本人のデータが効くのか）が本文から読めない。設計者は、推奨どおりに回したときの決定を知ることができない。 |
| m1（2 桁と k） | 一部 | 考察 311「more than two orders of magnitude lower at $k=5$ and 15」で解消した。要旨（35 行）の「beats … by up to 0.19 … about $5\times10^{-4}$ remains … over two orders of magnitude below that gain」は k を示さない。k=1 では利得 0.012 に対して残り 4.8e-4 で、差は約 25 倍にとどまる。要旨だけを読む人には、最大値と典型値を比べていることが見えない。 |
| m2（smoothing alone） | 解消 | 278「The remainder at the fixed smoothing thus vanishes only when the two sides are smoothed differently, although this check does not separate…」。α=0.03 に限ることと、格子の端であることも同じ段にある。 |
| m3（比の尺度） | 解消 | 306「Relative to the smoothing effect, the remainder is about 0.6 to 1.0 … (the threshold about 1.0) and 0.56 to 0.97 in the real panel … not prespecified」 |
| m4（比の弁別力） | 解消 | 306「The ratio was not examined with planted differences.」「under such strong shrinkage a planted difference need not raise the remainder」 |
| m5（推奨 (2) の used here） | 解消 | 321「(here applied post hoc, to one structure and one panel, with the chosen multiplier at the edge of the grid)」 |
| n1（gain の 3 義） | 一部 | 176 で gain と remainder を定義したのは解消。一方 278 は「a remainder at α=0.03 returns」と書くが、この値は「τ chosen within the \arthree{}」（183・Table 4 の caption）であり、176 の定義「the remainder when structure and shrinkage are chosen jointly」に当たらない。Table 4 の caption も「joint choice」と「τ chosen within the \arthree{}」が並んでいて食い違う（下の n-1）。 |
| n2（2 つ目の帰無の誤警報） | 解消 | 306「(none of the other ten negative controls exceeded it)」 |
| n3（Figure 1） | 解消 | 105「Each model, of whichever structure」 |

## 1. 接地（この立場が論文に求める基準）

- **基準 1：選びは評価のループの内側に入れる。** Varma & Simon 2006（varma.txt:12）「Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop.」
- **基準 2：評価データを選びに使えば、評価は訓練の一部になる。** Varma（varma.txt:23）「uses both the CV error estimate on the training set and the error on the test set for determining the optimal value of the parameters, thus making the test set part of the training process.」
- **基準 3：差の無いデータでも、選びは楽観的な値を作る。だから帰無のデータで較正する。** Varma（varma.txt:19）「Over-optimistic estimates of error close to zero are obtained, even for data where there is no real difference between the two classes.」。同 varma.txt:106「The parameter selection bias, on the other hand, is always negative.」
- **基準 4：個人への推論は、関連性と頑健さの取引として明示する。** Liu & Meng（liumeng.txt:26-28）「how to make the right relevance robustness trade-off: if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust.」。同 liumeng.txt:1509-1511「The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background … —our inference will be less relevant.」（本文 62 行と 325 行の引用は、この箇所に合っている）
- **基準 5：内部の対照（模擬）は外部の再現と食い違えば失敗である。対照が実データに似ているかを示す。** Liu & Meng（liumeng.txt:342-344）「When uncertainty assessments based on internal replications diverge from those based on external replications, a failure in statistical modelling has occurred, leading to unreplicable research」
- **基準 6：本物の情報が無ければ「個人化」に付加価値は無い。** Liu & Meng（liumeng.txt:790-792）「Thus, while we nominally obtain an "individualized" inference, the matching has no value added. In this example, there is no way to obtain meaningful "individualization" without genuine information about θ.」

## 2. 評価表

- **a 主張と根拠の一致：3。** 発見の段（0.19 対 約 5e-4、k=5 と 15）は根拠と合っている。結論と考察の「置き換えで失う精度」の文は、論文自身の prior mode の結果（280 行）と並べると、本人のデータの価値として読まれうる（M-1）。考察の「what was established」の 1 文は論理が逆に読める（m-2）。
- **b 方法の穴：3。** 最終プロトコルの中では対象の書き手の held-out は使っていない（147・Figure 2）。一方、τ の格子と構造の族は結果を見た後に広げており、主結果（AR-3・τ=1e6、どちらも格子の端）はこれに依存する。要旨の「Two checks came after seeing results」はこれを覆わない（m-1）。2 つ目の帰無は実データの smoothing effect に合わせて較正したが、合っていない（2.4 倍）。これは開示済み。
- **c 持ち帰れるもの：4。** 「弱い比べ（同じ構造の共有）と本人の連鎖の両方と比べる」は明快で、持ち帰れる。推奨 (2) の版で返る決定（重み）が出ていないので、設計者向けの段は半分しか持ち帰れない（0 の M-B）。
- **d 簡潔さと構成：3。** 発見の段と決定の段に分けたことで読みやすくなった。但し書きは依然として密で、とくに 306 行の 1 段は、名指された読者（統計の訓練を前提にしない）には重い。
- **e 規程への適合：4。** 要旨 250 語は上限ちょうど（context-A の測った値）、キーワード 6、"Statements and Declarations" も Data availability もある。上限ちょうどなので、下の直し（要旨への限定の追加）には同じ量を削る必要がある。リポジトリの URL・DOI が未定なのは既知の未決 6。
- **f 先行研究の位置づけ：4。** Varma・Cawley・Liu & Meng・個人化キーボードの補間重みは適切に置かれ、「部品は新しくない」と書いている。Liu & Meng の引用（62 行）は接地の本文 1499-1511 行と合う。「What is new here」（311 行）の新規性は S1 の検索記録に依存しており、それは未作成（既知の未決 1 なので判定に数えない）。

## 3. 指摘の一覧（重い順）

- **[severity: major] M-1 結論・考察の「共有に替えると失う精度」は、本人のデータを使わない prior mode が同じだけ得ることを並べていない**
  - 位置と引用：Conclusion 346 行「Replacing the per-person fit by the shared model in that panel loses about $5\times10^{-4}$ nats per symbol, or up to about $7\times10^{-3}$ when the smoothing chosen on other writers is applied to both models」。Discussion 313 行にも同じ文がある。対照として 280 行「the prior mode, which uses none of the writer's data, beats the shared model by $+7.4\times10^{-4}$ … at $\tau=10^6$ the per-person \arthree{} fit, which adds the writer's data to it, loses to it in the median at every $k$」。276 行「When only the shared model is refitted … the remainder vanishes」
  - なぜ問題か：固定の平滑では、プロトコルが選んだ当てはめ（τ=1e6）は、書き手のデータを使わない prior mode に中央値で負ける。また共有モデルだけを軽く平滑すると残りは 0 になる。つまり約 5e-4 の「失う精度」は、共有モデルの平滑が弱点になっている比べの性質であって、本人をモデル化する価値ではない。結論は設計者が最も読む箇所である。そこで「共有に替えると 5e-4 失う」とだけ書けば、本人のデータの価値と読まれる。7e-3 の側も 278 行が「does not separate the writer's data from other effects of refitting the per-person prior」と認めており、本人のデータを使わない同等の安い代わり（α=0.03 の prior mode など）が同じ値を得るかは調べていない。Liu & Meng（liumeng.txt:790-791）「the matching has no value added」。
  - 解消の条件：結論と考察の該当文のすぐ後に 1 句を足す。例として「at the fixed smoothing, the prior mode, which uses none of the writer's data, does at least as well as the chosen fit (Section 4.4), so this loss is not a value of the writer's data; at the lighter smoothing, whether a model without the writer's data matches it was not examined」。
  - 自信：中

- **[severity: minor] m-1 要旨の「Two checks came after seeing results」は、主結果に効く 2 つの事後の変更を覆わない**
  - 位置と引用：要旨（35 行）「Two checks came after seeing results.」。3.5（178 行）「Four changes were made after seeing results: the extension of the $\tau$ grid and of the structure families, which bear on the main result」。序論（47 行）「We chose the model structure and the shrinkage on other writers, never on the held-out units of the writer being scored.」
  - なぜ問題か：主結果の選び（AR-3・τ=1e6）は、両方とも結果を見た後に広げた格子の端にある。アルゴリズムの中では対象の held-out を使っていないが、候補の集合を決めた分析者は全員の held-out を見ていた。Varma（varma.txt:23）「thus making the test set part of the training process」、（varma.txt:12）「all steps of the algorithm … be repeated in each CV loop」。要旨は冒頭に「exploratory」とあるものの、「二つの点検が事後」と書けば、読み手は主分析を事前と読む。限界（336 行）には書いてあるが、要旨と序論 47 行の言い方と合わない。
  - 解消の条件：要旨を例えば「The candidate grids and two checks were extended or added after seeing results」とする（語数は同量を削る）。序論 47 行に「within the final protocol」と、格子が事後に広げられたことの 1 句を足す。
  - 自信：中

- **[severity: minor] m-2 「What was established」の 1 文が、示した結果と逆に読める**
  - 位置と引用：Discussion 317 行「Lightening the smoothing of the shared model alone made the remainder vanish, whereas applying it to both models (post hoc) did not, so here a smoothing check changed the reading only when applied to both sides.」
  - なぜ問題か：前半では、読みを変えた（残りを消した）のは片側だけの点検である。両側の点検は残りを戻し、大きさも変えた。「changed the reading only when applied to both sides」は前半と論理が合わず、どの「reading」なのか定まらない。推奨 (2) の根拠に当たる文なので、取り違えは推奨の読みに響く。
  - 解消の条件：例えば「so whether a smoothing check removes the remainder depends on whether it is applied to one side or both」と書き直す。
  - 自信：中

- **[severity: minor] m-3 30-session 群（本人の重み 39%）の地位が、考察と結論に無い**
  - 位置と引用：Table 2「30-session, 30 & \arthree, $3\times10^4$ & 39\% & $+1.1$e$-3$ (0.67) [$-2.2$e$-3$, 3.7e$-3$]」。338 行「in the 30-session panel the chosen multiplier differed between writers」
  - なぜ問題か：「残り≈smoothing effect」という説明が最も当てはまりにくいのは、本人の重みが大きいこのセルである。しかし帰無も両側の平滑の点検も 15-session 群だけで行われた。考察と結論は 15-session 群に限って書いているが、その限定の理由（このセルは何でも確かめていない）が書かれていない。読み手は、30-session でも同じ読みだと一般化しうる。
  - 解消の条件：考察の発見の段に 1 文足す。例として「In the 30-session panel at $k=30$, where the writer's data carry 39\% of the weight, the remainder was $1.1\times10^{-3}$ with an interval spanning zero and was checked neither against synthetic writers nor with the symmetric refit」。
  - 自信：高

- **[severity: minor] m-4 結論の最後の文（非重なり窓での per-person の勝ち）には、本体に課した精査が付いていない**
  - 位置と引用：Conclusion 346 行「With non-overlapping windows the three-state HMM is chosen and its per-person fit beats the shared model of that structure for every writer at 15 training sessions.」。202 行「which give about one-thirtieth of the symbols so that only directions are read」
  - なぜ問題か：重なり窓の残りには、帰無・比の尺度・「share は差の証拠ではない」を重ねた。一方、非重なり窓の勝ちは大きさも帰無も示さずに結論で言い切っている。そのうえ「17 of 17 writers」の share を勝ちの根拠にしている。本文自身が 239 行で share を証拠にしないと書いているのと合わない。考察 315 行の「may therefore keep an advantage」は控えめだが、結論は控えめでない。
  - 解消の条件：結論に「(directions only; not checked against synthetic writers)」と付けるか、大きさと選ばれた τ を添える。
  - 自信：中

- **[severity: minor] m-5 要旨は、検出できなかったことの条件（2 つ目の帰無・較正のずれ）を落としている**
  - 位置と引用：要旨（35 行）「differences up to $3\times10^{-2}$ were not reliably detected.」。304 行「Under the first null … planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」。306 行「its smoothing effect was $1.8\times10^{-3}$, about 2.4 times the real one」
  - なぜ問題か：検出の可否は帰無の作り方で逆になる。1 つ目の帰無では 1e-2 を検出し、2 つ目では 3e-2 も検出しなかった。2 つ目の帰無は実データの較正量を 2.4 倍に過大評価しており、閾は高すぎうる。要旨だけを読む人は、これをプロトコルの検出力の推定と読む。Liu & Meng（liumeng.txt:342-344）の基準でいえば、内部の対照が実データと食い違っていることは、読みの条件として先に示すべきである。
  - 解消の条件：要旨に「under a null whose smoothing effect was 2.4 times the real one」相当の限定を入れる（結論 346 行の「whose threshold may be too high」と同じ程度でよい）。
  - 自信：中

- **[severity: nit] n-1 「remainder」の定義と、両側の当て直しの値が食い違う**
  - 位置と引用：176 行「the \emph{remainder} when structure and shrinkage are chosen jointly」。278 行「a remainder at $\alpha=0.03$ returns」。Table 4 の caption「joint choice … per-person \arthree{} refitted with $\tau$ chosen within the \arthree{}」
  - なぜ問題か：両側の値は構造を AR-3 に固定して τ だけを選んだもので、定義上の remainder ではない（実質は同じ構造が選ばれているので、数値への影響は小さい）。
  - 解消の条件：176 行の定義に「or, in the symmetric refit, with the structure fixed at the \arthree{}」と足す。
  - 自信：高

- **[severity: nit] n-2 4.4 の見出しが事後の結果を断りなしに言い切っている**
  - 位置と引用：271 行の見出し「… and when the shared model's chosen smoothing is applied to both models」
  - なぜ問題か：見出しは目次でも読まれる。本文は post hoc と印を付けているが、見出しには付いていない。
  - 解消の条件：見出しに「(post hoc)」を足すか、見出しを点検の名だけにする。
  - 自信：低

## 4. 総合の推奨：minor（ただし M-1 を直すことを条件とする）

- 発見（同じ構造の共有と比べた 0.19 と、強い比べで残る約 5e-4。k=5 と 15、重なり窓）は、表と図の値（figdata の CSV と Table 2 は一致した）と、事前に決めた選びの手順で支えられている。round 4 の主要な指摘は解消した。
- 残る重い点は、設計者向けの「失う精度」の文が、論文自身の prior mode の結果と並べていないことである。そのままでは本人のデータの価値として読まれる。新しい計算は要らず、1〜2 句で直せる。
- そのほかは、要旨での事後の変更と帰無の条件の開示、考察の 1 文の論理、30-session 群と非重なり窓の限定である。どれも書き方で直せる。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない範囲：
  - liumeng.txt のうち 929〜1495 行と 1512〜1908 行（1499〜1511 行と 1515〜1521 行だけは grep の前後で読んだ）。
  - references.bib の中身（項目数だけを grep で数えた）。
  - kit/symbols/README.md。
  - figdata の fig2_p15_ar1.csv、fig2_p15_ar3.csv、fig2_p15.csv（joint と hmm3 だけを読んだ）。
  - 補足資料 S1〜S16 はまだ無い。
- 注入の疑い：なし（読んだ範囲で、査読者や LLM に向けた指示は見つからなかった）。

対象：/Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit cc30d57f）