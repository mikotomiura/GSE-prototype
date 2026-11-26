//! 手跡の「ほかの窓をどける」の macOS の部分（handmark-reveal-count 判断 3・4）。
//!
//! どける: 通常のアプリのうち隠れていない他のアプリの pid と、前面のアプリの pid をメモリに覚え、自分を前面に
//! 出してから `NSApplication.hideOtherApplications` を呼ぶ（試作 run9・run10 で、前面のアプリは外から
//! `NSRunningApplication.hide()` しても隠れずに残った）。
//! 戻す: 覚えた pid のアプリのうち、まだ隠れているものだけ `unhide()`。前面だったアプリを前面に戻す。
//!
//! 覚えた pid は記録・tracing に出さない。アプリの名前・bundle の ID は読まない。AppKit はメインスレッドで呼ぶ。

use std::sync::Mutex;

use objc2::MainThreadMarker;
use objc2_app_kit::{
    NSApplication, NSApplicationActivationOptions, NSApplicationActivationPolicy,
    NSRunningApplication, NSWorkspace,
};

use crate::handmark_reveal::is_mac_candidate;

/// どけたときに覚えたアプリ（メモリだけ）。
struct Remembered {
    pids: Vec<i32>,
    front: Option<i32>,
}

static REMEMBERED: Mutex<Option<Remembered>> = Mutex::new(None);

fn remembered() -> std::sync::MutexGuard<'static, Option<Remembered>> {
    REMEMBERED.lock().unwrap_or_else(|p| p.into_inner())
}

/// どける（`true`）・戻す（`false`）。メインスレッドならその場で、そうでなければメインスレッドへ回す
/// （終了の経路はメインスレッドから来るので、終わる前に戻せる）。
pub fn apply(app: &tauri::AppHandle, reveal: bool) {
    let run = move || {
        let Some(mtm) = MainThreadMarker::new() else {
            tracing::warn!("handmark: reveal skipped (not on the main thread)");
            return;
        };
        if reveal {
            reveal_on_main(mtm);
        } else {
            restore_on_main();
        }
    };
    if MainThreadMarker::new().is_some() {
        run();
    } else if let Err(e) = app.run_on_main_thread(run) {
        tracing::warn!("handmark: reveal could not reach the main thread: {e}");
    } else if !reveal {
        // 終了の経路がメインスレッドでなかったとき、終わるまでに戻せたかを実機で追えるように(固定の文だけ)
        tracing::info!("handmark: returning windows was queued to the main thread");
    }
}

fn reveal_on_main(mtm: MainThreadMarker) {
    let ws = NSWorkspace::sharedWorkspace();
    let me = NSRunningApplication::currentApplication().processIdentifier();
    let pids: Vec<i32> = ws
        .runningApplications()
        .iter()
        .filter(|a| {
            is_mac_candidate(
                a.activationPolicy() != NSApplicationActivationPolicy::Prohibited,
                a.isHidden(),
                a.processIdentifier() == me,
            )
        })
        .map(|a| a.processIdentifier())
        .collect();
    let front = ws
        .frontmostApplication()
        .map(|a| a.processIdentifier())
        .filter(|p| *p != me);
    {
        let mut g = remembered();
        // 戻す前に 2 回どけた（駆動役は交互にしか出さないが念のため）: 前に覚えたものを捨てない
        match g.as_mut() {
            Some(prev) => {
                for p in pids {
                    if !prev.pids.contains(&p) {
                        prev.pids.push(p);
                    }
                }
            }
            None => *g = Some(Remembered { pids, front }),
        }
    }
    let nsapp = NSApplication::sharedApplication(mtm);
    // 前面のアプリは外から隠せないので、先に自分を前面に出す（macOS 13 を支える版なので古い API を使う）
    #[allow(deprecated)]
    nsapp.activateIgnoringOtherApps(true);
    nsapp.hideOtherApplications(None);
}

fn restore_on_main() {
    let Some(r) = remembered().take() else {
        return;
    };
    for pid in r.pids {
        if let Some(a) = NSRunningApplication::runningApplicationWithProcessIdentifier(pid) {
            // 戻り値は実際に戻っても偽のことがある（試作 run9・run10）ので見ない
            if a.isHidden() {
                let _ = a.unhide();
            }
        }
    }
    if let Some(a) = r
        .front
        .and_then(NSRunningApplication::runningApplicationWithProcessIdentifier)
    {
        let _ = a.activateWithOptions(NSApplicationActivationOptions::empty());
    }
}
