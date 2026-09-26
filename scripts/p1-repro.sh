#!/usr/bin/env bash
# ★ P1 の再現を 1 コマンドで回す（issue 006・`reproducibility-discipline` ルール 4）。
#
# ⚠️★★★ 既定では **PG-1 の手前で止まる**（事前宣言 docs/preregistration-p1-episode.md §2.3）:
#   PG-1 は「一人あたり episode 数の下限」を、探索を 1 度も回す前に宣言するゲートである。
#   → 既定の `--stage pg1` は **3 極 → 参加者ごとの episode 数の分布 → episode DB** までで止まり、
#     格子（`p1_run_grid.py`）も選択（`p1_select.py`）も**呼ばない**。
#   ★ 分布を見て PG-1 を宣言（凍結 JSON の新版）してから、はじめて `--stage search` を回す。
#   ⚠️ PG-1 が宣言されていなければ `--stage search` は `p1_run_grid.py` の **exit 6 をそのまま返す**（握りつぶさない）。
#
# Usage:
#   bash scripts/p1-repro.sh <ndjson-root> <workdir> [--stage pg1|search] [--labels CSV]
#     <ndjson-root> = <P-ID>/<session>.ndjson を並べたディレクトリ（★ p1_run_grid.py と同じレイアウト・同じ検査）
#     <workdir>     = 成果物の置き場。⚠️ repo の外・空か未作成（★ 特徴行は共有禁止）
#     --stage pg1    （既定）3 極 → p1_pg1_distribution.py → build_p1_episode_db.py。ここで止まる
#     --stage search 上に続けて p1_run_grid.py → p1_select.py。⚠️ --labels 必須（転帰 CSV・外から渡す）
#   GSE_REPLAY_BIN=src-tauri/target/release/gse-replay bash scripts/p1-repro.sh <ndjson-root> <workdir>
#     ★ 長いセッションは release で。⚠️ 相対パスは呼び出し元の cwd から解決する。
#   GSE_DATASET=<gse-dataset のクローン> … 入力の commit（★ `git rev-parse HEAD` の hash だけを読む。中身は開かない）。
#
# 出力（<workdir> の直下）:
#   features/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json   3 極の封筒（中間成果物・共有しない）
#   pg1_distribution.json                                                   PG-1 に渡す分布（★ これだけを見る）
#   episodes.duckdb                                                         episode DB（使い捨て・共有しない）
#   grid/ ・ select_table.json                                              （--stage search のみ）
#   provenance.json                                                         刻印（★ 成功した実行にだけ付く）
#
# provenance.json のキー:
#   tool / stage / started_utc / finished_utc（UTC・秒）
#   repo_commit（実行の開始時の `git rev-parse HEAD`）/ repo_clean（★ 実行の**終了時**の作業ツリー。未追跡も数える）
#   input_commit（GSE_DATASET の HEAD。無ければ null）/ input_commit_reason（null でないときの理由。それ以外は null）
#   cargo_lock_sha256（src-tauri/Cargo.lock・終了時）/ frozen_json_sha256_prefix（src-tauri/prereg/p1-episode.json の先頭 16 桁）
#   hmm_version / prereg_version（封筒 config から。⚠️ 全セッション・全極で 1 通りでなければ exit 3）
#   search_seed（凍結 JSON の search_protocol.seed）/ n_participants / n_sessions
#
# ⚠️ fail-closed:
#   - どの段でも失敗したら**その段の終了コードで止まり、次の段へ進まない**（★ 各段の終了コードはそのまま返す）。
#   - ⚠️ 失敗した実行には **provenance.json を付けない**（★ provenance.json の無い <workdir> は完了していない残骸。
#     結果として読まない・使い回さない。診断のため成果物は消さない）。
#   - ⚠️ 封筒の `config.prereg_sha256_prefix`（★ 実行した gse-replay に埋め込まれた凍結 JSON の hash）が、
#     いま repo にある凍結 JSON の hash と食い違うなら exit 3（★ 古い binary で作った特徴を、別の凍結値の刻印で出さない）。
#
# Exit: 0 = 成功 / 1 = 環境が足りない（jq・git・python・sha256 が無い・git の commit を取れない）／ 3 = 封筒の identity が食い違う /
#       2 = 引数・入力・出力先のガード（<workdir> が git の作業ツリーの中・空でない・<ndjson-root> の中・
#           <ndjson-root> のレイアウト違反・--labels の不備）/
#       それ以外（4 / 5 / 6 …）= 各段の終了コードそのまま（★ 6 = PG-1 未宣言）
#
# 関連: docs/verification-runbook.md ／ scripts/templates/p1-experiment/README.md ／ .steering/20260926-p1-main-prep/
set -uo pipefail

