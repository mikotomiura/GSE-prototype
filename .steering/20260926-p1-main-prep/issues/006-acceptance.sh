#!/usr/bin/env bash
# issue 006（再現の雛形と 1 コマンド再現）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 006] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
command -v jq >/dev/null 2>&1 || fail "jq が無い"
export PYTHONUTF8=1
"$PY" -c "import duckdb" 2>/dev/null || fail "duckdb が無い"

T=scripts/templates/p1-experiment/README.md
for f in scripts/p1-repro.sh scripts/p1-repro-test.sh "$T"; do [ -f "$f" ] || fail "$f が無い"; done
[ ! -d experiments ] || [ -z "$(git ls-files --others --exclude-standard experiments/)" ] || fail "experiments/ に未追跡の新規物がある（★ 判断 14）"
# ★ 部品（002〜005）を本 issue が変えていない: タスクの base ブランチとの差分で見る
B="$(git rev-parse --verify -q feat/p1-main-prep || echo HEAD)"
git diff --quiet "$B" -- scripts/p1_features_io.py scripts/p1_pg1_distribution.py scripts/build_p1_episode_db.py \
  scripts/p1_run_grid.py scripts/p1_select.py scripts/run-features-all-poles.sh \
  || fail "部品（002〜005 の成果・3 極スクリプト）が変わっている（Out）"
git diff --quiet main -- src-tauri/prereg/ docs/preregistration-p1-episode.md || fail "凍結文書か凍結 JSON が変わっている"

bash scripts/p1-repro-test.sh || fail "p1-repro-test.sh が非 0"

# AC5: 雛形の欄
for w in "PG-1" "下限" "扱い" "INCONCLUSIVE" "seed" "HMM_VERSION" "Cargo.lock" "gse-dataset" "（未記入）"; do
  grep -q "$w" "$T" || fail "AC5: 雛形に '$w' が無い"
done

# AC1: 実物の gse-replay で E2E（repo の合成 fixture・出力は repo の外）
( cd src-tauri && cargo build --quiet --bin gse-replay ) || fail "AC1: build できない"
BIN="$REPO_ROOT/src-tauri/target/debug/gse-replay"; [ -x "$BIN" ] || BIN="$BIN.exe"
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"; trap 'rm -rf "$tmpd"' EXIT
mkdir -p "$tmpd/nd/P01" "$tmpd/nd/P02"
cp src-tauri/tests/fixtures/stall_onset_observed.ndjson "$tmpd/nd/P01/s1.ndjson"
cp src-tauri/tests/fixtures/pointer_pole.ndjson "$tmpd/nd/P01/s2.ndjson"
cp src-tauri/tests/fixtures/modifier_pole.ndjson "$tmpd/nd/P02/s1.ndjson"
GSE_REPLAY_BIN="$BIN" bash scripts/p1-repro.sh "$tmpd/nd" "$tmpd/w"; rc=$?
[ "$rc" -eq 0 ] || fail "AC1: --stage pg1 が非 0 (rc=$rc)"
[ -f "$tmpd/w/pg1_distribution.json" ] || fail "AC1: pg1_distribution.json が無い"
[ -f "$tmpd/w/provenance.json" ] || fail "AC1: provenance.json が無い"
ls "$tmpd/w"/*.duckdb >/dev/null 2>&1 || fail "AC1: episode DB が無い"
jq -e 'has("hmm_version") and has("prereg_version")' "$tmpd/w/provenance.json" >/dev/null || fail "AC1: provenance に刻印が無い"
[ -z "$(find "$tmpd/w" -name grid_manifest.json)" ] || fail "AC2: 既定で格子を回している"

GSE_REPLAY_BIN="$BIN" bash scripts/p1-repro.sh "$tmpd/nd" "$tmpd/w2" --stage search --labels /dev/null >/dev/null 2>&1; rc=$?
[ "$rc" -eq 6 ] || fail "AC3: --stage search が凍結 JSON で exit 6 にならない (rc=$rc)"

bash scripts/check-shell-portability.sh >/dev/null || fail "AC6: shell portability が赤"
bash scripts/check-tests-are-wired.sh >/dev/null || fail "AC6: CI に配線されていない"
bash scripts/check_no_feature_output.sh >/dev/null || fail "共有の門が赤（★ repo に特徴行が入った）"
echo "[acceptance 006] OK"
