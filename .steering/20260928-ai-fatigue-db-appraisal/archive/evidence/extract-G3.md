# 抽出結果 G3（AF011–AF014）

担当: AF011 / AF012 / AF013 / AF014。全レコード完了（未着手なし）。

---

## AF011

- アクセス範囲: **全文**（Europe PMC / PMC12367725 の fullTextXML、SAGE本体は403）。訂正記事（corrigendum, PMC13578129）も全文取得。
  使用URL: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12367725/fullTextXML`、`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13578129/fullTextXML`、Crossref `10.1177/09727531251359872` / `10.1177/09727531261489932`、OpenAlex。journals.sagepub.com の両URL（本体・訂正記事）はいずれも403で読んでいない。

- 書誌（一次で見えた値）:
  著者（全員）: Shalu（単名、ORCID 0009-0001-4941-0065）; Nidhi Verma（責任著者, ORCID 0000-0003-1463-5499）; Kapil Dev; Aradhana Balodi Bhardwaj（ORCID 0000-0002-3554-6500）; Krishan Kumar。
  誌名: Annals of Neurosciences。巻33・号1・頁73–84。年2025。オンライン公開日 2025-08-20（Crossref `published: {2025,8,20}`）。DOI表記: `10.1177/09727531251359872`。
  受理関連: 本文に "Received 2025 Jun 12; Revised 2025 Jun 26; Accepted 2025 Jul 2." とあり。

- 訂正・撤回・懸念表明: **あり（Corrigendum）**。主論文の前付に逐語: "This article has been corrected. See Ann Neurosci. 2026 Sep 14:09727531261489932." Crossref: `update-to` = `{DOI: 10.1177/09727531251359872, type: correction, label: Correction, updated: 2026-09-14}`。
  訂正記事（DOI `10.1177/09727531261489932`, 2026-09-14 online, PMC13578129）の全文逐語:
  「In the above-mentioned article, three references (43, 44, and 45) were inadvertently included in the reference list due to the transposition of author and journal details during manuscript preparation, as the cited works had similar author names and titles. Upon review, the authors identified these references as redundant. Accordingly, references 43, 44, and 45 given below have been removed from the article, and the subsequent references and their corresponding in-text citations have been renumbered throughout the manuscript.」
  削除された文献3件の逐語（原文ママ）:
  「43. Hadar LL, Sood S and Fox CR. Information overload in decision making: Effects of decision context and individual differences. J Behav Decis Mak 2021; 34(2): 151–165. DOI: 10.1002/bdm.2203」
  「44. Shariff AF, Greene JD and Uhlmann EL. The rise of moral machines: Integrating ethics and AI. Nat Mach Intell 2020; 2:13–15. DOI: 10.1038/s42256-019-0130-5」
  「45. Jones AB, Smith CD and Lee EF. The cognitive cost of artificial intelligence in daily life: Attention, fatigue, and trust. J Cogn Sci 2021; 32(4): 567–580. DOI: 10.1234/jcs.2021.32.4.567」
  （事実のみ記す: 削除された文献45のDOIプレフィックスは "10.1234" — テスト/プレースホルダーDOIとして一般に使われる文字列と同一である。判定はしない。）
  末尾: 「The online version of the article has been corrected.」PubMed（Europe PMC）の当該レコードは `pubTypeList: Published Erratum`、`abstractText: "[This corrects the article DOI: 10.1177/09727531251359872.]."`（PubMed定型文、訂正内容の詳細は含まない）。

- 研究デザイン: 横断・質問紙調査（quantitative survey, Pearson相関）。本文逐語: "A structured survey was administered both online and offline to a sample of 500 adults... Descriptive statistics and Pearson correlation analyses were conducted to explore the relationships between these variables."

- 対象・国・募集方法・収集時期:
  国/地域: インド Delhi–NCR地域。逐語: "A convenience sampling technique was employed to recruit 500 participants between the ages of 18–30 years, from the Delhi-NCR region of India."（標本抽出法＝convenience sampling、便宜的抽出）
  収集時期: 記載なし（オンライン・オフライン併用のみ記載、具体的な月日レンジは本文に無し）。
  Inclusion Criteria逐語: "Individuals aged between 18 and 30 years..."; "Regular users of digital technology..."; "Participants possessing a basic understanding or awareness of AI concepts."; "Participants who voluntarily provide informed consent for participation."
  Exclusion Criteria逐語: "Infrequent or non-users of digital technology..."; "Surveys with incomplete data, inconsistent answers, or random responding, which could compromise data integrity."

- N（募集・除外・解析の各段。単位）: N=500人（解析用サンプル）で統一。募集数・除外数・脱落率の内訳記載なし（除外基準は定性的に記述されているが、除外前の募集数や除外された件数の実数は記載なし）。Table 1の性別内訳 290男性(58%)+210女性(42%)=500人 と abstract の "500 adults (290 males, 210 females)" は一致。
  ★内部不整合: Table 1「Age group」項の内訳は 18–20歳 290人(58%)・21–25歳 110人(20%)・26–30歳 100人(18%) で人数合計は500人だが、パーセンテージ合計は58+20+18=**96%**（100%にならない）。かつ、Inclusion Criteriaは「18–30歳」なのに「18–20歳」という年齢区分自体が20歳以下を強調しており、本文Resultの"mean age of 24.2 ± 3.4 years"（Abstract Methods）と「58%が18–20歳」は整合性に乏しい（平均24.2歳・SD3.4なら18–20歳が過半数を占めるのは分布として不自然）。事実として記録するのみで解釈はしない。

- AIの種類・利用文脈: 特定のAIツール名の指定なし。「AI技術全般」への態度・不安・利用頻度・信頼を測定（"daily technology use"の文脈）。

- 疲労（Decision Fatigue）の操作化:
  構成概念名: Decision Fatigue（5件法, 5-point scale）。出典: 「developed from pre-existing scales or previously verified」としか書かれておらず、**具体的な尺度名・出典文献の引用なし**（記載なし）。項目数: 本文中に総項目数の明記なし。Table 5の列見出しに現れる項目文言（逐語、尺度原文かどうか不明）: "Mental exhaustion", "Too many choices", "AI conserves mental energy", "Cognitive exhaustion", "Lowered attention", "Information overload", "Lower self-assurance"。
  ★疲労の帰属: Table 6の変数名（逐語）"AI Tools Prevent Mental Energy from Decision-making (APME)"、"Attention Capacity Lowered after Long AI Exposure (ACL)"、"AI Causes Information Overload (AIO)" は明示的に疲労をAIの利用に帰属させる文言。一方Table 2の "Decision fatigue (5-point scale)" という総合得点の項目文自体は本文に逐語で示されていない。

- その他の主要変数: AI Anxiety（7段階, 7-point scale, 総合得点）、Attitude toward AI（1–7）、Cognitive Skills（自己評価, 5-point scale）、Trust in AI（信頼性・生産性・コントロールの下位次元）。

- 解析手法: 記述統計（平均・SD・歪度・尖度）とPearson相関分析（SPSS使用）。回帰・多変量解析・信頼性係数（Cronbach's α等）の報告なし。

- 主要結果（表・図ごとに報告された数値を逐語で）:
  **Abstract**: "r = 0.81, p = .053"（Attitude×使用頻度）／ reliability "r = 0.597", productivity "r = 0.985", control "r = 0.829"（trust関連、"measured via reliability, productivity, and control"という一文にまとめて提示）／ "r = 0.905"（long-term AI use と mental exhaustion, attention strain, information overloadを一括で結びつける一文）／ "r = −0.360"（long-term AI use × decision-making self-confidence）。
  **Table 2**（記述統計, N=500）: AI anxiety M=4.62 SD=1.14 min1.20 max7.00 skew−0.28 kurt−0.44／Attitude M=5.01 SD=1.06 min2.00 max7.00 skew−0.36 kurt−0.19／Cognitive skills M=3.72 SD=0.78 min1.00 max5.00 skew0.03 kurt−0.61／Decision fatigue M=3.94 SD=0.83 min1.20 max5.00 skew−0.22 kurt−0.37。
  **Table 3**（表タイトルに"N = 500"明記）: Attitude towards AI × Frequency of technology use, r=0.806, 脚注逐語 "Pearson correlation coefficient (r) = 0.806, p = .053 (marginally significant). *p < .10."
  **Figure 1キャプション逐語**: "The Above Scatterplot Depicts the Relationship Between Attitude Toward AI and Frequency of Technology Use **Across Six Survey Items**." ／ "The results highlight a strong, positive association between the two variables (r = 0.806, p = .053)."
  **Table 4**（Correlation Matrix of Trust and Confidence in AI, タイトルにNの明記なし, 変数=6項目）: Automating decisions×Reliable=0.311, ×Confidence in tasks=0.583, ×Improves productivity=0.498, ×Human judgment preferred=0.735, ×Control=0.520／Reliable×Confidence=0.486, ×Productivity=0.597, ×Human judgment=0.557, ×Control=0.829／Confidence×Productivity=0.985, ×Human judgment=0.510, ×Control=0.423／Productivity×Human judgment=0.516, ×Control=0.497／Human judgment×Control=0.902。p値・t値・df・N記載なし。
  **Table 5**（Influence of AI on Cognitive Skills and Decision Fatigue, タイトルにNの明記なし, 項目=7）: Mental exhaustion×Too many choices=−0.03, ×AI conserves energy=−0.09, ×Cognitive exhaustion=−0.25, ×Lowered attention=0.10, ×Info overload=−0.02, ×Lower self-assurance=−0.04／…／Lowered attention×Lower self-assurance=**0.32**（本文で強調, 表注逐語: "The bolded value (r = 0.32) indicates a moderate positive correlation between Lowered attention and Lower self-assurance in decision making."）。p値・t値・df・N記載なし。
  **Table 6**（Long-term Interaction with AI Systems and Cognitive-psychological Outcomes, タイトルにNの明記なし, 項目=7: LTI, TMC, APME, RI, ACL, AIO, LSA）: LTI×TMC=0.671, ×APME=0.915, ×RI=0.996, ×ACL=0.874, ×AIO=0.905, ×LSA=−0.360。他の全ペアも表に記載（0.639〜0.996の範囲、LSAとの相関は−0.401〜0.315）。p値・t値・df・N記載なし。
  ★**分析単位（人か項目か）の記載の食い違い（逐語で並べる）**:
  - Table 3のタイトル: "Correlation Between Attitude Toward AI and Frequency of Technology Use (**N = 500**)" → 人（500人のサンプル）を示唆。
  - しかし直後のFigure 1のキャプション: "Depicts the Relationship...**Across Six Survey Items**" → 6個の「調査項目」間の相関であることを示唆し、Table 3の"N=500"と整合しない。
  - Table 4・5・6は列見出しが個々の質問項目名（例: "Automating decisions", "Mental exhaustion", "LTI"）であり、いずれもタイトル・脚注にNの記載が無い。r=0.985（Table4, confidence×productivity）やr=0.996（Table6, LTI×RI）のような極端に1に近い値は、N=500人の個人データでの相関としては非常に稀であり、少数の項目（例えば6〜7項目の平均得点）間の相関である可能性を示唆するが、本文はこの点を明示的に説明していない。事実の並記のみ、判定はしない。

- 著者自身が述べる限界: 本文に明示的な「Limitations」節はない。Discussionに以下の逐語あり: "The marginal significance suggests that more research with larger and more diverse samples may be necessary to fully confirm and clarify the strength of this relationship, as individual differences in digital literacy, exposure to AI technologies, and resource availability may also have an impact on the results." Future Suggestions節: "Future investigations should adopt a longitudinal methodology..."（横断デザインである点を暗に認める記述のみ）。

- 倫理承認・同意（方法節と末尾宣言、別々に逐語）:
  方法節（"Data Collection"）: "The participants were well informed about the goal of the study and were assured that their answers would remain anonymous and confidential. Informed consent was obtained from all respondents prior to participation."
  方法節（"Ethical Considerations"）: "Participation was voluntary, and no personally identifiable information was collected. The study adhered to ethical research guidelines and ensured that all participants were aware of their right to withdraw from the study at any point without any negative consequences."
  末尾宣言欄「Statement of Ethics」: "Informed consent was obtained from all individual participants included in the study. Participation was voluntary, and confidentiality of all participant data was maintained throughout the research process."
  末尾宣言欄「Patient Consent」: "This manuscript does not involve any direct data collection from patients. No patient data (including identifiable information, medical records, or personal health details) were used, and therefore, patient consent was not required."
  ★注: いずれの節にも「機関倫理審査委員会（IRB/倫理委員会）による承認」の明記（委員会名・承認番号）は**一切ない**。「Informed consent」「voluntary」「no PII collected」等はあるが、審査機関名や承認番号は記載なし。

- 事前登録・データ/材料公開・資金・利益相反: 事前登録の記載なし。データ/材料公開の記載なし。資金: "Funding: The authors received no financial support for the research, authorship and/or publication of this article." 利益相反: "The authors declared no potential conflicts of interest with respect to the research, authorship and/or publication of this article."

- 設計別チェック（A. 横断研究、8項目。全文取得済み）:
  1（組入れ基準明確）: Yes — Inclusion/Exclusion Criteria節に明記。
  2（対象者と場の記述）: Yes（一部） — "Delhi-NCR region", 年齢18–30, デジタル機器の日常利用者、と記述。ただし職業・社会経済階層等の詳細記述はなし。
  3（曝露の妥当な測定）: Unclear — AI anxiety/attitude尺度の出典が「pre-existing scales or previously verified」としか書かれず、具体的な尺度名・妥当性の記載なし。
  4（アウトカムの客観的・標準的測定）: No/Unclear — Decision fatigueの尺度出典が不明（上記と同様）、自己報告のみ。
  5（交絡因子の特定）: No — 交絡因子への言及なし。
  6（交絡への対処）: No — 統計的統制（回帰等）は行われておらず、Pearson相関のみ。
  7（アウトカムの妥当な測定）: Unclear（尺度出典不明のため）。
  8（統計解析の適切さ）: No/Unclear — 相関行列のみでp値・t値・df・Nの表記が一部（Table3のみ）に限られ、多重比較の調整、信頼区間、外れ値/正規性の検討（歪度・尖度の報告はあるが検定なし）の記載がない。相関のみで因果的主張（"H4を支持"等）をしている点も統計的厳密性の観点で弱い（事実として指摘、判定はしない）。

- 気づいた内部不整合（再掲・出所つき）:
  (a) Abstract "r = 0.81" vs Table 3/本文 "r = 0.806"（丸め方の違いの可能性はあるが数値表記が不一致）。出所: Abstract "Result"節 / Table 3。
  (b) Abstract の trust "reliability r=0.597, productivity r=0.985, control r=0.829" という並記は、Table 4の実際の変数ペアと一致しない（reliability×productivity=0.597は正しいが、confidence in tasks×productivity=0.985であり "productivity" 単体の値として0.985を挙げるのは表の構造上不正確）。出所: Abstract Result / Table 4。
  (c) Abstract の "r = 0.905" は long-term AI use と "mental exhaustion, attention strain, and information overload" の3変数すべてに対して単一の値として書かれているが、Table 6ではLTI×mental exhaustion(TMC?)=0.671、LTI×ACL(attention)=0.874、LTI×AIO(info overload)=0.905と個別に異なる値。出所: Abstract Result / Table 6。
  (d) Table 1「Age group」パーセンテージ合計が96%（100%にならない）。出所: Table 1。
  (e) 訂正記事における削除参考文献45のDOI (`10.1234/jcs.2021.32.4.567`) がプレースホルダー的な文字列。出所: 訂正記事本文 / 元論文References 45。
  (f) 「分析単位（人か項目か）」の食い違い、上記主要結果セクション内で詳述。出所: Table 3タイトル vs Figure 1キャプション。

---

## AF012

- アクセス範囲: **全文**（Wayback Machine保存の MDPIページ, 2025年キャプチャ）。MDPI本体は直接アクセス403（WebFetch・curl両方）。
  使用URL: `https://web.archive.org/web/2025/https://www.mdpi.com/2227-7080/13/11/486`、補助でCrossref `10.3390/technologies13110486`、OpenAlex、Semantic Scholar（abstract確認用）。

