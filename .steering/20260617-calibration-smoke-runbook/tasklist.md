# タスクリスト — calibration-smoke-runbook

## 準備
- [x] logger.default_log_path (raw/P000 固定) / 既存 sync-* / dev-guidelines §10 を調査
- [x] 設計承認 (Step C・helper は .sh のみ)

## 実装
- [x] scripts/run-calibration-cohort.sh (raw/P*→calib.json→cohort、flags、OS判定、NDJSON読むだけ)
- [x] docs/calibration-smoke-runbook.md (env / build / dogfood / smoke / 整理 / 判定 / 共有)
- [x] docs/functional-design.md に runbook ポインタを1行追記

## 検証
- [x] ビルド検証: npm run build 緑 + cargo build --release (gse-replay/gse-cohort) 緑 (5m38s)
- [x] fixtures ドライラン: temp raw/P001,P002 に calib_subject NDJSON を置き helper 実行 →
      metrics/P00x/windows/*.calib.json 生成 + gse-cohort 判定 JSON 出力を確認。
      微小データで「PreReg-5 未達→データ拡充」と honest に判定 (gate 連鎖+正直報告を実証)。
- [~] cargo test --workspace: 製品コード無変更 (src-tauri/src 触らず) のため main の結果 (157+12) と同一・省略。

## レビュー
- [x] code-reviewer (bash 安全性) / security-checker (パス・プライバシー) 実施。Codex は jq 不在でスキップ。
- [x] HIGH 対応: H1 atomic write + 被験者単位 non-fatal。H2 は false positive (gse-cohort 全 verdict exit 0・検証済)。
- [x] 再ドライランで修正後も end-to-end 動作を確認 (data_insufficient 判定・dry-run 表示)。

## 完了処理
- [x] /finish-task: schema parity skip (schema 無変更)
- [ ] git commit (scripts + docs + steering)
- [ ] push / PR
