# docs/history —— 履歴の文書と旧パスの表

このディレクトリの文書は履歴で、現行の根拠に使わない（ADR-053）。現行の主張は `docs/` の現行の文書と `docs/adr/` が一次である。

- 書き直す前の全文を、ファイル名に日付を付けて逐語で残す。先頭の頭書きだけを足し、本文は変えない。
- 履歴の文書は直さない。

## 旧パスの表

ADR の本文は書き換えないので、ADR に書かれた旧パスはこの表で辿る。

| 旧パス | 扱い | 移し先・削除のコミット | 日付 | 理由 |
|---|---|---|---|---|
| `docs/research-positioning.md`（2026-11-15 より前の全文） | 書き直し・旧全文を写した | `docs/history/research-positioning-2026-11-15.md`（現行版は同じパスのまま） | 2026-11-15 | 改訂ブロック 3 層の上書きの鎖を解く（ADR-053） |
| `docs/design-history.md` | 履歴へ移した | `docs/history/design-history-2026-11-15.md` | 2026-11-15 | もともと履歴の文書（v2.1–v2.22）。現行の文書と分ける |
| `docs/design-history.ja.md` | 削除 | 削除のコミットは PR2（`docs/gse-docs-clarity-pr2`）。英語版と同じ内容 | 2026-11-15 | 英語版の写しを履歴に残したので重複を外す |
| `docs/calibration-smoke-runbook.md` | 履歴へ移した | `docs/history/calibration-smoke-runbook-2026-11-15.md`。§1.1–1.2（研究者デバッグ起動の二重 gate）は `docs/verification-runbook.md` §2.0 へ移した | 2026-11-15 | Phase1（v0.3 較正）は 2026-08-18 に終了した |
| `docs/architecture/gse-v2-overview.md` | 履歴へ移した | `docs/history/gse-v2-overview-2026-11-15.md` | 2026-11-15 | 2026-07 の Epic 期のアーキテクチャ。現行は `docs/architecture/gse-design-map.md` と ADR |
| `docs/architecture/intervention-decision-engine.md` | 履歴へ移した | `docs/history/intervention-decision-engine-2026-11-15.md` | 2026-11-15 | Nudge を中心にした Layer 5-7 の設計。Nudge は本体で出さない（ADR-040） |
| `docs/architecture/domain-adapter-boundary.md` | 履歴へ移した | `docs/history/domain-adapter-boundary-2026-11-15.md` | 2026-11-15 | 2026-07 の Epic 期の Layer 0-3 の案。現行は ADR-002・006 と gse-design-map |
| `docs/wbs-verification-halfyear.md` | 削除 | 削除のコミットは PR2（`docs/gse-docs-clarity-pr2`）。最後の版は main `6fdd4023` | 2026-11-15 | 研究者の指示。26 週の WBS は段 1・段 2 の設計（ADR-043〜052）で置き換わった |
| `docs/eh3-distribution-tag.md` | 削除 | 削除のコミットは PR2（`docs/gse-docs-clarity-pr2`）。最後の版は main `6fdd4023` | 2026-11-15 | EH3 は研究として実施しない（ADR-049） |
| `docs/architecture/personalization-and-online-learning.md` | 履歴へ移した | `docs/history/personalization-and-online-learning-2026-11-15.md` | 2026-11-15 | Epic 期の Proposed の設計（ADR-008・009）。今の推定の段の地図は ADR-046 D3 と gse-design-map |
| `docs/architecture/task-adaptation-and-scope-gating.md` | 履歴へ移した | `docs/history/task-adaptation-and-scope-gating-2026-11-15.md` | 2026-11-15 | Epic 期の Proposed の設計（ADR-010）。タスク適応は ADR-046 D3 の段の 1 つ |
