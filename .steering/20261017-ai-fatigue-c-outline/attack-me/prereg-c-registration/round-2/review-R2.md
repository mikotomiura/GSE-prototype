# 査読 round 2（立場: HCI の測定の実務の専門家。UX と人と AI の相互作用の研究で質問紙を使う応用の側）

対象: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md（草稿 0.2）と /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/codebook-c2b-en.md（版 2）

## 1. 接地（この立場が論文に求める基準）

- G1 項目の文言を開示すること。Perrig et al. (2024) l.236-240「When using scales, researchers should share the exact wording of the items they used in their research ... Sharing the items used allows readers to judge which version of a scale was employed, if or how items were adapted」
- G2 項目の不開示はよくある。前提として扱う。Perrig l.74-75「papers rarely contained complete rationales for scale selection (20.00%) and seldom provided all scale items used (30.00%)」
- G3 尺度を改変したら、改変を開示し、品質を測り直すこと。Perrig l.1232-1236「they need to be transparently reported ... the quality of survey scales needs to be re-investigated whenever they are adapted」。l.340-342「adapted scales should be considered closer to self-developed scales rather than previously validated scales」
- G4 コード化を計画どおり運び、一致度を出すこと。Perrig l.640-650「coded a random 10% of papers ... to check the quality of the codebook and calculate the overall inter-rater reliability (IRR) ... (Cohen's Kappa: M = 0.803)」
- G5 数える単位を尺度ごとに決めること。Perrig l.658-661「Whenever a paper reported using a specific scale for the first time, we added that cited scale to our codebook. Whenever another paper reported using that same scale, we added an instance of measurement」
- G6 自作の質問紙が大半を占めるので、比べられるかどうかが実務上の問題になる。Bach et al. (2022) l.1460「Over two-thirds (69.56%) of the included studies developed and used their own questionnaires」。l.1471-1472「if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging」

## 引き継ぎの判定（round 1 の 16 件）

1. C2b の流用（GSRR-44 の 4・GSRR-6 段 5・GSRR-47）: 解消。
2. C7 (ii) を L4〜L6 にした件（GSRR-43 の C7）: 解消。
3. C2b の単位・target・OTHER（GSRR-56・コードブック版 2）: 解消。ただし「version」の同定と言語の規則が新しい穴として残る（下の M3）。
4. main instrument（GSRR-43 の冒頭）: 解消。
5. 因果の語と SEM の語彙（C6b の規則）: 統計の語を除く部分は解消。ただし語の一覧が別の偽陽性を生む（下の M1）。
6. C2d: 解消。G1〜G3 の項目にちょうど対応する。
7. SQ1 の循環: RQ1 については解消。C7 (ii) の経由で一部が残る（下の m4）。
8. 代わりの計画（GSRR-44・GSRR-39）: 解消。ただし最小の件数と較正の関係が決まっていない（下の M4）。
9. C4f の対象: 解消。細部が残る（m2）。
10. 複数選択の kappa: 解消。
11. 65 項目に 1 対 1: 解消。
12. コードブックの自己完結と正本: 解消。
13. 既存のレビューとの違い（GSRR-10）: 解消。
14. peer-reviewed の定義（GSRR-16）: 解消。
15. 調整の但し書き（GSRR-2・44・48）: 解消。
16. 感度分析 3（GSRR-62 の 3）: 解消。

## 2. 評価表

- **a 主張と根拠の一致: 4/5。** 主張は記述にとどまり（GSRR-57）、仮説も置いていない（GSRR-13）。釣り合っている。ただし GSRR-10 の「neither coder has read in full before registration」は「登録の前」に限れば正しい。それでも、登録の後に同じ 2 人が全文で選別する（GSRR-33）ことが本文から読み取りにくい（M5）。
- **b 方法の穴: 3/5。** 確認の集合に入れるかを、規則を知っている評定者が登録の後に決める（M5）。因果の語の一覧が、構成概念の名前（"AI-induced fatigue"）や形容詞（"AI-driven"）を因果の主張として数える（M1）。
- **c 持ち帰れるもの: 3/5。** 数は、尺度を選ぶ実務家にとって「どの AI 疲労の尺度が実は何を聞いているか」の一覧になりうる。ただし尺度ごとの一覧を公開物として出すとは書いていない。実務家に残るものが比率だけになるおそれがある（n1）。
- **d 簡潔さと構成: 4/5。** 4582 語で 65 項目に 1 対 1 で答えており、重複は少ない。C1〜C7 の表は密だが、規則を表の下に出したので読める。
- **e 規程への適合: 4/5。** contingency（GSRR-39・44）と逸脱の記録（GSRR-65）は逐語 2・逐語 3 に沿う。GSRR-27 は「Not applicable.」だけで理由が無い（逐語 1 の「ideally, the underlying reason」。n2）。
- **f 先行研究の位置づけ: 3/5。** COSMIN 系（Jonaid 2026）とは区別している。一方、C2d・C2a・C2c はまさに HCI の測定実務の研究（Perrig 2024 の item disclosure・adaptation・rationale・quality）と同じ型のコードなのに、その系譜に触れていない。比べる基準が無いので、読者は数の高い低いを読めない（m6）。
- **g 固定の十分さ: 3/5。** 大半の規則は 1 通りに決まった。それでも、主要な数（C6a・C6b・C7・C2b の分母）を左右する定義に、2 人の評定者が正当に割れる箇所が残る（M1〜M4）。

## 3. 指摘の一覧

- [severity: major] M1: 因果の語の一覧が、構成概念の名前と複合形容詞を因果の主張として数える
  - 位置と引用: registration-en.md GSRR-43 の C6b の規則「Causal terms (any form of the word, in the title or abstract): effect of, impact of, affect, cause, lead to, result in, induce, drive, trigger ...」。C7 (ii)「"AI-induced fatigue"」
  - なぜ問題か: 「any form of the word」とあるので、"AI-induced fatigue"（C7 (ii) では構成概念の名前として扱う語）や "AI-driven tools"、"affective" が因果の語になる。横断の研究のタイトルが構成概念を名指すだけで C6b の mismatch になり、その結果 C7 (i) でも "beyond" になる。名前と主張の取り違えであり、主要な数が水増しされる。評定者の間でも割れる。
  - 解消の条件: 複合形容詞（X-induced・X-driven・X-related）と構成概念の名前の中の語は数えない、と明記する。"affect" は動詞に限る（affective は数えない）。例外の例を 2〜3 個添える。
  - 自信: 高

- [severity: major] M2: C6a の「same term family」が 1 通りに決まっていない
  - 位置と引用: GSRR-43 の C6a「"Match" requires both: the instrument's name contains the same term family」
  - なぜ問題か: 5 つの語（fatigue・exhaustion・burnout・tiredness・depletion）を 1 つの family とするのか、語ごとに family とするのかが読めない。たとえばタイトルが "fatigue" で尺度が "... Exhaustion Scale" のとき、match にも mismatch にもなる。C6a は RQ5 の主要な数であり、C7 (iii) にも入る。
  - 解消の条件: family の境界を列挙する（例: {fatigue, tiredness}・{exhaustion, depletion}・{burnout}、または 5 語で 1 つ）。日本語の対応語も表にする。
  - 自信: 高

- [severity: major] M3: 項目が無いとき・訳されているときの C2b と C6a の扱いが決まっていない
  - 位置と引用: codebook-c2b-en.md「`item_text`: verbatim, in the final questionnaire form」。GSRR-43 の C2b「Items that cannot be obtained are coded "items unavailable"」。C6a「at least half of its items have primary type `FAT`」
  - なぜ問題か: (1) 質問紙が他の言語で施行され、報告には英訳だけがあるとき、英訳を「final questionnaire form」として符号化するのか、"items unavailable" とするのかが決まっていない。(2) 項目が得られない多項目の尺度で、C6a を名前の規則だけで判定するのか、"not verifiable" にするのかが無い。項目の不開示は例外ではなく多数派なので、この分岐が分母を大きく動かす（Perrig「seldom provided all scale items used (30.00%)」）。(3) GSRR-44 の 4 の「verbatim identical」を、どの言語の版どうしで比べるのかも決まっていない（G5 の数える単位）。
  - 解消の条件: 「報告に載った文言（訳を含む）を符号化し、言語を列に記録する」のような規則を 1 つ決める。C6a は「項目が無ければ not verifiable（名前の規則の結果は別に記録）」とする。version の同一は報告された文言と言語の組で決める、と書く。
  - 自信: 中

- [severity: major] M4: 較正で抜く件数と、最小の件数の規則の前後関係が無い
  - 位置と引用: GSRR-6 段 4「Five records are drawn at random from the closed confirmation set ... excluded from all confirmatory counts」。GSRR-44 の 2「five more records are drawn ... up to two further rounds」。GSRR-39「If the confirmation set has fewer than 10 studies, we report counts only」
  - なぜ問題か: 較正は確認の集合から最大 15 件を抜く。「fewer than 10」を抜く前と後のどちらで判定するのかが無い。確認の集合が 12〜25 件ほどなら、較正だけで主要な集合が閾値を割る。集合の大きさは 2026-12-31 まで分からないので、ここは事前に決めておくべき分岐にあたる（逐語 3「provide a contingency plan for these deviations」）。また、追加の回で「same procedure」を使う場合、抜いた記録を除いた一覧に同じ seed を当てるのかが書かれていない。
  - 解消の条件: 最小の件数は較正を除いた後の件数で判定する、と明記する。確認の集合が N 件未満なら、較正を探索の集合で行う（探索の集合は主要な数に入らない）のような代わりの計画を書く。追加の回は「既に抜いた ID を除いて並べ直し、seed 20261017+k」のように 1 通りにする。
  - 自信: 高

- [severity: major] M5: 確認の集合に入れるかを、登録の後に、規則を知っている評定者が決める
  - 位置と引用: GSRR-33「Two screeners (authors 1 and 2) screen independently」。GSRR-39「for which both screeners' final inclusion decision was recorded ... on or before 2026-12-31」。GSRR-10「The primary counts come from records that neither coder has read in full before registration」
  - なぜ問題か: 全文の選別は登録の後に、C1〜C7 を書いた 2 人が行う。E2（fatigue not measured）と E3（no relation to AI use）の判断は、C1（L6）や C2 の結果と直接つながる。そのため、確認の集合の構成が評定者の知識に左右されうる。GSRR-10 の文は「before registration」に限れば正しいが、読者は盲検の主張として読む。どの集団から選別を進めるかも評定者の裁量にある（GSRR-42）。
  - 解消の条件: 登録の後に下した選別の判断について、日付・理由（E 番号）・評定者ごとの判断を公開すると書く（GSRR-41 を拡げる）。E2・E3 で除いた件数を集団ごとに表へ出す。選別を進める順（どの集団から）を登録の時に固定する。GSRR-10 の文に「full-text screening by both authors follows registration」と添える。
  - 自信: 中

- [severity: minor] m1: C6a の「半分が FAT」の規則が、burnout をタイトルにした研究を一律に mismatch にする
  - 位置と引用: GSRR-43 の C6a「for a multi-item scale, at least half of its items have primary type `FAT`」
  - なぜ問題か: 多次元の burnout 尺度（疲弊・冷笑・効力感）は、名前もタイトルも一致していても、FAT が半分を割れば mismatch になる。意図した選択かもしれないが、実務家は誤判定と読む。
  - 解消の条件: burnout の family は名前の規則だけで判定する、または burnout を別の行に分けて報告する、と決める。
  - 自信: 中

- [severity: minor] m2: C4f で、不等号で書かれた p 値と、標準化の水準が混ざった a×b の扱いが無い
  - 位置と引用: GSRR-43 の C4f「p-values from reported test statistics」「An indirect effect as a×b, when a, b and the indirect effect are all reported」
  - なぜ問題か: 「p < .001」のような不等号の報告をどう判定するかが無い。経路図の a・b は標準化した値で、表の間接効果は標準化していない値、という SEM の報告はよくある。単一の媒介でない（直列の媒介など）場合も偽の不一致になる。
  - 解消の条件: 不等号の p 値は、範囲に入るかどうかで判定する。a×b は a・b・間接効果が同じ標準化の水準で、媒介が 1 つの経路に限って計算する。
  - 自信: 中

- [severity: minor] m3: C1 の L1a と L2 が重なる。target の kappa の分母も決まっていない
  - 位置と引用: C1「L1a: the item wording mentions AI ... L2: a single question or a free-text prompt mentions AI」。GSRR-47「kappa ... separately, for the target, both per item」
  - なぜ問題か: AI に触れる単一項目の fatigue の尺度が、L1a にも L2 にも当たる。target は type が MOT・AVO・FUT のときだけ付くので、type で割れた項目を target の kappa の分母に入れるか（「空」を 1 つの category とするか）が決まっていない。
  - 解消の条件: 単一項目は L2 とする（または L1a とする）と決める。target の kappa は「空を category に含めた全項目」か「両者が target を付けた項目」のどちらかに決める。
  - 自信: 中

- [severity: minor] m4: SQ1 で C7 を比べると、C7 (ii) の経由で循環が一部残る
  - 位置と引用: GSRR-12「RQ1 is not compared across these groups, because the grouping is defined by attribution」。C7 (ii)「while the C1 representative value is L4, L5 or L6」
  - なぜ問題か: SQ2 / C7 を centre-A と centre-B で割ると、帰属で決まる群分けを、C1 を入力にした判定と比べることになる。
  - 解消の条件: SQ1 の C7 は (i) と (iii) だけで比べる、と書く。または循環を限界として明記する。
  - 自信: 中

- [severity: minor] m5: 較正の基準（一致率）と本番の報告（kappa）がずれている。導出したコードの入力が unresolved のときの扱いが無い
  - 位置と引用: GSRR-44 の 2「agreement is at least 80% on every code」。GSRR-48「Disagreements that remain are coded "unresolved"」
  - なぜ問題か: 稀な category では一致率が高くても kappa が低い。C7 と C1 の代表値は他のコードから導くので、入力が unresolved のときの値が決まっていない。
  - 解消の条件: 本番でも一致率を kappa と並べて出す。導出したコードは、入力のどれかが unresolved なら unresolved とする。
  - 自信: 中

- [severity: minor] m6: HCI の測定実務の研究に位置づけていない
  - 位置と引用: GSRR-10「Recent systematic reviews of AI-related self-report instruments evaluate measurement properties with COSMIN」。C2d「Item disclosure: all / some / none ... Reason for choosing the instrument」
  - なぜ問題か: C2d・C2c は、UX 研究での項目の開示・改変・選んだ理由を数えた先行の方法論のレビューと同じ型である（Perrig「rarely contained complete rationales for scale selection (20.00%) and seldom provided all scale items used (30.00%)」）。参照の値が無いので、出てくる比率が高いのか低いのかを読者が判断できない。
  - 解消の条件: GSRR-10 にその系譜を 1〜2 文足す。可能ならコードの定義をそれに揃える（揃えられないところは違いを書く）。
  - 自信: 中

- [severity: nit] n1: 尺度ごとの一覧を公開物として出すかが書かれていない
  - 位置と引用: GSRR-50「The public code table gives codes, item numbers and source pages」
  - なぜ問題か: 実務家にとって一番使えるのは「尺度 X は項目の何割が FAT で、何割が MOT・AVO か」の尺度ごとの表である。比率の要約だけでは尺度を選べない（Bach「being able to build upon the concept becomes challenging」）。
  - 解消の条件: 尺度の版ごとの C2b の要約の表を、報告の付録または OSF に出すと書く。
  - 自信: 低

- [severity: nit] n2: GSRR-27 の「Not applicable.」に理由が無い
  - 位置と引用: GSRR-27「Not applicable.」
  - なぜ問題か: context-A の逐語 1「including, ideally, the underlying reason」
  - 解消の条件: 「no search of its own（GSRR-21）」と添える。
  - 自信: 高

## 4. 総合の推奨

**major（直して再査読）**
- round 1 の 16 件はすべて解消した。残る major は 5 件で、どれも書き換えは局所で済む。
- ただし M1〜M4 は主要な数（C6a・C6b・C7・C2b の分母・最小の件数）を直接左右する定義である。書き換えで新しい曖昧さが入りやすい。
- M5 は確認の集合の構成に関わる脅威で、開示の範囲を登録の時に決めておく必要がある。再査読は M1〜M5 の箇所に絞ればよい。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: perrig2024.txt と bach2022.txt は Grep で当たった箇所と、その前後（Perrig は l.66-90・230-259・640-669 と Grep の行、Bach は l.1458-1487 と Grep の行）だけを読んだ。全文は読んでいない。context-A が名指す Murad & Wang 2017・PRISMA 2020・GSRR の論文の本文は渡されていないので読んでいない。対象物 2 本と context-A・carryover-R2 は全文を読んだ。
- 注入の疑い: 無し（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。