#!/usr/bin/env bash
# ★ `o1_form_builder_test.cjs` が **空回りしていない**ことを測る（変異テスト）。
#
# ⚠️★★★ なぜ要るか: 「78 ケース全部 OK」は、**検査が何も見ていなくても**出る。
#   ★ ガードを 1 つずつ壊して**赤になるか**を確かめるまで、緑に意味は無い
#     (`verify-before-claiming` ルール 5b)。
#
# ★ 本物の `GSE_O1_Form_Builder.gs` は 1 バイトも変更しない（一時ディレクトリで壊す）。
#
# 使い方: bash Form_O1/o1_form_builder_mutation_test.sh
# 終了コード: 0 = 全変異が赤になった / 1 = 赤にならない変異がある（★ 検査の穴）

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SRC="Form_O1/GSE_O1_Form_Builder.gs"
TEST="Form_O1/o1_form_builder_test.cjs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0

# 変異を 1 つ適用して、テストが**赤になる**ことを確かめる。
# $1 = 変異の名前 / $2.. = 一時コピーに対して走らせる perl の式
SEEN_HASHES=""

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
  # ⚠️★★★ **別の変異と同じ結果になっていないか**（code-reviewer HIGH・2026-08-29）。
  #   ★ 複合の `s///; s///` は**片方だけ当たっても** `cmp -s` を通ってしまうので、
  #     ⚠️ 「二重とも外す」つもりの変異が**片方だけの変異と byte 同一**になっていた。
  #   → ★ 生成物のハッシュを覚えておき、⚠️ **重複したら赤にする**
  #     （= どこかの置換が当たっていない、という構造的な証拠である）。
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
  if node "$TEST" "$f" > /dev/null 2>&1; then
    echo "  ❌ 壊しても緑のまま（★ 検査の穴）: $name"
    FAIL=$((FAIL+1))
  else
    echo "  ✅ 壊すと赤になる: $name"
    PASS=$((PASS+1))
  fi
}

echo "=== 変異テスト: ガードを 1 つずつ壊して赤になるか ==="

# --- §1 G1 のフォームを壊さない ----------------------------------------------
mutate "G1 の拒否リストを空にする" \
  's/var G1_FORM_IDS_DO_NOT_TOUCH = \{.*?\};/var G1_FORM_IDS_DO_NOT_TOUCH = {};/s'

mutate "o1AssertNotG1Form_ を素通りにする" \
  's/(function o1AssertNotG1Form_\(id, varName\) \{)/$1\n  return;/'

mutate "検証より先にフォームを開く（順序を入れ替える）" \
  's/  o1AssertNotG1Form_\(id, varName\);\n  return FormApp\.openById\(id\);/  var f = FormApp.openById(id);\n  o1AssertNotG1Form_(id, varName);\n  return f;/'

mutate "設定チェックから G1 の ID 検出を外す" \
  's/    if \(g1Label\) \{/    if (false) {/'

# ⚠️★ 2026-08-28: `installO1ConsentTrigger` は**二重に守られている**
#   （`o1ConfigProblems_` の G1 検出 ＋ 直接の `o1AssertNotG1Form_`）。
#   ★ 片方だけ外しても、もう片方が止めるので赤にならない —— それは**穴ではなく多層防御**である。
#   → ★ 意味のある変異は「**両方**外す」。⚠️ それでも緑なら本物の穴。
mutate "installO1ConsentTrigger の G1 検証を**二重とも**外す" \
  's/    if \(g1Label\) \{/    if (false) {/; s/  o1AssertNotG1Form_\(consentFormId, "FORM_ID_O1_CONSENT"\);\n//'

# --- §2 回答の保全 ------------------------------------------------------------
mutate "o1AssertSafeToRebuild_ を素通りにする" \
  's/(function o1AssertSafeToRebuild_\(form, label\) \{)/$1\n  return;/'

mutate "回答数を確認できないときに 0 件として続行する" \
  's/    throw new Error\(\n      "★ " \+\n        label \+\n        " の回答数を確認できませんでした/    n = 0; if (false) throw new Error(\n      "★ " +\n        label +\n        " の回答数を確認できませんでした/'

