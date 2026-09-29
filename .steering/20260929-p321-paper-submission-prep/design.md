# design — p321-paper-submission-prep

## 置き場所

| 何 | どこ |
|---|---|
| 作業記録（本ディレクトリ） | GSE の worktree `C:/wt/p321-submission`（ブランチ `docs/p321-paper-submission-prep`）。⚠️ main checkout は別ターミナルの IME 論文のセッションが使っている |
| 原稿・再現一式の変更 | 論文用リポジトリ `C:/self-resolution-measure`（`main`） |
| pdfLaTeX の TeX・Zenodo の API の応答・一時ファイル | このセッションの scratchpad（リポジトリに入れない） |
| Zenodo の token | `C:/zenodo/zenodo_token.txt`（研究者が置いた）。⚠️ プロセス内で読むだけ。コピー・表示・コミット・外部 LLM への送信をしない |

## 手順

1. **Zenodo の下書きと DOI の予約**（判断 4）
   - token が効くかを読み取りだけで確かめる（`GET /api/deposit/depositions`）。
   - 下書きを作る（`POST /api/deposit/depositions`）: 題「Replication package for: …」・creators（Mikoto Miura・ORCID）・説明（学術的な英語・GSE に言及しない）・ライセンス CC BY 4.0（コードの Apache-2.0 は説明と同梱の LICENSE に書く）・`prereserve_doi: true`。
   - 予約された DOI を控える。⚠️ ファイルのアップロードと公開は投稿日（判断 4）。下書きを消すと DOI も失われるので消さない。
2. **原稿の変更**（論文用リポジトリ）
   - Data availability: 仮置きを予約した DOI に置き換える。
   - 著者情報に ORCID（判断 7・`sn-jnl` の書き方を確かめてから）。
   - README の Licence 節: 原稿（`paper/main.tex`・`paper/refs.bib`）を CC BY 4.0 にする（判断 5）。DOI を書く。
   - `bash run.sh` と `bash paper/build.sh` が exit 0。
3. **pdfLaTeX での組版**（判断 2）
   - scratch に TinyTeX（持ち運べる形）を置き、`paper/` の複製で `pdflatex → bibtex → pdflatex ×2`。
   - 見るもの: エラー・未定義の参照と引用・Overfull の数・頁数（Tectonic の 21 頁と比べる）・フォントの埋め込み。
4. **研究者の通読**（判断 1）: 主張と根拠の対応表（1 頁）を作って渡す → 指摘を反映 → 研究者が確かめる。
5. **カバーレター・endorsement の依頼文の下書き**（判断 3・10）: 本ディレクトリに置く（公開しない）。
6. **`/cross-review`**: 原稿の変更（論文用リポジトリの差分）を GSE の worktree に `git fetch` してラッパーを範囲指定で呼ぶ（前タスク判断 9・memory `reference_codex_review_other_repo`）。⚠️ 今日は Codex の予算がほぼ尽きている（判断 9）→ 明日以降。
7. **投稿日**（研究者が行う・私は手順書を用意）: GitHub の public 化 → Zenodo に同じコミットの `git archive` の zip を上げて公開（研究者に確認してから）→ EMSE に投稿（研究者）→ endorsement が取れたら arXiv（研究者）→ 編集部に申告。

## テスト戦略

- 原稿の数値と主張は既存の機械検査（`make_results.py` の `claims()`・`--selftest`・`build.sh` の `cmp`）がそのまま守る。
- 原稿を直すたびに `bash run.sh` と `bash paper/build.sh`（exit 0）。
- pdfLaTeX の結果は Tectonic の結果と並べて記録する（頁数・警告）。
- 公開物の書き方: 書いてはいけないことの grep（前タスクの 11 パターン・GSE への言及なし）を原稿・README・Zenodo の説明・カバーレターに当てる。

## 結果（2026-09-29）

- 手順 1〜7 をこの順に実施し、**EMSE に投稿した（EMSE-D-26-01273）**。投稿日の手順は `submission-day-steps.md` を 2 巡目のレビューで「取り消せる検証を先に」の順（A〜G）に組み直した版で進めた（判断 12・13）。
- 計画から変わった点:
  - 通読は研究者の返答「表記などで気になった個所はない」で原稿を変えなかった（判断 1 の追記）。
  - ORCID は本文に入れない案 → EMSE の Title Page の規程を読み落としていたと分かり、タイトル頁に文字で入れた（判断 7 の追記 2）。
  - 投稿する版だけ `[referee,lineno]`（テンプレートの手引きの依頼・研究者の選択・判断 11）。
  - Editorial Manager の実物に合わせて、別添のタイトル頁（`title-page.docx`）を足し、`results.tex` を投稿用の `main.tex` に埋め込み、データへのリンクは GitHub のタグにした（判断 15）。
  - Zenodo の DOI の登録（DataCite）は公開の約 1 時間後だった → 解決を確かめてから投稿を確定した（判断 13）。
  - 公開後に README を書き直した（研究者の依頼・判断 14）。
- 残り（引き継ぎ `.steering/_handoff/next-session-p321-arxiv-and-review.md`）: endorsement が取れたら arXiv（21 頁の版・CC BY 4.0）→ 編集部への申告・Zenodo と README への追記／査読の結果への対応。

