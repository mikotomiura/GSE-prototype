# panel（prereg-window-overlap round 1・stage prereg）

論文 3 の revision-integrated round 1（.steering/20261125-paper3-next-venue/attack-me/revision-integrated/round-1/panel.md）と同じ立場・同じ接地の文献で回す。条件は論文 3 の仕組みの主張を確かめるためのもので、論文の査読と同じ角度（モデルの構造と比べの基準／使う側と評価の場面・記録の単位の漏れ／選択の偏りと推論の作法）が当たるため。E は prereg なので置かない。原本は round 1 の tmp/raw から写し、7 本とも SHA-256（先頭 16 桁）が round 1 の表と一致した（2026-11-27）。本文は tmp/sources/（git check-ignore で無視を確かめた）。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | SHA-256（先頭 16） | 本文 |
|---|---|---|---|---|---|
| R1 | 行動の記号列の系列モデル（HMM・マルコフ連鎖）の方法論 | その測り方が本当に主張を測っているかを疑う懐疑家 | Monaco & Tappert 2018 doi:10.1016/j.patcog.2017.11.021 | a70b89f58071d422 | tmp/sources/monaco.txt |
| | | | Pohle ほか 2017 doi:10.1007/s13253-017-0283-8 | 4acaa71d899fa416 | tmp/sources/pohle.txt |
| | | | Singer ほか 2014 doi:10.1371/journal.pone.0102070 | 9cf1758f75450d26 | tmp/sources/singer.txt |
| R2 | 個人化した行動のモデルの実務（モバイル・行動センシング・ユーザーモデル） | で、読者は何に使えるのかと問う実務家 | Aalbers ほか 2023 doi:10.2196/37469 | e123ba43a6ff09b2 | tmp/sources/aalbers.txt |
| | | | Saeb ほか 2017 doi:10.1093/gigascience/gix019 | 0aa8040872f142e4 | tmp/sources/saeb.txt |
| R3 | 評価の偏りと個人への推論の方法論（選択の偏り・再現性） | 過剰主張と検証できない手順の摘発者 | Varma & Simon 2006 doi:10.1186/1471-2105-7-91 | 376cbb34734c73a9 | tmp/sources/varma.txt |
| | | | Liu & Meng 2016 doi:10.1146/annurev-statistics-010814-020310（arXiv 版） | 9f51e95689c46411 | tmp/sources/liumeng.txt |

- 本文の絶対パスの前置き: /Users/johnd/GSE-prototype-window-overlap/.steering/20261127-gse-paper3-window-overlap/attack-me/prereg-window-overlap/round-1/
- Codex: memory（attack-me には聞かずに加える）により、4 本が返った後に直列で加える。渡すのは対象物の conditions.md と前の試験の conditions.md だけ（引き継ぎの handoff が外部に送ってよいとした条件の文書）。
