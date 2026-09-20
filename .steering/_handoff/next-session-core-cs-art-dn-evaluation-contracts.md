> ✅ **2026-09-18 追記**: 本メモの成果物（CORE-CS / CORE-ART / BRIDGE-DN の評価契約・命題カバレッジ行列）は
> **2026-09-17 15:00〜15:11 に作成済み**（`.steering/20260916-gse-theory-operationalization-review/`・2026-09-18 にコミット）。
> ★ 次は **Claude Code の批判的レビュー** → `next-session-theory-critical-review.md`。⚠️ 以下は当時の記述（履歴）。

# 次セッション用プロンプト: CORE-CS / CORE-ART / BRIDGE-DN 評価契約

> 作成: 2026-09-17
>
> Status: **未着手 / 次セッションの主タスク**
>
> ⚠️ 本タスクは pre-SSOT の評価契約作業である。成果物は `.steering/20260916-gse-theory-operationalization-review/` と既存 `.idea` 草案に限定し、Claude Code との批判的検討と人間による採否判断を経るまで `docs/`、ADR、事前登録、実装仕様へ昇格させない。

## 0. ユーザー指定

EVAL-NCC によって具体化した `CORE-NORM` に続き、残る `CORE-CS`、`CORE-ART`、`BRIDGE-DN` の評価契約を次セッションで作る。

サーヴェイが必要な場合は、必要な不足セルだけをサブエージェントへ委譲する。サーヴェイ担当は **gpt-5.5 または同等以上の調査能力を持つモデル**、推論強度は **xhigh 相当**を選ぶ。利用可能なモデル名が異なる場合も、軽量・高速モデルへ黙って落とさない。条件を満たすモデルを利用できなければ、その調査を `blocked / unresolved` と明記する。

## 1. 前セッションで完了したこと

次の EVAL-NCC v0.1 は作成済みであり、再作成しない。

1. `measurement-dictionary.md`: 判断品質、誤受容、無検証依存、支援到達可能性、罪悪感、応答義務、不利益予期、放置不安
2. `eval-ncc-analysis-contract.md`: IAS、C0-C4、estimand、競合転帰、欠測、共同 gate
3. `eval-ncc-dag.md`: 事前交絡、分岐、媒介、post-treatment 調整禁止
4. `gr-h4-h9-h11-h12-falsification-table.md`: GR-H4/H9/H11/H12 の支持・縮小・棄却・未解決

この結果、`CORE-NORM` は burden / quality / reliance / non-abandonment の4 gateで評価するところまで具体化した。今回、`CORE-NORM` の数値マージンや尺度妥当化を先に埋めず、他の CORE の契約を同じ解像度へ近づける。

## 2. 最初に読むファイル

次の順で読む。

1. `.steering/20260916-gse-theory-operationalization-review/next-task.md`
2. `.steering/20260916-gse-theory-operationalization-review/measurement-dictionary.md`
3. `.steering/20260916-gse-theory-operationalization-review/eval-ncc-analysis-contract.md`
4. `.steering/20260916-gse-theory-operationalization-review/eval-ncc-dag.md`
5. `.steering/20260916-gse-theory-operationalization-review/gr-h4-h9-h11-h12-falsification-table.md`
6. `.idea/20260915-gse-theory-architecture-and-roadmap.md` §1-3、§5、§7
7. `.idea/20260915-generative-relinquishment-theory.md` §3-10、§12
8. `.idea/20260908-measurement-terminating-practice-portraiture.md`
9. `.idea/20260916-gse-mitou-research-plan.md` §2-4、§10、§13
10. 読み取り専用の実装・SSOT照合として、必要な範囲だけ `docs/architecture/expression-channel.md`、ADR-023、ADR-025、ADR-027、ADR-028、ADR-029 を確認する

⚠️ handoff は三次資料である。条件名、実装状態、停止境界について主張する前に、`.idea` 原文、ADR、コードまたは実行結果で裏を取る。

## 3. 命題と評価契約の担当境界

