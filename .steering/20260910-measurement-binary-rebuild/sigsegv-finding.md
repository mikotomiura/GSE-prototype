# ⚠️★★★ v0.1.33 macOS SIGSEGV —— 機序の特定（★ 3 本の独立調査 ＋ 自分の実測）

★ 2026-09-10。★ `.ips` 精読 / コード監査 / 既知事例 の 3 本を独立に走らせ、
★ 要となる主張は**私が自分で grep し直して**裏を取った。

---

## ⚠️★★★ 0. まず自分の訂正 —— **読んでいた crate のバージョンが違った**

★ 私は最初 `core-graphics-0.25.0/src/event.rs` を引いて
「`impl Drop for CGEventTap` が `CFMachPortInvalidate` を呼ぶ」と書いた。⚠️ **これは効かない。**

★ 自分で確かめた一次資料:

```
src-tauri/Cargo.toml:153   core-graphics = { version = "0.24", features = ["highsierra"] }
Cargo.lock                 gse-next -> "core-graphics 0.24.0"
core-graphics-0.24.0 の impl Drop  : CGSRegion (private.rs:22) / VecWrapper (data_provider.rs:131) の 2 件のみ
                                     → ★ CGEventTap に Drop は **無い**
core-graphics-0.24.0 の CFMachPortInvalidate : **0 件**
```

⚠️ **0.25 で追加された安全網が 0.24 には無い。** → ★ **実態は仮説より悪い。**
（★ `Cargo.lock` には 0.25.0 も居るが、それは `tauri-nspanel` 側であって `hook_macos.rs` は 0.24 にリンクする）

★ 教訓: ⚠️ **crate のソースを引くときは `Cargo.lock` で版を先に確かめる。**
★ 「registry に置いてある最新版」を読んで断定した（`verify-before-claiming` ルール 1 の失敗）。

---

## ★ 1. クラッシュの事実（★ `.ips` から・実測のみ）

```
app_version 0.1.33 / EXC_BAD_ACCESS / SIGSEGV
subtype: KERN_INVALID_ADDRESS at 0x0000000000388be2
esr    : (Data Abort) byte read Translation fault
pc     : 0x10346f7f4 = usedImages[0] "gse-next" base 0x102f68000 + imageOffset 5273588
         → ★ cg_event_tap_callback_internal と厳密一致
far    : 0x388be2 / x8 = 0x388bba   ← ★ 差 0x28 (40 バイト)
vmRegionInfo: "0x388be2 is not in any region.  Bytes before following region: 4340970526"
procLaunch 13:04:27.4469 → captureTime 13:42:05.3604 = ★ 2257.9 秒 (37 分 38 秒)
extMods: thread_create / thread_set_state / task_for_pid すべて 0 ＝ ★ 外部注入の痕跡なし
```

★ **スレッドは 32 本。`hook_macos` の runloop は thread 20 の 1 本だけ**
→ ⚠️ 「古い tap の**スレッド**が残っている」説は**否定された**
（★ ただし私が疑ったのは同じ runloop に残った **source** なので、これは別の説である）。

⚠️★★ **`0x388be2` はどの region にも属さない**（★ 「解放済み領域」ではなく**一度もマップされていない**）。
→ ★ **素朴な「解放済み Box を読んだ」だけでは segfault しない**（★ heap ページは残るのでゴミを読むだけ）。
★ 整合するのは: `user_info` が指す **解放済み Box の中身**（`Box<dyn Fn>` ＝ fat pointer）を読み、
それがゴミ値 `0x388bba` になっていて、そこから **+0x28** を読もうとして落ちた、という描像。

⚠️ **未確認**: ★ 逆アセンブルはしていないので「+0x28 のロード命令」は**仮説**。

---

## ★ 2. コードの実測（★ 自分で grep し直した・陽性対照つき）

```
src-tauri/src/ 全体の呼び出し件数
  remove_source / remove_timer / CFRunLoopSourceInvalidate
  / CFRunLoopRemoveSource / CFMachPortInvalidate / CFRunLoopTimerInvalidate : ★ すべて 0 件
  ★ 陽性対照 add_source : 2 / add_timer : 1   ← ★ grep は機能している
API の実在: core-foundation-0.10.1/src/runloop.rs:107 remove_timer / :123 remove_source
  → ⚠️ **無いのではなく、呼んでいない**
```

