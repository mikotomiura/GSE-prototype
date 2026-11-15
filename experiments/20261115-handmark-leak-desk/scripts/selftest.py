"""統計と判定の自己検査（run.sh の頭で回す）。失敗したら exit 1。"""
import itertools
import math
import os
import sys

import numpy as np

# -I（隔離）で起動しても同じディレクトリの部品を読む
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stats as S
import verdict as V

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def auc_brute(score, y, w=None):
    w = np.ones(len(y)) if w is None else w
    num = den = 0.0
    for i, j in itertools.product(range(len(y)), repeat=2):
        if y[i] == 1 and y[j] == 0:
            ww = w[i] * w[j]
            den += ww
            num += ww * (1.0 if score[i] > score[j] else 0.5 if score[i] == score[j] else 0.0)
    return num / den if den else float("nan")


def test_auc():
    rng = np.random.default_rng(0)
    for _ in range(30):
        n = int(rng.integers(5, 25))
        s = np.round(rng.normal(size=n), 1)        # 同点を含める
        y = (rng.random(n) < 0.4).astype(int)
        w = rng.integers(0, 3, n).astype(float)
        a, b = S.auc(s, y), auc_brute(s, y)
        check(math.isnan(a) and math.isnan(b) or abs(a - b) < 1e-12, f"AUC {a} != {b}")
        a, b = S.auc(s, y, w), auc_brute(s, y, w)
        check(math.isnan(a) and math.isnan(b) or abs(a - b) < 1e-12, f"重みつき AUC {a} != {b}")
    check(math.isnan(S.auc([1, 2], [1, 1])), "片方のクラスだけなら nan")


def test_logistic():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(400, 3))
    y = (rng.random(400) < S.sigmoid(0.5 + X @ np.array([1.0, -2.0, 0.0]))).astype(float)
    for lam in (1e-4, 1e-1):
        beta = S.fit_logistic(X, y, lam)
        p = S.sigmoid(beta[0] + X @ beta[1:])
        g = np.concatenate([[np.mean(p - y)], X.T @ (p - y) / len(y) + lam * beta[1:]])
        check(np.max(np.abs(g)) < 1e-8, f"P-GRAD: 勾配が 0 でない（λ={lam}）: {np.max(np.abs(g))}")
    big = S.fit_logistic(X, y, 1e3)
    check(np.max(np.abs(big[1:])) < 1e-3, "強い罰で係数が 0 に寄らない")


def test_verdicts():
    check(V.three_valued(-0.1, 0.049) == V.MEETS, "上限 < δ は満たす")
    check(V.three_valued(-0.1, 0.05) == V.UNDETERMINED, "上限 = δ は判定不能")
    check(V.three_valued(0.051, 0.2) == V.FAILS, "下限 > δ は満たさない")
    check(V.three_valued(0.05, 0.2) == V.UNDETERMINED, "下限 = δ は判定不能")
    check(V.with_ceiling(-0.01, 0.01, 0.96) == (V.MEETS, True), "天井")
    check(V.with_ceiling(-0.01, 0.01, 0.95) == (V.MEETS, False), "A の下限 = 1 − δ は天井でない")
    check(V.with_ceiling(0.0, 0.06, 0.99) == (V.UNDETERMINED, False), "差の上限が δ 以上なら天井でも満たさない")
    vals = (V.MEETS, V.FAILS, V.UNDETERMINED)
    for a, b in itertools.product(vals, vals):
        got = V.combine_both(a, b)
        want = V.FAILS if V.FAILS in (a, b) else V.MEETS if a == b == V.MEETS else V.UNDETERMINED
        check(got == want, f"combine_both({a},{b})")
    table = {
        (V.MEETS, V.MEETS): (V.MEETS, False),
        (V.MEETS, V.FAILS): (V.FAILS, False),
        (V.MEETS, V.UNDETERMINED): (V.UNDETERMINED, True),
        (V.MEETS, V.NOT_RUN): (V.UNDETERMINED, True),
        (V.FAILS, V.MEETS): (V.FAILS, False),
        (V.FAILS, V.FAILS): (V.FAILS, False),
        (V.FAILS, V.UNDETERMINED): (V.FAILS, False),
        (V.FAILS, V.NOT_RUN): (V.FAILS, False),
        (V.UNDETERMINED, V.MEETS): (V.UNDETERMINED, False),
        (V.UNDETERMINED, V.FAILS): (V.FAILS, False),
        (V.UNDETERMINED, V.UNDETERMINED): (V.UNDETERMINED, False),
        (V.UNDETERMINED, V.NOT_RUN): (V.UNDETERMINED, False),
    }
    for (m, s), want in table.items():
        check(V.combine_main_sensitivity(m, s) == want, f"主 {m} × 感度 {s}")
    check(V.target_verdict({"state": (V.MEETS, True), "pixel": (V.MEETS, False)}) == (V.MEETS, False), "天井は両方のとき")
    check(V.target_verdict({"state": (V.MEETS, False), "pixel": (V.FAILS, False)}) == (V.FAILS, False), "B の片方が満たさない")


