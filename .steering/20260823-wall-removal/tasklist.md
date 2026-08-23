# タスクリスト — Wall (Lv2 介入) の全削除

> 2026-08-23 / ★ 研究者判断「wall_server も含めて全削除」＋「Monk Mode も (b) で削除」

## ✅ 完了

### Rust
- [x] `intervention.rs` — `InterventionAction::Wall` / 閾値 6 種 / `wall_accum_ms` / daily cap / cooldown / `force_wall_decision` / `apply_wall_suppressions`
- [x] `intervention_eval.rs` — ACT を `{nudge}` に。★ **HIR 指標自体は残した**
- [x] `logger.rs` — `wall_accum_ms` / Wall 応答 reason (`early_unlock` / `completed` / `idle_timeout`)
- [x] `schema_dto.rs` — Wall action / `wall_accum_ms` / Wall 応答 / `monk_mode`
- [x] `lib.rs` — module / `force_wall` コマンド / `FORCE_WALL` / `WallServerState` / shutdown 経路
- [x] **`wall_server.rs` を削除**（`git rm`）
- [x] `Cargo.toml` — `tiny_http` / `qrcode` を除去
- [x] **Monk Mode 全削除**（`InterventionInput` / `session_meta` / IPC 引数）

### Frontend
- [x] `Overlay.tsx` — Wall JSX / QR / 打鍵警告 / スマホ接続バッジ / wall server ライフサイクル / 全画面ブロック分岐
      （★ `applyFullscreenBlock` は **box 化失敗時の縮退路として残した**）
- [x] `App.tsx` — `isWallActive` / エッジ検出 / `sensor-accelerometer` 購読 / Monk Mode 購読
- [x] `Dashboard.tsx` — Monk Mode トグル / Wall 強制発動ボタン（★ クラス名を `debug-force-button` へ改名）
- [x] `App.css` — `.monk-mode-*` / `.wall-*` / `.qr-*` / `.phone-connected-badge`

### 文書
- [x] **ADR-015 を新設**（★ PM-D11 を覆すこと・凍結文書は書き換えないことを明記）
- [x] `intervention-design` / `physical-anchor` Skill — **冒頭に無効化バナー ＋ frontmatter の description を改訂**
      （★ description は起動条件そのものなので直さないと誤起動する。`.claude` / `.agents` の両コピー）
- [x] `docs/repository-structure.md` / `docs/agent-shared.md` / `CLAUDE.md` / `docs/adr/README.md`

## ⚠️ 検証（すべて緑）

- [x] `cargo test --workspace` → **461 passed / 0 failed**（★ 465 − 削除した Wall テスト 4 本）
- [x] `npx tsc --noEmit` → **エラーなし**
- [x] `npm run build` → **成功**（39 modules）
- [x] ゴールデン replay → **15 snapshots 一致**
- [x] `emit_schema` → **gse-dataset parity in sync**
- [x] `cargo fmt --check` → OK ／ clippy → ★ 新規警告なし（既存の `is_ime_active_check` のみ）
- [x] Tauri `capabilities/` に Wall 残存なし

## ⚠️★★★ 途中で 1 度やり直した

⚠️ `App.tsx` で **`// 4. Sensor Integration` 〜 `// 4c.` を範囲削除しようとして、間にあった
G1 機能（モード取得 / 参加者 ID 復元 / 自動提出状態 / 送信中の時計）まで消した。**
★ **`tsc` の `TS6133`（`setG1Mode` / `setNowMs` が未使用）で気づき、`git checkout` して丁寧にやり直した。**
→ ★ **教訓: コメント見出しを目印にした範囲削除は、間に別機能が挟まっていると巻き込む。**

## ⚠️ 残（★ 別タスク）

- [ ] ⚠️★★★ **Physical Anchor の運搬路（境界クラス）の再設計** — ADR-015 D4
- [ ] **運用文書の Wall 記述** — `verification-runbook.md` / `pilot-runbook.md` / `wbs-verification-halfyear.md` / `functional-design.md` / `architecture.md` / `development-guidelines.md` / `glossary.md`
- [ ] ⚠️ **`elapsed_ms`（`intervention_response`）** — 書く経路が無くなった。復活しないなら落とす候補
- [ ] ⚠️ **凍結中の G1 事前登録との表記ずれ**（起動モード表の「介入（Nudge / Wall）」）— ★ **書き換えず記録のみ**
- [ ] **gse-dataset の schema コミット**（★ ファイルは同期済み）
