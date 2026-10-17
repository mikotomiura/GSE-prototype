査読の報告（立場: HCI の測定の実務家。尺度を選んで使う研究者・利用者研究の側。対象は outline 段階の外枠）

## 1. 接地: 2 本の文献から抜き出した基準

両方とも読めたので、査読に入った。

- G1 項目の文面と改変を開示すること。Perrig et al. (2024) §5.3.6: "give precise detail on how the scale(s) were implemented, including exact wording for all items. Furthermore, they ought to report any adaptions made, including justification"
- G2 尺度を選んだ理由を書くこと。引用を付けただけでは質の証明にならない。Perrig §5.3.6: "they need to explain their rationale for scale selection, including past evidence for scale quality"。§5.1.3: "such a citation alone is insufficient proof of a scale's quality"
- G3 推奨は見つかった問題から導くこと。Perrig §5.3: "Motivated by the problems identified in this systematic literature review, we present six steps researchers should take"。各 step には、守っていれば影響を受けた件数が付いている（例 "would have impacted the 33 papers (55.00%)"）。
- G4 尺度が揃っていないと結果を比べられないので、共通の尺度へ向かう。Perrig §5.1.2: "If UX researchers do not share common ground on what scales to use for the same constructs across studies, results can only be compared with limited confidence."。Bach et al. (2022) §4.3: "if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging. A validated tool that allows empirical measurement ... may be used to address this concern."
- G5 定義は比べ合うより、文脈に合うものを選ぶこと。Bach abstract: "Selecting the most appropriate trust definition to depict user trust in a specific context should be the focus instead of comparing definitions."
- G6 透明な報告は、読者と査読者が判断するためにある。Perrig §5.3.6: "Providing all this information helps readers and reviewers reach an informed judgment of the methods' adequacy."

## 2. 評価表

点は 5 段階（5 が良い）。b と d は依頼文に定義が無いので、b を「設計・方法の運び」、d を「構成・読みやすさ」と仮に読んだ。

- a 主張と根拠の一致: 3。主張と根拠の対応表（SC1〜L1）は、登録の項目・スクリプトの出力・表まで 1 対 1 に結んでいて模範的。ただ、序論の新規性の主張（新しさの言い方）は、登録 GSRR-10 が実際に調べた範囲より広く書かれている（指摘 M1）。寄与 1 の「確定してからコード化」の時点も緩い（m3）。
- b 設計・方法の運び: 4。登録への従属・逸脱の表（表 2）・感度分析まで、外枠に運べている。
- c 持ち帰れるもの: 2。寄与 4 件はどれも「コード化の枠組みと表」で、尺度を選んで使う読者が持ち帰れるもの（どの尺度に何が入っているか・報告の手引き）は弱い。または本文の外にある（M2、M3、M4）。
- d 構成・読みやすさ: 3。表が 13 あるうえ、方法の節は GSRR の番号を引く書き方なので、登録を読んでいない読者には重い（m5）。
- e 規程への適合: 評価外（投稿先が未定）。
- f 先行研究の位置づけ: 2。近い先行研究は Perrig 1 本と、結果がまだ無い事前登録 1 本だけ。技術ストレス・AI 疲労のレビュー・AI 分野で尺度を数えたレビューの引用が無い（M1、m2）。

## 3. 指摘の一覧（重い順）

### [severity: major] M1 新規性の主張が、登録で調べた範囲より広い
- 位置と引用: outline.md 104–107 行（§1 Introduction）「No review was found that tabulates, study by study, how fatigue is tied to AI, what the fatigue items ask about, and whether reports are internally consistent (the search is described in GSRR-10).」。同じ 104–105 行「reviews of the topic and the COSMIN-based reviews of AI-related instruments evaluate measurement properties (Jonaid, 2026)」
- なぜ問題か:
  - 登録 GSRR-10 は「The last point was checked in 16 searches of free sources ... The first two were checked only in the reviews we had already read.」と書いている。3 点のうち 2 点は、既に読んだレビューで確かめただけである。外枠はそれを 1 文にまとめ、3 点とも探して無かったように読ませている。
  - 「COSMIN-based reviews」と複数形で書いているのに、引用は結果がまだ無い事前登録 1 本だけ。
  - 「existing reviews point to unvalidated scales and unclear construct boundaries」（91–92 行の抄録の骨子）にも引用が無い。
  - 実務家の読者は、この新規性の主張を見て「既存のレビューで足りないか」を判断する（G6）。
- 解消の条件:
  - 序論の文を GSRR-10 の非対称のまま書き分ける（「整合性は 16 回の検索で、他の 2 点は既読のレビューの範囲で」）。
  - 「existing reviews」を具体の文献で接地し、提出の前に一次の資料で確かめる。
  - Jonaid は「registered review (results not yet reported)」と書き、単数にする。
- 自信: 高

