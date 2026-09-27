# タスクリスト

## 準備
- [x] 引き継ぎを読み、状態を測り直す（main・CI・タグ・ゲート 2 本）
- [x] 一次資料（受け口・ビルダー・Rust の日番号・登録ログ・ゲート）を読む
- [x] grill（置き場所・出力先・未受領・日数）→ decisions.md

## T1 実装
- [x] `Form_O1/GSE_O1_Ledger.gs`
- [x] `Form_O1/o1_ledger_test.cjs`（164 ケース緑）
- [x] `Form_O1/o1_ledger_mutation_test.sh`（62 変異すべて赤・`VERBOSE=1` で赤の理由も確認）
- [x] ゲートへ配線（テスト実行・直書き走査・selftest fixture）／`.gitignore` ホワイトリスト
- [x] glossary
- [x] ゲートの selftest（63/0）

## T3 設計
- [x] `t3-person-ledger-design.md`

## T2 記録票 A の実測（★ 研究者の承認が先）
- [x] 研究者の承認（AskUserQuestion）・Chrome 前面化・セレクタは研究者が選択（私は押す前に DOM と画面で確認）
- [x] `checkConsentFormParity` を実行 → ✅ 一致（8 件）→ `t2-record-a-draft.md`（記録票への記入は研究者）
- [x] `consent.md` ⇔ コードの突合（語は両側に実在・言い回しと第 8 項目は逐語一致でない → 研究者判断）

## レビュー（作業ツリーを変えない）
- [x] 1 回目: code-reviewer ＋ security-checker ＋ cross-reviewer（並列）→ 指摘を一次で確かめて反映（decisions 判断 8〜13）
- [x] 2 回目: code-reviewer ＋ security-checker ＋ cross-reviewer（Codex 実行成功・テストファイルは除外）→ 判断 14〜22 で反映・見送りは理由つきで decisions.md へ

## 完了処理
- [ ] `/finish-task`（テスト・コミット・push → PR → CI 緑なら merge）
- [ ] 研究者待ちの一覧を報告（配備・記録票 B/C・裁定事項）
