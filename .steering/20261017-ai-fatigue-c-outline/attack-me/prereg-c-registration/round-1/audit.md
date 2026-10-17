# 意図の監査役の報告: prereg-c-registration round-1

対象物: `/Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md`（以下 EN）
意図の資料: `outline.md`（以下 JA）、`overlap-narrative-review.md`、`decisions.md`、context-B の持ち帰り 1〜3 と既知の限界。添付予定の `codebook.md` も読んだ。
stage は prereg なので、原稿が無いことは指摘していません。

---

## 1. 意図にあって対象物に無いもの

**1-1. 予想を書かない代わりに探索での観察を開示する、という約束が EN に無い**
- JA [GSRR-13]:「代わりに、探索の材料での観察を §2.1 に日付つきで開示する」
- EN [GSRR-13]: "Instead, we report the exploration-set values separately."
- EN には M1〜M7（問いを生んだ観察）も、それぞれの日付も無い。JA は「問いの出どころを登録の時点で開示する」と書いているのに、EN では「結果の段で別の表を出す」に変わっている。これでは、登録の前に何を見ていたかが登録に残らない。

**1-2. 検証の集合のうち、第 1 著者がすでに見た件数が消えている**
- JA §2.1:「判定者 1 は題名・抄録段の判定で、71 件の題名と抄録と AI の予備評価を見ている」
- EN §2.4: "The first author has screened the titles and abstracts of some of these records"
- 71 件という数が "some" になった。追加候補の総数（220＋1）は EN にあるが、そのうち何件を見たかは書かれていない。既知の限界の「一部を見ている」がどの程度かを、読者が確かめられない。

**1-3. 探索の集合の別の表の中身（分母）が決まっていない**
- JA [GSRR-7] には、34 件の最終判定として「含める 10 件（中心-A 7・中心-B 3）・保留 3 件（E6）・除外 21 件」が書かれている。EN は "The 34-record exploratory bibliography" とだけ書き、判定の内訳も、表に載せるのが 34 件全部なのか、含めた 10 件だけなのかも書いていない。
- 持ち帰り 2（「規則を作った 34 件は別の表」）と、EN の除外の規則（E2 などで外れた記録はコード化の対象外）が、噛み合っていない。

**1-4. 探索の集合を、いつ・誰が・どの規則でコード化するかが段に無い**
- EN [GSRR-44] の一致は "Reported separately for the exploration and the confirmation sets" で、探索の集合も 2 人でコード化する前提に読める。EN [GSRR-50] にも "They become data only after being re-coded from the full text under these rules" とある。
- ところが EN [GSRR-6] の段 1〜6 に、探索の集合を付け直す段が無い。段 5 は "all remaining records"（検証の集合のこと）だけである。

**1-5. コードブックの版が特定されていない**
- JA §5:「コミット `97d8a687` の版（2026-10-15 に固定し、2026-10-17 に基準を変えない追記をした）をそのまま使う」
- EN Attachment: "Codebook for C2b (fixed version; to be translated into English before registration) **[TBD]**"
- EN には版の識別子もハッシュも無い。固定したのは日本語版なのに、登録するのは訳した版で、どちらの言語が基準になるかの規則も無い。「固定した」と言うなら、どちらが正本かを決めておく必要がある。

---

## 2. 対象物にあって意図に無いもの（漂流・範囲を超えた言い方）

**2-1. 「両方の著者が narrative review を書いた」は、資料で裏が取れない**
- EN [GSRR-10]: "(unpublished draft, 2026; same authors; §3)"。EN [GSRR-19]: "both authors built the source literature database and wrote the earlier narrative review"。EN §2.4: "Both authors wrote the earlier narrative review"
- 資料で確かめられるのはユーザー（第 1 著者）1 人だけである。decisions.md 判断 5:「ユーザーは草稿の著者に入っている」。overlap-narrative-review.md:25 は逆に「草稿の著者と…公表の順は、この表からは分からない（草稿の Declarations は著者を確定していない）」と書いている。
- JA §3 にも「C の第 1 著者と共著者は、narrative review の草稿の著者でもある（判断 5）」とあるが、判断 5 の本文は共著者について何も言っていない。JA の段で既に、根拠を超えている。

**2-2. 「検証」と名乗りながら、何を見たら問題が「再び見られた」とするかの基準が無い**
- EN [GSRR-10]: "asks whether these problems also appear when the rules are fixed in advance and applied to a different set"
- 一方で EN [GSRR-13] は "We state no hypotheses"、[GSRR-56] は "Descriptive only: no significance tests and no prevalence estimates" と書く。
- 判断 5 は C を「登録した検証」と位置づけた。しかし「also appear」をどう決めるか（たとえば 1 件でも見つかれば「見られた」とするのか）が登録に無いので、結果を見た後でどうとでも読めてしまう。