- 書誌（一次で見えた値）: 著者: Syed Md Faisal Ali Khan; Salem Suhluli（Crossref表記）/ Salem Ali Suhluli（OpenAlex表記, 表記ゆれあり）。所属: 両著者とも "Department of Management Information Systems, College of Business, Jazan University, Jazan 45142, Saudi Arabia"。
  誌名: Technologies。巻13・号11・論文番号486。逐語: "Technologies 2025, 13(11), 486; https://doi.org/10.3390/technologies13110486"。
  Submission received: 7 September 2025 / Revised: 15 October 2025 / Accepted: 21 October 2025 / Published: 28 October 2025。特集号: "This article belongs to the Special Issue Human–AI Collaboration: Emerging Technologies and Applications"。

- 訂正・撤回・懸念表明: Crossref `update-to`: None、`relation`: {}（記載なし・訂正なし）。

- 研究デザイン: 定量・横断（構造方程式モデリング, SEM-PLS）。逐語: "Cognitive constructs... were examined using Structural Equation Modeling–Partial Least Squares (SEM-PLS)."

- 対象・国・募集方法・収集時期:
  逐語: "The study received data from 998 academic researchers, including PhD students and faculty members from a variety of fields, all of whom were actively involved in research. The responses are taken from the global top 500 ranking universities across diversified fields. Data was collected from personal contacts using social media and a structured communication channel (Refer Appendix E). Data was filtered for master's or above courses. Using a stratified random sample approach, people were put into groups depending on how often they said they used Generative AI tools like ChatGPT, Elicit, or Scite. Anonymous internet questionnaires were used to collect the data over the course of three months, making sure that everyone who took part did so willingly."
  国: 明記なし（"global top 500 ranking universities"とのみ、著者所属はサウジアラビア）。収集期間: 「3か月間」とのみ、具体的な暦月・年の記載なし。標本抽出法: 「stratified random sample approach（GenAI利用頻度で層化）」＋募集経路は「personal contacts using social media and a structured communication channel」＝実質的に便宜的・スノーボール的経路（無作為抽出枠の記載はなし）。

