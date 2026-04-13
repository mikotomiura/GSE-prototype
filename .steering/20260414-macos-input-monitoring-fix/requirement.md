# 要件定義: macOS Input Monitoring 権限問題の改善

## 背景

macOS (aarch64) で Input Monitoring 権限が正常に機能せず、キーストローク検知が開始されない。
診断結果: `input_monitoring_granted: false`, `callback_count: 0`, `hook_active: false`。
過去4回の修正（v0.1.8〜v0.1.12）で Windows 側は解決済みだが、macOS の TCC 権限付与が安定しない。

## 根本原因

1. ad-hoc 署名の CDHash がビルドごとに変化し、TCC の権限エントリが新ビルドと不一致
2. `codesign --deep` が Apple 非推奨で、ネスト署名の不整合を引き起こす可能性
3. アップデート後に「チェックを入れ直す」必要があることがユーザーに伝わっていない

## ゴール

1. CI のコード署名品質を向上（`--deep` 廃止 → レイヤード署名）
2. ランタイム診断を拡充し、問題の特定を容易にする
3. フロントエンド UX で CDHash 不一致への具体的な対処法を案内する
4. TCC リセット機能をアプリ内から提供する

## 受け入れ条件

- [ ] CI で `--deep` を使わないレイヤード署名が成功する
- [ ] `get_diagnostics` が `consecutive_tap_failures`, `bundle_path`, `quarantine_present`, `codesign_valid` を返す
- [ ] `reset_input_monitoring` Tauri コマンドが TCC リセット + System Settings 再オープンを行う
- [ ] Dashboard の permission banner が 30s/60s/90s で段階的にトラブルシューティングを表示する
- [ ] バージョンが Cargo.toml / tauri.conf.json で一致する
- [ ] `cargo check` が成功する
