#!/usr/bin/env bash
# loop-run.sh — モードC: 無人オーケストレータ。
#   制御 (何回試したか / 同じ失敗か / 予算を超えたか) は "簿記" であって推論ではないので
#   LLM ではなくこのスクリプトが持つ。LLM は 1 attempt の実装だけを担う。
#   events の writer はこのスクリプト。verify の exit code から機械的に記録するため、
#   「done は自己申告」問題が構造的に起きない。
#
#   CLI フラグ/JSON スキーマは claude 2.1.220 で実測済み (docs/loop-engineering.md 構築時 /
#   .steering/_setup-progress.md L5 参照)。`--help` は存在しないフラグも素通りするため、
#   `--max-turns` のような非掲載フラグは実行結果 (subtype/num_turns) で裏取りしている。
#
#   使い方: bash scripts/loop-run.sh <task-dir> [--parallel N] [--issues 001,002] [--dry-run]
set -uo pipefail

PREFIX="[loop-run]"
log()  { echo "$PREFIX $*"; }
die()  { echo "$PREFIX ERROR: $*" >&2; exit 1; }

# ---------- 引数 ----------
TASK_DIR="${1:-}"; [ -n "$TASK_DIR" ] || die "task ディレクトリを指定してください"
shift
PARALLEL_OVERRIDE=""; ONLY_ISSUES=""; DRY_RUN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --parallel) PARALLEL_OVERRIDE="${2:?}"; shift 2 ;;
    --issues)   ONLY_ISSUES="${2:?}";       shift 2 ;;
    --dry-run)  DRY_RUN=1;                  shift   ;;
    *) die "不明な引数: $1" ;;
  esac
done

command -v jq     >/dev/null 2>&1 || die "jq が必要です"
command -v claude >/dev/null 2>&1 || die "claude が PATH にありません"

