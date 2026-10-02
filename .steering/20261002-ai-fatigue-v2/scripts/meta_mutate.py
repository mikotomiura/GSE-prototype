"""検査器のメタ変異（design.md §12）: RULES_* に 1 行 1 つで登録した規則を 1 行ずつ外した写しを作り、
その写しの `--selftest` が落ちる（終了コード ≠ 0）ことを確かめる。落ちない写しがあれば、その規則を試す変異が足りない。

使い方: uv run --with openpyxl python meta_mutate.py check_ta_sheet.py [--jobs 4]
"""
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def rule_lines(src):
    """RULES_ で始まるリストの中の `    r_xxx,` の行番号。"""
    out, inside = [], False
    for n, line in enumerate(src.splitlines()):
        if re.match(r"^RULES_\w+\s*=\s*\[", line):
            inside = True
            continue
        if inside and line.strip() == "]":
            inside = False
            continue
        if inside and re.fullmatch(r"\s+r_\w+,\s*", line):
            out.append(n)
    return out


def run_one(path, src_lines, n, tmpd):
    name = src_lines[n].strip().rstrip(",")
    mut = src_lines[:n] + src_lines[n + 1:]
    p = os.path.join(tmpd, f"{os.path.splitext(os.path.basename(path))[0]}__no_{name}.py")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(mut) + "\n")
    env = dict(os.environ, PYTHONPATH=HERE + os.pathsep + os.environ.get("PYTHONPATH", ""), PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, p, "--selftest"], cwd=HERE, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    return name, r.returncode, fails[:3]


def main():
    path = os.path.join(HERE, sys.argv[1])
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 4
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines()
    idx = rule_lines(src)
    print(f"{os.path.basename(path)}: 規則 {len(idx)} 個", flush=True)
    tmpd = tempfile.mkdtemp(prefix="meta-")
    bad = []
    with ThreadPoolExecutor(jobs) as ex:
        for name, rc, fails in ex.map(lambda n: run_one(path, lines, n, tmpd), idx):
            good = rc != 0
            print(("PASS" if good else "FAIL"), f"{name} を外すと selftest が", "落ちる" if good else "通る（変異が足りない）",
                  fails if good else "", flush=True)
            if not good:
                bad.append(name)
    print("meta", "PASS" if not bad else f"FAIL {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
