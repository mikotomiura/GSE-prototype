# タスクリスト — p321-paper-submission-prep

## 0. 前提
- [x] 引き継ぎ（`next-session-pr257-and-p321-submission.md`）・前タスクの判断を読む
- [x] PR #257 は研究者の指示で Mac 側へ（この端末の Codex 1 巡目の控え `C:/wt/pr257-codex-r1/`・worktree は撤去・何も push していない）
- [x] 規程を一次で確かめる（arXiv・Springer Nature・Zenodo・EMSE）
- [x] grill（判断 1–10）・`/start-task`（worktree `C:/wt/p321-submission`）

## 1. Zenodo（判断 4）
- [ ] token が効くかを読み取りだけで確かめる
- [ ] 下書きを作り DOI を予約する（公開しない）

## 2. 原稿（論文用リポジトリ）
- [ ] Data availability に DOI・著者情報に ORCID・README の Licence（原稿 = CC BY 4.0）
- [ ] `bash run.sh` / `bash paper/build.sh` exit 0
- [ ] 書いてはいけないことの grep

## 3. pdfLaTeX（判断 2）
- [ ] scratch に TinyTeX を置いて組む・結果を Tectonic と比べて記録

## 4. 研究者
- [ ] 主張と根拠の対応表を渡す → 通読 → 指摘を反映 → 研究者が確かめる（判断 1）
- [ ] カバーレターの下書き（判断 10）
- [ ] endorsement の依頼文の下書き（判断 3）

## 5. 完了
- [ ] 原稿の変更に `/cross-review`（⚠️ Codex は予算が戻ってから・判断 9）
- [ ] 投稿日の手順書（GitHub の public 化・Zenodo の公開・申告）
- [ ] GSE 側: `/finish-task` の出荷フロー