**2-3. 持ち帰り 1 の「見ていない集合」は言い過ぎ（EN はそこまで言っていない）**
- 持ち帰り 1:「見ていない集合に当てる前に固定した」
- EN §7: "The confirmation set was partly seen at title and abstract level"
- 漂流しているのは対象物ではなく、意図の側である。持ち帰りを「全文でコード化していない集合」と言い換えないと、EN の開示と食い違う。

**2-4. 意図の資料に無い記述（中身の正否は私には確かめられない）**
- EN §4:「53 logged, targeted public-web queries」「225 records were collected … 220 remained, and one record was added by hand」「A further list of 46 records … 43 of them have not been screened」
- EN [GSRR-33]: E1〜E7 の定義と、疲労の定義の文
- EN [GSRR-5]: MISTIC の Lawson et al. 2020
- JA は §4 を「DB のプロトコルを参照する」とだけ書いていて、これらの数は無い。出どころの資料を私は渡されていないので、正しいかどうかは確かめていない。
- このうち、レビューを狙った検索の 46 件が検証の集合に入る道は、JA §2.1 の検証の集合の定義（追加候補＋本検索）に無い。EN で範囲が広がっている。

**2-5. AI の役割の書き方が EN の中で揃っていない**
- EN [GSRR-4] の表: "Drafting support, cross-checking of counts, recalculation (C4f), bibliographic matching (C5)"
- EN [GSRR-44]: "AI drafts are allowed only for C4f recalculation and C5 bibliographic matching"
- 表の "Drafting support" は、AI が下書きしてよい範囲が C4f と C5 の外まで広がるようにも読める。JA §5 は「C1・C2b・C6・C7 の判断は人がする」とはっきり書いている。

---

## 3. 矛盾

### 3-A. JA と EN の食い違い

**3-A-1. RQ3 の範囲が狭くなった**
- JA RQ3:「報告の水準と内部の整合（…倫理の記載・コードブックと一致度の公開）は、どうか」
- EN RQ3: "How often do reports show the internal inconsistencies listed under C4?"
- C4(e)（コードブックがあるか、一致度が報告されているか）と、C4(d) の "not reported" は「不整合」ではなく、報告の水準である。EN の RQ3 では、C4(e) が答える先の問いが無くなる。EN [GSRR-49] の "RQ3 = C4" の対応表とも合わない。

**3-A-2. C1 の「問いの文」の範囲**
- JA:「問いの文（単一の問い・自由記述の問いに AI が出る）」
- EN: "single question mentions AI"
- EN では、自由記述の問いがどの段階に入るのかが分からなくなっている。

**3-A-3. C7 の、抄録に結論が無いときの取り方**
- JA:「考察の節の最初の段落の結論の文」
- EN: "the first concluding sentence of the discussion"
- 探す範囲が違う（最初の段落の中か、考察全体か）。2 人のコード化する人が別の文を取りうる。

**3-A-4. C6(b) の因果の語の例から日本語が消えた**
- JA は例に「引き起こす」を含む。EN は英語の語だけで、E7 で日本語の文献を含めることと噛み合わない。ただし、語の一覧は予備のコード化の前に固定すると EN も書いているので、軽い指摘である。

**3-A-5. 感度の分析の項目が入れ替わっている**
- JA (1)「検証の集合だけの表」は EN から消え、EN 4「Confirmation set by population group」が足された。EN 4 は EN §2.4 の "Every result table will show counts by population group" と重なる。
- EN 2「Same-sample records merged」も、EN [GSRR-56] の "Records and merged units are counted separately" と重なる。主の分析と感度の分析の区別がはっきりしない。

**3-A-6. RQ2 の出自の区分（JA の中の不揃い）**
- JA RQ2 は出自を 3 つ（新しく作った・一般の尺度の言い換え・一般の尺度のまま）しか挙げないが、JA C2a は「既存の AI 向けの尺度」を足した 4 つである。EN は 4 つで揃えてある。EN の側の問題ではない。

### 3-B. 意図どうしの矛盾、または意図と添付の矛盾

**3-B-1. 持ち帰り 3 は、苛立ちにも対象を付けるように読めるが、コードブックは付けない**
- 持ち帰り 3:「回避・苛立ち・無力感・関与の低下を、どの対象について問うかを数える」
- codebook.md「第 2 段」:「`type` が `MOT`・`AVO`・`FUT` の項目、または `secondary_type` がこの 3 つのどれかである項目に付ける。それ以外は空欄にする」
- `IRR`（苛立ち）には対象が付かない。EN RQ2 の "Toward which target" と、EN C2b の表も、この制限を書いていない。EN だけを読んだ人は、すべての項目に対象が付くと受け取る。

