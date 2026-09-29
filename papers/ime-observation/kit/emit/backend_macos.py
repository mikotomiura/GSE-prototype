#!/usr/bin/env python3
# kit: selftest
"""macOS backend: posts synthetic keyboard events through Quartz Event Services (``CGEventPost``).

Synthetic events posted at the HID event tap drive the input method exactly as physical keys do,
so a conversion session opens and closes as it would for a person typing. Events are delivered to
whichever application is in front; the process needs the Accessibility permission, otherwise the
system silently drops them (``open`` therefore refuses to start when the permission is missing).

  backend_macos.py --probe      load the frameworks, create and release one event; nothing is posted
  backend_macos.py --selftest   check the key map and the call sequence against a stub; nothing is posted

The frameworks are loaded lazily, so importing this module on another operating system is harmless
and the self-test reports "not applicable" there.

Backend options (``--backend-opt k=v``):
  focus_app=<bundle id>   application brought to the front by the ``focus_back`` pseudo-key
  away_app=<bundle id>    application brought to the front by ``focus_away`` (default: com.apple.finder)
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APPSERVICES = "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
COREFOUNDATION = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
HID_SYSTEM_STATE = 1      # kCGEventSourceStateHIDSystemState
HID_EVENT_TAP = 0         # kCGHIDEventTap
SHIFT_FLAG = 0x20000      # kCGEventFlagMaskShift
PSEUDO_KEYS = frozenset(["focus_away", "focus_back"])
BUNDLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,127}$")


def _load_keymap():
    with open(os.path.join(HERE, "keymap_macos.json"), encoding="utf-8") as f:
        return json.load(f)


KEYMAP = _load_keymap()
SUPPORTED_KEYS = frozenset(KEYMAP) | PSEUDO_KEYS


class _Api(object):
    """Thin ctypes wrapper over the few Quartz calls that are needed."""

    def __init__(self):
        import ctypes
        self._c = ctypes
        self._app = ctypes.CDLL(APPSERVICES)
        self._cf = ctypes.CDLL(COREFOUNDATION)
        self._app.CGEventSourceCreate.restype = ctypes.c_void_p
        self._app.CGEventSourceCreate.argtypes = [ctypes.c_int32]
        self._app.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
        self._app.CGEventCreateKeyboardEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool]
        self._app.CGEventSetFlags.restype = None
        self._app.CGEventSetFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self._app.CGEventPost.restype = None
        self._app.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        self._app.AXIsProcessTrusted.restype = ctypes.c_bool
        self._app.AXIsProcessTrusted.argtypes = []
        self._cf.CFRelease.restype = None
        self._cf.CFRelease.argtypes = [ctypes.c_void_p]
        self._src = self._app.CGEventSourceCreate(HID_SYSTEM_STATE)
        if not self._src:
            raise RuntimeError("CGEventSourceCreate returned NULL")

    def trusted(self):
        return bool(self._app.AXIsProcessTrusted())

    def make_and_release(self, keycode):
        ev = self._app.CGEventCreateKeyboardEvent(self._src, keycode, True)
        if not ev:
            raise RuntimeError("CGEventCreateKeyboardEvent returned NULL")
        self._cf.CFRelease(ev)

    def post_key(self, keycode, down, flags):
        ev = self._app.CGEventCreateKeyboardEvent(self._src, keycode, bool(down))
        if not ev:
            raise RuntimeError("CGEventCreateKeyboardEvent returned NULL")
        try:
            self._app.CGEventSetFlags(ev, flags)
            self._app.CGEventPost(HID_EVENT_TAP, ev)
        finally:
            self._cf.CFRelease(ev)

    def close(self):
        if self._src:
            self._cf.CFRelease(self._src)
            self._src = None


class Backend(object):
    def __init__(self, opts, api=None):
        unknown = sorted(set(opts) - {"focus_app", "away_app"})
        if unknown:
            raise ValueError("unknown backend option(s) for macos: %s" % ", ".join(unknown))
        self._focus_app = opts.get("focus_app")
        self._away_app = opts.get("away_app", "com.apple.finder")
        for name, value in (("focus_app", self._focus_app), ("away_app", self._away_app)):
            if value is not None and not BUNDLE_ID.match(value):
                raise ValueError("%s is not a bundle identifier" % name)
        self._api = api
        self._flags = 0
        self._held = set()
        self._run = subprocess.run

    def open(self):
        if self._api is None:
            self._api = _Api()
        if not self._api.trusted():
            raise RuntimeError("the Accessibility permission is not granted to this process; "
                               "synthetic keys would be dropped silently")

    def send(self, key, down):
        if key in PSEUDO_KEYS:
            if down:
                self._focus(key)
            return
        if key == "shift":
            self._flags = (self._flags | SHIFT_FLAG) if down else (self._flags & ~SHIFT_FLAG)
        self._api.post_key(KEYMAP[key], down, self._flags)
        if down:
            self._held.add(key)
        else:
            self._held.discard(key)

    def _focus(self, key):
        if key == "focus_away":
            bundle = self._away_app
        else:
            bundle = self._focus_app
            if bundle is None:
                raise RuntimeError("focus_back needs the backend option focus_app=<bundle id>")
        self._run(["osascript", "-e", 'tell application id "%s" to activate' % bundle],
                  check=True, timeout=10)

    def close(self):
        api, self._api = self._api, None
        if api is None:
            return
        try:
            for key in sorted(self._held):
                if key == "shift":
                    self._flags &= ~SHIFT_FLAG
                api.post_key(KEYMAP[key], False, self._flags)
            self._held.clear()
        finally:
            api.close()


def probe():
    if sys.platform != "darwin":
        print("probe: not applicable on this operating system")
        return 0
    api = _Api()
    try:
        api.make_and_release(KEYMAP["a"])
        print("probe: frameworks loaded, one event created and released, nothing posted")
        print("probe: accessibility permission %s" % ("granted" if api.trusted() else "not granted"))
    finally:
        api.close()
    return 0


class _StubApi(object):
    def __init__(self, trusted=True):
        self.calls = []
        self._trusted = trusted
        self.closed = 0

    def trusted(self):
        return self._trusted

    def post_key(self, keycode, down, flags):
        self.calls.append((keycode, bool(down), flags))

    def close(self):
        self.closed += 1


def selftest():
    if sys.platform != "darwin":
        print("selftest: not applicable on this operating system")
        return 0
    failures = []

    def check(name, cond):
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            failures.append(name)

    values = list(KEYMAP.values())
    check("key map values are distinct integer key codes",
          all(isinstance(v, int) and 0 <= v < 128 for v in values) and len(set(values)) == len(values))
    check("key map has the input-method keys", KEYMAP.get("ime_on") == 104 and KEYMAP.get("ime_off") == 102)

    stub = _StubApi()
    b = Backend({}, api=stub)
    b.open()
    b.send("a", True)
    b.send("a", False)
    check("a plain key is posted as a press then a release", stub.calls == [(0, True, 0), (0, False, 0)])
    stub.calls[:] = []
    b.send("shift", True)
    b.send("a", True)
    b.send("a", False)
    b.send("shift", False)
    check("the shift flag is set while shift is held and cleared after",
          [c[2] for c in stub.calls] == [SHIFT_FLAG, SHIFT_FLAG, SHIFT_FLAG, 0])

    stub = _StubApi()
    b = Backend({}, api=stub)
    b.open()
    b.send("shift", True)
    b.close()
    check("close releases a key that is still held and releases the source",
          stub.calls[-1] == (KEYMAP["shift"], False, 0) and stub.closed == 1)

    ran = []
    b = Backend({"focus_app": "com.example.editor"}, api=_StubApi())
    b._run = lambda cmd, **kw: ran.append(cmd)
    b.send("focus_away", True)
    b.send("focus_away", False)
    b.send("focus_back", True)
    check("focus pseudo-keys activate an application on press only",
          len(ran) == 2 and "com.apple.finder" in ran[0][2] and "com.example.editor" in ran[1][2])

    b = Backend({}, api=_StubApi())
    try:
        b.send("focus_back", True)
        check("focus_back without focus_app is refused", False)
    except RuntimeError:
        check("focus_back without focus_app is refused", True)
    for bad in ({"nope": "1"}, {"focus_app": 'x" & (do shell script "y") & "'}):
        try:
            Backend(bad)
            check("bad option is refused: %s" % sorted(bad), False)
        except ValueError:
            check("bad option is refused: %s" % sorted(bad), True)
    b = Backend({}, api=_StubApi(trusted=False))
    try:
        b.open()
        check("open refuses when the Accessibility permission is missing", False)
    except RuntimeError:
        check("open refuses when the Accessibility permission is missing", True)
    return 1 if failures else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--probe"]:
        return probe()
    if argv == ["--selftest"]:
        return selftest()
    print("usage: backend_macos.py --probe | --selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
