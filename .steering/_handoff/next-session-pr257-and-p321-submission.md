# 次セッション（G-GEAR・このターミナル）— PR #257（O1 管理シート）の仕上げ → 2 本目の論文の投稿準備

> 作成: 2026-09-29（PR #256 の出荷の後）。
> ⚠️ **このメモを一次資料にしない。** 数字・状態は着手時に測り直す。
> ★ 研究者の指示（2026-09-29）:「PR#257, 二本目の論文をこのターミナルでは行う形にしましょう」。
> ⚠️ IME 論文（W4 以降）は**別のターミナルのセッション**が同じ PC・同じ main checkout で進めている → 本メモの作業は main checkout に触らない。

## §0 打ち込む用

```
git fetch origin してから git show origin/main:.steering/_handoff/next-session-pr257-and-p321-submission.md を読んで、次の 2 つをこの順で進めてください。
1. PR #257（O1 管理シート）: 予算で飛ばした Codex の /cross-review を回して指摘を裁定・修正し、CI 緑なら merge → main の CI を確認 → 研究者の実シート確認（researcher-steps.md）に渡す。
2. 2 本目の論文（C:/self-resolution-measure）: /start-task で投稿準備のタスクを作り、grill で §3 の論点を研究者と決めてから進める。
⚠️ main checkout（C:/GSE-prototype）は別ターミナルの IME 論文のセッションが使っている（feature/ime-eval-kit・未コミットの変更あり）。switch / checkout / add / stash / commit をしない。GSE 側の作業はすべて git worktree で切る。
Skill: git-workflow・verify-before-claiming・subagent-delegation・data-privacy（PR #257）・citation-ssot・reproducibility-discipline（論文）・browser-verification（Chrome を使う時）。
応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。コミットは git add パス指定（-A 禁止）。出荷は git-workflow ルール 6。
```

## §1 状態（2026-09-29 12 時頃 JST に測った値）

### PR #257（`feat(o1): O1 管理シートを見て分かる形にする`）

- ブランチ `feature/o1-mgmt-sheet-design`・head `7d6814df`（1 コミット・12 ファイル）。主な変更は `Form_O1/GSE_O1_Ledger.gs`・`Form_O1/GSE_O1_Form_Builder.gs` と、そのテスト（`o1_ledger_test.cjs`・`o1_form_builder_test.cjs`）・変異検査（`o1_ledger_mutation_test.sh`・`o1_form_builder_mutation_test.sh`）。記録は `.steering/20260928-o1-mgmt-sheet-design/`。
- open・CI は緑（Windows の check は 1 回 cancelled の後に success）。`git merge-tree` で main との衝突なし。⚠️ main が進んだので、GitHub 上の mergeable は UNKNOWN と出ていた。
- どの worktree にも checkout されていない。
- 済み: テスト（台帳 229・ビルダー 229）・変異（90/90・70/70）・実コードの出力を HTML に描いて Chrome で目視・code-reviewer ＋ security-checker（反映済み）。
- ⚠️ **残り**: Codex の `/cross-review` が予算ゲートで skip されている（2026-09-28 に 321,699 / 300,000・decisions.md「レビュー」）。CLAUDE.md は各タスク完了時に必須とする → 今日回す。
- ⚠️ 実シートでの表示は**まだ誰も見ていない**（研究者の配備待ち）。

### 2 本目の論文

- 論文用リポジトリ `C:/self-resolution-measure`（`mikotomiura/self-resolution-measure`・private）= `4a81a43`・clean・origin と一致。
- 題（確定・判断 12）: *When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets*。単著 Mikoto Miura（所属なし・Hiroshima, Japan）。
- 投稿先: *Empirical Software Engineering* の研究論文（single-blind・投稿料と掲載料ゼロ・reanalysis 判断 9 / 17）。arXiv へのプレプリントは投稿と同時（reanalysis 判断 10）。
- 原稿: 全節の初稿済み（21 頁・要旨 239 語・表 5 つ・図なし）。`/cross-review` は 2 巡済み。`bash paper/build.sh`（Tectonic＝XeTeX）で組める。
- 仮置きは Data availability の DOI だけ（`paper/main.tex:386` の "[archived copy with DOI to be added]"）。
- GSE 側の記録: `.steering/20260928-p321-reanalysis-paper/`（判断 1–17・`outline.md`）と `.steering/20260928-p321-paper-draft/`（判断 1–12・tasklist の「残課題」）。⚠️ どちらも main にあり、main checkout（IME のブランチ）には無い → `git show origin/main:<path>` か worktree で読む。

## §2 手順

### A. PR #257

