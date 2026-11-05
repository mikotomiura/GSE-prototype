# タスクリスト

- [x] ci.yml で `gse-win` に向く判定を全部探す（probe の 1 か所だけ。`build-windows` は元から `windows-latest`）
- [x] probe の step に env と分岐を足す
- [x] actionlint を前後で比べる（どちらも既存の 3 件・足した行に指摘なし）
- [x] probe の script を 5 通りに走らせる（下の decisions.md 判断 2）
- [x] code-reviewer と /cross-review
- [x] コミット
- [x] レビューの指摘を直す（decisions.md 判断 3）
- [x] /cross-review の 2 回目（`--ack-filtered`・判断 4）と指摘への対応（判断 5）
- [x] 研究者の確かめの後: リポジトリの変数を設定（`gh variable set GSE_WIN_FORCE_HOSTED --body 1`）→ この枝を push → PR → PR の run の `decide-win-runner` のログで notice `vars.GSE_WIN_FORCE_HOSTED=1 -> hosted (forced` を、`check` の Windows のレグのログ冒頭の `Runner name:` で hosted で走ったことを確かめる → マージ。変数を設定する直前に `gh run list --status queued` と `--status in_progress` が 0 件であることを確かめる（判断 5）
- [x] hosted の Windows の上限を 60 分に（判断 7）・main の既存の違反を直す（判断 6）・11a は別タスク（判断 8）
- [ ] その後に R1（`feature/nudge-default-off`）へ main を取り込み、`git show feature/nudge-default-off:.github/workflows/ci.yml | grep -c GSE_WIN_FORCE_HOSTED` が 0 でないことを確かめてから R1 を push する（判断 3。M5 の枝も同じ）
- [ ] 12 月に G-GEAR が空いたら変数を消す（研究者に確かめてから）
