//! 手跡の案 A の小面の試作（spike・本線に入れない）。
//!
//! `.steering/20261016-handmark-a-surface-spike/` の design.md を参照。
//! 環境変数 `GSE_HANDMARK_SPIKE=1` で起動したときだけ、macOS の画面の右下の端に 48×48 の窓を出し、
//! 打鍵のたびに印を短く光らせる。成り立つ条件（遅れ・取り込みからの除外・クリックの透過・フォーカス）を
//! 確かめるためのもので、見た目は仮。
//!
//! 守ること（親タスク `.steering/20261015-tangibility-design/decisions.md` 判断 16）:
//! - 推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。受け取るのは打鍵の時刻だけ。
//! - 本人の操作を記録しない。窓はマウスを受けない。計測の CSV は `GSE_HANDMARK_SPIKE_MEASURE=1` のときだけ
//!   書き、中身は通し番号と遅れだけ（キーの種類も内容も持たない）。
//! - 持ち越さない。状態はこのプロセスの中だけ。
//! - 取り込みから外せないときは窓を出さない（試作の判断 6・fail-closed）。

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// 小面の窓の label。capabilities/handmark.json と src/main.tsx の分岐と一致させる。
pub const LABEL: &str = "handmark";
/// 打鍵を窓へ知らせるイベント名。
pub const KEY_EVENT: &str = "handmark-key";

const ENV_ENABLE: &str = "GSE_HANDMARK_SPIKE";
const ENV_MEASURE: &str = "GSE_HANDMARK_SPIKE_MEASURE";
const ENV_FORCE_PROTECT_FAIL: &str = "GSE_HANDMARK_SPIKE_FORCE_PROTECT_FAIL";

/// 窓が出ていて打鍵を送ってよいときだけ true。閉じたら false に戻す。
static ACTIVE: AtomicBool = AtomicBool::new(false);
static SEQ: AtomicU64 = AtomicU64::new(0);

/// 環境変数の値を真偽に読む。`GSE_DEBUG` と同じく "1" のときだけ真。
fn flag_on(value: Option<&str>) -> bool {
    value == Some("1")
}

fn env_flag(name: &str) -> bool {
    flag_on(std::env::var(name).ok().as_deref())
}

/// 計測を有効にして起動したか。
pub fn measure_enabled() -> bool {
    env_flag(ENV_MEASURE)
}

/// 窓へ送る中身。キーの種類も内容も持たない。
#[derive(Clone, serde::Serialize)]
struct KeyPayload {
    seq: u64,
    /// フックが取った打鍵の時刻（壁時計のミリ秒）。
    t_key_ms: u64,
    /// 窓が遅れを返すか。
    measure: bool,
}

/// 計測の CSV の 1 行。通し番号と遅れ（ミリ秒）だけ。
fn csv_line(seq: u64, latency_ms: f64) -> String {
    format!("{seq},{latency_ms:.1}\n")
}

