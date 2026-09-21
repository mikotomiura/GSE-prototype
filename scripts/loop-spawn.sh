#!/usr/bin/env bash
# loop-spawn.sh — 1 issue 用の worktree を切り、その中で Claude セッションを起動する人間用ヘルパ。
#   使い方:  bash scripts/loop-spawn.sh --task <task> <issue-id> [short-slug]
#            bash scripts/loop-spawn.sh --cleanup <issue-id>
#            bash scripts/loop-spawn.sh --no-exec --task <task> <issue-id> [short-slug]   # worktree 生成のみ (モードC 用)
#
#   --task : ★ base の pin 元にする task。**ディレクトリ / basename / 日付接頭辞を落とした素名** の 3 形。
#            ★ env `LOOP_TASK` でも指定できる (⚠️ `--task` が優先)。
#            ⚠️★★★ `.steering/*/_loop-config.json` が **1 件以上**あるのに
#            `--task` / `LOOP_TASK` / `LOOP_BASE_BRANCH` のいずれも無ければ **止まる** (起票 23)。
#            ★ `--cleanup` は `--task` を使わない (撤去は base の解決に到達しない)。
# worktree は main checkout の隣 (../wt/) に作る。events は main checkout の絶対パスに集約されるため
# 各 worker が同じ _loop-events.jsonl に append できる。
set -euo pipefail

BASE_DEFAULT="${LOOP_BASE_BRANCH:-}"   # 未指定なら下で解決

die() { echo "loop-spawn: $*" >&2; exit 1; }

# ⚠️ このスクリプトは後段で repo_root → worktree と 2 回 cd するので、
#   ★ 兄弟スクリプトの場所は **cd する前に絶対パスで固定**する
#   (⚠️ `dirname "$0"` を後段で評価すると worktree 側の存在しないパスを指す)。
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ⚠️★★★ **main checkout (main worktree) を解決する。`--show-toplevel` をそのまま使わない。**
#   ★ `git rev-parse --show-toplevel` は **linked worktree の中では worktree 自身**を返す。
#   ⚠️ 2026-09-21 に実測: worktree の中から `--cleanup` を叩くと `repo_name` が
#     `<repo>-<id>-<short>` になり、★ **3 段が同時に無効化される** ——
#     (1) path 系統の一致が永久に当たらない (2) main checkout ガードが**本物の main を守らない**
#     (3) 残存 dir の網が存在しないパスを見る。
#     → ⚠️ `cleanup 完了` / exit 0 という**起票 18 と同じ嘘**に戻っていた (code-reviewer HIGH)。
#   ★ `git worktree list --porcelain` は **main worktree を必ず先頭に出す**ので、そこから取る。
#   ⚠️ awk で `exit` しない —— `set -o pipefail` 下で上流に SIGPIPE が飛ぶため (下記 `contains_line` と同じ理屈)。
main_worktree() {
  local out
  out="$(git worktree list --porcelain 2>/dev/null)" || return 1
  printf '%s\n' "${out}" | awk '/^worktree /{ if (!got) { print substr($0, 10); got = 1 } }'
}
repo_root="$(main_worktree)" || repo_root=""
if [ -z "${repo_root:-}" ]; then
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "git リポジトリ内で実行してください"
fi
here="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "${here:-}" ] && [ "${here}" != "${repo_root}" ]; then
  echo "loop-spawn: ★ linked worktree (${here}) から起動されたので main checkout (${repo_root}) で処理します" >&2
fi
cd "$repo_root"
repo_name="$(basename "$repo_root")"

# --- 先頭オプションの解析 ---
#   --no-exec: worktree 生成のみで Claude を起動しない (モードC 用)
#   --task   : ★ base の pin 元となる task を指定する (⚠️ 起票 23)
# ⚠️★★★ **このループは `--cleanup` の判定より *前* に置く。**
#   ★ `--cleanup` は `$1` で引く形を維持しており、`--task` を使わない
#     (★ 撤去は `resolve_base` に到達しないため)。
#   ⚠️ したがって `--cleanup` は先頭に来た時点でこのループを素通りする。
TASK_SEL="${LOOP_TASK:-}"   # ★ env は既定値。--task が来たら上書きする (--task が勝つ)
# ⚠️ die メッセージで「同じことをやり直す書き方」を出すために元の引数を控える
#   (★ 関数内の `$*` は **関数の引数**を指すので使えない)。
# ⚠️ **quoting は失われる** ので、空白入り slug ではそのままコプペしても再現しない
#   (★ die メッセージでは「参考」として示す。`code-reviewer` LOW・2026-09-21)。
SPAWN_ARGS="$*"
while true; do
  case "${1:-}" in
    --no-exec) LOOP_NO_EXEC=1; shift ;;
    --task)
      shift
      [ "$#" -gt 0 ] && [ -n "${1:-}" ] || die "--task にはタスク (ディレクトリ名 / パス / 素名) を指定してください"
      TASK_SEL="$1"; shift ;;
    --task=*)
      TASK_SEL="${1#--task=}"
      [ -n "$TASK_SEL" ] || die "--task= の値が空です"
      shift ;;
    *) break ;;
  esac
done

# --- base branch の解決 (pin) ---
# 優先順: LOOP_BASE_BRANCH → --task / LOOP_TASK で選んだ config の base_branch
#         → origin/HEAD → main → master → 現 HEAD
#
# ⚠ 未 merge の作業ブランチで作業している場合は必ず pin すること。
#    pin し忘れると main から worktree が切られ、実装がそこに存在しないため
#    **全 issue が即死する**。
#
# ⚠️★★★ **逆向きの事故もある (起票 23・2026-09-21 に実測)。**
#   ★ 旧実装は逐語 `cfg="$(ls -1 .steering/*/_loop-config.json ... | tail -1 || true)"` で、
#     ⚠️ **いま回そうとしている task と無関係に**、名前順で最後の config を **黙って 1 つ**拾っていた。
#   ★ 実害の実測: `LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz` が
#     **完了済みタスクの枝 (`docs/adr-030-stall-onset-definition`) から worktree を切り**、
#     ⚠️ **main より 38 コミット前**の状態になった (`git rev-list --left-right --count` = `38 0`)。
#   → ★ **task で選ぶ**。⚠️ **特定できなければ止める (fail-closed)** ——
#     ★★★ **config が 1 件でも止める** (⚠️ 研究者裁定 2026-09-21。
#     **上の事故は config が 1 件の状態で起きた**ので、「複数ヒットだけ止める」では直らない)。
#
# ⚠️★★★ **`jq` は使わない。**
#   ★ 旧実装は逐語 `b="$(jq -r '.base_branch // empty' "$cfg" 2>/dev/null || true)"` で、
#     ⚠️ **jq 不在 / 壊れた JSON / 不正な値のどれでも `b` が空になり、黙って main へ落ちた**
#     (＝ **config を書いたのに pin が無言で消える**)。
#   ★ jq を捨てる理由は 3 つ: (1) `ci.yml:651` 逐語「本テストは **jq を要らない**」を壊さない
#     (2) ⚠️ **macOS の self-hosted runner に jq があるか未検証**である (同じく ci.yml が明記)
#     (3) 読む値は **git のブランチ名 1 つ**で、config は repo が template から生成する機械可読ファイルである。

