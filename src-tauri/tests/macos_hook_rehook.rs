//! 層 3 (`request_reinstall`) が **実機で実際に発火するか** を確かめる結合テスト。
//!
//! ⚠️★★★ **単体テストでは足りない。** ★ 層 3 の本体は
//! 「`CFRunLoopStop` → `run_current()` が戻る → 既存の tap 再作成経路が走る」であり、
//! ⚠️ これは**本物の run loop が回っていないと 1 行も検証できない**。
//!
//! ⚠️★★ **TCC 権限が要る。** ★ Input Monitoring / Accessibility が無い環境では
//! tap が作れず `HOOK_ACTIVE` が立たない。→ ★ その場合は
//! **「権限が無いので検証していない」と明示して skip する** (⚠️ 緑にして誤魔化さない)。
#![cfg(target_os = "macos")]

use std::sync::atomic::Ordering;
use std::sync::Once;
use std::time::{Duration, Instant};

use gse_next_lib::input::hook;

/// ⚠️★★★ **skip を「緑」と読ませないための門。**
///
/// ★ 2026-09-05 に実測: CI (self-hosted mac) でこの 2 件は **10.5 秒で終わっていた** ——
/// ★ それは `wait_for_hook(true, 10s)` が空振りして skip した時間である。
/// ⚠️ しかも `cargo test` は成功したテストの stdout/stderr を**捨てる**ので、
/// **skip したことがログに残らない**。→ ★ 「CI が緑」を「検証された」と読めてしまう。
///
/// → ★ `GSE_REQUIRE_HOOK_TESTS=1` を立てると **skip を失敗に変える**。
/// ⚠️ 実機で検証したいときは必ずこれを付ける (★ 付けずに緑を見ても何も分かっていない)。
fn skip_or_fail(reason: &str) {
    if std::env::var("GSE_REQUIRE_HOOK_TESTS").as_deref() == Ok("1") {
        panic!(
            "⚠️ GSE_REQUIRE_HOOK_TESTS=1 なのに検証できなかった: {reason}\n\
             ★ Input Monitoring / Accessibility をこのプロセスに付与すること。"
        );
    }
    eprintln!(
        "⚠️ SKIP: {reason}\n         ★ このテストは **何も検証していない**。⚠️ 検証を強制するなら          GSE_REQUIRE_HOOK_TESTS=1 を付けて再実行すること。"
    );
}

/// ⚠️★★★ **フックは 1 プロセスに 1 本だけ立てる。**
///
/// ★ 2026-09-06 に CI (self-hosted mac) が **SIGSEGV** で落ちた。⚠️ 原因は
/// 本ファイルの 2 件が**それぞれ `init_hook` を呼んでいた**こと ——
/// `cargo test` は既定で**並列**に走らせるので、★ **hook スレッドが 2 本**立ち、
/// ⚠️ `TAP_PORT` の「同一スレッドで時間的に排他」という前提が破れる (UAF)。
/// → ★ `init_hook` 側にも門を足したが (`hook.rs`)、**テストも 1 回に絞る**。
static INIT: Once = Once::new();
fn init_hook_once() {
    INIT.call_once(|| {
        let (tx, rx) = crossbeam_channel::unbounded();
        // ⚠️ 受信端を捨てると channel が閉じるので、★ 意図的に漏らして生かしておく。
        std::mem::forget(rx);
        assert!(hook::init_hook(tx), "1 回目は起動するはず");
    });
}

fn wait_for_hook(active: bool, limit: Duration) -> bool {
    let t0 = Instant::now();
    while t0.elapsed() < limit {
        if hook::HOOK_ACTIVE.load(Ordering::Acquire) == active {
            return true;
        }
        std::thread::sleep(Duration::from_millis(100));
    }
    false
}

/// ⚠️★★★ **`None` の 2 つの意味を切り分けるための診断文字列。**
///
/// ★ `hook_reports_enabled()` が `None` を返す理由は **2 つあり、値からは区別できない**:
///
/// | | 意味 | ★ 見分け方 |
/// |---|---|---|
/// | (a) **公開順の穴** | payload がまだ書かれていない | ⚠️ `HOOK_ACTIVE` が **true のまま** |
/// | (b) **tap の実失効** | run loop が抜けて `-1` に倒された | ★ `HOOK_ACTIVE` が **false に落ちている** |
///
/// ⚠️ 2026-09-12 に main の CI が 2 本続けて `left: None` で赤くなったとき、
/// ★ **この 2 つを区別する情報がログに無く**、原因をコード読解で推定するしかなかった。
/// → ★ 次に赤くなったときは**ログだけで決着させる**。
///
/// ⚠️ `watchdog_recoveries()` も併記する: ★ 層 2 が復帰を試みた形跡があれば (b) の裏づけになる。
fn tap_diag() -> String {
    format!(
        "[診断] HOOK_ACTIVE={} (★ true のまま None なら **公開順の穴 (a)**、\
         false なら **tap の実失効 (b)**) / watchdog_recoveries={} \
         (★ 増えていれば層 2 が復帰を試みた = (b) の裏づけ)",
        hook::HOOK_ACTIVE.load(Ordering::Acquire),
        hook::watchdog_recoveries(),
    )
}