/// 窓から返ってきた遅れとして受け付けてよい値か。
fn latency_is_plausible(latency_ms: f64) -> bool {
    latency_ms.is_finite() && (-1_000.0..=60_000.0).contains(&latency_ms)
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use std::io::Write;
    use std::path::PathBuf;
    use std::sync::{Mutex, OnceLock};
    use tauri::{AppHandle, Emitter, Manager, Wry};
    use tauri_nspanel::ManagerExt;

    /// 小面の一辺（論理 px）と、画面の端からの余白。
    const SIDE: f64 = 48.0;
    const MARGIN: f64 = 16.0;

    static APP: OnceLock<AppHandle<Wry>> = OnceLock::new();
    static CSV: Mutex<Option<(PathBuf, std::fs::File)>> = Mutex::new(None);

    /// `setup()`（メインスレッド）から呼ぶ。環境変数が無ければ何もしない。
    pub fn setup(app: &tauri::App<Wry>) {
        if !env_flag(ENV_ENABLE) {
            return;
        }
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE handmark spike")
        .inner_size(SIDE, SIDE)
        .resizable(false)
        .decorations(false)
        .transparent(true)
        .shadow(false)
        .always_on_top(true)
        .skip_taskbar(true)
        .focused(false)
        .visible(false)
        .build()
        {
            Ok(w) => w,
            Err(e) => {
                tracing::warn!("handmark spike: window could not be built: {}", e);
                return;
            }
        };

        match prepare(app.handle(), &window) {
            Ok(()) => {
                // ⚠️ Tauri の show() は panel を key にしてフォーカスを奪う（overlay の D12）。
                //   key にしない orderFrontRegardless で前に出す。
                match app.get_webview_panel(LABEL) {
                    Ok(panel) => panel.order_front_regardless(),
                    Err(e) => {
                        tracing::warn!(
                            "handmark spike: panel lookup failed after prepare: {:?}",
                            e
                        );
                        hide(app.handle(), &window);
                        return;
                    }
                }
                let _ = APP.set(app.handle().clone());
                ACTIVE.store(true, Ordering::Release);
                tracing::info!(measure = measure_enabled(), "handmark spike: surface shown");
            }
            Err(e) => {
                // fail-closed（試作の判断 6）: 取り込みから外せたと確かめられないなら出さない。
                tracing::warn!("handmark spike: surface NOT shown (fail-closed): {}", e);
                hide(app.handle(), &window);
            }
        }
    }

    /// NSPanel 化・クリック透過・位置・取り込みからの除外と読み返し。どれかが失敗したら Err。
    fn prepare(app: &AppHandle<Wry>, window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        crate::overlay_panel::convert_overlay_to_panel(window)
            .map_err(|e| format!("NSPanel conversion failed: {e}"))?;
        let panel = app
            .get_webview_panel(LABEL)
            .map_err(|e| format!("get_webview_panel({LABEL}) failed: {e:?}"))?;
        panel.set_ignore_mouse_events(true);

        place_bottom_right(window)?;

        if env_flag(ENV_FORCE_PROTECT_FAIL) {
            return Err(format!(
                "simulated content-protection failure ({ENV_FORCE_PROTECT_FAIL}=1)"
            ));
        }
        window
            .set_content_protected(true)
            .map_err(|e| format!("set_content_protected failed: {e}"))?;
        if !sharing_type_is_none(window)? {
            return Err("sharingType read back is not None".to_string());
        }
        Ok(())
    }

    /// 主画面の作業領域（Dock とメニューバーを除く）の右下の端に置く。
    fn place_bottom_right(window: &tauri::WebviewWindow<Wry>) -> Result<(), String> {
        let monitor = window
            .primary_monitor()
            .map_err(|e| format!("primary_monitor failed: {e}"))?
            .ok_or_else(|| "no primary monitor".to_string())?;
        let scale = monitor.scale_factor();
        let area = monitor.work_area();
        let offset = ((SIDE + MARGIN) * scale).round() as i32;
        let x = area.position.x + area.size.width as i32 - offset;
        let y = area.position.y + area.size.height as i32 - offset;
        window
            .set_position(tauri::PhysicalPosition::new(x, y))
            .map_err(|e| format!("set_position failed: {e}"))
    }

    /// NSWindow の sharingType を読み返す（メインスレッドから呼ぶ）。
    fn sharing_type_is_none(window: &tauri::WebviewWindow<Wry>) -> Result<bool, String> {
        let ptr = window
            .ns_window()
            .map_err(|e| format!("ns_window failed: {e}"))?;
        if ptr.is_null() {
            return Err("ns_window is null".to_string());
        }
        // SAFETY: Tauri が返す NSWindow のポインタで、窓はこの呼び出しの間生きている。
        //   setup() はメインスレッドで動くので、AppKit の読み出しの制約を満たす。
        let ns_window: &objc2_app_kit::NSWindow =
            unsafe { &*(ptr as *const objc2_app_kit::NSWindow) };
        Ok(ns_window.sharingType() == objc2_app_kit::NSWindowSharingType::None)
    }

    /// 分析スレッドから呼ぶ。窓が出ているときだけ、時刻と通し番号を送る。
    pub fn notify_key(t_key_ms: u64) {
        if !ACTIVE.load(Ordering::Acquire) {
            return;
        }
        let Some(app) = APP.get() else { return };
        let payload = KeyPayload {
            seq: SEQ.fetch_add(1, Ordering::Relaxed),
            t_key_ms,
            measure: measure_enabled(),
        };
        let _ = app.emit_to(LABEL, KEY_EVENT, payload);
    }

    /// 窓を隠したままにする（壊さない）。
    /// ⚠️ NSPanel にした窓を `destroy()` すると Objective-C の例外でプロセスごと落ちた
    ///   （2026-10-16 実測: `fatal runtime error: Rust cannot catch foreign exceptions`）。
    fn hide(app: &AppHandle<Wry>, window: &tauri::WebviewWindow<Wry>) {
        ACTIVE.store(false, Ordering::Release);
        match app.get_webview_panel(LABEL) {
            Ok(panel) => panel.order_out(None),
            Err(_) => {
                let _ = window.hide();
            }
        }
    }

    /// トレイの「小面を閉じる」。
    pub fn close(app: &AppHandle<Wry>) {
        if let Some(w) = app.get_webview_window(LABEL) {
            hide(app, &w);
        }
        // ⚠️ 閉じたことは記録しない（applog にも出さない・本人の操作を記録しない・判断 16）。
    }

    /// 小面が出ているか（トレイが「小面を閉じる」を出すかの判断に使う）。
    pub fn is_shown(_app: &AppHandle<Wry>) -> bool {
        ACTIVE.load(Ordering::Acquire)
    }

    pub fn record_latency(seq: u64, latency_ms: f64) -> Result<(), String> {
        let mut guard = CSV.lock().map_err(|_| "csv lock poisoned".to_string())?;
        if guard.is_none() {
            let dir = std::env::temp_dir().join("gse-handmark-spike");
            std::fs::create_dir_all(&dir).map_err(|e| format!("create_dir_all: {e}"))?;
            let started = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_millis())
                .unwrap_or(0);
            let path = dir.join(format!("latency-{started}.csv"));
            let mut file = std::fs::File::create(&path).map_err(|e| format!("create csv: {e}"))?;
            file.write_all(b"seq,latency_ms\n")
                .map_err(|e| format!("write csv header: {e}"))?;
            tracing::info!(path = %path.display(), "handmark spike: latency csv opened");
            *guard = Some((path, file));
        }
        if let Some((_, file)) = guard.as_mut() {
            file.write_all(csv_line(seq, latency_ms).as_bytes())
                .map_err(|e| format!("write csv: {e}"))?;
        }
        Ok(())
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, is_shown, notify_key, setup};

