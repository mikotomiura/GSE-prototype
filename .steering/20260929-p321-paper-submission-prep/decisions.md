# 重要な設計判断

★ 2026-09-29 の grill（研究者との対話・3 回・計 12 問）で判断 1–10 を確定した。前提は前タスクの
`.steering/20260928-p321-reanalysis-paper/decisions.md`（判断 1–17）と `.steering/20260928-p321-paper-draft/decisions.md`（判断 1–12）。
⚠️ grill は main checkout ではなく worktree（`C:/wt/p321-submission`）で行った。main checkout は別ターミナルの IME 論文のセッションが使っているため（引き継ぎ §0）。

## 前提: grill の前に一次で確かめた規程（2026-09-29・curl で本文を取得）

| 何 | 出典 | 逐語 |
|---|---|---|
| arXiv の endorsement（2026-01-21 改定） | `https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy` | "As of January 21, 2026, arXiv will no longer accept institutional email addresses (i.e., an email address associated with an academic or research institution) as the sole qualifier of endorsement for new authors." ／ "The first path requires both 1) an institutional email address from an academic/research institution and 2) previous authorship on an existing paper which has been accepted to the arXiv “endorsement domain” they wish to submit to … New submitters who cannot meet these requirements can pursue the second path, which is seeking personal endorsement directly from an established arXiv author in the same endorsement domain." |
| arXiv の endorsement（help） | `https://info.arxiv.org/help/endorsement.html` | "it is best for you to find an endorser who you know personally and is knowledgeable in the subject area of your work." ／ "it is inappropriate to email large numbers of potential endorsers at once" |
| arXiv のライセンス | `https://info.arxiv.org/help/license/index.html` | "The license chosen is irrevocable and cannot be changed." ／ CC BY 4.0・CC BY-SA 4.0・CC BY-NC-SA 4.0・CC BY-NC-ND 4.0・arXiv の非独占ライセンス・CC0 |
| Springer Nature のプレプリント | `https://www.springer.com/gp/editorial-policies/preprint-sharing` | "preprints may be posted at any time during the peer review process. Posting of preprints is not considered prior publication" ／ "Authors should disclose details of preprint posting, including DOI and licensing terms, upon submission of the manuscript or at any other point during consideration" ／ "Authors may choose any license of their choice for the preprint including Creative Commons licenses." |
| Zenodo の GitHub 連携 | `https://support.zenodo.org/help/en-gb/24-github-integration/127-which-github-permissions-do-you-request-and-why` | "Private repositories (no access) We do not have access to your private repositories." |
| Zenodo の DOI の予約 | `https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/` | "In case you want to know the DOI in advance of publication, you can use the method described below to reserve a DOI." ／ "If you delete the draft upload, the reserved DOI is lost." ／（`create-new-upload`）"The DOI will only be registered once the record is published." |
| EMSE の投稿規程 | `https://link.springer.com/journal/10664/submission-guidelines` | ORCID: "Authors are recommended to use their ORCID ID when submitting an article for consideration or acquire an ORCID ID via the submission process." ／ 推薦査読者: "Authors are welcome to suggest suitable reviewers and/or request the exclusion of certain individuals … When suggesting reviewers, authors should make sure they are totally independent and not connected to the work in any way." ／ "All source files you upload in the online submission system will be automatically compiled into a single PDF file to be approved by you at the end of the submission process." ／ カバーレターは "providing transparency on re-use of material and mention any unpublished material … in a cover letter to the Editor"（責任著者の責務の文脈） |

## 判断 1: 研究者が原稿の全文を通読し、指摘を反映する

- **判断日時**: 2026-09-29
- **背景**: 原稿（21 頁）を研究者が通しで読んだ記録は無い（前タスク判断 12 で確認したのは著者情報・Statements・題・LLM の開示の文面・ライセンス・コミットの著者）。LLM の開示は "The author is responsible for the content" と書いている。
- **選択肢**: A: 全文を読む ／ B: 要所（要旨・Introduction・Conclusion・Threats・Statements）だけ ／ C: 読まない
- **採用**: A（研究者の選択）
- **やり方**: 読む前に「主張と根拠の対応表」（1 頁）を渡す。指摘は私が原稿に反映し、`bash run.sh` と `bash paper/build.sh` を回す。反映は研究者が確かめる。
- **影響範囲**: 投稿日（判断 9）。原稿の変更は `/cross-review` の対象（判断 9）。

