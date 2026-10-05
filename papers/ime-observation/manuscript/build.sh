#!/usr/bin/env bash
# Build the manuscript and the supplement with pdfLaTeX and BibTeX.
#
#   bash build.sh <template-dir> <out-dir>
#
# <template-dir> is the directory sn-article-template of the Springer Nature LaTeX template (it holds sn-jnl.cls and
# the directory bst); see BUILD.md for where to obtain it. The template is not part of this directory. <out-dir>
# receives main.pdf, supplement.pdf and the logs, so that no build output is written next to the sources.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: bash build.sh <template-dir> <out-dir>" >&2
  exit 2
fi
template=$1
out=$2
here=$(cd "$(dirname "$0")" && pwd)

if [ ! -f "$template/sn-jnl.cls" ] || [ ! -f "$template/bst/sn-apacite.bst" ]; then
  echo "build.sh: $template does not hold sn-jnl.cls and bst/sn-apacite.bst" >&2
  exit 2
fi
mkdir -p "$out"

# TeX reads the search paths with the separator of the system: a semicolon on Windows, a colon elsewhere.
sep=":"
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*) sep=";" ;;
esac
export TEXINPUTS="${template}${sep}"
export BSTINPUTS="${template}/bst${sep}"
export BIBINPUTS="${here}${sep}"

latex() {
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$out" "$1" > "$out/$(basename "$1" .tex).run.log"
}

# The manuscript: one pass to write the citations, BibTeX, and two passes for the references and cross-references.
cd "$here"
latex main.tex
(cd "$out" && bibtex main > main.bibtex.log)
latex main.tex
latex main.tex

# The supplement has no citations.
cd "$here/supplement"
latex supplement.tex
latex supplement.tex

for name in main supplement; do
  log="$out/$name.log"
  echo "$name: $(grep -c '^!' "$log" || true) errors, $(grep -c 'LaTeX Warning: Reference' "$log" || true) undefined references, $(grep -c '^Overfull' "$log" || true) overfull boxes"
done