# json_top_value <file> <key>
#   ★ config から **深さ 1 (トップレベル) の** `"<key>": null` / `"<key>": "文字列"` を取り出す。
#
# ⚠️★★★ **行や正規表現で引いてはならない (2 つの理由で壊れる)。**
#   (a) ★ 既存テストが書く fake config は逐語 `  "task": "stub", "mode": "C", "base_branch": "main",`
#       で、**1 行に 3 キーが同居**している (`loop-worktree-deny-test.sh` / `loop-run-guard-test.sh`)。
#       ⚠️ かつ fake repo の default ブランチは `main` なので、取り逃がして fallback に落ちても
#       **結果が偶然一致し、テストは緑のまま穴が生きる** (→ 群 7k が守る)。
#   (b) ⚠️★★★ **深さを見ないと入れ子の同名キーを拾う。** ★ 2026-09-21 の `code-reviewer` HIGH を
#       一次で実測: `{"task":"a","headless":{"base_branch":"sneaky"}}` を正規表現版に食わせると
#       **`sneaky` を採って pin した**。⚠️ template には `headless` オブジェクトが実在するので、
#       `base_branch` をその中に書き間違えると **起票 23 と同クラスの事故**になる
#       (★ しかも `jq '.base_branch'` は null を返すので **人の検算と食い違う**)。
#
# ★ したがって **JSON を文字単位で歩く**。⚠️ 文字列の中の `{` `}` とエスケープを除外できるのは
#   この形だけである。★ config は数 KB なので費用は問題にならない。
#
# ★ 出力は 6 行:
#   1) nkey   深さ 1 で `"<key>":` が出た回数
#   2) nany   **深さを問わず**出た回数 (⚠️ `nany != nkey` なら入れ子に在る ＝ 呼び出し側が die する)
#   3) nval   値として `null` か単純な文字列を読めた回数
#   4) isnull 値が `null` だったか (★ **空文字列 `""` と区別するため** —— ⚠️ `""` は
#             「未指定」ではなく**打ち間違い**なので呼び出し側が die する)
#   5) bad    ⚠️ JSON が壊れている (未終端文字列 / 括弧の収支が合わない) —— ★ **黙って fallback しない**
#   6) val    値そのまま (⚠️ エスケープは展開しない。★ `\` が残れば `valid_refname` が弾く)
#
# ⚠️ awk で `exit` しない (★ `set -o pipefail` 下で上流に SIGPIPE が飛ぶ。main_worktree と同じ理屈)。
# ⚠️ 入力の `\r` を落とす (★ CRLF の config で `null` が行末に来ると値の判定が OS で割れる)。
json_top_value() {
  awk -v key="$2" '
    { sub(/\r$/, ""); buf = buf $0 "\n" }
    END {
      nkey = 0; nany = 0; nval = 0; isnull = 0; bad = 0; val = ""
      depth = 0; i = 1; n = length(buf)
      while (i <= n) {
        c = substr(buf, i, 1)
        if (c == "\"") {
          # 文字列を読み切る (★ エスケープを考慮)
          j = i + 1; content = ""; closed = 0
          while (j <= n) {
            d = substr(buf, j, 1)
            if (d == "\\") { content = content d substr(buf, j + 1, 1); j += 2; continue }
            if (d == "\"") { closed = 1; break }
            content = content d; j++
          }
          if (!closed) { bad = 1; break }
          i = j + 1
          if (content == key) {
            k = i
            while (k <= n && substr(buf, k, 1) ~ /[ \t\n]/) k++
            if (substr(buf, k, 1) == ":") {
              nany++
              # ⚠️★★★ **群 8b の変異当て先。** ★ この行を殺すと入れ子の同名キーを深さ 1 として
              #   数えるようになり、`{"h":{"base_branch":"sneaky"}}` で `sneaky` に pin される。
              #   ⚠️ 書き方を変えるときは 8b の sed も直す (★ 当たらなくなったら 8b が NG を出す)。
              if (depth != 1) { i = k + 1; continue }
              nkey++
              k++
              while (k <= n && substr(buf, k, 1) ~ /[ \t\n]/) k++
              if (substr(buf, k, 4) == "null" && substr(buf, k + 4, 1) ~ /[ \t\n,}]|^$/) {
                nval++; isnull = 1; val = ""
              } else if (substr(buf, k, 1) == "\"") {
                m = k + 1; sv = ""; sclosed = 0
                while (m <= n) {
                  d = substr(buf, m, 1)
                  if (d == "\\") { sv = sv d substr(buf, m + 1, 1); m += 2; continue }
                  if (d == "\"") { sclosed = 1; break }
                  sv = sv d; m++
                }
                if (!sclosed) { bad = 1; break }
                nval++; isnull = 0; val = sv
              }
            }
          }
          continue
        }
        if (c == "{" || c == "[") { depth++; i++; continue }
        if (c == "}" || c == "]") { depth--; i++; continue }
        i++
      }
      if (depth != 0) bad = 1
      print nkey; print nany; print nval; print isnull; print bad; print val
    }
  ' "$1"
}

# sanitize_disp <値> → ⚠️ 表示・ログに出す前に通す
#   ⚠️★★★ **config の値を生で echo してはならない** (★ `security-checker` MEDIUM・2026-09-21)。
#   ★ 実測: `"task": "t<ESC>[8m EVIL"` の ESC バイトは抽出器を素通りし、
#     `config.task=` 行に残る。→ ⚠️ 端末で `\x1b[8m` (conceal) や `\r` を使うと、
#     ★★★ **その *後* に出る `start` 行と「⚠️ 乖離 = 既定より N コミット後ろ」行を
#     不可視・上書きにできる** ＝ **本スクリプトが足した唯一の検知手段を、記録を残したまま無力化できる**。
#   ⚠️ worktree の worker は `acceptEdits` で走り、deny は Bash の 9 パターンだけなので
#     **main checkout の `_loop-config.json` を Write で書き換える経路が開いている**。
#   → ★ 制御文字を落とし、長さも切る (⚠️ `loop-run.sh` の `log` に redaction は無いので **出す側で消す**)。
sanitize_disp() {
  printf '%s' "$1" | LC_ALL=C tr -d '\000-\037\177' | cut -c1-200
}

