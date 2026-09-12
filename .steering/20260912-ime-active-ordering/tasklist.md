# タスクリスト: `IME_ACTIVE` の Ordering

- [x] `hook-constraints` 共通-1 / 共通-2 を読む
- [x] mac の 判断 5 / 5b / §8.4 を読む (★ 片側修正の罠)
- [x] 7 箇所を実測で特定
- [x] #1 `hook.rs` `is_ime_active()` → `Acquire`
- [x] #2-#4 `hook_windows.rs` (★ #4 はフックコールバック内)
- [x] #5-#6 `ime_windows.rs`
- [x] #7 `lib.rs`
- [x] 残存 `Relaxed` が 0 件であることを実測
- [x] 回帰テストを追加 (★ `#[cfg]` を付けない / `concat!` で針を割る)
- [x] ⚠️ **変異させて赤になることを実測** (★ 復元後に緑)
- [x] `cargo clippy --all-targets --features package -- -D warnings` exit 0
- [x] `cargo fmt --check`
- [x] `cargo test --workspace` 655 passed / 0 failed
- [x] ゴールデン 6/6 一致 / `emit_schema` byte-equal
- [ ] `code-reviewer` + `security-checker` を並列起動
- [ ] `/cross-review`
- [ ] コミット / PR / CI 緑で merge
