// O1 (R3-a) の非打鍵チャネル — macOS 実装。
//
// ★ 実装するもの (ADR-014 D4 の段 1・macOS 分):
//   - **L-c フォーカス遷移**: `NSWorkspace.didActivateApplicationNotification`
//     （TCC 不要。objc2/objc2-app-kit 経由 — Cocoa API は Carbon の `#[link]` パターンでは書けない）
//   - **L-b ポインタ**: 既存の打鍵 tap とは *別* `CGEventTap`
//     （`MouseMoved`/`*Dragged`/`ScrollWheel` のみ。ADR-014 D4 逐語のマスクそのまま）
//   - **`secure_input`**: `IsSecureEventInputEnabled()` を 1Hz で確認、変化時のみ送出
//   - **キーボードレイアウト識別子**: `TISCopyCurrentKeyboardLayoutInputSource`（1回だけ）
//
// ⚠️★★★ ADR-016 D9 前提1（2プロセス同時稼働の実機確認）は 2026-08-24 に macOS 実機で
// ✅ 判定済み（`.steering/20260824-o1-macos-instrument/decisions.md` T1 節）。
//
// ## ⚠️ `buttons` は macOS では常に 0 になる（★ 「忘れている」のではない）
//
// ADR-014 D4 の mac 側マスクは逐語「`MouseMoved`/`*Dragged`/`ScrollWheel`」であり、
// `LeftMouseDown`/`RightMouseDown`/`OtherMouseDown` を含まない。→ ★ **クリック（移動を
// 伴わない押下）は本タップの対象外**であり、[`PointerBin::buttons`] は macOS では
// 恒常的に 0 になる（Windows は Raw Input の `usButtonFlags` で押下を直接数える非対称）。
// → ★ 研究者へ返す事項（`decisions.md` 判断2 参照）。

use std::ffi::c_void;
use std::ptr::NonNull;
use std::sync::atomic::{AtomicPtr, AtomicU32, AtomicU64, Ordering};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use core_foundation::base::TCFType;
use core_foundation::mach_port::CFMachPortRef;
use core_foundation::runloop::{kCFRunLoopDefaultMode, CFRunLoop};
use core_graphics::event::{
    CGEvent, CGEventTap, CGEventTapLocation, CGEventTapOptions, CGEventTapPlacement, CGEventType,
    EventField,
};

// `CGEventTapEnable`: core-graphics クレートは tap 実体無しの再有効化 API を公開していないため、
// `hook_macos.rs` と同じ理由で自前宣言する（無通知失効からの即再有効化用）。
#[link(name = "CoreGraphics", kind = "framework")]
extern "C" {
    fn CGEventTapEnable(tap: CFMachPortRef, enable: bool);
}

use block2::RcBlock;
use objc2::MainThreadMarker;
use objc2_app_kit::{NSWorkspace, NSWorkspaceDidActivateApplicationNotification};
use objc2_foundation::{NSNotification, NSOperationQueue};

use crate::analysis::pointer_bin::{PointerAccum, PointerBin};

use super::{FOCUS_TX, OBSERVATIONS_DROPPED, POINTER_TX, SECURE_INPUT_TX};

/// ★ macOS では両方とも実装がある（ADR-013 D1 の自己刻印に使う）。
pub const FOCUS_AVAILABLE: bool = true;
pub const POINTER_AVAILABLE: bool = true;
/// ★ macOS には `secure_input` の計器がある（`IsSecureEventInputEnabled`）。
pub const SECURE_INPUT_AVAILABLE: bool = true;

/// ビンの長さ。★ ADR-014 D4 の L-b 仕様（**1 秒固定ビン**・Windows 側と同じ）。
const BIN_MS: u64 = 1000;

fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

// ---------------------------------------------------------------------------
// L-c: フォーカス遷移 (NSWorkspace 通知)
// ---------------------------------------------------------------------------

