"""R1 の検査: 入力の digest の作り方・取り置きを外すこと・塩の照合。"""
import hashlib
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_cr as bc  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    rec = os.path.join(td, "recv")
    for pid, names in (("P009", ["P009_o1day01_gse_o1_20261101_083029.age", "P009_o1day02_gse_o1_20261101_083030.age"]),
                       ("P006", ["P006_o1day01_gse_o1_20261101_083030.age"])):
        os.makedirs(os.path.join(rec, pid))
        for n in names:
            open(os.path.join(rec, pid, n), "wb").write(n.encode())
    dig, rows = bc.input_digest(rec)
    want = hashlib.sha256("".join(hashlib.sha256(p.split("/")[1].encode()).hexdigest() + "  " + p + "\n"
                                  for p in sorted(r[1] for r in rows)).encode()).hexdigest()
    assert dig == want and [r[1] for r in rows] == sorted(r[1] for r in rows) and len(rows) == 3, rows
    # 中身を変えずに改名すると digest が変わる
    os.rename(os.path.join(rec, "P006", "P006_o1day01_gse_o1_20261101_083030.age"),
              os.path.join(rec, "P006", "P006_o1day02_gse_o1_20261101_083030.age"))
    assert bc.input_digest(rec)[0] != dig
    os.rename(os.path.join(rec, "P006", "P006_o1day02_gse_o1_20261101_083030.age"),
              os.path.join(rec, "P006", "P006_o1day01_gse_o1_20261101_083030.age"))
    bc.open_hold()
    use, odd, held = bc.build_n4.select(rec)
    assert held == 0 and sum(len(v) for v in use.values()) == 3, (use, held)
    # 塩: n4 の来歴と違えば止める
    n4w, w = os.path.join(td, "n4"), os.path.join(td, "w")
    os.makedirs(n4w)
    os.makedirs(w)
    open(os.path.join(n4w, "symbol_salt"), "w").write("abc")
    prov = os.path.join(td, "prov.json")
    json.dump({"symbol_salt_sha256": hashlib.sha256(b"abc").hexdigest()}, open(prov, "w"))
    bc.copy_salt(n4w, prov, w)
    assert open(os.path.join(w, "symbol_salt")).read() == "abc"
    json.dump({"symbol_salt_sha256": "0" * 64}, open(prov, "w"))
    try:
        bc.copy_salt(n4w, prov, os.path.join(td, "n4"))
        raise AssertionError("塩の照合が止めなかった")
    except SystemExit:
        pass
print("build_cr test ok")
