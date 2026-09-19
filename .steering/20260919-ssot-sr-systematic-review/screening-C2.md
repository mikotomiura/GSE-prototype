# ふるい分けの記録 —— C2

> 候補の定義（protocol.md §1）: **系とのやり取りが人に生む負担として、解釈と説明要求（出力の解釈・検証・説明を求められること）を記述・計上すること**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 653 |
| 段 1 で採った | 228 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 0 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 2 |
| 段 2 の判定（メインの訂正の後） | 該当 2 ／ 部分 0 ／ 非該当 0 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 107 |
| 1 回目の中断の前の段 2（抄録のみ・参考） | 121 |

## 結論

★ **既出**（該当: C2-0277 [P398]・C2-0413 [P399]）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C2-0277 | 該当 | 本文 | We identified three recurring gaps: (i) lack of trust in outputs, (ii) persistent verification burden, and (iii) requiring multiple tools. | Abstract | 系の出力の検証を求められる負担を利用者研究で記述 | メインが直接照合（1 回目の段 2 は抄録のみ） | ★ メインが本文で照合 |
| C2-0413 | 該当 | 本文 | We term this alignment debt: the user-side burden that arises when AI systems fail to align with cultural, linguistic, infrastructural, or epistemic contexts. | Abstract | 利用者側の検証の負担を計上・実測 | メインが直接照合（1 回目の段 2 は抄録のみ） | ★ メインが本文で照合 |

## 参考: 1 回目の中断の前の段 2（C2・⚠️ すべて抄録のみの判定）

