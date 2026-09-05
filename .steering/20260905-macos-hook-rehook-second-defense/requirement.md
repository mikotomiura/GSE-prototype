# macOS フックの 2 段目の防御 (request_reinstall の実装)

## 背景

★ 2026-09-05 の 8 時間実測 (`experiments/20260903-o1-runtime-cost/notes.md`) で、
⚠️ **打鍵していた 31 分のうちおおむね 1〜2 割が「記録できていない」と印されていた**
(`starve_window` 8 窓・合計 114 s ＋ 120 s 級の DOWN ブロック 2 回)。

★ 原因を一次資料で特定した —— `src-tauri/src/input/hook.rs:346`:

```rust
pub fn request_reinstall() -> bool {
    #[cfg(target_os = "windows")]
    { hook_windows::request_reinstall() }
    #[cfg(not(target_os = "windows"))]
    { false }          // ★ ← macOS は **何もしない**
}
```

⚠️ `lib.rs:4259` の liveness スレッドは Down を見たら再設置を要求するが、
★ macOS では**常に false を返すだけ**である (ログの `rehook_requested=false` はこれ)。

⚠️★★★ **`hook-constraints` Skill の mac-3 が規定するパターン**
(「Hook Thread のポーリングループで `tap_is_enabled()` を見て再作成する」) は
★ **実装されていない**。現状の回復は `hook_macos.rs:302` の**コールバック内 1 段だけ**で、
⚠️ OS が `TapDisabled*` を届けたときにしか働かない。
→ ★ 「正式に disable されずに飢える」型には手が無く、実測では **DOWN のまま 6 時間 25 分**
放置された (⚠️ その区間は打鍵 0 件なので実害は無かったが、状態としては `alive:false`)。

## ゴール

★ macOS に **2 段目・3 段目の防御**を入れ、`rehook_requested=true` が実際に意味を持つようにする。

## スコープ

### 含むもの
- ★ **層 2**: hook スレッドの runloop に timer を足し、**正しいスレッドから**
  `CGEventTapIsEnabled` を見て false なら `CGEventTapEnable(port, true)`。
- ★ **層 3**: `request_reinstall()` (macOS) を実装 —— liveness から `CFRunLoop::stop()` を叩き、
  **既存の「2 秒待って tap 再作成」経路**を起こす (★ その経路は既に動いている)。
- ★ **診断**: Down を見た瞬間の `CGEventTapIsEnabled` と `CALLBACK_COUNT` 差分を
  `tracing` に出す (⚠️ 次に起きたとき「どちらの機序だったか」が決着する)。
- ★ 判定ロジック (エピソード 1 回・バックオフ) を **OS 非依存の純関数**に切り出して両 OS でテスト。

### 含まないもの
- ⚠️ **NDJSON スキーマは変えない** (★ `hook_health` に列を足さない)。
  → ⚠️ `schema_dto.rs` を触ると `emit_schema` / `schema/current.json` / gse-dataset の
  parity まで波及する。★ 診断は `gse-app.log` (tracing) に出せば「次の 1 回」は決着するので、
  **費用対効果でスキーマ churn を避ける**。⚠️ 必要なら別 PR で足す。
- ⚠️ **Windows 側の挙動は変えない** (★ 既に `hook_windows::request_reinstall()` がある)。
- ⚠️ starvation の**根本原因**の究明 (★ OS 側の事情。本タスクは「飢えたら戻す」までを担う)。

## 受け入れ条件

- [ ] ★ `request_reinstall()` が macOS で **`true` を返しうる** (⚠️ 定数 false でなくなる)。
- [ ] ★ 判定ロジックの純関数に**両 OS で走る**テストがある
      (⚠️ memory `windows-only-code-needs-ci`: `cfg` で閉じると相手側 OS が未検証で残る)。
- [ ] ★ `cargo test --workspace` と `gse-replay` のゴールデン回帰が緑
      (⚠️ HMM を触らないので `HMM_VERSION` は bump しない)。
- [ ] ★ 実機で **起動 → 正常動作 → ログに層 2/層 3 の痕跡が出ない**ことを確認 (⚠️ 陰性対照)。
- [ ] ⚠️ **starvation の自然発生は待てない**ので、★ **強制的に Down を作る経路**で
      層 3 が発火することを確かめる (⚠️ 「実装した」だけで終わらせない)。

## 運用メモ
- /reimagine 適用: **No**
- 理由: ★ 手段の選択は grill で確定済み (層 2 = runloop timer で再有効化 / 層 3 = CFRunLoopStop で
  既存の再作成経路を起こす)。⚠️ 代替案 (再有効化だけ / 作り直しだけ) は研究者が明示的に却下した。