- N（募集・除外・解析の各段。単位＝人）: N=998人（researchers）。募集数・除外数の内訳記載なし（"filtered for master's or above courses"という絞り込みはあるが、絞り込み前後の人数は記載なし）。

- AIの種類・利用文脈: Generative AI（GenAI）全般。具体例として逐語: "tools like ChatGPT, Elicit, or Scite"。研究活動（文献レビュー・執筆支援・データ分析）での利用。

- 疲労（Task Fatigue & Mental Exhaustion）の操作化:
  構成概念名: "Task Fatigue & Mental Exhaustion"（TFME、3項目）。出典: 引用[80,81]（本文中では番号のみ、書誌詳細は未確認—Reference節は本抽出で未取得）。
  項目例（逐語, IPMA節より）: TFME3 "Even small research tasks feel overwhelming when I am tired."（スコア52.753、直接効果 −0.002）。他のTFME1/2項目文言は本文に逐語で示されず。
  ★AIへの帰属: Cognitive Load（CL）とTask Fatigue（TFME）自体の項目文言はAIに直接言及していない（例: CL1 "I often feel mentally overloaded…"）。AIへの帰属は別構成概念「Generative AI Immersion（GenAI1–4）」で測定されており、GenAI2の項目逐語: "Generative AI helps me simplify complex tasks during my research"、GenAI3: "I rely heavily on AI tools to assist in data analysis or content generation"。疲労とAI利用は構造モデル上のモデレーション関係（GenAI immersion × Cognitive Load / × Task Fatigue）として結び付けられており、疲労尺度そのものはAI利用に限定した項目文にはなっていない。

