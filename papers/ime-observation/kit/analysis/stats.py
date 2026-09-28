#!/usr/bin/env python3
# kit: selftest
"""E1（L1 / L2）と E2 が使う統計の部品（Python 標準ライブラリだけ）。

  stats.py --selftest      既知の値・閉じた式・性質・陽性/陰性対照（速い既定・1 秒未満）

  wilson(x, n, conf)                       割合の Wilson 区間（検出の適合率・再現率）
  cluster_bootstrap(clusters, stat, ...)   クラスタ（ブロック）を単位にしたブートストラップ区間
  bland_altman(a, b)                       偏りと一致限界（dwell_ms・L2 の測度）
  cohen_kappa(table)                       k x k の分割表の Cohen の kappa（abandon）
  icc(matrix, kind)                        級内相関 ICC(1,1) / (2,1) / (3,1)（L2 の絶対一致は (2,1)）
  median_abs_error(a, b)                   対の中央絶対誤差

★ 推定で書く（検定しない）。区間は「その値が正しいと言える幅」ではなく、この標本から見える幅である。
⚠️ 「求められない」は None で返す（0 件・1 クラスタ・分散 0 など）。0 や nan に丸めない
   —— 論文の表に 0 として載ると、推定できなかったことが読み取れなくなる。
⚠️ 乱数は random.Random(seed) の**インスタンス**だけを使う。グローバルな乱数状態は読みも書きもしない。

出典（著者・年・題だけ。`[Pn]` の採番は docs/references.md の管轄で本ファイルの範囲外）:
  - Wilson (1927) Probable inference, the law of succession, and statistical inference
  - Bland & Altman (1986) Statistical methods for assessing agreement between two methods of clinical measurement
  - Cohen (1960) A coefficient of agreement for nominal scales
  - Shrout & Fleiss (1979) Intraclass correlations: uses in assessing rater reliability
  - Efron (1979) Bootstrap methods: another look at the jackknife（パーセンタイル法）
"""
import argparse
import math
import random
import statistics
import sys

# Bland-Altman の一致限界の係数。慣習は 1.96（正規分布の 97.5% 点の丸め）。
BA_Z = 1.96


def _check_conf(conf):
    if not isinstance(conf, (int, float)) or isinstance(conf, bool) or not (0.0 < conf < 1.0):
        raise ValueError("conf は 0 より大きく 1 より小さい数")


def _z(conf):
    """両側 conf の正規分布の臨界値（conf = 0.95 なら 1.959964）。"""
    return statistics.NormalDist().inv_cdf((1.0 + conf) / 2.0)


def _is_count(v):
    return isinstance(v, int) and not isinstance(v, bool)


def wilson(x, n, conf=0.95):
    """割合 x / n の Wilson 区間 (lo, hi)。n = 0 は (None, None)。

    ★ 0 件・全件でも区間が [0, 1] に収まり、端で 0 幅にならない（Wald 区間との違い）。
    区間は x / n を必ず含む。
    """
    _check_conf(conf)
    if not (_is_count(x) and _is_count(n)) or n < 0 or x < 0 or x > n:
        raise ValueError("x, n は 0 <= x <= n の整数")
    if n == 0:
        return (None, None)
    z = _z(conf)
    z2 = z * z
    p = x / n
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / denom
    # x = 0 の下限と x = n の上限は数学的にちょうど 0 と 1（center と half が打ち消し合う）。
    # 浮動小数の誤差（2.8e-17 など）で x/n を含まなくなるのを防ぐため、その 2 つは明示する。
    lo = 0.0 if x == 0 else max(0.0, center - half)
    hi = 1.0 if x == n else min(1.0, center + half)
    return (lo, hi)


def _percentile(sorted_vals, q):
    """整列済みの列の q 分位（線形補間・q は 0..1）。"""
    pos = q * (len(sorted_vals) - 1)
    i = int(math.floor(pos))
    j = min(i + 1, len(sorted_vals) - 1)
    return sorted_vals[i] + (sorted_vals[j] - sorted_vals[i]) * (pos - i)


