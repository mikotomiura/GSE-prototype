# 設計 — `loop-spawn.sh --cleanup` の是正

## 実装アプローチ

★ `--cleanup` 分岐を **「集める → 撤去する → 確かめる → 数えて報告する」** の 4 段に組み替える。
⚠️ 既存の `abort_worktree`（★ 変更前の `loop-spawn.sh:126-149`）が**既に持っている作法**
（逐語「⚠️ 撤去できたかを**確かめてから**「撤去しました」と書く」）を `--cleanup` 側にも適用する。

### 0. ⚠️★★★ 前提: **main checkout を解決してから始める**（★ レビュー後に追加）

★ `git rev-parse --show-toplevel` は **linked worktree の中では worktree 自身**を返す。
⚠️ 2026-09-21 に実測（code-reviewer HIGH → メインが独立再現）:
worktree の中から `--cleanup` を叩くと `repo_name` が `<repo>-<id>-<short>` に化け、
★ **(1) path 系統の一致 (2) main checkout ガード (3) 残存 dir の網 が同時に無効化**され、
`cleanup 完了` / exit 0 という**起票 18 と同じ嘘**に戻っていた。
→ ★ `git worktree list --porcelain` の**先頭 ＝ main worktree** から `repo_root` を取る。

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

### 1b. ⚠️ id の検証（★ レビュー後に追加・security-checker MEDIUM）

★ `git branch --list` の引数は **fnmatch パターン**なので、`--cleanup '*'` は `loop/*` に化け、
⚠️ **merge 済みの `loop/*` ブランチが全部 `-d` の対象**になる。
★ 一方 worktree 側は literal 比較なので 1 件も当たらず、**両系統の広さが非対称**になる。
→ ★ `[A-Za-z0-9._-]` のみ・`-` 始まり禁止で弾く。⚠️ 併せて `..` / `/`（`../wt/` の外）と
`\`（`awk -v` がエスケープ列として解釈しシェル側とずれる）も閉じる。

### 2. 撤去の事後確認（起票 18 の直し方 2）

- worktree: `git worktree remove` → `--force` の順で試し、**その後 `git worktree list` を引き直して
  当該パスが消えたことを確認**する。⚠️ `remove` の exit code を信じない。
  ⚠️ **登録を読めなかったときは「撤去できた」と書かない**（fail-closed・★ レビュー後に追加）。
- ⚠️★★★ **未コミット変更がある worktree は撤去しない**（★ レビュー後に追加・security-checker MEDIUM）——
  ★ branch 側で `-D` を避けたのと同じ理屈。⚠️ 逸脱 worktree は**作業が載っている可能性が最も高い**。
- branch: `git branch -d` → **`git show-ref --verify refs/heads/<b>` で消えたことを確認**する。
  ⚠️ `-D` は使わない（★ 未 merge の作業を黙って捨てない。`abort_worktree` の先例と同じ判断）。
- ★ 1 つでも残っていたら `⚠️ cleanup 未完了` と書き、**exit 1**。

### 3. 未登録の残存ディレクトリ

★ `../wt/<repo_name>-<id>` / `../wt/<repo_name>-<id>-*` が**ディレクトリとして残っているのに
worktree 登録に無い**形（spawn 側の残存 dir 検査（★ 変更前の :92）が die する状態）を検出して警告する。
⚠️ **自動削除はしない**（★ `rm -rf` は破壊的で、中身が何か分からない）。★ ただし再実行を殺すので
**exit 1 の対象には含める**（＝「完了」とは書かない）。

### 4. 数えて報告する

```text
loop-spawn: cleanup 完了 issue <id> (worktree 1 件 / branch 1 件 を撤去)
loop-spawn: cleanup 対象なし issue <id> (★ 既に撤去済み)          # exit 0（冪等・AC4）
loop-spawn: ⚠️ cleanup 未完了 issue <id> — 撤去できなかったものが N 件あります  # exit 1
```

## 変更対象

### 修正するファイル
- `scripts/loop-spawn.sh` — `--cleanup` 分岐（★ **変更前の 54-71 行**）を上記 4 段に差し替え
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

★ **7 群 25 件**（★ レビュー後に 9 件追加）:

| 群 | ケース | 期待 |
|---|---|---|
| 1 | 正常系（`loop/<id>-<short>` のまま） | 撤去・exit 0（AC3） |
| 1 | ⚠️ **逸脱**（worktree が別ブランチを指す） | 撤去・exit 0（AC1・★ 本丸） |
| 1 | 対象 0 件 / 2 回目の実行 | exit 0・「対象なし」（AC4） |
| 1 | ★ **完全一致**（`--cleanup <id>-<short>`） | 撤去・exit 0（AC9） |
| 1 | ⚠️★★★ **linked worktree の中から叩く** | 撤去・main 無傷・報告が事実と一致（AC10） |
| 2 | ⚠️ 撤去不能（worktree を lock する） | **exit 1**・「完了」と書かない（AC2） |
| 2 | ⚠️★★★ **未コミット変更がある worktree** | 捨てない・**exit 1**（AC11） |
| 2c | ⚠️★★★ id に `*` / `../../x` | 拒否・**無関係な `loop/*` を消さない**（AC12） |
| 3 | ⚠️ 別 id（`005` と `0055`）| `005` の cleanup が `0055` を消さない（AC6） |
| 4 | ⚠️ **陰性対照** — main checkout | どの経路でも残る（AC5） |
| 5 | ⚠️ **陰性対照** — 残存ディレクトリ | exit 1・警告（★ 消さない） |
| 6 | ⚠️★★★ **変異テスト**（path 系統を潰す） | 逸脱 worktree が残り「完了」と書かない |

★ 併せて回すもの: `check-shell-portability.sh` / `check-tests-are-wired.sh` /
`loop-worktree-deny-test.sh` / `loop-run-guard-test.sh` / `check_workflow_invariants.py`。
★ **旧実装に当てると 17 件 NG / exit 1**（2026-09-21 実測 ＝ 検査は空振りしていない）。

## ロールバック計画

★ `scripts/loop-spawn.sh` の該当ブロックを差し戻すだけで足りる（1 ファイル・1 分岐）。
⚠️ 新テストと CI 配線は同一コミットに入れるので、**まとめて revert** する。