# ---------- main checkout の解決 (worktree からでも main を掴む) ----------
MAIN_ROOT="$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0,10); exit}')"
[ -n "${MAIN_ROOT:-}" ] || MAIN_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "${MAIN_ROOT:-}" ] || die "git リポジトリ内で実行してください"
cd "$MAIN_ROOT"
case "$TASK_DIR" in /*) : ;; *) TASK_DIR="$MAIN_ROOT/$TASK_DIR" ;; esac
[ -d "$TASK_DIR" ] || die "task ディレクトリが見つかりません: $TASK_DIR"

CFG="$TASK_DIR/_loop-config.json"
[ -f "$CFG" ] || die "_loop-config.json がありません: $CFG"

# ---------- config の読み込みと mode ガード ----------
MODE="$(jq -r '.mode // "A"' "$CFG")"
[ "$MODE" = "C" ] || die "mode が \"$MODE\" です。モードC 用のスクリプトなので中断します
  (A なら scripts/loop-spawn.sh、B なら /loop-orchestrate を使ってください)"

EVENTS="$(jq -r '.events_path' "$CFG")"
[ -n "$EVENTS" ] && [ "$EVENTS" != "null" ] || die "events_path が未設定です"
case "$EVENTS" in /*) : ;; *) die "events_path は絶対パスでなければなりません: $EVENTS" ;; esac
mkdir -p "$(dirname "$EVENTS")"; : >> "$EVENTS"

MAX_ATTEMPTS="$(jq -r '.budget.max_attempts        // 6'       "$CFG")"
NO_PROGRESS="$( jq -r '.budget.no_progress_threshold // 4'     "$CFG")"
TOKEN_CEIL="$(  jq -r '.budget.token_ceiling       // 2000000' "$CFG")"
PARALLEL="$(    jq -r '.budget.parallel            // 1'       "$CFG")"
[ -n "$PARALLEL_OVERRIDE" ] && PARALLEL="$PARALLEL_OVERRIDE"

MAX_TURNS="$(  jq -r '.headless.max_turns       // 30'           "$CFG")"
PERM_MODE="$(  jq -r '.headless.permission_mode // "acceptEdits"' "$CFG")"
WORK_MODEL="$( jq -r '.headless.model           // "sonnet"'      "$CFG")"
WD_MODEL="$(   jq -r '.headless.watchdog_model  // "haiku"'       "$CFG")"
FP_CMD="$(     jq -r '.headless.fingerprint_cmd // empty'         "$CFG")"
MAX_USD="$(    jq -r '.headless.max_budget_usd  // empty'         "$CFG")"
ALLOW_TOOLS="$(jq -r '.headless.allowed_tools   // empty'         "$CFG")"

# 安全側の既定: 昇格モードは明示合意 (LOOP_ALLOW_FULL_ACCESS=1) がない限り拒否する。
# 値は claude 2.1.220 の --permission-mode 選択肢に一致させること
# (acceptEdits / auto / bypassPermissions / manual / dontAsk / plan)。"default" は存在しない。
case "$PERM_MODE" in
  acceptEdits|plan|manual|dontAsk) : ;;
  auto|bypassPermissions)
    [ "${LOOP_ALLOW_FULL_ACCESS:-0}" = "1" ] \
      || die "permission_mode=$PERM_MODE は無人実行の既定として許可されていません。
  worktree 隔離を確認のうえ LOOP_ALLOW_FULL_ACCESS=1 で明示合意してください" ;;
  *) die "permission_mode=$PERM_MODE は claude が受け付けない値です
  (acceptEdits / auto / bypassPermissions / manual / dontAsk / plan)" ;;
esac

# ---------- events writer (このスクリプトが唯一の writer) ----------
emit() { # emit <issue> <phase> <event> [k=v ...]
  local issue="$1" phase="$2" event="$3"; shift 3
  local ts; ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local json; json="$(jq -cn --arg ts "$ts" --arg i "$issue" --arg p "$phase" --arg e "$event" \
                        '{ts:$ts, issue:$i, phase:$p, event:$e}')"
  local kv k v
  for kv in "$@"; do
    k="${kv%%=*}"; v="${kv#*=}"
    # 数値は数値として書く (README 2.4 は attempt/exit を数値と定義。文字列だと jq の
    # 数値比較が壊れ、loop-guard.sh / loop-status の集計が静かに誤る)
    if printf '%s' "$v" | grep -qE '^-?[0-9]+$'; then
      json="$(printf '%s' "$json" | jq -c --arg k "$k" --argjson v "$v" '.[$k]=$v')"
    else
      json="$(printf '%s' "$json" | jq -c --arg k "$k" --arg v "$v" '.[$k]=$v')"
    fi
  done
  # 単一 append。並列時も 1 行は書き込みサイズが小さく O_APPEND で原子的に落ちる
  printf '%s\n' "$json" >> "$EVENTS"
}

# ---------- worktree の必須 permissions.deny を「毎 attempt」保証する ----------
# ⚠️★★★ 注入は worktree 生成時の 1 回では足りない
#   (★ 2026-09-14 に code-reviewer / security-checker が **両方 HIGH** で指摘した):
#   ★ 既定 `permission_mode=acceptEdits` は **Edit/Write を自動承認**し、
#     必須 deny 7 件に Edit / Write 系は 1 件も無い。
#   → ⚠️ attempt N で deny に阻まれた worker が `<worktree>/.claude/settings.local.json` を
#     書き換え・削除すると、**attempt N+1 は新しいセッションなので deny 無しで起動する**。
#   → ★ `claude -p` を起動する **直前に毎回** 注入 (冪等) ＋ 検査を通し、
#     ⚠️ 保証できなければ **起動しない** (fail-closed)。
#   ⚠️ deny は「完全な境界」ではない (綴り違いの迂回は残る)。
#     ★ 実質的な境界は worktree 隔離と人間の merge ゲートである (loop-config.README.md 逐語)。
DENY_SH="$MAIN_ROOT/scripts/loop-worktree-deny.sh"
ensure_deny() { # ensure_deny <worktree>; 0 = 必須 deny が効いている
  [ -f "$DENY_SH" ] || return 1
  bash "$DENY_SH" "$1" >/dev/null 2>&1
}

# ---------- issue のメタ抽出 ----------
issue_file() { printf '%s/issues/%s.md' "$TASK_DIR" "$1"; }
issue_ids() {
  ls "$TASK_DIR"/issues/*.md 2>/dev/null | while read -r f; do basename "$f" .md; done | sort
}
issue_field() { # issue_field <id> <見出し> → 該当セクションの本文
  awk -v h="## $2" '$0==h{f=1;next} /^## /{f=0} f' "$(issue_file "$1")"
}
# ⚠ `## Dependencies` の 3 桁数字を無差別に拾うと、散文中の言及まで依存として拾ってしまう
#    (「issue 004 の merge 後に…」という説明文で自己依存デッドロックが起きる)。
#    → 箇条書き行の先頭にある id だけを拾い、自己依存は落とす。
#      推奨する書式:  - 003
#                     - 004  (loader の変更が前提)
issue_deps_raw() { # 自己依存も含めてそのまま返す (preflight が検出するため)
  issue_field "$1" Dependencies \
    | grep -oE '^[[:space:]]*[-*][[:space:]]*(#|issue[[:space:]]*)?[0-9]{3}\b' \
    | grep -oE '[0-9]{3}' \
    | sort -u
}
issue_deps() { # 実行時に使う版。自己依存は落としてデッドロックを避ける
  issue_deps_raw "$1" | grep -vx "$1" || true
}
issue_verify_level() { grep -m1 -E '^verify_level:' "$(issue_file "$1")" | awk '{print $2}'; }

# ---------- fingerprint ----------
# ⚠ 既定の抽出を `grep -aiE 'fail|error|assert'` だけにしてはならない。
#    lint / typecheck の出力には "fail" も "error" も "assert" も現れないことが多く、
#    **フィルタが空になって fingerprint が sha1("") に潰れる**
#    (例: ruff `app.py:42:1: E501 ...` / mypy `app.py:12: note: ...` はマッチしない)。
#    さらに `Found 2 errors.` のような**件数行だけ**が残ると、
#    中身の違う 2 つの失敗が同じ fingerprint になり「前進していないのに前進扱い」になる。
#    → 診断行らしきものを広めに拾い、**何も残らなければ生出力にフォールバックする**。
fingerprint() { # stdin = verify 出力
  if [ -n "${FP_CMD:-}" ]; then eval "$FP_CMD"; else
    _fp_normalize() {
      # 実行ごとに変わるが失敗の同一性とは無関係なものを落とす
      sed -E 's/[0-9]{2}:[0-9]{2}:[0-9]{2}//g
              s/0x[0-9a-f]+//g
              s/[0-9]+(\.[0-9]+)?s\b/Ns/g
              s#/(private/)?(tmp|var)/[A-Za-z0-9._-]+#TMP#g'
    }
    local raw kept
    raw="$(cat)"
    # cargo test/clippy/tsc + "file:line[:col]:" 形式の診断を拾う。
    # 件数だけの行 (Found 3 errors / test result: FAILED. N passed) は同一性の判断に使えないので落とす。
    kept="$(printf '%s\n' "$raw" \
            | grep -aE '(FAILED|FAIL|ERROR|error\[|error:|warning:|panicked at|assert|Assertion|thread .* panicked|^E )|^[^:[:space:]]+:[0-9]+(:[0-9]+)?:' \
            | grep -avE '^(Found|Checked|Ran|Collected|test result:) ' \
            | head -40)"
    # ここを空のままにすると sha1("") に潰れ、全ての失敗が同一と判定されて
    # budget.no_progress_threshold による停止が**実質的に機能しなくなる**。
    [ -n "$kept" ] || kept="$(printf '%s\n' "$raw" | tail -40)"
    printf '%s\n' "$kept" | _fp_normalize
  fi | shasum | awk '{print $1}'
}

# ---------- watchdog (verify_level: recheck の独立再検証) ----------
# ⚠ watchdog を `--permission-mode plan` で呼んではならない (「独立に verify を再実行して
#    緑を客観確認する」役割と plan mode の「コマンド実行に承認が必要」が構造的に矛盾する)。
#    → 検証コマンドの実行だけを許可し (Edit/Write は与えない = 実質 read-only)、
#      verdict は 1 行目の 1 語に固定して先頭一致で判定する (応答全文への部分一致は
#      理由文中の "NG" という 2 文字を拾う事故を招く)。
#    ※ verify はテストを実行するので「副作用ゼロ」ではない。read-only とは
#      「リポジトリのファイルを書き換えない」という意味である。
WD_TOOLS="Read,Glob,Grep,Bash(cargo test:*),Bash(cargo clippy:*),Bash(cargo check:*),Bash(cargo run:*),Bash(npx tsc:*),Bash(npm test:*),Bash(npm run:*),Bash(git diff:*),Bash(git status:*),Bash(echo:*),Bash(cat:*),Bash(ls:*),Bash(head:*),Bash(tail:*),Bash(grep:*),Bash(rg:*),Bash(wc:*),Bash(test:*)"

run_watchdog() { # run_watchdog <id> <worktree> <attempt>; 0=OK, 1=NG
  local id="$1" wt="$2" attempt="$3" wres verdict head try
  # ⚠️ watchdog も worktree 内の完全なセッションなので、起動前に deny を保証する。
  if ! ensure_deny "$wt"; then
    emit "$id" verify blocked attempt="$attempt" \
         detail="watchdog 起動前に worktree の必須 permissions.deny を保証できない。deny 無しでは起動しない"
    return 1
  fi
  for try in 1 2; do
    wres="$( (cd "$wt" && claude -p "issue $id の Acceptance Criteria を実際に充足しているか、
必要なら verify コマンドを自分で実行して確認せよ。
**出力の 1 行目は OK か NG のどちらか 1 語だけ**にし、2 行目以降に理由を書くこと。" \
          --max-turns 20 --permission-mode acceptEdits --allowedTools "$WD_TOOLS" \
          --model "$WD_MODEL" --output-format json) 2>&1 )"
    add_usage "$(printf '%s' "$wres" | usage_tokens)" \
              "$(printf '%s' "$wres" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo 0)"
    verdict="$(printf '%s' "$wres" | jq -r '.result // ""' 2>/dev/null)"
    # 1 行目だけを見る。理由文中の "NG" を拾わないため部分一致は使わない。
    head="$(printf '%s' "$verdict" | head -1 | tr -d '[:space:]*_`#')"
    case "$head" in
      OK|ok|Ok) return 0 ;;
      NG|ng|Ng) emit "$id" verify blocked attempt="$attempt" \
                     detail="AC 未充足: $(printf '%s' "$verdict" | head -c 200)"; return 1 ;;
    esac
    # 空応答 / 想定外の 1 行目 → 1 度だけ再試行する (実測で空応答が観測されている)。
    log "issue $id: watchdog の応答を解釈できません (try $try): $(printf '%s' "$verdict" | head -c 80)"
  done
  # 2 回とも解釈できなければ fail-closed (緑と断定しない)
  emit "$id" verify blocked attempt="$attempt" \
       detail="watchdog の verdict を解釈できず fail-closed (空応答/書式違反)。verify_level を parse に落とすか acceptance スクリプトでの機械検査を検討する"
  return 1
}

# > **未解決の既知の限界**: `recheck` の watchdog は現状まだ完全に信頼できる gate ではない。
# > 空応答を返すことがある (上の再試行 + fail-closed はその対策)。
# > **AC を機械的に検査できるなら `<id>-acceptance.sh` を書くほうが確実**であり、
# > watchdog はその補助と考えること。

# ---------- verify ----------
# ⚠ 呼び出し規約に注意: `kind="$(run_verify "$wt")"` の形で呼んではならない。
#   `$( )` はサブシェルを作るので、内部で書き込む変数は親に戻らない。
#   結果 fingerprint が常に sha1("") = da39a3ee5e6b4b0d3255bfef95601890afd80709 になり、
#   `budget.no_progress_threshold` による停止が**実質的に機能しなくなる**。
#   → コマンド置換をやめる。出力は**一時ファイル**で受け渡し、失敗種別はグローバル変数で返す。
#      呼び出し側は `if run_verify "$wt"; then` の形で直接 exit code を見ること。
#      **`$(run_verify ...)` の形に戻してはならない。**
VERIFY_KIND=""      # run_verify が設定する失敗種別
VERIFY_OUT_FILE=""  # run_verify が設定する出力ファイルのパス

run_verify() { # run_verify <worktree> <issue-id> <out-file>; 失敗種別は $VERIFY_KIND に
  local wt="$1" id="$2" out_file="$3" rc
  VERIFY_KIND=""
  VERIFY_OUT_FILE="$out_file"
  : > "$out_file"
  local key cmd
  for key in test typecheck lint; do
    cmd="$(jq -r --arg k "$key" '.verify[$k] // empty' "$CFG")"
    [ -n "$cmd" ] || continue
    ( cd "$wt" && eval "$cmd" ) >> "$out_file" 2>&1; rc=$?
    if [ $rc -ne 0 ]; then
      case "$key" in test) VERIFY_KIND=test_fail ;; typecheck) VERIFY_KIND=typecheck_fail ;; lint) VERIFY_KIND=lint_fail ;; esac
      return 1
    fi
  done

  # --- acceptance: AC を機械的に検査する段 ---
  # test/typecheck/lint が無条件に緑になる issue (docs 同期・設定変更など) では
  # この段が無いと **AC 未充足のまま issue_done** になる。
  # 規約: issue <id> の acceptance スクリプトは $TASK_DIR/issues/<id>-acceptance.sh。
  #       存在する issue だけこの段を走らせる (無い issue は従来どおり skip)。
  #       スクリプトは **worktree の中で** 実行され、exit 0 = AC 充足。
  local acc; acc="$TASK_DIR/issues/$id-acceptance.sh"
  if [ -f "$acc" ]; then
    ( cd "$wt" && bash "$acc" ) >> "$out_file" 2>&1; rc=$?
    if [ $rc -ne 0 ]; then VERIFY_KIND=acceptance_fail; return 1; fi
  fi
  return 0
}

# ---------- 予算の積算 (claude -p --output-format json の usage / total_cost_usd) ----------
# 注意 (実測): usage.input_tokens は **キャッシュ分を含まない**。
#   input+output だけ足すと 3 桁規模で過小計上し token_ceiling が永久に発火しない。
#   → cache_read / cache_creation を必ず加算する。
TOKENS_FILE="$(mktemp)"; echo 0 > "$TOKENS_FILE"
COST_FILE="$(mktemp)";   echo 0 > "$COST_FILE"

# verify 出力の受け渡し用。コマンド置換を使わずに親へ返すため実ファイルを使う
# (詳細は run_verify のコメント)。
WORK_TMP="$(mktemp -d)"
cleanup_tmp() { rm -rf "$WORK_TMP" "$TOKENS_FILE" "$COST_FILE" "$TOKENS_FILE.lock" 2>/dev/null || true; }
trap cleanup_tmp EXIT

usage_tokens() { # stdin = claude の JSON → 合計トークン
  jq -r '(.usage.input_tokens // 0) + (.usage.output_tokens // 0)
       + (.usage.cache_read_input_tokens // 0) + (.usage.cache_creation_input_tokens // 0)' 2>/dev/null || echo 0
}

add_usage() { # add_usage <tokens> <cost_usd>  並列からも安全に加算 (flock があれば使う)
  local n="${1:-0}" c="${2:-0}"
  _acc() {
    echo $(( $(cat "$TOKENS_FILE") + n )) > "$TOKENS_FILE"
    awk -v a="$(cat "$COST_FILE")" -v b="$c" 'BEGIN{printf "%.6f", a+b}' > "$COST_FILE"
  }
  if command -v flock >/dev/null 2>&1; then ( flock 9; _acc ) 9>>"$TOKENS_FILE.lock"; else _acc; fi
}
tokens_used() { cat "$TOKENS_FILE"; }
cost_used()   { cat "$COST_FILE"; }

# ---------- 1 issue の attempt ループ ----------
run_issue() {
  local id="$1" wt attempt=1 same=0 last_fp="" fp
  wt="$(LOOP_NO_EXEC=1 bash "$MAIN_ROOT/scripts/loop-spawn.sh" --no-exec "$id" 2>/dev/null | tail -1)"
  [ -d "${wt:-}" ] || { emit "$id" execute blocked detail="worktree 生成に失敗"; return 1; }

  while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
    if [ "$(tokens_used)" -ge "$TOKEN_CEIL" ]; then
      emit "$id" execute abandoned attempt="$attempt" detail="token_ceiling 超過"; return 1
    fi
    emit "$id" execute attempt_start attempt="$attempt"

    # ⚠️★★★ **毎 attempt** 必須 deny を保証する (★ 詳細は ensure_deny の冒頭)。
    if ! ensure_deny "$wt"; then
      emit "$id" execute blocked attempt="$attempt" \
           detail="worktree の必須 permissions.deny を保証できない (注入/検査に失敗)。deny 無しでは起動しない"
      return 1
    fi

    # --- 完全なセッションを 1 回。hook / スラッシュコマンド / settings が効く ---
    local res subtype denials
    local -a cargs=( -p "/loop-issue $id"
                     --max-turns "$MAX_TURNS"
                     --permission-mode "$PERM_MODE"
                     --model "$WORK_MODEL"
                     --output-format json )
    [ -n "${MAX_USD:-}" ]     && cargs+=( --max-budget-usd "$MAX_USD" )
    [ -n "${ALLOW_TOOLS:-}" ] && cargs+=( --allowedTools "$ALLOW_TOOLS" )
    res="$( (cd "$wt" && claude "${cargs[@]}") 2>&1 )"

    add_usage "$(printf '%s' "$res" | usage_tokens)" \
              "$(printf '%s' "$res" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo 0)"

    # --- セッションの終わり方を分類する (実測スキーマに基づく) ---
    subtype="$(printf '%s' "$res" | jq -r '.subtype // "unknown"' 2>/dev/null || echo unknown)"
    case "$subtype" in
      error_max_turns)
        # max_turns 到達は is_error:true だが「attempt が終わった」だけ。
        # run 全体の失敗ではないので、このまま verify に進む (ここで止めると 1 回で全部死ぬ)。
        emit "$id" execute attempt_start attempt="$attempt" detail="max_turns 到達 (attempt 打ち切り)" ;;
      success) : ;;
      *)
        emit "$id" execute blocked attempt="$attempt" \
             detail="セッション異常終了 subtype=$subtype $(printf '%s' "$res" | jq -r '.api_error_status // ""' 2>/dev/null)"
        return 1 ;;
    esac

    # --- 権限拒否は「記録するが致命扱いしない」 ---
    # ⚠ denial が 1 件でもあれば return 1 する実装は間違い。
    #    events_path は main checkout の絶対パスであり worktree の cwd 境界の外にあるため、
    #    append しようとすると**必ず**拒否される。無関係なディレクトリを 1 度覗いただけでも同じ。
    #    「静かな停滞」を防ぐ意図は **1 行必ず残す**ことで満たされる。
    #    **合否は run_verify の exit code だけが決める。** ここで return してはならない。
    denials="$(printf '%s' "$res" | jq -r '(.permission_denials // []) | length' 2>/dev/null || echo 0)"
    if [ "${denials:-0}" -gt 0 ]; then
      emit "$id" execute attempt_start attempt="$attempt" \
           detail="permission_denials=$denials (非致命・verify の exit code で判定する)"
    fi

    # --- 客観検証: exit code がすべて。LLM の申告は読まない ---
    # ⚠ `$(run_verify ...)` の形で呼ばないこと (サブシェルで VERIFY_* が失われる)。
    local vout="$WORK_TMP/verify-$id.out"
    if run_verify "$wt" "$id" "$vout"; then
      local lvl; lvl="$(issue_verify_level "$id")"
      if [ "$lvl" = "recheck" ]; then
        if ! run_watchdog "$id" "$wt" "$attempt"; then return 1; fi
      fi
      emit "$id" done issue_done attempt="$attempt"
      log "issue $id: done (attempt $attempt)"
      return 0
    fi

    # 一時ファイルから fingerprint を作る (サブシェル経由だと必ず sha1("") になる)
    fp="$(fingerprint < "$vout")"
    # 保険: 空出力なら fingerprint は無意味なので no-progress 判定に使わない
    if [ ! -s "$vout" ]; then
      emit "$id" verify "$VERIFY_KIND" attempt="$attempt" exit=1 fingerprint="$fp" \
           detail="WARN: verify 出力が空。fingerprint は無効として no-progress 判定に使わない"
      last_fp=""; same=0
      attempt=$((attempt+1)); continue
    fi
    emit "$id" verify "$VERIFY_KIND" attempt="$attempt" exit=1 fingerprint="$fp"
    if [ "$fp" = "$last_fp" ]; then same=$((same+1)); else same=1; last_fp="$fp"; fi
    if [ "$same" -ge "$NO_PROGRESS" ]; then
      emit "$id" verify no_progress_stop attempt="$attempt" fingerprint="$fp" \
           detail="同一 fingerprint × $same"
      log "issue $id: no_progress_stop"; return 1
    fi
    attempt=$((attempt+1))
  done
  emit "$id" verify abandoned attempt="$MAX_ATTEMPTS" detail="max_attempts 到達"
  return 1
}

# ---------- DAG 解決と実行 ----------
declare -a READY DONE_IDS
ALL="$(issue_ids)"
[ -n "$ONLY_ISSUES" ] && ALL="$(printf '%s' "$ONLY_ISSUES" | tr ',' '\n')"
[ -n "$ALL" ] || die "issues/ に issue がありません"

# ⚠ DONE_IDS を空で始めてはならない。
#    ウェーブを分けて**別プロセスで**起動する運用では、`## Dependencies` に issue 番号を書くと
#    2 波目で deps_met() が永久に false になり、対象 issue が**一度も実行されないまま終わる**。
#    → 起動時に events から既完了を seed する。
if [ -f "$EVENTS" ]; then
  while read -r seeded; do
    [ -n "$seeded" ] || continue
    DONE_IDS+=("$seeded")
  done <<< "$(jq -r -s '[.[] | select(.event=="issue_done") | .issue] | unique | .[]' "$EVENTS" 2>/dev/null || true)"
  [ "${#DONE_IDS[@]:-0}" -gt 0 ] && log "events から完了済みを復元: ${DONE_IDS[*]}"
fi

is_done() { printf '%s\n' "${DONE_IDS[@]:-}" | grep -qx "$1"; }
deps_met() { local d; for d in $(issue_deps "$1"); do is_done "$d" || return 1; done; return 0; }

# 自己依存・存在しない依存・循環を起動前に検出して die する (デッドロックで黙って止まらないため)
preflight_dag() {
  local id d bad=0
  for id in $ALL; do
    for d in $(issue_deps_raw "$id"); do
      if [ "$d" = "$id" ]; then
        echo "loop-run: issue $id が自分自身に依存しています。## Dependencies の箇条書きから
         '$id' を削除してください (散文で自分に言及したい場合は箇条書きにしない)" >&2; bad=1
      elif ! printf '%s\n' $ALL | grep -qx "$d"; then
        echo "loop-run: issue $id の依存 $d が issues/ に存在しません" >&2; bad=1
      fi
    done
  done
  [ "$bad" = "0" ] || die "DAG の前提が壊れています (上記を修正してください)"
}
preflight_dag

if [ "$DRY_RUN" = "1" ]; then
  log "--dry-run: 実行計画"
  for id in $ALL; do printf '  %s  deps=[%s] verify_level=%s acceptance=%s\n' \
      "$id" "$(issue_deps "$id" | tr '\n' ' ')" "$(issue_verify_level "$id")" \
      "$([ -f "$TASK_DIR/issues/$id-acceptance.sh" ] && echo yes || echo no)"; done
  log "parallel=$PARALLEL max_attempts=$MAX_ATTEMPTS token_ceiling=$TOKEN_CEIL"
  log "既完了 (events から): ${DONE_IDS[*]:-なし}"
  log "⚠ --dry-run で検証できるのは config / DAG まで。権限 (allowed_tools) / cwd 境界 / hook /"
  log "  契約の二重定義は --dry-run では観測できない。初回は最も安い issue 1 本を parallel=1 で回すこと。"
  exit 0
fi

log "開始: task=$(jq -r .task "$CFG") parallel=$PARALLEL mode=C"
remaining="$ALL"; progressed=1
while [ -n "$remaining" ] && [ "$progressed" = "1" ]; do
  progressed=0; batch=""
  for id in $remaining; do
    deps_met "$id" || continue
    batch="$batch $id"
    [ "$(printf '%s' "$batch" | wc -w)" -ge "$PARALLEL" ] && break
  done
  [ -n "$batch" ] || break
  pids=""
  for id in $batch; do run_issue "$id" & pids="$pids $!"; done
  for p in $pids; do wait "$p" || true; done
  for id in $batch; do
    # キー順に依存しないよう jq で判定する (grep の順序前提は静かに壊れる)
    if jq -e -s --arg i "$id" 'any(.[]; .issue==$i and .event=="issue_done")' "$EVENTS" >/dev/null; then
      DONE_IDS+=("$id"); progressed=1
    fi
    remaining="$(printf '%s\n' $remaining | grep -vx "$id" || true)"
  done
done

# 依存先が落ちて起動できなかった issue を明示的に blocked にする (握りつぶさない)
for id in $remaining; do emit "$id" execute blocked detail="依存 issue が未完のため未実行"; done

# ---------- レポート ----------
REPORT="$TASK_DIR/_loop-run-report.md"
{
  echo "# Loop Run Report — $(jq -r .task "$CFG")"
  echo; echo "実行日時: $(date -u +%Y-%m-%dT%H:%M:%SZ) / mode=C / parallel=$PARALLEL"
  echo "tokens: $(tokens_used) / $TOKEN_CEIL  (cache 込み) · cost: \$$(cost_used)"
  echo; echo "| issue | 最終 event | attempt |"; echo "|---|---|---|"
  for id in $ALL; do
    line="$(jq -c -s --arg i "$id" '[.[] | select(.issue==$i)] | last // {}' "$EVENTS")"
    printf '| %s | %s | %s |\n' "$id" \
      "$(printf '%s' "$line" | jq -r '.event // "-"')" \
      "$(printf '%s' "$line" | jq -r '.attempt // "-"')"
  done
  echo; echo "次: /loop-status で board を確認 → 全緑なら code-reviewer(Opus) と /cross-review"
} > "$REPORT"
log "レポート: $REPORT"
