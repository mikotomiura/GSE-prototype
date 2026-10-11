# tasklist

設計は 2026-10-11 に研究者が承認した（design.md）。

## PR1 — 記録とモード
- [ ] `eh3.rs`: 印 `eh3.mode` の解析（order・a_first・grammar・drift）・モードの決まり方（O1 前提・G1 優先）・テスト
- [ ] 稼働日の数え方（4:00 区切り・打鍵 1 回）と条件の決定・`~/.gse/eh3_state.json`・テスト
- [ ] `lib.rs`: EH3 の分岐（`INVITATION_ENABLED`・O1 の ESM を切る・Nudge は偽のまま）
- [ ] `meta` の断片 `eh3_mode` / `invitation_enabled`（`logger.rs`）・EH3 でないとき空のテスト
- [ ] 行種 `eh3_day` / `invitation_present`: `schema_dto.rs`・`logger.rs`・`capabilities.rs`・`replay.rs`・`redaction.rs`・`anonymize.rs`
- [ ] `emit_schema` → `schema/current.json`・parity・capabilities_gate
- [ ] `sync-session.{sh,ps1}` の振り分け
- [ ] cargo test / clippy / replay snapshot → code-reviewer ∥ security-checker → コミット・PR

## PR2 — 招待
- [ ] `analysis/invitation.rs` 状態機械と §3.5 のテスト（陽性対照つき）
- [ ] `lib.rs` の 1Hz の差し込み・`get_invitation_state`・設定の保存と IPC
- [ ] `InvitationGlyph.tsx`（候補 3 つ）・`Overlay.tsx` の表示・画面共有の除外
- [ ] 説明と設定の窓（`InvitationSettings.tsx`）・トレイの入口
- [ ] `check_invitation_surface.py`（M11 の 4 条件・`--selftest`）を CI に
- [ ] tsc / cargo test / clippy → レビュー → コミット・PR

## PR3 — 肖像と壁紙
- [ ] `analysis/portrait/`: canvas・generator（raw / lattice × none / diffuse）・schedule（recent）・decor・ending・テスト
- [ ] Python との移植の検算（一時スクリプト・結果を decisions に）
- [ ] `input/power_{windows,macos}.rs`（スリープの直前の通知）
- [ ] `wallpaper.rs` ＋ `wallpaper_windows.rs` / `wallpaper_macos.rs`（保存・書き込み・本人の差し替えの検出・復元の読み戻しと SHA-256・異常終了の後の復元）
- [ ] `lib.rs` の結線（終わり・始まり・期間の後・トレイの「研究を終える」）
- [ ] 肖像への操作が出力に写らない試験（§4.4・陽性対照つき）
- [ ] Windows 実機の手動確認（復元・異常終了・再起動・スリープ・複数モニタ・本人の差し替え）
- [ ] レビュー → コミット・PR

## PR4 — 配布と文書
- [ ] `docs/eh3-distribution-tag.md`・同意文書の記録項目と participant-guide の案
- [ ] functional-design / glossary / architecture / repository-structure / agent-shared の制約 11
- [ ] ADR-035 の見直しの記録・研究者に Accepted を聞く
- [ ] 図像の見本・形の文法の見本を研究者に見せる（F-1・F-3）
- [ ] macOS 実機の引き継ぎ
- [ ] /finish-task（/cross-review 2 巡）
