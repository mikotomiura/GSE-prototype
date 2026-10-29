# Building the manuscript

The manuscript (`main.tex`) uses the PoPETs 2027 submission template (class `acmart` with `popets.sty`, BibTeX style
`ACM-Reference-Format`). The template is not part of this directory; it is obtained from the symposium.

## Obtaining the template

1. Download `submission-template-2027.zip` from the information for authors of PoPETs 2027
   (<https://petsymposium.org/authors-2027.php>, file <https://petsymposium.org/files/submission-template-2027.zip>).
   The build was checked with the file downloaded on 20 October 2026, with the SHA-256
   `b1abbcc0832b7860f5fe8d9773088540b0456965a05fd14c3d47b3a8d85ea7d7`.
2. Unpack it outside this directory. It holds the directory `PoPETS-2027-latex-template`.

## Building

A TeX distribution with pdfLaTeX and BibTeX is needed. The build was checked with MacTeX on macOS.

    bash build.sh <path to PoPETS-2027-latex-template> <output directory>

The script writes `main.pdf` and the logs to the output directory, which must lie outside the directory of the
article. LaTeX runs without shell escape. The script ends by printing the number of errors, undefined references,
undefined citations and overfull boxes, and the number of BibTeX warnings.

The manuscript is anonymous for review. To build a version with the authors' names, give a third argument, a file
that holds the author block (`\author`, `\orcid`, `\affiliation` with `\institution` and `\country`, and
`\renewcommand{\shortauthors}{...}`), kept outside the directory of the article:

    bash build.sh <path to PoPETS-2027-latex-template> <output directory> <author file> References to sections that are not
written yet are reported as undefined.
