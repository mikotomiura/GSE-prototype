# 次セッション用プロンプト: EVAL-NCC 測定辞書と推定契約

> ✅ **2026-09-17 に EVAL-NCC v0.1 を完了。** `measurement-dictionary.md`、`eval-ncc-analysis-contract.md`、`eval-ncc-dag.md`、`gr-h4-h9-h11-h12-falsification-table.md` を作成した。
>
> ⚠️ このメモは完了時点の記録であり、次セッションの開始点ではない。後続の `CORE-CS` / `CORE-ART` / `BRIDGE-DN` 評価契約は `next-session-core-cs-art-dn-evaluation-contracts.md` を使う。

> 作成: 2026-09-17
>
> Status: **v0.1 完了 / 後続タスクへ移管済み**
>
> ⚠️ 本タスクは pre-SSOT の `.idea` 草案作業である。Claude Code との批判的検討と人間による採否判断を経るまで、理論・命題・名称を `docs/`、ADR、事前登録、実装仕様へ昇格させない。

## 0. ユーザー指定

次セッションでは、広いサーヴェイを先に追加せず、`EVAL-NCC` の測定辞書と推定契約を作る。

サーヴェイが必要になった場合は、必要箇所に限定してサブエージェントを使う。サーヴェイ担当は **gpt-5.5 または同等の調査能力を持つモデル**、推論強度は **xhigh 相当**を選ぶ。利用可能なモデル名が異なる場合も、軽量・高速モデルへ黙って落とさない。

## 1. 最初に読むファイル

次の順で読む。

1. `.steering/20260916-gse-theory-operationalization-review/next-task.md`
2. `.steering/20260916-gse-theory-operationalization-review/theory-propagation-audit.md`
3. `.steering/20260916-gse-theory-operationalization-review/requirement.md`
4. `.steering/20260916-gse-theory-operationalization-review/design.md`
5. `.steering/20260916-gse-theory-operationalization-review/decisions.md`
6. `.steering/20260916-gse-theory-operationalization-review/tasklist.md`
7. `.idea/20260915-generative-relinquishment-theory.md`
8. `.idea/20260915-gse-theory-architecture-and-roadmap.md`
9. `.idea/20260916-gse-mitou-research-plan.md`
10. `.steering/20260916-ai-fatigue-theory-integration/decisions.md`

⚠️ `.idea` の3文書はすべて **pre-SSOT draft** である。内部整合が取れていても、採用済み理論、正式ロードマップ、SSOT と呼ばない。

## 2. 今回の目的

`CORE-NORM`、`GR-H4`、`GR-H9`、`GR-H11`、`GR-H12` を反証可能にするため、次の8構成概念を操作化する。

1. 判断品質
2. 誤受容
3. 無検証依存
4. 支援到達可能性
5. 罪悪感
6. 応答義務
7. 不利益予期
8. 放置不安

単に質問項目を並べるのではなく、各概念に以下を持たせる。

- 構成概念の定義
- 含めない近接概念
- 観測単位と対象集団
- 測定時点と観測窓
- 主要・副次評価量
- 算出規則と望ましい方向
- 許容幅または非劣性マージンの決め方
- 主要交絡と媒介候補
- 構造的欠測、技術欠測、選択的無応答の処理
- 支持、縮小、棄却、未解決の判定条件

## 3. 必須成果物

成果物は `.steering/20260916-gse-theory-operationalization-review/` に pre-SSOT 草案として置く。

1. `measurement-dictionary.md`
2. `eval-ncc-analysis-contract.md`
3. `eval-ncc-dag.md`
4. `gr-h4-h9-h11-h12-falsification-table.md`

既存3本の `.idea` へは、4成果物を相互レビューした後に必要最小限だけ反映する。`docs/`、ADR、事前登録、実装コードは変更しない。

## 4. EVAL-NCC の最低契約

- 主要解析集団を招待へ割り付けられた全機会とし、再開者だけへ限定しない。
- 受容、保留、拒否、見逃し、無応答を事前定義する。
- 見逃しと意図的無応答を観測だけで完全識別できると仮定しない。
- 再開、再停止、外部化、離脱を競合転帰として扱う。
- 技術欠測、観測不能、選択的無応答を分ける。
- 分岐後の罪悪感、検証行動、支援利用を無条件に共変量調整しない。
- 負担低減だけで成功とせず、判断品質と支援到達可能性の非劣性を同時に要求する。
- 最小支援義務を定義し、それを欠く `negligent relinquishment` を負の対照に置く。
- completer-only 解析を主要解析にしない。

