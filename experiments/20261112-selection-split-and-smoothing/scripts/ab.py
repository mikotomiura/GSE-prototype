"""計算 A（書き手の二分）と B（共通の基の平滑・本人の連鎖の平滑を他人で選ぶ）の選びと集計（conditions.md D2〜D6）。
当てはめは回さない。B の共通の当て直しと r1 の数え直しは compute.py が行い、その値をここで読む。

使い方（HP Z2）: python3 -I ab.py <raw_prefix> <bvals.pkl> <out_dir> [--run-id ID]
  <raw_prefix>: mode の本計算の書き手ごとの値（<raw_prefix>.coauthor.pkl・.cs1.pkl・repo の外・人は開かない）。
  <bvals.pkl>: compute.py が書いた B の値（repo の外・人は開かない）。
出力: <out_dir>/summary.json（集計値だけ）・tables.md。書き手ごとの値・書き手の番号は書かない。
"""
import hashlib
import json
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned4  # noqa: E402
from pinned4 import H, ml  # noqa: E402

MUT = set()  # s1: 二分の選びに報告の半分を混ぜる・s2: 1 人を両方の半分に・s3: τ 他人の候補から ∞ を外す・
#              s5: B1 の τ = ∞ を pool(1) のまま・s6: α の選びに w 自身・s8: 2 段の選びの量を 本人 − 共通 に・
#              s9: B2 の v の r1 に v 自身の β*・s10: B1 の v の共通に v 自身の α*（s4・s7 は compute.py）
SEED = pinned4.SEED
N_SPLITS = 1000
MAIN_PANELS = {"coauthor": ["P15", "P30"], "cs1": ["C5"]}
DS_NO = {"coauthor": 0, "cs1": 1}
PANEL_NO = {"P15": 0, "P30": 1, "C5": 0}
ALPHAS = ["0.03", "0.1", "0.3", "1", "3"]
ALPHA_ORDER = ["1", "3", "0.3", "0.1", "0.03"]          # 同点は 1 倍、次に大きい倍率（D4）
BETAS = ["0.01", "0.03", "0.1", "0.3", "0.5", "1", "2"]
BETA_ORDER = ["0.5", "2", "1", "0.3", "0.1", "0.03", "0.01"]  # 同点は 0.5、次に大きい値（D5）
SN = [ml.sname(s) for s in ml.STRUCTS]
CHECKS = []  # P-CURRENT の結果（main が全部真でなければ止める）


# ---------------------------------------------------------------- 選び（共通）
def pick(values, members, cands):
    """members の中央値がいちばん大きい候補（同点は cands の先）。ml.select_joint / select_other と同じ規則で、
    除く書き手を呼ぶ側が members で渡す。"""
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in members if values[v].get(c) is not None]
        if not xs:
            continue
        m = float(np.median(xs))
        if bv is None or m > bv:
            best, bv = c, m
    return best


def tau_cands():
    c = ml.tau_cands()
    return [t for t in c if t != ml.INF] if "s3" in MUT else c


def region_of(t):
    if t == ml.INF:
        return "inf"
    if t == str(ml.TAUS_FIT[-1]):
        return "high_finite_end"
    if t == "0":
        return "low_end"
    return "inside"


def stats(d, rng):
    return ml.delta_stats(d, rng)


# ---------------------------------------------------------------- A: 書き手の二分
def split_pairs(n, rng, n_splits=N_SPLITS):
    """[(X, Y)]（位置の配列）。X は前の ⌊n/2⌋、Y は残り。s2 は 1 人を両方に入れる。"""
    out = []
    for _ in range(n_splits):
        p = rng.permutation(n)
        h = n // 2
        X = p[:h + 1] if "s2" in MUT else p[:h]
        out.append((np.sort(X), np.sort(p[h:])))
    return out


def argbest(V, rows):
    """V[rows] の列ごとの中央値の最大（同点は前の列・pick と同じ）。"""
    med = np.median(V[rows], axis=0)
    return int(np.argmax(med))


