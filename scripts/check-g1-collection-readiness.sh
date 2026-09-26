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
#   - ⚠️★★★ **前提条件が 8 個目に増えたこと自体** は検査 [0] の逐語固定でしか捕まえない。
#     ★ 本スクリプトは **1〜7 しか知らない**。事前登録は実際に増えてきた
#     (第 17 版 1〜4 → 第 18 版 +5,6 → 第 19 版 +7)。→ 宣言文が変わったら赤にする。
#
# 使い方:
#   bash scripts/check-g1-collection-readiness.sh
#   bash scripts/check-g1-collection-readiness.sh --selftest   # ★ ゲート自身を壊して赤になるか測る
#
# 終了コード: 0 = 収集を始めてよい / 1 = まだ始められない / 2 = 引数が不正
#
# ⚠️ Windows では git-bash から実行すること (PowerShell では動かない)。
# ⚠️ `--selftest` は **ゲート全体を 9 回ほど回す** (cargo test 5 本 + replay 6 本 + emit_schema を
#    毎回) ので **1 分強**かかる (2026-09-20 実測: 1m10s)。★ 実物の repo は 1 バイトも変えない。
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
# ★ 「実物の repo を 1 バイトも変えない」を**本当に**成り立たせる (code-reviewer LOW)。
#   ⚠️ 付けないと `assign.py` を実 repo 内で import した時点で `__pycache__/` が書かれる。
export PYTHONDONTWRITEBYTECODE=1

# ★ 一時ファイル / ディレクトリの後始末を 1 か所に集める。
#   ⚠️★★ **EXIT と HUP も張る** (security-checker M-2): `RETURN` / `INT` / `TERM` だけだと
#     `set -u` 違反での即死・端末を閉じた場合・本体モードの中断で **残る**。
#   ★ `${p:?}` で空文字の `rm -rf` を弾く。
GATE_TMPS=()
gate_cleanup () {
  local p
  for p in ${GATE_TMPS[@]+"${GATE_TMPS[@]}"}; do
    [ -n "${p}" ] && rm -rf "${p:?}"
  done
  GATE_TMPS=()
}
trap 'gate_cleanup' EXIT
trap 'gate_cleanup; exit 130' INT
trap 'gate_cleanup; exit 143' TERM
trap 'gate_cleanup; exit 129' HUP

gate_mktemp () { local p; p="$(mktemp "${TMPDIR:-/tmp}/g1gate.XXXXXX")" || return 1; GATE_TMPS+=("${p}"); printf '%s' "${p}"; }

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
# ⚠️★★★ **知らないトークンを黙って受け取らない** (security-checker M-3)。
#   ★ 旧版は `${MUT}` を ❌ 行にそのまま印字していたので、
#     `GSE_G1_GATE_MUTATE='同意文書が無い' ... --selftest` のように
#     ⚠️ **何も壊していないのに `expect_red` を通す文字列**を注入できた
#     (= 「ゲートは空回りしていない」という**証拠の側**を偽造できた)。
#   → ★ `--selftest` の打ち間違いを `exit 2` にするのと同じ規範を env にも当てる。
GATE_MUT_KNOWN="t1a t1b t1c t2a t2b golden_miss golden_break schema_break"
if [ -n "${MUT}" ]; then
  for tok in $(printf '%s' "${MUT}" | tr ',' ' '); do
    case " ${GATE_MUT_KNOWN} " in
      *" ${tok} "*) : ;;
      *) echo "知らない変異トークン: ${tok}" >&2; exit 2 ;;
    esac
  done
  # ⚠️★★ **検証と実処理の区切り文字をそろえる** (Codex /cross-review 1 巡目 #2)。
  #   ★ 検証は `tr ',' ' '` で空白区切りも通すのに、`mutated` は `,` しか見ていなかった。
  #     → ⚠️ `t1a t1b` は**検証を通るのに 1 つも変異しない**（黙って何もしないモード）。
  MUT="$(printf '%s' "${MUT}" | tr ' ' ',' | sed 's/,,*/,/g')"
fi
mutated () { case ",${MUT}," in *",$1,"*) return 0 ;; *) return 1 ;; esac ; }

# ★ ローカル絶対パスを画面に出さない (security-checker L-1)。
#   ⚠️ ゲートの出力は PR や cross-review 経由で外へ出うる。
#   ⚠️★★ **パスを sed のパターンとしてエスケープする** (Codex /cross-review 2 巡目 #3)。
#     ★ 素で埋め込むと、パスに `#` / `\` / `.` / `*` などが入る環境で
#       **sed 式が壊れる / 意図しない置換になる**。
redact () {
  local h p
  h="$(printf '%s' "${HOME}"  | sed 's/[][\\.*^$#&]/\\&/g')"
  p="$(printf '%s' "$(pwd)"   | sed 's/[][\\.*^$#&]/\\&/g')"
  sed -e "s#${h}#~#g" -e "s#${p}#<repo>#g"
}

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
  tmp="$(mktemp "${TMPDIR:-/tmp}/g1gate.XXXXXX")"
  # ⚠️★ 置き換えは成功したときだけ (★ 失敗して空ファイルにすると変異試験が意味を失う)。
  if sed "${args[@]}" "${f}" > "${tmp}"; then
    cat "${tmp}" > "${f}"
  else
    echo "sed に失敗した: ${f}" >&2
  fi
  rm -f "${tmp}"
}

