"""本計算（conditions.md D3・D4・D8）。複製ごとに生成 → 各セルの 3 案の W・p と記述の量・G_v を保存する。

使い方:
  python3 -I run_eye.py <select|report> <out_dir> <jobs> --null <1|2> [--npz PATH] [--run-id ID] [--budget-hours 24]
出力: <out_dir>/<組>/<群>.jsonl（1 行 = 1 複製・合成の値だけ）と <out_dir>/<組>/plan_null<n>.json（時間の見積もり）。
このスクリプトは複製の値を要約も表示もしない（D8: 時間だけを見る）。例外が出たら全体を止める。
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import gen as GN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SHAPE_NO = dict(coauthor=0, cs1=1)
CELLS = dict(coauthor=[(1, 0), (5, 0), (15, 0), (5, 5), (5, 10)], cs1=[(1, 0), (5, 0), (1, 1), (1, 4)])
MAIN = (5, 0)
CORE = ("eye.py", "gen.py", "run_eye.py", "selftest.py")   # 複製を作る中核（集計・D5・D9 は provenance で別に照らす）


def code_hash():
    h = hashlib.sha256()
    for f in CORE:
        h.update(f.encode() + open(os.path.join(HERE, f), "rb").read())
    for p, v in sorted(GN.PIN1.items()):
        h.update((os.path.relpath(p, GN.EXP).replace(os.sep, "/") + v).encode())   # 区切りを / に揃え、機械によらず同じ値にする（判断 40）
    return h.hexdigest()


# ---------------------------------------------------------------- 複製の一覧（D4 の表）
def plan(which):
    rows = []
    z = range(10000, 11000) if which == "select" else range(12000, 13000)   # v2: 種 10000 以上（v1 の D8）
    s = range(10000, 10500) if which == "select" else range(12000, 12500)

    def add(null, strand, shape, step, seeds):
        rows.extend(dict(null=null, strand=strand, shape=shape, step=step, seed=x) for x in seeds)

    if which == "select":
        add(1, "dose", "coauthor", 0.0, z)
        for g in GN.DOSE:
            add(1, "dose", "coauthor", g, s)
        add(1, "dist", "coauthor", 3e-2, s)
        for st in ("struct", "wobble", "drift", "volume", "stack"):
            add(1, st, "coauthor", 0.0, z)
        add(2, "dose", "coauthor", 0.0, z)
        add(2, "dose", "coauthor", 3e-2, s)
    else:
        for shape in ("coauthor", "cs1"):
            add(1, "dose", shape, 0.0, z)
            for g in GN.DOSE:
                add(1, "dose", shape, g, s)
        add(1, "dist", "coauthor", 3e-2, s)
        add(1, "struct", "coauthor", 0.0, z)
        add(1, "struct", "coauthor", 1e-2, s)
        add(1, "wobble", "coauthor", 0.0, z)
        add(1, "wobble", "coauthor", 1e-2, s)
        add(1, "wobble", "coauthor", 3e-2, s)
        add(1, "wobble", "cs1", 0.0, z)
        for shape in ("coauthor", "cs1"):
            add(1, "drift", shape, 0.0, z)
            add(1, "drift", shape, 0.5, s)
            add(1, "drift", shape, 0.9, s)
        for shape in ("coauthor", "cs1"):
            add(1, "volume", shape, 0.0, z)
            add(1, "stack", shape, 0.0, z)
        add(2, "dose", "coauthor", 0.0, z)
        for g in GN.DOSE:
            add(2, "dose", "coauthor", g, s)
    return rows


def group(r):
    return "null%d_%s_%s_%s" % (r["null"], r["strand"], r["shape"], repr(r["step"]))


def cells_of(which, shape):
    return [MAIN] if which == "select" else CELLS[shape]


# ---------------------------------------------------------------- ワーカー
_CTX = {}


def _init(npz):
    GN.assert_clean()
    if EY.MUT or GN.MUT:
        raise RuntimeError("本計算に変異が入っている")
    _CTX["second"] = GN.load_second(npz) if npz else None


def rep(a):
    r, which = a
    t0 = time.time()
    w, P = GN.make(r, second=_CTX["second"] if r["null"] == 2 else None)
    t1 = time.time()
    sh = GN.SY.SHAPES[r["shape"]]
    UC = EY.count_writers(w, GN.NSYM)
    out = dict(seed=r["seed"], cells={})
    for k, g in cells_of(which, r["shape"]):
        rng = np.random.default_rng([GN.SEED, r["null"], GN.STRAND[r["strand"]], SHAPE_NO[r["shape"]], k, g, r["seed"]])
        perms = EY.draw_perms(rng, P)
        key = EY.eq_key(GN.SEED, r["null"], GN.STRAND[r["strand"]], SHAPE_NO[r["shape"]], k, g, r["seed"])
        out["cells"]["k%d_g%d" % (k, g)] = EY.eval_cell(UC, P, sh["H"], k, g, perms, key)
    if r["strand"] == "dist":
        lam = GN.lam_first(3, r["step"])
        out["planted"] = [bool(GN.SY.lam_rule("dist", lam)(i) > 0) for i in range(P)]
    out["sec"] = dict(gen=t1 - t0, eye=time.time() - t1)
    return out


# ---------------------------------------------------------------- 本体
def done_seeds(path, ch):
    got = set()
    if os.path.exists(path):
        for line in open(path):
            d = json.loads(line)
            if d.get("code_hash") != ch:
                sys.exit("%s にコードのハッシュが違う行がある（消してからやり直す）" % path)
            got.add(d["seed"])
    return got


def main():
    argv = sys.argv[1:]
    opt = {}
    for key in ("--null", "--npz", "--run-id", "--budget-hours"):
        if key in argv:
            i = argv.index(key)
            opt[key] = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
    which, out, jobs = argv[0], argv[1], int(argv[2])
    null = int(opt["--null"])
    npz = opt.get("--npz")
    if which not in ("select", "report") or null not in (1, 2) or (null == 2) != (npz is not None):
        sys.exit("引数が違う（第 2 の帰無だけ --npz を渡す）")
    budget = float(opt.get("--budget-hours", "24"))
    run_id = opt.get("--run-id")
    ch = code_hash()
    GN.assert_clean()
    d = os.path.join(out, which)
    os.makedirs(d, exist_ok=True)
    rows = [r for r in plan(which) if r["null"] == null]
    groups = {}
    for r in rows:
        groups.setdefault(group(r), []).append(r)
    t0 = time.time()
    with ProcessPoolExecutor(jobs, initializer=_init, initargs=(npz,)) as ex:
        def run_rows(gname, rs):
            path = os.path.join(d, gname + ".jsonl")
            have = done_seeds(path, ch)
            todo = [r for r in rs if r["seed"] not in have]
            secs = []
            with open(path, "a") as f:
                for r, res in zip(todo, ex.map(rep, [(r, which) for r in todo], chunksize=2)):
                    res.update(run_id=run_id, code_hash=ch, row=r)
                    f.write(json.dumps(res) + "\n")
                    f.flush()
                    secs.append(res["sec"]["gen"] + res["sec"]["eye"])
            return secs

        # D8: 各群の最初の 10 複製で時間を測り、全体を見積もる（並列 jobs の 1 台）
        per = {}
        for gname, rs in groups.items():
            secs = run_rows(gname, rs[:10])
            per[gname] = float(np.mean(secs)) if secs else None
        known = [v for v in per.values() if v is not None]
        fill = max(known) if known else 0.0
        est = sum((per[g] if per[g] is not None else fill) * len(rs) for g, rs in groups.items()) / jobs / 3600
        P = dict(run_id=run_id, which=which, null=null, code_hash=ch, jobs=jobs, budget_hours=budget,
                 per_rep_seconds=per, estimate_hours=est, rows=len(rows))
        json.dump(P, open(os.path.join(d, "plan_null%d.json" % null), "w"), indent=1)
        print("見積もり %.1f 時間（%d 複製・jobs %d）" % (est, len(rows), jobs), flush=True)
        if est > budget:
            sys.exit("見積もりが %.1f 時間で予算 %.0f 時間を超える。回さずに止めて研究者に問う（D8）" % (est, budget))
        for gname, rs in groups.items():
            run_rows(gname, rs)
            print("群 %s 終わり（%.0f 秒）" % (gname, time.time() - t0), flush=True)
    for gname, rs in groups.items():
        have = done_seeds(os.path.join(d, gname + ".jsonl"), ch)
        if have != {r["seed"] for r in rs}:
            sys.exit("群 %s の複製が計画と合わない" % gname)
    P["seconds_total"] = time.time() - t0
    json.dump(P, open(os.path.join(d, "plan_null%d.json" % null), "w"), indent=1)
    print("終わり %.0f 秒" % P["seconds_total"], flush=True)


if __name__ == "__main__":
    main()
