#!/usr/bin/env python3
# kit: selftest
"""青空文庫の本文から句を切り出し、ひらがなの読みを付けて corpus/1 で書き出す前処理。

  build_corpus.py --src DIR --out FILE --seed N [--tokenizer sudachi|table:JSON]
                  [--min-reading 6] [--max-reading 30] [--per-work 100]
  build_corpus.py --validate FILE      corpus/1 の検査（違反があれば exit 1）
  build_corpus.py --selftest           辞書なしの陽性・陰性対照（速い既定）

処理: cp932 で読む → 題・記号の説明の枠・底本情報・注記・ルビ記法を除く → 文（。！？）に分ける →
節（読点・空白）に分ける → 読みを付ける → 読みの長さが min〜max に入る句にまとめる →
読みがひらがなだけの句を残す → 作品ごとに seed で K 句まで抽出する。

★ 読みの付与は SudachiPy（判断 19）だが、トークナイザは差し替えられる。`sudachipy` は
   SudachiTokenizer の中だけで import する（ファイル先頭に置かない）。辞書の無い機械でも
   --selftest と check.sh が緑になる。selftest は表トークナイザ（テストの中で作る小さな対応表）で回る。
⚠️ 読みは誤りうる（固有名詞など）。E1 の正解は変換事象なので、読みが原文と違っても打鍵列として妥当なら
   足りる。E2 の正解は「打った読み」（原文ではない）。

exit 0 = 成功 / 1 = 不合格（検査の違反・句が 1 件も残らない） / 2 = 作れなかった・検査できなかった
（使い方の誤り・ファイルが読めない・トークナイザが使えない）。★ 0 以外はすべて不合格として扱うこと。
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types

FORMAT = "corpus/1"
SOURCE = "aozora"
# corpus/1 の型（kit/formats/FORMATS.md）
READING_RE = re.compile(r"[ぁ-ゖー]+")
NAME_RE = re.compile(r"[0-9A-Za-z._+-]{1,64}")
WORK_ID_RE = re.compile(r"[a-z0-9][a-z0-9_]{0,31}")
PHRASE_ID_RE = re.compile(r"([a-z0-9][a-z0-9_]{0,31})-[0-9]+-[0-9]+")
HEADER_KEYS = ("kind", "format", "source", "tokenizer", "dict")
PHRASE_KEYS = ("kind", "phrase_id", "work_id", "text", "reading", "reading_len")

DEFAULT_MIN = 6
DEFAULT_MAX = 30
DEFAULT_PER_WORK = 100
MAX_SHOWN = 50

# 青空文庫のテキストの記法
DASH_RE = re.compile(r"-{10,}")            # 冒頭の「記号について」の枠（点線 2 本）
HEAD_SCAN = 40                             # 最初の点線は先頭のこの行数の中にある
HEAD_SPAN = 60                             # 2 本目の点線は最初の点線からこの行数の中にある
FOOT_RE = re.compile(r"底本[：:]")          # 作品末尾の底本情報の始まり（行頭）
ANNOT_RE = re.compile(r"［＃[^］]*］")       # 注記
RUBY_RE = re.compile(r"《[^》]*》")          # ルビ（読みは捨てる）
SENT_END_RE = re.compile(r"[。！？]+[」』）]*")
QUOTE_RE = re.compile(r"[「」『』]")
CLAUSE_RE = re.compile(r"[^、\s]+")         # 節: 読点と空白（全角空白を含む）で区切る


class BuildError(Exception):
    def __init__(self, msg, code=2):
        Exception.__init__(self, msg)
        self.code = code


def _dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def kata_to_hira(s):
    """カタカナ（ァ〜ヶ）をひらがなに直す。ー などそれ以外はそのまま。"""
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


# ---------------------------------------------------------------- トークナイザ（差し替え可能）

class TableTokenizer(object):
    """表（表記 → ひらがなの読み）の最長一致。表に無い文字はそのまま残す（ひらがなは自分が読み）。

    表に無い漢字・カタカナ・数字・英字は読みに残るので、その節は捨てられる（辞書なしのテスト用）。"""

    name = "table"

    def __init__(self, mapping, dict_name):
        self._map = dict(mapping)
        self._maxlen = max([len(k) for k in self._map] or [1])
        self.dict_name = dict_name

    def read(self, text):
        out = []
        p = 0
        while p < len(text):
            for n in range(min(self._maxlen, len(text) - p), 0, -1):
                hit = self._map.get(text[p:p + n])
                if hit is not None:
                    out.append(hit)
                    p += n
                    break
            else:
                out.append(text[p])
                p += 1
        return "".join(out)


def _dist_version(*names):
    """配布パッケージの版。取れなければ止める（版を記録できない実行は再現できない）。"""
    from importlib import metadata
    for n in names:
        try:
            return metadata.version(n)
        except metadata.PackageNotFoundError:
            continue
    raise BuildError("パッケージの版が取れない: %s" % "/".join(names), 2)


def _name_safe(s):
    return re.sub(r"[^0-9A-Za-z._+-]", "_", s)[:64]


class SudachiTokenizer(object):
    """SudachiPy（判断 19）。⚠️ sudachipy はここでだけ import する（先頭 import 禁止）。"""

    def __init__(self):
        try:
            from sudachipy import dictionary, tokenizer
        except ImportError as e:
            raise BuildError("sudachipy が入っていない（M0 で pip install sudachipy sudachidict_core）: %s" % e, 2)
        try:
            self._tok = dictionary.Dictionary().create()
            self._mode = tokenizer.Tokenizer.SplitMode.C
        except Exception as e:
            raise BuildError("SudachiPy の辞書を開けない（sudachidict_core が要る）: %s" % type(e).__name__, 2)
        self.name = _name_safe("sudachipy-" + _dist_version("SudachiPy", "sudachipy"))
        self.dict_name = _name_safe("sudachidict_core-" + _dist_version("SudachiDict-core", "sudachidict_core"))

    def read(self, text):
        # reading_form はカタカナ。空（未知語）なら表記を使う（ひらがなでなければ後で捨てられる）
        return kata_to_hira("".join(m.reading_form() or m.surface() for m in self._tok.tokenize(text, self._mode)))


def load_table(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        raise BuildError("表を開けない: %s（%s）" % (path, type(e).__name__), 2)
    try:
        mapping = json.loads(raw.decode("utf-8"))
    except ValueError:
        raise BuildError("表が JSON（UTF-8）として読めない: %s" % path, 2)
    if not isinstance(mapping, dict) or not mapping or not all(
            isinstance(k, str) and k and isinstance(v, str) and v for k, v in mapping.items()):
        raise BuildError("表は {表記: 読み} の空でないオブジェクト（文字列だけ）: %s" % path, 2)
    return TableTokenizer(mapping, hashlib.sha256(raw).hexdigest())


def make_tokenizer(spec):
    if spec == "sudachi":
        return SudachiTokenizer()
    if spec.startswith("table:") and len(spec) > len("table:"):
        return load_table(spec[len("table:"):])
    raise BuildError("--tokenizer は sudachi か table:<json>（受け取った値: %s）" % spec, 2)


# ---------------------------------------------------------------- 本文の整形・句の切り出し

def body_lines(text):
    """本文の行を返す。題・著者と記号の説明の枠（点線 2 本）・底本情報を除き、注記とルビ記法を除く。

    ★ ルビは原文の漢字を残して読みを捨てる（読みはトークナイザが付ける）。"""
    lines = re.split(r"\r\n|\r|\n", text)
    first = next((i for i, ln in enumerate(lines[:HEAD_SCAN]) if DASH_RE.fullmatch(ln.strip())), None)
    if first is not None:
        second = next((i for i in range(first + 1, min(len(lines), first + 1 + HEAD_SPAN))
                       if DASH_RE.fullmatch(lines[i].strip())), None)
        if second is not None:
            lines = lines[second + 1:]
    for i, ln in enumerate(lines):
        if FOOT_RE.match(ln):
            lines = lines[:i]
            break
    out = []
    for ln in lines:
        ln = ANNOT_RE.sub("", ln)
        out.append(RUBY_RE.sub("", ln).replace("｜", ""))
    return out


def sentences(lines):
    """行ごとに文（。！？）へ分け、終止記号と引用符（「」『』）を外す。空になった文は数えない。"""
    out = []
    for ln in lines:
        parts = []
        pos = 0
        for m in SENT_END_RE.finditer(ln):
            parts.append(ln[pos:m.end()])
            pos = m.end()
        parts.append(ln[pos:])
        for p in parts:
            core = QUOTE_RE.sub("", SENT_END_RE.sub("", p)).strip()
            if core:
                out.append(core)
    return out


def phrases_of(sentence, tok, min_r, max_r):
    """1 文を句にまとめる: [(text, reading), ...]。

    節（読点・空白で区切った単位）ごとに読みを付け、読みがひらがなだけの節を、合計が min に届くまで
    隣と束ねて 1 句にする（届いた時点で止める・max を超える束ねはしない）。読みが不正な節・max を超える節は
    どの句にも入らない。text は原文の切れ端（束ねた節のあいだの読点はそのまま残る）。"""
    spans = []
    for m in CLAUSE_RE.finditer(sentence):
        r = tok.read(m.group(0))
        spans.append((m.start(), m.end(), r if READING_RE.fullmatch(r) else None))
    out = []
    i = 0
    while i < len(spans):
        total = 0
        j = i
        while j < len(spans) and spans[j][2] is not None and total + len(spans[j][2]) <= max_r:
            total += len(spans[j][2])
            j += 1
            if total >= min_r:
                break
        if total >= min_r:
            out.append((sentence[spans[i][0]:spans[j - 1][1]], "".join(s[2] for s in spans[i:j])))
            i = j
        else:
            i += 1
    return out


def work_candidates(work_id, text, tok, min_r, max_r):
    """1 作品の候補句（本文の順）。phrase_id は <work_id>-<文番号>-<句番号>（入力から決まる・1 始まり）。"""
    cands = []
    for sno, sent in enumerate(sentences(body_lines(text)), 1):
        for pno, (surface, reading) in enumerate(phrases_of(sent, tok, min_r, max_r), 1):
            cands.append({"kind": "phrase", "phrase_id": "%s-%d-%d" % (work_id, sno, pno), "work_id": work_id,
                          "text": surface, "reading": reading, "reading_len": len(reading)})
    return cands


def pick(cands, seed, k):
    """seed で決まる順に k 句まで選び、本文の順に戻す。

    PRNG に頼らず SHA-256(seed:phrase_id) の小さい順に選ぶ（Python の版や OS に依らず同じ結果になる）。"""
    if len(cands) <= k:
        return list(cands)
    ranked = sorted(cands, key=lambda c: hashlib.sha256(("%d:%s" % (seed, c["phrase_id"])).encode("utf-8")).digest())
    chosen = set(c["phrase_id"] for c in ranked[:k])
    return [c for c in cands if c["phrase_id"] in chosen]


def work_id_for(filename):
    """ファイル名から work_id を決める（小文字の英数字と _・32 字まで・小文字か数字で始まる）。"""
    stem = os.path.splitext(os.path.basename(filename))[0].lower()
    wid = re.sub(r"[^a-z0-9_]+", "_", stem)[:32].strip("_")
    if not WORK_ID_RE.fullmatch(wid):
        raise BuildError("ファイル名から work_id を決められない（ASCII の英数字を含む名前にすること）: %s" % filename, 2)
    return wid


def read_works(src):
    """--src の *.txt（cp932）を名前順に読む: [(work_id, text)]。"""
    if not os.path.isdir(src):
        raise BuildError("--src がディレクトリではない: %s" % src, 2)
    names = sorted(n for n in os.listdir(src) if n.lower().endswith(".txt") and os.path.isfile(os.path.join(src, n)))
    if not names:
        raise BuildError(".txt が 1 本も無い: %s" % src, 2)
    works = []
    seen = {}
    for n in names:
        wid = work_id_for(n)
        if wid in seen:
            raise BuildError("work_id が衝突する: %s と %s（どちらも %s）" % (seen[wid], n, wid), 2)
        seen[wid] = n
        with open(os.path.join(src, n), "rb") as f:
            raw = f.read()
        try:
            works.append((wid, raw.decode("cp932")))
        except UnicodeDecodeError:
            raise BuildError("cp932 として読めない: %s" % n, 2)
    return works


def build_bytes(works, seed, tok, min_r, max_r, per_work, log=None):
    """[(work_id, text)] から corpus/1 のバイト列（UTF-8・LF）を作る。作った結果は自分で検査する。"""
    lines = [_dumps({"kind": "header", "format": FORMAT, "source": SOURCE,
                     "tokenizer": tok.name, "dict": tok.dict_name})]
    total = 0
    for wid, text in works:
        cands = work_candidates(wid, text, tok, min_r, max_r)
        chosen = pick(cands, seed, per_work)
        if log is not None:
            log("%s: 候補 %d 句 → 抽出 %d 句" % (wid, len(cands), len(chosen)))
        lines.extend(_dumps(c) for c in chosen)
        total += len(chosen)
    if total == 0:
        raise BuildError("句が 1 件も残らなかった（文字コード・トークナイザ・--min-reading / --max-reading を確かめる）", 1)
    data = ("\n".join(lines) + "\n").encode("utf-8")
    bad = validate_corpus(data)
    if bad:
        raise BuildError("書き出す corpus/1 が自分の検査に通らない（実装の誤り）: %s"
                         % "; ".join("%d行 [%s]" % (ln, code) for ln, code, _ in bad[:5]), 1)
    return data


# ---------------------------------------------------------------- 検査（--validate）

class _Reject(ValueError):
    def __init__(self, code, msg):
        ValueError.__init__(self, msg)
        self.code = code


def _no_float(_s):
    raise _Reject("float", "小数・指数表記の数（整数だけを許す）")


def _no_constant(_s):
    raise _Reject("constant", "NaN / Infinity は JSON の値ではない")


def _no_dup(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise _Reject("dup_key", "同じキーが 1 行に 2 回ある")
        d[k] = v
    return d


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _keys_ok(bad, ln, obj, want):
    ok = True
    for k in want:
        if k not in obj:
            bad(ln, "missing_key", "必須キーが無い: %s" % k)
            ok = False
    if any(k not in want for k in obj):
        bad(ln, "unknown_key", "未知のキーがある")
        ok = False
    return ok


def _check_header(bad, ln, obj):
    if obj.get("kind") != "header":
        bad(ln, "header", "1 行目がヘッダ（kind が header）ではない")
        return
    if not _keys_ok(bad, ln, obj, HEADER_KEYS):
        return
    if obj["format"] != FORMAT:
        bad(ln, "format", "format が %s ではない" % FORMAT)
    if obj["source"] != SOURCE:
        bad(ln, "source", "source が %s ではない" % SOURCE)
    for k in ("tokenizer", "dict"):
        if not (isinstance(obj[k], str) and NAME_RE.fullmatch(obj[k])):
            bad(ln, "name", "%s が名前と版の規則（^[0-9A-Za-z._+-]{1,64}$）に合わない" % k)


def _check_phrase(bad, ln, obj, seen):
    kind = obj.get("kind")
    if kind == "header":
        bad(ln, "second_header", "ヘッダが 2 つ目にもある")
        return
    if kind != "phrase":
        bad(ln, "kind", "kind が phrase ではない")
        return
    if not _keys_ok(bad, ln, obj, PHRASE_KEYS):
        return
    for k in ("phrase_id", "work_id", "text", "reading"):
        if not isinstance(obj[k], str):
            bad(ln, "type", "%s が文字列ではない" % k)
            return
    wid = obj["work_id"]
    if not WORK_ID_RE.fullmatch(wid):
        bad(ln, "work_id", "work_id が規則（^[a-z0-9][a-z0-9_]{0,31}$）に合わない")
    m = PHRASE_ID_RE.fullmatch(obj["phrase_id"])
    if m is None:
        bad(ln, "phrase_id", "phrase_id が <work_id>-<文番号>-<句番号> の形ではない")
    elif m.group(1) != wid:
        bad(ln, "work_id_mismatch", "phrase_id の作品名が work_id と違う")
    if obj["phrase_id"] in seen:
        bad(ln, "dup_id", "phrase_id が重複している")
    seen.add(obj["phrase_id"])
    if not obj["text"]:
        bad(ln, "text", "text が空")
    if not READING_RE.fullmatch(obj["reading"]):
        bad(ln, "reading", "reading がひらがなだけ（^[ぁ-ゖー]+$）ではない")
    if not _is_int(obj["reading_len"]):
        bad(ln, "type", "reading_len が整数ではない")
    elif obj["reading_len"] != len(obj["reading"]):
        bad(ln, "reading_len", "reading_len が reading の文字数と合わない")


def validate_corpus(data):
    """corpus/1 の検査。違反を (行番号, 種別, 説明) の列で返す（違反なしなら空）。"""
    found = []

    def bad(ln, code, msg):
        found.append((ln, code, msg))

    if data.startswith(b"\xef\xbb\xbf"):
        return [(1, "bom", "UTF-8 の BOM がある（付けない）")]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [(0, "encoding", "UTF-8 として読めない")]
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return [(0, "empty", "空のファイル（1 行目にヘッダが要る）")]
    seen = set()
    phrases = 0
    for ln, raw in enumerate(lines, 1):
        if raw.endswith("\r"):
            raw = raw[:-1]
        try:
            obj = json.loads(raw, object_pairs_hook=_no_dup, parse_float=_no_float, parse_constant=_no_constant)
        except _Reject as e:
            bad(ln, e.code, str(e))
            continue
        except (ValueError, RecursionError):
            bad(ln, "json", "JSON として読めない")
            continue
        if not isinstance(obj, dict):
            bad(ln, "not_object", "JSON のオブジェクトではない")
            continue
        if ln == 1:
            _check_header(bad, ln, obj)
        else:
            phrases += 1
            _check_phrase(bad, ln, obj, seen)
    if phrases == 0:
        bad(len(lines), "no_phrase", "句が 1 件も無い（ヘッダだけ）")
    return found


def cmd_validate(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        print("%s: 開けない（%s）" % (path, type(e).__name__), file=sys.stderr)
        return 2
    found = validate_corpus(data)
    for ln, code, msg in found[:MAX_SHOWN]:
        print("%s:%d: [%s] %s" % (path, ln, code, msg), file=sys.stderr)
    if len(found) > MAX_SHOWN:
        print("%s: …ほか %d 件" % (path, len(found) - MAX_SHOWN), file=sys.stderr)
    if found:
        return 1
    print("corpus/1 OK: %s" % path)
    return 0


# ---------------------------------------------------------------- selftest（辞書を使わない）

# 表トークナイザの対応表。ここに無い漢字・カタカナ・数字・英字は読みに残る（＝その節は捨てられる）
_TABLE = {
    "今日": "きょう", "青空": "あおぞら", "漢字": "かんじ", "私": "わたし", "朝": "あさ", "雨": "あめ",
    "降": "ふ", "行": "い", "読": "よ", "言": "い", "珈琲": "コーヒー",
}
_RULE = "-" * 55


def _tst_text():
    """青空文庫の形の作品（題・記号の説明の枠・本文・底本情報）。行末は CRLF。"""
    lines = [
        "てすとさくひん", "てすとさくしゃ", "",
        _RULE, "【テキスト中に現れる記号について】", "",
        "《》：ルビ", "（例）漢字《かんじ》", "",
        "｜：ルビの付く文字列の始まりを特定する記号", "（例）｜青空《あおぞら》",
        "これはわくのなかのぶんです。", _RULE, "",
        "［＃ここから見出し］",
        "　今日《こんにち》は｜青空《あおぞら》がきれいですね。",   # 1: ルビ（読みは捨てる）
        "漢字を［＃「漢字」に傍点］読みます。",                     # 2: 注記
        "朝、雨が降る、私は行く。",                               # 3: 短い節は束ねる
        "「今日は青空ですね」と私は言った。",                      # 4: 引用符
        "珈琲をのみます。",                                      # 5: 読みにカタカナ
        "今日は3時です。",                                       # 6: 読みに数字
        "今日はABCです。",                                       # 7: 読みに英字
        "朝です。",                                              # 8: 短い（あさです = 4 字）
        "あ" * 31 + "。",                                       # 9: 長い（31 字）
        "ここではないところへいきたいなあ。",                       # 10: かなだけ
        "", "底本：「テスト」", "これはていほんのぶんです。",
    ]
    return "\r\n".join(lines) + "\r\n"


def _many_text():
    """30 文（どれも読みが 6 字以上のひらがな）。K 句の抽出と seed の効きを見る。"""
    kana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほま"
    return "\r\n".join("きょうのてんき%sです。" % c for c in kana) + "\r\n"


def _works():
    return [("tst", _tst_text()), ("b_2", _many_text())]


def _build_fx(works=None, seed=1, per_work=100, min_r=DEFAULT_MIN, max_r=DEFAULT_MAX):
    return build_bytes(works if works is not None else [("tst", _tst_text())], seed,
                       TableTokenizer(_TABLE, "0" * 64), min_r, max_r, per_work)


def _rows(data):
    return [json.loads(ln) for ln in data.decode("utf-8").split("\n") if ln]


def _by_id(data):
    return dict((r["phrase_id"], r) for r in _rows(data)[1:])


def _t_annot_ruby():
    got = _by_id(_build_fx())
    r = got.get("tst-1-1")
    if r is None:
        return "ルビ付きの文が句にならない"
    if r["text"] != "今日は青空がきれいですね":
        return "ルビ・｜が残った: %s" % r["text"]
    if r["reading"] != "きょうはあおぞらがきれいですね":
        return "ルビの読みが混ざった（読みはトークナイザが付ける）: %s" % r["reading"]
    r = got.get("tst-2-1")
    if r is None or r["text"] != "漢字を読みます" or r["reading"] != "かんじをよみます":
        return "注記［＃…］が残った・または句が落ちた: %s" % (r,)
    for r in got.values():
        if any(c in r["text"] for c in "《》｜［］＃"):
            return "記法の文字が text に残った: %s" % r["text"]
    return None


def _t_head_foot():
    for r in _by_id(_build_fx()).values():
        for junk in ("ていほん", "わくのなか", "てすとさく"):
            if junk in r["reading"]:
                return "題・記号の説明の枠・底本情報が句に混ざった: %s" % r["phrase_id"]
    return None


def _t_same_seed():
    a = _build_fx(_works(), seed=7, per_work=5)
    b = _build_fx(_works(), seed=7, per_work=5)
    return None if a == b else "同じ入力・同じ seed で出力が違う"


def _t_seed_changes():
    a = _build_fx(_works(), seed=1, per_work=5)
    b = _build_fx(_works(), seed=2, per_work=5)
    if a == b:
        return "seed を変えても抽出が変わらない（陰性対照）"
    return None


def _t_dropped():
    got = _by_id(_build_fx())
    for sno in (5, 6, 7, 8, 9):
        if any(k.startswith("tst-%d-" % sno) for k in got):
            return "読みにカタカナ・数字・英字が残る句・長さが範囲外の句が残った（文 %d）" % sno
    for r in got.values():
        if not READING_RE.fullmatch(r["reading"]):
            return "ひらがな以外の読みが残った: %s" % r["phrase_id"]
    return None


def _t_length_range():
    got = _by_id(_build_fx())
    for r in got.values():
        if not DEFAULT_MIN <= r["reading_len"] <= DEFAULT_MAX or r["reading_len"] != len(r["reading"]):
            return "長さの範囲外・reading_len 不一致: %s" % r["phrase_id"]
    # 陰性対照: 範囲を変えると、捨てられていた句が入ってくる（範囲が捨てた理由であること）
    if "tst-8-1" not in _by_id(_build_fx(min_r=3)):
        return "--min-reading を下げても短い句（あさです）が入らない"
    long_ = _by_id(_build_fx(max_r=40)).get("tst-9-1")
    if long_ is None or long_["reading_len"] != 31:
        return "--max-reading を上げても長い句（31 字）が入らない"
    return None


def _t_merge():
    got = _by_id(_build_fx())
    a, b = got.get("tst-3-1"), got.get("tst-3-2")
    if a is None or a["text"] != "朝、雨が降る" or a["reading"] != "あさあめがふる":
        return "短い節（朝）が隣と束ならない: %s" % (a,)
    if b is None or b["text"] != "私は行く" or b["reading"] != "わたしはいく":
        return "届いた節（私は行く）が単独の句にならない: %s" % (b,)
    return None


def _t_quotes():
    r = _by_id(_build_fx()).get("tst-4-1")
    if r is None or r["text"] != "今日は青空ですねと私は言った" or r["reading"] != "きょうはあおぞらですねとわたしはいった":
        return "引用符「」を外した句にならない: %s" % (r,)
    return None


def _t_ids():
    want = ["tst-1-1", "tst-2-1", "tst-3-1", "tst-3-2", "tst-4-1", "tst-10-1"]
    got = [r["phrase_id"] for r in _rows(_build_fx())[1:]]
    return None if got == want else "phrase_id が入力から決まる形にならない: %s" % got


def _t_per_work():
    data = _build_fx(_works(), seed=1, per_work=7)
    ids = [r["phrase_id"] for r in _rows(data)[1:]]
    n_b = len([i for i in ids if i.startswith("b_2-")])
    n_t = len([i for i in ids if i.startswith("tst-")])
    if n_b != 7:
        return "候補 30 句の作品 b_2 は K = 7 句のはず（実際 %d）" % n_b
    if n_t != 6:
        return "候補 6 句（K 以下）の作品 tst は全部残るはず（実際 %d）" % n_t
    key = lambda i: tuple(int(x) for x in i.split("-")[-2:])
    if [i for i in ids if i.startswith("b_2-")] != sorted([i for i in ids if i.startswith("b_2-")], key=key):
        return "抽出した句が本文の順に並んでいない"
    return None


def _t_header():
    rows = _rows(_build_fx())
    want = {"kind": "header", "format": "corpus/1", "source": "aozora", "tokenizer": "table", "dict": "0" * 64}
    return None if rows[0] == want else "ヘッダが違う: %s" % rows[0]


def _t_self_valid():
    bad = validate_corpus(_build_fx(_works(), seed=3, per_work=5))
    return None if not bad else "書き出したものが --validate に通らない: %s" % bad[:3]


def _t_sudachi_fake():
    """偽の sudachipy（sys.modules に差す）で SudachiTokenizer の経路を確かめる。⚠️ 本物の辞書ではない。"""
    from importlib import metadata

    class Morph(object):
        def __init__(self, s, r):
            self._s, self._r = s, r

        def surface(self):
            return self._s

        def reading_form(self):
            return self._r

    table = {
        "青空がきれい": [("青空", "アオゾラ"), ("が", "ガ"), ("きれい", "キレイ")],
        "ヴァイオリンをひく": [("ヴァイオリン", "ヴァイオリン"), ("を", "ヲ"), ("ひく", "ヒク")],
        "※です": [("※", ""), ("です", "デス")],
    }
    seen_modes = []

    class FakeTokenizer(object):
        def tokenize(self, text, mode):
            seen_modes.append(mode)
            return [Morph(s, r) for s, r in table[text]]

    fake = types.ModuleType("sudachipy")
    fake.dictionary = types.SimpleNamespace(Dictionary=lambda: types.SimpleNamespace(create=FakeTokenizer))
    fake.tokenizer = types.SimpleNamespace(Tokenizer=types.SimpleNamespace(SplitMode=types.SimpleNamespace(C="MODE_C")))
    versions = {"SudachiPy": "0.6.8", "SudachiDict-core": "20240109"}

    def fake_version(name):
        if name not in versions:
            raise metadata.PackageNotFoundError(name)
        return versions[name]

    old_mod = sys.modules.get("sudachipy")
    old_ver = metadata.version
    sys.modules["sudachipy"] = fake
    metadata.version = fake_version
    try:
        tok = SudachiTokenizer()
        if (tok.name, tok.dict_name) != ("sudachipy-0.6.8", "sudachidict_core-20240109"):
            return "名前と版が違う: %s / %s" % (tok.name, tok.dict_name)
        if tok.read("青空がきれい") != "あおぞらがきれい":
            return "カタカナの読みがひらがなにならない: %s" % tok.read("青空がきれい")
        if tok.read("ヴァイオリンをひく") != "ゔぁいおりんをひく":
            return "ヴ・小書きのカタカナがひらがなにならない"
        if READING_RE.fullmatch(tok.read("※です")):
            return "読みが空の未知語（※）が表記のまま残らず、句に入ってしまう"
        if set(seen_modes) != {"MODE_C"}:
            return "分割モードが C ではない: %s" % sorted(set(seen_modes))
    finally:
        metadata.version = old_ver
        if old_mod is None:
            sys.modules.pop("sudachipy", None)
        else:
            sys.modules["sudachipy"] = old_mod
    return None


def _run_self(args, env_extra=None):
    env = dict(os.environ, PYTHONUTF8="1")
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def _t_cli():
    """cp932 のファイルを --src から読み、CLI で書き出す。in-process の結果とバイト一致・--validate が exit 0。"""
    tmp = tempfile.mkdtemp(prefix="build_corpus_selftest_")
    try:
        src = os.path.join(tmp, "src")
        os.mkdir(src)
        for name, text in (("Tst.txt", _tst_text()), ("b-2.txt", _many_text())):
            with open(os.path.join(src, name), "wb") as f:
                f.write(text.encode("cp932"))
        raw_table = _dumps(_TABLE).encode("utf-8")
        table = os.path.join(tmp, "table.json")
        with open(table, "wb") as f:
            f.write(raw_table)
        out = os.path.join(tmp, "out.jsonl")
        rc, text = _run_self(["--src", src, "--out", out, "--seed", "5", "--tokenizer", "table:" + table,
                              "--per-work", "5"])
        if rc != 0:
            return "CLI の書き出しが exit 0 でない（%d）: %s" % (rc, text.strip()[-200:])
        with open(out, "rb") as f:
            got = f.read()
        want = build_bytes(_works(), 5, TableTokenizer(_TABLE, hashlib.sha256(raw_table).hexdigest()),
                           DEFAULT_MIN, DEFAULT_MAX, 5)
        if got != want:
            return "CLI の出力が in-process の出力とバイト一致しない（cp932 / CRLF / 作品名の扱い）"
        if b"\r" in got or got.startswith(b"\xef\xbb\xbf"):
            return "出力に CR か BOM が入っている"
        if _rows(got)[0]["dict"] != hashlib.sha256(raw_table).hexdigest():
            return "table のヘッダの dict が表の SHA-256 でない"
        rc, text = _run_self(["--validate", out])
        if rc != 0:
            return "CLI の --validate が正しい出力で exit 0 でない（%d）: %s" % (rc, text.strip()[-200:])
        with open(out, "wb") as f:
            f.write(got.replace(b'"reading":"', '"reading":"亜'.encode("utf-8"), 1))
        rc, text = _run_self(["--validate", out])
        if rc != 1 or "Traceback" in text:
            return "読みに漢字を入れた出力が exit 1 で拒否されない（%d）" % rc
        rc, text = _run_self(["--validate", os.path.join(tmp, "missing.jsonl")])
        if rc != 2:
            return "存在しないファイルの --validate が exit 2 でない（%d）" % rc
        empty = os.path.join(tmp, "empty")
        os.mkdir(empty)
        rc, text = _run_self(["--src", empty, "--out", out, "--seed", "1", "--tokenizer", "table:" + table])
        if rc != 2:
            return ".txt の無い --src が exit 2 でない（%d）" % rc
        rc, text = _run_self(["--src", src, "--out", out, "--tokenizer", "table:" + table])
        if rc != 2:
            return "--seed が無いのが exit 2 でない（%d）" % rc
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _t_no_sudachi():
    """sudachipy を import できない環境で --tokenizer sudachi を選ぶと、Traceback ではなく exit 2 で止まる。"""
    tmp = tempfile.mkdtemp(prefix="build_corpus_selftest_")
    try:
        fake = os.path.join(tmp, "fake")
        src = os.path.join(tmp, "src")
        os.mkdir(fake)
        os.mkdir(src)
        with open(os.path.join(fake, "sudachipy.py"), "w") as f:
            f.write('raise ImportError("sudachipy is not available in this test")\n')
        with open(os.path.join(src, "tst.txt"), "wb") as f:
            f.write(_tst_text().encode("cp932"))
        rc, text = _run_self(["--src", src, "--out", os.path.join(tmp, "o.jsonl"), "--seed", "1",
                              "--tokenizer", "sudachi"], {"PYTHONPATH": fake})
        if rc != 2 or "Traceback" in text or "sudachipy" not in text:
            return "sudachipy が無いとき exit 2 と説明で止まらない（%d）: %s" % (rc, text.strip()[-200:])
        if os.path.exists(os.path.join(tmp, "o.jsonl")):
            return "止まったのに出力ファイルができている"
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _dump_lines(*objs):
    return "\n".join(_dumps(o) if isinstance(o, dict) else o for o in objs) + "\n"


def _hdr(**over):
    return dict({"kind": "header", "format": "corpus/1", "source": "aozora", "tokenizer": "table", "dict": "none"}, **over)


def _ph(pid="w1-1-1", **over):
    base = {"kind": "phrase", "phrase_id": pid, "work_id": "w1", "text": "青空", "reading": "あおぞら", "reading_len": 4}
    return dict(base, **over)


def _without(obj, key):
    return dict((k, v) for k, v in obj.items() if k != key)


def _validate_cases():
    """(名前, 中身, 期待する違反の種別)。期待が None なら通るべき。"""
    good = _dump_lines(_hdr(), _ph("w1-1-1"), _ph("w1-1-2", reading="ながいーよみ", reading_len=6))
    return [
        ("正しい corpus", good, None),
        ("正しい corpus（CRLF）", good.replace("\n", "\r\n"), None),
        ("読みに漢字", _dump_lines(_hdr(), _ph(reading="青空", reading_len=2)), "reading"),
        ("読みにカタカナ", _dump_lines(_hdr(), _ph(reading="アオゾラ", reading_len=4)), "reading"),
        ("読みに数字", _dump_lines(_hdr(), _ph(reading="あお3", reading_len=3)), "reading"),
        ("読みに英字", _dump_lines(_hdr(), _ph(reading="あおA", reading_len=3)), "reading"),
        ("読みが空", _dump_lines(_hdr(), _ph(reading="", reading_len=0)), "reading"),
        ("reading_len の不一致", _dump_lines(_hdr(), _ph(reading_len=5)), "reading_len"),
        ("reading_len が文字列", _dump_lines(_hdr(), _ph(reading_len="4")), "type"),
        ("reading_len が真偽値", _dump_lines(_hdr(), _ph(reading_len=True)), "type"),
        ("reading_len が小数", _dump_lines(_hdr(), '{"kind":"phrase","phrase_id":"w1-1-1","work_id":"w1","text":"青空",'
                                          '"reading":"あおぞら","reading_len":4.0}'), "float"),
        ("phrase_id の重複", _dump_lines(_hdr(), _ph("w1-1-1"), _ph("w1-1-1")), "dup_id"),
        ("phrase_id の形（大文字）", _dump_lines(_hdr(), _ph("P001-1-1", work_id="P001")), "phrase_id"),
        ("phrase_id の形（番号なし）", _dump_lines(_hdr(), _ph("w1")), "phrase_id"),
        ("phrase_id の作品名が work_id と違う", _dump_lines(_hdr(), _ph("w2-1-1")), "work_id_mismatch"),
        ("work_id が大文字", _dump_lines(_hdr(), _ph("W1-1-1", work_id="W1")), "work_id"),
        ("text が空", _dump_lines(_hdr(), _ph(text="")), "text"),
        ("ヘッダが無い（1 行目が句）", _dump_lines(_ph("w1-1-1")), "header"),
        ("format が違う", _dump_lines(_hdr(format="corpus/2"), _ph()), "format"),
        ("source が違う", _dump_lines(_hdr(source="other"), _ph()), "source"),
        ("tokenizer に空白", _dump_lines(_hdr(tokenizer="sudachi py"), _ph()), "name"),
        ("dict が 65 字", _dump_lines(_hdr(dict="a" * 65), _ph()), "name"),
        ("未知のキー", _dump_lines(_hdr(), _ph(extra=1)), "unknown_key"),
        ("必須キーが無い", _dump_lines(_hdr(), _without(_ph(), "work_id")), "missing_key"),
        ("同じキーが 2 回", _dump_lines(_hdr(), '{"kind":"phrase","kind":"phrase","phrase_id":"w1-1-1","work_id":"w1",'
                                          '"text":"青空","reading":"あおぞら","reading_len":4}'), "dup_key"),
        ("kind が違う", _dump_lines(_hdr(), _ph(kind="sentence")), "kind"),
        ("ヘッダが 2 つ", _dump_lines(_hdr(), _ph(), _hdr()), "second_header"),
        ("句が 0 件", _dump_lines(_hdr()), "no_phrase"),
        ("空のファイル", "", "empty"),
        ("行の途中の空行", _dump_lines(_hdr(), "", _ph()), "json"),
        ("壊れた JSON", _dump_lines(_hdr(), '{"kind":"phrase",'), "json"),
        ("行が配列", _dump_lines(_hdr(), "[1]"), "not_object"),
        ("BOM つき", b"\xef\xbb\xbf" + good.encode("utf-8"), "bom"),
        ("UTF-8 でない（cp932）", "あおぞら".encode("cp932"), "encoding"),
    ]


def _run_validate_cases(fails):
    n = 0
    for name, body, want in _validate_cases():
        n += 1
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        codes = set(c for _, c, _ in validate_corpus(data))
        if want is None:
            if codes:
                fails.append("validate「%s」: 通るべきなのに拒否: %s" % (name, sorted(codes)))
        elif not codes:
            fails.append("validate「%s」: 拒否されるべきなのに通った" % name)
        elif want not in codes:
            fails.append("validate「%s」: 別の理由で拒否された（期待 %s・実際 %s）" % (name, want, sorted(codes)))
    # 全キーの欠落を拒否する（表の取りこぼしを防ぐ）
    for k in HEADER_KEYS[1:]:
        n += 1
        if "missing_key" not in set(c for _, c, _ in validate_corpus(_dump_lines(_without(_hdr(), k), _ph()).encode("utf-8"))):
            fails.append("validate: ヘッダの必須キー %s が欠けても拒否されない" % k)
    for k in PHRASE_KEYS[1:]:
        n += 1
        if "missing_key" not in set(c for _, c, _ in validate_corpus(_dump_lines(_hdr(), _without(_ph(), k)).encode("utf-8"))):
            fails.append("validate: 句の必須キー %s が欠けても拒否されない" % k)
    return n


def _cases():
    return [
        ("注記とルビを除く", _t_annot_ruby),
        ("底本情報・記号の説明の枠・題を除く", _t_head_foot),
        ("同じ seed でバイト一致", _t_same_seed),
        ("seed を変えると変わる", _t_seed_changes),
        ("読みにカタカナ・数字・英字が残る句と長さが範囲外の句は捨てる", _t_dropped),
        ("読みの長さは min〜max・範囲を変えると句が入れ替わる", _t_length_range),
        ("短い節は隣と束ねて 1 句にする", _t_merge),
        ("引用符「」を外して句にする", _t_quotes),
        ("phrase_id は入力から決まる", _t_ids),
        ("作品ごとに K 句まで・本文の順", _t_per_work),
        ("ヘッダに tokenizer と dict を書く", _t_header),
        ("書き出したものを --validate が通す", _t_self_valid),
        ("sudachi の読みをひらがなにする（偽の sudachipy）", _t_sudachi_fake),
        ("cp932 のファイルを CLI で書き出す", _t_cli),
        ("sudachipy が無ければ exit 2 で止まる", _t_no_sudachi),
    ]


def selftest():
    fails = []
    n = 0
    for name, fn in _cases():
        n += 1
        try:
            msg = fn()
        except Exception as e:
            msg = "例外: %s: %s" % (type(e).__name__, e)
        if msg:
            fails.append("%s: %s" % (name, msg))
    n += _run_validate_cases(fails)
    if fails:
        for m in fails:
            print("FAIL " + m)
        print("selftest 失敗 %d 件 / %d 件" % (len(fails), n))
        return 1
    print("selftest OK（%d 件）" % n)
    return 0


# ---------------------------------------------------------------- CLI

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="青空文庫の句と読み（corpus/1）を作る前処理")
    ap.add_argument("--src", help="青空文庫の .txt（cp932）を置いたディレクトリ")
    ap.add_argument("--out", help="書き出す corpus/1 のファイル")
    ap.add_argument("--seed", type=int, help="作品ごとの抽出を決める seed（0 以上の整数）")
    ap.add_argument("--tokenizer", default="sudachi", help="sudachi（既定）または table:<json>")
    ap.add_argument("--min-reading", type=int, default=DEFAULT_MIN, help="句の読みの最小の長さ（既定 %d）" % DEFAULT_MIN)
    ap.add_argument("--max-reading", type=int, default=DEFAULT_MAX, help="句の読みの最大の長さ（既定 %d）" % DEFAULT_MAX)
    ap.add_argument("--per-work", type=int, default=DEFAULT_PER_WORK, help="作品ごとの最大句数（既定 %d）" % DEFAULT_PER_WORK)
    ap.add_argument("--validate", metavar="FILE", help="corpus/1 を検査する（違反で exit 1）")
    ap.add_argument("--selftest", action="store_true", help="辞書なしの自己検査")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.validate:
        return cmd_validate(args.validate)
    missing = [n for n in ("src", "out", "seed") if getattr(args, n) is None]
    if missing:
        ap.error("書き出しには --src --out --seed が要る（足りない: %s）" % " ".join("--" + m for m in missing))
    if args.seed < 0:
        ap.error("--seed は 0 以上")
    if args.min_reading < 1 or args.max_reading < args.min_reading or args.per_work < 1:
        ap.error("--min-reading は 1 以上・--max-reading は --min-reading 以上・--per-work は 1 以上")
    try:
        tok = make_tokenizer(args.tokenizer)
        works = read_works(args.src)
        data = build_bytes(works, args.seed, tok, args.min_reading, args.max_reading, args.per_work,
                           log=lambda m: print(m, file=sys.stderr))
    except BuildError as e:
        print("build_corpus.py: %s" % e, file=sys.stderr)
        return e.code
    with open(args.out, "wb") as f:
        f.write(data)
    print("書き出した: %s（tokenizer=%s dict=%s）" % (args.out, tok.name, tok.dict_name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
