#!/usr/bin/env python3
# kit: selftest
"""ブロックごとの同期マーカーから、oracle・正解（gt）・観測（obs）の時刻差の分布とドリフトを出す（Python 標準ライブラリだけ）。

  clock_sync.py --oracle ORACLE [--gt GT] [--obs-keys KEYS] --marker MARKER.json --out JSON [--window-ms N]
  clock_sync.py --selftest                                  陽性対照と陰性対照（速い既定）

MARKER.json = {"oracle_keys":[…], "gt_vks":[…], "obs_categories":[…], "max_gap_ms": int}
  * oracle_keys: 計画のブロックの marker（keyname の配列）。oracle の marker 行は 1 キーにつき 1 行（seq = 0 始まりの添字）で、
    ブロックの行が seq = 0 … len-1 の全部そろっていれば「oracle 側でマーカーが見つかった」とする。
  * gt_vks: 正解側の key_down 行の vk の並び。 obs_categories: 観測側の key 行（press=true）の category の並び。
    どちらも、それぞれの側で**途切れずに連続して**並び、隣り合う間隔が全部 max_gap_ms 以下の箇所をマーカーとして拾う。
    ⚠️ 3 つの並びの先頭は、同じ押下に対応させること（時刻を比べるのは各側の先頭のキー）。
    gt / obs のどちらかだけを渡すなら、その側の並びだけあればよい（gt_vks / obs_categories は使う側だけ要る）。
  * ⚠️ ブロックへの対応づけ = 各ブロックの oracle の先頭のキーの時刻（壁時計）の前後 --window-ms（既定 3000）以内で、
    最も近い出現（1 つの出現を 2 つのブロックに割り当てない）。時計のずれがこの幅を超えると全部「見つからない」になる。

出力する差 = 各側の先頭のキーの時刻 − oracle の先頭のキーの時刻（ms）。⚠️ **遅延（送出から記録までの時間）と時計のずれは分けられない**
（差にはその和が出る）。ブロックをまたいで**変わらない**なら遅延＋一定のずれ、**ブロック番号（時間）とともに動く**ならドリフト。
  * gt_minus_oracle_wall / gt_minus_oracle_mono / obs_minus_oracle_wall / obs_minus_gt_wall（gt と obs の両方があるとき）。
    ⚠️ 観測側は壁時計（Unix ms）だけを持つので、単調時計の差は gt と oracle の間だけ。
  * 各差の統計: 中央値・最小・最大・offset_at_start_ms（最初の oracle のマーカーの時刻での当てはめ値）・
    drift_ms_per_hour（oracle のマーカーの時刻（時間）に対する最小二乗の傾き。2 ブロック未満・時間が動かなければ null）・
    residual_max_ms（当てはめ直線からの最大のずれ）・ブロックごとの値。

⚠️ 観測側は keys-only（seal_obs.py の keys-out）だけを受ける。meta と key の行以外が 1 行でもあれば、内容に触れず拒否する。
   このファイルは ImeShadow の行を読まない・数えない・突き合わせない。
exit 0 = 出した / 1 = oracle にマーカーの揃ったブロックが無い・指定した側で 1 ブロックも見つからない / 2 = 入力が読めない・使い方の誤り。
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

MS_PER_HOUR = 3_600_000.0


class InputError(Exception):
    """入力が読めない・契約に合わない。"""


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def read_jsonl(path):
    rows = []
    try:
        f = open(path, encoding="utf-8")
    except OSError as e:
        raise InputError("%s を開けない（%s）" % (path, e.__class__.__name__))
    with f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                raise InputError("%s の %d 行目が JSON として読めない" % (path, n))
    return rows


def load_marker_spec(path, need_gt, need_obs):
    try:
        with open(path, encoding="utf-8") as f:
            spec = json.load(f)
    except (OSError, ValueError) as e:
        raise InputError("マーカーの仕様（%s）を読めない（%s）" % (path, e.__class__.__name__))

    def strs(key):
        v = spec.get(key) if isinstance(spec, dict) else None
        if not isinstance(v, list) or not v or not all(isinstance(x, str) for x in v):
            raise InputError("マーカーの仕様: %s は文字列の空でない配列" % key)

    if not isinstance(spec, dict):
        raise InputError("マーカーの仕様は object")
    strs("oracle_keys")
    if not _is_int(spec.get("max_gap_ms")) or spec["max_gap_ms"] < 0:
        raise InputError("マーカーの仕様: max_gap_ms は 0 以上の整数")
    if need_gt:
        v = spec.get("gt_vks")
        if not isinstance(v, list) or not v or not all(_is_int(x) for x in v):
            raise InputError("マーカーの仕様: --gt を使うには gt_vks が要る（整数の空でない配列）")
    if need_obs:
        strs("obs_categories")
    return spec


def load_oracle(path):
    """(ブロック ID の列, {block_id: {seq: (wall_ms, mono_ms)}}) を返す。"""
    blocks = []
    markers = {}
    for row in read_jsonl(path):
        if not isinstance(row, dict):
            continue
        kind = row.get("kind")
        if kind not in ("block_begin", "marker"):
            continue
        bid = row.get("block_id")
        if not _is_int(bid):
            raise InputError("%s: %s に整数の block_id が無い" % (path, kind))
        if kind == "block_begin":
            blocks.append(bid)
            continue
        wall, mono, seq = row.get("t_wall_ms"), row.get("t_mono_ns"), row.get("seq")
        if not (_is_int(wall) and _is_int(mono) and _is_int(seq)):
            raise InputError("%s: marker 行に整数の seq / t_wall_ms / t_mono_ns が無い" % path)
        per = markers.setdefault(bid, {})
        if seq in per:
            raise InputError("%s: 同じ block_id・seq の marker 行が 2 つある" % path)
        per[seq] = (wall, mono / 1e6)
    return blocks, markers


def oracle_found(blocks, markers, n_keys):
    """マーカーが揃ったブロック {block_id: (wall_ms, mono_ms)}（先頭のキー）と、揃わなかったブロックの一覧。"""
    found, missing = {}, []
    for b in blocks:
        per = markers.get(b, {})
        if set(per) == set(range(n_keys)):
            found[b] = per[0]
        else:
            missing.append({"block_id": b, "reason": "marker 行が無い" if not per else "marker 行が揃わない（seq が足りない・余る）"})
    return found, missing


def load_gt(path):
    """key_down 行 [(wall_ms, mono_ms, vk)] をファイルの順に返す。"""
    items = []
    for row in read_jsonl(path):
        if isinstance(row, dict) and row.get("kind") == "ev" and row.get("ev") == "key_down":
            wall, mono, vk = row.get("t_wall_ms"), row.get("t_mono_ns"), row.get("vk")
            if not (_is_int(wall) and _is_int(mono) and _is_int(vk)):
                raise InputError("%s: key_down 行に整数の t_wall_ms / t_mono_ns / vk が無い" % path)
            items.append((wall, mono / 1e6, vk))
    return items


def load_obs_keys(path):
    """keys-only の観測から press=true の key 行 [(t_ms, category)] を時刻順に返す。"""
    items = []
    for row in read_jsonl(path):
        kind = row.get("type") if isinstance(row, dict) else None
        if kind == "meta":
            continue
        if kind != "key":
            raise InputError("%s: keys-only ではない行がある（seal_obs.py の keys-out を渡すこと）" % path)
        if not _is_int(row.get("t")):
            raise InputError("%s: key 行に整数の t が無い" % path)
        if row.get("press") is True:
            items.append((row["t"], row.get("category")))
    items.sort(key=lambda x: x[0])
    return items


def find_occurrences(symbols, gap_clock, pattern, max_gap_ms):
    """symbols[i] が pattern と連続して一致し、隣り合う gap_clock[i] の差が 0 以上 max_gap_ms 以下の先頭の添字（重ならない）。"""
    n, m = len(symbols), len(pattern)
    out = []
    i = 0
    while i + m <= n:
        ok = all(symbols[i + k] == pattern[k] for k in range(m))
        if ok:
            for k in range(1, m):
                gap = gap_clock[i + k] - gap_clock[i + k - 1]
                if gap < 0 or gap > max_gap_ms:
                    ok = False
                    break
        if ok:
            out.append(i)
            i += m
        else:
            i += 1
    return out


def match_blocks(oracle_walls, occ_walls, window_ms):
    """近い順の一対一の割り当て。({block_id: 出現の番号}, どのブロックにも対応しない出現の数)。"""
    cands = sorted(
        (abs(tw - to), b, i)
        for b, to in oracle_walls.items()
        for i, tw in enumerate(occ_walls)
        if abs(tw - to) <= window_ms
    )
    assigned, used = {}, set()
    for _, b, i in cands:
        if b not in assigned and i not in used:
            assigned[b] = i
            used.add(i)
    return assigned, len(occ_walls) - len(used)


def summarize(points):
    """points = [(block_id, 時間 x, 差 ms)] → 統計。"""
    if not points:
        return None
    points = sorted(points, key=lambda p: p[1])
    ys = [p[2] for p in points]
    ordered = sorted(ys)
    n = len(ys)
    mid = n // 2
    median = ordered[mid] if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    slope = intercept = resid = None
    xs = [p[1] for p in points]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if n >= 2 and sxx > 0:
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        intercept = my - slope * mx
        resid = max(abs(y - (intercept + slope * x)) for x, y in zip(xs, ys))
    r3 = lambda v: None if v is None else round(v, 3)
    return {
        "n": n,
        "median_ms": r3(median),
        "min_ms": r3(ordered[0]),
        "max_ms": r3(ordered[-1]),
        "offset_at_start_ms": r3(intercept),
        "drift_ms_per_hour": r3(slope),
        "residual_max_ms": r3(resid),
        "per_block": [{"block_id": b, "diff_ms": r3(y)} for b, _, y in points],
    }


def analyze(blocks, markers, spec, gt_items, obs_items, window_ms):
    found, missing_oracle = oracle_found(blocks, markers, len(spec["oracle_keys"]))
    result = {
        "marker": {k: spec[k] for k in ("oracle_keys", "gt_vks", "obs_categories", "max_gap_ms") if k in spec},
        "params": {"window_ms": window_ms},
        "oracle": {"blocks": len(blocks), "with_marker": sorted(found), "missing": missing_oracle},
        "differences": {},
    }
    if not found:
        return result, False
    order = sorted(found, key=lambda b: found[b][0])
    t_first = found[order[0]][0]
    hours = {b: (found[b][0] - t_first) / MS_PER_HOUR for b in found}
    oracle_walls = {b: found[b][0] for b in found}
    matched = {}  # 側の名前 -> {block_id: (wall_ms, mono_ms)}
    complete = True

    def side(name, occ_first, gap_clock, symbols, pattern):
        nonlocal complete
        idx = find_occurrences(symbols, gap_clock, pattern, spec["max_gap_ms"])
        assigned, unmatched = match_blocks(oracle_walls, [occ_first[i][0] for i in idx], window_ms)
        matched[name] = {b: occ_first[idx[i]] for b, i in assigned.items()}
        miss = sorted(b for b in found if b not in assigned)
        result[name] = {"occurrences": len(idx), "matched": sorted(assigned), "missing": miss, "unmatched_occurrences": unmatched}
        if not assigned:
            complete = False

    if gt_items is not None:
        side("gt", [(w, m) for w, m, _ in gt_items], [m for _, m, _ in gt_items], [v for _, _, v in gt_items], spec["gt_vks"])
    if obs_items is not None:
        side("obs", [(t, t) for t, _ in obs_items], [t for t, _ in obs_items], [c for _, c in obs_items], spec["obs_categories"])

    diffs = result["differences"]
    if "gt" in matched:
        g = matched["gt"]
        diffs["gt_minus_oracle_wall"] = summarize([(b, hours[b], g[b][0] - found[b][0]) for b in g])
        diffs["gt_minus_oracle_mono"] = summarize([(b, hours[b], g[b][1] - found[b][1]) for b in g])
    if "obs" in matched:
        o = matched["obs"]
        diffs["obs_minus_oracle_wall"] = summarize([(b, hours[b], o[b][0] - found[b][0]) for b in o])
    if "gt" in matched and "obs" in matched:
        both = [b for b in matched["gt"] if b in matched["obs"]]
        diffs["obs_minus_gt_wall"] = summarize([(b, hours[b], matched["obs"][b][0] - matched["gt"][b][0]) for b in both])
    return result, complete


# --- selftest begin ---
def _selftest():
    fails = []

    def check(ok, what):
        print("  %s %s" % ("✅" if ok else "❌", what))
        if not ok:
            fails.append(what)

    def dump(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")

    T0, MONO0 = 1_700_000_000_000, 5_000_000_000_000
    SPACING = 1_800_000  # ブロックの間隔 30 分 → h = 0, 0.5, 1, …（傾きが ms の整数になる）
    GT_OFFSET, GT_DRIFT = 37, 10      # 既知のずれ +37 ms・ドリフト +10 ms / 時
    OBS_OFFSET, OBS_DRIFT = 12, -4
    MONO_OFFSET_MS = 250.5
    VKS = [105, 107, 113]
    CATS = ["function", "function", "function"]
    spec = {"oracle_keys": ["f13", "f14", "f15"], "gt_vks": VKS, "obs_categories": CATS, "max_gap_ms": 150}

    def build(n_blocks=6, gt_skip=(), obs_skip=(), oracle_skip=(), jitter=0, gt_gap=100, extra_gt=(), extra_obs=()):
        oracle = [{"kind": "header", "format": "oracle/1"}]
        gt = [{"kind": "header", "format": "gt/1", "src": "mac_nstic"}]
        obs = [{"type": "meta", "format": "obs/1"}]
        for b in range(n_blocks):
            bt = T0 + b * SPACING
            h = b * SPACING / MS_PER_HOUR
            j = jitter * (1 if b % 2 else -1)
            gt_off = int(round(GT_OFFSET + GT_DRIFT * h)) + j
            obs_off = int(round(OBS_OFFSET + OBS_DRIFT * h)) - j
            oracle.append({"kind": "block_begin", "block_id": b, "t_wall_ms": bt - 50, "t_mono_ns": MONO0})
            for k in range(3):
                at = bt + 100 * k
                if b not in oracle_skip:
                    oracle.append({"kind": "marker", "block_id": b, "seq": k, "t_wall_ms": at,
                                   "t_mono_ns": MONO0 + (at - T0) * 1_000_000})
                if b not in gt_skip:
                    gt_at = bt + gt_gap * k + gt_off
                    # 単調時計は壁時計のずれ・ドリフトとは別に、一定の +250.5 ms
                    gt_mono = MONO0 + (bt + gt_gap * k - T0) * 1_000_000 + int(MONO_OFFSET_MS * 1_000_000)
                    gt.append({"kind": "ev", "t_wall_ms": gt_at, "t_mono_ns": gt_mono, "ev": "key_down", "vk": VKS[k]})
                if b not in obs_skip:
                    obs.append({"type": "key", "t": bt + 100 * k + obs_off, "category": CATS[k], "press": True})
                    obs.append({"type": "key", "t": bt + 100 * k + obs_off + 20, "category": CATS[k], "press": False})
            # 試行の打鍵（マーカーではない）。gt の vk 0..2 と obs の alphabetic。
            for k in range(3):
                gt.append({"kind": "ev", "t_wall_ms": bt + 2000 + k * 100, "t_mono_ns": MONO0 + (bt + 2000 + k * 100 - T0) * 1_000_000,
                           "ev": "key_down", "vk": k})
                obs.append({"type": "key", "t": bt + 2000 + k * 100, "category": "alphabetic", "press": True})
        gt.extend(extra_gt)
        obs.extend(extra_obs)
        return oracle, gt, obs

    with tempfile.TemporaryDirectory() as tmp:
        def run(oracle, gt, obs, window=3000, sp=spec):
            paths = {}
            for name, rows in (("oracle", oracle), ("gt", gt), ("obs", obs)):
                paths[name] = os.path.join(tmp, name + ".jsonl")
                dump(paths[name], rows)
            blocks, markers = load_oracle(paths["oracle"])
            return analyze(blocks, markers, sp, load_gt(paths["gt"]), load_obs_keys(paths["obs"]), window)[0]

        # 既知のずれとドリフトを回復（gt +37 ms・+10 ms/時 ／ obs +12 ms・-4 ms/時）
        r = run(*build())
        g = r["differences"]["gt_minus_oracle_wall"]
        check(g["n"] == 6 and abs(g["offset_at_start_ms"] - GT_OFFSET) < 0.01 and abs(g["drift_ms_per_hour"] - GT_DRIFT) < 0.01,
              "既知のずれとドリフトを回復（gt: ずれ %s ms・ドリフト %s ms/時）" % (g["offset_at_start_ms"], g["drift_ms_per_hour"]))
        o = r["differences"]["obs_minus_oracle_wall"]
        check(o["n"] == 6 and abs(o["offset_at_start_ms"] - OBS_OFFSET) < 0.01 and abs(o["drift_ms_per_hour"] - OBS_DRIFT) < 0.01,
              "観測側のずれとドリフトも回復（ずれ %s ms・ドリフト %s ms/時）" % (o["offset_at_start_ms"], o["drift_ms_per_hour"]))
        d = r["differences"]["obs_minus_gt_wall"]
        check(abs(d["offset_at_start_ms"] - (OBS_OFFSET - GT_OFFSET)) < 0.01 and abs(d["drift_ms_per_hour"] - (OBS_DRIFT - GT_DRIFT)) < 0.01,
              "obs − gt は 2 つの差の差（ずれ %s ms・ドリフト %s ms/時）" % (d["offset_at_start_ms"], d["drift_ms_per_hour"]))
        check(g["residual_max_ms"] < 0.01 and g["min_ms"] == GT_OFFSET and g["max_ms"] == GT_OFFSET + 25, "差の範囲（%s〜%s ms）と残差" % (g["min_ms"], g["max_ms"]))
        m = r["differences"]["gt_minus_oracle_mono"]
        check(m["n"] == 6 and m["min_ms"] == m["max_ms"] == MONO_OFFSET_MS and abs(m["drift_ms_per_hour"]) < 0.01,
              "単調時計の差は別に出る（一定の +%s ms・ドリフト 0）" % MONO_OFFSET_MS)
        check(r["gt"]["missing"] == [] and r["obs"]["missing"] == [] and r["gt"]["unmatched_occurrences"] == 0, "全ブロックが見つかる")

        # ノイズ（±1 ms のゆらぎ）があっても、傾きとずれは 2 ms / (ms/時) 以内で回復する
        r = run(*build(jitter=1))
        g = r["differences"]["gt_minus_oracle_wall"]
        check(abs(g["offset_at_start_ms"] - GT_OFFSET) < 2 and abs(g["drift_ms_per_hour"] - GT_DRIFT) < 2 and g["residual_max_ms"] <= 1.5,
              "±1 ms のゆらぎがあっても回復（ずれ %s・ドリフト %s・残差 %s）" % (g["offset_at_start_ms"], g["drift_ms_per_hour"], g["residual_max_ms"]))

        # ⚠️ マーカーが無いブロックは「見つからない」に出る（陰性対照）
        r = run(*build(gt_skip=(3,), obs_skip=(1, 4)))
        check(r["gt"]["missing"] == [3] and r["obs"]["missing"] == [1, 4], "マーカーが無いブロックを「見つからない」に出す（gt %s・obs %s）" % (r["gt"]["missing"], r["obs"]["missing"]))
        g = r["differences"]["gt_minus_oracle_wall"]
        check(g["n"] == 5 and abs(g["drift_ms_per_hour"] - GT_DRIFT) < 0.01, "見つかったブロックだけで、ドリフトは変わらず回復する（n=%d）" % g["n"])
        check(r["differences"]["obs_minus_gt_wall"]["n"] == 3, "obs − gt は両方に見つかったブロックだけ（n=%d）" % r["differences"]["obs_minus_gt_wall"]["n"])
        r = run(*build(oracle_skip=(2,)))
        check([x["block_id"] for x in r["oracle"]["missing"]] == [2] and 2 not in r["oracle"]["with_marker"], "oracle 側の marker 行が無いブロックも「見つからない」に出る")

        # 間隔が max_gap_ms を超えるマーカーは拾わない・どのブロックの近くにも無い出現は割り当てない
        r = run(*build(gt_gap=300))
        check(r["gt"]["matched"] == [] and r["gt"]["missing"] == [0, 1, 2, 3, 4, 5], "キーの間隔が max_gap_ms を超えるとマーカーではない")
        stray = [{"kind": "ev", "t_wall_ms": T0 + 100 * SPACING + k * 100, "t_mono_ns": MONO0, "ev": "key_down", "vk": VKS[k]} for k in range(3)]
        r = run(*build(extra_gt=stray))
        check(r["gt"]["unmatched_occurrences"] == 1 and r["gt"]["matched"] == [0, 1, 2, 3, 4, 5], "どのブロックにも近くない出現は割り当てず、数える")
        partial = [{"kind": "ev", "t_wall_ms": T0 + 100 * SPACING, "t_mono_ns": MONO0, "ev": "key_down", "vk": VKS[0]},
                   {"kind": "ev", "t_wall_ms": T0 + 100 * SPACING + 50, "t_mono_ns": MONO0 + 50_000_000, "ev": "key_down", "vk": VKS[1]}]
        r = run(*build(extra_gt=partial))
        check(r["gt"]["occurrences"] == 6, "並びの途中で終わる出現はマーカーではない")
        r = run(*build(), window=1)  # gt のずれは 37 ms 以上・obs のずれは 12 ms から 2 ms へ縮むが、どれも 1 ms を超える
        check(r["gt"]["matched"] == [] and r["obs"]["matched"] == [], "時計のずれが --window-ms を超えると見つからない")

        # 入力の契約と終了コード
        me = os.path.abspath(__file__)
        op, gp, kp = (os.path.join(tmp, n + ".jsonl") for n in ("oracle", "gt", "obs"))
        sp, out = os.path.join(tmp, "marker.json"), os.path.join(tmp, "out.json")
        dump(op, build()[0]); dump(gp, build()[1]); dump(kp, build()[2])
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(spec, f)

        def cli(*extra, o=out):
            p = subprocess.run([sys.executable, me, "--oracle", op, "--marker", sp, "--out", o] + list(extra),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return p.returncode, p.stdout.decode("utf-8", "replace")

        rc, text = cli("--gt", gp, "--obs-keys", kp)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        check(rc == 0 and abs(data["differences"]["gt_minus_oracle_wall"]["drift_ms_per_hour"] - GT_DRIFT) < 0.01, "CLI: 出力の JSON にドリフト（exit %d）" % rc)
        rc, _ = cli("--gt", gp)
        check(rc == 0, "gt だけでも回る（exit %d）" % rc)
        dump(kp, build()[2] + [{"type": "x", "t": 1}])
        rc, text = cli("--obs-keys", kp, o=out + "2")
        check(rc == 2 and not os.path.exists(out + "2") and "keys-only" in text, "keys-only でない行があれば拒否する（exit %d・出力を書かない）" % rc)
        dump(kp, build(obs_skip=range(6))[2])
        rc, _ = cli("--obs-keys", kp, o=out + "3")
        check(rc == 1, "指定した側で 1 ブロックも見つからなければ exit 1（exit %d）" % rc)
        dump(op, build(oracle_skip=range(6))[0])
        rc, _ = cli("--gt", gp, o=out + "4")
        check(rc == 1, "oracle にマーカーの揃ったブロックが無ければ exit 1（exit %d）" % rc)
        with open(sp, "w", encoding="utf-8") as f:
            json.dump({"oracle_keys": ["f13"], "max_gap_ms": 150}, f)
        rc, _ = cli("--gt", gp, o=out + "5")
        check(rc == 2, "gt を使うのに gt_vks が無ければ exit 2（exit %d）" % rc)

    if fails:
        print("  ---- clock_sync selftest 失敗 %d 件 ----" % len(fails))
        return 1
    print("  ---- clock_sync selftest すべて緑 ----")
    return 0
# --- selftest end ---


def main(argv=None):
    ap = argparse.ArgumentParser(description="同期マーカーから、oracle・gt・観測の時刻差の分布とドリフトを出す")
    ap.add_argument("--selftest", action="store_true", help="陽性対照と陰性対照を回す")
    ap.add_argument("--oracle", help="実行器の出力（oracle/1）")
    ap.add_argument("--gt", help="正解の生ログ（gt/1）")
    ap.add_argument("--obs-keys", help="keys-only の観測（seal_obs.py の keys-out）")
    ap.add_argument("--marker", help="マーカーの仕様の JSON ファイル")
    ap.add_argument("--out", help="結果の JSON の出力先")
    ap.add_argument("--window-ms", type=int, default=3000, help="ブロックに出現を対応づける幅（既定 3000）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.oracle and args.marker and args.out):
        ap.error("--oracle / --marker / --out がすべて要る")
    if not (args.gt or args.obs_keys):
        ap.error("--gt か --obs-keys のどちらかは要る")
    if args.window_ms < 0:
        ap.error("--window-ms は 0 以上")
    try:
        spec = load_marker_spec(args.marker, bool(args.gt), bool(args.obs_keys))
        blocks, markers = load_oracle(args.oracle)
        gt_items = load_gt(args.gt) if args.gt else None
        obs_items = load_obs_keys(args.obs_keys) if args.obs_keys else None
        result, complete = analyze(blocks, markers, spec, gt_items, obs_items, args.window_ms)
    except InputError as e:
        print("clock_sync: %s" % e, file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    o = result["oracle"]
    print("ブロック %d（oracle にマーカーあり %d・見つからない %s）" % (
        o["blocks"], len(o["with_marker"]), [x["block_id"] for x in o["missing"]]))
    for name in ("gt", "obs"):
        if name in result:
            s = result[name]
            print("%s: 一致 %d・見つからない %s・どのブロックにも対応しない出現 %d" % (name, len(s["matched"]), s["missing"], s["unmatched_occurrences"]))
    for name, st in result["differences"].items():
        if st:
            print("%s: n=%d 中央値 %s ms（範囲 %s〜%s）・ドリフト %s ms/時" % (
                name, st["n"], st["median_ms"], st["min_ms"], st["max_ms"], st["drift_ms_per_hour"]))
    if not o["with_marker"]:
        print("clock_sync: oracle にマーカーの揃ったブロックが無い（marker 行と oracle_keys の長さを確かめること）", file=sys.stderr)
        return 1
    if not complete:
        print("clock_sync: 1 ブロックも対応づけられない側がある（--window-ms・マーカーの仕様・ログを確かめること）", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
