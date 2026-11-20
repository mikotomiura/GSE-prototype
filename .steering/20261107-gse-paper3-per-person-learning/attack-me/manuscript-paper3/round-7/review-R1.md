# R1 査読（UMUAI・行動の記号列の系列モデルの方法論の立場、懐疑家の下位人格）round 7・stage manuscript

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit ed297dd4）。行番号はこの版の main.tex のもの。

## 0. 引き継ぎの判定（round 6 → round 7）

| round 6 の指摘 | 判定 | 位置と逐語・理由 |
|---|---|---|
| major: 決定の段が、対照の無い事後の比べを「決定に関わる比べ」に格上げしている | **一部** | 書き手のデータを使わない対照が入った。L282「The prior mode built from the refitted shared model, which uses none of the writer's data, gains only $+2.5\times10^{-5}$ over that model」、L321「above the $2.5\times10^{-5}$ that the prior mode at the same smoothing gains without the writer's data (post hoc)」。ただし、足された対照は平滑を外した最頻値（τ→∞）で、選ばれた当てはめの平滑と τ の比に合っていない。このため、対称版の残りが平滑の重みの違いから出ているという代替説明を消していない（新しい指摘 N1 を参照）。 |
| minor: 4.4 の見出しが k = 12・15 の分布と合わない | **解消** | L275「The median remainder stays positive when choice and report use different writers」。Table 2 の split の中央値は k = 12・15 でも正（+6.8e-4・+7.4e-4）、割合は 0.95・0.75。L278 にも「at $k=12$ and 15, 5\% and 25\% of pairs are not positive」がある。見出しに残った小さな問題は N6。 |
| minor: 要旨の検出の結論が事後の帰無によることを示していない | **一部** | 要旨 L37 の対称版と合成の書き手には「(post hoc)」が付いた。一方、「planted differences up to $3\times10^{-2}$ were not reliably detected」には印が無い。この文が成り立つのは事後の第 2 の帰無だけで、第 1 の帰無では L308「planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」。序論 L51 も同じ（N3）。 |
| minor: 両側の版の τ の幅が広く、重みが読めない | **解消** | L282「$10^4$ for all 17 at $k=5$ and $10^3$ for all 17 at $k=15$, so at the median training length the writer's data carry about 24\% and 91\% of the weight」。Table 1 の訓練の記号の数と突き合わせると 24% と 91%（9,673/10,673）は合う。 |
| minor: remainder は構造しだい（1 次の連鎖の行では大きい） | **解消** | L319「The remainder is a value of the chosen structure: with the structure fixed at a first-order chain, the per-person fit beats the shared chain by $2\times10^{-3}$ at $k=15$, with no null run」。用語の小さなずれは N7。 |
| minor: AR3 の適合の根拠（m4 の継続） | **未解消**（著者は採らなかった。既知の未決 7） | L206「small values for the \arthree{} and the own chain (\Sref{13})」。本文には値が無い。既知の未決なので判定には数えない。ただし N5 で、本文に残すべき最小限の形を述べる。 |
| nit: 3.4 の remainder の定義の括弧 | **解消** | L180「We call per-person minus the same-structure shared model the \emph{gain} when the structure is fixed at the \hmmthree{}, and the \emph{remainder} when structure and shrinkage are chosen jointly. ... the symmetric refit ... keeps that structure and chooses only $\tau$.」 |

## 1. 接地（この立場が論文に求める基準）

