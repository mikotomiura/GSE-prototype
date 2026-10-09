"""Per-trial distances of the simulation attacker S for every variant (design.md section 6.2).

  distances.py --trials raw/trials.json --prepare results/prepare.json --out-dir raw/dist
               --summary results/distances.json [--processes 4]

For every scored trial outside the skipped scenarios and every phrase p of its scenario's pool (the corpus with
duplicate readings removed, restricted by _scenario_pool), the distance between the trial's observed tokens and
the predicted tokens of p under the trial's scenario and speed, as closed_set.py computes it (Predictor with the
IME paper's seed, timing "none", _distance). The variant decides how the tokens are formed:
  ime              the IME paper's tokens (runs "exact" = no_time, runs "count" = counts_only)
  rle w            one token per maximal run of one category, its count ceil(count / w) (w null: count 1)
  merge_categories the no_time tokens with the categories of each group renamed to the group
The distances are integers (every cost is a count when no time is used) and are written as one array of 32-bit
integers per variant, trial after trial in the order of raw/trials.json, each trial's values in pool order.
"""
import argparse
import math
import os
import sys
from array import array
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402

FORMAT = "matching-attack-distances/1"


def rle(tokens, w):
    out = []
    for c, n, _ in tokens:
        if out and out[-1][0] == c:
            out[-1][1] += n
        else:
            out.append([c, n])
    return tuple((c, 1 if w is None else -(-n // w), 0) for c, n in out)


def rename(tokens, groups):
    m = {}
    for g, cats in groups.items():
        for c in cats:
            m[c] = g
    return tuple((m.get(c, c), n, iv) for c, n, iv in tokens)


def transform(tokens, variant):
    kind = variant["kind"]
    if kind == "rle":
        return rle(tokens, variant["w"])
    if kind == "merge_categories":
        return rename(tokens, variant["groups"])
    raise ValueError("unknown variant kind %s" % kind)


def obs_tokens(kit, ev, variant):
    cs, so = kit.closed_set, kit.simulate_obs
    runs = variant["runs"] if variant["kind"] == "ime" else "exact"
    base = cs._tokens(cs._normalize(so.apply_features([tuple(e) for e in ev], "none", runs)), runs)
    return base if variant["kind"] == "ime" else transform(base, variant)


def pred_tokens(pred, phrase, scenario, speed, variant):
    runs = variant["runs"] if variant["kind"] == "ime" else "exact"
    v = pred.tokens(phrase, scenario, speed, "none", runs)
    if v is None:
        raise kitload.CheckError("phrase %s cannot be typed in scenario %s" % (phrase["phrase_id"], scenario))
    return v[0] if variant["kind"] == "ime" else transform(v[0], variant)


def scenario_pools(kit, recipes, os_name, corpus, scenarios):
    cs = kit.closed_set
    base = cs._pool_by_reading(corpus)
    return base, dict((s, cs._scenario_pool(recipes, os_name, s, base)) for s in sorted(scenarios))


def provenance(cfg):
    """What the distances depend on besides the trials and the pools: the definitions of the S variants, this
    file, and the kit files (data.load refuses distances computed under other values)."""
    return {"variants": dict((n, v) for n, v in cfg["variants"].items() if v["attacker"] == "S"),
            "distances_py_sha256": kitload.sha256_file(os.path.abspath(__file__)),
            "kit_code": dict((rel, cfg["code"][rel]) for _, rel in kitload.KIT_MODULES),
            "inputs": dict((k, cfg["inputs"][k]["sha256"]) for k in ("corpus", "recipes", "plan_config")),
            "os": cfg["os"], "attacker_seed": cfg["attacker_seed"]}


def used_trials(trials, cfg):
    return [t for t in trials if t["scenario"] not in cfg["skip_scenarios"]]


_W = {}


def _worker_init(trials_path, trials_sha):
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg)
    corpus, recipes, pcfg = kitload.load_inputs(cfg, kit)
    data, _ = kitload.read_json(trials_path, trials_sha)
    trials = used_trials(data["trials"], cfg)
    base, pools = scenario_pools(kit, recipes, cfg["os"], corpus, set(t["scenario"] for t in trials))
    _W.update({"cfg": cfg, "kit": kit, "recipes": recipes, "pcfg": pcfg, "trials": trials, "pools": pools})


def compute_variant(name):
    kitload.check_init()
    cfg, kit, trials, pools = _W["cfg"], _W["kit"], _W["trials"], _W["pools"]
    variant = cfg["variants"][name]
    cs = kit.closed_set
    pred = cs.Predictor(_W["recipes"], _W["pcfg"], cfg["os"], cfg["attacker_seed"])
    tok_id = {}      # token sequence -> small integer, so that the memo is keyed by two integers
    toks = []

    def intern(tk):
        i = tok_id.get(tk)
        if i is None:
            i = tok_id[tk] = len(toks)
            toks.append(tk)
        return i

    pids = {}        # (scenario, speed) -> token ids of the pool's predictions, in pool order
    memo = {}
    values = array("i")
    for t in trials:
        oid = intern(obs_tokens(kit, t["ev"], variant))
        key = (t["scenario"], t["speed"])
        if key not in pids:
            pids[key] = [intern(pred_tokens(pred, p, t["scenario"], t["speed"], variant))
                         for p in pools[t["scenario"]]]
        for pid in pids[key]:
            mk = (oid, pid)
            d = memo.get(mk)
            if d is None:
                d = cs._distance(toks[oid], toks[pid], "none")
                if d != math.floor(d) or d < 0 or d > 2 ** 31 - 1:
                    raise ValueError("a distance is not a non-negative integer (%r)" % d)
                d = int(d)
                memo[mk] = d
            values.append(d)
    return name, values, len(memo)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--trials", required=True)
    ap.add_argument("--prepare", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--processes", type=int, default=4)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    prep, _ = kitload.read_json(a.prepare)
    names = [n for n, v in cfg["variants"].items() if v["attacker"] == "S"]
    os.makedirs(a.out_dir, exist_ok=True)
    trials_path = os.path.abspath(a.trials)
    out = {}
    with Pool(a.processes, initializer=kitload.guarded_init,
              initargs=(_worker_init, trials_path, prep["trials_json_sha256"])) as pool:
        for name, values, n_pairs in pool.imap_unordered(compute_variant, names):
            if sys.byteorder != "little":
                values.byteswap()
            data = values.tobytes()
            path = os.path.join(a.out_dir, "%s.bin" % name)
            tmp = path + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            out[name] = {"sha256": kitload.sha256_bytes(data), "n_values": len(values), "n_distinct_pairs": n_pairs}
            print("  %s: %d values, %d distinct token pairs" % (name, len(values), n_pairs), flush=True)
    _worker_init(trials_path, prep["trials_json_sha256"])
    pools = _W["pools"]
    summary = {"format": FORMAT, "variants": out, "trials_json_sha256": prep["trials_json_sha256"],
               "n_trials": len(_W["trials"]), "pools": dict(
                   (s, {"n": len(pools[s]), "phrase_ids_sha256": kitload.sha256_bytes(
                       "\n".join(p["phrase_id"] for p in pools[s]).encode("utf-8"))}) for s in sorted(pools)),
               "attacker_seed": cfg["attacker_seed"], "provenance": provenance(cfg)}
    kitload.write_json(a.summary, summary)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except kitload.CheckError as e:
        print("!! %s" % e, file=sys.stderr)
        sys.exit(1)
