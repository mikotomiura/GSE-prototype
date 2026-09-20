# タスクリスト

## 準備
- [x] 一次資料を読む（起票 18 / `scripts/loop-spawn.sh` / `loop-run.sh:204`）
- [x] `--cleanup` の呼び出し元を grep（★ **人間のみ**。`loop-run.sh` は文言で案内するだけ）
- [x] ⚠️ **直す前に再現させる**（★ 逸脱 worktree → `cleanup 完了` / exit 0 を実測）

## 実装
- [x] 一致規則を branch ∪ path の 2 系統にする（⚠️ 前方一致に区切り `-` を要求）
- [x] 撤去の事後確認（worktree = 登録 ＋ ディレクトリ / branch = `show-ref`）
- [x] 1 つでも残れば **非 0** で終了・「完了」と書かない
- [x] main checkout の明示ガード
- [x] 残存ディレクトリの報告（⚠️ 自動削除しない）＋ **最後の網**（処理したものだけ除外）
- [x] 対象 0 件は exit 0（冪等）

## テスト
- [x] `scripts/loop-spawn-cleanup-test.sh` 新規（**8 群 28 件**・⚠️ 変異テスト付き）
- [x] 新テストが緑（**28 / 28**）
- [x] ⚠️★★★ **旧実装に当てて赤になることを実測**（**18 件 NG / exit 1**）＝ 空振りでない
- [x] `check-shell-portability.sh` 緑（12 / 0）
- [x] `check-tests-are-wired.sh` 緑（**17 本**すべて配線・self-test も緑）
- [x] `loop-worktree-deny-test.sh` 緑（34 / 0）
- [x] `loop-run-guard-test.sh` 緑（35 / 0）
- [x] `check_workflow_invariants.py` 緑（2 workflow / 7 job）＋ unittest 34 件 OK

## レビュー
- [x] `code-reviewer` ＋ `security-checker`（並列・opus）
- [x] ⚠️★★★ **HIGH 対応**: linked worktree の中から叩くと嘘が戻る形
      （★ メインが独立に再現 → `repo_root` を main worktree から解決・判断 7）
- [x] MEDIUM 対応: id の検証（判断 8）/ 未コミット変更を捨てない（判断 9）/
      `registered_bn` の fail-closed / 除外をパス同定へ / `prune` の裸実行 / 復旧案内に `unlock`
- [x] LOW 対応: テストの `grep -q` / 完全一致経路の追加 / CI の macOS 除外理由 / design の行番号・書式
- [x] ⚠️ 範囲外と判断したもの: `check` job の `permissions:`（★ 既存条件 → **起票 24**・判断 10）
- [x] `/cross-review` **1 巡目**（★ 指摘 5 件 → 判断 11 / 12。⚠️ 足したテストが**実害を 1 件検出**）
- [ ] `/cross-review` **2 巡目**（★ 自分が足した規則の境界条件）

## ドキュメント
- [x] 起票 18 に **✅ 是正済み** を追記（★ 本文は書き換えず追記）
- [x] `loop-run.sh:204` の `detail`（★ 是正で**嘘になる**案内文）を更新
- [x] CI 配線（ubuntu ＋ Windows の 2 か所）
- [x] ⚠️ 派生発見を **起票 23**（`resolve_base` が config を `tail -1` で選ぶ）と
      **起票 24**（`check` job の `permissions:`）として登録
- [ ] glossary への用語追加（★ 新語なし → 不要）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [ ] git commit（⚠️ `git add -A` 禁止・明示パスのみ）
