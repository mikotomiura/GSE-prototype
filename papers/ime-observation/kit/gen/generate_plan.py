#!/usr/bin/env python3
# kit: selftest
"""シナリオ生成器: corpus/1 と recipes（OS ごとのキーの手順）から plan/1 を出す（Python 標準ライブラリだけ）。

  generate_plan.py --corpus F --recipes F --config F --os macos|windows --seed N --out F
  generate_plan.py --validate PLAN                                    plan/1 の検査（違反で exit 1）
  generate_plan.py --estimate --config F --recipes F --os OS [--corpus F]   1 セルの所要時間（秒）
  generate_plan.py --selftest                                         陽性・陰性対照（速い既定）

Exit: 0 = 成功 / 1 = --validate が違反を見つけた / 2 = 使い方の誤り・入力（設定・コーパス・recipes）が読めない。

★ 手順（どのキーをどの順に打つか）はコードではなく recipes.json のデータ。較正パイロットの後に直すのはデータだけ。
★ 速さ（キー間隔の分布）・思考の間・n の値は設定から読むだけで、ここでは決めない。
★ 決定性: 乱数は random() だけを使う（Python の版で変わりうる shuffle / choice / lognormvariate を使わない）。
  試行ごとの乱数は (seed, trial_id) から導く（trial_rng）ので、build_trial を同じ引数で直接呼ぶと計画の該当行と一致する。
  ⚠️ 浮動小数点の演算（log / exp / cos）は OS の数学ライブラリに依るので、バイト一致を保証するのは
  「同じ機械・同じ Python」での再生成まで。別の OS で作った計画は作り直さず、ファイルを配る。
公開する関数: build_trial(...)・load_recipes(path)・trial_rng(seed, trial_id)・load_corpus(path)・
  normalize_config(config)・plan_rows(...)・render_plan(rows)・validate_plan(data)・typed_reading(trial, recipes)。
"""
import argparse
import contextlib
import hashlib
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import romaji  # noqa: E402

GENERATOR_VERSION = "1.1.0"
SPEEDS = ("slow", "mid", "fast")
SCENARIOS = tuple("S%d" % i for i in range(1, 16))
OS_NAMES = ("macos", "windows")
KEYNAMES = frozenset(
    [chr(c) for c in range(ord("a"), ord("z") + 1)] + [str(d) for d in range(10)]
    + ["space", "enter", "esc", "backspace", "tab", "left", "right", "up", "down", "minus", "comma", "period",
       "ime_on", "ime_off"] + ["f%d" % i for i in range(13, 20)]
    + ["shift", "mouse_click", "focus_away", "focus_back"]
)
COMMITS = ("enter", "digit", "mouse", "none")
INTENT_KEYS = ("commit", "cand_index", "nav_count", "abandon", "predictive", "ime_toggle_mid", "focus_switch_mid",
               "expect_session")
INTENT_BOOLS = ("abandon", "predictive", "ime_toggle_mid", "focus_switch_mid", "expect_session")
TRIAL_KEYS = ("kind", "trial_id", "block_id", "scenario", "speed", "gap_before_ms", "think_ms", "phrase_id",
              "reading_len", "steps", "intent")
BLOCK_KEYS = ("kind", "block_id", "speed", "reset_ime", "marker", "marker_gap_ms")
HEADER_KEYS = ("kind", "format", "os", "seed", "generator_version", "config_sha256", "recipes_sha256",
               "corpus_sha256")

VERSION_RE = re.compile(r"^[0-9A-Za-z.+-]{1,32}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
TRIAL_ID_RE = re.compile(r"^t[0-9]{5,}$")
PHRASE_ID_RE = re.compile(r"^(?:[a-z0-9][a-z0-9_]{0,31}-[0-9]+-[0-9]+|kana-[0-9]+)$")
WORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,31}$")
DICT_RE = re.compile(r"^[0-9A-Za-z._+-]{1,64}$")
READING_RE = re.compile(r"^[ぁ-ゖー]+$")
SEED_MAX = 2 ** 63 - 1

# 時間の式（eval は使わない・この 3 つと整数リテラルだけ）
TIMES = {
    "cand_index+1": lambda v: v["cand_index"] + 1,
    "nav_count": lambda v: v["nav_count"],
    "reading_len": lambda v: v["reading_len"],
}
CONFIG_DEFAULTS = {"n_per_cell_scenario_speed": 75, "block_size": 25, "assumed_reading_len": 12,
                   "kana_len_min": 4, "kana_len_max": 8}
CONFIG_REQUIRED = ("speeds", "key_hold_ms", "think_ms", "cand_index_max", "nav_count_max", "inter_trial_ms",
                   "marker", "marker_gap_ms", "reset_ime_every_block")
CONFIG_KNOWN = frozenset(CONFIG_REQUIRED) | frozenset(CONFIG_DEFAULTS) | {"scenarios"}
ESTIMATE_BASE = "かんじへんかんのそくどをはかる"


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- 乱数（random() だけ）