| 上位命題 | 主な構成命題 | 主な実証予測 | 今回の主担当 |
|---|---|---|---|
| `CORE-CS` 停止可能な適応系 | `GR-C1/C2/C4/C7` | `GR-H3/H5/H7/H8/H9/H11` | システム境界・実装監査契約。H9/H11 の人間側指標は既存契約を参照 |
| `CORE-ART` 終端を作品形式にする | `GR-C2/C3/C4/C5` | `GR-H1-H6/H10` | 作品比較・知覚・解釈・形成的評価契約 |
| `CORE-NORM` 権限返還と負担解除 | `GR-C1/C4/C6/C7` | `GR-H2-H5/H8-H12` | EVAL-NCC v0.1 済み。今回は整合確認だけ |
| `BRIDGE-DN` 計算機自然内部の局所的非認定 | `GR-C2/C4/C5` | `GR-H3/H7/H8` | 概念比較・境界監査契約。独立理論や介入効果へしない |

命題の重複は削除しない。主担当・副担当を定め、同じ `GR-H*` に別定義や別の成功条件を作らない。

## 4. 必須成果物

成果物は `.steering/20260916-gse-theory-operationalization-review/` に pre-SSOT 草案として置く。

1. `core-cs-evaluation-contract.md`
2. `core-art-evaluation-contract.md`
3. `bridge-dn-evaluation-contract.md`
4. `core-proposition-coverage-matrix.md`

4成果物を相互レビューした後、必要最小限だけ次へ反映する。

- `.idea/20260915-generative-relinquishment-theory.md`
- `.idea/20260915-gse-theory-architecture-and-roadmap.md`
- `.idea/20260916-gse-mitou-research-plan.md`

`docs/`、ADR、事前登録、実装コードは変更しない。

## 5. CORE-CS 評価契約

`CORE-CS` を「UI が消えた」「invitation が none になった」だけで支持しない。最低限、次を定義する。

### 5.1 比較条件候補

- 連続推論・連続認定
- 表示だけ消える見かけ上の停止
- 意味推論・達成認定を停止する Semantic Stop
- Semantic Stop + no residual response duty + non-recapture
- timeout / failure / disconnect（意図的終端の対照）

### 5.2 システム評価量

- 停止対象となる event / field / state transition の閉包
- stop request から禁止処理停止までの latency
- 境界後の forbidden-event count
- 認定、報酬、ランキング、介入入力への recapture count
- expiry、解除、再接続後の状態遷移
- 通常状態推定、認証、順序、期限、安全処理など継続を許可する処理
- replay / log での監査可能性と再現性
- 観測不足時の neutral / abstain への退化率

### 5.3 利用者側の評価量

- intentional termination と failure / timeout の弁別
- system authority attribution、surveillance perception
- 主タスク継続の非劣性
- non-recapture と支援継続の理解
- 実装説明の有無と終端表現の有無を分離した manipulation check

### 5.4 棄却条件

- UIだけ停止し、禁止した推論・認定・報酬処理が続く
- `invitation: none` を停止証拠として扱う
- 停止後の行為を後から成功・回復・遵守として再捕捉する
- 観測不足を安定状態や人格特徴として表示する
- 停止により必要な運用安全性または支援到達可能性が破綻する

## 6. CORE-ART 評価契約

`CORE-ART` を「美しい」「抽象的」「意味が開かれている」という好意的評価だけで支持しない。

### 6.1 比較条件候補

- 状態 widget / 数値表示
- 経路を使わない装飾的抽象表示
- 経路依存 Practice Portrait
- Portrait + Immanent Aperture
- Portrait + 見かけ上の終了
- Portrait + 監査可能な Semantic Stop
- failure / timeout 表示

同じ終点・異なる経路、および異なる終点・類似経路を含む固定 replay trace を使い、経路依存性と最終量依存を分離する。

### 6.2 構成概念候補

- path distinguishability / path dependence
- portraitness、self-relatedness、session-specificity
- diagnostic / essentialist interpretation の低さ
- intentional termination / failure discrimination
- work completeness / termination-as-form
- invitation と命令の弁別
- interpretation burden、second-work formation、再確認
- gaming、長期 linkability、自己量化的読解
- ambiguity dose と任意解釈の範囲

各概念に定義、非該当例、観測単位、測定時点、主要・副次評価量、方向、欠測、失敗条件を持たせる。好み、美しさ、理解度、作品成立を一つの総合点へ畳まない。

### 6.3 方法

