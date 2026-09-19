# CORE 命題カバレッジ表 v0.1

> Status: pre-SSOT evaluation draft / 2026-09-17
>
> 本表は命題ごとの主要判定先を一つに固定する。副担当は証拠を供給するが、別の成功条件を作らない。数値マージン、採用尺度、標本設計は未決であり、`docs/`、ADR、事前登録、実装仕様を変更しない。

## 1. 担当原則

- `CORE-CS` は処理境界、停止閉包、非再捕捉、退化、運用継続を主要判定する。
- `CORE-ART` は経路依存の作品成立、非診断性、終端形式、曖昧さ、gaming、linkability を主要判定する。
- `EVAL-NCC` は `CORE-NORM` の実証契約として、応答義務、負担、品質、支援、依存の共同 gate を主要判定する。
- `MEAS-CDPD` は測定・予測トラックであり、CORE の成功を代行しない。
- `BRIDGE-DN` は独立理論や利用者効果ではなく、既存理論との概念比較と処理境界の接続を判定する。
  > ★ **2026-09-19（J-6）**: `BRIDGE-DN` は独立の接続命題として数えず、`CORE-CS` の比較節（`core-cs-evaluation-contract.md` §16）へ統合した。下の表の `BRIDGE-DN` の列・行は統合の前の形である。
- この表では EVAL-NCC の条件 `C0-C4` を、`GR-C1-C7` との混同を避けるため `EVAL-C0` から `EVAL-C4` と表記する。参照先契約の条件名自体は変更しない。
- 同じ命題に複数の関連領域がある場合、主要判定は下表の `primary contract owner` だけが持つ。

## 2. 横断命題

| proposition | theoretical parent | primary contract owner | secondary evidence | construct / observable | comparison | evidence tier | support / shrink / reject / unresolved | current status | unresolved cell |
|---|---|---|---|---|---|---|---|---|---|
| `CORE-CS` 停止可能な適応系 | `TH-GR` / `SUB-SWM` | `CORE-CS` | `EVAL-NCC`, `CORE-ART` | stop closure、forbidden event、recapture、allowed continuation、abstention | 連続認定 / 表示停止 / Semantic Stop / failure | EH0→EH1、知覚は EH3-4 | EH1 成立・知覚差なしなら監査可能な stop mechanism へ縮小 / 知覚のみなら終端表現へ縮小 / UI-only 又は禁止処理継続で棄却 / 実装前は未解決 | defined; not instrumented | stop target registry、`t0`、監査 event schema、latency margin |
| `CORE-ART` 終端を作品形式にする | `TH-MTP` / `SUB-PGP` / `SUB-SWM` | `CORE-ART` | `CORE-CS`, `EVAL-NCC` | path dependence、portraitness、non-diagnostic reading、termination-as-form、burden | widget / decoration / portrait / aperture / apparent stop / Semantic Stop / failure | EH0、EH2、EH3-4 | 構成概念別 gate / GSE 固有技法へ縮小 / 状態計・診断・故障読解で棄却 / artifact 未実装は未解決 | defined; not instrumented | replay artifact、codebook、尺度妥当化、外部標本 |
| `CORE-NORM` 権限返還と負担解除 | `TH-GR` / `EVAL-NCC` | `EVAL-NCC` | `CORE-CS`, `CORE-ART` | burden / quality / reliance / non-abandonment | EVAL-C0-EVAL-C4 | EH0、EH3-4 | 4 gate 全通過 / 処理構造の記述へ縮小 / 放置・品質悪化で棄却 / margin 未決は未解決 | defined v0.1; not piloted | 数値マージン、採用尺度、課題ルーブリック |
| `BRIDGE-DN` 局所的非認定 | `TH-GR` と Digital Nature の接続 | conceptual review | `CORE-CS`, `CORE-ART` | 借用範囲、局所停止、環境継続、非再捕捉、再接続 | comparative argument / counterexample / boundary audit | EH0、境界証拠は EH1 参照 | 差分保持 / 既存概念へ統合・縮小 / 差分なし又は存在論的過大化で棄却 / 一次資料不足は未解決 | defined; limited survey completed | 体系的 review、Digital Nature 書籍一次全文との射程照合 |

## 3. 構成命題 `GR-C1-C7`

