//! 手跡の背景の層の試作（spike・本線に入れない）。
//!
//! `.steering/20261016-handmark-stage-spike/` の design.md を参照。
//! 環境変数 `GSE_HANDMARK_STAGE_SPIKE=1` で起動したときだけ、macOS の主画面の全体に透明な窓を
//! デスクトップの高さ（壁紙の上・アイコンと他の窓の下）で出し、打鍵の時刻から等高線の波を描く。
//! 成り立つ条件（層の上下・Spaces・全画面・覆われても動き続けるか・取り込みに写るか・負荷）を確かめるためのもの。
//!
//! 守ること（親タスク `.steering/20261015-tangibility-design/decisions.md` 判断 16・表現の議論の判断 2）:
//! - 推定（`engine`・`invitation`・`p_stuck`・`level`）を use しない。受け取るのは打鍵の時刻だけ。
//! - 壁紙の画像を読まない・書かない（EH3 の壁紙の経路に触れない）。
//! - 本人の操作を記録しない。窓はマウスを受けない。計測の CSV は `GSE_HANDMARK_SPIKE_MEASURE=1` のときだけ書き、
//!   中身は 1 秒ごとの描画の量と窓の見え方だけ（打鍵の時刻もキーの種類も持たない）。
//!   ⚠️ ただし描画は打鍵の後の数秒しか回らないので、毎秒の `frames` は「その秒に打っていたか」の粗い代わりの値になる。
//!   行の時刻は窓を開いてからの相対で、ファイル名にも起動時刻を入れない（プロセス番号だけ）。
//!   CSV は OS の一時ディレクトリに残るので、試作の計測の後は消す（手順書）。
//! - 共有の種別は既定のまま出す（写るかを測る）。`GSE_HANDMARK_STAGE_SPIKE_PROTECT=1` のときだけ「なし」にし、
//!   読み返せなければ出さない（小面と同じ fail-closed）。

#[cfg(target_os = "macos")]
use std::sync::atomic::{AtomicBool, Ordering};

/// 背景の窓の label。capabilities/handmark-stage.json と src/main.tsx の分岐と一致させる。
pub const LABEL: &str = "handmark-stage";
/// 打鍵を窓へ知らせるイベント名。
#[cfg(target_os = "macos")]
const KEY_EVENT: &str = "handmark-stage-key";

#[cfg(target_os = "macos")]
const ENV_ENABLE: &str = "GSE_HANDMARK_STAGE_SPIKE";
#[cfg(target_os = "macos")]
const ENV_PROTECT: &str = "GSE_HANDMARK_STAGE_SPIKE_PROTECT";

/// 窓が出ていて打鍵を送ってよいときだけ true。閉じたら false に戻す。
#[cfg(target_os = "macos")]
static ACTIVE: AtomicBool = AtomicBool::new(false);

/// 窓へ送る中身。打鍵の時刻だけ（キーの種類も内容も持たない）。
#[cfg(target_os = "macos")]
#[derive(Clone, serde::Serialize)]
struct KeyPayload {
    measure: bool,
}

/// 窓から 1 秒ごとに返ってくる描画の記録。
#[derive(Debug, Clone, Copy)]
struct TickRecord {
    /// 窓を開いてからの 1 秒の刻みの番号。
    tick: u64,
    /// 窓の `performance.now()`（窓を開いてからのミリ秒）。壁時計を持たない。
    t_ms: f64,
    /// その 1 秒で描いたフレームの数。
    frames: u32,
    /// `document.visibilityState` が visible だったか。
    doc_visible: bool,
    /// 1 秒の刻みが予定より何 ms 遅れたか。
    lag_ms: f64,
}

/// 窓から返ってきた 1 秒ごとの記録として受け付けてよい値か。
fn tick_is_plausible(r: &TickRecord) -> bool {
    let time_ok = |v: f64| v.is_finite() && (0.0..=86_400_000.0).contains(&v);
    time_ok(r.t_ms)
        && r.frames <= 1_000
        && r.lag_ms.is_finite()
        && (-1_000.0..=600_000.0).contains(&r.lag_ms)
}

