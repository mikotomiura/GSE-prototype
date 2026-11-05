"""DUX・SWELL-KW を 1 セッションずつ変換 → replay → add_feat → replay --features し、解析が読む項目だけを残す（E3・E4）。

使い方:
  python3 -I build_extend.py dux   <gse-replay> <holdout.json> <work_dir> <jobs> <v0.csv> <v1.csv> [--tab-as-nav]
  python3 -I build_extend.py swell <gse-replay> <holdout.json> <work_dir> <jobs> <raw_dir>
出力（repo の外）: <work_dir>/<番号>.json（keys・feat・onsets・observed_intervals・clicks・moves・focus・writer・cond・stats）
と build_summary.json（件数だけ）。中間の NDJSON と replay の出力は 1 本ごとに消す。
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import convert_extend as cx  # noqa: E402

ADD_FEAT = os.path.join(HERE, "../../20261031-coauthor-pre-request-signal/scripts/add_feat.py")
REPLAY_SHA = "26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3"
SW_NAME = re.compile(r"^a_pp(\d+)_c(\d)")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def replay_one(keys, side, meta, replay, out):
    if len(keys) < 2:
        return {"status": "few_presses"}
    with tempfile.TemporaryDirectory(dir=os.path.dirname(out)) as td:
        nd = os.path.join(td, "s.ndjson")
        cx.write_ndjson(keys, nd)
        feat_p = os.path.join(td, "feat.json")
        with open(feat_p, "w") as f:
            r = subprocess.run([replay, nd], stdout=f, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        if r.returncode != 0:
            return {"status": "replay_failed"}
        wf = os.path.join(td, "withfeat.ndjson")
        subprocess.run([sys.executable, "-I", ADD_FEAT, nd, feat_p, wf], check=True)
        ft = subprocess.run([replay, wf, "--features"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL)
        if ft.returncode != 0:
            return {"status": "features_failed"}
        feat = json.load(open(feat_p))
        d = json.loads(ft.stdout)
    onsets = [[x["stall_onset"]["s_ms"], x["stall_onset"]["t0_ms"], x["stall_onset"]["theta_person_ms"],
               x["stall_onset"]["theta_sample_n"]] for x in d["rows"] if x["stall_onset"].get("is_onset")]
    rec = dict(meta, keys=[[k[0], k[2]] for k in keys],
               feat=[[x["timestamp"], x["p_stuck"], x["ewma_x"]] for x in feat],
               onsets=onsets,
               observed_intervals=[[iv["a_ms"], iv["b_ms"]] for iv in d["provenance"]["observed_intervals"]],
               clicks=side["clicks"], moves=side["moves"], focus=side["focus"],
               replay_stderr_bytes=len(r.stderr) + len(ft.stderr))
    with open(out + ".tmp", "w") as f:
        json.dump(rec, f, separators=(",", ":"))
    os.replace(out + ".tmp", out)
    return {"status": "ok", "onsets": len(onsets)}


def dux_task(args):
    rows, sid, idx, replay, work, tab_as_nav = args
    keys, side, st = cx.dux_session(rows, tab_as_nav)
    res = replay_one(keys, side, {"writer": sid, "cond": None, "stats": st}, replay,
                     os.path.join(work, "%05d.json" % idx))
    res["stats"] = st
    return res


def swell_task(args):
    path, pp, cond, idx, replay, work = args
    keys, side, st = cx.swell_file(path)
    if not keys:
        return {"status": "no_presses", "cond": cond}
    if st["subsecond_presses"] == 0:  # 全押下がちょうどの秒（一部だけ粗いファイルは通る）
        return {"status": "coarse_ts", "cond": cond}
    res = replay_one(keys, side, {"writer": "pp%d" % pp, "cond": cond, "stats": st}, replay,
                     os.path.join(work, "%05d.json" % idx))
    res["stats"] = st
    return res


def main():
    argv = sys.argv[1:]
    kind, replay, hold_p, work, jobs = argv[:5]
    rest = argv[5:]
    if sha256(replay) != REPLAY_SHA:
        sys.exit("gse-replay の SHA-256 が違う")
    hold = json.load(open(hold_p))
    os.makedirs(work, exist_ok=True)
    if any(n.endswith(".json") for n in os.listdir(work)):
        sys.exit("work_dir に前の中間がある。空の場所で作り直す")
    status, agg, excl_cond = Counter(), Counter(), Counter()
    if kind == "dux":
        tab_as_nav = "--tab-as-nav" in rest
        paths = [p for p in rest if not p.startswith("--")]
        sess, held_rows = cx.dux_read(paths, set(hold["dux"]))
        tasks = [(sess[s], s, i, replay, work, tab_as_nav) for i, s in enumerate(sorted(sess))]
        fn = dux_task
        extra = {"sessions": len(sess), "held_rows_skipped": held_rows, "tab_as_nav": tab_as_nav,
                 "inputs_sha256": [sha256(p) for p in paths]}
    elif kind == "swell":
        raw = rest[0]
        names = sorted(n for n in os.listdir(raw) if n.endswith(".xml"))
        tasks, held = [], 0
        for i, n in enumerate(names):
            m = SW_NAME.match(n)
            pp, cond = int(m.group(1)), "c" + m.group(2)
            if pp in hold["swell"]:
                held += 1
                continue
            tasks.append((os.path.join(raw, n), pp, cond, i, replay, work))
        fn = swell_task
        cat = hashlib.sha256()
        for n in names:
            cat.update(n.encode())
            cat.update(sha256(os.path.join(raw, n)).encode())
        extra = {"files": len(names), "held_files_skipped": held, "inputs_digest": cat.hexdigest()}
    else:
        sys.exit("kind は dux か swell")
    with ProcessPoolExecutor(int(jobs)) as ex:
        for res in ex.map(fn, tasks):
            status[res["status"]] += 1
            if res["status"] == "ok":  # 外した単位の数は足さない（レビューの後に改めた）
                for k, v in res["stats"].items():
                    agg[k] += v
            elif "cond" in res:
                excl_cond["%s|%s" % (res["status"], res["cond"])] += 1
    summ = dict(extra, attempted=len(tasks), status=status, stats_sum_ok=agg, excluded_by_condition=excl_cond,
                replay_sha256=sha256(replay), holdout_sha256=sha256(hold_p), add_feat_sha256=sha256(ADD_FEAT),
                converter_sha256=sha256(os.path.join(HERE, "convert_extend.py")),
                build_sha256=sha256(os.path.abspath(__file__)))
    json.dump(summ, open(os.path.join(work, "build_summary.json"), "w"), indent=1)
    print(json.dumps(summ))
    if status["replay_failed"] or status["features_failed"]:
        sys.exit("失敗したセッションがある")
    with open(os.path.join(work, "build_ok"), "w") as f:  # 成功の印（run.sh が見る）
        f.write("ok\n")


if __name__ == "__main__":
    main()
