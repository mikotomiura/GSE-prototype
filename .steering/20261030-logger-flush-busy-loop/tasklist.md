# タスクリスト

## 準備
- [x] 引き継ぎ・logger.rs のループ・tray の「停止中」の意味を読む
- [x] 設計の承認（2026-10-30）

## 実測（直す前）
- [x] 計測の道具を試作の枝から写す（`GSE_HANDMARK_STAGE_SPIKE` を外す）
- [x] 開発版（main）の「停止中」の CPU を累積 CPU 時間の差で測る（「記録中」は測っていない。空回りの条件に入らないため）

## 実装（TDD）
- [x] `FlushClock` を今の挙動のまま書いてループを置き換える（既存テスト緑）
- [x] 回帰テストを書き、赤を見る
- [x] 直す（期限で時計を進める・判断をループの先頭へ）
- [x] cargo test --workspace・clippy 緑

## 実測（直した後）
- [x] 同じ手順で測る代わりに、ロガーを実際に動かすテストで直す前後を測った（開発版の開始前の「停止中」では再現しなかった・decisions.md 判断 6）
- [x] ループの周回数のテストを足し、変異で赤を確かめた（MEDIUM・判断 2）

## O1 への影響
- [x] 被験者の一時停止中に起きる道筋をまとめ、配る版の扱いを研究者に聞く

## レビュー
- [x] code-reviewer + security-checker を並列で
- [x] /finish-task で /cross-review（Claude と Codex。Codex は利用上限の解除を待って回した・判断 7）
- [x] Codex の指摘 3 件を直す

## 完了処理
- [x] design.md・decisions.md の最終化
- [x] git commit
- [ ] push（PR は研究者に確かめてから）
