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
import stat
import sys

NAME = re.compile(r"^gse_[a-z0-9]+_\d{8}_\d{6}\.ndjson$|^gse_\d{8}_\d{6}\.ndjson$")


def first_meta(lines):
    """最初の meta（session_start を持つ行）。lines は bytes の行。"""
    for line in lines:
        try:
            r = json.loads(line.decode("utf-8"))
        except ValueError:   # UnicodeDecodeError も含む
            continue
        if isinstance(r, dict) and r.get("type") == "meta" and "session_start" in r:
            return r
    return None


def split_lines(raw):
    """bytes を `\n` だけで行に分ける（splitlines は U+2028 などでも分けて 1 行を 2 行にするので使わない）。

    返り値は (行の列, 最後の行を除いたか)。最後の行が UTF-8 として・JSON として読めなければ除く
    （落ちて切れた記録・C2）。それより前の行は手を付けずに残し、読めなければ gse-replay が止める。
    """
    lines = raw.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    if lines:
        try:
            json.loads(lines[-1].decode("utf-8"))
        except ValueError:
            return lines[:-1], True
    return lines, False


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--require-synthetic", action="store_true",
                    help="合成の記録（meta.synthetic が真）だけを受ける。試しの通しで本人の記録を回さないため")
    ap.add_argument("--ledger", help="区間指定削除の台帳。写しを ledger.jsonl として作り、SHA-256 を manifest に書く")
    a = ap.parse_args(argv)
    os.makedirs(a.out, mode=0o700, exist_ok=True)
    all_names = os.listdir(a.records_dir)
    names = sorted(n for n in all_names if NAME.match(n))
    skipped_name = sum(1 for n in all_names if n.endswith(".ndjson") and not NAME.match(n))
    manifest, skipped, truncated, not_regular = [], 0, 0, 0
    for n in names:
        path = os.path.join(a.records_dir, n)
        # シンボリックリンク・通常でないファイルは読まない（security-checker の指摘）
        if not stat.S_ISREG(os.lstat(path).st_mode):
            not_regular += 1
            continue
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as f:
            raw = f.read()
        lines, cut = split_lines(raw)
        meta = first_meta(lines)
        if meta is None or meta.get("s1_mode") in (None, False, ""):
            skipped += 1
            continue
        if a.require_synthetic and meta.get("synthetic") is not True:
            print("--require-synthetic: 合成でない段 1 の記録がある。本人の記録は RECORDS_OUT なしで回す", file=sys.stderr)
            sys.exit(4)
        truncated += cut
        out_name = f"r{len(manifest):03d}.ndjson"
        dst = os.path.join(a.out, out_name)
        fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as g:
            for line in lines:
                g.write(line + b"\n")
        manifest.append({"name": n, "sha256": hashlib.sha256(raw).hexdigest(), "copy": out_name,
                         "last_line_cut": cut})
    if not manifest:
        print("段 1 の記録（meta.s1_mode）が 1 本も無い", file=sys.stderr)
        sys.exit(3)
    ledger = None
    if a.ledger:
        # 回の途中で台帳が書き換わっても結果を再現できるよう、写しを使い SHA-256 を残す（/cross-review 指摘 9）
        with open(a.ledger, "rb") as f:
            raw = f.read()
        fd = os.open(os.path.join(a.out, "..", "ledger.jsonl"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as g:
            g.write(raw)
        ledger = {"name": os.path.basename(a.ledger), "sha256": hashlib.sha256(raw).hexdigest(), "copy": "ledger.jsonl"}
    manifest = {"records": manifest, "redaction_ledger": ledger}
    with open(a.manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({"files": len(manifest["records"]), "skipped_not_s1": skipped, "skipped_name": skipped_name,
                      "not_regular": not_regular, "last_line_cut": truncated,
                      "ledger": ledger is not None},
                     ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
