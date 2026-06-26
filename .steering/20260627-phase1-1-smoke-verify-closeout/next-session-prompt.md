# 次セッション用 開始プロンプト（macOS フック失効 → idle/away 誤リセット ＆ ランダムプローブ誤発火の修正）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 前タスク `20260627-phase1-1-smoke-verify-closeout`（#1 backend 層2 のスモーク検証＆クローズアウト）は完了。
> 機械的検証（cargo test / gse-replay / tsc）グリーン、起動方法 A＋C 確定、事後アンケート GAS 実装済み確認。
> 本タスクはそこで発見した **F4（Phase1 前倒し確定分）** の修正。

---

## 依頼
macOS で待機中に CGEventTap が OS により失効 → 再インストール時に `LAST_KEY_MS=0` リセットされ、
**(1) Dashboard の idle カウンタが 0 に戻る、(2) idle/away 判定が壊れる、(3) 離席中にランダムプローブが
誤発火して空回答/汚染データになる** 問題を根治する。
実装系なので **`/start-task`**（task-name=`macos-tap-idle-away-fix`、または本クローズアウト dir を引き継ぎ）で
steering を起こす。**`/fix-bug`**（TDD: 回帰テスト先行）で進める。`*.rs` は `architecture-rules`/`rust-standards`/
`hook-constraints` 必須参照。`input/` の OS フック変更のため `hook-constraints` Skill を必ず読む。

## 確定済みの根本原因（前タスクで特定）
- `get_keyboard_idle_ms()`（`lib.rs:427`）＝`now - LAST_KEY_MS`。**`LAST_KEY_MS==0` で 0 を返す**（`:429`）。
- `LAST_KEY_MS` が 0 にストアされるのは **OS がフックを失効させ再インストールする時のみ**:
  - macOS: `hook_macos.rs:637`（CGEventTap 失効・CFRunLoop 退出）/ `:612`（runloop source 生成失敗）
  - Windows: `hook_windows.rs:231`（メッセージループ退出＝`WM_QUIT` のみ＝**アプリ終了時だけ**）
- macOS の tap は **`KeyDown`/`KeyUp` のみ登録**（`hook_macos.rs:577`）で、`kCGEventTapDisabledByTimeout`/
  `ByUserInput` を受けて `CGEventTapEnable(tap,true)` で**再有効化する標準ハンドラが無い** →
  失効時にタップ丸ごと作り直し＋2秒 sleep＋`LAST_KEY_MS=0` に倒れている。
- **ランダムプローブ誤発火（同根）**: 駆動側 `last_key==0 → idle=0`（`lib.rs:1608`）。離席中に tap 再インストール
  されると idle が 0 リセット → `away=false`（`probe_scheduler.rs:206`、`away_idle_ms=180_000`）→
  離席中にプローブ発火。
- **Windows は本症状なし（厳密確認済み）**: メッセージループは `WM_QUIT` でしか抜けず待機中に
  `WH_KEYBOARD_LL` は外れない → `LAST_KEY_MS` 保持 → away 正常。Windows の別ギャップ（callback timeout の
  silent unhook → stale `HOOK_ACTIVE`・`last_key` 凍結、検出/復旧なし）は**症状が逆**で発生確率低 → 本タスク対象外、Phase2。

## やること（着手順）
### 1【macOS フック失効の軽量復旧】（主修正）
- `hook_macos.rs` の tap 登録に `kCGEventTapDisabledByTimeout` / `kCGEventTapDisabledByUserInput` を含め、
  callback でこれらを受けたら **タップを作り直さず即 `CGEventTapEnable(tap, true)` で再有効化**する。
  作り直し＋2秒 sleep の重い経路は「本当に invalidate された時」だけに限定する。
  ※ `core-graphics` 0.23 の API 表面（`CGEventTapEnable` 相当 / `CGEventType` の disabled バリアント）を
    ソースで確認。`CGEventType` は `PartialEq` 未実装なので `matches!` を使う（既知 gotcha）。
