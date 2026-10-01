# panel — 3 つの立場と接地の文献（attack-me・stage `manuscript`・round 1）

作成: 2026-10-02（G-GEAR・メイン）。書誌は OpenAlex の記録（`https://api.openalex.org/works/doi:<DOI>`・JSON のまま取得）で題・筆頭著者・年・DOI が一致し、`open_access.is_oa` が真で無料の版があることを確かめた（＝確認済み）。本文はメインが取得してテキストにし、本文の題が書誌と一致したもの（＝読めた）だけを数える。本文は印字していない（先頭の 2 行・頁数・文字数だけ）。
本文テキストの置き場: `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\sources\`（root の `.gitignore` の `tmp/` が無視する・`git check-ignore -v` で確かめた）。

検索は DOI での照会だけ（立場と手法の一般語で候補を挙げ、OpenAlex を DOI で引いた）。対象物の文・数値は検索に入れていない。
★ 対象物が自分で引いている文献（Sjøberg & Bergersen 2022・Hellas et al. 2023・Hesterberg 2015）も接地に入れた。対象物がその基準に本当に従っているかを、その伝統の査読者が確かめるため（自分たちの論文・内部の文書ではない）。

## R1 — 手法の核: ソフトウェア工学の測定の妥当性と、質的なコーディングを量として再利用することの伝統

- 立場: 構成概念妥当性（概念と指標の対応・指標の過少代表と偏り）の方法論と、質的研究のコーディングの信頼性の議論に通じた、経験的ソフトウェア工学の測定の査読者。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（元の研究者が別の目的で付けたコードを、別の概念の指標として転用してよいのか／1 名のコーダーのコードを数えてよいのか／「妥当性の節」がガイドラインの形式をなぞっているだけではないか）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Sjøberg, D. I. K., & Bergersen, G. R. (2023). Construct validity in software engineering. *IEEE Transactions on Software Engineering, 49*(3), 1374–1396. doi:10.1109/TSE.2022.3176725（OpenAlex の年は 2022 = オンライン公開） | 確認済み | 読めた（23 頁・141,444 字） | `https://ieeexplore.ieee.org/ielx7/32/10070338/09780058.pdf`（OpenAlex の `oa_url`） | `457858d6af60ccdef5f457a0e477e9773c55a25aa6af8f612bb532c994d0fc29` | `tmp\sources\sjoberg2022.txt` |
| Sjøberg, D. I. K., & Bergersen, G. R. (2023). Improving the reporting of threats to construct validity. In *Proceedings of EASE 2023* (pp. 205–209). doi:10.1145/3593434.3593449 | 確認済み | 読めた（5 頁・26,880 字） | ⚠️ `oa_url`（ACM の PDF）は試していない → **arXiv の版（arXiv:2306.05336・OpenAlex の記録で同じ題・同じ筆頭著者）で代えた** | `50f8ab3ab7e5261c6cf52e2158c7e25b98437dfc29b6c34f39d9957568051b84` | `tmp\sources\sjoberg2023.txt` |
| O'Connor, C., & Joffe, H. (2020). Intercoder reliability in qualitative research: Debates and practical guidelines. *International Journal of Qualitative Methods, 19*. doi:10.1177/1609406919899220 | 確認済み | 読めた（13 頁・72,170 字） | ⚠️ `oa_url`（doi.org → SAGE の PDF）は 403 → **UCL Discovery の版（OpenAlex の OA の所在の 1 つ・`https://discovery.ucl.ac.uk/id/eprint/10091273/1/1609406919899220.pdf`）で代えた**（題・筆頭著者が一致） | `1ff859a271acf5ee9f3ca4a09e1da9bff12752d43c472421d3e819a63997a4bb` | `tmp\sources\oconnor2020.txt` |

- 試して使えなかった候補: Ralph & Tempero (2018, EASE・doi:10.1145/3210459.3210461) は `is_oa` が偽 → 使わない。McDonald, Schoenebeck & Forte (2019, PACM HCI・doi:10.1145/3359174) は `oa_url`（ACM）が 403 で他の所在なし → 使わない。

## R2 — 隣接分野: 開発者の debugging と助けを求める行動を観察する研究者（道具を作る側・利用者の側）

- 立場: IDE の中での debugging の実際の振る舞いや、プログラマーの助けの求め方を観察・記録して、道具の設計や教育に生かしてきた、プログラミングの人間の側（HCI・計算機教育を含む）の査読者。
- 下位人格: 「で、読者は何に使えるのか」と問う実務家／冗長さに厳しい読者（提言が、観察研究を設計する人・データを再利用する人・道具を評価する人にとって具体的か。21 頁の再解析に見合う持ち帰りがあるか）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Beller, M., Spruit, N., Spinellis, D., & Zaidman, A. (2018). On the dichotomy of debugging behavior among programmers. In *Proceedings of ICSE 2018* (pp. 572–583). doi:10.1145/3180155.3180175 | 確認済み | 読めた（14 頁・79,840 字・冒頭に TU Delft の表紙が 1 頁ある） | TU Delft Repository（OpenAlex の `oa_url` = `resolver.tudelft.nl/uuid:82fbe2e2-…` → `https://repository.tudelft.nl/file/File_d0b41a0e-4399-4ebb-b0c8-de683b68d2da`） | `b4b33224bac1b75cb93977bfb32b4aedd653983ba66b691e63b521115e2927c1` | `tmp\sources\beller2018.txt` |
| Hellas, A., Leinonen, J., Sarsa, S., Koutcheme, C., Kujanpää, L., & Sorva, J. (2023). Exploring the responses of large language models to beginner programmers' help requests. In *Proceedings of ICER 2023* (pp. 93–105). doi:10.1145/3568813.3600139 | 確認済み | 読めた（13 頁・81,307 字） | arXiv の版（arXiv:2306.05715・OpenAlex の OA の所在の 1 つ） | `388d55ee283d17d2866d036c7983c46bd3848fcd9406468a68e5d19c11eb7a9a` | `tmp\sources\hellas2023.txt` |

