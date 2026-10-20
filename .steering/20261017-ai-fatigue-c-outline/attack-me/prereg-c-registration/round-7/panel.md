# panel（round 7・2026-10-20）

R1・R2・R3 の立場は round 1〜6 と同じ。R1・R2 の文献も同じ（本文は /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-1/tmp/sources/ ・書誌と原本の SHA-256 は round-1/panel.md のとおり）。

R3 に 3 本を足した（研究者の選択・2026-10-20・AskUserQuestion）。理由: 0.11 の後に選別の形が「人 2 人・段 1 の 8 割は第一著者だけ・AI は段 1 の網・第一著者だけの除外の監査」に変わり、それを直接扱う方法論の文献が今の 6 本に無かった。Skill の「round 2 以降は同じ立場・同じ文献」からの逸脱として、ここに記録する。

| 役 | 立場 | 下位人格 | 文献 |
|---|---|---|---|
| R1 | 心理測定と構成概念の妥当性の専門家 | 「その測定は本当にそれを測っているか」を疑う懐疑家 | Elson et al. 2023・Lintner 2024 |
| R2 | HCI の測定の実務家（応用の側） | 「で、読者は何に使えるのか」と問う実務家・冗長さに厳しい | Perrig et al. 2024・Bach et al. 2022 |
| R3 | メタ研究・事前登録・再現性の番人 | 過剰主張と検証できない手順の摘発者 | van den Akker et al. 2023・Nuijten et al. 2016・〔新〕Waffenschmidt et al. 2019・Garritty et al. 2020・Khraisha et al. 2024 |

## 足した 3 本（確認済み・読めた）

書誌は OpenAlex の記録（`https://api.openalex.org/works/doi:<DOI>`）で題・筆頭著者・年・DOI・`is_oa` を確かめた。本文の保存先は round-7/tmp/sources/（git が無視する。`git check-ignore` で確かめた）。

| 短い名 | 書誌 | 経路 | 原本の SHA-256 |
|---|---|---|---|
| waffenschmidt2019 | Waffenschmidt, S., et al. (2019). Single screening versus conventional double screening for study selection in systematic reviews: a methodological systematic review. *BMC Medical Research Methodology*, 19, 132. doi:10.1186/s12874-019-0782-0 | Europe PMC の全文 XML（PMC6599339）。出版社の PDF は bot の確認で HTML が返った | 596b29b6…e18ea（`596b29b61d569ff828642d09a4c108cb2e50f89d9b17054255ccc0eac2cfe834`） |
| garritty2020 | Garritty, C., et al. (2020). Cochrane Rapid Reviews Methods Group offers evidence-informed guidance to conduct rapid reviews. *Journal of Clinical Epidemiology*, 130, 13–22. doi:10.1016/j.jclinepi.2020.10.007 | Europe PMC の全文 XML（PMC7557165） | `9cdc5ef85b55e1ae9062ebdf0a43b231f92ff50284993bdb90baae41b7186397` |
| khraisha2024 | Khraisha, Q., et al. (2024). Can large language models replace humans in systematic reviews? Evaluating GPT-4's efficacy in screening and extracting data from peer-reviewed and grey literature in multiple languages. *Research Synthesis Methods*, 15, 616–626. doi:10.1002/jrsm.1715 | arXiv の版（2310.17526・著者の公開版・10 頁）。出版社の版は bot の確認で HTML が返った。題と筆頭著者は一致 | `68c9b95af31f743315579f6961abf4d6b33876a76f0381b32232b4e90acc0d9e` |

- 替えた 1 本: 研究者に示した候補は Gartlehner et al. 2020（doi:10.1016/j.jclinepi.2020.01.005・*J Clin Epidemiol*）だったが、無料の本文が取れなかった（出版社は bot の確認、Europe PMC に全文なし、Unpaywall の置き場は PDF なし）。同じ立場（1 人の選別と一部の二重の選別の手引き）の Garritty et al. 2020 で代えた。
- 規程の本文（van den Akker 2023）は round 7 で取り直した（`round-7/tmp/raw/gsrr.xml`・SHA-256 は round 1 と同じ `c8408c10…`）。
- 本文は印字していない（題の確認に先頭の 160 字と文字数だけ）。
