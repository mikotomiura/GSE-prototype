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
  's/    if \(g1Label\) \{/    if (false) {/; s/  o1AssertNotG1Form_\(FORM_ID_O1_CONSENT, "FORM_ID_O1_CONSENT"\);\n//'

# --- §2 回答の保全 ------------------------------------------------------------
mutate "o1AssertSafeToRebuild_ を素通りにする" \
  's/(function o1AssertSafeToRebuild_\(form, label\) \{)/$1\n  return;/'

mutate "回答数を確認できないときに 0 件として続行する" \
  's/    throw new Error\(\n      "★ " \+\n        label \+\n        " の回答数を確認できませんでした/    n = 0; if (false) throw new Error(\n      "★ " +\n        label +\n        " の回答数を確認できませんでした/'

# --- §3 fail-closed -----------------------------------------------------------
mutate "空のフォーム ID でも開きにいく" \
  's/  if \(!id\) \{\n    throw new Error\(\n      "★ " \+\n        varName \+\n        " が空です。フォームを量産しないため停止しました/  if (false) {\n    throw new Error(\n      "★ " +\n        varName +\n        " が空です。フォームを量産しないため停止しました/'

mutate "配布 URL が空でも受付メールを作る" \
  's/  if \(!O1_APP_DOWNLOAD_URL\) \{\n    throw new Error\(/  if (false) {\n    throw new Error(/'

# --- §4/§5 採番と冪等 ----------------------------------------------------------
mutate "採番が 1 行だけのロスターを見落とす（G1 の last > 1 に戻す）" \
  's/var values = last >= 1 \?/var values = last > 1 ?/'

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
  's/(function migrateO1ConsentForm\(\) \{\n  var form = o1OpenFixed_\(FORM_ID_O1_CONSENT, "FORM_ID_O1_CONSENT"\);)/$1\n  o1ClearForm_(form);/'

mutate ".gs にシークレットを直書きする" \
  's/(var O1_AUTO_SEND = true;)/$1\nvar SHARED_SECRET = "abcdefghijklmnopqrstuvwxyz123456";/'

# --- ★ 2026-08-28 のレビュー指摘で入れたガード -------------------------------
mutate "★ 申告された P-ID をメール検証なしで信用する（他人の ID を名乗れる）"   's/      if \(!rowEmail\) return \{ pid: rowPid, row: i \+ 1 \};.*
      \/\/ .*
      return \{ conflict: true, pid: rowPid, row: i \+ 1 \};/      return { pid: rowPid, row: i + 1 };/'

mutate "★ P-ID 列が空の行で appendRow に落とす（1 人に 2 つの ID）"   's/      var p = found\.pid;
      if \(!p\) \{/      var p = found.pid;
      if (false) {/'

mutate "★ 受付メールを作れない設定でも先に採番する"   's/  try \{
    o1RegisterAckBody_\("P000"\);
  \} catch \(cfgErr\) \{/  try {
    if (false) o1RegisterAckBody_("P000");
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
echo "────────────────────────────────────────"
echo "  変異: 赤になった $PASS 件 / 緑のままだった $FAIL 件"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ 検査は空回りしていない（全変異が捕まった）。"
else
  echo "  ❌ ⚠️ 上の変異は検査をすり抜けた。★ ケースを足すこと。"
fi
echo "────────────────────────────────────────"
[ "$FAIL" -eq 0 ]