USAGE="usage: bash scripts/p1-repro.sh <ndjson-root> <workdir> [--stage pg1|search] [--labels CSV]"
reject() { echo "[p1-repro] NG: $*" >&2; exit 2; }
die() { echo "[p1-repro] NG: $*" >&2; exit 1; }

# ── 引数 ─────────────────────────────────────────────────────────────
if [ "$#" -lt 2 ]; then
  echo "${USAGE}" >&2
  exit 2
fi
NDJSON_ROOT="$1"
WORKDIR="$2"
shift 2
STAGE="pg1"; STAGE_SET=0
LABELS=""; LABELS_SET=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --stage)
      [ "$#" -ge 2 ] || reject "'--stage' に値が続いていない"
      [ "${STAGE_SET}" -eq 0 ] || reject "'--stage' が 2 回指定されている"
      STAGE_SET=1; STAGE="$2"; shift 2 ;;
    --labels)
      [ "$#" -ge 2 ] || reject "'--labels' に値が続いていない"
      [ "${LABELS_SET}" -eq 0 ] || reject "'--labels' が 2 回指定されている"
      LABELS_SET=1; LABELS="$2"; shift 2 ;;
    *)
      echo "${USAGE}" >&2
      exit 2 ;;
  esac
done
case "${STAGE}" in
  pg1|search) ;;
  *) reject "--stage は pg1 か search（実際: '${STAGE}'）" ;;
esac
if [ "${STAGE}" = "pg1" ] && [ "${LABELS_SET}" -eq 1 ]; then
  reject "--labels は --stage search でだけ使う（★ pg1 は転帰を見ない。黙って無視すると search を回したと誤読される）"
fi
if [ "${STAGE}" = "search" ]; then
  [ "${LABELS_SET}" -eq 1 ] || reject "--stage search には --labels <転帰 CSV> が要る"
  { [ -n "${LABELS}" ] && [ -r "${LABELS}" ] && [ ! -d "${LABELS}" ]; } || reject "--labels を読めない: '${LABELS}'"
fi
[ -n "${NDJSON_ROOT}" ] || reject "<ndjson-root> が空文字（★ 変数が未設定のまま展開されていないか）"
[ -n "${WORKDIR}" ] || reject "<workdir> が空文字（★ 変数が未設定のまま展開されていないか）"
[ -d "${NDJSON_ROOT}" ] || reject "<ndjson-root> がディレクトリでない: ${NDJSON_ROOT}"

# ── 道具 ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FROZEN_JSON="${REPO_ROOT}/src-tauri/prereg/p1-episode.json"
CARGO_LOCK="${REPO_ROOT}/src-tauri/Cargo.lock"

command -v jq >/dev/null 2>&1 || die "jq が無い（★ 封筒の照合と provenance.json の組み立てに使う）"
command -v git >/dev/null 2>&1 || die "git が無い（★ commit の刻印と <workdir> の git 判定に使う）"
PY=""
if [ -n "${PYTHON:-}" ]; then
  "${PYTHON}" -c 'import sys' >/dev/null 2>&1 && PY="${PYTHON}"
else
  for candidate in python3 python; do
    if "${candidate}" -c 'import sys' >/dev/null 2>&1; then PY="${candidate}"; break; fi
  done
fi
[ -n "${PY}" ] || die "python が動かない（★ PYTHON=<実行ファイル> で指定できる）"
# ★ Windows コンソールは cp932。P1 の Python 部品は日本語を出す
export PYTHONUTF8=1

