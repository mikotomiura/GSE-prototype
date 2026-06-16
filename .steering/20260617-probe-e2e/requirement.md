# Task E — 通し検証 (cohort orchestration + 自己ドッグフード→3-5名スモーク)

## 背景

v0.3 較正スモーク (D-14) の実装順 A→(B∥C)→D→**E** の最後。
- A (schema, PR#4 main 済) / B (probe scheduler) / C (frontend collect) / D (オフライン解析
  `calibration_eval` + `gse-replay --calibration`、PR#5) は実装・cross-review 済。
- D の `compute_calibration_metrics` は **1 被験者・複数セッション**を解析する。
  被験者横断ゲート `model_gate(&[f64])` / `measurement_gate(overall, &[f64])` は純関数として
  実装済・合成多被験者で golden test 済。
- E はこれらを **実データで駆動**し、被験者横断 (cohort) の Go/Kill/INCONCLUSIVE を出す層が未実装。
  加えて A+B+C+D 統合アプリの通し動作 (収集→解析) が未検証。

## ゴール

1. 被験者横断 cohort orchestration を実装し、被験者別 metrics を集約して PreReg ゲート
   (`model_gate`/`measurement_gate`) でコホート判定 (Go/Kill/INCONCLUSIVE) を出す cohort レポート (JSON) を生成できる。
2. A+B+C+D 統合アプリをビルドし、実セッション 1 本を記録 → `gse-replay --calibration` で
   metrics.json が出ることを end-to-end 確認 (自己ドッグフード)。
3. 3-5 名スモークの実データを cohort orchestration にかけ PreReg-1..8 ゲート判定。
   PreReg-5 最低要件 (評価セッション≥6/人・ランダムプローブ≥16/人) を満たすか確認し、
   満たさなければ「データ拡充」と正直に報告 (§11 主張限界、無理に Go と言わない)。

## スコープ

### 含むもの
- (1) cohort orchestration コード (D の純関数を再利用。実装形態は要設計)。
- (2) 自己ドッグフード運用 (統合ビルド→1 セッション記録→ replay 解析の通し確認)。
- (3) 3-5 名スモーク運用 → cohort 判定 + PreReg 最終判定。

### 含まないもの
- D の `calibration_eval` 再実装 (compute_calibration_metrics / model_gate / measurement_gate 再利用)。
- 比較条件 (context_beacon/波形 cue)・統制課題 (task_checkpoint)・コーナー介入 UI → Phase 4 以降。
- Recall 点推定・三層対照 → v0.3 では取らない (延期)。
- schema 変更 (A 凍結・`schema_dto.rs` touch しない)。
- 上記 (1)〜(3) 以外の追加。

## 受け入れ条件

- [ ] cohort orchestration が被験者別 metrics を集約し cohort レポート (JSON) を出力する。
- [ ] cohort 判定が `model_gate`/`measurement_gate` (D の純関数) を再利用して算出される。
- [ ] cohort orchestration に golden/単体テストがあり `cargo test --workspace` 緑。
- [ ] `gse-replay --snapshot` 回帰維持・clippy 緑・main ビルド可。
- [ ] 自己ドッグフード: 統合アプリで 1 セッション記録 → replay で metrics.json 生成を確認。
- [ ] PreReg は凍結・変更せず、データが要件未達なら「データ拡充」と正直報告。
- [ ] 作業記録 (requirement/design/tasklist) を `.steering/20260617-probe-e2e/` に残す。

## 関連ドキュメント

- `.steering/20260616-probe-analysis/{requirement,design,decisions}.md` (D 成果・DD-1..DD-9・責務境界)
- `src-tauri/src/analysis/calibration_eval.rs` (compute_calibration_metrics / model_gate / measurement_gate / CalibrationReport)
- `src-tauri/src/bin/replay.rs` (--calibration、load_calibration_session、MAX_CALIBRATION_FILES)
- `docs/preregistration-v0.3.md` (PreReg-1..8・Go/Kill/INCONCLUSIVE 契約・凍結)
- `docs/development-guidelines.md` §10 (gse-dataset 連携: metrics/P*/<os>/*.metrics.json)
- `.idea/GSE_事後ラベリングシステム設計書_v0.3.md` §7 (2段ゲート) / §8 (holdout 最低 eval≥6・probe≥16/人) / §11 (主張限界)

## 運用メモ
- /reimagine 適用: **Yes**
- 理由: cohort orchestration の実装形態に複数案あり (gse-replay `--cohort` サブモード / 独立バイナリ
  `gse-cohort` / Python 集約スクリプト)、入力 (被験者別 metrics.json vs NDJSON ツリー) と
  代表値 (pooled vs session-median) の設計判断も含むため。設計承認 (Step C) 後に /reimagine で 2 案比較。
- ブランチ: `feature/probe-e2e` (起点 = `feature/probe-collect` = A+B+C+D 統合 tip)。main マージは E 完了後。
- 未コミットの infra(Codex bridge)+docs 39 ファイルは E と分離 (放置・選択 add)。