- randomized artifact comparison と順序効果対策
- forced-choice の経路識別と自由記述の読解コード
- 形成的 think-aloud は本試行の outcome と分ける
- outsider linkability と本人の self-relatedness を別々に測る
- qualitative coding のコードブック、二重コーディング、反例ケースを残す
- `EH2` 本人試視を `EH3` 外部形成的評価として数えない

### 6.4 棄却・縮小条件

- 最終量だけで同等に説明でき、経路情報の追加価値がない
- Portrait が状態計、装飾、人格・能力・健康の診断として主に読まれる
- 終端が故障と区別されない、または説明を読んだ時だけ成立する
- 曖昧さが任意解釈でなく義務的な解読や第二作業を増やす
- 長期 linkability、gaming、自己量化的読解が許容幅を超える
- 既存の data portrait / open work / interactive art だけで十分説明できる場合、独立理論でなくGSE固有技法へ縮小する

## 7. BRIDGE-DN 評価契約

`BRIDGE-DN` は第四の主理論でも、Digital Nature 全体への反論でもない。評価対象を「計算と物理の循環が続く環境内部で、個別システムの意味推論・達成認定・応答要求を局所的に終端できる」という狭い接続命題に限定する。

### 7.1 必須要素

- Digital Nature / computational ecology から借りる主張と借りない主張
- 環境全体の計算継続と、局所 Semantic Stop の両立条件
- 局所性、監査可能性、非再捕捉性、再接続条件
- 「計算の外部」「自然への復帰」「非計算」を不用意に主張しない境界
- CORE-CS と重なる実装証拠、CORE-ART と重なる知覚証拠の参照関係
- 接続命題を保持、統合、縮小、棄却する条件

### 7.2 主な反例

- 停止後も別サービスや遅延処理が同じ行為を評価・報酬へ回収する
- 単なる通信切断やセンサー不在を局所的非認定と呼ぶ
- 利用者が画面外へ移ったことを「自然」または「身体回帰」と認定する
- Digital Nature の既存議論が同じ局所終端を既に十分記述しており、追加差分が残らない

### 7.3 評価形式

初期段階ではユーザー尺度を無理に作らない。一次資料に基づく comparative argument、反例表、処理境界監査を主要とする。利用者評価を追加する場合も、BRIDGE-DN 自体の成立ではなく、終端の知覚可能性に限定する。

## 8. `core-proposition-coverage-matrix.md`

最低限、次の列を持たせる。

| 列 | 内容 |
|---|---|
| proposition | CORE-* / BRIDGE-DN / GR-C* / GR-H* |
| theoretical parent | TH-GR / TH-MTP / SUB-PGP / SUB-SWM |
| primary contract owner | CORE-CS / CORE-ART / EVAL-NCC / MEAS-CDPD / conceptual review |
| secondary evidence | 補助的に参照する契約 |
| construct / observable | 観測可能量 |
| comparison | 条件・対照 |
| evidence tier | EH0-EH5 |
| support / shrink / reject / unresolved | 判定規則 |
| current status | defined / instrumented / piloted / externally tested |
| unresolved cell | 不足する尺度、実装、文献、標本 |

全 `GR-H1-H12` に primary owner を一つだけ割り当てる。二つ以上の契約が主要判定を競合する場合は、定義を統合するか `unresolved` とする。

## 9. サーヴェイとサブエージェント

### 9.1 起動条件

- 既存定義を確認しないと構成概念が循環する
- CORE-ART の portraitness、termination-as-form、diagnostic reading に妥当な既存操作化が必要
- CORE-CS の termination、deactivation、adjustable autonomy、non-use、non-recapture に一次資料が必要
- BRIDGE-DN の接続範囲が既存理論の射程と衝突する
- 現行草案の引用が一次資料を超えている疑いがある

「念のため」の広い探索、引用数を増やすだけの探索、新しい理論名を増やす探索は行わない。

### 9.2 推奨する最大3分割

1. **CORE-CS / adaptive systems**: mixed initiative、adjustable autonomy、interruptibility、termination、deactivation、contestability、non-use
2. **CORE-ART / art-HCI**: generative art、open work、data portrait、autographic visualization、interactive art、withdrawal / termination as form
3. **BRIDGE-DN**: Digital Nature、computational ecology、ubiquitous computation、局所的な非計算・停止・境界

### 9.3 モデルと出力条件

