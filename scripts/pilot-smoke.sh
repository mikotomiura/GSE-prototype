#!/usr/bin/env bash
# pilot-smoke: M1 パイロット データ収集→分析パイプラインの end-to-end 統合スモーク
# (pilot-pipeline-runbook GAP⑤ / 受け入れ条件の検証ゲート)。
#
# 合成 session (実データ非依存) を全段に通し、cross_section が生成されるまでを 1 コマンドで検証する:
#
#   合成 raw NDJSON
#     → gse-package   (匿名化 + age 暗号化)            [被験者側]
#     → gse-unpack    (age 復号 → 匿名化 NDJSON)        [研究者側 D-PP1]
#     → sync-session  (gse-replay --metrics → metrics.json)
#     → gen_sessions_manifest (sessions.csv 生成 + phase 記入)
#     → build_analysis_db (#6 DuckDB join → cross_section)
#
# age CLI 非依存 (gse-unpack が age crate で鍵生成・復号も担う)。必要なのは cargo + python + duckdb。
# 一時資材 (鍵・平文 NDJSON・age・metrics・DB) はすべて mktemp ディレクトリ内で完結し、
# trap で必ず後始末する (data-privacy: 鍵/平文を repo に残さない)。
#
# Usage:
#   ./scripts/pilot-smoke.sh
#
# Exit codes: 0 = PASS, 非0 = どこかの段で結線が壊れている (出力に失敗段を明示)。
#
# 前提: git-bash (Windows) / bash、cargo、python3、`pip install -r scripts/requirements-dev.txt` (duckdb)。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID="P900"   # 合成被験者 (実在 P-ID と衝突しない高位番号)
FIXTURE="$REPO_ROOT/src-tauri/tests/fixtures/outcome_metrics.ndjson"

step() { echo "[pilot-smoke] $*"; }
fail() { echo "[pilot-smoke] FAIL: $*" >&2; exit 1; }

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then PYTHON_BIN="python"
else fail "python3/python not found on PATH"; fi

[[ -f "$FIXTURE" ]] || fail "synthetic fixture not found: $FIXTURE"

# OS ラベル (metrics パス用)。MINGW/MSYS/CYGWIN は windows 扱い。
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) OS_LABEL="windows" ;;
    Linux)               OS_LABEL="linux" ;;
    *)                   OS_LABEL="macos" ;;
esac

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT
step "work dir: $WORK (auto-removed on exit)"

# cargo bin を src-tauri から package feature 付きで実行するヘルパ。
run_cargo_bin() {
    local bin="$1"; shift
    ( cd "$REPO_ROOT/src-tauri" && cargo run --quiet --features package --bin "$bin" -- "$@" )
}

# === Step 1: 研究者鍵ペア生成 (gse-unpack --keygen) ===
step "Step 1/6: gse-unpack --keygen (age 鍵ペア生成)"
KEYFILE="$WORK/age-identity.txt"
KEYGEN_OUT="$(run_cargo_bin gse-unpack --keygen --out "$KEYFILE")"
# 公開鍵トークンのみ抽出 (行頭依存にしない: 将来 stdout 文言が増えても堅牢)。
PUBKEY="$(printf '%s\n' "$KEYGEN_OUT" | grep -m1 -oE 'age1[0-9a-z]+' || true)"
[[ -n "$PUBKEY" ]] || fail "could not parse age public key from keygen output"
[[ -f "$KEYFILE" ]] || fail "identity file not written: $KEYFILE"
step "  pubkey: ${PUBKEY:0:20}…  secret: $KEYFILE"

# === Step 2: 被験者側 gse-package (匿名化 + age 暗号化) ===
step "Step 2/6: gse-package (匿名化 + age 暗号化)"
run_cargo_bin gse-package --input "$FIXTURE" --participant "$PID" --recipient "$PUBKEY" --out "$WORK" >/dev/null
AGE_FILE="$WORK/${PID}_outcome_metrics.age"
[[ -f "$AGE_FILE" ]] || fail "expected age artifact not produced: $AGE_FILE"
# 暗号塊に平文 category 文字列が露出しないこと (転送経路の信用不要性)。
if grep -aq "alphabetic" "$AGE_FILE"; then fail "plaintext 'alphabetic' leaked into .age ciphertext"; fi
step "  produced: $(basename "$AGE_FILE")"

# === Step 3: 研究者側 gse-unpack (age 復号 → 匿名化 NDJSON) ===
step "Step 3/6: gse-unpack (age 復号)"
run_cargo_bin gse-unpack --input "$AGE_FILE" --identity "$KEYFILE" --out "$WORK" >/dev/null
DECRYPTED="$WORK/${PID}_outcome_metrics.ndjson"
[[ -f "$DECRYPTED" ]] || fail "decrypt did not produce $DECRYPTED"
grep -q '"category"' "$DECRYPTED" || fail "decrypted NDJSON has no category fields (anonymization lost?)"
if grep -q '"vk"' "$DECRYPTED"; then fail "raw \"vk\" present in decrypted NDJSON — not anonymized"; fi
step "  decrypted: $(basename "$DECRYPTED") ($(wc -l < "$DECRYPTED") lines, anonymized)"

