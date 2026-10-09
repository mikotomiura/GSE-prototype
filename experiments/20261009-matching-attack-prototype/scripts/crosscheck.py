"""Compare the length sequence synthesised from each phrase's text with the one counted from the record
(design.md section 4; goal 1). Computed before any attack.

  crosscheck.py --trials raw/trials.json --prepare results/prepare.json --out results/crosscheck.json

Record side: the trial's presses cut at the boundary categories (enter, sentence_punctuation); each segment counts
text keys minus BackSpace; what follows the last boundary is an open segment (it would join the next trial's
segment in a continuous record).
Synthesised side: the previous task's procedure (SudachiPy reading, B0 cuts at the reading-point and period,
the romaji table) applied to the phrase's text, the last segment closed by the commit Enter.
Each trial gets every cause flag that applies, from the plan and the text alone (never from the record):
procedure (the scenario departs from "type the reading, commit with Enter"), comma (the text holds a
reading-point the executor did not type), reading (the previous procedure's reading differs from the corpus
reading the executor typed, or is invalid), synthetic (an S12 kana string that is not in the corpus).
A trial with no flag whose sequences differ is unexplained and listed by its trial id.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402

COMMA_IN_TEXT = frozenset("、，,")


def record_segments(cats, counted, minus, bounds):
    """([closed segment counts], open count or None). A segment is closed by a boundary press; the presses after
    the last boundary form the open segment (None when the trial ends with a boundary)."""
    closed = []
    cur = 0
    started = False
    for c in cats:
        if c in bounds:
            closed.append(cur)
            cur = 0
            started = False
            continue
        started = True
        if c in counted:
            cur += 1
        elif c in minus:
            cur -= 1
    return closed, (cur if started else None)


def synthesise(text, tok, bs):
    """The previous task's B0 segments of one phrase text: ([key counts], [unit strings], all valid)."""
    out, _ = bs.segments_of_work([text], tok)
    segs = out["B0"]
    return [s[0] for s in segs], [s[1] for s in segs], all(s[3] for s in segs)


def classify(trial, phrase, syn_units, syn_valid, cfg):
    flags = []
    if trial["scenario"] in cfg["procedure_scenarios"]:
        flags.append("procedure")
    if phrase is None:
        flags.append("synthetic")
        return flags
    if any(ch in COMMA_IN_TEXT for ch in phrase["text"]):
        flags.append("comma")
    if not syn_valid or "".join(syn_units) != phrase["reading"]:
        flags.append("reading")
    return flags


def summarise_deltas(deltas):
    hist = {}
    for d in deltas:
        hist[str(d)] = hist.get(str(d), 0) + 1
    if not deltas:
        return {"n": 0}
    return {"n": len(deltas), "mean": sum(deltas) / len(deltas), "min": min(deltas), "max": max(deltas),
            "hist": hist}


def run(trials, corpus, cfg, kit, tok):
    bs, rt, romaji = kit.build_segments, kit.romaji_table, kit.romaji
    by_id = dict((p["phrase_id"], p) for p in corpus)
    counted = frozenset(cfg["counted_categories"])
    minus = frozenset(cfg["minus_categories"])
    bounds = frozenset(cfg["boundary_categories"])
    syn_cache = {}
    per_sc = {}
    per_cause = {}
    unexplained = []
    table_mismatch = 0
    n_reading_differs = 0
    for t in trials:
        cats = [c for _, c in t["ev"]]
        closed, open_ = record_segments(cats, counted, minus, bounds)
        rec_total = sum(closed) + (open_ or 0)
        phrase = by_id.get(t["phrase_id"]) if t["in_corpus"] else None
        if phrase is not None:
            if phrase["phrase_id"] not in syn_cache:
                syn_cache[phrase["phrase_id"]] = synthesise(phrase["text"], tok, bs)
                if rt.count_keys(phrase["reading"]) != len(romaji.to_keys(phrase["reading"])):
                    table_mismatch += 1
            syn, syn_units, syn_valid = syn_cache[phrase["phrase_id"]]
        else:
            syn, syn_units, syn_valid = None, None, False
        flags = classify(t, phrase, syn_units, syn_valid, cfg)
        if phrase is not None and "reading" in flags:
            n_reading_differs += 1
        if syn is not None and syn_valid:
            seq_equal = closed == syn and open_ is None
            total_equal = rec_total == sum(syn)
            delta = rec_total - sum(syn)
        else:
            seq_equal = total_equal = None
            delta = None
        sc = per_sc.setdefault(t["scenario"], {"n": 0, "n_compared": 0, "seq_equal": 0, "total_equal": 0,
                                                "deltas": [], "open_segment": 0, "n_closed_segments": {},
                                                "flags": {}})
        sc["n"] += 1
        if open_ is not None:
            sc["open_segment"] += 1
        key = str(len(closed))
        sc["n_closed_segments"][key] = sc["n_closed_segments"].get(key, 0) + 1
        for f in flags:
            sc["flags"][f] = sc["flags"].get(f, 0) + 1
        if seq_equal is not None:
            sc["n_compared"] += 1
            sc["seq_equal"] += int(seq_equal)
            sc["total_equal"] += int(total_equal)
            sc["deltas"].append(delta)
        cause = "+".join(flags) if flags else "none"
        pc = per_cause.setdefault(cause, {"n": 0, "n_compared": 0, "seq_equal": 0, "total_equal": 0, "deltas": []})
        pc["n"] += 1
        if seq_equal is not None:
            pc["n_compared"] += 1
            pc["seq_equal"] += int(seq_equal)
            pc["total_equal"] += int(total_equal)
            pc["deltas"].append(delta)
        if not flags and seq_equal is not True:
            unexplained.append(t["trial_id"])
    for d in list(per_sc.values()) + list(per_cause.values()):
        d["delta"] = summarise_deltas(d.pop("deltas"))
    return {"by_scenario": per_sc, "by_cause": per_cause, "unexplained_trial_ids": unexplained,
            "n_unexplained": len(unexplained), "n_trials": len(trials),
            "n_phrases_synthesised": len(syn_cache),
            "n_trials_reading_differs": n_reading_differs,
            "n_phrases_table_mismatch": table_mismatch}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--trials", required=True)
    ap.add_argument("--prepare", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg, prior=True)
    corpus, _, _ = kitload.load_inputs(cfg, kit)
    prep, _ = kitload.read_json(a.prepare)
    data, _ = kitload.read_json(a.trials, prep["trials_json_sha256"])
    tok = kit.build_segments.Tokenizer(40000)
    res = run(data["trials"], corpus, cfg, kit, tok)
    res["format"] = "matching-attack-crosscheck/1"
    res["alignment"] = prep["alignment"]
    res["n_scored_trials_differing_from_plan"] = prep["n_scored_trials_differing_from_plan"]
    kitload.write_json(a.out, res)
    print("unexplained mismatches: %d of %d trials" % (res["n_unexplained"], res["n_trials"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except kitload.CheckError as e:
        print("!! %s" % e, file=sys.stderr)
        sys.exit(1)
