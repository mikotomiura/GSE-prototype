# タスクリスト — Task E (cohort orchestration v2)

## 準備
- [x] 関連する docs / D 成果を読む (Explore で reuse 面を抽出済)
- [x] /reimagine で v1/v2 比較 → v2 採用
- [x] rust-standards / architecture-rules Skill を読む (新規 .rs + 新規バイナリのため)

## 実装 (1) cohort orchestration コード
- [x] `analysis/cohort.rs` 作成: read-model DTO `SubjectCalibrationView` (serde、必要フィールドのみ)
- [x] `analysis/cohort.rs`: 出力型 `CohortReport` + 純関数 `cohort_verdict(...)` (model_gate/measurement_gate 再利用)
- [x] session_median=None 被験者の除外 + notes 記録ロジック
- [x] `analysis/mod.rs` に `pub mod cohort;` 追加
- [x] `bin/cohort.rs` 作成: dataset ツリー走査 (`metrics/P*/<os>/*.calib.json`)・JSON 読込・出力
- [x] `Cargo.toml` に `[[bin]] name="gse-cohort"` 追記
- [x] 走査上限・パスバリデーション (security: ファイル数上限・symlink/深さ・bounded read)

## テスト
- [x] `analysis/cohort.rs` 単体/golden: Go/Kill/INCONCLUSIVE/DataInsufficient 境界 + None/品質除外
- [x] 合成 fixture `tests/fixtures/cohort/*.calib.json` 作成 (D の実 JSON 形に一致)
- [x] 統合: `gse-cohort` を fixture ツリーに通し出力検証 + DTO drift ガード (実 D 出力に結合)
- [x] `cargo test --workspace` パス (157 lib + 12 replay bin)
- [x] `gse-replay --snapshot` 回帰チェック (OK: 15 match)
- [x] clippy 緑 (新規ファイルに warning なし)

## レビュー
- [x] code-reviewer + security-checker 並列実行・指摘対応 (Step G)
- [x] HIGH 指摘への対応 (PreReg-2 per_subject_pass をゲート母数条件に追加)

## ドキュメント
- [x] docs/functional-design.md に cohort 機能を追記 (§2.x+1)
- [x] docs/repository-structure.md に gse-cohort バイナリを追記
- [x] glossary に新用語追加 (コホート判定 / DataInsufficient)

## 自己ドッグフード (2) / スモーク (3) — 運用 (実機・残課題)
- [~] A+B+C+D 統合ビルド: cargo build (Rust) 緑。npm run build / GUI 起動は実機手動 (input OS フック)。
- [ ] 実セッション 1 本記録 → `gse-replay --calibration` で metrics.json 生成確認 (E2E・GUI 実機手動)
- [ ] (実データが揃えば) `gse-cohort` で PreReg-1..8 判定。未達なら「データ拡充」と正直報告
  ※ コード経路は drift ガードテスト + fixture ツリー実行で担保済。実データ収集は運用フェーズ。

## 完了処理
- [ ] /finish-task で /cross-review (Claude code-reviewer ∥ Codex codex-review) 必須
- [x] decisions.md 作成 (E の設計判断 ED-1..ED-7)
- [ ] git commit (選択 add・infra/docs 混在に注意)
