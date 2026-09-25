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
  # ⚠️ **削除ではなく `?` へ置換する** (★ Codex `/cross-review` 2 巡目・2026-09-21)。
  #   ★ 削除すると `ab<CR>cd` が `abcd` に見え、⚠️ **何かがあったこと自体が消える**。
  #   ★ 目的は「表示を崩さないこと」であって「痕跡を消すこと」ではないので、
  #     **位置と個数を残す**方が事故調査に強い。
  printf '%s' "$1" | LC_ALL=C tr '\000-\037\177' '?' | cut -c1-200
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

# validate_name <label> <value>
#   ⚠️★★★ 起票 A: 旧実装は `--cleanup` 経路にしか id 検証が無く、spawn 経路 (id / short) は
#     無検証で `branch=` / `wtdir=` へ直接埋め込んでいた。→ ★ 検証本体をここに括り出し、
#     cleanup の id・spawn の id・spawn の short の **3 か所**から呼ぶ (振る舞いは元の
#     --cleanup の case と同一。`label` だけ呼び出し元で変える)。
validate_name() {
  local label="$1" v="$2"
  # ⚠️★★★ LOW (レビュー): die メッセージの値は `sanitize_disp` を通す。
  #   ★ 生で出すと端末への制御シーケンス注入 (`sanitize_disp` の注記と同じ経路) を許す。
  case "${v}" in
    -*) die "${label} が '-' 始まりです: [$(sanitize_disp "${v}")]" ;;
    *[!A-Za-z0-9._-]*) die "${label} に使えない文字が入っています (英数字 . _ - のみ): [$(sanitize_disp "${v}")]" ;;
    # ★ `.` / `..` / `a..b` は上を通るが、ref としても名前としても紛らわしい (⚠️ Codex /cross-review 1 巡目)。
    #   ★ パス脱出は起きない (`<repo>-..` は 1 つの名前であって親ディレクトリではない) が、通す意味も無い。
    .|..|*..*) die "${label} にドットの連なりは使えません: [$(sanitize_disp "${v}")]" ;;
  esac
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
  # ★ 起票 A: 検証本体は共通関数 validate_name に括り出した (spawn 経路の id / short もここを通る)。
  validate_name "issue-id" "${id}"
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
# ★ 起票 A: --cleanup 経路にしか無かった検証を spawn 経路 (id / short) にも適用する。
validate_name "issue-id" "${id}"
validate_name "short-slug" "${short}"
resolve_base                # ⚠️ コマンド置換にしない (★ die が抜けず、provenance も取れない)
base="$RESOLVED_BASE"
branch="loop/${id}-${short}"
wtdir="../wt/${repo_name}-${id}-${short}"

# --- ⚠️★★★ P1-K: spawn を直列化する mkdir ロック (git-bash に flock が無い前提) ---
#   ★ 根本原因 (design.md P1-K 表): `git worktree add -b` は upstream 設定で `.git/config` を
#     書くため、2 本同時だと git 自身の内部ロックで片方が落ち、`set -e` で
#     **ブランチだけ作られた状態で die** し、片づけないまま終わっていた。
#     → ★ 原因 (同時実行) そのものを mkdir ロックで消す。
#   ★ `git rev-parse --git-common-dir` は全 worktree が共有する 1 か所を指す
#     (⚠️ worktree ごとに別内容を持つ `.git` ファイルの場所ではない)。
# ⚠️★★★ LOW (レビュー): `git rev-parse --git-common-dir` は cwd 相対 (例: `.git`) を返しうる。
#   ★ 相対のままだと、後段で `cd` を跨いだ時にロックが指す先がずれかねない。
#   → ★ `cd … && pwd` で絶対化する (⚠️ この時点では既に repo_root に cd 済み)。
_git_common_dir="$(git rev-parse --git-common-dir)" || die "git-common-dir を解決できませんでした"
# ⚠️★★★ LOW (Codex /cross-review): `cd "$dir" && pwd` は CDPATH の影響を受ける
#   (★ CDPATH に相対パスの一致先があると、意図しないディレクトリへ `cd` しうる)。
#   → ★ `CDPATH=` で無効化し、`cd -P` / `pwd -P` でシンボリックリンクも解決した物理パスに揃える。
_git_common_dir_abs="$(CDPATH= cd -P -- "${_git_common_dir}" && pwd -P)" \
  || die "git-common-dir (${_git_common_dir}) を絶対パスにできませんでした"
