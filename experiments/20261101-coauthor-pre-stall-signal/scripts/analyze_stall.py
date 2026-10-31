"""conditions.md S3〜S7: 停滞の手前（最後の文字の入力）の推定の上がりを、停滞にならなかった短い休止の手前と比べる。

使い方: python3 -I analyze_stall.py <work2_dir> <meta_creative.csv> <meta_argumentative.csv> <seed> <out_dir>
work2_dir は前の実験の run2.sh の中間（<sid>.ndjson / <sid>_events.json / <sid>_feat.json / writers/）。
出力: counts.json（AUC の前に書く）・auc.json・describe.json。書き手の ID は出さない。
"""
import bisect
import glob
import json
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402  前の実験のコードの写し（AUC・ブートストラップ・書き手の対応）
import analyze2 as A2  # noqa: E402  前の実験のコードの写し（セッションの読み込み・onset の戻し）

TEXT = {"alphabetic", "numeric", "punctuation", "sentence_punctuation", "space", "enter", "tab"}
STALL_GAP = 30_000
CTRL_LO, CTRL_HI = 2_000, 30_000
WARM, GUARD, D_WIN = 60_000, 60_000, 30_000
N_MATCHED, MIN_STALL = 5, 5
SIGNALS = ["d_p_stuck", "d_ewma_x", "p_stuck", "ewma_x"]


def text_presses(s):
    return [(t, c) for t, c in zip(s.press, s.cat) if c in TEXT]


def sig_at(s, u):
    a, b = s.snap(u), s.snap(u - D_WIN)
    if a is None or b is None:
        return None
    return {"d_p_stuck": a["p_stuck"] - b["p_stuck"], "d_ewma_x": a["ewma_x"] - b["ewma_x"],
            "p_stuck": a["p_stuck"], "ewma_x": a["ewma_x"]}


