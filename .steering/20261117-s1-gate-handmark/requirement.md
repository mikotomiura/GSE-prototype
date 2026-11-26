# 段 1 の配布の門に手跡の検査を足す

## 背景

`scripts/check-s1-release-readiness.sh` は [1]〜[4] を見るが、手跡（ADR-051）を見ていない。v0.1.42 の本人の配布では
手跡の文字列と割付の表の SHA-256 を手で確かめた（`.steering/20261116-release-v0.1.42-handmark/decisions.md` 判断 2）。
3 名に配る版（ADR-052 D5・Windows の手跡が通ってから）の前に門へ入れる。

## ゴール

門が次を見て、満たさなければ赤になる。
1. gse-next の実体が手跡を知っている（`handmark_assignment.json`・`handmark_assignment.sha256` の文字列）
2. [2] のリリースタグが手跡の実装（`handmark_store.rs`・`handmark_driver.rs`）を含む
3. 各配布物に割付の表と `.sha256` があり、SHA-256 が合う（表は参加者ごとに置くので zip だけでは赤）

## 受け入れ条件

- [ ] 陽性対照: v0.1.41 の実体（手跡なし）で赤、v0.1.42 で緑
- [ ] selftest で 3 つの検査それぞれが壊すと赤・満たすと緑
- [ ] 本人の配布フォルダ（`~/Desktop/S1_実施用_macOS/`）の写しで門が通る（本物は触らない・gse-next を止めない）
- [ ] 門の bash は macOS の bash 3.2 で走る

## スコープ外

- Q3 の 6 択に「作業していた」を足すこと（引き継ぎの B・別タスク）
- Windows の手跡の表示が通ったかの検査（文字列では分からない。ADR-052 D5 の運用で守る）
- 本人の配布物を入れ替えること

## 運用メモ
- /reimagine 適用: No
- 理由: 既存の門に検査を足すだけで、設計の分岐が小さい
