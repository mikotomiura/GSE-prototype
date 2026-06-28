# タスク

- [x] reveal_in_file_manager ヘルパ追加 (win/mac/linux)
- [x] 成功メッセージにパス強調 + OneDrive/iCloud 注意書き
- [x] 生成後に reveal 呼び出し
- [x] cargo build --features package --bin gse-submit
- [x] 手動 reveal 動作確認 (mac)
- [x] レビュー / コミット

## 追補: 参加者ID の対話入力 (ファイル名 Pxxx 崩れ対策)
- [x] prompt_participant_id ヘルパ (デフォルト/検証/リトライ/EOFフォールバック)
- [x] 自動生成ID (P+12hex) 判定 → デフォルトに採用しない
- [x] env (GSE_PARTICIPANT_ID/GSE_PID) 経路はプロンプト省略
- [x] run() でラベルIDを入力値に、入力探索は従来通り
- [x] cargo build (mac) + 隔離スモーク (Enter/誤入力/正常)
