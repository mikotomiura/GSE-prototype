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
- [x] endorsement の依頼文の下書き（`endorsement-request-draft.md`・判断 3）→ 送るのは §6（コードと URL を埋めた版は判断 20）

## 5. 完了
- [x] `/cross-review` 1 巡目（code-reviewer ＋ security-checker（全履歴）＋ Codex 2 回・研究者の許可で予算を一時引き上げ）→ 裁定と修正（判断 11・論文用リポジトリ `02380c5`）
- [x] `/cross-review` 2 巡目（Codex 2 回 ＋ code-reviewer）→ 裁定と修正（判断 12・論文用リポジトリ `75ce1ff`・手順書を「取り消せる検証を先に」へ組み直した）。3 巡目は回さない・Codex の上限は 300000 に戻した
- [x] 投稿日の手順書（`submission-day-steps.md`）
- [x] 投稿日の A〜E（判断 13）: タグ `submission-2026-09-29`・zip の照合・投稿用の原稿（`C:/wt/emse-upload/`）・GitHub の public 化・Zenodo の公開
- [x] DOI が doi.org で解決する（2026-09-29 20:55 JST に確認・DataCite の登録は 20:34 JST）
- [x] F: 研究者が EMSE に投稿（確定）→ **EMSE-D-26-01273**・2026-09-29（判断 15。タイトル頁の別添・results.tex の埋め込み・リンクは GitHub のタグ）
- [ ] G: arXiv → §6 に移した（2026-09-30）
- [x] 論文用リポジトリを push（`75ce1ff`・タグ `submission-2026-09-29`）
- [x] 完了時の `/cross-review`（Codex 1 回・README／code-reviewer・README と作業記録）→ 裁定と修正（判断 16・論文用リポジトリ `728e81c`）
- [ ] endorsement の依頼（研究者）→ §6 に移した（2026-09-30）
- [ ] GSE 側: `/finish-task` の出荷フロー

## 6. arXiv（2026-09-30・引き継ぎ §2 A・研究者の指示「Draft まで Claude・publish から研究者」）
- [x] A-0: 規程を一次で確かめ直す（判断 18: `results.tex` は最上位の候補にならない・cls と bst は同梱が必須・クロスリストと endorsement の関係は help に記述なし）
- [x] A-1: ソース一式（タグの 3 ファイル＋cls・bst＋`main.bbl`）を scratch で組む → 21 頁・BibTeX なしでも同じ（判断 19）。zip は `C:/wt/arxiv-upload/arxiv-source.zip`
- [x] 研究者の選択: cls と bst を同梱・著者 Mikoto Miura・コメントに投稿先を書かない・cs.SE ＋ cs.HC（判断 19）
- [x] A-2: 研究者のログイン（判断 20）
- [x] Start の段（ライセンス CC BY 4.0・規約・著者・cs.SE）= 研究者 → "You are not endorsed for this archive"（判断 20）
- [x] endorsement の依頼のメール（03:21 JST）→ 依頼文を埋めた版と添付 PDF（`C:/wt/arxiv-upload/`・判断 20）
- [x] 最初の知り合い → endorser の資格が無かった（判断 22）
- [x] 候補の短いリスト（`C:/wt/arxiv-upload/endorser-shortlist.md`）・Authorea は今は使えない（判断 23）
- [ ] 研究者がリストの上から 1 人ずつ依頼を送る（endorse できる条件は `endorsement-request-draft.md` の冒頭）→ endorse される
- [ ] A-3: 下書き `submit/8151855`（期限 2026-10-13）の続き: Start（研究者）→ Add Files（zip）→ 組版のログと Preview（TeX Live 2025）→ メタデータ・cs.HC のクロスリスト
- [ ] A-4: 研究者が cls と bst の同梱を再確認して最後に Submit（判断 19・21）→ 公開後に EMSE へ申告・Zenodo の related_identifiers・README
- [x] 完了時の `/cross-review`（code-reviewer ＋ Codex 1 回・4 ファイル限定）→ 裁定と修正・zip の 6 ファイルの走査（判断 21）