- **G1 平滑の効きはデータの量で変わる。同じ「事前の数」でも、少ないデータと多いデータでは重みが違う。** Monaco & Tappert 2018 §3.7「As N increases, event type frequencies increase and the effect of parameter smoothing is diminished, while parameters conditioned on infrequent or missing event types are biased toward the marginal.」「The purpose of parameter smoothing is twofold. First, it acts as a kind of regularization to avoid overfitting, a problem often encountered when there is a large number of parameters and small number of observations.」→ 両側に「同じ平滑」を当てたと言う比べは、平滑の相対の重みまで揃っているかを見なければならない。
- **G2 書き手ごとに適合の検定を行う。** Monaco & Tappert 2018 §5.1「The test is performed for both the HMM and the POHMM for each user ... the HMM is rejected for 45% of users, while the POHMM is rejected for 22% of users.」→ 採った構造が書き手ごとに当てはまるかを、本文で示すことが求められる。
- **G3 依存の仮定とモデルの点検。尤度で選ぶだけでは足りない。** Pohle et al. 2017 §2.3「with (i) and (ii) specified with little or no investigation into the corresponding goodness-of-fit of the resulting models」。§4.3「the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions」。§1「stresses the importance of the study aim, expert knowledge and model checking procedures.」
- **G4 状態の数は格子の端に寄りやすい。それは無視した構造（個人差を含む）を吸収した結果でありうる。** Pohle et al. 2017 §1「real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure」。
- **G5 尤度は複雑さとともに必ず上がる。比べは複雑さと、最も単純な基準（0 次・1 次）に対して行う。** Singer et al. 2014「the likelihood grows per definition with increasing order and number of model parameters and therefore, the likelihood based methods for model selection fail to penalize the increasing model complexity」。「there might be no improvement over the most basic zero order Markov chain model」。
- **G6 事前の数（偽の数）が無ければ見ていない遷移は予測できない。評価は平滑の扱いに依存する。** Singer et al. 2014「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible.」

## 2. 評価表

- **a 主張と根拠の一致: 3/5。** 固定の平滑での残り（約 5e-4）が最頻値の平滑の効き（7.4e-4）以下で、書き手のデータの価値を示さないという読みは、根拠と合っている。一方、両側の版は「the comparison that bears on a designer's decision」（L51）、「The comparison that bears on the decision」（L321）と格付けされている。その根拠は「above the 2.5e-5 that the prior mode ... gains」だが、この対照は平滑の重みが揃っていない（N1）。さらに設計者への結論（「does not show here that a per-person model is worth its cost」）と、決定に関わるとした比べの値（15 人中 15 人前後が正で 3.4〜5.2e-3）の関係が書かれていない（N2）。要旨と序論の「planted differences up to 3e-2 were not reliably detected」には、事後の帰無に限るという印が無い（N3）。
- **b 方法の穴: 3/5。** 主な脅威は 2 つある。(i) 対称版の残りが、書き手のデータではなく、同じ α が少ない記号の側でより重く効くことから出ている可能性（著者自身も L187 で「the same prior counts weigh differently」と書いているのに、対照がそれを切り分けていない）。(ii) 系列の境界の採点（初期分布と先頭の記号）が、残りと同じ桁の差を生みうること（N4）。
- **c 持ち帰れるもの: 4/5。** 同じ構造の共有モデルという弱い比べと、自分の連鎖という基準を並べよという勧めは明快で、他の領域へも移せる。両側の版の勧め (2) は事後で、1 構造・1 パネルであることが明記されている。
- **d 簡潔さと構成: 3/5。** 要旨は 247 語。固定の平滑の値と両側の版の値を 1 組で出したため、要旨（L37）は数の並びが密になった。「3.4 and $5.2\times10^{-3}$」（3.4 に桁が付いていない、N8）のように読み違えやすい。4.4 の見出しは 3 節をつないだ一文で長い。
- **e 規程への適合: 4/5。** 要旨 247 語（150〜250）、キーワード 6 個（4〜6）、"Statements and Declarations" あり、Data availability あり。本文 7,502 語に上限の規定は無い。L20–21 に使っていない `\PENDING` のマクロとコメント（「remove before submission」）が残る（N9）。
- **f 先行研究の位置づけ: 4/5。** Pohle・Singer・Monaco・Berchtold & Raftery への言及は、どれも原文と食い違わない（Singer の「page level / topical level」は抄録の「the memoryless model represents a quite practical model ... on a page level. However ... on a topical level ... the memoryless assumption is violated」と合う）。Pohle がモデルの点検（残差）を選択の中心に置いている点（G3）は、本文が補足へ送っている部分と対照的に見える（N5）。

