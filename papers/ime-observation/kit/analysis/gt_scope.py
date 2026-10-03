#!/usr/bin/env python3
# kit: selftest
"""The long trials of a Windows cell, taken from the ground-truth sessions, in the form of the prediction that
match.py reads for its scopes (Python standard library only).

  gt_scope.py --selftest

Why this exists (deviation D3, experiment/deviations.md). The scopes of questions 1 to 3 set aside the trials whose
session the observer is specified to cut off at 20 seconds (section 6.4 of the pre-registration). On macOS the
observer infers sessions from key presses, and the prediction (spec_predict.py) marks these trials from what was sent.
On Windows the observer reads the input method's own composition events, so no prediction from the key presses
applies, and without one the frozen pipeline had the scope all_trials only. For a Windows cell a trial is long when a
ground-truth session assigned to it lasts at least limit_ms (end minus start on the wall clock, the definition of the
truncation check in l1.py); the observer's cut-off is the same 20,000 ms on both systems.

as_prediction_bytes() renders these trials as a prediction object (format spec_predict/2) so that match.evaluate()
builds under_limit and over_limit from them unchanged. Only the long flags carry information: carried_out,
received_carry and closing_key_in_reading are false and n_started counts the trial's ground-truth sessions; the
pipeline does not report the prediction's layers for such a cell.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import match  # noqa: E402

SOURCE = "ground_truth_duration"


def long_trials(sessions, limit_ms):
    """Trial ids with a ground-truth session (any definition: the list "all") of at least limit_ms."""
    out = set()
    for s in sessions["definitions"]["all"]:
        if s.get("trial_id") is not None and s.get("end_wall_ms") is not None \
                and s["end_wall_ms"] - s["start_wall_ms"] >= limit_ms:
            out.add(s["trial_id"])
    return out


def as_prediction_bytes(sessions, oracle_bytes, plan_bytes, limit_ms):
    plan = match.parse_plan_strata(plan_bytes)
    longs = long_trials(sessions, limit_ms)
    started = {}
    for s in sessions["definitions"]["all"]:
        if s.get("trial_id") is not None:
            started[s["trial_id"]] = started.get(s["trial_id"], 0) + 1
    by = dict((tid, {"long": tid in longs, "carried_out": False, "received_carry": False,
                     "closing_key_in_reading": False, "n_started": started.get(tid, 0)})
              for tid in sorted(plan["trials"]))
    obj = {"format": match.PREDICTION_FORMAT, "source": SOURCE, "limit_ms": limit_ms,
           "inputs_sha256": {"oracle": hashlib.sha256(oracle_bytes).hexdigest(), "plan": plan["sha256"]},
           "trials": {"n_long": len(longs & set(by)), "by_trial": by}}
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def selftest():
    fails = []

    def check(name, ok):
        print("  %s %s" % ("ok  " if ok else "FAIL", name))
        if not ok:
            fails.append(name)

    def sess(tid, a, b):
        return {"trial_id": tid, "start_wall_ms": a, "end_wall_ms": b}

    sessions = {"definitions": {"all": [sess("t00001", 0, 19999), sess("t00002", 0, 20000), sess("t00003", 5, None),
                                        sess(None, 0, 90000), sess("t00004", 0, 1000), sess("t00004", 2000, 30000)]}}
    got = long_trials(sessions, 20000)
    check("a session of exactly limit_ms is long, one ms less is not", "t00002" in got and "t00001" not in got)
    check("an open session and a session of no trial make no trial long", "t00003" not in got and None not in got)
    check("one long session of several makes its trial long", got == {"t00002", "t00004"})
    plan = b"\n".join(json.dumps(x).encode() for x in [
        {"kind": "header", "format": "plan/1", "os": "windows"},
        {"kind": "block", "block_id": 0, "speed": "slow"},
        {"kind": "trial", "trial_id": "t00001", "block_id": 0, "scenario": "S1", "speed": "slow"},
        {"kind": "trial", "trial_id": "t00002", "block_id": 0, "scenario": "S13", "speed": "slow"},
        {"kind": "trial", "trial_id": "t00004", "block_id": 0, "scenario": "S1", "speed": "slow"},
        {"kind": "trial", "trial_id": "t00005", "block_id": 0, "scenario": "S5", "speed": "slow"}]) + b"\n"
    try:
        pb = as_prediction_bytes(sessions, b"oracle", plan, 20000)
        parsed = match.parse_prediction(pb, hashlib.sha256(b"oracle").hexdigest(), match.parse_plan_strata(plan)["sha256"])
        check("match.py reads the rendered object, and its long trials are the ground truth's",
              parsed["long"] == {"t00002", "t00004"})
        obj = json.loads(pb)
        check("every planned trial is listed, with only the long flag set",
              sorted(obj["trials"]["by_trial"]) == ["t00001", "t00002", "t00004", "t00005"]
              and not any(d[k] for d in obj["trials"]["by_trial"].values()
                          for k in ("carried_out", "received_carry", "closing_key_in_reading"))
              and obj["trials"]["by_trial"]["t00004"]["n_started"] == 2 and obj["source"] == SOURCE)
        try:
            match.parse_prediction(pb, hashlib.sha256(b"other").hexdigest(), match.parse_plan_strata(plan)["sha256"])
            check("an object made from another oracle is refused by match.py", False)
        except match.InputError:
            check("an object made from another oracle is refused by match.py", True)
    except Exception as e:  # a shape the plan parser or match.py does not accept
        check("the rendered object is accepted (%s: %s)" % (type(e).__name__, e), False)
    print("selftest %s (%d failed)" % ("OK" if not fails else "FAILED", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    sys.stderr.write(__doc__)
    sys.exit(2)
