# ふるい分けの記録 —— C3

> 候補の定義（protocol.md §1）: **権限と責任がそろったまま人の側へ返っても、残務（解釈・検証・応答）が人へ移ること**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 373 |
| 段 1 で採った | 87 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 0 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 13 |
| 段 2 の判定（メインの訂正の後） | 該当 1 ／ 部分 6 ／ 非該当 6 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 73 |

## 結論

★ **既出**（該当: C3-0214 [P400]。⚠️ 工学の記述 1 件で、「そろったままでも」を主張として立てた文献ではない）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C3-0214 | 該当 | 本文 | The code column contains the abbreviation for the mode and the party that is uniquely responsible for control actions: O – operator; or A – automation. | Table 1 (§3.2) | MoO(モード)表が「control(権限)」と「responsible(責任)」を同一の当事者(operator)に一致させて定義(要素1)。CA状態からS3(operator is in control)への遷移で権限・責任が人間側へ戻り(要素2)、その際に人間は「understand the developing situation」(解釈)「make the correct actions… |  | ★ メインが本文で照合 |
| C3-0089 | 部分 | 本文 | AI was sold as a way to remove drudgery and return judgment to the worker. Automate the repetitive work, and free the person for higher-value thinking. In practice, the higher-value thinking is oversight: monitoring and … | p.1 | 権限(authority)・責任(accountable)がともに人に帰属した状態で、AIが生成した出力の検証(verification)という残務が人へ課されることを「Verification Overrun」として定式化。「return judgment to the worker」の語で権限が人へ返る構図、「held accountable for a verification」で責任、「a… | 段 2 担当は「該当」→ メインが下げた（説明責任と検証能力の不均衡として定式化・そろったままを述べない） | メインが抄録・取り出したテキストと機械照合 |
| C3-0185 | 部分 | 抄録のみ | We developed and clinically validated a rule-guided, agent-based LLM that assists gastrointestinal (GI) biopsy reporting by automating report structuring while preserving full diagnostic authority with the pathologist. | 抄録 | 「preserving full diagnostic authority with the pathologist」は権限(要素1)が病理医に留まることを明示するが、「責任」の語は抄録に出てこず、要素(1)は権限のみで部分的。「Agent outputs were reviewed」は検証という残務(要素3)を示唆するが、これは今回の検証研究自体の評価手続きの記述であり、日常臨床でのルーチンな残… |  | メインが抄録・取り出したテキストと機械照合 |
| C3-0188 | 部分 | 本文 | Clinicians need the authority to override or set aside AI recommendations whenever those recommendations conflict with the patient's values, the clinical context, or the clinician's own professional assessment. | §6.3 Normative Requirements for MHC (Pri… | Meaningful Human Control (MHC)の規範的要件として、権限(authority to override)と専門的責任(professional responsibility)がともに臨床医に帰属すること(要素1・2)を明示し、同時にAI出力の信頼性・限界を判断する検証・解釈作業(要素3、traceability/epistemic responsibility)を臨床医に… | 段 2 担当は「該当」→ メインが下げた（権限は返るのでなく保持され続ける） | メインが抄録・取り出したテキストと機械照合 |
| C3-0233 | 部分 | 抄録のみ | the assumption of human oversight and liability | 抄録・5メカニズムの(1) | 『oversight(監督)とliability(責任)が人間側にあることを前提とする』設計であることが明示されており(要素: 権限と責任がそろったまま人の側にある)、かつ『vigilanceの負担/oversight・liabilityの負担をユーザーが吸収する』ことも明示されている(要素: 残務が人へ移る)。AIツールが解釈労働(トライアンドエラー学習・診断支援)を肩代わりしつつ監督・責任は人… | 段 2 担当は「該当」→ メインが下げた（moral crumple zone は責任と統制の不一致の側） | メインが抄録・取り出したテキストと機械照合 |
| C3-0258 | 部分 | 本文 | Writing burden becomes editing burden. Thinking burden becomes verification burden. Care burden becomes risk-routing burden. Companionship burden becomes attachment burden. Decision burden becomes accountability burden. | §16 Displacement, Not Removal (p.20) | 「keeps humans in real authority」で権限、「Decision burden becomes accountability burden」で責任が人に帰属することを述べ(要素1・2)、同時に「Thinking burden becomes verification burden」など検証・解釈という残務(要素3)が人へ移ることを列挙。Runtime Testの表は権限(… | 段 2 担当は「該当」→ メインが下げた（負担の移転は明言・権限と責任がそろって返る構図は無い） | メインが抄録・取り出したテキストと機械照合 |
| C3-0283 | 部分 | 抄録のみ | The responsibility to verify the diagnosis, assess risk, and accept the consequences of action remained with the attending physician. | 抄録・症例記述部分 | 医学生がAIを用いて臨床問題を再構成(解釈労働をAIが肩代わり)した上で、『診断の検証・リスク評価・行動の結果を引き受ける責任は指導医(attending physician)に留まった』と明記されている。権限(結果を引き受ける)と責任(検証・リスク評価)がそろったまま人間側にあり、検証という残務が人へ移る、というC3の3要素をいずれも満たす。 | 段 2 担当は「該当」→ メインが下げた（責任は返るのでなく保持され続ける） | メインが抄録・取り出したテキストと機械照合 |
| C3-0002 | 非該当 | 本文 | Several problems can intrinsically arise when the responsibility and authority are not assigned to the same agent, including the additional monitoring actions the responsible agent must perform. | Metric 2: Mismatches Between Responsibil… | 「残務が人へ移る」に相当する記述（責任と権限のmismatch時に人間へ追加の監視タスクが生じる）は本文全体で繰り返し確認できる。しかしC3が要求する『権限と責任がそろったまま(整合を保ったまま)人の側へ返る』という前提とは逆方向で、本論文のMetric 2はむしろ責任と権限が一致していない(mismatch)場合にのみ監視負担が生じると論じており、整合している場合(mismatch=0)に残務が… |  |  |
| C3-0142 | 非該当 | 抄録のみ | intelligent systems into high-risk industries is reshaping how work is performed, decisions are made, and responsibility is distributed... they also introduce under-recognised sociotechnical risks, including degraded hum… | 抄録 | 抄録が述べるのは「degraded human decision authority」(権限の劣化・低下)であり、C3が定義する「権限と責任がそろったまま人の側へ返る」構図とは逆に近い(権限がむしろ失われていく懸念)。「責任」が権限と対で人に帰属したまま残るという記述も、「解釈・検証・応答」という具体的な残務の記述も抄録中に無いため、3要素とも確認できない。 |  |  |
| C3-0166 | 非該当 | 本文 | we note that humans have limited capabilities and authority is interconnected with responsibility. | Abstract | 「authority is interconnected with responsibility」は権限と責任の相互関連性のみを述べ、C3の要素(1)の断片に触れるに留まる。本論文の主張は逆方向で、人間の能力の限界を理由に機械主導で権限を人間から機械へ移すこと(machine-initiated trading of authority)を正当化するものであり、「権限と責任がそろったまま人の側へ返… |  |  |
| C3-0173 | 非該当 | 抄録のみ |  |  | 抄録は『人間と自動化の役割を責任・権限の二次元空間で分析する手法(Dimensional Role Analysis)』を提案するのみで、『権限と責任がそろったまま人の側へ返る』『残務が人へ移る』という主張は抄録中に見当たらない。responsibility/authorityという語は登場するが、C3定義の3要素（整合/返る/残務）のいずれも確認できない。 |  |  |
| C3-0177 | 非該当 | 抄録のみ |  |  | 抄録は『AI自動意思決定における人間関与の構造的縮減』『人間介入の権利の意義と限界』を検討する憲法学的論文であると述べるが、これは主にデータ主体(決定対象者)の権利の実効性を論じるものであり、C3が定義する『権限と責任がそろったまま人の側(操作者・利用者側)へ返っても残務が移る』という構図とは対象が異なる。定義の3要素は抄録中に確認できない。 |  |  |
| C3-0225 | 非該当 | 抄録のみ |  |  | 抄録は『自律チームメイトが人間オペレーターと責任・権限・タスクを共有(share)し、Playbookインターフェースで機能配分を委譲(delegate)する』という設計を述べるのみ。『権限と責任がそろったまま人の側に返る』『残務が人へ移る』という主張は抄録中に明示されていない。 |  |  |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C3-0002 | 2013 | Measuring Human-Automation Function Allocation | 10.1177/1555343413490166 | 機能配分の複数指標の一つに責任-権限の関係を含む計算的枠組み。整合時の残務の有無は本文確認要 → 採る | 照合 |
| C3-0004 | 2011 | Model-based metrics of human-automation function allocation in complex work environments |  | C3-0002 と同系列(Georgia Tech)の機能配分枠組み。同様の理由で段階2確認 → 採る | 未実施（逸脱 2） |
| C3-0016 | 2026 | Beyond Automation: Reimagining Human-Centered Systems for AI-Mediated Institutions | 10.5281/zenodo.22801769 | 「責任-権限の整合」を設計原則としつつ、整合下でも残る「不可視の制度的貢献」を提示。C3該当の可能性 → 採る | 未実施（逸脱 2） |
| C3-0017 | 2026 | Beyond Automation: Reimagining Human-Centered Systems for AI-Mediated Institutions | 10.5281/zenodo.22801770 | C3-0016 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0022 | 2026 | The Calculus of Sovereign Delegation An Architectural Proposition for Separating Machine Intelligence from Hum… | 10.5281/zenodo.19688559 | AIへの権限委譲に人間の識別可能性・実行可能性・証拠的関与を要求。権限が人間に残る場合の実質的関与(残務)を論じる可能性 → 採る | 未実施（逸脱 2） |
| C3-0023 | 2026 | The Calculus of Sovereign Delegation An Architectural Proposition for Separating Machine Intelligence from Hum… | 10.5281/zenodo.19688560 | C3-0022 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0027 | 2026 | Use of Agent-Based AI Applications in Research Institutions | 10.52403/ijrr.20260119 | AIエージェント支援下でも責任を委譲せず人間が解釈・優先順位付け・意思決定を保持すると明記。C3に強く合致 → 採る | 未実施（逸脱 2） |
| C3-0030 | 2026 | An Ethical Framework for Human–Machine Interaction in Civil Low-Altitude Aviation Systems: High-Consequence Re… | 10.5281/zenodo.21899311 | 低高度航空の倫理枠組み。責任に比例した知識・介入能力・拒否権の保持を中心的問いとする → 採る | 未実施（逸脱 2） |
| C3-0031 | 2026 | An Ethical Framework for Human–Machine Interaction in Civil Low-Altitude Aviation Systems: High-Consequence Re… | 10.5281/zenodo.21899310 | C3-0030 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0041 | 2024 | Human–AI Capital Allocation for Large-Scale Robotic Systems: A Framework for Efficient, Accountable, and Adapt… | 10.64388/irev7i9-1713393 | 大規模ロボットシステムの資本配分における人間-AI間の権限・責任の相互作用を論じる意思決定系。段階2で確認 → 採る | 未実施（逸脱 2） |
| C3-0042 | 2026 | AICOS_OS_Decision_Authority_Science_Yasin_Kalafatoglu_2026.pdf | 10.5281/zenodo.18525474 | 人間の最終意思決定権限保持に伴う監視疲労・認知負荷(監視という残務)を論じる → 採る | 未実施（逸脱 2） |
| C3-0043 | 2026 | AICOS_OS_Decision_Authority_Science_Yasin_Kalafatoglu_2026.pdf | 10.5281/zenodo.18525475 | C3-0042 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0049 | 2026 | PREPARING FOR A HUMAN–AI FUTURE: A HUMAN-CENTRIC FRAMEWORK FOR COLLABORATIVE READINESS | 10.5281/zenodo.20176291 | 人間中心の協働準備性枠組みで「意思決定権限」を次元に含み、人間がAIを導く/問う/統治する関与を論じる → 採る | 未実施（逸脱 2） |
| C3-0050 | 2026 | PREPARING FOR A HUMAN–AI FUTURE: A HUMAN-CENTRIC FRAMEWORK FOR COLLABORATIVE READINESS | 10.5281/zenodo.20176290 | C3-0049 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0052 | 2025 | Designing Human?AI Collaboration Models for Commercial Decision Systems: A Business Management Perspective | 10.64388/irev9i1-1713981 | 権限・責任・制御の意図的配分を論じる商業意思決定系のデザイン原則。段階2で確認 → 採る | 未実施（逸脱 2） |
| C3-0068 | 2026 | Human-in-the-Loop Enhances Machine Learning Inference in Intraoperative Optical Coherence Tomography Glioma Im… | 10.3390/medsci14020263 | HITL手術支援(OCT)で人間の文脈的解釈と権限行使の自信を実証的に検討。C3の実装研究として合致 → 採る | 未実施（逸脱 2） |
| C3-0075 | 2026 | When Machines Moderate Machines: Toward a Governance Vacuum Theory |  | AI生成×AIモデレーションの各構成で人間レビューが説明責任を回復する条件を検討。整合時の残務(人間レビュー)の可能性 → 採る | 未実施（逸脱 2） |
| C3-0085 | 2025 | IMm-Technologies: A Meta-Epistemological Framework for Responsible Knowledge Production under Persistent Exper… | 10.5281/zenodo.18048442 | 人間が較正・文脈付け・拒否権を担う継続的検証の認識論的枠組み。適応的人間-機械系での残務(検証)を論じる → 採る | 未実施（逸脱 2） |
| C3-0086 | 2025 | IMm-Technologies: A Meta-Epistemological Framework for Responsible Knowledge Production under Persistent Exper… | 10.5281/zenodo.18048443 | C3-0085 と同一文献(重複エントリ)。同じ理由で採る | 未実施（逸脱 2） |
| C3-0089 | 2026 | Verification Overrun: The Safety Hazard Inside AI Oversight | 10.5281/zenodo.20874288 | 「検証超過」として、移行後に人へ委ねられる検証責務と検証能力(権限を含む)の関係を定式化。C3該当の可能性が高い → 採る | 照合 |
| C3-0097 | 2026 | Implementation of human teaming in aviation industry: The Turkish Airlines case study | 10.54941/ahfe1007830 | トルコ航空の人間-AIチーミング事例研究。AI導入後も乗務員に残る認知的負荷・解釈作業を検討する可能性 → 採る | 未実施（逸脱 2） |
| C3-0102 | 2026 | Rethinking Aviation Safety in the Age of Autonomy: From Tools to Cognitive Partners | 10.1007/978-3-032-29456-2_15 | 抄録なし。『ツールから認知パートナーへ』の再定義は人間役割の残務変化を示唆しうる | 未実施（逸脱 2） |
| C3-0110 | 2026 | Artificial intelligence and robotics in Ophthalmology – Understanding the spectrum, respecting the limits | 10.4103/kjo.kjo_8_26 | AI自律性スペクトラムで説明責任は人間に残ると述べる、整合下の残務論に近い可能性があり判断は段2に委ねる | 未実施（逸脱 2） |
| C3-0142 | 2026 | Human Authority in the Age of Intelligent Systems: A Sociotechnical Framework for Decision Assurance and Psych… | 10.54941/ahfe1008213 | Human Authority Index、権限を形式的に保持しても認知過負荷・心理的負荷が生じると論じ整合下の残務に近い | 照合 |
| C3-0144 | 2020 | Transformations of Responsibility in the Age of Automation: Being Answerable to Human and Non-Human Others | 10.1007/978-3-476-04896-7_2 | 自動化時代の責任の変容、人間・非人間への応答可能性を論じる哲学的考察で残務(応答)論に近い可能性 | 未実施（逸脱 2） |
| C3-0148 | 2026 | Structuring Human-AI Collaboration in Residential Property Valuation Using Levels of Automation | 10.47772/ijriss.2026.100500087 | LOAを用いた不動産評価のHuman-AI協働、ガバナンス層があっても専門家責任は譲渡不能と明記、整合下の残務の良い一致 | 未実施（逸脱 2） |
| C3-0150 | 2026 | TOWARD A HYBRID MAQĀṢID-BASED ARTIFICIAL INTELLIGENCE FATWĀS GOVERNANCE MODEL: Rethinking Ijtihad Authority, A… | 10.21274/epis.2026.21.01.1-21 | AIは補助的でありイジュティハードの認識論的責任は学者に厳格に残ると明記、整合下で解釈作業が人間に残る例 | 未実施（逸脱 2） |
| C3-0153 | 2026 | Using AI in HR decision-making: what HR leaders must change to avoid bias, blind automation and loss of trust? | 10.1108/shr-12-2025-0126 | AIは意思決定支援に留め人間が最終責任を保持、構造化レビュー段階を要求し残務(レビュー)の記述あり | 未実施（逸脱 2） |
| C3-0159 | 2026 | The coalescent architecture of agency: normative directionality as the key to human–AI integration | 10.1007/s00146-026-02979-x | 人間AI統合における主体性の規範的方向性の理論的考察(抄録なしだがタイトルから深い理論的関与を示唆) | 未実施（逸脱 2） |
| C3-0160 | 2026 | Human-in-the-Loop Automation Workflow for SAR Review and Escalation Using Low-Code Platforms | 10.37082/ijirmps.v14.i2.233001 | SAR審査のHITLワークフロー、調査員が最終決定権者として責任を持つと明記、残務(調査判断)の記述あり | 未実施（逸脱 2） |
| C3-0166 | 2011 | Authority and responsibility in human–machine systems: probability theoretic validation of machine-initiated t… | 10.1007/s10111-011-0193-4 | 人間中心自動化における権限と責任の相互関連性、機械主導の権限委譲の確率論的検証。基礎文献として関連性高い | 照合 |
| C3-0167 | 2026 | Framework for an Intelligent Reliability Engineering Assistant: A Rag-Based Genai Approach Leveraging Python C… | 10.1109/aqtr70159.2026.11577866 | 信頼性工学アシスタントのRAG基盤GenAI、AIへの自律的意思決定権限の移譲を明示的に回避し人間責任を完全維持、残務が丸ごと人間に残る例 | 未実施（逸脱 2） |
| C3-0169 | 2026 | An AI-Assisted Research Automation System for Scholarly Paper Retrieval and Review With Workflow Orchestration | 10.3844/jcssp.2026.2082.2091 | 学術論文検索AI自動化ワークフロー、人間の監督と最終意思決定権限の維持を明記、残務(最終判断)の記述あり | 未実施（逸脱 2） |
| C3-0171 | 2012 | Special issue on human–automation coagency | 10.1007/s10111-011-0197-0 | 『人間-自動化共同エージェンシー』特集号(抄録なしだがテーマがC3と直接関連) | 未実施（逸脱 2） |
| C3-0172 | 2025 | Does AI in Healthcare Need an Editor-in-Chief? A Leading Example of True Human Oversight. | 10.1163/15718093-12423581 | AI医療における真の人間監督を論じ、監督者に継続的批判的検討の実務作業を要求。整合下の残務の良い一致 | 未実施（逸脱 2） |
| C3-0173 | 2023 | Dimensional Role Analysis: The Role of Humans and Automation for Increasingly Autonomous Aviation Systems | 10.1109/icns58246.2023.10124260 | 自律航空システムにおける人間と自動化の役割の二次元分析手法(責任と権限)、基礎的枠組み論文で関連性高い | 照合 |
| C3-0177 | 2026 | Human Intervention in Artificial Intelligence-Based Automated Decision-Making | 10.21592/eucj.2026.50.161 | AI自動意思決定への『人間介入の権利』の憲法学的検討、形式的権利があっても実質的関与が構造的に縮減されると論じ整合下の残務に近い | 照合 |
| C3-0179 | 2020 | An Ethical Inquiry of the Effect of Cockpit Automation on the Responsibilities of Airline Pilots: Dissonance o… | 10.1007/s10551-020-04640-z | コックピット自動化とパイロット責任の倫理的考察(抄録なし。『不協和か有意味な統制か』というタイトルがC3と直結しうる) | 未実施（逸脱 2） |
| C3-0180 | 2026 | Automation and autonomy in the IVF laboratory: concepts and implications for embryologists. | 10.1016/j.rbmo.2026.105920 | IVFラボの自動化と自律性、臨床責任の保持を論じる概念的レビューで残務(責任保持)に言及 | 未実施（逸脱 2） |
| C3-0182 | 2025 | AI AS A CO-PILOT (Enhancing Aviation Safety and Efficiency while Keeping Human Pilots at the Center) | 10.55041/ijsrem48815 | 航空AIコパイロットにおける人間操縦士中心の統合ガバナンス提言、残務(監視)への言及あり | 未実施（逸脱 2） |
| C3-0185 | 2026 | End-to-End Clinical Validation of a Human-Supervised Large Language Model Agent for Enterprise Surgical Pathol… | 10.1016/j.modpat.2026.101049 | LLM病理報告支援、病理医が完全な診断権限を保持しつつ実際に出力レビュー・誤り修正を行うことを実証。整合下の残務の強い実証例 | 照合 |
| C3-0188 | 2026 | Beyond Algorithmic Oversight: Internal Morality of Medicine and Meaningful Human Control in AI-Assisted Care | 10.3390/healthcare14121638 | 『意味のある人間の統制』は形式的監督では不十分で実質的臨床判断が人間に残ると論じる。整合下の残務の良い一致 | 照合 |
| C3-0190 | 2026 | Substance, Form, and Machines: AI Assistance and Human Normative Judgment in Taxation | 10.32591/coas.ojre.0902.01041s | AI支援があっても実質的規範判断(経済的実質・比例性等)は人間に必然的に残ると明記。整合下の残務の強い一致 | 未実施（逸脱 2） |
| C3-0193 | 2026 | Collaborative Intelligence in Accounting: A Human + AI Complementarity Framework for Professional Work | 10.64044/vpm19y22 | 会計における人間+AI補完フレームワーク、専門家が独立検証・つき合わせ等の検証作業を行うと明記。整合下の残務の強い一致 | 未実施（逸脱 2） |
| C3-0194 | 2026 | Trusting the Algorithm or Trusting the Nurse? Critical Care Nurses' Experiences of Automation Bias and Profess… | 10.1111/nicc.70620 | 集中治療AIアラートに対する看護師の自動化バイアスと職業的自律性の質的研究、ベッドサイド評価で解釈・上書きする実証。残務の強い実証例 | 未実施（逸脱 2） |
| C3-0198 | 2025 | Generative Design and Parametric Architecture: Redefining the Role of the Architect through Artificial Intelli… | 10.36948/ijfmr.2025.v07i05.59414 | 生成的設計における建築家の役割再定義、建築家がアルゴリズム知性の評価者として残務(評価・監督)を担うと記述 | 未実施（逸脱 2） |
| C3-0200 | 2026 | TRANSFORMATION OF MANAGERIAL ROLES UNDER THE INTEGRATION OF ARTIFICIAL INTELLIGENCE TECHNOLOGIES INTO MANAGERI… | 10.32782/easterneurope.51-11 | AI統合下の経営役割変容、経営者介入が決定的であり続ける条件を論じており残務論に近い | 未実施（逸脱 2） |
| C3-0203 | 2026 | Structuring administrative judgment for reasoning-oriented AI: a case of foreign food facility registration | 10.1007/s00146-026-03058-x | 抄録なし。AI推論支援下での行政判断構造化というタイトルから、整合していても人間の判断が残る可能性があり判断留保 | 未実施（逸脱 2） |
| C3-0205 | 1991 | Appropriate automation - Integrating technical, human, organizational, economic and cultural factors | 10.1016/0005-1098(91)90127-n | 抄録なし。適切な自動化統合という古典的人的要因論文で判断留保 | 未実施（逸脱 2） |
| C3-0209 | 2025 | When an AI “Agentforce” enters the workforce: generative AI, employment relations, and the changing social con… | 10.1007/s41469-025-00196-2 | 抄録なし。AIエージェントの労働参入による雇用関係変化というタイトルで判断留保 | 未実施（逸脱 2） |
| C3-0212 | 2026 | An auxiliary book editing and proofreading algorithm based on rule–semantic hybrid modeling | 10.1117/12.3117916 | AI編集支援でも編集者が最終決定権と修正フィードバックを保持し続けると明示、検証作業が残る | 未実施（逸脱 2） |
| C3-0214 | 2026 | Formal descriptions of MASS Operational Envelope and Operational Design Domain | 10.1088/1742-6596/3299/1/012001 | MASS操船の権限委譲設計で、引継ぎ時のout-of-the-loop問題と人間側の作業を明示 | 照合 |
| C3-0215 | 2026 | Artificial Intelligence in Judicial Decision-Making: Can a Robot Replace a Judge? | 10.36475/12.1.1 | AIは裁判官に取って代われず、解釈・文脈評価・道徳判断という残務は人間に留まると主張 | 未実施（逸脱 2） |
| C3-0218 | 1990 | Appropriate Automation – Integrating Technical, Human, Organizational, Economic, and Cultural Factors | 10.1016/s1474-6670(17)52057-1 | C3-0205と同一内容の重複エントリ、同様に判断留保 | 未実施（逸脱 2） |
| C3-0219 | 2026 | HUMAN VALIDATION IN HOLTER MONITORING: THE ROLE OF SPECIALIZED TECHNICAL ANALYSIS IN THE ERA OF ARTIFICIAL INT… | 10.56238/levv17n63-074 | AI自動判定後も専門技師による検証層が不可欠と明示、整合していても残務が残る典型例 | 未実施（逸脱 2） |
| C3-0220 | 2007 | Panel on authority distribution in human-machine systems | 10.3182/20070904-3-kr-2922.00079 | 抄録なし。人間-機械系における権限配分パネルというタイトルで判断留保 | 未実施（逸脱 2） |
| C3-0223 | 2020 | Human Factors Guideline in the Human Machine Interface Design of Datalink System | 10.1007/978-3-030-51828-8_32 | 抄録なし。データリンクシステムHMIの人的要因ガイドラインで判断留保 | 未実施（逸脱 2） |
| C3-0225 | 2019 | The Evaluation of a Playbook Interface for Human-Autonomy Teaming in Single Pilot Operations | 10.1109/dasc43569.2019.9081620 | パイロットと自律チームメイト間の権限委譲インターフェースで、監督・適応責任の残存を扱う | 照合 |
| C3-0226 | 2026 | Malpractice in the machine age: Legal and ethical responses to machine learning in medical imaging. | 10.1016/j.radi.2026.103339 | AI画像診断の医療過誤論で、検証済みシステム使用時も臨床医の検証責任が残ると論じる | 未実施（逸脱 2） |
| C3-0227 | 2025 | AI IN PHOTOJOURNALISM ETHICS AND MANAGEMENT | 10.29121/shodhkosh.v6.i3s.2025.6767 | AIフォトジャーナリズム倫理で、編集者の権限・職務保持による説明責任実践を扱う | 未実施（逸脱 2） |
| C3-0228 | 2016 | Synthesis of allocations of authority in air traffic concepts of operation | 10.1109/dasc.2016.7778047 | 抄録なし。航空管制における権限配分の統合というタイトルで判断留保 | 未実施（逸脱 2） |
| C3-0252 | 2025 | Moral Responsibility and Artificial Intelligence | 10.5040/9781509956876 | AIの責任ギャップ概念に反論し複数人が責任を保持し続けるとする議論で判断留保 | 未実施（逸脱 2） |
| C3-0258 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.6084/m9.figshare.32456571.v1 | AI出力の検証負担が利用者に残ることを明示するsynthetic remainder概念、C3型の典型 | 照合 |
| C3-0259 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.5281/zenodo.20426157 | C3-0258と同一内容の重複エントリ | 照合 |
| C3-0260 | 2026 | Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems | 10.5281/zenodo.20426158 | C3-0258と同一内容の重複エントリ | 照合 |
| C3-0265 | 2026 | The Scaffold Jump Pattern: Progressive, Evidence-Gated Fading of Human Roles in Artificial Intelligence System… | 10.21203/rs.3.rs-10414106/v1 | 抄録なし。AIシステムにおける人間役割の段階的フェードを扱うタイトルで判断留保 | 未実施（逸脱 2） |
| C3-0279 | 2025 | Effects of knowledge and importance on responsibility in human-AI decision making | 10.1038/s41598-025-32513-w | 人間-AI意思決定における責任帰属の実験研究で、C3に関連しうるため判断留保 | 未実施（逸脱 2） |
| C3-0283 | 2026 | Instant Answers, Enduring Responsibility: Teaching Judgment in the Age of Artificial Intelligence | 10.1177/00031348261422742 | AI診断支援後も医師が検証・リスク評価・結果引受という残務を負うと明示、C3の典型例 | 照合 |
| C3-0287 | 2025 | Responsibility for errors of generative AI in legal practice: analysis of "hallucination" cases and profession… | 10.23939/law2025.48.531 | AI幻覚エラーに対し弁護士に全責任が集中する現状の負担を記述、C3に関連しうる | 未実施（逸脱 2） |
| C3-0293 | 2026 | Exploring the perceptions of athletes and DCOs on the remote sampling procedure in anti-doping testing: shifti… | 10.3389/fspor.2026.1825926 | 遠隔検体採取システムの導入で監督者から利用者へ負担が移ることを実証、C3に関連しうる | 未実施（逸脱 2） |
| C3-0300 | 2025 | When AI Writes Back: Ethical Considerations by Physicians on AI-Drafted Patient Message Replies | 10.48550/arxiv.2508.13217 | AI下書き返信後も医師が倫理的責任を負うと明示、C3の典型例 | 未実施（逸脱 2） |
| C3-0302 | 2020 | Don't lose your coin! Investigating Security Practices of Cryptocurrency Users | 10.1145/3357236.3395535 | 暗号資産のセルフカストディが鍵管理責任をユーザーに置くHCI研究(DIS)、権限が内在していても残務が残る可能性 → 採る | 未実施（逸脱 2） |
| C3-0305 | 2026 | The Pseudo-Confidence Paradox: The Epistemic Gap in Everyday AI Use | 10.3390/philosophies11030097 | 生成AI利用時の認識論的ギャップ・ユーザーの検証負担を論じるHCI寄りの研究 → 採る | 未実施（逸脱 2） |
| C3-0307 | 2025 | Online Dating Platform Safeguards and Self-Protection: How Dating Platforms Characterise, Respond to, and Safe… | 10.1145/3706599.3719825 | マッチングアプリの安全策がユーザー責任へ移る点を論じるHCI研究(CHI EA) → 採る | 未実施（逸脱 2） |
| C3-0310 | 2023 | Cleaning Up the Streets: Understanding Motivations, Mental Models, and Concerns of Users Flagging Social Media… |  | SNSのフラグ機能でプラットフォームとユーザー間の労働・責任分配を論じるHCI研究 → 採る | 未実施（逸脱 2） |
| C3-0312 | 2022 | Integrating artificial intelligence in pathology: a qualitative interview study of users’ experiences and expe… | 10.1038/s41379-022-01123-6 | 病理診断へのAI統合で専門家の役割・責任の変化を論じるインタビュー研究 → 採る | 未実施（逸脱 2） |
| C3-0315 | 2025 | From Patient Burdens to User Agency: Designing for Real-Time Protection Support in Online Health Consultations | 10.1145/3714394.3756335 | オンライン医療相談のプライバシー労務がユーザーへ転嫁される点とLLM支援ツールSafeShareを論じるHCI研究 → 採る | 未実施（逸脱 2） |
| C3-0316 | 2026 | MindCopilot: Towards Formalizing and Evaluating Granular Human-LLM Co-Writing | 10.48550/arxiv.2605.23535 | LLM協調執筆でユーザーの受容・編集という残務を定式化・測定するHCI研究 → 採る | 未実施（逸脱 2） |
| C3-0321 | 2026 | Building health-literate artificial intelligence. | 10.1038/s41562-026-02595-1 | 題名から健康リテラシーに配慮したAI構築を論じる可能性、抄録欠如のため題名で暫定採用 → 採る | 未実施（逸脱 2） |
| C3-0322 | 2026 | We Need Explanation Cards to Connect Explanation Algorithms to the Real World | 10.48550/arxiv.2606.16786 | 説明アルゴリズムの解釈負担が従来ユーザー側に残っていた問題を記述し、説明カードで対応を提案するXAI研究 → 採る | 未実施（逸脱 2） |
| C3-0324 | 2026 | To Believe or Not To Believe: Comparing Supporting Information Tools to Aid Human Judgments of AI Veracity | 10.1145/3805713.3820430 | AI生成回答の真偽判断をユーザーが担う負担と支援情報ツールを比較するHCI研究 → 採る | 未実施（逸脱 2） |
| C3-0325 | 2026 | Towards Effective Generation of Interactive Visualizations with Vibe Coding: An Empirical Study |  | vibeコーディングにおける開発労働の転嫁と人間-エージェント協業戦略を論じるHCI研究 → 採る | 未実施（逸脱 2） |
| C3-0328 | 2021 | Personality Shifting Agent to Remove Users' Negative Impression on Speech Recognition Failure | 10.5220/0010687400003060 | 音声認識失敗後のユーザーの言い直し負担とエージェントの責任受容を扱うHRI研究 → 採る | 未実施（逸脱 2） |
| C3-0343 | 2025 | Mind the Gaps: Logical English, Prolog, and Multi-agent Systems for Autonomous Vehicles | 10.4204/eptcs.416.9 | 自動運転車の責任シフトが人間ドライバーに負担を課さないことを目指す交通規則推論システムの研究 → 採る | 未実施（逸脱 2） |
| C3-0347 | 2025 | THE ETHICAL STARTUP? | 10.52214/vib.v11i.14119 | DNAマーケットプレイスの消費者エンパワーメントの約束と有限合理性による倫理的負担の残存を論じる研究 → 採る | 未実施（逸脱 2） |
| C3-0365 | 2026 | Compliance without infrastructure: the ethics of AI-driven safety governance in small-scale logistics | 10.1007/s43681-026-01142-y | 中小物流事業者向けAI主導安全ガバナンスのコンプライアンス倫理(抄録欠如、題名から対話系に該当) → 採る | 未実施（逸脱 2） |
| C3-0367 | 2026 | The Principia of Generative-AI Pedagogy: Three Theories of Generative Motion | 10.1109/icett70124.2026.11665848 | 生成AI教育論における『倫理的力』がAI利用強度に応じ責任を要求すると説く概念枠組み → 採る | 未実施（逸脱 2） |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

