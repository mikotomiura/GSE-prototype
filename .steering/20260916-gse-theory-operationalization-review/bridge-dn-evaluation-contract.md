# BRIDGE-DN 評価契約 v0.1

> Status: pre-SSOT conceptual evaluation draft / 2026-09-17
>
> `BRIDGE-DN` は第四の主理論でも Digital Nature 全体への反論でもない。本書は、計算と物理の循環が続く環境内部で個別システムの意味推論・達成認定・応答要求を局所的に終端できる、という狭い接続命題だけを評価する。

## 1. 命題と理論的親

**命題**: 計算と物理が循環する計算機自然の内部でも、個別システムの意味推論、達成認定、応答要求には、局所的かつ監査可能な終端を設計できる。

- 内部側の理論的親: `TH-GR`、`SUB-SWM`、Semantic Stop Boundary
- 外部接続先: Digital Nature、ubiquitous computing、information / artifact / hybrid ecology
- 関連命題: `GR-C2/C4/C5`、`GR-H3/H7/H8`
- 主要方法: comparative argument、反例表、処理境界監査への参照
- 利用者評価は BRIDGE-DN 自体の成立でなく、終端の知覚可能性に限り CORE-ART / CORE-CS を参照する。

## 2. 含む範囲と含まない範囲

### 含む

- 環境全体では計算・通信・物理相互作用が継続しうること
- その内部の GSE サブシステムが特定の inference / certification / response-duty edge を終えられること
- 局所性、停止対象、bounded continuation、非再捕捉、再接続条件の監査
- Digital Nature / UbiComp / ecology から借りる環境記述と、GSE が追加する境界条件の分離
- 外部 service、OS、隣接 artifact が同じ行為を回収する反例
- 既存理論が同じ結合を十分に記述している場合の統合・縮小・棄却

### 含まない

- 「計算の外部」「非計算」「自然への復帰」「デジタルからの脱出」
- 画面外へ移ったこと、歩行、休憩、回復、身体回帰の認定
- 環境全体、OS、他サービス、他組織の計算やデータ利用を GSE が停止できるという主張
- calm、invisible、peripheral、ambient であることを Semantic Stop と同一視すること
- BRIDGE-DN 独自のユーザー尺度、介入効果、規範的優位
- Digital Nature の存在論全体を採用または否定すること

## 3. 観測単位、対象、証拠階梯

| 項目 | 契約 |
|---|---|
| 概念単位 | `external claim x GSE claim x borrowed / not-borrowed scope` |
| 境界単位 | `stop episode x GSE subsystem x adjacent system / consumer` |
| 主要対象 | GSE が所有・監査できる処理境界 |
| `EH0` | 一次資料比較、差分表、反例、主張禁止線 |
| `EH1` | CORE-CS の stop closure / non-recapture / bounded continuation 監査結果を参照 |
| `EH3-4` | CORE-ART / CORE-CS の intentional termination / failure 知覚を補助参照 |
| 非対象 | BRIDGE-DN 単独の効果試験、独自尺度、フィールドでの一般化 |

## 4. 借用範囲マトリクス

| 系譜 | 借りる主張 | 借りない主張 | GSE が追加検査するもの |
|---|---|---|---|
| Digital Nature | 計算過程と物理現象が同じ環境内で循環しうるという環境前提 | GSE が計算の外部や自然への復帰を作ること | 循環内部の局所的 non-certification / non-recapture |
| Ubiquitous computing | 計算が環境へ埋め込まれ、継続的 interaction と interruption / resumption を生むこと | invisible / calm なら応答義務が消えること | 消える表示でなく停止対象を監査できること |
| Context-aware computing | context は完全に事前表象できず、相互行為の中で成立するという警告 | 追加の自己説明や応答を利用者へ無限に求めること | 推論射程を局所停止で閉じること |
| Information ecology | 技術を人、実践、価値、ローカル環境の関係で捉えること | 生態全体を一システムが制御できること | 自システムの境界と他系の残存処理を明記すること |
| Artifact / hybrid ecology | artifact は相互影響する集合内で理解すべきこと、physical / digital の seam が残ること | 隣接 artifact の非再捕捉まで自動保証されること | 外部 consumer を反例として列挙し、主張を局所化すること |
| Calm technology | offer but not demand、中心 / 周辺注意の設計語彙 | calmness が no residual response duty を保証すること | 知覚上の静けさと処理上の停止を別 gate にすること |

