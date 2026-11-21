# panel — 3 つの立場と接地の文献（attack-me・stage `manuscript`・round 2）

作成: 2026-11-21（Surface・メイン）。round 1 の panel は `.steering/20260929-p321-paper-submission-prep/attack-me/manuscript-emse/round-1/panel.md`（ブランチ `docs/p321-attack-me`）。

本文テキストの置き場: `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\sources\`（root の `.gitignore` の `tmp/` が無視する・`git check-ignore -v` で確かめた）。本文は印字していない（先頭の数行・頁数・文字数だけ）。

## round 1 からの引き継ぎと変更

- R1・R2 は round 1 と同じ立場・同じ文献。原本は round 1 の `tmp/raw/` から写し、**SHA-256 が round 1 の panel の値と一致する**ことを確かめた（本文のテキストも round 1 のものを写した）。
- R3 は立場を「投稿先（JSS）の方法論と再現性の番人」に替え、**Hesterberg (2015) を MacKinnon, Nielsen & Webb (2023) に替えた**。理由: 改訂の設計（`design.md` §3 の S8・研究者が承認した）が、この round の席を「再解析と測定の妥当性・クラスタが少ないときの推論・debugging の人的要因」と決めた。改訂の原稿は、クラスタが少ないときの補助の区間（CR2・Bell–McCaffrey）と leave-one-developer-out を足しており、それを審査できる文献が要る。⚠️ MacKinnon et al. (2023) は対象物が自分で引いている文献（round 1 で Sjøberg・Hellas を入れたのと同じ扱い・その伝統の基準に本当に従っているかを確かめるため）。
- 出し先が EMSE から JSS に替わったので、R3 の規程の照合は JSS の規程で行う（context-A）。

## R1 — 手法の核: ソフトウェア工学の測定の妥当性と、質的なコーディングを量として再利用することの伝統

- 立場と下位人格: round 1 と同じ（構成概念妥当性・コーディングの信頼性 ／「その測定は本当にそれを測っているか」を疑う懐疑家）。

| 文献 | 確認 | 読めた | 原本 SHA-256 | 本文 |
|---|---|---|---|---|
| Sjøberg & Bergersen (2023). Construct validity in software engineering. *IEEE TSE 49*(3). doi:10.1109/TSE.2022.3176725 | 確認済み（round 1） | 読めた | `457858d6af60ccde…`（round 1 と一致） | `tmp\sources\sjoberg2022.txt` |
| Sjøberg & Bergersen (2023). Improving the reporting of threats to construct validity. *EASE 2023*. doi:10.1145/3593434.3593449（arXiv:2306.05336 の版） | 確認済み（round 1） | 読めた | `50f8ab3ab7e5261c…`（一致） | `tmp\sources\sjoberg2023.txt` |
| O'Connor & Joffe (2020). Intercoder reliability in qualitative research. *IJQM 19*. doi:10.1177/1609406919899220（UCL Discovery の版） | 確認済み（round 1） | 読めた | `1ff859a271acf5ee…`（一致） | `tmp\sources\oconnor2020.txt` |

## R2 — 隣接分野: 開発者の debugging と助けを求める行動を観察する研究者（debugging の人的要因）

- 立場と下位人格: round 1 と同じ（IDE の中の debugging・助けの求め方を観察して道具や教育に生かす ／「で、読者は何に使えるのか」と問う実務家・冗長さに厳しい読者）。

| 文献 | 確認 | 読めた | 原本 SHA-256 | 本文 |
|---|---|---|---|---|
| Beller, Spruit, Spinellis & Zaidman (2018). On the dichotomy of debugging behavior among programmers. *ICSE 2018*. doi:10.1145/3180155.3180175（TU Delft の版） | 確認済み（round 1） | 読めた | `b4b33224bac1b75c…`（一致） | `tmp\sources\beller2018.txt` |
| Hellas et al. (2023). Exploring the responses of large language models to beginner programmers' help requests. *ICER 2023*. doi:10.1145/3568813.3600139（arXiv:2306.05715 の版） | 確認済み（round 1） | 読めた | `388d55ee283d17d2…`（一致） | `tmp\sources\hellas2023.txt` |

- ⚠️ Hellas et al. (2023) は改訂の原稿が §7 で新しく使っている（"Beyond these two datasets"）。その使い方が文献に忠実かを、この立場が確かめられる。

## R3 — 投稿先（JSS）の方法論と再現性の番人（経験的研究の基準・オープンサイエンス・LLM の利用・クラスタが少ないときの推論）

- 立場: ソフトウェア工学の経験的研究の基準（ACM SIGSOFT Empirical Standards の一般基準・再現・メタ科学・オープンサイエンス・二次データの倫理）と、研究での LLM の利用の報告、クラスタが少ないときのクラスタ頑健な推論に通じた査読者。
- 下位人格: 過剰主張と検証できない手順の摘発者（事前に決まっていない分岐・後から足した解析の扱い・少ないクラスタからの推論・LLM が生成した転記・コード・数え直しの検証の甘さを探す）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Ralph et al. (2020). Empirical standards for software engineering research. arXiv:2010.03525（公式リポジトリ `acmsigsoft/EmpiricalStandards` のコミット `554118c6…` の基準 6 つを連結した版） | 確認済み（round 1） | 読めた | round 1 と同じ | `580abe323e675369…`（一致） | `tmp\sources\empirical-standards.txt` |
| Wagner, Muñoz Barón, Falessi & Baltes (2025). Towards evaluation guidelines for empirical studies involving LLMs. arXiv:2411.07668v3 | 確認済み（round 1） | 読めた | round 1 と同じ | `cf58e03aaf7721ec…`（一致） | `tmp\sources\wagner2024.txt` |
| MacKinnon, Nielsen & Webb (2023). Cluster-robust inference: A guide to empirical practice. *Journal of Econometrics 232*(2), 272–299. doi:10.1016/j.jeconom.2022.04.001 | **確認済み**（2026-11-21・OpenAlex の記録を `curl -s` で JSON のまま取得: 題・筆頭著者 James G. MacKinnon・年 2022〔オンライン公開〕・DOI が一致・`open_access.is_oa` 真・`oa_status` hybrid） | **読めた**（57 頁・165,621 字・先頭の行 "Cluster-Robust Inference: / A Guide to Empirical Practice" で題が一致） | ⚠️ `oa_url`（doi.org → Elsevier）は試していない。OpenAlex の OA の所在のうち Aarhus 大学の版（journal 版の PDF）は pypdf の抽出で語間の空白が落ちて検索に向かなかった → **arXiv の版（arXiv:2205.03285・OpenAlex の同じ記録の OA の所在）で代えた**（題と筆頭著者が一致） | `8f151977901cdb4c09b424a4c21eea1e7b54e8be7afaec5deb36d7bfe52dbaa6`（arXiv の PDF）／ 参考: journal 版 `8cc9d0571b4278ff99e3ef608982b2c669616856b107a0ae3fdae7ad6fa96981` | `tmp\sources\mackinnon2023.txt` |

- 使わなくなった文献: Hesterberg (2015)（round 1 の R3）。原本と本文は `tmp\` に写してあるが、この round の依頼文には入れない。

## 再解析の原典（接地ではない・事実の確かめ用。context-A の一覧に入れた）

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Alaboudi & LaToza (2021). arXiv:2105.02162v1（D1 のプレプリント） | `0221981324b04cb1…`（round 1 と一致） | `tmp\sources\alaboudi2021.txt` |
| Li & Coblenz (2026). arXiv:2602.11435v3（D2） | `4b3ba562ae43c845…`（一致） | `tmp\sources\li2026.txt` |

## 3 つの立場が違う角度であること

R1 は測定の妥当性（概念と指標・コードの転用・コーダーの信頼性）、R2 は使う側（debugging と助けを求める行動の研究者の問い・持ち帰り）、R3 は手続きと推論（経験的研究の基準・再現・LLM の利用の報告・少ないクラスタの推論）。系譜は round 1 と同じく重ならない（R3 の統計の文献だけが、ブートストラップの教育から計量経済学のクラスタ頑健推論に替わった）。
