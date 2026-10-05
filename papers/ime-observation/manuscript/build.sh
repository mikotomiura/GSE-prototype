#!/usr/bin/env bash
# Build the manuscript and the supplement with pdfLaTeX and BibTeX.
#
#   bash build.sh <template-dir> <out-dir>
#
# <template-dir> is the directory sn-article-template of the Springer Nature LaTeX template (it holds sn-jnl.cls and
# the directory bst); see BUILD.md for where to obtain it. The template is not part of this directory. <out-dir>
# receives main.pdf, supplement.pdf and the logs, so that no build output is written next to the sources; it must lie
# outside this directory. Both may be given as relative paths.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: bash build.sh <template-dir> <out-dir>" >&2
  exit 2
fi
template=$1
out=$2

# TeX reads the search paths with the separator of the system: a semicolon on Windows, a colon elsewhere. On Windows
# every directory is passed in the form of the system (C:/...), which a Windows TeX can open and bash can use.
windows=0
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*) windows=1 ;;
esac
absolute() {
  if [ "$windows" = 1 ]; then (cd "$1" && pwd -W); else (cd "$1" && pwd); fi
}
here=$(absolute "$(dirname "$0")")

if [ ! -f "$template/sn-jnl.cls" ] || [ ! -f "$template/bst/sn-apacite.bst" ]; then
  echo "build.sh: $template does not hold sn-jnl.cls and bst/sn-apacite.bst" >&2
  exit 2
fi
created=0
if [ ! -d "$out" ]; then
  mkdir -p "$out"
  created=1
fi
# Both directories are made absolute before the script changes directory, so that a relative path names the same place
# throughout.
template=$(absolute "$template")
out=$(absolute "$out")
case "$out/" in
  "$here"/*)
    if [ "$created" = 1 ]; then rmdir "$out"; fi
    echo "build.sh: $out lies inside the manuscript directory; give an output directory outside it" >&2
    exit 2 ;;
esac

sep=":"
if [ "$windows" = 1 ]; then sep=";"; fi
export TEXINPUTS="${template}${sep}"
export BSTINPUTS="${template}/bst${sep}"
export BIBINPUTS="${here}${sep}"

# The tables and values of the results must match the result files (set PYTHON when python3 is not the interpreter).
"${PYTHON:-python3}" "$here/tools/results_tables.py" --results "$here/../experiment/results" --out "$here/generated" --check

# The template's class is run without shell escape.
latex() {
  local log
  log="$out/$(basename "$1" .tex).run.log"
  if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory="$out" "$1" > "$log"; then
    echo "build.sh: pdflatex failed on $1; see $log" >&2
    exit 1
  fi
}

# The manuscript: one pass to write the citations, BibTeX, and two passes for the references and cross-references.
# BibTeX exits with 1 when it only warns; the warnings are counted below.
cd "$here"
latex main.tex
(cd "$out" && bibtex main > main.bibtex.log) || [ $? -eq 1 ] || {
  echo "build.sh: bibtex failed; see $out/main.blg" >&2
  exit 1
}
latex main.tex
latex main.tex

# The supplement has no citations.
cd "$here/supplement"
latex supplement.tex
latex supplement.tex

for name in main supplement; do
  log="$out/$name.log"
  echo "$name: $(grep -c '^!' "$log" || true) errors, $(grep -c 'LaTeX Warning: Reference' "$log" || true) undefined references, $(grep -c 'Warning: Citation' "$log" || true) undefined citations, $(grep -c 'Package results Warning: Result value' "$log" || true) result values not generated, $(grep -c '^Overfull' "$log" || true) overfull boxes"
done
echo "bibtex: $(grep -c '^Warning--' "$out/main.blg" || true) warnings"