def cluster_bootstrap(clusters, stat, B, seed, conf=0.95):
    """クラスタを単位に復元抽出するブートストラップのパーセンタイル区間 (lo, hi)。

    clusters: クラスタごとの値の配列（例: ブロックごとの試行の値）。
    stat: 抽出したクラスタの列（各クラスタは tuple）を受けて 1 つの有限な数を返す関数。
          ⚠️ 渡されるクラスタは元と同じ中身のまま（要素を混ぜない）。クラスタ内の相関を保つのが目的。
    B: 反復回数。seed: 整数（random.Random(seed) だけを使う）。

    ⚠️ クラスタが 2 個未満なら (None, None)（1 個だと区間が 1 点に潰れ、狭く見えて誤解を生む）。
    ⚠️ stat が None / 非有限を返したら ValueError（黙って捨てると区間が偏る。stat の側で扱うこと）。
    ★ 抽出位置には Random.random() だけを使う。Python の文書が、seed と random() の列だけは
       版を跨いで変わらないと保証しているため（randrange などは版で変わりうる）。
    """
    _check_conf(conf)
    if not _is_count(B) or B < 1:
        raise ValueError("B は 1 以上の整数")
    if not _is_count(seed):
        raise ValueError("seed は整数")
    cl = [tuple(c) for c in clusters]
    k = len(cl)
    if k < 2:
        return (None, None)
    rng = random.Random(seed)
    reps = []
    for _ in range(B):
        sample = [cl[min(k - 1, int(rng.random() * k))] for _ in range(k)]
        v = stat(sample)
        if v is None or not math.isfinite(v):
            raise ValueError("stat が有限でない値を返した（None / nan / inf）")
        reps.append(v)
    reps.sort()
    a = (1.0 - conf) / 2.0
    return (_percentile(reps, a), _percentile(reps, 1.0 - a))


def _paired(a, b):
    a, b = list(a), list(b)
    if len(a) != len(b):
        raise ValueError("a と b は同じ長さの対でなければならない（%d と %d）" % (len(a), len(b)))
    return a, b


def bland_altman(a, b):
    """差 a - b の偏りと一致限界。{"bias", "sd", "loa_lo", "loa_hi", "n"}。

    sd は標本標準偏差（n - 1 で割る）。一致限界 = bias ± 1.96 * sd。
    ⚠️ n = 0 は bias も None、n = 1 は sd と一致限界が None（分散が定義できない）。
    """
    a, b = _paired(a, b)
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    if n == 0:
        return {"bias": None, "sd": None, "loa_lo": None, "loa_hi": None, "n": 0}
    bias = statistics.fmean(d)
    if n == 1:
        return {"bias": bias, "sd": None, "loa_lo": None, "loa_hi": None, "n": 1}
    sd = statistics.stdev(d)
    return {"bias": bias, "sd": sd, "loa_lo": bias - BA_Z * sd, "loa_hi": bias + BA_Z * sd, "n": n}


def cohen_kappa(table):
    """k x k の分割表（行 = 評定者 1・列 = 評定者 2・度数）の Cohen の kappa。

    kappa = (po - pe) / (1 - pe)。po = 一致率・pe = 周辺度数から見た偶然の一致率。
    ⚠️ 総数 0、または pe = 1（両者が同じ 1 カテゴリだけを使った）は定義できないので None。
    """
    t = [list(r) for r in table]
    k = len(t)
    if k == 0 or any(len(r) != k for r in t):
        raise ValueError("table は k x k（k >= 1）")
    if any((not isinstance(v, (int, float))) or isinstance(v, bool) or v < 0 or not math.isfinite(v)
           for r in t for v in r):
        raise ValueError("table の度数は 0 以上の有限な数")
    n = float(sum(sum(r) for r in t))
    if n == 0:
        return None
    po = sum(t[i][i] for i in range(k)) / n
    rows = [sum(t[i]) for i in range(k)]
    cols = [sum(t[i][j] for i in range(k)) for j in range(k)]
    pe = sum(rows[i] * cols[i] for i in range(k)) / (n * n)
    if pe == 1.0:
        return None
    return (po - pe) / (1.0 - pe)