def test_day_bootstrap():
    """日を単位に引き直す: 陽性が 1 日目だけ・陰性が 2 日目だけなら、標本の半分ほどで片方のクラスが欠ける。

    窓の単位で引き直すとほとんど欠けない（変異 m2 を赤にする対照 P-DAY）。
    """
    groups = np.array([0] * 30 + [1] * 30)
    y = np.array([1] * 30 + [0] * 30, dtype=float)
    rng = np.random.default_rng(9)
    p = rng.random(60)
    _, _, dropped = S.fixed_bootstrap([p], [p], [y], groups, 400, np.random.default_rng(10))
    check(120 <= dropped <= 280, f"P-DAY: 日の引き直しで欠けた標本が {dropped}/400（半分ほどのはず）")
    w = S.weights_for(np.array([1, 1, 0]), groups)
    check(np.all(w[:30] == 1) and np.all(w[30:] == 2), "weights_for は日の回数")


def fake_rows(days, per_day, leak, rng):
    """A は打鍵の量だけ・対象は A と隠れた量の両方に依る・B_state に隠れた量を leak の強さで混ぜる。"""
    rows = []
    for d in range(days):
        for _ in range(per_day):
            a = rng.normal(size=22)
            hidden = rng.normal()
            y = int(rng.random() < S.sigmoid(1.0 * a[0] + 2.0 * hidden))
            b = list(rng.normal(size=13))
            b[0] = leak * hidden + (1 - leak) * b[0]
            rows.append({"day": d, "a": list(a), "b_state": b, "t1": y, "t1_all": y, "t2": int(rng.integers(0, 3)),
                         "t_since_t0": int(rng.integers(30_000, 3_600_000))})
    return rows


def test_analysis_controls():
    """統計の部分だけの対照: 隠れた量を B に入れれば満たさない・入れなければ満たさない以外（設計 v2 §6 S1）。"""
    header = {"a_names": [f"a{i}" for i in range(22)]}
    header["a_names"][:8] = S.A2_BASE
    rng = np.random.default_rng(2)
    leak = S.analyse(fake_rows(10, 60, 1.0, rng), header, None, seed=3, R=300, diagnostics=False)
    check(leak["targets"]["T1"].get("state", {}).get("verdict") == V.FAILS, f"P-LEAK: 漏れを入れて満たさないにならない: {leak['targets']['T1']}")
    none = S.analyse(fake_rows(10, 60, 0.0, rng), header, None, seed=3, R=300, diagnostics=False)
    check(none["targets"]["T1"].get("state", {}).get("verdict") != V.FAILS, "漏れが無いのに満たさない")
    check(none["targets"]["T1"]["pixel"]["verdict"] == V.UNDETERMINED and none["targets"]["T1"]["verdict"] != V.MEETS,
          "画素の特徴が無いのに対象が満たす")
    few = S.analyse(fake_rows(5, 60, 0.0, rng), header, None, seed=3, R=50, diagnostics=False)
    check(few["overall"] == V.UNDETERMINED, "日が足りなければ判定不能")
    r1 = S.analyse(fake_rows(9, 40, 0.5, np.random.default_rng(4)), header, None, seed=5, R=100, diagnostics=False)
    r2 = S.analyse(fake_rows(9, 40, 0.5, np.random.default_rng(4)), header, None, seed=5, R=100, diagnostics=False)
    r1.pop("seconds", None)
    r2.pop("seconds", None)
    check(r1 == r2, "同じ種で同じ結果")
    # 判定に入れない処理（診断・入れ子）の有無で、主の区間と判定が変わらない（乱数の流れを分ける）
    r3 = S.analyse(fake_rows(9, 40, 0.5, np.random.default_rng(4)), header, None, seed=5, R=100, diagnostics=True,
                   R_nested=20)
    for t in ("T1", "T2"):
        a, b = r1["targets"][t].get("state", {}), r3["targets"][t].get("state", {})
        check((a.get("ci90"), a.get("verdict")) == (b.get("ci90"), b.get("verdict")),
              f"{t}: 診断・入れ子の有無で主の区間が変わる")
        check("verdict" in b.get("nested", {}) or t == "T2" and r3["targets"][t].get("reason"),
              f"{t}: 入れ子にも判定が付く")