# --- §3 fail-closed -----------------------------------------------------------
mutate "空のフォーム ID でも開きにいく" \
  's/  if \(!id\) \{\n    throw new Error\(\n      "★ " \+\n        varName \+\n        " が空です。フォームを量産しないため停止しました/  if (false) {\n    throw new Error(\n      "★ " +\n        varName +\n        " が空です。フォームを量産しないため停止しました/'

mutate "古いほうの管理シートを素通りにする" \
  's/  return String\(id \|\| ""\)\.indexOf\("12T8WU4D"\) === 0;/  return false;/'

mutate "受付メールがスナップショットを無視して毎回読み直す" \
  's/    appDownloadUrlOpt === undefined \? o1Config_\(\)\.appDownloadUrl : appDownloadUrlOpt;/    o1Config_().appDownloadUrl;/'

mutate "配布 URL が URL でなくても通す（打ち間違いを見逃す）" \
  's/  return String\(url \|\| ""\)\.indexOf\("https:\/\/"\) !== 0;/  return false;/'

# ⚠️★★ **空検査だけを外しても赤にならなくなった**（2026-08-29）:
#   ★ 直後に `o1AppDownloadUrlIsBad_` が空文字も弾くため（= 多層防御が効いている）。
#   → ★ 変異は「**fail-closed を全部外す**」に変える（⚠️ 片方だけでは意味が無い）。
mutate "配布 URL の fail-closed を全部外す" \
  's/  if \(!appDownloadUrl\) \{/  if (false) {/; s/  if \(o1AppDownloadUrlIsBad_\(appDownloadUrl\)\) \{/  if (false) {/'

# --- §4/§5 採番と冪等 ----------------------------------------------------------
mutate "採番が 1 行だけのロスターを見落とす（G1 の last > 1 に戻す）" \
  's/var values = last >= 1 \?/var values = last > 1 ?/'

# --- §11 ロスターへの書き込みの防波堤（起票 T-22 / T-23 / T-24・2026-08-29） -------

mutate "ロスターへ書く値を無害化しない（★ 数式インジェクション・security-checker HIGH）" \
  's/  return \/\^\[=\+\\-\@\\t\\r\]\/\.test\(s\) \? "'"'"'" \+ s : s;/  return s;/'

mutate "書き込み経路で古い管理シートの拒否リストを見ない（security-checker MEDIUM）" \
  's/  if \(o1IsKnownWrongRoster_\(rosterSheetId\)\) \{\n    Logger\.log\("⛔⚠️★★★ \*\*古いほうの管理シート\*\*を指しています。/  if (false) {\n    Logger.log("⛔⚠️★★★ **古いほうの管理シート**を指しています。/'

mutate "点検関数が古い管理シートの拒否リストを見ない（security-checker MEDIUM）" \
  's/  if \(o1IsKnownWrongRoster_\(rosterSheetId\)\) \{\n    Logger\.log\("⛔⚠️★★★ \*\*古いほうの管理シート\*\*を指しています（/  if (false) {\n    Logger.log("⛔⚠️★★★ **古いほうの管理シート**を指しています（/'

mutate "ロスターの形の検査を丸ごと素通りにする（T-23）" \
  's/function o1RosterShapeProblem_\(sheet\) \{/function o1RosterShapeProblem_(sheet) {\n  return "";/'

mutate "見出しの列一致だけを外す（T-23・A 列が合っていれば通す）" \
  's/    if \(actual !== O1_ROSTER_HEAD\[c\]\) \{/    if (false) {/'

mutate "P-ID の行が 1 つも無くても通す（T-23・新規の空ロスターを見逃す）" \
  's/  return \(\n    "P-ID の行が 1 つもありません/  return "";\n  return (\n    "P-ID の行が 1 つもありません/'

mutate "点検関数が形の違いを黙って通す（T-23・checkO1RosterShape）" \
  's/    Logger\.log\(\n      "⛔⚠️★★★ ロスターの形が違います: " \+ problem \+ "\\n" \+/    Logger.log(\n      "" +/'

