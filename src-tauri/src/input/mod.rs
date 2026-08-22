pub mod clipboard;
pub mod hook;
pub mod ime;
// ⚠️★ **OS 非依存**にしてあるので `#[cfg]` を付けない。
//   ★ そうすると macOS の CI でも `CloakFold` のテストが走る
//   (`agent-shared.md`「OS ごとに規則が違うロジックは両 OS に対のテストを置く」)。
//   ⚠️ Win32 呼び出しは `ime_windows.rs` 側にあり、ここには 1 つも無い。
pub mod ime_cloak;
pub mod liveness;
