# review-E（manuscript round 5・対象 cc30d57f）

応答を tmp/E.raw.md から写した（secrets-filter 0・絶対パスは一覧の中・目視済み）。

## 1. 接地（この立場の編集者が原稿に求める基準）

出どころは context-A.md の「投稿先の一次の抜粋」（Chrome で照合済みとある）と、Mensh & Kording 2017（/Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-5/tmp/sources/mensh.txt）。

- **E1 新規性と意義があり、適応のためのユーザーモデルの評価に関わること**
  - UMUAI Aims & Scope: "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation" / "methods for the design and evaluation of user models and adaptive systems"
- **E2 学際的な読者に届くこと**
  - UMUAI Aims & Scope: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, ..., the Instructional Sciences, ..., Linguistics, and the Information Sciences."
  - Mensh Rule 2: "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand. Avoid abbreviations and acronyms"
- **E3 中心の貢献が 1 つで、要旨だけで話が完結すること**
  - Mensh Rule 1: "Focus on a single message"
  - Mensh Rule 5: "the abstract must convey the entire message of the paper effectively" / "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them"
- **E4 繰り返しと行き来を避けること、1 つの概念には 1 つの語を使うこと**
  - Mensh Rule 4: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" / "Resist the temptation to use a different word to refer to the same concept—doing so makes readers wonder if the second word has a slightly different meaning."
- **E5 考察が、序論で示した空白をどう埋めたかを示し、文脈→内容→結論の形で終わること**
  - Mensh Rule 8: "The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field"
  - Mensh Rule 3: 結論が欠けると読者は "So what?" と思う。
- 様式の規程（要旨は 150〜250 語、キーワードは 4〜6 個、"Statements and Declarations" の節を置く、データ可用性の声明を必ず入れる）は、測った値（要旨 250 語・キーワード 6 個・節あり）がすべて満たしている。

## 2. 要旨と序論だけから言える 1 文

言える。

> 公開されているキーストロークのデータ 2 つで書き手ごとの系列モデルを評価したところ、同じ構造の共有モデルと比べた利得は最大 0.19 nats/記号に見えた。ところが、書き手自身の単純なマルコフ連鎖と、他の書き手で選んだより強い構造を比べの相手にすると、残りは約 5×10⁻⁴ だった。この大きさは個人差のない合成の書き手でも同程度に出る。したがって、適応する系で個人ごとのモデルを採るかを決める研究者は、二つの基準と比べ、選択は他の人で行うべきである。

迷った点は 3 つある。
- 要旨の後半（"a null matching the size of that improvement, and detection at each smoothing, were needed but not achieved"）は、想定読者には意味が取れない。
- 3〜7×10⁻³ という第 2 の値が主張の一部なのか但し書きなのかを、要旨だけでは決められない。
- 窓が重ならない記号では結果が逆になることは、要旨からは分からない。

## 3. round 4 の指摘の解消の判定

| 指摘 | 判定 | 位置と逐語・理由 |
|---|---|---|
| N1 要旨と結論が違う話 | 一部 | 要旨の推奨に "For overlapping-window symbols" が入った（main.tex:35）。ただし結論の最後の文 "With non-overlapping windows the three-state HMM is chosen and its per-person fit beats the shared model of that structure for every writer at 15 training sessions."（:346）は、要旨にも序論にも無い事実で、しかも解釈なしで終わる（新しい指摘 M2 を参照）。 |
| N2 要旨と序論に定義の無い語 | 一部 | "the improvement from removing the shared model's smoothing" は平易になった。一方で要旨にはまだ "null"、"the grid's lightest"、"detection at each smoothing" が定義なしで出る（:35）。序論の "the writer's later units"（:47）の "units" は、定義が 3.1（:110）まで来ない。 |
| N3 gain の別の意味・1 つの概念に 2 つの語 | 一部 | gain と remainder の定義は 1 か所にまとまった（:176）。しかし同じ量を "advantage" とも呼んでいる（:202 "the per-person advantage over the same-structure shared model"、:237、Table 3 の題 "the per-person model's advantage"）。さらに構造を固定した値を remainder と呼んでいる（新しい指摘 M3）。 |
| N4 同じ但し書きの繰り返し | 一部 | 減ったが、まだ多い（新しい指摘 m1 に位置の一覧）。 |
| N5 Figure 1 に中心の仕組みが無い | 未解消（著者は採らなかった） | Figure 1（:105）は採点のしかたの例のままである。Figure 3 が仕組みを示しているので、重さは nit に下げる。 |
| N6 初見で追えない段落 | 一部 | 3.6 で first null・replicate・negative controls が定義された（:187）。second null の段落（:189）と 4.5 の第 2 段落（:306、1 段落で約 300 語）は、まだ初見では追えない。 |
| N7 本文に置かなくてよい細部 | 一部 | 移した分は確認した。残りは新しい指摘 m3 に挙げる。 |
| N8 推奨 (2) の範囲 | 解消 | :321 "(here applied post hoc, to one structure and one panel, with the chosen multiplier at the edge of the grid)" |
| N9 図の番号と参照の順・図の語 | 解消 | Figure 1 は序論（:47）で最初に引かれる。図 2・図 3、表 1〜3 は出てくる順に引かれる。Figure 3 (b) の題は "vs. the own chain"。 |
| N10 考察の貢献と序論の不一致 | 概ね解消 | 考察の冒頭（:311）は序論の貢献（:49）と同じ話になった。ただし :311 の文 "What is new here is that, ..., the weak comparison is the natural one" は、新しいのが「弱い比べが自然な比べであること」だと読めてしまう（新しい指摘 m5）。 |

