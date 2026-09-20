# ふるい分けの記録 —— C4

> 候補の定義（protocol.md §1）: **系が故障や限界ではなく、価値判断によって任意に権限を返す（手放す）局面**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 722 |
| 段 1 で採った | 19 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 0 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 19 |
| 段 2 の判定（メインの訂正の後） | 該当 1 ／ 部分 11 ／ 非該当 7 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 0 |

## 結論

★ **既出**（該当: C4-0298 [P401]。⚠️ 査読のないプレプリント 1 件）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C4-0298 | 該当 | 本文 | Capability Can(a, C_t)? Can the AI perform action a? This concerns model and system capability. ... Participation Should(a, C_t)? Among available and permissible actions, is a the appropriate form of participation now? | p.9-10, §3.5 Capability, Permission, and Participation | 「系が」（AIシステム自身が）、「故障や限界ではなく」（Can=能力とShould=参加選択を明確に分離し、権限返却をCanの不足に帰さない）、「価値判断によって」（Should/Governanceに基づく文脈適合性の判断=Participation Optimization）、「任意に」（系が admissible な選択肢の中から自ら選択する最適化問題として定式化）、「権限を返す（手放す）」… |  | ★ メインが本文で照合 |
| C4-0190 | 部分 | 抄録のみ | we consider computer tools for architectural design based on shape grammar design systems, and evaluate the advantages and disadvantage of handing over these tools to inhabitants for the design of their apartments. This … | abstract | 『権限(設計ツール)を手放す(hand over)』ことが『価値(values of inhabitants, architects, and cities)』の定性的評価に基づくという要素は明確（抄録に故障・限界への言及はない）。ただし手放す主体は『系』自身ではなく建築家・研究者であり、運用中の系が任意の局面で判断して権限を返すのではなく、設計方針として事前に評価・提案する構造である点でC4の想… | メイン未照合（出典ページが開けない） |  |
| C4-0244 | 部分 | 本文 | We will argue that full autonomy of the robot will not be appreciated by a human subject; a human being by nature will try to read the situation and adapt the team (robot and human) behaviour to that reading. ... Thus so… | p.1 Introduction | 『人間に受け入れられないから』『人間が支配的立場であることを望むから』というC4の言う価値判断（信頼・受容・支配）に基づき、ロボットの自律性・権限を制限するという要素は明確で、故障や性能限界への言及ではない。一方で、これは運用中の系が任意の局面で権限を『返す』出来事ではなく、設計段階で自律性の上限を最初から低く固定する設計方針であり、C4が想定する『局面』性・『系が自ら』返すという要素はやや弱い。 |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0255 | 部分 | 本文 | At one end of the spectrum, Reef seeks to be informative by showing useful eco-feedback to help decision-making, letting users remain in control | p.5 Eco-Coaching Style | 『ユーザーのagencyを尊重する(respecting users' agency)』という価値判断がhands-off設計（＝制御をユーザーに残す）の一因として明記されており、この点はC4の『価値判断』要素に該当。しかし同じ文で『不正確さへの対処(handles inaccuracy)』『予測の不完全性(imperfect prediction)』という系の限界も並列の理由として明記されており… |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0277 | 部分 | 抄録のみ | requiring agents to be willing to give up their current resources to those with greater need by reasoning about what is for the common good | abstract | 『共通善(common good)の推論』という価値判断に基づき、エージェントが現在保持する資源を手放すという要素は抄録レベルで該当的（故障・限界への言及なし、ex-ante rationalという規範的枠組み）。ただし『手放す』対象はタスクが占有する計算資源であり、権限を受け取る側も人間ではなくエージェント間の再配分である点が、C4が想定する適応系→人への認識的・意思決定権限の返還とは主体関係が… |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0310 | 部分 | 本文 | Ethical safeguards: All generated content is cross-referenced against the knowledge graph to ensure ideological consistency, and potentially sensitive adaptations (e.g., frustration-triggered difficulty reduction) requir… | p.12, §3.7 End-to-end adaptive tutoring algorithm | 「権限を返す」に対応する記述は『sensitive adaptations は educator approval を要する』の一文のみ。sensitivityという価値的理由に基づく点はC4に部分的に合致するが、同じ節にある『confidence閾値を下回ったらfallback』という故障・限界起因の分岐と並置されているだけで、両者を『故障ではなく価値判断』として明示的に区別する記述は本文になく… |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0328 | 部分 | 抄録のみ | Second, the paper specifies implementable safeguards including anti-coercion detection (engagement-truthfulness alignment monitoring), honesty requirements with confidence thresholds, and autonomy preservation through bo… | Abstract | 『bounded system authority』は尊厳・反強制という価値に基づき系の権限を制限する設計であり、『価値判断』『権限』の要素には触れる。しかし『bounded（上限を設ける）』は恒常的な権限の制限設計であり、C4が指す『返す（手放す）』という動的な移譲局面とは性質が異なる。『故障や限界ではなく』という対比も、『任意に』（局面ごとの系の裁量）という要素も抄録からは確認できない。 |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0331 | 部分 | 抄録のみ | HAPF is introduced as an operational framework structured around four pillars: transparency and interpretability supports, control and override mechanisms, bias and value auditing, and agency assessment. | Abstract | 『control and override mechanisms』は人間が系の決定を制御・上書きできる仕組みを指し、『権限を返す』に部分的に対応する。ただしこれは人間側に用意された介入手段という記述であり、系が自発的に（任意に）、故障や限界ではなく価値判断によって権限を手放す、という能動的局面を述べたものではない。抄録からは『故障や限界ではなく』の対比も確認できない。 |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0341 | 部分 | 抄録のみ | As agentic AI increasingly serves as a source of expert advice, designers face critical moral questions: should AI advisors optimize outcomes, guide users, or present information neutrally? | Abstract | 『complete agency』（情報提示のみで推奨を控える設計）は、系が評価的・助言的権限を行使せず情報提示に留める点で『権限を返す（手放す）』に対応し、“moral questions”“normative roles”という価値判断に基づく設計選択であることも明示される。ただしこれは利用者選好を実測した実証研究であり、『故障や限界ではなく』という対比は抄録に明示されない。また対象は当初から… |  | メインが抄録・取り出したテキストと機械照合 |
| C4-0351 | 部分 | 本文 | A transfer of control that is triggered by the system is desirable in circumstances e.g., where the human is not responsive, under extreme stress or in a suppressed cognitive state | § Variable Autonomy | 価値を理由に人の統制を設計する点は当たる・系が移す契機は人の状態 | 段 1 で protocol に無い理由で除外 → 逸脱 3 の検算で復活。メインが直接照合 | ★ メインが本文で照合 |
| C4-0370 | 部分 | 本文 | the AI would no longer act as an authority that merely generates textual information or provides decision-making recommendations, but would instead function as a facilitator that guides users in their reflective processe… | Conclusion 節 | 「系(SocrAIチャットボット)が」「価値判断(procedural neutrality・自律性尊重という設計上の価値)によって」「任意に(設計上の選択として)」「権限(authority=回答を下す役割)を人へ返す」の4要素は確認できる。「故障や限界ではなく」の要素は、序論で『通常のチャットボットが自律性を侵害するのは開発者の意図的な設計選択ではなく AI の内在的限界に由来する』(l.98… | 段 2 担当は「該当」→ メインが下げた（設計として恒常的に権威を持たない形・局面での返却ではない） | メインが抄録・取り出したテキストと機械照合 |
| C4-0530 | 部分 | 本文 | we argue for a perspective shift towards disengagement as a design tool that allows for unobtrusive and smooth exits from the game | Abstract | 「系(ゲームデザイン)が」「価値判断(自律性・健全な関係という価値)によって」「任意に(at their own volition)」プレイヤーへ「主体性/agency を返す(re-gain agency)」という要素は本文中に確認できる。「故障や限界ではなく」の要素は、§2.2 で述べる『主流見解=disengagement は poor design(=故障/限界)の結果』という立場を§4結… | 段 2 担当は「該当」→ メインが下げた（離脱の手がかりの設計・系が局面で任意に返す形ではない） | メインが抄録・取り出したテキストと機械照合 |
| C4-0016 | 非該当 | 抄録のみ | a model for agents to reason about whether to retain autonomy or fully transfer decision-making control to another entity (user or agent) | abstract | 抄録は『状況に応じて自律性を保持するか、決定権限を完全に他エンティティへ移譲するかを推論する』とあるのみで、移譲の理由が価値判断か自律性の限界（誤り費用・信頼度等）かを明示しない。定義の必須要素『故障や限界ではなく』『価値判断によって』を裏づける逐語が本文（未読）にも抄録にも見当たらない。 |  |  |
| C4-0049 | 非該当 | 本文 | When an autonomous automation that is working side-by-side with a human reaches a limit for its autonomy, there must be a way for the human to cope with a reduction in autonomy. | p.261 Introduction | 自動化が人間(ATCO)に相談し判断を委ねる『権限を返す』局面自体はある。しかし本文全体でその契機は一貫して『自律性の限界に達すること(reaches a limit for its autonomy)』『管轄・手段の欠如(does not have the jurisdiction nor the means)』であり、C4の必須要素『故障や限界ではなく』と正面から矛盾する。Discussion… |  |  |
| C4-0217 | 非該当 | 抄録のみ |  |  | 抄録が空文字列で本文・抄録とも入手できず、題名 (Transfer of Control / Adjustable Autonomy Multiagent Systems) のみで判定。Transfer of Control (ToC) 研究は一般に、エージェントが自身の能力・確信度の限界を評価して人へ制御を移す『限界駆動』の枠組みが主流であり、これは C4 が要求する『故障や限界ではなく』の要件… |  |  |
| C4-0318 | 非該当 | 抄録のみ | Findings indicate that users value personalization when it is contextual, explainable, and controllable, but they reject systems that feel opaque, mistimed, or overly directive. | Abstract | 抄録は利用者が『制御可能性』『透明性』を求め、過度に指示的なシステムを拒否するという利用者選好の実証結果を述べるに留まる。『系が』『故障や限界ではなく』『価値判断によって』『任意に』『権限を返す（手放す）』という定義の要素に当たる記述は抄録中に見当たらない。C1（系が利用者に認識的権限を返す）寄りの主題に見えるが、C4が要求する『故障ではなく価値判断による能動的な返却』を明示する逐語はない。 |  |  |
| C4-0626 | 非該当 | 抄録のみ |  |  | 抄録には『系が故障や限界ではなく価値判断によって任意に権限を返す』という要素の逐語が無い。主語は『研究者・早期思春期の子ども』であり、対象は親による媒介戦略(parental mediation)の共創であって、系(アプリ等)自体が能力を持ちながら価値判断で権限を手放す場面は記述されていない。 |  |  |
| C4-0627 | 非該当 | 抄録のみ |  |  | 抄録は通知設計を『共感的・協働的・文脈依存』に再設計し負担を減らす、という主旨で、解釈・負担(C2寄り)の記述はあるが、C4が要求する『系が故障や限界ではなく価値判断によって任意に権限を返す』という逐語は無い。通知を出す/出さないという権限の返還そのものへの言及もない。 |  |  |
| C4-0628 | 非該当 | 抄録のみ |  |  | 抄録の主語は『個人(利用者)』の目標離脱過程であり、『系(技術)が』権限を返すという構図ではない。技術は『適応的な目標離脱を支援するよう設計されうる (can be designed to support adaptive goal disengagement)』とあるが、これは利用者自身の離脱プロセスを支援する機能提案であって、系自身が能力を持ちながら価値判断で介入・通知等の権限を手放す場面の逐… |  |  |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C4-0016 | 2005 | A hybrid transfer of control model for adjustable autonomy multiagent systems | 10.1145/1082473.1082667 | マルチエージェントの調整可能自律性における制御移譲の意思決定モデル。限界起因か価値判断起因か本文確認が必要 | 照合 |
| C4-0049 | 2022 | Reduced autonomy workspace (RAW)—an interaction design approach for human-automation cooperation | 10.1007/s10111-022-00695-2 | 自動化の自律性低下時の人への引き継ぎ設計(RAW)。低下の理由が価値判断か状況要求かを本文確認する必要 | 照合 |
| C4-0190 | 2021 | Shape Grammar Systems as a Technology for Flexible Design for Values in Cities: Giving Architectural Design to… | 10.1007/978-3-030-52313-8_12 | アーキテクチャ設計システムが価値判断で住民に設計権限を与える論点の可能性(抄録欠如、題名のみで判断、段2で確認) | 照合 |
| C4-0244 | 2013 | Enhancing trust and confidence in human robot interaction |  | 盲導犬との類推で責任分担を論じ、信頼構築のための設計選択が倫理的課題を伴うと明記（混合主導・責任の非全面委譲）。段2で価値判断による自発的権限抑制の逐語を確認 | 照合 |
| C4-0255 | 2017 | Reef | 10.1145/3064663.3064685 | 快適性・持続可能性・制御・利便性・エージェンシー配分という『価値』を尊重する設計として、完全自動化ではなく混合主導のエコ・コーチングを提案。段2で価値判断による権限抑制の逐語を確認 | 照合 |
| C4-0277 | 2012 | An Ex-Ante Rational Distributed Resource Allocation System using Transfer of Control Strategies for Preemption… |  | エージェントが『共通善』の推論に基づき自発的に資源を手放すことを要件とする分散資源配分。能力限界ではなく規範的判断による権限放棄の可能性があり、段2で確認 | 照合 |
| C4-0298 | 2026 | Beyond Output Quality: Participation Quality as a Distinct Evaluation Construct and Control Objective for Huma… | 10.5281/zenodo.21837135 | AIが『いつ答え、いつ判断を人間に残すか、いつ制御を返すか』を評価するParticipation Qualityの枠組みを提案。系が判断・制御を人間に残す/返すことを明示的に論じており、価値判断による自発的選択かを段2で確認 | 照合 |
| C4-0300 | 2026 | Beyond Output Quality: Participation Quality as a Distinct Evaluation Construct and Control Objective for Huma… | 10.5281/zenodo.21837134 | 298と同一内容（別DOI） | 照合 |
| C4-0310 | 2026 | Integrating knowledge tracing and reinforcement learning in an AI-powered system for personalized ideological … | 10.1007/s44163-026-01679-1 | AI思想教育システムが'non-persuasive oversight mechanisms'により価値形成的自動化のリスクを抑制する設計を論じる。系が能力があっても説得的介入を価値判断で控える設計原理に該当しうるため段2で確認 | 照合 |
| C4-0318 | 2026 | Between AI and User Agency: Designing Adaptive AI Guidance Systems for Intentional Wellness Decisions | 10.1184/r1/32984789.v1 | 適応的AIウェルネス助言システムの設計論。過剰自動化を避け利用者の自律性を保持する'guided'ではなく透明で利用者定義の境界を持つ設計を提案しており、価値判断による行使抑制の設計原理に該当しうる。段2で確認 | 照合 |
| C4-0319 | 2026 | Between AI and User Agency: Designing Adaptive AI Guidance Systems for Intentional Wellness Decisions | 10.1184/r1/32984789 | C4-0318と同一研究(学位論文版)。同理由で段2確認 | 照合 |
| C4-0328 | 2026 | Dignity-First Artificial Intelligence: Privacy, Ethics, and Human Agency in Stateful Systems | 10.2139/ssrn.6532179 | 'Dignity-First AI'が'bounded system authority'によりステートフルAIシステムの権限を建築的に制限する枠組みを提案。尊厳・反強制という価値に基づき能力を制限する設計原理に該当しうる。段2で確認 | 照合 |
| C4-0331 | 2026 | Human Agency in AI-Mediated Education or Ethical Risks and Opportunities via the Human Agency Preservation Fra… | 10.1109/usbereit70063.2026.11580622 | Human Agency Preservation Framework(HAPF)が'control and override mechanisms'の柱でagency-preserving/constrainingなシステム挙動を区別する評価枠組みを提示。段2で確認 | 照合 |
| C4-0341 | 2026 | Autonomy or Guidance: What Users Want from AI versus Human Advisors | 10.1145/3815120 | AI助言システムのcomplete agency(情報提示のみで推奨を控える)設計をユーザが選好する実証研究。系が能力があっても指示的助言を控える価値判断的設計の実測に該当。段2で確認 | 照合 |
| C4-0370 | 2025 | Addressing Autonomy Risks in Generative Chatbots with the Socratic Method | 10.1007/s11948-025-00567-8 | 生成AIチャットボット(SocrAI)がソクラテス式問答法により直接回答を控え利用者の自律性・認知的関与を保持する設計を提案。能力があっても直接的援助を価値判断的に抑制する設計原理に該当。段2で確認 | 照合 |
| C4-0530 | 2023 | Designing for Disengagement: Challenges and Opportunities for Game Design to Support Children's Exit From Play | 10.48550/arxiv.2303.15400 | ゲームデザインが子どものプレイからの離脱(disengagement)を自律性尊重の設計原理として論じており、系が能力があっても人へ関与を返す価値判断の設計を扱うC4候補に明示的に合致する | 照合 |
| C4-0626 | 2023 | Co-Designing with Early Adolescents: Understanding Perceptions of and Design Considerations for Tech-Based Med… | 10.1145/3544548.3581134 | 技術ディスエンゲージメントを促す媒介戦略の共創研究。candidate定義の例示語 'designing for disengagement' に直接該当しうるが、系自身の行使抑制か親による利用制限かは抄録では未確定のため段2で確認 | 照合 |
| C4-0627 | 2025 | “Can you stop beeping!”: Designing Notifications that Empathise with Fatigue in Diabetes Technology | 10.1145/3715668.3736353 | 糖尿病技術の通知を疲労への共感から再設計する研究。価値(共感・負担軽減)に基づき通知という介入を控える設計原理を論じている可能性があり段2で確認 | 照合 |
| C4-0628 | 2026 | Designing for Health Goal Disengagement and Prioritization | 10.1145/3786579.3801803 | 健康目標からの'適応的ディスエンゲージメント'を支援する個人情報技術の設計論。'designing for disengagement'に類似する題名だが、系の権限返還か利用者自身の目標変更支援かは抄録では未確定のため段2で確認 | 照合 |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