def _derive(seed, tag):
    h = hashlib.sha256(("%d:%s" % (seed, tag)).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


def trial_rng(seed, trial_id):
    """試行ごとの乱数。(seed, trial_id) から決まるので、build_trial を直接呼んで計画の該当行を再現できる。"""
    return random.Random(_derive(seed, trial_id))


def _below(rng, k):
    return min(int(rng.random() * k), k - 1)


def _randint(rng, lo, hi):
    return lo + _below(rng, hi - lo + 1)


def _shuffle(rng, xs):
    for i in range(len(xs) - 1, 0, -1):
        j = _below(rng, i + 1)
        xs[i], xs[j] = xs[j], xs[i]


def _normal(rng):
    u1 = 1.0 - rng.random()
    u2 = rng.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def _draw_iki(rng, speed_cfg):
    """キー間隔（対数正規・中央値 iki_median_ms）を整数 ms で。"""
    v = speed_cfg["iki_median_ms"] * math.exp(speed_cfg["iki_sigma"] * _normal(rng))
    return max(1, int(round(v)))


def _draw_think(rng, think):
    """思考の間（対数一様）。"""
    lo, hi = think["min"], think["max"]
    v = math.exp(math.log(lo) + rng.random() * (math.log(hi) - math.log(lo)))
    return min(hi, max(lo, int(round(v))))


# ---------------------------------------------------------------- 設定

def unknown_config_keys(config):
    return sorted(k for k in config if k not in CONFIG_KNOWN and not str(k).startswith("_"))


def normalize_config(config):
    """既定値を補い、型と範囲を検査する（冪等）。不正は ValueError。"""
    if not isinstance(config, dict):
        raise ValueError("設定がオブジェクトではない")
    cfg = dict(CONFIG_DEFAULTS)
    cfg.update(config)
    missing = [k for k in CONFIG_REQUIRED if k not in cfg]
    if missing:
        raise ValueError("設定に無いキー: " + ", ".join(missing))

    def need_int(key, lo):
        if not _is_int(cfg[key]) or cfg[key] < lo:
            raise ValueError("設定 %s は %d 以上の整数" % (key, lo))

    need_int("n_per_cell_scenario_speed", 1)
    need_int("block_size", 1)
    need_int("assumed_reading_len", 2)
    need_int("kana_len_min", 1)
    need_int("kana_len_max", cfg["kana_len_min"])
    need_int("key_hold_ms", 1)
    need_int("cand_index_max", 0)
    need_int("nav_count_max", 0)
    need_int("inter_trial_ms", 0)
    need_int("marker_gap_ms", 0)
    if not isinstance(cfg["reset_ime_every_block"], bool):
        raise ValueError("設定 reset_ime_every_block は真偽値")
    sp = cfg["speeds"]
    if not isinstance(sp, dict):
        raise ValueError("設定 speeds はオブジェクト")
    for name in SPEEDS:
        s = sp.get(name)
        if not isinstance(s, dict) or not _is_num(s.get("iki_median_ms")) or s["iki_median_ms"] <= 0 \
                or not _is_num(s.get("iki_sigma")) or s["iki_sigma"] < 0:
            raise ValueError("設定 speeds.%s は iki_median_ms（> 0）と iki_sigma（>= 0）を持つ" % name)
    th = cfg["think_ms"]
    if not isinstance(th, dict) or not _is_int(th.get("min")) or not _is_int(th.get("max")) \
            or th["min"] < 1 or th["max"] < th["min"]:
        raise ValueError("設定 think_ms は 1 <= min <= max の整数")
    mk = cfg["marker"]
    if not isinstance(mk, list) or any(k not in KEYNAMES for k in mk):
        raise ValueError("設定 marker は keyname の配列")
    if cfg.get("scenarios") is not None:
        sc = cfg["scenarios"]
        if not isinstance(sc, list) or not sc or len(set(sc)) != len(sc) or any(s not in SCENARIOS for s in sc):
            raise ValueError("設定 scenarios は S1〜S15 の重複しない空でない配列")
    return cfg


# ---------------------------------------------------------------- recipes

def _check_step_element(where, el, params):
    if not isinstance(el, dict):
        raise ValueError("%s: 手順の要素がオブジェクトではない" % where)
    if "type_reading" in el:
        extra = set(el) - {"type_reading", "part", "input"}
        if el["type_reading"] is not True or extra:
            raise ValueError("%s: type_reading の書式" % where)
        if el.get("part", "all") not in ("all", "first_half"):
            raise ValueError("%s: part は all か first_half" % where)
        if el.get("input", "romaji") not in ("romaji", "kana"):
            raise ValueError("%s: input は romaji か kana" % where)
    elif "key" in el:
        if set(el) != {"key"} or el["key"] not in KEYNAMES:
            raise ValueError("%s: key の書式・keyname" % where)
    elif "repeat" in el:
        if set(el) != {"repeat", "times"} or el["repeat"] not in KEYNAMES:
            raise ValueError("%s: repeat の書式・keyname" % where)
        t = el["times"]
        if not (_is_int(t) and t >= 0) and t not in TIMES:
            raise ValueError("%s: times は 0 以上の整数か %s" % (where, "/".join(sorted(TIMES))))
        for need in ("cand_index", "nav_count"):
            if t == need or t == need + "+1":
                if need not in params:
                    raise ValueError("%s: times が params に無い %s を使う" % (where, need))
    elif "digit" in el:
        if set(el) != {"digit"} or el["digit"] != "cand_index+1" or "cand_index" not in params:
            raise ValueError("%s: digit は cand_index+1 だけ（params に cand_index が要る）" % where)
    elif "pause" in el:
        if set(el) != {"pause"} or el["pause"] != "think":
            raise ValueError("%s: pause は think だけ" % where)
    elif "pause_ms" in el:
        if set(el) != {"pause_ms"} or not _is_int(el["pause_ms"]) or el["pause_ms"] < 0:
            raise ValueError("%s: pause_ms は 0 以上の整数" % where)
    else:
        raise ValueError("%s: 未知の手順の要素" % where)


def check_recipes(data):
    if not isinstance(data, dict):
        raise ValueError("recipes がオブジェクトではない")
    layout = data.get("kana_layout")
    if not isinstance(layout, dict) or not layout:
        raise ValueError("recipes.kana_layout が無い")
    for k, v in layout.items():
        if k not in KEYNAMES or not isinstance(v, str) or len(v) != 1 or not READING_RE.fullmatch(v):
            raise ValueError("recipes.kana_layout の項目が不正")
    if len(set(layout.values())) != len(layout):
        raise ValueError("recipes.kana_layout に同じかなが 2 つのキーにある")
    table = data.get("os")
    if not isinstance(table, dict) or set(table) != set(OS_NAMES):
        raise ValueError("recipes.os は macos と windows の両方を持つ")
    for os_name in OS_NAMES:
        for sc, entry in table[os_name].items():
            where = "recipes.os.%s.%s" % (os_name, sc)
            if sc not in SCENARIOS or not isinstance(entry, dict):
                raise ValueError("%s: シナリオ名・書式" % where)
            extra = set(entry) - {"steps", "intent", "params", "default_enabled", "reading_len"}
            if extra or "steps" not in entry or "intent" not in entry:
                raise ValueError("%s: キー（steps・intent が要る／未知のキー）" % where)
            params = entry.get("params", {})
            for name, spec in params.items():
                if name not in ("cand_index", "nav_count") or not isinstance(spec, dict) \
                        or not _is_int(spec.get("min")) or set(spec) - {"min", "max", "cap"} \
                        or not (_is_int(spec.get("max")) or spec.get("max") in ("cand_index_max", "nav_count_max")):
                    raise ValueError("%s: params の書式" % where)
            if not isinstance(entry["steps"], list):
                raise ValueError("%s: steps が配列でない" % where)
            for i, el in enumerate(entry["steps"]):
                _check_step_element("%s.steps[%d]" % (where, i), el, params)
            it = entry["intent"]
            if not isinstance(it, dict) or set(it) != set(INTENT_KEYS):
                raise ValueError("%s: intent は 8 キーをすべて持つ" % where)
            for k, v in it.items():
                if isinstance(v, dict):
                    if set(v) != {"$param"} or v["$param"] not in params:
                        raise ValueError("%s: intent.%s の $param" % (where, k))
                    continue
                if k == "commit":
                    if v not in COMMITS:
                        raise ValueError("%s: intent.commit が列挙外" % where)
                elif k == "cand_index":
                    if v is not None and not (_is_int(v) and v >= 0):
                        raise ValueError("%s: intent.cand_index が 0 以上の整数か null でない" % where)
                elif k == "nav_count":
                    if not (_is_int(v) and v >= 0):
                        raise ValueError("%s: intent.nav_count が 0 以上の整数でない" % where)
                elif k in INTENT_BOOLS:
                    if not isinstance(v, bool):
                        raise ValueError("%s: intent.%s が真偽値でない" % (where, k))
            if "default_enabled" in entry and not isinstance(entry["default_enabled"], bool):
                raise ValueError("%s: default_enabled は真偽値" % where)
            rl = entry.get("reading_len")
            if rl is not None:
                rl_bad = not isinstance(rl, dict) or not rl or set(rl) - {"min", "max"} \
                    or ("min" in rl and not (_is_int(rl["min"]) and rl["min"] >= 1)) \
                    or ("max" in rl and not (_is_int(rl["max"]) and rl["max"] >= 1)) \
                    or ("min" in rl and "max" in rl and rl["min"] > rl["max"])
                if rl_bad:
                    raise ValueError("%s: reading_len は {min?, max?}（1 以上の整数・min<=max）" % where)
    return data


def load_recipes(path):
    with open(path, "rb") as f:
        data = json.loads(f.read().decode("utf-8"))
    return check_recipes(data)


def _entry(recipes, os_name, scenario):
    if os_name not in OS_NAMES:
        raise ValueError("os は macos か windows")
    entry = recipes["os"][os_name].get(scenario)
    if entry is None:
        raise ValueError("%s に %s の手順が無い" % (os_name, scenario))
    if not entry["steps"]:
        raise ValueError("%s の手順が未定義（recipes の steps が空）" % scenario)
    return entry


def _uses_kana(entry):
    return any(el.get("input") == "kana" for el in entry["steps"] if "type_reading" in el)


def _uses_think(entry):
    return any(el.get("pause") == "think" for el in entry["steps"])


# ---------------------------------------------------------------- 1 試行

def build_trial(phrase, scenario, speed, os_name, recipes, config, rng, trial_id, block_id):
    """plan/1 の試行行 1 つ（dict）を返す。乱数は rng.random() だけを使う。"""
    cfg = normalize_config(config)
    if speed not in SPEEDS:
        raise ValueError("speed は slow / mid / fast")
    entry = _entry(recipes, os_name, scenario)
    reading = phrase["reading"]
    if not reading or not READING_RE.fullmatch(reading):
        raise ValueError("phrase.reading はひらがなだけ")
    if phrase.get("reading_len", len(reading)) != len(reading):
        raise ValueError("phrase.reading_len が reading の長さと違う")
    speed_cfg = cfg["speeds"][speed]
    hold = cfg["key_hold_ms"]
    v = {"reading_len": len(reading)}
    for name in sorted(entry.get("params", {})):
        spec = entry["params"][name]
        hi = spec["max"] if _is_int(spec["max"]) else cfg[spec["max"]]
        if "cap" in spec:
            hi = min(hi, spec["cap"])
        if hi < spec["min"]:
            raise ValueError("%s の %s の範囲が空（設定の上限が小さい）" % (scenario, name))
        v[name] = _randint(rng, spec["min"], hi)
    think = _draw_think(rng, cfg["think_ms"]) if _uses_think(entry) else 0

    # 手順を「キー」と「次のキーまでの間」に展開する
    seq = []
    for el in entry["steps"]:
        if "type_reading" in el:
            part = reading
            if el.get("part") == "first_half":
                part = reading[:max(1, len(reading) // 2)]
            if el.get("input") == "kana":
                inv = dict((c, k) for k, c in recipes["kana_layout"].items())
                if any(c not in inv for c in part):
                    raise ValueError("かな配列で打てない文字がある（phrase %s）" % phrase.get("phrase_id"))
                keys = [inv[c] for c in part]
            else:
                keys = romaji.to_keys(part)
            seq.extend(("key", k) for k in keys)
        elif "key" in el:
            seq.append(("key", el["key"]))
        elif "repeat" in el:
            t = el["times"]
            n = t if _is_int(t) else TIMES[t](v)
            seq.extend(("key", el["repeat"]) for _ in range(n))
        elif "digit" in el:
            d = TIMES[el["digit"]](v)
            if not 1 <= d <= 9:
                raise ValueError("数字キーで選べる候補は 1〜9 番")
            seq.append(("key", str(d)))
        elif el.get("pause") == "think":
            seq.append(("pause", think))
        elif "pause_ms" in el:
            seq.append(("pause", el["pause_ms"]))

    steps = []
    t = 0
    override = None
    first = True
    for kind, val in seq:
        if kind == "pause":
            if not first:
                override = val
            continue
        if not first:
            gap = override if override is not None else _draw_iki(rng, speed_cfg)
            t += max(gap, hold + 1)
        override = None
        first = False
        steps.append({"key": val, "at_ms": t, "down": True})
        steps.append({"key": val, "at_ms": t + hold, "down": False})
    if not steps:
        raise ValueError("手順から送るキーが 1 つも出ない")

    intent = {}
    for k in INTENT_KEYS:
        val = entry["intent"][k]
        intent[k] = v[val["$param"]] if isinstance(val, dict) else val
    return {"kind": "trial", "trial_id": trial_id, "block_id": block_id, "scenario": scenario, "speed": speed,
            "gap_before_ms": cfg["inter_trial_ms"], "think_ms": think if _uses_think(entry) else 0,
            "phrase_id": phrase["phrase_id"], "reading_len": len(reading), "steps": steps, "intent": intent}


_ROMAJI_READING_KEYS = frozenset("abcdefghijklmnopqrstuvwxyz") | {"minus"}


def _trial_uses_kana(scenario, recipes):
    """そのシナリオが（どちらかの OS で）かな入力かを recipes から見る。os_name を trial は持たない。"""
    for os_name in OS_NAMES:
        entry = recipes["os"].get(os_name, {}).get(scenario)
        if entry is not None:
            return _uses_kana(entry)
    return False


def typed_reading(trial, recipes):
    """plan/1 の試行行 1 つから、実際に打った読みをひらがなで返す（steps の down だけを見る）。
    ローマ字入力は romaji.from_keys の逆写像、かな入力（S12）は recipes.kana_layout の逆引き。
    読みの打鍵は、そのシナリオで読みの打鍵に使わないキーが最初に来た所で終わる
    （ローマ字は a-z / minus 以外、かな入力は kana_layout のキー以外）。通常は句の読み全体、
    S10 は前半だけ、S12 は合成かな列を含めそのまま返る。"""
    downs = [s["key"] for s in trial["steps"] if s["down"]]
    if _trial_uses_kana(trial["scenario"], recipes):
        layout = recipes["kana_layout"]
        keys = []
        for k in downs:
            if k not in layout:
                break
            keys.append(k)
        return "".join(layout[k] for k in keys)
    keys = []
    for k in downs:
        if k not in _ROMAJI_READING_KEYS:
            break
        keys.append(k)
    return romaji.from_keys(keys)


# ---------------------------------------------------------------- コーパス

def load_corpus(path):
    """corpus/1 を読む（違反は ValueError・値は出さない）。"""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raise ValueError("コーパスに BOM がある")
    lines = raw.decode("utf-8").split("\n")
    phrases = []
    seen = set()
    for ln, line in enumerate(lines, start=1):
        line = line.rstrip("\r")
        if not line:
            if ln == len(lines):
                continue
            raise ValueError("コーパス %d 行目: 空行" % ln)
        try:
            obj = json.loads(line)
        except ValueError:
            raise ValueError("コーパス %d 行目: JSON として読めない" % ln)
        if ln == 1:
            if not isinstance(obj, dict) or obj.get("kind") != "header" or obj.get("format") != "corpus/1" \
                    or not isinstance(obj.get("tokenizer"), str) or not DICT_RE.fullmatch(obj["tokenizer"]) \
                    or not isinstance(obj.get("dict"), str) or not DICT_RE.fullmatch(obj["dict"]):
                raise ValueError("コーパスのヘッダが corpus/1 でない")
            continue
        ok = isinstance(obj, dict) and obj.get("kind") == "phrase" and isinstance(obj.get("phrase_id"), str) \
            and isinstance(obj.get("work_id"), str) and isinstance(obj.get("reading"), str)
        if ok:
            ok = PHRASE_ID_RE.fullmatch(obj["phrase_id"]) and WORK_ID_RE.fullmatch(obj["work_id"]) \
                and obj["phrase_id"].startswith(obj["work_id"] + "-") and READING_RE.fullmatch(obj["reading"]) \
                and _is_int(obj.get("reading_len")) and obj["reading_len"] == len(obj["reading"]) \
                and isinstance(obj.get("text"), str) and not obj["phrase_id"].startswith("kana-")
        if not ok:
            raise ValueError("コーパス %d 行目: 句の行が corpus/1 の型に合わない" % ln)
        if obj["phrase_id"] in seen:
            raise ValueError("コーパス %d 行目: phrase_id の重複" % ln)
        seen.add(obj["phrase_id"])
        phrases.append(obj)
    if not phrases:
        raise ValueError("コーパスに句が無い")
    return phrases


# ---------------------------------------------------------------- 計画

class _Pool(object):
    """句の取り出し口。cycle なら尽きたら並べ直して繰り返す。cycle でなければ尽きたら None。"""

    def __init__(self, phrases, rng, cycle):
        self.phrases = list(phrases)
        self.rng = rng
        self.cycle = cycle
        self.order = []
        self.pos = 0
        self._refill()

    def _refill(self):
        self.order = list(self.phrases)
        _shuffle(self.rng, self.order)
        self.pos = 0

    def next(self):
        if self.pos >= len(self.order):
            if not self.cycle or not self.phrases:
                return None
            self._refill()
        p = self.order[self.pos]
        self.pos += 1
        return p


def enabled_scenarios(recipes, cfg, os_name):
    """有効なシナリオの一覧と警告の列を返す（stderr には出さない。呼び出し側が出す）。"""
    table = recipes["os"][os_name]
    warnings = []
    if cfg.get("scenarios") is None:
        return [s for s in SCENARIOS if s in table and table[s].get("default_enabled", True)], warnings
    out = []
    for s in cfg["scenarios"]:
        if s in table:
            out.append(s)
        else:
            warnings.append("%s に %s の手順が無いので飛ばす" % (os_name, s))
    return out, warnings


def plan_rows(corpus, recipes, config, os_name, seed, config_sha256, recipes_sha256, corpus_sha256, warnings=None):
    """計画の行（dict の列）と {trial_id: 句} を返す。stderr には出さない。
    `warnings` にリストを渡すと、飛ばしたシナリオなどの注意を追記する（呼び出し側が出す）。"""
    cfg = normalize_config(config)
    if os_name not in OS_NAMES:
        raise ValueError("os は macos か windows")
    if not _is_int(seed) or not 0 <= seed <= SEED_MAX:
        raise ValueError("seed は 0〜2^63-1 の整数")
    scen, scen_warnings = enabled_scenarios(recipes, cfg, os_name)
    if warnings is not None:
        warnings.extend(scen_warnings)
    if not scen:
        raise ValueError("有効なシナリオが 1 つも無い")
    for s in scen:
        _entry(recipes, os_name, s)
    layout = recipes["kana_layout"]
    inv = dict((c, k) for k, c in layout.items())
    typable = [p for p in corpus if all(c in inv for c in p["reading"])]
    prng = random.Random(_derive(seed, "plan"))
    n = cfg["n_per_cell_scenario_speed"]
    synth_ids = {}
    layout_chars = sorted(inv)

    def synth():
        length = _randint(prng, cfg["kana_len_min"], cfg["kana_len_max"])
        reading = "".join(layout_chars[_below(prng, len(layout_chars))] for _ in range(length))
        if reading not in synth_ids:
            synth_ids[reading] = len(synth_ids) + 1
        return {"phrase_id": "kana-%d" % synth_ids[reading], "work_id": "kana", "text": "", "reading": reading,
                "reading_len": length}

    specs = dict((sp, []) for sp in SPEEDS)
    for s in scen:
        entry = recipes["os"][os_name][s]
        kana = _uses_kana(entry)
        rl = entry.get("reading_len", {})
        lo, hi = rl.get("min", 1), rl.get("max", 10 ** 9)
        eligible = [p for p in (typable if kana else corpus) if lo <= p["reading_len"] <= hi]
        if not eligible and not kana:
            raise ValueError("%s の要求（読みの長さ）に合う句がコーパスに無い" % s)
        pool = _Pool(eligible, prng, cycle=not kana)
        for sp in SPEEDS:
            for _ in range(n):
                ph = pool.next()
                if ph is None:
                    ph = synth()
                specs[sp].append((s, ph))
    blocks = []
    for sp in SPEEDS:
        lst = specs[sp]
        _shuffle(prng, lst)
        for i in range(0, len(lst), cfg["block_size"]):
            blocks.append((sp, lst[i:i + cfg["block_size"]]))
    _shuffle(prng, blocks)

    rows = [{"kind": "header", "format": "plan/1", "os": os_name, "seed": seed,
             "generator_version": GENERATOR_VERSION, "config_sha256": config_sha256,
             "recipes_sha256": recipes_sha256, "corpus_sha256": corpus_sha256}]
    phrases = {}
    n_trial = 0
    for bid, (sp, items) in enumerate(blocks):
        rows.append({"kind": "block", "block_id": bid, "speed": sp, "reset_ime": cfg["reset_ime_every_block"],
                     "marker": list(cfg["marker"]), "marker_gap_ms": cfg["marker_gap_ms"]})
        for s, ph in items:
            n_trial += 1
            tid = "t%05d" % n_trial
            rows.append(build_trial(ph, s, sp, os_name, recipes, cfg, trial_rng(seed, tid), tid, bid))
            phrases[tid] = ph
    return rows, phrases


def render_plan(rows):
    """計画のバイト列（UTF-8・LF・BOM なし）。"""
    return ("\n".join(dumps(r) for r in rows) + "\n").encode("utf-8")


# ---------------------------------------------------------------- 見積もり

def estimate(config, recipes, os_name, corpus=None):
    """1 セルの所要時間（全ステップ ＋ 試行間 ＋ マーカー）を (秒, 説明の行) で返す。"""
    cfg = normalize_config(config)
    assumed = cfg["assumed_reading_len"]
    note = "読みの長さ: コーパスの句"
    if corpus is None:
        reading = (ESTIMATE_BASE * (assumed // len(ESTIMATE_BASE) + 1))[:assumed]
        corpus = [{"phrase_id": "est-1-1", "work_id": "est", "text": "", "reading": reading, "reading_len": assumed}]
        cfg = dict(cfg, kana_len_min=assumed, kana_len_max=assumed)
        note = "読みの長さ: %d 字と仮定（設定 assumed_reading_len）" % assumed
    rows, _ = plan_rows(corpus, recipes, cfg, os_name, 0, "0" * 64, "0" * 64, "0" * 64)
    trial_ms = gap_ms = marker_ms = n_trial = n_block = 0
    for r in rows:
        if r["kind"] == "trial":
            n_trial += 1
            trial_ms += r["steps"][-1]["at_ms"]
            gap_ms += r["gap_before_ms"]
        elif r["kind"] == "block":
            n_block += 1
            marker_ms += len(r["marker"]) * r["marker_gap_ms"]
    total = (trial_ms + gap_ms + marker_ms) / 1000.0
    lines = ["試行 %d 件・ブロック %d 個（%s）" % (n_trial, n_block, note),
             "試行の中 %.1f 秒 ＋ 試行間 %.1f 秒 ＋ マーカー %.1f 秒（IME のリセット・起動は含まない）"
             % (trial_ms / 1000.0, gap_ms / 1000.0, marker_ms / 1000.0),
             "1 試行あたり %.2f 秒" % (total / n_trial if n_trial else 0.0),
             "合計（秒）："]
    return total, lines


# ---------------------------------------------------------------- 検査

class _Reject(ValueError):
    pass


def _no_dups(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise _Reject("dup_key")
        d[k] = v
    return d


def _reject_number(_s):
    raise _Reject("float")


def validate_plan(data):
    """plan/1 の検査。[(行番号, コード, 説明)] を返す（空なら違反なし）。説明に値は出さない。"""
    found = []

    def bad(ln, code, msg):
        found.append((ln, code, msg))

    if data[:3] == b"\xef\xbb\xbf":
        bad(1, "bom", "UTF-8 の BOM がある")
        return found
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        bad(1, "encoding", "UTF-8 として読めない")
        return found
    if not text:
        bad(1, "empty", "空のファイル")
        return found
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()

    def keys_ok(ln, obj, expected, what):
        miss = [k for k in expected if k not in obj]
        extra = [k for k in obj if k not in expected]
        if miss:
            bad(ln, "missing_key", "%s に足りないキー: %s" % (what, ",".join(miss)))
        if extra:
            bad(ln, "extra_key", "%s に未知のキーがある（%d 個）" % (what, len(extra)))
        return not miss and not extra

    blocks = []          # (block_id の値, speed, 行番号, 試行数の入れ物)
    n_trials = 0
    for ln, raw in enumerate(lines, start=1):
        line = raw[:-1] if raw.endswith("\r") else raw
        if not line:
            bad(ln, "blank", "空行がある")
            continue
        if chr(92) in line:
            bad(ln, "escape", "行にバックスラッシュがある（エスケープは使わない）")
            continue
        try:
            obj = json.loads(line, object_pairs_hook=_no_dups, parse_float=_reject_number,
                             parse_constant=_reject_number)
        except _Reject as e:
            bad(ln, str(e), "重複キーまたは整数でない数がある")
            continue
        except (ValueError, RecursionError):
            bad(ln, "json", "JSON として読めない")
            continue
        if not isinstance(obj, dict):
            bad(ln, "type", "オブジェクトではない")
            continue
        if dumps(obj) != line:
            bad(ln, "format", "区切りの空白・エスケープ・数の書式が正規形（空白なし・エスケープなし）でない")
        if ln == 1:
            if not keys_ok(ln, obj, HEADER_KEYS, "ヘッダ"):
                continue
            if obj["kind"] != "header" or obj["format"] != "plan/1":
                bad(ln, "header", "1 行目が plan/1 のヘッダでない")
            if obj["os"] not in OS_NAMES:
                bad(ln, "header", "os が列挙外")
            if not _is_int(obj["seed"]) or not 0 <= obj["seed"] <= SEED_MAX:
                bad(ln, "header", "seed が 0〜2^63-1 の整数でない")
            if not isinstance(obj["generator_version"], str) or not VERSION_RE.fullmatch(obj["generator_version"]):
                bad(ln, "header", "generator_version の書式")
            if not isinstance(obj["config_sha256"], str) or not SHA_RE.fullmatch(obj["config_sha256"]):
                bad(ln, "header", "config_sha256 が小文字 16 進 64 桁でない")
            if not isinstance(obj["recipes_sha256"], str) or not SHA_RE.fullmatch(obj["recipes_sha256"]):
                bad(ln, "header", "recipes_sha256 が小文字 16 進 64 桁でない")
            if not isinstance(obj["corpus_sha256"], str) or not SHA_RE.fullmatch(obj["corpus_sha256"]):
                bad(ln, "header", "corpus_sha256 が小文字 16 進 64 桁でない")
            continue
        kind = obj.get("kind")
        if kind == "block":
            if not keys_ok(ln, obj, BLOCK_KEYS, "ブロック"):
                continue
            if obj["block_id"] != len(blocks) or not _is_int(obj["block_id"]):
                bad(ln, "block_id", "block_id が 0 からの連番でない")
            if obj["speed"] not in SPEEDS:
                bad(ln, "speed", "ブロックの speed が列挙外")
            if not isinstance(obj["reset_ime"], bool):
                bad(ln, "type", "reset_ime が真偽値でない")
            if not isinstance(obj["marker"], list) or any(
                    not isinstance(k, str) or k not in KEYNAMES for k in obj["marker"]):
                bad(ln, "keyname", "marker に keyname でない要素がある")
            if not _is_int(obj["marker_gap_ms"]) or obj["marker_gap_ms"] < 0:
                bad(ln, "type", "marker_gap_ms が 0 以上の整数でない")
            blocks.append([obj["block_id"], obj["speed"], ln, 0])
        elif kind == "trial":
            n_trials += 1
            if not keys_ok(ln, obj, TRIAL_KEYS, "試行"):
                continue
            if not isinstance(obj["trial_id"], str) or not TRIAL_ID_RE.fullmatch(obj["trial_id"]) \
                    or obj["trial_id"] != "t%05d" % n_trials:
                bad(ln, "trial_id", "trial_id が t＋5 桁以上の 1 からの連番でない")
            blk = None
            if blocks and _is_int(obj["block_id"]) and obj["block_id"] == blocks[-1][0]:
                blk = blocks[-1]
                blk[3] += 1
            else:
                bad(ln, "block_ref", "block_id が直前のブロック行の block_id と一致しない")
            if obj["scenario"] not in SCENARIOS:
                bad(ln, "scenario", "scenario が S1〜S15 でない")
            if obj["speed"] not in SPEEDS:
                bad(ln, "speed", "speed が列挙外")
            elif blk is not None and obj["speed"] != blk[1]:
                bad(ln, "speed_mismatch", "試行の speed がブロックの speed と違う")
            for k in ("gap_before_ms", "think_ms"):
                if not _is_int(obj[k]) or obj[k] < 0:
                    bad(ln, "type", "%s が 0 以上の整数でない" % k)
            if not isinstance(obj["phrase_id"], str) or not PHRASE_ID_RE.fullmatch(obj["phrase_id"]):
                bad(ln, "phrase_id", "phrase_id の書式")
            if not _is_int(obj["reading_len"]) or obj["reading_len"] < 1:
                bad(ln, "type", "reading_len が 1 以上の整数でない")
            _check_steps(ln, obj["steps"], bad)
            _check_intent(ln, obj["intent"], bad)
        else:
            bad(ln, "kind", "kind が header / block / trial のどれでもない（または 2 行目以降がヘッダ）")
    if n_trials == 0:
        bad(1, "no_trial", "試行が 1 つも無い")
    for blk in blocks:
        if blk[3] == 0:
            bad(blk[2], "empty_block", "試行の無いブロックがある")
    return found


def _check_steps(ln, steps, bad):
    if not isinstance(steps, list) or not steps:
        bad(ln, "steps", "steps が空でない配列でない")
        return
    held = set()
    prev = -1
    order_bad = pair_bad = key_bad = shape_bad = False
    for st in steps:
        if not isinstance(st, dict) or set(st) != {"key", "at_ms", "down"}:
            shape_bad = True
            continue
        if not isinstance(st["key"], str) or st["key"] not in KEYNAMES:
            key_bad = True
            continue
        if not _is_int(st["at_ms"]) or st["at_ms"] < 0 or not isinstance(st["down"], bool):
            shape_bad = True
            continue
        if st["at_ms"] < prev:
            order_bad = True
        prev = max(prev, st["at_ms"])
        if st["down"]:
            if st["key"] in held:
                pair_bad = True
            held.add(st["key"])
        else:
            if st["key"] not in held:
                pair_bad = True
            held.discard(st["key"])
    if held:
        pair_bad = True
    if shape_bad:
        bad(ln, "step_shape", "steps の要素が {key, at_ms（0 以上の整数）, down（真偽値）} でない")
    if key_bad:
        bad(ln, "keyname", "steps に keyname の列挙に無いキーがある")
    if order_bad:
        bad(ln, "at_ms_order", "at_ms が単調非減少でない")
    if pair_bad:
        bad(ln, "pair", "down と up が対になっていない")


def _check_intent(ln, intent, bad):
    if not isinstance(intent, dict) or set(intent) != set(INTENT_KEYS):
        bad(ln, "intent_keys", "intent が 8 キーを過不足なく持たない")
        return
    if intent["commit"] not in COMMITS:
        bad(ln, "intent_type", "intent.commit が列挙外")
    ci = intent["cand_index"]
    if ci is not None and (not _is_int(ci) or ci < 0):
        bad(ln, "intent_type", "intent.cand_index が 0 以上の整数か null でない")
    if not _is_int(intent["nav_count"]) or intent["nav_count"] < 0:
        bad(ln, "intent_type", "intent.nav_count が 0 以上の整数でない")
    for k in INTENT_BOOLS:
        if not isinstance(intent[k], bool):
            bad(ln, "intent_type", "intent.%s が真偽値でない" % k)


# ---------------------------------------------------------------- selftest

def _selftest_env(tmp):
    readings = ["あおぞら", "にほん", "がっこう", "みなさん", "たのしい", "きょうは", "ふぁんたじー", "てんき", "ゆめ",
                "ちょっと", "はなし", "ほんとう", "おおきな", "ながれる"]
    lines = ['{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}']
    for i, r in enumerate(readings, start=1):
        lines.append(dumps({"kind": "phrase", "phrase_id": "w1-%d-1" % i, "work_id": "w1", "text": "x",
                            "reading": r, "reading_len": len(r)}))
    corpus_path = os.path.join(tmp, "corpus.jsonl")
    with open(corpus_path, "wb") as f:
        f.write(("\n".join(lines) + "\n").encode("utf-8"))
    cfg = {"n_per_cell_scenario_speed": 6, "block_size": 12,
           "speeds": {"slow": {"iki_median_ms": 300, "iki_sigma": 0.3}, "mid": {"iki_median_ms": 200, "iki_sigma": 0.3},
                      "fast": {"iki_median_ms": 120, "iki_sigma": 0.3}},
           "key_hold_ms": 60, "think_ms": {"min": 200, "max": 2000}, "cand_index_max": 4, "nav_count_max": 3,
           "inter_trial_ms": 1000, "marker": ["f13", "f14", "f13"], "marker_gap_ms": 150, "reset_ime_every_block": True}
    cfg_path = os.path.join(tmp, "cfg.json")
    with open(cfg_path, "wb") as f:
        f.write(json.dumps(cfg, indent=1).encode("utf-8"))
    return corpus_path, cfg, cfg_path


def _sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _scenario_checks(rows, phrases, recipes, cfg, fails):
    """シナリオごとの手順が recipes の意図どおりに出ているか（陽性の内容検査）。"""
    inv = dict((c, k) for k, c in recipes["kana_layout"].items())
    seen = set()
    for r in rows:
        if r["kind"] != "trial":
            continue
        sc, ph, it = r["scenario"], phrases[r["trial_id"]], r["intent"]
        downs = [s["key"] for s in r["steps"] if s["down"]]
        at = [s["at_ms"] for s in r["steps"] if s["down"]]
        rd = ph["reading"]
        full = romaji.to_keys(rd)
        seen.add(sc)
        ok = True
        if sc == "S1":
            ok = downs == full + ["space", "enter"] and cfg["think_ms"]["min"] <= r["think_ms"] <= cfg["think_ms"]["max"]
        elif sc == "S2":
            k = it["cand_index"] + 1
            ok = 1 <= it["cand_index"] <= cfg["cand_index_max"] and downs == full + ["space"] * k + ["enter"]
        elif sc == "S3":
            ok = downs == full + ["enter"] and r["think_ms"] == 0
        elif sc == "S4":
            ok = downs == full + ["space", "esc", "esc"] and it["abandon"] is True
        elif sc == "S5":
            ok = downs == full + ["esc"]
        elif sc == "S6":
            ok = downs == full + ["backspace"] * len(rd)
        elif sc == "S7":
            ok = downs == full + ["space"] + ["right"] * it["nav_count"] + ["enter"] \
                and 1 <= it["nav_count"] <= cfg["nav_count_max"]
        elif sc == "S8":
            ok = downs == full + ["space", "space", str(it["cand_index"] + 1)] and it["commit"] == "digit"
        elif sc == "S10":
            ok = downs == romaji.to_keys(rd[:max(1, len(rd) // 2)]) + ["tab", "enter"] and it["predictive"] is True
        elif sc == "S11":
            ok = downs == full + ["enter"]
        elif sc == "S12":
            ok = downs[-2:] == ["space", "enter"] and all(k in recipes["kana_layout"] for k in downs[:-2]) \
                and "".join(recipes["kana_layout"][k] for k in downs[:-2]) == rd
        elif sc == "S13":
            ok = downs[-2:] == ["space", "enter"] and at[-1] - at[-2] == 21000
        elif sc == "S14":
            ok = downs == full + ["space", "ime_off", "ime_on"] and it["ime_toggle_mid"] is True
        elif sc == "S15":
            i = downs.index("focus_away")
            ok = downs[i:] == ["focus_away", "focus_back", "enter"] and at[i + 1] - at[i] == 1000
        if not ok:
            fails.append("シナリオ %s の手順が recipes の意図と違う（%s）" % (sc, r["trial_id"]))
            return
    return seen


def _median(xs):
    xs = sorted(xs)
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2.0


def selftest():
    fails = []
    n = [0]

    def check(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append(name + (": " + detail if detail else ""))

    recipes_path = os.path.join(_HERE, "recipes.json")
    tmp = tempfile.mkdtemp(prefix="generate_plan_selftest_")
    try:
        recipes = load_recipes(recipes_path)
        corpus_path, cfg, cfg_path = _selftest_env(tmp)
        corpus = load_corpus(corpus_path)
        sha = _sha_file(cfg_path)
        rsha = _sha_file(recipes_path)
        csha = _sha_file(corpus_path)
        ncfg = normalize_config(cfg)

        def gen(os_name="macos", seed=7, config=None):
            rows, ph = plan_rows(corpus, recipes, config if config is not None else cfg, os_name, seed, sha,
                                  rsha, csha)
            return rows, ph

        rows1, ph1 = gen()
        bytes1 = render_plan(rows1)
        check("recipes.json が検査を通る", True)

        # --- 決定性と seed の効き（acceptance がケース名を検査する）
        check("同じ seed でバイト一致", render_plan(gen()[0]) == bytes1)
        rows2, _ = gen(seed=8)
        order = lambda rs: [(r["scenario"], r["phrase_id"]) for r in rs if r["kind"] == "trial"]
        check("seed を変えると順が変わる（陰性対照）", order(rows1) != order(rows2) and render_plan(rows2) != bytes1)
        check("BOM なし・LF だけ・最後は改行", not bytes1.startswith(b"\xef\xbb\xbf") and b"\r" not in bytes1
              and bytes1.endswith(b"\n"))

        # --- 件数とブロック
        trials = [r for r in rows1 if r["kind"] == "trial"]
        blocks = [r for r in rows1 if r["kind"] == "block"]
        scen_mac = [s for s in SCENARIOS if s in recipes["os"]["macos"] and recipes["os"]["macos"][s].get("default_enabled", True)]
        n_cell = ncfg["n_per_cell_scenario_speed"]
        check("件数 = シナリオ数 × 3 × n", len(trials) == len(scen_mac) * 3 * n_cell, "%d" % len(trials))
        per_speed = len(scen_mac) * n_cell
        check("ブロック数 = 速さごとの ceil(件数/block_size) の合計",
              len(blocks) == 3 * -(-per_speed // ncfg["block_size"]), "%d" % len(blocks))
        check("割り切れるとき ceil(件数 / block_size) と一致",
              per_speed % ncfg["block_size"] != 0 or len(blocks) == -(-len(trials) // ncfg["block_size"]))
        rows_w, ph_w = gen("windows")
        blocks_w = [r for r in rows_w if r["kind"] == "block"]
        trials_w = [r for r in rows_w if r["kind"] == "trial"]
        check("windows のブロック数（割り切れない場合も式どおり）",
              len(blocks_w) == 3 * -(-((len(scen_mac) - 1) * n_cell) // ncfg["block_size"]), "%d" % len(blocks_w))
        check("ブロックは速さで揃う（試行の speed = ブロック行の speed）",
              all(t["speed"] == blocks[t["block_id"]]["speed"] for t in trials))
        check("ブロック行に marker・marker_gap_ms・reset_ime を設定から書く",
              all(b["marker"] == cfg["marker"] and b["marker_gap_ms"] == 150 and b["reset_ime"] is True for b in blocks))
        check("試行行に gap_before_ms を設定から書く", all(t["gap_before_ms"] == 1000 for t in trials))
        check("trial_id と block_id が連番", [t["trial_id"] for t in trials] == ["t%05d" % i for i in range(1, len(trials) + 1)]
              and [b["block_id"] for b in blocks] == list(range(len(blocks))))
        check("ブロックの並びが seed で並べ替わっている（速さが 3 つ固まっていない）",
              [b["speed"] for b in blocks] != sorted(b["speed"] for b in blocks))

        # --- S9 / S11
        check("S9 が既定で出ない", "S9" not in set(t["scenario"] for t in trials))
        check("S11 が macos では出る", "S11" in set(t["scenario"] for t in trials))
        check("S11 が windows で出ない", "S11" not in set(t["scenario"] for t in trials_w))
        for os_name in OS_NAMES:
            try:
                gen(os_name, config=dict(cfg, scenarios=["S9"]))
                check("S9 を明示しても手順が未定義なら止まる (%s)" % os_name, False, "止まらなかった")
            except ValueError:
                check("S9 を明示しても手順が未定義なら止まる (%s)" % os_name, True)
        rows_s11, _ = gen("windows", config=dict(cfg, scenarios=["S1", "S11"]))
        check("windows で S11 を明示しても飛ばして残りを作る",
              set(t["scenario"] for t in rows_s11 if t["kind"] == "trial") == {"S1"})

        # --- 速さの中央値が順に並ぶ
        rows_s3, _ = gen(config=dict(cfg, scenarios=["S3"], n_per_cell_scenario_speed=40, block_size=40))
        med = {}
        for sp in SPEEDS:
            gaps = []
            for t in rows_s3:
                if t["kind"] == "trial" and t["speed"] == sp:
                    ds = [s["at_ms"] for s in t["steps"] if s["down"]]
                    gaps.extend(b - a for a, b in zip(ds, ds[1:]))
            med[sp] = _median(gaps)
        check("キー間隔の中央値が slow > mid > fast", med["slow"] > med["mid"] > med["fast"], str(med))
        check("キー間隔の中央値が設定の中央値に近い（±10%）",
              all(abs(med[sp] - cfg["speeds"][sp]["iki_median_ms"]) <= 0.1 * cfg["speeds"][sp]["iki_median_ms"]
                  for sp in SPEEDS), str(med))

        # --- シナリオごとの手順（recipes の意図）
        seen = _scenario_checks(rows1, ph1, recipes, ncfg, fails)
        n[0] += 1
        check("macos の既定で 14 シナリオすべてが出る", seen == set(scen_mac), str(sorted(seen or [])))
        _scenario_checks(rows_w, gen("windows")[1], recipes, ncfg, fails)
        check("S12 で合成かな列（kana-）が使われる（打てる句が足りない）",
              any(t["phrase_id"].startswith("kana-") for t in trials if t["scenario"] == "S12"))
        check("S12 以外は kana- を使わない", all(not t["phrase_id"].startswith("kana-") for t in trials if t["scenario"] != "S12"))
        check("S10 は読みの長さが 2 以上の句だけ", all(t["reading_len"] >= 2 for t in trials if t["scenario"] == "S10"))
        check("steps の各キーは down と up が対で、キーは列挙内",
              all(len(t["steps"]) % 2 == 0 and all(s["key"] in KEYNAMES for s in t["steps"]) for t in trials))
        check("at_ms は試行の先頭から（最初は 0）", all(t["steps"][0]["at_ms"] == 0 for t in trials))

        # --- typed_reading（判断 29）: 全シナリオ・両 OS で「打った読み」が期待どおり
        def _typed_mismatches(rows, phrases):
            bad = []
            for t in rows:
                if t["kind"] != "trial":
                    continue
                rd = phrases[t["trial_id"]]["reading"]
                want = rd[:max(1, len(rd) // 2)] if t["scenario"] == "S10" else rd
                got = typed_reading(t, recipes)
                if got != want:
                    bad.append((t["trial_id"], t["scenario"], want, got))
            return bad

        bad_mac = _typed_mismatches(rows1, ph1)
        check("typed_reading が全シナリオで期待どおり（macos・通常は全体・S10 は前半・S12 は合成かな列）",
              not bad_mac, str(bad_mac[:3]))
        bad_win = _typed_mismatches(rows_w, ph_w)
        check("typed_reading が全シナリオで期待どおり（windows）", not bad_win, str(bad_win[:3]))

        # --- 公開関数は stderr に出さない（項目7）。警告は戻り値で返す
        _buf = io.StringIO()
        with contextlib.redirect_stderr(_buf):
            _warns = []
            plan_rows(corpus, recipes, dict(cfg, scenarios=["S1", "S11"]), "windows", 1, sha, rsha, csha,
                      warnings=_warns)
        check("plan_rows / enabled_scenarios は stderr に出さず、警告は戻り値で返す（windows に無い S11）",
              _buf.getvalue() == "" and any("S11" in w for w in _warns), repr(_buf.getvalue()))

        # --- check_recipes: intent の値の型・reading_len の指定の型（項目5）
        def _bad_recipes(mutate_fn):
            data = json.loads(json.dumps(recipes))
            mutate_fn(data)
            return data

        for name, fn in [
            ("intent.commit が列挙外", lambda d: d["os"]["macos"]["S1"]["intent"].__setitem__("commit", "click")),
            ("intent.cand_index が負", lambda d: d["os"]["macos"]["S1"]["intent"].__setitem__("cand_index", -1)),
            ("intent.nav_count が負", lambda d: d["os"]["macos"]["S1"]["intent"].__setitem__("nav_count", -1)),
            ("intent の真偽値の欄が整数", lambda d: d["os"]["macos"]["S1"]["intent"].__setitem__("abandon", 0)),
            ("reading_len.min が 0", lambda d: d["os"]["macos"]["S10"].__setitem__("reading_len", {"min": 0})),
            ("reading_len に未知のキー", lambda d: d["os"]["macos"]["S10"].__setitem__("reading_len", {"min": 2, "zz": 1})),
        ]:
            try:
                check_recipes(_bad_recipes(fn))
                check("check_recipes が拒否する（型）: %s" % name, False, "拒否されなかった")
            except ValueError:
                check("check_recipes が拒否する（型）: %s" % name, True)

        # --- load_corpus: phrase_id が kana- で始まる行を拒否する（項目6）
        kana_corpus = os.path.join(tmp, "kana_corpus.jsonl")
        with open(kana_corpus, "wb") as f:
            f.write(('{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}\n'
                     + dumps({"kind": "phrase", "phrase_id": "kana-1", "work_id": "kana", "text": "x",
                              "reading": "あい", "reading_len": 2}) + "\n").encode("utf-8"))
        try:
            load_corpus(kana_corpus)
            check("load_corpus が kana- 始まりの phrase_id を拒否する", False, "拒否されなかった")
        except ValueError:
            check("load_corpus が kana- 始まりの phrase_id を拒否する", True)

        # --- fullmatch の直接確認（項目4・末尾に改行が付いた値は re.match の $ だと通ってしまう）
        check("正規表現が末尾の改行を拒否する（fullmatch・陰性対照）",
              PHRASE_ID_RE.fullmatch("w1-1-1\n") is None and VERSION_RE.fullmatch("1.0.0\n") is None
              and SHA_RE.fullmatch("0" * 64 + "\n") is None and TRIAL_ID_RE.fullmatch("t00001\n") is None)
        check("正規表現は末尾の改行が無ければ通る（陽性対照）",
              PHRASE_ID_RE.fullmatch("w1-1-1") is not None and VERSION_RE.fullmatch("1.0.0") is not None)

        # --- fullmatch の実地確認（項目4）: load_corpus はバックスラッシュを禁止しないので、
        #     ヘッダの tokenizer に「末尾に改行の付いた値」（\n エスケープで JSON としては合法）を仕込むと、
        #     .match のままなら $ が改行の直前で一致して通ってしまう。fullmatch なら拒否する。
        bad_tok_corpus = os.path.join(tmp, "bad_tokenizer_corpus.jsonl")
        with open(bad_tok_corpus, "wb") as f:
            bad_header = dumps({"kind": "header", "format": "corpus/1", "source": "aozora",
                                 "tokenizer": "table" + chr(10), "dict": "none"})
            f.write((bad_header + "\n" + dumps({"kind": "phrase", "phrase_id": "w1-1-1", "work_id": "w1",
                                                "text": "x", "reading": "あい", "reading_len": 2}) + "\n")
                    .encode("utf-8"))
        try:
            load_corpus(bad_tok_corpus)
            check("load_corpus が末尾に改行の付いた tokenizer を拒否する（fullmatch・項目4）", False, "拒否されなかった")
        except ValueError:
            check("load_corpus が末尾に改行の付いた tokenizer を拒否する（fullmatch・項目4）", True)

        # --- 検査器: 陽性対照
        check("生成した計画（macos）を --validate が通す", validate_plan(bytes1) == [], str(validate_plan(bytes1)[:2]))
        check("生成した計画（windows）を --validate が通す", validate_plan(render_plan(rows_w)) == [])
        check("CRLF の計画も通す", validate_plan(bytes1.replace(b"\n", b"\r\n")) == [])

        # --- 検査器: 陰性対照（1 か所ずつ壊す・理由まで確かめる）
        def mutate(kind_row, fn, block_kind=None):
            rs = json.loads(json.dumps(rows1))
            for r in rs:
                if r["kind"] == kind_row and fn(r, rs):
                    return render_plan(rs)
            raise AssertionError("変異を入れられない")

        def first_trial(fn):
            return mutate("trial", lambda r, rs: (fn(r), True)[1])

        muts = [
            ("未知の keyname", first_trial(lambda r: r["steps"][0].__setitem__("key", "hyper")), "keyname"),
            ("at_ms の逆行", first_trial(lambda r: r["steps"][0].__setitem__("at_ms", r["steps"][-1]["at_ms"] + 1000)),
             "at_ms_order"),
            ("ブロックと速さの不一致", first_trial(lambda r: r.__setitem__(
                "speed", {"slow": "fast", "mid": "slow", "fast": "mid"}[r["speed"]])), "speed_mismatch"),
            ("down が 2 回続く", first_trial(lambda r: r["steps"].__setitem__(1, dict(r["steps"][1], down=True))), "pair"),
            ("up が無い", first_trial(lambda r: r["steps"].pop()), "pair"),
            ("trial_id が飛ぶ", first_trial(lambda r: r.__setitem__("trial_id", "t99999")), "trial_id"),
            ("block_id が存在しない", first_trial(lambda r: r.__setitem__("block_id", 9999)), "block_ref"),
            ("scenario が S99", first_trial(lambda r: r.__setitem__("scenario", "S99")), "scenario"),
            ("intent のキーが足りない", first_trial(lambda r: r["intent"].pop("commit")), "intent_keys"),
            ("intent に未知のキー", first_trial(lambda r: r["intent"].__setitem__("zz", 1)), "intent_keys"),
            ("intent.commit が列挙外", first_trial(lambda r: r["intent"].__setitem__("commit", "click")), "intent_type"),
            ("intent の真偽値が整数", first_trial(lambda r: r["intent"].__setitem__("abandon", 0)), "intent_type"),
            ("試行に未知のキー", first_trial(lambda r: r.__setitem__("zz", 1)), "extra_key"),
            ("試行のキーが足りない", first_trial(lambda r: r.pop("think_ms")), "missing_key"),
            ("phrase_id の書式（大文字）", first_trial(lambda r: r.__setitem__("phrase_id", "Xray1")), "phrase_id"),
            ("reading_len が 0", first_trial(lambda r: r.__setitem__("reading_len", 0)), "type"),
            ("at_ms が真偽値", first_trial(lambda r: r["steps"][0].__setitem__("at_ms", True)), "step_shape"),
            ("ブロックの marker に未知のキー", mutate("block", lambda r, rs: (r["marker"].append("hyper"), True)[1]), "keyname"),
            ("ブロックの speed が列挙外", mutate("block", lambda r, rs: (r.__setitem__("speed", "warp"), True)[1]), "speed"),
            ("ヘッダの format", mutate("header", lambda r, rs: (r.__setitem__("format", "plan/2"), True)[1]), "header"),
            ("ヘッダの seed が負", mutate("header", lambda r, rs: (r.__setitem__("seed", -1), True)[1]), "header"),
            ("ヘッダの config_sha256 が大文字", mutate("header", lambda r, rs: (r.__setitem__("config_sha256", "A" * 64), True)[1]),
             "header"),
            ("ヘッダの recipes_sha256 が短い", mutate("header", lambda r, rs: (r.__setitem__("recipes_sha256", "ab"), True)[1]),
             "header"),
            ("ヘッダの corpus_sha256 が大文字", mutate("header", lambda r, rs: (r.__setitem__("corpus_sha256", "B" * 64), True)[1]),
             "header"),
            ("ヘッダに recipes_sha256 が無い", mutate("header", lambda r, rs: (r.pop("recipes_sha256"), True)[1]),
             "missing_key"),
            ("block_id が直前でなく前のブロックを指す（判断 29）",
             mutate("trial", lambda r, rs: (r.__setitem__("block_id", 0), True)[1] if r["block_id"] > 0 else False),
             "block_ref"),
        ]
        text = bytes1.decode("utf-8")
        muts += [
            ("区切りに空白", text.replace('"kind":"block"', '"kind": "block"', 1).encode("utf-8"), "format"),
            ("エスケープ（バックスラッシュを含む行）",
             text.replace('"kind":"block"', '"kind":"bl' + chr(92) + 'u006fck"', 1).encode("utf-8"), "escape"),
            ("BOM", b"\xef\xbb\xbf" + bytes1, "bom"),
            ("空行", text.replace("\n", "\n\n", 1).encode("utf-8"), "blank"),
            ("小数", text.replace('"at_ms":0,', '"at_ms":0.0,', 1).encode("utf-8"), "float"),
            ("重複キー", text.replace('"kind":"trial"', '"kind":"trial","kind":"trial"', 1).encode("utf-8"), "dup_key"),
            ("試行が無い", "\n".join(text.split("\n")[:2]).encode("utf-8") + b"\n", "no_trial"),
            ("空のファイル", b"", "empty"),
        ]
        for name, body, want in muts:
            found = validate_plan(body)
            codes = set(c for _, c, _ in found)
            check("検査器が拒否する: %s" % name, want in codes, "期待 %s・実際 %s" % (want, sorted(codes)))
        leak_found = []
        for leak_fn in (lambda r: r["steps"][0].__setitem__("key", "leakykey9"),
                        lambda r: r.__setitem__("phrase_id", "leakyvalue1"),
                        lambda r: r.__setitem__("leakyextra", 1)):
            one = validate_plan(first_trial(leak_fn))
            check("陰性対照の材料が拒否される（漏れの検査の前提）", len(one) >= 1)
            leak_found.extend(one)
        check("検査器の説明に値もキー名も出ない", all("leaky" not in m for _, _, m in leak_found))

        # --- 公開関数と CLI の一致
        out1 = os.path.join(tmp, "plan1.jsonl")
        out2 = os.path.join(tmp, "plan2.jsonl")
        me = os.path.abspath(__file__)
        env = dict(os.environ, PYTHONUTF8="1")

        def run(*args):
            p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env=env)
            return p.returncode, p.stdout.decode("utf-8", "replace")

        base_args = ["--corpus", corpus_path, "--recipes", recipes_path, "--config", cfg_path, "--os", "macos"]
        rc, msg = run(*(base_args + ["--seed", "7", "--out", out1]))
        check("CLI が計画を作る", rc == 0, msg[-200:])
        rc, msg = run(*(base_args + ["--seed", "7", "--out", out2]))
        with open(out1, "rb") as f1, open(out2, "rb") as f2:
            cli1, cli2 = f1.read(), f2.read()
        check("CLI を 2 回回すとバイト一致（同じ seed でバイト一致）", cli1 == cli2 and len(cli1) > 100)
        check("CLI の出力 = 関数の出力（config_sha256 は設定ファイルのバイト列の SHA-256）", cli1 == bytes1)
        check("CLI の出力を --validate が通す", run("--validate", out1)[0] == 0)
        by_id = dict((p["phrase_id"], p) for p in corpus)
        mism = 0
        checked = 0
        for line in cli1.decode("utf-8").split("\n"):
            if not line.startswith('{"kind":"trial"'):
                continue
            row = json.loads(line)
            if row["phrase_id"] not in by_id:
                continue
            got = build_trial(by_id[row["phrase_id"]], row["scenario"], row["speed"], "macos", recipes, cfg,
                              trial_rng(7, row["trial_id"]), row["trial_id"], row["block_id"])
            checked += 1
            if dumps(got) != line:
                mism += 1
        check("build_trial を直接呼んだ結果と CLI の該当行が一致する", checked > 100 and mism == 0,
              "確かめた %d 行・不一致 %d" % (checked, mism))
        check("load_recipes / build_trial が公開されている", callable(load_recipes) and callable(build_trial))

        # --- CLI の入口
        bad_cfg = os.path.join(tmp, "bad_cfg.json")
        with open(bad_cfg, "wb") as f:
            f.write(json.dumps({"key_hold_ms": 60}).encode("utf-8"))
        rc, msg = run("--corpus", corpus_path, "--recipes", recipes_path, "--config", bad_cfg, "--os", "macos",
                      "--seed", "1", "--out", os.path.join(tmp, "x.jsonl"))
        check("設定にキーが足りなければ exit 2", rc == 2, "exit %d" % rc)
        rc, msg = run("--validate", os.path.join(tmp, "no-such-file.jsonl"))
        check("存在しない計画の --validate は exit 2", rc == 2, "exit %d" % rc)
        mut_path = os.path.join(tmp, "mut.jsonl")
        with open(mut_path, "wb") as f:
            f.write(muts[0][1])
        rc, msg = run("--validate", mut_path)
        check("違反のある計画の --validate は exit 1（行番号つき）", rc == 1 and ":" in msg, "exit %d" % rc)
        rc, msg = run("--seed", "1")
        check("モードが無ければ exit 2", rc == 2, "exit %d" % rc)
        rc, msg = run(*(base_args + ["--seed", "-3", "--out", os.path.join(tmp, "y.jsonl")]))
        check("seed が負なら exit 2", rc == 2, "exit %d" % rc)

        # --- 見積もり
        secs, lines = estimate(cfg, recipes, "macos")
        check("--estimate（コーパス無し）が正の数", secs > 0 and lines[-1].endswith("："))
        secs2, _ = estimate(cfg, recipes, "macos", corpus)
        check("--estimate（コーパスあり）が正の数", secs2 > 0)
        rc, msg = run("--estimate", "--config", cfg_path, "--recipes", recipes_path, "--os", "macos")
        last = msg.strip().split("\n")[-1]
        check("--estimate の最後の行が正の数 1 つだけ", rc == 0 and re.fullmatch(r"[0-9]+(\.[0-9]+)?", last) is not None
              and float(last) > 0, "exit %d・最後の行 %s" % (rc, last))
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)

    if fails:
        for m in fails:
            print("FAIL " + m)
        print("selftest 失敗 %d 件 / %d 件" % (len(fails), n[0]))
        return 1
    print("selftest OK（%d 件）" % n[0])
    return 0


# ---------------------------------------------------------------- CLI

def _read_json(path, what):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        raise ValueError("%s を開けない（%s）" % (what, type(e).__name__))
    try:
        return raw, json.loads(raw.decode("utf-8"))
    except ValueError:
        raise ValueError("%s が JSON として読めない" % what)


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="plan/1 の生成器・検査器・見積もり")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--validate", metavar="PLAN")
    ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--corpus")
    ap.add_argument("--recipes")
    ap.add_argument("--config")
    ap.add_argument("--os", dest="os_name", choices=OS_NAMES)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.validate is not None:
        try:
            with open(args.validate, "rb") as f:
                data = f.read()
        except OSError as e:
            print("%s: 開けない（%s）" % (args.validate, type(e).__name__), file=sys.stderr)
            return 2
        found = validate_plan(data)
        for ln, code, msg in found[:50]:
            print("%s:%d: [%s] %s" % (args.validate, ln, code, msg), file=sys.stderr)
        if len(found) > 50:
            print("%s: …ほか %d 件" % (args.validate, len(found) - 50), file=sys.stderr)
        return 1 if found else 0

    generating = args.out is not None or args.seed is not None or args.corpus is not None
    if not args.estimate and not generating:
        print("generate_plan.py: --selftest / --validate PLAN / --estimate / 生成（--corpus --recipes --config --os --seed --out）"
              "のどれかを指定する", file=sys.stderr)
        return 2
    try:
        if not args.recipes or not args.config or not args.os_name:
            raise ValueError("--recipes・--config・--os が要る")
        recipes = load_recipes(args.recipes)
        recipes_sha256 = _sha_file(args.recipes)
        raw_cfg, config = _read_json(args.config, "設定")
        normalize_config(config)
        unknown = unknown_config_keys(config)
        if unknown:
            print("generate_plan.py: 設定の未知のキーは無視する: %s" % ", ".join(str(k) for k in unknown),
                  file=sys.stderr)
        corpus = load_corpus(args.corpus) if args.corpus else None
        corpus_sha256 = _sha_file(args.corpus) if args.corpus else None
        if args.estimate:
            secs, lines = estimate(config, recipes, args.os_name, corpus)
            for line in lines:
                print(line)
            print("%.1f" % secs)
            sys.stdout.flush()
            return 0
        if corpus is None or args.seed is None or not args.out:
            raise ValueError("生成には --corpus・--seed・--out が要る")
        if not 0 <= args.seed <= SEED_MAX:
            raise ValueError("--seed は 0〜2^63-1 の整数")
        gen_warnings = []
        rows, _ = plan_rows(corpus, recipes, config, args.os_name, args.seed, hashlib.sha256(raw_cfg).hexdigest(),
                             recipes_sha256, corpus_sha256, warnings=gen_warnings)
        for w in gen_warnings:
            print("generate_plan.py: %s" % w, file=sys.stderr)
    except (ValueError, OSError) as e:
        print("generate_plan.py: %s" % e, file=sys.stderr)
        return 2
    body = render_plan(rows)
    problems = validate_plan(body)
    if problems:  # 自分の出力が自分の検査を通らないのは生成器の不具合
        for ln, code, msg in problems[:10]:
            print("generate_plan.py: 生成した計画が検査に通らない %d 行目 [%s] %s" % (ln, code, msg), file=sys.stderr)
        return 2
    with open(args.out, "wb") as f:
        f.write(body)
    n_trial = sum(1 for r in rows if r["kind"] == "trial")
    n_block = sum(1 for r in rows if r["kind"] == "block")
    print("計画を書いた: 試行 %d 件・ブロック %d 個（os=%s・seed=%d）" % (n_trial, n_block, args.os_name, args.seed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
