"""実データの照合（公開しない）。生データから書き直しで記号を作り、試験の中間（replay の 1 回目の出力）と比べる。
出すのは件数だけ（書き手・セッション・課題の番号と値は出さない）。

使い方:
  python3 -I check_against_replay.internal.py coauthor <coauthor.zip> <old_work_dir(sessions.json)> <obs_work_dir> <metadata.csv>...
  python3 -I check_against_replay.internal.py cs1 <keystrokes.csv> <holdout.json> <obs_work_dir>
"""
import csv
import json
import os
import sys
import zipfile
from collections import Counter, defaultdict

KIT = os.environ.get("KIT", "/Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols")
sys.path.insert(0, KIT)
from symbolizer import load_constants, symbolize  # noqa: E402
from adapters import coauthor, cs1_2021  # noqa: E402

C = load_constants()


def cmp_rows(got, feat):
    """feat: [t, p_flow, p_inc, p_stuck, ewma_x, ewma_y, obs, alpha]"""
    if len(got) != len(feat):
        return "row_count"
    for g, f in zip(got, feat):
        if g[0] != f[0]:
            return "time"
        if g[3] != f[6]:
            return "symbol"
        if g[1].hex() != float(f[4]).hex() or g[2].hex() != float(f[5]).hex():
            return "xy_bits"
        if g[4] != f[7]:
            return "alpha"
    return None


def coauthor_main(zp, old, work, metas):
    keep = json.load(open(os.path.join(old, "sessions.json")))
    sid2w = {}
    for p in metas:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            sid2w[r["session_id"]] = r["worker_id"]
    res = Counter()
    rows_total = sym_rows_eq = 0
    with zipfile.ZipFile(zp) as z:
        by_sid = {os.path.basename(m)[:-len(".jsonl")]: m for m in z.namelist() if m.endswith(".jsonl")}
        sids = sorted(set(by_sid) & set(sid2w))
        for k in sorted(keep):
            i = int(k)
            fp = os.path.join(work, "s%05d.json" % i)
            if not os.path.exists(fp):
                res["no_intermediate"] += 1
                continue
            rows = [json.loads(l) for l in z.read(by_sid[sids[i]]).decode("utf-8").splitlines() if l.strip()]
            t0, presses = coauthor.presses_from_rows(rows)
            feat = json.load(open(fp))["feat"]
            got = symbolize(t0, presses, C)
            kind = cmp_rows(got, feat)
            res[kind or "match"] += 1
            rows_total += len(feat)
            sym_rows_eq += sum(1 for g, f in zip(got, feat) if g[0] == f[0] and g[3] == f[6])
    print(json.dumps({"dataset": "coauthor", "units": dict(res), "feat_rows": rows_total,
                      "rows_same_time_and_symbol": sym_rows_eq}))


def cs1_main(path, hold_p, work):
    hold = set(json.load(open(hold_p))["2021"])
    csv.field_size_limit(10**9)
    units = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["SubjectID"] in hold:
                continue
            units[(row["SubjectID"], row["AssignmentID"])].append(row)
    res = Counter()
    rows_total = sym_rows_eq = 0
    for i, k in enumerate(sorted(units)):
        fp = os.path.join(work, "u%05d.json" % i)
        if not os.path.exists(fp):
            res["no_intermediate"] += 1
            continue
        got = []
        for t0, presses in cs1_2021.blocks_from_rows(units[k]):
            got += symbolize(t0, presses, C)
        feat = json.load(open(fp))["feat"]
        kind = cmp_rows(got, feat)
        res[kind or "match"] += 1
        rows_total += len(feat)
        sym_rows_eq += sum(1 for g, f in zip(got, feat) if g[0] == f[0] and g[3] == f[6])
    print(json.dumps({"dataset": "cs1_2021", "units": dict(res), "feat_rows": rows_total,
                      "rows_same_time_and_symbol": sym_rows_eq}))


if __name__ == "__main__":
    if sys.argv[1] == "coauthor":
        coauthor_main(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
    else:
        cs1_main(sys.argv[2], sys.argv[3], sys.argv[4])
