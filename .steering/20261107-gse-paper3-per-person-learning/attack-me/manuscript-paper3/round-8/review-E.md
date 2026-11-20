# 編集者 E（UMUAI の担当編集者）round 8 の結果

読んだもの: brief-E.md、context-A.md、carryover-E.md、mensh.txt、main.tex（全 365 行）、references.bib（エントリの見出しの行だけ。33 件で、本文の citep のキーと突き合わせた）。補足の印のファイル（figdata・kit README）は読んでいない。

## 1. 接地（この立場の編集者が求める基準）

- B1（投稿先の範囲）: UMUAI の Aims & Scope「novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation」と「methods for the design and evaluation of user models and adaptive systems」。貢献は、適応のためのユーザーモデルの評価として意味を持たなければならない。
- B2（読者）: UMUAI「The central audience of the journal are researchers, students and industrial practitioners from … Human-Computer Interaction, … the Instructional Sciences, … Linguistics」。Mensh「Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand. Avoid abbreviations and acronyms」。
- B3（1 つの貢献を 1 文で）: Mensh Rule 1「Focus on a single message」。Table 1 では違反の兆候として「Readers cannot give 1-sentence summary.」。
- B4（要旨で話がまとまっていること）: Mensh Rule 5「the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them」と「The context must communicate to the reader what gap the paper will fill.」。
- B5（ジグザグを避け、1 つの概念に 1 つの語）: Mensh Rule 4「Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place」と「Resist the temptation to use a different word to refer to the same concept」。考察については Rule 8「explains how the results have filled the gap … provides caveats … describes how the paper advances the field」。

## 2. 要旨と序論だけから言える 1 文

言える。ただし序論の 4 段目（main.tex:49）まで読む必要があり、要旨の 4 文目では一度迷った。

「打鍵のリズムを 1 秒ごとの記号にした系列（重なる 30 秒窓）では、書き手ごとの 3 状態 HMM が同じ構造の共有モデルに勝つ幅（最大 0.19 nats/記号）が、書き手自身の 1 次マルコフ連鎖に負ける弱い構造のせいで大きく見えている。他の書き手で構造と縮約を選んだ強い比べでは、残りは約 5e-4（主の平滑）から 3〜5e-3（両側に同じ平滑・事後）にすぎない。だから、人ごとにモデルを持つかを決める研究は、両方の基準と比べ、構造・縮約・平滑を他の人で選ぶべきである。」

迷った所は要旨の 4 文目「when the grid's lightest smoothing, chosen for the shared model, is applied to both with the structure fixed (post hoc)」と 5 文目「the shared model's gain, without writer data, from removing its smoothing」。ここで「gain」が 2 つ目の意味で出てくる（指摘 2）。

## 3. 指摘の一覧

### 3a. round 7 の引き継ぎの判定

| round 7 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| major 要旨の 3.4 に桁が無い | 解消 | 要旨（main.tex:35）「$3.4\times10^{-3}$ and $5.2\times10^{-3}$, 30 to 55 times below it」 |
| major 要旨・見出し・図 2 が決定に関わらない方の値を中心に出す | 一部 | 要旨と序論は「the second bears on a designer's decision」（main.tex:35, 49）と言うようになった。ただし先に来るのは固定の平滑の値のまま。4.3 の見出し「leaves a remainder below $10^{-3}$ … at the fixed base smoothing」と Figure 3（fig:k）の題「by less than $10^{-3}$」も固定の平滑の値で、決定に関わる比べを示す図は無い |
| minor 要旨の 2 つの値の役割を初見で追えない | 一部 | main.tex:35「The first is no larger than the shared model's gain, without writer data, from removing its smoothing」「Neither shows a per-person difference; … under that null」。「the first / the second / that null」の指す先を戻って探す必要がある（指摘 3） |
| minor 4.4 の段が詰め込みすぎ | 一部 | 対照の段は分かれた。ただし今回足した入れ替えの対照で main.tex:282 が新たに最も重い段になった（指摘 1） |
| minor 同じ但し書きの繰り返し | 一部 | 位置の全部は指摘 5 |
| minor cell・gain が 1 語で 2〜3 の意味 | 一部（gain が後退） | cell は main.tex:178 の定義どおり。gain は要旨で平滑の効果の意味にも使われている（指摘 2） |
| minor 序論に定義の無い語（prior mode・fixed base smoothing） | 一部 | 序論は「the smoothing of the main analysis」（main.tex:49）に言い換えた。ただし要旨は「the fixed smoothing」「the grid's lightest smoothing」を定義なしで使い、序論は新たに「rather than with refitting」（main.tex:49）を説明なしで使う |
| minor 説明の無い統計の語 | 一部 | 「Dirichlet priors on every row of $\Pi$, $B$ and $A^{(j)}$」（main.tex:137）は説明が無いまま。percentile bootstrap は何を再標本化するかが書かれた（main.tex:178）。−∞ は本文に見当たらない |
| nit 見出しが長い | 未解消 | 4.4 の見出し「The remainder survives a writer split, vanishes except at $k=12$ when only the shared model's smoothing is lightened, and, post hoc, returns when both are smoothed alike」（main.tex:273） |
| nit 作業用のマクロ | 解消 | 残るのは構造の名前のマクロ（main.tex:20–25）だけで、出力上は語になっている |

