//! macOS 限定: overlay 窓を非アクティブ NSPanel へ変換する (decisions D7)。
//!
//! 透明 always_on_top overlay 窓は **非 key (非アクティブ) 窓**のため、macOS は
//! クリックを content view (WKWebView) へルーティングせず、カードのボタンが押せなかった
//! (実測で確定した真因)。`accept_first_mouse` も独立した別ゲートで不足する。
//!
//! Spotlight / Raycast と同じく `NSWindowStyleMaskNonActivatingPanel` (1<<7) の NSPanel に
//! 変換すると、**アプリをアクティブ化せず (フォーカスを奪わず) クリックを webview へ配送**できる。
//! `canBecomeKeyWindow → YES` は tauri-nspanel v2 の `RawNSPanel` 側で自動付与されるため、
//! ここで subclass override を書く必要はない。
//!
//! 制約:
//! - **panel level は Floating (4) 固定。昇格させない**: tauri-nspanel #104 で高 level が
//!   IME をブロックする。GSE は日本語 IME 合成パイプラインがあるため必須 (hook-constraints)。
//! - `to_panel()` は既存 NSWindow を `object_setClass` でその場で再クラス化する (新窓を作らない)。
//!   AppKit の窓/クラス操作はメインスレッド限定。呼び出しは setup() (メインスレッド) から行う。
//! - 透明性・show/hide・setSize/setPosition・setIgnoreCursorEvents は標準 Tauri 窓 API の
//!   ままで動作する (NSPanel は NSWindow のサブクラスで、同一オブジェクトを再クラス化するため)。

use tauri::{AppHandle, Runtime, WebviewWindow};
#[allow(deprecated)]
use tauri_nspanel::cocoa::appkit::NSWindowCollectionBehavior;
use tauri_nspanel::{ManagerExt, WebviewWindowExt};

/// NSWindowStyleMaskNonActivatingPanel (cocoa crate が定数を省くため自前定義。nspanel #19)。
/// borderless (= 0) を内包するので、これ単独で「非アクティブ + 枠なし」になる。
const NS_NONACTIVATING_PANEL: i32 = 1 << 7;
/// NSFloatingWindowLevel。Wall/カードを他窓の上に出すのに十分。**昇格させない** (IME ブロック回避)。
const NS_FLOATING_WINDOW_LEVEL: i32 = 4;

/// 既存の overlay 窓を非アクティブ NSPanel へ変換する。
/// **メインスレッドから呼ぶこと** (AppKit 制約。setup() がこれを満たす)。
///
/// `NSWindowCollectionBehavior` は tauri-nspanel が再エクスポートする旧 `cocoa` crate 由来で
/// deprecated 扱い (objc2-app-kit へ移行推奨) だが、プラグインの `set_collection_behaviour` が
/// この型を要求するため踏襲する。プラグインが objc2 へ移行したら追従する。
#[allow(deprecated)]
pub fn convert_overlay_to_panel<R: Runtime>(window: &WebviewWindow<R>) -> tauri::Result<()> {
    // 同一 NSWindow をその場で NSPanel 化する。canBecomeKeyWindow=YES はプラグインが自動付与。
    // 戻り値は `tauri::Result` (このリポジトリは anyhow を依存に持たず Result<_,String>/tauri::Result
    // を使う規約。bin/replay.rs 参照)。to_panel 失敗は呼び出し側 (setup) が tracing で握る。
    let panel = window.to_panel()?;

    // 非アクティブ Panel: アプリをアクティブ化せずクリックを受ける (フォーカス非奪取)。
    // 注: `setStyleMask:` は既存マスクを**置換**する (OR ではない)。overlay は decorations(false)
    // で生成済 = 既存マスクは NSWindowStyleMaskBorderless(=0) なので、1<<7 単独でも borderless を
    // 内包し既存ビットは失われない。Pluely の Tauri 2.x レシピと同一 (set_style_mask(1<<7))。
    panel.set_style_mask(NS_NONACTIVATING_PANEL);

    // Floating level (昇格禁止)。style mask の後に設定する (mask 変更で level がリセットされる
    // AppKit のエッジケースを避ける)。
    panel.set_level(NS_FLOATING_WINDOW_LEVEL);

    // 全 Space + フルスクリーンアプリ上に重ねる。Wall (全画面ブロック) を Space 切替で
    // 回避されないためにも望ましい。idle (Probe/Nudge/Wall 非表示) 時は Overlay.tsx が窓を
    // 画面外 (-20000,-20000) + 1x1 へ退避するので、常駐窓が背後クリックを奪わない・常駐コストも
    // 無視できる (CanJoinAllSpaces のまま退避するため Space 切替でも露出しない)。
    panel.set_collection_behaviour(
        NSWindowCollectionBehavior::NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehavior::NSWindowCollectionBehaviorFullScreenAuxiliary,
    );

    // becomesKeyOnlyIfNeeded=YES: テキスト編集等が必要な時だけ key 化する (decisions D12)。
    // カードはマウス操作のみ (テキスト入力なし) のため key を取らず、前面アプリの
    // タイピングフォーカスを奪わない (非ブロック設計の維持)。クリックは accept_first_mouse +
    // ignoresMouseEvents=false で届く。
    panel.set_becomes_key_only_if_needed(true);

    Ok(())
}

/// overlay panel のクリック受理を切り替える (decisions D9)。
/// `interactive=true` で `ignoresMouseEvents=NO` (カード/Wall がクリックを捕捉)、
/// `false` で `=YES` (背後アプリへクリック透過)。
///
/// 真因: NSPanel 化した窓では JS の `setIgnoreCursorEvents` が `ignoresMouseEvents` に実効せず
/// クリックが素通りしていた (実機確認・ゲート1)。プラグインの `set_ignore_mouse_events` を
/// **Rust 権威**で直接叩いて確実に効かせる。
///
/// クリックの webview への配送 (ゲート2) は overlay builder の `accept_first_mouse(true)` +
/// 非アクティブ panel が担うため、ここでは **key 化しない** (`make_key_window` を呼ばない)。
/// これにより前面アプリのタイピングフォーカスを奪わない (非ブロック設計の維持)。
pub fn set_panel_interactive<R: Runtime>(
    app: &AppHandle<R>,
    interactive: bool,
) -> Result<(), String> {
    let panel = app
        .get_webview_panel("overlay")
        .map_err(|e| format!("get_webview_panel(overlay) failed: {e:?}"))?;
    panel.set_ignore_mouse_events(!interactive);

    // フォーカス非奪取 (decisions D12): Tauri の `win.show()` が `makeKeyAndOrderFront` で panel を
    // key 化してしまう (becomesKeyOnlyIfNeeded では抑止できなかった)。GSE は被験者が書き続ける
    // 研究ツールで、カード表示が前面アプリ (エディタ) のタイピングフォーカスを奪うと執筆データが
    // 壊れる。カードはマウス操作のみで key 不要なので、ここで即座に key を返す。クリックは
    // `accept_first_mouse(true)` + `ignoresMouseEvents=false` で非 key のまま webview へ届く。
    panel.resign_key_window();

    Ok(())
}
