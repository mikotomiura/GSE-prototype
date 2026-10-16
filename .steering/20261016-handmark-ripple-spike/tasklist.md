# タスクリスト

## 準備
- [x] 引き継ぎと表現の議論の判断 5・6・8 を読む
- [x] 前の試作の記録とコードを読む
- [x] 見本の甲-2 の式を読む

## 実装
- [x] `HandmarkSurface.tsx` を canvas の波紋にする（28 px・250 ms・打ち切り・灰・ループは波紋があるあいだだけ）
- [x] `handmark_spike.rs` の窓を 32×32 にし、波紋の一生の計測コマンドと CSV を足す
- [x] `synthetic-burst.applescript`

## テスト
- [x] `cargo test`・`cargo clippy`・`npx tsc --noEmit`
- [x] 起動のログで除外の読み返しが通ることを確かめる
- [x] 一定の間隔 5 本とバーストを流し、動いていた割合・打ち切りの広がり・消えるまでを集計する
- [x] 遅れを取り直す（0.15 秒 × 200・0.06 秒 × 100）

## レビュー
- [x] code-reviewer・security-checker
- [x] /cross-review

## ドキュメント
- [x] results.md
- [x] manual-check.md（研究者が自分の画面で見る手順）
- [ ] 研究者の試視
- [ ] push（PR は出さない）
