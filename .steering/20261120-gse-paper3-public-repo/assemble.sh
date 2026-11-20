#!/usr/bin/env bash
# 論文 3 の公開 repo（per-person-keystroke-models）の中身を、GSE のコミット済みの中身から写す。
# 使い方: assemble.sh <GSE の checkout（枝 docs/gse-paper3-per-person-learning）> <出力先（空か、.git だけのディレクトリ）>
# 写す一覧はこのファイルが単一の記録。写した後の検査は出力先の tools/verify.sh。
# 書き換えるのは 1 ファイルだけ（README に明記。休止の割合の範囲は論文と同じく出す＝判断 2）:
#   paper/supplement.tex  \journalline を空にし、その説明のコメント 1 行を外し、1 行目のコメントから提出のファイル名
#                         （ESM_1.pdf）を外す（投稿先と状態を書かない・判断 5）
# 終了コード: 0 = 写した / 1 = 一覧のファイルが無い・書き換えの前提が違う / 2 = 使い方
set -euo pipefail
export LC_ALL=C
[ $# -eq 2 ] || { echo "usage: assemble.sh <gse-checkout> <out>" >&2; exit 2; }
SRC="$(cd "$1" && pwd -P)"; OUT="$2"
if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null | grep -v '^\.git$' || true)" ]; then
  echo "output dir is not empty (only .git may exist): $OUT" >&2; exit 2
