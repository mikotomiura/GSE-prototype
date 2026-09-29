# 投稿日の手順（判断 3・4・9）

⚠️ 前提: 通読の反映・pdfLaTeX・原稿の変更への `/cross-review`・カバーレターの確認が済んでいること（判断 9）。
⚠️ 🔒 の付いた操作は取り消しにくい → **その場で研究者に確かめてから**行う。

## 0. 論文用リポジトリを確定する（私）
1. `git status` が clean・`bash run.sh` と `bash paper/build.sh` が exit 0。
2. 投稿する版にタグを付ける（例 `submission-2026-MM-DD`）→ `git push origin main --tags`（private のまま）。

## 1. 🔒 GitHub を public にする（研究者の確認の後・私か研究者）
- `gh repo edit mikotomiura/self-resolution-measure --visibility public --accept-visibility-change-consequences`
- ⚠️ 履歴ごと公開される（`4a81a43` より前のコミットの著者のメールアドレスを含む・前タスク判断 12 で承知済み）。
- 確かめる: ログインしていないブラウザで README が見える・`raw/` と `sn-jnl.cls` / `sn-basic.bst` が入っていない（`.gitignore`）。

## 2. 🔒 Zenodo を公開する（研究者の確認の後・私が token で行う）
1. `git archive --format=zip --prefix=self-resolution-measure/ <tag> -o <scratch>/self-resolution-measure-<tag>.zip`（★ 追跡しているファイルだけ・`raw/` とテンプレートは入らない）。
2. 下書き `23029603` の bucket にアップロード → metadata の `version` = タグ・`related_identifiers` に当該コミットの URL（`https://github.com/mikotomiura/self-resolution-measure/tree/<tag>`）を足す。
3. 下書きの画面（`https://zenodo.org/deposit/23029603`）を研究者が見て確かめる。
4. 公開（`POST /api/deposit/depositions/23029603/actions/publish`）。⚠️ 公開後はファイルを差し替えられない（新しい版を作るしかない）。
5. `https://doi.org/10.5281/zenodo.23029603` が記録のページに解決することを確かめる（★ DOI は公開した時点で登録される）。

## 3. EMSE に投稿する（研究者）
- 投稿システム: EMSE の "Submit manuscript"（規程ページの案内に従う）。
- 原稿: LaTeX のソースを**サブフォルダなしで**上げる（規程 "Please do not use subfolders"）: `main.tex`・`results.tex`（`\input` される）・`refs.bib`・`sn-jnl.cls`・`sn-basic.bst`（＋必要なら `main.bbl`）。
- ★ 投稿システムが組んだ PDF を承認する前に見る: **21 頁前後**・表 1〜5 が枠に収まっている・参考文献が著者名と年で並んでいる・Data availability の DOI（判断 2 の追記: 手元の pdfLaTeX では問題なし）。
- 入力: ORCID `0009-0000-4196-0508`（判断 7）・推薦査読者なし（判断 8）・カバーレター（`cover-letter-draft.md` を研究者が直したもの）・Statements は原稿のとおり。
- 投稿後: 受付のメールを記録する（`decisions.md` に日付と原稿番号）。

## 4. arXiv（endorsement が取れてから・研究者）
- カテゴリ cs.SE・ライセンス **CC BY 4.0**（判断 5・⚠️ 後から変えられない）。
- ⚠️ TeX のソースの出し方（`.bbl` を同梱する必要があるか・対応する TeX Live の版）は、出す時に arXiv の help を一次で確かめる（未確認）。
- 出したら: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"）・Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる）・README にプレプリントを書く。
