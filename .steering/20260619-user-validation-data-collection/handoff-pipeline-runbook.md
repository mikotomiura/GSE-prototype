# 次セッション開始プロンプト — M1 パイロット パイプライン結線 + 運用 runbook (Phase C→F bridge)

> `feedback_handoff_prompt_in_steering` 方針に従い CLAUDE.md 制約込みで固定。
> 親: `roadmap-xy.md` Phase C/F / `decisions.md` D5(分析DB)・D6(匿名化→age→Dropbox) / #6 DuckDB join (PR #30)。
> **新規 `/start-task` で着手。main 基点で別ブランチ・別 PR。main 直コミット禁止。**
> **このタスクは新規セッションで `/clear` してから着手すること** (タスク境界 = /clear、CLAUDE.md コンテキスト管理ルール2)。

## なぜこれが次か
Phase A/B/C の**コードは全完了** (#18/#20 捕捉 / #19 (a)(b) 指標 / #27 anonymize+age / #29 replay D6 /
**#6 DuckDB join = PR #30**)。logger の参加者 ID 設定可能化 (D1 前提) も実装済 (`logger.rs` の
`first_valid_id`/`generate_participant_id`/`~/.gse/participant_id`)。残るのは **個々の部品を
end-to-end に結線し、M1 パイロット (n=3-5) を実際に回せる運用パイプライン化**。これが Phase F
(通しパイロット) の直前ステップ。実データ不要で合成 session により先行構築・検証できる。

## 既に在る部品 (調査済 2026-06-24・取りこぼし防止)
- **被験者側**: `gse-package` (`src-tauri/src/bin/package.rs`) = raw NDJSON を匿名化→age 暗号化し
  `P###_<session>.age` を生成する自己完結 CLI。被験者は bundled exe を 1 コマンド + Dropbox に D&D (D6)。
- **研究者側 metrics 同期**: `scripts/sync-session.{sh,ps1}` = session NDJSON → `gse-replay --metrics`
  → schema 検証 → gse-dataset の `metrics/P###/<os>/` に commit/push。`sync-all.{sh,ps1}` は束ね版。
