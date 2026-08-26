# タスクリスト

## 準備
- [x] 関連する docs を読む（`ci.yml` の `decide-win-runner`/`check` 全文、コメント込み）
- [x] 障害復旧を確認する（githubstatus.com incidents API / Actions component）
- [x] requirement.md の観測台帳・受け入れ条件を更新する

## 実装
- [x] `ci.yml`: `decide-win-runner` の `runs-on` を `ubuntu-latest` → `[self-hosted, gse-mac]`
- [x] 変更理由・新しいトレードオフをコメントで明記する

## テスト
- [ ] 本ブランチへ push し、実 run で `decide-win-runner` が `gse-mac` 上で解決されることを確認
- [ ] `check(win)` / `check(mac)` が従来どおり success することを確認

## レビュー
- [x] code-reviewer によるレビュー → HIGH 2件・MEDIUM 2件を反映済み（design.md 参照）
- [x] security-checker によるレビュー（`RUNNER_STATUS_TOKEN` の扱いに変更が無いことを含め確認） → MEDIUM（M-1 スロット競合）を反映済み。fork PR 経路・ログ混入・checkout 有無は問題なしと確認
- [x] HIGH 指摘への対応
- [x] `/cross-review`（Codex 独立レビュー） → ブロッキング HIGH 新規指摘なし。低優先2件を design.md に反映済み

## ドキュメント
- [ ] 変更なし（`docs/` 更新不要 — CI 内部実装の変更）

## 完了処理
- [ ] design.md の最終化
- [ ] git commit
- [ ] push → CI green 確認
- [ ] PR #119 を main へマージ
- [ ] `/finish-task` Step 5（マージ後の CI 発火確認）が OK を返すことを確認
