# タスクリスト

- [x] 検査 5 を check_doc_lexicon.py に足す
- [x] 直す前に赤（3 件）を見る
- [x] Dashboard.tsx・App.tsx の文を直す
- [x] functional-design.md:249 の注を直す
- [x] 検査が緑・tsc が緑
- [x] 画面で文を見る
- [x] code-reviewer・security-checker・/cross-review（判断 4・5）
- [ ] コミット（push と PR は研究者の手元で）

## 場面ごとに使うもの

- コードの変更 → code-reviewer＋security-checker（並列）＋/cross-review
- 被験者向けの文 → typescript-standards・data-privacy（文の契約）

## 記録（2026-11-05）

- 直す前の検査: 3 件（App.tsx:118・Dashboard.tsx:492・493）で exit 1。コメント中の語・英語のラベルは拾わなかった。
- 直した後: exit 0。`npx tsc --noEmit` rc=0。
- 画面: `http://127.0.0.1` の vite 開発サーバーで、Tauri の shim を先に入れた一時のページ（検証の後に消した）から実のスタイルシートで実マウントした。O1 のモードの注意書き・O1 以外のスタート画面の週の説明・較正のモードの注意書きの 3 か所が新しい文で、本文に Flow・Incubation・Stuck・推定状態は 0 件。注意書きの文字色 rgb(248,250,252) は暗い地の上で読める。配布のバイナリでは確かめていない。
