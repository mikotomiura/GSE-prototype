# タスクリスト

## 準備
- [x] requirement.md / hypotheses.md / 先行 steering / memory を読む
- [x] 関連 Skill (architecture-rules / rust-standards / hook-constraints / typescript-standards / intervention-design) を読む
- [x] overlay 窓のバックエンド制御 (set_overlay_interactive / 窓生成 / debug gate) を調査
- [x] origin/main へ同期 (幾何退避修正の入った版で作業)

## 実装 (計装のみ — 推測修正はしない)
- [x] Rust: `OverlayWindowState` DTO + `debug_overlay_window_state` command を lib.rs に追加
- [x] Rust: `generate_handler!` に登録
- [x] TS: Overlay.tsx に `OVERLAY_DEBUG` ゲート + `auditWindowState(tag)` ヘルパ追加
- [x] TS: 統合 effect の idle / widget / fullscreen 直後に readback 呼び出し (idle は遅延読みも)
- [x] runbook.md (Windows 状態行列手順) を作成

## テスト
- [x] `cargo build --target aarch64-apple-darwin` (macOS path コンパイル) — warning は既存の was_active のみ
- [x] `cargo test --workspace` (回帰なし確認) — 22 passed
- [x] tsc で TS 型チェック (`npx tsc --noEmit`) — exit 0
- [x] (Windows) cfg(windows) path の型チェック — scratch crate で `cargo check --target x86_64-pc-windows-msvc` 成功 (本体最終ビルドは CI)

## レビュー
- [x] code-reviewer + security-checker 並列 — HIGH なし
- [x] /cross-review (Codex 独立レビュー) — H1 (windows 版数不一致) 検出
- [x] HIGH 指摘への対応 — H1 を生ポインタ橋渡しで修正＋scratch crate で Windows 型チェック検証 (decisions D-audit-2)

## 実機計測 (次段・要 Windows)
- [ ] runbook.md の状態行列を Windows 実機で実行・ログ収集
- [ ] H1-H5 を確定/棄却 → 真因に対する修正 → 同 command で回帰番兵化

## 完了処理
- [ ] design.md / decisions.md 最終化
- [ ] git commit (対象ファイルを明示 pathspec で限定)
- [ ] memory `macos-overlay-clickthrough-bug` 更新
