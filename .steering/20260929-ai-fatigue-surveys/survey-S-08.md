# S-08 AI 疲労の測定の一覧（＋ N-07）—— 事実

> 取得日: 2026-09-29（日本時間。検索 21:46＝JSON の executed。本文の確認はその後）。手順は `design.md` §3（尺度の検索の前に固定）。
> ★ このファイルは事実だけを書く（論文・資料に書いてあること）。COSMIN の評価と判定に関わる記述は別のファイル（`survey-S-08-ai-judgments.md`）にある。
> ⚠️ 尺度の項目文は書かない（項目番号・下位尺度・AI が入るかだけ）。
> 生の結果（書誌だけ）: `evidence/S-08/s08_results_2026-09-29.json`。スクリプト: `evidence/S-08/search_scales.py`。
> AF001 の本文は、研究者の Downloads にある出版社版 PDF を平文にし、サブエージェント（Sonnet）が項目を抜き出したものを、メインが該当箇所と Table 1 の頁の画像で確かめた。

## 1. 検索記録（尺度の開発・検証）

| 情報源 | 検索式 | 総件数 | 目で見た範囲 | 当たった尺度の開発・検証 |
|---|---|---|---|---|
| Europe PMC（題名・抄録） | `TITLE_ABS:("AI fatigue" OR "artificial intelligence fatigue" OR "generative AI fatigue" OR "ChatGPT fatigue" OR "AI-induced fatigue" OR "AI-related fatigue" OR "chatbot fatigue" OR "GenAI fatigue" OR "AI exhaustion" OR "AI burnout") AND TITLE_ABS:(scale OR questionnaire OR inventory OR instrument OR psychometric OR validation OR "factor analysis")` | 2 | 全件 | AF001 の前刷り（PsyArXiv, doi:10.31234/osf.io/kp7zs_v1） |
| Semantic Scholar（一括検索） | 同じ語を `\|` と `+` で | 6 | 全件 | AF001・AF009 |
| Crossref（`query.title`・関連度順） | `AI fatigue scale`／`AI fatigue questionnaire`／`generative AI fatigue scale` | —（関連度検索で件数は意味を持たない） | 各上位 50 件の題名 | AF001 とその前刷り |
| OpenAlex（`search`） | 上と同じ語（OR・AND） | 350 | 関連度の上位 200 件の題名（AI の語と疲労の語を両方含むもの 24 件を見た） | AF001・その前刷り・ResearchBox 6748 の写し（Zenodo） |
| Semantic Scholar（AF001 を引く論文） | doi:10.1016/j.chbr.2026.101186 の citations | 5 | 全件 | 無し（翻訳版・再検証の論文は無い。5 件は AI への態度・批判的思考の尺度・適応的業績・教育の成果物・情動調整の総説） |

- OpenAlex は、S-12 の英語の検索（21:21）とその直後の再試行では 503 だったが、S-08 の検索（21:46）では応答した。
- 題名に AI の語と疲労の語を含み、尺度の開発・検証ではない記録（概念の提案・総説・AI が疲労を検知する道具など）は §5 に書いた。

## 2. AI に向けた疲労の測定（項目文・定義・教示に AI が入るもの）

