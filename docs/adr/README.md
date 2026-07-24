# Architecture Decision Records (ADR)

GSE の重要なアーキテクチャ判断を記録する。各 ADR は **Context / Decision / Alternatives / Consequences /
Migration** を持つ。SSOT のアーキテクチャ概要は `docs/architecture/gse-v2-overview.md`、研究の主張・
エビデンス温度は `docs/research-positioning.md`、現行実態は `.steering/20260724-epic0-repo-reality-check/`。

## ステータス凡例
- **Accepted**: 決定済み。実装が従う。
- **Proposed**: 方向は合意。詳細/確定は実装時 or 後続 ADR。
- **Deferred**: 判断を保留（エビデンス待ち／Phase1 完了待ち／研究者判断待ち）。
- **Superseded by ADR-xxx**: 後続 ADR に置換。

> **前提**: すべて Phase1 完了 + 研究者承認が前提。Epic 1（本 ADR 群）は**コード変更ゼロ**。凍結対象
> （`schema_dto.rs`/`schema/current.json`・`engine.rs` HMM_VERSION・`intervention.rs` 閾値・`probe_scheduler.rs`・
> `App.tsx` argumentative lock・`preregistration-v0.3.md`）は Phase1 完了まで変更禁止。

## 一覧

| ADR | 主題 | ステータス | 対応 Epic |
|---|---|---|---|
| [ADR-001](ADR-001-hmm-as-writing-baseline.md) | HMM を Writing baseline へ降格・三状態表示の降格 | Accepted（実装は後続） | Epic 1→2 |
| [ADR-002](ADR-002-domain-local-inference.md) | domain-local inference / DomainAdapter 境界 | Proposed | Epic 2 |
| [ADR-003](ADR-003-accountability-outside-core.md) | Accountability を core 外の opt-in extension に分離 | Proposed（採否は Deferred・第4ラウンド待ち） | Epic 3.5+ |
| [ADR-004](ADR-004-decision-engine-boundary.md) | Decision Engine 境界（pure function 化）+ Consent 軸 | Accepted（Consent 実装は Epic 3） | Epic 3 |
| [ADR-005](ADR-005-event-envelope-versioning.md) | Event Envelope schema versioning | Proposed | Epic 2/5 |
| [**ADR-006**](ADR-006-task-kind-beta-wiring.md) | **task_kind → β baseline 配線 or IME 代理を正とするか** | **Accepted（枠組み C「分離」＋下位決定 #2/#3 確定 2026-07-24）・実装は Phase1 後** | Epic 2 分岐点 |
| [ADR-007](ADR-007-receptivity-decomposed-vs-unified.md) | receptivity 統合スコア化 or 分解維持 | Accepted（分解維持を推奨） | Epic 3 |
