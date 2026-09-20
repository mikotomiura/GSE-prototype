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

## ★ 結果（2026-09-19・最終化）

- ★ 全単位（a・b・c・d-1・d-2・d-3・e・f・g・h・i・SR）を 2 巡の `/cross-review` を経てコミットした（単位ごとのコミットは `.steering/_handoff/next-session-theory-stage3-followups.md` §1）。
- ⚠️ **Codex の系統はほぼ全単位で skip**（日次予算の残り 47,400 が、段 3 の cross-review 1 回の実測消費 54,000〜56,000 を下回った —— 単位 e 判断 3）。★ Claude のレビュー担当だけで 2 巡を回し、単位ごとの `decisions.md` に skip の理由を書いた。★ 2026-09-19 夜の再開以降、レビュー担当は opus・操作系のサブエージェントは sonnet で起動した（研究者の指示・memory `feedback_subagent_model_split`）。
- ★ 当初の設計からの変更:
  - 単位 i は「検討メモ（起票しないこともある）」から **ADR-035（Proposed）の起票**へ（研究者判断 3 #2）。
  - SR は段 2 を「結論が確定した時点で打ち切る」形へ（逸脱 2・利用上限に 2 回当たったため）。手動の補完（ACM DL・PhilPapers）は研究者の Chrome で行った。
  - d-3 は RP §4 だけでなく、「体系的レビューの前」と保留していた箇所（RP §1 / §3・用語集・ADR-033・`docs/theory/`）にも日付つきの注記で結果を当てた。
- ★ 研究者の確認待ち・実装フェーズへ渡すものは引き継ぎ §2 / §3。
