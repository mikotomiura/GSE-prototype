# panel（round 1）

書誌はすべて OpenAlex の記録（https://api.openalex.org/works/doi:<DOI>）で題・筆頭著者・年・DOI が一致し、open_access.is_oa が真で oa_url がある（2026-11-07）。本文は oa_url か同じ論文の公開版（arXiv・Europe PMC）から取り、題が一致したものを「読めた」とした。原本は tmp/raw/、本文は tmp/sources/（git が無視する）。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | 原本 SHA-256（先頭 16） | 本文 |
|---|---|---|---|---|---|
| R1 | 行動の記号列の系列モデル（HMM・マルコフ連鎖）の方法論 | その測り方が本当に主張を測っているかを疑う懐疑家 | Monaco & Tappert 2018 Pattern Recognition doi:10.1016/j.patcog.2017.11.021（arXiv:1607.03854） | a70b89f58071d422 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/monaco.txt |
| | | | Pohle ほか 2017 JABES doi:10.1007/s13253-017-0283-8（arXiv:1701.08673） | 4acaa71d899fa416 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/pohle.txt |
| | | | Singer ほか 2014 PLoS ONE doi:10.1371/journal.pone.0102070 | 9cf1758f75450d26 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/singer.txt |
| R2 | 個人化した行動のモデルの実務（モバイル・行動センシング・ユーザーモデル） | で、読者は何に使えるのかと問う実務家・冗長さに厳しい読者 | Aalbers ほか 2023 JMIR mHealth uHealth doi:10.2196/37469（Europe PMC PMC10132040） | e123ba43a6ff09b2 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/aalbers.txt |
| | | | Saeb ほか 2017 GigaScience doi:10.1093/gigascience/gix019（Europe PMC PMC5441397） | 0aa8040872f142e4 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/saeb.txt |
| R3 | 評価の偏りと個人への推論の方法論（選択の偏り・再現性） | 過剰主張と検証できない手順の摘発者 | Varma & Simon 2006 BMC Bioinformatics doi:10.1186/1471-2105-7-91（Europe PMC PMC1397873） | 376cbb34734c73a9 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/varma.txt |
| | | | Liu & Meng 2016 Annu Rev Stat Appl doi:10.1146/annurev-statistics-010814-020310（arXiv:1510.08539 v1） | 9f51e95689c46411 | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/liumeng.txt |
| E | 投稿先の担当編集者 | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる | Mensh & Kording 2017 PLoS Comput Biol doi:10.1371/journal.pcbi.1005619 ＋ context-A の投稿先の一次 | f02a2c14c630369f | /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/mensh.txt |

外した候補: Cawley & Talbot 2010（JMLR）は OpenAlex で is_oa が偽（closed）のため「確認済み」の条件に合わない。
3 つの立場の角度: R1 はモデルの構造と比べの基準、R2 は使う側と評価の場面、R3 は選択の偏りと推論の作法。系譜は互いに違う。
Codex: 研究者の指示（2026-11-06・聞かずに加える）により、5 本が返った後に直列で加える。
