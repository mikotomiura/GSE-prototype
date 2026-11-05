"""O1 の 4 人の .age を復号し、停滞の分解の build_o1.py で中間を作る（conditions.md N1）。

usage: build_n4.py <receiving_dir> <gse-unpack> <identity> <gse-replay> <work_dir>
記号は repo の外の塩（<work_dir>/symbol_salt・無ければ作る・権限 600）で付ける（判断 8）。repo の SEED では付けない
（SEED と P-ID の並びは repo にあるので、それで付けると対応を誰でも計算し直せる）。
出力（すべて repo の外の <work_dir>）:
  plain/<P-ID>/<stem>.ndjson   復号した平文（削除台帳 A-4 の置き場）
  inter/<P-ID>/<stem>.json     build_o1.py の中間
  files.json                   人ごとのファイルの表（中間の場所・平文の SHA-256・meta の版）
  symbols.json                 記号と P-ID の対応
本文は読まない。meta 行は app_version と hmm_version だけを読む。標準出力に P-ID・ファイル名を出さない。
"""
import hashlib
import json
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../20261102-stall-decomposition/o1"))
import build_o1  # noqa: E402

NAME = re.compile(r"^(P\d{3})_o1day\d{2}_gse_o1_(\d{8})_(\d{6})\.age$")
HOLD_FROM = "20261101_083030"
SELF_PID = "P009"           # 研究者本人（decisions.md 判断 1）。取り置きは本人だけ（判断 3）
UNPACK_SHA = "c9475ded4858b0336c21754839f1389e2169284dea89d3402a87b841a4fdc282"
PIDS = ("P006", "P009", "P011", "P013")


def salt(work):
    p = os.path.join(work, "symbol_salt")
    if not os.path.exists(p):
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, os.urandom(32).hex().encode())
        os.close(fd)
    return open(p).read().strip()


def symbols(pids, seed):
    xs = sorted(pids)
    random.Random(seed).shuffle(xs)
    return {p: "ABCD"[i] for i, p in enumerate(xs)}


def select(receiving):
    """名前の規則（N1）で使う .age を選ぶ。戻り値: ({pid: [(stem, path)]}, 形の合わない数, 取り置きの数)"""
    use, odd, held = {}, 0, 0
    for pid in sorted(os.listdir(receiving)):
        d = os.path.join(receiving, pid)
        if not os.path.isdir(d):
            odd += 1  # 人のフォルダに入っていないファイル
            continue
        for fn in sorted(os.listdir(d)):
            m = NAME.match(fn)
            if not m or m.group(1) != pid:
                odd += 1
                continue
            if pid == SELF_PID and f"{m.group(2)}_{m.group(3)}" >= HOLD_FROM:
                held += 1
                continue
            use.setdefault(pid, []).append((fn[:-len(".age")], os.path.join(d, fn), m.group(2)))
    return use, odd, held


def meta(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(o, dict) and o.get("type") == "meta":
                return {"app_version": o.get("app_version"), "hmm_version": o.get("hmm_version")}
    return {"app_version": None, "hmm_version": None}


def main(receiving, unpack, identity, replay, work):
    if build_o1.sha256(unpack) != UNPACK_SHA:
        sys.exit("gse-unpack の SHA-256 が違う")
    use, odd, held = select(receiving)
    if tuple(sorted(use)) != PIDS:
        sys.exit("受け取りフォルダの人が 4 人（条件の P-ID）でない")
    sym = symbols(PIDS, salt(work))
    table = {"odd_names": odd, "held_out": held, "people": {}}
    for pid, items in sorted(use.items()):
        pdir = os.path.join(work, "plain", pid)
        idir = os.path.join(work, "inter", pid)
        os.makedirs(pdir, exist_ok=True)
        os.makedirs(idir, exist_ok=True)
        rows = []
        for stem, age, date in items:
            nd = os.path.join(pdir, stem + ".ndjson")
            ok = nd + ".ok.json"  # 復号が済み、生キーの行が 0 だった印（平文の SHA-256 つき）
            reuse = False
            if os.path.exists(nd) and os.path.exists(ok):
                try:
                    mk = json.load(open(ok))
                except (OSError, ValueError):
                    mk = {}  # 壊れた印は無いのと同じに扱い、復号し直す
                reuse = (mk.get("raw_key_lines") == 0 and mk.get("plain_sha256") == build_o1.sha256(nd)
                         and mk.get("age_sha256") == build_o1.sha256(age))
            if not reuse:
                for x in (nd, ok):
                    if os.path.exists(x):
                        os.remove(x)
                r = subprocess.run([unpack, "--input", age, "--identity", identity, "--out", pdir],
                                   capture_output=True, text=True)
                # unpack.rs は生キー由来の行が 1 以上のときだけ stderr に "raw key field" を出す（平文は書き出した後）
                if r.returncode != 0 or "raw key field" in r.stderr or not r.stdout.startswith("age-decrypted ") \
                        or not os.path.exists(nd):
                    if os.path.exists(nd):
                        os.remove(nd)
                    sys.exit(f"復号に失敗したか、生キー由来の行がある（人 {sym[pid]}）")
                json.dump({"raw_key_lines": 0, "plain_sha256": build_o1.sha256(nd), "age_sha256": build_o1.sha256(age)},
                          open(ok, "w"))
            try:
                build_o1.build(replay, idir, nd)
            except (Exception, SystemExit):
                # build_o1 の失敗の文にはファイル名が入るので、記号だけで止める
                sys.exit(f"中間の作成に失敗した（人 {sym[pid]}）")
            try:
                rows.append({"inter": os.path.join(idir, stem + ".json"), "date": date,
                             "plain_sha256": build_o1.sha256(nd), **meta(nd)})
            except OSError:
                sys.exit(f"平文が読めない（人 {sym[pid]}）")
        table["people"][pid] = {"symbol": sym[pid], "files": rows}
        print(f"人 {sym[pid]}: {len(rows)} 本", file=sys.stderr)
    json.dump(table, open(os.path.join(work, "files.json"), "w"), indent=1)
    json.dump(sym, open(os.path.join(work, "symbols.json"), "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
