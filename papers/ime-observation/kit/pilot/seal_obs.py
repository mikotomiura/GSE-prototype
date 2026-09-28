#!/usr/bin/env python3
# kit: selftest
"""単体ロガーの出力（obs/1）から meta 行と key 行だけを取り出し、元のファイルを封印する（Python 標準ライブラリだけ）。

  seal_obs.py --obs FILE --keys-out FILE --sealed-dir DIR   封印する（元のファイルは DIR へ移り、FILE の場所からは消える）
  seal_obs.py --unseal SEALED --out FILE                    開封する（プロトコル凍結後の解析パイプライン専用）
  seal_obs.py --selftest                                    陽性対照と陰性対照（速い既定）

較正パイロットは ImeShadow の行を見ない・数えない・突き合わせない（精度の実測ではないので、プロトコルを凍結する前に
値を見てはならない）。そのために、パイロットの解析は封印の後に出る keys-out だけを読む。

規則は**許可リスト**である（捨てる行の種類を名指しせず、残す行の種類だけを名指す）:
  * 残す行 = 1 行目の meta と、key 行。それ以外の行は、種類を問わず keys-out に書かない。
  * meta 行・key 行は、どちらも仕様の欄から**作り直して**書く（許可リストは行の種類だけでなく、行の中の
    フィールドにも効く）。meta はヘッダのキー（type / format / os / logger_version / manifest_sha256 /
    capabilities）だけを残し、capabilities の名前も key だけを残す。key 行は {type, t, category, press} の
    4 つの欄だけから作り直し、それ以外の欄が 1 つでもあれば行ごと拒否する。JSON の同じキーが 2 回ある行も拒否する
    （後の値を黙って採用しない）。

⚠️ 出力（標準出力・seal.json・エラーメッセージ）に、捨てた行の情報（行数・値・行番号・種類）を出さない。
   ★ 元のバイト数・行数も出さない（判断 31）。バイト数と封印先の大きさから ImeShadow の行数が推せてしまうため。
   出すのは、元のファイル全体の SHA-256 と、残した key 行の数だけ。完全性は SHA-256 だけで確かめる。
⚠️ 封印先のファイルは 1 MiB（1048576 バイト）の倍数の大きさに詰める（0 バイトで埋める）。元の長さは、詰め物の
   後ろに置く固定長の欄（8 バイト・big-endian の符号なし整数）に記録し、開封のときだけそこから取り除く。
   ★ この設計だと、封印先の大きさからは「1 MiB 単位でしか」元の大きさが分からない（判断 31 が許す粗さ）。
⚠️ 元のファイルを開く道具は作らない。--unseal は封印先を**そのまま元のバイト列に戻すだけ**で、中身を解釈しない
   （プロトコルを凍結した後の解析パイプラインだけが使う）。

読めない行（JSON Lines として不正・同じキーが 2 回ある・仕様の欄と違う）・1 行目が meta でない・meta が 2 つ以上の
ファイルは、何も動かさずに拒否する（exit 1）。keys-out が既にある・封印先に同名のファイルか seal.json が既にある
ときも拒否する。ロガーがまだ書き込み中（大きさか mtime が安定しない）ファイルも拒否する
（★ ロガーを止めてから封印すること）。
exit 0 = 封印した（開封した）/ 1 = 拒否（元のファイルは動かしていない。封印後の照合が崩れたときだけ例外で、
メッセージが言う）/ 2 = 使い方の誤り。
"""
import argparse
import datetime
import errno
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time

