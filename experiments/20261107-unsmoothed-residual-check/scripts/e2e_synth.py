"""配管の合成の通し（実データの前・合成のデータだけ）。中間と新しい中間の形の合成のファイルを一時の dir に作り、
fit.py → residual.py → report.py を本計算と同じ入口で n・o・u の順に回し、出力の形と門を確かめる。

確かめること: 3 列 × 2 データの parts がそろう・npz の読み戻しの照合が 0 件外れ・o の列の当てはめが新しい中間を
使わない読み込み（data.py そのまま）と一致する・u・n の顔ぶれ（人数）が o と同じ・summary.json と tables.md ができる。
使い方: python3 -I e2e_synth.py <seed> <out.json> [jobs]
返り値: 0 = 通った・3 = 通らない。
"""
import gzip
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pinned import H  # noqa: E402
import build_variants as BV  # noqa: E402


def make_data(root, seed):
    rng = np.random.default_rng([seed, 90])
    cm = H.random_model("hmm", 3, rng)
    cm["A"] = 0.9 * np.eye(3) + 0.1 * cm["A"]
    co, cs = os.path.join(root, "co"), os.path.join(root, "cs")
    os.makedirs(co)
    os.makedirs(cs)
    side = {}
    # CoAuthor の形: 8 人 × 21 単位 × 150 行（1 行 1 秒）
    s2w, W, i = {}, {}, 0
    for w in range(8):
        for u in range(21):
            n = 150
            a = 10_000_000 * i + 1000
            t = a + 1000 * np.arange(n)
            obs = H.sample(cm, [n], rng)[0]
            uu = (obs + rng.integers(0, 3, n)) % 26
            feat = [[int(t[j]), 0.0, 0.0, 0.5, 0.1, 0.8, int(obs[j]), 0.3] for j in range(n)]
            keys = [[int(x), "a"] for x in t[::3] - 500]
            json.dump(dict(keys=keys, feat=feat, onsets=[], observed_intervals=[[int(a), int(t[-1])]], events=[]),
                      open(os.path.join(co, "s%05d.json" % i), "w"))
            s2w[str(i).zfill(5)] = "w%02d" % w
            m = BV.n_marks([[int(x) for x in t]])[0]
            W.setdefault("w%02d" % w, []).append((a, dict(o=[obs.tolist()], u=[uu.tolist()], n=[[int(b) for b in m]])))
            i += 1
    json.dump(s2w, open(os.path.join(co, "sessions.json"), "w"))
    side["coauthor"] = [[r for _, r in sorted(W[w], key=lambda x: x[0])] for w in sorted(W)]
    # CS1 の形: 8 人 × 7 課題 × 2 まとまり × 200 行
    u2w, W, i = {}, {}, 0
    for w in range(8):
        for u in range(7):
            base = 100_000_000 * i
            feat, blocks, o_s, u_s, n_s, keys = [], [], [], [], [], []
            for b in range(2):
                a = base + b * 5_000_000
                t = a + 1000 * np.arange(200)
                obs = H.sample(cm, [200], rng)[0]
                uu = (obs + rng.integers(0, 3, 200)) % 26
                feat += [[int(t[j]), 0.0, 0.0, 0.5, 0.1, 0.8, int(obs[j]), 0.3] for j in range(200)]
                blocks.append([int(a), int(t[-1])])
                keys += [[int(x), "a"] for x in t[::4]]
                o_s.append(obs.tolist())
                u_s.append(uu.tolist())
                n_s.append([int(x) for x in BV.n_marks([[int(x) for x in t]])[0]])
            json.dump(dict(keys=keys, feat=feat, onsets=[], observed_intervals=blocks, blocks=blocks, events=[]),
                      open(os.path.join(cs, "u%05d.json" % i), "w"))
            u2w[str(i).zfill(5)] = "w%02d" % w
            W.setdefault("w%02d" % w, []).append((min(k[0] for k in keys), dict(o=o_s, u=u_s, n=n_s)))
            i += 1
    json.dump(u2w, open(os.path.join(cs, "units.json"), "w"))
    side["cs1"] = [[r for _, r in sorted(W[w], key=lambda x: x[0])] for w in sorted(W)]
    paths = {}
    for ds in ("coauthor", "cs1"):
        p = os.path.join(root, "side_%s.json.gz" % ds)
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump(dict(dataset=ds, writers=side[ds]), f)
        paths[ds] = p
    return dict(coauthor=co, cs1=cs), paths


