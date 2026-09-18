# S1 生報告の退避（サブエージェント S1-a / S1-b）—— ⚠️ 未検証。3 票検証の入力

> 2026-09-19。サブエージェント（Opus）の報告をそのまま保存する（★ 取り込みは S7・S8 のコミット後）。⚠️ 逐語・頁・DOI はサブエージェントの報告であり、カード化の前にメインが要所を検算する。

## S1-a（ironies of automation / moral crumple zone / responsibility gap / 検証負担の移転）

### 要点（サブエージェントの結論）
- 草案 1（返権の負荷逆説）の一般形 ——「権限を名目上は人の側に置いたまま、負担を人へ集中させる配置」—— には先例がある: **Woods 1985「responsibility/authority double-bind」**、Elish 2019、Green 2022、Bainbridge 1983。
- 草案 2（二重台帳）にも直接の先例: **Flemisch et al. 2012 の A2CR**（ability / authority / control / responsibility を主体ごとに別記述し、整合規則を置く）。「権限を渡すと責任が生じる」も逐語（C9）。
- 残る差分（読んだ範囲）: (a) 返される権限の**対象**（既存 = 制御・上書き・決定 ／ 草案 = 意味づけ・認定・報酬化）、(b) 返す**動機**（既存 = 自動化の破綻時のテイクオーバーか、制度が正当化のために置く名目上の上書き権 ／ 草案 = システムが設計価値として自ら手放す局面を失敗様式として分析）—— 後者は今回の検索範囲で見つからず。
- 注意（サブエージェントの推論・逐語ではない）: 草案の配置は権限と責任が両方とも利用者側にあるので A2CR の「authority ≥ responsibility」に違反しない。A2CR で捉えられるのは「ability < authority」の不整合だけ。草案が「ability < authority ＋ 権限を渡すと責任が生じる」の言い換えに縮約されないことを示せるかが新規性の要。

### 文献表
| 著者 年 | 題名 | DOI | 読めた範囲 |
|---|---|---|---|
| Bainbridge 1983 | Ironies of automation（Automatica 19(6):775–779） | 10.1016/0005-1098(83)90046-8（Crossref 確認） | 全文 |
| Strauch 2018 | Ironies of Automation: Still Unresolved After All These Years（IEEE THMS 48(5):419–433） | 10.1109/THMS.2017.2732506 | 全文（著者受理稿・頁は推定） |
| Simkute et al. 2024/25 | Ironies of Generative AI（IJHCI） | 10.1080/10447318.2024.2405782 | 全文（arXiv:2402.11364 版） |
| Elish 2019 | Moral Crumple Zones（ESTS 5:40–60） | 10.17351/ests2019.260 | 全文 |
| Matthias 2004 | The responsibility gap（Ethics & Inf Tech 6(3):175–183） | 10.1007/s10676-004-3422-1 | 全文 |
| Santoni de Sio & Mecacci 2021 | Four Responsibility Gaps with AI（Phil & Tech 34:1057–1084） | 10.1007/s13347-021-00450-x | 全文 |
| Passi & Vorvoreanu 2022 | Overreliance on AI: Literature review（MSR-TR-2022-12） | DOI なし | 全文 |
| Woods 1985 | Cognitive Technologies: The Design of Joint Human-Machine Cognitive Systems（AI Magazine 6(4):86–92） | 10.1609/aimag.v6i4.511（doi.org 解決確認・Crossref API 応答なし） | 全文 |
| Flemisch et al. 2012 | Towards a dynamic balance between humans and automation: authority, ability, responsibility and control…（Cognition, Technology & Work 14(1):3–18） | 10.1007/s10111-011-0191-6 | 全文（OA） |
| Green 2022 | The flaws of policies requiring human oversight of government algorithms（Computer Law & Security Review 45:105681） | 10.1016/j.clsr.2022.105681 | 全文（arXiv:2109.05067v4） |
| Wagner 2019 | Liable, but Not in Control?（Policy & Internet 11(1):104–122） | 10.1002/poi3.198 | abstract のみ |

