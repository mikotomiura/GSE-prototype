"""Write data/drive_links.json: the Google Drive link of every full-text file (decision 35).

The full texts are copied into a folder synced by Google Drive for desktop. Each synced file carries its Drive
file ID in the extended attribute 'com.google.drivefs.item-id#S'. The link is https://drive.google.com/file/d/<ID>/view.
Stops if a file has no ID yet (not synced) or differs in size from the local copy, so a partial table is not written.

Usage: python3 drive_links.py --drive <synced folder> --fulltext ~/Documents/TRACE/fulltext --data ~/Documents/TRACE/data
"""

import argparse
import json
import os
import subprocess
import sys

ATTR = "com.google.drivefs.item-id#S"


def item_id(path):
    r = subprocess.run(["xattr", "-p", ATTR, path], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive", required=True)
    ap.add_argument("--fulltext", required=True)
    ap.add_argument("--data", required=True)
    a = ap.parse_args()
    drive, ft, data = (os.path.expanduser(x) for x in (a.drive, a.fulltext, a.data))
    links, problems = {}, []
    for name in sorted(os.listdir(ft)):
        local, synced = os.path.join(ft, name), os.path.join(drive, name)
        if not os.path.exists(synced):
            problems.append(f"{name}: not in the Drive folder")
        elif os.path.getsize(synced) != os.path.getsize(local):
            problems.append(f"{name}: size differs from the local copy")
        elif not item_id(synced):
            problems.append(f"{name}: no Drive ID yet (still syncing?)")
        else:
            links[name] = f"https://drive.google.com/file/d/{item_id(synced)}/view"
    if problems:
        sys.exit(f"{len(problems)} files not ready; no table written:\n  " + "\n  ".join(problems[:20]))
    with open(os.path.join(data, "drive_links.json"), "w", encoding="utf-8") as f:
        json.dump(links, f, indent=1)
    print(f"wrote drive_links.json: {len(links)} files")


if __name__ == "__main__":
    main()