def main(seed, out, jobs):
    t0 = time.time()
    R = {}
    with tempfile.TemporaryDirectory() as td:
        work, side = make_data(td, seed)
        res_dir, raw = os.path.join(td, "results"), os.path.join(td, "raw")
        os.makedirs(res_dir)
        os.makedirs(raw)
        ok = True
        for col in ("n", "o", "u"):
            for ds in ("coauthor", "cs1"):
                for sc, extra in (("fit.py", [str(jobs)]), ("residual.py", [])):
                    r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, sc), ds, col, work[ds], side[ds],
                                        str(seed), res_dir, raw] + extra + ["--run-id", "e2e"], capture_output=True, text=True)
                    R["%s %s %s" % (sc, col, ds)] = r.returncode
                    if r.returncode != 0:
                        R["stderr"] = r.stderr[-3000:]
                        ok = False
                        break
        if ok:
            subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "report.py"), res_dir, "--run-id", "e2e"], check=True)
            S = json.load(open(os.path.join(res_dir, "summary.json"), encoding="utf-8"))
            cols = S["columns"]
            R["parts_complete"] = all(ds in cols.get(c, {}) and "fit" in cols[c][ds] and "residual" in cols[c][ds]
                                      for c in ("o", "u", "n") for ds in ("coauthor", "cs1"))
            R["npz_check_ok"] = all(cols[c][ds]["npz_check"]["mismatched"] == 0 and cols[c][ds]["npz_check"]["checked"] > 0
                                    for c in ("o", "u", "n") for ds in ("coauthor", "cs1"))
            same_panel = True
            for ds, pn in (("coauthor", "P15"), ("cs1", "C5")):
                for k in cols["o"][ds]["fit"]["em"][pn]:
                    a = cols["o"][ds]["fit"]["em"][pn][k]
                    for c in ("u", "n"):
                        b = cols[c][ds]["fit"]["em"][pn][k]
                        same_panel = same_panel and a["writers"] + a["missing"] == b["writers"] + b["missing"]
            R["same_panel"] = bool(same_panel)
            # o の列は新しい中間を使わない読み込み（side = "-"）と同じ値になる
            r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "fit.py"), "cs1", "o", work["cs1"], "-",
                                str(seed), os.path.join(td, "res2"), raw, str(jobs), "--run-id", "e2e"], capture_output=True, text=True)
            b = json.load(open(os.path.join(td, "res2", "parts", "fit.cs1.o.json"), encoding="utf-8"))["fit"]["em"]
            a = json.load(open(os.path.join(res_dir, "parts", "fit.cs1.o.json"), encoding="utf-8"))["fit"]["em"]
            strip = lambda d: json.dumps(d, sort_keys=True)  # noqa: E731
            R["o_without_sidecar_same"] = r.returncode == 0 and strip(a) == strip(b)
            R["tables_md"] = os.path.getsize(os.path.join(res_dir, "tables.md")) > 0
            R["readings_present"] = len(S["readings"]["columns"]) == 6 and len(S["readings"]["residual"]) == 9
            ok = all(R[k] for k in ("parts_complete", "npz_check_ok", "same_panel", "o_without_sidecar_same", "tables_md",
                                    "readings_present"))
        R["passed"] = bool(ok)
    R["seconds"] = time.time() - t0
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(R))
    return 0 if R["passed"] else 3


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4))
