"""R8 変異: 主な規則を壊した写しで陽性対照が赤になることを確かめる。

変異していない写しが通ることを先に求める。置き換えの文字列が見つからなければ止める（変異が当たっていない）。
読み込みの失敗（ImportError・SyntaxError）による赤は数えない。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ("auc.py", "conduct.py", "prewin.py", "cr_common.py", "build_cr.py", "ledger_gate.py")

MUTANTS = [
    ("auc.py", "対の同値を 1 にする", "1.0 if a > b else 0.5 if a == b else 0.0", "1.0 if a >= b else 0.0"),
    ("auc.py", "折りを日でなく行で分ける", "    fs = [fold[u] for u in s_unit]\n    fc = [fold[u] for u in c_unit]",
     "    fs = [i % FOLDS for i in range(len(s_unit))]\n    fc = [i % FOLDS for i in range(len(c_unit))]"),
    ("auc.py", "写しに引いた位置の単位を付ける", "            sunit.append(u)\n", "            sunit.append((u, len(srcs)))\n"),
    ("auc.py", "欠けの中央値を学習と評価の全体で決める",
     "med = np.array([np.nanmedian(Xtr[:, j]) if (~np.isnan(Xtr[:, j])).any() else 0.0 for j in range(Xtr.shape[1])])",
     "med = np.nanmedian(np.vstack([Xtr, Xte]), axis=0)"),
    ("auc.py", "標準化を学習と評価の全体で決める", "mu, sd = A.mean(axis=0), A.std(axis=0)",
     "mu, sd = np.vstack([A, Bm]).mean(axis=0), np.vstack([A, Bm]).std(axis=0)"),
    ("auc.py", "同じ u の停滞を 2 行にする", "        if u in seen_u:", "        if False:"),
    ("auc.py", "W1 と W0 を取り違える", "w1 = k9(f, u - D_WIN, u)\n    w0 = k9(f, u - 2 * D_WIN, u - D_WIN)",
     "w0 = k9(f, u - D_WIN, u)\n    w1 = k9(f, u - 2 * D_WIN, u - D_WIN)"),
    ("auc.py", "対照の G の上限を外す", "ctrl_lo <= g < CTRL_HI", "ctrl_lo <= g"),
    ("auc.py", "区切りの種類を揃えない", "pool = [c for c in ca if c[1] == b]", "pool = list(ca)"),
    ("auc.py", "停滞の窓に入る対照を外さない", "if any(s - D_WIN <= u <= t0 for s, t0 in f.onsets):", "if False:"),
    ("auc.py", "u ≥ s の停滞を外さない", "if u >= s:", "if False:"),
    ("auc.py", "副の窓を外す", "out += n_counts(f, u, u + EARLY)", "out += [0.0] * len(n_counts(f, u, u + EARLY))"),
    ("auc.py", "W1 の左端を閉じる", "return bisect.bisect_right(ts, b) - bisect.bisect_right(ts, a)",
     "return bisect.bisect_right(ts, b) - bisect.bisect_left(ts, a)"),
    ("auc.py", "50 ms の下限を外す", "g50 = [g for g in gaps if g > 50]", "g50 = list(gaps)"),
    ("auc.py", "欠けを 0 で埋める", "pcts = [nearest_rank(g50, q) for q in (0.1, 0.5, 0.9)] if g50 else [nan] * 3",
     "pcts = [nearest_rank(g50, q) for q in (0.1, 0.5, 0.9)] if g50 else [0.0] * 3"),
    ("auc.py", "打鍵以外の量を K+N に入れない", "XKN_s, XKN_c = np.hstack([XK_s, XN_s]), np.hstack([XK_c, XN_c])",
     "XKN_s, XKN_c = XK_s, XK_c"),
    ("conduct.py", "ポインタの閾値を 30 にする", "POINTER_PER_H = 60", "POINTER_PER_H = 30"),
    ("conduct.py", "欠番を数えない", "sum(1 for k in range(1, mx + 1) if k not in seen)", "0"),
    ("conduct.py", "重複を数えない", "sum(1 for v in seen.values() if v >= 2)", "0"),
    ("prewin.py", "無作為の窓を固定長にする", "length = (t0 - s + tc.PRE_WIN) if kind == \"same_length\" else tc.PRE_WIN",
     "length = tc.PRE_WIN"),
    ("prewin.py", "無作為の窓を置かない", "out[kind][\"random\"][tc.Rec.klass(dy.rec.flags(u - length, u))] += 1",
     "out[kind][\"random\"][\"silence\"] += 1"),
    ("build_cr.py", "取り置きを戻す", 'build_n4.HOLD_FROM = "99999999_999999"', "pass"),
    ("build_cr.py", "digest からパスを外す", 'f"{s}  {p}\\n" for s, p in rows', 'f"{s}\\n" for s, p in rows'),
    ("cr_common.py", "丸めを偶数側に戻す", "math.floor(v / step + 0.5) * step", "round(v / step) * step"),
    ("cr_common.py", "割合を粗くしない", "        return round(x, 2)\n", "        return x\n"),
    ("cr_common.py", "率を粗くしない", "        return sig2(x)\n", "        return x\n"),
    ("cr_common.py", "版の種類の数を出す", 'DROP_KEYS = {"app_version_kinds", "random_windows"}', 'DROP_KEYS = {"random_windows"}'),
    ("ledger_gate.py", "見本の行が 1 行だけかを見ない", "return len(data) == 1 and PLACEHOLDER in data[0]",
     "return any(PLACEHOLDER in r for r in data)"),
    ("ledger_gate.py", "行頭の空白を許さない", "lines = [ln.strip() for ln in sec.splitlines()]",
     "lines = sec.splitlines()"),
    ("cr_common.py", "親の規則を引き継がない", "ck = k if rule(k) else (key if rule(key) else k)", "ck = k"),
    ("cr_common.py", "share を粗くしない", ' or "share" in key', ""),
    ("cr_common.py", "AUC を粗くしない", 'THREE_KEYS = {"auc_K", "auc_KN", "delta_auc", "diff"}', "THREE_KEYS = set()"),
    ("cr_common.py", "伏せた割合の差を残す", '            out["diff"] = None\n            out["diff_ci95"] = None\n',
     "            pass\n"),
    ("cr_common.py", "無作為の窓の数を出す", 'DROP_KEYS = {"app_version_kinds", "random_windows"}', 'DROP_KEYS = {"app_version_kinds"}'),
    ("prewin.py", "区間の単位を本に戻す", 'by_date.setdefault(f["date"], [])', 'by_date.setdefault(f["inter"], [])', "e2e"),
    ("auc.py", "分割の単位を本に戻す", 'F(f["inter"], d, x, pok, f["date"])', 'F(f["inter"], d, x, pok, f["inter"])', "e2e"),
    ("auc.py", "日の下限を外す", "N_MATCHED, MIN_STALLS, MIN_DAYS, FOLDS, NBOOT = 5, 30, 5, 5, 200",
     "N_MATCHED, MIN_STALLS, MIN_DAYS, FOLDS, NBOOT = 5, 30, 1, 5, 200", "e2e"),
    ("cr_common.py", "規則の無い小数を粗くしない", "    return sig3(x)  #", "    return x  #"),
    ("build_cr.py", "写しの停滞の始まりを照らさない", "        if got != [list(o) for o in onsets]:", "        if False:"),
    ("cr_common.py", "公開版の件数の丸めを外す", "ps.COUNT_KEYS |= EXTRA_COUNT_KEYS", "ps.COUNT_KEYS = set()"),
]

REPLAY = os.environ.get("GSE_REPLAY", os.path.expanduser("~/gse-public-data/klicke/bin/gse-replay"))
TESTS = {"e2e": ["e2e_test.py", REPLAY], "auc.py": ["auc.py", "--selftest"], "conduct.py": ["conduct.py", "--selftest"],
         "prewin.py": ["prewin.py", "--selftest"], "cr_common.py": ["cr_common_test.py"], "build_cr.py": ["build_cr_test.py"], "ledger_gate.py": ["ledger_gate.py", "--selftest"]}


def run(dirp, target):
    r = subprocess.run([sys.executable, "-I", "-B", *TESTS[target]], cwd=dirp, capture_output=True, text=True, timeout=600)
    loadfail = any(x in r.stderr for x in ("ImportError", "ModuleNotFoundError", "SyntaxError", "IndentationError"))
    return r.returncode, loadfail


def copy_tree(dst):
    for f in os.listdir(HERE):
        if f.endswith(".py"):
            shutil.copy(os.path.join(HERE, f), dst)


def main():
    with tempfile.TemporaryDirectory() as td:
        # 写しの中の相対の import（n4 ほか）が同じに解けるよう、experiments の下に置く
        base = os.path.join(td, "experiments")
        os.makedirs(base)
        for d in ("20261103-o1-n4-pause-stall", "20261102-stall-decomposition", "20261101-klicke-early-stall-trigger",
                  "20261103-stall-candidates-c1c2c6"):
            os.symlink(os.path.join(HERE, "..", d), os.path.join(base, d))
        os.symlink(os.path.join(HERE, "../../src-tauri"), os.path.join(td, "src-tauri"))  # e2e が fixture を読む
        work = os.path.join(base, "copy")
        os.makedirs(work)
        copy_tree(work)
        for t in sorted({(m[4] if len(m) > 4 else m[0]) for m in MUTANTS}):
            rc, lf = run(work, t)
            if rc != 0:
                sys.exit(f"変異していない写しが通らない: {t}")
        bad = []
        for m in MUTANTS:
            target, name, old, new = m[:4]
            test = m[4] if len(m) > 4 else target
            copy_tree(work)
            p = os.path.join(work, target)
            s = open(p).read()
            if old not in s:
                sys.exit(f"変異が当たらない: {name}")
            open(p, "w").write(s.replace(old, new, 1))
            rc, lf = run(work, test)
            if lf:
                sys.exit(f"変異の写しが読み込めない: {name}")
            if rc == 0:
                bad.append(name)
        copy_tree(work)
        if bad:
            sys.exit("緑のままの変異: " + "・".join(bad))
        print(f"mutants ok: {len(MUTANTS)} 種すべて赤")


if __name__ == "__main__":
    main()