## 3. 指摘の一覧（重い順）

- [severity: major] N1 両側の版の「書き手のデータを使わない対照」が平滑の重みを揃えておらず、平滑の重みの違いという代替説明を消していない
  - 位置と引用: main.tex L282「The prior mode built from the refitted shared model, which uses none of the writer's data, gains only $+2.5\times10^{-5}$ over that model ... and the chosen fit beats it by $+3.3\times10^{-3}$ at $k=5$ and $+7.9\times10^{-3}$ at $k=15$」。L187「the same prior counts weigh differently against a writer's few symbols and the other writers' many.」L321「above the $2.5\times10^{-5}$ that the prior mode at the same smoothing gains without the writer's data (post hoc)」。要旨 L37「The second exceeds that gain at the lighter smoothing ($2.5\times10^{-5}$)」
  - なぜ問題か: 最頻値は τ→∞ で基の平滑を外した数であり、選ばれた当てはめ（事前 = α·基 + τ̂·S̄、τ̂ = 10^3〜10^4）とは平滑の相対の重みがまったく違う。共有モデルは他の書き手の多くの記号に対して α を当て、個人の当てはめは τ̂ 個分の擬似の数と書き手の数千の記号に対して同じ α を当てる。だから稀な行では個人の側の平滑が相対的に重い。round 6 までに本文自身が「固定の平滑では、平滑の当て方の違いが残りを作る」と読んだのと同じ機構が、向きを変えて働いている可能性がある（G1: Monaco「the effect of parameter smoothing is diminished」as N increases）。書き手のデータを使わず、事前の構成だけを同じにした対照、すなわち書き手の記号を 0 にした事後（正規化した α·基 + τ̂·S̄）と共有モデルの差が無いため、「書き手のデータの寄与」と「事前を作り直したことの寄与」は分かれない。L282 自身も「this check does not separate the writer's data from other effects of refitting the per-person prior」と書いているが、要旨・序論・決定の段・結論は 2.5e-5 を超えたことを、書き手のデータを使わない対照に勝ったと読ませる書き方になっている。加えて、この最頻値は 2 人で −∞ になる（L282）。見ていない遷移を予測できない対照（G6）は比べの相手として退化している。
  - 解消の条件: (a) 選ばれた τ̂ と α で、書き手の記号を入れない事後（α·基 + τ̂·S̄ の正規化）を対照に置き、その対照と共有モデルの差、選ばれた当てはめとの差を中央値で出す。または (b) この計算をしないなら、要旨・序論・決定の段（L321）・結論（L350）の「exceeds that gain」「above ... without the writer's data」を外す。そのうえで、2.5e-5 の対照は平滑を外した最頻値で、選ばれた当てはめの事前とは平滑の重みが違うので、書き手のデータの寄与を示す対照ではない、と同じ所に書く。
  - 自信: 中（機構は本文の L187 の自認から導ける。大きさは計算しないと分からない）

- [severity: major] N2 「決定に関わる比べ」とした値から、設計者は何を結論するのかが書かれていない
  - 位置と引用: L51「the second is the comparison that bears on a designer's decision. Neither value shows how much writers differ.」L321「For a designer, the protocol does not show here that a per-person model is worth its cost. ... The comparison that bears on the decision applies the same smoothing to both models. ... leaves $3.4\times10^{-3}$ at $k=5$ and $5.2\times10^{-3}$ at $k=15$」。L182「we use ... no meaningful-difference threshold」
  - なぜ問題か: 設計者の決定に要るのは、書き手のデータを使ったときの予測の得である。その得が書き手の差から来るか（機構）は二次の問題になる。本文は「決定に関わるのはこちら」と言う一方で、結論は機構の否定（「does not by themselves show per-person differences」）だけを述べる。その比べの値（約 0.3〜0.5% の perplexity の低下、k = 15 で 17 人中 15 人前後が正）が設計者にとって「得がある」なのか、「小さい」なのか、「判定できない」なのかを言わない。読者には、決定に関わる比べが正の値を返したのに、なぜ「worth its cost を示さない」のかが分からない。G5（Singer）の流儀でいえば、比べの基準を置いたら、その基準に対して何を採るかを言う必要がある。
  - 解消の条件: 決定の段に 1 文を足す。例: 「この比べが正しい場合でも、書き手のデータが 1 記号あたりに足す予測は約 0.3〜0.5% で、本研究はその大きさが保存と収集の費用に見合うかの閾を置かないので、決定は読者の費用に委ねる」。または、この比べを「決定に関わる」と呼ぶのをやめ、「書き手のデータを使う版を両側の平滑を揃えて読む比べ」と呼び直す。N1 の対照が無い間は、後者が安全。
  - 自信: 中

