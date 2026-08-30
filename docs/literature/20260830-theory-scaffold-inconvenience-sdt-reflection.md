# 研究コンセプトの理論骨格 — 不便益・SDT・反省の系譜を一次に降ろすサーヴェイ (2026-08-30)

## 動機（★ 書誌上の空白の実測。何が 0 件だったか）

★ 本ラウンドの前提を **本日 grep で実測した**。⚠️ **前提の 1 つは誤りだったので、まず訂正する。**

| 対象 | 想定 | ★ 実測（2026-08-30） | 判定 |
|---|---|---|---|
| 不便益 | [P6] 1 行のみ・URL なし・要旨 12 文字 | ✅ **その通り** | **確定** |
| Self-Determination Theory 本体 | 0 件 | ✅ **その通り**。`Deci` / `Ryan` / `self-determination` / `autonomy` で当たるのは [P99]（1999 メタ分析）と [P107]（Cameron の反論）のみで、**理論本体は 1 行も無い** | **確定** |
| Slow Technology | 0 件 | ❌ **誤り。[P104] が既に存在する**（★ `provisional`・一次全文未取得＝二次記述水準） | **訂正** |
| Reflective Design (Sengers et al.) | 0 件 | ✅ **その通り**。`Sengers` / `Boehner` / `reflective design` すべて 0 件 | **確定** |
| Informative Art | [P113] provisional・一次未取得 | ✅ その通り。★ **本ラウンドで一次 PDF 全文を取得したので閉じた**（DOI 確定・active へ昇格） | **解消** |
| Ludic Design (Gaver) | （想定なし） | ⚠️ **0 件**。[P45] Ambiguity as a resource はあるが ludic design は無い | **新規の空白** |
| GSE 側の「自律性」主張の所在 | 「繰り返し主張している」 | ⚠️★★ **`research-positioning.md` には GSE 自身の自律性主張が 1 つも無い**（★ 該当行はすべて他者研究の記述）。実際の主張は **`gse-v2-overview.md:44`「本人の自律性を損なわない範囲で」**と ADR-004 / `intervention-decision-engine.md` の「倫理・自律性ゲート」、そして ★★★ **`wbs-verification-halfyear.md:293` Gate H に `autonomy loss` が *アウトカム指標として* 置かれている** | **場所を特定** |

> ★★★ **最も重い実測**: GSE は **`autonomy loss` を検証ゲート（Gate H・拒否権付き）のアウトカムに据えている**のに、
> **理論本体も測定尺度も 1 つも登録されていなかった。**
> ⚠️★★★ **これは「書誌が薄い」ではなく「計器が無い」である。**

---

## 検証状態

| 項目 | 数 |
|---|---|
| 探索 angle | **7**（① 不便益・日本語一次 ② 不便益・英語/書籍 ③ SDT 理論本体 ④ SDT の HCI 運用化 ⑤ 反省/遅い技術の系譜 ⑥ 主張形式の先行と評価方法論 ⑦ **反証**＝実証の薄さ・評価不能性） |
| 取得ソース（書誌同定まで到達） | **26** |
| ★ **一次全文を自読** | **11**（⚠️ うち 3 本は日本語 PDF で **CJK CID 埋め込みのため部分欠落あり**。英語ラベル・数値・数式は取得できた） |
| abstract / 二次記述水準 | 8 |
| 書誌のみ（本文未取得） | 7 |
| claim | **14** |
| confirmed | **3-0 が 7 / 2-1 が 3** |
| ⚠️ **否決** | **3 件**（D-1 / D-2 / D-3） |
| ★ 判定不能 | **1 件**（U-1） |
| 新規登録 | **22 件**（[P170]–[P191]）＋ **[V88]**。★ **既出 2 件（[P113] / [P104]）は新規登録せず既存行を更新した** |

> ⚠️ **ゼロはゼロと書く**: 「不便益の効果を無作為化統制下で検定した研究」は **本ラウンドの探索でゼロ**だった。
> ★★★ **ここでは「空白は有望を意味しない」の逆が起きている** ——
> ★ **不便益は 20 年以上の蓄積を持ちながら、効果量を持つ研究をほぼ産んでいない。**

---

## gate 判定（★ 要点先出し・下位問いごとに温度 1 行）

| 下位問い | 温度 | 1 行 |
|---|---|---|
| **RQ-4a 不便益** | ★ **語彙と分類は確定 / 効果は判定不能（実証が事実上無い）** | ★ GSE が使う「主体性・気づき・工夫の余地」は **8 枚の不便益カードのうち 3 枚（Encouraging initiative / Enhancing awareness / Devising ways）に literally 一致**し射程に乗る [P170]。⚠️ **しかし不便益側の実証は N=32・1 週間・仮説生成の 1 本しかなく、そこでも便益を感じたのは 32 名中 6 名である** [P171] |
| **RQ-4b SDT** | ★★★ **確定（定義は原典逐語で取れた）／ただし GSE 側に計器が無い** | ★ 逐語 *"autonomy is not defined by the absence of external influences but rather by one's assent to such influences"* ／ *"**having many options is not a basic need**"* [P178] → ⚠️★★★ **「opt-in と dismiss があるから自律性を脅かさない」は SDT では成立しない。** 効くのは **本人が是認できるか**である |
| **RQ-4c 反省・遅い技術** | ★★ **確定（系譜が一次で繋がった）** | ★ Informative Art の一次を取得し *"Informative art can be seen as a kind of slow technology, i.e. a technology that promotes moments of concentration and reflection."* [P113] で Slow Technology へ直結。⚠️ ただし **系譜全体が設計論であり効果の出典ではない**（[P45] [P67] と同じ温度） |
| **RQ-4d 主張形式** | ★★★ **確定・しかも GSE に有利** | ★ Reflective Design 原則 4 の逐語 *"Technology that monitors and reports on user activity or experiences should be carefully designed to **avoid making the technology, rather than the user, the final authority on what the user is doing**"* [P183] ＝ ★ **GSE の「断定しない・外在化に留める」は、名前を持った既存の設計原則である**（★ GSE の独創ではないが、正当化される） |
| **RQ-4e 反証** | ⚠️★★★ **確定・かつ GSE に不利な側が具体的に出た** | ⚠️ SDT メタ分析（k=99 / 119 標本）逐語 *"contrary to SDT, the variance basic psychological needs account for in some of these outcomes is **statistically significant but practically insignificant**"* [P182] ／ [P187] の **displacement 警告** ／ Slow Technology 最長の実配備は **N=3 世帯・14 か月の質的所見** [P186] |