LOCK="${_git_common_dir_abs}/loop-spawn.lock"
LOCK_HELD=0
REAP_HELD=0   # ★ 判断 9 (C-M1/C-M2 の後始末): stale 除去用ロック (${LOCK}.reap) を自分が保持しているか
# ⚠️ テストでは待ち間隔・上限を短縮できるよう env で上書き可能にする (★ 既定は本番相当)。
LOCK_POLL="${LOOP_SPAWN_LOCK_POLL:-0.5}"
LOCK_TIMEOUT="${LOOP_SPAWN_LOCK_TIMEOUT:-120}"
# ⚠️★★★ LOW (レビュー): POLL=0 だと下の `acquire_spawn_lock` 内の `awk` (`n=t/p`) が
#   0 除算になり、`set -e` 下でコマンド置換の失敗が **メッセージ無しにスクリプトを終わらせる**。
#   → ★ 正の数値であることを case (文字種) + awk (符号) の 2 段で検証してから使う。
case "${LOCK_POLL}" in
  ''|.|*[!0-9.]*|*.*.*) die "LOOP_SPAWN_LOCK_POLL が数値ではありません: [$(sanitize_disp "${LOCK_POLL}")]" ;;
esac
awk -v p="${LOCK_POLL}" 'BEGIN{ exit !(p+0 > 0) }' \
  || die "LOOP_SPAWN_LOCK_POLL は 0 より大きい数値にしてください: [$(sanitize_disp "${LOCK_POLL}")]"
case "${LOCK_TIMEOUT}" in
  ''|.|*[!0-9.]*|*.*.*) die "LOOP_SPAWN_LOCK_TIMEOUT が数値ではありません: [$(sanitize_disp "${LOCK_TIMEOUT}")]" ;;
esac
awk -v t="${LOCK_TIMEOUT}" 'BEGIN{ exit !(t+0 > 0) }' \
  || die "LOOP_SPAWN_LOCK_TIMEOUT は 0 より大きい数値にしてください: [$(sanitize_disp "${LOCK_TIMEOUT}")]"

release_spawn_lock() {
  # ⚠️★★★ 判断 9 (C-M1/C-M2 の後始末): reap 用ロックが自分の手に残っていれば先に片づける
  #   (★ mkdir "${LOCK}.reap" と rmdir "${LOCK}.reap" の間で中断されると残骸になる —— ここが最後の網)。
  if [ "${REAP_HELD}" -eq 1 ]; then
    rmdir "${LOCK}.reap" 2>/dev/null || true
    REAP_HELD=0
  fi
  if [ "${LOCK_HELD}" -eq 1 ]; then
    # ⚠️★★★ レビュー指摘: 解放前に「いま ${LOCK} を掴んでいるのは自分か」を確かめる。
    #   ★ 確かめずに rm -rf すると、何らかの理由で自分のロックが既に消え、別プロセスが
    #     同じパスへ新しいロックを作っていた場合に **他人のロックを消してしまう**
    #     (＝ 直列化そのものが壊れる)。★ pid が読めない/一致しないときは **消さずに** WARN する。
    local held_pid
    held_pid="$(cat "${LOCK}/pid" 2>/dev/null || true)"
    if [ "${held_pid:-}" = "$$" ]; then
      rm -rf "${LOCK}" 2>/dev/null || true
    else
      echo "loop-spawn: ⚠️ ロック (${LOCK}) の pid ([$(sanitize_disp "${held_pid:-空}")]) が自分 ($$) と一致しないため解放しません" >&2
      echo "            ★ 手で確認:  cat \"${LOCK}/pid\"" >&2
    fi
    LOCK_HELD=0
  fi
}
# ⚠️★★★ 異常終了 (set -e による die を含む) でも解放する保険。
#   ★ ただし **正常系では `git worktree add` の直後に明示解放する** (下記) —— ⚠️ `exec claude` は
#     プロセスを置き換えるだけで「シェルの終了」ではないため、EXIT trap が exec 前に
#     必ず走るとは限らない。だから **明示解放が本筋、trap は異常系の保険**。
#   ⚠️★★★ 判断 9 (Codex P1): `git worktree add` 失敗時は **この trap まで解放しない**
#     (★ 下の `abort_worktree` 呼び出し部を参照。失敗直後の明示解放をやめ、後始末が
#     終わって `die` が exit するまでロックを保持する)。
trap release_spawn_lock EXIT

