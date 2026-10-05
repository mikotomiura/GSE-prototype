# panel — 3 つの立場と接地の文献（attack-me・stage `outline`・round 2）

作成: 2026-10-05（G-GEAR・メイン）。**round 1 と同じ立場・同じ下位人格・同じ文献 9 本**（Skill の Step 1「round 2 以降は同じ立場・同じ文献で回す」）。立場・下位人格・書誌・確認の経緯は round 1 の `panel.md` を見る（書誌は round 1 で OpenAlex の記録により確認済み）。

## 原本と本文の置き場（この round）

- 原本: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-2\tmp\raw\`
- 本文テキスト: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-2\tmp\sources\`
- ★ 取り直し方: round 1 の `tmp/` がこの機械に残っていたので、原本を写し、**SHA-256 が round 1 の `panel.md` の記録と 9 本とも一致する**ことを `sha256sum` で確かめた（同じ原本であることの確認。本文テキストは原本から決まる抽出なので一緒に写した）。本文の先頭の約 110 字で題が書誌と一致することを確かめた（＝読めた）。本文は印字していない。
- `git check-ignore -v` で `round-2/tmp/sources/` が root の `.gitignore` の `tmp/` に無視されることを確かめた。

| 役 | 文献 | 原本 SHA-256（round 1 と一致） | 本文（文字数は `wc -m`） |
|---|---|---|---|
| R1 | Pinet ら（2017）BRM・doi:10.3758/s13428-016-0776-3 | `5b22bf8d38958e8d0526d0465bd0079cb2bc213156ffa41b28a576be42943ec2` | `tmp\sources\pinet2016.txt`（54,622） |
| R1 | Bridges ら（2020）PeerJ・doi:10.7717/peerj.9414 | `25dcabfc1a05f3e4b4c9aab20adbc97d2980d01e2bc468d1c8c2bb53040e6d9f`（XML） | `tmp\sources\bridges2020.txt`（87,181） |
| R1 | Plant（2016）BRM・doi:10.3758/s13428-015-0577-0 | `7913cbac645fcf6858e0282e4253e73f9e53a35cea3a609ca53824806ad61fef` | `tmp\sources\plant2016.txt`（21,703） |
| R2 | Conijn ら（2019）Reading and Writing・doi:10.1007/s11145-019-09953-8 | `76b0a8042dc7a5834a9d4b93a4844254ef083e3d3e1adbb1e1772fd2c7555196` | `tmp\sources\conijn2019.txt`（71,432） |
| R2 | Monaco（2018）IEEE S&P・doi:10.1109/SP.2018.00026 | `af13534fea80e2cb2b75713da2c4d4ca05d27c87590dbfd296d9be54e8524aa5` | `tmp\sources\monaco2018.txt`（120,002） |
| R2 | Crotti ら（2026）IEEE Access・doi:10.1109/ACCESS.2026.3718565（arXiv:2601.17753 の accepted version で代えた・round 1 と同じ） | `f17f901b5b406c02c48d65641e208b1999c35362630e210cf63db33bfacb9d52` | `tmp\sources\crotti2026.txt`（106,177） |
| R3 | Wicherts ら（2016）Frontiers in Psychology・doi:10.3389/fpsyg.2016.01832 | `26d1f9f6fc49b5f60bc05a3830a150051396e69c0b7f4bea7500b8195b3f46bb` | `tmp\sources\wicherts2016.txt`（74,296） |
| R3 | Gebru ら（2021）CACM・doi:10.1145/3458723（arXiv の版） | `c7f595988ee2c109631d5173fdae37ff1774c68ec17add51bd012f2a6e8792d0` | `tmp\sources\gebru2021.txt`（57,581） |
| R3 | Wilkinson ら（2016）Scientific Data・doi:10.1038/sdata.2016.18 | `cdddd9f4808f7e3e1f013139c3915ef4d7cdccb008fa947ef5f72b4c7b6ffde7` | `tmp\sources\wilkinson2016.txt`（47,584） |

- 各立場とも「確認済み、かつ読めた」文献が 3 本（必要な本数 2 を満たす）。
- 検索: 新しい検索はしていない（同じ文献で回すため）。

## 機械の上の封印物と秘密のファイル（起動の前に研究者に知らせる）

この機械（G-GEAR）には、Windows パイロットの最初の試しの生ログと封印（`C:/ime-pilot-win/runs/*/sealed/`）と、Zenodo のトークンがある。査読者役の `Read` は構造では縛れないので、依頼文で読んでよいファイルを限り、応答の保存の検査（絶対パスの突き合わせ）で止める。
