"""列（o・u・n）を選ぶ読み込み（conditions D1）。

単位は tau-extend の data.py の読み込み（ml.load）のまま作り、u・n では系列の記号を新しい中間の u に替える。
新しい中間の o が data.py の系列と 1 つでも違えば止める（並べの取り違えを防ぐ）。
n は系列ごとに印のある行だけを採り、押下の印（pflag）も同じ行を採る。行が 1 つも残らない系列は落とすが、
単位は残す（単位とパネルの顔ぶれは o と同じ・conditions D1）。
"""
import gzip
import json

import numpy as np

import pinned

COLS = {"o": 0, "u": 1, "n": 2}


def read_sidecar(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def apply_column(writers, side, col):
    """writers: data.py の単位（o）。side: 新しい中間（同じ並べ）。col: "o"・"u"・"n"。"""
    if col == "o":
        return writers
    W = side["writers"]
    if len(W) != len(writers):
        raise SystemExit("新しい中間の書き手の数が data.py と違う")
    out = []
    for a, b in zip(writers, W):
        if len(a) != len(b):
            raise SystemExit("新しい中間の単位の数が data.py と違う")
        units = []
        for ua, ub in zip(a, b):
            if len(ua["seqs"]) != len(ub["o"]) or not all(
                    np.array_equal(np.asarray(x, dtype=np.int64), np.asarray(y, dtype=np.int64)) for x, y in zip(ua["seqs"], ub["o"])):
                raise SystemExit("新しい中間の o が data.py の系列と違う")
            seqs, pflag = [], []
            for s_u, m_n, pf in zip(ub["u"], ub["n"], ua["pflag"]):
                s_u = np.asarray(s_u, dtype=np.int64)
                pf = np.asarray(pf, dtype=bool)
                if col == "n":
                    m = np.asarray(m_n, dtype=bool)
                    s_u, pf = s_u[m], pf[m]
                if len(s_u):
                    seqs.append(s_u)
                    pflag.append(pf)
            u = dict(ua)
            u["seqs"], u["pflag"] = seqs, pflag
            units.append(u)
        out.append(units)
    return out


def load_column(ds, work, side_path, seed, col):
    writers, _ = pinned.ml.load(ds, work, seed)
    if col == "o":
        return writers
    return apply_column(writers, read_sidecar(side_path), col)
