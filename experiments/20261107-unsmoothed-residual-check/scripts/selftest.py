"""この試験で足す陽性対照（合成のデータだけ・conditions V2）。tau-extend から引き継ぐ対照は tau-extend の ml.py --selftest を
そのまま回す（run.sh）。

使い方: python3 -I selftest.py <seed> <out.json> [--mutate mX] [--only NAME,...] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を「赤」と読む）。例外は Python の既定（1）。
判定の数（0.02・0.97〜1.03・0.1）は合成の配管の門で、実データの読みの区切りではない。
kit の変異（m41・m42）は kit を一時の dir に写し、1 か所を書き換えた写しで kit_probe.py を回す（公開の kit に切り替えを置かない）。
"""
import json
import math
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinned  # noqa: E402
from pinned import DT, H, ml  # noqa: E402
import build_variants as BV  # noqa: E402
import fit as F  # noqa: E402
import load as L  # noqa: E402
import residual as R  # noqa: E402

NAMES = ["P-KIT", "P-RAW", "P-U", "P-THIN", "P-RES-CAL", "P-RES-MIS", "P-CRN", "P-NPZ", "P-SAME", "P-PIN"]
KIT = BV.KIT
# kit の変異: (ファイル, 変える前, 変えた後)。変える前の文字列がちょうど 1 回現れなければ変異は当たらない（例外 = 1 で終わる）
KIT_MUT = {
    "m41": ("variants.py", "x_raw, y_raw = sym.last_raw", "x_raw, y_raw = r[1], r[2]"),
    "m42": ("variants.py", "    if o == c[\"backspace_run_symbol\"]:\n        return o\n", ""),
}


def set_mut(mut):
    for mod in (F, R, BV):
        mod.MUT.clear()
        mod.MUT.update(mut)
    ml.set_mut([])


# ---------------------------------------------------------------- kit（P-KIT・P-RAW・P-U）
def p_kit():
    r = subprocess.run([sys.executable, "-I", os.path.join(KIT, "selftest.py")], capture_output=True, text=True)
    return dict(passed=r.returncode == 0, returncode=r.returncode, tail=r.stdout[-300:])


def kit_rows(mut):
    """kit_probe.py を回した出力。m41・m42 は書き換えた写しの kit で回す。"""
    with tempfile.TemporaryDirectory() as td:
        kit = KIT
        for m in mut:
            if m in KIT_MUT:
                kit = os.path.join(td, "kit")
                shutil.copytree(KIT, kit, ignore=shutil.ignore_patterns("__pycache__"))
                fn, a, b = KIT_MUT[m]
                p = os.path.join(kit, fn)
                s = open(p, encoding="utf-8").read()
                if s.count(a) != 1:
                    raise RuntimeError("変異 %s が当たらない（%d 回）" % (m, s.count(a)))
                open(p, "w", encoding="utf-8").write(s.replace(a, b))
        out = os.path.join(td, "rows.json")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "kit_probe.py"), kit, out], check=True)
        return json.load(open(out))


def p_raw(K):
    """x_raw・y_raw と前の行の x・y と alpha から平滑を計算し直すと、x・y と bit まで一致する（全行）。"""
    c = K["constants"]
    rows, bad = 0, 0
    for case in K["cases"]:
        px, py = c["smoothing_initial"]["x"], c["smoothing_initial"]["y"]
        for t, o, u, xr, yr, x, y, alpha, path in case:
            xr, yr, x, y = (float.fromhex(v) for v in (xr, yr, x, y))
            if path == "typing":
                ex = c["typing_alpha"] * xr + c["typing_keep"] * px
                ey = c["typing_alpha"] * yr + c["typing_keep"] * py
            else:
                ex = alpha * xr + (1.0 - alpha) * px
                ey = alpha * yr + (1.0 - alpha) * py
            rows += 1
            bad += int(ex.hex() != x.hex() or ey.hex() != y.hex())
            px, py = x, y
    return dict(passed=rows > 0 and bad == 0, rows=rows, mismatched=bad)


def band(v, g=5):
    return min(max(math.floor(v * g), 0), g - 1)


