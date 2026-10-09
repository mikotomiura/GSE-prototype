"""Fetch the selected Aozora Bunko zips and fix their versions by SHA-256 (design.md section 3).

  fetch_works.py --selection results/selection.json --config config.json --zips raw/zips
                 --manifest results/corpus_manifest.json [--verify-only]

Takes the first `fetch_count` works of the ordered list and the reference works. A zip already on disk is
not downloaded again. Work IDs must be six digits and URLs must point to https://www.aozora.gr.jp/cards/;
anything else stops the run (the values come from the index CSV).

When the manifest already exists (it is committed), it is never rewritten: the works to fetch must be
exactly the works it lists, every zip must have the SHA-256 recorded there, and every work it fetched must
be fetched again; otherwise the run stops (the selection or the text changed, the file is damaged or the
network failed). --verify-only needs the manifest, downloads nothing, writes nothing and checks every work
the manifest lists. Standard library only.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

WORK_ID_RE = re.compile(r"[0-9]{6}")
SITE_PREFIX = "https://www.aozora.gr.jp/"
URL_PREFIX = SITE_PREFIX + "cards/"
MAX_ZIP_BYTES = 20 * 1024 * 1024  # the largest archive in the corpus is far below this


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def check_entry(wid, url):
    if not WORK_ID_RE.fullmatch(wid):
        raise SystemExit("fetch_works: work ID %r is not six digits" % wid)
    if not url.startswith(URL_PREFIX) or not url.endswith(".zip"):
        raise SystemExit("fetch_works: URL %r is not an Aozora Bunko card archive" % url)


class SameSiteRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only inside https://www.aozora.gr.jp/ (the checked URL must not lead elsewhere)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith(SITE_PREFIX):
            raise urllib.error.HTTPError(newurl, code, "redirect outside %s refused" % SITE_PREFIX, headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(SameSiteRedirect)


def fetch_bytes(url, cfg):
    """The body of url, or an exception. A body longer than MAX_ZIP_BYTES, shorter than its Content-Length
    (read(amt) does not raise on a truncated response) or not a readable zip archive is refused."""
    req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"]})
    with _OPENER.open(req, timeout=60) as r:
        declared = r.headers.get("Content-Length")
        if declared is not None and int(declared) > MAX_ZIP_BYTES:
            raise ValueError("declared length %s is larger than %d bytes" % (declared, MAX_ZIP_BYTES))
        data = r.read(MAX_ZIP_BYTES + 1)
    if len(data) > MAX_ZIP_BYTES:
        raise ValueError("larger than %d bytes" % MAX_ZIP_BYTES)
    if declared is not None and len(data) != int(declared):
        raise ValueError("truncated: %d of %s bytes" % (len(data), declared))
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        bad = z.testzip()
    if bad is not None:
        raise ValueError("damaged member %s" % bad)
    return data


def download(url, dest, cfg):
    last = None
    for attempt in range(cfg["retries"]):
        try:
            data = fetch_bytes(url, cfg)
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            return None
        except Exception as e:  # network errors and refused bodies are retried, then reported
            last = "%s: %s" % (type(e).__name__, e)
            time.sleep(cfg["interval_s"] * (attempt + 2))
    return last


def verify_only(manifest_path, zips):
    if not os.path.exists(manifest_path):
        print("fetch_works: --verify-only needs the manifest %s" % manifest_path, file=sys.stderr)
        return 1
    works = json.load(open(manifest_path, encoding="utf-8"))["works"]
    bad = []
    for e in works:
        if "sha256" not in e:
            continue
        check_entry(e["work_id"], e["url"])
        path = os.path.join(zips, e["work_id"] + ".zip")
        if not os.path.exists(path) or sha256_file(path) != e["sha256"]:
            bad.append(e["work_id"])
    if bad:
        print("fetch_works: %d works missing or different from the manifest (e.g. %s)" % (len(bad), bad[0]),
              file=sys.stderr)
        return 1
    print("fetch_works: all %d works of the manifest are on disk with the recorded SHA-256"
          % sum(1 for e in works if "sha256" in e))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--zips", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args(argv)
    if a.verify_only:
        return verify_only(a.manifest, a.zips)
    sel = json.load(open(a.selection, encoding="utf-8"))
    cfg_all = json.load(open(a.config, encoding="utf-8"))
    cfg, scfg = cfg_all["fetch"], cfg_all["selection"]
    os.makedirs(a.zips, exist_ok=True)
    ime_sha = {r["work_id"]: r["ime_sha256"] for r in scfg["reference_works"]}

    todo = [(w, "corpus") for w in sel["ordered"][:scfg["fetch_count"]]]
    todo += [(w, "reference") for w in sel["reference"]]
    for w, _role in todo:
        check_entry(w["work_id"], w["text_url"])
    known = None
    if os.path.exists(a.manifest):
        known_list = json.load(open(a.manifest, encoding="utf-8"))["works"]
        if [(e["work_id"], e["role"], e["url"]) for e in known_list] != \
                [(w["work_id"], role, w["text_url"]) for w, role in todo]:
            print("fetch_works: the selection differs from the committed manifest (index, seed or config changed)",
                  file=sys.stderr)
            return 1
        known = {e["work_id"]: e for e in known_list}

    entries, failed, mismatched = [], [], []
    last_request = 0.0
    for w, role in todo:
        wid = w["work_id"]
        dest = os.path.join(a.zips, wid + ".zip")
        error = None
        if not os.path.exists(dest):
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
            if known is not None and known[wid].get("sha256") not in (None, digest):
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
        print("fetch_works: SHA-256 differs from the committed manifest for %s. If the file is damaged, delete it "
              "and run again; if Aozora Bunko changed the text, the recorded selection cannot be reproduced "
              "(data.md)." % ", ".join(mismatched), file=sys.stderr)
        return 1
    if known is not None:
        # a committed manifest is never rewritten: every work it fetched must be on disk again
        missing = [e["work_id"] for e in entries if "error" in e and "sha256" in known[e["work_id"]]]
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
