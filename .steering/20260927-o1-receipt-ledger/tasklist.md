# タスクリスト

## 準備
- [x] 引き継ぎを読み、状態を測り直す（main・CI・タグ・ゲート 2 本）
- [x] 一次資料（受け口・ビルダー・Rust の日番号・登録ログ・ゲート）を読む
- [x] grill（置き場所・出力先・未受領・日数）→ decisions.md

## T1 実装
- [x] `Form_O1/GSE_O1_Ledger.gs`
- [x] `Form_O1/o1_ledger_test.cjs`（116 ケース緑）
- [x] `Form_O1/o1_ledger_mutation_test.sh`（42 変異すべて赤・`VERBOSE=1` で赤の理由も確認）
- [x] ゲートへ配線（テスト実行・直書き走査・selftest fixture）／`.gitignore` ホワイトリスト
- [x] glossary
- [ ] ゲートの selftest が壊れていないか確認（`--selftest` 相当）

## T3 設計
- [x] `t3-person-ledger-design.md`

## T2 記録票 A の実測（★ 研究者の承認が先）
- [ ] 研究者の承認（Chrome で G1 の Apps Script の読み取り専用関数を 1 本実行）
- [ ] `browser-verification` を読み、`checkConsentFormParity` を実行 → ✅/❌ を記録票 A の下書きに
- [ ] `consent.md` ⇔ `consentItemTitles_()` の突合（別に）

## レビュー（作業ツリーを変えない）
- [ ] code-reviewer ＋ security-checker（並列・model 明示・範囲/禁止/締切つき）
- [ ] HIGH 指摘への対応（一次で確かめてから）
- [ ] `/cross-review`（Codex・縮退したら理由を明記）

## 完了処理
- [ ] `/finish-task`（テスト・コミット・push → PR → CI 緑なら merge）
- [ ] 研究者待ちの一覧を報告（配備・記録票 B/C・裁定事項）