# ★ 完全一致した行の**直後**に 1 行足す (`--selftest` の変異用)。
#   ⚠️ `sed` の `a\` も replacement 中の `\n` も **BSD と GNU で書き方が違う**ので awk を使う。
insert_after () {   # $1 = ファイル / $2 = 一致させる行 (完全一致) / $3 = 挿入する行
  local tmp
  tmp="$(mktemp "${TMPDIR:-/tmp}/g1gate.XXXXXX")"
  if awk -v m="$2" -v ins="$3" '{ print; if ($0 == m) print ins }' "$1" > "${tmp}"; then
    cat "${tmp}" > "$1"
  else
    echo "insert_after に失敗した: $1" >&2
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
  tmp="$(gate_mktemp)"; rc=0
  "${CARGO_BIN}" test --quiet --manifest-path src-tauri/Cargo.toml --lib "${filter}" \
    > "${tmp}" 2>&1 || rc=$?
  passed="$(grep -oE '[0-9]+ passed' "${tmp}" | head -1 | grep -oE '[0-9]+' || true)"
  [ -n "${passed}" ] || passed=0
  if [ "${rc}" -ne 0 ]; then
    tail -8 "${tmp}" | redact | sed 's/^/      /'
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
#   ⚠️★★ 行末は `[[:space:]]*$` で受ける (code-reviewer M6): `.gitattributes` は `*.md` を
#     LF 固定していないので、`core.autocrlf=true` の環境では `$` アンカーが CR で外れ、
#     **正しく埋めても永久に赤**になる (★ しかも「まだ実施されていない」と誤った理由が出る)。
record_ok () {
  local key="$1" label="$2" sec fields scan bad sha
  sec="$(record_section "${key}")"
  if [ -z "${sec}" ]; then
    ng "記録票 ${label}: 節が見つからない (★ 記録票の見出しが変わった可能性)"
    return
  fi
  # ★ 記入欄だけを取り出す (⚠️ 引用の規則文を書式検査の対象にしない)。
  fields="$(printf '%s\n' "${sec}" | grep '^- ' || true)"
  # ⚠️★★ **秘匿の走査は節全体**から行う (Codex /cross-review 2 巡目 #4)。
  #   ★ `- ` 行だけだと、**継続行**に URL を書かれたときに見落とす。
  #   ⚠️ 逐語を引いている引用行 (`>`) だけは除く (★ 規則文そのものを誤検知しない)。
  scan="$(printf '%s\n' "${sec}" | grep -v '^>' || true)"
  if ! printf '%s\n' "${sec}" | grep -qE '^- 状態: \*\*確認済み\*\*[[:space:]]*$'; then
    ng "記録票 ${label}: まだ実施されていない (★ 状態が「確認済み」でない)"
    return
  fi
  if printf '%s\n' "${sec}" | grep -q '（未記入）'; then
    ng "記録票 ${label}: 未記入の欄が残っている"
    return
  fi
  # ⚠️★★★ **一時 public 運用の repo に鍵を書かせない** (security-checker H-1)。
  #   ★ `protocol.md:1133` 逐語「❌ 成果物にセッション日時・氏名・メール・所属を出す」/
  #     `notes.md:1057` 逐語「★ 実 URL は repo に置かない。」と同じ規約をこの票にも当てる。
  #   ⚠️ 28 文字以上の英数字トークンは Google の file id の形 (★ 通常の日本語記入では出ない)。
  #   ⚠️★★★ **見ていないもの** (Codex /cross-review 1 巡目 #3): ★ **氏名・所属は機械では弾けない**。
  #     → 記録票にも「一部しか弾けない」と書いてある。★ 最後は書いた人が責任を持つ。
  bad=""
  printf '%s\n' "${scan}" | grep -qE 'https?://'              && bad="URL"
  printf '%s\n' "${scan}" | grep -q  '@'                      && bad="${bad}${bad:+ / }メールアドレス"
  printf '%s\n' "${scan}" | grep -qE '[A-Za-z0-9_-]{28,}'     && bad="${bad}${bad:+ / }ID らしき長いトークン"
  printf '%s\n' "${scan}" | grep -qE '[0-9]{1,2}:[0-9]{2}'    && bad="${bad}${bad:+ / }時刻"
  if [ -n "${bad}" ]; then
    ng "記録票 ${label}: 書いてはいけないものが入っている (${bad}) —— ★ 本 repo は一時 public にする"
    return
  fi
  if ! printf '%s\n' "${fields}" | grep -qE '^- 確認日: \*\*20[0-9]{2}-[0-9]{2}-[0-9]{2}\*\*[[:space:]]*$'; then
    ng "記録票 ${label}: 確認日が YYYY-MM-DD の形で入っていない"
    return
  fi
  # ⚠️★★★ **一括置換で埋める抜け道を塞ぐ** (Codex /cross-review 2 巡目 #1)。
  #   ★ `s/（未記入）/2026-09-20/g` のように**全部を同じ日付で埋める**と、
  #     日付の形も禁止語も満たしてしまい、⚠️ **中身の無い記録で「人手確認済み」**になる。
  #   → ★ `確認日` 以外の欄が**日付だけ**なら赤にする。
  if printf '%s\n' "${fields}" | grep -v '^- 確認日: ' \
       | grep -qE ': \*\*20[0-9]{2}-[0-9]{2}-[0-9]{2}\*\*[[:space:]]*$'; then
    ng "記録票 ${label}: 確認日以外の欄が日付のまま (★ 一括置換で埋めていないか)"
    return
  fi
  # ★ B / C だけが持つ「対象のコミット」。⚠️ **HEAD の祖先でなくなったら赤に戻す**
  #   (code-reviewer M7): 確認したのは「その版」であって、以後の任意の版ではない。
  if printf '%s\n' "${fields}" | grep -q '^- 対象のコミット: '; then
    sha="$(printf '%s\n' "${fields}" | sed -n 's/^- 対象のコミット: \*\*\([0-9a-f]\{7,40\}\)\*\*.*$/\1/p' | head -1)"
    if [ -z "${sha}" ]; then
      ng "記録票 ${label}: 対象のコミットが 7〜40 桁の hex で入っていない"
      return
    fi
    if ! git rev-parse --verify --quiet "${sha}^{commit}" > /dev/null 2>&1; then
      ng "記録票 ${label}: 対象のコミット ${sha} がこのリポジトリに無い"
      return
    fi
    if ! git merge-base --is-ancestor "${sha}" HEAD > /dev/null 2>&1; then
      ng "記録票 ${label}: 対象のコミット ${sha} は現在の HEAD の祖先でない (★ 確認し直すこと)"
      return
    fi
  fi
  ok "記録票 ${label} が埋まっている (⚠️ ゲートは人が書いたことしか見ていない)"
}

# ★ 事前登録の改訂履歴にある**最大の版番号**。
#   ⚠️★★ **見出しに限定する** (code-reviewer H2-a)。★ 文書全体だと 24 件ヒットし
#     (見出しは 18 件・2026-09-20 実測)、⚠️ **本文中の前方参照 1 行で版が上がったことになる**。
latest_prereg_rev () {
  grep -oE '^#+ .*改訂履歴 — 第 [0-9]+ 版' "${PREREG}" 2>/dev/null \
    | grep -oE '第 [0-9]+ 版' | grep -oE '[0-9]+' | sort -n | tail -1
}

# ★ 「第 N 版以降の見出し節」の本文を取り出す (★ 新しい版が先頭にある)。
prereg_section_for_rev () {
  awk -v want="$1" '
    /^#+ .*改訂履歴 — 第 [0-9]+ 版/ {
      n = $0; sub(/.*改訂履歴 — 第 /, "", n); sub(/ 版.*/, "", n)
      f = (n + 0 >= want + 0) ? 1 : 0
    }
    f { print }
  ' "${PREREG}"
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

# --- 0. 前提条件の数 ---------------------------------------------------------
# ⚠️★★★ **本スクリプトは 1〜7 しか知らない** (code-reviewer H3)。
#   ★ 事前登録は実際に増えてきた (第 17 版 1〜4 → 第 18 版 +5,6 → 第 19 版 +7)。
#   → ⚠️ 8 個目が足されたとき、ゲートが黙って 7 件だけ検査して緑を返すと
#     **事前登録違反を機械が追認する**。→ ★ 宣言文を逐語で固定する。
head_ 0 "前提条件の数が変わっていない (★ ゲートは 1〜7 しか見ていない)"
if [ ! -f "${PREREG}" ]; then
  ng "事前登録が無い: ${PREREG}"
elif grep -qF '**1〜7 が終わるまで新コホートの収集を始めない。**' "${PREREG}"; then
  ok "事前登録の宣言は「1〜7 が終わるまで」のまま"
else
  ng "前提条件の数が変わった可能性がある (★ ゲートは 1〜7 しか見ていない。検査を足すこと)"
fi

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
echo "     ⚠️ 見ているのは**手元の 2 つの md の記録項目表に語が在るか**だけ。"
echo "        ★ 配布済みの電子同意フォームとの突合は検査 [8] の記録票 A。"
# ⚠️★★★ **「記録する」側に在ることまで見る** (code-reviewer M4)。
#   ★ `consent.md:40` の表は `| 記録する | 記録しない |` の 2 列である。
#     ⚠️ 文書全体の grep だと **「記録しない」列に入れても緑**になり、意味が反転しても捕まらない。
#   → ★ 表の行 (`| ... |`) の **1 セル目**に在ることを要求する。
#   ⚠️ `participant-guide.md` は表とは限らないので、**箇条書きの項目行**も受ける。
#   ⚠️ **この検査が見ていないもの**: 列見出しが入れ替わった場合 (★ 1 セル目が「記録しない」に
#     なっていても通る)。→ 列見出しの並びは検査 [8] の記録票 A で人が見る。
#   ⚠️★★ **表を特定してから 1 セル目を見る** (Codex /cross-review 2 巡目 #2)。
#     ★ 旧式は「どこかの表の 1 セル目」で緑になったので、⚠️ **別表への追記でも通った**。
#     → ★ 「記録する」と「記録しない」を**両方持つヘッダ行**を見つけ、その表の行だけを見る。
#   ⚠️ **この検査が見ていないもの**: 列見出しの左右が入れ替わった場合 (★ 1 セル目が
#     「記録しない」側になっていても通る)。→ そこは検査 [8] の記録票 A で人が見る。
records_term () {   # $1 = ファイル / $2 = 語
  awk -v term="$2" '
    # ★ ヘッダ行を見つけたら表に入る (★ ヘッダ自身は項目行として数えない)。
    /^\|/ && /記録(する|します)/ && /記録(しない|しません)/ { intable = 1; next }
    intable && !/^\|/ { intable = 0 }
    intable && /^\|/ {
      line = $0
      sub(/^\|/, "", line)
      n = split(line, cell, "|")
      first = cell[1]
      gsub(/[ \t-]/, "", first)
      if (first != "" && index(cell[1], term) > 0) { found = 1 }
    }
    END { exit found ? 0 : 1 }
  ' "$1"
}
#   ⚠️★★★ **見る語は識別子ではなく、被験者が読む語**（2026-09-26・研究者判断＝推奨 A）。
#     ★ ADR-013 追補 2b（2026-08-20 実施・公開フォームと突合済み）は、`starve_window` を
#       「1 分ごとの短い中断の回数と合計」、`app_version` を「アプリの版」という**平易な言葉**で
#       表へ追記した。識別子の文字列を要求していた旧版は、内容が在るのに ❌ を出していた。
#     ★ 被験者向け文書に技術識別子を出す利益は無い（変えると電子同意フォームとの突合もやり直し）。
#   ⚠️ 語は「1 セル目」で見るので、**本文の箇条書きに同じ語が在っても緑にならない**
#     （旧版の箇条書き救済は、平易な語になると表の行を消しても通ってしまうので廃止した）。
TERM_STARVE='短い中断'      # ← `starve_window`
TERM_VERSION='アプリの版'   # ← `app_version`
for pair in "${CONSENT}|同意文書" "${GUIDE}|参加案内"; do
  path="${pair%%|*}"; name="${pair##*|}"
  if [ ! -f "${path}" ]; then
    ng "${name}が無い: ${path}"
  elif ! records_term "${path}" "${TERM_STARVE}"; then
    ng "${name}の記録項目表に「${TERM_STARVE}」（starve_window）の行が無い"
  elif ! records_term "${path}" "${TERM_VERSION}"; then
    ng "${name}の記録項目表に「${TERM_VERSION}」（app_version）の行が無い"
  else
    ok "${name}の記録項目表に「${TERM_STARVE}」と「${TERM_VERSION}」が書いてある"
  fi
done

# --- 4. ゴールデンと schema (前提条件 4) ------------------------------------
head_ 4 "ゴールデン ${GOLDEN_EXPECT} 本 byte-equal / schema parity (前提条件 4)"
echo "     ⚠️ **両 OS の対**は 1 台では見られない。★ CI の run は検査 [8] の記録票 B。"
# ★ `ls` のパイプ解析をやめ、glob で集める (code-reviewer LOW: 改行入りのファイル名で数を誤る)。
snaps=()
for p in "${SNAPDIR}"/*.json; do
  [ -e "${p}" ] && snaps+=("${p}")
done
# ★ 変異: ゴールデンを 1 本落とす (⚠️ 本数ガードが効いているか)。
#   ⚠️ 要素 1 本のとき `${snaps[@]:1}` は bash 3.2 + `set -u` で unbound になるので `-gt 1`。
if mutated golden_miss && [ "${#snaps[@]}" -gt 1 ]; then
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
  emitted="$(gate_mktemp)"
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
    0) ok "gse-dataset の schema と一致している ($(printf '%s' "${DATASET}" | redact))" ;;
    1) ng "gse-dataset の schema と食い違っている (schema parity)" ;;
    2) ng "${SCHEMA} が無いので schema parity を判定できない" ;;
    3) ng "gse-dataset 側の schema/current.json が無いので schema parity を判定できない" ;;
    4) ng "schema parity の引数か I/O が不正 (rc=4)" ;;
    *) ng "schema parity の検査を実行できない (rc=${prc})" ;;
  esac
fi

# --- 5. 課題ページ (前提条件 5) ---------------------------------------------
head_ 5 "課題ページに生の ** が残っていない (前提条件 5)"
echo "     ⚠️ 見ているのは**生成器**だけ。★ Drive 上の実物の差し替えは検査 [8] の記録票 C。"
if ! command -v python3 > /dev/null 2>&1; then
  ng "python3 が無いので課題ページを判定できない"
# ⚠️★★ **予約 ID が実被験者に使われていないこと**を機械で見る (security-checker L-3)。
#   ★ 旧版はコメントで予約を宣言しただけだった (= 誰も確かめない)。
elif [ -e "${G1DIR}/blocks/${GATE_SUBJECT}.json" ]; then
  ng "${GATE_SUBJECT} はゲートが使う予約 ID なのに割付ファイルがある (★ 実被験者に使わない)"
else
  t5="$(mktemp -d "${TMPDIR:-/tmp}/g1gate.XXXXXX")"; GATE_TMPS+=("${t5}")
  # ★ 「実物の repo を 1 バイトも変えない」を**主張でなく検査**にする (code-reviewer LOW)。
  g1_before="$(git status --porcelain "${G1DIR}" 2>/dev/null)"
  mkdir -p "${t5}/blocks" "${t5}/pages"
  if ! ( cd "${G1DIR}" && python3 assign.py --subject "${GATE_SUBJECT}" --json ) \
        > "${t5}/blocks/${GATE_SUBJECT}.json" 2> "${t5}/assign.err"; then
    tail -5 "${t5}/assign.err" | redact | sed 's/^/      /'
    ng "課題ページの割付を作れない (assign.py)"
  elif ! ( cd "${G1DIR}" && python3 build_task_pages.py --subject "${GATE_SUBJECT}" \
             --blocks-dir "${t5}/blocks" --out "${t5}/pages" ) > "${t5}/build.log" 2>&1; then
    tail -8 "${t5}/build.log" | redact | sed 's/^/      /'
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
  # ⚠️ 生成の副作用で実 repo が変わっていないこと (★ 主張でなく検査にする)。
  if [ "$(git status --porcelain "${G1DIR}" 2>/dev/null)" != "${g1_before}" ]; then
    ng "課題ページの生成が実リポジトリを変更した (★ ゲートは副作用を持ってはならない)"
  fi
  rm -rf "${t5:?}"
fi

# --- 6. 記録用紙 (前提条件 6) -----------------------------------------------
head_ 6 "記録用紙に「文字数」欄がある (前提条件 6)"
# ⚠️★★★ **ERE の交替が壊れていた** (code-reviewer M5・2026-09-20 に修正)。
#   ★ 旧式 `'^ *#? *\| *条件|文字数'` は `|` が最上位に効くので
#     `(^ *#? *\| *条件) OR (文字数)` の意味になり、⚠️ **どこかに「文字数」が在れば常に真**。
#     → 「文字数は数えません」と散文で書いてあるだけでも緑になっていた。
#   → ★ **表の行**に「文字数」が在ることを要求する。
if [ ! -f "${SHEET}" ]; then
  ng "確証用の記録用紙が無い: ${SHEET}"
# ⚠️ 表はコードブロックの中にあり、**先頭に `#` 列**がある (`record-sheet-confirmatory.md:40`)。
#   ★ `#?` を許さないと、実体が在るのに赤になる (2026-09-20 に実測して修正)。
elif ! grep -qE '^ *#? *\|.*文字数' "${SHEET}"; then
  ng "記録用紙の表に文字数欄が見つからない (★ 散文での言及は数えない)"
else
  ok "記録用紙の表に「文字数」欄がある"
fi

# --- 7. 途中でやめた人の数え方 (前提条件 7) ---------------------------------
head_ 7 "途中でやめた人の記録の数え方 (前提条件 7)"
echo "     ⚠️ 見ているのは**版が上がり、そこで 3 点に触れているか**だけ。"
echo "        ★ 答えの中身が妥当かは研究者判断であり、ゲートは判定しない。"
rev="$(latest_prereg_rev)"
if [ -z "${rev}" ]; then
  ng "事前登録の改訂履歴を読めない: ${PREREG}"
else
  if [ "${rev}" -lt "${PREREG_REV_FOR_7}" ]; then
    ng "やめた人の数え方が未決 (事前登録は第 ${rev} 版。第 ${PREREG_REV_FOR_7} 版以降の記録が要る)"
  else
    # ⚠️★★★ **版番号だけを proxy にしない** (code-reviewer H2-b)。
    #   ★ 事前登録 `:48-49` が要求しているのは (a) 同意撤回に当たるか / (b) n に数えるか /
    #     (c) 補充するか の **3 点への回答**であって、版が上がったことではない。
    #   ⚠️ **この検査が見ていないもの**: 答えの中身。★ 3 点に**触れている**ことしか見ない。
    sec7="$(prereg_section_for_rev "${PREREG_REV_FOR_7}")"
    miss=""
    printf '%s\n' "${sec7}" | grep -q '前提条件 7\|途中でやめた' || miss="${miss} 前提条件7への言及"
    printf '%s\n' "${sec7}" | grep -q 'n に数え'                || miss="${miss} (b)nに数えるか"
    printf '%s\n' "${sec7}" | grep -q '補充'                    || miss="${miss} (c)補充するか"
    if [ -n "${miss}" ]; then
      ng "第 ${rev} 版にやめた人の数え方の記録が無い (触れていない:${miss})"
    else
      ok "第 ${rev} 版に (a)(b)(c) への言及がある (⚠️ 中身の妥当性は見ていない)"
    fi
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
  # ⚠️★★★ **値を ❌ 行に印字しない** (security-checker M-3)。
  #   ★ 印字すると、操作者が与えた文字列が `expect_red` の照合語に化けて**証拠を偽造できる**。
  echo "     (変異トークン: ${MUT})"
  ng "変異モードで実行した。★ この実行結果を根拠にしてはならない"
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
  local repo fix out sp sf base_red base_green real_red
  # ⚠️★★★ **外側の変異モードを遮断する** (security-checker M-3)。
  #   ★ 遮断しないと fixture 実行にも env が継承され、「空回りしていない」という証拠が壊れる。
  unset GSE_G1_GATE_MUTATE
  MUT=""
  repo="$(pwd)"
  fix="$(mktemp -d "${TMPDIR:-/tmp}/g1gate.XXXXXX")"; GATE_TMPS+=("${fix}")
  sp=0; sf=0

  # ⚠️★★★ **allow-list で写す** (security-checker M-1)。
  #   ★ 旧版は `cp -r` でディレクトリ全体を写してから `pages` / `results` / `handouts` を
  #     消していたので、(a) `blocks/*.json` (**NDJSON のファイル名 = セッション日時**が入る。
  #     `blocks/.gitignore` が一時 public 運用を理由に除外している) が**そのまま写り**、
  #     (b) 被験者向け docx も一度は temp に出て、(c) 将来足されたフォルダは**自動で漏れた**
  #     (= fail-open)。→ ★ 必要なものだけを列挙する (`check-o1-release-readiness.sh` と同じ形)。
  #   ⚠️ 写す先は `mktemp -d` で、正常・中断のどちらでも `gate_cleanup` が消す。
  FIXTURE_FILES="consent.md participant-guide.md record-sheet-confirmatory.md \
                 collection-readiness-record.md preregistration.md config.json SEED \
                 assign.py build_task_pages.py writing-pad.html"
  build () {
    local f
    rm -rf "${fix:?}/w"
    mkdir -p "${fix}/w/scripts" "${fix}/w/${G1DIR}"
    # ⚠️★★ **`cp` の失敗を握りつぶさない** (code-reviewer M8): 部分的に失敗した fixture は
    #   「欠落」系の `expect_red` を**変異と無関係に**通してしまう (= 偽陽性)。
    cp "${SCRIPT_PATH}" "${fix}/w/scripts/gate.sh" \
      || { echo "  ❌ fixture を作れない: gate.sh"; return 1; }
    cp "${repo}/scripts/check_schema_parity.py" "${fix}/w/scripts/" \
      || { echo "  ❌ fixture を作れない: check_schema_parity.py"; return 1; }
    for f in ${FIXTURE_FILES}; do
      cp "${repo}/${G1DIR}/${f}" "${fix}/w/${G1DIR}/${f}" \
        || { echo "  ❌ fixture を作れない: ${f}"; return 1; }
    done
    cp -r "${repo}/${G1DIR}/materials" "${fix}/w/${G1DIR}/materials" \
      || { echo "  ❌ fixture を作れない: materials/"; return 1; }
    # ★ fixture を git リポジトリにし、**コミットを 1 本作る** (Codex /cross-review 1 巡目 #1)。
    #   ⚠️ `init` だけだと HEAD が無く、記録票の「対象のコミット」検査は
    #     **「実在しない → 赤」の経路しか試せない**。★ 正しい SHA で緑になる経路が未検証だった。
    git -C "${fix}/w" init -q > /dev/null 2>&1 || true
    git -C "${fix}/w" -c user.name=gate -c user.email=gate@example.invalid \
        add -A > /dev/null 2>&1 || true
    git -C "${fix}/w" -c user.name=gate -c user.email=gate@example.invalid \
        commit -q -m fixture > /dev/null 2>&1 || true
    FIX_SHA="$(git -C "${fix}/w" rev-parse --short=7 HEAD 2>/dev/null || true)"
  }

  # ★ 記録票を**欄ごとに**現実的な値で埋める。
  #   ⚠️ 一括置換 (`s/（未記入）/日付/g`) は本体側が赤にするようになったので、
  #     selftest も**人が埋めるのと同じ形**で埋める (Codex /cross-review 2 巡目 #1)。
  fill_record () {
    sed_i \
      -e 's/^- 状態: \*\*未実施\*\*/- 状態: **確認済み**/' \
      -e 's/^- 確認日: .*/- 確認日: **2026-09-20**/' \
      -e 's/^- 確認者のロール: .*/- 確認者のロール: **研究者 A**/' \
      -e 's/^- 突合したフォームの定数名: .*/- 突合したフォームの定数名: **G1_CONSENT_FORM_C**/' \
      -e 's/^- 突合の結果: .*/- 突合の結果: **一致していた**/' \
      -e 's/^- 確認した CI の run 番号.*/- 確認した CI の run 番号: **1234 と 1235**/' \
      -e 's/^- 差し替えた配布フォルダの通称.*/- 差し替えた配布フォルダの通称: **G1 課題ページ 秋版**/' \
      -e 's/^- 差し替え後に確認した枚数.*/- 差し替え後に確認した枚数: **10 枚**/' \
      "${fix}/w/${RECORD}"
  }

  # ★ fixture の実行。⚠️ `env -u` で変異モードの継承を**構造的に**断つ。
  run_fixture () { ( cd "${fix}/w" && env -u GSE_G1_GATE_MUTATE bash scripts/gate.sh 2>&1 ) ; }

  # ============================================================================
  # ⚠️★★★ **baseline 照合を恒久の不変量にする** (code-reviewer H1)
  # ============================================================================
  #   ★ fixture は**実物の repo のコピー**なので、実物が前提条件を満たした瞬間に
  #     `sed_i` の変異が **no-op** になる。⚠️ それでも期待どおりの色が出るので、
  #     **ゲートが緑になる直前 = 収集を始める直前に、selftest が最も空回りする。**
  #   ★ 2026-09-20 に手で 1 回検算して 1 件見つけた (「参加案内だけ未追記」)。
  #     → ⚠️ 手の検算は次回には残らない。**変異前の出力と照合する規則**として固定する。
  #   ★ 規則: `expect_red` の照合語が**変異前から ❌ に在る**なら、その検査は何も測っていない。
  #           `expect_green` の照合語が**変異前から ✅ に在る**なら、同じく何も測っていない。
  capture_base () {
    local b
    build || return 1
    b="$(run_fixture)"
    base_red="$(printf '%s\n' "${b}"   | grep -E '^  ❌' || true)"
    base_green="$(printf '%s\n' "${b}" | grep -E '^  ✅' || true)"
    real_red="$( ( cd "${repo}" && env -u GSE_G1_GATE_MUTATE bash "${SCRIPT_PATH}" 2>&1 ) \
                 | grep -E '^  ❌' || true )"
  }

  # $1 = 赤くなるはずの ❌ 行に含まれる語 / $2 = 説明
  expect_red () {
    local pat="$1" label="$2"
    if printf '%s\n' "${base_red}" | grep -q -- "${pat}"; then
      echo "  ❌ ⚠️ 変異前から赤い (この検査は何も測っていない): ${label}"; sf=$((sf+1)); return
    fi
    out="$(run_fixture)"
    if printf '%s\n' "${out}" | grep -E '^  ❌' | grep -q -- "${pat}"; then
      echo "  ✅ 壊すと赤になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: ${label}"; sf=$((sf+1))
    fi
  }
  # ★ 実物の repo に対して撃つ (⚠️ 1 バイトも変更しない)。
  expect_red_real () {
    local token="$1" pat="$2" label="$3"
    if printf '%s\n' "${real_red}" | grep -q -- "${pat}"; then
      echo "  ❌ ⚠️ 変異前から赤い (この検査は何も測っていない): ${label}"; sf=$((sf+1)); return
    fi
    out="$( cd "${repo}" && GSE_G1_GATE_MUTATE="${token}" bash "${SCRIPT_PATH}" 2>&1 )"
    if printf '%s\n' "${out}" | grep -E '^  ❌' | grep -q -- "${pat}"; then
      echo "  ✅ 壊すと赤になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: ${label}"; sf=$((sf+1))
    fi
  }
  # $1 = 緑になるはずの ✅ 行に含まれる語 / $2 = 説明
  expect_green () {
    local pat="$1" label="$2"
    if printf '%s\n' "${base_green}" | grep -q -- "${pat}"; then
      echo "  ❌ ⚠️ 変異前から緑 (この検査は何も測っていない): ${label}"; sf=$((sf+1)); return
    fi
    out="$(run_fixture)"
    if printf '%s\n' "${out}" | grep -E '^  ✅' | grep -q -- "${pat}"; then
      echo "  ✅ 満たすと緑になる: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 満たしても赤のまま: ${label}"; sf=$((sf+1))
    fi
  }

  # ★ **摂動を加えても緑のまま**であること（⚠️ baseline が緑でも空回りではない）。
  #   ★ `expect_green` は「baseline に無い ✅ が変異で出る」ことを見るので、実 repo が満たした後は
  #     使えない（2026-09-26 に前提条件 7 が満たされ、検査 7 の 2 件が空回りに転落した）。
  #   ★ こちらは**変異が入っていること**（呼び出し側が実在の摂動を入れる）を前提に、
  #     $1 の ✅ が残り、$2 の ❌ が**出ない**ことを見る。摂動が効く設計（旧実装なら $2 が出る）にすること。
  expect_stays_green () {
    local pat_ok="$1" pat_ng="$2" label="$3"
    out="$(run_fixture)"
    if printf '%s\n' "${out}" | grep -E '^  ✅' | grep -q -- "${pat_ok}" \
       && ! printf '%s\n' "${out}" | grep -E '^  ❌' | grep -q -- "${pat_ng}"; then
      echo "  ✅ 摂動しても緑のまま: ${label}"; sp=$((sp+1))
    else
      echo "  ❌ 摂動で緑が崩れた: ${label}"; sf=$((sf+1))
    fi
  }

  echo "=== selftest 0: 変異前の出力を取る (★ 以後の照合語をこれと突き合わせる) ==="
  if ! capture_base; then
    echo "  ❌ baseline を取れなかった"; return 1
  fi
  echo "  ✅ baseline: fixture ❌ $(printf '%s\n' "${base_red}" | grep -c . || true) 行 /" \
       "✅ $(printf '%s\n' "${base_green}" | grep -c . || true) 行," \
       "実 repo ❌ $(printf '%s\n' "${real_red}" | grep -c . || true) 行"
  echo

  # ⚠️★★ **照合語はメッセージ固有にする** (★ 別の理由で出た ❌ を拾って偽の合格にしない)。

  echo "=== selftest 1: ファイル系の検査を 1 つずつ壊す ==="
  build; rm -f "${fix}/w/${CONSENT}"
  expect_red "同意文書が無い" "同意文書の欠落 (検査 3)"
  # ⚠️★★★ **2 語目が本当に見られているか**を撃つ (2026-09-20 に検算して差し替えた)。
  #   ★ 旧版は「参加案内だけ未追記」を期待していたが、⚠️ **変異しなくても同じ ❌ が出る**
  #     (参加案内は元から未追記) ので、**空回りで緑を返していた**。
  #   → ★ 1 語目だけ足し、**2 語目で赤になる**ことを見る (baseline に無い ❌)。
  # ⚠️★★★ 検査 3 は 2026-09-26 に「識別子の有無」から「被験者が読む語の行の有無」へ変えた。
  #   ★ 実 repo は緑（内容は 2026-08-20 から表に在る）なので、**壊して赤になること**だけを見る。
  #   ★ 各変異は baseline に無い ❌ を出す（空回りしない）。
  # (1) 表の行を消す。⚠️ 本文の箇条書き（「短い中断」について）は残る → 散文で通らないこと。
  build; sed_i -E '/^\|.*短い中断/d' "${fix}/w/${CONSENT}"
  expect_red "同意文書の記録項目表に「短い中断」" "★ 表から消して散文だけ残す: 短い中断 (検査 3)"
  build; sed_i -E '/^\|.*アプリの版/d' "${fix}/w/${CONSENT}"
  expect_red "同意文書の記録項目表に「アプリの版」" "★ 表から消す: アプリの版 (検査 3)"
  # (2) ⚠️★★★ **「記録しない」側（2 セル目）に入れても緑にしないこと**（code-reviewer M4）。
  build; sed_i -E '/^\|.*短い中断/d' "${fix}/w/${CONSENT}"
  insert_after "${fix}/w/${CONSENT}" '|---|---|' '| — | 短い中断 |'
  expect_red "同意文書の記録項目表に「短い中断」" "★ 記録しない列へ入れる (検査 3)"
  # (3) 参加案内。★ 表のヘッダは「記録します / 記録しません」（同意文書と語尾が違う）。
  build; sed_i -E '/^\|.*短い中断/d' "${fix}/w/${GUIDE}"
  expect_red "参加案内の記録項目表に「短い中断」" "参加案内: 表から消す (検査 3・ヘッダ語尾の対照)"
  build; sed_i -E '/^\|.*アプリの版/d' "${fix}/w/${GUIDE}"
  expect_red "参加案内の記録項目表に「アプリの版」" "参加案内: 表から消す (検査 3)"
  build; rm -f "${fix}/w/${SHEET}"
  expect_red "確証用の記録用紙が無い" "記録用紙の欠落 (検査 6)"
  build; sed_i 's/文字数/字数欄なし/g' "${fix}/w/${SHEET}"
  expect_red "記録用紙の表に文字数欄が見つからない" "記録用紙の文字数欄の喪失 (検査 6)"
  # ⚠️★★★ **散文の言及だけでは緑にしないこと** (code-reviewer M5: ERE 交替の壊れを封じる)。
  #   ⚠️ `\?` は BSD sed の BRE では何にもマッチせず変異が**無音で空振り**する (macOS 実測・2026-09-26)。
  #      → ERE (`-E`) で書く。空振りすると「壊しても緑のまま」と出る。
  build; sed_i -E '/^ *#? *\|/ s/文字数/字数欄なし/g' "${fix}/w/${SHEET}"
  expect_red "記録用紙の表に文字数欄が見つからない" "★ 表から消して散文だけ残す (検査 6)"
  # ⚠️★★★ **前提条件の数が変わったら赤になること** (code-reviewer H3)。
  build; sed_i 's/\*\*1〜7 が終わるまで新コホートの収集を始めない。\*\*/**1〜8 が終わるまで新コホートの収集を始めない。**/' \
                "${fix}/w/${PREREG}"
  expect_red "前提条件の数が変わった可能性がある" "★ 前提条件が 8 個目に増える (検査 0)"
  build; rm -f "${fix}/w/${RECORD}"
  expect_red "人手確認の記録票が無い" "記録票の欠落 (検査 8)"
  build; sed_i 's/^## A\./## Z./' "${fix}/w/${RECORD}"
  expect_red "記録票 A (配布済みフォームとの突合): 節が見つからない" "記録票の見出しの改名 (検査 8)"
  # ⚠️★★★ **状態だけ書き換えても緑にならないこと** (★ 中身の無い確認で通さない)。
  build; sed_i 's/^- 状態: \*\*未実施\*\*/- 状態: **確認済み**/' "${fix}/w/${RECORD}"
  expect_red "記録票 A (配布済みフォームとの突合): 未記入の欄が残っている" \
             "★ 状態だけ確認済みにする (検査 8)"
  # ⚠️★★★ **URL を書いたら赤になること** (security-checker H-1)。
  #   ★ 本 repo は一時 public にする運用があり、フォーム / Drive のリンクは**それ自体が鍵**。
  build; fill_record
  sed_i 's#^- 突合したフォームの定数名: .*#- 突合したフォームの定数名: **https://docs.google.com/forms/d/e/x/viewform**#' \
        "${fix}/w/${RECORD}"
  expect_red "書いてはいけないものが入っている (URL" "★ 記録票に URL を書く (検査 8)"
  # ⚠️★★ **時刻を書いたら赤** (Codex /cross-review 1 巡目 #3: `protocol.md:1112` は日付までと決めている)。
  build; fill_record
  sed_i 's/^- 突合の結果: .*/- 突合の結果: **14:30 に一致を確認**/' "${fix}/w/${RECORD}"
  expect_red "書いてはいけないものが入っている (時刻" "★ 記録票に時刻を書く (検査 8)"
  # ⚠️★★★ **確認日が形になっていないと赤** (code-reviewer M4 相当)。
  build; sed_i 's/^- 状態: \*\*未実施\*\*/- 状態: **確認済み**/; s/（未記入）/済/g' "${fix}/w/${RECORD}"
  expect_red "記録票 A (配布済みフォームとの突合): 確認日が YYYY-MM-DD" \
             "★ 確認日を「済」で埋める (検査 8)"
  # ⚠️★★★ **無関係なコミットを書いたら赤** (code-reviewer M7: 一度埋めたら永久に緑、にしない)。
  build; fill_record
  sed_i 's/^- 対象のコミット: .*/- 対象のコミット: **0000000**/' "${fix}/w/${RECORD}"
  expect_red "対象のコミット 0000000 がこのリポジトリに無い" "★ 実在しないコミットを書く (検査 8)"
  # ⚠️★★★ **一括置換で全部埋めても緑にしないこと** (Codex /cross-review 2 巡目 #1)。
  build; sed_i 's/^- 状態: \*\*未実施\*\*/- 状態: **確認済み**/; s/（未記入）/2026-09-20/g' \
                "${fix}/w/${RECORD}"
  expect_red "確認日以外の欄が日付のまま" "★ 全欄を同じ日付で一括置換する (検査 8)"
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
  fill_record
  expect_green "記録票 A (配布済みフォームとの突合) が埋まっている" "記録票 A を埋める (検査 8)"
  # ★ **正しい SHA なら緑になる**経路 (Codex /cross-review 1 巡目 #1)。
  #   ⚠️ 「実在しない → 赤」だけでは、`merge-base` が常に偽でも気づけない。
  build
  fill_record
  sed_i "s/^- 対象のコミット: .*/- 対象のコミット: **${FIX_SHA}**/" "${fix}/w/${RECORD}"
  expect_green "記録票 B (両 OS の対のテスト) が埋まっている" \
               "★ HEAD の祖先である SHA を書く (検査 8)"
  # ⚠️★★★ **版を上げただけでは緑にならず、3 点に触れて初めて緑になること** (code-reviewer H2-b)。
  #   ⚠️ 2026-09-26 に実 repo が第 20 版で前提条件 7 を満たした。→ ★ 以後は**緑から壊す**:
  #     第 20 版の見出しを第 19 版へ戻す（＝第 20 版の記録が無い）と「未決」で赤になること。
  build
  sed_i 's/^## ★ 改訂履歴 — 第 20 版/## ★ 改訂履歴 — 第 19 版/' "${fix}/w/${PREREG}"
  expect_red "やめた人の数え方が未決" "★ 第 20 版の記録が無い＝未決 (検査 7)"
  # ⚠️★★★ **本文中の前方参照では版が上がらないこと** (code-reviewer H2-a)。
  #   ★ 旧版は文書**全体**を grep していたので、本文の 1 行で `rev` が上がった
  #     (2026-09-20 実測: 全体 24 件ヒットに対し見出しは 18 件)。
  #   ★ 見出しを 20 に上げたうえで**本文に第 25 版の言及**を混ぜる。
  #     → ⚠️ 全体 grep なら `rev=25` になって「config とずれている」で赤。
  #       ★ 見出し限定なら `rev=20` のままで**緑**になる (= この ✅ が出れば限定が効いている)。
  #   ★ 実 repo は既に第 20 版・config 20 で揃っている。→ 本文に第 25 版の言及を混ぜても
  #     「config とずれている」で**赤にならない**（全体 grep の旧実装なら rev=25 で赤）。
  build
  printf '\n★ これは本文中の言及である: 改訂履歴 — 第 25 版 で扱う。\n' >> "${fix}/w/${PREREG}"
  expect_stays_green "config.json の revision が事前登録と同じ版 (20)" "revision が事前登録とずれている" \
                     "★ 本文に第 25 版の言及を混ぜても見出しだけを見る (検査 7)"
  build
  # ★ 版は 20 のまま、⚠️ 3 点の語（「n に数え」「補充」）だけを消す（＝版だけ上げて中身が無い）。
  sed_i 's/n に数え/nに数え/g; s/補充/ほじゅう/g' "${fix}/w/${PREREG}"
  expect_red "やめた人の数え方の記録が無い" "★ 版だけ上げて中身が無い (検査 7)"

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
