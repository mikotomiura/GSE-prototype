# Search log: forward citations of D1/D2 and keyword searches

Date: 2026-11-21. Run by one agent, no subagents.

## Criterion (fixed in advance, applied literally)
INSTANCE: a passage that reads units (episodes/tasks/sessions) without recorded consultation of external resources as resolved, as resolved without help, or as not needing help, OR infers a low need for help from a low rate of consultation.
NEAR: comes close but does not meet it (reason given in note). NONE: read, nothing relevant. NOT-READ: no free full text.

## Search A: sources
- OpenAlex: `https://api.openalex.org/works?filter=cites:W4386603916&per-page=200` (D1: 54 works) and `cites:W7128812742` (D2: 4 works).
- Semantic Scholar Graph API `/paper/{arXiv:2105.02162 | DOI:10.1007/s10664-023-10352-5 | DOI:10.1145/3797077 | arXiv:2602.11435}/citations?fields=title,year,externalIds,contexts,isOpenAccess,openAccessPdf&limit=1000` (27, 28, 4, 4 records).
- Dedup: same DOI, or same arXiv id, or same normalised title (lowercase alphanumerics). 121 raw records -> 70 unique works (64 cite D1, 6 cite D2, none cite both). C18 is D2 itself (it cites D1), so 69 works excluding D2.
- The previous run's 58 vs 70 here: not resolvable from this side. Likely causes: S2 and OpenAlex added works the other lacks (12 works only in S2, 16 only in OpenAlex, 42 in both) and the previous run may not have merged the arXiv/journal versions of D1 or counted D2 citers.
- Full text: free PDFs via arXiv, openAccessPdf, OpenAlex OA locations (curl, default user agent, %PDF check), arXiv API title search for the rest. Converted with pdftotext; scanned with regex for consult/help-seeking/unaided/without help/on their own/external resources/self-resolved and a second proximity regex (resource term near negation); every hit read in context. PDFs in downloads/pdf, text in downloads/txt, scripts in ../scripts.
- Counts: 70 unique; 43 full texts read (NONE 41, NEAR 2 = C04, C29, INSTANCE 0); 27 NOT-READ (judged on S2 contexts/abstract only, nothing relevant).

## Search B
See keyword-queries.tsv. OpenAlex returned HTTP 429 (free daily budget used by Search A) so none of the 7 OpenAlex queries ran. Substitute: Semantic Scholar bulk phrase search over title/abstract (7 queries, 2 hits total, both irrelevant). The unquoted S2 relevance searches hit 429 too and were not completed. Search B is therefore NOT a valid replacement for the specified OpenAlex search and should be rerun after 00:00 UTC (or with an OpenAlex API key).

## Gaps and cautions
- Keyword scan is regex-based over extracted PDF text; two-column layout can split sentences, so misses are possible. Publisher PDFs (ACM, IEEE) behind bot challenges were not fetched.
- Several NOT-READ works are ACM/IEEE papers with no free copy found; some may have author copies not located.
- D1 version coverage: OpenAlex merges arXiv and journal; S2 queried both ids.
