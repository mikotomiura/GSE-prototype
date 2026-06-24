# 設計（#1 プローブ/Nudge カードのボタン無反応・出っぱなし）

## 根本原因（調査結果）

両カードは **backend コマンドが成功したときだけ閉じる**設計。3 コマンド
（`record_realtime_answer` / `record_realtime_skip` / `record_intervention_dismiss`）の
唯一の共通失敗点は **bounded log channel `tx.try_send`**（`logger.rs:789` で `bounded::<LogEntry>(512)`）。

- 静的検証で deterministic な parse 失敗は否定:
  - `InterventionAction::parse("nudge")` → `Some(Nudge)`（`intervention.rs:39`）。
  - `ProbeSource::parse` / `ProbeId::is_valid` は backend が emit した値が round-trip するため整合。
  - `parse_dismiss_reason("not_stuck"|...)` 全受理。
- consumer（`SessionLogger::start` の専用スレッド `logger.rs:793-`）はアプリ setup で常時 drain。
  → 「毎回 full」になるのは **(a) consumer スレッド死亡**（`File::create` 失敗で `logger.rs:799-804` が
  early return → 以後 `try_send` は **Disconnected**）か **(b) 真の backlog で 512 滞留**のいずれか。
  crossbeam の `TrySendError` Display は Full="sending on a full channel" /
  Disconnected="sending on a disconnected channel" で区別可能だが、コマンドは両方を
  `"log channel full: {}"` で潰しており**ラベルが誤誘導**（disconnected を full と表示）。

フロント側の「失敗時保持」設計が、この backend Err を**ユーザー可視のバグ**に変換:
- ProbeCard（`ProbeCard.tsx:63-91`）: 成功時のみ `setProbe(null)`。失敗で**死んだボタン**化。
- Nudge（`Overlay.tsx:63-76` + effect `259-284`）: 失敗 catch で `setNudgeDismissed(false)` →
  effect が `action===nudge` のまま即再表示 → **押す→消える→即再表示の無限ループ**。

## 実装アプローチ（2 層に分離）

### 層1: フロント UX 修正（本セッションで実装・backend エラー種別に非依存）
「データを静かに失わない」意図は維持しつつ、**無限再表示ループと死んだボタン化を断つ**。

- **ProbeCard**: `error: string | null` state を追加。invoke 失敗時に**カードを保持**したまま
  インラインのエラー文＋「もう一度」を表示（ボタンは再有効化 = リトライ）。成功で `setProbe(null)`。
- **Nudge（Overlay）**: `handleNudgeDismiss` を **await 化**。成功時のみ `nudgeVisible=false`+`nudgeDismissed=true`。
  失敗時は**カードを保持**しインラインエラー表示、**`setNudgeDismissed(false)` の再表示ループを廃止**
  （ボタン再押下がリトライ）。silent timeout（`267-277`）の失敗も同様にカード保持＋エラー表示に変更
  （`setNudgeDismissed(false)` ループを廃止）。
- 参加者向け文言は固定の和文（生エラー文字列は UI に出さない＝余計な不安/情報露出回避）。
  生エラーは既存の `console.error`（`ProbeCard.tsx:74,87` / `Overlay.tsx:71,273`）に残し devtools で確認。
- `typescript-standards`: `any` 禁止・IPC 型維持。`intervention-design`: Nudge 保持/silent 仕様維持。

### 層2: backend 根本修正（**実エラー文字列の確定後**に実装）
- repro の `console.error` 文字列が **Full か Disconnected か**で分岐:
  - Disconnected（consumer 死亡）→ `logger.rs` の consumer を **`File::create` 失敗で死なせない**
    （フォールバック先へ再作成 or 明示エラー伝播）+ 起動順/パス検証。
  - Full（真の backlog）→ チャネル容量・drain 律速の是正（coalesce 不可な realtime_label は
    落とさない方針を維持）。
- 併せて **誤誘導ラベル是正**: `"log channel full"` を Full/Disconnected で文言分岐（診断容易化）。
- backend 変更時は回帰テスト先行（TDD 順序）。`logger.rs` 変更は security-checker 必須。

## 変更対象
### 修正するファイル（層1）
- `src/components/ProbeCard.tsx` — error state + インラインエラー/リトライ表示。
- `src/components/Overlay.tsx` — handleNudgeDismiss await 化・再表示ループ廃止・nudge エラー表示。
### 修正するファイル（層2・エラー確定後）
- `src-tauri/src/logger.rs` — consumer 耐障害化（該当時）。
- `src-tauri/src/lib.rs` — try_send エラー文言の Full/Disconnected 分岐。

## 影響範囲
- `src/components/{ProbeCard,Overlay}.tsx` のみ（層1）。HMM 挙動・NDJSON schema は不変 →
  ゴールデン/Schema 再生成不要。`logger.rs` を触る層2 のみ security-checker トリガー。

## テスト戦略
- フロントにテストハーネス無し（vitest/jest 不在）→ 層1 は **実機手動確認**
  （ボタン押下で確実に閉じる／失敗継続時にエラー表示＋リトライ可／無限再表示が起きない）。
- 層2 backend は `cargo test --workspace` に回帰テスト追加（consumer 耐障害 or 文言分岐）。
- HMM 不変のため `gse-replay --snapshot` は現状維持で回帰確認。

## ロールバック計画
- 層1 は 2 ファイルの差分のみ → revert 容易。層2 は logger/lib の最小差分に限定。

## ユーザー確認が必要な事項
1. 層1 UX 修正の方針承認（カード保持＋インラインエラー＋リトライ、生エラーは UI 非表示）。
2. **repro の devtools `console.error` 文字列**（"...full channel" か "...disconnected channel" か）。
   これが層2 backend 修正の確定情報。
