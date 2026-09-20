# タスクリスト

## 準備
- [x] `ADR-032` を**全文通読**（D2 / D5 / D6 / D9 / M7 / M11 / §Consequences）
- [x] 判断 4 / 判断 5 / 判断 25 #16 を読む
- [x] ⚠️ 起票 6 の**一次の所在を特定**（★ 引継ぎメモの参照先は誤りだった）
- [x] 起票 7 / 起票 19 / 起票 21 を読む
- [x] `schema/current.json` の行種を機械列挙（22 行種）
- [x] `feat_offline/` の実装フィールドを列挙（7 モジュール）
- [x] fixture を数え直す（★ **15 本**・すべて合成）

## 実測
- [x] `gse-replay --features` を 6 本に当てて Tier 別の非 null 率を取る
- [x] ⚠️ `ime_shadow` を持つ fixture が **1 本 2 行だけ**であることを確認
- [x] ⚠️ `phase1_ime_heavy` が **rows=0** を返すことを確認（★ feat 行だけでは作れない）
- [x] ★ Escape / Backspace / Space が両 OS で `key` 行に出ることを一次で確認
- [x] ★ macOS の状態機械が Backspace でセッションを閉じないことを確認
- [x] ★ `replay` の `key` DTO が `vk` / `category` **両対応**であることを確認

## 文書
- [x] `docs/architecture/offline-replay-capability-matrix.md` を作成
- [x] ⚠️ 3 層（W / M-off / M-on）に分け、**層を識別できない**ことを明記
- [x] 9 候補すべてに 3 値判定
- [x] `要再判定` を 6 件明示
- [x] `check_citations.py` / `check_doc_lexicon.py` が緑

## 裁定（★ 表が閉じたら）
- [ ] ADR-032 未決 ④（IME content-free 状態機械）
- [ ] ADR-032 未決 ⑤（`esc_count`）
- [ ] M11 / 起票 21（単独キー用の門）
- [ ] ⚠️ ライブ変換の層識別子を記録するかの検討（★ 起票する）

## レビュー
- [ ] `code-reviewer` ＋ `security-checker`（並列・opus）
- [ ] `/cross-review` 2 巡

## 完了処理
- [ ] decisions.md
- [ ] git commit
