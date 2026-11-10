"""読みの形（conditions D5）の判定。selftest（P-COMP・P-PERS）と report.py が同じ関数を使う。
値は全記号の中央値。「1/2」「1/10」は読みの言い方を決める区切りで、検定ではない。"""


def part1(v):
    """1 列の部分 1: vanish（消える）/ not_follow（沿わない）/ split。v: G_o・G_p・D_o・D_p。"""
    if None in (v.get("G_o"), v.get("G_p"), v.get("D_o"), v.get("D_p")):
        return None
    dD = v["D_o"] - v["D_p"]
    if dD > 0 and v["G_o"] > 0 and v["G_p"] < v["G_o"] / 2:
        return "vanish"
    if dD > 0 and v["G_p"] >= v["G_o"]:
        return "not_follow"
    return "split"


def part2(v):
    """1 列の部分 2: others_win（他の人でも勝つ）/ own（本人に固有）。v: S0_o・G0_o。"""
    if None in (v.get("S0_o"), v.get("G0_o")):
        return None
    if v["S0_o"] > 0 and v["S0_o"] > v["G0_o"] / 10:
        return "others_win"
    return "own"


def cell_part1(labels):
    """主のセルの部分 1（3 列）: 3 列とも vanish → vanish、どれかが not_follow → not_follow、ほかは split。"""
    if None in labels:
        return None
    if all(x == "vanish" for x in labels):
        return "vanish"
    if any(x == "not_follow" for x in labels):
        return "not_follow"
    return "split"


def cell_part2(labels):
    if None in labels:
        return None
    if all(x == "others_win" for x in labels):
        return "others_win"
    if all(x == "own" for x in labels):
        return "own"
    return "split"


def form(p1, p2):
    """セルの形: A / A' / B / C。"""
    if p1 == "vanish" and p2 == "others_win":
        return "A"
    if p1 == "vanish" and p2 == "own":
        return "A'"
    if p1 == "not_follow":
        return "B"
    return "C"


def overall(forms):
    """主のセルすべてで同じ形のときだけその形、割れれば C。"""
    return forms[0] if forms and all(f == forms[0] for f in forms) else "C"
