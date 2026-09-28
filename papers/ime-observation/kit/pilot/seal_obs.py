#!/usr/bin/env python3
# kit: selftest
"""単体ロガーの出力（obs/1）から meta 行と key 行だけを取り出し、元のファイルを封印する（Python 標準ライブラリだけ）。

  seal_obs.py --obs FILE --keys-out FILE --sealed-dir DIR   封印する（元のファイルは DIR へ移り、FILE の場所からは消える）
  seal_obs.py --selftest                                    陽性対照と陰性対照（速い既定）

較正パイロットは ImeShadow の行を見ない・数えない・突き合わせない（精度の実測ではないので、プロトコルを凍結する前に
値を見てはならない）。そのために、パイロットの解析は封印の後に出る keys-out だけを読む。

規則は**許可リスト**である（捨てる行の種類を名指しせず、残す行の種類だけを名指す）:
  * 残す行 = 1 行目の meta と、key 行。それ以外の行は、種類を問わず keys-out に書かない。
  * meta 行は、ヘッダのキー（type / format / os / logger_version / manifest_sha256 / capabilities）だけを残し、
    capabilities の名前も key だけを残す（ImeShadow の名前が meta にも残らないように）。

⚠️ 出力（標準出力・seal.json・エラーメッセージ）に、捨てた行の情報（行数・値・行番号・種類）を出さない。
   出すのは、元のファイル全体の SHA-256・バイト数（プロトコルが記録を求める）と、残した key 行の数だけ。
   ⚠️ 元のバイト数と残した行のバイト数の差から、捨てた行の**バイト数の合計**は逆算できる（行数・値は分からない）。
⚠️ 元のファイルを開く道具は作らない。封印を開けてよいのは、プロトコルを凍結した後の解析パイプラインだけ。

読めない行（JSON Lines として不正）・1 行目が meta でない・meta が 2 つ以上のファイルは、何も動かさずに拒否する
（exit 1）。keys-out が既にある・封印先に同名のファイルか seal.json が既にあるときも拒否する。
exit 0 = 封印した / 1 = 拒否（元のファイルは動かしていない。封印後の照合が崩れたときだけ例外で、メッセージが言う）/ 2 = 使い方の誤り。
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

META_KEYS = ("type", "format", "os", "logger_version", "manifest_sha256", "capabilities")
CAP_GROUPS = ("unconditional", "threshold_gated", "config_gated")
KEEP_CAPABILITIES = ("key",)


class Refused(Exception):
    """封印しない理由（メッセージに、捨てる行の情報を入れないこと）。"""


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _meta_line(obj):
    """meta 行を許可リストで作り直す（ヘッダのキーと、capabilities の key だけを残す）。"""
    caps = obj.get("capabilities")
    if not isinstance(caps, dict):
        raise Refused("meta の capabilities が object ではない")
    kept_caps = {}
    for group in CAP_GROUPS:
        names = caps.get(group)
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise Refused("meta の capabilities が文字列の配列ではない")
        kept_caps[group] = [n for n in names if n in KEEP_CAPABILITIES]
    out = {k: obj[k] for k in META_KEYS if k in obj}
    out["capabilities"] = kept_caps
    return _compact(out)


def seal(obs, keys_out, sealed_dir):
    """封印して、標準出力に出してよい要約（dict）を返す。拒否は Refused。"""
    if not os.path.isfile(obs):
        raise Refused("--obs がファイルではない")
    if os.path.exists(keys_out):
        raise Refused("--keys-out が既にある（上書きしない）")
    part = keys_out + ".part"
    if os.path.exists(part):
        raise Refused("--keys-out の作業ファイル（.part）が既にある")
    target = os.path.join(sealed_dir, os.path.basename(obs))
    seal_json = os.path.join(sealed_dir, "seal.json")
    if os.path.abspath(target) == os.path.abspath(obs):
        raise Refused("--obs は既に封印先の中にある")
    if os.path.exists(target) or os.path.exists(seal_json):
        raise Refused("封印先に同名のファイルか seal.json が既にある（上書きしない）")

    h = hashlib.sha256()
    nbytes = 0
    kept = 0
    seen_meta = False
    try:
        with open(obs, "rb") as src, open(part, "wb") as dst:
            for raw in src:
                h.update(raw)
                nbytes += len(raw)
                body = raw.rstrip(b"\r\n")
                if not body.strip():
                    continue
                try:
                    obj = json.loads(body.decode("utf-8"))
                except ValueError:  # UnicodeDecodeError も ValueError
                    raise Refused("JSON Lines として読めない行がある")
                if not isinstance(obj, dict):
                    raise Refused("JSON Lines として読めない行がある")
                kind = obj.get("type")
                if not seen_meta and kind != "meta":
                    raise Refused("1 行目が meta ではない")
                if kind == "meta":
                    if seen_meta:
                        raise Refused("meta が 2 つ以上ある")
                    seen_meta = True
                    dst.write((_meta_line(obj) + "\n").encode("utf-8"))
                elif kind == "key":
                    dst.write(body + b"\n")
                    kept += 1
        if not seen_meta:
            raise Refused("meta 行が無い")
    except BaseException:
        if os.path.exists(part):
            os.remove(part)
        raise

    sha = h.hexdigest()
    os.rename(part, keys_out)
    try:
        os.makedirs(sealed_dir, exist_ok=True)
        shutil.move(obs, target)
    except OSError as e:
        os.remove(keys_out)  # 元のファイルは動いていない。次の試行が「keys-out が既にある」で止まらないよう戻す
        raise Refused("封印先へ移せなかった（%s）" % e.__class__.__name__)
    after = _sha256_file(target)
    if after != sha:
        raise RuntimeError("封印後の SHA-256 が読んだときと一致しない（元の sha256=%s）。封印先を確かめること" % sha)
    summary = {
        "sealed_file": os.path.basename(obs),
        "sha256": sha,
        "bytes": nbytes,
        "sealed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "keys_out": os.path.basename(keys_out),
        "keys_out_sha256": _sha256_file(keys_out),
        "kept_key_rows": kept,
    }
    with open(seal_json, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


# --- selftest begin ---
def _selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    validator = os.path.join(here, "..", "formats", "validate_logs.py")
    me = os.path.abspath(__file__)
    fails = []

    def check(ok, what):
        print("  %s %s" % ("✅" if ok else "❌", what))
        if not ok:
            fails.append(what)

    meta = ('{"type":"meta","format":"obs/1","os":"macos","logger_version":"0.1.0",'
            '"manifest_sha256":"' + "0" * 64 + '","capabilities":{"unconditional":["key"],'
            '"threshold_gated":[],"config_gated":["ime_shadow"]}}')
    good = [
        meta,
        '{"type":"key","t":10,"category":"alphabetic","press":true}',
        '{"type":"ime_shadow","t":20,"dwell_ms":987654,"nav":1,"abandon":false}',
        '{"type":"key","t":30,"category":"space","press":true}',
        '{"type":"ime_shadow","t":40,"dwell_ms":987655,"nav":0,"abandon":true}',
        '{"type":"ime_shadow","t":50,"dwell_ms":987656,"nav":2,"abandon":false}',
        '{"type":"future_row","t":60,"x":1}',
    ]
    leaks = ("ime_shadow", "98765")

    def run(obs, keys, sealed):
        p = subprocess.run([sys.executable, me, "--obs", obs, "--keys-out", keys, "--sealed-dir", sealed],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode("utf-8", "replace")

    def write(path, lines, crlf=False):
        with open(path, "wb") as f:
            f.write((("\r\n" if crlf else "\n").join(lines) + ("\r\n" if crlf else "\n")).encode("utf-8"))

    with tempfile.TemporaryDirectory() as tmp:
        # 陽性: 許可リストで残す。捨てた行の情報が出力に出ない。元のファイルは封印先へ移り、SHA-256 が一致する。
        obs = os.path.join(tmp, "obs.jsonl")
        keys = os.path.join(tmp, "keys.jsonl")
        sealed = os.path.join(tmp, "sealed")
        write(obs, good)
        orig_sha = _sha256_file(obs)
        orig_bytes = os.path.getsize(obs)
        rc, out = run(obs, keys, sealed)
        check(rc == 0, "封印できる（exit 0）")
        with open(keys, encoding="utf-8") as f:
            kept = f.read().splitlines()
        check(len(kept) == 3 and kept[0].startswith('{"type":"meta"'), "keys-out は meta 1 行 + key 2 行だけ（%d 行）" % len(kept))
        check(sum(1 for l in kept if l.startswith('{"type":"key"')) == 2, "keys-out の key 行は 2 行")
        check(not any(w in "\n".join(kept) for w in leaks), "keys-out に ImeShadow の名前も値も無い（meta の capabilities も）")
        check('"config_gated":[]' in kept[0] and '"unconditional":["key"]' in kept[0], "meta の capabilities から key 以外の名前が消える")
        check("future_row" not in "\n".join(kept), "未知の種類の行も残らない（許可リスト）")
        check(not os.path.exists(obs), "元のファイルは元の場所から消える")
        moved = os.path.join(sealed, "obs.jsonl")
        check(os.path.isfile(moved) and _sha256_file(moved) == orig_sha, "元のファイルは封印先に、同じ内容で移る")
        with open(os.path.join(sealed, "seal.json"), encoding="utf-8") as f:
            seal_text = f.read()
        info = json.loads(seal_text)
        check(info["sha256"] == orig_sha and info["bytes"] == orig_bytes, "seal.json の SHA-256 とバイト数が元と一致")
        check(info["kept_key_rows"] == 2 and info["sealed_at"].endswith("Z"), "seal.json に残した key 行数と封印時刻がある")
        check(not any(w in seal_text for w in leaks), "seal.json に ImeShadow の情報が無い")
        check(not any(w in out for w in leaks) and orig_sha in out, "標準出力に ImeShadow の情報が無く、SHA-256 は出る")
        check(not os.path.exists(keys + ".part"), "作業ファイル（.part）が残らない")
        p = subprocess.run([sys.executable, validator, "--kind", "obs", keys], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 0, "keys-out は obs/1 の検査器を通る（exit %d）" % p.returncode)

        # CRLF のファイルでも封印できる（Windows のロガーの出力）。
        obs2 = os.path.join(tmp, "obs2.jsonl")
        write(obs2, good, crlf=True)
        rc, _ = run(obs2, os.path.join(tmp, "keys2.jsonl"), os.path.join(tmp, "sealed2"))
        with open(os.path.join(tmp, "keys2.jsonl"), "rb") as f:
            raw2 = f.read()
        check(rc == 0 and b"\r" not in raw2 and raw2.count(b'"type":"key"') == 2, "CRLF のファイルも封印でき、keys-out は LF")

        # 陰性: 拒否は何も動かさない。
        def refuse(name, lines, pre=None, sealed_dir=None):
            o = os.path.join(tmp, name + ".jsonl")
            k = os.path.join(tmp, name + ".keys")
            sd = sealed_dir or os.path.join(tmp, name + "-sealed")
            write(o, lines)
            if pre:
                pre(k, sd)
            before = _sha256_file(o)
            rc, out = run(o, k, sd)
            untouched = os.path.isfile(o) and _sha256_file(o) == before
            check(rc == 1 and untouched and not os.path.exists(k + ".part") and not any(w in out for w in leaks),
                  "拒否する: %s（exit %d・元のファイルは動かない・情報は出ない）" % (name, rc))
            return k, sd

        def make_keys(k, sd):
            with open(k, "w", encoding="utf-8") as f:
                f.write("x\n")

        k, _ = refuse("keys-out-exists", good, pre=make_keys)
        with open(k, encoding="utf-8") as f:
            check(f.read() == "x\n", "既にある keys-out を上書きしない")
        refuse("no-meta", good[1:])
        refuse("meta-not-first", [good[1], good[0]] + good[2:])
        refuse("second-meta", good[:2] + [meta] + good[2:])
        refuse("broken-json", good[:2] + ["{not json"] + good[2:])
        refuse("not-object", good[:2] + ["[1,2]"] + good[2:])
        refuse("empty", [])

        def make_seal(k, sd):
            os.makedirs(sd)
            with open(os.path.join(sd, "seal.json"), "w", encoding="utf-8") as f:
                f.write("{}\n")

        refuse("seal-json-exists", good, pre=make_seal)
        same = os.path.join(tmp, "same-name")
        os.makedirs(same)
        o = os.path.join(tmp, "dup.jsonl")
        write(o, good)
        with open(os.path.join(same, "dup.jsonl"), "w", encoding="utf-8") as f:
            f.write("x\n")
        rc, _ = run(o, os.path.join(tmp, "dup.keys"), same)
        check(rc == 1 and os.path.isfile(o), "封印先に同名のファイルがあれば拒否し、元のファイルは動かない")

        # 使い方の誤り。
        p = subprocess.run([sys.executable, me, "--obs", o], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "必須の引数が無ければ exit 2")

    if fails:
        print("  ---- seal_obs selftest 失敗 %d 件 ----" % len(fails))
        return 1
    print("  ---- seal_obs selftest すべて緑 ----")
    return 0
# --- selftest end ---


def main(argv=None):
    ap = argparse.ArgumentParser(description="obs/1 の meta 行と key 行だけを取り出し、元のファイルを封印する")
    ap.add_argument("--selftest", action="store_true", help="陽性対照と陰性対照を回す")
    ap.add_argument("--obs", help="単体ロガーの出力（封印される）")
    ap.add_argument("--keys-out", help="meta 行と key 行だけを書く先（既にあれば止まる）")
    ap.add_argument("--sealed-dir", help="元のファイルの移し先（seal.json もここへ）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.obs and args.keys_out and args.sealed_dir):
        ap.error("--obs / --keys-out / --sealed-dir がすべて要る")
    try:
        info = seal(args.obs, args.keys_out, args.sealed_dir)
    except Refused as e:
        print("seal_obs: 拒否（元のファイルは動かしていない）: %s" % e, file=sys.stderr)
        return 1
    except RuntimeError as e:
        print("seal_obs: 封印後の照合が崩れた: %s" % e, file=sys.stderr)
        return 1
    print("sealed: %s" % info["sealed_file"])
    print("sha256: %s" % info["sha256"])
    print("bytes: %d" % info["bytes"])
    print("key rows kept: %d" % info["kept_key_rows"])
    print("keys-out: %s" % args.keys_out)
    print("seal.json: %s" % os.path.join(args.sealed_dir, "seal.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