## 5. 一次資料と引用射程

検索日: 2026-09-17。検索先は DOI resolver、J-STAGE、Ochiai Lab、Scientific American、ACM、Springer、First Monday、INFORMS と一次公開元。検索式は `Digital Nature Yoichi Ochiai DOI`、`ubiquitous computing calm technology DOI`、`information ecology DOI`、`artifact ecology HCI DOI`、`hybrid ecologies DOI` を中心とした。

| 一次資料 | 種類 | 借りられる範囲 | 借りられない範囲 / 外挿限界 |
|---|---|---|---|
| Ochiai, *Digital Nature* (2018), ISBN 978-4-905325-09-3; [Ochiai Lab](https://www.ochyai.dev/philosophy) | 著書 / 概念ステートメント | コンピュータを単なる道具でなく物理・デジタルが循環する環境として捉える出発点 | Semantic Stop、非再捕捉、利用者負担の実証根拠ではない |
| Ochiai (2026), [doi:10.24669/trajectory.3.0_5](https://doi.org/10.24669/trajectory.3.0_5) | Digital Nature 関連エッセイ / 作品文脈 | 物理・デジタル融合の作品文脈 | GSE が Digital Nature 全体へ反論する根拠ではない |
| Weiser (1991), [doi:10.1038/scientificamerican0991-94](https://doi.org/10.1038/scientificamerican0991-94) | UbiComp vision | 計算が環境へ埋め込まれる系譜 | invisibility と推論停止は同じでない |
| Weiser & Brown (1996), [primary text](https://calmtech.com/papers/coming-age-calm-technology) | design manifesto | center / periphery、offer but not demand | calmness から応答義務終了を推論しない |
| Abowd & Mynatt (2000), [doi:10.1145/344949.344988](https://doi.org/10.1145/344949.344988) | UbiComp research agenda | continuous interaction、interruption / resumption、評価困難 | capture / access の拡大を GSE の正当化にしない |
| Dourish (2004), [doi:10.1007/s00779-003-0253-8](https://doi.org/10.1007/s00779-003-0253-8) | context-aware computing critique | context の相互行為性と表象限界 | user への継続的説明要求を正当化しない |
| Nardi & O'Day (1999), [doi:10.5210/fm.v4i5.668](https://doi.org/10.5210/fm.v4i5.668) | information ecology | 人・実践・価値・ローカル環境の生態 | 生態全体の制御可能性を主張しない |
| Star & Ruhleder (1996), [doi:10.1287/isre.7.1.111](https://doi.org/10.1287/isre.7.1.111) | infrastructure ethnography | 局所実践と大規模変化の接続、透明性の条件性 | 透明化を成功条件にしない |
| Bødker & Klokmose (2012), [doi:10.1145/2399016.2399085](https://doi.org/10.1145/2399016.2399085) | artifact ecology | 単一 artifact を相互影響する ecology 内で読む | 隣接 artifact の処理を GSE が保証できるとはしない |
| Crabtree & Rodden (2008), [doi:10.1007/s00779-007-0142-7](https://doi.org/10.1007/s00779-007-0142-7) | hybrid ecology / ethnographic cases | physical / digital ecology の fragmented / seamful interaction | 協調事例の効果を個人作業へ外挿しない |

この表は文献台帳の代替ではない。`docs/references.md` は本タスクでは変更せず、正式採用時に重複・書誌・一次全文を再監査する。

## 6. Comparative argument

### 6.1 接続が成立する最小形

1. Digital Nature / UbiComp 側から、環境全体では計算・通信・物理相互作用が継続するという前提を借りる。
2. GSE はその環境から退出した、非計算になった、自然へ戻ったとは言わない。
3. GSE が所有する処理 graph のうち、特定の意味推論、達成認定、報酬、応答要求 edge を `T_stop` として局所的に閉じる。
4. 認証、順序、期限、安全、minimum support など `T_allow` は継続できる。
5. 他サービス、OS、隣接 artifact が同じ行為を回収する場合、その範囲まで非再捕捉を主張しない。
6. したがって接続命題は「環境計算の停止」ではなく「環境内部の一サブシステムによる局所的非認定」である。

### 6.2 CORE 契約への参照

| 問い | 主要証拠 |
|---|---|
| 本当に処理が止まるか | `core-cs-evaluation-contract.md` の EH1 intersection gate |
| failure / disconnect と違うか | CORE-CS の技術対照と CORE-ART の termination discrimination |
| 終端が作品上知覚可能か | `core-art-evaluation-contract.md` の Termination family |
| 負担を利用者へ残していないか | EVAL-NCC の burden / quality / reliance / non-abandonment gate |
| 外部系が回収していないか | CORE-CS consumer registry と BRIDGE-DN の scope ledger |

BRIDGE-DN はこれらの結果を再判定しない。接続差分がなお残るかだけを判定する。

## 7. 反例表

| 反例 | 判定 |
|---|---|
| 「計算が遍在するので停止は不可能」 | 不採用。停止対象は環境全体でなく GSE の局所 edge |
| 通信断、timeout、sensor absence を Semantic Stop と呼ぶ | 棄却。authored stop と failure を分ける |
| UI が消えたので非認定になった | 棄却。CORE-CS の downstream closure が必要 |
| 画面外へ移った利用者を自然へ戻った、歩いた、回復したと表示する | 棄却。non-certification 違反 |
| 停止後もランキング、達成、報酬、次回介入入力へ回収する | 棄却。non-recapture 違反 |
| 意味推論は止まるが検証・説明・応答義務が残る | BRIDGE-DN 単独の失敗でなく EVAL-NCC の負担転嫁として判定 |
| OS / 他サービスが行為履歴を保持・評価する | GSE 外部を制御できないため主張を監査可能なサブシステムへ縮小 |
| Digital Nature / ecology 文献が同じ局所終端を既に十分記述する | BRIDGE-DN を独立接続命題から CORE-CS / TH-GR の比較節へ統合 |
| calm / peripheral なので応答義務がない | 棄却。知覚的静けさと norm / processing を混同している |

## 8. 操作確認、欠測、境界

| 項目 | 契約 |
|---|---|
| scope ledger | GSE が制御できる producer / consumer と、外部で制御できない system を列挙する |
| borrowed-claim ledger | 各一次資料について borrowed / not borrowed を固定する |
| implementation evidence | CORE-CS EH1 未実施なら「設計可能性」以上を主張しない |
| perception evidence | CORE-ART / CS の EH3 未実施なら「知覚可能」と主張しない |
| external-system unknown | 非回収成功にせず、局所 scope の限界として残す |
| inaccessible primary source | 二次要約で穴埋めせず provisional / unresolved とする |
| no user response | BRIDGE-DN の支持・棄却に使わない |

### 8.1 構成概念と主要観測量

| 構成概念 | 主要観測量 | 副次観測量 | 失敗条件 |
|---|---|---|---|
| locality | GSE が所有する producer / consumer と外部系を分けた scope ledger | OS / service / device 別の不明領域 | 環境全体まで停止を主張する |
| auditable stop | CORE-CS EH1 の stop closure と forbidden-event count | replay / log reproducibility | UI 非表示や通信断だけを証拠にする |
| environmental continuation | `T_allow` と隣接系の継続を明記する | auth / safety / support / expiry | 全計算停止を必要条件にする |
| non-recapture | GSE subsystem 内の downstream recapture count | 外部系の known / unknown ledger | 停止後に評価・報酬へ戻す |
| conceptual residual | 既存理論から借りる部分を除いた残余差分 | prior-art collision matrix | 差分が既存概念の言い換えだけになる |

BRIDGE-DN の主要評価は `conceptual residual` と scope の妥当性である。利用者側の termination perception は副次参照であり、接続命題の主要 outcome にしない。

### 8.2 評価時点と観測窓

| 時点 | 評価 |
|---|---|
| `DN-T0` 概念固定時 | borrowed / not-borrowed ledger、反例、禁止線を一次資料で監査 |
| `DN-T1` 実装候補完成時 | CORE-CS EH1 と同じ stop episode の境界・非再捕捉を参照 |
| `DN-T2` 外部形成時 | termination / failure の知覚だけを CORE-ART / CS から補助参照 |
| `DN-T3` 接続更新時 | OS、service、adjacent artifact、再接続を含む scope ledger を再監査 |

文献検索期間、実装 build、consumer inventory の版を固定する。後から見つかった一次資料で差分が消えた場合は、新規性を守るために検索窓を閉じず、統合・縮小・棄却へ移す。

### 8.3 交絡、媒介、効果修飾

- **概念交絡**: invisibility、calmness、disconnection、non-use、data refusal、open work を Semantic Stop と混同しない。
- **境界交絡**: GSE の処理停止と OS / network failure を分ける。
- **媒介**: termination perception や authority attribution は利用者効果の媒介候補だが、BRIDGE-DN の成立条件にしない。
- **効果修飾**: OS、transport、external service、device ecology は scope を変える。平均化せず system 別に記述する。
- **欠測による選択**: 監査できる consumer だけで全 ecology の non-recapture を主張しない。

## 9. 保持、統合、縮小、棄却、未解決

| 判定 | 条件 |
|---|---|
| 保持 | 既存理論から借りる環境前提と GSE の追加境界が分離され、CORE-CS が authored stop、semantic withdrawal、non-certification、non-recapture、bounded continuation を監査可能に示す |
| 統合 | 差分が CORE-CS の停止可能性を別語で述べるだけなら、BRIDGE-DN を独立接続命題から TH-GR / CORE-CS の比較節へ統合する |
| 縮小 | 外部 service / OS / adjacent artifact の回収を監査できない場合、「計算機自然内部」一般でなく「GSE の所有するサブシステム内」へ縮小する |
| 棄却 | 命題が非計算、自然への復帰、計算の外部を必要とする、既存理論に差分がない、又は stop 後も禁止処理・認定・報酬が更新される |
| 未解決 | 一次全文、実装監査、consumer scope、再接続、外部回収が未確認 |

## 10. 主張禁止線

- Digital Nature の外部、計算の外部、非計算領域、自然への復帰を立てない。
- 画面外身体を recovery、walking、embodiment の成功として認定しない。
- UbiComp の invisibility や calmness を Semantic Stop の証拠にしない。
- ecology の語から環境全体の制御可能性を推論しない。
- GSE 外部の OS、service、device、organization まで非再捕捉を保証しない。
- BRIDGE-DN を独立理論、利用者効果、規範的成功として数えない。

## 11. 現在地と未解決

現在地は `EH0 / conceptual review` である。ADR-027/028 は event、解除、断、失効、再接続の設計を持つが、現行コードに `invitation` / Semantic Stop の実装は確認できないため、EH1 の局所停止証拠はない。

未解決は次である。

1. Digital Nature の書籍一次全文と語の厳密な引用射程。
2. 「computational ecology」が HCI ecology と生態学的 simulation のどちらを指すかの用語境界。
3. GSE が所有する consumer と外部 consumer の scope ledger。
4. OS / service / adjacent artifact による delayed recapture の監査可能性。
5. transport、expiry 数値、OS 非対称、保持・暗号化・削除の未決事項。
6. 既存理論が局所的 semantic withdrawal と non-recapture の結合を既に十分記述していないかの体系的 review。
