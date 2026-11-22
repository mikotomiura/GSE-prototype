# Search B run notes (2026-11-22)

Queries ran 17:04:57-17:05:03 (local) via curl default UA, no key/email. Exact URLs: urls.txt (7 lines, one per query).
All 7 returned HTTP 200 first try; no 429s, no retries. Raw: downloads/kw_1..7.json (+ .hdr).

Counts: meta.count per query = 185, 3, 5, 35, 393, 23, 7 (sum 651). Raw rows on page 1 = 50+3+5+35+50+23+7 = 173; unique works = 171 (K135 in q5+q6, K09 in q1+q5).
Screen: KEEP 43, OFF-TOPIC 128 (incl. duplicate title versions K105/K109/K110 kept as separate works).
Full texts read: 27 (real PDFs, pdftotext -layout). K109/K110 are other versions of K105 (journal PDFs 404) -> marked NONE with note, K105 text used.
Status: INSTANCE 1 (K19), NEAR 1 (K169), NONE 27 (25 read + K109/K110 by K105), NOT-READ 14.

Method: regex scan of each txt (consult*, help-seek*, seek* help, unaided, without help/assistance/support, on their own, external resource/help, self-resolv*, resolved without, independently, without asking/searching); every hit read in a 3-line context (scan.txt); K19 and K169 contexts re-read in the txt.
Fulltext sources: OpenAlex oa_url where it gave a real PDF; arXiv (title search, https://export.arxiv.org) for K01, K04, K73, K135, K139 after the OA link was 403.

NOT-READ (14): K02, K03, K41, K53, K55, K59, K61, K96, K131, K136, K143, K148, K149, K157. Reasons: HTTP 403 (ACM, T&F, MDPI, Springer-bot pages, Northeastern, SSRN, TechRxiv, De Gruyter 202), 401 (Southampton), 000 (UNC), or HTML landing page (K96); no arXiv by title. Not circumvented (no UA spoofing, no CAPTCHA). Those with an institutional-repository PDF (e.g. K61 Southampton, K59 Bristol, K143 Northeastern, K53 UNC) may be reachable in a browser.

Known gaps:
- OpenAlex relevance search with quoted phrase is not an exact phrase filter: most page-1 hits are unrelated (e.g. q1 top 50 of 185). Page 1 only, as specified; q5 ("unaided") has 393 hits, 343 not seen.
- Two-column PDFs: pdftotext -layout interleaves columns, so a line number may contain text from both columns; sentences quoted may be split across lines.
- Title+abstract screening of 128 works was quick; works with empty abstracts (K16, K25, K34, K39, K56, K72, K79, K81, K86, K134, K136, K139 in OpenAlex) were screened on title only (K81, K136, K139 kept; others off).
- K15 (children's board game), K95 (preschool coding), K149, K53 kept as marginal human programming/help contexts.
- Regex scan only; passages using other wording (e.g. "no hint requests", "no queries to tutor") are not found.
- arXiv ids for K21/K98/K119/K169 resolve to 2026 preprints per OpenAlex; read as given.

Files: keyword-hits.tsv, keyword-queries-openalex.tsv, run-notes.md, scan.txt (regex hits), screen.txt (abstract screening dump), works.json.
