#!/usr/bin/env bash
# issue 001 acceptance — 論文ディレクトリの境界・ログ形式の契約・content-free 検査器・検証の入口
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
V="${K}/formats/validate_logs.py"

echo "[001] 境界・形式の契約・content-free 検査器・検証の入口"
for f in papers/README.md papers/ime-observation/README.md papers/ime-observation/.gitignore \
         "${K}/check.sh" "${K}/formats/FORMATS.md" "${V}"; do need_file "${f}"; done

# AC1
selftest_ok "${V}"

# AC3: 正しい gt（3 src）と obs が通る
H='"kind":"header","format":"gt/1","app_version":"0.1.0"'
printf '%s\n' "{${H},\"src\":\"mac_nstic\",\"os\":\"macos\"}" \
  '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"set_marked","len":3,"sel_loc":3,"sel_len":0}' \
  '{"kind":"ev","t_wall_ms":3,"t_mono_ns":4,"ev":"insert_text","len":2}' \
  '{"kind":"ev","t_wall_ms":5,"t_mono_ns":6,"ev":"do_command","cmd":"cancelOperation:"}' > "${TMP}/mac.jsonl"
printf '%s\n' "{${H},\"src\":\"win_imm\",\"os\":\"windows\"}" \
  '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"start_comp"}' \
  '{"kind":"ev","t_wall_ms":3,"t_mono_ns":4,"ev":"comp","flags":2048,"comp_len":0,"result_len":2}' \
  '{"kind":"ev","t_wall_ms":5,"t_mono_ns":6,"ev":"notify","imn":5}' > "${TMP}/imm.jsonl"
printf '%s\n' "{${H},\"src\":\"win_tsf\",\"os\":\"windows\"}" \
  '{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"tsf_start"}' \
  '{"kind":"ev","t_wall_ms":3,"t_mono_ns":4,"ev":"ui_begin","ui_kind":"candidate"}' > "${TMP}/tsf.jsonl"
printf '%s\n' '{"type":"meta","format":"obs/1","os":"macos","logger_version":"0.1.0","manifest_sha256":"0000000000000000000000000000000000000000000000000000000000000000","capabilities":{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}' \
  '{"type":"key","t":10,"category":"alphabetic","press":true}' \
  '{"type":"ime_shadow","t":20,"dwell_ms":900,"nav":0,"abandon":false}' > "${TMP}/obs.jsonl"
for g in mac imm tsf; do run_ok "AC3 正しい gt (${g}) を通す" "${PY}" "${V}" --kind gt "${TMP}/${g}.jsonl"; done
run_ok "AC3 正しい obs を通す" "${PY}" "${V}" --kind obs "${TMP}/obs.jsonl"

# AC2: ⚠️ 本文入りを拒否する（陰性対照）
cp "${TMP}/mac.jsonl" "${TMP}/leak.jsonl"
echo '{"kind":"ev","t_wall_ms":7,"t_mono_ns":8,"ev":"insert_text","len":3,"text":"日本語"}' >> "${TMP}/leak.jsonl"
run_fail "AC2 本文キー入りの gt を拒否する" "${PY}" "${V}" --kind gt "${TMP}/leak.jsonl"
cp "${TMP}/mac.jsonl" "${TMP}/leak2.jsonl"
echo '{"kind":"ev","t_wall_ms":7,"t_mono_ns":8,"ev":"insert_text","len":"日本"}' >> "${TMP}/leak2.jsonl"
run_fail "AC2 整数の位置の文字列を拒否する" "${PY}" "${V}" --kind gt "${TMP}/leak2.jsonl"
cp "${TMP}/mac.jsonl" "${TMP}/leak4.jsonl"
echo '{"kind":"ev","t_wall_ms":7,"t_mono_ns":8,"ev":"do_command","cmd":"insertText:"}' >> "${TMP}/leak4.jsonl"
run_fail "AC2 列挙外の cmd を拒否する" "${PY}" "${V}" --kind gt "${TMP}/leak4.jsonl"
cp "${TMP}/obs.jsonl" "${TMP}/leak3.jsonl"
echo '{"type":"key","t":30,"category":"a","press":true}' >> "${TMP}/leak3.jsonl"
run_fail "AC2 列挙外の category を拒否する" "${PY}" "${V}" --kind obs "${TMP}/leak3.jsonl"
tail -n +2 "${TMP}/obs.jsonl" > "${TMP}/nohead.jsonl"
run_fail "AC2 ヘッダの無い obs を拒否する" "${PY}" "${V}" --kind obs "${TMP}/nohead.jsonl"

