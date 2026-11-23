"""O1 の中間（conditions.md C1）。1 ファイルずつ、停滞の始まり・観測区間・ADR-024 の単位の結果・
型に要る時刻の並びだけを repo の外の中間に書く。本文は読まない（key 行は時刻・press・category だけ）。

usage: build_o1.py <gse-replay> <work_dir> <ndjson>...
中間: <work_dir>/<basename>.json（入力の SHA-256 を持つ。同じ SHA-256 の中間があれば作り直さない）
"""
import hashlib
import json
import os
import subprocess
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def events(path):
    keys, ptr, focus, paste, types = [], [], [], [], {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                types["<unparsed>"] = types.get("<unparsed>", 0) + 1
                continue
            if not isinstance(o, dict):
                types["<non_object>"] = types.get("<non_object>", 0) + 1
                continue
            ty = o.get("type")
            types[str(ty)] = types.get(str(ty), 0) + 1
            if ty == "key" and o.get("press") is True:
                keys.append([o["t"], o.get("category")])
            elif ty == "pointer_bin":
                ptr.append([o["t"], o.get("moved", 0), o.get("buttons", 0), o.get("wheel", 0)])
            elif ty == "focus_transition":
                focus.append(o["t"])
            elif ty == "paste":
                paste.append([o["t"], o.get("external_paste_chars")])
    keys.sort()
    ptr.sort()
    return {"keys": keys, "pointer": ptr, "focus": sorted(focus), "paste": sorted(paste), "types": types}


def run_json(cmd, tmp):
    with open(tmp, "w") as out, open(tmp + ".err", "w") as err:
        subprocess.run(cmd, stdout=out, stderr=err, check=True)
    d = json.load(open(tmp))
    # 警告は行の中身を残さず、種類（解析できない行の警告か、それ以外か）の数だけを持つ
    lines = open(tmp + ".err", encoding="utf-8", errors="replace").read().splitlines()
    warn = {"failed_to_parse": sum(1 for x in lines if "failed to parse" in x),
            "other_nonempty_lines": sum(1 for x in lines if x.strip() and "failed to parse" not in x)}
    os.remove(tmp)
    os.remove(tmp + ".err")
    return d, warn


def build(replay, work, path):
    b = os.path.basename(path)[:-len(".ndjson")]
    dst = os.path.join(work, b + ".json")
    digest = sha256(path)
    made_by = {"replay_sha256": sha256(replay), "build_o1_sha256": sha256(os.path.abspath(__file__))}
    if os.path.exists(dst):
        old = json.load(open(dst))
        if old.get("input_sha256") == digest and old.get("made_by") == made_by:
            return "kept"
    feat, w1 = run_json([replay, path, "--features"], os.path.join(work, "tmp_features.json"))
    onsets = [[r["stall_onset"]["s_ms"], r["stall_onset"]["t0_ms"]] for r in feat["rows"]
              if r["stall_onset"]["is_onset"]]
    p = feat["provenance"]
    met, w2 = run_json([replay, path, "--metrics", "--json"], os.path.join(work, "tmp_metrics.json"))
    rfr = met["outcome"]["receipt_free_resumption"]
    ev = events(path)
    if digest != sha256(path):
        sys.exit("中間を作る間に入力が変わった（書き込み中のファイルの可能性）: " + b)
    out = {"input_sha256": digest, "made_by": made_by, "observed_intervals": p["observed_intervals"],
           "hmm_version": p.get("hmm_version"), "o1_mode": p.get("o1_mode"),
           "onsets": onsets, "receipt_free_resumption": rfr,
           "replay_stderr_bytes": {"features": w1, "metrics": w2}, **ev}
    json.dump(out, open(dst, "w"))
    return "built"


if __name__ == "__main__":
    replay, work, *files = sys.argv[1:]
    os.makedirs(work, exist_ok=True)
    for i, f in enumerate(files):
        print(i + 1, len(files), build(replay, work, f), file=sys.stderr)
