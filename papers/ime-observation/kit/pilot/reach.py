#!/usr/bin/env python3
# kit: selftest
"""合成入力が観測部のフックに届くかを、観測側の key 行だけで確かめる（Python 標準ライブラリだけ）。

  reach.py --oracle ORACLE --obs-keys KEYS --out JSON [--pre-ms N] [--tail-ms N] [--ignore-keys a,b,...]
  reach.py --selftest                                       陽性対照と陰性対照（速い既定）

試行ごとに、実行器が**送った押下の数**（oracle の sent 行で down=true・擬似キーを除く）と、その試行の区間に落ちた
**key 行（press=true）の数**を比べる。
  * reach_rate = Σ min(送った, 届いた) / Σ 送った。⚠️ 届いた数が多い試行（重複・別の試行の行）で、別の試行の
    取りこぼしが隠れないように min を取る。多かった分は excess_rows に別に数える。
  * diff_distribution = 試行ごとの（届いた − 送った）の分布。0 なら全部届いた・負ならその数だけ取りこぼした。
  * 区間 = oracle の trial_begin から trial_end まで（壁時計）。観測側の行は送出の後に出るので、区間の前に
    --pre-ms（既定 20）・後ろに --tail-ms（既定 300）の余裕を取る。
    ⚠️ 区間の後ろは、**次の oracle 行**（reset / block_begin / marker / 次の trial_begin）でも切る
    （--tail-ms との min）。切らないと、次のブロックの先頭のマーカーの押下が前のブロックの最後の試行に
    数えられ、その試行の取りこぼしが隠れる。どの試行の区間にも入らない行は outside_trials_rows に数える
    （ブロック頭のマーカーのキーがここに入る）。

⚠️ 観測側は keys-only（seal_obs.py の keys-out）だけを受ける。meta と key の行以外が 1 行でもあれば、内容に触れず拒否する。
   このファイルは ImeShadow の行を読まない・数えない・突き合わせない。
exit 0 = 集計した / 1 = 集計できる送信が 1 つも無い（空振りを緑にしない）/ 2 = 入力が読めない・使い方の誤り。
"""
import argparse
import bisect
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

DEFAULT_IGNORE = ("mouse_click", "focus_away", "focus_back")  # 実キーではない擬似キー（key 行を作らない）


class InputError(Exception):
    """入力が読めない・契約に合わない。"""


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _no_dup_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("同じキーが 2 回ある行がある")
        out[k] = v
    return out


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
                rows.append(json.loads(line, object_pairs_hook=_no_dup_pairs))
            except ValueError:
                raise InputError("%s の %d 行目が JSON として読めない" % (path, n))
    return rows


def load_oracle(path):
    """試行の一覧 [{trial_id, begin, end, sent}]（begin / end は t_wall_ms・sent は押下の keyname の列）と、
    区間を切るための「次の oracle 行」の時刻の昇順の列（reset / block_begin / marker / trial_begin）を返す。
    """
    trials = {}
    order = []
    cuts = []
    for row in read_jsonl(path):
        if not isinstance(row, dict):
            continue
        kind = row.get("kind")
        if kind in ("reset", "block_begin", "marker"):
            wall = row.get("t_wall_ms")
            if _is_int(wall):
                cuts.append(wall)
            continue
        if kind not in ("trial_begin", "trial_end", "sent"):
            continue
        tid = row.get("trial_id")
        if not isinstance(tid, str):
            raise InputError("%s: trial_id が文字列ではない行がある" % path)
        if tid not in trials:
            trials[tid] = {"trial_id": tid, "begin": None, "end": None, "sent": []}
            order.append(tid)
        t = trials[tid]
        if kind == "sent":
            if row.get("down") is True:
                t["sent"].append(row.get("key"))
            continue
        wall = row.get("t_wall_ms")
        if not _is_int(wall):
            raise InputError("%s: %s に整数の t_wall_ms が無い" % (path, kind))
        field = "begin" if kind == "trial_begin" else "end"
        if t[field] is not None:
            raise InputError("%s: 同じ trial_id に %s が 2 つある" % (path, kind))
        t[field] = wall
        if kind == "trial_begin":
            cuts.append(wall)
    cuts.sort()
    return [trials[k] for k in order], cuts