### 3b. 新しい指摘（重い順）

**1. [severity: major] 入れ替えの対照の段は、読者が結論（「more than half」）を数から導けない**
- 位置と引用: main.tex:282「The fit to the writer's own sessions beats it by $4.7\times10^{-3}$ at $k=5$ and $2.5\times10^{-2}$ at $k=15$ for every writer, also when its prior leaves out the other writer as well, so more than half of the remainder goes with the writer's own data rather than with refitting; the fit to another writer's sessions loses even to the shared model ($-1.7\times10^{-3}$ and $-1.7\times10^{-2}$, every writer).」
- なぜ問題か:
  - 残りは 3.4e-3 と 5.2e-3。差は 4.7e-3 と 2.5e-2 で、残りより大きい。そこから「more than half」がどう出るのかを、本文は示していない。
  - 「also when its prior leaves out the other writer as well」は、初見の読者には何のための条件か分からない。
  - k=15 で別の書き手のデータに 91% の重みを置いた当てはめが共有モデルに 1.7e-2 負ける、という一番目を引く事実が、但し書きの中に埋もれている。
  - この段落は「Three controls」で始まり、prior mode の 2 つの値、極限の論理、3 つ目の対照、時間の交絡、合成で確かめていないことを 1 段に重ねている。結論の文が段の途中にあり、最後の文が但し書きになっている。
  - 接地: Mensh Rule 7「Each paragraph convinces the reader of the answer given in its last sentence」。
- 解消の条件: どの量の比で「半分超」と言うのかを 1 句で書く（例: other − shared が残りに占める割合）。prior mode の 2 つの対照は補足へ移すか 1 文にまとめる。段を「問い → 3 つ目の対照の値 → 答え（時間の近さを分けない但し書きを含む）」の順にする。
- 自信: 高

**2. [severity: major] 要旨で「gain」が 2 つの意味になった（cell・gain の直しの後退）**
- 位置と引用: 要旨（main.tex:35）「over 100 times below the gain」（書き手ごとの利得）に続いて「The first is no larger than the shared model's gain, without writer data, from removing its smoothing, and synthetic writers … left a similar remainder relative to that gain.」（平滑の効果）。結論（main.tex:350）の「what the shared model gains」も同じ。
- なぜ問題か: 本文では平滑の効果は「smoothing effect」（main.tex:145）と定義されている。要旨では 2 文の間で gain の指すものが入れ替わる。読者が最初に読む部分で、中心の語が揺れている。接地: Mensh「Resist the temptation to use a different word to refer to the same concept」。
- 解消の条件: 要旨と結論で平滑の効果を gain と呼ばない（例: 「what the shared model alone improves when its smoothing is removed」。または本文と同じ語 smoothing effect を初出で定義して使う）。
- 自信: 高