/// `NSWorkspace.didActivateApplicationNotification` を購読する。
///
/// ## ⚠️★★★ 通知オブジェクトから何も読まない
///
/// ★ ブロックの引数 `NonNull<NSNotification>` は**受け取るが中身を一切読まない**
/// （`userInfo`/`object` を問い合わせない）。送るのは **`u64` の時刻 1 個だけ**である
/// （`FOCUS_TX` の型がそれしか運べない形にしてある）。
///
/// ## ⚠️ Objective-C オブジェクトを `forget` する理由
///
/// ★ `workspace`/`center`/`queue`/`block`/`observer_token` はプロセス寿命ぶん
/// 購読を維持する（★ フックスレッドが「戻らない」のと同じ作法・cleanup 不要）。
/// ⚠️ 通常どおり drop すると `release` が呼ばれ、`NSOperationQueue`/block の生存が
/// 保証できなくなる。⚠️★★★ これらの型は `Send`/`Sync` を持たない
/// （`NSWorkspace` 等）ため `static` に格納できず、**`mem::forget` で解放を止める**
/// のが最小のリスクで意図を達成する手段である。
///
/// ## ⚠️ hook-constraints
///
/// ★ ブロック本体は Atomic と `try_send` のみ（コールバック内の制約と同じ精神）。
fn install_focus_observer() {
    let workspace = NSWorkspace::sharedWorkspace();
    let center = workspace.notificationCenter();
    // ★ 通知ブロックはメインスレッド (Tauri の `setup()`) を塞がないよう、
    //   専用の背景 `NSOperationQueue` で実行する。
    let queue = NSOperationQueue::new();

    let block: RcBlock<dyn Fn(NonNull<NSNotification>)> =
        RcBlock::new(|_notification: NonNull<NSNotification>| {
            if let Some(tx) = FOCUS_TX.get() {
                if tx.try_send(now_ms()).is_err() {
                    OBSERVATIONS_DROPPED.fetch_add(1, Ordering::Relaxed);
                }
            }
        });

    // SAFETY: `block` は捕捉する状態を持たず（`FOCUS_TX`/`OBSERVATIONS_DROPPED` は
    // グローバル static）、任意のスレッド・任意の回数呼ばれても安全である。
    // `queue` を渡しているので、呼び出し元スレッド (ここではフォーカス遷移をポストする
    // OS 側スレッド) を塞がない。
    let observer_token = unsafe {
        center.addObserverForName_object_queue_usingBlock(
            Some(NSWorkspaceDidActivateApplicationNotification),
            None,
            Some(&queue),
            &block,
        )
    };

    // ★ 上記コメントの通り、プロセス寿命ぶん解放しない (意図的な forget)。
    std::mem::forget(workspace);
    std::mem::forget(center);
    std::mem::forget(queue);
    std::mem::forget(block);
    std::mem::forget(observer_token);

    tracing::info!("O1: NSWorkspace focus-transition observer installed");
}

// ---------------------------------------------------------------------------
// L-b: ポインタ (既存の打鍵 tap とは別 tap)
// ---------------------------------------------------------------------------

/// ★ tap コールバックから積む生カウンタ（Atomic のみ・`hook-constraints` 準拠）。
///
/// ⚠️ `PointerAccum` を直接コールバックに置かない —— ★ 通常のフィールドは
/// Atomic ではないため、複数のコールバック呼び出し間でのデータ競合になる。
static POINTER_ABS_DELTA_SUM: AtomicU64 = AtomicU64::new(0);
static POINTER_WHEEL_TICKS: AtomicU32 = AtomicU32::new(0);

/// ポインタ tap の**生存信号**（★ 単調増加）。
///
/// ⚠️★★★ ゼロ抑制と組み合わさると「マウスを触っていない」と「tap が黙って死んだ」が
/// ログ上まったく区別できなくなる —— ADR-013 が「2 件起きた」と書いている失敗類型
/// そのもの（`hook.rs::CALLBACK_COUNT` と同じ役割）。診断用に公開しておく。
static POINTER_CALLBACK_COUNT: AtomicU64 = AtomicU64::new(0);

/// 現在有効なポインタ tap の mach port。★ `hook_macos.rs::TAP_PORT` と同じ作法
/// （無通知失効 (`TapDisabledByTimeout`/`ByUserInput`) からの即再有効化用）。
/// ⚠️ O1 は数日〜数週間走るため、tap が 2 系統になると無通知失効も 2 倍起きうる
/// （引き継ぎ文書 §2 T2 の指摘）。
///
/// ⚠️★★★ **null クリアする経路は無い。** ★ 安全な理由は「tap が生きている間だけ
/// 非 null」ではなく、[`run_pointer_loop`] が **戻らない**ため、設置に使った
/// `CGEventTap`（`try_install_pointer_tap` 内で `mem::forget` 済み）が
/// **プロセス終了まで有効な mach port を指し続ける**ことにある
/// （`hook_macos.rs::TAP_PORT` の doc と同じ論法・code-reviewer L3 指摘の是正）。
/// ⚠️ 将来「tap 完全失効時の作り直し」（decisions.md 判断4 の (b)）を実装するときは、
/// 作り直す**前に必ず null store** すること（`hook_macos.rs:780/848` と同じ不変条件）。
static POINTER_TAP_PORT: AtomicPtr<c_void> = AtomicPtr::new(std::ptr::null_mut());

