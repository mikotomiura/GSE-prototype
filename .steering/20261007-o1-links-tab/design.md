# 設計

## アプローチ
G1 の `buildLinksTab_` に倣い、O1 の運営シート（`O1_MGMT_SHEET_ID`）に「O1 リンク集」タブを置く。

- `o1LinksRows_(props, cfg, manual)`: 行を作るだけ（表に触れない）。全セルを `o1PlainText_` で数式から倒す。
- `o1ReadLinksManual_(sheet)`: 手で入れる欄（`O1_LINKS_MANUAL` の 3 項目）の値を**項目名で**拾う。
- `o1BuildLinksTab_(ss)`: 「参加者ロスター」タブを持つ表なら止める → 手入力の値を拾う → `clear` → `setValues` → 見た目。
- `refreshO1LinksTab()`（公開）: `o1MgmtConfigProblem_` で止める → リンク集だけ作り直す。
- `buildO1MgmtSheet()` からも呼ぶ（⚠️ 失敗してもログのタブの用意は止めない＝ try/catch でログ）。

## 書かないもの
参加者ロスターの ID・URL（名前で指すだけ）・氏名・メール・提出の受け口と秘密。

## 変更対象
- `Form_O1/GSE_O1_Form_Builder.gs`（本体・冒頭の配備手順に 5b）
- `Form_O1/o1_form_builder_test.cjs`（§18 の 12 ケース・偽シートに `clear` / `setValues`・下限 215 → 235）
- `Form_O1/o1_form_builder_mutation_test.sh`（リンク集の変異 6 件）

## テスト
- `node Form_O1/o1_form_builder_test.cjs` → 241 ケース
- `bash Form_O1/o1_form_builder_mutation_test.sh` → 76 件すべて赤
- `bash scripts/check-o1-release-readiness.sh` → 24/24
