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

#[test]
fn request_reinstall_actually_restarts_the_tap() {
    // ★ フック未起動なら要求は出せない (⚠️ 嘘をつかない)。
    assert!(
        !hook::request_reinstall(),
        "フック起動前は false のはず (★ 要求を出せていない)"
    );
    assert_eq!(
        hook::hook_reports_enabled(),
        None,
        "tap が無いのに Some を返してはいけない"
    );

    let (tx, _rx) = crossbeam_channel::unbounded();
    hook::init_hook(tx);

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
        "tap 起動直後は有効のはず"
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
        "再作成後も tap は有効のはず"
    );
}

/// ⚠️★★★ **陰性対照**: 健全なときに層 2 の watchdog が**余計なことをしない**か。
///
/// ★ watchdog は 3 秒ごとに `CGEventTapIsEnabled` を見る。⚠️ もしここが誤判定すると
/// **健全な tap を 3 秒ごとに再有効化し続ける**ことになり、starvation より質が悪い。
/// → ★ 数周期ぶん回して、再有効化が **1 回も起きない**ことを確かめる。
#[test]
fn watchdog_does_not_touch_a_healthy_tap() {
    let (tx, _rx) = crossbeam_channel::unbounded();
    hook::init_hook(tx);
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
        "★ この間 tap は健全だったはず (⚠️ そうでないと陰性対照にならない)"
    );
    assert_eq!(
        hook::watchdog_recoveries(),
        before,
        "⚠️ 健全な tap を watchdog が触っている (★ 誤判定 = starvation より質が悪い)"
    );
}
