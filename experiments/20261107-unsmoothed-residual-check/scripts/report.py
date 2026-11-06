"""parts/ の集計を summary.json にまとめ、tables.md を作る（conditions V3）。読みの語は D5 の形を機械で当てる。

使い方: python3 -I report.py <out_dir> [--run-id ID]
集計値だけを書く（書き手・セッション・課題の番号を書かない）。
"""
import glob
import json
import os
import sys

COLS = ["o", "u", "n"]
DSETS = {"coauthor": "P15", "cs1": "C5"}
MAIN = [("coauthor", "5"), ("coauthor", "15"), ("cs1", "5")]
QTY = {"G": ("hmm3", "tau_other", "all/self_minus_pool_same"),
       "C2a": ("hmm3", "tau_other", "all/self_minus_r1"),
       "C2b": (None, "two_stage_other", "all/self_minus_r1")}
FREE_ORDER = ["hmm3", "ar1", "ar2", "ar3"]  # 自由な母数の少ない順（同数の最頻の構造はこの順で先）


def load_parts(out):
    S = {}
    for p in sorted(glob.glob(os.path.join(out, "parts", "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        kind = os.path.basename(p).split(".")[0]
        S.setdefault(d["column"], {}).setdefault(d["dataset"], {})
        if kind == "fit":
            S[d["column"]][d["dataset"]]["fit"] = d["fit"]
            S[d["column"]][d["dataset"]]["pin_sha256"] = d["pin_sha256"]
        else:
            S[d["column"]][d["dataset"]]["residual"] = d["residual"]
            S[d["column"]][d["dataset"]]["npz_check"] = d["npz_check"]
    return S


def cell(S, col, ds, k):
    try:
        return S[col][ds]["fit"]["em"][DSETS[ds]][k]
    except KeyError:
        return None


def qty(E, name):
    if E is None:
        return None
    s, row, key = QTY[name]
    c = E["two_stage"]["other"][row][key] if s is None else E["structs"][s][row][key]
    return None if c is None or c.get("suppressed") else c


def word_u(o, u):
    """u と o の比べ（D5）。o が 0 なら比べない。"""
    if o is None or u is None:
        return None
    if o == 0:
        return "比べない（o = 0）"
    if u == 0:
        return "縮む"  # 向きが無く、大きさは |o| / 2 より小さい
    if (u > 0) != (o > 0):
        return "逆"
    return "残る" if abs(u) >= abs(o) / 2 else "縮む"


def word_n(o, n):
    if o is None or n is None:
        return None
    if o == 0:
        return "比べない（o = 0）"
    if n == 0:
        return "0"
    return "同じ向き" if (n > 0) == (o > 0) else "逆"


def modal_struct(E):
    c = E["two_stage"]["other"]["chosen_struct"] if E else None
    if not c or c.get("suppressed"):
        return None
    best = max(c.values())
    return [s for s in FREE_ORDER if c.get(s) == best][0]


def r1med(R, model, ax):
    try:
        c = R["models"][model]["acf_" + ax]["1"]
    except (KeyError, TypeError):
        return None
    return None if c is None or c.get("suppressed") else c["median"]


def readings(S):
    out = dict(columns={}, residual={})
    for name in QTY:
        for col, fw in (("u", word_u), ("n", word_n)):
            words, vals = [], []
            for ds, k in MAIN:
                o, x = qty(cell(S, "o", ds, k), name), qty(cell(S, col, ds, k), name)
                ov, xv = (o or {}).get("median"), (x or {}).get("median")
                vals.append(dict(cell="%s/%s/k%s" % (ds, DSETS[ds], k), o=ov, **{col: xv}, word=fw(ov, xv)))
                words.append(fw(ov, xv))
            same = len(set(words)) == 1 and words[0] is not None and not words[0].startswith("比べない")
            out["columns"]["%s/%s" % (name, col)] = dict(cells=vals, reading=words[0] if same else "割れる")
    for col in COLS:
        for ds, k in MAIN:
            E = cell(S, col, ds, k)
            try:
                R = S[col][ds]["residual"][DSETS[ds]][k]
            except KeyError:
                continue
            ms = modal_struct(E)
            v = {m: {ax: r1med(R, m, ax) for ax in ("x", "y")} for m in ("pool_hmm3", "pool_" + ms if ms else None, "r1") if m}
            word = "どちらでもない"
            if ms and ms.startswith("ar") and all(v[m][ax] is not None for m in v for ax in ("x", "y")):
                ar = "pool_" + ms
                carries = all(abs(v[ar][ax]) < abs(v["pool_hmm3"][ax]) for ax in ("x", "y"))
                if carries:
                    word = "ar でも残る" if all(abs(v[ar][ax]) >= abs(v["r1"][ax]) for ax in ("x", "y")) else "ar で運べる"
            out["residual"]["%s/%s/%s/k%s" % (col, ds, DSETS[ds], k)] = dict(modal_struct=ms, lag1_median=v, reading=word)
    return out


def fmt(x):
    return "—" if x is None else ("%.4f" % x if isinstance(x, float) else str(x))


def tables(S, Rd):
    L = ["# 表（report.py が summary.json から作る・集計値だけ）", ""]
    L += ["## 列の比べ（D5・全記号の中央値）", "", "| 量 / 列 | セル | o | 列の値 | 語 |", "|---|---|---|---|---|"]
    for key, d in Rd["columns"].items():
        col = key.split("/")[1]
        for c in d["cells"]:
            L.append("| %s | %s | %s | %s | %s |" % (key, c["cell"], fmt(c["o"]), fmt(c[col]), fmt(c["word"])))
        L.append("| %s | 読み | | | %s |" % (key, d["reading"]))
    L += ["", "## 尤度の差（列ごと・主のセルと k = 1）", "", "| 列 | セル | 量 | 中央値 | 四分位 | 良い側の割合 | 人数 | 欠け |",
          "|---|---|---|---|---|---|---|---|"]
    for col in COLS:
        for ds, pn in DSETS.items():
            for k in (["1", "5", "15"] if ds == "coauthor" else ["1", "5"]):
                E = cell(S, col, ds, k)
                for name in QTY:
                    c = qty(E, name)
                    if c is None:
                        L.append("| %s | %s/%s/k%s | %s | — | — | — | — | %s |" % (col, ds, pn, k, name, fmt(E and E.get("missing"))))
                        continue
                    L.append("| %s | %s/%s/k%s | %s | %s | %s〜%s | %s | %s | %s |" % (
                        col, ds, pn, k, name, fmt(c["median"]), fmt(c["q25"]), fmt(c["q75"]), fmt(c.get("better_share")), c["n"],
                        fmt(E.get("missing"))))
    L += ["", "## 残差の遅れ 1 の自己相関（中央値・主のセル）", "", "| セル | 最頻の構造 | モデル | zx | zy | 読み |", "|---|---|---|---|---|---|"]
    for key, d in Rd["residual"].items():
        for m, v in d["lag1_median"].items():
            L.append("| %s | %s | %s | %s | %s | %s |" % (key, fmt(d["modal_struct"]), m, fmt(v["x"]), fmt(v["y"]), d["reading"]))
    L += ["", "## 残差の遅れ 1〜10・較正（列 × セル × モデル・中央値）", ""]
    for col in COLS:
        for ds, pn in DSETS.items():
            for k in (["1", "5", "15"] if ds == "coauthor" else ["1", "5"]):
                try:
                    R = S[col][ds]["residual"][pn][k]
                except KeyError:
                    continue
                L += ["### %s %s/%s/k%s（書き手 %d）" % (col, ds, pn, k, R["writers"]), "",
                      "| モデル | 軸 | " + " | ".join("r%d" % l for l in range(1, 11)) + " | 平均 | 分散 | 押下の r1 | 25 の割合 |",
                      "|---|---|" + "---|" * 14]
                for m, A in R["models"].items():
                    for ax in ("x", "y"):
                        rs = [A["acf_" + ax][str(l)] for l in range(1, 11)]
                        med = lambda c: None if c is None or c.get("suppressed") else c["median"]  # noqa: E731
                        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                            m, ax, " | ".join(fmt(med(c)) for c in rs), fmt(med(A["mean_" + ax])), fmt(med(A["var_" + ax])),
                            fmt(med(A["acf1_pressed_" + ax])), fmt(med(A["share25"]))))
                L.append("")
    return "\n".join(L) + "\n"


def main(argv):
    out = argv[0]
    run_id = argv[argv.index("--run-id") + 1] if "--run-id" in argv else None
    S = load_parts(out)
    Rd = readings(S)
    json.dump(dict(run_id=run_id, columns=S, readings=Rd), open(os.path.join(out, "summary.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(out, "tables.md"), "w", encoding="utf-8").write(tables(S, Rd))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
