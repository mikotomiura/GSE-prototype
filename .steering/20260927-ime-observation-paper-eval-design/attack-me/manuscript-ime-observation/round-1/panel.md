# panel — 3 つの立場と接地の文献（attack-me・stage `manuscript`・round 1）

作成: 2026-10-05 夜（G-GEAR・メイン）。対象物は原稿の全体（`papers/ime-observation/manuscript/`）。

★ 立場と下位人格は、外枠の attack-me（`attack-me/outline-ime-manuscript/round-1/panel.md`・round 2 も同じ）と**同じ 3 つ**にした。外枠の round 1・2 の指摘を引き継いで解消を判定させるため（判断 150-4）。
★ 文献は stage が変わったので組み直した（Skill の「同じ文献で回す」は同じ stage の round 2 以降の規則）。外枠の 9 本のうち 7 本を残し、2 本を統計の方法論の文献に替えた。

| 役 | 外した文献 | 代わりに入れた文献 | 理由 |
|---|---|---|---|
| R1 | Bridges ら（2020）PeerJ（時刻の精度の大規模な比較） | Giavarina（2015）Biochemia Medica（Bland–Altman の解説） | 原稿の主の推定は、ロガーと参照の**方法の比較**（`dwell_ms` の偏りと一致の限界）。計時の検証の系譜は Pinet と Plant で残る。Bridges は 87,181 字と長く、原稿の全体（約 21,000 語）と合わせると締切に収まりにくい |
| R3 | Wilkinson ら（2016）FAIR | Koo & Li（2016）ICC の選び方と報告の指針 | Skill Step 1「`manuscript` では、対象物が使う統計手法そのものの方法論の論文を入れることを勧める」。原稿は ICC(A,1)・kappa・Wilson・一致の限界を使う。データの公開は Gebru（説明書）と規程（type 4・TOP Level 2）で見られる。寄託はまだ（DOI は `\tbd`） |

## 新しく入れた 2 本の確認（OpenAlex・`curl -s` で JSON のまま取得・2026-10-05）

- 検索語: 新しい検索はしていない。統計手法の一般語（intraclass correlation reporting guideline / Bland–Altman agreement）で既知の文献を、OpenAlex の DOI で引いた。対象物の文・数値は検索に入れていない。
- **Koo, T. K., & Li, M. Y. (2016).** A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine, 15*(2), 155–163. doi:10.1016/j.jcm.2016.02.012
  - OpenAlex: 題・筆頭著者（Terry K. K. Koo）・年（2016）・DOI が一致。`open_access.is_oa` = true、`oa_url` = sciencedirect → **確認済み**。
  - 本文: `oa_url`（ScienceDirect）ではなく、**PubMed Central の公開版で代えた**（`https://pmc.ncbi.nlm.nih.gov/articles/PMC4913118/`・OpenAlex の locations に在る）。題が一致 → **読めた**。⚠️ Europe PMC の全文 XML は 500、NCBI efetch の XML は要旨だけ（8 KB）だったので使っていない。
- **Giavarina, D. (2015).** Understanding Bland Altman analysis. *Biochemia Medica, 25*(2), 141–151. doi:10.11613/BM.2015.015
  - OpenAlex: 題・筆頭著者（Davide Giavarina）・年（2015）・DOI が一致。`is_oa` = true、`oa_url` = 誌の PDF → **確認済み**。本文の題が一致 → **読めた**（11 頁）。
- ★ 巻・頁は OpenAlex で確かめた範囲の外（論文で引くときに citation-ssot で確かめる）。

## 立場・文献・原本と本文の置き場（この round）

