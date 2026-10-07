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
  's/if \(was\[e\.flag\] === undefined\) return true;/return true;/'
mutate "通知: 次の状態を保存しない（毎回通知になる）" \
  's/next\[key\] = entries/next[key] = "" \&\& entries/'
mutate "通知: 対象外の名前を通知しない" \
  's/consider\("\*", foreignCount > 0 \? \[\{ flag: O1_LEDGER_FLAG_FOREIGN, detail: String\(foreignCount\) \}\] : \[\]\);/consider("*", []);/'
mutate "通知: 対象外の名前の件数の増加を見ない（旗だけ）" \
  's/return Number\(e\.detail\) > Number\(was\[e\.flag\] \|\| 0\);/return false;/'
mutate "通知: 欠番の番号の増加を見ない（旗だけ）" \
  's/if \(e\.flag === O1_LEDGER_FLAG_GAP\) \{\n          var old/if (false) {\n          var old/'
mutate "通知: 打ち切りの回でも判定を通知する" \
  's/var reliable = !result\.ops\.truncated;/var reliable = true;/'
mutate "運用: 打ち切りを運用アラートにしない" \
  's/if \(ops\.truncated\) active\[O1_LEDGER_OPS_TRUNCATED\] = true;//'
mutate "運用: 登録ログの日時不読を運用アラートにしない" \
  's/if \(ops\.regSkipped > 0\) active\[O1_LEDGER_OPS_REGSKIP\] = true;//'
mutate "運用: 台帳の不読行を運用アラートにしない" \
  's/if \(ops\.badRows > 0\) active\[O1_LEDGER_OPS_BADROWS\] = true;//'
mutate "運用: 欠番の列挙を丸めない" \
  's/gaps\.slice\(0, O1_LEDGER_GAP_LIST_MAX\)/gaps.slice(0)/'

# --- 実行の失敗（検知器の沈黙）
mutate "失敗: 同じ原因でも毎回送る（重複排除を外す）" \
  's/if \(props\.getProperty\(O1_LEDGER_PROP_FAIL\) === msg\) return;[^\n]*\n//'
mutate "失敗: 成功しても失敗の状態を解消しない" \
  's/PropertiesService\.getScriptProperties\(\)\.deleteProperty\(O1_LEDGER_PROP_FAIL\);//'
mutate "失敗: 通知はするが例外を握りつぶす（再送出しない）" \
  's/(o1LedgerNotifyFailure_\(e\);[^\n]*)\n    throw e;/$1/'
mutate "失敗: 通知に長い英数字（ID の形）を伏せない" \
  's/\.replace\(\/\[0-9A-Za-z_-\]\{25,\}\/g, "<ID>"\)//'
mutate "失敗: 失敗を通知しない（呼び出しを外す）" \
  's/    o1LedgerNotifyFailure_\(e\);[^\n]*\n//'
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
mutate "同期: 名前列の無害化を外す（先頭の = + - @ を通す）" \
  's/for \(var ci = 1; ci < row\.length; ci\+\+\) row\[ci\] = o1LedgerSafeCell_\(row\[ci\]\);//'
mutate "無害化: 先頭の = + - @ を前置しない" \
  's/return \/\^\[=\+\\-\@\\t\\r\]\/\.test\(v\) \? "⚠" \+ v : v;/return v;/'
mutate "途絶タブ: 削除済み（tombstone）を不読行にする" \
  's/if \(String\(v\[O1_LEDGER_COL\.kind\]\) === O1_LEDGER_KIND_ERASED\) return;[^\n]*\n//'
mutate "途絶タブ: 日番号 0 を不読行にする" \
  's/var dayRaw = String\(v\[O1_LEDGER_COL\.day\] === undefined \|\| v\[O1_LEDGER_COL\.day\] === null \? "" : v\[O1_LEDGER_COL\.day\]\)\.trim\(\);/var dayRaw = String(v[O1_LEDGER_COL.day] === undefined || v[O1_LEDGER_COL.day] === null || v[O1_LEDGER_COL.day] === "" ? "1" : v[O1_LEDGER_COL.day]).trim();/'
mutate "判定: 日番号 0 を番号の集合に入れる" \
  's/if \(f\.day >= 1\) \{/if (true) {/'
mutate "点検: o1LedgerCheck に時間予算を持たせない" \
  's/> O1_LEDGER_TIME_BUDGET_MS\) \{\n      truncated = true;\n      break;\n    \}\n    var f = it\.next\(\);\n    var name/> 1e15) {\n      truncated = true;\n      break;\n    }\n    var f = it.next();\n    var name/'
