# タスクリスト — cs1-landscape

- [x] worktree を origin/main（28568c5c）から切る・ディスク 8.8 GB（≥ 3 GB）
- [x] requirement.md・decisions.md（判断 1 承諾）
- [ ] Dataverse API でファイル一覧 → `keystrokes.csv`・`readme.txt` だけ取得 → `data.md`
- [ ] 列名・EventType の種類と件数・人と課題の単位を確かめる（中身は出さない）
- [ ] `conditions.md`（変換の対応表・holdout・L1〜L6 の当て方）をコミット
- [ ] 変換スクリプト → replay → 集計（中間は 1 本ずつ消す）
- [ ] `notes.md`（課題の数・1 単位の長さの四分位・言える範囲）
- [ ] code-reviewer ＋ /cross-review（並列）
- [ ] main へ `--no-ff`・`[skip ci]`（コードと CI 設定が無いことを確かめる）

## 場面ごとの道具
- コード（変換・集計の python）→ code-reviewer ＋ /cross-review
- Codex には集計と docs の diff だけ（打鍵の本文・生ファイルは送らない）
