# タスクリスト

## 実装

- [x] `input/liveness.rs` 新規: 純関数 `step()` / `health()` ＋ `HookHealth` / `Thresholds` / `Starvation`
- [x] `input/liveness.rs`: `system_idle_ms` ではなく **`last_system_input_tick()`（生 tick の変化）**
      ★ `GetTickCount64` が features に無かったため差分方式に変更 → **依存追加もラップアラウンド検討も不要**になった
- [x] `input/mod.rs` に `pub mod liveness;`
- [x] `input/hook.rs`: `HOOK_STARVED` 追加 ／ `CALLBACK_COUNT` を両 OS 共通化 ／ `request_reinstall()`
- [x] `input/hook_windows.rs`: コールバックに `CALLBACK_COUNT.fetch_add` ／ `REINSTALL_REQUESTED` ／ `unhook_all()`
- [x] `logger.rs`: `LogEntry::HookHealth` の追加と NDJSON 書き出し
- [x] `schema_dto.rs`: `LogEntryDto::HookHealth` variant
- [x] `lib.rs`: 1 Hz 監視スレッド（★ 再設置は **1 エピソード 1 回**・復帰行にピーク値・`try_send` 失敗をログ）
- [x] `lib.rs`: `get_diagnostics` に `hook_starved` / `callback_count`（⚠️ `get_hook_status` は**意図的に不変**）
- [x] `tray.rs`: `HOOK_ACTIVE && !HOOK_STARVED`
- [x] `bin/replay.rs`: `ReplayEvent::HookHealth`（⚠️ **無いと `--snapshot` が丸ごと落ちる**）
- [x] `schema/current.json` を `emit_schema` で再生成

## 検証（★ すべて実測）

- [x] `assess` 系の単体テスト **7 件**（正常 / 両閾値 / ⚠️ マウスのみ / 非活性 / 沈黙の凍結 / 復帰 / `None`）
- [x] ★★ **わざと壊して赤を実測**（純関数 3 通り）
      - A 比較の向き `>=`→`>` → **2 件赤**（`silent_hook_...` の「120 秒ちょうど」と `mouse_only`）
      - B `session_active` 判定を外す → **1 件赤**
      - C 沈黙時の凍結をやめる → **2 件赤**
- [x] ★★ replay 回帰も**空回りしていないことを実測**（serde タグを壊す → 赤 → 復元して緑）
- [x] `cargo test --workspace` **315 passed / 0 failed**（従来 308 → +7）＋ replay 24（従来 23 → +1）
- [x] `gse-replay --snapshot` ゴールデン **15 snapshots match**（byte-equal）
- [x] `emit_schema` 出力が `schema/current.json` と **byte-equal**
- [x] `cargo fmt --check` 緑 ／ clippy **新規警告なし**（警告位置が diff 範囲外であることを実測）／ `tsc --noEmit` 緑
- [x] ⚠️★ Windows ターゲットの `cargo check` は **build script が `llvm-rc` を要求して不可**
      → ★ **API 呼び出しだけを隔離した最小クレートで型検査**した
      （`GetLastInputInfo` / `UnhookWindowsHookEx` / `UnhookWinEvent` / `PostThreadMessageW` の署名一致を実測）
- [ ] ⚠️★★ **Windows 実機での発火確認は未実施**（開発機は macOS。★ 「動くはず」と書かない）

## レビュー

- [x] `code-reviewer` ＋ `security-checker`（並列）→ **HIGH 2 件**を修正
- [x] ★ `/cross-review`（Claude ∥ Codex）**実施。縮退なし**（機密なし / 予算 0 used / codex あり）
      → 両者一致 HIGH **1 件**（誤検知中に生きたフックを壊し続ける）を修正
- [x] Codex 単独指摘: 一時ファイル名に PID（採用）／ MSRV・トレイ誤表示（★ 一次資料で**不成立**と判定）
- [x] HIGH 全対応（合計 3 件）

## 仕上げ

- [ ] `docs/functional-design.md` に機能追記
- [ ] `windows-verification.md` §5-6 の提案表を「実装済み」に更新
- [ ] git コミット（`git-workflow`・`Refs:` 付き）

## ⚠️ 次タスクへ送るもの

- [ ] macOS への配線（`CGEventSourceSecondsSinceLastEventType`）— D-4
- [ ] ⚠️ `CALLBACK_COUNT` は macOS のタップ再作成時に **0 リセット**される（`hook_macos.rs:713`）。
      ★ 今は macOS が常に `system_input_seen=false` なので無害だが、**配線した瞬間に偽の生存シグナルになる**
- [ ] ⚠️ `CALLBACK_COUNT` は「呼ばれた回数」であって「記録できた回数」ではない
      → `try_send` が詰まって捨てられても `alive=true` になる（security-checker MEDIUM・未対応）
- [ ] ⚠️ `hook_health` を**読む消費者がまだ居ない**（`analyze.py` / `validate_blocks.py` 側）
- [ ] ⚠️ `gse-dataset` 側 `schema/current.json` に `hook_health` を反映しないと提出検証が落ちる
      （★ `check_schema_parity.py` で `Missing variants in B: hook_health` を実測済み）
- [ ] ⚠️ `packaging.rs::has_any_data_row` が `hook_health` を data row と数える（空セッション検出が緩む）
- [ ] ⚠️ `step()` に渡す `tick_ms` が公称値で実測ではない（`starved_ms` が実時間とずれうる）
