# 設計

## 実施アプローチ

- **段 1（批判的レビュー）**: 文書 A → B → C → D の順に全文を読み、各文書に `review-<A|B|C|D>.md`（主張台帳・SSOT 衝突・要サーヴェイ・研究者判断の 4 節）を置く。
  SSOT との突き合わせは範囲が広いので、読み取り専用のサブエージェント 4 本（research-positioning／表現・介入 ADR 群／文献台帳／研究計画の事実照合）へ並列に委ね、
  **判定を左右する逐語はメインが一次で検算してから**採る（`ssot-collision-findings.md` の検算欄）。
- 禁止用語は `scripts/check_doc_lexicon.py` が**引数を無視する**ため、同じ規則（`scan()` と許可パターン）を import して草案 17 本へ当てる。
- 研究者判断は AskUserQuestion でまとめて聞き、`decisions.md` に記録する（推測で埋めない）。
- **段 2（サーヴェイ）**: 研究者が選んだ S7 → S8 → S1 → S2（＋必要なら Digital Nature）を `/literature-review` で 1 ラウンドずつ回し、ラウンドごとにコミットする。

## 変更対象

### 新規作成するファイル（すべて本ディレクトリ）
- `review-A.md` / `review-B.md` / `review-C.md` / `review-D.md` — 文書ごとの主張台帳と判定
- `ssot-collision-findings.md` — SSOT 衝突の統合表（X-01〜X-32）
- `citations-audit.md` — 草案の引用 × `docs/references.md`
- `definitions-restop-t1d-t1c.md` — 「再開」「再停止」の一体定義 → `T1d`、`T1c` の候補
- `adr-030-amendment-draft.md` — ADR-030 補訂案（⚠️ 案まで）
- `survey-plan.md` / `questions-batch-1.md` / `resume-0150.md`

### 段 2 で変更するファイル
- `docs/references.md`（append-only）・`docs/literature/<日付>-<topic>.md`（新規カード）・`docs/literature/_index.md`（追記）
- ⚠️ それ以外の `docs/`・ADR・事前登録・実装は変更しない（研究者判断 1 と別トラックの規約）

## 影響範囲

- タスク 2（`.steering/20260914-mhd-feature-offline-tiers/`）の issue 004 / 006 の定義と、ADR-030 の補訂（段 3）。
- 段 3（SSOT 昇格）の入力: J-1 / J-3 / J-4 / J-5 / J-13 / J-15 の反映先（`decisions.md` 判断 1）。

## 既存パターンとの整合性

- 判定語（保持・統合・縮小・棄却）は別トラック `design.md` Workstream D と同じ。
- 段 2 は `literature-review` / `citation-ssot` / `literature-card` の規約どおり（append-only・恒久 ID・DOI 重複検査）。

## テスト戦略

- 実装変更は無い。代わりに: 禁止用語の実検査（草案 17 本）／ `scripts/check_citations.py` を「違反なし」まで／サブエージェント報告の一次検算。

## ロールバック計画

- 段 1 は本ディレクトリ内だけなので、ディレクトリを戻せば消える。段 2 はラウンドごとのコミットを `git revert` する（⚠️ `references.md` は append-only なので取り消しは tombstone で行う）。
