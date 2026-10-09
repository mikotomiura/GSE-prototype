#!/usr/bin/env python3
"""Windows で O1（v0.1.40）がスリープをまたいで記録・送信を続けるかを点検する。

使い方（git-bash か PowerShell。python は `py -3` でもよい）:
  python win_sleep_check.py snapshot   # 寝かせる前に 1 回。基線を同じフォルダに書く
  python win_sleep_check.py check      # 復帰して 2 分ほど待ってから 1 回

読むもの: NDJSON の「行の種類」と「時刻」、gse-app.log の行数と新しい行、Windows のイベントログ、
プロセスの有無。NDJSON の中身（キーの種類・数値）は読まない・出さない。

判定できないときは「判定しない」と出す（不在を 0 と読まない）。
macOS 版の考え方は .steering/20260910-intake-windows-and-cpu-convention/post-wake-check.sh。
"""
import collections
import datetime as dt
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "pre-sleep-snapshot.json")
HOME = os.path.expanduser("~")
# Documents が OneDrive に移されている端末があるので、両方を探す。
SESSION_DIRS = [
    os.path.join(HOME, "Documents", "GSE-sessions"),
    os.path.join(HOME, "OneDrive", "Documents", "GSE-sessions"),
    os.path.join(HOME, "OneDrive", "ドキュメント", "GSE-sessions"),
]
GAP_MS = 60_000  # feat はおよそ 1 Hz。60 秒を超える穴を「途切れ」とみなす


def now_text():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def jst(ms):
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%m/%d %H:%M:%S")


def session_dir():
    for d in SESSION_DIRS:
        if os.path.isdir(d):
            return d
    return None


def latest_o1_file(d):
    fs = glob.glob(os.path.join(d, "gse_o1_*.ndjson"))
    return max(fs, key=os.path.getmtime) if fs else None


def scan(path):
    """行の種類の数と、時刻（t か wall_ms）の並びだけを返す。"""
    c = collections.Counter()
    ts = []
    meta = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            c["<壊れた行>"] += 1
            continue
        t = d.get("type")
        c[t] += 1
        if t == "meta" and not meta:
            meta = {
                "app_version": d.get("app_version"),
                "o1_mode": d.get("o1_mode"),
                "has_o1_install_id": bool(d.get("o1_install_id")),
            }
        for k in ("t", "wall_ms", "ts_ms", "ts"):
            v = d.get(k)
            if isinstance(v, (int, float)) and v > 1.7e12:
                ts.append(int(v))
                break
    return c, sorted(ts), meta


def applog_path(d):
    p = os.path.join(d, "gse-app.log")
    return p if os.path.isfile(p) else None


