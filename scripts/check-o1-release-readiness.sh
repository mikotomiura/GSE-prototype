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
FORM_BUILDER="Form_G1/GSE_O1_Form_Builder.gs"
FORM_BUILDER_TEST="Form_G1/o1_form_builder_test.cjs"
SYNC_GUARD_TEST="scripts/sync_session_o1_guard_test.sh"
MEASURE="experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md"

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

# ★★ 2026-08-28: **ファイルの存在だけを見る検査から、ガード検査の実行に差し替えた**
#   （旧版のコメントが「フォームを作る人は本チェックを差し替えること」と指示していたもの）。
#   ⚠️ 存在だけを見ていた頃は**空ファイルでも緑になった**。
#   ★ いま見ているのは「G1 のフォームを壊さないか」「被験者への約束を破っていないか」である。
if [ ! -s "$FORM_BUILDER" ]; then
  ng "O1 のフォーム類が無い（参加登録・P-ID 採番・受付メール・終了後アンケート）"
elif [ ! -f "$FORM_BUILDER_TEST" ]; then
  ng "O1 フォームビルダーのガード検査が無い: $FORM_BUILDER_TEST"
elif ! command -v node > /dev/null 2>&1; then
  ng "node が無いので O1 フォームビルダーのガード検査を実行できない"   # ⚠️ 飛ばさず赤にする
else
  out=$(node "$FORM_BUILDER_TEST" "$FORM_BUILDER" 2>&1); rc=$?
  n=$(printf '%s\n' "$out" | sed -n 's/^全 \([0-9]*\) ケース期待どおり$/\1/p' | tail -1)
  if [ "$rc" -eq 0 ]; then
    ok "O1 のフォームビルダーがあり、ガード検査が緑（${n:-件数不明} ケース）"
  else
    ng "O1 フォームビルダーのガード検査が赤"
    printf '%s\n' "$out" | grep '^NG' | sed 's/^/       /'   # ★ 原因を画面に出す
  fi
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
if [ "$sync_ok" -ne 1 ]; then
  ng "sync-session.sh / .ps1 に O1 を弾くガードが無い（★ 通すと削除が git 履歴の書き換えになる）"
elif [ ! -f "$SYNC_GUARD_TEST" ]; then
  # ⚠️★★ 2026-08-28: 旧版はここで緑にしていたが、それは「語が出てくる」しか見ていない。
  #   ★ **弾くことを示すテストを要求する**（旧版のコメントが自分で要求していたもの）。
  ng "O1 ガードの検査が無い: $SYNC_GUARD_TEST（⚠️ 語の存在だけでは弾く証拠にならない）"