def icc(matrix, kind="2,1"):
    """級内相関。matrix は n 行（対象）x k 列（評定者・方法）。二元配置の分散分析の平均平方から。

      "1,1"  ICC(1,1)  一元配置・単一評定者（評定者の効果を分けない）
      "2,1"  ICC(2,1)  二元ランダム・単一評定者・**絶対一致**（評定者間の偏りも不一致に数える）★ L2 の主評価
      "3,1"  ICC(3,1)  二元混合・単一評定者・**整合性**（評定者ごとの一定の偏りは不一致に数えない）

    Shrout & Fleiss (1979) の式: BMS = 対象の平均平方・JMS = 評定者の平均平方・EMS = 残差・WMS = 対象内。
    ⚠️ 分母が 0（全員が全部同じ値）は None。n >= 2 行・k >= 2 列が要る（満たさなければ ValueError ——
       「求められない値」の None とは別。呼び出し側は形の誤りとして扱う）。
    ★ 先に全体を 1 つの値だけ平行移動してから計算する（ICC は平行移動で不変）。0.1 のような値が全員で揃うと、
       総平均の丸めで分母が 0 にならず、でたらめな値が出るため（全員同じなら偏差がちょうど 0 になる）。
    """
    if kind not in ("1,1", "2,1", "3,1"):
        raise ValueError('kind は "1,1" / "2,1" / "3,1"')
    m = [list(r) for r in matrix]
    n = len(m)
    k = len(m[0]) if n else 0
    if n < 2 or k < 2 or any(len(r) != k for r in m):
        raise ValueError("matrix は n >= 2 行・k >= 2 列の長方形")
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for r in m for v in r):
        raise ValueError("matrix の値は有限な数")
    base = m[0][0]
    m = [[v - base for v in r] for r in m]
    grand = sum(sum(r) for r in m) / (n * k)
    row_mean = [sum(r) / k for r in m]
    col_mean = [sum(m[i][j] for i in range(n)) / n for j in range(k)]
    ss_total = sum((v - grand) ** 2 for r in m for v in r)
    ss_rows = k * sum((rm - grand) ** 2 for rm in row_mean)
    ss_cols = n * sum((cm - grand) ** 2 for cm in col_mean)
    ss_err = ss_total - ss_rows - ss_cols
    ss_within = ss_total - ss_rows
    bms = ss_rows / (n - 1)
    jms = ss_cols / (k - 1)
    ems = ss_err / ((n - 1) * (k - 1))
    wms = ss_within / (n * (k - 1))
    if kind == "1,1":
        num, den = bms - wms, bms + (k - 1) * wms
    elif kind == "2,1":
        num, den = bms - ems, bms + (k - 1) * ems + k * (jms - ems) / n
    else:
        num, den = bms - ems, bms + (k - 1) * ems
    # 分母は数学的に 0 以上（n >= 2, k >= 2）。丸めで負や 0 になったら求められないとみなす
    if den <= 0:
        return None
    return num / den


def median_abs_error(a, b):
    """対の中央絶対誤差 median(|a - b|)。対が 0 個なら None。"""
    a, b = _paired(a, b)
    if not a:
        return None
    return statistics.median(abs(x - y) for x, y in zip(a, b))


# ---------------------------------------------------------------- selftest
# Shrout & Fleiss (1979) の例: 6 対象（行）x 4 評定者（列）。
SF_MATRIX = [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]]
Z95 = 1.959963984540054


def _mean_of_clusters(cs):
    return sum(sum(c) for c in cs) / sum(len(c) for c in cs)


