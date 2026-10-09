#!/usr/bin/env python3
"""Windows で O1（v0.1.40）がシャットダウン → 電源オン → サインインの後に自動で立ち上がり、記録するかを点検する。

使い方（git-bash か PowerShell。python は `py -3` でもよい）:
  python win_boot_check.py

基線は shutdown-test.md の「基線」節に手で書いてある（このスクリプトは基線のファイルを使わない）。
読むもの: プロセス・イベントログ・レジストリの GSE-O1・~/.gse の o1_install_id・NDJSON の「行の種類」と「時刻」と meta、
gse-app.log の O1 の行。NDJSON の中身（キーの種類・数値）は読まない・出さない。
判定できないときは「判定しない」と出す（不在を 0 と読まない）。
"""
import collections
import datetime as dt
import glob
import json
import os
import subprocess

HOME = os.path.expanduser("~")
SESS = os.path.join(HOME, "Documents", "GSE-sessions")
# 基線（2026-10-09 00:04・shutdown-test.md と同じ値）
BASE_FILE = "gse_o1_20261008_150341.ndjson"
BASE_INSTALL_ID = "990828be74d2993d"
BASE_PID = 25596
BASE_BOOT = "2026-10-04 00:10:57"
SINCE = "2026-10-09 00:00:00"


def ps(cmd, timeout=60):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip()[:300]
    except Exception as e:
        return None, f"PowerShell を実行できない: {e}"


def reg(key, value):
    try:
        r = subprocess.run(["reg", "query", key, "/v", value], capture_output=True, timeout=20)
        out = r.stdout.decode("cp932", errors="replace")
        rows = [l.strip() for l in out.splitlines() if value in l]
        return rows[0] if rows else "（無い）"
    except Exception as e:
        return f"判定しない: {e}"


def jst(ms):
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%m/%d %H:%M:%S")


def scan(path):
    c = collections.Counter()
    first = last = None
    meta = None
    has_end = False
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            c["<壊れた行>"] += 1
            continue
        t = d.get("type")
        c[t] += 1
        if t == "meta":
            if "session_end" in d:
                has_end = True
            elif meta is None:
                meta = {k: d.get(k) for k in ("app_version", "o1_mode", "o1_install_id")}
        for k in ("t", "wall_ms", "ts_ms", "ts"):
            v = d.get(k)
            if isinstance(v, (int, float)) and v > 1.7e12:
                first = v if first is None else first
                last = v
                break
    return c, first, last, meta, has_end