- その他の主要変数: Research Engagement（RE, 3項目）、Resilience to Cognitive Fatigue（RCF, 3項目）、Research Quality & Academic Influence（RQAI, 8項目, アウトカム）。合計6構成概念・24項目。構成概念と項目数の対応表（Table 1逐語）: "Cognitive Load — CL1–CL3 — 3 — [78,79]"／"Task Fatigue & Mental Exhaustion — TFME1–TFME3 — 3 — [80,81]"／"Generative AI Immersion — GenAI1–GenAI4 — 4 — Adapted from [82,83]"／"Research Engagement — RE1–RE3 — 3 — [84,85]"／"Resilience to Cognitive Fatigue — RCF1–RCF3 — 3 — [86]"／"Research Quality & Academic Influence — RQAI1–RQAI8 — 8 — [58,87]"。

- 解析手法: SEM-PLS（PLS-SEM, CB-SEMではなくPLS-SEMを選択した理由を明記: "it works better with complicated prediction models that have many moderation and mediation effects and can handle non-normal data distributions"）。IPMA（Importance-Performance Map Analysis）も実施。

- 主要結果（報告された数値を逐語で）:
  **Table 2 収束的妥当性**: Cognitive Load α=0.886, rho_a=0.886, rho_c=0.929, AVE=0.814／Generative AI α=0.915, rho_a=0.915, rho_c=0.940, AVE=0.796／Research Engagement α=0.897, rho_a=0.897, rho_c=0.936, AVE=0.829／Research Quality & Academic Influence α=0.912, rho_a=0.913, rho_c=0.929, AVE=0.620／Resilience to Cognitive Fatigue α=0.883, rho_a=0.883, rho_c=0.928, AVE=0.810／Task Fatigue & Mental Exhaustion α=0.895, rho_a=0.896, rho_c=0.935, AVE=0.826。
  **Table 3 判別的妥当性(HTMT)の一部**: Cognitive Load×Research Engagement=0.805／Task Fatigue×Resilience=0.765（他の値は0.017〜0.104の範囲で低い）。
  **Table 4 モデル適合度**: R²: Research Engagement=0.521、Research Quality & Academic Influence=0.709、Resilience to Cognitive Fatigue=0.472。Q² predict: 0.516/0.674/0.468。SRMR: saturated=0.054, estimated=0.057。Chi-square: 2824.476 と 2850.245。NFI: 0.845 と 0.843。
  **Table 5 仮説検定（逐語の数値, β=Original Sample, T=T Statistics, p=p Values）**:
  H1 Cognitive Load→RQAI: β=−0.175, T=5.371, p=0.000, f²=0.049
  H2 Task Fatigue & Mental Exhaustion→RQAI: β=−0.124, T=3.722, p=0.000, f²=0.027
  H3 GenAI×Cognitive Load→RQAI: β=−0.067, T=3.966, p=0.000, f²=0.025
  H4 GenAI×Task Fatigue→RQAI: β=−0.114, T=6.261, p=0.000, f²=0.082
  H5 Cognitive Load→Research Engagement→RQAI: β=0.137, T=5.50, p=0.000
  H6 Cognitive Load→Resilience→RQAI: β=0.014, T=2.398, p=0.017
  H7 Task Fatigue→Research Engagement→RQAI: β=0.012, T=1.544, p=0.123（非有意）
  H8 Task Fatigue→Resilience→RQAI: β=0.104, T=4.647, p=0.000
  IPMA個別項目（逐語, 効果量|スコア）: GenAI1 "I regularly use tools like ChatGPT or Elicit for literature review and writing support" 効果−0.236, スコア39.156／GenAI2 効果−0.229, スコア38.294／GenAI3 効果−0.238, スコア38.838／GenAI4 効果−0.232, スコア38.385／CL1 "I often feel mentally overloaded…" 効果−0.009, スコア38.339／CL2 効果−0.009, スコア38.566／CL3 効果−0.009, スコア38.203／TFME3 "Even small research tasks feel overwhelming when I am tired." スコア52.753, 直接効果−0.002。
  分析単位: 個人(N=998人)。表タイトル・本文とも単位の食い違いは確認されなかった。

