# 重要な設計判断

★ 2026-09-29 の grill（研究者との対話・3 回・計 12 問）で判断 1–10 を確定した。前提は前タスクの
`.steering/20260928-p321-reanalysis-paper/decisions.md`（判断 1–17）と `.steering/20260928-p321-paper-draft/decisions.md`（判断 1–12）。
⚠️ grill は main checkout ではなく worktree（`C:/wt/p321-submission`）で行った。main checkout は別ターミナルの IME 論文のセッションが使っているため（引き継ぎ §0）。

## 前提: grill の前に一次で確かめた規程（2026-09-29・curl で本文を取得）

| 何 | 出典 | 逐語 |
|---|---|---|
| arXiv の endorsement（2026-01-21 改定） | `https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy` | "As of January 21, 2026, arXiv will no longer accept institutional email addresses (i.e., an email address associated with an academic or research institution) as the sole qualifier of endorsement for new authors." ／ "The first path requires both 1) an institutional email address from an academic/research institution and 2) previous authorship on an existing paper which has been accepted to the arXiv “endorsement domain” * they wish to submit to … New submitters who cannot meet these requirements can pursue the second path, which is seeking personal endorsement directly from an established arXiv author in the same endorsement domain." |
| arXiv の endorsement（help） | `https://info.arxiv.org/help/endorsement.html` | "it is best for you to find an endorser who you know personally and is knowledgeable in the subject area of your work." ／ "it is inappropriate to email large numbers of potential endorsers at once" |
| arXiv のライセンス | `https://info.arxiv.org/help/license/index.html` | "Please note that different versions of the work can have different licenses." ／ "The license chosen is irrevocable and cannot be changed." ／ "the license chosen for each version is irrevocable" ／ CC BY 4.0・CC BY-SA 4.0・CC BY-NC-SA 4.0・CC BY-NC-ND 4.0・arXiv の非独占ライセンス・CC0 |
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

### 判断 1 の追記: 研究者の通読の結果（2026-09-29）

- 研究者の返答（逐語）: 「pdfを見た感じ, 特に表記などで気になった個所はない」。読んだ版は `e1e527b` の `paper/main.pdf`（21 頁・`reading-guide.md` を添えた）。
- → **原稿は変えない。** ⚠️ 返答の範囲は研究者の言葉のとおり記録する（`reading-guide.md` の「特に見てほしいところ」5 点を個別に確かめたかは、返答からは分からない）。

## 判断 2: pdfLaTeX での組版は scratch に TeX を置いて手元で確かめる

- **判断日時**: 2026-09-29
- **背景**: 前タスク判断 2 の残課題。手元の Tectonic は XeTeX で、EMSE の投稿システムと arXiv の pdfLaTeX とは別物。
- **選択肢**: A: scratch に TeX（TinyTeX など持ち運べるもの）を置く ／ B: 投稿システムの PDF に任せる ／ C: Overleaf
- **採用**: A（研究者の選択）
- **理由**: 原稿を外部サービスに上げず、投稿日より前に差を見つけられる。前タスク判断 2（Tectonic を scratch に置く・システムには入れない）と同じ扱い。
- **影響範囲**: `paper/build.sh` は Tectonic のまま。pdfLaTeX での確認は別の手順として記録する（結果は本ファイルに追記）。
- **見直しタイミング**: pdfLaTeX で差が出たとき（原稿か `build.sh` を直す）。

### 判断 2 の追記: pdfLaTeX で組んだ結果（2026-09-29・論文用リポジトリ `e1e527b`）

