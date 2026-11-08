//! 手跡の背景の層の窓（macOS だけ・ADR-051）。試作 `handmark_stage_spike.rs` の窓の作りを写した。
//!
//! 主画面の全体に透明な窓をデスクトップの高さ（壁紙の上・アイコンと他の窓の下）で出す。窓はマウスを受けない。
//! 開け閉めは駆動役の出来事（`handmark_driver::Effect`）だけが決める（環境変数の門は無い）。
//! 窓は何も返さない（`invoke` の口も記録も無い）。受け取るのは状態（`StageState`）だけで、
//! 推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。壁紙の画像を読まない・書かない。
//!
//! 窓は `setup()`（メインスレッド）で隠したまま作り、`open` / `close` は `run_on_main_thread` で行う。
//! 閉じる要求は止めて隠す（NSWindow を壊さない）。

use crate::analysis::handmark::state::StageState;

/// 背景の窓の label。`capabilities/handmark-stage.json` と `src/main.tsx` の分岐と一致させる。
pub const LABEL: &str = "handmark-stage";
/// 状態を窓へ配るイベント名（`StageState` か、閉じたときの `null`）。
pub const STATE_EVENT: &str = "handmark-state";

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use std::sync::atomic::{AtomicU8, Ordering};
    use tauri::{AppHandle, Emitter, Manager, Wry};

    /// 窓の様子の印(駆動役が読む)。0 = まだ・1 = 出た・2 = 失敗(作れなかった・出せなかった)。
    static STATUS: AtomicU8 = AtomicU8::new(0);
    /// `setup()` で窓を作れなかった(以後の `open` はすぐ失敗にする)。
    static BUILD_FAILED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

    /// 窓の様子(駆動役が刻みごとに読む)。
    pub fn status() -> crate::handmark_driver::WindowStatus {
        use crate::handmark_driver::WindowStatus;
        match STATUS.load(Ordering::Acquire) {
            1 => WindowStatus::Shown,
            2 => WindowStatus::Failed,
            _ => WindowStatus::Pending,
        }
    }

    // CGWindowLevelKey（CGWindowLevel.h）のデスクトップの層（アイコンの層 kCGDesktopIconWindowLevelKey より下）。
    const K_CG_DESKTOP_WINDOW_LEVEL_KEY: i32 = 2;

    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGWindowLevelForKey(key: i32) -> i32;
    }

    fn ns_window(window: &tauri::WebviewWindow<Wry>) -> Result<&objc2_app_kit::NSWindow, String> {
        let ptr = window
            .ns_window()
            .map_err(|e| format!("ns_window failed: {e}"))?;
        if ptr.is_null() {
            return Err("ns_window is null".to_string());
        }
        // SAFETY: Tauri が返す NSWindow のポインタで、窓は壊さない（hide だけ）のでアプリの終了まで生きている。
        //   呼び出しはすべてメインスレッド（setup と run_on_main_thread の中）で行う。
        Ok(unsafe { &*(ptr as *const objc2_app_kit::NSWindow) })
    }

    /// `setup()`（メインスレッド）から呼ぶ。窓を隠したまま作る。
    pub fn setup(app: &tauri::App<Wry>) {
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE")
        .inner_size(800.0, 600.0)
        .resizable(false)
        .decorations(false)
        .transparent(true)
        .shadow(false)
        .skip_taskbar(true)
        .focused(false)
        .visible(false)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                tracing::warn!("handmark stage: window could not be built: {}", e);
                BUILD_FAILED.store(true, Ordering::Release);
                return;
            }
        };
        let hide_target = window.clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = hide_target.hide();
            }
        });
    }

    /// 大きさ・層・Spaces・クリックの透過を設定して前に出す。どれかが失敗したら Err。
    fn prepare(window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        // 作業領域ではなく画面の全体（メニューバーと Dock の下も壁紙がある）。
        window
            .set_size(*monitor.size())
            .map_err(|e| format!("set_size failed: {e}"))?;
        window
            .set_position(*monitor.position())
            .map_err(|e| format!("set_position failed: {e}"))?;
        let ns = ns_window(window)?;
        // SAFETY: CoreGraphics の純粋な問い合わせで、引数は CGWindowLevelKey の定数。
        let level = unsafe { CGWindowLevelForKey(K_CG_DESKTOP_WINDOW_LEVEL_KEY) };
        ns.setLevel(level as objc2_app_kit::NSWindowLevel);
        ns.setCollectionBehavior(
            objc2_app_kit::NSWindowCollectionBehavior::CanJoinAllSpaces
                | objc2_app_kit::NSWindowCollectionBehavior::Stationary
                | objc2_app_kit::NSWindowCollectionBehavior::IgnoresCycle,
        );
        ns.setIgnoresMouseEvents(true);
        // 画面の共有・収録・スクリーンショットに写さない(NSWindowSharingNone)。読み返せなければ出さない。
        //   macOS 15 以降の収録で効くかは画面の確かめで見る。
        window
            .set_content_protected(true)
            .map_err(|e| format!("set_content_protected failed: {e}"))?;
        if ns.sharingType() != objc2_app_kit::NSWindowSharingType::None {
            return Err("sharingType read back is not None (fail-closed)".to_string());
        }
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        Ok(())
    }

    /// 窓を出す(メインスレッドで行う)。出せなくても何も返さない(警告だけ)。
    pub fn open(app: &AppHandle<Wry>) {
        STATUS.store(0, Ordering::Release);
        if BUILD_FAILED.load(Ordering::Acquire) {
            STATUS.store(2, Ordering::Release);
            return;
        }
        let handle = app.clone();
        let dispatched = app.run_on_main_thread(move || {
            let Some(window) = handle.get_webview_window(LABEL) else {
                tracing::warn!("handmark stage: window is not available");
                STATUS.store(2, Ordering::Release);
                return;
            };
            match prepare(&window) {
                Ok(()) => STATUS.store(1, Ordering::Release),
                Err(e) => {
                    tracing::warn!("handmark stage: stage NOT shown: {}", e);
                    let _ = window.hide();
                    STATUS.store(2, Ordering::Release);
                }
            }
        });
        if dispatched.is_err() {
            STATUS.store(2, Ordering::Release);
        }
    }

    /// 窓を隠す。描画も止めさせる(状態に `null` を送る)。
    pub fn close(app: &AppHandle<Wry>) {
        let _ = app.emit_to(LABEL, STATE_EVENT, Option::<StageState>::None);
        let handle = app.clone();
        let _ = app.run_on_main_thread(move || {
            if let Some(w) = handle.get_webview_window(LABEL) {
                let _ = w.hide();
            }
        });
    }

    /// 状態を窓へ配る。
    pub fn emit_state(app: &AppHandle<Wry>, state: &StageState) {
        let _ = app.emit_to(LABEL, STATE_EVENT, Some(*state));
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, emit_state, open, setup, status};
