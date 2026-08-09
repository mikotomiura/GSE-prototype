# タスクリスト

## 【A】G1-M / G1-S の導線（最優先）

- [x] A-1 `g1FormLink_()` を足す（短縮 → publishedUrl → 構築 URL の 3 段）
      ★ 3 段目が匿名で開けることを `curl`（Cookie 無し）で実測
- [x] A-2 受付メールに「■ ご回答いただくフォームは 3 つです」を足す（★ 両分岐共通）
- [x] A-3 `check_g1_emails.py` に不変条件を足す（★ 13 変異すべて赤を実測）
- [x] A-4 `python3 scripts/check_g1_emails.py` が緑
- [x] A-5 GAS を貼り直し → `previewRegisterAckEmail()` で実物を目視
      ★ 本番の本文に x.gd 4 本（アプリ / 課題ページ / G1-M / G1-S）・生の forms URL は 0
- [x] A-6 `participant-guide.md` §3b/§4 に「リンクは受付メールの (2)/(3)」を追記

## 【B】管理シート

- [x] B-1 `RUN_HEADER` を第 13 版に合わせる（削除 2 / 改名 2 / 追加 1 → 19 列）
- [x] B-2 `migrateRunSheetToV14()`（冪等・値を捨てない・最後に assert）
- [x] B-3 `applyRunValidation_` の選択肢を更新（実施形態・G1モード確認）
- [x] B-4 `refreshG1RunSheet` が `配布URL(短縮)` を埋める（実シートで `x.gd/ShrIJx` を確認）
- [x] B-5 レイアウト（バナー / ネイビーヘッダ / 2 行＋1 列固定 / 交互背景 / 幅 / 条件付き書式）
- [x] B-6 `Form_G1/README.md` の列名と移行手順を追随
- [x] B-7 実シートで移行を実行し、ヘッダ一致と見た目を目視
      ★ P009 の値が正しい列に残り、`実施形態` が「在宅（初回起動のみ同席）」に置換された
- [x] B-8 ⚠️ 実配備で出た 2 件を直した（結合と固定の衝突 / 6 分タイムアウト）+ 偽シートに制約を実装

## 【C】残りの検証と後片付け

- [x] C-1 `blockNN.html` を **`file://` ＋ 実マウス**で検証（Playwright・trusted event）
      ★ 押す前は課題も記入欄も出ない / 実クリックで出る / 実キー入力と文字数カウンタが動く
      （16 項目すべて緑・前後のスクリーンショットで目視）
- [ ] C-2 ⚠️ **未実施**: Windows 新品端末での初回起動（`windows-verification.md §3`）
- [ ] C-3 ⚠️ **未実施（研究者の判断待ち）**: 端末に残るテスト状態
      `~/.gse/g1_participant_id`（= `P009`）/ `~/Desktop/G1_実施用_macOS` / 受け取りフォルダのテスト `.age`
      ★ 消してよいか分からないので**触っていない**
