# 設計 — duckdb-join-harness (#6 / D5)

## 実装アプローチ

`scripts/build_analysis_db.py` (Python 3.11 + `duckdb` パッケージ + 埋め込み SQL)。
既存 `scripts/check_schema_parity.py` の流儀に合わせる: stdlib + `argparse` + `pathlib` +
型注釈 + `from __future__ import annotations` + docstring + 明示 exit code、テストは
stdlib `unittest`。duckdb は解析専用依存 (`scripts/requirements-dev.txt`、app 非依存)。

DuckDB に「ファイル真実源」(metrics.json / survey.csv / sessions.csv) を読み込み、
`participant_id` (と phase) で **outer join** して横断テーブルを作る。`analysis.db` は
使い捨て (毎回 drop→再生成)。ユーザー承認: 実装形態=Python+duckdb / duckdb は pip 導入 (2026-06-24)。

## データソースと由来 (重要)

`metrics.json` 本体には **participant_id / os / session_id / pre-post が無い**。これらは
**ファイルパス**から来る (`metrics/P###/<os>/<stem>.metrics.json`)。よって path から導出する。

| stream | 場所 | キー由来 | 主な列 |
|---|---|---|---|
| ③ metrics | `<dataset>/metrics/P*/<os>/*.metrics.json` | participant_id/os=path, session_id=filename stem | (a) `outcome.external_paste_count` 等 / (b) `outcome.manual_contribution_ratio` 等 / HMM 精度 |
| ② survey | `<dataset>/survey/*.csv` | 列 `participant_id`, `phase` | (c) `gse_total` (10-40) / `nasa_tlx_total` / demographics |
| manifest | `<dataset>/sessions.csv` (任意) | `participant_id, session_id, os, phase` | session→phase (pre/post) 割当 |

- participant_id/os/session_id は **Python で path 相対導出** (metrics_root に対する相対 parts)。
  ハードコード `/metrics/` regex を使わないため `--metrics-subdir` 任意値で正しく動く
  (cross-review C1 修正)。JSON 本体も stdlib `json` でパース (check_schema_parity.py 流儀)。
- `outcome` は古い metrics.json には無い → `outcome.get(name)` が None → SQL NULL。
- `*.range*.metrics.json` (range 版) は本ハーネスでは除外 ((a)(b) を持たない別経路)。
- survey は (participant_id, phase) で一意必須。重複は fail-closed で exit 4 (cross-review C2 修正)。
- ③ 匿名化 NDJSON 再計算メトリクスは「同形の metrics.json」として同経路で取り込める
  (`--metrics-subdir` で切替)。再計算自体は replay の責務でスコープ外。

## join 粒度とテーブル設計

最終 grain = **(participant_id, phase)**。phase ∈ {pre, post, unknown}。

1. `metrics_per_session` … read_json + path 由来列 (participant_id, os, session_id) を付与。
2. `sessions` … manifest。`metrics_per_session` を (participant_id, session_id, os) で LEFT JOIN
   → phase 付与 (manifest 無し or 未登録 session は phase='unknown')。
3. `metrics_agg` … (participant_id, phase) で集約。
   - 件数系 (paste_count 等) = SUM、比率系 (manual_contribution_ratio 等) = AVG (透明性のため
     `session_count` も併記。重み付けは将来課題としてコメント)。
   - 集約は metrics 行が在る (P,phase) のみに出る (「データ無し」と「実測ゼロ」を混同しない)。
4. `survey` … survey CSV を union。(participant_id, phase) grain。
5. `cross_section` … `metrics_agg` FULL OUTER JOIN `survey` ON (participant_id, phase)。
   - `COALESCE` で participant_id/phase を埋める。
   - `has_metrics` / `has_survey` BOOLEAN で stream 欠落を明示 (NULL=データ無し、0=実測ゼロを区別)。

## 変更対象

### 新規作成するファイル
- `scripts/build_analysis_db.py` — DuckDB join ハーネス本体 (CLI)。
- `scripts/tests/test_build_analysis_db.py` — stdlib unittest E2E。
- `scripts/fixtures/analysis_join/**` — 合成 fixture (P-ID 3名分 metrics/survey/sessions)。
- `scripts/requirements-dev.txt` — `duckdb==1.5.4` (解析専用)。

### 修正するファイル
- なし (既存 Rust / cargo / schema / 他 scripts には触れない)。

## 出力 / CLI

```
python scripts/build_analysis_db.py --dataset C:/gse-dataset --out analysis.db \
    [--export-dir <dir>] [--format csv|parquet|both] [--metrics-subdir metrics]
```
- `analysis.db` (使い捨て) + ビュー (`cross_section`/`metrics_per_session`/`metrics_agg`/`survey`)。
- エクスポート `cross_section.csv` は `ORDER BY participant_id, phase` で決定論安定。
- exit code: 0=OK / 2=dataset 不在 / 3=ストリーム皆無 / 4=引数/IO / 5=duckdb 未導入 (pip hint) /
  6=privacy ガード違反。

## 既存パターンとの整合性

- `check_schema_parity.py`: `from __future__ import annotations` / argparse / pathlib / 明示 exit code /
  `_load_*` private helper / `main(argv)->int` + `sys.exit(main())`。本ファイルも同型。
- テストは `scripts/tests/` に `unittest` (`python -m unittest scripts.tests.test_build_analysis_db`)。

## data-privacy 厳守 (security-checker 対応)

- 取り込むのは metrics.json (集約数値) / survey.csv (P-ID + 尺度得点) / sessions.csv (P-ID メタ) のみ。
- **raw/ ・ _keymap/enrollment.csv (実名↔P-ID) は読まない**。raw/ は走査対象外。
- survey CSV に禁止列 (`name`,`email`,`real_name`,`furigana`,`address`,`phone` 等) があれば
  exit 6 で停止 (実名混入の早期検知)。
- 出力 DB/CSV に本文・実名・生 NDJSON を入れない (数値・P-ID・phase・os のみ)。

## テスト戦略

合成 fixture で end-to-end (実データ不要):
- T1: fixture→`analysis.db` 生成、`cross_section` が (P-ID×phase) で揃う。
- T2: 生成→破棄→再生成で CSV エクスポートが byte-equal (D5「再生成可能」・決定論)。
- T3: survey 欠落 P-ID=`has_survey=false`、metrics 欠落 phase=`has_metrics=false` で欠損明示。
- T4: 実測ゼロ (paste_count=0) と データ無し (NULL) を区別。
- T5: 禁止列入り survey CSV → exit 6 (privacy ガード)。
- T6: duckdb 未導入時 exit 5 hint (import を関数内 try で確認)。

## ロールバック計画

新規ファイルのみ。問題時は `scripts/build_analysis_db.py` 系を削除すれば原状復帰
(既存挙動への影響ゼロ)。`analysis.db` は使い捨てで gitignore 対象。
