"""Mac で生データから公開の kit（variants.py）で u・n を作り、今の中間の feat 行と照らして（P-U）、新しい中間を repo の外に書く。

conditions D1・V1 P-U。出すのは件数だけ（書き手・セッション・課題の番号と値を出さない）。
新しい中間（$DATA_DIR/landscape/unsmoothed_residual_<データ>.json.gz）は、tau-extend の data.py が作る単位の並べ
（書き手 → 単位 → 系列）と同じ並べで、各系列の o・u・n の印を持つ。書き手の ID は書かない。
並べが data.py と同じことは、ここで data.py の読み込みの o と照らして確かめ（dt_order_mismatched_units）、
HP Z2 の load.py でもう一度照らす。

使い方:
  python3 -I build_variants.py coauthor <coauthor.zip> <coauthor_work_obs> <seed> <out.json.gz> <gate.json> <metadata.csv>...
  python3 -I build_variants.py cs1 <keystrokes.csv> <holdout.json> <work2021_obs> <seed> <out.json.gz> <gate.json>
返り値: 0 = すべて一致、3 = 外れた行・単位がある（直さずに研究者に聞く）。
"""
import csv
import glob
import gzip
import json
import os
import sys
import zipfile
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.environ.get("KIT_DIR", os.path.realpath(os.path.join(HERE, "../../../papers/per-person-learning/kit/symbols")))
MUT = set()  # m43: 行の番号（30 行ごと）で間引く・m44: 単位の系列をつないで間引く（P-THIN）


def kit():
    if KIT not in sys.path:
        sys.path.insert(0, KIT)
    import symbolizer  # noqa: F401
    import variants
    from adapters import coauthor, cs1_2021
    return variants, coauthor, cs1_2021


def n_marks(series_times):
    """系列ごとの行の時刻のリスト → 系列ごとの n の印（kit の thinned_mask を系列ごとに当てる）。"""
    variants, _, _ = kit()
    if "m43" in MUT:
        return [[i > 0 and i % 30 == 0 for i in range(len(ts))] for ts in series_times]
    if "m44" in MUT:
        flat = [t for ts in series_times for t in ts]
        m = variants.thinned_mask(flat)
        out, i = [], 0
        for ts in series_times:
            out.append(m[i:i + len(ts)])
            i += len(ts)
        return out
    return [variants.thinned_mask(list(ts)) for ts in series_times]


def cmp_rows(got, feat):
    """kit の行 (t, o, u, xr, yr, x, y, alpha, path) と中間の feat 行 [t, p1, p2, p3, ewma_x, ewma_y, obs, alpha]。
    返り値: 外れた行の数（行の数が違えば多い方の行の数）。"""
    if len(got) != len(feat):
        return max(len(got), len(feat))
    bad = 0
    for g, f in zip(got, feat):
        if g[0] != f[0] or g[1] != f[6] or g[5].hex() != float(f[4]).hex() or g[6].hex() != float(f[5]).hex():
            bad += 1
    return bad


def unit_record(series_rows, series_mask_dt, feat):
    """series_rows: kit の呼び出しごとの行（空でない呼び出しだけ）。series_mask_dt: data.py の系列の行の添字（空でない系列だけ）。
    返り値: (記録, 系列の割りが data.py と違うか)。"""
    lens_kit = [len(r) for r in series_rows]
    lens_dt = [len(ix) for ix in series_mask_dt]
    flat_ix = [int(i) for ix in series_mask_dt for i in ix]
    split_bad = lens_kit != lens_dt or flat_ix != list(range(len(flat_ix))) or len(flat_ix) != len(feat)
    marks = n_marks([[r[0] for r in rows] for rows in series_rows])
    rec = dict(o=[[r[1] for r in rows] for rows in series_rows], u=[[r[2] for r in rows] for rows in series_rows],
               n=[[int(b) for b in m] for m in marks])
    return rec, split_bad


def coauthor_main(zp, work, seed, out, gate, metas):
    variants, coauthor, _ = kit()
    s2w = json.load(open(os.path.join(work, "sessions.json")))
    sid2w = {}
    for p in metas:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            sid2w[r["session_id"]] = r["worker_id"]
    G = dict(units=0, rows=0, rows_mismatched=0, units_split_mismatched=0, units_without_raw=0, n_rows=0)
    by_w = {}
    with zipfile.ZipFile(zp) as z:
        by_sid = {os.path.basename(m)[:-len(".jsonl")]: m for m in z.namelist() if m.endswith(".jsonl")}
        sids = sorted(set(by_sid) & set(sid2w))
        # data.py の load_coauthor と同じ選びと並べ
        for f in sorted(glob.glob(os.path.join(work, "s[0-9]*.json"))):
            sid = os.path.basename(f)[1:-5]
            if sid not in s2w:
                continue
            d = json.load(open(f))
            if len(d["observed_intervals"]) != 1 or not d["feat"]:
                continue
            i = int(sid)
            if i >= len(sids):
                G["units_without_raw"] += 1
                continue
            rows = [json.loads(l) for l in z.read(by_sid[sids[i]]).decode("utf-8").splitlines() if l.strip()]
            t0, presses = coauthor.presses_from_rows(rows)
            got = variants.variant_rows(t0, presses)
            feat = d["feat"]
            G["units"] += 1
            G["rows"] += len(feat)
            G["rows_mismatched"] += cmp_rows(got, feat)
            rec, split_bad = unit_record([got] if got else [], [list(range(len(feat)))], feat)
            G["units_split_mismatched"] += int(split_bad)
            G["n_rows"] += sum(sum(m) for m in rec["n"])
            by_w.setdefault(s2w[sid], []).append((d["observed_intervals"][0][0], rec))
    finish("coauthor", work, seed, by_w, G, out, gate)


