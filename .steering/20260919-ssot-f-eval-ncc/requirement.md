# 単位 f: EVAL-NCC を既存トラックへ接続し直す

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **f**。

## 背景と入力

- 前段のレビュー（`review-D.md` D-21〜D-27・衝突 X-01 / X-03 / X-04）: EVAL-NCC の転帰語彙（再開・再停止・外部化・離脱）は ADR-029 D5 が却下した第三語彙の再導入であり、「受容 = W0 内の明示選択」は SSOT の行動定義（ADR-018 D5）と食い違い、「coupling as primary outcome」は ADR-023 の名だけを借りている。
- 研究者判断 J-13（理論レビュー 判断 1 #7）: 転帰は ADR-023 / 024 / 029 に接続し直す。「受容」は SSOT の行動定義。明示の受諾・保留・拒否の記録は別計器の実験（EH3 / EH4）のみ。「coupling as primary outcome」の名の流用をやめる。再開 / 再停止は定義案 §3.3 の置き換え案。＋ J-10（再停止は条件 A の辺）・J-16（研究対照は別計器）・J-7（GR-H11 の保留）・J-15（受容率を成功指標にしない）。

## ゴール

- 分析契約・DAG・測定辞書・反証表・理論 A の該当箇所に、上の裁定を当てる。

## スコープ

### 含むもの
- `.steering/20260916-gse-theory-operationalization-review/{eval-ncc-analysis-contract,eval-ncc-dag,measurement-dictionary,gr-h4-h9-h11-h12-falsification-table}.md`・`docs/theory/theory-architecture-and-roadmap.md`（coupling の名の 1 か所）
### 含まないもの
- ⚠️ レビューの提案を当てること・既存尺度への置き換え（S6b）・マージンや標本数の確定

## 受け入れ条件

- [ ] 転帰の語彙が ADR-029（`externalized` / `left_observation` / 打ち切り）と ADR-030 補訂 1（`r` / `s'`）に一致する
- [ ] 「受容」と「明示の受諾」を呼び分けている
- [ ] 研究対照を別計器に閉じると書いている
- [ ] `/cross-review` 2 巡（⚠️ Claude 単独になりうる）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 研究者の裁定を契約へ写す作業である