/// 直近で normal イベントを 1 件も挟まずに連続して tap 再有効化した回数。
///
/// ★ `hook_macos.rs::CONSECUTIVE_REENABLES` と同じスラッシング防止
/// （病的ケースでカーネルが即再 disable し続けたときに無限に再有効化を試みない）。
static POINTER_CONSECUTIVE_REENABLES: AtomicU32 = AtomicU32::new(0);
/// `POINTER_CONSECUTIVE_REENABLES` の上限。★ `hook_macos.rs::MAX_CONSECUTIVE_REENABLES` と同値。
const MAX_CONSECUTIVE_REENABLES: u32 = 100;

/// ⚠️★★★ **スラッシング上限に達し、再有効化を諦めたことを外側ループへ伝える信号**。
///
/// ★ cross-review (Claude+Codex 一致 HIGH・2026-08-24) で発見: 上限到達後はコールバックが
/// 「何もせず return」するだけで、`run_pointer_loop` 側の `pointer_ok` を `false` に戻す経路が
/// 無かった —— ★ **外側の backoff-retry ループ（`pointer_ok == false` のときだけ動く）が
/// 永久に発火せず、`pointer_bin` がプロセス再起動までサイレントに死に続ける**バグだった
/// （`capabilities.config_gated()` は `pointer_bin` を宣言し続けるため、ADR-013 D1
/// 「計器が無いなら自己申告する」の趣旨に反する「黙って動かない計器」になっていた）。
static POINTER_TAP_GAVE_UP: std::sync::atomic::AtomicBool =
    std::sync::atomic::AtomicBool::new(false);

/// 相対 delta の絶対値和を求める（★ 純関数・callback とテストの両方が使う）。
///
/// ⚠️★★★ 符号は**足す前**に落とす（`unsigned_abs`）。★ Windows 側
/// `observe_windows.rs::accumulate_from_buffer` と同じ精神。
fn fold_delta(dx: i64, dy: i64) -> u64 {
    dx.unsigned_abs().saturating_add(dy.unsigned_abs())
}

/// 1 秒ビンを組み立てる（★ 純関数・callback の外に切り出してテストできる形にする）。
///
/// ⚠️★★★ **macOS では `button_presses` を常にリテラル `0` で渡す** ——
/// ADR-014 D4 の mac 側マスクに `*MouseDown` が無いため、本 tap にはボタン押下の
/// ソースがそもそも存在しない（モジュール doc 参照）。
fn build_pointer_bin(delta_sum: u64, wheel_ticks: u32, timestamp: u64) -> PointerBin {
    PointerAccum {
        abs_delta_sum: delta_sum,
        button_presses: 0,
        wheel_ticks,
    }
    .close(timestamp)
}