- 著者自身が述べる限界: 節「Limitations of the Study」逐語: "The research employed Self-reported online survey data may have introduced social desirability and self-selection biases to the study. Several controls were applied to reduce risks. Voluntary and anonymous participation reduced societal pressure to respond positively... Although these measures reduce bias, the authors recognize that self-reported perceptions may differ from actual behavior. Mixed-method or longitudinal study using behavioral and observational data to supplement survey responses could improve validity."

- 倫理承認・同意（方法節 と 末尾宣言、別々に逐語）:
  ★方法節（3.4. Sample and Data Collection, 末尾）: 「The study had ethical approval from the institutional review board, which protected the rights and privacy of all the people who took part.」
  方法節（3.7. Ethical Considerations, 全文）: 「Participants were informed about the study's objectives, confidentiality measures, and the voluntary nature of their participation. No personal identifiers were collected. All procedures complied with the ethical standards of research involving human subjects.」
  ★末尾宣言欄「Institutional Review Board Statement」: 「**Not applicable.**」
  ★末尾宣言欄「Informed Consent Statement」: 「**Not applicable.**」
  ★★内部不整合（重要・出所つき）: 本文3.4節は「the institutional review board」から倫理承認を得たと明言する一方、論文末尾の正式な宣言欄（MDPI標準フォーマット）は Institutional Review Board Statement / Informed Consent Statement とも「Not applicable」としている。承認機関名・承認番号はいずれの箇所にも記載なし。

- 事前登録・データ/材料公開・資金・利益相反:
  事前登録: 記載なし。
  Data Availability Statement逐語: 「The original contributions presented in this study are included in the article/Supplementary Materials. Further inquiries can be directed to the corresponding author.」
  Funding逐語: 「This research received no external funding.」
  Conflicts of Interest逐語: 「The author declares no financial or personal relationships that could have influenced the work reported in this paper.」（"The author"と単数形— 2名著者にもかかわらず単数表記、事実として記録）。
  Supplementary Materials逐語: 「The following supporting information can be downloaded at: https://www.mdpi.com/article/10.3390/technologies13110486/s1.」

- 設計別チェック（A. 横断研究、8項目。全文取得済み）:
  1（組入れ基準明確）: Unclear — 「998 researchers, PhD students and faculty, filtered for master's or above」との記述はあるが、具体的な組入れ/除外の判定手順（誰が除外され何人だったか）は記載なし。
  2（対象者と場の記述）: Unclear — 「global top 500 ranking universities」とあるが具体国・分野比率・職位比率などは提示されず。
  3（曝露の妥当な測定）: Yes（一部）— GenAI Immersion尺度は先行文献[82,83]から適応、Table 2でCronbach's α=0.915, AVE=0.796と高い信頼性・妥当性指標が報告されている。
  4（アウトカムの客観的・標準的測定）: No — Research Quality & Academic Influenceは自己報告のみ（客観的な研究成果指標、例えば被引用数等の使用なし）。
  5（交絡因子の特定）: No — 交絡因子への明示的言及なし。
  6（交絡への対処）: Unclear — SEM-PLSでモデレーション・メディエーションを統制しているが、年齢・分野・経験年数等の人口統計学的交絡の統制は記載なし。
  7（アウトカムの妥当な測定）: Yes（一部）— RQAI尺度もTable 2で信頼性・妥当性指標が報告されている（α=0.912, AVE=0.620）。
  8（統計解析の適切さ）: Yes（相対的に良好）— SEM-PLSの手法選択理由、収束的/判別的妥当性、モデル適合度（SRMR, NFI, R², Q²）、仮説ごとのβ・T統計量・p値・f²を報告しており、AF011より統計的透明性は高い。ただしHTMT一部（0.805, 0.765）がやや高く判別的妥当性に懸念の余地がある点は本文で議論されていない（事実の指摘のみ）。

- 気づいた内部不整合（出所つき）:
  (a) 方法節「institutional approval obtained」vs 末尾宣言「Not applicable」（上記倫理承認の項で詳述、最重要）。
  (b) 著者名の表記ゆれ: Crossref「Salem Suhluli」 vs OpenAlex「Salem Ali Suhluli」。出所: 各API応答。
  (c) Conflicts of Interest文が単数形「The author」（2名著者の論文）。出所: 末尾宣言欄。

---

## AF013

- アクセス範囲: **全文**（PDF直接取得に成功, `https://ijahss.net/assets/files/1755327497.pdf`, 8頁）。