def selftest():
    fails = []
    count = [0]

    def check(name, cond, detail=""):
        count[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    def near(name, got, want, tol):
        check(name, got is not None and abs(got - want) <= tol, "got %r want %r（許容 %g）" % (got, want, tol))

    def raises(name, fn, exc=ValueError):
        count[0] += 1
        try:
            fn()
        except exc:
            return
        except Exception as e:  # 別の例外は「拒否」と数えない
            fails.append("%s 別の例外: %r" % (name, e))
            return
        fails.append("%s 例外が出なかった" % name)

    # --- ICC: 文献の値（4 桁）
    near("ICC(1,1) = 0.1657 (Shrout & Fleiss)", icc(SF_MATRIX, kind="1,1"), 0.1657, 0.0005)
    near("ICC(2,1) = 0.2898 (Shrout & Fleiss)", icc(SF_MATRIX, kind="2,1"), 0.2898, 0.0005)
    near("ICC(3,1) = 0.7148 (Shrout & Fleiss)", icc(SF_MATRIX, kind="3,1"), 0.7148, 0.0005)
    near("ICC の既定は 2,1", icc(SF_MATRIX), icc(SF_MATRIX, kind="2,1"), 0.0)
    # 性質: 絶対一致 (2,1) は評定者の偏りを不一致に数え、整合性 (3,1) は数えない（型の取り違えを検出する）
    shifted = [[r[0], r[1], r[2], r[3] + 5] for r in SF_MATRIX]
    near("ICC(3,1) は 1 列に定数を足しても変わらない", icc(shifted, kind="3,1"), icc(SF_MATRIX, kind="3,1"), 1e-9)
    check("ICC(2,1) は 1 列に定数を足すと下がる", icc(shifted, kind="2,1") < icc(SF_MATRIX, kind="2,1") - 0.05,
          "%r -> %r" % (icc(SF_MATRIX, kind="2,1"), icc(shifted, kind="2,1")))
    ident = [[1, 1], [3, 3], [2, 2], [5, 5]]
    for kd in ("1,1", "2,1", "3,1"):
        near("ICC(%s) 完全一致は 1" % kd, icc(ident, kind=kd), 1.0, 1e-12)
    near("ICC は対象（行）の並べ替えで不変", icc(list(reversed(SF_MATRIX)), kind="2,1"), icc(SF_MATRIX, kind="2,1"), 1e-12)
    near("ICC は評定者（列）の並べ替えで不変", icc([list(reversed(r)) for r in SF_MATRIX], kind="2,1"),
         icc(SF_MATRIX, kind="2,1"), 1e-12)
    check("ICC 全員が同じ値なら None", icc([[3, 3], [3, 3], [3, 3]]) is None)
    for kd in ("1,1", "2,1", "3,1"):
        # ★ 総平均の丸めで分母が 0 にならない値（0.1）でも None になること
        check("ICC(%s) 全員が 0.1 なら None" % kd, icc([[0.1, 0.1]] * 3, kind=kd) is None,
              repr(icc([[0.1, 0.1]] * 3, kind=kd)))
        check("ICC(%s) 3 列とも 0.1 なら None" % kd, icc([[0.1] * 3] * 3, kind=kd) is None,
              repr(icc([[0.1] * 3] * 3, kind=kd)))
    raises("ICC 未知の kind", lambda: icc(SF_MATRIX, kind="2,k"))
    raises("ICC 長方形でない", lambda: icc([[1, 2], [3]]))
    raises("ICC 1 行だけ", lambda: icc([[1, 2]]))

    # --- Wilson: 閉じた式
    near("Wilson 0/10 の上限 = z^2/(n+z^2) = 0.2775", wilson(0, 10)[1], 0.2775, 0.0005)
    near("Wilson 10/10 の下限 = n/(n+z^2) = 0.7225", wilson(10, 10)[0], 0.7225, 0.0005)
    near("Wilson 0/10 の下限は 0", wilson(0, 10)[0], 0.0, 0.0)
    near("Wilson 10/10 の上限は 1", wilson(10, 10)[1], 1.0, 0.0)
    near("Wilson 0/1 の上限 = z^2/(1+z^2)", wilson(0, 1)[1], Z95 ** 2 / (1 + Z95 ** 2), 1e-12)
    near("Wilson conf=0.90 の 0/10 の上限（z = 1.6448536）", wilson(0, 10, conf=0.90)[1],
         1.6448536 ** 2 / (10 + 1.6448536 ** 2), 1e-6)
    check("Wilson n = 0 は (None, None)", wilson(0, 0) == (None, None))
    inside, mirror, defining = True, True, True
    for n in list(range(1, 61)) + [1000]:
        for x in range(0, n + 1):
            lo, hi = wilson(x, n)
            if not (0.0 <= lo <= x / n <= hi <= 1.0):
                inside = False
            lo2, hi2 = wilson(n - x, n)
            if abs((1.0 - hi) - lo2) > 1e-12 or abs((1.0 - lo) - hi2) > 1e-12:
                mirror = False
            # 定義式: 区間の端 p は (x/n - p)^2 = z^2 p (1 - p) / n を満たす（スコア検定の反転）。端が 0 / 1 に
            # 丸められた場合は除く。
            for p in (lo, hi):
                if 0.0 < p < 1.0 and abs((x / n - p) ** 2 - Z95 ** 2 * p * (1 - p) / n) > 1e-12:
                    defining = False
    check("Wilson の区間が常に [0, 1] に収まり x/n を含む（n <= 60 と 1000 の全 x）", inside)
    check("Wilson は x と n - x で鏡像", mirror)
    check("Wilson の端はスコア検定の定義式を満たす", defining)
    raises("Wilson x > n", lambda: wilson(5, 3))
    raises("Wilson x < 0", lambda: wilson(-1, 3))
    raises("Wilson conf = 1", lambda: wilson(1, 3, conf=1.0))

    # --- Cohen の kappa
    near("kappa [[20,5],[10,15]] = 0.40（po 0.70・pe 0.50）", cohen_kappa([[20, 5], [10, 15]]), 0.40, 0.0005)
    near("kappa 3x3 [[5,1,0],[1,5,1],[0,1,5]] = 41/60", cohen_kappa([[5, 1, 0], [1, 5, 1], [0, 1, 5]]), 41.0 / 60.0, 1e-12)
    # 周辺度数が非対称な表: po = 0.60・pe = (60*70 + 40*30) / 100^2 = 0.54 → kappa = 0.06 / 0.46 = 3/23。
    # ⚠️ [[20,5],[10,15]] は行の周辺度数が等しく、行 x 列 と 行 x 行 の取り違えを見分けられない。
    near("kappa [[45,15],[25,15]] = 3/23（周辺度数が非対称）", cohen_kappa([[45, 15], [25, 15]]), 3.0 / 23.0, 1e-12)
    near("kappa は評定者の入れ替え（転置）で不変", cohen_kappa([[45, 25], [15, 15]]), cohen_kappa([[45, 15], [25, 15]]), 1e-12)
    near("kappa 完全一致は 1", cohen_kappa([[10, 0], [0, 10]]), 1.0, 1e-12)
    near("kappa 周辺が独立なら 0", cohen_kappa([[10, 10], [10, 10]]), 0.0, 1e-12)
    near("kappa 完全な不一致は -1", cohen_kappa([[0, 10], [10, 0]]), -1.0, 1e-12)
    check("kappa 片方のカテゴリだけ（pe = 1）は None", cohen_kappa([[10, 0], [0, 0]]) is None)
    check("kappa 総数 0 は None", cohen_kappa([[0, 0], [0, 0]]) is None)
    raises("kappa k x k でない", lambda: cohen_kappa([[1, 2, 3], [4, 5, 6]]))
    raises("kappa 負の度数", lambda: cohen_kappa([[1, -1], [1, 1]]))

    # --- Bland-Altman
    ba = bland_altman([2, 3, 4, 5, 6], [1, 1, 1, 1, 1])
    near("BA 偏り = 3.0（差 1..5）", ba["bias"], 3.0, 1e-12)
    near("BA sd = 1.5811（標本標準偏差）", ba["sd"], 1.5811, 0.0005)
    near("BA 一致限界の上 = 3.0 + 1.96 * 1.5811", ba["loa_hi"], 3.0 + 1.96 * 1.5811388300841898, 1e-9)
    near("BA 一致限界の下 = 3.0 - 1.96 * 1.5811", ba["loa_lo"], 3.0 - 1.96 * 1.5811388300841898, 1e-9)
    check("BA の n", ba["n"] == 5)
    rev = bland_altman([1, 1, 1, 1, 1], [2, 3, 4, 5, 6])
    near("BA a と b を入れ替えると偏りの符号が反転", rev["bias"], -3.0, 1e-12)
    near("BA a と b を入れ替えても sd は同じ", rev["sd"], ba["sd"], 1e-12)
    one = bland_altman([4], [1])
    check("BA n = 1 は sd と一致限界が None", one["bias"] == 3 and one["sd"] is None and one["loa_lo"] is None)
    check("BA n = 0 は全部 None", bland_altman([], [])["bias"] is None)
    raises("BA 長さが違う", lambda: bland_altman([1, 2], [1]))

    # --- 中央絶対誤差
    near("MAE 奇数個", median_abs_error([1, 2, 3], [2, 2, 5]), 1.0, 1e-12)
    near("MAE 偶数個は中央 2 つの平均", median_abs_error([0, 1, 2, 3], [0, 0, 0, 0]), 1.5, 1e-12)
    near("MAE 符号を見ない", median_abs_error([5, 5, 5], [1, 9, 1]), 4.0, 1e-12)
    check("MAE 対が 0 個は None", median_abs_error([], []) is None)
    raises("MAE 長さが違う", lambda: median_abs_error([1], [1, 2]))

    # --- クラスタ・ブートストラップ
    cl = [[1.0, 1.2, 0.9], [2.0, 2.1], [0.5, 0.4, 0.6, 0.5], [1.5]]
    a = cluster_bootstrap(cl, _mean_of_clusters, B=500, seed=7)
    b = cluster_bootstrap(cl, _mean_of_clusters, B=500, seed=7)
    check("cluster_bootstrap 同じ seed で完全に同じ区間", a == b, "%r %r" % (a, b))
    # ⚠️ seed を変えると変わることは、値が連続でクラスタ数が十分な標本で見る。4 クラスタだと平均が高々 256 通りの
    # 離散値になり、2.5% / 97.5% 点が両端の同じ値に落ちて seed が違っても区間が一致しうる（実測）。
    rich = [[0.31 * i % 1.7 + 0.11 * j for j in range(1 + i % 3)] for i in range(12)]
    s1 = cluster_bootstrap(rich, _mean_of_clusters, B=500, seed=1)
    s1b = cluster_bootstrap(rich, _mean_of_clusters, B=500, seed=1)
    s2 = cluster_bootstrap(rich, _mean_of_clusters, B=500, seed=2)
    check("cluster_bootstrap 連続値の標本で同じ seed は同じ区間", s1 == s1b, "%r %r" % (s1, s1b))
    check("cluster_bootstrap seed を変えると区間が変わる", s1 != s2, "%r %r" % (s1, s2))
    g0 = random.getstate()
    cluster_bootstrap(cl, _mean_of_clusters, B=200, seed=1)
    check("cluster_bootstrap がグローバルな乱数状態に触らない", random.getstate() == g0)
    check("cluster_bootstrap の区間は lo <= hi", a[0] <= a[1])
    # 閉じた式: 2 クラスタ [1.0] と [3.0] の平均は {1, 2, 3} を確率 1/4・1/2・1/4 で取る。
    # 2.5% 点は 1.0・97.5% 点は 3.0 なのでパーセンタイル区間はちょうど (1.0, 3.0)。
    two = cluster_bootstrap([[1.0], [3.0]], _mean_of_clusters, B=4000, seed=3)
    check("cluster_bootstrap パーセンタイル法の閉じた式 (1.0, 3.0)", two == (1.0, 3.0), repr(two))
    # 分位の定義（線形補間）を固定する: 標本に依らず 0, 1, ..., 1000 を返す stat なら B = 1001 の反復値は
    # ちょうど 0..1000 なので、95% 区間は (25.0, 975.0)・90% 区間は (50.0, 950.0)。
    def counter():
        state = [-1]

        def f(cs):
            state[0] += 1
            return float(state[0])
        return f

    # ⚠️ (1 - conf) / 2 は 0.025000000000000022 のように浮動小数の誤差を持つので、== でなく許容誤差で比べる。
    q95 = cluster_bootstrap(cl, counter(), B=1001, seed=1)
    near("cluster_bootstrap 95% 区間の下側の分位 = 25.0", q95[0], 25.0, 1e-9)
    near("cluster_bootstrap 95% 区間の上側の分位 = 975.0", q95[1], 975.0, 1e-9)
    q90 = cluster_bootstrap(cl, counter(), B=1001, seed=1, conf=0.90)
    near("cluster_bootstrap 90% 区間の下側の分位 = 50.0", q90[0], 50.0, 1e-9)
    near("cluster_bootstrap 90% 区間の上側の分位 = 950.0", q90[1], 950.0, 1e-9)
    # 標準誤差の検算: 値 0..9 の 10 クラスタ（各 1 要素）の平均の SE = sqrt(8.25 / 10) = 0.9083。区間の幅は約 3.56。
    ten = cluster_bootstrap([[float(v)] for v in range(10)], _mean_of_clusters, B=4000, seed=11)
    check("cluster_bootstrap 10 クラスタの平均の区間の幅が標準誤差と合う", 3.2 <= ten[1] - ten[0] <= 3.9, repr(ten))
    check("cluster_bootstrap 区間が標本の平均を挟む", ten[0] < 4.5 < ten[1], repr(ten))
    # クラスタを壊さない: stat に渡る各クラスタは元のクラスタそのもので、個数は元と同じ。実際に重複・脱落が起きる。
    originals = [(1.0, 1.5), (2.0, 2.5, 2.75), (3.0,), (4.0, 4.5), (5.0, 5.25, 5.5, 5.75)]
    seen = {"foreign": 0, "wrong_k": 0, "dup": 0, "missing": 0}

    def spy(cs):
        if len(cs) != len(originals):
            seen["wrong_k"] += 1
        if any(c not in originals for c in cs):
            seen["foreign"] += 1
        if len(set(cs)) < len(cs):
            seen["dup"] += 1
        if len(set(cs)) < len(originals):
            seen["missing"] += 1
        return 0.0

    cluster_bootstrap([list(o) for o in originals], spy, B=300, seed=5)
    check("cluster_bootstrap は元のクラスタだけを元の個数だけ抽出する", seen["foreign"] == 0 and seen["wrong_k"] == 0, repr(seen))
    check("cluster_bootstrap は復元抽出（重複と脱落が実際に起きる）", seen["dup"] > 0 and seen["missing"] > 0, repr(seen))
    # ⚠️ 陽性対照: 各クラスタが定数（クラスタ内相関が 1）なら、要素を単位にした抽出より区間が広い。
    # 10 クラスタ x 20 要素。クラスタ単位の SE ~ sigma / sqrt(10)・要素単位の SE ~ sigma / sqrt(200)（約 4.5 倍）。
    const_clusters = [[float(v)] * 20 for v in range(10)]
    flat_as_clusters = [[x] for c in const_clusters for x in c]
    w_cluster = cluster_bootstrap(const_clusters, _mean_of_clusters, B=2000, seed=21)
    w_element = cluster_bootstrap(flat_as_clusters, _mean_of_clusters, B=2000, seed=21)
    wc, we = w_cluster[1] - w_cluster[0], w_element[1] - w_element[0]
    check("クラスタ内相関で区間が広がる（クラスタ単位 > 要素単位の 2 倍）", wc > 2.0 * we, "cluster %.4f element %.4f" % (wc, we))
    check("クラスタ内相関で区間が広がる: 要素単位は狭く出る（陰性側の確認）", we < 1.0, "element %.4f" % we)
    check("cluster_bootstrap クラスタ 1 個は (None, None)", cluster_bootstrap([[1.0, 2.0]], _mean_of_clusters, 10, 1) == (None, None))
    check("cluster_bootstrap クラスタ 0 個は (None, None)", cluster_bootstrap([], _mean_of_clusters, 10, 1) == (None, None))
    raises("cluster_bootstrap stat が None を返す", lambda: cluster_bootstrap(cl, lambda cs: None, 10, 1))
    raises("cluster_bootstrap stat が nan を返す", lambda: cluster_bootstrap(cl, lambda cs: float("nan"), 10, 1))
    raises("cluster_bootstrap B = 0", lambda: cluster_bootstrap(cl, _mean_of_clusters, 0, 1))
    raises("cluster_bootstrap seed が整数でない", lambda: cluster_bootstrap(cl, _mean_of_clusters, 10, "a"))
    raises("cluster_bootstrap conf = 0", lambda: cluster_bootstrap(cl, _mean_of_clusters, 10, 1, conf=0.0))

    if fails:
        for f in fails:
            print("NG: " + f)
        print("selftest 失敗 %d 件 / %d 件" % (len(fails), count[0]))
        return 1
    print("selftest OK（%d 件）" % count[0])
    return 0


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="E1 / E2 の統計の部品（ライブラリ。単体で動かすのは --selftest だけ）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
