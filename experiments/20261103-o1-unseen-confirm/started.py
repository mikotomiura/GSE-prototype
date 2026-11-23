"""最初の 1 回の記録（conditions.md U1・判断 7・8）。
  started.py begin <started.json> <ndjson>...   無ければ排他で作る。あれば本の数と SHA-256 が同じときだけ回数を足して続ける
  started.py check <started.json> <ndjson>...   今の入力が started.json と同じでなければ止める
"""
import datetime
import hashlib
import json
import sys


def shas(files):
    return [hashlib.sha256(open(p, "rb").read()).hexdigest() for p in files]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def begin(path, files):
    cur = shas(files)
    try:
        with open(path, "x") as f:
            json.dump({"started_utc": now(), "input_files": len(files), "inputs_sha256": cur, "attempts": [now()]}, f, indent=1)
        return
    except FileExistsError:
        pass
    d = json.load(open(path))
    if d["input_files"] != len(files) or d["inputs_sha256"] != cur:
        sys.exit("前の回と入力が違う（本の数か SHA-256）。再実行は同じ入力のときだけ（判断 8）")
    d["attempts"].append(now())
    json.dump(d, open(path, "w"), indent=1)
    print(f"前の回が途中で止まっていた。同じ入力なので続ける（{len(d['attempts'])} 回目）", file=sys.stderr)


def check(path, files):
    d = json.load(open(path))
    if d["input_files"] != len(files) or d["inputs_sha256"] != shas(files):
        sys.exit("started.json と今の入力が違う")


def selftest():
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        a, b = os.path.join(t, "a"), os.path.join(t, "b")
        open(a, "w").write("1")
        open(b, "w").write("2")
        st = os.path.join(t, "started.json")
        begin(st, [a])
        check(st, [a])
        begin(st, [a])                              # 同じ入力なら続ける
        assert len(json.load(open(st))["attempts"]) == 2
        for bad in ([a, b], [b]):                   # 本を足す・中身が違う
            try:
                begin(st, bad)
            except SystemExit:
                pass
            else:
                raise AssertionError("止まらなかった")
        open(a, "w").write("x")
        try:
            check(st, [a])
        except SystemExit:
            pass
        else:
            raise AssertionError("check が止まらなかった")
    print("started selftest ok", file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        {"begin": begin, "check": check}[sys.argv[1]](sys.argv[2], sys.argv[3:])