def cs1_main(path, hold_p, work, seed, out, gate):
    variants, _, cs1_2021 = kit()
    hold = set(json.load(open(hold_p))["2021"])
    csv.field_size_limit(10 ** 9)
    raw = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["SubjectID"] in hold:
                continue
            raw[(row["SubjectID"], row["AssignmentID"])].append(row)
    keys = sorted(raw)
    u2w = json.load(open(os.path.join(work, "units.json")))
    G = dict(units=0, rows=0, rows_mismatched=0, units_split_mismatched=0, units_without_raw=0, n_rows=0)
    by_w = {}
    for uid in sorted(u2w):  # data.py の load_cs1 と同じ並べ
        d = json.load(open(os.path.join(work, "u%s.json" % uid)))
        if not d["feat"]:
            continue
        i = int(uid)
        if i >= len(keys):
            G["units_without_raw"] += 1
            continue
        series = [variants.variant_rows(t0, presses) for t0, presses in cs1_2021.blocks_from_rows(raw[keys[i]])]
        series = [s for s in series if s]
        got = [r for s in series for r in s]
        feat = d["feat"]
        ft = np.array([r[0] for r in feat], dtype=np.float64)
        blocks = sorted(d["blocks"])
        starts = np.array([b[0] for b in blocks] + [np.iinfo(np.int64).max], dtype=np.int64)
        bi = np.searchsorted(starts, ft, side="right") - 1
        dt_series = [np.nonzero(bi == j)[0] for j in range(len(blocks)) if (bi == j).sum() > 0]
        G["units"] += 1
        G["rows"] += len(feat)
        G["rows_mismatched"] += cmp_rows(got, feat)
        rec, split_bad = unit_record(series, dt_series, feat)
        G["units_split_mismatched"] += int(split_bad)
        G["n_rows"] += sum(sum(m) for m in rec["n"])
        keys_ms = sorted(int(k[0]) for k in d["keys"])
        by_w.setdefault(u2w[uid], []).append((keys_ms[0], rec))
    finish("cs1", work, seed, by_w, G, out, gate)


def finish(ds, work, seed, by_w, G, out, gate):
    """data.py と同じ並べ（書き手の鍵の順 → 単位の始まりの順・同点は読んだ順）に並べ、data.py の o と照らして書く。"""
    sys.path.insert(0, HERE)
    import pinned  # noqa: F401  （tau-extend の data.py・ml.py を SHA-256 を照らして読み込む）
    writers = [[rec for _, rec in sorted(by_w[w], key=lambda x: x[0])] for w in sorted(by_w)]
    dt, _ = pinned.ml.load(ds, work, seed)
    bad = 0
    if len(dt) != len(writers):
        bad = max(len(dt), len(writers))
    else:
        for a, b in zip(dt, writers):
            if len(a) != len(b):
                bad += max(len(a), len(b))
                continue
            for ua, ub in zip(a, b):
                same = len(ua["seqs"]) == len(ub["o"]) and all(
                    np.array_equal(np.asarray(x, dtype=np.int64), np.asarray(y, dtype=np.int64)) for x, y in zip(ua["seqs"], ub["o"]))
                bad += int(not same)
    G["dt_order_mismatched_units"] = bad
    G["writers"] = len(writers)
    G["passed"] = G["units"] > 0 and all(G[k] == 0 for k in ("rows_mismatched", "units_split_mismatched", "units_without_raw",
                                                               "dt_order_mismatched_units"))
    if G["passed"]:
        with gzip.open(out, "wt", encoding="utf-8") as f:
            json.dump(dict(dataset=ds, writers=writers), f, separators=(",", ":"))
    prev = json.load(open(gate)) if os.path.exists(gate) else {}
    prev[ds] = G
    json.dump(prev, open(gate, "w"), indent=1)
    print(json.dumps({ds: G}))
    sys.exit(0 if G["passed"] else 3)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "coauthor":
        coauthor_main(a[1], a[2], int(a[3]), a[4], a[5], a[6:])
    else:
        cs1_main(a[1], a[2], a[3], int(a[4]), a[5], a[6])