- 96 件（`stage2_out_C2_1/2.jsonl`）。★ 該当 38 件。★ メインが本文で確かめたのは C2-0277・C2-0413 の 2 件だけである（上の表）。

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C2-0002 | 2024 | Participatory Censorship With Illusory Empowerment: Algorithmic Folklore and Interpretive Labor beyond Fandom | 10.1177/20563051241295800 | アルゴリズム民話とinterpretive laborの概念を導入しファンの検閲参加における解釈労働を民族誌的に論じる | 未実施（逸脱 2） |
| C2-0004 | 2021 | Interpretation Machines: Contradictions of ‘Artificial Intelligence’ in 21st-Century Capitalism |  | AIによる自動化を『解釈労働の機械化』として論じるマルクス主義的分析 | 未実施（逸脱 2） |
| C2-0005 | 2026 | Artificial intelligence and the library as Third Place: cognitive automation and the reconfiguration of labour | 10.1108/jd-11-2025-0346 | AIが図書館業務のroutine interpretive labourを減らすと論じる(逆向きの可能性があり段2で確認) | 未実施（逸脱 2） |
| C2-0007 | 2026 | Reconceptualizing customer experience co-creation and service delivery in the age of artificial intelligence | 10.1080/19368623.2025.2611513 | AIが接客サービス共創におけるinterpretive laborを再配分すると論じる概念論文 | 未実施（逸脱 2） |
| C2-0009 | 2025 | The Evolution of Digital Pathology in Infrastructure, Artificial Intelligence and Clinical Impact | 10.11106/ijt.2025.18.1.6 | AIが病理医のinterpretive workを増強すると論じるレビュー | 未実施（逸脱 2） |
| C2-0010 | 2025 | Algorithmic decision-making in organizations: a systematic review toward an integrated tension alignment frame… | 10.1108/omj-11-2024-2342 | 組織におけるアルゴリズム意思決定の系統レビューでinterpretive laborを媒介要因として明示的に位置づける | 未実施（逸脱 2） |
| C2-0014 | 2011 | A transportable assessment protocol for prescribing youth psychosocial treatments in real-world settings: Redu… | 10.1037/a0025176 | 自己報告尺度によりadministration and interpretation burdenを低減するアルゴリズムベースの評価法を提案・実測 | 未実施（逸脱 2） |
| C2-0018 | 2026 | Building health-literate artificial intelligence | 10.1038/s41562-026-02595-1 | 抄録なし、題名『ヘルスリテラシーを持つAI』はAI出力の患者側理解負担に関わりうる | 未実施（逸脱 2） |
| C2-0019 | 2025 | Artificial Intelligence and Social Research: Methods, contexts, imaginaries | 10.69146/55440895 | LLMが質的研究のinterpretive workを支援しつつinterpretive competenceの侵食・interpretive burdenに関わる懸念を論じる | 未実施（逸脱 2） |
| C2-0020 | 2026 | Automating the Past: Artificial Intelligence and the Next Frontiers of Digital History | 10.3366/ijhac.2026.0361 | AIモデルが歴史家のinterpretive workにどう関わるかを論じる基調講演論文 | 未実施（逸脱 2） |
| C2-0021 | 2026 | Before The Leap: Collective Sensemaking Of Artificial Intelligence In Digital Platform Ecosystems |  | 起業家がAIを集合的センスメイキングするプロセスをinterpretive workとして分析する実証研究 | 未実施（逸脱 2） |
| C2-0024 | 2026 | A New Multi-Class Framework for Electrocardiogram Arrhythmia Classification Using Artificial Intelligence | 10.1109/imcet69180.2026.11503730 | 臨床医のinterpretation burdenを増やさないことを明示的な設計目標とする心電図AIの論文 | 未実施（逸脱 2） |
| C2-0026 | 2026 | CONTINUING MEDICAL EDUCATION AND ARTIFICIAL INTELLIGENCE INTEGRATION IN CLINICAL PRACTICE: A CASE STUDY OF PHY… |  | 医師のAI統合をinterpretive judgment・interpretive burdenとして質的に分析する事例研究 | 未実施（逸脱 2） |
| C2-0027 | 2026 | Knowing Enough to Be Dangerous: The Problem of “Artificial Certainty” for Expert Authority When Using AI for D… | 10.1287/orsc.2023.18224 | AI生成表象への対応をプロセス専門家のinterpretive workとして再概念化する比較研究 | 未実施（逸脱 2） |
| C2-0028 | 2026 | Multimodal artificial intelligence in capsule endoscopy: Integrating video and sensor data for advanced gastro… | 10.37126/aige.v7.i1.117988 | カプセル内視鏡診断でAI導入前のinterpretive burdenを明示し、AIによる低減を検証するレビュー | 未実施（逸脱 2） |
| C2-0029 | 2025 | Can AI Lend a Hand? Integrating Artificial Intelligence into Education Systematic Reviews and Meta-Analyses | 10.35542/osf.io/wu64b_v1 | AI支援の系統レビューでcomplex interpretive workを人間コーダーに残す設計を提案し実証する | 未実施（逸脱 2） |
| C2-0030 | 2025 | Can AI Lend a Hand? Integrating Artificial Intelligence into Education Systematic Reviews and Meta-Analyses |  | 0029と同一研究のプレプリント版 | 未実施（逸脱 2） |
| C2-0034 | 2026 | Operationalising uncertainty: the automation of threat knowledge and situational awareness | 10.1093/secdia/xhag010 | 自動化された脅威検知システムがオペレーターに生む終わりのないinterpretive labourをエスノグラフィックに実証 | 未実施（逸脱 2） |
| C2-0037 | 2026 | EFFECTIVE ACT: ABOLITION OF "USER" AND INAUGURAL CASE Phase X Lexical Intervention · Airlock Reclassification … | 10.5281/zenodo.19014634 | 『user』という語がプラットフォームによる意味的労働(interpretive work)の搾取を隠すと論じる(非学術的な自費出版的文書で質に留保) | 未実施（逸脱 2） |
| C2-0039 | 2026 | Anthropology – Digital Ethnography and Algorithmic Thick Description | 10.4324/9781003790358-8 | デジタル民族誌でAIとの協働によるinterpretive workの分担を論じる | 未実施（逸脱 2） |
| C2-0040 | 2026 | The transparency trap: Generative AI and the rise of interpretive load | 10.1002/rev3.70139 | 生成AI関連ポリシーが学生にinterpretive load(認知・情動・倫理・手続き的労働)を課すと明示的に論じ操作化する | 未実施（逸脱 2） |
| C2-0042 | 2026 | Calibration labour: making careers machine-legible under algorithmic hiring | 10.1080/1369118x.2026.2715575 | アルゴリズム採用がinterpretive labourを求職者側へ再配分し機関の説明責任を解除すると明示的に論じるエスノグラフィー | 未実施（逸脱 2） |
| C2-0043 | 2026 | Cognitive Integrity: A Framework for Understanding Interpretative Autonomy in Algorithmically Mediated Environ… | 10.5281/zenodo.19916093 | AIが人の内面で行っていた解釈作業を代替することを扱うCognitive Integrityの枠組み(自費出版的シンセシスで質に留保) | 未実施（逸脱 2） |
| C2-0044 | 2026 | Cognitive Integrity: A Framework for Understanding Interpretative Autonomy in Algorithmically Mediated Environ… | 10.5281/zenodo.19916092 | 0043と同一研究の別版 | 未実施（逸脱 2） |
| C2-0048 | 2009 | High-performance computer aided detection system for polyp detection in CT colonography with fluid and fecal t… | 10.1117/12.811654 | CADシステムが仮想内視鏡診断のinterpretation burdenを低減すると明示するレビュー | 未実施（逸脱 2） |
| C2-0055 | 2025 | The Architecture of Judgment: AI and the Drift of Judicial Character | 10.21428/cb6ab371.8d74a38c | AI助言システムが司法判断のinterpretive laborを再構成し裁判官の徳性発達に影響すると論じる | 未実施（逸脱 2） |
| C2-0056 | 2026 | The Mirage of Safety: Unpacking the "AI Guard-Down Effect" on Cybersecurity Vigilance and Privacy Behaviors |  | AIエージェントへのinterpretive laborの委任がVerification Displacementを介し人間の警戒心を蝕むと理論化・実験設計する | 未実施（逸脱 2） |
| C2-0059 | 2026 | From Prediction to Horizon: Clinicians' Negotiations of AI‐Driven Personal Prognoses in Clinical Practice | 10.1111/1467-9566.70209 | AI予後予測が臨床医に新たなinterpretive workを生むとエスノグラフィックに実証する | 未実施（逸脱 2） |
| C2-0060 | 2026 | Listening in the Afterlife of AI: Interpretive Infrastructures, Communicative Overreliance and Synthetic Conse… | 10.2139/ssrn.7123658 | 抄録なし、題名『Interpretive Infrastructures, Communicative Overreliance』は主題合致と判断 | 未実施（逸脱 2） |
| C2-0061 | 2026 | Mobile AI as Relational Infrastructure: Translating Meaning and Belonging in International Student Onboarding | 10.3390/aieduc2020010 | モバイル生成AIが留学生対応でtranslational, emotional, interpretive laborを再配分すると論じる | 未実施（逸脱 2） |
| C2-0064 | 2026 | Authorial Positioning and Creative Agency in AI-Mediated Music | 10.1177/20594364261423866 | AI媒介音楽制作で創作者が著作性を主張するために継続的interpretive labourを要すると実証する | 未実施（逸脱 2） |
| C2-0065 | 2026 | Acceptable English, Vanishing Voice: AI Polishing and the South- North Politics of Academic Style | 10.1080/02560046.2026.2714805 | AIによる学術英語の均質化を論じ、査読・評価にinterpretive labourを要求すべきと主張する論説 | 未実施（逸脱 2） |
| C2-0071 | 2026 | Intimacy as Service, Harm as Externality: Critical Perspectives on AI Companion Platform Accountability |  | AIコンパニオン利用者が構造的支援なくharm mitigationの全負担とinterpretive laborを負うと実証するインタビュー研究 | 未実施（逸脱 2） |
| C2-0072 | 2026 | Intimacy as Service, Harm as Externality: Critical Perspectives on AI Companion Platform Accountability | 10.48550/arxiv.2604.06381 | 0071と同一研究の別版 | 未実施（逸脱 2） |
| C2-0073 | 2025 | WITHDRAWN | 10.31235/osf.io/gzquh_v1 | BIツールが組織内のinterpretive labourを再配分すると論じる(題名がWITHDRAWNと表示され撤回の可能性あり、質に留保) | 未実施（逸脱 2） |
| C2-0074 | 2026 | Evaluating Epistemic Guardrails in AI Reading Assistants: A Behavioral Audit of a Minimal Prototype |  | AI読解アシスタントがinterpretive displacement(意味づけ作業の読者からシステムへの移転)を起こすかを行動監査で測定する | 未実施（逸脱 2） |
| C2-0075 | 2026 | Evaluating Epistemic Guardrails in AI Reading Assistants: A Behavioral Audit of a Minimal Prototype | 10.48550/arxiv.2604.27275 | 0074と同一研究の別版 | 未実施（逸脱 2） |
| C2-0076 | 2026 | When AI Rewrites Practice: Epistemic Transformations in AI-Assisted Academic Writing and Practice-Based Music … | 10.2139/ssrn.6297815 | 抄録なし、題名『AIによる実践の書き換え:認識論的変容』はAI支援執筆の解釈的変化を扱うと判断 | 未実施（逸脱 2） |
| C2-0084 | 2025 | Generative AI, Researcher Reflexivity, and the Epistemic Politics of Qualitative Inquiry: Toward a Framework o… | 10.35542/osf.io/kz793_v1 | 生成AIが質的研究のinterpretive authorityを複雑化すると論じ、人間中心の解釈を保つ枠組みを提案する | 未実施（逸脱 2） |
| C2-0085 | 2026 | Co-Constructing AI Boundaries: Agency, Judgment, and Ethical Literacy in AI-Mediated Meaning-Making | 10.1177/23813377261476996 | 教員志望者がAIへinterpretive workを委任する度合いを相互作用トレースから実証的に分析する | 未実施（逸脱 2） |
| C2-0087 | 2026 | WrenchBuddy: A Governance Framework for Human-Centered Industrial AI Fault Diagnostics | 10.3390/machines14090984 | 産業AI故障診断ガバナンスでinterpretability burdenを定量指標として明示的に測定する | 未実施（逸脱 2） |
| C2-0089 | 2026 | Transformative phygital service research (TPSR): an agenda for future research | 10.1108/jsm-09-2025-0679 | フィジタルサービスにおけるagency・governance・interpretive labourの曖昧さを理論統合する概念論文 | 未実施（逸脱 2） |
| C2-0090 | 2026 | The Age of Intent in Practice: Intent-Native Systems as Cognitive Load Stewards in Real-World Domains | 10.5281/zenodo.18235358 | 意図ネイティブシステムがinterpretive burdenを低減する『認知負荷スチュワード』であるべきと規範的に論じる(自費出版シリーズで質に留保) | 未実施（逸脱 2） |
| C2-0091 | 2026 | The Age of Intent in Practice: Intent-Native Systems as Cognitive Load Stewards in Real-World Domains | 10.5281/zenodo.18235357 | 0090と同一研究の別版 | 未実施（逸脱 2） |
| C2-0094 | 2026 | Chasing RATs: Tracing Reading for and as Creative Activity |  | アルゴリズムフィード/AI要約が人間のinterpretive laborを圧縮・自動化することを論じ可視化ツールを提案する | 未実施（逸脱 2） |
| C2-0095 | 2026 | Chasing RATs: Tracing Reading for and as Creative Activity | 10.48550/arxiv.2603.11031 | 0094と同一研究の別版 | 未実施（逸脱 2） |
| C2-0097 | 2026 | “Hermeneutic burden” and clinical responsibility: a response to Sparrow et al. on explanation and machine lear… | 10.1007/s40592-026-00300-6 | Sparrow et al.のXAIによる臨床医への『hermeneutic burden』概念を批判的に検討し操作化する直接的な論文 | 未実施（逸脱 2） |
| C2-0099 | 2026 | Interpreting Ambient Digital Biomarkers in Aging-in-Place Care: A Contextual Framework (Preprint) | 10.2196/preprints.111064 | 在宅高齢者ケアの環境センシングAI出力を臨床家が個別参照点なしに解釈する困難を論じる | 未実施（逸脱 2） |
| C2-0104 | 2026 | From Triage to Intensive Care: A Qualitative Study of Nurses' Experiences with AI ‐Enabled Decision Support | 10.1111/nicc.70537 | AI搭載意思決定支援ツールのアラートを看護師が臨床判断と併せて解釈する負担(judgment under algorithmic pressure)を質的に扱う | 未実施（逸脱 2） |
| C2-0112 | 2026 | Reaction videos as “interpassive” aesthetic experiences: Understanding the meaning of diffuse media practices … | 10.1080/10714421.2026.2647307 | プラットフォームのアルゴリズム増幅下でのリアクション動画視聴を「委任された感情的・解釈的労働」として論じる | 未実施（逸脱 2） |
| C2-0118 | 2026 | Catch the Patient, Not the AI: Collective Sensemaking in an Online Health Community | 10.48550/arxiv.2608.07516 | 患者がAIで医療情報を解釈する際にAI出力に圧倒される負担やコミュニティでの検証行動を実証的に扱う | 未実施（逸脱 2） |
| C2-0120 | 2025 | Pixels and Weights : The Situated Work of Teaching Computers to See |  | コンピュータビジョン科学者がブラックボックス化した自システムの出力を共有的な解釈作業で意味づける実践を民族誌的に分析 | 未実施（逸脱 2） |
| C2-0123 | 2026 | Economic Autophagy under Superintelligence: A Structural Model of Systemic Over-Optimization and Institutional… | 10.5281/zenodo.18279321 | 超知能下でアルゴリズム制御された制度が人間の「解釈的労働」を消費すると明示的に論じ対抗策として解釈的インセンティブを提案する | 未実施（逸脱 2） |
| C2-0124 | 2026 | Economic Autophagy under Superintelligence: A Structural Model of Systemic Over-Optimization and Institutional… | 10.5281/zenodo.18257008 | C2-0123と同一内容の重複エントリ | 未実施（逸脱 2） |
| C2-0125 | 2026 | Economic Autophagy under Superintelligence: A Structural Model of Systemic Over-Optimization and Institutional… | 10.5281/zenodo.18257007 | C2-0123と同一内容の重複エントリ | 未実施（逸脱 2） |
| C2-0126 | 2026 | Economic Autophagy under Superintelligence: A Structural Model of Systemic Over-Optimization and Institutional… | 10.5281/zenodo.18276185 | C2-0123と同一内容の重複エントリ | 未実施（逸脱 2） |
| C2-0131 | 2026 | Platformised digital agriculture and technostress: implications for psychosocial occupational safety and healt… | 10.15159/ar.26.035 | プラットフォーム媒介型デジタル農業のtechnostressとして「不透明な出力下での解釈的負担」を4パターンの一つに明示的に位置づける | 未実施（逸脱 2） |
| C2-0136 | 2020 | How Secrets Behind Data Reshape the Model of Cancer Care | 10.1097/ncc.0000000000000799 | ビッグデータ/AIによる医療診断支援がデータの「解釈的負担」を医療者と患者双方にもたらすと明示的に述べる | 1 回目（抄録のみ） |
| C2-0140 | 2026 | Domesticating the Latent: How Topic Models Become Evidence across the Social Sciences | 10.6082/d9rmy-qwt77 | トピックモデルという計算系の出力を研究者が証拠へと変換する際の解釈作業を実証的コーパス分析で扱う | 1 回目（抄録のみ） |
| C2-0141 | 2026 | Catch the Patient, Not the AI: Collective Sensemaking in an Online Health Community | 10.31235/osf.io/bruhj_v1 | AI出力に圧倒される患者コミュニティのセンスメイキングを扱う研究(C2-0118の初期投稿版) | 未実施（逸脱 2） |
| C2-0142 | 2026 | Domesticating the Latent: How Topic Models Become Evidence across the Social Sciences | 10.6082/ywq02-8jq28 | C2-0140と同一論文の別バージョンで同理由により採用 | 1 回目（抄録のみ） |
| C2-0148 | 2026 | Automating RGT for Subjective Insight via Hybrid UI (HUI) Design |  | ハイブリッドUI(会話型+GUI)によるレパートリーグリッド技法自動化研究で分析時の実質的な解釈作業負担を明示的に課題設定する | 1 回目（抄録のみ） |
| C2-0158 | 2026 | Dynamic triage in hypertension: a quantitative framework for follow-up scheduling based on clinician heuristic… | 10.3389/fdgth.2026.1858572 | 家庭血圧モニタリング(mHealth)データが臨床医に求める解釈的作業負担の増大を明示的に扱う | 1 回目（抄録のみ） |
| C2-0159 | 2026 | EFFECTIVE ACT: ABOLITION OF "USER" AND INAUGURAL CASE Phase X Lexical Intervention · Airlock Reclassification … | 10.5281/zenodo.19014633 | プラットフォーム上の「ユーザー」概念批判の前衛的テキストで、時間・関心・解釈労働がプラットフォームに搾取される構図を論じる | 未実施（逸脱 2） |
| C2-0167 | 2024 | Exploring users’ algorithmic knowledge and reflexivity in a music streaming context: A critical realist approa… | 10.1177/13548565241277379 | Spotifyユーザーが推薦アルゴリズムの出力を解釈・内省するリフレクシビティ様式を批判的実在論で分析 | 1 回目（抄録のみ） |
| C2-0168 | 2024 | Algorithmic experiences of Netflix’s users in the Arab world: Implications for agency and social practice | 10.1177/13548565241301125 | Netflixユーザーがアルゴリズムと関わり解釈し抵抗するエージェンシーを社会構成主義的に分析 | 1 回目（抄録のみ） |
| C2-0169 | 2020 | User Perceptions of Algorithmic Decisions in the Personalized AI System:Perceptual Evaluation of Fairness, Acc… | 10.1080/08838151.2020.1843357 | パーソナライズAIシステムの決定を利用者が知覚・意味づけする過程と公正性・説明可能性への影響を検討 | 1 回目（抄録のみ） |
| C2-0170 | 2026 | The Algorithmic Mirror: Knowledge Creation and Self-Perception in Dating Applications | 10.1145/3772318.3790901 | 出会い系アプリの「アルゴリズムの鏡」に対するユーザーの解釈・戦略的対処と感情労働を分析 | 1 回目（抄録のみ） |
| C2-0171 | 2022 | D-BIAS: A Causality-Based Human-in-the-Loop System for Tackling Algorithmic Bias | 10.1109/tvcg.2022.3209484 | アルゴリズムバイアスを対話的に監査・是正する人間参加型ツールで、ユーザーが因果関係を解釈・検証する負担を伴う設計を扱う | 1 回目（抄録のみ） |
| C2-0174 | 2024 | Transparency in Algorithmic Decision-making: Interpretable Models for Ethical Accountability | 10.1051/e3sconf/202449102041 | アルゴリズム意思決定の透明性のため利用者が理解・検証し説明責任を果たす必要性を明示的に論じる | 1 回目（抄録のみ） |
| C2-0175 | 2023 | Identifying Explanation Needs of End-users: Applying and Extending the XAI Question Bank | 10.1145/3603555.3608551 | AIシステム利用時のエンドユーザーの説明ニーズをXAI Question Bankを用いて実証的に調査する研究 | 1 回目（抄録のみ） |
| C2-0176 | 2023 | “Big data see through you”: Sexual identifications in an age of algorithmic recommendation | 10.1177/20539517231215358 | Douyinのアルゴリズムによる性的指向分類に対する視聴者・投稿者の解釈・省察経験を分析 | 1 回目（抄録のみ） |
| C2-0177 | 2020 | Impact of Algorithmic Decision Making on Human Behavior: Evidence from Ultimatum Bargaining | 10.1609/hcomp.v8i1.7462 | アルゴリズム決定支援システムにおける説明の提示が利用者の解釈・信頼・協力行動に与える影響を実験的に検証 | 1 回目（抄録のみ） |
| C2-0178 | 2021 | The Invisible Cage: Workers’ Reactivity to Opaque Algorithmic Evaluations | 10.1177/00018392211010118 | 不透明なアルゴリズム評価システムの基準をフリーランサーが解読できず対処に苦慮する負担を実証的に分析 | 1 回目（抄録のみ） |
| C2-0179 | 2022 | Understanding user sensemaking in fairness and transparency in algorithms: algorithmic sensemaking in over-the… | 10.1007/s00146-022-01525-9 | OTTプラットフォームのアルゴリズムの公正性・透明性に関するユーザーのセンスメイキングを扱う(題名から判断、抄録なし) | 1 回目（抄録のみ） |
| C2-0180 | 2016 | Algorithmic Authority: the Ethics, Politics, and Economics of Algorithms that Interpret, Decide, and Manage | 10.1145/2851581.2886426 | アルゴリズムが解釈・決定・管理する権威性の倫理・政治・経済をCHIで論じる(題名から判断、抄録なし) | 1 回目（抄録のみ） |
| C2-0181 | 2021 | "How advertiser-friendly is my video?": YouTuber's Socioeconomic Interactions with Algorithmic Content Moderat… | 10.1145/3479573 | YouTubeアルゴリズムモデレーションの不透明性に対しYouTuberが実践知で解読・対処する負担を分析 | 1 回目（抄録のみ） |
| C2-0182 | 2025 | Thinking through Prompting: Cognitive Mediation in Human–AI Interaction | 10.1145/3746175.3747192 | 生成AIへのプロンプト入力を認知的媒介・解釈的交渉として捉え、ユーザーの認知労働を論じる | 1 回目（抄録のみ） |
| C2-0183 | 2017 | Analytics in action: users and predictive data in the neonatal intensive care unit | 10.1080/1369118x.2017.1291701 | NICUにおける予測分析データと利用者の関わりを扱う(題名から判断、抄録なし、利用者による予測データの解釈的関与が想定される) | 1 回目（抄録のみ） |
| C2-0184 | 2021 | Outcome-Explorer: A Causality Guided Interactive Visual Interface for Interpretable Algorithmic Decision Makin… | 10.1109/tvcg.2021.3102051 | アルゴリズム意思決定の説明が非専門ユーザーに理解されにくい課題を扱う因果ベース対話型インターフェース研究 | 1 回目（抄録のみ） |
| C2-0191 | 2020 | Good Explanation for Algorithmic Transparency | 10.2139/ssrn.3503603 | AIシステムの「良い説明」の特徴を定義し、ユーザーの理解・信頼への影響を大規模実験で検証 | 1 回目（抄録のみ） |
| C2-0196 | 2018 | 'Datafied' reading: framing behavioral data and algorithmic news recommendations | 10.1145/3240167.3240194 | 行動データとアルゴリズム推薦をユーザーがどう解釈し意味づけたかをGoffmanのフレーム分析で検討 | 1 回目（抄録のみ） |
| C2-0199 | 2018 | Explaining Explanations: An Overview of Interpretability of Machine Learning | 10.1109/dsaa.2018.00018 | MLの解釈可能性・説明可能性(XAI)概念を包括的に整理しユーザーへの説明の意義を論じる | 1 回目（抄録のみ） |
| C2-0200 | 2024 | Categorical and Continuous Features in Counterfactual Explanations of AI Systems | 10.1145/3673907 | 反実仮想説明がAIシステムの意思決定理解に与える効果をユーザー実験で検証 | 1 回目（抄録のみ） |
| C2-0202 | 2017 | The human touch: How non-expert users perceive, interpret, and fix topic models | 10.1016/j.ijhcs.2017.03.007 | 非専門家ユーザーによるトピックモデルの解釈・修正を明示的に調査(強く合致) | 1 回目（抄録のみ） |
| C2-0205 | 2023 | SkinGPT-4: An Interactive Dermatology Diagnostic System with Visual Large Language Model | 10.1101/2023.06.10.23291127 | 皮膚科診断AIで医師の読影負担・労力(labor-intensive)を明示的に述べる(境界事例) | 1 回目（抄録のみ） |
| C2-0208 | 2025 | From algorithm aversion to AI dependence: Deskilling, upskilling, and emerging addictions in the GenAI age | 10.1002/arcp.70008 | GenAIへの認知労働委任(Division of Cognitive Labor)とCognitive Surrenderを明示的に理論化(強く合致) | 1 回目（抄録のみ） |
| C2-0247 | 2022 | Social Media Profiling Continues to Partake in the Development of Formalistic Self-Concepts. Social Media User… | 10.1145/3514094.3534192 | SNSプロファイリングでself-interpretの正当化・統制という利用者の解釈的自己決定負担を明示的に論じる(境界事例) | 1 回目（抄録のみ） |
| C2-0249 | 2024 | Commodifying the microbial self: microbiome-based personalization and the quest for symbiotic singularity | 10.1057/s41599-024-04209-5 | マイクロバイオームAIサービスの利用者によるアルゴリズム系の解釈を明示的に調査(境界事例) | 1 回目（抄録のみ） |
| C2-0251 | 2024 | From Transparency to Accountability and Back: A Discussion of Access and Evidence in AI Auditing | 10.1145/3689904.3694711 | AI監査アクセスのガバナンス論でaccountability/説明責任の構造を論じる(境界事例、C2-b候補ヒットあり) | 1 回目（抄録のみ） |
| C2-0258 | 2024 | Heuristics and biases in human–algorithm interaction and hotel revenue management override decision-making | 10.1108/ijchm-02-2024-0288 | ホテル収益管理システムでの人間-アルゴリズム相互作用における解釈・上書き判断を明示的に調査(強く合致) | 1 回目（抄録のみ） |
| C2-0267 | 2026 | From Verification Burden to Trusted Collaboration: Design Goals for LLM-Assisted Literature Reviews | 10.1145/3742414.3794723 | LLM支援文献レビューでverification burdenを明示的に定義・測定(強く合致) | 1 回目（抄録のみ） |
| C2-0271 | 2026 | SΔϕ-65 — Slop as Externalized Restabilization Cost: AI Slop, Human Slop, Authority Slop, and the Cost of Re-en… | 10.5281/zenodo.20173455 | AI SlopのExternalized Restabilization Cost(検証・訂正・再参入コストの外部化)を明示的に理論化(強く合致) | 1 回目（抄録のみ） |
| C2-0275 | 2026 | Living with Imperfect AI: User Adaptation, Trust Recalibration, and the Emerging Burden of Verification in Res… | 10.1145/3833541.3833828 | 生成AIハルシネーションに対するverification burdenを明示的に概念化・測定(強く合致) | 1 回目（抄録のみ） |
| C2-0276 | 2025 | From Verification Burden to Trusted Collaboration: Design Goals for LLM-Assisted Literature Reviews |  | 267と同一内容(早期arXiv版) | 1 回目（抄録のみ） |
| C2-0277 | 2025 | From Verification Burden to Trusted Collaboration: Design Goals for LLM-Assisted Literature Reviews | 10.48550/arxiv.2512.11661 | 267と同一内容(正式arXiv版) | 照合 |
| C2-0278 | 2026 | AI Debt: Verification Burdens, Rework Externalities, and the Hidden Costs of Asymmetric Generative-AI Adoption | 10.33774/coe-2026-nw4pm | 生成AI採用のverification burdenとrework externalitiesを明示的に理論化(強く合致) | 1 回目（抄録のみ） |
| C2-0280 | 2026 | Generative AI in Pharmacotherapy: Why Evidence Traceability, Verification Burden, Uncertainty, and Human Overr… | 10.51847/xt3dqdt8kp | 生成AI薬物療法でverification burdenを明示的に医療安全の境界要因として論じる(強く合致) | 1 回目（抄録のみ） |
| C2-0285 | 2026 | Efficiency Without Candidate Closure A Multi-Platform Case Study of Candidate Burden Externalization, Explanat… | 10.5281/zenodo.20837394 | AI/DXリクルーティング基盤でCandidate Burden Externalization(検証・説明の負担外部化)を明示的に理論化(強く合致) | 1 回目（抄録のみ） |
| C2-0286 | 2026 | Efficiency Without Candidate Closure A Multi-Platform Case Study of Candidate Burden Externalization, Explanat… | 10.5281/zenodo.20838276 | 285と同一内容(別DOI) | 1 回目（抄録のみ） |
| C2-0287 | 2026 | Efficiency Without Candidate Closure A Multi-Platform Case Study of Candidate Burden Externalization, Explanat… | 10.5281/zenodo.20837393 | 285と同一内容(別DOI) | 1 回目（抄録のみ） |
| C2-0288 | 2026 | Efficiency Without Candidate Closure A Multi-Platform Case Study of Candidate Burden Externalization, Explanat… | 10.5281/zenodo.21084556 | 285と同一内容(別DOI) | 1 回目（抄録のみ） |
| C2-0294 | 2026 | Ask Before or After? Clarification Timing and User Experience in Generative AI | 10.1145/3803784.3816856 | 生成AIの明確化質問タイミングによるverification burdenを明示的に測定(強く合致) | 1 回目（抄録のみ） |
| C2-0296 | 2026 | Five failure modes of aligned LLMs: A behavioral taxonomy of user-side verification costs | 10.5281/zenodo.20319044 | アラインメント済みLLMの失敗分類でverification burdenのユーザーへの転嫁を明示的に理論化(強く合致) | 1 回目（抄録のみ） |
| C2-0300 | 2026 | Five failure modes of aligned LLMs: A behavioral taxonomy of user-side verification costs | 10.5281/zenodo.20318790 | 296と同一内容(別DOI) | 1 回目（抄録のみ） |
| C2-0305 | 2026 | The Residual Human Burden Index (RHBI) | 10.5281/zenodo.20577637 | RHBIとして検証・修正・認知負担等、AI導入後に人が担う残余負担を明示的に操作化・測定する枠組み。 | 1 回目（抄録のみ） |
| C2-0307 | 2026 | The Residual Human Burden Index (RHBI) | 10.5281/zenodo.20577636 | C2-0305と同一のRHBI論文(重複エントリ)で検証負担等を明示的に操作化。 | 1 回目（抄録のみ） |
| C2-0309 | 2026 | The Organizational Behavior of Agentic AI: Collective Intelligence in Human-Agent Workflows | 10.48550/arxiv.2606.30986 | エージェント集団のワークフローにおける検証負担を組織形態比較の中で明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0310 | 2026 | The Organizational Behavior of Agentic AI: Collective Intelligence in Human-Agent Workflows |  | C2-0309と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0311 | 2025 | Plausibility as Failure: How LLMs and Humans Co-Construct Epistemic Error | 10.48550/arxiv.2512.16750 | LLM出力の解釈・評価における人間の認知的負担(検証負担・認知ドリフト)を実証的に検討。 | 1 回目（抄録のみ） |
| C2-0316 | 2026 | RHBI Scoring Rubric v1.0: A Pre-Registered Scoring Protocol for the Residual Human Burden Index | 10.5281/zenodo.21595667 | RHBIの事前登録スコアリング規約で検証負担クラスを明示的に定義・操作化。 | 1 回目（抄録のみ） |
| C2-0317 | 2026 | RHBI Scoring Rubric v1.0: A Pre-Registered Scoring Protocol for the Residual Human Burden Index | 10.5281/zenodo.21595666 | C2-0316と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0320 | 2026 | Measure, Then Bind: Coupling the Residual Human Burden Index to a Governance Architecture for Delegated Machin… | 10.5281/zenodo.21404608 | RHBIをガバナンス枠組みに接続し検証負担の測定を扱う。 | 1 回目（抄録のみ） |
| C2-0321 | 2026 | Measure, Then Bind: Coupling the Residual Human Burden Index to a Governance Architecture for Delegated Machin… | 10.5281/zenodo.21404607 | C2-0320と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0323 | 2026 | Informational Autoimmunity: The Fallout from Ungoverned AI Deployment — A Framework for Human Capital Atrophy … | 10.5281/zenodo.22695956 | LLM出力に対する受け手側の検証負担の拡大を中心命題として明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0324 | 2026 | Informational Autoimmunity: The Fallout from Ungoverned AI Deployment — A Framework for Human Capital Atrophy … | 10.5281/zenodo.22731374 | C2-0323と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0325 | 2026 | Informational Autoimmunity: The Fallout from Ungoverned AI Deployment — A Framework for Human Capital Atrophy … | 10.5281/zenodo.22695955 | C2-0323と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0327 | 2026 | The Governance of Human Capacity in the AI Age, Vol. 1: The Burnout of Possibility — Capability-Bandwidth Mism… | 10.5281/zenodo.19563035 | 生成AIが拡張する選択肢を人間が監督・検証・統合する認知的負担(CBM)を明示的に定式化。 | 1 回目（抄録のみ） |
| C2-0328 | 2026 | The Governance of Human Capacity in the AI Age, Vol. 1: The Burnout of Possibility — Capability-Bandwidth Mism… | 10.5281/zenodo.19563034 | C2-0327と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0330 | 2026 | SΔϕ-65 — Slop as Externalized Restabilization Cost: AI Slop, Human Slop, Authority Slop, and the Cost of Re-en… | 10.5281/zenodo.20127427 | AI生成物がもたらす検証・修正・再参入コストの外部化を明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0333 | 2026 | Self-regulation shapes who benefits from large language models | 10.31234/osf.io/nytj8_v1 | LLMとの相互作用における検証負担・検証債務を自己制御学習の枠組みで明示的に理論化。 | 1 回目（抄録のみ） |
| C2-0334 | 2026 | When AI Supervises and is Supervised: The Algorithmic Sandwich Model of Work | 10.5465/amproc.2026.17571abstract | 生成AI出力の検証・説明責任を「検証負担」として明示的に定義し実験データで検証。 | 1 回目（抄録のみ） |
| C2-0336 | 2026 | The efficiency–verification trade-off in large language model-assisted workplace risk assessment | 10.3176/proc.2026.3.10 | LLM支援リスク評価における検証負担をAI-人間の不一致として明示的に操作化・実測。 | 1 回目（抄録のみ） |
| C2-0337 | 2026 | The 5 Turns Strike LLM: The Trinity Sins and The Commercialized P $\neq$ NP Illusion | 10.5281/zenodo.18185154 | 生成AI出力の真偽検証負担がユーザーに転嫁される構図を明示的に主張。 | 1 回目（抄録のみ） |
| C2-0338 | 2026 | The 5 Turns Strike LLM: The Trinity Sins and The Commercialized P $\neq$ NP Illusion | 10.5281/zenodo.18185153 | C2-0337と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0345 | 2026 | "AI-Fatigue-Learning-6000: Measuring Artificial Intelligence Fatigue in AI-Assisted Learning Environments" | 10.21227/rz27-ze05 | AI学習支援環境における「検証負担」をAI疲労指標の一構成要素として明示的に測定するデータセット。 | 1 回目（抄録のみ） |
| C2-0349 | 2025 | The Social Responsibility Stack: A Control-Theoretic Architecture for Governing Socio-Technical AI |  | 社会技術AIガバナンス設計において認知的負担・説明品質を継続監視・実装する対象として明示的に位置付け。 | 1 回目（抄録のみ） |
| C2-0350 | 2025 | The Social Responsibility Stack: A Control-Theoretic Architecture for Governing Socio-Technical AI | 10.48550/arxiv.2512.16873 | C2-0349と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0354 | 2026 | From Behavioural Offloading to Governance Responsibility: Social Behaviour, AI Governance, and Educational Rec… | 10.20944/preprints202605.0019.v1 | AI拡散が招く検証負担等の認知的負荷を社会行動・ガバナンスの観点から明示的に列挙。 | 1 回目（抄録のみ） |
| C2-0355 | 2026 | Quantifying the Expectation-Realisation Gap for Agentic AI Systems |  | エージェントAI導入で検証負担が期待と実績の乖離をもたらす要因として明示的に指摘。 | 1 回目（抄録のみ） |
| C2-0356 | 2026 | Quantifying the Expectation-Realisation Gap for Agentic AI Systems | 10.48550/arxiv.2602.20292 | C2-0355と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0357 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.6084/m9.figshare.32456571.v1 | AI生成物の検証・所有・修復コストという「合成残余」概念を明示的に理論化。 | 1 回目（抄録のみ） |
| C2-0358 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.5281/zenodo.20426157 | C2-0357と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0359 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.5281/zenodo.20426158 | C2-0357と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0360 | 2026 | The Architect of Intelligence: Orchestration, Attribution, and the Creator in the Age of Artificial Intelligen… | 10.5281/zenodo.22004943 | 生成AIによる制作物への「産出と検証の非対称性の崩壊」を明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0362 | 2026 | The Architect of Intelligence: Orchestration, Attribution, and the Creator in the Age of Artificial Intelligen… | 10.5281/zenodo.22004944 | C2-0360と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0363 | 2026 | "AI-Fatigue-SEM-PLS-15000: A Large-Scale Dataset for Modeling Artificial Intelligence Fatigue in AI-Assisted L… | 10.21227/94rd-ny74 | AI支援学習環境の疲労指標に「Verification Burden」を潜在変数として明示的に含む大規模データセット。 | 1 回目（抄録のみ） |
| C2-0366 | 2026 | Generative AI in Marketing Communication: Consumer Perceptions, Brand Credibility, and Responsible AI Practice… | 10.25401/cardiffmet.32326287.v1 | 生成AIマーケティング文章に対する消費者の「検証負担」等を主要メカニズムとして明示的に特定。 | 1 回目（抄録のみ） |
| C2-0367 | 2026 | Generative AI in Marketing Communication: Consumer Perceptions, Brand Credibility, and Responsible AI Practice… | 10.25401/cardiffmet.32326287 | C2-0366と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0368 | 2026 | Bortom den tekniska tröskeln : Design av en konversationell AI-artefakt förutbildningsanalys inom en organisat… |  | 対話型AI意思決定支援における「検証負担」「誘導負担」をパラドックスとして明示的に概念化。 | 1 回目（抄録のみ） |
| C2-0369 | 2026 | Out-of-the-box: Provenance, verification, and the ethics of generative AI in information work | 10.1177/02663821261487913 | 生成AI情報の応答前に要する「検証負担」の差異を情報行動理論から明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0370 | 2025 | On-Premise AI for the Newsroom: Evaluating Small Language Models for Investigative Document Search | 10.48550/arxiv.2509.25494 | LLM+RAGのニュース編集室導入における検証負担をハルシネーションリスクと並ぶ阻害要因として明示的に指摘。 | 1 回目（抄録のみ） |
| C2-0371 | None | The Hobbesian Regression: Zero-Trust Architecture and the Dissolution of the Epistemic Covenant |  | ゼロトラスト・アーキテクチャ下で「現実を検証する負担」が個人に私化される構図を明示的に論じる。 | 1 回目（抄録のみ） |
| C2-0372 | 2026 | Computational Return Threshold: A Theory of AI Value Conversion, Resource Bubbles, and Delayed Technological P… | 10.5281/zenodo.20594088 | AI生成物拡大に伴う検証負担がAIの正味便益を損なう要因として明示的に位置付け。 | 1 回目（抄録のみ） |
| C2-0375 | 2026 | Why Workforce Governance Is the Limiting Factor in National Security Innovation |  | AI出力の解釈・検証・行動化にかかる「協調・検証負担」を国家安全保障組織の文脈で明示的に指摘。 | 1 回目（抄録のみ） |
| C2-0376 | 2026 | Computational Return Threshold: A Theory of AI Value Conversion, Resource Bubbles, and Delayed Technological P… | 10.5281/zenodo.20594089 | C2-0372と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0377 | 2026 | Supervising in the Age of Generative AI: Triangulating Graduate Nursing Students’ and Advisers’ Perspectives o… | 10.1007/978-3-032-33997-3_6 | 題名にAIの「Verification」と教育監督の文脈が明記され、対話的AI利用に伴う検証負担を示唆。 | 1 回目（抄録のみ） |
| C2-0383 | 2026 | The AI Assurance Cost Paradox: Fixed Governance Costs,Heterogeneous-Firm Adoption, and Market Concentration | 10.68050/jams103 | AI導入の固定費用モデルに「比例的検証負担」を明示的な変数として組み込み操作化。 | 1 回目（抄録のみ） |
| C2-0386 | 2026 | SΔϕ-71 — Cost Attribution Redesign: Low-Cost Transition, Asymmetric Cost Burden, Binding Fiction, and AI Inclu… | 10.5281/zenodo.20420270 | AI導入に伴うコスト帰属の再設計において検証負担を明示的に構成要素として位置付け。 | 1 回目（抄録のみ） |
| C2-0387 | 2026 | SΔϕ-71 — Cost Attribution Redesign: Low-Cost Transition, Asymmetric Cost Burden, Binding Fiction, and AI Inclu… | 10.5281/zenodo.20420269 | C2-0386と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0388 | 2026 | Cognitive Workload and Mental Burden in Health Care Professionals Interacting With AI: Systematic Review and M… | 10.2196/93618 | 医療従事者のAI利用における「検証負担」概念を中心に系統的レビュー・メタ分析で明示的に検討。 | 1 回目（抄録のみ） |
| C2-0390 | 2026 | BU216 Multi-Agent Regime Switching and Mechanism Design under B_U BU216／B_U 体系下多代理 Regime Switching 与机制设计 | 10.5281/zenodo.21100952 | マルチエージェント系の体制移行における検証負担を人間監督者を含む文脈で明示的に列挙。 | 1 回目（抄録のみ） |
| C2-0391 | 2026 | BU216 Multi-Agent Regime Switching and Mechanism Design under B_U BU216／B_U 体系下多代理 Regime Switching 与机制设计 | 10.5281/zenodo.21100951 | C2-0390と同一論文(重複エントリ)。 | 1 回目（抄録のみ） |
| C2-0396 | 2025 | VERITAS: Verification and Explanation of Realness in Images for Transparency in AI Systems | 10.48550/arxiv.2507.05146 | AI生成画像検出の判定理由を人間可読な説明として提示する仕組みで、出力解釈支援を明示的に提案。 | 1 回目（抄録のみ） |
| C2-0397 | 2025 | Improving Human Verification of LLM Reasoning through Interactive Explanation Interfaces | 10.1145/3742413.3789134 | LLM推論の対話的説明インターフェースによる人間の検証(誤り検出)を明示的に測定・改善。 | 1 回目（抄録のみ） |
| C2-0398 | 2024 | XAIVIER: Time Series Classifier Verification with Faithful Explainable AI | 10.1145/3640544.3645217 | 時系列分類モデルの検証にXAI説明手法を用いる仕組みで、モデル出力の解釈・検証を明示的に扱う。 | 1 回目（抄録のみ） |
| C2-0401 | 2026 | Explainability Burden and Accountability of Organizational AI Decisions: A Blockchain Based Governance Model | 10.51290/dpusbe.1879148 | AI決定への説明可能性負担(explainability burden)を説明の作成・維持・検証・保証の労働として定義し配分枠組みを提案 | 1 回目（抄録のみ） |
| C2-0402 | 2025 | Design of explanation user interfaces for interactive machine learning using the example of a knowledge graph-… | 10.1007/s00766-025-00437-6 | 対話的機械学習のための説明UIを、専門家利用者による検証・修正ニーズに基づき設計 | 1 回目（抄録のみ） |
| C2-0403 | 2025 | FACTS&EVIDENCE: An Interactive Tool for Transparent Fine-Grained Factual Verification of Machine-Generated Tex… | 10.48550/arxiv.2503.14797 | AI生成テキストの主張を利用者が理解・検証・選択的に信頼できるよう支援する対話的ツール | 1 回目（抄録のみ） |
| C2-0404 | 2025 | Found in Translation: semantic approaches for enhancing AI interpretability in face verification | 10.48550/arxiv.2501.05471 | AI出力(顔認証)の解釈可能性向上手法をユーザースタディで検証し利用者の解釈負担軽減を評価 | 1 回目（抄録のみ） |
| C2-0406 | 2026 | DeepFake Reporter Guard: A Deep Learning and Explainability-based System for Reliable News Verification | 10.1109/icssit69151.2026.11656466 | 非専門家(記者)がAI判定の説明を理解し真偽を検証できるよう設計されたXAIシステム | 1 回目（抄録のみ） |
| C2-0407 | 2024 | User-Centered Development of Explanation User Interfaces for AI-Based CDSS: Lessons Learned from Early Phases | 10.3233/shti240478 | AI診断支援システムの説明ニーズを医師から収集・検証するユーザー中心設計プロセス | 1 回目（抄録のみ） |
| C2-0408 | 2025 | Non-programmers Assessing AI-Generated Code: A Case Study of Business Users Analyzing Data | 10.1109/vl-hcc65237.2025.00044 | 非プログラマがAI生成コード・データ分析を十分に検証できないことを実証した研究 | 1 回目（抄録のみ） |
| C2-0410 | 2026 | Ask, Verify, Refine: A Question-Aware Multimodal XUI with Feedback-Guided Refinement for Clinical Verification | 10.1145/3772363.3798745 | 臨床医が意図別に質問しAI出力を確認・検証する多モーダル説明UIを提案 | 1 回目（抄録のみ） |
| C2-0411 | 2025 | Explainable AI (XAI) for Object Detection and Application to Satellite Imagery | 10.1109/access.2025.3624198 | 物体検出の説明手法の中核に利用者による部位の明示的検証を組み込む設計 | 1 回目（抄録のみ） |
| C2-0413 | 2025 | Alignment Debt: The Hidden Work of Making AI Usable | 10.48550/arxiv.2511.09663 | 「alignment debt」として利用者側の出力検証などの補償的労働を定量化し測定 | 照合 |
| C2-0414 | 2026 | Explainable AI for Signature Forgery Verification with Automated Multilingual Report Generation | 10.1109/esci68015.2026.11493357 | 題名のみだが、説明可能AIによる署名偽造検証と多言語レポート生成(人向け説明)を扱う | 1 回目（抄録のみ） |
| C2-0415 | 2025 | HOL4PSG: AI-Driven Proof Sequence Generation for the HOL4 Theorem Prover | 10.1109/adacis65663.2025.11436933 | 対話的定理証明でAI生成証明列に対する利用者の認知的負担を明記し軽減を主張 | 1 回目（抄録のみ） |
| C2-0416 | 2024 | When Do People Want an Explanation from a Robot? | 10.1145/3610977.3634990 | ロボットからの説明を人がいつ求めるかを事前登録実験で実証 | 1 回目（抄録のみ） |
| C2-0419 | 2018 | Explanation Methods in Deep Learning: Users, Values, Concerns and Challenges | 10.1007/978-3-319-98131-4_2 | 深層学習の説明手法について利用者の懸念・妥当性をレビューし説明対象としての利用者を分類 | 1 回目（抄録のみ） |
| C2-0421 | 2026 | HANSEL: Extracting Breadcrumbs from Web Agent Trajectories for Interactive Verification | 10.48550/arxiv.2606.18671 | Webエージェント軌跡の検証負担・労力をユーザースタディで実測し軽減手法を提案 | 1 回目（抄録のみ） |
| C2-0423 | 2025 | Design and Evaluation Methods for LLM-Based Explainable AI (XAI)-Based Human-AI Collaboration Systems | 10.54364/aaiml.2025.53240 | LLM-XAIの多段階検証機構と対話性を含む評価指標を提案する設計研究 | 1 回目（抄録のみ） |
| C2-0424 | 2025 | Explainable AI in Demand Forecasting Machine Learning Models | 10.37082/ijirmps.v13.i5.232718 | 需要予測モデルの複雑性が「解釈の負担」になると明記しXAI手法で対応 | 1 回目（抄録のみ） |
| C2-0426 | 2025 | Explaining at the Speed of Sight: Attention-Aware XAI for OODA-Inspired AI Design | 10.1109/cogmi67134.2025.00032 | AR環境での説明提示が利用者の認知負荷・注意負担に与える影響を実測 | 1 回目（抄録のみ） |
| C2-0427 | 2025 | In AI We Trust? Exploring the Role of Explainable GenAI and Expertise in Education | 10.1177/00187208251401773 | 説明の長さが学生のAI推奨への信頼較正・答案修正行動に与える影響を実験で検証 | 1 回目（抄録のみ） |
| C2-0428 | 2025 | Evaluating the Impact of AI-Generated Visual Explanations on Decision-Making for Image Matching | 10.1145/3708359.3712121 | AI視覚説明が画像照合における意思決定・検証目的の利用に与える影響を実験で検証 | 1 回目（抄録のみ） |
| C2-0429 | 2024 | The Role of Explainability in Collaborative Human-AI Disinformation Detection | 10.1145/3630106.3659031 | 人間中心評価によりXAI機能が偽情報検出時の理解しやすさ・有用性に与える影響を測定 | 1 回目（抄録のみ） |
| C2-0431 | 2025 | Explainable Biomedical Claim Verification with Large Language Models | 10.48550/arxiv.2502.21014 | LLMによる生物医学的主張検証で利用者主導の推論確認・正当化プロセスを統合し透明化 | 1 回目（抄録のみ） |
| C2-0432 | 2024 | ClaimVer: Explainable Claim-Level Verification and Evidence Attribution of Text Through Knowledge Graphs | 10.48550/arxiv.2403.09724 | 主張検証の説明生成で利用者の認知負荷低減と検証ニーズへの対応を明示的に設計 | 1 回目（抄録のみ） |
| C2-0437 | 2026 | It Matters How You Say It: Exploring Rhetorical Patterns for AI-Assisted Information Evaluation | 10.48550/arxiv.2607.17627 | AI応答の修辞パターンが事実検証課題での内省・検証行動に与える影響を実験で検証 | 1 回目（抄録のみ） |
| C2-0441 | 2026 | AuraWear: Designing for Human-AI Co-Decision in Creative Fashion Recommendation | 10.1145/3803784.3816845 | ファッション推薦のAI提案を利用者が検査・上書きし説明を伴う共同意思決定を行う設計 | 未実施（逸脱 2） |
| C2-0442 | 2026 | JudgmentLens: Human-AI Sensemaking of Complex Legal Judgments |  | 法律文書の対話的読解支援で構造・解釈・検証の破綻を特定し、検証可能な追跡リンクを設計 | 未実施（逸脱 2） |
| C2-0444 | 2018 | How Can AI Help Reduce the Burden of Disaster Management Decision-Making? | 10.1007/978-3-319-94334-3_14 | 題名のみだが、AIが災害対応の意思決定負担をどう軽減できるかを扱っており対象範囲に含め得る | 未実施（逸脱 2） |
| C2-0445 | 2025 | Human-AI experience in integrated development environments: a systematic literature review | 10.1007/s10664-025-10793-0 | AI支援IDE内のHuman-AI体験レビューで検証オーバーヘッド・過度の依存を論点化 | 未実施（逸脱 2） |
| C2-0446 | 2026 | LLMs in Civil Engineering: Education Usage Patterns, Verification Practices, and Curriculum Implications from … | 10.1061/jceecd.eieng-2449 | 土木教育でのLLM検証実践(手計算・基準照合等)をタクソノミーに基づき実測調査 | 未実施（逸脱 2） |
| C2-0448 | 2025 | Exploring automation bias in human–AI collaboration: a review and implications for explainable AI | 10.1007/s00146-025-02422-7 | 自動化バイアスと説明可能AIのレビューでタスク検証要求・説明複雑性を論点として扱う | 未実施（逸脱 2） |
| C2-0449 | 2024 | AI Based Hallucination Detector | 10.47392/irjash.2024.050 | ハルシネーション検証ツールで、利用者が検証プロセスを理解できる対話的説明機能を提供 | 未実施（逸脱 2） |
| C2-0453 | 2025 | Large language models in programming: a meta-analysis of tools, users, and human-computer interaction themes | 10.54941/ahfe1006934 | LLMプログラミング支援のメタ分析で認知負荷管理・信頼較正をHCIテーマとして扱う | 未実施（逸脱 2） |
| C2-0455 | 2025 | Beyond Transparency: Evaluating Explainability in AI-Supported Fact-Checking | 10.1145/3733567.3735566 | AI支援ファクトチェックの説明可能性を人間中心評価(n=406)で検証し過信リスクも報告 | 未実施（逸脱 2） |
| C2-0457 | 2025 | Explainable AI in Edge Devices: A Lightweight Framework for Real-Time Decision Transparency | 10.18535/ijecs.v14i07.5181 | エッジAIのXAIで「利用者が判断を理解・検証・信頼するのが困難」と明記しその解決を試みる | 未実施（逸脱 2） |
| C2-0459 | 2025 | XAI for U 2025: 2$nd$ International Workshop on Explainable AI for Ubiquitous, Pervasive and Wearable Computin… | 10.1145/3714394.3750557 | ユビキタスXAIワークショップの趣旨説明で、利用者らが信頼性等を検証する困難さを明記 | 未実施（逸脱 2） |
| C2-0460 | 2025 | Explainable AI in nuclear medicine | 10.1007/s00259-025-07675-4 | ブラックボックスAIの説明要否を「利用者が自ら出力を検証・実行できるか」で切り分ける枠組みを提示 | 未実施（逸脱 2） |
| C2-0464 | 2025 | Explainable AI for Autonomous Systems: A Framework for Trustworthy Decision-Making | 10.1109/iccce66530.2025.11473362 | 自律システムXAIで利用者・開発者・規制者が判断を解釈・信頼するのが困難な点を明記し人間参加検証を支援 | 未実施（逸脱 2） |
| C2-0466 | 2025 | Blockchain + AI for Transparent and Auditable AI Models | 10.51583/ijltemas.2025.1413sp013 | ブロックチェーン監査ログにより利用者・関係者がAI判断の妥当性を確認できる設計を提案 | 未実施（逸脱 2） |
| C2-0469 | 2025 | The Fast and Spurious: Developer Productivity with GenAI | 10.1145/3803437.3806710 | GenAI開発でコードレビュー負担・出力検証による持続的な認知負荷の増加を明記 | 未実施（逸脱 2） |
| C2-0471 | 2026 | Designing meaningful human oversight in AI | 10.1007/s43681-026-01147-7 | solve-verify非対称性を利用し人間の検証負担を軽減する監督設計の枠組みを提案 | 未実施（逸脱 2） |
| C2-0473 | 2026 | Explainable AI for Equitable Nurse Scheduling: Pragmatic Pre-Post Implementation Study | 10.2196/94450 | 説明可能AI看護スケジューリングで公平性監視ダッシュボードを通じたスタッフの検証・受容を扱う | 未実施（逸脱 2） |
| C2-0474 | 2026 | Beyond Explainable AI (XAI): An Overdue Paradigm Shift and Post-XAI Research Directions | 10.48550/arxiv.2602.24176 | Post-XAIの一環として検証重視の対話的AI(IAI)というパラダイムを提案 | 未実施（逸脱 2） |
| C2-0476 | 2026 | Explainable AI and echo state networks calibrate trust in human machine interaction | 10.1038/s41598-025-30899-1 | 説明可能AIによる信頼較正を人間機械相互作用実験(2x2要因計画)で実測 | 未実施（逸脱 2） |
| C2-0477 | 2025 | Enhancing XAI Interpretation through a Reverse Mapping from Insights to Visualizations | 10.1109/vis60296.2025.00013 | 利用者が説明から推論するのに苦労する点を指摘し、可視化により検証ループを支援する手法を提案 | 未実施（逸脱 2） |
| C2-0478 | 2026 | StepMIND: A Visual Framework for Stepwise, Multimodal, and Bidirectional Explanations of AI-Generated Data Ana… | 10.1145/3742413.3789070 | AI生成データ分析パイプラインの検証・解釈・修正のしやすさを可視化枠組みで支援しユーザースタディで実測 | 未実施（逸脱 2） |
| C2-0479 | 2026 | Designing Explainable AI-Powered Adaptive UX Interfaces to Reduce Technostress and Improve Digital Wellbeing a… | 10.67294/h4hm2621 | XAI+適応UXでテクノストレス・認知負荷・解釈的負担を軽減する枠組みを提案し実験で評価 | 未実施（逸脱 2） |
| C2-0482 | 2026 | AI-generated patient instructions as safety-critical communication: a provisional evidence-informed framework … | 10.1016/j.ijmedinf.2026.106645 | AI生成患者向け説明の誤りを患者が検出できないという解釈・検証の限界を安全枠組みとして提示 | 未実施（逸脱 2） |
| C2-0483 | 2021 | Explainable AI for Robot Failures: Generating Explanations that Improve User Assistance in Fault Recovery | 10.1145/3434073.3444657 | ロボット失敗の説明が非専門家の原因特定・復旧に有効かを実証しユーザーに必要な情報を検討 | 未実施（逸脱 2） |
| C2-0488 | 2026 | SpheriCity: Designing Trustworthy Conversational AI for Sustainability Decision Support | 10.1145/3811242.3819112 | 対話AIの根拠不透明性・要検証性を明記し証拠追跡性を重視した設計を提案 | 未実施（逸脱 2） |
| C2-0495 | 2021 | White paper: The Helix Pathogenicity Prediction Platform | 10.48550/arxiv.2104.01033 | AI予測プラットフォームにより「診断労力の負担がデータ収集から解釈へシフトした」と明記 | 未実施（逸脱 2） |
| C2-0499 | 2026 | Users as Allies:Why Clinicians Are Key to Explainable Clinical AI |  | 誤整合した説明が臨床医に認知的負担を移すと明記し、解釈的・警戒的負担の軽減を論じる | 未実施（逸脱 2） |
| C2-0511 | 2026 | When AI outperforms humans, who bears the burden of proof? | 10.1007/s00146-026-03375-1 | 抄録なし、題名『AIが人間を上回るとき証明責任は誰が負うか』は主題合致と判断 | 未実施（逸脱 2） |
| C2-0512 | 2026 | Terminus: Against the Cognitive Prerequisite for Algorithmic Justice | 10.5281/zenodo.21792061 | 説明要求が市民に隠れた負担を課すと明示し、負担をシステム側の説明責任へ転換する制度提案(自費出版で質に留保) | 未実施（逸脱 2） |
| C2-0513 | 2026 | Terminus: Against the Cognitive Prerequisite for Algorithmic Justice | 10.5281/zenodo.21792062 | 0512と同一研究の別版 | 未実施（逸脱 2） |
| C2-0516 | None | Terminus: Against the CoTerminus: Against the Cognitive Prerequisite for Algorithmic Justice |  | 0512/513と同一研究のPhilPapers版 | 未実施（逸脱 2） |
| C2-0517 | 2026 | From Prediction to Public Accountability: An Accountability-Chain Framework for AI Classification in Critical … | 10.20944/preprints202606.1297.v1 | 公共サービスAI分類システムが立証負担を市民へ転嫁すると明示するアカウンタビリティ枠組み論文 | 未実施（逸脱 2） |
| C2-0519 | 2026 | Useful for Exploration, Risky for Precision: Evaluating AI Tools in Academic Research | 10.48550/arxiv.2605.10125 | XAIの精度不足が検証の負担を研究者へ押し戻すと明示的に実証するベンチマーク研究 | 未実施（逸脱 2） |
| C2-0520 | 2026 | Useful for Exploration, Risky for Precision: Evaluating AI Tools in Academic Research |  | 0519と同一研究の別版 | 未実施（逸脱 2） |
| C2-0521 | 2026 | The Cost of Always Answering: Governance Costs of Generative AI in Operational Environments | 10.5281/zenodo.19023402 | 生成AIの常時応答設計がinterpretation, verification, correctionという組織的ガバナンス作業を生むと明示的に理論化(強く合致・自費出版で質に留保) | 未実施（逸脱 2） |
| C2-0522 | 2026 | The Cost of Always Answering: Governance Costs of Generative AI in Operational Environments | 10.5281/zenodo.19021353 | 0521と同一研究の別版 | 未実施（逸脱 2） |
| C2-0523 | 2026 | The Cost of Always Answering: Governance Costs of Generative AI in Operational Environments | 10.5281/zenodo.19021352 | 0521と同一研究の別版 | 未実施（逸脱 2） |
| C2-0526 | 2025 | SUNDUS: A Human-Centered Framework for Fostering Human-AI Collaboration Through Transparency | 10.14569/ijacsa.2025.0161104 | オペレーターがAI出力の解釈・実装に訓練を要する負担を明示し、透明性設計で認知負荷をオフロードする枠組み(強く合致) | 未実施（逸脱 2） |
| C2-0527 | 2026 | Differential Friction Conditioning in Human-LLM Interaction: A Developmental Risk Framework for Child-AI Syste… | 10.5281/zenodo.18332215 | LLMが子どもの発話を誤解釈し修正・再構成させる相互作用摩擦を実証し、意図検証負担をシステム側へ転換する提案を含む | 未実施（逸脱 2） |
| C2-0528 | 2026 | Differential Friction Conditioning in Human-LLM Interaction: A Developmental Risk Framework for Child-AI Syste… | 10.5281/zenodo.18332216 | 0527と同一研究の別版 | 未実施（逸脱 2） |
| C2-0538 | 2025 | ‘The Justification Machine’ - Automating Reason-Giving | 10.53136/97912218237763 | 自動化された行政理由付けが受け手に複雑な変数解釈と説明的負担を課すと明示的に論じる | 未実施（逸脱 2） |
| C2-0547 | 2026 | Behavioral Forensics in Large Language Models: Why a Distinct Field Is Needed | 10.5281/zenodo.19774520 | LLMの逐次的行動シグネチャの一つとしてburden shiftingを文書化する行動法医学の枠組み論文(自費出版で質に留保) | 未実施（逸脱 2） |
| C2-0548 | 2026 | Behavioral Forensics in Large Language Models: Why a Distinct Field Is Needed | 10.5281/zenodo.19774521 | 0547と同一研究の別版 | 未実施（逸脱 2） |
| C2-0554 | 2026 | Behavioral Forensics in Large Language Models: Why a Distinct Field is Needed A Field-Framing Paper for Transc… | 10.2139/ssrn.6652160 | 0547/548と同一研究のSSRN版(抄録なしだが同一内容と判断) | 未実施（逸脱 2） |
| C2-0584 | 2025 | Explained or Certified? Examining the Influence of XAI and AI-Seals on Users’ Trust and Understanding | 10.1145/3743049.3743072 | XAIが利用者へ認知的負担をシフトすると明示し、AI-Sealsとの比較実験で理解・信頼への影響を実測(強く合致) | 未実施（逸脱 2） |
| C2-0588 | 2026 | Towards Effective Generation of Interactive Visualizations with Vibe Coding: An Empirical Study |  | LLMコード生成(vibe coding)が開発労働をどうシフトするかをユーザー研究で実証、人間-エージェント協働戦略を分析(境界事例) | 未実施（逸脱 2） |
| C2-0594 | 2026 | AI scribes as novice performers: Insights from simulation science | 10.1177/20552076261437267 | AIスクライブの機能不整合が臨床医の認知的負荷を増大させると論じるコメンタリー(境界事例) | 未実施（逸脱 2） |
| C2-0621 | 2026 | From testbeds to high-stakes work: a review of Human-AI teaming domains and teaming factors | 10.3389/frobt.2026.1733942 | Human-AIチーミングのシステマティックレビューで、trust・explainability/transparency・decision-makingをチーミング要因として明示的に検討しており、対話的・自動化系における解釈・説明の負担に直接該当する | 未実施（逸脱 2） |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