# acquire_spawn_lock → ★ mkdir で排他を取る。stale (pid が死んでいる) なら別ロックで直列化して除去し取り直す。
#   ⚠️ pid ファイルが無い/読めない (作成直後の競合) ときは stale と見なさない (待つ側に倒す)。
acquire_spawn_lock() {
  local i=0 max_i lock_pid reap_pid
  # ⚠️ bash 3.2 に浮動小数演算は無いので、待ち回数は awk で整数化する (sleep 自体は小数を受ける)。
  max_i="$(awk -v t="${LOCK_TIMEOUT}" -v p="${LOCK_POLL}" \
    'BEGIN{n=t/p; i=int(n); if (n>i) i++; if (i<1) i=1; print i}')"
  # ⚠️★★★ レビュー指摘 (巨大な TIMEOUT): `max_i` が `1e+20` のような指数表記や桁あふれになると、
  #   下の `[ "${i}" -gt "${max_i}" ]` が非数値比較エラーを起こして **常に偽** になり、
  #   ⚠️ タイムアウトが無効化されて無限に待ち続ける (die しない)。
  #   → ★ `max_i` が数字だけ・9 桁以下であることを要求する (⚠️ 黙って進まない)。
  case "${max_i}" in
    ''|*[!0-9]*)
      die "待ち回数を計算できませんでした (max_i=[$(sanitize_disp "${max_i}")])。
            LOOP_SPAWN_LOCK_TIMEOUT / LOOP_SPAWN_LOCK_POLL の値を確認してください。" ;;
  esac
  if [ "${#max_i}" -gt 9 ]; then
    die "LOOP_SPAWN_LOCK_TIMEOUT (${LOCK_TIMEOUT}) / LOOP_SPAWN_LOCK_POLL (${LOCK_POLL}) から計算した
          待ち回数が大きすぎます (max_i=${max_i})。
          ⚠️ このまま進めると数値比較が壊れてタイムアウトが効かなくなるため、判定せず止まります。"
  fi
  while ! mkdir "${LOCK}" 2>/dev/null; do
    if [ -f "${LOCK}/pid" ]; then
      lock_pid="$(cat "${LOCK}/pid" 2>/dev/null || true)"
      case "${lock_pid:-}" in
        '') : ;;              # ⚠️ 読めない (作成直後の競合) → stale と見なさない
        *[!0-9]*) : ;;        # ⚠️ 壊れた pid → stale と見なさない
        *)
          if ! kill -0 "${lock_pid}" 2>/dev/null; then
            # ⚠️★★★ C-M2 (レビュー): stale 除去に TOCTOU がある —— 待ち手 A と B が同じ死んだ pid を
            #   読み、A が除去して取り直した直後に B が **古い判断のまま** A の新しいロックを消しうる
            #   (＝ 2 本が同時にクリティカルセクションへ入る)。
            #   → ★ 除去そのものを別ロック "${LOCK}.reap" (mkdir) で直列化する。reap を取れた者だけが、
            #     その中で pid を **読み直し**、読み直した pid が「死んでいると判断した pid」と
            #     同じで、なお kill -0 が失敗するときに限り rm -rf する。
            #   ⚠️ reap を取れなければここでは何もしない (★ 下の i 加算 / sleep で普通に待つ)。
            if mkdir "${LOCK}.reap" 2>/dev/null; then
              # ⚠️★★★ 判断 9 (C-M1/C-M2 の後始末): ここから rmdir までの間に中断されると
              #   `${LOCK}.reap` が残骸になる。★ フラグを立てておき、EXIT trap
              #   (`release_spawn_lock`) にも同じ後始末をさせる (＝ 中断されても最後の網が効く)。
              REAP_HELD=1
              reap_pid="$(cat "${LOCK}/pid" 2>/dev/null || true)"
              if [ "${reap_pid:-}" = "${lock_pid}" ] && ! kill -0 "${lock_pid}" 2>/dev/null; then
                rm -rf "${LOCK}" 2>/dev/null || true
              fi
              # ⚠️★★★ reap は必ず解放する。★ 取った側がこの中で死ぬと reap の残骸が残り、
              #   以後の stale 除去ができなくなる (許容する —— 待ち切れば die し、
              #   die メッセージで reap ディレクトリの手動削除を案内する。
              #   ⚠️ ★ ここで中断されても EXIT trap が REAP_HELD を見て後始末する)。
              rmdir "${LOCK}.reap" 2>/dev/null && REAP_HELD=0
            fi
          fi
          ;;
      esac
    fi
    # ⚠️★★★ C-M1 (レビュー): 除去を試みた周も **必ず** ここまで来て i を進め sleep する。
    #   ★ 旧実装は stale 分岐で `continue` しており、rm が失敗し続けると (Windows のハンドル保持等)
    #   タイムアウトが一切効かないまま CPU を回し続けた。
    i=$((i + 1))
    if [ "${i}" -gt "${max_i}" ]; then
      die "loop-spawn.lock を ${LOCK_TIMEOUT} 秒待っても取得できませんでした: ${LOCK}
            ⚠️ 他の loop-spawn.sh が動いていないか確認してください。
            ★ 完全に止まっているなら手で削除:  rmdir \"${LOCK}\"
            ⚠️ stale 除去用ロック ${LOCK}.reap が残っている場合は、そちらも手で削除してください:  rmdir \"${LOCK}.reap\""
    fi
    sleep "${LOCK_POLL}"
  done
  printf '%s' "$$" > "${LOCK}/pid" 2>/dev/null || true
  LOCK_HELD=1
}

