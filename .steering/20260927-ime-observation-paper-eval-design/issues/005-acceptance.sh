#!/usr/bin/env bash
# issue 005 acceptance — 実行器の Windows バックエンド
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os windows
E="${K}/emit/emit.py"; W="${K}/emit/backend_windows.py"; KM="${K}/emit/keymap_windows.json"

echo "[005] 実行器の Windows バックエンド"
need_file "${W}"; need_file "${KM}"

# AC1 / AC2 / AC5
selftest_ok "${W}"
run_ok "AC2 backend_windows.py --probe が緑（送出なし）" "${PY}" "${W}" --probe
run_ok "AC5 核の emit.py --selftest が緑" "${PY}" "${E}" --selftest

# AC3: ⚠️ フラグなしでは送らない
printf '%s\n' '{"kind":"header","format":"plan/1","os":"windows","seed":1,"generator_version":"0","config_sha256":"0000000000000000000000000000000000000000000000000000000000000000"}' \
  '{"kind":"block","block_id":0,"reset_ime":false,"marker":[]}' \
  '{"kind":"trial","trial_id":"t0","block_id":0,"scenario":"S3","speed":"mid","think_ms":200,"phrase_id":"w1-0-0","reading_len":1,"steps":[{"key":"a","at_ms":0,"down":true},{"key":"a","at_ms":60,"down":false}],"intent":{"commit":"enter","cand_index":0,"nav_count":0,"abandon":false,"predictive":false,"ime_toggle_mid":false,"focus_switch_mid":false,"expect_session":true}}' > "${TMP}/plan.jsonl"
run_exit 2 "AC3 フラグなしの windows バックエンドは exit 2" "${PY}" "${E}" --plan "${TMP}/plan.jsonl" --out "${TMP}/o_real.jsonl" --backend windows
if [ -f "${TMP}/o_real.jsonl" ] && grep -q '"kind":"sent"' "${TMP}/o_real.jsonl"; then ng "AC3 フラグなしなのに sent 行がある"; else ok "AC3 フラグなしで sent 行が 0"; fi

# ★ 境界の形（issue 004 が固定した形）
need_grep "${W}" "SUPPORTED_KEYS" "境界: SUPPORTED_KEYS を持つ"
for m in "def open" "def send" "def close"; do need_grep "${W}" "${m}" "境界: ${m}"; done
need_grep "${W}" "timeBeginPeriod" "境界: open で timeBeginPeriod"
need_grep "${W}" "timeEndPeriod" "境界: close で timeEndPeriod"

# AC4
cat > "${TMP}/cover.py" <<'EOF2'
import json, sys
km = json.load(open(sys.argv[2], encoding="utf-8"))
# ★ 契約（issue 001 の keyname の列挙）を直接持つ。FORMATS.md の書式に依存しない（空振りの緑を防ぐ）。
names = [chr(c) for c in range(ord("a"), ord("z") + 1)] + [str(d) for d in range(10)] + ["f%d" % n for n in range(13, 20)]
names += ["space","enter","esc","backspace","tab","left","right","up","down","minus","comma","period","ime_on","ime_off","shift"]
fm = open(sys.argv[1], encoding="utf-8").read()
for n in ["mouse_click", "focus_away", "focus_back", "ime_on", "ime_off", "f13", "f19"]:
    if n not in fm:
        print("FORMATS.md に keyname が無い:", n); sys.exit(1)
missing = sorted(n for n in names if n not in km)
print("missing:", missing, "checked:", len(names))
sys.exit(1 if missing else 0)
EOF2
run_ok "AC4 keymap_windows.json が keyname を網羅" "${PY}" "${TMP}/cover.py" "${K}/formats/FORMATS.md" "${KM}"

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/emit/(backend_windows\.py|keymap_windows\.json)$'
finish
