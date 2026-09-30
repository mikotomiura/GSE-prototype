# p321-paper-submission-prep — 2 本目の論文（自己解決の指標の再解析）の投稿準備

## 背景

2 本目の論文 *When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets*
（単著 Mikoto Miura・論文用リポジトリ `C:/self-resolution-measure` = `mikotomiura/self-resolution-measure`・private）は
全節の初稿が済み（`4a81a43`・21 頁・要旨 239 語・`/cross-review` 2 巡済み）。投稿先は *Empirical Software Engineering* の
研究論文（single-blind・投稿料と掲載料ゼロ）。前タスク `.steering/20260928-p321-paper-draft/` の残課題と、
引き継ぎ `.steering/_handoff/next-session-pr257-and-p321-submission.md` §3 の 5 論点（通読・pdfLaTeX・公開と DOI・arXiv・投稿の手続き）が残っている。

## ゴール

研究者が EMSE に投稿できる状態にする。具体的には:

- 原稿の仮置き（Data availability の DOI）が埋まり、研究者の通読の指摘が反映されている
- pdfLaTeX（投稿システム・arXiv と同じエンジン）で組めることを手元で確かめてある
- 再現一式の DOI が予約済みで、投稿日に公開する手順（GitHub の public 化・Zenodo の公開）が決まっている
- カバーレターの下書きと arXiv の endorsement の依頼文の下書きがある

## スコープ

### 含むもの
- grill で 5 論点を決める（`decisions.md` 判断 1–10）
- Zenodo の下書きの作成と DOI の予約（研究者が token を提供し、自動での操作を許可した・2026-09-29）
- 原稿の変更（DOI・原稿のライセンス・ORCID・通読の反映）と、そのビルド・検査
- pdfLaTeX での組版の確認（scratch に TeX を置く）
- カバーレター・endorsement の依頼文の下書き・研究者の通読のための主張と根拠の対応表
- 原稿の変更への `/cross-review`（Codex は予算が戻ってから）

### 含まないもの
- EMSE への投稿そのもの・arXiv への投稿・endorsement の依頼（研究者が行う）
- GitHub の public 化と Zenodo の公開（投稿日。どちらも取り消しにくいので、その時点で研究者に確認してから行う）
- PR #257（O1 管理シート）: 研究者の指示で Mac 側に移った（2026-09-29）。この端末の Codex 1 巡目の控えは `C:/wt/pr257-codex-r1/`
- ADR-024 D7 の根拠の訂正（前タスク判断 14: 次の関連 ADR で行う）・IME 論文の decisions への追記（IME のタスク側）

## 受け入れ条件

- [ ] 論文用リポジトリで `bash run.sh` と `bash paper/build.sh` が exit 0（原稿を直した後）
- [ ] pdfLaTeX（+ BibTeX）で `paper/main.tex` を組み、エラーなし・未定義の参照と引用なし・頁数と Overfull を Tectonic の結果と比べて記録
- [ ] Zenodo の下書きに DOI が予約され、原稿の Data availability に同じ DOI が入っている（公開はしていない）
- [ ] 研究者が全文を通読し、指摘の反映を研究者が確かめた
- [ ] カバーレターと endorsement の依頼文の下書きを研究者が確かめた
- [ ] 原稿の変更に `/cross-review`（Codex ＋ Claude）を当て、指摘を裁定した

## 関連ドキュメント

- `.steering/20260928-p321-reanalysis-paper/decisions.md`（判断 1–17・投稿先・プレプリント・ライセンス・EMSE の書式）
- `.steering/20260928-p321-paper-draft/decisions.md`（判断 1–12・テンプレート・ビルド・著者情報）
- `.steering/_handoff/next-session-pr257-and-p321-submission.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 投稿の手続きと原稿の仕上げで、設計判断を伴わない。論点は grill で研究者と決めた（判断 1–10）。
