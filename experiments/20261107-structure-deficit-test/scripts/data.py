"""データの読み込み・問い・特徴・分け方（design §1・§2・§4.1）。値を出さない。

単位（unit）は dict:
  seqs   EM の系列（記号の配列のリスト・CoAuthor は 1 本・CS1 はまとまりごと）
  pflag  各系列の各記号の「窓 [t − 31, t − 1] に押下が 1 つ以上あるか」（EM の副の平均に使う）
  probes 主の問い（dict: tab・recal・y）・probes_all 副の問い（CS1 だけ・押下の限りを外した版）
  start  並べの鍵（CoAuthor は観測区間の始まり・CS1 は課題の最初の押下）
CoAuthor は B と同じ（観測区間が 1 本のセッション・問いは 1 セッション 3 回まで・ラベルは suggestion-get）。
CS1 は課題（まとまりごとの系列・問いはまとまりごとに上限なし・ラベルは lookup-accept）。
変異の切り替え（MUT）は ml.py が設定する。m9: CS1 の問いの押下の限りを外す。

structure-deficit-test（conditions D1）: 単位に rows（系列ごとの [ewma_x, ewma_y, obs] の配列）を足す。
variant() が列 q（q × q + 1 記号）と順（o そのまま・p 並べ替え）の seqs・pflag を rows から作り直す。
m31: 上の端を min(q) にする・m32: obs = 25 を格子の記号として扱う・m33: 系列をまたいで並べ替える・
m34: 評価の単位を並べ替えない（variant の呼び出しで評価の単位を知らせる）。
"""
import glob
import json
import math
import os

import numpy as np

WIN_START, WIN_END = 31_000, 1_000
LABEL_MS = 60_000
GAP_MS = 6 * 60_000
MUT = set()


# ---------------------------------------------------------------- 問い
def subtract(allowed, lo, hi):
    out = []
    for x, y in allowed:
        if y <= lo or x >= hi:
            out.append((x, y))
        else:
            if x < lo:
                out.append((x, lo))
            if y > hi:
                out.append((hi, y))
    return [(x, y) for x, y in out if y > x]


def draw_probes(rng, allowed, max_probes=None):
    """許される区間の和集合から一様に引き、引いた時刻の前後 6 分を外して続ける（B の draw_probes を区間の和集合に広げた）。"""
    allowed = [(x, y) for x, y in allowed if y > x]
    out = []
    while allowed and (max_probes is None or len(out) < max_probes):
        lens = np.array([y - x for x, y in allowed], dtype=np.float64)
        u = rng.uniform(0, lens.sum())
        i = min(int(np.searchsorted(np.cumsum(lens), u, side="right")), len(allowed) - 1)
        x, y = allowed[i]
        t = min(max(int(x + (u - (lens[:i].sum()))), x), y)
        out.append(t)
        allowed = subtract(allowed, t - GAP_MS, t + GAP_MS)
    return sorted(out)


def press_union(keys, a, b):
    """[a, b] と、各押下 p の (p + 1 秒, p + 31 秒] の和集合の共通部分（端は整数 ms で (p + 1000, p + 31000] → [p + 1001, p + 31000]）。"""
    iv = []
    for p in keys:
        x, y = max(int(p) + WIN_END + 1, a), min(int(p) + WIN_START, b)
        if y >= x:
            if iv and x <= iv[-1][1]:
                iv[-1] = (iv[-1][0], max(iv[-1][1], y))
            else:
                iv.append((x, y))
    return iv


def tab_features(keys, bs, ft, ps, ex, t):
    """窓 [t − 31, t − 1) の押下数・backspace の数・押下の間の最長の間隔（秒・2 未満なら 30）・t − 1 秒以前の最後の feat 行の p_stuck・ewma_x。
    t − 1 秒以前に feat 行が無ければ None（B は行 0 を使っていた・判断 11 の直し）。"""
    w0, w1 = t - WIN_START, t - WIN_END
    k = keys[(keys >= w0) & (keys < w1)]
    nb = int(((bs >= w0) & (bs < w1)).sum())
    gap = float(np.diff(k).max()) / 1000.0 if len(k) >= 2 else 30.0
    j = int(np.searchsorted(ft, w1, side="right")) - 1
    if j < 0:
        return None
    return [float(len(k)), float(nb), gap, float(ps[j]), float(ex[j])], j


