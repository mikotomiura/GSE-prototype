"""The three worlds side by side, per width c (descriptive; design 1.5, 3.3 (i), (j)).

Reads this task's results (results/ceiling/ceiling.json and, per step, results/<step>/main/{summary,e13}.json and
results/<step>/split/split.json) and the earlier tasks' files listed in config.json compare.prev_sha256 (paths from
experiments/, each checked against its SHA-256 before it is read), and writes results/compare/compare.json. Nothing is
judged again: the verdicts and readings are copied as they are. A step that did not run (ceiling, unmeasured, or no
main run yet) is "not_run", never counted as green or vanishes.

Usage: compare.py <config.json> <out dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LABELS = ("L300", "L60", "L1800")
RED = ("red_detected", "red_detected_stop_path")
R2_KEYS = ("lr|R2", "lrbin|R2", "hgb|R2")
VERDICT_KEYS = ("green", "red_detected", "red_detected_stop_path", "red_unconfirmed", "undecidable")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_prev(cfg: dict, exp_root: Path) -> dict:
    """The earlier tasks' files, each checked against compare.prev_sha256 (a mismatch or a missing file stops)."""
    out, bad = {}, []
    for rel, want in cfg["compare"]["prev_sha256"].items():
        p = exp_root / rel
        if not p.is_file():
            bad.append(f"{p} is missing")
        elif sha256(p) != want:
            bad.append(f"{p} has SHA-256 {sha256(p)}, not {want}")
        else:
            out[rel] = json.loads(p.read_text(encoding="utf-8"))
    if bad:
        raise SystemExit(f"design 1.5: {bad}")
    return out


def candidates(summary: dict) -> list[str]:
    return sorted(k for k in summary if k.startswith("S-"))


def world_column(status: str, summary: dict | None, e13: dict | None, split: dict | None) -> dict:
    """One world at one c. status: the step's pilot 0 status. A step runs only when go and its main run exists."""
    if status != "go" or summary is None or e13 is None:
        return {"status": status, "ran": False, "reading_i": "not_run"}
    cands = candidates(summary)
    col = {"status": status, "ran": True,
           "auc_A_speed": {t: e13[t].get("auc_A_speed") for t in LABELS},
           "verdict_counts": {t: {v: sum(summary[c][t] == v for c in cands) for v in VERDICT_KEYS} for t in LABELS},
           "verdicts_L300": {c: summary[c]["L300"] for c in cands}}
    col["has_red_L300"] = any(summary[c]["L300"] in RED for c in cands)
    if split is None:
        col["split"] = "not_run"
    else:
        col["split"] = {"counts": split["counts"],
                        "R2": {vk: split["readings"][vk] for vk in R2_KEYS},
                        "pcr_counts": split.get("pcr_counts"),
                        "pcr_R2": {vk: split["pcr_readings"][vk] for vk in R2_KEYS if vk in split.get("pcr_readings", {})}}
    return col


def reading_i(factor: dict, drift: dict) -> str:
    """design 3.3 (i): the table of the two worlds at one c (only when both ran)."""
    if not (factor["ran"] and drift["ran"]):
        return "not_run"
    f, d = factor["has_red_L300"], drift["has_red_L300"]
    return {(False, True): "drift", (True, False): "factor", (True, True): "either",
            (False, False): "neither_alone"}[(f, d)]


def build(cfg: dict, exp_dir: Path, prev: dict) -> dict:
    ceiling = json.loads((exp_dir / "results" / "ceiling" / "ceiling.json").read_text(encoding="utf-8"))
    prev_root = "20261014-rhythm-stage-speed-confound-world/results"
    split_root = "20261015-rhythm-stage-speed-cause-split/results"
    out = {"_note": "Descriptive (design 1.5, 3.3 (i)): copied verdicts and readings, no test; rows are not paired "
                    "across worlds (only the component draws are).", "by_c": {}}
    for c, pair in cfg["compare"]["pairs"].items():
        cs = pair["confound"]
        h_status = prev[f"{prev_root}/ceiling/ceiling.json"]["steps"][cs]["status"]
        cols = {"confound": world_column(h_status, prev[f"{prev_root}/{cs}/main/summary.json"],
                                         prev[f"{prev_root}/{cs}/main/e13.json"],
                                         prev[f"{split_root}/{cs}/main/split.json"])}
        for w in ("factor", "drift"):
            step = pair[w]
            st_ = ceiling["steps"][step]
            if st_["world"] != w:
                raise SystemExit(f"step {step} is {st_['world']} in ceiling.json, not {w}")
            d = exp_dir / "results" / step
            load = lambda f: json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
            cols[w] = world_column(st_["status"], load(d / "main" / "summary.json"), load(d / "main" / "e13.json"),
                                   load(d / "split" / "split.json"))
            cols[w]["step"] = step
        cols["confound"]["step"] = cs
        out["by_c"][c] = {"worlds": cols, "reading_i": reading_i(cols["factor"], cols["drift"])}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("out")
    a = ap.parse_args()
    cfg_path = Path(a.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    exp_dir = cfg_path.parent
    prev = load_prev(cfg, exp_dir.parent)
    doc = build(cfg, exp_dir, prev)
    doc["prev_sha256_checked"] = cfg["compare"]["prev_sha256"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "compare.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, allow_nan=False)
        fh.write("\n")
    for c, v in doc["by_c"].items():
        print(f"c = {c}: reading (i) {v['reading_i']}; "
              + ", ".join(f"{w} {col['status']}/{'red' if col.get('has_red_L300') else 'no red' if col['ran'] else 'not run'}"
                          for w, col in v["worlds"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
