# macOS CGEventTap 失効による idle/away 誤リセット ＆ ランダムプローブ誤発火の修正 (F4)

## 背景

macOS で待機中に OS が CGEventTap を失効させる (`kCGEventTapDisabledByTimeout` /
スリープ・ディスプレイスリープ復帰) と、`CFRunLoop::run_current()` が抜けて
`hook_macos.rs:637` で `LAST_KEY_MS=0` にリセットされる。その結果:

1. **Dashboard の idle カウンタが 0 に戻る** (`get_keyboard_idle_ms()` は `last==0` で 0 を返す, `lib.rs:429`)。
2. **idle/away 判定が壊れる**。
3. **離席中にランダムプローブが誤発火**する (同根)。駆動側は `last_key==0 → idle=0` (`lib.rs:1608`) →
   `away=false` (`probe_scheduler.rs:206`, `away_idle_ms=180_000`) → 離席中でも発火 → 空回答/汚染データ。

研究妥当性 (`realtime_label` の一様ランダム性) に直接効くため、F4 のみ Phase1 前倒し
(`phase2-followups.md` 参照)。Windows は本症状なし (メッセージループは `WM_QUIT` でしか抜けない)。

## ゴール

- OS 都合の一時失効では idle/away の連続性が壊れない。
- 離席 (3 分以上 idle) 中にランダムプローブが発火しない。
- macOS の tap 失効を「作り直し」ではなく軽量な再有効化で回復し、失効頻度・取りこぼしを最小化する。

## スコープ

### 含むもの
- `hook_macos.rs`: tap-disabled イベント (`TapDisabledByTimeout`/`ByUserInput`) を callback で受けて
  `CGEventTapEnable(tap, true)` で即再有効化する。
- `hook_macos.rs`: OS 都合の失効 (`:637`/`:612` の runloop 退出) で `LAST_KEY_MS=0` にしない。
- プローブ駆動側 (`lib.rs:1608`): `last_key==0` を「idle 不明 → away 寄り (発火しない)」に倒す保守設計。
- `probe_scheduler.rs`: 上記駆動ロジックを純関数に切り出し、回帰テストを追加。

### 含まないもの
- Windows silent-unhook (callback timeout) 検出/復旧 → Phase2。
- 加速度センサー等、F4 と無関係な macOS 既知制約。
- HMM 挙動の変更 (features/engine は不変、`HMM_VERSION` bump なし)。
- `schema_dto.rs` の変更。

## 受け入れ条件

- [ ] OS 都合の tap 失効で `LAST_KEY_MS` が 0 にリセットされない (コードレビュー + 純関数テスト)。
- [ ] `idle` が途中で 0 に戻る系列でも away 中はプローブが発火しない (回帰テスト green)。
- [ ] `TapDisabledByTimeout`/`ByUserInput` を callback で再有効化する経路がある。
- [ ] `cargo test --workspace` green。
- [ ] HMM 不変: `gse-replay --snapshot tests/snapshots/minimal.json` 現状一致。
- [ ] `hook-constraints` 厳守 (callback 内は Atomic + 軽量 FFI のみ、ブロッキング/heap/log なし)。

## 関連ドキュメント

- `.steering/20260627-phase1-1-smoke-verify-closeout/phase2-followups.md` (F4 全文)
- `.steering/20260627-phase1-1-smoke-verify-closeout/next-session-prompt.md` (本タスク指示)
- `hook-constraints` / `rust-standards` / `architecture-rules` Skill

## 運用メモ
- /reimagine 適用: No
- 理由: 根本原因が前タスクで特定済みで、対処方針 (callback 再有効化 + idle 非リセット +
  プローブ away 保守化) が一意に定まっている。設計空間が広くないためゼロ再生成の便益が薄い。
