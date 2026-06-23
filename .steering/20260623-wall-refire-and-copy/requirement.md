# wall-refire-and-copy (Wall 解除後の再発火修正 + 文言修正)

## 背景 (実機フィードバック)
1. **Wall を一度解除しても、もう一度 Wall が発生する**。原因: デバッグ `force_wall_decision` が
   cooldown (`last_wall_at_ms`) を立てないため、解除直後に p_stuck が高いままだと wall_accum が
   再び 30s 溜まって即再発火する (実 Wall は activation 時に cooldown を立てるので再発火しない)。
2. **「⚠ キーボードは使えません！」が実態と不一致**。Wall は視覚オーバーレイで、キー入力は
   実際には抑止していない (使える) ため、文言を「使うのを控えて」という趣旨に直すべき。
3. (確認) Wall が全画面なのは意図的か → **意図的・全画面の段階減光を維持** (ユーザー承認)。
   右上=穏やかな Nudge/プローブの役割で、Wall は強い Lv2 介入。コード変更なし。

## ゴール
- forced wall も実 Wall と同様 cooldown を開始し、解除直後に即再発火しない。
- Wall 中の打鍵バナーを穏やかで正確な文言にする。

## スコープ
### 含むもの
- `force_wall_decision` に now_ms を渡し `last_wall_at_ms` を設定 (cooldown 開始)。テスト更新。
- 打鍵バナー文言を「いまは手を止めて、ひと休みしましょう」に変更。
### 含まないもの
- Wall の見た目変更 (全画面段階減光維持・ユーザー承認)。介入閾値/HMM/schema 変更。

## 受け入れ条件
- [ ] forced wall 解除後、p_stuck 高でも即再発火しない (cooldown 抑止)・単体テスト緑
- [ ] 打鍵バナーが正確で穏やかな文言
- [ ] cargo test --workspace 緑・--snapshot byte-equal・build 緑

## 運用メモ
- /reimagine: No (小修正)。別 PR・main 基点。
- 判断: #22 D2「force は cooldown 非汚染」を**再発火回避を優先して方針変更** (force も cooldown 開始)。