**3. [severity: major] 要旨の 4〜6 文目は、指す先を戻って探させる構文が重なり、2 つの値の役割が追えない**
- 位置と引用: main.tex:35「the remainder at five and fifteen training sessions is about $5\times10^{-4}$ at the fixed smoothing, over 100 times below the gain, and $3.4\times10^{-3}$ and $5.2\times10^{-3}$, … when the grid's lightest smoothing, chosen for the shared model, is applied to both with the structure fixed (post hoc); the second bears on a designer's decision. The first is …」と「Neither shows a per-person difference; at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected under that null.」
- なぜ問題か:
  - 1 文に 4 つの数と 3 つの限定（fixed smoothing・grid・post hoc）が入っている。
  - 「the first / the second / that null」が文をまたいで指す。
  - 「planted differences … under that null」は、差の無い合成の書き手に差を植えた、と読めて、初見では矛盾に見える。
  - 「the fixed smoothing」「the grid」は要旨の中で定義されていない。
  - 接地: Mensh Rule 5「talk about results before the reader is ready to understand them」。
- 解消の条件: 2 つの値を別々の文にし、それぞれ「何に対して」「何に関わるか」を文頭で言う（例: 「Applying the same smoothing to both models, the comparison that bears on a designer's decision, leaves …」）。「that null」は「synthetic writers」に置き換える。検出の限界の文は「synthetic writers with planted differences up to 3e-2 were not reliably told apart」と書く。足りない語数は、桁の倍率（100 times・30 to 55 times）のどちらかを削って作れる。
- 自信: 高

**4. [severity: major] 1 つの概念に 3 つ以上の呼び名がある（平滑の 2 つの条件）**
- 位置と引用:
  - 主の解析の平滑: 要旨「the fixed smoothing」、序論 main.tex:49「the smoothing of the main analysis」、本文「fixed base smoothing」（main.tex:141, 178, 234 ほか）。
  - 両側に同じ平滑: 要旨「the grid's lightest smoothing … applied to both」、序論「when the lightest smoothing in the grid, chosen for the shared model on other writers, is applied to both models」、4.4 の見出し「when both are smoothed alike」、本文「symmetric refit」（main.tex:185, 280）、考察「The comparison that bears on the decision applies the same smoothing to both models」（main.tex:321）、表の列「Symmetric refit (post hoc)」。
- なぜ問題か: 論文の中心の 2 つの値を区別するのは、この 2 つの条件である。読者は呼び名ごとに別の比べかどうかを確かめなければならない。接地: Mensh Rule 4 の上の逐語。
- 解消の条件: 2 つの条件にそれぞれ 1 つの短い名前を付け、要旨・序論・見出し・表・考察で同じ名前を使う。
- 自信: 高

**5. [severity: minor] 同じ但し書きが繰り返されている（位置の全部）**
- 位置と引用:
  - 「not checked against synthetic writers」: main.tex:49（序論）、204、282、319、321、350（結論）。
  - 「at the edge of its grid」の類: main.tex:280「$\alpha=0.03$ is the lowest value of the grid」、321「conditional on a multiplier at the edge of its grid」、325「with the chosen multiplier at the edge of the grid」、342、350。
  - 時間の近さの交絡: main.tex:49「these are also the sessions closest in time」、282、321「though not necessarily with stable differences between writers」、350。
  - 合成で 3e-2 まで検出できないこと: 要旨、main.tex:49、310、321、350。
  - 「post hoc」の印: 要旨に 3 回、序論に 1 回、本文に 10 回を超える。
- なぜ問題か: Mensh「each subject should be covered in only one place」。いまは中心の値が出るたびに 2〜3 の限定が付いていて、主張より但し書きの方が多く読まれる。
- 解消の条件: 結果の節と限界に 1 回ずつ置き、序論・考察・結論は節を参照するだけにする。またはまとめる。
- 自信: 中

