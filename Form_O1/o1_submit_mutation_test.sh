#!/usr/bin/env bash
# ★ `o1_submit_guard_test.cjs` が **空回りしていない**ことを測る（変異テスト）。
#
# ⚠️★★★ なぜ要るか: 「全ケース OK」は、**検査が何も見ていなくても**出る。
#   ★ ガードを 1 つずつ壊して**赤になるか**を確かめるまで、緑に意味は無い
#     (`verify-before-claiming` ルール 5b)。
# ⚠️★★ **変異は 1 箇所ずつ**入れる（複数を同時に壊して赤 = 片方しか証明できていない・
#   memory `measurement-instrument-false-positives`）。
#
# ★ 本物の `GSE_O1_Submit.gs` は 1 バイトも変更しない（一時ディレクトリで壊す）。
#
# 使い方: bash Form_O1/o1_submit_mutation_test.sh
# 終了コード: 0 = 全変異が赤になった / 1 = 赤にならない変異がある（★ 検査の穴）

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SRC="Form_O1/GSE_O1_Submit.gs"
TEST="Form_O1/o1_submit_guard_test.cjs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
SEEN_HASHES=""

# ⚠️★★★ **`node "$TEST" "$f"` にはタイムアウトを掛ける**（2026-09-27 3 回目レビュー指摘の教訓）。
#   ★ 「無限ループを再導入する変異」を検知したいテスト自体が、変異を当てた瞬間に**本当に無限ループする**
#   （= 本ハーネスが固まる）。★ `timeout`/`gtimeout` は macOS 標準に無い（memory
#   `macos-default-tools-break-gates`）ので、bash 標準機能だけで書く。
run_with_timeout_ () { # $1 = 秒 / $2.. = コマンド
  local secs="$1"; shift
  "$@" & local pid=$!
  local i=0
  local limit=$((secs * 20))
  while kill -0 "$pid" 2> /dev/null; do
    sleep 0.05
    i=$((i + 1))
    if [ "$i" -ge "$limit" ]; then
      kill -9 "$pid" 2> /dev/null
      wait "$pid" 2> /dev/null
      return 124
    fi
  done
  wait "$pid"
}

# ★ 先に「壊していない本物」で緑になることを確かめる（⚠️ 最初から赤なら、以下の赤は全部無意味）。
if ! node "$TEST" "$SRC" > /dev/null 2>&1; then
  echo "❌ 壊していない本物のソースで、すでにテストが赤い。変異テストの前提が崩れている。"
  exit 1
fi

# 変異を 1 つ適用して、テストが**赤になる**ことを確かめる。
# $1 = 変異の名前 / $2.. = 一時コピーに対して走らせる perl の式
mutate () {
  local name="$1"; shift
  local f="$TMP/mutant.gs"
  cp "$SRC" "$f"
  perl -0777 -i -pe "$@" "$f" || { echo "  ⚠️ 変異を適用できません: $name"; FAIL=$((FAIL+1)); return; }
  if cmp -s "$SRC" "$f"; then
    # ⚠️★ 変異が当たっていない（置換対象が消えた等）。★ **緑にしない。**
    echo "  ❌ 変異が当たらなかった（置換対象が消えた？）: $name"
    FAIL=$((FAIL+1))
    return
  fi
  # ⚠️★★★ 別の変異と byte 同一なら、どこかの置換が当たっていない。
  local h
  h=$(cksum < "$f" | tr -d ' ')
  case " $SEEN_HASHES " in
    *" $h "*)
      echo "  ❌ 別の変異と同じ結果になった（★ 置換のどれかが当たっていない）: $name"
      FAIL=$((FAIL+1))
      return
      ;;
  esac
  SEEN_HASHES="$SEEN_HASHES $h"
  # ⚠️ 構文エラーで赤になった変異は「ガードが止めた」のではない → 構文が通ることを先に確かめる。
  if ! node -e "new (require('vm').Script)(require('fs').readFileSync('$f','utf8'))" 2> /dev/null; then
    echo "  ❌ 変異が構文エラー（★ 赤になっても意味が無い）: $name"
    FAIL=$((FAIL+1))
    return
  fi
  local rc
  run_with_timeout_ 10 node "$TEST" "$f" > /dev/null 2>&1
  rc=$?
  if [ "$rc" -eq 124 ]; then
    echo "  ⚠️★★★ 変異がハングした（10 秒でも終わらない・無限ループの疑い）: $name"
    echo "     ★ ハングも「壊れた」の一種として扱う（検知できているので緑）。"
    PASS=$((PASS+1))
    return
  fi
  if [ "$rc" -eq 0 ]; then
    echo "  ❌ 壊しても緑のまま（★ 検査の穴）: $name"
    FAIL=$((FAIL+1))
  else
    echo "  ✅ 壊すと赤になる: $name"
    PASS=$((PASS+1))
    # ★ VERBOSE=1 のとき、**どの検査で赤になったか**を出す（⚠️ 例外で落ちただけの赤は「ガードが止めた」証拠にならない）。
    if [ "${VERBOSE:-0}" = "1" ]; then
      node "$TEST" "$f" 2>&1 | grep -E '^NG |Error' | head -2 | cut -c1-150 | sed 's/^/       ↳ /'
    fi
  fi
}

