# S2 生報告の退避（S2-a / S2-b）—— ⚠️ 未検証。3 票検証の入力

> 2026-09-19。サブエージェント（Opus）の報告。取得済み本文: `%TEMP%\s2b\`。DOI は Crossref 照合済み。

## S2-b（nudge 倫理・boost・digital nudging・contestability・METUX）

### 結論（サブエージェント）
- 既存の枠組みで**定式化済み**: **異議可能性**のみ
- **部分的**: 限定性・非放棄性・品質下限
- **今回の範囲で該当ゼロ**: **見逃し可能性・非再捕捉性** —— ⚠️ しかも主流は**逆向き**（nudge は無反応を「選択」として読む／contestability は利用者の訂正を学習データとして回収する）→ **差分として立てられる候補**

### 文献表
| 著者 年 | 題名 | DOI | 既登録 | 範囲 |
|---|---|---|---|---|
| Thaler & Sunstein 2003 | Libertarian Paternalism（AER 93(2):175–179） | 10.1257/000282803321947001 | 未（[P13] は 2008 書籍） | 全 5 頁（スキャン・目視） |
| Sunstein & Thaler 2003 | Libertarian Paternalism Is Not an Oxymoron（U Chicago Law Review 70(4):1159） | 10.2307/1600573 | 未 | 全文 |
| Hausman & Welch 2010 | To Nudge or Not to Nudge（J Political Philosophy 18(1):123–136） | 10.1111/j.1467-9760.2009.00351.x | 未 | ⚠️ **原本未取得・逐語は二次** |
| Hansen & Jespersen 2013 | Nudge and the Manipulation of Choice（EJRR 4(1):3–28） | 10.1017/S1867299X00002762 | 未 | 全文（CC BY） |
| Hertwig & Grüne-Yanoff 2017 | Nudging and Boosting（Perspectives on Psychological Science 12(6):973–986） | 10.1177/1745691617702496 | 未 | 全文 |
| Weinmann, Schneider & vom Brocke 2016 | Digital Nudging（BISE 58(6):433–436） | 10.1007/s12599-016-0453-1 | 未 | 全文 |
| Hirsch et al. 2017 | Designing Contestability（DIS 2017 pp.95–99） | 10.1145/3064663.3064703 | 未 | 全文（PMC 著者稿・節名で引用） |
| Vaccaro et al. 2019 | Contestability in Algorithmic Systems（CSCW Companion） | 10.1145/3311957.3359435 | 未 | ⚠️ 未取得（二次のみ） |
| Lyons, Velloso & Miller 2021 | Conceptualising Contestability（PACM HCI 5 CSCW1 Art.106） | 10.1145/3449180 | 未 | 全文（頁は arXiv v1） |
| Alfrink, Keller, Kortuem & Doorn 2023 | Contestable AI by Design（Minds and Machines 33(4):613–639） | 10.1007/s11023-022-09611-z | 未 | 全文（OA） |
| Peters, Calvo & Ryan 2018 | METUX | 10.3389/fpsyg.2018.00797 | **[V88]** | pp.4–5 |
| Susser, Roessler & Nissenbaum 2019 | Technology, autonomy, and manipulation（Internet Policy Review 8(2)） | 10.14763/2019.2.1410 | 未 | 全文（節で引用） |
| Elish 2019 | （S1 と共通） | 10.17351/ests2019.260 | 未 | — |
| 規範テキスト | 45 CFR 46.116(b)(8)・GDPR 前文 42 / 第 5 条 1(b) | — | 未 | 該当条文 |

### 補助原則ごとの判定
| 原則 | 最も近い既存（逐語） | 判定 |
|---|---|---|
| 限定性 | GDPR 5(1)(b) *"collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes"*／ Alfrink p.621 *"implement formal constraints on system behavior"*／ Hirsch *"highlight confidence scores to indicate the degree of certainty"* | **部分的**（目的・期間はデータ保護法。⚠️ 確信度で介入そのものを境界づける形は見つからず） |
| 異議可能性 | Hirsch *"We therefore must provide mechanisms for users to challenge model predictions."*／ Alfrink p.621 *"allow users to correct or override a system decision"*／ [P183] | **既に定式化**（既存は重大な「決定」への異議。GSE の推論・表現の訂正・拒否は軽い側） |
| 見逃し可能性 | 45 CFR 46.116(b)(8) *"refusal to participate will involve no penalty or loss of benefits"*／ GDPR 前文 42 *"unable to refuse or withdraw consent without detriment"*／ Peters p.5 *"do not in turn demand actions from users without their assent"* | **今回の範囲で見つからず**（近いのは「明示的な拒否」の不利益禁止。「無反応」は扱わない。⚠️ nudge は無反応を積極的に選択として読む） |
| 非放棄性 | Lyons p.16 *"contesting places a burden on the decision subject: the onus is on the individual to pursue an appeal"*／ Alfrink p.623 *"A risk of appeal procedures is that burdens are shifted to individual subjects."*／ Elish p.40 | **部分的**（「保持した権限・便益に対応する負担」の一般形は見つからず） |
| 非再捕捉性 | GDPR 5(1)(b)（目的外の後続処理の禁止）／ Hirsch（ゲーム化への懸念） | **今回の範囲で見つからず**。⚠️ 主流は逆向き: Hirsch *"CORE-MI relies on end-user input to train and improve its algorithms"*／ Alfrink p.621 *"such corrections may also function as a feedback loop for further system learning"*（★ review の X-06 / ADR-008 D1 と同じ形） |
| 品質下限 | Alfrink p.614 実践 3・4（開発時・運用後の品質保証）／ Hertwig Table 1 p.974 | **部分的**（非劣性の制約は S2-b の範囲外） |

### claim（逐語）
- 定義: Thaler & Sunstein 2003 p.175 paternalism *"a policy counts as "paternalistic" if it is selected with the goal of influencing the choices of affected parties in a way that will make those parties better off"*／ Sunstein & Thaler 2003 p.1161 *"people should be free to opt out of specified arrangements if they choose to do so"*／ Hansen & Jespersen p.15 nudge *"A nudge is any attempt at influencing behaviour in a predictable way without forbidding any previously available courses of actions or making alternatives appreciably more costly…"*・type 1/2（p.15）・透明な nudge（p.17）／ Hertwig p.977 *"we define boosts as interventions that target competences rather than immediate behavior"*／ Weinmann p.433 *"the use of user-interface design elements to guide people's behavior in digital choice environments"*／ Hirsch *"a new principle for designing systems that evaluate human behavior"*／ Alfrink p.613 *"responsive to human intervention throughout the system lifecycle"*／ Peters p.4 *"Autonomy should not be confused with merely doing things independently or being in control"*
- 反証（dismiss・opt-out できれば自律は脅かされない、は成り立たない）: C1 Hausman & Welch（二次）／ C2 Hertwig p.981 デフォルトは *"skirt conscious deliberation, meaning that they are perhaps not as easily reversible as thought and thus fail to meet the criterion of freedom of choice"*／ C3 Hansen & Jespersen p.18／ C4 Susser §1 *"When we are manipulated, by contrast, we are not constrained. Rather, we are directed, outside our conscious awareness…"*／ C5 Lyons p.16 *"contestability, recourse and redress qualify merely as opportunities…"*
- 反証の標的: C6 Sunstein & Thaler 2003 p.1167 注 *"respect for autonomy is adequately accommodated by the libertarian aspect of libertarian paternalism"*／ C7 Thaler & Sunstein 2003 p.177
- GSE に有利: C8 Peters p.5 *"Devices that offer options and choices over use, and do not in turn demand actions from users without their assent, enhance feelings of autonomy."*（assent が条件）／ C9 Hansen & Jespersen p.21（透明な type 2 の例 *"providing real-time feedback on energy-use"*・*"if the citizen does not agree with the ends or means, he may actively resist"*）／ C10 Hertwig p.977 boost *"they can choose to adopt it; if not, they can decline to engage with it… a boost's objective must be transparent"*（★ 招待は形が boost に近いが、能力を狙わない点が違う）
- ⚠️ GSE に不利な警告: **C11 Susser §2（抑うつが疑われる人に *"only at the specific times of day they were thought to be most afflicted"* 広告を出すのは manipulative）→ GSE の「Stuck 推定時に Nudge」と同じ構造。防御線は透明性だけ（C9）**／ C12 Susser §1 *"ideal vehicles for manipulation because they are already in a real sense hidden"*／ C13 Hertwig p.982 *"sometimes the nudge rests on the very assumption that individuals will do nothing"*／ C14 Thaler & Sunstein 2003 p.179／ C15 Weinmann p.433 *"there is no neutral way to present choices"*

### 見つからなかったもの
- 「無反応を不利益・評価低下の根拠にしない」を**適応系の設計原則として**述べた学術文献: **0 件**（近いのは研究倫理・GDPR の明示的拒否）
- 「返還後の行為を評価・報酬・最適化へ回収しない」: **0 件**（主流は逆）
- 「権限・便益に対応する負担」の一般形: 見つからず ／ 「確信度で介入を境界づける」: 見つからず
- 未取得: Sunstein 後続（2014 / 2015）・Hausman & Welch 原本・Vaccaro 2019–2021・[P13] 再読
- ⚠️ 読んだ一次はすべて概念・設計論文 → **効果の出典には使えない**

## S2-a（共和主義的非支配・関係的自律）

> 取得資料: `/tmp/s2a/`（サブエージェントの作業領域）。★ 全件 references.md 未登録。⚠️ Pettit 1997 / 2012 の**書籍本文は未読**（逐語は二次経由）。

### 文献表
| 著者 年 | 題名 | DOI / ISBN | 範囲 |
|---|---|---|---|
| Pettit 1997 | *Republicanism: A Theory of Freedom and Government* | ISBN 0198290837 ／ 1999 版 10.1093/0198296428.001.0001 | ⚠️ 二次経由（Nielsen & Landes 2016, 10.1093/phe/phv029） |
| Pettit 2012 | *On the People's Terms* | 10.1017/CBO9781139017428 | ⚠️ 二次経由（Schmidt 2017・Muldoon & Raekstad） |
| Pettit 2011 | The Instability of Freedom as Noninterference（Ethics 121(4)） | 10.1086/660694 | 一次全文 |
| Schmidt 2017 | The Power to Nudge（APSR 111(2)） | 10.1017/S0003055417000028 | 一次全文 |
| Hoeksema 2023 | Digital Domination and the Promise of Radical Republicanism（Philosophy & Technology） | 10.1007/s13347-023-00618-7 | 一次全文 |
| Muldoon & Raekstad 2023 | Algorithmic domination in the gig economy（European Journal of Political Theory） | 10.1177/14748851221082078 | 一次全文 |
| Maas 2022 | Machine learning and power relations / Neo-Republican critique of AI ethics（J Responsible Technology） | 10.1016/j.jrt.2021.100022 | abstract のみ |
| Mackenzie & Stoljar 2000 | *Relational Autonomy*（Introduction pp.3–31） | ISBN 9780195123333 | 序論の一次全文 |
| Mhlambi & Tiribelli 2023 | Decolonizing AI Ethics（Topoi） | 10.1007/s11245-022-09874-2 | 一次全文 |
| Bennett, Metatla, Roudaut & Mekler 2023 | How does HCI Understand Human Agency and Autonomy?（CHI 2023） | 10.1145/3544548.3580651 | arXiv 全文 |
| Aelterman et al. 2019 | Toward an integrative and fine-grained insight in motivating and demotivating teaching styles: the merits of a circumplex approach（J Educational Psychology） | 10.1037/edu0000293 | abstract のみ |
| Quill & Brody 1996 | Physician Recommendations and Patient Autonomy: Finding a Balance between Physician Power and Patient Choice（Annals of Internal Medicine 125(9)） | 10.7326/0003-4819-125-9-199611010-00010 | abstract のみ |

### 対応（逐語）
- 支配（Pettit 1997 p.52・二次）: *"someone has dominating power over another […] to the extent that (i) they have the capacity to interfere; (ii) on an arbitrary basis; (iii) in certain choices that the other is in a position to make"* → ★ 問題は**行為でなく能力**。草案の「撤退」は行為の抑制なので定義の外
- 統制されない介入（Pettit 2012 p.50・Schmidt pp.406–407 経由）: *"A, will be dominated in a certain choice by another agent or agency, B, to the extent that B has a power of interfering in the choice that is not itself controlled by A"* → ★ **招待が非支配と言えるかは、本人がその出し方を統制できるかで決まる**
- 善意は免罪しない（Pettit 2011 p.706–707）: *"When I grant you the favor of choosing as you wish, it remains the case that should my will change, then I will interfere"*／ *"It may just consist in my having the power to interfere more or less without cost, should my will incline that way"*
- 介入の範囲（Pettit 2011 p.699）: *"undermining the informed, deliberative character of the choice by deception or manipulation"*／ 選択肢に罰を付けることは *"however slight it may be"* でも介入（Pettit 2012 pp.51–2・Muldoon p.590 経由）→ ★ **「拒否・無視・別解釈・継続を等しく可能に」は「どの選択肢にも罰を付けない」要件として Pettit に接地できる（唯一しっかり依拠できる点）**
- 微小支配（O'Shea 2018:136・Muldoon p.603 経由）: 個々には軽すぎて争えない決定が蓄積すると大きな影響 → 「招待は軽いから支配でない」とは言えない
- 構成的支配（Thompson 2018・Hoeksema p.2 経由）: 特定の選択でなく *"cognitive as well as evaluative dimensions"* に向かう影響 → ★ **草案の「意味認定」に当たる**
- 関係的自律（M&S p.4）: *"an umbrella term […] premised on a shared conviction […] that persons are socially embedded"*／ 構成的 vs 因果的に関係的（p.22）
- 自律 ≠ 独立（M&S p.6）: 「自律的な男」の理想は *"valuing substantive independence over all other values"* → ★ **「放置的返還」を退ける根拠は共和主義ではなくここ**

### claim
- 行使されなくても能力だけで不自由（Schmidt p.407 *"the mere uncontrolled power to interfere suffices to render someone unfree, even if such power is never exercised"*）
- 一度の同意は統制ではない（Schmidt p.410 *"exercising control over a power to interfere is different from giving consent…"*／ *"not just transparency before a nudge is enacted but also afterwards such that continued control is feasible"*）
- 本人が依頼したナッジは支配ではない（Schmidt p.411・p.412 *"'choices over choices' will give individuals more direct control"*）
- 関係的自律は非支配を含み、意志が一致しても懸念は残る（Schmidt p.408）
- 退出の保障や同意だけでは足りない（Hoeksema p.1）
- アルゴリズムによる支配の定義（Muldoon & Raekstad p.588 *"algorithmic domination occurs when an individual is subjected to an uncontrolled power, the operations of which are determined by an algorithm"*）
- AI 倫理は害に偏り権力を見落とす（Maas 2022 abstract）
- HCI は自律を独立と同一視しがち（Bennett 2023 §4.4.4: 独立重視 n=50 / 相互依存重視 n=54）
- **反証: 父権と放置の両方を避ける構図は SDT に既にある**（Aelterman 2019 abstract *"autonomy support, structure, control, and chaos […] participative and attuning, guiding and clarifying, demanding and domineering, and abandoning and awaiting"*）
- **反証: 医療倫理にも 1996 年から同じ構図**（Quill & Brody 1996: independent choice model は *"confuses the concepts of independence and autonomy"*・対案 *"enhanced autonomy"*）

### 3 つの問いへの答え（サブエージェント）
- (i) 能力そのものが問題になる → **「招待を出し、その後に撤退する」はそれだけでは非支配の基準を満たさない**。満たす条件: 招待を出す力を本人が継続的に統制できる／時期・有無・型を本人が選べる（choices over choices）／事前だけでなく事後も透明
- (ii) 誤読の危険: ① 非支配は放置を問題にしない → **「放置的返還を避ける」は非支配から導けない** ② 支配する主体は設計者・研究者になる（研究者と被験者の関係まで射程に入る） ③ 非支配の処方は政治的な共有統制 ④ 罪悪感・負担の集中は非支配の語彙で扱えない
- (iii) 関係的自律から借りられる: 自律 ≠ 独立・系を因果的に関係的な存在として扱う・自己信頼の損傷 → 罪悪感への接続
- **言い換えでない可能性が残るのは 2 点**: 選択肢間の対称性要件（Pettit の罰を付けられた選択肢で接地可）／ **意味認定と応答要求を終了させること（先例見つからず）**

### 見つからなかったもの
- Pettit 1997 / 2012 の本文 ／ 招待・申し出（offer）が介入に当たるかの Pettit 自身の記述 ／ 非支配を**個人規模の適応的介入系**に当てはめた研究（見つかったのはプラットフォーム・国家・職場規模のみ）／ 放置を共和主義の悪として扱う議論 ／ 関係的自律を明示的に設計原理にした HCI 論文（Bennett のレビューで "relational" 0 件）／ HCI の contestability 研究（Alfrink 2023）は Pettit・republican を 0 件引用