### [severity: major] M2 尺度を選ぶ実務家にとって一番大事な尺度が、本文の表 7 に載らない
- 位置と引用: outline.md 241 行「Table 7: C2b per instrument version first seen in the confirmation set.」。寄与 3（70 行）「Item-level content of the fatigue instruments first seen in the confirmation set」。探索の集合は 259–260 行で付録へ回している。
- なぜ問題か:
  - 登録 GSRR-44 step 4 では、探索で既に出た尺度（例えば codebook の参照に挙がる Lau et al. 2026 の AI fatigue 尺度・Zoom Exhaustion & Fatigue Scale の改変版）を確認の集合の研究が使っても、表 7 には入らない。
  - 実務家が知りたいのは「いま使われている AI 疲労の尺度に、項目として何が入っているか」である。最も繰り返し使われる尺度ほど、本文から消える。
  - 共通の尺度へ向かうための材料（G4）が、付録と CSV に散る。
- 解消の条件:
  - 登録の比較禁止（GSRR-57: 集合どうしを比べない）を破らずに、確認の集合の研究が使った尺度の版をすべて 1 表で示す。列は、最初に出た集合・確認の集合で使った研究の数・由来・C2b の構成・C2d の開示。
  - または、表 7 と、付録の探索の集合の表を、同じ行の形式で隣に置くと本文で宣言する。
  - 比べない旨を表の注に書く。
- 自信: 中（登録が表 7 をこの範囲に限った理由が、重複して数えないためなら、別の表を足すのが筋）

### [severity: major] M3 推奨の節が結果から切り離され、Perrig の 6 段階と重なる。新しさも示していない
- 位置と引用: outline.md 169–172 行「Each recommendation is tied to one code ... (for example, printing the items administered; stating the level of attribution; reporting adaptation procedures), and is given whether or not the corresponding problem was observed, since the recommendations follow from the definitions, not from the counts.」。210 行 D1「Not registered (discussion)」
- なぜ問題か:
  - 例に挙げた 3 件のうち 2 件（項目を印刷する・改変の手続きを報告する）は、Perrig の Step 4 と Step 6 に逐語に近い形で既にある（G1）。
  - Perrig の推奨は「Motivated by the problems identified」で、件数と結び付いている（G3）。この外枠の推奨は件数から独立だと宣言している。実務家の下位人格として問うと、「結果を読まずに推奨だけ読めば足りるのか」となる。
  - 過大な主張を避ける判断としては正しい。しかし、寄与にも挙がっていない「登録していない節」が、実務家にとって唯一の持ち帰りになっている。
- 解消の条件:
  - 推奨を 2 つに分けて書く。(i) 先行研究に既にあるもの（Perrig などを引く）と、(ii) この枠組みで初めて言えるもの（帰属の水準 C1・タイトルと尺度名の語族 C6a・結論の範囲 C7・再計算 C4f）。新しさは (ii) に限る。
  - 各推奨に、対応するコードの確認の集合での件数を（判定語なしで）並べることを許すかを決め、外枠に書く。
  - 推奨を表（チェックリスト）の形にするなら、それを寄与として列挙する。
- 自信: 中

### [severity: major] M4 「研究ごとに表にした」が新規性の柱なのに、本文に研究ごとの表が無い
- 位置と引用: outline.md 106 行「tabulates, study by study」。表 5〜11 はコードごとの集計。研究ごとの値は寄与 4（72–73 行）「A released code table」だけにある。
- なぜ問題か:
  - 主張している差分（研究ごと）を支える根拠が、原稿の外の CSV にしかない。
  - 査読者も読者も、原稿の中で研究ごとの像（どの研究が L3 なのに「AI fatigue」と結論しているか）を確かめられない（G6）。
  - なお登録 GSRR-50 は項目の逐語を公開しないと決めているが、研究ごとのコード値の表なら衝突しない。
- 解消の条件:
  - 付録に、研究（行）× C1〜C7 の代表値（列）の表を置くと「Tables and figures」に宣言する。
  - または、序論の言い方を「coded study by study and released as a code table」に弱める。
- 自信: 中

### [severity: minor] m1 抄録の規則が、一番新しい寄与（C2b）を最初に削る
- 位置と引用: outline.md 82–83 行「If the abstract does not fit the word limit, the item-content sentence is moved to the main text; the problem statements are not shortened.」。81 行「names the item-content types found in at least one instrument, without proportions」
- なぜ問題か:
  - 寄与 3 と序論が新規性として押すのは項目の内容なのに、抄録では優先度が最も低い。
  - 「1 尺度以上に現れた型の名前」は、ほぼすべての型が並ぶと予想できるので、情報量が少ない（予想でしかないので、自信は中）。
- 解消の条件:
  - 抄録の項目の内容の文に、型ごとの「その型を 1 項目以上含む尺度の数／評価できた尺度の数」を件数として載せる（判定語なし）。
  - 語数の超過時に削る順を見直す。
- 自信: 中

