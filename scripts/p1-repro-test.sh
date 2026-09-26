#!/usr/bin/env bash
# ★ scripts/p1-repro.sh のテスト（issue 006）。偽の `gse-replay`（GSE_REPLAY_BIN）と合成の入力だけで回す。
#
# ⚠️ 見るもの:
#   1. 既定の `--stage pg1` が features / pg1_distribution.json / episodes.duckdb / provenance.json を出し、
#      provenance.json に決めたキーがすべてある（★ 値は独立に取り直して照合する）
#   2. ⚠️ 既定で格子を呼ばない（偽 gse-replay の呼び出し記録に `--set` が 1 度も無い）
#   3. ⚠️ `--stage search` は凍結 JSON（PG-1 未宣言）で exit 6 を返す。provenance.json は付けない
#   4. ガード（<workdir> が git 管理下 / 空でない / <ndjson-root> の中・レイアウト違反・引数）→ exit 2、
#      封筒の identity が食い違う → exit 3、段の失敗 → 非 0 で止まり次の段へ進まない
#
# ⚠️ duckdb 入りで走らせる（★ episode DB を作る段を skip しない。無ければ**赤にする**）。
# ⚠️ 実データは使わない・repo の中に何も書かない（★ 一時ディレクトリは repo の外）。
#
# Usage: bash scripts/p1-repro-test.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET="${SCRIPT_DIR}/p1-repro.sh"
FROZEN_JSON="${REPO_ROOT}/src-tauri/prereg/p1-episode.json"

PASS=0
FAIL=0
LOG=""
RC=0
ok() { PASS=$((PASS + 1)); echo "  ✅ $1"; }
ng() {
  FAIL=$((FAIL + 1)); echo "  ❌ $1"
  if [ -n "${LOG}" ] && [ -f "${LOG}" ]; then sed 's/^/       | /' "${LOG}" | tail -n 12; fi
}
check() { # check <説明> <コマンド...>（真なら ok）
  local desc="$1"
  shift
  if "$@" > /dev/null 2>&1; then ok "${desc}"; else ng "${desc}"; fi
}
expect_rc() { # expect_rc <説明> <期待する終了コード>（直前の run の結果）
  if [ "${RC}" -eq "$2" ]; then ok "$1 (exit $2)"; else ng "$1: exit ${RC}（期待 $2）"; fi
}
CASE=0
run() { # run <コマンド...> → RC と LOG（★ 出力は捕捉する）
  CASE=$((CASE + 1))
  LOG="${TMP}/log.${CASE}"
  "$@" > "${LOG}" 2>&1
  RC=$?
}

command -v jq > /dev/null 2>&1 || { echo "jq が無い"; exit 2; }
PY=""
for candidate in "${PYTHON:-}" python3 python; do
  [ -n "${candidate}" ] || continue
  if "${candidate}" -c 'import sys' > /dev/null 2>&1; then PY="${candidate}"; break; fi
done
[ -n "${PY}" ] || { echo "python が動かない"; exit 2; }
export PYTHONUTF8=1
"${PY}" -c 'import duckdb' > /dev/null 2>&1 || { echo "⚠️ duckdb が無い（★ 入れないと episode DB の段を検査できない。pip install duckdb）"; exit 2; }

TMP="$(mktemp -d)" || { echo "一時ディレクトリを作れない"; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

py_sha16() { "${PY}" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()[:16])' "$1"; }
py_sha64() { "${PY}" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
FROZEN_SHA16="$(py_sha16 "${FROZEN_JSON}" | tr -d '\r')"
LOCK_SHA64="$(py_sha64 "${REPO_ROOT}/src-tauri/Cargo.lock" | tr -d '\r')"
FROZEN_VERSION="$(jq -r '.version' "${FROZEN_JSON}" | tr -d '\r')"

# ── 偽の gse-replay ──────────────────────────────────────────────────
#   ★ `<session> --features --pole <極> [--set k=v ...]` を受け、p1_features_io の封筒の形を出す（onset 2 本）。
#   ★ 呼び出しを FAKE_LOG に 1 行ずつ記録する（格子を回したかの証拠）。
#   ★ 入力のファイル名で挙動を変える: *fail* = 失敗 / *hmmdrift* = hmm_version が違う / *preregdrift* = prereg_version が違う
FAKE="${TMP}/fake-gse-replay"
cat > "${FAKE}" <<'FAKE_EOF'
#!/usr/bin/env bash
in="$1"
echo "$(basename "$in") $*" >> "${FAKE_LOG:?}"
pole=""
shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --pole) pole="$2"; shift 2 ;;
    *) shift ;;
  esac
