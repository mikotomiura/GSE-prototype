# 編集者（UMUAI 担当・役 E）round 6 の判定

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit e6fdad49）と references.bib。行番号は main.tex のもの。

## 1. 接地（抜き出した基準）

- B1 新規で意義のある、適応とユーザーモデルの研究であること。UMUAI Aims & Scope（context-A.md の抜粋）: "provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." 分野の列挙に "methods for the design and evaluation of user models and adaptive systems" も含む。
- B2 素養の異なる読者に届くこと。同: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, Artificial Intelligence, the Instructional Sciences, Information Systems, Linguistics, and the Information Sciences."
- B3 要旨だけで全体が伝わること。規程: "Please provide an abstract of 150 to 250 words." Mensh & Kording Rule 5: "the abstract must convey the entire message of the paper effectively" / "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them."
- B4 中心の貢献を 1 つに絞ること。Mensh Rule 1: "Focus on a single message"。違反のしるし（Table 1）: "Readers cannot give 1-sentence summary."
- B5 用語を定義し、1 つの概念に語を 1 つだけ使い、ジグザグに書かないこと。Mensh Rule 2: "Define technical terms clearly"。Rule 4: "Only the central idea of the paper should be touched upon multiple times" / "Resist the temptation to use a different word to refer to the same concept"。Rule 8: 考察は "explains how the results have filled the gap ... provides caveats ... describes how the paper advances the field"。

## 2. 要旨と序論だけから言える 1 文

言える。ただし数字を 2 つ並べないと言えない。

「打鍵のリズムを 1 秒ごとの記号にしたデータで、書き手ごとの系列モデルの利得は、同じ弱い構造の共通モデルと比べると最大 0.19 nats/記号と大きく見える。だがその構造は書き手自身の単純なマルコフ連鎖に負ける。強い構造と縮約を他の書き手で選んで比べ直すと、利得は約 5e-4（固定の平滑）または 3〜7e-3（両側に同じ平滑・事後）にまで縮み、どちらも書き手ごとの違いの証拠にはならない。だから、人ごとにモデルを作るかを決めるときは、共通モデルと本人の連鎖の両方と比べ、選択は他の人で行うべきである。」

迷った所は 2 つある。(a)「残るもの」がどちらの数字か、要旨と序論からは決められない（下の M-A）。(b) 要旨の "relative to the effect of the shared model's smoothing" が何と何の比かは、序論まで読んでも分からない。

## 3. 指摘（重い順）

### round 5 の引き継ぎの判定

- **M1 要旨の後半が読めない: 一部。** "improvement" は消え、"The candidate grids were extended, and two checks added, after seeing results" と書き換えられた。しかし L35 の "Synthetic writers without per-person differences left a similar remainder relative to the effect of the shared model's smoothing (not prespecified), so it does not show a per-person difference" と "Applying the smoothing chosen on other writers (the grid's lightest) to both models leaves 3 to $7\times10^{-3}$ from five training sessions on, not checked against synthetic writers" は、shrinkage・smoothing・grid・planted を定義しないまま使っている。要旨の 9 文のうち 4 文が但し書き。
- **M2 重ならない窓の逆転: 解消。** L202 "this reversal may reflect the amount of data as well as the symbolization; it was not checked against synthetic writers"、L346 "studies should report the symbolization together with the comparison" で閉じている。
- **M3 remainder の定義の外の使用: 解消。** L176 で定義し、L204 は "beats the shared \arone{} by $+0.002$" と、remainder の語を使っていない。ただし定義の括弧が読みにくい（m-C）。
- **M4 決定の段が 2 つの平滑に割れている: 一部。** 決定の段の中は解消した。L315 "The comparison that bears on the decision applies the smoothing chosen on other writers to both models." ところが要旨・序論・考察の冒頭・結論は、決定に関わらないと L315 が言う 5e-4 を見出しの数字にしている。割れは原稿全体の水準に移った（M-A）。
- **m1 但し書きの繰り返し: 一部。** "not checked against synthetic writers" とその言い換えが今も 5 回ある。L35 "not checked against synthetic writers"、L49 "the second was not checked against synthetic writers"、L202 "it was not checked against synthetic writers"、L278 "These values were not checked against synthetic writers."、L313 "was checked neither against synthetic writers"。詳しくは m-A。
- **m2 定義なしの語: 一部。** perplexity・idiographic・DIC・EM・MAP は直った。cell・null・full pooling などが残っている（m-B）。
- **m3 本文に置かなくてよい細部: 解消。** Code availability（L351）は短くなった。ほかの細部は m-D に回す。
- **m4 新規性の置き方: 解消。** L45 "a shared model of the same structure is the natural comparison, but it is a weak one whenever that structure cannot carry the dependence between consecutive symbols."
- **m5 考察の冒頭の取り違え: 解消。** L311。
- **n1 図表で量の名前が出ない: 一部。** Table 2 の題は "falls from a gain of about $0.2$ to a remainder" と直った。Figure 2 の軸と表題（L215・L220 "(a) vs.\ same-structure shared model"、"nats per symbol"）には gain / remainder の語が無い。
- **n2 Figure 1 が中心の仕組みを示さない: 未解消（著者の判断）。** Figure 2 がその役を担っているので nit に下げる。

