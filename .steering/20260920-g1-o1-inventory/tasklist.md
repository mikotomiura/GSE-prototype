# タスクリスト — G1 / O1 の残タスクの棚卸し

## 準備
- [x] `.steering/_handoff/next-session-g1-o1-inventory.md` を読む
- [x] 前段の一次（`.steering/20260920-decision4-reflection/decisions.md` 判断 8）を読む
- [x] grill: 範囲を研究者と確定（棚卸し ＋ 機械的修正 ＋ マージ計画 ＋ 検査の追加）
- [ ] 一次確認 4 本（G1 / O1・ADR-034 / マージ・schema / Q3・Q4 の材料）の結果を受け取る

## 棚卸し
- [ ] `inventory.md` を作る（行ごとに 根拠 = ファイル:行 or コマンド＋終了コード）
- [ ] 各行を [研究者] / [機械] / [ゲート] に分類
- [ ] 引き継ぎの「未検証メモ」と実測の食い違いを明示（★ 古い記述は一次へ戻す）

## 研究者の判断
- [ ] Q1（前提条件 7 の範囲）を一次つきで提示 → `decisions.md`
- [ ] Q2（「G1 の最初の配布」＋ Migration 3）→ `decisions.md`
- [ ] Q3（「テストの中の陽性対照」の境界）→ `decisions.md`
- [ ] Q4（R-1 の「被験者」に EH2・開発者利用が入るか）→ `decisions.md`

## 機械的な修正
- [ ] cp932 問題（`run.sh` / `check_g1_emails.py` ほか `open()` の encoding 欠落）を直す
- [ ] 修正後に `PYTHONUTF8` 無しで `run.sh` を実行し終了コード 0 を確認
- [ ] ⚠️ 直した範囲が「研究者判断の要らないもの」に収まっているか確認（事前登録の記録は触らない）

## 検査の追加
- [ ] D6（案内日の分離）の検査の置き場を決める（`decisions.md` に判断として記録）
- [ ] 検査を追加
- [ ] ★ わざと壊した入力で赤・正常な入力で緑の両方を実測（自己検査の 3 状態）

## マージ計画
- [ ] `merge-plan.md`（衝突予測・schema drift `activity_label`・タグとの順序・実行手順）
- [ ] ⚠️ マージの実行はしない

## レビュー
- [ ] `code-reviewer`（opus）∥ `security-checker`（opus）
- [ ] `/cross-review` 2 巡（コミット後・パス限定・出力は scratchpad）

## 完了処理
- [ ] `design.md` の最終化 / `decisions.md` の確定
- [ ] 次セッションの引き継ぎを `.steering/_handoff/` に置く
- [ ] git commit（`Refs: .steering/20260920-g1-o1-inventory/`）
