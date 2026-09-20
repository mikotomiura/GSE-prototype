#!/usr/bin/env bash
# check-g1-collection-readiness.sh — ★ G1 の**新コホートの収集を始める前**に通すゲート。
#
# ============================================================================
# ⚠️★★★ このゲートは **今は赤いのが正しい。**
# ============================================================================
#   ★ 事前登録は逐語で「⚠️ **1〜7 が終わるまで新コホートの収集を始めない。**」と宣言している
#     (`experiments/20260801-controlled-friction-task/preregistration.md:69`)。
#   ⚠️ ところが 2026-09-20 まで、**この 7 つを確かめる機械検査は 1 件も無かった。**
#     ★ `run.sh` は自分で「**技術的な準備が整っているかだけを見る**」と宣言しており
#       (`run.sh:7-9`)、⚠️ それでも「`run.sh` が緑だから収集してよい」と読める状態が残っていた。
#   → ★ 本スクリプトの役目は「何が残っているかを**人の記憶ではなく機械に持たせる**」こと。
#   ⚠️ 緑になるまで新コホートを 1 人も走らせない。
#
# ⚠️★★★ **このゲートが見ていないもの**(★ 隠さずに書く):
#   - ★ **配布したバイナリの実行時の挙動** (見ているのはソースツリーのテストが緑であること)
#   - ⚠️ **外部サービスの状態** (配布済みの電子同意フォーム / Drive 上の実物 / CI の両 OS の run)
#     → ★ これらは `experiments/.../collection-readiness-record.md` の**人手の記録票**に落とす。
#       ⚠️ 検査 [8] が見ているのは「**人が確かめたと書いたこと**」だけである。
#   - ★ **前提条件 7 の中身の妥当性** (★ 研究者判断。見るのは「決めて記録されたか」だけ)
#
# 使い方:
#   bash scripts/check-g1-collection-readiness.sh
#   bash scripts/check-g1-collection-readiness.sh --selftest   # ★ ゲート自身を壊して赤になるか測る
#
# 終了コード: 0 = 収集を始めてよい / 1 = まだ始められない / 2 = 引数が不正
#
# ⚠️ Windows では git-bash から実行すること (PowerShell では動かない)。
# ⚠️ `--selftest` は **cargo を 8 回ほど走らせる**ので数分かかる (★ 実物の repo は 1 バイトも変えない)。
#
# 関連: .steering/20260920-g1-collection-readiness-gate/
#       scripts/check-o1-release-readiness.sh (★ O1 側の対になるゲート)

set -uo pipefail

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
cd "$(dirname "$0")/.." || { echo "リポジトリ直下へ移動できません" >&2; exit 1; }

# ⚠️★★ 子プロセス (python3) の**出力**を UTF-8 に固定する。
#   ★ Windows の既定 (cp932) だと `build_task_pages.py` の日本語 print が
#     `UnicodeEncodeError` で落ち、⚠️ **生成は成功しているのに赤**になる (2026-09-20 に実測)。
#   ⚠️ `PYTHONUTF8=1` は足さない (★ ファイルの読み方まで変わる。`run.sh:22-24` と同じ判断)。
export PYTHONIOENCODING=utf-8:backslashreplace

MODE=main
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) MODE=selftest; shift ;;
    -h|--help)  sed -n '1,40p' "$0"; exit 0 ;;
    # ⚠️ ★ 知らない引数を**黙って無視しない**。無視すると `--selftst` の打ち間違いが
    #   「通常のゲートが緑だった」に化ける (★ 本スクリプトが戒めている silent pass そのもの)。
    *) echo "知らない引数: $1" >&2; exit 2 ;;
  esac
done