def a_pairs(Vsel, Vreps, pairs):
    """組ごとの (選んだ候補の位置, {報告: h}, {報告: i})。2 つの向き。s1 は選びに報告の半分を混ぜる。"""
    out = []
    for X, Y in pairs:
        for S, R in ((X, Y), (Y, X)):
            Ssel = np.union1d(S, R) if "s1" in MUT else S
            cS, cR = argbest(Vsel, Ssel), argbest(Vsel, R)
            h = {lab: float(np.median(V[R, cS])) for lab, V in Vreps.items()}
            i = {lab: float(np.median(V[R, cR])) for lab, V in Vreps.items()}
            out.append((cS, h, i))
    return out


def a_summary(res, cand_labels):
    """組の要約（書き手ごとの値は出さない）。"""
    out = dict(pairs=len(res))
    for lab in res[0][1]:
        h = np.array([r[1][lab] for r in res])
        i = np.array([r[2][lab] for r in res])
        o = i - h
        out[lab] = {nm: dict(median=float(np.median(x)), mean=float(np.mean(x)),
                             q025=float(np.quantile(x, 0.025)), q975=float(np.quantile(x, 0.975)))
                    for nm, x in (("honest", h), ("insample", i), ("optimism", o))}
        out[lab]["honest_pos_share"] = float(np.mean(h > 0))
        out[lab]["honest_zero_share"] = float(np.mean(h == 0))
    reg, sts = {}, {}
    for r in res:
        lab = cand_labels[r[0]]
        rg = region_of(lab[1] if isinstance(lab, tuple) else lab)
        reg[rg] = reg.get(rg, 0) + 1
        if isinstance(lab, tuple):
            sts[lab[0]] = sts.get(lab[0], 0) + 1
    out["chosen_region_on_select_half"] = reg
    if sts:
        out["chosen_struct_on_select_half"] = sts  # D3「c_S の (構造, τ) の数」（レビュー LOW 7）
    return out


def joint_mats(results, ws, k):
    jc = ml.joint_cands()
    r1 = np.array([[ml.me_of(results, v, k, n, t, 0) - results[v]["em"]["k"][str(k)]["r1"][0] for n, t in jc] for v in ws])
    rp = np.array([[ml.me_of(results, v, k, n, t, 0) - results[v]["em"]["pool"][n][0] for n, t in jc] for v in ws])
    return jc, (rp if "s8" in MUT else r1), {"self_minus_pool": rp, "self_minus_r1": r1}


def loo_median(Vsel, Vrep):
    """w を除く選び（今の手順）で、書き手ごとの報告の量の中央値（mode の q と同じ inverted_cdf）。"""
    n = Vsel.shape[0]
    d = [float(Vrep[i, argbest(Vsel, np.array([j for j in range(n) if j != i]))]) for i in range(n)]
    return ml.q(d)["median"]


def tau_mats(results, ws, k, name):
    tc = tau_cands()
    V = np.array([[(0.0 if t == ml.INF else ml.me_of(results, v, k, name, t, 0) - results[v]["em"]["pool"][name][0])
                   for t in tc] for v in ws])
    return tc, V, {"self_minus_pool": V}