def load_keys_only(path):
    """keys-only の観測を読み、press=true の key 行の (t・Unix ms, category) を時刻の昇順で返す。"""
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


def analyze(trials, cuts, presses, pre_ms, tail_ms, ignore):
    done = sorted((t for t in trials if t["begin"] is not None and t["end"] is not None), key=lambda t: t["begin"])
    starts = [t["begin"] - pre_ms for t in done]
    ends = []
    for t in done:
        end_i = t["end"] + tail_ms
        i = bisect.bisect_right(cuts, t["end"])
        if i < len(cuts):
            end_i = min(end_i, cuts[i] - 1)
        ends.append(end_i)
    counts = [0] * len(done)
    obs_cats = [[] for _ in done]
    outside = 0
    for ts, cat in presses:
        i = bisect.bisect_right(starts, ts) - 1
        if i >= 0 and ts <= ends[i]:
            counts[i] += 1
            obs_cats[i].append(cat)
        else:
            outside += 1
    per_trial = []
    dist = {}
    sent_total = reached = excess = full = lossy = 0
    for t, got, cats in zip(done, counts, obs_cats):
        sent_keys = [k for k in t["sent"] if k not in ignore]
        sent = len(sent_keys)
        per_trial.append({"trial_id": t["trial_id"], "sent": sent, "obs": got, "sent_keys": sent_keys, "obs_categories": cats})
        sent_total += sent
        reached += min(sent, got)
        excess += max(0, got - sent)
        d = got - sent
        dist[d] = dist.get(d, 0) + 1
        if d >= 0:
            full += 1
        else:
            lossy += 1
    return {
        "params": {"pre_ms": pre_ms, "tail_ms": tail_ms, "ignore_keys": sorted(ignore)},
        "trials_measured": len(done),
        "trials_incomplete": len(trials) - len(done),
        "sent_presses": sent_total,
        "reached": reached,
        "reach_rate": (reached / sent_total) if sent_total else None,
        "excess_rows": excess,
        "outside_trials_rows": outside,
        "trials_with_all_reached": full,
        "trials_with_loss": lossy,
        "diff_distribution": {str(k): dist[k] for k in sorted(dist)},
        "per_trial": per_trial,
    }


