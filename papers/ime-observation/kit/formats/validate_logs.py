#!/usr/bin/env python3
# kit: selftest
"""gt/1 と obs/1 の content-free 検査器（Python 標準ライブラリだけ）。

  validate_logs.py --kind gt|obs FILE...   違反を行番号つきで出して exit 1 / 違反なしなら exit 0
  validate_logs.py --selftest              陽性対照と陰性対照（速い既定・1 秒未満）

exit 2 は「検査できなかった」（使い方の誤り・ファイルが開けない）。違反 0 件とは区別する。
★ 0 以外はすべて不合格として扱うこと。違反が 1 件でもあれば、開けないファイルが混ざっていても exit 1 を返す。

ここが保証するのは gt と obs の行の**形**である: 文字列を値に持てるキーは FORMATS.md の列挙か
正規表現で縛り、未知のキーとエスケープ（バックスラッシュ）を拒否し、整数の位置に整数以外を置かせない。
⚠️ 保証の範囲外: 整数の欄・版の文字列・manifest_sha256 の**値の意味**（そこへ符号化された本文）は
   検査しない。content-free は生産側の設計（種別・長さ・時刻しか書かない）が担い、本検査器はその形を
   機械で確かめる。
⚠️ 違反の説明には**値を出さない**（本文が混じっていた場合に、検査器の出力から漏れないように）。
   出すのは違反の種類と、FORMATS.md に載っている既知のキー名だけ（未知のキー名は出さない）。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

U64_MAX = 2 ** 64 - 1
U32_MAX = 2 ** 32 - 1
I64_MIN = -(2 ** 63)

VERSION_RE = re.compile(r"[0-9A-Za-z.+-]{1,32}")
SHA256_RE = re.compile(r"[0-9A-Fa-f]{64}")
# ★ 単体ロガーの行の種類は 2 つだけ。3 つの配列を通して各名前は高々 1 回（＝合計 2 個まで）。
CAP_NAMES = ("key", "ime_shadow")

OS_NAMES = ("macos", "windows")
GT_SRCS = ("mac_nstic", "win_imm", "win_tsf")
CMDS = (
    "insertNewline:", "cancelOperation:", "deleteBackward:", "deleteForward:",
    "moveLeft:", "moveRight:", "moveUp:", "moveDown:", "insertTab:", "insertBacktab:",
    "noop:", "other",
)
UI_KINDS = ("candidate", "reading", "other")
ENUM_FIELDS = {"cmd": CMDS, "ui_kind": UI_KINDS}

# gt/1 の ev と付随フィールド: ev -> (必須, 省略可)。付随フィールドは整数（cmd / ui_kind だけ列挙）。
_COMMON_EVENTS = {
    "key_down": (("vk",), ()),
    "focus_in": ((), ()),
    "focus_out": ((), ()),
}
_NO_FIELDS = ((), ())
GT_EVENTS = {
    "mac_nstic": dict(
        _COMMON_EVENTS,
        set_marked=(("len", "sel_loc", "sel_len"), ("rep_loc", "rep_len")),
        insert_text=(("len",), ("rep_loc", "rep_len")),
        unmark=_NO_FIELDS,
        first_rect=_NO_FIELDS,
        do_command=(("cmd",), ()),
    ),
    "win_imm": dict(
        _COMMON_EVENTS,
        start_comp=_NO_FIELDS,
        end_comp=_NO_FIELDS,
        comp=(("flags", "comp_len", "result_len"), ()),
        notify=(("imn",), ()),
    ),
    "win_tsf": dict(
        _COMMON_EVENTS,
        tsf_start=_NO_FIELDS,
        tsf_end=((), ("result_len",)),
        tsf_update=(("len",), ()),
        ui_begin=(("ui_kind",), ()),
        ui_update=(("ui_kind",), ()),
        ui_end=(("ui_kind",), ()),
    ),
}
GT_HEADER_KEYS = ("kind", "format", "src", "app_version", "os")
GT_EVENT_BASE = ("kind", "t_wall_ms", "t_mono_ns", "ev")

# obs/1（GSE の NDJSON 行と同じ名前・同じ形）
OBS_CATEGORIES = (
    "alphabetic", "numeric", "punctuation", "sentence_punctuation", "tab", "backspace",
    "delete", "space", "enter", "navigation", "modifier", "function", "escape", "other",
)
OBS_HEADER_KEYS = ("type", "format", "os", "logger_version", "manifest_sha256", "capabilities")
CAP_KEYS = ("unconditional", "threshold_gated", "config_gated")
OBS_KEY_KEYS = ("type", "t", "category", "press")
OBS_SHADOW_KEYS = ("type", "t", "dwell_ms", "nav", "abandon")

# 違反の説明に出してよいキー名（FORMATS.md に載っている名前だけ）
KNOWN_KEYS = frozenset(
    GT_HEADER_KEYS + GT_EVENT_BASE + OBS_HEADER_KEYS + CAP_KEYS + OBS_KEY_KEYS + OBS_SHADOW_KEYS
    + tuple(k for table in GT_EVENTS.values() for req, opt in table.values() for k in req + opt)
)

MAX_SHOWN = 50


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
    for k, val in pairs:
        if k in d:
            raise _Reject("dup", "同じキーが 1 行に 2 回ある")
        d[k] = val
    return d


def _safe(name):
    """キー名を出してよいのは既知の名前のときだけ（本文がキー名に入っていても漏らさない）。"""
    if isinstance(name, str) and name in KNOWN_KEYS:
        return name
    return "（FORMATS.md に無い名前・表示しない）"


def _has_space_outside_strings(text):
    in_str = False
    esc = False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch in " \t\r\n":
            return True
    return False


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


class _Errs(object):
    def __init__(self):
        self.items = []

    def add(self, ln, code, msg):
        self.items.append((ln, code, msg))


def _check_keys(errs, ln, obj, required, optional):
    allowed = set(required) | set(optional)
    for k in obj:
        if k not in allowed:
            errs.add(ln, "unknown_key", "未知のキー: " + _safe(k))
    for k in required:
        if k not in obj:
            errs.add(ln, "missing_key", "必須のキーが無い: " + k)


def _check_int(errs, ln, key, v, lo=I64_MIN, hi=U64_MAX):
    if not _is_int(v):
        errs.add(ln, "type", "整数の位置に整数以外がある: " + key)
    elif v < lo or v > hi:
        errs.add(ln, "range", "整数が範囲の外: " + key)


def _check_bool(errs, ln, key, v):
    if not isinstance(v, bool):
        errs.add(ln, "type", "真偽値の位置に真偽値以外がある: " + key)


def _check_enum(errs, ln, key, v, allowed):
    if not isinstance(v, str):
        errs.add(ln, "type", "文字列の位置に文字列以外がある: " + key)
    elif v not in allowed:
        errs.add(ln, "enum", "値が列挙の外: " + key)


def _check_regex(errs, ln, key, v, rx):
    if not isinstance(v, str):
        errs.add(ln, "type", "文字列の位置に文字列以外がある: " + key)
    elif not rx.fullmatch(v):
        errs.add(ln, "regex", "値が正規表現に合わない: " + key)


def _check_fixed(errs, ln, code, key, v, want):
    if v != want:
        errs.add(ln, code, "値が規定と違う: " + key)


def _parse_line(raw, ln, errs):
    """1 行を検査して dict を返す。返せないときは None（理由は errs に入れる）。"""
    if raw.endswith(b"\r"):
        raw = raw[:-1]
    if b"\\" in raw:
        # 許される文字列値はどれも \ を含まない。エスケープで綴ると生の文字列で行を探す検査が素通りする
        errs.add(ln, "escape", "エスケープ（\\）がある（gt / obs の行はエスケープを使わない）")
        # 中身の検査は続ける（他の違反も一度に出す）
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        errs.add(ln, "utf8", "UTF-8 として読めない")
        return None
    try:
        obj = json.loads(text, object_pairs_hook=_no_dup, parse_float=_no_float,
                         parse_constant=_no_constant)
    except _Reject as e:
        errs.add(ln, e.code, str(e))
        return None
    except (ValueError, RecursionError):
        errs.add(ln, "json", "JSON として読めない（空行を含む）")
        return None
    if not isinstance(obj, dict):
        errs.add(ln, "type", "1 行 1 オブジェクトでなければならない")
        return None
    if _has_space_outside_strings(text):
        errs.add(ln, "sep", "文字列の外に空白がある（区切りに空白を入れない）")
        # 中身の検査は続ける（他の違反も一度に出す）
    return obj


def _check_gt_header(obj, ln, errs):
    _check_keys(errs, ln, obj, GT_HEADER_KEYS, ())
    _check_fixed(errs, ln, "header", "kind", obj.get("kind"), "header")
    if "format" in obj:
        _check_fixed(errs, ln, "format", "format", obj["format"], "gt/1")
    if "src" in obj:
        _check_enum(errs, ln, "src", obj["src"], GT_SRCS)
    if "app_version" in obj:
        _check_regex(errs, ln, "app_version", obj["app_version"], VERSION_RE)
    if "os" in obj:
        _check_enum(errs, ln, "os", obj["os"], OS_NAMES)
    src = obj.get("src")
    return src if isinstance(src, str) and src in GT_SRCS else None


def _check_gt_event(obj, ln, src, errs):
    kind = obj.get("kind")
    if kind != "ev":
        errs.add(ln, "kind", "2 行目以降の kind は ev だけ（ヘッダは 1 行目に 1 回）")
        return
    ev = obj.get("ev")
    if not isinstance(ev, str):
        errs.add(ln, "type", "文字列の位置に文字列以外がある: ev")
        return
    table = GT_EVENTS[src]
    if ev not in table:
        errs.add(ln, "ev", "この src では出ない ev、または未知の ev")
        return
    required, optional = table[ev]
    _check_keys(errs, ln, obj, GT_EVENT_BASE + tuple(required), optional)
    for k, v in obj.items():
        if k in ("kind", "ev"):
            continue
        if k in ENUM_FIELDS:
            _check_enum(errs, ln, k, v, ENUM_FIELDS[k])
        elif k in GT_EVENT_BASE or k in required or k in optional:
            _check_int(errs, ln, k, v)
        # それ以外のキーは _check_keys が unknown_key にした


def _check_capabilities(errs, ln, cap):
    if not isinstance(cap, dict):
        errs.add(ln, "type", "オブジェクトの位置にオブジェクト以外がある: capabilities")
        return
    _check_keys(errs, ln, cap, CAP_KEYS, ())
    seen = set()
    for k in CAP_KEYS:
        if k not in cap:
            continue
        names = cap[k]
        if not isinstance(names, list):
            errs.add(ln, "type", "配列の位置に配列以外がある: " + k)
            continue
        for n in names:
            _check_enum(errs, ln, k, n, CAP_NAMES)
            if isinstance(n, str) and n in CAP_NAMES:
                if n in seen:
                    errs.add(ln, "dup", "capabilities の同じ名前が 2 回以上ある: " + k)
                seen.add(n)


def _check_obs_header(obj, ln, errs):
    _check_keys(errs, ln, obj, OBS_HEADER_KEYS, ())
    _check_fixed(errs, ln, "header", "type", obj.get("type"), "meta")
    if "format" in obj:
        _check_fixed(errs, ln, "format", "format", obj["format"], "obs/1")
    if "os" in obj:
        _check_enum(errs, ln, "os", obj["os"], OS_NAMES)
    if "logger_version" in obj:
        _check_regex(errs, ln, "logger_version", obj["logger_version"], VERSION_RE)
    if "manifest_sha256" in obj:
        _check_regex(errs, ln, "manifest_sha256", obj["manifest_sha256"], SHA256_RE)
    if "capabilities" in obj:
        _check_capabilities(errs, ln, obj["capabilities"])


def _check_obs_line(obj, ln, errs):
    t = obj.get("type")
    if t == "key":
        _check_keys(errs, ln, obj, OBS_KEY_KEYS, ())
        if "t" in obj:
            _check_int(errs, ln, "t", obj["t"], 0, U64_MAX)
        if "category" in obj:
            _check_enum(errs, ln, "category", obj["category"], OBS_CATEGORIES)
        if "press" in obj:
            _check_bool(errs, ln, "press", obj["press"])
    elif t == "ime_shadow":
        _check_keys(errs, ln, obj, OBS_SHADOW_KEYS, ())
        if "t" in obj:
            _check_int(errs, ln, "t", obj["t"], 0, U64_MAX)
        if "dwell_ms" in obj:
            _check_int(errs, ln, "dwell_ms", obj["dwell_ms"], 0, U64_MAX)
        if "nav" in obj:
            _check_int(errs, ln, "nav", obj["nav"], 0, U32_MAX)
        if "abandon" in obj:
            _check_bool(errs, ln, "abandon", obj["abandon"])
    else:
        errs.add(ln, "type", "key / ime_shadow 以外の type（2 行目以降の meta を含む）")


def validate(kind, data):
    """bytes を検査して [(行番号, コード, 説明)] を返す。空なら違反なし。"""
    errs = _Errs()
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    if not lines:
        errs.add(0, "header", "空のファイル（1 行目にヘッダが要る）")
        return errs.items
    src = None
    for ln, raw in enumerate(lines, 1):
        obj = _parse_line(raw, ln, errs)
        if obj is None:
            continue
        if kind == "gt":
            if ln == 1:
                src = _check_gt_header(obj, ln, errs)
            elif src is not None:
                _check_gt_event(obj, ln, src, errs)
        elif ln == 1:
            _check_obs_header(obj, ln, errs)
        else:
            _check_obs_line(obj, ln, errs)
    return errs.items


# ---------------------------------------------------------------- selftest

def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _gt_header(src="mac_nstic", **over):
    h = {"kind": "header", "format": "gt/1", "src": src, "app_version": "0.1.0",
         "os": "macos" if src == "mac_nstic" else "windows"}
    h.update(over)
    return h


def _ev(name, **fields):
    d = {"kind": "ev", "t_wall_ms": 1, "t_mono_ns": 2, "ev": name}
    d.update(fields)
    return d


_ZERO64 = "0" * 64


def _obs_header(**over):
    h = {"type": "meta", "format": "obs/1", "os": "macos", "logger_version": "0.1.0",
         "manifest_sha256": _ZERO64,
         "capabilities": {"unconditional": ["key"], "threshold_gated": [],
                          "config_gated": ["ime_shadow"]}}
    h.update(over)
    return h


def _key(**over):
    d = {"type": "key", "t": 10, "category": "alphabetic", "press": True}
    d.update(over)
    return d


def _shadow(**over):
    d = {"type": "ime_shadow", "t": 20, "dwell_ms": 900, "nav": 0, "abandon": False}
    d.update(over)
    return d


def _text(*objs):
    """dict は _dump し、str はそのまま行にする。"""
    return "\n".join(o if isinstance(o, str) else _dump(o) for o in objs) + "\n"


def _positive_gt():
    mac = [
        _ev("key_down", vk=65), _ev("focus_in"), _ev("focus_out"),
        _ev("set_marked", len=3, sel_loc=3, sel_len=0),
        _ev("set_marked", len=3, sel_loc=3, sel_len=0, rep_loc=0, rep_len=2),
        _ev("insert_text", len=2), _ev("insert_text", len=2, rep_loc=0, rep_len=1),
        _ev("unmark"), _ev("first_rect"),
    ] + [_ev("do_command", cmd=c) for c in CMDS]
    imm = [
        _ev("key_down", vk=13), _ev("start_comp"), _ev("end_comp"),
        _ev("comp", flags=2048, comp_len=0, result_len=2), _ev("notify", imn=5),
    ]
    tsf = [
        _ev("key_down", vk=13), _ev("tsf_start"), _ev("tsf_end"), _ev("tsf_end", result_len=2),
        _ev("tsf_update", len=4),
    ] + [_ev(n, ui_kind=u) for n in ("ui_begin", "ui_update", "ui_end") for u in UI_KINDS]
    return {"mac_nstic": mac, "win_imm": imm, "win_tsf": tsf}


def _gt_cases():
    """(名前, 本文, 期待するコード。None は通るべき)"""
    mac_h = _gt_header()
    ok = [_ev("set_marked", len=3, sel_loc=3, sel_len=0)]
    cases = []
    for src, evs in _positive_gt().items():
        cases.append(("gt 正: " + src + "（全 ev）", _text(_gt_header(src), *evs), None))
    cases += [
        ("gt 正: ヘッダだけ", _text(mac_h), None),
        ("gt 正: CRLF の行末", _text(mac_h, *ok).replace("\n", "\r\n"), None),
        ("gt 正: 整数の上限（2^64-1）", _text(mac_h, _ev("insert_text", len=U64_MAX)), None),
    ]
    neg = [
        ("本文キー（text）", _text(mac_h, _ev("insert_text", len=3, text="日本語")), "unknown_key"),
        ("整数の位置の文字列（数字）", _text(mac_h, _ev("insert_text", len="3")), "type"),
        ("整数の位置の文字列（日本語）", _text(mac_h, _ev("insert_text", len="日本")), "type"),
        ("整数の位置の真偽値", _text(mac_h, _ev("insert_text", len=True)), "type"),
        ("整数の位置の配列", _text(mac_h, _ev("insert_text", len=[3])), "type"),
        ("整数の位置のオブジェクト", _text(mac_h, _ev("insert_text", len={"a": 1})), "type"),
        ("整数の位置の null", _text(mac_h, _ev("insert_text", len=None)), "type"),
        ("小数", _text(mac_h, _ev("insert_text", len=3.0)), "float"),
        ("整数の範囲外（2^64）", _text(mac_h, _ev("insert_text", len=U64_MAX + 1)), "range"),
        ("NaN", _text(mac_h, '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"insert_text","len":NaN}'),
         "constant"),
        ("列挙外の cmd", _text(mac_h, _ev("do_command", cmd="insertText:")), "enum"),
        ("cmd が文字列でない", _text(mac_h, _ev("do_command", cmd=3)), "type"),
        ("列挙外の ui_kind", _text(_gt_header("win_tsf"), _ev("ui_begin", ui_kind="日本語")), "enum"),
        ("未知のキー（ヘッダ）", _text(_gt_header(note="x")), "unknown_key"),
        ("未知のキー（日本語のキー名）", _text(mac_h, _ev("unmark", **{"日本語": 1})), "unknown_key"),
        ("未知のキー（ローマ字のキー名・名前を出さない）", _text(mac_h, _ev("unmark", nihongowokaku=1)),
         "unknown_key"),
        ("エスケープ（format の \\/）",
         _text('{"kind":"header","format":"gt\\/1","src":"mac_nstic","app_version":"0.1.0","os":"macos"}'),
         "escape"),
        ("エスケープ（ev の \\u）", _text(mac_h, '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"\\u0075nmark"}'),
         "escape"),
        ("エスケープ（キー名の \\u）",
         _text(mac_h, '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"unmark","t\\u0065xt":1}'), "escape"),
        ("ヘッダが無い", _text(*ok), "header"),
        ("空のファイル", "", "header"),
        ("format が違う", _text(_gt_header(format="gt/2")), "format"),
        ("app_version に日本語", _text(_gt_header(app_version="日本語")), "regex"),
        ("app_version が長すぎる", _text(_gt_header(app_version="1" * 33)), "regex"),
        ("app_version に空白", _text(_gt_header(app_version="0.1 0")), "regex"),
        ("app_version に末尾の改行", _text(_gt_header(app_version="0.1.0\n")), "regex"),
        ("src が列挙外", _text(_gt_header(src="win_foo")), "enum"),
        ("os が列挙外", _text(_gt_header(os="linux")), "enum"),
        ("この src に無い ev（mac に win の ev）", _text(mac_h, _ev("start_comp")), "ev"),
        ("この src に無い ev（imm に mac の ev）",
         _text(_gt_header("win_imm"), _ev("set_marked", len=1, sel_loc=0, sel_len=0)), "ev"),
        ("未知の ev", _text(mac_h, _ev("bogus")), "ev"),
        ("必須フィールドが無い", _text(mac_h, _ev("set_marked", len=3, sel_len=0)), "missing_key"),
        ("時刻が無い", _text(mac_h, '{"kind":"ev","t_wall_ms":1,"ev":"unmark"}'), "missing_key"),
        ("時刻が文字列", _text(mac_h, _ev("unmark", t_wall_ms="1")), "type"),
        ("なしのはずの ev に付随フィールド", _text(mac_h, _ev("unmark", len=1)), "unknown_key"),
        ("2 行目にヘッダ", _text(mac_h, mac_h), "kind"),
        ("未知の kind", _text(mac_h, {"kind": "foo"}), "kind"),
        ("途中の空行", _text(mac_h, "", *ok), "json"),
        ("オブジェクトでない行", _text(mac_h, "[1]"), "type"),
        ("区切りに空白（': '）", _text(mac_h, '{"kind": "ev","t_wall_ms":1,"t_mono_ns":2,"ev":"unmark"}'),
         "sep"),
        ("区切りに空白（', '）", _text(mac_h, '{"kind":"ev", "t_wall_ms":1,"t_mono_ns":2,"ev":"unmark"}'),
         "sep"),
        ("同じキーが 2 回", _text(mac_h, '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"insert_text",'
                                  '"len":3,"len":4}'), "dup"),
        ("UTF-8 でない", _text(mac_h).encode("utf-8") + b'{"kind":"ev","ev":"\xff"}\n', "utf8"),
    ]
    for name, body, code in neg:
        cases.append(("gt 誤: " + name, body, code))
    return cases


def _obs_cases():
    h = _obs_header()
    cases = [
        ("obs 正: meta ＋ key ＋ ime_shadow", _text(h, _key(), _shadow()), None),
        ("obs 正: ヘッダだけ", _text(h), None),
        ("obs 正: 14 種すべての category",
         _text(h, *[_key(category=c, press=bool(i % 2)) for i, c in enumerate(OBS_CATEGORIES)]), None),
        ("obs 正: os=windows ＋ 全部空の capabilities",
         _text(_obs_header(os="windows", capabilities={"unconditional": [], "threshold_gated": [],
                                                       "config_gated": []}), _key()), None),
        ("obs 正: 2 つの名前を同じ配列に",
         _text(_obs_header(capabilities={"unconditional": ["key", "ime_shadow"], "threshold_gated": [],
                                         "config_gated": []})), None),
        ("obs 正: CRLF の行末", _text(h, _key()).replace("\n", "\r\n"), None),
    ]
    caps = h["capabilities"]

    def cap(**over):
        c = dict(caps)
        c.update(over)
        return c

    neg = [
        ("category が 14 種の外", _text(h, _key(category="a")), "enum"),
        ("category が文字列でない", _text(h, _key(category=1)), "type"),
        ("ime_shadow に text キー", _text(h, _shadow(text="日本語")), "unknown_key"),
        ("key に vk キー（旧形式）", _text(h, _key(vk=65)), "unknown_key"),
        ("ヘッダが無い（key から始まる）", _text(_key(), _shadow()), "header"),
        ("空のファイル", "", "header"),
        ("format が違う", _text(_obs_header(format="obs/2")), "format"),
        ("os が列挙外", _text(_obs_header(os="linux")), "enum"),
        ("logger_version に日本語", _text(_obs_header(logger_version="日本語")), "regex"),
        ("manifest_sha256 が 63 桁", _text(_obs_header(manifest_sha256="0" * 63)), "regex"),
        ("manifest_sha256 が hex でない", _text(_obs_header(manifest_sha256="g" * 64)), "regex"),
        ("capabilities の名前が日本語", _text(_obs_header(capabilities=cap(config_gated=["日本語"]))),
         "enum"),
        ("capabilities の名前が大文字", _text(_obs_header(capabilities=cap(unconditional=["Key"]))),
         "enum"),
        ("capabilities の名前がローマ字の単語列",
         _text(_obs_header(capabilities=cap(unconditional=["watashi", "ha", "nihongo", "wo", "kaku"]))),
         "enum"),
        ("capabilities の名前が同じ配列で重複",
         _text(_obs_header(capabilities=cap(unconditional=["key", "key"]))), "dup"),
        ("capabilities の名前が別の配列で重複",
         _text(_obs_header(capabilities=cap(unconditional=["key"], config_gated=["key"]))), "dup"),
        ("capabilities の名前が文字列でない", _text(_obs_header(capabilities=cap(unconditional=[1]))),
         "type"),
        ("capabilities のキー欠落",
         _text(_obs_header(capabilities={"unconditional": ["key"], "config_gated": []})), "missing_key"),
        ("capabilities に未知のキー", _text(_obs_header(capabilities=cap(extra=[]))), "unknown_key"),
        ("capabilities の値が配列でない", _text(_obs_header(capabilities=cap(unconditional="key"))),
         "type"),
        ("capabilities がオブジェクトでない", _text(_obs_header(capabilities=["key"])), "type"),
        ("capabilities が無い", _text({k: v for k, v in h.items() if k != "capabilities"}), "missing_key"),
        ("未知の type", _text(h, {"type": "paste", "t": 1}), "type"),
        ("2 行目に meta", _text(h, h), "type"),
        ("press が整数", _text(h, _key(press=1)), "type"),
        ("press が文字列", _text(h, _key(press="true")), "type"),
        ("press が無い", _text(h, {"type": "key", "t": 10, "category": "space"}), "missing_key"),
        ("t が文字列", _text(h, _key(t="10")), "type"),
        ("t が負", _text(h, _key(t=-1)), "range"),
        ("nav が u32 の外", _text(h, _shadow(nav=U32_MAX + 1)), "range"),
        ("abandon が整数", _text(h, _shadow(abandon=0)), "type"),
        ("区切りに空白", _text(h, '{"type": "key","t":10,"category":"space","press":true}'), "sep"),
        ("エスケープ（type の \\u）", _text(h, '{"type":"k\\u0065y","t":10,"category":"space","press":true}'),
         "escape"),
        ("gt のヘッダを obs として検査", _text(_gt_header(), _ev("unmark")), "header"),
    ]
    for name, body, code in neg:
        cases.append(("obs 誤: " + name, body, code))
    return cases


def _as_bytes(body):
    return body if isinstance(body, bytes) else body.encode("utf-8")


# 陰性対照に埋めた本文の目印。違反の説明にこれが出たら漏れている
_LEAK_SENTINELS = ("日本", "insertText", "nihongo", "watashi")


def _run_cases(fails):
    n = 0
    for kind, cases in (("gt", _gt_cases()), ("obs", _obs_cases())):
        for name, body, want in cases:
            n += 1
            found = validate(kind, _as_bytes(body))
            codes = set(c for _, c, _ in found)
            if want is None:
                if found:
                    fails.append("%s: 通るべきなのに拒否: %s" % (name, sorted(codes)))
            elif not found:
                fails.append("%s: 拒否されるべきなのに通った" % name)
            elif want not in codes:
                fails.append("%s: 別の理由で拒否された（期待 %s・実際 %s）" % (name, want, sorted(codes)))
            else:
                # ⚠️ 説明に値（本文）も未知のキー名も出していないこと
                for _, _, msg in found:
                    if any(s in msg for s in _LEAK_SENTINELS):
                        fails.append("%s: 違反の説明に値が出ている: %s" % (name, msg))
    return n


def _run_sweep(fails):
    """table の全 ev で「必須が欠けたら拒否」「未知のキーが付いたら拒否」（table の取りこぼしを防ぐ）。"""
    n = 0
    for src, table in GT_EVENTS.items():
        for ev, (required, optional) in table.items():
            def fill(keys):
                return dict((k, ENUM_FIELDS[k][0] if k in ENUM_FIELDS else 1) for k in keys)
            base = fill(tuple(required))
            hdr = _gt_header(src)
            n += 1
            if validate("gt", _as_bytes(_text(hdr, _ev(ev, **base)))):
                fails.append("sweep %s/%s: 必須だけの行が拒否された" % (src, ev))
            n += 1
            if validate("gt", _as_bytes(_text(hdr, _ev(ev, **dict(base, **fill(tuple(optional))))))):
                fails.append("sweep %s/%s: 省略可も付けた行が拒否された" % (src, ev))
            for k in required:
                n += 1
                part = dict((kk, vv) for kk, vv in base.items() if kk != k)
                codes = set(c for _, c, _ in validate("gt", _as_bytes(_text(hdr, _ev(ev, **part)))))
                if "missing_key" not in codes:
                    fails.append("sweep %s/%s: 必須 %s が欠けても拒否されない" % (src, ev, k))
            n += 1
            codes = set(c for _, c, _ in validate("gt", _as_bytes(_text(hdr, _ev(ev, **dict(base, zz=1))))))
            if "unknown_key" not in codes:
                fails.append("sweep %s/%s: 未知のキーが拒否されない" % (src, ev))
    return n


def _run_cli(fails):
    """入口（exit code と行番号つきの出力）を実際に叩く。"""
    tmp = tempfile.mkdtemp(prefix="validate_logs_selftest_")
    me = os.path.abspath(__file__)
    env = dict(os.environ, PYTHONUTF8="1")
    good = os.path.join(tmp, "good.jsonl")
    leak = os.path.join(tmp, "leak.jsonl")
    with open(good, "wb") as f:
        f.write(_text(_gt_header(), _ev("insert_text", len=2)).encode("utf-8"))
    with open(leak, "wb") as f:
        f.write(_text(_gt_header(), _ev("insert_text", len=2),
                      _ev("insert_text", len=3, text="日本語")).encode("utf-8"))

    calls = [0]

    def run(*args):
        calls[0] += 1
        p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=env)
        return p.returncode, p.stdout.decode("utf-8", "replace")

    try:
        rc, out = run("--kind", "gt", good)
        if rc != 0:
            fails.append("CLI: 正しい gt が exit 0 でない（%d）: %s" % (rc, out.strip()[-200:]))
        rc, out = run("--kind", "gt", leak)
        if rc != 1:
            fails.append("CLI: 本文入りの gt が exit 1 でない（%d）" % rc)
        if ":3:" not in out:
            fails.append("CLI: 違反が行番号つきで出ない: %s" % out.strip()[-200:])
        if "日本語" in out:
            fails.append("CLI: 出力に本文が漏れている")
        rc, out = run("--kind", "obs", good)
        if rc != 1:
            fails.append("CLI: gt のファイルを obs として検査して exit 1 でない（%d）" % rc)
        rc, out = run("--kind", "gt", os.path.join(tmp, "missing.jsonl"))
        if rc != 2:
            fails.append("CLI: 存在しないファイルが exit 2 でない（%d）" % rc)
        rc, out = run("--kind", "gt", good, leak)
        if rc != 1:
            fails.append("CLI: 複数ファイルの一方が違反なら exit 1（実際 %d）" % rc)
        rc, out = run("--kind", "gt", os.path.join(tmp, "missing.jsonl"), leak)
        if rc != 1:
            fails.append("CLI: 開けないファイルと違反が重なったら exit 1 を優先（実際 %d）" % rc)
        rc, out = run("--kind", "bogus", good)
        if rc != 2:
            fails.append("CLI: 未知の --kind が exit 2 でない（%d）" % rc)
        rc, out = run("--kind", "gt")
        if rc != 2:
            fails.append("CLI: FILE が無いのが exit 2 でない（%d）" % rc)
        return calls[0]
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)


def selftest():
    fails = []
    n = _run_cases(fails) + _run_sweep(fails) + _run_cli(fails)
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
    ap = argparse.ArgumentParser(description="gt/1・obs/1 の content-free 検査器")
    ap.add_argument("--kind", choices=("gt", "obs"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.kind or not args.files:
        ap.error("--kind gt|obs と FILE が要る")
    violated = False
    unreadable = False
    for path in args.files:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            print("%s: 開けない（%s）" % (path, type(e).__name__), file=sys.stderr)
            unreadable = True
            continue
        found = validate(args.kind, data)
        for ln, code, msg in found[:MAX_SHOWN]:
            print("%s:%d: [%s] %s" % (path, ln, code, msg), file=sys.stderr)
        if len(found) > MAX_SHOWN:
            print("%s: …ほか %d 件" % (path, len(found) - MAX_SHOWN), file=sys.stderr)
        if found:
            violated = True
    # ★ 違反を優先する（exit 2 を「読み飛ばし」と扱う呼び出し側でも違反が赤になるように）
    if violated:
        return 1
    return 2 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
