"""最頻値を他人で選ぶ候補と比べの相手に置いた集計（conditions.md D2〜D5）。当てはめは回さない。

使い方（HP Z2）: python3 -I sel.py <raw_prefix> <out_dir> [--run-id ID]
  <raw_prefix>: mode の本計算の書き手ごとの値（<raw_prefix>.coauthor.pkl・<raw_prefix>.cs1.pkl・repo の外・人は開かない）。
出力: <out_dir>/summary.json（集計値だけ）・tables.md・repro_check.json。
門: P-REPRO（pickle に mode の summarize_em を当て直し、mode の summary.json の em と同じ）。外れれば止める。
"""
import hashlib
import json
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned3  # noqa: E402
from pinned3 import H, ml  # noqa: E402

MUT = set()  # n1: 選びに w 自身・n2: 最頻値を ∞ より先・n3: 最頻値が選ばれた書き手の 本人 − 最頻値 を b に・n4: −∞ を選びから捨てる
MODE = ml.MODE
MAIN_PANELS = {"coauthor": ["P15", "P30"], "cs1": ["C5"]}
OPPS = ("r1", "pool_same", "mode_same")


# ---------------------------------------------------------------- 候補と選び
def tau_cands_mode():
    """∞ → 最頻値 → 10^6 → … → 0（mode の m22 と同じ位置）。n2 は最頻値を ∞ より先に。"""
    c = sorted(ml.TAU_KEYS, key=ml.tau_val, reverse=True)
    return [MODE] + c if "n2" in MUT else c[:1] + [MODE] + c[1:]


def joint_cands_mode():
    return [(ml.sname(s), t) for t in tau_cands_mode() for s in sorted(ml.STRUCTS, key=lambda s: H.n_free(*s))]


def _select(values, w, cands):
    """w を除く v の中央値がいちばん大きい候補（同点は cands の先）。n1 は w を入れる・n4 は −∞ を捨てる。"""
    vs = [v for v in values if v != w or "n1" in MUT]
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in vs if values[v].get(c) is not None]
        if "n4" in MUT:
            xs = [x for x in xs if x != -np.inf]
        if not xs:
            continue
        m = float(np.median(xs))
        if bv is None or m > bv:
            best, bv = c, m
    return best


def tau_values(results, ws, k, name):
    """τ 他人の値: 本人(τ) − 同じ構造の共通（最頻値の行は 最頻値 − 共通・τ = ∞ は 0）。全記号。"""
    return {v: {t: ml.me_of(results, v, k, name, t, 0) - results[v]["em"]["pool"][name][0] for t in tau_cands_mode()}
            for v in ws}


def joint_values(results, ws, k):
    """2 段（他人）の値: 本人(構造, τ) − r1（最頻値の行は 最頻値 − r1）。全記号。"""
    out = {}
    for v in ws:
        r1 = results[v]["em"]["k"][str(k)]["r1"][0]
        out[v] = {(n, t): ml.me_of(results, v, k, n, t, 0) - r1 for n, t in joint_cands_mode()}
    return out


# ---------------------------------------------------------------- 集計
def deltas(results, ws, k, pick, j, opp):
    """行 − 相手（書き手ごと）。mode の row_deltas（最頻値が選ばれた書き手の 本人 − 最頻値 は 0）。n3 はそれを b にする。"""
    d = ml.row_deltas(results, ws, k, pick, j, opp)
    if "n3" in MUT and opp == "mode_same":
        d = [(results[w]["em"]["mode"][pick[w][0]][j] - results[w]["em"]["pool"][pick[w][0]][j])
             if pick[w] is not None and pick[w][1] == MODE else x for w, x in zip(ws, d)]
    return d


def row_stats(results, ws, k, pick, rng):
    return {lab + "/self_minus_" + opp: ml.delta_stats(deltas(results, ws, k, pick, j, opp), rng)
            for j, lab in enumerate(("all", "pressed")) for opp in OPPS}


