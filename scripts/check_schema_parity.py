#!/usr/bin/env python3
"""Verify JSON-semantic parity between gse-prototype's and gse-dataset's
`schema/current.json`.

Invoked as pre-flight by scripts/sync-all.ps1 / sync-all.sh. Fails fast
(before any file copy or gse-replay run) if the two schemas disagree,
printing a unified diff and a repair command hint.

The check is **semantic**, not byte-equal: line-ending and key-ordering
differences are ignored so Windows `core.autocrlf` does not produce
false positives. If you need byte-level integrity, see `schema drift
CI check` inside the prototype repo (separate concern).

Exit codes:
    0 = schemas are semantically equal
    1 = drift detected (both files present, content differs)
    2 = src-tauri/schema/current.json not found
    3 = <dataset>/schema/current.json not found
    4 = invalid arguments / I/O error

Usage:
    python scripts/check_schema_parity.py --dataset C:/gse-dataset
    python scripts/check_schema_parity.py \
        --src-tauri-schema <path> \
        --dataset-schema <path>
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROTO_SCHEMA = REPO_ROOT / "src-tauri" / "schema" / "current.json"

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_PROTO_MISSING = 2
EXIT_DATASET_MISSING = 3
EXIT_USAGE = 4

DIFF_CLIP_LINES = 30


def _load_normalized(path: Path) -> tuple[object, str]:
    """Load JSON and return (parsed, canonical-string) where canonical-string
    is the pretty-printed form used only for unified-diff output.

    Uses `utf-8-sig` encoding so UTF-8 BOM-prefixed files (Windows Notepad
    default save format) parse cleanly instead of erroring on \ufeff.
    """
    with open(path, encoding="utf-8-sig") as f:
        parsed = json.load(f)
    # Canonical pretty form for diff readability and stable ordering.
    canonical = json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
    return parsed, canonical


def _collect_type_enums(schema: object) -> set[str]:
    """Walk a JSON Schema document and collect all string values appearing
    under a `type` property's `enum` or `const`. This matches the
    tagged-union discriminators used by schema_dto.rs' `#[serde(tag="type")]`
    output (enum) and by single-variant `#[serde(tag="type", content=...)]`
    shapes that schemars emits as `const`.

    Uses an explicit stack to avoid Python's default 1000-frame recursion
    limit blowing up on pathologically deep schemas (defensive; current
    GSE schema is ~320 lines).
    """
    found: set[str] = set()
    stack: list[object] = [schema]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict):
                type_prop = props.get("type")
                if isinstance(type_prop, dict):
                    enum_vals = type_prop.get("enum")
                    if isinstance(enum_vals, list):
                        for v in enum_vals:
                            if isinstance(v, str):
                                found.add(v)
                    const_val = type_prop.get("const")
                    if isinstance(const_val, str):
                        found.add(const_val)
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return found


def _diff_clip(a_canonical: str, b_canonical: str, a_name: str, b_name: str) -> str:
    lines = list(
        difflib.unified_diff(
            a_canonical.splitlines(keepends=False),
            b_canonical.splitlines(keepends=False),
            fromfile=a_name,
            tofile=b_name,
            lineterm="",
        )
    )
    if len(lines) > DIFF_CLIP_LINES:
        clipped = lines[:DIFF_CLIP_LINES]
        clipped.append(f"... ({len(lines) - DIFF_CLIP_LINES} more diff lines elided)")
        lines = clipped
    return "\n".join(lines)


def _report_drift(proto_path: Path, dataset_path: Path,
                  proto_json: object, dataset_json: object,
                  proto_canon: str, dataset_canon: str) -> None:
    proto_variants = _collect_type_enums(proto_json)
    dataset_variants = _collect_type_enums(dataset_json)
    missing_in_b = sorted(proto_variants - dataset_variants)
    extra_in_b = sorted(dataset_variants - proto_variants)

    print("[check_schema_parity] DRIFT detected between:")
    print(f"  A: {proto_path}")
    print(f"  B: {dataset_path}")
    print()
    print(f"Missing variants in B: {', '.join(missing_in_b) if missing_in_b else '(none)'}")
    print(f"Extra variants in B:   {', '.join(extra_in_b) if extra_in_b else '(none)'}")
    print()
    print(f"First differences (unified diff, first {DIFF_CLIP_LINES} lines):")
    diff = _diff_clip(proto_canon, dataset_canon, proto_path.as_posix(), dataset_path.as_posix())
    if diff:
        print(diff)
    else:
        print("  (diff produced no line-level output — see variant summary above)")
    print()
    print("To fix (typical case: B is stale after schema_dto.rs update):")
    print("  cd src-tauri && cargo run --bin emit_schema > schema/current.json")
    print(f"  cp src-tauri/schema/current.json {dataset_path}")
    print("  (then commit both sides)")


def _emit_machine_status(rc: int, enabled: bool) -> None:
    # 必ず stdout に出す理由: PowerShell 5.1 -File invocation + [CmdletBinding()]
    # 下では stderr が ErrorRecord に変換されて `2>&1` でも pipe に乗らない事象あり
    # (sync-all.ps1 の Step 0 実測 2026-04-17)。stdout ならいずれの invocation path
    # でも確実に parent shell が取得できる。
    if enabled:
        print(f"HELPER_EXITCODE={rc}")


def _make_stdio_encoding_safe() -> None:
    """Windows の cp932 コンソールで **drift の中身を出す前に落ちる**のを防ぐ。

    ⚠️★★★ 2026-09-11 に実測した不具合:
    `schema/current.json` の `description` には日本語の全角ダッシュ (U+2014 `—`) が
    入っており、cp932 の stdout へ `print(diff)` した瞬間に `UnicodeEncodeError` で
    **トレースバックだけ出して終わる**。

    → ⚠️ 本スクリプトの唯一の仕事である「**何がどう drift したか**」と
    「**どう直すか**」が **1 行も表示されない**。★ しかも `sync-all` の pre-flight
    なので、操作者はここで止まったまま次に何をすべきか分からない。

    ⚠️ 終了コードは Python の例外でも 1 になるため fail-closed 自体は保たれていた
    (= 壊れたまま同期は進まない)。★ 直すのは**報告の可読性**である。

    `errors="replace"` にしてあるのは、⚠️ **表示できない文字があっても
    報告を止めない**ため (差分の中身より「止まらないこと」が優先)。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            # ⚠️ 差し替えられた stdout (テストの StringIO 等) には無い。★ 何もしない。
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            # ⚠️ 再設定できない環境でも**本処理は続ける** (報告が化けるだけ)。
            pass


