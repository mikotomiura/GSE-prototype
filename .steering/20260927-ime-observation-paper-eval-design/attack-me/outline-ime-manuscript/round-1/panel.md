# panel — 3 つの立場と接地の文献（attack-me・stage `outline`・round 1）

作成: 2026-10-04（G-GEAR・メイン）。書誌は OpenAlex の記録（`https://api.openalex.org/works/doi:<DOI>`・`curl -s` で JSON のまま取得）で、題・筆頭著者・年・DOI が一致し、`open_access.is_oa` が真で `oa_url` があることを確かめた（＝確認済み）。本文はメインが取得してテキストにし、本文の先頭の題が書誌と一致したもの（＝読めた）だけを数える。本文は印字していない（先頭の約 110 字・頁数・文字数だけ）。
本文テキストの置き場: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-1\tmp\sources\`（root の `.gitignore` の `tmp/` が無視する・`git check-ignore -v` で確かめた）。

検索語: 新しい検索はしていない。R1・R2 の 5 本は stage `prereg`（round 1〜5・同じ論文の事前登録）で確認した文献を取り直した。R2 の 1 本と R3 の 3 本は、立場の一般語（non-alphabetic keystroke logging / datasheets for datasets / FAIR data principles / researcher degrees of freedom）で既知の文献を OpenAlex の DOI で引いた。対象物の文・数値は検索に入れていない。

★ stage `outline` の重み（a 主張と根拠・c 持ち帰れるもの・f 先行研究の位置づけ）に合わせ、R2 に非アルファベットの書字の打鍵記録の文献を、R3 にデータの公開の文献を入れた（データセットを貢献に加えたため）。

## R1 — 手法の核: 打鍵の時刻を測る道具の検証（計測の伝統）

- 立場: 心理学の実験で打鍵や反応の時刻を測る道具の精度を、外部の基準で検証してきた方法論の伝統の査読者。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性を疑う）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Pinet, S., Zielinski, C., Mathôt, S., Dufau, S., Alario, F.-X., & Longcamp, M. (2017). Measuring sequences of keystrokes with jsPsych: Reliability of response times and interkeystroke intervals. *Behavior Research Methods, 49*, 1163–1176. doi:10.3758/s13428-016-0776-3（OpenAlex の年は 2016） | 確認済み | 読めた（14 頁・53,650 字） | `https://link.springer.com/content/pdf/10.3758/s13428-016-0776-3.pdf` | `5b22bf8d38958e8d0526d0465bd0079cb2bc213156ffa41b28a576be42943ec2` | `tmp\sources\pinet2016.txt` |
| Bridges, D., Pitiot, A., MacAskill, M. R., & Peirce, J. W. (2020). The timing mega-study. *PeerJ, 8*, e9414. doi:10.7717/peerj.9414 | 確認済み | 読めた（87,177 字） | Europe PMC の全文 XML（PMC7512138）（`oa_url` の peerj は前回 403） | `25dcabfc1a05f3e4b4c9aab20adbc97d2980d01e2bc468d1c8c2bb53040e6d9f`（XML） | `tmp\sources\bridges2020.txt`（参考文献の一覧は除いた） |
| Plant, R. R. (2016). A reminder on millisecond timing accuracy and potential replication failure in computer-based psychology experiments. *Behavior Research Methods, 48*, 408–411. doi:10.3758/s13428-015-0577-0（OpenAlex の年は 2015） | 確認済み | 読めた（4 頁・21,330 字） | `https://link.springer.com/content/pdf/10.3758/s13428-015-0577-0.pdf` | `7913cbac645fcf6858e0282e4253e73f9e53a35cea3a609ca53824806ad61fef` | `tmp\sources\plant2016.txt` |

## R2 — 隣接分野: 打鍵記録を使う書字過程の研究者（非アルファベットの書字と記録の公開の安全を含む）

