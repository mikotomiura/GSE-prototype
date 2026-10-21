#!/usr/bin/env bash
# 段 2・3: b01〜b19 を束ごとに export-author → 出た CSV だけを add・コミット。push は最後に 1 回（手で）。
set -euo pipefail
cd "$HOME/TRACE/scripts"
for n in $(seq -w 1 19); do
  b="b$n"
  out="../screening/s2/$b.author1.csv"
  if [ -e "$out" ]; then echo "skip $b (exists)"; continue; fi
  uv run -q --with openpyxl python c_screening.py export-author --stage 2 --batch "$b"
  [ -e "$out" ] || { echo "no $out after export-author" >&2; exit 1; }
  git -C "$HOME/TRACE" add -- "screening/s2/$b.author1.csv"
  counts=$(python3 -I -c 'import csv,sys,collections;c=collections.Counter(r["decision"] for r in csv.DictReader(open(sys.argv[1])));print(", ".join(f"{c[k]} {k}" for k in ("include","exclude","pending")))' "$out")
  git -C "$HOME/TRACE" commit -q -m "Screening stage 2, batch $b: author 1's decisions ($counts)"
  echo "done $b"
done
git -C "$HOME/TRACE" status --short
