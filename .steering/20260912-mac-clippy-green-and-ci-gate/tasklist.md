# タスクリスト

## 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-mac-clippy-and-ci-gate.md` を読む
- [x] 一次資料 `.steering/20260912-post-mac-sync-cleanup/decisions.md` 判断 8/9/12/13/14 を読む
- [x] 起票 10② の実体 (`20260911-outcome-arbitration-and-o1-preflight/blockers.md`) を読む
- [x] `hook-constraints` Skill 共通-2 (Ordering 規則) を読む
- [x] `main` を fetch して最新 (8d4b8c3) であることを確認
- [x] 作業ブランチ `fix/mac-clippy-green-and-ci-gate` を切る

## 実装
- [x] clippy 実測 (mac: exit=101 / 7 件 — 引き継ぎ §7.3 と一致)
- [x] `lib.rs:3610` unused `was_active` → `#[cfg(target_os="windows")]`
- [x] `lib.rs:854/862` `map_or(false,..)` → `is_some_and`
- [x] `hook_macos.rs:100` doc 段落を分離 (⚠️ help の「字下げ」には従わない)
- [x] `hook_macos.rs:204` 二重キャストの no-op を除去 (⚠️ FFI を一次資料で確認)
- [x] `hook_macos.rs:1062` `% 10 == 0` → `is_multiple_of(10)`
- [x] `ime_macos.rs:77` `map_or(true,..)` → `is_none_or`
- [x] **コミット 1** `fix(clippy)` 5e29fec
- [x] 起票 10②: `ime_macos.rs:79` / `ime_windows.rs:289` の `IME_OPEN.store` を Release
- [x] **コミット 2** `fix(ime)` 5aa05e4 (⚠️ lint と分ける)
- [x] `ci.yml` の check job に clippy step + `components: clippy` を追加
- [x] **コミット 3** `ci(check)` df471ca

## テスト
- [x] `cargo clippy --quiet --all-targets -- -D warnings` **exit 0**
- [x] CI と同一スコープ (`--features package --target aarch64-apple-darwin`) でも **exit 0**
- [x] `cargo fmt --check` clean
- [x] `cargo test --workspace` **659 passed / 0 failed** (★ ベースラインから減っていない)
- [x] ゴールデン 6 fixture / **226 snapshot byte-equal** (⚠️ `HMM_VERSION` bump なし)
- [x] `emit_schema` が `schema/current.json` と byte-equal
- [x] `actionlint` の指摘件数が変更前後で同じ (3 件・すべて pre-existing)

## レビュー
- [x] `code-reviewer` / `security-checker` を並列起動
- [x] HIGH 指摘への対応 (★ steering をコミット) ＋ MEDIUM 2 件 (load 側 Acquire / ci.yml 注記の訂正)
- [ ] `/cross-review` (Codex 独立レビュー)

## ドキュメント
- [x] `requirement.md` / `design.md` / `decisions.md`
- [x] 起票 10② を閉じたことを `blockers.md` 側にも残す (⚠️ `IME_ACTIVE` は新起票として残)
- [ ] `_handoff/` の当該メモを「完了」へ更新

## 完了処理
- [ ] PR 作成 → **CI の両 OS レグが緑であることを確認** (★ R-1 の受け入れ条件)
- [ ] R-4 (CI の `USERPROFILE` / `HOME`) の観察結果を研究者へ報告
