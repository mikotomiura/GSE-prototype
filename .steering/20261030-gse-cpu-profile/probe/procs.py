#!/usr/bin/env python3
# 開発版の本体と、それに結びつく WebKit の子（GPU・WebContent・Networking）のプロセス番号を出す。
# 子は ppid が 1 なので、責任者のプロセス番号（responsibility_get_pid_responsible_for_pid）で結びつける。
# `npx tauri dev` の起動では、子の責任者は本体ではなく起動元になるので、{本体, 本体の責任者} の両方で拾う。
# 使い方: procs.py <本体の実行ファイルのパスに含まれる文字列> [除くプロセス番号のファイル] [期待する子の数]
# 出力: 1 行目に本体、続けて子を「pid 名前」で。最後に件数。本体が無ければ rc=3、子の数が期待と違えば rc=4。
# ⚠️ 起動元が責任者の子も拾うので、同じ起動元から動く別の WebKit を混ぜうる。起動前の一覧を除くファイルで渡し、件数で確かめる。
import ctypes, subprocess, sys
lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
f = lib.responsibility_get_pid_responsible_for_pid
f.argtypes = [ctypes.c_int]; f.restype = ctypes.c_int
needle = sys.argv[1]
exclude = set()
if len(sys.argv) > 2:
    exclude = {int(x) for x in open(sys.argv[2]).read().split() if x.isdigit()}
rows = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True, text=True, check=True).stdout.splitlines()
procs = []
for r in rows:
    pid, _, comm = r.strip().partition(" ")
    procs.append((int(pid), comm.strip()))
main = [p for p, c in procs if needle in c and c.endswith("/gse-next")]
if len(main) != 1:
    print(f"本体が 1 つに決まらない: {main}", file=sys.stderr); sys.exit(3)
m = main[0]
r = f(m)
owners = {m} | ({r} if r > 1 else set())
kids = [(p, c) for p, c in procs if "com.apple.WebKit." in c and p not in exclude and f(p) in owners]
print(m, "gse-next")
for p, c in kids:
    print(p, c.rsplit("/", 1)[-1])
print(f"# main=1 webkit={len(kids)} owners={sorted(owners)}", file=sys.stderr)
if len(sys.argv) > 3 and len(kids) != int(sys.argv[3]):
    print(f"子の数が期待と違う: {len(kids)} != {sys.argv[3]}", file=sys.stderr); sys.exit(4)