PASS=0; FAIL=0
ok()    { echo "  ✅ $*"; PASS=$((PASS+1)); }
ng()    { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
head_() { echo; echo "[$1] $2"; }

G1DIR="experiments/20260801-controlled-friction-task"
PREREG="${G1DIR}/preregistration.md"
CONSENT="${G1DIR}/consent.md"
GUIDE="${G1DIR}/participant-guide.md"
SHEET="${G1DIR}/record-sheet-confirmatory.md"
RECORD="${G1DIR}/collection-readiness-record.md"
CONFIG="${G1DIR}/config.json"
SNAPDIR="src-tauri/tests/snapshots"
FIXDIR="src-tauri/tests/fixtures"
SCHEMA="src-tauri/schema/current.json"

# ★ 事前登録の逐語「ゴールデン **6 本** byte-equal」(`preregistration.md:359`)。
#   ⚠️ CI は `minimal.ndjson` **1 本**しか再生していない (`ci.yml:581-582`・2026-09-20 実測)。
GOLDEN_EXPECT=6
# ★ 前提条件 7 の記録先は「本文書の改訂履歴 (**第 20 版以降**)」(`preregistration.md:52`)。
PREREG_REV_FOR_7=20
# ★ 課題ページの生成検査に使う被験者 ID。⚠️ **実在の被験者に割り当ててはならない**。
#   ★ `assign.py` は `P<数字>` 形式しか受け付けず、**何も書き込まない** (2026-09-20 に確認)。
GATE_SUBJECT="P999"

# ============================================================================
# ★ 変異モード (⚠️ `--selftest` 専用)
# ============================================================================
#   ⚠️★★★ **なぜ env で壊すのか**: 検査 [1] [2] [4] は cargo を呼ぶので、
#     一時ディレクトリの fixture では**常に「manifest が無い」で赤**になり、
#     ⚠️ **壊しても壊さなくても赤 = 変異試験が成立しない**。
#     → ★ これらだけは **実物の repo に対して**、フィルタ名や比較対象を差し替えて撃つ。
#   ⚠️★★★ **悪用できないようにする**: 変異モードでは最後に必ず `ng` を 1 件足すので、
#     ★ **どう壊しても緑 (exit 0) にはならない**。→ 「変異モードで緑だった」は原理的に作れない。
MUT="${GSE_G1_GATE_MUTATE:-}"
mutated () { case ",${MUT}," in *",$1,"*) return 0 ;; *) return 1 ;; esac ; }

# ★ in-place sed の移植版 (BSD と GNU の `-i` の差を避ける)。
sed_i () {
  local n=$# f tmp i
  eval "f=\${${n}}"
  local args=()
  i=1
  while [ "${i}" -lt "${n}" ]; do
    eval "args+=(\"\${${i}}\")"
    i=$((i + 1))
  done
  tmp="$(mktemp)"
  # ⚠️★ 置き換えは成功したときだけ (★ 失敗して空ファイルにすると変異試験が意味を失う)。
  if sed "${args[@]}" "${f}" > "${tmp}"; then
    cat "${tmp}" > "${f}"
  else
    echo "sed に失敗した: ${f}" >&2
  fi
  rm -f "${tmp}"
}

CARGO_BIN=""
resolve_cargo () {
  CARGO_BIN="$(command -v cargo 2>/dev/null || true)"
  if [ -z "${CARGO_BIN}" ] && [ -x "${HOME}/.cargo/bin/cargo" ]; then
    CARGO_BIN="${HOME}/.cargo/bin/cargo"
  fi
}

# ★ `run.sh` の `run_cargo_filter` と**同じ形**。
#   ⚠️★★★ **本数まで見る**のは、0 件マッチでも cargo が rc=0 を返すためである
#   (★ テストが消えた / 改名されたときに緑のままになる ＝ silent pass の穴)。
cargo_expect () {
  local expect="$1" filter="$2" label="$3" tmp rc passed
  if [ -z "${CARGO_BIN}" ]; then
    ng "cargo が無いので判定できない: ${label}"
    return
  fi
  tmp="$(mktemp)"; rc=0
  "${CARGO_BIN}" test --quiet --manifest-path src-tauri/Cargo.toml --lib "${filter}" \
    > "${tmp}" 2>&1 || rc=$?
  passed="$(grep -oE '[0-9]+ passed' "${tmp}" | head -1 | grep -oE '[0-9]+' || true)"
  [ -n "${passed}" ] || passed=0
  if [ "${rc}" -ne 0 ]; then
    tail -8 "${tmp}" | sed 's/^/      /'
    ng "${label}: テストが赤 (rc=${rc})"
  elif [ "${passed}" -lt "${expect}" ]; then
    ng "${label}: ${passed} 本しか通っていない (${expect} 本を期待。★ テストが消えた/改名された可能性)"
  else
    ok "${label} (${passed} / ${expect} 本)"
  fi
  rm -f "${tmp}"
}

