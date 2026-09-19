# タスクリスト

## 準備
- [x] ADR-030 を全文読む（993 行）
- [x] 補訂案・判断 25 / 26・起票 11〜15 / 19・S7 / S8 カード・ADR-032 D9 を読む
- [x] 一次で確認: `stall_onset.rs`（観測区間・不応期）／ `RecordingControls.tsx`（分単位）／ `lib.rs` `delete_time_range` ／ `hook_macos.rs`（修飾キーの行が届かない）／ `schema_dto.rs`（`ime_shadow` の doc）

## 実装
- [x] ADR-030 末尾に補訂 1 節（項目 1〜5・7〜9 ＋ 項目 6 は保留）
- [x] 冒頭と D7 に参照を 1 行ずつ
- [x] README の ADR-030 行

## テスト
- [x] `check_citations.py` 違反なし
- [x] 禁止用語の規則を補訂節に当てて 0 件

## レビュー
- [ ] `/cross-review` 1 巡目（自文書と他文書の矛盾）
- [ ] `/cross-review` 2 巡目（足した規則の境界条件）
- [ ] 指摘の採否を `decisions.md` に記録

## 完了処理
- [ ] git commit
