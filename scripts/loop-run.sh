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
#   終了コード: 0 = 完走 (失敗した issue があっても・token_ceiling で中止しても) / 3 = 境界侵害で run を中止 / 1 = 起動前エラー
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

# ⚠️★★★ TASK_DIR の repo 相対パス (worktree 側の issue ファイルを引く土台・2026-09-25 追加)。
#   ★ MAIN_ROOT は `C:/...`、TASK_DIR は `/c/...` のように git-bash で表記が揺れうるので、
#     文字列の前方一致 (`${TASK_DIR#$MAIN_ROOT}`) では剥がせない (実測: 揺れると一致しない)。
#   → git 自身に相対パスを聞く。worktree はリポジトリ全体をミラーするので、
#     この相対パスは worktree ルート以下でもそのまま通用する。
TASK_DIR_RELPATH="$(git -C "$TASK_DIR" rev-parse --show-prefix 2>/dev/null)"
TASK_DIR_RELPATH="${TASK_DIR_RELPATH%/}"
[ -n "$TASK_DIR_RELPATH" ] || die "TASK_DIR の repo 相対パスを解決できません: $TASK_DIR"

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
#
# ⚠️★★★ **黙って自己修復しない**（★ Codex /cross-review HIGH・2026-09-14）:
#   ★ 先に `--verify` で**現状を見てから**直す。⚠️ いきなり再注入すると
#     「安全設定が消されていた」という**無人ループで最も記録に値する事実**が
#     events に 1 行も残らない。★ 検知（記録）と回復（再注入）を分ける。
DENY_SH="$MAIN_ROOT/scripts/loop-worktree-deny.sh"
# ⚠️★★★ **境界侵害の印**（★ 2026-09-27・`security-checker` MEDIUM）。
#   ★ ensure_deny / ensure_branch が blocked を返すのは「worker を隔離できていない」ときであり、
#     ⚠️ 同じ run で次の issue を spawn すると、逸脱した worker が base に残したものから切りうる。
#   ★ run_issue はバックグラウンドのサブシェルで動き変数を親へ返せないので、**ファイル**で伝える。
#     親の DAG ループがバッチの後にこれを見て run を中止する。
#   ⚠️ 書けなかったら黙らない（★ `code-reviewer` LOW: 印が消えると run が続く = fail-open）。
mark_boundary_breach() {
  printf '%s\n' "$1" >> "$WORK_TMP/boundary-breach" 2>/dev/null \
    || log "⚠️★★★ 境界侵害の印を書けなかった (issue $1)。run は止まらない可能性がある —— events の blocked を確認すること"
}
ensure_deny() { # ensure_deny <issue> <phase> <attempt> <worktree>; 0 = 必須 deny が効いている
  local id="$1" phase="$2" attempt="$3" wt="$4"
  if [ ! -f "$DENY_SH" ]; then
    emit "$id" "$phase" blocked attempt="$attempt" \
         detail="必須 deny の注入スクリプトが無い: $DENY_SH"
    mark_boundary_breach "$id"
    return 1
  fi
  bash "$DENY_SH" --verify "$wt" >/dev/null 2>&1 && return 0
  # ⚠️ 失われていた事実を必ず 1 行残す
  #   (★ 書式は既存の permission_denials / max_turns と同じ「attempt_start ＋ detail」に揃える。
  #    ⚠️ events 語彙は 10 種で固定なので新しい event 値を作らない)
  #
  # ⚠️★★★ **phase は呼び出し元に関わらず `execute` で出す** (★ Codex /cross-review 2 巡目)。
  #   ★ `loop-status` の折り畳み表は逐語「`attempt_start` → 🔄 running (**phase=execute**)」であり、
  #     ⚠️ `phase=verify` の `attempt_start` は**表に無い組み合わせ**になって board が解釈できない。
  #   ★ 不変条件はこう置く: **`detail` の無い `attempt_start` が attempt ごとにちょうど 1 件**。
  #     ⚠️ `detail` 付きは「その attempt の中で起きたこと」の記録であり、attempt の数ではない
  #     (★ 既存の max_turns / permission_denials も同じ作法。`loop-status` は件数ではなく
  #      **最後の event** を見るので、この重複で board は壊れない)。
  emit "$id" execute attempt_start attempt="$attempt" \
       detail="WARN: worktree の必須 permissions.deny が失われていた (削除/改ざん)。再注入を試みる"
  bash "$DENY_SH" "$wt" >/dev/null 2>&1 && return 0
  emit "$id" "$phase" blocked attempt="$attempt" \
       detail="worktree の必須 permissions.deny を保証できない (注入/検査に失敗)。deny 無しでは起動しない"
  mark_boundary_breach "$id"
  return 1
}