- **道具**: TinyTeX v2026.09（`TinyTeX-v2026.09.zip`・246,897,183 B・SHA-256 `e82d8b78fcf5740639f10ac8518f0c83c9202830e6bba364c70104601c12c6be` = GitHub の release が示す digest と一致）を scratch に展開。pdfTeX 3.141592653-2.6-1.40.29（TeX Live 2026）。⚠️ 既定の取得先 `tlnet.yihui.org` は "not verified: pubkey missing" だったので、scratch の TinyTeX の取得先を CTAN 公式のミラー（`mirror.ctan.org`）に替えた（こちらも Windows の TinyTeX に gpg が無く署名は未検証）。足したパッケージは `ncctools`（`manyfoot.sty`）と `xurl` の 2 つ。
- **手順**: `paper/` の 5 ファイル（`main.tex`・`refs.bib`・`results.tex`・`sn-jnl.cls`・`sn-basic.bst`）を scratch に複製し、`pdflatex → bibtex → pdflatex ×3`（3 回目の後に "Label(s) may have changed" が出たので 4 回目で収束）。
- **結果**: すべて exit 0。**21 頁**（Tectonic と同じ）。未定義の参照・引用 0 ／ Overfull `\hbox` 0 ／ Underfull `\hbox` 0 ／ Missing character 0 ／ フォント 30 種すべて埋め込み。
- 残る警告: Overfull `\vbox` 1 件（1.9pt・`\output` 中。★ Tectonic でも HEAD の原稿で同じ 1 件（2.05pt）が出る＝今回の変更とは無関係）／ hyperref のしおりの階層の飛び 8 件（Statements の `\bmhead`）／ `rsfs` の寸法の代用 4 件（`mathrsfs` を読み込んでいるが使っていない）。
- ⚠️ 頁割りは XeTeX と一部ずれる（21 頁中 6 頁で頁の書き出しと終わりが一致・他は数行ずれる）。組版エンジンの字幅の違いで、内容の違いではない（本文の抽出で語の並びの違いは空白の入り方だけ）。
- → **pdfLaTeX で組めない原因は見当たらない。** 投稿システムが組んだ PDF は、投稿時に研究者が承認する前に頁数と表の収まりを見る。

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

### 判断 4 の追記: Zenodo の下書きと DOI の予約（2026-09-29）

- token が効くかを読み取りだけで確かめた（`GET /api/deposit/depositions` = 200・本番の zenodo.org・研究者の既存の公開済み記録 3 件には触れていない）。
- **下書き**: deposition `23029603`・状態 `unsubmitted`（未公開）・**予約した DOI = `10.5281/zenodo.23029603`**。⚠️ Zenodo の規程では DOI は公開した時点で登録される（"The DOI will only be registered once the record is published."）→ **投稿日は Zenodo の公開を先に行い、DOI が解決することを確かめてから EMSE に投稿する**。⚠️ 下書きを消すと予約した DOI も失われる。
- **メタデータ**（研究者の既存の記録 `22735437`・`22733449` に揃えた）: creators = "Miura, Mikoto"・affiliation "Independent Researcher"・ORCID `0009-0000-4196-0508` ／ license `cc-by-4.0` ／ access `open` ／ related_identifiers = `isSupplementTo` `https://github.com/mikotomiura/self-resolution-measure` ／ keywords は原稿と同じ 6 語 ／ 説明は学術的な英語（GSE への言及なし・grep 0 件）。
- ★ **資源の種類 = dataset**（私の選択）: 中身が転記データ・結果・凍結した設定・解析コード・原稿の TeX で、原稿の Data availability が指す先だから。⚠️ Zenodo のメタデータは公開後も直せる（ファイルは直せない）。研究者が software などを望めば投稿日までに直す。
- **原稿**: 論文用リポジトリ `e1e527b` —— Data availability の仮置きを DOI に置き換え、開発用リポジトリを「凍結と解析の順序を記録するコミット履歴の置き場所」として名指した。README: 原稿を CC BY 4.0 に（判断 5）・DOI を記載。`bash run.sh` exit 0・`bash paper/build.sh` exit 0（21 頁）。⚠️ まだ push していない（レビューの後）。

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
- **影響範囲**: 原稿は都市と国だけ（`\affil` に所属を書かない）。Zenodo の所属欄は、研究者の既存の Zenodo の記録 2 件に揃えて "Independent Researcher"（所属なしの書き方）にした（2026-09-29 に研究者が「このまま」と確認）。arXiv のアカウントのメールは、endorsement の経路（判断 3）では自動の条件に効かない。

