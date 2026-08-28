#!/usr/bin/env bash
# check-o1-release-readiness.sh — ★ O1 (R3-a) を**被験者に配る前**に通すゲート。
#
# ============================================================================
# ⚠️★★★ このゲートは **今は赤いのが正しい。**
# ============================================================================
#   ★ O1 の配備インフラは未完である。★ 本スクリプトの役目は
#     「何が残っているか」を**人の記憶ではなく機械に持たせる**ことである。
#   ⚠️ 緑になるまで被験者を 1 人も走らせない。
#
#   ★ なぜ要るか: 2026-08-27 に dev が `Form_G1/README.md` の古い記述だけを見て
#     「GAS 受け口は未作成」「通し確認は未実施」と**誤報した**（どちらも済んでいた）。
#     → ⚠️ **文書は実体ではない。** ★ 実体を毎回見に行くものを置く。
#
# 使い方:
#   bash scripts/check-o1-release-readiness.sh
#   bash scripts/check-o1-release-readiness.sh --selftest   # ★ ゲート自身を 3 状態で試す
#
# 終了コード: 0 = 配布してよい / 1 = まだ配れない
#
# ⚠️ Windows では git-bash から実行すること（PowerShell では動かない）。

set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"

PASS=0; FAIL=0
ok()   { echo "  ✅ $*"; PASS=$((PASS+1)); }
ng()   { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
head_() { echo; echo "[$1] $2"; }

CONSENT=".steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md"
LEDGER="docs/o1-deletion-ledger.md"
RECEIVER="Form_G1/GSE_O1_Submit.gs"
RECEIVER_TEST="Form_G1/o1_submit_guard_test.cjs"

# --- 1. 同意文書 -------------------------------------------------------------
head_ 1 "同意文書（★ 被験者への約束の正本の元）"
if [ ! -f "$CONSENT" ]; then
  ng "同意文書が無い: $CONSENT"
else
  # ⚠️ 空欄のまま配ると、被験者は問い合わせ先を知らないまま常時記録に同意することになる。
  if grep -q "（実施前に記入）" "$CONSENT"; then
    ng "同意文書に未記入の欄が残っている（『（実施前に記入）』）"
  else
    ok "同意文書に未記入の欄が無い"
  fi
  # ★ 連絡先が実体として入っていること（★ 空文字や記号だけを通さない）。
  if grep -qE '^- 連絡先: \*\*[^*（ ]+@[^*（ ]+\*\*$' "$CONSENT"; then
    ok "連絡先にメールアドレスが入っている"
  else
    ng "連絡先が埋まっていない"
  fi
  if grep -qE '^- 所属: \*\*[^*（ ]+\*\*$' "$CONSENT"; then
    ok "所属が入っている"
  else
    ng "所属が埋まっていない"
  fi
fi

# --- 2. 削除台帳（ADR-014 D8 制約 3 / 実装 acceptance 3）----------------------
head_ 2 "削除台帳（⚠️ 欠けると ADR-014 判断 O1-2 が成立しない）"
if [ ! -f "$LEDGER" ]; then
  ng "削除台帳が無い: $LEDGER"
else
  ok "削除台帳がある: $LEDGER"
  # ⚠️★ 保管上限は ADR-014 D8 制約 3 が**名指しで**要求している。
  #   ★ 空欄のまま配ると同意文書 §5 の逐語「保管の上限…は台帳に記録します」が嘘になる。
  if grep -q "⚠️ \*\*未確定\*\*" "$LEDGER"; then
    ng "削除台帳の保管上限が未確定のまま（★ 数値を入れること）"
  else
    ok "削除台帳の保管上限が埋まっている"
  fi
fi

# --- 3. 提出の受け口 ---------------------------------------------------------
head_ 3 "O1 の提出受け口（GAS doPost）"
if [ ! -f "$RECEIVER" ]; then
  ng "受け口が無い: $RECEIVER"
else
  ok "受け口がある: $RECEIVER"
  # ⚠️★ 秘密を .gs に直書きしていないこと（repo は一時 public にする運用がある）。
  if grep -qE "(SHARED_SECRET|FOLDER_ID)[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" "$RECEIVER"; then
    ng "★ 受け口の .gs にシークレット / フォルダ ID が直書きされている"
  else
    ok "受け口の .gs に秘密が直書きされていない"
  fi
  if [ ! -f "$RECEIVER_TEST" ]; then
    ng "受け口のガード検査が無い: $RECEIVER_TEST"
  elif ! command -v node > /dev/null 2>&1; then
    # ⚠️ ★ 飛ばさず赤にする（「node が無いから通した」を作らない）。
    ng "node が無いので受け口のガード検査を実行できない"
  else
    out=$(node "$RECEIVER_TEST" 2>&1); rc=$?
    n=$(printf '%s\n' "$out" | sed -n 's/^全 \([0-9]*\) ケース期待どおり$/\1/p' | tail -1)
    if [ "$rc" -eq 0 ]; then
      ok "受け口のガード検査が緑（${n:-件数不明} ケース）"
    else
      ng "受け口のガード検査が赤"
    fi
  fi
fi

# --- 4. ⚠️ まだ作っていないもの（★ 未着手を機械に持たせる）--------------------
head_ 4 "⚠️ 配備インフラ（★ ここが赤いあいだは被験者を走らせない）"

# ★ O1 のフォーム類（参加登録 / 終了後アンケート）。⚠️ 現在 0 件。
if ls Form_G1/GSE_O1_Form_Builder.gs > /dev/null 2>&1; then
  ok "O1 のフォームビルダーがある"
else
  ng "O1 のフォーム類が無い（参加登録・P-ID 採番・受付メール・終了後アンケート）"
fi

# ★ 配布物に o1.mode を置く経路。⚠️ 現在は g1.mode しか置いていない。
if grep -rqlE '(^|[^a-z])o1\.mode' experiments/20260801-controlled-friction-task/make-distribution.sh \
     experiments/20260801-controlled-friction-task/make-common-app-zip.sh 2>/dev/null; then
  ok "配布スクリプトが o1.mode を置く"
else
  ng "配布スクリプトが o1.mode を置かない（★ 対象は make-distribution.sh / make-common-app-zip.sh）"
fi

# ⚠️★★★ O1 を gse-dataset へ出さないガード。
#   ★ 実測（2026-08-28）: sync-session.* に O1 の記述は 0 件で、gse-dataset の
#     metrics/ は追跡・push されている。→ 通すと削除が git 履歴の書き換えになる。
# ⚠️★ このチェックの限界を隠さない: 見ているのは「`gse_o1_` という語が出てくるか」だけで、
#   ★ **実際に弾くかどうかは測っていない**（sync-session.sh は dataset と gse-replay を要求するので
#   ここから実行できない）。⚠️ コメントに書くだけでも緑になる。
#   → ★ ガードを入れる人は、**弾くことを示すテストを一緒に置くこと**。
if grep -q 'gse_o1_' scripts/sync-session.sh 2>/dev/null; then
  ok "sync-session.sh が gse_o1_ に言及している（⚠️ 弾くことまでは測っていない）"
else
  ng "sync-session.sh に O1 を弾くガードが無い（★ 通すと削除が git 履歴の書き換えになる）"
fi

# ★ 「マウスのみの作業で誤警告が出る」問題（2026-08-28 に実測）。
#   ⚠️ O1 の対象作業（図面 / 動画編集）では常態になる。
if grep -q "Thresholds::default()" src-tauri/src/lib.rs 2>/dev/null && \
   ! grep -q "o1_liveness_thresholds\|O1_LIVENESS" src-tauri/src/lib.rs 2>/dev/null; then
  ng "★ O1 で liveness の閾値が G1 と同じ（マウスのみ 2 分で「計測できていません」が出る）"
else
  ok "O1 の liveness 閾値が別扱いになっている"
fi

# --- 出力 -------------------------------------------------------------------
echo
echo "────────────────────────────────────────"
echo "  通過 $PASS 件 / 未達 $FAIL 件"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ O1 を配布してよい状態です。"
  exit 0
fi
echo "  ❌ ⚠️ まだ配れません。上の ❌ を全部消すこと。"
echo "────────────────────────────────────────"
exit 1