- 立場: 打鍵記録から書字過程の指標を計算して使う書字研究の利用者で、入力方式を通して書く言語の記録の道具と、打鍵の記録から内容が漏れる経路にも通じた査読者。
- 下位人格: 「で、読者は何に使えるのか」と問う実務家（冗長さに厳しく、先行の道具との比べ方が公平か、推奨が実際に使えるかを問う）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Conijn, R., Roeser, J., & van Zaanen, M. (2019). Understanding the keystroke log: the effect of writing task on keystroke features. *Reading and Writing, 32*, 2353–2374. doi:10.1007/s11145-019-09953-8 | 確認済み | 読めた（22 頁・70,383 字） | `https://link.springer.com/content/pdf/10.1007/s11145-019-09953-8.pdf` | `76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196` | `tmp\sources\conijn2019.txt` |
| Monaco, J. V. (2018). SoK: Keylogging side channels. In *2018 IEEE Symposium on Security and Privacy* (pp. 211–228). doi:10.1109/SP.2018.00026 | 確認済み | 読めた（18 頁・118,041 字） | `https://ieeexplore.ieee.org/ielx7/8418581/8418583/08418605.pdf` | `af13534fea80e2cb2b75713da2c4d4ca05d27c87590dbfd296d9be54e8524aa5` | `tmp\sources\monaco2018.txt` |
| Crotti, R., Denaro, G., Du, Z., & Muñoz Martín, R. (2026). Hylog: A hybrid approach to logging text production in non-alphabetic scripts. *IEEE Access, 14*, 117046–117067. doi:10.1109/ACCESS.2026.3718565 | 確認済み | 読めた（21 頁・104,219 字） | ⚠️ `oa_url`（doi.org）ではなく **arXiv の accepted version（arXiv:2601.17753）で代えた**（題・筆頭著者が一致） | `f17f901b5b406c02c48d65641e208b1999c35362630e210cf63db33bfacb9d52` | `tmp\sources\crotti2026.txt` |

- ⚠️ Crotti ら（2026）は外枠が §2 で比べる相手の 1 つである（自分たちの論文ではない）。比べ方が公平か（評価表 f）を、比べる相手の本文で確かめさせるために入れた。

## R3 — 投稿先の方法論と再現性の番人（事前登録・データと材料の公開）

- 立場: 事前登録の具体性・研究者の自由度と、データと材料の公開（説明書・再利用の条件）を審査する、メタサイエンスとデータ管理の方法論の査読者。
- 下位人格: 過剰主張と検証できない手順の摘発者（根拠より強い言い方・事前に決まっていない分岐・再利用できない公開を探す）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Wicherts, J. M., et al. (2016). Degrees of freedom in planning, running, analyzing, and reporting psychological studies: A checklist to avoid p-hacking. *Frontiers in Psychology, 7*, 1832. doi:10.3389/fpsyg.2016.01832 | 確認済み | 読めた（12 頁・73,089 字） | `https://www.frontiersin.org/articles/10.3389/fpsyg.2016.01832/pdf` | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp\sources\wicherts2016.txt` |
| Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86–92. doi:10.1145/3458723 | 確認済み | 読めた（18 頁・56,662 字） | `https://arxiv.org/pdf/1803.09010`（OpenAlex の `oa_url`・arXiv の版） | `c7f595988ee2c109631d5173fdae37ff1774c68ec17add51bd012f2a6e8792d0` | `tmp\sources\gebru2021.txt` |
| Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data, 3*, 160018. doi:10.1038/sdata.2016.18 | 確認済み | 読めた（9 頁・47,064 字） | `https://www.nature.com/articles/sdata201618.pdf` | `cdddd9f4808f7e3e1f013139c3915ef4d7cdccb008fa947ef5f72b4c7b6ffde7` | `tmp\sources\wilkinson2016.txt` |

- ⚠️ Gebru ら（2021）は外枠が §10 で引く予定の文献でもある（説明書の形）。R3 には「説明書の形を本当に満たしているか」を見させる。
- ★ 書誌の巻・頁（Gebru ら・Wilkinson ら・Crotti ら）は OpenAlex で題・筆頭著者・年・DOI を確かめた範囲で、巻・頁は論文で引くときに citation-ssot で確かめる。

## 3 つの立場が違う角度であること

R1 は**計測の道具の妥当性**（基準・時刻・検証の設計）、R2 は**指標を使う側と先行の道具との比べ方・公開の安全**（書字研究と非アルファベットの記録とセキュリティ）、R3 は**推論の固定とデータの公開**（メタサイエンスとデータ管理）。系譜が重ならない。

## 機械の上の封印物と秘密のファイル（起動の前に研究者に知らせた）

この機械（G-GEAR）には、Windows パイロットの最初の試しの生ログと封印（`C:/ime-pilot-win/runs/*/sealed/`・`pilot-windows-ggear-notes.md` の 72 行）と、Zenodo のトークン（memory の参照）がある。査読者役の `Read` は構造では縛れないので、依頼文で読んでよいファイルを限り、応答の保存の検査（絶対パスの突き合わせ）で止める。