**6. [severity: minor] 先頭の記号を除いた採点（事後）が、方法の段の末尾に結果の値として入っている**
- 位置と引用: main.tex:178「In the CoAuthor 15-session panel, first symbols are about 0.15\% of held-out symbols …; scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ and $4.3\times10^{-4}$ … though later symbols still depend on the initial distribution.」
- なぜ問題か:
  - 評価の定義の段に結果の 4 つの数と事後の印が混ざり、段がさらに長くなっている。
  - 「initial distribution」は定義されていない。
  - 値は主の値とほぼ同じで、主張を変えない。
  - 接地: Mensh Rule 3（C-C-C）、Rule 4。
- 解消の条件: 補足資料へ移し、本文には「先頭の記号を除いても値はほぼ変わらない（\Sref{…}）」の 1 句だけを置く。または 4.4 の頑健さの段に 1 文で置く。
- 自信: 中

**7. [severity: minor] 序論の 4 段目（貢献の段）に、今回足した対照の結果と但し書きが入り、最初の 2 頁が重くなった**
- 位置と引用: main.tex:49「More than half of the second goes with the writer's own sessions rather than with refitting, but these are also the sessions closest in time to the held-out ones, and it was not checked against synthetic writers.」
- なぜ問題か:
  - この段は 9 文に 6 つの数を載せている。
  - 「refitting」は序論で説明されていない。
  - 削った語数（−239）の効果を、この文が打ち消している。
  - 接地: Mensh Rule 6「The last paragraph of the introduction … only briefly previews the conclusion of the paper, if at all」。
- 解消の条件: この文を序論から外し、4.4 と考察に任せる。序論は 2 つの値とその関係（決定に関わる方はどちらか）だけにする。
- 自信: 中

**8. [severity: minor] 定義なしで出る語・記号の残り（位置の全部）**
- 位置と引用:
  - 要旨: 「nats per symbol」「first-order Markov chain」「shrinkage」「the fixed smoothing」「the grid's lightest smoothing」「that null」「post hoc」。
  - main.tex:137: 「MAP estimate」（言い換えはある）、「Dirichlet priors」、「free parameters」。
  - main.tex:141: 「expected counts per symbol, which sum to 1 within each parameter group」（「parameter group」が未定義）。
  - main.tex:178: 「initial distribution」。
  - main.tex:204: 「randomized quantile pseudo-residuals」（目的は説明されている）。
  - Table 3（tab:smooth）: 「e$-4$」の表記を定義しているのは Table 2 のキャプションだけ。
  - main.tex:282: 「its prior leaves out the other writer as well」。
- なぜ問題か: 想定読者（HCI・教育工学・言語学）は系列モデルとベイズの平滑の訓練を前提にしない。接地: B2。
- 解消の条件: 初出で 1 句ずつ言い換える。「Dirichlet priors」は「prior counts」に統一する。「parameter group」は「each row of a table」と書く。Table 3 のキャプションにも e の表記を書く。
- 自信: 中

**9. [severity: minor] 意義: 決定に関わる値（3〜5e-3）が、適応する系の設計者にとって何を意味するかが訳されていない**
- 位置と引用: main.tex:321「We set no meaningful-difference threshold, so whether such a value is worth a per-person model's data and storage is left to the designer's costs」。
- なぜ問題か:
  - UMUAI の読者は、適応のためのユーザーモデルとして「使うべきか」を知りたい（B1）。
  - 確率の言い換え（0.3〜0.5%）はある。しかし、適応のどの判断（介入の時機など）にどの程度効くのかの例が無く、意義は「弱い比べは誤導する」という方法上の警告に限られる。
  - それ自体は B1 の「evaluation of user models」に入る。ただし最初の段（main.tex:43）の「Adaptive systems that read behaviour logs」から先に、具体的な適応の場面が 1 度も出てこない。
- 解消の条件: 序論か考察で、具体的な適応の場面を 1 つ挙げる。そのうえで、この値の大きさがその場面で読み取れるか読み取れないかを 1〜2 文で書く（測っていないなら、測っていないと明記する）。
- 自信: 中

