# ふるい分けの記録 —— C7

> 候補の定義（protocol.md §1）: **系による意味の認定と応答の要求を終了させることを、設計の規範的な要件にすること**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 617 |
| 段 1 で採った | 6 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 6 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 7 |
| 段 2 の判定（メインの訂正の後） | 該当 0 ／ 部分 3 ／ 非該当 4 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 0 |

## 結論

★ **部分的に既出** —— ⚠️ **本プロトコル（検索式・検索元・期間・採否基準）の範囲で該当 0 件**（⚠️ 網が粗い —— RP §4）。部分: C7-0134 [P406]・C7-0209 [P407]・手動の補完 `JACTRT`・C7-0608（d-3 の cross-review 2 巡目で拾い直した・抄録のみ）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C7-0134 | 部分 | 本文 | Work emails stopped being delivered shortly after the working day and resumed before the next shift | §6, p.12 | 要素(b)『系が人へ向ける応答の要求を終了させることを設計の規範的な要件にする』は、Volkswagenのメール配信停止事例で明確に述べられている(配信という技術的な仕組みが『a visible stopping point』を作り、著者は『communication systems can be designed to protect personal time』と規範的に主張)。一方、要素(a… |  | メインが抄録・取り出したテキストと機械照合 |
| C7-0209 | 部分 | 抄録のみ | a proactive auto-response messaging agent that can reduce perceived obligations and social pressure to respond quickly to incoming messages by providing unavailability-related context | abstract | 抄録で、系(auto-response messaging agent)が『応答すべきという知覚された義務・社会的圧力を軽減する』ことを明示的な設計目的として掲げており、要素(b)『系が人へ向ける応答の要求を(軽減/終了)させることを設計目的にする』に近い。ただし動詞は『reduce(軽減する)』であり『終了させる(end/terminate)』ではなく、規範的要件として明記されているかは本文未確… |  | メインが抄録・取り出したテキストと機械照合 |
| C7-0608 | 部分 | 抄録のみ | remaining strictly within non-inference, non-diagnostic constraints. By focusing on cognition extraction rather than interpretation | Abstract | 系が意味の認定（推論・診断）をしない制約を設計の要件にする。⚠️ 恒常的な範囲の制限で「終了させる」ではない・応答の要求の要素は無い | 段 1 で除外 → d-3 の cross-review 2 巡目で拾い直した。メインが抄録で判定 | メインが抄録で照合 |
| C7-0091 | 非該当 | 抄録のみ |  |  | 本文非公開。抄録は『前提研究[1]のresponse obligation estimation(ROE)手法をHALOGENでリアルタイム評価する』という報告であり、ROEは系(対話ロボット)が入力音声に反応すべきかを系自身が推定するタスク。C7が求める『系が人へ向ける応答の要求の終了』『系による意味の認定の終了』のいずれの要素も無く、向きが逆(系が自らの応答要否を判定し続ける枠組み)。 |  |  |
| C7-0104 | 非該当 | 抄録のみ |  |  | 抄録が『Response obligation is whether a spoken dialogue system should react to an input sound』とROEを明確に定義しており、これは系自身が『自分は応答すべきか』を推定するタスクであって、系が人へ向ける応答の要求を終了させる話ではない。応答しないことを『the system's neglect of its us… |  |  |
| C7-0477 | 非該当 | 抄録のみ |  |  | 本文は認証プロトコル(SSO/ローミング)の技術論文であり、対話的・適応的な系による意味の認定や、系が人へ向ける応答要求を終了させるという論点は抄録に存在しない。『does not require any end-user interactions while roaming』はローミング中に認証セッションを維持するための技術要件であり、C7が扱う意味認定・応答義務の終了とは対象ドメインが異なる。 |  |  |
| C7-0573 | 非該当 | 本文 |  |  | 本文は、会話AI『Sage』が一度形成した物語解釈(narrative interpretation)を『State Stickiness』として保持し続け、ユーザーがそれを改訂しにくくなる問題を指摘し、『Narrative Plasticity』(ユーザーが系の解釈を改訂できる能力)の保存を設計上の要件として論じる。これは系の意味認定の権威を『ユーザーが改訂可能な状態に保つ』論であり、系がその意… |  |  |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C7-0091 | 2017 | Online Evaluation of Response Obligation Estimation on the HALOGEN Multimodal Interaction Framework | 10.1145/3029798.3038326 | 対話・対人ロボットシステムのResponse Obligation Estimation(応答義務推定)を明示的に操作化しており、系が入力への応答要否を判定・終了させる候補に合致 | 照合 |
| C7-0104 | 2019 | Response Obligation Estimation That Considers Users' Repetitive Utterances using Knowledge-Guided Random Fores… | 10.1109/humanoids43949.2019.9035079 | 対話・対人ロボットシステムのResponse Obligation Estimation(応答義務推定)を明示的に操作化しており、系が入力への応答要否を判定・終了させる候補に合致 | 照合 |
| C7-0134 | 2026 | Boundary Blurring and Recovery Difficulty in After-Hours Work Messaging | 10.53104/curr.res.psychol.sci.2026.06001 | 勤務時間外のメール配信制限など、系が応答期待を終了させる設計を具体例として論じており候補に該当しうる(迷ったら採る) | 照合 |
| C7-0209 | 2023 | Co-Designing with Users the Explanations for a Proactive Auto-Response Messaging Agent | 10.1145/3604248 | 受信メッセージへの即時応答という社会的圧力・義務感を、不在情報の提示で系が軽減する自動応答エージェントを参加型デザインで検討しており、候補C7を明示的に扱う | 照合 |
| C7-0477 | 2005 | Authentication across heterogeneous networks | 10.1002/bltj.20093 | SSO認証がローミング中に end-user interactions を一切要求しない設計を明示しており、系が応答要求を終了/不要化する論点に触れるため段2で精査 | 照合 |
| C7-0573 | 2026 | Narrative Plasticity and State Stickiness: Designing Hybrid AI Systems for High-Stakes Communication | 10.1145/3800645.3813073 | 対話AIが一度形成した意味解釈(narrative interpretation)の持続・改訂困難性(State Stickiness)と、その解釈状態を統治する設計上の考慮を論じており、系による意味認定の終了/改訂という論点に直接関わるため段2で精査 | 照合 |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

- C7-0108（2026）The Individual Rights Response Obligation: Why the Right to Contestation in Enterprise AI Governance Requires … —— AI意思決定への異議申立てに対する人間審査の応答義務を論じており、系が応答要求を終了させる候補とは逆に応答義務の維持・強化を主張する
- C7-0109（2026）The Individual Rights Response Obligation: Why the Right to Contestation in Enterprise AI Governance Requires … —— AI意思決定への異議申立てに対する人間審査の応答義務を論じており、系が応答要求を終了させる候補とは逆に応答義務の維持・強化を主張する
- C7-0110（2026）The Individual Rights Response Obligation: Why the Right to Contestation in Enterprise AI Governance Requires … —— AI意思決定への異議申立てに対する人間審査の応答義務を論じており、系が応答要求を終了させる候補とは逆に応答義務の維持・強化を主張する
- C7-0165（2026）Cognitive Bioprediction and Moral Responsibility: Foreseeability, Control and the Ethics of Anticipated Cognit… —— 予測技術による認知機能低下警告への応答義務を課す方向の議論で、候補(応答要求の終了)とは逆向き
- C7-0450（2019）Effective design of in-home displays —— 家庭用エネルギーディスプレイの設計レビューであり、『end-user interaction and responseが最大化されるよう』推奨しており、候補C7(応答要求の終了)とは逆方向(応答の最大化)の主張
- C7-0563（2021）Synergistic Social Technology: Designing Systems with ‘Needs’ that Encourage and Support Social Interaction —— 系自身が相互作用への「必要」を持つよう設計するSynergistic Social Technology論で、応答を求め続ける逆方向の設計思想の例
