"""D7 実データ（conditions.md の追記 1・凍結 b0f5821a）。CoAuthor の 15-session パネルと CS1 の five-assignment パネルを E1 で読む。

読み込みは論文 3 の作り（tau-extend の data.py・ml.py を gen.py の pinned 経由で SHA-256 を照らして読む）。
数え・揃え・近さ・入れ替えは eye.py の関数をそのまま呼ぶ（eye.py は変えない）。E2・E3 は計算しない。

段:
  check  合成の 1 複製（報告の組・第 1 の帰無の用量の差なし・種 12000・両形）を同じ経路に入れ、
         results/report の保存の値（run_eye の出力）と一致するかを見る。実データは読まない。
  pre    計算の前に出す量（追記 1 (2)）。T と p は計算しない。
  main   9 セル × r = 0〜20 と頻度だけの基準線（追記 1 (2)〜(5)）。

使い方: python -I -X utf8 realdata.py <check|pre|main> <出力 json> [--data-dir DIR]
出力に書き手の ID は書かない（パネルの番号の列の SHA-256 だけ）。書き手ごとの値は番号を外して並べ替えた列だけを書く。
"""
import glob
import hashlib
import json
import math
import os
import platform
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import eye as EY  # noqa: E402
import gen as GN  # noqa: E402
import run_eye as RE  # noqa: E402

DT, ML = GN.DT, GN.ml
TAU = os.path.realpath(os.path.join(EXP, "..", "20261104-timeseries-tau-extend"))
LOAD_SEED = int(open(os.path.join(TAU, "SEED")).read().strip())   # load_* の seed（記号の系列に効かない・追記 1 (2)）
NULL_REAL, STRAND_REAL = 0, 7                                     # 実データの印（追記 1 (2)）
R_MAX = 20
HOLD_CS1_SHA = "a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47"
PANEL = dict(coauthor="P15", cs1="C5")
SE_N = EY.N_PERM


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def paths(data_dir):
    return dict(coauthor=os.path.join(data_dir, "landscape", "coauthor_work_obs"),
                coauthor_old=os.path.join(data_dir, "landscape", "coauthor_work"),
                cs1=os.path.join(data_dir, "cs1", "work2021_obs"),
                hold_coauthor=os.path.join(data_dir, "landscape", "holdout.json"),
                hold_cs1=os.path.join(data_dir, "cs1", "holdout.json"))


# ---------------------------------------------------------------- 固定するもの（追記 1 (2)）
def check_clean():
    """data.MUT・ml.MUT・eye.MUT（と hmm2・synth・gen）が空であること。空でなければ止める。"""
    bad = {n: sorted(m) for n, m in dict(data=DT.MUT, ml=ML.MUT, eye=EY.MUT, hmm2=ML.H.MUT, synth=GN.SY.MUT, gen=GN.MUT).items() if m}
    if bad:
        sys.exit("MUT が空でない: %r" % bad)
    return True


def list_hash(d, pat):
    fs = sorted(glob.glob(os.path.join(d, pat)))
    return dict(files=len(fs), sha256_of_sha256_list=hashlib.sha256("".join(os.path.basename(f) + sha(f) for f in fs).encode()).hexdigest())


