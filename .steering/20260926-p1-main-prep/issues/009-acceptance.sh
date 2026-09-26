#!/usr/bin/env bash
# issue 009（P1-A: 凍結既定で restop を測る統合テスト）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 009] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
T=src-tauri/tests/p1_restart_default_config.rs
[ -f "$T" ] || fail "$T が無い"
git diff --quiet main -- src-tauri/src/analysis/feat_offline/restart.rs src-tauri/src/analysis/feat_offline/stall_onset.rs \
  || fail "実装（restart.rs / stall_onset.rs）が変わっている（Out）"
git diff --quiet main -- src-tauri/tests/fixtures/ src-tauri/prereg/ || fail "fixture か凍結 JSON が変わっている"
grep -Eq -- '"--set"|"--feature-config"' "$T" && fail "テストが --set / --feature-config を渡している（★ 凍結既定のまま測る）"

log="$(cd src-tauri && cargo test --test p1_restart_default_config 2>&1)"; rc=$?
[ "$rc" -eq 0 ] || { printf '%s\n' "$log" | tail -30; fail "統合テストが非 0"; }
for t in restop_is_measurable_under_frozen_defaults restop_absent_without_second_silence; do
  printf '%s' "$log" | grep -Eq "test ${t} \.\.\. ok" || fail "テスト $t が ok で走っていない"
done
echo "[acceptance 009] OK"
