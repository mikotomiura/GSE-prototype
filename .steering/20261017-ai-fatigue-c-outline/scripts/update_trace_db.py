"""After full texts or abstracts change, bring the Drive copy and both databases up to date in one run (decision 36).

1. Copy to the Drive folder AI-fatigue/TRACE/fulltext every file of ~/Documents/TRACE/fulltext that is missing there
   or differs in size (never deletes anything on Drive).
2. Wait until Drive for desktop has given each file a Drive ID (up to --wait seconds), then write drive_links.json.
3. Rebuild author 1's workbook (TRACE_database.xlsx, carrying over what author 1 has entered) and the whole database
   (TRACE_database_all.xlsx) in the Drive folder.
New abstracts need their translations in ja.json first; this script does not translate.

Run (openpyxl via uv):
    uv run --with openpyxl python update_trace_db.py
(--source-db defaults to the final version of the source database, next to the TRACE folder on Drive.)
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

from c_screening import drive_trace
from drive_links import item_id

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="~/Documents/TRACE/data")
    ap.add_argument("--fulltext", default="~/Documents/TRACE/fulltext")
    ap.add_argument("--source-db", default=str(drive_trace().parent / "AI_fatigue_database_2026-10-18_final.xlsx"))
    ap.add_argument("--abstracts34", default="~/TRACE-screening/check34-r3/in")
    ap.add_argument("--wait", type=int, default=600)
    a = ap.parse_args()
    data, ft = os.path.expanduser(a.data), os.path.expanduser(a.fulltext)
    drive = drive_trace()
    if not drive.is_dir():
        sys.exit(f"the Drive folder is not there: {drive}")
    dft = drive / "fulltext"
    copied = []
    for name in sorted(os.listdir(ft)):
        src, dst = os.path.join(ft, name), dft / name
        if not dst.exists() or dst.stat().st_size != os.path.getsize(src):
            shutil.copy2(src, dst)
            copied.append(name)
    print(f"copied to Drive: {len(copied)} {copied[:10]}")
    deadline = time.time() + a.wait
    while True:
        waiting = [n for n in copied if not item_id(str(dft / n))]
        if not waiting:
            break
        if time.time() > deadline:
            sys.exit(f"no Drive ID after {a.wait} s: {waiting[:10]}; run again later")
        time.sleep(10)
    py = sys.executable
    steps = [
        [py, "drive_links.py", "--drive", str(dft), "--fulltext", ft, "--data", data],
        [py, "make_trace_db.py", "--data", data, "--fulltext", ft, "--out", str(drive / "TRACE_database.xlsx")],
        [py, "make_trace_all_db.py", "--data", data, "--source-db", a.source_db, "--abstracts34", a.abstracts34,
         "--out", str(drive / "TRACE_database_all.xlsx")],
    ]
    for cmd in steps:
        if subprocess.run(cmd, cwd=HERE).returncode != 0:
            sys.exit(f"stopped at {cmd[1]}")


if __name__ == "__main__":
    main()