/// ポインタ tap のコールバック本体。
///
/// ## ⚠️★★★ ここで捨てているもの
///
/// - **絶対座標** …… `CGEventGetLocation` を**呼ばない**（ADR-014 D4 段1の禁止表）
/// - **どちらのボタンでドラッグしたか** …… `MOUSE_EVENT_BUTTON_NUMBER` を読まない
/// - **ホイールの向き・刻み幅** …… 呼ばれた回数だけを 1 として数える
///
/// ⚠️ `buttons`（クリック押下）は本 tap のマスクに `*MouseDown` が無いため
/// **恒常的に 0** になる（モジュール doc 参照・ADR-014 D4 逐語のマスクそのまま）。
fn pointer_event_callback(event_type: CGEventType, event: &CGEvent) {
    // ★ `hook_macos.rs::handle_event` の F4 修正と同じ扱い: 無通知失効を検知したら
    //   作り直さず即再有効化する。CGEventType は PartialEq 未実装のため matches! で判定。
    if matches!(
        event_type,
        CGEventType::TapDisabledByTimeout | CGEventType::TapDisabledByUserInput
    ) {
        // ⚠️★★★ スラッシング防止（code-reviewer MEDIUM-1）: 病的ケース（カーネルが
        //   有効化しても即再 disable し続ける）で再有効化を無限に繰り返さない。
        let n = POINTER_CONSECUTIVE_REENABLES.fetch_add(1, Ordering::Relaxed);
        if n < MAX_CONSECUTIVE_REENABLES {
            let port = POINTER_TAP_PORT.load(Ordering::Acquire);
            if !port.is_null() {
                // SAFETY: port は `try_install_pointer_tap` が設置直後に格納した値であり、
                // その tap は `mem::forget` 済みでプロセス終了まで生存する
                // （`POINTER_TAP_PORT` の doc 参照）。CGEventTapEnable は Apple 推奨の
                // 軽量な再有効化呼び出しで、ブロッキング I/O・アロケーション・ログを伴わない。
                unsafe {
                    CGEventTapEnable(port as CFMachPortRef, true);
                }
            }
        } else {
            // ⚠️★★★ cross-review HIGH の是正: 諦めたことを外側ループへ伝える
            //   （Atomic のみ・コールバック内の制約を満たす）。
            POINTER_TAP_GAVE_UP.store(true, Ordering::Relaxed);
        }
        return;
    }

    // normal イベント到達 = tap 健全 → 連続再有効化カウンタをリセットし、生存信号を進める。
    POINTER_CONSECUTIVE_REENABLES.store(0, Ordering::Relaxed);
    POINTER_CALLBACK_COUNT.fetch_add(1, Ordering::Relaxed);

    match event_type {
        CGEventType::MouseMoved
        | CGEventType::LeftMouseDragged
        | CGEventType::RightMouseDragged
        | CGEventType::OtherMouseDragged => {
            // ⚠️★★★ 読むのは**相対** delta のみ（「前回の移動イベントからの差分」）。
            //   `CGEventGetLocation`（絶対座標）は一度も呼ばない。
            let dx = event.get_integer_value_field(EventField::MOUSE_EVENT_DELTA_X);
            let dy = event.get_integer_value_field(EventField::MOUSE_EVENT_DELTA_Y);
            POINTER_ABS_DELTA_SUM.fetch_add(fold_delta(dx, dy), Ordering::Relaxed);
        }
        CGEventType::ScrollWheel => {
            // ★ Windows 側 (`add_wheel`) と同じ精神: 向きは見ない。回数だけ。
            POINTER_WHEEL_TICKS.fetch_add(1, Ordering::Relaxed);
        }
        _ => {}
    }
}

/// `secure_input` を送るべきか（★ 純関数・テストできる形に切り出す）。
///
/// ⚠️★★★ **変化したときだけ `true` を返す。** ★ 毎秒ポーリングしても、
/// 状態が変わらない限り行を出さない（ADR-014 D4 段1「区間フラグ」の実体）。
/// ★ 初回（`last` が `None`）は常に送る（★ 起動直後の状態を確定させる必要がある）。
fn secure_input_should_emit(last: Option<bool>, current: bool) -> bool {
    last != Some(current)
}

/// リトライ間隔（★ `hook_macos.rs` の tap 再作成バックオフと同じ 3 段階）。
fn pointer_tap_retry_backoff(consecutive_failures: u32) -> Duration {
    match consecutive_failures {
        0..=4 => Duration::from_secs(2),
        5..=19 => Duration::from_secs(5),
        _ => Duration::from_secs(10),
    }
}

/// ポインタ tap を 1 回だけ作って設置を試みる。
///
/// ⚠️★★★ 成功したら `tap` を `mem::forget` する —— ★ `run_pointer_loop` は戻らないので
/// 本来 drop されないが、本関数はそのループより**内側のスコープ**（呼び出しごとに
/// 戻る）なので、`forget` しないと関数を抜けた瞬間に tap が release されてしまう。
fn try_install_pointer_tap(run_loop: &CFRunLoop) -> bool {
    let tap = CGEventTap::new(
        CGEventTapLocation::Session,
        CGEventTapPlacement::HeadInsertEventTap,
        CGEventTapOptions::ListenOnly,
        vec![
            CGEventType::MouseMoved,
            CGEventType::LeftMouseDragged,
            CGEventType::RightMouseDragged,
            CGEventType::OtherMouseDragged,
            CGEventType::ScrollWheel,
        ],
        |_proxy, event_type, event| {
            pointer_event_callback(event_type, event);
            None
        },
    );

    let Ok(tap) = tap else {
        return false;
    };
    let Ok(source) = tap.mach_port.create_runloop_source(0) else {
        return false;
    };
    // SAFETY: `kCFRunLoopDefaultMode` は CoreFoundation 定数。常に有効。
    run_loop.add_source(&source, unsafe { kCFRunLoopDefaultMode });
    tap.enable();
    // ★ callback (TapDisabledByTimeout/ByUserInput) から即再有効化できるよう
    //   mach port を公開する（`hook_macos.rs::TAP_PORT` と同じ作法）。
    POINTER_TAP_PORT.store(
        tap.mach_port.as_concrete_TypeRef() as *mut c_void,
        Ordering::Release,
    );
    POINTER_CONSECUTIVE_REENABLES.store(0, Ordering::Relaxed);
    // ★ 上記 doc の通り、本関数のスコープを抜けても tap を生かし続ける意図的なリーク。
    std::mem::forget(tap);
    true
}