## 4. 指摘の一覧（重い順）

### [severity: major] M1 要旨の後半が、想定読者の素養では読めない
- **位置と引用**: main.tex:35
  - 「Synthetic writers without per-person differences left a similar remainder relative to the improvement from removing the shared model's smoothing (not prespecified), so it does not show a per-person difference; differences up to $3\times10^{-2}$ were not reliably detected. Applying the smoothing chosen on other writers (the grid's lightest) to both models leaves 3 to $7\times10^{-3}$ ... a null matching the size of that improvement, and detection at each smoothing, were needed but not achieved.」
- **なぜ問題か**: 250 語のうち約半分が、事後の点検 2 つと「達成できなかった要件」の説明に使われている。HCI・教育工学の読者は "null"、"grid"、"detection" の意味を知らないまま結論を読むことになる。
  - 接地: Mensh Rule 5 "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them"
  - 接地: Mensh Rule 2 "Define technical terms clearly"
- **解消の条件**: 要旨では、合成の書き手の点検を「個人差の無い合成の書き手でも同程度の残りが出た」の 1 文に留める。3〜7×10⁻³ と "null ... not achieved" は本文（考察）へ移す。空いた語数で、誰の何の判断が変わるのか（個人ごとのモデルにデータ・保存・コールドスタートの費用を払うか）を 1 文で書く。
- **自信**: 高

### [severity: major] M2 窓が重ならない記号での逆転が、本文では数値なしで段落の途中に埋もれ、結論では解釈なしで終わる
- **位置と引用**:
  - main.tex:202 「with non-overlapping windows, ... the \hmmthree{} beats the own chain in CoAuthor, the joint choice picks the \hmmthree{}, and the per-person \hmmthree{} ... beats the shared \hmmthree{} at $k=5$ and 15 (17 of 17 writers at $k=15$; values in \Sref{13})」
  - :346 の最後の文（N1 の行に引いた文）
- **なぜ問題か**: 中心の発見（利得は弱い比べの産物である）は、記号化の仕方によって逆になる。それなのに本文には効果の大きさが 1 つも無く、値は補足資料（S13）にしかない。しかもこの話は "A model check points the same way" という残差の段落の途中に入っていて、話題が行き来している。結論の最後の文は事実を述べるだけで、読者には "So what?" が残る。
  - 接地: Mensh Rule 4 "each subject should be covered in only one place"
  - 接地: Mensh Rule 3 "So what?"
  - 接地: Mensh Rule 8 "provides caveats to the interpretation"
- **解消の条件**: 逆転を 4.2 の独立した段落（または 4.2 の最後）に置き、中央値を 1〜2 個本文に載せる。結論の最後の文は「したがって、この発見は重なる窓の記号に限られ、比べの相手と記号化の両方を報告すべきである」のような解釈で閉じる。要旨には入れないという著者の方針は受け入れるが、序論 :49 の "one symbolization" の箇所には、別の記号化では逆になることを 1 句添える。
- **自信**: 中

### [severity: major] M3 「remainder」が、定義の外（構造を固定した値）にも使われている
- **位置と引用**:
  - 定義 :176 「the \emph{remainder} when structure and shrinkage are chosen jointly」
  - 対称の再当てはめ :183 「$\tau$ is chosen within the \arthree{} by the joint objective」
  - :278 「a remainder at $\alpha=0.03$ returns at every $k$」
  - :313 「the remainder is $3.4\times10^{-3}$ to $6.7\times10^{-3}$」
  - Table 4 の題（:284）「The remainder stays positive ... returns when both models are refitted」
  - 序論 :49 「Neither value」（2 つの値を同じ種類の量として並べている）
