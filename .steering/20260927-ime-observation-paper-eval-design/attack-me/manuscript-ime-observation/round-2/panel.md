# panel — 3 つの立場と接地の文献（attack-me・stage `manuscript`・round 2）

作成: 2026-10-06（G-GEAR・メイン）。対象物は原稿の全体（`papers/ime-observation/manuscript/`・round 1 の指摘を直した版）。

★ Skill「round 2 以降は同じ立場・同じ文献で回す」に従い、**立場・下位人格・接地の文献は round 1 と同じ**（`round-1/panel.md`）。

## 原本の照合（2026-10-06 15 時頃）

- round 1 の `tmp/raw/` と `tmp/sources/` から 9 本を `round-2/tmp/` に写し、`sha256sum` の値が `round-1/panel.md` の記録と**9 本とも一致**することを確かめた（`grep -c` で各値が 1 回ずつ在る）。
- 本文テキストの文字数（`wc -m`）も round 1 の記録と同じ（pinet 54,622・plant 21,703・giavarina 38,486・conijn 71,432・monaco 120,002・crotti 106,177・wicherts 74,296・gebru 57,581・koo 31,503）。
- 本文は印字していない。
- `git check-ignore -v round-2/tmp/sources/pinet2016.txt` → root の `.gitignore` 244 行の `tmp/` が無視する。

## [V162]（Torrance & Conijn 2024）を R2 の接地に足すか → **足さない**

- 理由 1（Skill の規則）: 同じ stage の round 2 は同じ文献で回す。替えてよいのは原本が取れなくなった文献だけ。R2 の 3 本は取れている。
- 理由 2（役割の違い）: [V162] は原稿が Discussion の最後の段落で**引いている**文献で、対象物の一部である。接地は「この立場の基準」を持たせるためのもので、原稿の引用の正しさを確かめるためのものではない。引用の逐語（p.243）は、判断 201 でメインが原本を pypdf で読んで確かめた。R2 は原稿の引用の文を読める（言い換えの妥当さは対象物の中で評価できる）。
- 理由 3（比べやすさ）: round 1 と同じ文献にすると、round 1 の指摘の解消を同じ基準で判定できる。

## 立場・文献・原本と本文の置き場（この round）

- 原本: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-2\tmp\raw\`
- 本文テキスト: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-2\tmp\sources\`

### R1 — 手法の核: 打鍵の時刻を測る道具の検証と、方法の比較（計測の伝統）

- 立場: 心理学の実験で打鍵や反応の時刻を測る道具の精度を、外部の基準で検証してきた方法論の伝統の査読者。新しい測定を参照の測定と比べる方法の比較（一致の解析）にも通じている。
- 下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性を疑う）。

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Pinet ら（2017）BRM・doi:10.3758/s13428-016-0776-3 | `5b22bf8d38958e8d0526d0465bd0079cb2bc213156ffa41b28a576be42943ec2` | `tmp\sources\pinet2016.txt` |
| Plant（2016）BRM・doi:10.3758/s13428-015-0577-0 | `7913cbac645fcf6858e0282e4253e73f9e53a35cea3a609ca53824806ad61fef` | `tmp\sources\plant2016.txt` |
| Giavarina（2015）Biochemia Medica・doi:10.11613/BM.2015.015 | `b4bb31955724c37682eb7d3d68ec1f9d2b0c239258473edc306e26f004961321` | `tmp\sources\giavarina2015.txt` |

### R2 — 隣接分野: 打鍵記録を使う書字過程の研究者（非アルファベットの書字と記録の公開の安全を含む）

- 立場: 打鍵記録から書字過程の指標を計算して使う書字研究の利用者で、入力方式を通して書く言語の記録の道具と、打鍵の記録から内容が漏れる経路にも通じた査読者。
- 下位人格: 「で、読者は何に使えるのか」と問う実務家（冗長さに厳しく、先行の道具との比べ方が公平か、推奨が実際に使えるかを問う）。

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Conijn ら（2019）Reading and Writing・doi:10.1007/s11145-019-09953-8 | `76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196` | `tmp\sources\conijn2019.txt` |
| Monaco（2018）IEEE S&P・doi:10.1109/SP.2018.00026 | `af13534fea80e2cb2b75713da2c4d4ca05d27c87590dbfd296d9be54e8524aa5` | `tmp\sources\monaco2018.txt` |
| Crotti ら（2026）IEEE Access・doi:10.1109/ACCESS.2026.3718565（arXiv:2601.17753 の accepted version） | `f17f901b5b406c02c48d65641e208b1999c35362630e210cf63db33bfacb9d52` | `tmp\sources\crotti2026.txt` |

- ⚠️ Crotti ら（2026）は原稿が §2 と表 1 で比べる相手（自分たちの論文ではない）。

### R3 — 投稿先の方法論と再現性の番人（統計の報告・事前登録・データと材料の公開）

- 立場: 事前登録の具体性・研究者の自由度と、データと材料の公開（説明書・再利用の条件）を審査する、メタサイエンスとデータ管理の方法論の査読者。一致の指標（ICC・kappa・一致の限界）の報告の規範にも通じている。
- 下位人格: 過剰主張と検証できない手順の摘発者（根拠より強い言い方・事前に決まっていない分岐・再利用できない公開を探す）。

| 文献 | 原本 SHA-256 | 本文 |
|---|---|---|
| Wicherts ら（2016）Frontiers in Psychology・doi:10.3389/fpsyg.2016.01832 | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp\sources\wicherts2016.txt` |
| Gebru ら（2021）CACM・doi:10.1145/3458723（arXiv の版） | `c7f595988ee2c109631d5173fdae37ff1774c68ec17add51bd012f2a6e8792d0` | `tmp\sources\gebru2021.txt` |
| Koo & Li（2016）J Chiropr Med・doi:10.1016/j.jcm.2016.02.012（PMC の版） | `767ec4ce324b24c2e95a406e53c7ef4666505ae58575448ee846c3235da16f24`（HTML） | `tmp\sources\koo2016.txt` |

- 各立場とも「確認済み、かつ読めた」文献が 3 本（必要な本数 2 を満たす）。書誌の確認（OpenAlex）は round 1 と外枠の round で済んでいる（`round-1/panel.md`）。

## 3 つの立場が違う角度であること

round 1 と同じ: R1 は計測の道具の妥当性と方法の比較、R2 は指標を使う側と先行の道具との比べ方・公開の安全、R3 は推論の固定・統計の報告・データの公開。

## 機械の上の封印物と秘密のファイル（起動の前に研究者に知らせる）

この機械（G-GEAR）には、Windows のパイロットの最初の試しの生ログと封印（`C:/ime-pilot-win/runs/*/sealed/`）、Windows の本計測の run（`papers/ime-observation/experiment/runs/windows-msime-tsf-2`・git の外）が在る（2026-10-06 に `ls` で確かめた）。Zenodo のトークンも memory の記録ではこの機械にある（置き場は確かめていない）。査読者役の `Read` は構造では縛れないので、依頼文で読んでよいファイルを限り（`experiment/runs/` と `sealed/` を名指して禁じる）、応答の保存の検査（絶対パスの突き合わせ）で止める。round 1 と同じ。