| proposition | theoretical parent | primary contract owner | secondary evidence | construct / observable | comparison | evidence tier | support / shrink / reject / unresolved | current status | unresolved cell |
|---|---|---|---|---|---|---|---|---|---|
| `GR-C1` 委譲は双方向 | `TH-GR` | `CORE-CS` | `EVAL-NCC` | O/I/F/V/C/R の境界前後の権限移動 | 一方向の連続占有 vs authored stop | EH0→EH1 | 権限移動を監査可能 / stop control へ縮小 / C/R 継続で棄却 / boundary 未実装は未解決 | defined; not instrumented | 権限 registry と state transition |
| `GR-C2` 非知は設計素材 | `TH-GR` | `CORE-CS` | `CORE-ART`, `BRIDGE-DN` | deliberate abstention と sensor absence の弁別 | authored abstention vs missing / failure | EH0→EH1 | 意図的な推論射程制限を再現 / 欠測処理へ縮小 / 欠測の意味化で棄却 | defined; not instrumented | neutral / abstain の実装表現 |
| `GR-C3` 作品単位は権限軌跡 | `TH-GR` / `TH-MTP` | `CORE-ART` | `CORE-CS` | 観測→推論→形式→招待→停止の全軌跡 | 静止画評価 vs trace-based artifact | EH0、EH3 | 軌跡情報に追加価値 / process visualization へ縮小 / 終点だけで説明できれば棄却 | defined; artifact absent | 軌跡提示と順序操作 |
| `GR-C4` 終了は美的・規範的形式 | `TH-GR` / `TH-MTP` | `CORE-CS` | `CORE-ART`, `EVAL-NCC`, `BRIDGE-DN` | 停止対象、表現、義務終了、故障弁別 | termination / expiry / dismiss / disconnect | EH0→EH1→EH3 | 監査と知覚を別 gate で支持 / technical stop へ縮小 / どちらかの偽装で棄却 | defined; not instrumented | stop event と artifact ending の同期 |
| `GR-C5` 画面外身体は欠損でない | `TH-GR` / `TH-MTP` | `CORE-ART` | `BRIDGE-DN`, `CORE-CS` | non-certification、未確定性、欠測の非人格化 | open ending vs imputation / recovery claim | EH0、EH3 | 未確定性として読まれる / open-work 技法へ縮小 / 身体回帰・回復認定で棄却 | defined; not externally tested | 画面外意味を問わない評価手順 |
| `GR-C6` 返権は善性を自動保証しない | `TH-GR` | `EVAL-NCC` | `CORE-ART`, `CORE-CS` | harm、abandonment、quality、support、surveillance | target vs negligent relinquishment / active control | EH3-4 | 共同 gate 全通過 / 中立な処理構造へ縮小 / harm 又は放置で棄却 | defined v0.1 | margin と安全停止規則 |
| `GR-C7` 権限返還と負担解除は独立 | `TH-GR` / `EVAL-NCC` | `EVAL-NCC` | `CORE-CS` | 権限台帳と負担台帳 | EVAL-C2 vs EVAL-C3 vs EVAL-C4 | EH0、EH3-4 | 二台帳を弁別 / 記述的枠組みへ縮小 / 同一尺度への畳み込みで棄却 | burden side drafted v0.1; authority-ledger instrument unresolved | accountability displacement の計器 |

## 4. 実証予測 `GR-H1-H12`