# ★ GSE と同じ形の capabilities（3 キー・配列）を通し、壊れた形を拒否する（capabilities.rs:319-332）
CAPOK='{"type":"meta","format":"obs/1","os":"windows","logger_version":"0.1.0","manifest_sha256":"0000000000000000000000000000000000000000000000000000000000000000","capabilities":{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}'
printf '%s\n' "${CAPOK}" '{"type":"key","t":10,"category":"space","press":false}' > "${TMP}/cap_ok.jsonl"
run_ok "AC3 GSE と同じ形の capabilities を通す" "${PY}" "${V}" --kind obs "${TMP}/cap_ok.jsonl"
printf '%s\n' "$(echo "${CAPOK}" | sed 's/"config_gated":\["ime_shadow"\]/"config_gated":["日本語"]/')" > "${TMP}/cap_bad.jsonl"
run_fail "AC2 capabilities の名前が正規表現に合わなければ拒否する" "${PY}" "${V}" --kind obs "${TMP}/cap_bad.jsonl"
printf '%s\n' "$(echo "${CAPOK}" | sed 's/,"threshold_gated":\[\]//')" > "${TMP}/cap_miss.jsonl"
run_fail "AC2 capabilities のキーが欠けていれば拒否する" "${PY}" "${V}" --kind obs "${TMP}/cap_miss.jsonl"
# ★ 区切りの空白を拒否する（後続の検査が空白なしの文字列で行を探すため）
printf '%s\n' "{${H},\"src\":\"mac_nstic\",\"os\":\"macos\"}" '{"kind": "ev", "t_wall_ms": 1, "t_mono_ns": 2, "ev": "unmark"}' > "${TMP}/spaced.jsonl"
run_fail "AC2 空白入りの区切りを拒否する" "${PY}" "${V}" --kind gt "${TMP}/spaced.jsonl"

# AC4 / AC5
check_entry_green
run_ok "AC4 check.sh --self-test（陰性対照）が緑" bash "${K}/check.sh" --self-test
run_ok "AC5 check.sh --compile が緑" bash "${K}/check.sh" --compile

# AC6
for p in papers/ime-observation/runs/x.jsonl papers/ime-observation/kit/logger/target/a papers/ime-observation/sealed/y.ndjson papers/ime-observation/kit/refinput-macos/.build/z; do
  if git check-ignore -q "${p}"; then ok "AC6 ignored: ${p}"; else ng "AC6 ignore されない: ${p}"; fi
done
if git check-ignore -q papers/ime-observation/kit/corpus/data/phrases.jsonl; then
  ng "AC6 句のデータ（kit/corpus/data/*.jsonl）が ignore されている（例外が効いていない）"
else ok "AC6 句のデータは追跡できる（例外が効いている）"; fi

# AC7
run_ok "AC7 check-shell-portability が緑" bash scripts/check-shell-portability.sh

# AC8
need_grep docs/repository-structure.md 'papers/' "AC8 repository-structure.md に papers/"
need_grep docs/experiment-tracking.md 'papers/<paper>/experiment/' "AC8 experiment-tracking.md に 1 行"

forbid_gse_changes
only_allowed '^(papers/README\.md|papers/ime-observation/(README\.md|\.gitignore|kit/check\.sh|kit/formats/(FORMATS\.md|validate_logs\.py))|docs/(repository-structure|experiment-tracking)\.md)$'
finish