- **分析**: `scripts/build_analysis_db.py` (#6) = `metrics.json`/`survey/*.csv`/`sessions.csv` を
  participant_id×phase で join し `cross_section` を生成。`analysis.db` は使い捨て・再生成可能。
- **runbook 先例**: `docs/calibration-smoke-runbook.md` (X 較正側の通し手順書)。Y 側の対応物が無い。

## 結線されていない GAP (= 本タスクの主眼)
1. **研究者側 decrypt 経路が無い**: 受領した `.age` → `age -d` → 匿名化 NDJSON にする手順/スクリプトが未整備
   (`gse-package` は暗号化のみ)。これが無いと sync-session に渡せない。
2. **`sessions.csv` (phase manifest) を作る手段が無い**: `build_analysis_db.py` は pre/post 割当に
   `sessions.csv` を要求するが、生成テンプレート/ヘルパが無い (P-ID×session×os×phase)。
3. **survey CSV の配置規約が運用に無い**: `survey/P###.csv` をどこに置き誰がいつ入れるかが未文書。
4. **通し runbook が無い**: 被験者 3 step (gse-package→Dropbox) + 研究者 (decrypt→sync-session→
   survey 配置→sessions.csv→build_analysis_db) を 1 本に束ねた Y パイロット運用手順書が未作成。
5. **end-to-end 統合検証が無い**: 合成 session を package→decrypt→replay metrics→build_analysis_db に
   通すスモークが無く、結線が壊れても気づけない。

## スコープ
### 含むもの
- 研究者側 **decrypt ラッパ** (`scripts/unpack-session.{sh,ps1}` 等、`.age`→匿名化 NDJSON。age CLI 前提)。
- **`sessions.csv` テンプレート + 生成ヘルパ** (gse-dataset の metrics/ を走査し P-ID×session×os 行を吐き、
  phase 列は研究者が pre/post 記入)。`build_analysis_db.py` とキー整合。
- **survey/P###.csv 配置規約**の明文化 + (任意) 軽い検証 (data-privacy 列ガードは #6 に既存)。
  **散歩受容 (D8)**: post survey に WoZ 自己申告 1-3 問 (歩いたか/作業に戻れたか/不便益として受容できたか)
  の列を最小スキーマに含める (build_analysis_db は任意 survey 列対応済で改修不要)。
- **Y パイロット運用 runbook** (`docs/pilot-runbook.md` 等): 被験者手順 + 研究者手順を end-to-end で。
  Dropbox File Request 手順 (D6) を被験者向けに明記。**散歩は WoZ (D8)**: Wall の散歩文言は出る前提で、
  被験者手順に「Wall が出たら席を立つ/歩く」を含め、受容性は post survey で拾う (新規計測コード不要)。
  `calibration-smoke-runbook.md` の様式に倣う。
- **end-to-end 統合スモーク**: 合成 session を全段に通し `cross_section` が出るまで検証 (実データ不要)。

### 含まないもの
- PreReg 凍結の中身そのもの・実 Google Form 作成 (= ユーザー操作。schema は最小プレースホルダ追従)。
- **Physical Anchor (Lv3/Lv4 計測) の実装**: Phase 1 は散歩 = WoZ + 自己申告で受容性のみ (D8 決定済)。
  歩数/移動計測の Flutter 連携は**次段フォーク** (受容が肯定的なら着手)。本タスクでは作らない。
- 統計解析・効果量推定 (Phase F 本体) / 可視化ダッシュボード。
- HMM/features/engine ロジック変更・anonymize/replay/gse-package の機能変更 (完了済)。

## 着手前に決めるべき設計判断 (/start-task → 必要なら /reimagine)
1. **decrypt の形態**: Rust bin (`gse-unpack`) に足すか shell/PS ラッパか。研究者側は age CLI 利用可
   (被験者と違い技術者前提)。鍵 (age 秘密鍵) の置き場と扱い (リポジトリに置かない・data-privacy)。
2. **sessions.csv の phase 割当運用**: 全自動化はできない (どの session が pre/post かは研究設計)。
   テンプレ生成 + 手記入 が現実解か。命名規約 (例 metrics 配下のサブディレクトリ) で半自動化するか。
3. **runbook 配置**: `docs/` (永続) か `.steering/`。calibration-smoke-runbook.md は `docs/`。

## 必須プロトコル (CLAUDE.md 準拠)
1. **新規セッションで `/clear`** → `/start-task` → `/add-feature` (runbook 部分は docs 作業として適宜)。
2. docs 先読み: `docs/calibration-smoke-runbook.md` (先例) / `decisions.md` D5・D6 /
   `development-guidelines.md` §10 (gse-dataset 連携) / `bin/package.rs`・`scripts/sync-session.sh`・
   `scripts/build_analysis_db.py` のソース。
3. Skill: `data-privacy` (復号後の平文・生 NDJSON はローカルのみ・外部送信/commit 禁止、鍵を repo に置かない) /
   `git-workflow` / Rust に触れるなら `rust-standards`・`architecture-rules`。
4. file-finder/impact-analyzer で既存 sync スクリプトの I/O 契約・gse-dataset レイアウトを調査。
5. 実装後 `code-reviewer` + (**復号・鍵・個人データを扱うため**) `security-checker` 並列。
6. `/cross-review` (jq 導入済)。7. `/finish-task`。

## 検証ゲート
- 合成 session を `gse-package` → decrypt → `gse-replay --metrics` → `build_analysis_db.py` に通し、
  `cross_section` が生成される (end-to-end 結線確認)。
- 復号後の平文・生 NDJSON・age 秘密鍵が repo / 出力 (DB/CSV) / commit に混入しない (data-privacy)。
- 既存 `cargo test --workspace` / `gse-replay --snapshot` / `emit_schema` parity が不変。

## 制約
- data-privacy 厳守: 生 NDJSON・復号平文を gse-dataset repo に置かない (共有は `metrics.json` のみ)。
  鍵をコミットしない。P-ID のみ・本文/実名非混入。tracing/anyhow/any 禁止 (Rust に触れる場合)。
- `.steering/` 記録必須。別 PR・main 基点。Hook の [guard] に従う。

## 受け入れ条件
- 合成 session が package→decrypt→metrics→join の全段を通り `cross_section` を生成できる。
- 研究者が runbook 通りに被験者データを受領→匿名化 NDJSON→metrics→survey→sessions.csv→analysis.db まで
  迷わず辿れる (被験者向け Dropbox 3 step も記載)。
- 個人識別情報・平文・鍵の非混入。CRITICAL/HIGH なし。

## 補足: 全体の現在地 / 次の研究判断フォーク (ユーザー決定待ち)
- Phase A/B/C コード完了。本タスク = C→F の運用結線。これが済めば Phase F (通しパイロット) は
  **研究設計の決定待ち**になる。新セッションで本タスクより先にこれらを決めたい場合は再指示可:
  - ~~**Phase E 散歩 (Physical Anchor)**~~ → **決定済 (D8)**: Phase 1 は WoZ + 自己申告で受容性のみ。
    Physical Anchor 計測実装は次段。
  - **X/Y セッション設計** (roadmap §5): 同一セッションで取るか分離か / 前後比較設計 (PreReg-5)。
  - **Phase D** (任意・X 強化): context_beacon (波形 cue でなく confound-free cue が先)。
- Phase D/E はパイロットの**ブロッカーではない** (roadmap §4)。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-pipeline-runbook.md に従い、M1 パイロットの
データ収集→分析パイプラインを end-to-end に結線し、Y パイロット運用 runbook を整備してください。
Phase A/B/C のコードは完了済 (#6 DuckDB join = PR #30)。残るは部品の結線。

GAP: ①研究者側 decrypt 経路 (.age→匿名化 NDJSON) が無い ②sessions.csv (phase manifest) 生成手段が無い
③survey/P###.csv 配置規約が未文書 ④Y 通し runbook が無い (X 側 calibration-smoke-runbook.md のみ)
⑤end-to-end 統合スモークが無い。合成 session で実データ非依存に構築・検証する。

/start-task → (設計が非自明なら /reimagine) → /add-feature。先に決める: decrypt の形態 (Rust bin か
shell/PS ラッパ・age CLI 前提・鍵は repo 非格納)・sessions.csv の phase 割当運用 (テンプレ生成+手記入)・
runbook 配置 (docs/ 想定)。docs 先読み: docs/calibration-smoke-runbook.md / decisions.md D5,D6 /
development-guidelines §10 / bin/package.rs・scripts/sync-session.sh・scripts/build_analysis_db.py。
Skill: data-privacy (復号平文/生NDJSON はローカルのみ・鍵を commit しない) / git-workflow。
実装後 code-reviewer + security-checker (復号・鍵・個人データ) 並列 → /cross-review → /finish-task。
制約: data-privacy 厳守・別 PR・main 基点。スコープ外: PreReg 凍結内容・実 Google Form 作成・
Phase E 散歩実装 (別フォーク)・統計解析本体・HMM/anonymize/replay の機能変更。
```
