"""漏れの判定の純関数（ADR-051 D3・conditions.md）。数値を受けて判定を返すだけで、IO を持たない。

3 値: 「満たす」「満たさない」「判定不能」。天井は「満たす」の印（ceiling）として持つ。
selftest.py が、合わせ方の表の全部のマスを縛る。
"""

MEETS = "meets"
FAILS = "fails"
UNDETERMINED = "undetermined"
NOT_RUN = "not_run"

DELTA = 0.05


def three_valued(diff_lo, diff_hi, delta=DELTA):
    """差 AUC(B) − AUC(A) の両側 90% 区間から 3 値（ADR-051 D3）。"""
    if diff_hi < delta:
        return MEETS
    if diff_lo > delta:
        return FAILS
    return UNDETERMINED


def with_ceiling(diff_lo, diff_hi, auc_a_lo, delta=DELTA):
    """3 値に天井を足す。返り値は (判定, 天井か)。

    天井: 同じ引き直しの A の AUC の 5% 点が 1 − δ を超え、かつ差の上限が δ 未満（ADR-051 D3 判断 8）。
    天井は差の判定と別の合格の経路にしない: 差の上限が δ 以上なら天井にしない。
    """
    v = three_valued(diff_lo, diff_hi, delta)
    ceiling = v == MEETS and auc_a_lo > 1.0 - delta
    return v, ceiling


def combine_both(a, b):
    """両方が満たすときだけ満たす。どちらかが満たさなければ満たさない。それ以外は判定不能。

    2 つの対象（T1・T2）の合わせ方と、B の 2 つ（状態・画素）の合わせ方の両方に使う（設計 v2 §4）。
    """
    if FAILS in (a, b):
        return FAILS
    if a == MEETS and b == MEETS:
        return MEETS
    return UNDETERMINED


def combine_main_sensitivity(main, sens):
    """主と感度分析の合わせ方（ADR-051 D3 の表）。返り値は (全体, 仮に満たすか)。

    | 主 | 感度分析 | 全体 |
    | どれでも | 満たさない | 満たさない |
    | 満たさない | どれでも | 満たさない |
    | 満たす | 満たす | 満たす |
    | 満たす | 判定不能・未実施 | 判定不能（関門としては「仮に満たす」） |
    | 判定不能 | 満たさない以外 | 判定不能 |
    """
    if sens == FAILS or main == FAILS:
        return FAILS, False
    if main == MEETS and sens == MEETS:
        return MEETS, False
    if main == MEETS and sens in (UNDETERMINED, NOT_RUN):
        return UNDETERMINED, True
    return UNDETERMINED, False


def target_verdict(per_b):
    """1 つの対象について、B の 2 つ（例: {"state": (v, ceiling), "pixel": (v, ceiling)}）を合わせる。

    返り値は (判定, 天井か)。天井は両方が天井のときだけ立てる（報告で印を分けるため）。
    """
    vs = [v for v, _ in per_b.values()]
    out = vs[0]
    for v in vs[1:]:
        out = combine_both(out, v)
    ceiling = out == MEETS and all(c for _, c in per_b.values())
    return out, ceiling