def region(taus):
    taus = [t for t in taus if t is not None]
    r = dict(inf=0, mode=0, high_finite_end=0, inside=0, low_end=0)
    for t in taus:
        if t == ml.INF:
            r["inf"] += 1
        elif t == MODE:
            r["mode"] += 1
        elif t == str(ml.TAUS_FIT[-1]):
            r["high_finite_end"] += 1
        elif t == "0":
            r["low_end"] += 1
        else:
            r["inside"] += 1
    return r


def summarize(results, ds, rng):
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    S = {}
    for pn in MAIN_PANELS[ds]:
        P = {}
        for k, ws in members[pn].items():
            if not ws:
                continue
            E = dict(writers=len(ws), structs={})
            for s in ml.STRUCTS:
                name = ml.sname(s)
                vals = tau_values(results, ws, k, name)
                pick = {w: (name, _select(vals, w, tau_cands_mode())) for w in ws}
                St = row_stats(results, ws, k, pick, rng)
                St["chosen_tau"] = ml.count_vals(p[1] for p in pick.values())
                St["chosen_region"] = region(p[1] for p in pick.values())
                E["structs"][name] = St
            jv = joint_values(results, ws, k)
            jc = joint_cands_mode()
            pick = {w: _select(jv, w, jc) for w in ws}
            T = row_stats(results, ws, k, pick, rng)
            T["chosen_struct"] = ml.count_vals(p[0] for p in pick.values())
            T["chosen_tau"] = ml.count_vals(p[1] for p in pick.values())
            T["chosen_region"] = region(p[1] for p in pick.values())
            E["two_stage_other"] = T
            P[str(k)] = E
        S[pn] = P
    return S


# ---------------------------------------------------------------- 読み（D5）
def k_form(E):
    T = E["two_stage_other"]
    n, r = E["writers"], T["chosen_region"]
    fin = r["high_finite_end"] + r["inside"] + r["low_end"]
    a = T["all/self_minus_mode_same"]
    if r["inf"] * 2 > n:
        return "∞"
    if r["mode"] * 2 > n:
        return "M"
    if fin * 2 > n:
        return "S" if (a["median"] > 0 and a["better_share"] > 0.5) else "N"
    return "なし"


def readings(S):
    """パネルごとに k の形と、パネルの形（∞ の k を除いた k の半分を超える形・conditions.md D5）。"""
    out = {}
    for ds, panels in S.items():
        for pn, P in panels.items():
            ks = {k: k_form(E) for k, E in P.items()}
            counted = [f for f in ks.values() if f != "∞"]
            pf = "全 k で ∞" if not counted else next((f for f in ("M", "S", "N") if counted.count(f) * 2 > len(counted)), "なし")
            out[pn] = dict(k_forms=ks, counted=len(counted), panel_form=pf)
    return out


# ---------------------------------------------------------------- 本計算
def repro(results, ds, seed):
    """P-REPRO: mode の summarize_em を当て直し、mode の summary.json の em と JSON として同じか。"""
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    got = json.loads(json.dumps(ml.enc(ml.summarize_em(results, cfg, ns, np.random.default_rng(seed + 4))), allow_nan=False))
    want = json.load(open(pinned3.MODE_SUMMARY))["datasets"][ds]["em"]
    return got == want


