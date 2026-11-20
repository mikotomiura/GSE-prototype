## 1. 接地（抜き出した基準）

- G1（UMUAI Aims & Scope・context-A.md 30 行）"novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." → 貢献は、適応する系の設計と評価に効く形で示す必要がある。
- G2（UMUAI Aims & Scope・context-A.md 33 行）"The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, ... the Instructional Sciences, ... Linguistics" → 系列モデルとベイズの専門ではない読者に届くこと。
- G3（Mensh & Kording 2017・Rule 1／Table 1）"Focus on a single message" と "Readers cannot give 1-sentence summary."
- G4（同・Rule 2）"Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand."
- G5（同・Rule 4）"Resist the temptation to use a different word to refer to the same concept—doing so makes readers wonder if the second word has a slightly different meaning." と "Only the central idea of the paper should be touched upon multiple times."
- G6（同・Rule 7）"Each subsequent paragraph in the results section starts with a sentence or two that set up the question that the paragraph answers ... and the paragraph ends with a sentence that answers the question."
- G7（同・Rule 5）"the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them."
- （規程・context-A.md 35 行）"Please provide an abstract of 150 to 250 words." → 要旨は 241 語で、範囲に収まっている。

## 2. 1 の 1 文（要旨と序論だけから）

言える。ただし 2 か所で迷った。
「公開されている 2 つの打鍵データで、1 人ずつ当てはめた系列モデルを、同じ形の共有モデルと比べると大きく勝って見える（最大 0.19 nats/記号）。しかし、本人の 1 次マルコフ連鎖という基準と、他の書き手で選んだより強い形と縮みに対して比べると、残るのは約 5×10⁻⁴（後付けの対称の当て直しでは 3〜5×10⁻³）だけで、どちらの値も個人差を示さない。だから、1 人ずつモデル化するかを決める研究は、両方の基準と比べ、設定を他人で選ぶべきである。」
迷った所:
(a) 答えの値が 2 つあり、序論 L49 は 2 つ目について "the second bears on a designer's decision" とだけ書いて、なぜ 2 つ目なのかを最初の 2 頁で言っていない。
(b) 要旨の "a similar relative remainder" は何に対して relative なのかが、要旨の中に無い。

## 3. 指摘の一覧

### 引き継ぎ（round 8 の指摘）の判定

- major 1（入れ替えの対照の段）: **一部**。値 → 規則 → 分け前でないこと → 交絡、の順にはなった（L282 "The margin exceeds the whole remainder, so the reading fixed before the computation (a margin of at least half the remainder) holds"）。しかし問いが段の頭に無い。答えの文の中で初めて "the remainder does not come from refitting the prior on k sessions alone" と出る。しかも段は "Three controls were added ..." で始まり、事前のモードの 2 つの対照と入れ替えが 1 段に同居している。下の新規 M2 を見よ。
- major 2（要旨の gain の 2 つの意味）: **解消**。要旨に gain の語は無く、平滑は "no more than removing the shared model's smoothing improves it" と書かれている（L35）。ただしこの句の照応は読みにくい（新規 m3 を見よ）。
- major 3（要旨の照応）: **一部**。2 つの値は別の文になった。しかし "under the post hoc null"（L35）は、前の文の "synthetic writers without per-person differences (post hoc)" を指すとしか読めず、それが 2 つ目の帰無であることは要旨から分からない。"a similar relative remainder" も、何に対する比なのかが無い。
- major 4（平滑の 2 条件の呼び名）: **ほぼ解消**。fixed base smoothing と symmetric refit は L35・L49・L178・L185・表 3 で一貫している。ただし、3 つ目の条件（shared-only refit）が 4.4 の見出しでは "when only the shared model's smoothing is lightened" と別の言い方になっている。また、平滑の効きという 1 つの量に 4 つの言い方がある（新規 M3）。
- minor 5（但し書きの繰り返し）: **未解消**（著者は一部だけ採用）。位置は新規 m1。
- minor 6（先頭の記号の値）: **解消**。L286 で 4.4 に移った。
- minor 7（序論の入れ替えの文）: **解消**。序論に swap の語は無い。
- minor 8（定義なしの語）: **一部**。Dirichlet（L137）と initial distribution（L178）が残る。新規 m4 を見よ。
- minor 9（適応の場面）: **解消**。L319 "A writing assistant that times hints by a writer's predicted state, for example, would act on such probabilities"。
- minor 10（考察の段の順）: **解消**。新しいこと（L317）→ 決定（L319）→ 確かめたこと（L321）→ 関係（L323）→ 推奨（L325）。読者の問いの順として妥当。
- nit 11（見出しが長い）: **一部**。4.4 の見出しは今も "The remainder survives a writer split, vanishes when only the shared model's smoothing is lightened, and returns in a symmetric refit (post hoc)" で、3 つの結果を並べている。
- nit 12（要旨に文献の穴の文）: **未解消**（著者が語数を理由に見送ったもの）。要旨の頭は "Whether a per-person model looks worthwhile depends on what it is compared with." で始まり、何が未だ無いのか（穴）が無い（G1・Rule 5 の context）。