# --- selftest begin ---
def _selftest():
    fails = []

    def check(ok, what):
        print("  %s %s" % ("OK" if ok else "NG", what))
        if not ok:
            fails.append(what)

    def dump(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")

    # 6 試行 × 押下 4（+ 離し 4）・キーの間隔 100 ms・試行の間隔 1500 ms。試行 2 だけ擬似キーを 1 つ含む。
    t0 = 1_700_000_000_000
    oracle = [{"kind": "header", "format": "oracle/1"}, {"kind": "block_begin", "block_id": 0, "t_wall_ms": t0 - 900, "t_mono_ns": 0}]
    for s in range(3):
        oracle.append({"kind": "marker", "block_id": 0, "seq": s, "t_wall_ms": t0 - 800 + s * 100, "t_mono_ns": 0})
    obs_full = [{"type": "meta", "format": "obs/1"}]
    for s in range(3):  # マーカーのキーの観測(どの試行の区間にも入らない)
        obs_full.append({"type": "key", "t": t0 - 800 + s * 100 + 3, "category": "function", "press": True})
    for n in range(6):
        tid = "t%05d" % (n + 1)
        base = t0 + n * 1500
        oracle.append({"kind": "trial_begin", "trial_id": tid, "t_wall_ms": base, "t_mono_ns": 0})
        for s in range(4):
            at = base + s * 100
            oracle.append({"kind": "sent", "trial_id": tid, "step": 2 * s, "key": "a", "down": True, "t_wall_ms": at, "t_mono_ns": 0})
            oracle.append({"kind": "sent", "trial_id": tid, "step": 2 * s + 1, "key": "a", "down": False, "t_wall_ms": at + 20, "t_mono_ns": 0})
            obs_full.append({"type": "key", "t": at + 3, "category": "alphabetic", "press": True})
            obs_full.append({"type": "key", "t": at + 23, "category": "alphabetic", "press": False})
        if n == 1:
            oracle.append({"kind": "sent", "trial_id": tid, "step": 8, "key": "mouse_click", "down": True, "t_wall_ms": base + 350, "t_mono_ns": 0})
        oracle.append({"kind": "trial_end", "trial_id": tid, "t_wall_ms": base + 301, "t_mono_ns": 0})
    oracle.append({"kind": "block_end", "block_id": 0, "t_wall_ms": t0 + 9000, "t_mono_ns": 0})

    trials = None
    with tempfile.TemporaryDirectory() as tmp:
        op = os.path.join(tmp, "oracle.jsonl")
        dump(op, oracle)
        trials, cuts = load_oracle(op)
        check(len(trials) == 6 and all(len(t["sent"]) == 4 + (1 if i == 1 else 0) for i, t in enumerate(trials)),
              "oracle: 6 試行・押下だけを数える（離しは数えない）")

        def measure(rows, **kw):
            kp = os.path.join(tmp, "keys.jsonl")
            dump(kp, rows)
            return analyze(trials, cuts, load_keys_only(kp), kw.get("pre", 20), kw.get("tail", 300), set(kw.get("ignore", DEFAULT_IGNORE)))

        r = measure(obs_full)
        check(r["reach_rate"] == 1.0 and r["sent_presses"] == 24 and r["diff_distribution"] == {"0": 6},
              "全部届くと到達率 100%%（送った押下 %d・擬似キーは数えない）" % r["sent_presses"])
        check(r["outside_trials_rows"] == 3, "マーカーのキーは試行の外の行に数える（%d 行）" % r["outside_trials_rows"])
        check(measure(obs_full, ignore=())["sent_presses"] == 25, "擬似キーを無視しない指定なら送った押下が 1 つ増える")
        check(r["per_trial"][0]["sent_keys"] == ["a", "a", "a", "a"] and r["per_trial"][0]["obs_categories"] == ["alphabetic"] * 4,
              "per_trial に送った keyname の並びと届いた category の並びが出る（%s）" % r["per_trial"][0])

        # ⚠️ 陽性対照: 押下の key 行を 1 つおきに消すと 50%
        press_rows = [r_ for r_ in obs_full if r_.get("press") is True and r_["t"] >= t0]
        drop = set(id(x) for x in press_rows[1::2])
        half = [x for x in obs_full if id(x) not in drop]
        r = measure(half)
        check(r["reach_rate"] == 0.5 and r["trials_with_loss"] == 6, "key 行を半分消すと 50%%（実測 %.1f%%）" % (100 * r["reach_rate"]))
        r = measure([x for x in obs_full if x.get("type") == "meta" or x["t"] < t0])
        check(r["reach_rate"] == 0.0, "届いた key 行が無ければ 0%")
        r = measure([x for x in obs_full if x.get("press") is not False])
        check(r["reach_rate"] == 1.0, "離し（press=false）の行が無くても 100%（押下だけを数える）")
        dup = obs_full + [{"type": "key", "t": t0 + 5, "category": "alphabetic", "press": True}]
        r = measure(dup)
        check(r["reach_rate"] == 1.0 and r["excess_rows"] == 1 and r["diff_distribution"] == {"0": 5, "1": 1},
              "重複の行は到達率を上げず、excess_rows に数える")
        check(measure(obs_full, tail=0)["reach_rate"] < 1.0, "区間の後ろの余裕（tail）が無いと、遅れて届く行を取りこぼす")

        # ★ 2 ブロック・block_end の 5 ms 後にマーカーが来る陽性対照。
        #   区間を「次の oracle 行」で切らないと、このマーカーの押下が前ブロックの最後の試行に
        #   数えられ、その試行の取りこぼし（2 送って 1 しか届かない）が隠れる（reach_rate が 1 になってしまう）。
        base2 = t0 + 100_000
        oracle2 = [
            {"kind": "header", "format": "oracle/1"},
            {"kind": "block_begin", "block_id": 0, "t_wall_ms": base2 - 50, "t_mono_ns": 0},
            {"kind": "trial_begin", "trial_id": "b0t1", "t_wall_ms": base2, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b0t1", "step": 0, "key": "a", "down": True, "t_wall_ms": base2, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b0t1", "step": 1, "key": "a", "down": False, "t_wall_ms": base2 + 20, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b0t1", "step": 2, "key": "a", "down": True, "t_wall_ms": base2 + 100, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b0t1", "step": 3, "key": "a", "down": False, "t_wall_ms": base2 + 120, "t_mono_ns": 0},
            {"kind": "trial_end", "trial_id": "b0t1", "t_wall_ms": base2 + 150, "t_mono_ns": 0},
            {"kind": "block_end", "block_id": 0, "t_wall_ms": base2 + 200, "t_mono_ns": 0},
            {"kind": "block_begin", "block_id": 1, "t_wall_ms": base2 + 205, "t_mono_ns": 0},
        ]
        marker_t = base2 + 200 + 5  # block_end の 5 ms 後
        oracle2.append({"kind": "marker", "block_id": 1, "seq": 0, "t_wall_ms": marker_t, "t_mono_ns": 0})
        oracle2 += [
            {"kind": "trial_begin", "trial_id": "b1t1", "t_wall_ms": base2 + 400, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b1t1", "step": 0, "key": "a", "down": True, "t_wall_ms": base2 + 400, "t_mono_ns": 0},
            {"kind": "sent", "trial_id": "b1t1", "step": 1, "key": "a", "down": False, "t_wall_ms": base2 + 420, "t_mono_ns": 0},
            {"kind": "trial_end", "trial_id": "b1t1", "t_wall_ms": base2 + 450, "t_mono_ns": 0},
            {"kind": "block_end", "block_id": 1, "t_wall_ms": base2 + 500, "t_mono_ns": 0},
        ]
        # 観測: b0t1 は 2 個送って 1 個しか届かない（本物の取りこぼし）。マーカーの押下は marker_t + 3 ms で届く。
        obs2 = [
            {"type": "meta", "format": "obs/1"},
            {"type": "key", "t": base2 + 3, "category": "alphabetic", "press": True},
            {"type": "key", "t": marker_t + 3, "category": "function", "press": True},
            {"type": "key", "t": base2 + 403, "category": "alphabetic", "press": True},
            {"type": "key", "t": base2 + 423, "category": "alphabetic", "press": False},
        ]
        op2 = os.path.join(tmp, "oracle2.jsonl")
        kp2 = os.path.join(tmp, "keys2b.jsonl")
        dump(op2, oracle2)
        dump(kp2, obs2)
        trials2, cuts2 = load_oracle(op2)
        r2 = analyze(trials2, cuts2, load_keys_only(kp2), 20, 300, set(DEFAULT_IGNORE))
        b0 = next(p for p in r2["per_trial"] if p["trial_id"] == "b0t1")
        check(b0["obs"] == 1 and b0["sent"] == 2, "次ブロックのマーカーの押下は前ブロックの最後の試行に数えない（b0t1: 送った %d・届いた %d）" % (b0["sent"], b0["obs"]))
        check(r2["reach_rate"] < 1.0, "区間を次の oracle 行で切ると、隠れていた取りこぼしが到達率に出る（%.2f）" % r2["reach_rate"])
        check(r2["outside_trials_rows"] == 1, "マーカーの押下はどの試行の区間にも入らない行に数える")

        # 入力の契約と終了コード。
        me = os.path.abspath(__file__)
        kp = os.path.join(tmp, "k.jsonl")
        out = os.path.join(tmp, "out.json")
        dump(kp, obs_full)
        p = subprocess.run([sys.executable, me, "--oracle", op, "--obs-keys", kp, "--out", out], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        check(p.returncode == 0 and data["reach_rate"] == 1.0, "CLI: 出力の JSON に到達率（exit %d）" % p.returncode)
        dump(kp, obs_full + [{"type": "x", "t": 1}])
        p = subprocess.run([sys.executable, me, "--oracle", op, "--obs-keys", kp, "--out", out + "2"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = p.stdout.decode("utf-8", "replace")
        check(p.returncode == 2 and not os.path.exists(out + "2") and "keys-only" in text, "keys-only でない行があれば拒否する（exit %d・出力を書かない）" % p.returncode)
        with open(kp, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"type":"meta","type":"meta2"}\n')
        p = subprocess.run([sys.executable, me, "--oracle", op, "--obs-keys", kp, "--out", out + "5"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "obs-keys に同じキーが 2 回ある行があれば拒否する（exit %d）" % p.returncode)
        dump(kp, obs_full)
        dump(op + "0", [{"kind": "header", "format": "oracle/1"}])
        p = subprocess.run([sys.executable, me, "--oracle", op + "0", "--obs-keys", kp, "--out", out + "3"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 1, "送った押下が 1 つも無ければ空振りで exit 1（exit %d）" % p.returncode)
        p = subprocess.run([sys.executable, me, "--oracle", os.path.join(tmp, "nothing"), "--obs-keys", kp, "--out", out + "4"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "oracle が開けなければ exit 2（exit %d）" % p.returncode)

    if fails:
        print("  ---- reach selftest 失敗 %d 件 ----" % len(fails))
        return 1
    print("  ---- reach selftest すべて緑 ----")
    return 0
# --- selftest end ---


def main(argv=None):
    ap = argparse.ArgumentParser(description="合成入力が観測部のフックに届くかを、key 行だけで確かめる")
    ap.add_argument("--selftest", action="store_true", help="陽性対照と陰性対照を回す")
    ap.add_argument("--oracle", help="実行器の出力（oracle/1）")
    ap.add_argument("--obs-keys", help="keys-only の観測（seal_obs.py の keys-out）")
    ap.add_argument("--out", help="結果の JSON の出力先")
    ap.add_argument("--pre-ms", type=int, default=20, help="試行の区間の前の余裕（既定 20）")
    ap.add_argument("--tail-ms", type=int, default=300, help="試行の区間の後ろの余裕（既定 300）")
    ap.add_argument("--ignore-keys", default=",".join(DEFAULT_IGNORE), help="数えない keyname のカンマ区切り（既定: 擬似キー）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.oracle and args.obs_keys and args.out):
        ap.error("--oracle / --obs-keys / --out がすべて要る")
    if args.pre_ms < 0 or args.tail_ms < 0:
        ap.error("--pre-ms / --tail-ms は 0 以上")
    ignore = set(k for k in args.ignore_keys.split(",") if k)
    try:
        trials, cuts = load_oracle(args.oracle)
        result = analyze(trials, cuts, load_keys_only(args.obs_keys), args.pre_ms, args.tail_ms, ignore)
    except InputError as e:
        print("reach: %s" % e, file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    rate = result["reach_rate"]
    print("試行 %d（区間の外の行 %d）・送った押下 %d・届いた %d・到達率 %s・多かった行 %d" % (
        result["trials_measured"], result["outside_trials_rows"], result["sent_presses"], result["reached"],
        "なし" if rate is None else "%.1f%%" % (100 * rate), result["excess_rows"]))
    print("届いた−送った の分布: %s" % json.dumps(result["diff_distribution"], separators=(",", ":")))
    if rate is None:
        print("reach: 集計できる送信が 1 つも無い（oracle に完結した試行と押下があるか確かめること）", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
