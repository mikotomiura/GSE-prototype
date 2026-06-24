# duckdb-join-harness — #6 DuckDB join ハーネス (Phase C / D5)

## 背景

Phase C データパイプラインは #27 (anonymize→age 暗号化 `gse-package`) → #29 (replay の
category 対応 / D6) まで完了。残るコード項目は **#6 DuckDB join ハーネス** = 3 ストリームを
`participant_id` で結合し (a)(b)(c) を横断分析できるようにする Phase C 最後の実装
(`decisions.md` **D5**)。これで「収集→算出→結合」が閉じ、M1 パイロット (n=3-5) の分析基盤が揃う。

実データ (survey) 到着前でも、**合成 fixture + スキーマで先行構築・テスト可能** (実データ非依存)。

親: `roadmap-xy.md` Phase C / `decisions.md` D5 / handoff `handoff-duckdb-join.md`。

## ゴール

合成 fixture で 3 ストリーム
(① `gse-replay --metrics --json` の `metrics.json` / ② survey CSV / ③ 必要なら匿名化 NDJSON
再計算メトリクス) を `participant_id` で join し、(a)(b)(c) を 1 つの横断テーブル
(P-ID × pre/post × OS × 指標) に落とす DuckDB ハーネスを実装する。`analysis.db` は
**使い捨て・再生成可能**。stream 欠落は outer join + 欠損明示 (NULL 混同なし)。

## スコープ

### 含むもの
- 3 ストリームを `participant_id` で join する DuckDB ハーネス (`analysis.db` 使い捨て・再生成可能)。
- (a)(b)(c) を 1 つの横断テーブル/ビュー (P-ID × pre/post × OS × 指標) に落とす SQL/クエリ。
- 合成 fixture (ダミー P-ID 数名分の `metrics.json` + `survey.csv`) で end-to-end 検証。実データ不要。
- 出力: 分析用テーブル/ビュー (CSV/Parquet エクスポート or クエリ集)。
  欠損 P-ID・stream 欠落の扱いを明示。

### 含まないもの
- `gse-package` / `anonymize` / `replay` の変更 (#27/#29 完了)。HMM/features/engine ロジック。
- 実被験者データ収集・Google Form 実体・Dropbox File Request 運用手順書 (WBS 0.15 運用残務, 別)。
- 統計解析・効果量推定そのもの (Phase F)。可視化ダッシュボード。

## 受け入れ条件

- [ ] 合成 fixture で 3 ストリームを `participant_id` join し (a)(b)(c) 横断テーブルを生成できる。
- [ ] `analysis.db` は使い捨てで、生成→破棄→再生成が決定論的 (D5「再生成可能」)。
- [ ] join 結果が P-ID × pre/post で正しく揃い、stream 欠落が欠損として明示される
      (「実測ゼロ」と「データ無し」を混同しない・#19 の outcome=None 方針と整合)。
- [ ] 本文・実名・生 NDJSON が DB/CSV に混入しない (data-privacy)。P-ID のみ。
- [ ] 既存 `cargo test --workspace` / snapshot / `emit_schema` parity は本タスクで触らず不変。
- [ ] CRITICAL/HIGH なし (code-reviewer + security-checker + /cross-review)。

## 既に判明している事実 (調査済 2026-06-24)

- **metrics.json の形**: `src-tauri/src/analysis/metrics.rs` の `SessionMetrics` (L86) を
  serde_json 直列化。`outcome` (Option<OutcomeMetrics>, L189) に (a)(b) が入る:
  (a)=`external_paste_count`/`external_paste_chars_total`/`large_paste_rate` 等、
  (b)=`manual_contribution_ratio`/`productive_manual_recovery_rate` 等。比率は算出不能時 `null`。
  schema は `schema_dto.rs`→`emit_schema` が真実源。
- **既存 Python 流儀** (`scripts/check_schema_parity.py`): stdlib のみ・`argparse`・`pathlib`・
  型注釈・`from __future__ import annotations`・docstring・明示的 exit code。
  テストは **stdlib `unittest`** (`python -m unittest scripts.tests.xxx`)。pytest は未導入。
- **duckdb**: pip 1.5.4 が利用可能だが **未インストール**。app には載らない解析専用依存。
- **共有レイアウト** (decisions.md D5 末尾): `metrics/P###/<os>/` (③), `survey/P###.csv` (②),
  `anonymized/P###/` (①)。本機 clone は `C:\gse-dataset` (HTTPS)。生 NDJSON は repo に置かない。

## 関連ドキュメント

- `.steering/20260619-user-validation-data-collection/decisions.md` D5 (本体) / D1-D7
- `.steering/20260619-user-validation-data-collection/roadmap-xy.md` Phase C
- `.steering/20260619-user-validation-data-collection/handoff-duckdb-join.md` (本タスク handoff)
- `docs/development-guidelines.md` §10 (gse-dataset 連携)
- `src-tauri/src/analysis/metrics.rs` (SessionMetrics / OutcomeMetrics)
- `data-privacy` Skill (P-ID のみ・本文/実名/生 NDJSON 非混入)

## 運用メモ
- /reimagine 適用: No
- 理由: アーキテクチャは D5 で確定済 (DuckDB・ファイル真実源・使い捨て analysis.db・
  outer join + 欠損明示)。設計空間が狭く最良案が自明。残る選択 (実装形態・survey 最小スキーマ)
  は handoff に推奨あり、ユーザー確認で確定する (下記)。
