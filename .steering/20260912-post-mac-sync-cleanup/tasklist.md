# タスクリスト: mac 同期後の後片付け

## 0. 準備
- [x] `main` を `origin/main` (`0d4cafb`) へ同期
- [x] 29 件が mac 側変更由来でないことを一次資料で確認
- [x] 作業ブランチ `chore/post-mac-sync-cleanup` を作成

## 1. clippy (低リスク群を先に)  ★ 実測は 29 → 33 件 (lib を緑にすると bin が見えた)
- [x] B: doc 字下げ 8 件 (`engine.rs` / `logger.rs` / `schema_dto.rs`)
- [x] D: `is_multiple_of` 3 件 (`features.rs` / `metrics.rs`)
- [x] G: 範囲パターン 1 件 (`hook_windows.rs`)
- [x] I/J: `map_or` 3 件 + `collapsible_if` 1 件 (`ime_windows.rs` / `lib.rs`)
- [x] L/M: `redundant_closure` / `explicit_auto_deref` (`lib.rs`)
- [x] E: `needless_lifetimes` (`metrics.rs`)
- [x] H: `Default` impl (`ime_windows.rs`)

## 2. clippy (要確認群)
- [x] A: `is_ime_active_check` 削除 (`ime_windows.rs`)
- [x] F: `abs_diff` — ★ 型と呼び出し元を読んでから当てる (`metrics.rs`)
- [x] K: `too_many_arguments` を `#[allow]` + 理由コメント (`logger.rs`)

## 3. ⚠️★★★ clippy (最高リスク)
- [x] C: `needless_range_loop` 6 件 (`engine.rs`) — ★ **加算順序を変えない**
- [x] ★ C の直後に **単独で** ゴールデン 6 fixture を回す

## 4. 検証 (受け入れ条件)
- [x] `cargo clippy --quiet -- -D warnings` exit 0
- [x] `cargo test --workspace` 653 passed / 0 failed
- [x] ゴールデン 6 fixture 全一致
- [x] `emit_schema` が `schema/current.json` と byte-equal
- [x] `cargo fmt --check`

## 5. レビュー
- [x] `code-reviewer` + `security-checker` を**並列**起動
- [x] `/cross-review` (Codex 独立レビュー) — ★ パス限定で回す

## 6. 後片付け
- [x] マージ済みローカルブランチ 26 本を `git branch -d`
- [x] `C:\gse-dataset` の未追跡 metrics 13 本を削除
- [x] `git status --porcelain` が両 repo で空

## 7. 完了処理
- [x] コミット (`chore(clippy): ...`)
- [x] `.steering/` 最終化 (`decisions.md` 記入)
