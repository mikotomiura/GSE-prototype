# タスクリスト

## 準備
- [x] `preregistration.md §2.2 / §2.11 / §2.12 / §2.13 / §2.14` を読む
- [x] `materials/topic01_hi.md` / `_lo.md` と `materials/README.md` で HI/LO の操作を確認
- [x] `writing-pad.html` / `build_task_pages.py` / `protocol.md §1.2b / §4b.2` を読む
- [x] `lib.rs` のブロック自動終了スレッドと順序保証を確認
- [x] 影響範囲を grep で洗い出し（事前開示に触れるファイル一覧）

## 実装
- [x] `writing-pad.html` — ゲート（開始前は課題文・記入欄・文字数を出さない）
- [x] `writing-pad.html` — `setTimeout(timeIsUp, BLOCK_MS)` を `startBlock()` の中へ移す
- [x] `writing-pad.html` — 注意書きを書き換え（開いても始まらない／開き直せば戻る）
- [x] `build_task_pages.py` — `promise_check` に「開始の約束」を追加
- [x] `build_task_pages.py --selftest` — ゲートの存在と空回り検査を追加
- [x] `GSE_G1_Form_Builder.gs` — 受付メール本文（事前に読む記述を削除）
- [x] `GSE_G1_Form_Builder.gs` — 事前資料メール本文・件名
- [x] `GSE_G1_Form_Builder.gs` — `Q_S_PREREAD` / `Q_S_PREREAD_NOTE` の文言
- [x] `scripts/check_g1_emails.py` — 検査基準の更新＋「事前に読んでよい」系が残らない検査を追加
- [x] `Form_G1/materials_autosend_test.cjs` — 期待値の更新

## 凍結文書の改訂
- [x] `preregistration.md` — 第 11 版の改訂履歴（⚠️ **向き (a)(b) を両方**書く）
- [x] `preregistration.md §2.12` — 宣言の書き換え（事前開示の撤回）
- [x] `preregistration.md §2.12-3 / §2.12-6` — 残す（根拠を「手元に HTML がある」に付け替え）
- [x] `preregistration.md §2.12-4` — 残す（記録する内容を「ボタンを押して見たか」に）
- [x] `preregistration.md §2.13` — ゲートで先読み防止が部分的に戻ったことを訂正
- [x] `protocol.md §1.2 の表 / §1.2b / §4b.2` — 手順の更新
- [x] `participant-guide.md` — 事前に読む前提の記述
- [x] `consent.md` / `debrief.md` — 波及の有無を確認

## テスト
- [x] `python3 build_task_pages.py --selftest` 緑
- [x] `python3 scripts/check_g1_emails.py` 緑
- [x] `node Form_G1/materials_autosend_test.cjs` 緑
- [x] `bash run.sh` 緑
- [x] ⚠️ `git diff` で `§3.1/§3.2/§3.4/§3.5/§3.6` が無変更であることを確認
- [x] ブラウザで `block02.html` を開いて実地確認（押す前に読めない／押すと同時に出る）

## レビュー
- [ ] `code-reviewer` + `security-checker` を並列起動
- [ ] `/cross-review`（Codex 独立レビュー）
- [ ] HIGH 指摘への対応

## ドキュメント
- [x] `pages/` を再生成し `dist/_drive/` と差分確認
- [ ] 次セッター向け引き継ぎ（Drive 差し替え・GAS 再配備・G1-S 再構築）

## 完了処理
- [x] `design.md` の最終化
- [x] `decisions.md` の記録
- [ ] git commit
