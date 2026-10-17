# Provenance for query-strings.md (internal)

R = /Users/johnd/GSE-prototype/.steering/ . Line numbers as read on 2026-10-17. "JSON meta.executed" = key read with python -I from the named evidence JSON.

## Sec. 1 Base bibliography, 53 web queries
- Strings Q001-Q053, date, purposes: R/20260928-ai-fatigue-db-appraisal/archive/input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx, sheet "検索ログ" (xl/worksheets/sheet6.xml), rows 5-57; columns A=ID, B=date (all 2026-09-18), C=source "Web検索（公開学術情報）", D=string, E=purpose, F="検索総ヒット件数は未取得..." ; header row 4; row 2 "53件の公開Web検索を記録...".
- "53 = number of queries, not literature found": same workbook, sheet "はじめに" cell C25; sheet "項目定義・採択基準" cells B24/C24; date at "はじめに" A2.
- Records unscreened, hit counts not recorded: R/20260930-ai-fatigue-protocol/protocol-ja.md:503 (A1).
- CONTRADICTION: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md GSRR-25 (line ~162) says database-specific strings were not kept; the workbook sheet holds all 53 strings (hit counts indeed absent).
- Time of day and search engine: not recorded (sheet6 has date column only; source column generic).

## Sec. 2 Search-gap check
- Queries, counts, date: R/20260928-ai-fatigue-db-appraisal/archive/evidence/searchgap.md:3 (date only), :11-45 (table), :47 and :119-120 (Europe PMC not run), :49-53 (caveats), :57 (141).
- Endpoints, top 50, filters (online <= 2026-09-28, English): archive/evidence/searchgap-brief.md, sections "対象の定義" and "検索" (lines ~11-33).
- 933 viewed: archive/README.md:20; searchgap-analysis.json (keys log_rows=11, candidates=933).
- 141 prejudged on title and keywords only: db-appraisal/decisions.md:121; protocol-ja.md:507 (A5).
- 11 S-02 records = 8 starred + 3 from reference list of AF017: R/20260929-ai-fatigue-db-readable-and-gaps/issues.md:12, :71, :503-513; R/20260929-ai-fatigue-surveys/design.md:130.
- CONTRADICTION 3 vs 4: db-appraisal/tasklist.md:25 "AF017 の引用追跡 4 件" vs issues.md:71 / design.md:130 "3 件". Selection method for these items: not recorded (checked db-appraisal decisions.md, design.md, tasklist.md, requirement.md; issues.md).
- Time of day: not recorded.
- IEEE DataPort cross-match, not added: protocol-ja.md:507; db-appraisal/design.md:96; R/20260930-ai-fatigue-candidates-appraisal/decisions.md:85 (row in "足さなかった記録", section starts :61).

## Sec. 3 Sizing
- Queries and counts, date 2026-09-29: R/20260929-ai-fatigue-db-readable-and-gaps/issues.md:470-499 (appendix B; J-STAGE/CiNii rows :496-499).
- 12:14, "not a full search": protocol-ja.md:509 (A7).
- 429 after 7 of 26; J-STAGE/CiNii 8 words x top 100; seed existence check: db-readable-and-gaps/decisions.md:44-49 (judgment 4; OpenAlex bullet :46, J-STAGE bullet :49).
- Origin of 31 seeds: only "confirmed in Crossref/DataCite" (issues.md:501); origin otherwise not recorded.

