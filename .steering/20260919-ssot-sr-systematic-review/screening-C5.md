# ふるい分けの記録 —— C5

> 候補の定義（protocol.md §1）: **見逃し可能性: 介入・通知・招待に応答しないことを、選択・同意・不利益・評価低下の根拠として読まないこと**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 485 |
| 段 1 で採った | 27 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 23 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 7 |
| 段 2 の判定（メインの訂正の後） | 該当 2 ／ 部分 1 ／ 非該当 4 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 19 |

## 結論

★ **既出**（該当: C5-0452 [P402]・C5-0227 [P403]）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C5-0227 | 該当 | 本文 | Whether due to implied endorsement, cognitive biases, or, to a lesser extent, effort, all three causes of default effects suggest that defaults can be “hidden persuaders” that are inconsistent with consumers exercising c… | p.162, 「Do Defaults Violate Consumer Autonomy?」節 | (i) デフォルト（選択画面での非切替＝無応答）を対象とし、(ii) それが implied endorsement／cognitive biases／effort のいずれに由来するにせよ genuine な選択・同意の根拠にならない（consumer sovereignty test に失敗する）と論じ、非切替を不利益の根拠にしないための開示義務・規制という具体的設計提案まで操作化している。両… |  | ★ メインが本文で照合 |
| C5-0452 | 該当 | 本文 | Examples include failing to claim benefits within prescribed deadlines, not completing verification procedures, not responding to notifications, or not maintaining continuous usage of services. | p.3, 第2節 | (i) 通知・催告・手続きプロンプトへの無応答（not responding to notifications 等）を対象とし、(ii) それを consent／forfeiture（同意・権利喪失という不利益）の根拠として読まないことを設計原理「Silence ≠ Consent」として明示的に提案・操作化している。両要素とも充足。 |  | ★ メインが本文で照合 |
| C5-0403 | 部分 | 本文 | When Inertia (1) drives choices and individuals recognize the choices and understand that they can reject the default option, then autonomy is maintained (Smith et al., 2013). | p.362, 「Ethical Implications」節 | (i) デフォルト維持（＝選択画面への無応答）を対象としている点は該当。(ii) しかし『無応答＝同意として読まない』ことを著者自身の設計原則として明確に主張・操作化してはおらず、『認識していれば自律性は保たれる』という条件付き記述や、『無応答者が実は選好と一致するかは未確認』という先行研究紹介にとどまる（先行研究レビュー論文であり評価は多くSmith et al. 2013等の引用に依拠）。一部… |  | メインが抄録・取り出したテキストと機械照合 |
| C5-0018 | 非該当 | 本文 |  |  | 通知への応答時間・重要度評価を大規模実測する研究であり、通知が無視される頻度や反応時間を測定してはいるが、『無応答を同意・不利益・評価低下の根拠として読まない』ことを述べる・提案する箇所は無い（要素(ii)不成立）。開発者向け推奨も『重要な通知だけ出せ』という設計指針で、無応答の解釈規範には踏み込まない。 |  |  |
| C5-0454 | 非該当 | 本文 |  |  | 対象はソフトウェアエージェント間の対話プロトコルにおける『沈黙の一手』であり、人に対する介入・通知・招待への無応答ではない（要素(i)不成立）。かつ『沈黙は同意』と『沈黙は不承諾』の2つの既存の規約を対比的に記述するのみで、無応答を同意等の根拠として読まないことを著者自身が主張・提案してはいない（要素(ii)不成立）。 |  |  |
| C5-0472 | 非該当 | 本文 |  |  | デジタル市場の同意画面・ダークパターン・『consent fatigue（同意疲れ）』を扱うが、記述されているのは疲弊から『Accept』を能動的にクリックしてしまう挙動であり、無応答・沈黙そのものではない（要素(i)不成立）。無応答を同意等の根拠として読まないことを述べる・提案する記述も見当たらない（要素(ii)不成立）。 |  |  |
| C5-0477 | 非該当 | 本文 |  |  | AI governance におけるヒューマンオーバーサイト（guardrail）が action path を実際に変更できるか（binding point 前に介入余地を保つか）を論じるが、対象は『レビュアーが能動的に承認/否認する』プロセスの実効性であり、人が介入・通知・招待に無応答であることそのものを同意・不利益・評価低下の根拠として読むか否かは論じていない（要素(i)(ii)とも不成立）… |  |  |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C5-0018 | 2014 | Large-scale assessment of mobile notifications | 10.1145/2556288.2557189 | モバイル通知への応答・無視をユーザー視点で大規模実測した通知システム研究 | 照合 |
| C5-0040 | 2012 | Understanding Why Clinicians Answer or Ignore Clinical Decision Support Prompts | 10.4338/aci-2012-04-ra-0013 | 臨床意思決定支援システムのプロンプトへの応答/無視の要因を実測したCDSS研究 | 未実施（逸脱 2） |
| C5-0089 | 2014 | Sensor-Based Identification of Opportune Moments for Triggering Notifications | 10.1109/mprv.2014.15 | スマートフォンセンサーで通知応答/無視の状況を予測しタイミング最適化を図る通知システム研究 | 未実施（逸脱 2） |
| C5-0093 | 2007 | Considerate home notification systems: a field study of acceptability of notifications in the home | 10.1007/s00779-007-0176-x | ホーム通知システムの受容性フィールド調査(思いやりのある通知設計)で対話的自動化系に該当 | 未実施（逸脱 2） |
| C5-0102 | 2004 | The effects of affective interventions in human–computer interaction | 10.1016/j.intcom.2003.12.001 | HCI実験でシステムがユーザーを無視する(介入なし)条件と感情的介入条件を比較実測 | 未実施（逸脱 2） |
| C5-0105 | 2017 | Clinical reminder alert fatigue in healthcare: a systematic literature review protocol using qualitative evide… | 10.1186/s13643-017-0627-z | CDSSの臨床リマインダーアラート疲労(無視される現象)を扱う系統的レビュープロトコル | 未実施（逸脱 2） |
| C5-0219 | 2015 | Nudges, Agency, and Abstraction: A Reply to Critics | 10.1007/s13164-015-0266-z | 抄録なし。題名『ナッジ・エージェンシー・抽象化：批判への応答』は非応答・行為主体性の解釈を扱う可能性があり、迷ったため採る。 | 未実施（逸脱 2） |
| C5-0227 | 2013 | Choice without Awareness: Ethical and Policy Implications of Defaults | 10.1509/jppm.10.114 | デフォルト効果の一因として『黙示の是認（implied endorsement）』、すなわち非応答をデフォルト選択への同意として読む解釈を明示的に検討している。 | 照合 |
| C5-0293 | 2016 | An Exploratory Study of Driver Response to Reduced System Confidence Notifications in Automated Driving | 10.1109/tiv.2017.2691158 | 自動運転システムの信頼度低下通知に対するドライバーの応答を検証する自動化・通知系の研究であり、対象条件を満たすため段2判断に回す。 | 未実施（逸脱 2） |
| C5-0310 | 2020 | Nudge for Deliberativeness: How Interface Features Influence Online Discourse | 10.1145/3313831.3376646 | オンライン議論インターフェースの返信選択プロンプトが評価への恐れから応答意欲を低下させることを示す対話的系の研究であり、通知への非応答と評価の関係を扱うため該当。 | 未実施（逸脱 2） |
| C5-0346 | 2013 | Nudging in Context: Response to Open Peer Commentaries on “Nudging and Informed Consent” | 10.1080/15265161.2013.839774 | ナッジとインフォームド・コンセントの関係を論じる論文で候補領域に直接該当 | 未実施（逸脱 2） |
| C5-0352 | 2016 | Nudges That Fail | 10.2139/ssrn.2809658 | ナッジの失敗を論じる表題で候補領域に近く抄録なし・迷ったら採る | 未実施（逸脱 2） |
| C5-0360 | 2019 | E-Nudging Justice: The Role of Digital Choice Architecture in Online Courts |  | オンライン裁判所のデジタル選択アーキテクチャを論じ候補領域に近接 | 未実施（逸脱 2） |
| C5-0395 | 2017 | Why Nudges Coerce: Experimental Evidence on the Architecture of Regulation | 10.1007/s11948-017-9944-9 | ナッジの強制性を論じる表題で候補領域に近く抄録なし・迷ったら採る | 未実施（逸脱 2） |
| C5-0403 | 2021 | Options to design more ethical and still successful default nudges: a review and recommendations | 10.1017/bpp.2021.33 | デフォルト・ナッジの倫理と能動選択という代替設計を論じるレビュー | 照合 |
| C5-0405 | 2022 | Empowering Consumers to Make Environmentally Sustainable Online Shopping Decisions: A Digital Nudging Approach | 10.24251/hicss.2022.574 | デフォルト/能動選択/セルフナッジを比較しデジタル・ナッジの倫理を評価する実験 | 未実施（逸脱 2） |
| C5-0418 | 2025 | Defaults change choices, not minds: Practical and ethical benefits of brief educational boosts for water recyc… | 10.1017/jdm.2025.10 | デフォルトナッジと教育的ブーストを比較しデフォルトの倫理的リスクを論じる実験 | 未実施（逸脱 2） |
| C5-0421 | 2023 | When Do Informational Interventions Work? Experimental Evidence From New York City High School Choice | 10.3102/01623737231203293 | 学校選択制度で無応答時に割り当てられるデフォルト校を情報提供介入で回避させる研究 | 未実施（逸脱 2） |
| C5-0433 | 2019 | Clinicians’ Perceptions of Behavioral Economic Strategies to Increase the Use of Lung-Protective Ventilation | 10.1513/annalsats.201905-410oc | 肺保護換気のデフォルト設定と能動選択等5戦略への臨床医の認識調査 | 未実施（逸脱 2） |
| C5-0444 | 2023 | Should We Trust Consumers or Bureaucrats with Health Insurance Choices? | 10.1007/978-3-031-32890-9_10 | 消費者かお役所かという医療保険選択の決定権論、パターナリズム論争に近接し迷ったら採る(抄録なし・題名判定) | 未実施（逸脱 2） |
| C5-0452 | 2026 | Beyond Tacit Consent: Designing Structural Fairness into Systems that Silence Citizens | 10.5281/zenodo.18737547 | 市民の沈黙を黙示の同意とみなす制度設計を批判し沈黙=同意の拒絶を設計原理として提案 | 照合 |
| C5-0454 | 2002 | Communication protocols for logic-based agents |  | 論理ベースエージェントの対話プロトコルで『沈黙は同意』の解釈可否を明示的に論じる | 照合 |
| C5-0455 | 2026 | Beyond Tacit Consent: Designing Structural Fairness into Systems that Silence Citizens | 10.5281/zenodo.18737546 | 0452と同一論文、沈黙=同意の拒絶を設計原理として提案 | 照合 |
| C5-0457 | 2026 | An AI Convenor for Multi-Domain Co-Creation: A Governance-Constrained Decision-Rights and Escalation Framework | 10.23726/cij.2026.1824 | AI主催者の統治枠組みでAI提案/人間決定へのデフォルト付与とエスカレーションを論じ候補領域に近接、迷ったら採る | 未実施（逸脱 2） |
| C5-0463 | 2017 | Editors’ note | 10.1353/bsp.2017.0009 | 行動科学政策誌の巻頭言で選択アーキテクチャとデフォルトの概念を紹介、迷ったら採る | 未実施（逸脱 2） |
| C5-0472 | 2025 | Smokescreens of digital markets—choice manipulation and the illusion of consent | 10.1093/jeclap/lpaf050 | デジタル市場の同意画面設計と『同意の幻影』を論じ、系(選択画面UI)と候補領域に直接該当 | 照合 |
| C5-0477 | 2026 | Guardrail Laundering and Pre-Action Capture: A Threshold Account of Ceremonial Human Oversight | 10.5281/zenodo.20820458 | AIの人間監督における安全策が実質的な応答機会を保全するかを論じ、候補に近接する論点 | 照合 |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

