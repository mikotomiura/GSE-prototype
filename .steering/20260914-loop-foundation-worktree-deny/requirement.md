# Loop 基盤整備 — worktree への `permissions.deny` 注入（2z）

## 背景

`docs/loop-engineering.md` は無人モード C を「本命の自動化」と位置づけ、
`.steering/_template/loop-config.README.md` は逐語で
「`.claude/settings.json` の `permissions.deny` を**必ず併用する**（`deny` は allow と
frontmatter の**両方に優先**）」と書き、7 件のリストを示している。

⚠️ しかし 2026-09-13 の前提監査（実測）で次が判明した:

| # | 実測 |
|---|---|
| 1 | `.claude/settings.json` の `permissions.deny` は **`chmod -R` / `sudo` の 2 件だけ**（本セッションで再確認） |
| 2 | 残り 5 件（`git push` / `gh pr merge` / `git reset --hard` / `git rebase` / `rm -rf`）は `deny` ではなく **`ask`** または未記載 |
| 3 | ⚠️★★★ **deny を worktree へ入れる仕組みが無い**（`loop-spawn.sh` / `loop-run.sh` を grep して `settings` は 0 件 — 本セッションで再確認） |

★ さらに本セッションで確認した固有の事実:
`.claude/settings.json` には `"allow": ["Bash(git *)", "Bash(gh *)"]` があり、
5 件は `deny` ではなく **`ask`**（＝ **人が承認することを前提にした設定**）に置かれている。
⚠️ 無人モード C には承認する人が居ないので、★ **`ask` に頼る設計そのものが前提を満たさない**。
（⚠️ `-p` 実行時に `ask` が実際にどう解決されるかは**本セッションでは実測していない** —— 
★ だからこそ「`deny` を必ず併用する」という README の逐語規約に従う。）

⚠️ かつ無人実行は過去 2 回、**コード 0 行のまま終了**している（約 $11 を消費。原因は
`allowed_tools` を `null` にしたこと）。★ 基盤の安全装置が整う前に Loop を回さない。

## ゴール

★ **worktree が作られた時点で、その worktree の Claude セッションに必須 7 件の `deny` が効いている**
状態を機械的に保証し、**保証できなければ worktree を使わせない**（fail-closed）。

## スコープ

### 含むもの
- `<worktree>/.claude/settings.local.json` へ必須 deny 7 件を注入する新スクリプト
- `scripts/loop-spawn.sh` から worktree 作成直後に呼ぶ配線（モード A / C の両方が通る）
- 3 状態（不在 / 正常 / 壊れている）＋ 冪等性 ＋ 陰性対照を持つテスト
- テストの CI 配線（`check-tests-are-wired.sh` の要求）
- 契約の二重定義検出（スクリプトの 7 件 ⇄ `loop-config.README.md` の 7 件）

### 含まないもの
- ⚠️ **main checkout の `.claude/settings.json` の変更**（★ 対話セッションの `git push` を塞ぐ）
- ⚠️ `allowed_tools` の変更（★ テンプレートの既定リストは修正済み。`null` に戻さない）
- `_loop-config.json` の作成（★ 着手順 2。タスク 2 の分解セッション以降）
- `acceptance.sh` の作成（★ 着手順 3）
- 実際の Loop 実行（★ 着手順 4-5）

## 受け入れ条件

- [ ] AC1: worktree に `.claude/settings.local.json` が無いとき、必須 7 件を持つ有効な JSON が新規作成される
- [ ] AC2: 既存の `settings.local.json` があるとき、**他のキーを消さず** `deny` 配列へマージされ、重複が出ない
- [ ] AC3: 既存ファイルが**壊れた JSON** のとき、**上書きせず非 0 で停止**する（fail-closed）
- [ ] AC4: 注入後に必須 7 件が揃っていることを**検査する段**があり、揃っていなければ非 0 で停止する
- [ ] AC5: 検査の陰性対照が通る（1 件抜いたら検査が赤になる ＝ 空振りしていない）
- [ ] AC6: `scripts/loop-spawn.sh` が worktree 作成直後にこれを実行し、失敗したら worktree を使わせない
- [ ] AC7: ⚠️ `loop-spawn.sh --no-exec` の**stdout 最終行が worktree 絶対パス**である契約を壊さない（`loop-run.sh:275` が `tail -1` で読む）
- [ ] AC8: テストが CI から走る（`bash scripts/check-tests-are-wired.sh` が緑）
- [ ] AC9: `bash scripts/check-shell-portability.sh` が緑
- [ ] AC10: ベースライン（`cargo test --workspace` exit 0 / 670 passed）を壊さない

## 関連ドキュメント

- `docs/loop-engineering.md`（Loop Engineering の単一 SSOT）
- `.steering/_template/loop-config.README.md`（★ 必須 deny 7 件の逐語リスト ＝ 契約元）
- `.steering/_handoff/next-session-mhd-feature-redesign-ssot.md` §8c（★ 材料の確定版）
- `.steering/_handoff/next-session-loop-foundation-and-task2-slicing.md` §2

## 運用メモ
- /reimagine 適用: No
- 理由: ★ 設計は §8c で確定済み（「再導出しないこと」）。置き場・内容・理由がすべて
  一次資料で閉じており、複数案を比較する余地が無い。
