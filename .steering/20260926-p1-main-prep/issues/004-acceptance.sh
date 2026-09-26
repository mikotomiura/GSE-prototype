#!/usr/bin/env bash
# issue 004（探索格子の実行器・規則 (d)）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 004] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
export PYTHONUTF8=1

for f in scripts/p1_run_grid.py scripts/tests/test_p1_run_grid.py; do [ -f "$f" ] || fail "$f が無い"; done
git diff --quiet main -- src-tauri/prereg/ docs/preregistration-p1-episode.md || fail "凍結文書か凍結 JSON が変わっている"
git diff --quiet main -- src-tauri/src/ || fail "Rust が変わっている（判断 7: CLI は変えない）"

log="$("$PY" -m unittest scripts.tests.test_p1_run_grid -v 2>&1)"; rc=$?
printf '%s\n' "$log" | tail -5
[ "$rc" -eq 0 ] || fail "unittest が非 0 (rc=$rc)"
printf '%s' "$log" | grep -q "skipped" && fail "skip がある"
for t in test_grid_has_31_configs test_warmup_paired_with_q test_rule_d_table test_rule_d_excludes_mismatched_runs \
         test_refuses_without_pg1 test_manifest_complete_only_on_success test_guards test_all_poles_passthrough_whitelist; do
  printf '%s' "$log" | grep -Eq "^${t} .*\.\.\. ok$" || fail "テスト $t が ok で走っていない"
done

# ★ AC5 を実物の凍結 JSON で: 既定の読み先（pg1 無し）では exit 6
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT
mkdir -p "$tmpd/nd/P01"; cp src-tauri/tests/fixtures/minimal.ndjson "$tmpd/nd/P01/s1.ndjson"
"$PY" scripts/p1_run_grid.py --ndjson-root "$tmpd/nd" --out "$tmpd/out" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 6 ] || fail "AC5: 凍結 JSON（pg1 無し）で exit 6 にならない (rc=$rc)"
[ -z "$(ls -A "$tmpd/out" 2>/dev/null)" ] || fail "AC5: exit 6 なのに出力がある"

# ★ AC7: パススルーの白リスト（実物のスクリプトで）
out7="$tmpd/o7"
bash scripts/run-features-all-poles.sh src-tauri/tests/fixtures/minimal.ndjson "$out7" -- --pole baseline >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] || fail "AC7: '-- --pole' が exit 2 にならない (rc=$rc)"
bash scripts/run-features-all-poles.sh src-tauri/tests/fixtures/minimal.ndjson "$out7" -- --set evil=1 >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] || fail "AC7: 知らないキーが exit 2 にならない (rc=$rc)"
bash scripts/run-features-all-poles.sh src-tauri/tests/fixtures/minimal.ndjson "$out7" -- --set 'q=0.99;rm' >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] || fail "AC7: 形の違う値が exit 2 にならない (rc=$rc)"
bash scripts/run-features-all-poles.sh src-tauri/tests/fixtures/minimal.ndjson "$out7" -- --set q=0.99 --set q=0.999 >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] || fail "AC7: 同じキーの 2 回指定が exit 2 にならない (rc=$rc)"
# ★ 陽性対照: 正しい組は通り、封筒 config に反映される
( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "AC7: build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"
GSE_REPLAY_BIN="$BIN" bash scripts/run-features-all-poles.sh src-tauri/tests/fixtures/stall_onset_observed.ndjson "$tmpd/o8" \
  -- --set q=0.995 --set warmup_count=200 >/dev/null 2>&1 || fail "AC7: 正しい --set の組が通らない"
command -v jq >/dev/null 2>&1 || fail "jq が無い"
for p in baseline pointer_b modifier_m_plus; do
  jq -e '.config.q == 0.995 and .config.warmup_count == 200' "$tmpd/o8/$p.json" >/dev/null || fail "AC7: $p の config に --set が反映されていない"
done
# ★ 後方互換: 前タスク 008 の acceptance（`--` なしの挙動）
bash .steering/20260921-p1-prereg-cli-poles/issues/008-acceptance.sh >/dev/null 2>&1 || fail "AC7: 前タスク 008-acceptance が赤（★ 後方互換が壊れた）"

bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC8: CI に配線されていない"
grep -q "scripts.tests.test_p1_run_grid" .github/workflows/ci.yml || fail "AC8: ci.yml にモジュール名が無い"
echo "[acceptance 004] OK"
