# gse-next とそれが責任を持つ WebKit の子の CPU 累積秒の合計を出す。
import ctypes, subprocess, sys
lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
f = lib.responsibility_get_pid_responsible_for_pid
f.restype = ctypes.c_int; f.argtypes = [ctypes.c_int]
root = int(sys.argv[1])
def secs(t):
    p = t.split(":"); s = 0.0
    for x in p: s = s*60 + float(x)
    return s
R = {root, f(root)}
tot = 0.0; n = 0; names = []
for line in subprocess.run(["ps","-A","-o","pid=,time=,comm="],capture_output=True,text=True).stdout.splitlines():
    pid, t, comm = line.strip().split(None, 2)
    pid = int(pid)
    if pid == root or ("WebKit" in comm and f(pid) in R):
        tot += secs(t); n += 1; names.append(comm.rsplit("/",1)[-1].replace("com.apple.WebKit.",""))
print(f"{tot:.2f} {n} " + ",".join(names))
