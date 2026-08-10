# タスクリスト

## 準備
- [x] grill 2 問で確定（P010 を含める / 承認は実施前）
- [x] requirement.md / decisions.md

## 実装
- [x] `config.json`: roster 移動・`status`・`revision` 16・`v16_changes`（違反を先に書く）
- [x] `analyze.py`: `PREREG_REVISION` 16
- [x] `preregistration.md` 第 16 版（違反 → 緩和 → 実施条件の訂正 → 代償 → P-S 条項を残す）
- [x] 第 15 版の 3 箇所に撤回/訂正の印（★ 本文は消さない）
- [x] `notes.md` / `data.md` の実態反映

## テスト
- [x] `analyze.py --selftest` / `validate_blocks.py --selftest` 緑（第 15 版の境界検査が無傷）
- [x] 版 3 点一致（16）
- [x] ★ 実データ: 「確証標本が **1 名**で n=3 未達」で停止（第 15 版は「0 名」だった）
- [x] ⚠️★ 壊して赤: `n_subjects=1` で roster ゲートを通過し `§3.10` で止まる
- [x] `bash run.sh` GREEN

## ドキュメント
- [x] 引き継ぎを書き直し `next-session-prompt-p010-confirmatory-records.md` に改名

## レビュー
- [x] `/cross-review` 実施（Codex 47,462 tokens）。★ 4 件に対応:
      HIGH=§2.4 本文の訂正漏れ（P010 は含まないが残っていた）/ HIGH=block07 感度分析の事前登録 /
      MEDIUM=承認の立証水準が非対称（検証不能と明記）/ MEDIUM=「results/ が空」は状況証拠

## 完了処理
- [x] `/finish-task`（schema 非 touch で skip）
- [ ] コミット → push → PR → merge

## ★ 次にやること（別タスク）
- **P010 のフォーム回収**（`produced_chars` 10 件 / 操作チェック 7 件）★ 確証標本なので**必須**になった
- ⚠️ 記録用紙と `file` 列の突き合わせ（`notes.md §10-5`）★ 同上
- ⚠️ `gse-app.log` 回収（版の特定 / block07 で参加者が見た画面）
- **確証標本 残り 2 名**の募集・実施