def test_sensitivity_wiring():
    """主と感度分析の合わせ方の配線（C7・ADR-051 D3）。表そのものは test_verdicts が縛る。"""
    header = {"a_names": [f"a{i}" for i in range(22)]}
    header["a_names"][:8] = S.A2_BASE
    rows = fake_rows(9, 40, 0.0, np.random.default_rng(6))
    r = S.with_sensitivity(rows, header, None, seed=7, R=100, diagnostics=False)
    check(r["sensitivity"]["overall"] == V.NOT_RUN, "印の無い窓だけなら感度分析は未実施")
    check(r["combined"]["overall"] == V.combine_main_sensitivity(r["overall"], V.NOT_RUN)[0], "未実施の合わせ方")
    leak = fake_rows(10, 60, 1.0, np.random.default_rng(8))
    for x in leak:
        x["sens"] = True
    r = S.with_sensitivity(leak, header, None, seed=7, R=200, diagnostics=False)
    check(r["targets"]["T1"]["state"]["verdict"] == V.FAILS, "P-SENS: 主が漏れを拾わない")
    check(r["sensitivity"].get("targets", {}).get("T1", {}).get("state", {}).get("verdict") == V.FAILS, "P-SENS: 印の窓の感度分析が漏れを拾わない")
    check(r["combined"]["overall"] == V.FAILS, "感度分析が満たさないなら全体も満たさない")
    few = fake_rows(9, 40, 0.0, np.random.default_rng(9))
    for x in few:
        x["sens"] = x["day"] < 3
    r = S.with_sensitivity(few, header, None, seed=7, R=100, diagnostics=False)
    check(r["sensitivity"]["overall"] == V.UNDETERMINED and r["sensitivity"]["n_days"] == 3,
          "感度分析は印の窓だけで回り、日が足りなければ判定不能")


def test_prepare_records():
    """記録の写しの行の分け方（C2）: \n だけで分け、最後の行だけを救う。"""
    import json
    import prepare_records as P
    u2028 = json.dumps({"type": "x", "s": "a\u2028b"}, ensure_ascii=False).encode()
    good = b'{"type":"meta","session_start":1}\n' + u2028 + b"\n"
    lines, cut = P.split_lines(good)
    check(len(lines) == 2 and not cut, "U+2028 を含む行を 2 つに割った")
    cutmb = good + '{"type":"key","s":"あ'.encode()[:-1]
    lines, cut = P.split_lines(cutmb)
    check(len(lines) == 2 and cut, "多バイト文字の途中で切れた最後の行を除かない")
    mid = b'{"type":"meta"}\nnot json\n{"a":1}\n'
    lines, cut = P.split_lines(mid)
    check(len(lines) == 3 and not cut, "途中の壊れた行を勝手に除いた（gse-replay が止めるべき）")
    check(P.split_lines(b"") == ([], False), "空の記録")


def main():
    test_auc()
    test_logistic()
    test_verdicts()
    test_day_bootstrap()
    test_analysis_controls()
    test_sensitivity_wiring()
    test_prepare_records()
    if FAILS:
        for f in FAILS:
            print("FAIL:", f)
        sys.exit(1)
    print("selftest OK")


if __name__ == "__main__":
    main()