def fixed(P_):
    """入力・取り置き・コード・版の記録。取り置きは作る段で外れている（作る段の記録と一覧の SHA-256 で確かめる）。"""
    hold_cs1 = sha(P_["hold_cs1"])
    if hold_cs1 != HOLD_CS1_SHA:
        sys.exit("CS1 の取り置きの一覧の SHA-256 が論文 3 の値と違う")
    bs_cs1 = json.load(open(os.path.join(P_["cs1"], "build_summary.json")))
    n_hold_cs1 = len(json.load(open(P_["hold_cs1"]))["2021"])
    if bs_cs1["holdout_sha256"] != hold_cs1 or bs_cs1["holdout_writers_skipped"] != n_hold_cs1:
        sys.exit("CS1 の中間が今の取り置きの一覧で作られていない")
    bs_coa = json.load(open(os.path.join(P_["coauthor_old"], "build_summary.json")))
    s_new = json.load(open(os.path.join(P_["coauthor"], "sessions.json")))
    s_old = json.load(open(os.path.join(P_["coauthor_old"], "sessions.json")))
    if s_new != s_old:
        sys.exit("CoAuthor の obs の中間の sessions.json が、取り置きを外した中間と違う")
    if not bs_coa.get("held_out_sessions"):
        sys.exit("CoAuthor の中間の作る段で取り置きのセッションが外れた記録が無い")
    d6 = os.path.join(EXP, "results", "report", "d6.json")
    eqa = os.path.join(EXP, "results", "explore", "eq_amounts.json")
    return dict(
        mut_empty=check_clean(),
        inputs=dict(coauthor=dict(list_hash(P_["coauthor"], "s[0-9]*.json"), sessions_json=sha(os.path.join(P_["coauthor"], "sessions.json"))),
                    cs1=dict(list_hash(P_["cs1"], "u[0-9]*.json"), units_json=sha(os.path.join(P_["cs1"], "units.json")),
                             build_summary=sha(os.path.join(P_["cs1"], "build_summary.json")))),
        holdout=dict(coauthor_sha256=sha(P_["hold_coauthor"]), coauthor_held_out_sessions_at_build=bs_coa["held_out_sessions"],
                     coauthor_obs_sessions_equal_holdout_removed_work=True,
                     cs1_sha256=hold_cs1, cs1_writers_skipped_at_build=bs_cs1["holdout_writers_skipped"]),
        code_hash=RE.code_hash(),
        scripts={os.path.basename(p): sha(p) for p in sorted(glob.glob(os.path.join(HERE, "*.py")))},
        pinned_tau={f: sha(os.path.join(TAU, "scripts", f)) for f in ("data.py", "ml.py", "hmm2.py")},
        python=platform.python_version(), numpy=np.__version__, machine=platform.platform(),
        d6_json_sha256=sha(d6), eq_amounts_json_sha256=sha(eqa), load_seed=LOAD_SEED)


# ---------------------------------------------------------------- 読み込み（論文 3 の作り）
def writer_ids(ds, path):
    """sorted(by_w) の鍵（作業ディレクトリの書き手の番号）と単位の数。load_* と同じ選びをなぞる（値は返さない）。"""
    cnt = {}
    if ds == "coauthor":
        s2w = json.load(open(os.path.join(path, "sessions.json")))
        for f in sorted(glob.glob(os.path.join(path, "s[0-9]*.json"))):
            sid = os.path.basename(f)[1:-5]
            if sid not in s2w:
                continue
            d = json.load(open(f))
            if len(d["observed_intervals"]) != 1 or not d["feat"]:
                continue
            cnt[s2w[sid]] = cnt.get(s2w[sid], 0) + 1
    else:
        u2w = json.load(open(os.path.join(path, "units.json")))
        for uid in sorted(u2w):
            d = json.load(open(os.path.join(path, "u%s.json" % uid)))
            if d["feat"]:
                cnt[u2w[uid]] = cnt.get(u2w[uid], 0) + 1
    ids = sorted(cnt)
    return ids, [cnt[i] for i in ids]


def load_real(ds, path):
    """返り値: (UC（パネルを先頭に）, P, H, 記録)。書き手は除外しない。"""
    writers, _ = ML.load(ds, path, LOAD_SEED)
    ids, ns = writer_ids(ds, path)
    if ns != [len(u) for u in writers]:
        sys.exit("書き手の番号の列が load_* の書き手と合わない（%s）" % ds)
    for u in writers:
        for x in u:
            for s in x["seqs"]:
                if len(s) and (int(np.min(s)) < 0 or int(np.max(s)) >= GN.NSYM):
                    sys.exit("記号が 0〜%d の外（%s）" % (GN.NSYM - 1, ds))
    H = ML.DATASETS[ds]["H"]
    nmin = ML.DATASETS[ds]["panels"][PANEL[ds]][0]
    UC = EY.count_writers(writers, GN.NSYM)
    UC, idx = panel_first(UC, nmin)
    rec = dict(writers_loaded=len(writers), H=H, panel_rule="n >= %d" % nmin, panel=len(idx),
               panel_ids_sha256=hashlib.sha256("\n".join(str(ids[i]) for i in idx).encode()).hexdigest(),
               eligible_n_ge_H1=sum(1 for u in writers if len(u) >= H + 1))
    return UC, len(idx), H, rec


def panel_first(UC, nmin):
    """パネル（単位が nmin 以上）を元の順（sorted(by_w)）のまま先頭に、残りを後ろに。S と π は全員の和なので並べに依らない。"""
    idx = [i for i, u in enumerate(UC) if len(u) >= nmin]
    rest = [i for i in range(len(UC)) if i not in idx]
    return [UC[i] for i in idx] + [UC[i] for i in rest], idx


