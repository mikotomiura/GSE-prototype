#!/usr/bin/env bash
# kit/check.sh — 論文キットの検証の入口（ループの verify の test / typecheck）。
#
#   bash kit/check.sh              既定: kit/ 配下で「# kit: selftest」を含む .py を全部探し、
#                                  python3 <file> --selftest を順に回す。1 本でも赤なら exit 1。
#                                  ⚠️ 1 本も見つからなければ exit 1（空振りの緑を出さない）。
#   bash kit/check.sh --compile    kit/ 配下の全 .py を python3 -m py_compile（0 本なら exit 1）。
#   bash kit/check.sh --self-test  この入口自身の陰性対照。緑になる / 赤になる selftest を一時ディレクトリに
#                                  作り、入口が赤を赤として返す（空振りを緑にしない）ことを確かめる。
#
# ★ 規則（後続の selftest を書く人へ）: この入口は verify で毎回、各 acceptance でも回る。
#   selftest は**速い既定**で書くこと（1 本 30 秒以内）。重い検査は `--selftest --full` などに分け、
#   既定では回さない。1 本が 30 秒を超えたら警告を出す（止めはしない）。
#
# 環境変数: KIT_SLOW_SECONDS=警告の閾値（既定 30・--self-test が警告を確かめるために使う）
# Exit: 0 = 緑 / 1 = 赤（または 0 本の空振り） / 2 = 使い方の誤り・python が無い
#
# ⚠️ bash 3.2（macOS 標準）で動くこと: 変数は必ず ${VAR} で括る（多バイト文字の直前に括らない
#    変数を置くと、bash 3.2 は「変数名 ＋ 文字のバイト」を 1 つの名前として読んで落ちる）。
#    配列・mapfile は使わない（set -u で空配列が落ちる版がある）。
set -u

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="selftests"
SLOW="${KIT_SLOW_SECONDS:-30}"
MARK="# kit: selftest"

while [ $# -gt 0 ]; do
  case "$1" in
    --compile) MODE="compile" ;;
    --self-test) MODE="entry-selftest" ;;
    --root)
      if [ $# -lt 2 ]; then echo "check.sh: --root にはディレクトリが要る" >&2; exit 2; fi
      ROOT="$2"; shift ;;
    -h|--help) sed -n '2,22p' "${SELF}"; exit 0 ;;
    *) echo "check.sh: 未知の引数: ${1}（--compile / --self-test / --root DIR）" >&2; exit 2 ;;
  esac
  shift
done

export PYTHONUTF8=1
PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "${PY}" >/dev/null 2>&1; then
  echo "check.sh: python3 も python も無い（検査できない）" >&2
  exit 2
fi

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

# kit/ 配下の .py を安定した順序で列挙する（生成物のディレクトリは見ない）。
list_py () { # list_py <root>
  find "$1" -type f -name '*.py' \
    -not -path '*/__pycache__/*' -not -path '*/target/*' -not -path '*/.build/*' \
    2>/dev/null | LC_ALL=C sort
}

run_selftests () { # run_selftests <root>  ★ 緑 0 / 赤 1
  local root="$1" f t0 dt total=0 failed=0 out
  list_py "${root}" > "${WORK}/py.list"
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    grep -qF -- "${MARK}" "${f}" || continue
    total=$((total + 1))
    out="${WORK}/out.${total}"
    t0="${SECONDS}"
    if "${PY}" "${f}" --selftest > "${out}" 2>&1; then
      dt=$((SECONDS - t0))
      echo "  ✅ ${f#${root}/}（${dt} 秒）"
    else
      dt=$((SECONDS - t0))
      failed=$((failed + 1))
      echo "  ❌ ${f#${root}/}（${dt} 秒）"
      tail -n 20 "${out}" | sed 's/^/       /'
    fi
    if [ "${dt}" -gt "${SLOW}" ]; then
      echo "  ⚠️ ${f#${root}/} が ${dt} 秒かかった（${SLOW} 秒超）。重い検査は --selftest --full などに分け、既定を速くすること"
    fi
  done < "${WORK}/py.list"
  if [ "${total}" -eq 0 ]; then
    echo "  ❌ '${MARK}' を含む .py が 1 本も無い（★ 空振りの緑は出さない）: ${root}"
    return 1
  fi
  if [ "${failed}" -ne 0 ]; then
    echo "  ---- selftest ${total} 本中 ${failed} 本が赤 ----"
    return 1
  fi
  echo "  ---- selftest ${total} 本すべて緑 ----"
  return 0
}

run_compile () { # run_compile <root>
  local root="$1" f total=0 failed=0
  list_py "${root}" > "${WORK}/py.list"
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    total=$((total + 1))
    # ★ 出力先を一時ディレクトリに逃がす（__pycache__ を repo に残さない）
    if ! PYTHONPYCACHEPREFIX="${WORK}/pyc" "${PY}" -m py_compile "${f}" > "${WORK}/compile.out" 2>&1; then
      failed=$((failed + 1))
      echo "  ❌ ${f#${root}/}"
      tail -n 10 "${WORK}/compile.out" | sed 's/^/       /'
    fi
  done < "${WORK}/py.list"
  if [ "${total}" -eq 0 ]; then
    echo "  ❌ .py が 1 本も無い（★ 空振りの緑は出さない）: ${root}"
    return 1
  fi
  if [ "${failed}" -ne 0 ]; then
    echo "  ---- compile ${total} 本中 ${failed} 本が赤 ----"
    return 1
  fi
  echo "  ---- compile ${total} 本すべて緑 ----"
  return 0
}

