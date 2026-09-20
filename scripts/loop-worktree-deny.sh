#!/usr/bin/env bash
# loop-worktree-deny.sh — worktree の Claude セッションに必須 `permissions.deny` を注入する。
#
# ⚠️★★★ **なぜ要るか**（★ 2026-09-13 の前提監査で実測・2026-09-14 に再確認）:
#   ★ `.steering/_template/loop-config.README.md` は逐語でこう書いている ——
#     「許可を 1 つ間違えるだけで全体が迂回できる。**実質的な境界は worktree 隔離と
#       人間の merge ゲート**」「`.claude/settings.json` の `permissions.deny` を
#       **必ず併用する**（`deny` は allow と frontmatter の**両方に優先**）」。
#   ⚠️ ところが実測では:
#     - repo の `.claude/settings.json` の `deny` は **`chmod -R` / `sudo` の 2 件だけ**。
#       ★ 残り 5 件は `deny` ではなく **`ask`**（＝ 人が承認する前提の設定）に置かれている。
#       ⚠️ 無人モード C には**承認する人が居ない**ので、`ask` に頼る設計は前提を満たさない。
#     - ⚠️★★★ **deny を worktree へ入れる仕組みが 1 つも無かった**
#       (`loop-spawn.sh` / `loop-run.sh` を grep して `settings` は 0 件)。
#
# ★ 置き場が `<worktree>/.claude/settings.local.json` である理由:
#   1. ★ `.gitignore` で ignore 済み → **worktree ごとに別物にできる**。
#   2. ★ `.claude/` 自体は git 追跡なので、worktree には settings.json / agents / commands が複製される。
#   3. ⚠️★★★ **main checkout の `.claude/settings.json` に入れてはならない** ——
#      ★ 対話セッションでも `git push` が塞がれ、日常の作業が壊れる。
#
# ★ 使い方:
#   bash scripts/loop-worktree-deny.sh <worktree-dir>            # 注入（マージ）＋ 検査
#   bash scripts/loop-worktree-deny.sh --verify <worktree-dir>   # 検査のみ（書かない）
#   bash scripts/loop-worktree-deny.sh --print                   # 必須 deny を 1 行ずつ stdout へ
#
# ★ exit: 0 = 必須 deny が効いていることを確認できた / それ以外 = 確認できなかった（⚠️ fail-closed）
#
# ⚠️★★★ **縮退しない**: jq が無い / JSON が壊れている / 検査に失敗した、のいずれでも
#   「deny 無しで続行」はしない。★ 安全装置を条件つきで外すと、外れた事実が誰にも見えなくなる。
#
# 関連: .steering/20260914-loop-foundation-worktree-deny/
set -euo pipefail

PREFIX="[loop-deny]"
die() { echo "${PREFIX} ERROR: $*" >&2; exit 1; }
log() { echo "${PREFIX} $*" >&2; }   # ⚠️ stdout は使わない（loop-spawn.sh の stdout 契約を守る）

# ---------- 必須 deny（★ `loop-config.README.md` の逐語リストと集合一致させる） ----------
# ⚠️★★★ ここと README の 2 か所に同じリストが存在する（**契約の二重定義**）。
#   → ★ `loop-worktree-deny-test.sh` が `--print` の出力と README のコードブロックを
#     突き合わせ、**片方だけ増やす事故**を機械で止める。⚠️ 手で揃える運用にしない。
DENY_REQUIRED='["Bash(git push:*)","Bash(gh pr merge:*)","Bash(git reset --hard:*)","Bash(git rebase:*)","Bash(sudo:*)","Bash(rm -rf:*)","Bash(chmod -R:*)"]'

# ---------- 引数 ----------
MODE="apply"
case "${1:-}" in
  --print)  MODE="print"; shift ;;
  --verify) MODE="verify"; shift ;;
  -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
  "") die "worktree ディレクトリを指定してください (使い方は --help)" ;;