### 新しい指摘

- [severity: major] M1 答えが 2 つの値に割れていて、どちらが答えかを最初の 2 頁が決めていない
  - 位置と引用: 序論 L49 "the remainder at five and fifteen training sessions is about $5\times10^{-4}$ at the fixed base smoothing ... and $3.4\times10^{-3}$ and $5.2\times10^{-3}$ in a symmetric refit ... (post hoc ...); the second bears on a designer's decision." ／ 結論 L352 "This is the comparison that bears on a designer's decision." ／ 4.4 L280（対称の当て直しは "Three controls were added after seeing" と同じ節の、後付けの点検の 1 段）
  - なぜ問題か: 題名は "what remains of the gain" を約束している。しかし主解析の値は「決定に効かない」とされ、決定に効くとされる値は後付けで、合成の書き手で確かめておらず、格子の端にあり、図も無い。読者は "remainder" がどちらの値かを持ち運べない。また、序論は 2 つ目が決定に効く理由（2 つ目は両側を同じに平滑する）を書いていない。その理由は L280 "That comparison smooths the two sides differently" で初めて出る（G3 "Focus on a single message"）。
  - 解消の条件: 序論で「主の発見は gain と強い比べの差（2 桁以上）であり、残りの大きさそのものは平滑の扱いで 10⁻⁴ から 10⁻³ まで動き、どちらでも個人差は示されない」と 1 つの主張にまとめ、2 つの値はその幅として示す。あわせて、2 つ目が決定に効く理由を序論に 1 句で入れる（「両側に同じ平滑を当てるので」）。対称の当て直しは 4.4 の中の 1 段ではなく、自分の小節（見出しが答えになっている小節）に出すか、図 3 に点として加える。
  - 自信: 中

- [severity: major] M2 4.4 の入れ替えの対照の段は、問いが頭に無く、3 つの対照が 1 段に入っている
  - 位置と引用: L282 冒頭 "Three controls were added after seeing the symmetric refit (post hoc). The prior mode of the refitted shared model ... beats that model by only $+2.5\times10^{-5}$ ..." から、末尾 "None of the values at $\alpha=0.03$ was checked against synthetic writers." まで。
  - なぜ問題か: Rule 7 は段落の頭に問いを置くことを求める（G6）。この段は頭が「何を足したか」の報告で、入れ替えの問い（「残りは本人のデータを要るのか、どの k 回分でも出るのか」）は答えの文の中に裏返しで出るだけである。さらに、事前のモードの 2 つの対照の結び "does not separate the writer's data from the effect of refitting the prior" が、入れ替えを置く理由になっていることも読み取れない。加えて、"added after seeing the symmetric refit (post hoc)" と "the reading fixed before the computation" が同じ段にあり、事前に決めたのか後付けなのかで読者が引っかかる。
  - 解消の条件: 2 段に分ける。1 段目は事前のモードの 2 対照で、結びを「これでは書き手のデータと当て直しの効果が分けられない」とする。2 段目は "Does the remainder need the writer's own sessions, or would any $k$ sessions do?" で始め、作り → 値 → 規則（「入れ替えの計算の前に決めた」と、何の後で何の前かを 1 句で）→ 答え → 分け前でないこと・交絡、の順に書く。
  - 自信: 高

