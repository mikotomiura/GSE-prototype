"""The person-world checks: (5) re-identification of a person from a stage's drawing, (6) a per-person reader against a
common reader, the raw-keystroke attacker (PC-raw), the oracle, the descriptions and the calibration of k.

Design: .steering/20261123-rhythm-stage-person-world/design.md 1.5-1.8, 3.0-3.4. The window tables, the stage and the
verdict rule are the earlier task's and are imported, not rewritten: baseline.tables / checks.label_tables (the L300
rows), stage.series (the drawing and the controls), checks.judge (the verdict; the new names are mapped to the old
roles on the way in and back on the way out: to_old / from_old).

Sections: names and roles; summaries (R1: a closed input); the raw-keystroke attacker; pairs and folds; (5) fits, gains,
bootstrap and null; (6) readers; the oracle and the descriptions; the calibration of k and the pilot's choices; the
modes (--ceiling, --pilot-k, --pilot, --apply-pilot, --run for the smoke and the main run).

Usage (run.sh calls it):
  person.py --ceiling <config> <SEED file> <work> <out dir> --step S [--jobs N]
  person.py --pilot-k <config> <SEED file> <out dir> --step S [--jobs N]
  person.py --pilot   <config> <SEED file> <work> <out dir> --step S [--jobs N]
  person.py --apply-pilot <config> <step> [--what k|lam]
  person.py --run     <config> <SEED file> <work> <out dir> --step S [--smoke] [--jobs N]
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import shutil
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import baseline as bl
import checks as ck
import gen_sessions as gs
import stage as st

KINDS = ck.KINDS
FSETS = ck.FSETS
ATTACKERS = ck.ATTACKERS
BASES = ck.BASES
BASE_NAME = ck.BASE_NAME
VAR = "~ws"  # the suffix of the variant without the smoothness features (design 1.4)
A_COLS = 11  # model A's window quantities (A_NAMES); the L300 table's first 15 columns are these and the span's four
WS_LO, WS_HI = 15, 28  # A_speed's 13 window quantities (WS_NAMES) in the L300 A_speed table


def clean(o):
    return ck.clean(o)


def dump(path: Path, obj) -> None:
    ck.dump(path, obj)


# ---------------------------------------------------------------------------
# Seeds and the fingerprints
# ---------------------------------------------------------------------------

SEED_MODE = {"main": "main", "pilot": "pilot", "pilot-k": "kgrid", "ceiling": "ceiling", "smoke": "smoke"}


def run_seed(mode: str, base_seed: int, cfg: dict) -> int:
    """design 1.3: the seed of a mode (the k grid and the pilots are not the main run's seed). A seam for the mutant."""
    return base_seed + int(cfg["person"]["seed_offsets"][SEED_MODE[mode]])


def cfg_fingerprint(cfg: dict) -> str:
    """The SHA-256 of config.json without the _ keys and without what the pilots write (pc_person.lam, pc_pers.lam,
    person.k)."""
    c = json.loads(json.dumps(cfg))

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if not k.startswith("_")}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o

    c = strip(c)
    c["pc_person"] = {k: v for k, v in c["pc_person"].items() if k != "lam"}
    c["pc_pers"] = {k: v for k, v in c["pc_pers"].items() if k != "lam"}
    c["person"] = {k: v for k, v in c["person"].items() if k != "k"}
    c["pc_stall"] = {k: v for k, v in c["pc_stall"].items() if k != "lam"}
    return hashlib.sha256(json.dumps(c, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def code_fingerprint() -> str:
    h = hashlib.sha256()
    here = Path(__file__).resolve().parent
    for f in sorted(here.glob("*.py")) + [here.parent / "run.sh"]:
        h.update(f.name.encode() + b"\0" + f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Names and roles (design 1.5, 1.8; the verdict is checks.judge)
# ---------------------------------------------------------------------------

ROLES = {"id": (("pc1", "PC1-id"), ("pcs", "PCp-"), ("pc0", "PC0-id-")),
         "pers": (("pc1", "PC1-pers"), ("pcs", "PCps-"), ("pc0", "PC0p-"))}
OLD_NAME = {"pc1": "PC1", "pcs": "PCs-", "pc0": "PC0-"}


def role_prefixes(q: str) -> dict:
    """The name (or name prefix) of each role in the question q ("id" = (5), "pers" = (6)); a seam for the mutant."""
    return dict(ROLES[q])


def to_old(q: str, name: str) -> str:
    pre = role_prefixes(q)
    if name == pre["pc1"]:
        return OLD_NAME["pc1"]
    for role in ("pcs", "pc0"):
        if name.startswith(pre[role]):
            return OLD_NAME[role] + name[len(pre[role]):]
    return name


def from_old(q: str, name: str) -> str:
    pre = role_prefixes(q)
    if name == OLD_NAME["pc1"]:
        return pre["pc1"]
    for role in ("pcs", "pc0"):
        if name.startswith(OLD_NAME[role]):
            return pre[role] + name[len(OLD_NAME[role]):]
    return name


def judge_q(q: str, attk: dict, nulls: dict | None, auc_s: dict | None, cands: list[str], cfg: dict, fit_failed: bool,
            forced: str | None = None) -> dict:
    """checks.judge on names mapped to the old roles, the answer mapped back. weak_stall_pc is weak_person_pc here."""
    a2 = {to_old(q, n): v for n, v in attk.items()}
    n2 = None if nulls is None else {to_old(q, n): v for n, v in nulls.items()}
    r = ck.judge(a2, n2, auc_s, cands, cfg, fit_failed, forced=forced)

    def back(d):
        return None if d is None else {from_old(q, k): v for k, v in d.items()}

    for c, d in r["detector"].items():
        d["reasons"] = ["weak_person_pc" if x == "weak_stall_pc" else x for x in d["reasons"]]
    r["maxima"], r["null95"], r["verdicts"] = back(r["maxima"]), back(r["null95"]), back(r["verdicts"])
    return r


TRUNC_DECLARE = 0.10  # design 3.3 (b): the share of sessions with a cut dimension above which the world is declared cut


def variant_name(c: str) -> str:
    return c + VAR


def variant_record(parent: dict, var: dict, parent_verdict: str, auc_s: dict | None, cfg: dict) -> dict:
    """design 3.3 (c), fixed before the results (cross-review 2): the variant is read on the same attackers as the
    parent's verdict (the non-ceiling ones), by their maxima. One reading only: the parent red_detected and the variant's
    upper_max below the margin -> "smooth_path"; anything else (a bound across the margin, NaN, the parent not red)
    -> "not_read". There is no reading of the lower bound (the variant has no null of its own)."""
    use = [a for a in ck.ATTACKERS if a.split("/")[1] not in ck.ceiling_kinds(auc_s, cfg)]
    mx = ck.maxima(var, use)
    red = parent_verdict == "red_detected"  # the confirmed red only (not red_unconfirmed, not the stop path)
    smooth = red and bool(np.isfinite(mx["upper_max"]) and mx["upper_max"] < cfg["e13"]["margin"])
    return {"parent": parent, "without_smooth": var, "use": use, "maxima": mx,
            "reading": "smooth_path" if smooth else "not_read"}


# ---------------------------------------------------------------------------
# Summaries (design 1.5; R1: a closed input, no person number and no latent value)
# ---------------------------------------------------------------------------

class SummaryInput:
    """The only view of the window table the summaries get: the rows' features F and their session index G."""
    ALLOWED = ("F", "G")

    def __init__(self, F: np.ndarray, G: np.ndarray):
        self._c = {"F": F, "G": G}
        self.read: set = set()

    def __getitem__(self, name: str) -> np.ndarray:
        if name not in self.ALLOWED:
            raise KeyError(f"design 1.5: the summaries do not read {name!r}")
        self.read.add(name)
        return self._c[name]


def summarize(inp: SummaryInput, n_sess: int) -> tuple[np.ndarray, np.ndarray]:
    """The mean and SD (population) of each feature over a session's window rows. NaN for a session with no rows."""
    F, G = np.asarray(inp["F"], dtype=np.float64), np.asarray(inp["G"], dtype=np.int64)
    cnt = np.bincount(G, minlength=n_sess).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.stack([np.bincount(G, weights=F[:, j], minlength=n_sess) / cnt for j in range(F.shape[1])], axis=1)
        dev2 = (F - mean[G]) ** 2
        sd = np.sqrt(np.stack([np.bincount(G, weights=dev2[:, j], minlength=n_sess) / cnt
                               for j in range(F.shape[1])], axis=1))
    return mean, sd


def base_summary(tab: dict, base: str, n_sess: int) -> np.ndarray:
    """A: model A's 11 window quantities (mean, SD) = 22 dims; S: A plus the 13 speed quantities = 48 dims."""
    t = tab[ck.TAG]
    F = t["XA"][:, :A_COLS] if base == "A" else np.hstack([t["XA"][:, :A_COLS], t["XS"][:, WS_LO:WS_HI]])
    m, s = summarize(SummaryInput(F, t["G"]), n_sess)
    return np.hstack([m, s])


def cand_summary(Frows: np.ndarray, G: np.ndarray, n_sess: int, drop: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    F = Frows if drop is None else Frows[:, ck.keep_cols(drop)]
    return summarize(SummaryInput(F, G), n_sess)


def feature_sets(vb: np.ndarray, m: np.ndarray, s: np.ndarray) -> dict:
    """small = the base + the 20 means; full = the base + the means and SDs."""
    return {"small": np.hstack([vb, m]), "full": np.hstack([vb, m, s])}


# ---------------------------------------------------------------------------
# The raw-keystroke attacker PC-raw (design 1.6)
# ---------------------------------------------------------------------------

RAW_NAMES = ("lg_p10", "lg_p50", "lg_p90", "burst_sd", "burst_ac1", "burst_absratio", "share_long", "pause_med",
             "run_n_med", "run_s_med", "keys_per_active_s", "active_share")


def raw_features(presses_ms: np.ndarray, duration_s: int, rc: dict) -> np.ndarray:
    """12 quantities of one session from the press times only (design 1.6; rc: the pc_raw settings of the config)."""
    pm = np.sort(np.asarray(presses_ms, dtype=np.int64))
    out = np.full(12, np.nan)
    iv = np.diff(pm)
    iv = iv[iv > 0].astype(np.float64)
    short, burst, pmax = rc["short_ms"], rc["burst_ms"], rc["pause_max_ms"]
    sh = iv[iv < short]
    if len(sh):
        out[0:3] = np.percentile(np.log(sh), [10, 50, 90])
    d = np.diff(pm).astype(np.float64)
    b = d[(d > 0) & (d < burst)]
    if len(b) > 1:
        out[3] = float(np.std(np.log(b)))
    ok = (d[:-1] > 0) & (d[:-1] < burst) & (d[1:] > 0) & (d[1:] < burst)
    if ok.sum() > 2:
        x, y = np.log(d[:-1][ok]), np.log(d[1:][ok])
        out[4] = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 1e-9 and np.std(y) > 1e-9 else 0.0
        out[5] = float(np.median(np.abs(x - y)))
    if len(iv):
        out[6] = float((iv >= short).mean())
    pau = iv[(iv >= burst) & (iv < pmax)]
    if len(pau):
        out[7] = float(np.median(np.log(pau)))
    if len(pm):  # runs of presses joined by intervals below burst_ms
        cut = np.nonzero(~((d > 0) & (d < burst)))[0] + 1 if len(d) else np.zeros(0, dtype=np.int64)
        starts = np.concatenate([[0], cut]).astype(np.int64)
        ends = np.concatenate([cut, [len(pm)]]).astype(np.int64)
        out[8] = float(np.median(ends - starts))
        out[9] = float(np.median((pm[ends - 1] - pm[starts]) / 1000.0))
        act = len(np.unique(pm // 1000))
        out[10] = len(pm) / act if act else np.nan
        out[11] = act / max(duration_s, 1)
    return out


def raw_matrix(work: Path, sids: list[str], rc: dict) -> np.ndarray:
    rows = []
    for sid in sids:
        lab = np.load(work / "labels" / f"{sid}.npz")
        rows.append(raw_features(lab["presses_ms"], int(lab["duration_s"]), rc))
    return np.stack(rows)


# ---------------------------------------------------------------------------
# Pairs, folds and weights (design 1.5)
# ---------------------------------------------------------------------------

def make_model(kind: str, seed: int):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if kind == "hgb":
        return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, early_stopping=False, random_state=seed)
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=2000))


def fold_of_person(seed: int, n_persons: int, folds: int, tag: str = "folds") -> np.ndarray:
    """A split of the persons into folds (n_persons / folds each) from derive_rng(seed, tag)."""
    perm = gs.derive_rng(seed, tag).permutation(n_persons)
    f = np.empty(n_persons, dtype=np.int64)
    f[perm] = np.arange(n_persons) % folds
    return f


class FoldAuc:
    """The matching AUC as the mean of the validation folds' own AUCs (each fold has its own fitted classifier, so the
    scores of two folds are not on one scale: design 1.5, decisions 10). Called with pair weights (or none)."""

    def __init__(self, score: np.ndarray, y: np.ndarray, pf: np.ndarray):
        self.groups = [(np.nonzero(pf == f)[0]) for f in np.unique(pf)]
        self.preps = [ck.auc_prep(score[g], y[g]) for g in self.groups]
        self.short_calls = 0  # calls where a fold had no defined AUC and was left out of the mean (cross-review 2)

    def __call__(self, w: np.ndarray | None = None) -> float:
        v = [ck.auc_w(p, np.ones(len(g)) if w is None else w[g]) for g, p in zip(self.groups, self.preps)]
        v = [x for x in v if np.isfinite(x)]
        if len(v) < len(self.groups):
            self.short_calls += 1
        return float(np.mean(v)) if v else float("nan")


def fold_auc(score: np.ndarray, y: np.ndarray, pf: np.ndarray) -> FoldAuc:
    """Seam: the per-fold AUC object (the mutant pools the folds' scores)."""
    return FoldAuc(score, y, pf)


def eval_pairs(fold_s: np.ndarray, folds: int) -> tuple[np.ndarray, np.ndarray]:
    """The pairs i < j of sessions inside the same validation fold, fold by fold."""
    I, J = [], []
    for f in range(folds):
        idx = np.nonzero(fold_s == f)[0]
        a, b = np.triu_indices(len(idx), 1)
        I.append(idx[a])
        J.append(idx[b])
    return np.concatenate(I), np.concatenate(J)


def train_sessions(fold_s: np.ndarray, f: int) -> np.ndarray:
    """The sessions the pair classifier of validation fold f learns from: the other folds' persons only (a seam)."""
    return np.nonzero(fold_s != f)[0]


def train_pairs(person: np.ndarray, fold_s: np.ndarray, f: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    tr = train_sessions(fold_s, f)
    a, b = np.triu_indices(len(tr), 1)
    I, J = tr[a], tr[b]
    return I, J, (person[I] == person[J]).astype(np.int64)


def pair_X(Z: np.ndarray, I: np.ndarray, J: np.ndarray) -> np.ndarray:
    return np.hstack([np.abs(Z[I] - Z[J]), (Z[I] + Z[J]) / 2.0])


def pair_scores(V: np.ndarray, person: np.ndarray, fold_s: np.ndarray, kind: str, seed: int, folds: int) -> np.ndarray:
    """The scores of eval_pairs(fold_s): per validation fold, the classifier learned from the other folds' pairs."""
    from threadpoolctl import threadpool_limits

    out = []
    for f in range(folds):
        I, J, y = train_pairs(person, fold_s, f)
        tr = train_sessions(fold_s, f)
        with np.errstate(invalid="ignore"):
            mu, sd = np.nanmean(V[tr], axis=0), np.nanstd(V[tr], axis=0)
        sd = np.where(np.isfinite(sd) & (sd > 0), sd, 1.0)
        Z = (V - mu) / sd
        te = np.nonzero(fold_s == f)[0]
        a, b = np.triu_indices(len(te), 1)
        with threadpool_limits(1):
            model = make_model(kind, seed)
            model.fit(pair_X(Z, I, J), y)
            out.append(model.predict_proba(pair_X(Z, te[a], te[b]))[:, 1])
    return np.concatenate(out)


def pair_weights(m: np.ndarray, pi: np.ndarray, pj: np.ndarray) -> np.ndarray:
    """The weights of a person bootstrap draw (m: how many times each person was drawn): a same-person pair has the
    weight m_p (a repeated person's copies are not paired with each other), a different-person pair m_p m_q."""
    return np.where(pi == pj, m[pi], m[pi] * m[pj])


def boot_counts(seed: int, tag: str, n: int, nboot: int) -> np.ndarray:
    return gs.derive_rng(seed, tag).multinomial(n, np.full(n, 1.0 / n), size=nboot).astype(np.float64)


def permute_persons(seed: int, r: int, n_sess: int, slots: int) -> tuple[np.ndarray, np.ndarray]:
    """Permutation r: the sessions dealt at random into n_sess / slots fake persons of `slots` sessions each (1 person's
    6 sessions are kept together in number, independent of the real persons). Returns (fake person, fake slot)."""
    order = gs.derive_rng(seed, "perm", r).permutation(n_sess)
    person = np.empty(n_sess, dtype=np.int64)
    slot = np.empty(n_sess, dtype=np.int64)
    person[order] = np.arange(n_sess) // slots
    slot[order] = np.arange(n_sess) % slots
    return person, slot


def _pair_task(args: tuple):
    key, V, person, fold_s, kind, seed, folds = args
    return key, pair_scores(V, person, fold_s, kind, seed, folds)


def _map(fn, tasks: list, jobs: int) -> dict:
    if jobs <= 1:
        return dict(fn(t) for t in tasks)
    os.environ["OMP_NUM_THREADS"] = "1"
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        return dict(ex.map(fn, tasks, chunksize=1))


def fit5(mats: dict, vbase: np.ndarray, person: np.ndarray, seed: int, folds: int, jobs: int,
         fold_tag: str = "folds") -> tuple[dict, dict, tuple]:
    """mats: name -> {fs: V}. Returns ({(name, fs, kind): scores}, {kind: base scores}, (I, J, y, fold of each pair))."""
    n_p = int(person.max()) + 1
    fop = fold_of_person(seed, n_p, folds, fold_tag)
    fold_s = fop[person]
    tasks = [(("__base__", "-", k), vbase, person, fold_s, k, seed, folds) for k in KINDS]
    for name, d in mats.items():
        for fs, V in d.items():
            for k in KINDS:
                tasks.append(((name, fs, k), V, person, fold_s, k, seed, folds))
    got = _map(_pair_task, tasks, jobs)
    I, J = eval_pairs(fold_s, folds)
    y = (person[I] == person[J]).astype(np.int64)
    base = {k: got[("__base__", "-", k)] for k in KINDS}
    return {k: v for k, v in got.items() if k[0] != "__base__"}, base, (I, J, y, fold_s[I])


def gain_records(scores: dict, base: dict, pairs: tuple, person: np.ndarray, M: np.ndarray | None) -> tuple[dict, dict]:
    """name -> attacker -> {"gain", "ci95", "auc"} and the base's AUC per kind. M: the bootstrap multiplicities."""
    I, J, y, pf = pairs
    pi, pj = person[I], person[J]
    fa_b = {k: fold_auc(base[k], y, pf) for k in KINDS}
    auc_b = {k: fa_b[k]() for k in KINDS}
    ws = None if M is None else [pair_weights(m, pi, pj) for m in M]
    out: dict = {}
    for (name, fs, k), s in scores.items():
        fa = fold_auc(s, y, pf)
        auc = fa()
        rec = {"gain": auc - auc_b[k], "auc": auc}
        if ws is not None:
            s0 = fa.short_calls
            d = np.array([fa(w) - fa_b[k](w) for w in ws])
            rec["ci95"] = ck.ci95(d)
            rec["boot_short_folds"] = fa.short_calls - s0  # draws whose mean left a fold out (described, not judged)
        out.setdefault(name, {})[f"{fs}/{k}"] = rec
    return out, auc_b


def point_gains(scores: dict, base: dict, pairs: tuple) -> dict:
    """name -> attacker -> gain (no interval): what a permutation records."""
    I, J, y, pf = pairs
    auc_b = {k: fold_auc(base[k], y, pf)() for k in KINDS}
    out: dict = {}
    for (name, fs, k), s in scores.items():
        out.setdefault(name, {})[f"{fs}/{k}"] = fold_auc(s, y, pf)() - auc_b[k]
    return out


def attk_of(rec: dict) -> dict:
    return {n: {a: {"gain": v["gain"], "ci95": v["ci95"]} for a, v in d.items()} for n, d in rec.items()}


def null5(mats: dict, vbase: np.ndarray, n_sess: int, slots: int, seed: int, folds: int, nperm: int, jobs: int) -> dict:
    """The permutations of (5): fake persons (6 sessions kept), the folds and the fits redone; name -> [attacker -> gain]."""
    nulls: dict = {n: [] for n in mats}
    for r in range(nperm):
        fake, _ = permute_persons(seed, r, n_sess, slots)
        sc, base, pairs = fit5(mats, vbase, fake, seed, folds, jobs, fold_tag=f"folds-perm-{r}")
        g = point_gains(sc, base, pairs)
        for n in mats:
            nulls[n].append(g[n])
    return nulls


def pair_auc_raw(V: np.ndarray, person: np.ndarray, seed: int, folds: int, M: np.ndarray | None, jobs: int) -> dict:
    """PC-raw: the matching AUC of the raw-keystroke summaries per classifier, with a person-bootstrap interval."""
    n_p = int(person.max()) + 1
    fop = fold_of_person(seed, n_p, folds)
    fold_s = fop[person]
    tasks = [(k, V, person, fold_s, k, seed, folds) for k in KINDS]
    got = _map(_pair_task, tasks, jobs)
    I, J = eval_pairs(fold_s, folds)
    y = (person[I] == person[J]).astype(np.int64)
    pi, pj = person[I], person[J]
    out = {}
    for k in KINDS:
        fa = fold_auc(got[k], y, fold_s[I])
        rec = {"auc": fa()}
        if M is not None:
            s0 = fa.short_calls  # the point estimate above is not a draw
            d = np.array([fa(pair_weights(m, pi, pj)) for m in M])
            rec["ci95"] = ck.ci95(d)
            rec["boot_short_folds"] = fa.short_calls - s0  # draws whose mean left a fold out (described, not judged)
        out[k] = rec
    best = max(KINDS, key=lambda k: (-1.0 if not np.isfinite(out[k]["auc"]) else out[k]["auc"]))
    out["best"] = {"kind": best, **out[best]}
    return out


def raw_gate(rec: dict, cfg: dict) -> dict:
    """design 3.0: PC-raw works when the lower bound of its AUC is above person.pc_raw.gate_lower."""
    lo = rec["best"].get("ci95", [float("nan")] * 2)[0]
    g = cfg["person"]["pc_raw"]["gate_lower"]
    return {"lower": lo, "gate": g, "works": bool(np.isfinite(lo) and lo > g)}


# ---------------------------------------------------------------------------
# The oracle and the description (design 1.5: e1, e2, e3)
# ---------------------------------------------------------------------------

def oracle_pair(La: np.ndarray, Lb: np.ndarray) -> np.ndarray:
    """-(Euclidean distance) of the true latent values of pairs (rows of La and Lb)."""
    return -np.sqrt(((La - Lb) ** 2).sum(axis=1))


def oracle_scores(L: np.ndarray) -> np.ndarray:
    """The oracle's score of every pair i < j (L: n x dims)."""
    a, b = np.triu_indices(len(L), 1)
    return oracle_pair(L[a], L[b])


def oracle_auc(L: np.ndarray, person: np.ndarray) -> float:
    a, b = np.triu_indices(len(L), 1)
    return ck.weighted_auc(oracle_scores(L), (person[a] == person[b]).astype(int), np.ones(len(a)))


def chance_check(X: np.ndarray, person: np.ndarray, seed: int, nperm: int, slots: int) -> dict:
    """design 3.3 (d), fixed before the results (cross-review 2): the distance AUC of X against the 95th percentile of
    the same AUC over fake persons (6 sessions kept). above_null: the AUC is above that percentile (to tell the
    researcher; not a verdict). NaN in X -> NaN, not above."""
    if not np.all(np.isfinite(X)) or nperm < 1:
        return {"auc": float("nan"), "null95": float("nan"), "above_null": False}
    auc = oracle_auc(X, person)
    nul = [oracle_auc(X, permute_persons(seed, r, len(person), slots)[0]) for r in range(nperm)]
    n95 = float(np.percentile(nul, 95))
    return {"auc": auc, "null95": n95, "above_null": bool(auc > n95)}


def top1_hit(V: np.ndarray, person: np.ndarray) -> dict:
    """e2: a distance attacker (no learning) on the sessions standardized over all of them: each session is a query; a
    person's score is the mean distance to the person's other sessions; the nearest person's being the owner is a hit."""
    Z = (V - np.nanmean(V, axis=0)) / np.where(np.nanstd(V, axis=0) > 0, np.nanstd(V, axis=0), 1.0)
    Z = np.nan_to_num(Z)
    D = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2))
    n_p = int(person.max()) + 1
    hits = 0
    for i in range(len(Z)):
        best, who = np.inf, -1
        for p in range(n_p):
            idx = np.nonzero((person == p) & (np.arange(len(Z)) != i))[0]
            d = float(D[i, idx].mean())
            if d < best:
                best, who = d, p
        hits += int(who == person[i])
    a, b = np.triu_indices(len(Z), 1)
    auc = ck.weighted_auc(-D[a, b], (person[a] == person[b]).astype(int), np.ones(len(a)))
    return {"top1": hits / len(Z), "chance": 1.0 / n_p, "pair_auc": auc}


def latent_names(world: str) -> list[str]:
    return ["m_log"] if world == "person-m" else ["x1", "x2", "x3", "speed_log"]


def r2_of_latents(Vfull: np.ndarray, person: np.ndarray, ms: list[dict], world: str, cfg: dict, smooth_V: np.ndarray) -> dict:
    """e3: Ridge R^2 (persons as groups) of each latent from a candidate's full summary and from its six smoothness
    quantities' summary alone."""
    out = {}
    alpha, folds = cfg["person"]["ridge_alpha"], cfg["person"]["folds"]
    for nm in latent_names(world):
        y = np.array([m[nm] for m in ms], dtype=np.float64)
        out[nm] = {"full": ck.oof_r2(np.nan_to_num(Vfull), y, person, folds, alpha),
                   "smooth_only": ck.oof_r2(np.nan_to_num(smooth_V), y, person, folds, alpha)}
    return out


# ---------------------------------------------------------------------------
# (6) per-person and common readers (design 1.8)
# ---------------------------------------------------------------------------

def personal_split(person_w: np.ndarray, slot_w: np.ndarray, p: int, train_slots: tuple) -> tuple[np.ndarray, np.ndarray]:
    """Person p's windows of the training slots (the fit) and of the other slots (the reading)."""
    mine = person_w == p
    intr = np.isin(slot_w, train_slots)
    return np.nonzero(mine & intr)[0], np.nonzero(mine & ~intr)[0]


def common_train_mask(fold_w: np.ndarray, f: int, slot_w: np.ndarray) -> np.ndarray:
    """The windows the common reader of validation fold f learns from: every window of the other folds' persons."""
    return fold_w != f


def _fit_predict(X: np.ndarray, y: np.ndarray, tr: np.ndarray, te: np.ndarray, kind: str, seed: int) -> np.ndarray:
    from threadpoolctl import threadpool_limits

    with threadpool_limits(1):
        model = make_model(kind, seed)
        model.fit(X[tr], y[tr])
        return model.predict_proba(X[te])[:, 1]


def reader_aucs(X: np.ndarray, y: np.ndarray, person_w: np.ndarray, slot_w: np.ndarray, fop: np.ndarray, kind: str,
                seed: int, train_slots: tuple) -> tuple[np.ndarray, np.ndarray, int]:
    """(per-person reader AUC, common reader AUC, persons left out) of one feature matrix X, per person (NaN where a
    person's fitting slots or reading slots hold one class: such a person is left out, design 1.8)."""
    n_p = len(fop)
    pers = np.full(n_p, np.nan)
    comm = np.full(n_p, np.nan)
    fold_w = fop[person_w]
    ones = lambda n: np.ones(n)
    ok = np.zeros(n_p, dtype=bool)
    for p in range(n_p):
        tr, te = personal_split(person_w, slot_w, p, train_slots)
        if len(tr) == 0 or len(te) == 0 or len(np.unique(y[tr])) < 2 or len(np.unique(y[te])) < 2:
            continue
        ok[p] = True
        pers[p] = ck.weighted_auc(_fit_predict(X, y, tr, te, kind, seed), y[te], ones(len(te)))
    for f in range(int(fop.max()) + 1):
        tr = np.nonzero(common_train_mask(fold_w, f, slot_w))[0]
        te = np.nonzero((fold_w == f) & ~np.isin(slot_w, train_slots))[0]
        if len(te) == 0 or len(np.unique(y[tr])) < 2:
            continue
        sc = _fit_predict(X, y, tr, te, kind, seed)
        for p in np.nonzero(fop == f)[0]:
            if ok[p]:
                m = person_w[te] == p
                comm[p] = ck.weighted_auc(sc[m], y[te][m], ones(int(m.sum())))
    return pers, comm, int((~ok).sum())


def _reader_task(args: tuple):
    key, X, y, person_w, slot_w, fop, kind, seed, ts = args
    return key, reader_aucs(X, y, person_w, slot_w, fop, kind, seed, ts)


def window_X(XA: np.ndarray, Frows: np.ndarray | None, G: np.ndarray, sess_all: np.ndarray | None, rows: np.ndarray | None,
             Fall: np.ndarray | None, fs: str, drop: str | None) -> np.ndarray:
    """Model A's window features (15) alone (Frows None), or with the drawing's 20 (small) or + the differences to the
    two earlier windows (full)."""
    if Fall is None:
        return XA
    F = Fall if drop is None else Fall[:, ck.keep_cols(drop)]
    parts = [XA, F[rows]]
    if fs == "full":
        parts.append(ck.diffs(F, sess_all, 2)[rows])
    return np.hstack(parts)


def fit6(Xs: dict, XA: np.ndarray, y: np.ndarray, person_w: np.ndarray, slot_w: np.ndarray, fop: np.ndarray, seed: int,
         jobs: int, train_slots: tuple) -> dict:
    """Xs: name -> {fs: X}. Returns {(name, fs, kind): (pers, comm, left_out)} and {("__A__", "-", kind): ...}."""
    tasks = [(("__A__", "-", k), XA, y, person_w, slot_w, fop, k, seed, train_slots) for k in KINDS]
    for name, d in Xs.items():
        for fs, X in d.items():
            for k in KINDS:
                tasks.append(((name, fs, k), X, y, person_w, slot_w, fop, k, seed, train_slots))
    return _map(_reader_task, tasks, jobs)


def six_D(c: tuple, a: tuple) -> dict:
    """The per-person quantities of one name against model A for one classifier: delta_pers, delta_comm, D = their
    difference, per person (NaN where a person is left out), over persons valid in all four AUCs."""
    pc, cc, _ = c
    pa, ca, _ = a
    dp, dc = pc - pa, cc - ca
    return {"dp": dp, "dc": dc, "D": dp - dc}


def six_records(got: dict, M: np.ndarray | None) -> tuple[dict, dict]:
    """name -> attacker -> {"gain" (= D, the mean over the valid persons), "ci95", "d_pers", "d_comm"} and the A
    readers' mean AUC per classifier ({kind: {"pers", "comm", "max", "left_out"}})."""
    out: dict = {}
    auc_a = {}
    for k in KINDS:
        pa, ca, lo = got[("__A__", "-", k)]
        auc_a[k] = {"pers": float(np.nanmean(pa)) if np.isfinite(pa).any() else float("nan"),
                    "comm": float(np.nanmean(ca)) if np.isfinite(ca).any() else float("nan"), "left_out": lo}
        auc_a[k]["max"] = max(auc_a[k]["pers"], auc_a[k]["comm"]) if np.isfinite(auc_a[k]["pers"]) else float("nan")
    for (name, fs, k), v in got.items():
        if name == "__A__":
            continue
        d = six_D(v, got[("__A__", "-", k)])
        valid = np.isfinite(d["D"])
        last = v[0] - v[1]  # AUC(A + name | per-person) - AUC(A + name | common), per person
        rec = {"last_diff": float(last[valid].mean()) if valid.any() else float("nan"),
               "gain": float(d["D"][valid].mean()) if valid.any() else float("nan"),
               "d_pers": float(d["dp"][valid].mean()) if valid.any() else float("nan"),
               "d_comm": float(d["dc"][valid].mean()) if valid.any() else float("nan"), "n_persons": int(valid.sum())}
        if M is not None:
            Dp = np.where(valid, d["D"], 0.0)
            den = (M * valid[None, :]).sum(axis=1)
            with np.errstate(invalid="ignore", divide="ignore"):
                draws = (M * Dp[None, :]).sum(axis=1) / den
            rec["ci95"] = ck.ci95(draws[np.isfinite(draws)]) if np.isfinite(draws).any() else [float("nan")] * 2
            dl = np.where(valid, last, 0.0)
            with np.errstate(invalid="ignore", divide="ignore"):
                dr = (M * dl[None, :]).sum(axis=1) / den
            rec["last_diff_ci95"] = ck.ci95(dr[np.isfinite(dr)]) if np.isfinite(dr).any() else [float("nan")] * 2
        out.setdefault(name, {})[f"{fs}/{k}"] = rec
    return out, auc_a


def null6(Xs: dict, XA: np.ndarray, y: np.ndarray, G: np.ndarray, n_sess: int, slots: int, seed: int, nperm: int,
          jobs: int, train_slots: tuple, folds: int = 5) -> dict:
    """The permutations of (6): fake persons (and slots) of the sessions, the readers refitted; name -> [attacker -> D]."""
    nulls: dict = {n: [] for n in Xs}
    for r in range(nperm):
        fake, fslot = permute_persons(seed, r, n_sess, slots)
        fop = fold_of_person(seed, int(fake.max()) + 1, folds, f"folds-perm6-{r}")
        got = fit6(Xs, XA, y, fake[G], fslot[G], fop, seed, jobs, train_slots)
        rec, _ = six_records(got, None)
        for n in Xs:
            nulls[n].append({a: v["gain"] for a, v in rec[n].items()})
    return nulls


# ---------------------------------------------------------------------------
# The calibration of k (design 1.7)
# ---------------------------------------------------------------------------

def choose_k(grid: list[float], aucs: list[float], target: float, tol: float) -> dict:
    """The point of the grid whose isotonic fit of the PC-raw AUC is nearest to the target (ties: the smaller k).
    Not reached (k None, status k_unreached) when the target is outside the fit's range or the nearest fit is more
    than tol away."""
    fit = [0.0] * len(grid)
    for s, e, v in ck.isotonic_blocks([float(a) for a in aucs]):
        for i in range(s, e + 1):
            fit[i] = v
    lo, hi = min(fit), max(fit)
    dist = [round(abs(f - target), 6) for f in fit]
    i = int(np.argmin(dist))  # argmin keeps the first of equal distances: the smaller k
    reached = lo <= target <= hi and dist[i] <= tol
    return {"k": grid[i] if reached else None, "status": "ok" if reached else "k_unreached", "nearest_k": grid[i],
            "fit": [[g, f] for g, f in zip(grid, fit)], "target": target, "tol": tol, "range": [lo, hi]}


_KCFG: dict = {}


def _k_init(cfg: dict) -> None:
    _KCFG.clear()
    _KCFG.update(cfg)
    os.environ["OMP_NUM_THREADS"] = "1"


def _k_task(args: tuple):
    seed, world, icc, k, i, dur_s = args
    segs, lat = gs.person_session(seed, _KCFG, world, icc, k, i, dur_s)
    times, _, _, dur_ms = gs.assemble(segs)
    return (k, i), (raw_features(times, dur_ms // 1000, _KCFG["person"]["pc_raw"]), lat["clipped"])


def kgrid_curve(cfg: dict, seed: int, world: str, icc: float, grid: list[float], jobs: int, dur_s: int | None = None
                ) -> list[dict]:
    """PC-raw AUC at each k of the grid (the same seed, so the sequences and latents are paired across the grid)."""
    n_p, slots = cfg["person"]["n_persons"], cfg["person"]["sessions_per_person"]
    dur = dur_s or cfg["session"]["duration_s"]
    tasks = [(seed, world, icc, k, i, dur) for k in grid for i in range(n_p * slots)]
    if jobs <= 1:
        _k_init(cfg)
        got = dict(_k_task(t) for t in tasks)
    else:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_k_init, initargs=(cfg,)) as ex:
            got = dict(ex.map(_k_task, tasks, chunksize=8))
    person = np.arange(n_p * slots) // slots
    out = []
    for k in grid:
        V = np.stack([got[(k, i)][0] for i in range(n_p * slots)])
        cl = np.array([got[(k, i)][1] for i in range(n_p * slots)], dtype=bool)
        rec = pair_auc_raw(V, person, seed, cfg["person"]["folds"], None, jobs)
        out.append({"k": k, "auc_hgb": rec["hgb"]["auc"], "auc_lr": rec["lr"]["auc"], "auc": rec["best"]["auc"],
                    "clipped_share_any": float(cl.any(axis=1).mean()), "clipped_share_by_dim": cl.mean(axis=0).tolist()})
    return out


def ceiling_status(auc_by_kind: dict, main_auc: float) -> str:
    """ceiling when both classifiers' AUC is at or above main_auc; unmeasured when one is NaN; else go."""
    v = [auc_by_kind[k] for k in KINDS]
    if any(not np.isfinite(x) for x in v):
        return "unmeasured"
    return "ceiling" if all(x >= main_auc for x in v) else "go"


def pilot_gate(raw_works: bool, five_status: dict, six_status: str) -> dict:
    """design 3.0: what the step runs next. PC-raw not working stops (5); (5) and (6) both stopped stops the step."""
    five_ok = raw_works and five_status["A"] == "go"
    six_ok = six_status == "go"
    return {"five": five_ok, "six": six_ok, "go": bool(five_ok or six_ok),
            "five_reason": None if five_ok else ("no_person_signal" if not raw_works else five_status["A"]),
            "six_reason": None if six_ok else six_status}


# ---------------------------------------------------------------------------
# The window table of a step and the run of the stage names
# ---------------------------------------------------------------------------

def load_step(work: Path, cfg: dict, scratch: Path | None = None) -> dict:
    """The sessions of a work directory (P only), their person and slot, the L300 table. The manifest's latents stay in
    ms and are read only by the oracle, the descriptions and the controls' checks, never by a candidate."""
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    person = np.array([m["person"] for m in ms], dtype=np.int64)
    slot = np.array([m["slot"] for m in ms], dtype=np.int64)
    tab = ck.label_tables(work, sids, cfg, scratch) if scratch is not None else bl.tables(work, sids, cfg)
    return {"ms": ms, "sids": sids, "person": person, "slot": slot, "tab": tab, "n": len(sids)}


def lam_key_problems(values) -> list[str]:
    """Two different lambdas that print alike with three decimals would share a stage key: refuse them."""
    seen: dict = {}
    out = []
    for v in values:
        k = f"{float(v):.3f}"
        if k in seen and seen[k] != float(v):  # exact equality only, against the first value seen (cross-review 2)
            out.append(f"lambdas {seen[k]} and {v} both print as {k}")
        seen.setdefault(k, float(v))
    return out


def stage_specs(cands: list[str], lam5: dict, lam6: dict | None, with5: bool, with6: bool) -> list[tuple]:
    """(key, name, lambda) of every stage run: the candidates, the (5) controls (PCp and PC0-id at each base's lambda)
    and the (6) controls. lam5: base -> cand -> lambda; lam6: cand -> lambda."""
    bad = lam_key_problems([x for b in lam5 for x in lam5[b].values()] + list((lam6 or {}).values()))
    if bad:
        raise SystemExit(f"lambda keys collide: {bad}")
    specs = [(c, c, None) for c in cands]
    if with5:
        specs.append(("PC1-id", "PC1-id", None))
        for b in BASES:
            for c in cands:
                for nm, pre in (("PCp-", "PCp-"), ("PC0-id-", "PC0-id-")):
                    key = f"{pre}{c}@{lam5[b][c]:.3f}"
                    if key not in [s[0] for s in specs]:
                        specs.append((key, f"{pre}{c}", float(lam5[b][c])))
    if with6:
        specs.append(("PC1-pers", "PC1-pers", None))
        for c in cands:
            for pre in ("PCps-", "PC0p-"):
                specs.append((f"{pre}{c}@{lam6[c]:.3f}", f"{pre}{c}", float(lam6[c])))
    return specs


# ---------------------------------------------------------------------------
# The records a later mode needs (fail closed)
# ---------------------------------------------------------------------------

def step_k(cfg: dict, step: str):
    k = cfg["person"]["k"].get(step)
    return None if k is None else float(k)


def check_world(work: Path, cfg: dict, step: str, mode: str, seed: int) -> dict:
    """The work directory was made for this step, mode and seed: its world, ICC, k, seed and mode are the caller's."""
    w = json.loads((work / "world.json").read_text(encoding="utf-8"))
    s = cfg["person"]["steps"][step]
    want = {"world": s["world"], "icc": float(s["icc"]), "k": None if s["world"] == "person-m" else step_k(cfg, step),
            "seed": seed, "mode": mode}
    if w != want:
        raise SystemExit(f"{work}/world.json is {w}, not {want} (step {step})")
    return w


def record_problems(doc: dict, cfg: dict, base_seed: int, step: str, mode: str, what: str) -> list[str]:
    """Is this record the step's, made at this mode's seed under this config, these instruments and this k?"""
    out = []
    if doc.get("step") != step:
        out.append(f"{what}: step {doc.get('step')} is not {step}")
    if doc.get("seed") != run_seed(mode, base_seed, cfg):
        out.append(f"{what}: seed {doc.get('seed')} is not the {mode} seed {run_seed(mode, base_seed, cfg)}")
    if doc.get("config_fingerprint") != cfg_fingerprint(cfg):
        out.append(f"{what}: made under another config.json (fingerprint)")
    if doc.get("code_fingerprint") != code_fingerprint():
        out.append(f"{what}: made by other instruments (code fingerprint): run it again")
    if doc.get("k") != step_k(cfg, step):
        out.append(f"{what}: k {doc.get('k')} is not the config's {step_k(cfg, step)}")
    return out


def load_record(path: Path, what: str) -> dict:
    if not path.exists():
        raise SystemExit(f"{path} is missing ({what} must be run first)")
    return json.loads(path.read_text(encoding="utf-8"))


def require_ceiling(cfg: dict, base_seed: int, step: str, step_dir: Path) -> dict:
    doc = load_record(step_dir / "ceiling" / "ceiling.json", "--ceiling")
    bad = record_problems(doc, cfg, base_seed, step, "ceiling", "ceiling.json")
    if bad or "gate" not in doc:
        raise SystemExit(f"ceiling.json: {bad or 'no gate'}")
    return doc


def lam_problems(gate: dict, pilot: dict, lam5: dict, lam6) -> list[str]:
    """The gate, the pilot's choices and config.json's lambdas agree (apply-pilot was run on this pilot)."""
    out = []
    five_p, six_p = pilot.get("five", {}), pilot.get("six", {})
    if gate["five"]:
        if not isinstance(five_p, dict) or not five_p:
            out.append("the gate runs (5) but the pilot has no (5) part")
        elif not five_p.get("stop"):
            for b in BASES:
                v = five_p.get(b)
                if not isinstance(v, dict):
                    out.append(f"the pilot has no (5) part for base {b}")
                elif not v.get("stop") and lam5.get(b) != v.get("lam"):
                    out.append(f"pc_person.lam base {b} is not the pilot's choice (run --apply-pilot)")
    elif five_p:
        out.append("the gate stops (5) but the pilot ran it")
    if gate["six"]:
        if not isinstance(six_p, dict) or not six_p:
            out.append("the gate runs (6) but the pilot has no (6) part")
        elif not six_p.get("stop") and lam6 != six_p.get("lam"):
            out.append("pc_pers.lam is not the pilot's choice (run --apply-pilot)")
    elif six_p:
        out.append("the gate stops (6) but the pilot ran it")
    return out


def require_pilot(cfg: dict, base_seed: int, step: str, step_dir: Path, gate: dict) -> dict:
    doc = load_record(step_dir / "pilot" / "pilot.json", "--pilot")
    bad = record_problems(doc, cfg, base_seed, step, "pilot", "pilot.json")
    bad += lam_problems(gate, doc, cfg["pc_person"]["lam"].get(step, {}), cfg["pc_pers"]["lam"].get(step))
    if bad:
        raise SystemExit(f"pilot.json / config.json: {bad}")
    return doc


def wiring_problems(summ: dict) -> list[str]:
    """design 3.7, the wiring on the run's own columns: PC1-id's gain (5) and PC1-pers's D (6) above 0.10, PC0-id and PC0p
    (upper bound) below 0.03. A failure is reported to the researcher; the results stay."""
    out = []
    for label, part in list(summ.get("five", {}).items()) + [("six", summ.get("six", {}))]:
        j = part.get("judge")
        if not j:
            continue
        pc1 = "PC1-pers" if label == "six" else "PC1-id"
        mx = j["maxima"]
        g = mx.get(pc1, {}).get("gain_max")
        if g is None or not (g > 0.10):
            out.append(f"{label}: {pc1} gain {g} is not above 0.10")
        pre = "PC0p-" if label == "six" else "PC0-id-"
        for n, r in mx.items():
            if n.startswith(pre) and not (r["upper_max"] < 0.03):
                out.append(f"{label}: {n} upper bound {r['upper_max']} is not below 0.03")
    return out


def wiring_checked(summ: dict) -> int:
    """How many parts ((5) per base, (6)) had a judge for wiring_problems to read (cross-review 2: 0 is recorded)."""
    parts = list(summ.get("five", {}).values()) + [summ.get("six", {})]
    return sum(1 for p in parts if p.get("judge"))


# ---------------------------------------------------------------------------
# The modes: ceiling (pilot 0), pilot-k, pilot (pilot 1), apply-pilot, run (smoke and main)
# ---------------------------------------------------------------------------

def bases_of(tab: dict, n: int) -> dict:
    return {b: base_summary(tab, b, n) for b in BASES}


def ceiling_run(cfg: dict, seed: int, step: str, work: Path, out: Path, jobs: int) -> dict:
    """design 3.0: AUC(A) and AUC(A_speed) of (5), PC-raw and its lower bound, (6)'s readers on model A; the status of
    each question. No gse-replay (the baselines and the raw keystrokes read the press times and the labels only)."""
    check_world(work, cfg, step, "ceiling", seed)
    d = load_step(work, cfg)
    n, person, tab = d["n"], d["person"], d["tab"]
    n_p = int(person.max()) + 1
    M = boot_counts(seed, "boot-ceiling", n_p, cfg["person"]["bootstrap"])
    raw = pair_auc_raw(raw_matrix(work, d["sids"], cfg["person"]["pc_raw"]), person, seed, cfg["person"]["folds"], M, jobs)
    gate = raw_gate(raw, cfg)
    main_auc = cfg["ceiling"]["main_auc"]
    five, five_status = {}, {}
    for b, vb in bases_of(tab, n).items():
        _, base, pairs = fit5({}, vb, person, seed, cfg["person"]["folds"], jobs)
        I, J, y, pf = pairs
        five[b] = {k: fold_auc(base[k], y, pf)() for k in KINDS}
        five_status[b] = ceiling_status(five[b], main_auc)
    t = tab[ck.TAG]
    fop = fold_of_person(seed, n_p, cfg["person"]["folds"])
    got = fit6({}, t["XA"], t["Y"], person[t["G"]], d["slot"][t["G"]], fop, seed, jobs,
               tuple(cfg["person"]["reader"]["train_slots"]))
    _, auc_a = six_records(got, None)
    six_status = ceiling_status({k: auc_a[k]["max"] for k in KINDS}, main_auc)
    doc = {"step": step, "seed": seed, "n_sessions": n, "config_fingerprint": cfg_fingerprint(cfg),
           "code_fingerprint": code_fingerprint(), "k": step_k(cfg, step), "main_auc": main_auc, "pc_raw": raw, "pc_raw_gate": gate,
           "five_auc": five, "five_status": five_status, "six_auc_A": auc_a, "six_status": six_status,
           "gate": pilot_gate(gate["works"], five_status, six_status),
           "world": json.loads((work / "world.json").read_text(encoding="utf-8"))}
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "ceiling.json", doc)
    print(json.dumps(clean({"gate": doc["gate"], "pc_raw": raw["best"], "five_auc": five, "six": six_status}), indent=1))
    return doc


def kgrid_run(cfg: dict, base_seed: int, step: str, out: Path, jobs: int, root: Path) -> dict:
    """design 1.7: PC-raw AUC over the k grid at SEED + 1 for a person-r step; the target is the same-ICC person-m
    step's pilot value."""
    s = cfg["person"]["steps"][step]
    if s["world"] != "person-r":
        raise SystemExit(f"{step} is not a person-r step: it has no k")
    tgt_f = root / "results" / s["target_step"] / "pilot" / "pilot.json"
    if not tgt_f.exists():
        raise SystemExit(f"{tgt_f} is missing: the person-m step {s['target_step']} runs first (design 1.3)")
    tdoc = json.loads(tgt_f.read_text(encoding="utf-8"))
    bad = []
    if tdoc.get("step") != s["target_step"] or tdoc.get("seed") != run_seed("pilot", base_seed, cfg):
        bad.append("not the target step's pilot at the pilot seed")
    if tdoc.get("config_fingerprint") != cfg_fingerprint(cfg):
        bad.append("made under another config.json")
    if tdoc.get("code_fingerprint") != code_fingerprint():
        bad.append("made by other instruments")
    if bad:
        raise SystemExit(f"{tgt_f}: {bad}")
    target = float(tdoc["pc_raw"]["best"]["auc"])
    seed = run_seed("pilot-k", base_seed, cfg)
    if not all(math.isfinite(float(k)) and 0.0 <= float(k) <= gs.K_MAX for k in cfg["person"]["k_grid"]):
        raise SystemExit(f"the k grid must be finite numbers in [0, {gs.K_MAX}]")
    curve = kgrid_curve(cfg, seed, "person-r", s["icc"], [float(k) for k in cfg["person"]["k_grid"]], jobs)
    ch = choose_k([c["k"] for c in curve], [c["auc"] for c in curve], target, cfg["person"]["k_tolerance"])
    doc = {"step": step, "seed": seed, "target_step": s["target_step"], "target": target, "curve": curve, "choice": ch,
           "config_fingerprint": cfg_fingerprint(cfg), "code_fingerprint": code_fingerprint()}
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "pilot-k.json", doc)
    print(json.dumps(clean({"k": ch["k"], "status": ch["status"], "nearest_k": ch["nearest_k"]})))
    return doc


def select_for(grid: list[float], recs: dict, cfg: dict, use: list[str]) -> dict:
    """The lambda of one candidate from the pilot's per-lambda records (x -> name record -> attacker -> {gain, ci95})."""
    ps = cfg["pc_stall"]
    mx = [ck.maxima(recs[x], use) for x in grid]
    return ck.select_lambda(grid, [m["gain_max"] for m in mx], [m["lower_max"] for m in mx], ps["aim"], ps["lower"],
                            ps["upper"])


def pilot_stop_of(use: list[str], pc1: dict | None, sel: dict, cfg: dict) -> str | None:
    if not use:
        return "ceiling"
    if not (pc1 and ck._gt(pc1["lower_max"], cfg["e13"]["pc_lower"])):
        return "weak_detector"
    if any(s["lam"] is None for s in sel.values()):
        return "no_finite_pcs"
    return None


def pilot_run(cfg: dict, base_seed: int, step: str, work: Path, out: Path, jobs: int, with5: bool, with6: bool) -> dict:
    """design 1.7: PCp and PCps on the lambda grid, per base and candidate; PC1-id and PC1-pers; PC-raw."""
    seed = run_seed("pilot", base_seed, cfg)
    check_world(work, cfg, step, "pilot", seed)
    grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
    if lam_key_problems(grid):
        raise SystemExit(f"the pilot grid's keys collide: {lam_key_problems(grid)}")
    cands = st.candidates()
    scratch = Path(tempfile.mkdtemp(prefix="pilot-", dir=work))
    try:
        d = load_step(work, cfg, scratch)
        n, person, slot, tab, ms = d["n"], d["person"], d["slot"], d["tab"], d["ms"]
        n_p = int(person.max()) + 1
        folds = cfg["person"]["folds"]
        specs = []
        if with5:
            specs.append(("PC1-id", "PC1-id", None))
            specs += [(f"PCp-{c}@{x:.3f}", f"PCp-{c}", x) for c in cands for x in grid]
        if with6:
            specs.append(("PC1-pers", "PC1-pers", None))
            specs += [(f"PCps-{c}@{x:.3f}", f"PCps-{c}", x) for c in cands for x in grid]
        F = ck.run_stage(specs, ms, work, seed, jobs)
        t = tab[ck.TAG]
        rows = np.nonzero(t["rows"])[0]
        M = boot_counts(seed, "boot-pilot", n_p, cfg["person"]["bootstrap"])
        raw = pair_auc_raw(raw_matrix(work, d["sids"], cfg["person"]["pc_raw"]), person, seed, folds, M, jobs)
        doc = {"step": step, "seed": seed, "n_sessions": n, "bootstrap": cfg["person"]["bootstrap"],
               "rule": {k: cfg["pc_stall"][k] for k in ck.RULE_KEYS}, "config_fingerprint": cfg_fingerprint(cfg),
               "code_fingerprint": code_fingerprint(), "k": step_k(cfg, step),
               "pc_raw": raw, "pc_raw_gate": raw_gate(raw, cfg), "five": {},
               "six": {}}
        if with5 and doc["pc_raw_gate"]["works"]:
            for b, vb in bases_of(tab, n).items():
                mats = {}
                for key, *_ in specs:
                    if key == "PC1-id" or key.startswith("PCp-"):
                        mats[key] = variant_mats(F[key], rows, t["G"], n, vb, None)
                sc, base, pairs = fit5(mats, vb, person, seed, folds, jobs)
                rec, auc_b = gain_records(sc, base, pairs, person, M)
                use = [a for a in ATTACKERS if a.split("/")[1] not in ck.ceiling_kinds(auc_b, cfg)]
                sel = ({c: select_for(grid, {x: rec[f"PCp-{c}@{x:.3f}"] for x in grid}, cfg, use) for c in cands}
                       if use else {})
                pc1 = ck.maxima(rec["PC1-id"], use) if use else None
                doc["five"][b] = {"stop": pilot_stop_of(use, pc1, sel, cfg), "auc_base": auc_b, "pc1": pc1,
                                  "selection": sel, "lam": {c: s["lam"] for c, s in sel.items()}}
        elif with5:
            doc["five"] = {"stop": "no_person_signal"}
        if with6:
            XA, sess_all = t["XA"], t["G_all"]
            Xs = {k: {fs: window_X(XA, None, t["G"], sess_all, rows, F[k], fs, None) for fs in FSETS}
                  for k, *_ in specs if k.startswith(("PC1-pers", "PCps-"))}
            fop = fold_of_person(seed, n_p, folds)
            got = fit6(Xs, XA, t["Y"], person[t["G"]], slot[t["G"]], fop, seed, jobs,
                       tuple(cfg["person"]["reader"]["train_slots"]))
            rec, auc_a = six_records(got, M)
            ceil = [k for k in KINDS if np.isfinite(auc_a[k]["max"]) and auc_a[k]["max"] >= cfg["ceiling"]["main_auc"]]
            use = [a for a in ATTACKERS if a.split("/")[1] not in ceil]
            sel = ({c: select_for(grid, {x: rec[f"PCps-{c}@{x:.3f}"] for x in grid}, cfg, use) for c in cands}
                   if use else {})
            pc1 = ck.maxima(rec["PC1-pers"], use) if use else None
            doc["six"] = {"stop": pilot_stop_of(use, pc1, sel, cfg), "auc_A": auc_a, "pc1": pc1, "selection": sel,
                          "lam": {c: s["lam"] for c, s in sel.items()}}
        out.mkdir(parents=True, exist_ok=True)
        dump(out / "pilot.json", doc)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return doc


def apply_pilot(cfg_path: Path, step: str, what: str) -> int:
    """Write the pilot's choices to config.json: person.k.<step> (r steps) and pc_person.lam / pc_pers.lam. The rest of
    the file is kept."""
    root = cfg_path.parent
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_seed = int((root / "SEED").read_text().strip())
    wrote = {}
    kf = root / "results" / step / "pilot-k" / "pilot-k.json"
    if what in ("k", "all") and kf.exists():
        p = json.loads(kf.read_text(encoding="utf-8"))
        if p["seed"] != run_seed("pilot-k", base_seed, cfg) or p["step"] != step:
            raise SystemExit("pilot-k.json is not this step's at the k grid's seed")
        if p["config_fingerprint"] != cfg_fingerprint(cfg):
            raise SystemExit("pilot-k.json was made under another config.json")
        if p.get("code_fingerprint") != code_fingerprint():
            raise SystemExit("pilot-k.json was made by other instruments (code fingerprint)")
        if p["choice"]["k"] is None:
            raise SystemExit(f"{step}: k_unreached (nearest k {p['choice']['nearest_k']}): no k is written (design 1.7)")
        cfg["person"]["k"][step] = p["choice"]["k"]
        wrote["k"] = p["choice"]["k"]
    f = root / "results" / step / "pilot" / "pilot.json"
    if what in ("lam", "all") and f.exists():
        p = json.loads(f.read_text(encoding="utf-8"))
        if p["seed"] != run_seed("pilot", base_seed, cfg) or p["step"] != step:
            raise SystemExit("pilot.json is not this step's at the pilot's seed")
        if p["config_fingerprint"] != cfg_fingerprint(cfg):
            raise SystemExit("pilot.json was made under another config.json")
        if p.get("code_fingerprint") != code_fingerprint():
            raise SystemExit("pilot.json was made by other instruments (code fingerprint)")
        if p.get("k") != step_k(cfg, step):
            raise SystemExit("pilot.json was made at another k than config.json's")
        grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
        five = {b: v["lam"] for b, v in p.get("five", {}).items()
                if b in BASES and isinstance(v, dict) and not v.get("stop")}
        if five:
            cfg["pc_person"]["lam"][step] = five
        six = p.get("six", {})
        if isinstance(six, dict) and six and not six.get("stop"):
            cfg["pc_pers"]["lam"][step] = six["lam"]
        tables = list(cfg["pc_person"]["lam"].get(step, {}).values()) + [cfg["pc_pers"]["lam"].get(step, {})]
        for tb in tables:
            bad = [c for c, v in tb.items() if not any(abs(float(v) - x) < 1e-12 for x in grid)]
            if bad:
                raise SystemExit(f"lambda off the grid: {bad}")
        wrote["lam"] = {"five": five, "six": cfg["pc_pers"]["lam"].get(step)}
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(wrote, indent=1))
    return 0


