# TRACE: How studies of "AI fatigue" tie fatigue to AI, measure it and report it

Materials for a methodological review (meta-research) of how studies of AI-related fatigue attribute fatigue to AI,
measure it and report it. The protocol will be registered with the Generalized Systematic Review Registration form;
it is not registered yet.

- `manuscript/outline.md`: the structure of the manuscript, the claims and their evidence, and the table shells. It
  is to be attached to the registration, so that the version fixed before coding can be checked.
- `manuscript/draft/`: the manuscript draft in LaTeX (`main.tex`, `tables.tex` for Figure 1 and Tables 1 to 15,
  `figure1.tex`, `refs.bib`). It has the Introduction, Background, Method and the parts of the Discussion that do not
  depend on results (recommendations drawn from existing standards and the limitations); the Results hold only table
  shells, and no result. Build the PDF with `latexmk -pdf figure1.tex main.tex`. A Word copy is made with
  `python3 make_docx.py` (pandoc, then the tables are given column widths, rules, numbers and, for the two widest
  tables, landscape pages).
- `manuscript/abstract-mock.md`: a mock abstract built from empty tables, used to test the rule for the abstract
  against the word limit. It contains no result.

The code table, codebook, coding form and synthesis scripts will be added at registration and publication.
