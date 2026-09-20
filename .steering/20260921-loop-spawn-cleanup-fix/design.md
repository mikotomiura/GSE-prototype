# 設計 — `loop-spawn.sh --cleanup` の是正

## 実装アプローチ

★ `--cleanup` 分岐を **「集める → 撤去する → 確かめる → 数えて報告する」** の 4 段に組み替える。
⚠️ 既存の `abort_worktree`（`loop-spawn.sh:126-149`）が**既に持っている作法**
（逐語「⚠️ 撤去できたかを**確かめてから**「撤去しました」と書く」）を `--cleanup` 側にも適用する。

### 1. 引き方: ブランチ名 **OR** パス の 2 系統（起票 18 の直し方 1）

| 系統 | 一致条件 |
|---|---|
| branch | `loop/<id>` 完全一致 **または** `loop/<id>-` 前方一致 |
| path   | basename が `<repo_name>-<id>` 完全一致 **または** `<repo_name>-<id>-` 前方一致 |

- ⚠️ **現行の `$0 ~ ("loop/" id)` は正規表現の部分一致**なので、`--cleanup zzz` が
  `loop/zzz2-issue` にも当たる。★ 前方一致＋区切り `-` を要求して塞ぐ（AC6）。
- ★ id に `001-issue` のような `<id>-<short>` 込みの値を渡す運用が実在する
  （`.steering/_handoff/next-session-issue001-pause-const-arbitration.md:123` 逐語
   `--cleanup 001-issue`）。→ ★ **完全一致も許す**ことで両方の渡し方を拾う。
- ⚠️★★★ **main checkout は絶対に撤去しない**。★ パス一致が `$repo_root` に当たる経路は
  理論上無いが（basename が `<repo_name>-…` を要求するため）、**明示ガードを置く**（AC5）。

### 2. 撤去の事後確認（起票 18 の直し方 2）

- worktree: `git worktree remove` → `--force` の順で試し、**その後 `git worktree list` を引き直して
  当該パスが消えたことを確認**する。⚠️ `remove` の exit code を信じない。
- branch: `git branch -d` → **`git show-ref --verify refs/heads/<b>` で消えたことを確認**する。
  ⚠️ `-D` は使わない（★ 未 merge の作業を黙って捨てない。`abort_worktree` の先例と同じ判断）。
- ★ 1 つでも残っていたら `⚠️ cleanup 未完了` と書き、**exit 1**。

### 3. 未登録の残存ディレクトリ

★ `../wt/<repo_name>-<id>` / `../wt/<repo_name>-<id>-*` が**ディレクトリとして残っているのに
worktree 登録に無い**形（`loop-spawn.sh:92` が die する状態）を検出して警告する。
⚠️ **自動削除はしない**（★ `rm -rf` は破壊的で、中身が何か分からない）。★ ただし再実行を殺すので
**exit 1 の対象には含める**（＝「完了」とは書かない）。

### 4. 数えて報告する

```text
loop-spawn: cleanup 完了 issue <id> (worktree 1 件 / branch 1 件 を撤去)
loop-spawn: cleanup 対象なし issue <id> (★ 既に撤去済み)          # exit 0（冪等・AC4）
loop-spawn: ⚠️ cleanup 未完了 issue <id> — 残: worktree 1 件 …    # exit 1
```

## 変更対象

### 修正するファイル
- `scripts/loop-spawn.sh` — `--cleanup` 分岐（54-71 行）を上記 4 段に差し替え
- `scripts/loop-run.sh` — `:204` の `detail` 文言（★ 「`--cleanup` はブランチ名で引くので
  逸脱した worktree を撤去できない」が**修正後は嘘になる**）
- `.github/workflows/ci.yml` — 新テストを ubuntu 側 `docs-check` 系 job と Windows 側へ配線
- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` — 起票 18 に**是正済み**を追記

### 新規作成するファイル
- `scripts/loop-spawn-cleanup-test.sh` — ⚠️ `loop-worktree-deny-test.sh` の
  `setup_fake_repo` パターンを踏襲（★ 一時 git repo・`GIT_CONFIG_GLOBAL=/dev/null` で
  実行者の global 設定を継承しない）。**実 repo には 1 バイトも触れない。**

## 影響範囲

- ★ `--cleanup` の**呼び出し元は人間のみ**（2026-09-21 に repo 全体を grep して確認:
  `loop-run.sh:204` は文言で案内しているだけで**実行していない**）。
  → ⚠️ exit code を非 0 にしても**自動経路は壊れない**。
- ★ `git-workflow` SKILL.md:193 の記述（「merge 後は `--cleanup` で remove + branch -d + prune」）は
  **修正後も真**なので変更しない。

## 既存パターンとの整合性

- ★ 撤去の事後確認 → `loop-spawn.sh` の `abort_worktree`
- ★ テストの作法（3 状態 ＋ **陰性対照**）→ `loop-worktree-deny-test.sh` 冒頭の規約
- ★ exit code の契約（0=緑 / 1=違反 / 2=判定不能）→ `check-shell-portability.sh`
- ★ `${name}` で括る → `check-shell-portability.sh` の規約（macOS bash 3.2）

## テスト戦略

`scripts/loop-spawn-cleanup-test.sh`（一時 git repo 内・実 worktree）:

| # | ケース | 期待 |
|---|---|---|
| 1 | 正常系（`loop/<id>-<short>` のまま） | 撤去・exit 0（AC3） |
| 2 | ⚠️ **逸脱**（worktree が別ブランチを指す） | 撤去・exit 0（AC1・★ 本丸） |
| 3 | 対象 0 件 / 2 回目の実行 | exit 0・「対象なし」（AC4） |
| 4 | ⚠️ 撤去不能（worktree を lock する） | **exit 1**・「完了」と書かない（AC2） |
| 5 | ⚠️ 別 id（`zzz` と `zzz2`）| `zzz` の cleanup が `zzz2` を消さない（AC6） |
| 6 | ⚠️ **陰性対照** — main checkout | どの経路でも残る（AC5） |
| 7 | ⚠️ **陰性対照** — 未登録の残存ディレクトリ | exit 1・警告（★ 消さない） |

★ 併せて回すもの: `bash scripts/check-shell-portability.sh` / `bash scripts/check-tests-are-wired.sh`。

## ロールバック計画

★ `scripts/loop-spawn.sh` の該当ブロックを差し戻すだけで足りる（1 ファイル・1 分岐）。
⚠️ 新テストと CI 配線は同一コミットに入れるので、**まとめて revert** する。
