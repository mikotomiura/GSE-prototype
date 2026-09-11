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
- [x] `code-reviewer` の指摘対応（HIGH 2 / MEDIUM 5 / LOW 5 — **全件対応**）
- [x] `security-checker` の指摘対応（⚠️ CRITICAL / HIGH は **0 件**。MEDIUM 2 件を対応）
- [ ] ⚠️ `/cross-review` — ★ **未実施**（親 PR #182 で 1 度通しており、本 PR は
      その上の追加分。⚠️ **やるなら #182 マージ後にパス限定で回す**）

## ドキュメント
- [x] `requirement.md` / `design.md`
- [ ] ⚠️ **mac 引き継ぎの更新** — ★ 「jq で開く」の前に「画面で見る」を足す
      （⚠️ `dwell_ms` の妥当性と行数 vs 操作回数は**引き続き jq が要る**ので、jq 手順は消さない）

## 完了処理
- [x] git commit（`1cdfed5`）
- [x] PR → https://github.com/mikotomiura/GSE-prototype/pull/184
      （⚠️ **base は `feat/macos-ime-shadow`**。★ #182 の上に積んである）
- [ ] ⚠️★★★ **#184 では CI が 1 本も走らない** —— `ci.yml` の `pull_request` は
      **`branches: [main]`** 限定なので、base が `main` でない PR は発火しない。
      ★ #182 がマージされれば GitHub が #184 を main へ自動 retarget し、そこで CI が走る。
      ⚠️ **それまでは Windows 手元の検証（652 passed 等）が唯一の根拠**である。