# ★ 記録票の 1 節を取り出す (★ `## A.` から次の `## ` の直前まで)。
record_section () {
  awk -v pat="$1" '
    index($0, pat) == 1 { f = 1; next }
    /^## / { if (f) exit }
    f { print }
  ' "${RECORD}"
}

# ★ 記録票の 1 節が「埋まっているか」。
#   ⚠️ **状態だけ書き換えても緑にしない** (★ 欄が空なら中身の無い確認である)。
record_ok () {
  local key="$1" label="$2" sec
  sec="$(record_section "${key}")"
  if [ -z "${sec}" ]; then
    ng "記録票 ${label}: 節が見つからない (★ 記録票の見出しが変わった可能性)"
    return
  fi
  if ! printf '%s\n' "${sec}" | grep -q '^- 状態: \*\*確認済み\*\*$'; then
    ng "記録票 ${label}: まだ実施されていない (★ 状態が「確認済み」でない)"
    return
  fi
  if printf '%s\n' "${sec}" | grep -q '（未記入）'; then
    ng "記録票 ${label}: 未記入の欄が残っている"
    return
  fi
  ok "記録票 ${label} が埋まっている (⚠️ ゲートは人が書いたことしか見ていない)"
}

# ★ 事前登録の改訂履歴にある**最大の版番号**。
latest_prereg_rev () {
  grep -oE '改訂履歴 — 第 [0-9]+ 版' "${PREREG}" 2>/dev/null \
    | grep -oE '[0-9]+' | sort -n | tail -1
}

# ★ `config.json` の `revision.version`。
config_rev () {
  python3 -c 'import json,sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print(d.get("revision", {}).get("version", ""))' "${CONFIG}" 2>/dev/null
}