sha256_of() { # sha256_of <file> → 16 進 64 桁だけを標準出力へ
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    return 1
  fi
}
[ -f "${FROZEN_JSON}" ] || die "凍結 JSON が無い: ${FROZEN_JSON}"
[ -f "${CARGO_LOCK}" ] || die "Cargo.lock が無い: ${CARGO_LOCK}"
FROZEN_SHA16="$(sha256_of "${FROZEN_JSON}" | cut -c1-16)"
[ "${#FROZEN_SHA16}" -eq 16 ] || die "凍結 JSON の sha256 を取れない（sha256sum / shasum が無い）"
SEED="$(jq -c '.search_protocol.seed // null' "${FROZEN_JSON}" | tr -d '\r')" || die "凍結 JSON から seed を読めない"

REPO_COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null)" || die "repo の commit を取れない（★ git の作業ツリーで実行すること）"

# ── <workdir> のガード（★ 副作用の前に済ませる）─────────────────────────
#   git の管理下なら拒否（★ 特徴行は共有禁止 (sharing: prohibited)。repo 内に書くと git add で stage されうる）。
#   ⚠️ 判定が「not a git repository」以外のエラーで失敗したら、管理外と見なさず拒否する（fail-closed）。
#   ★ まだ無い <workdir> は、実在する最も近い祖先で判定する（祖先が作業ツリーの中なら、その下も中）。
if [ -e "${WORKDIR}" ] && [ ! -d "${WORKDIR}" ]; then
  reject "<workdir> がディレクトリでない: ${WORKDIR}"
fi
PROBE="${WORKDIR}"
while [ ! -d "${PROBE}" ]; do
  PARENT="$(dirname "${PROBE}")"
  [ "${PARENT}" != "${PROBE}" ] || break
  PROBE="${PARENT}"
done
[ -d "${PROBE}" ] || reject "<workdir> の祖先にディレクトリが無い: ${WORKDIR}"
GIT_CHECK_ERR="$(env -u GIT_DIR -u GIT_WORK_TREE -u GIT_CEILING_DIRECTORIES LC_ALL=C LANGUAGE=C \
  git -C "${PROBE}" rev-parse --is-inside-work-tree 2>&1 1>/dev/null)"
GIT_CHECK_RC=$?
if [ "${GIT_CHECK_RC}" -eq 0 ]; then
  reject "<workdir> が git 管理下: ${WORKDIR}（★ 特徴行は共有禁止。<workdir> は repo の外に置く）"
fi
case "${GIT_CHECK_ERR}" in
  *"not a git repository"*) ;;
  *) reject "<workdir> の git 判定がエラー（'not a git repository' 以外・★ 管理外として素通りさせない）: ${GIT_CHECK_ERR}" ;;
esac
if [ -d "${WORKDIR}" ] && [ -n "$(ls -A "${WORKDIR}" 2>&1)" ]; then
  reject "<workdir> が空でない: ${WORKDIR}（★ 使い回し拒否。空のディレクトリか、まだ無いパスを指定する）"
fi

# ── 入力（★ p1_run_grid.py と同じ list_sessions を使う。--stage search が見る集合と食い違わない）──
NDJSON_ABS="$(cd "${NDJSON_ROOT}" && pwd -P)"
IFS= read -r -d '' LIST_PY <<'PY' || true
import sys

sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # ★ Windows の既定は CRLF。bash の read に \r が混ざる
sys.path.insert(0, sys.argv[1])
import p1_run_grid as grid

try:
    sessions = grid.list_sessions(sys.argv[2])
except grid.GuardError as e:
    grid._emit(sys.stderr, "[p1-repro] NG (layout): %s" % e)
    sys.exit(2)
for participant, session, _ in sessions:
    sys.stdout.write("%s\t%s\n" % (participant, session))
PY
SESSIONS="$("${PY}" -c "${LIST_PY}" "${SCRIPT_DIR}" "${NDJSON_ABS}")"
LIST_RC=$?
[ "${LIST_RC}" -eq 0 ] || exit "${LIST_RC}"
[ -n "${SESSIONS}" ] || reject "セッションが 1 つも無い: ${NDJSON_ROOT}"
N_SESSIONS="$(printf '%s\n' "${SESSIONS}" | grep -c .)"
N_PARTICIPANTS="$(printf '%s\n' "${SESSIONS}" | cut -f1 | sort -u | grep -c .)"

