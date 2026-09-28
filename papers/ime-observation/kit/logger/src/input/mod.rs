// GSE の `src-tauri/src/input/` のうち、変換セッションの状態機械だけを持つ。
// ⚠️ `ime_compose` / `ime_cloak` / `ime_mode` は GSE の逐語コピー（manifest.json が SHA-256 で固定する）。
//    `hook` は GSE の `hook.rs` の定数と Atomic だけのシム。⚠️ コピーの側は直さない。
// ⚠️ ロガーが使わない関数（Windows の cloak 折り畳みなど）も残るので dead_code を許す。
#[allow(dead_code)]
pub mod hook;
#[allow(dead_code)]
pub mod ime_cloak;
#[allow(dead_code)]
pub mod ime_compose;
#[allow(dead_code)]
pub mod ime_mode;
