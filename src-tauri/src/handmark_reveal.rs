//! 手跡の背景を見るために、他のアプリの窓をどける操作（spike・本線に入れない・macOS だけ）。
//!
//! `.steering/20261030-handmark-edge-strip-impl/` の design.md「どける操作」と、設計のタスクの論点 6。
//! 入口はトレイの 1 項目（「背景を見る」と「戻す」を切り替える）。
//!
//! - 隠す: 見えている regular のアプリ（自分を除く）と、層 0 の窓の前後の順番（pid だけ）と、前面のアプリを覚える。
//!   自分を前面に出して最大 1 秒待ち、出られなければ隠さずにやめる（判断 3。全画面の中ではここでやめる）。
//!   出られたら覚えたアプリを `hide()` する。
//! - 戻す: 覚えたアプリだけを `unhide()` する。前面が自分のままなら、元の重なりの奥から順に前へ出し、
//!   最後に元の前面のアプリを出す。前面が他のアプリに替わっていたら前へ出し直さない（焦点を奪わない）。
//! - 終了時: まだ戻していなければ `unhide()` する（`lib.rs` の `shutdown()`）。落ちたときは戻せない
//!   （隠れたアプリは Dock や Cmd+Tab で選べば戻る）。
//!
//! 守ること: アプリの名前を読まない。覚えた一覧（pid）・回数をログにもファイルにも書かない（ログに出すのは
//! 前面に出られたかと待った時間と、隠した・戻したアプリの数だけ）。覚えた一覧は戻したら捨てる。

/// 隠すアプリ: 見えている regular のアプリのうち、自分と、もともと隠れているものを除く。
/// `apps` は (pid, 隠れているか)。
pub(crate) fn plan_hide(apps: &[(i32, bool)], self_pid: i32) -> Vec<i32> {
    apps.iter()
        .filter(|(pid, hidden)| *pid != self_pid && !*hidden)
        .map(|(pid, _)| *pid)
        .collect()
}

/// 戻すときに前へ出す順番: 層 0 の窓の前後の順番（前から奥・pid）のうち隠したアプリを、
/// 奥から前へ 1 回ずつ並べる。元の前面のアプリは最後にする。窓が無かったアプリは先頭（いちばん奥）に置く。
pub(crate) fn restore_order(front_to_back: &[i32], hidden: &[i32], front: Option<i32>) -> Vec<i32> {
    // 前から見て最初に出てきた位置が、そのアプリのいちばん前の窓。
    let mut firsts: Vec<i32> = Vec::new();
    for pid in front_to_back {
        if hidden.contains(pid) && !firsts.contains(pid) {
            firsts.push(*pid);
        }
    }
    let mut order: Vec<i32> = hidden
        .iter()
        .filter(|p| !firsts.contains(p))
        .copied()
        .collect();
    order.extend(firsts.iter().rev());
    if let Some(f) = front {
        if let Some(i) = order.iter().position(|p| *p == f) {
            let f = order.remove(i);
            order.push(f);
        }
    }
    order
}

#[cfg(target_os = "macos")]
mod imp {
    use super::{plan_hide, restore_order};
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::{mpsc, Mutex, OnceLock};
    use std::time::{Duration, Instant};
    use tauri::{AppHandle, Wry};

    /// 前面に出るのを待つ上限と、読む間隔（論点 6）。
    const ACTIVATE_WAIT: Duration = Duration::from_millis(1000);
    const ACTIVATE_POLL: Duration = Duration::from_millis(50);
    /// 戻すとき、前へ出すアプリの間隔（設計のタスクの試し run13 と同じ約 0.2 秒）。
    const RESTORE_STEP: Duration = Duration::from_millis(200);
    /// 研究者が自分でアプリを戻したかを見る間隔。
    const WATCH_EVERY: Duration = Duration::from_millis(1000);
    /// やめたことを知らせる文字を出しておく時間。
    const NOTICE_FOR: Duration = Duration::from_secs(4);

    pub const LABEL_SHOW: &str = "背景を見る";
    pub const LABEL_RESTORE: &str = "戻す";
    const LABEL_ABORTED: &str = "背景を見る（前に出られませんでした）";

