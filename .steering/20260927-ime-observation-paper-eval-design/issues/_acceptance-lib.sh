# issue の acceptance が共通で使う関数（source して使う・単体では実行しない）。
# ⚠️ cwd は worktree のルート。bash 3.2 で動くこと（変数は ${} で括る）。
# ⚠️ worker はこのファイルを変えない（どの issue の Allowed Files にも入っていない）。

K="papers/ime-observation/kit"
PY="python3"; command -v python3 >/dev/null 2>&1 || PY="python"
export PYTHONUTF8=1
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }
TMP="$(mktemp -d)"; trap 'rm -rf "${TMP}"' EXIT

# runs_on の検査。合わない OS では 2 で止める（★ 失敗ではなく「この機械で回すな」）。
require_os () {
  case "$1" in
    any) return 0 ;;
    macos) [ "$(uname -s)" = "Darwin" ] && return 0 ;;
    windows) case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) return 0 ;; esac ;;
  esac
  echo "  ⛔ runs_on=$1 の issue をこの OS ($(uname -s)) で検査している。_issue-plan.md の機械割り当てを見ること。"
  exit 2
}

need_file () { if [ -f "$1" ]; then ok "存在: $1"; else ng "無い: $1"; fi; }
need_grep () { # need_grep <file> <固定文字列> <説明>
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}
forbid_grep () { # forbid_grep <file> <拡張正規表現> <説明>
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qE -- "$2" "$1"; then ng "$3 (禁止パターンが在る: $2)"; else ok "$3"; fi
}
run_ok () { # run_ok <説明> <コマンド...>
  local d="$1"; shift
  if "$@" >"${TMP}/last.out" 2>&1; then ok "${d}"; else ng "${d}（exit≠0・末尾: $(tail -n 3 "${TMP}/last.out" | tr '\n' ' ')）"; fi
}
run_fail () { # run_fail <説明> <コマンド...>  ★ 陰性対照: 非 0 で終わるべき
  #   ⚠️ 道具が無い・例外で落ちた（Traceback / can't open file / panicked）は「拒否」と数えない（空振りの緑を防ぐ）。
  local d="$1"; shift
  if "$@" >"${TMP}/last.out" 2>&1; then ng "${d}（exit 0 で通ってしまった）"
  elif grep -qE "Traceback|can't open file|No such file|panicked at|command not found" "${TMP}/last.out"; then
    ng "${d}（拒否ではなく異常終了: $(grep -m 1 -E "Traceback|can't open file|No such file|panicked at|command not found" "${TMP}/last.out")）"
  else ok "${d}"; fi
}
run_exit () { # run_exit <期待する終了コード> <説明> <コマンド...>  ★ 異常終了は数えない
  local want="$1" d="$2" rc; shift 2
  "$@" >"${TMP}/last.out" 2>&1; rc=$?
  if grep -qE "Traceback|can't open file|No such file|panicked at|command not found" "${TMP}/last.out"; then
    ng "${d}（異常終了: $(grep -m 1 -E "Traceback|can't open file|No such file|panicked at|command not found" "${TMP}/last.out")）"
  elif [ "${rc}" -eq "${want}" ]; then ok "${d}"
  else ng "${d}（exit ${rc}・期待 ${want}）"; fi
}
selftest_ok () { # selftest_ok <py>  ★ 目印つきで --selftest が緑
  need_grep "$1" "# kit: selftest" "目印 '# kit: selftest': $1"
  run_ok "--selftest が緑: $1" "${PY}" "$1" --selftest
}

_base () {
  local r
  # ★ ローカルの base を先に見る（loop-spawn はローカルが先行していればローカルから切る・P1-J）。
  for r in feature/ime-eval-kit origin/feature/ime-eval-kit origin/main; do
    if git rev-parse -q --verify "${r}" >/dev/null 2>&1; then git merge-base HEAD "${r}" 2>/dev/null; return; fi
  done
}

# ⚠️ GSE 本体を変えていないこと（base からの差分に src-tauri/ src/ scripts/ .github/ が無い）。
forbid_gse_changes () {
  local base; base="$(_base)"
  if [ -z "${base}" ]; then ok "GUARD base が見つからない（検査を飛ばす）"; return; fi
  if git diff --name-only "${base}"..HEAD | grep -E '^(src-tauri|src|scripts|\.github)/' >/dev/null; then
    ng "GUARD GSE 本体（src-tauri/ src/ scripts/ .github/）を変えている"
  else ok "GUARD GSE 本体を変えていない"; fi
}

# ★ base からの差分が Allowed Files（拡張正規表現）だけであること。
#   issue ファイル自身（Status / Execution Result の更新）は許す。
#   ⚠️ issue ブランチの上で回すと意味を持つ。merge 後の枝では差分が空になり素通りする。
only_allowed () { # only_allowed <拡張正規表現>
  local base bad; base="$(_base)"
  if [ -z "${base}" ]; then ok "SCOPE base が見つからない（検査を飛ばす）"; return; fi
  bad="$(git diff --name-only "${base}"..HEAD | grep -vE -- "$1" | grep -vE '^\.steering/20260927-ime-observation-paper-eval-design/issues/[0-9]{3}\.md$' || true)"
  if [ -n "${bad}" ]; then ng "SCOPE Allowed Files の外を変えている: $(echo "${bad}" | tr '\n' ' ')"
  else ok "SCOPE 変更は Allowed Files の中だけ"; fi
}

check_entry_green () { run_ok "kit/check.sh が緑" bash "${K}/check.sh"; }

finish () {
  echo "  ---- 失敗 ${FAILS} 件 ----"
  [ "${FAILS}" -eq 0 ] || exit 1
  exit 0
}