## 判断 7: ORCID = 0009-0000-4196-0508 を原稿と Zenodo に入れる

- **判断日時**: 2026-09-29
- **背景**: EMSE は ORCID の使用を推奨（前提の表）。研究者は ORCID を持っている。
- **一次で確かめたこと**: 検査数字（ISO 7064 MOD 11-2）が一致。`https://pub.orcid.org/v3.0/0009-0000-4196-0508/person` の氏名 = Mikoto Miura。
- **影響範囲**: `paper/main.tex` の著者情報（`sn-jnl` の書き方に合わせる）・Zenodo の creators・投稿システム。

### 判断 7 の追記: 原稿の本文には ORCID を入れない（2026-09-29・テンプレートを一次で確かめた結果）

- ⚠️ grill では「原稿・Zenodo の著者情報に入れる」と聞いていた。
- **一次**: `sn-jnl.cls` の定義は `\gdef\orcidlogo{\includegraphics{Orcidlogo.eps}}`・`\gdef\orcid#1{\href{#1}{\orcidlogo}}`。★ `Orcidlogo.eps` は公式 zip（前タスク判断 1）に**入っていない**（zip の中身は `sn-jnl.cls`・`sn-article.tex`・`bst/` 9 本・`empty.eps`・`fig.eps`・`sn-article.pdf`・`sn-bibliography.bib`・`user-manual.pdf`）。見本の `sn-article.tex` と手引き `user-manual.pdf`（14 頁）には ORCID の記述が 1 つも無い。⚠️ Tectonic は EPS を扱えない（前タスク判断 2）。
- **採用**: ORCID は**投稿システムと Zenodo**（下書きの creators に入れ済み）に入れ、原稿の本文には入れない。EMSE の規程も ORCID を「投稿の際に使う」ものとして書いている（前提の表）。
- **見直しタイミング**: 採択後の組版で出版社が求めたとき、または研究者が本文への記載を求めたとき。

### 判断 7 の追記 2: 上の追記を取り消し、ORCID をタイトル頁に入れる（2026-09-29・code-reviewer MEDIUM）

- ⚠️★ **上の追記は EMSE の規程を 1 か所しか読んでいなかった**（`verify-before-claiming` ルール 7 の違反）。規程の Title Page の節（逐語）: "Please make sure your title page contains the following information. … Author information … If available, the 16-digit ORCID of the author(s)"。→ 規程は ORCID を**タイトル頁に載せる**よう求めている。
- **採用**: タイトル頁の「Corresponding author(s). E-mail(s): …」の行に `ORCID: https://orcid.org/0009-0000-4196-0508` を文字で続ける（論文用リポジトリ `02380c5`・`\g@addto@macro\corrauthemail{…}`）。クラスの `\orcid` は同梱されない EPS を読むので使わない（上の追記の一次はそのまま正しい）。grill の答え（原稿・Zenodo に入れる）に戻った。
- ⚠️ クラスの内部マクロ（`\corrauthemail`）に足す形。手引きは "non-standard packages and macros are frequent causes of error" と注意しているので、投稿システムが組んだ PDF でタイトル頁の ORCID を確かめる（`submission-day-steps.md` 手順 4）。Tectonic・pdfLaTeX の両方で組めることは確かめた。

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

## 判断 11: `/cross-review` 1 巡目の裁定と、投稿する版の行間（2026-09-29）

