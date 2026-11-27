"""D5 の読み（conditions D5）: G の語・作りの確かめ・型・勧め (1) の境・本文と補足の英文を、書き手ごとの値から機械で組み立てる。

入力 V（analyze.py が作る・書き手の ID は持たず通し番号だけ）:
  V["cells"][k]（k = "5"・"15"）: {"G": {列: {w: 値}}, "C2a": …, "R1P": …（r1 − 共有 hmm3）, "G_nohead": …, "G_t10000": …}
  V["constr"]: {"M_diff": {列: {w: 値}}, "D_s": …, "rho_x": …, "rho_y": …}
  V["desc"]: 本文の句に入れる記述の値（"stretch_C30_sec"・"w_ar3"・"w_ar3_t10000"・"w_hmm3"（{列: {k: 値}}）・
             "resid_diff"（{列: {k: {"x": 値, "y": 値}}}））
閾値・語・英文は条件の第 7 版のまま（変えない）。中央値は inverted_cdf（S13 の ml.q と同じ）。区間は ml.boot_median。
変異: m69 「3 つ以上」を「2 つ以上」／m74 中央値どうしの差／m75 φ の分母を G_A1 の中央値／m79 作りの確かめの正の条件を外す／
m81 共通の集合を列ごとの集合に／m82 型 1 の結果の文から句 (3) を落とす／m83 留保の句を新しい節だけに付ける。
"""
import math

import numpy as np

STEPS = [5, 10, 15, 30]
GRID = [1, 5, 10, 15, 30]
CELLS = ["5", "15"]
M_MIN = 12
MUT = set()

W_EN = {
    "列 C では縮みが小さい": "the gap stayed at an equal number of symbols",
    "列 C でも同じ程度に縮む": "the gap shrank about as much at an equal number of symbols",
    "列 C でかえって大きく縮む": "the gap shrank more at an equal number of symbols",
    "比が 1.5 を超える": "the ratio exceeded 1.5",
    "形が定まらない": "no pattern by the prespecified cut points",
    "割れる": "the two cells disagreed",
    "欠けがある": "fewer than 12 writers with all values",
    "列 A で縮まない": "no shrinkage between the 1-second and 30-second steps",
}
TYPE_OF = {"列 C では縮みが小さい": "1", "列 C でも同じ程度に縮む": "2", "列 C でかえって大きく縮む": "3"}
TYPE_NAME = {
    "1": "この比べでは、記号の数をそろえても差が残る形",
    "2": "この比べでは、記号の数をそろえると同じ程度に縮み、差が残るという予測を支えない形",
    "3": "この比べでは、記号の数をそろえるとかえって大きく縮み、差が残るという予測を支えない形",
    "なし": "形が定まらない",
    "外れ": "作りの確かめが外れた",
}
CLS = ("両方正", "両方正でない", "混ざる", "欠け")


def set_mut(mut):
    MUT.clear()
    MUT.update(mut)