- `hook-constraints` 厳守: callback 内は Atomic＋channel のみ、ブロッキング禁止。再有効化呼び出しの可否を確認
  （callback 内で安全に呼べるか、別経路が要るか）。

### 2【idle/away を OS 都合の失効で壊さない】（研究妥当性の核）
- **OS 都合の一時失効では `LAST_KEY_MS=0` にしない**。`hook_macos.rs:637`/`:612`（必要なら `:231` も）で、
  「セッション境界の真リセット」と「OS 都合の一時失効」を区別する。後者では `LAST_KEY_MS` を保持し、
  idle/away が連続性を保つようにする。
- 代替案として `last_key==0` の sentinel を「idle 不明」として扱い、プローブ駆動側で**不明時は away 寄り
  （発火しない）に倒す**保守的設計も検討（`lib.rs:1608` / `get_keyboard_idle_ms`）。ただしセッション開始直後の
  挙動が変わるため**設計判断（decisions に記録）**。憶測で確定せずトレードオフを明記。

### 3【テスト（TDD 先行）】
- `probe_scheduler` は純ロジックなので、**idle が途中で 0 に戻る系列でも away 中は発火しない**ことを
  検証する回帰テストを追加（now/idle を直接渡せる既存 `simulate` 系を活用）。
- フック層（OS API）は `cargo test` で直接検証困難 → ロジックを純関数に切り出してテスト可能にするか、
  最低限「`LAST_KEY_MS` 保持/リセットの分岐」を単体化する。
- `cargo test --workspace` パス。**HMM 不変**（features/engine を触らない）なら
  `gse-replay --snapshot tests/snapshots/minimal.json` 現状一致を確認。`schema_dto.rs` を触らない。

### 4【リビルド & 実機検証（研究者作業）】
- `smoke-test-runbook.md` 準拠で本番ビルド起動。**長時間 Idle で idle カウンタが 0 に戻らない**こと、
  `hook_macos.rs:638` の "CGEventTap CFRunLoop exited" warn が（失効頻度として）減ることを確認。
- 離席（3分以上 idle）中にランダムプローブが発火しないことを確認（デバッグでは時間がかかるため、
  必要なら `away_idle_ms` を一時的に短縮した検証ビルドで確認し、本番値に戻す）。

### 5【完了処理】
- code-reviewer ＋ security-checker（`input/` フック変更）→ `/finish-task` で `/cross-review`。
- ブランチ: 新規 `fix/macos-tap-idle-away`（#1 とは別 PR で良い）。

## 真実源（先に読む）
- 本クローズアウト dir `phase2-followups.md`（F4 全文・Windows 厳密調査・ランダムプローブ同根の記述）。
- `src-tauri/src/input/hook_macos.rs`（230 handle_event / 573-642 tap 作成・失効・再インストール・`LAST_KEY_MS=0`）。
- `src-tauri/src/input/hook_windows.rs`（169-238 ループ・`WM_QUIT` のみ退出・`:231` reset）。
- `src-tauri/src/lib.rs`（427 `get_keyboard_idle_ms`・1567- プローブ駆動スレッド・1608 idle 計算）。
- `src-tauri/src/analysis/probe_scheduler.rs`（195 poll・206 away・107-118 ProbeConfig）。

## 制約
- NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない（data-privacy）。
- `analysis/` で OS API を直接呼ばない（OS 依存は `input/` に閉じる）。`winapi`/`println!`/`eprintln!` 禁止、`tracing` のみ。
- 既存テストを無断削除しない。HMM 挙動を変えるなら `HMM_VERSION` bump＋ゴールデン再生成（本タスクは HMM 不変が前提）。
- diff に未関係な未ステージ変更（budget.json/scripts/docs削除/MEMO/advice.md）を混ぜない。
- フック層の OS 都合復旧は推測で広げず、F4 のスコープ（macOS tap 再有効化＋idle 非リセット＋プローブ away 健全化）に限定。
  Windows silent-unhook 検出は Phase2（本タスク対象外）。