# --- --self-test: 入口が「赤を赤として」返すことを確かめる（陰性対照） ---------------------
ST_FAILS=0
st_ng () { echo "  ❌ ${1}"; ST_FAILS=$((ST_FAILS + 1)); }
st_ok () { echo "  ✅ ${1}"; }
# st_expect <期待する exit code> <説明> <引数...>  ★ 入口を別の root に向けて回す
st_expect () {
  local want="$1" desc="$2" rc; shift 2
  bash "${SELF}" "$@" > "${WORK}/st.out" 2>&1; rc=$?
  if [ "${rc}" -eq "${want}" ]; then st_ok "${desc}（exit ${rc}）"
  else st_ng "${desc}（期待 exit ${want}・実際 ${rc}）: $(tail -n 3 "${WORK}/st.out" | tr '\n' ' ')"; fi
}
st_expect_out () { # st_expect_out <固定文字列> <説明>  ★ 直前の st_expect の出力に含まれること
  if grep -qF -- "$1" "${WORK}/st.out"; then st_ok "$2"; else st_ng "$2（出力に無い: $1）"; fi
}

entry_selftest () {
  local T="${WORK}/st"
  mkdir -p "${T}/green/sub" "${T}/red" "${T}/nomark" "${T}/empty" "${T}/broken" "${T}/slow" "${T}/ignored/target"
  printf '# kit: selftest\nimport sys\nsys.exit(0)\n' > "${T}/green/a.py"
  printf '# kit: selftest\nimport sys\nsys.exit(0)\n' > "${T}/green/sub/b.py"
  cp "${T}/green/a.py" "${T}/red/a.py"
  printf '# kit: selftest\nimport sys\nprint("boom")\nsys.exit(1)\n' > "${T}/red/bad_selftest.py"
  printf 'import sys\nsys.exit(0)\n' > "${T}/nomark/plain.py"
  printf '# kit: selftest\nthis is not python (\n' > "${T}/broken/syntax.py"
  printf '# kit: selftest\nimport time\ntime.sleep(2)\n' > "${T}/slow/slow.py"
  # target/ 配下は見ない（赤くなる selftest があっても無視される）
  printf '# kit: selftest\nimport sys\nsys.exit(1)\n' > "${T}/ignored/target/x.py"
  printf '# kit: selftest\nimport sys\nsys.exit(0)\n' > "${T}/ignored/ok.py"

  echo "=== 入口の陰性対照 ==="
  st_expect 0 "緑の selftest だけなら緑" --root "${T}/green"
  st_expect 1 "赤の selftest が 1 本あれば赤" --root "${T}/red"
  st_expect_out "bad_selftest.py" "赤になった selftest の名前が出る"
  st_expect_out "boom" "赤になった selftest の出力が出る"
  st_expect 1 "目印の無い .py だけなら空振りで赤" --root "${T}/nomark"
  st_expect 1 ".py が 1 本も無ければ空振りで赤" --root "${T}/empty"
  st_expect 0 "target/ 配下の赤い selftest は見ない" --root "${T}/ignored"
  st_expect 0 "遅い selftest は警告だけで止めない" --root "${T}/slow"
  KIT_SLOW_SECONDS=1 bash "${SELF}" --root "${T}/slow" > "${WORK}/st.out" 2>&1
  st_expect_out "秒超" "閾値を超えたら警告が出る（KIT_SLOW_SECONDS=1）"
  st_expect 0 "--compile: 構文が正しければ緑" --compile --root "${T}/green"
  st_expect 1 "--compile: 構文エラーがあれば赤" --compile --root "${T}/broken"
  st_expect 1 "--compile: .py が 0 本なら空振りで赤" --compile --root "${T}/empty"
  st_expect 2 "未知の引数は exit 2" --bogus
  st_expect 2 "--root の値が無ければ exit 2" --root

  # ★ 実物の kit/ に対して: 目印つきの .py が 1 本以上ある（この入口が空振りしていない）
  if [ "${ROOT}" = "$(cd "$(dirname "${SELF}")" && pwd)" ]; then
    list_py "${ROOT}" > "${WORK}/py.list"
    n=0
    while IFS= read -r f; do
      [ -n "${f}" ] && grep -qF -- "${MARK}" "${f}" && n=$((n + 1))
    done < "${WORK}/py.list"
    if [ "${n}" -ge 1 ]; then st_ok "実物の kit/ に selftest が ${n} 本ある"
    else st_ng "実物の kit/ に selftest が 1 本も無い"; fi
  fi

  echo "  ---- 入口の陰性対照 失敗 ${ST_FAILS} 件 ----"
  [ "${ST_FAILS}" -eq 0 ]
}

case "${MODE}" in
  selftests) echo "=== kit selftest（${ROOT}）==="; run_selftests "${ROOT}" ;;
  compile) echo "=== kit compile（${ROOT}）==="; run_compile "${ROOT}" ;;
  entry-selftest) entry_selftest ;;
esac
exit $?
