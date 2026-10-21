"""Self-test of the A4 matching path on synthetic writers (no human data, no GPU): fake reconstructions equal to the
true text (full) and the true window text (windows) must be matched; A4 stays out of the strongest attacker.

    python -I scripts/selftest_a4.py                       # PASS
    MAIN_MUTATE=a4_unnormalised python -I scripts/selftest_a4.py   # FAIL
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a4_keytar  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import evaluate  # noqa: E402
import matching  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402

FAIL = []


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


def main():
    check("normalise", evaluate.a4_norm("Hello,  World!\nOK") == "hello world ok")
    c = evaluate.a4_costs("abc", [A.Cand("abcd"), A.Cand("ABC.")])
    check("normalised distance", abs(c[0] - 0.25) < 1e-12 and c[1] == 0.0)
    seed = seeds.read_seed()
    per, take = 14, 4
    tmp = tempfile.mkdtemp(prefix="a4selftest")
    try:
        ws = corpus.synthetic_corpus(seed, prompts=4, per_prompt=per, tag="main")
        kept = {}
        for w in ws:
            w.rows = corpus.active_rows(w.rows)
            if not corpus.exclusion_reason(w):
                kept.setdefault(w.prompt, {})[w.writer] = w
        sample = matching.eval_sample(seed, {p: list(v) for p, v in kept.items()}, take)
        for p, ids in sample.items():
            for wid in ids:
                w = kept[p][wid]
                inputs = a4_keytar.writer_inputs(w.rows, w.text, seed, p, wid)
                words = re.findall(r"[A-Za-z0-9]+", w.text)
                rec = {}
                for v, d in inputs.items():
                    win = {}
                    for key in d["windows"]:
                        k, si = map(int, key.split(":"))
                        final, origins = corpus.replay_origins(w.rows)
                        valid, _ = matching.true_window_starts(w.rows, final, origins,
                                                               re.findall(r"[A-Za-z0-9]+", final), words, k)
                        s = valid[si][2]
                        win[key] = " ".join(words[s:s + k])
                    rec[v] = {"full": w.text, "windows": win}
                with open(os.path.join(tmp, "%s__%s.json" % (p, wid)), "w", encoding="utf-8") as f:
                    json.dump({"prompt": p, "writer": wid, "variants": rec, "stats": {},
                               "source": a4_keytar.source_hashes(w),
                               "fingerprint": dict(a4_keytar.fingerprint(), dry=False)}, f)
        out = os.path.join(tmp, "out.json")
        args = argparse.Namespace(source="synthetic", root=None, out=out, workers=1, all=False, forms="main",
                                  a4_dir=tmp, a4_partial=False, per_prompt=per, per_prompt_sample=take, open_world_n=10,
                                  no_timing=True, cache_dir=None, exploratory_3_5=None)
        run_main.run(args)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        ref = res["main500"]["reference_A4"]
        check("A4 cells", any(k.startswith("full|R0|A4|10") for k in ref))
        check("A4 full accuracy", ref.get("full|R0|A4|10", {}).get("acc") == 1.0)
        check("A4 R3-t accuracy", ref.get("full|R3-t(100)|A4|10", {}).get("acc") == 1.0)
        wins = [v["acc"] for k, v in ref.items() if k.startswith("window|R3|A4|10|")]
        check("A4 window accuracy", wins and min(wins) == 1.0)
        check("A4 not strongest", all(v["attacker"] != "A4" for v in res["main500"]["strongest"].values()))
        check("A4 not on R4", not any("|R4(" in k for k in ref))
        check("a4 writers", res["a4_writers"] == sum(len(v) for v in sample.values()))
        # a file without the fingerprint of a real generation is refused
        p0, w0 = sorted(sample)[0], sample[sorted(sample)[0]][0]
        path = os.path.join(tmp, "%s__%s.json" % (p0, w0))
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        d["fingerprint"]["dry"] = True  # also a different fingerprint
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f)
        ctx = argparse.Namespace(a4_dir=tmp)
        try:
            evaluate.load_a4(ctx, kept[p0][w0])
            check("dry file refused", False)
        except ValueError:
            pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAIL" if FAIL else "PASS", len(FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
