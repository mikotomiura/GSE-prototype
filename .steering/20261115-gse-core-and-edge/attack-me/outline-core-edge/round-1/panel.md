# panel —— attack-me・stage `outline`・対象物 `docs/mitou_submission/core-and-edge-material.md`・round 1

作成: 2026-11-15（Mac・メイン）。対象物は commit `bc8e936a`（枝 `docs/gse-core-and-edge`）。投稿先は 2027 年度未踏 IT 人材発掘・育成事業（応募の素材で、応募書類そのものではない）。

- 原本: `round-1/tmp/raw/`・本文テキスト: `round-1/tmp/sources/`（root の `.gitignore` 244 行の `tmp/` が無視する）。本文は印字していない（題の確認に先頭の数行と文字数だけ）。
- 書誌の確認は OpenAlex（`https://api.openalex.org/works/doi:<DOI>`）の題・筆頭著者・年・`is_oa`。

## 取得の逸脱

- 当初の R1 の候補 Conijn ら（2019・doi:10.1007/s11145-019-09953-8）と Monaco（2018・doi:10.1109/SP.2018.00026）は、Springer の PDF が HTML の転送で返り、取り直しの試みの 1 つが auto mode の判定で止められた。回り込まず、2 本を外して下の 2 本に替えた。
- Amershi ら（2019）・Horvitz（1999 CHI）・Steegen ら（2016）は OpenAlex で `is_oa` が偽だったので使わない。

## R1 —— 手法の核: 打鍵記録で休止を定義し、打鍵の記録から何が推測されるかを扱う計測の伝統

- 立場: 打鍵記録（keystroke logging）で書字の休止を定義・測定してきた方法論の伝統と、行動生体データ（打鍵の時刻を含む）から本人や内容が推測される経路と匿名化の技法に通じた査読者。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家。

| 文献 | 確認 | 原本 SHA-256 | 本文 |
|---|---|---|---|
| Chukharev-Hudilainen（2014）Journal of Writing Research 6(1)・doi:10.17239/jowr-2014.06.01.3（jowr.org の記事の PDF） | OpenAlex 一致・OA | `d9851d50354d0415e91b935a190450100024bb4eb46161f501dd921f12ca9f2a` | `tmp/sources/chukharev2014.txt`（68,772 字） |
| Hanisch ら（arXiv:2109.04120・OpenAlex の題は公刊版の "Anonymization Techniques for Behavioral Biometric Data: A Survey"・本文の題は "Privacy-Protecting Techniques for Behavioral Biometric Data: A Survey"） | OpenAlex 一致（arXiv の DOI）・OA | `2922e10a8ae31281a3b4552d84af4492372dccf24f3d4bb37c3aed7f61eed54b` | `tmp/sources/hanisch2021.txt`（198,405 字） |

## R2 —— 隣接分野: 注意・中断を扱う HCI と、受動センシングで本人の状態を推す応用の実務家

- 立場: 利用者の注意の状態を推して通知や介入の時機を決める系（mixed-initiative・attention-sensitive）と、受動センシングと申告を組み合わせた 1 人ごとの推定を作って使ってきた応用の研究者。
- 下位人格: 「で、読者は何に使えるのか・何を作るのか」と問う実務家。

| 文献 | 確認 | 原本 SHA-256 | 本文 |
|---|---|---|---|
| Horvitz, Jacobs & Hovel — Attention-Sensitive Alerting（UAI 1999・arXiv:1301.6707） | OpenAlex 一致（arXiv の DOI・2013）・OA | `95748281d1a851cc26672d5938e08d3566eb6abd2ed828aee2d1ccc64bb02ada` | `tmp/sources/horvitz1999.txt`（41,496 字） |
| Hart ら（2022）J Med Internet Res 24(4):e34015・doi:10.2196/34015（Europe PMC の全文 XML・PMC9100543） | OpenAlex 一致・OA | `a97a79dbed5c0c318407b76af21cfdb08cb8077d84df93a2a4064d6a142101a9`（XML） | `tmp/sources/hart2022.txt`（76,642 字） |

## R3 —— 方法論と再現性の番人（研究者の自由度・同等性の判定）

- 立場: 事前登録と研究者の自由度、同等性の検定の報告を審査するメタサイエンスの査読者。
- 下位人格: 過剰主張と検証できない手順の摘発者。

| 文献 | 確認 | 原本 SHA-256 | 本文 |
|---|---|---|---|
| Wicherts ら（2016）Frontiers in Psychology・doi:10.3389/fpsyg.2016.01832 | OpenAlex 一致・OA（SHA-256 は IME 論文の round の記録と一致） | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp/sources/wicherts2016.txt`（72,946 字） |
| Lakens（2017）Social Psychological and Personality Science・doi:10.1177/1948550617697177（PMC5502906 の HTML） | OpenAlex 一致・OA | `8b085a1204c7ea08b3918d5993df88734370341dacf8c005ab722c415f785637`（HTML） | `tmp/sources/lakens2017.txt`（45,114 字） |

## E —— 編集者の役（未踏 IT の審査で最初に読む者）

| 接地 | 確認 | 本文 |
|---|---|---|
| 2027 年度未踏 IT 人材発掘・育成事業 公募概要（`https://www.ipa.go.jp/jinzai/mitou/it/2027/koubo.html`・公開日 2026-11-09・取得 2026-11-15・curl） | 原文から逐語（下の context-A） | `tmp/sources/mitou-2027-koubo.txt` |
| 同 PM のページ（`.../2027/pm.html`） | curl | `tmp/sources/mitou-2027-pm.txt` |
| Mensh & Kording（2017）PLoS Comput Biol・doi:10.1371/journal.pcbi.1005619 | OpenAlex 一致・OA | `tmp/sources/mensh2017.txt`（30,216 字・SHA-256 `f02a2c14c630369f2058403a448f94e7aaeafb3c1cc681c9d6862812590b7b6c`） |

- 各立場とも「確認済み、かつ読めた」文献が 2 本（必要な本数 2 を満たす）。3 つの立場は、計測・応用・メタサイエンスで系譜が違う。