---

## ★ GSE の主張の書き方 — 支えられている所 / 過大な所 / 言い換えるべき所

> ⚠️ **言い換えは案である。§4 / §5 の実際の書き換えは次セッションの研究者判断であり、ここでは断定しない。**
> ★ **言い換えが要る箇所 = 5 件**（★ うち最重要 = 1 件）。

| # | 該当記述（逐語） | 判定 | 根拠 | 提案する書き換え |
|---|---|---|---|---|
| **1 ★★★** | `research-positioning.md`「**不便益を測定可能・介入可能にした前向き実証**を HCI コミュニティへ提示する」 | ⚠️★★★ **過大** | ★ **不便益には合意された測定尺度が存在しない。** 唯一の統制実験 [P171] すら不便益そのものを測らず、**自作の 2 システム比較アンケート ＋ 既存の人格尺度**で「便益を感じたと答えた人の特性」を推定しているだけである。★ **GSE が実際に測るのは行動指標（機会保存）であって不便益ではない** | 「**不便益を思想として掲げた介入を、content-free な行動指標で前向きに検証した実装例**を提示する」。★ **「不便益を測定した」と読ませない** |
| **2 ★★★** | `research-positioning.md`「GSE は摩擦を区別して『消すべきでない摩擦』の下で自力解決の機会を保存する**不便益 [P6] HCI である**」 | ⚠️★★ **現行実装では支えられない** | ★ 不便益の定義は逐語で **「不便であること」＝「労力がかかること」**（物理的／心理的の 2 種）＋ **3 条件**（条件 1: 益は不便だからこそ／条件 2: 不便を被るのは受益者本人／条件 3: 副次的）[P170]。⚠️★★★ **ADR-015 で Lv2 Wall を削除した後、稼働する介入は Lv1 Nudge のみで、それは非ブロック・自動消失＝労力を課さない**。⚠️ 不便を実際に担う Lv3/Lv4 Physical Anchor は**未実装**（★ しかも ADR-015 D4 で運搬路を失っている） | 「GSE は **不便益を設計思想として引く** HCI である。⚠️ ★ **不便を実際に担うのは Lv3/Lv4 Physical Anchor であり、本フェーズでは未実装である**（★ 現行の Lv1 Nudge は労力を課さないため、不便益の定義には乗らない）」 |
| **3 ★★** | `architecture/gse-v2-overview.md:44`「**本人の自律性を損なわない範囲で**『何もしない／待つ／軽く気づかせる／一度離す』を選択する」 | ⚠️ **定義が空（誤読の危険）** | ★ SDT の autonomy は原典逐語で **"regulation by the self"**、その反対 heteronomy は **"regulation that occurs without self-endorsement"**。⚠️★★★ *"having many options is not a basic need"* ＋ *"one could have only one option … and yet feel quite autonomous so long as one truly endorses that option"* [P178] → ★ **「選べる／消せる」は自律性の定義ではない** | 「本人が **自ら是認できる (self-endorsed)** 範囲で…」＋ 逐語出典として [P178] を引く。★ **「opt-in / dismiss があるから自律的」という論法は使わない** |
| **4 ★★** | `wbs-verification-halfyear.md:293` Gate H「annoyance・tension・**autonomy loss**・false-positive cost…」 | ⚠️ **計器が無い（★ 拒否権付きゲートなのに）** | ★ Gate H は「**悪化した場合、X1 が Go でも介入機能は Go としない**」＝ **反証ゲート**である。にもかかわらず `autonomy loss` の**尺度も理論も未登録**だった | 「**autonomy loss**（★ 尺度＝ **[V88] METUX の TENS-Interface の autonomy 下位尺度**を第一候補とする。⚠️ 著者自身が *"The measures presented are initial iterations that will require more thorough validation"* と留保しているので、**確証には使わず Gate の運用指標として使う**）」 |
| **5 ★** | `research-positioning.md:111`「**不便益 (Benefit of Inconvenience)** [P6]: 川上・内藤。利便性と便益を直交軸とみなす設計思想。GSE の介入哲学の源流。」 | ○ **記述は正しい。書誌が空なだけ** | ★ [P174] 章 1 の逐語 *"a value axis orthogonal to efficiency and functionality"* が「直交」を裏づける | **本文は変更不要。** ★ `references.md` 側で **[P6] を tombstone せずに残しつつ、一次 4 本（[P170] / [P171] / [P172] / [P174]）へ誘導する**のが正しい処置（★ 本ラウンドで実施済み） |

### ★ 逆に「支えられている」ことが分かった記述（★ 変更不要・むしろ強化できる）

| 該当記述 | なぜ支えられるか |
|---|---|
| 「★ **判定 = `de-risk 先行`。★ 効果を主張しない。**」 | ★★★ **これは HCI に名前を持つ立場である。** ⚠️ しかも**先行研究の側が自分で効果を否定している** —— Informative Art の創始者が自作物について *"its usefulness as an awareness support is rather limited"* と書いている [P113]。★ **「効果を主張しない」は逃げではなく、この系譜の標準的な作法** |
| 「本フェーズで GSE が主張・測定するのは**自力解決の機会の保存**（行動指標）に限定し…」 | ★★★ **[P187] の displacement 警告を構造的に回避している。** 逐語: *"risks a displacement, wherein reflection is linked with some desired outcome … and assessment of that outcome is taken as evidence that reflection occurred"*。→ ★ GSE は**行動を測って行動だけを主張する**ので、この罠に落ちていない。★ **この設計判断の方法論的根拠として [P187] を引ける** |
| 「測定（キーストローク）・**思想（不便益）**・学習科学・身体性を…統合」 | ○ **「思想」と明示していて正しい温度。** ★ 上記 #1 の行はこの温度に合わせるべきで、逆ではない |
| 「脳内状態を読まない／断定しない／外在化に留める」 | ★★★ **[P183] Reflective Design 原則 4 の逐語そのもの。** ★ **GSE の独創ではないが、既存原則に正確に一致している** ＝「原則に接地している」と書ける（⚠️ **ただし効果の接地ではない**） |