★ 再作成 1 周（`hook_macos.rs:793-1061`）で**後始末されないもの**:

| ★ 資源 | ★ 生成 | ⚠️ 1 周を抜けるとき |
|---|---|---|
| `CGEventTap`（`callback_ref: Box`） | `:847` | ★ drop ＝ **Box が解放**。⚠️ 0.24 なので invalidate も**されない** |
| `CFRunLoopSource` | `:878` | ⚠️★★★ **runloop から外されない** |
| runloop への source 登録 | `:901 add_source` | ⚠️★★★ **周回ごとに積み上がる** |
| `CFRunLoopTimer`（watchdog） | `:909` | ⚠️ 外されない |
| timer 登録 | `:922 add_timer` | ⚠️ 積み上がる |
| `TAP_PORT` | `:932` | ★ `:981` で null クリア（★ **唯一きちんと後始末されている**） |

⚠️★★★ **timer には逐語の配慮コメントがあるのに（`:912-916`「無効化された runloop に残った
timer を掴む余地が出る」）、source には無い。** ★ しかも **その配慮の結論自体が誤り** ——
`CFRunLoopAddSource` は `kCFTypeSetCallBacks`（**retain する** set）に入れるので、
⚠️ **Rust 側を drop しても runloop からは外れない**。

★ drop 順は宣言の逆＝ `watchdog` → `run_loop` → `loop_source` → **最後に `tap`**。
→ ⚠️ **source を外す機会がコード上に存在しない。**

---

## ★ 3. Apple の一次資料（★ 逐語）

**① 公式の回復手順は「作り直す」ではなく「再有効化する」**

> "If an event tap becomes unresponsive... a `kCGEventTapDisabled` event is passed to the event tap
> callback function. **Event taps may be re-enabled by calling this function.**"
> — `CGEventTapEnable(tap:enable:)` Discussion

→ ⚠️ GSE の「`run_current()` が返ったら作り直す」は Apple の想定と違う。

**② `CFMachPortInvalidate` は source も無効化し、callout 直前に再チェックが入る**（`CFMachPort.c` 逐語）

```c
CF_INLINE void __CFMachPortInvalidateLocked(CFRunLoopSourceRef source, CFMachPortRef mp) {
    ...  CFRunLoopSourceInvalidate(source);  CFRelease(source);
```
```c
CF_PRIVATE void *__CFMachPortPerform(void *msg, ...) {
    __CFLock(&mp->_lock);  Boolean isValid = __CFMachPortIsValid(mp);  __CFUnlock(&mp->_lock);
    if (isValid) { mp->_callout(mp, msg, size, context_info); }
```

→ ★ **invalidate さえされていれば、この再チェックで配送は止まる。**
⚠️★★★ **0.24 では invalidate が 1 度も呼ばれない** ＝ ★ stale 配送は例外ではなく**正常系**。

**③ invalidate しない限り port は永久に valid**（`CFMachPortCreateRunLoopSource` 逐語）

```c
context.info = (void *)mp;  context.retain = CFRetain;  context.release = CFRelease;
mp->_source = CFRunLoopSourceCreate(allocator, order, &context);
```
→ ★ `source → mp` を retain、`mp->_source` が source を強参照 ＝ **CF 内部の retain cycle**。
⚠️ `CFRelease` だけでは切れず、`__CFMachPortDeallocate` は**永久に走らない**。

**④ 定番実装（Hammerspoon）は 4 点セットで外す**

```objc
CFMachPortInvalidate(e->tap);
CFRunLoopRemoveSource(CFRunLoopGetMain(), e->runloopsrc, kCFRunLoopCommonModes);
CFRelease(e->runloopsrc);  CFRelease(e->tap);
```
★ かつ timeout / userInput では**作り直さず `CGEventTapEnable(tap, true)` だけ**。

---

## ★★★ 4. 機序（★ 上の実測だけで組み立てた因果連鎖）