### 新しい指摘

- [severity: major] M-A 見出しの数字が、考察自身が「決定に関わらない」とした方の数字になっている
  - 位置と引用: 要旨 L35 "about $5\times10^{-4}$ remains over that structure's shared model at its fixed smoothing"／序論 L49 "about $5\times10^{-4}$ remains at the shared model's fixed smoothing"／考察 L311 "a remainder of about $5\times10^{-4}$ (0.05\%)"／結論 L346 "about $5\times10^{-4}$ remained at the fixed smoothing"。一方 L315 は "Nor does the remainder of about $5\times10^{-4}$ at that smoothing show a value of the writer's data ... The comparison that bears on the decision applies the smoothing chosen on other writers to both models" と書き、両側を同じ平滑にした版は 3.4e-3／5.2e-3（事後・合成で未確認）。
  - なぜ問題か: 題は "what remains of the gain" と問うのに、答えが 2 つある。しかも前面に出ている方の数字を、考察は決定の根拠として退けている。読者が 1 年後に持ち帰る数字が決まらない（B4: Mensh Rule 1 "Focus on a single message"）。設計者が 3〜7e-3（perplexity で約 0.3〜0.7%）を人ごとにモデルを作るに値すると読むべきかにも、本文は答えていない。
  - 解消の条件: 見出しを数字ではなく比べの構造に置く。たとえば「弱い比べでは約 0.19、強い比べではその 1/30 以下で、残りはどの平滑でも書き手の違いの証拠にならない」。そのうえで 2 つの数字を要旨・序論・結論で同じ 1 文の組として出し、どちらが決定に関わるかを同じ所で言う。3〜7e-3 が決定にとってどの大きさなのか（費用との対比、または判断できないこと）を考察で 1 文書く。
  - 自信: 高

- [severity: major] M-B 一般の UMUAI 読者に届く理由（仕組みの橋）が結論で細くなる
  - 位置と引用: 序論 L43 は広く "Adaptive systems that read behaviour logs often model each person separately" と始める。結論 L346 は "These findings are limited to overlapping-window symbols" で閉じ、推奨 L319 も "for overlapping-window symbolizations like ours" に限られる。
  - なぜ問題か: 「基準線しだいで人ごとの利得が大きく見える」という一般の教訓は、序論 L45 が自ら挙げるとおり他分野で既知。新しいのは、重なる窓で連続する観測が強く依存すると、依存を運べない構造の共通モデルが弱い比べになる、という仕組みのほうである。だが本文はこれを打鍵の記号の話にとどめている。このままだと、UMUAI の読者（B1 "novel and significant"、B2 の広い読者）にとっての意義が、1 データセットと 1 記号化の狭い所見に見えてしまう（Mensh Rule 1 の "the bridge that unifies these two facets"）。
  - 解消の条件: 序論の最後か考察の冒頭に 1〜2 文足す。滑らせた窓で特徴を作る適応系一般（学習ログ・センサ・対話）で同じ弱い比べが生じうること、その確かめ方（本人の 1 次の連鎖を基準線に足すこと）を書く。範囲の限定はそのまま残してよい。
  - 自信: 中