| 研究 | 測定 | 項目数・下位尺度 | 回答形式 | AI への向け方 | 標本（国・N） | 報告された信頼性 | 構造の検証 | 読んだ範囲 |
|---|---|---|---|---|---|---|---|---|
| **AF001** Lau ほか 2026（CHB Reports） | AI Fatigue Scale | **15 項目**・4 下位尺度（認知的過負荷 項目 1〜4・情動的緊張 5〜7・行動の回避と離脱 8〜11・身体・感覚の消耗 12〜15）＋高次因子。得点は 4 下位尺度の平均の平均 | 5 件法（1 = Strongly disagree〜5 = Strongly agree） | 前文が「AI での経験」を問い、**15 項目すべてに AI（AI・AI tools・AI models・AI outputs など）が入る**（Table 1 の頁の画像で確認） | 米国（Prolific）300（研究 2・EFA）／290（研究 3・CFA）、シンガポール 122（研究 4・再検査） | α: 研究 2 全体 .90（下位 .81〜.89）、研究 3 全体 .92（下位 .85〜.90）。合成信頼性 ρc（下位）.85〜.90。再検査 ICC(2,1) 全体 .65 [.53, .74]・下位 .54〜.71（2 週間） | EFA（研究 2）→ CFA（研究 3）: 高次モデル CFI .98・TLI .98・RMSEA .05・SRMR .04 | 本文（出版社版 PDF） |
| **AF009** Miranda ほか 2025（IEEE SCOReD） | AI 誘発疲労（探索的） | 29 項目から **25 項目**・3 因子（認知・情動の疲労／技術の明瞭さの疲労／受動的疲労）・説明率 46.5% | 5 件法 | 抄録は「AI の道具を学業で使うときの疲労」を問うとする。項目文は未確認 | フィリピン（パンパンガ州の高等教育機関）594（2025–26 年度の第 1 学期） | 「許容できる内的一貫性」（抄録。数値なし） | EFA（主因子法・バリマックス回転）のみ | 抄録 |
| **AF005** Zhao & Liu 2026（Front Psychol） | AI の誤情報への疲労・AI のプライバシーへの疲労（上位の概念は「AI 認知疲労」） | **8 項目・8 項目**（Choi ほか 2018 のプライバシー疲労の尺度から翻案） | 7 件法 | **16 項目すべてに AI が入る**（本文の表 2 で確認） | オンライン調査（Wenjuanxing・SNS で配布）有効 426。国は本文の範囲で明示が見つからない | α .910・.899／CR .926・.918／AVE .610・.585 | 測定モデル（PLS-SEM）。負荷量 .680〜.843・.703〜.812。HTMT で弁別を確認。適合度は SRMR だけを報告 | 本文（PMC） |
| **AF008** Soriano ほか 2026（IAES IJ-AI） | 「全般的な疲労の水準」（9 構成概念の 1 つ） | **3 項目**（出典として精神的疲労の測定の総説と Kim & Lee 2024 を挙げる） | Likert | 定義が「AI の長い・頻繁な利用から生じる心身の消耗」（表 1）。項目文は本文に無い | フィリピン 388（2024 年 11〜12 月・Messenger の紹介で募集） | 報告なし | 報告なし | 本文（出版社の PDF） |
| **AF011** Shalu ほか 2025（Annals of Neurosciences） | 意思決定疲労 | 尺度得点ではなく、項目ごとの相関の表で示す（精神的消耗・選択肢の多さ など）。出典・項目数の記載なし | Likert | 項目の一部に AI が入る（表の行の見出しで確認） | インド（デリー首都圏）500 | 報告なし | 報告なし | 本文（PMC） |
| AF002・AF003 Yang ほか（IJIM 2025・CHB 2026） | 生成 AI の不確実さに関わる疲労（DB の記述） | 未確認 | 未確認 | 未確認 | 未確認 | 未確認 | 未確認 | 抄録も取れていない（09-28 も書誌だけ） |
| Chung & Kwon 2025（EIT）【S-02 #6】 | プライバシー疲労 | 未確認（本文の表が取り出せない） | 5 件法 | 本文は「全項目に ChatGPT を組み込んだ」と書く（MBI-GS から翻案） | 韓国の学部生 695 | α>0.6・CR>0.7（全構成概念についての記述だけ） | PLS-SEM の測定モデル | 本文（出版社の HTML） |
| Kang & Li 2025（JBC）【S-02 #7】 | AI 疲労 | 未確認 | 未確認 | 抄録は「AI 疲労」を構成概念として立てる | 韓国の AI 利用者 212 | 未確認 | SEM | 抄録 |
| Asmi ほか 2026（JEIM）【S-02 #1】 | 意思決定疲労 | 未確認 | 未確認 | 抄録からは分からない | 知識労働者 460（国は抄録に無い） | 未確認 | CB-SEM | 抄録 |
| IEEE DataPort の 2 件【S-02 §5】 | 「AI Fatigue（AIF）」7 指標（15000 件の方）・「AI Fatigue Index」 | 7 指標（ほかに検証の負担 5 など） | Likert | 構成概念名に AI | 由来の記載なし | — | — | ページの説明 |

- ★ AF001 の 15 項目は本文の **Table 1** にあり、前文・採点の方法も同じ表にある。補足資料の **Table S6** は 30 項目版（本文 §4 の記述）。
- ★ 翻訳版: AF001 の本文に翻訳版への言及は無い（開発は英語）。AF001 を引く論文（5 件）にも翻訳版・再検証は無い。ほかの測定にも翻訳版の報告は見当たらない。