# ---------- worktree が期待どおりのブランチに居ることを保証する ----------
# ⚠️★★★ **これが worktree 隔離の「境界」である**（★ 起票 10 の是正・判断 1 / 2・2026-09-20）。
#   ★ 実測（2026-09-15・issue 004）で worker が `git checkout main` を打ち、
#     worktree が `main` を掴んだまま attempt が終わった。reflog 逐語:
#       `92fd22f HEAD@{0}: checkout: moving from loop/004-issue to main`
#   ⚠️ このとき `run_verify` は **別ブランチの内容を検査して緑/赤を出す**。
#
# ⚠️★★★ **`deny` では閉じない**（★ 2026-09-20 に実測 —— `measurements.md` M3）:
#   ★ 必須 deny に `Bash(git checkout:*)` を足しても、**`git -C . checkout main` は
#     拒否 0 件で通り、ブランチが動いた**。前置一致は綴りを網羅できない。
#   → ★ だから**到達した綴りを問わず、結果（HEAD）だけを見る**。
#
# ⚠️ **自動で戻さない**（★ 判断 2）。`ensure_deny` は「検知して再注入」する型だが、
#   ここは違う: ★ 未コミットの変更を抱えたまま `git checkout` で戻すと、
#   **変更が別ブランチへ持ち越されるか checkout 自体が失敗する**。
#   ⚠️ 起票 10 の実害が「無かった」のは worker が commit **後**に checkout したからで、
#   ★ 自動復帰はその偶然に依存する設計になる。→ **記録して止める (fail-closed)**。
#
# ⚠️★★★ **ブランチ「名」だけでは、名前を保ったままの履歴入れ替えを見逃す**
#   （★ `security-checker` MEDIUM・2026-09-20）。★ `git reset --soft|--mixed <other>` /
#   `git branch -f loop/<id>-issue <other>` は **HEAD の symbolic ref を保ったまま**中身を差し替える
#   （⚠️ deny に在るのは `git reset --hard:*` だけである）。
#   → ★ 第 5 引数に「**worktree を作った時点の commit**」を渡したときは、
#     **現 HEAD がその子孫であること**も見る。
#
#   ⚠️★★★ **アンカーは「attempt 開始前の HEAD」にしてはならない**
#     （★ Codex `/cross-review` HIGH・2026-09-20。⚠️ 最初はそう書いていた）:
#     ★ attempt 2 の worker が **attempt 1 のコミットを `git commit --amend`** すると、
#       新しい HEAD は同じ親を持つ別コミットになり、⚠️ **直前の HEAD は祖先でなくなる**。
#       → ★ 正当な作業が blocked になる（`git commit --amend` は deny に無い）。
#     ★ **worktree 生成時点**に固定すれば、worker が自分のコミットをどう作り直しても
#       アンカーは常に祖先のままであり、⚠️ **他ブランチへの差し替えだけが不一致になる**。
#
# ⚠️★★★ **それでも見ていないもの**（★ 明示する。⚠️ 2 つある）:
#   (a) `git restore --source=<other> -- .` / `git read-tree -u` のような
#       **HEAD を 1 mm も動かさない内容の差し替え**は原理的に拾えない。
#   (b) **同じブランチ内の巻き戻し** —— `git reset --soft|--mixed <anchor>` は
#       HEAD がアンカーそのものになるので `--is-ancestor` は **TRUE を返す**
#       （★ 2026-09-20 に実測。Codex `/cross-review` 2 巡目 HIGH）。
#       ⚠️ ただし **`--soft` / `--mixed` は作業ツリーを保つ**ので、
#       ★ `run_verify` が測る内容は worker の成果物のままである（★ これも実測した）。
#       → ★ 害は「**コミットが捨てられる**」であって「**別の内容を測る**」ではない。
#       ★ これは判断 5（「未コミットで終わる」を失敗にしない）と**同じ型**として**許容する**。
#       ⚠️ `git reset --hard` は deny に在るので別（★ そちらは作業ツリーも消す）。
#   ★ ここが「境界」の限界である。⚠️ **deny で塞ぐ方向に戻さない**（★ M3 のとおり閉じない）。
ensure_branch() { # ensure_branch <issue> <phase> <attempt> <worktree> [worktree生成時の-sha]; 0 = 期待どおり
  local id="$1" phase="$2" attempt="$3" wt="$4" base="${5:-}" head
  # ★ detached HEAD は `HEAD` という文字列が返るので、下の case に当たらず不一致になる (正しい)。
  head="$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  case "$head" in
    # ★ 前方一致にする: `loop-spawn.sh` の branch は `loop/<id>-<short>` で、
    #   ⚠️ `short` は第 2 引数で可変（モードC は省略して既定 `issue`）。
    #   ★ 厳密一致にすると将来 short を渡した瞬間に全 attempt が blocked になる。
    "loop/$id"|"loop/$id-"*) : ;;
    *)
      emit "$id" "$phase" blocked attempt="$attempt" \
           detail="worktree が loop/$id-* から外れている (HEAD=${head:-取得不能})。別ブランチを verify しないため停止する。★ worktree は残す: ${wt} ／ ★ 撤去は「bash scripts/loop-spawn.sh --cleanup ${id}」(★ 2026-09-21 に起票 18 を是正し、逸脱した worktree も**パスで**引いて撤去できるようになった。⚠️ 撤去できなければ非 0 で止まる)"
      mark_boundary_breach "$id"
      return 1 ;;
  esac
  if [ -n "$base" ] && ! git -C "$wt" merge-base --is-ancestor "$base" HEAD 2>/dev/null; then
    emit "$id" "$phase" blocked attempt="$attempt" \
         detail="worktree の履歴が入れ替わっている (HEAD=$head が worktree 生成時の $base の子孫でない)。★ reset --soft/--mixed や branch -f で中身が差し替わった可能性。★ worktree は残す: $wt"
    mark_boundary_breach "$id"
    return 1
  fi
  return 0
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
# ⚠️★★★ P1-D（design.md 判断 7）: `- **001**（説明）` のように強調で囲まれると、
#   装飾を剥がす前の正規表現は一致しない。→ ★ 行ごとに `*` `_` `` ` `` を剥がしてから拾う
#   (issue_status_key が装飾を剥がすのと同じ発想)。
# ⚠️★★★ ただし箇条書きの `*` は**先に `-` へ正規化してから**剥がす (2026-09-26 メインのレビュー)。
#   ★ `s/[*_`]//g` だけだと `* 001` の箇条書き記号まで消え、従来の `[-*]` が受けていた書式が拾えなくなる。
deps_section_plain() { # deps_section_plain <id> → 装飾を剥がした Dependencies 節
  issue_field "$1" Dependencies \
    | sed -e 's/^\([[:space:]]*\)[*]\([[:space:]]\)/\1-\2/' -e 's/[*_`]//g' \
    | LC_ALL=C tr -c '\11\12\40-\176' ' '
  # ⚠️★★★ 非 ASCII のバイトを空白に置き換える (★ 2026-09-26 PR #224 の Windows CI で実測)。
  #   ★ 下流の `\b` は、ロケールが C の環境 (self-hosted runner は NetworkService で動く) では
  #     マルチバイト文字のバイトを単語の一部とみなし、`- 001（説明）` の `001` と `（` の間に境界を作らない
  #     → **依存を黙って落とす** (P1-D の再発)。手元の UTF-8 ロケールでは再現しない。
  #   → ★ 依存の判定に要るのは ASCII だけなので、非 ASCII を空白にしてからロケール非依存で拾う。
}
issue_deps_raw() { # 自己依存も含めてそのまま返す (preflight が検出するため)
  deps_section_plain "$1" \
    | grep -oE '^[[:space:]]*[-*][[:space:]]*(#|issue[[:space:]]*)?[0-9]{3}\b' \
    | grep -oE '[0-9]{3}' \
    | sort -u
}
issue_deps() { # 実行時に使う版。自己依存は落としてデッドロックを避ける
  issue_deps_raw "$1" | grep -vx "$1" || true
}
# ⚠️★★★ P1-D（design.md 判断 7）: 散文中の言及 (「issue 004 の merge 後に…」) は正当にありうる。
#   die はせず WARN するための材料をここで作る —— Dependencies 節 (装飾を剥がした後) にある
#   単語境界の 3 桁数字のうち、箇条書き行の先頭として拾えなかったもの。
issue_deps_unparsed() { # issue_deps_unparsed <id> → 拾えなかった 3 桁数字 (1 行 1 件、無ければ空)
  local all_nums parsed n
  all_nums="$(deps_section_plain "$1" | grep -oE '\b[0-9]{3}\b' | sort -u)"
  parsed="$(issue_deps_raw "$1")"
  for n in $all_nums; do
    printf '%s\n' "$parsed" | grep -qx "$n" || printf '%s\n' "$n"
  done
}
issue_verify_level() { grep -m1 -E '^verify_level:' "$(issue_file "$1")" | awk '{print $2}'; }

# ⚠️★★★ `## Status` を読む (★ 判断 26 の申し送り・判断 4・2026-09-20)。
#   ★ これが無いと `--issues` なしの実行で **`blocked` の issue も走る**。
#     実績: issue 004 は blocked のまま回されて **attempt 1〜3 を失った**。
#   ★ 節の**最初の非空行**を見る。⚠️ 実際の値は
#     `blocked（★ 2026-09-19 更新・判断 26 —— …）` のように注釈が続くので、**前方一致**で判定する。
issue_status() { # issue_status <id> → ## Status 節の最初の非空行 (無ければ空文字)
  issue_field "$1" Status 2>/dev/null | grep -m1 -v '^[[:space:]]*$' || true
}
# ⚠️★★★ **装飾を剥がしてから判定する**（★ `code-reviewer` MEDIUM・2026-09-20）。
#   ⚠️ 素の前方一致は、実在する書式で **fail-open する**（★ 2026-09-20 に全 issue を走査して実測）:
#     `.steering/20260911-outcome-arbitration-and-o1-preflight/issues/008.md` → `✅ **done**（2026-09-12）`
#     同 `009.md` → `⚠️★★★ **不要（not needed）** ——`
#   → ★ 同じ書き手が `⚠️ **blocked**（…）` と書いた瞬間に **blocked の issue が既定実行に載る**
#     （＝ 起票の動機そのものが再発する）。
#   ★ 先頭の ASCII 英字までを捨ててから小文字化する（⚠️ `${v,,}` は bash 3.2 に無いので `tr`）。
issue_status_key() { # issue_status_key <id> → 判定用に正規化した文字列
  issue_status "$1" | sed -e 's/^[^A-Za-z]*//' | tr 'A-Z' 'a-z'
}

# ⚠️★★★ 上の issue_status* は $TASK_DIR (main checkout 側) を読む。既存の呼び出し元
#   (dry-run の実行計画 / ALL の決定) はそれで正しいので**変えない**。
#   ★ ここで足すのは **worktree 側のコピー**を読む版 (2026-09-25 実測の是正):
#     worker が Allowed Files 外の変更が必要と判断して `## Status` を blocked に書き換えるのは
#     worktree 側のファイルであり、main checkout 側は動かない。正規化は issue_status_key と揃える。
wt_issue_file() { printf '%s/%s/issues/%s.md' "$1" "$TASK_DIR_RELPATH" "$2"; } # wt_issue_file <wt> <id>
wt_issue_status() { # wt_issue_status <wt> <id> → worktree 側 ## Status 節の最初の非空行 (無ければ空文字)
  local f; f="$(wt_issue_file "$1" "$2")"
  [ -f "$f" ] || { printf ''; return; }
  awk '$0=="## Status"{f=1;next} /^## /{f=0} f' "$f" | grep -m1 -v '^[[:space:]]*$' || true
}
wt_issue_status_key() { # wt_issue_status_key <wt> <id> → 判定用に正規化した文字列
  wt_issue_status "$1" "$2" | sed -e 's/^[^A-Za-z]*//' | tr 'A-Z' 'a-z'
}

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
  ensure_deny "$id" verify "$attempt" "$wt" || return 1
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

