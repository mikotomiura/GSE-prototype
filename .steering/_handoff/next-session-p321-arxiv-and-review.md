# 次セッション — 2 本目の論文（EMSE-D-26-01273）の arXiv と、査読への対応

> 作成: 2026-09-29（EMSE への投稿の後）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す（EMSE の状態・arXiv・Zenodo・GitHub）。
> 一次の記録: `.steering/20260929-p321-paper-submission-prep/decisions.md`（判断 1–15）・`submission-day-steps.md`。

## §0 打ち込む用

```
git fetch origin してから git show origin/main:.steering/_handoff/next-session-p321-arxiv-and-review.md を読んで、§2 A（arXiv）を進めてください。研究者の指示（2026-09-29）: 「Draft までは Claude が進め、後半の publish から研究者にお願いする」＝ arXiv の投稿画面で組版の Preview を確かめ、メタデータを入れた下書き（incomplete）まで私が作る。ライセンスの確定と最後の Submit は研究者。（⚠️ origin/main に無ければ、前セッションのブランチ docs/p321-paper-submission-prep の PR #267 がまだ merge されていない → 先に確かめる）。
⚠️ main checkout（C:/GSE-prototype）は別ターミナルの IME 論文のセッションが使っているかもしれない。git status を見て、使っていれば GSE 側の作業は git worktree で切る。
Skill: git-workflow・verify-before-claiming・subagent-delegation・citation-ssot（原稿を直すとき）・browser-verification（Chrome を使うとき）。
応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。取り消しにくい操作（arXiv への投稿・Zenodo の新しい版の公開・EMSE への返信）はその場で研究者に確かめる。
```

## §1 状態（2026-09-29 23:20 JST に測った値）

- **EMSE**: 原稿番号 **EMSE-D-26-01273**・2026-09-29 投稿・状態 Submitted（Editorial Manager https://www.editorialmanager.com/emse ・研究者のアカウントは ORCID 0009-0000-4196-0508 に結び付け済み）。投稿した版は行間と行番号つき（`[referee,lineno]`・32 頁）で、`results.tex` を本体に埋め込んだ 1 ファイルの `main.tex`（判断 15）。カバーレターはプレプリントについて「まだ無い・査読中に arXiv（CC BY 4.0）に出して ID を知らせる」と書いた。
- **論文用リポジトリ** `C:/self-resolution-measure`（`mikotomiura/self-resolution-measure`・★ **public**）: main = `728e81c`（README の書き直しと、完了時レビューでの修正）・投稿した版のタグ `submission-2026-09-29` = `75ce1ff`。
- **Zenodo**: 記録 23029603・DOI 10.5281/zenodo.23029603（findable・version `submission-2026-09-29`・zip 1 つ）。token は `C:/zenodo/zenodo_token.txt`（memory `reference_zenodo_token`・公開は都度確認）。
- **arXiv**: 未投稿。自動の endorsement の条件を満たさない（memory `project_arxiv_endorsement_2026`）→ 研究者が知り合いの CS の研究者に個人的な endorsement を頼む（依頼文 `.steering/20260929-p321-paper-submission-prep/endorsement-request-draft.md`・カテゴリ cs.SE）。
- 手元の置き場（repo の外）: `C:/wt/emse-upload/`（EMSE に上げた 6 ファイル＋`title-page.docx`）・`C:/wt/emse-cover-letter.txt`・`C:/wt/emse-upload-form-text.txt`・`C:/wt/emse-preview-2026-09-29.pdf`・研究者の Downloads の `EMSE-S-26-01791.pdf`（EM が組んだ PDF）。⚠️ 査読の対応が済むまで消さない。

## §2 やること

### A. arXiv（★ 次のセッションの主題・研究者の指示で「Draft まで Claude・publish から研究者」）

★ 分担:

| 段 | 誰 | 何 |
|---|---|---|
| A-0 | 私 | arXiv の規程を一次で確かめ直す（下の「確かめ済みの規程」に無いもの＝endorsement が無い状態で下書きをどこまで作れるか・メタデータの欄の形・ライセンスの選択肢の表示） |
| A-1 | 私 | ソースの一式を scratch で作り、pdfLaTeX で組む（下の 1） |
| A-2 | ⚠️ 研究者 | arXiv にログインする（⚠️ パスワードの入力とアカウントの作成は私が行えない）→ Chrome の**このセッションのタブグループ**にタブを入れてもらう（前セッションで、グループの最後のタブが閉じられるとグループごと消えると分かった → 空のタブを 1 つ残す） |
| A-3 | 私（研究者の承認の後） | 新しい投稿を始め、カテゴリ cs.SE・ファイルの上げ込み・arXiv 側の組版のログと Preview の確認・メタデータ（題・著者・要旨・コメント）の入力まで。⚠️ フォームへの入力・ファイルの上げ込みは、その都度研究者に確かめてから行う |
| A-4 | ⚠️ 研究者 | ライセンス（CC BY 4.0）の確定・最後の Submit（⚠️ ライセンスは版ごとに選び後から変えられない・Submit は公開の手続きに入る）。⚠️ endorsement が要る段で止まったら、依頼文（`endorsement-request-draft.md`）で知り合いの CS の研究者に頼む |