mutate "点検: タイムゾーンを出さない" \
  's/  console\.log\("このプロジェクトのタイムゾーン: "[^\n]*\n//'
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

# --- §9 2026-09-27 2 回目レビュー指摘の反映 ------------------------------------
mutate "辞書キー: byPid を素のオブジェクトに戻す（constructor で例外）" \
  's/var byPid = Object\.create\(null\);/var byPid = {};/'
mutate "辞書キー: seen を素のオブジェクトに戻す" \
  's/var seen = Object\.create\(null\);/var seen = {};/'
mutate "同期: Drive ファイル ID にも無害化を掛ける（冪等性が壊れる）" \
  's/for \(var ci = 1; ci < row\.length; ci\+\+\)/for (var ci = 0; ci < row.length; ci++)/'
mutate "途絶タブ: 日番号の空セルを弾かない（day 0 に化ける）" \
  's/!\/\^\\d\+\$\/\.test\(dayRaw\)/false/'
mutate "登録ログ: 見出しの中身を見ない（列を挿入されても気づけない）" \
  's/if \(String\(regHead\[hc\]\)\.trim\(\) !== O1_LEDGER_REG_HEAD\[hc\]\) \{/if (false) {/'
mutate "登録ログ: 列数の下限を見ない" \
  's/if \(reg\.getMaxColumns\(\) < O1_LEDGER_REG_HEAD\.length\) \{/if (false) {/'
mutate "通知: 打ち切りが続いても再通知しない（沈黙が続く）" \
  's/var opsDue = opsPlan\.added\.length === 0 && opsStillActive && nowForOps - lastOpsMs >= O1_LEDGER_OPS_RENOTIFY_MS;/var opsDue = false;/'
mutate "通知: 打ち切りの再通知間隔をゼロにする（毎回送ってしまう）" \
  's/var O1_LEDGER_OPS_RENOTIFY_MS = 7 \* 24 \* 60 \* 60 \* 1000;/var O1_LEDGER_OPS_RENOTIFY_MS = 0;/'
mutate "途絶タブ: 書き込み前の無害化を外す" \
  's/return o1LedgerSafeCell_\(String\(c\)\);/return String(c);/'
mutate "失敗通知: 宛先未設定でもログを出さない" \
  's/console\.log\("⚠️ " \+ O1_LEDGER_PROP_EMAIL \+ " が未設定なので実行失敗の通知を送っていません。"\);//'

mutate "登録ログ: 空タブ（見出し無し）でも見出し検査をスキップする（3 回目レビューで見つかった後退）" \
  's/if \(reg\.getLastRow\(\) < 2\) \{/if (false) {/'
mutate "登録ログ: registered を素のオブジェクトに戻す（辞書キー安全化の後退）" \
  's/var registered = Object\.create\(null\);/var registered = {};/'

mutate "途絶タブ: 桁あふれの日番号（Infinity）を弾かない（無限ループの回帰）" \
  's/!Number\.isSafeInteger\(day\)/false/'

# ★ 2026-09-28 受け口が `<P-ID>/` に保存する版（受け口 V-3）に合わせた走査
mutate "台帳の走査: 直下しか読まない（受け口の変更後に全員を未受領と誤報する）" \
  's/var it = o1LedgerAllFiles_\(folder, t0 \+ O1_LEDGER_TIME_BUDGET_MS\);(\n  var truncated = false;)/var it = (function (f) { var i = f.getFiles(); i.timedOut = function () { return false; }; return i; })(folder);$1/'
mutate "点検の走査: 直下しか読まない" \
  's/var it = o1LedgerAllFiles_\(folder, t0 \+ O1_LEDGER_TIME_BUDGET_MS\);(\n  var ok = 0;)/var it = (function (f) { var i = f.getFiles(); i.timedOut = function () { return false; }; return i; })(folder);$1/'
mutate "走査: ごみ箱のサブフォルダも読む" \
  's/      if \(d\.isTrashed\(\)\) continue;\n//'
# ⚠️ security-checker MEDIUM（2026-09-28）: 空フォルダの大量列挙で実行ごと落ちない
mutate "走査: サブフォルダ列挙の期限を見ない（大量の空フォルダで実行ごと落ちる）" \
  's/if \(new Date\(\)\.getTime\(\) > deadlineMs\) \{/if (false) {/'
mutate "台帳の走査: 期限切れを打ち切りとして扱わない" \
  's/  if \(it\.timedOut\(\)\) truncated = true;[^\n]*\n(\n)/$1/'
