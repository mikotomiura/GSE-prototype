# 動機・疲労と再着手の面のサーヴェイ（S-MR・1 ラウンド）と、設計案の具体化

## 背景

- 2026-10-05、研究者が AI 疲労 DB の文献を読んでいて気付いたことから議論した（Claude Code との対話）。議論の記録と決定は `.idea/20261005-motivation-fatigue-reentry-surface.md`（版管理外・main checkout）にある。
- 議論で決めたこと（研究者の回答）:
  - 「AI 疲労の始まり」は順序ではなく**構成**として持つ（中身の少なからぬ部分は動機＝投資を続ける意思の低下）。
  - ワクワクは**非随伴**（思いがけない形が返る）の側。
  - 「併発」は**両方高い人がいる**（人と人のあいだ）の意味。
  - 着手の面は **A: セッション内に閉じ、打鍵から形が立ち上がる**（D 日替わりの地模様を対照に）。
  - 疲労と停滞は **A: 多層**（人の背景 × その人の中の停滞の配合と終わり方）で結ぶ。
- 議論の時点の根拠は repo 内の既存の一次だけだった。次の 3 点が未接地のまま残った: (1) AI 疲労とデジタル疲労が両方高い人がいる、の根拠が AF001 の 1 本だけ ／ (2) 非随伴の驚きが動機・再関与に効く証拠が repo にゼロ ／ (3) 動機が効くのは着手より再着手だ、は推測。

## ゴール

1. `/literature-review` の 1 ラウンドを回し、上の 3 点を外部の一次に接地する（下位問い 4 つ・5 angle・20〜25 ソース・名前空間 `P`・用途は設計の根拠の補強とランドスケープ。gate 判定ではない）。
2. 結果を `.idea/20261005-motivation-fatigue-reentry-surface.md` §7 に書き、設計案を具体化する（何を・どの面に・いつ・何で評価し・何で棄却するか）。

## スコープ

### 含むもの
- 精読カード `docs/literature/20261005-motivation-fatigue-reentry-surface.md`（落合 6 項目・敵対的 3 票・否決リスト）
- `docs/references.md` への append-only 登録（メインが直列）・`docs/literature/_index.md` への 1 行
- `.idea/` の §7 と具体化（版管理外）
- コミット・push。`/cross-review` 2 巡（コミット後・パス限定）

### 含まないもの
- `docs/research-positioning.md` の還元（研究者の決定: **還元不要**と明記する）
- ADR・RP §1・ADR-023 D11-a の改訂（日常の PC 面を主線に上げる判断はしていない）
- G1/O1 の収集・配布物の変更（質問紙の追加を含む）
- attack-me（研究者の決定: 今回は回さない。EH3 の事前登録の前に回す）
- 実装（合成 trace・描画）
- AI 疲労 DB の研究者へ渡す文書への反映
- 有料の DB・有料の本文

## 受け入れ条件

- [ ] 下位問いごとにエビデンス温度（確定 / PLAUSIBLE BUT UNPROVEN / 判定不能）が 1 行ずつある（平均化しない）
- [ ] 反証 angle を含み、否決リストがある
- [ ] 断定に使う一次はメインが開いて確かめている（subagent の要約だけで断定しない）
- [ ] `python scripts/check_citations.py` が `=== 違反なし ===` で終わる（是正→再実行を繰り返す）
- [ ] このラウンドを単独でコミットしている
- [ ] `.idea/` §7 に結果と具体案があり、根拠の格（一次で確かめた / 抄録だけ / 推測）が書き分けられている
- [ ] `/cross-review` 2 巡の結果と対応が `decisions.md` にある。計測の run 中なので PR は出さず push だけ

## 関連ドキュメント

- `.idea/20261005-motivation-fatigue-reentry-surface.md`（議論の記録）
- `.steering/20260921-media-expression-theory-audit/pc-workplace-media-reassessment.md`（main checkout・未追跡）
- `docs/glossary.md`「関与の再開」・`docs/literature/20260907-pc-invitation-surface-and-peripheral-cost.md`
- `.steering/20261001-ai-fatigue-34-screening/measurement-issues.md`・`wave1/extract-X1.md`