def make_probe(keys, bs, ft, ps, ex, labels, t):
    r = tab_features(keys, bs, ft, ps, ex, t)
    if r is None:
        return None
    tab, j = r
    if any(not math.isfinite(v) for v in tab):
        return None
    pj = min(max(ps[j], 1e-6), 1 - 1e-6)
    y = int(((labels > t) & (labels <= t + LABEL_MS)).any())
    return dict(t=int(t), tab=tab, recal=[float(math.log(pj / (1 - pj)))], y=y)


def press_flags(ft, keys):
    """各 feat 行の時刻 t について、窓 [t − 31, t − 1) に押下が 1 つ以上あるか。"""
    lo = np.searchsorted(keys, ft - WIN_START, side="left")
    hi = np.searchsorted(keys, ft - WIN_END, side="left")
    return hi > lo


def cs1_probe_times(rng, keys, a, b, restrict):
    """CS1 のまとまり [a, b] の問いの時刻。[a + 31 秒, b − 60 秒] から 6 分空けで上限なし。
    restrict（主）は窓 [t − 31, t − 1) に押下が 1 つ以上ある時刻に限る（m9 は限りを外す）。"""
    allowed = [(a + WIN_START, b - LABEL_MS)]
    if restrict and "m9" not in MUT:
        allowed = press_union(keys, a + WIN_START, b - LABEL_MS)
    return draw_probes(rng, allowed)


# ---------------------------------------------------------------- CoAuthor（B の load と同じ選び）
def load_coauthor(work, seed):
    s2w = json.load(open(os.path.join(work, "sessions.json")))
    by_w = {}
    stats = dict(probes_dropped=0)
    for f in sorted(glob.glob(os.path.join(work, "s[0-9]*.json"))):
        sid = os.path.basename(f)[1:-5]
        if sid not in s2w:
            continue
        d = json.load(open(f))
        if len(d["observed_intervals"]) != 1:
            continue
        a, b = d["observed_intervals"][0]
        if not d["feat"]:
            stats["units_without_feat"] = stats.get("units_without_feat", 0) + 1
            continue
        F = np.array([r[:7] for r in d["feat"]], dtype=np.float64)
        keys = np.sort(np.array([k[0] for k in d["keys"]], dtype=np.int64))
        bs = np.sort(np.array([k[0] for k in d["keys"] if k[1] == "backspace"], dtype=np.int64))
        gets = np.sort(np.array([e[0] for e in d["events"] if e[1] == "suggestion-get"], dtype=np.int64))
        ft, ps, ex, obs = F[:, 0], F[:, 3], F[:, 4], F[:, 6].astype(np.int64)
        rows = F[:, 4:7].copy()
        rng = np.random.default_rng([seed, int(sid)])
        probes = []
        for t in draw_probes(rng, [(a + WIN_START, b - LABEL_MS)], max_probes=3):
            p = make_probe(keys, bs, ft, ps, ex, gets, t)
            if p is None:
                stats["probes_dropped"] += 1
            else:
                probes.append(p)
        by_w.setdefault(s2w[sid], []).append(dict(start=a, seqs=[obs], pflag=[press_flags(ft, keys)], rows=[rows],
                                                  probes=probes, probes_all=probes))
    writers = [sorted(by_w[w], key=lambda u: u["start"]) for w in sorted(by_w)]
    check_units(writers, stats)
    return writers, stats