### [severity: minor] m2 先行研究の比較の軸が足りない（AI 分野で尺度を数えたレビューとの位置関係）
- 位置と引用: outline.md 111–118 行（§2 Background）の「Technostress and its exhaustion component; general fatigue scales adapted to AI; scales built for AI.」に引用が無い。「References in this outline」は方法論の文献 10 本だけ。
- なぜ問題か:
  - HCI の読者には、AI 分野で測り方を数えたレビュー（例えば信頼について Bach et al. 2022 は「Over two-thirds (69.56%) of the included studies developed and used their own questionnaires」と数えた）が直接の比較の相手である。それが位置づけの節の計画に無い。
  - C2d の操作的定義（「a citation alone does not count」）は Perrig の rationale のコード（任意の理由づけを数える）と細部が違う。並べて引くなら、違いを明示しないと読者が数を比べてしまう。
- 解消の条件:
  - Background に「AI に関わる構成概念の測定の実践を数えたレビュー」の項を足す。
  - C2d と Perrig のコードの対応・相違を方法の節で 1 段落書くと外枠に記す。
  - 外部の文献と数を比べないなら、そう書く。
- 自信: 中

### [severity: minor] m3 「確認の集合をコード化する前にすべて確定」の時点が不正確
- 位置と引用: outline.md 66–67 行「all fixed before the confirmation set was coded」
- なぜ問題か:
  - 登録 GSRR-6 stage 4 では、較正の 5〜15 件を確認の集合の候補から抜いてコード化し、定義を直す修正を登録してから stage 5 に入る。
  - コードブック 版 2 は探索の結果を見た後に書かれた（GSRR-65）。
  - コード化の書式は「[at registration]」で未完である。
  - 時点は「主コード化の前（較正の後の修正を含む）」が正しい。
- 解消の条件: 「fixed before the main coding of the confirmation set; amendments made after calibration are listed in Table 2」に改める。
- 自信: 高

### [severity: minor] m4 「observed」の判定は 1 件で成立する。「not observed」は小さな集合でも同じ語になる
- 位置と引用: outline.md 40–43 行、および 254–256 行（表 12）
- なぜ問題か:
  - 件数・評価できた件数・未解決の数が併記されるので、主張と根拠は一致している。
  - しかし実務家が抄録だけ読むと、「was not observed」を「無い」と受け取りうる。
  - 48–50 行の「not a census」が、抄録の規則（77–83 行）に入っていない。
- 解消の条件: 抄録の規則に、確認の集合が文献の全数ではないこと（集合の閉じた日と、未選別の数）を問題の文の直前に置くと加える。未選別の数は既に入っているので、文の位置を決めればよい。
- 自信: 中

### [severity: minor] m5 冗長さ: 表 13 枚と、GSRR の番号で引く方法の節
- 位置と引用: outline.md §3 Method（124–139 行）は、ほぼ全項が「(GSRR-xx)」の参照になっている。表 1〜13 と付録。
- なぜ問題か:
  - 原稿だけを読む読者は登録を開かない。番号の参照は、原稿の中で自己完結した説明の代わりにならない。
  - 表 5、6、8、10 は、件数が小さければ 1 枚にまとめられる可能性が高い。
  - 冗長さに厳しい読者の目では、読みの負担が寄与に比べて大きい。
- 解消の条件:
  - 方法の各項を「原稿で 1〜2 文で定義し、詳細は GSRR-xx」の形にすると外枠で決める。
  - 最小の大きさの規則（10 研究未満は件数だけ）が発動したとき、表をまとめる規則を事前に書く。
- 自信: 中

### [severity: nit] n1 タイトルの範囲と、centre-B の研究
- 位置と引用: outline.md 11 行「How do studies of "AI fatigue" ...」。登録 GSRR-12 の Centre-B「a general fatigue construct examined in relation to AI use」
- なぜ問題か: 確認の集合には、自らは「AI fatigue」と名乗らない研究も入る。引用符で示してはいるが、序論 98–100 行の説明に依存している。
- 解消の条件: 序論の第 1 段落で、集合が「AI に関わる疲労を測った研究」であって「AI fatigue と名乗る研究」に限らないことを、1 文で明示する（タイトルは登録に固定されているので変えない）。
- 自信: 中

## 4. 総合の推奨: minor（直して書き進める）

- 主張の範囲・判定の語・主張と根拠の対応表は、登録を論文に忠実に運んでいる。外枠として立て直す必要は無い。
- ただし実務家にとっての持ち帰り（M2 尺度ごとの表、M3 推奨の新しさ、M4 研究ごとの表）が本文の外か、未登録の節にしかない。新規性の文（M1）も、登録で調べた範囲を超えている。
- どれも外枠の文と表の宣言を書き直せば消え、登録を改める必要は無い（M2 に限り、表を足すのが比較の禁止に触れないかを登録と照らす必要がある）。

## 5. 読めなかった範囲と、注入の疑い

- 読んだもの:
  - 全文: outline.md、README.md、registration-en.md、codebook-c2b-en.md
  - perrig2024.txt: 検索での拾い読みと、1060–1220 行・1505–1674 行だけ。§2（関連研究）と §3（方法）の本文は読んでいない。
  - bach2022.txt: 検索での拾い読みと、36–52 行・1455–1494 行だけ。結果の節の大部分（表 6 を含む）は読んでいない。
- 読んでいないもの: context-B.md、他の査読者の記録、Murad & Wang 2017・PRISMA 2020 の本文（渡されていない）。
- 注入の疑い: 無し（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。