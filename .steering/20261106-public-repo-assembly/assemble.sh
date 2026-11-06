#!/usr/bin/env bash
# 論文 1 の公開 repo（stall-runup-equivalence）の中身を、GSE の作業ツリーの「追跡済みのファイル」から写す。
# 使い方: assemble.sh <GSE の checkout> <出力先（空か、無いディレクトリ）>
# 写す一覧はこのファイルが単一の記録。写した後の検査は出力先の tools/verify.sh。
# 終了コード: 0 = 写した / 1 = 一覧のファイルが無い・未追跡・作業ツリーで変更あり / 2 = 使い方
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: assemble.sh <gse-checkout> <out>" >&2; exit 2; }
SRC="$(cd "$1" && pwd -P)"; OUT="$2"
if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null | grep -v '^\.git$' || true)" ]; then
  echo "output dir is not empty (only .git may exist): $OUT" >&2; exit 2
fi
# 出力先が GSE の中でないことを、作る前に確かめる（親をたどって実パスで比べる）
parent="$OUT"; while [ ! -e "$parent" ]; do parent="$(dirname "$parent")"; done
case "$(cd "$parent" && pwd -P)/" in "$SRC"/*) echo "output must be outside the GSE checkout" >&2; exit 2 ;; esac
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd -P)"
case "$OUT/" in "$SRC"/*) echo "output must be outside the GSE checkout" >&2; exit 2 ;; esac

# 1) ディレクトリごと写す（追跡済みのファイルだけ）
WHOLE=(
  experiments/20261104-cs1-landscape
  experiments/20261105-findings-paper1-prefreeze
  experiments/20261106-findings-paper1-exploration
  experiments/20261107-findings-paper1-round3-checks
)
# 2) 依存先の実験: 変換と解析のスクリプト・実行の手順・条件・データの記録（results と notes は入れない）
DEP_DIRS=(
  experiments/20261031-coauthor-pre-request-signal
  experiments/20261101-klicke-early-stall-trigger
  experiments/20261102-public-data-landscape
  experiments/20261103-coauthor-per-person
)
# 3) GSE の docs・.steering・src-tauri は入れない（研究者の指示 2026-11-06・判断 2）。manifest のうち docs と .steering の
#    6 件は tools/check_manifest.py が「公開しない」と示し、src-tauri の停滞の定義 1 件は estimator/prereg/ の同じバイトで照合する。
# 4) 推定器の crate は estimator/ へ、論文の tex は paper/ へ
CRATE=papers/public-data-findings/kit/estimator
PAPER=papers/public-data-findings/manuscript

cd "$SRC"
list=()
fail=0
for d in "${WHOLE[@]}"; do
  n0=${#list[@]}; while IFS= read -r f; do list+=("$f"); done < <(git ls-files -- "$d")
  [ "${#list[@]}" -gt "$n0" ] || { echo "no tracked files under $d" >&2; fail=1; }
done
for d in "${DEP_DIRS[@]}"; do
  n0=${#list[@]}
  while IFS= read -r f; do
    case "$f" in
      "$d"/scripts/*|"$d"/run*.sh|"$d"/conditions*.md|"$d"/data.md|"$d"/env.md|"$d"/SEED|"$d"/mutate.sh) list+=("$f") ;;
    esac
  done < <(git ls-files -- "$d")
  [ "${#list[@]}" -gt "$n0" ] || { echo "no scripts under $d" >&2; fail=1; }
done

# 必ずあるはずのもの（無ければ古い・別の checkout）
for f in experiments/20261105-findings-paper1-prefreeze/confirm-manifest.sha256 \
         experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py \
         "$CRATE/Cargo.toml" "$CRATE/Cargo.lock" "$CRATE/prereg/p1-episode.json" "$PAPER/main.tex"; do
  git ls-files --error-unmatch -- "$f" >/dev/null 2>&1 || { echo "required file not tracked: $f" >&2; fail=1; }
done
# シンボリックリンク（mode 120000）は写さない
links="$(git ls-files -s -- "${list[@]}" "$CRATE" "$PAPER" | awk '$1 == "120000" {print $4}')"
[ -z "$links" ] || { echo "symbolic links are not copied:" >&2; echo "$links" >&2; fail=1; }
for f in "${list[@]}"; do
  git ls-files --error-unmatch -- "$f" >/dev/null 2>&1 || { echo "not tracked: $f" >&2; fail=1; continue; }
done
# 作業ツリーの変更があれば止める（写すのはコミットした中身）
dirty="$(git status --porcelain -- "${list[@]}" "$CRATE" "$PAPER")"
[ -z "$dirty" ] || { echo "uncommitted changes:" >&2; echo "$dirty" >&2; fail=1; }
[ "$fail" -eq 0 ] || exit 1

for f in "${list[@]}"; do mkdir -p "$OUT/$(dirname "$f")"; cp -p "$f" "$OUT/$f"; done
while IFS= read -r f; do
  rel="${f#$CRATE/}"; mkdir -p "$OUT/estimator/$(dirname "$rel")"; cp -p "$f" "$OUT/estimator/$rel"
done < <(git ls-files -- "$CRATE")
while IFS= read -r f; do
  rel="${f#$PAPER/}"; mkdir -p "$OUT/paper/$(dirname "$rel")"; cp -p "$f" "$OUT/paper/$rel"
done < <(git ls-files -- "$PAPER")

export TZ=UTC0
# 5) GSE の git の来歴（GSE は非公開なので、各ファイルを最初と最後に入れたコミットの時刻と id を表にする）
{
  printf 'path\tfirst_commit\tfirst_commit_utc\tlast_commit\tlast_commit_utc\n'
  for f in "${list[@]}"; do
    first="$(git log --diff-filter=A --follow --format='%H%x09%cd' --date=format-local:'%Y-%m-%dT%H:%M:%SZ' -- "$f" | tail -1)"
    last="$(git log -1 --format='%H%x09%cd' --date=format-local:'%Y-%m-%dT%H:%M:%SZ' -- "$f")"
    [ -n "$first" ] && [ -n "$last" ] || { echo "no commit found for $f" >&2; exit 1; }
    printf '%s\t%s\t%s\n' "$f" "$first" "$last"
  done
} > "$OUT/gse-commits.tsv.tmp"
mv "$OUT/gse-commits.tsv.tmp" "$OUT/gse-commits.tsv"
printf 'gse_head\t%s\n' "$(git rev-parse HEAD)" > "$OUT/gse-source.tsv"
echo "copied ${#list[@]} files + crate into $OUT"