| proposition | theoretical parent | primary contract owner | secondary evidence | construct / observable | comparison | evidence tier | support / shrink / reject / unresolved | current status | unresolved cell |
|---|---|---|---|---|---|---|---|---|---|
| `GR-H1` 経路依存性 | `TH-MTP` / `SUB-PGP` | `CORE-ART` | `MEAS-CDPD` | 同終点・異経路の識別、path-sensitive similarity | path replay vs endpoint-only control | EH1 artifact check、EH3-4 participant | 経路情報の追加価値 / 装飾的 process view へ縮小 / 終点だけで同等なら棄却 | defined; not instrumented | trace set、識別課題、分析モデル |
| `GR-H2` 非診断的読解 | `TH-MTP` / `SUB-PGP` | `CORE-ART` | `EVAL-NCC` | diagnostic / essentialist code、session-specific reading | widget vs portrait | EH3-4 | 診断読解低下かつ session-specific / temporal-relation reading 増加 / 抽象表示へ縮小 / 片側だけ又はいずれも不成立なら棄却 | defined; not piloted | codebook、認知インタビュー |
| `GR-H3` Semantic Stop の効果 | `TH-GR` / `SUB-SWM` | `CORE-CS` | `CORE-ART`, `EVAL-NCC`, `BRIDGE-DN` | surveillance、authority attribution、task continuation | continuous certification vs Semantic Stop | EH1 + EH4 | 実装成立後に知覚改善と継続非劣性 / stop mechanism 又は終端表現へ縮小 / 禁止処理継続、安全破綻、知覚改善なし、又は継続が非劣性外なら棄却 | defined; not instrumented | target event、知覚尺度、非劣性 margin |
| `GR-H4` 招待と命令の差 | `TH-GR` / `EVAL-NCC` | `EVAL-NCC` | `CORE-ART` | obligation、guilt、penalty、branch distribution、support | EVAL-C1 / EVAL-C3 / EVAL-C0 | EH3-4 | EVAL-NCC intersection gate / 表現差へ縮小 / 圧力・再要求・不利益・一行為誘導・早期離脱又は分布集中・支援破綻で棄却 | contract defined v0.1 | margin、項目妥当化 |
| `GR-H5` 非回収性とゲーム化 | `TH-MTP` / `SUB-PGP` | `CORE-ART` | `CORE-CS` | gaming rate、reward/certification recapture count | nonnumeric nonreward portrait vs numeric/reward | EH1 + EH3-5 | recapture=0 かつ gaming 非悪化 / 非報酬 UI 技法へ縮小 / 再回収又は gaming 悪化で棄却 | defined; not instrumented | gaming protocol、許容幅、長期観測 |
| `GR-H6` セッション局所性 | `TH-MTP` / `SUB-PGP` | `CORE-ART` | privacy review | within-session path utility、cross-session linkability | same-session vs cross-session matching | EH1、EH3-5 | path utility 保持かつ linkability 上限内 / ephemeral visualization へ縮小 / 個人署名化で棄却 | defined; not instrumented | attack model、閾値、標本 |
| `GR-H7` 停止境界の監査可能性 | `TH-GR` / `SUB-SWM` | `CORE-CS` | `BRIDGE-DN` | forbidden-event count、allowed continuation、replay equality | pre/post boundary、failure controls | EH1 | 禁止 event=0 と許可処理継続 / documentation claim へ縮小 / 禁止処理発生で棄却 | defined; not instrumented | audit log、replay fixture、stop closure |
| `GR-H8` 観測不足への退化 | `TH-GR` / `SUB-SWM` | `CORE-CS` | `CORE-ART`, `EVAL-NCC`, `BRIDGE-DN` | neutral / abstain rate、false stable portrait | low observation / IME missing / non-typing controls | EH1 + EH3 | 中立退化し意味断定なし / missingness policy へ縮小 / 人格・状態表現なら棄却 | defined; not instrumented; neutral / abstain policy partially specified | neutral state と知覚操作確認 |
| `GR-H9` 負担転嫁と返権の弁別 | `TH-GR` / `EVAL-NCC` | `EVAL-NCC` | `CORE-CS`, `CORE-ART` | burden / quality / reliance / non-abandonment | EVAL-C2 / EVAL-C3 / EVAL-C4 | EH3-4 | 4 gate 全通過 / 処理構造へ縮小 / burden 不変、品質・支援悪化、誤受容又は UVR 増加、EVAL-C3/C4 弁別不能、minimum support 不成立で棄却 | contract defined v0.1 | margin、尺度、課題 |
| `GR-H10` 曖昧さの用量限界 | `TH-MTP` / `SUB-PGP` | `CORE-ART` | `EVAL-NCC` | interpretation time、recheck、second work、abandonment | low / medium / high ambiguity | EH3-4 | 高曖昧で第二作業化・再確認・放置不安が増え、用量限界が示される / 形成的指針へ縮小 / 負担増がなく単調有益モデルが残れば棄却 | defined; not piloted | dose manipulation、モデル比較 |
| `GR-H11` 生産的摩擦との両立 | `TH-GR` / `EVAL-NCC` | `EVAL-NCC` | `CORE-CS` | DQ、EA、UVR、burden、completion | independent mini-experiment: zero / light / heavy friction; not EVAL-C0-EVAL-C4 main gate | EH4 | light が reliance を改善し品質非劣性又は改善、burden 上限内 / 特定課題・層へ縮小 / 検証改善なしで burden のみ増加又は品質・公平性悪化で棄却 | independent mini-experiment drafted v0.1 | margin、item pool、power |
| `GR-H12` AI 疲労推定の分離 | `EVAL-NCC` / `MEAS-CDPD` | `EVAL-NCC` | `MEAS-CDPD` | AFS、incremental validity、calibration、group error | measurement boundary audit; intervention comparison ではない | EH4-5 | 測定役割を分離し、研究用予測時のみ外部標本で増分妥当性・校正成立 / 外部自己報告 outcome のみに縮小 / 診断・介入入力への流用、独自 AFS、又は校正不成立の無視で棄却 | boundary rule drafted; predictive validation unresolved | 日本語妥当化、独立標本、遅延 outcome |

## 5. 競合の裁定

1. `GR-H4/H9/H11/H12` は既存の EVAL-NCC 成果物群を primary とし、新契約では定義し直さない。ただし H11 は独立ミニ実験、H12 は介入比較ではない測定境界監査として、EVAL-C0-EVAL-C4 の主比較から分離する。
2. `GR-H5` は仮説本文が gaming の条件比較なので `CORE-ART` を primary とする。`CORE-CS` は非再捕捉の実装前提を副担当する。
3. `GR-H3` は Semantic Stop の実装成立が前提なので `CORE-CS` を primary とする。監視感等の尺度は EVAL-NCC の測定原則を参照する。
4. `GR-C4` は美的形式と規範形式を含むが、技術的 termination / failure / expiry の識別を先に通すため `CORE-CS` を primary とする。
5. `BRIDGE-DN` は `GR-H3/H7/H8` の結果を再判定しない。既存理論との接続差分だけを判定する。

## 6. 整合性検査

- `GR-H1-H12` の primary owner は各一つである。
- EH1 実装監査、EH2 本人試視、EH3 外部形成、EH4 統制比較、EH5 フィールドを代替関係にしない。
- 実装監査の成功を利用者知覚の成功にせず、知覚成功を処理停止の証拠にしない。
- `invitation: none`、表示消去、timeout、disconnect を Semantic Stop の成立証拠にしない。
- 新しい数値閾値は置かず、margin、dose、latency、linkability 上限は `unresolved` とする。
