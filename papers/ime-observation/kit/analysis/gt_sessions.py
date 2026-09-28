#!/usr/bin/env python3
# kit: selftest
"""正解の組み立て: 参照入力欄の生ログ（gt/1）と実行器の記録（oracle/1）から、正解側の変換セッションを作る。
Python 標準ライブラリだけ。

  gt_sessions.py --gt GT --oracle ORACLE --rules RULES --out SESSIONS [--plan PLAN]
  gt_sessions.py --selftest       速い既定（1 秒未満）

単位は正解側の 1 変換セッション（開始 = 最初の marked text / 変換開始の通知、終了 = 確定または取消）。
開始・確定・取消・候補窓の**規則は設定（RULES・JSON）から読む**。IME の呼び出し順序は OS 側の文書に無く、
実機の呼び出し列で決める前提なので、規則を差し替えるだけで組み立てが変わる。

規則ファイル（src ごと。`_` で始まるキーは注釈で、読まれない）:
  {"mac_nstic": {"start": 条件, "commit": [条件…], "cancel": [条件…], "candidate": 条件|null,
                 "candidate_end": 条件|null, "clock_jump_ms": 整数},
   "win_imm": {…}, "win_tsf": {…}}
  条件 = 事象の述語: {"ev": 名前, <欄>: 値, <欄>_gt|ge|lt|le|eq|ne: 整数, …}
    ・欄は gt/1 の表にある付随フィールド（その ev が持つもの）。欄だけを書くと等しいことを表す。
    ・commit / cancel の条件だけが次を持てる:
        "after_result": true|false   セッションの中でここまでに結果文字列（result_len > 0）が出た / 出ていない
        "not_followed_by": 条件, "within_ms": 整数   この事象の後 within_ms（単調時計）以内に、その条件に合う事象が来ない
      not_followed_by を書くときは within_ms が要る（逆も同じ）。ログの終わりまでに来なければ「来ない」と数える。
    ・abandon が偽で commit が none の試行は、oracle_agreement では組み立てたセッションの実際の outcome を
      問わず一致に数える（意図が「確定も取消も期待しない」ため。_classify 参照）。
  事象は 1 本ずつ順に見る。セッションが無いとき start に合えば開く。開いている間は commit → cancel の順に
  調べ、最初に合った方で閉じる（閉じる事象の時刻が終了）。start に合う事象が開いている間に来ても何もしない
  （★ 件数は診断用の n_start_while_open に出る）。
  candidate に合う事象がセッションの区間（両端を含む）にあれば候補窓が出たセッションになる。null なら候補窓は
  取れないので candidate_shown は null で、windows_def も作れない（null）。
  ★ candidate_end（判断 27）: 候補窓が閉じたとみなす条件。candidate と同じ形（単一の条件・null 可）。
    candidate が開いている間に candidate_end に合う事象が来ればそこで閉じる（次に candidate が来ればまた開く。
    1 セッションに複数回あってよい）。閉じないまま閉じる規則（commit/cancel）に達したときはセッションの終わり
    （open_at_end はログの最後）で閉じたものとして数える。candidate が null なら candidate_end も null。
  clock_jump_ms: 隣り合う 2 事象の壁時計の差と単調時計の差のずれがこれを超えたら「時計の跳び」（除外）。

出力（SESSIONS・JSON）:
  {"src", "rules_sha256", "definitions": {"all", "macos_def", "windows_def"}, "oracle_agreement", "excluded"}
  ・セッション = {"trial_id", "start_wall_ms", "end_wall_ms", "start_mono_ns", "end_mono_ns", "outcome",
    "candidate_shown", "nav_true", "nav_true_cand", "excluded_by", "n_start_while_open"}。outcome = commit /
    cancel / open_at_end（閉じないままログが終わった。このとき end_* は null）。trial_id は oracle の
    trial_begin〜trial_end との重なり（壁時計・最大の重なり・同点は先の試行）で決め、重ならなければ null。
    nav_true = セッションの区間（両端を含む・壁時計）の中で実行器が送った矢印キー（left/right/up/down の押下）
    の数。区間は IME 自身が出した事象から取るので、数と区間が循環しない。open_at_end の区間は最後の事象までと
    して数える。★ nav_true と nav_true_cand が数える矢印は、trial_id が付いたセッションでは、その trial_id の
    送出（oracle の sent の trial_id）に限る（確定が遅れて次の試行の矢印を拾わないため・判断 27）。trial_id が
    null のセッションだけは区間内の全 sent を数える。
    ★ nav_true_cand（判断 27）: candidate が null でない src で、セッションの中の「候補窓が開いていた区間」
    （candidate_end で複数回開閉すれば全部）に入る矢印の数（数え方は nav_true と同じ）。candidate が null の
    src（mac_nstic）では null。Windows の `nav` の正解は design.md の定義どおり候補窓が開いていた区間の矢印数
    なので、後続 issue はこちらを使う。
    ★ excluded_by（判断 28）: このセッションが除外の対象になった理由の配列（"clock_jump" / "log_truncated"。
    空なら対象外）。判定は下の excluded の trial_ids にこのセッションの trial_id が入っているか、または
    セッションの区間が時計の跳びを直接またいでいるか。
    ★ n_start_while_open（判断 28・診断用）: このセッションが開いている間に来た start 事象の数（整数）。
  ・all = 全 composition。macos_def = かな入力の一区切りすべて（参照側では all と同じ。定義の違いは観測側の
    数え方にある）。windows_def = 候補窓が出たセッションだけ（candidate が null なら null）。
  ・oracle_agreement: --plan（plan/1）があるとき、試行ごとに計画の意図（expect_session / abandon / commit）と
    組み立てたセッション（all）を比べる。意図は oracle に無いので plan が要る。plan の SHA-256 が oracle の
    ヘッダと違えば拒否する。不一致は捨てず型ごとに数える（no_session / unexpected_session / multiple_sessions /
    expected_cancel_got_commit / expected_commit_got_cancel / open_at_end / unknown_trial）。
    --plan が無いときは {"plan_available": false, "n_trials": N} だけで、CLI は stderr に一致率が出ない旨を
    1 行警告する（終了コードは 0 のまま）。
  ・excluded: 時計の跳び（clock_jump・gt と oracle の両方）と、最後のセッションが閉じないままログが終わった区間
    （log_truncated）。時刻はどちらも隣り合う 2 事象の時刻（時計が戻ったときは end が start より前になりうるので、
    そのときは mono で見る）。★ 各要素に trial_ids（判断 28・影響する試行の trial_id の配列）が付く。oracle の
    跳びは「跳びの直前の事象を含む試行（試行の間なら次の試行）から同じブロックの最後の試行まで」。gt の跳びは
    同じ考え方だが位置は跳びの直前の gt 事象の壁時計を oracle の試行の区間に当てて決め、加えて跳びを区間の中に
    含むセッションの trial_id も足す。log_truncated は閉じなかったセッションの trial_id（null なら空）。

⚠️ 読むのは正解側（gt / oracle / plan）だけで、観測側のログは読まない。
⚠️ gt / oracle の行の形の検査は kit/formats/validate_logs.py の仕事（ここでは必要な欄だけ読む）。
   出力は種別・整数・列挙だけで、本文は載らない。
⚠️ 入力の頑健性: 規則・gt・oracle・plan の JSON はすべて、同じキーが 1 行に 2 回あれば拒否する（object_pairs_hook）。
   深すぎる入れ子（RecursionError）も入力エラーとして拒否する。oracle / plan の trial_id は出力にそのまま出る
   唯一の自由な文字列なので `^[A-Za-z0-9_-]{1,64}$` に絞る。--out が --gt/--oracle/--rules/--plan のどれかと
   同じファイル（os.path.samefile）なら拒否する（出力は同じディレクトリの一時ファイル経由の os.replace）。

exit: 0 = 出力した / 2 = 入力が読めない・規則が壊れている・使い方の誤り。
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
ARROW_KEYS = ("left", "right", "up", "down")
COMMIT_KINDS = ("enter", "digit", "mouse", "none")
MISMATCH_TYPES = (
    "no_session", "unexpected_session", "multiple_sessions",
    "expected_cancel_got_commit", "expected_commit_got_cancel", "open_at_end", "unknown_trial",
)
_OPS = ("gt", "ge", "lt", "le", "eq", "ne")
_BLOCK_KEYS = ("start", "commit", "cancel", "candidate", "candidate_end", "clock_jump_ms")
# ★ oracle / plan の trial_id は出力にそのまま出る唯一の自由な文字列（判断 28 のレビュー・security LOW）。
TRIAL_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class InputError(ValueError):
    """入力（ログ・規則・計画）が読めない。exit 2。"""


# ---------------------------------------------------------------- gt/1 の表（validate_logs.py の表を流用）

def _gt_tables():
    d = os.path.normpath(os.path.join(_HERE, os.pardir, "formats"))
    if d not in sys.path:
        sys.path.insert(0, d)
    import validate_logs
    return validate_logs.GT_EVENTS, validate_logs.GT_SRCS, validate_logs.ENUM_FIELDS


# ---------------------------------------------------------------- 入力の読み取り

def _no_float(_s):
    raise InputError("小数・指数表記の数は読まない")


def _no_constant(_s):
    raise InputError("NaN / Infinity は読まない")


def _lines(data, what):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("%s: UTF-8 として読めない" % what)
    out = []
    for n, raw in enumerate(text.split("\n"), 1):
        raw = raw.rstrip("\r")
        if raw.strip():
            out.append((n, raw))
    return out


def _no_dup_pairs(pairs, where):
    seen = set()
    out = {}
    for k, v in pairs:
        if k in seen:
            raise InputError("%s: 同じキーが 1 行に 2 回ある" % where)
        seen.add(k)
        out[k] = v
    return out


def _loads(raw, where):
    try:
        return json.loads(raw, parse_float=_no_float, parse_constant=_no_constant,
                          object_pairs_hook=lambda pairs: _no_dup_pairs(pairs, where))
    except InputError:
        raise
    except (ValueError, RecursionError):
        raise InputError("%s: JSON として読めない" % where)


def _is_int(v):
    return type(v) is int


def _read_times(row, where):
    for k in ("t_wall_ms", "t_mono_ns"):
        if not _is_int(row.get(k)):
            raise InputError("%s: %s が整数でない" % (where, k))


def _check_trial_id(v, where):
    if not isinstance(v, str) or not TRIAL_ID_RE.fullmatch(v):
        raise InputError("%s: trial_id の形が違う（^[A-Za-z0-9_-]{1,64}$ でない）" % where)


def parse_gt(data):
    """gt/1 → (src, 事象の配列)。事象は単調時計が非減少であること。"""
    _events, srcs, _enum = _gt_tables()
    lines = _lines(data, "gt")
    if not lines:
        raise InputError("gt: 空のファイル")
    hdr = _loads(lines[0][1], "gt:%d" % lines[0][0])
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "gt/1":
        raise InputError("gt: 1 行目が gt/1 のヘッダでない")
    src = hdr.get("src")
    if src not in srcs:
        raise InputError("gt: ヘッダの src が既知の値でない")
    events = []
    prev_mono = None
    for n, raw in lines[1:]:
        where = "gt:%d" % n
        row = _loads(raw, where)
        if not isinstance(row, dict) or row.get("kind") != "ev" or not isinstance(row.get("ev"), str):
            raise InputError("%s: ev 行でない" % where)
        _read_times(row, where)
        if prev_mono is not None and row["t_mono_ns"] < prev_mono:
            raise InputError("%s: 単調時計が戻っている（時刻順でない）" % where)
        prev_mono = row["t_mono_ns"]
        events.append(row)
    return src, events


def parse_oracle(data):
    """oracle/1 → {"plan_sha256", "rows"（ヘッダ以外）, "trials"（試行の窓）,
    "arrows"（矢印の押下の壁時計と trial_id）, "block_of_trial", "trials_by_block"（判断 28 の除外の位置決め用）}。
    """
    lines = _lines(data, "oracle")
    if not lines:
        raise InputError("oracle: 空のファイル")
    hdr = _loads(lines[0][1], "oracle:%d" % lines[0][0])
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "oracle/1":
        raise InputError("oracle: 1 行目が oracle/1 のヘッダでない")
    rows, trials, arrows = [], [], []
    open_trial = None
    seen = set()
    prev_mono = None
    block_of_trial, trials_by_block = {}, {}
    cur_block = None
    for n, raw in lines[1:]:
        where = "oracle:%d" % n
        row = _loads(raw, where)
        if not isinstance(row, dict) or not isinstance(row.get("kind"), str):
            raise InputError("%s: kind が無い" % where)
        _read_times(row, where)
        if prev_mono is not None and row["t_mono_ns"] < prev_mono:
            raise InputError("%s: 単調時計が戻っている（時刻順でない）" % where)
        prev_mono = row["t_mono_ns"]
        rows.append(row)
        kind = row["kind"]
        if kind == "block_begin":
            cur_block = row.get("block_id")
            trials_by_block.setdefault(cur_block, [])
        elif kind == "block_end":
            cur_block = None
        elif kind == "trial_begin":
            tid = row.get("trial_id")
            if open_trial is not None:
                raise InputError("%s: 試行が入れ子になっている" % where)
            _check_trial_id(tid, where)
            if tid in seen:
                raise InputError("%s: trial_id が重複している" % where)
            seen.add(tid)
            open_trial = {"trial_id": tid, "begin_wall_ms": row["t_wall_ms"]}
            if cur_block is not None:
                block_of_trial[tid] = cur_block
                trials_by_block.setdefault(cur_block, []).append(tid)
        elif kind == "trial_end":
            if open_trial is None or row.get("trial_id") != open_trial["trial_id"]:
                raise InputError("%s: trial_end が対応する trial_begin と合わない" % where)
            open_trial["end_wall_ms"] = row["t_wall_ms"]
            trials.append(open_trial)
            open_trial = None
        elif kind == "sent":
            tid = row.get("trial_id")
            _check_trial_id(tid, where)
            if row.get("key") in ARROW_KEYS and row.get("down") is True:
                arrows.append((row["t_wall_ms"], tid))
    if open_trial is not None:
        raise InputError("oracle: trial_end が無いまま終わった試行がある")
    return {"plan_sha256": hdr.get("plan_sha256"), "rows": rows, "trials": trials, "arrows": arrows,
            "block_of_trial": block_of_trial, "trials_by_block": trials_by_block}


def parse_plan(data):
    """plan/1 → {trial_id: intent}。使う 3 つの意図だけ検査する。"""
    lines = _lines(data, "plan")
    if not lines:
        raise InputError("plan: 空のファイル")
    hdr = _loads(lines[0][1], "plan:%d" % lines[0][0])
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "plan/1":
        raise InputError("plan: 1 行目が plan/1 のヘッダでない")
    out = {}
    for n, raw in lines[1:]:
        where = "plan:%d" % n
        row = _loads(raw, where)
        if not isinstance(row, dict) or row.get("kind") != "trial":
            continue
        tid, it = row.get("trial_id"), row.get("intent")
        _check_trial_id(tid, where)
        if tid in out:
            raise InputError("%s: trial_id が重複している" % where)
        if (not isinstance(it, dict) or type(it.get("expect_session")) is not bool
                or type(it.get("abandon")) is not bool or it.get("commit") not in COMMIT_KINDS):
            raise InputError("%s: intent の形が違う（expect_session / abandon / commit）" % where)
        out[tid] = {"expect_session": it["expect_session"], "abandon": it["abandon"], "commit": it["commit"]}
    return out


# ---------------------------------------------------------------- 規則のコンパイル

class _Cond(object):
    __slots__ = ("ev", "preds", "after_result", "nfb", "within_ms")

    def __init__(self, ev, preds, after_result, nfb, within_ms):
        self.ev, self.preds, self.after_result, self.nfb, self.within_ms = ev, preds, after_result, nfb, within_ms


class _Block(object):
    __slots__ = ("start", "commit", "cancel", "candidate", "candidate_end", "clock_jump_ms")


def _compile_pred(key, val, ev_fields, enum_fields, where):
    field, op = key, "eq"
    head, sep, tail = key.rpartition("_")
    if sep and tail in _OPS and head in ev_fields:
        field, op = head, tail
    if field not in ev_fields:
        raise InputError("%s: 条件のキー '%s' はこの ev の欄でも予約語でもない" % (where, key))
    if field in enum_fields:
        if op not in ("eq", "ne") or not isinstance(val, str) or val not in enum_fields[field]:
            raise InputError("%s: '%s' は列挙の欄（eq / ne と列挙の値だけ）" % (where, key))
    elif not _is_int(val):
        raise InputError("%s: '%s' の値は整数" % (where, key))
    return (field, op, val)


def _compile_cond(obj, where, src, role):
    events, _srcs, enum_fields = _gt_tables()
    if not isinstance(obj, dict):
        raise InputError("%s: 条件はオブジェクト" % where)
    ev = obj.get("ev")
    if not isinstance(ev, str) or ev not in events[src]:
        raise InputError("%s: ev が無い、またはこの src の ev でない" % where)
    req, opt = events[src][ev]
    ev_fields = set(req + opt)
    closing = role in ("commit", "cancel")
    preds, after_result, nfb, within_ms = [], None, None, None
    for key, val in obj.items():
        if key == "ev":
            continue
        if key in ("after_result", "not_followed_by", "within_ms"):
            if not closing:
                raise InputError("%s: '%s' は commit / cancel の条件だけが持てる" % (where, key))
            if key == "after_result":
                if type(val) is not bool:
                    raise InputError("%s: after_result は真偽値" % where)
                after_result = val
            elif key == "within_ms":
                if not _is_int(val) or val < 0:
                    raise InputError("%s: within_ms は 0 以上の整数" % where)
                within_ms = val
            else:
                nfb = _compile_cond(val, where + ".not_followed_by", src, "nested")
            continue
        preds.append(_compile_pred(key, val, ev_fields, enum_fields, where))
    if (nfb is None) != (within_ms is None):
        raise InputError("%s: not_followed_by と within_ms は一緒に書く" % where)
    return _Cond(ev, tuple(preds), after_result, nfb, within_ms)


def _compile_block(src, obj):
    where = src
    if not isinstance(obj, dict):
        raise InputError("%s: src の規則はオブジェクト" % where)
    for key in obj:
        if key not in _BLOCK_KEYS and not key.startswith("_"):
            raise InputError("%s: 未知のキー '%s'" % (where, key))
    for key in _BLOCK_KEYS:
        if key not in obj:
            raise InputError("%s: '%s' が無い（candidate / candidate_end は null でよい）" % (where, key))
    b = _Block()
    b.start = _compile_cond(obj["start"], where + ".start", src, "start")
    for role in ("commit", "cancel"):
        lst = obj[role]
        if not isinstance(lst, list) or (role == "commit" and not lst):
            raise InputError("%s: %s は配列（commit は 1 件以上）" % (where, role))
        setattr(b, role, tuple(_compile_cond(c, "%s.%s[%d]" % (where, role, i), src, role)
                               for i, c in enumerate(lst)))
    b.candidate = (None if obj["candidate"] is None
                   else _compile_cond(obj["candidate"], where + ".candidate", src, "candidate"))
    b.candidate_end = (None if obj["candidate_end"] is None
                        else _compile_cond(obj["candidate_end"], where + ".candidate_end", src, "candidate_end"))
    if not _is_int(obj["clock_jump_ms"]) or obj["clock_jump_ms"] < 0:
        raise InputError("%s: clock_jump_ms は 0 以上の整数" % where)
    b.clock_jump_ms = obj["clock_jump_ms"]
    return b


def compile_rules(rules_bytes):
    _events, srcs, _enum = _gt_tables()
    try:
        obj = _loads(rules_bytes.decode("utf-8"), "rules")
    except UnicodeDecodeError:
        raise InputError("rules: UTF-8 として読めない")
    if not isinstance(obj, dict):
        raise InputError("rules: 最上位はオブジェクト")
    out = {}
    for src, block in obj.items():
        if src.startswith("_"):
            continue
        if src not in srcs:
            raise InputError("rules: 未知の src '%s'" % src)
        out[src] = _compile_block(src, block)
    if not out:
        raise InputError("rules: src の規則が 1 つも無い")
    return out


# ---------------------------------------------------------------- 事象の照合

def _ev_match(c, e):
    if e.get("ev") != c.ev:
        return False
    for field, op, val in c.preds:
        v = e.get(field)
        if isinstance(val, str):
            if not isinstance(v, str):
                return False
            if (v == val) != (op == "eq"):
                return False
            continue
        if not _is_int(v):
            return False
        if op == "eq" and not v == val:
            return False
        if op == "ne" and not v != val:
            return False
        if op == "gt" and not v > val:
            return False
        if op == "ge" and not v >= val:
            return False
        if op == "lt" and not v < val:
            return False
        if op == "le" and not v <= val:
            return False
    return True


def _has_result(e):
    v = e.get("result_len")
    return _is_int(v) and v > 0


def _close_match(c, events, i, result_seen):
    e = events[i]
    if not _ev_match(c, e):
        return False
    if c.after_result is not None and result_seen != c.after_result:
        return False
    if c.nfb is not None:
        limit = e["t_mono_ns"] + c.within_ms * 1000000
        for j in range(i + 1, len(events)):
            f = events[j]
            if f["t_mono_ns"] > limit:
                break
            if _ev_match(c.nfb, f):
                return False
    return True


def _run_machine(b, events):
    sessions = []
    cur = None
    for i, e in enumerate(events):
        if cur is None:
            if _ev_match(b.start, e):
                cand_open = e["t_wall_ms"] if (b.candidate is not None and _ev_match(b.candidate, e)) else None
                cur = {"start_wall_ms": e["t_wall_ms"], "start_mono_ns": e["t_mono_ns"],
                       "result_seen": _has_result(e),
                       "candidate_shown": None if b.candidate is None else (cand_open is not None),
                       "n_start_while_open": 0, "cand_open": cand_open, "cand_windows": []}
            continue
        if _ev_match(b.start, e):
            cur["n_start_while_open"] += 1
        if _has_result(e):
            cur["result_seen"] = True
        if b.candidate is not None:
            if cur["cand_open"] is None:
                if _ev_match(b.candidate, e):
                    cur["cand_open"] = e["t_wall_ms"]
                    cur["candidate_shown"] = True
            elif b.candidate_end is not None and _ev_match(b.candidate_end, e):
                cur["cand_windows"].append((cur["cand_open"], e["t_wall_ms"]))
                cur["cand_open"] = None
        outcome = None
        for c in b.commit:
            if _close_match(c, events, i, cur["result_seen"]):
                outcome = "commit"
                break
        if outcome is None:
            for c in b.cancel:
                if _close_match(c, events, i, cur["result_seen"]):
                    outcome = "cancel"
                    break
        if outcome is not None:
            cur["end_wall_ms"], cur["end_mono_ns"], cur["outcome"] = e["t_wall_ms"], e["t_mono_ns"], outcome
            sessions.append(cur)
            cur = None
    if cur is not None:
        cur["end_wall_ms"], cur["end_mono_ns"], cur["outcome"] = None, None, "open_at_end"
        sessions.append(cur)
    return sessions


# ---------------------------------------------------------------- 除外・試行への帰属・nav・照合

def _skew_ms(skew_ns):
    q = abs(skew_ns) // 1000000
    return q if skew_ns >= 0 else -q


def _clock_jumps(rows, log, threshold_ms):
    out = []
    for prev, cur in zip(rows, rows[1:]):
        skew_ns = ((cur["t_wall_ms"] - prev["t_wall_ms"]) * 1000000
                   - (cur["t_mono_ns"] - prev["t_mono_ns"]))
        if abs(skew_ns) > threshold_ms * 1000000:
            out.append({"type": "clock_jump", "log": log,
                        "start_wall_ms": prev["t_wall_ms"], "end_wall_ms": cur["t_wall_ms"],
                        "start_mono_ns": prev["t_mono_ns"], "end_mono_ns": cur["t_mono_ns"],
                        "skew_ms": _skew_ms(skew_ns)})
    return out


def _assign_trial(lo_wall, hi_wall, trials):
    best, best_ov = None, 0
    for tr in trials:
        ov = min(hi_wall, tr["end_wall_ms"]) - max(lo_wall, tr["begin_wall_ms"])
        point = (lo_wall == hi_wall and tr["begin_wall_ms"] <= lo_wall <= tr["end_wall_ms"])
        if (ov > best_ov) or (best is None and point):
            best, best_ov = tr, max(ov, 0)
    return None if best is None else best["trial_id"]


def _count_arrows(arrows, lo, hi, trial_id):
    """arrows = [(t_wall_ms, trial_id)…]。区間 [lo, hi]（両端を含む）の中で、trial_id が付いていれば
    その試行の送出だけを数える（判断 27: 確定が遅れて次の試行の矢印を拾わないため）。null なら区間内の全部。"""
    n = 0
    for t, tid in arrows:
        if lo <= t <= hi and (trial_id is None or tid == trial_id):
            n += 1
    return n


def _locate_trial(t_wall_ms, trials):
    """壁時計 t を oracle の試行の並びに当てる: 含む試行があればそれ、無ければ次に始まる試行、
    どちらも無ければ None（判断 28: 除外の trial_ids の位置決め）。trials は出現順（時系列）と仮定する。"""
    for tr in trials:
        if tr["begin_wall_ms"] <= t_wall_ms <= tr["end_wall_ms"]:
            return tr["trial_id"]
    for tr in trials:
        if tr["begin_wall_ms"] > t_wall_ms:
            return tr["trial_id"]
    return None


def _block_range_trial_ids(trial_id, block_of_trial, trials_by_block):
    """位置決めした試行から、同じブロックの最後の試行までの trial_id の列（判断 28）。"""
    if trial_id is None:
        return []
    block_id = block_of_trial.get(trial_id)
    if block_id is None:
        return [trial_id]
    ids = trials_by_block.get(block_id, [])
    if trial_id not in ids:
        return [trial_id]
    return list(ids[ids.index(trial_id):])


def _jump_trial_ids(prev_wall_ms, oracle):
    pos = _locate_trial(prev_wall_ms, oracle["trials"])
    return _block_range_trial_ids(pos, oracle["block_of_trial"], oracle["trials_by_block"])


def _classify(intent, sess):
    if intent is None:
        return "unknown_trial"
    n = len(sess)
    if not intent["expect_session"]:
        return None if n == 0 else "unexpected_session"
    if n == 0:
        return "no_session"
    if n >= 2:
        return "multiple_sessions"
    s = sess[0]
    if s["outcome"] == "open_at_end":
        return "open_at_end"
    want = "cancel" if intent["abandon"] else ("commit" if intent["commit"] != "none" else None)
    if want is None or want == s["outcome"]:
        return None
    return "expected_cancel_got_commit" if want == "cancel" else "expected_commit_got_cancel"


def _agreement(trials, sessions, plan):
    if plan is None:
        return {"plan_available": False, "n_trials": len(trials)}
    by_trial = {}
    for s in sessions:
        if s["trial_id"] is not None:
            by_trial.setdefault(s["trial_id"], []).append(s)
    counts = dict((t, 0) for t in MISMATCH_TYPES)
    mismatches = []
    agree = 0
    for tr in trials:
        tid = tr["trial_id"]
        kind = _classify(plan.get(tid), by_trial.get(tid, []))
        if kind is None:
            agree += 1
        else:
            counts[kind] += 1
            mismatches.append({"trial_id": tid, "type": kind})
    n = len(trials)
    return {"plan_available": True, "n_trials": n, "n_agree": agree,
            "rate": (agree / n if n else None), "by_type": counts, "mismatches": mismatches,
            "unassigned_sessions": sum(1 for s in sessions if s["trial_id"] is None)}


# ---------------------------------------------------------------- 組み立て

def assemble(gt_bytes, oracle_bytes, rules_bytes, plan_bytes=None):
    rules = compile_rules(rules_bytes)
    src, events = parse_gt(gt_bytes)
    if src not in rules:
        raise InputError("rules: この gt の src（%s）の規則が無い" % src)
    b = rules[src]
    oracle = parse_oracle(oracle_bytes)
    plan = None
    if plan_bytes is not None:
        plan = parse_plan(plan_bytes)
        want = oracle["plan_sha256"]
        if not isinstance(want, str) or want.lower() != hashlib.sha256(plan_bytes).hexdigest():
            raise InputError("plan: SHA-256 が oracle のヘッダの plan_sha256 と違う（対応しない計画）")

    sessions = _run_machine(b, events)
    last_wall = events[-1]["t_wall_ms"] if events else None
    for s in sessions:
        hi = last_wall if s["end_wall_ms"] is None else s["end_wall_ms"]
        s["_hi"] = hi
        s["trial_id"] = _assign_trial(s["start_wall_ms"], hi, oracle["trials"])
        s["nav_true"] = _count_arrows(oracle["arrows"], s["start_wall_ms"], hi, s["trial_id"])
        if b.candidate is None:
            s["nav_true_cand"] = None
        else:
            windows = list(s["cand_windows"])
            if s["cand_open"] is not None:
                windows.append((s["cand_open"], hi))
            s["nav_true_cand"] = sum(_count_arrows(oracle["arrows"], lo_c, hi_c, s["trial_id"])
                                     for lo_c, hi_c in windows)

    # ---- 除外（判断 28: excluded の trial_ids と、セッションの excluded_by / n_start_while_open）
    gt_jumps = _clock_jumps(events, "gt", b.clock_jump_ms)
    for j in gt_jumps:
        j["trial_ids"] = _jump_trial_ids(j["start_wall_ms"], oracle)
        lo_j, hi_j = sorted((j["start_wall_ms"], j["end_wall_ms"]))
        for s in sessions:
            if (s["trial_id"] is not None and s["trial_id"] not in j["trial_ids"]
                    and s["start_wall_ms"] <= lo_j and s["_hi"] >= hi_j):
                j["trial_ids"].append(s["trial_id"])
    oc_jumps = _clock_jumps(oracle["rows"], "oracle", b.clock_jump_ms)
    for j in oc_jumps:
        j["trial_ids"] = _jump_trial_ids(j["start_wall_ms"], oracle)
    excluded = gt_jumps + oc_jumps
    if sessions and sessions[-1]["outcome"] == "open_at_end":
        s = sessions[-1]
        excluded.append({"type": "log_truncated", "log": "gt",
                         "start_wall_ms": s["start_wall_ms"], "end_wall_ms": last_wall,
                         "start_mono_ns": s["start_mono_ns"], "end_mono_ns": events[-1]["t_mono_ns"],
                         "trial_ids": [] if s["trial_id"] is None else [s["trial_id"]]})

    for s in sessions:
        reasons = set()
        for e in excluded:
            if s["trial_id"] is not None and s["trial_id"] in e.get("trial_ids", ()):
                reasons.add(e["type"])
            if e["type"] == "clock_jump":
                lo_j, hi_j = sorted((e["start_wall_ms"], e["end_wall_ms"]))
                if s["start_wall_ms"] <= lo_j and s["_hi"] >= hi_j:
                    reasons.add("clock_jump")
        s["excluded_by"] = sorted(reasons)

    pub = [{"trial_id": s["trial_id"], "start_wall_ms": s["start_wall_ms"], "end_wall_ms": s["end_wall_ms"],
            "start_mono_ns": s["start_mono_ns"], "end_mono_ns": s["end_mono_ns"], "outcome": s["outcome"],
            "candidate_shown": s["candidate_shown"], "nav_true": s["nav_true"], "nav_true_cand": s["nav_true_cand"],
            "excluded_by": s["excluded_by"], "n_start_while_open": s["n_start_while_open"]} for s in sessions]
    return {
        "src": src,
        "rules_sha256": hashlib.sha256(rules_bytes).hexdigest(),
        "definitions": {
            "all": list(pub),
            "macos_def": list(pub),
            "windows_def": None if b.candidate is None else [s for s in pub if s["candidate_shown"]],
        },
        "oracle_agreement": _agreement(oracle["trials"], pub, plan),
        "excluded": excluded,
    }


def render(result):
    """出力のバイト列（LF・UTF-8・BOM なし）。同じ入力なら同じバイト列。"""
    return (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _read(path, what):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise InputError("%s: 開けない（%s）" % (what, type(e).__name__))


def _same_file(a, b):
    """--out が既存の入力ファイルと同じか（security LOW）。どちらか無ければ違うファイル扱い。"""
    try:
        return os.path.exists(a) and os.path.exists(b) and os.path.samefile(a, b)
    except OSError:
        return False


def build_sessions(gt_path, oracle_path, rules_path, plan_path=None):
    return assemble(_read(gt_path, "gt"), _read(oracle_path, "oracle"), _read(rules_path, "rules"),
                    None if plan_path is None else _read(plan_path, "plan"))


# ---------------------------------------------------------------- selftest

WALL0 = 1700000000000
MONO0 = 50000000


def _jl(*rows):
    return ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n").encode("utf-8")


def _gt_bytes(src, evs, wall_shift=None):
    """evs = [(t_ms, ev, {欄}), …]。wall_shift = {添字: 壁時計だけを足す ms}（それ以降すべてに効く）。"""
    rows = [{"kind": "header", "format": "gt/1", "src": src, "app_version": "0.1.0",
             "os": "macos" if src == "mac_nstic" else "windows"}]
    shift = 0
    for i, (t, ev, kw) in enumerate(evs):
        shift += (wall_shift or {}).get(i, 0)
        row = {"kind": "ev", "t_wall_ms": WALL0 + t + shift, "t_mono_ns": (MONO0 + t) * 1000000, "ev": ev}
        row.update(kw)
        rows.append(row)
    return _jl(*rows)


def _oracle_bytes(trials, sents=(), plan_sha="0" * 64, wall_shift=None):
    """trials = [(trial_id, begin_ms, end_ms)]、sents = [(t_ms, key, down)]。"""
    items = [(min(t[1] for t in trials) - 50 if trials else 0, 0, {"kind": "block_begin", "block_id": 0})]
    for tid, b, e in trials:
        items.append((b, 1, {"kind": "trial_begin", "trial_id": tid}))
        items.append((e, 3, {"kind": "trial_end", "trial_id": tid}))
    for k, (t, key, down) in enumerate(sents):
        tid = [x[0] for x in trials if x[1] <= t <= x[2]][0]
        items.append((t, 2, {"kind": "sent", "trial_id": tid, "step": k, "key": key, "down": down}))
    if trials:
        items.append((max(t[2] for t in trials) + 50, 4, {"kind": "block_end", "block_id": 0}))
    items.sort(key=lambda x: (x[0], x[1]))
    rows = [{"kind": "header", "format": "oracle/1", "plan_sha256": plan_sha, "os": "macos",
             "emitter_version": "0", "backend": "dryrun"}]
    shift = 0
    for i, (t, _o, row) in enumerate(items):
        shift += (wall_shift or {}).get(i, 0)
        r = dict(row)
        r["t_wall_ms"], r["t_mono_ns"] = WALL0 + t + shift, (MONO0 + t) * 1000000
        rows.append(r)
    return _jl(*rows)


def _plan_bytes(intents):
    rows = [{"kind": "header", "format": "plan/1", "os": "macos", "seed": 1, "generator_version": "0",
             "config_sha256": "0" * 64}]
    for tid, (expect, abandon, commit) in intents:
        rows.append({"kind": "trial", "trial_id": tid, "block_id": 0,
                     "intent": {"expect_session": expect, "abandon": abandon, "commit": commit}})
    return _jl(*rows)


def _example_rules():
    with open(os.path.join(_HERE, "gt_rules.example.json"), "rb") as f:
        return f.read()


def _rules_with(mut):
    obj = json.loads(_example_rules().decode("utf-8"))
    mut(obj)
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def _sm(t, n):
    return (t, "set_marked", {"len": n, "sel_loc": n, "sel_len": 0})


def _ins(t, n):
    return (t, "insert_text", {"len": n})


def _wins(trials, sessions):
    return [x for x in sessions if x["trial_id"] in trials]


def _case_five_types():
    """5 型: 基本（開始 → 確定）・取消・候補窓あり / なし・1 試行に 2 セッション・閉じないまま終わる（3 つの src）。"""
    f = []
    rules = _example_rules()
    # --- mac_nstic: 基本 / 取消 / 2 セッション / 取消に見えて確定 / 閉じない
    evs = [
        _sm(100, 1), _sm(300, 3), _ins(500, 2),                                   # t00001 基本
        _sm(2100, 2), _sm(2300, 0), (2600, "key_down", {"vk": 53}),               # t00002 取消
        _sm(4100, 1), _ins(4200, 1), _sm(4400, 1), (4500, "unmark", {}),          # t00003 2 セッション
        _sm(6100, 2), _sm(6200, 0), _ins(6230, 2),                                # t00004 空にして直後に確定
        _sm(8100, 1), (8300, "focus_out", {}),                                    # t00005 閉じない
    ]
    trials = [("t00001", 0, 900), ("t00002", 2000, 2900), ("t00003", 4000, 4900),
              ("t00004", 6000, 6900), ("t00005", 8000, 8900)]
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials), rules)
    got = [(s["trial_id"], s["outcome"], s["start_wall_ms"] - WALL0,
            None if s["end_wall_ms"] is None else s["end_wall_ms"] - WALL0) for s in r["definitions"]["all"]]
    want = [("t00001", "commit", 100, 500), ("t00002", "cancel", 2100, 2300), ("t00003", "commit", 4100, 4200),
            ("t00003", "commit", 4400, 4500), ("t00004", "commit", 6100, 6230), ("t00005", "open_at_end", 8100, None)]
    if got != want:
        f.append("mac の 5 型が期待と違う: %r" % (got,))
    if len(_wins(("t00003",), r["definitions"]["all"])) != 2:
        f.append("mac: 1 試行に 2 セッションが出ない")
    if r["definitions"]["windows_def"] is not None or any(s["candidate_shown"] is not None for s in r["definitions"]["all"]):
        f.append("mac: 候補窓は取れない（windows_def と candidate_shown は null）")
    if r["definitions"]["macos_def"] != r["definitions"]["all"]:
        f.append("macos_def が all と違う")
    last = r["definitions"]["all"][-1]
    if last["end_wall_ms"] is not None or last["end_mono_ns"] is not None:
        f.append("open_at_end の end_* が null でない")
    if [x["type"] for x in r["excluded"]] != ["log_truncated"]:
        f.append("閉じないまま終わったログが excluded に出ない: %r" % (r["excluded"],))

    # --- win_imm: 候補窓あり / なし（imn 6 は数えない）/ 取消 / 2 セッション / 閉じない
    comp = lambda t, cl, rl: (t, "comp", {"flags": 8, "comp_len": cl, "result_len": rl})
    evs = [
        (100, "start_comp", {}), comp(200, 2, 0), (250, "notify", {"imn": 5}), comp(500, 0, 2), (520, "end_comp", {}),
        (2100, "start_comp", {}), comp(2200, 2, 0), (2250, "notify", {"imn": 6}), (2300, "end_comp", {}),
        (4100, "start_comp", {}), comp(4200, 0, 2), (4250, "end_comp", {}),
        (4400, "start_comp", {}), (4450, "notify", {"imn": 5}), comp(4500, 0, 2), (4550, "end_comp", {}),
        (6100, "start_comp", {}), comp(6200, 2, 0), (6300, "focus_out", {}),
    ]
    trials = [("t00001", 0, 900), ("t00002", 2000, 2900), ("t00003", 4000, 4900), ("t00004", 6000, 6900)]
    r = assemble(_gt_bytes("win_imm", evs), _oracle_bytes(trials), rules)
    got = [(s["trial_id"], s["outcome"], s["candidate_shown"]) for s in r["definitions"]["all"]]
    want = [("t00001", "commit", True), ("t00002", "cancel", False), ("t00003", "commit", False),
            ("t00003", "commit", True), ("t00004", "open_at_end", False)]
    if got != want:
        f.append("win_imm の 5 型が期待と違う: %r" % (got,))
    wd = r["definitions"]["windows_def"]
    if wd is None or [(s["trial_id"], s["start_wall_ms"] - WALL0) for s in wd] != [("t00001", 100), ("t00003", 4400)]:
        f.append("windows_def が候補窓ありのセッションだけを含まない: %r" % (wd,))
    if len(r["definitions"]["all"]) != 5:
        f.append("all が全 composition でない")

    # --- win_tsf: 候補窓あり / reading だけは数えない / 結果 0 は取消 / 閉じない
    evs = [
        (100, "tsf_start", {}), (200, "tsf_update", {"len": 2}), (250, "ui_begin", {"ui_kind": "candidate"}),
        (400, "ui_end", {"ui_kind": "candidate"}), (500, "tsf_end", {"result_len": 2}),
        (2100, "tsf_start", {}), (2200, "tsf_update", {"len": 2}), (2250, "ui_begin", {"ui_kind": "reading"}),
        (2300, "tsf_end", {}),
        (4100, "tsf_start", {}), (4200, "tsf_end", {"result_len": 0}),
        (6100, "tsf_start", {}),
    ]
    trials = [("t00001", 0, 900), ("t00002", 2000, 2900), ("t00003", 4000, 4900), ("t00004", 6000, 6900)]
    r = assemble(_gt_bytes("win_tsf", evs), _oracle_bytes(trials), rules)
    got = [(s["trial_id"], s["outcome"], s["candidate_shown"]) for s in r["definitions"]["all"]]
    want = [("t00001", "commit", True), ("t00002", "cancel", False), ("t00003", "cancel", False),
            ("t00004", "open_at_end", False)]
    if got != want:
        f.append("win_tsf の 5 型が期待と違う: %r" % (got,))
    if r["definitions"]["windows_def"] is None or len(r["definitions"]["windows_def"]) != 1:
        f.append("win_tsf: windows_def が候補窓ありの 1 件でない")
    return f


def _case_nav_interval():
    """nav_true が区間内の矢印だけを数える（区間外の矢印を数えない）。"""
    f = []
    evs = [_sm(500, 1), _ins(1000, 1)]
    trials = [("t00001", 0, 2000)]
    sents = [(100, "left", True), (200, "right", True),                       # 区間の前（数えない）
             (500, "left", True),                                             # 開始と同時（数える・両端を含む）
             (600, "right", True), (650, "right", False), (700, "a", True),   # 離しと矢印でないキーは数えない
             (800, "down", True), (1000, "up", True),                         # 終了と同時（数える）
             (1500, "left", True)]                                            # 区間の後（数えない）
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials, sents), _example_rules())
    got = [s["nav_true"] for s in r["definitions"]["all"]]
    if got != [4]:
        f.append("nav_true が区間内の矢印（押下）だけの 4 でない: %r" % (got,))
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials, [(100, "left", True), (1500, "left", True)]),
                 _example_rules())
    if [s["nav_true"] for s in r["definitions"]["all"]] != [0]:
        f.append("区間外の矢印だけのとき nav_true が 0 でない")
    return f


def _case_nav_true_cand():
    """nav_true_cand: 候補窓が開いていた区間（判断 27・design.md:100）だけの矢印数。mac_nstic は null。"""
    f = []
    comp = lambda t, cl, rl: (t, "comp", {"flags": 8, "comp_len": cl, "result_len": rl})
    evs = [
        (100, "start_comp", {}), (150, "notify", {"imn": 5}),                  # 候補窓 1 回目開く
        comp(200, 2, 0),
        (300, "notify", {"imn": 4}),                                          # 1 回目閉じる
        (350, "notify", {"imn": 5}),                                          # 2 回目開く
        comp(400, 0, 2), (420, "notify", {"imn": 4}),                        # 2 回目閉じる（結果あり）
        (500, "end_comp", {}),                                                # commit（after_result=true）
    ]
    trials = [("t00001", 0, 900)]
    sents = [(120, "left", True),    # 候補窓の前（cand には数えない・nav_true には数える）
             (180, "right", True),   # 窓 1（cand に数える）
             (320, "up", True),      # 窓の間（cand には数えない）
             (380, "down", True),    # 窓 2（cand に数える）
             (600, "left", True)]    # セッションの後（どちらにも数えない）
    r = assemble(_gt_bytes("win_imm", evs), _oracle_bytes(trials, sents), _example_rules())
    s = r["definitions"]["all"][0]
    if s["nav_true"] != 4:
        f.append("nav_true が 4 でない（区間全体・120/180/320/380）: %r" % (s["nav_true"],))
    if s["nav_true_cand"] != 2:
        f.append("nav_true_cand が候補窓の区間だけの 2 でない（180/380）: %r" % (s["nav_true_cand"],))

    # mac_nstic は candidate が null なので nav_true_cand も null
    r2 = assemble(_gt_bytes("mac_nstic", [_sm(100, 1), _ins(500, 2)]),
                  _oracle_bytes([("t00001", 0, 900)], [(200, "left", True)]), _example_rules())
    if r2["definitions"]["all"][0]["nav_true_cand"] is not None:
        f.append("mac_nstic の nav_true_cand が null でない")

    # 規則を変えると変わる（陰性対照）: candidate_end を null にすると窓が session の終わりまで閉じない
    r3 = assemble(_gt_bytes("win_imm", evs), _oracle_bytes(trials, sents),
                 _rules_with(lambda o: o["win_imm"].__setitem__("candidate_end", None)))
    if r3["definitions"]["all"][0]["nav_true_cand"] != 3:  # 180・320・380（150 以降ずっと開いたまま）
        f.append("candidate_end を null にしても nav_true_cand が変わらない: %r" %
                 (r3["definitions"]["all"][0]["nav_true_cand"],))
    return f


def _case_nav_trial_scope():
    """nav_true / nav_true_cand は、セッションが帰属した試行の sent だけを数える
    （確定が遅れて次の試行の矢印を拾わない・判断 27）。trial_id が null のセッションは区間内の全 sent を数える。"""
    f = []
    # セッション A: mac_nstic・開始 100・確定が 950 まで遅れる（試行 t00001=[0,900] に帰属するが、
    # 区間は隣の試行 t00002=[920,1900] にわずかに食い込む）。
    # セッション B: 3000〜3200・どちらの試行にも重ならない（trial_id は null）。
    evs = [_sm(100, 1), _ins(950, 2), _sm(3000, 1), _ins(3200, 2)]
    rows = [{"kind": "header", "format": "oracle/1", "plan_sha256": "0" * 64, "os": "macos",
             "emitter_version": "0", "backend": "dryrun"}]

    def row(kind, t, **kw):
        r = dict(kw, kind=kind, t_wall_ms=WALL0 + t, t_mono_ns=(MONO0 + t) * 1000000)
        return r

    rows += [
        row("trial_begin", 0, trial_id="t00001"),
        row("sent", 200, trial_id="t00001", step=0, key="left", down=True),
        row("trial_end", 900, trial_id="t00001"),
        row("trial_begin", 920, trial_id="t00002"),
        row("sent", 940, trial_id="t00002", step=0, key="right", down=True),   # 隣の試行の矢印（数えない）
        row("sent", 1300, trial_id="t00002", step=1, key="up", down=True),
        row("trial_end", 1900, trial_id="t00002"),
        row("sent", 3100, trial_id="t00002", step=2, key="down", down=True),   # trial_id null のセッション（数える）
    ]
    r = assemble(_gt_bytes("mac_nstic", evs), _jl(*rows), _example_rules())
    sessA, sessB = r["definitions"]["all"]
    if sessA["trial_id"] != "t00001":
        f.append("セッション A の trial_id が t00001 でない: %r" % (sessA["trial_id"],))
    if sessA["nav_true"] != 1:
        f.append("セッション A の nav_true が 1 でない（隣の試行の矢印 940 を拾っている）: %r" % (sessA["nav_true"],))
    if sessB["trial_id"] is not None:
        f.append("セッション B の trial_id が null でない: %r" % (sessB["trial_id"],))
    if sessB["nav_true"] != 1:
        f.append("セッション B（trial_id null）の nav_true が区間内の全 sent（1）でない: %r" % (sessB["nav_true"],))
    return f


def _case_clock_jump():
    """時計の跳び（壁時計だけが進む）を excluded に出す。閾値以下は出さない。gt と oracle の両方。"""
    f = []
    evs = [_sm(100, 1), _sm(300, 3), _ins(500, 2)]
    trials = [("t00001", 0, 900)]
    for skew, expect in ((5000, True), (1001, True), (1000, False), (900, False), (-5000, True)):
        r = assemble(_gt_bytes("mac_nstic", evs, {2: skew}), _oracle_bytes(trials), _example_rules())
        jumps = [x for x in r["excluded"] if x["type"] == "clock_jump"]
        if expect != bool(jumps):
            f.append("gt の壁時計のずれ %d ms（閾値 1000）の扱いが違う: %r" % (skew, jumps))
        if expect and (len(jumps) != 1 or jumps[0]["log"] != "gt" or jumps[0]["skew_ms"] != skew):
            f.append("gt の clock_jump の中身が違う（skew %d）: %r" % (skew, jumps))
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials, wall_shift={2: 5000}), _example_rules())
    jumps = [x for x in r["excluded"] if x["type"] == "clock_jump"]
    if len(jumps) != 1 or jumps[0]["log"] != "oracle":
        f.append("oracle の時計の跳びが excluded に出ない: %r" % (jumps,))
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials), _example_rules())
    if r["excluded"]:
        f.append("跳びが無いのに excluded が空でない")
    return f


def _case_excluded_by():
    """excluded の trial_ids と、セッションの excluded_by / n_start_while_open（判断 28）。"""
    f = []
    # --- シナリオ 1: oracle の時計の跳び。ブロック中央の試行から位置決めし、そこから最後の試行まで。
    #     先頭の試行（t00001）は範囲に入らず、区間も跳びをまたがないので excluded_by は空（陰性対照）。
    trials = [("t00001", 0, 900), ("t00002", 1000, 1900), ("t00003", 2000, 2900)]
    evs = [_sm(100, 1), _ins(500, 2),                                  # セッション 1（t00001）
           _sm(1100, 1), _sm(1150, 1), _ins(1500, 2),                  # セッション 2（t00002・開いている間に start 1 回）
           _sm(2100, 1), _ins(2500, 2)]                                # セッション 3（t00003）
    # wall_shift の添字は _oracle_bytes の items（block_begin, t1begin, t1end, t2begin, t2end, t3begin, t3end, block_end）の並び。
    r = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials, wall_shift={4: 5000}), _example_rules())
    jumps = [x for x in r["excluded"] if x["type"] == "clock_jump"]
    if len(r["excluded"]) != 1 or len(jumps) != 1 or jumps[0]["log"] != "oracle":
        f.append("シナリオ1: oracle の時計の跳びがちょうど 1 件でない: %r" % (r["excluded"],))
    elif set(jumps[0]["trial_ids"]) != {"t00002", "t00003"}:
        f.append("シナリオ1: trial_ids がブロック中央から最後までの {t00002,t00003} でない: %r" % (jumps[0]["trial_ids"],))
    s1, s2, s3 = r["definitions"]["all"]
    if s1["excluded_by"] != []:
        f.append("シナリオ1: 範囲外・区間も跳ばないセッション 1 の excluded_by が空でない: %r" % (s1["excluded_by"],))
    if s2["excluded_by"] != ["clock_jump"] or s3["excluded_by"] != ["clock_jump"]:
        f.append("シナリオ1: セッション 2/3 の excluded_by に clock_jump が無い: %r / %r" %
                 (s2["excluded_by"], s3["excluded_by"]))
    if (s1["n_start_while_open"], s2["n_start_while_open"], s3["n_start_while_open"]) != (0, 1, 0):
        f.append("シナリオ1: n_start_while_open が (0,1,0) でない: %r" %
                 ((s1["n_start_while_open"], s2["n_start_while_open"], s3["n_start_while_open"]),))

    # --- シナリオ 2: gt の時計の跳び。位置決めした試行（t00002）だけでは基準の範囲に入らない
    #     セッション（trial_id=t00001）が、区間の中に跳びを含むので trial_ids に足される（判断 28「加えて」）。
    trials2 = [("t00001", 0, 900), ("t00002", 3000, 5000)]
    evs2 = [_sm(100, 1), (1005, "focus_out", {}), (1010, "focus_in", {}), _ins(1050, 2)]
    r2 = assemble(_gt_bytes("mac_nstic", evs2, wall_shift={2: 1001}), _oracle_bytes(trials2), _example_rules())
    jumps2 = [x for x in r2["excluded"] if x["type"] == "clock_jump"]
    if len(jumps2) != 1 or jumps2[0]["log"] != "gt":
        f.append("シナリオ2: gt の時計の跳びがちょうど 1 件でない: %r" % (r2["excluded"],))
    elif set(jumps2[0]["trial_ids"]) != {"t00001", "t00002"}:
        f.append("シナリオ2: trial_ids に位置決めした t00002 と、区間が跳びを含む t00001 の両方が無い: %r" %
                 (jumps2[0]["trial_ids"],))
    if r2["definitions"]["all"][0]["trial_id"] != "t00001":
        f.append("シナリオ2: セッションの trial_id が t00001 でない: %r" % (r2["definitions"]["all"][0]["trial_id"],))

    # --- シナリオ 3: log_truncated の trial_ids（閉じなかったセッションの trial_id）。
    trials3 = [("t00001", 0, 900)]
    r3 = assemble(_gt_bytes("mac_nstic", [_sm(100, 1), (300, "focus_out", {})]), _oracle_bytes(trials3),
                 _example_rules())
    trunc = [x for x in r3["excluded"] if x["type"] == "log_truncated"]
    if len(trunc) != 1 or trunc[0]["trial_ids"] != ["t00001"]:
        f.append("シナリオ3: log_truncated の trial_ids が [t00001] でない: %r" % (trunc,))
    if r3["definitions"]["all"][0]["excluded_by"] != ["log_truncated"]:
        f.append("シナリオ3: 閉じなかったセッションの excluded_by が [log_truncated] でない: %r" %
                 (r3["definitions"]["all"][0]["excluded_by"],))
    return f


def _case_rules_change_result():
    """規則を変えると結果が変わる（規則が本当に読まれている・陰性対照）。"""
    f = []
    evs = [_sm(100, 1), _sm(300, 3), _ins(500, 2), _sm(1100, 2), _sm(1200, 0), _ins(1230, 2)]
    trials = [("t00001", 0, 900), ("t00002", 1000, 1900)]
    gt, orc = _gt_bytes("mac_nstic", evs), _oracle_bytes(trials)
    base_rules = _example_rules()
    base = assemble(gt, orc, base_rules)
    if assemble(gt, orc, base_rules) != base:
        f.append("同じ規則で結果が変わる（非決定的）")
    b_out = [(s["outcome"], s["start_wall_ms"] - WALL0) for s in base["definitions"]["all"]]
    if b_out != [("commit", 100), ("commit", 1100)]:
        f.append("基準の結果が期待と違う: %r" % (b_out,))

    def only_unmark(o):
        o["mac_nstic"]["commit"] = [{"ev": "unmark"}]

    def start_len_gt_1(o):
        o["mac_nstic"]["start"] = {"ev": "set_marked", "len_gt": 1}

    def tight_within(o):
        o["mac_nstic"]["cancel"][0]["within_ms"] = 5

    def jump_loose(o):
        o["mac_nstic"]["clock_jump_ms"] = 10

    variants = (
        ("commit を unmark だけにする", only_unmark, lambda r: [s["outcome"] for s in r["definitions"]["all"]] == ["open_at_end"]),
        ("start を len_gt 1 にする", start_len_gt_1,
         lambda r: r["definitions"]["all"][0]["start_wall_ms"] - WALL0 == 300),
        ("within_ms を 5 にする（30 ms 後の確定を待たず取消）", tight_within,
         lambda r: [(s["outcome"]) for s in r["definitions"]["all"]] == ["commit", "cancel"]),
    )
    for name, mut, check in variants:
        rules = _rules_with(mut)
        r = assemble(gt, orc, rules)
        if r == base or r["rules_sha256"] == base["rules_sha256"]:
            f.append("規則（%s）を変えても結果が変わらない" % name)
        elif not check(r):
            f.append("規則（%s）を変えたときの結果が期待と違う: %r" % (name, r["definitions"]["all"]))
    # 候補窓の規則（win_imm: imn 5 → 6）
    evs = [(100, "start_comp", {}), (150, "notify", {"imn": 5}), (300, "comp", {"flags": 8, "comp_len": 0, "result_len": 2}),
           (320, "end_comp", {})]
    gt_w, orc_w = _gt_bytes("win_imm", evs), _oracle_bytes([("t00001", 0, 900)])
    a = assemble(gt_w, orc_w, base_rules)
    b = assemble(gt_w, orc_w, _rules_with(lambda o: o["win_imm"].__setitem__("candidate", {"ev": "notify", "imn": 6})))
    if not (a["definitions"]["all"][0]["candidate_shown"] is True and b["definitions"]["all"][0]["candidate_shown"] is False):
        f.append("candidate の規則を変えても candidate_shown が変わらない")
    # 時計の跳びの閾値
    evs = [_sm(100, 1), _ins(500, 2)]
    gt_j = _gt_bytes("mac_nstic", evs, {1: 3000})
    if not (assemble(gt_j, orc, base_rules)["excluded"]
            and not assemble(gt_j, orc, _rules_with(lambda o: o["mac_nstic"].__setitem__("clock_jump_ms", 10000)))["excluded"]):
        f.append("clock_jump_ms を変えても excluded が変わらない")
    return f


def _case_agreement():
    """oracle と正解の一致率と、不一致の型ごとの件数。"""
    f = []
    T = lambda k: "t%05d" % k
    evs = [_sm(100, 1), _ins(300, 2)]                                                   # 迷子（試行の外）
    plan_intents = []
    trials = []
    k = 0

    def add(expect, abandon, commit, evlist=None, in_plan=True):
        nonlocal k
        k += 1
        base = k * 2000
        trials.append((T(k), base, base + 900))
        if in_plan:
            plan_intents.append((T(k), (expect, abandon, commit)))
        for (t, ev, kw) in (evlist or ()):
            evs.append((base + t, ev, kw))

    commit_seq = [_sm(100, 1), _ins(300, 2)]
    cancel_seq = [_sm(100, 2), _sm(300, 0), (600, "key_down", {"vk": 53})]
    add(True, False, "enter", commit_seq)                                        # 1 一致（確定）
    add(False, False, "none")                                                    # 2 一致（開かないはずで開かない）
    add(True, False, "enter")                                                    # 3 no_session
    add(False, False, "none", commit_seq)                                        # 4 unexpected_session
    add(True, False, "enter", cancel_seq)                                        # 5 expected_commit_got_cancel
    add(True, True, "none", commit_seq)                                          # 6 expected_cancel_got_commit
    add(True, False, "enter", commit_seq + [_sm(500, 1), _ins(700, 1)])          # 7 multiple_sessions
    add(True, True, "none", cancel_seq)                                          # 8 一致（取消）
    add(True, False, "none", commit_seq)                                         # 9 一致（結果の指定なし）
    add(True, False, "enter", None, in_plan=False)                               # 10 unknown_trial
    add(True, False, "enter", [_sm(100, 1), (300, "focus_out", {})])             # 11 open_at_end
    # ★ open_at_end は最後のセッションでなければならないので 10 を 11 の前に置いた（時刻順は k で決まる）
    evs.sort(key=lambda x: x[0])
    plan = _plan_bytes(plan_intents)
    sha = hashlib.sha256(plan).hexdigest()
    orc = _oracle_bytes(trials, plan_sha=sha)
    r = assemble(_gt_bytes("mac_nstic", evs), orc, _example_rules(), plan)
    ag = r["oracle_agreement"]
    want_types = dict((t, 0) for t in MISMATCH_TYPES)
    for t in ("no_session", "unexpected_session", "expected_commit_got_cancel", "expected_cancel_got_commit",
              "multiple_sessions", "unknown_trial", "open_at_end"):
        want_types[t] = 1
    want_ids = [(T(3), "no_session"), (T(4), "unexpected_session"), (T(5), "expected_commit_got_cancel"),
                (T(6), "expected_cancel_got_commit"), (T(7), "multiple_sessions"), (T(10), "unknown_trial"),
                (T(11), "open_at_end")]
    if (ag.get("plan_available"), ag.get("n_trials"), ag.get("n_agree")) != (True, 11, 4):
        f.append("一致の件数が期待（11 試行中 4 件）と違う: %r" % ({k2: ag.get(k2) for k2 in ("plan_available", "n_trials", "n_agree")},))
    if ag.get("by_type") != want_types:
        f.append("不一致の型ごとの件数が期待と違う: %r" % (ag.get("by_type"),))
    if [(m["trial_id"], m["type"]) for m in ag.get("mismatches", [])] != want_ids:
        f.append("不一致の試行と型が期待と違う: %r" % (ag.get("mismatches"),))
    if ag.get("rate") != 4 / 11:
        f.append("一致率が 4/11 でない")
    if ag.get("unassigned_sessions") != 1:
        f.append("試行の外のセッション（1 件）が unassigned_sessions に数えられない: %r" % (ag.get("unassigned_sessions"),))
    if not any(s["trial_id"] is None for s in r["definitions"]["all"]):
        f.append("試行と重ならないセッションの trial_id が null でない")
    # plan なし
    r0 = assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials), _example_rules())
    if r0["oracle_agreement"] != {"plan_available": False, "n_trials": 11}:
        f.append("plan が無いときの oracle_agreement が期待と違う: %r" % (r0["oracle_agreement"],))
    # 対応しない plan は拒否
    try:
        assemble(_gt_bytes("mac_nstic", evs), _oracle_bytes(trials, plan_sha="0" * 64), _example_rules(), plan)
        f.append("oracle のヘッダと SHA-256 が違う plan を拒否しない")
    except InputError:
        pass
    return f


def _case_rules_validation():
    """壊れた規則は黙って通さない（InputError）。"""
    f = []
    good = json.loads(_example_rules().decode("utf-8"))

    def mut(fn):
        o = json.loads(json.dumps(good))
        fn(o)
        return json.dumps(o).encode("utf-8")

    bad = (
        ("未知の src", lambda o: o.__setitem__("mac_nstc", o["mac_nstic"])),
        ("src のブロックの未知のキー", lambda o: o["mac_nstic"].__setitem__("comit", [])),
        ("clock_jump_ms が無い", lambda o: o["mac_nstic"].pop("clock_jump_ms")),
        ("candidate が無い（null と書くこと）", lambda o: o["win_imm"].pop("candidate")),
        ("candidate_end が無い（null と書くこと）", lambda o: o["win_imm"].pop("candidate_end")),
        ("commit が空", lambda o: o["mac_nstic"].__setitem__("commit", [])),
        ("not_followed_by だけで within_ms が無い", lambda o: o["mac_nstic"]["cancel"][0].pop("within_ms")),
        ("within_ms だけで not_followed_by が無い", lambda o: o["mac_nstic"]["commit"][0].__setitem__("within_ms", 5)),
        ("その src に無い ev", lambda o: o["win_imm"].__setitem__("start", {"ev": "set_marked"})),
        ("その ev に無い欄", lambda o: o["mac_nstic"]["start"].__setitem__("comp_len_gt", 0)),
        ("整数でない値", lambda o: o["mac_nstic"]["start"].__setitem__("len_gt", "0")),
        ("列挙の外の値", lambda o: o["win_tsf"]["candidate"].__setitem__("ui_kind", "bogus")),
        ("start に after_result", lambda o: o["win_imm"]["start"].__setitem__("after_result", True)),
        ("after_result が真偽値でない", lambda o: o["win_imm"]["commit"][0].__setitem__("after_result", 1)),
        ("src の規則が 1 つも無い", lambda o: [o.pop(k) for k in ("mac_nstic", "win_imm", "win_tsf")]),
    )
    for name, fn in bad:
        try:
            compile_rules(mut(fn))
            f.append("壊れた規則（%s）を拒否しない" % name)
        except InputError:
            pass
        except Exception as e:  # 異常終了は拒否と数えない
            f.append("壊れた規則（%s）で InputError でなく %s" % (name, type(e).__name__))
    try:
        compile_rules(json.dumps(good).encode("utf-8"))
    except InputError as e:
        f.append("正しい規則を拒否した: %s" % e)
    # 入力ログの拒否
    evs = [_sm(100, 1), _ins(500, 2)]
    ok_gt, ok_or = _gt_bytes("mac_nstic", evs), _oracle_bytes([("t00001", 0, 900)])
    back = _gt_bytes("mac_nstic", [_sm(500, 1), _ins(100, 2)])
    trunc = ok_or.split(b"\n")
    trunc = b"\n".join(x for x in trunc if b'"trial_end"' not in x)
    for name, gt, orc, rules in (
            ("単調時計が戻る gt", back, ok_or, _example_rules()),
            ("trial_end が無い oracle", ok_gt, trunc, _example_rules()),
            ("ヘッダが違う gt", ok_or, ok_or, _example_rules()),
            ("その src の規則が無い", _gt_bytes("win_imm", [(100, "start_comp", {})]), ok_or,
             mut(lambda o: o.pop("win_imm")))):
        try:
            assemble(gt, orc, rules)
            f.append("壊れた入力（%s）を拒否しない" % name)
        except InputError:
            pass
    return f


def _case_input_hardening():
    """入力の頑健性（security LOW）: 重複キーの JSON・深すぎる入れ子・oracle / plan の trial_id の形。"""
    f = []
    try:
        _loads('{"a":1,"a":2}', "dup-test")
        f.append("同じキーが 1 行に 2 回ある JSON を拒否しない")
    except InputError:
        pass
    deep = ("[" * 3000) + ("]" * 3000)
    try:
        _loads(deep, "deep-test")
        f.append("深すぎる入れ子の JSON（RecursionError）を拒否しない")
    except InputError:
        pass
    try:
        assemble(_gt_bytes("mac_nstic", [_sm(100, 1), _ins(500, 2)]), _oracle_bytes([("bad id!", 0, 900)]),
                 _example_rules())
        f.append("oracle の trial_id（記号入り）を拒否しない")
    except InputError:
        pass
    try:
        assemble(_gt_bytes("mac_nstic", [_sm(100, 1), _ins(500, 2)]), _oracle_bytes([("t" * 65, 0, 900)]),
                 _example_rules())
        f.append("oracle の trial_id（65 文字）を拒否しない")
    except InputError:
        pass
    try:
        parse_plan(_plan_bytes([("bad id!", (True, False, "enter"))]))
        f.append("plan の trial_id（記号入り）を拒否しない")
    except InputError:
        pass
    try:
        parse_plan(_plan_bytes([("t00001", (True, False, "enter"))]))  # 陽性対照: 普通の trial_id は通る
    except InputError as e:
        f.append("普通の trial_id を拒否した: %s" % e)
    return f


def _case_example_rules_minimal():
    """例の規則で最小の入力（macOS の開始 → 確定 1 回）が動く。"""
    f = []
    r = assemble(_gt_bytes("mac_nstic", [_sm(100, 1), _sm(200, 3), _ins(500, 2)]),
                 _oracle_bytes([("t00001", 0, 600)]), _example_rules())
    if len(r["definitions"]["all"]) != 1 or r["definitions"]["windows_def"] is not None:
        f.append("例の規則で最小の入力が 1 セッションにならない")
    if r["rules_sha256"] != hashlib.sha256(_example_rules()).hexdigest():
        f.append("rules_sha256 が規則ファイルのバイト列の SHA-256 でない")
    return f


def _case_cli_bytes_identical():
    """CLI: 同じ入力で出力がバイト一致・LF・BOM なし。壊れた入力は exit 2（異常終了でない）。"""
    f = []
    tmp = tempfile.mkdtemp(prefix="gt_sessions_selftest_")
    me = os.path.abspath(__file__)
    env = dict(os.environ, PYTHONUTF8="1")
    paths = {}
    try:
        evs = [_sm(100, 1), _sm(300, 3), _ins(500, 2), _sm(2100, 2), _sm(2300, 0), (2600, "key_down", {"vk": 53})]
        plan = _plan_bytes([("t00001", (True, False, "enter")), ("t00002", (True, True, "none"))])
        files = {"gt.jsonl": _gt_bytes("mac_nstic", evs),
                 "oracle.jsonl": _oracle_bytes([("t00001", 0, 900), ("t00002", 2000, 2900)],
                                               plan_sha=hashlib.sha256(plan).hexdigest()),
                 "plan.jsonl": plan, "rules.json": _example_rules()}
        for name, data in files.items():
            paths[name] = os.path.join(tmp, name)
            with open(paths[name], "wb") as fh:
                fh.write(data)

        def run(*args):
            p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env)
            return p.returncode, p.stdout.decode("utf-8", "replace")

        base = ["--gt", paths["gt.jsonl"], "--oracle", paths["oracle.jsonl"], "--rules", paths["rules.json"]]
        outs = []
        for i in range(2):
            o = os.path.join(tmp, "out%d" % i, "s.json")
            rc, text = run(*(base + ["--plan", paths["plan.jsonl"], "--out", o]))
            if rc != 0:
                f.append("CLI が exit 0 でない（%d）: %s" % (rc, text.strip()[-200:]))
                return f
            with open(o, "rb") as fh:
                outs.append(fh.read())
        if outs[0] != outs[1]:
            f.append("同じ入力で出力がバイト一致しない")
        if b"\r" in outs[0] or outs[0].startswith(b"\xef\xbb\xbf") or not outs[0].endswith(b"\n"):
            f.append("出力が LF・BOM なし・末尾改行でない")
        d = json.loads(outs[0].decode("utf-8"))
        if d["oracle_agreement"].get("n_agree") != 2 or len(d["definitions"]["all"]) != 2:
            f.append("CLI の出力の中身が期待と違う")
        if outs[0] != render(assemble(files["gt.jsonl"], files["oracle.jsonl"], files["rules.json"], plan)):
            f.append("CLI の出力が assemble の結果と違う")

        # --plan が無いときは一致率が出ない旨の警告（項目3 MEDIUM）。exit code は 0 のまま。
        o_noplan = os.path.join(tmp, "noplan.json")
        rc, text = run(*(base + ["--out", o_noplan]))
        if rc != 0:
            f.append("--plan なしの CLI が exit 0 でない（%d）" % rc)
        elif "一致率が出ない" not in text:
            f.append("--plan が無いときに警告が出ない: %s" % text.strip()[-200:])
        rc, text = run(*(base + ["--plan", paths["plan.jsonl"], "--out", os.path.join(tmp, "withplan.json")]))
        if rc == 0 and "一致率が出ない" in text:
            f.append("--plan があるのに一致率が出ない旨の警告が出ている")

        # --out が既存の入力ファイルと同じなら exit 2（security LOW）。入力ファイルも壊れないこと。
        rc, text = run(*(base + ["--plan", paths["plan.jsonl"], "--out", paths["gt.jsonl"]]))
        if rc != 2 or "Traceback" in text:
            f.append("--out が --gt と同じファイルなのに exit 2 でない（%d）: %s" % (rc, text.strip()[-160:]))
        with open(paths["gt.jsonl"], "rb") as fh:
            if fh.read() != files["gt.jsonl"]:
                f.append("--out が入力と同じ判定のはずが入力ファイルが書き換わった")

        o = os.path.join(tmp, "x.json")
        for name, args in (
                ("gt が無い", ["--gt", os.path.join(tmp, "none.jsonl")] + base[2:] + ["--out", o]),
                ("対応しない plan", base + ["--plan", paths["rules.json"], "--out", o])):
            rc, text = run(*args)
            if rc != 2 or "Traceback" in text:
                f.append("CLI（%s）が exit 2 でない（%d）: %s" % (name, rc, text.strip()[-160:]))
        rc, text = run("--gt", paths["gt.jsonl"])
        if rc != 2:
            f.append("引数が足りないのが exit 2 でない（%d）" % rc)
        if os.path.exists(o):
            f.append("失敗したのに出力ファイルができている")
    finally:
        for root, dirs, names in os.walk(tmp, topdown=False):
            for n in names:
                os.remove(os.path.join(root, n))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(tmp)
    return f


CASES = (
    ("5 型（開始 → 確定・取消・候補窓あり / なし・1 試行に 2 セッション・閉じないまま終わる）× 3 つの src", _case_five_types),
    ("nav_true は区間内の矢印だけを数える（区間外の矢印を数えない）", _case_nav_interval),
    ("nav_true_cand は候補窓が開いていた区間だけを数える（判断 27）", _case_nav_true_cand),
    ("nav_true / nav_true_cand は帰属した試行の sent だけを数える（試行の限定・判断 27）", _case_nav_trial_scope),
    ("時計の跳び（壁時計だけが進む）を excluded に出す", _case_clock_jump),
    ("excluded の trial_ids とセッションの excluded_by / n_start_while_open（判断 28）", _case_excluded_by),
    ("規則を変えると結果が変わる（陰性対照）", _case_rules_change_result),
    ("oracle ↔ 正解の一致率と不一致の型", _case_agreement),
    ("壊れた規則・入力を拒否する", _case_rules_validation),
    ("入力の頑健性（重複キー・深い入れ子・trial_id の形）", _case_input_hardening),
    ("例の規則で最小の入力が動く", _case_example_rules_minimal),
    ("CLI: バイト一致・exit code", _case_cli_bytes_identical),
)


def selftest():
    bad = 0
    for name, fn in CASES:
        try:
            fails = fn()
        except Exception as e:  # 想定外の例外は失敗
            fails = ["例外 %s: %s" % (type(e).__name__, e)]
        if fails:
            bad += 1
            print("  ❌ " + name)
            for m in fails:
                print("     FAIL " + m)
        else:
            print("  ✅ " + name)
    if bad:
        print("selftest 失敗 %d 件 / %d 件" % (bad, len(CASES)))
        return 1
    print("selftest OK（%d 件）" % len(CASES))
    return 0


# ---------------------------------------------------------------- CLI

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="正解の組み立て（gt/1 ＋ oracle/1 → 変換セッション）")
    ap.add_argument("--gt")
    ap.add_argument("--oracle")
    ap.add_argument("--rules")
    ap.add_argument("--plan")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.gt and args.oracle and args.rules and args.out):
        ap.error("--gt / --oracle / --rules / --out が要る（--plan は任意）")
    for inp in (args.gt, args.oracle, args.rules, args.plan):
        if inp and _same_file(inp, args.out):
            print("gt_sessions: --out が入力ファイルと同じ（%s）" % inp, file=sys.stderr)
            return 2
    try:
        result = build_sessions(args.gt, args.oracle, args.rules, args.plan)
        data = render(result)
        d = os.path.dirname(os.path.abspath(args.out)) or "."
        os.makedirs(d, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=d, prefix=".gt_sessions_tmp_")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp_path, args.out)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise
    except InputError as e:
        print("gt_sessions: %s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("gt_sessions: 出力できない（%s）" % type(e).__name__, file=sys.stderr)
        return 2
    if not args.plan:
        print("gt_sessions: --plan が無いので oracle_agreement の一致率が出ない", file=sys.stderr)
    allx = result["definitions"]["all"]
    print("gt_sessions: src=%s sessions=%d (commit=%d cancel=%d open_at_end=%d) excluded=%d" % (
        result["src"], len(allx), sum(1 for s in allx if s["outcome"] == "commit"),
        sum(1 for s in allx if s["outcome"] == "cancel"),
        sum(1 for s in allx if s["outcome"] == "open_at_end"), len(result["excluded"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
