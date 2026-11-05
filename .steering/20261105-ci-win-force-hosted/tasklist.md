# タスクリスト

- [x] ci.yml で `gse-win` に向く判定を全部探す（probe の 1 か所だけ。`build-windows` は元から `windows-latest`）
- [x] probe の step に env と分岐を足す
- [x] actionlint を前後で比べる（どちらも既存の 3 件・足した行に指摘なし）
- [x] probe の script を 5 通りに走らせる（下の decisions.md 判断 2）
- [ ] code-reviewer と /cross-review
- [ ] コミット
- [ ] 研究者の確かめの後: リポジトリの変数を設定（`gh variable set GSE_WIN_FORCE_HOSTED --body 1`）→ push → PR → run のログで hosted を確かめる → マージ
- [ ] 12 月に G-GEAR が空いたら変数を消す（研究者に確かめてから）