# ---------------------------------------------------------------- 計算の前に出す量（追記 1 (2)）
def q5(x):
    x = np.asarray(x, float)
    return dict(min=float(x.min()), q1=float(np.quantile(x, 0.25)), median=float(np.median(x)), q3=float(np.quantile(x, 0.75)), max=float(x.max()))


def pre_amounts(UC, P, H, cells):
    out = dict(panel=P, outside=len(UC) - P, outside_units=int(sum(len(u) for u in UC[P:])),
               outside_units_list=sorted(len(u) for u in UC[P:]),
               panel_units=q5([len(u) for u in UC[:P]]), panel_units_list=sorted(len(u) for u in UC[:P]), cells={})
    for k, g in cells:
        T = EY.cell_tables(UC, P, H, k, g)
        tA = T["NA"].reshape(P, -1).sum(1)
        tB = T["NB"].reshape(P, -1).sum(1)
        out["cells"]["k%d_g%d" % (k, g)] = dict(nA=int(tA.min()), nB=int(tB.min()),
                                                 ratio_A=float(tA.min() / np.median(tA)), ratio_B=float(tB.min() / np.median(tB)))
    return out


WIDE = dict(A=(0.078, 0.665), B=(0.083, 0.552))   # 追記 1「CS1 の読みの範囲」の wide の量の比の範囲


def marks(ds, pre):
    """追記 1 (5) の範囲の表（eq_amounts.json の by_cell）と、CS1 は wide の比の範囲に照らした印。"""
    rng = json.load(open(os.path.join(EXP, "results", "explore", "eq_amounts.json")))["by_cell"]
    out = {}
    for c, v in pre["cells"].items():
        r = rng["%s/%s" % (ds, c)]
        m = {}
        for side in ("A", "B"):
            n = v["n" + side]
            m["n" + side] = "下" if n < r["n%s_min" % side] else ("上" if n > r["n%s_max" % side] else "内")
            if ds == "cs1":
                lo, hi = WIDE[side]
                x = v["ratio_" + side]
                m["wide_ratio_" + side] = "下" if x < lo else ("上" if x > hi else "内")
        m["range"] = "内" if m["nA"] == "内" and m["nB"] == "内" else "外"
        m["table"] = dict(r)
        out[c] = m
    return out


# ---------------------------------------------------------------- 頻度だけの基準線（追記 1 (2)）
def sim_freq(T, M, m=EY.M_SHARE):
    """s0(w → v) = Σ_c NB_v の列の和[c] · log q_w^A[c] / Σ NB_v。q_w^A = (A の列の和 + m f) / (A の総数 + m)。"""
    J = M.shape[0]
    f = (M.sum(0) + 0.5 * J) / (M.sum() + 0.5 * J * J)
    P = len(T["NA"])
    colA = T["NA"].sum(1).astype(float)       # P×J: Σ_j N_w^A[j, c]
    qA = (colA + m * f[None, :]) / (colA.sum(1, keepdims=True) + m)
    colB = T["NB"].sum(1).astype(float)
    return (np.log(qA) @ colB.T) / colB.sum(1)[None, :]


def sim_freq_loop(T, M, w, v, m=EY.M_SHARE):
    """検査用: s0(w → v) をループで独立に計算する。"""
    J = M.shape[0]
    tot = float(M.sum()) + 0.5 * J * J
    f = [(float(M[:, c].sum()) + 0.5 * J) / tot for c in range(J)]
    NA, NB = T["NA"][w], T["NB"][v]
    na = float(NA.sum())
    s, n = 0.0, 0.0
    for c in range(J):
        qc = (float(NA[:, c].sum()) + m * f[c]) / (na + m)
        nb = float(NB[:, c].sum())
        s += nb * math.log(qc)
        n += nb
    return s / n


# ---------------------------------------------------------------- 1 セル
def eye_e1(T, perms, P):
    s = EY.sim_e1(T)
    if not np.isfinite(s).all():
        raise FloatingPointError("E1 の近さに有限でない値（D2: 止める）")
    c = EY.score_matrix(s)
    p, W = EY.p_sampled(c, perms)
    return s, c, p, W


