#!/usr/bin/env bash
# issue 002（PG-1 分布集計）の AC 検査
# ⚠️ loop-run.sh は worktree を cwd にして呼ぶ → repo root は cwd。
set -uo pipefail
fail() { echo "[acceptance 002] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
command -v jq >/dev/null 2>&1 || fail "jq が無い"
export PYTHONUTF8=1

for f in scripts/p1_features_io.py scripts/p1_pg1_distribution.py scripts/tests/test_p1_pg1_distribution.py; do
  [ -f "$f" ] || fail "$f が無い"
done

log="$("$PY" -m unittest scripts.tests.test_p1_pg1_distribution -v 2>&1)"; rc=$?
printf '%s\n' "$log" | tail -5
[ "$rc" -eq 0 ] || fail "unittest が非 0 (rc=$rc)"
printf '%s' "$log" | grep -q "skipped" && fail "skip がある"
for t in test_counts_and_summary test_output_invariant_to_non_onset_fields test_output_keys_whitelist \
         test_not_applicable_counted_separately test_zero_episode_participant_included test_fail_closed_layout test_rejects_non_frozen test_out_inside_git_rejected; do
  printf '%s' "$log" | grep -Eq "^${t} .*\.\.\. ok$" || fail "テスト $t が ok で走っていない"
done

# ★ 構造の保証を静的にも見る: PG-1 の CLI は封筒の中の禁止キーを名指ししない
for k in restart dispersion ime_overlap theta_person_ms theta_sample_n t0_ms s_ms; do
  grep -q "$k" scripts/p1_pg1_distribution.py && fail "p1_pg1_distribution.py が '$k' に触れている（★ 射影 project_pg1 だけを使う）"
done

# ── AC7: E2E（repo の合成 fixture → 実物の 3 極スクリプト → レイアウト → CLI）──
( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "AC7: gse-replay を build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"
[ -x "$BIN" ] || fail "AC7: gse-replay のバイナリが見つからない"
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT
git -C "$tmpd" rev-parse --is-inside-work-tree >/dev/null 2>&1 && fail "AC7: 一時ディレクトリが git 管理下（★ 検査の前提が崩れている）"
root="$tmpd/root"
mk() { # <P-ID> <session> <fixture>
  mkdir -p "$root/$1"
  GSE_REPLAY_BIN="$BIN" bash scripts/run-features-all-poles.sh "src-tauri/tests/fixtures/$3" "$root/$1/$2" >/dev/null 2>&1 \
    || fail "AC7: run-features-all-poles.sh が非 0 ($3)"
}
mk P01 s1 stall_onset_observed.ndjson
mk P01 s2 pointer_pole.ndjson
mk P02 s1 modifier_pole.ndjson
"$PY" scripts/p1_pg1_distribution.py --root "$root" --out "$tmpd/pg1.json"; rc=$?
[ "$rc" -eq 0 ] || fail "AC7: CLI が非 0 (rc=$rc)"
jq -e '.provenance.n_sessions == 3' "$tmpd/pg1.json" >/dev/null || fail "AC7: n_sessions が 3 ではない"
# ★ 出力に行単位の中身が漏れていない（封筒の印も特徴行の形も無い）
grep -q '"prohibited"' "$tmpd/pg1.json" && fail "AC7: 出力に共有禁止の封筒の印がある"
grep -Eq '"(t0_ms|restart|dispersion|ime_overlap)"' "$tmpd/pg1.json" && fail "AC7: 出力に行の中身のキーがある"

# ★ AC7 の陰性対照: 同じレイアウトで 1 セッションの極を 1 つ消すと exit 3
rm "$root/P02/s1/pointer_b.json"
"$PY" scripts/p1_pg1_distribution.py --root "$root" --out "$tmpd/pg1b.json" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 3 ] || fail "AC7: 極の欠けで exit 3 にならない (rc=$rc)"

bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC8: CI に配線されていない"
grep -q "scripts.tests.test_p1_pg1_distribution" .github/workflows/ci.yml || fail "AC8: ci.yml にモジュール名が無い"
echo "[acceptance 002] OK"
