"""Load what the attacks need, after checking every SHA-256 (design.md sections 5 and 6).

Returns a dict:
  trials     the scored trials outside the skipped scenarios, in plan order (records of raw/trials.json)
  pools      scenario -> the phrases a decoy of that scenario is drawn from (closed_set._scenario_pool of the
             corpus without duplicate readings), in a fixed order
  typed      scenario -> [typed reading of each pool phrase under the scenario] (closed_set._typed_reading)
  R          scenario -> [standard key count of each pool phrase's whole reading] (len(romaji.to_keys))
  true_j     [pool index of each trial's phrase (the phrase with the same reading)]
  dist       variant -> [one array of distances per trial, over the trial's pool] (only when requested)
"""
import os
import sys
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402
from distances import scenario_pools, used_trials  # noqa: E402


def load(cfg, kit, trials_path, prepare_path, dist_dir=None, dist_summary_path=None, variants=()):
    corpus, recipes, pcfg = kitload.load_inputs(cfg, kit)
    cs, romaji = kit.closed_set, kit.romaji
    prep, _ = kitload.read_json(prepare_path)
    data, _ = kitload.read_json(trials_path, prep["trials_json_sha256"])
    trials = used_trials(data["trials"], cfg)
    _, pools = scenario_pools(kit, recipes, cfg["os"], corpus, set(t["scenario"] for t in trials))
    typed, R, index_of_reading = {}, {}, {}
    for s, pool in pools.items():
        typed[s] = [cs._typed_reading(recipes, pcfg, p, s, cfg["os"]) for p in pool]
        R[s] = array("i", [len(romaji.to_keys(p["reading"])) for p in pool])
        index_of_reading[s] = dict((p["reading"], j) for j, p in enumerate(pool))
    by_id = dict((p["phrase_id"], p) for p in corpus)
    true_j = []
    for t in trials:
        j = index_of_reading[t["scenario"]].get(by_id[t["phrase_id"]]["reading"])
        if j is None:
            raise kitload.CheckError("trial %s: its phrase is not in its scenario's pool" % t["trial_id"])
        if typed[t["scenario"]][j] != t["typed"]:
            raise kitload.CheckError("trial %s: the pool phrase types a different reading" % t["trial_id"])
        true_j.append(j)
    out = {"trials": trials, "pools": pools, "typed": typed, "R": R, "true_j": true_j, "dist": {},
           "prepare": prep, "recipes": recipes, "pcfg": pcfg, "corpus": corpus}
    if variants:
        summ, _ = kitload.read_json(dist_summary_path)
        if summ["trials_json_sha256"] != prep["trials_json_sha256"]:
            raise kitload.CheckError("the distances were computed from another raw/trials.json")
        if summ["attacker_seed"] != cfg["attacker_seed"]:
            raise kitload.CheckError("the distances were computed with another attacker seed")
        for s, pool in pools.items():
            want = summ["pools"][s]
            got = kitload.sha256_bytes("\n".join(p["phrase_id"] for p in pool).encode("utf-8"))
            if want["n"] != len(pool) or want["phrase_ids_sha256"] != got:
                raise kitload.CheckError("the pool of %s differs from the one the distances were computed on" % s)
        for name in variants:
            path = os.path.join(dist_dir, "%s.bin" % name)
            with open(path, "rb") as f:
                raw = f.read()
            if kitload.sha256_bytes(raw) != summ["variants"][name]["sha256"]:
                raise kitload.CheckError("SHA-256 of %s differs from results/distances.json" % path)
            vals = array("i")
            vals.frombytes(raw)
            if sys.byteorder != "little":
                vals.byteswap()
            per = []
            pos = 0
            for t in trials:
                n = len(pools[t["scenario"]])
                per.append(vals[pos:pos + n])
                pos += n
            if pos != len(vals):
                raise kitload.CheckError("%s holds %d values, not the %d the trials need" % (path, len(vals), pos))
            out["dist"][name] = per
    return out
