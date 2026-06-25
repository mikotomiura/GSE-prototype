# 設計

## 実装アプローチ

F4 は 3 つの独立した防御を組み合わせる (どれか 1 つでも欠けると別経路で再発しうる)。

### (A) callback での tap 即時再有効化 (主修正)
macOS は重い処理時に tap を `TapDisabledByTimeout`/`ByUserInput` で無効化する。これらの
disabled イベントは event mask に関係なく callback に届く。現状 callback (`handle_event`) は
press/release 以外を早期 return して**無視**しているため、tap が死んだまま runloop が
回り続けるか、最終的に runloop 退出 → 丸ごと作り直しに倒れる。

→ disabled イベントを受けたら `CGEventTapEnable(tap, true)` で**即再有効化**する。これは
Apple 公式の標準復旧手順であり、tap を作り直さないため取りこぼし・失効頻度が最小。

**chicken-and-egg 問題**: closure は tap 生成前に `CGEventTap::new` へ渡すため、closure 内から
tap オブジェクトを参照できない。`core-graphics` 0.24 の `CGEventTapEnable` は crate 非公開
(public は `tap.enable()` のみ、tap 実体が要る)。
→ tap 生成後に `tap.mach_port.as_concrete_TypeRef()` (CFMachPortRef) を静的 `AtomicPtr` に格納し、
callback はそのポインタを読んで自前 extern の `CGEventTapEnable(port, true)` を呼ぶ。
書き込み (hook thread) と読み出し (同 hook thread の runloop callback) は**同一スレッド**なので
データ競合なし。runloop 退出時にポインタを null クリアして stale 参照を防ぐ。

### (B) OS 都合の失効で LAST_KEY_MS=0 にしない (研究妥当性の核)
`hook_macos.rs:637` (runloop 退出) と `:612` (runloop source 生成失敗) の
`LAST_KEY_MS.store(0)` を**削除**する。`LAST_KEY_MS` は「最後の物理打鍵時刻」を表すグローバルで
セッション非依存。OS 都合の失効はキーボード活動の有無と無関係なので 0 に倒す理由がない。
削除すれば失効前の値が保持され、`now - last_key` で idle/away の連続性が保たれる。
初回起動前 (打鍵なし) は元々 0 のまま保持される (削除で副作用なし)。

### (C) プローブ駆動側で last_key==0 を away 寄りに倒す (多層防御)
`lib.rs:1608` の idle 計算を純関数 `probe_scheduler::driver_idle_ms(now, last_key, away_idle_ms)` に
切り出す。`last_key==0` (打鍵なし or 不明) は `away_idle_ms` を返して**プローブを抑止**する。
(B) で失効中も last_key が保持されるため (C) は基本的に冗長だが、初回打鍵前や将来の別経路で
last_key が 0 になった場合でも離席誤発火しない保険。Dashboard 表示用 `get_keyboard_idle_ms` は
変更しない (表示は 0 = 「未打鍵」が自然。設計判断は decisions.md)。

## 変更対象

### 修正するファイル
- `src-tauri/src/input/hook_macos.rs` —
  - 自前 extern `CGEventTapEnable` 宣言 + 静的 `TAP_PORT: AtomicPtr` 追加。
  - `handle_event` 冒頭で disabled イベント → 再有効化。
  - tap 生成後に `TAP_PORT` へ port 格納、runloop 退出時に null クリア。
  - `:637`/`:612` の `LAST_KEY_MS.store(0)` を削除 (`HOOK_ACTIVE.store(false)` は残す)。
- `src-tauri/src/analysis/probe_scheduler.rs` —
  - `pub fn driver_idle_ms(now_ms, last_key_ms, away_idle_ms) -> u64` を追加。
  - 回帰テストを追加。
- `src-tauri/src/lib.rs` —
  - プローブ駆動スレッド (`:1608`) の idle 計算を `driver_idle_ms` に置換。

### 新規作成・削除
- なし。

## 影響範囲
- `LAST_KEY_MS` 読み手: `get_keyboard_idle_ms` / `get_last_keypress_timestamp` / プローブ駆動。
  (B) でいずれも「失効中も連続」になり挙動改善。破壊的変化なし。
- HMM (features/engine): 不変。`gse-replay --snapshot` で確認。
- `analysis/` で OS API を呼ばない原則: `driver_idle_ms` は純算術のみで遵守。

## 既存パターンとの整合性
- `probe_scheduler.rs` の「純ロジックを analysis/ に閉じ OS API を呼ばない」方針に沿う。
- `hook-constraints` mac-1 (callback は Atomic + 軽量のみ)。`CGEventTapEnable` は Apple 推奨の
  軽量 FFI で input pipeline の復旧そのもの。heap/mutex/blocking/log は callback 内に持ち込まない。
- `CGEventType` は `PartialEq` 未実装 → `matches!` で判定 (既知 gotcha)。

## テスト戦略
- 単体 (純関数): `driver_idle_ms` の last_key==0 → away、通常時 → `now-last_key`。
- 回帰 (統合): away 中に last_key が周期的に 0 へ落ちる系列を `driver_idle_ms` 経由で
  `ProbeScheduler::poll` に流し、発火ゼロを確認 (旧ロジックなら発火 → 回帰検出)。
- フック層 (OS API): `cargo test` で直接検証困難 → ロジックを純関数化してカバー。
  再有効化経路はコードレビュー + 実機検証 (runbook) で担保。
- HMM 回帰: `gse-replay --snapshot tests/snapshots/minimal.json`。

## ロールバック計画
- 3 つの変更は独立。問題時は (A) callback 再有効化のみ revert しても (B)(C) で
  研究妥当性は維持される。逆に (B) のみ revert すると idle 連続性が壊れるため (B) が要。
- ブランチ `fix/macos-tap-idle-away` を main から切り、#1 とは別 PR。