# ── 入力の commit（★ hash だけを読む。gse-dataset の中身は開かない）──
INPUT_COMMIT=""
INPUT_REASON=""
if [ -z "${GSE_DATASET:-}" ]; then
  INPUT_REASON="GSE_DATASET が未設定"
elif [ ! -d "${GSE_DATASET}" ]; then
  INPUT_REASON="GSE_DATASET がディレクトリでない"
elif ! INPUT_COMMIT="$(git -C "${GSE_DATASET}" rev-parse HEAD 2>/dev/null)"; then
  INPUT_COMMIT=""
  INPUT_REASON="GSE_DATASET で git rev-parse HEAD が失敗した（git のクローンでない）"
fi

# ── ここから副作用 ───────────────────────────────────────────────────
mkdir -p "${WORKDIR}" || die "<workdir> を作れない: ${WORKDIR}"
WORK_ABS="$(cd "${WORKDIR}" && pwd -P)"
# ⚠️ <workdir> が <ndjson-root> の中だと、入力のディレクトリに成果物を撒く（search 段は入力のレイアウト違反で落ちる）
case "${WORK_ABS}/" in
  "${NDJSON_ABS}/"*)
    rmdir "${WORK_ABS}" 2>/dev/null
    reject "<workdir> が <ndjson-root> の中: ${WORK_ABS}（★ 入力のディレクトリに成果物を置かない）" ;;
esac
START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[p1-repro] stage=${STAGE} sessions=${N_SESSIONS} participants=${N_PARTICIPANTS} → ${WORK_ABS}"

run_step() { # run_step <名前> <コマンド...> ★ 失敗したらその終了コードで止まる（次の段へ進まない）
  local name="$1" rc
  shift
  # ★ stdin は切る（⚠️ 下の while は here-string を stdin にしているので、子が読むと残りのセッションが消える）
  "$@" < /dev/null
  rc=$?
  if [ "${rc}" -ne 0 ]; then
    echo "[p1-repro] NG: ${name} が exit ${rc}（★ 次の段へ進まない。provenance.json は付けない）" >&2
    exit "${rc}"
  fi
}

# ── 1. 3 極（★ 1 セッション 1 回・凍結既定のまま）───────────────────────
FEATURES="${WORK_ABS}/features"
mkdir -p "${FEATURES}" || die "features/ を作れない"
while IFS=$'\t' read -r PARTICIPANT SESSION; do
  [ -n "${PARTICIPANT}" ] || continue
  run_step "run-features-all-poles (${PARTICIPANT}/${SESSION})" \
    bash "${SCRIPT_DIR}/run-features-all-poles.sh" \
    "${NDJSON_ABS}/${PARTICIPANT}/${SESSION}.ndjson" "${FEATURES}/${PARTICIPANT}/${SESSION}"
done <<< "${SESSIONS}"

# ── 2. 封筒の identity（★ 全セッション・全極で 1 通り。repo の凍結 JSON とも一致）──
IFS= read -r -d '' IDENTITY_PY <<'PY' || true
import sys

sys.stdout.reconfigure(encoding="utf-8", newline="\n")
sys.path.insert(0, sys.argv[1])
import p1_features_io as fio

identities = set()
try:
    for _participant, _session, paths in fio.discover(sys.argv[2]):
        for envelope in fio.load_session(paths).values():
            config = envelope["config"]
            identities.add((config["hmm_version"], config["prereg_version"], config["prereg_sha256_prefix"]))
except fio.FeaturesIOError as e:
    sys.stderr.write("[p1-repro] NG (envelope): %s\n" % e)
    sys.exit(3)
for identity in sorted(identities):
    sys.stdout.write("\t".join(identity) + "\n")
PY
IDENTITY="$("${PY}" -c "${IDENTITY_PY}" "${SCRIPT_DIR}" "${FEATURES}")"
IDENTITY_RC=$?
[ "${IDENTITY_RC}" -eq 0 ] || exit "${IDENTITY_RC}"
if [ "$(printf '%s\n' "${IDENTITY}" | grep -c .)" -ne 1 ]; then
  {
    echo "[p1-repro] NG: 封筒の (hmm_version prereg_version prereg_sha256_prefix) が 1 通りでない（★ 別々の binary・別の凍結値が混ざっている）:"
    printf '%s\n' "${IDENTITY}" | tr '\t' ' ' | sed 's/^/    /'
  } >&2
  exit 3
