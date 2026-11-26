"""結果の置き場の elapsed_*.json と leak_*.json を、Markdown の表にまとめる（数だけ・日付や時刻は書かない）。

  python report.py <dir>      （controls なら下の negative・clock_stop・clock_start・leak も読む）
"""
import glob
import json
import os
import sys


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def fmt(x, nd=3):
    return "—" if x is None else f"{x:.{nd}f}"


def elapsed_table(paths):
    lines = ["| 版・層 | 確かめ | 項目 | 止まり | 日 | ρ リッジ | ρ 近傍 | 統計量 | 帰無 95% 点 | 帰無の平均 ± SD | p | 判定 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in paths:
        r = load(p)
        for t in ("i", "ii", "iii"):
            v = r["tests"][t]
            nl = v.get("null", {})
            lines.append("| {} | ({}) | {} | {} | {} | {} | {} | {} | {} | {} ± {} | {} | {} |".format(
                r.get("tag") or os.path.basename(p), t, v.get("n_items"), v.get("n_stops", "—"), v.get("n_days", "—"),
                fmt(v.get("rho_ridge")), fmt(v.get("rho_knn")), fmt(v.get("stat")), fmt(nl.get("q95")),
                fmt(nl.get("mean")), fmt(nl.get("sd")), fmt(v.get("p")), v.get("verdict")))
    return lines


def leak_table(paths):
    lines = ["| 版 | 窓 | 日 | T1 B′_state | T1 B_pixel′ | T2 B′_state | T2 B_pixel′ | 主 |",
             "|---|---|---|---|---|---|---|---|"]
    for p in paths:
        r = load(p)
        cell = []
        for t in ("T1", "T2"):
            for b in ("state", "pixel"):
                v = r.get("targets", {}).get(t, {}).get(b, {})
                ci = v.get("ci90")
                cell.append(f"{v.get('verdict')}（{fmt(ci[0], 4)}〜{fmt(ci[1], 4)}）" if ci else str(v.get("verdict")))
        tag = os.path.basename(p)[len("leak_"):-len(".json")]
        lines.append(f"| {tag} | {r.get('n_windows')} | {r.get('n_days')} | " + " | ".join(cell)
                     + f" | {r.get('combined', {}).get('main')} |")
    return lines


def main(d):
    out = [f"# 止まりの層の机上の確かめ（{os.path.basename(os.path.normpath(d))}）", ""]
    subs = [d] + sorted(x for x in glob.glob(os.path.join(d, "*")) if os.path.isdir(x))
    for s in subs:
        el = sorted(glob.glob(os.path.join(s, "elapsed_*.json")))
        lk = sorted(glob.glob(os.path.join(s, "leak_*.json")))
        if not el and not lk:
            continue
        out.append(f"## {os.path.relpath(s, d) if s != d else '本体'}")
        out.append("")
        if el:
            out += ["### 経過が読めないこと (i)〜(iii)（片側 5%・判断 9）", ""] + elapsed_table(el) + [""]
        if lk:
            out += ["### 漏れの検査（ADR-051 D3・δ = 0.05）", ""] + leak_table(lk) + [""]
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
