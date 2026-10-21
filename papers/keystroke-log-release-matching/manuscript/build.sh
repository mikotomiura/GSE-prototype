#!/usr/bin/env bash
# Build the manuscript with pdfLaTeX and BibTeX.
#
#   bash build.sh <template-dir> <out-dir>
#
# <template-dir> is the directory PoPETS-2027-latex-template of the PoPETs 2027 submission template (it holds
# acmart.cls, popets.sty and ACM-Reference-Format.bst); see BUILD.md for where to obtain it. The template is not part
# of this directory. <out-dir> receives main.pdf and the logs; it must lie outside the directory of the article.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: bash build.sh <template-dir> <out-dir>" >&2
  exit 2
fi
absolute() { (cd "$1" && pwd -P); }
here=$(absolute "$(dirname "$0")")
root=$(absolute "$here/..")
template=$1
out=$2

for f in acmart.cls popets.sty ACM-Reference-Format.bst; do
  if [ ! -f "$template/$f" ]; then
    echo "build.sh: $template does not hold $f" >&2
    exit 2
  fi
done
created=0
if [ ! -d "$out" ]; then
  mkdir -p "$out"
  created=1
fi
template=$(absolute "$template")
out=$(absolute "$out")
case "$out/" in
  "$root"/*)
    if [ "$created" = 1 ]; then rmdir "$out"; fi
    echo "build.sh: $out lies inside $root; give an output directory outside it" >&2
    exit 2 ;;
esac

# The directory of the manuscript comes first: the template directory holds a main.tex of its own.
export TEXINPUTS="${here}:${template}:"
export BSTINPUTS="${template}:"
export BIBINPUTS="${here}:"

latex() {
  if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory="$out" "$here/main.tex" \
      > "$out/main.run.log"; then
    echo "build.sh: pdflatex failed; see $out/main.run.log" >&2
    exit 1
  fi
}

# One pass to write the citations, BibTeX, and two passes for the references and cross-references. BibTeX exits with
# 1 when it only warns; the warnings are counted below.
cd "$here"
latex
(cd "$out" && bibtex main > main.bibtex.log) || [ $? -eq 1 ] || {
  echo "build.sh: bibtex failed; see $out/main.blg" >&2
  exit 1
}
latex
latex

log="$out/main.log"
echo "main: $(grep -c '^!' "$log" || true) errors, $(grep -c 'LaTeX Warning: Reference' "$log" || true) undefined references, $(grep -c 'Warning: Citation' "$log" || true) undefined citations, $(grep -c '^Overfull' "$log" || true) overfull boxes"
echo "bibtex: $(grep -c '^Warning--' "$out/main.blg" || true) warnings"