esac
# ⚠️ 余剰引数を黙って無視しない（★ `--print <dir>` のような取り違えを表に出す）
if [ "${MODE}" = "print" ] && [ $# -gt 0 ]; then die "--print は引数を取りません: $*"; fi
if [ "${MODE}" != "print" ] && [ $# -gt 1 ]; then die "引数が多すぎます: $*"; fi

command -v jq >/dev/null 2>&1 || die "jq が必要です。
  ★ deny の注入と検査は JSON の意味で行う必要があり、grep では代用しない。
  ⚠️ jq が無いことを理由に deny 無しで続行はしない (安全装置を黙って外さない)。
  → Windows(git-bash): winget install jqlang.jq / macOS: brew install jq"

if [ "${MODE}" = "print" ]; then
  # ⚠️★★★ Windows(git-bash) の jq は **CRLF で出力する**（★ 2026-09-14 に実測）。
  #   ★ 呼び出し側が行単位で突き合わせると **同じに見えるのに一致しない**ので、ここで CR を落とす。
  printf '%s' "${DENY_REQUIRED}" | jq -r '.[]' | tr -d '\r'
  exit 0
fi

WT="${1:?worktree ディレクトリを指定してください}"
[ -d "${WT}" ] || die "ディレクトリが存在しません: ${WT}"
SETTINGS_DIR="${WT}/.claude"
SETTINGS="${SETTINGS_DIR}/settings.local.json"

# ---------- 検査（★ 書いた後も必ずここを通す） ----------
# ⚠️★★★ 「書いたから入っているはず」で終わらせない（`verify-before-claiming` ルール 6）。
verify_deny() { # verify_deny <settings-file>; 0 = 必須 7 件がすべて在る
  local f="$1" out rc
  [ -f "${f}" ] || { log "検査: ファイルが無い → ${f}"; return 1; }
  jq -e 'type == "object"' "${f}" >/dev/null 2>&1 \
    || { log "検査: JSON オブジェクトとして読めない → ${f}"; return 1; }

  # ⚠️★★★ **jq の失敗を握りつぶさない**（★ 2026-09-14 に code-reviewer / security-checker が
  #   **両方 HIGH で指摘し、実測で再現した**）。
  #   ★ 旧実装は `2>/dev/null || true` だったため、`{"permissions": "nope"}` のように
  #     `.permissions.deny` を評価できない形では **jq が落ちて出力が空 → 「欠けなし」＝ 緑**になった。
  #     ⚠️ deny が 1 件も無いファイルを「必須 deny 7 件が効いている」と報告していた（＝ **fail-open**）。
  #   → ★ 対策は 2 段:
  #     (1) jq プログラムを **total** にする（型が想定外なら必須 7 件を全部「欠け」として出す）。
  #     (2) **sentinel を要求する** —— 出力が `__ALL_PRESENT__` でなければ合格にしない。
  #        ⚠️ これで「jq が落ちて出力が空」は**自動的に不合格**になる（★ 空 = 不合格）。
  out="$(jq -r --argjson req "${DENY_REQUIRED}" '
      (.permissions // {}) as $p
      | (if ($p | type) == "object" then ($p.deny // null) else null end) as $have
      | (if ($have | type) != "array" then $req else ($req - $have) end) as $missing
      | if ($missing | length) == 0 then "__ALL_PRESENT__" else $missing[] end
    ' "${f}" 2>/dev/null)"; rc=$?

  if [ "${rc}" -ne 0 ] || [ -z "${out}" ]; then
    log "検査: ⚠️ 検査そのものを実行できなかった (jq rc=${rc}) → ${f}"
    log "  ★ 「検査できなかった」を緑にしない。★ 不合格として扱う。"
    return 1
  fi
  if [ "${out}" != "__ALL_PRESENT__" ]; then
    log "検査: 必須 deny が欠けている →"
    printf '%s\n' "${out}" | while IFS= read -r m; do [ -n "${m}" ] && log "  - ${m}"; done
    return 1
  fi
  return 0
}

if [ "${MODE}" = "verify" ]; then
  verify_deny "${SETTINGS}" || die "必須 deny が効いていない: ${SETTINGS}"
  log "検査 OK: 必須 deny 7 件が効いている → ${SETTINGS}"
  exit 0
fi

# ---------- 注入 ----------
mkdir -p "${SETTINGS_DIR}" 2>/dev/null \
  || die "設定ディレクトリを作れない: ${SETTINGS_DIR}
  ⚠️ 同名の通常ファイルが在る / 書き込み権限が無い、のどちらかを確認すること。"

tmp="$(mktemp "${SETTINGS_DIR}/.settings.local.json.XXXXXX")" \
  || die "一時ファイルを作れない: ${SETTINGS_DIR}"
# ⚠️ 途中で死んだら一時ファイルを残さない（★ 次回の mktemp が増え続けるのを防ぐ）
#   ★ シグナルでも掃除する（⚠️ EXIT だけだと INT / TERM で残る形がありうる）。
trap 'rm -f "${tmp}"' EXIT INT TERM HUP

if [ -e "${SETTINGS}" ]; then
  # --- 既存あり: ⚠️ **上書きしない**。deny 配列へマージする（★ 他のキーを消さない） ---
  if ! jq -e 'type == "object"' "${SETTINGS}" >/dev/null 2>&1; then
    # ⚠️★★★ 壊れた JSON（またはオブジェクトでない JSON）は **触らずに落ちる**。
    #   ★ 人が置いた設定を黙って捨てない。★ 同時に「deny 無しで続行」もしない (fail-closed)。
    die "既存の settings.local.json を JSON オブジェクトとして読めない: ${SETTINGS}
  ⚠️ 安全のため**上書きしていない**。★ 手で直すか退避してから再実行すること。
  ★ 0 バイト（書き込み中断の痕跡）なら削除してから再実行してよい。"
  fi
  # ★ 既存の順序を保ったまま重複を落とす（unique は並べ替えてしまい diff が読みにくい）
  jq --argjson req "${DENY_REQUIRED}" '
      def dedupe: reduce .[] as $x ([]; if (index([$x]) != null) then . else . + [$x] end);
      .permissions = ((.permissions // {})
        | .deny = (((.deny // []) + $req) | dedupe))
    ' "${SETTINGS}" > "${tmp}" \
    || die "既存 settings.local.json のマージに失敗した: ${SETTINGS}
  ⚠️ permissions / permissions.deny の型が想定外の可能性がある。★ 上書きしていない。"
else
  # --- 既存なし（★ 通常経路。git worktree add は ignore 済みファイルを複製しない） ---
  printf '%s' "${DENY_REQUIRED}" | jq '{permissions: {deny: .}}' > "${tmp}" \
    || die "settings.local.json の生成に失敗した"
fi

# ★ 生成物が JSON として読めることを確認してから置き換える（⚠️ 壊れたものを置かない）
jq -e . "${tmp}" >/dev/null 2>&1 || die "生成した JSON が壊れている。★ 置き換えを中止した。"
mv "${tmp}" "${SETTINGS}"
trap - EXIT INT TERM HUP

# ---------- 書いた結果を読み直して検査する ----------
verify_deny "${SETTINGS}" || die "注入したのに必須 deny が揃っていない: ${SETTINGS}
  ⚠️★★★ この worktree で無人セッションを回してはならない。"

log "OK: 必須 deny 7 件を注入・確認した → ${SETTINGS}"