- [severity: major] N4 系列の境界での採点（初期分布と先頭の記号）が、残りと同じ桁の差を生みうるのに、本文で切り分けられていない
  - 位置と引用: L180「Each held-out session, and in CS1 each work block, is scored as its own sequence, one step ahead from the model's initial distribution; first symbols are scored and counted (\Sref{3}).」Table 1 L128「Held-out symbols 3,296」（5 セッションなので 1 セッションあたり約 660 記号）
  - なぜ問題か: 1 セッション約 660 記号なので、先頭の 1 記号の対数確率が約 0.33 nats 違えば、1 記号あたりで約 5e-4 になる。固定の平滑での残り（4.1〜7.2e-4）と同じ桁である。AR-HMM の先頭の記号は直前の記号を持たないので、その確率は初期分布と別の放出の扱いに依存する。その扱いは本文に無い（S3 へ送られている）。個人の当てはめ（τ で縮めた初期分布）と共有モデルの初期分布の違いは、書き手の記号の遷移とは別の経路で残りを動かす。自分の連鎖の先頭の記号の扱いも本文で定義されていない（L149 は遷移の数だけ）。CS1 は作業の区切りごとに系列を切るので、先頭の記号はさらに多い。これは補足に送ってよい細部ではなく、主要な量の代替説明である（G3: 依存の仮定の点検）。
  - 解消の条件: 先頭の記号を除いた（またはすべてのモデルで先頭を同じ分布で採点した）残りを、固定の平滑と両側の版の k = 5・15 について 1 文で本文に出す。少なくとも、自分の連鎖と AR-HMM が先頭の記号に何の分布を使うかを本文で 1 句定義する。
  - 自信: 中（桁の見積もりは本文の数から。実際の差の大きさは分からない）

- [severity: minor] N3 要旨と序論の「planted differences up to 3e-2 were not reliably detected」に、事後の第 2 の帰無に限るという印が無い
  - 位置と引用: 要旨 L37「Neither shows a per-person difference, and planted differences up to $3\times10^{-2}$ were not reliably detected.」序論 L51「Nor do the results rule differences out: planted differences up to $3\times10^{-2}$ were not reliably detected.」。対して L308「planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」（第 1 の帰無）、結論 L350「under a synthetic null added after seeing results」
  - なぜ問題か: 結論は印を付けたが、要旨と序論は付けていない。第 1 の帰無（事前に決めた方）では 1e-2 が検出されているので、印の無い文は事前に決めた解析と食い違って読める。また「Neither shows」の「Neither」は両側の版も含むが、両側の版は合成の書き手で確かめておらず、検出の確かめは固定の平滑だけである。
  - 解消の条件: 要旨と序論の該当文に「(post hoc null, at the fixed base smoothing)」相当の句を付ける。
  - 自信: 高

- [severity: minor] N5 構造の選択の根拠（AR3 の当てはまり）が本文に数として無い
  - 位置と引用: L206「leave a correlation between consecutive residuals (lag-1 autocorrelation) of 0.23 to 0.64 for the \hmmthree{} and small values for the \arthree{} and the own chain (\Sref{13})」。L340「the \arthree, its largest structure, was chosen in every cell」
  - なぜ問題か: 既知の未決 7 なので判定には数えない。ただし主張に響く。AR3 は格子の端で毎回選ばれ、Pohle（G4）は端の状態の数が「heterogeneity between individuals」を吸い込みうると言う。残りの大きさの解釈（個人差が共有モデルの構造に吸われたか）は、AR3 が書き手ごとに当てはまるかに依存する（G2: Monaco は書き手ごとの棄却率を本文に出している）。「small values」は数になっていない。
  - 解消の条件: AR3 と自分の連鎖の lag-1 自己相関の範囲（数 2 つ）を本文の L206 に出す。図は補足でよい。
  - 自信: 中

