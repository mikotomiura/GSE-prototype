# ふるい分けの記録 —— C1

> 候補の定義（protocol.md §1）: **適応系・自動化系が、認識的権限（意味の認定・評価・報酬化）を人へ返す（手放す）こと**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 720 |
| 段 1 で採った | 179 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 0 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 13 |
| 段 2 の判定（メインの訂正の後） | 該当 3 ／ 部分 10 ／ 非該当 0 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 159 |

## 結論

★ **既出**（該当: C1-0675 [P396]・C1-0276 [P397]・C1-0465（抄録のみ））

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C1-0276 | 該当 | 本文 | an effective LLM-KBP must relinquish epistemic authority | Section 2.0 | 「系(LLM-KBP)が」「epistemic authority（認識的権限）を」「relinquish（手放す）」と、C1定義の語彙とほぼ逐語で一致する記述を本文で確認。設計要件（prompt-level/developer-level/model-level）まで操作化されており、3要素すべてを満たす。 |  | ★ メインが本文で照合 |
| C1-0465 | 該当 | 抄録のみ | ...we show how such systems not only misinterpret emotions but also displace the human as the primary interpreter of their own inner life. To safeguard emotional autonomy, we propose a four-principle design framework:(1)… | 抄録 | 「系が」（感情AIが）「認識的権限（感情の意味を認定する解釈的役割＝primary interpreter）を」保持し人から奪っている現状を問題視した上で、それを「人へ返す・手放す」規範的設計原則（Design Restraint 等の四原則）を提案している。C1定義の3要素（系／認識的権限／人へ返す）を抄録レベルで確認。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0675 | 該当 | 本文 | The agent asks reflective questions grounded exclusively in user input and refuses to provide advice, recommendations, or interpretations. | Abstract | 「系（CASELy）が」助言・解釈という認識的権限の行使を明示的に「拒否（refuses）」し、「意思決定者としてのユーザーの地位」を「維持（maintaining user as decision-maker rather than delegating authority to system）」する設計を本文で明示。系が権限を取らない／人に残す、という形でC1の3要素を満たす。 |  | ★ メインが本文で照合 |
| C1-0022 | 部分 | 本文 | algorithmic paternalism is reflected in language—for example, efforts to improve trust in AI might imply that clinicians should learn to defer to AI. | 序論 | 読めた範囲（序論）では「AI（系）が臨床判断の権威を過剰に主張すること（algorithmic paternalism）」を問題視する記述のみ確認できた。表題が明示する「患者の知恵を組み込むことで権限を患者（人）へ返す」という結論・提言部分の逐語は購読の壁で確認できず、「人へ返す」要素は本文で未確認（タイトルからの推測にとどまる）。 | メイン未照合（購読の壁） |  |
| C1-0030 | 部分 | 抄録のみ | the deeper societal challenge of modern probabilistic semantic systems may lie elsewhere: in the gradual transfer of epistemic and operational authority from humans and institutions toward semantically persuasive but fun… | 抄録 | 抄録は「系へ認識的・操作的権限が移転すること」を問題として明示的に記述しており、C1の「認識的権限」の要素は満たす。ただしそれを反転して「人へ返す」規範的原則（Semantic Authority Separation）の具体的な操作化（系が何をどう手放すか）は抄録が「…」で切れており確認できず、「人へ返す・手放す」要素は未確認。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0174 | 部分 | 本文 | The criteria of success — what counts as error, relevance, or correctness — are specified in advance through loss functions, reward signals, or training objectives. | p.3, §2.1 | 「認識的権限（意味の認定・評価・報酬化）」に相当する要素（損失関数・報酬信号・評価基準が系の外部＝人間側に属し続けるという主張）は強く裏付けられる。ただし本論文の主張は「系がいったん保持した権限を能動的に手放す・返す」ではなく「系は評価的権限を構造的にそもそも持ち得ない（never had）」であり、C1 が想定する能動的な返還という要素は欠ける。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0187 | 部分 | 本文 | Delegation Boundaries define the limits of the moral and interpretive responsibility that can be transferred from humans to AI. They specify where automation stops and human judgement takes over. | p.22, Pillar 1 | 「系（自動化・委任の設計）が」「認識的権限（解釈的・道徳的権限）を」「人へ返す（automation stops and human judgement takes over／restore interpretive ownership）」の三要素がそろって明示されている。ただし対象は解釈的・道徳的権限であり「報酬化」への直接の言及はない。 | 段 2 担当は「該当」→ メインが下げた（組織が AI への委任の境界を決める話で、系が手放す話ではない） | メインが抄録・取り出したテキストと機械照合 |
| C1-0217 | 部分 | 抄録のみ | Current AI lacks epistemic autonomy because its outputs remain dependent on institutionally maintained standards, corrective processes, and accountable authorization. | 抄録 | 現状では AI に認識的自律性がなく、認識的機能・制度的権限は放射線科医らの側に留まっている、という点は「権限が人に属する」要素と一致する。しかし記述は「AI はまだ権限を獲得していない（獲得には制度的な権限の移譲が必要）」という現状記述であり、C1 が想定する「系がいったん持った権限を能動的に手放す・返す」という動的な返還の記述ではない。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0248 | 部分 | 本文 | P2: assistance without authority. Users may bypass diagnosis, dismiss or select a proposal, revise the queued request, and accept or reject the candidate artifact; a proposal never becomes a committed change without expl… | Section 3 (Design Principles) | 「系(PROS)が」問題発見の主導権(epistemic initiative)は持つが、採否・確定という認識的権限に相当する部分は設計原則P2「assistance without authority」として明示的に「系が権限を取らない／人が持つ」形で操作化。C1の3要素を本文で確認（「返す」というより「最初から系に持たせない」設計だが、権限が人に一貫して残る点でC1に該当）。 | 段 2 担当は「該当」→ メインが下げた（変更を確定する権限を手放すが、認識的な主導は系が持つ） | メインが抄録・取り出したテキストと機械照合 |
| C1-0382 | 部分 | 本文 | Retain a Minimum Threshold of Human Judgment in Critical Systems... Implementing a "judgment retention ratio" is crucial for integrating moral reasoning, empathy, and interpretive discretion into high-stakes decision-mak… | p.7-8, Recommendations | 「人間の判断（認識的権限の一部）が保持される」という結論は一致するが、これは「最初から完全自動化しない（judgment retention ratio を設ける）」という予防的設計原理であり、C1 が要求する「系がいったん担った権限を能動的に手放す・返す」という移譲の構造とは異なる。「報酬化」への言及もない。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0638 | 部分 | 抄録のみ | We argue that systems for judgment-heavy cultural tasks should support interpretation rather than automate judgment, laying the groundwork for future user-centered re-creation. | 抄録 | 「系が判断を自動化せず解釈を支援すべき」という規範は認識的権限（意味の認定＝correctnessの判断）を専門家（人）に残すべきだという主張であり、C1の「人へ返す」要素と方向は一致する。ただし「系が」「手放す(relinquish)」に相当する逐語（系がいったん保持した権限を明示的に放棄する記述）は抄録に確認できず、部分的一致にとどまる。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0659 | 部分 | 本文 | Existing LLMs often respond by presupposing a single interpretation of such ambiguous requests, frustrating users who intended a different interpretation. | p.1, Abstract | LLM が曖昧な要求に対して単一の解釈を押し付けず、明確化質問によってユーザー自身に意味の確定を委ねるという挙動は「意味の認定を人へ返す」ことの操作化と読めるが、本文全体を通じて「epistemic authority」「interpretive authority」等の権限論の語彙は一切使われておらず、応答精度・ユーザー満足度を上げる技術的手法として提示されているにとどまる。 |  | メインが抄録・取り出したテキストと機械照合 |
| C1-0661 | 部分 | 本文 | Conversational AI could reduce the cost of answering formulated questions, yet novices may still bear the upstream work of deciding what to ask, organizing answers into a case-level understanding, and verifying those ans… | §5.3.2 What Conversational AI Left to the User | 会話型 AI が質問形成・統合・検証という、意味の確定・評価に関わる作業をユーザーに残す（委ねる）という実証結果は、「意味の認定・評価」が人の側に留まる点で C1 と重なる。ただしこれは系が規範的に権限を「手放す・返す」という設計上の主張ではなく、実証研究において会話型 AI が対応しきれずユーザーに残った作業負担の記述であり、C1 というより C2（解釈と説明要求の負担）に近い。 |  | メインが抄録・取り出したテキストと機械照合 |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C1-0007 | 2025 | What Is the Role of Explainability in Medical Artificial Intelligence? A Case-Based Approach | 10.3390/bioengineering12040375 | 説明可能性が患者の自律性や医師患者関係を支える文脈でCDSSの権限配分を論じる | 未実施（逸脱 2） |
| C1-0010 | 2024 | Healthy Mistrust: Medical Black Box Algorithms, Epistemic Authority, and Preemptionism | 10.1017/s0963180123000646 | preemptionism批判を通じ、医療アルゴリズムの結果が患者の確信を完全代替すべきでないと論じる | 未実施（逸脱 2） |
| C1-0017 | 2026 | Perceiving AI as an Epistemic Authority or Algority: A User Study on the Human Attribution of Authority to AI | 10.3390/make8020036 | 透明性・説明可能性がAI出力への批判的関与を支えるという設計含意を実証的に検討する | 未実施（逸脱 2） |
| C1-0018 | 2026 | Cognitive sovereignty and decolonial public health: reclaiming epistemic authority in the global AI era | 10.3389/fpubh.2026.1785170 | コミュニティがAIシステムの認識論理・解釈枠組み・アルゴリズム推論そのものを統治すべきと論じる | 未実施（逸脱 2） |
| C1-0022 | 2023 | Patient wisdom should be incorporated into health AI to avoid algorithmic paternalism | 10.1038/s41591-023-02224-8 | health AIにpatient wisdomを組み込みalgorithmic paternalismを避けるべきという明確な設計原理（タイトルのみで判定、抄録なし） | 照合 |
| C1-0023 | 2023 | Experts or Authorities? The Strange Case of the Presumed Epistemic Superiority of Artificial Intelligence Syst… | 10.2139/ssrn.4561425 | AIのepistemic優越性の前提を批判する哲学論文と見られる（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0024 | 2023 | Algorithm aversion to mobile clinical decision support among clinicians: a choice-based conjoint analysis | 10.1080/0960085x.2023.2251927 | アルゴリズムが臨床医の結果修正権を制限すると忌避が生じるという知見は、医師に判断権限を残す設計含意を持つ | 未実施（逸脱 2） |
| C1-0025 | 2025 | Rethinking evidence-informed policy and practice in the age of generative artificial intelligence | 10.14324/lre.23.1.16 | AI依存下でのEIPPにおいて批判的思考により人間側の評価権限保持を主張する | 未実施（逸脱 2） |
| C1-0027 | 2026 | When Artificial Intelligence Shapes the way we Think | 10.1007/s13347-026-01055-y | タイトルのみで判定不能なため迷ったら採るのルールに従う（抄録なし） | 未実施（逸脱 2） |
| C1-0030 | 2026 | From Kant to "Agents of Chaos" Why the Central Problem of AI Is Not Intelligence but Epistemic Authority | 10.5281/zenodo.20374829 | AIへの認知的権限移譲への対抗としてSemantic Authority Separationという統治原理を提案する | 照合 |
| C1-0032 | 2025 | REIMAGINING THE DIGITAL ORACLE: AN AFRICAN PHILOSOPHICAL AND THEOLOGICAL CRITIQUE OF ARTIFICIAL INTELLIGENCE | 10.56943/jssh.v4i4.869 | AIを自律的な神託ではなく意思決定支援ツールと位置づけ、共同体の解釈権限保持を規範として論じる | 未実施（逸脱 2） |
| C1-0035 | 2026 | Artificial Intelligence and the Professional Work of Physics Teachers in STEAM Education | 10.59324/jaitd.2026.2(2).18 | AIを権威源でなく一時的協働者として扱うことで教師の認識論的判断を保持する設計論 | 未実施（逸脱 2） |
| C1-0038 | 2024 | Artificial Intelligence and Digital Tafsīr: Assessing the Interpretive Accuracy of ChatGPT’s Engagement with T… | 10.15642/juit.2024.2.1.86-118 | AIは伝統的学術的権威に取って代わるべきでないと明示的に結論づける | 未実施（逸脱 2） |
| C1-0040 | 2025 | We Reject the Use of Generative Artificial Intelligence for Reflexive Qualitative Research - Response | 10.2139/ssrn.5690262 | 質的研究におけるGenAI使用拒否への応答で、研究者の解釈権限保持を論じると見られる（迷ったら採る） | 未実施（逸脱 2） |
| C1-0041 | 2025 | The Delegation of Thought: Education and Judgement in the Age of Artificial Intelligence | 10.37284/eajis.8.1.3254 | AIはepistemic authorityになってはならないという明示的規範主張 | 未実施（逸脱 2） |
| C1-0049 | 2026 | Taxation and Technology: How Artificial Intelligence Reconfigures Professional Judgment, Expertise, and Instit… | 10.2139/ssrn.6331138 | 税務専門職の判断とAIによる再構成を論じる（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0053 | 2025 | The Algorithmic Construction of Epistemic Injustice | 10.2139/ssrn.5172655 | アルゴリズムによるepistemic injusticeの構築を論じる（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0054 | 2023 | Power asymmetries, epistemic imbalances and barriers to knowledge: the (im)possibility of knowing algorithms | 10.4337/9781803928562.00058 | アルゴリズム的認識論に対する拒否・抵抗の戦略を通じ人間側への権限奪還の道筋を論じる | 未実施（逸脱 2） |
| C1-0056 | 2025 | Bridging Revelation and Algorithm | 10.32678/dmr.v3i1.38 | AIは自律的解釈権威ではなくepistemological instrumentであるべきと明示し人間の解釈権威を再確認する | 未実施（逸脱 2） |
| C1-0057 | 2025 | The Algorithmic Construction of Epistemic Injustice | 10.1007/978-3-032-07581-9_5 | C1-0053と同一タイトルの別版で同じ理由により採る | 未実施（逸脱 2） |
| C1-0062 | 2026 | Human Agency and Epistemic Authority Under Generative Artificial Intelligence | 10.55982/openpraxis.18.3.1149 | 評価・判断のAIへの委任が人間の責任とepistemic authorityを侵食すると論じ、人間側の責任回復を志向する | 未実施（逸脱 2） |
| C1-0064 | 2026 | The Algorithmic Mujtahid: Artificial Intelligence, Ijtihād, and the Question of Interpretive Authority in Cont… | 10.1080/14746700.2026.2725297 | AIは代替でなく補助的道具に留まるべきと明示する | 未実施（逸脱 2） |
| C1-0065 | 2026 | Epistemic Authority in Medical Artificial Intelligence: A Virtue Epistemological Analysis | 10.12014/j.issn.1002-0772.2026.09.01 | 医療AIを完全なepistemic authorityとはみなさずhuman-AIハイブリッドモデルを提案する | 未実施（逸脱 2） |
| C1-0066 | 2026 | Epistemic Authority and Algorithmic Governance: A Comprehensive Analysis of Artificial Intelligence within the… | 10.59075/ijsshc.v2i2.650 | AIは単独で宗教的・法的権威になり得ず人間の監督下の意思決定支援ツールとすべきと明示する | 未実施（逸脱 2） |
| C1-0068 | 2025 | Automating epistemology: how AI reconfigures truth, authority, and verification | 10.1007/s00146-025-02560-y | アルゴリズム検証の設計・監督への参加型アプローチを求めており人間側の関与保持を論じる | 未実施（逸脱 2） |
| C1-0069 | 2025 | Negotiating Qur’anic Interpretive Authority in the Age of Artificial Intelligence in Aceh | 10.22373/tafse.v10i2.33016 | AIの解釈的権威が制限され伝統的師弟継承（人間）に権威が留まる実証的知見を示す | 未実施（逸脱 2） |
| C1-0071 | 2026 | INTEGRATING ARTIFICIAL INTELLIGENCE IN ISLAMIC RELIGIOUS EDUCATION: INNOVATION AND TEACHERS’ EPISTEMIC AUTHORI… | 10.47498/tadib.v18i1.6385 | AI統合が教師のepistemic authority保持と人間の検証・監督を要件とすると論じる | 未実施（逸脱 2） |
| C1-0074 | 2026 | Reconstructing Epistemic Authority: A Post-Human Pedagogical Framework for Artificial Intelligence in Islamic … | 10.61987/educazione.v4i1.2400 | AIに認識論的参加は認めるが権威は否定し人間の位階を保持する設計枠組みを提案する | 未実施（逸脱 2） |
| C1-0075 | 2026 | Reply: Artificial Intelligence in Respiratory Medicine: Epistemic Authority, Trust and Responsibility in Pract… | 10.4274/thoracrespract.2026.2026-8-21 | 呼吸器内科AIの認識的権威・責任に関する議論（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0077 | 2026 | Letter to the Editor: Artificial Intelligence in Respiratory Medicine: Epistemic Authority, Trust and Responsi… | 10.4274/thoracrespract.2026.2026-8-8 | C1-0075と対をなす同一議論のLetter（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0079 | 2026 | Ethics of Using Artificial Intelligence (AI) in Islamic Education: A Philosophical Inquiry into Responsibility… | 10.59059/perspektif.v4i2.3339 | AIを自律的な道徳的・認識的権威ではなく教育的道具として位置づけると明示する | 未実施（逸脱 2） |
| C1-0080 | 2026 | MAPPING ARTIFICIAL INTELLIGENCE-BASED MODELS FOR TAFSĪR LEARNING: A SCOPING REVIEW OF TECHNOLOGIES, PEDAGOGY, … | 10.66053/ri.v4i2.1255 | AIベースのTafsir学習モデルにおける解釈的権威をスコーピングレビューする（迷ったら採る） | 未実施（逸脱 2） |
| C1-0083 | 2026 | The Impact of Generative Artificial Intelligence on the Structure of Modern Education: The Decentralization of… | 10.2991/978-94-6239-699-9_48 | GenAIによる認識的権威の脱中心化と教師学生関係の再構成を論じる（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0084 | 2026 | Digital Platforms and Epistemic Authority | 10.2139/ssrn.7225518 | デジタルプラットフォームとepistemic authorityに関する論文（タイトルのみで判定、迷ったら採る） | 未実施（逸脱 2） |
| C1-0085 | 2026 | Digital Platforms and Epistemic Authority | 10.2139/ssrn.7225058 | C1-0084と同一タイトルの別版（迷ったら採る） | 未実施（逸脱 2） |
| C1-0086 | 2026 | Epistemic Authority in the Age of Generative AI: A Study of Knowledge Trust, Control, and Algorithmic Mediatio… | 10.25077/jds.3.1.58-69.2026 | GenAI時代もユーザーは人間の専門知識・機関的信頼性・独立検証への依拠を続けると論じる | 未実施（逸脱 2） |
| C1-0092 | 2026 | Digital Platforms and Epistemic Authority (forthcoming 2026) | 10.2139/ssrn.7207722 | 抄録が空で題名のみでは方向性を判定できないため迷って採る | 未実施（逸脱 2） |
| C1-0097 | 2026 | AI, PEERS, AND SUPERVISORS: EPISTEMIC AUTHORITY IN POSTGRADUATE SUPERVISION | 10.31932/jees.v9i1.6211 | AI・同輩・指導教員の認識的権威階層を実証的に調べ指導教員の権威維持を示す点で候補に関連する(迷い) | 未実施（逸脱 2） |
| C1-0098 | 2021 | Concerning a seemingly intractable feature of the accountability gap | 10.1136/medethics-2021-107353 | ブラックボックスアルゴリズムの認識的権威は医師の専門性で抑制されるべきと明示的に論じている | 未実施（逸脱 2） |
| C1-0100 | 2026 | Navigating the Algorithmic Turn: A Systematic Review of Boundary Work, Epistemic Authority, and Governance in … |  | AI統合ジャーナリズムにおける境界画定・認識的権威・ガバナンスを扱うレビュー主題が候補に合致するため採る | 未実施（逸脱 2） |
| C1-0101 | 2026 | From Archive to Algorithm: Artificial Intelligence, Memory, and the Future of Literary Interpretation | 10.67693/bjcr-y674x85r | AIを解釈の媒介層と位置づけ人間読者との解釈的権威の再配分を明示的に論じている | 未実施（逸脱 2） |
| C1-0103 | 2026 | Algorithmic epistemic authority and the degradation of organizational knowledge: how generative AI breaks the … | 10.1108/jkm-03-2026-0627 | 生成AIが組織知の来歴構造を破壊する分析だが実務含意としてアーキテクチャ分離による対応にも触れるため採る(迷い) | 未実施（逸脱 2） |
| C1-0107 | 2026 | Beyond the Algorithm: Artificial intelligence, clinical decision-making, and the moral ecology of care in Afri… | 10.31235/osf.io/5r37j_v1 | 臨床AIが認識的権威を再構成する中で責任の再配分と地域住民との知識共創を明示的に提案している | 未実施（逸脱 2） |
| C1-0108 | 2026 | Fostering the moral self in the age of algorithms: an Islamic ethical framework for Artificial Intelligence in… | 10.1080/17449642.2026.2703052 | AIを批判的に媒介された場合のみ倫理的省察を促す道具と位置づけ人間の対話的判断を残す枠組みを論じている(迷い) | 未実施（逸脱 2） |
| C1-0109 | 2026 | Beyond the Algorithm: Artificial Intelligence, Clinical Decision-Making, and the Moral Ecology of Care in Afri… | 10.1007/s11948-026-00616-w | C1-0107の査読誌掲載版で同一内容 | 未実施（逸脱 2） |
| C1-0111 | 2026 | Epistemic Authority without Stability? The Moral Crumple Zone in Agentic AI Workflows | 10.2139/ssrn.5993114 | 抄録は空だがエージェント型AIワークフローにおける認識的権威の不安定さとmoral crumple zoneという主題が候補に強く合致するため採る | 未実施（逸脱 2） |
| C1-0113 | 2026 | The silent knowledge crisis: Algorithmic epistemology and the marginalisation of tacit and indigenous knowledg… | 10.65221/0221 | アルゴリズム的認識論による暗黙知・先住民知の周縁化を批判し認識的多元主義という対応枠組みを提案している | 未実施（逸脱 2） |
| C1-0114 | 2026 | From Epistemic Impunity to Democratic Accountability: Algorithmic Epistemic Authority, AI-Driven Policing, and… | 10.2139/ssrn.6830084 | AI出力を異議申し立て不能な権威として扱う警察運用を批判し市民の異議申し立てと民主的説明責任の回復を論じている | 未実施（逸脱 2） |
| C1-0116 | 2026 | Machine-Readable Personhood: AI, Epistemic Authority, and Technocratic Colonialism A Conceptual Working Paper | 10.2139/ssrn.6755058 | 抄録が空で題名のみだがAIの認識的権威と技術植民地主義という主題が候補に関連しうるため迷って採る | 未実施（逸脱 2） |
| C1-0117 | 2026 | Indigenous-led futures in Artificial Intelligence | 10.4000/16m4y | 先住民コミュニティがAIシステムに関与し自らの知識体系に沿うよう技術を再構成する権限の主張を論じている | 未実施（逸脱 2） |
| C1-0118 | 2026 | Artificial intelligence and the ethics and practice of evaluation | 10.4324/9781003799139-32 | AIが評価実践で人間の解釈的権威を奪うリスクを明示的に論じAI主導推論が制度化する前の倫理的関与を主張している | 未実施（逸脱 2） |
| C1-0119 | 2026 | Who speaks for culture? Generative AI, epistemic authority, and narrative negotiation in an intercultural clas… | 10.1007/s00146-026-03130-6 | 抄録は空だが生成AIと異文化教室での認識的権威・物語交渉という主題が候補に合致するため採る | 未実施（逸脱 2） |
| C1-0120 | 2026 | Epistemology of Education in the Era of Artificial Intelligence | 10.56916/jirpe.v5i2.3066 | AI時代の教育認識論の変容の一つとして認識的権威の再配分を挙げ教師をepistemic curatorshipとして再定位している | 未実施（逸脱 2） |
| C1-0121 | 2026 | Epistemic Authority and Clinical Governance in AI-Integrated Radiography: A Practice-Oriented Narrative Review | 10.36017/jahc202682578 | 放射線技師がAI媒介出力の妥当性・解釈可能性・ガバナンスの説明責任ある保証者であり続けると明示的に論じている | 未実施（逸脱 2） |
| C1-0122 | 2026 | From Kant to "Agents of Chaos" Why the Central Problem of AI Is Not Intelligence but Epistemic Authority | 10.5281/zenodo.20374828 | AIへの意味論的権威の移譲を批判しSemantic Authority Separationという権威分離の統治原理を提案している | 照合 |
| C1-0123 | 2026 | From Kant to "Agents of Chaos" Why the Central Problem of AI Is Not Intelligence but Epistemic Authority | 10.2139/ssrn.6825719 | C1-0122のSSRN版で同一内容 | 照合 |
| C1-0124 | 2026 | Generative AI, epistemic authority, and knowledge governance tension: implications for innovation novelty and … | 10.1186/s43093-026-00938-y | 生成AI統合と認識的権威の再配分の関係を実証的に調査する組織調査研究 | 未実施（逸脱 2） |
| C1-0126 | 2026 | Reflexive Qualitative Research and Generative AI: A Call to go Beyond the Binary | 10.1177/10778004261429383 | AI主導分析と人間主導分析を区別し認識的権威に議論を再焦点化するガバナンス志向の対応を提案している | 未実施（逸脱 2） |
| C1-0131 | 2026 | Ecclesial Discernment in the Era of Generative Artificial Intelligence | 10.14422/ee.v101.i397.y2026.004 | 生成AIによる教会的識別への影響を論じ人間共同体の周縁の声への配慮を残す神学的・司牧的基準を提示している | 未実施（逸脱 2） |
| C1-0132 | 2026 | Who Evaluates? Delegated Financial Cognition and the Allocation of Epistemic Authority in AI-Mediated Financia… | 10.2139/ssrn.6877758 | 抄録は空だがAI媒介金融意思決定における認識的権威の配分という題名が候補に強く合致するため採る | 未実施（逸脱 2） |
| C1-0134 | 2026 | Curated information frameworks and the Governance of artificial intelligence | 10.1007/s43681-026-01242-9 | 参加型フレームワークによりAIシステムの解釈的権威をエンジニアから農民・労働者・規制者へ再配分することを明示的に提案している | 未実施（逸脱 2） |
| C1-0136 | 2026 | Artificial Intelligence as an Epistemological Challenge in Contemporary Islamic Education | 10.52366/edusoshum.v6i3.501 | AIを自律的な認識的権威ではなく教育的補助と位置づけるべきと明示的に論じている | 未実施（逸脱 2） |
| C1-0137 | 2025 | The Potential Synergy Between Epistemology and Explainable Artificial Intelligence | 10.5281/zenodo.21512858 | XAI文脈でepistemic deferenceなど人間-AI相互作用における認識的権威配分の概念群を論じている | 未実施（逸脱 2） |
| C1-0138 | 2025 | The Potential Synergy Between Epistemology and Explainable Artificial Intelligence | 10.5281/zenodo.21512859 | C1-0137と同一内容の重複 | 未実施（逸脱 2） |
| C1-0139 | 2025 | Artificial Intelligence: An Interdisciplinary Review of Emerging Paradigms in the Humanities | 10.5281/zenodo.18209572 | AIを中立的道具ではなく認識的アクターと位置づけつつ批判的判断を損なわない統合を論じている(迷い) | 未実施（逸脱 2） |
| C1-0140 | 2025 | Artificial Intelligence: An Interdisciplinary Review of Emerging Paradigms in the Humanities | 10.5281/zenodo.18209571 | C1-0139と同一内容の重複 | 未実施（逸脱 2） |
| C1-0141 | 2025 | Dominant Disciplinary and Thematic Approaches to Automated Fact-Checking: A Scoping Review and Reflection | 10.1080/21670811.2024.2427036 | アルゴリズムを擬人化して認識的権威を求めるのではなく日常的利用を強調すべきと明示的に論じている | 未実施（逸脱 2） |
| C1-0142 | 2026 | Human-AI Collaborative Inductive Thematic Analysis: AI Guided Analysis and Human Interpretive Authority |  | AI支援分析ツールを用いても解釈的権威は人間研究者に留まったと実証的に論じている | 未実施（逸脱 2） |
| C1-0143 | 2026 | Human-AI Collaborative Inductive Thematic Analysis: AI Guided Analysis and Human Interpretive Authority | 10.48550/arxiv.2601.11850 | C1-0142のarXiv版で同一内容 | 未実施（逸脱 2） |
| C1-0144 | 2026 | Encountering Generative AI: Narrative Self-Formation and Technologies of the Self Among Young Adults | 10.3390/soc16010026 | チャットボットとの関わりにおける物語的解釈的権威と審議のアウトソーシングの緊張を論じている(迷い) | 未実施（逸脱 2） |
| C1-0145 | 2026 | Artificial Intelligence, Personhood, Common Sense, and Democracy: A Critical Analysis | 10.32920/31099855.v1 | AIによる判断領域への参入が既存の常識・直観の権威を掘り崩す中で民主的判断の再構築を論じている | 未実施（逸脱 2） |
| C1-0146 | 2026 | Artificial Intelligence, Personhood, Common Sense, and Democracy: A Critical Analysis | 10.32920/31099855 | C1-0145と同一内容の重複 | 未実施（逸脱 2） |
| C1-0147 | 2026 | ARTIFICIAL INTELLIGENCE, ETHICS, AND LEGAL ACCOUNTABILITY IN HIGHER EDUCATION INSTITUTIONS | 10.29121/shodhkosh.v7.i14s.2026.8537 | AI生成の推奨が人間により適切にチェックされていない点をガバナンス上の弱点として明示的に指摘している | 未実施（逸脱 2） |
| C1-0148 | 2026 | Does ChatGPT Undermine Human Epistemic Authority? A Multi-Dimensional Analysis of Artificial Intelligence's Ch… | 10.5281/zenodo.21822133 | ChatGPTが人間の認識的権威を掘り崩すかを多次元的に実証分析し条件付き代替に留まると論じている | 未実施（逸脱 2） |
| C1-0149 | 2026 | Does ChatGPT Undermine Human Epistemic Authority? A Multi-Dimensional Analysis of Artificial Intelligence's Ch… | 10.5281/zenodo.21822132 | C1-0148と同一内容の重複 | 未実施（逸脱 2） |
| C1-0151 | 2026 | Modelling the impact of generative artificial intelligence on information behaviour research | 10.1108/jd-03-2026-0150 | 生成AIの特性に対応するため情報行動モデルに倫理評価という人間判断の新段階を明示的に追加提案している | 未実施（逸脱 2） |
| C1-0154 | 2026 | From Computers to Google to Artificial Intelligence: Evolution of Digital Knowledge Infrastructures | 10.1201/9781042018116-22 | AIが専門知の垂直モデルに挑戦し参加型・水平的な知識生成を可能にする点を論じている(迷い) | 未実施（逸脱 2） |
| C1-0155 | 2025 | Ethical and Responsible AI in Education: Situated Ethics for Democratic Learning | 10.3390/educsci15121594 | アルゴリズム的採点等が解釈的主体性を再編する中、学習者の自律性と民主的判断を規範基準とする枠組みを提案している | 未実施（逸脱 2） |
| C1-0158 | 2026 | Towards a critical socio-technical model of journalism training in the age of artificial intelligence | 10.1080/22041451.2026.2655081 | AIが認識的権威を再配分しジャーナリズム実践を再構成すると論じる社会技術モデルを提案している | 未実施（逸脱 2） |
| C1-0159 | 2026 | Artificial Intelligence as Co-Author: Rethinking Authorship and Creativity in Contemporary Literature | 10.64882/ijrt.v14.is1.1060 | 技術的協働を認めつつ人間の説明責任と解釈的権威を保持する著者性の再概念化を明示的に提唱している | 未実施（逸脱 2） |
| C1-0162 | 2026 | The Contestation of Interpretational Authority between ʻUlamāʻ and Artificial Intelligence: A Critical Study o… | 10.64691/dh6rwb84 | AIは意図性等の認識的前提を欠くため解釈的権威を持ち得ないと論じウラマーの解釈的権威を実質的に支持している | 未実施（逸脱 2） |
| C1-0163 | 2026 | The Design of Transhuman Classes in the Context of Artificial Intelligence, Cognitive Development, and the Fut… | 10.4018/979-8-2600-1232-1.ch017 | AIによる教師-生徒関係・認識的権威の再定義と認知依存への懸念を論じている(迷い) | 未実施（逸脱 2） |
| C1-0164 | 2026 | Negotiating epistemic authority in the age of generative AI: AI reliance, responsibility, and usage intensity … | 10.1007/s00146-026-03242-z | コーチがGenAIを構造的タスクに用いつつ関係的・解釈的作業への人間の権威を維持する境界作業を実証的に論じている | 未実施（逸脱 2） |
| C1-0166 | 2026 | Digital Knowledge Systems and Islamic Epistemology: Artificial Intelligence Adoption in Pesantren Education | 10.62097/falasifa.v17i01.2902 | デジタル情報システムと教師中心の解釈的権威が共存するハイブリッドな知識環境を実証的に論じている | 未実施（逸脱 2） |
| C1-0167 | 2025 | AI and Qur’anic Interpretation: Exploring the Ethical and Epistemological Boundaries of Artificial Intelligenc… | 10.58518/alfurqan.v8i2.4243 | AIを解釈の主体ではなく道具的分析手段と位置づけるべきと明示的に論じている | 未実施（逸脱 2） |
| C1-0168 | 2026 | Artificial Intelligence Paradigm in Islamic Education: Epistemological Offerings to the Concept of Teacher and… | 10.68195/ijiel.v1i2.9 | AIをイスラーム教育における認識的権威としてではなく手段(wasīlah)として位置づける枠組みを提案している | 未実施（逸脱 2） |
| C1-0169 | 2026 | Artificial Intelligence in Zoological Sciences and English Literary Research: A Comparative Interdisciplinary … | 10.36948/ijfmr.2026.v08i01.66540 | 分野を横断してAI利用下でも人間の判断・文脈的推論への重点が共有されると実証的に論じている(迷い) | 未実施（逸脱 2） |
| C1-0171 | 2026 | Who speaks when machines read scripture: boundary-making and interpretive authority in AI-mediated religious k… | 10.1007/s43681-026-01254-5 | AIを宗教的知識体系における解釈的な権威者ではなく補助的分析手段として再定位する枠組みを提案している | 未実施（逸脱 2） |
| C1-0172 | 2026 | THE RELIANCE ON ARTIFICIAL INTELLIGENCE AS A PREDICTOR OF ACADEMIC INTEGRITY AMONG HIGHER EDUCATION STUDENTS | 10.25258/ijddt.16.61s.174 | AIへの依存が委任された倫理・認識的権威として機能する問題を実証し批判的思考が悪影響を緩和すると論じている(迷い) | 未実施（逸脱 2） |
| C1-0174 | 2026 | The Duck Criterion in Artificial Intelligence: Evaluative Structure and the Attribution of Agency, Authority, … | 10.5281/zenodo.19160995 | 評価基準を改訂できないシステムは行動が複雑でも構造的に維持系にすぎないとしAIの真正な認識的主体性に疑義を呈している | 照合 |
| C1-0175 | 2026 | Digital Narratives And Artificial Intelligence: Reimagining Language, Meaning, And Literary Expression In The … | 10.29284/z99te581 | 物語生成の自動化が著者性・解釈的権威に挑戦しつつ人間の意図とAI生成の動的相互作用を論じている(迷い) | 未実施（逸脱 2） |
| C1-0176 | 2026 | The Duck Criterion in Artificial Intelligence: Evaluative Structure and the Attribution of Agency, Authority, … | 10.5281/zenodo.19160994 | C1-0174と同一内容の重複 | 照合 |
| C1-0177 | 2021 | Mapping and contesting peer selection in digitalized public sector benchmarking | 10.1111/faam.12306 | アルゴリズム的ベンチマーキングに対し実務者が地域的知識で抵抗・異議申し立てる実証事例を論じている | 未実施（逸脱 2） |
| C1-0178 | 2026 | Authorship in the age of artificial intelligence (AI): Ethics letter number four (4) | 10.4314/ajsw.v16i2.6 | AIへの技術的作業の委任を認めつつ分析的・理論的・文脈的な役割という人間の不可欠な知的貢献を明示的に保持している | 未実施（逸脱 2） |
| C1-0179 | 2025 | ARTIFICIAL INTELLIGENCE AS ARTIST AND HISTORIAN: INTERPRETING AND INVENTING STYLES IN THE AGE OF MACHINE CREAT… | 10.35603/sws.iscss.2025/s04.44 | AI媒介の美術解釈における解釈的権威という論点を含む学芸員的枠組みを論じている(迷い) | 未実施（逸脱 2） |
| C1-0180 | 2026 | Artificial Intelligence and Islamic Legal Reasoning: Reconstructing Ethical Governance for Sharia Decision-Mak… | 10.67140/jhies.v2i2.18 | AIを分析的道具として位置づけイスラーム法学者の規範的権威の下に置くハイブリッドモデルを明示的に提案している | 未実施（逸脱 2） |
| C1-0184 | 2026 | Artificial Intelligence, the Clinician–patient Relationship and the Democratisation of Health Care: A Critical… | 10.9734/bpi/dhrrd/v2/7853 | 臨床AIによる認識的権威の再分配とその信頼への帰結を中心分析軸に据えたレビューで、系・医師・患者間の権限配分を論じている。 | 未実施（逸脱 2） |
| C1-0187 | 2026 | Expectation Inflation of Artificial Intelligence: When Human Demands on AI Exceed Moral Design Capacity | 10.32388/2suyhm.2 | AIへの過剰委任を防ぐ委任の境界(Delegation Boundaries)を提案する概念枠組みで、解釈的・道徳的権限の人間への保持を明示的に論じる。 | 照合 |
| C1-0188 | 2026 | Integration of Artificial Intelligence in the Science of Tafsīr: A Critical Analysis of Opportunities and Chal… | 10.64691/3zsxrs39 | タフスィール(クルアーン解釈)におけるAIの認識論的境界と機能を定式化し、AIが人間の解釈的権威に依存すると論じる。 | 未実施（逸脱 2） |
| C1-0192 | 2026 | Epistemology of Interpretation in the Era of Artificial Intelligence: Authority, Validity, and the Limits of A… | 10.64691/21y5h822 | AIはクルアーン解釈における認識的媒介者に留まり人間の解釈的権威に依存すると明示的に結論づけている。 | 未実施（逸脱 2） |
| C1-0196 | 2025 | Computational Literary Analysis in the Age of AI: Transforming Textual Interpretation Through Artificial Intel… | 10.1109/iceca66444.2025.11383132 | AI支援の文学分析が人間の監督(human oversight)の下で解釈的権威を保つべきだと明示的に述べている。 | 未実施（逸脱 2） |
| C1-0197 | 2025 | Ethics and Limits of Artificial Intelligence (AI) in Quranic Exegesis According to the Epistemological Framewo… | 10.22452/quranica.vol17no2.5 | AIはクルアーン解釈における副次的な補助ツールに留めるべきで、自律的釈義者・主要な解釈的権威にはすべきでないと明示的に結論づけている。 | 未実施（逸脱 2） |
| C1-0198 | 2026 | Ethical integration of generative artificial intelligence in Islamic religious education involves human mediat… | 10.1007/s44163-026-02251-7 | 生成AIは教師の代替でなく教育補助であるべきとし、教師による監督・検証を要件とする明示的な設計原則を示している。 | 未実施（逸脱 2） |
| C1-0203 | 2025 | Hybrid cognitive authority and algorithmic subjectivity: rethinking knowledge management in AI-driven communic… | 10.1108/jkm-02-2025-0252 | HCIによるユーザー中心AIツール設計の文脈でHybrid Cognitive Authority(人間とAIの知識共構築)を提案し、権限の人間側への配分を論じる。 | 未実施（逸脱 2） |
| C1-0204 | 2026 | Rethinking the evaluation of news algorithms: aligning epistemic standards, user priorities and evaluation met… | 10.3389/fcomm.2026.1844993 | ニュース推薦系の評価をユーザーの認識的基準(信頼性等)に沿わせる評価枠組みを提案し、系設計をユーザーの認識的能力に接地させている。 | 未実施（逸脱 2） |
| C1-0205 | 2025 | Algorithmic Authority and the Ethical Turn in Educational Technology: A Praxis-Oriented Approach | 10.65831/joapoe.v1i1.3 | 教育工学における実践志向設計を提唱し、手続き的倫理や人間監督だけでは不十分だとして人間の尊厳・主体性を中心に据えた参加型設計を論じる。 | 未実施（逸脱 2） |
| C1-0207 | 2026 | Epistemic Trust and the Limits of AI Authority in Islam | 10.1515/opth-2025-0069 | AIは限定的な認知機能には認識的信頼に値するが道徳的・宗教的権威としては不適格と明示的に線引きしている。 | 未実施（逸脱 2） |
| C1-0208 | 2026 | Whose Knowledge Counts in Labour? Obstetric Nurses Negotiating Clinical Judgement, Algorithmic Authority and W… | 10.1111/nin.70166 | AI強化胎児モニタリング系とのやり取りで看護師が臨床判断の権威を交渉する実証研究で、系のアラートは臨床的啓示ではなく既存の懸念への許可として機能すると論じる。 | 未実施（逸脱 2） |
| C1-0211 | 2024 | Categorizing Algorithmic Recommendations: a Matter of System, Agent, Patient |  | 抄録なし。題名から推薦系におけるシステム・エージェント・患者の役割分類を扱うと読め、責任・権限帰属に関わりうるため題名判定の原則に従い迷って採る。 | 未実施（逸脱 2） |
| C1-0217 | 2026 | Radiology Is not a Task: AI and the Epistemic System of Radiology. | 10.1016/j.acra.2026.08.107 | AIは制度的に維持された基準に依存し対立の裁定・基準の改訂・説明責任の引き受けの権限を持たないと明示的に論じ、責任は放射線科医らに帰属し続けるとする。 | 照合 |
| C1-0219 | 2023 | Why Won’t You Listen To Me? Predictive Neurotechnology and Epistemic Authority | 10.1007/s12152-023-09527-0 | 予測神経技術という介入系がユーザーの自律的選択を補完でなく代替してしまうリスク(認識的権威の委譲問題)を論じ、系・利用者間の権限配分を扱う。 | 未実施（逸脱 2） |
| C1-0220 | 2026 | Generative AI User Experience: Developing Human-AI Epistemic Partnership | 10.48550/arxiv.2603.23863 | 生成AIのUXを交渉される権威・再分配された認知を含む認識的パートナーシップ理論として説明し、人間-AI間の権限交渉を明示的に扱う。 | 未実施（逸脱 2） |
| C1-0222 | 2026 | Youth Participation and Epistemic Authority in Digital Mental Health Design and Governance | 10.63711/ijdr.net20260102 | 若者を知識保有者として認め意思決定権限を若者側へ再分配すべきだとデジタルメンタルヘルスのガバナンス設計を論じている。 | 未実施（逸脱 2） |
| C1-0223 | 2024 | Justitia ex machina: The impact of an AI system on legal decision-making and discretionary authority | 10.1177/20539517241255101 | 裁判所のAI意思決定支援系が法律家の裁量的権威に与える影響をHCI・STSの観点から実証的に分析している。 | 未実施（逸脱 2） |
| C1-0224 | 2026 | Beyond efficiency: epistemic well-being at work under algorithmic governance | 10.1007/s00146-026-03351-9 | アルゴリズム的統治下で個人・集団が判断力・異議申立て能力を行使できる組織的条件(Epistemic Well-being at Work)を概念化し、人間の判断保持を中心に据える。 | 未実施（逸脱 2） |
| C1-0228 | 2026 | Navigating Algorithmic Opacity: Folk Theories and User Agency in Semi-Autonomous Vehicles | 10.48550/arxiv.2602.07312 | 半自動運転車の設計が運転者を受動的データ源ではなく認識的主体として扱っていないと批判し、透明性と参加型ガバナンスによる権限付与を提案する。 | 未実施（逸脱 2） |
| C1-0229 | 2025 | Epistemic Agency with Impact on Technological Humanity | 10.64736/cim2025.cp03 | 非人間系への認識的権威の委任リスクを論じ、批判的自律性と認知的責任の維持・保存の必要性を主張する概念論文。 | 未実施（逸脱 2） |
| C1-0230 | 2024 | Contributory Injustice, Epistemic Calcification and the Use of AI Systems in Healthcare | 10.1609/aies.v7i1.31659 | AI利用がもたらす認識的石灰化への対応として、AI系自体を超えた争訟可能性(contestability)の必要性を論じている。 | 未実施（逸脱 2） |
| C1-0231 | 2025 | RETHINKING SCIENTIFIC OBJECTIVITY IN THE AGE OF ALGORITHMIC MEDIATION: A PHILOSOPHICAL INQUIRY | 10.47353/satukata.v4i1.4601 | 科学的客観性を人間の判断を中心に据えた拡張された客観性(augmented objectivity)として再構成する哲学的提案。 | 未実施（逸脱 2） |
| C1-0232 | 2025 | Epistemic Deference to AI | 10.1007/978-3-032-01377-4_9 | AIへの全面委任(preemptionism)に対し、AI出力を置き換えでなく寄与的理由として扱う総合証拠説を展開し、人間の関与・監督保持を明示的に主張する。 | 未実施（逸脱 2） |
| C1-0235 | 2026 | Governance Models for AI-Driven Design Automation: Ensuring Human-Centered Decision Authority in UX and Produc… | 10.63084/wyq4ba10 | AI駆動デザイン自動化においてAIを補助ツールであり人間判断の代替ではないとするガバナンスモデルを提案し、意思決定権限の所在を明示的に設計している。 | 未実施（逸脱 2） |
| C1-0238 | 2026 | Algorithmic ethics and healthcare pluralism: rethinking care between automation and global inequality | 10.1007/s00146-026-02854-9 | アルゴリズム系がグローバルサウスの医療に及ぼす認識的疎外を批判し、参加型の臨床判断を回復する連帯的ガバナンス枠組み(epistemic solidarity)を提案している。 | 未実施（逸脱 2） |
| C1-0240 | 2026 | Algorithmic Fact-Verification | 10.1093/9780197849644.001.0001 | AIファクトチェックの正統性は透明で争訟可能かつ包摂的な設計に依存するとし、人間の異議申立て可能性を通じた権限保持を論じている。 | 未実施（逸脱 2） |
| C1-0243 | 2026 | Artificial Intelligence, Religious Authority, and Digital Governance: A Maqasid Framework for Governing Religi… | 10.31559/sis2026.11.1.4 | ファトワ的助言に対する人間参加型監督(human-in-the-loop)や争訟可能性、不確実性の明示的伝達をガバナンスツールとして提案している。 | 未実施（逸脱 2） |
| C1-0247 | 2026 | Algorithmic Decision Making in Management: A Philosophical Inquiry from an Islamic Ethical Perspective | 10.33086/jic.v7i2.8471 | アルゴリズムによる意思決定は自律的権威ではなく意思決定支援機構として扱うべきと明示的に結論づけている。 | 未実施（逸脱 2） |
| C1-0248 | 2026 | Beyond Instruction-Driven Editing: Source-Grounded Problem Discovery with User-Governed Repair for Scientific … |  | 対話的編集系PROSが認識的主導権(問題の指摘)と行動的権限(変更の採否決定)を明確に分離し、変更の最終的な権限はユーザーに残す設計を明示的に提案・実証している。 | 照合 |
| C1-0254 | 2023 | Trust criteria for artificial intelligence in health: normative and epistemic considerations | 10.1136/jme-2023-109338 | 臨床AI(生存予測アルゴリズム)への過信・過小信頼を防ぐ信頼基準を医師・患者への面接から抽出し、適切な依拠(reliance)の較正を論じている(判定に迷いあり)。 | 未実施（逸脱 2） |
| C1-0258 | 2026 | Designing for disagreement: epistemic friction, sycophancy, and the ethics of human–AI advice—a critical integ… | 10.1007/s43681-026-01379-7 | 抄録なし。題名Designing for disagreementはAIの追従(sycophancy)を避け認識的摩擦を設計するという、系がユーザーの評価的関与を保つ設計原理を直接示唆する。 | 未実施（逸脱 2） |
| C1-0262 | 2025 | Artificial Epistemic Authorities | 10.1080/02691728.2025.2449602 | AI系が人工的認識的権威(AEA)たり得るかを哲学的に検討し、人間が独立した認識的理由を保持する代替モデルを論じている。 | 未実施（逸脱 2） |
| C1-0263 | 2025 | Classifying Epistemic Relationships in Human-AI Interaction: An Exploratory Approach | 10.48550/arxiv.2508.03673 | 学術従事者へのインタビューからHCIの観点で人間-AI認識的関係を類型化し、権威の移譲(Authority Displacement)や認識的棄権等、ユーザーの知識貢献者としての役割変化を明示的に扱う。 | 未実施（逸脱 2） |
| C1-0266 | 2025 | Constitutive knowledge sources: an institutional approach to epistemic trust in opaque AI systems | 10.1007/s43681-025-00930-2 | AI出力は制度的検証を経て初めて効力を持つとし、系自体は権威の源泉ではなく人間・制度的検証に依存すると明示的に論じている。 | 未実施（逸脱 2） |
| C1-0276 | 2026 | Epistemic Agency in the Age of Large Language Models: Design Principles for Knowledge-Building AI | 10.3390/ai7030099 | LLMシステムを「認識的権威を主張せず探究を支援するKnowledge-Building Partner」として設計する原理を明示的に提案している | 照合 |
| C1-0281 | 2026 | From delegation to moral abdication: classifying large language model uses by judgment and epistemic control | 10.1007/s00146-026-03281-6 | LLM利用をユーザーへの判断委任度と利用者が保持する認識的統制度で分類し、利用者が意味論的責任を行使できる構造的条件を論じている | 未実施（逸脱 2） |
| C1-0382 | 2025 | Not All That Can Be Automated Should Be Automated – Strategic Minimalism as a Disciplined and Ethically Ground… | 10.61093/bel.9(4).57-66.2025 | AI導入における「戦略的ミニマリズム」を論じる経営倫理論文で、自動化強度と人間の判断保持(retained human judgment)を中核軸に据え自制を設計原理として論じており、対話的自動化系の話ではないため迷うが可能性を残して含める。 | 照合 |
| C1-0423 | 2026 | Accountability Protocol: Decision, Exception, Responsibility | 10.2139/ssrn.6238138 | 抄録なし・題名のみで判断不能だが「Decision, Exception, Responsibility」というアカウンタビリティ枠組みの題名から自動化系の権限論との関連が否定できないため含める。 | 未実施（逸脱 2） |
| C1-0435 | 2026 | Not All That Can Be Automated Should Be Automated – Strategic Minimalism as a Disciplined and Ethically Ground… | 10.6084/m9.figshare.30996499.v1 | 「自動化すべきでないもの」論文の別プラットフォーム掲載版で、C1-0382と同一内容につき同一判断(含める)。 | 照合 |
| C1-0437 | 2026 | Not All That Can Be Automated Should Be Automated – Strategic Minimalism as a Disciplined and Ethically Ground… | 10.6084/m9.figshare.30996499 | 「自動化すべきでないもの」論文のさらに別掲載版で、C1-0382と同一内容につき同一判断(含める)。 | 照合 |
| C1-0438 | 2026 | Not All That Can Be Automated Should Be Automated: Strategic Minimalism as a Disciplined and Ethically Grounde… | 10.48550/arxiv.2609.13188 | 「自動化すべきでないもの」論文のarXiv版で、C1-0382と同一内容につき同一判断(含める)。 | 照合 |
| C1-0453 | 2025 | Network-Centric Distributed LLM Architecture with Epistemic Sovereignty | 10.2139/ssrn.5618412 | 抄録なし。題名の「Epistemic Sovereignty」がLLMアーキテクチャの認識的主権を扱う可能性があり迷ったら採るで含める | 未実施（逸脱 2） |
| C1-0465 | 2025 | Affective Sovereignty in the Age of Emotional AI: Reclaiming the Right to Feel | 10.31234/osf.io/ms7gv_v1 | 感情AI(Replika/Affectiva)が持つ解釈的権限を人へ返す設計原則(Design Restraint等)を明示的に提案している | 照合 |
| C1-0467 | 2025 | WITHDRAWN | 10.31234/osf.io/ms7gv_v2 | C1-0465と同一論文の撤回版(WITHDRAWN)だが内容は同一で候補定義に合致 | 照合 |
| C1-0481 | 2024 | Developing evaluative judgement for a time of generative artificial intelligence | 10.1080/02602938.2024.2335321 | 生成AI時代の評価的判断力育成を論じ、人が質の裁定者であり続けるべきと明示している | 未実施（逸脱 2） |
| C1-0483 | 2024 | Artificial intelligence in mental healthcare: transformative potential vs. the necessity of human interaction | 10.3389/fpsyg.2024.1378904 | AIへの過度な依存に対する人的関与・監督の必要性を論じており候補に近いが明示性はやや弱い | 未実施（逸脱 2） |
| C1-0513 | 2025 | The Outsourcing of Agency: How Reliance on AI May Lead to the Delegation of Human Decision-Making | 10.2139/ssrn.5262236 | AIへの依存が人間の意思決定の委任(outsourcing)へ至る過程を扱う題名で候補と近接するが抄録なし | 未実施（逸脱 2） |
| C1-0514 | 2024 | Redefining Spectral Data Analysis with Immersive Analytics: Exploring Domain-Shifted Model Spaces for Optimal … | 10.1177/00037028241280669 | 自律的な化学計量機械学習が人の判断を排除する問題に対し没入型分析で専門家の判断を要所に再挿入する設計を提案し候補に明確に合致 | 未実施（逸脱 2） |
| C1-0521 | 2011 | Needs And Approach For Combining Formal Analysis And Human Instinct In Logistics Simulation Projects | 10.7148/2011-0601-0607 | 定式化されたアルゴリズムがシミュレーション担当者の直観を奪うことを問題視し人間の解釈的役割を維持する統合手法を提案している | 未実施（逸脱 2） |
| C1-0540 | 2026 | Reclaiming Judgment in the Age of Generative AI: Design, Internalized Hierarchy, and Individual Agency | 10.5281/zenodo.18136100 | 生成AIによる選択アーキテクチャが人間の判断力を侵食する過程を分析し判断を取り戻す設計を論じている | 未実施（逸脱 2） |
| C1-0541 | 2026 | Reclaiming Judgment in the Age of Generative AI: Design, Internalized Hierarchy, and Individual Agency | 10.5281/zenodo.18136101 | 生成AIによる推薦・最適化が個人の判断を内面化させ認識的境界を委譲させる過程を論じ、摩擦・不確実性・責任の保持という設計論的含意を持つため採る（迷いあり） | 未実施（逸脱 2） |
| C1-0552 | 2025 | Algorithmic Governance of Territory and Market Dominion: The Role of Public Oversight | 10.1007/978-3-032-19720-7_25 | アルゴリズムによる行政サービス個別化が個人ユーザーに評価・影響力を付与すると明記しており、系が評価権限を個人へ渡す論点を含むため採る（迷いあり、主眼は行政の統制喪失批判） | 未実施（逸脱 2） |
| C1-0567 | 2025 | Visualizing data using immersive virtual reality for improved analysis | 10.1117/12.3052999 | 自律的機械学習が人間の関与を排除しようとする傾向を批判し、没入型分析(IVR)により重要なアルゴリズム的分岐点で専門家の人間判断を挿入する設計を提案しており、系が評価権限を人へ返す設計原理として明示的に該当する | 未実施（逸脱 2） |
| C1-0583 | 2026 | A Framework to Leverage Large Language Models to Address Pressing Issues in US Academic Medicine | 10.31234/osf.io/y7etf_v1 | LLMを学術医療計画の思考支援に用いつつ、その出力を利害関係者の専門的判断でフィルタリングし人間の批判的判断を保持する枠組みを明示しており、系が評価権限を人間の判断へ委ねる設計として該当する | 未実施（逸脱 2） |
| C1-0584 | 2026 | A Framework to Leverage Large Language Models to Address Pressing Issues in US Academic Medicine |  | C1-0583と同一内容の別版で同様の理由により採用 | 未実施（逸脱 2） |
| C1-0623 | 2026 | AI With and Within User Research Across the Product Lifecycle | 10.54941/ahfe1007314 | AIの自動出力への過信によるリサーチ判断力の侵食を明示的に課題視し、AIを補助ツールと位置づけて解釈・意思決定の説明責任を人間の研究者に残す人間工学フレームワークを提案しており、C1の定義に明確に該当する | 未実施（逸脱 2） |
| C1-0629 | 2025 | A Philosophical Approach to Judicial AI: The Role of Judgment in The Decision-Making Process |  | 抄録空だが題名『司法AIにおける判断の所在』から、系と人間の判断権限の哲学的検討と読め、迷ったら採る原則により採用 | 未実施（逸脱 2） |
| C1-0634 | 2026 | IntelliAudit: Using Large Language Models to Evaluate Audit Controls |  | 監査エビデンス評価AIが「自律的認定システムではなく意思決定支援に留まるべき」とし、十分性判断の権限を人間監査人に残すと明記している | 未実施（逸脱 2） |
| C1-0638 | 2026 | When Experts Disagree: Diagnosing Cultural Heritage Image Editing Through the Lens of Interpretive Plurality | 10.1145/3772363.3798599 | 文化遺産画像編集AIについて「系は判断を自動化するのではなく解釈を支援すべき」と明示的に論じている | 照合 |
| C1-0643 | 2026 | Beyond Distance Metrics: A Nested Model of Similarity in Visual Art Search | 10.1145/3811427.3811442 | 芸術検索における類似性を「メトリック中心から利用者の解釈・主体性を重視する層構造へ」転換すべきと明示的に論じている | 未実施（逸脱 2） |
| C1-0646 | 2012 | SYSTEM FOR INTERPRETATION OF REVIEWER FEEDBACK ON SOCIAL WEB by SHRIKANT DESAI |  | 抄録なし。題名「レビューフィードバック解釈システム」は系による意味解釈の扱いに触れる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0652 | 2026 | Reconfiguring Geovisualization in the Age of Generative AI: Insights from Domain Experts |  | GenAI導入により「ボトルネックが生産から判断・検証へ移行し、専門的価値は解釈・倫理的判断に依存する」と明示的に論じている | 未実施（逸脱 2） |
| C1-0653 | 2016 | Retrieval Profiling Framework for Thematic Interpretation of Al-Quran | 10.1109/ict4m.2016.036 | 抄録なし。題名「クルアーン主題解釈のための検索システム」は解釈権限の扱いに触れる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0658 | 2018 | Consensus Theory and Relevance Judgment Model: a test case of English Wikipedia |  | 抄録なし。題名「合意理論と関連性判断モデル」はWikipediaにおける人間側の合意による判断権限の扱いに触れる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0659 | 2024 | Modeling Future Conversation Turns to Teach LLMs to Ask Clarifying Questions | 10.48550/arxiv.2410.13788 | LLMが単一解釈を押し付けず明確化質問を通じてユーザーの意図した解釈を確認するよう学習させる手法を提案している | 照合 |
| C1-0660 | 2026 | Algorithmic Compassion in Holistic Nursing: A Concept Analysis and Conceptual Model. | 10.1177/08980101261487731 | AI介護システムの「共感的応答」が人間の判断・尊厳・同意によって倫理的に境界づけられた補助的役割にとどまると概念定義している | 未実施（逸脱 2） |
| C1-0661 | 2026 | JudgmentLens: Human-AI Sensemaking of Complex Legal Judgments |  | 法律文書解釈支援AIシステムで、質問形成・回答統合・出典確認は利用者に委ねられると実証的に報告している | 照合 |
| C1-0662 | 2016 | Explicit In Situ User Feedback for Web Search Results | 10.1145/2911451.2914754 | 抄録なし。題名「Web検索結果への明示的なその場ユーザーフィードバック」は利用者側の評価権限維持に触れる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0664 | 2021 | Metaphor, Blending and Irony in Action: Creative Performance as Interpretation and Emotionally-Grounded Choice |  | 抄録なし。題名は計算論的創造性会議(ICCC)の論文で創造的パフォーマンスの解釈権限に触れる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0666 | 2019 | Human expertise in the interpretation of remote sensing data: A cognitive task analysis of forest disturbance … | 10.1016/j.jag.2018.08.026 | 森林撹乱判読において自動画像解析の限界から「人間と計算機の共生的解釈系を設計すべき」と明示的に論じている | 未実施（逸脱 2） |
| C1-0668 | 2025 | Augmented Intelligence in Enterprise Content Management: Human-in-the-Loop Systems and Conversational Interfac… | 10.22399/ijcesen.4245 | 文書分類・機密情報削除を系が提案し、専門職員が採用前に検証・承認することで法的に重要な判断の制御を維持すると明記している | 未実施（逸脱 2） |
| C1-0671 | 2023 | Human–AI Collaboration in Creative and Analytical Tasks | 10.67228/3071561x/ijirht-2023pi5q5c | Human-AI協働レビューで「人間の判断が倫理的監督と正確な解釈を担保し、自動化と人間の制御のバランスが必要」と明示的に論じている | 未実施（逸脱 2） |
| C1-0673 | 2026 | Personal Health Large Language Models and the Negotiation of Medical Authority in Clinical Care: Opportunities… | 10.2196/91727 | Personal Health LLMが臨床医-患者の二者関係を臨床医・患者・アルゴリズム物語の三者間の権限交渉へ変容させると明示的に論じている | 未実施（逸脱 2） |
| C1-0675 | 2026 | Trust by Design: Trust Calibration Through Non-Advisory Socratic Dialogue in Conversational Agents |  | 対話エージェントCASELyが助言・解釈を拒否し自らの権限を制約することでユーザーの意思決定権限を保持する設計を明示している | 照合 |
| C1-0676 | 2026 | Red Light, Grey Zone: A Multi-Perspective Interactive Narrative for Autonomous Driving Ethics | 10.48550/arxiv.2607.15888 | 対話型ナラティブが自動運転倫理の責任判断を系ではなく参加者自身に委ねるよう設計されていると報告している | 未実施（逸脱 2） |
| C1-0678 | 2025 | HUMAN-CENTERED AI AND EXPLAINABLE DECISION SUPPORT | 10.59982/18294359-25.2-hc-18 | Human-Centered AIの説明は「人間の推論を支援するためのものであり、人々が判断能力を維持できるようにする」と明示的に論じている | 未実施（逸脱 2） |
| C1-0683 | 2026 | ReliaPy: A Python Workbench for Accessible Reliability Analysis | 10.1109/mrl.2026.3718843 | 信頼性解析ワークベンチReliaPyが「専門家の工学的判断を置き換えるものではない」と明示的に位置づけている | 未実施（逸脱 2） |
| C1-0685 | 2025 | When Music Paints: A Multi-Agent Framework for Cross-Modal Cultural Semantics | 10.1109/iscid68789.2025.00059 | 音楽画像生成マルチエージェント系がHuman-in-the-Loopにより利用者が感情解釈を修正・上書きできる設計を明記している | 未実施（逸脱 2） |
| C1-0703 | 2016 | A Crowd-Powered System for Fashion Similarity Search | 10.1145/2897365 | 抄録なし。題名「クラウドパワード・ファッション類似検索系」は類似性判断を人間の集合判断に委ねる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0705 | 1988 | A financial expert decision support system | 10.1007/978-3-642-83555-1_25 | 抄録なし。題名「金融エキスパート意思決定支援システム」は専門家判断を支援するに留まる設計を論じる可能性があり判断保留のため採用 | 未実施（逸脱 2） |
| C1-0713 | 1989 | Guidelines for computer-based psychological tests and interpretations | 10.1016/0747-5632(89)90020-4 | コンピュータによる心理検査解釈のガイドラインで、専門家による確認・利用を前提とし系が単独で解釈権限を持たないよう規定する可能性が高い | 未実施（逸脱 2） |
| C1-0717 | 2003 | Automated Laboratory Reporting of Infectious Diseases in a Climate of Bioterrorism | 10.3201/eid0909.020486 | 自動化された感染症検査室報告システムにおいて「プロセス内での人間の判断の保持」が必要と明示的に提言している | 未実施（逸脱 2） |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