# --- abort_worktree はここで定義する (★ P1-K で `git worktree add` 失敗時にも使うため) ---
#   ★ 元は下段の deny 注入失敗時だけの後始末だったが、`git worktree add` 自体の失敗
#     (根本原因: 同時実行によるブランチだけ残る事故) にも同じ規則を適用する。
#   ⚠️ 関数本体は呼び出し時まで評価されないので、`$branch` / `$wtdir` / `$start_sha` が
#     まだ代入されていないこの位置で定義してよい。
#   ⚠️★★★ 撤去できたことを確かめてから「完了」と書く（★ 起票 18・2026-09-20 の実測で発見）。
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

# --- dirty tree ハンドリング ---
if [ -n "$(git status --porcelain)" ]; then
  echo "loop-spawn: 作業ツリーに未コミット変更があります。worktree add は index を共有しません" >&2
  echo "            が、混乱を避けるため commit / stash を推奨します。続行するには LOOP_FORCE=1。" >&2
  [ "${LOOP_FORCE:-0}" = "1" ] || die "中断 (LOOP_FORCE=1 で強行可)"
fi

# --- ⚠️★★★ P1-K: ここから `git worktree add` 完了までロックで直列化する ---
#   ★ stale 検出 (ロックの pid が死んでいないか) 〜 `git worktree add` までを囲む。
acquire_spawn_lock

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

# local_ref_or_raw <base> → ★ ローカルに <base> というブランチがあれば `refs/heads/<base>`、
#   無ければ <base> のまま (⚠️ 従来どおりの無修飾値。ローカルに無い形まで書き換えない)。
#   ⚠️★★★ 判断 9/10 (Codex /cross-review LOW): 無修飾の `$base` は同名の tag があると
#     `git worktree add` が `fatal: ambiguous object name` で落ちる (12g で local-ahead 側は実測済み)。
#     fetch 失敗・origin 無しの経路も同じ危険を持つので、ここに括り出して両方から呼ぶ。
local_ref_or_raw() {
  if git show-ref --verify --quiet "refs/heads/$1"; then
    printf 'refs/heads/%s' "$1"
  else
    printf '%s' "$1"
  fi
}