- [severity: major] M-C 要旨と序論の第 4 段が、結果を受け取れる前に但し書きを積む
  - 位置と引用: 序論 L49 は約 330 語の 1 段落で、貢献・4 つの数字・"post hoc" 2 回・"a ratio not prespecified"・合成の書き手・設計者への含意・手順の部品・分析の地位・限界を全部運ぶ。要旨 L35 は 248 語（上限 250）。
  - なぜ問題か: Mensh Rule 6 は、序論の最後の段落は "compactly summarizes the results" と言う。いまは読者が最初の 2 頁で読む所に、方法の地位の説明が混ざっている。忙しい読者は L49 の途中で何が貢献か見失う（B3・B4）。
  - 解消の条件: L49 を 2 段に割る。(i) 発見と 2 つの数字と設計者への含意。(ii) 手順の部品が既存であること、事後のもの、限界の参照。"(a ratio not prespecified)"・"including what \emph{post hoc} marks" は 3.4 節（L175 以下）に任せて消す。要旨からは "relative to the effect of the shared model's smoothing (not prespecified)" を外し、「同じ手順は、書き手の違いの無い合成データでも同程度の残りを返した」と言い切る。
  - 自信: 中

- [severity: minor] m-A 同じ但し書き・地位の説明の繰り返し（位置を全部挙げる）
  - "post hoc"／"after seeing results": L35、L49（2 回）、L178、L183、L189、L271（節題）、L278、L284、L290、L306、L313、L315（2 回）、L321、L336、L337、L346。
  - "does not show a per-person difference" とその言い換え: L35、L49、L239、L306、L315、L346。
  - 割合（share）は証拠でない: L239、L243（表題）。
  - "conditional on the fits and the choice": L176、L243。
  - 重なる窓に限る: L202 "The findings of this and the next section hold for overlapping, smoothed symbols"、L311 "This holds for overlapping, smoothed symbols"、L319、L331、L346。
  - なぜ問題か: Mensh Rule 4 "Only the central idea of the paper should be touched upon multiple times"。
  - 解消の条件: 3.4 節と表の一列（または脚注の記号）で地位を一度だけ定め、各所は記号か節の参照で済ませる。要旨・結論には各 1 回まで。
  - 自信: 高

- [severity: minor] m-B 定義なしの語・1 つの概念に複数の語（想定読者の素養で読んだ場合）
  - 定義なしの語:
    - "cell"（L176 "in every cell of that panel"、L235 "for every writer in every cell"）。panel × k のことと読めるが、定義が無い。
    - "first null"／"second null"（L187・L189）。統計の訓練の無い読者は帰無仮説と取りうる。
    - "full pooling"・"boundary estimate of a variance component"（L65）。
    - "double chain Markov model"・"mixture transition distribution"（L69）。
    - "backoff"（L59）。
    - "record-wise splits"（L45）。
    - "Dirichlet priors"（L135）。
    - "lag-1 autocorrelation"（L202）。
    - "nats"（要旨・L47 で単位の意味が無い）。
    - "e" 表記（Table 2・3）。
  - 1 つの概念に複数の語:
    - 平滑を共通モデル側だけに当てた比べ: "the asymmetric one"（L178）、"In the first version"（L183）、"Only shared refitted"（Table 3）、"When only the shared model is refitted"（L276）。
    - 両側の当て直し: "symmetric refit"（L176・L178・L338）、"symmetric version"（L183）、"Both refitted"（Table 3）、"applying the same smoothing to both models"（L313）。
    - 基準の平滑: "fixed smoothing"、"fixed base smoothing"、"base smoothing"。
    - 本人の連鎖: "own chain"、"writer's own Markov chain"、"writer's own first-order Markov chain"。
    - "joint choice" と "joint objective"（L183）。
    - "advantage"（L143 "median advantage over the shared model"）が gain / remainder と並んで残る。
  - 図と本文: Figure 2 の題 "(a) vs.\ same-structure shared model" は本文の gain / remainder に対応しない（n1）。
  - 解消の条件: 語を 1 つずつに固定し（例: "shared-only refit" と "symmetric refit"）、上の語は初出で 1 句ずつ定義するか、関連研究の専門語は削る。
  - 自信: 高

- [severity: minor] m-C remainder の定義の括弧が初見で矛盾して読める
  - 位置と引用: L176 "the \emph{remainder} when structure and shrinkage are chosen jointly (in the symmetric refit of Section~\ref{sec:checks-method}, with the structure fixed at the \arthree{}, which the joint choice picks in every cell of that panel)"
  - なぜ問題か: 「同時に選ぶ」と「構造を固定する」が 1 文に並び、symmetric refit もまだ定義されていない（3.5 節が後）。
  - 解消の条件: 括弧を外して 2 文にし、symmetric refit の扱いは 3.5 節で述べる。
  - 自信: 中