1. 周 N: tap T₁ を作る。★ `user_info` = Box₁ のポインタ。source S₁ を runloop に **add**。
2. OS が tap を無効化 → `run_current()` から復帰 → `TAP_PORT` を null → 2 秒 sleep。
3. ⚠️ ブロック末尾で T₁ が drop → **Box₁ が解放**。★ 0.24 なので **invalidate は呼ばれない**。
4. ⚠️★★★ S₁ は runloop に**残ったまま**。★ retain cycle で `mp₁` は**生存かつ valid**。
5. 周 N+1: T₂ 生成に成功（★ ログの「2 秒後に再作成 → 成功」と一致）。
6. ⚠️ `mp₁` にメッセージが 1 通届く → `__CFRunLoopDoSource1` → `__CFMachPortPerform`
   （★ isValid = **true** なので通過）→ `eventTapMessageHandler` → `processEventTapData`
   → `cg_event_tap_callback_internal(user_info = 解放済み Box₁)` → **deref → SIGSEGV**

★ **`.ips` の faulting stack と 1 対 1 で一致する。**

⚠️ **決めていないこと**: ★ 「無効化された port に**何のメッセージ**が届いたか」は WindowServer 側の
挙動でありコードからは決まらない。★ **決めなくても結論は変わらない** —— ⚠️ 1 通でも届けば落ちる構造。

---

## ⚠️ 5. 副次的に見つかったもの

| # | 場所 | 内容 |
|---|---|---|
| a | `hook_macos.rs:381 tap_is_enabled()` | ⚠️ 非 hook スレッド（liveness）から port を触る。★ 現状は §3-③ の retain cycle で**偶然**無害。⚠️★★★ **0.25 へ上げた瞬間に本物の UAF になる**（Drop が cycle を切るため） |
| b | `hook_macos.rs:532,615,619,626,635,643,650,664` | ⚠️ **コールバック内で `tracing::debug!` を 8 箇所**呼んでいる ＝ `hook-constraints` 共通-1 違反。★ tap の timeout 無効化を誘発しうる（＝ 3 分に 1 回の Down の一因かもしれない・**未検証**） |
| c | timer の蓄積 | ★ N 本 × 3 秒周期で冗長発火。⚠️ UAF ではないがリーク |
| d | `HOOK_RUNLOOP`（`OnceLock`） | ★ **問題なし**（★ `CFRunLoop::get_current()` はスレッドごとに同一。hook スレッドは終了しない）＝ ⚠️ 私が疑った点は**反証された** |
| e | ⚠️ 再作成の頻度 | ★ `request_reinstall`（2026-09-05 に有効化・`liveness.rs` の `MAX_REHOOK_ATTEMPTS_PER_EPISODE`）で ⚠️ **周回数が実運用で増えた** ＝ 露出が増えている |

---

## ★ 6. 直す方向（⚠️ **まだ直していない**・パッチは書かない）

★ `run_current()` の復帰直後（`:981` の隣）で、**`tap` が drop される前に**:

1. `run_loop.remove_source(&loop_source, kCFRunLoopDefaultMode)` ＋ `remove_timer(&watchdog, ...)`
2. `tap.mach_port` に `CFMachPortInvalidate` を自前 extern で呼ぶ（★ `:48-55` に宣言を足す）
3. ⚠️★★★ **順序が本質** —— ★ `tap` は match binding なので**最後に落ちる**。★ 現状の順序では間に合わない。
4. ⚠️ 2 を入れると §5-a が**現実の UAF に昇格する**ので**同時に**塞ぐ
5. ⚠️ **1 と 2 は片方だけでは足りない**（★ 1 だけでは port が valid のまま／2 だけでは cycle 由来のリークが残る）

⚠️ **crate を 0.25 へ上げる案は別タスク**: ★ `CallbackResult` の破壊的変更を伴い、
`tauri-nspanel` との 2 版並存も動く。★ しかも **`remove_source` は 0.25 でも自動化されない**。

---

## ⚠️ 7. まだやっていないこと（★ 「問題なし」と書かないため）

- [ ] ⚠️★★★ **再現していない**（★ tap 失効を意図的に繰り返す陽性対照が要る）
- [ ] ⚠️ **修正していない**（★ `hook-constraints` を読んだうえで・要承認）
- [ ] ⚠️ **v0.1.31 以前でも起きるか未確認**（★ 過去の `.ips` 3 件は `SIGKILL (Code Signature Invalid)` で別物）
- [ ] ⚠️ **被験者影響の評価** —— ★ 落ちると NDJSON が**無言で止まる**（★ 終了ログ無し・tray が消えるだけ）
- [ ] ⚠️ クラッシュしたプロセスは `responsibleProc: "Code"` ＝ ★ **私が nohup で起こしたもの**。
      ⚠️ **被験者の起動経路（Finder / launcher）で同じかは未確認**
