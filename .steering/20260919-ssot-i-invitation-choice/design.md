# 設計

## 実施アプローチ

- 検討メモ（`analysis.md`）で既存の選択の仕組みと既決が退けた選ばせ方を整理し、選択肢 A / B / C を研究者へ示した → 研究者判断「A: 原則だけの ADR を起こす」（段 3 判断 3 #2）。
- ADR-035（Proposed）: D1 要件（有無と時期の範囲）・D2〜D6 原則（既定値・少数の選択肢・設定の変更を応答にしない・本人の目標にしない・数値で返さない）。★ D4〜D6 は既決（ADR-033 / 018 / 025）の言い換えで、新しい決定は D1〜D3 だと Consequences に書いた。
- UI・既定値・選択肢の具体は Physical Anchor の実装時（ADR-026 PC-5 / PC-6 と一緒に）。

## 変更対象

- `docs/adr/ADR-035-invitation-choice-principles.md`（新規）・`docs/adr/README.md`

## テスト戦略

- `check_citations.py` 違反なし。`/cross-review` 2 巡（⚠️ Claude 単独になりうる）。
