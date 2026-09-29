# 次セッション — 2 本目の論文（EMSE-D-26-01273）の arXiv と、査読への対応

> 作成: 2026-09-29（EMSE への投稿の後）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す（EMSE の状態・arXiv・Zenodo・GitHub）。
> 一次の記録: `.steering/20260929-p321-paper-submission-prep/decisions.md`（判断 1–15）・`submission-day-steps.md`。

## §0 打ち込む用

```
git fetch origin してから git show origin/main:.steering/_handoff/next-session-p321-arxiv-and-review.md を読んで、§2 のうち研究者に言われたものを進めてください。
⚠️ main checkout（C:/GSE-prototype）は別ターミナルの IME 論文のセッションが使っているかもしれない。git status を見て、使っていれば GSE 側の作業は git worktree で切る。
Skill: git-workflow・verify-before-claiming・subagent-delegation・citation-ssot（原稿を直すとき）・browser-verification（Chrome を使うとき）。
応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。取り消しにくい操作（arXiv への投稿・Zenodo の新しい版の公開・EMSE への返信）はその場で研究者に確かめる。
```

## §1 状態（2026-09-29 23:20 JST に測った値）

- **EMSE**: 原稿番号 **EMSE-D-26-01273**・2026-09-29 投稿・状態 Submitted（Editorial Manager https://www.editorialmanager.com/emse ・研究者のアカウントは ORCID 0009-0000-4196-0508 に結び付け済み）。投稿した版は行間と行番号つき（`[referee,lineno]`・32 頁）で、`results.tex` を本体に埋め込んだ 1 ファイルの `main.tex`（判断 15）。カバーレターはプレプリントについて「まだ無い・査読中に arXiv（CC BY 4.0）に出して ID を知らせる」と書いた。
- **論文用リポジトリ** `C:/self-resolution-measure`（`mikotomiura/self-resolution-measure`・★ **public**）: main = `0e3c9ed`（README の書き直し）・投稿した版のタグ `submission-2026-09-29` = `75ce1ff`。
- **Zenodo**: 記録 23029603・DOI 10.5281/zenodo.23029603（findable・version `submission-2026-09-29`・zip 1 つ）。token は `C:/zenodo/zenodo_token.txt`（memory `reference_zenodo_token`・公開は都度確認）。
- **arXiv**: 未投稿。自動の endorsement の条件を満たさない（memory `project_arxiv_endorsement_2026`）→ 研究者が知り合いの CS の研究者に個人的な endorsement を頼む（依頼文 `.steering/20260929-p321-paper-submission-prep/endorsement-request-draft.md`・カテゴリ cs.SE）。
- 手元の置き場（repo の外）: `C:/wt/emse-upload/`（EMSE に上げた 6 ファイル＋`title-page.docx`）・`C:/wt/emse-cover-letter.txt`・`C:/wt/emse-upload-form-text.txt`・`C:/wt/emse-preview-2026-09-29.pdf`・研究者の Downloads の `EMSE-S-26-01791.pdf`（EM が組んだ PDF）。⚠️ 査読の対応が済むまで消さない。

## §2 やること

### A. arXiv（endorsement が取れたら）
1. arXiv 用のソースを作る: **今の行間（21 頁）の版**＝タグ `submission-2026-09-29` の `paper/`（`[referee,lineno]` を付けない）。⚠️ `.bbl` の同梱の要否・TeX Live の版・`\input{results}` の扱いは **arXiv の help を一次で確かめてから**（未確認）。pdfLaTeX で組めることは確かめ済み（判断 2 の追記）。
2. 研究者が投稿する（ライセンス **CC BY 4.0**・⚠️ 版ごとに選び、後から変えられない）。
3. 載ったら: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"・EM の "View Submission Correspondence" か編集部への連絡の手段を一次で確かめる）／ Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる）／ README にプレプリントを書く（公開物の規律・GSE に言及しない）。

### B. 査読の結果が来たら
- 判定と査読コメントを読み、対応の方針を研究者と決める（grill）。原稿を直すなら、数値は `results/metrics.json` から生成し直書きしない（前タスク判断 6）・`bash run.sh` と `bash paper/build.sh` exit 0・`/cross-review`。
- 改訂版を出すときも EM の落とし穴（別添のタイトル頁・`.tex` は 1 つ・キーワードはセミコロン・Zenodo のリンクは無効扱い）に注意（memory `reference_springer_editorial_manager`）。
- 再現一式を変えたら、Zenodo は**新しい版**として出す（公開済みのファイルは差し替えられない）。

## §3 気をつけること

- ⚠️ Codex の台帳: 2026-09-29 は、本タスクのブランチで origin/main を merge して和を採った値が **372,458 / 10 回**（`_comment_merge_2026_09_29`）で、上限 300,000 を超えている。⚠️ PR #257 の 1 巡目 +81,661 / +1 回（G-GEAR で実行）は**どのブランチにも記帳されていない**（研究者の指示で Mac 側に渡したが、PR #257 の merge `7ae41eba` には入っていない）→ どちらか一方で 1 回だけ足す（二重に足さない）。merge で `today` が衝突したら和を採る（memory `feedback_codex_budget_is_a_ledger`）。
- ⚠️ 公開物（README・Zenodo の説明・arXiv の要旨・編集部への連絡）は学術的な英語・GSE に言及しない（memory `feedback_public_artifacts_academic_no_gse`）。
