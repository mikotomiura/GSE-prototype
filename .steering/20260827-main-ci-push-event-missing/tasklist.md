# タスクリスト

## 準備
- [x] 関連する docs を読む（`ci.yml` の `decide-win-runner`/`check` 全文、コメント込み）
- [x] 障害復旧を確認する（githubstatus.com incidents API / Actions component）
- [x] requirement.md の観測台帳・受け入れ条件を更新する

## 実装
- [x] `ci.yml`: `decide-win-runner` の `runs-on` を `ubuntu-latest` → `[self-hosted, gse-mac]`
- [x] 変更理由・新しいトレードオフをコメントで明記する

## テスト
- [x] 本ブランチへ push し、実 run で `decide-win-runner` が `gse-mac` 上で解決されることを確認 → run 32999649870, `macbook-air-m-arm64` 上で success、2秒で gse-win online 検知
- [x] `check(win)` / `check(mac)` が従来どおり success することを確認 → win: `g-gear-win-x64` success / mac: `macbook-air-m-arm64` success

## レビュー
- [x] code-reviewer によるレビュー → HIGH 2件・MEDIUM 2件を反映済み（design.md 参照）
- [x] security-checker によるレビュー（`RUNNER_STATUS_TOKEN` の扱いに変更が無いことを含め確認） → MEDIUM（M-1 スロット競合）を反映済み。fork PR 経路・ログ混入・checkout 有無は問題なしと確認
- [x] HIGH 指摘への対応
- [x] `/cross-review`（Codex 独立レビュー） → ブロッキング HIGH 新規指摘なし。低優先2件を design.md に反映済み

## ドキュメント
- [ ] 変更なし（`docs/` 更新不要 — CI 内部実装の変更）

## 完了処理
- [x] design.md の最終化
- [x] git commit（`adbf178`, `a99bea3`）
- [x] push → CI green 確認（run 32999649870, 33000351336 とも success）
- [x] PR #119 を main へマージ（merge commit `d6ff124`）
- [x] `/finish-task` Step 5（マージ後の CI 発火確認）が OK を返すことを確認 → run 33000927868 success

## クローズ（2026-08-26 完了）
本起票は受け入れ条件 5 件すべて満たし、クローズする。
- 原因: GitHub Actions major outage（特定済み）
- 復旧確認: run 32996144273（イベント起因、success）
- decide-win-runner self-hosted 化: 実装・レビュー（code-reviewer/security-checker/cross-review）・実 run 検証済み
- PR #119: マージ済み（`d6ff124`）
- finish-task Step 5: main への push で run 発火を確認（OK）