def variant_mats(F: np.ndarray, rows: np.ndarray, G: np.ndarray, n: int, vb: np.ndarray, drop: str | None) -> dict:
    m_, s_ = cand_summary(F[rows], G, n, drop)
    return feature_sets(vb, m_, s_)


def run_main(cfg: dict, base_seed: int, step: str, work: Path, out: Path, jobs: int, smoke: bool, step_dir: Path) -> dict:
    """design 1.5-1.8: the candidates, their variants and the controls through (5) on both bases and (6); the verdicts;
    the descriptions. smoke: SEED + 2, bootstrap 200, 2 permutations (the pipeline check). step_dir is
    results/<step> (the step's ceiling.json and pilot-k.json are read from it)."""
    mode = "smoke" if smoke else "main"
    seed = run_seed(mode, base_seed, cfg)
    pcfg = cfg["person"]
    nboot = pcfg["smoke"]["bootstrap"] if smoke else pcfg["bootstrap"]
    nperm = pcfg["smoke"]["null_perms"] if smoke else pcfg["null_perms"]
    cands = st.candidates()
    lam5 = cfg["pc_person"]["lam"].get(step, {})
    lam6 = cfg["pc_pers"]["lam"].get(step)
    check_world(work, cfg, step, mode, seed)
    ceil_doc = require_ceiling(cfg, base_seed, step, step_dir)
    gate = ceil_doc["gate"]
    pilot_doc = require_pilot(cfg, base_seed, step, step_dir, gate)
    five_p = pilot_doc.get("five", {})
    ok_bases = [b for b in BASES if isinstance(five_p.get(b), dict) and not five_p[b].get("stop")]
    with5 = bool(gate["five"]) and not five_p.get("stop") and bool(ok_bases)
    with6 = bool(gate["six"]) and not pilot_doc.get("six", {}).get("stop")
    if with5:
        lam5 = {b: lam5[b] for b in ok_bases}
    if not (with5 or with6):
        raise SystemExit("the pilot stopped both questions: nothing to run (design 3.0)")
    scratch = Path(tempfile.mkdtemp(prefix="main-", dir=work))
    try:
        d = load_step(work, cfg, scratch)
        n, person, slot, tab, ms = d["n"], d["person"], d["slot"], d["tab"], d["ms"]
        n_p, folds = int(person.max()) + 1, pcfg["folds"]
        world = json.loads((work / "world.json").read_text(encoding="utf-8"))["world"]
        t = tab[ck.TAG]
        rows = np.nonzero(t["rows"])[0]
        G = t["G"]
        specs = stage_specs(cands, {b: lam5.get(b, {c: 0.1 for c in cands}) for b in BASES}, lam6 or {}, with5, with6)
        F = ck.run_stage(specs, ms, work, seed, jobs)
        M = boot_counts(seed, "boot-main", n_p, nboot)
        t0 = time.time()
        res: dict = {"step": step, "seed": seed, "smoke": smoke, "world": world, "gate": gate, "n_sessions": n,
                     "k": step_k(cfg, step), "config_fingerprint": cfg_fingerprint(cfg),
                     "code_fingerprint": code_fingerprint(),
                     "pilot_stops": {"five": five_p.get("stop") or {b: five_p[b].get("stop") for b in BASES
                                                                   if isinstance(five_p.get(b), dict)},
                                     "six": pilot_doc.get("six", {}).get("stop")}}
        raw_V = raw_matrix(work, d["sids"], pcfg["pc_raw"])
        raw = pair_auc_raw(raw_V, person, seed, folds, M, jobs)
        gate_raw = raw_gate(raw, cfg)
        res["pc_raw"], res["pc_raw_gate"] = raw, gate_raw
        vbs = bases_of(tab, n)
        names_all = list(cands)
        res["five"] = {}
        for b in BASES:
            label = BASE_NAME[b]
            if not with5 or b not in lam5 or not gate_raw["works"]:
                pst = five_p.get(b, {}).get("stop") if isinstance(five_p.get(b), dict) else five_p.get("stop")
                why = ("no_person_signal" if (with5 and not gate_raw["works"] and b in lam5) else
                       (f"pilot_stop:{pst}" if pst else ("pilot_stop" if with5 else "not_run")))
                res["five"][label] = {"verdicts": {c: "undecidable" for c in names_all}, "reason": why}
                continue
            vb = vbs[b]
            mats = {"PC1-id": variant_mats(F["PC1-id"], rows, G, n, vb, None)}
            for c in cands:
                lam = lam5[b][c]
                keys = {"": c, "PCp-": f"PCp-{c}@{lam:.3f}", "PC0-id-": f"PC0-id-{c}@{lam:.3f}"}
                for pre, key in keys.items():
                    mats[f"{pre}{c}"] = variant_mats(F[key], rows, G, n, vb, None)
                # the variant is a description: the candidate's picture without the smoothness features, no control
                mats[variant_name(c)] = variant_mats(F[c], rows, G, n, vb, pcfg["variant_drop"])
            sc, base, pairs = fit5(mats, vb, person, seed, folds, jobs)
            rec, auc_b = gain_records(sc, base, pairs, person, M)
            attk = attk_of(rec)
            null_names = ["PC1-id"] + [f"{p}{c}" for c in cands for p in ("", "PCp-", "PC0-id-")]
            nulls = (null5({k: mats[k] for k in null_names}, vb, n, pcfg["sessions_per_person"], seed, folds, nperm, jobs)
                     if nperm else None)
            par = {k: v for k, v in attk.items() if VAR not in k}
            j = judge_q("id", par, nulls, auc_b, cands, cfg, False)
            verd = {c: j["verdicts"][c] for c in cands}
            variants = {c: variant_record(attk[c], attk[variant_name(c)], verd[c], auc_b, cfg) for c in cands}
            res["five"][label] = {"verdicts": verd, "variants": variants, "judge": j, "auc_base": auc_b, "records": rec}
            print(f"(5) {label} done at {time.time() - t0:.0f} s", flush=True)
        if with6:
            XA, sess_all = t["XA"], t["G_all"]
            Xs = {"PC1-pers": {fs: window_X(XA, None, G, sess_all, rows, F["PC1-pers"], fs, None) for fs in FSETS}}
            for c in cands:
                for pre, key in (("", c), ("PCps-", f"PCps-{c}@{lam6[c]:.3f}"), ("PC0p-", f"PC0p-{c}@{lam6[c]:.3f}")):
                    Xs[f"{pre}{c}"] = {fs: window_X(XA, None, G, sess_all, rows, F[key], fs, None) for fs in FSETS}
                Xs[variant_name(c)] = {fs: window_X(XA, None, G, sess_all, rows, F[c], fs, pcfg["variant_drop"])
                                       for fs in FSETS}
            fop = fold_of_person(seed, n_p, folds)
            ts = tuple(pcfg["reader"]["train_slots"])
            got = fit6(Xs, XA, t["Y"], person[G], slot[G], fop, seed, jobs, ts)
            rec, auc_a = six_records(got, M)
            attk = attk_of(rec)
            null_names = ["PC1-pers"] + [f"{p}{c}" for c in cands for p in ("", "PCps-", "PC0p-")]
            nulls = (null6({k: Xs[k] for k in null_names}, XA, t["Y"], G, n, pcfg["sessions_per_person"], seed, nperm,
                           jobs, ts, folds) if nperm else None)
            auc_s = {k: auc_a[k]["max"] for k in KINDS}
            par = {k: v for k, v in attk.items() if VAR not in k}
            j = judge_q("pers", par, nulls, auc_s, cands, cfg, False)
            verd = {c: j["verdicts"][c] for c in cands}
            variants = {c: variant_record(attk[c], attk[variant_name(c)], verd[c], auc_s, cfg) for c in cands}
            res["six"] = {"verdicts": verd, "variants": variants, "judge": j, "auc_A": auc_a, "records": rec,
                          "last_auc_diff": {n: {a: {"diff": v["last_diff"], "ci95": v.get("last_diff_ci95")}
                                                for a, v in d_.items()} for n, d_ in rec.items() if VAR not in n}}
            print(f"(6) done at {time.time() - t0:.0f} s", flush=True)
        else:
            sp_ = pilot_doc.get("six", {}).get("stop")
            res["six"] = {"verdicts": {c: "undecidable" for c in names_all},
                          "reason": f"pilot_stop:{sp_}" if gate["six"] and sp_ else f"gate:{ceil_doc['six_status']}"}
        desc: dict = {}
        lat = latent_names(world)[: (1 if world == "person-m" else 3)]
        L = np.array([[m[k] for k in lat] for m in ms])
        desc["e1_oracle"] = {"auc": oracle_auc(L, person), "latents": lat}
        if world == "person-r":  # the speed shift alone must not identify a person (it is tied to no person)
            sp_only = np.array([[m["speed_log"]] for m in ms])
            slots = pcfg["sessions_per_person"]
            desc["e1_speed_log_only"] = chance_check(sp_only, person, seed, nperm, slots)  # the generator's latent
            # observed: the median log of the short intervals (PC-raw's lg_p50), which dimensions 1 and 3 do not move
            desc["e1_short_median_only"] = chance_check(raw_V[:, [1]], person, seed, nperm, slots)
            cl = np.array([m["clipped"] for m in ms], dtype=bool)
            share = float(cl.any(axis=1).mean())
            # design 3.3 (b), fixed before the results (cross-review 2): above TRUNC_DECLARE the types are declared
            # a world cut at the tails (not "k h x")
            res["clipped"] = {"share_any": share, "share_by_dim": cl.mean(axis=0).tolist(),
                              "truncated_world": bool(share > TRUNC_DECLARE), "declare_above": TRUNC_DECLARE}
        desc["e2_top1"] = {"oracle": top1_hit(L, person), "pc_raw": top1_hit(raw_V, person),
                           **{BASE_NAME[b]: top1_hit(vbs[b], person) for b in BASES}}
        desc["e3_r2"] = {}
        for c in cands:
            m_, s_ = cand_summary(F[c][rows], G, n)
            desc["e2_top1"][c] = top1_hit(np.hstack([m_, s_]), person)
            desc["e3_r2"][c] = r2_of_latents(np.hstack([m_, s_]), person, ms, world, cfg,
                                             np.hstack([m_[:, ck.SMOOTH_COLS], s_[:, ck.SMOOTH_COLS]]))
        kf = step_dir / "pilot-k" / "pilot-k.json"
        if kf.exists():
            desc["e5_k"] = json.loads(kf.read_text(encoding="utf-8"))
        res["descriptions"] = desc
        res["_wall_s"] = time.time() - t0
        out.mkdir(parents=True, exist_ok=True)
        dump(out / "summary.json", res)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(json.dumps(clean({a: v.get("verdicts") for a, v in {**res["five"], "six": res["six"]}.items()}), indent=1))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=False)
    for m_ in ("ceiling", "pilot-k", "pilot", "apply-pilot", "run"):
        mode.add_argument(f"--{m_}", dest="mode", action="store_const", const=f"--{m_}")
    ap.add_argument("config")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--step", default=None)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--what", default="all", choices=["k", "lam", "all"])
    ap.add_argument("--wiring", default=None, help="check a main summary.json's wiring (design 3.7) and exit")
    a = ap.parse_args()
    if a.wiring:
        sp_ = Path(a.wiring)
        doc = json.loads(sp_.read_text(encoding="utf-8"))
        bad = wiring_problems(doc)
        checked = wiring_checked(doc)
        doc["wiring"] = {"passed": not bad, "problems": bad, "checked": checked}  # checked 0: nothing was judged
        print(f"wiring: {checked} part(s) checked")
        dump(sp_, doc)
        for b in bad:
            print("WIRING FAILED:", b)
        if bad:
            print("=== the wiring check of design 3.7 failed: tell the researcher; do not go on (the results are kept) ===")
        return 1 if bad else 0
    if a.mode is None:
        raise SystemExit("a mode is required")
    cfg_path = Path(a.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if a.step not in cfg["person"]["steps"]:
        raise SystemExit(f"--step must be one of {sorted(cfg['person']['steps'])}")
    if a.mode == "--apply-pilot":
        return apply_pilot(cfg_path, a.step, a.what)
    base_seed = int((cfg_path.parent / "SEED").read_text().strip())
    seed = int(Path(a.rest[0]).read_text().strip())
    out = Path(a.rest[-1])
    mode_name = {"--pilot-k": "pilot-k", "--ceiling": "ceiling", "--pilot": "pilot",
                 "--run": "smoke" if a.smoke else "main"}[a.mode]
    if seed != run_seed(mode_name, base_seed, cfg):
        raise SystemExit(f"the seed file holds {seed}, not the {mode_name} seed {run_seed(mode_name, base_seed, cfg)}")
    if a.mode == "--pilot-k":
        kgrid_run(cfg, base_seed, a.step, out, a.jobs, cfg_path.parent)
        return 0
    work = Path(a.rest[1])
    if a.mode == "--ceiling":
        ceiling_run(cfg, seed, a.step, work, out, a.jobs)
    elif a.mode == "--pilot":
        gate = require_ceiling(cfg, base_seed, a.step, cfg_path.parent / "results" / a.step)["gate"]
        if not gate["go"]:
            raise SystemExit(f"{a.step}: both questions stopped at the ceiling (design 3.0)")
        pilot_run(cfg, base_seed, a.step, work, out, a.jobs, bool(gate["five"]), bool(gate["six"]))
    else:
        run_main(cfg, base_seed, a.step, work, out, a.jobs, a.smoke, cfg_path.parent / "results" / a.step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