## 5. GR-H11 の独立設計

生産的摩擦は一般的な「負荷は悪い」という命題への反例なので、EVAL-NCC の付記で済ませない。

- zero / light / heavy friction の3水準候補
- 客観的に検証可能な課題
- 誤受容と無検証依存の区別
- interaction burden / verification burden
- 判断品質と負担の同時判定
- 摩擦への好み、Need for Cognition、事前知識などの効果修飾候補

用量、課題、評価量が決まらない場合は、決まった体で埋めず `unresolved` とする。

## 6. サーヴェイとサブエージェントの運用

### 起動する条件

- 構成概念の既存定義や確立尺度を確認しないと循環定義になる。
- estimand、競合転帰、principal stratum、missingness など統計契約の選択に一次資料が必要。
- guilt / obligation / autonomy、overreliance / appropriate reliance など、隣接概念の識別に専門領域の確認が必要。
- 現行草案の引用が一次資料の射程を超えている疑いがある。

### 起動しない条件

- 「念のため」領域全体を広く探す。
- 新理論や新ジャンルを増やす材料を探す。
- 測定辞書を作る前に、Digital Nature や生成芸術全体の差分レビューへ戻る。
- 既に [P361]-[P367] と [P127]/[V37] で足りる主張を、引用数だけ増やす。

### 推奨する分割

必要になった問いだけを、最大3本程度へ分ける。

1. human-AI reliance: 判断品質、誤受容、無検証依存、verifiability
2. autonomy / affect: 罪悪感、応答義務、不利益予期、放置不安、支援到達可能性
3. causal inference: ITT 相当、競合転帰、分岐別 estimand、欠測、post-treatment bias

各サブエージェントへ、対象概念、読むローカル節、必要な一次資料、除外範囲、出力表を明示する。報告には DOI / URL、研究設計、対象集団、N、借りられる定義、借りられない主張、GSE への外挿限界を含める。主担当が一次資料と DOI を再照合してから採否する。

## 7. SSOT 境界

- `.idea` と本 steering 配下は草案・作業記録である。
- `docs/references.md` は書誌 SSOT だが、文献登録は理論採用を意味しない。
- 今回は `docs/references.md` への追加も、測定契約に不可欠な一次資料が新たに確定した場合だけに限定する。
- 理論の昇格案は別成果物として提案できるが、実際の昇格編集は行わない。
- Claude Code のレビュー結果と人間の採否判断を記録してから、別タスクで SSOT 反映を行う。

## 8. 完了条件

- 8構成概念が相互に識別され、同義語による循環定義がない。
- 各概念に測定時点、方向、欠測処理、交絡、失敗条件がある。
- EVAL-NCC の解析集団、分岐、estimand、競合転帰、欠測規則が書かれている。
- post-treatment 変数と事前交絡が DAG で分離されている。
- negligent relinquishment の負の対照がある。
- GR-H11 に摩擦の用量と、負担・判断品質の同時判定がある。
- AI Fatigue Scale を瞬間状態、独自短縮尺度、介入入力として扱っていない。
- AI 実装 `EH1`、本人パイロット `EH2`、外部形成的評価 `EH3` 以降を混同していない。
- 広いサーヴェイを未実施のまま残しても、それを失敗扱いにしない。
- 4成果物を敵対的にレビューし、未解決点を隠さず列挙する。

## 9. 現在の作業状態

- ブランチ: `docs/adr-030-stall-onset-definition`
- HEAD: `da1b8b2 merge(loop): issue 005 (stall onset t0) を取り込む`
- `.idea` は gitignore 対象で、通常の `git diff` / `git status` に出ない。
- `docs/references.md` は [P361]-[P367] の書誌追加で変更中。これは理論昇格ではない。
- `.steering/20260916-ai-fatigue-theory-integration/` と `.steering/20260916-gse-theory-operationalization-review/` は未追跡。
- `.worktrees/` と `tmp/` は既存の未追跡物であり、本タスクで削除・変更しない。
- コミットはユーザーが明示した場合だけ行う。

## 10. 開始時の短い実行指示

上記の読書順で現状を確認し、まず4成果物の見出しと表スキーマを作る。既存文献だけで埋められる箇所を先に操作化し、根拠が不足するセルだけを列挙する。その不足セルについてのみ、gpt-5.5 または同等の調査モデル・xhigh 相当のサブエージェントへ領域別に委譲する。調査結果を主担当が再照合して4成果物へ統合し、敵対的レビューと整合性検査まで完了する。