/// CSV の 1 行。窓の記録に、Rust 側で読んだ occlusionState の可視ビットを足す。
#[cfg(target_os = "macos")]
fn tick_csv_line(r: &TickRecord, occlusion_visible: Option<bool>) -> String {
    let occ = occlusion_visible
        .map(|v| u8::from(v).to_string())
        .unwrap_or_default();
    format!(
        "{},{:.1},{},{},{:.1},{}\n",
        r.tick,
        r.t_ms,
        r.frames,
        u8::from(r.doc_visible),
        r.lag_ms,
        occ
    )
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use crate::handmark_spike::measure_enabled;
    use std::io::Write;
    use std::path::PathBuf;
    use std::sync::{Mutex, OnceLock};
    use tauri::{AppHandle, Emitter, Manager, Wry};

    // CGWindowLevelKey（CGWindowLevel.h）のデスクトップの層（アイコンの層 kCGDesktopIconWindowLevelKey より下）。
    const K_CG_DESKTOP_WINDOW_LEVEL_KEY: i32 = 2;

    #[link(name = "CoreGraphics", kind = "framework")]
    extern "C" {
        fn CGWindowLevelForKey(key: i32) -> i32;
    }

    static APP: OnceLock<AppHandle<Wry>> = OnceLock::new();
    static CSV: Mutex<Option<(PathBuf, std::fs::File)>> = Mutex::new(None);

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

    /// `setup()`（メインスレッド）から呼ぶ。環境変数が無ければ何もしない。
    pub fn setup(app: &tauri::App<Wry>) {
        if !crate::handmark_spike::env_flag(ENV_ENABLE) {
            return;
        }
        let window = match tauri::WebviewWindowBuilder::new(
            app,
            LABEL,
            tauri::WebviewUrl::App("index.html".into()),
        )
        .title("GSE handmark stage spike")
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
                tracing::warn!("handmark stage spike: window could not be built: {}", e);
                return;
            }
        };

        match prepare(&window) {
            Ok(()) => {
                let _ = APP.set(app.handle().clone());
                ACTIVE.store(true, Ordering::Release);
                tracing::info!(
                    measure = measure_enabled(),
                    protect = crate::handmark_spike::env_flag(ENV_PROTECT),
                    "handmark stage spike: stage shown at desktop level"
                );
            }
            Err(e) => {
                tracing::warn!("handmark stage spike: stage NOT shown: {}", e);
                let _ = window.hide();
            }
        }
    }

    /// 大きさ・層・Spaces・クリックの透過・共有の種別を設定して前に出す。どれかが失敗したら Err。
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

        if crate::handmark_spike::env_flag(ENV_PROTECT) {
            window
                .set_content_protected(true)
                .map_err(|e| format!("set_content_protected failed: {e}"))?;
        }

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

        if crate::handmark_spike::env_flag(ENV_PROTECT)
            && ns.sharingType() != objc2_app_kit::NSWindowSharingType::None
        {
            return Err("sharingType read back is not None (fail-closed)".to_string());
        }
        // key にしない（フォーカスを奪わない）。
        ns.orderFrontRegardless();
        tracing::info!(level, "handmark stage spike: window level set");
        Ok(())
    }

    /// 分析スレッドから呼ぶ。窓が出ているときだけ、打鍵があったことを送る。
    pub fn notify_key() {
        if !ACTIVE.load(Ordering::Acquire) {
            return;
        }
        let Some(app) = APP.get() else { return };
        let _ = app.emit_to(
            LABEL,
            KEY_EVENT,
            KeyPayload {
                measure: measure_enabled(),
            },
        );
    }

    /// トレイの「背景を閉じる」。隠すだけ（記録しない）。
    pub fn close(app: &AppHandle<Wry>) {
        ACTIVE.store(false, Ordering::Release);
        if let Some(w) = app.get_webview_window(LABEL) {
            let _ = w.hide();
        }
    }

    pub fn is_shown(_app: &AppHandle<Wry>) -> bool {
        ACTIVE.load(Ordering::Acquire)
    }

    fn append_csv(line: &str) -> Result<(), String> {
        if crate::recording::is_paused() {
            return Ok(());
        }
        let mut guard = CSV.lock().map_err(|_| "csv lock poisoned".to_string())?;
        if guard.is_none() {
            let dir = std::env::temp_dir().join("gse-handmark-spike");
            std::fs::create_dir_all(&dir).map_err(|e| format!("create_dir_all: {e}"))?;
            // 起動時刻を入れると、行の相対時刻と合わせて打っていた時間帯が戻せてしまうので、プロセス番号だけにする。
            let path = dir.join(format!("stage-pid{}.csv", std::process::id()));
            let mut file = std::fs::File::create(&path).map_err(|e| format!("create csv: {e}"))?;
            file.write_all(b"tick,t_ms,frames,doc_visible,lag_ms,occlusion_visible\n")
                .map_err(|e| format!("write csv header: {e}"))?;
            tracing::info!(path = %path.display(), "handmark stage spike: csv opened");
            *guard = Some((path, file));
        }
        if let Some((_, file)) = guard.as_mut() {
            file.write_all(line.as_bytes())
                .map_err(|e| format!("write csv: {e}"))?;
        }
        Ok(())
    }

    /// occlusionState をメインスレッドで読んでから 1 行書く。
    pub(super) fn record_tick(
        window: tauri::WebviewWindow<Wry>,
        r: TickRecord,
    ) -> Result<(), String> {
        let w = window.clone();
        window
            .run_on_main_thread(move || {
                let visible = ns_window(&w).ok().map(|ns| {
                    ns.occlusionState()
                        .contains(objc2_app_kit::NSWindowOcclusionState::Visible)
                });
                if let Err(e) = append_csv(&tick_csv_line(&r, visible)) {
                    tracing::warn!("handmark stage spike: csv write failed: {}", e);
                }
            })
            .map_err(|e| format!("run_on_main_thread failed: {e}"))
    }
}