/// ポインタ tap を設置し、1 秒ビンを閉じて送り続ける。
///
/// ⚠️★★★ **既存の打鍵 tap (`hook_macos.rs`) とは別スレッド・別 tap である。**
/// 相乗りさせると打鍵観測を巻き込んで失効する（ADR-014 D4 / `data-privacy` ルール7）。
fn run_pointer_loop() {
    let run_loop = CFRunLoop::get_current();

    let mut pointer_ok = try_install_pointer_tap(&run_loop);
    if pointer_ok {
        tracing::info!("O1: pointer tap installed (macOS, separate from keystroke tap)");
    } else {
        tracing::warn!("O1: pointer CGEventTap installation failed, will retry with backoff");
    }

    let mut bin_started = Instant::now();
    let mut last_secure: Option<bool> = None;
    let mut last_secure_poll = Instant::now();
    let mut last_install_attempt = Instant::now();
    let mut consecutive_install_failures: u32 = 0;

    loop {
        // ⚠️★★★ cross-review HIGH の是正: スラッシング上限に達して再有効化を諦めた
        //   ことをコールバックから受け取り、`pointer_ok` を `false` に戻す。
        //   ★ ここで戻さないと、下の `if pointer_ok` が永久に `run_in_mode` 分岐を選び続け、
        //   外側の backoff-retry（`else` 分岐）が二度と発火しない
        //   （＝ tap がプロセス再起動まで無音で死に続ける）。
        if POINTER_TAP_GAVE_UP.swap(false, Ordering::Relaxed) {
            tracing::warn!(
                "O1: pointer tap gave up re-enabling after {} consecutive failures; \
                 will recreate it from scratch with backoff",
                MAX_CONSECUTIVE_REENABLES
            );
            pointer_ok = false;
            last_install_attempt = Instant::now();
        }

        if pointer_ok {
            // ★ run loop を短時間ポンプする (tap のコールバックはここで駆動される)。
            //   Windows 側 (`PeekMessageW` + 5ms sleep) と同じ精神の粒度。
            CFRunLoop::run_in_mode(
                unsafe { kCFRunLoopDefaultMode },
                Duration::from_millis(100),
                false,
            );
        } else {
            // ⚠️★★★ security-checker 実測 (H1): source を 1 つも持たない run loop で
            //   `CFRunLoopRunInMode` を呼ぶと、タイムアウトを待たず即座に返り**ビジーループ**
            //   になる（spawned thread で 500ms あたり ~2.9M 反復を実測）。
            //   → ★ tap が無い間は run loop を回さず、素直に sleep で待つ。
            thread::sleep(Duration::from_millis(100));
            if last_install_attempt.elapsed()
                >= pointer_tap_retry_backoff(consecutive_install_failures)
            {
                last_install_attempt = Instant::now();
                pointer_ok = try_install_pointer_tap(&run_loop);
                if pointer_ok {
                    tracing::info!(
                        "O1: pointer tap installed (macOS, after {} failed attempt(s))",
                        consecutive_install_failures
                    );
                    consecutive_install_failures = 0;
                } else {
                    consecutive_install_failures = consecutive_install_failures.saturating_add(1);
                }
            }
        }

        // ── ★ 1 秒ビンを閉じる ───────────────────────────────────
        if bin_started.elapsed() >= Duration::from_millis(BIN_MS) {
            let delta_sum = POINTER_ABS_DELTA_SUM.swap(0, Ordering::Relaxed);
            let wheel_ticks = POINTER_WHEEL_TICKS.swap(0, Ordering::Relaxed);
            bin_started = Instant::now();
            let bin = build_pointer_bin(delta_sum, wheel_ticks, now_ms());
            // ⚠️★★★ **ゼロ抑制** (ADR-014 D5): 何も起きていない秒は行にしない。
            if !bin.is_empty() {
                if let Some(tx) = POINTER_TX.get() {
                    if tx.try_send(bin).is_err() {
                        OBSERVATIONS_DROPPED.fetch_add(1, Ordering::Relaxed);
                    }
                }
            }
        }

        // ── ★ secure_input を 1Hz で確認し、変化したときだけ送る ─────
        if last_secure_poll.elapsed() >= Duration::from_secs(1) {
            last_secure_poll = Instant::now();
            if let Some(on) = secure_input_enabled() {
                if secure_input_should_emit(last_secure, on) {
                    if let Some(tx) = SECURE_INPUT_TX.get() {
                        // ⚠️★★★ code-reviewer HIGH-1 の是正: **送信が成功したときだけ**
                        //   `last_secure` を進める。先に進めると、`try_send` が失敗した瞬間
                        //   その遷移が永久に失われる —— `secure_input` は edge-encoded な
                        //   区間フラグなので、1 本落ちると以降の区間解釈が全部反転する
                        //   （`focus`/`pointer` の 1 サンプル欠落とは壊れ方の質が違う）。
                        if tx.try_send(on).is_ok() {
                            last_secure = Some(on);
                        } else {
                            OBSERVATIONS_DROPPED.fetch_add(1, Ordering::Relaxed);
                            // ★ `last_secure` は進めない → 次の 1Hz tick で再送を試みる。
                        }
                    }
                }
            }
        }
    }
}

