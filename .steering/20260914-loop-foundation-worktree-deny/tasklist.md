# タスクリスト

## 準備
- [x] `docs/loop-engineering.md` / `loop-config.README.md` / 引き継ぎ §8b §8c を読む
- [x] ベースライン実測（`cargo test --workspace` exit 0 / 670 passed / 0 failed）
- [x] `.claude/settings.json` と `.gitignore:46` を実測
- [x] `loop-spawn.sh` / `loop-run.sh` を読み、注入点と stdout 契約を特定

## 実装
- [x] `scripts/loop-worktree-deny.sh` を書く（注入 / `--verify` / `--print`）
- [x] `scripts/loop-spawn.sh` に配線（worktree 作成直後・失敗で die・出力は stderr）
- [x] `.github/workflows/ci.yml` にテストステップを追加

## テスト
- [x] `scripts/loop-worktree-deny-test.sh` を書く（3 状態 ＋ 冪等 ＋ 陰性対照 ＋ 契約突合 ＋ 配線）
- [x] テストが緑（★ 21/21・`bash scripts/loop-worktree-deny-test.sh` exit 0）
- [x] `bash scripts/check-shell-portability.sh` が緑
- [x] `bash scripts/check-tests-are-wired.sh` が緑
- [x] ベースライン（`cargo test --workspace`）— ★ Rust は 1 行も触っていない。実測 exit 0 / 670 passed / 0 failed

## レビュー
- [x] code-reviewer + security-checker を並列起動（★ 両方 HIGH 2 件で一致）
- [x] `/cross-review` 1 巡目（Codex・HIGH 1 / MEDIUM 2 / LOW 1 / テスト不足 1）
- [x] HIGH 指摘への対応（★ verify の fail-open ／ 毎 attempt の保証 ／ 黙って自己修復しない）
- [x] MEDIUM / LOW も全件対応（★ backlog に punt しない）

## ⚠️ 副産物として見つかった実バグ（★ 2 件・どちらも「モード C を 1 度も回していない」ことの帰結）
- [x] `loop-run.sh:415` `${#DONE_IDS[@]:-0}` が **bad substitution**（★ 復元ログが黙って消えていた）
- [x] ⚠️★★★ **モード C が 1 issue 目で必ず死ぬ** —— `loop-run.sh` が `_loop-events.jsonl` を
      **作ってから** `loop-spawn.sh` を呼ぶため、spawn の dirty-tree 判定に自分で作ったファイルが当たる
      （★ stub 実行で再現 → `.gitignore` に Loop の実行時生成物 3 件を追加して解消）

## ドキュメント
- [x] `loop-config.README.md` に「注入は自動である」旨を追記（★ 契約の所在を 1 か所に）
- [x] `docs/loop-engineering.md` の C の危険と既定に 1 行

## 完了処理
- [ ] design.md の最終化
- [ ] decisions.md（判断が出たら）
- [ ] git commit
