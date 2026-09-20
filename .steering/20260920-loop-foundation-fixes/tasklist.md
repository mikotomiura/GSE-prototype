# タスクリスト

## 準備
- [x] 一次資料を読む（`loop-run.sh` / `loop-worktree-deny.sh` / `.claude/settings.json` / `_loop-config.json` / `docs/loop-engineering.md` / 起票 3・10 / 判断 25・26）
- [x] grill で判断分岐を閉じる（判断 1〜6）
- [x] `.steering/20260920-loop-foundation-fixes/` を作成

## 実測（★ 先にやる —— スキーマが分かってから実装する）
- [ ] **M1 対照**: deny 7 件のまま worktree 内で `git checkout main` を依頼 → ★ 通ることを撮る
- [ ] **M1b**: `permission_denials` 配列の**実際のスキーマ**を採取する（⚠️ `.tool_name` を推測しない）
- [ ] **M2**: deny 9 件で同じ依頼 → ★ 拒否されることを撮る
- [ ] `measurements.md` に生ログを残す
- [ ] `bash scripts/loop-spawn.sh --cleanup zzz` で撤去

## 実装
- [ ] `scripts/loop-worktree-deny.sh` — `DENY_REQUIRED` 7 → 9 件 ＋ 文言
- [ ] `.steering/_template/loop-config.README.md` — 逐語リスト 9 件 ＋ 「境界はブランチ検査」
- [ ] `scripts/loop-run.sh` — `ensure_branch` を追加し 2 か所で呼ぶ
- [ ] `scripts/loop-run.sh` — `permission_denials` の内訳保存 ＋ detail の集計
- [ ] `scripts/loop-run.sh` — `issue_status` / Status フィルタ / `--issues` 時の警告
- [ ] `scripts/loop-run.sh` — ⚠️ `preflight_dag` の存在確認を `ALL_FILES` に対して行う（回帰の予防）
- [ ] `scripts/loop-run.sh` — レポートに除外した id を出す
- [ ] `.gitignore` — `.steering/**/_loop-artifacts/`
- [ ] `.claude/commands/loop-issue.md` — 「worker は commit してから終わる」（判断 5）

## テスト
- [ ] `scripts/loop-worktree-deny-test.sh` の期待件数 7 → 9
- [ ] `scripts/loop-run-guard-test.sh` を新規作成（B1〜B3 / S1〜S4 / D1）
- [ ] ⚠️ **陰性対照**を入れる（B2 = 検査が空振りでないこと）
- [ ] ⚠️ **検査が見ていないもの**を検査自身のコメントに書く
- [ ] `bash scripts/loop-worktree-deny-test.sh` が exit 0
- [ ] `bash scripts/loop-run-guard-test.sh` が exit 0
- [ ] `bash scripts/check-tests-are-wired.sh` が exit 0
- [ ] ⚠️ `tr -cd '\r' | wc -c` が 0（CRLF 混入なし）

## ドキュメント
- [ ] `docs/loop-engineering.md` — 「多層防御であって境界ではない」節を実測結果で更新
- [ ] `docs/loop-engineering.md` — 新語（ブランチ検査 / worktree 逸脱）を「基本単位」に足す（判断 6）
- [ ] `.steering/20260914-mhd-feature-offline-tiers/blockers.md` — 起票 3 / 10 を**閉じる**（⚠️ 消さない）

## レビュー
- [ ] `code-reviewer`（opus）＋ `security-checker`（opus）を**並列**起動
- [ ] `/cross-review` **2 巡**（パス限定・コミット後）
- [ ] HIGH / MEDIUM 指摘への対応

## 完了処理
- [ ] `design.md` の最終化
- [ ] `decisions.md` にレビュー裁定を追記
- [ ] git commit（⚠️ `git add -A` / `git add <dir>` 禁止）
