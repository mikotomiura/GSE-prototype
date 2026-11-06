"""CS1 2021 の作り直した中間が、俯瞰の変換（build_cs1.py）で同じ入力から作った中間と一致するかを確かめる（design §1.2 の門・P-D1 の CS1 側）。

使い方: python3 -I check_same_cs1.py <ref_work> <obs_work> <landscape_build_summary_2021.json>
  python3 -I check_same_cs1.py --selftest
値は出さず、件数と総数だけを出す。1 つでも外れれば終了コード 1。
  - units.json・writers.json が完全一致。
  - 全課題で keys・observed_intervals・blocks・onsets が完全一致。
  - events は、新しい中間の "lookup-accept" を "ide-action" に戻したものが俯瞰の events と完全一致
    （受け入れの行は俯瞰では ide-action だったので、戻せば同じ表になる）。
  - feat の行数が同じで、新しい中間の [t, p_stuck, ewma_x]（0・3・4 列）が俯瞰の 3 列と完全一致（NaN は NaN 同士）、
    obs は 0〜25 の整数、alpha は {0.3, 0.15, 0.18, 0.25} のどれか、行の長さは 8。
  - 書き手の数・課題の数・status・holdout の SHA-256 が、repo の俯瞰の build_summary_2021.json と一致。
  - lookup-accept の総数が 0 でない（名前の取り違えの見張り）。
"""
import json
import math
import os
import sys

ALPHAS = (0.3, 0.15, 0.18, 0.25)


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def unit_ok(a, b):
    """a = 俯瞰の 1 課題・b = 作り直した 1 課題。(一致したか, feat 行の数, 受け入れの数)。"""
    n_acc = sum(1 for e in b["events"] if e[1] == "lookup-accept")
    ok = all(a[f] == b[f] for f in ("keys", "observed_intervals", "blocks", "onsets"))
    back = [[t, "ide-action" if v == "lookup-accept" else v] for t, v in b["events"]]
    ok = ok and back == a["events"]
    ok = ok and len(a["feat"]) == len(b["feat"])
    rows = 0
    for ra, rb in zip(a["feat"], b["feat"]):
        rows += 1
        if not (len(rb) == 8 and all(same(x, y) for x, y in zip(ra, (rb[0], rb[3], rb[4])))
                and isinstance(rb[6], int) and not isinstance(rb[6], bool) and 0 <= rb[6] <= 25
                and rb[7] in ALPHAS):
            ok = False
            break
    return ok, rows, n_acc


def main():
    ref, new, summ_p = sys.argv[1:4]
    errs = []
    for name in ("units.json", "writers.json"):
        if json.load(open(os.path.join(ref, name))) != json.load(open(os.path.join(new, name))):
            errs.append(name + " が違う")
    units = json.load(open(os.path.join(new, "units.json")))
    bad = rows = acc = 0
    for k in sorted(units):
        a = json.load(open(os.path.join(ref, "u%s.json" % k)))
        b = json.load(open(os.path.join(new, "u%s.json" % k)))
        ok, r, n = unit_ok(a, b)
        bad += not ok
        rows += r
        acc += n
    land = json.load(open(summ_p))
    sb = json.load(open(os.path.join(new, "build_summary.json")))
    for f in ("writers_read", "holdout_writers_skipped", "units", "attempted", "holdout_sha256", "status",
              "blocks_kept", "blocks_few_presses", "span_too_long_days"):
        if sb.get(f) != land.get(f):
            errs.append("build_summary の %s が俯瞰と違う" % f)
    if bad:
        errs.append("一致しない課題がある")
    if acc == 0:
        errs.append("lookup-accept が 0 件")
    out = {"units": len(units), "feat_rows": rows, "mismatched_units": bad, "lookup_accept_total": acc,
           "errors": errs}
    print(json.dumps(out, ensure_ascii=False))
    if errs:
        sys.exit(1)


def selftest():
    nan = float("nan")
    a = {"keys": [[0, "a"]], "observed_intervals": [[0, 9]], "blocks": [[0, 9]], "onsets": [],
         "events": [[5, "ide-action"], [6, "run"]], "feat": [[1000, nan, 0.5]]}
    b = dict(a, events=[[5, "lookup-accept"], [6, "run"]], feat=[[1000, 0.2, 0.3, nan, 0.5, 0.1, 7, 0.3]])
    assert unit_ok(a, b) == (True, 1, 1)
    # 陰性: 受け入れでない出来事が違う・feat の列が違う・obs が範囲外・alpha が想定外・行が足りない
    assert not unit_ok(a, dict(b, events=[[5, "lookup-accept"], [6, "paste"]]))[0]
    assert not unit_ok(a, dict(b, events=[[5, "lookup-accept"]]))[0]
    assert not unit_ok(a, dict(b, feat=[[1000, 0.2, 0.3, 0.1, 0.5, 0.1, 7, 0.3]]))[0]
    assert not unit_ok(a, dict(b, feat=[[1000, 0.2, 0.3, nan, 0.5, 0.1, 26, 0.3]]))[0]
    assert not unit_ok(a, dict(b, feat=[[1000, 0.2, 0.3, nan, 0.5, 0.1, 7.0, 0.3]]))[0]
    assert not unit_ok(a, dict(b, feat=[[1000, 0.2, 0.3, nan, 0.5, 0.1, 7, 0.2]]))[0]
    assert not unit_ok(a, dict(b, feat=[]))[0]
    assert not unit_ok(a, dict(b, blocks=[[0, 8]]))[0]
    # 俯瞰の ide-action のうち受け入れでないものは、作り直しでも ide-action のまま
    a2 = dict(a, events=[[5, "ide-action"], [6, "ide-action"]])
    assert unit_ok(a2, dict(b, events=[[5, "lookup-accept"], [6, "ide-action"]]))[0]
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
