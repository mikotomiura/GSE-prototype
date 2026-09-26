#!/usr/bin/env bash
# issue 008（feat 行 0 本で T1a を null）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 008] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
command -v jq >/dev/null 2>&1 || fail "jq が無い"

git diff --quiet main -- src-tauri/tests/fixtures/ src-tauri/tests/snapshots/ src-tauri/schema/ src-tauri/prereg/ \
  || fail "AC5: fixture・スナップショット・schema・凍結 JSON に差分がある"
hv_main="$(git show main:src-tauri/src/analysis/engine.rs | grep -E 'HMM_VERSION' | head -1)"
hv_head="$(grep -E 'HMM_VERSION' src-tauri/src/analysis/engine.rs | head -1)"
[ "$hv_main" = "$hv_head" ] || fail "AC5: HMM_VERSION が変わった"

( cd src-tauri && cargo test --quiet --lib -- --list 2>/dev/null ) > /tmp/p1-008-list.$$ || true
grep -q "no_observed_interval_yields_empty_windows: test" /tmp/p1-008-list.$$ || { rm -f /tmp/p1-008-list.$$; fail "AC1: テストが無い"; }
grep -q "t1a_is_null_without_feat_rows: test" /tmp/p1-008-list.$$ || { rm -f /tmp/p1-008-list.$$; fail "AC2: テストが無い"; }
rm -f /tmp/p1-008-list.$$

( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"

# ★ main の gse-replay を別 worktree で作り、出力を比べる
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
cleanup() { git worktree remove --force "$tmpd/main" >/dev/null 2>&1; rm -rf "$tmpd"; }
trap cleanup EXIT
git worktree add --detach "$tmpd/main" main >/dev/null 2>&1 || fail "main の worktree を作れない"
( cd "$tmpd/main/src-tauri" && CARGO_TARGET_DIR="$REPO_ROOT/src-tauri/target/p1-008-main" cargo build --quiet --bin gse-replay ) || fail "main を build できない"
MBIN="$REPO_ROOT/src-tauri/target/p1-008-main/debug/gse-replay"; [ -x "$MBIN" ] || MBIN="$MBIN.exe"

# AC2: feat 行 0 本 → T1a 全 null・iki_cv / surprise は main と同じ
F=src-tauri/tests/fixtures/deep_silence.ndjson
[ "$(grep -c '"type":"feat"' "$F")" -eq 0 ] || fail "AC2: 前提が崩れた（deep_silence に feat 行がある）"
"$BIN"  "$F" --features > "$tmpd/h.json" 2>/dev/null || fail "AC2: --features が非 0"
"$MBIN" "$F" --features > "$tmpd/m.json" 2>/dev/null || fail "AC2: main の --features が非 0"
jq -e '[.rows[].dispersion | .pause_p50_ms, .pause_p90_ms, .pause_max_ms] | all(. == null)' "$tmpd/h.json" >/dev/null \
  || fail "AC2: feat 行 0 本なのに pause_* に値がある"
jq -e '[.rows[].dispersion.pause_max_ms | select(. != null)] | length > 0' "$tmpd/m.json" >/dev/null \
  || fail "AC2 の対照: main でも pause_max_ms が全 null（★ 検査の前提が崩れた）"
a="$(jq -c '[.rows[].dispersion | [.iki_cv, .surprise]]' "$tmpd/h.json")"; b="$(jq -c '[.rows[].dispersion | [.iki_cv, .surprise]]' "$tmpd/m.json")"
[ "$a" = "$b" ] || fail "AC2: iki_cv / surprise が変わった"

# AC3: feat 行を持つ fixture は main と byte 同一
for f in t1a_window stall_onset_observed pointer_pole modifier_pole; do
  for p in baseline pointer_b modifier_m_plus; do
    "$BIN"  "src-tauri/tests/fixtures/$f.ndjson" --features --pole "$p" > "$tmpd/h.$f.$p" 2>/dev/null || fail "AC3: $f/$p が非 0"
    "$MBIN" "src-tauri/tests/fixtures/$f.ndjson" --features --pole "$p" > "$tmpd/m.$f.$p" 2>/dev/null || fail "AC3: main の $f/$p が非 0"
    cmp -s "$tmpd/h.$f.$p" "$tmpd/m.$f.$p" || fail "AC3: $f / $p の出力が main と違う"
  done
done

# AC4: 張り直した過去 acceptance 2 本
bash .steering/20260914-mhd-feature-offline-tiers/issues/003-acceptance.sh >/dev/null 2>&1 || fail "AC4: mhd-feature-offline-tiers/003-acceptance が赤"
bash .steering/20260921-p1-prereg-cli-poles/issues/003-acceptance.sh >/dev/null 2>&1 || fail "AC4: p1-prereg-cli-poles/003-acceptance が赤"
grep -q '"type":"feat"' .steering/20260914-mhd-feature-offline-tiers/issues/003-acceptance.sh \
  || fail "AC4: 旧検査が feat 行を足す形になっていない（★ 値の検査が空振りしている疑い）"

# AC5: ゴールデン
( cd src-tauri && cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json >/dev/null 2>&1 ) \
  || fail "AC5: ゴールデン再生が赤"
echo "[acceptance 008] OK"
