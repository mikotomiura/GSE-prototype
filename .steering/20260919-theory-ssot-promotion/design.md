# 設計（段 3 全体）

## 実施アプローチ

- ★ **1 単位 = 1 タスク**。各単位の `requirement.md` / `design.md` / `tasklist.md` / `decisions.md` は単位のディレクトリに置き、本ディレクトリは段全体の判断（研究者判断バッチ 3）と進行だけを持つ。
- ★ **ADR 本文は書き換えない**。補訂節（先例: ADR-014「判断 4 の追補」・ADR-031「M9 の追補」）か、番号の大きい新 ADR で上書きする（`docs/adr/README.md`）。
- ★ ADR を書くときは `citation-ssot` を引く（先例 ADR-010 D5）。
- ★ 各単位の `/cross-review` は **2 巡**（1 巡目 = 自文書と他文書の矛盾 ／ 2 巡目 = 自分が足した規則の境界条件）。コミット後にパス限定で回し、出力先は scratchpad（`$CLAUDE_JOB_DIR/tmp`）。Codex は repo を読めないので資料をプロンプトに貼る。
- ★ 研究者判断が要る箇所は推測で埋めない。実装の設計（issue 004 の U1〜U4 / 006 の V1〜V5）は聞かずに実装フェーズへ回す。

## 変更対象（段全体の見取り図）

| 単位 | 反映先 |
|---|---|
| a | `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（補訂節を足す） |
| b / c / i | `docs/adr/ADR-033-…` 以降（新規）・`docs/adr/README.md`（索引） |
| d | `docs/research-positioning.md` |
| e | `docs/glossary.md` |
| f / g | `.steering/20260916-gse-theory-operationalization-review/*.md` |
| h | `docs/theory/`（新設）・`docs/agent-shared.md` / `docs/repository-structure.md`（ディレクトリの記述） |
| SR | `.steering/20260919-ssot-sr-…/`・`docs/references.md`（append-only）・`docs/literature/` |

## 影響範囲

- タスク 2（`20260914-mhd-feature-offline-tiers`）の実装フェーズ: ADR-030 補訂 1 の規範（観測区間・`feat` 行 0 本）は issue 008 の実装を追認する側であり、実装は変えない。
- G1 / O1 の運用（単位 c）: ADR-014 判断 1 / 4 の上書き。⚠️ 被験者向け文書の変更が要る場合は研究者へ返す。

## テスト戦略

- 実装変更は無い。代わりに: `python scripts/check_citations.py` を「違反なし」まで／禁止用語の検査（`check_doc_lexicon.py` の `scan()` を新しい文書へも当てる）／`/cross-review` 2 巡。

## ロールバック計画

- 単位ごとのコミットを `git revert` する。⚠️ `docs/references.md` は append-only なので、取り消しは tombstone で行う。
