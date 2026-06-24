# 設計判断 (decisions) — duckdb-join-harness

## CD1: 実装形態 = Python + duckdb パッケージ + 埋め込み SQL (ユーザー承認 2026-06-24)
- SQL ファイル + duckdb CLI ランナーではなく、Python スクリプトに SQL を埋め込む。
- 根拠: 既存 `scripts/check_schema_parity.py` の流儀 (stdlib + argparse + unittest) に揃い、
  duckdb CLI バイナリ依存を避け、stdlib unittest で end-to-end テストできる。
- duckdb は `scripts/requirements-dev.txt` に固定 (1.5.4)。解析専用で app バイナリ非依存。

## CD2: キー由来 = ファイルパス (metrics.json 本体に P-ID/os/session/phase は無い)
- participant_id / os / session_id は `metrics/P###/<os>/<stem>.metrics.json` の path から導出。
- pre/post (phase) は metrics に無い → 任意の `sessions.csv` manifest で session→phase を割当。
  manifest 無し/未登録は phase='unknown'。最終 grain = (participant_id, phase)。

## CD3: 欠損の明示 (「実測ゼロ」≠「データ無し」)
- `cross_section` は metrics_agg FULL OUTER JOIN survey。`has_metrics`/`has_survey` BOOLEAN で
  stream 欠落を明示。NULL=データ無し、0=実測ゼロを区別 (#19 outcome=None 方針と整合)。

## CD4: privacy ガードは「列名」ゲート (substring・日英) — fail-closed
- survey CSV ヘッダに PII トークン (`name`/`mail`/`氏名`/`メール` 等) が substring 一致したら exit 6。
- 値ベース PII (自由記述セルの実名等) は検知対象外 = 研究者のオペレーション責任 (D1)。
  ハーネスは早期検知ネットであり唯一の防御線ではない (data-privacy / cross-review L2 文書化)。
- raw/ ・ _keymap/enrollment.csv は glob 構造上読まない (`P*/*/*.metrics.json` / `survey/*.csv` 限定)。

## CD5: cross-review 指摘の解消 (2026-06-24)
- **C1 (HIGH, 両者一致)**: ハードコード `/metrics/` regex が `--metrics-subdir` 非既定値で
  空キーを生みサイレント破壊。→ **path 相対導出 + stdlib json パースに全面置換**して構造的に解消
  (regex/SQL 補間も排除しインジェクション面も縮小)。回帰 T9。
- **C2 (MEDIUM, 両者一致)**: survey の (P-ID, phase) 重複が cross_section を多重化。
  → 重複検出で fail-closed (exit 4)。回帰 T10。
- **L2 (MEDIUM)**: 値ベース PII 未防御 → 責任分担を docstring/decisions に明文化 (上記 CD4)。
- L1 (blacklist 偽陽性)/L3 (close refactor)/L4・X1 (false positive) は対応不要と判断。

## CD6: ブランチ基点 (運用メモ)
- main checkout が無関係 WIP (replay-category tasklist 等) で阻止されたため be85b62
  (feature/replay-category tip / PR #29) 基点で作業。commit は本タスク分のみで隔離されており、
  #29 が main にマージ後 `git rebase main` で be85b62 が落ち本タスク commit のみ残る。
