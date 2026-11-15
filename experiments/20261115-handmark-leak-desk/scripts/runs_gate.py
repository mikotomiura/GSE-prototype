"""回の記録（runs.txt）を読み、同じ回をもう一度回してよいかを決める（事前登録 S1-F5）。

終了コード:
  10  回してよい（この回で統計に入った実行が無い・または日数の門で止まった実行だけ）
   0  止める（統計に入った実行がある。判定まで進んだもの・終わりの行が無いもの）
   3  止める（回の記録が読めない・形が違う）。想定していない誤りもすべてここ（fail-closed）

行の形: {"event": "started", "run": str, "phase": str, ...} と
        {"event": "finished", "run": str, "phase": str, "judged": bool, ...}
"""
import json
import os
import stat
import sys

GO, BLOCKED, BROKEN = 10, 0, 3


def decide(path, phase):
    # 無いときだけ「回してよい」。読めない（親の権限・ぶら下がったリンク）・通常のファイルでないは止める
    # （os.path.exists は OSError を False にして門を開くので使わない・/cross-review 3 巡目）
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        if os.path.lexists(path):
            return BROKEN
        return GO
    if not stat.S_ISREG(st.st_mode):
        return BROKEN
    phase_of, done = {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if not isinstance(r, dict):
                return BROKEN
            ev, run, ph = r.get("event"), r.get("run"), r.get("phase")
            if ev not in ("started", "finished") or not isinstance(run, str) or not isinstance(ph, str):
                return BROKEN
            if ev == "started":
                if run in phase_of:
                    return BROKEN
                phase_of[run] = ph
            else:
                if phase_of.get(run) != ph or run in done or not isinstance(r.get("judged"), bool):
                    return BROKEN
                done[run] = r["judged"]
    # この回の実行で、判定まで進んだもの・終わりの行が無いものが 1 つでもあれば止める
    mine = [k for k, ph in phase_of.items() if ph == phase]
    return BLOCKED if any(done.get(k, True) for k in mine) else GO


def main(argv):
    try:
        path, phase = argv
        return decide(path, phase)
    except Exception:   # 読めない・権限が無い・想定外は全部止める
        return BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