else
  out=$(bash "$SYNC_GUARD_TEST" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then
    # ⚠️★ PowerShell の無い機械では .ps1 が**未実行**のまま緑になる。★ そのことを画面に出す。
    if printf '%s\n' "$out" | grep -q '未実行'; then
      ok "sync-session が O1 を実際に弾く（⚠️ ★ .ps1 は未実行。Windows で 1 回は走らせること）"
    else
      ok "sync-session.sh / .ps1 の両方が O1 を実際に弾く（★ 陽性対照つき）"
    fi
  else
    ng "sync-session の O1 ガードが弾いていない"
    printf '%s\n' "$out" | grep '❌' | sed 's/^/     /'
  fi
fi

# ★ 「マウスのみの作業で誤警告が出る」問題（2026-08-28 に実測）。
#   ⚠️ O1 の対象作業（図面 / 動画編集）では常態になる。
#   ⚠️★ **アンカー喪失を緑にしない**（code-reviewer 指摘）: `Thresholds::default()` が
#     改名・移動しただけで「別扱いになっている」に落ちるのを防ぐ。
# ⚠️★★ **定数があるだけでは緑にしない**（2026-08-28 に強化）。
#   ★ 旧版は `grep O1_LIVENESS` ただ 1 本だったので、**どこかに定数を 1 行足すだけ**で緑になった。
#   ⚠️ 定数が**トレイに配線されていなければ**、被験者の画面は 1 ミリも変わらない。
#   → ★ 目印（定数）と**配線**（`HOOK_STARVED` が O1 を見る純関数を通る）の**両方**を見る。
#   ⚠️★★ `HOOK_STARVED` の読み手は **2 つ**ある（トレイ ＋ アプリ内バッジ）。
#     ★ どちらも被験者向けなので、まとめて遅らせるのが意図である（`liveness.rs` の doc を見よ）。
#   ★ 純関数の実在はコンパイラが保証する（配線行が呼んでいるので、無ければ CI が赤くなる）。
if [ ! -f src-tauri/src/lib.rs ]; then
  ng "src-tauri/src/lib.rs が読めない（liveness 閾値を確かめられない）"
elif ! grep -q "O1_LIVENESS\|o1_liveness_thresholds" src-tauri/src/lib.rs; then
  if grep -q "Thresholds::default()" src-tauri/src/lib.rs; then
    ng "★ O1 で liveness の閾値が G1 と同じ（マウスのみ 2 分で「計測できていません」が出る）"
  else
    ng "liveness 閾値の目印（Thresholds::default）が見つからない（★ 移動/改名したら本検査を直す）"
  fi
elif ! grep -q "liveness::participant_visible_starved" src-tauri/src/lib.rs; then
  ng "★ O1 の閾値の目印はあるが、被験者に見える表示（HOOK_STARVED）に配線されていない"
else
  ok "O1 の liveness 閾値が別扱いになっている（★ 被験者に見える表示への配線まで確認）"
fi

# ⚠️★★★ 転送路の実力（code-reviewer 指摘・2026-08-28）。
#   ★ 受け口の MAX_BYTES を上げても、送信側が運べなければ届かない。
#     `reconcile.rs` の timeout は **180 秒固定**、実測は 300KB/1.45s ≒ 207KB/s。
#     → 実測の 1 日ぶん 18MB でも base64 24MB ≒ 116 秒＝ timeout の 2/3。
#     ⚠️ しかもこの実測は **Drive 保存時間を含まない**。
#
# ⚠️★★★ **旧版の検査は `grep from_secs(180)` ただ 1 本だった**（2026-08-28 に差し替え）。
#   ★ それだと **数字を書き換えるだけで緑になる** ——
#   ⚠️ 実測しないまま緑にできる検査は、本リポジトリがいちばん嫌う「**見えないまま緑**」を
#   **ゲート自身**に作る。→ ★ **実測の記録**と**コードの修正**の**両方**でだけ緑にする。
#   ★ 記録票は `<!-- gate:o1-upload-timeout -->` の直後のブロックだけを読む
#   （⚠️ 同じ文書の「記入例」を誤って拾わないため）。
measure_block=""
[ -f "$MEASURE" ] && measure_block=$(sed -n '/<!-- gate:o1-upload-timeout -->/,/^$/p' "$MEASURE")
# ★ 記録票の 1 欄が埋まっているか。⚠️ 空欄の目印（（未記入））は `[^（*]` で弾く。
mfield () { printf '%s\n' "$measure_block" | grep -qE "$1"; }
if [ ! -f "$MEASURE" ]; then
  ng "★ 送信 timeout の実測記録票が無い: $MEASURE（★ .gs 手順 8 の「1 日ぶんの通し確認」）"
elif ! mfield '^- 状態: \*\*実測済み\*\*$'; then
  ng "★ 送信 timeout が未実測（記録票の「状態」が「実測済み」でない。★ .gs 手順 8 を実施すること）"
elif ! mfield '^- 実測日: \*\*[0-9]{4}-[0-9]{2}-[0-9]{2}\*\*$' \
  || ! mfield '^- 送信バイト数 \(base64 後\): \*\*[^*]*[0-9][^*]*\*\*$' \
  || ! mfield '^- 所要時間 \(Drive 保存を含む\): \*\*[^*]*[0-9][^*]*\*\*$' \
  || ! mfield '^- 実効スループット: \*\*[^*]*[0-9][^*]*\*\*$' \
  || ! mfield '^- 採用した timeout: \*\*[^*]*[0-9][^*]*\*\*$'; then
  # ⚠️★ 値に **数字を 1 つ以上**要求する（code-reviewer LOW・2026-08-28）。
  #   ★ そうしないと `**未定**` や `** **` が「埋まっている」として通る。
  ng "★ 実測記録票の必須欄が埋まっていない（実測日 / 送信バイト数 / 所要時間 / 実効スループット / 採用した timeout）"
elif [ ! -f src-tauri/src/reconcile.rs ]; then
  # ⚠️★★ **アンカー喪失を緑にしない**（code-reviewer MEDIUM・2026-08-28）。
  #   ★ 旧版は `grep -q ... 2>/dev/null` だけだったので、⚠️ **ファイルが消えても偽 → `else` → ✅**
  #     になった（★ liveness 側では同じ穴を塞いでいるのに、ここだけ空いていた）。
  ng "★ src-tauri/src/reconcile.rs が読めない（★ 移動/改名したら本検査を直す）"
elif grep -q "from_secs(180)" src-tauri/src/reconcile.rs; then
  ng "★ 実測は記録されたのに送信 timeout が 180 秒固定のまま（★ 記録票の「採用した timeout」を反映すること）"
else
  ok "送信 timeout が実測にもとづいて見直されている"
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
    # ★ フォームビルダーとその検査。⚠️ 検査は G1 のビルダー（拒否リストの突き合わせ）と
    #   同意文書（連絡先の突き合わせ）も読むので、**3 つとも**写す。
    cp "$repo/$FORM_BUILDER" "$repo/$FORM_BUILDER_TEST" \
       "$repo/Form_G1/GSE_G1_Form_Builder.gs" "$fix/w/Form_G1/" 2>/dev/null
    cp "$repo/$SYNC_GUARD_TEST" "$fix/w/scripts/" 2>/dev/null
    cp "$repo/$CONSENT" "$fix/w/$CONSENT" 2>/dev/null
    cp "$repo/scripts/sync-session.sh" "$fix/w/scripts/" 2>/dev/null
    cp "$repo/scripts/sync-session.ps1" "$fix/w/scripts/" 2>/dev/null
    cp "$repo/experiments/20260801-controlled-friction-task/make-distribution.sh" \
       "$repo/experiments/20260801-controlled-friction-task/make-common-app-zip.sh" \
       "$fix/w/experiments/20260801-controlled-friction-task/" 2>/dev/null
    # ⚠️★★ **本物の `lib.rs` を写す**（2026-08-28 に差し替え）。
    #   ★ 以前はスタブ 1 行だったので、liveness の検査は「未達を満たすと緑になるか」しか
    #   測れなかった。⚠️ いまは repo 側が緑なので、**壊すと赤になるか**を測る側へ移す。
    cp "$repo/src-tauri/src/lib.rs" "$fix/w/src-tauri/src/lib.rs" 2>/dev/null
    printf 'x\n.timeout(std::time::Duration::from_secs(180))\n' > "$fix/w/src-tauri/src/reconcile.rs"
    cp "$repo/$MEASURE" "$fix/w/$MEASURE" 2>/dev/null
    cons="$fix/w/$CONSENT"
  }

  # ★ 実測記録票を「実測済み」で埋める（⚠️ **selftest の中だけ**。本物は 1 バイトも触らない）。
  fill_measure () {
    sed -i \
      -e 's/^- 状態: \*\*未実施\*\*$/- 状態: **実測済み**/' \
      -e 's/^- 実測日: \*\*（未記入）\*\*$/- 実測日: **2026-09-01**/' \
      -e 's/^- 送信バイト数 (base64 後): \*\*（未記入）\*\*$/- 送信バイト数 (base64 後): **24 MB**/' \
      -e 's/^- 所要時間 (Drive 保存を含む): \*\*（未記入）\*\*$/- 所要時間 (Drive 保存を含む): **210 秒**/' \
      -e 's/^- 実効スループット: \*\*（未記入）\*\*$/- 実効スループット: **117 KB\/s**/' \
      -e 's/^- 採用した timeout: \*\*（未記入）\*\*$/- 採用した timeout: **固定 900 秒**/' \
      "$fix/w/$MEASURE"
  }
  # ★ 送信側を実測にもとづいて直した状態（= 180 秒固定でなくなった）。
  fix_timeout () {
    printf 'x\n.timeout(std::time::Duration::from_secs(900))\n' > "$fix/w/src-tauri/src/reconcile.rs"
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
  build; sed -i 's/^<!-- o1-retention: set -->$//' "$fix/w/docs/o1-deletion-ledger.md"; expect_red "マーカ.*が見つからない" "保管上限マーカの喪失"
  build; rm -f "$fix/w/Form_G1/GSE_O1_Submit.gs";                              expect_red "受け口が無い" "受け口の欠落"
  build; sed -i "s/^var MAX_BYTES/var SHARED_SECRET = 'abcdefghijklmnopqrstuvwxyz012345';\nvar MAX_BYTES/" "$fix/w/Form_G1/GSE_O1_Submit.gs"; expect_red "直書きされている" ".gs への秘密直書き"
  build; sed -i 's/_o1day/_block/' "$fix/w/Form_G1/GSE_O1_Submit.gs";          expect_red "ガード検査が赤" "受け口の名前ガード"
  build; rm -f "$fix/w/Form_G1/o1_submit_guard_test.cjs";                      expect_red "ガード検査が無い" "ガード検査の欠落"
  build; echo 'let th = SomethingElse::new();' > "$fix/w/src-tauri/src/lib.rs"; expect_red "目印.*が見つからない" "liveness アンカーの喪失"
  # ⚠️★★ **O1 の目印を消したら赤になること**（★ 2026-08-28 に緑になったので satisfy 側から移した）。
  build; sed -i 's/O1_LIVENESS_TRAY_AFTER_MS/RENAMED_AWAY_/g' "$fix/w/src-tauri/src/lib.rs"; expect_red "G1 と同じ" "O1 の liveness の目印の喪失"
  # ⚠️★★★ **定数が残っていても、配線が消えたら赤になること**（★ 被験者の画面は配線でしか変わらない）。
  build; sed -i 's/liveness::participant_visible_starved/liveness::NOT_WIRED_/g' "$fix/w/src-tauri/src/lib.rs"; expect_red "配線されていない" "liveness の配線の喪失"
  # ★ 実測記録票そのものが消えたら、⚠️「未実測」ではなく**票が無い**と言うこと（★ 原因が違う）。
  build; rm -f "$fix/w/$MEASURE";                                              expect_red "実測記録票が無い" "実測記録票の喪失"
  # ⚠️★★ **アンカー喪失を緑にしない**（★ 記録票を埋めた後に顕在化する穴だった）。
  build; fill_measure; rm -f "$fix/w/src-tauri/src/reconcile.rs";              expect_red "reconcile.rs が読めない" "reconcile.rs のアンカー喪失"
  # ★★ 2026-08-28 に緑になった 3 件。⚠️ **緑になったものは selftest 2 から 1 へ移す**
  #   （satisfy 側に置いたままだと「もともと緑」を「満たしたから緑」と読み違える）。
  build; sed -i 's/^<!-- o1-retention: set -->$/<!-- o1-retention: unset -->/' "$fix/w/docs/o1-deletion-ledger.md"; expect_red "保管上限が未確定" "保管上限を未確定へ戻す"
  build; rm -f "$fix/w/Form_G1/GSE_O1_Form_Builder.gs";                        expect_red "フォーム類が無い" "フォームビルダーの欠落"
  build; rm -f "$fix/w/Form_G1/o1_form_builder_test.cjs";                      expect_red "ガード検査が無い" "フォームビルダーの検査の欠落"
  # ⚠️★★★ **中身を壊しても赤になること。** ★ 存在するだけで緑になっていた旧版の再発防止。
  build; sed -i 's/^var G1_FORM_IDS_DO_NOT_TOUCH = {$/var G1_FORM_IDS_DO_NOT_TOUCH = {}; var UNUSED_ = {/' "$fix/w/Form_G1/GSE_O1_Form_Builder.gs"; expect_red "フォームビルダーのガード検査が赤" "フォームビルダーの G1 拒否リスト"
  # ⚠️★ 行は**字下げされている**。`^` で固定すると変異が当たらず、
  #   ★ 「壊したつもりで壊れていない」偽の合格になる（2026-08-28 に実際に踏んだ）。
  build; sed -i 's|: > "$M/o1.mode"|: > "$M/DISABLED"|; s|: > "$W/o1.mode"|: > "$W/DISABLED"|'               "$fix/w/experiments/20260801-controlled-friction-task/make-common-app-zip.sh"; expect_red "o1.mode を置かない" "o1.mode の書き出しの喪失"
  build; rm -f "$fix/w/scripts/sync_session_o1_guard_test.sh";                 expect_red "O1 ガードの検査が無い" "sync ガードの検査の欠落"
  # ⚠️★★ **語だけ残してガードの実体を消しても赤になること**（★ 旧版はここを緑にしていた）。
  build; sed -i 's/^    exit 4$/    return 0/' "$fix/w/scripts/sync-session.sh";  expect_red "弾いていない" "sync ガードが弾かなくなる"

  echo
  echo "=== selftest 2: 未達を満たすと緑に変わるか（★ 陽性対照）==="
  # ⚠️★★★ **実測の記録とコードの修正が「両方そろって」初めて緑にする。**
  #   ★ 旧版は `grep from_secs(180)` ただ 1 本だったので、**数字を書き換えるだけで緑**になった。
  #   ★ liveness の陽性対照は selftest 1（壊すと赤）へ移した（= repo 側が緑になったため）。
  build; fill_measure; fix_timeout; expect_green "実測にもとづいて見直されている" "送信 timeout（実測 ＋ 修正）"

  echo
  echo "=== selftest 3: 片方だけでは緑にしない（★ 部分的な修正で騙されないか）==="
  # ⚠️★★ Windows が O1 の主ターゲットである。★ `.ps1` だけ壊れていても**必ず赤にする**
  #   （片方だけ見ていると、もう片方の OS から O1 が dataset へ漏れる）。
  build; sed -i 's/gse_o1_/gse_XX_/g' "$fix/w/scripts/sync-session.ps1"; expect_red "sync-session" "ps1 だけ壊しても赤になる"
  build; sed -i 's/gse_o1_/gse_XX_/g' "$fix/w/scripts/sync-session.sh";  expect_red "sync-session" "sh だけ壊しても赤になる"
  # ⚠️★★★ **A-2 の肝**: 片方だけでは緑にしない（★「見えないまま緑」への抜け道を塞ぐ）。
  build; fix_timeout;   expect_red "未実測"           "コードだけ直しても赤になる（実測が無い）"
  build; fill_measure;  expect_red "180 秒固定のまま" "記録だけ埋めても赤になる（コードが古い）"
  # ★「状態」だけ実測済みにして必須欄が空なら赤（⚠️ 中身の無い記録で緑にしない）。
  build; sed -i 's/^- 状態: \*\*未実施\*\*$/- 状態: **実測済み**/' "$fix/w/$MEASURE"; fix_timeout; expect_red "必須欄が埋まっていない" "必須欄が空なら赤になる"

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