/// O1 観測を開始する。
///
/// ★ フォーカス観測はこの呼び出しスレッド (Tauri `setup()` = メインスレッド) で
/// 同期的に登録する（★ NSWorkspace 通知の購読自体はメインスレッド限定ではないが、
/// 呼ばれる場所がそうなので自然にそこで行う）。ポインタ tap + `secure_input` ポーリングは
/// 専用スレッドを起こして即座に返る（★ `init_hook`/`observe_windows::start` と同じ作法）。
///
/// ⚠️★★★ **2 回目以降の呼び出しは無視される**（security-checker LOW-L2・二重起動ガードは
/// `observe.rs::start()` 側にある）。★ 二重に呼ぶと `NSWorkspace` observer と `CGEventTap`
/// が二重に設置され、同じ `POINTER_ABS_DELTA_SUM` を 2 つの tap が加算して `moved` バケットが
/// 水増しされる（`focus_transition` も 2 行ずつ出る）。
pub fn start() {
    install_focus_observer();
    thread::Builder::new()
        .name("gse-o1-pointer".to_string())
        .spawn(run_pointer_loop)
        .expect("failed to spawn O1 pointer observation thread");
}

// ---------------------------------------------------------------------------
// キーボードレイアウト識別子
// ---------------------------------------------------------------------------

#[allow(non_camel_case_types)]
type TISInputSourceRef = *const c_void;
#[allow(non_camel_case_types)]
type CFStringRef = *const c_void;

#[link(name = "Carbon", kind = "framework")]
extern "C" {
    // ⚠️★★★ ADR-014 D4 逐語が指定しているのは *Layout* 版。
    //   `ime_macos.rs` の `TISCopyCurrentKeyboardInputSource`（＝入力ソース = IME）とは別 API。
    //   欲しいのは**物理配列**（`com.apple.keylayout.US` 等）である。
    fn TISCopyCurrentKeyboardLayoutInputSource() -> TISInputSourceRef;
    fn TISGetInputSourceProperty(source: TISInputSourceRef, key: CFStringRef) -> *const c_void;
    #[allow(non_upper_case_globals)]
    static kTISPropertyInputSourceID: CFStringRef;
    // `secure_input_enabled` 用 (下記)。
    //
    // ⚠️★★★ security-checker L1: 戻り値は Rust `bool` ではなく `u8` で受ける。
    //   ★ Carbon の宣言は `Boolean IsSecureEventInputEnabled(void)` で、
    //   `Boolean` は `typedef unsigned char`（C99 `_Bool` ではない）。
    //   ⚠️ Rust の `bool` は 0/1 以外のビットパターンを持つと**未定義動作**になるため、
    //   `Boolean` を直接 `bool` として受けるのは構造的に危険（値が 1 であることを
    //   OS の実装詳細に賭けることになる）。★ `u8` で受けて `!= 0` に正規化する。
    fn IsSecureEventInputEnabled() -> u8;
}