    /// 覚えたこと（pid だけ。名前は持たない）。戻したら捨てる。
    struct Remembered {
        hidden: Vec<i32>,
        order: Vec<i32>,
    }

    static STATE: Mutex<Option<Remembered>> = Mutex::new(None);
    /// 隠す・戻すが走っている間だけ true（重ねて走らせない）。
    static BUSY: AtomicBool = AtomicBool::new(false);
    /// トレイの項目（文字を状態に合わせて替える）。
    static ITEM: OnceLock<tauri::menu::MenuItem<Wry>> = OnceLock::new();

    pub fn set_menu_item(item: tauri::menu::MenuItem<Wry>) {
        let _ = ITEM.set(item);
    }

    fn set_label(text: &str) {
        if let Some(item) = ITEM.get() {
            let _ = item.set_text(text);
        }
    }

    /// メインスレッドで `f` を走らせて結果を待つ（最大 `wait`）。メインスレッドから呼ばない。
    fn on_main<T: Send + 'static>(
        app: &AppHandle<Wry>,
        wait: Duration,
        f: impl FnOnce() -> T + Send + 'static,
    ) -> Option<T> {
        let (tx, rx) = mpsc::channel();
        app.run_on_main_thread(move || {
            let _ = tx.send(f());
        })
        .ok()?;
        rx.recv_timeout(wait).ok()
    }

    fn self_pid() -> i32 {
        std::process::id() as i32
    }

    /// 見えている regular のアプリ（pid と隠れているか）と、前面のアプリ。
    fn running_apps() -> (Vec<(i32, bool)>, Option<i32>) {
        let ws = objc2_app_kit::NSWorkspace::sharedWorkspace();
        let mut apps = Vec::new();
        for a in ws.runningApplications().iter() {
            if a.activationPolicy() == objc2_app_kit::NSApplicationActivationPolicy::Regular
                && !a.isTerminated()
            {
                apps.push((a.processIdentifier(), a.isHidden()));
            }
        }
        let front = ws.frontmostApplication().map(|a| a.processIdentifier());
        (apps, front)
    }

    /// 層 0 の、画面に出ている窓の持ち主の pid（前から奥へ）。窓の名前は読まない。
    fn window_owner_order() -> Vec<i32> {
        use core_foundation::base::{CFType, TCFType};
        use core_foundation::dictionary::{CFDictionary, CFDictionaryRef};
        use core_foundation::number::CFNumber;
        use core_foundation::string::CFString;
        use core_graphics::window::{
            copy_window_info, kCGNullWindowID, kCGWindowLayer, kCGWindowListExcludeDesktopElements,
            kCGWindowListOptionOnScreenOnly, kCGWindowOwnerPID,
        };
        let mut out = Vec::new();
        let Some(list) = copy_window_info(
            kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
            kCGNullWindowID,
        ) else {
            return out;
        };
        // SAFETY: kCGWindowLayer / kCGWindowOwnerPID は CoreGraphics の定数の CFString で、プロセスの間ずっと生きている。
        let (layer_key, pid_key) = unsafe {
            (
                CFString::wrap_under_get_rule(kCGWindowLayer),
                CFString::wrap_under_get_rule(kCGWindowOwnerPID),
            )
        };
        for item in list.iter() {
            // SAFETY: CGWindowListCopyWindowInfo の要素は CFDictionary（Apple の文書）。get の規則で包み、所有しない。
            let dict: CFDictionary<CFString, CFType> =
                unsafe { CFDictionary::wrap_under_get_rule(*item as CFDictionaryRef) };
            let num = |k: &CFString| {
                dict.find(k)
                    .and_then(|v| v.downcast::<CFNumber>())
                    .and_then(|n| n.to_i32())
            };
            if num(&layer_key) == Some(0) {
                if let Some(pid) = num(&pid_key) {
                    out.push(pid);
                }
            }
        }
        out
    }

    /// 自分を前面に出し、最大 1 秒の間に前面になったか。メインスレッドから呼ばない。
    fn activate_and_wait(app: &AppHandle<Wry>) -> (bool, u64) {
        let started = Instant::now();
        let _ = app.run_on_main_thread(|| {
            if let Some(mtm) = objc2::MainThreadMarker::new() {
                objc2_app_kit::NSApplication::sharedApplication(mtm).activate();
            }
        });
        let mut active = false;
        while started.elapsed() < ACTIVATE_WAIT {
            std::thread::sleep(ACTIVATE_POLL);
            if on_main(app, ACTIVATE_POLL * 4, || {
                objc2_app_kit::NSRunningApplication::currentApplication().isActive()
            })
            .unwrap_or(false)
            {
                active = true;
                break;
            }
        }
        (active, started.elapsed().as_millis() as u64)
    }

    fn app_of(pid: i32) -> Option<objc2::rc::Retained<objc2_app_kit::NSRunningApplication>> {
        objc2_app_kit::NSRunningApplication::runningApplicationWithProcessIdentifier(pid)
            .filter(|a| !a.isTerminated())
    }

    /// トレイの項目を選んだとき。隠していれば戻し、隠していなければ隠す。
    pub fn toggle(app: &AppHandle<Wry>) {
        if BUSY.swap(true, Ordering::AcqRel) {
            return;
        }
        let remembered = STATE.lock().map(|s| s.is_some()).unwrap_or(false);
        let handle = app.clone();
        let spawned = std::thread::Builder::new()
            .name("gse-handmark-reveal".to_string())
            .spawn(move || {
                if remembered {
                    restore(&handle);
                } else {
                    hide(&handle);
                }
                BUSY.store(false, Ordering::Release);
            });
        if spawned.is_err() {
            BUSY.store(false, Ordering::Release);
            tracing::warn!("handmark reveal: thread could not start");
        }
    }

    fn hide(app: &AppHandle<Wry>) {
        // 1. 覚える（前に出る前の前面のアプリを覚える）。
        let Some((apps, front, windows)) = on_main(app, Duration::from_secs(2), || {
            let (apps, front) = running_apps();
            (apps, front, window_owner_order())
        }) else {
            return;
        };
        let me = self_pid();
        let hidden = plan_hide(&apps, me);
        let front = front.filter(|f| *f != me);
        let order = restore_order(&windows, &hidden, front);

        // 2. 前面に出て待つ。出られなければやめる（全画面の中ではここでやめる・判断 3）。
        let (active, waited_ms) = activate_and_wait(app);
        tracing::info!(
            active,
            activate_wait_ms = waited_ms,
            "handmark reveal: activate before hiding"
        );
        if !active {
            set_label(LABEL_ABORTED);
            std::thread::sleep(NOTICE_FOR);
            if STATE.lock().map(|s| s.is_none()).unwrap_or(false) {
                set_label(LABEL_SHOW);
            }
            return;
        }

        // 3. 隠す。成否は isHidden を読み直す（hide() の戻り値は当てにしない）。
        let to_hide = hidden.clone();
        let _ = on_main(app, Duration::from_secs(2), move || {
            for pid in &to_hide {
                if let Some(a) = app_of(*pid) {
                    let _ = a.hide();
                }
            }
        });
        std::thread::sleep(Duration::from_millis(500));
        let still = on_main(app, Duration::from_secs(2), {
            let h = hidden.clone();
            move || {
                h.iter()
                    .filter(|p| app_of(**p).is_some_and(|a| !a.isHidden()))
                    .count()
            }
        })
        .unwrap_or(0);
        tracing::info!(
            hidden = hidden.len(),
            not_hidden = still,
            "handmark reveal: hidden"
        );
        if let Ok(mut s) = STATE.lock() {
            *s = Some(Remembered { hidden, order });
        }
        set_label(LABEL_RESTORE);
        start_watch(app.clone());
    }

    fn restore(app: &AppHandle<Wry>) {
        let Some(r) = STATE.lock().ok().and_then(|mut s| s.take()) else {
            return;
        };
        let me = self_pid();
        let hidden = r.hidden.clone();
        let front_is_me = on_main(app, Duration::from_secs(2), move || {
            for pid in &hidden {
                if let Some(a) = app_of(*pid) {
                    let _ = a.unhide();
                }
            }
            objc2_app_kit::NSWorkspace::sharedWorkspace()
                .frontmostApplication()
                .map(|a| a.processIdentifier())
                == Some(me)
        })
        .unwrap_or(false);
        // 前面が他のアプリに替わっていたら、前へ出し直さない（焦点を奪わない）。
        if front_is_me {
            for pid in r.order.iter().copied() {
                let _ = app.run_on_main_thread(move || {
                    if let Some(a) = app_of(pid) {
                        let _ = a.activateWithOptions(
                            objc2_app_kit::NSApplicationActivationOptions::ActivateAllWindows,
                        );
                    }
                });
                std::thread::sleep(RESTORE_STEP);
            }
        }
        tracing::info!(
            restored = r.hidden.len(),
            reordered = front_is_me,
            "handmark reveal: restored"
        );
        set_label(LABEL_SHOW);
    }

    /// 隠している間、研究者が自分でアプリを全部戻したら（Dock・Cmd+Tab）、覚えた一覧を捨てて項目を戻す。
    fn start_watch(app: AppHandle<Wry>) {
        let _ = std::thread::Builder::new()
            .name("gse-handmark-reveal-watch".to_string())
            .spawn(move || loop {
                std::thread::sleep(WATCH_EVERY);
                if crate::is_shutting_down() {
                    return;
                }
                let hidden = match STATE.lock() {
                    Ok(s) => match s.as_ref() {
                        Some(r) => r.hidden.clone(),
                        None => return,
                    },
                    Err(_) => return,
                };
                let any_hidden = on_main(&app, Duration::from_secs(2), move || {
                    hidden
                        .iter()
                        .any(|p| app_of(*p).is_some_and(|a| a.isHidden()))
                })
                .unwrap_or(true);
                if !any_hidden && !BUSY.load(Ordering::Acquire) {
                    if let Ok(mut s) = STATE.lock() {
                        *s = None;
                    }
                    set_label(LABEL_SHOW);
                    tracing::info!("handmark reveal: all apps came back by themselves");
                    return;
                }
            });
    }

    /// 終了時（`shutdown()` から）: まだ隠していれば戻す。並べ直しはしない。
    pub fn restore_on_exit(app: &AppHandle<Wry>) {
        let Some(r) = STATE.lock().ok().and_then(|mut s| s.take()) else {
            return;
        };
        let unhide = move || {
            for pid in &r.hidden {
                if let Some(a) = app_of(*pid) {
                    let _ = a.unhide();
                }
            }
        };
        if objc2::MainThreadMarker::new().is_some() {
            unhide();
        } else {
            let _ = on_main(app, Duration::from_secs(2), unhide);
        }
        tracing::info!("handmark reveal: restored on exit");
    }
}

