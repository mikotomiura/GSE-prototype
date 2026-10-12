# 設計

## アプローチ

調査と判定のタスク（実装なし）。`/literature-review` の手順で 1 ラウンドを回し、判定の材料を 1 枚にまとめ、研究者に AskUserQuestion で判定してもらい、記録する。

1. 下位問いを引き継ぎの (a)(b)(c) から Q-a / Q-b1 / Q-b2 / Q-c に割った（`b` を攻撃と加工の 2 つに分けた・反証 angle を各本に指定）。
2. 探索はサブエージェント 4 本（Sonnet・並列・各 20 分・入れ子禁止）。生の出力は scratchpad の `survey/`。
3. 断定に使う一次はメインが取り直して照合した（PDF は pypdf・Kaggle と Drive は Chrome）。OpenAlex で引用の追跡を足し、[V267] KeyTAR を見つけた。
4. 判定の材料 `judgement-material.md`、判定 `decisions.md`、著者への問い合わせの下書き `author-inquiry-draft.md`、次の引き継ぎ `_handoff/next-session-public-keystroke-matching-prereg.md`。

## 変更対象

- `docs/literature/20261012-public-keystroke-matching-novelty.md`（新規・カード 5 枚）
- `docs/references.md`（[V264]–[V274] を追加・[V237] と [P274] に注記を追記）
- `docs/literature/_index.md`（1 行追加）
- `docs/adr/ADR-039-research-use-and-release.md`（D1 に 2026-10-12 の注）
- `.steering/_handoff/README.md`・`next-session-public-keystroke-matching-prereg.md`

## 触らないもの

- データの本体（KLiCKe の zip・Kaggle の CSV）は取得していない。打鍵の記録・NDJSON は開いていない。
- `docs/research-positioning.md` は還元不要（カードの判断）。

## 検証

- `scripts/check_citations.py` が「違反なし」で終わること。
- 完了時の `/cross-review` 2 巡。