# ---------------------------------------------------------------- CS1 2021
def load_cs1(work, seed, probe_unit):
    """probe_unit: "block"（まとまり [最初の押下, 最後の押下]）か "interval"（replay の観測区間）。"""
    u2w = json.load(open(os.path.join(work, "units.json")))
    by_w = {}
    stats = dict(probes_dropped=0, probes_dropped_all=0)
    for uid in sorted(u2w):
        d = json.load(open(os.path.join(work, "u%s.json" % uid)))
        if not d["feat"]:
            stats["units_without_feat"] = stats.get("units_without_feat", 0) + 1
            continue
        F = np.array([r[:7] for r in d["feat"]], dtype=np.float64)
        keys = np.sort(np.array([k[0] for k in d["keys"]], dtype=np.int64))
        bs = np.sort(np.array([k[0] for k in d["keys"] if k[1] == "backspace"], dtype=np.int64))
        acc = np.sort(np.array([e[0] for e in d["events"] if e[1] == "lookup-accept"], dtype=np.int64))
        ft, ps, ex, obs = F[:, 0], F[:, 3], F[:, 4], F[:, 6].astype(np.int64)
        blocks = sorted(d["blocks"])
        # EM の系列: feat 行をまとまりに割る（行の時刻がそのまとまりの始まり以上・次のまとまりの始まり未満）
        starts = np.array([b[0] for b in blocks] + [np.iinfo(np.int64).max], dtype=np.int64)
        bi = np.searchsorted(starts, ft, side="right") - 1
        pf = press_flags(ft, keys)
        seqs, pflag, rows = [], [], []
        for i in range(len(blocks)):
            m = bi == i
            if m.sum() > 0:
                seqs.append(obs[m])
                pflag.append(pf[m])
                rows.append(F[m, 4:7].copy())
        spans = blocks if probe_unit == "block" else sorted(d["observed_intervals"])
        probes, probes_all = [], []
        for bi_, (a, b) in enumerate(spans):
            for restrict, out, key in ((True, probes, "probes_dropped"), (False, probes_all, "probes_dropped_all")):
                rng = np.random.default_rng([seed, int(uid), bi_, int(restrict)])
                for t in cs1_probe_times(rng, keys, a, b, restrict):
                    p = make_probe(keys, bs, ft, ps, ex, acc, t)
                    if p is None:
                        stats[key] += 1
                    else:
                        out.append(p)
        by_w.setdefault(u2w[uid], []).append(dict(start=int(keys[0]), seqs=seqs, pflag=pflag, rows=rows,
                                                 probes=probes, probes_all=probes_all))
    writers = [sorted(by_w[w], key=lambda u: u["start"]) for w in sorted(by_w)]
    check_units(writers, stats)
    return writers, stats


def check_units(writers, stats):
    """feat 行の無い単位・空の系列の単位があれば、件数だけを出して先に止める（本計算の途中で落ちないように）。"""
    empty = sum(1 for ss in writers for u in ss if not any(len(s) for s in u["seqs"]))
    if stats.get("units_without_feat") or empty:
        raise SystemExit("feat 行の無い単位 %d 件・系列が空の単位 %d 件" % (stats.get("units_without_feat", 0), empty))


# ---------------------------------------------------------------- 分け方（design §2）
def split(n, k, H, mut=None):
    """評価 = 後ろの H 単位、学習 = 評価の直前の k 単位。m6 は学習に評価の 1 単位を混ぜる。"""
    mut = MUT if mut is None else mut
    test = list(range(n - H, n))
    train = list(range(n - H - k, n - H))
    if "m6" in mut:
        train = train[1:] + [test[0]]
    return train, test


def folds(train, mut=None):
    """本人の中の時間順の折り目（k ≥ 3）: F1 = (u_1…u_{k−1} → u_k)、F2 = (u_1…u_{k−2} → u_{k−1})。m7 は F1 の評価を当てはめより前にする。"""
    mut = MUT if mut is None else mut
    if len(train) < 3:
        return []
    f1 = (train[:-1], [train[-1]])
    if "m7" in mut:
        f1 = (train[1:], [train[0]])
    return [f1, (train[:-2], [train[-2]])]


def check_split(n, k, H):
    tr, te = split(n, k, H)
    ok = len(set(tr) & set(te)) == 0 and min(te) > max(tr) and len(tr) == k and len(te) == H
    for fit, ev in folds(tr):
        ok = ok and max(fit) < min(ev) and set(fit) <= set(tr) and set(ev) <= set(tr)
    return ok


