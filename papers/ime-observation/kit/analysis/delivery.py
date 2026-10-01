#!/usr/bin/env python3
# kit: selftest
"""Delivery report: how faithfully scripted key presses were delivered, press by press, in a method-validation
run (Python standard library only). Descriptive only: it counts and summarises, and it makes no pass/fail
decision.

  delivery.py --plan PLAN --oracle ORACLE --obs OBS --gt GT --out OUT.json [--pre-ms N] [--tail-ms N]
  delivery.py --selftest      positive and negative controls (fast)

Inputs: the plan (plan/1), the oracle (oracle/1; one row per press as sent by the runner), the observation log
(obs/1) and the reference log (gt/1). From the observation log only the rows whose type is "key" are read (fields
t and press); every other row is skipped without its other fields being inspected, so this tool does not depend on
the session rows. From the reference log only the rows whose ev is "key_down", "focus_out" or "focus_in" are read
(field t_wall_ms); the key code a key_down carries is not interpreted. A row that does not parse as JSON, or a row that is not an object, is refused.

Definitions.
  * A press is an oracle "sent" row with down = true whose key is not a pseudo-key (PSEUDO_KEYS: focus_away,
    focus_back, mouse_click). Pseudo-keys are never real keys and are ignored everywhere. MODE_KEYS (ime_on,
    ime_off) are input-mode keys, which the observation side does not record by design; every reach figure is
    therefore given twice, over all presses and over the presses excluding the mode keys ("excluding_mode_keys").
  * Send lateness of a press = (sent.t_mono_ns - (trial_begin.t_mono_ns + steps[step].at_ms * 1e6)) / 1e6, in
    milliseconds. Positive means the press was sent later than scheduled. steps[step] is the plan step indexed by
    the sent row's step field.
  * Reach, for each side (observation key rows with press = true; reference key_down rows), per trial: the number
    of presses sent against the number of rows received. A trial's interval runs from the trial_begin wall time
    minus pre_ms (default 20) to the trial_end wall time plus tail_ms (default 300). The tail end is also cut at the
    next oracle row (reset, block_begin, marker or the next trial_begin), whichever comes first, so that a marker
    press at the head of the next block is not counted into the last trial of the previous block. A trial without
    both a trial_begin and a trial_end has no interval and is counted as incomplete. Reported: sent_presses,
    reached = sum over trials of min(sent, received), reach_rate = reached / sent_presses, excess_rows = sum of
    max(0, received - sent), rows_outside_trials (rows that fall inside no interval), trials_with_loss
    (received < sent) and trials_with_excess (received > sent).
  * Segments, per side. The block_begin rows of the oracle divide the time of the log into half-open segments:
    one from the start up to the first block_begin (block_id null), then, for each block, one from its own
    block_begin time (included) to the next block_begin time (excluded), the last one to the end; a log with no
    block_begin is one segment with block_id null. For each segment, in time order and also when it holds no row:
    n_rows = the rows that fall in it, inside a trial's interval or outside every one; n_reached = the sum, over
    the measured trials whose trial_begin wall time lies in the segment, of min(sent, the number of rows assigned
    to the trial (as for reach) that lie in the segment); n_unexplained = n_rows - n_reached (never negative);
    n_marker_presses = the length of the marker array the plan gives the block (0 for the first segment and for
    a block with no marker); n_unexplained_beyond_markers = max(0, n_unexplained - n_marker_presses).
    n_segments and max_unexplained_beyond_markers (the largest of the latter over the segments) head the list.
    A press that the runner makes outside the oracle, such as the key that selects the input method before a
    block, has no oracle row; wherever it falls, inside the interval of the last trial of the segment or outside
    every interval, it adds one to n_unexplained of the same segment, because min(sent, received) of a trial is
    capped at sent; where it falls changes the count only when a press of that trial was lost (the blind spot
    below). Blind spot: when, in one trial, a
    sent press does not arrive and a press from outside arrives in its place, the two cancel in n_reached and
    n_unexplained does not change; a replaced press is not detected. This tool only counts: the bounds on
    n_unexplained and the decision on a run belong to the pre-registration (section 3.4) and to pipeline.py.
  * Delay and interval error, per side, only in trials in which the number of received rows equals the number of
    presses excluding the mode keys (and is at least one); such a trial is "paired" and its i-th press is matched
    with its i-th row in time order (presses in the order of the oracle file). delay_ms = row wall time - sent
    t_wall_ms (positive: the row is later than the send). interval_error_ms = (row[i+1] - row[i]) -
    (sent[i+1] - sent[i]) over consecutive pairs of one trial. n_trials_paired counts the paired trials and
    n_trials_not_paired the trials with a different count; a trial with no press and no row belongs to neither.
  * Summary = {n, mean, min, p05, median, p95, max}, all null when n = 0. Percentiles use linear interpolation
    between order statistics at position p * (n - 1) (the "type 7" rule); the median is the p = 0.5 case.
    Values are rounded to six decimals.
  * Focus losses of the reference input field: a loss interval runs from a focus_out row to the next focus_in row
    (to the end of the log when none follows); a focus_out inside a loss interval already open starts no new one.
    A loss that is not regained therefore covers every later trial, although the reference field no longer
    receives their keys. A loss interval overlaps a trial when it shares at least one millisecond with the
    trial's interval (as defined for reach). Reported: the numbers of focus_out and of focus_in rows, the number
    of loss intervals, the number of loss intervals that overlap no trial interval, the trials that overlap at
    least one loss interval (trials_with_focus_loss, sorted) and per stratum (scenario, speed) the number of
    measured trials and of trials with a focus loss. A planned switch to another application (scenario S15) is
    not counted: an S15 trial is left out of the list when every loss interval it overlaps begins and ends inside
    its own interval (the focus came back within the trial); any other loss, including an S15 switch that does
    not return inside the trial, is listed together with every trial it reaches.

Refused (exit 2): a block row of the plan whose block_id is repeated or whose marker is not an array of strings; a
block_begin whose block_id is not in the plan or that appears twice for one block; a plan whose SHA-256 differs
from the oracle header's plan_sha256; a sent row whose trial or step is absent from the plan, or whose key or down
flag disagrees with the plan step; a sent row of a trial with no trial_begin; a duplicated trial_begin or
trial_end; and malformed input. Error messages carry only row numbers
and field names, never a value read from a log.

The output holds no path and identical input yields identical output bytes (sorted keys, LF, UTF-8, no BOM). The
SHA-256 of each input is recorded under "inputs_sha256".
Exit status: 0 written / 1 selftest failure / 2 usage error or invalid input.
"""
import argparse
import bisect
import hashlib
import json
import os
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

FORMAT = "delivery/1"
PSEUDO_KEYS = ("focus_away", "focus_back", "mouse_click")
MODE_KEYS = ("ime_on", "ime_off")
SPEEDS = ("slow", "mid", "fast")
CUT_KINDS = ("reset", "block_begin", "marker")


