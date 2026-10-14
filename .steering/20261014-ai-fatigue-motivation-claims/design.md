# 設計

## アプローチ

`/literature-review` 1 ラウンド（S-AF2 と呼ぶ）。6 angle を Sonnet のサブエージェントへ並列に投げ、逐語・完全な書誌・反証を持ち帰らせる。断定に使う一次はメインが開く。採番と references.md への追記はメインが直列で行う。

## 変更対象

- `docs/literature/20261014-ai-fatigue-motivation-discriminant.md`（新規カード）
- `docs/references.md`（append-only）・`docs/literature/_index.md`（1 行）
- `.steering/20261014-ai-fatigue-motivation-claims/summary.md`（まとめの表）
- `docs/research-positioning.md` への還元: 不要の見込み（GSE の外の研究のため）。判断はカードに書く。

## テスト戦略

- `python3 scripts/check_citations.py` が `=== 違反なし ===` まで繰り返す。
- /cross-review（docs の diff）。
