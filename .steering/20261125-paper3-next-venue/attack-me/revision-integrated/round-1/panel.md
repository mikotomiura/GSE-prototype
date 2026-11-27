# panel（revision-integrated round 1・stage revision・投稿先 TMLR）

前の attack-me（`.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/`・round 1〜10・UMUAI 向け）と同じ立場・同じ接地の文献で回す。投稿先が変わったので E の接地を TMLR の一次（context-A）に替えた。R1〜R3 の立場は投稿先に依らない角度（モデルの構造と比べの基準／使う側と評価の場面／選択の偏りと推論の作法）なので替えない。原本は 2026-11-27 に取り直し、8 本とも SHA-256（先頭 16 桁）が前の round の表と一致した。本文は tmp/sources/（`git check-ignore` で無視を確かめた）。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | 取得元 | SHA-256（先頭 16） | 本文 |
|---|---|---|---|---|---|---|
| R1 | 行動の記号列の系列モデル（HMM・マルコフ連鎖）の方法論 | その測り方が本当に主張を測っているかを疑う懐疑家 | Monaco & Tappert 2018 Pattern Recognition doi:10.1016/j.patcog.2017.11.021 | arxiv.org/pdf/1607.03854 | a70b89f58071d422 | tmp/sources/monaco.txt |
| | | | Pohle ほか 2017 JABES doi:10.1007/s13253-017-0283-8 | arxiv.org/pdf/1701.08673 | 4acaa71d899fa416 | tmp/sources/pohle.txt |
| | | | Singer ほか 2014 PLoS ONE doi:10.1371/journal.pone.0102070 | journals.plos.org（printable） | 9cf1758f75450d26 | tmp/sources/singer.txt |
| R2 | 個人化した行動のモデルの実務（モバイル・行動センシング・ユーザーモデル） | で、読者は何に使えるのかと問う実務家・冗長さに厳しい読者 | Aalbers ほか 2023 JMIR mHealth uHealth doi:10.2196/37469 | Europe PMC PMC10132040 fullTextXML | e123ba43a6ff09b2 | tmp/sources/aalbers.txt |
| | | | Saeb ほか 2017 GigaScience doi:10.1093/gigascience/gix019 | Europe PMC PMC5441397 fullTextXML | 0aa8040872f142e4 | tmp/sources/saeb.txt |
| R3 | 評価の偏りと個人への推論の方法論（選択の偏り・再現性） | 過剰主張と検証できない手順の摘発者 | Varma & Simon 2006 BMC Bioinformatics doi:10.1186/1471-2105-7-91 | Europe PMC PMC1397873 fullTextXML | 376cbb34734c73a9 | tmp/sources/varma.txt |
| | | | Liu & Meng 2016 Annu Rev Stat Appl doi:10.1146/annurev-statistics-010814-020310（arXiv 版で代えた） | arxiv.org/pdf/1510.08539v1 | 9f51e95689c46411 | tmp/sources/liumeng.txt |
| E | 投稿先（TMLR）の担当の action editor | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる。判定は context-A の想定読者（機械学習の研究者で個人化の評価をする人）に届くかで行う | Mensh & Kording 2017 PLoS Comput Biol doi:10.1371/journal.pcbi.1005619 ＋ context-A の投稿先の一次（TMLR・照合済み） | journals.plos.org（printable） | f02a2c14c630369f | tmp/sources/mensh.txt |

- 本文の絶対パスの前置き: /Users/johnd/GSE-prototype-paper3/.steering/20261125-paper3-next-venue/attack-me/revision-integrated/round-1/
- stage revision の round 1: 前の投稿先の指摘は "lack sufficient depth" の一句だけ（応答書は無い）。これを E と R1〜R3 に渡し、改訂（書き直し v2 と S14）が応えたかを見させる。
- Codex: 研究者の指示（memory: attack-me には聞かずに加える）により、5 本が返った後に直列で加える。本文の tex と補足の tex と規程の抜粋だけを渡し、既知の未決 3 件を添える。
