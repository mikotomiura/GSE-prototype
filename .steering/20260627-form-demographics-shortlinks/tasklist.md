# タスクリスト: F2 属性設問 ＋ 短縮URL反映

## 実装（エージェント・完了）
- [x] 短縮URLが全て viewform（回答用）であることを WebFetch で検証
- [x] SHORT_URL_F1/F2/F4/F5 定数を追加
- [x] DROPBOX_FILE_REQUEST_URL を短縮版 x.gd/PHtwA に（リダイレクト先＝現行と同一）
- [x] メール本文(onF1Submit)の F2/F4/F5 を短縮URL優先＋動的取得フォールバックに
- [x] F2-A 先頭に年代・職業（単一選択・必須）を追加
- [x] node --check で構文 parse 成功
- [x] git diff が対象4箇所のみ・無関係変更なしを確認

## ユーザー確認（実機・Apps Script）
- [ ] 最新 .gs を Apps Script エディタへ貼り直す
- [ ] buildF2 を再実行 → F2-A 先頭に「年代」「ご職業」が出る／既存 a1/a2/a3・GSE-10・TSE は不変
- [ ] onF1Submit ドライラン → 受信メールの F2/F4/F5 リンクが x.gd 短縮、Dropbox も x.gd/PHtwA
- [ ] （任意）短縮URLをクリックして各 viewform に飛ぶことを確認

## 追加実装（APP_DOWNLOAD_INFO 確定・2026-06-27）
- [x] 配布チャネル確定（Google Drive 閲覧専用・private repo 回避）→ findings F-1（pilot-smoke-verify）
- [x] APP_DOWNLOAD_INFO を Drive 短縮URL(x.gd/6crxj)+OS別ファイル名+同梱明記に
- [x] PUBKEY_SOURCE_INFO を「配布フォルダ同梱・全員共通」に
- [x] メール本文の重複「3点」補足行を削除
- [x] node --check 構文OK / メモリ build-ci-and-pilot-distribution 更新

## 備考
- SHORT_URL_F1 は現状メール本文未使用（募集・公開リンク集用に定数化して保持）。
- 公開リンク集シート(18vs0qbEa...)への短縮URL転記は手動運用（.gs 生成外）。
- 残課題 F-1（APP_DOWNLOAD_INFO プレースホルダ）は pilot-smoke-verify/findings.md 参照。本タスクとは独立。
