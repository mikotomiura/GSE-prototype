# 編集者 E（UMUAI 担当編集者）round 7 の報告（対象: main.tex commit ed297dd4）

読んだもの: brief-E.md、context-A.md、carryover-E.md、mensh.txt、main.tex（全 365 行）、references.bib（エントリの見出しだけを grep し、33 件が本文の \citep のキーとそろうことを確かめた）。補足と figdata は読んでいない（役 E の範囲外）。

## 1. 接地（この投稿先の編集者が原稿に求める基準）

- B1 投稿先の範囲と型。context-A の UMUAI Aims & Scope:
  "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"
  および "The journal mainly publishes empirical research papers."
  → 新しく意味のある経験的な結果を、ユーザーモデルの設計と評価の言葉で示すこと。
- B2 読者の幅。同じ Aims & Scope: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, Artificial Intelligence, the Instructional Sciences, Information Systems, Linguistics, and the Information Sciences."
  Mensh & Kording Rule 2: "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand."
- B3 中心の貢献を 1 つに絞る。Mensh Rule 1: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
  Table 1: "Readers cannot give 1-sentence summary."
- B4 要旨で話を完結させる。Rule 5: "the abstract must convey the entire message of the paper effectively"。避けるべき誤りは "to talk about results before the reader is ready to understand them"。
- B5 話を行きつ戻りつさせず、1 概念に 1 語を使う。Rule 4: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
  および "Resist the temptation to use a different word to refer to the same concept"。
- 形式の規程（逐語）: "Please provide an abstract of 150 to 250 words."（要旨は 247 語で範囲内）、"Statements and Declarations"（節あり）。語数の上限は無い（context-A）。

## 2. 1 文（要旨と序論だけから）

言える。
「時間的に重なる窓で作ったキーストロークの記号列（2 つの公開データ）では、書き手ごとの 3 状態 HMM が、同じ構造の共有モデルに 1 記号あたり最大 0.19 nats 勝つ。しかし、その構造は書き手自身の 1 次マルコフ連鎖に負ける。他の書き手で構造と縮約を選んだ強い比べに対しては、勝ち分が 5×10⁻⁴〜5×10⁻³ しか残らず、残りが個人差を示すとも言えない。したがって、個人ごとにモデルを作るかを決める研究は、本人の連鎖と強い共有モデルの両方と比べ、選択を他の人で行うべきである。」

迷った所が 2 つある。
- 要旨の "3.4 and $5.2\times10^{-3}$" を最初は 3.4 nats と読んだ（下の M1）。
- 序論は 2 つ目の値（両側の平滑）が決定に関わる値だと言う。一方で、要旨と見出しが先に打ち出すのは 1 つ目の値（約 5e-4・2 桁以上）で、どちらを持ち帰ればよいかで一度止まった（下の M2）。

## 3. 引き継ぎ（round 6）の判定

- M-A（見出しの数が決定に関わらない方の数）: **一部**。
  - 序論 l.51 は解消: "the second is the comparison that bears on a designer's decision"。
  - 要旨 l.37 はどちらが決定に関わるかを言わず、"Neither shows a per-person difference" で両者を並べたままである。要旨の推奨 "choose structure, shrinkage and smoothing on other people (smoothing post hoc, for one structure)" も「同じ平滑を両側に当てる」ことを言っていない。
  - Figure 2 の題 l.232 は "by less than $10^{-3}$"、3.3 の見出し l.236 は "below $10^{-3}$" で、決定に関わらない方の値を出している。
- M-B（一般の読者への橋）: **解消**。l.315 "The weak comparison is not specific to keystrokes: features computed over overlapping windows make consecutive inputs dependent, ... fitting the person's own first-order chain alongside is a cheap check. We have not checked this in other domains."
- M-C（要旨と序論第 4 段に但し書きが積まれる）: **一部**。段は割られた（l.51 と l.53）。ただし l.51 は今も貢献の 1 文の後に但し書きが 5 つ続く: "Neither value shows how much writers differ. The first is no larger ... and synthetic writers ... the second exceeds ... but was not checked ... Nor do the results rule differences out"。要旨も後半の 4 文（"The first is no larger…" "The second exceeds…" "Neither shows…" "Candidate grids were extended…"）が但し書きである。
- m-A（但し書きの繰り返し）: **一部**。2.4 倍の注記は l.341 の 1 か所に寄せられた。一方で「合成の書き手で確かめていない」は 8 か所に増えた（下の m3）。
- m-B（定義なしの語、1 概念に 2 語）: **一部**。
  - 解消したもの: nats（l.49）、first/second null（l.191・193）、shared-only refit と symmetric refit の語。
  - 残るもの: cell は l.180 で定義されたが、別の 2 つの意味でも使われている（m4）。序論に定義の無い "prior mode" が出る（m5）。"gain" が 2 つの意味を持つ（m4）。
