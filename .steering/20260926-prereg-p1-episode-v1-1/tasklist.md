# タスクリスト

- [x] 一次の読み込み（凍結文書全文・凍結 JSON・ADR-030 補訂 2 全文・前タスク判断 15/16/19/25〜29・起票表・parity 検査・v0.3 の前例）
- [x] grill（判断 1〜4 を研究者が裁定）・requirement / design / decisions
- [x] v1.1 改訂宣言ブロックを挿入する
- [x] 検証 4 本（parity / self-test / src-tauri 不変 / 削除行 0）
- [x] `/cross-review`（Codex gpt-6-astra・パス限定）と是正
- [x] `/finish-task` → 出荷フロー（push → PR → CI 緑なら merge → main の CI）

## 完了時の記録
- `/cross-review` 2 巡（1 巡目: Codex ＋ code-reviewer・2 巡目: Codex で是正コミットだけ）。HIGH／両系統一致の指摘は是正済み（decisions 判断 6・7）
- security-checker・test-runner は起動しなかった: 変更はドキュメントと `.steering/` だけで、コード・外部入力・データ保存に触れない（`git diff main -- src-tauri/` は空）
- schema parity check: skip（schema を触っていない）／ `check_prereg_parity.py` と `--self-test` は exit 0