#[cfg(target_os = "macos")]
pub use imp::{restore_on_exit, set_menu_item, toggle, LABEL_SHOW};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hides_only_visible_apps_other_than_self() {
        let apps = [(10, false), (11, true), (12, false), (99, false)];
        assert_eq!(plan_hide(&apps, 99), vec![10, 12]);
    }

    #[test]
    fn restore_goes_from_back_to_front_and_ends_with_the_old_front() {
        // 前から: 12 の窓, 10 の窓, 12 の窓, 13 の窓（13 は隠していない）, 11 の窓
        let windows = [12, 10, 12, 13, 11];
        let hidden = [10, 11, 12, 14];
        // 14 は窓が無いので先頭。奥から: 11, 10, 12。元の前面 10 を最後へ。
        assert_eq!(
            restore_order(&windows, &hidden, Some(10)),
            vec![14, 11, 12, 10]
        );
    }

    #[test]
    fn a_front_app_that_was_not_hidden_is_not_added() {
        let windows = [5, 6];
        assert_eq!(restore_order(&windows, &[6], Some(5)), vec![6]);
        assert_eq!(restore_order(&windows, &[6], None), vec![6]);
    }

    #[test]
    fn nothing_hidden_means_nothing_to_restore() {
        assert!(restore_order(&[1, 2], &[], Some(1)).is_empty());
    }
}
