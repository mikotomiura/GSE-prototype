#!/usr/bin/env python3
# プロセスのスレッドごとの累積 CPU 時間（user + system）を、<秒> の前後で読んで、1 コアに対する割合を出す。
# proc_pidinfo の PROC_PIDLISTTHREADIDS（28）と PROC_PIDTHREADID64INFO（15）を使う。root は要らない（同じ利用者のプロセス）。
# スレッドの id は sample の「Thread_<id>」と同じ数なので、名前の無いスレッドは sample の山と突き合わせる。
# 使い方: threads.py <秒> <pid> [表示する上位の数]。プロセスが無ければ rc=3、秒の不正で rc=2。
import ctypes, sys, time
if len(sys.argv) < 3 or not sys.argv[1].isdigit() or int(sys.argv[1]) <= 0 \
        or not sys.argv[2].isdigit() or (len(sys.argv) > 3 and not sys.argv[3].isdigit()):
    print("使い方: threads.py <正の整数の秒> <pid> [上位の数]", file=sys.stderr); sys.exit(2)
secs, pid = int(sys.argv[1]), int(sys.argv[2])
top = int(sys.argv[3]) if len(sys.argv) > 3 else 15
lib = ctypes.CDLL("/usr/lib/libproc.dylib")
lib.proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
class TI(ctypes.Structure):
    _fields_ = [("user", ctypes.c_uint64), ("sys", ctypes.c_uint64), ("cpu_usage", ctypes.c_int32),
                ("policy", ctypes.c_int32), ("run_state", ctypes.c_int32), ("flags", ctypes.c_int32),
                ("sleep_time", ctypes.c_int32), ("curpri", ctypes.c_int32), ("priority", ctypes.c_int32),
                ("maxpriority", ctypes.c_int32), ("name", ctypes.c_char * 64)]
def snap():
    buf = (ctypes.c_uint64 * 4096)()
    n = lib.proc_pidinfo(pid, 28, 0, buf, ctypes.sizeof(buf))
    if n <= 0:
        print(f"pid={pid} を読めない（無い・権限）", file=sys.stderr); sys.exit(3)
    out = {}
    for tid in buf[: n // 8]:
        ti = TI()
        if lib.proc_pidinfo(pid, 15, tid, ctypes.byref(ti), ctypes.sizeof(ti)) == ctypes.sizeof(ti):
            out[tid] = (ti.user + ti.sys, ti.name.decode(errors="replace"))
    # 読めたスレッドが一覧の半分に満たなければ止める（構造体の大きさが OS で変わったときに 0% を黙って出さない）
    if not out or len(out) * 2 < n // 8:
        print(f"pid={pid} のスレッドを読めない（一覧 {n // 8}・読めた {len(out)}）", file=sys.stderr); sys.exit(4)
    return out
# pth_user_time / pth_system_time はナノ秒（Apple Silicon でも mach の時間の単位ではない。1 コアを回すスレッドで 100% になることを確かめた）
a = snap(); t0 = time.monotonic(); time.sleep(secs); b = snap(); dt = time.monotonic() - t0
rows = []
for tid, (t, name) in b.items():
    d = t - a.get(tid, (0, ""))[0] if tid in a else t
    rows.append((d / 1e9 / dt * 100, tid, name, tid not in a))
rows.sort(reverse=True)
total = sum(r[0] for r in rows)
gone = len(set(a) - set(b))
print(f"# pid={pid} secs={dt:.1f} threads={len(b)} new={sum(r[3] for r in rows)} gone={gone} total_pct={total:.2f}")
for pct, tid, name, new in rows[:top]:
    print(f"{pct:7.2f}  Thread_{tid}  {name or '-'}{'  (new)' if new else ''}")
