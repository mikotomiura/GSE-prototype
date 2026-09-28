# searchgap.md — AI 疲労文献 DB 検索漏れ点検

生成日時: 2026-09-28（実行環境時刻ベース）

採否の判定は行っていません。以下は機械的な予備ふるいの印と根拠語のみです。

**手法メモ**: 予備ふるいは正規表現による題名・抄録の語マッチ（fatigue系語 AND AI利用系語）で機械的に行った。除外シグナル語（driver/EEG/金属疲労系語/AI検出ツール系語など）を検出したものは 3節の境界例に回したが、この語彙リストは網羅的ではなく、著者名の頭文字が偶然 "Ai" に一致するなどの残存ノイズも起こりうる。したがって 2節・3節とも人手での内容確認が別途必要。

## 1. 検索ログ

| # | クエリ | 情報源 | ヒット件数 (API) | 見た件数 | 既存DBと一致 | 予備ふるい新規件数 |
|---|---|---|---|---|---|---|
| 1 | "AI fatigue" | OpenAlex | 158 | 50 | (下記合算) | (下記合算) |
| 1 | "AI fatigue" | Crossref | 752472 | 50 | (下記合算) | (下記合算) |
| 1 | "AI fatigue" | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **8** | **73** |
| 2 | "AI-induced fatigue" | OpenAlex | 4 | 4 | (下記合算) | (下記合算) |
| 2 | "AI-induced fatigue" | Crossref | 2385273 | 50 | (下記合算) | (下記合算) |
| 2 | "AI-induced fatigue" | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **4** | **18** |
| 3 | "generative AI" fatigue | OpenAlex | 31618 | 50 | (下記合算) | (下記合算) |
| 3 | "generative AI" fatigue | Crossref | 815534 | 50 | (下記合算) | (下記合算) |
| 3 | "generative AI" fatigue | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **4** | **6** |
| 4 | ChatGPT fatigue | OpenAlex | 19900 | 50 | (下記合算) | (下記合算) |
| 4 | ChatGPT fatigue | Crossref | 248107 | 50 | (下記合算) | (下記合算) |
| 4 | ChatGPT fatigue | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **0** | **12** |
| 5 | chatbot fatigue users | OpenAlex | 9686 | 50 | (下記合算) | (下記合算) |
| 5 | chatbot fatigue users | Crossref | 347615 | 50 | (下記合算) | (下記合算) |
| 5 | chatbot fatigue users | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **0** | **7** |
| 6 | "AI exhaustion" OR "AI burnout" | OpenAlex | 249 | 50 | (下記合算) | (下記合算) |
| 6 | "AI exhaustion" OR "AI burnout" | Crossref | 595527 | 50 | (下記合算) | (下記合算) |
| 6 | "AI exhaustion" OR "AI burnout" | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **0** | **48** |
| 7 | "decision fatigue" artificial intelligence | OpenAlex | 1362 | 50 | (下記合算) | (下記合算) |
| 7 | "decision fatigue" artificial intelligence | Crossref | 2420206 | 50 | (下記合算) | (下記合算) |
| 7 | "decision fatigue" artificial intelligence | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **1** | **14** |
| 8 | "cognitive fatigue" "generative AI" | OpenAlex | 1049 | 50 | (下記合算) | (下記合算) |
| 8 | "cognitive fatigue" "generative AI" | Crossref | 1416271 | 50 | (下記合算) | (下記合算) |
| 8 | "cognitive fatigue" "generative AI" | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **6** | **15** |
| 9 | "prompt fatigue" OR "prompting fatigue" | OpenAlex | 139 | 50 | (下記合算) | (下記合算) |
| 9 | "prompt fatigue" OR "prompting fatigue" | Crossref | 247747 | 50 | (下記合算) | (下記合算) |
| 9 | "prompt fatigue" OR "prompting fatigue" | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **0** | **8** |
| 10 | "AI technostress" fatigue | OpenAlex | 21 | 21 | (下記合算) | (下記合算) |
| 10 | "AI technostress" fatigue | Crossref | 754090 | 50 | (下記合算) | (下記合算) |
| 10 | "AI technostress" fatigue | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **1** | **10** |
| 11 | "AI fatigue scale" OR "AI fatigue" scale | OpenAlex | 23624334 | 50 | (下記合算) | (下記合算) |
| 11 | "AI fatigue scale" OR "AI fatigue" scale | Crossref | 1513925 | 50 | (下記合算) | (下記合算) |
| 11 | "AI fatigue scale" OR "AI fatigue" scale | **合算 (両情報源, DOI重複排除前カウント)** | - | - | **1** | **7** |