## 3. AF001 の妥当性の検証（本文に書いてあること）

- **内容妥当性**（研究 1）: 技術の利用に関わる既存の 5 尺度から初期 60 項目 → 上級研究者 2 名と大学院生 1 名の検討で 32 項目 → 構成概念を知らない学部生 5 名が 4 次元に割り当て（psa・csv の基準 .72・.51）→ 30 項目（全体 psa=.97・csv=.95）。可読性は Flesch-Kincaid 6.43。対象となる利用者への面接・認知面接は本文に無い。
- **構造**: 研究 2（N=300）の EFA で 30 → 15 項目・4 因子（負荷量 .59〜.91・説明率 64%。並行分析は 5 因子を示唆し、理論に基づき 4 因子を採った）。研究 3（N=290）の CFA で一次 4 因子と高次モデルを比べ、差は有意でなく（Δχ²(2)=5.60, p=.06）、高次モデルを採用。
- **測定の不変性**（研究 3）: 性別（女性 147・男性 143）で configural・metric・scalar・strict（ΔCFI −.007〜.000）。頑健 χ² の差は configural→metric で p=.008。
- **収束**（研究 3）: Fatigue Assessment Scale r=.63・Chalder Fatigue Scale r=.52・Multidimensional Fatigue Inventory r=.59・Screen Fatigue Scale r=.60・Social Media Fatigue Scale r=.63・AI テクノストレス（複雑さ・不確実さ）r=.46・（過負荷・侵入）r=.18。
- **弁別**（研究 3）: AI 利用での批判的思考 r=.05・AI 依存 r=.11・AI への愛着 r=−.17。Fornell–Larcker の基準を満たすと著者は書く。
- **基準・増分**（研究 3）: 現在の AI 利用の頻度（単一項目）β=−.27、今後 3 か月に利用を減らす意図（単一項目）β=.33。既存の疲労尺度と AI テクノストレスを入れた後の ΔR² は 8.38%・2.62%。
- **再検査**（研究 4）: シンガポールの若年成人 122 名（心理学実験を告知する Telegram のチャンネルで募集・平均 24.15 歳）、2 週間（±2 日）。著者は「中程度の時間的安定性」と書く。研究 4 の α は本文に無い。
- **事前登録・公開**: 本文は「研究 2〜4 は事前登録した設計・分析・標本計画に従った」と書く（登録番号は本文に無い）。IRB は IRB-25-197-A159 (925)。データは ResearchBox 6748。
- **著者が書いた限界**: 横断・相関のデータ／英語圏・一般の生成 AI 利用者が中心で、文化・言語をまたぐ不変性は未検証／基準変数が単一項目の自己報告。

## 4. N-07: AF001 の補足資料・ResearchBox 6748

| 何 | 値 | 出どころ |
|---|---|---|
| 15 項目の場所 | 本文 Table 1（前文・5 件法・採点の方法つき） | 出版社版 PDF の 6 頁 |
| 30 項目版 | 補足資料 Table S6 | 本文 §4 |
| 事前登録 | 研究 2: AsPredicted #249,222（2025-09-27）・研究 3: #249,751（2025-10-01）・研究 4: #253,505（2025-10-23）。研究 1 は無し | ResearchBox 6748 のページ |
| データ | `AI_Fatigue_Study2.csv`・`Study3.csv`・`Study4.csv`（2026-06-28） | 同上 |
| 資料・コード | ResearchBox に「Materials」「Code」の欄のファイルは無い | 同上 |
| 公開の開始 | 2026-06-29。ResearchBox の内容は CC BY 4.0。写しが Zenodo（doi:10.5281/zenodo.21053220） | 同上 |
| 論文の利用許諾 | CC BY-NC-ND 4.0（出版社版の公開 2026-06-26） | Crossref |
| 補足資料そのもの（Table S1〜S13） | 取得していない（ScienceDirect はスクリプトを弾く） | — |

## 5. AI の文脈の研究で使われた一般的な疲労・燃え尽きの測定（項目は AI に触れない）

