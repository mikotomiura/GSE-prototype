# タスクリスト: clearForm 安全ガード

- [x] 定数 `ALLOW_CLEAR_WITH_RESPONSES = false` を追加(CLEAR_EXISTING 直後) → L33
- [x] ヘルパ `assertClearableForm_(form, key)` を追加(clearForm 直前, fail-closed) → L2141
- [x] `buildForm` に配線("F1") → L181
- [x] `buildF2` に配線("F2") → L434
- [x] `buildF4` に配線("F4") → L659
- [x] `buildF5` に配線("F5") → L760
- [x] JS 構文チェック(node --check、.js コピーで parse 通過)
- [x] 机上ロジック確認(n>0→中断 / n==0→通常 / 例外→中断)
- [ ] cross-review(/finish-task Step 3) ※任意・小差分のため要否をユーザー確認
- [ ] コミット(fix(form): ...) ※ユーザー承認待ち
- [ ] Apps Script エディタへ貼り付け(研究者手動) ← これをしないとガードは効かない

## 関連 restart 前提(このタスク外・別途)
- [ ] restart 手順(回答クリーンアップ + ロスター初期化 + 被験者連絡)
- [ ] M0 tooling 修正(較正収量/提出)の完了確認
- [ ] restart 日(木曜)の可否判断
