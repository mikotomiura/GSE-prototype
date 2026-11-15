"""合成の対照（設計 v2 §6・conditions.md）。1 組 = 合成の記録 → gse-replay → 画素 → 統計。

S2: 陰性（λ = 0）。S3: 段階をつけた陽性（λ > 0）。組ごとに合成の種を変え、同じ組の中では λ だけを変える
（記録と推定は同じで、描き直しの状態にだけ p_stuck を混ぜる）。中間のファイルは作業のディレクトリに置き、
組が終わったら消す。結果は組ごとの summary を results/controls/ に残す（集計だけ）。

使い方: python controls.py --work DIR --out DIR --sets N --lams 0,0.1,0.2,0.4 [--jobs 4] [--days 20] [--hours 1.5]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} が失敗: {r.stderr[-2000:]}")
    return r


def one_set(job):
    a, k = job["args"], job["set"]
    work = os.path.join(a["work"], f"set{k:03d}")
    os.makedirs(work, exist_ok=True)
    py, rep, tbl = a["python"], a["replay"], a["table_dir"]
    seed = a["seed"] * 1000 + k
    t0 = time.time()
    run([py, "-I", os.path.join(HERE, "synth.py"), "--seed", str(seed), "--days", str(a["days"]),
         "--hours", str(a["hours"]), "--out", os.path.join(work, "rec")])
    recs = sorted(os.path.join(work, "rec", f) for f in os.listdir(os.path.join(work, "rec")))
    timing = {"synth_s": round(time.time() - t0, 1)}
    out = []
    for lam in a["lams"]:
        tag = f"set{k:03d}_lam{lam}"
        w = os.path.join(work, f"w_{lam}.ndjson")
        f = os.path.join(work, f"f_{lam}.bin")
        p = os.path.join(work, f"p_{lam}.ndjson")
        s = time.time()
        with open(w, "w") as fh:
            r = subprocess.run([rep, *recs, "--handmark-windows", "--utc-offset-secs", "32400",
                                "--handmark-table", os.path.join(tbl, "handmark_assignment.json"),
                                "--handmark-table-sha", os.path.join(tbl, "handmark_assignment.sha256"),
                                "--labels", "recomputed", "--samples", str(a["samples"]),
                                "--inject-stuck", str(lam), "--frames", f], stdout=fh, stderr=subprocess.PIPE, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"gse-replay が失敗: {r.stderr[-2000:]}")
        timing[f"replay_s_{lam}"] = round(time.time() - s, 1)
        s = time.time()
        run(["node", os.path.join(HERE, "pixels.mjs"), f, str(a["samples"]), p], cwd=os.path.dirname(HERE))
        timing[f"pixels_s_{lam}"] = round(time.time() - s, 1)
        os.remove(f)
        s = time.time()
        summ = os.path.join(a["out"], f"{tag}.json")
        cmd = [py, "-I", os.path.join(HERE, "stats.py"), w, "--pixels", p, "--seed", str(seed),
               "--R", str(a["R"]), "--out", summ]
        if a["truth"]:
            cmd += ["--truth"]
        if a["R_nested"]:
            cmd += ["--R-nested", str(a["R_nested"])]
        if a["mut"]:
            cmd += ["--mut", a["mut"]]
        run(cmd)
        timing[f"stats_s_{lam}"] = round(time.time() - s, 1)
        with open(summ) as fh:
            res = json.load(fh)
        if a["truth"]:
            out.append({"set": k, "lam": lam, "truth": res["truth"], "n_days": res["n_days"]})
            continue
        out.append({"set": k, "lam": lam, "overall": res.get("overall"),
                    "T1": {b: res["targets"].get("T1", {}).get(b, {}).get("verdict") for b in ("state", "pixel")},
                    "T2": {b: res["targets"].get("T2", {}).get(b, {}).get("verdict") for b in ("state", "pixel")},
                    "ci90": {t: {b: res["targets"].get(t, {}).get(b, {}).get("ci90") for b in ("state", "pixel")}
                             for t in ("T1", "T2")},
                    "auc": {t: res["targets"].get(t, {}).get("auc") for t in ("T1", "T2")},
                    "newton_nonconverged": res.get("newton_nonconverged")})
    shutil.rmtree(work, ignore_errors=True)
    for o in out:
        o["timing"] = timing
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--replay", required=True)
    ap.add_argument("--table-dir", required=True)
    ap.add_argument("--sets", type=int, required=True)
    ap.add_argument("--first-set", type=int, default=0)
    ap.add_argument("--lams", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--days", type=int, default=20)
    ap.add_argument("--hours", type=float, default=1.5)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--R", type=int, default=2000)
    ap.add_argument("--R-nested", type=int, default=0)
    ap.add_argument("--mut", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--truth", action="store_true", help="大きな合成で母集団の差の近似を出す（S5）")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    args = {"work": a.work, "out": a.out, "replay": a.replay, "table_dir": a.table_dir, "python": sys.executable,
            "lams": [float(x) for x in a.lams.split(",")], "seed": a.seed, "days": a.days, "hours": a.hours,
            "samples": a.samples, "R": a.R, "R_nested": a.R_nested, "mut": a.mut, "truth": a.truth}
    jobs = [{"args": args, "set": k} for k in range(a.first_set, a.first_set + a.sets)]
    rows = []
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for res in ex.map(one_set, jobs):
            rows.extend(res)
            for r in res:
                print(json.dumps({k: r[k] for k in ("set", "lam", "overall", "T1", "T2", "truth") if k in r},
                                 ensure_ascii=False), flush=True)
    # 書き終えてから置き換える（途中で止まっても壊れた controls.json を残さない）
    dst = os.path.join(a.out, "controls.json")
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, dst)


if __name__ == "__main__":
    main()
