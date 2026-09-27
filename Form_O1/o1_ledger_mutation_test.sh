#!/usr/bin/env bash
# ★ `o1_ledger_test.cjs` が **空回りしていない**ことを測る（変異テスト）。
#
# ⚠️★★★ なぜ要るか: 「116 ケース全部 OK」は、**検査が何も見ていなくても**出る。
#   ★ ガードを 1 つずつ壊して**赤になるか**を確かめるまで、緑に意味は無い
#     (`verify-before-claiming` ルール 5b)。
# ⚠️★★ **変異は 1 箇所ずつ**入れる（複数を同時に壊して赤 = 片方しか証明できていない・
#   memory `measurement-instrument-false-positives`）。
#
# ★ 本物の `GSE_O1_Ledger.gs` は 1 バイトも変更しない（一時ディレクトリで壊す）。
#
# 使い方: bash Form_O1/o1_ledger_mutation_test.sh
# 終了コード: 0 = 全変異が赤になった / 1 = 赤にならない変異がある（★ 検査の穴）

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SRC="Form_O1/GSE_O1_Ledger.gs"
TEST="Form_O1/o1_ledger_test.cjs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
SEEN_HASHES=""

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
  if node "$TEST" "$f" > /dev/null 2>&1; then
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

# --- §1 名前の読み取り --------------------------------------------------------
mutate "名前: _dup- を読まない" \
  's/\(_dup-\\d\{1,15\}\)\?//'
mutate "名前: 末尾の \$ を外す（.age.exe を通す）" \
  's/\(\?:_\\d\{1,10\}\)\?\(_dup-\\d\{1,15\}\)\?\\\.age\$\//(?:_\\d{1,10})?(_dup-\\d{1,15})?\\.age\//'
mutate "名前: P-ID の上限を 17 にする" \
  's/\(\[A-Za-z0-9\]\{1,16\}\)_o1day/([A-Za-z0-9]{1,17})_o1day/'
mutate "名前: 日番号を 1 桁も通す" \
  's/_o1day\(\\d\{2,3\}\)/_o1day(\\d{1,3})/'

# --- §2 判定 --------------------------------------------------------------------
mutate "途絶の日数を 6 にする" \
  's/var O1_LEDGER_STALE_DAYS = 5;/var O1_LEDGER_STALE_DAYS = 6;/'
mutate "途絶の境界を > にする（ちょうど 5 日を見逃す）" \
  's/nowMs - last >= O1_LEDGER_STALE_DAYS/nowMs - last > O1_LEDGER_STALE_DAYS/'
mutate "欠番の猶予を 4 日にする" \
  's/var O1_LEDGER_GAP_DAYS = 5;/var O1_LEDGER_GAP_DAYS = 4;/'
mutate "欠番の猶予を外す（届いた直後でも欠番にする）" \
  's/minLater !== null && nowMs - minLater >= O1_LEDGER_GAP_DAYS \* O1_LEDGER_DAY_MS/minLater !== null/'
mutate "欠番: 番号 1 を数えない" \
  's/for \(var d = maxDay; d >= 1; d--\)/for (var d = maxDay; d >= 2; d--)/'
mutate "欠番: 基準を最古でなく最新の受領にする" \
  's/earliestByDay\[d\] < minLater\) \{/earliestByDay[d] > minLater) {/'
mutate "未受領の日数を 8 にする" \
  's/var O1_LEDGER_NEVER_DAYS = 7;/var O1_LEDGER_NEVER_DAYS = 8;/'
mutate "未受領: 受領があっても立てる" \
  's/fs\.length === 0 && regMs !== null/regMs !== null/'
mutate "最終受領を最新でなく最古にする" \
  's/f\.receivedMs > last\) last/f.receivedMs < last) last/'
mutate "重複を数えない（dupCount が常に 0）" \
  's/if \(f\.dup\) dupCount\+\+;//'

# --- §3 通知の差分 --------------------------------------------------------------
mutate "通知: 続いているだけでも毎回通知する" \
  's/return was\.indexOf\(f\) < 0;/return true;/'
mutate "通知: 次の状態を保存しない（毎回通知になる）" \
  's/next\[key\] = flags\.join\(","\);/next[key] = "";/'
mutate "通知: 対象外の名前を通知しない" \
  's/consider\("\*", foreignCount > 0 \? \[O1_LEDGER_FLAG_FOREIGN\] : \[\]\);/consider("*", []);/'
mutate "通知: 宛先が未設定でも通知済みにする" \
  's/  if \(!cfg\.email\) \{/  props.setProperty(O1_LEDGER_PROP_STATE, JSON.stringify(plan.next));\n  if (!cfg.email) {/'
