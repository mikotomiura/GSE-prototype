"""公開データの停滞の型（conditions.md C1・C3・C4）。記述だけ・検定なし。

使い方:
  python3 -I analyze_public.py <klicke_work.tar.gz> <klicke_side.json> <coauthor_work_dir> <holdout.json> <out_dir> <coauthor.zip> <metadata.csv>...
  python3 -I analyze_public.py --selftest
出力は集計値だけ（書き手・セッションの ID も番号も出さない）: <out_dir>/types.json・counts.json。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../20261102-public-data-landscape/scripts"))
import types_core as tc  # noqa: E402
import analyze_landscape as land  # noqa: E402  俯瞰の読み込み・取っておいた書き手の照合・Session

CLASSES_PUBLIC = ("move_or_click", "delete2", "silence")


def to_rec(s):
    """俯瞰の Session → 型の Rec（公開データには focus が無い・開始はセッションの最初の押下）。"""
    return tc.Rec(s.text, s.delete, s.other_nontext, s.intervals, clicks=s.clicks, focus=None, moves=None,
                  block_starts=[s.t_start])


def session_rows(s, normal):
    rec = to_rec(s)
    rows = []
    for o in s.onsets:
        r = rec.stall(o[0], o[1])
        if normal and not r.get("no_interval"):
            end = r["resume"] if r["resume"] is not None else r["interval"][1]
            if s.near_ai(o[0] - tc.PRE_WIN, end):
                continue
        r["third"] = third_of(s, o[1])
        rows.append(r)
    return rows


def third_of(s, t):
    L = s.span_ms()
    if L <= 0:
        return None
    k = int((t - s.t_start) * 3 // L)
    return min(max(k, 0), 2)


def p3_rates(writers, normal):
    """位置ごとの停滞の 1 時間あたり（観測区間との重なりで割る・C4 の P3）。"""
    per_unit = {p: [] for p in tc.POS}
    tot = {p: [0, 0] for p in tc.POS}
    for w in writers:
        u = {p: [0, 0] for p in tc.POS}
        for s in w:
            ivs = land.merge([list(iv) for iv in s.intervals])
            end = max(s.t_end, max(b for _, b in s.intervals))
            regions = {"early": [[s.t_start, s.t_start + tc.EARLY_MS]], "later": [[s.t_start + tc.EARLY_MS, end]]}
            for p, reg in regions.items():
                if reg[0][1] <= reg[0][0]:
                    continue
                part = intersect(ivs, reg)
                ob = sum(b - a for a, b in part)
                if normal:
                    ob -= land.overlap_len(part, s.ai_cover)
                u[p][1] += ob
            for r in session_rows(s, normal):
                if r.get("no_interval") or r["pos"] is None:
                    continue
                u[r["pos"]][0] += 1
        for p in tc.POS:
            tot[p][0] += u[p][0]
            tot[p][1] += u[p][1]
            if u[p][1] > 0:
                per_unit[p].append(u[p][0] / (u[p][1] / tc.H))
    return {p: {"pooled_per_h": round(tot[p][0] / (tot[p][1] / tc.H), 4) if tot[p][1] else None,
                "stalls": tot[p][0], "obs_h": round(tot[p][1] / tc.H, 3),
                "unit_median_per_h": tc.quart(per_unit[p])} for p in tc.POS}


def intersect(ivs, reg):
    out = []
    for a, b in ivs:
        for c, d in reg:
            lo, hi = max(a, c), min(b, d)
            if hi > lo:
                out.append([lo, hi])
    return out


def thirds_share(units, classes):
    ok = [r for u in units for r in tc.typed(u) if r.get("third") is not None]
    return {nm: {c: tc.pooled(sum(1 for r in ok if r["third"] == k and r["pre_class"] == c),
                              sum(1 for r in ok if r["third"] == k)) for c in classes}
            for k, nm in enumerate(("early", "middle", "late"))}


def summarize(writers, normal):
    units = [[r for s in w for r in session_rows(s, normal)] for w in writers]
    res = tc.summarize_types(units, classes=CLASSES_PUBLIC)
    focus_rows = sum(1 for u in units for r in tc.typed(u) if r["pre_class"] == "focus")
    if focus_rows:
        sys.exit("公開データに focus の型が立った（focus は無いはず）")
    res["writers"] = len(writers)
    res["P3"] = p3_rates(writers, normal)
    res["thirds_class_share"] = thirds_share(units, CLASSES_PUBLIC)
    return res


def run(tar_p, side_p, cwork, hold_p, out_dir, czip, *metas):
    hold = json.load(open(hold_p))
    kw, seen = land.load_klicke(tar_p, side_p, set(hold["klicke"]))
    side_keys = set(json.load(open(side_p)))
    if side_keys & {"%05d" % i for i in hold["klicke"]}:
        sys.exit("取っておく書き手が KLiCKe の補いに入っている")
    cw = land.load_coauthor(cwork, land.coauthor_hold_idx(czip, metas, set(hold["coauthor"])))
    k_el = [w for w in kw if sum(s.obs_ms() for s in w) >= land.MIN_WRITER_OBS]
    c_el = [w for w in cw if sum(s.obs_ms() for s in w) >= land.MIN_WRITER_OBS]
    counts = {"klicke": {"writers_loaded": len(kw), "holdout_skipped_in_tar": seen,
                         "excluded_obs_lt_10min": len(kw) - len(k_el)},
              "coauthor": {"writers_loaded": len(cw), "sessions_loaded": sum(len(w) for w in cw),
                           "excluded_obs_lt_10min": len(cw) - len(c_el),
                           "sessions_eligible": sum(len(w) for w in c_el)}}
    res = {"klicke": summarize(k_el, normal=False),
           "coauthor_all": summarize(c_el, normal=False),
           "coauthor_normal": summarize(c_el, normal=True)}
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "types.json"), "w"), indent=1)
    json.dump(counts, open(os.path.join(out_dir, "counts.json"), "w"), indent=1)
    print(json.dumps(counts))


def selftest():
    tc.selftest()
    press = [i * 1000 for i in range(200)] + [259_000 + i * 1000 for i in range(50)]
    keys = [[t, "alphabetic"] for t in press] + [[220_000, "backspace"], [221_000, "backspace"]]
    keys.sort()
    d = {"keys": keys, "feat": [[t, 0.1, 0.1] for t in press],
         "onsets": [[229_000, 235_000, 1000, 199]], "observed_intervals": [[0, 199_000], [199_000, 400_000]]}
    s = land.Session(d, clicks=[], receipts=[], ai=[])
    rows = session_rows(s, normal=False)
    assert len(rows) == 1 and rows[0]["pre_class"] == "delete2" and rows[0]["resume"] == 259_000, rows
    assert rows[0]["pos"] == "early" and rows[0]["third"] == 2
    s2 = land.Session(d, clicks=[230_000], receipts=[], ai=[])
    assert session_rows(s2, normal=False)[0]["pre_class"] == "move_or_click"
    s3 = land.Session(d, clicks=[], receipts=[], ai=[300_000])
    assert session_rows(s3, normal=True) == [] and len(session_rows(s3, normal=False)) == 1
    r = summarize([[s]], normal=False)
    assert r["typed"] == 1 and r["P1_counts"]["delete2|early"] == 1
    assert r["P3"]["early"]["stalls"] == 1 and r["P3"]["later"]["stalls"] == 0
    print("public selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