done
hmm="0.5.0"
prereg="${FAKE_PREREG_VERSION:?}"
case "$(basename "$in")" in
  *fail*) echo "fake gse-replay: boom" >&2; exit 1 ;;
  *hmmdrift*) hmm="9.9.9" ;;
  *preregdrift*) prereg="9.9.9" ;;
esac
jq -n --arg pole "$pole" --arg hmm "$hmm" --arg prereg "$prereg" --arg sha "${FAKE_PREREG_SHA:?}" '
def row($t; $t0): {
  t_ms: $t,
  activity: {key_count: 3, backspace_count: 1},
  boundary: {pauses: 1},
  dispersion: {pause_p50_ms: 2100, pause_p90_ms: 3000, pause_max_ms: 4000, iki_cv: 0.5},
  stall_onset: {
    is_onset: ($t0 != null),
    s_ms: (if $t0 == null then null else $t0 - 3000 end),
    t0_ms: $t0,
    theta_person_ms: (if $t0 == null then null else 2500 end),
    theta_sample_n: (if $t0 == null then null else 120 end),
    task_kind: (if $t0 == null then null else "writing" end),
    phase: "unspecified",
    ime_overlap: (if $t0 == null then null else true end)
  },
  quality: {missing_reasons: []},
  revision: {units_closed: 0},
  restart: {restop_ms: (if $t0 == null then null else 4000 end), stable_generation_ms: (if $t0 == null then null else 9000 end)}
};
{
  provenance: {tool: "gse-replay", source_basename: "synthetic.ndjson", hmm_version: "0.5.0"},
  config: {
    pole: $pole, pole_applicable: true, pole_not_applicable_reason: null,
    prereg_id: "p1-episode", prereg_version: $prereg, prereg_sha256_prefix: $sha,
    config_source: "frozen", overrides: [], hmm_version: $hmm
  },
  rows: [row(1700000000000; null), row(1700000001000; 1700000010000), row(1700000002000; null),
         row(1700000003000; 1700000020000), row(1700000004000; null)]
}'
FAKE_EOF
chmod +x "${FAKE}"
export GSE_REPLAY_BIN="${FAKE}"
export FAKE_LOG="${TMP}/fake.log"
export FAKE_PREREG_VERSION="${FROZEN_VERSION}"
export FAKE_PREREG_SHA="${FROZEN_SHA16}"
unset GSE_DATASET

# ── 合成の入力（★ 中身は偽の gse-replay が読まないので 1 行でよい）──
make_input() { # make_input <root> <P-ID>/<session>...
  local root="$1" rel
  shift
  for rel in "$@"; do
    mkdir -p "${root}/$(dirname "${rel}")"
    echo '{"synthetic":true}' > "${root}/${rel}.ndjson"
  done
}
ND="${TMP}/nd"
make_input "${ND}" P01/s1 P01/s2 P02/s1
fake_calls() { if [ -f "${FAKE_LOG}" ]; then grep -c . "${FAKE_LOG}"; else echo 0; fi; }

echo "=== p1-repro.sh のテスト（偽 gse-replay・duckdb 入り）==="

# ── 1. 既定 = --stage pg1 ─────────────────────────────────────────────
echo "── 1. 既定の stage は pg1（3 つの成果物と provenance.json）"
W1="${TMP}/w1"
run bash "${TARGET}" "${ND}" "${W1}"
expect_rc "既定の実行" 0
check "3 セッション × 3 極の封筒が features/ に出る" \
  test "$(find "${W1}/features" -name '*.json' | grep -c .)" -eq 9