mutate "点検の走査: 期限切れを打ち切りとして扱わない" \
  's/  if \(it\.timedOut\(\)\) truncated = true;[^\n]*\n(  var elapsed)/$1/'

# ★ 2026-09-28 見た目（状況ボード・受領台帳の書式）
mutate "見た目: 要対応順に並べない" \
  's/return rows\.slice\(\)\.sort\(function \(a, b\) \{/return rows.slice().sort(function (a, b) { return 0;/'
mutate "見た目: 途絶の色を欠番の色にする" \
  's/\{ flag: O1_LEDGER_FLAG_STALE, bg: O1_UI\.dangerBg, fg: O1_UI\.dangerFg \}/{ flag: O1_LEDGER_FLAG_STALE, bg: O1_UI.gapBg, fg: O1_UI.dangerFg }/'
mutate "見た目: 途絶タブを clear でなく clearContents（前回の色が残る）" \
  's/  dash\.clear\(\); \/\/ ★ 値と書式の両方/  dash.clearContents(); \/\/ ★ 値と書式の両方/'
mutate "見た目: 途絶タブの見出しを固定しない" \
  's/  dash\.setFrozenRows\(H\);/  dash.setFrozenRows(2);/'
mutate "見た目: 受領台帳の書式を毎回付け直す（研究者の列幅を戻す）" \
  's/  if \(sheet\.getFrozenRows\(\) === 2\) return false;\n  var width = O1_LEDGER_HEAD\.length;/  var width = O1_LEDGER_HEAD.length;/'
mutate "見た目: 条件付き書式の範囲を 1 列狭くする" \
  's/sheet\.getRange\("A3:" \+ colLetter\(width - 1\)\)/sheet.getRange("A3:" + colLetter(width - 2))/'
mutate "見た目: 結合を表題の 4 行だけ解く（空の案内行の結合が残る）" \
  's/dash\.getRange\(1, 1, dash\.getMaxRows\(\), width\)\.breakApart\(\);/dash.getRange(1, 1, H - 1, width).breakApart();/'
mutate "見た目: 経過日数の赤字を外す" \
  's/dash\.getRange\(row, 4\)\.setFontColor\(O1_UI\.dangerFg\)/dash.getRange(row, 4).setFontColor(O1_UI.ink)/'

mutate "見た目: 途絶タブの書式の例外を捕まえない（通知が止まる）" \
  's/\} catch \(e\) \{\n    console\.log\("⚠️ 途絶タブの見た目/} catch (e) { throw e;\n    console.log("⚠️ 途絶タブの見た目/'
mutate "見た目: 受領台帳の書式の例外を捕まえない（走査が止まる）" \
  's/  try \{\n    o1LedgerStyleLedgerTab_\(sheet\);/  o1LedgerStyleLedgerTab_(sheet); if (false) try {/'

# ★ 2026-10-07 O1 終了判定（`.steering/20261007-o1-end-judgement/`）
mutate "終了判定: 21 日目の当日に終了にする（1 日早い）" \
  's/var ended = todayKey > endKey;/var ended = todayKey >= endKey;/'
mutate "終了判定: 期間を 20 日にする" \
  's/var endKey = first \+ O1_LEDGER_END_DAYS - 1;/var endKey = first + O1_LEDGER_END_DAYS - 2;/'
mutate "終了判定: 登録日より前の日付も起算日に使う" \
  's/ \|\| k < regKey \|\| / || /'
mutate "終了判定: 受領日より後（未来）の日付も使う" \
  's/ \|\| k > recvKey \+ 1\) \{/) {/'
mutate "終了判定: 受領日よりずっと前の日付も使う" \
  's/      if \(k < recvKey - O1_LEDGER_END_MAX_LAG_DAYS\) \{/      if (false) {/'
mutate "終了判定: 重複行の下の記入を捨てる" \
  's/            if \(!a\) cur\[c\] = r\[c\];\n            else if \(b && a !== b\) cur\[c\] = a \+ " ／ " \+ b;/            0;/'
mutate "終了判定: 遅れて届いた記録があっても片づけを可にする" \
  's/      if \(late > 0\) settle = O1_LEDGER_END_SETTLE_CHECK;\n      else if/      if/'
mutate "終了判定: 遅れて届いた除外を表示しない" \
  's/        \(r\.late \? /        (false ? /'