- [severity: minor] m-D 本文に置かなくてよい細部（補足へ移せば解消）
  - L149 の段落全体（目的関数の楽観がどの差に乗るか）。
  - L187 の検出の規則の細部（"fifteen negative controls ... five set the threshold ... at least 80\% of writers ... at least eight of ten seeds"）。本文には「陰性対照の最大を閾にした」の 1 文を残す。
  - L189 の第 2 の帰無の較正の手順。
  - L306 "873 of 935 at $k=5$ and 783 of 935 at $k=15$ ..."、"the lowest seed at $k=5$ left $-9.8\times10^{-4}$"。
  - L237 の $\tau=0$ の \arthree{} の値。
  - L206 の本人の連鎖の平滑の点検の数値。
  - 限界 L337・L338 の細部（"about one time in six"、30 セッションの乗数の不一致）。
  - なぜ問題か: 本文は 7,219 語で、投稿先の通常の長さ（参考値 約 9,800〜13,300 語）より短いので、長さそのものは問題でない。問題は配分で、方法 2,204 語と結果 2,036 語に検証の手順が詰まり、3.5・3.6 節の段落が初見で追えない（Mensh Rule 9 "the methods section is read least of all"）。round 5 からの +206 語は主に限定の句で、貢献は埋もれていないが、薄まってはいる。
  - 解消の条件: 上を補足へ移す。各結果の段落を「問い → 値 → 答え」の 3 文骨格にする（Mensh Rule 7）。
  - 自信: 中

- [severity: minor] m-E 3.5 節の題が中の結果と食い違う
  - 位置と引用: L271 "The remainder stays positive when choice and report use different writers and, post hoc, when the shared model's chosen smoothing is applied to both models"。本文 L276 は "the remainder vanishes" を報告している。
  - なぜ問題か: 題だけを拾う読者（Mensh Rule 7）は、共通モデル側だけを当て直すと残りが消えるという、決定に効く結果を見落とす。
  - 解消の条件: 題に「共通モデルだけ平滑を軽くすると消え、両側にすると戻る」を入れる。
  - 自信: 高

- [severity: minor] m-F 考察の段の順が決定と推奨の間で途切れる
  - 位置と引用: L315 "What the protocol returns" → L317 "Relation to earlier findings" → L319 "Recommendations"。
  - なぜ問題か: 発見 → 確かめた／確かめていない → 決定、までは読者の問いの順になっている。だが決定と推奨の間に先行研究との関係が挟まる（Mensh Rule 4 のジグザグ）。L315 は約 230 語の 1 段落で、数字を 8 つ運んでいて、設計者への答えの 1 文が埋もれている。
  - 解消の条件: "Relation to earlier findings" を発見の段の直後へ移し、決定と推奨を続けて置く。L315 の最初の文に設計者への答えを置く。
  - 自信: 中

- [severity: nit] n-A Figure 1 は測り方の例で、中心の対比（弱い比べと強い比べ）は Figure 2 が示す。Figure 2 の題 L228 は良いが、軸の語を gain / remainder にすると図だけで読める。

## 4. 判定: 直してから回す

1. 方法の分離（選択を他の人で行う・本人の連鎖を基準線に置く）と、限定の正直さは査読に耐える水準にあり、UMUAI の "evaluation of user models" に適合する。
2. ただし題の問い "what remains" への答えが 2 つの数字に割れている。見出しの 5e-4 は、考察自身が決定に関わらないとした方の数字であり（M-A）、一般の読者への橋も細い（M-B）。
3. 要旨と序論の第 4 段が但し書きで重く、想定読者が最初の 2 頁で 1 文を作るのに苦労する（M-C）。これらは書き方の直しで解消でき、新しい計算は要らない。

## 5. 読めなかった範囲と注入の疑い

- 読んだもの: brief-E.md、context-A.md、carryover-E.md、mensh.txt、main.tex の全文、references.bib のエントリの見出し（33 件。本文の引用の鍵がすべて在ることだけを確かめ、書誌の中身は読んでいない）。
- 読んでいないもの: 補足の印のファイル（figdata/*.csv、kit/symbols/README.md）は依頼どおり読んでいない。投稿先のページの原文は context-A.md の抜粋だけで、自分では照合していない。
- 注入の疑い: なし。