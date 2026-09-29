# 投稿日の手順（判断 3・4・9・11・12）

⚠️ 前提: 通読（済み）・pdfLaTeX（済み）・原稿の変更への `/cross-review`（2 巡済み）・カバーレターの確認が済んでいること（判断 9）。
⚠️ 🔒 の付いた操作は取り消しにくい → **その場で研究者に確かめてから**行う。
★ **並び順の原則**（判断 12）: 取り消せる検証（A〜C）を**すべて**、取り消しにくい操作（D 以降）より前に済ませる。検証で失敗したら、直して A からやり直す（タグはまだ手元にしか無いので付け直せる）。
★ D（GitHub の public 化）と E（Zenodo の公開）は**間を置かずに続けて**行う（間があると README の DOI が解決しない時間ができる）。そのため E で時間のかかる作業（zip の検証・アップロード・下書きの確認）は C までに済ませておく。

## A. 論文用リポジトリを確定する（私・取り消せる）
1. `git status` が clean・`bash run.sh` と `bash paper/build.sh` が exit 0。
2. ★ **公開前の履歴の検査**: 2026-09-29 に security-checker が `416a0fc`〜`e1e527b` の全 11 コミットを検査済み（秘密情報・ローカルパス・GSE への言及・再配布しないファイル = 0 件）。⚠️ それ以後のコミット（`02380c5` 以降）は、**コミットごとに**（`git log -p <e1e527b>..<tag>` で各コミットの変更を 1 つずつ）同じ観点で検査する（⚠️ 範囲の一括 diff だと、途中で入れて後で消したものが見えない）。GitHub 側（ブランチ main だけ・タグ・Release・PR・Issue・Actions の実行がいずれも 0）も `gh api` で見直す。
3. 投稿する版にタグを**手元で**付ける（例 `submission-2026-MM-DD`）。⚠️ まだ push しない。

## B. 公開する zip を作って検証する（私・scratch・取り消せる）
1. `git -c core.autocrlf=false archive --format=zip --prefix=self-resolution-measure/ <tag> -o <scratch>/self-resolution-measure-<tag>.zip`（★ 追跡しているファイルだけ。`raw/` とテンプレートは入らない。⚠️ この機械の system gitconfig は `core.autocrlf=true` で、`.gitattributes` が LF を固定しているのは `*.sh`・`*.py`・`paper/*.tex`・`paper/*.bib` だけ → 変換を止めて作る）。
2. 空のディレクトリに展開し、**中身まで**照合する: 接頭辞を外したファイルの一覧（ディレクトリの項目を除く）が `git ls-tree -r --name-only <tag>` と一致し、各ファイルの `git hash-object` が `git ls-tree -r <tag>` の blob ID と一致する。
3. 展開したものの `raw/` に D1 の zip を置いて（`DATA.md` の取得手順）`bash run.sh` が exit 0（同梱の `results/` と一致）。`bash paper/build.sh` はネットワークと Tectonic（`TECTONIC=<scratch の tectonic.exe>`）が要る → exit 0。
4. Zenodo の下書き `23029603` の bucket に、この zip をアップロードする（★ 下書きのファイルは公開前なら消せる）。metadata の `version` = タグ・`related_identifiers` に当該タグの URL（`https://github.com/mikotomiura/self-resolution-measure/tree/<tag>`）を足す。
5. 下書きの画面（`https://zenodo.org/deposit/23029603`）を研究者が見て確かめる。

## C. 投稿用の原稿を作る（私・scratch・取り消せる）
★ 判断 11: 投稿する版だけ `\documentclass[pdflatex,sn-basic,referee,lineno]{sn-jnl}`（行間 ＋ 行番号・32 頁）。リポジトリと arXiv の原稿は今の行間（21 頁）のまま。
1. タグの `paper/` から `main.tex`・`results.tex`・`refs.bib` と、`build.sh` が SHA-256 を照合した `sn-jnl.cls`・`sn-basic.bst` を、**サブフォルダの無い 1 つのフォルダ**に置く（規程 "Please do not use subfolders"）。
2. `main.tex` の `\documentclass[pdflatex,sn-basic]{sn-jnl}` を上の形に置き換える（1 か所だけであることを確かめる）。
3. scratch の TinyTeX（判断 2 の追記）で `pdflatex → bibtex → pdflatex ×3`。エラー 0・未定義 0・Overfull `\hbox` 0・32 頁・タイトル頁に ORCID が 1 回を確かめる。★ ここで出来た `main.bbl` も上げるファイルに含める（投稿システムが BibTeX を回さなくても参考文献が組めるように。⚠️ EMSE の規程に `.bbl` の記述は無い）。
4. （できれば）研究者が EMSE の投稿システムでファイルを上げ、**システムが組んだ PDF を見るところまで**進める（承認はしない。規程 "automatically compiled into a single PDF file to be approved by you at the end of the submission process"）。見るもの: 32 頁前後・行番号と行間・表 1〜5 が枠に収まる・参考文献が著者名と年で並ぶ・タイトル頁に ORCID が 1 回（⚠️ クラスの内部マクロに足した行なので、ここで必ず見る・判断 7 の追記 2）。

## D. 🔒 push して GitHub を public にする（研究者の確認の後）
1. `git push origin main` と `git push origin <tag>`（★ そのタグだけ。⚠️ `--tags` は使わない）。
2. `gh repo edit mikotomiura/self-resolution-measure --visibility public --accept-visibility-change-consequences`
3. ⚠️ 履歴ごと公開される（`4a81a43` より前のコミットの著者のメールアドレスを含む・前タスク判断 12 で承知済み）。
4. 確かめる（公開後の実物）: ログインしていないブラウザで README が見える・`raw/` と `sn-jnl.cls`・`sn-basic.bst` が無い・ブランチは main だけ。

## E. 🔒 Zenodo を公開する（D の直後・私が token で行う）
1. 公開（`POST /api/deposit/depositions/23029603/actions/publish`）。⚠️ 公開後はファイルを差し替えられない（新しい版を作るしかない）。
2. `https://doi.org/10.5281/zenodo.23029603` が記録のページに解決することを確かめる（★ DOI は公開した時点で登録される）。

## F. 🔒 EMSE に投稿する（研究者・E の後）
- 上げるファイル（サブフォルダなし）: `main.tex`（C の版）・`results.tex`・`refs.bib`・`main.bbl`・`sn-jnl.cls`・`sn-basic.bst`。C.4 で途中まで進めていれば、その続きから。
- システムが組んだ PDF を C.4 と同じ観点で見てから承認する。Data availability の DOI と GitHub の URL がこの時点で開けることも確かめる。
- 入力: ORCID `0009-0000-4196-0508`（判断 7）・推薦査読者なし（判断 8）・カバーレター（`cover-letter-draft.md` を研究者が直したもの）・Statements は原稿のとおり。
- 投稿後: 受付のメールを記録する（`decisions.md` に日付と原稿番号）。

## G. 🔒 arXiv（endorsement が取れてから・研究者）
- カテゴリ cs.SE・ライセンス **CC BY 4.0**（判断 5・⚠️ 版ごとに選び、選んだ版のライセンスは後から変えられない）。原稿は今の行間（21 頁）の版。
- ⚠️ TeX のソースの出し方（`.bbl` の要否・TeX Live の版）は、出す時に arXiv の help を一次で確かめる（未確認）。
- 出したら: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"）・Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる）・README にプレプリントを書く。