- **レビュー**: Claude 系統 = code-reviewer（論文用リポジトリ `4a81a43..e1e527b` ＋ 本ディレクトリ 8 ファイル）と security-checker（論文用リポジトリの**全 11 コミット**・公開前提 ＋ `zen.py`・Zenodo のメタデータ）。Codex 系統 = 前タスク判断 9 の方法（GSE の worktree に `git fetch` してラッパーを範囲指定）で 2 回: ① 原稿 `4a81a43..e1e527b -- paper/main.tex README.md` ② 本ディレクトリの 5 ファイル。★ 入れ子を避けるため `cross-reviewer` エージェントは使わず、メインから起動した。**CRITICAL は 0 件**。
- **Codex の予算**: 研究者の許可（逐語「Codexは必要であれば予算引き上げしていいよ」）で `daily_token_budget` を一時的に 450000 に上げた（台帳の `_comment_2026_09_29_temporary_raise`）。実消費 ① 20,864 ② 28,014（本ブランチの台帳 109,931 → 158,809 / 4 回）。同日の合算は約 314,136 / 6 回（他の 2 件は判断 9 のとおり）。
- ★ **採用（両系統が一致）**:
  1. カバーレターと Zenodo の説明が凍結を言い過ぎていた（"frozen before the results were produced"）—— code-reviewer HIGH・Codex P2。原稿 §5.1 の主語と限定（"committed … before the analysis code produced the results reported here"・既知だった推定値の開示）に揃えた。Zenodo の下書きは説明だけを差し替えた（DOI は不変・未公開のまま）。
  2. endorsement の依頼を投稿日より前に送ると DOI がまだ解決しない —— code-reviewer MEDIUM・Codex P2 → 下書きに注意書きと書き換えの指示。
  3. Zenodo に上げる zip の検証が無い —— code-reviewer MEDIUM・Codex P2（原稿の差分でも「アーカイブの中身との対応」を指摘）→ 手順書 2.2 に「展開して `git ls-tree` と照合・D1 を置いて `run.sh` exit 0」。
  4. 「履歴が凍結と解析の順序を記録する」の言い方 —— Codex（原稿・低）・code-reviewer MEDIUM（README は zip に入ると履歴を失う）・LOW（参照先は 5.1 節）→ 原稿と README を「解析の設定が、解析のコードが結果を出す前にコミットされたことを記録する」に改め、README は開発用リポジトリの URL を名指しし、5.1 節に label を付けて参照した（論文用リポジトリ `02380c5`）。
- ★ **採用（片方だけ）**:
  - code-reviewer MEDIUM: 「すべての結果を再現一式から生成」に D1 のデータを取得してからの条件を付けた ／ 判断 6 の所属の記述と Zenodo の不一致 → 判断 6 を直し、研究者が "Independent Researcher" を「このまま」と確認 ／ ORCID → 判断 7 の追記 2 ／ `main.bbl` の出どころ → 手順書 3。
  - code-reviewer LOW: arXiv のライセンスは版ごと（前提の表・手順書 5）／ arXiv ブログの引用の脚注の印 ／ Zenodo の説明を "Table 4 and three rows of Table 5" に ／ カバーレター "comes from a study published in this journal" ／ 手順 1 と 2 を続けて行う ／ EMSE と arXiv にも 🔒。
  - Codex P1: 公開前に全履歴を検査すること・`--tags` を使わないこと → security-checker が全 11 コミットを検査済み（手順書 0.2 に記録し、それ以後のコミットは差分を検査する）・タグだけを push（手順書 0.3）。
  - security-checker LOW 1: `zen.py` の token がリダイレクトで転送先に渡りうる → `add_unredirected_header` に変えた（scratch のスクリプト・リポジトリ外）。
  - security-checker（セキュリティ外）: `4aab7f0` の「手で・2 人が独立に転記」という誤った記述が公開される履歴に残る → `NOTES.md` の D2 transcription の節に、誤りと `ae39be6` での訂正（値は不変・CSV は改名だけで 0 行の変更）を記録した（`02380c5`）。⚠️ 原稿の "Seven later changes" は解析の逸脱の数なので、`Deviations` には入れていない。⚠️ **出どころは `4aab7f0` だけではなかった**（2 巡目の code-reviewer・判断 12 で訂正）。
- **採用しない**:
  - code-reviewer LOW 15（requirement.md の ORCID の記述が古い）→ 判断 7 の追記 2 で原稿に入れたので、requirement.md は正しいまま。
  - security-checker LOW 2（履歴に旧ディレクトリ名 `data/p434` が残る）→ 受け入れる。消すには履歴の書き換えが要り、原稿が根拠にする凍結の順序の記録と矛盾する（`NOTES.md` は旧名を別プロジェクトの引用キーと説明しており、プロジェクト名は出ない）。
