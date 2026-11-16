"""R8 の通しの検査: 合成の 4 人分の作業フォルダで conduct・prewin・auc の run を最後まで通し、公開版に漏れが無い。
追加の中間は repo の fixture に本物の gse-replay を当てて作る。usage: e2e_test.py <gse-replay>"""
import hashlib
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auc  # noqa: E402
import build_cr  # noqa: E402
import conduct  # noqa: E402
import prewin  # noqa: E402

replay = sys.argv[1]
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
with tempfile.TemporaryDirectory() as td:
    # 追加の中間（本物の replay・fixture）
    fx = os.path.join(root, "src-tauri/tests/fixtures/instrument_rich.ndjson")
    dst = os.path.join(td, "x.json")
    build_cr.build_extra(replay, fx, dst, 7)
    x = json.load(open(dst))
    assert x["day_number"] == 7 and x["feat"] and len(x["ime_state"]) == 5 and x["plain_sha256"] == build_cr.sha256(fx), x.keys()
    assert all(len(r) == 3 for r in x["feat"]) and all(len(r) == 3 for r in x["ime_state"])
    assert x["ime_state"][:2] == [[1700000100010, 0, 0], [1700000101100, 1, 1]], x["ime_state"][:2]
    # 合成の 4 人
    rng = random.Random(5)
    table = {"odd_names": 0, "held_out": 0, "people": {}}
    for k, pid in enumerate(("P006", "P009", "P011", "P013")):
        rows = []
        os.makedirs(os.path.join(td, pid))
        nfile = 8 if pid == "P013" else 12  # 同じ日に 2 本ずつ。D だけ 4 日（下限の 5 日に届かない）
        for i in range(nfile):
            d, xx = auc.synth_file(rng, 12, k == 0, False, i, raw=True)
            d["types"] = {"key": len(d["keys"]), "focus_transition": len(d["focus"]), "pointer_bin": 0}
            sha = hashlib.sha256(f"{pid}{i}".encode()).hexdigest()
            d["input_sha256"] = sha
            xx.update({"plain_sha256": sha, "day_number": i + 1 if i != 3 else 9})
            ip, xp = os.path.join(td, pid, f"i{i}.json"), os.path.join(td, pid, f"x{i}.json")
            json.dump(d, open(ip, "w"))
            json.dump(xx, open(xp, "w"))
            rows.append({"inter": ip, "extra": xp, "date": f"202611{i // 2 + 10:02d}", "plain_sha256": sha,
                         "app_version": "0.1.99", "hmm_version": "0.5.0"})
        table["people"][pid] = {"symbol": "ABCD"[k], "files": rows}
    json.dump(table, open(os.path.join(td, "files.json"), "w"))
    out = os.path.join(td, "out")
    os.makedirs(out)
    conduct.run(td, os.path.join(out, "conduct.json"))
    prewin.run(td, "3", os.path.join(out, "prewin.json"))
    auc.run(td, "3", os.path.join(out, "auc.json"))
    c = json.load(open(os.path.join(out, "conduct.json")))
    assert c["people"]["A"]["files_used"] == 10 and c["people"]["A"]["calendar_days"] == 5, c["people"]["A"]  # 12・6 を丸め
    assert c["people"]["A"]["missing_day_numbers"] == 0 and c["people"]["A"]["max_day_number"] == 10, c["people"]["A"]
    # 日の単位: 6 日（丸めて 5）。本の単位なら 12（丸めて 10）になる
    pw = json.load(open(os.path.join(out, "prewin.json")))
    assert pw["people"]["A"]["days_used"] == 5, pw["people"]["A"]
    a = json.load(open(os.path.join(out, "auc.json")))
    assert a["people"]["A"]["main"]["days_with_stalls"] == 5, a["people"]["A"]["main"]
    assert a["people"]["A"]["main"]["ci95"]["delta"][0] > 0, a["people"]["A"]["main"]  # A だけ停滞の手前に遷移
    assert "auc_K" in a["people"]["B"]["main"] and "early_5s" in a["people"]["B"]
    assert a["people"]["D"]["main"]["status"] == "数が足りない" and "auc_K" not in a["people"]["D"]["main"], a["people"]["D"]
    for f in os.listdir(out):
        t = open(os.path.join(out, f)).read()
        assert "P00" not in t and "202611" not in t and "0.1.99" not in t, f
    assert os.path.exists(os.path.join(td, "auc.full.json"))
print("e2e test ok")