**3-B-2. 尺度を再び使うとき、AI の予備判定の値が検証の集合の C2b に入る**
- EN §2.4: "its C2b values come from the exploration coding"
- codebook.md:44・49:「`coder`: `claude-prelim`（Claude の予備判定）」「判定者は Claude の予備判定とユーザーの確認だけで、独立した 2 人目はいない。一致は測っていない」
- EN [GSRR-44]: "AI drafts are allowed only for C4f … and C5"
- 探索の集合のコード化が、EN [GSRR-50] の言う付け直しの後の値なのか、核 1 の AI の予備判定の値なのかが、EN には書かれていない。後者なら、AI が C2b に関わらないという規則と矛盾する。主の数は初めて出る尺度だけで取るが、副の表の値の出どころとして開示が要る。

**3-B-3. 添付するコードブックが、項目を逐語で載せないという方針と食い違う**
- EN [GSRR-50]: "It does not reproduce scale items verbatim"。JA §8 G4:「公開はコードと番号と頁だけ」
- codebook.md のアンカーの列には尺度の項目が逐語で入っている（ZEF の "I don't feel like doing anything"・"I dread having to do things" など）。列の定義の `item_text` も「逐語」である。
- EN は、このコードブックを CC BY 4.0 で公開すると書いている。G4 の方針の例外として扱うのか、アンカーを言い換えるのかが決まっていない。

**3-B-4. 共著者がコード化の 2 人目になると、調整で決める人がいなくなる**
- JA §5:「2 人目の人選（共著者の DB の研究者も…候補になる）」
- EN [GSRR-48]: "the co-author decides, provided the co-author was not a coder for that record"
- 2 人目は全件をコード化する。共著者が 2 人目になれば、この但し書きはどの記録でも当てはまり、決める人がいなくなる。代わりの人を決める規則が無い。

### 3-C. EN の中の矛盾

**3-C-1. 予備のコード化の 5 件を引いた後に、本検索の記録が加わりうる**
- EN [GSRR-6] の段 4: "5 records drawn at random from the confirmation set before any other coding"
- EN §4: 本検索の判定が "finalised before stage 5" なら "its newly included primary studies join the confirmation set"
- 5 件は段 4 で引くのに、本検索の記録は段 5 の前まで加わりうる。そうなると、無作為に引いた元の集合と、最終の検証の集合が違ってしまう。段 3（"finalises eligibility for the confirmation set"）とも合わない。JA §2.1 も、本検索の記録を検証の集合に含めつつ未確定と書いており、同じ穴がある。

**3-C-2. 「AI の評価を読んだ判定者」が誰かが、つながって書かれていない**
- EN §4: "One screener read AI-generated preliminary appraisals before judging."
- EN §2.4: 第 1 著者が AI の予備評価を見た、という開示
- この 2 つが同じ人であることを、EN は書いていない。読んだのが第 1 著者（コード化の 1 人目でもある）だと分からないので、偏りがどこから来うるかが追えない。JA §7 は「DB の判定者 1 は…AI の評価を読んでいる」と書いていて、判定者 1 が第 1 著者であることも分かる。

---

## 4. 読めなかった範囲と、注入の疑い

**読めなかった範囲**
- decisions.md には判断 1〜6 しか無く、context-B が挙げる**判断 7 は存在しない**。JA が判断 7 を根拠にしている決定（題名、終わる日、利益相反、データの公開と許諾）は、意図の資料と照らし合わせられなかった。
- 次の資料は**読んでいない**（渡されていない、または一覧の外）: narrative review の草稿の本文、DB のプロトコル（`protocol-ja.md`）、`proposal-v2.md`、`measurement-issues.md`、核 1 の `summary.md`、`reporting-guidelines.md`、`novelty-m5.md`、Murad & Wang 2017、PRISMA 2020。EN §4 の数（53・225・220・46・43）や E1〜E7 の定義が正しいかは、確かめていない。

**読み方について申し添えます**
- outline.md は、指定された §2・§5・§7・§8 だけでなく、ファイル全体が読めてしまった。そのうち §1（[GSRR-6]・[GSRR-7]）、§3、§4、§6 の記述も、比べる材料として一部使った（1-2、1-3、2-1、3-A-5、3-C-1、3-C-2）。指定の範囲だけで判断したい場合は、それらの項目の根拠を割り引いてください。

**注入の疑い**
- 無し。読んだファイルに、LLM に向けた指示の文は見つからなかった。