- **情報**: security-checker が見つけた到達不能なコミット `090be99`・`605103e` は、2026-09-29 13:02 に私が論文用リポジトリで余計に行った `git stash` → `git stash pop` の跡（ローカルだけ・どの ref にも無いので push されない・作業ツリーは元どおりと確認済み）。GitHub 側（security-checker は読んでいない）は `gh api` で確かめた: ブランチ main だけ・タグ・Release・PR・Issue・Actions の実行がいずれも 0。
- ★ **投稿する版の行間**（`.bbl` を調べる途中で見つけた・研究者の選択）: テンプレートの手引き（逐語）"For the peer review and editorial stages you are requested to enable double-line spacing by using the [referee] option"（EMSE の規程自体には行間の指定が無い）。→ **投稿する版だけ `[referee,lineno]`**（pdfLaTeX で 32 頁・Overfull `\hbox` 0・未定義 0）。リポジトリと arXiv の原稿は今の行間（21 頁）のまま。投稿用の版は投稿日に scratch で作る（手順書 3）。

## 判断 12: `/cross-review` 2 巡目の裁定（2026-09-29）

- **範囲**: 1 巡目で足した規則の境界条件（memory `project_cross_review_two_rounds`）。Codex 2 回（① 論文用リポジトリ `e1e527b..02380c5 -- paper/main.tex README.md NOTES.md` ② 本ディレクトリ `e40940e2..017a4ee9` の 4 ファイル）＋ code-reviewer。**CRITICAL は 0 件**。
- **Codex の予算**: 実消費 ① 22,169 ② 25,536（本ブランチの台帳 158,809 → 206,514 / 6 回）。同日の合算は約 361,841 / 8 回（引き上げた上限 450,000 の内）。
- ★ **採用（両系統が一致）**:
  1. ⚠️ **手順書の並び順**（code-reviewer HIGH・Codex P2）: 取り消せる検証（zip の検証・投稿用の原稿の組版・投稿システムの PDF の確認）が、取り消しにくい操作（GitHub の public 化）の後にあった。さらに「public 化と Zenodo の公開を間を置かずに」という自分で足した規則を、手順どおりに進めると必ず破る形だった。→ A（確定・履歴の検査・タグは手元だけ）→ B（zip の作成・中身の照合・Zenodo の下書きへのアップロード・研究者の確認）→ C（投稿用の原稿・投稿システムの PDF を承認せずに見る）→ D（push と public 化）→ E（Zenodo の公開）→ F（EMSE）→ G（arXiv）に組み直した。
  2. 履歴が示せる範囲（Codex ① P2・code-reviewer MEDIUM）: 凍結のコミット `416a0fc` は設定とデータだけで、解析のコードと結果は `834f16a` で入った（`git show --stat` で確認）。⚠️ 設定はその後も `ae39be6`・`098b01a` で変わった（`git log -- config.json`）。→ Data availability・README・カバーレター・Zenodo の説明を「設定は解析のコードと結果より**先に最初に**コミットされ、その後の変更は記録してある」に揃えた（論文用リポジトリ `75ce1ff`・Zenodo の下書きは説明だけ差し替え・DOI は不変）。原稿 §5.1 の文は変えていない（"Seven later changes … are logged" の限定を既に持つ）。
