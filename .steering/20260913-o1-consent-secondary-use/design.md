# 設計

## 実装アプローチ

★ **同意文書（上流の雛形）→ フォーム（正本）→ 検査 → ゲート → 台帳** の順で、
**同じ 1 つの約束を 4 か所に同時に通す**。⚠️ 片方だけ直すと `o1_form_builder_test.cjs` が赤になる。

⚠️★★★ **`clearForm()` 系を撃たない**（★ 2026-08-07 に G1-C の全設問が消えた事故）。
→ ★ 追加経路は `migrateO1ConsentForm()`。

## 変更対象

### 修正するファイル

| ファイル | 何を変えるか |
|---|---|
| `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md` | ★ §3 末尾（「この研究で作られるもの」の下）に**任意項目の節**を追加 |
| `Form_O1/GSE_O1_Form_Builder.gs` | ★ `Q_O1_SECONDARY_USE` 定数 / `o1ConsentOptionalItemTitles_()` / `o1ConsentSecondaryUseHelp_()` / `o1AddOptionalConsentItem_()` / `o1AddOptionalConsentSection_()` / `o1SecondaryUseNote_()` / `buildO1ConsentForm` ・ `migrateO1ConsentForm` の配線 / `o1ConsentAnswers_` の `secondaryUse` / `o1FinishO1Registration_` の note 連結。⚠️★ **`o1ConsentFormDescription_`（フォーム本文）は触らない** —— ★ 本文は *必須の同意* の説明であり、⚠️ そこへ任意の用途を書くと「上記すべてに同意し…」の射程が曖昧になる。→ ★ 任意の内容は**専用セクション＋設問の補足に閉じる**（＝ 構造で「別物」を示す） |
| `Form_O1/o1_form_builder_test.cjs` | ★ §6 の「すべて必須」を**必須群/任意群に分割** / §8 migrate の期待値 / **新 §6b**（任意項目の性質・1 対 1・固有名の不在）/ §13 の note 検査 |
| `scripts/check-o1-release-readiness.sh` | ★ 検査 1 本追加（§1 同意文書の節 ＋ §4 ビルダーの任意項目）と **selftest 3 状態** |
| `docs/o1-deletion-ledger.md` | ★ §2 に**撤回経路**、§5b に **fail-closed 規則**と A-13 の意味の追記 |

### 新規作成するファイル
- なし（★ `.steering/20260913-o1-consent-secondary-use/` の記録のみ）

### 削除するファイル
- なし（⚠️ **既存の同意項目は 1 つも消さない**）

## 影響範囲

| 影響先 | 対処 |
|---|---|
| ⚠️ 既存の O1-C 配備済みフォーム | ★ `migrateO1ConsentForm()` が末尾に 1 問足す。⚠️ **既存回答者は未回答＝不同意**（fail-closed） |
| ⚠️ 登録ログの備考欄 | ★ `2nd-use: yes|no` を連結。⚠️ 許可リスト `O1_MGMT_NOTE_ALLOWED` を通ることを検査で担保 |
| ⚠️ 削除経路 | ★ **増えない**（A-13 が既に登録ログを覆っている）。⚠️ 撤回の手順だけ台帳に足す |
| ★ 配布ゲート | ⚠️ **未達が 1 件増える可能性**（★ 実装するので緑のはず。⚠️ 赤なら中身を読む。**検査を緩めない**） |

## 既存パターンとの整合性

- ★ 定数は `Q_O1_*` の命名に合わせる（`GSE_O1_Form_Builder.gs:231-235`）。
- ★ 検査は `push("§n ...", 条件, 詳細)` の形（`o1_form_builder_test.cjs`）。
- ★ ゲートは `ok()` / `ng()` ＋ `expect_red` / `expect_green` の変異試験（`check-o1-release-readiness.sh`）。
- ★ 被験者向け文言は**平易な日本語・敬体**、`★` / `⚠️` の記法を周囲に揃える。

## テスト戦略

- **単体（node）**: `node Form_O1/o1_form_builder_test.cjs` — ★ 既存 221 ケース ＋ 追加分が全緑。
  ★ 追加で測るもの:
  1. 任意項目が**存在し、`__required === false`**
  2. **必須の一括同意は依然として必須**（★ 混ざっていない）
  3. 任意項目が**必須群より後**に置かれている
  4. `.md` に対応する節がある（**1 対 1**）
  5. ⚠️ 被験者向け文言に**固有名（Portrait / 肖像）が無い**
  6. `o1ConsentAnswers_` の**往復**（チェック有 → `true` / チェック無 → `false` / **項目不在 → `false`**）
  7. `migrate` が任意項目も足し、**2 回目は 0**（冪等）／⚠️ **既存項目を 1 つも消さない**
  8. 登録ログの備考に `2nd-use: yes|no` が入り、⚠️ **`***` に潰されていない**
- **ゲート（bash）**: `bash scripts/check-o1-release-readiness.sh` が **19 緑を維持**し、
  `--selftest` で新検査が **3 状態**（在る＝緑 / 無い＝赤 / 壊れている＝赤）に反応する。
- **禁止用語**: `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0。
- ⚠️ **実機（GAS）配備は行わない** — ★ 研究者が手で行う。本セッションはコードと文言まで。

## ロールバック計画

★ 変更は 1 コミットに閉じる（`docs(consent): ...`）。⚠️ 配備していないので `git revert` で完全に戻る。
★ 既に `migrateO1ConsentForm()` を実行してしまった場合は**フォーム側に 1 問残る** ——
⚠️ **消さずに放置してよい**（★ 任意項目なので回答を強制せず、未回答は不同意に落ちる）。