# ---------------------------------------------------------------- 数の部品
def med(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return float(np.quantile(np.asarray(xs, dtype=float), 0.5, method="inverted_cdf"))


def colA(s):
    return "A%d" % s


def colC(s, prefix="C"):
    return "%s%d" % (prefix, s)


def present(vals, col):
    return {w for w, v in vals.get(col, {}).items() if v is not None}


def common(vals, cols):
    """共通の書き手の集合（全部の列に値のある書き手）。m81 は None（列ごとの集合を使う）。"""
    if "m81" in MUT:
        return None
    ws = None
    for c in cols:
        p = present(vals, c)
        ws = p if ws is None else ws & p
    return sorted(ws or [], key=lambda x: int(x))


def set_size(vals, cols, ws):
    if ws is not None:
        return len(ws)
    return min(len(present(vals, c)) for c in cols)  # m81: 列ごとの集合の最小


def paired(vals, a, b, ws):
    """同じ書き手の対応のある差の中央値（a − b）。m74 は中央値どうしの差。m81 は 2 列にある書き手だけ。"""
    if ws is None:
        ws = sorted(present(vals, a) & present(vals, b), key=lambda x: int(x))
    if not ws:
        return None
    if "m74" in MUT:
        return med([vals[a][w] for w in ws]) - med([vals[b][w] for w in ws])
    return med([vals[a][w] - vals[b][w] for w in ws])


def level(vals, col, ws):
    if ws is None:
        ws = sorted(present(vals, col), key=lambda x: int(x))
    return med([vals[col][w] for w in ws])


# ---------------------------------------------------------------- G の語
def g_word(G, prefix="C", drop=None):
    """1 セルの G の語。返り値: (語, 詳しい値)。drop は 1 人抜きの書き手。"""
    cols = ["A1"] + [colA(s) for s in STEPS] + [colC(s, prefix) for s in STEPS]
    ws = common(G, cols)
    if drop is not None and ws is not None:
        ws = [w for w in ws if w != drop]
    m = set_size(G, cols, ws)
    det = dict(m=m)
    if m < M_MIN:
        return "欠けがある", det
    shrink = {s: paired(G, "A1", colA(s), ws) for s in STEPS}
    stay = {s: paired(G, colC(s, prefix), colA(s), ws) for s in STEPS}
    phi = {s: (stay[s] / shrink[s] if shrink[s] is not None and shrink[s] > 0 and stay[s] is not None else None) for s in STEPS}
    if "m75" in MUT:
        g1 = level(G, "A1", ws)
        phi[30] = stay[30] / g1 if g1 else None
    npos = sum(1 for s in STEPS if stay[s] is not None and stay[s] > 0)
    det.update(shrink={str(s): shrink[s] for s in STEPS}, stay={str(s): stay[s] for s in STEPS},
               phi={str(s): phi[s] for s in STEPS}, stay_pos=npos)
    if shrink[30] is None or shrink[30] <= 0:
        return "列 A で縮まない", det
    p = phi[30]
    if p is None:
        return "形が定まらない", det
    if p > 1.5:
        return "比が 1.5 を超える", det
    if p >= 0.5 and npos >= (2 if "m69" in MUT else 3):
        return "列 C では縮みが小さい", det
    if abs(p) < 0.25:
        return "列 C でも同じ程度に縮む", det
    if p <= -0.25:
        return "列 C でかえって大きく縮む", det
    return "形が定まらない", det


def combine(words):
    w5, w15 = words
    if w5 == w15:
        return w5
    if "欠けがある" in (w5, w15):
        return "欠けがある"
    return "割れる"


def cell_words(V, key="G", prefix="C"):
    out = {k: g_word(V["cells"][k][key], prefix) for k in CELLS}
    return combine([out[k][0] for k in CELLS]), out


# ---------------------------------------------------------------- 作りの確かめ
def construction(C):
    Md = C["M_diff"]
    cols = ["A1"] + [colA(s) for s in STEPS] + [colC(s) for s in STEPS]
    ws = common(Md, cols)
    m = set_size(Md, cols, ws)
    out = dict(m=m)
    exp = {}
    for q in ("D_s", "rho_x", "rho_y"):
        X = C[q]
        wq = common(X, cols)
        d = {str(s): paired(X, colC(s), colA(s), wq) for s in STEPS}
        npos = sum(1 for s in STEPS if d[str(s)] is not None and d[str(s)] > 0)
        exp[q] = dict(m=set_size(X, cols, wq), paired_C_minus_A=d,
                      ok=bool(npos >= 3 and d["30"] is not None and d["30"] > 0))
    out["expectation"] = exp
    out["as_expected"] = all(e["ok"] for e in exp.values())
    if m < M_MIN:
        out.update(M_missing=True, passed=False)
        return out
    v = {c: level(Md, c, ws) for c in cols}
    chain = ["A1"] + [colA(s) for s in STEPS]
    mono = sum(1 for a, b in zip(chain[:-1], chain[1:]) if v[a] >= v[b])
    pos1 = v["A1"] > 0 or "m79" in MUT
    i_ok = pos1 and (v["A1"] - v["A30"] >= v["A1"] / 2) and mono >= 3
    ii = {}
    for s in STEPS:
        d = paired(Md, colC(s), colA(s), ws)
        ii[str(s)] = dict(level_C=v[colC(s)], paired_C_minus_A=d,
                          ok=bool((v[colC(s)] > 0 or "m79" in MUT) and d is not None and d > 0))
    ii_ok = sum(1 for s in STEPS if ii[str(s)]["ok"]) >= 3
    out.update(M_missing=False, levels=v, monotone_pairs=mono, i=bool(i_ok), ii=ii, ii_ok=bool(ii_ok), passed=bool(i_ok and ii_ok))
    return out


def type_of(constr_passed, word):
    if not constr_passed:
        return "外れ"
    return TYPE_OF.get(word, "なし")


# ---------------------------------------------------------------- 勧め (1) の境
def classify(a, b):
    if a is None or b is None:
        return "欠け"
    if a > 0 and b > 0:
        return "両方正"
    if a <= 0 and b <= 0:
        return "両方正でない"
    return "混ざる"


def cell_set(V, k):
    G = V["cells"][k]["G"]
    return common(G, ["A1"] + [colA(s) for s in STEPS] + [colC(s) for s in STEPS])


def med_on(V, k, key, col):
    X = V["cells"][k][key]
    ws = cell_set(V, k)
    if ws is None:
        ws = sorted(present(X, col), key=lambda x: int(x))
    xs = [X.get(col, {}).get(w) for w in ws]
    if not xs or any(x is None for x in xs):
        return None
    return med(xs)


def share_pos(V, k, key, col):
    X = V["cells"][k][key]
    ws = cell_set(V, k)
    if ws is None:
        ws = sorted(present(X, col), key=lambda x: int(x))
    xs = [X[col][w] for w in ws if X.get(col, {}).get(w) is not None]
    return float(np.mean([x > 0 for x in xs])) if xs else None


def boundary(V):
    cls = {s: classify(*(med_on(V, k, "C2a", colA(s) if s > 1 else "A1") for k in CELLS)) for s in GRID}
    pos = [s for s in GRID if cls[s] == "両方正"]
    s_star = None
    if pos:
        s0 = min(pos)
        if all(cls[s] == "両方正" for s in GRID if s >= s0) and all(cls[s] in ("両方正でない", "混ざる") for s in GRID if s < s0):
            s_star = s0
    if s_star == 1:
        s_star = None
    out = dict(classes={str(s): cls[s] for s in GRID}, s_star=s_star,
               r1_minus_pool_classes={str(s): classify(*(med_on(V, k, "R1P", colA(s) if s > 1 else "A1") for k in CELLS))
                                      for s in GRID})
    if s_star is not None:
        out["share"] = {k: share_pos(V, k, "C2a", colA(s_star)) for k in CELLS}
        out["mixed_below"] = [s for s in GRID if s < s_star and cls[s] == "混ざる"]
        out["r1p_at_s_star"] = out["r1_minus_pool_classes"][str(s_star)]
        out["colC_at_s_star"] = classify(*(med_on(V, k, "C2a", colC(s_star)) for k in CELLS))
    return out


# ---------------------------------------------------------------- 感度（1 人抜き・区間）
def loo(V, key="G"):
    out = {}
    for k in CELLS:
        G = V["cells"][k][key]
        full, det = g_word(G)
        ws = cell_set(V, k) or []
        same = sum(1 for w in ws if g_word(G, drop=w)[0] == full)
        out[k] = dict(same=same, m=det["m"], threshold=math.ceil(12 * det["m"] / 17))
    return out


def interval(V, seed, ml):
    out = {}
    for k in CELLS:
        G = V["cells"][k]["G"]
        ws = cell_set(V, k) or []
        d = [G["C30"][w] - G["A30"][w] for w in ws]
        rng = np.random.default_rng([seed + 4, 9, int(k)])
        ci = ml.boot_median(d, rng) if d else None
        out[k] = dict(ci=ci, spans_zero=bool(ci is not None and ci[0] <= 0 <= ci[1]))
    return out


# ---------------------------------------------------------------- 英文
def fd(x):
    if x is None:
        return "NA"
    if x == 0:
        return "0"
    return "%.3f" % x if abs(x) >= 0.001 else "%.1e" % x


def fr(x):
    return "NA" if x is None else "%.2f" % x


def two(f, a, b):
    return "%s / %s" % (f(a), f(b))


def join_s(ss):
    ss = [str(s) for s in ss]
    return ss[0] if len(ss) == 1 else ", ".join(ss[:-1]) + " and " + ss[-1]


FIRST_TWO = ("In unsmoothed symbols, we compared the same number of symbols taken either at a coarser step or from a contiguous stretch "
             "at the 1-second step, with the step (window overlap, prediction horizon and time covered by the same number of symbols, "
             "not separated); this was not checked in the smoothed symbols of the main analysis, and the construction check (lag-1 "
             "mutual information minus that of shuffled symbols) only checks that the step changed the dependence of consecutive "
             "symbols, not that the independent information was matched. The reading rules were not checked on synthetic data.")
INS_136 = ", except the comparison of steps in Section X, which uses unsmoothed symbols"
INS_337 = "; a 10-second step was among those we varied in unsmoothed symbols (Section X), but other parts of their symbolization differ"
ABSTRACT_OLD = "the second smoothing variant, these synthetic writers and wider candidate grids were added after seeing results"
ABSTRACT_NEW = ("the second smoothing variant, these synthetic writers, wider candidate grids and a comparison of steps in unsmoothed "
                "symbols were added after seeing results")
DISC_OLD = ("The weak comparison is likely not specific to keystrokes: features computed over overlapping windows make consecutive "
            "inputs dependent, and a shared model whose structure misses that dependence makes a per-person fit look good. "
            "We have not checked this in other domains.")
WHICH_DEL = ", which may also reflect the smaller amount of data"


def result_sentence(t, g, wc):
    sh, st, ph = g["shrink30"], g["stay30"], g["phi30"]
    if t == "1":
        s = ("In unsmoothed symbols, against the median shrinkage of the gain between the 1-second step and non-overlapping windows "
             "(%s), the median paired difference between the same number of symbols from a contiguous stretch at the 1-second step "
             "and the non-overlapping windows was %s (ratio %s), with the step's components not separated; the same number of "
             "symbols did not carry the same independent information." % (sh, st, ph))
        if "m82" in MUT:
            s = s.replace("; the same number of symbols did not carry the same independent information.", ".")
        return s
    if t == "2":
        return ("In unsmoothed symbols, the median paired difference between the same number of symbols from a contiguous stretch "
                "at the 1-second step and the non-overlapping windows was %s, small against the median shrinkage of %s (ratio %s), "
                "with the step's components not separated; the same number of symbols did not carry the same independent "
                "information, and a per-person fit may learn little from such a short stretch." % (st, sh, ph))
    if t == "3":
        return ("In unsmoothed symbols, the median paired difference between the same number of symbols from a contiguous stretch "
                "at the 1-second step and the non-overlapping windows was %s, below zero (ratio %s to the median shrinkage of %s), "
                "with the step's components not separated; the same number of symbols did not carry the same independent "
                "information, and a per-person fit may learn little from such a short stretch." % (st, ph, sh))
    if t == "なし":
        return ("In unsmoothed symbols, the comparison at an equal number of symbols, with the step's components not separated, "
                "did not settle (%s)." % W_EN[wc])
    return ("In unsmoothed symbols, changing the step (window overlap, prediction horizon and time covered by the same number of "
            "symbols, not separated) did not meet the prespecified construction check (lag-1 mutual information minus that of "
            "shuffled symbols), so no type is assigned (values in Supplement S<n>).")


def discussion(t):
    return {
        "1": ("In unsmoothed symbols and in this comparison, a median paired difference in the same-structure gain remained at an "
              "equal number of symbols when the step differed (window overlap, prediction horizon and time covered by the same "
              "number of symbols, not separated), although the same number of symbols did not carry the same independent "
              "information; the step boundary for recommendation (1) is given in Section X. We have not checked this pattern in "
              "other domains."),
        "2": ("In unsmoothed symbols, at an equal number of symbols, the median paired difference in the same-structure gain between "
              "the 1-second step and non-overlapping windows was small against their shrinkage, with the step's components not "
              "separated and the same number of symbols not carrying the same independent information. We had guessed that the "
              "step, rather than the number of symbols, drives this shrinkage; in this comparison, the prediction that a gap remains "
              "at an equal number of symbols was not supported."),
        "3": ("In unsmoothed symbols, at an equal number of symbols, the median paired difference in the same-structure gain between "
              "the 1-second step and non-overlapping windows was below zero, with the step's components not separated and the same "
              "number of symbols not carrying the same independent information. We had guessed that the step, rather than the "
              "number of symbols, drives this shrinkage; in this comparison, the prediction that a gap remains at an equal number of "
              "symbols was not supported."),
        "なし": ("In unsmoothed symbols, the comparison at an equal number of symbols, with the step's components not separated, did "
                "not settle. We had guessed that the step, rather than the number of symbols, drives this shrinkage, and have not "
                "checked it."),
        "外れ": ("In unsmoothed symbols, changing the step did not meet the prespecified construction check, so the comparison at an "
                "equal number of symbols, with the step's components not separated, was not read. We had guessed that the step, "
                "rather than the number of symbols, drives this shrinkage, and have not checked it."),
    }[t]


def main_223(t, g):
    st, ph = g["stay30"], g["phi30"]
    if t == "1":
        return ("In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired "
                "difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch "
                "at the 1-second step and the non-overlapping windows was %s (ratio %s to the shrinkage), although the same number "
                "of symbols did not carry the same independent information (Section X)." % (st, ph))
    if t == "2":
        return ("In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired "
                "difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch "
                "at the 1-second step and the non-overlapping windows was small against the shrinkage (ratio %s), and the same "
                "number of symbols did not carry the same independent information (Section X)." % ph)
    if t == "3":
        return ("In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired "
                "difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch "
                "at the 1-second step and the non-overlapping windows was below zero (ratio %s), and the same number of symbols did "
                "not carry the same independent information (Section X)." % ph)
    return ("In unsmoothed symbols, a comparison of the per-person gain at an equal number of symbols, with the step's components "
            "not separated, did not settle whether the smaller number of symbols goes with that shrinkage (Section X).")


def contribution(t):
    if t == "1":
        return ("An added comparison in unsmoothed symbols, conditioned on the known ends and with the step's components not "
                "separated, found in this comparison a median paired difference in the same-structure gain between steps at an "
                "equal number of symbols, which did not carry the same independent information (Section X).")
    if t in ("2", "3"):
        return ("In an added comparison in unsmoothed symbols, conditioned on the known ends and with the step's components not "
                "separated, the prediction that a difference in the same-structure gain between steps remains at an equal number of "
                "symbols was not supported; the same number of symbols did not carry the same independent information (Section X).")
    return "An added comparison in unsmoothed symbols, with the step's components not separated, did not settle this (Section X)."


COLC_PRE = ("In unsmoothed symbols, in the comparison at an equal number of symbols from a contiguous stretch at the 1-second step, "
            "with the step's components not separated and the same number of symbols not carrying the same independent information, ")


def boundary_sentences(B):
    """返り値: (列 A の部分の文の list, 列 C の部分の文 か None)。"""
    if B["s_star"] is None:
        return (["In unsmoothed symbols, no grid step separated the steps at which the median difference favoured the per-person "
                 "HMM over the own chain in both cells (Supplement S<n>)."], None)
    s = B["s_star"]
    a = ["In unsmoothed symbols, when symbols were made from the same recording time at a grid step of %d s or longer (fewer "
         "symbols at longer steps), the median difference favoured the per-person HMM over the person's own first-order chain in "
         "both cells (share of writers favouring the per-person HMM at %d s: %s and %s, k = 5 / k = 15); at every shorter grid "
         "step it did not favour the per-person HMM in both cells at once, and both ends of this grid (1 s and 30 s) were known "
         "before the check." % (s, s, fr(B["share"]["5"]), fr(B["share"]["15"]))]
    if B["mixed_below"]:
        a.append("(At %s s it favoured the per-person HMM in one cell only.)" % join_s(B["mixed_below"]))
    r = B["r1p_at_s_star"]
    if r == "両方正でない":
        a.append("At that step the median difference also favoured the shared HMM over the own chain in both cells.")
    elif r == "両方正":
        a.append("At that step the median difference still favoured the own chain over the shared HMM in both cells.")
    else:
        a.append("At that step the own chain against the shared HMM differed between cells.")
    c = B["colC_at_s_star"]
    tail = {"両方正": "the median difference also favoured the per-person HMM in both cells.",
            "両方正でない": "the median difference did not favour the per-person HMM in both cells at once."}.get(
        c, "the two cells disagreed.")
    return a, COLC_PRE + tail


def reservations(lo, iv, wc, w_nohead, w_t10000):
    out = ["(Same word in %d of %d and %d of %d leave-one-writer-out medians, k = 5 / k = 15; the scores were not refitted.)"
           % (lo["5"]["same"], lo["5"]["m"], lo["15"]["same"], lo["15"]["m"])]
    if any(lo[k]["same"] < lo[k]["threshold"] for k in CELLS):
        out.append("(The word is unstable when one writer is left out.)")
    if any(iv[k]["spans_zero"] for k in CELLS):
        out.append("(The interval spans zero in at least one cell.)")
    if w_nohead != wc:
        out.append("(Without the first symbol of each sequence the word is: %s.)" % W_EN[w_nohead])
    if w_t10000 != wc:
        out.append("(With τ fixed at 10,000 the word is: %s.)" % W_EN[w_t10000])
    return out


def after_result(t, D):
    out = ["(The contiguous stretch at the 30-second step lasts %s s in the median.)" % (
        "NA" if D["stretch_C30_sec"] is None else "%d" % round(D["stretch_C30_sec"]))]
    w, wt, h = D["w_ar3"], D["w_ar3_t10000"], D["w_hmm3"]
    out.append("With the structure fixed at the three-state AR-HMM, the per-person data carried a median weight of %s and %s in the "
               "30-second columns with τ chosen on others (%s and %s at τ = 10,000), and for the three-state HMM that decides the "
               "type %s and %s (k = 5 / k = 15); because a small weight can make the comparison with the fixed AR-HMM uninformative "
               "at so few symbols, this study does not judge whether the gap vanishes against a shared structure that can carry the "
               "dependence (values in Supplement S<n>)."
               % (two(fd, w["A30"]["5"], w["A30"]["15"]), two(fd, w["C30"]["5"], w["C30"]["15"]),
                  two(fd, wt["A30"]["5"], wt["A30"]["15"]), two(fd, wt["C30"]["5"], wt["C30"]["15"]),
                  two(fd, h["A30"]["5"], h["A30"]["15"]), two(fd, h["C30"]["5"], h["C30"]["15"])))
    if t == "1":
        r = D["resid_diff"]
        out.append("Values only, not read: the lag-1 autocorrelation of residuals, per-person HMM minus shared HMM (median), was x %s "
                   "and y %s at the 1-second step and x %s and y %s at the 30-second contiguous stretch."
                   % (two(fd, r["A1"]["5"]["x"], r["A1"]["15"]["x"]), two(fd, r["A1"]["5"]["y"], r["A1"]["15"]["y"]),
                      two(fd, r["C30"]["5"]["x"], r["C30"]["15"]["x"]), two(fd, r["C30"]["5"]["y"], r["C30"]["15"]["y"])))
    return out


def assemble(V, seed, ml):
    wc, gw = cell_words(V)
    con = construction(V["constr"])
    t = type_of(con["passed"], wc)
    g = dict(shrink30=two(fd, gw["5"][1].get("shrink", {}).get("30"), gw["15"][1].get("shrink", {}).get("30")),
             stay30=two(fd, gw["5"][1].get("stay", {}).get("30"), gw["15"][1].get("stay", {}).get("30")),
             phi30=two(fr, gw["5"][1].get("phi", {}).get("30"), gw["15"][1].get("phi", {}).get("30")))
    lo = loo(V)
    iv = interval(V, seed, ml)
    w_nh, _ = cell_words(V, "G_nohead")
    w_t4, _ = cell_words(V, "G_t10000")
    w_p1, _ = cell_words(V, prefix="P1-")
    w_p3, _ = cell_words(V, prefix="P3-")
    B = boundary(V)
    resv = reservations(lo, iv, wc, w_nh, w_t4) if t != "外れ" else []
    res_s = result_sentence(t, g, wc)
    S = dict(new_section_first_two=FIRST_TWO, new_section_result=res_s,
             new_section_result_reservations=resv if t != "外れ" else [],
             new_section_after_result=after_result(t, V["desc"]) if t != "外れ" else [],
             discussion_replace=dict(old=DISC_OLD, new=discussion(t)),
             main_223=dict(delete=WHICH_DEL, add=main_223(t, g)),
             main_223_reservations=resv if t in ("1", "2", "3") and "m83" not in MUT else [],
             contribution_add=contribution(t),
             contribution_reservations=resv if t in ("1", "2", "3") and "m83" not in MUT else [],
             main_136_insert=INS_136, main_337_insert=INS_337, abstract_replace=dict(old=ABSTRACT_OLD, new=ABSTRACT_NEW))
    ba, bc = boundary_sentences(B)
    S["recommendation1_boundary_colA"] = ba
    S["recommendation1_boundary_colC"] = bc
    notes = []
    if w_p1 != wc or w_p3 != wc:
        notes.append("The word changes with the position of the stretch: %s (first quarter) and %s (third quarter)."
                     % (W_EN[w_p1], W_EN[w_p3]))
    if not con["as_expected"]:
        notes.append("The shared-structure deficit or the residual autocorrelation did not follow the expected direction.")
    S["supplement_notes"] = notes
    return dict(word=wc, word_en=W_EN[wc], cells={k: dict(word=gw[k][0], **gw[k][1]) for k in CELLS},
                construction=con, type=t, type_name=TYPE_NAME[t], loo=lo, interval=iv,
                word_nohead=w_nh, word_tau10000=w_t4, word_C1=w_p1, word_C3=w_p3, boundary=B, sentences=S)
