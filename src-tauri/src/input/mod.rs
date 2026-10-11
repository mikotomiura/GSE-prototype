pub mod clipboard;
pub mod hook;
pub mod ime;
// ⚠️★ **OS 非依存**にしてあるので `#[cfg]` を付けない。
//   ★ そうすると macOS の CI でも `CloakFold` のテストが走る
//   (`agent-shared.md`「OS ごとに規則が違うロジックは両 OS に対のテストを置く」)。
//   ⚠️ Win32 呼び出しは `ime_windows.rs` 側にあり、ここには 1 つも無い。
pub mod ime_cloak;
// ⚠️★ **OS 非依存**にしてあるので `#[cfg]` を付けない (`ime_cloak` と同じ理由)。
//   ★ そうすると **Windows の CI でも** 変換セッションの畳み込みテストが走る。
//   ⚠️ `hook_macos.rs` のテストモジュールは Windows では 1 行も走らないので、
//   判断をあちらに置くと**どちらの CI も検証しない**状態になる。
//   ⚠️ macOS API 呼び出しは `hook_macos.rs` 側にあり、ここには 1 つも無い。
pub mod ime_compose;
// ⚠️★ **OS 非依存**にしてあるので `#[cfg]` を付けない (`ime_compose` と同じ理由)。
//   ★ IME モードキー (`VK_DBE_*` / `VK_KANJI`) の遷移表は **両 OS で同じ意味**なので 1 か所に置く。
//   ⚠️★★★ 以前は `hook_windows.rs` と `hook_macos.rs` に**複製**されており、
//   **macOS 側の複製が無テストのまま意味がずれていた** (2026-09-12 に実機で発覚)。
pub mod ime_mode;
pub mod liveness;
// ⚠️★★★ O1 (R3-a) の非打鍵チャネル (ADR-014 D4 の段 1)。
//   ★ OS 依存は `observe_{windows,macos}.rs` に閉じ、ここ (`observe.rs`) は受け口だけ。
pub mod observe;
// EH3: スリープの直前と復帰の通知（肖像の終わりと始まり）。OS 依存は `power_{windows,macos}.rs`。
pub mod power;