- 書誌（一次で見えた値）: 著者: Mahlatse Ragolane（Research Associate, REGENT Business School, Johannesburg, South Africa）; Shahiem Patel（Academic Dean, 同校）。誌名: International Journal of Arts, Humanities and Social Sciences（PDF本文表記）／Crossrefでは "International Journal of Arts , Humanities & Social Science"（表記ゆれ: PDF本文と入力レコードの誌名・Crossrefのコンテナタイトルとで微妙に異なる: 入力は"...Social Science"、PDF本文ヘッダは"...Social Sciences"（複数形の有無））。ISSN 2693-2547(Print)/2693-2555(Online)。巻06・号08・頁53–60。年2025年8月。DOI: 10.56734/ijahss.v6n8a7（Crossref `published: 2025-08-16`）。

- 訂正・撤回・懸念表明: Crossref `update-to`: None、`relation`: {}（記載なし）。

- 研究デザイン: ナラティブ・レビュー（質的、二次資料）。方法節の逐語: 「This study adopts a qualitative, secondary research design to explore the phenomenon of AI fatigue... A narrative literature review with thematic synthesis was employed.」

- 対象・国・募集方法・収集時期: 該当なし（一次データ収集なし、文献レビューのため）。

- N: 該当なし（個別参加者データなし）。採択文献数は明示されていない（下記チェックD参照）。

- AIの種類・利用文脈: AI全般（生成AIを含む）。職場・教育・日常決定における利用文脈。

- 疲労（AI fatigue）の操作化: 構成概念の定義（測定尺度ではなく概念定義）。逐語: 「Defined as the exhaustion or overwhelm triggered by constant interaction with AI-driven tools and the relentless pressure to adapt, AI fatigue reflects a broader digital malaise...」量的尺度は使用されていない（レビュー論文のため測定なし）。★AIへの帰属: 定義文自体が明示的に「AI-driven tools」との相互作用に帰属させている。

- その他の主要変数: 該当なし（概念整理のみ）。

- 解析手法: 主題分析（thematic synthesis）による質的統合。逐語: 「Findings were discussed thematically into core themes as cognitive overload, emotional exhaustion, organisational drivers, ethical opacity, and structural inequality.」

- 主要結果: 該当なし（数量的結果なし、概念的知見の整理）。

- 著者自身が述べる限界: 方法節末尾に逐語: 「As a secondary research study, the analysis is contingent on the quality, availability, and scope of existing literature. Given the novelty of the topic, much of the evidence is conceptual or based on small-scale studies, with potential publication bias towards negative impacts of AI. These limitations reinforce the need for future empirical, longitudinal, and cross-cultural research to validate and extend these findings.」

- 倫理承認・同意: 方法節・末尾とも記載なし（人を対象とした一次データ収集がないため、IRB/インフォームドコンセントの節自体が存在しない。全文を確認したが該当節なし）。

- 事前登録・データ/材料公開・資金・利益相反: いずれも**記載なし**（全文8頁を確認したが、Funding/Conflict of Interest/Data Availability/事前登録のいずれの宣言も本文・末尾に存在しない）。

- 設計別チェック（D. システマティック／その他のレビュー、11項目+ 検索式・採択件数等。全文取得済み）:
  1（問いが明確か）: Yes — 「examining its cognitive, emotional, and organisational drivers」等、目的は明記されているが、PICO形式のような定式化されたリサーチクエスチョンはなし。
  2（組入れ基準が問いに適切か）: Unclear — 「published peer-reviewed journal articles, conference papers, industry reports, and policy briefs from 2017 to 2025」との範囲指定はあるが、明確な組入れ/除外の判定基準（質的閾値など）は逐語で明記されていない。
  3（検索戦略が適切か: 式・日付・情報源）: Unclear/No — 情報源は逐語で明記: 「Sources were identified through systematic searches of academic and professional databases, including Google Scholar, Scopus, ResearchGate, PubMed and IEEE Xplore.」検索キーワードも逐語: 「Search keywords included "AI fatigue", "artificial intelligence burnout", "technostress", "digital burnout", "generative AI stress".」しかし**検索式（ブール演算子等の組み合わせ）・検索実行日・検索期間（実施日ベース）の記載はなし**（対象文献の発表年範囲2017–2025は記載されているが、これは検索実行日ではない）。
  4（情報源が十分か）: Yes（一部）— 学術DB5種＋業界プラットフォームを使用したと明記: 「To ensure practitioner insights were captured, targeted searches were also conducted on reputable organisational and industry platforms.」（具体名は記載なし）。
  5（研究の批判的吟味の基準が適切か）: No — 個々の採択文献に対する質的評価（critical appraisal）の実施・基準の記載なし。
  6（吟味を2名以上が独立に行ったか）: No/記載なし — 2名の著者はいるが、独立スクリーニング・吟味の手順（一致率等）の記載なし。
  7（抽出の誤りを減らす手順）: No/記載なし。
  8（統合方法の適切さ）: Yes（一部）— 主題分析（thematic synthesis）という統合手法は明記。
  9（出版バイアスの評価）: 部分的にYes — 上記「限界」節で「potential publication bias towards negative impacts of AI」と自己言及あり（正式な評価手法ではなく言及のみ）。
  10（提言がデータに支持されているか）: Unclear（判定は行わない方針のため、記載の有無のみ: 提言セクションは存在する）。
  11（今後の研究への指示が適切か）: Yes — 「future empirical, longitudinal, and cross-cultural research」と明記。
  ★**採択件数**: 明記なし（レビュー対象となった文献の総数がどこにも数値として記載されていない。References節には約30件の文献が列挙されているが、これが「採択件数」と同義かどうかは本文に明言なし）。
  ★**検索日**: 記載なし。
  ★**PRISMA流れ図の有無**: なし（本文中にフロー図の言及・図表番号の割当てもなし。図はFigure 1のみで概念モデル図）。

