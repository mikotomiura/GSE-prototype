# 単位 g: CORE-CS 評価契約の改訂

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **g**。

## 背景と入力

- 評価契約群（pre-SSOT）は `.steering/20260916-gse-theory-operationalization-review/` にある。前段のレビュー（`review-D.md` D-07〜D-10・D-16）が、CORE-CS の `T_stop` に載せる処理が現行 GSE に無いこと（構成不能な陽性対照）・`t0` の記号衝突・BRIDGE-DN の統合候補を指摘した。
- 研究者判断: J-3（`T_stop` を実在する処理から取る）・J-9（終端の弁別は解除 vs 断だけ）・J-6（BRIDGE-DN を CORE-CS の比較節へ統合・Digital Nature は補足で回す）・J-16（研究対照は別計器に閉じる）・J-4（ADR-033）・機械的な規則（CORE-CS の `t0` → `t_stop`）。

## ゴール

- `core-cs-evaluation-contract.md` に上の裁定を当て、Digital Nature の比較節（§16）を足す。旧 BRIDGE-DN 契約と命題カバレッジ行列に統合の注記を足す。

## スコープ

### 含むもの
- `core-cs-evaluation-contract.md`・`bridge-dn-evaluation-contract.md`・`core-proposition-coverage-matrix.md`（いずれも `.steering/20260916-…/`）
### 含まないもの
- ⚠️ レビューの提案（保持・縮小など）を当てること・`docs/` の変更・§15 の文献の登録

## 受け入れ条件

- [ ] 裁定事項と機械的な規則だけを当てている（冒頭に一覧）
- [ ] `T_stop` の候補が一次（ADR-033・ADR-008 D1・ADR-027 D5）と一致する
- [ ] Digital Nature の比較節が DN カードの「書いてよいこと / いけないこと」を守る
- [ ] `/cross-review` 2 巡（⚠️ Codex の日次予算の都合で Claude 単独になりうる）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 研究者の裁定を契約へ写す作業である
