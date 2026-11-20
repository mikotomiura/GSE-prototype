# panel（manuscript round 7）

round 1〜6 と同じ立場・同じ接地の文献で回す（Skill: round 2 以降は同じ立場・同じ文献）。原本は round 6 の tmp/raw から写し、8 本とも SHA-256（先頭 16 桁）が下の表と一致することを 2026-11-20 に確かめた。本文は tmp/sources/（git が無視する・`git check-ignore` で確かめた）。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | 取得元 | SHA-256（先頭 16） | 本文 |
|---|---|---|---|---|---|---|
| R1 | 行動の記号列の系列モデル（HMM・マルコフ連鎖）の方法論 | その測り方が本当に主張を測っているかを疑う懐疑家 | Monaco & Tappert 2018 Pattern Recognition doi:10.1016/j.patcog.2017.11.021 | arxiv.org/pdf/1607.03854 | a70b89f58071d422 | tmp/sources/monaco.txt |
| | | | Pohle ほか 2017 JABES doi:10.1007/s13253-017-0283-8 | arxiv.org/pdf/1701.08673 | 4acaa71d899fa416 | tmp/sources/pohle.txt |
| | | | Singer ほか 2014 PLoS ONE doi:10.1371/journal.pone.0102070 | journals.plos.org（printable） | 9cf1758f75450d26 | tmp/sources/singer.txt |
| R2 | 個人化した行動のモデルの実務（モバイル・行動センシング・ユーザーモデル） | で、読者は何に使えるのかと問う実務家・冗長さに厳しい読者 | Aalbers ほか 2023 JMIR mHealth uHealth doi:10.2196/37469 | Europe PMC PMC10132040 fullTextXML | e123ba43a6ff09b2 | tmp/sources/aalbers.txt |
| | | | Saeb ほか 2017 GigaScience doi:10.1093/gigascience/gix019 | Europe PMC PMC5441397 fullTextXML | 0aa8040872f142e4 | tmp/sources/saeb.txt |
| R3 | 評価の偏りと個人への推論の方法論（選択の偏り・再現性） | 過剰主張と検証できない手順の摘発者 | Varma & Simon 2006 BMC Bioinformatics doi:10.1186/1471-2105-7-91 | Europe PMC PMC1397873 fullTextXML | 376cbb34734c73a9 | tmp/sources/varma.txt |
| | | | Liu & Meng 2016 Annu Rev Stat Appl doi:10.1146/annurev-statistics-010814-020310（arXiv 版で代えた） | arxiv.org/pdf/1510.08539v1 | 9f51e95689c46411 | tmp/sources/liumeng.txt |
| E | 投稿先（UMUAI）の担当編集者 | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる。判定は context-A の想定読者の素養（系列モデルと統計の専門の訓練を前提にしない UMUAI の読者）に届くかで行う | Mensh & Kording 2017 PLoS Comput Biol doi:10.1371/journal.pcbi.1005619 ＋ context-A の投稿先の一次 | journals.plos.org（printable） | f02a2c14c630369f | tmp/sources/mensh.txt |

- 3 つの立場の角度: R1 はモデルの構造と比べの基準、R2 は使う側と評価の場面、R3 は選択の偏りと推論の作法。
- 手順: 本線（origin/main）の attack-me で読んだ（worktree の写しは古い）。想定読者の素養は round 3〜5 と同じ値。
- 本文の絶対パスの前置き: /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/
- Codex: 研究者の指示（2026-11-06・attack-me には聞かずに加える）により、5 本が返った後に直列で加える。本文の tex と規程の抜粋だけを渡し、既知の未決と保留した論点の一覧（round 6 の一覧から、直した τ の範囲・要旨の 3〜7e-3 の保留を外し、新しい保留を足した）を添え、再掲しないよう頼む。
