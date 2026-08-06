# 次セッション開始プロンプト — #6 DuckDB join ハーネス (Phase C / D5)

> `feedback_handoff_prompt_in_steering` 方針に従い CLAUDE.md 制約込みで固定。
> 親: `roadmap-xy.md` Phase C / `decisions.md` D5 / transfer-pipeline (#27) / replay-category (#29)。
> **新規 `/start-task` で着手。main 基点で別ブランチ・別 PR。main 直コミット禁止。**
> **このタスクは新規セッションで `/clear` してから着手すること** (タスク境界 = /clear、CLAUDE.md コンテキスト管理ルール2)。

## なぜこれが次か
Phase C のデータパイプラインは #27 (anonymize→age 暗号化 `gse-package`) → #29 (replay の category 対応・D6
Replay-as-Truth) まで完了。残るコード項目は **#6 DuckDB join ハーネス** = 3 ストリームを participant_id で
結合し (a)(b)(c) を横断分析できるようにする最後の Phase C 実装 (decisions.md **D5**)。実データ (survey) 到着
前でも、**合成 fixture + スキーマで先行構築・テスト可能** (実データ非依存)。これで「収集→算出→結合」が閉じ、
M1 パイロット (n=3-5) の分析基盤が揃う。

## 既に判明している事実 (前セッション調査・取りこぼし防止)
- **D5 の 3 ストリーム (P-ID で結合)**:
  ① セッション NDJSON (高機微・端末ローカル/age 暗号) ②フォーム CSV (低〜中機微・Google Form, channel A) /
  ③ 派生メトリクス `gse-replay --metrics --json` 出力 (`metrics.json`, 集約・唯一の共有アーティファクト)。
- **D5 設計**: サーバ DB 不要規模 (N=3-10)。NDJSON/JSON/CSV を**一次ソース**とし、分析時に DuckDB へ
  読み込んで join。`analysis.db` は**使い捨て** (消せば再生成可)。DuckDB は JSON/CSV/Parquet を直接クエリ可。
- **共有レイアウト** (agent-shared.md §データ repo): 共有は `metrics.json` のみ。
  [mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset) (private) の `metrics/P*/<os>/` に置く。
  本機の clone は `C:\gse-dataset` (HTTPS, memory `reference_gse_dataset_layout`)。**生 NDJSON は repo に置かない**。
- **metrics.json の形**: `src-tauri/src/analysis/metrics.rs` の `SessionMetrics` (L86) / `OutcomeMetrics` (L189)
  を `serde_json` で直列化したもの。`gse-replay <session.ndjson> --metrics --json` で出力。
  (a)=`external_paste_count`/`external_paste_chars_total`、(b)=`manual_contribution_ratio` /
  `productive_manual_recovery_rate` 等。schema は `schema_dto.rs`→`emit_schema` が真実源。
- **survey CSV**: channel A (Google Form) の (c) GSE 自己効力感・NASA-TLX・デモグラ等。pre/post 2 時点、
  participant_id 紐付け (D2/D3)。実名↔P-ID 対応表はデータ本体と物理分離 (D1, 研究者のみ)。
- **未着手の確認**: リポジトリに DuckDB/SQL ハーネスは存在しない (`*.sql` / duckdb スクリプト無し)。
  paste 捕捉は main にマージ済 (`input/clipboard.rs` 他)。`feature/clipboard-paste-count` は残骸ブランチ。

## スコープ
### 含むもの (要・設計フェーズで詰める)
- 3 ストリーム (① replay 由来 metrics.json / ② survey CSV / ③ 必要なら匿名化 NDJSON 再計算 metrics) を
  **participant_id で join** する DuckDB ハーネス。`analysis.db` 再生成可能・使い捨て。
- (a)(b)(c) を 1 つの横断テーブル (P-ID × pre/post × OS × 指標) に落とす SQL/クエリ。
- 合成 fixture (ダミー P-ID 数名分の metrics.json + survey.csv) で end-to-end 検証。実データ不要。
- 出力: 分析用テーブル/ビュー (CSV/Parquet エクスポート or クエリ集)。欠損 P-ID・stream 欠落の扱いを明示。