- ★ **採用（片方だけ）**:
  - code-reviewer MEDIUM: `NOTES.md` の訂正文が誤りの出どころを取り違えていた。`git log -S` で確かめると "transcribed by hand"（`DATA.md`）は**凍結のコミット `416a0fc`** から、`ENV.md` の "by hand" と `NOTES.md` の "coder B independently" は `834f16a` から、"Two people transcribed independently" だけが `4aab7f0`。→ 3 つのコミットごとに挙げ直した（`75ce1ff`）。判断 11 の該当行にも訂正を注記した。
  - Codex ② P2: 履歴の検査は**コミットごとに**（手順書 A.2）。
  - Codex ② P3: ⚠️★ `decisions.md` 判断 6 の `\affil` が **BEL（0x07）** になっていた（heredoc 経由の Python で `\a` が制御文字に変わった・memory `feedback_backslash_via_bash_heredoc` と同じ型）→ Write で作ったスクリプトで直し、本ディレクトリと論文用リポジトリの全テキストに制御文字が無いことを走査で確かめた。
  - code-reviewer LOW: ORCID の行は責任著者の `\email` の直後に置く必要がある（前に置く・`\email` を消すと区切れない・消える）→ `main.tex` のコメントに書いた ／ zip の照合は名前だけでなく blob ID で・`core.autocrlf=false` で作る・`build.sh` には Tectonic が要る（手順書 B）／ 依頼文の日本語版の注意書きを `[...]` の形に・添付 PDF の中のリンクもまだ開けない旨（`endorsement-request-draft.md`）／ public 化の後の実物の目視を戻した（手順書 D.4）。
  - Codex ① P2（ORCID がクラスの内部マクロに頼る）: 通常の版と投稿する版（`[referee,lineno]`）の両方の PDF で、タイトル頁に ORCID が 1 回・リンク先が `https://orcid.org/0009-0000-4196-0508` であることを確かめた。投稿システムが組んだ PDF でも見る（手順書 C.4）。
- ★ 論文用リポジトリ `75ce1ff`: `bash run.sh` exit 0・`bash paper/build.sh` exit 0・pdfLaTeX で通常の版 21 頁／投稿する版 32 頁（どちらも Overfull `\hbox` 0・未定義 0）。
- **3 巡目は回さない**: 2 巡目の指摘はすべて一次で確かめて直し、残る論点は投稿日に手順書のとおりに実物で確かめる段（zip の照合・投稿システムの PDF）へ収束した（memory `project_cross_review_two_rounds`「打ち切りは残る論点が別の段へ収束したから」）。→ Codex の上限を 300,000 に戻す。

## 判断 13: 投稿日の実施記録（2026-09-29・研究者の選択「今日投稿まで進む」）

- **A（確定）**: 論文用リポジトリ `75ce1ff`（clean・`run.sh` / `build.sh` exit 0）。security-checker の検査より後の 2 コミット（`02380c5`・`75ce1ff`）を**コミットごとに**検査した（差分とメッセージに秘密情報・ローカルパス・GSE への言及 0 件・著者とコミッタは Mikoto Miura だけ）。GitHub 側: ブランチ main だけ・タグ 0・Release 0・PR 0。注釈付きタグ `submission-2026-09-29` → `75ce1ff`（tagger Mikoto Miura）を手元で付けた。
- **B（zip）**: `git -c core.autocrlf=false archive --format=zip --prefix=self-resolution-measure/ submission-2026-09-29` → `self-resolution-measure-submission-2026-09-29.zip`（90,183 B・SHA-256 `65a216b029ea99acae270dd88f4cc85b1d7c5ff7a2ee7f8a086c09c67b5b76c3`・MD5 `513601c006f39a6a409f512014e2121e`）。展開して **27 ファイルすべてが名前と blob ID（`git hash-object --no-filters`）でタグと一致**。展開したものに D1 の zip を置いて `run.sh` exit 0（同梱の `results/` と一致）・`build.sh` exit 0（21 頁）。Zenodo の下書きにアップロード（サーバの MD5 = 手元）・`version` = `submission-2026-09-29`・タグの URL を `isSupplementTo` に追加。
- **C（投稿用の原稿）**: `C:/wt/emse-upload/` に 6 ファイル（`main.tex`・`results.tex`・`refs.bib`・`main.bbl`・`sn-jnl.cls`・`sn-basic.bst`）。`main.tex` はタグの版と `\documentclass[pdflatex,sn-basic,referee,lineno]{sn-jnl}` の 1 行だけ違う（`diff` で確認）・`results.tex` / `refs.bib` はタグと同一（`cmp`）・cls / bst は `build.sh` が固定する SHA-256 と一致。pdfLaTeX で 32 頁・Overfull `\hbox` 0・未定義 0・字形の欠落 0・タイトル頁に ORCID が 1 回。見本の PDF は `C:/wt/emse-preview-2026-09-29.pdf`（上げない）。
- **D・E（研究者の確認の後・逐語の選択「D と E を続けて実行する」）**:
  - タグだけを push → `gh repo edit --visibility public`（`{"private":false,"visibility":"public"}`）。認証なしで GitHub のページ 200・最上位に `raw/`・cls・bst なし・`paper/` は 5 ファイル・ブランチ main だけ。
  - Zenodo の公開: ⚠️ 私が足した安全確認（下書きのファイルの MD5 が検証した zip と一致すること）が、下書きの一覧の MD5 に `md5:` の接頭辞が無いことで**一度拒否した**（ファイルは正しかった）→ 接頭辞を外して比べるよう直して公開（202・state `done`・10:34 UTC = 19:34 JST）。公開の API で DOI `10.5281/zenodo.23029603`・版・ファイル 1 つ・open を確認。
  - ⚠️ doi.org は公開の 6 分後も 404（DataCite の API も 404 = まだ登録されていない）。→ 解決するまで EMSE の承認は待つ（手順書 F）。