def p_u(K):
    """全行で u = grid(x_raw, y_raw)、o が 25 の行は u も 25。境界（i / 5）・負・1 以上で式どおり。"""
    rows, bad, run_rows = 0, 0, 0
    for case in K["cases"]:
        for t, o, u, xr, yr, *_ in case:
            exp = 25 if o == 25 else band(float.fromhex(xr)) * 5 + band(float.fromhex(yr))
            rows += 1
            run_rows += int(o == 25)
            bad += int(u != exp)
    ebad = sum(int(u != (25 if o == 25 else band(x) * 5 + band(y))) for o, x, y, u in K["edges"])
    return dict(passed=rows > 0 and run_rows > 0 and bad == 0 and ebad == 0, rows=rows, run_rows=run_rows,
                mismatched=bad, edge_cases=len(K["edges"]), edge_mismatched=ebad)


# ---------------------------------------------------------------- P-THIN
def p_thin(seed):
    """n の行の時刻がすべて s + 30,000 · j（j ≥ 1）、該当する行はすべて採る、系列をまたがない、採った行の pflag が元の行の pflag。"""
    rng = np.random.default_rng([seed, 43])
    series = []
    for s0, n in ((5_000, 400), (1_000_500, 300), (7_777_000, 25)):
        t = s0 + 1000 * np.arange(n)
        drop = rng.choice(np.arange(1, n), size=n // 10, replace=False)
        drop = np.union1d(drop, np.array([j for j in range(1, n) if (t[j] - s0) == 60_000], dtype=np.int64)).astype(np.int64)
        # ↑ s + 60 秒の行を落とす（その j を飛ばす）
        series.append([int(x) for x in np.delete(t, drop)])
    marks = BV.n_marks(series)
    ok_time, complete, kept = True, True, 0
    for ts, m in zip(series, marks):
        s = ts[0]
        for t, b in zip(ts, m):
            hit = t > s and (t - s) % 30_000 == 0
            ok_time = ok_time and (not b or hit)
            complete = complete and (b == hit)
            kept += int(b)
    # pflag が行といっしょに動く（load.apply_column）
    seqs = [rng.integers(0, 26, len(ts)) for ts in series]
    pfs = [rng.random(len(ts)) < 0.5 for ts in series]
    writers = [[dict(seqs=[s.copy() for s in seqs], pflag=[p.copy() for p in pfs])]]
    side = dict(writers=[[dict(o=[s.tolist() for s in seqs], u=[((s + 1) % 26).tolist() for s in seqs],
                              n=[[int(b) for b in m] for m in marks])]])
    got = L.apply_column(writers, side, "n")[0][0]
    exp_pf = [p[np.asarray(m, dtype=bool)] for p, m in zip(pfs, marks)]
    exp_sq = [((s + 1) % 26)[np.asarray(m, dtype=bool)] for s, m in zip(seqs, marks)]
    exp_pf = [p for p, s in zip(exp_pf, exp_sq) if len(s)]
    exp_sq = [s for s in exp_sq if len(s)]
    pf_ok = len(got["pflag"]) == len(exp_pf) and all(np.array_equal(a, b) for a, b in zip(got["pflag"], exp_pf))
    sq_ok = len(got["seqs"]) == len(exp_sq) and all(np.array_equal(a, b) for a, b in zip(got["seqs"], exp_sq))
    return dict(passed=bool(ok_time and complete and kept > 0 and pf_ok and sq_ok), times_ok=bool(ok_time),
                complete=bool(complete), kept_rows=kept, pflag_ok=bool(pf_ok), symbols_ok=bool(sq_ok))


# ---------------------------------------------------------------- 残差（P-RES-CAL・P-RES-MIS・P-CRN）
def res_model():
    """既知の AR(1)-HMM（K = 2）。依存は x の帯だけに置き（状態ごとに x の帯の 1 次の遷移が違う）、y の帯は独立で
    状態に依らない（y の帯の分布 qy）。25 は確率 0.02 で独立に出る。P-RES-MIS は x の軸で見る（判断 7）。"""
    K, G = 2, 5
    qy = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
    lo = np.array([0.5, 0.25, 0.15, 0.07, 0.03])
    Qx = np.zeros((K, G, G))
    for b in range(G):
        stay = np.zeros(G)
        stay[b] = 1
        Qx[0, b] = 0.6 * stay + 0.4 * lo
        Qx[1, b] = 0.6 * stay + 0.4 * lo[::-1]
    p25 = 0.02
    C = np.zeros((K, 26, 26))
    Hh = np.zeros((K, 26))
    for k in range(K):
        for prev in range(26):
            pb = prev // G if prev < 25 else 2
            C[k, prev, :25] = (1 - p25) * np.outer(Qx[k, pb], qy).ravel()
            C[k, prev, 25] = p25
        Hh[k, :25] = (1 - p25) * np.outer(np.full(G, 1 / G), qy).ravel()
        Hh[k, 25] = p25
    return dict(kind="ar", pi=np.array([0.5, 0.5]), A=np.array([[0.8, 0.2], [0.2, 0.8]]), H=Hh, C=C)


def sample_fast(m, L_, rng):
    K = len(m["pi"])
    cA, cH, cC = np.cumsum(m["A"], 1), np.cumsum(m["H"], 1), np.cumsum(m["C"], 2)
    u = rng.random((L_, 2))
    z = int(np.searchsorted(np.cumsum(m["pi"]), u[0, 0], side="right"))
    s = np.empty(L_, dtype=np.int64)
    s[0] = min(int(np.searchsorted(cH[z], u[0, 1], side="right")), 25)
    for t in range(1, L_):
        z = min(int(np.searchsorted(cA[z], u[t, 0], side="right")), K - 1)
        s[t] = min(int(np.searchsorted(cC[z, s[t - 1]], u[t, 1], side="right")), 25)
    return s


def r0_model(seqs):
    p, _, _ = H.r0_r1(seqs)
    return dict(kind="hmm", pi=np.ones(1), A=np.ones((1, 1)), B=p[None, :].copy())


def p_res(seed):
    """P-RES-CAL・P-RES-MIS（同じ模擬の列: 書き手 20 人 × 20,000 記号・1 人 4 系列）。"""
    rng = np.random.default_rng([seed, 45])
    m = res_model()
    per_true, per_r0 = [], []
    zs = {"x": [], "y": []}
    for w in range(20):
        seqs = [sample_fast(m, 5000, rng) for _ in range(4)]
        units = [dict(seqs=[s], pflag=[np.ones(len(s), dtype=bool)]) for s in seqs]
        E = R.EvalSeq(units)
        st = R.writer_residuals(E, [("true", ("model", m)), ("r0", ("model", r0_model(seqs)))], seed, 0, w, 0, debug=True)
        per_true.append(st["true"])
        per_r0.append(st["r0"])
        for j, ax in enumerate(("x", "y")):
            z = st["true"]["_z"][j]
            zs[ax].append(z[~np.isnan(z)])
    cal = {}
    ok = True
    for ax in ("x", "y"):
        z = np.concatenate(zs[ax])
        mean, var = float(z.mean()), float(z.var())
        lagmed = {l: float(np.median([abs(p["acf_" + ax][str(l)]) for p in per_true])) for l in R.LAGS}
        cal[ax] = dict(mean=mean, var=var, max_lag_median_abs=max(lagmed.values()))
        ok = ok and abs(mean) < 0.02 and 0.97 <= var <= 1.03 and max(lagmed.values()) < 0.02
    r1_true = float(np.median([p["acf_x"]["1"] for p in per_true]))
    r1_r0 = float(np.median([p["acf_x"]["1"] for p in per_r0]))
    mis = dict(passed=bool(r1_r0 - r1_true >= 0.1), r1_true_median=r1_true, r1_r0_median=r1_r0,
               r1_r0_median_y=float(np.median([p["acf_y"]["1"] for p in per_r0])))
    return dict(passed=bool(ok), **cal), mis


def p_crn(seed):
    """同じ書き手・列・時刻で、モデルが違っても v が同じ。列が違えば v の流れが違う。"""
    rng = np.random.default_rng([seed, 48])
    m = res_model()
    seqs = [sample_fast(m, 400, rng) for _ in range(3)]
    units = [dict(seqs=[s], pflag=[np.ones(len(s), dtype=bool)]) for s in seqs]
    E = R.EvalSeq(units)
    models = [("true", ("model", m)), ("r0", ("model", r0_model(seqs))), ("r1", ("r1", H.r0_r1(seqs)[1:]))]
    a = R.writer_residuals(E, models, seed, 1, 7, 0, debug=True)
    b = R.writer_residuals(E, models[:1], seed, 1, 7, 1, debug=True)
    same = all(np.array_equal(a["true"]["_v"], a[n]["_v"]) for n in ("r0", "r1"))
    differ_col = not np.array_equal(a["true"]["_v"], b["true"]["_v"])
    again = R.writer_residuals(E, models[:1], seed, 1, 7, 0, debug=True)
    repeat = np.array_equal(a["true"]["_v"], again["true"]["_v"])
    return dict(passed=bool(same and differ_col and repeat), same_across_models=bool(same), differ_across_columns=bool(differ_col),
                repeatable=bool(repeat))


# ---------------------------------------------------------------- 当てはめ（P-NPZ・P-SAME）
def synth(seed, tag, n_w, n_u, L_):
    rng = np.random.default_rng([seed, tag])
    cm = H.random_model("hmm", 3, rng)
    cm["A"] = 0.9 * np.eye(3) + 0.1 * cm["A"]
    writers = []
    for _ in range(n_w):
        writers.append([dict(start=0, seqs=[s], pflag=[rng.random(len(s)) < 0.7], probes=[], probes_all=[])
                        for s in H.sample(cm, [L_] * n_u, rng)])
    pool = H.sample(cm, [400] * 10, rng)
    _, hp, Tp = H.r0_r1(pool)
    Dp = H.Data(pool, chunk=H.CHUNK)
    pools = {}
    for s in ml.STRUCTS:
        m = H.random_model(s[0], s[1], rng, r1=Tp, r0=hp)
        S, _ = H.counts(m, Dp)
        pools[ml.sname(s)] = (m, H.sbar_of(S, Dp.nobs))
    return writers, pools


def p_npz(seed):
    """npz から読み戻した母数で計算した評価の尤度が、当てはめの段の中の値とちょうど一致する（全構造・全 τ・共通・r1）。"""
    writers, pools = synth(seed, 49, 2, 7, 200)
    Hh, ks_all, ks_make = 5, [1, 2], [1, 2]
    cells, bad = 0, 0
    with tempfile.TemporaryDirectory() as td:
        flat, outs = {}, []
        for w, units in enumerate(writers):
            res, par = F.fit_writer(units, Hh, ks_all, ks_make, pools, np.random.default_rng([seed + 10, w]))
            outs.append(res)
            flat.update(F.flat_params(w, par))
        p = os.path.join(td, "p.npz")
        np.savez_compressed(p, **flat)
        with np.load(p) as z:  # 閉じてから一時フォルダを抜ける（Windows は開いたままのファイルを消せない）
            for w, units in enumerate(writers):
                _, test = DT.split(len(units), 1, Hh)
                ev = ml.Eval(ml.seqs_of([units[i] for i in test]), ml.pflags_of([units[i] for i in test]))
                res = outs[w]
                for s in ml.STRUCTS:
                    nm = ml.sname(s)
                    cells += 1
                    bad += int(ev.ll(F.get_pool(z, w, nm)) != res["pool"][nm])
                    for k in map(str, ks_make):
                        for t in ml.TAU_KEYS:
                            cells += 1
                            bad += int(ev.ll(F.get_self(z, w, nm, k, t)) != res["k"][k]["self"][nm][t])
                for k in map(str, ks_make):
                    cells += 1
                    bad += int(ev.ll_r1(*F.get_r1(z, w, k)) != res["k"][k]["r1"])
    return dict(passed=cells > 0 and bad == 0, cells=cells, mismatched=bad)


def p_same(seed):
    """合成の書き手 3 人で、作る k の本人（全 τ）・共通・r1・診断が tau-extend の em_writer（別のプロセス）とちょうど一致する。
    作らない k（2・3）・作る k の折り目（k = 5）・外した構造の乱数を捨てる番を含む。"""
    writers, pools = synth(seed, 50, 3, 11, 160)
    Hh, ks_all, ks_make = 5, [1, 2, 3, 5], [1, 5]
    mine = [F.fit_writer(u, Hh, ks_all, ks_make, pools, np.random.default_rng([seed + 10, w]))[0] for w, u in enumerate(writers)]
    with tempfile.TemporaryDirectory() as td:
        pin, pout = os.path.join(td, "in.pkl"), os.path.join(td, "out.pkl")
        pickle.dump(dict(writers=writers, pools=pools, seed=seed, H=Hh, ks=ks_all), open(pin, "wb"))
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "same_ref.py"), pin, pout],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return dict(passed=False, note="tau-extend のコードが走らない", stderr=r.stderr[-2000:])
        ref = pickle.load(open(pout, "rb"))
    ref_dir_ok = os.path.realpath(os.path.dirname(ref["ml_file"])) == pinned.TAU
    cells, diff = 0, 0
    for a, b in zip(mine, ref["results"]):
        for s in ml.STRUCTS:
            nm = ml.sname(s)
            cells += 1
            diff += int(a["pool"][nm] != b["pool"][nm])
        for k in map(str, ks_make):
            ka, kb = a["k"][k], b["k"][k]
            cells += 2
            diff += int(ka["r1"] != kb["r1"]) + int(ka["n_train"] != kb["n_train"])
            for s in ml.STRUCTS:
                nm = ml.sname(s)
                cells += 2
                diff += int(ka["self"][nm] != kb["self"][nm]) + int(ka["diag"][nm] != kb["diag"][nm])
        cells += 1
        diff += int(a["n_eval"] != b["n_eval"])
    folds = all(b["k"]["5"]["fold"]["ar2"] is not None for b in ref["results"])
    return dict(passed=bool(diff == 0 and cells > 0 and folds and ref_dir_ok), cells=cells, differing=diff,
                ref_has_folds=bool(folds), ref_from_tau_extend=bool(ref_dir_ok))


