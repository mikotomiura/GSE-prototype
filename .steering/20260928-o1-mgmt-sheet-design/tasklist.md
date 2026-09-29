# tasklist — o1-mgmt-sheet-design

- [x] 途絶タブを状況ボードに（台帳）
- [x] 受領台帳・登録ログ・却下ログの書式（条件付き書式・値は不変）
- [x] テスト: 台帳 229・ビルダー 229 緑
- [x] 変異検査: 台帳 90/90・ビルダー 70/70
- [x] 目視（実コードの出力を HTML に描いて Chrome で確認）→ 2 点修正
- [x] code-reviewer ＋ security-checker（反映済み）。⚠️ Codex は予算ゲートで skip（decisions）
- [x] コミット → PR → CI → merge（PR #257・`7ae41eba`・Windows の check は再実行で緑）
- [x] 研究者: 配備（2026-09-29）・`o1LedgerRun()` で途絶タブに P999 が「正常」で載ることを確認
- [ ] 研究者: 実シートの見た目（文字の切れ・色）の目視 ／ Codex の事後レビュー（予算で skip した分）
