# 投稿日の手順（判断 3・4・9・11）

⚠️ 前提: 通読（済み）・pdfLaTeX（済み）・原稿の変更への `/cross-review`・カバーレターの確認が済んでいること（判断 9）。
⚠️ 🔒 の付いた操作は取り消しにくい → **その場で研究者に確かめてから**行う。
★ 手順 1（GitHub の public 化）と手順 2（Zenodo の公開）は**間を置かずに続けて**行う（間があると README の DOI が解決しない時間ができる）。

## 0. 論文用リポジトリを確定する（私）
1. `git status` が clean・`bash run.sh` と `bash paper/build.sh` が exit 0。
2. ★ **公開前の履歴の検査**: 2026-09-29 に security-checker が全 11 コミット（`416a0fc`〜`e1e527b`）を検査済み（秘密情報・ローカルパス・GSE への言及・再配布しないファイル = 0 件）。⚠️ それ以後のコミット（`02380c5` 以降）は、同じ観点で差分を検査してから進む。GitHub 側（ブランチ main だけ・タグ・Release・PR・Issue・Actions の実行がいずれも 0）も `gh api` で見直す。
3. 投稿する版にタグを付ける（例 `submission-2026-MM-DD`）→ ★ **そのタグだけ**を push する（`git push origin main` と `git push origin <tag>`。⚠️ `--tags` は使わない）。

## 1. 🔒 GitHub を public にする（研究者の確認の後）
- `gh repo edit mikotomiura/self-resolution-measure --visibility public --accept-visibility-change-consequences`
- ⚠️ 履歴ごと公開される（`4a81a43` より前のコミットの著者のメールアドレスを含む・前タスク判断 12 で承知済み）。
- 確かめる: ログインしていないブラウザで README が見える。

## 2. 🔒 Zenodo を公開する（研究者の確認の後・私が token で行う）
1. `git archive --format=zip --prefix=self-resolution-measure/ <tag> -o <scratch>/self-resolution-measure-<tag>.zip`（★ 追跡しているファイルだけ。`raw/` とテンプレートは入らない）。
2. ★ **zip を検証する**（⚠️ 公開後はファイルを差し替えられない）:
   - 空のディレクトリに展開し、ファイルの一覧が `git ls-tree -r --name-only <tag>` と一致する。
   - D1 の zip を `raw/` に置いて（`DATA.md` の取得手順）`bash run.sh` が exit 0（同梱の `results/` と一致）。
   - `paper/build.sh` はテンプレートを取得するので、ネットワークがあれば exit 0 まで確かめる。
3. 下書き `23029603` の bucket にアップロード → metadata の `version` = タグ・`related_identifiers` に当該タグの URL（`https://github.com/mikotomiura/self-resolution-measure/tree/<tag>`）を足す。
4. 下書きの画面（`https://zenodo.org/deposit/23029603`）を研究者が見て確かめる。
5. 公開（`POST /api/deposit/depositions/23029603/actions/publish`）。
6. `https://doi.org/10.5281/zenodo.23029603` が記録のページに解決することを確かめる（★ DOI は公開した時点で登録される）。

## 3. 投稿用の原稿を作る（私・scratch）
★ 判断 11 の追記: 投稿する版だけ `\documentclass[pdflatex,sn-basic,referee,lineno]{sn-jnl}`（行間 ＋ 行番号・32 頁）。リポジトリと arXiv の原稿は今の行間（21 頁）のまま。
1. タグの `paper/` から `main.tex`・`results.tex`・`refs.bib` と、`build.sh` が SHA-256 を照合した `sn-jnl.cls`・`sn-basic.bst` を、**サブフォルダの無い 1 つのフォルダ**に置く（規程 "Please do not use subfolders"）。
2. `main.tex` の `\documentclass[pdflatex,sn-basic]{sn-jnl}` を上の形に置き換える（1 か所だけであることを確かめる）。
3. scratch の TinyTeX（判断 2 の追記）で `pdflatex → bibtex → pdflatex ×3`。エラー 0・未定義 0・Overfull `\hbox` 0 を確かめる。★ ここで出来た `main.bbl` も上げるファイルに含める（投稿システムが BibTeX を回さなくても参考文献が組めるように。⚠️ EMSE の規程に `.bbl` の記述は無い）。

## 4. 🔒 EMSE に投稿する（研究者）
- 投稿システム: EMSE の規程ページの案内に従う。
- 上げるファイル（サブフォルダなし）: `main.tex`（手順 3 の版）・`results.tex`・`refs.bib`・`main.bbl`・`sn-jnl.cls`・`sn-basic.bst`。
- ★ 投稿システムが組んだ PDF を承認する前に見る: **32 頁前後**・行番号と行間がある・表 1〜5 が枠に収まる・参考文献が著者名と年で並ぶ・タイトル頁に ORCID・Data availability の DOI。
- 入力: ORCID `0009-0000-4196-0508`（判断 7）・推薦査読者なし（判断 8）・カバーレター（`cover-letter-draft.md` を研究者が直したもの）・Statements は原稿のとおり。
- 投稿後: 受付のメールを記録する（`decisions.md` に日付と原稿番号）。

## 5. 🔒 arXiv（endorsement が取れてから・研究者）
- カテゴリ cs.SE・ライセンス **CC BY 4.0**（判断 5・⚠️ 版ごとに選び、選んだ版のライセンスは後から変えられない）。原稿は今の行間（21 頁）の版。
- ⚠️ TeX のソースの出し方（`.bbl` の要否・TeX Live の版）は、出す時に arXiv の help を一次で確かめる（未確認）。
- 出したら: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"）・Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる）・README にプレプリントを書く。
