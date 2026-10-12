# panel（round 1・2026-10-12）

本文は `tmp/raw/`（原本）と `tmp/sources/`（テキスト）に置いた（git が無視する。`git check-ignore` で確かめた）。確認済み = OpenAlex の記録で題・筆頭著者・年が一致し `open_access.is_oa` が真。

## R1 打鍵の側路・匿名化の攻撃と防御の専門家（セキュリティの測定の伝統）

下位人格: 「その攻撃は本当に最も強い攻撃か・その加工は攻撃者が適応しても効くか」を疑う懐疑家。

| 文献 | OpenAlex | 原本 | SHA-256 | テキスト |
|---|---|---|---|---|
| Monaco, J. V. & Tappert, C. C. — Obfuscating Keystroke Time Intervals to Avoid Identification and Impersonation（arXiv 1609.07612, 2016） | 確認済み（is_oa 真・oa_url arXiv） | https://arxiv.org/pdf/1609.07612 | 0432655c49c838923c4a75fa7709689b6c2151348fad5c219541a355c63af5e7 | `tmp/sources/monaco2017.txt`（8 頁） |
| Monaco, J. V. — What Are You Searching For? A Remote Keylogging Attack on Search Engine Autocomplete（USENIX Security 2019） | OpenAlex は closed（W2966813956）。USENIX の公開版で代えた（題・筆頭著者が一致） | https://www.usenix.org/system/files/sec19-monaco.pdf | a62d8d90c738a1bf705283637f60f47b11aadfdb3e04792ba4c922590ce83bc0 | `tmp/sources/monaco2019.txt`（19 頁） |
| Qiu, M. et al. — KeyTAR: Practical Keystroke Timing Attacks and Input Reconstruction（IEEE S&P 2026） | OpenAlex は closed（W7166823774）。著者のページの camera-ready で代えた（題・筆頭著者が一致） | https://andrewkwong.org/docs/keytar-camera.pdf | dc78bb28c4f9ae956df94764bf14612d705af39a1d034bdc7c0be45487eb5de4 | `tmp/sources/keytar2026.txt`（20 頁） |

逸脱: R1 の 3 本のうち 2 本は OpenAlex で is_oa が偽（出版社・著者の公開版は無料で読める）。Skill の「oa_url が取れないときは著者・所属機関の公開版で代えてよい」に当たるとして使った。Leinonen ら 2017（L@S・is_oa 真）は oa_url が Cloudflare の人間確認で取れず外した。

## R2 作文研究（打鍵の記録の利用者）の専門家

下位人格: 「その加工の後に、作文研究で使う指標は本当に残るのか。読者（記録を公開する側）は何を明日から変えればよいのか」と問う実務家。

| 文献 | OpenAlex | 原本 | SHA-256 | テキスト |
|---|---|---|---|---|
| Tian, Y., Crossley, S. A. & Van Waes, L. — The KLiCKe corpus（Journal of Writing Research 17(1), 2025） | 確認済み | https://www.jowr.org/jowr/article/download/1556/993 | 48fb8d6667e53257306716766ca0cf8f28639988dafa8ccc17b15cbbf638c732 | `tmp/sources/klicke2025.txt`（38 頁） |
| Conijn, R. et al. — Understanding the keystroke log: the effect of writing task on keystroke features（Reading and Writing 32, 2019） | 確認済み | https://link.springer.com/content/pdf/10.1007/s11145-019-09953-8.pdf | 76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196 | `tmp/sources/conijn2019.txt`（22 頁） |

Galbraith & Baaijen 2019（is_oa 真）は oa_url が Cloudflare の人間確認で取れず外した。

## R3 プライバシーの評価の方法論と事前登録の番人

下位人格: 過剰主張と検証できない手順の摘発者。

| 文献 | OpenAlex | 原本 | SHA-256 | テキスト |
|---|---|---|---|---|
| Wagner, I. & Eckhoff, D. — Technical Privacy Metrics: a Systematic Survey（arXiv 1512.00327・ACM CSUR 2018 の著者版） | 確認済み | https://arxiv.org/pdf/1512.00327 | c5424575f7580807b369766c6aac2fc1087a1b47e8d7e54df22d76830c1af920 | `tmp/sources/wagner2015.txt`（45 頁） |
| Nosek, B. A. et al. — The preregistration revolution（PNAS 115(11), 2018） | 確認済み（PMC） | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5856500/ | 90b934e0d00ebfc195311fc9227a6864df857a76c8096dd9195b2c0939d1e1ec | `tmp/sources/nosek2018.txt`（HTML） |

3 つの立場の角度: R1 = 攻撃者の強さ（セキュリティ）／ R2 = 記録の利用者の有用性（作文研究）／ R3 = 評価の指標と事前登録の固定（方法論）。系譜は重ならない。