echo "=== 変異テスト: ガードを 1 つずつ壊して赤になるか ==="

# --- V-3 P-ID ごとのサブフォルダ（2026-09-28） ---------------------------------
mutate "保存先: 直下に戻す（P-ID フォルダを使わない）" \
  's/var folder = pidFolder_\(root, pidOfName_\(name\)\);/var folder = root;/'
mutate "P-ID: 先頭でなく 2 番目の要素を取る" \
  "s/return name\.split\('_'\)\[0\];/return name.split('_')[1];/"
mutate "同名フォルダ: 最古でなく最新を使う" \
  's/getTime\(\) < oldest\.getDateCreated/getTime() > oldest.getDateCreated/'
mutate "同名フォルダ: ごみ箱のフォルダも使う" \
  's/      if \(f\.isTrashed\(\)\) continue;\n//'
mutate "同名フォルダ: 名前の完全一致を確かめない" \
  's/      if \(f\.getName\(\) !== pid\) continue;\n//'
mutate "同名フォルダ: 既存を探さず毎回作る" \
  's/return oldest \|\| root\.createFolder\(pid\);/return root.createFolder(pid);/'
mutate "ロック: 取れなくても続ける" \
  's/if \(!lock\.tryLock\(PID_FOLDER_LOCK_MS\)\) return null;/lock.tryLock(PID_FOLDER_LOCK_MS);/'
mutate "ロック: 返さない" \
  's/    lock\.releaseLock\(\);\n//'
mutate "ロック: finally でなく正常系でだけ返す（例外でロックが残る）" \
  's/    return oldest \|\| root\.createFolder\(pid\);\n  \} finally \{\n    lock\.releaseLock\(\);\n  \}/    var r = oldest || root.createFolder(pid);\n    lock.releaseLock();\n    return r;\n  } finally {\n  }/'
mutate "ロック: 検索・作成の前に返す（直列化していない）" \
  's/  try \{\n    var it = root\.getFoldersByName\(pid\);/  lock.releaseLock();\n  try {\n    var it = root.getFoldersByName(pid);/'
mutate "ロック失敗: busy を返さず保存する" \
  's/return json_\(\{ ok: false, error: .busy. \}\);/folder = root;/'

# --- 既存のガード（代表） -------------------------------------------------------
mutate "名前: G1 の _block 形も通す" \
  's/_o1day\\d\{2,3\}_gse_o1_/_(?:o1day|block)\\d{2,3}_gse_(?:o1_)?/'
mutate "重複: 同名でも別名にしない（同じ名前で足す）" \
  's/if \(duplicateName\) \{/if (false) {/'
mutate "上限: MAX_BYTES の検査を外す" \
  's/if \(decodedLength_\(b64\) > MAX_BYTES\) \{/if (false) {/'
mutate "秘密: 照合を常に通す" \
  's/return diff === 0;/return true;/'

echo
echo "壊すと赤: $PASS / 穴: $FAIL"
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 赤にならない変異がある（★ 検査の穴）。上の ❌ を埋めること。"
  exit 1
fi
echo "✅ 全変異が赤になった"
exit 0
