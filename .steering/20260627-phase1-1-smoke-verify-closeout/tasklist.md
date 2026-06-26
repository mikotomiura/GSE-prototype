# タスクリスト

## 機械的検証（Claude）
- [x] `cargo test --lib` … pass
- [x] `gse-replay --snapshot` … pass（HMM 不変）
- [x] `tsc --noEmit` … pass

## advice.md 回答
- [x] issue 1: dev/被験者で初期 Dashboard 不変 → 設計通り（VITE_GSE_DEBUG gate のみ差分）と確認
- [x] issue 2: 起動方法 → codex consult → A＋C 推奨を文書化（`launch-method-decision.md`）
- [x] issue 3: 事後アンケート GAS → `buildF5` 実装済みと確認（新規作成不要）

## 成果物
- [x] `smoke-test-runbook.md`（研究者向け実機手順）
- [x] `launch-method-decision.md`（起動方法の推奨＋codex 盲点）
- [x] `design.md` / `requirement.md`

## ユーザー判断待ち（このタスクで決め切らない）
- [ ] 起動方法 A＋C を確定するか
- [ ] codex follow-up（first-run self-check / ログ堅牢化）を Phase1 前か Phase2 か
- [ ] 研究者: 実機スモーク（runbook）＋ GAS 実機確認（`buildAllSupportForms`）の実施

## 注意
- diff に未関係な未ステージ変更（budget.json/scripts/docs削除/MEMO/advice.md）を混ぜない。
  本タスク成果物は `.steering/20260627-.../` のみ。