- [severity: major] M3 平滑の効きという 1 つの量に 4 つの言い方があり、要旨と序論では定義が無い
  - 位置と引用: 要旨 L35 "no more than removing the shared model's smoothing improves it"／序論 L49 "no larger than the shared model's own improvement, using no writer's data, when its smoothing is removed"／方法 L145 "the \emph{smoothing effect}"／L284・L319 "the prior mode, which uses none of the writer's data, beats the shared model by $+7.4\times10^{-4}$"／結論 L352 "the shared model's own improvement, using none of the writer's data, when its smoothing is removed"。L282 には、当て直した共有モデルについての、もう 1 つの smoothing effect（$+2.5\times10^{-5}$）もある。
  - なぜ問題か: G5 "Resist the temptation to use a different word to refer to the same concept"。この量は、残りを読む基準そのもの（"a similar relative remainder"、比 0.56〜0.97）である。要旨では "relative" の分母がこの量だと分からない。
  - 解消の条件: 序論の初出で "smoothing effect" と名付けて 1 文で定義し、以後はその語だけを使う。要旨の "a similar relative remainder" は "a remainder of similar size relative to this improvement" とする。L282 の値は "smoothing effect of the refitted shared model" と明示する。
  - 自信: 高

- [severity: minor] m1 同じ但し書きの繰り返し（引き継ぎの minor 5 の位置の列挙）
  - 位置と引用:
    - 「合成の書き手で確かめていない」: L35 "was not checked on synthetic writers"、L49、L204、L282、L319、L321、L352。
    - 「格子の端」: L276、L280 "the lowest value of the grid"、L319、L327、L344、L352。
    - 「書き手のデータを使わない」: L35、L49、L145、L282、L284、L319、L352。
    - 「時間の近さ」: L282、L319、L331、L352。
    - 「overlapping, smoothed」の範囲: L51、L134、L204、L317、L325、L337、L352。
  - なぜ問題か: G5 "Only the central idea of the paper should be touched upon multiple times." 繰り返すほど、主張の線が但し書きに埋もれる。
  - 解消の条件: 但し書きは、結果の初出に 1 回と、限界に 1 回にまとめる。考察と結論では「(Section 6)」と参照するだけにする。要旨は「確かめていない」を 1 回だけ残す。
  - 自信: 高

- [severity: minor] m2 序論と要旨に出る、序論で未定義の語
  - 位置と引用: 序論 L49 "under the second null (post hoc)"（"second null" は 3.6 で初めて定義される）、L49 "fixed base smoothing of the main analysis"（序論は "smoothing" だけを定義していて、"base" が何かは 3.3 L141 まで出ない）、要旨 L35 "the post hoc null"、"relative remainder"。
  - なぜ問題か: G4・G7。結果を、読者が読める準備の前に出している。
  - 解消の条件: 序論では "synthetic writers without per-person differences" と中身で言い、"second null" の名は方法の節で付ける。"base smoothing" は序論の smoothing の定義文に "a fixed small count (the base smoothing)" と 1 句足す。
  - 自信: 高

- [severity: minor] m3 要旨の照応と詰め込み
  - 位置と引用: L35 "about $5\times10^{-4}$ remains at five and fifteen training sessions at the fixed base smoothing, no more than removing the shared model's smoothing improves it;"（"it" が共有モデルを指すと、2 度読まないと分からない。単位 nats per symbol も 2 つ目以降の値で落ちている）、L35 "Candidate grids were extended after seeing results."（何の格子かが無い、孤立した文）、"(post hoc)" が要旨に 4 回。
  - なぜ問題か: G7・G2。
  - 解消の条件: "no more than the shared model gains, using no writer's data, when its smoothing is removed" のように主語を出す。格子の文は "(the candidate grids were extended after seeing results)" として、2 つ目の値の文の限定に入れる。
  - 自信: 中