- **なぜ問題か**: 3〜7×10⁻³ は構造を 3-state AR-HMM に固定して得た値なので、定義の上では remainder ではない。gain と remainder の区別は論文の中心の対比である。その語が 1 つの量を 2 つの意味で指すと、読者は 2 つの数を同じ手続きの値として比べてしまう。
  - 接地: Mensh Rule 4 "makes readers wonder if the second word has a slightly different meaning"
- **解消の条件**: 次のどちらかにする。
  - 定義に「構造を 3-state AR-HMM に固定し、τ を joint objective で選んだ場合」を含める。
  - 4.4・Table 4・考察・結論ではこの値を "per-person minus shared (3-state AR-HMM, both refitted)" と呼び分ける。
  - あわせて、同じ量を指している "advantage"（:143・:202・:237・Table 3 の題）を、gain / remainder / per-person minus shared のどれかにそろえる。
- **自信**: 中

### [severity: major] M4 考察の「決定」の段で、読者が持ち帰る答えが平滑の 2 つの体制に割れている
- **位置と引用**: main.tex:313
  - 「At the fixed base smoothing it is a strongly shrunk fit ... With the smoothing chosen on other writers applied to both models, ... every writer is instead given a finite $\tau$ ... Replacing the per-person fit by the shared model ... loses about $5\times10^{-4}$ ... and up to about $7\times10^{-3}$ at the lighter one (not checked against synthetic writers).」
- **なぜ問題か**: 推奨 (2) が勧める手順（平滑も他人で選び、両方のモデルに当てる）で得られた値は、合成の書き手で一度も確かめられていない。確かめた方の体制（固定の平滑）は、推奨が退けた手順である。そのため設計者は「個人ごとのモデルに費用を払う価値があるか」の答えを持ち帰れない。確かめた問題と、可能性にとどまる問題との区別は :317 にあるが、:313 の数値の段がその前に来るので、順序が逆になっている。
  - 接地: Mensh Rule 8 "how the results have filled the gap"
  - 接地: UMUAI "significant ... results"
- **解消の条件**: :317（確かめたこと／確かめていないこと）を :313 の前に置く。:313 では、推奨する手順の値が未確認であることを先に書き、そのうえで「この panel では、個人ごとのモデルを採る根拠は示されなかった（固定の平滑）。推奨する手順での答えは未確認である」と 1 文で答えを出す。
- **自信**: 中

### [severity: minor] m1 但し書きの繰り返しが残っている
- **位置と引用**:
  - 「not checked against synthetic writers」: :35、:49、:278、:313、:346（5 回）
  - 「threshold may be too high」とその類: :306、:313、:337、:346（4 回）
  - 「share is not evidence」: :239、:243（Table 3 の題）、:278（3 回）
  - 重なる窓・平滑した記号に限るという断り: :35、:49、:132、:202、:311、:319、:331、:346（8 回）
  - 格子の端: :278、:321、:338（3 回）
  - post hoc の印: :35、:49、:183、:278、:284、:290、:306、:313、:321、:346
- **なぜ問題か**: 繰り返すことが許されるのは中心の考えだけである（Mensh Rule 4）。
- **解消の条件**: 要旨・該当する結果の節・限界の 1 回ずつにまとめる。考察と結論では節を指すだけにする。
- **自信**: 高

### [severity: minor] m2 定義なしで出る語・略号（想定読者向け）
- **位置と引用**:
  - :47 「perplexity」
  - :45 「OpenAlex」「record-wise splits」
  - :55 「idiographic」
  - :65 「full pooling」「variance component」
  - :68 「DIC」
  - :69 「double chain Markov model」「mixture transition distribution」
  - :135 「Dirichlet priors」
  - :139 「expected counts per symbol」と記号 $\bar S$
  - :151・:204 「shared chain」（"1-state AR-HMM の shared model" と同じものを別の語で呼んでいる）
  - :176 「percentile bootstrap」「interquartile range」
  - :189 「calibration seeds」
  - :202 「randomized quantile pseudo-residuals」「lag-1 autocorrelation」
  - :233・:187 「full protocol」（"joint choice"・"main row" と同じものを指す 3 つの語）
