"""Self-test of exploratory analysis 7 (A2-scan). Analysis 7 needs analysis 6's cache and output, so its checks
(align_local against align_vec and a brute force over the suffixes, the chunks, a naive scan per writer, the guard on
exploratory_lambda.json, the mutants fixed_start, keep_short_chunk and chunk_min) run inside
selftest_exploratory_lambda.py on the same synthetic main run; this file runs that self-test.

    python -I scripts/selftest_exploratory_scan.py
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sys.exit(subprocess.run([sys.executable, "-I", os.path.join(here, "selftest_exploratory_lambda.py")]).returncode)
