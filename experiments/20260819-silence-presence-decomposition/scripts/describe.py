#!/usr/bin/env python
"""L1 / L2 の記述統計。★ **model-free**。

⚠️★★★ 本スクリプトは推定も予測もしない。**測った量の内訳だけ**を出す。
→ L3 (`analyze.py`) が全滅しても、ここの結論は残る
   (`cv-gate-null` が §3-2 / §3-3 を model-free に保ったのと同じ構造)。

L1 … 沈黙ギャップの分布 (被験者別)
L2 … ⚠️★★★ **5 分窓の時間内訳**。特に `keydown < 100` で除外される窓の中身
"""

from __future__ import annotations

import argparse
import json


def quantile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    pos = q * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def summarize_gaps(gaps: list[dict]) -> dict:
    if not gaps:
        return {"n": 0}
    durs = [g["duration_ms"] for g in gaps]
    with_suspect = [g for g in gaps if g["suspect_at_ms"] is not None]
    observable = [g for g in gaps if g.get("presence_observable")]
    # ⚠️★★★ **`presence_ratio` は「確定値」だけで計算する**（code-reviewer HIGH）。
    #   復帰行の無いギャップ（右側打ち切り等）の `presence_ms` は**下界**にすぎず、
    #   混ぜると中央値が下振れする。
    exact = [g for g in gaps if g.get("presence_kind") == "exact"]
    ratios = [
        g["presence_ms"] / g["duration_ms"]
        for g in exact
        if g["duration_ms"] > 0
    ]
    return {
        "n": len(gaps),
        "n_event": sum(1 for g in gaps if g["event"]),
        "n_censored": sum(1 for g in gaps if not g["event"]),
        "n_with_suspect": len(with_suspect),
        # ⚠️ 分母は**観測可能なギャップ**（code-reviewer MEDIUM）。
        #   全ギャップを分母にすると、計器が無いだけで「presence は 0%」と読めてしまう。
        "frac_with_suspect": (len(with_suspect) / len(observable)) if observable else None,
        "n_with_down": sum(1 for g in gaps if g["down_at_ms"] is not None),
        "n_presence_observable": sum(1 for g in gaps if g.get("presence_observable")),
        "n_rehook": sum(1 for g in gaps if g["rehook"]),
        "duration_ms_p50": quantile(durs, 0.5),
        "duration_ms_p90": quantile(durs, 0.9),
        "duration_ms_max": max(durs),
        "total_silence_ms": sum(durs),
        "presence_ratio_p50": quantile(ratios, 0.5),
        "presence_ratio_p90": quantile(ratios, 0.9),
        "n_presence_exact": len(exact),
        "presence_kind_counts": {
            k: sum(1 for g in gaps if g.get("presence_kind") == k)
            for k in ("exact", "lower_bound", "interval_censored")
        },
        "health_lines_rejected_total": sum(g.get("health_lines_rejected", 0) for g in gaps),
    }


