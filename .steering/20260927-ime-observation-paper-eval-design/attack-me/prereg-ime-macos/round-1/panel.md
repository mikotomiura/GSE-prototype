# panel — 3 つの立場と接地の文献（attack-me・stage `prereg`・round 1）

作成: 2026-10-01（G-GEAR・メイン）。書誌は OpenAlex の記録（`https://api.openalex.org/works/doi:<DOI>`・`curl` 相当で JSON のまま取得）で、題・筆頭著者・年・DOI が一致し、`open_access.is_oa` が真で `oa_url` があることを確かめた（＝確認済み）。本文はメインが取得してテキストにし、本文の題が書誌と一致したもの（＝読めた）だけを数える。本文は印字していない（先頭の数行・頁数・文字数だけ）。
本文テキストの置き場: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\prereg-ime-macos\round-1\tmp\sources\`（root の `.gitignore` の `tmp/` が無視する・`git check-ignore -v` で確かめた）。

検索語は立場と手法の一般語だけ（keystroke timing accuracy / keystroke logging writing / keylogging side channel / sample size justification / preregistration / intraclass correlation）。対象物の文・数値・仮説は入れていない。

## R1 — 手法の核: 打鍵の時刻を測る道具の検証（計測の伝統）

- 立場: 心理学の実験で打鍵や反応の時刻を測る道具（ソフトウェア・ハードウェア）の精度を、外部の基準で検証してきた方法論の伝統の査読者。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性を疑う）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Pinet, S., Zielinski, C., Mathôt, S., Dufau, S., Alario, F.-X., & Longcamp, M. (2017). Measuring sequences of keystrokes with jsPsych: Reliability of response times and interkeystroke intervals. *Behavior Research Methods, 49*, 1163–1176. doi:10.3758/s13428-016-0776-3（OpenAlex の年は 2016 = オンライン公開） | 確認済み | 読めた（14 頁・53,650 字） | `https://link.springer.com/content/pdf/10.3758/s13428-016-0776-3.pdf` | `5b22bf8d38958e8d0526d0465bd0079cb2bc213156ffa41b28a576be42943ec2` | `tmp\sources\pinet2016.txt` |
| Bridges, D., Pitiot, A., MacAskill, M. R., & Peirce, J. W. (2020). The timing mega-study: comparing a range of experiment generators, both lab-based and online. *PeerJ, 8*, e9414. doi:10.7717/peerj.9414 | 確認済み | 読めた（87,198 字） | ⚠️ `oa_url`（peerj.com の PDF）は 403 → **Europe PMC の全文 XML（PMC7512138）で代えた**（題・筆頭著者が一致） | `25dcabfc1a05f3e4b4c9aab20adbc97d2980d01e2bc468d1c8c2bb53040e6d9f`（XML） | `tmp\sources\bridges2020.txt`（参考文献の一覧は除いた） |
| Plant, R. R. (2016). A reminder on millisecond timing accuracy and potential replication failure in computer-based psychology experiments: An open letter. *Behavior Research Methods, 48*, 408–411. doi:10.3758/s13428-015-0577-0（OpenAlex の年は 2015 = オンライン公開） | 確認済み | 読めた（4 頁・21,330 字） | `https://link.springer.com/content/pdf/10.3758/s13428-015-0577-0.pdf` | `7913cbac645fcf6858e0282e4253e73f9e53a35cea3a609ca53824806ad61fef` | `tmp\sources\plant2016.txt` |

## R2 — 隣接分野: 打鍵記録を使う書字過程の研究者と、行動ログの公開の安全（利用者の側）