check "pg1_distribution.json が出る" test -f "${W1}/pg1_distribution.json"
check "episodes.duckdb が出る" test -s "${W1}/episodes.duckdb"
check "provenance.json が出る" test -f "${W1}/provenance.json"
check "⚠️ 途中の一時ファイル・ロックが残らない" test -z "$(find "${W1}" -mindepth 1 -name '.*')"
PROV="${W1}/provenance.json"
check "provenance に決めたキーがすべてある" jq -e '
  (["tool","stage","started_utc","finished_utc","repo_commit","repo_clean","input_commit","input_commit_reason",
    "cargo_lock_sha256","frozen_json_sha256_prefix","hmm_version","prereg_version","search_seed",
    "n_participants","n_sessions"] - keys) == []' "${PROV}"
check "stage は pg1" jq -e '.stage == "pg1"' "${PROV}"
check "repo_commit は git rev-parse HEAD と一致" \
  jq -e --arg c "$(git -C "${REPO_ROOT}" rev-parse HEAD | tr -d '\r')" '.repo_commit == $c' "${PROV}"
check "repo_clean は真偽値" jq -e '.repo_clean | type == "boolean"' "${PROV}"
check "cargo_lock_sha256 は Cargo.lock の sha256（独立に計算）" jq -e --arg h "${LOCK_SHA64}" '.cargo_lock_sha256 == $h' "${PROV}"
check "frozen_json_sha256_prefix は凍結 JSON の先頭 16 桁（独立に計算）" \
  jq -e --arg h "${FROZEN_SHA16}" '.frozen_json_sha256_prefix == $h' "${PROV}"
check "hmm_version / prereg_version は封筒の値" \
  jq -e --arg p "${FROZEN_VERSION}" '.hmm_version == "0.5.0" and .prereg_version == $p' "${PROV}"
check "search_seed は凍結 JSON の search_protocol.seed" \
  jq -e --argjson s "$(jq -c '.search_protocol.seed' "${FROZEN_JSON}" | tr -d '\r')" '.search_seed == $s' "${PROV}"
check "n_participants=2 / n_sessions=3" jq -e '.n_participants == 2 and .n_sessions == 3' "${PROV}"
check "GSE_DATASET が無ければ input_commit は null で理由がある" \
  jq -e '.input_commit == null and (.input_commit_reason | type == "string" and length > 0)' "${PROV}"
check "開始・終了時刻は UTC・秒" \
  jq -e '(.started_utc | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")) and (.finished_utc | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"))' "${PROV}"
check "pg1_distribution.json は 3 極ぶんの分布" jq -e '.poles | keys | length == 3' "${W1}/pg1_distribution.json"

echo "── 2. ⚠️ 既定では格子を呼ばない"
check "偽 gse-replay に --set が 1 度も渡っていない（格子は --set を渡す）" test -z "$(grep -e '--set' "${FAKE_LOG}" || true)"
check "偽 gse-replay は 3 セッション × 3 極 = 9 回だけ呼ばれた" test "$(fake_calls)" -eq 9
check "grid/ も grid_manifest.json も無い" test -z "$(find "${W1}" -name 'grid*')"
check "select_table.json も無い" test ! -e "${W1}/select_table.json"

echo "── 2b. 入力の commit（GSE_DATASET は hash だけを読む）"
DS="${TMP}/dataset"
mkdir -p "${DS}"
git -C "${DS}" init -q
git -C "${DS}" -c user.name=t -c user.email=t@example.invalid commit -q --allow-empty -m init
W1B="${TMP}/w1b"
run env GSE_DATASET="${DS}" bash "${TARGET}" "${ND}" "${W1B}"
expect_rc "GSE_DATASET つきの実行" 0
check "input_commit は GSE_DATASET の HEAD・理由は null" \
  jq -e --arg c "$(git -C "${DS}" rev-parse HEAD | tr -d '\r')" '.input_commit == $c and .input_commit_reason == null' "${W1B}/provenance.json"