#[cfg(not(target_os = "macos"))]
pub fn notify_key(_t_key_ms: u64) {}

/// 窓が描画の後に返す遅れを受ける。計測を有効にして起動し、小面の窓から呼ばれたときだけ書く。
#[tauri::command]
pub fn handmark_spike_latency(
    window: tauri::WebviewWindow,
    seq: u64,
    latency_ms: f64,
) -> Result<(), String> {
    if window.label() != LABEL || !measure_enabled() {
        return Err("handmark spike measurement is not enabled".to_string());
    }
    if !latency_is_plausible(latency_ms) {
        return Err("implausible latency".to_string());
    }
    #[cfg(target_os = "macos")]
    {
        imp::record_latency(seq, latency_ms)
    }
    #[cfg(not(target_os = "macos"))]
    {
        let _ = seq;
        Err("handmark spike is macOS only".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_flag_is_true_only_for_exactly_one() {
        assert!(flag_on(Some("1")));
        assert!(!flag_on(None));
        assert!(!flag_on(Some("")));
        assert!(!flag_on(Some("0")));
        assert!(!flag_on(Some("true")));
        assert!(!flag_on(Some(" 1")));
    }

    #[test]
    fn a_csv_line_carries_only_the_sequence_and_the_latency() {
        assert_eq!(csv_line(0, 12.34), "0,12.3\n");
        assert_eq!(csv_line(199, 250.0), "199,250.0\n");
        assert_eq!(csv_line(7, 0.0).matches(',').count(), 1);
    }

    #[test]
    fn implausible_latencies_are_rejected() {
        assert!(latency_is_plausible(16.7));
        assert!(latency_is_plausible(0.0));
        assert!(!latency_is_plausible(f64::NAN));
        assert!(!latency_is_plausible(f64::INFINITY));
        assert!(!latency_is_plausible(-5_000.0));
        assert!(!latency_is_plausible(120_000.0));
    }
}