- 立場: 打鍵記録から書字過程の指標（休止・修正・産出の速さ）を計算して使う書字研究の利用者で、記録を公開するときに打鍵の時刻から内容が漏れる経路（サイドチャネル）にも通じた査読者。
- 下位人格: 「で、読者は何に使えるのか」と問う実務家（冗長さに厳しく、指標が書字研究の問いに直結しているか、公開の推奨が実際に使えるかを問う）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Conijn, R., Roeser, J., & van Zaanen, M. (2019). Understanding the keystroke log: the effect of writing task on keystroke features. *Reading and Writing, 32*, 2353–2374. doi:10.1007/s11145-019-09953-8 | 確認済み | 読めた（22 頁・70,383 字） | `https://link.springer.com/content/pdf/10.1007/s11145-019-09953-8.pdf` | `76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196` | `tmp\sources\conijn2019.txt` |
| Monaco, J. V. (2018). SoK: Keylogging side channels. In *2018 IEEE Symposium on Security and Privacy* (pp. 211–228). doi:10.1109/SP.2018.00026 | 確認済み | 読めた（18 頁・118,041 字） | `https://ieeexplore.ieee.org/ielx7/8418581/8418583/08418605.pdf`（OpenAlex の `oa_url`） | `af13534fea80e2cb2b75713da2c4d4ca05d27c87590dbfd296d9be54e8524aa5` | `tmp\sources\monaco2018.txt` |

- 試して使えなかった候補: Leijten & Van Waes (2013, *Written Communication*・doi:10.1177/0741088313491692) は OpenAlex で `is_oa` が偽 → 使わない。Galbraith & Baaijen (2019, *Observing Writing*・doi:10.1163/9789004392526_015) は `oa_url`（research.rug.nl）が 403 → 使わない。R2 は 2 本（必要な本数を満たす）。

## R3 — 投稿先の方法論と再現性の番人（統計・事前登録・規程）

- 立場: 事前登録の具体性・研究者の自由度・標本の大きさの根拠を審査する、メタサイエンスと統計の方法論の査読者。対象物が名指しする一致度の指標（ICC）の方法論にも通じる。
- 下位人格: 過剰主張と検証できない手順の摘発者（事前に 1 通りに決まっていない分岐・根拠の無い n・後から選べる指標を探す）。

| 文献 | 確認 | 読めた | 取得元 | 原本 SHA-256 | 本文 |
|---|---|---|---|---|---|
| Lakens, D. (2022). Sample size justification. *Collabra: Psychology, 8*(1), 33267. doi:10.1525/collabra.33267 | 確認済み | 読めた（32 頁・147,824 字） | ⚠️ `oa_url`（ucpress の PDF）は 403 → **著者の公開版（PsyArXiv / OSF `9d3yf`・冒頭に "Please cite as D. Lakens (2022). Sample Size Justification. Collabra: Psychology"）で代えた**（題・著者が一致） | `9346742b1e4e33d8da1433b583e8cd1f09f13006cea60c910d68b4b2ceca2648` | `tmp\sources\lakens2022.txt` |
| Wicherts, J. M., Veldkamp, C. L. S., Augusteijn, H. E. M., Bakker, M., van Aert, R. C. M., & van Assen, M. A. L. M. (2016). Degrees of freedom in planning, running, analyzing, and reporting psychological studies: A checklist to avoid p-hacking. *Frontiers in Psychology, 7*, 1832. doi:10.3389/fpsyg.2016.01832 | 確認済み | 読めた（12 頁・73,089 字） | `https://www.frontiersin.org/articles/10.3389/fpsyg.2016.01832/pdf` | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp\sources\wicherts2016.txt` |
| Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine, 15*(2), 155–163. doi:10.1016/j.jcm.2016.02.012（対象物が使う統計手法そのものの方法論） | 確認済み | 読めた（26,112 字） | ⚠️ `oa_url`（sciencedirect）ではなく **PubMed Central の HTML（PMC4913118）で代えた**（題・筆頭著者が一致） | `dd4ff4936b088b148b0575ba19e5627272347e19e51b34a959f14b8140bb2292`（HTML） | `tmp\sources\koo2016.txt`（参考文献の一覧は除いた） |

- 取得したが使わない: Bakker et al. (2020, *PLOS Biology*・doi:10.1371/journal.pbio.3000937・読めた・`tmp\sources\bakker2020.txt`）。R3 の 3 本に収めるため外した（round 2 で替えが要れば使う）。

## 3 つの立場が違う角度であること

- R1 は**計測の道具の妥当性**（基準・時刻の精度・検証の設計）、R2 は**指標を使う側と公開の安全**（書字研究の問いへの接続・漏洩の脅威の現実性）、R3 は**推論の固定と統計**（分析者の自由度・n の根拠・ICC）。系譜が重ならない（R1 は実験心理の道具の検証、R2 は書字研究とセキュリティ、R3 はメタサイエンス）。