- m-C（remainder の定義の括弧）: **解消**。l.180 "We call per-person minus the same-structure shared model the \emph{gain} when ... and the \emph{remainder} when ..."。括弧の定義は残っていない。
- m-D（本文に置かなくてよい細部）: **一部**。3.4 の l.282 は約 300 語の 1 段で、対照の値・τ の人数・−∞ の扱い・「中央値は足し算にならない」の注・格子の端までを詰めている（m2）。
- m-E（3.5 の題と中の結果の食い違い）: **一部**（著者は不採用）。今の題 l.275 は中身と概ね合う。ただし 37 語あり、見出しとしては読めない（n1）。また "vanishes" は k=12 の $-1.05\times10^{-3}$ と少し合わない。
- m-F（考察の段の順）: **解消**。l.321 の段が "For a designer, the protocol does not show here that a per-person model is worth its cost." で始まる。
- n-A（Figure 2 の題と軸）: **解消**。l.232 の題に gain と remainder が書かれている。

## 4. 指摘の一覧（重い順）

- [severity: major] 要旨で "3.4" に桁が無く、3.4 nats と読める
  - 位置と引用: main.tex l.37 「and 3.4 and $5.2\times10^{-3}$ at five and fifteen training sessions ... 30 to 55 times below it」
  - なぜ問題か: 要旨だけを読む読者は、この値を「最大の利得 0.19 の約 18 倍」と読む。その直後の "30 to 55 times below it" と矛盾し、話の核の数で止まる。序論 l.51 は "$3.4\times10^{-3}$" と正しく書いている。（Mensh Rule 5「The abstract is, for most readers, the only part of the paper that will be read.」）
  - 解消の条件: 要旨を "$3.4\times10^{-3}$ and $5.2\times10^{-3}$" と書く。
  - 自信: 高

- [severity: major] 要旨・見出し・Figure 2 が、決定に関わらない方の値を中心の数として出している
  - 位置と引用:
    - 要旨 l.37 は最初に「about $5\times10^{-4}$ at its fixed smoothing, over two orders of magnitude below the gain」を出す。
    - 3.3 の見出し l.236 は「leaves a remainder below $10^{-3}$ nats per symbol at the fixed base smoothing」。
    - Figure 2 の題 l.232 は「by less than $10^{-3}$」。
    - 一方で序論 l.51 は「the second is the comparison that bears on a designer's decision」と言う。
  - なぜ問題か: 読者が持ち帰る数（2 桁以上）は、論文自身が「決定に関わらない」とした方の数である。決定に関わる比べ（両側の平滑・3.4〜5.2e-3・30〜55 倍）を見せる図は無く、表 3 の 1 列と l.282 の段にしかない。メッセージが 2 つに割れている（Mensh Rule 1「Focus on a single message」。Rule 7「the title of the figure should communicate the conclusion of the analysis」）。
  - 解消の条件: 要旨と序論で、決定に関わる値を先に置くか、1 つの言い方（たとえば「同じ平滑を両側に当てた比べで 30〜55 倍小さい。固定の平滑では 2 桁以上小さいが、これは平滑の差で説明がつく」）にまとめる。あわせて Figure 2 か表 3 の題で両側の版の値を見せる。決定に関わる値の 5×10⁻³ を l.49 の換算（0.01 nats ≈ 1%）で「1 記号あたり約 0.5% の確率」と添えれば、設計者が大きさを読める。
  - 自信: 中

