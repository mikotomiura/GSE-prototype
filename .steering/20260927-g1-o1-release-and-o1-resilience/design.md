# 設計 — g1-o1-release-and-o1-resilience

## アプローチ
- T1 は手順の実行（承認 → タグ → Release 実体検証 → zip → 記録）。設計判断なし。
- T2 は subagent で**事実の収集**（4 本並列・調査のみ）→ 断定に使う箇所はメインが一次で開く → 判断は `decisions.md`。
- T3 は研究者の採否待ち。GAS は 1 行も変えていない。

## 変更対象（本コミット時点）
- `.steering/20260927-g1-o1-release-and-o1-resilience/`（記録のみ）
- `experiments/20260801-controlled-friction-task/distribution-tag.md`（ADR-034 Migration 3 の記録・新規）
- コード変更なし。

## テスト戦略
- 配布物は実体検証（`LC_ALL=C grep -a` を対照つき・`codesign --verify --strict`・zip 展開後の再検算）。
- T2 のコード修正（承認後）は O1 用の別タグで、`cargo test` ＋ 両 OS の対のテスト（`docs/agent-shared.md`）。
