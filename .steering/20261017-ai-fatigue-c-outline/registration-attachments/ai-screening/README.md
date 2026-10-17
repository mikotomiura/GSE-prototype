# Attachment 6: the AI screener

- `instructions.md`: the instructions given unchanged to the AI screener (the version used in round 3 of the check and registered).
- `call.md`: the wording that wraps a batch of records for one call, and the settings of the call.
- `check-34.csv`: the check on the 34 exploratory records before registration, record by record. `human_final` and `human_centre` are the final decisions of the source database's two human screeners. For each round (`r1`, `r2`, `r3`), the AI screener's stage-1 decision and code, stage-2 decision and code, and centre. An empty stage-2 cell means that the record was excluded at stage 1. No abstract, full text or quotation is included.

The screening tools are attached with these files (GSRR-33, GSRR-41):

- `c_screening.py`: cuts the batches from the fixed screening order; writes the AI screener's inputs (the title and abstract, or the free full text with its source on the first line) and the call wording for each batch, in a working directory outside the repository; refuses to accept an output unless author 1's judgements of the batch are committed and pushed and the output files are newer than that commit (and, on a re-run, newer than the first output); checks the format of the output without displaying its content (a quotation has at most 25 words, a word being a whitespace-separated token with a letter or digit, and two Japanese characters counting as one word) and records the SHA-256 and time of each output; records the final decisions (a pending record found later with a free full text is screened again in a new batch); writes the table for the screening agreement (also for the first and second halves of the screening order); and writes the public list, with the quotations, notes and longer place descriptions that author 1 marked as scale items removed.
- `check_screening.py`: runs every step of `c_screening.py` on 20 dummy records and checks the results and the refusals.
- `make_trace_db.py`: builds the screening database for author 1 (bibliographic data, abstracts and full-text status, with no judgement). Stage 1 is judged on a sheet without full-text columns.

Round 1 used the instructions committed before any record was judged. Round 2 used the instructions after one question (Q4) was clarified. Round 3 used the instructions after web access was removed. Neither revision was called for by the pre-set rule (GSRR-37).
