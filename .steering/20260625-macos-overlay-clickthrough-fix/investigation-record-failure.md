# 調査: 「記録に失敗」(record_realtime_* / record_intervention_dismiss) — 2026-06-26

引き継ぎ HANDOFF-nspanel-DONE-and-record-failure.md §2 の主タスク。NSPanel 化でクリックが
効くようになった結果露出したとされる「記録に失敗しました」インラインエラーの調査。

## 静的解析で消し込んだ決定的原因 (deterministic causes ELIMINATED)

1. **channel Disconnected** … 構造的にありえない。`SessionLogger::start` (logger.rs:899) は
   `open_log_target` で書込先を **spawn 前に同期確定**し、失敗時も temp→`io::sink()` へ縮退して
   **consumer スレッドを必ず spawn** する (commit 342a444 / 別タスク 20260626-phase1-card-repro-backend-fix)。
   よって `try_send` が Disconnected を返す経路は消えている。
2. **build_probe_ref 不正** … 3 つの probe_triggered emitter (debug_force_probe=random_probe・
   M ホットキー=self_marker/probe_id=null・実スケジューラ=random_probe) は **全て有効入力**を作る。
   ID は常に `ProbeId::generate` (16 文字 base64url)、`is_valid` と一致。self_marker は probe_id=None で OK。
3. **window_end < window_start** … 窓は self_marker_window_clamped / FiredProbe 由来で順序保証。
4. **コード regression なし** … `git diff HEAD` で record_realtime_* / record_intervention_dismiss /
   try_send / LogState / build_probe_ref / logger.rs は **working tree = コミット版で byte-identical**。
   このオーバーレイ task の変更は記録パスを一切触っていない。全コマンドは invoke_handler に登録済み。
5. **capability gating ではない** … Tauri 2.0 で generate_handler のアプリ独自コマンドは capability
   ゲート対象外 (capability は core:/plugin コマンドのみ)。record_* は任意ウィンドウから呼べる。

## NDJSON 実証 (records DID succeed)
`~/Documents/GSE-sessions/` の Jun26 セッション:
- 14:04 / 14:14 / 14:16 で **source=random_probe の realtime_label が成功して着地**
  (= debug_force_probe → ProbeCard クリック → record_realtime_answer 成功)。primary パス着地 = LogStatus::Ok。
- 最後の 14:29 (gse_20260626_052909) は realtime_label=0・intervention_response=0、real `defer` 判定2件のみ。

## 残る可能性 (need live error to distinguish)
- **channel Full** (bounded(512))。ただし consumer は連続 drain するため実質到達困難。
- **stale build** … ユーザーが最後に走らせたビルドが現 working tree と異なり、再ビルドで再現しない可能性。
- **NSPanel overlay 固有の IPC transport 失敗** (record コマンド到達前)。

## 仕込んだ計器 (DIAG TEMP・検証後に §3 と一緒に要除去)
4 つの catch を `void invoke("fe_dbg", { msg: \`record_... FAILED: ${String(e)}\` })` で計装:
- `src/components/ProbeCard.tsx` submitAnswer / submitSkip
- `src/components/Overlay.tsx` nudge dismiss / silent dismiss
→ backend が返す**正確な Err 文字列**が `npm run tauri dev` ターミナルに `[FE] record_... FAILED: <e>`
として出る。`log_send_error` が Full / Disconnected を区別する。

## ★真因確定 (2026-06-26 live repro)
ターミナル計器が出した正確な Err:
```
[FE] record_realtime_answer FAILED: window_end_ms must be >= window_start_ms
[FE] record_realtime_skip   FAILED: window_end_ms must be >= window_start_ms
```
**channel 問題ではなかった** (commit 342a444 の backend 修正は正しく無関係)。真因 =
`self_marker_window_clamped` (probe_scheduler.rs:65) の**窓終端非クランプによる反転**:
- 窓始端のみ `session_start` にクランプ、終端 `t−5s` は未クランプ。
- プローブ/マーカーが**起動 5s 以内**に発火すると `we = t−5s < session_start ≤ ws` で反転。
- `record_realtime_*` の `we >= ws` 検証で弾かれ Err → 「記録に失敗」。try_send には到達しない。
- live repro: session_start=1782455891153 / probe=1782455895487 → elapsed 4334ms<5000 → 反転。
- NDJSON 14:04–14:16 が成功していたのは、たまたま起動 5s 超で叩いていたため。
- 実スケジューラは 31s ウォームアップで到達せず安全。M/D 自己マーカーは起動直後押下で同バグ
  (実被験者でもラベル静的損失の縁) → 関数自体を修正。

## ★修正 (DONE)
`self_marker_window_clamped` に `let we = we.max(ws);` を追加し終端を始端以上にクランプ
(セッション未収窓は `[ws, ws]` ゼロ幅に畳む = 開始前データなしを正しく表現)。
回帰テスト `self_marker_window_clamped_never_inverts_within_5s_of_start` 追加。
検証: `cargo test --lib` 228 passed / replay snapshot 一致 (HMM 不変) / schema_dto 不変。

## 残: closeout
1. ★再現確認 (ユーザー): fix 込み再ビルドで起動直後にデバッグプローブ → `[FE] ... FAILED` が消え
   `realtime_label` が NDJSON に着地。
2. DIAG 全除去 (HANDOFF §3 の一覧 + 本調査で足した 4 つの fe_dbg エラー捕捉)。
3. cargo build / tsc / cargo test green。
4. code-reviewer + security-checker + /cross-review。
5. commit (git-workflow 準拠)。メモリ更新。