# ---------------------------------------------------------------- P-PIN
def p_pin(mut):
    """読み込んだファイルの SHA-256 が条件の値なら通り、1 バイト変えた写しを読めば止まる（陰性対照）。m51 は写しを本物として読む。"""
    def probe(tau):
        env = dict(os.environ, TAU_SCRIPTS=tau)
        return subprocess.run([sys.executable, "-I", os.path.join(HERE, "pin_probe.py")], env=env, capture_output=True).returncode
    with tempfile.TemporaryDirectory() as td:
        bad = os.path.join(td, "scripts")
        shutil.copytree(pinned.TAU, bad, ignore=shutil.ignore_patterns("__pycache__"))
        with open(os.path.join(bad, "hmm2.py"), "ab") as f:
            f.write(b"\n")  # 1 バイト足す（数式は変わらない・ハッシュだけが変わる）
        real = probe(bad if "m51" in mut else pinned.TAU)
        neg = probe(bad)
    return dict(passed=real == 0 and neg == 4, real_returncode=real, modified_copy_returncode=neg)


# ---------------------------------------------------------------- 入口
def main(seed, out, only, mut, run_id):
    set_mut(mut)
    t0 = time.time()
    want = set(only) if only else set(NAMES)
    Rr = dict(run_id=run_id, mutate=mut)
    if "P-KIT" in want:
        Rr["P-KIT"] = p_kit()
    if want & {"P-RAW", "P-U"}:
        K = kit_rows(mut)
        if "P-RAW" in want:
            Rr["P-RAW"] = p_raw(K)
        if "P-U" in want:
            Rr["P-U"] = p_u(K)
    if "P-THIN" in want:
        Rr["P-THIN"] = p_thin(seed)
    if want & {"P-RES-CAL", "P-RES-MIS"}:
        cal, mis = p_res(seed)
        if "P-RES-CAL" in want:
            Rr["P-RES-CAL"] = cal
        if "P-RES-MIS" in want:
            Rr["P-RES-MIS"] = mis
    if "P-CRN" in want:
        Rr["P-CRN"] = p_crn(seed)
    if "P-NPZ" in want:
        Rr["P-NPZ"] = p_npz(seed)
    if "P-SAME" in want:
        Rr["P-SAME"] = p_same(seed)
    if "P-PIN" in want:
        Rr["P-PIN"] = p_pin(mut)
    Rr["seconds"] = time.time() - t0
    Rr["all_passed"] = all(Rr[n]["passed"] for n in NAMES if n in Rr)
    json.dump(Rr, open(out, "w"), indent=1, default=float)
    print(json.dumps({n: Rr[n]["passed"] for n in NAMES if n in Rr}))
    return 0 if Rr["all_passed"] else 3


if __name__ == "__main__":
    argv = sys.argv[1:]
    mut, only, run_id = [], None, None
    while "--mutate" in argv:
        i = argv.index("--mutate")
        mut.append(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if "--only" in argv:
        i = argv.index("--only")
        only = argv[i + 1].split(",")
        argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id")
        run_id = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    sys.exit(main(int(argv[0]), argv[1], only, sorted(mut), run_id))