print("=== 点検の時刻:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("\n=== 1. 本当に電源を入れ直したか")
out, err = ps("(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('yyyy-MM-dd HH:mm:ss')")
print(f"  LastBootUpTime: {out}（基線 {BASE_BOOT}。変わっていれば起動し直した）", err)
ev_cmd = (
    "$s=[datetime]'" + SINCE + "';"
    "Get-WinEvent -FilterHashtable @{LogName='System';StartTime=$s} -ErrorAction SilentlyContinue |"
    " Where-Object { ($_.ProviderName -eq 'Microsoft-Windows-Kernel-General' -and $_.Id -in 12,13) -or"
    " ($_.ProviderName -eq 'Microsoft-Windows-Kernel-Boot' -and $_.Id -eq 27) -or"
    " ($_.ProviderName -eq 'User32' -and $_.Id -eq 1074) -or"
    " ($_.ProviderName -eq 'Microsoft-Windows-Kernel-Power' -and $_.Id -in 41,42,107,109,506,507) } |"
    " Sort-Object TimeCreated | ForEach-Object { '{0:yyyy-MM-dd HH:mm:ss} {1} {2} {3}' -f"
    " $_.TimeCreated, $_.ProviderName.Replace('Microsoft-Windows-',''), $_.Id,"
    " (($_.Message -split \"`n\")[0].Trim()) }"
)
out, err = ps(ev_cmd)
if out is None:
    print("  判定しない:", err)
else:
    for l in out.splitlines():
        print("   ", l[:200])
    print("  読み方: Kernel-General 13 = OS が止まった / 12 = OS が始まった / Kernel-Power 109 = カーネルの電源遷移の開始 /")
    print("          Kernel-Boot 27 = 起動の種類（本文の 0x0 = 通常の起動・0x1 = 高速スタートアップ・0x2 = 休止状態から）/")
    print("          User32 1074 = 誰がシャットダウンしたか / Kernel-Power 41 = 予期しない停止（あれば要注意）")
out, _ = ps("Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-Kernel-Boot';Id=27;StartTime=[datetime]'"
            + SINCE + "'} -ErrorAction SilentlyContinue | % { '{0:HH:mm:ss} ' -f $_.TimeCreated + ($_.Properties | % { $_.Value }) -join ',' }")
print("  Kernel-Boot 27 の値:", out or "（無い）")

print("\n=== 2. 自動で立ち上がったか（プロセス・親・起動の遅れ）")
out, err = ps(
    "$e=(Get-Process explorer -ErrorAction SilentlyContinue | Sort StartTime | Select -First 1);"
    "'explorer ' + $e.Id + ' ' + $e.StartTime.ToString('yyyy-MM-dd HH:mm:ss');"
    "Get-CimInstance Win32_Process -Filter \"Name='gse-next.exe'\" | % {"
    " $p=Get-Process -Id $_.ProcessId; $par=Get-CimInstance Win32_Process -Filter (\"ProcessId=\" + $_.ParentProcessId);"
    " 'gse-next ' + $_.ProcessId + ' ' + $p.StartTime.ToString('yyyy-MM-dd HH:mm:ss') + ' parent=' + $_.ParentProcessId + ':' + $par.Name + ' cmd=' + $_.CommandLine }"
)
print(" ", (out or "").replace("\n", "\n  "), err)
print(f"  基線の PID は {BASE_PID}（別の値なら新しく起動したプロセス）。")
print("  ⚠ 親が explorer.exe なのは、Run キーからの自動起動でも、ダブルクリックで手で開いた場合でも同じ（2026-10-09 に確認）。")
print("    自動起動と言えるのは「研究者がサインイン後に手で開いていない」かつ「起動が explorer の数分後」のとき。cmd.exe なら bat 経由")

print("\n=== 3. 登録（レジストリ・印）")
print("  Run\\GSE-O1:", reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run", "GSE-O1"))
print("  StartupApproved\\Run\\GSE-O1:", reg(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", "GSE-O1"))
print("  （基線では StartupApproved に無かった。初めての自動起動で 02… が現れるのが 10/01 の観察）")
try:
    iid = open(os.path.join(HOME, ".gse", "o1_install_id"), encoding="utf-8").read().strip()
    print(f"  o1_install_id: {iid}（基線 {BASE_INSTALL_ID}・{'一致' if iid == BASE_INSTALL_ID else '不一致'}）")
except OSError as e:
    print("  o1_install_id: 判定しない:", e)

print("\n=== 4. 記録（NDJSON の行の種類と時刻だけ）")
files = sorted(glob.glob(os.path.join(SESS, "gse_o1_*.ndjson")), key=os.path.getmtime)
if not files:
    print("  gse_o1_*.ndjson が 1 本も無い")
for f in files:
    c, first, last, meta, has_end = scan(f)
    tag = "（基線のファイル）" if os.path.basename(f) == BASE_FILE else ""
    print(f"  {os.path.basename(f)} {tag}")
    print(f"    meta={meta}  session_end の行={'あり' if has_end else 'なし'}")
    if first:
        print(f"    最初 {jst(first)} → 最後 {jst(last)}")
    print("    行の種類:", dict(c.most_common(12)))
print("  見るところ: 基線のファイルに session_end が付いたか（シャットダウンの前か、次の起動の掃除で）/")
print("             新しいファイルの meta が 0.1.40・o1_mode・同じ o1_install_id か / 新しいファイルで key が増えているか")

print("\n=== 5. アプリのログ（O1 の行だけ）")
alog = os.path.join(SESS, "gse-app.log")
if not os.path.isfile(alog):
    print("  判定しない（gse-app.log が無い）")
else:
    lines = open(alog, encoding="utf-8", errors="replace").read().splitlines()
    keys = ("O1 MODE", "orphan sweep", "autostart", "auto-submit", "shutdown", "session closed",
            "ERROR", "hook is", "enrollment", "daily-rotate")
    hit = [l for l in lines if l.startswith("2026-10-08T15:") or l[:10] >= "2026-10-09"]
    hit = [l for l in hit if any(k in l for k in keys)]
    for l in hit[-40:]:
        print("   ", l[:210])
    print("  時刻は UTC（+9 時間で日本時間）")
