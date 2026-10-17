# 設計

## アプローチ

- DB のプロトコル草稿 v0.2（`../20260930-ai-fatigue-protocol/protocol-ja.md`）と同じ GSRR 65 項目の順で書く。同じ所は「DB のプロトコル [GSRR-n] に従う」と参照し、C で違う所だけを書く。
- 材料は M1〜M7（`../20261001-ai-fatigue-34-screening/measurement-issues.md`）・提案書 v2 §6（`../20261002-ai-fatigue-v2/proposal/proposal-v2.md:90-115`）・核 1（`../20261014-ai-fatigue-core1-item-analysis/`）。
- 出典の文献は新しく足さない。手引きの名を出すときは、一次で確かめるまで「候補」と書く。

## 変更対象

- `.steering/20261017-ai-fatigue-c-outline/outline.md`（新規）だけ。

## テスト戦略

- 検査の道具は作らない（骨子の段）。受け入れ条件の 5 点を目で確かめ、`/cross-review` に回す。
