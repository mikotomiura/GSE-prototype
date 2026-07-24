# ADR-003: Accountability を GSE Core 外の opt-in extension に分離する

- **ステータス**: Proposed（**境界は分離で合意・採否は Deferred**＝効果エビデンス未確定・第4ラウンド/RQ-3 待ち）
- **日付**: 2026-07-24
- **関連**: 設計書 §1.3/§4・`gse-v2-overview.md §5`・`research-positioning.md §8`

## Context
Phase1 で 1 名から「向かいに人がいて義務感が生じ作業が捗った」という所見（**n=1・逸話水準**）。この作用は
認知活性化でなく **社会的説明責任 → 義務感 → 開始/継続** の経路と解釈され、GSE Core（作業中の摩擦・前進・
介入可能性）とは別物。放置すると Core の状態推定・介入効果を**交絡**させる。

## Decision
Accountability（他者存在・約束・締切）を **`extensions/accountability/` として Core の外へ分離**する
（`core/{sensing,inference,opportunity,intervention}` と別境界）。**標準機能にせず opt-in の実験モジュール**とする。
Core の intervention condition とは分離する。

> ⚠️ **効果は主張しない**。分離は「交絡を切り離す」ための境界判断であり、Accountability が効くという主張ではない。
> 採否（研究対象に残すか）は deep-research 第4ラウンド（RQ-3）のエビデンス確認後に判断する（Deferred）。

## Alternatives
- **Core に統合**: 状態推定・介入効果を交絡させる（設計書 §1.3）。研究の内的妥当性を損なう。却下。
- **完全に無視/削除**: n=1 とはいえプロダクト示唆があり、境界を切って観察余地を残す方が安全。
- **標準機能化**: エビデンスゼロで常時 ON は過大主張。opt-in 実験に限定。

## Consequences
- 採用する場合も最小仕様（設計書 §4.2）: opt-in / 相手の詳細進捗を表示しない / タイピング状態を相互公開しない /
  退出通知を強制しない / ランキング・連続記録を作らない / Core の intervention condition と分離。
- 評価は成果量だけで Go 判定しない。start/completion rate に加え perceived obligation・tension・autonomy・
  reuse・performance without partner・perceived surveillance・early exit を**同時に**測る（§4.3）。

## Migration
1. 本 ADR ではディレクトリ境界（`extensions/accountability/`）の**方針のみ**確定。実装しない。
2. RQ-3 のエビデンス確認（deep-research 第4ラウンド）後に採否を決める。採用なら Phase 1.5/2 で opt-in prototype。
3. `SessionContext.accountability_opt_in: bool` は Session Context（Epic 3.5）の additive フィールドとして予約。