# ---------- P1-I: 「未コミット／コミット 0 件」の attempt を verify すら回さず失敗にする ----------
# ⚠️★★★ 実例（005 / 008）: verify はworktree の**作業ツリー**を測るので、worker が
#   `max_turns` で切れて何もコミットしなくても緑になりうる (★ design.md P1-I・判断 5)。
#   → ★ 「ちゃんとコミットされているか」を別に見る。
# ⚠️★★★ **呼び出し順序はレビュー指摘 C-M3/C-M4（2026-09-26）で verify の前に是正した。**
#   ★ 呼び出し側 (run_issue の verify 直前) がこの順序を強制する。詳細はそちらのコメントを参照。
#
# ⚠️★★★ **2026-09-26 の 2 回目の是正 (/cross-review + security-checker・判断 10)**:
#   ★ 「check_committed を verify の前に置く」だけでは 3 つの穴が残っていた:
#     (a) code-reviewer MEDIUM: 赤の verify が gitignore 外の生成物を作業ツリーに残すと、
#         worker が正しくコミットしても porcelain には生成物が**未追跡のまま**残り続け、
#         次の attempt の check_committed が**恒久的に dirty**になる (worker は rm を持たない)。
#     (b) Codex P2-3: 逆に `status.showUntrackedFiles=no` の設定下では、生の `git status --porcelain`
#         は未追跡ファイルを一切表示しない。→ コミットしていない新規ファイルを使って
#         見かけ上クリーンになり、緑になりうる。
#     (c) Codex P2-2 / security LOW 1: check_committed が見ているのは「呼ばれた時点のスナップショット」
#         でしかない。verify が追跡ファイルを書き換えた場合や、skip-worktree / assume-unchanged の
#         印が付いたファイルがある場合、**コミットの内容そのものは検証されていない**。
#   ★ 是正: (a)(b) は check_committed 内で対処し、(c) は run_issue 側で verify 前後の不変性を見る。
#
# ⚠️★★★ **限界（境界ではなく明示する）**:
#   worker が verify の生成物と同じパスを後で意図的に編集しても、未追跡のままなら
#   引き続き除外される。gitignore 対象のパスは見ない (そもそも porcelain に出ない)。
#   これは検査の穴ではなく、**最終判定は merge 前にメインが clean な checkout で回す acceptance**
#   に委ねる設計 (前タスク判断 21 / 22 の運用・判断 8 と同じ型)。
untracked_paths() { # untracked_paths <worktree> → 未追跡パス一覧 (1 行 1 パス。"?? " 接頭辞は剥がす)
  #   ⚠️★★★ `--untracked-files=all` を明示する ((b) の対策そのもの)。指定しないと
  #     `status.showUntrackedFiles=no` の設定を継承してしまい、未追跡ファイルを一切拾えない。
  git -C "$1" status --porcelain --untracked-files=all 2>/dev/null | grep '^?? ' | sed 's/^?? //'
}

record_verify_generated() { # record_verify_generated <worktree> <u0-file> <gen-file>
  #   verify (run_verify / watchdog) が実行される**前後**の未追跡集合の差分 (U1 - U0) を
  #   <gen-file> に積む。次回以降の check_committed がこの集合に含まれる未追跡パスを
  #   dirty 判定から除外する ((a) の対策)。緑でも赤でも呼ぶこと (どちらも生成物を残しうる)。
  local wt="$1" u0="$2" gen="$3" u1
  u1="$(mktemp)" || return 0
  untracked_paths "$wt" > "$u1"
  if [ -s "$u0" ]; then
    grep -Fxvf "$u0" "$u1" 2>/dev/null >> "$gen" || true
  else
    cat "$u1" >> "$gen" 2>/dev/null || true
  fi
  rm -f "$u1"
}

# ⚠️★★★ 3 回目の是正 (/cross-review 2 巡目・2026-09-26): skip-worktree / assume-unchanged の印は
#   `check_committed` だけでなく、verify・watchdog **後**の不変確認 (run_issue) からも見る必要がある。
#   ★ `git diff --quiet HEAD --` は印が付いたパスの変更を見ないため、verify.test 自身が
#     追跡ファイルを書き換えたうえで印を付けると、不変確認は「クリーン」と誤診して素通りしてしまう。
#   → ★ 判定を関数に括り出し、check_committed と run_issue の不変確認の両方から呼ぶ。
flagged_tracked_files() { # flagged_tracked_files <worktree> → skip-worktree(S)/assume-unchanged(小文字) の印が付いた行 (空なら印なし)
  git -C "$1" ls-files -v 2>/dev/null | grep -E '^(S |[a-z] )' || true
}

check_committed() { # check_committed <worktree> <anchor> <out-file> <gen-file>; 0 = コミット済み
  local wt="$1" anchor="$2" out_file="$3" gen_file="$4"
  local n_commits rc
  : > "$out_file"
  [ -f "$gen_file" ] || : > "$gen_file"

  # --- (1) 未追跡ファイルは設定非依存で全件見る。verify が作った生成物だけを除外する ---
  local porcelain line path dirty_lines="" excluded_lines=""
  porcelain="$(git -C "$wt" status --porcelain --untracked-files=all 2>&1)"
  if [ -n "$porcelain" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      case "$line" in
        "?? "*)
          path="${line#"?? "}"
          # ⚠️★★★ 3 回目の是正 (/cross-review 2 巡目): `$path` が `-` で始まると
          #   (例: `-report.txt`) grep がオプションと誤解釈し、毎回 dirty 扱いになっていた。
          #   → `-e` でパターンだと明示し、`--` で以降を非オプション引数に固定する。
          if grep -Fxq -e "$path" -- "$gen_file" 2>/dev/null; then
            excluded_lines="${excluded_lines}${line}"$'\n'
          else
            dirty_lines="${dirty_lines}${line}"$'\n'
          fi ;;
        *) dirty_lines="${dirty_lines}${line}"$'\n' ;;
      esac
    done <<< "$porcelain"
  fi
  {
    echo "# check_committed: git status --porcelain --untracked-files=all"
    if [ -n "$porcelain" ]; then printf '%s\n' "$porcelain"; else echo "(クリーン)"; fi
    if [ -n "$excluded_lines" ]; then
      echo "# → 除外した生成物 (verify が作った未追跡パスなので dirty 判定から外した):"
      printf '%s' "$excluded_lines"
    fi
  } >> "$out_file"
  if [ -n "$dirty_lines" ]; then
    echo "# → 未コミットの変更がある (dirty)" >> "$out_file"
    return 1
  fi

  # --- (2) skip-worktree / assume-unchanged の印はコミットの内容を保証しない ---
  local flagged
  flagged="$(flagged_tracked_files "$wt")"
  if [ -n "$flagged" ]; then
    {
      echo "# check_committed: git ls-files -v に skip-worktree(S) / assume-unchanged(小文字) の印がある"
      printf '%s\n' "$flagged"
      echo "# → コミット済みの内容が保証できないため fail-closed"
    } >> "$out_file"
    return 1
  fi

  # ⚠️ anchor が空・rev-list が失敗 → 数えられない ＝ fail-closed (done にしない側)。
  if [ -z "$anchor" ]; then
    echo "# → anchor (worktree 生成時の HEAD) を取得できていない。コミット数を数えられないため fail-closed" >> "$out_file"
    return 1
  fi
  n_commits="$(git -C "$wt" rev-list --count "$anchor..HEAD" 2>&1)"; rc=$?
  echo "# check_committed: git rev-list --count $anchor..HEAD = $n_commits (rc=$rc)" >> "$out_file"
  if [ $rc -ne 0 ]; then
    echo "# → rev-list に失敗した。数えられないため fail-closed" >> "$out_file"
    return 1
  fi
  case "$n_commits" in
    ''|*[!0-9]*)
      echo "# → rev-list の出力が数値でない。fail-closed" >> "$out_file"
      return 1 ;;
  esac
  if [ "$n_commits" -eq 0 ]; then
    echo "# → anchor からコミットが 0 件" >> "$out_file"
    return 1
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

# ⚠️★★★ **run をまたいで残す**置き場 (★ 起票 3・判断 3)。
#   ★ `WORK_TMP` は上の `cleanup_tmp` で run 終了時に消えるので、**後から読みたいものは置けない**。
#   ⚠️ `.gitignore` に `.steering/**/_loop-artifacts/` を入れてある
#     （★ 無いと `loop-spawn.sh` の dirty-tree 判定に当たって次の issue が死ぬ）。
ARTIFACTS_DIR="$TASK_DIR/_loop-artifacts"