mutate "終了判定: 起算日が無いと除外数を出さない" \
  's/      \(r\.status === O1_LEDGER_END_UNREG \? "" : String\(r\.daysIn\)\) \+\n        \(r\.ignored \?/      (r.status === O1_LEDGER_END_UNREG ? "" : String(r.daysIn)) +\n        (r.firstKey !== null \&\& r.ignored ?/'
mutate "終了判定: 登録の無い P-ID も判定する" \
  's/    if \(regKey === null\) \{\n      return \{ pid: pid, status: O1_LEDGER_END_UNREG/    if (false) {\n      return { pid: pid, status: O1_LEDGER_END_UNREG/'
mutate "終了判定: 2000 年より前の年も読む" \
  's/  if \(y < 2000\) return null;/  /'
mutate "終了判定: 届いた日の数に期間の後の日も数える" \
  's/      return k <= endKey;\n    \}\)\.length;/      return true;\n    }).length;/'
mutate "終了判定: 21 日目の記録が無くてもすぐ片づけ可にする" \
  's/      else settle = O1_LEDGER_END_SETTLE_WAIT;/      else settle = O1_LEDGER_END_SETTLE_ELAPSED;/'
mutate "終了判定: ありえない日付も読む" \
  's/  if \(back\.getUTCMonth\(\) !== mo - 1 \|\| back\.getUTCDate\(\) !== d\) return null;/  /'
mutate "終了判定: 終了が続くたびに通知する" \
  's/      return !before\[r\.pid\];/      return true;/'
mutate "終了判定: 打ち切りの回にも終了を通知する" \
  's/var endedToSend = reliable \? endPlan\.added : \[\];/var endedToSend = endPlan.added;/'
mutate "終了判定: 研究者の記入を引き継がない" \
  's/      manualByPid\[pid\] = r\.slice\(\);\n    \}\);/      0;\n    });/'
mutate "終了判定: 書く前にタブを clear する（失敗で記入が消える）" \
  's/  if \(!sheet\) sheet = ss\.insertSheet\(O1_LEDGER_END_TAB\);\n  o1LedgerEnsureRows_\(sheet, out\.length\);/  if (!sheet) sheet = ss.insertSheet(O1_LEDGER_END_TAB);\n  sheet.clear();\n  o1LedgerEnsureRows_(sheet, out.length);/'
mutate "終了判定: 見出しを照合しない（記入がずれる）" \
  's/      if \(String\(head\[hc\]\)\.trim\(\) !== O1_LEDGER_END_HEAD\[hc\]\) \{/      if (false) {/'
mutate "終了判定: 貼られた日付を整形しない" \
  's/    if \(v instanceof Date\) return/    if (false) return/'
mutate "終了判定: メールに 21 日目の日付を載せる" \
  's/" 日目が過ぎました（今日 " \+ e\.dayNo \+/" 日目（" + o1LedgerKeyToStr_(e.endKey) + "）が過ぎました（今日 " + e.dayNo +/'
mutate "終了判定: タイムゾーンの警告を出さない" \
  's/  if \(tz !== "Asia\/Tokyo"\) warn\.push/  if (false) warn.push/'
mutate "終了判定: 終了判定のタブの例外を捕まえない（途絶の通知が止まる）" \
  's/  try \{\n    o1LedgerWriteEnd_\(ss, endRows, nowMs, (\{[^\n]*\})\);\n  \} catch \(e\) \{/  { o1LedgerWriteEnd_(ss, endRows, nowMs, $1); } if (false) { var e;/'
mutate "終了判定: タブをテキスト形式にしない" \
  's/  var all = sheet\.getRange\(1, 1, out\.length, width\);\n  all\.setNumberFormat\("@"\);/  var all = sheet.getRange(1, 1, out.length, width);/'
mutate "終了判定: 記入欄を無害化しない" \
  's/      return o1LedgerSafeCell_\(String\(cell\)\); \/\/ ★ 研究者の記入欄も含めて無害化する/      return String(cell);/'
mutate "終了判定: 連絡済みの表示にしない" \
  's/  if \(manual && filled\(manual\[O1_LEDGER_END_MANUAL\.contacted\]\)\) return O1_LEDGER_END_CONTACTED;/  /'
mutate "終了判定: byPidEnd を素のオブジェクトに戻す（constructor で例外）" \
  's/var byPidEnd = Object\.create\(null\);/var byPidEnd = {};/'

echo
echo "壊すと赤: $PASS / 穴: $FAIL"
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 赤にならない変異がある（★ 検査の穴）。上の ❌ を埋めること。"
  exit 1
fi
echo "✅ 全変異が赤になった"
exit 0
