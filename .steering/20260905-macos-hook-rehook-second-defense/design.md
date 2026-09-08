# design — macOS フックの 2 段目の防御

## ★ 現状の構造（⚠️ ここを読み違えると設計を誤る）

★ hook スレッドは `CFRunLoop::run_current()` で **駐車している**。
→ ⚠️ **外のスレッドから触る手段が極端に限られる**。既存の回復は 1 段だけ:

| 段 | どこ | いつ働くか |
|---|---|---|
| 層 1 | `hook_macos.rs` コールバック内 | ★ OS が `TapDisabledByTimeout` / `ByUserInput` を**届けたときだけ** |

⚠️ `hook-constraints` Skill の **mac-3**（「Hook Thread のポーリングループで `tap_is_enabled()`」）は
★ **実装されていなかった**。⚠️ 2026-09-04 の実測で、層 1 は**一度も発火していない**。

## ★ 採った設計（grill で確定）

| 段 | 手段 | ★ どのスレッド | ⚠️ 効かない場合 |
|---|---|---|---|
| **層 2**（新） | runloop に `CFRunLoopTimer` を載せ、3 秒ごとに `CGEventTapIsEnabled` → false なら `CGEventTapEnable(port,true)` | ★ hook スレッド（runloop 上） | ⚠️ **runloop 自体が楽をしている**と timer も発火しない |
| **層 3**（新） | `request_reinstall()` = `CFRunLoop::stop()` → `run_current()` が戻り、**既存の再作成経路**が走る | ★ liveness スレッドから要求 | ⚠️ run loop 停止中の要求は落ちる（★ 次の tick で再試行する） |

★ **層 3 は新しい復帰経路を作らない** —— 既存の `CGEventTap CFRunLoop exited → 2 秒後に再作成`
（★ 既に動いている）を**起こすだけ**。⚠️ 経路を増やすと、どれか 1 つが静かに壊れる。

### ★ なぜ `CFRunLoop::stop()` が安全か
- `CFRunLoop` は crate 側で `Send + Sync`（`core-foundation-0.10.1/src/runloop.rs:29`）
- ★ Apple が「run loop は thread-safe」と明記する数少ない CF 型
- ⚠️ `TAP_PORT` には**触らない**ので、既存の UAF 回避の根拠を壊さない

### ★ 層 2 の安全性は既存の doc と同じ根拠
★ timer callout は `run_current()` 実行中に **hook スレッド自身の上で**走る。
→ ⚠️ 本体（store / null クリア）と**時間的に排他**なので port は生存している。
★ callout 内では `tracing` を呼ばない（`hook-constraints` 共通-1）。記録は Atomic に置き、
**liveness スレッドが読んで**書く。

## ⚠️★★★ ついでに直した既存のバグ

★ `lib.rs` の旧実装:

```rust
if health == Down && !rehook_done_this_episode {
    rehook = request_reinstall();
    rehook_done_this_episode = true;   // ⚠️ 戻り値に関わらず「済み」
}
```

→ ⚠️ macOS では `request_reinstall()` が常に `false`（何もしていない）だったので、
★ **「試したことにして永久に諦める」**動きだった。
→ ★ **要求が実際に出た（true）ときだけ済みにし、出せなければ上限 3 回まで再試行**に変えた。
⚠️ 上限が無いと 1Hz で叩き続ける。判定は `liveness.rs` の**純関数**に出した（両 OS でテスト）。

## ★ 診断（⚠️ NDJSON スキーマは変えない）

★ Down を記録する `tracing::error!` に `tap_enabled` と `watchdog_recoveries` を足した。

| `tap_enabled` | ★ 読み方 |
|---|---|
| `Some(false)` | ★ **tap が disable されている** → 層 2 の担当 |
| `Some(true)` | ⚠️ **disable されていないのに飢えている** → 再有効化では直らない（層 3 の担当） |
| `None` | ⚠️ **その OS では答えられない**（★ Windows は `WH_KEYBOARD_LL` に「有効か」を聞く API が無い）。⚠️ 「無効」ではない |

⚠️ **NDJSON に列を足さない**理由: `schema_dto.rs` を触ると `emit_schema` /
`schema/current.json` / gse-dataset の parity まで波及する。★ 研究者の機械では
`gse-app.log` に出れば「次の 1 回」は決着するので、費用対効果で見送った。
⚠️ 被験者データにも残したくなったら別 PR。

## テスト戦略（⚠️ 3 状態 ＋ 対照 ＋ 変異）

| # | 何 | ★ 結果 |
|---|---|---|
| ① | 純関数 5 件（両 OS で走る・`cfg` で閉じない） | ★ 緑 |
| ② | 契約 3 件（`request_reinstall` / `hook_reports_enabled` / `watchdog_recoveries` がフック未起動で嘘をつかない） | ★ 緑 |
| ③ | **結合**: `request_reinstall()` → `HOOK_ACTIVE` が落ちて**戻る**（★ 本物の run loop が要る） | ★ 緑（2.28 s = 再作成の 2 秒待ちを含む） |
| ④ | ⚠️ **陰性対照**: 健全な tap を層 2 が 12 秒（4 周期）触らない | ★ 緑 |
| ⑤ | **変異 A**: 純関数を旧実装（1 回で諦める）に戻す | ⚠️ **赤 2 件** |
| ⑥ | **変異 B**: `hook_reports_enabled` が `Some(true)` と偽る | ⚠️ **赤** |
| ⑦ | **変異 C**: macOS の `request_reinstall` を定数 `false` に戻す | ⚠️ **赤**（★ 0.20 s ＝ 2 秒待ちが消える＝経路を通っていた証拠） |
| ⑧ | ★ すべて復元後に緑（陰性対照） | ★ 緑 |

⚠️ 権限が無い環境（CI）では ③④ は **`SKIP` を stderr に出して**通す。
★ 「検証していない」と明示する（⚠️ 緑で誤魔化さない）。