- モデル: **gpt-5.5 または同等以上の調査モデル**
- reasoning effort: **xhigh 相当**
- 条件を満たさないモデルへ黙って downgrade しない
- 対象概念、読むローカル節、必要な一次資料、除外範囲、検索日、データベース／検索式を明示する
- DOI / URL、研究設計、対象集団、N、操作、評価量、借りられる定義、借りられない主張、GSEへの外挿限界を表で返す
- main agent が DOI、一次資料、引用射程を再照合してから統合する
- NDJSON、キーストローク内容、参加者データ、秘密情報を渡さない

## 10. 共通の評価契約スキーマ

各成果物に次を持たせる。

1. 命題の一文と理論的親
2. 含む範囲・含まない範囲
3. 観測単位・対象集団・証拠階梯
4. 条件と対照
5. 構成概念と観測可能量
6. 測定時点・観測窓
7. 主要・副次評価量と算出規則
8. 実装／知覚／規範の操作確認
9. 交絡、媒介、効果修飾
10. 構造的欠測、技術欠測、選択的無応答
11. 支持、縮小、棄却、未解決
12. 代替説明、最強の反例、主張禁止線

## 11. 敵対的レビュー質問

- CORE-CS は単なる stop button、timeout、表示消去を新概念化していないか。
- CORE-ART は好みや美しさを作品成立と取り違えていないか。
- 終端表現を理解できたことを、裏側の処理停止の証拠にしていないか。
- 実装上停止したことを、利用者が故障と弁別できる証拠にしていないか。
- `BRIDGE-DN` が「計算機自然の外」を立てる過大な存在論へ膨張していないか。
- EVAL-NCC と新契約で同じ GR-H を別の成功条件で判定していないか。
- 本人試視、AI実装監査、外部形成的評価を混同していないか。
- 支持例だけでなく、縮小・棄却・未解決へ実際に落ちる規則があるか。

## 12. 完了条件

- CORE-CS の実装監査と利用者知覚を分離した契約がある。
- CORE-ART の作品成立、経路依存、非診断性、終端形式、負担を別々に測れる。
- BRIDGE-DN の狭い接続範囲と棄却条件がある。
- `GR-H1-H12` すべてに primary owner が一つ割り当てられている。
- CORE-NORM / EVAL-NCC v0.1 と定義・成功条件が衝突していない。
- EH1、EH2、EH3、EH4、EH5 を混同していない。
- 新しい数値閾値を根拠なく置いていない。根拠不足は `unresolved` のまま残す。
- 必要なサーヴェイのみ、gpt-5.5相当・xhigh相当で実施し、主担当が一次資料を再照合している。
- 4成果物を敵対的にレビューし、既存3本の `.idea` へ必要最小限だけ反映している。
- `docs/`、ADR、事前登録、実装コードを変更していない。

## 13. 現在の作業状態

- ブランチ: `docs/adr-030-stall-onset-definition`
- HEAD: `da1b8b2 merge(loop): issue 005 (stall onset t0) を取り込む`
- EVAL-NCC v0.1 の4成果物は `.steering/20260916-gse-theory-operationalization-review/` に作成済み。
- `.idea` の3文書には EVAL-NCC の共同 gate と参照先を反映済み。`.idea` は gitignore 対象。
- `docs/references.md` と `.steering/_handoff/README.md` には本タスク以前から未コミット変更がある。上書き・巻き戻しをしない。
- `.steering/20260916-ai-fatigue-theory-integration/` と `.steering/20260916-gse-theory-operationalization-review/` は未追跡。
- `.worktrees/` と `tmp/` は既存の未追跡物であり、削除・変更しない。
- コミットはユーザーが明示した場合だけ行う。

## 14. 開始時の短い実行指示

既存 EVAL-NCC v0.1 を評価契約の型として読み、まず `core-proposition-coverage-matrix.md` に全命題と primary owner を配置する。次に CORE-CS、CORE-ART、BRIDGE-DN の順で、既存文献とローカル資料だけで埋められるセルを操作化する。不足セルだけを最大3本のサーヴェイへ分割し、gpt-5.5または同等以上・xhigh相当のサブエージェントへ委譲する。主担当が一次資料と引用射程を再照合し、4成果物を相互レビューしてから `.idea` へ最小反映する。SSOT は触らない。