def main():
    wd, mc, ma, seed, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
    os.makedirs(out, exist_ok=True)
    rng = random.Random(seed)
    writers = A.load_writers([mc, ma])
    by_w = {}
    for p in sorted(glob.glob(os.path.join(wd, "*_events.json"))):
        sid = os.path.basename(p)[: -len("_events.json")]
        if sid in writers:
            by_w.setdefault(writers[sid], []).append(A2.S2(wd, sid))
    counts = {"writers_total": len(by_w), "onsets_total": 0, "onsets_unassigned": 0, "onsets_no_text_before": 0,
              "onsets_gap_lt_30s": 0, "onsets_duplicate_anchor": 0, "stall_anchors": 0, "stall_ineligible": 0,
              "stall_no_control": 0}
    data = {}
    for w in sorted(by_w):
        sess = by_w[w]
        ft = json.load(open(os.path.join(wd, "writers", f"{w}_ft.json")))
        offs = json.load(open(os.path.join(wd, "writers", f"{w}_offsets.json")))
        on = [r["t_ms"] for r in ft["rows"] if r["stall_onset"].get("is_onset")]
        counts["onsets_total"] += len(on)
        spans = sorted((min(s.press[:1] + s.feat_t[:1]) + offs[s.sid], max(s.press[-1:] + s.feat_t[-1:]) + offs[s.sid], s)
                       for s in sess if s.sid in offs and (s.press or s.feat_t))
        anchors = {}  # (sid, u) -> (session, u, gap, cls)
        for t in on:
            hit = next(((s, t - offs[s.sid]) for a, b, s in spans if a <= t <= b), None)
            if hit is None:
                counts["onsets_unassigned"] += 1
                continue
            s, t0 = hit
            tp = text_presses(s)
            ts = [x[0] for x in tp]
            i = bisect.bisect_right(ts, t0) - 1
            if i < 0:
                counts["onsets_no_text_before"] += 1
                continue
            u = ts[i]
            nxt = ts[i + 1] if i + 1 < len(ts) else s.t_end
            if nxt - u < STALL_GAP:
                counts["onsets_gap_lt_30s"] += 1
                continue
            if (s.sid, u) in anchors:
                counts["onsets_duplicate_anchor"] += 1
                continue
            anchors[(s.sid, u)] = (s, u, nxt, "boundary" if tp[i][1] in A2.BOUNDARY else "mid")
        counts["stall_anchors"] += len(anchors)
        # 対照の候補: 文字の入力の間隔が 2〜30 秒
        cands = {"boundary": [], "mid": []}
        for s in sess:
            tp = text_presses(s)
            for (u, c), (v, _) in zip(tp, tp[1:]):
                if CTRL_LO <= v - u < CTRL_HI and u - s.t_start >= WARM and not s.any_in(s.ai, u - GUARD, u + GUARD + 1):
                    cands["boundary" if c in A2.BOUNDARY else "mid"].append((s, u))
        rows = []
        for s, u, nxt, cls in anchors.values():
            if u - s.t_start < WARM or s.any_in(s.ai, u - GUARD, u + 1):
                counts["stall_ineligible"] += 1
                continue
            v = sig_at(s, u)
            if v is None:
                counts["stall_ineligible"] += 1
                continue
            pool = cands[cls][:]
            rng.shuffle(pool)
            ctrl = []
            for cs, cu in pool:
                cv = sig_at(cs, cu)
                if cv is not None:
                    ctrl.append(cv)
                    if len(ctrl) == N_MATCHED:
                        break
            if not ctrl:
                counts["stall_no_control"] += 1
                continue
            ended_ai = s.any_in(s.req, u + 1, nxt)
            rows.append((v, ctrl, ended_ai))
        data[w] = rows
    used = [w for w in sorted(data) if len(data[w]) >= MIN_STALL]
    counts["writers_used"] = len(used)
    counts["stalls_used"] = sum(len(data[w]) for w in used)
    counts["controls_used"] = sum(len(c) for w in used for _, c, _ in data[w])
    counts["stalls_ended_ai"] = sum(int(e) for w in used for _, _, e in data[w])
    json.dump(counts, open(os.path.join(out, "counts.json"), "w"), indent=1)

    res = {}
    for sig in SIGNALS:
        per = [A.auc([v[sig] for v, _, _ in data[w]], [c[sig] for _, cs, _ in data[w] for c in cs]) for w in used]
        r = A.boot_median(per, random.Random(seed + 1))
        r["share_gt_05"] = sum(1 for a in per if a > 0.5) / len(per)
        res[sig] = r
    json.dump(res, open(os.path.join(out, "auc.json"), "w"), indent=1)

    desc = {"ended": {}, "threshold": {}}
    for sig in ["d_p_stuck", "d_ewma_x"]:
        ai = [v[sig] for w in used for v, _, e in data[w] if e]
        se = [v[sig] for w in used for v, _, e in data[w] if not e]
        desc["ended"][sig] = {"mean_ai": statistics.mean(ai) if ai else None, "n_ai": len(ai),
                              "mean_self": statistics.mean(se) if se else None, "n_self": len(se)}
        both = [w for w in used if sum(e for _, _, e in data[w]) >= 3 and sum(not e for _, _, e in data[w]) >= 3]
        per = [A.auc([v[sig] for v, _, e in data[w] if e], [v[sig] for v, _, e in data[w] if not e]) for w in both]
        desc["ended"][sig]["writers_both_ge3"] = len(both)
        desc["ended"][sig]["auc_ai_gt_self_median"] = statistics.median(per) if len(both) >= 10 else None
        desc["threshold"][sig] = {}
        for q in (0.8, 0.9, 0.95):
            hits = []
            for w in used:
                cv = sorted(c[sig] for _, cs, _ in data[w] for c in cs)
                th = cv[min(len(cv) - 1, int(q * len(cv)))]
                hits.append(sum(1 for v, _, _ in data[w] if v[sig] > th) / len(data[w]))
            desc["threshold"][sig][str(q)] = {"stall_hit_rate_median": statistics.median(hits)}
    json.dump(desc, open(os.path.join(out, "describe.json"), "w"), indent=1)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