Europe PMC は時間制約のため未実行（下記「未実行」欄参照）。

### 検索ログに関する注記
- Crossref の `query.bibliographic` はフレーズ完全一致（引用符）を保証しない。関連度順の自由語検索のため、`total-results`（ヒット件数）は数十万〜数百万件と大きく出るが、これはクエリ全体に緩く関連する Crossref 全収録物の件数であり、実際に条件を満たす文献数ではない。上位 50 件のみを内容突合の対象とした。
- OpenAlex `search` パラメータも同様に自由語検索であり、クエリ 11（`"AI fatigue scale" OR "AI fatigue" scale`）は引用符外の単独語 `scale` が広く一致してヒット件数が 23,624,334 件という明らかに異常な値になった。これは検索式の構文限界（引用符付きフレーズと裸の単語の混在が意図通りに絞り込まれない）によるもので、実際の該当文献数を表さない。上位 50 件のみ内容突合。
- 「見た件数」は各情報源で実際にタイトル・抄録を突合した件数（上限 50）。
- 「既存DBと一致」「予備ふるい新規件数」の行は OpenAlex + Crossref 上位 50 件ずつを合算し DOI 重複排除する前の延べ件数（同一文献が両情報源・複数クエリに出ればその都度カウント）。ユニーク新規候補は下記候補表を参照。

## 2. 新規候補表（予備ふるいに当たったもの・除外語なし・最大40件、上位 40 件を表示）

（予備ふるい該当かつ除外シグナル語なしのユニーク新規 DOI: 総数 141 件のうち上位 40 件）