# --- ⚠️★★★ P1-J: base を remote と同期し、祖先関係で start を決める (判断 3) ---
#   ★ 旧実装は fetch 成功なら**無条件で** `origin/$base` を採用しており、ローカル $base が
#     先行していても無視していた (design.md P1-J の根本原因)。
#   ★ 判定表 (decisions.md 判断 3):
#     一致       → refs/remotes/origin/$base
#     ローカル先行 (origin が ローカルの祖先) → refs/heads/$base (ローカル) ＋ 未 push 件数の WARN
#     ローカル遅れ (ローカルが origin の祖先) → refs/remotes/origin/$base (現行どおり)
#     分岐 (どちらでもない)                  → **die** (worktree も branch も作る前に)
#     ローカルに $base が無い                 → refs/remotes/origin/$base (現行どおり)
#   ⚠️★★★ 判断 9/10 (Codex /cross-review LOW): 旧実装は上記のうち **local-ahead だけ**
#     `refs/heads/$base` で修飾しており、他 (equal / local-behind / no-local) は
#     短縮形 `origin/$base` のまま、fetch 失敗・origin 無しは無修飾 `$base` のままだった。
#     → ★ remote 側は `refs/remotes/origin/$base`、ローカル側は `refs/heads/$base`
#       (ローカルに無いときは `local_ref_or_raw` が従来どおりの値を返す) に揃える。
start="$(local_ref_or_raw "$base")"
start_choice=""      # ★ 値は equal|local-ahead|local-behind|no-local|fetch-failed のいずれか
start_ahead_n=""
if git remote get-url origin >/dev/null 2>&1; then
  if git fetch --quiet origin "$base"; then
    if ! git show-ref --verify --quiet "refs/heads/$base"; then
      start="refs/remotes/origin/$base"; start_choice="no-local"
    else
      local_sha="$(git rev-parse --verify --quiet "refs/heads/$base" 2>/dev/null || true)"
      origin_sha="$(git rev-parse --verify --quiet "refs/remotes/origin/$base" 2>/dev/null || true)"
      # ⚠️★★★ LOW (レビュー): fetch は成功したのに origin_sha が読めないのは **分岐とは別の異常**
      #   (参照の破損など)。「分岐」の die に混ぜると誤診断を招くので専用メッセージで止める。
      if [ -z "${origin_sha:-}" ]; then
        die "fetch は成功したのに refs/remotes/origin/$base の sha を解決できませんでした
              ⚠️ 分岐とは別の異常です。fail-closed のため worktree も branch も作らずに止まります。
              ★ 手で確認:  git -C ${repo_root} rev-parse refs/remotes/origin/${base}"
      fi
      if [ -n "${local_sha:-}" ] && [ "${local_sha}" = "${origin_sha}" ]; then
        start="refs/remotes/origin/$base"; start_choice="equal"
      else
        # ⚠️★★★ LOW (レビュー): `git merge-base --is-ancestor` の rc は 0=祖先 / 1=祖先でない /
        #   128=異常終了 (shallow clone 等で判定不能) の 3 通り。「分岐」(＝両方 1) と
        #   rc 128 (＝判定できていない) を同じ die にしない (⚠️ `set -e` 下で直接 rc を読むため
        #   `cmd || rc=$?` の形にする —— bare command を書くと非 0 でスクリプトごと落ちる)。
        ahead_rc=0
        git merge-base --is-ancestor "refs/remotes/origin/$base" "refs/heads/$base" 2>/dev/null || ahead_rc=$?
        if [ "${ahead_rc}" -eq 0 ]; then
          # ★ origin が ローカルの祖先 ＝ ローカルが先行している。
          # ⚠️★★★ `refs/heads/` で修飾する (★ 2026-09-26 メインのレビュー)。
          #   ★ 無修飾の `$base` は、同名の tag があると `git worktree add` が
          #     `fatal: ambiguous object name` で落ちる (12g で実測)。この経路は P1-J で新設したもの。
          start="refs/heads/$base"; start_choice="local-ahead"
          start_ahead_n="$(git rev-list --count "refs/remotes/origin/${base}..refs/heads/${base}" 2>/dev/null || true)"
        elif [ "${ahead_rc}" -eq 128 ]; then
          die "merge-base --is-ancestor が異常終了しました (rc=128・shallow clone 等の可能性): refs/remotes/origin/${base} → refs/heads/${base}
                ⚠️ 「祖先でない」(rc 1・分岐の可能性) とは区別します。fail-closed のため worktree も branch も作らずに止まります。
                ★ 手で確認:  git -C ${repo_root} merge-base --is-ancestor refs/remotes/origin/${base} refs/heads/${base}; echo \$?"
        else
          behind_rc=0
          git merge-base --is-ancestor "refs/heads/$base" "refs/remotes/origin/$base" 2>/dev/null || behind_rc=$?
          if [ "${behind_rc}" -eq 0 ]; then
            # ★ ローカルが origin の祖先 ＝ ローカルが遅れている (stale local base)。
            start="refs/remotes/origin/$base"; start_choice="local-behind"
          elif [ "${behind_rc}" -eq 128 ]; then
            die "merge-base --is-ancestor が異常終了しました (rc=128・shallow clone 等の可能性): refs/heads/${base} → refs/remotes/origin/${base}
                  ⚠️ 「祖先でない」(rc 1・分岐の可能性) とは区別します。fail-closed のため worktree も branch も作らずに止まります。
                  ★ 手で確認:  git -C ${repo_root} merge-base --is-ancestor refs/heads/${base} refs/remotes/origin/${base}; echo \$?"
          else
            # ⚠️★★★ 分岐: どちらが正しいか自動で決められない → fail-closed。
            #   ★ worktree も branch もまだ何も作っていない時点で止める。
            die "base '$base' はローカルと origin で分岐しています (ローカル=${local_sha:-?} / origin=${origin_sha})
                  ⚠️ どちらが正しいか自動で決められないため、worktree も branch も作らずに止まります (判断 3・fail-closed)。
                  ★ 手で解決してから再実行してください (例:  git -C ${repo_root} pull --ff-only origin ${base})。"
          fi
        fi
      fi
    fi
  else
    start="$(local_ref_or_raw "$base")"
    start_choice="fetch-failed"
    # ⚠️ 他の診断行と同じく stderr へ (★ 旧実装は stdout に出ており、`--no-exec` の
    #   「stdout の最終行 = worktree の絶対パス」契約は壊さないが、診断の置き場が不揃いだった)。
    echo "loop-spawn: fetch 失敗 (オフライン?) ローカル base で続行" >&2
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
  # ⚠️★★★ P1-J: 別 subagent (loop-run.sh 側) がこの行を `start-choice = local-ahead` で
  #   grep するので、綴りを変えない (契約は decisions.md 判断 3 / design.md P1-J)。
  if [ -n "${start_choice:-}" ]; then
    echo "loop-spawn:   start-choice = ${start_choice}"
    if [ "${start_choice}" = "local-ahead" ]; then
      echo "loop-spawn:     ⚠️ 未 push の ${start_ahead_n:-?} コミットを含む worktree になります"
    fi
  fi
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
# ⚠️★★★ P1-K: `set -e` に落とし込んで die しない —— ★ ここで `set -e` に死なせると
#   `abort_worktree` を経由せずブランチだけが残るケース (根本原因) を直せない。
if ! git worktree add -b "$branch" "$wtdir" "$start"; then
  # ⚠️★★★ 判断 9 (Codex P1): **ここで明示解放しない。**
  #   ★ 旧実装はここで release_spawn_lock してから abort_worktree していたため、
  #     ロックを放した直後に**並行する別 spawn**が同じ id/short の worktree を作ってしまい、
  #     abort_worktree の `remove --force` / `branch -D` がその**他人の worktree/branch**を
  #     消しうる (＝ 直列化の意味が失われる)。
  #   → ★ 後始末 (abort_worktree) が終わって die が exit するまでロックを保持し続け、
  #     EXIT trap (`release_spawn_lock`) に解放させる。
  abort_worktree "git worktree add に失敗しました: branch=$branch / worktree=$wtdir / start=$start"
fi
# ★ 成功時のみ、ここで明示的に解放する (⚠️ `exec claude` の前に必ず解放済みにする契約)。
release_spawn_lock
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
#   ⚠️ `abort_worktree` はここでは定義しない —— P1-K で `git worktree add` 失敗時にも使うため、
#     より前方 (id/short/base/branch/wtdir の直後) で定義している。
deny_script="${SCRIPT_DIR}/loop-worktree-deny.sh"
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
