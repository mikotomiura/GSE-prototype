# requirement — macOS の公開フラグを payload の後に立てる (main の赤を止める)

## 背景

⚠️★★★ **main の CI (`check (gse-mac-selfhosted)`) が赤い。**
★ 2026-09-12 の `mac-default-clippy-green` タスクの完了報告中に発見した (⚠️ 元タスクとは無関係)。

落ちているのは毎回 `tests/macos_hook_rehook.rs::request_reinstall_actually_restarts_the_tap`:

| run | commit | 落ちたアサーション | 値 |
|---|---|---|---|
| 10:51 | `6239d5b` (⚠️ **本件の作業より前**) | 「tap 起動直後は有効のはず」 | `left: None` |
| 11:44 | `e9ceac1` | 「**再作成後も** tap は有効のはず」 | `left: None` |

★ **間欠**である: PR #199 の mac job では **11:35:13 に同テストが ok**、その 9 分後の main run で FAILED。
⚠️ 手元の開発クローンでは **6/6 成功**。

## ★ 根本原因 (コードで特定済み)

★ `hook_reports_enabled()` → `tap_is_enabled()` は `TAP_ENABLED_SNAPSHOT == -1` のときだけ `None` を返す。
⚠️★★★ そして `hook_macos.rs` は **両方向で公開フラグを payload より先に書いていた**:

```
設置時 (:937-951 旧)          退出時 (:993-1002 旧)
  HOOK_ACTIVE = true   ←先      HOOK_ACTIVE = false  ←先
  TAP_ENABLED_SNAPSHOT          TAP_PORT = null
  TAP_PORT                      TAP_ENABLED_SNAPSHOT = -1
```

★ テストは `wait_for_hook(true)` で `HOOK_ACTIVE` を `Acquire` で待ってから snapshot を読む。
⚠️ release/acquire の happens-before は「**フラグより前に書いたもの**」しか運ばないので、
★ **フラグを先に立てると、フラグを見た側が payload の初期値 (`-1`) を読みうる。**

★ これは **PR #191 が `IME_ACTIVE` に対して行った修正と同じ欠陥クラス**である
(⚠️「Release の位置を payload の後へ移す」)。

## ⚠️★★★ ただし原因は 1 つに確定していない

★ `None` は **2 つの状態を区別できない**:

| | 意味 |
|---|---|
| (a) 公開順の穴 | payload がまだ書かれていない (★ 本 PR が直すもの) |
| (b) tap の実失効 | ランナー上で tap が実際に死んだ (⚠️ `:891` / `:1002` が `-1` を書く) |

⚠️ **現状のテストはどちらか言えない。** → ★ **それ自体が直すべき欠陥である。**

## ゴール (受け入れ条件)

1. ★ 設置時・退出時の**両方**で、公開フラグ `HOOK_ACTIVE` が
   payload (`TAP_ENABLED_SNAPSHOT` / `TAP_PORT`) の**後に立ち・先に下りる**こと。
2. ⚠️ テストが失敗したとき、**(a) と (b) を切り分けられる情報**を出すこと
   (★ 具体的には `HOOK_ACTIVE` の現在値・`watchdog_recoveries()` を併記する)。
3. ★ `cargo clippy --all-targets [--features package] -- -D warnings` が **exit 0**。
4. ★ ゴールデンが byte-equal・`cargo test` 緑。
5. ★ **main の CI が緑に戻る**こと (⚠️ 間欠なので 1 回の緑では「直った」と断定しない)。

## スコープ外

- ⚠️ **`HMM_VERSION` は bump しない** (★ `analysis/` に触らない。挙動不変)。
- ⚠️ **テストを skip / ignore にして緑にしない** (★ `skip_or_fail` の門を緩めない)。
- ⚠️ (b) が真因だった場合の**根治はしない** (★ 切り分け情報を出すところまで)。
- ⚠️ Windows 側の `hook_windows.rs` は触らない (★ `HOOK_ACTIVE` は共有だが公開順の穴は macOS 側)。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 修正方針は PR #191 で確立済みの既存イディオム (公開フラグは payload の後) をなぞるだけで、
  設計上の選択肢が無い。
