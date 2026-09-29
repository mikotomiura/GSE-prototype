#!/usr/bin/env python3
# kit: selftest
"""Windows backend: posts synthetic keyboard events through ``user32!SendInput``.

Character keys are sent as hardware scan codes (``KEYEVENTF_SCANCODE``), so the input method sees the same
event stream as a physical keyboard. Arrow keys are extended keys (``KEYEVENTF_EXTENDEDKEY``). The two
input-method keys and the function keys F13-F19 have no reliable scan code and are sent as virtual keys;
``ime_on`` and ``ime_off`` are ``VK_IME_ON`` (0x16) and ``VK_IME_OFF`` (0x1A), and whether a given input method
honours them has to be confirmed in a pilot before the key map is relied upon. Events go to whichever window
has the keyboard focus; a process cannot inject into a window of a higher integrity level (UIPI).

  backend_windows.py --probe      load user32 and winmm, build one INPUT record; nothing is sent
  backend_windows.py --selftest   check the key map, the structure layout and the call sequence against a
                                  stub; nothing is sent

The libraries are loaded lazily, so importing this module on another operating system is harmless and the
self-test reports "not applicable" there.

Timer resolution: the default system timer tick is 15.6 ms, which is coarser than the inter-key intervals of
a plan. ``open`` therefore requests a 1 ms resolution with ``winmm!timeBeginPeriod(1)`` and ``close``
restores it with ``timeEndPeriod(1)``; the driver calls ``close`` in a ``finally`` block.

Backend options (``--backend-opt k=v``):
  focus_window=<title>   top-level window brought to the front by the ``focus_back`` pseudo-key
  away_window=<title>    top-level window brought to the front by ``focus_away``

The window is looked up by its exact title (``FindWindowW``), so the same plan moves to the same window on
every run. Both options have no default: a plan that uses a pseudo-key is refused before anything is sent
unless the option it needs is given. After every activation the backend reads the foreground window back
and stops the run when it is not the requested one, so that later keys are never sent to the wrong window.
"""
import ctypes
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
INPUT_KEYBOARD = 1
TIMER_PERIOD_MS = 1
PSEUDO_KEYS = frozenset(["focus_away", "focus_back"])
KEY_OPTIONS = {"focus_away": "away_window", "focus_back": "focus_window"}
FRONT_CHECKS = 5          # how many times the foreground window is read back after an activation
FRONT_WAIT_S = 0.2        # pause between two readings
MAX_TITLE = 256


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16), ("dwFlags", ctypes.c_uint32),
                ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_int32), ("dy", ctypes.c_int32), ("mouseData", ctypes.c_uint32),
                ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_uint32), ("wParamL", ctypes.c_uint16), ("wParamH", ctypes.c_uint16)]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_uint32), ("u", _INPUT_UNION)]


def _load_keymap():
    with open(os.path.join(HERE, "keymap_windows.json"), encoding="utf-8") as f:
        return json.load(f)


KEYMAP = _load_keymap()
SUPPORTED_KEYS = frozenset(KEYMAP) | PSEUDO_KEYS


def make_input(key, down):
    """Build the INPUT record for one press or release of ``key`` (a name in the key map)."""
    entry = KEYMAP[key]
    flags = 0 if down else KEYEVENTF_KEYUP
    vk = scan = 0
    if "scan" in entry:
        scan = entry["scan"]
        flags |= KEYEVENTF_SCANCODE
        if entry.get("ext"):
            flags |= KEYEVENTF_EXTENDEDKEY
    else:
        vk = entry["vk"]
    rec = INPUT()
    rec.type = INPUT_KEYBOARD
    rec.ki.wVk = vk
    rec.ki.wScan = scan
    rec.ki.dwFlags = flags
    return rec


class _Api(object):
    """Thin ctypes wrapper over the few user32 / winmm calls that are needed."""

    def __init__(self):
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._winmm = ctypes.WinDLL("winmm", use_last_error=True)
        self._user32.SendInput.restype = ctypes.c_uint
        self._user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
        self._user32.FindWindowW.restype = ctypes.c_void_p
        self._user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        self._user32.SetForegroundWindow.restype = ctypes.c_int
        self._user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
        self._user32.GetForegroundWindow.restype = ctypes.c_void_p
        self._user32.GetForegroundWindow.argtypes = []
        self._winmm.timeBeginPeriod.restype = ctypes.c_uint
        self._winmm.timeBeginPeriod.argtypes = [ctypes.c_uint]
        self._winmm.timeEndPeriod.restype = ctypes.c_uint
        self._winmm.timeEndPeriod.argtypes = [ctypes.c_uint]

    def send_input(self, rec):
        return self._user32.SendInput(1, ctypes.byref(rec), ctypes.sizeof(INPUT))

    def time_begin(self, ms):
        return self._winmm.timeBeginPeriod(ms)

    def time_end(self, ms):
        return self._winmm.timeEndPeriod(ms)

    def find_window(self, title):
        return self._user32.FindWindowW(None, title)

    def set_foreground(self, hwnd):
        return self._user32.SetForegroundWindow(hwnd)

    def foreground(self):
        return self._user32.GetForegroundWindow()