#[cfg(target_os = "macos")]
pub use imp::{close, is_shown, notify_key, setup};

#[cfg(not(target_os = "macos"))]
pub fn notify_key() {}

/// 背景の窓が起動時に、計測するかを問い合わせる（最初の打鍵の前の秒も記録するため）。
#[tauri::command]
pub fn handmark_stage_measure_enabled(window: tauri::WebviewWindow) -> bool {
    window.label() == LABEL && crate::handmark_spike::measure_enabled()
}

/// 窓が 1 秒ごとに返す描画の記録を受ける。計測を有効にして起動し、背景の窓から呼ばれたときだけ書く。
#[tauri::command]
pub fn handmark_stage_tick(
    window: tauri::WebviewWindow,
    tick: u64,
    t_ms: f64,
    frames: u32,
    doc_visible: bool,
    lag_ms: f64,
) -> Result<(), String> {
    if window.label() != LABEL || !crate::handmark_spike::measure_enabled() {
        return Err("handmark stage measurement is not enabled".to_string());
    }
    // 閉じた（隠した）後は受け付けない（窓のタイマーは回り続けるため）。
    #[cfg(target_os = "macos")]
    if !ACTIVE.load(Ordering::Acquire) {
        return Err("handmark stage is closed".to_string());
    }
    let record = TickRecord {
        tick,
        t_ms,
        frames,
        doc_visible,
        lag_ms,
    };
    if !tick_is_plausible(&record) {
        return Err("implausible tick record".to_string());
    }
    #[cfg(target_os = "macos")]
    {
        imp::record_tick(window, record)
    }
    #[cfg(not(target_os = "macos"))]
    {
        // tick は macOS の CSV でしか読まないので、ここで読まないと Windows で dead_code になる。
        let _ = record.tick;
        Err("handmark stage spike is macOS only".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tick(frames: u32, lag_ms: f64) -> TickRecord {
        TickRecord {
            tick: 3,
            t_ms: 3_000.0,
            frames,
            doc_visible: true,
            lag_ms,
        }
    }

    #[test]
    fn implausible_ticks_are_rejected() {
        assert!(tick_is_plausible(&tick(60, 4.0)));
        assert!(!tick_is_plausible(&tick(5_000, 4.0)));
        assert!(!tick_is_plausible(&tick(60, f64::NAN)));
        assert!(!tick_is_plausible(&TickRecord {
            t_ms: -1.0,
            ..tick(60, 4.0)
        }));
    }

    #[cfg(target_os = "macos")]
    #[test]
    fn a_tick_csv_line_has_six_fields_and_no_wall_clock() {
        let line = tick_csv_line(&tick(58, 3.5), Some(false));
        assert_eq!(line, "3,3000.0,58,1,3.5,0\n");
        assert_eq!(tick_csv_line(&tick(0, 0.0), None), "3,3000.0,0,1,0.0,\n");
    }
}