def run_cell(UC, P, H, k, g, shape_no, null, strand, eq_last, perm_last, rs, indexed=False):
    """rs[0] が主の 1 回（判定）。rs[1:] は揃えだけを引き直す（σ は共有）。indexed は検査用（番号つきの値を返す）。"""
    base = EY.cell_tables(UC, P, H, k, g)
    M = EY.shared_counts(UC, H)
    perms = EY.draw_perms(np.random.default_rng([GN.SEED, null, strand, shape_no, k, g, perm_last]), P)
    out = dict(P=P)
    side0 = [s for s, N in (("A", base["NA"]), ("B", base["NB"])) if int(N.reshape(P, -1).sum(1).min()) == 0]
    if side0:
        out["status"] = "計算できなかった"
        out["zero_side"] = side0
        return out
    rep = []
    for i, r in enumerate(rs):
        T = EY.equalize(base, EY.eq_key(GN.SEED, null, strand, shape_no, k, g, eq_last(r)))
        s, c, p, W = eye_e1(T, perms, P)
        if i == 0:
            auc = EY.auc_rows(c)
            G = EY.gain_own(T)
            eg, ee = EY.eer_pair(s)
            out.update(status="計算した", nA=T["nA"], nB=T["nB"], W=W, T=float(EY.t_of_w(W, P)), p=p,
                       se=math.sqrt(p * (1 - p) / SE_N), rank1=EY.rank1(s), eer_glob=eg, eer_each=ee,
                       auc_sorted=sorted(auc.tolist()), auc_q=q5(auc), G_sorted=sorted(G.tolist()), G_q=q5(G))
            if indexed:
                out["_idx"] = dict(W=W, p=p, auc=auc.tolist(), G=G.tolist(), rank1=EY.rank1(s), eer_glob=eg, eer_each=ee,
                                   nA=T["nA"], nB=T["nB"], T=T, M=M)
            s0 = sim_freq(T, M)
            if np.isfinite(s0).all():
                c0 = EY.score_matrix(s0)
                p0, W0 = EY.p_sampled(c0, perms)
                out["freq"] = dict(status="計算した", W=W0, T=float(EY.t_of_w(W0, P)), p=p0, se=math.sqrt(p0 * (1 - p0) / SE_N))
            else:
                out["freq"] = dict(status="算出できなかった")
            if indexed:
                out["_idx"]["s0"] = s0
        else:
            rep.append(dict(r=r, W=W, T=float(EY.t_of_w(W, P)), p=p))
    if rep:
        ps = [x["p"] for x in rep]
        Ts = [x["T"] for x in rep]
        out["redraw"] = dict(n=len(rep), p_min=min(ps), p_max=max(ps), T_min=min(Ts), T_max=max(Ts),
                             p_le_005=sum(1 for x in ps if x <= 0.05), rows=rep)
    return out


def holm(ps):
    """Holm の補正（単調にした値）。"""
    n = len(ps)
    o = sorted(range(n), key=lambda i: ps[i])
    adj = [0.0] * n
    run = 0.0
    for rank, i in enumerate(o):
        run = max(run, min(1.0, (n - rank) * ps[i]))
        adj[i] = run
    return adj


# ---------------------------------------------------------------- 段
def stage_check():
    """合成の 1 複製（第 1 の帰無・用量・差なし・種 12000）を同じ経路に入れ、保存の値と照らす。実データは読まない。"""
    check_clean()
    ch = RE.code_hash()
    res = dict(code_hash=ch, shapes={}, ok=True)
    for shape in ("coauthor", "cs1"):
        row = dict(null=1, strand="dose", shape=shape, step=0.0, seed=12000)
        w, P = GN.make(row)
        sh = GN.SY.SHAPES[shape]
        nmin = ML.DATASETS[shape]["panels"][PANEL[shape]][0]
        UC = EY.count_writers(w, GN.NSYM)
        UC2, idx = panel_first(UC, nmin)
        if idx != list(range(P)) or sh["H"] != ML.DATASETS[shape]["H"]:
            sys.exit("合成のパネルの選びが run_eye と違う（%s）" % shape)
        saved = None
        for line in open(os.path.join(EXP, "results", "report", "null1_dose_%s_0.0.jsonl" % shape)):
            d = json.loads(line)
            if d["seed"] == 12000:
                saved = d
                break
        if saved is None or saved["code_hash"] != ch:
            sys.exit("保存の値が無いか code_hash が違う（%s）" % shape)
        pre = pre_amounts(UC2, P, sh["H"], RE.CELLS[shape])
        cells = {}
        for k, g in RE.CELLS[shape]:
            name = "k%d_g%d" % (k, g)
            o = run_cell(UC2, P, sh["H"], k, g, RE.SHAPE_NO[shape], 1, GN.STRAND["dose"], lambda r: r, 12000, [12000], indexed=True)
            x, sv = o["_idx"], saved["cells"][name]
            e1 = sv["E1"]
            diffs = dict(W=x["W"] == e1["W"], p=x["p"] == e1["p"], nA=x["nA"] == sv["nA"] == pre["cells"][name]["nA"],
                         nB=x["nB"] == sv["nB"] == pre["cells"][name]["nB"],
                         auc=bool(np.allclose(x["auc"], e1["auc"], rtol=0, atol=1e-12)),
                         G=bool(np.allclose(x["G"], sv["G"], rtol=0, atol=1e-12)),
                         rank1=abs(x["rank1"] - e1["rank1"]) <= 1e-12, eer_glob=abs(x["eer_glob"] - e1["eer_glob"]) <= 1e-12,
                         eer_each=abs(x["eer_each"] - e1["eer_each"]) <= 1e-12)
            diffs = {kk: bool(vv) for kk, vv in diffs.items()}
            loop = float(max(abs(sim_freq_loop(x["T"], x["M"], a, b) - x["s0"][a, b]) for a, b in ((0, 0), (0, P - 1), (P - 1, 0), (3, 5))))
            diffs["freq_loop_1e-12"] = bool(loop <= 1e-12)
            diffs["freq_finite"] = o["freq"]["status"] == "計算した"
            cells[name] = dict(match=diffs, freq_loop_maxdiff=loop)
            if not all(diffs.values()):
                res["ok"] = False
        res["shapes"][shape] = cells
    # 揃えの鍵: 実データの鍵は合成の鍵（帰無 1・2、筋 0〜6）と重ならない
    res["key_disjoint"] = bool(NULL_REAL not in (1, 2) and STRAND_REAL not in GN.STRAND.values())
    res["ok"] = res["ok"] and res["key_disjoint"]
    return res


