# tasklist

- [x] `hook-constraints` / `verify-before-claiming` Skill を読む
- [x] ★ 原因を一次資料で確定（`hook.rs:346` が定数 false・mac-3 が未実装）
- [x] ★ 手段を grill で確定（層 2 = runloop timer / 層 3 = CFRunLoopStop）
- [x] 層 2: `CGEventTapIsEnabled` FFI ＋ `CFRunLoopTimer` を runloop に載せる
- [x] 層 3: `request_reinstall()` を macOS で実装（`HOOK_RUNLOOP` ＋ `stop()`）
- [x] ⚠️ 既存バグ修正: 「戻り値に関わらず済みにする」→ 出せたときだけ済み・上限 3 回
- [x] 判定を `liveness.rs` の純関数に切り出し、**両 OS で走る**テストを置く
- [x] 診断: Down のログに `tap_enabled` / `watchdog_recoveries`（⚠️ スキーマは変えない）
- [x] `cargo build` / `cargo test --workspace` (547+30+2+1) / ゴールデン 15 件
- [x] `cargo fmt` / clippy（★ 新規警告なし）/ ⚠️ schema drift なし
- [x] ⚠️ **変異 3 種で赤を見た**（★ 緑を信じない）＋ 復元で緑（陰性対照）
- [x] ★ 実機の結合テストで層 3 の発火を確認（⚠️ **CI では skip される** — D5）
- [ ] ⚠️ **本物の starvation での確認は未実施**（★ 自然発生を待つしかない）
- [ ] ⚠️ **Windows 実機での回帰確認は CI 頼み**（★ この Mac では 1 行もコンパイルされない）
