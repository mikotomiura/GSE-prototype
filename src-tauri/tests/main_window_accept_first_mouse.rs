//! 主窓は、前面にないときの 1 回目のクリックもボタンに届かなければならない（macOS）。
//!
//! Tauri の既定（`acceptFirstMouse: false`）では、前面にない窓への 1 回目のクリックは
//! 窓を前に出すだけで消える。被験者が「すぐ止める」を押しても 1 回目は何も起きず、
//! 押し直すと止まり、もう一度押すと再開する（2026-10-30 の実機の交互の組・
//! `.steering/20261031-pause-auto-resume/results.md`）。同意文書 §4 の「すぐ止める」を
//! 1 回の押下で満たすため、主窓だけ `acceptFirstMouse` を立てる。
//!
//! ⚠️ 設定ファイルの検査なので OS を問わず走る（設定は macOS でだけ効く）。

use std::path::Path;

#[test]
fn main_window_accepts_first_mouse() {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("tauri.conf.json");
    let text = std::fs::read_to_string(&path).expect("tauri.conf.json を読めない");
    let conf: serde_json::Value =
        serde_json::from_str(&text).expect("tauri.conf.json が JSON でない");
    let windows = conf["app"]["windows"]
        .as_array()
        .expect("app.windows が配列でない");
    // ★ 主窓は label を省いた窓（Tauri の既定の label は "main"）。
    //   ⚠️ 該当がちょうど 1 つであることも確かめる（別の窓を主窓と取り違えない）。
    let mains: Vec<_> = windows
        .iter()
        .filter(|w| w.get("label").and_then(|l| l.as_str()).unwrap_or("main") == "main")
        .collect();
    assert_eq!(
        mains.len(),
        1,
        "主窓（label が無いか \"main\"）がちょうど 1 つでない"
    );
    let main = mains[0];
    assert_eq!(
        main.get("acceptFirstMouse").and_then(|v| v.as_bool()),
        Some(true),
        "主窓の acceptFirstMouse が true でない（前面にない窓の 1 回目のクリックが「すぐ止める」に届かない）"
    );
}