# ── 3. --stage search ─────────────────────────────────────────────────
echo "── 3. ⚠️ --stage search は PG-1 未宣言（凍結 JSON）で exit 6"
: > "${TMP}/labels.csv"
W3="${TMP}/w3"
run bash "${TARGET}" "${ND}" "${W3}" --stage search --labels "${TMP}/labels.csv"
expect_rc "凍結 JSON では PG-1 が宣言されていない" 6
check "⚠️ 格子は 1 度も回っていない（偽 gse-replay に --set が無い）" test -z "$(grep -e '--set' "${FAKE_LOG}" || true)"
check "grid/ が作られていない" test ! -e "${W3}/grid"
check "⚠️ 失敗した実行に provenance.json を付けない" test ! -e "${W3}/provenance.json"
run bash "${TARGET}" "${ND}" "${TMP}/w3b" --stage search
expect_rc "--stage search に --labels が無い" 2
check "作業ディレクトリを作らない" test ! -e "${TMP}/w3b"
run bash "${TARGET}" "${ND}" "${TMP}/w3c" --labels "${TMP}/labels.csv"
expect_rc "--stage pg1 に --labels（黙って無視しない）" 2
run bash "${TARGET}" "${ND}" "${TMP}/w3d" --stage search --labels "${TMP}/no-such.csv"
expect_rc "--labels を読めない" 2
run bash "${TARGET}" "${ND}" "${TMP}/w3e" --stage bogus
expect_rc "知らない --stage" 2
run bash "${TARGET}" "${ND}" "${TMP}/w3f" --stage pg1 --stage pg1
expect_rc "--stage の 2 回指定" 2
run bash "${TARGET}" "${ND}"
expect_rc "引数不足" 2
check "上のガードはどれも <workdir> を作らない" test -z "$(ls -d "${TMP}"/w3[b-f] 2>/dev/null || true)"

# ── 4. ガード ─────────────────────────────────────────────────────────
echo "── 4. ガード（<workdir> / <ndjson-root>）"
CALLS_BEFORE_GUARDS="$(fake_calls)"
mkdir -p "${TMP}/repo"
git -C "${TMP}/repo" init -q
run bash "${TARGET}" "${ND}" "${TMP}/repo/w"
expect_rc "<workdir> が git の作業ツリーの中" 2
check "⚠️ 作業ツリーの中に何も作らない" test ! -e "${TMP}/repo/w"
run bash "${TARGET}" "${ND}" "${TMP}/repo/a/b/w"
expect_rc "まだ無い深いパスでも、祖先が作業ツリーの中なら拒否" 2
check "⚠️ 深いパスも作らない" test ! -e "${TMP}/repo/a"
mkdir -p "${TMP}/full"
echo keep > "${TMP}/full/keep.txt"
run bash "${TARGET}" "${ND}" "${TMP}/full"
expect_rc "<workdir> が空でない" 2
check "既存のファイルに触らない・何も足さない" test "$(ls -A "${TMP}/full")" = "keep.txt"
run bash "${TARGET}" "${ND}" "${W1}"
expect_rc "成功済みの <workdir> の使い回し" 2
echo x > "${TMP}/afile"
run bash "${TARGET}" "${ND}" "${TMP}/afile"
expect_rc "<workdir> がファイル" 2
run bash "${TARGET}" "${TMP}/no-such-root" "${TMP}/w4a"
expect_rc "<ndjson-root> が無い" 2
BAD="${TMP}/bad"
make_input "${BAD}" P01/s1
echo stray > "${BAD}/P01/notes.txt"
run bash "${TARGET}" "${BAD}" "${TMP}/w4b"
expect_rc "<ndjson-root> のレイアウト違反（契約に無いエントリ）" 2
check "⚠️ レイアウト違反では <workdir> を作らない" test ! -e "${TMP}/w4b"
run bash "${TARGET}" "${ND}" "${ND}/out"
expect_rc "<workdir> が <ndjson-root> の中" 2
check "⚠️ 入力のディレクトリに何も作らない" test ! -e "${ND}/out"
run bash "${TARGET}" "${ND}" "${ND}/deep/er/out"
expect_rc "<workdir> が <ndjson-root> の 2 段以上下（まだ無い）" 2
check "⚠️ 2 段以上下でも入力のディレクトリに中間の階層を残さない" test ! -e "${ND}/deep"
make_input "${TMP}/nd4d" P01/s1
mkdir "${TMP}/nd4d/P02"
run bash "${TARGET}" "${TMP}/nd4d" "${TMP}/nd4d/P02"
expect_rc "<workdir> が <ndjson-root> の中の既存の空ディレクトリ（P-ID の形）" 2
check "⚠️ 利用者の既存の空ディレクトリを消さない（rmdir しない）" test -d "${TMP}/nd4d/P02"
run bash "${TARGET}" "${ND}" "${TMP}/w4d/new/../w4e"
expect_rc "まだ無い <workdir> が '..' を含む" 2
check "⚠️ '..' を含む未作成の <workdir> では何も作らない" test ! -e "${TMP}/w4d"
mkdir -p "${TMP}/empty-root"
run bash "${TARGET}" "${TMP}/empty-root" "${TMP}/w4c"
expect_rc "セッションが 1 つも無い <ndjson-root>" 2
check "⚠️ どのガードも副作用の前に止まる（偽 gse-replay は 1 度も呼ばれていない）" \
  test "$(fake_calls)" -eq "${CALLS_BEFORE_GUARDS}"

