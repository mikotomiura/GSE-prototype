#!/usr/bin/env bash
# issue 003（episode 表の DuckDB）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 003] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
export PYTHONUTF8=1
"$PY" -c "import duckdb" 2>/dev/null || fail "duckdb が無い（★ 無いと skip で緑になるので検査しない）"

for f in scripts/build_p1_episode_db.py scripts/tests/test_p1_episode_db.py; do [ -f "$f" ] || fail "$f が無い"; done
git diff --quiet origin/main -- scripts/build_analysis_db.py 2>/dev/null || git diff --quiet main -- scripts/build_analysis_db.py \
  || fail "build_analysis_db.py が変わっている（Out）"

log="$("$PY" -m unittest scripts.tests.test_p1_episode_db -v 2>&1)"; rc=$?
printf '%s\n' "$log" | tail -5
[ "$rc" -eq 0 ] || fail "unittest が非 0 (rc=$rc)"
printf '%s' "$log" | grep -q "skipped" && fail "skip がある"
for t in test_tables_and_counts test_t0_table_excludes_retrospective test_manifest_join \
         test_not_applicable_sessions_recorded test_guards; do
  printf '%s' "$log" | grep -Eq "^${t} .*\.\.\. ok$" || fail "テスト $t が ok で走っていない"
done

# ── AC6: E2E ──
( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "AC6: gse-replay を build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT
root="$tmpd/root"
mk() { mkdir -p "$root/$1"; GSE_REPLAY_BIN="$BIN" bash scripts/run-features-all-poles.sh "src-tauri/tests/fixtures/$3" "$root/$1/$2" >/dev/null 2>&1 || fail "AC6: 3 極が非 0 ($3)"; }
mk P01 s1 stall_onset_observed.ndjson
mk P01 s2 pointer_pole.ndjson
mk P02 s1 modifier_pole.ndjson
printf 'participant_id,session_id,os,phase\nP01,s1,windows,pre\n' > "$tmpd/sessions.csv"
"$PY" scripts/build_p1_episode_db.py --root "$root" --out "$tmpd/ep.duckdb" --sessions "$tmpd/sessions.csv"; rc=$?
[ "$rc" -eq 0 ] || fail "AC6: CLI が非 0 (rc=$rc)"
"$PY" - "$tmpd/ep.duckdb" <<'EOF' || fail "AC6: DB の中身が期待と違う"
import sys, duckdb
c = duckdb.connect(sys.argv[1], read_only=True)
n = c.execute("select count(*) from sessions").fetchone()[0]
assert n == 9, f"sessions={n}"
cols = {r[0] for r in c.execute("select column_name from information_schema.columns where table_name='episodes_t0'").fetchall()}
assert "ime_overlap" not in cols and "restart" not in cols, cols
rcols = {r[0] for r in c.execute("select column_name from information_schema.columns where table_name='episodes_retrospective'").fetchall()}
assert "ime_overlap" in rcols, rcols
m = c.execute("select count(*) from episodes_with_manifest where has_manifest").fetchone()[0]
nm = c.execute("select count(*) from episodes_with_manifest where not has_manifest").fetchone()[0]
assert m + nm == c.execute("select count(*) from episodes_t0").fetchone()[0]
EOF

# ★ git 管理下の出力先は拒否
"$PY" scripts/build_p1_episode_db.py --root "$root" --out "$REPO_ROOT/.p1-accept-probe.duckdb" >/dev/null 2>&1; rc=$?
rm -f "$REPO_ROOT/.p1-accept-probe.duckdb"
[ "$rc" -eq 2 ] || fail "repo の中への出力が exit 2 にならない (rc=$rc)"

# AC7: 配線と順序（duckdb の install より後）
bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC7: CI に配線されていない"
inst="$(grep -n 'pip install --quiet duckdb' .github/workflows/ci.yml | head -1 | cut -d: -f1)"
use="$(grep -n 'scripts.tests.test_p1_episode_db' .github/workflows/ci.yml | head -1 | cut -d: -f1)"
[ -n "$inst" ] && [ -n "$use" ] || fail "AC7: install 行かモジュール行が見つからない"
[ "$use" -gt "$inst" ] || fail "AC7: duckdb の install より前で走る（★ 全件 skip の緑になる）"
echo "[acceptance 003] OK"