- 取り消せない操作の間隔: public 化から Zenodo の公開までは数分（安全確認の拒否と修正の分）。
- ⚠️ **DOI の登録待ち**（20:12 JST = 公開の約 38 分後）: doi.org・DataCite の API とも 404。Zenodo の記録の API では `pids.doi` = `10.5281/zenodo.23029603`・provider `datacite`・published。研究者の既存の記録（22735437・22733449）の DOI は doi.org で解決し DataCite も 200 → 経路は正常で、この記録の登録だけが Zenodo 側の非同期の処理で遅れている。
- ★ **DOI が解決した**（20:55 JST に確認）: doi.org → `https://zenodo.org/doi/10.5281/zenodo.23029603`（302）→ 記録のページ 200。DataCite の API: state `findable`・registered `2026-09-29T11:34:34Z`（= 20:34 JST・公開の約 1 時間後）・version `submission-2026-09-29`。→ 研究者の選択（逐語「解決するまで待つ」）どおり、ここから EMSE の確定（手順書 F）へ。

## 判断 14: 公開後の README の書き直し（2026-09-29・研究者の依頼「もうちょいおしゃれで門な感じに」）

- ⚠️ 「門な感じ」は「モダンな感じ」と読んで進めた（研究者に伝えた・違えば直す）。
- **形**: 題と副題を中央に・DOI（Zenodo）・ライセンス 2 つ・Python のバッジ／Overview（要旨の言い方に揃えた）／指標の表／データの表／Quick start（clone → D1 をブラウザで取得 → `bash run.sh`）／`run.sh` が確かめること 6 項目／原稿の組み直し／Freeze and provenance／ファイル配置の表／Citation（Zenodo の記録の BibTeX）／ライセンスの表。公開物の規律（学術的な英語・GSE への言及なし・絵文字や口語なし）を守った（grep と文字の走査で 0 件）。
- ★ **書き直しの途中で見つけた言い過ぎ 3 つも直した**（1・2 巡目の裁定と同じ型）: `config.json` の説明 "frozen before results were computed" → 「解析のコードと結果より先に最初にコミットされ、その後の変更は NOTES.md に記録」／D2 の抽出元 "Table 4 and Table 5 only" → 「Table 4・Table 5 の 3 行・本文の 3 文」（原稿 main.tex と一致）／転記を "independent" → 「同じ LLM の別々のインスタンス」（NOTES.md の限界と一致）。「原稿のすべての数値」→「解析の結果」（原著からの引用値を含まないため）。
- 確かめたこと: バッジ 4 つが SVG で 200・相対リンク 12 件がすべて実在・制御文字 0。論文用リポジトリ `0e3c9ed`（main に push・タグ `submission-2026-09-29` と Zenodo の版は変わらない）。
