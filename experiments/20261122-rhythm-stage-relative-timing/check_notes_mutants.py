"""Mutants for check_notes.py: each broken notes.md must make it exit 1, the unbroken one 0.

Outside the instrument's fingerprint (not under scripts/). Run: python check_notes_mutants.py . <empty work dir>
The work dir gets a copy of results/<step>/main, check_notes.py and each mutated notes.md (it is removed first).
"""
import shutil
import subprocess
import sys
from pathlib import Path

exp = Path(sys.argv[1])
work = Path(sys.argv[2])
if work.exists():
    shutil.rmtree(work)
for st in ("g050", "f200"):
    shutil.copytree(exp / "results" / st / "main", work / "results" / st / "main")
shutil.copy(exp / "check_notes.py", work / "check_notes.py")
src = (exp / "notes.md").read_text(encoding="utf-8")

ROW = "| g050 | A（主） | rd | rd | rd | rd | rd | rd |"
DROP = "| g050 | D-run | 0.217・0.215・0.153・0.151 |"
AUC = "| g050 | 0.771 / 0.749 |"
for s in (ROW, DROP, AUC):
    assert src.count(s) == 1, s
MUT = {
    "none": src,
    "drop_last_col": src.replace(ROW, "| g050 | A（主） | rd | rd | rd | rd | rd |"),
    "dup_row": src.replace(ROW, ROW + "\n" + ROW.replace("| rd |", "| u |", 1)),
    "dup_row_short": src.replace(ROW, ROW + "\n| g050 | A（主） | rd |"),
    "dup_shared_prefix_short": src.replace(AUC, "| g050 | 0.1 |\n" + AUC),
    "digit": src.replace(DROP, "| g050 | D-run | 0.218・0.215・0.153・0.151 |"),
    "digit_d2": src.replace("| g050 | 窓の打鍵の数（全量） | 0.767 |", "| g050 | 窓の打鍵の数（全量） | 0.768 |"),
    "verdict_word": src.replace(ROW, "| g050 | A（主） | rd | rd | rd | rd | rd | u |"),
}
assert MUT["digit_d2"] != src
bad = 0
for name, text in MUT.items():
    (work / "notes.md").write_text(text, encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-I", str(work / "check_notes.py"), str(work)], capture_output=True, text=True)
    want = 0 if name == "none" else 1
    ok = r.returncode == want
    bad += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: exit {r.returncode} (want {want})")
print("bad", bad)
sys.exit(1 if bad else 0)