| 測定 | 使った研究 | 出どころ |
|---|---|---|
| Fatigue Assessment Scale（10 項目） | AF001（収束）・DB の AF028 は尺度の原著 | AF001 本文 |
| Chalder Fatigue Scale（11 項目）・Multidimensional Fatigue Inventory | AF001（収束）。AF004 は MFI-20 の認知疲労の下位尺度（09-28 の評価版の記述・本文は未読） | AF001 本文／評価版 |
| Screen Fatigue Scale・Social Media Fatigue Scale | AF001（収束） | AF001 本文 |
| Maslach Burnout Inventory（6 項目） | Kim & Lee 2024（S-02 #9） | 本文 |
| MBI-Student Survey（15 項目） | Wu 2026（S-12） | 本文 |
| Burnout Assessment Tool（BAT-22） | The Cognitive Costs of AI: Burnout and Executive Functioning in Higher Education（Mind & Society 2025, doi:10.56011/mind-mri-143-20259・大学生 401・AI 利用者 332 と非利用者 69 を比べる） | 抄録 |
| デジタル燃え尽き尺度（24 項目）・デジタル疲労（6 項目） | Honggang ほか 2026（S-02 #2） | 本文 |
| 公衆衛生協会ストレスチェックリスト短縮版の疲労・身体反応 | Cureus 2025 チャットボット（S-12） | 本文 |
| 精神的・身体的疲労の単一項目（5 件法） | AI-Echo RCT（S-12） | 補足資料 |
| NASA-TLX（作業負荷） | Omon ほか 2025（S-12） | 抄録 |
| Zoom Exhaustion & Fatigue Scale | DB の AF026（尺度の原著・AI ではない） | DB |

## 6. 尺度ではないが、AI 疲労の測定・定義に触れる記録（§1 の検索で当たったもの）

| 記録 | 書いてあること |
|---|---|
| Synthetonia: Tonal Strain as a Candidate Facet of AI Fatigue（Zenodo 2026・doi:10.5281/zenodo.22566309 ほか版違い 2 件） | 立場表明の論文。既存の尺度は「生成物の量・検証の負担・プロンプトの反復」というやり取りのコストを測るとし、会話 AI の文体の単調さへの飽き（Synthetonia）を別の源として提案。尺度の開発は今後の課題として挙げる |
| A Control-Theoretic Approach to GenAI Fatigue（Zenodo 2025・doi:10.5281/zenodo.17772700） | 「GenAI Fatigue」を、長い多回の対話で LLM の想起・文脈の忠実さが落ちる現象（人ではなくモデルの側）の名として使う |
| Too Much, Too Fast: Understanding AI Fatigue in the Digital Acceleration Era（IJAHSS 2025・doi:10.56734/ijahss.v6n8a7） | 叙述的な文献レビュー。AI 疲労をテクノストレス・認知的過負荷・情動的消耗の組み合わせとして概念化 |
| Digital-Age Psychosocial Strain: A Systematic Literature Review …（IJRISS 2026・doi:10.47772/ijriss.2026.102400020） | Scopus・WoS・ScienceDirect の系統的レビュー（2022〜2026 年の 24 研究）。テクノストレス・デジタル燃え尽き・AI 疲労などの構成概念の次元と測定の方法を整理 |
| RecalibrateGPT: AI Fatigue Resilient Conversational Interfaces（arXiv 2026・doi:10.48550/arxiv.2609.00506） | 題名だけ（AI 疲労に配慮した対話の画面） |
| Anti-Design Approach in Countering AI Fatigue（International Design Journal 2026） | 題名だけ |
| AI Fatigue: Views From the Trenches（Editorial Office News 2026） | 題名だけ |

## 7. 数のまとめ

- AI に向けた疲労の測定: 10 種類（§2）。うち、開発・検証の論文があるもの 1（AF001）、探索的因子分析だけのもの 1（AF009）、既存の尺度を AI に向けて翻案したもの 2（AF005・Chung & Kwon）、項目数だけ・項目ごとのもの 2（AF008・AF011）、測定を確かめられていないもの 3（AF002/AF003・Kang & Li・Asmi）、由来の記載のないデータセット 1。
- 項目文・前文に AI が入ることを一次で確かめたもの: AF001（15/15）・AF005（16/16）。本文の記述で確かめたもの: Chung & Kwon。
- 翻訳版: 0。
- AI の文脈の研究で使われた一般的な測定: 11 種類（§5）。