fi
parent="$OUT"; while [ ! -e "$parent" ]; do parent="$(dirname "$parent")"; done
case "$(cd "$parent" && pwd -P)/" in "$SRC"/*) echo "output must be outside the GSE checkout" >&2; exit 2 ;; esac
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd -P)"
case "$OUT/" in "$SRC"/*) echo "output must be outside the GSE checkout" >&2; exit 2 ;; esac

BRANCH_NAME=docs/gse-paper3-per-person-learning   # 論文 3 の枝（HEAD がこの枝であること）
MAIN_NAME=origin/main                             # 構造の補い（S8 の確かめ 2）はこの枝に無い
# 1) ディレクトリごと（追跡済みのファイル全部）
WHOLE=(
  experiments/20261103-coauthor-per-person
  experiments/20261104-coauthor-ml-improve
  experiments/20261104-cs1-landscape
  experiments/20261104-timeseries-tau-extend
  experiments/20261106-tau-mode-candidate
  experiments/20261107-unsmoothed-residual-check
  experiments/20261110-per-person-sensitivity
  experiments/20261111-mode-in-selection
  experiments/20261111-objective-and-pause
  experiments/20261111-sensitivity-mode-decomposition
  experiments/20261112-selection-split-and-smoothing
  experiments/20261112-sensitivity-ten-seeds
  experiments/20261113-null-from-shared
)
WHOLE_MAIN=(experiments/20261107-structure-deficit-test)
# 2) 依存先: 変換と解析のスクリプト・実行の手順・条件・データの記録だけ（results と notes は入れない）
DEP_DIRS=(
  experiments/20261031-coauthor-pre-request-signal
  experiments/20261101-klicke-early-stall-trigger
  experiments/20261102-public-data-landscape
)
KIT=papers/per-person-learning/kit/symbols
PAPER=papers/per-person-learning/manuscript
PAPER_FILES=(main.tex supplement.tex references.bib)   # ＋ figdata/*.csv。様式（cls・bst）と outline.md は入れない

cd "$SRC"
[ "$(git branch --show-current)" = "$BRANCH_NAME" ] || { echo "the checkout is not on $BRANCH_NAME" >&2; exit 1; }
# ref は最初に 1 度だけコミットの id に固定する（一覧・写し・来歴の表が同じコミットを見る）
BRANCH_REF="$(git rev-parse --verify -q 'HEAD^{commit}')" || { echo "HEAD not found" >&2; exit 1; }
MAIN_REF="$(git rev-parse --verify -q "$MAIN_NAME^{commit}")" || { echo "ref not found: $MAIN_NAME (git fetch origin main)" >&2; exit 1; }
fail=0
declare -a list_b=() list_m=()
add_dir() {  # <ref> <dir> <filter: all|dep> <array name>
  local ref="$1" d="$2" mode="$3" n=0 f
  while IFS= read -r f; do
    if [ "$mode" = dep ]; then
      case "$f" in
        "$d"/scripts/*|"$d"/run*.sh|"$d"/conditions*.md|"$d"/data.md|"$d"/env.md|"$d"/SEED|"$d"/mutate.sh|"$d"/.gitattributes) ;;
        *) continue ;;
      esac
    fi
    eval "$4+=(\"\$f\")"; n=$((n + 1))
  done < <(git ls-tree -r --name-only "$ref" -- "$d")
  [ "$n" -gt 0 ] || { echo "no tracked files under $d at $ref" >&2; fail=1; }
}
for d in "${WHOLE[@]}"; do add_dir "$BRANCH_REF" "$d" all list_b; done
for d in "${DEP_DIRS[@]}"; do add_dir "$BRANCH_REF" "$d" dep list_b; done
for d in "${WHOLE_MAIN[@]}"; do add_dir "$MAIN_REF" "$d" all list_m; done
add_dir "$BRANCH_REF" "$KIT" all list_b
for f in "${PAPER_FILES[@]}"; do list_b+=("$PAPER/$f"); done
while IFS= read -r f; do list_b+=("$f"); done < <(git ls-tree -r --name-only "$BRANCH_REF" -- "$PAPER/figdata")

# 必ずあるはずのもの
for f in experiments/20261113-null-from-shared/scripts/pinned6.py "$KIT/selftest.py" "$KIT/hashes/hashes.py" \
         "$PAPER/main.tex" "$PAPER/supplement.tex"; do
  git cat-file -e "$BRANCH_REF:$f" 2>/dev/null || { echo "required file not in $BRANCH_REF: $f" >&2; fail=1; }
done
git cat-file -e "$MAIN_REF:experiments/20261107-structure-deficit-test/run.sh" 2>/dev/null || { echo "structure-deficit-test missing in $MAIN_REF" >&2; fail=1; }
# シンボリックリンク（mode 120000）は写さない
links="$( { git ls-tree -r "$BRANCH_REF" -- "${list_b[@]}"; git ls-tree -r "$MAIN_REF" -- "${list_m[@]}"; } | awk '$1 == "120000" {print $4}')"
[ -z "$links" ] || { echo "symbolic links are not copied:" >&2; echo "$links" >&2; fail=1; }
# 同じパスを 2 つの ref から写さない
dup="$(printf '%s\n' "${list_b[@]}" "${list_m[@]}" | sort | uniq -d)"
[ -z "$dup" ] || { echo "path listed twice: $dup" >&2; fail=1; }
[ "$fail" -eq 0 ] || exit 1

# コミット済みの中身を写す（作業ツリーの変更は写らない）
git archive --format=tar "$BRANCH_REF" -- "${list_b[@]}" | tar -x -C "$OUT"
git archive --format=tar "$MAIN_REF" -- "${list_m[@]}" | tar -x -C "$OUT"
# kit と原稿は短いパスへ
mkdir -p "$OUT/kit" "$OUT/paper"
mv "$OUT/$KIT" "$OUT/kit/symbols"
for f in "${PAPER_FILES[@]}"; do mv "$OUT/$PAPER/$f" "$OUT/paper/$f"; done
mv "$OUT/$PAPER/figdata" "$OUT/paper/figdata"
rm -rf "$OUT/papers"

# 書き換え: 補足の \journalline を空に（行がちょうど 1 つあることを確かめる）
SUP="$OUT/paper/supplement.tex"
[ "$(grep -c '^\\newcommand{\\journalline}{' "$SUP")" = 1 ] || { echo "journalline line not found once" >&2; exit 1; }
python3 -I - "$SUP" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"^\\newcommand\{\\journalline\}\{.*\}$", r"\\newcommand{\\journalline}{}", s, flags=re.M)
assert n == 1
# このコメントは提出の版の作り方を書いたもので、公開の写しには要らない（状態を書かない）
c = "% The journal line is required in the submitted file only; it is left out of public copies.\n"
assert s2.count(c) == 1, "comment line not found once"
s2 = s2.replace(c, "")
f = "% Online Resource 1 (supplementary information, file ESM_1.pdf) for the manuscript in main.tex.\n"
assert s2.startswith(f), "first comment line not as expected"
s2 = s2.replace(f, "% Online Resource 1 (supplementary information) for the manuscript in main.tex.\n", 1)
open(p, "w", encoding="utf-8").write(s2)
PY

export TZ=UTC0
# GSE の git の来歴（GSE は非公開なので、各ファイルを最初と最後に入れたコミットの時刻と id を表にする）
row() {  # <ref> <path in GSE> <path in release>
  local first last
  first="$(git log "$1" --diff-filter=A --follow --format='%H%x09%cd' --date=format-local:'%Y-%m-%dT%H:%M:%SZ' -- "$2" | tail -1)"
  last="$(git log "$1" -1 --format='%H%x09%cd' --date=format-local:'%Y-%m-%dT%H:%M:%SZ' -- "$2")"
  [ -n "$first" ] && [ -n "$last" ] || { echo "no commit found for $2" >&2; exit 1; }
  printf '%s\t%s\t%s\t%s\n' "$3" "$2" "$first" "$last"
}
{
  printf 'path\tgse_path\tfirst_commit\tfirst_commit_utc\tlast_commit\tlast_commit_utc\n'
  for f in "${list_b[@]}"; do
    case "$f" in
      "$KIT"/*) rel="kit/symbols/${f#$KIT/}" ;;
      "$PAPER"/*) rel="paper/${f#$PAPER/}" ;;
      *) rel="$f" ;;
    esac
    row "$BRANCH_REF" "$f" "$rel"
  done
  for f in "${list_m[@]}"; do row "$MAIN_REF" "$f" "$f"; done
} | sort > "$OUT/gse-commits.tsv.tmp"
{ head -1 <(printf 'path\tgse_path\tfirst_commit\tfirst_commit_utc\tlast_commit\tlast_commit_utc\n'); grep -v '^path	' "$OUT/gse-commits.tsv.tmp"; } > "$OUT/gse-commits.tsv"
rm "$OUT/gse-commits.tsv.tmp"
printf 'ref\tcommit\nbranch\t%s\nmain\t%s\n' "$(git rev-parse "$BRANCH_REF")" "$(git rev-parse "$MAIN_REF")" > "$OUT/gse-source.tsv"
echo "copied $(( ${#list_b[@]} + ${#list_m[@]} )) files into $OUT"
