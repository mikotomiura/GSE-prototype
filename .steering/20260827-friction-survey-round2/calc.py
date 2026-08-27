#!/usr/bin/env python3
"""摩擦操作サーヴェイ 第 2 ラウンドの自前計算の検算スクリプト。

★ カード / notes.md §15 / _index.md に載せた「文献の引用ではない数値」を、すべてここで再現する。
⚠️ 依存は標準ライブラリのみ（scipy 不要）。repo 直下から `python3 .steering/20260827-friction-survey-round2/calc.py` で走る。

出典:
  docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md
  experiments/20260801-controlled-friction-task/notes.md §15
"""
import json
import math
import os
from math import comb
from statistics import NormalDist, median

ND = NormalDist()
Phi, Phinv = ND.cdf, ND.inv_cdf
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXP = os.path.join(REPO, "experiments", "20260801-controlled-friction-task")

# ★ 実測の異条件ペアの分母（notes.md §13-1）。P007=6 / P014=4 / P016=5
DENOMS = [("P007", 6), ("P014", 4), ("P016", 5)]
GATE = 0.70  # preregistration.md §2.6


def h(t):
    print(f"\n=== {t} ===")


def two_sided_binom_p(k, n, p=0.5):
    probs = [comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(n + 1)]
    return sum(pr for pr in probs if pr <= probs[k] + 1e-12)


def dz(t, n):
    return t / math.sqrt(n)


def ci_dz(d, n):
    se = math.sqrt(1 / n + d * d / (2 * n))
    return d - 1.96 * se, d + 1.96 * se


def need_n(d, power=0.80):
    z = Phinv(0.975) + Phinv(power)
    return math.ceil((z / d) ** 2)


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


# ---------------------------------------------------------------- カード 1
h("カード 1: [P135] Rong & Révész (2025) の効果量（N=56・被験者内）")
for name, t in [("Reading mental effort", 1.30), ("Writing mental effort", 3.02),
                ("Task difficulty", 1.69)]:
    d = dz(t, 56)
    lo, hi = ci_dz(d, 56)
    print(f"  {name:24s} d_z={d:.3f}  95%CI[{lo:+.3f},{hi:+.3f}]  power.80 に要る N={need_n(d)}")
print(f"  ★ task difficulty: 報告 両側 p=.097 → 片側 p={0.097/2:.4f}（★ 著者は方向を事前に述べている）")

h("カード 1: Gelman–Stern — 2 係数の差が有意になるのに要る DV 間相関")
b1, b2, se = 0.43, 0.24, 0.14
diff = b1 - b2
for r in (0.0, 0.5, 0.7, 0.76, 0.8):
    se_d = math.sqrt(2 * se * se * (1 - r))
    print(f"  r={r:.2f} → SE_diff={se_d:.4f}  t={diff/se_d:.2f}"
          + ("  ← 有意" if abs(diff / se_d) >= 1.96 else ""))

# ---------------------------------------------------------------- カード 2
h("カード 2: 一次アンカーを強制比較に写す（仮定: 比較のノイズ SD ＝ 評定の SD → P=Φ(d)）")
ANCHORS = [("[P135] writing mental effort (p=.004)", 0.404),
           ("[P135] task difficulty (両側 p=.097)", 0.226),
           ("(参考) [P133] perceived difficulty (N=310)", 0.42)]
for name, d in ANCHORS:
    print(f"  {name:42s} d={d:.3f} → P(HI 選択)={Phi(d):.3f}")
print(f"  ★ ゲート ≥{GATE:.0%} に必要な d = Φ⁻¹({GATE}) = {Phinv(GATE):.3f} → どのアンカーも届かない")

h("カード 2: コホート全員合格ゲート（analyze.py:786 の all(...)）の通過確率")
for name, d in ANCHORS[:2]:
    p = Phi(d)
    prod, parts = 1.0, []
    for who, n in DENOMS:
        k = math.ceil(GATE * n)
        pr = sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))
        parts.append(f"{who}(分母{n}) {pr:.3f}")
        prod *= pr
    print(f"  d={d:.3f}: " + " / ".join(parts) + f"  → 全員合格 {prod:.3f}")

h("カード 2: 実効閾値 ceil(0.7n)/n（★ G1 の保証域 4〜6 では *単調増加*・非単調は n≥7）")
prev = None
for n in range(4, 11):
    k = math.ceil(GATE * n)
    v = k / n
    mark = "  ← 下がった（非単調）" if prev is not None and v < prev else ""
    inr = " ★保証域" if 4 <= n <= 6 else ""
    print(f"  n={n:2d}: {k}/{n} = {v:.3f}{mark}{inr}")
    prev = v

