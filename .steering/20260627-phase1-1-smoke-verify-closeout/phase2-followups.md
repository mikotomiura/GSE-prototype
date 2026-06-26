# Phase2 follow-up（codex consult 由来・2026-06-25 / Phase1 では未着手）

ユーザー確定: Phase1 配布は現状の fail-loud 修正で進め、以下は **Phase2 送り（記録のみ）**。

## F1. 初回起動セルフチェック ＋ 診断コード
- 起動時に「権限OK / hook 受信OK / ログ書込OK / 残容量OK」を一括判定。
- 失敗時は研究者に送れる **診断コード**（機微情報を含まない）を UI 表示。
- 狙い: A 配布の真のリスク＝「インストール成功」ではなく「権限付与後に正しく動作している証明」を埋める。
- 影響: `lib.rs`（起動シーケンス・新 IPC）/ `Dashboard.tsx`（診断バナー）。`data-privacy` 厳守（キー内容は出さない）。

## F2. ログ全損対策を `File::create` 超えに拡張
現行の層2（temp フォールバック＋fail-loud バナー）が埋めていない残存経路:
- ディスク満杯 / 実行中の権限変更 / スリープ復帰 / ローテーション失敗 / JSON 書込途中クラッシュ / 排他競合。
- 対策候補: 追記成功カウンタ、flush・fsync 方針の明確化、定期 heartbeat、最終書込時刻の UI 表示、
  起動時の前回異常終了検出。
- 影響: `logger.rs`（consumer loop・sink）。HMM/schema 不変を維持。回帰テスト先行（TDD）。

## F4. macOS CGEventTap 失効による idle/away 誤リセット（ユーザー報告 2026-06-25・macOS 確定）
- **症状**: 長時間 Idle 中に Dashboard の `Idle Ns` カウンタが突然 0 に戻る。
- **機構**: 待機中に macOS がイベントタップを失効（`kCGEventTapDisabledByTimeout` または
  スリープ/ディスプレイスリープ復帰）→ `CFRunLoop::run_current()` が抜け（`hook_macos.rs:633-642`）→
  `LAST_KEY_MS.store(0)` ＋ 2 秒後に**タップを丸ごと再インストール**。`get_keyboard_idle_ms()` は
  `last==0` で 0 を返すため（`lib.rs:429`）カウンタが 0 表示になる。
- **影響評価**:
  - HMM 状態推定: ほぼ無害（Idle 中は打鍵なし＋沈黙は合成特徴量。打鍵中に落ちた場合のみ ~2s 取りこぼし）。
  - **away 判定（研究妥当性に効く・要注意）**: `probe_scheduler` は `idle_ms ≥ 180_000` で離席棄却
    （`probe_scheduler.rs:206`）。失効で idle_ms が 0 リセットされると**離席中でも「在席」と誤判定 →
    離席中にプローブ発火 → 空回答/汚染データ**。intervention の idle ゲートも同様に揺れる。
- **推奨対応**:
  1. `kCGEventTapDisabledByTimeout`/`ByUserInput` を受けたら**タップ作り直さず即 `CGEventTapEnable(tap,true)`**
     で再有効化（軽量・取りこぼし最小）。現タップ登録は `KeyDown`/`KeyUp` のみ（`hook_macos.rs:577`）で
     この再有効化ハンドラが無い。
  2. **OS 都合の一時失効では `LAST_KEY_MS=0` にしない**（セッション境界の真リセットと区別）。これだけで
     away 誤リセットは解消。
  3. 失効頻度は `hook_macos.rs:638` の warn ログ（"CGEventTap CFRunLoop exited…"）で定量化可能。
- **Windows 厳密調査結果（2026-06-25）**: **同症状（待機中の 0 リセット）は Windows では起きない**。
  Windows のメッセージループ（`hook_windows.rs:216-226`）は **`WM_QUIT`（アプリ終了）でしか抜けない**。
  watchdog も health ベース再インストールも無く、`WH_KEYBOARD_LL` は待機中に OS から外されない →
  `LAST_KEY_MS` 保持 → カウンタは正しく増加 → away ゲート正常。
  ただし Windows には**別の低頻度ギャップ**: `WH_KEYBOARD_LL` が callback タイムアウト
  （`LowLevelHooksTimeout` 既定 ~300ms 超過）で**サイレント unhook** された場合、`WM_QUIT` は来ないため
  ループは回り続け、**`HOOK_ACTIVE` が stale-true（誤検出）・`last_key` 凍結**のまま打鍵が静かに止まる。
  検出/復旧コードが無い。ただし本コードの callback は Atomic store＋非ブロッキング channel send のみで
  高速なため発生確率は低い。**症状は macOS と逆（0 に戻らず増加し続ける）**。Phase2 で silent-unhook
  検出（CALLBACK_COUNT 監視 or 定期 re-hook）を検討。

- **ランダムプローブのバグ（F4 と同根・2026-06-25）**: 駆動側は `last_key==0 → idle=0`（`lib.rs:1608`）。
  `last_key==0` は (a) セッション開始前の未打鍵、(b) **macOS: 待機中の tap 再インストール毎（F4）** で成立。
  (b) では離席中（idle 数分）でも idle が 0 にリセット → `away=false`（`probe_scheduler.rs:206`）→
  **離席中にランダムプローブが発火 → 空回答/汚染**。F4 の修正（OS 都合の失効で `LAST_KEY_MS=0` にしない）で
  両方解消。加えて保守的化として「idle 不明（last_key==0）を `away` 寄りに扱う」案も検討余地
  （ただしセッション開始直後の挙動が変わるため要設計判断）。

- **Phase1 前倒し判断**: F1/F2/F3 と違い、away 汚染（macOS）＋ランダムプローブ誤発火は **Phase1 データに直接効く**ため、
  **F4 のみ Phase1 前倒しを推奨**。次タスクプロンプト（`next-session-prompt.md`）に反映済み。

## F3. 盲検の非 env 漏洩経路の点検
- UI 文言・ログファイル名・通知・メニュー・プロセス名・設定ファイル・配布ファイル名から
  Week1/2 の条件が推測されないか点検。Week1/2 を同一バイナリ・同一起動導線に保つ。

## 起点（次セッションで読む）
- 本タスク `launch-method-decision.md`（codex 盲点 1-4 の原文）。
- 前タスク `.steering/20260626-phase1-card-repro-backend-fix/decisions.md`（層2 のスコープ＝判断1）。
- `src-tauri/src/logger.rs`（consumer・open_log_target・LogStatus）。
