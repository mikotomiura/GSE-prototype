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
- [x] ADR-032 未決 ④ → **ADR-036 D1**（schema を足さない）
- [x] ADR-032 未決 ⑤ → **ADR-036 D2**（派生量として定義・schema 不変）
- [x] M11 / 起票 21 → **ADR-036 D3 / D4**（門を定義し、1 件目を通してみせた）
- [x] ⚠️ ライブ変換の層識別子 → **起票 24**（`20260914-instrument-change-arbitration`）

## レビュー
- [x] `code-reviewer` ＋ `security-checker`（並列・opus）
- [x] ⚠️★★★ **HIGH 対応 5 件**（★ 2 人が**独立に同じ穴**を指摘した 1 件を含む）:
      門と派生量の切り分け（判断 8）／ `s-i` にポインタ結合禁止を戻す ／
      `ime_shadow.t` の macOS 記述を訂正（判断 9-1）／ `s-vii` 後半の取りこぼし（判断 9-2）／
      `esc_count` の OS 間比較を凍結
- [x] MEDIUM 対応: 条件数 10 / `meta` のキー数の限定語 / 同意逐語の裏取り（判断 10）/ 出力先を M4 へ
- [x] LOW 対応: D5 の表は 2 行である旨 / `feat_offline` は mod.rs 除き 7
- [ ] `/cross-review` 2 巡

## 完了処理
- [x] decisions.md
- [ ] git commit