# ---------------------------------------------------------------- カード 3
h("カード 3: 条件別の打鍵スパン（★ metrics.json から読む・§3.5-1 の報告義務・封印対象外）")
mp = os.path.join(EXP, "results", "metrics.json")
if os.path.exists(mp):
    m = json.load(open(mp))
    assert m.get("verdict_sealed") is True, "⚠️ 封印が解かれている"
    print(f"  verdict_sealed = {m['verdict_sealed']}（★ 封印は保たれている）")
    for s in m["per_subject"]:
        by = {}
        for b in s["block_summary"]:
            by.setdefault(b["condition"], []).append(b["span_ms"] / 1000)
        hi, lo = sorted(by["HI"]), sorted(by["LO"])
        sep = max(hi) < min(lo)
        print(f"  {s['subject']}: 中央値 HI={median(hi):6.1f}s < LO={median(lo):6.1f}s "
              f"= {median(hi) < median(lo)} / **全ブロック分離={'YES' if sep else 'NO'}** "
              f"(HI最大={max(hi):.1f} vs LO最小={min(lo):.1f})")
    print("  ★ 中央値では 3/3 で HI<LO だが、全ブロック分離は P016 のみ（2026-08-28 訂正）")
else:
    print("  (metrics.json 無し — skip)")

# ---------------------------------------------------------------- カード 4
h("カード 4: [P133] のユニット水準の共線性（Tab.2 の 5 ユニット）")
UNITS = [("Catalano", 0, 1273), ("Nothing", 0, 1320), ("2134", 1, 1458),
         ("Universe", 1, 1439), ("Animals", 1, 2172)]
d_, L_ = [u[1] for u in UNITS], [u[2] for u in UNITS]
r_all = pearson(d_, L_)
print(f"  全 5 ユニット: r(文書数, 総語数) = {r_all:.3f}  VIF = {1/(1-r_all**2):.1f}")
for i, u in enumerate(UNITS):
    dd = [x for j, x in enumerate(d_) if j != i]
    LL = [x for j, x in enumerate(L_) if j != i]
    r = pearson(dd, LL)
    print(f"    {u[0]:10s} を除くと r = {r:+.3f}  VIF = {1/(1-r*r):6.1f}"
          + ("   ← ★ 分離はこの 1 ユニットに依存" if r > 0.9 else ""))
print("  ★ ユニット水準の残差自由度 = 5 - 3(unit variables) - 1 = 1")
print("  ★ [P133] Tab.6 の係数 95%CI（DV が z 標準化なので B はそのまま d）:")
for name, b, se in [("PD ~ number of documents", 0.42, 0.10), ("ME ~ number of documents", 0.08, 0.07)]:
    print(f"    {name:26s} B={b:+.2f}  95%CI[{b-1.96*se:+.3f},{b+1.96*se:+.3f}]")

# ---------------------------------------------------------------- カード 7
h("カード 7: per-subject の符号検定（完全連続時）— ★ 分母を増やすと *弱くなる*")
for n in range(4, 9):
    rej = [k for k in range(n + 1) if two_sided_binom_p(k, n) <= 0.05]
    pw = sum(comb(n, k) * 0.2**k * 0.8 ** (n - k) for k in rej)  # 真に 80% 逆向き
    print(f"  n={n}: 両側α=.05 の棄却域 k={rej if rej else '空'}  逆向きの検出力={pw:.3f}")

h("カード 7: 記述的対称三分割の到達可能性と、帰無での決定率")
for who, n in DENOMS:
    up, lo = math.ceil(GATE * n), math.floor(0.30 * n)
    pr = sum(comb(n, k) * 0.5**n for k in range(n + 1) if k >= up or k <= lo)
    print(f"  {who}(分母{n}): 合格 {up}/{n}={up/n:.3f} / 逆向き {lo}/{n}={lo/n:.3f} "
          f"→ 両側とも到達可能 / 帰無で決定的バケツ {pr:.3f}")

h("カード 7 / 9: コホート水準でペアをプールした実測")
print(f"  HI 選択 6/15 = {6/15:.3f}  両側 p = {two_sided_binom_p(6,15):.4f}")
print("  ★ 「原理的に有意にならない」はコホート水準では偽")

print("\n★ すべての数値はカード / notes.md §15 / _index.md の記載と一致するはず。")