## Sec. 4 S-12
- Header dates and times: R/20260929-ai-fatigue-surveys/survey-S-12.md:3. JSON meta.executed in evidence/S-12/: s12_ja_results_2026-09-29.json 21:12:33; s12_abstract_filter_2026-09-29.json 21:17:53; s12_abstract_filter_body_2026-09-29.json 21:19:26; s12_en_results_2026-09-29.json 21:21:36.
- Design fixed before first query: surveys design.md:65; decisions.md:42-44 (judgment 8).
- Term lists: design.md:85-92; survey-S-12.md:30.
- Count table: survey-S-12.md:14-33 (J-STAGE title row :18); hit list: :31; full-text counts: :32.
- CiNii/NDL strings: JSON runs of s12_ja_results (CiNii (all)/(projects) queries; NDL queries "AI 疲労", "AI 疲れ"...); design.md:94-98; survey-S-12.md:24-26.
- Parameters: evidence/S-12/search_ja.py:58-59, :79-81, :104-105; search_en.py:40-41, :67, :86.
- English queries and counts: survey-S-12.md:42-51 (2.3); JSON s12_en_results (4 runs; OpenAlex status ERR "HTTP Error 503").
- OpenAlex 503 (21:21 and retry 21:40): survey-S-12.md:51; decisions.md:16-18.
- 215/110/132 retrieved; 75 after sieve; 145 abstracts, 139+6, 22 passed: survey-S-12.md:35-40; decisions.md:9-14.
- 39 after DOI de-dup: survey-S-12.md:51-52.
- Not searched: survey-S-12.md:53-60; design.md:83.
- Two items outside fixed queries: decisions.md:20-24.
- First assembly 5 + 4 (04:50): judge-file/design.md:9; judge-file/decisions.md:76-78; survey-S-12.md:140-158 (§4.1, §4.2).
- 16 further: candidates-appraisal/decisions.md:13-28, :35-60, :87.

## Sec. 5 S-02
- 2026-09-29 21:38:40: evidence/S-02/s02_meta_2026-09-29.json meta.executed; survey-S-02.md:3.
- 11 DOIs, N-06: surveys design.md:126-167. 10 abstracts/1 missing: survey-S-02.md:25.
- Zenodo 403 and later reading: decisions.md:36-38; survey-S-02.md:7-8, :1-9 header notes.
- 2 later S-02 §7 candidates: judge-file/decisions.md:125-136.

## Sec. 6 S-08
- 2026-09-29 21:46:49: evidence/S-08/s08_results_2026-09-29.json meta.executed; survey-S-08.md:3.
- Queries/hits: s08 JSON runs (Europe PMC 2, Semantic Scholar 6, Crossref x3 no count, OpenAlex 350, citations 5); survey-S-08.md:11-17; design.md:186-190.
- OpenAlex 503 vs 21:46: survey-S-08.md:19.
- Endpoints: evidence/S-08/search_scales.py:40-41, :64, :80, :88-90, :100-101.
- Three later candidates S08-01..03: candidates-appraisal/decisions.md:35-40.

## Sec. 7 S-04
- 21:58:48: evidence/S-04/s04_results_2026-09-29.json meta.executed; survey-S-04.md:3. Query strings in JSON runs equal design.md:219-224. Totals 170/28/85/1119/124279: JSON; survey-S-04.md:12-16.
- Endpoints: evidence/S-04/search_s04.py:52-53, :76-79, :98-99. No year/language filter in these calls.
- Deviations: decisions.md:47-55, :57-61, :63-68, :84-87; survey-S-04.md:18-27.
- 2,319/993/267/289: survey-S-04.md:18.
- Tai-Seale 2024: survey-S-04.md:27, :155; judge-file/decisions.md:205.
- Candidate rows: judge-file/design.md:9; judge-file/decisions.md:78 (33 and 4 after overlap), :155-167, :199-207.

## Sec. 8 S-05
- 22:08:22: evidence/S-05/s05_results_2026-09-29.json meta.executed; surveys design.md:277.
- Queries = JSON runs = design.md:247-255; totals 6/26/25/11/36/87/205/52: JSON; survey-S-05.md:10-21. Not OpenAlex: design.md:256.
- Overwrite defect: decisions.md:105-108, :125-131.
- 354/221: survey-S-05.md:22.
- Scope (b), 9 records: judge-file/decisions.md:15-16, :23, :78; survey-S-05.md:81.