mutate "重複検査が失敗したときに送信を止めてしまう（T-24・検査の失敗で被験者を止める）" \
  's/  if \(dupRows === null\) \{/  if (dupRows === null) {\n    return;/'

mutate "P-ID 重複でも受付メールを送る（T-24）" \
  's/  \} else if \(dupRows\.length > 1\) \{/  } else if (false) {/'

mutate "新規行に OS を書かない（T-22）" \
  's/      o1PlainText_\(a\.os \|\| ""\),\n//'

mutate "既存行の空の OS を補わない（T-22）" \
  's/      if \(a\.os && !String\(roster\.getRange\(found\.row, 4\)\.getValue\(\)\)\.trim\(\)\) \{/      if (false) {/'

mutate "既存行の OS を上書きしてしまう（T-22・陰性対照を撃つ）" \
  's/      if \(a\.os && !String\(roster\.getRange\(found\.row, 4\)\.getValue\(\)\)\.trim\(\)\) \{/      if (a.os) {/'

mutate "受付メール失敗時に P-ID をログへ残さない" \
  's/"❌⚠️★★ 受付メールに失敗しました（P-ID は確定済: " \+/"❌ 受付メールに失敗しました（" + "" +/'

mutate "ログに実メールアドレスをそのまま出す" \
  's/function o1MaskEmail_\(email\) \{/function o1MaskEmail_(email) {\n  return String(email);/'

# --- §6 同意項目と約束 ---------------------------------------------------------
mutate "回答取得の設問タイトルをずらす（構築側と食い違わせる）" \
  's/else if \(title === Q_O1_EMAIL\)/else if (title === "メール")/'

mutate "録画の同意をこのフォームで取ってしまう" \
  's/(    "上記すべてに同意し、この記録と研究利用に同意します。",)/    "画面の録画に同意します。",\n$1/'

# ⚠️★ 変異は「値が本当に消える」形で書くこと。★ 2026-08-28 に、置換したつもりで
#   後続行の連結が生き残り、**変異が効いていないのに緑**という偽の合格を一度出している。
mutate "同意項目から保管上限を落とす（当たり障りのない文言に置き換える）" \
  's/(function o1ConsentItemTitles_\(\) \{)/$1\n  if (true) return new Array(11).fill("上記に同意します。");/'

mutate "連絡先メールを同意文書と食い違わせる" \
  's/var O1_CONTACT_EMAIL = "[^"]*";/var O1_CONTACT_EMAIL = "someone.else\@example.com";/'

# --- §7 アンケートが約束を破らない --------------------------------------------
mutate "アンケートで一時停止の理由を尋ねる" \
  's/(  var del = form\.addMultipleChoiceItem\(\);)/  form.addParagraphTextItem().setTitle("「一時停止」を使った理由を教えてください。");\n$1/'

mutate "「理由は聞かない」の明記を消す" \
  's/⚠️ 「一時停止」や「削除」を使われた\*\*理由はお聞きしません\*\*（お約束のとおりです）。/よろしくお願いします。/'

# --- §8/§10 -------------------------------------------------------------------
mutate "migrate が既存設問を消すようにする" \
  's/(function migrateO1ConsentForm\(\) \{\n  var form = o1OpenFixed_\(o1Config_\(\)\.consentFormId, "FORM_ID_O1_CONSENT"\);)/$1\n  o1ClearForm_(form);/'

mutate ".gs にシークレットを直書きする" \
  's/(var O1_AUTO_SEND = true;)/$1\nvar SHARED_SECRET = "abcdefghijklmnopqrstuvwxyz123456";/'  # gate:allow-id ★ 変異が注入する偽の秘密（アルファベット順）