# ── 5. 封筒の identity ────────────────────────────────────────────────
echo "── 5. ⚠️ 封筒の identity が食い違ったら exit 3"
make_input "${TMP}/nd5" P01/a P01/b_hmmdrift
run bash "${TARGET}" "${TMP}/nd5" "${TMP}/w5a"
expect_rc "セッション間で hmm_version が違う" 3
check "hmm_version の食い違いを言う" grep -q 'hmm_version' "${LOG}"
check "⚠️ 分布にも DB にも進まない" test ! -e "${TMP}/w5a/pg1_distribution.json" -a ! -e "${TMP}/w5a/episodes.duckdb"
check "provenance.json を付けない" test ! -e "${TMP}/w5a/provenance.json"
make_input "${TMP}/nd5b" P01/a P01/b_preregdrift
run bash "${TARGET}" "${TMP}/nd5b" "${TMP}/w5b"
expect_rc "セッション間で prereg_version が違う" 3
run env FAKE_PREREG_SHA=deadbeefdeadbeef bash "${TARGET}" "${ND}" "${TMP}/w5c"
expect_rc "封筒の凍結 JSON の hash が repo の凍結 JSON と違う（古い binary）" 3
check "⚠️ 古い binary では分布に進まない" test ! -e "${TMP}/w5c/pg1_distribution.json"

# ── 6. 段の失敗は次へ進まない ──────────────────────────────────────────
echo "── 6. ⚠️ 段の失敗は非 0 で止まり、次の段へ進まない"
make_input "${TMP}/nd6" P01/a P01/b_fail P02/c
BEFORE="$(fake_calls)"
run bash "${TARGET}" "${TMP}/nd6" "${TMP}/w6"
expect_rc "3 極スクリプトが失敗するセッションがある" 1
check "失敗したセッションより後ろの参加者は回していない" test ! -e "${TMP}/w6/features/P02"
check "⚠️ 分布にも DB にも進まない" test ! -e "${TMP}/w6/pg1_distribution.json" -a ! -e "${TMP}/w6/episodes.duckdb"
check "provenance.json を付けない" test ! -e "${TMP}/w6/provenance.json"
check "失敗までに偽 gse-replay が呼ばれた（a の 3 極 + b_fail の 1 回）" test "$(( $(fake_calls) - BEFORE ))" -eq 4

echo "────────────────────────────────────────"
echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
if [ "${FAIL}" -eq 0 ]; then
  echo "  ✅ p1-repro.sh のテストは緑"
  exit 0
fi
echo "  ❌ 上の ❌ を直すこと"
exit 1
