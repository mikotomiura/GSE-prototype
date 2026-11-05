"""変異の確かめ（conditions.md U5）。confirm.py の判定の要の行を 1 つずつ壊し、--selftest が赤になることを確かめる。
ファイルは書き換えない（読み込んだ文字列を置き換えて、同じ場所の名前で実行する）。
  python3 -I mutants.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "confirm.py")

MUTANTS = [
    ("p の閾値", "st[\"p_one_sided\"] < ALPHA", "st[\"p_one_sided\"] < 0.5"),
    ("SD の比の条件を外す", " and st[\"sd_ratio\"] >= SD_RATIO_MIN", ""),
    ("φ の上限の分位", "x2 / chi2_ppf(0.025, k)", "x2 / chi2_ppf(0.975, k)"),
    ("反証の線", "st[\"phi_upper95\"] < PHI_UPPER_MAX", "st[\"phi_upper95\"] < 0"),
    ("日数の下限", "MIN_DAYS = 5 ", "MIN_DAYS = 4 "),
    ("4 時間の境界", "if obs < MIN_DAY_OBS:", "if obs <= MIN_DAY_OBS:"),
    ("温まりを除かない（H4a）", "(max(a, wend), b) for a, b in sorted(intervals)", "(a, b) for a, b in sorted(intervals)"),
    ("H4a の観測時間に温まりを戻す", "units.append((sum(b - a for a, b in pw),", "units.append((dy.obs,"),
    ("RR の向き", "    return L / E", "    return E / L"),
    ("0 の補正", "if E == 0 or L == 0:", "if E == 0 and L == 0:"),
    ("頭の 10 分", "max(a + tc.EARLY_MS, wend)", "max(a, wend)"),
    ("θ の温まり", "pool[cc.WARM - 1][0]", "pool[cc.WARM][0]"),
    ("前半と後半の切れ目", "m = _cut(rem, 0.5)", "m = _cut(rem, 0.4)"),
    ("切れ目ちょうど", "                if t < m:", "                if t <= m:"),
    ("まとまりの終わり", "last = press[bisect.bisect_left(press, nxt) - 1]", "last = min(nxt, intervals[-1][1])"),
    ("60 分のまとまり", "MIN_BOUT_OBS = 60 * 60_000", "MIN_BOUT_OBS = 0"),
    ("まとまりの下限", "MIN_BOUTS = 10 ", "MIN_BOUTS = 5 "),
    ("件数の下限", "E + L < MIN_HALF_COUNT", "E + L < 0"),
    ("H5 の支持", "\"support\" if lo > 1", "\"support\" if hi > 1"),
    ("H5 の反証", "\"refute\" if hi < RR_REFUTE", "\"refute\" if lo < RR_REFUTE"),
    ("区間の幅（狭く）", "math.exp(math.log(obs) - 1.96 * se)", "math.exp(math.log(obs) - 1.0 * se)"),
    ("区間の幅（広く）", "math.exp(math.log(obs) + 1.96 * se)", "math.exp(math.log(obs) + 3.0 * se)"),
    ("ブートストラップの抽出", "bouts[rng.randrange(len(bouts))]", "bouts[0]"),
    ("並べ替えの不等号", "f >= f_obs", "f > f_obs"),
    ("並べ替えの +1", "(1 + ge) / (B + 1)", "ge / B"),
    ("群の中が 0 の F", "return math.inf if ssb > 0 else None", "return None"),
    ("ブロック 2 未満の日", "    groups = [g for g in groups if len(g) >= 2]\n    f_obs", "    f_obs"),
    ("1 時間のブロック", "step = min(H - acc, b - t)", "step = min(H // 2 - acc, b - t)"),
    ("切れ目のまたぎ", "step = min(H - acc, b - t)", "step = H - acc"),
    ("ブロックの半開", "bisect.bisect_left(origins, y) - bisect.bisect_left(origins, x)", "bisect.bisect_right(origins, y) - bisect.bisect_left(origins, x)"),
    ("U4 の幅", "0.35 <= x <= 0.65", "0.35 <= x <= 0.66"),
    ("温まりの後の 4 時間（H5）", "if sum(b - a for a, b in post_warm(dy.intervals, we)) < MIN_DAY_OBS:", "if sum(b - a for a, b in post_warm(dy.intervals, we)) < 0:"),
    ("温まりの後の 4 時間（H4a）", "            if sum(b - a for a, b in pw) < MIN_DAY_OBS:", "            if sum(b - a for a, b in pw) < 0:"),
    ("まとまりの数の境界", "len(bouts) < MIN_BOUTS", "len(bouts) <= MIN_BOUTS"),
    ("件数の境界", "E + L < MIN_HALF_COUNT", "E + L <= MIN_HALF_COUNT"),
    ("自己検査を外す", "if port != dy.replay_onsets:", "if False:"),
    ("SHA-256 の照合を外す", "if d[\"input_sha256\"] != cc.sha256(f):", "if False:"),
    ("SD の比を丸める", "ratio = sd_b / sd_p if sd_p else None", "ratio = round(sd_b, 4) / round(sd_p, 4) if sd_p else None"),
    ("f の欠けを繰り返さなかったにする", "\"repeated\": None if missing else rule(x)", "\"repeated\": False if missing else rule(x)"),
    ("U4 の割合のキー", "\"C0_is_C2\", \"ratio\")", "\"C0_is_C2\", \"num\")"),
]


RUNNER = (
    "import sys, types\n"
    "src = sys.stdin.read()\n"
    "m = types.ModuleType('confirm_mut'); m.__file__ = sys.argv[1]\n"
    "exec(compile(src, sys.argv[1], 'exec'), m.__dict__)\n"
    "m.selftest()\n"
)
TIMEOUT_S = 60  # 無限ループになる変異は時間切れを赤と数える


def run_selftest(src):
    try:
        r = subprocess.run([sys.executable, "-I", "-c", RUNNER, SRC], input=src, text=True,
                           capture_output=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    if r.returncode != 0:
        last = (r.stderr.strip().splitlines() or [""])[-1]
        return False, last.split(":")[0][:40]
    return True, None


def main():
    src = open(SRC).read()
    ok, _ = run_selftest(src)
    if not ok:
        sys.exit("元のコードで selftest が赤")
    bad = []
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            sys.exit(f"変異の対象が 1 か所でない: {name}（{src.count(old)}）")
        green, why = run_selftest(src.replace(old, new))
        print(f"{'緑のまま' if green else '赤'}\t{name}\t{why or ''}", file=sys.stderr)
        if green:
            bad.append(name)
    if bad:
        sys.exit("変異で赤にならなかった: " + "・".join(bad))
    print(f"変異 {len(MUTANTS)} 種すべて赤", file=sys.stderr)


if __name__ == "__main__":
    main()
