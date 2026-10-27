"""Decision 117: drive_links.py of TRACE, with one exception. After S13-18.pdf was replaced in the synced folder
(decision 115), Drive for desktop no longer puts the Drive ID attribute on the local file, although the Drive API
shows the same file (same ID and size). Every other file is checked as drive_links.py checks it (in the Drive folder,
same size, has an ID). For the files named in OVERRIDE, the ID is taken from the current drive_links.json, and only if
it is the ID given here (checked through the Drive API by hand) and the synced file has the local size.
Usage: drive_links_with_override.py <drive fulltext dir> <fulltext dir> <data dir>"""
import json, os, sys
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from drive_links import item_id

OVERRIDE = {"S13-18.pdf": "1nJ3WoYUrbKnHKaZeMEvUnKdOpdeKsxwL"}   # Drive API 2026-10-27: 2,664,837 bytes, title S13-18.pdf

drive, ft, data = (os.path.expanduser(x) for x in sys.argv[1:4])
old = json.load(open(os.path.join(data, "drive_links.json"), encoding="utf-8"))
links, problems = {}, []
for name in sorted(os.listdir(ft)):
    local, synced = os.path.join(ft, name), os.path.join(drive, name)
    if not os.path.exists(synced):
        problems.append(f"{name}: not in the Drive folder")
    elif os.path.getsize(synced) != os.path.getsize(local):
        problems.append(f"{name}: size differs from the local copy")
    elif item_id(synced):
        links[name] = f"https://drive.google.com/file/d/{item_id(synced)}/view"
    elif name in OVERRIDE and old.get(name) == f"https://drive.google.com/file/d/{OVERRIDE[name]}/view":
        links[name] = old[name]
    else:
        problems.append(f"{name}: no Drive ID yet (still syncing?)")
if problems:
    sys.exit(f"{len(problems)} files not ready; no table written:\n  " + "\n  ".join(problems[:20]))
with open(os.path.join(data, "drive_links.json"), "w", encoding="utf-8") as f:
    json.dump(links, f, indent=1)
print(f"wrote drive_links.json: {len(links)} files")