- 気づいた内部不整合: 誌名表記ゆれ（入力レコード"International Journal of Arts, Humanities & Social Science" 単数形 vs PDF本文・Crossref"...Social Sciences"複数形、および著者所属機関名表記）。出所: 入力レコード / PDF本文表紙 / Crossref `container-title`。

---

## AF014

- アクセス範囲: **全文**（OJSページ本文 + 実PDF本体20頁を直接ダウンロードして取得。当初の `/QS/article/view/70890/46360` はビューア用HTMLでPDF本体ではなく、真のPDFは `https://apcz.umk.pl/QS/article/download/70890/46360/235124` から取得）。

- 書誌（一次で見えた値、★出版社ページのVolume表示とDOI文字列をそのまま転記）:
  著者: Piotr Sosiński（責任著者, ORCID 0009-0006-3673-4067）; Natalia Piasecka（University Clinical Center of the Medical University of Warsaw, Warsaw, Poland, ORCID 0009-0001-2361-8060）。
  誌名: Quality in Sport。
  ★**出版社ページ上のVolume表示（逐語）**: 「Vol. 55 (2026)」（パンくずリスト表示） / 「Issue」欄にも「Vol. 55 (2026)」。引用生成機能（ISO 690形式, 逐語）: 「SOSIŃSKI, Piotr and PIASECKA, Natalia. AI Fatigue and Mental Health Implications: A Comprehensive Literature Review. Quality in Sport. Online. 6 May 2026. **Vol. 55**, p. 70890. [Accessed 28 September 2026]. DOI 10.12775/QS.2026.54.70890.」ページ埋め込みのOpenURLメタタグにも `rft.volume=55` と明記。
  ★**DOI文字列（逐語）**: 「https://doi.org/10.12775/QS.2026.54.70890」（DOI中の巻番号らしき部分は「**54**」）。
  ★★**内部不整合（出版社ページ内で完結、重要）**: 出版社ページ・引用生成・OpenURLメタタグはすべて一貫して「Vol. 55 (2026)」と表示する一方、DOI文字列自体には「2026.**54**.70890」と「54」が埋め込まれている。Volume表示（55）とDOI内の数字（54）が一致しない。事実の記録のみ、原因の推測はしない。
  Section: 「Health Sciences」。論文番号（page）: 70890。Published: 「2026-05-06」。License: 「Copyright (c) 2026 Piotr Sosiński, Natalia Piasecka」「This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.」投稿日・受理日: OJSページ・PDF本文いずれにも記載なし（Submission/Revised/Accepted日付の表示なし。AF012のMDPIページと対照的）。

- 訂正・撤回・懸念表明: 記載なし（OJSページ上に訂正・撤回の表示なし）。

- 研究デザイン: 文献レビュー（"A Comprehensive Literature Review"、著者による分類名。システマティックレビューを名乗ってはいない）。

- 対象・国・募集方法・収集時期: 該当なし（一次データ収集なし）。レビュー対象文献の対象者: 「doctors, technology professionals, factory workers, and office employees」（個別研究の対象者の要約）。

- N: 該当なし。★**採択件数の記載に内部不整合あり**:
  - Abstract逐語: 「This review summarizes **22 studies** published between March 2025 and March 2026.」
  - OJSページ上に列挙された参考文献リストの実数: **[1]〜[22]の22件**（カウント一致）。
  - しかし本文 Introduction逐語: 「This literature review synthesizes findings from **30 studies** to address three key questions...」
  - 本文 Section 3冒頭逐語: 「**The 30 reviewed studies** used a variety of research methods, reflecting the complexity of AI fatigue research.」
  - つまりAbstract(22)・参考文献リスト件数(22)と、本文2箇所(30, 30)が一致しない。出所: Abstract / References節 / Introduction / Section 3冒頭（いずれも取得PDF内）。

- AIの種類・利用文脈: AI全般（生成AI含む）。医療（臨床文書作成支援等）・技術職・製造業・事務職での利用。

- 疲労（AI fatigue）の操作化: 個別尺度の使用なし（レビューのため）。概念定義（Abstract逐語）: 「AI fatigue... workers feel stressed by the technology, overwhelmed by too much information, anxious about AI capabilities, and tired from constantly having to adapt to new systems.」レビュー対象文献が用いた尺度の言及（逐語）: 「Studies used validated measurement tools, including burnout scales (e.g., Maslach Burnout Inventory components), technology stress perception scales, AI anxiety inventories, and patient safety attitude questionnaires... Several studies also developed new measures specifically designed for AI-related stressors, such as AI-induced workload scales and AI transparency [scales]」（末尾一部OCR欠落の可能性あり、原文ママ）。

- その他の主要変数: burnout、technostress、cognitive overload、workplace stress、clinician burnout、human-computer interaction（Keywordsより）。

- 解析手法: 該当個別統計なし。定性的総合（narrative synthesis相当）。「quantitative effect sizes, odds ratios, and β coefficients」に注目したと明記（Introduction）が、レビュー自体が独自のメタ解析を行った記載はない。

- 主要結果（報告された数値を逐語で）:
  「Cross-sectional surveys were the most common research design, with samples ranging from 200 to 683 participants drawn from technology professionals, healthcare workers, and general employees [2-3, 5, 10, 13].」
  「While the HCI-guided intervention showed promising pilot results (25% stress reduction) [3], rigorous evaluation through randomized controlled trials is lacking.」
  IPMA的な個別数値の引用は本論文内になし（他研究の統計を要約する形のみ）。