def stage_pre(P_):
    out = dict(fixed=fixed(P_), datasets={})
    for ds in ("coauthor", "cs1"):
        UC, P, H, rec = load_real(ds, P_[ds])
        pre = pre_amounts(UC, P, H, RE.CELLS[ds])
        out["datasets"][ds] = dict(rec, pre=pre, marks=marks(ds, pre))
    return out


def stage_main(P_):
    out = dict(fixed=fixed(P_), datasets={}, chosen="E1", n_perm=EY.N_PERM, r_max=R_MAX)
    c = json.load(open(os.path.join(EXP, "results", "report", "d6.json")))["c"]
    order = []
    for ds in ("coauthor", "cs1"):
        UC, P, H, rec = load_real(ds, P_[ds])
        pre = pre_amounts(UC, P, H, RE.CELLS[ds])
        cells = {}
        for k, g in RE.CELLS[ds]:
            name = "k%d_g%d" % (k, g)
            o = run_cell(UC, P, H, k, g, RE.SHAPE_NO[ds], NULL_REAL, STRAND_REAL, lambda r: r, 0, list(range(R_MAX + 1)))
            if o["status"] == "計算した":
                cv = c["%s/%s" % (ds, name)]
                o["c"] = cv
                o["G_gt_c"] = sum(1 for x in o["G_sorted"] if x > cv)
                o["G_gt_0"] = sum(1 for x in o["G_sorted"] if x > 0)
                o["verdict"] = "拾った" if o["p"] <= 0.05 else "拾わなかった"
            else:
                o["verdict"] = "計算できなかった"
            cells[name] = o
            order.append((ds, name))
        out["datasets"][ds] = dict(rec, pre=pre, marks=marks(ds, pre), cells=cells)
    ps = [out["datasets"][d]["cells"][n].get("p", 1.0) if out["datasets"][d]["cells"][n]["verdict"] != "計算できなかった" else 1.0
          for d, n in order]
    for (d, n), a in zip(order, holm(ps)):
        out["datasets"][d]["cells"][n]["p_holm"] = a
    return out


def main():
    argv = sys.argv[1:]
    data_dir = os.path.join(os.path.expanduser("~"), "gse-public-data")
    if "--data-dir" in argv:
        i = argv.index("--data-dir")
        data_dir = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    stage, out = argv[0], argv[1]
    check_clean()
    GN.assert_clean()
    if stage == "check":
        res = stage_check()
    elif stage == "pre":
        res = stage_pre(paths(data_dir))
    elif stage == "main":
        res = stage_main(paths(data_dir))
    else:
        sys.exit("段が違う: %s" % stage)
    res["stage"] = stage
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    if stage == "check" and not res["ok"]:
        sys.exit("合成の照合が合わない（%s）" % out)
    print("終わり: %s → %s" % (stage, out), flush=True)


if __name__ == "__main__":
    main()
