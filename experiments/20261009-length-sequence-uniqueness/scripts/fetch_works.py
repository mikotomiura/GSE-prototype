"""Fetch the selected Aozora Bunko zips and fix their versions by SHA-256 (design.md section 3).

  fetch_works.py --selection results/selection.json --config config.json --zips raw/zips
                 --manifest results/corpus_manifest.json [--verify-only]

Takes the first `fetch_count` works of the ordered list and the reference works. A zip already on disk is
not downloaded again. When the manifest already exists (it is committed), it is never rewritten: every zip
must have the SHA-256 recorded there and every work it fetched must be fetched again; otherwise the run
stops (the text was changed upstream, the file is damaged or the network failed). With --verify-only
nothing is downloaded. Standard library only.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, cfg):
    last = None
    for attempt in range(cfg["retries"]):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"]})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            return None
        except Exception as e:  # network errors are retried, then reported
            last = "%s: %s" % (type(e).__name__, e)
            time.sleep(cfg["interval_s"] * (attempt + 2))
    return last


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--zips", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args(argv)
    sel = json.load(open(a.selection, encoding="utf-8"))
    cfg_all = json.load(open(a.config, encoding="utf-8"))
    cfg, scfg = cfg_all["fetch"], cfg_all["selection"]
    os.makedirs(a.zips, exist_ok=True)
    known = {}
    if os.path.exists(a.manifest):
        for e in json.load(open(a.manifest, encoding="utf-8"))["works"]:
            known[e["work_id"]] = e
    ime_sha = {r["work_id"]: r["ime_sha256"] for r in scfg["reference_works"]}

    todo = [(w, "corpus") for w in sel["ordered"][:scfg["fetch_count"]]]
    todo += [(w, "reference") for w in sel["reference"]]
    entries, failed, mismatched = [], [], []
    last_request = 0.0
    for w, role in todo:
        wid = w["work_id"]
        dest = os.path.join(a.zips, wid + ".zip")
        error = None
        if not os.path.exists(dest):
            if a.verify_only:
                error = "missing"
            else:
                wait = cfg["interval_s"] - (time.time() - last_request)
                if wait > 0:
                    time.sleep(wait)
                last_request = time.time()
                error = download(w["text_url"], dest, cfg)
        entry = {"work_id": wid, "role": role, "url": w["text_url"]}
        if error is None:
            digest = sha256_file(dest)
            entry["sha256"] = digest
            entry["bytes"] = os.path.getsize(dest)
            if wid in known and known[wid].get("sha256") not in (None, digest):
                mismatched.append(wid)
            if role == "reference":
                entry["matches_ime_paper"] = digest == ime_sha.get(wid)
        else:
            entry["error"] = error
            failed.append(wid)
        entries.append(entry)
        if len(entries) % 100 == 0:
            print("fetch_works: %d / %d" % (len(entries), len(todo)), flush=True)
    if mismatched:
        print("fetch_works: SHA-256 differs from the committed manifest for %s" % ", ".join(mismatched), file=sys.stderr)
        return 1
    if known:
        # a committed manifest is never rewritten: every work it fetched must be on disk again
        missing = [e["work_id"] for e in entries if "error" in e and "sha256" in known.get(e["work_id"], {})]
        if missing:
            print("fetch_works: could not fetch %d works of the manifest (e.g. %s)" % (len(missing), missing[0]),
                  file=sys.stderr)
            return 1
    else:
        out = {"format": "manifest/1", "selection_seed": sel["seed"], "works": entries}
        with open(a.manifest, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
            f.write("\n")
    ref_match = sum(1 for e in entries if e.get("matches_ime_paper"))
    print("fetch_works: %d ok, %d failed; reference works matching the IME paper's archives: %d / %d"
          % (len(entries) - len(failed), len(failed), ref_match, len(sel["reference"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
