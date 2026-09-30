#!/usr/bin/env bash
# issue 004 acceptance — 実行器の核と dry-run・macOS バックエンド
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os macos
E="${K}/emit/emit.py"; M="${K}/emit/backend_macos.py"; KM="${K}/emit/keymap_macos.json"

echo "[004] 実行器の核と macOS バックエンド"
for f in "${E}" "${K}/emit/backend_dryrun.py" "${M}" "${KM}" "${K}/emit/README.md"; do need_file "${f}"; done

# AC1
selftest_ok "${E}"

# 最小の計画（1 ブロック・1 試行・キー 1 つ）
printf '%s\n' '{"kind":"header","format":"plan/1","os":"macos","seed":1,"generator_version":"0","config_sha256":"0000000000000000000000000000000000000000000000000000000000000000"}' \
  '{"kind":"block","block_id":0,"reset_ime":false,"marker":[]}' \
  '{"kind":"trial","trial_id":"t0","block_id":0,"scenario":"S3","speed":"mid","think_ms":200,"phrase_id":"w1-0-0","reading_len":1,"steps":[{"key":"a","at_ms":0,"down":true},{"key":"a","at_ms":60,"down":false}],"intent":{"commit":"enter","cand_index":0,"nav_count":0,"abandon":false,"predictive":false,"ime_toggle_mid":false,"focus_switch_mid":false,"expect_session":true}}' > "${TMP}/plan.jsonl"

# AC2: ⚠️ フラグなしの実バックエンドは exit 2 で、何も送らない
run_exit 2 "AC2 フラグなしの macos バックエンドは exit 2" "${PY}" "${E}" --plan "${TMP}/plan.jsonl" --out "${TMP}/o_real.jsonl" --backend macos
if [ -f "${TMP}/o_real.jsonl" ] && grep -q '"kind":"sent"' "${TMP}/o_real.jsonl"; then ng "AC2 フラグなしなのに sent 行がある"; else ok "AC2 フラグなしで sent 行が 0"; fi

# AC3: dryrun の oracle は通り、壊した oracle は拒否される
run_ok "AC3 dryrun で oracle を出す" "${PY}" "${E}" --plan "${TMP}/plan.jsonl" --out "${TMP}/o.jsonl" --backend dryrun
run_ok "AC3 dryrun の oracle が --validate を通る" "${PY}" "${E}" --validate "${TMP}/o.jsonl"
grep -v '"kind":"trial_end"' "${TMP}/o.jsonl" > "${TMP}/o_bad.jsonl"
run_fail "AC3 trial_end を欠いた oracle を拒否する" "${PY}" "${E}" --validate "${TMP}/o_bad.jsonl"

# ★ 境界の形（SUPPORTED_KEYS / Backend の open・send・close）
for b in backend_dryrun backend_macos; do
  need_grep "${K}/emit/${b}.py" "SUPPORTED_KEYS" "境界: ${b}.py が SUPPORTED_KEYS を持つ"
  for m in "def open" "def send" "def close"; do need_grep "${K}/emit/${b}.py" "${m}" "境界: ${b}.py の ${m}"; done
done
if grep -q 'mouse_click' "${K}/emit/backend_dryrun.py" "${K}/emit/backend_macos.py"; then ng "境界: mouse_click を既定のバックエンドが持っている（issue 026 の範囲）"; else ok "境界: mouse_click は既定のバックエンドに無い"; fi

# AC4: 送らずにフレームワークを読む
run_ok "AC4 backend_macos.py --probe が緑（送出なし）" "${PY}" "${M}" --probe

# AC5: keymap が keyname を網羅する
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
run_ok "AC5 keymap_macos.json が keyname を網羅" "${PY}" "${TMP}/cover.py" "${K}/formats/FORMATS.md" "${KM}"

# ⚠️ selftest が実バックエンドを呼んでいないこと（送出の経路をテストに入れない）
forbid_grep "${E}" 'i-understand-this-sends-keys.*selftest|selftest.*i-understand-this-sends-keys' "GUARD selftest が送出フラグを使っていない"

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/emit/(emit\.py|backend_dryrun\.py|backend_macos\.py|keymap_macos\.json|README\.md)$'
style_ok
finish
