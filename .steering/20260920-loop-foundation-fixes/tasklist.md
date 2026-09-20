# タスクリスト

## 準備
- [x] 一次資料を読む（`loop-run.sh` / `loop-worktree-deny.sh` / `.claude/settings.json` / `_loop-config.json` / `docs/loop-engineering.md` / 起票 3・10 / 判断 25・26）
- [x] grill で判断分岐を閉じる（判断 1〜6）
- [x] `.steering/20260920-loop-foundation-fixes/` を作成

## 実測
- [x] **M1 対照**: deny 7 件で `git checkout main` → ★ **通った**（起票 10 の再現）
- [x] **M1b**: `permission_denials` の実スキーマを採取 → ⚠️ **`.tool_name` だけでは内訳が分からない**
- [x] **M2**: deny 9 件で同じ依頼 → ★ **拒否された**
- [x] **M3**: ⚠️★★★ `git -C . checkout main` は **deny 9 件でも通る**（★ 想定外の追加実測）
- [x] **M4**: ⚠️ 逸脱した worktree は `--cleanup` で撤去できない（★ 起票 18 へ）
- [x] `measurements.md` に生ログを残す
- [x] 使い捨て worktree を撤去（⚠️ `--cleanup` が空振りしたので手で `git worktree remove --force`）

## 実装
- [x] `scripts/loop-worktree-deny.sh` — `DENY_REQUIRED` 7 → 9 件 ＋ 文言
- [x] `.steering/_template/loop-config.README.md` — 逐語リスト 9 件 ＋ 「境界はブランチ検査」
- [x] `scripts/loop-run.sh` — `ensure_branch`（**名前 ＋ 履歴の子孫性**）
- [x] `scripts/loop-run.sh` — `issue_done` の**直前**にも検査（★ レビュー HIGH）
- [x] `scripts/loop-run.sh` — 履歴アンカーを **worktree 生成時点**に固定（★ Codex HIGH）
- [x] `scripts/loop-run.sh` — `permission_denials` の内訳保存 ＋ **秘密のマスク** ＋ 14 日 prune
- [x] `scripts/loop-run.sh` — `issue_status_key`（**装飾を剥がす**）/ Status フィルタ / `--issues` の警告と記録
- [x] `scripts/loop-run.sh` — ⚠️ `preflight_dag` の存在確認を `ALL_FILES` に（回帰の予防）
- [x] `scripts/loop-run.sh` — `--issues` の id 検証 / `detail` の長さ制限 / 成果物を `mv` で書く
- [x] レポートに除外した id を出す
- [x] `.gitignore` — `**/_loop-artifacts/`（⚠️ `.steering/**` 限定では足りない）
- [x] `.claude/commands/loop-issue.md` — 「worker は commit してから終わる」（判断 5）

## テスト
- [x] `scripts/loop-worktree-deny-test.sh` の期待件数を定数化（7 → 9・`EXPECT_MERGED` も）
- [x] `scripts/loop-run-guard-test.sh` を新規作成（**B1〜B7 / S1〜S9 / D1〜D2 = 35 件**・★ B7 / S9 は判断 9 で追加）
- [x] ⚠️ **陰性対照**を入れる（B2 = 逸脱なし ／ B6 = 正当な `--amend`）
- [x] ⚠️ **突然変異 8 種**（M-a〜M-h）で該当検査が赤になることを確認（★ M-h は `measurements.md` §M-h）
- [x] ⚠️ **検査が見ていないもの 6 項目**を検査自身のコメントに明記
- [x] `bash scripts/loop-run-guard-test.sh` → **35 / 35**（★ 2026-09-20 に main で再実行して確認）
- [x] `bash scripts/loop-worktree-deny-test.sh` → **34 / 34**
- [x] `bash scripts/check-shell-portability.sh` → **12 / 12**（⚠️ 一度赤 = `$wt」`）
- [x] `bash scripts/check-tests-are-wired.sh` → **16 / 16**（★ CI に配線）
- [x] ⚠️ `tr -cd '\r' | wc -c` が 0

## ドキュメント
- [x] `docs/loop-engineering.md` — 「多層防御であって境界ではない」を**実測で更新**
- [x] `docs/loop-engineering.md` — ブランチ検査 / Status フィルタ / denials の節を追加
- [x] `docs/loop-engineering.md` — 新語（ブランチ検査 / worktree 逸脱）を「基本単位」に（判断 6）
- [x] `blockers.md` — 起票 3 / 10 を**閉じた**（⚠️ 消していない）＋ **起票 18 を新規**

## レビュー
- [x] `code-reviewer`（opus）＋ `security-checker`（opus）を**並列**起動
- [x] HIGH 3 / MEDIUM 7 / LOW 4 を反映（★ 判断 7）
- [x] `/cross-review` **1 巡目**（Codex gpt-5.5・パス限定）→ HIGH 1 件採用 / MEDIUM 2 件は**偽陽性として却下**（★ 判断 8）
- [x] `/cross-review` **2 巡目**（★ 研究者の指示で上限を 300,000 → 350,000 へ**一時**引き上げて実行）
      → MEDIUM 1 件採用（**S9** = ファイル名由来 id の単語分割）／ HIGH 1 件は**仕様として裁定**し **B7**
      で「検出しないこと」を固定 ／ 未決 2 件は研究者へ（★ 判断 9）
      → ★ 実消費 41,188（300,360 → 341,548）。**上限は 300,000 に戻した**
      （⚠️ `today.tokens_used` は戻していない = 本日これ以上の `/cross-review` は予算ガードで止まる）

## 完了処理
- [x] `design.md` / `decisions.md` / `measurements.md` の最終化
- [x] git commit（★ 6 本・⚠️ `git add -A` は使っていない）
- [x] `.codex/budget.json` の記帳をコミット（⚠️ `git checkout --` で戻さない）
- [x] ★ **push / PR / merge 済み**（`fix/loop-foundation-guards` → **PR #212** → `main` = `60d4257`）
- [x] ★ **main の CI が緑**（run `35504518108` = success / 2026-09-20 10:14Z・6m6s）
      → `decide-win-runner` / `frontend-check` / `check (gse-win-selfhosted)` / `check (gse-mac-selfhosted)` が success。
      ⚠️ `build-windows` / `build-macos` / `release` は **skipped**（★ tag push でないため = 設計どおり）
