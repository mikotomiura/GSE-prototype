"""追記（2026-11-11・conditions.md の追記）: CS1 の種を足す 6 本（番号 27〜32）を回す。合成だけ。

run_synth.py は変えずに読み込む（前の 27 本と同じ生成と当てはめ・ほかの試験がそのハッシュを照らしている）。
このファイルが scripts/ に増えるので、code_hash（scripts/*.py 全体）は前の 27 本と違う。

使い方: python3 -I run_add.py <seed> <out_dir> <jobs> [--run-id ID]
  - 較正は <out_dir>/calibration.json（前の 27 本のコードのハッシュ）を読む（計算し直さない）。
  - 先に P-REREP: 今のコードで複製 00 を回し直し（<out_dir>/rerep_00.json）、前の 00.json と書き手ごとの値・λ・診断がビットまで同じ。
  - 足す 6 本を <out_dir>/replicates/ に、計画を <out_dir>/plan_add.json に書く（前の plan.json は書き換えない）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_synth as RS  # noqa: E402
import synth as SY  # noqa: E402

BASE_CODE_HASH = "bff1edd9fe9a8bd3fa9e30cfff64ed86bc4abc3afdc280145ed42c7b1534c27c"  # 前の 27 本
BASE_ROWS = 27
SAME_AS_BASE = {  # bd5b36c0 と同じでなければならない 4 つ（conditions.md の追記「コードの置き場の直し」・レビュー MEDIUM 1）
    "synth.py": "41c60dd5ec954f6d1bd526560c318f96847641533e31f3826f099fb443d64ee3",
    "run_synth.py": "103ad29bcae6eee2b7c95fa117906a7098399effe494203b00775b7f2d951f5f",
    "pinned.py": "02317ec7174be93aa60c18a022ba411d5652cc1f97aab7fd1c0408e254ab8006",
    "analysis.py": "ce20b5855bbe89cbe635f6af40e6f5993f9cb0ff3e47d8771ccd7bbfdfb3f4ef",
}


def check_same_as_base():
    import hashlib
    here = os.path.dirname(os.path.abspath(__file__))
    got = {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest() for f in SAME_AS_BASE}
    if got != SAME_AS_BASE:
        sys.exit("bd5b36c0 と同じでなければならないコードが変わっている: %r" % sorted(f for f in got if got[f] != SAME_AS_BASE[f]))
    return got


def plan_all():
    """前の 27 本（RS.plan() そのまま）の後ろに、足す 6 本を番号 27〜32 で並べる。"""
    rows = RS.plan()
    assert len(rows) == BASE_ROWS
    add = [dict(strand="dose", shape="cs1", K=3, g=g, seed=1) for g in RS.DOSE]
    add += [dict(strand="dose", shape="cs1", K=3, g=0.0, seed=s) for s in (3, 4)]
    for i, r in enumerate(add):
        r["no"] = BASE_ROWS + i
    return rows + add


def strip_sec(R):
    return [{k: v for k, v in w.items() if k != "sec"} for w in R["writers"]]


def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    seed, out, jobs = int(argv[0]), argv[1], int(argv[2])
    same = check_same_as_base()
    ch = RS.code_hash()
    if ch == BASE_CODE_HASH:
        sys.exit("今のコードのハッシュが前の 27 本と同じ（想定と違う）")
    cd = json.load(open(os.path.join(out, "calibration.json")))
    if cd.get("seed") != seed or cd.get("code_hash") != BASE_CODE_HASH:
        sys.exit("前の calibration.json の seed かコードのハッシュが条件の値と違う")
    cal = {int(k): v for k, v in cd["cal"].items()}
    m0s = {K: SY.make_m0(K, seed) for K in (3, 5)}
    rows = plan_all()
    added = rows[BASE_ROWS:]
    P = dict(run_id=run_id, seed=seed, code_hash=ch, base_code_hash=BASE_CODE_HASH, kept=[r["no"] for r in added],
             rows=added, reused=[], same_as_base=same)
    # P-REREP
    old = json.load(open(os.path.join(out, "replicates", "00.json")))
    if old.get("code_hash") != BASE_CODE_HASH or old["rep"] != rows[0] or old.get("seed") != seed:
        sys.exit("前の複製 00 のハッシュか行が条件の値と違う")
    rr = os.path.join(out, "rerep_00.json")
    if not os.path.exists(rr):
        R0 = RS.run_rep(rows[0], cal, m0s, seed, jobs)
        R0.update(run_id=run_id, seed=seed, code_hash=ch)
        json.dump(R0, open(rr, "w"))
    R0 = json.load(open(rr))
    if R0.get("code_hash") != ch or R0.get("seed") != seed or R0.get("rep") != rows[0]:
        sys.exit("rerep_00.json のコードのハッシュが今回と違う（消してからやり直す）")
    rerep_ok = (strip_sec(R0) == strip_sec(old) and R0["lams"] == old["lams"] and R0["planted"] == old["planted"]
            and R0["pool_full_diag"] == old["pool_full_diag"] and R0["lam"] == old["lam"])
    P["p_rerep"] = bool(rerep_ok)
    json.dump(P, open(os.path.join(out, "plan_add.json"), "w"), indent=1)
    if not rerep_ok:
        sys.exit("P-REREP が外れた（今のコードで複製 00 が前と同じにならない）。止めて研究者に聞く")
    print("P-REREP 通過", flush=True)
    for r in added:
        p = os.path.join(out, "replicates", "%02d.json" % r["no"])
        if os.path.exists(p):
            o = json.load(open(p))
            if o.get("seed") != seed or o.get("code_hash") != ch or o["rep"] != r:
                sys.exit("複製 %02d の seed・コードのハッシュ・行が今回と違う（消してからやり直す）" % r["no"])
            P["reused"].append(r["no"])
            continue
        R = RS.run_rep(r, cal, m0s, seed, jobs)
        R.update(run_id=run_id, seed=seed, code_hash=ch)
        json.dump(R, open(p, "w"))
        print("複製 %02d（%s・%s・g* %g・種 %d）%.0f 秒" % (r["no"], r["strand"], r["shape"], r["g"], r["seed"],
                                                       R["seconds"]["total"]), flush=True)
    json.dump(P, open(os.path.join(out, "plan_add.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
