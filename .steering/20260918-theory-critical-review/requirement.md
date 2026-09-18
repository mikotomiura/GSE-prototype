# GSE 理論草案の批判的レビュー（pre-SSOT → SSOT 候補の仕分け）

> Status: **pre-SSOT**。本タスクの成果物はこの作業ディレクトリの中だけに置く。
> `docs/`・ADR・事前登録・実装は**研究者の採否なしに変更しない**（別トラック `20260916-gse-theory-operationalization-review/requirement.md` 冒頭の規約）。
> 起点: `.steering/_handoff/next-session-theory-critical-review.md`（⚠️ 一次資料ではない）／研究者判断 25（`.steering/20260914-mhd-feature-offline-tiers/decisions.md`）。

## 背景

- 制限期間中に Codex と議論して、`.idea/` に理論草案 3 本（A: 理論体系・ロードマップ／B: 生成的返権論／C: 未踏研究計画）と、
  別トラック `.steering/20260916-gse-theory-operationalization-review/` に評価契約群（D）ができた。
- 別トラックの規約は「Claude Code との批判的検討と人間による採否判断を経るまで SSOT へ上げない」と定める。
  → ★ 本タスクは **SSOT 昇格の前に必ず通る段**である。
- 研究者判断 25（2026-09-18）で、次の 3 件も本タスクに入った:
  1. `T1d`（issue 006）の「再停止」「安定生成」を、EVAL-NCC の「再停止」と**一体で**定義する（起票 17）
  2. `T1c`（issue 004）の revision 系 4 項目（`rewrite` / `redelete` / `loop_depth` / `local_recurrence`）の算出式を、CORE-CS／修正の理論と突き合わせて決める（起票 9）
  3. ADR-030 の**補訂案**を作る（観測区間の規則・feat 行 0 本で onset を立てない・修飾キー規則の両極・IME 抑制は P1 まで保留・`hole_gap_ms` と削除 UI 最小幅の制約）。⚠️ 案まで

## ゴール

- A → B → C → D の順に**全文**を読み、各文書に `review-<A|B|C|D>.md`（主張台帳／SSOT 衝突／要サーヴェイ一覧／研究者判断一覧）を作る。
- 研究者判断が要る箇所を AskUserQuestion でまとめて聞き、回答を `decisions.md` に記録する。
- 「再停止」の定義（EVAL-NCC）と `T1d` への写像案、`T1c` の算出式案、ADR-030 補訂案を作る。
- 別トラックの未チェックの受け入れ条件を判定する。
- 段 1 で「要サーヴェイ」とした箇所に限り、段 2 のサーヴェイ（`/literature-review`、1 ラウンド＝1 問い・即コミット）を行う。

## スコープ

### 含むもの

- 文書 A / B / C / D の批判的レビュー（主張台帳・判定：保持・統合・縮小・棄却・要サーヴェイ）
- 既存 SSOT（`docs/research-positioning.md` / `docs/preregistration-v0.3.md` / `docs/glossary.md` / ADR-023・025・027〜032 / `docs/architecture/expression-channel.md` / `docs/references.md`）との衝突の洗い出し
- 禁止用語の機械検査（`scripts/check_doc_lexicon.py`）
- 「再停止」／`T1d`／`T1c` の定義案、ADR-030 補訂案（作業ディレクトリ内の草案として）
- 段 2: 要サーヴェイ箇所のサーヴェイと `docs/references.md` への append-only 登録

### 含まないもの

- `docs/`・ADR・事前登録・実装の変更（段 3 = 別タスク。研究者の採否の後）
- issue 004 / 006 の実装（定義確定後、タスク 2 の再開順で）
- `.idea/` 草案本体の書き換え（レビュー結果は作業ディレクトリに置く）
- 参加者実験・効果量の推定
- 体系的レビュー完了前に「先行研究が存在しない」と書くこと

## 受け入れ条件

- [ ] `review-A.md`〜`review-D.md` の 4 本が、主張台帳・SSOT 衝突・要サーヴェイ・研究者判断の 4 節を持つ
- [ ] 各文書を全文読んだうえで判定している（1 節で代表させていない）
- [ ] `check_doc_lexicon.py` の結果を各レビューに記録している
- [ ] 研究者判断を AskUserQuestion で得て `decisions.md` に記録している（推測で埋めていない）
- [ ] 「再停止」の定義と `T1d`（`restop_ms` / `stable_generation_ms`）への写像案が 1 つの定義から導かれている
- [ ] `T1c` の算出式案が CORE-CS／修正の理論と突き合わされている
- [ ] ADR-030 補訂案が §1-3 の 5 項目を含み、ADR 本文を変更していない
- [ ] 別トラックの未チェック受け入れ条件に判定（充足・未充足・持ち越し）が付いている
- [ ] 未実証の因果・新規性・一般化・ジャンル成立を断定していない
- [ ] 段 2 を行った場合、1 ラウンドごとにコミットし、`check_citations.py` が違反なしになっている

## 関連ドキュメント

- `.steering/_handoff/next-session-theory-critical-review.md`
- `.idea/20260915-gse-theory-architecture-and-roadmap.md`（A）
- `.idea/20260915-generative-relinquishment-theory.md`（B）
- `.idea/20260916-gse-mitou-research-plan.md`（C）
- `.steering/20260916-gse-theory-operationalization-review/`（D）
- `.idea/20260908-measurement-terminating-practice-portraiture.md`（参考）
- `.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25 ／ `blockers.md` 起票 9・11・12・15・17

## 運用メモ

- /reimagine 適用: **No**（2026-09-18 研究者回答・`decisions.md` 判断 1 #18）
- 理由: 本タスクはレビューであり、定義案・補訂案は段 3（SSOT 昇格）の別タスクで `/cross-review` 2 巡を通す。必要ならそこで /reimagine する
- モデル: レビュー本体・研究者判断の整理は Opus（メイン）。サーヴェイのサブエージェントは調査向けモデル、実装系（Loop）は Sonnet