/// キーボードレイアウトの識別子（例 `com.apple.keylayout.US`）。
///
/// ⚠️★★★ **`UCKeyTranslate` を呼ばない。** ★ 呼んだ瞬間に**入力文字そのものが
/// プロセス内に出現する**（`data-privacy` ルール1の一線）。
///
/// ## ⚠️★★★ `dispatch_sync_f` を使わない（★ 2026-08-24 に実機クラッシュで判明）
///
/// ★ 唯一の呼び出し元は `lib.rs` の `setup()` であり、Tauri の `setup()` クロージャは
/// **メインスレッド**で（`did_finish_launching` から）同期的に呼ばれる。
/// ⚠️★★★ **実機で `dispatch_sync_f` を使ったところ、メインスレッドからメインキューへ
/// 自己 dispatch する形になり `EXC_BREAKPOINT`/SIGTRAP でクラッシュした**
/// （`hook-constraints` mac-2「メインスレッドから呼ばない」の逐語通りの帰結。
/// `.steering/20260824-o1-macos-instrument/decisions.md` 判断3 に実測を記録）。
/// → ★ `ime_macos.rs::is_japanese_ime_open()` は**背景スレッド**（IME ポーリングスレッド）
/// から呼ばれるので dispatch が要るが、**この関数はすでにメインスレッド上**にいるため、
/// TIS を直接呼ぶのが正しい。
///
/// # Safety（呼び出し元の契約）
/// この関数は**メインスレッドからのみ**呼ぶこと。背景スレッドから呼ぶ新しい呼び出し元を
/// 追加するなら、そのときは `dispatch_sync_f` 経由に戻すこと（★ 逆方向の同じ間違いをしない）。
pub fn keyboard_layout_id() -> Option<String> {
    use core_foundation::base::{CFRelease, TCFType};
    use core_foundation::string::CFString;

    // ⚠️★★★ code-reviewer MEDIUM-6: 「メインスレッドから呼ぶこと」という契約を
    //   *コメントだけ*にしない。★ 判断3 で踏んだクラッシュは「コメントに書いてあったのに
    //   検証しなかった」種類だったので、検査をコードにする（ADR-013 の教訓と同じ形）。
    //   ⚠️ debug_assert なので release ビルドではコストが無い（判定不能なら黙って通す）。
    debug_assert!(
        MainThreadMarker::new().is_some(),
        "keyboard_layout_id() はメインスレッドからのみ呼ぶこと \
         (dispatch_sync_f を使わない設計なので背景スレッドから呼ぶと未定義の挙動になる)"
    );

    // SAFETY: 呼び出し元契約によりメインスレッド上。HIToolbox の TIS API はメインスレッド
    // からの直接呼び出しを想定している（`ime_macos.rs` が背景スレッドから `dispatch_sync_f`
    // 経由で呼ぶのは、そちらの呼び出し元がメインスレッドではないため）。
    unsafe {
        let source = TISCopyCurrentKeyboardLayoutInputSource();
        if source.is_null() {
            return None;
        }
        let id_ref = TISGetInputSourceProperty(source, kTISPropertyInputSourceID);
        let result = if id_ref.is_null() {
            None
        } else {
            let cf_str =
                CFString::wrap_under_get_rule(id_ref as core_foundation::string::CFStringRef);
            Some(cf_str.to_string())
        };
        // ⚠️ `TISCopyCurrentKeyboardLayoutInputSource` は "Copy" セマンティクス
        //   （+1 の所有権を呼び出し側が持つ）なので解放が要る（`ime_macos.rs` と対の作法）。
        CFRelease(source);
        result
    }
}

// ---------------------------------------------------------------------------
// secure_input
// ---------------------------------------------------------------------------