## 判断 2: pdfLaTeX での組版は scratch に TeX を置いて手元で確かめる

- **判断日時**: 2026-09-29
- **背景**: 前タスク判断 2 の残課題。手元の Tectonic は XeTeX で、EMSE の投稿システムと arXiv の pdfLaTeX とは別物。
- **選択肢**: A: scratch に TeX（TinyTeX など持ち運べるもの）を置く ／ B: 投稿システムの PDF に任せる ／ C: Overleaf
- **採用**: A（研究者の選択）
- **理由**: 原稿を外部サービスに上げず、投稿日より前に差を見つけられる。前タスク判断 2（Tectonic を scratch に置く・システムには入れない）と同じ扱い。
- **影響範囲**: `paper/build.sh` は Tectonic のまま。pdfLaTeX での確認は別の手順として記録する（結果は本ファイルに追記）。
- **見直しタイミング**: pdfLaTeX で差が出たとき（原稿か `build.sh` を直す）。

## 判断 3: arXiv の endorsement は並行して求め、EMSE への投稿を待たせない（前タスク判断 10 を改める）

- **判断日時**: 2026-09-29
- **背景**: 前タスク判断 10 は「arXiv へのプレプリントは投稿と同時」。⚠️ しかし arXiv の規程が 2026-01-21 に変わり、自動の endorsement には所属機関のメール**と**同じ分野での既存の arXiv 論文の**両方**が要る（前提の表）。研究者は ZEN 大学の学生用ドメインのメールを持つが、arXiv に自分の論文は無い → **個人的な endorsement が要る**。
- **選択肢**: A: 並行して求め、投稿は待たせない ／ B: 取れるまで投稿も待つ（判断 10 どおり） ／ C: arXiv はやめる
- **採用**: A（研究者の選択）
- **理由**: Springer Nature の規程で査読中のいつでもプレプリントを出せる（"preprints may be posted at any time during the peer review process"）。endorsement は相手の返事次第で期日が読めないので、投稿を待たせない。
- **endorsement を頼む相手**: 研究者が知っている CS の研究者（arXiv の cs に論文がある人）。依頼文は私が下書きし、研究者が送る（arXiv の help: 個人的に知っていて分野に詳しい人に頼む・大勢に一斉に頼まない）。
- **カテゴリ**: cs.SE（主）。
- ⚠️ **投稿後に arXiv に出したら**、Springer の規程どおり DOI（arXiv ID）とライセンスを編集部に申告する。
- **影響範囲**: 前タスク判断 10（本判断で置き換える）・カバーレター（投稿時点ではプレプリントなしと書く）。

## 判断 4: 再現一式は Zenodo の手動アップロードで DOI を予約し、投稿日に GitHub の public 化と Zenodo の公開を行う

- **判断日時**: 2026-09-29
- **背景**: 原稿の Data availability の DOI が仮置き（`paper/main.tex:386` "[archived copy with DOI to be added]"）。Zenodo の GitHub 連携は private のリポジトリを扱えない（前提の表）。⚠️ 原稿の Method は凍結の順序の根拠を "the commit history records the order" と書いている → 読者が確かめるには**履歴ごと**公開する必要がある。
- **選択肢**: A: Zenodo で DOI を予約 → 原稿に記入 → 投稿日に GitHub を public にし、同じコミットの zip を Zenodo で公開 ／ B: 先に public にして GitHub 連携で DOI（公開が投稿より前になる） ／ C: GitHub は private のまま Zenodo に zip だけ（Method の書き方も直す）
- **採用**: A（研究者の選択）
- **Zenodo の操作**: 研究者が token を提供し、自動での操作を許可した（2026-09-29・逐語「zenodo の token あるからそこで自動でやっていいよ」）。
  - ★ **今日**: 下書きの作成と DOI の予約まで（下書きは消せる）。token はプロセス内で読むだけにし、画面・ログ・リポジトリ・Codex に出さない。
  - ⚠️ **投稿日**: GitHub の public 化と Zenodo の公開は、どちらも取り消しにくい（Zenodo は公開後にファイルを差し替えられない）ので、その時点で研究者にもう一度確かめてから行う。
