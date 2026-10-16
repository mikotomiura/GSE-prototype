# タスクリスト

## 準備
- [x] 引き継ぎと表現の議論の判断 5・6・8 を読む
- [x] 前の試作の記録とコードを読む
- [x] 見本の甲-2 の式を読む

## 実装
- [ ] `HandmarkSurface.tsx` を canvas の波紋にする（28 px・250 ms・打ち切り・灰・ループは波紋があるあいだだけ）
- [ ] `handmark_spike.rs` の窓を 32×32 にし、波紋の一生の計測コマンドと CSV を足す
- [ ] `synthetic-burst.applescript`

## テスト
- [ ] `cargo test`・`cargo clippy`・`npx tsc --noEmit`
- [ ] 起動のログで除外の読み返しが通ることを確かめる
- [ ] 一定の間隔 5 本とバーストを流し、動いていた割合・打ち切りの広がり・消えるまでを集計する
- [ ] 遅れを取り直す（0.15 秒 × 200・0.06 秒 × 100）

## レビュー
- [ ] code-reviewer・security-checker
- [ ] /cross-review

## ドキュメント
- [ ] results.md
- [ ] manual-check.md（研究者が自分の画面で見る手順）
- [ ] 研究者の試視
- [ ] push（PR は出さない）
