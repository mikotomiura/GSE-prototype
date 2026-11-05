"""DUX と SWELL-KW を、本文を含まない GSE の NDJSON と打鍵の外の時刻に変換する（extend/conditions.md E3）。

出力の NDJSON は meta / session_start / key 行（時刻・category・press）だけ。
打鍵の外は {"clicks": [...], "moves": [...] or None, "focus": [...] or None} の時刻だけ。
キーの名前・文字・欄の値・ウィンドウの題名は書き出さない。

  python3 -I convert_extend.py --selftest
"""
import calendar
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

HMM_VERSION = "0.5.0"
DWELL = 100
SENTENCE_PUNCT = set(".,")
PUNCT = set(";:'\"!?-_=+()[]{}<>/\\|`~@#$%^&*")

csv.field_size_limit(1 << 30)


def char_category(c):
    """CoAuthor の convert.py の char_category と同じ。"""
    if c.isalpha():
        return "alphabetic"
    if c.isdigit():
        return "numeric"
    if c == " ":
        return "space"
    if c == "\n":
        return "enter"
    if c == "\t":
        return "tab"
    if c in SENTENCE_PUNCT:
        return "sentence_punctuation"
    if c in PUNCT:
        return "punctuation"
    return "other"


# ---------- DUX ----------

DUX_PUNCT = {"SEMICOLON", "QUOTE", "SLASH", "BACK_SLASH", "OPEN_BRACKET", "CLOSE_BRACKET", "EQUALS", "MINUS"}
DUX_MOD = {"SHIFT", "CONTROL", "ALT", "ALT_GRAPH", "META", "CAPS_LOCK"}
DUX_NAV = {"LEFT", "RIGHT", "UP", "DOWN", "HOME", "END", "PAGE_UP", "PAGE_DOWN"}
DUX_CLICK = {"MouseButtonDown", "Scroll"}


def dux_category(key, tab_as_nav=False):
    if key.startswith("LETTER_") or key == "ANONYMIZED":
        return "alphabetic"
    if key.startswith("DIGIT_") or key.startswith("NUMPAD_"):
        return "numeric"
    if key == "SPACE":
        return "space"
    if key == "ENTER":
        return "enter"
    if key == "TAB":
        return "navigation" if tab_as_nav else "tab"
    if key == "BACK_SPACE":
        return "backspace"
    if key == "DELETE":
        return "delete"
    if key in ("PERIOD", "COMMA"):
        return "sentence_punctuation"
    if key in DUX_PUNCT or key.startswith("DEAD_"):
        return "punctuation"
    if key in DUX_MOD:
        return "modifier"
    if key in DUX_NAV:
        return "navigation"
    if key == "ESCAPE":
        return "escape"
    if re.fullmatch(r"F([1-9]|1[0-9]|2[0-4])", key):
        return "function"
    return "other"


def truthy(v):
    v = v.strip().lower()
    if v not in ("true", "false", ""):
        raise ValueError("unexpected flag value")
    return v == "true"


def dux_read(paths, hold):
    """{(版, session): [(t, type, key, repeat, ctrl, alt, meta), ...]}（取っておく session は識別子で振り分けて捨てる）。"""
    if len(paths) != 2:
        raise ValueError("DUX は v0 と v1 の 2 本")
    out, held_rows = {}, 0
    for ver, p in zip(("v0", "v1"), paths):
        with open(p, newline="", encoding="utf-8") as f:
            r = csv.reader(f, delimiter="\t")
            head = next(r)
            ix = {c: head.index(c) for c in ("session", "timestamp", "type", "key", "repeat", "control", "alt", "meta")}
            for n, row in enumerate(r):
                sid = "%s:%s" % (ver, row[ix["session"]])
                if sid in hold:
                    held_rows += 1
                    continue
                try:
                    t = int(row[ix["timestamp"]])
                except ValueError:
                    raise ValueError("timestamp column") from None
                out.setdefault(sid, []).append((t, n, row[ix["type"]], row[ix["key"]],
                                                row[ix["repeat"]], row[ix["control"]], row[ix["alt"]], row[ix["meta"]]))
    return out, held_rows