- 著者自身が述べる限界（8.2 Limitations and Gaps、逐語）:
  「Temporal Dynamics: Most studies employed cross-sectional designs, limiting understanding of how AI fatigue develops over time...」
  「Intervention Effectiveness: While the HCI-guided intervention showed promising pilot results (25% stress reduction) [3], rigorous evaluation through randomized controlled trials is lacking.」
  「Generalizability: Samples were often limited to specific geographic regions (e.g., Pakistan, Turkey, Indonesia, UK) or occupational groups, raising questions about generalizability across cultural contexts and sectors...」
  「Mechanism Specificity: While mediation pathways have been identified, the specific psychological mechanisms remain underspecified...」
  「Positive Outcomes: The literature focuses heavily on negative outcomes... with less attention to potential positive impacts...」
  「Individual Differences: ...systematic investigation of individual difference moderators... is limited.」
  「Measurement Standardization: The field lacks standardized, validated measures of AI-specific stressors and fatigue...」

- 倫理承認・同意（本文と末尾宣言。レビュー論文だが末尾に定型宣言欄あり、逐語）:
  本文中に倫理承認・同意に関する記述箇所は無い（一次データ収集がないため、Methods的な節にも言及なし）。
  末尾「Disclosure」内、逐語:
  「Institutional Review Board Statement — Not Applicable.」
  「Informed Consent Statement — Not Applicable.」
  「Data Availability Statement — Not Applicable.」
  「Funding Statement — The article did not receive any funding.」
  「Conflict Of Interest — The authors declare no conflict of interest.」
  「Acknowledgements — This research has not received any administrative or technical support.」
  ★特記: 「Declaration of the use of generative AI and AI-assisted technologies in the writing process」節が存在し逐語: 「During the preparation of this work, the author used generative AI to assist with grammar and stylistic editing to ensure appropriate academic language and for translation into English. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the final content of the manuscript.」（AI疲労を論じる論文自身が執筆にAIを使用したことを開示している。事実の記録のみ）。

- 事前登録・データ/材料公開・資金・利益相反: 上記の宣言欄と同一（事前登録の言及なし、データ公開「Not Applicable」、資金なし、COIなし）。

- 設計別チェック（D. システマティック／その他のレビュー、11項目 + 検索式・採択件数等。全文取得済み）:
  1（問いが明確か）: Yes — Introduction逐語「to address three key questions: (1) How does AI implementation affect clinician burnout? (2) What are the mechanisms linking AI use to user well-being and career outcomes? (3) What organizational factors and design interventions can reduce AI-related stress and fatigue?」
  2（組入れ基準が問いに適切か）: Unclear — 対象期間「Between March 2025 and March 2026」は明記されるが、組入れ/除外の質的基準（研究デザイン限定の有無、言語制限等）の記載なし。
  3（検索戦略が適切か: 式・日付・情報源）: **No** — データベース名・検索式（ブール演算子等）・検索実行日のいずれも本文中に一切記載がない（AF013にあった「Google Scholar, Scopus...」のような情報源列挙すら本論文には存在しない）。
  4（情報源が十分か）: Unclear/No — 情報源の名称自体が記載されていないため評価不能。
  5（研究の批判的吟味の基準が適切か）: No — 個々の採択研究への質的評価基準の記載なし。
  6（吟味を2名以上が独立に行ったか）: No/記載なし — 著者2名だが独立スクリーニングの手順記載なし（"Check: [NP]"という著者貢献欄の記載はあるが、スクリーニング手順としての説明ではない）。
  7（抽出の誤りを減らす手順）: No/記載なし。
  8（統合方法の適切さ）: Unclear — 「narrative」的な主題別章立て（4.1 Clinician Burnout等）はあるが、正式な統合手法名の明記はなし。
  9（出版バイアスの評価）: No — 言及なし（AF013にあった publication bias への言及はAF014になし）。
  10（提言がデータに支持されているか）: 判定しない方針のため、節の存在のみ記録（9. Future Directions and Recommendations節あり）。
  11（今後の研究への指示が適切か）: Yes — Limitations節・Future Directions節に具体的な今後の研究課題（縦断研究・RCT・測定尺度の標準化等）を列挙。
  ★**採択件数**: **内部不整合あり**（上記N節参照）: Abstract=22件・References=22件 vs 本文2箇所=30件。
  ★**検索日**: 記載なし（対象文献の発表期間「March 2025–March 2026」のみで、検索実行日の記載なし）。
  ★**PRISMA流れ図の有無**: なし（本文中に図表としてのPRISMAフロー・スクリーニング人数の推移の記載一切なし）。

- 気づいた内部不整合（まとめ、出所つき）:
  (a) 出版社ページのVolume表示「55」とDOI文字列内の「54」の不一致。出所: OJSページ本文・引用生成・OpenURLメタタグ vs DOI文字列自体。
  (b) 採択研究数「22」（Abstract・References件数）vs「30」（Introduction・Section 3冒頭、2箇所）。出所: PDF本文各所（上記に頁内引用済み）。
  (c) AI疲労を論じる論文自体が、執筆にAIを使用したと開示（皮肉的だが事実）。出所: Disclosure節「Declaration of the use of generative AI」。

---

## 未確認・読んでいない範囲の明記

- AF011: journals.sagepub.com の本体・訂正記事いずれも403で直接閲覧していない（Europe PMC全文で代替、内容は一次のXML全文であり欠落は無いと考えられるが、SAGE版のレイアウト・図版そのものは未確認）。
- AF012: MDPI本体ページは403で直接閲覧できず、Wayback Machineの2025年キャプチャ（更新版でない可能性）で代替。Appendix A–Eの表内容は本抽出では詳細に読み切っていない（Table 5「Hypothesis Testing」とTable 1–4は読了、Table 6「Gap Analysis」・Table 7・Appendix A–Eは見出しのみ確認し中身は未読）。Reference [78]–[87]（各尺度の出典文献）の書誌詳細は未確認。
- AF013: 全文読了。未読範囲なし。
- AF014: 全文（PDF20頁）読了。Reference [1]–[22]各文献の個別内容（本文が要約する統計値の一次ソースまでは遡っていない）は未検証。
