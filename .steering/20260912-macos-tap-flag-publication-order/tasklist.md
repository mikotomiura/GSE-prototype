# tasklist — macOS 公開フラグの公開順修正

## 調査
- [x] 失敗テスト・アサーション・値を CI ログで特定 (`left: None` ×2 本)
- [x] PR #199 の mac job で同テストが **ok** だったことをログで確認 (= 間欠)
- [x] 手元で 6 回連続実行 → 6/6 成功
- [x] `None` を返す条件を `tap_is_enabled()` の実装で確定 (`TAP_ENABLED_SNAPSHOT == -1`)
- [x] `-1` を書く経路を**全部**列挙 (`:891` / `:1002` / 初期値)
- [x] 公開順が設置時・退出時の**両方**で逆になっていることを特定

## 実装
- [x] 設置時: `HOOK_ACTIVE.store(true)` を snapshot / `TAP_PORT` の**後**へ移す
- [x] 退出時: `HOOK_ACTIVE.store(false)` を payload クリアの**前**に保つ (★ 下ろすのは先)
- [ ] 退出時の `Ordering` を `Relaxed` → `Release` に揃える
- [x] テストに切り分け情報を足す (`HOOK_ACTIVE` 現在値 / `watchdog_recoveries()`)

## 検証
- [x] `cargo clippy --all-targets -- -D warnings` → exit 0
- [x] `cargo clippy --all-targets --features package -- -D warnings` → exit 0
- [x] `cargo test --features package --workspace` → 緑
- [x] ⚠️ `macos_hook_rehook` を**連続 10 回**回して緑 (★ 間欠なので 1 回では足りない)
- [x] ゴールデン byte-equal / schema byte-equal
- [x] ⚠️ `HMM_VERSION` を bump していない

## 記録
- [x] `decisions.md`
- [ ] コミット / PR
- [ ] ⚠️ main の CI が緑に戻ったことを確認 (★ 間欠なので複数 run を見る)
