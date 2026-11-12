#!/usr/bin/env bash
# Build the preprint version (preprint.tex) with pdfLaTeX and BibTeX.
#
#   bash build-preprint.sh <out-dir> <author-file>
#
# Unlike build.sh, this needs no template of a venue: preprint.tex uses the article class and the BibTeX style
# abbrvnat of the TeX distribution. <author-file> defines \ppauthor, \ppaffiliation, \ppemail and \pporcid and must
# lie outside the repository. <out-dir> receives preprint.pdf and the logs; it must lie outside the directory of the
# article.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: bash build-preprint.sh <out-dir> <author-file>" >&2
  exit 2
fi
absolute() { (cd "$1" && pwd -P); }
here=$(absolute "$(dirname "$0")")
root=$(absolute "$here/..")
out=$1
authors=$2
if [ ! -f "$authors" ]; then
  echo "build-preprint.sh: $authors is not a file" >&2
  exit 2
fi
authors=$(realpath "$authors")
repo=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || echo "$root")
repo=$(absolute "$repo")
case "$authors" in
  "$repo"/*)
    echo "build-preprint.sh: $authors lies inside $repo; keep the author file outside it" >&2
    exit 2 ;;
  *[%#{}~\\\ ]*)
    echo "build-preprint.sh: the path of the author file may not contain % # { } ~ \\ or a space" >&2
    exit 2 ;;
esac
created=0
if [ ! -d "$out" ]; then
  mkdir -p "$out"
  created=1
fi
out=$(absolute "$out")
case "$out/" in
  "$root"/*)
    if [ "$created" = 1 ]; then rmdir "$out"; fi
    echo "build-preprint.sh: $out lies inside $root; give an output directory outside it" >&2
    exit 2 ;;
esac

export TEXINPUTS="${here}:"
export BIBINPUTS="${here}:"
job=preprint
source_tex="\\def\\authorfile{$authors}\\input{$here/preprint.tex}"

latex() {
  if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -jobname="$job" -output-directory="$out" \
      "$source_tex" > "$out/$job.run.log"; then
    echo "build-preprint.sh: pdflatex failed; see $out/$job.run.log" >&2
    exit 1
  fi
}

cd "$here"
latex
(cd "$out" && bibtex "$job" > "$job.bibtex.log") || [ $? -eq 1 ] || {
  echo "build-preprint.sh: bibtex failed; see $out/$job.blg" >&2
  exit 1
}
latex
latex

log="$out/$job.log"
echo "$job: $(grep -c '^!' "$log" || true) errors, $(grep -c 'LaTeX Warning: Reference' "$log" || true) undefined references, $(grep -c 'Warning: Citation' "$log" || true) undefined citations, $(grep -c '^Overfull' "$log" || true) overfull boxes"
echo "bibtex: $(grep -c '^Warning--' "$out/$job.blg" || true) warnings"
