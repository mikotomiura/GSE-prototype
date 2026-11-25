"""変異で自己検査が赤になるか（conditions.md K5）。どれか 1 つでも緑のままなら終了コード 1。

usage: python3 -I check_mutations.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUTANTS = ("strat", "unanswered", "cutoff0", "early", "gt", "nowindow", "crossday")


def main():
    bad = []
    for m in MUTANTS:
        env = dict(os.environ, STOPRULE_MUTATE=m)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "selftest.py")], env=env,
                           capture_output=True, text=True)
        red = r.returncode != 0 and "SELFTEST FAIL" in r.stdout
        fails = [ln[5:] for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
        print(("red   " if red else "GREEN ") + m + ("  <- " + " / ".join(fails) if fails else ""))
        if not red:
            bad.append(m)
    # 変異なしは緑であること（対照）
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "selftest.py")], capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if k != "STOPRULE_MUTATE"})
    base_ok = r.returncode == 0 and "SELFTEST PASS" in r.stdout
    print(("green " if base_ok else "RED   ") + "(変異なし)")
    print("MUTATIONS", "PASS" if not bad and base_ok else "FAIL")
    return 0 if not bad and base_ok else 1


if __name__ == "__main__":
    sys.exit(main())