def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    raw, out = argv[0], argv[1]
    repo = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    if os.path.realpath(raw).startswith(repo + os.sep):
        sys.exit("書き手ごとの値が repo の中を指している")
    os.makedirs(out, exist_ok=True)
    seed = pinned3.SEED
    S, rc = dict(run_id=run_id, datasets={}), dict(run_id=run_id, pkl_sha256={}, p_repro={})
    for ds in ("coauthor", "cs1"):
        p = raw + "." + ds + ".pkl"
        rc["pkl_sha256"][ds] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        with open(p, "rb") as fp:
            results = pickle.load(fp)  # mode の本計算が書いた自前の pickle（人は開かない）
        ok = repro(results, ds, seed)
        rc["p_repro"][ds] = ok
        json.dump(rc, open(os.path.join(out, "repro_check.json"), "w"), indent=1)
        if not ok:
            sys.exit("P-REPRO が外れた（%s）。mode の run.sh で回し直してから使う（conditions.md D1）" % ds)
        S["datasets"][ds] = summarize(results, ds, np.random.default_rng([seed + 4, 1]))
    S["readings"] = readings(S["datasets"])
    ml.dump_json(S, os.path.join(out, "summary.json"), indent=1)
    write_tables(S, os.path.join(out, "tables.md"))


def fm(x):
    if x is None:
        return "—"
    if isinstance(x, str):
        return {"+inf": "+∞", "-inf": "−∞"}.get(x, x)
    if not np.isfinite(x):
        return "+∞" if x > 0 else "−∞"
    if x == 0:
        return "0"
    return ("%+.2e" % x) if abs(x) < 1e-2 and x != 0 else ("%+.3f" % x)


def cellv(st):
    if st is None or st.get("suppressed"):
        return "—"
    return "%s（良 %.2f）" % (fm(st["median"]), st["better_share"])


def write_tables(S, path):
    """前（mode の summary・最頻値を候補に入れない）と後（ここ）を並べる。全記号。"""
    S = json.loads(json.dumps(ml.enc(S)))
    old = json.load(open(pinned3.MODE_SUMMARY))["datasets"]
    L = ["# 最頻値を候補と相手に置いた主の表（集計値だけ）", "",
         "差は 1 記号あたりの対数尤度（全記号）・書き手ごとの差の中央値（良 = > 0 の割合）。前 = 最頻値を候補に入れない（mode の値）。", "",
         "## 2 段（他人）", "",
         "| パネル | k | n | 前: 本人 − 共通 | 前: 本人 − 最頻値 | 後: 本人 − 共通 | 後: 本人 − 最頻値 | 後: 本人 − r1 | 後: 選ばれた τ の領域 | 後: 構造 | 形 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for ds, panels in S["datasets"].items():
        for pn, P in panels.items():
            for k, E in P.items():
                T = E["two_stage_other"]
                O = old[ds]["em"][pn][k]["two_stage"]["other"]["two_stage_other"]
                rg = " ".join("%s:%d" % kv for kv in T["chosen_region"].items() if kv[1])
                L.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    pn, k, E["writers"], cellv(O["all/self_minus_pool_same"]), cellv(O["all/self_minus_mode_same"]),
                    cellv(T["all/self_minus_pool_same"]), cellv(T["all/self_minus_mode_same"]),
                    cellv(T["all/self_minus_r1"]), rg, " ".join("%s:%d" % kv for kv in T["chosen_struct"].items()),
                    S["readings"][pn]["k_forms"][k]))
    L += ["", "## τ 他人（構造ごと）", "",
          "| パネル | k | 構造 | 前: 本人 − 共通 | 後: 本人 − 共通 | 後: 本人 − 最頻値 | 後: 本人 − r1 | 後: 選ばれた τ の領域 |",
          "|---|---|---|---|---|---|---|---|"]
    for ds, panels in S["datasets"].items():
        for pn, P in panels.items():
            for k, E in P.items():
                for name, St in E["structs"].items():
                    O = old[ds]["em"][pn][k]["structs"][name]["tau_other"]
                    rg = " ".join("%s:%d" % kv for kv in St["chosen_region"].items() if kv[1])
                    L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                        pn, k, name, cellv(O["all/self_minus_pool_same"]), cellv(St["all/self_minus_pool_same"]),
                        cellv(St["all/self_minus_mode_same"]), cellv(St["all/self_minus_r1"]), rg))
    L += ["", "## 読み（D5 の機械の当て）", "", "```", json.dumps(S["readings"], indent=1, ensure_ascii=False), "```"]
    open(path, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
