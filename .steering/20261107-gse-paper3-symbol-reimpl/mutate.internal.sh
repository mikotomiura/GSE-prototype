#!/bin/bash
# 変異で赤を見る（公開しない）。kit を一時の dir に写し、1 か所ずつ壊して合成の適合の検査を回す。
# 期待: 変異が当たり（ファイルが変わり）、検査が非 0 で終わる。
set -u
KIT=/Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols
S=/private/tmp/claude-501/-Users-johnd-GSE-prototype/098173bb-e9d7-4de0-853a-714ea3c7f716/scratchpad/sym
run() {
  local name="$1" file="$2" from="$3" to="$4"
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
  local rc_apply=$?
  if [ $rc_apply -ne 0 ] || cmp -s "$KIT/$file" "$W/$file"; then echo "$name: NOT APPLIED"; rm -rf "$W"; return; fi
  python3 -I "$W/conformance/check.py" "$S/inputs.json" "$S/expected.json" > "$W/out.txt" 2>&1
  local rc=$?
  echo "$name: rc=$rc $(tail -1 "$W/out.txt" | cut -c1-120)"
  rm -rf "$W"
}
run m1_keep_literal symbolizer.py 'c["typing_keep"] * self.ex' '(1.0 - c["typing_alpha"]) * self.ex'
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
