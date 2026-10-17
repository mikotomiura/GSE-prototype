# TRACE: How studies of "AI fatigue" tie fatigue to AI, measure it and report it

Materials for a methodological review (meta-research) of how studies of AI-related fatigue attribute fatigue to AI,
measure it and report it. The protocol will be registered with the Generalized Systematic Review Registration form;
it is not registered yet.

- `manuscript/outline.md`: the structure of the manuscript, the claims and their evidence, and the table shells. It
  is to be attached to the registration, so that the version fixed before coding can be checked.
- `manuscript/draft/`: the manuscript draft in LaTeX (`main.tex`, `refs.bib`). It has the Introduction, Background and
  Method; the Results and Discussion hold only headings and table shells, and no result. Build with `latexmk -pdf
  main.tex`; a Word copy is made with `python3 make_docx.py`
  (pandoc, then the tables are given column widths, rules and numbers).
- `manuscript/abstract-mock.md`: a mock abstract built from empty tables, used to test the rule for the abstract
  against the word limit. It contains no result.

The code table, codebook, coding form and synthesis scripts will be added at registration and publication.
