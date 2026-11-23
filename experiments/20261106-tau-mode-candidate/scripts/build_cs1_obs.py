"""CS1 2021 年版の中間を、B と同じ 8 列の feat 行と補完の受け入れの時刻を残す形で作り直す（conditions.md の D1）。

使い方:
  python3 -I build_cs1_obs.py <keystrokes.csv> <gse-replay> <holdout.json> <work_dir> <jobs>
  python3 -I build_cs1_obs.py --selftest
俯瞰の build_cs1.py（experiments/20261104-cs1-landscape/scripts/）をそのまま読み込み、変えるのは 2 つだけ:
  - feat 行を [[t, p_flow, p_inc, p_stuck, ewma_x, ewma_y, obs, alpha], ...] で残す。
  - X-Action の X-Metadata が "Choose Lookup Item" か "Choose Lookup Item Replace" に完全一致する行を、
    出来事の表に "lookup-accept" として残す（俯瞰ではほかの名前と一緒に "ide-action" だった）。
出力（repo の外）は俯瞰と同じ形（u<番号>.json・units.json・writers.json・build_summary.json）。
InsertText は長さだけを使う（俯瞰と同じ）。キーの文字・挿入と削除の文字・貼り付けた文字は書き出さない。
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../20261104-cs1-landscape/scripts"))
import build_cs1 as bc  # noqa: E402

ACCEPT = ("Choose Lookup Item", "Choose Lookup Item Replace")
_map_orig = bc.map_2021


def map_2021_obs(row):
    r = _map_orig(row)
    if row["EventType"] == "X-Action" and r == ("ev", "ide-action") and row["X-Metadata"] in ACCEPT:
        return ("ev", "lookup-accept")
    return r


def one(args):
    """bc.one と同じ手順。違いは feat の列と、課題の中の出来事の表に lookup-accept が入ること。"""
    idx, items, replay, work = args
    out = os.path.join(work, "u%05d.json" % idx)
    items.sort(key=lambda x: (x[0], x[1]))
    blocks_raw = bc.split_blocks(items)
    all_keys, all_feat, blocks, few, kept_ev = [], [], [], 0, []
    with tempfile.TemporaryDirectory(dir=work) as td:
        for b in blocks_raw:
            presses = [(t, v) for t, _, k, v in b if k == "key"]
            if len(presses) < 2:
                few += 1
                continue
            nd, fp = os.path.join(td, "b.ndjson"), os.path.join(td, "b_feat.json")
            bc.write_ndjson(nd, presses[0][0], bc.key_rows(presses))
            with open(fp, "w") as f:
                r = subprocess.run([replay, nd], stdout=f, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
            if r.returncode != 0:
                return {"status": "replay_failed"}
            all_feat += json.load(open(fp))
            all_keys += presses
            kept_ev += [[t, v] for t, _, k, v in b if k == "ev"]
            blocks.append([presses[0][0], presses[-1][0]])
            os.remove(nd)
            os.remove(fp)
        if len(all_keys) < 2:
            return {"status": "few_presses", "blocks_few": few}
        nd, fp, wf = (os.path.join(td, n) for n in ("u.ndjson", "u_feat.json", "u_withfeat.ndjson"))
        bc.write_ndjson(nd, all_keys[0][0], bc.key_rows(all_keys))
        json.dump(all_feat, open(fp, "w"))
        subprocess.run([sys.executable, "-I", bc.ADD_FEAT, nd, fp, wf], check=True)
        ft = subprocess.run([replay, wf, "--features"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL)
        if ft.returncode != 0:
            if b"time span too large" in ft.stderr:
                return {"status": "span_too_long", "span_days": (all_keys[-1][0] - all_keys[0][0]) / 86_400_000}
            return {"status": "features_failed"}
        d = json.loads(ft.stdout)
    onsets = [[x["stall_onset"]["s_ms"], x["stall_onset"]["t0_ms"], x["stall_onset"]["theta_person_ms"],
               x["stall_onset"]["theta_sample_n"]] for x in d["rows"] if x["stall_onset"].get("is_onset")]
    rec = {"keys": [list(k) for k in all_keys],
           "feat": [[x["timestamp"], x["p_flow"], x["p_inc"], x["p_stuck"], x["ewma_x"], x["ewma_y"], x["obs"], x["alpha"]]
                    for x in all_feat],
           "onsets": onsets,
           "observed_intervals": [[iv["a_ms"], iv["b_ms"]] for iv in d["provenance"]["observed_intervals"]],
           "blocks": blocks,
           "events": kept_ev}
    with open(out + ".tmp", "w") as f:
        json.dump(rec, f, separators=(",", ":"))
    os.replace(out + ".tmp", out)
    return {"status": "ok", "blocks": len(blocks), "blocks_few": few, "onsets": len(onsets),
            "accept": sum(1 for e in kept_ev if e[1] == "lookup-accept")}


def main():
    path, replay, hold_p, work, jobs = sys.argv[1:6]
    bc.map_2021 = map_2021_obs  # read_units が年版の写像をここで選ぶ
    bc.one = one
    # bc.main は sys.argv を読むので、同じ形に並べ替えて呼ぶ（--limit は使わない）
    sys.argv = [sys.argv[0], "2021", path, replay, hold_p, work, jobs]
    bc.main()
    # 受け入れの総数（名前の取り違えの見張り）。書き手ごとには出さない
    n_acc = n_onsets = n_feat = 0
    for f in sorted(os.listdir(work)):
        if f.startswith("u") and f.endswith(".json") and f != "units.json":
            d = json.load(open(os.path.join(work, f)))
            n_acc += sum(1 for e in d["events"] if e[1] == "lookup-accept")
            n_onsets += len(d["onsets"])
            n_feat += len(d["feat"])
    p = os.path.join(work, "build_summary.json")
    s = json.load(open(p))
    s.update(lookup_accept_total=n_acc, onsets_total=n_onsets, feat_rows_total=n_feat)
    json.dump(s, open(p, "w"), indent=1)
    print(json.dumps(dict(lookup_accept_total=n_acc, onsets_total=n_onsets, feat_rows_total=n_feat)))


def selftest():
    r = lambda **kw: {"EventType": "X-Action", "EditType": "", "X-Keystroke": "nan", "X-Metadata": "nan",  # noqa: E731
                      "InsertText": "", **kw}
    assert map_2021_obs(r(**{"X-Metadata": "Choose Lookup Item"})) == ("ev", "lookup-accept")
    assert map_2021_obs(r(**{"X-Metadata": "Choose Lookup Item Replace"})) == ("ev", "lookup-accept")
    assert map_2021_obs(r(**{"X-Metadata": "Undo Choose Lookup Item"})) == ("ev", "ide-action")
    assert map_2021_obs(r(**{"X-Metadata": "Choose Lookup Item "})) == ("ev", "ide-action")  # 完全一致だけ
    assert map_2021_obs(r(**{"X-Metadata": "Tab"})) == ("key", "tab")
    assert map_2021_obs(r(**{"X-Metadata": "Left"})) == ("key", "navigation")
    assert map_2021_obs(r(EventType="X-Keystroke", **{"X-Metadata": "a"})) == ("key", "alphabetic")
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
