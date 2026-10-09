"""Assign the observed presses to the planned trials and write one record per trial (design.md section 3).

  prepare.py --out raw/trials.json --summary results/prepare.json

The observation is read with the IME paper's read_obs and assigned to the plan with segment_by_plan
(markers_in_obs, as in its section 6.8); a block whose presses differ from the plan is not scored. Each scored
trial keeps its presses as (time, category), its key count c (alphabetic + numeric + punctuation presses minus
backspace presses) and its typed reading, taken from the plan row (generate_plan.typed_reading).

raw/trials.json holds the category sequence of every trial and stays out of git; results/prepare.json holds only
counts and the SHA-256 of raw/trials.json, which the later steps check before they read it.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402

FORMAT = "matching-attack-trials/1"


def key_count(cats, counted, minus):
    """Text keys minus BackSpace (design.md section 3)."""
    return sum(1 for c in cats if c in counted) - sum(1 for c in cats if c in minus)


def build(cfg, kit):
    cs, gp = kit.closed_set, kit.generate_plan
    corpus, recipes, pcfg = kitload.load_inputs(cfg, kit)
    by_id = dict((p["phrase_id"], p) for p in corpus)
    plan = cs.read_plan(kitload.input_path(cfg, "plan"))
    for what, name in (("recipes", "recipes"), ("config", "plan_config")):
        if plan[0]["%s_sha256" % what] != cfg["inputs"][name]["sha256"]:
            raise kitload.CheckError("the plan was built from a different %s file" % what)
    events, n_shadow, obs_os = cs.read_obs(kitload.input_path(cfg, "obs"))
    if obs_os != cfg["os"]:
        raise kitload.CheckError("the observation's os is %s, not %s" % (obs_os, cfg["os"]))
    seg, alignment = cs.segment_by_plan(events, plan, obs_os, markers_in_obs=cfg["markers_in_obs"], tag="s0-")
    rows = dict((r["trial_id"], r) for r in plan[1:] if r["kind"] == "trial")
    counted = frozenset(cfg["counted_categories"])
    minus = frozenset(cfg["minus_categories"])
    out = []
    n_plan_mismatch = 0
    for s in seg:
        tid = s["trial_id"][len("s0-"):]
        row = rows[tid]
        cats = [c for _, c in s["observed"]]
        if cats != cs.expected_categories(row):
            n_plan_mismatch += 1
        typed = gp.typed_reading(row, recipes)
        in_corpus = row["phrase_id"] in by_id
        if in_corpus and row["scenario"] not in cfg["skip_scenarios"]:
            probe = cs._typed_reading(recipes, pcfg, by_id[row["phrase_id"]], row["scenario"], obs_os)
            if probe != typed:
                raise kitload.CheckError("trial %s: the typed reading of the plan row and of the phrase differ" % tid)
        out.append({"trial_id": tid, "block_id": row["block_id"], "scenario": row["scenario"], "speed": row["speed"],
                    "phrase_id": row["phrase_id"], "in_corpus": in_corpus, "typed": typed,
                    "ev": [[t, c] for t, c in s["observed"]], "c": key_count(cats, counted, minus)})
    return out, alignment, n_shadow, n_plan_mismatch


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", required=True)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg)
    trials, alignment, n_shadow, n_plan_mismatch = build(cfg, kit)
    if n_plan_mismatch:
        raise kitload.CheckError("%d scored trials differ from the plan (segment_by_plan should never score them)"
                                 % n_plan_mismatch)
    sha = kitload.write_json(a.out, {"format": FORMAT, "trials": trials})
    by_sc = {}
    for t in trials:
        by_sc[t["scenario"]] = by_sc.get(t["scenario"], 0) + 1
    summary = {"format": "matching-attack-prepare/1", "alignment": alignment, "n_trials_scored": len(trials),
               "n_scored_by_scenario": by_sc, "n_ime_shadow_rows_unused": n_shadow,
               "n_scored_trials_differing_from_plan": n_plan_mismatch,
               "n_presses_scored": sum(len(t["ev"]) for t in trials),
               "trials_json_sha256": sha,
               "inputs": dict((k, v.get("sha256")) for k, v in cfg["inputs"].items())}
    kitload.write_json(a.summary, summary)
    print("trials scored: %d of %d (blocks unscored: %d)" % (len(trials), alignment["n_trials"],
                                                               alignment["n_blocks_unscored"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except kitload.CheckError as e:
        print("!! %s" % e, file=sys.stderr)
        sys.exit(1)
