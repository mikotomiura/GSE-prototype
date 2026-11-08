# panel（manuscript round 4・論文 2）

round 1〜3 と同じ立場・同じ文献で回す。原本は round 3 の `tmp/raw/` から写し、SHA-256 が round 3 の値と一致した。JEDM の About と Submissions は round 4 の前（2026-11-08）に curl で取り直し、判定に使う文が逐語で在ることを確かめた（動的なページなので SHA-256 は表の値と違う）。本文は印字していない。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | 原本の SHA-256（先頭 16 桁） | 保存先（tmp/sources/） |
|---|---|---|---|---|---|
| R1 | 打鍵の記録と作文・プログラミングの過程の測定の伝統 | その測定は本当にそれを測っているかを疑う懐疑家 | Guo, Zhang, Deane & Bennett 2020 doi:10.5281/zenodo.3911797・Li & An 2026 doi:10.3389/fpsyg.2026.1792834 | ea96d922b1ed835f・2cf4b1a1321c079f | guo2020.txt・bayesmix2026.txt |
| R2 | 教育データの検出・予測のモデルの評価の実務 | で、読者は何に使えるのかと問う実務家 | Gardner & Brooks 2018 doi:10.18608/jla.2018.52.7・Pelánek 2015 doi:10.5281/zenodo.3554665 | e76aea2d98126728・388805dbd5c1917d | gardner2018.txt・pelanek2015.txt |
| R3 | 分析の柔軟さ・multiverse・機械学習を使う研究の再現性 | 過剰主張と検証できない手順の摘発者 | Hoffmann ら 2021 doi:10.1098/rsos.201925・Kapoor & Narayanan 2023 doi:10.1016/j.patter.2023.100804 | bfb1f9c69e8edba4・aab2d4bcc58efe6f | hoffmann2021.txt・kapoor2023.txt |
| E | JEDM の担当編集者 | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる | JEDM の About と Submissions（一次・curl・2026-11-08）・Mensh & Kording 2017 doi:10.1371/journal.pcbi.1005619 | 9073c34afc8e6c3a（About）・d83a4735ad46c0c7（Submissions）・f02a2c14c630369f | jedm_aims.txt・jedm_submissions.txt・mensh2017.txt |

注: Li & An 2026 は、この round の原稿で引用文献にもなった（関連研究）。接地の文献として使い続ける（立場の基準を抜き出すためで、原稿の引用の当否は査読の対象）。