def a_dataset(results, ds, mode_em):
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    S = {}
    for pn in MAIN_PANELS[ds]:
        P = {}
        ws0 = next(iter(members[pn].values()))
        rng = np.random.default_rng([SEED + 20, DS_NO[ds], PANEL_NO[pn]])
        pairs = split_pairs(len(ws0), rng)  # 分け方は同じパネルの k の間で共有する（D3）
        for k, ws in members[pn].items():
            assert ws == ws0
            M = mode_em[pn][str(k)]
            E = dict(writers=len(ws), half_sizes=[len(ws) // 2, len(ws) - len(ws) // 2])
            jc, sel, reps = joint_mats(results, ws, k)
            E["two_stage_other"] = a_summary(a_pairs(sel, reps, pairs), jc)
            cur = M["two_stage"]["other"]["two_stage_other"]["all/self_minus_pool_same"]["median"]
            E["two_stage_other"]["current"] = cur
            # P-CURRENT（実データの門・レビュー MEDIUM 1）: 行列から w を除く選びで作った中央値が mode の値とビットまで同じ
            CHECKS.append(loo_median(sel, reps["self_minus_pool"]) == cur)
            E["structs"] = {}
            for name in SN:
                tc, V, reps = tau_mats(results, ws, k, name)
                E["structs"][name] = a_summary(a_pairs(V, reps, pairs), tc)
                cur = M["structs"][name]["tau_other"]["all/self_minus_pool_same"]["median"]
                E["structs"][name]["current"] = cur
                CHECKS.append(loo_median(V, reps["self_minus_pool"]) == cur)
            P[str(k)] = E
        S[pn] = P
    return S


# ---------------------------------------------------------------- B: α と β の選び
def alpha_star(PV, ws, name):
    """{w: α*}。w を除く v の pool_v(α) − pool_v(1) の中央値（D4）。s6 は w を入れる。"""
    order = [a for a in ALPHA_ORDER if all(a in PV[v][name] for v in ws)]  # 時間の規則で削った α は除く（V2）
    vals = {v: {a: PV[v][name][a][0] - PV[v][name]["1"][0] for a in order} for v in ws}
    return {w: pick(vals, [v for v in ws if v != w or "s6" in MUT], order) for w in ws}


def beta_star(RV, ws, k):
    """{w: β*}。w を除く v の r1_v(β) − r1_v(0.5) の中央値（パネル × k ごと・D5）。"""
    vals = {v: {b: RV[v][str(k)][b][0] - RV[v][str(k)]["0.5"][0] for b in BETAS} for v in ws}
    return {w: pick(vals, [v for v in ws if v != w], BETA_ORDER) for w in ws}


class Ref:
    """書き手ごとの値の参照。astar: {構造名: {w: α}}（None なら共通は mode のまま）・bstar: {w: β}（None なら r1 は mode のまま）。
    τ = ∞ の本人の値は、B1 では pool(α*) に替える（s5 は替えない）。"""

    def __init__(self, results, k, PV=None, astar=None, RV=None, bstar=None):
        self.R, self.k, self.PV, self.a, self.RV, self.b = results, str(k), PV, astar, RV, bstar

    def pool(self, v, name, w):
        if not self.a:
            return self.R[v]["em"]["pool"][name][0]
        return self.PV[v][name][self.a[name][v if "s10" in MUT else w]][0]

    def r1(self, v, w):
        if not self.b:
            return self.R[v]["em"]["k"][self.k]["r1"][0]
        return self.RV[v][self.k][self.b[v if "s9" in MUT else w]][0]

    def me(self, v, name, t, w):
        if t == ml.INF and self.a and "s5" not in MUT:
            return self.pool(v, name, w)
        return ml.me_of(self.R, v, int(self.k), name, t, 0)


def joint_rows(ref, ws, rng):
    """2 段（他人）を ref の値で選び直す。返り値: 要約と選ばれた組。"""
    jc = ml.joint_cands()
    pk, dp, dr = {}, [], []
    for w in ws:
        vals = {v: {(n, t): ref.me(v, n, t, w) - ref.r1(v, w) for n, t in jc} for v in ws}
        c = ml.select_joint(vals, w, jc)
        pk[w] = c
        me = ref.me(w, c[0], c[1], w)
        dp.append(me - ref.pool(w, c[0], w))
        dr.append(me - ref.r1(w, w))
    return dict(self_minus_pool=stats(dp, rng), self_minus_r1=stats(dr, rng),
                chosen_struct=ml.count_vals(c[0] for c in pk.values()),
                chosen_tau_region=ml.tau_region(c[1] for c in pk.values())), pk, dp


def tau_rows(ref, ws, name, rng):
    """τ 他人（構造ごと）を ref の共通で選び直す（τ = ∞ は 0）。"""
    tc = ml.tau_cands()
    d, pk = [], {}
    for w in ws:
        vals = {v: {t: (0.0 if t == ml.INF else ref.me(v, name, t, w) - ref.pool(v, name, w)) for t in tc} for v in ws}
        t = ml.select_other(vals, w, tc)
        pk[w] = t
        d.append(0.0 if t == ml.INF else ref.me(w, name, t, w) - ref.pool(w, name, w))
    return dict(self_minus_pool=stats(d, rng), chosen_tau_region=ml.tau_region(pk.values())), pk


def b_dataset(results, ds, BV, mode_em, rng):
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    RV, PV = BV[ds]["r1"], BV[ds].get("pool")
    S = {}
    for pn in MAIN_PANELS[ds]:
        P = {}
        ws0 = next(iter(members[pn].values()))
        ast = {n: alpha_star(PV, ws0, n) for n in SN} if PV else None
        for k, ws in members[pn].items():
            M = mode_em[pn][str(k)]
            E = dict(writers=len(ws), current=M["two_stage"]["other"]["two_stage_other"]["all/self_minus_pool_same"]["median"])
            # B2: β*
            bst = beta_star(RV, ws, k)
            ref2 = Ref(results, k, RV=RV, bstar=bst)
            E["b2"] = dict(chosen_beta=ml.count_vals(bst.values()),
                           r1_gain=stats([RV[w][str(k)][bst[w]][0] - RV[w][str(k)]["0.5"][0] for w in ws], rng))
            E["b2"]["two_stage"], _, _ = joint_rows(ref2, ws, rng)
            E["b2"]["structs"] = {}
            for name in ("hmm3", "ar3"):
                vals = ml.em_values(results, ws, k, next(s for s in ml.STRUCTS if ml.sname(s) == name))
                pk = {w: ml.select_other(vals, w, ml.tau_cands()) for w in ws}
                E["b2"]["structs"][name] = dict(
                    self_minus_r1=stats([ml.me_of(results, w, k, name, pk[w], 0) - ref2.r1(w, w) for w in ws], rng),
                    pool_minus_r1=stats([results[w]["em"]["pool"][name][0] - ref2.r1(w, w) for w in ws], rng))
            if PV:
                # B1: α*（k に依らない）
                ref1 = Ref(results, k, PV=PV, astar=ast)
                E["b1"] = dict(chosen_alpha={n: ml.count_vals(ast[n][w] for w in ws) for n in SN},
                               pool_gain={n: stats([PV[w][n][ast[n][w]][0] - PV[w][n]["1"][0] for w in ws], rng) for n in SN})
                E["b1"]["two_stage"], pk1, _ = joint_rows(ref1, ws, rng)
                E["b1"]["two_stage"]["alpha_of_chosen_struct_is_1"] = int(sum(ast[pk1[w][0]][w] == "1" for w in ws))
                E["b1"]["structs"] = {n: tau_rows(ref1, ws, n, rng)[0] for n in SN}
                E["b1"]["pool_minus_r1"] = {n: stats([ref1.pool(w, n, w) - ref1.r1(w, w) for w in ws], rng)
                                            for n in ("hmm3", "ar3")}
                # B12: α* と β* の両方
                ref12 = Ref(results, k, PV=PV, astar=ast, RV=RV, bstar=bst)
                E["b12"], _, _ = joint_rows(ref12, ws, rng)
            P[str(k)] = E
        S[pn] = P
    return S


# ---------------------------------------------------------------- 読み（D6・機械の当て）
def a_form(L, Hm):
    if Hm <= 0:
        return "消える"
    return "残る" if Hm >= L / 2 else "縮む"


def b1_form(E):
    b = E["b1"]["two_stage"]
    if b["alpha_of_chosen_struct_is_1"] * 2 > E["writers"]:
        return "1 倍"
    R1, R0 = b["self_minus_pool"]["median"], E["current"]
    if R1 <= 0:
        return "消える"
    return "残る" if R1 >= R0 / 2 else "縮む"


def panel_form(forms):
    vals = list(forms.values())
    for f in dict.fromkeys(vals):
        if vals.count(f) * 2 > len(vals):
            return f
    return "混ざる"


def readings(A, B):
    out = {}
    P = A["coauthor"]["P15"]
    fa = {k: a_form(E["two_stage_other"]["current"], E["two_stage_other"]["self_minus_pool"]["honest"]["median"]) for k, E in P.items()}
    fs = {k: a_form(E["structs"]["ar3"]["current"], E["structs"]["ar3"]["self_minus_pool"]["honest"]["median"]) for k, E in P.items()}
    out["A"] = dict(two_stage=dict(k_forms=fa, panel_form=panel_form(fa)), ar3_tau_other=dict(k_forms=fs, panel_form=panel_form(fs)))
    PB = B["coauthor"]["P15"]
    if all("b1" in E for E in PB.values()):
        fb = {k: b1_form(E) for k, E in PB.items()}
        out["B1"] = dict(k_forms=fb, panel_form=panel_form(fb))
    cells = [(pn, k, E) for ds, pns in (("coauthor", ["P15"]), ("cs1", ["C5"])) for pn in pns for k, E in B[ds][pn].items()]
    bad = [dict(panel=pn, k=k) for pn, k, E in cells
           if not (E["b2"]["structs"]["hmm3"]["self_minus_r1"]["median"] < 0 and E["b2"]["two_stage"]["self_minus_r1"]["median"] > 0)]
    out["B2"] = dict(form="連鎖の所見は残る" if not bad else "変わる", cells_out=bad)
    return out


# ---------------------------------------------------------------- 表
def fm(x):
    if x is None:
        return "—"
    if isinstance(x, str):
        return {"+inf": "+∞", "-inf": "−∞"}.get(x, x)
    if x == 0:
        return "0"
    return ("%+.2e" % x) if abs(x) < 1e-2 else ("%+.3f" % x)


def st(s):
    if s is None or s.get("suppressed"):
        return "—"
    return "%s（良 %.2f）" % (fm(s["median"]), s["better_share"])


def write_json(obj, path):
    """改行を LF に固定して書く（HP Z2 でも repo の LF と同じバイト・レビュー LOW 12）。"""
    with open(path, "w", newline="\n") as f:
        json.dump(ml.enc(obj), f, indent=1, ensure_ascii=False, allow_nan=False)


def outside_repo(p):
    repo = os.path.normcase(os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..")))
    return not os.path.normcase(os.path.realpath(p)).startswith(repo + os.sep)


def write_tables(S, path):
    S = json.loads(json.dumps(ml.enc(S)))
    L = ["# 計算 A・B の表（集計値だけ・report が summary から作る）", "",
         "差は 1 記号あたりの対数尤度（全記号）。今 = mode の値（w を除く選び・全員の中央値）。", "",
         "## A: 書き手の二分（2,000 組の中央値 [2.5%, 97.5%]）", "",
         "| データ | パネル | k | 行 | 今 | 正直 h | 同じ半分 i | 楽観 o | h > 0 の割合 |", "|---|---|---|---|---|---|---|---|---|"]
    for ds, panels in S["A"].items():
        for pn, P in panels.items():
            for k, E in P.items():
                rows = [("2 段 本人 − 共通", E["two_stage_other"], "self_minus_pool"),
                        ("2 段 本人 − r1", E["two_stage_other"], "self_minus_r1")]
                rows += [("τ 他人 %s" % n, E["structs"][n], "self_minus_pool") for n in ("hmm3", "ar3")]
                for lab, X, key in rows:
                    Y = X[key]
                    cur = X["current"] if key == "self_minus_pool" else None
                    L.append("| %s | %s | %s | %s | %s | %s [%s, %s] | %s | %s | %.2f |" % (
                        ds, pn, k, lab, fm(cur), fm(Y["honest"]["median"]), fm(Y["honest"]["q025"]), fm(Y["honest"]["q975"]),
                        fm(Y["insample"]["median"]), fm(Y["optimism"]["median"]), Y["honest_pos_share"]))
    L += ["", "## B1: 共通の基の擬似度数を他人で選ぶ（CoAuthor）", "",
          "| パネル | k | 今 | 2 段 本人 − 共通(α*) | 2 段 本人 − r1 | 2 段の構造の α* = 1 の人数 | ar3 の α* の人数 | ar3 の 共通(α*) − 共通(1) | τ 他人 ar3 本人 − 共通(α*) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for pn, P in S["B"]["coauthor"].items():
        for k, E in P.items():
            if "b1" not in E:
                continue
            b = E["b1"]
            L.append("| %s | %s | %s | %s | %s | %d/%d | %s | %s | %s |" % (
                pn, k, fm(E["current"]), st(b["two_stage"]["self_minus_pool"]), st(b["two_stage"]["self_minus_r1"]),
                b["two_stage"]["alpha_of_chosen_struct_is_1"], E["writers"],
                " ".join("%s:%s" % kv for kv in b["chosen_alpha"]["ar3"].items()), st(b["pool_gain"]["ar3"]),
                st(b["structs"]["ar3"]["self_minus_pool"])))
    L += ["", "## B2: 本人の連鎖の加える値を他人で選ぶ", "",
          "| データ | パネル | k | β* の人数 | r1(β*) − r1(0.5) | hmm3 本人 − r1(β*) | 共通 hmm3 − r1(β*) | 2 段 本人 − r1(β*) | 2 段 本人 − 共通 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for ds, panels in S["B"].items():
        for pn, P in panels.items():
            for k, E in P.items():
                b = E["b2"]
                L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    ds, pn, k, " ".join("%s:%s" % kv for kv in b["chosen_beta"].items()), st(b["r1_gain"]),
                    st(b["structs"]["hmm3"]["self_minus_r1"]), st(b["structs"]["hmm3"]["pool_minus_r1"]),
                    st(b["two_stage"]["self_minus_r1"]), st(b["two_stage"]["self_minus_pool"])))
    L += ["", "## B12（並べるだけ・CoAuthor）", "", "| パネル | k | 本人 − 共通(α*) | 本人 − r1(β*) |", "|---|---|---|---|"]
    for pn, P in S["B"]["coauthor"].items():
        for k, E in P.items():
            if "b12" in E:
                L.append("| %s | %s | %s | %s |" % (pn, k, st(E["b12"]["self_minus_pool"]), st(E["b12"]["self_minus_r1"])))
    L += ["", "## 読み（D6 の機械の当て）", "", "```", json.dumps(S["readings"], indent=1, ensure_ascii=False), "```"]
    open(path, "w", newline="\n").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- 本計算
def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    raw, bvals, out = argv[0], argv[1], argv[2]
    files = {ds: raw + "." + ds + ".pkl" for ds in ("coauthor", "cs1")}
    if not all(outside_repo(p) for p in list(files.values()) + [bvals]):
        sys.exit("書き手ごとの値が repo の中を指している")
    # compute.py が照らした pickle と書いた B の値と同じファイルか（レビュー MEDIUM 6）
    rc = json.load(open(os.path.join(out, "repro_check.json")))
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    if any(sha(files[ds]) != rc["pkl_sha256"][ds] for ds in files) or sha(bvals) != rc["bvals_sha256"]:
        sys.exit("読む pickle が compute.py の照らしたものと違う")
    mode_sum = json.load(open(pinned4.MODE_SUMMARY))["datasets"]
    with open(bvals, "rb") as fp:
        BV = pickle.load(fp)  # compute.py が書いた自前の pickle（人は開かない）
    S = dict(run_id=run_id, A={}, B={})
    rng = np.random.default_rng([SEED + 4, 3])
    for ds in ("coauthor", "cs1"):
        with open(files[ds], "rb") as fp:
            results = pickle.load(fp)  # mode の本計算が書いた自前の pickle（人は開かない・P-REPRO は compute.py で済ませた）
        S["A"][ds] = a_dataset(results, ds, mode_sum[ds]["em"])
        S["B"][ds] = b_dataset(results, ds, BV, mode_sum[ds]["em"], rng)
    S["p_current"] = dict(passed=all(CHECKS), checked=len(CHECKS))
    if not all(CHECKS):
        write_json(S["p_current"], os.path.join(out, "p_current_failed.json"))
        sys.exit("P-CURRENT が外れた（行列から作った今の値が mode の summary と違う）。止めて調べる")
    S["readings"] = readings(S["A"], S["B"])
    write_json(S, os.path.join(out, "summary.json"))
    write_tables(S, os.path.join(out, "tables.md"))


if __name__ == "__main__":
    main()