| DOI | 題名 | 年 | 誌名/収録先 | 文献種別 | 根拠語 | どのクエリ (#) |
|---|---|---|---|---|---|---|
| 10.36227/techrxiv.177015854.42176901/v1 | Cognitive Load-Aware Edge AI: Reducing Acute Operator Fatigue in Human-AI IoT System | 2026 |  | プレプリント | fatigue / ai, human-ai | 1,2,8,11 |
| 10.31234/osf.io/kp7zs_v1 | AI Fatigue in Human–AI Interaction: Conceptual Framework, Scale Development and Validation, and Associations with AI Engagement | 2026 |  | 尺度 | exhaustion, fatigue / ai | 1,2,11 |
| 10.2139/ssrn.7358579 | Digital Fatigue in the Age of Generative AI: Effects on Academic Engagement and Learning Outcomes | 2026 |  | プレプリント | exhaustion, fatigue / ai, genai, generative ai | 1,3,8 |
| 10.70675/3243d394z7c80z43d7z9fbezf203f23d4818 | Explainable AI (XAI) with Convolutional Neural Networks for Mental Fatigue Modeling |  |  | 一次研究 | fatigue, fatigués / ai | 1,2,11 |
| 10.1186/s41073-023-00133-5 | Fighting reviewer fatigue or amplifying bias? Considerations and recommendations for use of ChatGPT and other large language models in scholarly peer review | 2023 | Research Integrity and Peer Review | レビュー | fatigue / chatgpt | 3,4,5 |
| 10.2139/ssrn.7243542 | When Fatigue Coexists with Risk Awareness: Boundary Conditions on the Privacy Calculus in Generative AI Adoption | 2026 |  | プレプリント | fatigue / ai, generative ai | 1,3,8 |
| 10.2139/ssrn.5223740 | A Framework for Creative Problem-Solving in AI Inspired by Neural Fatigue Mechanisms | 2025 |  | プレプリント | fatigue / ai | 1,2 |
| 10.32469/10355/111040 | Effects of AI-generated personalized financial recommendations on engagement, intrusiveness, and fatigue |  |  | 一次研究 | fatigue / ai, artificial intelligence | 1,2 |
| 10.1108/ijwhm-09-2025-0252 | How digital leadership and innovative climate interact to lessen AI-related job insecurity, AI use anxiety, technostress, and emotional exhaustion | 2026 | International Journal of Workplace Health Management | 一次研究 | exhaustion / ai | 6,10 |
| 10.66669/cineforum.v66is6.1515 | The Faculty Paradox: Assessing Digital Fatigue and Institutional Readiness for AI Integration in Higher Education | 2026 |  | 一次研究 | fatigue / ai | 1,2 |
| 10.31152/jb.2025.12.10.6.297 | AI Anxiety to Fatigue and Its Consequences: The Moderating Role of AI Usage Motivation | 2025 | Journal of Business Convergence | 一次研究 | fatigue / ai | 1 |
| 10.21203/rs.3.rs-2587766/v1 | Fighting reviewer fatigue or amplifying bias? Considerations and recommendations for use of ChatGPT and other Large Language Models in scholarly peer review | 2023 | Research Square | レビュー | fatigue / chatgpt | 4 |
| 10.36948/ijfmr.2026.v08i02.74796 | Generative AI and Creative Engagement: A Review of Cognitive Fatigue, Creative Self-Efficacy and Psychological Ownership | 2026 | International Journal For Multidisciplinary Research | レビュー | fatigue / ai, artificial intelligence, generative ai | 8 |
| 10.5465/amproc.2024.15756abstract | Impact of Generative AI on Creativity: The Role of Intellectual Stimulation and Cognitive Fatigue | 2024 | Academy of Management Proceedings | 会議 | fatigue / ai, artificial intelligence, chatgpt | 8 |
| 10.1016/b978-0-443-44958-1.00005-7 | Mitigating bias in AI-driven burnout risk predictions for optimal staff scheduling in healthcare | 2026 | Elsevier eBooks | 一次研究 | burnout / ai | 6 |
| 10.1007/s10639-024-13198-6 | Privacy fatigue and its effects on ChatGPT acceptance among undergraduate students: is privacy dead? | 2025 | Education and Information Technologies | 一次研究 | fatigue, weariness / chatgpt | 4 |
| 10.34293/blp.9789395659611.ch022 | Worklife Balance Challenges in AI – Supported Hybrid Work Models: A Technostress Perspective | 2026 | Disrupt to Win: Modern Business Techniques for Innovation and Growth | 一次研究 | exhaustion / ai, artificial intelligence | 10 |
| 10.21227/rz27-ze05 | "AI-Fatigue-Learning-6000: Measuring Artificial Intelligence Fatigue in AI-Assisted Learning Environments" | 2026 | IEEE DataPort | データセット | fatigue / ai, artificial intelligence, human-ai | 1 |
| 10.21227/94rd-ny74 | "AI-Fatigue-SEM-PLS-15000: A Large-Scale Dataset for Modeling Artificial Intelligence Fatigue in AI-Assisted Learning Environment" | 2026 | IEEE DataPort | データセット | fatigue / ai, artificial intelligence, generative ai | 1 |
| 10.5281/zenodo.17696030 | AI Anhedonia: The Shift from AI Fatigue to Algorithmic Indifference in the Post-Hype Era | 2025 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | exhaustion, exhaustive, fatigue / ai, artificial intelligence | 1 |
| 10.5281/zenodo.17696031 | AI Anhedonia: The Shift from AI Fatigue to Algorithmic Indifference in the Post-Hype Era | 2025 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | exhaustion, exhaustive, fatigue / ai, artificial intelligence | 1 |
| 10.21203/rs.3.rs-9220394/v1 | AI Awareness as a Workplace Stressor Examining Emotional Exhaustion Through Job Insecurity and Work Family Interference | 2026 |  | プレプリント | exhaustion, exhaustions / ai, artificial intelligence | 6 |
| 10.5281/zenodo.22234080 | AI Burnout: From an Individual Condition to an Emerging Epidemic | 2026 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | burnout / ai, artificial intelligence | 6 |
| 10.5281/zenodo.22234079 | AI Burnout: From an Individual Condition to an Emerging Epidemic | 2026 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | burnout / ai, artificial intelligence | 6 |
| 10.63282/wcai25-115 | AI Copilots for Clinical Documentation to Reduce Physician Burnout | 2025 | World Congress on Computing, AI, and Machine Learning | 会議 | burnout / ai | 6 |
| 10.5281/zenodo.22838191 | AI Fatigue in Higher Education: A Systematic Review of Associated Conditions, Manifestations, and Lifelong Learning Implications | 2026 | Zenodo (CERN European Organization for Nuclear Research) | レビュー | fatigue / ai | 1 |
| 10.5281/zenodo.22838190 | AI Fatigue in Higher Education: A Systematic Review of Associated Conditions, Manifestations, and Lifelong Learning Implications | 2026 | Zenodo (CERN European Organization for Nuclear Research) | レビュー | fatigue / ai | 1 |
| 10.1145/3734515 | AI Fatigue: Reflections on the Human Side of AI’s Rapid Advancement | 2025 | Communications of the ACM | 一次研究 | fatigue / ai | 1 |
| 10.18243/eon/2026.19.5.5 | AI Fatigue: Views From the Trenches | 2026 | Editorial Office News | 一次研究 | fatigue / ai | 1 |
| 10.2196/preprints.85247 | AI Induced Burnout in Tech: A SHAP Based Diagnostic Study with an HCI-Guided Intervention Model (Preprint) | 2025 |  | プレプリント | burnout / ai, artificial intelligence | 6 |
| 10.5281/zenodo.22233199 | AI burnout: da fenomeno individuale a epidemia | 2026 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | burnout / ai | 6 |
| 10.5281/zenodo.22233200 | AI burnout: da fenomeno individuale a epidemia | 2026 | Zenodo (CERN European Organization for Nuclear Research) | プレプリント | burnout / ai | 6 |
| 10.3389/fpsyg.2026.1897395 | AI information encounters and university students’ digital burnout: the mediating role of cognitive flexibility and the moderating effect of AI learning trust | 2026 | Frontiers in Psychology | 一次研究 | burnout / ai, artificial intelligence | 6 |
| 10.34218/ijm_17_04_009 | AI-DRIVEN BURNOUT MANAGEMENT SYSTEM 4.0: A CENTRALIZED APPROACH TO REDUCING BURNOUT IN THE IT INDUSTRY USING WORK PATTERN MONITORING, AGENTIC AI, TEMPORAL MACHINE LEARNING, RETRIEVAL-AUGMENTED GENERATION, DIGITAL TWINS, AND COUNTERFACTUAL REASONING | 2026 | INTERNATIONAL JOURNAL OF MANAGEMENT | 一次研究 | burnout / ai | 6 |
| 10.1001/jama.2024.5157 | AI-Drafted Responses to Patients Reduced Clinician Burnout | 2024 | JAMA | 一次研究 | burnout / ai | 6 |
| 10.47191/etj/v10i04.09 | AI-Driven Burnout Management System: A Novel Approach Using Generative AI, MongoDB Atlas, Python, And Training Large Language Models (LLMs) - Version 3 | 2025 | Engineering and Technology Journal | 一次研究 | burnout / ai, generative ai | 6 |
| 10.2196/preprints.70579 | AI-Driven Mental Health Solutions for Healthcare Worker Burnout: A Strategic Approach (Preprint) | 2024 |  | プレプリント | burnout / ai, artificial intelligence | 6 |
| 10.5220/0013898300004919 | AI-Driven Multimodal Posture and Action Analysis for Detecting Workplace Fatigue and Productivity | 2025 | Proceedings of the 1st International Conference on Research and Development in Information, Communication, and Computing Technologies | 会議 | fatigue / ai | 1 |
| 10.1080/07380569.2026.2712296 | Adopting Artificial Intelligence in Schools: Opportunities and Challenges in the Diffusion of a Commercial Large Language Model Across a Teaching Population | 2026 | Computers in the Schools | 一次研究 | fatigue / ai, artificial intelligence, copilot | 1 |
| 10.1093/jamia/ocaf065 | Adoption of artificial intelligence in healthcare: survey of health system priorities, successes, and challenges | 2025 | Journal of the American Medical Informatics Association | 一次研究 | burnout / ai, artificial intelligence, generative ai | 3 |

## 3. 当たらなかったが境界例と思われるもの（予備ふるいには該当したが除外シグナル語も検出・最大10件、10 件表示）

理由列は機械的に検出した除外シグナル語（AI が疲労を検出/予測する道具である可能性、または材料工学の fatigue の可能性）。

| DOI | 題名 | 年 | 誌名/収録先 | 根拠語 (fatigue/AI) | 除外シグナル語 | どのクエリ (#) |
|---|---|---|---|---|---|---|
| 10.70675/e7faeb7cz94a9z48adzbf0fz56fe3448b863 | AI based fatigue assessment system for athletes using smart textile wearables |  |  | fatigue / ai | fatigue assessment, smart textile, wearables | 1,2,11 |
| 10.55248/gengpi.07.0326.0459 | AI-Based Driver Fatigue Detection With Live Alerts | 2026 | International Journal of Research Publication and Reviews | fatigue / ai | driver, fatigue detection | 1,2,11 |
| 10.1016/j.ijfatigue.2025.109280 | Buffeting-induced fatigue in suspension bridges: time-domain analysis with AI techniques | 2026 | International Journal of Fatigue | fatigue / ai | materials-fatigue-journal | 1,2,11 |
| 10.1016/0142-1123(92)90049-i | Fractal characterization of fatigue thresholdFu, R., Mu, Z.Q., Lung, C.W. and Ai, S.H. | 1992 | International Journal of Fatigue | fatigue / ai | materials-fatigue-journal | 1,2,11 |
| 10.1016/0142-1123(95)98287-d | A critical verification of post-threshold non-propagation (hysteresis in fatigue crack propagation) utilizing compression pre-cracking on AI-2024T3 alloy | 1995 | International Journal of Fatigue | fatigue / ai | alloy, crack propagation, materials-fatigue-journal | 1,2 |
| 10.5220/0014549300005024 | AI Powered Predictive Health Tracker for Identifying Early Signs of Chronic Fatigue Syndrome | 2025 | Proceedings of the 1st International Conference on Computational and Cognitive Systems Science | fatigue / ai | fatigue syndrome | 1,2 |
| 10.2118/229322-ms | AI-Powered Driver Fatigue and Distraction Detection Cameras | 2025 | ADIPEC | fatigue / ai, artificial intelligence | driver, fatigue monitoring | 1,2 |
| 10.1016/j.ijfatigue.2024.108321 | AI-based macro model learning for high cycle fatigue assessment of welded joints in large-span steel structures | 2024 | International Journal of Fatigue | fatigue / ai | fatigue assessment, materials-fatigue-journal, steel | 1,2 |
| 10.1016/0142-1123(96)82912-4 | Dislocation structure of fatigue crack tip Zheng, Y.S., Wang, Z.G. and Ai, S.H. Acta. Metall. Sin. (China) (1995) 31 (3), A105–A114 (in Chinese) | 1996 | International Journal of Fatigue | fatigue / ai | materials-fatigue-journal | 1,2 |
| 10.1016/j.ijfatigue.2025.109068 | Pre-corrosion very-high-cycle AI-fatigue in completion string | 2025 | International Journal of Fatigue | fatigue / ai | corrosion, materials-fatigue-journal | 1,2 |

## 4. 未実行
- Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/search`): 時間制約のため 11 クエリとも未実行。
- 日本語文献の別枠検索: 時間制約のため未実行。