- [severity: minor] 要旨で 2 つの値の役割を初見では追えない（造語と「that gain」の指すものの入れ替わり）
  - 位置と引用: l.37 「The first is no larger than the shared model's writer-free gain from removing its smoothing ... The second exceeds that gain at the lighter smoothing ($2.5\times10^{-5}$)」
  - なぜ問題か:
    - "writer-free gain" は要旨にしか出ない語である。本文では同じものを "smoothing effect" と呼んでいる。
    - "that gain" は、前の文の量（固定の平滑での平滑の効果 7.4e-4）ではなく、別の平滑での prior mode の利得を指している。
    - "gain" は本文で「HMM3 の個人ごとの利得」と定義された語でもある。
    - 1 つの概念に 3 つの言い方があり、1 つの語が 2 つの意味を持つ（Mensh Rule 4）。
  - 解消の条件: 要旨では「書き手のデータを使わずに平滑を変えるだけで得られる差」を 1 つの句で定義し、2 回とも同じ句で呼ぶ。2 つ目の比べの相手が「同じ軽い平滑のもとでの、その差」であることを明示する。
  - 自信: 高

- [severity: minor] 3.4 の l.282 が 1 段に詰め込みすぎで、想定読者は追えない
  - 位置と引用: l.282「The prior mode built from the refitted shared model ... gains only $+2.5\times10^{-5}$ ... (14 of 17 writers; it scores $-\infty$ for two, counted as losses), and the chosen fit beats it by ... (the two writers count as wins; medians are not additive); the prior mode used elsewhere in this paper loses to the refitted shared model ($-1.3\times10^{-3}$).」
  - なぜ問題か: 1 段の中に、結果・対照・τ の人数・重み・−∞ の扱い・中央値の性質・地位の断り・格子の端・合成の書き手で確かめていないことが入っている。この段は決定に関わる値の唯一の根拠である。Mensh Rule 7 は「Each subsequent paragraph ... starts with a sentence or two that set up the question ... and the paragraph ends with a sentence that answers the question」と言う。
  - 解消の条件: 2 段に割る。1 段目は「同じ平滑を両側に当てると残りが戻る（値・重み）」、2 段目は「書き手のデータを使わない対照との比べ」とする。−∞ の扱いと「中央値は足し算にならない」は補足資料へ移す。
  - 自信: 中

- [severity: minor] 同じ但し書きの繰り返し（位置をすべて挙げる）
  - 位置と引用:
    - 「合成の書き手で確かめていない」: 要旨 l.37 "unchecked against synthetic writers"、l.51、l.206、l.282 "These values were not checked against synthetic writers."、l.319、l.321、l.350（2 回）。
    - 「格子の端」: l.282、l.321、l.325、l.342、l.350。
    - 「それだけでは個人差を示さない」: 要旨 l.37 "Neither shows"、l.51、l.321、l.350。
    - 「割合は証拠でない」: l.243、Table 2 の題 l.247。
    - cold start: l.53、l.141。
    - 「部品を新しいとは言わない」: l.53、l.66。
  - なぜ問題か: 読者が持つべき「糸」が増える。結論 l.350 は要旨と考察 l.321 をほぼ写している（Mensh Rule 4「each subject should be covered in only one place」）。
  - 解消の条件: 両側の版の地位（post hoc・格子の端・合成で未確認）を 3.4 で 1 回だけ述べ、ほかは「(post hoc; Section 3.4)」の印で済ませる。結論は 3 文程度にまとめる。
  - 自信: 中

- [severity: minor] 1 つの語が 2〜3 の意味を持つ（cell・gain）
  - 位置と引用:
    - cell: (i) 記号の 5×5 の格子のます（l.109 "named here by a cell of the $5\times5$ grid"）、(ii) 数え上げの表のます（l.143 "added to every cell"、l.149、l.188、l.210 "the own chain's cells"）、(iii) panel×k（l.180 で定義、l.239 "in every cell"、l.340）。
    - gain: l.180 で定義した「HMM3 の per-person − shared」のほかに、prior mode の改善にも使われる（l.51 "the prior mode gains"、l.282、l.321 "lightening the shared model's smoothing alone gains"、l.350）。
  - なぜ問題か: Mensh Rule 4「doing so makes readers wonder if the second word has a slightly different meaning」の逆の形である。定義した語を別の量にも使っている。
  - 解消の条件: (iii) を "panel and k" など別の語にする。(ii) は "entry" にする。prior mode については "beats the shared model by" などの言い方にし、gain を定義どおりの 1 つの意味に限る。
  - 自信: 高