def main(argv: list[str] | None = None) -> int:
    _make_stdio_encoding_safe()
    parser = argparse.ArgumentParser(
        description="Verify schema parity between gse-prototype and gse-dataset.",
    )
    parser.add_argument(
        "--dataset",
        help=(
            "Path to the gse-dataset repo root. "
            "Resolves to <dataset>/schema/current.json. "
            "Takes precedence over --dataset-schema when both are given."
        ),
    )
    parser.add_argument(
        "--src-tauri-schema",
        default=str(DEFAULT_PROTO_SCHEMA),
        help=f"Path to prototype schema JSON (default: {DEFAULT_PROTO_SCHEMA})",
    )
    parser.add_argument(
        "--dataset-schema",
        help="Path to dataset schema JSON (overridden by --dataset if given)",
    )
    parser.add_argument(
        "--machine-readable",
        action="store_true",
        help=(
            "Print an unambiguous final line 'HELPER_EXITCODE=<n>' to stdout. "
            "Shell wrappers on PS 5.1 parse this because $LASTEXITCODE is "
            "unreliable via Git Bash -> powershell.exe -File invocation path. "
            "Emitted to stdout (not stderr) because PS [CmdletBinding()] scripts "
            "intercept stderr into ErrorRecords and 2>&1 cannot recover it."
        ),
    )
    args = parser.parse_args(argv)

    proto_path = Path(args.src_tauri_schema)
    if args.dataset:
        dataset_path = Path(args.dataset) / "schema" / "current.json"
    elif args.dataset_schema:
        dataset_path = Path(args.dataset_schema)
    else:
        print(
            "[check_schema_parity] ERROR: specify --dataset or --dataset-schema",
            file=sys.stderr,
        )
        return EXIT_USAGE

    if not proto_path.exists():
        print(f"[check_schema_parity] FAIL: prototype schema not found: {proto_path}", file=sys.stderr)
        print("  run: cd src-tauri && cargo run --bin emit_schema > schema/current.json", file=sys.stderr)
        _emit_machine_status(EXIT_PROTO_MISSING, args.machine_readable)
        return EXIT_PROTO_MISSING

    if not dataset_path.exists():
        print(f"[check_schema_parity] FAIL: dataset schema not found: {dataset_path}", file=sys.stderr)
        print(f"  run: cp {proto_path} {dataset_path}", file=sys.stderr)
        _emit_machine_status(EXIT_DATASET_MISSING, args.machine_readable)
        return EXIT_DATASET_MISSING

    # Separate JSON parse errors from other I/O issues so reviewers can tell
    # "schema file is corrupt" from "file missing" / "permissions" at a glance.
    try:
        proto_json, proto_canon = _load_normalized(proto_path)
    except json.JSONDecodeError as e:
        print(f"[check_schema_parity] ERROR: cannot parse {proto_path}: {e}", file=sys.stderr)
        _emit_machine_status(EXIT_USAGE, args.machine_readable)
        return EXIT_USAGE
    except OSError as e:
        print(f"[check_schema_parity] ERROR: I/O on {proto_path}: {e}", file=sys.stderr)
        _emit_machine_status(EXIT_USAGE, args.machine_readable)
        return EXIT_USAGE
    try:
        dataset_json, dataset_canon = _load_normalized(dataset_path)
    except json.JSONDecodeError as e:
        print(f"[check_schema_parity] ERROR: cannot parse {dataset_path}: {e}", file=sys.stderr)
        _emit_machine_status(EXIT_USAGE, args.machine_readable)
        return EXIT_USAGE
    except OSError as e:
        print(f"[check_schema_parity] ERROR: I/O on {dataset_path}: {e}", file=sys.stderr)
        _emit_machine_status(EXIT_USAGE, args.machine_readable)
        return EXIT_USAGE

    if proto_json == dataset_json:
        print(f"[check_schema_parity] OK: schemas in sync ({len(proto_canon)} bytes canonical)")
        _emit_machine_status(EXIT_OK, args.machine_readable)
        return EXIT_OK

    _report_drift(proto_path, dataset_path, proto_json, dataset_json, proto_canon, dataset_canon)
    _emit_machine_status(EXIT_DRIFT, args.machine_readable)
    return EXIT_DRIFT


if __name__ == "__main__":
    sys.exit(main())
