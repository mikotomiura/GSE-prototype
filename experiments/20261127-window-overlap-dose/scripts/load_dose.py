"""列 A・列 B・列 C の読み込み（conditions D1）。S13 の試験の load.py の load_column と同じ形で、列の名を受ける。

列の名: "A<s>"（s ∈ 1, 5, 10, 15, 30）・"B<s>"・"C<s>"・"P1-<s>"・"P3-<s>"（s ∈ 5, 10, 15, 30。P1・P3 は列 C′1・C′3）。
単位は tau-extend の data.py の読み込み（ml.load）のまま作り、S13 の load.apply_column で u に替えてから、
系列ごとに行を採る。行の時刻は data.py が読む今の中間（coauthor_work_obs）の feat 行の第 1 列を、
data.py と同じ選び・同じ並べで読む。読んだ単位の obs が data.py の系列と 1 つでも違えば止める。
単位とパネルの顔ぶれは o と同じ（行が 0 になった系列は落とし、単位は残す）。
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S13 = os.path.realpath(os.path.join(HERE, "../../20261107-unsmoothed-residual-check/scripts"))
if S13 not in sys.path:
    sys.path.insert(0, S13)
import load as L13  # noqa: E402  S13 の load.py（SHA-256 は pins.py で照らす）
import pinned  # noqa: E402
import masks as MK  # noqa: E402

MUT = set()  # m68: 差し替えた読み込みで pflag を採らない／m70: 列 C の始まりを 0 に／m71: 列 C の行の数を 1 つ多く


def parse(col):
    if col not in COLS:
        raise SystemExit("列の名が違う: %s" % col)
    if col.startswith("P"):
        return col[:2], int(col.split("-")[1])
    return col[0], int(col[1:])


def coauthor_times(work):
    """data.py の load_coauthor と同じ選び・並べで、単位ごとの feat 行の時刻と obs を返す。"""
    s2w = json.load(open(os.path.join(work, "sessions.json")))
    by_w = {}
    for f in sorted(glob.glob(os.path.join(work, "s[0-9]*.json"))):
        sid = os.path.basename(f)[1:-5]
        if sid not in s2w:
            continue
        d = json.load(open(f))
        if len(d["observed_intervals"]) != 1 or not d["feat"]:
            continue
        a = d["observed_intervals"][0][0]
        t = [int(r[0]) for r in d["feat"]]
        obs = np.array([r[6] for r in d["feat"]], dtype=np.float64).astype(np.int64)
        by_w.setdefault(s2w[sid], []).append(dict(start=a, t=t, obs=obs))
    return [sorted(by_w[w], key=lambda u: u["start"]) for w in sorted(by_w)]


def block(n_rows, n_a, arm="C"):
    """列 C は始まり floor((L − n_A) / 2)、列 C′1 は floor((L − n_A) / 4)、列 C′3 は floor(3 (L − n_A) / 4)。"""
    if n_a <= 0:
        return []
    n = n_a + 1 if "m71" in MUT else n_a
    free = n_rows - n_a
    st = {"C": free // 2, "P1": free // 4, "P3": (3 * free) // 4}[arm]
    if "m70" in MUT and arm == "C":
        st = 0
    return list(range(st, min(st + n, n_rows)))


def select_rows(times, arm, s):
    """1 系列の時刻 → 採る行の番号の list の list（列 B は位相ごと、他は 1 つ）。"""
    if arm == "A":
        m = MK.mask_a(times, s)
        return [[i for i, v in enumerate(m) if v]]
    if arm in ("C", "P1", "P3"):
        n_a = sum(MK.mask_a(times, s))
        return [block(len(times), n_a, arm)]
    return MK.phases_b(times, s)


def apply_rows(writers_u, times_all, col):
    arm, s = parse(col)
    if len(times_all) != len(writers_u):
        raise SystemExit("時刻の書き手の数が data.py と違う")
    out = []
    for units, tunits in zip(writers_u, times_all):
        if len(units) != len(tunits):
            raise SystemExit("時刻の単位の数が data.py と違う")
        new = []
        for u, tu in zip(units, tunits):
            seqs, pflag = [], []
            if len(u["seqs"]) > 1:
                raise SystemExit("CoAuthor の単位は 1 系列のはず")
            for su, pf in zip(u["seqs"], u["pflag"]):
                su = np.asarray(su, dtype=np.int64)
                pf = np.asarray(pf, dtype=bool)
                if len(su) != len(tu["t"]):
                    raise SystemExit("時刻の数が系列の長さと違う")
                for rows in select_rows(tu["t"], arm, s):
                    if not rows:
                        continue
                    idx = np.asarray(rows, dtype=np.int64)
                    seqs.append(su[idx])
                    pflag.append(np.ones(len(idx), dtype=bool) if "m68" in MUT else pf[idx])
            v = dict(u)
            v["seqs"], v["pflag"] = seqs, pflag
            new.append(v)
        out.append(new)
    return out


def check_obs(writers_o, times_all):
    """data.py の o の系列と、読んだ feat 行の obs が全単位で一致することを確かめる。"""
    for units, tunits in zip(writers_o, times_all):
        for u, tu in zip(units, tunits):
            if len(u["seqs"]) != 1 or not np.array_equal(np.asarray(u["seqs"][0], dtype=np.int64), tu["obs"]):
                raise SystemExit("時刻を読んだ単位の obs が data.py の系列と違う")


def load_column(ds, work, side_path, seed, col):
    """S13 の load.load_column と同じ引数。"""
    if ds != "coauthor":
        raise SystemExit("この試験は CoAuthor だけ")
    writers, _ = pinned.ml.load(ds, work, seed)
    times_all = coauthor_times(work)
    if len(times_all) != len(writers) or any(len(a) != len(b) for a, b in zip(writers, times_all)):
        raise SystemExit("時刻を読んだ単位の並べが data.py と違う")
    check_obs(writers, times_all)
    wu = L13.apply_column(writers, L13.read_sidecar(side_path), "u")
    return apply_rows(wu, times_all, col)


# 列の番号 c（conditions D2 の表）。A1 = 1・A30 = 2 は S13 の残差の v の列の番号（u 1・n 2）と同じ。
COLS = {c: i + 1 for i, c in enumerate(
    ["A1", "A30", "A5", "A10", "A15", "C5", "C10", "C15", "C30", "B5", "B10", "B15", "B30",
     "P1-5", "P1-10", "P1-15", "P1-30", "P3-5", "P3-10", "P3-15", "P3-30"])}
