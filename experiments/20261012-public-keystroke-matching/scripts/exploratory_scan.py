"""Exploratory analysis 7 of notes.md, "Exploratory analyses, part 3": A2-scan (exploratory_lambda.py has the
computation and the controls; align_local.py the free-start alignment). Run after analysis 6 has passed its positive
controls: the strongest attacker here also takes the analysis 6 variants, read from analysis 6's cache.

    python -I scripts/exploratory_scan.py --source klicke --root raw/klicke/extracted/WritingTask \
        --main-cache raw/derived/main_cache/33fa95833296d7a5 --compare-main results/main.json \
        --lambda-cache raw/derived/explore_cache/analysis6/<fingerprint> \
        --compare-lambda results/exploratory_lambda.json \
        --cache-dir raw/derived/explore_cache --out results/exploratory_scan.json --workers 12 [--time-first 10]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exploratory_lambda as X  # noqa: E402


def main():
    ap = X.parser(__doc__.split("\n")[0])
    ap.add_argument("--lambda-cache", required=True, help="analysis 6's cache folder (with its fingerprint)")
    ap.add_argument("--compare-lambda", required=True, help="exploratory_lambda.json")
    X.run(ap.parse_args(), 7)


if __name__ == "__main__":
    main()