# valid_refname <value>
#   ⚠️★★★ **解決した base は `git fetch origin "$base"` と `git worktree add ... "$start"` に
#     引数として流れる** ので、★ 先頭が `-` の値は **オプションとして読まれうる**。
#   ★★★ これは机上ではない —— `security-checker` が使い捨て repo で実測 (2026-09-21):
#     `git fetch origin --bogus-opt` は **位置引数の後でもオプションとして解釈され**、
#     ⚠️ `git fetch origin --upload-pack=echo` は **警告のみで受理される**。
#     → ★ 旧実装 (`jq -r` の結果を無検証で渡す) では、config に
#       `"base_branch": "--upload-pack=<cmd>"` を書くだけで **コマンド実行に到達しえた**。
#     ★ `:` `+` `^` `~` `@{` `*` も文字集合で落ちるので、**`X:Y` 形の refspec で
#       fetch にローカル ref を上書きさせる経路**も閉じている。
#
# ⚠️★★★ **`git check-ref-format --branch` は「ブランチ名として妥当か」しか見ない。**
#   ★ 実測 (2026-09-21): `HEAD` と `main.lock` は落ちるが、
#     ⚠️ **`FETCH_HEAD` / `ORIG_HEAD` / 40 桁 hex / `refs/heads/main` / `origin/main` は通る**。
#   ⚠️ うち **`FETCH_HEAD` と 40 桁 hex は `git worktree add` が *成功する*** ——
#     ★ 「直前に誰かが fetch した何か」や **どのブランチにも乗っていない commit** から
#     worktree が切られる。→ ★ **予約名 / `refs/` / hex を明示的に拒否する。**
valid_refname() {
  local v="$1" first
  case "$v" in
    ''|-*) return 1 ;;
    */) return 1 ;;
    *..*) return 1 ;;
    *[!A-Za-z0-9._/-]*) return 1 ;;
    refs/*) return 1 ;;                       # ⚠️ 完全修飾は受けない (★ origin/refs/... に化ける)
  esac
  # ⚠️ git の pseudo-ref を拒否する。
  #   ⚠️★★★ **「先頭コンポーネントが全部大文字なら拒否」にしてはならない**
  #     (★ Codex `/cross-review` 1 巡目・2026-09-21)。★ 実測で `RELEASE/2026-09` /
  #     `FEATURE/foo` / `HOTFIX/x` まで**誤って拒否していた** ——
  #     ⚠️ 運用ブランチを大文字で切る repo では徒に止まる。
  #   ★ 実在する pseudo-ref はすべて `HEAD` か `*_HEAD` か `AUTO_MERGE` である
  #     (HEAD / FETCH_HEAD / ORIG_HEAD / MERGE_HEAD / CHERRY_PICK_HEAD /
  #      REVERT_HEAD / BISECT_HEAD / REBASE_HEAD / AUTO_MERGE)。→ ★ **そこだけを拒む**。
  case "$v" in
    HEAD|*_HEAD|AUTO_MERGE) return 1 ;;
  esac
  # ⚠️ commit sha を枝と誤認しない (★ 40 桁 = SHA-1 / 64 桁 = SHA-256)
  case "$v" in
    *[!0-9a-fA-F]*) : ;;
    *) [ "${#v}" -ne 40 ] && [ "${#v}" -ne 64 ] || return 1 ;;
  esac
  git check-ref-format --branch "$v" >/dev/null 2>&1
}

# list_configs → .steering/*/_loop-config.json を 1 行 1 件で出す (★ 0 件なら何も出さない)
#   ⚠️ `ls -1` に依存しない (★ Codex `/cross-review` 1 巡目・2026-09-21) ——
#     ★ glob を直接回すので `ls` の出力整形に左右されない。
#   ⚠️ ただし **ディレクトリ名に改行が入ると行単位の出力は壊れる**
#     (★ 本 repo の task dir は kebab-case 規約であり、改行入りなら
#      `.steering/` の他の仕組みも先に壊れるので、ここでは抱えない)。
list_configs() {
  local c
  for c in .steering/*/_loop-config.json; do
    [ -f "$c" ] && printf '%s
' "$c"
  done
  return 0
}

# find_task_config <selector> → ★ 一致した config のパスを **FOUND_CFG に入れる** (⚠️ 0 件 / 複数件なら die)
#   ⚠️★★★ **stdout で返してはならない。**
#     ★ `cfg="$(find_task_config ...)"` の形にすると、**die (exit) が
#       コマンド置換のサブシェルしか抜けず**、⚠️ 呼び出し元は `cfg` が空のまま**続行する**
#       (＝ **fail-closed のつもりで fail-open になる**)。→ ★ グローバルで返す。
#   ★ selector の 3 形を受ける:
#     (a) ディレクトリ (絶対でも相対でも) —— ★ モードC が `$TASK_DIR` を渡す形
#     (b) task ディレクトリの basename そのまま (`20260914-mhd-feature-offline-tiers`)
#     (c) 日付接頭辞を落とした素名 (`mhd-feature-offline-tiers`)
#
# ⚠️★★★ **解決先は必ず `<repo>/.steering/<task>/_loop-config.json` の形に閉じる**
#   (★ `security-checker` MEDIUM・2026-09-21)。★ 閉じない場合の実害:
#   ⚠️ `--task .steering/20260914-foo/requirement.md` (★ タブ補完で 1 つ深く押した) が
#     `[ -f "$sel" ]` に当たり、**config でないファイルを config として受ける** →
#     キー 0 件 → **die せず fallback** ＝ ★ **起票 23 の事故が別経路で復活する**。
#   ⚠️ かつ `--task /abs/any/dir` / `--task ../../other/x.json` で **repo 外**も読めた。
FOUND_CFG=""
# cfg_rel <path> → ★ repo 相対の `.steering/<task>/_loop-config.json` を CFG_REL に入れる (⚠️ 形が違えば非 0)
#   ⚠️★★★ **`$repo_root` の前方一致で相対化してはならない。**
#     ★ Windows では `git worktree list --porcelain` が `C:/GSE-prototype` を返し、
#       一方モードC が渡す `$TASK_DIR` は `/c/GSE-prototype/...` になりうる (★ bash の `pwd` 由来)。
#     ⚠️ 前方一致で剥がすと**一致せず、モードC が Windows だけで死ぬ**。
#   → ★ **`/.steering/` の位置から相対形を組み立て、repo 相対で存在を確かめる。**
#     ⚠️ これにより **読む対象は必ず main checkout 直下の `.steering/*/_loop-config.json` に閉じる**
#       (★ 絶対パスで repo 外を指されても、repo 外は 1 バイトも読まない)。
#     ★ 実際に読んだパスは provenance 行に出るので、人が食い違いに気づける。
CFG_REL=""
cfg_rel() {
  local p="$1"
  CFG_REL=""
  case "$p" in *..*) return 1 ;; esac         # ⚠️ .steering/../.. を弾く
  case "$p" in
    .steering/*/_loop-config.json)   CFG_REL="$p" ;;
    */.steering/*/_loop-config.json) CFG_REL=".steering/${p#*/.steering/}" ;;
    *) return 1 ;;
  esac
  # ★ 入れ子が深すぎる形 (.steering/a/b/_loop-config.json) を弾く
  case "${CFG_REL#.steering/}" in */*/*) return 1 ;; esac
  [ -f "$CFG_REL" ]
}
find_task_config() {
  local sel="$1" hits="" n=0 c bn cand
  FOUND_CFG=""
  # (a) ディレクトリとして解釈できるか (★ モードC が渡す形)
  if [ -d "$sel" ] && [ -f "$sel/_loop-config.json" ]; then
    cand="$sel/_loop-config.json"
    cfg_rel "$cand" \
      || die "--task が repo の .steering/<task>/ の形になっていません: [$(sanitize_disp "$cand")]"
    FOUND_CFG="$CFG_REL"; return 0
  fi
  # ⚠️ **任意の既存ファイルを受けない** —— ★ basename と位置の両方を要求する
  if [ -f "$sel" ]; then
    cfg_rel "$sel" \
      || die "--task にはタスクのディレクトリか _loop-config.json を指定してください: [$(sanitize_disp "$sel")]
            ⚠️ 指定されたのは repo の .steering/<task>/_loop-config.json ではありません。
            ★ config でないファイルを config として受けると、キーが 0 件になって
              **黙って既定ブランチへ落ちます** ＝ 起票 23 の事故が別経路で復活します。"
    FOUND_CFG="$CFG_REL"; return 0
  fi
  # (b) / (c) 名前で引く
  # ⚠️ `????????-` は **任意の 8 文字**に当たる (★ `code-reviewer` MEDIUM・2026-09-21 実測:
  #   `fix-loop-spawn` → `spawn` / `loop_run-x` → `x`)。→ ★ **数字 8 桁に限る。**
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    bn="$(basename "$(dirname "$c")")"
    if [ "$bn" = "$sel" ] || [ "${bn#[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-}" = "$sel" ]; then
      hits="${hits}${c}
"
      n=$((n + 1))
    fi
  done <<EOF
$(list_configs)
EOF
  if [ "$n" -eq 0 ]; then
    {
      echo "loop-spawn: ⚠️ --task で指定したタスクの _loop-config.json が見つかりません: [${sel}]"
      echo "            ★ 現存する候補:"
      list_configs | sed 's/^/              - /'
      echo "            ★ 指定できる形: ディレクトリ (.steering/20260914-foo) / basename (20260914-foo) / 素名 (foo)"
    } >&2
    exit 1
  fi
  if [ "$n" -gt 1 ]; then
    {
      echo "loop-spawn: ⚠️★★★ --task [${sel}] が ${n} 件に一致しました。★ 一意に指定してください。"
      printf '%s' "$hits" | sed 's/^/              - /'
    } >&2
    exit 1
  fi
  # ★ 1 件だけ残っているので、末尾の改行を落として返す
  #   ⚠️ bash 限定の入れ子パターン展開は使わない
  #   (★ macOS 既定の bash 3.2 を踏む必要がない。`code-reviewer` LOW・2026-09-21)。
  FOUND_CFG="$(printf '%s' "$hits" | sed -n '1p')"
}

# resolve_base → ★ 結果を RESOLVED_BASE / RESOLVED_FROM に入れる
#   ⚠️ stdout で返さない —— ★ provenance を 2 値目として返す必要があり、
#     stdout を 2 行にすると呼び出し側 (`base="$(resolve_base)"`) が壊れるため。
RESOLVED_BASE=""
RESOLVED_FROM=""
resolve_base() {
  if [ -n "$BASE_DEFAULT" ]; then
    RESOLVED_BASE="$BASE_DEFAULT"; RESOLVED_FROM="env:LOOP_BASE_BRANCH"
    valid_refname "$RESOLVED_BASE" \
      || die "LOOP_BASE_BRANCH の値がブランチ名として妥当ではありません: [${RESOLVED_BASE}]"
    return
  fi

  local b="" cfg="" n_cfg=0
  # ⚠️★★★ **`|| true` で飲まない** (★ `security-checker` LOW・2026-09-21) ——
  #   ★ 旧形 `n_cfg="$(list_configs | grep -c . || true)"` は、grep 不在なら `n_cfg` が **空**になり、
  #     `${n_cfg:-0}` で 0 に化けて ⚠️ **下の fail-closed ブロックを飛ばして黙って fallback** する。
  #   → ★ **起票 23 で潰したのと同じ形の生き残り**だったので、数えたうえで**数値であることを要求する**。
  n_cfg="$(list_configs | wc -l)" || die "config の候補を数えられませんでした (★ 判定せず止まります)"
  n_cfg="${n_cfg//[[:space:]]/}"
  case "${n_cfg}" in
    ''|*[!0-9]*) die "config の件数が数値として読めません: [${n_cfg}] (★ 判定せず止まります)" ;;
  esac

  if [ -n "${TASK_SEL:-}" ]; then
    # ⚠️ コマンド置換にしない (★ die が抜けなくなる。find_task_config 冒頭の注記)
    find_task_config "$TASK_SEL"
    cfg="$FOUND_CFG"
  elif [ "${n_cfg:-0}" -gt 0 ]; then
    # ⚠️★★★ **ここが起票 23 の本丸。黙って 1 つ選ばない。**
    {
      echo "loop-spawn: ⚠️★★★ base の pin 元を特定できません (★ 起票 23 の fail-closed)。"
      echo "            .steering/ に _loop-config.json が ${n_cfg} 件あります:"
      while IFS= read -r c; do
        [ -n "$c" ] || continue
        local bb
        bb="$(json_top_value "$c" base_branch | sed -n '6p')"
        echo "              - $(dirname "$c")  (base_branch=$(sanitize_disp "${bb:-null}"))"
      done <<EOF2
$(list_configs)
EOF2
      echo "            ★ どちらかを指定してください (⚠️ 引数の quoting は失われているので **参考**):"
      echo "              bash scripts/loop-spawn.sh --task <task> ${SPAWN_ARGS}"
      echo "              LOOP_BASE_BRANCH=main bash scripts/loop-spawn.sh ${SPAWN_ARGS}"
      echo "            ⚠️ 黙って 1 つ選ぶことはしません (★ 2026-09-21 に 38 コミット前の枝から"
      echo "               worktree が切られた実測がある)。"
    } >&2
    exit 1
  fi

  if [ -n "${cfg:-}" ]; then
    [ -f "$cfg" ] || die "config が読めません: [$(sanitize_disp "$cfg")]"
    # ★ 判定表 (⚠️ **想定外は必ず die**。黙って fallback する経路を作らない):
    #   | bad=1                          | ⚠️ JSON が壊れている            → die |
    #   | nany != nkey                   | ⚠️ 深さ 1 以外に base_branch    → die |
    #   | nkey > 1                       | ⚠️ 深さ 1 に複数                → die |
    #   | nkey=1 かつ nval != 1          | ⚠️ 値が null / 文字列でない     → die |
    #   | nkey=1, nval=1, isnull=1       | ★ 未指定として fallback (正当)        |
    #   | nkey=1, nval=1, isnull=0, 空   | ⚠️ 明示的な空文字列 = 打ち間違い → die |
    #   | nkey=1, nval=1, isnull=0, 有値 | ★ 検証して採用                        |
    #   | nkey=0 かつ nany=0             | ★ キー無し → fallback (正当)          |
    local out n_key n_any n_val is_null is_bad
    out="$(json_top_value "$cfg" base_branch)" \
      || die "config の読み取りに失敗しました: [$(sanitize_disp "$cfg")]"
    n_key="$(printf '%s\n' "$out" | sed -n '1p')"
    n_any="$(printf '%s\n' "$out" | sed -n '2p')"
    n_val="$(printf '%s\n' "$out" | sed -n '3p')"
    is_null="$(printf '%s\n' "$out" | sed -n '4p')"
    is_bad="$(printf '%s\n' "$out" | sed -n '5p')"
    b="$(printf '%s\n' "$out" | sed -n '6p')"
    if [ "${is_bad:-0}" -ne 0 ]; then
      die "config の JSON が壊れています (★ 未終端の文字列か括弧の収支が合いません): [$(sanitize_disp "$cfg")]
            ⚠️ 黙って既定ブランチへ落ちることはしません (★ 起票 23)。"
    fi
    if [ "${n_any:-0}" -ne "${n_key:-0}" ]; then
      die "config の base_branch が **深さ 1 (トップレベル) 以外**にあります: [$(sanitize_disp "$cfg")]
            ★ 深さ 1 に ${n_key} 件 / 全体に ${n_any} 件。
            ⚠️★★★ 入れ子 (例: \"headless\": { \"base_branch\": … }) に書いた pin は効きません。
            ★ jq '.base_branch' も null を返すので、**人の検算と食い違います**。
            → ★ base_branch はトップレベルに 1 つだけ置いてください。"
    fi
    if [ "${n_key:-0}" -gt 1 ]; then
      die "config の深さ 1 に base_branch が ${n_key} 回出てきます (⚠️ 推測で 1 つ選びません): [$(sanitize_disp "$cfg")]"
    fi
    if [ "${n_key:-0}" -eq 1 ] && [ "${n_val:-0}" -ne 1 ]; then
      die "config の base_branch の値を読めません (★ null か単純な文字列だけを受けます): [$(sanitize_disp "$cfg")]"
    fi
    if [ "${n_key:-0}" -eq 1 ] && [ "${is_null:-0}" -eq 0 ] && [ -z "${b:-}" ]; then
      # ⚠️★★★ `""` は「未指定」ではない —— ★ pin を書こうとした打ち間違いである。
      #   → ★ null と同じ扱いにすると「**pin を書いたのに無言で main へ落ちる**」が復活する。
      die "config の base_branch が空文字列です: [$(sanitize_disp "$cfg")]
            ★ pin しないなら null を書いてください (⚠️ \"\" は打ち間違いとして扱います)。"
    fi
    # ★ config の `task` は **表示のためだけ**に読む (⚠️ 一致を強制する門にはしない ——
    #   ★ 「ディレクトリ名と config.task の正規化規則」を新しく発明することになり、
    #     ⚠️ その規則自体が黙って間違うクラスを増やす。→ **人が見て気づける形**に留める)。
    cfg_task_name="$(json_top_value "$cfg" task | sed -n '6p')" || cfg_task_name=""
    if [ -n "${b:-}" ]; then
      valid_refname "$b" \
        || die "config の base_branch がブランチ名として妥当ではありません: [$(sanitize_disp "$b")]  ($(sanitize_disp "$cfg"))
            ⚠️ 受けないもの: 先頭が '-' / 空白や引用符を含む / '..' / 'refs/' 始まり /
               予約名 (HEAD・FETCH_HEAD・ORIG_HEAD …) / 40 桁・64 桁の hex (＝ commit sha)。"
      RESOLVED_BASE="$b"; RESOLVED_FROM="config:${cfg}"
      return
    fi
    # ★ キーが無い / null → 未指定として fallback (⚠️ die しない)
    #   ⚠️ 「null」と言い切らない —— ★ ここへ来る理由は **キー無し** と **null** の 2 つある
    #     (★ `code-reviewer` MEDIUM・2026-09-21: 旧文言は 4 状態を「null」と言い切っていた)。
    RESOLVED_FROM="fallback (config:${cfg} の base_branch は未指定 = キー無し または null)"
  else
    RESOLVED_FROM="fallback (config なし)"
  fi

  # origin/HEAD が指す既定ブランチ → 無ければ main → master の順
  b="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')" || true
  if [ -n "${b:-}" ]; then
    RESOLVED_BASE="$b"; RESOLVED_FROM="${RESOLVED_FROM} → origin/HEAD"; return
  fi
  if git show-ref --verify --quiet refs/heads/main; then
    RESOLVED_BASE=main; RESOLVED_FROM="${RESOLVED_FROM} → refs/heads/main"; return
  fi
  if git show-ref --verify --quiet refs/heads/master; then
    RESOLVED_BASE=master; RESOLVED_FROM="${RESOLVED_FROM} → refs/heads/master"; return
  fi
  RESOLVED_BASE="$(git rev-parse --abbrev-ref HEAD)"
  RESOLVED_FROM="${RESOLVED_FROM} → 現 HEAD"
}

# default_branch → ★ 乖離の基準に使う既定ブランチ
# ⚠️★★★ **remote-tracking を優先する。**
#   ★ `start` は fetch 成功時に `origin/$base` になる（下の `--- base を remote と同期 ---`）。
#   ⚠️ 基準側を**ローカル**の `main` にすると **片側だけ remote** という非対称になり、
#     ★ **ローカル main が古い環境では `behind` が過小に出て、古い pin を見逃す**
#     （＝ 起票 23 が起きうる状況そのもの。`code-reviewer` MEDIUM / `security-checker` LOW・2026-09-21）。
#   → ★ `refs/remotes/origin/<d>` が在ればそれを使い、無ければローカルへ縮退する。
default_branch() {
  local d
  d="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')" || true
  if [ -z "${d:-}" ]; then
    if git show-ref --verify --quiet refs/heads/main; then d=main
    elif git show-ref --verify --quiet refs/heads/master; then d=master
    fi
  fi
  [ -n "${d:-}" ] || return 0
  if git show-ref --verify --quiet "refs/remotes/origin/${d}"; then
    printf '%s' "origin/${d}"
  else
    printf '%s' "$d"
  fi
}

# --- cleanup モード (merge 後の撤去) ---
# ⚠️★★★ **撤去できたことを確かめてから「完了」と書く**（★ 起票 18・2026-09-20 の実測で発見）。
#   ★ 旧実装は worktree を **ブランチ名だけ**で引いていたので、
#     ⚠️ 起票 10 の形で `loop/<id>-*` から逸脱した worktree が **1 件もヒットせず**、
#     **branch だけ消して worktree を残したまま `cleanup 完了` / exit 0** を返していた。
#     ★ 実害: 同じ id の再実行が恒久的に死に (下の `:同名 worktree が既に存在`)、
#       ⚠️ main checkout が `main` を取れなくなり、**失敗が誰にも見えない**。
#   → ★ 直し方は 3 つ: **(1) パスでも引く (2) 撤去できたか再確認してから報告する
#     (3) 1 つでも残ったら非 0 で止まる**。
#
# ★ 一致規則は **branch と path の 2 系統**（どちらかに当たれば対象）:
#     branch: `loop/<id>` 完全一致 / `loop/<id>-` 前方一致
#     path  : basename が `<repo>-<id>` 完全一致 / `<repo>-<id>-` 前方一致
#   ⚠️ 前方一致には区切り `-` を要求する —— ★ 旧実装の `$0 ~ ("loop/" id)` は
#     **正規表現の部分一致**なので `--cleanup zzz` が `loop/zzz2-issue` にも当たった。
#   ★ `<id>-<short>` を丸ごと渡す運用 (`--cleanup 001-issue`) が実在するので**完全一致も許す**。
if [ "${1:-}" = "--cleanup" ]; then
  id="${2:?--cleanup には issue-id が必要です}"
  # ⚠️★★★ **id を検証する** (★ security-checker MEDIUM・2026-09-21)。
  #   ★ `git branch --list` の引数は **fnmatch パターン**なので、`--cleanup '*'` は `loop/*` に化け、
  #     ⚠️ **merge 済みの `loop/*` ブランチが全部 `-d` の対象になる**。
  #   ⚠️ 一方 worktree 側の一致は literal 比較 (`==` / `index()`) なので glob を解釈せず、
  #     ★ **両系統の広さが非対称**になる (branch だけ全部消え、worktree は 1 件も消えない)。
  #   ★ 併せて閉じるもの: `../wt/` の外を指す `..` / `/` と、`awk -v` がエスケープ列として
  #     解釈する `\` (⚠️ シェル側の glob と awk 側の一致文字列がずれる)。
  case "${id}" in
    -*) die "issue-id が '-' 始まりです: [${id}]" ;;
    *[!A-Za-z0-9._-]*) die "issue-id に使えない文字が入っています (英数字 . _ - のみ): [${id}]" ;;
    # ★ `.` / `..` / `a..b` は上を通るが、ref としても名前としても紛らわしい (⚠️ Codex /cross-review 1 巡目)。
    #   ★ パス脱出は起きない (`<repo>-..` は 1 つの名前であって親ディレクトリではない) が、通す意味も無い。
    .|..|*..*) die "issue-id にドットの連なりは使えません: [${id}]" ;;
  esac
  left=0; n_wt=0; n_br=0; processed_path=""

  # ★ 登録済み worktree の **パス** 集合を返す（★ git の出力そのまま）。
  #   ⚠️ **取得できなければ非 0 を返す**（★ code-reviewer MEDIUM —— 旧版はエラーを握りつぶして
  #     空を返し、⚠️ 「取れなかった」を「撤去できた」と読んでいた）。
  #   ★ **パスで突き合わせてよいのはここだけ** —— ⚠️ 比べる相手 (`${wt}`) も **git の出力**だからである
  #     (★ bash の `pwd` は `/c/wt/...`、git は `C:/wt/...` を返すので、混ぜると必ずずれる)。
  registered_paths() {
    local out
    out="$(git worktree list --porcelain 2>/dev/null)" || return 1
    printf '%s\n' "${out}" | awk '/^worktree /{print substr($0, 10)}'
  }
  # ★ 登録済み worktree の **basename** 集合（★ シェル側のパスと突き合わせるときだけ使う）。
  registered_bn() {
    local out
    out="$(registered_paths)" || return 1
    printf '%s\n' "${out}" \
      | awk '{p=$0; gsub(/\\/,"/",p); n=split(p,seg,"/"); if (p != "") print seg[n]}'
  }
  # ★ 改行を番兵にした完全一致判定（⚠️ `grep -q` を使わない —— `set -o pipefail` 下では
  #   grep の早期終了が上流に SIGPIPE を投げ、**一致したのに非 0** になりうるため）。
  contains_line() { # contains_line <candidates> <needle>
    case "
$1
" in
      *"
$2
"*) return 0 ;;
    esac
    return 1
  }

  # ★ path 系統が見てよい置き場（★ `git` の表記で組み立てる —— `repo_root` が git 由来なので揃う）。
  #   ⚠️★★★ **basename だけで一致させない**（★ 2026-09-21 に新テストが実害を検出）——
  #     `--cleanup 013` が、**別の場所にある同名 worktree**（`../other/<repo>-013-t`）まで撤去していた。
  #   ★ 本スクリプトが作る worktree は必ず `../wt/` 直下なので、**そこに限る**。
  #   ⚠️ 置き場を移されたものは path 系統では拾えない（★ branch 系統が `loop/<id>` なら拾う）。
  wt_home="$(dirname "${repo_root}")/wt/"

  # porcelain の worktree 行はプレフィックス除去で取得 (空白入りパスに耐える)
  # ⚠️ 取得に失敗したら黙って進まない (★ `set -o pipefail` 下では無言で exit していた)。
  wts="$(git worktree list --porcelain | awk -v id="${id}" -v rn="${repo_name}" -v home="${wt_home}" '
    BEGIN {
      exa_p = rn "-" id; pfx_p = rn "-" id "-"; exa_b = "loop/" id; pfx_b = "loop/" id "-"
      # ⚠️ 表記の正規化は **両側に**かける（★ Codex /cross-review 2 巡目）——
      #   ★ worktree パス側だけ `\` → `/` にして `home` を素のままにすると、
      #   ⚠️ 区切りが混ざった環境で path 系統が**空振り**し、直したはずの穴が戻る。
      gsub(/\\/, "/", home)
    }
    function flush() {
      if (p != "" && (hitb || hitp)) print p
      p = ""; hitb = 0; hitp = 0
    }
    /^worktree /{
      flush()
      p = substr($0, 10)
      q = p; gsub(/\\/, "/", q); n = split(q, seg, "/"); bn = seg[n]
      # ★ 名前が合うだけでは足りない —— **`../wt/` 直下にあること**も要求する。
      if (index(q, home) == 1 && (bn == exa_p || index(bn, pfx_p) == 1)) hitp = 1
    }
    /^branch /{
      b = substr($0, 8); sub(/^refs\/heads\//, "", b)
      if (b == exa_b || index(b, pfx_b) == 1) hitb = 1
    }
    END { flush() }
  ')" || die "worktree の一覧を取得できませんでした"

  if [ -n "${wts}" ]; then
    while IFS= read -r wt; do
      [ -n "${wt}" ] || continue
      wt_bn="$(basename "${wt}")"
      # ★ 触ったものを**パスで**記録する (⚠️ basename では別 worktree と衝突する ——
      #   `/elsewhere/<repo>-001-t` を撤去すると `../wt/<repo>-001-t` が黙って除外された)。
      #   ★ 値は git の出力そのままなので、後段も git の出力と突き合わせる (表記が揃う)。
      processed_path="${processed_path}
${wt}"
      # ⚠️★★★ main checkout は**絶対に**撤去しない（★ 明示ガード。basename 規則上は届かないが置く）。
      if [ "${wt}" = "${repo_root}" ]; then
        echo "loop-spawn: ⚠️ main checkout (${wt}) は撤去対象にしません" >&2
        echo "            ★ この id を掴んでいるのは main checkout 自身です (branch を切り替えてから再実行)" >&2
        left=$((left + 1))
        continue
      fi
      # ⚠️★★★ **未コミット変更がある worktree を黙って捨てない**（★ security-checker MEDIUM）。
      #   ★ branch 側で `-D` を使わないと決めた判断と同じ理屈である。
      #   ⚠️ 逸脱した worktree（起票 10 の形）は **作業が載っている可能性が最も高い**対象であり、
      #     旧実装のように `--force` を無条件で撃つと**復旧不能に失われる**。
      #   ⚠️★★★ **status が読めないときも撤去しない**（★ Codex /cross-review 2 巡目）——
      #     旧版は `|| true` で「dirty なし」に倒れ、⚠️ 権限・破損・I/O エラーのときに
      #     **`--force` まで進んでいた**（★ fail-open）。
      if ! dirty="$(git -C "${wt}" status --porcelain 2>/dev/null)"; then
        echo "loop-spawn: ⚠️ 状態を読めないので撤去しません: ${wt}" >&2
        echo "            ★ 手で確認:  git -C \"${wt}\" status" >&2
        left=$((left + 1))
        continue
      fi
      if [ -n "${dirty}" ]; then
        echo "loop-spawn: ⚠️ 未コミット変更があるので撤去しません: ${wt}" >&2
        echo "            ★ 中身を確認:  git -C \"${wt}\" status" >&2
        echo "            ★ 捨ててよいなら:  git worktree remove --force \"${wt}\"" >&2
        left=$((left + 1))
        continue
      fi
      if ! git worktree remove "${wt}" >/dev/null 2>&1; then
        # ⚠️ `--force` へ落ちたことを**黙らない**（★ 旧実装は無音だった）。
        echo "loop-spawn: ★ 通常の remove が通らないので --force で再試行します: ${wt}" >&2
        git worktree remove --force "${wt}" >/dev/null 2>&1 || true
      fi
      # ★ remove の exit code を信じず、**登録とディレクトリを引き直して**確かめる。
      #   ⚠️ 登録を読めなかったときは「撤去できた」と書かない（fail-closed）。
      #   ⚠️ **basename ではなくパスで見る**（★ Codex /cross-review 1 巡目）——
      #     別パスに同じ basename の worktree が登録されていると、
      #     ★ 対象は消えているのに「撤去失敗」と誤判定していた（⚠️ 安全側だが嘘である）。
      still=1
      if reg="$(registered_paths)"; then
        still=0
        if contains_line "${reg}" "${wt}"; then still=1; fi
        if [ -e "${wt}" ]; then still=1; fi
      else
        echo "loop-spawn: ⚠️ worktree 登録を読めませんでした (撤去できたか確認できません)" >&2
      fi
      if [ "${still}" -eq 1 ]; then
        echo "loop-spawn: ⚠️ worktree 撤去失敗: ${wt}" >&2
        echo "            ★ lock されているなら:  git worktree unlock \"${wt}\"  →  git worktree remove --force \"${wt}\"" >&2
        echo "            ★ それでも残るなら中身を確認のうえ手で削除してください" >&2
        left=$((left + 1))
      else
        echo "loop-spawn: ★ worktree 撤去: ${wt}"
        n_wt=$((n_wt + 1))
      fi
    done <<EOF
${wts}
EOF
  fi

  # 同一 id の branch を 1 つずつ削除 (複数一致でも壊れない)
  # ⚠️ `-D` は使わない（★ 未 merge の作業を黙って捨てない。★ `abort_worktree` と同じ判断）。
  # ★ `--format` で取る —— ⚠️ `git branch --list` の素の出力は別 worktree が掴む枝に `+` を付ける。
  brs="$(git branch --list "loop/${id}" "loop/${id}-*" --format='%(refname:short)')"
  if [ -n "${brs}" ]; then
    while IFS= read -r b; do
      [ -n "${b}" ] || continue
      git branch -d "${b}" >/dev/null 2>&1 || true
      # ★ 削除できたかを **show-ref で**確かめてから書く。
      if git show-ref --verify --quiet "refs/heads/${b}"; then
        echo "loop-spawn: ⚠️ branch ${b} を削除できませんでした (未 merge か worktree が掴んでいる)" >&2
        echo "            ★ 内容を確認のうえ:  git branch -D ${b}" >&2
        left=$((left + 1))
      else
        echo "loop-spawn: ★ branch 撤去: ${b}"
        n_br=$((n_br + 1))
      fi
    done <<EOF
${brs}
EOF
  fi

  # ⚠️ 裸で置かない —— ★ ここで落ちると**残存 dir の網も最終報告も出ずに**終わる。
  git worktree prune || {
    echo "loop-spawn: ⚠️ git worktree prune に失敗しました" >&2
    left=$((left + 1))
  }

  # ★ 撤去しきれずに**ディレクトリが残っている**形（下方の `ディレクトリ … が残存` が die する状態）。
  #   ⚠️ **自動削除はしない** —— `rm -rf` は破壊的で、中に何が入っているか分からない。
  #   ★ ただし同じ id の再実行を殺すので、**「完了」とは書かない**（left に数える）。
  #   ⚠️★★★ **上のループで触ったものだけを除外する**（★ 「登録にあるなら除外」にしない）——
  #     ★ 一致規則が退行して worktree を拾えなくなったとき、**ここが最後の網**になる。
  #     ⚠️ 登録の有無で除外すると、拾えなかった worktree が黙って「完了」に化ける（＝ 起票 18 の再来）。
  #   ⚠️ **配置 `../wt/` に依存している**（★ Codex /cross-review 1 巡目）——
  #     ★ 下方の `wtdir="../wt/${repo_name}-${id}-${short}"` と**同じ前提**であり、
  #     ⚠️ 置き場を変えるときは**この網も一緒に変える**こと（★ 片方だけ動かすと網が空振りする）。
  for d in "../wt/${repo_name}-${id}" "../wt/${repo_name}-${id}-"*; do
    [ -d "${d}" ] || continue
    d_bn="$(basename "${d}")"
    # ★ 除外は **パス同定**で行う（⚠️ basename だと同名の別 worktree を黙って外す）。
    #   ★ `git -C … --show-toplevel` は **git の表記**を返すので `processed_path` と揃う
    #     (⚠️ bash の `pwd` は `/c/...` を返すので使えない)。
    d_top="$(git -C "${d}" rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -n "${d_top:-}" ] && contains_line "${processed_path}" "${d_top}"; then continue; fi
    if reg="$(registered_bn)" && contains_line "${reg}" "${d_bn}"; then
      echo "loop-spawn: ⚠️ worktree 登録に残っているのに id と結び付けられませんでした: ${d}" >&2
      echo "            ★ 手で:  git worktree remove --force \"${d}\"" >&2
    else
      echo "loop-spawn: ⚠️ worktree 登録に無いディレクトリが残存: ${d}" >&2
      echo "            ★ 中身を確認のうえ手で削除してください (★ 残ると同じ id の再実行が死にます)" >&2
    fi
    left=$((left + 1))
  done

  if [ "${left}" -gt 0 ]; then
    echo "loop-spawn: ⚠️ cleanup 未完了 issue ${id} — 撤去できなかったものが ${left} 件あります" >&2
    echo "            (★ 撤去できたのは worktree ${n_wt} 件 / branch ${n_br} 件)" >&2
    exit 1
  fi
  if [ "$((n_wt + n_br))" -eq 0 ]; then
    echo "loop-spawn: cleanup 対象なし issue ${id} (★ 既に撤去済み)"
  else
    echo "loop-spawn: cleanup 完了 issue ${id} (worktree ${n_wt} 件 / branch ${n_br} 件 を撤去)"
  fi
  exit 0
fi

id="${1:?issue-id を指定してください}"
short="${2:-issue}"
resolve_base                # ⚠️ コマンド置換にしない (★ die が抜けず、provenance も取れない)
base="$RESOLVED_BASE"
branch="loop/${id}-${short}"
wtdir="../wt/${repo_name}-${id}-${short}"

# --- dirty tree ハンドリング ---
if [ -n "$(git status --porcelain)" ]; then
  echo "loop-spawn: 作業ツリーに未コミット変更があります。worktree add は index を共有しません" >&2
  echo "            が、混乱を避けるため commit / stash を推奨します。続行するには LOOP_FORCE=1。" >&2
  [ "${LOOP_FORCE:-0}" = "1" ] || die "中断 (LOOP_FORCE=1 で強行可)"
fi

# --- stale worktree 検出 (basename 一致・空白入りパスに耐える) ---
# ⚠️★★★ `grep -q` をパイプの終端に置かない（★ 2026-09-21 に `--cleanup` 側で同じ形を直した）——
#   `set -o pipefail` 下では grep の早期終了が上流へ SIGPIPE を投げ、
#   ★ **一致したのに非 0** になりうる（＝ stale 検出が静かに反転し、同名 worktree を素通りさせる）。
#   → ★ `grep -c` で全部読ませ、件数で判定する。
target_bn="$(basename "$wtdir")"
stale_hits="$(git worktree list --porcelain \
  | awk -v bn="$target_bn" '/^worktree /{p=substr($0,10); gsub(/\\/,"/",p); n=split(p,seg,"/"); if (seg[n] == bn) c++} END{print c+0}')"
if [ "${stale_hits:-0}" -gt 0 ]; then
  die "同名 worktree が既に存在: $wtdir  (完了済みなら --cleanup $id を先に)"
fi
if [ -d "$wtdir" ]; then die "ディレクトリ $wtdir が残存。手動で確認/削除してください"; fi
if git show-ref --verify --quiet "refs/heads/$branch"; then
  die "ブランチ $branch が既存。--cleanup $id で撤去してから再実行"
fi
git worktree prune   # 消えたパスの登録を掃除

# --- base を remote と同期し、可能なら remote-tracking から分岐 (stale local base を避ける) ---
start="$base"
if git remote get-url origin >/dev/null 2>&1; then
  if git fetch --quiet origin "$base"; then
    start="origin/$base"          # fetch 成功時は最新の remote から分岐
  else
    echo "loop-spawn: fetch 失敗 (オフライン?) ローカル base で続行"
  fi
fi

# --- ⚠️★★★ 解決した base を「人が承認できる形」で出す (起票 23 の 2 つ目) ---
#   ★ 旧実装も `base=… (start=…)` を 1 行出していたが、⚠️ **stdout** に出していたため
#     `loop-run.sh:436` の `... 2>/dev/null | tail -1` が **パイプに吸わせて捨てていた**
#     (＝ **無人モードC では誰も読まない**)。
#   → ★ **stderr へ出す** (⚠️ `--no-exec` の「stdout の最終行 = worktree の絶対パス」を
#      構造的に壊さないため。`loop-worktree-deny.sh:37` と同じ作法)。
#   ★ あわせて **既定ブランチからの乖離**を出す —— ⚠️ 起票 23 の事故は
#     「pin 自体は表示されていたのに、それが 38 コミット前だと気づけなかった」形である。
{
  echo "loop-spawn: ── base の解決 ──────────────────────────────"
  # ⚠️★★★ **config 由来の値は `sanitize_disp` を通して出す。**
  #   ★ 生で出すと `\x1b[8m` (conceal) や `\r` で **この後に続く乖離の警告行を隠せる**
  #     (★ `security-checker` MEDIUM・2026-09-21 に実測)。→ ★ 詳細は sanitize_disp の注記。
  echo "loop-spawn:   base       = $(sanitize_disp "${base}")"
  echo "loop-spawn:   provenance = $(sanitize_disp "${RESOLVED_FROM}")"
  if [ -n "${cfg_task_name:-}" ]; then
    echo "loop-spawn:   config.task= $(sanitize_disp "${cfg_task_name}")"
  fi
  echo "loop-spawn:   start      = $(sanitize_disp "${start}")"
  _def="$(default_branch)"
  if [ -z "${_def:-}" ]; then
    echo "loop-spawn:   ⚠️ 既定ブランチを特定できないため乖離を出せません"
  elif [ "${_def#origin/}" = "${base}" ]; then
    # ⚠️ `origin/` を剥がして比べる (★ default_branch は remote-tracking を優先して返す)
    echo "loop-spawn:   乖離       = なし (★ base は既定ブランチ ${_def} そのもの)"
  else
    _cnt="$(git rev-list --left-right --count "${_def}...${start}" 2>/dev/null || true)"
    if [ -z "${_cnt:-}" ]; then
      echo "loop-spawn:   ⚠️ 既定 (${_def}) との乖離を数えられませんでした"
    else
      _behind="$(printf '%s' "${_cnt}" | awk '{print $1+0}')"
      _ahead="$(printf '%s' "${_cnt}" | awk '{print $2+0}')"
      if [ "${_behind}" -gt 0 ]; then
        echo "loop-spawn:   ⚠️★★★ 乖離  = 既定 (${_def}) より ${_behind} コミット後ろ / ${_ahead} コミット先"
        echo "loop-spawn:          ★ 意図した pin か確かめてください (⚠️ 起票 23: 古い pin が残っていた事故がある)"
      else
        echo "loop-spawn:   乖離       = 既定 (${_def}) より 0 コミット後ろ / ${_ahead} コミット先"
      fi
    fi
  fi
  echo "loop-spawn: ─────────────────────────────────────────────"
} >&2
echo "loop-spawn: base=$base (start=$start) → branch=$branch / worktree=$wtdir"
# ★ 撤去判定に使う「作成時の commit」を控えておく (★ abort_worktree の注記を参照)。
start_sha="$(git rev-parse --verify --quiet "$start" 2>/dev/null || true)"
git worktree add -b "$branch" "$wtdir" "$start"
cd "$wtdir"

# --- ⚠️★★★ 必須 `permissions.deny` の注入（★ worktree 作成直後・失敗したら使わせない） ---
#   ★ モードC (`loop-run.sh:275`) は worktree 生成を **このスクリプトへ委譲している**ので、
#     ここに 1 か所置けば **モードA（人が spawn）とモードC（無人）の両方**が通る。
#   ⚠️ 逆に `loop-run.sh` 側に置くと **モードA が素通りする**。
#   ⚠️★★★ 出力は **stderr** へ流す —— ★ `--no-exec` の
#     「**stdout の最終行 = worktree の絶対パス**」という契約 (`loop-run.sh:275` の `tail -1`) を壊さないため。
#   ⚠️ 失敗しても続行する経路は作らない (fail-closed)。理由は loop-worktree-deny.sh 冒頭。
#   ⚠️★★★ 失敗したら **worktree と branch ごと撤去する**（★ code-reviewer / security-checker
#     MEDIUM・2026-09-14）。★ 残すと (a) 人が手で `cd` して deny 無しで起動できてしまい、
#     (b) 同じ id の再実行が「同名 worktree が既に存在」で**恒久的に死ぬ**。
#     ★ 作りたてで中身が無いので、撤去して失うものは無い。
deny_script="${SCRIPT_DIR}/loop-worktree-deny.sh"
abort_worktree() { # abort_worktree <理由>
  local left_wt="" left_br="" tip=""
  cd "$repo_root" 2>/dev/null || true
  # ⚠️ 撤去できたかを**確かめてから**「撤去しました」と書く（★ Codex /cross-review 2 巡目）。
  git worktree remove --force "$wtdir" >/dev/null 2>&1 || left_wt="$wtdir"
  # ⚠️★★★ **`-D` を無条件で使わない**（★ Codex /cross-review 1 巡目 MEDIUM）。
  #   ★ ただし `-d` の merged 判定は **現在の HEAD 依存**なので、作業ブランチに居ると
  #     ⚠️ 空のブランチでも拒否されて残骸になる（★ Codex 2 巡目）。
  #   → ★ 判定を HEAD に依存させない: **作成時の commit から 1 mm も動いていないときだけ**消す。
  tip="$(git rev-parse --verify --quiet "refs/heads/$branch" 2>/dev/null || true)"
  if [ -n "$tip" ] && [ "$tip" = "${start_sha:-}" ]; then
    git branch -D "$branch" >/dev/null 2>&1 || left_br="$branch"
  elif [ -n "$tip" ]; then
    # ⚠️ 何かがコミットされている ＝ 作りたてではない。★ 消さずに残して人に渡す。
    left_br="$branch"
  fi
  git worktree prune >/dev/null 2>&1 || true
  die "$1
            ${left_wt:+⚠️ worktree ($left_wt) を撤去できませんでした。手で確認してください。}${left_wt:+
            }${left_wt:-★ worktree ($wtdir) は撤去しました。}
            ${left_br:+⚠️ branch $left_br は作成時から動いているため残しました (手で確認してください)。}
            ★ 原因を直してから再実行してください。
            (既存 worktree を手で点検するなら  bash scripts/loop-worktree-deny.sh --verify <worktree>)"
}
[ -f "${deny_script}" ] || abort_worktree "必須 deny の注入スクリプトが見つかりません: ${deny_script}"
bash "${deny_script}" "$(pwd)" >&2 \
  || abort_worktree "worktree への必須 deny 注入に失敗しました。★ deny 無しの worktree は渡しません。"

echo "loop-spawn: worktree 準備完了。"

# --no-exec / NO_EXEC: worktree を作るだけで Claude を起動しない (モードC の loop-run.sh から再利用する)。
# worktree の絶対パスを stdout に 1 行だけ出す (呼び出し側が読む契約)。
if [ "${LOOP_NO_EXEC:-0}" = "1" ] || [ "${NO_EXEC:-0}" = "1" ]; then
  pwd
  exit 0
fi

echo "loop-spawn: Claude を起動します → /loop-issue $id を実行してください"
# Windows(Git Bash) では claude が .cmd/.ps1 shim のことがあり exec が滑る。見つからなければ手順を案内。
if command -v claude >/dev/null 2>&1; then
  exec claude
else
  echo "loop-spawn: 'claude' が PATH に見つかりません。手動で:  cd \"$wtdir\" && claude"
  exit 0
fi