def summarize_windows(windows: list[dict], gate: int) -> dict:
    """★ 窓の時間内訳。⚠️ **ゲートで切った両側を必ず並べる**。"""

    def block(ws: list[dict]) -> dict:
        if not ws:
            return {"n": 0}
        tot = sum(w["window_ms"] for w in ws)
        sil = sum(w["silence_ms"] for w in ws)
        pres = sum(w["silence_with_presence_ms"] for w in ws)
        void = sum(w["silence_void_only_ms"] for w in ws)
        unk = sum(w.get("silence_unknown_ms", 0) for w in ws)
        lead = sum(w.get("silence_leading_ms", 0) for w in ws)
        exc = sum(w.get("silence_excluded_ms", 0) for w in ws)
        return {
            "n": len(ws),
            "total_ms": tot,
            "silence_ms": sil,
            "silence_frac": sil / tot if tot else None,
            "silence_with_presence_ms": pres,
            "silence_with_presence_frac": pres / tot if tot else None,
            "silence_void_only_ms": void,
            "silence_void_only_frac": void / tot if tot else None,
            # ⚠️★★★ **unknown を void と混ぜない。** 計器 (`hook_health`) が無いログでは
            #   「入力皆無だった」ではなく「判定材料が無い」が正しい。
            "silence_unknown_ms": unk,
            "silence_unknown_frac": unk / tot if tot else None,
            # ★ 先頭ギャップ（計測開始 -> 最初の打鍵）。⚠️ **上の内訳とは排他**なので、
            #   「沈黙の総量」は silence_frac + silence_leading_frac で読む。
            "silence_leading_ms": lead,
            "silence_leading_frac": lead / tot if tot else None,
            # ★ E1/E2/E3 で落としたギャップの時間。⚠️ 落とした分を分母から消さずに残す
            #   （消すと沈黙が過小評価される・code-reviewer MEDIUM）。
            "silence_excluded_ms": exc,
            "silence_excluded_frac": exc / tot if tot else None,
            "silence_total_frac": (sil + lead + exc) / tot if tot else None,
            "keydowns_p50": quantile([w["keydowns"] for w in ws], 0.5),
        }

    below = [w for w in windows if w["keydowns"] < gate]
    at_or_above = [w for w in windows if w["keydowns"] >= gate]
    zero = [w for w in windows if w["keydowns"] == 0]
    low = [w for w in windows if 1 <= w["keydowns"] < gate]

    return {
        "gate_keydown": gate,
        "all": block(windows),
        "below_gate": block(below),
        "at_or_above_gate": block(at_or_above),
        "zero_keydown": block(zero),
        "low_nonzero_keydown": block(low),
        "excluded_frac": (len(below) / len(windows)) if windows else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.extract, encoding="utf-8") as fh:
        data = json.load(fh)

    gaps = data["gaps"]
    windows = data["windows"]
    pids = data["participants"]
    # ⚠️ ゲートは本実験では**適用しない**（探索トラック・decisions.md D-4）。
    #    ここでは「上流が何を落としているか」を記述するためだけに使う。
    gate = 100

    leading = data.get("leading_gaps", [])
    l1 = {
        "leading_gaps": summarize_gaps(leading) if leading else {"n": 0},
        "all": summarize_gaps(gaps),
        "by_participant": {p: summarize_gaps([g for g in gaps if g["pid"] == p]) for p in pids},
    }
    l2 = {
        "all": summarize_windows(windows, gate),
        "by_participant": {
            p: summarize_windows([w for w in windows if w["pid"] == p], gate) for p in pids
        },
    }

    payload = {
        "schema": "silence-presence-describe/v1",
        "note": (
            "L1/L2 は model-free。ゲート 100 は上流 (cv-gate-null) が何を落としているかを"
            "記述するためだけに使い、本実験の対象は絞っていない (探索トラック)。"
        ),
        "input_manifest": data["input_manifest"],
        "excluded": data["excluded"],
        "multi_session_files": data["multi_session_files"],
        "L1_gaps": l1,
        "L2_windows": l2,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    a = l1["all"]
    w = l2["all"]
    print(f"L1: gaps={a['n']} event={a['n_event']} censored={a['n_censored']} "
          f"with_suspect={a['n_with_suspect']} rehook={a['n_rehook']}")
    obs = l1["all"].get("n_presence_observable", 0)
    if obs == 0:
        print("⚠️ presence が観測可能なギャップは 0 個 = このコホートに計器 (hook_health) が無い。")
    if w["below_gate"]["n"]:
        b = w["below_gate"]
        print(f"L2: <100 窓 n={b['n']} silence={b['silence_frac']:.3f} "
              f"(+先頭 {b['silence_leading_frac']:.3f} = 計 {b['silence_total_frac']:.3f}) "
              f"presence={b['silence_with_presence_frac']:.3f} "
              f"void={b['silence_void_only_frac']:.3f} "
              f"unknown={b['silence_unknown_frac']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
