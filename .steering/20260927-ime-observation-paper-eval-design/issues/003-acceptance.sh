#!/usr/bin/env bash
# issue 003 acceptance — シナリオ生成器
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
G="${K}/gen/generate_plan.py"; R="${K}/gen/romaji.py"; J="${K}/gen/recipes.json"

echo "[003] シナリオ生成器"
need_file "${G}"; need_file "${R}"; need_file "${J}"; need_file "${K}/gen/README.md"

# AC1 / AC2
selftest_ok "${R}"
selftest_ok "${G}"
run_ok "recipes.json が JSON として読める" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "${J}"

# AC3
need_grep "${G}" "同じ seed でバイト一致" "AC3 selftest ケース: 同じ seed でバイト一致"
need_grep "${G}" "seed を変えると順が変わる" "AC3 selftest ケース: seed を変えると順が変わる（陰性対照）"

# 小さな設定とコーパスをここで作る
cat > "${TMP}/cfg.json" <<'EOF'
{"n_per_cell_scenario_speed": 2, "block_size": 4, "scenarios": ["S1","S3"],
 "speeds": {"slow": {"iki_median_ms": 300, "iki_sigma": 0.3}, "mid": {"iki_median_ms": 200, "iki_sigma": 0.3}, "fast": {"iki_median_ms": 120, "iki_sigma": 0.3}},
 "key_hold_ms": 60, "think_ms": {"min": 200, "max": 2000}, "cand_index_max": 3, "nav_count_max": 3,
 "inter_trial_ms": 1000, "marker": ["f13","f14","f13"], "marker_gap_ms": 150, "reset_ime_every_block": true}
EOF
printf '%s\n' '{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}' \
  '{"kind":"phrase","phrase_id":"w1-0-0","work_id":"w1","text":"青空","reading":"あおぞら","reading_len":4}' \
  '{"kind":"phrase","phrase_id":"w1-0-1","work_id":"w1","text":"日本","reading":"にほん","reading_len":3}' \
  '{"kind":"phrase","phrase_id":"w1-1-0","work_id":"w1","text":"学校","reading":"がっこう","reading_len":4}' > "${TMP}/corpus.jsonl"

# AC4: 正しい計画を通し（陽性対照）、1 か所ずつ壊した計画を拒否する（変異）
run_ok "AC4 CLI で計画を作る" "${PY}" "${G}" --corpus "${TMP}/corpus.jsonl" --recipes "${J}" --config "${TMP}/cfg.json" --os macos --seed 3 --out "${TMP}/plan.jsonl"
run_ok "AC4 正しい計画を --validate が通す（陽性対照）" "${PY}" "${G}" --validate "${TMP}/plan.jsonl"
cat > "${TMP}/mut.py" <<'EOF'
import json, sys
src, kind, out = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
done = False
for r in rows:
    if done: break
    if kind == "keyname" and r.get("kind") == "trial":
        r["steps"][0]["key"] = "hyper"; done = True
    elif kind == "back" and r.get("kind") == "trial" and len(r["steps"]) >= 2:
        r["steps"][0]["at_ms"] = r["steps"][-1]["at_ms"] + 1000; done = True
    elif kind == "speed" and r.get("kind") == "trial":
        r["speed"] = {"slow": "fast", "mid": "slow", "fast": "mid"}[r["speed"]]; done = True
if not done: print("変異を入れられなかった:", kind); sys.exit(2)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
EOF
for k in keyname back speed; do
  if "${PY}" "${TMP}/mut.py" "${TMP}/plan.jsonl" "${k}" "${TMP}/m_${k}.jsonl" >/dev/null 2>&1; then
    run_fail "AC4 変異（${k}）を入れた計画を拒否する" "${PY}" "${G}" --validate "${TMP}/m_${k}.jsonl"
  else ng "AC4 変異（${k}）を入れられない（計画が無い・形が違う）"; fi
done

# AC5: 見積もり（最後の行が正の数 1 つだけ）
if "${PY}" "${G}" --estimate --config "${TMP}/cfg.json" --recipes "${J}" --os macos > "${TMP}/est.out" 2>&1 \
   && tail -n 1 "${TMP}/est.out" | grep -Eq '^[0-9]+(\.[0-9]+)?$' && [ "$(tail -n 1 "${TMP}/est.out" | tr -d '0.')" != "" ]; then
  ok "AC5 --estimate の最後の行が正の数"
else ng "AC5 --estimate が失敗、または最後の行が数 1 つでない（$(tail -n 2 "${TMP}/est.out" | tr '\n' ' ')）"; fi

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/gen/(generate_plan\.py|romaji\.py|recipes\.json|README\.md)$'
finish