# ⚠️★★★ 保存する前に資格情報を伏せる jq の前置き（★ `security-checker` HIGH・2026-09-20）。
#   ★ 3 段: (a) 秘密らしいキーの直後の値 (b) `KEY=VALUE` の値 (c) 200 文字で切る。
#   ⚠️ **完全ではない**（★ 明示する）—— 任意の位置に置かれた裸のトークン
#     （例: `gh api -f body=<token>` 以外の形、base64 の断片）は伏せられない。
#     ★ ここは「よくある形を減らす」多層防御であって、**秘密を入れてよい置き場ではない**。
DENY_REDACT='
def redact:
  gsub("(?<a>authorization|token|secret|password|passwd|api[-_]?key|access[-_]?token|bearer)(?<b>[^[:alnum:]]{1,3})(?<c>[^[:space:]]+)"; .a + .b + "***"; "i")
  | gsub("(?<p>^|[[:space:]])(?<n>[A-Za-z_][A-Za-z0-9_]*)=(?<v>[^[:space:]]+)"; .p + .n + "=***")
  | if (length > 200) then .[0:200] + "…(切り詰め)" else . end;
'

# ⚠️ 古い artifacts を掃除する（★ `security-checker` HIGH の「保持期間が無い」）。
#   ★ `.gitignore` 済みなので `git status` に出ず、**増え続けても誰も気づかない**。
#   ⚠️ 失敗しても run は止めない（★ 掃除は本務ではない）。
if [ -d "$ARTIFACTS_DIR" ]; then
  pruned="$(find "$ARTIFACTS_DIR" -type f -name '*-denials.json*' -mtime +14 -print 2>/dev/null | wc -l | tr -d ' ')"
  if [ "${pruned:-0}" -gt 0 ]; then
    find "$ARTIFACTS_DIR" -type f -name '*-denials.json*' -mtime +14 -delete 2>/dev/null || true
    log "14 日より古い denials 成果物を $pruned 件削除した → $ARTIFACTS_DIR"
  fi
fi

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

# ---------- worker が worktree 側で Status を blocked にしたか (2026-09-25 追加) ----------
# ⚠️★★★ 実測 (issue 001・2026-09-25): worker が「Allowed Files の外の変更が必要」と判断し、
#   worktree 側の issue ファイルの `## Status` を `blocked（…）` に書き換えて attempt を止めたのに、
#   loop-run.sh は気づかず acceptance_fail として **同じ worker を max_attempts まで再起動**した
#   (issue 001 で 5 attempt の空回り)。
#   ★ 検知するのは「開始時は blocked でなかったのに今 blocked」という*遷移*だけにする ——
#     `--issues` で最初から blocked な issue を明示実行する既存経路 (BYPASSED_BLOCKED) は
#     遷移が起きないのでこの関数を素通りする (壊さない)。
check_wt_became_blocked() { # check_wt_became_blocked <id> <wt> <attempt> <was-blocked-at-start:0|1>; 0=遷移を検知 1=検知せず
  local id="$1" wt="$2" attempt="$3" was_blocked="$4"
  [ "$was_blocked" = "0" ] || return 1
  case "$(wt_issue_status_key "$wt" "$id")" in
    blocked*)
      emit "$id" verify blocked attempt="$attempt" \
           detail="worker が Status を blocked にした ($(wt_issue_status "$wt" "$id" | head -c 120))。★ worktree は残す: $wt"
      return 0 ;;
  esac
  return 1
}

# ---------- 1 issue の attempt ループ ----------
# ⚠️★★★ **失敗で抜けたら、最後にもう一度ブランチを見る**（★ 2026-09-27・`code-reviewer` MEDIUM）。
#   ★ `ensure_branch` は attempt 冒頭・verify 直前・issue_done 直前でしか呼ばれない。
#     ⚠️ **最終 attempt の verify / watchdog の最中**に HEAD が動くと（verify.test は worker が書いたテストを走らせる）、
#     abandoned / no_progress_stop / watchdog NG / verify 赤のどの出口でも `ensure_branch` を通らずに抜け、
#     境界侵害の印が付かず、同じ run の次のバッチが spawn されていた。
#   → ★ 本体 (`run_issue_body`) の出口を 1 つずつ塞がず、**出口の外側で 1 回だけ**見る。
#     ★ 本体は worktree とアンカーを `$WORK_TMP/wt-<id>` に残す（★ サブシェルなので変数では渡らない）。
#     ⚠️ すでに印が付いた issue は見直さない（★ 同じ blocked を 2 回 emit しない）。
run_issue() {
  local id="$1" rc=0 wt anchor last
  run_issue_body "$id" || rc=$?
  [ "$rc" -ne 0 ] || return 0
  [ -f "$WORK_TMP/wt-$id" ] || return "$rc"
  grep -qxF -e "$id" "$WORK_TMP/boundary-breach" 2>/dev/null && return "$rc"
  wt="$(sed -n 1p "$WORK_TMP/wt-$id")"; anchor="$(sed -n 2p "$WORK_TMP/wt-$id")"
  [ -d "$wt" ] || return "$rc"
  last="$(jq -s --arg i "$id" '[.[] | select(.issue==$i and (.attempt|type)=="number") | .attempt] | max // 0' "$EVENTS" 2>/dev/null || echo 0)"
  ensure_branch "$id" verify "${last:-0}" "$wt" "$anchor" || true
  return "$rc"
}