def dux_session(rows, tab_as_nav=False):
    """1 session の行 → (keys [(t_down, t_up, category)], side, stats)。"""
    rows = same_ms_order(sorted(rows, key=lambda x: (x[0], x[1])))
    st = {"presses": 0, "repeat_excluded": 0, "anonymized": 0, "other": 0, "modified_to_other": 0,
          "release_paired": 0, "release_synth": 0, "release_orphan": 0}
    presses, opened = [], {}
    clicks, moves = [], []
    for t, _, typ, key, rep, ctl, alt, meta in rows:
        if typ == "KeyPressed":
            if truthy(rep):
                st["repeat_excluded"] += 1
                continue
            cat = dux_category(key, tab_as_nav)
            if cat not in ("modifier", "backspace", "delete") and (truthy(ctl) or truthy(alt) or truthy(meta)):
                cat = "other"
                st["modified_to_other"] += 1
            if key == "ANONYMIZED":
                st["anonymized"] += 1
            if cat == "other":
                st["other"] += 1
            presses.append([t, None, cat])
            opened[key] = len(presses) - 1
        elif typ == "KeyReleased":
            i = opened.pop(key, None)
            if i is None:
                st["release_orphan"] += 1
            else:
                presses[i][1] = max(t, presses[i][0])
                st["release_paired"] += 1
        elif typ in DUX_CLICK:
            clicks.append(t)
        elif typ == "MouseMovement":
            moves.append(t)
    keys = synth_releases(presses, st)
    st["presses"] = len(keys)
    return keys, {"clicks": clicks, "moves": moves, "focus": None}, st


def same_ms_order(rows):
    """同じ ms の中で、(1) すでに開いている押下を閉じる離し (2) 押下 (3) 残りの離し、の順に並べ替える。
    同じキーの「離し → 再押下」は前の押下を閉じ、「押下 → 離し」は同じ ms の押下と対になる。"""
    out, i, opened = [], 0, set()
    while i < len(rows):
        j = i
        while j < len(rows) and rows[j][0] == rows[i][0]:
            j += 1
        grp = rows[i:j]
        first = [r for r in grp if r[2] == "KeyReleased" and r[3] in opened]
        press = [r for r in grp if r[2] == "KeyPressed"]
        rest = [r for r in grp if r not in first and r not in press]
        for r in first:
            opened.discard(r[3])
        for r in press:
            opened.add(r[3])
        for r in rest:
            if r[2] == "KeyReleased":
                opened.discard(r[3])
        out.extend(first + press + rest)
        i = j
    return out


def synth_releases(presses, st):
    """離しが無い押下に、押下 + DWELL と次の押下の 1 ms 前の早いほうを入れる（押下より前にしない）。"""
    presses = sorted(presses, key=lambda p: p[0])
    out = []
    for i, (t, up, cat) in enumerate(presses):
        if up is None:
            up = t + DWELL
            if i + 1 < len(presses):
                up = min(up, max(t, presses[i + 1][0] - 1))
            st["release_synth"] = st.get("release_synth", 0) + 1
        out.append((t, up, cat))
    return out


# ---------- SWELL-KW ----------

SW_SPECIAL = {"Space": "space", "Return": "enter", "Enter": "enter", "Tab": "tab", "Backspace": "backspace",
              "Delete": "delete", "Left arrow": "navigation", "Right arrow": "navigation", "Up arrow": "navigation",
              "Down arrow": "navigation", "Home": "navigation", "End": "navigation", "PageUp": "navigation",
              "PageDown": "navigation", "Escape": "escape"}
SW_CLICK = {"clicked", "doubleclicked", "dragged", "wheel turned"}
TS_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?Z$")


def ts_ms(s):
    m = TS_RE.match(s.strip())
    if not m:
        raise ValueError("timestamp format")
    y, mo, d, h, mi, se, frac = m.groups()
    sec = calendar.timegm((int(y), int(mo), int(d), int(h), int(mi), int(se), 0, 0, 0))
    ms = int((frac or "0")[:3].ljust(3, "0"))
    return sec * 1000 + ms


def sw_special(v, allow_char=False):
    if v in SW_SPECIAL:
        return SW_SPECIAL[v]
    if re.fullmatch(r"NumPad[0-9]", v):
        return "numeric"
    if re.fullmatch(r"F([1-9]|1[0-9]|2[0-4])", v):
        return "function"
    if allow_char and len(v) == 1:
        return char_category(v)
    return "other"


def sw_category(action, value):
    if action == "character":
        return char_category(value) if len(value) == 1 else "other"
    if action == "special key":
        return sw_special(value)
    if action == "key combination":
        parts = [p.strip() for p in value.split(" + ")]
        mods, last = parts[:-1], parts[-1]
        if mods and set(mods) == {"Shift"}:
            return sw_special(last, allow_char=True)
        if last in ("Backspace", "Delete") and ({"Ctrl", "Alt"} & set(mods)):
            return SW_SPECIAL[last]
        return "other"
    raise ValueError("keyboard action")


