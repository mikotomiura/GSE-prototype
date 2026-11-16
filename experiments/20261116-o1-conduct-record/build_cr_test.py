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
    # 逸脱 1: 知らない行の型だけを除いた写しで回し、写しの停滞の始まりが元の中間と一致しなければ止める
    fake = os.path.join(td, "fake_replay")
    open(fake, "w").write(f"""#!{sys.executable}
import json, sys
text = open(sys.argv[1]).read()
for t in ("probe_frame", "day_question"):
    if '"type": "' + t + '"' in text:
        sys.stderr.write("Error: unknown variant `" + t + "`, expected one of `meta`, `key` at line 3 column 9\\n")
        sys.exit(1)
if "--features" in sys.argv:
    print(json.dumps({{"rows": [{{"stall_onset": {{"is_onset": True, "s_ms": 10, "t0_ms": 20}}}},
                               {{"stall_onset": {{"is_onset": False, "s_ms": None, "t0_ms": None}}}}]}}))
else:
    print(json.dumps([{{"timestamp": 1, "p_stuck": 0.1, "ewma_x": 0.2}}]))
""")
    os.chmod(fake, 0o755)
    nd = os.path.join(td, "x.ndjson")
    open(nd, "w").write('{"type": "meta"}\n{"type": "key", "t": 1}\n{"type": "probe_frame", "t": 2}\n'
                        '{"type": "day_question", "t": 3}\n{"type": "probe_frame", "t": 4}\n')
    feat, stripped = bc.replay_feat(fake, nd, [[10, 20]], td)
    assert feat == [[1, 0.1, 0.2]] and stripped == {"probe_frame": 2, "day_question": 1}, (feat, stripped)
    assert not [f for f in os.listdir(td) if f.startswith("stripped-")]  # 一時の写しは消す
    try:
        bc.replay_feat(fake, nd, [[10, 21]], td)
        raise AssertionError("停滞の始まりの食い違いで止めなかった")
    except RuntimeError as e:
        assert str(e) == "onsets"
    assert not [f for f in os.listdir(td) if f.startswith("stripped-")]
    ok = os.path.join(td, "ok.ndjson")
    open(ok, "w").write('{"type": "key", "t": 1}\n')
    assert bc.replay_feat(fake, ok, [], td) == ([[1, 0.1, 0.2]], {})  # 知らない型が無ければ写しを作らない
print("build_cr test ok")
