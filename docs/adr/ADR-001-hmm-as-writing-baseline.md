# ADR-001: HMM を Writing baseline へ降格し、三状態表示を降格する

- **ステータス**: Accepted（方向性）。実装（三状態表示の置換）は Epic 2 / UI 改修で・Phase1 完了後。
- **日付**: 2026-07-24
- **関連**: `gse-v2-overview.md §4`・設計書 §2.3/§3.3/§3.5/§7.2

## Context
旧設計は HMM の三状態（Flow/Incubation/Stuck）出力を GSE の主役に置く。GSE v2 は「内面を断定せず連続 proxy を
扱い、主役を Intervention Decision Engine に移す」（設計書 §0）。現行実態（Epic 0）:
- `engine.rs` の HMM は既に OS 非依存・β dual baseline を持ち、Writing 前提で動く。
- 旧 **Flow/Incubation/Stuck 三状態表示**が `src/App.tsx:65-98,195` と `src/components/Dashboard.tsx:22,189-190` に
  残存。ただし calibration blind（week1）では**非表示に gate 済み**（Dashboard.tsx:51）。

## Decision
HMM を **GSE 全体の ontology でなく「Writing Head の baseline（補助モデル）」**として位置づける。HMM は廃棄しない。
出力は三状態の断定でなく **v2 proxy + uncertainty**（`WorkStateEstimate`）へ写す。UI の三状態表示は
**連続 proxy 表示へ置換、または歴史的説明へ降格**する。

## Alternatives
- **HMM を主役のまま拡張**: 旧設計の延長。設計書 §0/§13 が明確に否定（三状態分類は claim しない）。却下。
- **HMM を撤去**: Phase1 の確証トラック（Writing X1）を失う。過剰。却下（廃棄しない）。
- **三状態表示を即削除**: calibration UI の blind gate に波及するリスク（migration-risk-register）。段階的降格を採る。

## Consequences
- HMM の内部挙動・`HMM_VERSION` は**変えない**（降格は「位置づけ」と「表示」の話）。Phase1 凍結と両立。
- README/技術設計の「三状態を正確に分類」表現を段階的に削除（設計書 §2.3/§7.3・本体書換は研究者承認後）。
- Phase1 が Kill でも「Writing Head/HMM の破綻」であって GSE 全体の Kill ではない（Adapter 化で差替可能に）。

## Migration
1. **表示ロジックと blind gate ロジックを分離**してから三状態表示を置換（calibration parity をテスト・migration-risk-register）。
2. `WorkStateEstimate` への写像は Epic 2（Writing Adapter 抽出）で導入。
3. README/docs の主張置換は別タスク（研究者承認後）。docs 側の方針は `gse-v2-overview.md §4` に記載済み。