/// `EnableSecureEventInput` が有効か。
///
/// ★ `IsSecureEventInputEnabled` は状態を読むだけの pure な Carbon 呼び出しであり、
/// `AXIsProcessTrustedWithOptions`/TIS クエリと異なり GCD メインスレッド dispatch は要らない
/// （`hook_macos.rs` の `CGPreflightListenEventAccess`/`AXIsProcessTrusted` と同じ扱い）。
pub fn secure_input_enabled() -> Option<bool> {
    // SAFETY: 引数を取らない pure read-only の Carbon API 呼び出し。
    // ★ `u8 != 0` で正規化する（上の extern 宣言の doc 参照・Boolean は unsigned char）。
    Some(unsafe { IsSecureEventInputEnabled() != 0 })
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ★ ビンの長さは 1 秒である (ADR-014 D4 の L-b 仕様・Windows と対)。
    #[test]
    fn pointer_bin_is_one_second() {
        assert_eq!(BIN_MS, 1000);
    }

    /// ⚠️★★★ **`secure_input` は状態が変化したときにしか行を出さない**（★ 区間フラグの実体）。
    #[test]
    fn secure_input_only_emits_on_transition() {
        // 初回 (last=None) は常に送る (★ 起動直後の状態を確定させる)。
        assert!(secure_input_should_emit(None, false));
        assert!(secure_input_should_emit(None, true));
        // 同じ値が続く限り送らない。
        assert!(!secure_input_should_emit(Some(false), false));
        assert!(!secure_input_should_emit(Some(true), true));
        // 変化したときだけ送る。
        assert!(secure_input_should_emit(Some(false), true));
        assert!(secure_input_should_emit(Some(true), false));
    }

    /// ⚠️★★★ **ポインタの変換は座標を持たない**（★ delta のみを足す）。
    ///
    /// ★ 実機の `CGEventTap` は使えないので、[`pointer_event_callback`] が実際に呼ぶ
    /// [`fold_delta`] そのものをテストする（★ code-reviewer MEDIUM-5 の是正 ——
    /// 以前は `PointerAccum::add_move` を叩いていたが、callback は `add_move` を
    /// 呼ばず同じ計算を再実装していたため、テストが production の配線を通っていなかった）。
    #[test]
    fn fold_delta_never_carries_sign_or_position() {
        // ⚠️ 符号付きの delta を足しても、絶対値の和だけが残ること。
        assert_eq!(fold_delta(-500, 500), 1000);
        assert_eq!(fold_delta(500, -500), 1000);
        assert_eq!(fold_delta(0, 0), 0);
        // ★ 左右・上下で区別できないこと（軌跡復元の入口を塞ぐ）。
        assert_eq!(fold_delta(10, 0), fold_delta(-10, 0));
        assert_eq!(fold_delta(0, 10), fold_delta(0, -10));
    }

    /// ⚠️★★★ **macOS では `buttons` が恒常的に 0 になる**（★ 意図的・忘れではない）。
    ///
    /// ADR-014 D4 の mac 側マスクは `MouseMoved`/`*Dragged`/`ScrollWheel` のみで
    /// `*MouseDown` を含まない。→ ★ [`build_pointer_bin`]（`run_pointer_loop` が実際に
    /// 呼ぶビン生成関数そのもの）が `button_presses` に常に `0` を渡すことを固定する
    /// （★ code-reviewer MEDIUM-5 の是正 —— 以前はテスト内で `button_presses: 0` を
    /// 自分で書いて 0 を assert するトートロジーだった）。
    #[test]
    fn macos_pointer_bin_never_counts_button_presses() {
        let bin = build_pointer_bin(999, 3, 0);
        assert_eq!(bin.buttons, 0, "macOS では buttons は常に 0");
        assert_eq!(bin.wheel, 3, "wheel_ticks はそのまま量子化される");
    }

    /// ★ [`build_pointer_bin`] がゼロ抑制対象を正しく組み立てること
    /// （`PointerBin::is_empty` は既に `pointer_bin.rs` 側でテスト済みだが、
    /// ここでは「本関数が正しいフィールドへ配線している」ことを固定する）。
    #[test]
    fn build_pointer_bin_wires_fields_correctly() {
        let empty = build_pointer_bin(0, 0, 1234);
        assert!(empty.is_empty());
        assert_eq!(empty.timestamp, 1234);

        let active = build_pointer_bin(1, 0, 1234);
        assert!(!active.is_empty());
    }

    /// ⚠️★★★ **`secure_input_enabled` は `None` を返さない**（macOS には常に計器がある）。
    ///
    /// ★ `SECURE_INPUT_AVAILABLE = cfg!(target_os = "macos")` (`observe.rs`) の前提と
    /// 整合していること —— macOS で常に `Some` を返さないと過大申告になる。
    #[test]
    fn secure_input_enabled_returns_some_on_macos() {
        assert!(
            secure_input_enabled().is_some(),
            "macOS では secure_input_enabled は常に Some を返す想定"
        );
    }

    /// ★ H1/HIGH-2 是正: 設置失敗が続くほどリトライ間隔が伸びる（CPU を焼き続けない）。
    #[test]
    fn pointer_tap_retry_backoff_grows_with_consecutive_failures() {
        assert_eq!(pointer_tap_retry_backoff(0), Duration::from_secs(2));
        assert_eq!(pointer_tap_retry_backoff(4), Duration::from_secs(2));
        assert_eq!(pointer_tap_retry_backoff(5), Duration::from_secs(5));
        assert_eq!(pointer_tap_retry_backoff(19), Duration::from_secs(5));
        assert_eq!(pointer_tap_retry_backoff(20), Duration::from_secs(10));
        assert_eq!(pointer_tap_retry_backoff(u32::MAX), Duration::from_secs(10));
    }
}