### claim（逐語）
- C1 Bainbridge p.775 "THE classic aim of automation is to replace human manual control, planning and problem solving by automatic devices and computers."
- C2 Bainbridge p.775 "the designer who tries to eliminate the operator still leaves the operator to do the tasks which the designer cannot think how to automate … little thought may have been given to providing support for them."
- C3 Bainbridge p.776 "very boring but very responsible, yet there is no opportunity to aquire or maintain the qualities required to handle the responsibility." / "The human monitor has been given an impossible task."
- C4 Strauch（受理稿 p.2）"automating heretofore operator-performed tasks leaves the operator with the responsibility of addressing the consequences of automated system anomalies."
- C5 Simkute p.2 "users' roles have shifted from producing output to evaluating it, often with little contextual information and situational awareness."
- C6 Simkute p.16 "GenAI tools provide ideas in an open-ended form (e.g., probing questions), rather than as explicit suggestions … found to be particularly helpful in copywriting"（★ 緩和策として扱い、失敗様式は論じない）
- C7 Elish p.41 "incongruities between control and responsibility" / "their tendency to become 'liability sponges'"；p.49 "While control has been effectively distributed, responsibility has not scaled accordingly."
- C8 Elish p.47 "Alternate Law … a mode in which primary control is in the hands of the pilot. It is in effect when parts of the computer system or autopilot are unable to work as designed"
- C9 Flemisch p.7 "Ability should not be smaller than authority; authority should not be smaller than responsibility." / "the existence of sufficient ability and authority to control constitutes also the responsibility to control."；p.15 "the co-system does not just drop control"
- C10 Woods p.88 "it is the human problem solver who has responsibility for the outcome. Of course, the person has in principle the authority to override the machine" / "great danger of a responsibility/authority double-bind"；p.86 "the potentially difficult and unsupported task of filtering poor machine solutions"
- C11 Matthias p.176 "In situations where the operator has reduced control over the machine he also bears less or no responsibility."
- C12 Santoni de Sio & Mecacci p.1057 "gaps in culpability, moral and public accountability, active responsibility"；p.1063 public accountability = "an obligation to explain and to justify"
- C13 Passi & Vorvoreanu（要旨）"calls for greater human oversight—making users the last line of defense against AI failures"
- C14 Green p.9 "shift accountability for algorithmic harms from agency leaders … to frontline human operators (who are relatively powerless)."
- C15 Passi & Vorvoreanu p.13 "CFFs mitigate overreliance but are often less favored by users because of the added cognitive burden."
- C16 Wagner（abstract）"'quasi-automation' as inclusion of humans as a basic rubber-stamping mechanism"

### 見つからなかったもの（今回の範囲）
- システムが意味づけ・認定・報酬化の権限を**設計価値として自ら手放す**局面を失敗様式として分析した記述
- 解釈・検証・修正（認知的労働）と応答・是正・帰結（規範的責任）を**同じ負担台帳**に並べる枠組み
- 「liability sponge」の査読文献での出典（Elish p.41 は出典表示なし）
- ⚠️ 範囲外で差分を脅かしうる系譜（未検証）: privacy self-management / notice-and-choice（Solove 2013）・社会学の responsibilization・Dekker 2002・Woods & Cook 2002・accountability sink（Davies 2024）

## S1-b（A2CR・take-over・adjustable autonomy・mixed initiative）