★ **確かめ済みの規程**（2026-09-29・`https://info.arxiv.org/help/submit_tex.html` ほか・逐語）: "We do not have your style files or macros"（→ cls と bst は同梱が要る）／ "Do not submit in double-spaced "referee" mode"（→ 21 頁の版）／ "Include .bib or .bbl files if you use BibTeX/Biber" ／ "arXiv offers currently TeX Live 2023 and 2025 (the default)" ／ 投稿後・公開前は "Unsubmit" で incomplete に戻して直せる（`https://info.arxiv.org/help/submit/index.html`）／ ファイルを上げると arXiv 側で組まれ、ログと PDF の Preview が見られる。

1. arXiv 用のソースを作る: **今の行間（21 頁）の版**＝タグ `submission-2026-09-29` の `paper/`（`[referee,lineno]` を付けない）。⚠️ タグには `sn-jnl.cls`・`sn-basic.bst` が**入っていない**（再配布しない方針・前タスク判断 5）→ `paper/build.sh` が公式 zip から SHA-256 を照合して取り出したものを使う。⚠️ `sn-jnl.cls` の冒頭は "This file may only be distributed together with a copy of the LaTeX base system." と書く → arXiv はソースを公開するので、**同梱してよいか（arXiv の TeX Live に入っているか）を arXiv の help で一次で確かめ、研究者に判断してもらう**。★ `.bbl` は同梱する（help "Include .bib or .bbl files"・natbib ＋ BibTeX なので biblatex の版の問題は当たらない）。arXiv の既定は TeX Live 2025（手元の TinyTeX は 2026）→ **arXiv 側の Preview で必ず確かめる**。⚠️ `results.tex` を別ファイルのまま上げてよいか（2 つ目の `.tex` を最上位のファイルと取り違えないか）は未確認 → 迷ったら EM と同じく本体に埋め込む（判断 15・PDF が一致することは確認済み）。pdfLaTeX で組めることは、タグの版で確かめ済み（判断 12・判断 13 の C）。
★ endorsement が取れないままなら、代わりに Research Square にプレプリントを載せる道がある（投稿後のメール・RSID rs-1120754・endorsement 不要・判断 16）→ 研究者が決め、載せたら編集部に知らせる。
2. 下書きの入力（A-3）と送信（A-4・研究者）: ライセンス **CC BY 4.0**（⚠️ 版ごとに選び、後から変えられない）。要旨の欄は R マクロを数値に置き換えた平文が要る → `C:/wt/emse-upload-form-text.txt` の要旨を使う（数値は PDF と照合済み）。コメント欄の案: "21 pages, 5 tables. Submitted to Empirical Software Engineering. Replication package: https://doi.org/10.5281/zenodo.23029603"（⚠️ 研究者に確かめる）。
3. 載ったら: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"・EM の "View Submission Correspondence" か編集部への連絡の手段を一次で確かめる）／ Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる）／ README にプレプリントを書く（公開物の規律・GSE に言及しない）。

### B. 査読の結果が来たら
- 判定と査読コメントを読み、対応の方針を研究者と決める（grill）。原稿を直すなら、数値は `results/metrics.json` から生成し直書きしない（前タスク判断 6）・`bash run.sh` と `bash paper/build.sh` exit 0・`/cross-review`。
- 改訂版を出すときも EM の落とし穴（別添のタイトル頁・`.tex` は 1 つ・キーワードはセミコロン・Zenodo のリンクは無効扱い）に注意（memory `reference_springer_editorial_manager`）。
- 再現一式を変えたら、Zenodo は**新しい版**として出す（公開済みのファイルは差し替えられない）。⚠️ 波及: (a) 新しい版には新しい DOI が付く → 原稿の Data availability・README のバッジと BibTeX・カバーレターが名指ししている 23029603 を、新しい版の DOI か concept DOI（全版をまとめる DOI・記録のページで一次で確かめる）に改める ／ (b) 解析を変えたら `NOTES.md` の Deviations に追記し、原稿 §5.1 の "Seven later changes … none changed a reported value" の件数と文を更新する（凍結の主張を守る要）／ (c) 改訂版にも新しいタグを付け、arXiv にも新しい版を出す（ライセンスは版ごと）／ (d) 査読への返答書（point-by-point）と EM の改訂期限を記録する。

## §3 気をつけること

- ⚠️ Codex の台帳: 2026-09-29 は、本タスクのブランチで origin/main を merge して和を採った値が **372,458 / 10 回**（`_comment_merge_2026_09_29`）、その後の完了時のレビュー 1 回を足して **395,426 / 11 回**で、上限 300,000 を超えている（記帳漏れの PR #257 の分を足すと実合算は **477,087 / 12 回**）。⚠️ PR #257 の 1 巡目 +81,661 / +1 回（G-GEAR で実行）は**どのブランチにも記帳されていない**（研究者の指示で Mac 側に渡したが、PR #257 の merge `7ae41eba` には入っていない）→ どちらか一方で 1 回だけ足す（二重に足さない）。merge で `today` が衝突したら和を採る（memory `feedback_codex_budget_is_a_ledger`）。
- ⚠️ 公開物（README・Zenodo の説明・arXiv の要旨・編集部への連絡）は学術的な英語・GSE に言及しない（memory `feedback_public_artifacts_academic_no_gse`）。