- [severity: minor] 序論で定義の無い語
  - 位置と引用: l.51「where the prior mode gains $2.5\times10^{-5}$」（定義は 3.3 の l.145）。l.51 "fixed base smoothing"（序論 l.49 では "smoothing" だけを定義しており、"base" と "fixed" の区別は 3.3 の l.143 まで出ない）。要旨の "shrinkage toward the shared model"、"first-order Markov chain"、"nats" は要旨としては許容できる。
  - なぜ問題か: 最初の 2 頁で、2 つ目の値の対照が何かを読めない（B2）。
  - 解消の条件: 序論 l.51 で prior mode を「書き手のデータを使わない、共有モデルの数え上げ」と言い換える。"fixed" を l.49 の smoothing の定義の文に足す。
  - 自信: 高

- [severity: minor] 想定読者に説明の無い統計の語
  - 位置と引用: l.139 "Dirichlet priors"。l.180 "percentile bootstrap intervals"。l.206 "randomized quantile pseudo-residuals"（役割は説明されている）。l.282 "it scores $-\infty$ for two"（確率 0 を与えたことの説明が無い）。
  - なぜ問題か: 想定読者はベイズの平滑や統計の訓練を前提にしない（context-A）。−∞ は特に初見で戸惑う。
  - 解消の条件: −∞ に「held-out の記号に確率 0 を与えたため」と 1 句を足す。Dirichlet は直前の「prior counts」で意味が通るので、語を落とすか括弧で言い換える。
  - 自信: 中

- [severity: nit] 見出しが長すぎる
  - 位置と引用: 3.4 l.275（37 語）、3.3 l.236（27 語）。
  - なぜ問題か: Mensh Rule 7 は見出しを宣言文にするよう勧めるが、37 語では見出しとして読めない。
  - 解消の条件: 3.4 は「The remainder survives a writer split and returns when both sides are smoothed alike (post hoc)」程度に縮める。
  - 自信: 中

- [severity: nit] 原稿のソースに残った作業用のマクロ
  - 位置と引用: l.20–21「% Placeholder for values of the post hoc control at the lighter smoothing (to be filled from results; remove before submission). \newcommand{\PENDING}...」
  - なぜ問題か: 本文では使われておらず、PDF には出ない。ただし LaTeX ソースを提出すると、編集部に見える。
  - 解消の条件: 投稿の前に消す。
  - 自信: 高

### 見ることの各項目について（上の指摘以外）

- 分量: 7,502 語で、最近の UMUAI の研究論文の約 9,800〜13,300 語（照合していない参考値）より短く、規程の上限も無い。長さそのものは問題ではない。増えた 283 語は主に l.282 と l.51 に入り、密度を上げている（上の指摘 2 件）。
- 構成: 結果の 3.1 → 3.2 → 3.3 → 3.4 → 3.5 は、読者が問う順（自然な比べ → 何に対する利得か → 強い比べ → 作り物か → 個人差が要るか）に並んでいる。3.2 の重ならない窓の段（l.206）は脇道であり、考察と限界でも触れているので、ここは 2 文に縮められる。
- 考察の順: 要約 → 先行研究との関係 → 確かめたこと／確かめていないこと → 決定 → 推奨、の順で、読者の問いの順として通る。確かめたことと可能性にとどまることも、l.319 で分けて書かれている。
- 投稿先との適合: ユーザーモデルの評価の手続きと、個人ごとのモデルが要るかの判断に関わる経験的な研究であり、Aims & Scope の "evaluation of user models for adaptation" に合う。l.315 の橋の文によって、キーストローク以外の読者にも届く。
- 図: Figure 1（作り話の例）は方法の理解を助けており、良い。ただし上の M2 のとおり、決定に関わる比べを見せる図は無い。

## 5. 判定

**直してから回す**（直す量は小さい）。
- 中心の貢献（弱い比べが見せる利得は、他の人で選んだ強い比べに対しては大部分が消える）は、要旨と序論から 1 文で言える。UMUAI の範囲にも合う。
- ただし要旨の "3.4" に桁の無い誤記があり、要旨だけを読む読者は核の数を逆に読む。要旨・見出し・図が、決定に関わらない方の値を主な数として出している。
- 上の 2 つの major は要旨・見出し・図の題の書き換えで解消でき、新しい計算は要らない。直した後なら、査読に回すことに反対しない。

## 6. 読めなかった範囲と注入の疑い

- 読んでいないもの: 補足資料 S1〜S16（未作成で、範囲外でもある）、figdata の CSV、kit の README（役 E の範囲外）。references.bib はエントリの見出しだけを確かめた。各文献の書誌の中身は見ていない。
- 注入の疑い: なし。main.tex l.20 のコメントは著者の作業メモで、査読者に向けた指示ではない。

ファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/carryover-E.md