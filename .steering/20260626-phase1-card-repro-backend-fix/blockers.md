# ブロッカー記録

## ブロッカー 1: 最終確認（実機 repro / 本番ビルドスモーク）は研究者作業（未解決・本タスクで緩和済）

- **発生日時**: 2026-06-26（前タスク blockers B1 の継続）
- **症状**: #1（プローブ/Nudge カードのボタン無反応）の **devtools `console.error` 生文字列**
  （Full か Disconnected か）は実キーボードフック＋OS 権限＋実セッションを伴う repro でしか確定できず、
  Claude 側では再現不可。
- **本タスクでの緩和**:
  1. **再現性確保**: debugView gate（`VITE_GSE_DEBUG==="1"`）で `📝 プローブ強制表示` / `💡 Nudge 強制表示`
     ボタンを追加。研究者が能動的に card→`record_realtime_*` / nudge→`record_intervention_dismiss` を
     テストできる。
  2. **原因に依らない構造的修正**: consumer を `File::create` 失敗で死なせず temp フォールバック＋sink
     縮退にしたため、channel が Disconnected にならず #1（カードが閉じない）は原因側で解消。Full でも
     誤誘導ラベル是正で `console.error` が「full」/「disconnected」を区別表示するので診断は容易。
- **残作業（研究者）**:
  1. **本番（release）ビルド**で `VITE_GSE_DEBUG=1` を有効化しスモーク: プローブ/Nudge を強制表示 →
     各ボタンで確実に閉じ `record_*` が NDJSON に残る／ログ書込失敗時に fail-loud バナーが出る、を確認。
  2. もし repro でカードのインラインエラーが出たら `console.error` の文言を共有（「full」なら真の backlog
     対策＝容量/drain を別タスクで、「disconnected」なら本修正が直撃）。
  3. macOS は Documents/TCC 文脈が dev と異なるため **本番 .app/.dmg でこそ** fail-loud（temp フォールバック
     バナー）が効くかを確認（next-session-prompt §4）。
- **教訓**: 実機依存の間欠バグは「症状を出すデバッグトリガ」＋「原因に依らず両分岐に効く構造的修正」を
  先に入れると、repro 待ちで停滞せず前進できる。