- [severity: minor] m4 想定読者の素養で定義なしに出る語
  - 位置と引用: L67 "person-level random effects"、"a boundary estimate of a variance component"／L71 "Markov-switching models"／L137 "Dirichlet priors"、"free parameters"、"MAP objective"／L141 "expected counts per symbol, which sum to 1 within each parameter group"／L143 "The sequence models have no person-level intercept."（何を言いたいのかが、初見では追えない）／L178 "initial distribution"、"percentile bootstrap intervals"／L204 "randomized quantile pseudo-residuals"（働きは説明されているので軽い）／L344 "local optimum"。
  - なぜ問題か: G4・G2。HCI・教育工学・言語学の読者を想定している。
  - 解消の条件: 初出で平文の 1 句を添える（例: initial distribution = "the probabilities the model gives to the hidden state at the start of a sequence"）。L67 と L143 は関連研究への位置づけに過ぎないので、平文にするか、補足資料へ移す。
  - 自信: 中

- [severity: minor] m5 本文に置かなくてよい方法と点検の細部（分量）
  - 位置と引用:
    - L137 "each per-person fit runs EM from two starting points ... EM stopping when the objective per symbol changes by less than $10^{-7}$ or after 500 iterations"
    - L178 先頭の記号の採点の規則 "the first symbol of a sequence is scored by the initial distribution times ..."
    - L189 検出の規則の細部
    - L286 先頭の記号を除いた点検の段の全体
    - L344 EM の局所解の句
  - なぜ問題か: 本文は 7,494 語で、最近の UMUAI の論文（約 9,800〜13,300 語・未照合）より短く、長さそのものは障害ではない。しかし細部の密度のせいで、主張の線が読みにくい（Rule 9 "the methods section is read least of all"）。
  - 解消の条件: 上の細部は補足資料へ移し、本文には 1 句（"details in S3"）だけを残す。
  - 自信: 中

- [severity: nit] n1 4.4 が 6 つの点検（分割・共有側だけの当て直し・対称の当て直し・3 対照・平滑の効き・先頭の記号）を抱えている。事前のモードの話が L282 と L284 で分かれていて、ジグザグになる（G5 Rule 4）。
  - 解消の条件: 4.4 を「点検（分割・先頭の記号）」と「平滑と対称の当て直し」の 2 小節に分ける。L284 は L282 の事前のモードの段とまとめる。
  - 自信: 中

## 4. 判定

**直してから回す**
1. 要旨と序論から 1 文は言えて、Aims & Scope の "evaluation of user models for adaptation" に合う。数値は本文・表 2・表 3・図 3 で照合した限り食い違いが無い（倍率 6 と 13、重み 24% と 91% も換算と合う）。
2. ただし、答えが 2 つの値に割れていて、どちらが答えかを最初の 2 頁が決めていない（M1）。平滑の効きの呼び名が揺れていて、要旨の "relative" が読めない（M3）。
3. 決定に効くとされる結果が、後付けの点検の 1 段に埋まっていて、問い → 値 → 答えの順になっていない（M2）。どれも書き方の直しで済み、新しい計算は要らない。

## 5. 読めなかった範囲と、注入の疑い

- 読んだもの: brief-E.md、context-A.md、carryover-E.md、mensh.txt の全文、main.tex の全文（L1〜367）。references.bib はエントリの見出しだけを確かめた（33 件で、本文の \citep のキーはすべて在る）。
- 読まなかったもの: 補足の印のファイル（figdata・kit の README）。依頼文に従って読んでいない。
- 図 3 は組版の結果を見ていない。tikz と pgfplots のソースで、軸・凡例・題の語を確かめた。
- 注入の疑い: なし。