- 試して使えなかった候補: Sadowski, Stolee & Elbaum (2015, FSE・doi:10.1145/2786805.2786855) は `oa_url`（ACM）が 403 → 使わない。Xia et al. (2017, EMSE・doi:10.1007/s10664-017-9514-4) は `oa_url`（SMU の機関リポジトリ）がボット避けの頁を返した → 使わない。Ko, LaToza & Burnett (2015, EMSE)・Aleven et al. (2003, RER)・Lo et al. (2015, FSE) は `is_oa` が偽 → 使わない。R2 は 2 本（必要な本数を満たす）。

## R3 — 投稿先の方法論と再現性の番人（経験的研究の基準・オープンサイエンス・LLM の利用・統計）

- 立場: ソフトウェア工学の経験的研究の基準（ACM SIGSOFT Empirical Standards の一般基準・再現・メタ科学・オープンサイエンス・二次データの倫理）と、研究での LLM の利用の報告、対象物が使う統計手法（ブートストラップ）の方法論に通じた査読者。
- 下位人格: 過剰主張と検証できない手順の摘発者（事前に決まっていない分岐・後から選べる定義・小さな標本からの一般化・LLM が生成した転記やコードの検証の甘さを探す）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Ralph, P., et al. (2020). Empirical standards for software engineering research. arXiv:2010.03525（ACM SIGSOFT Paper and Peer Review Quality Task Force） | 確認済み | 読めた（52,071 B の Markdown） | ⚠️ `oa_url`（arXiv の PDF・v0.2.0・20 頁）は取得できたが、基準の本体を収めていない概要の文書だった（PDF 自身が基準の本体として GitHub のリポジトリを示す）→ **その公式リポジトリ `acmsigsoft/EmpiricalStandards` のコミット `554118c6b60580aeba4cbe1222fbe12df5e62171` から、該当する基準 6 つ（standards: GeneralStandard・Replication・MetaScience ／ supplements: OpenScience・EthicsSecondaryData・Sampling）を連結した版で代えた** | `580abe323e675369835f15c62640bd0dc273df6de214943724b7106f3281ea87`（連結した Markdown）／ 参考: arXiv の PDF `ba3bb87a00acdc868b3d777c9fdabc2ef7ba2f9d908d51f65eef8e1fc71fbeca` | `tmp\sources\empirical-standards.txt` |
| Wagner, S., Muñoz Barón, M., Falessi, D., & Baltes, S. (2025). Towards evaluation guidelines for empirical studies involving LLMs. arXiv:2411.07668v3 | 確認済み | 読めた（4 頁・25,376 字） | `https://arxiv.org/pdf/2411.07668`（OpenAlex の `oa_url`） | `cf58e03aaf7721ec31496ae881e3835fb52006eaa055f8a8f1f6fa0a4e23fd9a` | `tmp\sources\wagner2024.txt` |
| Hesterberg, T. C. (2015). What teachers should know about the bootstrap: Resampling in the undergraduate statistics curriculum. *The American Statistician, 69*(4), 371–386. doi:10.1080/00031305.2015.1089789（対象物が使う統計手法そのものの方法論） | 確認済み | 読めた（83 頁・145,975 字） | arXiv の版（arXiv:1411.5279・OpenAlex の記録で同じ題・同じ著者・`is_oa` 真） | `80e30e7435f9860a584d7d0da5859b97f00d0c9cea2d1ca81dc1f51f42532430` | `tmp\sources\hesterberg2015.txt` |

- 取得したが使わない候補: Méndez, Graziotin, Wagner & Seibold (2020, *Contemporary Empirical Methods in SE*・doi:10.1007/978-3-030-32489-6_17・OA）。R3 の 3 本に収めるため取得していない（round 2 で替えが要れば使う）。Baltes & Ralph (2022)・Cameron & Miller (2015)・Brown et al. (2001) は `is_oa` が偽 → 使わない。

## 再解析の原典（接地ではない・事実の確かめ用。context-A の一覧に入れた）

| 文献 | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|
| Alaboudi & LaToza (2021). An exploratory study of debugging episodes. arXiv:2105.02162v1（D1 のプレプリント） | `https://arxiv.org/pdf/2105.02162v1` | `0221981324b04cb17b3b2455e3f5bebac2bbfa2abccab30797b8abf6d57fb728` | `tmp\sources\alaboudi2021.txt`（11 頁） |
| Li & Coblenz (2026). A grounded theory of debugging in professional software engineering practice. arXiv:2602.11435v3（D2・原稿が転記した版。OpenAlex の記録 doi:10.1145/3797077 の OA の所在） | 論文用リポジトリの `raw/` にあった PDF を写した | `4b3ba562ae43c845dcba37845503cd199a79a781b8bb5670991793785352337f` | `tmp\sources\li2026.txt`（22 頁） |

- ⚠️ D1 の journal 版（doi:10.1007/s10664-023-10352-5）は `is_oa` が偽 → 渡さない。

## 3 つの立場が違う角度であること

- R1 は**測定の妥当性**（概念と指標・コードの転用・コーダーの信頼性）、R2 は**使う側**（debugging と助けを求める行動を観察して道具や教育に生かす研究者の問い・持ち帰り）、R3 は**手続きと推論**（経験的研究の基準・再現・LLM の利用の報告・ブートストラップ）。系譜が重ならない（R1 は SE の測定論と質的研究の方法論、R2 は IDE の行動計測と計算機教育、R3 は SIGSOFT の基準・LLM 研究の評価指針・統計）。
