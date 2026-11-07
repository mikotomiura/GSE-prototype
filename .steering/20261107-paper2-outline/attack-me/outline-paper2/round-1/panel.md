# panel（outline round 1・論文 2）

想定の投稿先は JEDM（`../../../decisions.md` 判断 3）。立場は論文 1 の panel と同じ 3 つの角度を、論文 2 の中身（定義の multiverse・過分散・分散の分解）に合わせて組み直した。R3 は事前登録と同等性の検定から、分析の柔軟さと multiverse・再現性に替えた。

書誌の確認: OpenAlex の記録（`/works/doi:<DOI>`）で題・筆頭著者・年が一致し、`is_oa` が真で `oa_url` がある（2026-11-07・メインが curl で確認）。本文はメインが取得し `tmp/sources/` に置いた（tmp/ は git が無視・`git check-ignore` で確認）。本文は印字していない（題の行を grep で確かめただけ）。

| 役 | 立場 | 下位人格 | 文献（確認済み・読めた） | 原本の SHA-256（先頭 16 桁）| 保存先 |
|---|---|---|---|---|---|
| R1 | 打鍵の記録と作文・プログラミングの過程の測定の伝統 | その測定は本当にそれを測っているかを疑う懐疑家 | Guo, Zhang, Deane & Bennett 2020 doi:10.5281/zenodo.3911797（JEDM・PDF は JEDM の OJS）・Li & An 2026 doi:10.3389/fpsyg.2026.1792834（Europe PMC の全文 XML・PMC13254725） | ea96d922b1ed835f・2cf4b1a1321c079f | guo2020.txt・bayesmix2026.txt |
| R2 | 教育データの検出・予測のモデルの評価の実務 | で、読者は何に使えるのかと問う実務家 | Gardner, Brooks & Baker 2018 doi:10.18608/jla.2018.52.7（JLA の PDF）・Pelánek 2015 doi:10.5281/zenodo.3554665（JEDM の OJS） | e76aea2d98126728・388805dbd5c1917d | gardner2018.txt・pelanek2015.txt |
| R3 | 分析の柔軟さ・multiverse・機械学習を使う研究の再現性 | 過剰主張と検証できない手順の摘発者 | Hoffmann ら 2021 doi:10.1098/rsos.201925（Europe PMC の全文 XML・PMC8059606）・Kapoor & Narayanan 2023 doi:10.1016/j.patter.2023.100804（Europe PMC・PMC10499856） | bfb1f9c69e8edba4・aab2d4bcc58efe6f | hoffmann2021.txt・kapoor2023.txt |
| E | JEDM の担当編集者 | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる | JEDM の About（Focus and Scope・一次・curl）・Mensh & Kording 2017 doi:10.1371/journal.pcbi.1005619（PLoS の PDF） | 8815b5e653d963c4・f02a2c14c630369f | jedm_aims.txt・mensh2017.txt |

試して使わなかったもの: Steegen ら 2016・Simonsohn ら 2020（OpenAlex で OA なし）、Del Giudice & Gangestad 2021・Silberzahn ら 2018（OA の記録はあるが、出版社と機関リポジトリが curl を bot 対策で止めた）、Botvinik-Nezer ら 2020（Europe PMC の全文 XML が取れない）、Roeser ら 2025（APA の頁が取れない）。