# ---------------------------------------------------------------- 量子化の列と並べ替え（conditions D1・structure-deficit-test）
PENALTY = 25  # engine.rs の backspace 連打の記号


def axis_bin(v, q):
    """engine.rs の (x * 5.0).floor().min(4.0) as usize を q に一般化（負は 0 に飽和・Rust の float → usize の cast）。
    NaN は quantize が先に止める（Rust の f64::min(NaN, 4.0) は 4.0 を返すが、numpy は NaN を運ぶ）。
    m31 は上の端を q にする（q の記号がはみ出す）。"""
    b = np.floor(np.asarray(v, dtype=np.float64) * q)
    b = np.minimum(b, q if "m31" in MUT else q - 1)
    b = np.maximum(b, 0)
    return b.astype(np.int64)


def quantize(rows, q):
    """rows（n × 3: ewma_x・ewma_y・obs）→ 記号（0〜q²）。obs = 25 は q²（m32 は格子の記号のまま）。"""
    rows = np.asarray(rows, dtype=np.float64)
    if np.isnan(rows).any():
        raise ValueError("feat 行の ewma か obs に NaN がある（件数だけを報告する）")  # Rust と numpy で扱いが違うので止める
    sym = axis_bin(rows[:, 0], q) * q + axis_bin(rows[:, 1], q)
    if "m32" not in MUT:
        sym = np.where(rows[:, 2].astype(np.int64) == PENALTY, q * q, sym)
    return sym.astype(np.int64)


def shuffle_rng(seed, ds_no, wi, ui, si):
    return np.random.default_rng([seed + 41, ds_no, wi, ui, si])


def variant(writers, q, order, seed, ds_no, H_):
    """列 q・順 order（"o" / "p"）の単位の並び（writers と同じ形・seqs と pflag を作り直す・rows は残す）。
    並べ替えは系列ごとに行の番号に当て（記号と pflag が行といっしょに動く）、その後で記号を作るので 3 列で同じ並べ替え。
    乱数は [SEED + 41, データの番号, 書き手の通し番号, 単位の番号, 系列の番号]（EM の乱数とは別）。
    m33 は単位の系列をつないで並べ替えてから元の長さで切り直す（系列をまたぐ）。m34 は評価の単位（後ろの H_ 単位）を並べ替えない。"""
    out = []
    for wi, ss in enumerate(writers):
        nu = []
        for ui, u in enumerate(ss):
            is_eval = ui >= len(ss) - H_
            seqs, pflag = [], []
            if order == "p" and not (is_eval and "m34" in MUT):
                if "m33" in MUT:
                    allr = np.concatenate(u["rows"])
                    allf = np.concatenate([np.asarray(f) for f in u["pflag"]])
                    perm = shuffle_rng(seed, ds_no, wi, ui, 0).permutation(len(allr))
                    allr, allf = allr[perm], allf[perm]
                    cut = np.cumsum([len(r) for r in u["rows"]])[:-1]
                    parts = list(zip(np.split(allr, cut), np.split(allf, cut)))
                else:
                    parts = []
                    for si, (r, f) in enumerate(zip(u["rows"], u["pflag"])):
                        perm = shuffle_rng(seed, ds_no, wi, ui, si).permutation(len(r))
                        parts.append((r[perm], np.asarray(f)[perm]))
            else:
                parts = [(r, np.asarray(f)) for r, f in zip(u["rows"], u["pflag"])]
            for r, f in parts:
                seqs.append(quantize(r, q))
                pflag.append(f)
            nu.append(dict(u, seqs=seqs, pflag=pflag))
        out.append(nu)
    return out


def q_gate(writers):
    """P-Q: q = 5 で作り直した記号が、全行で中間の obs と一致するか。返り値: (行の数, 外れた行の数)。"""
    n = bad = 0
    for ss in writers:
        for u in ss:
            for r, s in zip(u["rows"], u["seqs"]):
                n += len(r)
                bad += int((quantize(r, 5) != np.asarray(s)).sum())
    return n, bad
