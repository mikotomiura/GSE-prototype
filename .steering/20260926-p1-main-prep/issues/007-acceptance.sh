#!/usr/bin/env bash
# issue 007（P1-G: --feature-config の id / version の検証）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 007] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
command -v jq >/dev/null 2>&1 || fail "jq が無い"
git diff --quiet main -- src-tauri/prereg/ src-tauri/schema/ docs/preregistration-p1-episode.md || fail "凍結 JSON・schema・凍結文書が変わっている"
git diff --quiet main -- src-tauri/Cargo.toml || fail "Cargo.toml が変わっている（新規依存は Stop）"

log="$(cd src-tauri && cargo test --quiet --bin gse-replay -- --nocapture feature_config 2>&1)"; rc=$?
[ "$rc" -eq 0 ] || { printf '%s\n' "$log" | tail -20; fail "cargo test が非 0"; }
log2="$(cd src-tauri && cargo test --bin gse-replay -- --list 2>/dev/null)"
for t in feature_config_rejects_malformed_id feature_config_rejects_malformed_version \
         feature_config_accepts_wellformed_other_id frozen_json_id_version_are_wellformed; do
  printf '%s' "$log2" | grep -q "$t: test" || fail "テスト $t が無い"
done

# AC5: CLI として（不正 id → 非 0・stdout 空 ／ 陽性対照: 正しい別 id → 0・封筒に写る）
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"; trap 'rm -rf "$tmpd"' EXIT
jq '.id = "Bad ID/../x"' src-tauri/prereg/p1-episode.json > "$tmpd/bad.json"
jq '.id = "p1-episode-alt" | .version = "2.3.4"' src-tauri/prereg/p1-episode.json > "$tmpd/good.json"
( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"
out="$("$BIN" src-tauri/tests/fixtures/minimal.ndjson --features --feature-config "$tmpd/bad.json" 2>/dev/null)"; rc=$?
[ "$rc" -ne 0 ] || fail "AC5: 不正な id で exit 0"
[ -z "$out" ] || fail "AC5: 不正な id なのに stdout に出力がある"
"$BIN" src-tauri/tests/fixtures/minimal.ndjson --features --feature-config "$tmpd/good.json" > "$tmpd/o.json" 2>/dev/null \
  || fail "AC5 陽性対照: 形式に合う別 id が拒否された"
jq -e '.config.prereg_id == "p1-episode-alt" and .config.prereg_version == "2.3.4" and .config.config_source == "file"' "$tmpd/o.json" >/dev/null \
  || fail "AC5 陽性対照: 封筒に写っていない"
echo "[acceptance 007] OK"
