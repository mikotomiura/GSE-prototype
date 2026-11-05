# design

## アプローチ

`/literature-review` の手順どおり。下位の問い 4 つ（研究者の合意・decisions 判断 1）を、Sonnet の general-purpose サブエージェント 4 本に 1 本ずつ並列で渡す（入れ子禁止・締切 20 分・逐語と書誌を持ち帰らせる・references.md に既にある文献は番号だけ）。

- SQ-1 動機づけ: 1 日 1 回・1〜2 項目で今日の作業への動機づけを尋ねた日誌・ESM の尺度と、人内の信頼性・妥当性。
- SQ-2 主体感・同期・共存: 主体感の短い自己報告と、表示や他者との同期・共在の短い尺度。打鍵に連動する表示への当てはまり。
- SQ-3 1 項目の妥当性: ESM・日誌の 1 項目の人内の信頼性、1 項目と多項目、日の終わりの振り返りとその場の報告の差。
- SQ-4 反証: 1 項目の信頼性の低さ、期待・要求特性で膨らむ同期・主体感の報告、日次の尋ね方の反応性、遅れた回答の偏り。

メインが逐語を一次（全文 PDF か抄録）で照合し、3 票（内的妥当性・外挿＝打鍵の作業と日の終わり・頑健性）を付け、カードに落とす。採番は V386 から（全枝で V の最大は V385。P は未マージの枝が P485〜P554 を使っているので P を使わない）。

## 変更対象

- `docs/literature/20261105-daily-end-of-day-items.md`（新規）
- `docs/references.md`（append）
- `docs/literature/_index.md`（1 行）
- `docs/research-positioning.md`（還元するなら）

## テスト戦略

- `python3 scripts/check_citations.py` が違反なしまで繰り返す。
- 完了時に code-reviewer と /cross-review（docs の diff）。
