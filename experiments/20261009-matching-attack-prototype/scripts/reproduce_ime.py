"""Check, before the main computation, that the per-trial distances of S_no_time and S_counts_only reproduce the
IME paper's published closed-set results at k = 1 (design.md section 6.4).

  reproduce_ime.py --trials raw/trials.json --prepare results/prepare.json --dist-dir raw/dist
                   --dist-summary results/distances.json --out results/reproduce_ime.json

The candidates are drawn as closed_set.evaluate draws them (_make_candidates with the trial's seed, from the
scenario pool of phrases with distinct readings) and the tie is broken as closed_set.attack breaks it (one
random key per candidate from the tie seed). The distances are looked up in raw/dist instead of being computed
by attack. The number of correct trials and the mean rank of the true phrase must equal the published acc_raw
and mean_rank for every K and both feature sets; otherwise the script exits with status 1. The same candidates are
also scored through matching.py's s_scores and credit, which must agree with the tie-broken choice wherever the
credit is 0 or 1 (a check of matching.py's scoring path on real data).
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402
import data as dataload  # noqa: E402
import matching  # noqa: E402

FEATURE_VARIANT = {"no_time": "S_no_time", "counts_only": "S_counts_only"}


def run(d, kit, rcfg, published):
    cs = kit.closed_set
    seed = rcfg["seed"]
    tag = rcfg["tag"]
    by_id = dict((p["phrase_id"], p) for p in d["corpus"])
    typed_of_s = dict((s, dict((p["phrase_id"], d["typed"][s][j]) for j, p in enumerate(pool)))
                      for s, pool in d["pools"].items())
    pos_of_s = dict((s, dict((p["phrase_id"], j) for j, p in enumerate(pool))) for s, pool in d["pools"].items())
    out = {}
    ok = True
    for K in rcfg["K"]:
        out[str(K)] = {}
        for f in rcfg["features"]:
            dist = d["dist"][FEATURE_VARIANT[f]]
            correct = 0
            rank_sum = 0
            path_mismatch = 0
            for i, t in enumerate(d["trials"]):
                s = t["scenario"]
                pool = d["pools"][s]
                typed_of = typed_of_s[s]
                pos_of = pos_of_s[s]
                true_ph = by_id[t["phrase_id"]]
                tseed = cs._sub_seed(seed, "trial", tag + t["trial_id"], K)
                cands, ti = cs._make_candidates(random.Random(cs._sub_seed(tseed, "cand")), list(pool), true_ph, K,
                                                typed_of, t["typed"])
                dv = dist[i]
                dists = [dv[d["true_j"][i]] if c is true_ph else dv[pos_of[c["phrase_id"]]] for c in cands]
                rng = random.Random(cs._sub_seed(cs._sub_seed(tseed, "tie", f), "tie"))
                keys = [rng.random() for _ in cands]
                order = sorted(range(len(cands)), key=lambda m: (dists[m], keys[m]))
                chosen = cands[order[0]]
                chosen_typed = t["typed"] if order[0] == ti else typed_of[chosen["phrase_id"]]
                ok_trial = 1 if chosen_typed == t["typed"] else 0
                correct += ok_trial
                rank_sum += order.index(ti) + 1
                # the scoring path of matching.py (s_scores and credit) on the same candidates must agree with
                # the tie-broken choice: credit 1 -> correct, credit 0 -> not correct
                decoys = [pos_of[c["phrase_id"]] for m, c in enumerate(cands) if m != ti]
                cr = matching.credit(*matching.s_scores(dist, [i], [decoys], [d["true_j"][i]]))
                if (cr == 1.0 and not ok_trial) or (cr == 0.0 and ok_trial):
                    path_mismatch += 1
            n = len(d["trials"])
            pub = published["results"][str(K)][f]
            mine_acc = correct / n
            mine_rank = rank_sum / n
            match = (pub["n"] == n and abs(pub["acc_raw"] - mine_acc) < 1e-12
                     and abs(pub["mean_rank"] - mine_rank) < 1e-9 and path_mismatch == 0)
            ok = ok and match
            out[str(K)][f] = {"n": n, "correct": correct, "acc_raw": mine_acc, "mean_rank": mine_rank,
                              "published_acc_raw": pub["acc_raw"], "published_mean_rank": pub["mean_rank"],
                              "published_n": pub["n"], "match": match,
                              "matching_path_disagreements": path_mismatch}
    return out, ok


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--trials", required=True)
    ap.add_argument("--prepare", required=True)
    ap.add_argument("--dist-dir", required=True)
    ap.add_argument("--dist-summary", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg)
    rcfg = cfg["reproduce_ime"]
    d = dataload.load(cfg, kit, a.trials, a.prepare, a.dist_dir, a.dist_summary,
                      [FEATURE_VARIANT[f] for f in rcfg["features"]])
    pub_path = kitload.input_path(cfg, "published_closed_set")
    published, pub_sha = kitload.read_json(pub_path)
    if published["seed"] != rcfg["seed"]:
        raise kitload.CheckError("the published results used seed %s" % published["seed"])
    for k in ("corpus", "recipes"):
        if published["%s_sha256" % k] != cfg["inputs"][k]["sha256"]:
            raise kitload.CheckError("the published results used another %s file" % k)
    if published["config_sha256"] != cfg["inputs"]["plan_config"]["sha256"]:
        raise kitload.CheckError("the published results used another plan configuration")
    res, ok = run(d, kit, rcfg, published)
    prep, _ = kitload.read_json(a.prepare)
    _, dsha = kitload.read_json(a.dist_summary)
    kitload.write_json(a.out, {"format": "matching-attack-reproduce-ime/1", "published_sha256": pub_sha,
                               "trials_json_sha256": prep["trials_json_sha256"], "distances_json_sha256": dsha,
                               "config_sha256": kitload.sha256_file(kitload.CONFIG),
                               "all_match": ok, "results": res})
    for K, fs in sorted(res.items(), key=lambda kv: int(kv[0])):
        for f, r in sorted(fs.items()):
            print("  K=%s %s: %d/%d correct (published acc_raw %.6f) mean rank %.4f (published %.4f) %s" % (
                K, f, r["correct"], r["n"], r["published_acc_raw"], r["mean_rank"], r["published_mean_rank"],
                "OK" if r["match"] else "MISMATCH"))
    if not ok:
        print("!! the k = 1 reproduction of the IME paper's closed set does not match; stop", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except kitload.CheckError as e:
        print("!! %s" % e, file=sys.stderr)
        sys.exit(1)