#[test]
fn request_reinstall_actually_restarts_the_tap() {
    // ⚠️★★ **「フック未起動なら false」の検査はここに置かない。**
    //   ★ 2 件が並列に走るので、⚠️ **もう一方が先にフックを立てていると偽の赤になる**
    //   (= 順序に依存する検査)。→ ★ その契約は
    //   `input::liveness::tests::request_reinstall_is_callable_without_a_hook` が
    //   **両 OS で**見ている (⚠️ 単体テストは 1 プロセス 1 テストなので順序に依存しない)。
    init_hook_once();

    if !wait_for_hook(true, Duration::from_secs(10)) {
        // ⚠️★★★ **権限が無い環境では検証できない。** ★ 緑にせず、理由を出して skip する。
        skip_or_fail(
            "CGEventTap を作れなかった (Input Monitoring / Accessibility 未付与)。層 3 は未検証",
        );
        return;
    }

    // ★ tap が立っている ＝ 診断は Some(true) を返すはず。
    assert_eq!(
        hook::hook_reports_enabled(),
        Some(true),
        "tap 起動直後は有効のはず {}",
        tap_diag()
    );

    // ★★★ ここが本題: 層 3 を叩くと run loop が抜け、tap が作り直される。
    assert!(
        hook::request_reinstall(),
        "run loop を掴めているなら true を返すはず (⚠️ 定数 false に戻っていないか)"
    );

    // ⚠️ 既存経路は「run loop 退出 → HOOK_ACTIVE=false → 2 秒待って再作成」。
    //   ★ 落ちることと戻ることの**両方**を見る (⚠️ 片方だけだと「何も起きなかった」と
    //   区別が付かない)。
    assert!(
        wait_for_hook(false, Duration::from_secs(5)),
        "⚠️ HOOK_ACTIVE が落ちない = run loop が抜けていない (層 3 が効いていない)"
    );
    assert!(
        wait_for_hook(true, Duration::from_secs(20)),
        "⚠️ 再作成されない = 既存の復帰経路が壊れている"
    );
    assert_eq!(
        hook::hook_reports_enabled(),
        Some(true),
        "再作成後も tap は有効のはず {}",
        tap_diag()
    );
}

/// ⚠️★★★ **陰性対照**: 健全なときに層 2 の watchdog が**余計なことをしない**か。
///
/// ★ watchdog は 3 秒ごとに `CGEventTapIsEnabled` を見る。⚠️ もしここが誤判定すると
/// **健全な tap を 3 秒ごとに再有効化し続ける**ことになり、starvation より質が悪い。
/// → ★ 数周期ぶん回して、再有効化が **1 回も起きない**ことを確かめる。
#[test]
fn watchdog_does_not_touch_a_healthy_tap() {
    init_hook_once();
    if !wait_for_hook(true, Duration::from_secs(10)) {
        skip_or_fail("権限が無く tap を作れない。層 2 は未検証");
        return;
    }
    let before = hook::watchdog_recoveries();
    // ★ WATCHDOG_INTERVAL_S = 3 s なので、12 秒で **4 周期ぶん**回る。
    std::thread::sleep(Duration::from_secs(12));
    assert_eq!(
        hook::hook_reports_enabled(),
        Some(true),
        "★ この間 tap は健全だったはず (⚠️ そうでないと陰性対照にならない) {}",
        tap_diag()
    );
    assert_eq!(
        hook::watchdog_recoveries(),
        before,
        "⚠️ 健全な tap を watchdog が触っている (★ 誤判定 = starvation より質が悪い)"
    );
}

/// ⚠️★★★ **`init_hook` の門が効いているか**（★ 2026-09-06 の SIGSEGV の再発防止）。
///
/// ★ 2 回目の呼び出しが `false` を返し、**hook スレッドを 2 本目にしない**こと。
/// ⚠️ これが破れると `TAP_PORT` の「同一スレッドで時間的に排他」が成り立たず、
/// ★ CI が **SIGSEGV** で落ちる（2026-09-06 に実際に落ちた）。
///
/// ⚠️ **この検査は macOS でしか実行していない。** ★ 門は `hook.rs` の共有コードなので
/// Windows でも同じものが走るが、⚠️ **Windows 実機での実行は未検証**である。
#[test]
fn init_hook_refuses_to_start_a_second_hook() {
    init_hook_once();
    let (tx, rx) = crossbeam_channel::unbounded();
    std::mem::forget(rx);
    assert!(
        !hook::init_hook(tx),
        "⚠️ 2 回目の init_hook が true を返した = hook スレッドが 2 本立つ (★ UAF の入口)"
    );
}
