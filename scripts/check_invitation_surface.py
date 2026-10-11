#!/usr/bin/env python3
"""ADR-026 M11: the four failure conditions of the invitation surface, as executable checks.

The checks are static (source text). They exist because ADR-026 requires that the first code of the
invitation surface ships together with the checks that can fail on it (M11), and because a check
that has nothing to look at passes silently (`verify-before-claiming` rule 5b). Each check therefore
also asserts that the thing it inspects is present.

Failure conditions (ADR-026 Migration M11, `.steering/20261011-portrait-eh3-impl/design.md` 3.4):
  1. The invitation surface shows text or a quantity (A20 / ADR-025 D1). The glyph has no text node
     and no interpolated value; the settings window shows no quantity about the person (count,
     remaining, total, streak) and no controlling wording (I-4).
  2. Code calls an API that detects screen sharing or recording (A19 / data-privacy rule 7).
  3. The surface can be empty while the invitation is present (PC-12): the overlay must render the
     glyph when the state says present, the state command must read the state machine, and the
     state machine must have the test that it presents when everything allows it.
  4. Unresolved citations: delegated to scripts/check_citations.py (run separately in CI); here we
     only assert that the script exists.

Usage:
  python scripts/check_invitation_surface.py            # check the repository
  python scripts/check_invitation_surface.py --selftest # the checks fail on planted violations

Exit codes: 0 = all conditions hold, 1 = a condition failed, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

GLYPH = Path("src/components/InvitationGlyph.tsx")
SETTINGS = Path("src/components/InvitationSettings.tsx")
OVERLAY = Path("src/components/Overlay.tsx")
LIB = Path("src-tauri/src/lib.rs")
MACHINE = Path("src-tauri/src/analysis/invitation.rs")
CITATIONS = Path("scripts/check_citations.py")

# Condition 2: APIs that enumerate or detect capture sessions (Windows Graphics Capture, macOS
# ScreenCaptureKit / window lists, browser display capture). EnumWindows is NOT listed: the IME
# detector uses it for its own candidate window and it does not detect capture.
CAPTURE_DETECTION_APIS = (
    "GraphicsCaptureSession",
    "GraphicsCaptureItem",
    "IGraphicsCaptureItemInterop",
    "CGWindowListCopyWindowInfo",
    "CGWindowListCreateImage",
    "CGPreflightScreenCaptureAccess",
    "SCShareableContent",
    "SCStream",
    "getDisplayMedia",
)

# Condition 1 (settings window): quantities about the person (ADR-025 D1: count, remaining,
# total, streak, elapsed) and controlling wording (I-4). System setting values ("1 日 2 回まで")
# are allowed (ADR-035 D6).
PERSON_QUANTITY_WORDS = ("回目", "残り", "あと", "累計", "これまで", "今日は", "連続", "日続", "合計")
CONTROLLING_WORDS = ("ください", "すべき", "しましょう", "必ず", "しなければ")

JSX_TEXT = re.compile(r">([^<>{}]*)<")
COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.S)
COMMENT_LINE = re.compile(r"(^|[^:])//[^\n]*")
JSX_COMMENT = re.compile(r"\{/\*.*?\*/\}", re.S)


def strip_comments(src: str) -> str:
    src = JSX_COMMENT.sub("", src)
    src = COMMENT_BLOCK.sub("", src)
    return COMMENT_LINE.sub(r"\1", src)


def read(root: Path, rel: Path) -> str | None:
    p = root / rel
    return p.read_text(encoding="utf-8") if p.is_file() else None


# Interpolations allowed inside the glyph's JSX: numeric literals, the fixed colour/size constants, the
# shape table lookup, and the one prop. Anything else (a count, a time, a prop that varies per
# presentation) fails: an allow-list, so a new variable name cannot slip through.
GLYPH_ALLOWED_EXPR = re.compile(
    r"^(-?\d+(\.\d+)?|STROKE|FILL|GLYPH_SIZE_PX|paths\[variant\]|variant|\(\{[^{}]*\}\)\s*=>.*)$"
)


def check_glyph(root: Path) -> list[str]:
    src = read(root, GLYPH)
    if src is None:
        return [f"1: {GLYPH} is missing (nothing to check)"]
    code = strip_comments(src)
    problems = []
    if "<svg" not in code:
        problems.append(f"1: {GLYPH} has no <svg> (nothing to check)")
    # the whole file, not only the part after <svg>: the shape table sits before it
    for tag in ("<text", "<tspan", "<foreignObject", "<title", "<desc"):
        if tag in code:
            problems.append(f"1: {GLYPH} uses {tag}> (text in the drawing)")
    for m in JSX_TEXT.finditer(code):
        t = m.group(1).strip()
        # TypeScript generics and comparisons also produce ">...<"; only flag runs that look like words
        if t and re.search(r"[0-9A-Za-z\u3040-\u30ff\u4e00-\u9fff]", t) and not re.search(r"[;=(){},:.|]", t):
            problems.append(f"1: {GLYPH} has a text node: {t!r}")
    # attribute values ={...} and JSX children {...} (after a tag or after another child expression)
    for m in re.finditer(r"=\{([^{}]*)\}", code):
        expr = m.group(1).strip()
        if expr and not GLYPH_ALLOWED_EXPR.match(expr):
            problems.append(f"1: {GLYPH} interpolates a value: {{{expr}}}")
    # a value drawn as a child (`<g>{x}</g>`) may only be the fixed shape table
    for m in re.finditer(r"(?<=[>}])\s*\{([^{}]*)\}", code):
        expr = m.group(1).strip()
        if expr and expr != "paths[variant]":
            problems.append(f"1: {GLYPH} draws a value as a child: {{{expr}}}")
    props = re.search(r"interface\s+InvitationGlyphProps\s*\{([^}]*)\}", code)
    if not props:
        problems.append(f"1: {GLYPH} has no InvitationGlyphProps (nothing to check)")
    else:
        fields = [f.strip() for f in props.group(1).replace("\n", ";").split(";") if f.strip()]
        if fields != ["variant: GlyphVariant"]:
            problems.append(f"1: {GLYPH} props must be only `variant: GlyphVariant`, got {fields}")
    return problems


def check_overlay_glyph_block(root: Path) -> list[str]:
    src = read(root, OVERLAY)
    if src is None:
        return [f"3: {OVERLAY} is missing"]
    code = strip_comments(src)
    i = code.find('className="invitation-glyph"')
    if i < 0:
        return [f"3: {OVERLAY} has no invitation-glyph element"]
    j = code.find("</button>", i)
    block = code[i : j + 1]  # keep the "<" of </button> so a trailing text node is seen
    problems = []
    # the button's children must be exactly the glyph element
    k = block.find(">")
    children = re.sub(r"\s+", " ", block[k + 1 : -1]).strip() if k >= 0 else ""
    if children != "<InvitationGlyph variant={INVITATION_GLYPH} />":
        problems.append(f"1: the invitation glyph button in {OVERLAY} must contain only the glyph, got {children!r}")
    return problems


def check_settings(root: Path) -> list[str]:
    src = read(root, SETTINGS)
    if src is None:
        return [f"1: {SETTINGS} is missing (nothing to check)"]
    code = strip_comments(src)
    problems = []
    for w in PERSON_QUANTITY_WORDS:
        if w in code:
            problems.append(f"1: {SETTINGS} shows a quantity about the person: {w!r}")
    for w in CONTROLLING_WORDS:
        if w in code:
            problems.append(f"1: {SETTINGS} uses controlling wording: {w!r}")
    invoked = set(re.findall(r'invoke(?:<[^>]*>)?\(\s*"([a-z_]+)"', code))
    extra = invoked - {"get_invitation_settings", "set_invitation_settings"}
    if extra:
        problems.append(f"1: {SETTINGS} reads something other than the settings: {sorted(extra)}")
    if not invoked:
        problems.append(f"1: {SETTINGS} invokes nothing (nothing to check)")
    return problems


def check_capture_detection(root: Path) -> list[str]:
    problems = []
    scanned = 0
    for base in ("src-tauri/src", "src"):
        d = root / base
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.suffix not in (".rs", ".ts", ".tsx", ".swift", ".m", ".mm"):
                continue
            scanned += 1
            code = strip_comments(p.read_text(encoding="utf-8", errors="replace"))
            for api in CAPTURE_DETECTION_APIS:
                if api in code:
                    problems.append(f"2: {p.relative_to(root)} calls {api}")
    if scanned == 0:
        problems.append("2: no source files were scanned (nothing to check)")
    # the Windows Graphics Capture namespace pulled in as a crate feature
    cargo = root / "src-tauri" / "Cargo.toml"
    if cargo.is_file() and "Graphics_Capture" in cargo.read_text(encoding="utf-8"):
        problems.append("2: src-tauri/Cargo.toml enables a Graphics_Capture feature")
    return problems


def check_present_is_drawn(root: Path) -> list[str]:
    problems = []
    overlay = strip_comments(read(root, OVERLAY) or "")
    guard = re.search(r"\{\s*invitationPresent\s*&&(.*?)<InvitationGlyph", overlay, re.S)
    if guard and re.search(r"\b(false|0|null|undefined)\b|!\s*(true|1)\b", guard.group(1)):
        problems.append(f"3: {OVERLAY} guards the glyph with a constant that is never true")
    if not re.search(r"invitationPresent\s*&&[^;]*<InvitationGlyph", overlay, re.S):
        problems.append(f"3: {OVERLAY} does not render <InvitationGlyph> when invitationPresent")
    # the window must be shown (not left 1x1 off screen) while the invitation is present
    if not re.search(r"const visible = [^;]*invitationPresent", overlay):
        problems.append(f"3: {OVERLAY} does not show the overlay window while invitationPresent")
    if 'invoke<boolean>("get_invitation_state")' not in overlay:
        problems.append(f"3: {OVERLAY} does not read get_invitation_state")
    lib = read(root, LIB) or ""
    m = re.search(r"fn get_invitation_state\(\)[^{]*\{(.*?)\n\}", lib, re.S)
    if not m or "INVITATION_PRESENT.load" not in m.group(1):
        problems.append(f"3: {LIB} get_invitation_state does not read INVITATION_PRESENT")
    if "INVITATION_PRESENT.store(out.present" not in lib:
        problems.append(f"3: {LIB} does not store the state machine's output in INVITATION_PRESENT")
    settings = strip_comments(read(root, SETTINGS) or "")
    if "variant={INVITATION_GLYPH}" not in settings:
        problems.append(f"3: {SETTINGS} does not show the same glyph as the overlay (INVITATION_GLYPH)")
    machine = strip_comments(read(root, MACHINE) or "")
    if not re.search(r"fn presents_when_everything_allows_it\(\)\s*\{[^}]*assert(_eq|_ne)?!\(", machine):
        problems.append(f"3: {MACHINE} lacks the test that it presents when everything allows it")
    return problems


def check_citations_delegated(root: Path) -> list[str]:
    return [] if (root / CITATIONS).is_file() else [f"4: {CITATIONS} is missing"]


def run_checks(root: Path) -> list[str]:
    return (
        check_glyph(root)
        + check_overlay_glyph_block(root)
        + check_settings(root)
        + check_capture_detection(root)
        + check_present_is_drawn(root)
        + check_citations_delegated(root)
    )


def _copy_tree(dst: Path) -> None:
    for rel in (GLYPH, SETTINGS, OVERLAY, LIB, MACHINE, CITATIONS, Path("src-tauri/Cargo.toml")):
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst / rel)


def _mutate(root: Path, rel: Path, old: str, new: str) -> None:
    p = root / rel
    s = p.read_text(encoding="utf-8")
    assert old in s, f"selftest anchor not found in {rel}: {old!r}"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as td:
        clean = Path(td) / "clean"
        _copy_tree(clean)
        base = run_checks(clean)
        if base:
            failures.append(f"the clean copy fails: {base}")

    mutations = [
        ("1: text in glyph", GLYPH, "{paths[variant]}", "{paths[variant]}<text>休憩</text>", "1:"),
        ("1: count in glyph", GLYPH, "{paths[variant]}", "{paths[variant]}{count}", "1:"),
        ("1: text in the shape table", GLYPH, "<rect x={11}", "<text>x</text><rect x={11}", "1:"),
        ("1: a varying value", GLYPH, "r={19}", "r={props.size}", "1:"),
        ("1: an extra prop", GLYPH, "    variant: GlyphVariant;", "    variant: GlyphVariant;\n    count: number;", "1:"),
        ("1: interpolation in glyph button", OVERLAY, "<InvitationGlyph variant={INVITATION_GLYPH} />",
         "<InvitationGlyph variant={INVITATION_GLYPH} />{count}", "1:"),
        ("1: text in glyph button", OVERLAY, "<InvitationGlyph variant={INVITATION_GLYPH} />",
         "<InvitationGlyph variant={INVITATION_GLYPH} />休憩", "1:"),
        ("1: person quantity", SETTINGS, "この印について", "この印について（今日はあと 1 回）", "1:"),
        ("1: controlling wording", SETTINGS, "応じても応じなくてもかまいません。", "席を立ってください。", "1:"),
        ("1: reads a count", SETTINGS, 'invoke<InvitationSettingsValue>("get_invitation_settings")',
         'invoke<InvitationSettingsValue>("get_invitation_count")', "1:"),
        ("2: capture feature", Path("src-tauri/Cargo.toml"), '"Win32_Foundation",', '"Win32_Foundation",\n    "Graphics_Capture",', "2:"),
        ("2: capture detection", LIB, "fn get_invitation_state() -> bool {",
         "fn get_invitation_state() -> bool {\n    let _ = \"GraphicsCaptureSession\";", "2:"),
        ("3: overlay no longer draws", OVERLAY, "<InvitationGlyph variant={INVITATION_GLYPH} />", "<span />", "3:"),
        ("1: digits in glyph", GLYPH, "{paths[variant]}", "{paths[variant]}<g>123</g>", "1:"),
        ("1: number drawn as child", GLYPH, "{paths[variant]}", "{paths[variant]}<g>{123}</g>", "1:"),
        ("3: constant false guard", OVERLAY, "{invitationPresent && !probeActive", "{invitationPresent && false && !probeActive", "3:"),
        ("3: settings shows another glyph", SETTINGS, "variant={INVITATION_GLYPH}", 'variant="steps"', "3:"),
        ("3: PC-12 test with only a comment", MACHINE, "fn presents_when_everything_allows_it() {",
         "fn presents_when_everything_allows_it() { // assert\n    }\n    fn _old() {", "3:"),
        ("3: negated true guard", OVERLAY, "{invitationPresent && !probeActive", "{invitationPresent && !true && !probeActive", "3:"),
        ("3: empty PC-12 test", MACHINE, "fn presents_when_everything_allows_it() {", "fn presents_when_everything_allows_it() {}\n    fn _old() {", "3:"),
        ("3: window not shown", OVERLAY, "const visible = probeActive || nudgeVisible || invitationPresent;",
         "const visible = probeActive || nudgeVisible;", "3:"),
        ("3: state not stored", LIB, "INVITATION_PRESENT.store(out.present", "INVITATION_PRESENT.store(false", "3:"),
        ("3: PC-12 test removed", MACHINE, "fn presents_when_everything_allows_it", "fn renamed_away", "3:"),
        ("4: citation checker removed", CITATIONS, None, None, "4:"),
    ]
    for name, rel, old, new, prefix in mutations:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _copy_tree(root)
            if old is None:
                (root / rel).unlink()
            else:
                _mutate(root, rel, old, new)
            got = run_checks(root)
            if not any(g.startswith(prefix) for g in got):
                failures.append(f"positive control did not fail: {name} (got {got})")
    if failures:
        for f in failures:
            print("SELFTEST FAIL:", f)
        return 1
    print(f"selftest ok: clean copy passes, {len(mutations)} planted violations each fail")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    problems = run_checks(REPO)
    if problems:
        for p in problems:
            print("FAIL", p)
        return 1
    print("invitation surface: the four ADR-026 M11 failure conditions hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
