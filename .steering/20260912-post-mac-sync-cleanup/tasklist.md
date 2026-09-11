# タスクリスト: mac 同期後の後片付け

## 0. 準備
- [x] `main` を `origin/main` (`0d4cafb`) へ同期
- [x] 29 件が mac 側変更由来でないことを一次資料で確認
- [x] 作業ブランチ `chore/post-mac-sync-cleanup` を作成

## 1. clippy (低リスク群を先に)
- [ ] B: doc 字下げ 8 件 (`engine.rs` / `logger.rs` / `schema_dto.rs`)
- [ ] D: `is_multiple_of` 3 件 (`features.rs` / `metrics.rs`)
- [ ] G: 範囲パターン 1 件 (`hook_windows.rs`)
- [ ] I/J: `map_or` 3 件 + `collapsible_if` 1 件 (`ime_windows.rs` / `lib.rs`)
- [ ] L/M: `redundant_closure` / `explicit_auto_deref` (`lib.rs`)
- [ ] E: `needless_lifetimes` (`metrics.rs`)
- [ ] H: `Default` impl (`ime_windows.rs`)

## 2. clippy (要確認群)
- [ ] A: `is_ime_active_check` 削除 (`ime_windows.rs`)
- [ ] F: `abs_diff` — ★ 型と呼び出し元を読んでから当てる (`metrics.rs`)
- [ ] K: `too_many_arguments` を `#[allow]` + 理由コメント (`logger.rs`)

## 3. ⚠️★★★ clippy (最高リスク)
- [ ] C: `needless_range_loop` 6 件 (`engine.rs`) — ★ **加算順序を変えない**
- [ ] ★ C の直後に **単独で** ゴールデン 6 fixture を回す

## 4. 検証 (受け入れ条件)
- [ ] `cargo clippy --quiet -- -D warnings` exit 0
- [ ] `cargo test --workspace` 653 passed / 0 failed
- [ ] ゴールデン 6 fixture 全一致
- [ ] `emit_schema` が `schema/current.json` と byte-equal
- [ ] `cargo fmt --check`

## 5. レビュー
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] `/cross-review` (Codex 独立レビュー) — ★ パス限定で回す

## 6. 後片付け
- [ ] マージ済みローカルブランチ 26 本を `git branch -d`
- [ ] `C:\gse-dataset` の未追跡 metrics 13 本を削除
- [ ] `git status --porcelain` が両 repo で空

## 7. 完了処理
- [ ] コミット (`chore(clippy): ...`)
- [ ] `.steering/` 最終化 (`decisions.md` 記入)