def count_lines(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def gse_running():
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq gse-next.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except Exception as e:  # tasklist が無い・失敗
        return None, f"tasklist を実行できない: {e}"
    rows = [r for r in out.splitlines() if "gse-next.exe" in r]
    return (len(rows) > 0), (rows[0] if rows else "")


def power_events(since_text):
    """スリープ・復帰のイベントを PowerShell で取る。取れなければ None。"""
    ps = (
        "$s=[datetime]'" + since_text + "';"
        "Get-WinEvent -FilterHashtable @{LogName='System';StartTime=$s} -ErrorAction SilentlyContinue |"
        " Where-Object { ($_.ProviderName -eq 'Microsoft-Windows-Kernel-Power' -and $_.Id -in 42,107,506,507) -or"
        " ($_.ProviderName -eq 'Microsoft-Windows-Power-Troubleshooter' -and $_.Id -eq 1) } |"
        " Sort-Object TimeCreated | ForEach-Object { '{0:yyyy-MM-dd HH:mm:ss} {1} {2} {3}' -f"
        " $_.TimeCreated, $_.ProviderName.Replace('Microsoft-Windows-',''), $_.Id,"
        " ($_.Message -split \"`n\")[0].Trim() }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        return None, f"PowerShell を実行できない: {e}"
    return [l for l in r.stdout.splitlines() if l.strip()], r.stderr.strip()[:200]


def sleep_states():
    try:
        r = subprocess.run(["powercfg", "/a"], capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"powercfg を実行できない: {e}"


def find_hwm():
    for base in [os.path.join(HOME, ".gse")] + SESSION_DIRS:
        p = os.path.join(base, ".o1_clock_hwm")
        if os.path.isfile(p):
            try:
                return p, open(p, encoding="utf-8").read().strip()
            except OSError:
                return p, None
    return None, None


def snapshot():
    d = session_dir()
    if not d:
        sys.exit("GSE-sessions のフォルダが見つからない（Documents と OneDrive の両方を探した）。止める。")
    f = latest_o1_file(d)
    if not f:
        sys.exit("O1 の NDJSON（gse_o1_*.ndjson）が 1 本も無い。O1 が動いていない。止める。")
    c, ts, meta = scan(f)
    alog = applog_path(d)
    running, row = gse_running()
    hwm_path, hwm = find_hwm()
    snap = {
        "taken_at": now_text(),
        "session_dir": d,
        "o1_file": os.path.basename(f),
        "o1_file_last_ms": ts[-1] if ts else None,
        "rows": sum(c.values()),
        "meta": meta,
        "applog_lines": count_lines(alog) if alog else None,
        "gse_running": running,
        "hwm": hwm,
        "hwm_path": hwm_path,
    }
    with open(SNAP, "w", encoding="utf-8") as fp:
        json.dump(snap, fp, ensure_ascii=False, indent=2)
    print("基線を書いた:", SNAP)
    for k, v in snap.items():
        print(f"  {k}: {v}")
    print("\n対応しているスリープ状態（powercfg /a）:")
    print(sleep_states())
    if not running:
        print("\n注意: gse-next.exe が動いていない。O1 を起動してから採り直すこと。")
    if not meta.get("o1_mode"):
        print("\n注意: meta に o1_mode が無い。O1 モードで動いていない。")


def check():
    if not os.path.isfile(SNAP):
        sys.exit("基線（pre-sleep-snapshot.json）が無い。寝かせる前に snapshot を採っていないので判定しない。")
    snap = json.load(open(SNAP, encoding="utf-8"))
    d = snap["session_dir"]
    print("=== 点検の時刻:", now_text(), " / 基線:", snap["taken_at"])

    print("\n=== 1. プロセスは生きているか")
    running, row = gse_running()
    print("  ", "生きている" if running else ("判定できない: " + row if running is None else "落ちている"), row)

    print("\n=== 2. 本当に寝たか（イベントログ）")
    ev, err = power_events(snap["taken_at"])
    if ev is None:
        print("  判定しない:", err)
    else:
        # 陽性対照: 基線以降に System ログ自体が取れているか
        if not ev:
            print("  基線以降に Kernel-Power 42/107/506/507・Power-Troubleshooter 1 が 1 件も無い。")
            print("  → 寝ていない見込み（または権限で読めない）。下の 4 の穴と合わせて読むこと。", err)
        for l in ev[-12:]:
            print("   ", l[:180])
        print("  読み方: Kernel-Power 42 = スリープに入った / 107 = 復帰 / 506・507 = モダンスタンバイの出入り /")
        print("          Power-Troubleshooter 1 = 復帰（スリープ時刻と復帰時刻が本文にある）")

    print("\n=== 3. 基線以降のアプリのログ")
    alog = applog_path(d)
    pre = snap.get("applog_lines")
    if not alog or pre is None:
        print("  判定しない（gse-app.log か基線の行数が無い）")
    else:
        lines = open(alog, encoding="utf-8", errors="replace").read().splitlines()
        new = lines[pre:]
        print(f"  {pre} 行 → {len(lines)} 行（新しい行 {len(new)}）")
        keys = ("auto-submit", "rotation", "rotate", "periodic", "ERROR", "WARN", "starved", "hook")
        for l in new:
            if any(k in l for k in keys):
                print("   ", l[:200])

    print("\n=== 4. NDJSON の連続性（いちばん強い証拠。行の種類と時刻だけ）")
    files = sorted(glob.glob(os.path.join(d, "gse_o1_*.ndjson")), key=os.path.getmtime)
    start = snap.get("o1_file_last_ms") or 0
    for f in files:
        if os.path.getmtime(f) * 1000 < start - 60_000:
            continue
        c, ts, meta = scan(f)
        after = [x for x in ts if x >= start]
        print(f"  {os.path.basename(f)}  meta={meta}")
        if not after:
            print("    基線以降の行が無い")
            continue
        print(f"    基線以降: {jst(after[0])} → {jst(after[-1])}  ({len(after)} 行)")
        gaps = [(after[i] - after[i - 1], after[i - 1], after[i]) for i in range(1, len(after))
                if after[i] - after[i - 1] > GAP_MS]
        if not gaps:
            print("    60 秒を超える穴は無い → 寝ていない（または寝ている間も記録が続いた＝モダンスタンバイの可能性）")
        for g, a, b in gaps:
            print(f"    穴 {g / 1000:.0f} 秒: {jst(a)} → {jst(b)}  ← 2 のスリープ時刻と比べる")
        last_gap_end = gaps[-1][2] if gaps else after[0]
        print("    行の種類（全体）:", dict(c.most_common(12)))
        print("    ※ 復帰後に打鍵（key）が増えているかは、復帰後に数十文字打ってから点検すること")

    print("\n=== 5. 時計の高水位（巻き戻り）")
    hwm_path, hwm = find_hwm()
    print(f"  基線 {snap.get('hwm')} → 現在 {hwm}  ({hwm_path})")
    try:
        if snap.get("hwm") and hwm and int(hwm) < int(snap["hwm"]):
            print("  巻き戻っている（要調査）")
    except ValueError:
        print("  数字として読めない（判定しない）")

    print("\n=== 6. 合否の言い方")
    print("  6 項目（生存・寝た証拠・ログ・NDJSON の穴がスリープ時刻と一致・復帰後に key と feat が増えた・巻き戻りなし）")
    print("  のうち実測で確かめた数と、判定しなかった数を分けて書く。1 つでも欠けたら「成立した」と書かない。")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "snapshot":
        snapshot()
    elif mode == "check":
        check()
    else:
        sys.exit("使い方: python win_sleep_check.py snapshot | check")
