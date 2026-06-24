# タスクリスト

## 準備
- [x] 前タスク steering（design 層2 / blockers B1 / decisions 判断2）を読む
- [x] logger.rs / lib.rs / intervention.rs / ProbeCard / Overlay / Dashboard の該当箇所を読む
- [x] requirement.md / design.md を記入

## 実装 — 1. 再現性確保（デバッグトリガ）
- [x] intervention.rs: `force_nudge_decision` 追加
- [x] lib.rs: `FORCE_NUDGE` static ＋ `force_nudge` コマンド ＋ get_intervention_decision overlay 分岐で消費
- [x] lib.rs: `debug_force_probe(app)` コマンド（probe_triggered emit・有効 ProbeId・窓クランプ）
- [x] lib.rs: invoke_handler に登録
- [x] Dashboard.tsx: debugView gate にプローブ/Nudge デバッグボタン

## 実装 — 2. 誤誘導ラベル是正
- [x] lib.rs: `log_send_error` ヘルパ ＋ `"log channel full"` 6 箇所を置換

## 実装 — 3. consumer 耐障害化 ＋ fail-loud
- [x] logger.rs: `LogStatus` enum ＋ `open_log_target`/`create_file_at`/`temp_fallback_path`
- [x] logger.rs: `SessionLogger::start` を同期 open + フォールバック + sink 縮退に変更（戻り値 4 タプル）
- [x] lib.rs: `run()` で LogStatus を managed state へ ＋ `get_log_status` コマンド ＋ invoke_handler 登録
- [x] Dashboard.tsx: 起動時に get_log_status → Ok 以外で fail-loud バナー
- [x] caller 追従（logger.rs test 2 箇所・lib.rs:1147）

## テスト
- [x] logger.rs: open_log_target フォールバック回帰テスト
- [x] log_send_error の Full/Disconnected 区別テスト
- [x] `cargo test --lib` パス（220 件）
- [x] `gse-replay --snapshot tests/snapshots/minimal.json` 現状一致（HMM 不変確認）
- [x] `cargo fmt` / `cargo clippy`（新規警告なし） / `tsc --noEmit` クリーン

## レビュー
- [x] code-reviewer ＋ security-checker（logger.rs 変更で必須）並列 → HIGH/CRITICAL なし
- [x] 指摘対応: force_nudge 真ワンショット化 / consumer ウィンドウ非対称コメント / 0600・0700 権限 /
      get_log_status catch の fail-loud / debug probe ID 衝突コメント（MEDIUM/LOW を全て対応 or 文書化）
- [x] force_nudge_decision 回帰テスト追加
- [x] /cross-review: Codex パス取得成功（commit 後に `main...HEAD` で実行）。両者一致 HIGH = backend
      debug gate → 対応。Codex HIGH/MEDIUM（temp 衝突・親 dir chmod 副作用・テスト不足）→ 対応。
      計 222 件パス

## 完了処理
- [x] decisions.md 作成（判断1 スコープ / 判断2 ゲート方針 / 判断3 権限）
- [ ] design.md 最終化
- [ ] git commit（feature/phase1-pilot-fixes 継続）
- [ ] 実機 repro / 本番ビルドスモークの依頼（研究者作業）・PR 作成
