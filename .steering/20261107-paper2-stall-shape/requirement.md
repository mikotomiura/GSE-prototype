# 論文 2（停滞の形）: 濃くする計算で単独にできるかを決める

## 背景

- 公開データの知見のうち、知見 1（停滞の手前の上がり）は論文 1 として JEDM に投稿した（投稿番号 1484・査読中）。知見 2（停滞の形）は、判断 4 の文献のラウンド（`docs/literature/20261105-public-data-findings-novelty.md` のカード 3・4）で 5 点のうち 3 点が既出、残る 2 点は「見つからなかった」水準にとどまった。
- 先行が 0 件だったのは 3 つの計算（揺れの 3 水準以上の分解・停滞の数のポアソンとの比・停滞の定義と切り方を振る multiverse）。判断 43（`.steering/20261105-public-data-findings-paper/decisions.md`）で、これを回してから単独にするかを決めると決めた。
- 研究者の確認（2026-11-07）: 論文 3 の HP Z2 の計算待ちの間に今始める。読者は論文 1 と同じ（判断 5: 行動ログで状態を推す研究者・変えたいのは評価の設計）。取り置きは論文 1 で開けた分（CS1 2019 の 146 人・KLiCKe の 1,498 人）は使い、未開封（CoAuthor 18 人・CS1 2021 の 13 人）は閉じたまま。条件は repo のコミットだけ（OSF には出さない）。

## ゴール

3 つの計算の結果から、知見 2 を「停滞のラベルは分析者の切り方でどれだけ変わるか」という方法の論文として単独にできるかを、回す前に書いた基準で判定し、研究者に聞ける状態にする。

## スコープ

### 含むもの
- 文献の追いかけ（判断 4 以降に 3 つの計算に当たる先行が出ていないか・既存の文献は番号だけ）。
- 条件（`experiments/20261107-stall-shape-multiverse/conditions.md`）を、単独にする判定の基準とともに回す前にコミットする。
- 停滞の検出の Python の写しと replay との照合、3 つの計算、結果の notes。
- 単独にするかを研究者に聞く（AskUserQuestion）。

### 含まないもの
- O1（判断 7）。未開封の取り置き（CoAuthor 18 人・CS1 2021 の 13 人）。
- 原稿の外枠・/reimagine・attack-me（単独と決まった後の次のタスク）。
- OSF への事前登録。

## 受け入れ条件

- [ ] 条件と判定の基準が、計算の前のコミットにある。
- [ ] Python の検出器が replay の停滞の始まりと一致する（照合）・陽性対照と変異の確かめ。
- [ ] 3 つの計算の結果が `notes.md` にあり、言える範囲と言えない範囲を分けている。
- [ ] レビュー（code-reviewer と /cross-review）を通す。
- [ ] 研究者に単独にするかを聞いた。

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-public-data-findings-paper2.md`（引き継ぎ・一次資料にしない）
- `experiments/20261102-stall-decomposition/`・`20261104-cs1-landscape/`・`20261102-public-data-landscape/`・`20261103-stall-candidates-c1c2c6/`
- `docs/literature/20261105-public-data-findings-novelty.md`

## 運用メモ
- /reimagine 適用: No（この段は計算の条件。単独と決まったら原稿の外枠で /reimagine を使う）
- 理由: 引き継ぎ §2 の 4 が外枠の段で /reimagine を置いている
