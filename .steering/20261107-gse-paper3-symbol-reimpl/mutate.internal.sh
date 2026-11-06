#!/bin/bash
# 変異で赤を見る（公開しない）。kit を一時の dir に写し、1 か所ずつ壊して合成の適合の検査を回す。
# 捕捉 = 変異が当たり（ファイルが変わり）、検査の JSON の mismatched_cases が 0 より大きい。
# 先に無変異の対照（rc=0・mismatched_cases=0）を確かめる。生存・未適用・異常終了があれば非 0 で終える。
# 等価と分かっている変異（EQUIV）は生存を期待する。
set -u
KIT=/Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols
S=/private/tmp/claude-501/-Users-johnd-GSE-prototype/098173bb-e9d7-4de0-853a-714ea3c7f716/scratchpad/sym
IN="$KIT/conformance/data/inputs.json.gz"; EX="$KIT/conformance/data/expected.json.gz"
mkdir -p "$S"
fail=0
mism() { python3 -I -c 'import json,sys
try: print(json.loads(open(sys.argv[1]).read().strip().splitlines()[-1]).get("mismatched_cases", -1))
except Exception: print(-1)' "$1"; }
out=$(mktemp "$S/ctl.XXXX")
python3 -I "$KIT/conformance/check.py" "$IN" "$EX" > "$out" 2>&1; rc=$?
if [ $rc -ne 0 ] || [ "$(mism "$out")" != "0" ]; then echo "CONTROL FAILED rc=$rc"; exit 2; fi
echo "control: rc=0 mismatched=0"; rm -f "$out"
run() {
  local name="$1" file="$2" from="$3" to="$4" expect="${5:-caught}"
  local W; W=$(mktemp -d "$S/mut.XXXX")
  cp -R "$KIT/." "$W/"
  python3 -I - "$W/$file" "$from" "$to" <<'PY'
import sys
p, a, b = sys.argv[1:4]
s = open(p).read()
if s.count(a) != 1:
    sys.exit("pattern count %d" % s.count(a))
open(p, "w").write(s.replace(a, b))
PY
  if [ $? -ne 0 ] || cmp -s "$KIT/$file" "$W/$file"; then echo "$name: NOT APPLIED"; fail=1; rm -rf "$W"; return; fi
  python3 -I "$W/conformance/check.py" "$IN" "$EX" > "$W/out.txt" 2>&1
  local rc=$? m; m=$(mism "$W/out.txt")
  local got
  if [ "$m" -gt 0 ] 2>/dev/null; then got=caught; elif [ $rc -eq 0 ] && [ "$m" = "0" ]; then got=survived; else got=error; fi
  echo "$name: $got (expected $expect) rc=$rc mismatched=$m"
  [ "$got" = "$expect" ] || fail=1
  rm -rf "$W"
}
run m1_keep_literal symbolizer.py 'c["typing_keep"] * self.ex' '(1.0 - c["typing_alpha"]) * self.ex' survived
run m2_alpha_threshold constants.json '"min_silence_s": 15.0' '"min_silence_s": 16.0'
run m3_run_threshold constants.json '"backspace_run_threshold": 14' '"backspace_run_threshold": 13'
run m4_tick_order symbolizer.py 'while sym.next_tick_ms <= t:' 'while sym.next_tick_ms < t:'
run m5_release constants.json '"synthetic_release_ms": 100' '"synthetic_release_ms": 99'
run m6_x_order symbolizer.py 'xw["f3"] * p3 + xw["f6"] * p6 + xw["f1"] * p1 + xw["f5"] * p5' 'xw["f1"] * p1 + xw["f3"] * p3 + xw["f6"] * p6 + xw["f5"] * p5'
run m7_reset_presses constants.json '"silence_reset_presses": 3' '"silence_reset_presses": 2'
run m8_pending_kept symbolizer.py '                self.pending_run_symbol = False
' ''
run m9_buffer constants.json '"buffer_capacity_events": 600' '"buffer_capacity_events": 598'
run m10_window_cutoff symbolizer.py 'events = [e for e in buffer if e[0] >= cutoff]' 'events = [e for e in buffer if e[0] > cutoff]'
echo "overall: $([ $fail -eq 0 ] && echo ok || echo FAIL)"
exit $fail