# === Step 4: sync-session (gse-replay --metrics → metrics.json) ===
step "Step 4/6: sync-session --no-commit (metrics 生成)"
DATASET="$WORK/dataset"
METRICS_DIR="$DATASET/metrics/$PID/$OS_LABEL"
mkdir -p "$METRICS_DIR" "$DATASET/survey"
# sync-session.sh は GSE_DATASET 配下に metrics を書く。PID はパス導出不可なので GSE_PID で渡す。
GSE_DATASET="$DATASET" GSE_PID="$PID" \
    "$REPO_ROOT/scripts/sync-session.sh" "$DECRYPTED" --no-commit --output-dir "$METRICS_DIR" \
    || fail "sync-session failed (gse-replay --metrics path)"
METRICS_JSON="$METRICS_DIR/${PID}_outcome_metrics.metrics.json"
[[ -f "$METRICS_JSON" ]] || fail "metrics JSON not produced: $METRICS_JSON"
step "  metrics: ${PID}/${OS_LABEL}/$(basename "$METRICS_JSON")"

# === Step 5: survey 配置 + sessions.csv 生成 + phase 記入 ===
step "Step 5/6: survey 配置 + gen_sessions_manifest + phase=pre 記入"
# survey: 最小スキーマ + D8 WoZ 列 (post 行)。(P-ID, phase) 一意。
cat > "$DATASET/survey/${PID}.csv" <<CSV
participant_id,phase,gse_total,nasa_tlx_total,walk_done,returned_to_work,inconvenience_benefit_accepted
${PID},pre,22,65,,,
${PID},post,30,50,1,4,4
CSV
"$PYTHON_BIN" "$REPO_ROOT/scripts/gen_sessions_manifest.py" --dataset "$DATASET" >/dev/null \
    || fail "gen_sessions_manifest failed"
SESSIONS_CSV="$DATASET/sessions.csv"
[[ -f "$SESSIONS_CSV" ]] || fail "sessions.csv not generated"
# 研究者の手記入を模す: 空 phase を pre に設定 (1 session のみ)。
"$PYTHON_BIN" - "$SESSIONS_CSV" <<'PY' || fail "phase fill failed"
import csv, sys
path = sys.argv[1]
with open(path, newline="", encoding="utf-8-sig") as fh:
    rows = list(csv.DictReader(fh))
for r in rows:
    if not (r.get("phase") or "").strip():
        r["phase"] = "pre"
with open(path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["participant_id", "session_id", "os", "phase"], lineterminator="\n")
    w.writeheader(); w.writerows(rows)
PY
step "  sessions.csv + survey/${PID}.csv ready"

# === Step 6: build_analysis_db (#6 DuckDB join → cross_section) ===
step "Step 6/6: build_analysis_db.py (DuckDB join)"
BUILD_OUT=""
if ! BUILD_OUT="$("$PYTHON_BIN" "$REPO_ROOT/scripts/build_analysis_db.py" \
        --dataset "$DATASET" --out "$WORK/analysis.db" --export-dir "$WORK" --format csv 2>&1)"; then
    echo "$BUILD_OUT" >&2
    fail "build_analysis_db failed (is duckdb installed? pip install -r scripts/requirements-dev.txt)"
fi
echo "$BUILD_OUT" | sed 's/^/  | /'
# build_analysis_db.py の OK 行 "cross_section rows=N" から行数を抽出する (出力フォーマット依存)。
# build 側の文言が変わると ROWS が空になり、下の assert が loud に fail する (サイレント素通りしない)。
ROWS="$(printf '%s\n' "$BUILD_OUT" | grep -oE 'cross_section rows=[0-9]+' | grep -oE '[0-9]+' || true)"
[[ -n "$ROWS" && "$ROWS" -gt 0 ]] || fail "cross_section has no rows (join produced nothing)"

# 出力 CSV に P900 の完全 join 行 (has_metrics=true, has_survey=true) があること。
EXPORT_CSV="$WORK/cross_section.csv"
[[ -f "$EXPORT_CSV" ]] || fail "cross_section.csv not exported"
grep -q "^${PID},pre,true,true" "$EXPORT_CSV" \
    || fail "expected fully-joined ${PID} pre row (has_metrics=true,has_survey=true) not found"

# プライバシー後始末確認: 復号平文・鍵が repo 配下に漏れていないこと。
# `\( ... \)` で -o をグループ化 (グループ化しないと暗黙 -print が後半 -name のみに付き検知漏れ)。
# target/ (ビルド生成物) は除外。資材はすべて $WORK (repo 外の mktemp) にあるので本来 0 件。
if find "$REPO_ROOT" -not -path '*/target/*' \
        \( -name "${PID}_*.ndjson" -o -name "${PID}_*.age" \) 2>/dev/null | grep -q .; then
    fail "leaked decrypted/age artifact under repo tree"
fi

echo
step "PASS ✅  end-to-end: package → unpack → metrics → sessions.csv → cross_section (${ROWS} row(s))"
