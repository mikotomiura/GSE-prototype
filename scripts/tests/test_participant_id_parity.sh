#!/usr/bin/env bash
# 参加者 ID allowlist の logger ⇄ sync スクリプト パリティ回帰テスト。
#
# Part 3 (20260619-sync-auto-participant-id) で sync スクリプトに移植した
# is_valid_pid / GSE_RESERVED_IDS が、logger の is_valid_participant_id
# (src-tauri/src/logger.rs) と挙動一致し続けることを機械的に保証する。
# 4 スクリプト間で手書き重複しているため (D2「完全一致」)、ドリフトを検出する。
#
# 実行方法:
#   bash scripts/tests/test_participant_id_parity.sh
# Exit: 0=全パス / 1=ドリフトまたは不一致
#
# 関連: .steering/20260619-sync-auto-participant-id/decisions.md D2

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOGGER="$REPO_ROOT/src-tauri/src/logger.rs"
SS_SH="$REPO_ROOT/scripts/sync-session.sh"
SA_SH="$REPO_ROOT/scripts/sync-all.sh"

fail=0
note() { echo "  $1"; }
err()  { echo "  FAIL: $1" >&2; fail=1; }

# --- 1. logger の予約名集合と各スクリプトの予約名集合が一致するか ---
# logger.rs: WINDOWS_RESERVED_NAMES: &[&str] = &["CON", "PRN", ...]; を抽出
logger_reserved="$(
    awk '/WINDOWS_RESERVED_NAMES/{f=1} f{print} /\];/{if(f)exit}' "$LOGGER" \
    | grep -oE '"[A-Z0-9]+"' | tr -d '"' | sort -u
)"
# script: GSE_RESERVED_IDS=" CON PRN ... " を抽出 (両 sh は同一実装)
script_reserved="$(
    grep -E '^GSE_RESERVED_IDS=' "$SS_SH" \
    | sed -E 's/^GSE_RESERVED_IDS="//; s/"$//' | tr ' ' '\n' | sed '/^$/d' | sort -u
)"
if [[ "$logger_reserved" == "$script_reserved" ]]; then
    note "reserved-name set matches logger ($(printf '%s' "$logger_reserved" | grep -c .) names)"
else
    err "reserved-name set DRIFT between logger.rs and sync scripts:"
    diff <(printf '%s\n' "$logger_reserved") <(printf '%s\n' "$script_reserved") >&2 || true
fi

# --- 2. is_valid_pid が両 sh で byte-identical か ---
extract_is_valid() { awk '/^is_valid_pid\(\)/{f=1} f{print} f&&/^}/{exit}' "$1"; }
if diff <(extract_is_valid "$SS_SH") <(extract_is_valid "$SA_SH") >/dev/null; then
    note "is_valid_pid identical across sync-session.sh and sync-all.sh"
else
    err "is_valid_pid DIVERGED between sync-session.sh and sync-all.sh"
fi

# --- 3. is_valid_pid の挙動を logger テスト (logger.rs:1719-1772) と同じケースで検証 ---
# sync-session.sh のヘルパー領域だけを source する (本体は実行しない)
helpers="$(mktemp)"
awk '/^set -euo pipefail/{f=1;next} /^SESSION_PATH=""/{f=0} f' "$SS_SH" > "$helpers"
# shellcheck disable=SC1090
source "$helpers"
rm -f "$helpers"

pass=0
check() { # $1=expected(0=valid,1=invalid) $2=id
    if is_valid_pid "$2"; then r=0; else r=1; fi
    if [[ "$r" == "$1" ]]; then pass=$((pass+1)); else err "is_valid_pid([$2]) expected=$1 got=$r"; fi
}
# valid
for v in P000 P003 P123 pilot_01 a-b_C9 CON1 CONSOLE P_CON COM10 Pa3f9c2e1b7d0; do check 0 "$v"; done
# invalid (path injection / 特殊文字 / 長さ / 予約名)
for x in "" "." ".." "../secret" 'a/b' 'a\b' 'P000/../P001' 'P 000' 'P:000' '~' '$HOME'; do check 1 "$x"; done
check 1 $'P000\n'
check 1 "$(printf 'a%.0s' {1..65})"     # 65 chars NG
check 0 "$(printf 'a%.0s' {1..64})"     # 64 chars OK
for r in CON PRN AUX NUL COM1 COM9 LPT1 LPT9 con nul Com5; do check 1 "$r"; done
note "behavioral cases passed: $pass"

if [[ "$fail" -eq 0 ]]; then
    echo "PASS: participant id allowlist parity (logger ⇄ sync scripts)"
    exit 0
else
    echo "FAIL: participant id allowlist parity drift detected" >&2
    exit 1
fi
