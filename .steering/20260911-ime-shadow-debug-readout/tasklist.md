# タスクリスト

## 準備
- [x] ⚠️ **既存の診断パネルが `debugView` で囲まれているか実測**（★ 囲まれて**いなかった** → 設計変更）
- [x] `typescript-standards` / `data-privacy` Skill を参照
- [x] 既存の `debug_force_probe` / `force_nudge` / `ensure_debug_enabled` の作法を確認
- [x] `get_session_file` が既にパスを返していることを確認（★ 再利用した）

## 実装
- [x] `input/hook.rs` — `IME_SHADOW_EMITTED` / `IME_SHADOW_ABANDONED`
- [x] `lib.rs` — `tally_ime_shadow()` を `emit_ime_shadow` の 2 経路に配線
- [x] `lib.rs` — `ImeShadowDebugDto` / `get_ime_shadow_debug`（⚠️ `ensure_debug_enabled()?`）
- [x] `lib.rs` — `invoke_handler` へ登録
- [x] `Dashboard.tsx` — 型 / state / **`debugView` で囲んだ**ブロック
- [x] `App.css` — `.debug-ime-shadow*`

## テスト
- [x] `tally_counts_confirmed_and_abandoned`
- [x] `abandoned_never_exceeds_emitted`
- [x] `the_debug_command_is_gated_on_the_backend`
- [x] ⚠️★★★ `the_participant_visible_diagnostics_do_not_carry_the_tally`
- [x] `the_readout_block_is_gated_on_the_frontend`（⚠️ 初版が doc コメントに当たって赤 → 修正）
- [x] `cargo test --workspace` — **651 passed / 0 failed**（親 646 → +5）
- [x] ゴールデン `gse-replay --snapshot` — 15 一致
- [x] ⚠️ `emit_schema` parity — **差分なし**（★ NDJSON の行を 1 行も増やしていない証拠）
- [x] `cargo fmt --check` / `cargo clippy` — **29 件で不変**
- [x] `npx tsc --noEmit` / `npm run build`
- [ ] ⚠️ **macOS 実機での動作確認** → ★ mac 引き継ぎで AC 6 と同時に行う

## レビュー
- [ ] `code-reviewer` の指摘対応
- [ ] `security-checker` の指摘対応
- [ ] `/cross-review`

## ドキュメント
- [x] `requirement.md` / `design.md`
- [ ] ⚠️ **mac 引き継ぎの更新** — ★ 「jq で開く」の前に「画面で見る」を足す
      （⚠️ `dwell_ms` の妥当性と行数 vs 操作回数は**引き続き jq が要る**ので、jq 手順は消さない）

## 完了処理
- [x] git commit（`1cdfed5`）
- [ ] PR（⚠️ **#182 の上に積んである**ので、base を何にするか要判断）
