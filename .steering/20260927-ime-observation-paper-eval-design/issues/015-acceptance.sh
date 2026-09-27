#!/usr/bin/env bash
# issue 015 acceptance — 較正パイロットの道具（ImeShadow を見ない）
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
P="${K}/pilot"

echo "[015] 較正パイロットの道具"
for f in call_types clock_sync reach seal_obs; do selftest_ok "${P}/${f}.py"; done
need_file "${P}/README.md"
need_grep "${P}/clock_sync.py" "既知のずれとドリフトを回復" "AC4 selftest ケース: 既知のずれとドリフトを回復"
need_grep "${P}/reach.py" "key 行を半分消すと 50%" "AC5 selftest ケース: key 行を半分消すと 50%（陽性対照）"

# AC2: ⚠️ ImeShadow を読まない
for f in call_types clock_sync reach; do forbid_grep "${P}/${f}.py" 'ime_shadow|dwell_ms' "AC2 ${f}.py が ImeShadow に触れない"; done
cat > "${TMP}/cnt.py" <<'EOF'
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
if "# --- selftest begin ---" not in src or "# --- selftest end ---" not in src:
    print("selftest の区間の目印が無い"); sys.exit(1)
src = re.sub(r"# --- selftest begin ---.*?# --- selftest end ---", "", src, flags=re.S)
src = re.sub(r'""".*?"""', "", src, flags=re.S)
lines = [l.split("#")[0] for l in src.splitlines()]
hits = [l for l in lines if "ime_shadow" in l]
print("ime_shadow を含むコード行:", len(hits))
sys.exit(0 if len(hits) <= 1 else 1)
EOF
run_ok "AC2 seal_obs.py の ime_shadow は捨てる規則の 1 行以下" "${PY}" "${TMP}/cnt.py" "${P}/seal_obs.py"

# AC3: ⚠️ 封印が情報を漏らさない
printf '%s\n' '{"type":"meta","format":"obs/1","os":"macos","logger_version":"0.1.0","manifest_sha256":"0000000000000000000000000000000000000000000000000000000000000000","capabilities":{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}' \
  '{"type":"key","t":10,"category":"alphabetic","press":true}' \
  '{"type":"ime_shadow","t":20,"dwell_ms":987654,"nav":1,"abandon":false}' \
  '{"type":"key","t":30,"category":"space","press":true}' \
  '{"type":"ime_shadow","t":40,"dwell_ms":987655,"nav":0,"abandon":true}' \
  '{"type":"ime_shadow","t":50,"dwell_ms":987656,"nav":2,"abandon":false}' > "${TMP}/obs.jsonl"
SHA="$("${PY}" -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${TMP}/obs.jsonl")"
if "${PY}" "${P}/seal_obs.py" --obs "${TMP}/obs.jsonl" --keys-out "${TMP}/keys.jsonl" --sealed-dir "${TMP}/sealed" > "${TMP}/stdout.txt" 2>&1; then
  ok "AC3 seal_obs.py が緑"
else ng "AC3 seal_obs.py が赤（$(tail -n 2 "${TMP}/stdout.txt" | tr '\n' ' ')）"; fi
if [ -f "${TMP}/keys.jsonl" ] && ! grep -q 'ime_shadow' "${TMP}/keys.jsonl" && [ "$(grep -c '"type":"key"' "${TMP}/keys.jsonl")" = "2" ]; then ok "AC3 keys-out は key 2 行だけ"; else ng "AC3 keys-out の中身が違う"; fi
if grep -qE 'ime_shadow|98765[456]' "${TMP}/stdout.txt"; then ng "AC3 標準出力に ImeShadow 由来の情報がある"; else ok "AC3 標準出力に ImeShadow 由来の情報が無い"; fi
SEAL="$(find "${TMP}" -name seal.json | head -n 1)"
if [ -n "${SEAL}" ] && ! grep -qE 'ime_shadow|98765[456]' "${SEAL}" && grep -q "${SHA}" "${SEAL}"; then ok "AC3 seal.json は SHA-256 を持ち、ImeShadow 由来の情報が無い"; else ng "AC3 seal.json が無い・SHA-256 が違う・情報が漏れている"; fi
if [ ! -f "${TMP}/obs.jsonl" ] && [ -n "$(ls "${TMP}/sealed" 2>/dev/null)" ]; then ok "AC3 元のファイルが sealed へ移った"; else ng "AC3 元のファイルが sealed へ移っていない"; fi

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/pilot/(call_types|clock_sync|reach|seal_obs)\.py$|^papers/ime-observation/kit/pilot/README\.md$'
finish