def swell_file(path):
    """1 ファイル → (keys, side, stats)。読むのは EventType・EventAction・TimeStamp・KeyboardValue だけ。"""
    st = {"presses": 0, "other": 0, "focus": 0, "clicks": 0, "subsecond_presses": 0}
    presses, clicks, focus = [], [], []
    n = 0
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag != "Event":
            continue
        typ, act = el.findtext("EventType"), el.findtext("EventAction")
        raw_ts = el.findtext("TimeStamp")
        if raw_ts is None:  # 末尾で切れた出来事（notes の逸脱）
            st["no_timestamp"] = st.get("no_timestamp", 0) + 1
            el.clear()
            continue
        t = ts_ms(raw_ts)
        if typ == "Keyboard":
            cat = sw_category(act, el.findtext("KeyboardValue") or "")
            if cat == "other":
                st["other"] += 1
            presses.append([t, None, cat, n])
        elif typ == "Mouse" and act in SW_CLICK:
            clicks.append(t)
        elif typ == "Other" and act == "Window Activated":
            focus.append(t)
        n += 1
        el.clear()
    presses.sort(key=lambda p: (p[0], p[3]))
    keys = synth_releases([p[:3] for p in presses], st)
    st["presses"] = len(keys)
    st["subsecond_presses"] = sum(1 for k in keys if k[0] % 1000)
    st["focus"], st["clicks"] = len(focus), len(clicks)
    return keys, {"clicks": sorted(clicks), "moves": None, "focus": sorted(focus)}, st


# ---------- 書き出し ----------

def write_ndjson(keys, dst):
    rows = []
    for td, tu, cat in keys:
        rows.append((td, 0, {"type": "key", "t": td, "category": cat, "press": True}))
        rows.append((tu, 1, {"type": "key", "t": tu, "category": cat, "press": False}))
    rows.sort(key=lambda r: (r[0], r[1]))
    t0 = keys[0][0]
    with open(dst, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "session_start": t0, "hmm_version": HMM_VERSION}) + "\n")
        f.write(json.dumps({"type": "session_start", "t": t0}) + "\n")
        for _, _, r in rows:
            f.write(json.dumps(r) + "\n")


# ---------- 自己検査（陽性対照つき） ----------