### 含まないもの
- gse-package / anonymize / replay の変更 (#27/#29 完了)。HMM/features/engine ロジック。
- 実被験者データ収集・Google Form 実体・Dropbox File Request 運用手順書 (= WBS 0.15 運用残務, 別)。
- 統計解析・効果量推定そのもの (Phase F)。可視化ダッシュボード。

## 着手前に決めるべき設計判断 (/start-task → 必要なら /reimagine)
1. **実装言語/形態**: Python (`duckdb` パッケージ + SQL) か、SQL スクリプト + シェルランナーか。
   既存パイプラインは Rust bin だが、本件は「使い捨て分析 DB」(D5) で ad-hoc 分析寄り。
   `scripts/check_schema_parity.py` 等の既存 Python スクリプト流儀との整合を検討。
2. **配置先**: 本 repo `scripts/` か、gse-dataset repo 側か。一次ソースは gse-dataset の `metrics/P*/<os>/`
   だが、ハーネス (コード) は本 repo `scripts/` が自然 (再現性・レビュー対象化)。
3. **survey CSV スキーマの確定**: Google Form の列名が未確定。合成 fixture 用に最小スキーマを仮置きし、
   実フォーム確定時に追従する前提を明記 (PreReg 凍結待ち)。
4. **join キーと粒度**: participant_id × session × pre/post × os。stream 欠落 (survey 未提出等) は
   outer join + 欠損明示 (「実測ゼロ」と「データ無し」を混同しない・#19 の outcome=None 方針と整合)。

## 必須プロトコル (CLAUDE.md 準拠)
1. **新規セッションで `/clear`** → `/start-task` → `/add-feature` (または分析スクリプトなら適宜)。
2. docs 先読み: `roadmap-xy.md` Phase C / `decisions.md` D1-D6 / `development-guidelines §10` (gse-dataset 連携) /
   `architecture.md` のデータフロー (metrics.json 出力経路)。
3. Skill: `data-privacy` (CSV/DB に本文・実名を入れない、P-ID のみ) / 必要なら `git-workflow`。
4. file-finder/impact-analyzer で metrics.rs の SessionMetrics/OutcomeMetrics フィールド・既存 scripts/ の
   Python 流儀・gse-dataset レイアウトを調査。
5. 実装後 `code-reviewer` + (個人データ/CSV/DB を扱うため) `security-checker` 並列。
6. `/cross-review` (jq 導入済)。7. `/finish-task`。

## 検証ゲート
- 合成 fixture で `analysis.db` を生成→破棄→再生成が決定論的 (D5「再生成可能」)。
- join 結果が P-ID × pre/post で正しく揃い、stream 欠落が欠損として明示される (NULL 混同なし)。
- 本文・実名・生 NDJSON が DB/CSV に混入しない (data-privacy)。
- 既存 `cargo test --workspace` / snapshot / emit_schema parity は本タスクで触らないため不変。

## 制約
- data-privacy: P-ID のみ・本文/実名/生 NDJSON 非混入。tracing/anyhow/any 禁止 (Rust に触れる場合)。
- `.steering/` 記録必須。別 PR・main 基点。生 NDJSON を gse-dataset repo に置かない。

## 受け入れ条件
- 合成 fixture で 3 ストリームを participant_id join し (a)(b)(c) 横断テーブルを生成できる。
- `analysis.db` は使い捨てで再生成可能。stream 欠落が欠損として明示される。
- 個人識別情報・本文の非混入。CRITICAL/HIGH なし。

## 補足: プロジェクト全体の現在地 (WBS 準拠)
- Phase A (捕捉 #18/#20) / Phase B (指標 #19) / Phase C パイプライン前半 (#27 anonymize+age / #29 replay D6) 完了。
- 残コード: **本タスク #6 DuckDB join** (これで Phase C のコード完了)。
- 残り運用/文書: PreReg 凍結・Google Form 事後アンケート実体・Dropbox File Request 手順書 (WBS 0.15 残務)・
  blind 品質ルーブリック・Go/No-Go 拡張。M1 Phase 1a (n=3-5 募集・実施) はコードのブロッカー無し。
- Phase E 散歩 (Physical Anchor) は研究設計フォーク (i 実装 / ii WoZ / iii 次段) で要ユーザー判断。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-duckdb-join.md に従い、#6 DuckDB join
ハーネスを実装してください。Phase C 最後のコード項目 (decisions.md D5)。3 ストリーム
(① gse-replay --metrics の metrics.json / ② survey CSV / ③ 必要なら匿名化 NDJSON 再計算) を
participant_id で join し (a)(b)(c) を横断テーブルにする。analysis.db は使い捨て・再生成可能。
実データ到着前でも合成 fixture で end-to-end 構築・検証する。

/start-task → (設計が非自明なら /reimagine) → /add-feature。先に決める: 実装言語 (Python+duckdb か
SQL+runner)・配置先 (本 repo scripts/ 想定)・survey CSV 最小スキーマ・join 粒度 (P-ID×session×pre/post×os,
stream 欠落は outer join + 欠損明示)。docs 先読み: roadmap-xy.md Phase C / decisions.md D1-D6 /
development-guidelines §10。Skill: data-privacy (P-ID のみ・本文/実名/生 NDJSON 非混入)。
実装後 code-reviewer + security-checker 並列 → /cross-review → /finish-task。
制約: data-privacy 厳守・別 PR・main 基点。スコープ外: anonymize/replay 変更・Google Form 実体・
Dropbox 運用手順書・統計解析本体・可視化。
```