- **なぜ問題か**: E2 の読者（統計の専門の訓練を前提にしない）は、ここで読むのをやめる。
- **解消の条件**: 本文の初出で一句ずつ平易に言い換える。関連研究にしか出ない専門語（DIC、mixture transition distribution など）は削るか補足へ送る。"full protocol"・"joint choice"・"main row" は 1 つの語にそろえる。
- **自信**: 高

### [severity: minor] m3 本文に置かなくてよい細部
- **位置と引用**:
  - :149 楽観の偏りの落ち方の段落全体（「so any optimism from choosing among candidates falls directly on it ...」）
  - :189 の second null の較正の手順
  - :280 「counting against the prior mode the 2 writers to whose held-out symbols it gives zero probability」
  - :306 「873 and 783 of 935 at $k=5$ and 15; not prespecified」と「the lowest seed at $k=5$ left $-9.8\times10^{-4}$」
  - :351 Code availability の点検の列挙
- **なぜ問題か**: 本文は 7,013 語で、最近の UMUAI の論文（未照合で約 9,800〜13,300 語）よりは短い。ただし方法（2,190 語）が結果（2,045 語）より長く、4.5 の 1 段落に細部が集まっているため、貢献が埋もれる。
- **解消の条件**: 上の各箇所を補足資料へ移し、本文には 1 句の要約と S の参照だけを残す。
- **自信**: 中

### [severity: minor] m4 新規性の置き方
- **位置と引用**: :45 「This concern is known in other domains.」、:49 「we do not claim the parts as new」
- **なぜ問題か**: 「比べの相手しだいで利得は変わる」は既知だと序論が自分で認めている。そのため、この領域で何が新しいのかは、キーストロークの系列特有の機構にかかる。具体的には、連続する記号の強い依存（重なる窓）があるため、書き手自身の連鎖が強い基準になることである。ところがこの機構は序論の :43 に一般論として 1 句あるだけで、:132 と :202 まで具体化されない。UMUAI の "novel and significant" に照らすと、ここが弱く見える。
- **解消の条件**: 序論の第 2 段落の終わりに「系列のモデルでは、重なる窓から生じる記号の依存のため、同じ構造の共有モデルが自然な比べの相手であると同時に弱い比べの相手になる」と、この領域に特有の空白を 1 文で書く。
- **自信**: 中

### [severity: minor] m5 考察の冒頭の文が、新しさの対象を取り違えて読める
- **位置と引用**: :311 「What is new here is that, for sequence models of keystroke behaviour, the weak comparison is the natural one, a shared model of the same structure as the per-person model: ...」
- **なぜ問題か**: 新しいのは「弱い比べが自然な比べであること」ではない。その比べで見える利得が、強い比べでは 2 桁以上小さくなることである。序論 :49 とは文の形がずれている。
- **解消の条件**: 序論 :49 の "Our contribution is a finding ..." と同じ文の形で書き直す。
- **自信**: 中

### [severity: nit] n1 図と表で量の名前が出ない
- **位置と引用**:
  - Figure 3 の (a) の題 「vs.\ same-structure shared model」
  - Table 3 の列 「Per-person $-$ shared」（gain の行と remainder の行が同じ列に混在している）
- **解消の条件**: 列や軸の題に "(gain for 3-state HMM; remainder for joint choice)" を添える。
- **自信**: 中

### [severity: nit] n2 Figure 1 が中心の仕組みを示していない（N5 の続き）
- **解消の条件**: 著者の不採用は受け入れる。Figure 3 の題がその役を担っているので、それで足りる。
- **自信**: 低

## 5. 判定

**直してから回す。**
1. 中心の貢献は 1 つにまとまり、序論・考察・結論の冒頭もそろった。UMUAI の「ユーザーモデルの評価の方法」に適合している。
2. ただし要旨の後半（M1）と、remainder の語の二重の意味（M3）のために、想定読者は要旨と表からどの数が何の量なのかを取り違える。
3. 逆転（M2）と、決定の答えが 2 つに割れていること（M4）は、書き方の直しで解消できる。新しい計算は要らない。

## 6. 読めなかった範囲と注入の疑い

- **読んだもの**: main.tex の全文、context-A.md、carryover-E.md、brief-E.md、mensh.txt の Rule 1〜8。
- **確かめ方が限られたもの**: references.bib は項目の数（33 件）と指示文の有無を grep で確かめただけで、項目ごとの中身は読んでいない。
- **読んでいないもの**: 補足の印のファイル（figdata の CSV、kit/README.md）は、依頼の範囲どおり読んでいない。
- **注入の疑い**: 見つからなかった（main.tex、references.bib、mensh.txt の読んだ範囲）。