1. worktree を短いパスに切る（例: `git worktree add C:/wt/o1-mgmt-sheet feature/o1-mgmt-sheet-design`。ローカルにブランチが無ければ origin から）。
2. **Codex の予算を見積もる**。⚠️ 台帳はブランチごとに分かれる（memory `project_codex_ledger_branch_split`）。PR のブランチの `.codex/budget.json` は 09-28 の値のままで、ラッパーは日付が変わると 0 から数える → ★ **origin/main の今日の値**（09-29 の測定時点で 109,931・2 回）と、**他の作業中ブランチ**（`feature/ime-eval-kit` など・別ターミナルが使うかもしれない）の今日の値を足して残りを見る。1 巡の実績は 33k〜77k。足りなければ研究者に聞く。
3. `/cross-review` を**パス限定**で回す（memory `project_cross_review_cached_gap`: `scripts/run-codex-review.sh -- <paths>`。範囲は `origin/main...HEAD`、対象は `Form_O1/` の `.gs` とテスト）。Claude 側（code-reviewer / security-checker）は済んでいるので、裁定するのは Codex の指摘。1 巡目で直した場合は、2 巡目で直した箇所の境界条件を見る（memory `project_cross_review_two_rounds`）。
4. 直したらテストと変異を回し直す → `decisions.md` に裁定を書き、「Codex は skip」の記録を実施済みに更新 → `.codex/budget.json` の記帳も含めてコミット（memory `feedback_codex_budget_is_a_ledger`）→ push。
5. CI 緑なら `gh pr merge 257 --merge` → main の run の発火を確認。
6. 研究者に `researcher-steps.md` を示す。貼り付けと `o1LedgerRun()`・`buildO1MgmtSheet()` の実行は研究者が行う。★ #253（受け取りフォルダの P-ID 分け）の配備と同じ機会でよい。Chrome で表示を見るなら `browser-verification`（読むだけ・実行する前に承認を取る）。

### B. 2 本目の論文の投稿準備

1. `/start-task`（例: `p321-paper-submission-prep`）。GSE 側の作業記録は GSE の worktree の `.steering/` に、原稿の変更は論文用リポジトリに置く。
2. grill で §3 の論点を研究者と決め、`decisions.md` に書く。
3. 決まった順に進める。原稿を直したら `bash run.sh` と `bash paper/build.sh` が exit 0 になることを確かめる。

## §3 研究者と決めること（投稿準備の論点）

1. **研究者の通読**: 原稿（21 頁）を研究者が通しで読んだという記録は無い（draft 判断 12 で確認したのは、著者情報・Statements・題・LLM の開示の文面・ライセンス・コミットの著者）。投稿前に通読してもらうか、その返答をどう反映するか。
2. **pdfLaTeX で組めるかの確認**（draft 判断 2 の残課題）: Overleaf（原稿を外部サービスに上げる）／投稿システムのプレビュー／scratch に TeX を置いて手元で組む（システムには入れない方針）のどれにするか。
3. **公開と DOI**: GitHub の repo を public にする時期・Zenodo の DOI の取り方（GitHub 連携か手動アップロードか）・原稿（`paper/`）のライセンス（README は「未定」）。⚠️ public にすると、`4a81a43` より前のコミットの著者（別のメールアドレス）も公開される（draft 判断 12）。⚠️ 外部アカウントの操作は研究者が行う。
4. **arXiv**: 投稿と同時（reanalysis 判断 10）。⚠️ 初めて投稿する人は endorsement が要る場合がある → 規程を一次で確かめてから決める（**未確認**）。カテゴリとライセンスも決める。
5. **投稿の手続き**: EMSE の規程を開き直す（draft の残課題）・カバーレター・投稿システムで必須の項目（ORCID・推薦査読者など・**未確認**）・投稿する日。

## §4 気をつけること / やらないこと

- ⚠️ **main checkout に触らない**（別ターミナルの IME のセッション）。worktree は短いパスに置く（`C:/wt/...`。scratchpad の長いパスだと Rust の `target/` を消せないことがある）。
- ⚠️ Windows の CI の runner はこの PC そのもの。IME の loop-run と重なっても Windows の check が 12〜13 分で通った run が 3 本ある（PR #256・main `36512457012`）。30 分で打ち切られたら、再実行を繰り返して通そうとしない（git-workflow ルール 6）。背景は `.steering/_handoff/next-session-win-ci-timeout-headroom.md`。
- ⚠️ 論文で書いてはいけないこと: `next-session-p321-reanalysis-paper.md` §3・`outline.md`・`docs/glossary.md` の禁止用語。公開物は学術的な英語で、GSE に言及しない（memory `feedback_public_artifacts_academic_no_gse`）。原稿の数値は `results/metrics.json` から生成し、直書きしない（draft 判断 6）。
- ⚠️ 論文用リポジトリの差分を Codex に見せるときは、GSE の worktree に `git fetch` してからラッパーを範囲指定で呼ぶ（memory `reference_codex_review_other_repo`）。
- ⚠️ 論文の投稿・arXiv・Zenodo・repo の public 化は、研究者が行うか、研究者の承認を得てから行う。
- ⚠️ ADR-024 D7 の根拠の訂正（reanalysis 判断 14）は「次の関連 ADR」で行う。今回はやらない。
- ⚠️ IME 論文の `decisions.md` 判断 8・13 に CHI 取り下げ（reanalysis 判断 15）を追記するのは IME のタスク側（別ターミナル）の仕事。
