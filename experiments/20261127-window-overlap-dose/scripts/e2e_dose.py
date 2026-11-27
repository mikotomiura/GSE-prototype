"""配管の合成の通し（実データの前・合成のデータだけ）。合成の中間を一時の dir に作り、run.sh と同じ入口で
全 21 列の drive.py fit → residual → extra → analyze.py を回し、出力の形と門を確かめる。列ごとの時間も測る（見積もりに使う）。

確かめること: 全列の parts がそろう・npz の読み戻しの照合と D_s の照合が 0 件外れ・パネルの顔ぶれ（人数）が全列で同じ・
analyze の内部の照合（書き手ごとの値の中央値 = fit の summary）が 0 件外れ・readings.json に型と英文がある・
P-ROWS（rows_check.py）が通る・端の再現の門の配管: S13 の fit.py・residual.py を u・n で直接回した parts から作った
S13 の形の summary と、列 A1・A30 が repro_dose.py で 0 件外れ（A30 の kit の間引きが S13 の n の印と同じことも含む）。
使い方: python3 -I e2e_dose.py <seed> <out.json> [jobs] [--keep DIR]
返り値: 0 = 通った・3 = 通らない。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import synth_work as SW  # noqa: E402
import load_dose as LD  # noqa: E402

S13 = os.path.realpath(os.path.join(HERE, "../../20261107-unsmoothed-residual-check/scripts"))


def sub(args):
    return subprocess.run([sys.executable, "-I", "-X", "utf8"] + args, capture_output=True, text=True)


def main(seed, out, jobs, keep=None):
    t0 = time.time()
    R = dict(steps={}, seconds_per_column={})
    td = tempfile.mkdtemp()
    try:
        co, side = SW.make(td, seed, n_w=6, n_u=22, lengths=(300, 700), tag=91)
        res, raw = os.path.join(td, "results"), os.path.join(td, "raw")
        os.makedirs(res)
        os.makedirs(raw)
        ok = True
        for col in LD.ORDER:
            t1 = time.time()
            for mode, extra in (("fit", [str(jobs)]), ("residual", []), ("extra", [])):
                r = sub([os.path.join(HERE, "drive.py"), mode, col, co, side, str(seed), res, raw] + extra + ["--run-id", "e2e"])
                R["steps"]["%s %s" % (mode, col)] = r.returncode
                if r.returncode != 0:
                    R["stderr"] = r.stderr[-3000:]
                    ok = False
                    break
            R["seconds_per_column"][col] = time.time() - t1
            if not ok:
                break
        if ok:
            r = sub([os.path.join(HERE, "analyze.py"), res, raw, str(seed), "--run-id", "e2e"])
            R["analyze_exit"] = r.returncode
            if r.returncode != 0:
                R["stderr"] = r.stderr[-3000:]
            S = json.load(open(os.path.join(res, "summary.json"), encoding="utf-8"))
            cols = S["columns"]
            R["parts_complete"] = set(cols) == set(LD.ORDER)
            R["npz_check_ok"] = all(c["npz_check"]["checked"] > 0 and c["npz_check"]["mismatched"] == 0 for c in cols.values())
            R["ds_check_ok"] = all(c["extra"]["ds_check"]["checked"] > 0 and c["extra"]["ds_check"]["mismatched"] == 0
                                   for c in cols.values())
            tot = {col: {k: c["cells"][k]["writers"] + c["cells"][k]["missing"] for k in c["cells"]} for col, c in cols.items()}
            R["same_panel"] = len({json.dumps(v, sort_keys=True) for v in tot.values()}) == 1
            R["internal_consistency"] = S["internal_consistency"]
            Rd = S["readings"]
            R["readings_present"] = bool(Rd) and Rd["type"] in ("1", "2", "3", "なし", "外れ") and os.path.exists(
                os.path.join(res, "readings.json")) and bool(Rd["sentences"]["new_section_result"])
            R["type_on_synthetic"] = Rd and Rd["type"]
            R["figure_csv"] = os.path.getsize(os.path.join(res, "figure_medians.csv")) > 0
            # P-ROWS
            r = sub([os.path.join(HERE, "rows_check.py"), co, side, str(seed), os.path.join(td, "rows.json")])
            R["rows_check_exit"] = r.returncode
            # 端の再現の門の配管: S13 のコードを u・n で直接回す
            res13, raw13 = os.path.join(td, "res13"), os.path.join(td, "raw13")
            os.makedirs(raw13)
            ok13 = True
            for col in ("u", "n"):
                for scr, extra in (("fit.py", [str(jobs)]), ("residual.py", [])):
                    r = sub([os.path.join(S13, scr), "coauthor", col, co, side, str(seed), res13, raw13] + extra + ["--run-id", "e2e"])
                    ok13 = ok13 and r.returncode == 0
            fake = dict(columns={})
            for col in ("u", "n"):
                f = json.load(open(os.path.join(res13, "parts", "fit.coauthor.%s.json" % col), encoding="utf-8"))
                g = json.load(open(os.path.join(res13, "parts", "res.coauthor.%s.json" % col), encoding="utf-8"))
                fake["columns"][col] = dict(coauthor=dict(fit=f["fit"], residual=g["residual"]))
            fp = os.path.join(td, "s13_like_summary.json")
            json.dump(fake, open(fp, "w"))
            rr = {}
            for col in ("A1", "A30"):
                o = os.path.join(td, "repro_%s.json" % col)
                r = sub([os.path.join(HERE, "repro_dose.py"), os.path.join(res, "summary.json"), fp, o, col])
                rr[col] = json.load(open(o)) if os.path.exists(o) else dict(passed=False, stderr=r.stderr[-1000:])
            R["repro_gate_plumbing"] = dict(s13_direct_ok=ok13, **{c: dict(passed=v.get("passed"), leaves=v.get("leaves"),
                                                                          mismatched=v.get("mismatched")) for c, v in rr.items()})
            ok = (R["analyze_exit"] == 0 and R["parts_complete"] and R["npz_check_ok"] and R["ds_check_ok"] and R["same_panel"] and
                  R["internal_consistency"]["mismatched"] == 0 and R["internal_consistency"]["checked"] > 0 and R["readings_present"]
                  and R["figure_csv"] and R["rows_check_exit"] == 0 and ok13 and all(v.get("passed") for v in rr.values()))
        R["passed"] = bool(ok)
    finally:
        if keep:
            shutil.copytree(td, keep, dirs_exist_ok=True)
        shutil.rmtree(td, ignore_errors=True)
    R["seconds"] = time.time() - t0
    json.dump(R, open(out, "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(dict(passed=R["passed"], seconds=R["seconds"], type=R.get("type_on_synthetic")), ensure_ascii=False))
    return 0 if R["passed"] else 3


if __name__ == "__main__":
    a = sys.argv[1:]
    keep = None
    if "--keep" in a:
        i = a.index("--keep")
        keep = a[i + 1]
        a = a[:i] + a[i + 2:]
    sys.exit(main(int(a[0]), a[1], int(a[2]) if len(a) > 2 else 4, keep))