- ⚠️ **トレードオフ**: GitHub を public にすると、`4a81a43` より前のコミットの著者（別のメールアドレス）も公開される（前タスク判断 12 で研究者が承知・履歴は書き換えない）。
- **影響範囲**: `paper/main.tex` の Data availability・README（DOI・原稿のライセンス）・投稿日の手順。

## 判断 5: 原稿のライセンス = CC BY 4.0（arXiv のプレプリントとリポジトリの `paper/`）

- **判断日時**: 2026-09-29
- **背景**: README は逐語 "The manuscript (`paper/main.tex`, `paper/refs.bib`) is **not** covered by either licence; its terms will be set when it is submitted and posted as a preprint."（前タスク判断 12: 投稿時に決める）。arXiv のライセンスは後から変えられない。Springer はプレプリントにどのライセンスでもよいと明記。
- **選択肢**: A: CC BY 4.0 ／ B: arXiv の非独占ライセンス ／ C: CC BY-NC-ND 4.0
- **採用**: A（研究者の選択）
- **理由**: データ・文書（前タスク判断 11）と揃う。採択後に出版社へ著作権を譲渡しても、プレプリント版は CC BY のまま残る。
- ⚠️ **範囲**: 原稿の文章と `refs.bib`。テンプレートのクラスと bst（`sn-jnl.cls`・`sn-basic.bst`）はリポジトリに入れていない（前タスク判断 5）ので対象外。引用した第三者の文は元の条件のまま（README の既存の書き方と同じ）。
- **影響範囲**: README の Licence 節・Zenodo の下書きのライセンス欄。

## 判断 6: 論文の所属は「所属なし・Hiroshima, Japan」のまま

- **判断日時**: 2026-09-29
- **背景**: 研究者は ZEN 大学の学生（学生用ドメインのメールを持つ）。前タスク判断 12 で所属なし（都市と国だけ）にしていた。
- **採用**: 今のまま（研究者の選択）。この研究は大学とは別に行ったものとして扱う。
- **影響範囲**: なし（原稿・Zenodo の著者情報は所属なし）。arXiv のアカウントのメールは、endorsement の経路（判断 3）では自動の条件に効かない。

## 判断 7: ORCID = 0009-0000-4196-0508 を原稿と Zenodo に入れる

- **判断日時**: 2026-09-29
- **背景**: EMSE は ORCID の使用を推奨（前提の表）。研究者は ORCID を持っている。
- **一次で確かめたこと**: 検査数字（ISO 7064 MOD 11-2）が一致。`https://pub.orcid.org/v3.0/0009-0000-4196-0508/person` の氏名 = Mikoto Miura。
- **影響範囲**: `paper/main.tex` の著者情報（`sn-jnl` の書き方に合わせる）・Zenodo の creators・投稿システム。

## 判断 8: 推薦査読者は挙げない

- **判断日時**: 2026-09-29
- **採用**: 挙げない（研究者の選択）。EMSE では任意で、編集者に任せる。

## 判断 9: 投稿日は準備が済み次第（日付を決めない）

- **判断日時**: 2026-09-29
- **採用**: 研究者の選択。順序は 通読の反映 → pdfLaTeX → 原稿の変更への `/cross-review` → カバーレター → 投稿。
- ⚠️ **Codex の予算**: 今日（2026-09-29）の合算は約 265k / 300k（origin/main 109,931 ＋ PR #257 の Codex 1 巡目 81,661（`C:/wt/pr257-codex-r1/`・どのブランチにも未記帳）＋ `docs/ai-fatigue-db-readable-gaps` の未コミット 73,666）。→ 原稿を直した後の Codex は**明日以降**に回す。

## 判断 10: カバーレターは私が下書きし、研究者が確かめる

- **判断日時**: 2026-09-29
- **採用**: 研究者の選択。1 頁程度（研究の要点・既存の公開データの再解析であること・データとコードの公開と DOI・投稿時点でプレプリントは無いこと（判断 3）・LLM の使用は本文 Sect. 5.5 に開示済み）。
- ⚠️ 公開物と同じく、学術的な英語で書き、GSE に言及しない（memory `feedback_public_artifacts_academic_no_gse`）。
