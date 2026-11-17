# 設計

## アプローチ

`/literature-review` の 1 ラウンド。下位の問い 1〜4（引き継ぎの案のまま）を、問いごとに 2 本（うち 1 本は反証の向き）の angle に分け、Sonnet のサブエージェント 8 本を並列で回す（入れ子なし・各 25 分）。共通の依頼文は scratchpad の common-brief.md に置き、登録済みの照合は main と未マージの各枝の references.md を書き出して grep させた。

メインは、サブエージェントが保存した全文のテキストで逐語を照合し、書誌を Crossref・DataCite・arXiv で確かめてから採番した。3 票はメインが 3 つの視点（内的妥当性 / GSE への外挿 / 網の粗さ）で付けた（S-3C と同じ逸脱）。

## 変更対象

- docs/literature/20261117-expression-audit-precedent.md（新規・カード 4）
- docs/references.md（P555〜P585 を append）
- docs/literature/_index.md（1 行）
- 議題 1b（`.steering/_handoff/next-session-gse-research-meta-after-run1.md`・本線のチェックアウトの未追跡のファイル）に 1 段落

## 検証

- scripts/check_citations.py が「違反なし」
- /cross-review（Codex には設計の抜粋と文献の書誌だけを送る）