# --- ★ 2026-08-28 のレビュー指摘で入れたガード -------------------------------
# ⚠️★ 2026-09-03: 対象コードを `bare-row-claim` の修正で書き換えたので、変異も追随させた。
#   ★ 旧変異は `if (!rowEmail) return {...}` の 1 行を決め打ちしており、
#   ⚠️ 修正後は**置換対象が消えて「変異が当たらなかった」**になっていた
#   （★ すり抜けではなく、変異ハーネス側の陳腐化である）。
mutate "★ 申告された P-ID をメール検証なしで信用する（他人の ID を名乗れる）"   's/      return \{ conflict: true, pid: rowPid, row: i \+ 1, reason: "email-mismatch" \};/      return { pid: rowPid, row: i + 1 };/'

# ⚠️★★★ 裸の行の乗っ取り（2026-09-03 に G1 から移植した修正を壊す）。
mutate "★ 裸の行（氏名もメールも空）を申告 P-ID だけで渡す（総当たりで取れる）"   's/        if \(!rowName\) \{/        if (false) {/'

mutate "★ P-ID 列が空の行で appendRow に落とす（1 人に 2 つの ID）"   's/      var p = found\.pid;
      if \(!p\) \{/      var p = found.pid;
      if (false) {/'

mutate "★ 受付メールを作れない設定でも先に採番する"   's/  try \{
    o1RegisterAckBody_\("P000", ackUrlSnapshot\);
  \} catch \(cfgErr\) \{/  try {
    if (false) o1RegisterAckBody_("P000", ackUrlSnapshot);
  } catch (cfgErr) {/'

mutate "★ 設定が欠けていてもトリガを張る"   's/  var problems = o1ConfigProblems_\(\);
  if \(problems\.length\) \{
    throw new Error\(
      "⛔ 設定に問題があるのでトリガを張りません/  var problems = [];
  if (problems.length) {
    throw new Error(
      "⛔ 設定に問題があるのでトリガを張りません/'

mutate "★ アンケートで動機を尋ねる設問を戻す"   's/(  var otherDevice = form\.addMultipleChoiceItem\(\);)/  form.addMultipleChoiceItem().setTitle("記録を避けるために、アプリを止めましたか。");
$1/'

echo
# --- ★ 2026-09-03 に足したガード（#1 管理シート / #4 メール重複 / #5 予約トークン） ---

mutate "★ 登録ログの PII 歯止めを外す（@ を含む値をそのまま書く）" \
  's/(function o1MgmtSafeCell_\(v\) \{)/$1\n  return String(v);/'

mutate "★ 登録ログが「参加者ロスター」タブを持つ表でも書く（2 か所採番の芽）" \
  's/  if \(ss\.getSheetByName\("参加者ロスター"\)\) \{\n    Logger\.log\(/  if (false) {\n    Logger.log(/'

mutate "★ 登録ログにロスターと同じ ID を指しても問題にしない" \
  's/  if \(cfg\.rosterSheetId && id === cfg\.rosterSheetId\) \{/  if (false) {/'

mutate "★ 採番元に登録ログと同じ表を指しても開く（逆向きのガードを外す）" \
  's/  if \(rosterSheetId && o1cfg\.mgmtSheetId && rosterSheetId === o1cfg\.mgmtSheetId\) \{/  if (false) {/'

mutate "★ 構築時に O1_MGMT_SHEET_ID を検査しない（fail-closed を外す）" \
  's/  var mgmtProblem = o1MgmtConfigProblem_\(cfg\);/  var mgmtProblem = "";/'

mutate "★ 登録ログに書けなかったことを黙って捨てる（silent failure）" \
  's/    if \(!sheet\) \{\n      Logger\.log\(/    if (false) {\n      Logger.log(/'

# ⚠️★ 2026-09-03: 対象コードを**却下タブ分離**で書き換えたので、変異も追随させた。
#   ★ 旧変異は `if (last >= O1_MGMT_MAX_ROWS) {` を決め打ちしており、
#   ⚠️ 変更後は **置換対象が消えて「変異が当たらなかった」**になっていた
#   （★ ハーネスの `cmp -s` がそれを赤で報告した ＝ 空回りを見逃さなかった）。
mutate "★ 登録ログの上限を無視して無制限に追記する" \
  's/    if \(sheet\.getLastRow\(\) >= cap\) \{/    if (false) {/'

mutate "★ ロスターに同じメールが 2 行あっても先頭行を黙って採る" \
  's/    if \(emailHits\.length > 1\) \{/    if (false) {/'

mutate "★ conflict の文面を理由によらず固定文に戻す（嘘の直し方を案内する）" \
  's/  switch \(found\.reason\) \{/  switch ("email-mismatch") {/'

mutate "★ 予約トークンを P-ID の形にする（採番に混ざる）" \
  's/(function o1ReserveToken_\(\) \{)/$1\n  return "P999999";/'

mutate "★ 採番したあと読み返さずに確定する（譲らない = 二重採番を配る）" \
  's/    if \(o1CountPidRows_\(roster, candidate\) === 1\) return \{ pid: candidate, row: row \};/    if (true) return { pid: candidate, row: row };/'

# --- ★ 2026-09-03 のレビュー指摘で入れたガード -------------------------------

mutate "⚠️★★★ 数える側だけ正規化する（★ 表記ゆれで採番が恒久デッドロック）" \
  's/    if \(String\(col\[i\]\[0\]\) === pid\) n\+\+;/    if (String(col[i][0]).trim().toUpperCase() === String(pid).trim().toUpperCase()) n++;/'

mutate "★ 候補が進まないときの番人を外す（★ 3 回粘って毎回失敗する形に戻す）" \
  's/    if \(k > 1 && candidate === lastCandidate\) \{/    if (false) {/'

mutate "★ 採番中の例外を捕まえない（★「採番済み・通知なし・記録なし」に戻す）" \
  's/  \} catch \(e\) \{\n    Logger\.log\(\n      "❌⚠️★★★ 採番の途中で失敗しました/  } catch (eIgnored) { throw eIgnored; } if (false) { try {} catch (e) {\n    Logger.log(\n      "❌⚠️★★★ 採番の途中で失敗しました/'

mutate "★ 未捕捉の例外を握らない（★ 最も説明の要る失敗が記録されなくなる）" \
  's/  \} catch \(unexpected\) \{/  } catch (unexpected) { throw unexpected; } if (false) { try {} catch (unexpected2) {/'

mutate "⚠️★★★ 却下を登録ログと同じ枠に書く（★ 監査証跡を第三者が止められる）" \
  's/    var rejected = result === "blocked";/    var rejected = false;/'

# ⚠️★ 2026-09-03: 対象コードを try/catch 化したので変異も追随させた
#   （★ ハーネスの `cmp -s` が「変異が当たらなかった」と赤で報告した）。
mutate "★ 空 P-ID 行の採番だけ読み返しを飛ばす（★ #5 の穴を 1 経路だけ戻す）" \
  's/          settled = o1SettlePidForToken_\(roster, blankToken\);/          settled = { pid: o1NextParticipantId_(roster), row: found.row };/'

mutate "★ 重複の原因を言い分けない（★ 表記ゆれでも「同時採番」と誤って伝える）" \
  's/    if \(drifted\.length\) \{/    if (false) {/'

mutate "★ 備考の許可リストを拒否リストへ戻す（★ @ を含まない PII が素通り）" \
  's/  if \(!O1_MGMT_NOTE_ALLOWED\.test\(probe\)\) \{/  if (probe.indexOf("@") >= 0) {/'

mutate "★ 却下ログ満杯を消えない側に残さない（★ 黙らされたことが黙って消える）" \
  's/      if \(rejected\) o1NoteRejectLogFull_\(\);/      if (false) o1NoteRejectLogFull_();/'

mutate "★ 送信ログを try の内側へ戻す（★ 送信済みなのに mail-failed と記録しうる）" \
  's/  o1LogMgmt_\("register", pid, logResult, logReason, outcome\.note\);/  \/* moved *\//'

mutate "★ 空 P-ID 行の採番で例外を捕まえない（★ 中途半端な P-ID が残る）" \
  's/        \} catch \(blankErr\) \{/        } catch (blankErrIgnored) { throw blankErrIgnored; } if (false) { try {} catch (blankErr) {/'

mutate "★ 登録経路のログ呼び出しだけ消す（★ 定義は残す = 件数ガードの単独検証）" \
  's/o1LogMgmt_\("register"/o1SkipLog_("register"/g'

# ★ 2026-09-28 見た目（登録ログ・却下ログ）
mutate "見た目: 書式を毎回付け直す（研究者の列幅を戻す）" \
  's/  if \(sheet\.getFrozenRows\(\) === 2\) return false;\n  var U = O1_MGMT_UI;/  var U = O1_MGMT_UI;/'
mutate "見た目: partial を緑にする" \
  's/(=\$D3="partial".), result, U\.warnBg/$1, result, U.okBg/'
mutate "見た目: 却下ログを登録ログと同じ色にする" \
  's/sheet\.setTabColor\(rejected \? U\.dangerFg : U\.navy\);/sheet.setTabColor(U.navy);/'
mutate "見た目: 既存タブには書式を付けない" \
  's/    styled = o1StyleMgmtTab_\(sheet, tab === O1_MGMT_REJECT_TAB\);/    styled = false;/'
mutate "見た目: system の灰を先に置く（満杯の警告行が埋もれる）" \
  's/(    rule\(.=\$D3="ok".*?\n)(.*?\n)(.*?\n)(    rule\(.=\$B3="system".*?)\n/    rule(\x27=$B3="system"\x27, rows, U.grayBg, U.muted),\n$1$2$3/s'
mutate "見た目: 書式の例外を捕まえない" \
  's/  try \{\n    styled = o1StyleMgmtTab_/  { styled = o1StyleMgmtTab_/'

# ★ 2026-10-07 O1 リンク集（`.steering/20261007-o1-links-tab/`）
mutate "リンク集: ロスタータブを持つ表にも書く" \
  's/(function o1BuildLinksTab_\(ss\) \{\n.*?\n)  if \(ss\.getSheetByName\("参加者ロスター"\)\) \{/$1  if (false) {/s'
mutate "リンク集: 手で入れた欄を引き継がない" \
  's/  var manual = o1ReadLinksManual_\(sheet\);/  var manual = {};/'
mutate "リンク集: 数式を無害化しない" \
  's/    return r\.map\(o1PlainText_\);/    return r;/'
mutate "リンク集: 運営シートの ID の検査を外す" \
  's/(function refreshO1LinksTab\(\) \{\n  var cfg = o1Config_\(\);\n  var problem = o1MgmtConfigProblem_\(cfg\);\n)  if \(problem\) throw new Error\("⛔ " \+ problem\);/$1/'
mutate "リンク集: O1-S の回答 URL に編集 URL を載せる" \
  's/s \? s\.publishedUrl : notYet/s ? s.editUrl : notYet/'
mutate "リンク集: buildO1MgmtSheet から作らない" \
  's/    o1BuildLinksTab_\(ss\);\n  \} catch \(e\) \{/    0;\n  } catch (e) {/'
mutate "リンク集: 手で入れた欄を表示値でなく値で読む（日付が化ける）" \
  's/var vals = sheet\.getRange\(1, 1, last, 2\)\.getDisplayValues\(\);/var vals = sheet.getRange(1, 1, last, 2).getValues();/'
mutate "リンク集: build でリンク集の例外を捕まえない" \
  's/  try \{\n    o1BuildLinksTab_\(ss\);\n  \} catch \(e\) \{/  {\n    o1BuildLinksTab_(ss);\n  } if (false) { var e;/'
mutate "リンク集: 同じ項目名は最後の値を採る" \
  's/    if \(out\[label\] === undefined \|\| out\[label\] === ""\) out\[label\] = v;/    out[label] = v;/'
mutate "リンク集: O1-S の「いつ」から終了判定の後を消す" \
  's/【期間の終わり・「O1 終了判定」タブが終了（連絡待ち）になった後】研究者が/研究者が/'

# --- §19 O1-C の登録用の設問の照合と修復（2026-10-08） -------------------------
mutate "修復: メールアドレスを足さない" \
  's/(  missing\.forEach\(function \(t\) \{\n)    o1AddRegistrationItem_\(form, t\);/$1    if (t !== Q_O1_EMAIL) o1AddRegistrationItem_(form, t);/'
# 2026-10-08 に私が実際に入れかけた誤り。残っている登録用の設問を全部から取ると、参加者ID だけ欠けた形を素通りさせる。
mutate "修復: 最後に来るべき設問を、欠けより前でなく残っている全部から取る" \
  's/  var kept = O1_REGISTRATION_TITLES\.slice\(0, O1_REGISTRATION_TITLES\.indexOf\(missing\[0\]\)\);/  var kept = O1_REGISTRATION_TITLES.filter(function (t) { return !!present[t]; });/'
mutate "修復: フォームの最後の設問を見ない" \
  's/  if \(lastTitle !== wantLast \|\| lastIsHeader !== !kept\.length\) \{/  if (false) {/'
mutate "修復: 揃っていても足す（冪等でない）" \
  's/  if \(!missing\.length\) \{\n    Logger\.log\(\n.*?\n    \);\n    return 0;\n  \}/  if (!missing.length) missing = [Q_O1_OS];/s'
mutate "照合: 欠けを挙げない" \
  's/      problems\.push\("欠けている: " \+ e\.title\);\n      return;/      return;/'
mutate "照合: 必須の有無を見ない" \
  's/      if \(req !== e\.required\) \{/      if (false) {/'
mutate "照合: 並びを見ない" \
  's/    if \(pos < lastPos\) \{/    if (false) {/'
mutate "照合: 種類を見ない" \
  's/    if \(type !== e\.type\) \{/    if (false) {/'
mutate "照合: 同意項目を期待に入れない" \
  's/(  o1ConsentItemTitles_\(\)\.forEach\(function \(t\) \{\n)    expected\.push\(\{ title: t, type: FormApp\.ItemType\.CHECKBOX, required: true \}\);/$1    0;/'
mutate "照合: 一致しないのに true を返す" \
  's/      problems\.join\("\\n  - "\)\n  \);\n  return false;/      problems.join("\\n  - ")\n  );\n  return true;/'
mutate "migrate: 照合せずに「一致しています」と言う（10/03 の誤報）" \
  's/  var problems = o1ConsentFormShapeProblems_\(form\);\n  if \(problems\.length\) \{\n    Logger\.log\(\n      \(added \? "" : "追加する同意項目はありません。"\)/  var problems = [];\n  if (problems.length) {\n    Logger.log(\n      (added ? "" : "追加する同意項目はありません。")/'
mutate "照合: 選択肢を見ない" \
  's/      if \(e\.choices\) \{/      if (false) {/'
mutate "照合: 重複を見ない" \
  's/    if \(seen\[t\] === 1\) problems\.push/    if (false) problems.push/'
mutate "修復: 欠け以外の問題を見ずに足す" \
  's/  if \(other\.length\) \{/  if (false) {/'
mutate "照合: 既知のタイトルの辞書にプロトタイプを持たせる" \
  's/  var known = Object\.create\(null\);/  var known = {};/'
mutate "修復: 最後の設問の種類を見ない" \
  's/  if \(lastTitle !== wantLast \|\| lastIsHeader !== !kept\.length\) \{/  if (lastTitle !== wantLast) {/'
mutate "構築: 登録用の設問を足す順を入れ替える" \
  's/var O1_REGISTRATION_TITLES = \[Q_O1_PID, Q_O1_NAME, Q_O1_EMAIL, Q_O1_OS\];/var O1_REGISTRATION_TITLES = [Q_O1_PID, Q_O1_EMAIL, Q_O1_NAME, Q_O1_OS];/'

echo "────────────────────────────────────────"
echo "  変異: 赤になった $PASS 件 / 緑のままだった $FAIL 件"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ 検査は空回りしていない（全変異が捕まった）。"
else
  echo "  ❌ ⚠️ 上の変異は検査をすり抜けた。★ ケースを足すこと。"
fi
echo "────────────────────────────────────────"
[ "$FAIL" -eq 0 ]
