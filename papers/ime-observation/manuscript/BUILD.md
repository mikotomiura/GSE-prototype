# Building the manuscript

The manuscript (`main.tex`) and the supplement (`supplement/supplement.tex`) use the Springer Nature LaTeX template
with the APA reference style (class `sn-jnl`, option `sn-apa`, BibTeX style `sn-apacite`). The template is not part
of this directory: its files carry their own terms (the class file states the LaTeX Project Public License), and
they are obtained from the publisher.

## Obtaining the template

1. Download the journal article template package from the LaTeX author support page of Springer Nature
   (<https://www.springernature.com/gp/authors/campaigns/latex-author-support>, "Download the journal article
   template package"). The build was checked with the package of December 2024, a ZIP file of 901,814 bytes with
   the SHA-256 `812e76dcaa9c28dc1bff1fb6065d51729b67d4ea140552a05088317414a3ecae`, downloaded on 5 October 2026.
2. Unpack it outside this directory. It holds the directory `sn-article-template`, with `sn-jnl.cls` and the
   directory `bst`.

## Building

A TeX distribution with pdfLaTeX and BibTeX is needed; the packages that the class and the preamble load (among
them `apacite`, `rotating`, `threeparttable`, `longtable`, `xurl` and `lmodern`) are part of the usual distributions.
The build was checked with MiKTeX 25.12 (pdfTeX 4.23) on Windows.

    bash build.sh <path to sn-article-template> <output directory>

The script writes `main.pdf`, `supplement.pdf` and the logs to the output directory and leaves the sources
untouched; both directories may be given as relative paths, and the output directory must lie outside this directory.
LaTeX runs without shell escape. The script ends by printing, for each document, the number of errors, of undefined
references and citations, of result values that the text reads but that were not generated (`\rv{<key>}` with no
value, printed in bold as a value still to be filled in), and of overfull boxes, and the number of BibTeX warnings.
References to sections and figures that are not written yet are reported as undefined.

## Results tables and values

The tables of the results and every value of the results quoted in the text are generated from the result files of
the analysis by `tools/results_tables.py` (standard library only) into `generated/`; the text reads a value with
`\rv{<key>}`, and `generated/values.json` gives the source of each value inside the result files. After the result
files change:

    python3 tools/results_tables.py --results ../experiment/results --out generated

`build.sh` first runs the same command with `--check` and stops when a generated file no longer matches the result
files (set `PYTHON` when the interpreter is not `python3`). `python3 tools/results_tables.py --selftest` checks the
script on synthetic result files.

## Submission

For submission the sections are combined into one file, and the template files are not uploaded unless the
submission system asks for them.