def selftest():
    import os
    import tempfile
    canary = "ZQXCANARYVALUE"
    with tempfile.TemporaryDirectory() as td:
        # DUX: 本文の列に秘密の文字列を入れた偽の入力
        cols = ["session", "timestamp", "type", "target", "alt", "control", "shift", "meta", "key", "repeat", "button",
                "x", "y", "xPosition", "yPosition", "selectedValue", "enteredText"]
        def row(s, t, typ, key="", rep="False", ctl="False", alt="False", meta="False"):
            d = dict.fromkeys(cols, "")
            d.update(session=s, timestamp=str(t), type=typ, key=key, repeat=rep, control=ctl, alt=alt, meta=meta,
                     target=canary, selectedValue=canary, enteredText=canary)
            return [d[c] for c in cols]
        rows0 = [row("1", 1000, "KeyPressed", "LETTER_A"), row("1", 1050, "KeyReleased", "LETTER_A"),
                 row("1", 1100, "KeyPressed", "LETTER_B"), row("1", 1150, "KeyPressed", "LETTER_B", rep="True"),
                 row("1", 1200, "KeyPressed", "LETTER_C", ctl="True"),
                 row("1", 1200, "KeyPressed", "BACK_SPACE", ctl="True"),
                 row("1", 1300, "MouseButtonDown"), row("1", 1310, "MouseClick"), row("1", 1400, "MouseMovement"),
                 row("1", 1500, "KeyPressed", "TAB"), row("1", 1600, "KeyReleased", "LETTER_Z"),
                 row("1", 1700, "KeyReleased", "LETTER_Q"), row("1", 1700, "KeyPressed", "LETTER_Q"),
                 row("1", 1800, "KeyPressed", "LETTER_W"), row("1", 1850, "KeyPressed", "LETTER_W"),
                 row("1", 1900, "KeyReleased", "LETTER_W"),
                 row("1", 2000, "KeyPressed", "LETTER_E"), row("1", 2100, "KeyPressed", "LETTER_E"),
                 row("1", 2100, "KeyReleased", "LETTER_E"), row("1", 2150, "KeyReleased", "LETTER_E"),
                 row("2", 5000, "KeyPressed", "LETTER_A")]
        p0, p1 = os.path.join(td, "v0.csv"), os.path.join(td, "v1.csv")
        for p, rs in ((p0, rows0), (p1, [row("1", 9000, "KeyPressed", "LETTER_A")])):
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter="\t")
                w.writerow(cols)
                w.writerows(rs)
        sess, held = dux_read([p0, p1], hold={"v0:2"})
        assert set(sess) == {"v0:1", "v1:1"} and held == 1, (set(sess), held)
        try:
            dux_read([p0], hold=set())
            raise AssertionError("1 本で通った")
        except ValueError:
            pass
        keys, side, st = dux_session(sess["v0:1"])
        cats = [k[2] for k in keys]
        assert cats == ["alphabetic", "alphabetic", "other", "backspace", "tab", "alphabetic", "alphabetic",
                        "alphabetic", "alphabetic", "alphabetic"], cats
        # 同じ ms の「離し → 再押下」: 離しは前の押下を閉じ、再押下は後の離しと対になる（Codex の指摘）
        assert keys[8][1] == 2100 and keys[9][1] == 2150, keys[8:]
        assert keys[5][1] == 1700  # 同じ ms の離しは押下と対になる
        assert keys[6][1] == 1849 and keys[7][1] == 1900  # 離さずに 2 回押す: 前の押下は合成・後の押下が対
        assert st["release_synth"] == 5 and st["release_paired"] == 5 and st["release_orphan"] == 1, st
        assert st["repeat_excluded"] == 1 and st["modified_to_other"] == 1 and st["release_orphan"] == 1
        assert keys[0][1] == 1050  # 対になった離し
        assert keys[2][1] == 1200 and keys[3][1] == 1300  # 同じ ms の次の押下 → 離しは押下と同じ時刻
        assert side["clicks"] == [1300] and side["moves"] == [1400] and side["focus"] is None
        k2, _, _ = dux_session(sess["v0:1"], tab_as_nav=True)
        assert k2[4][2] == "navigation"
        nd = os.path.join(td, "d.ndjson")
        write_ndjson(keys, nd)
        blob = open(nd, encoding="utf-8").read() + json.dumps(side)
        assert canary not in blob and "LETTER" not in blob
        # 陽性対照: 検査が秘密の文字列を見つけられること
        assert canary in open(p0, encoding="utf-8").read()
        # SWELL-KW: 題名・URL・文字に秘密の文字列を入れた偽の入力
        xml = f"""<?xml version="1.0" encoding="utf-8"?><Log>
<Event><EventType>Other</EventType><EventAction>Window Activated</EventAction><TimeStamp>2012-10-08T11:10:02.3649796Z</TimeStamp><EventDescription>{canary}</EventDescription><Control><ControlWindowText>{canary}</ControlWindowText></Control></Event>
<Event><EventType>Keyboard</EventType><EventAction>character</EventAction><TimeStamp>2012-10-08T11:10:03.0001Z</TimeStamp><KeyboardValue>Z</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>special key</EventAction><TimeStamp>2012-10-08T11:10:03.0009Z</TimeStamp><KeyboardValue>Backspace</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>key combination</EventAction><TimeStamp>2012-10-08T11:10:04.5Z</TimeStamp><KeyboardValue>Shift + Left arrow</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>key combination</EventAction><TimeStamp>2012-10-08T11:10:05Z</TimeStamp><KeyboardValue>Alt + Tab</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>key combination</EventAction><TimeStamp>2012-10-08T11:10:06Z</TimeStamp><KeyboardValue>Ctrl + Backspace</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>special key</EventAction><TimeStamp>2012-10-08T11:10:06.5Z</TimeStamp><KeyboardValue>Q</KeyboardValue></Event>
<Event><EventType>Keyboard</EventType><EventAction>key combination</EventAction><TimeStamp>2012-10-08T11:10:06.7Z</TimeStamp><KeyboardValue>Win + Backspace</KeyboardValue></Event>
<Event><EventType>Mouse</EventType><EventAction>clicked</EventAction><TimeStamp>2012-10-08T11:10:07Z</TimeStamp></Event>
<Event><EventType>Other</EventType><EventAction>Keyboa</EventAction></Event>
<Event><EventType>Other</EventType><EventAction>Browser URL changed</EventAction><TimeStamp>2012-10-08T11:10:08Z</TimeStamp><CustomEventProperties><CustomName>Browser URL</CustomName><CustomValue>{canary}</CustomValue></CustomEventProperties></Event>
</Log>"""
        px = os.path.join(td, "a.xml")
        open(px, "w", encoding="utf-8").write(xml)
        keys, side, st = swell_file(px)
        base = calendar.timegm((2012, 10, 8, 11, 10, 0, 0, 0, 0)) * 1000
        assert [k[0] - base for k in keys] == [3000, 3000, 4500, 5000, 6000, 6500, 6700], [k[0] - base for k in keys]
        assert [k[2] for k in keys] == ["alphabetic", "backspace", "navigation", "other", "backspace", "other", "other"]
        assert keys[0][1] == keys[0][0]  # 同じ ms の次の押下
        assert st["no_timestamp"] == 1
        assert side["focus"] == [base + 2364] and side["clicks"] == [base + 7000] and side["moves"] is None
        nd2 = os.path.join(td, "s.ndjson")
        write_ndjson(keys, nd2)
        blob = open(nd2, encoding="utf-8").read() + json.dumps(side)
        assert canary not in blob and '"Z"' not in blob
        assert canary in open(px, encoding="utf-8").read()
    print("convert_extend selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