fi
IFS=$'\t' read -r HMM_VERSION PREREG_VERSION ENVELOPE_SHA <<< "${IDENTITY}"
if [ "${ENVELOPE_SHA}" != "${FROZEN_SHA16}" ]; then
  echo "[p1-repro] NG: 封筒の prereg_sha256_prefix (${ENVELOPE_SHA}) が repo の凍結 JSON の hash (${FROZEN_SHA16}) と食い違う（★ 古い binary。gse-replay を作り直す）" >&2
  exit 3
fi

# ── 3. PG-1 に渡す分布 → 4. episode DB（★ ここで止まる）─────────────────
run_step "p1_pg1_distribution" \
  "${PY}" "${SCRIPT_DIR}/p1_pg1_distribution.py" --root "${FEATURES}" --out "${WORK_ABS}/pg1_distribution.json"
run_step "build_p1_episode_db" \
  "${PY}" "${SCRIPT_DIR}/build_p1_episode_db.py" --root "${FEATURES}" --out "${WORK_ABS}/episodes.duckdb"

# ── 5. 格子 → 選択の素の表（★ --stage search のみ。PG-1 未宣言なら p1_run_grid.py が exit 6 で止める）──
if [ "${STAGE}" = "search" ]; then
  run_step "p1_run_grid" \
    "${PY}" "${SCRIPT_DIR}/p1_run_grid.py" --ndjson-root "${NDJSON_ABS}" --out "${WORK_ABS}/grid"
  run_step "p1_select" \
    "${PY}" "${SCRIPT_DIR}/p1_select.py" --grid-out "${WORK_ABS}/grid" --labels "${LABELS}" --out "${WORK_ABS}/select_table.json"
fi

# ── 刻印（★ 成功した実行だけ）────────────────────────────────────────
REPO_STATUS="$(git -C "${REPO_ROOT}" status --porcelain --untracked-files=all 2>&1)" || die "git status が失敗した: ${REPO_STATUS}"
REPO_CLEAN=true
[ -z "${REPO_STATUS}" ] || REPO_CLEAN=false
LOCK_SHA="$(sha256_of "${CARGO_LOCK}")" || die "Cargo.lock の sha256 を取れない"
END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PROVENANCE_TMP="${WORK_ABS}/.provenance.json.tmp"
jq -n \
  --arg stage "${STAGE}" --arg started "${START_UTC}" --arg finished "${END_UTC}" \
  --arg repo_commit "${REPO_COMMIT}" --argjson repo_clean "${REPO_CLEAN}" \
  --arg input_commit "${INPUT_COMMIT}" --arg input_reason "${INPUT_REASON}" \
  --arg lock "${LOCK_SHA}" --arg frozen "${FROZEN_SHA16}" \
  --arg hmm "${HMM_VERSION}" --arg prereg "${PREREG_VERSION}" \
  --argjson seed "${SEED}" --argjson n_participants "${N_PARTICIPANTS}" --argjson n_sessions "${N_SESSIONS}" \
  '{
    tool: "p1-repro", stage: $stage, started_utc: $started, finished_utc: $finished,
    repo_commit: $repo_commit, repo_clean: $repo_clean,
    input_commit: (if $input_commit == "" then null else $input_commit end),
    input_commit_reason: (if $input_commit == "" then $input_reason else null end),
    cargo_lock_sha256: $lock, frozen_json_sha256_prefix: $frozen,
    hmm_version: $hmm, prereg_version: $prereg, search_seed: $seed,
    n_participants: $n_participants, n_sessions: $n_sessions
  }' > "${PROVENANCE_TMP}" \
  && mv -f "${PROVENANCE_TMP}" "${WORK_ABS}/provenance.json" \
  || { rm -f "${PROVENANCE_TMP}"; die "provenance.json を書けない"; }

echo "[p1-repro] OK: stage=${STAGE} → ${WORK_ABS}"
if [ "${STAGE}" = "pg1" ]; then
  echo "[p1-repro] ★ PG-1 の手前で止まった。pg1_distribution.json の分布だけを見て PG-1 を宣言（凍結 JSON の新版）してから --stage search を回す"
fi