mutate "通知: 送信失敗でも通知済みにする" \
  's/\} catch \(err\) \{\n    console\.log\("⚠️ 通知メールの送信に失敗/} catch (err) {\n    props.setProperty(O1_LEDGER_PROP_STATE, JSON.stringify(plan.next));\n    console.log("⚠️ 通知メールの送信に失敗/'
mutate "通知本文に URL を載せる" \
  's/※ 詳細は O1 管理シートの/※ 詳細は https:\/\/docs.google.com\/ O1 管理シートの/'
mutate "通知本文で「やめた」と断定する" \
  's/「途絶」「未受領」は「やめた」ではありません/「途絶」「未受領」は本人がやめましたという意味です/'

# --- §4 登録ログの読み取り --------------------------------------------------------
mutate "登録ログ: 却下（blocked）も登録に数える" \
  's/if \(result !== "ok" && result !== "partial"\) continue;//'
mutate "登録ログ: 最古でなく最新の登録を採る" \
  's/ms < registered\[pid\]\) registered/ms > registered[pid]) registered/'
mutate "登録ログ: 読めない日時を黙って捨てる（skipped を数えない）" \
  's/skipped\+\+;//'

# --- §5 設定 ----------------------------------------------------------------------
mutate "設定: フォルダ ID の欠落を問題にしない" \
  's/if \(!cfg\.folderId\) problems\.push\(/if (false) problems.push(/'
mutate "設定: 宛先の形を検査しない" \
  's/if \(cfg\.email && !\/\^\[\^\\s\@\]\+\@\[\^\\s\@\]\+\\\.\[\^\\s\@\]\+\$\/\.test\(cfg\.email\)\) \{/if (false) {/'

# --- §6 通し ----------------------------------------------------------------------
mutate "同期: 既知の ID を飛ばさない（冪等が壊れる）" \
  's/if \(known\[id\]\) continue;//'
mutate "同期: ごみ箱のファイルも数える" \
  's/if \(f\.isTrashed\(\)\) continue;//'
mutate "同期: 文字列の列をテキスト形式にしない（数式注入）" \
  's/rows\.length, 1\)\.setNumberFormat\("\@"\);/rows.length, 1).setNumberFormat("0");/'
mutate "同期: 行を足さない（範囲外で落ちる）" \
  's/if \(max < lastRowNeeded\)/if (false)/'
mutate "同期: 時間予算を無効にする" \
  's/> O1_LEDGER_TIME_BUDGET_MS/> 1e15/'
mutate "実行: ロックを取らない" \
  's/if \(!lock\.tryLock\(30000\)\) \{/if (false) {/'
mutate "実行: ロスターのタブを持つ表にも書く" \
  's/if \(ss\.getSheetByName\("参加者ロスター"\)\) \{/if (false) {/'
mutate "途絶タブ: 登録ログが無くても黙って続ける" \
  's/if \(!reg\) \{\n    throw new Error\(/if (!reg) {\n    return { rows: [], foreignCount: 0 };\n    throw new Error(/'
mutate "途絶タブ: 判定を常に「正常」と表示する" \
  's/r\.flags\.length \? r\.flags\.join\("・"\) : "正常"/"正常"/'
mutate "トリガー: 既存の同名トリガーを消さない（増える）" \
  's/ScriptApp\.deleteTrigger\(triggers\[i\]\)/void 0/'
mutate "トリガー: 他のトリガーまで消す" \
  's/triggers\[i\]\.getHandlerFunction\(\) === "o1LedgerRun"/true/'
mutate "点検: o1LedgerCheck が書き込む" \
  's/(function o1LedgerCheck\(\) \{\n  var cfg = o1LedgerConfig_\(\);)/$1\n  SpreadsheetApp.openById(cfg.sheetId).insertSheet("x");/'

# --- §7 ソースの性質 ---------------------------------------------------------------
mutate "ソース: GmailApp を使う" \
  's/\z/\nfunction leak_() { GmailApp.getInboxThreads(); }\n/'
mutate "ソース: メールアドレスを直書きする" \
  's/\z/\nvar LEAK_ADDR = "someone\@example.com";\n/'
mutate "ソース: Drive に書く（ごみ箱へ送る）" \
  's/\z/\nfunction wipe_(f) { f.setTrashed(true); }\n/'
mutate "ソース: 未受領の日数をあとから 9 に上書きする（定数の直書き換え）" \
  's/var O1_LEDGER_NEVER_DAYS = 7;/var O1_LEDGER_NEVER_DAYS = 7;\nvar O1_LEDGER_STALE_DAYS_X = 5;\nO1_LEDGER_NEVER_DAYS = 9;/'

echo
echo "壊すと赤: $PASS / 穴: $FAIL"
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 赤にならない変異がある（★ 検査の穴）。上の ❌ を埋めること。"
  exit 1
fi
echo "✅ 全変異が赤になった"
exit 0
