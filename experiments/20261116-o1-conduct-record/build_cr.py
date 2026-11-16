"""O1 の全受領を復号し、n4 と同じ中間と追加の中間を作る（conditions.md R1）。

usage: build_cr.py <receiving_dir> <gse-unpack> <identity> <gse-replay> <work_dir> <n4_work_dir> <n4_provenance_json>
n4 の build_n4.main を、取り置きを外して呼ぶ（コードは変えない・HOLD_FROM を全期間の外に替える）。
記号は n4 の塩を写して付ける（判断 4）。追加の中間:
  extra/<P-ID>/<stem>.json  {"plain_sha256", "day_number", "feat": [[t, p_stuck, ewma_x]], "ime_state": [[t, on, active]],
                             "ime_shadow": [t]}
本文は読まない（ime 行は時刻と真偽だけ）。標準出力に P-ID・ファイル名を出さない。
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
N4 = os.path.join(HERE, "../20261103-o1-n4-pause-stall")
sys.path.insert(0, N4)
import build_n4  # noqa: E402

DAYNUM = re.compile(r"_o1day(\d{2})_")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_digest(receiving):
    """R1: .age を相対パスの昇順に並べ、「SHA-256 + 空白 2 つ + 相対パス」を 1 行ずつ（末尾に改行）連結した列の SHA-256 と表。
    パスを入れるので、並びを変えない改名でも digest が変わる。"""
    paths = []
    for root, _, files in os.walk(receiving):
        for fn in files:
            if fn.endswith(".age"):
                paths.append(os.path.relpath(os.path.join(root, fn), receiving))
    paths.sort()
    rows = [(sha256(os.path.join(receiving, p)), p) for p in paths]
    return hashlib.sha256("".join(f"{s}  {p}\n" for s, p in rows).encode()).hexdigest(), rows


def copy_salt(n4_work, n4_prov, work):
    src = os.path.join(n4_work, "symbol_salt")
    want = json.load(open(n4_prov))["symbol_salt_sha256"]
    if sha256(src) != want:
        sys.exit("n4 の塩の SHA-256 が n4 の来歴と違う")
    dst = os.path.join(work, "symbol_salt")
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o600)
    if sha256(dst) != want:
        sys.exit("写した塩の SHA-256 が n4 の来歴と違う")


def ime_rows(path):
    st, sh = [], []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"ime_' not in line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(o, dict):
                continue
            if o.get("type") == "ime_state":
                st.append([o["t"], 1 if o.get("on") else 0, 1 if o.get("active") else 0])
            elif o.get("type") == "ime_shadow":
                sh.append(o["t"])
    return sorted(st), sorted(sh)


UNKNOWN = re.compile(r"unknown variant `([a-z_0-9]+)`")
MAX_STRIP = 10


def strip_types(src, dst, types):
    """src から type が types のどれかの行を除いて dst に写す。除いた行の数を型ごとに返す（中身は読まない）。"""
    n = {t: 0 for t in types}
    with open(src, encoding="utf-8", errors="replace") as fi, open(dst, "w", encoding="utf-8") as fo:
        for line in fi:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                fo.write(line)
                continue
            if isinstance(o, dict) and o.get("type") in n:
                n[o["type"]] += 1
                continue
            fo.write(line)
    return n


def replay_feat(replay, plain, onsets, tmpdir):
    """逸脱 1（notes・研究者の決定 2026-11-16）: 固定した replay が知らない行の型（版 0.1.41 の probe_frame など）で
    止まったら、その型の行だけを除いた一時の写しで回す。写しの --features の停滞の始まりが元の本の中間（onsets）と
    全件一致しなければ止める。戻り値: (feat の列, {除いた型: 行の数})。"""
    r = subprocess.run([replay, plain], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode == 0:
        return [[x["timestamp"], x["p_stuck"], x["ewma_x"]] for x in json.loads(r.stdout)], {}
    types = []
    tmp = os.path.join(tmpdir, "stripped.ndjson")
    try:
        for _ in range(MAX_STRIP):
            m = UNKNOWN.search(r.stderr)
            if not m or m.group(1) in types:
                raise RuntimeError("replay")
            types.append(m.group(1))
            counts = strip_types(plain, tmp, types)
            r = subprocess.run([replay, tmp], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if r.returncode == 0:
                break
        else:
            raise RuntimeError("replay")
        feat = [[x["timestamp"], x["p_stuck"], x["ewma_x"]] for x in json.loads(r.stdout)]
        fr = subprocess.run([replay, tmp, "--features"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if fr.returncode != 0:
            raise RuntimeError("replay")
        got = [[x["stall_onset"]["s_ms"], x["stall_onset"]["t0_ms"]] for x in json.loads(fr.stdout)["rows"]
               if x["stall_onset"]["is_onset"]]
        if got != [list(o) for o in onsets]:
            raise RuntimeError("onsets")
        return feat, counts
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def build_extra(replay, plain, dst, day_number, onsets=None, tmpdir=None):
    digest = sha256(plain)
    if os.path.exists(dst):
        try:
            old = json.load(open(dst))
            if old.get("plain_sha256") == digest and old.get("replay_sha256") == sha256(replay):
                return
        except (OSError, ValueError):
            pass
    feat, stripped = replay_feat(replay, plain, onsets or [], tmpdir or os.path.dirname(dst))
    st, sh = ime_rows(plain)
    if sha256(plain) != digest:
        raise RuntimeError("changed")
    json.dump({"plain_sha256": digest, "replay_sha256": sha256(replay), "day_number": day_number,
               "stripped_types_for_feat": stripped, "feat": sorted(feat), "ime_state": st, "ime_shadow": sh},
              open(dst, "w"))


def open_hold():
    """R1: n4 の取り置き（本人の 20261101_083030 以降）を外す（判断 2）。"""
    build_n4.HOLD_FROM = "99999999_999999"


def main(receiving, unpack, identity, replay, work, n4_work, n4_prov, want_digest):
    os.makedirs(work, exist_ok=True)
    os.chmod(work, 0o700)
    dig, rows = input_digest(receiving)
    if dig != want_digest:
        sys.exit("入力の digest が条件と違う（R1）")
    with open(os.path.join(work, "inputs.txt"), "w") as f:
        f.writelines(f"{s}  {p}\n" for s, p in rows)  # digest と同じ書式（この表から digest を作り直せる）
    copy_salt(n4_work, n4_prov, work)
    open_hold()
    build_n4.main(receiving, unpack, identity, replay, work)
    table = json.load(open(os.path.join(work, "files.json")))
    if table["held_out"] != 0:
        sys.exit("取り置きが残っている")
    for pid, p in table["people"].items():
        xdir = os.path.join(work, "extra", pid)
        os.makedirs(xdir, exist_ok=True)
        for f in p["files"]:
            stem = os.path.basename(f["inter"])[:-len(".json")]
            plain = os.path.join(work, "plain", pid, stem + ".ndjson")
            m = DAYNUM.search(stem)
            if not m:
                sys.exit(f"日番号が読めない（人 {p['symbol']}）")
            dst = os.path.join(xdir, stem + ".json")
            try:
                onsets = json.load(open(f["inter"]))["onsets"]
                build_extra(replay, plain, dst, int(m.group(1)), onsets, work)
            except Exception:  # noqa: BLE001  失敗の文にファイル名が入りうるので記号だけで止める
                sys.exit(f"追加の中間の作成に失敗した（人 {p['symbol']}）")
            f["extra"] = dst
    json.dump(table, open(os.path.join(work, "files.json"), "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