> 取得済み本文: `C:\Users\johnd\AppData\Local\Temp\s1b\`。DOI はすべて Crossref 確認。

### 結論（サブエージェント）
- **GR-C1 は制御権限については既存研究の中心的な記述対象で、新規命題としては書けない** —— Flemisch 2012 は「制御配分を変える権限（change authority）」を人と機械の双方に割り当てる。adjustable autonomy は定義上「エージェント → 人」の移譲。Parasuraman 1996 は自動化した課題を監視能力のために一時的に人へ戻す実験を行っている。
- **権限と責任を別次元として扱い不一致を問題にする形式は既にある**（Flemisch A2CR 図・Pritchett 2014 の不一致指標 ＝ 不一致が生む監視作業を作業負荷として別計上・Elish 2019）。返還に伴う負担の移転も記述済み（Lu 2016・Scerri 2002・Parasuraman, Sheridan & Wickens 2000 の「残り物」批判）。
- **残る差分は狭い** —— 今回の範囲で見つからなかったのは次の 3 点の**組み合わせ**: (a) 返す対象が制御ではなく**意味の認定・評価・報酬という認識的権限**、(b) 負担項目に**解釈と説明要求**が入る、(c) **権限と責任が一致したまま返還しても残務が移る型**。⚠️ (a) の近傍に PSW 2000 の「情報分析」の自動化・Simkute 2024・既登録の [P183] / [P364] / [P365]。

### 文献表
| # | 著者 年 | 題名 | DOI | 範囲 |
|---|---|---|---|---|
| 1 | Flemisch, Heesen, Hesse, Kelsch, Schieben & Beller 2012 | （S1-a と共通・CTW 14(1):3–18） | 10.1007/s10111-011-0191-6 | 全文 OA |
| 2 | Flemisch, Abbink, Itoh, Pacaux-Lemoine & Weßel 2019 | Joining the blunt and the pointy end of the spear（CTW 21(4):555–568） | 10.1007/s10111-019-00576-1 | 該当箇所 |
| 3 | Pritchett, Kim & Feigh 2014 | Measuring human-automation function allocation（JCEDM 8(1):52–77） | 10.1177/1555343413490166 | 著者版全文 |
| 4 | Lu, Happee, Cabrall, Kyriakidis & de Winter 2016 | Human factors of transitions in automated driving（TR-F 43:183–198） | 10.1016/j.trf.2016.10.007 | 受理稿全文（頁は受理稿） |
| 5 | Eriksson & Stanton 2017 | Takeover time in highly automated vehicles（Human Factors 59(4):689–705） | 10.1177/0018720816685832 | abstract |
| 6 | McCall et al. 2019 | A taxonomy of autonomous vehicle handover situations（TR-A 124:507–522） | 10.1016/j.tra.2018.05.005 | abstract |
| 7 | SAE 2021 | J3016 APR2021 | 10.4271/J3016_202104 | ⚠️ 第三者ホストの DL 版（公式でない） |
| 8 | Parasuraman, Sheridan & Wickens 2000 | A model for types and levels of human interaction with automation（IEEE SMC-A 30(3):286–297） | 10.1109/3468.844354 | 全文 |
| 9 | Parasuraman, Mouloua & Molloy 1996 | Effects of adaptive task allocation on monitoring…（Human Factors 38(4):665–679） | 10.1518/001872096778827279 | abstract |
| 10 | Scerri, Pynadath & Tambe 2002 | Towards adjustable autonomy for the real world（JAIR 17:171–228） | 10.1613/jair.1037 | 全文 |
| 11 | Horvitz 1999 | **[P42]**（キー `proc:chi-1999-mixed-initiative`・DOI 付きの別行は無い → **新規登録しない**） | 10.1145/302979.303030 | 著者版全文 |
| 12 | Elish 2019 | （S1-a と共通） | 10.17351/ests2019.260 | — |
| 13 | Simkute et al. 2024 | （S1-a と共通） | 10.1080/10447318.2024.2405782 | abstract（S1-a は arXiv 全文） |

### claim（逐語）
- C1 Flemisch 2012 p.6: *"the authority of an actor can be defined by what the actor is allowed to do or not to do"* / *"(Control) Change authority: This is the authority to change the control authority to another control distribution giving more or less control to one of the actors."*
- C2 p.6–7: *"the authority to perceive, to act, to change the aim or to inform or warn the other actor"*
- C3 p.7: *"responsibility is assigned beforehand to motivate certain actions and evaluated afterwards"* / *"Ability should not be smaller than authority; authority should not be smaller than responsibility."*
- C4 p.11: *"An extreme would be an automation that does the control task completely, but where the human would keep all the responsibility."*
- C5 p.14: *"whether an actor looses or drops control 'silently' … or whether an actor explicitly requests another actor to take over control in time"*
- C6 p.15: *"The co-system has the authority to initiate a transition of control towards the driver only in the case of environment changes that cannot be handled by the co-system … and in case of detected driver drowsiness and distraction (due to responsibility issues)."* / *"the actual control as well as the responsibility is shifted to the new control distribution."*
- C7 p.17: *"leave the human with low abilities, low authority and insufficient control, but still with the full responsibility"*
- C8 Flemisch 2019 p.558: *"describe authority as a pre-requisite for control"*／ p.563 *"supported by nudges on all layers of cooperation, after initially authorizing the automation to execute these nudges"*
- C9 Pritchett 2014 p.54: *"authority is generally used to describe who is assigned the execution of a function in operational sense, responsibility identifies who will be held accountable in an organizational and legal sense for the outcome."*
- C10 p.59: *"Several problems can intrinsically arise when the responsibility and authority are not assigned to the same agent, including the additional monitoring actions the responsible agent must perform."*
- C11 Lu 2016 §3.1: *"whoever is in control is responsible for the safe execution of the driving task."*
- C12 §3.1: *"optional transitions are always initiated by the driver"* / *"automation-initiated transitions can only be mandatory."*
- C13 §3.2.3: *"'adaptive automation', whereby the automation hands over control to the human in an attempt to raise the driver's situation awareness"*
- C14 §4: *"This low-workload situation is sometimes followed by a high-workload safety-critical AIDC transition"*
- C15 J3016 3.22 p.18: *"receptive to a request to intervene … whether or not the ADS issues a request to intervene"*／ p.24 *"technical rather than legal"*
- C16 McCall 2019（abstract）: *"gaps between the current legal liability … and … the situational awareness requirements placed on driver"*
- C17 PSW 2000 p.287: *"the human retains authority for executing that alternative or choosing another one"*
- C18 p.294: *"the human operator is left with functions that the designer finds hard, expensive, or impossible to automate … defines the human operator's roles and responsibilities in terms of the automation"*
- C19 Parasuraman 1996（abstract）: *"temporary return of the automated engine status task to the human operator … as a possible countermeasure to monitoring inefficiency"*
- C20 Scerri 2002 p.171: *"transferring decision-making control to other entities (typically agents transferring control to human users)"* / *"it can choose to reduce its own autonomy"*
- C21 p.172: *"interrupting a user has high costs and the user may be unable to make and communicate a decision"*
- C22 p.180: *"it would wait indefinitely for the user to make the decision, even though this inaction caused miscoordination"*
- C23 Horvitz 1999 [P42] 原理 5 *"considering the costs of potentially bothering a user needlessly"*／ 原理 8 *"A preference for 'doing less' … minimize the need for costly undoing"*／ 原理 9 *"users may often wish to complete or refine an analysis provided by an agent"*
- C24 Elish p.40: *"responsibility for an action may be misattributed to a human actor who had limited control"*／ p.50 *"this 'handoff' scenario detracts from, rather than enhances, human performance"*
- C25 Simkute（abstract）: *"a shift in users' roles from production to evaluation"*
- C26 Eriksson & Stanton（abstract）: *"drivers occupied by a secondary task exhibit larger variance and slower responses to requests to resume control"*

### 見つからなかったもの（今回の範囲）
1. 「意味の認定・評価・報酬」を権限として扱い、システムがそれを返す記述
2. 負担項目としての「説明要求」（「解釈」も状況認識・監視以外の形では無し）
3. 権限と責任が一致したまま返還されても残務が移る型を独立に立てた記述
4. 価値判断に基づくシステムの**任意の**返還（Lu は射程外と明記 C12。近いのは C13 と C19）
- 未取得・未検索: Inagaki 2003 "Automation and the cost of authority"・Woods & Cook 2002・Miller & Parasuraman 2007・Pritchett らの対論文（10.1177/1555343413490944）

### サブエージェントの提案（解釈）
- GR-C1 は「既存の双方向性（C1, C19, C20）を**認識的な権限へ拡張する**」と書く
- GR-C7 と二重台帳は A2CR（C4, C7）と Pritchett の不一致指標（C9, C10）を**先行形式として明示的に引用**し、新規性を「一致した返還でも残務が移る型」と「認識的な負担項目」に限定する
- Flemisch C5（黙って手放すか、明示的に要請して引き受けを確認するか）は、草案の返権がどちらの型かを明示させる問いとして使える
- Horvitz 原理 8 / 9 の非対称（「控えめにする」を手戻りを減らす側でのみ書く）への反論として GR-C7 を位置づけうる
