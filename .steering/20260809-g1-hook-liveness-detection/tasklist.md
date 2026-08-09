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

## ✅ 積み残しの片づけ（2026-08-09・コミット `eb7eaf8`）

- [x] ⚠️ `CALLBACK_COUNT` は「呼ばれた回数」で「**記録できた回数**」ではない
      → `EVENTS_DROPPED` を追加し、`hook_health` に `dropped` を載せ、監視スレッドが `ERROR` を出す。
      ★ 併せて **コールバック内の `tracing::warn!`（`hook-constraints` 共通-1 の既存違反）も解消**
- [x] ⚠️ macOS の `CALLBACK_COUNT` 0 リセット → **廃止**（単調増加に）。
      ★ 残すと配線した瞬間に**偽の生存シグナル**（死んでいるのに Ok）になる
- [x] ⚠️ `packaging.rs::has_any_data_row` が診断行を data row と数える → 除外。
      ★ 3 状態（meta のみ / meta+診断行 / meta+打鍵）のテストを追加し、**除外を外して赤も実測**
- [x] ⚠️ `step()` の `tick_ms` が公称値 → `Instant` の**実測値**に
- [x] ★★ `hook_health` を**読む消費者**を実装（`validate_blocks.py::read_hook_health`）。
      `alive=false` → **FAIL**（「打鍵が少ない＝打たなかった」と読ませない）／ `dropped>0` → WARN。
      ★ selftest に**対照 2 本**（行が無い / `alive=true`）を含む 4 ケース。**3 通りの壊し方で赤を実測**
- [x] ⚠️ `gse-dataset` の schema 同期 → `~/gse-dataset` で `7cc8430` としてコミット（★ **push はしていない**）。
      `check_schema_parity` **OK (in sync)**。★ さらに使い捨て venv で `validate_schema.py` を走らせ、
      **`hook_health` 行が通ること**と、⚠️ **`dropped` を落とすと落ちること**（＝検査が空回りしていない）を実測

## ⚠️ この作業で**新たに見つかった**もの（★ 私の変更とは無関係）

- [ ] ⚠️★★ **`gse-dataset` の既存 NDJSON は schema 検証を通らない。**
      `raw/` の実ファイルは匿名化済みで `key` 行が `{"category":…}` だが、
      schema の `Key` variant は `{"vk": u32}` しか受け付けない
      → ★ **実測: 1 ファイルで 13,115 errors**。schema と匿名化パイプラインのどちらを正とするか判断が要る
- [ ] ⚠️★ **`cargo test --workspace` は `packaging` の 23 件を走らせない**
      （`#[cfg(feature = "package")]` の裏）。★ `--features package` を付けると 315 → **338**。
      `docs/agent-shared.md` のテスト手順がこれを取りこぼしている

## ⚠️ 次タスクへ送るもの

- [ ] macOS への配線（`CGEventSourceSecondsSinceLastEventType`）— D-4
- [ ] ⚠️ `analyze.py` 側の消費者（`validate_blocks.py` には入れたが `analyze.py` は未対応）
- [ ] ⚠️★★ **Windows 実機での発火確認**（★ ここが埋まるまで「動く」とは書かない）
