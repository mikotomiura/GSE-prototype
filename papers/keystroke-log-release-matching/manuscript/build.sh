#!/usr/bin/env bash
# Build the manuscript with pdfLaTeX and BibTeX.
#
#   bash build.sh <template-dir> <out-dir> [<author-file>]
#
# <template-dir> is the directory PoPETS-2027-latex-template of the PoPETs 2027 submission template (it holds
# acmart.cls, popets.sty and ACM-Reference-Format.bst); see BUILD.md for where to obtain it. The template is not part
# of this directory. <out-dir> receives main.pdf and the logs; it must lie outside the directory of the article.
# <author-file>, if given, holds the author block (\author, \affiliation and so on) and builds a version with the
# authors' names in place of the anonymous version for review, written as main-authors.pdf. It must lie outside the
# repository (outside the directory of the article when git is not available).
set -euo pipefail

if [ "$#" -ne 2 ] && [ "$#" -ne 3 ]; then
  echo "usage: bash build.sh <template-dir> <out-dir> [<author-file>]" >&2
  exit 2
fi
absolute() { (cd "$1" && pwd -P); }
here=$(absolute "$(dirname "$0")")
root=$(absolute "$here/..")
template=$1
out=$2
authors=${3:-}
if [ -n "$authors" ] && [ ! -f "$authors" ]; then
  echo "build.sh: $authors is not a file" >&2
  exit 2
fi

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

job=main
if [ -n "$authors" ]; then
  authors=$(realpath "$authors")
  repo=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || echo "$root")
  repo=$(absolute "$repo")
  case "$authors" in
    "$repo"/*)
      echo "build.sh: $authors lies inside $repo; keep the author file outside it" >&2
      exit 2 ;;
    *[%#{}~\\\ ]*)
      echo "build.sh: the path of the author file may not contain % # { } ~ \\ or a space" >&2
      exit 2 ;;
  esac
  job=main-authors
  source_tex="\\def\\authorfile{$authors}\\input{$here/main.tex}"
else
  source_tex="\\input{$here/main.tex}"
fi
# Keep the local paths of included files (such as the licence logo of the template) out of the PDF: pdfTeX writes
# them as PTEX.FileName, which would show the build directory in the anonymous version.
source_tex="\\pdfsuppressptexinfo=-1 $source_tex"

latex() {
  if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -jobname="$job" -output-directory="$out" \
      "$source_tex" > "$out/$job.run.log"; then
    echo "build.sh: pdflatex failed; see $out/$job.run.log" >&2
    exit 1
  fi
}

# One pass to write the citations, BibTeX, and two passes for the references and cross-references. BibTeX exits with
# 1 when it only warns; the warnings are counted below.
cd "$here"
latex
(cd "$out" && bibtex "$job" > "$job.bibtex.log") || [ $? -eq 1 ] || {
  echo "build.sh: bibtex failed; see $out/$job.blg" >&2
  exit 1
}
latex
latex

log="$out/$job.log"
echo "$job: $(grep -c '^!' "$log" || true) errors, $(grep -c 'LaTeX Warning: Reference' "$log" || true) undefined references, $(grep -c 'Warning: Citation' "$log" || true) undefined citations, $(grep -c '^Overfull' "$log" || true) overfull boxes"
echo "bibtex: $(grep -c '^Warning--' "$out/$job.blg" || true) warnings"
