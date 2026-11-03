"""N6 の変異: pausestall.py の要の行を壊した写しで --selftest が赤になるかを確かめる。1 つでも緑なら止める。

usage: mutants.py
写しは一時フォルダに置き、candidates.py などは元の場所から読む（sys.path は写しの HERE ではなく元を指すよう置き換える）。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "pausestall.py")).read()
SRC_B = open(os.path.join(HERE, "build_n4.py")).read()
BAD = ("ImportError", "ModuleNotFoundError", "SyntaxError", "IndentationError", "NameError")

MUTANTS = {
    "BIC の罰を消す": ("pen = (3 * k - 1) * math.log(n)", "pen = 0.0"),
    "階級の度数を無視する": ("r = dens / tot[:, None] * c[:, None]", "r = dens / tot[:, None]"),
    "0 ms を外さない": ("xs = sorted(g for g in gaps if g > 0)", "xs = sorted(g for g in gaps if g >= 0)"),
    "フォーカス 0 を C1 側に入れる": ("            if d[\"focus\"]:\n", "            if True:\n"),
    "4 時間の下限を消す": ("u = [x for x in units if x[0] >= MIN_UNIT_MS]", "u = [x for x in units if x[0] >= 0]"),
    "単位の数の下限を消す": ("if len(u) < MIN_UNITS:", "if len(u) < 2:"),
    "P-ID の走査を外す": ("    if any(pid in text for pid in pids):\n", "    if False:\n"),
    "流れ A にフォーカス 0 の本を入れる": ("ga = [g for dy in p.focus for _, g in cd.gap_pool(dy.act, dy.intervals)]",
                                     "ga = [g for dy in p.all for _, g in cd.gap_pool(dy.act, dy.intervals)]"),
    "between のキー名を誤る": ('r["N4_focus_files"]["O1_counts_rates"][k]["pooled_per_h"], True)',
                            'r["N4_focus_files"]["O1_counts_rate"][k]["pooled_per_h"], True)'),
    "日付の単位を足さない": ("        a[1] += n\n", "        a[1] = n\n"),
    "取り置きを全員にかける": ('if pid == SELF_PID and f"{m.group(2)}_{m.group(3)}" >= HOLD_FROM:',
                            'if f"{m.group(2)}_{m.group(3)}" >= HOLD_FROM:'),
    "公開用の丸めを外す": ("    text = json.dumps(public(res), indent=1, ensure_ascii=False)",
                         "    text = json.dumps(res, indent=1, ensure_ascii=False)"),
    "日付の形の走査を外す": (r'if re.search(r"\d{8}_\d{6}", text) or re.search(', 'if False and re.search('),
    "丸めを件数のキーに限らない": ("    if isinstance(x, int) and key in COUNT_KEYS:\n", "    if isinstance(x, int):\n"),
    "小さい分母の割合を伏せない": ('and x["den"] < MIN_DEN:', 'and x["den"] < 0:'),
    "観測 0 を外さない": ("            if dy.obs <= 0:\n", "            if dy.obs < 0:\n"),
}


def run_copy(tmp, src, src_b):
    """写し（pausestall_mut.py と build_n4.py）で --selftest を回す。HERE だけ元のフォルダを指す。"""
    d = tempfile.mkdtemp(dir=tmp)
    fix = lambda t: t.replace("HERE = os.path.dirname(os.path.abspath(__file__))", f"HERE = {d!r}")
    # pausestall の写しは candidates を元の場所から読む（sys.path の行は HERE からの相対なので、元の場所を足す）
    src = fix(src).replace('sys.path.insert(0, os.path.join(HERE, "../20261103-stall-candidates-c1c2c6"))',
                           f'sys.path.insert(0, {os.path.join(HERE, "../20261103-stall-candidates-c1c2c6")!r})')
    src_b = src_b.replace("HERE = os.path.dirname(os.path.abspath(__file__))", f"HERE = {HERE!r}")
    open(os.path.join(d, "pausestall.py"), "w").write(src)
    open(os.path.join(d, "build_n4.py"), "w").write(src_b)
    return subprocess.run([sys.executable, "-I", "-B", os.path.join(d, "pausestall.py"), "--selftest"],
                          capture_output=True, text=True, timeout=900)


def main():
    tmp = tempfile.mkdtemp()
    green, bad = [], []
    try:
        r = run_copy(tmp, SRC, SRC_B)
        if r.returncode != 0:
            sys.exit("変異していない写しが通らない（写しの作り方が壊れている）:\n" + r.stderr[-2000:])
        for name, (a, b) in MUTANTS.items():
            in_b = SRC_B.count(a) == 1 and SRC.count(a) == 0
            if not in_b and SRC.count(a) != 1:
                sys.exit(f"変異の行が 1 か所に当たらない: {name}")
            r = run_copy(tmp, SRC if in_b else SRC.replace(a, b), SRC_B.replace(a, b) if in_b else SRC_B)
            red = r.returncode != 0
            if red and any(x in r.stderr for x in BAD):
                bad.append(name)
            print(("赤" if red else "緑"), name, file=sys.stderr)
            if not red:
                green.append(name)
    finally:
        shutil.rmtree(tmp)
    if green or bad:
        sys.exit("変異が素通りした: " + "・".join(green) + " / 読み込みの失敗で赤: " + "・".join(bad))
    print("mutants ok", file=sys.stderr)


if __name__ == "__main__":
    main()
