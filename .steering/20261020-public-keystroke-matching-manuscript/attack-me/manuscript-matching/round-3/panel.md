# panel（stage: manuscript・round 3・原稿の全体・2026-10-29）

R1〜R3 は round 1 と同じ立場・同じ接地の文献（round-1/panel.md）。本文は round-2/tmp/sources/ から round-3/tmp/sources/ に写し、round-1/tmp/sources/ と同じであることを `cmp` で確かめた（7 本・2026-10-29）。原本の SHA-256 は round-1/panel.md のとおり。

この round から、paper-write の試し（判断 77）で attack-me に足した**編集者の役 E** を入れる（枝 `chore/paper-write-skill` の `.claude/skills/attack-me/SKILL.md`・コミット da068db7 の版に従う。E は初めて入るので引き継ぎは無い）。

| 役 | 立場 | 批判的な下位人格 | 接地の文献 |
|---|---|---|---|
| R1 | 再識別・匿名化への攻撃の評価の専門家 | 「その評価は本当にリスクを測っているか・脅威モデルは攻撃者に甘すぎないか／厳しすぎないか」を疑う懐疑家 | narayanan・stadler・rocher（round-1/panel.md） |
| R2 | データを公開・管理する側（大学・教育データの管理と、行動の生体情報の匿名化の実務） | 「で、データを公開する側は何に使えるのか」と問う実務家／冗長さに厳しい読者 | borgman・hanisch（同上） |
| R3 | 投稿先の方法論・倫理・再現性の番人 | 過剰主張と、現実離れした脅威モデル・検証できない手順の摘発者 | arp・kohno（同上） |
| E | PoPETs の担当編集者（査読に回す前に本文だけを読む） | 忙しい読者。最初の 2 頁で貢献が分からなければ読むのをやめる | (1) 投稿先の一次（context-A.md の規程と CfP の抜粋）、(2) Mensh & Kording 2017, Ten simple rules for structuring papers, PLoS Comput Biol 13(9): e1005619, doi:10.1371/journal.pcbi.1005619 |

- Mensh & Kording: 確認済み（OpenAlex `works/doi:10.1371/journal.pcbi.1005619` で題・筆頭著者 Brett D. Mensh・2017・DOI が一致、`is_oa` 真、`oa_url` は journals.plos.org の printable PDF・2026-10-29）。読めた（PDF 9 頁を curl で取得、pdftotext で本文の 3 行目に題）。原本 SHA-256 `f02a2c14c630369f2058403a448f94e7aaeafb3c1cc681c9d6862812590b7b6c`・`round-3/tmp/raw/mensh.pdf`・本文 `round-3/tmp/sources/mensh.txt`（30,377 字）。
- Codex は加えない（既定）。
