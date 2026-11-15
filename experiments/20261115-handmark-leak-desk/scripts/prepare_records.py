"""本人の記録を作業のディレクトリへ写す（conditions.md C2・C8）。中身は表示しない。

- 選ぶのは `gse_*.ndjson` のうち、最初の `meta`（`session_start` を持つ行）に `s1_mode` があるものだけ
  （段 1 の記録。O1 などの記録は選ばない）。
- 落ちて最後の行が切れた記録は、最後の行を除いた写しを作る（C2）。それ以外の読めない行はそのまま写し、
  gse-replay が止める（fail-closed）。
- 写しの名前は番号だけ（`r000.ndjson`）。元の名前と SHA-256 は manifest に書く（data.md に写すため。
  ファイル名は日付と時刻の形で、個人に結びつく名を含まない）。
- 標準出力には数だけを出す。

使い方: python prepare_records.py --records-dir DIR --out DIR --manifest PATH
"""
import argparse
import hashlib
import json
import os
import re
import sys

NAME = re.compile(r"^gse_[a-z0-9]+_\d{8}_\d{6}\.ndjson$|^gse_\d{8}_\d{6}\.ndjson$")


def first_meta(lines):
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("type") == "meta" and "session_start" in r:
            return r
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out, mode=0o700, exist_ok=True)
    names = sorted(n for n in os.listdir(a.records_dir) if NAME.match(n))
    manifest, skipped, truncated = [], 0, 0
    for n in names:
        with open(os.path.join(a.records_dir, n), "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8")
        lines = text.splitlines()
        meta = first_meta(lines)
        if meta is None or meta.get("s1_mode") in (None, False, ""):
            skipped += 1
            continue
        cut = False
        if lines:
            try:
                json.loads(lines[-1])
            except ValueError:
                lines = lines[:-1]
                cut = True
                truncated += 1
        out_name = f"r{len(manifest):03d}.ndjson"
        dst = os.path.join(a.out, out_name)
        fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as g:
            g.write("\n".join(lines))
            if lines:
                g.write("\n")
        manifest.append({"name": n, "sha256": hashlib.sha256(raw).hexdigest(), "copy": out_name,
                         "last_line_cut": cut})
    if not manifest:
        print("段 1 の記録（meta.s1_mode）が 1 本も無い", file=sys.stderr)
        sys.exit(3)
    with open(a.manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({"files": len(manifest), "skipped_not_s1": skipped, "last_line_cut": truncated},
                     ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