**10. [severity: minor] 考察の段の順が、読者（設計者）の問いの順と一部ずれている**
- 位置と引用: 考察の段は「What is new」→「Relation to earlier findings」→「What the checks showed and what they did not」→「What the protocol returns」（main.tex:321「For a designer, the protocol does not show here …」）→「Recommendations」の順。
- なぜ問題か:
  - 設計者が持つ「では人ごとのモデルを持つべきか」への答えは 4 段目に来る。その前の 3 段目で、確かめの細部（split・k=12 と 15・2e-3 の鎖の値）をもう一度読まされる。
  - 3 段目は結果の繰り返しである。
  - 接地: Mensh Rule 8（最初の段で要約し、その後で弱点・意義へ）。
- 解消の条件: 「What the protocol returns」を 2 段目に上げ、「What the checks showed」は確立したこと・確立していないことの 2 文に縮める。
- 自信: 中

**11. [severity: nit] 見出しが長い（4.3 と 4.4）**
- 位置と引用: main.tex:234「Choosing structure and shrinkage on other writers leaves a remainder below $10^{-3}$ nats per symbol at the fixed base smoothing in the 15-session panel」と main.tex:273（3a の表）。
- なぜ問題か: 宣言文の見出しは Mensh Rule 7 に沿う。しかし限定を全部載せた 30 語前後の見出しは、目次として読めない。
- 解消の条件: 限定は本文の最初の文へ移し、見出しは主張だけにする。
- 自信: 中

**12. [severity: nit] 要旨に、文献の穴（何が欠けていたか）の文が無い**
- 位置と引用: 要旨の 1 文目「Whether a per-person model looks worthwhile depends on what it is compared with.」の次の文が、すぐに方法（「In exploratory analyses of two public keystroke datasets …」）になる。
- なぜ問題か: 接地: Mensh Rule 5「The context must communicate to the reader what gap the paper will fill.」。序論 main.tex:45 にある「no study that compared … with both a stronger shared model and the person's own simple baseline」が、要旨には無い。
- 解消の条件: 語数が許せば、穴を 1 句で足す（指摘 3 で削る語数を充てる）。
- 自信: 低

### 3c. 分量（brief の「見ること」の 2）

- 規程に上限は無い。7,263 語は、参考に挙がっている UMUAI の論文（約 9,800〜13,300 語・照合していない）より短い。長さそのものは欠陥にしない。
- 問題は長さよりも密度と繰り返しである（指摘 5）。
- 本文に置く必要が無く、補足資料へ移せるもの:
  - main.tex:137 の EM の初期化と収束（「each fit runs EM from two starting points … at most 500 iterations」）
  - main.tex:149 の同値の扱い
  - main.tex:178 の先頭の記号の採点（指摘 6）
  - main.tex:180 の 6 つの事後の変更の列挙（本文には数と参照だけを残す）
  - main.tex:276 の split の細部（「5\% and 25\% of pairs」）
  - main.tex:282 の prior mode の 2 つの対照
  - main.tex:341 と 342 の限界の細部（「about one time in six」「different local optimum」）

## 4. 判定

**直してから回す。**

1. 中心の発見（弱い比べでの利得 0.19 に対し、強い比べでの残りは桁が下）は、要旨と序論から 1 文で言える。UMUAI の「evaluation of user models」にも入るので、回さない理由は無い。
2. ただし要旨の中で gain が 2 つの意味を持ち、2 つの平滑の条件に 3 つ以上の呼び名がある。そのため、決定に関わる値がどれかを、想定読者は戻り読みなしでは掴めない（指摘 2〜4）。
3. 今回足した入れ替えの対照は、「more than half」の根拠が数から追えないまま序論と 4.4 に入り、読みやすさを下げた（指摘 1・7）。語の統一とこの段の組み直しは、計算を足さずに済む。

## 5. 読めなかった範囲と注入の疑い

- 読めなかった範囲: 補足の印のファイル（figdata の CSV・kit の README）は、指示どおり読んでいない。Figure 3 の数値の点は CSV に依存するので、図の中の値は本文と表からしか照らしていない。references.bib はエントリの見出しの行だけを見て（33 件）、書誌の中身は読んでいない。
- 注入の疑い: なし（main.tex・mensh.txt・context-A・carryover に、査読者や LLM に向けた指示の文は見当たらなかった）。

参照したファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-8/context-A.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-8/carryover-E.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-8/tmp/sources/mensh.txt