---

## カード 1: 不便益の定義は「労力がかかること」＋3 条件であり、GSE が使う 3 語は 8 枚のカードに literally 一致する **[検証済 3-0]** [P170]

**1. どんなもの**: 平岡敏洋「不便益を得るシステムの要件」（*計測自動制御学会誌* 60(12), 2021）。
★ **不便益の 20 年の定義の変遷を 1 本にまとめ直し、要件を形式化した論文。**★ 一次 PDF 全文を pypdf で読解
（⚠️ CJK CID 埋め込みのため日本語に部分欠落あり。英語ラベル・数式・数値は取得できた）。

**2. 先行研究と比べてどこがすごい**: ★ 著者自身が冒頭で **「不便益に対する注目が増しているが、その意味・解釈が
受け手ごとに多様になっており、川上の定義とは異なるケースが少なくない」** と書いており、
★ **概念の拡散を止めるために書かれた「定義の SSOT」である。**
→ ★ **GSE が引くべきはここであって、メディア記事や書籍の紹介文ではない。**

**3. 技術・手法の肝（★ 原典の定義）**:
- ★ **「不便であること」＝「労力がかかること」**。労力には **① 物理的労力 ② 心理的労力** の 2 種。
- ★ **不便益カード（8 種）**の英語ラベル（★ 図 1 の逐語）:
  **System comprehension / Devising ways / Improvement / Preventing loss of skill /
  Feelings of relaxation and trust / Personalization / Encouraging initiative / Enhancing awareness**
  （**Objective benefits** と **Subjective benefits** の 2 群）。
- ★ **不便益と認定するための 3 条件**: **条件 1 益は不便だからこそ／条件 2 不便を被るのは受益者本人／条件 3 副次的**。
- ★ **6 タイプ (I–VI)**。表 2 の帰結: **III・VI は不便益システムではない**／**IV・V は「益システム」**。
- ★ **9 原理**。★ **旧 12 原理から「疲れさせよ」「時間がかかるようにせよ」等を除外した** ——
  ★ **理由は「それらは *結果* であって *操作* ではないから」。**

**4. どうやって有効だと検証したか**: ⚠️★★★ **していない。解説（レビュー）論文であり、実証を一切含まない。**

**5. 議論はあるか（留保）**:
- ⚠️★★★ **著者自身が「タイプ II〜VI を不便益とみなしてよいかという議論を進めていく必要がある」と書いて、
  *未決のまま置いている*。** → ★ **不便益は 2021 年時点でも境界が確定していない概念である。**
- ⚠️ **効果の出典ではない**（[P45] [P67] [P104] と同じ温度＝**定義と語彙まで**）。

**6. 次に読むべき論文**: [P176]（カードの英語一次）／[P174] 章 5「Supporting Human Activities by Obstruction」。
⚠️ **[P177]（岩波ジュニア新書『不便益のススメ』）は査読文献ではないので、研究の根拠には使わず
思想の一般向け説明としてのみ扱う**（★ [P67] Eno のライナーノーツ・[P146] Sony 製品文書と同じ温度）。

> **GSE への含意**:
> ① ★ GSE が使う「**主体性・気づき・工夫の余地**」は **Encouraging initiative / Enhancing awareness /
> Devising ways** に literally 一致する ＝ **射程に乗っている（3-0）**。
> ② ⚠️★★★ **しかし条件 1（益は不便だからこそ）が現行実装で満たされない。**
> Lv1 Nudge は非ブロック・自動消失で**労力を課さない**ため、そもそも「不便」ではない。
> ★ **不便を担うのは Lv3/Lv4 Physical Anchor（未実装）である。**
> ③ ★ 条件 2・3 は満たす（不便を被るのは本人／益は主目的＝執筆の副次）。

---

## カード 2: 不便益の唯一の統制実験 —— ⚠️ **N=32・1 週間・仮説生成であり、便益を感じたのは 32 名中 6 名だった** **[検証済 3-0]** [P171]

**1. どんなもの**: 荒木卓・川上浩司・平岡敏洋「システムから不便益を得るユーザ特性に関する実験的考察」
（*計測自動制御学会論文集* 51(11), 2015）。★ 一次 PDF 全文（同上の CID 欠落あり）。

**2. 先行研究と比べてどこがすごい**: ★ **本ラウンドの 7 angle で見つかった、不便益を統制条件下で操作した
唯一の査読論文**である。
⚠️★★★ **逆に言えば「20 年・書籍複数冊・Springer の編著書 1 冊を持つ設計思想に、統制実験が実質 1 本しかない」
ということである。**

**3. 技術・手法の肝**:
- ★ **不便益の定義を式で書いている（逐語）**:
  **`便利 ≡ 特定のタスク達成に省労力であること`** / **`労力 ⊃ 特定のスキルを要するもの ⊃ 心的負荷`**。
- ★ **操作**: Android ジェスチャランチャの便利版 vs **相違度に比例する起動遅延**（`t_d = r·D(G,T̄)`・最大 10 秒）を
  各 1 週間・被験者内・順序カウンターバランス。

**4. どうやって有効だと検証したか（★ 実数）**:
- **N=32**（男 21 / 女 11・18–25 歳・学生）。
- ⚠️★★★ **不便版に肯定評点を付けた＝不便益を感じたのは 32 名中 6 名のみ。**
- ★ その 6 名は **有能感が有意に高い**（Welch の t 検定 **p=0.015**）／
  **熟練度の分散が有意に小さい**（F 検定 **p=0.027 / p=0.023**）。
