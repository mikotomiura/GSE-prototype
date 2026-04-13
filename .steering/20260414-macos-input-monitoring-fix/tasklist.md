# タスクリスト

## Phase 1: CI 署名修正
- [ ] ci.yml の `--deep` を廃止しレイヤード署名に変更
- [ ] CDHash ログ出力を追加

## Phase 2: バックエンド診断強化
- [ ] hook.rs に `CONSECUTIVE_TAP_FAILURES: AtomicU32` 追加
- [ ] hook_macos.rs で失敗カウンタをインクリメント/リセット
- [ ] lib.rs の `get_diagnostics()` に拡張フィールド追加
- [ ] lib.rs に `reset_input_monitoring` コマンド追加
- [ ] `invoke_handler` に登録

## Phase 3: フロントエンド UX
- [ ] DiagnosticInfo インターフェース拡張
- [ ] 段階的トラブルシューティング (30s/60s/90s)
- [ ] 診断情報コピーボタン
- [ ] TCC リセットボタン (90s+)

## Phase 4: バージョン同期
- [ ] Cargo.toml → 0.1.16
- [ ] tauri.conf.json → 0.1.16

## 検証
- [ ] cargo check 成功
