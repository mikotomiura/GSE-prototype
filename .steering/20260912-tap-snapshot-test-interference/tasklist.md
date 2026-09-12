# tasklist — テスト直列化

## 調査
- [x] 機序の特定 (同一 lib バイナリ・並列・グローバル共有)
- [x] ⚠️ **再現させた**: 40 回中 **7 回** 失敗 (`left: Some(false)`)
- [x] 同型の他テストが無いか確認 (`watchdog_recoveries_starts_at_zero` は
      `WATCHDOG_REENABLES` を書くテストが無いので安全)
- [x] `serial_test` 未導入を確認 (→ 依存を足さない方針)

## 実装
- [x] `hook.rs` に `#[cfg(test)]` の `TAP_SNAPSHOT_TEST_LOCK` を置く
- [x] `hook_macos.rs` の書き換え側テストで取得
- [x] `liveness.rs` の読み側テストで取得 (⚠️ macOS のみ必要だが両 OS で取って害はない)

## 検証
- [x] ⚠️ **再現手順を同じ回数** (40 回 × `--test-threads=8`) → 失敗 **0** を要求
- [x] `cargo clippy --all-targets -- -D warnings` → exit 0
- [x] `cargo clippy --all-targets --features package -- -D warnings` → exit 0
- [x] `cargo test --features package --workspace` → 緑
- [x] ゴールデン / schema byte-equal
- [x] ⚠️ テストの契約を弱めていないこと (3 状態検査が残っているか目視)

## 記録
- [x] decisions.md / コミット / PR