- ★ 結論の 3 特性: **(1) 有能感が高い (2) スキルが特定範囲に収まる (3) 評価が低い**。
- ★★★ **有能感尺度の引用元が Deci & Ryan の SDT ハンドブック** ＝ **不便益研究が解釈を SDT に借りている。**

**5. 議論はあるか（留保）**:
- ⚠️★★★ **著者自身が「仮説生成」と明記し、「他の不便さでも成立するか検証が必要」で終わる ＝ 確証ではない。
  効果量は 1 つも報告されていない。**
- ⚠️ 学生・1 週間・単一の不便操作（起動遅延）。

**6. 次に読むべき論文**: [P175]（英語の設計ガイドライン）。

> ★★ **GSE への含意**: ★ **「摩擦の効果は安定した個人特性で調整される」の 3 本目の独立収束**
> （[P127] Need for Cognition / [P128] Friction Disposition に続く。★ ADR-008 と整合）。
> ⚠️ **ただし本行が最も軽い**（N=32・仮説生成・効果量なし）。

---

## カード 3: SDT の autonomy は「選択肢の多さ」ではなく **self-endorsement** である **[検証済 3-0]** [P178]

**1. どんなもの**: Ryan & Deci (2006) *Journal of Personality* 74(6)。★ **一次全文を pypdf で読解。**

**2. 先行研究と比べてどこがすごい**: ★ **SDT の中でも「autonomy とは何でないか」を正面から扱った回**である。

**3. 技術・手法の肝（★ 原典の定義の逐語）**:
> *"The term **autonomy** literally refers to **regulation by the self**. Its opposite, heteronomy, refers to
> controlled regulation, or **regulation that occurs without self-endorsement**."*

> *"autonomy is **not defined by the absence of external influences** but rather by **one's assent to such
> influences** or inputs. Autonomy is thus **not equivalent to independence**"*

> ★★★ *"One can have many options and not feel autonomy, but instead feel overwhelmed and resentful at the
> effort entailed in the decision making. Alternatively, **one could have only one option (which functionally
> means no choice) and yet feel quite autonomous so long as one truly endorses that option**."*

> 結論: *"independence is not a universal need; **having many options is not a basic need**, nor is it even
> always edifying"*

**4. どうやって有効だと検証したか**: ⚠️ **理論論文＋自陣のレビューであり、本論文自身は新規の実証を含まない。**

**5. 議論はあるか（留保）**:
- ⚠️ **自陣レビューである**（★ [P107] Cameron と同じ理由で単独では引かない）。対抗出典は [P182]。
- ⚠️ 本論文内に Eisenberger & Cameron 1996 への反論も含まれており、**係争の当事者の文章**である。

**6. 次に読むべき論文**: [P179]（BPNT の定式化）／[P181]（現行の体系書）。

> ⚠️★★★ **GSE への含意（★ 設計判断を直接縛る）**:
> **「GSE の opt-in / dismiss は自律性を保護する」は SDT では成立しない**（→ 否決 D-2）。
> ★ **正しい書き方は「事前の是認 (self-endorsement) を取っているから」であって「選べるから」ではない。**
> → ★ `gse-v2-overview.md:44` の「本人の自律性を損なわない範囲で」は
> **「本人が自ら是認できる範囲で」**と書き直すのが正確である。

---

## カード 4: SDT を HCI で運用可能にした枠組み（METUX）—— ⚠️ 「ある層で needs を支え、別の層で損なう」ことが起こると明記している **[検証済 3-0]** [V88]

**1. どんなもの**: Peters, Calvo & Ryan (*Frontiers in Psychology* 9:797, 2018)。★ **一次全文 15 頁を読解。**
★ **Ryan 本人が共著**であり、**SDT を HCI で運用可能にした唯一の公式枠組み**である。

**2. 先行研究と比べてどこがすごい**: ★ **6 sphere**（Adoption / Interface / Task / Behavior / Life / Society）に
分けて、**どの層で needs を測るのかを分離**した。

**3. 技術・手法の肝（★ 逐語）**:
> *"a technology can **support psychological needs at one level while undermining them at another**"*

→ ★ **GSE では「表現層で autonomy を支えつつ介入層で損なう」が構造的にありうる。**

> *"Devices that offer options and choices over use, and **do not in turn demand actions from users without
> their assent**, enhance feelings of autonomy."*

→ ★ `intervention-design` の**非ブロック性ルールの理論的正当化**になる。

★ **尺度**: **ACTA**（採用）／**TENS-Interface** ／ **TENS-Task** ／ **TENS-Life**
（★ PENS 21 項目からゲーム固有項目を除いて構成）＋ BPNS / PNSES / Flourishing Scale。
★ SUS との違い（逐語）: *"high usability does not necessarily predict high engagement or positive experience"*。

**4. どうやって有効だと検証したか**: ⚠️★★★ **していない。HYPOTHESIS AND THEORY 区分の理論提案である。**

**5. 議論はあるか（留保）**:
- ⚠️★★★ **著者自身の留保（逐語）**: *"**The measures presented are initial iterations that will require more
  thorough validation and refinement**"* ／ *"SDT, while a mature theory with robust support, remains a
  psychological theory open to ongoing interrogation."*
- ⚠️ **付録の妥当性検証の N と TENS の項目数は本文から読めなかった（判定不能）。**
- ⚠️ **n=3–10 での反復測定としての妥当性は本論文からは言えない**（★ 併せて [P182] の
  *"we discourage cross-sectional self-report studies"* を読むこと）。

**6. 次に読むべき論文**: [P182]（SDT の実務的有意性への反証）／[P191]（反省の水準の枠組み）。

> ★★★ **GSE への含意**: ★ **Gate H の `autonomy loss` に対する唯一の計器候補である。**
> → ★ **確証には使わず、Gate の運用指標として使う**（★ 著者自身が初期版だと留保しているため）。