- C5-0165（2025）When Software Becomes Medicine: Ignoring It May Soon Be Malpractice —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】適応的なデジタル治療（PDT）を医師が使わない（無視する）ことを医療過誤とみなす方向性を論じ、系への非応答を不利益の根拠として読む逆向きの主張に該当。
- C5-0173（2019）A Nudge Toward Universal Aspirin for Preeclampsia Prevention —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】臨床ガイドラインをopt-inからopt-outへ変更し、非応答（拒否しないこと）を介入（アスピリン予防投与）への同意として扱う設計を提案しており、候補の逆向きの主…
- C5-0220（2012）Nudge, Nudge or Shove, Shove—The Right Way for Nudges to Increase the Supply of Donated Cadaver Organs —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】臓器提供のデフォルト（家族拒否権付き）を提案し、非応答（拒否しないこと）を同意として読む設計であり、候補の逆向きの主張に該当。
- C5-0241（2022）Nudging App Adoption: Choice Architecture Facilitates Consumer Uptake of Mobile Apps —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】アプリ導入時に『有効化がデフォルトの応答であるかのように』文言を設計し、非応答を採用への同意として扱う効果を示しており、候補の逆向きの主張に該当。
- C5-0368（2017）Student Loan Nudges: Experimental Evidence on Borrowing and Educational Attainment —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】デフォルトのローン提示額が借入行動に与える効果を測定し候補の裏面(無応答=同意)を操作化
- C5-0401（2023）Dark defaults: How choice architecture steers political campaign donations —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】非応答のままのデフォルト(チェックを外さない)を継続寄付への同意とみなす実例を計測、候補と逆向きの主流
- C5-0402（2019）Nudging In MicroBiology Laboratory Evaluation (NIMBLE): A scoping review —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】微生物検査報告のデフォルト表示変更というナッジ介入の系統的スコーピングレビュー
- C5-0404（2017）Progress Evaluation for the Restaurant Industry Assessed by a Voluntary Marketing-Mix and Choice-Architecture … —— 【メイン訂正: 逆向きの主張しかない → protocol §4 段 1 により採らない（逆向きの主流として記録）】レストラン業界のデフォルト健康選択等の選択アーキテクチャ戦略の進捗評価
