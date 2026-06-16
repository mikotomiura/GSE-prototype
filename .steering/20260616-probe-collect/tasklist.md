# タスクリスト — Task C frontend 収集

## 準備
- [x] v0.3 §3/§4/§6/§14/原則5 精読、DB-4(B↔C 契約)確認
- [x] logger 構築子(realtime_label_*/SessionMeta/VignetteResponse)・enum parse・ProbeRef 確認
- [x] frontend 既存パターン(App.tsx routing / Overlay.tsx listen+invoke)確認

## 設計 (/add-feature Step 3 → 2案比較)
- [x] DC-1 カード配置 = Overlay(承認)
- [x] DC-2 起動導線 = start 画面宣言 + ビネット導線(承認)
- [x] design.md 最終化

## 実装 — backend
- [x] logger.rs: `LogEntry::vignette_response` clamp 構築子(DC-4)
- [x] probe_scheduler.rs: `ProbeId::is_valid(&str)` + テスト(DC-3)
- [x] lib.rs: `record_session_meta`(Track/TaskKind parse)
- [x] lib.rs: `record_realtime_answer` / `record_realtime_skip`(source/probe_id 検証 → ProbeRef → 構築子)
- [x] lib.rs: `record_vignette_response`(ExpectedQuadrant parse + vignette_id 検証 → 構築子)
- [x] lib.rs: `generate_handler!` に 4 command 登録

## 実装 — frontend
- [x] 共有型 `probeTypes.ts`(any 禁止)
- [x] `ProbeCard.tsx`: probe_triggered listen + Q1/Q2 slider + skip(2択) + latency 計測 → answer/skip command
- [x] `VignetteTest.tsx`: 8 シナリオ(§6.3)→ vignette_response、PreReg-1 ゲート表示(client-side feedback)
- [x] App.tsx: start 画面に task_kind 宣言 + ビネット導線 + handleStart で record_session_meta
- [x] Overlay.tsx: ProbeCard mount + 表示中の cursor events 制御

## テスト
- [x] ProbeId::is_valid 単体(有効/長さ/不正文字/マルチバイト/インジェクション様)
- [x] vignette_response clamp 単体(0→1, 9→5)
- [x] `cargo test --lib` 112 緑(既存不変)/ `cargo clippy` 新規警告ゼロ / `npm run build`(tsc)緑

## レビュー (並列起動)
- [x] code-reviewer + security-checker 並行 + test-runner(112 緑)
- [x] security: CRITICAL/HIGH/MEDIUM なし(三重防御・本文非到達を確認)
- [x] code-reviewer MEDIUM 対応: 送信成功後遷移(DC-6)・取りこぼし warn・Wall 非共存(DC-7)
- [x] 受容項目を根拠付きで decisions.md に記録(DC-8)

## 完了処理
- [x] design.md / decisions.md 最終化(DC-1..DC-8)
- [ ] /finish-task(parity guard は skip 想定)→ commit
