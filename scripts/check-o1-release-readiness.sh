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
#   bash scripts/check-o1-release-readiness.sh --selftest   # ★ ゲート自身を壊して赤になるか測る
#
# 終了コード: 0 = 配布してよい / 1 = まだ配れない / 2 = 引数が不正
#
# ⚠️ Windows では git-bash から実行すること（PowerShell では動かない）。

set -uo pipefail

MODE=main
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) MODE=selftest; shift ;;
    -h|--help)  sed -n '1,22p' "$0"; exit 0 ;;
    # ⚠️ ★ 知らない引数を**黙って無視しない**。無視すると `--selftst` の打ち間違いが
    #   「通常のゲートが緑だった」に化ける（★ 本スクリプトが戒めている silent pass そのもの）。
    *) echo "知らない引数: $1" >&2; exit 2 ;;
  esac
done

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
cd "$(dirname "$0")/.." || { echo "リポジトリ直下へ移動できません" >&2; exit 1; }

PASS=0; FAIL=0
ok()    { echo "  ✅ $*"; PASS=$((PASS+1)); }
ng()    { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
head_() { echo; echo "[$1] $2"; }

CONSENT=".steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md"
LEDGER="docs/o1-deletion-ledger.md"
RECEIVER="Form_G1/GSE_O1_Submit.gs"
RECEIVER_TEST="Form_G1/o1_submit_guard_test.cjs"

run_checks () {

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
  # ⚠️★★ 状態表が本文より古くなる事故を捕まえる（★ security-checker / code-reviewer が一致して指摘）。
  #   ★ 本ゲートを作った動機（古い記述による誤報）が、同じ文書の中で再発していた。
  if grep -q '⚠️ \*\*未了' "$CONSENT"; then
    ng "同意文書の状態表に『⚠️ **未了』が残っている（★ 本文と食い違っていないか確かめる）"
  else
    ok "同意文書の状態表に未了が残っていない"
  fi
fi

# --- 2. 削除台帳（ADR-014 D8 制約 3 / 実装 acceptance 3）----------------------
head_ 2 "削除台帳（⚠️ 欠けると ADR-014 判断 O1-2 が成立しない）"
if [ ! -f "$LEDGER" ]; then
  ng "削除台帳が無い: $LEDGER"
else
  ok "削除台帳がある: $LEDGER"
  # ⚠️★ 散文を grep すると表記ゆれで空回りする（security-checker 指摘）。
  #   → ★ **機械可読マーカ**で判定する。埋めた人はこの行を `set` に変える。
  if grep -q '^<!-- o1-retention: set -->$' "$LEDGER"; then
    ok "削除台帳の保管上限が埋まっている"
  elif grep -q '^<!-- o1-retention: unset -->$' "$LEDGER"; then
    ng "削除台帳の保管上限が未確定のまま（★ §5 を埋めてマーカを set にする）"
  else
    # ⚠️ ★ マーカ自体が消えたら**緑にしない**（アンカー喪失を赤にする）。
    ng "削除台帳の保管上限マーカ（o1-retention）が見つからない"
  fi
fi

# --- 3. 提出の受け口 ---------------------------------------------------------
head_ 3 "O1 の提出受け口（GAS doPost）"
if [ ! -f "$RECEIVER" ]; then
  ng "受け口が無い: $RECEIVER"
else
  ok "受け口がある: $RECEIVER"
  if grep -qE "(SHARED_SECRET|FOLDER_ID)[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" "$RECEIVER"; then
    ng "★ 受け口の .gs にシークレット / フォルダ ID が直書きされている"
  else
    ok "受け口の .gs に秘密が直書きされていない"
  fi
  if [ ! -f "$RECEIVER_TEST" ]; then
    ng "受け口のガード検査が無い: $RECEIVER_TEST"
  elif ! command -v node > /dev/null 2>&1; then
    ng "node が無いので受け口のガード検査を実行できない"   # ⚠️ 飛ばさず赤にする
  else
    out=$(node "$RECEIVER_TEST" 2>&1); rc=$?
    n=$(printf '%s\n' "$out" | sed -n 's/^全 \([0-9]*\) ケース期待どおり$/\1/p' | tail -1)
    if [ "$rc" -eq 0 ]; then
      ok "受け口のガード検査が緑（${n:-件数不明} ケース）"
    else
      ng "受け口のガード検査が赤"
      printf '%s\n' "$out" | grep '^NG' | sed 's/^/       /'   # ★ 原因を画面に出す
    fi
  fi
fi

# --- 4. ⚠️ まだ作っていないもの（★ 未着手を機械に持たせる）--------------------
head_ 4 "⚠️ 配備インフラ（★ ここが赤いあいだは被験者を走らせない）"

# ⚠️★ 限界を隠さない: ここは**ファイルの存在**しか見ていない。空ファイルでも緑になる。
#   → ★ フォームを作る人は、ガード検査を併せて置き、本チェックをそれに差し替えること。
if [ -s Form_G1/GSE_O1_Form_Builder.gs ] 2>/dev/null; then
  ok "O1 のフォームビルダーがある（⚠️ 中身の妥当性は測っていない）"
else
  ng "O1 のフォーム類が無い（参加登録・P-ID 採番・受付メール・終了後アンケート）"
fi

# ⚠️★ 限界: **書き込み文**を要求する（コメントに `o1.mode` と書くだけでは緑にしない）。
if grep -rqE '>[[:space:]]*"?\$[A-Za-z_]+/o1\.mode"?' \
     experiments/20260801-controlled-friction-task/make-distribution.sh \
     experiments/20260801-controlled-friction-task/make-common-app-zip.sh 2>/dev/null; then
  ok "配布スクリプトが o1.mode を書き出す"
else
  ng "配布スクリプトが o1.mode を置かない（★ 対象は make-distribution.sh / make-common-app-zip.sh）"
fi

# ⚠️★★★ O1 を gse-dataset へ出さないガード。
#   ★ 実測（2026-08-28）: sync-session.* に O1 の記述は 0 件で、gse-dataset の
#     metrics/ は追跡・push されている（34 件）。→ 通すと削除が git 履歴の書き換えになる。
#   ⚠️ 限界: 見ているのは「`gse_o1_` という語が出てくるか」だけで、**実際に弾くかは測っていない**
#     （sync-session は dataset と gse-replay を要求するのでここから実行できない）。
#   ★ ガードを入れる人は、弾くことを示すテストを一緒に置くこと。
#   ⚠️★ **両方**を要求する（片方だけ直して緑になると、もう片方から漏れる。Windows が主ターゲット）。
sync_ok=1
for f in scripts/sync-session.sh scripts/sync-session.ps1; do
  [ -f "$f" ] || { sync_ok=0; break; }
  grep -q 'gse_o1_' "$f" || sync_ok=0
done
if [ "$sync_ok" -eq 1 ]; then
  ok "sync-session.sh / .ps1 の両方が gse_o1_ に言及している（⚠️ 弾くことまでは測っていない）"
else
  ng "sync-session.sh / .ps1 に O1 を弾くガードが無い（★ 通すと削除が git 履歴の書き換えになる）"
fi

# ★ 「マウスのみの作業で誤警告が出る」問題（2026-08-28 に実測）。
#   ⚠️ O1 の対象作業（図面 / 動画編集）では常態になる。
#   ⚠️★ **アンカー喪失を緑にしない**（code-reviewer 指摘）: `Thresholds::default()` が
#     改名・移動しただけで「別扱いになっている」に落ちるのを防ぐ。
if [ ! -f src-tauri/src/lib.rs ]; then
  ng "src-tauri/src/lib.rs が読めない（liveness 閾値を確かめられない）"
elif grep -q "O1_LIVENESS\|o1_liveness_thresholds" src-tauri/src/lib.rs; then
  ok "O1 の liveness 閾値が別扱いになっている"
elif grep -q "Thresholds::default()" src-tauri/src/lib.rs; then
  ng "★ O1 で liveness の閾値が G1 と同じ（マウスのみ 2 分で「計測できていません」が出る）"
else
  ng "liveness 閾値の目印（Thresholds::default）が見つからない（★ 移動/改名したら本検査を直す）"
fi

# ⚠️★★★ 転送路の実力（code-reviewer 指摘・2026-08-28）。
#   ★ 受け口の MAX_BYTES を上げても、送信側が運べなければ届かない。
#     `reconcile.rs` の timeout は **180 秒固定**、実測は 300KB/1.45s ≒ 207KB/s。
#     → 実測の 1 日ぶん 18MB でも base64 24MB ≒ 116 秒＝ timeout の 2/3。
#     ⚠️ しかもこの実測は **Drive 保存時間を含まない**。
if grep -q "from_secs(180)" src-tauri/src/reconcile.rs 2>/dev/null; then
  ng "★ 送信 timeout が 180 秒固定のまま（★ 1 日ぶんが入りきるか未実測。.gs 手順 8 を実施すること）"
else
  ok "送信 timeout が見直されている"
fi

}

# =============================================================================
# ★ selftest — ⚠️ **ゲート自身が空回りしていないか**を測る（`verify-before-claiming` 5b）
# =============================================================================
#   ★ 検査対象のファイルを一時ディレクトリへ写し、**✅ を 1 つずつ壊して赤になるか**、
#     ⚠️ 逆に**未達を満たすと緑に変わるか**を実際に実行して確かめる。
#   ⚠️ 本物のリポジトリは 1 バイトも変更しない。
selftest () {
  local repo fix cons rc out
  repo="$(pwd)"
  fix="$(mktemp -d)"
  trap 'rm -rf "$fix"' RETURN

  build () {
    rm -rf "${fix:?}/w"
    mkdir -p "$fix/w/scripts" "$fix/w/docs" "$fix/w/Form_G1" \
             "$fix/w/$(dirname "$CONSENT")" \
             "$fix/w/experiments/20260801-controlled-friction-task" "$fix/w/src-tauri/src"
    cp "$SCRIPT_PATH" "$fix/w/scripts/gate.sh"
    cp "$repo/$LEDGER" "$fix/w/docs/" 2>/dev/null
    cp "$repo/$RECEIVER" "$repo/$RECEIVER_TEST" "$fix/w/Form_G1/" 2>/dev/null
    cp "$repo/$CONSENT" "$fix/w/$CONSENT" 2>/dev/null
    cp "$repo/scripts/sync-session.sh" "$fix/w/scripts/" 2>/dev/null
    cp "$repo/scripts/sync-session.ps1" "$fix/w/scripts/" 2>/dev/null
    cp "$repo/experiments/20260801-controlled-friction-task/make-distribution.sh" \
       "$repo/experiments/20260801-controlled-friction-task/make-common-app-zip.sh" \
       "$fix/w/experiments/20260801-controlled-friction-task/" 2>/dev/null
    echo 'let th = Thresholds::default();' > "$fix/w/src-tauri/src/lib.rs"
    printf 'x\n.timeout(std::time::Duration::from_secs(180))\n' > "$fix/w/src-tauri/src/reconcile.rs"
    cons="$fix/w/$CONSENT"
  }

  local sp=0 sf=0
  # $1 = 赤くなるはずの行に含まれる語 / $2 = 説明
  expect_red () {
    out=$(bash "$fix/w/scripts/gate.sh" 2>&1)
    if printf '%s\n' "$out" | grep -E '^  ❌' | grep -q -- "$1"; then
      echo "  ✅ 壊すと赤になる: $2"; sp=$((sp+1))
    else
      echo "  ❌ 壊しても緑のまま: $2"; sf=$((sf+1))
    fi
  }
  # $1 = 緑になるはずの行に含まれる語 / $2 = 説明
  expect_green () {
    out=$(bash "$fix/w/scripts/gate.sh" 2>&1)
    if printf '%s\n' "$out" | grep -E '^  ✅' | grep -q -- "$1"; then
      echo "  ✅ 満たすと緑になる: $2"; sp=$((sp+1))
    else
      echo "  ❌ 満たしても赤のまま: $2"; sf=$((sf+1))
    fi
  }

  echo "=== selftest 1: ✅ を 1 つずつ壊す（★ 赤にならなければゲートが空回りしている）==="
  build; sed -i 's/^- 所属: \*\*.*\*\*$/- 所属: **（実施前に記入）**/' "$cons"; expect_red "同意文書に未記入" "同意文書の空欄"
  build; sed -i 's/^- 連絡先: .*/- 連絡先: **（未定）**/' "$cons";             expect_red "連絡先が埋まっていない" "連絡先"
  build; sed -i 's/^- 所属: \*\*.*\*\*$/- 所属: **/' "$cons";                  expect_red "所属が埋まっていない" "所属"
  build; printf '\n| x | ⚠️ **未了: なにか** | y |\n' >> "$cons";              expect_red "未了" "状態表の未了残置"
  build; rm -f "$fix/w/docs/o1-deletion-ledger.md";                            expect_red "削除台帳が無い" "削除台帳の欠落"
  build; sed -i 's/^<!-- o1-retention: unset -->$//' "$fix/w/docs/o1-deletion-ledger.md"; expect_red "マーカ.*が見つからない" "保管上限マーカの喪失"
  build; rm -f "$fix/w/Form_G1/GSE_O1_Submit.gs";                              expect_red "受け口が無い" "受け口の欠落"
  build; sed -i "s/^var MAX_BYTES/var SHARED_SECRET = 'abcdefghijklmnopqrstuvwxyz012345';\nvar MAX_BYTES/" "$fix/w/Form_G1/GSE_O1_Submit.gs"; expect_red "直書きされている" ".gs への秘密直書き"
  build; sed -i 's/_o1day/_block/' "$fix/w/Form_G1/GSE_O1_Submit.gs";          expect_red "ガード検査が赤" "受け口の名前ガード"
  build; rm -f "$fix/w/Form_G1/o1_submit_guard_test.cjs";                      expect_red "ガード検査が無い" "ガード検査の欠落"
  build; echo 'let th = SomethingElse::new();' > "$fix/w/src-tauri/src/lib.rs"; expect_red "目印.*が見つからない" "liveness アンカーの喪失"

  echo
  echo "=== selftest 2: 未達を満たすと緑に変わるか（★ 陽性対照）==="
  build; sed -i 's/^<!-- o1-retention: unset -->$/<!-- o1-retention: set -->/' "$fix/w/docs/o1-deletion-ledger.md"; expect_green "保管上限が埋まっている" "保管上限"
  build; echo '# gse_o1_ は同期しない' >> "$fix/w/scripts/sync-session.sh"
         echo '# gse_o1_ は同期しない' >> "$fix/w/scripts/sync-session.ps1"; expect_green "sync-session" "sync-session の両方"
  build; echo 'x' > "$fix/w/Form_G1/GSE_O1_Form_Builder.gs";                 expect_green "フォームビルダーがある" "フォームビルダー"
  build; echo ': > "$M/o1.mode"' >> "$fix/w/experiments/20260801-controlled-friction-task/make-distribution.sh"; expect_green "o1.mode を書き出す" "o1.mode の書き出し"
  build; echo 'const O1_LIVENESS: u64 = 1;' >> "$fix/w/src-tauri/src/lib.rs"; expect_green "別扱いになっている" "liveness の別扱い"
  build; printf 'x\n.timeout(std::time::Duration::from_secs(600))\n' > "$fix/w/src-tauri/src/reconcile.rs"; expect_green "timeout が見直されている" "送信 timeout"

  echo
  echo "=== selftest 3: 片方だけでは緑にしない（★ 部分的な修正で騙されないか）==="
  build; echo '# gse_o1_ は同期しない' >> "$fix/w/scripts/sync-session.sh"; expect_red "sync-session" "sh だけ直しても赤のまま"

  echo
  echo "────────────────────────────────────────"
  echo "  selftest: 通過 $sp 件 / 失敗 $sf 件"
  if [ "$sf" -eq 0 ]; then
    echo "  ✅ ゲートの各検査は実際に発火している。"
    return 0
  fi
  echo "  ❌ ⚠️ 空回りしている検査がある。上の ❌ を直すこと。"
  return 1
}

if [ "$MODE" = selftest ]; then
  selftest; exit $?
fi

run_checks

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