---

## カード 5: 「技術が本人より上位の判定者になってはならない」—— Reflective Design 原則 4 は GSE の主張形式そのものである **[検証済 3-0]** [P183]

**1. どんなもの**: Sengers, Boehner, David & Kaye (*Critical Computing '05*)。★ **一次全文を読解**（著者版 PDF）。

**2. 先行研究と比べてどこがすごい**: ★ **「反省を目的とする設計」に原則と戦略を与えた基礎文献。**

**3. 技術・手法の肝（★ 逐語）**:
> ★★★ **原則 4**: *"Technology should support skepticism about and reinterpretation of its own working. …
> **Technology that monitors and reports on user activity or experiences should be carefully designed to
> avoid making the technology, rather than the user, the final authority on what the user is doing.**"*

> ★ **原則 5**: *"**Reflection is not a separate activity from action but is folded into it** as an integral
> part of experience."*

→ ★★ **HCI の「使いやすさは反省と背反」という読みを名指しで否定しており、
GSE が *作業中に* Nudge を出す（別画面の振り返りではない）ことの理論的根拠になる。**

> ★ **戦略 1**: *"Provide for **interpretive flexibility**. Reflective design allows users to maintain control
> of and responsibility for the meaning-making process."*（★ [P45] Gaver の ambiguity を明示的に採用）

> ★ **戦略 2**: *"Give users license to participate"*
> ⚠️ **見慣れぬものにすると「疎外・混乱・無関心」を招く**（★ [P112] の「装飾だと思った」と同型の警告）。

**4. どうやって有効だと検証したか**: ⚠️★★★ **していない。** ケーススタディ 2 件は例示のみで統制・効果測定なし。

**5. 議論はあるか（留保）**:
- ⚠️★★★ **概念・設計論文であり効果の出典ではない**（[P45] [P54] [P67] と同じ温度）。
- ⚠️★★★ **したがって「断定しない」を *新規性* として書いてはならない** ——
  ★ **2005 年に名前が付いた既存原則である。**

**6. 次に読むべき論文**: [P187]（評価方法論）／[P189]（説得しない設計）。

> ★★★ **GSE への含意**: ★ **GSE の「断定しない・外在化に留める」は独創ではなく、既存原則に正確に一致している。**
> → ★ **書けるのは「既存原則を、実作業中のリアルタイム推定に初めて適用した」という形まで**であり、
> ⚠️ **本ラウンドはそれを支持する証拠を持っていない**（★ 判定は次セッション）。

---

## カード 6: ⚠️ Informative Art の一次を取得した —— 定義は確定し、同時に **著者自身が有用性を "rather limited" と書いていた** **[検証済 3-0]** [P113]

> ★ **既出 [P113]。本ラウンドで一次を取得し、DOI を確定して provisional → active へ昇格した。**

**1. どんなもの**: Redström, Skog & Hallnäs (*DARE 2000*)。★ **一次全文 10 頁を読解。**

**2. 先行研究と比べてどこがすごい（★ 本ラウンドでの新しさ）**:
⚠️★★★ **既存の二次記述の逐語は語順が誤っていた** ——
正しくは *"works of art that **not only are** aesthetical objects **but also** information displays"*。

**3. 技術・手法の肝（★ 逐語 3 点）**:
- ★★★ **Slow Technology への直結**:
  *"**Informative art can be seen as a kind of slow technology, i.e. a technology that promotes moments of
  concentration and reflection.**"*
  → ★ **[P104] が一次未取得のままでも、Slow Technology の定義だけは同著者の本論文で押さえられる。**
- ★ **遅さの必要性**: *"If an object of informative art should be of some interest as an object of reflection
  **it can not be too fast and immediate. There must be something to reflect on** … The objects can not just
  act as tools for fast access to information."*
- ★ **表現原理**: *"a **mapping between design structure and information structure** rather than a effective
  presentation of information content"*
  → ★ **内容でなく構造を写す** ＝ **GSE の content-free 制約と原理レベルで一致する。**

**4. どうやって有効だと検証したか**: ⚠️★★★ **していない。しかも著者自身が自作物を否定的に評価している**（逐語）:
> *"**its usefulness as an awareness support is rather limited**, since some people found the recombination of
> material as more of a degradation of information"*

★ 評価の難しさも逐語で述べられている:
> *"In the case of an artwork, evaluations in this sense are not relevant at all. Instead reflection and
> critical analyses are of interest. Since informative art falls somewhere in between these two categories of
> design, **evaluating pieces of informative art might be a quite complex issue**."*

**5. 議論はあるか（留保）**:
- ⚠️★★★ **本論文のプライバシー論（抽象性と対称性で監視にならない）は、[P132] の 2024 年実測に否定されている側**である。
  ★ **2000 年の楽観を引き写さないこと。**
- ⚠️ **効果の出典ではない。**

**6. 次に読むべき論文**: [P104]（★ 一次到達不能の可能性）／[P185]（10 年後の総括）。

> ★★★ **GSE への含意**: ★ **「効果を主張しない」は逃げではなく、この系譜の標準的な作法である** ——
> ★ **創始者自身が自作物の有用性を "rather limited" と書いている。**

---

## カード 7: 「効果を主張しない」評価の作法 —— ⚠️ 反省を望ましいアウトカムで代理すると **displacement** になる **[検証済 3-0]** [P187]

**1. どんなもの**: Baumer (*CHI '15*)。★ **一次全文を読解**（著者版）。

**2. 先行研究と比べてどこがすごい**: ★ **「反省を目的とする設計」の評価方法論に、初めて概念的な次元を与えた。**

**3. 技術・手法の肝**: ★ **3 次元 —— Breakdown / Inquiry / Transformation。**
★ Breakdown の根拠は Dewey の *doubtful or puzzling situations*、Schön の
*"there is some puzzling, or troubling, or interesting phenomenon"*、Mezirow の *"disturbing anomalies"*。
★ 設計含意（逐語）:
> *"**drawing attention to or even inducing breakdowns may provide opportunities for moments of reflection.**"*

→ ★★ **GSE の `p_stuck` 高値の瞬間はまさに breakdown であり、介入タイミングに理論的根拠が 1 本増える。**

**4. どうやって有効だと検証したか**: ⚠️ **概念論文で実証は無い。** ★ ただし**分野の実測を 1 つ提示している**（逐語）:
> *"few of the papers describing systems purported to support reflection provide more than a one- or
> two-sentence definition of the concept"*

★★★ **そして GSE に最重要の警告（逐語）**:
> *"risks a **displacement**, wherein reflection is linked with some desired outcome (e.g., increased learning,
> improved performance), and **assessment of that outcome is taken as evidence that reflection occurred**."*

★ 量化への警告（逐語）:
> *"Trying to determine when an individual (or group) is being 'more reflective' seems at best a misconstrual
> of the value of reflection and at worst a harmful and deleterious reduction"*

**5. 議論はあるか（留保）**:
- ⚠️ 著者自身が反省の**特権性**と *"paralysis by analysis"* を留保として挙げる。
- ⚠️ **概念論文であり、3 次元の妥当性は検証されていない。**

**6. 次に読むべき論文**: [P188]（★ 実測値がここにある）／[P191]（反省の水準 R0–R4）。

> ★★★ **GSE への含意**: ★ **GSE が行動指標だけを測って学習効果を主張しないのは、この displacement を
> 構造的に回避している** ＝ **主張範囲の限定に方法論的根拠が 1 本増える。**
> ⚠️ **逆に、将来「表現層が反省を促した」と言いたくなったとき、行動指標の改善をその証拠にしてはならない**
> （★ その場合の正しい計器は既登録の [V77] TSRI / [V78] RRT）。

---

## カード 8: ⚠️ SDT の基本欲求は「統計的に有意だが実務的には無視できる」分散しか説明しない場合がある **[検証済 3-0]** [P182]

**1. どんなもの**: Van den Broeck, Ferris, Chang & Rosen (*Journal of Management* 42(5), 2016)。
**k=99 研究・119 独立標本**のメタ分析レビュー。★ **一次全文を読解**（OA 版）。

**2. 先行研究と比べてどこがすごい**: ★ **SDT を職場文脈で初めて大規模に検証し、支持と反証を同じ論文内で出した。**

**3. 技術・手法の肝**: ★ **定義の補強（逐語）**:
> *"the need for autonomy **does not imply a need to act independently** from the desires of others; rather,
> it implies the need to act with a **sense of choice and volition**, even if doing so means complying with
> the wishes of others."*

**4. どうやって有効だと検証したか（★ 逐語）**:
- ★ **支持側**: *"we find general support for SDT's requirement that each need should independently predict
  indicators of psychological growth, internalization, and well-being."*
- ⚠️★★★ **反証側（同じ文の後半）**: *"However, our findings also illustrate that **contrary to SDT, the
  variance basic psychological needs account for in some of these outcomes is statistically significant but
  practically insignificant**; our review also surfaces issues with the literature's most commonly used scale."*
- ⚠️ 実数の一例: **need satisfaction 全体が attendance の分散の 2% しか説明せず予測に失敗。**

**5. 議論はあるか（留保）**:
- ⚠️ **尺度依存**（Deci et al. 2001 vs Van den Broeck et al. 2010 で結果が変わる）。
- ⚠️ 他の need 候補との比較検定がほぼ無い ＝ **「3 つで足りる」は未検証。**
- ★★★ **方法論的警告（★ GSE に有利・逐語）**:
  > *"the vast majority of the studies we examined used **cross-sectional** research designs … We therefore
  > **discourage cross-sectional self-report studies** dealing with basic psychological needs"*

  → ★ **GSE の個人内・縦断・日次デザインは、SDT 文献が自ら求める方向にある（貢献として書ける）。**

**6. 次に読むべき論文**: [P179] / [P181]（理論本体）。

> ⚠️★★★ **GSE への含意**: ★ **SDT を引くときは本行を併記する**（★ [P99] に対する [P107] と同じ役割）。
> ★ **「autonomy を支えれば良い結果が出る」とは書けない。**

---

## カード 9: ludic design ——「外から与えられた課題ではなく、好奇心・探索・反省に動機づけられた活動」のために設計する **[検証済 2-1]** [P184]

**1. どんなもの**: Gaver ら (*CHI '04 Extended Abstracts*, Design Case Study)。★ **一次全文を読解。**

**3. 技術・手法の肝（★ 逐語）**:
> *"activities motivated by **curiosity, exploration, and reflection** rather than **externally-defined tasks**"*

> *"design choices we made, for example to **block or disguise utilitarian functionality**"*

> *"The table's role in these activities is **not as a source of definitive information**."*

**4. どうやって有効だと検証したか**: ⚠️ 数週間の家庭内エスノグラフィのみ（世帯単位で 1 桁・統制なし・アウトカム測定なし）。

**5. 議論はあるか（留保）**:
- ⚠️★★★ **GSE は ludic design ではない**（→ 否決 D-3）—— ludic の定義が **"rather than externally-defined tasks"**
  であるのに対し、**GSE は externally-defined task（論述執筆）の真っ最中に働く。**

**6. 次に読むべき論文**: [P45]（既出・ambiguity）。

> ★ **GSE への含意**: ★ **借りるのは「効果でなく *使われ方* を書く」評価作法まで。**
> ⚠️ **系譜として名乗ってはならない。**

---

## ⚠️ 否決リスト

| # | 否決した主張 | 票 | 否決理由 |
|---|---|---|---|
| **D-1** | 「**不便益は実証的に支持された設計原理である**」 | **0-3** | (i) 原典忠実性 ✗ —— 不便益の一次自身が「実証」を主張していない（[P170] は解説・[P172] は総論・[P174] は編著）。(ii) 外挿 ✗ —— 唯一の統制実験 [P171] は**著者が明示的に「仮説生成」と書き、効果量を 1 つも報告していない**。(iii) 実証 ✗ —— 7 angle の探索で **RCT ゼロ / メタ分析ゼロ / 追試ゼロ**。→ ★ **不便益は [P45] と同じ「語彙まで」の温度に確定する。** ⚠️ **案に有利な主張** |
| **D-2** | 「**GSE の opt-in / dismiss は自律性を保護する**」 | **1-2** | (i) 原典 ✓ 該当文献はある。(ii) 外挿 ✗ —— SDT 原典逐語が真っ向から否定する: *"having many options is not a basic need"* / *"one could have only one option … and yet feel quite autonomous so long as one truly endorses that option"* [P178]。(iii) 実証 ✗ —— **GSE 側に autonomy の測定が 1 つも無いので、保護されているかを言えない**。→ ★ **正しい書き方は「事前の是認 (self-endorsement) を取っているから」であって「選べるから」ではない。** ⚠️ **案に有利な主張** |
| **D-3** | 「**GSE は ludic design / slow technology の系譜に属する**」 | **1-2** | (i) 原典 ✓ 定義は一次で取れた。(ii) 外挿 ✗✗ —— ludic の定義は **"rather than externally-defined tasks"** [P184] であり、GSE は externally-defined task の最中に働く。slow technology は **"technology that promotes moments of concentration and reflection"** [P113] で**長期・低頻度・非作業文脈**を前提にする（実配備例は 14 か月の家庭内 Photobox [P186]）。→ ★ **GSE が属するのは reflective design（カード 5）であり、そこは語彙が一致する。** ⚠️ **案に有利な主張** |

### ★ 判定不能（★ 丸めない）

| # | 主張 | なぜ判定不能か |
|---|---|---|
| **U-1** | 「**Encouraging initiative（主体性）と Enhancing awareness（気づき）は、不便益理論では *主観的益* に分類される**」（＝ GSE が客観的行動指標で測ろうとしているものが、理論側では主観カテゴリである） | ★ [P170] 図 1 の **8 つの英語ラベルは CID から完全に取れた**が、**Objective / Subjective のどちらの群に属するかは図のレイアウト依存**で、テキスト抽出からは確証できない。⚠️★★★ **もしこれが真なら、GSE の headline（行動指標での機会保存）と不便益の益カテゴリが *ずれている* ことになり、主張の書き方に影響する。** → ★ **次ラウンドで図を画像として確認するか、[P176] で照合する必要がある。** |

★ **対称性の記録**: ⚠️ **否決 3 件はすべて GSE に有利な主張である。**
★ **同時に、GSE に不利な側（reflective design 一致は新規性を削る／SDT の実務的有意性が低い／不便益に実証が無い）は
すべて本体に残した。** ★ **有利な主張を落とし、不利な主張を残す方向に非対称である。**

---

## ★ 既出 [n] への更新

| 既出 | 本ラウンドでの処置 |
|---|---|
| **[P113]** Informative Art | ★★★ **一次全文 10 頁を取得。key を `url:dare2000-informative-art` → `doi:10.1145/354666.354677` に確定し、provisional → active へ昇格。** ⚠️ **既存の二次記述の逐語は語順が誤っていた**ので訂正。★ 足した別の主張 3 点（Slow Technology への直結 / 遅さの必要性 / 構造を写す原理）と、⚠️ **著者自身の否定的評価**を追記 |
| **[P104]** Slow Technology | ⚠️★★★ **昇格できなかったことを明記した**（Springer CLOSED・Unpaywall にも OA なし）。★ **査読二次からの逐語 2 本**で代用しつつ、⚠️ **一方の頁番号が本論文自身の頁範囲と矛盾する**ことを「未検証」として記録。★ **定義自体は [P113] で押さえられた** |
| **[P6]** 不便益 | ⚠️★★★ **書誌そのものが未検証であることを追記し、`active` → `provisional` に落とした。** ★ **番号は再利用しないので行は残す**が、**不便益を引くときは一次（[P170] / [P171] / [P172] / [P174]）を引く**よう誘導した |

---

## ⚠️ やり残し（★ 次ラウンドの入口）

1. ★★★ **[P6] の書誌そのものが検証できていない** —— 「Kawakami, H. & Naito, K. *Benefit of Inconvenience*,
   Proc. Design Society, 2019」に該当する文献を本ラウンドでは確認できなかった。
   ⚠️★★★ **「コア思想」と呼ぶものの書誌が未検証のまま `active` になっていた**（★ 本ラウンドで provisional に落とした）。
   → ★ **次ラウンドの最優先。**（★ Naito, K. は不便益カードの共著者 [P176] なので、その系列の可能性が高い。）
2. ★★★ **判定不能 U-1 の解消**: [P170] 図 1 の 8 枚のうち **`Encouraging initiative` と `Enhancing awareness` が
   Objective / Subjective のどちらの群か**。→ ★ 図を画像で確認するか、[P176] で照合する。
3. ★★ **[P104] Slow Technology の一次全文**（★ 経路が無い可能性が高い）。
   → ★ **「一次到達不能」と明記して provisional のまま固定する判断もありうる。**
4. ★★ **[P188] Baumer et al. DIS '14 "Reviewing Reflection" の一次**（★ 対象論文数・年代・「定義していない」の実数）。
   ★ **RQ-4e の反証の *強さ* がこの数字で決まる。**
5. ★★ **[P189] Brynjarsdóttir et al. CHI '12 の一次**（★ 本ラウンドの含意は二次記述に基づく推論に留まる）。
   ★ 「技術を客観的裁定者の位置に置く」の逐語が取れれば、[P183] 原則 4 と独立の 2 本目になる。
6. ★★ **[P190] Leshed & Sengers CHI '11 の一次**（★ GSE の対象領域そのものへの批判）。
7. ★ **[P175] 不便益の英語設計ガイドライン**と **[P174] 章 5「Supporting Human Activities by Obstruction」／
   章 6「Weak Robots」**（★ GSE の介入設計に最も近い章）。
8. ★ **[P173] 野坂 2021**（PDF は取得済み・未読）。
9. ★ **[V88] METUX 付録の妥当性検証の N と因子構造**（★ Gate H の計器として採用するなら必要）。
   ★ 併せて **TENS-Interface / TENS-Task の項目数**。
10. ★ **SDT の残る一次**（[P179] / [P180] / [P181]）。
    ⚠️ **ただし autonomy の定義は [P178] の一次逐語で取れているので優先度は低い。**
11. ⚠️ **本ラウンドで探索できなかった angle**: **Cognitive Evaluation Theory の一次**（Deci & Ryan 1985）と、
    **「介入が自律性を損なうか」を実測した HCI 研究**（★ [P46] は設計空間レビューで実測ではない）。

---

## `research-positioning.md` §3 / §4 への還元

> ⚠️ **§4 / §5 の実際の書き換えは次セッションの研究者判断である。以下は §3 への追記のみを行い、
> §4 への影響は「判定」として記録するに留める。**

### §4（差分 = 研究の所在）に **影響するか** の判定（★ 書き換えはしない）

| 論点 | §4 に影響するか | 判定の根拠 |
|---|---|---|
| **不便益の実証が事実上無い** | ⚠️★★ **影響する（ただし *強める* 方向）** | ★ §4 の既存記述「不便益は介入の思想を与えるが、実作業中にそれをリアルタイム同定する閉ループを持たない」は**そのまま正しい**。★ **本ラウンドが足すのは「思想を持つだけでなく、*実証もほぼ持っていない*」**という一段強い空白の記述である。⚠️ **ただし同時に「不便益を測定可能・介入可能にした前向き実証」は過大になる** |
| **GSE の主張形式が reflective design に一致する** | ⚠️ **§4 の *新規性* には影響しない（むしろ新規性を 1 つ削る）** | ★ 「断定しない・外在化に留める」は **2005 年に名前が付いた既存原則**である。→ ★ **これを新規性として書いてはならない。** ★ 代わりに「既存原則を、実作業中のリアルタイム推定に初めて適用した」という形にできる（⚠️ **本ラウンドはそれを支持する証拠を持っていない**） |
| **SDT の autonomy 定義** | ⚠️ **§4 には影響しない。§5（仮説）／§8（限界）／WBS Gate H に影響する** | ★ autonomy は GSE の**新規性の所在ではなく、測定と限界の問題**である |
| **displacement 警告** | ○ **§4 に影響しない。§1 / §8 の限定を *支持* する** | ★ 既存の限定（機会保存に絞る）が正しいことの追加根拠。→ ★ **書き換えではなく出典の追加。** |
| **不便益の効果が個人特性で調整される** | ⚠️ **§4 の探索的 heterogeneity に影響しうる** | ★ [P127] [P128] に続く **3 本目の独立収束**。⚠️ **ただし [P171] は N=32・仮説生成なので、重みは 3 本目として最も軽い。** |

### ⚠️ §4 / §5 について本ラウンドが **判断しないこと**

- ★ **「不便益 HCI である」という自己規定を維持するか、Physical Anchor 実装まで留保するか**は研究者判断である。
  ★ 本ラウンドが出せるのは **「現行実装では定義の条件 1 を満たさない」という事実**までである。
- ★ **Gate H の autonomy に TENS を採用するか**も研究者判断である。★ 本ラウンドが出せるのは
  **「候補が 1 つあり、著者自身が初期版だと留保している」**までである。

---

## ★ 自己点検

- [x] **反証 angle を含めたか** — ★ angle ⑦ を独立に置いた。★ さらに「GSE の理論的立場は正当だ」側
  （reflective design 一致）も **同じ 3 票フィルタにかけ、カード 9 で ludic 側の外挿を落とした。**
- [x] **温度が分かれているか** — ★ RQ-4b / RQ-4d は **確定**、RQ-4c は **確定（設計論として）**、
  RQ-4a は **語彙は確定・効果は判定不能**、RQ-4e は **確定かつ GSE に不利**。★ **平均化していない。**
- [x] **`判定不能` を丸めていないか** — ★ **U-1 を丸めずに残した。** ★ [V88] 付録の N も「読めなかった」と書いた。
  ★ [P104] の頁 161 の矛盾も「未検証」と書いた。
- [x] **否決リストを残したか** — ★ **3 件。票と理由を (i)/(ii)/(iii) で分けて記載。**
  ⚠️ **3 件とも GSE に有利な主張である**（★ 対称性は「有利を落とし不利を残す」方向）。
- [x] **provisional と active を取り違えていないか** — ★ **一次全文を自読できた 11 本のみ `active`**。
  ★ **[P104] は昇格できなかったことを明記した**（★ 昇格したい誘惑を退けた）。
  ★ **[P6] は書誌未検証なので active → provisional に落とした。**
- [x] **既出 key を新規扱いしていないか** — ★ **20 個の key を照合し、既出は [P113] と [P104] の 2 件だけであることを実測。**
  ★ 両方とも新規登録せず既存行を更新し、[P113] については「足す別の主張」を 3 点で明示した。
- [x] **理論の定義を原典の逐語で取ったか** — ★ **autonomy = [P178] の一次逐語**（二次記述で代用していない）／
  **不便益 = [P170] [P172] [P171] の一次**／**reflective design = [P183] の一次**／
  **informative art / slow technology = [P113] の一次**／**ludic = [P184] の一次**。
  ⚠️★★★ **唯一 [P104] Slow Technology だけは一次に到達できず、査読二次からの引用逐語 2 本で代用した。
  これは「定義として使えるが、原典逐語ではない」と明記した。**
- [x] **data-privacy 規約** — ★ **キーストローク内容・NDJSON セッションログを検索クエリにも外部送信にも
  一切含めていない。** 検索は理論名・著者名・論文タイトルのみ。