class InputError(Exception):
    """Input is unreadable, or does not match the contract."""


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _no_dup_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("a row has the same key twice")
        out[k] = v
    return out


def _lines(data, what):
    """Return [(line number, text)] of the non-empty lines of a UTF-8 byte string."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("%s: not valid UTF-8" % what)
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        line = line.strip()
        if line:
            out.append((n, line))
    return out


def _loads(line, where, strict):
    try:
        if strict:
            return json.loads(line, object_pairs_hook=_no_dup_pairs)
        return json.loads(line)
    except ValueError:
        raise InputError("%s: the line does not parse as JSON" % where)


# --- readers ---------------------------------------------------------------------------------------------------

def read_plan(data):
    """Return (trials, markers) from a plan/1 byte string. trials is {trial_id: {"scenario", "speed", "steps":
    [(key, at_ms, down)]}}; markers is {block_id: the number of marker presses the plan puts at the head of the
    block} (0 when the block row has no marker)."""
    lines = _lines(data, "plan")
    if not lines:
        raise InputError("plan: empty file")
    hdr = _loads(lines[0][1], "plan:%d" % lines[0][0], True)
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "plan/1":
        raise InputError("plan: line 1 is not a plan/1 header")
    trials = {}
    markers = {}
    for n, raw in lines[1:]:
        where = "plan:%d" % n
        row = _loads(raw, where, True)
        if not isinstance(row, dict) or not isinstance(row.get("kind"), str):
            raise InputError("%s: missing kind" % where)
        if row["kind"] == "block":
            bid = row.get("block_id")
            if not (_is_int(bid) or isinstance(bid, str)) or bid in markers:
                raise InputError("%s: block_id is missing, not an integer or a string, or repeated" % where)
            marker = row.get("marker", [])
            if not isinstance(marker, list) or not all(isinstance(k, str) for k in marker):
                raise InputError("%s: marker is not an array of strings" % where)
            markers[bid] = len(marker)
            continue
        if row["kind"] != "trial":
            continue
        tid = row.get("trial_id")
        if not isinstance(tid, str) or tid in trials:
            raise InputError("%s: trial_id is missing, not a string, or repeated" % where)
        if row.get("speed") not in SPEEDS:
            raise InputError("%s: speed is not one of the allowed names" % where)
        if not isinstance(row.get("scenario"), str):
            raise InputError("%s: scenario is missing or not a string" % where)
        steps = row.get("steps")
        if not isinstance(steps, list):
            raise InputError("%s: steps is not an array" % where)
        parsed = []
        for st in steps:
            if (not isinstance(st, dict) or not isinstance(st.get("key"), str) or not _is_int(st.get("at_ms"))
                    or not isinstance(st.get("down"), bool)):
                raise InputError("%s: a step is malformed (key, at_ms, down)" % where)
            parsed.append((st["key"], st["at_ms"], st["down"]))
        trials[tid] = {"scenario": row["scenario"], "speed": row["speed"], "steps": parsed}
    return trials, markers


def read_oracle(data, plan, plan_sha256, blocks):
    """Return (trials, cuts, begins). trials is a list, in file order, of {trial_id, begin_wall, begin_mono,
    end_wall, sent: [{key, step, wall, mono, down}]}; cuts is the sorted list of wall times of the oracle rows that
    end a trial's interval (reset / block_begin / marker / trial_begin); begins is the list of (wall time,
    block_id) of the block_begin rows, sorted by time. blocks is the set of the block_ids of the plan. The sent
    rows are checked against the plan, and a block_begin against the blocks."""
    lines = _lines(data, "oracle")
    if not lines:
        raise InputError("oracle: empty file")
    hdr = _loads(lines[0][1], "oracle:%d" % lines[0][0], True)
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "oracle/1":
        raise InputError("oracle: line 1 is not an oracle/1 header")
    if hdr.get("plan_sha256") != plan_sha256:
        raise InputError("oracle: plan_sha256 in the header does not match the plan given")
    trials = {}
    order = []
    cuts = []
    begins = []
    for n, raw in lines[1:]:
        where = "oracle:%d" % n
        row = _loads(raw, where, True)
        if not isinstance(row, dict) or not isinstance(row.get("kind"), str):
            raise InputError("%s: missing kind" % where)
        kind = row["kind"]
        if kind in CUT_KINDS:
            if not _is_int(row.get("t_wall_ms")):
                raise InputError("%s: t_wall_ms is missing or not an integer" % where)
            cuts.append(row["t_wall_ms"])
            if kind == "block_begin":
                bid = row.get("block_id")
                if not (_is_int(bid) or isinstance(bid, str)) or bid not in blocks:
                    raise InputError("%s: block_id of a block_begin is missing or not in the plan" % where)
                if any(b == bid for _t, b in begins):
                    raise InputError("%s: block_begin appears twice for one block" % where)
                begins.append((row["t_wall_ms"], bid))
            continue
        if kind not in ("trial_begin", "trial_end", "sent"):
            continue
        tid = row.get("trial_id")
        if not isinstance(tid, str) or tid not in plan:
            raise InputError("%s: trial_id is missing or not in the plan" % where)
        if not _is_int(row.get("t_wall_ms")) or not _is_int(row.get("t_mono_ns")):
            raise InputError("%s: t_wall_ms or t_mono_ns is missing or not an integer" % where)
        if kind == "trial_begin":
            if tid in trials:
                raise InputError("%s: trial_begin appears twice for one trial" % where)
            trials[tid] = {"trial_id": tid, "begin_wall": row["t_wall_ms"], "begin_mono": row["t_mono_ns"],
                           "end_wall": None, "sent": []}
            order.append(tid)
            cuts.append(row["t_wall_ms"])
            continue
        if tid not in trials:
            raise InputError("%s: a %s row comes before the trial_begin of its trial" % (where, kind))
        t = trials[tid]
        if kind == "trial_end":
            if t["end_wall"] is not None:
                raise InputError("%s: trial_end appears twice for one trial" % where)
            t["end_wall"] = row["t_wall_ms"]
            continue
        step, key, down = row.get("step"), row.get("key"), row.get("down")
        steps = plan[tid]["steps"]
        if not _is_int(step) or step < 0 or step >= len(steps):
            raise InputError("%s: step has no counterpart in the plan" % where)
        if key != steps[step][0] or down != steps[step][2]:
            raise InputError("%s: key or down disagrees with the plan step" % where)
        t["sent"].append({"key": key, "step": step, "down": down, "wall": row["t_wall_ms"],
                          "mono": row["t_mono_ns"]})
    cuts.sort()
    begins.sort(key=lambda b: b[0])
    return [trials[k] for k in order], cuts, begins


def read_obs_presses(data):
    """Return the sorted wall times (ms) of the observation rows of type "key" with press = true. Rows of any
    other type are skipped without reading any field of theirs."""
    out = []
    for n, raw in _lines(data, "obs"):
        where = "obs:%d" % n
        row = _loads(raw, where, False)
        if not isinstance(row, dict):
            raise InputError("%s: the row is not an object" % where)
        if row.get("type") != "key":
            continue
        if not _is_int(row.get("t")) or not isinstance(row.get("press"), bool):
            raise InputError("%s: a key row lacks an integer t or a boolean press" % where)
        if row["press"]:
            out.append(row["t"])
    out.sort()
    return out


def read_gt_events(data, ev):
    """Return the sorted wall times (ms) of the reference rows whose ev is the one given; nothing else is read."""
    out = []
    for n, raw in _lines(data, "gt"):
        where = "gt:%d" % n
        row = _loads(raw, where, False)
        if not isinstance(row, dict):
            raise InputError("%s: the row is not an object" % where)
        if row.get("kind") != "ev" or row.get("ev") != ev:
            continue
        if not _is_int(row.get("t_wall_ms")):
            raise InputError("%s: a %s row lacks an integer t_wall_ms" % (where, ev))
        out.append(row["t_wall_ms"])
    out.sort()
    return out


def read_gt_key_downs(data):
    """Return the sorted wall times (ms) of the reference rows whose ev is "key_down"."""
    return read_gt_events(data, "key_down")


def _loss_intervals(outs, ins):
    """Return [(begin, end)] of the focus loss intervals: from a focus_out to the next focus_in, or to None (the
    end of the log) when none follows. A focus_out while a loss is open and a focus_in while none is open add
    nothing. On equal times a focus_out is taken before a focus_in."""
    events = sorted([(t, 0) for t in outs] + [(t, 1) for t in ins])
    out, begin = [], None
    for t, kind in events:
        if kind == 0 and begin is None:
            begin = t
        elif kind == 1 and begin is not None:
            out.append((begin, t))
            begin = None
    if begin is not None:
        out.append((begin, None))
    return out


def _focus_losses(done, plan, outs, ins, starts, ends):
    losses = _loss_intervals(outs, ins)
    def overlap(loss, i):
        return loss[0] <= ends[i] and (loss[1] is None or loss[1] >= starts[i])
    def inside(loss, i):
        return loss[0] >= starts[i] and loss[1] is not None and loss[1] <= ends[i]
    hit = []
    for i, t in enumerate(done):
        mine = [loss for loss in losses if overlap(loss, i)]
        planned = plan[t["trial_id"]]["scenario"] == "S15" and all(inside(loss, i) for loss in mine)
        hit.append(bool(mine) and not planned)
    outside = sum(1 for loss in losses if not any(overlap(loss, i) for i in range(len(done))))
    per = {}
    for t, got in zip(done, hit):
        info = plan[t["trial_id"]]
        c = per.setdefault((info["scenario"], info["speed"]), [0, 0])
        c[0] += 1
        c[1] += 1 if got else 0
    def order(k):
        sc = k[0][1:]
        return (int(sc) if sc.isdigit() else 0, k[0], SPEEDS.index(k[1]))
    return {"n_focus_out": len(outs), "n_focus_in": len(ins), "n_loss_intervals": len(losses),
            "n_loss_intervals_outside_trials": outside, "n_trials_with_focus_loss": sum(1 for g in hit if g),
            "trials_with_focus_loss": sorted(t["trial_id"] for t, got in zip(done, hit) if got),
            "by_stratum": [{"scenario": k[0], "speed": k[1], "n_trials": per[k][0], "n_trials_with_focus_loss": per[k][1]}
                           for k in sorted(per, key=order)]}


# --- computation -----------------------------------------------------------------------------------------------

def _percentile(sorted_vals, p):
    pos = p * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (pos - lo) * (sorted_vals[hi] - sorted_vals[lo])


def summarize(values):
    """{n, mean, min, p05, median, p95, max}; null fields when there is no value (linear-interpolation
    percentiles)."""
    vals = sorted(values)
    if not vals:
        return {"n": 0, "mean": None, "min": None, "p05": None, "median": None, "p95": None, "max": None}
    return {"n": len(vals), "mean": round(sum(vals) / len(vals), 6), "min": round(vals[0], 6),
            "p05": round(_percentile(vals, 0.05), 6), "median": round(_percentile(vals, 0.5), 6),
            "p95": round(_percentile(vals, 0.95), 6), "max": round(vals[-1], 6)}


def _by_speed(pairs):
    """pairs = [(speed, value)] -> {"overall": summary, "by_speed": {speed: summary}}."""
    return {"overall": summarize([v for _, v in pairs]),
            "by_speed": {s: summarize([v for sp, v in pairs if sp == s]) for s in SPEEDS}}


def _presses(trial):
    return [s for s in trial["sent"] if s["down"] and s["key"] not in PSEUDO_KEYS]


def _windows(done, cuts, pre_ms, tail_ms):
    starts = [t["begin_wall"] - pre_ms for t in done]
    ends = []
    for t in done:
        end = t["end_wall"] + tail_ms
        i = bisect.bisect_right(cuts, t["end_wall"])
        if i < len(cuts):
            end = min(end, cuts[i] - 1)
        ends.append(end)
    return starts, ends


def _assign(times, starts, ends):
    """Assign sorted row times to the trial intervals. Return (rows per trial, number outside every interval)."""
    rows = [[] for _ in starts]
    outside = 0
    for ts in times:
        i = bisect.bisect_right(starts, ts) - 1
        if i >= 0 and ts <= ends[i]:
            rows[i].append(ts)
        else:
            outside += 1
    return rows, outside


def _reach(sent_counts, got_rows, outside):
    sent = sum(sent_counts)
    reached = sum(min(s, len(g)) for s, g in zip(sent_counts, got_rows))
    return {
        "sent_presses": sent,
        "reached": reached,
        "reach_rate": round(reached / sent, 6) if sent else None,
        "excess_rows": sum(max(0, len(g) - s) for s, g in zip(sent_counts, got_rows)),
        "rows_outside_trials": outside,
        "trials_with_loss": sum(1 for s, g in zip(sent_counts, got_rows) if len(g) < s),
        "trials_with_excess": sum(1 for s, g in zip(sent_counts, got_rows) if len(g) > s),
    }


def _timing(done, speeds, got_rows):
    delays, errors = [], []
    paired = not_paired = 0
    for t, speed, rows in zip(done, speeds, got_rows):
        sent = [s for s in _presses(t) if s["key"] not in MODE_KEYS]
        if len(sent) != len(rows):
            not_paired += 1
            continue
        if not sent:
            continue
        paired += 1
        for s, r in zip(sent, rows):
            delays.append((speed, r - s["wall"]))
        for i in range(len(sent) - 1):
            errors.append((speed, (rows[i + 1] - rows[i]) - (sent[i + 1]["wall"] - sent[i]["wall"])))
    return {"n_trials_paired": paired, "n_trials_not_paired": not_paired,
            "delay_ms": _by_speed(delays), "interval_error_ms": _by_speed(errors)}


def _segments(done, times, rows, begins, markers):
    """Per segment (see Definitions): the rows that fall in it, those explained by a press that was sent, and the
    rest. begins = [(wall time, block_id)] sorted by time; markers = {block_id: marker presses}."""
    cut_times = [b[0] for b in begins]
    n_rows = [0] * (len(begins) + 1)
    reached = [0] * (len(begins) + 1)
    for ts in times:
        n_rows[bisect.bisect_right(cut_times, ts)] += 1
    for t, got in zip(done, rows):
        seg = bisect.bisect_right(cut_times, t["begin_wall"])
        inside = sum(1 for ts in got if bisect.bisect_right(cut_times, ts) == seg)
        reached[seg] += min(len(_presses(t)), inside)
    by_segment = []
    for i in range(len(begins) + 1):
        bid = begins[i - 1][1] if i else None
        marker = markers[bid] if i else 0
        unexplained = n_rows[i] - reached[i]
        by_segment.append({"block_id": bid, "n_rows": n_rows[i], "n_reached": reached[i],
                           "n_unexplained": unexplained, "n_marker_presses": marker,
                           "n_unexplained_beyond_markers": max(0, unexplained - marker)})
    return {"n_segments": len(by_segment),
            "max_unexplained_beyond_markers": max(b["n_unexplained_beyond_markers"] for b in by_segment),
            "by_segment": by_segment}


def _side(done, speeds, times, starts, ends, begins, markers):
    rows, outside = _assign(times, starts, ends)
    all_counts = [len(_presses(t)) for t in done]
    excl_counts = [len([s for s in _presses(t) if s["key"] not in MODE_KEYS]) for t in done]
    return {"reach": {"all_presses": _reach(all_counts, rows, outside),
                      "excluding_mode_keys": _reach(excl_counts, rows, outside)},
            "timing": _timing(done, speeds, rows),
            "segments": _segments(done, times, rows, begins, markers)}


def evaluate(plan_bytes, oracle_bytes, obs_bytes, gt_bytes, pre_ms=20, tail_ms=300):
    """Compute the delivery report from the four input byte strings. Raises InputError on invalid input."""
    if not _is_int(pre_ms) or not _is_int(tail_ms) or pre_ms < 0 or tail_ms < 0:
        raise InputError("pre_ms and tail_ms must be integers of 0 or greater")
    sha = {"plan": hashlib.sha256(plan_bytes).hexdigest(), "oracle": hashlib.sha256(oracle_bytes).hexdigest(),
           "obs": hashlib.sha256(obs_bytes).hexdigest(), "gt": hashlib.sha256(gt_bytes).hexdigest()}
    plan, markers = read_plan(plan_bytes)
    trials, cuts, begins = read_oracle(oracle_bytes, plan, sha["plan"], markers)
    obs_times = read_obs_presses(obs_bytes)
    gt_times = read_gt_key_downs(gt_bytes)

    lateness = []
    for t in trials:
        steps = plan[t["trial_id"]]["steps"]
        for s in _presses(t):
            sched_ns = t["begin_mono"] + steps[s["step"]][1] * 1000000
            lateness.append((plan[t["trial_id"]]["speed"], (s["mono"] - sched_ns) / 1e6))

    done = sorted((t for t in trials if t["end_wall"] is not None), key=lambda t: t["begin_wall"])
    speeds = [plan[t["trial_id"]]["speed"] for t in done]
    starts, ends = _windows(done, cuts, pre_ms, tail_ms)
    n_all = sum(len(_presses(t)) for t in trials)
    n_excl = sum(len([s for s in _presses(t) if s["key"] not in MODE_KEYS]) for t in trials)
    return {
        "format": FORMAT,
        "params": {"pre_ms": pre_ms, "tail_ms": tail_ms, "pseudo_keys": sorted(PSEUDO_KEYS),
                   "mode_keys": sorted(MODE_KEYS)},
        "inputs_sha256": sha,
        "trials": {"planned": len(plan), "begun": len(trials), "measured": len(done),
                   "incomplete": len(trials) - len(done)},
        "presses": {"all": n_all, "excluding_mode_keys": n_excl},
        "send_lateness_ms": _by_speed(lateness),
        "observation": _side(done, speeds, obs_times, starts, ends, begins, markers),
        "reference": _side(done, speeds, gt_times, starts, ends, begins, markers),
        "reference_focus_loss": _focus_losses(done, plan, read_gt_events(gt_bytes, "focus_out"),
                                              read_gt_events(gt_bytes, "focus_in"), starts, ends),
    }


def render(out):
    """Render the output bytes (LF line endings, UTF-8, no BOM, keys in a fixed sorted order)."""
    return (json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


# --- selftest begin ---
def _jl(rows):
    return "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows).encode("utf-8")


W0 = 1_700_000_000_000
MONO0 = 7_000_000_000
PLAN_STEPS = {
    "t1": ("slow", [("a", 0, True), ("a", 50, False), ("ime_on", 200, True), ("ime_on", 250, False),
                    ("b", 400, True), ("b", 450, False)]),
    "t2": ("fast", [("c", 0, True), ("c", 30, False), ("d", 100, True), ("d", 130, False)]),
    "t3": ("mid", [("focus_away", 0, True), ("focus_away", 10, False), ("e", 100, True), ("e", 130, False)]),
}
BEGIN = {"t1": 0, "t2": 2000, "t3": 4000}
END = {"t1": 500, "t2": 2200, "t3": 4300}
LATE_NS = {("t1", 0): 2_000_000, ("t1", 2): 1_000_000, ("t1", 4): 3_500_000, ("t2", 2): 4_000_000}


def _fixture(plan_edit=None, oracle_edit=None, extra_obs=(), obs_drop=None):
    """Plan, oracle, observation and reference bytes. Hand-computed truth of the default fixture:
    lateness a 2, ime_on 1, b 3.5, c 0, d 4, e 0 ms; observation rows lose the mode-key press of t1 and gain a
    duplicate in t3; reference rows also see the mode key. A marker follows t2 at +2210 ms."""
    plan_rows = [{"kind": "header", "format": "plan/1", "os": "windows"}, {"kind": "block", "block_id": 0}]
    for tid, (speed, steps) in PLAN_STEPS.items():
        plan_rows.append({"kind": "trial", "trial_id": tid, "block_id": 0, "scenario": "S1", "speed": speed,
                          "steps": [{"key": k, "at_ms": at, "down": d} for k, at, d in steps]})
    if plan_edit:
        plan_edit(plan_rows)
    plan = _jl(plan_rows)
    ora = [{"kind": "header", "format": "oracle/1", "plan_sha256": hashlib.sha256(plan).hexdigest()},
           {"kind": "block_begin", "block_id": 0, "t_wall_ms": W0 - 200, "t_mono_ns": MONO0 - 200_000_000},
           {"kind": "marker", "block_id": 0, "seq": 0, "t_wall_ms": W0 - 100, "t_mono_ns": MONO0 - 100_000_000}]
    for tid, (speed, steps) in PLAN_STEPS.items():
        bw, bm = W0 + BEGIN[tid], MONO0 + BEGIN[tid] * 1_000_000
        ora.append({"kind": "trial_begin", "trial_id": tid, "t_wall_ms": bw, "t_mono_ns": bm})
        for i, (k, at, d) in enumerate(steps):
            late = LATE_NS.get((tid, i), 0)
            ora.append({"kind": "sent", "trial_id": tid, "step": i, "key": k, "down": d,
                        "t_wall_ms": bw + at + late // 1_000_000, "t_mono_ns": bm + at * 1_000_000 + late})
        ora.append({"kind": "trial_end", "trial_id": tid, "t_wall_ms": W0 + END[tid],
                    "t_mono_ns": MONO0 + END[tid] * 1_000_000})
        if tid == "t2":
            ora.append({"kind": "marker", "block_id": 0, "seq": 1, "t_wall_ms": W0 + 2210,
                        "t_mono_ns": MONO0 + 2210 * 1_000_000})
    ora.append({"kind": "block_end", "block_id": 0, "t_wall_ms": W0 + 6000, "t_mono_ns": MONO0 + 6000 * 1_000_000})
    if oracle_edit:
        oracle_edit(ora)
    obs_t = [W0 - 97, W0 + 7, W0 + 409, W0 + 2008, W0 + 2114, W0 + 2215, W0 + 4107, W0 + 4120]
    if obs_drop is not None:
        obs_t = [t for t in obs_t if t not in obs_drop]
    obs = [{"type": "meta", "format": "obs/1"}]
    obs += [{"type": "key", "t": t, "category": "alphabetic", "press": True} for t in reversed(obs_t)]
    obs += [{"type": "key", "t": t + 20, "category": "alphabetic", "press": False} for t in obs_t]
    obs += list(extra_obs)
    gt = [{"kind": "header", "format": "gt/1", "src": "x"}]
    gt += [{"kind": "ev", "t_wall_ms": W0 + t, "t_mono_ns": 1, "ev": "key_down", "vk": 65}
           for t in (-97, 3, 202, 405, 2001, 2105, 2211, 4101)]
    gt += [{"kind": "ev", "t_wall_ms": W0 + 5, "t_mono_ns": 1, "ev": "set_marked", "len": "bad"},
           {"kind": "ev", "t_wall_ms": W0 + 6, "t_mono_ns": 1, "ev": "key_up", "vk": 65},
           {"kind": "ev", "t_wall_ms": W0 + 4110, "t_mono_ns": 1, "ev": "focus_out"},
           {"kind": "ev", "t_wall_ms": W0 + 5000, "t_mono_ns": 1, "ev": "focus_out"}]
    return plan, _jl(ora), _jl(obs), _jl(gt)


SEG_TRIALS = (("a0", 0, 1000, 1200), ("a1", 0, 2000, 2200), ("b0", 1, 4500, 4700))
SEG_BEGIN = {0: 0, 1: 3500}


def _seg_fixture(gt_extra=(), gt_drop=(), plan_edit=None, oracle_edit=None):
    """Two blocks of four marker presses each (an oracle marker row per press, a reference key_down 2 ms after it)
    and three one-press trials (a0, a1 in block 0; b0 in block 1; the key_down is 5 ms after the send). Times are
    ms from W0. The reference rows of the default fixture: 4 + 2 of block 0, 4 + 1 of block 1. gt_extra adds
    key_down rows, gt_drop removes the ones at the times given."""
    plan_rows = [{"kind": "header", "format": "plan/1", "os": "macos"}]
    for b in (0, 1):
        plan_rows.append({"kind": "block", "block_id": b, "marker": ["m1", "m2", "m3", "m4"]})
    for tid, b, _bg, _en in SEG_TRIALS:
        plan_rows.append({"kind": "trial", "trial_id": tid, "block_id": b, "scenario": "S1", "speed": "mid",
                          "steps": [{"key": "a", "at_ms": 0, "down": True}, {"key": "a", "at_ms": 50, "down": False}]})
    if plan_edit:
        plan_edit(plan_rows)
    plan = _jl(plan_rows)
    ora = [{"kind": "header", "format": "oracle/1", "plan_sha256": hashlib.sha256(plan).hexdigest()}]
    gt_t, obs_t = [], []
    for b in (0, 1):
        ora.append({"kind": "block_begin", "block_id": b, "t_wall_ms": W0 + SEG_BEGIN[b], "t_mono_ns": 1})
        for i in range(4):
            ora.append({"kind": "marker", "block_id": b, "seq": i, "t_wall_ms": W0 + SEG_BEGIN[b] + 10 * (i + 1),
                        "t_mono_ns": 1})
            gt_t.append(SEG_BEGIN[b] + 10 * (i + 1) + 2)
        for tid, tb, bg, en in SEG_TRIALS:
            if tb != b:
                continue
            ora.append({"kind": "trial_begin", "trial_id": tid, "t_wall_ms": W0 + bg, "t_mono_ns": (W0 + bg) * 1000000})
            for i, down in enumerate((True, False)):
                ora.append({"kind": "sent", "trial_id": tid, "step": i, "key": "a", "down": down,
                            "t_wall_ms": W0 + bg + 50 * i, "t_mono_ns": (W0 + bg + 50 * i) * 1000000})
            ora.append({"kind": "trial_end", "trial_id": tid, "t_wall_ms": W0 + en, "t_mono_ns": (W0 + en) * 1000000})
            gt_t.append(bg + 5)
            obs_t.append(bg + 5)
        ora.append({"kind": "block_end", "block_id": b, "t_wall_ms": W0 + SEG_BEGIN[b] + 1900, "t_mono_ns": 1})
    if oracle_edit:
        oracle_edit(ora)
    gt_t = [t for t in gt_t if t not in gt_drop] + list(gt_extra)
    obs = [{"type": "meta", "format": "obs/1"}] + [{"type": "key", "t": W0 + t, "category": "alphabetic", "press": True}
                                                    for t in obs_t]
    gt = [{"kind": "header", "format": "gt/1", "src": "x"}] + [
        {"kind": "ev", "t_wall_ms": W0 + t, "t_mono_ns": 1, "ev": "key_down", "vk": 65} for t in gt_t]
    return plan, _jl(ora), _jl(obs), _jl(gt)


def _close(a, b):
    if a is None or b is None:
        return a is b
    return abs(a - b) < 1e-6


def _selftest():
    fails = []

    def check(ok, what):
        print("  %s %s" % ("OK" if ok else "NG", what))
        if not ok:
            fails.append(what)

    def summ_is(s, n, mean, mn, p05, med, p95, mx):
        got = [s["n"], s["mean"], s["min"], s["p05"], s["median"], s["p95"], s["max"]]
        return all(_close(g, e) for g, e in zip(got, [n, mean, mn, p05, med, p95, mx]))

    def refused(fx, needle=None):
        try:
            evaluate(*fx)
        except InputError as e:
            return needle is None or needle not in str(e)
        return False

    fx = _fixture()
    out = evaluate(*fx)

    lat = out["send_lateness_ms"]
    check(summ_is(lat["overall"], 6, 1.75, 0, 0, 1.5, 3.875, 4), "send lateness overall (sign, unit, monotonic clock)")
    check(summ_is(lat["by_speed"]["slow"], 3, 2.166667, 1, 1.1, 2, 3.35, 3.5)
          and summ_is(lat["by_speed"]["fast"], 2, 2, 0, 0.2, 2, 3.8, 4)
          and summ_is(lat["by_speed"]["mid"], 1, 0, 0, 0, 0, 0, 0), "send lateness by speed")
    check(out["presses"] == {"all": 6, "excluding_mode_keys": 5}, "pseudo-keys are not presses")

    o = out["observation"]["reach"]
    a, x = o["all_presses"], o["excluding_mode_keys"]
    check(a["sent_presses"] == 6 and a["reached"] == 5 and _close(a["reach_rate"], 5 / 6)
          and a["trials_with_loss"] == 1, "observation reach over all presses: a lost press lowers reach")
    check(a["excess_rows"] == 1 and a["trials_with_excess"] == 1, "observation: a duplicate row is counted as excess")
    check(x["sent_presses"] == 5 and x["reached"] == 5 and x["reach_rate"] == 1.0 and x["trials_with_loss"] == 0
          and x["excess_rows"] == 1, "observation reach excluding mode keys")
    check(a["rows_outside_trials"] == 2 and x["rows_outside_trials"] == 2,
          "marker rows (head of block, and after trial end) fall outside every trial")
    g = out["reference"]["reach"]
    ga, gx = g["all_presses"], g["excluding_mode_keys"]
    check(ga["sent_presses"] == 6 and ga["reached"] == 6 and ga["excess_rows"] == 0 and ga["trials_with_loss"] == 0
          and ga["rows_outside_trials"] == 2, "reference reach over all presses (mode key is seen)")
    check(gx["sent_presses"] == 5 and gx["reached"] == 5 and gx["excess_rows"] == 1 and gx["trials_with_excess"] == 1,
          "reference reach excluding mode keys counts the mode-key row as excess")

    ot = out["observation"]["timing"]
    check(ot["n_trials_paired"] == 2 and ot["n_trials_not_paired"] == 1, "observation: unequal-count trial is not paired")
    check(summ_is(ot["delay_ms"]["overall"], 4, 7.25, 5, 5.15, 7, 9.7, 10)
          and summ_is(ot["delay_ms"]["by_speed"]["slow"], 2, 5.5, 5, 5.05, 5.5, 5.95, 6)
          and ot["delay_ms"]["by_speed"]["mid"]["n"] == 0 and ot["delay_ms"]["by_speed"]["mid"]["mean"] is None,
          "observation delay (row minus sent), overall and by speed")
    check(summ_is(ot["interval_error_ms"]["overall"], 2, 1.5, 1, 1.05, 1.5, 1.95, 2), "observation interval error "
          "uses both the row gaps and the sent gaps")
    gt_ = out["reference"]["timing"]
    check(gt_["n_trials_paired"] == 2 and gt_["n_trials_not_paired"] == 1
          and summ_is(gt_["delay_ms"]["overall"], 3, 1, 1, 1, 1, 1, 1)
          and summ_is(gt_["interval_error_ms"]["overall"], 1, 0, 0, 0, 0, 0, 0)
          and summ_is(gt_["interval_error_ms"]["by_speed"]["fast"], 1, 0, 0, 0, 0, 0, 0)
          and gt_["interval_error_ms"]["by_speed"]["mid"]["n"] == 0, "reference timing (mode-key trial not paired)")
    fo = out["reference_focus_loss"]
    want_fo = [{"scenario": "S1", "speed": "slow", "n_trials": 1, "n_trials_with_focus_loss": 0},
               {"scenario": "S1", "speed": "mid", "n_trials": 1, "n_trials_with_focus_loss": 1},
               {"scenario": "S1", "speed": "fast", "n_trials": 1, "n_trials_with_focus_loss": 0}]
    check(fo["trials_with_focus_loss"] == ["t3"], "the trials with a focus loss are listed: %r" % (fo["trials_with_focus_loss"],))
    check(fo["n_focus_out"] == 2 and fo["n_focus_in"] == 0 and fo["n_loss_intervals"] == 1
          and fo["n_loss_intervals_outside_trials"] == 0 and fo["n_trials_with_focus_loss"] == 1
          and fo["by_stratum"] == want_fo, "focus losses of the reference are counted per trial and stratum")

    # Focus loss intervals, on the fixture without its own focus_out rows. Trial intervals (ms from W0): t1 -20..800,
    # t2 1980..2209, t3 3980..4600. s15 turns t2 into a scenario S15 trial.
    def loss(events, s15=False):
        def edit(rows):
            if s15:
                rows[3]["scenario"] = "S15"
        f = _fixture(plan_edit=edit)
        keep = [r for r in (json.loads(x) for x in f[3].decode("utf-8").split("\n") if x) if r.get("ev") != "focus_out"]
        keep += [{"kind": "ev", "t_wall_ms": W0 + t, "t_mono_ns": 1, "ev": ev} for t, ev in events]
        return evaluate(f[0], f[1], f[2], _jl(keep))["reference_focus_loss"]
    r = loss([(2100, "focus_out")])
    check(r["trials_with_focus_loss"] == ["t2", "t3"] and r["n_loss_intervals"] == 1 and r["n_focus_in"] == 0,
          "a loss that is not regained covers the following trials up to the end of the log")
    r = loss([(700, "focus_out"), (2100, "focus_in")])
    check(r["trials_with_focus_loss"] == ["t1", "t2"] and r["n_focus_in"] == 1,
          "a loss regained in the next trial covers both trials and not the one after")
    r = loss([(2050, "focus_out"), (2150, "focus_in")], s15=True)
    check(r["trials_with_focus_loss"] == [] and r["n_loss_intervals"] == 1 and r["n_loss_intervals_outside_trials"] == 0,
          "a planned S15 switch that returns inside the trial is not listed")
    r = loss([(2050, "focus_out"), (2150, "focus_in")])
    check(r["trials_with_focus_loss"] == ["t2"], "the same switch in a scenario other than S15 is listed")
    r = loss([(2050, "focus_out")], s15=True)
    check(r["trials_with_focus_loss"] == ["t2", "t3"],
          "an S15 switch that does not return is listed together with the following trials")
    r = loss([(2050, "focus_out"), (2300, "focus_in")], s15=True)
    check(r["trials_with_focus_loss"] == ["t2"], "an S15 switch that returns only after the trial's interval is listed")
    r = loss([(2050, "focus_out"), (2100, "focus_in"), (2150, "focus_out")], s15=True)
    check(r["trials_with_focus_loss"] == ["t2", "t3"],
          "an S15 switch that returns, followed by a second loss that does not, is listed with the following trials")
    r = loss([(2300, "focus_out"), (3500, "focus_in")])
    check(r["trials_with_focus_loss"] == [] and r["n_loss_intervals"] == 1 and r["n_loss_intervals_outside_trials"] == 1,
          "a loss between two trials that is regained before the next trial overlaps no trial")
    r = loss([(3500, "focus_in"), (2050, "focus_out"), (2060, "focus_out"), (2100, "focus_in")])
    check(r["n_loss_intervals"] == 1 and r["n_focus_out"] == 2 and r["n_focus_in"] == 2
          and r["trials_with_focus_loss"] == ["t2"]
          and [(b["speed"], b["n_trials_with_focus_loss"]) for b in r["by_stratum"]]
          == [("slow", 0), ("mid", 0), ("fast", 1)],
          "a focus_in with no loss open and a repeated focus_out add no interval")
    check(out["trials"] == {"planned": 3, "begun": 3, "measured": 3, "incomplete": 0}
          and out["inputs_sha256"]["plan"] == hashlib.sha256(fx[0]).hexdigest(), "trial counts and input hashes")

    # window tail is cut at the next oracle row: t2 receives exactly its own two rows.
    rows, _ = _assign([W0 + 2008, W0 + 2114, W0 + 2215], *_windows(
        [{"begin_wall": W0 + 2000, "end_wall": W0 + 2200}], [W0 + 2000, W0 + 2210], 20, 300))
    check(len(rows[0]) == 2, "the interval tail is cut at the next oracle row (marker row lands outside)")
    one = [{"begin_wall": W0 + 2000, "end_wall": W0 + 2200}]
    check(_windows(one, [], 20, 0) == ([W0 + 1980], [W0 + 2200]) and _windows(one, [], 5, 300) == ([W0 + 1995], [W0 + 2500])
          and evaluate(*fx, pre_ms=0, tail_ms=7)["params"] == dict(out["params"], pre_ms=0, tail_ms=7),
          "pre_ms and tail_ms are honoured")

    # all rows lost, and a lost-only variant.
    none = evaluate(*_fixture(obs_drop=set(W0 + t for t in (7, 409, 2008, 2114, 4107, 4120))))
    check(none["observation"]["reach"]["all_presses"]["reached"] == 0
          and none["observation"]["timing"]["n_trials_paired"] == 0, "no row received: reach is zero, nothing paired")

    # ime_shadow rows of any shape change nothing, and are never read.
    junk = [{"type": "ime_shadow", "t": "bad", "press": True, "dwell_ms": None},
            {"type": "ime_shadow", "t": W0 + 10, "press": True, "dwell_ms": [1]},
            {"type": "ime_shadow", "t": W0 + 2010}, {"type": "ime_shadow"}]
    with_junk = evaluate(*_fixture(extra_obs=junk))
    with_junk["inputs_sha256"]["obs"] = out["inputs_sha256"]["obs"]
    check(with_junk == out, "ime_shadow rows with malformed fields do not change anything")
    check(refused((fx[0], fx[1], fx[2] + b"not json\n", fx[3])), "an unparsable observation row is refused")

    # determinism and rendering.
    r1, r2 = render(evaluate(*fx)), render(evaluate(*_fixture()))
    check(r1 == r2 and r1.endswith(b"\n") and b"\r" not in r1 and not r1.startswith(b"\xef\xbb\xbf"),
          "two runs are byte-identical (LF, no BOM)")
    check(json.loads(r1.decode("utf-8")) == out and "\\" not in r1.decode("utf-8"), "output round-trips and holds no path")

    # refusals.
    def other_plan(rows):
        rows[2]["speed"] = "mid"
    check(refused((_fixture(plan_edit=other_plan)[0], fx[1], fx[2], fx[3])), "an unrelated plan is refused")

    def bad_key(ora):
        next(r for r in ora if r.get("kind") == "sent")["key"] = "zzsecretkey"

    def bad_down(ora):
        next(r for r in ora if r.get("kind") == "sent")["down"] = False

    def bad_step(ora):
        next(r for r in ora if r.get("kind") == "sent")["step"] = 99

    def no_begin(ora):
        ora[:] = [r for r in ora if not (r.get("kind") == "trial_begin" and r["trial_id"] == "t2")]

    def two_ends(ora):
        ora.append(dict(next(r for r in ora if r.get("kind") == "trial_end")))
    check(refused(_oracle_with(fx, bad_key), "zzsecretkey"), "sent key that disagrees with the plan is refused, value not echoed")
    check(refused(_oracle_with(fx, bad_down)), "sent down flag that disagrees with the plan is refused")
    check(refused(_oracle_with(fx, bad_step)), "sent step with no plan step is refused")
    check(refused(_oracle_with(fx, no_begin)), "a sent row without its trial_begin is refused")
    check(refused(_oracle_with(fx, two_ends)), "a repeated trial_end is refused")
    check(refused((fx[0], fx[1][:-1] + b"x\n", fx[2], fx[3])), "malformed oracle is refused")

    # segments. Reference rows per segment: the first holds the key outside any block (kana1), block 0 holds its four
    # marker presses and two trial presses, block 1 four marker presses and one trial press.
    def segs(*args, **kw):
        return evaluate(*_seg_fixture(*args, **kw))["reference"]["segments"]

    def row(bid, n_rows, n_reached, marker):
        un = n_rows - n_reached
        return {"block_id": bid, "n_rows": n_rows, "n_reached": n_reached, "n_unexplained": un,
                "n_marker_presses": marker, "n_unexplained_beyond_markers": max(0, un - marker)}
    base = segs()
    check(base["by_segment"] == [row(None, 0, 0, 0), row(0, 6, 2, 4), row(1, 5, 1, 4)] and base["n_segments"] == 3
          and base["max_unexplained_beyond_markers"] == 0, "segments: marker presses are explained by the plan")
    kana_in, kana_out = segs(gt_extra=(-500, 2300)), segs(gt_extra=(-500, 2900))
    want = [row(None, 1, 0, 0), row(0, 7, 2, 4), row(1, 5, 1, 4)]
    check(kana_in["by_segment"] == want and kana_out["by_segment"] == want and kana_in == kana_out
          and kana_in["max_unexplained_beyond_markers"] == 1,
          "segments: a key without an oracle row counts once in its segment, inside or outside the last trial's window")
    full_in = evaluate(*_seg_fixture(gt_extra=(-500, 2300)))["reference"]["reach"]["all_presses"]
    full_out = evaluate(*_seg_fixture(gt_extra=(-500, 2900)))["reference"]["reach"]["all_presses"]
    check(full_in["excess_rows"] == 1 and full_out["excess_rows"] == 0
          and full_in["rows_outside_trials"] + 1 == full_out["rows_outside_trials"],
          "segments: the whole-run counts of reach do depend on where such a key falls (the reason for the segments)")
    at_begin = segs(gt_extra=(SEG_BEGIN[1],))["by_segment"]
    check(at_begin == [row(None, 0, 0, 0), row(0, 6, 2, 4), row(1, 6, 1, 4)],
          "segments: a row at the time of a block_begin belongs to the new block")
    before_begin = segs(gt_extra=(SEG_BEGIN[1] - 1,))["by_segment"]
    check(before_begin[1] == row(0, 7, 2, 4) and before_begin[2] == row(1, 5, 1, 4),
          "segments: a row one millisecond before a block_begin belongs to the previous block")
    swap = segs(gt_drop=(2005,), gt_extra=(2300,))["by_segment"]
    check(swap == base["by_segment"],
          "segments: a press that does not arrive, replaced by one from outside in the same trial, is not detected")
    lost = segs(gt_drop=(2005,))["by_segment"]
    check(lost[1] == row(0, 5, 1, 4) and lost[1]["n_unexplained"] == base["by_segment"][1]["n_unexplained"],
          "segments: a press that does not arrive adds nothing to n_unexplained")
    obs_seg = evaluate(*_seg_fixture())["observation"]["segments"]
    check(obs_seg["by_segment"] == [row(None, 0, 0, 0), row(0, 2, 2, 4), row(1, 1, 1, 4)]
          and obs_seg["max_unexplained_beyond_markers"] == 0, "segments: the observation side is counted the same way")
    nob = evaluate(_seg_fixture()[0], _oracle_with(_seg_fixture(), lambda rows: rows.__setitem__(
        slice(None), [r for r in rows if r.get("kind") != "block_begin"]))[1], *_seg_fixture()[2:])
    check(nob["reference"]["segments"]["n_segments"] == 1
          and nob["reference"]["segments"]["by_segment"] == [row(None, 11, 3, 0)],
          "segments: with no block_begin the whole log is one segment with a null block_id")

    def plan_with(edit):
        return _seg_fixture(plan_edit=edit)

    def bad_marker(rows):
        rows[1]["marker"] = "zzmarker"

    def bad_marker_item(rows):
        rows[1]["marker"] = ["m1", 7]

    def dup_block(rows):
        rows.insert(2, dict(rows[1]))

    def extra_begin(ora):
        ora.append({"kind": "block_begin", "block_id": "zzblock", "t_wall_ms": W0 + 5000, "t_mono_ns": 1})

    def twice_begin(ora):
        ora.append({"kind": "block_begin", "block_id": 0, "t_wall_ms": W0 + 5000, "t_mono_ns": 1})

    def no_id_begin(ora):
        ora.append({"kind": "block_begin", "t_wall_ms": W0 + 5000, "t_mono_ns": 1})
    check(refused(plan_with(bad_marker), "zzmarker"), "a block row whose marker is not an array is refused, value not echoed")
    check(refused(plan_with(bad_marker_item)), "a block row whose marker holds a non-string is refused")
    check(refused(plan_with(dup_block)), "a repeated block_id in the plan is refused")
    check(refused(_oracle_with(_seg_fixture(), extra_begin), "zzblock"),
          "a block_begin of a block that is not in the plan is refused, value not echoed")
    check(refused(_oracle_with(_seg_fixture(), twice_begin)), "a repeated block_begin is refused")
    check(refused(_oracle_with(_seg_fixture(), no_id_begin)), "a block_begin without a block_id is refused")
    check(json.loads(render(evaluate(*_seg_fixture())).decode("utf-8"))["reference"]["segments"] == base,
          "segments: the rendered output holds the same figures")

    # command line.
    me = os.path.abspath(__file__)
    with tempfile.TemporaryDirectory() as tmp:
        paths = {}
        for name, data in zip(("plan", "oracle", "obs", "gt"), fx):
            paths[name] = os.path.join(tmp, name + ".jsonl")
            with open(paths[name], "wb") as f:
                f.write(data)
        outp = os.path.join(tmp, "out.json")
        base = [sys.executable, me, "--plan", paths["plan"], "--oracle", paths["oracle"], "--obs", paths["obs"],
                "--gt", paths["gt"], "--out", outp]
        p = subprocess.run(base, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with open(outp, "rb") as f:
            written = f.read()
        check(p.returncode == 0 and written == render(out), "CLI: exit 0 and the file equals render(evaluate)")
        p = subprocess.run(base, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "CLI: an existing --out is not overwritten (exit 2)")
        with open(outp, "rb") as f:
            check(f.read() == written, "CLI: the existing --out is left untouched")
        with open(paths["plan"], "ab") as f:
            f.write(b'{"kind":"block","block_id":1}\n')
        p = subprocess.run(base[:-1] + [outp + "2"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2 and not os.path.exists(outp + "2"), "CLI: a plan whose hash differs exits 2, nothing written")
        p = subprocess.run([sys.executable, me, "--plan", paths["plan"]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "CLI: a missing argument exits 2")

    if fails:
        print("  ---- delivery selftest: %d failed ----" % len(fails))
        return 1
    print("  ---- delivery selftest: all green ----")
    return 0


def _oracle_with(fx, edit):
    """The fixture with its oracle edited (the header hash is kept, so only the edit can cause a refusal)."""
    rows = [json.loads(line) for line in fx[1].decode("utf-8").split("\n") if line]
    edit(rows)
    return (fx[0], _jl(rows), fx[2], fx[3])
# --- selftest end ---


def _read_file(path, what):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise InputError("cannot open the %s file (%s)" % (what, e.__class__.__name__))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Descriptive report of how faithfully scripted key presses were delivered")
    ap.add_argument("--selftest", action="store_true", help="run the positive and negative controls")
    ap.add_argument("--plan", help="the plan (plan/1)")
    ap.add_argument("--oracle", help="the runner's record of what was sent (oracle/1)")
    ap.add_argument("--obs", help="the observation log (obs/1)")
    ap.add_argument("--gt", help="the reference log (gt/1)")
    ap.add_argument("--out", help="destination for the result JSON (never overwritten)")
    ap.add_argument("--pre-ms", type=int, default=20, help="margin before a trial's interval (default 20)")
    ap.add_argument("--tail-ms", type=int, default=300, help="margin after a trial's interval (default 300)")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if args.selftest:
        return _selftest()
    if not (args.plan and args.oracle and args.obs and args.gt and args.out):
        print("delivery: --plan / --oracle / --obs / --gt / --out are all required", file=sys.stderr)
        return 2
    if args.pre_ms < 0 or args.tail_ms < 0:
        print("delivery: --pre-ms / --tail-ms must be 0 or greater", file=sys.stderr)
        return 2
    if os.path.exists(args.out):
        print("delivery: the output file already exists and is not overwritten", file=sys.stderr)
        return 2
    try:
        data = [_read_file(getattr(args, k), k) for k in ("plan", "oracle", "obs", "gt")]
        body = render(evaluate(data[0], data[1], data[2], data[3], args.pre_ms, args.tail_ms))
    except InputError as e:
        print("delivery: %s" % e, file=sys.stderr)
        return 2
    try:
        with open(args.out, "xb") as f:
            f.write(body)
    except OSError as e:
        print("delivery: cannot write the output file (%s)" % e.__class__.__name__, file=sys.stderr)
        return 2
    print("delivery: wrote the report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