# ============================================================================
run_checks () {

resolve_cargo

# --- 1. ADR-013 の計器 (前提条件 1) -----------------------------------------
head_ 1 "ADR-013 の計器が**出力に載る** (前提条件 1)"
echo "     ⚠️ 見ているのは出力行を固定したテストが緑であること。★ 配布物の実行時挙動は見ていない。"
T1A="logger::tests::meta_line_is_byte_identical_when_not_g1"
T1B="logger::tests::starve_window_line_shape_is_stable"
T1C="logger::tests::dropped_delta_is_written_alongside_cumulative_dropped"
mutated t1a && T1A="logger::tests::__gate_selftest_missing__"
mutated t1b && T1B="logger::tests::__gate_selftest_missing__"
mutated t1c && T1C="logger::tests::__gate_selftest_missing__"
cargo_expect 1 "${T1A}" "meta 行に app_version と capabilities が載る"
cargo_expect 1 "${T1B}" "starve_window 行の書式が固定されている"
cargo_expect 1 "${T1C}" "dropped_delta が累積の dropped と並んで書かれる"

# --- 2. G-1 の修正 (前提条件 2) ---------------------------------------------
head_ 2 "実行中の再押下は「前を閉じてから新規」 (前提条件 2)"
echo "     ⚠️ ★ これらのテストは在ったが run.sh は呼んでいなかった (2026-09-20 実測)。"
T2A="g1::tests::g1_restart_while_active_rotates_without_counting"
T2B="g1::tests::restart_is_distinguished_from_meta_retry_by_the_handshake"
mutated t2a && T2A="g1::tests::__gate_selftest_missing__"
mutated t2b && T2B="g1::tests::__gate_selftest_missing__"
cargo_expect 1 "${T2A}" "再押下で前を閉じ、回転はするが数えない"
cargo_expect 1 "${T2B}" "再押下と meta 再試行が握手で区別される"

# --- 3. 記録項目表への追記 (前提条件 3) -------------------------------------
head_ 3 "同意文書と参加案内の記録項目表 (前提条件 3)"
echo "     ⚠️ 見ているのは**手元の 2 つの md に語が在るか**だけ。"
echo "        ★ 配布済みの電子同意フォームとの突合は検査 [8] の記録票 A。"
for pair in "${CONSENT}|同意文書" "${GUIDE}|参加案内"; do
  path="${pair%%|*}"; name="${pair##*|}"
  if [ ! -f "${path}" ]; then
    ng "${name}が無い: ${path}"
  elif ! grep -q 'starve_window' "${path}"; then
    ng "${name}の記録項目表に starve_window が無い"
  elif ! grep -q 'app_version' "${path}"; then
    ng "${name}の記録項目表に app_version が無い"
  else
    ok "${name}に starve_window と app_version が書いてある"
  fi
done

# --- 4. ゴールデンと schema (前提条件 4) ------------------------------------
head_ 4 "ゴールデン ${GOLDEN_EXPECT} 本 byte-equal / schema parity (前提条件 4)"
echo "     ⚠️ **両 OS の対**は 1 台では見られない。★ CI の run は検査 [8] の記録票 B。"
snaps=()
while IFS= read -r p; do
  [ -n "${p}" ] && snaps+=("${p}")
done < <(ls "${SNAPDIR}"/*.json 2>/dev/null | sort)
# ★ 変異: ゴールデンを 1 本落とす (⚠️ 本数ガードが効いているか)。
if mutated golden_miss && [ "${#snaps[@]}" -gt 0 ]; then
  snaps=("${snaps[@]:1}")
fi
if [ "${#snaps[@]}" -lt "${GOLDEN_EXPECT}" ]; then
  ng "ゴールデンが ${#snaps[@]} 本しかない (${GOLDEN_EXPECT} 本を期待)"
else
  ok "ゴールデンが ${#snaps[@]} 本ある"
fi
if [ -z "${CARGO_BIN}" ]; then
  ng "cargo が無いのでゴールデンを再生できない"
else
  gfail=0; gdone=0; first=1
  for snap in ${snaps[@]+"${snaps[@]}"}; do
    name="$(basename "${snap}" .json)"
    fixture="${FIXDIR}/${name}.ndjson"
    use_snap="${snap}"
    # ★ 変異: 1 本目だけ**別のゴールデン**と突き合わせる (⚠️ 比較が本当に走っているか)。
    if [ "${first}" = "1" ] && mutated golden_break && [ "${#snaps[@]}" -gt 1 ]; then
      use_snap="${snaps[1]}"
    fi
    first=0
    if [ ! -f "${fixture}" ]; then
      ng "ゴールデンに対応する fixture が無い: ${fixture}"
      gfail=$((gfail+1)); continue
    fi
    if "${CARGO_BIN}" run --quiet --bin gse-replay --manifest-path src-tauri/Cargo.toml -- \
         "${fixture}" --snapshot "${use_snap}" > /dev/null 2>&1; then
      gdone=$((gdone+1))
    else
      ng "ゴールデンが一致しない: ${name}"
      gfail=$((gfail+1))
    fi
  done
  if [ "${gfail}" -eq 0 ] && [ "${gdone}" -gt 0 ]; then
    ok "ゴールデン ${gdone} 本が byte-equal で一致した"
  elif [ "${gdone}" -eq 0 ] && [ "${gfail}" -eq 0 ]; then
    ng "ゴールデンを 1 本も再生していない (★ 対象が見つからなかった)"
  fi

  # ★ schema drift: `emit_schema` の出力が `schema/current.json` と byte-equal か。
  emitted="$(mktemp)"
  if "${CARGO_BIN}" run --quiet --bin emit_schema --manifest-path src-tauri/Cargo.toml \
       > "${emitted}" 2>/dev/null; then
    # ★ 変異: 出力を 1 バイト汚す (⚠️ 比較が本当に走っているか)。
    mutated schema_break && printf 'x' >> "${emitted}"
    if cmp -s "${emitted}" "${SCHEMA}"; then
      ok "emit_schema の出力が ${SCHEMA} と byte-equal"
    else
      ng "emit_schema の出力が schema/current.json と一致しない (schema drift)"
    fi
  else
    ng "emit_schema を実行できない"
  fi
  rm -f "${emitted}"
fi

# ★ schema parity: gse-dataset 側の schema と意味的に一致するか。
#   ⚠️ 見つからなければ **赤**にする (★ skip を作らない)。
DATASET="${GSE_DATASET:-${DATASET_ROOT:-}}"
if [ -z "${DATASET}" ]; then
  for cand in "${HOME}/gse-dataset" "/c/gse-dataset" "C:/gse-dataset"; do
    [ -d "${cand}" ] && { DATASET="${cand}"; break; }
  done
fi
if ! command -v python3 > /dev/null 2>&1; then
  ng "python3 が無いので schema parity を判定できない"
elif [ -z "${DATASET}" ] || [ ! -d "${DATASET}" ]; then
  ng "gse-dataset が見つからないので schema parity を判定できない (GSE_DATASET を指す)"
else
  # ⚠️★★ **終了コードで原因を分ける** (★ `check_schema_parity.py` の docstring より)。
  #   ★ 分けないと「schema が無い」を「食い違っている」と報告し、⚠️ **直す先を誤らせる**
  #     (2026-09-20 に selftest の fixture で実際に誤報していた)。
  python3 scripts/check_schema_parity.py --dataset "${DATASET}" > /dev/null 2>&1
  prc=$?
  case "${prc}" in
    0) ok "gse-dataset の schema と一致している (${DATASET})" ;;
    1) ng "gse-dataset の schema と食い違っている (schema parity)" ;;
    2) ng "${SCHEMA} が無いので schema parity を判定できない" ;;
    3) ng "gse-dataset 側の schema/current.json が無いので schema parity を判定できない" ;;
    *) ng "schema parity の検査を実行できない (rc=${prc})" ;;
  esac
fi

# --- 5. 課題ページ (前提条件 5) ---------------------------------------------
head_ 5 "課題ページに生の ** が残っていない (前提条件 5)"
echo "     ⚠️ 見ているのは**生成器**だけ。★ Drive 上の実物の差し替えは検査 [8] の記録票 C。"
if ! command -v python3 > /dev/null 2>&1; then
  ng "python3 が無いので課題ページを判定できない"
else
  t5="$(mktemp -d)"
  mkdir -p "${t5}/blocks" "${t5}/pages"
  if ! ( cd "${G1DIR}" && python3 assign.py --subject "${GATE_SUBJECT}" --json ) \
        > "${t5}/blocks/${GATE_SUBJECT}.json" 2> "${t5}/assign.err"; then
    tail -5 "${t5}/assign.err" | sed 's/^/      /'
    ng "課題ページの割付を作れない (assign.py)"
  elif ! ( cd "${G1DIR}" && python3 build_task_pages.py --subject "${GATE_SUBJECT}" \
             --blocks-dir "${t5}/blocks" --out "${t5}/pages" ) > "${t5}/build.log" 2>&1; then
    tail -8 "${t5}/build.log" | sed 's/^/      /'
    ng "課題ページを生成できない (build_task_pages.py)"
  else
    pdir="${t5}/pages/${GATE_SUBJECT}"
    total="$(ls "${pdir}"/*.html 2>/dev/null | wc -l | tr -d ' ')"
    if [ "${total}" = "0" ]; then
      ng "課題ページが 1 枚も生成されていない"
    else
      raw="$(grep -l -- '\*\*' "${pdir}"/*.html 2>/dev/null | wc -l | tr -d ' ')"
      strong="$(grep -l -- '<strong>' "${pdir}"/*.html 2>/dev/null | wc -l | tr -d ' ')"
      if [ "${raw}" = "0" ]; then
        ok "生の ** を含むページが 0 枚 (${total} 枚中)"
      else
        ng "生の ** が残っているページが ${raw} 枚ある (${total} 枚中)"
      fi
      # ★ 陰性対照: 強調が `<strong>` として**実際に出ている**こと。
      #   ⚠️ これが無いと「そもそも強調が 1 つも無いページ」を緑と読んでしまう。
      if [ "${strong}" = "${total}" ]; then
        ok "陰性対照: <strong> が全 ${total} 枚にある"
      else
        ng "陰性対照が成立しない: <strong> があるのは ${strong} 枚 (${total} 枚を期待)"
      fi
    fi
  fi
  rm -rf "${t5:?}"
fi

# --- 6. 記録用紙 (前提条件 6) -----------------------------------------------
head_ 6 "記録用紙に「文字数」欄がある (前提条件 6)"
if [ ! -f "${SHEET}" ]; then
  ng "確証用の記録用紙が無い: ${SHEET}"
elif ! grep -qE '^ *#? *\| *条件|文字数' "${SHEET}"; then
  ng "記録用紙に文字数欄が見つからない"
elif ! grep -q '文字数' "${SHEET}"; then
  ng "記録用紙に文字数欄が見つからない"
else
  ok "記録用紙に「文字数」欄がある"
fi

# --- 7. 途中でやめた人の数え方 (前提条件 7) ---------------------------------
head_ 7 "途中でやめた人の記録の数え方 (前提条件 7)"
echo "     ⚠️ 見ているのは**決めて記録されたか**だけ。★ 中身の妥当性は研究者判断。"
rev="$(latest_prereg_rev)"
if [ -z "${rev}" ]; then
  ng "事前登録の改訂履歴を読めない: ${PREREG}"
else
  if [ "${rev}" -ge "${PREREG_REV_FOR_7}" ]; then
    ok "事前登録に第 ${rev} 版の記録がある (第 ${PREREG_REV_FOR_7} 版以降)"
  else
    ng "やめた人の数え方が未決 (事前登録は第 ${rev} 版。第 ${PREREG_REV_FOR_7} 版以降の記録が要る)"
  fi
  crev="$(config_rev)"
  if [ -z "${crev}" ]; then
    ng "config.json の revision.version を読めない"
  elif [ "${crev}" = "${rev}" ]; then
    ok "config.json の revision が事前登録と同じ版 (${crev})"
  else
    ng "config.json の revision が事前登録とずれている (config=${crev} / 事前登録=${rev})"
  fi
fi

# --- 8. 人手確認の記録票 -----------------------------------------------------
head_ 8 "人手確認の記録票 (★ 外部サービスの状態)"
echo "     ⚠️★★★ ここで見ているのは「**人が確かめたと書いたこと**」だけである。"
echo "        ★ Drive 上の実物も、配布済みフォームの中身も、CI の run も、ゲートは見ていない。"
if [ ! -f "${RECORD}" ]; then
  ng "人手確認の記録票が無い: ${RECORD}"
else
  record_ok "## A." "A (配布済みフォームとの突合)"
  record_ok "## B." "B (両 OS の対のテスト)"
  record_ok "## C." "C (Drive の差し替え)"
fi

# ⚠️★★★ 変異モードでは**必ず 1 件落とす**。★ どう壊しても緑にはならない。
if [ -n "${MUT}" ]; then
  echo
  ng "変異モード (GSE_G1_GATE_MUTATE=${MUT}) で実行した。★ この実行結果を根拠にしてはならない"
fi

}

# ============================================================================
# ★ selftest — ⚠️ **ゲート自身が空回りしていないか**を測る
# ============================================================================
#   ★ 2 通りで撃つ:
#     (i)  ファイル系の検査 ([3] [5] [6] [7] [8]) → 一時ディレクトリへ写して**壊す / 満たす**
#     (ii) cargo 系の検査 ([1] [2] [4])          → ⚠️ fixture では常に赤なので変異試験が
#          成立しない。★ **実物の repo** に対し `GSE_G1_GATE_MUTATE` で撃つ
#          (⚠️ 実物は 1 バイトも変更しない)
selftest () {
  local repo fix out sp sf
  repo="$(pwd)"
  fix="$(mktemp -d)"
  trap 'rm -rf "${fix:?}"' RETURN
  trap 'rm -rf "${fix:?}"; exit 130' INT
  trap 'rm -rf "${fix:?}"; exit 143' TERM
  sp=0; sf=0

  build () {
    rm -rf "${fix:?}/w"
    mkdir -p "${fix}/w/scripts" "${fix}/w/experiments"
    cp "${SCRIPT_PATH}" "${fix}/w/scripts/gate.sh"
    cp "${repo}/scripts/check_schema_parity.py" "${fix}/w/scripts/" 2>/dev/null
    cp -r "${repo}/${G1DIR}" "${fix}/w/experiments/" 2>/dev/null
    # ⚠️ 重い / 配布物 / 生成物は写さない (★ handouts には被験者向け docx が入っている)。
    rm -rf "${fix}/w/${G1DIR}/pages" "${fix}/w/${G1DIR}/results" \
           "${fix}/w/${G1DIR}/handouts" "${fix}/w/${G1DIR}/__pycache__"
  }

  # $1 = 赤くなるはずの ❌ 行に含まれる語 / $2 = 説明 / $3.. = 実行環境 (省略可)
  expect_red () {
    local pat="$1" label="$2"; shift 2
    out="$("$@" bash "${fix}/w/scripts/gate.sh" 2>&1)"
    if printf '%s\n' "${out}" | grep -E '^  ❌' | grep -q -- "${pat}"; then
      echo "  ✅ 壊すと赤になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: ${label}"; sf=$((sf+1))
    fi
  }
  # ★ 実物の repo に対して撃つ (⚠️ 1 バイトも変更しない)。
  expect_red_real () {
    local token="$1" pat="$2" label="$3"
    out="$(cd "${repo}" && GSE_G1_GATE_MUTATE="${token}" bash "${SCRIPT_PATH}" 2>&1)"
    if printf '%s\n' "${out}" | grep -E '^  ❌' | grep -q -- "${pat}"; then
      echo "  ✅ 壊すと赤になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: ${label}"; sf=$((sf+1))
    fi
  }
  # $1 = 緑になるはずの ✅ 行に含まれる語 / $2 = 説明
  expect_green () {
    local pat="$1" label="$2"
    out="$(bash "${fix}/w/scripts/gate.sh" 2>&1)"
    if printf '%s\n' "${out}" | grep -E '^  ✅' | grep -q -- "${pat}"; then
      echo "  ✅ 満たすと緑になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 満たしても赤のまま: ${label}"; sf=$((sf+1))
    fi
  }

  # ⚠️★★ **照合語はメッセージ固有にする** (★ 別の理由で出た ❌ を拾って偽の合格にしない)。

  echo "=== selftest 1: ファイル系の検査を 1 つずつ壊す ==="
  build; rm -f "${fix}/w/${CONSENT}"
  expect_red "同意文書が無い" "同意文書の欠落 (検査 3)"
  # ⚠️★★★ **2 語目が本当に見られているか**を撃つ (2026-09-20 に検算して差し替えた)。
  #   ★ 旧版は「参加案内だけ未追記」を期待していたが、⚠️ **変異しなくても同じ ❌ が出る**
  #     (参加案内は元から未追記) ので、**空回りで緑を返していた**。
  #   → ★ 1 語目だけ足し、**2 語目で赤になる**ことを見る (baseline に無い ❌)。
  build; printf '\nstarve_window\n' >> "${fix}/w/${CONSENT}"
  expect_red "同意文書の記録項目表に app_version が無い" "★ 1 語目だけ足す (検査 3)"
  build; rm -f "${fix}/w/${SHEET}"
  expect_red "確証用の記録用紙が無い" "記録用紙の欠落 (検査 6)"
  build; sed_i 's/文字数/字数欄なし/g' "${fix}/w/${SHEET}"
  expect_red "記録用紙に文字数欄が見つからない" "記録用紙の文字数欄の喪失 (検査 6)"
  build; rm -f "${fix}/w/${RECORD}"
  expect_red "人手確認の記録票が無い" "記録票の欠落 (検査 8)"
  build; sed_i 's/^## A\./## Z./' "${fix}/w/${RECORD}"
  expect_red "記録票 A (配布済みフォームとの突合): 節が見つからない" "記録票の見出しの改名 (検査 8)"
  # ⚠️★★★ **状態だけ書き換えても緑にならないこと** (★ 中身の無い確認で通さない)。
  build; sed_i 's/^- 状態: \*\*未実施\*\*$/- 状態: **確認済み**/' "${fix}/w/${RECORD}"
  expect_red "記録票 A (配布済みフォームとの突合): 未記入の欄が残っている" \
             "★ 状態だけ確認済みにする (検査 8)"
  build; sed_i 's/改訂履歴 — 第 19 版/改訂履歴 — 第 21 版/' "${fix}/w/${PREREG}"
  expect_red "config.json の revision が事前登録とずれている" "版のずれ (検査 7)"
  # ★ 課題ページ: 生の ** を 1 枚に混ぜる材料を作れないので、**陰性対照側**を壊す。
  build; sed_i 's|<strong>|<em>|g' "${fix}/w/${G1DIR}/writing-pad.html"
  expect_red "陰性対照が成立しない" "陰性対照の喪失 (検査 5)"
  build; rm -f "${fix}/w/${G1DIR}/build_task_pages.py"
  expect_red "課題ページを生成できない" "生成器の欠落 (検査 5)"

  echo
  echo "=== selftest 2: 未達を満たすと緑に変わるか ==="
  build
  sed_i 's/^- 状態: \*\*未実施\*\*$/- 状態: **確認済み**/; s/（未記入）/2026-09-20/g' \
        "${fix}/w/${RECORD}"
  expect_green "記録票 A (配布済みフォームとの突合) が埋まっている" "記録票 A を埋める (検査 8)"
  build
  sed_i 's/^| 記録する | 記録しない |$/| 記録する (starve_window \/ app_version) | 記録しない |/' \
        "${fix}/w/${CONSENT}"
  expect_green "同意文書に starve_window と app_version" "同意文書への追記 (検査 3)"
  # ★ **2 つの文書が別々に見られている**ことの対照 (★ baseline にこの ✅ は無い)。
  build
  printf '\n- `starve_window` と `app_version` を記録します。\n' >> "${fix}/w/${GUIDE}"
  expect_green "参加案内に starve_window と app_version" "参加案内への追記 (検査 3)"
  build
  sed_i 's/^## ★ 改訂履歴 — 第 19 版/## ★ 改訂履歴 — 第 20 版/' "${fix}/w/${PREREG}"
  sed_i 's/"version": 19/"version": 20/' "${fix}/w/${CONFIG}"
  expect_green "事前登録に第 20 版の記録がある" "前提条件 7 を決めて記録する (検査 7)"

  echo
  echo "=== selftest 3: cargo 系の検査 (★ 実物の repo・⚠️ 1 バイトも変更しない) ==="
  expect_red_real t1a  "meta 行に app_version と capabilities が載る: 0 本" \
                       "meta 行テストの改名 (検査 1)"
  expect_red_real t1b  "starve_window 行の書式が固定されている: 0 本" \
                       "starve_window テストの改名 (検査 1)"
  expect_red_real t1c  "dropped_delta が累積の dropped と並んで書かれる: 0 本" \
                       "dropped_delta テストの改名 (検査 1)"
  expect_red_real t2a  "再押下で前を閉じ、回転はするが数えない: 0 本" \
                       "再押下テストの改名 (検査 2)"
  expect_red_real t2b  "再押下と meta 再試行が握手で区別される: 0 本" \
                       "握手テストの改名 (検査 2)"
  expect_red_real golden_miss  "ゴールデンが 5 本しかない" "ゴールデンが 1 本消える (検査 4)"
  expect_red_real golden_break "ゴールデンが一致しない" "ゴールデンの突き合わせ先のすり替え (検査 4)"
  expect_red_real schema_break "schema drift" "emit_schema 出力の汚損 (検査 4)"

  echo
  echo "────────────────────────────────────────"
  echo "  selftest 通過 ${sp} 件 / 失敗 ${sf} 件"
  if [ "${sf}" -eq 0 ] && [ "${sp}" -gt 0 ]; then
    echo "  ✅ ゲートは空回りしていない。"
    return 0
  fi
  echo "  ❌ ⚠️ 空回りしている検査がある。上の ❌ を直すこと。"
  return 1
}

if [ "${MODE}" = selftest ]; then
  selftest; exit $?
fi

echo "=============================================================="
echo " G1 収集開始ゲート (★ 前提条件 1〜7)"
echo "=============================================================="

run_checks

echo
echo "────────────────────────────────────────"
echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
if [ "${FAIL}" -eq 0 ]; then
  echo "  ✅ 前提条件 1〜7 は満たされています (★ 収集を始めてよい)。"
  exit 0
fi
echo "  ❌ ⚠️ まだ新コホートの収集を始められません。上の ❌ を全部消すこと。"
echo "────────────────────────────────────────"
exit 1