class Backend(object):
    def __init__(self, opts, api=None):
        unknown = sorted(set(opts) - {"focus_window", "away_window"})
        if unknown:
            raise ValueError("unknown backend option(s) for windows: %s" % ", ".join(unknown))
        self._focus_window = opts.get("focus_window")
        self._away_window = opts.get("away_window")
        for name, value in (("focus_window", self._focus_window), ("away_window", self._away_window)):
            if value is not None and (not value or len(value) > MAX_TITLE
                                      or any(ord(ch) < 32 for ch in value)):
                raise ValueError("%s is not a usable window title" % name)
        self._api = api
        self._timer = False
        self._held = set()
        self._sleep = time.sleep

    def open(self):
        if self._api is None:
            self._api = _Api()
        if self._api.time_begin(TIMER_PERIOD_MS) != 0:
            raise RuntimeError("timeBeginPeriod(%d) was refused" % TIMER_PERIOD_MS)
        self._timer = True

    def _post(self, key, down):
        sent = self._api.send_input(make_input(key, down))
        if sent != 1:
            raise RuntimeError("SendInput accepted %d of 1 events (blocked by another desktop or a "
                               "higher-integrity window?)" % sent)

    def send(self, key, down):
        if key in PSEUDO_KEYS:
            if down:
                self._focus(key)
            return
        if down:
            self._held.add(key)      # recorded before sending, so that close releases it even if the send fails
        self._post(key, down)
        if not down:
            self._held.discard(key)

    def _focus(self, key):
        title = self._away_window if key == "focus_away" else self._focus_window
        if title is None:
            raise RuntimeError("%s needs the backend option %s=<window title>" % (key, KEY_OPTIONS[key]))
        hwnd = self._api.find_window(title)
        if not hwnd:
            raise RuntimeError("no top-level window has the title given for %s" % key)
        self._api.set_foreground(hwnd)
        for i in range(FRONT_CHECKS):
            if i:
                self._sleep(FRONT_WAIT_S)
            if self._api.foreground() == hwnd:
                return
        raise RuntimeError("the foreground window is not the one requested by %s; "
                           "stopping before any further key is sent" % key)

    def close(self):
        api, self._api = self._api, None
        if api is None:
            return
        first = None
        try:
            for key in sorted(self._held):
                try:
                    if api.send_input(make_input(key, False)) != 1:
                        raise RuntimeError("SendInput did not accept the release of %s" % key)
                except Exception as e:      # every held key gets its release attempt
                    if first is None:
                        first = e
            self._held.clear()
        finally:
            if self._timer:
                self._timer = False
                api.time_end(TIMER_PERIOD_MS)
        if first is not None:
            raise first


def probe():
    if sys.platform != "win32":
        print("probe: not applicable on this operating system")
        return 0
    _Api()
    rec = make_input("a", True)
    print("probe: user32 and winmm loaded, one INPUT record built (%d bytes), nothing sent" % ctypes.sizeof(rec))
    return 0


class _StubApi(object):
    def __init__(self, accept=1, timer_result=0):
        self.sent = []
        self.timer = []
        self._accept = accept
        self._timer_result = timer_result
        self.windows = {}
        self.front = None

    def send_input(self, rec):
        self.sent.append((rec.ki.wVk, rec.ki.wScan, rec.ki.dwFlags))
        return self._accept

    def time_begin(self, ms):
        self.timer.append(("begin", ms))
        return self._timer_result

    def time_end(self, ms):
        self.timer.append(("end", ms))
        return 0

    def find_window(self, title):
        return self.windows.get(title)

    def set_foreground(self, hwnd):
        self.front = hwnd
        return 1

    def foreground(self):
        return self.front


