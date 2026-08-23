pub mod clipboard;
pub mod hook;
pub mod ime;
// ⚠️★ **OS 非依存**にしてあるので `#[cfg]` を付けない。
//   ★ そうすると macOS の CI でも `CloakFold` のテストが走る
//   (`agent-shared.md`「OS ごとに規則が違うロジックは両 OS に対のテストを置く」)。
//   ⚠️ Win32 呼び出しは `ime_windows.rs` 側にあり、ここには 1 つも無い。
pub mod ime_cloak;
pub mod liveness;
// ⚠️★★★ O1 (R3-a) の非打鍵チャネル (ADR-014 D4 の段 1)。
//   ★ OS 依存は `observe_{windows,macos}.rs` に閉じ、ここ (`observe.rs`) は受け口だけ。
pub mod observe;