META_KEYS = ("type", "format", "os", "logger_version", "manifest_sha256", "capabilities")
CAP_GROUPS = ("unconditional", "threshold_gated", "config_gated")
KEEP_CAPABILITIES = ("key",)
KEY_FIELDS = ("type", "t", "category", "press")
KEY_CATEGORIES = (
    "alphabetic", "numeric", "punctuation", "sentence_punctuation", "tab", "backspace",
    "delete", "space", "enter", "navigation", "modifier", "function", "escape", "other",
)
VERSION_RE = re.compile(r"^[0-9A-Za-z.+-]{1,32}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

PAD_UNIT = 1024 * 1024  # 1 MiB — 封印先の大きさはこの倍数に詰める
TRAILER_LEN = 8  # 詰め物の後ろの固定長の欄（元の長さ・big-endian u64）
STABLE_CHECKS = 2
STABLE_INTERVAL_S = 0.02

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


class Refused(Exception):
    """封印しない・開封しない理由（メッセージに、捨てる行の情報を入れないこと）。"""


class SealVerificationError(Exception):
    """封印・開封の後の SHA-256 照合が崩れた（RuntimeError の系列にしない —— RecursionError と混ざらないように）。"""


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _no_dup_pairs(pairs):
    """json.loads の object_pairs_hook。同じキーが 2 回ある行を拒否する（後の値を黙って採用しない）。"""
    out = {}
    for k, v in pairs:
        if k in out:
            raise Refused("JSON の行に同じキーが 2 回ある")
        out[k] = v
    return out


def _parse_line(body):
    try:
        return json.loads(body.decode("utf-8"), object_pairs_hook=_no_dup_pairs)
    except (ValueError, RecursionError):
        # UnicodeDecodeError は ValueError の系列。深すぎる入れ子（RecursionError）も拒否として扱う
        # （封印後の照合失敗と混同しない —— どちらも「読めない」であって「壊れている」ではない）。
        raise Refused("JSON Lines として読めない行がある")


def _meta_line(obj):
    """meta 行を許可リストで作り直す（ヘッダのキーと、capabilities の key だけを残す）。値の型と形も確かめる。"""
    if not isinstance(obj, dict):
        raise Refused("meta 行が object ではない")
    if set(obj) - set(META_KEYS):
        raise Refused("meta 行に仕様にないキーがある")
    if obj.get("type") != "meta":
        raise Refused("meta の type が違う")
    if obj.get("format") != "obs/1":
        raise Refused("meta の format が obs/1 ではない")
    if obj.get("os") not in ("macos", "windows"):
        raise Refused("meta の os が仕様の列挙にない")
    if not isinstance(obj.get("logger_version"), str) or not VERSION_RE.match(obj["logger_version"]):
        raise Refused("meta の logger_version が仕様の形ではない")
    if not isinstance(obj.get("manifest_sha256"), str) or not SHA256_RE.match(obj["manifest_sha256"]):
        raise Refused("meta の manifest_sha256 が仕様の形ではない")
    caps = obj.get("capabilities")
    if not isinstance(caps, dict) or set(caps) != set(CAP_GROUPS):
        raise Refused("meta の capabilities が仕様の形ではない")
    kept_caps = {}
    for group in CAP_GROUPS:
        names = caps.get(group)
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise Refused("meta の capabilities が文字列の配列ではない")
        kept_caps[group] = [n for n in names if n in KEEP_CAPABILITIES]
    out = {k: obj[k] for k in META_KEYS if k in obj}
    out["capabilities"] = kept_caps
    return _compact(out)


def _key_line(obj):
    """key 行を仕様の 4 つの欄だけから作り直す（それ以外の欄が 1 つでもあれば拒否）。"""
    if not isinstance(obj, dict):
        raise Refused("key 行が object ではない")
    if set(obj) != set(KEY_FIELDS):
        raise Refused("key 行のキーが仕様と違う")
    if obj.get("type") != "key":
        raise Refused("key 行の type が違う")
    if not _is_int(obj.get("t")) or obj["t"] < 0:
        raise Refused("key 行の t が 0 以上の整数ではない")
    if obj.get("category") not in KEY_CATEGORIES:
        raise Refused("key 行の category が仕様の 14 種にない")
    if not isinstance(obj.get("press"), bool):
        raise Refused("key 行の press が真偽値ではない")
    return _compact({"type": "key", "t": obj["t"], "category": obj["category"], "press": obj["press"]})


def _stable(path, checks=STABLE_CHECKS, interval_s=STABLE_INTERVAL_S):
    """大きさと mtime が checks 回の観測で変わらないか（ロガーが書き込み中でないか）。"""
    prev = None
    for i in range(checks):
        try:
            st = os.stat(path)
        except OSError:
            return False
        cur = (st.st_size, getattr(st, "st_mtime_ns", st.st_mtime))
        if prev is not None and cur != prev:
            return False
        prev = cur
        if i + 1 < checks:
            time.sleep(interval_s)
    return True


def _pad_sealed_file(path, orig_len):
    """path の末尾に 0 の詰め物と固定長の欄（元の長さ）を足し、全体を PAD_UNIT の倍数にする。"""
    pad_len = (-(orig_len + TRAILER_LEN)) % PAD_UNIT
    block = b"\x00" * (1 << 20)
    with open(path, "r+b") as f:
        f.seek(0, os.SEEK_END)
        remaining = pad_len
        while remaining > 0:
            n = min(remaining, len(block))
            f.write(block[:n])
            remaining -= n
        f.write(struct.pack(">Q", orig_len))


def _read_orig_len(path):
    size = os.path.getsize(path)
    if size < TRAILER_LEN:
        raise Refused("封印先が小さすぎる（詰め物の欄が無い）")
    with open(path, "rb") as f:
        f.seek(size - TRAILER_LEN)
        trailer = f.read(TRAILER_LEN)
    (orig_len,) = struct.unpack(">Q", trailer)
    if orig_len > size - TRAILER_LEN:
        raise Refused("封印先の詰め物の欄の値がおかしい")
    return orig_len


def _hash_prefix(path, orig_len):
    h = hashlib.sha256()
    remaining = orig_len
    with open(path, "rb") as f:
        while remaining > 0:
            chunk = f.read(min(1 << 20, remaining))
            if not chunk:
                raise SealVerificationError("封印先が元の長さより短い（壊れている）")
            h.update(chunk)
            remaining -= len(chunk)
    return h.hexdigest()


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
    seal_json_part = seal_json + ".part"
    if os.path.abspath(target) == os.path.abspath(obs):
        raise Refused("--obs は既に封印先の中にある")
    if os.path.exists(target) or os.path.exists(seal_json):
        raise Refused("封印先に同名のファイルか seal.json が既にある（上書きしない）")
    if not _stable(obs):
        raise Refused("--obs の大きさか更新時刻が安定しない（ロガーが書き込み中の可能性。止めてから封印すること）")

    # 1. keys-out を .part に書く（同時に元のファイル全体の SHA-256 を計算する）。
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
                obj = _parse_line(body)
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
                    dst.write((_key_line(obj) + "\n").encode("utf-8"))
                    kept += 1
        if not seen_meta:
            raise Refused("meta 行が無い")
    except BaseException:
        if os.path.exists(part):
            os.remove(part)
        raise

    sha = h.hexdigest()

    # 2. 元のファイルを移す。同じボリュームなら os.rename だけ。別ボリュームは拒否する
    #    （rename はアトミックなので、失敗しても部分的なファイルは残らない）。
    try:
        os.makedirs(sealed_dir, exist_ok=True)
        os.rename(obs, target)
    except OSError as e:
        if os.path.exists(part):
            os.remove(part)
        if getattr(e, "errno", None) == errno.EXDEV:
            raise Refused("元のファイルと封印先が別ボリューム（コピーはしない）")
        raise Refused("封印先へ移せなかった（%s）" % e.__class__.__name__)

    # 詰め物と固定長の欄を足す。★ ここから先、target には元のデータしかない（消してはいけない）。
    try:
        _pad_sealed_file(target, nbytes)
    except OSError as e:
        if os.path.exists(part):
            os.remove(part)
        raise Refused("封印先の詰め物を書けなかった（%s）。封印先 %s の中身は元のデータのまま残っている" % (
            e.__class__.__name__, target))

    # 3. SHA-256 を照合（専用の例外クラス。RecursionError と混ざらない）。
    after = _hash_prefix(target, nbytes)
    if after != sha:
        raise SealVerificationError("封印後の SHA-256 が読んだときと一致しない（元の sha256=%s）。封印先 %s を確かめること" % (sha, target))

    # 4. seal.json を .part に書いて rename。
    summary = {
        "sealed_file": os.path.basename(obs),
        "sha256": sha,
        "sealed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "keys_out": os.path.basename(keys_out),
        "keys_out_sha256": _sha256_file(part),
        "kept_key_rows": kept,
    }
    try:
        with open(seal_json_part, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        os.rename(seal_json_part, seal_json)
    except OSError as e:
        if os.path.exists(seal_json_part):
            os.remove(seal_json_part)
        if os.path.exists(part):
            os.remove(part)
        raise Refused("seal.json を書けなかった（%s）。封印先 %s の中身は元のデータのまま残っている" % (
            e.__class__.__name__, target))

    # 5. 最後に keys-out の .part を rename。★ これが終わった時点で「keys-out があるなら封印は完了している」。
    os.rename(part, keys_out)
    return summary


def unseal(sealed_path, out_path):
    """封印先から元のバイト列を復元して out_path に書く。seal.json の SHA-256 と照合する。拒否は Refused。"""
    if not os.path.isfile(sealed_path):
        raise Refused("--unseal がファイルではない")
    seal_json = os.path.join(os.path.dirname(os.path.abspath(sealed_path)), "seal.json")
    try:
        with open(seal_json, encoding="utf-8") as f:
            info = json.load(f, object_pairs_hook=_no_dup_pairs)
    except (OSError, ValueError) as e:
        raise Refused("seal.json を読めない（%s）" % e.__class__.__name__)
    if not isinstance(info, dict) or not isinstance(info.get("sha256"), str) or not SHA256_RE.match(info["sha256"]):
        raise Refused("seal.json の形が違う（sha256 が無い）")
    expected = info["sha256"]

    orig_len = _read_orig_len(sealed_path)
    if os.path.exists(out_path):
        raise Refused("--out が既にある（上書きしない）")
    part = out_path + ".part"
    if os.path.exists(part):
        raise Refused("--out の作業ファイル（.part）が既にある")
    h = hashlib.sha256()
    remaining = orig_len
    try:
        with open(sealed_path, "rb") as src, open(part, "wb") as dst:
            while remaining > 0:
                chunk = src.read(min(1 << 20, remaining))
                if not chunk:
                    raise Refused("封印先が元の長さより短い（壊れている）")
                h.update(chunk)
                dst.write(chunk)
                remaining -= len(chunk)
    except BaseException:
        if os.path.exists(part):
            os.remove(part)
        raise
    got = h.hexdigest()
    if got != expected:
        if os.path.exists(part):
            os.remove(part)
        raise SealVerificationError("開封した内容の SHA-256 が seal.json と一致しない（期待 %s・実際 %s）" % (expected, got))
    os.rename(part, out_path)
    return {"bytes": orig_len, "sha256": got}


# --- selftest begin ---
def _selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    validator = os.path.join(here, "..", "formats", "validate_logs.py")
    me = os.path.abspath(__file__)
    fails = []

    def check(ok, what):
        print("  %s %s" % ("OK" if ok else "NG", what))
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

    def run(*args):
        p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode("utf-8", "replace")

    def run_seal(obs, keys, sealed):
        return run("--obs", obs, "--keys-out", keys, "--sealed-dir", sealed)

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
        rc, out = run_seal(obs, keys, sealed)
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
        check(os.path.isfile(moved) and _sha256_file(moved) != orig_sha, "封印先はそのままの内容ではない（詰め物が付く）")
        check(os.path.getsize(moved) % PAD_UNIT == 0, "封印先の大きさは 1 MiB の倍数（%d バイト）" % os.path.getsize(moved))
        with open(os.path.join(sealed, "seal.json"), encoding="utf-8") as f:
            seal_text = f.read()
        info = json.loads(seal_text)
        check(info["sha256"] == orig_sha, "seal.json の SHA-256 が元と一致")
        check("bytes" not in info, "★ seal.json にバイト数を記録しない（判断 31）")
        check(info["kept_key_rows"] == 2 and info["sealed_at"].endswith("Z"), "seal.json に残した key 行数と封印時刻がある")
        check(not any(w in seal_text for w in leaks), "seal.json に ImeShadow の情報が無い")
        check(not any(w in out for w in leaks) and orig_sha in out, "標準出力に ImeShadow の情報が無く、SHA-256 は出る")
        check("bytes" not in out and "byte" not in out.lower(), "★ 標準出力にバイト数を出さない（判断 31）")
        check(not os.path.exists(keys + ".part"), "作業ファイル（.part）が残らない")
        p = subprocess.run([sys.executable, validator, "--kind", "obs", keys], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 0, "keys-out は obs/1 の検査器を通る（exit %d）" % p.returncode)

        # --unseal: 元のバイト列にきっちり戻り、SHA-256 が一致する。
        expected_bytes = ("\n".join(good) + "\n").encode("utf-8")
        restored = os.path.join(tmp, "restored.jsonl")
        rc, _ = run("--unseal", moved, "--out", restored)
        check(rc == 0, "開封できる（exit 0）")
        with open(restored, "rb") as f:
            restored_bytes = f.read()
        check(restored_bytes == expected_bytes, "開封した内容が元のバイト列にきっちり戻る")
        check(_sha256_file(restored) == orig_sha, "開封した内容の SHA-256 が元と一致する")
        check(os.path.exists(restored + ".part") is False, "開封の作業ファイル（.part）が残らない")
        rc, out2 = run("--unseal", moved, "--out", restored)
        check(rc == 1 and "拒否" in out2, "--out が既にあれば開封を拒否する（上書きしない）")

        # CRLF のファイルでも封印できる（Windows のロガーの出力）。
        obs2 = os.path.join(tmp, "obs2.jsonl")
        write(obs2, good, crlf=True)
        rc, _ = run_seal(obs2, os.path.join(tmp, "keys2.jsonl"), os.path.join(tmp, "sealed2"))
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
            rc, out = run_seal(o, k, sd)
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

        # 深すぎる入れ子（RecursionError）も拒否として扱う（封印後の照合失敗と混同しない）。
        deep = "[" * 3000 + "]" * 3000
        refuse("too-deep", good[:1] + ['{"type":"key","t":1,"category":"other","press":' + deep + '}'] + good[2:])

        # key 行の許可リストがフィールドにも効く: 余計な欄・仕様外の category・型違いは拒否。
        refuse("key-extra-field", good[:1] + ['{"type":"key","t":10,"category":"space","press":true,"extra":1}'])
        refuse("key-bad-category", good[:1] + ['{"type":"key","t":10,"category":"not_a_real_category","press":true}'])
        refuse("key-press-not-bool", good[:1] + ['{"type":"key","t":10,"category":"space","press":1}'])
        refuse("key-t-not-int", good[:1] + ['{"type":"key","t":"10","category":"space","press":true}'])

        # 同じキーが 2 回ある行（後の値を黙って採用しない）。
        refuse("dup-key-in-key-row", good[:1] + ['{"type":"key","type":"key","t":10,"category":"space","press":true}'])
        refuse("dup-key-in-meta", ['{"type":"meta","type":"meta","format":"obs/1","os":"macos","logger_version":"0.1.0",'
                                    '"manifest_sha256":"' + "0" * 64 + '","capabilities":{"unconditional":[],'
                                    '"threshold_gated":[],"config_gated":[]}}'] + good[1:])

        # meta の値の型と形も確かめる。
        bad_os_meta = meta.replace('"os":"macos"', '"os":"linux"')
        refuse("meta-bad-os", [bad_os_meta] + good[1:])
        bad_sha_meta = meta.replace('"manifest_sha256":"' + "0" * 64 + '"', '"manifest_sha256":"zz"')
        refuse("meta-bad-sha", [bad_sha_meta] + good[1:])

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
        rc, _ = run_seal(o, os.path.join(tmp, "dup.keys"), same)
        check(rc == 1 and os.path.isfile(o), "封印先に同名のファイルがあれば拒否し、元のファイルは動かない")

        # ロガーが書き込み中（大きさが安定しない）ファイルは拒否する。
        import threading
        unstable = os.path.join(tmp, "unstable.jsonl")
        write(unstable, good)

        def grow_soon():
            time.sleep(STABLE_INTERVAL_S / 2)
            with open(unstable, "ab") as f:
                f.write(b"x")

        th = threading.Thread(target=grow_soon)
        th.start()
        rc, out = run_seal(unstable, os.path.join(tmp, "unstable.keys"), os.path.join(tmp, "unstable-sealed"))
        th.join()
        check(rc == 1 and os.path.isfile(unstable), "大きさが安定しないファイルは拒否する（ロガーを止めてから封印すること）")
        check(_stable(unstable) is True, "書き込みが止まれば安定と判定する（陽性対照）")

        # 使い方の誤り。
        p = subprocess.run([sys.executable, me, "--obs", o], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "必須の引数が無ければ exit 2")
        p = subprocess.run([sys.executable, me, "--unseal", moved], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        check(p.returncode == 2, "--unseal には --out が要る（exit 2）")

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
    ap.add_argument("--unseal", help="封印先のファイル（--out と組で使う。プロトコル凍結後の解析パイプライン専用）")
    ap.add_argument("--out", help="--unseal の書き出し先")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.unseal:
        if not args.out:
            ap.error("--unseal には --out が要る")
        try:
            info = unseal(args.unseal, args.out)
        except Refused as e:
            print("seal_obs: 拒否: %s" % e, file=sys.stderr)
            return 1
        except SealVerificationError as e:
            print("seal_obs: 開封後の照合が崩れた: %s" % e, file=sys.stderr)
            return 1
        print("unsealed: %s" % args.out)
        print("sha256: %s" % info["sha256"])
        return 0
    if not (args.obs and args.keys_out and args.sealed_dir):
        ap.error("--obs / --keys-out / --sealed-dir がすべて要る（または --unseal / --out）")
    try:
        info = seal(args.obs, args.keys_out, args.sealed_dir)
    except Refused as e:
        print("seal_obs: 拒否（元のファイルは動かしていない）: %s" % e, file=sys.stderr)
        return 1
    except SealVerificationError as e:
        print("seal_obs: %s" % e, file=sys.stderr)
        return 1
    print("sealed: %s" % info["sealed_file"])
    print("sha256: %s" % info["sha256"])
    print("key rows kept: %d" % info["kept_key_rows"])
    print("keys-out: %s" % args.keys_out)
    print("seal.json: %s" % os.path.join(args.sealed_dir, "seal.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