def selftest():
    if sys.platform != "win32":
        print("selftest: not applicable on this operating system")
        return 0
    failures = []

    def check(name, cond):
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            failures.append(name)

    check("key map covers every plain key name", set(KEYMAP) == SUPPORTED_KEYS - PSEUDO_KEYS)
    check("every entry has a scan code or a virtual key, not both",
          all((("scan" in v) != ("vk" in v)) and set(v) <= {"scan", "vk", "ext"} for v in KEYMAP.values()))
    scans = [v["scan"] for v in KEYMAP.values() if "scan" in v]
    check("scan codes are distinct bytes", all(0 < s < 128 for s in scans) and
          len(set((v["scan"], bool(v.get("ext"))) for v in KEYMAP.values() if "scan" in v)) == len(scans))
    check("the input-method keys are the virtual keys 0x16 and 0x1A",
          KEYMAP.get("ime_on") == {"vk": 0x16} and KEYMAP.get("ime_off") == {"vk": 0x1A})
    check("arrow keys are extended keys", all(KEYMAP[k].get("ext") for k in ("left", "right", "up", "down")))
    expected = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28
    check("INPUT has the size the operating system expects (%d)" % expected, ctypes.sizeof(INPUT) == expected)

    press, release = make_input("a", True), make_input("a", False)
    check("a character key is a scan-code press then a keyup",
          (press.ki.wVk, press.ki.wScan, press.ki.dwFlags) == (0, 30, KEYEVENTF_SCANCODE)
          and release.ki.dwFlags == KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP and press.type == INPUT_KEYBOARD)
    up = make_input("up", True)
    check("an arrow key carries the extended flag", up.ki.dwFlags == KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY)
    ime = make_input("ime_on", True)
    check("a virtual key is sent without the scan-code flag", (ime.ki.wVk, ime.ki.wScan, ime.ki.dwFlags) == (0x16, 0, 0))

    stub = _StubApi()
    b = Backend({}, api=stub)
    b.open()
    b.send("a", True)
    b.send("a", False)
    b.close()
    check("open and close pair the timer request", stub.timer == [("begin", 1), ("end", 1)])
    check("a key is sent as a press then a release", len(stub.sent) == 2 and stub.sent[0][2] == KEYEVENTF_SCANCODE)

    stub = _StubApi()
    b = Backend({}, api=stub)
    b.open()
    b.send("shift", True)
    b.close()
    check("close releases a key that is still held",
          stub.sent[-1] == (0, KEYMAP["shift"]["scan"], KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP))

    stub = _StubApi(accept=0)
    b = Backend({}, api=stub)
    b.open()
    try:
        b.send("a", True)
        check("a send that SendInput does not accept raises", False)
    except RuntimeError:
        check("a send that SendInput does not accept raises", True)
    try:
        b.close()
    except RuntimeError:
        pass
    check("the timer request is undone even when the release fails", stub.timer == [("begin", 1), ("end", 1)])

    stub = _StubApi(timer_result=97)
    b = Backend({}, api=stub)
    try:
        b.open()
        check("a refused timer request stops the run", False)
    except RuntimeError:
        check("a refused timer request stops the run", True)
    b.close()
    check("close after a refused timer request does not end a period that was never begun",
          stub.timer == [("begin", 1)])

    stub = _StubApi()
    stub.windows = {"Editor": 11, "Other": 22}
    b = Backend({"focus_window": "Editor", "away_window": "Other"}, api=stub)
    b._sleep = lambda s: None
    b.send("focus_away", True)
    b.send("focus_away", False)
    check("focus_away activates the named window on press only", stub.front == 22)
    b.send("focus_back", True)
    check("focus_back activates the named window", stub.front == 11)

    class _Stuck(_StubApi):
        def set_foreground(self, hwnd):
            return 0

    stuck = _Stuck()
    stuck.windows = {"Other": 22}
    stuck.front = 5
    sleeps = []
    b = Backend({"away_window": "Other"}, api=stuck)
    b._sleep = sleeps.append
    try:
        b.send("focus_away", True)
        check("a foreground window that differs after activation stops the run", False)
    except RuntimeError:
        check("a foreground window that differs after activation stops the run", len(sleeps) == FRONT_CHECKS - 1)

    b = Backend({"away_window": "Missing"}, api=_StubApi())
    try:
        b.send("focus_away", True)
        check("a window title that matches nothing is refused", False)
    except RuntimeError:
        check("a window title that matches nothing is refused", True)
    for pseudo in ("focus_away", "focus_back"):
        try:
            Backend({}, api=_StubApi()).send(pseudo, True)
            check("%s without its option is refused" % pseudo, False)
        except RuntimeError:
            check("%s without its option is refused" % pseudo, True)
    check("the pseudo-keys declare the option each one needs",
          KEY_OPTIONS == {"focus_away": "away_window", "focus_back": "focus_window"})
    for bad in ({"nope": "1"}, {"focus_window": ""}, {"away_window": "a\nb"}, {"focus_window": "x" * (MAX_TITLE + 1)}):
        try:
            Backend(bad)
            check("bad option is refused: %s" % sorted(bad), False)
        except ValueError:
            check("bad option is refused: %s" % sorted(bad), True)
    return 1 if failures else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--probe"]:
        return probe()
    if argv == ["--selftest"]:
        return selftest()
    print("usage: backend_windows.py --probe | --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
