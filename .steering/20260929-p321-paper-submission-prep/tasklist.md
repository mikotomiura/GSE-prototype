# タスクリスト — p321-paper-submission-prep

## 0. 前提
- [x] 引き継ぎ（`next-session-pr257-and-p321-submission.md`）・前タスクの判断を読む
- [x] PR #257 は研究者の指示で Mac 側へ（この端末の Codex 1 巡目の控え `C:/wt/pr257-codex-r1/`・worktree は撤去・何も push していない）
- [x] 規程を一次で確かめる（arXiv・Springer Nature・Zenodo・EMSE）
- [x] grill（判断 1–10）・`/start-task`（worktree `C:/wt/p321-submission`）

## 1. Zenodo（判断 4）
- [x] token が効くかを読み取りだけで確かめる（200・既存の記録には触れていない）
- [x] 下書きを作り DOI を予約する（deposition `23029603`・DOI `10.5281/zenodo.23029603`・未公開）

## 2. 原稿（論文用リポジトリ）
- [x] Data availability に DOI・README の Licence（原稿 = CC BY 4.0）→ `e1e527b`（⚠️ 未 push）
- [x] ORCID はタイトル頁に文字で（判断 7 の追記 2・`02380c5`。追記 1「本文に入れない」は規程の読み落としで取り消した）
- [x] `bash run.sh` / `bash paper/build.sh` exit 0（21 頁・Overfull `\vbox` 1 件は HEAD にもある）
- [x] 書いてはいけないことの grep（原稿・README・Zenodo の説明に GSE なし）

## 3. pdfLaTeX（判断 2）
- [x] scratch に TinyTeX v2026.09 を置いて組む → エラー 0・未定義 0・Overfull `\hbox` 0・21 頁・フォント全埋め込み（判断 2 の追記）

## 4. 研究者
- [x] 通読の手引き（`reading-guide.md`・主張と根拠の対応表）
- [x] 研究者の通読（2026-09-29・「表記などで気になった個所はない」→ 原稿は変えない・判断 1 の追記）
- [x] カバーレターの下書き（`cover-letter-draft.md`・判断 10）→ [ ] 研究者が確かめる
- [x] endorsement の依頼文の下書き（`endorsement-request-draft.md`・判断 3）→ [ ] 研究者が確かめて送る

## 5. 完了
- [x] `/cross-review` 1 巡目（code-reviewer ＋ security-checker（全履歴）＋ Codex 2 回・研究者の許可で予算を一時引き上げ）→ 裁定と修正（判断 11・論文用リポジトリ `02380c5`）
- [x] `/cross-review` 2 巡目（Codex 2 回 ＋ code-reviewer）→ 裁定と修正（判断 12・論文用リポジトリ `75ce1ff`・手順書を「取り消せる検証を先に」へ組み直した）。3 巡目は回さない・Codex の上限は 300000 に戻した
- [x] 投稿日の手順書（`submission-day-steps.md`）
- [x] 投稿日の A〜E（判断 13）: タグ `submission-2026-09-29`・zip の照合・投稿用の原稿（`C:/wt/emse-upload/`）・GitHub の public 化・Zenodo の公開
- [ ] DOI が doi.org で解決する（⚠️ DataCite の登録待ち）
- [ ] F: 研究者が EMSE に投稿（確定）→ 受付の日付と原稿番号を記録
- [ ] G: endorsement が取れたら arXiv（研究者）→ EMSE に申告・Zenodo と README に追記
- [x] 論文用リポジトリを push（`75ce1ff`・タグ `submission-2026-09-29`）
- [ ] GSE 側: `/finish-task` の出荷フロー