run_issue_body() {
  local id="$1" wt attempt=1 same=0 last_fp="" fp wt_anchor wt_blocked_at_start=0
  # ⚠️★★★ verify が生成した未追跡パスの集合 (判断 10)。attempt をまたいで蓄積する
  #   (前 attempt が残した生成物は次の attempt でも未追跡のまま残るため)。issue ごとに 1 本、
  #   run_issue の開始で空にする (WORK_TMP は run 全体で 1 つなので id 違いと混線しない)。
  local gen_file="$WORK_TMP/verify-generated-$id.txt"
  : > "$gen_file"
  # ⚠️★★★ **`--task` を渡す** (★ 起票 23)。
  #   ★ 旧実装は `--no-exec "$id"` だけを渡しており、⚠️ **loop-run.sh は `$TASK_DIR` を
  #     持っているのに伝えていなかった**ので、`loop-spawn.sh` が `.steering/*/_loop-config.json` を
  #     `tail -1` で**再導出**していた。→ ★ 2026-09-21 に **38 コミット前の枝**から worktree が
  #     切られる事故が実測された。
  # ⚠️★★★ **stderr を捨てない。**
  #   ★ 旧実装の `2>/dev/null` は、`loop-spawn.sh` が出す
  #     「解決した base は何で、既定からどれだけ離れているか」を**丸ごと消していた**
  #     (＝ **無人モードC では誰も読まない** ＝ 起票 23 の 2 つ目の論点)。
  #   → ★ run ログへ流す。⚠️ stdout 側の契約 (最終行 = worktree の絶対パス) は変えない。
  local spawn_err _l spawn_local_ahead=0
  spawn_err="$(mktemp)" || { emit "$id" execute blocked detail="mktemp に失敗 (worktree 生成前)"; return 1; }
  # ⚠️ 早期 return でも必ず掃除する (★ Codex `/cross-review` 1 巡目・2026-09-21)。
  #   ★ 現在は下の `rm -f` に到達するので leak は無いが、
  #   ⚠️ 将来 `set -e` を足すか途中で return を増やすと残る。
  #   ★ bash では関数内の RETURN trap がその関数の戻りで発火する (2026-09-21 に実測)。
  trap 'rm -f "$spawn_err"' RETURN
  wt="$(LOOP_NO_EXEC=1 bash "$MAIN_ROOT/scripts/loop-spawn.sh" --no-exec --task "$TASK_DIR" "$id" 2>"$spawn_err" | tail -1)"
  # ⚠️ `[ -n "$_l" ] && log "$_l"` と書かない —— ★ 最終行が空なら
  #   ループ本体の戻り値が非 0 になる。⚠️ 今は `set -e` を使っていないので無害だが、
  #   ★ 将来 `set -e` を足すと **空行 1 本で run_issue が落ちる** (`code-reviewer` LOW・2026-09-21)。
  while IFS= read -r _l; do
    [ -n "$_l" ] || continue
    log "$_l"
    # ⚠️★★★ P1-J（design.md 判断 3）: spawn が「ローカルが origin/<base> より先行している」と
    #   判定して**ローカル base**から切ったこと (未 push のコミットを含みうる) を検出する。
    #   ★ ここでは検出だけし、emit は下の attempt=1 の attempt_start に合流させる
    #   (★ events 語彙は増やさない。ensure_deny / BYPASSED_BLOCKED と同じ「attempt_start + detail」の作法)。
    # ⚠️★★★ レビュー指摘 (2026-09-26): 緩い部分一致 `*start-choice*local-ahead*` は、
    #   config 由来の base 名が偶然 "start-choice-local-ahead" になった場合の
    #   `loop-spawn:   start      = start-choice-local-ahead` という無関係な行にも一致してしまう
    #   (★ その行は「解決した base 名」であって「ローカル先行の判定」ではない)。
    #   → ★ loop-spawn.sh が出す契約の行 (loop-spawn.sh 側の該当コメントで綴りを固定) である
    #     `loop-spawn:   start-choice = local-ahead` の**完全一致**にする
    #     (行頭から行末まで。末尾の空白だけは許す)。
    local _l_trimmed; _l_trimmed="$(printf '%s' "$_l" | sed -e 's/[[:space:]]*$//')"
    case "$_l_trimmed" in
      "loop-spawn:   start-choice = local-ahead") spawn_local_ahead=1 ;;
    esac
  done < "$spawn_err"
  rm -f "$spawn_err"
  [ -d "${wt:-}" ] || { emit "$id" execute blocked detail="worktree 生成に失敗"; return 1; }

  # ⚠️★★★ **履歴検査のアンカーは「worktree を作った時点」に固定する**
  #   （★ Codex `/cross-review` HIGH・2026-09-20）。
  #   ⚠️ attempt ごとの「直前の HEAD」を使うと、attempt 2 の worker が
  #     **attempt 1 のコミットを `git commit --amend`** した瞬間に祖先関係が切れ、
  #     ★ 正当な作業が blocked になる（`git commit --amend` は deny に無い）。
  #   ★ 生成時点なら、worker が自分のコミットをどう作り直してもアンカーは祖先のままで、
  #     ⚠️ **他ブランチへの差し替えだけが不一致になる**。
  #   ⚠️ 取れなければ空のまま進む（★ 名前の検査は base 無しでも効く。fail-open にはしない）。
  wt_anchor="$(git -C "$wt" rev-parse HEAD 2>/dev/null || true)"
  printf '%s\n%s\n' "$wt" "$wt_anchor" > "$WORK_TMP/wt-$id" 2>/dev/null || true

  # ⚠️★★★ worktree 生成直後の Status を記録する (2026-09-25 追加)。
  #   ★ `--issues` で最初から blocked な issue を明示実行する経路 (BYPASSED_BLOCKED) では
  #     ここが 1 になり、`check_wt_became_blocked` は「遷移していない」として素通りする。
  case "$(wt_issue_status_key "$wt" "$id")" in
    blocked*) wt_blocked_at_start=1 ;;
    *)        wt_blocked_at_start=0 ;;
  esac

  while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
    if [ "$(tokens_used)" -ge "$TOKEN_CEIL" ]; then
      emit "$id" execute abandoned attempt="$attempt" detail="token_ceiling 超過"; return 1
    fi
    emit "$id" execute attempt_start attempt="$attempt"

    # ⚠️★★★ **blocked を承知で回したことを events に残す**（★ `security-checker` MEDIUM・2026-09-20）。
    #   ★ 除外も迂回も従来は `log`（stdout）と `_loop-run-report.md`（**gitignore 済み**）にしか出ず、
    #     ⚠️ **後から監査できるのが端末のスクロールバックだけ**になっていた。
    #   ★ events 語彙は増やさない —— `ensure_deny` と同じ「`attempt_start` ＋ `detail`」の作法。
    if [ "$attempt" = "1" ]; then
      case " $BYPASSED_BLOCKED " in
        *" $id "*) emit "$id" execute attempt_start attempt="$attempt" \
                        detail="WARN: Status=blocked の issue を --issues で明示指定して実行している ($(issue_status "$id" | head -c 120))" ;;
      esac
      # ⚠️★★★ P1-J（design.md 判断 3）: 両方該当したら 2 行 emit でよい (既存 WARN と同じ作法)。
      if [ "$spawn_local_ahead" = "1" ]; then
        emit "$id" execute attempt_start attempt="$attempt" \
             detail="WARN: base をローカル先行（未 push を含む）から切った: loop-spawn の provenance (start-choice) を確認してください"
      fi
    fi

    # ⚠️★★★ **毎 attempt** 必須 deny を保証する (★ 詳細は ensure_deny の冒頭)。
    ensure_deny "$id" execute "$attempt" "$wt" || return 1
    # ★ 前の attempt が残した逸脱を次の attempt に持ち越さない (★ 詳細は ensure_branch の冒頭)。
    #
    # ⚠️★★★ **この 1 行は、現在のモードC では到達しない**（★ `code-reviewer` HIGH・2026-09-20）。
    #   ★ 逸脱はセッション中に起きるので、必ず先に verify 側 (下記) が拾って `return 1` する。
    #     → attempt 2 が始まらないので、ここに逸脱した状態で来ることがない。
    #   ★ 逸脱後の再実行も `loop-spawn.sh` の「同名 worktree が既に存在」で先に死ぬ。
    #   → ⚠️ **検出力を持つのは verify 直前と issue_done 直前の 2 つ**であり、ここは
    #     「将来 worktree を再利用する経路が生えたとき」のための保険である。
    #   ⚠️ **「3 か所で検査している」と数えないこと**（★ 検査があるつもりで検査していない型）。
    ensure_branch "$id" execute "$attempt" "$wt" "$wt_anchor" || return 1

    # --- 完全なセッションを 1 回。hook / スラッシュコマンド / settings が効く ---
    local res subtype denials
    local -a cargs=( -p "/loop-issue $id"
                     --max-turns "$MAX_TURNS"
                     --permission-mode "$PERM_MODE"
                     --model "$WORK_MODEL"
                     --output-format json )
    [ -n "${MAX_USD:-}" ]     && cargs+=( --max-budget-usd "$MAX_USD" )
    [ -n "${ALLOW_TOOLS:-}" ] && cargs+=( --allowedTools "$ALLOW_TOOLS" )
    # ⚠️★★★ `MSYS2_ARG_CONV_EXCL` を外さないこと（2026-09-18 に実測で発見）。
    #   ★ Windows の git-bash (MSYS) は、ネイティブ実行ファイルへ渡す `/` 始まりの引数を
    #     Windows パスへ書き換える。→ `-p "/loop-issue 008"` は worker に
    #     **`C:/Program Files/Git/loop-issue 008`** として届き、スラッシュコマンドが展開されない。
    #   ⚠️ worker の transcript で確認したところ、003 / 004 / 005 / 008 の**全 attempt**がこの形で届いており、
    #     worker は `/loop-issue` の契約を読まずに worktree 名やコミット履歴から推測して動いていた
    #     （★ 「具体的な指示がまだありません」と返して何もせず終わる attempt が実在した）。
    #   ★ 除外するのはこの接頭辞だけ（他の引数のパス変換は従来どおり効かせる）。macOS / Linux では無害。
    res="$( (cd "$wt" && MSYS2_ARG_CONV_EXCL="/loop-issue" claude "${cargs[@]}") 2>&1 )"

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
    #
    # ⚠️★★★ **件数だけでは「非致命」と言い切れない**（★ 起票 3・判断 3・2026-09-20）。
    #   ★ issue 002 の 6 attempt で 1 / 2 / 5 / 10 件が記録されたが、**内訳が分からなかった**。
    #   → ★ (a) events に **何が拒否されたか**の集計を書き、(b) 生配列をファイルに残す。
    #   ⚠️ **`WORK_TMP` には置かない** —— `trap cleanup_tmp EXIT` が run 終了時に `rm -rf` する
    #     （★ 起票 3 が書いていた「`WORK_TMP` に保存」は後から読めない）。
    #   ★ 集計キーは **`.tool_input.command` の先頭 2 語**にする（★ 2026-09-20 の実測 M1b）:
    #     拒否はすべて `tool_name == "Bash"` になるので、**`.tool_name` だけ数えても何も分からない**。
    #
    # ⚠️★★★ **保存する前に必ず伏せる**（★ `security-checker` HIGH・2026-09-20）:
    #   ★ `.tool_input.command` は worker が組み立てた**自由文字列**であり、
    #     `CI_TOKEN=<値> gh api …` / `curl -H "Authorization: Bearer …"` の形で
    #     ⚠️ **資格情報がそのまま入りうる**。★ 保存先は 2 か所（events の detail ＋ 生配列）で、
    #     どちらも**恒久**に残る（`cleanup_tmp` の対象外）。
    #   → ★ `DENY_REDACT` で (a) `KEY=VALUE` の値 (b) 秘密らしいキーの直後の値 を伏せ、
    #     (c) 1 件 200 文字で切る。⚠️ **伏せてから集計キーを作る**
    #     （★ そうしないと「先頭 2 語」が `CI_TOKEN=<値>` を狙い撃ちで拾う）。
    denials="$(printf '%s' "$res" | jq -r '(.permission_denials // []) | length' 2>/dev/null || echo 0)"
    if [ "${denials:-0}" -gt 0 ]; then
      local by_tool art tmp_art
      by_tool="$(printf '%s' "$res" | jq -r "$DENY_REDACT"'
          [ (.permission_denials // [])[]
            | if (.tool_name // "") == "Bash"
              then "Bash(" + ((.tool_input.command // "?") | redact
                              | [splits("[[:space:]]+")] | map(select(. != "")) | .[0:2] | join(" ")) + ")"
              else (.tool_name // "?") end ]
          | group_by(.) | map("\(.[0])x\(length)") | join(" ")
        ' 2>/dev/null | tr -d '\r' | tr '\n' ' ' | head -c 300)"
      art="$ARTIFACTS_DIR/$id-attempt$attempt-denials.json"
      # ⚠️ 直接リダイレクトすると **jq が失敗しても 0 バイトのファイルが残る**
      #   （★ 「空 ＝ 拒否内訳が空」と読み違える。`code-reviewer` MEDIUM）。→ 一時ファイル ＋ mv。
      tmp_art="$art.tmp$$"
      if mkdir -p "$ARTIFACTS_DIR" 2>/dev/null \
         && printf '%s' "$res" | jq "$DENY_REDACT"'
              [ (.permission_denials // [])[]
                | if (.tool_input.command // null) != null
                  then .tool_input.command |= redact else . end ]
            ' > "$tmp_art" 2>/dev/null \
         && [ -s "$tmp_art" ] && mv "$tmp_art" "$art" 2>/dev/null; then
        : # ★ 保存できた
      else
        # ⚠️ 保存に失敗しても attempt は落とさない (★ 記録の補助であって判定ではない)。
        rm -f "$tmp_art" 2>/dev/null || true
        art="(保存できず)"
      fi
      emit "$id" execute attempt_start attempt="$attempt" \
           detail="permission_denials=$denials [${by_tool:-内訳不明}] (非致命・verify の exit code で判定する) → $art"
    fi

    # --- ⚠️★★★ verify の直前にブランチを確かめる ---
    #   ★ **起票 10 の実測はこの形だった**: worker が session の最後に `git checkout main` を打ち、
    #     ⚠️ `run_verify` が **別ブランチの内容**を検査するところだった。
    #   ★ ここを通さずに verify すると、緑も赤も**何を測ったのか分からない数字**になる。
    ensure_branch "$id" verify "$attempt" "$wt" "$wt_anchor" || return 1

    # --- 客観検証: exit code がすべて。LLM の申告は読まない ---
    # ⚠ `$(run_verify ...)` の形で呼ばないこと (サブシェルで VERIFY_* が失われる)。
    local vout="$WORK_TMP/verify-$id.out"
    # ⚠️★★★ P1-I（design.md 判断 5・レビュー指摘 C-M3/C-M4 で 2026-09-26 是正）:
    #   `check_committed` は **`run_verify` より前**に見る。
    #   ⚠️★★★ **さらに 2026-09-26 の 2 回目の是正 (/cross-review + security-checker・判断 10)**:
    #   ★ 分岐を明示にする —— `if ! check_committed …; then VERIFY_KIND=uncommitted;
    #     elif run_verify …; then …（緑の経路）…; fi` の形にし、`[ -n "$VERIFY_KIND" ] ||
    #     VERIFY_KIND=uncommitted` という**暗黙の推論**はやめる。
    #   ★ check_committed 自身の生成物除外・未追跡設定非依存・skip-worktree 検査は
    #     check_committed のコメントを参照。★ ここで足すのは verify 前後の不変性検査:
    #     run_verify (と recheck の watchdog) の**前後**で「未追跡集合 U0/U1」を取り、
    #     U1 − U0 を生成集合に足す (次回以降の check_committed が除外できるようにする)。
    #     さらに issue_done の直前で「HEAD が動いていない」かつ「追跡ファイルに差分がない」
    #     ことを確かめ、崩れていれば uncommitted 扱いにして done にしない
    #     (Codex P2-2 / security LOW 1 —— verify が追跡ファイルを書き換えても
    #     check_committed 単体では気づけない)。
    VERIFY_KIND=""
    local uncommitted_detail=""
    if ! check_committed "$wt" "$wt_anchor" "$vout" "$gen_file"; then
      VERIFY_KIND=uncommitted
    else
      local u0_file head_before head_after flagged_after
      u0_file="$WORK_TMP/verify-u0-$id.txt"
      untracked_paths "$wt" > "$u0_file"
      head_before="$(git -C "$wt" rev-parse HEAD 2>/dev/null || true)"
      if run_verify "$wt" "$id" "$vout"; then
        # ★ 緑になった直後にも U1 を取って生成集合を更新する (verify 自体が生成物を作りうる)。
        record_verify_generated "$wt" "$u0_file" "$gen_file"
        local lvl; lvl="$(issue_verify_level "$id")"
        if [ "$lvl" = "recheck" ]; then
          if ! run_watchdog "$id" "$wt" "$attempt"; then
            return 1
          fi
          # ⚠️★★★ 3 回目の是正 (/cross-review 2 巡目): `run_watchdog` もフルセッション 1 回分であり
          #   gitignore 外の生成物を残しうる。上の記録は verify 直後の 1 回だけだったので、
          #   watchdog が作った未追跡ファイルは次の attempt の check_committed でも dirty のままに
          #   固定されていた。★ 冒頭コメント (P1-I) の「run_verify (と recheck の watchdog) の
          #   前後で…」という記述はこれで実装と一致する。
          #   ★ U0 は run_verify の前に取った `$u0_file` を再利用する
          #     (watchdog 用に取り直す必要はない。gen_file は行の集合として追記するだけなので
          #     verify 分と watchdog 分が重複して積まれても害はない)。
          record_verify_generated "$wt" "$u0_file" "$gen_file" # WATCHDOG-POST-RECORD (3 回目の是正)
        fi
        # ⚠️★★★ **`issue_done` を出す直前に「HEAD 不変」かつ「追跡ファイルに差分なし」かつ
        #   「skip-worktree/assume-unchanged の印が付いていない」ことを確かめる**
        #   （★ Codex P2-2 / security LOW 1・2026-09-26。★ `code-reviewer` / `security-checker` の
        #     旧 HIGH 指摘・2026-09-20 の「HEAD だけ見る」検査をさらに強める）。
        #   ★ `run_watchdog` は worktree 内で **もう 1 回フルセッション**を起動する
        #     (`verify_level: recheck` の issue)。そこや `run_verify` の最中に
        #     追跡ファイルが書き換えられていても、check_committed 通過時点のスナップショットだけでは
        #     見えない。→ ★ ここで H0 との一致と `git diff --quiet HEAD --` を見る。
        #   ⚠️★★★ 3 回目の是正 (/cross-review 2 巡目): `git diff --quiet HEAD --` は
        #     skip-worktree/assume-unchanged の印が付いたパスの変更を**見ない**。
        #     verify.test 自身が追跡ファイルを書き換えたうえで印を付けると、上の 2 条件だけでは
        #     「クリーン」に見えてしまう (check_committed 通過時点では印は無かったはずなので、
        #     ここで見つかる印は verify/watchdog の最中に付いたものである)。
        #     → `flagged_tracked_files` (check_committed と共通の判定) をここでも通す。
        #   ⚠️ `head_before` / `head_after` が両方とも rev-parse 失敗で空文字列だと
        #     `"" = ""` が成立して fail-open するため、`head_before` が空でないことも確かめる。
        head_after="$(git -C "$wt" rev-parse HEAD 2>/dev/null || true)"
        flagged_after="$(flagged_tracked_files "$wt")"
        if [ -n "$head_before" ] && [ "$head_after" = "$head_before" ] && git -C "$wt" diff --quiet HEAD -- 2>/dev/null && [ -z "$flagged_after" ]; then
          # ⚠️ ブランチ名 / 履歴入れ替えの検査は従来どおり残す (HEAD 不変チェックとは別の観点:
          #   `ensure_branch` はブランチ名と anchor からの祖先関係を見る)。
          ensure_branch "$id" verify "$attempt" "$wt" "$wt_anchor" || return 1
          emit "$id" done issue_done attempt="$attempt"
          log "issue $id: done (attempt $attempt)"
          return 0
        fi
        {
          echo "# → verify（または watchdog）が追跡ファイル / HEAD を変更したか、skip-worktree/assume-unchanged の印を残した"
          echo "#   HEAD: 前=$head_before 後=$head_after"
          if [ -n "$flagged_after" ]; then
            echo "#   flagged (skip-worktree/assume-unchanged):"; printf '%s\n' "$flagged_after"
          fi
        } >> "$vout"
        VERIFY_KIND=uncommitted
        uncommitted_detail="verify/watchdog の前後で追跡ファイル差分・HEAD 移動・flagged ファイルのいずれかを検出した (HEAD 前=$head_before 後=$head_after)"
      else
        # run_verify が失敗した場合も生成物を残しうる (test_fail 等)。
        # VERIFY_KIND は run_verify 自身が設定済みなので、ここでは上書きしない。
        record_verify_generated "$wt" "$u0_file" "$gen_file"
      fi
    fi

    # 一時ファイルから fingerprint を作る (サブシェル経由だと必ず sha1("") になる)
    fp="$(fingerprint < "$vout")"
    # 保険: 空出力なら fingerprint は無意味なので no-progress 判定に使わない
    if [ ! -s "$vout" ]; then
      emit "$id" verify "$VERIFY_KIND" attempt="$attempt" exit=1 fingerprint="$fp" \
           detail="WARN: verify 出力が空。fingerprint は無効として no-progress 判定に使わない"
      # ★ no_progress 判定より前に見る (2026-09-25 追加。詳細は check_wt_became_blocked の冒頭)。
      check_wt_became_blocked "$id" "$wt" "$attempt" "$wt_blocked_at_start" && return 1
      last_fp=""; same=0
      attempt=$((attempt+1)); continue
    fi
    if [ -n "$uncommitted_detail" ]; then
      emit "$id" verify "$VERIFY_KIND" attempt="$attempt" exit=1 fingerprint="$fp" detail="$uncommitted_detail"
    else
      emit "$id" verify "$VERIFY_KIND" attempt="$attempt" exit=1 fingerprint="$fp"
    fi
    # ★ no_progress 判定より前に見る (2026-09-25 追加。詳細は check_wt_became_blocked の冒頭)。
    check_wt_became_blocked "$id" "$wt" "$attempt" "$wt_blocked_at_start" && return 1
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
# ⚠️★★★ `ALL_FILES` は **フィルタ前の全 id**。★ 下の `preflight_dag` の「依存が存在するか」は
#   必ずこちらに対して行う (★ フィルタ後の `$ALL` で引くと、`blocked` な issue に依存している
#   issue が「issues/ に存在しません」で **die する** —— 実際には存在するのに)。
ALL_FILES="$(issue_ids)"
# ⚠️★★★ **ファイル名由来の id も検証する**（★ Codex `/cross-review` 2 巡目 MEDIUM・2026-09-20）。
#   ★ 1 巡目の是正で `--issues` 側だけ検証していたが、⚠️ `issue_ids()` 由来は素通りだった。
#   ★ 以降のすべてが **`for id in $ALL_FILES` の単語分割**に依存しているので、
#     空白や glob メタ文字を含む issue ファイルがあると
#     ⚠️ **id が黙って分割され / パターンとして解釈される**（★ `case " $BYPASSED_BLOCKED "` も同じ）。
#   → ★ 早い段階で **die** する（⚠️ 黙って壊れた id で走らせない）。
#   ⚠️★★★ **`for id in $ALL_FILES` で検査してはならない** —— ★ その時点で**既に分割済み**であり、
#     `0 06.md` は `0` と `06` という**見かけ上は正当な 2 つの id** になってしまう
#     （★ 2026-09-20 に検査 S9 が実測で捕まえた）。→ ★ **行単位**で、分割される前に見る。
bad_ids="$(issue_ids | grep -vE '^[A-Za-z0-9._-]+$' || true)"
bad_ids="$bad_ids$(issue_ids | grep -xE '\.|\.\.' || true)"
[ -z "$bad_ids" ] || die "issue ファイル名が不正です (英数字 . _ - のみ):
$(printf '%s\n' "$bad_ids" | sed 's/^/  - /')
  ⚠️ 空白や glob メタ文字を含む名前は、id の単語分割・パターン解釈を壊します。"
ALL="$ALL_FILES"
SKIPPED_BLOCKED=""
BYPASSED_BLOCKED=""
if [ -n "$ONLY_ISSUES" ]; then
  # ★ 明示指定はフィルタしない (⚠️ blocked を承知で回せる余地を残す・判断 4)。
  ALL="$(printf '%s' "$ONLY_ISSUES" | tr ',' '\n')"
  # ⚠️★★★ **id を検証する**（★ `security-checker` LOW・2026-09-20）。
  #   ★ `$id` は下で `_loop-artifacts/$id-attempt…` のパス組み立てに使う。
  #     `--issues ../../x` を通すと **`.gitignore` の外**へ書けてしまう
  #     (⚠️ `issue_ids()` 由来の id は `basename f .md` なのでスラッシュを含まず、この経路は運用者入力だけ)。
  for id in $ALL; do
    case "$id" in
      *[!A-Za-z0-9._-]*|""|.|..) die "--issues の id が不正です: '$id' (英数字 . _ - のみ)" ;;
    esac
  done
  for id in $ALL; do
    case "$(issue_status_key "$id")" in
      blocked*)
        BYPASSED_BLOCKED="$BYPASSED_BLOCKED $id"
        log "⚠️ issue $id は Status=blocked ですが --issues で明示指定されたので実行します" ;;
    esac
  done
else
  # ⚠️★★★ `blocked` を**既定の選択から外す**（★ 判断 4）。
  #   ★ `done` は外さない —— 外すと `deps_met()` が永久に false になり、
  #     ⚠️ その issue に依存する後続が「依存 issue が未完のため未実行」で落ちる。
  #     ★ 完了の復元は下の「events から seed」が担っている。
  #   ★ `## Status` が無い issue は**回す**（⚠️ テンプレの Status 節は見出しだけで値が空。
  #     外すと新規に切った issue が黙って走らなくなる）。
  kept=""
  for id in $ALL_FILES; do
    case "$(issue_status_key "$id")" in
      blocked*) SKIPPED_BLOCKED="$SKIPPED_BLOCKED $id" ;;
      *)        kept="$kept $id" ;;
    esac
  done
  ALL="$(printf '%s\n' $kept)"
  if [ -n "$SKIPPED_BLOCKED" ]; then
    # ⚠️ events には出さない —— ★ events 語彙は 10 種で固定であり、
    #   「**実行しなかった**」は状態遷移ではない。★ ログとレポートで人に見せる。
    log "⚠️ Status=blocked のため既定の選択から外した:$SKIPPED_BLOCKED"
    log "   ★ 承知で回すなら --issues$(printf '%s' "$SKIPPED_BLOCKED" | tr ' ' ',') を付ける"
  fi
fi
[ -n "$ALL" ] || die "実行対象の issue がありません (⚠️ Status=blocked で全件外れた可能性:${SKIPPED_BLOCKED:- なし})"

# ⚠ DONE_IDS を空で始めてはならない。
#    ウェーブを分けて**別プロセスで**起動する運用では、`## Dependencies` に issue 番号を書くと
#    2 波目で deps_met() が永久に false になり、対象 issue が**一度も実行されないまま終わる**。
#    → 起動時に events から既完了を seed する。
# ⚠️★★★ `${#DONE_IDS[@]:-0}` は **bash の構文として不正**で `bad substitution` になる
#   (★ 2026-09-14 に stub 実行で実測。`${#arr[@]}` に `:-` は付けられない)。
#   ⚠️ `set -e` を付けていないので**エラーを出したまま続行**し、復元ログだけが黙って消えていた。
#   → ★ カウンタで数える (★ `check-shell-portability.sh` が言うとおり、空配列の参照自体を避ける)。
DONE_COUNT=0
if [ -f "$EVENTS" ]; then
  while read -r seeded; do
    [ -n "$seeded" ] || continue
    DONE_IDS+=("$seeded"); DONE_COUNT=$((DONE_COUNT+1))
  done <<< "$(jq -r -s '[.[] | select(.event=="issue_done") | .issue] | unique | .[]' "$EVENTS" 2>/dev/null || true)"
  [ "$DONE_COUNT" -gt 0 ] && log "events から完了済みを復元: ${DONE_IDS[*]}"
fi

# ★ `-F`: id は `.` を含みうる（`issue_ids` の検証が許す）ので、正規表現として比べない。
is_done() { printf '%s\n' "${DONE_IDS[@]:-}" | grep -qxF -e "$1"; }
deps_met() { local d; for d in $(issue_deps "$1"); do is_done "$d" || return 1; done; return 0; }

# 自己依存・存在しない依存を起動前に検出して die する (デッドロックで黙って止まらないため)
# ⚠️★★★ **循環は検出していない**（★ `code-reviewer` LOW・2026-09-20 に指摘。旧コメントは
#   「循環を起動前に検出」と書いていたが**実装していなかった**）。★ ただし黙って止まりはしない ——
#   循環する issue は `deps_met` が永久に false になり、下の `remaining` ループを抜けて
#   `blocked`（「依存 issue が未完のため未実行」）が events に残る。⚠️ **原因が循環だとは書かれない。**
preflight_dag() {
  local id d bad=0 unparsed
  for id in $ALL; do
    for d in $(issue_deps_raw "$id"); do
      if [ "$d" = "$id" ]; then
        echo "loop-run: issue $id が自分自身に依存しています。## Dependencies の箇条書きから
         '$id' を削除してください (散文で自分に言及したい場合は箇条書きにしない)" >&2; bad=1
      elif ! printf '%s\n' $ALL_FILES | grep -qx "$d"; then
        # ⚠️★★★ `$ALL` ではなく `$ALL_FILES` (フィルタ前) で引く。
        #   ★ `$ALL` で引くと、Status=blocked で外れた issue に依存しているだけで
        #     「存在しません」と誤診して die する (★ 2026-09-20 の Status フィルタ導入で入りうる回帰)。
        echo "loop-run: issue $id の依存 $d が issues/ に存在しません" >&2; bad=1
      fi
    done
    # ⚠️★★★ P1-D（design.md 判断 7）: 箇条書きの先頭で拾えなかった 3 桁数字は WARN するが
    #   die しない。散文中の言及 (「issue 004 の merge 後に…」) は正当にありうるので、
    #   黙らないことが要点であって止めることではない。★ --dry-run でも見える (preflight は
    #   DRY_RUN の判定より前に走る)。
    unparsed="$(issue_deps_unparsed "$id")"
    if [ -n "$unparsed" ]; then
      log "WARN: issue $id の Dependencies に依存として拾わなかった 3 桁数字: $(printf '%s' "$unparsed" | tr '\n' ' ')（箇条書き行の先頭にない）"
    fi
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
  log "Status=blocked で除外:${SKIPPED_BLOCKED:- なし}"
  log "⚠ --dry-run で検証できるのは config / DAG まで。権限 (allowed_tools) / cwd 境界 / hook /"
  log "  契約の二重定義は --dry-run では観測できない。初回は最も安い issue 1 本を parallel=1 で回すこと。"
  exit 0
fi

log "開始: task=$(jq -r .task "$CFG") parallel=$PARALLEL mode=C"
# ⚠️★★★ 継続条件は「`deps_met` が真の issue がまだ `remaining` にあるか」だけ（★ 2026-09-27 是正）。
#   ⚠️ 旧実装は `progressed`（そのバッチで issue_done が 1 件でも出たか）でも止めていたため、
#     parallel=1 で**無関係な issue 1 本が失敗しただけで**ループを抜け、依存を満たしているのに
#     まだ試していない issue まで末尾で「依存 issue が未完のため未実行」の blocked にしていた
#     （★ 実測: `.steering/20260927-precondition8-t3-and-consent/blockers.md` §1）。
#   ★ 「試せる issue が無い」の判定は下の `[ -n "$batch" ] || break` が持つ。
#   ★ **停止と非再試行の保証**: バッチの issue は成否に関わらず `remaining` から外れるので、
#     1 周ごとに `remaining` は必ず 1 件以上減る（＝ 同じ issue を同じ run で再試行しない・
#     周回は高々 issue 数）。⚠️ この「成否に関わらず外す」を崩すなら、再試行ガードを別に要る。
#   ⚠️ ただし保証は**この 1 プロセスの中**だけ。`--issues` なしで同じ task を再実行すると、
#     `issue_done` 済みの issue も再び spawn される（★ 既存の挙動・done は ALL から外さない）。
# ⚠️★★★ run 全体を止める条件は 2 つだけ（★ 2026-09-27・`security-checker` MEDIUM / LOW）:
#   (a) 境界侵害 (`mark_boundary_breach`) —— 旧実装では parallel=1 の「どれか 1 本の失敗で抜ける」が
#       **偶然** fail-closed として効いていた。⚠️ それを消したので、意図した停止として入れ直す。
#   (b) token_ceiling 超過 —— バッチを組む前に見る（★ 超過後に worktree / branch を作らない）。
#   ★ 通常の失敗 (verify 赤・max_attempts・no_progress) では止めない（★ それが今回の是正）。
remaining="$ALL"; stop_reason=""; stop_kind=""
while [ -n "$remaining" ]; do
  if [ "$(tokens_used)" -ge "$TOKEN_CEIL" ]; then
    stop_kind="token_ceiling"; stop_reason="token_ceiling 超過のため run を中止し未実行"; break
  fi
  batch=""
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
      DONE_IDS+=("$id")
    fi
    remaining="$(printf '%s\n' $remaining | grep -vxF -e "$id" || true)"
  done
  if [ -s "$WORK_TMP/boundary-breach" ]; then
    stop_kind="boundary"
    stop_reason="境界侵害 (issue $(sort -u "$WORK_TMP/boundary-breach" | tr '\n' ' ' | sed 's/ $//')) のため run を中止し未実行"
    break
  fi
done

# 起動できなかった issue を明示的に blocked にする (握りつぶさない)。
#   ★ 既定の理由は「依存先が落ちた」。run を中止したときはその理由を書く。
[ -n "$stop_reason" ] && log "⚠️ $stop_reason"
for id in $remaining; do emit "$id" execute blocked detail="${stop_reason:-依存 issue が未完のため未実行}"; done

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
  # ⚠️ 除外した issue を**黙って消さない**（★ ALL から外すとこの表に 1 行も出ないため）。
  if [ -n "$SKIPPED_BLOCKED" ]; then
    echo; echo "## ⚠️ Status=blocked のため実行しなかった issue"
    echo; for id in $SKIPPED_BLOCKED; do
      printf -- '- %s — `%s`\n' "$id" "$(issue_status "$id" | head -c 120)"
    done
    echo; echo "★ 承知で回すなら \`--issues$(printf '%s' "$SKIPPED_BLOCKED" | tr ' ' ',')\` を付ける。"
  fi
  # ⚠️ run を中止したことを report にも残す（★ `code-reviewer` MEDIUM: log と各 issue の detail にしか出ていなかった）。
  if [ -n "$stop_reason" ]; then
    echo; echo "## ⚠️ run を中止した理由"
    echo; echo "- $stop_reason"
    [ "$stop_kind" = "boundary" ] && echo "- ★ worktree は残してある。原因を確かめてから \`bash scripts/loop-spawn.sh --cleanup <id>\` で撤去する。"
  fi
  echo; echo "次: /loop-status で board を確認 → 全緑なら code-reviewer(Opus) と /cross-review"
} > "$REPORT"
log "レポート: $REPORT"

# ⚠️★★★ 境界侵害で中止したら **非 0 で終わる**（★ 2026-09-27 判断 6）。
#   ★ 無人の呼び出し元（nohup / cron）が「通常終了」と区別できるように。
#   ★ token_ceiling は予定された予算の停止なので 0 のまま（report と events には残る）。
[ "$stop_kind" = "boundary" ] && exit 3
exit 0
