# tasklist

設計は 2026-10-11 に研究者が承認した（design.md）。

## PR1 — 記録とモード
- [x] `eh3.rs`: 印 `eh3.mode` の解析（order・a_first・grammar・drift）・モードの決まり方（O1 前提・G1 優先）・テスト
- [x] 稼働日の数え方（4:00 区切り・打鍵 1 回）と条件の決定・`~/.gse/eh3_state.json`・テスト
- [x] `lib.rs`: EH3 の分岐（`INVITATION_ENABLED`・O1 の ESM を切る・Nudge は偽のまま）
- [x] `meta` の断片 `eh3_mode` / `invitation_enabled`（`logger.rs`）・EH3 でないとき空のテスト
- [x] 行種 `eh3_day` / `invitation_present`: `schema_dto.rs`・`logger.rs`・`capabilities.rs`・`replay.rs`・`redaction.rs`・`anonymize.rs`
- [x] `emit_schema` → `schema/current.json`・parity・capabilities_gate
- [x] `sync-session.{sh,ps1}` の振り分け（変更不要: O1 の門で止まる・design §2.3）
- [x] cargo test / clippy / replay snapshot → code-reviewer ∥ security-checker（判断 4）→ コミット・PR

## PR2 — 招待
- [x] `analysis/invitation.rs` 状態機械と §3.5 のテスト（陽性対照つき）
- [x] `lib.rs` の 1Hz の差し込み・`get_invitation_state`・設定の保存と IPC
- [x] `InvitationGlyph.tsx`（候補 3 つ）・`Overlay.tsx` の表示・画面共有の除外
- [x] 説明と設定の窓（`InvitationSettings.tsx`）・トレイの入口
- [x] `check_invitation_surface.py`（M11 の 4 条件・`--selftest`）を CI に
- [x] tsc / cargo test / clippy → レビュー（判断 5・6）→ コミット・PR
- [ ] 実機（Windows）で図像の表示・失効・説明と設定の窓・画面共有からの除外を確かめる（PR3 の実機の確認と一緒に）

## PR3 — 肖像と壁紙
- [x] `analysis/portrait/`: canvas・generator（raw / lattice × none / diffuse）・schedule（recent）・decor・ending・テスト
- [x] Python との移植の検算（一時スクリプト・結果を decisions に）
- [x] `input/power_{windows,macos}.rs`（スリープの直前の通知）
- [x] `wallpaper.rs` ＋ `wallpaper_windows.rs` / `wallpaper_macos.rs`（保存・書き込み・本人の差し替えの検出・復元の読み戻しと SHA-256・異常終了の後の復元）
- [x] `lib.rs` の結線（終わり・始まり・期間の後・トレイの「研究を終える」）
- [x] 肖像への操作が出力に写らない試験（§4.4・陽性対照つき）
- [x] Windows 実機の手動確認のうち自動でできる範囲（起動・日の割り当て・壁紙の差し替え・異常終了の後の復元・EH3 でない meta）（判断 8）
- [ ] Windows 実機の残り（肖像の成長・終了時の seed・スリープ・再起動・複数モニタ・本人の差し替え・トレイ・招待の図像・画面共有）
- [x] レビュー（判断 7）→ コミット（PR は PR2 の merge の後）

## PR4 — 配布と文書
- [ ] `docs/eh3-distribution-tag.md`・同意文書の記録項目と participant-guide の案
- [ ] functional-design / glossary / architecture / repository-structure / agent-shared の制約 11
- [ ] ADR-035 の見直しの記録・研究者に Accepted を聞く
- [ ] 図像の見本・形の文法の見本を研究者に見せる（F-1・F-3）
- [ ] macOS 実機の引き継ぎ
- [ ] /finish-task（/cross-review 2 巡）