## Sec. 9 S-15
- 03:59:20: R/20260930-ai-fatigue-judge-file/evidence/S-15/s15_results_2026-09-30.json meta.executed; survey-S-15.md:3. Design fixed 03:54: judge-file/design.md:59.
- Queries: design.md:82-88 = JSON runs; totals 51/114/436/58/36: JSON; survey-S-15.md:10-17.
- 641/192/6/187/189, years > 2026 = 0: survey-S-15.md:17-21 (bullets).
- E1 string rewrite: judge-file/decisions.md:70-74; JSON runs[0].query_note.
- CONTRADICTION in time: protocol-ja.md:518 (A16) "検索 04:01〜04:03" vs S-15 JSON 03:59:20 (S-14 04:01:22, S-14s 04:02:50, S-13 04:03:12).
- Candidates 17, then +6: decisions.md:78, :98.

## Sec. 10 S-14
- 04:01:22 / 04:02:50: evidence/S-14/s14_results_2026-09-30.json and s14s_results_2026-09-30.json meta.executed; survey-S-14.md:3.
- Queries: design.md:114-119 (main), decisions.md:58-59 (supplementary) = JSON runs; totals 24/11/93/14 and 31/17: JSON; survey-S-14.md:10-17.
- 113/95/92; 44/6/24/14/106: survey-S-14.md:18-20. Deviation (record after run): decisions.md:53-57; protocol-ja.md:518.
- Candidates 34, +4 +6 +2: decisions.md:78, :98-99.

## Sec. 11 S-13
- 04:03:12: evidence/S-13/s13_results_2026-09-30.json meta.executed; survey-S-13.md:3.
- Queries: design.md:145-150 = JSON; totals 78/39/166/30; 270/112/2/110, 64 no abstract: survey-S-13.md:9-18.
- Candidates 15, +5: decisions.md:78, :98.

## Sec. 12 No-candidate rounds; dev trial
- S-09/S-11: protocol-ja.md:525 (A23 "候補は足していない"); R/20260930-ai-fatigue-theory-and-usage/decisions.md:8 (rationale), :30-34 (only 3 supplementary mentions of existing candidates); survey-S-09.md:3; survey-S-11.md:3 (18:13), :112-116 (Crossref title search; S2 429 at 18:28 and 18:35). Confirmed: no candidate additions in theory-and-usage decisions (grep for 追加候補/足さ/候補は).
- Dev trial: protocol-ja.md:532 (A30); evidence/search-dev.md:1-30; strings :101-183; protocol-ja.md:593-638 (D.1-D.4).
- 259 breakdown: evidence/search-dev.md:58-70 (§4 table); protocol-ja.md:640-642. Check: 34+47+25+9+39+13+46+20+26 = 259.

## Sec. 13 Non-search additions
- 1: db-appraisal/tasklist.md:25; issues.md:71, :511-513.
- 2: surveys decisions.md:20-24.
- 3: judge-file/decisions.md:125-136; protocol-ja.md:520 (A18). Sieve after matching: decisions.md:132; protocol-ja.md:520.
- 4: judge-file/decisions.md:80, :98; protocol-ja.md:519 (A17).
- 5: judge-file/decisions.md:155-167, :189-207; protocol-ja.md:521-522 (A19, A20).
- 6: candidates-appraisal/decisions.md:13-28, :35-87; protocol-ja.md:524 (A22); source services: decisions.md:32.
- 7: see Sec. 2.
- 8: protocol-ja.md:528, :530 (A26, A28); judge-file/decisions.md:216.

## "Not recorded" items and files checked
- Time of day: 53 web queries (workbook sheet 検索ログ), search-gap check (searchgap.md), sizing (issues.md appendix B). Hit counts: 53 web queries. Search engine of the web queries. How AF017 reference-list records were chosen. Origin of the 31 seed papers.
- Review-targeted search in GSRR-21 (third bullet): no distinct search found in the cited files. Likely referents: S-04 reviews table (survey-S-04.md:193; drawn from the S-04 Europe PMC / Semantic Scholar / OpenAlex queries) and the search-gap check (OpenAlex/Crossref). Needs researcher confirmation.

## Not read
- survey-S-*-ai-judgments.md, db-proposals.md (blinding; unneeded). No NDJSON logs. Search-development JSON files and search_dev.py not opened beyond search-dev.md. Individual result lists of the J-STAGE/CiNii runs (only totals and queries).