- 原本: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-1\tmp\raw\`
- 本文テキスト: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-1\tmp\sources\`
- ★ 外枠から残した 7 本は、外枠の round 2 の `tmp/` から原本を写し、**SHA-256 が外枠の `panel.md` の記録と一致する**ことを `sha256sum` で確かめた（本文テキストは原本から決まる抽出なので一緒に写した）。本文は印字していない（先頭の約 110〜160 字・頁数・文字数だけ）。
- `git check-ignore -v` で `round-1/tmp/sources/` が root の `.gitignore` の `tmp/`（244 行）に無視されることを確かめた。

### R1 — 手法の核: 打鍵の時刻を測る道具の検証と、方法の比較（計測の伝統）

- 立場: 心理学の実験で打鍵や反応の時刻を測る道具の精度を、外部の基準で検証してきた方法論の伝統の査読者。新しい測定を参照の測定と比べる方法の比較（一致の解析）にも通じている。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性を疑う）。

| 文献 | 原本 SHA-256 | 本文（文字数は `wc -m`） |
|---|---|---|
| Pinet ら（2017）BRM・doi:10.3758/s13428-016-0776-3 | `5b22bf8d38958e8d0526d0465bd0079cb2bc213156ffa41b28a576be42943ec2` | `tmp\sources\pinet2016.txt`（54,622） |
| Plant（2016）BRM・doi:10.3758/s13428-015-0577-0 | `7913cbac645fcf6858e0282e4253e73f9e53a35cea3a609ca53824806ad61fef` | `tmp\sources\plant2016.txt`（21,703） |
| ★ Giavarina（2015）Biochemia Medica・doi:10.11613/BM.2015.015 | `b4bb31955724c37682eb7d3d68ec1f9d2b0c239258473edc306e26f004961321` | `tmp\sources\giavarina2015.txt`（38,486） |

### R2 — 隣接分野: 打鍵記録を使う書字過程の研究者（非アルファベットの書字と記録の公開の安全を含む）

- 立場: 打鍵記録から書字過程の指標を計算して使う書字研究の利用者で、入力方式を通して書く言語の記録の道具と、打鍵の記録から内容が漏れる経路にも通じた査読者。
- 下位人格: 「で、読者は何に使えるのか」と問う実務家（冗長さに厳しく、先行の道具との比べ方が公平か、推奨が実際に使えるかを問う）。

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Conijn ら（2019）Reading and Writing・doi:10.1007/s11145-019-09953-8 | `76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196` | `tmp\sources\conijn2019.txt`（71,432） |
| Monaco（2018）IEEE S&P・doi:10.1109/SP.2018.00026 | `af13534fea80e2cb2b75713da2c4d4ca05d27c87590dbfd296d9be54e8524aa5` | `tmp\sources\monaco2018.txt`（120,002） |
| Crotti ら（2026）IEEE Access・doi:10.1109/ACCESS.2026.3718565（arXiv:2601.17753 の accepted version で代えた・外枠と同じ） | `f17f901b5b406c02c48d65641e208b1999c35362630e210cf63db33bfacb9d52` | `tmp\sources\crotti2026.txt`（106,177） |

- ⚠️ Crotti ら（2026）は原稿が §2 と表 1 で比べる相手（自分たちの論文ではない）。比べ方が公平か（評価表 f）を本文で確かめさせる。

### R3 — 投稿先の方法論と再現性の番人（統計の報告・事前登録・データと材料の公開）

- 立場: 事前登録の具体性・研究者の自由度と、データと材料の公開（説明書・再利用の条件）を審査する、メタサイエンスとデータ管理の方法論の査読者。一致の指標（ICC・kappa・一致の限界）の報告の規範にも通じている。
- 下位人格: 過剰主張と検証できない手順の摘発者（根拠より強い言い方・事前に決まっていない分岐・再利用できない公開を探す）。

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Wicherts ら（2016）Frontiers in Psychology・doi:10.3389/fpsyg.2016.01832 | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp\sources\wicherts2016.txt`（74,296） |
| Gebru ら（2021）CACM・doi:10.1145/3458723（arXiv の版） | `c7f595988ee2c109631d5173fdae37ff1774c68ec17add51bd012f2a6e8792d0` | `tmp\sources\gebru2021.txt`（57,581） |
| ★ Koo & Li（2016）J Chiropr Med・doi:10.1016/j.jcm.2016.02.012（PMC の版） | `767ec4ce324b24c2e95a406e53c7ef4666505ae58575448ee846c3235da16f24`（HTML） | `tmp\sources\koo2016.txt`（31,503） |

- 各立場とも「確認済み、かつ読めた」文献が 3 本（必要な本数 2 を満たす）。

## 3 つの立場が違う角度であること

R1 は**計測の道具の妥当性と方法の比較**（基準・時刻・一致の解析）、R2 は**指標を使う側と先行の道具との比べ方・公開の安全**、R3 は**推論の固定・統計の報告・データの公開**。系譜が重ならない（R1 の Giavarina は「一致の解析をどう読むか」、R3 の Koo & Li は「信頼性の指標をどう選び報告するか」で、角度が違う）。

## 機械の上の封印物と秘密のファイル（起動の前に研究者に知らせる）

この機械（G-GEAR）には、Windows パイロットの最初の試しの生ログと封印（`C:/ime-pilot-win/runs/*/sealed/`）と、Zenodo のトークンがある。査読者役の `Read` は構造では縛れないので、依頼文で読んでよいファイルを限り、応答の保存の検査（絶対パスの突き合わせ）で止める。