- [severity: minor] N6 4.4 の見出しの「post hoc」が、事前に決めた共有の側だけの当て直しにも掛かって読める。また k = 12 の負の値を「vanishes」で括っている
  - 位置と引用: L275「post hoc, it vanishes when only the shared model's smoothing is lightened and returns when the same smoothing is applied to both」。L182「the symmetric refit of Section~\ref{sec:checks-method}, added after seeing the result of the asymmetric one」。Table 2 L301「$-1.05$e$-3$ (0.29)」
  - なぜ問題か: 事後なのは両側の版だけである（L182）。見出しは両方の節を「post hoc」で括っている。k = 12 では消えるのではなく負になる。
  - 解消の条件: 「it vanishes (except at $k=12$) when only the shared model's smoothing is lightened, and, post hoc, returns when ...」の語順にする。
  - 自信: 高

- [severity: minor] N7 「remainder」の定義が、使っている場面と一致しない
  - 位置と引用: L180「the \emph{remainder} when structure and shrinkage are chosen jointly」。L319「The remainder is a value of the chosen structure: with the structure fixed at a first-order chain, the per-person fit beats the shared chain by $2\times10^{-3}$」。L282 の両側の版も構造を固定している
  - なぜ問題か: 1 次の連鎖を固定した行は定義上「remainder」ではない。両側の版は L180 の 2 文目で手当てされているが、1 次の連鎖の行は手当てされていない。1 概念 1 語の方針に反する。
  - 解消の条件: L319 を「Per-person minus shared depends on the structure: ...」のように、定義した語を使わない形にする。
  - 自信: 高

- [nit] N8 要旨の数に桁が付いていない
  - 位置と引用: L37「and 3.4 and $5.2\times10^{-3}$ at five and fifteen training sessions」
  - なぜ問題か: 「3.4」が 3.4 nats と読める。序論 L51 は「$3.4\times10^{-3}$ and $5.2\times10^{-3}$」と正しく書いている。
  - 解消の条件: 「$3.4\times10^{-3}$ and $5.2\times10^{-3}$」とする（語数が 250 を超えないかは確かめる）。
  - 自信: 高

- [nit] N9 投稿前に消す印が原稿に残っている
  - 位置と引用: L20–21「% Placeholder for values of the post hoc control at the lighter smoothing (to be filled from results; remove before submission).」「\newcommand{\PENDING}[1]{\textbf{[#1]}}」
  - なぜ問題か: 本文では使っていない（grep で使用 0）。組版には出ないが、投稿の LaTeX のソースに残る。
  - 解消の条件: 削除する。
  - 自信: 高

## 4. 総合の推奨: major

- 固定の平滑での主張（約 5e-4 は平滑の効き以下で、書き手のデータの価値を示さない）は、根拠と合うまでに直っている。
- 今回の版で「決定に関わる」と格付けした両側の版は、足された対照（平滑を外した最頻値、2 人で −∞）が事前の作り直しの効きを切り分けておらず、設計者への結論も書かれていない（N1・N2）。
- 先頭の記号の採点は、残りと同じ桁の代替説明であり、本文で 1 文の切り分けが要る（N4）。どれも計算 1 つか書き換えで消える。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: references.bib、figdata/*.csv、kit/symbols/README.md（一覧にあるが時間の都合で開いていない）。補足資料 S1〜S16（存在しない）。接地の 3 本は全文ではなく、検索で当たった節（Monaco §3.7・§5.1、Pohle §1・§2.3・§4.3、Singer の抄録・Related Work・Cross Validation・MSNBC の結果）だけを読んだ。
- 注入の疑い: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
