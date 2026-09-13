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
RECEIVER="Form_O1/GSE_O1_Submit.gs"
RECEIVER_TEST="Form_O1/o1_submit_guard_test.cjs"
FORM_BUILDER="Form_O1/GSE_O1_Form_Builder.gs"
FORM_BUILDER_TEST="Form_O1/o1_form_builder_test.cjs"
SYNC_GUARD_TEST="scripts/sync_session_o1_guard_test.sh"
MEASURE="experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md"
# ★ 収集仕様の自己記述（ADR-013 D1）。★ 6 択 ESM の計器が**この版に在るか**を見る。
CAPS="src-tauri/src/capabilities.rs"
# ★ 6 択 ESM の**送出元**（★ 呼ぶ側）。⚠️ writer（`logger.rs`）ではない。
EMITTER="src-tauri/src/lib.rs"

# ★ 秘密検出の**判定器**。⚠️★★ **トップレベルに置く**（2026-08-29 に実測で判明）:
#   `run_checks` の中に置くと `--selftest` からは**見えない**（★ selftest は `run_checks` を
#   呼ばないため）。⚠️ 見えないまま比較すると、**対照が常に失敗する / 常に通る**ことになる。
leak_name_hits () { grep -iE '(^|/)[go]1[-_]submit[^/]*\.json$' || true; }
# ⚠️ **実物の** Apps Script デプロイ ID（★ 40 文字以上）。
#   ★ プレースホルダを誤検知しない閾値: 本 repo の `DRYRUN_NOT_A_REAL_DEPLOYMENT` は **28 文字**、
#   実物は 57〜72 文字（★ 2026-08-29 に実測して 40 で分離できることを確認）。
leak_url_re='script\.google\.com/macros/s/[A-Za-z0-9_-]{40,}/exec'

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
  # ⚠️★★★ **計器と同意を機械で連動させる**（ADR-031 D1 / D5 保証 3・2026-09-14 追加）。
  #   ★ 6 択 ESM（`activity_label`）は**画面に問いを出す**ので、同意文書 §3 注 C の逐語
  #     「この記録では画面に何も出しません」を**破る**。
  #   → ★ **計器がこの版に在るなら、同意の ESM 追補が承認済みでなければ配れない。**
  #   ⚠️ 承認マーカ `<!-- o1-esm-consent: approved -->` は**研究者が入れる**
  #     （★ dev が案を書いただけでは緑にしない ＝ 承認の代理をさせない）。
  #
  # ⚠️★★★ **引き金は「送出元があるか」である**（2026-09-14 訂正・`/cross-review` HIGH）。
  #   ★ 初版は `capabilities.rs` に語が在るかを見ていたが、⚠️ **schema と writer が在っても
  #     呼ぶ側が無ければ 1 行も記録されない** —— ★ それを「計器がある」と読むと、
  #     **記録できない計器のためにゲートが赤くなる**（＝ 偽の赤）。
  #   ★ ADR-013 D2 の「導出元は *送出元があるか* であって writer ではない」と基準を揃える。
  if [ ! -f "$EMITTER" ]; then
    ng "送出元の判定対象が無い: ${EMITTER}（★ 計器と同意の連動を判定できない）"
  elif grep -qE 'activity_label_(answered|skipped)\(' "$EMITTER"; then
    # ⚠️★★★ **行頭完全一致で見る**（2026-09-14 に実測で踏んだ）。
    #   ★ 部分一致にすると、**dev メモの「承認したらこのマーカを入れること」という
    #     *説明文* 自体にヒットして緑になる**（= 承認していないのに配れてしまう）。
    if grep -qE '^<!-- o1-esm-consent: approved -->[[:space:]]*$' "$CONSENT"; then
      ok "6 択 ESM の送出元がある版で、同意の ESM 追補が承認済み"
    else
      ng "6 択 ESM の送出元があるのに同意の ESM 追補が未承認（★ 注 D ＋ 承認マーカを研究者が入れること）"
    fi
    # ⚠️★★★ **送出元があるなら、同意の門を通していなければならない**（ADR-031 M5）。
    #   ★ `o1::activity_label_allowed(o1_mode, consent_approved)` を経由せずに記録すると、
    #     **同意承認と実際の記録が結びつかない穴**になる（★ `/cross-review` の「テスト不足」）。
    if grep -q 'activity_label_allowed(' "$EMITTER"; then
      ok "6 択 ESM の記録が同意の門（activity_label_allowed）を通っている"
    else
      ng "6 択 ESM の送出元が同意の門を通っていない（★ o1::activity_label_allowed を経由すること）"
    fi
  else
    ok "6 択 ESM の送出元がまだ無い（★ 同意の ESM 追補は不要）"
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
    ng "★ 受け口の .gs に秘密が直書きされている（★ スクリプト プロパティへ移すこと）"
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

# ⚠️★★★ **配れるバイナリが存在するか**（2026-08-30 に本番事故として実測して追加）。
#
#   ★ 2026-08-30 に macOS 実機で踏んだ: `--mode o1 --tag v0.1.29` は**最後まで緑で完走**し、
#     `o1.mode` 入りの正常に見える配布物ができた。⚠️ ところが `v0.1.29`（2026-08-23）は
#     **`src-tauri/src/o1.rs` を 1 バイトも含まない**（O1 実装は 08-27 の 7a062cc）。
#   ⚠️ 起動して実測した結果: ファイル名が `gse_o1_*` にならず、`Probe scheduler thread started`
#     ＝ **黙って通常モードで動き、ランダムプローブが復活していた**
#     （preregistration.md §5.4-5 が「取り返しがつかない」と書いている事故そのもの）。
#   ★ 本ゲートは「配ってよいか」の単一の真実源なのに、⚠️ **この状態を 1 度も赤にしていなかった**。
#
#   ⚠️★★ **タグの新しさで代用しない。** ★ 見るのは「そのタグに O1 の実装が入っているか」である。
#     （★ release 資産そのものの検査は `make-common-app-zip.sh` の `strings` 側にある。
#       ⚠️ ここでは repo だけで判定できることに徹する。）
o1_release_tag=""
if git rev-parse --git-dir > /dev/null 2>&1; then
  while IFS= read -r t; do
    [ -n "$t" ] || continue
    if git cat-file -e "${t}:src-tauri/src/o1.rs" 2>/dev/null; then
      o1_release_tag="$t"
      break
    fi
  done <<< "$(git tag --sort=-v:refname 2>/dev/null)"
  if [ -n "$o1_release_tag" ]; then
    # ⚠️★★★ **「o1.rs がある」だけでは足りない**（2026-09-01 に実測して判明）。
    #   ★ 上のコメントは「タグの新しさで代用しない・見るのは実装が入っているか」と
    #     正しく書いているのに、⚠️ **実装は `git cat-file -e` ＝ファイルの有無しか見ていなかった**。
    #   → ★ v0.1.30 は `o1.rs` を持つので緑になったが、⚠️ **`label_row_allowed`（O1 で
    #     出てはいけない UI を塞ぐ門）が 0 件**で、staged 配布物はその古い版だった。
    #   ⚠️ これは memory `gate-green-but-artifact-broken` ②「タグが新しい ≠ 機能が
    #     入っている」の**再発**である（★ 前回は o1.rs が 0 バイト、今回は o1.rs が古い）。
    #
    # ★ そこで **タグ以降にコードが動いていないか**を見る。
    #   ⚠️ 特定の関数名を焼き込まない —— 焼き込むと**次に足した機能でまた素通りする**。
    #
    # ⚠️★★★ **「O1 に関係するファイル」を手で列挙しない**（code-reviewer 指摘・2026-09-01）。
    #   ★ 初版は `o1.rs` / `redaction.rs` / `Dashboard.tsx` 等を列挙したが、
    #     ⚠️ **今回の発端 `label_row_allowed` は `o1.rs` と `lib.rs` の両方にあり**、
    #     `lib.rs` は列挙から漏れていた。★ 実際 `cddbe3a` は `logger.rs` 側が主で、
    #     ⚠️ **たまたま `o1.rs` も触ったから赤になっただけ**である
    #     —— `logger.rs`/`lib.rs` だけの O1 修正なら**緑のまま通っていた**。
    #   → ★ ゲートの問いは「O1 に関係するか」ではなく「**タグのバイナリが現行か**」である。
    #     ⚠️ 手書きの列挙は「発端の欠陥と同型の取りこぼし」を必ず残す。
    o1_paths=( src-tauri/src src-tauri/Cargo.toml src )

    # ⚠️★★ 比較先を `HEAD` にしない（code-reviewer 指摘）。
    #   ★ 「再ビルドのためタグを checkout する」は現実的な手順で、⚠️ その状態だと
    #     `<tag>..HEAD` が空になり **偽の緑**になる（実測で再現された）。
    #   → ★ `origin/main`（無ければ `main`）と比べる。
    cmp_ref=""
    for r in origin/main main; do
      if git rev-parse --verify --quiet "$r^{commit}" > /dev/null 2>&1; then cmp_ref="$r"; break; fi
    done
    if [ -z "$cmp_ref" ]; then
      # ⚠️ 判定できないことを緑にしない（memory: silent-failure-in-guard-scripts）
      ng "⚠️ 比較先 (origin/main / main) が解決できないため、リリースタグの鮮度を判定できません"
      cmp_ref=""
    fi
    stale_commits=""
    if [ -n "$cmp_ref" ]; then
      # ⚠️ タグ自体が解決できないなら黙って緑にしない
      if ! git rev-parse --verify --quiet "${o1_release_tag}^{commit}" > /dev/null 2>&1; then
        ng "⚠️ リリースタグ ${o1_release_tag} を解決できません（★ 鮮度を判定できない）"
      else
        stale_commits="$(git log --oneline "${o1_release_tag}..${cmp_ref}" -- "${o1_paths[@]}" 2>/dev/null || true)"
      fi
    fi
    stale_n="$(printf '%s' "$stale_commits" | grep -c . || true)"
    if [ "${stale_n:-0}" -gt 0 ]; then
      ng "⚠️★★★ リリースタグ ${o1_release_tag} は **古い**。★ タグ以降にコードが ${stale_n} コミット動いている（★ 配るバイナリにその修正が入らない）:
$(printf '%s' "$stale_commits" | sed 's/^/        /')
      → ★ **再ビルドして新しいタグを切ること。** ⚠️ 走らせた日は取り返せない。"
    else
      ok "O1 実装を含むリリースタグがある（${o1_release_tag}）★ タグ以降に配布物のコード変更なし"
    fi
  else
    ng "⚠️ O1 実装を含むリリースタグが 1 つも無い（★ 配るバイナリが o1.mode を読めず、黙って通常モードで動く。⚠️ ランダムプローブが復活する）"
  fi
else
  # ⚠️ 判定できないことを緑にしない（memory: silent-failure-in-guard-scripts）。
  ng "⚠️ git リポジトリではないので O1 実装を含むリリースタグの有無を確かめられない"
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
  ng "O1 ガードの検査が無い: ${SYNC_GUARD_TEST}（⚠️ 語の存在だけでは弾く証拠にならない）"
else
  out=$(bash "$SYNC_GUARD_TEST" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then
    # ⚠️★★ **どの PowerShell で検証したかまで見る**（2026-08-30）。
    #   ★ `pwsh`(Core 7+) と `powershell.exe`(Desktop 5.1) は別物で、
    #     ⚠️ 5.1 は BOM 無しを CP932 で読むため日本語で parse が壊れる型がある。
    #   → ★ **Core で緑になっただけで「両方 OK」と言わない。**
    ps1v="$(printf '%s\n' "$out" | sed -n 's/^PS1_VERIFIED: *//p' | tail -1)"
    case "${ps1v}" in
      desktop*)
        ok "sync-session.sh / .ps1 の両方が O1 を実際に弾く（★ ${ps1v} ＝ 被験者と同じ実行系）" ;;
      core*)
        ok "sync-session が O1 を実際に弾く（⚠️ ★ .ps1 は ${ps1v} のみ。**Windows 5.1 は未検証**）" ;;
      *)
        ok "sync-session が O1 を実際に弾く（⚠️ ★ .ps1 は未実行。Windows で 1 回は走らせること）" ;;
    esac
  else
    ng "sync-session の O1 ガードが弾いていない"
    printf '%s\n' "$out" | grep '❌' | sed 's/^/     /'
  fi
fi

# ⚠️★★★ シェルの移植性（★ 上のガードが **macOS でだけ壊れていた**ので足した・2026-08-29）。
#   ★ 実害: `sync-session.sh` の O1 ガードが `exit 4` に到達できず `exit 1` を返していた。
#     ⚠️ 真因は macOS 標準の **bash 3.2 が多バイト文字を変数名の一部として読む**こと
#     （変数を括らずにその直後へ全角括弧を置くと、「変数名 ＋ 括弧のバイト」という
#       存在しない変数として読まれ、`set -u` で落ちる）。
#   ⚠️★ **上の検査だけでは足りない**: あれは「弾くか」を見るが、
#     ★ 同じ罠は**まだ触っていないスクリプト**にも入りうる（実際 17 箇所あった）。
if [ ! -f scripts/check-shell-portability.sh ]; then
  ng "シェル移植性ゲートが無い: scripts/check-shell-portability.sh"
else
  # ⚠️★ `if` の条件部で受ける（★ Codex /cross-review 指摘・2026-08-29）。
  #   ★ 本スクリプトは現在 `set -uo pipefail`（`-e` 無し）なので `sp_out=$(...)` でも動くが、
  #   ⚠️ **あとで `set -e` が足された瞬間に、この検査は代入行で死んで黙って飛ぶ**。
  #   ★ 「ゲートが黙って飛ぶ」はこのプロジェクトが最も踏んでいる型なので、形のほうを堅くする。
  if sp_out=$(bash scripts/check-shell-portability.sh 2>&1); then
    ok "シェルスクリプトが bash 3.2 で壊れる書き方をしていない（★ 陽性/陰性対照つき）"
  else
    ng "★ bash 3.2 で壊れる書き方が残っている（★ \${name} と括ること）"
    printf '%s\n' "$sp_out" | grep -E '❌|:[0-9]+:' | sed 's/^/     /'
  fi
fi

# ⚠️★★ **配備ごとに変わる値が `.gs` に直書きされていないか**（2026-08-29 追加・起票 T-18）。
#   ★ 受け口は前から `FOLDER_ID` / `SHARED_SECRET` をスクリプト プロパティに置いていたが、
#     ⚠️ **ビルダーは `.gs` の `var` に貼る設計**で、そこに検査が無かった。
#   ★ 2026-08-29 にビルダーも同じ規約へ移したので、⚠️ **戻ってこないように機械で止める**。
#   ⚠️ 直書きが危ないのは 2 つの理由である:
#     1. repo のコードと Apps Script 上のコードが**食い違う**（★ 直したつもりが届かない）
#     2. 配布フォルダ URL は「リンクを知る全員=閲覧者」で、★ その中に提出設定が入りうる
# ⚠️★★ **`.gs` だけでは足りない**（security-checker MEDIUM・2026-08-29 に実測で判明）:
#   ★ `.gs` から実ロスター ID を消したのに、**隣のテストが同じ値をフルで持っていた**。
#   → ★ `Form_O1/` の `.cjs` / `.sh` も走査する。
#   ⚠️ **限界を隠さない**: これは「**鍵名**の直書き」を見る検査なので、
#     ★ 変数名を変えれば素通りする（実際 `ROSTER_ID` が素通りしていた）。
# ⚠️★★ **鍵名ではなく「ID の形」で見る**（2026-08-29 に差し替え）。
#   ★ 最初は鍵名（`FOLDER_ID` 等）で見ていたが、⚠️ **変数名を変えれば素通り**した
#     （実際 `ROSTER_ID = "<実 ID>"` が素通りしていた）。★ 逆にスタブ値を誤検知もした。
#   → ★ Google の ID は **25 文字以上の `[A-Za-z0-9_-]`** である。この**形**を見る。
#   ⚠️ 正当な例外（G1 の拒否リスト・テストの固定値）は **`gate:allow-id` を同じ行に書く**。
#     ★ 例外を「見えるところに 1 行で」置くのが要点である（★ 黙って除外しない）。
# ⚠️★★★ **2 つの規則を「併置」する**（code-reviewer HIGH・2026-08-29 に訂正）。
#   ★ 一度 ID 形だけに**置き換えた**が、⚠️ URL は `://` を含むため
#     「引用符に隣接した 25 文字の連なり」にならず、★ **当初の動機だった
#     `O1_APP_DOWNLOAD_URL = "https://…"` の直書きを見逃していた**（実測で確認）。
#   → ★ 鍵名規則（`.gs` のみ）と ID 形規則（全ファイル）の**両方**を回す。
#   ⚠️ 鍵名規則を `.gs` に限るのは、★ テストが `ctx.__props.X = "スタブ"` と書くためである
#     （= production の `.gs` に「設定の代入」があってはならない、という規則）。
#
# ⚠️★★ **`grep -q` をパイプの下流に置かない**（code-reviewer MEDIUM・2026-08-29）:
#   `set -o pipefail` の下で `grep -q` が早期終了すると上流が SIGPIPE(141) を返し、
#   ★ **入力が大きいときだけ黙って見逃す**。→ 変数に受けて中身の有無で判定する。
hardcoded=""
scan_ () { # $1 = ファイル / $2 = 正規表現 / $3 = ラベル
  local hits
  hits=$(grep -nE "$2" "$1" 2>/dev/null | grep -v 'gate:allow-id' || true)
  [ -z "$hits" ] && return 0
  hardcoded="$hardcoded $1:$(printf '%s' "$hits" | cut -d: -f1 | tr '\n' ',')($3)"
}
for f in "$RECEIVER" "$FORM_BUILDER"; do
  [ -f "$f" ] || continue
  # (a) ★ `.gs` に「設定の代入」があってはならない（⚠️ 空文字の代入は対象外）。
  scan_ "$f" "(SHARED_SECRET|FOLDER_ID|O1_APP_DOWNLOAD_URL|PHASE1_MGMT_SHEET_ID|O1_MGMT_SHEET_ID|ROSTER_ID|FORM_ID_O1_(CONSENT|SURVEY))[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" "設定の直書き"
done
for f in "$RECEIVER" "$FORM_BUILDER" Form_O1/*.cjs Form_O1/*.sh; do
  [ -f "$f" ] || continue
  # (b) ★ Google の ID の形（25 文字以上の `[A-Za-z0-9_-]`）
  scan_ "$f" "['\"][A-Za-z0-9_-]{25,}['\"]" "ID 形"
  # (c) ⚠️ Drive のフォルダ URL（★ T-15 と同じ形を O1 で作らせない）
  scan_ "$f" "drive\.google\.com/drive/folders/" "Drive URL"
done
if [ -z "$hardcoded" ]; then
  ok "O1 のファイルに ID / URL の直書きが無い（★ 例外は gate:allow-id で明示）"
else
  ng "★ O1 のファイルに ID / URL が直書きされている（⚠️ スクリプト プロパティへ。正当なら gate:allow-id を付ける）:$hardcoded"
fi

# ⚠️★★★ **提出設定（endpoint ＋ secret）が git に入っていないか**（2026-08-29 追加）。
#   ★ 動機は仮定ではない: 同日、`Form_O1/o1_submit.json`（**実 endpoint ＋ 実 secret**）が
#     `.gitignore` の網から外れ、⚠️ **`git add -A` の対象になっていた**
#     （★ code-reviewer / security-checker が独立に実測で検出。⚠️ コミット前に止めた）。
#   ⚠️ 既存の秘密検査は `.gs` **1 本**しか読まないので、★ **`.json` は素通り**だった。
#   ★ `.gitignore` は自身のコメントで「本リポジトリは**一時 public にする運用がある**」
#     「⚠️ **履歴からは消せない**」と書いている。→ ★ **入る前に止めるしかない。**
secret_leak=""
# (a) 提出設定そのもののファイル名（★ g1 / o1 の両方・`-` と `_` の両方を見る）
leak_files=$(git ls-files | leak_name_hits)
[ -z "$leak_files" ] || secret_leak="$secret_leak 提出設定:$(printf '%s' "$leak_files" | tr '\n' ' ')"
# (b) 追跡ファイルに実物のデプロイ ID が無いか
leak_url=$(git grep -lIE "$leak_url_re" 2>/dev/null || true)
[ -z "$leak_url" ] || secret_leak="$secret_leak 実 endpoint:$(printf '%s' "$leak_url" | tr '\n' ' ')"
# (c) ⚠️★★★ **作業ツリーに提出設定があるのに「無視されていない」**状態
#     （★ `git add -A` 一発で入る = 2026-08-29 に実際に踏みかけた状態そのもの）。
#     ★ `--others --exclude-standard` は「未追跡かつ無視されていない」ものだけを出す。
#     ⚠️ (a)(b) は **git に入った後**しか見ないので、この 1 本が**入る前**を受け持つ。
leak_pending=$(git ls-files --others --exclude-standard | leak_name_hits)
[ -z "$leak_pending" ] || secret_leak="$secret_leak 未無視:$(printf '%s' "$leak_pending" | tr '\n' ' ')"
# (d) ⚠️★★★ **secret の「値」を散文に書いた経路**（security-checker CRITICAL・2026-08-30）。
#     ★ 動機は仮定ではない: 同日、私が `.steering/.../blockers.md` に
#       **実 secret の先頭 45 文字**を貼った（⚠️ 未追跡のうちに削除。履歴には未混入）。
#     ⚠️ (a)(b)(c) は 3 本とも**これを捕まえられない**:
#       (a)(c) は *ファイル名*、(b) は *endpoint の形* しか見ていない。
#     ★ `.steering/` は `.gitignore` されておらず、⚠️ CLAUDE.md の運用は
#       「全作業を `.steering/` に記録・コミット」である ＝ `git add -A` 一発で入る。
#     ⚠️★ **ゲート自身が secret を出力しない**（★ ヒットはファイル名だけ報告する）。
#     ⚠️★★★ 射程: 判定できるのは**手元に `o1_submit.json` がある機械だけ**である。
#       ★ 旧版はここにこのコメントだけを書き、⚠️ **明示する実装を書いていなかった**
#         （2026-08-30・cross-review の HIGH で検出。★ コメントと実装の不一致）。
#       ⚠️ (a)〜(d) は 1 つの `secret_leak` に畳み込まれて**単一の緑メッセージ**になるので、
#         ★ (d) が走らなかったことが**その緑に紛れて見えなくなる**。
#       → ★ 走ったかどうかを持ち、走らなかったら**必ず画面に出す**
#         （★ 同ファイルが `git rev-parse --git-dir` で採っている
#           「判定できないことを緑にしない」原則に揃える）。
secret_val_checked=0
if [ -f Form_O1/o1_submit.json ] && command -v python3 > /dev/null 2>&1; then
  leak_needle=$(python3 -c "
import json,sys
try:
    s=json.load(open('Form_O1/o1_submit.json'))['secret']
except Exception:
    sys.exit(0)
# ★ 16 文字あれば偶然一致しない。⚠️ 短すぎると散文の普通の語に当たる。
print(s[:16] if len(s)>=16 else '')
" 2>/dev/null || true)
  if [ -n "$leak_needle" ]; then
    leak_val=$({ git ls-files -z; git ls-files -z --others --exclude-standard; } \
      | xargs -0 grep -lF -- "$leak_needle" 2>/dev/null \
      | grep -v '^Form_O1/o1_submit.json$' || true)
    [ -z "$leak_val" ] || secret_leak="$secret_leak 実 secret の値:$(printf '%s' "$leak_val" | tr '\n' ' ')"
    secret_val_checked=1
  fi
fi
# ⚠️★ **検査の射程を誇張しない**（Codex 指摘）: ここが見るのは
#   「**いまの**追跡ツリー」と「**いま**無視されていない未追跡ファイル」だけである。
#   ★ **過去のコミットに混入したもの**は見ていない（→ 混入したら履歴の書き換えが要る）。
# ⚠️★★ **(d) が走らなかったことを緑に紛れさせない。** ★ ✅/❌ の件数には足さない
#   （★ この機械では判定できないだけで、欠陥があるとは言っていない）が、
#   ⚠️ **必ず目に入る**ようにする（memory: `silent-success-is-not-visible`）。
if [ "$secret_val_checked" -ne 1 ]; then
  echo "  ⚠️ 未確認: Form_O1/o1_submit.json が無い（か python3 が無い）ので、"
  echo "     ★ この機械では **実 secret の値が散文に混入していないか**を判定していない。"
  echo "     ⚠️ 下の緑はこの 1 点を含まない。★ 設定のある機械で走らせ直すこと。"
fi
if [ -z "$secret_leak" ]; then
  if [ "$secret_val_checked" -eq 1 ]; then
    ok "提出設定（endpoint / secret）が git に入っておらず、入る手前でもなく、値の混入も無い"
  else
    ok "提出設定（endpoint / secret）が git に入っておらず、入る手前でもない（⚠️ 値の混入は未判定）"
  fi
else
  ng "⚠️★★★ 秘密が git に入る（★ push 前に止めること。⚠️ 入ると履歴からは消せない）:$secret_leak"
fi

# ⚠️★★★ **O1 のファイルが git に追跡されているか**（2026-08-29 追加）。
#   ★ 動機（⚠️ 2026-08-29 に**実測して確かめた挙動**。推測ではない）:
#     - 実験A: 無視されたディレクトリに **新規** ファイルを置いて `git add` すると
#       **拒否される**（`The following paths are ignored`）。⚠️ `git add -A` は**黙って飛ばす**。
#     - 実験B: **すでに追跡されている**ファイルは `.gitignore` を足しても**外れない**
#       （★ したがって `git mv` で移したものは残る）。
#   → ⚠️ 危ないのは「`Form_O1/` を無視したまま **新しい O1 ファイルを足す**」場合と、
#     「`git mv` ではなく素の `mv` ＋ `git add -A` で移す」場合である。
#     ★ どちらも**手元にはファイルがある**ので、上の `[ -f ... ]` 検査は**全部緑のまま通る**。
#     気づけるのは「clone した機械で配備が失敗したとき」になる。
#   → ★ 存在ではなく **追跡** を見る。⚠️ これが「見えないまま緑」の代表例である。
# ⚠️★★ **列挙せず、ディスクを走査する**（code-reviewer MEDIUM・2026-08-29）。
#   ★ 既知の 5 本だけを見ると、⚠️ **6 本目**が `.gitignore` に飲まれても気づけない
#     （★ `.gitignore` は名前列挙のホワイトリストなので、足し忘れが起こりうる形である）。
untracked=""
# ⚠️★ **射程を誇張しない**（Codex 指摘・2026-08-29）: 見ているのは `.gs` / `.cjs` / `.sh` の 3 種。
#   ★ `.gitignore` は `README.md` も通しているが、⚠️ **それは検査していない**
#   （= README を足し忘れても赤くならない）。新しい種類を足すならここにも足すこと。
for f in Form_O1/*.gs Form_O1/*.cjs Form_O1/*.sh; do
  [ -e "$f" ] || continue          # ★ glob が展開されなかった場合
  git ls-files --error-unmatch "$f" > /dev/null 2>&1 || untracked="$untracked $f"
done
if [ -z "$untracked" ]; then
  ok "O1 のファイルが git に追跡されている（★ .gitignore に飲まれていない）"
else
  ng "★ O1 のファイルが git に追跡されていない（⚠️ .gitignore を確認すること）:$untracked"
fi

# ⚠️★★★ O1 の運用管理シート（★ 提出イベントの追記ログ・起票 T-25）が**実装されているか**。
#   ★ 期限がある: ⚠️ **配布後に作ると、それ以前の提出分が遡って埋まらない**。
#   ⚠️★ **射程を誇張しない**: ここで見ているのは **repo 側の実装**だけである。
#     ★ 実物のスクリプト プロパティ `O1_MGMT_SHEET_ID` が入っているかは**見ていない**
#       （= GAS を叩かないと分からない）。→ ★ そちらは `checkO1FormConfig()` が
#       fail-closed で止めるので、⚠️ **配備時に実行して確かめること**。
mgmt_missing=""
if [ ! -f "$FORM_BUILDER" ]; then
  mgmt_missing="ビルダーが読めない"
else
  # ⚠️★★★ **「キー名が出てくるか」では測れない**（2026-09-03 に 3 状態で実測して判明）。
  #   ★ 最初はコメント行を除いた `O1_MGMT_SHEET_ID` の出現で測ろうとしたが、
  #     ⚠️ **エラーメッセージの文字列リテラル**（「スクリプト プロパティ O1_MGMT_SHEET_ID が
  #     空です」）が非コメント行なので、★ **実際の読み取りを全部消しても緑のまま**だった。
  #     → ⚠️ 起票時点（= コメント 2 行だけ）の状態を再現しても検出できない＝検査が空回り。
  #   → ★ **実際にプロパティを読んでいるか**だけを見る。
  grep -q 'getProperty("O1_MGMT_SHEET_ID")' "$FORM_BUILDER" ||
    mgmt_missing="$mgmt_missing スクリプト プロパティ O1_MGMT_SHEET_ID を読んでいない"
  grep -q "function buildO1MgmtSheet" "$FORM_BUILDER" || mgmt_missing="$mgmt_missing buildO1MgmtSheet が無い"
  grep -q "function o1LogMgmt_" "$FORM_BUILDER" || mgmt_missing="$mgmt_missing o1LogMgmt_ が無い"
  # ★ 「関数はあるが誰も呼んでいない」を弾く（⚠️ 呼ばれない実装は実装ゼロと同じ）。
  # ⚠️★ **`[ … ] && x=…` を else ブロックの最終コマンドにしない**（code-reviewer MEDIUM）。
  #   ★ 健全時に compound が rc=1 で終わる形になり、⚠️ **あとで `set -e` が足された瞬間に
  #     この検査は代入行で死んで黙って飛ぶ**（★ 本ファイル自身が :306 で戒めている型）。
  #
  # ⚠️★★★ **部分一致で数えない**（cross-review MEDIUM・2026-09-03）。
  #   ★ 旧実装は `grep -c "o1LogMgmt_("` だった。⚠️ ところが `DISABLED_o1LogMgmt_(` も
  #     **その部分文字列を含む**ので、★ 呼び出しを全部潰す変異を当てても
  #     **件数が 11 → 11 で変わらなかった**（2026-09-03 に実測）。
  #   ⚠️ その変異が赤になっていたのは**別の検査**（`function o1LogMgmt_` の消失）が
  #     先に発火していたからで、★ **この件数ガード自体は一度も検証されていなかった**。
  #     （★ memory `measurement-instrument-false-positives` の「対照文字列の自己参照」と同型）
  #   → ★ **直前の文字が識別子でないこと**を要求し、⚠️ 定義行 (`function o1LogMgmt_(kind`) は
  #     `("` を要求することで除外する（★ 呼び出しは必ず文字列リテラルが第 1 引数）。
  if [ "$(grep -cE '(^|[^A-Za-z0-9_])o1LogMgmt_\("' "$FORM_BUILDER")" -lt 3 ]; then
    mgmt_missing="$mgmt_missing o1LogMgmt_ の呼び出しが少なすぎる（★ 提出経路に配線されていない）"
  fi
fi
if [ -z "$mgmt_missing" ]; then
  ok "O1 の運用管理シート（登録ログ）が実装され、提出経路に配線されている"
else
  ng "★ O1 の運用管理シートが未実装（⚠️ 配布後に作ると遡って埋まりません）:$mgmt_missing"
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
  ng "★ 送信 timeout の実測記録票が無い: ${MEASURE}（★ .gs 手順 8 の「1 日ぶんの通し確認」）"
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

# ⚠️★★★ **`sed -i` を直接書かない**（security-checker HIGH・2026-08-29 に macOS で実測）:
#   ★ GNU sed は `-i` の直後に式を取るが、⚠️ **BSD(macOS) sed は次の引数を「バックアップ拡張子」
#     として食う**ため、`sed_i 's/a/b/' f` は `sed: 1: "f": invalid command code` で落ちる。
#   ⚠️ 実害: 本ファイルの `--selftest` が macOS で **通過 18 / 失敗 17** になっており、
#     ★ そのなかに「**O1 ガードが空回りしていないことを示す唯一の変異試験**」
#     （`sync ガードが弾かなくなる`）が含まれていた。→ ⚠️ **macOS では 1 度も実行されていなかった。**
#   ★ `-i ''` は BSD では通るが GNU では「'' というファイル」と解される。→ どちらでも同義になる
#     **一時ファイルへ書いて置き換える**形に統一する。
#   ⚠️ 引数の並びは `sed` と同じ（最後の引数が対象ファイル）。
sed_i () {
  local n=$# f tmp i
  eval "f=\${${n}}"
  local args=()
  i=1
  while [ "${i}" -lt "${n}" ]; do
    eval "args+=(\"\${${i}}\")"
    i=$((i + 1))
  done
  tmp="$(mktemp)"
  # ⚠️★ 置き換えは成功したときだけ（★ 失敗して空ファイルにすると変異試験が意味を失う）。
  if sed "${args[@]}" "${f}" > "${tmp}"; then
    cat "${tmp}" > "${f}"        # ★ mv でなく上書き（⚠️ パーミッションと inode を保つ）
    rm -f "${tmp}"
  else
    rm -f "${tmp}"
    return 1
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
    # ⚠️★ **`Form_O1/` も作る** (2026-08-29 に O1 のファイルを移した)。
    #   ★ 作らないと `cp` が黙って失敗し、⚠️ selftest が**空回りする**。
    mkdir -p "$fix/w/scripts" "$fix/w/docs" "$fix/w/Form_G1" "$fix/w/Form_O1" \
             "$fix/w/$(dirname "$CONSENT")" \
             "$fix/w/experiments/20260801-controlled-friction-task" "$fix/w/src-tauri/src"
    cp "$SCRIPT_PATH" "$fix/w/scripts/gate.sh"
    cp "$repo/$LEDGER" "$fix/w/docs/" 2>/dev/null
    cp "$repo/$RECEIVER" "$repo/$RECEIVER_TEST" "$fix/w/Form_O1/" 2>/dev/null
    # ★ フォームビルダーとその検査は `Form_O1/` へ。
    #   ⚠️ ただし検査は **G1 のビルダー**（拒否リストの突き合わせ・`Form_G1/` に残る）と
    #   同意文書（連絡先の突き合わせ）も読むので、**3 つとも**写す。
    cp "$repo/$FORM_BUILDER" "$repo/$FORM_BUILDER_TEST" "$fix/w/Form_O1/" 2>/dev/null
    cp "$repo/Form_G1/GSE_G1_Form_Builder.gs" "$fix/w/Form_G1/" 2>/dev/null
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
    # ⚠️★★★ **収集仕様の自己記述も写す**（ADR-031・2026-09-14）。
    #   ★ 写さないと「計器があるか」の判定が常に「ファイルが無い」で赤になり、
    #     ⚠️ **連動の検査だけ変異試験が成立しない**（★ 本ゲートが戒めている型そのもの）。
    cp "$repo/$CAPS" "$fix/w/$CAPS" 2>/dev/null
    printf 'x\n.timeout(std::time::Duration::from_secs(180))\n' > "$fix/w/src-tauri/src/reconcile.rs"
    cp "$repo/$MEASURE" "$fix/w/$MEASURE" 2>/dev/null
    # ⚠️★★★ **移植性ゲートも写す**（security-checker 指摘・2026-08-29）。
    #   ★ 写さないと selftest 中は常に「ゲートが無い」で赤になり、
    #     ⚠️ **新しく足した検査だけ変異試験が無い**状態になる（★ 本ゲートが戒めている型そのもの）。
    cp "$repo/scripts/check-shell-portability.sh" "$fix/w/scripts/" 2>/dev/null
    # ⚠️★★ **一時ツリーを git リポジトリにする**。
    #   ★ 移植性ゲートは `git ls-files` で対象を集めるので、⚠️ 非 git のままだと
    #     **必ず「検査できなかった」になり、壊しても壊さなくても赤**＝ 変異試験が成立しない。
    #   ★ `init` だけでよい（⚠️ commit は不要。`--others` で未追跡も集まる）。
    git -C "$fix/w" init -q 2>/dev/null || true
    cons="$fix/w/$CONSENT"
  }

  # ★ 実測記録票を「実測済み」で埋める（⚠️ **selftest の中だけ**。本物は 1 バイトも触らない）。
  fill_measure () {
    sed_i \
      -e 's/^- 状態: \*\*未実施\*\*$/- 状態: **実測済み**/' \
      -e 's/^- 実測日: \*\*（未記入）\*\*$/- 実測日: **2026-09-01**/' \
      -e 's/^- 送信バイト数 (base64 後): \*\*（未記入）\*\*$/- 送信バイト数 (base64 後): **24 MB**/' \
      -e 's/^- 所要時間 (Drive 保存を含む): \*\*（未記入）\*\*$/- 所要時間 (Drive 保存を含む): **210 秒**/' \
      -e 's/^- 実効スループット: \*\*（未記入）\*\*$/- 実効スループット: **117 KB\/s**/' \
      -e 's/^- 採用した timeout: \*\*（未記入）\*\*$/- 採用した timeout: **固定 900 秒**/' \
      "$fix/w/$MEASURE"
  }
  # ⚠️★★★ **記録票を「未実測」へ戻す**（★ 2026-09-14 追加）。
  #   ★ なぜ要るか: `fill_measure` は「空欄を埋める」変異だったが、⚠️ **実物の記録票は
  #     2026-09-05 に実測済みで埋まった**。→ ★ 「埋める」変異はもう**状態を何も変えない**ので、
  #     ⚠️ **selftest 3 の 2 本が「壊しても緑のまま」と報告し続けていた**（★ 空回り）。
  #   → ★ いまは **逆向き（空に戻す）** が正しい変異である。
  blank_measure () {
    sed_i       -e 's/^- 状態: \*\*実測済み\*\*$/- 状態: **未実施**/'       -e 's/^- 実測日: \*\*.*\*\*$/- 実測日: **（未記入）**/'       -e 's/^- 送信バイト数 (base64 後): \*\*.*\*\*$/- 送信バイト数 (base64 後): **（未記入）**/'       -e 's/^- 所要時間 (Drive 保存を含む): \*\*.*\*\*$/- 所要時間 (Drive 保存を含む): **（未記入）**/'       -e 's/^- 実効スループット: \*\*.*\*\*$/- 実効スループット: **（未記入）**/'       -e 's/^- 採用した timeout: \*\*.*\*\*$/- 採用した timeout: **（未記入）**/'       "$fix/w/$MEASURE"
  }
  # ★ 「状態」だけ実測済みのまま、値の欄を空に戻す（⚠️ 中身の無い記録で緑にしないことの対照）。
  blank_measure_fields () {
    blank_measure
    sed_i 's/^- 状態: \*\*未実施\*\*$/- 状態: **実測済み**/' "$fix/w/$MEASURE"
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

  # ⚠️★★ **照合語はメッセージ固有にする**（code-reviewer LOW・2026-08-29）。
  #   ★ `expect_red` は「その語を含む ❌ 行があるか」しか見ないので、
  #   ⚠️ 複数の検査が同じ語を使うと、**別の理由で出た ❌ を拾って偽の合格**になる。
  echo "=== selftest 1: ✅ を 1 つずつ壊す（★ 赤にならなければゲートが空回りしている）==="
  build; sed_i 's/^- 所属: \*\*.*\*\*$/- 所属: **（実施前に記入）**/' "$cons"; expect_red "同意文書に未記入" "同意文書の空欄"
  build; sed_i 's/^- 連絡先: .*/- 連絡先: **（未定）**/' "$cons";             expect_red "連絡先が埋まっていない" "連絡先"
  build; sed_i 's/^- 所属: \*\*.*\*\*$/- 所属: **/' "$cons";                  expect_red "所属が埋まっていない" "所属"
  build; clear_pending; printf '\n| x | ⚠️ **未了: なにか** | y |\n' >> "$cons";              expect_red "未了" "状態表の未了残置"
  build; rm -f "$fix/w/docs/o1-deletion-ledger.md";                            expect_red "削除台帳が無い" "削除台帳の欠落"
  build; sed_i 's/^<!-- o1-retention: set -->$//' "$fix/w/docs/o1-deletion-ledger.md"; expect_red "マーカ.*が見つからない" "保管上限マーカの喪失"
  build; rm -f "$fix/w/Form_O1/GSE_O1_Submit.gs";                              expect_red "受け口が無い" "受け口の欠落"
  build; sed_i "s/^var MAX_BYTES/var SHARED_SECRET = 'abcdefghijklmnopqrstuvwxyz012345';\nvar MAX_BYTES/" "$fix/w/Form_O1/GSE_O1_Submit.gs"; expect_red "秘密が直書き" ".gs への秘密直書き"
  build; sed_i 's/_o1day/_block/' "$fix/w/Form_O1/GSE_O1_Submit.gs";          expect_red "ガード検査が赤" "受け口の名前ガード"
  build; rm -f "$fix/w/Form_O1/o1_submit_guard_test.cjs";                      expect_red "ガード検査が無い" "ガード検査の欠落"
  build; echo 'let th = SomethingElse::new();' > "$fix/w/src-tauri/src/lib.rs"; expect_red "目印.*が見つからない" "liveness アンカーの喪失"
  # ⚠️★★ **O1 の目印を消したら赤になること**（★ 2026-08-28 に緑になったので satisfy 側から移した）。
  build; sed_i 's/O1_LIVENESS_TRAY_AFTER_MS/RENAMED_AWAY_/g' "$fix/w/src-tauri/src/lib.rs"; expect_red "G1 と同じ" "O1 の liveness の目印の喪失"
  # ⚠️★★★ **定数が残っていても、配線が消えたら赤になること**（★ 被験者の画面は配線でしか変わらない）。
  build; sed_i 's/liveness::participant_visible_starved/liveness::NOT_WIRED_/g' "$fix/w/src-tauri/src/lib.rs"; expect_red "配線されていない" "liveness の配線の喪失"
  # ★ 実測記録票そのものが消えたら、⚠️「未実測」ではなく**票が無い**と言うこと（★ 原因が違う）。
  build; rm -f "$fix/w/$MEASURE";                                              expect_red "実測記録票が無い" "実測記録票の喪失"
  # ⚠️★★★ ADR-031: **送出元を足すと、承認が無い限り赤になる**（★ M5 が来た瞬間に門が効く）。
  build; printf '\nfn wired() { activity_label_answered(); activity_label_allowed(true, true); }\n' >> "$fix/w/$EMITTER"
  expect_red "同意の ESM 追補が未承認" "計器と同意の連動（送出元あり・未承認）"
  # ⚠️★★★ 運用管理シート（起票 T-25）—— ★ **3 つの壊し方を別々に撃つ**。
  #   ⚠️ 1 つだけだと「どれか 1 つでも欠けたら赤」なのか「たまたま拾えた」のか分からない。
  build; sed_i 's/function buildO1MgmtSheet/function DISABLED_buildO1MgmtSheet/' "$fix/w/$FORM_BUILDER"
  expect_red "運用管理シートが未実装" "管理シートの構築関数の喪失"
  build; sed_i 's/o1LogMgmt_(/DISABLED_o1LogMgmt_(/g' "$fix/w/$FORM_BUILDER"
  expect_red "運用管理シートが未実装" "登録ログの関数と配線の喪失"
  # ⚠️★★★ **件数ガードだけを撃つ**（cross-review MEDIUM・2026-09-03）。
  #   ★ 上の変異は `function o1LogMgmt_` も壊すので、⚠️ **別の検査が先に発火していた**
  #     （＝ 件数ガードは一度も検証されていなかった）。
  #   → ★ **定義はそのまま残し、呼び出しだけを消す**。
  #     ⚠️ `assign` の 2 か所だけが残るので 3 未満になり、件数ガードだけで赤になるはず。
  build; sed_i 's/o1LogMgmt_("register"/o1SkipLog_("register"/g' "$fix/w/$FORM_BUILDER"
  expect_red "呼び出しが少なすぎる" "★ 定義は残して呼び出しだけ消す（件数ガード単独）"
  # ⚠️★★★ **「コメントだけ実装」が緑にならないこと**（★ 2026-09-03 以前の実体がこれだった）。
  #   ★ 実コードの参照を消してコメントだけ残す = 起票時点の状態を再現する。
  build; sed_i 's/^    mgmtSheetId: String(props.getProperty("O1_MGMT_SHEET_ID").*$/    mgmtSheetId: "",/' "$fix/w/$FORM_BUILDER"
  expect_red "運用管理シートが未実装" "★ コメントだけ残して実コードを消す（起票時点の再現）"
  # ⚠️★★ **追跡の検査は fixture では測れない**（$fix/w は git 管理下に無く、常に「未追跡」になる）。
  #   → ★ 代わりに **本物の repo で陽性・陰性の対照**を取る（⚠️ 1 バイトも変更しない）。
  #   ⚠️★★★ 陰性対照は「**存在するのに追跡されていない**」でなければならない
  #     （code-reviewer MEDIUM・2026-08-29）: ★ 旧版は無視対象の手控えを使っていたが、
  #     それは fresh clone では**単に存在しない**ので、⚠️ **実在しない任意のパスでも通った**
  #     （= 対照になっていなかった）。
  #   ⚠️ 対照に使えるファイルが無い環境では **skip と明示する**（★ 黙って緑にしない）。
  # ⚠️★★★ **`neg` を見つけるだけで終わらせない**（Codex 指摘・2026-08-29）:
  #   ★ 旧版は候補を探した後 `$RECEIVER` しか assert しておらず、
  #   ⚠️ **陰性側が常に緑になる壊れ方**（判定器が何でも「追跡済み」と言う）を検出できなかった。
  #   → ★ 「候補が在るのに陰性が 1 つも取れない」も**赤**にする。
  cand=""; neg=""
  for c in "Form_O1/o1_submit.json" "Form_O1/Drive関連情報.md"; do
    [ -f "$c" ] || continue
    cand="$c"
    git ls-files --error-unmatch "$c" > /dev/null 2>&1 || { neg="$c"; break; }
  done
  if [ -z "$cand" ]; then
    echo "  ⏭️ skip: 追跡の検査の陰性対照（★ 対照に使えるファイルがこの機械に無い）"
  elif [ -z "$neg" ]; then
    echo "  ❌ 見分けられない: 候補 ($cand) が在るのに全部「追跡済み」と判定された"; sf=$((sf+1))
  elif git ls-files --error-unmatch "$RECEIVER" > /dev/null 2>&1 \
       && ! git ls-files --error-unmatch "$neg" > /dev/null 2>&1; then
    echo "  ✅ 判定器が両側を見分ける: 追跡の検査（★ 追跡済み=是 / 実在するが未追跡=非）"; sp=$((sp+1))
  else
    echo "  ❌ 見分けられない: 追跡の検査（★ 常に緑 or 常に赤になっている）"; sf=$((sf+1))
  fi

  # ⚠️★★ **秘密検出そのものに陽性・陰性の対照を置く**（Codex 指摘・2026-08-29）。
  #   ★ 本体は `git ls-files` を読むので fixture では撃てない。→ **検出関数を直接撃つ**。
  if [ "$(printf 'Form_O1/o1_submit.json\nnotes.md\n' | leak_name_hits)" = "Form_O1/o1_submit.json" ] \
     && [ -z "$(printf 'Form_O1/README.md\ndocs/o1.md\n' | leak_name_hits)" ] \
     && [ "$(printf 'g1-submit.json\n' | leak_name_hits)" = "g1-submit.json" ]; then
    echo "  ✅ 判定器が両側を見分ける: 提出設定のファイル名検出（★ o1_ / g1- を拾い、無関係は拾わない）"; sp=$((sp+1))
  else
    echo "  ❌ 見分けられない: 提出設定のファイル名検出"; sf=$((sf+1))
  fi
  # ★ URL 側: **実物の長さ**は拾い、⚠️ 本 repo のプレースホルダ (28 文字) は拾わないこと。
  real_url="https://script.google.com/macros/s/AKfycb$(printf 'x%.0s' $(seq 1 60))/exec"
  fake_url="https://script.google.com/macros/s/DRYRUN_NOT_A_REAL_DEPLOYMENT/exec"
  if printf '%s\n' "$real_url" | grep -qE "$leak_url_re" \
     && ! printf '%s\n' "$fake_url" | grep -qE "$leak_url_re"; then
    echo "  ✅ 判定器が両側を見分ける: 実 endpoint 検出（★ 実物=是 / プレースホルダ=非）"; sp=$((sp+1))
  else
    echo "  ❌ 見分けられない: 実 endpoint 検出（★ 閾値 40 文字を確かめること）"; sf=$((sf+1))
  fi
  # ⚠️★★ **アンカー喪失を緑にしない**（★ 記録票を埋めた後に顕在化する穴だった）。
  build; fill_measure; rm -f "$fix/w/src-tauri/src/reconcile.rs";              expect_red "reconcile.rs が読めない" "reconcile.rs のアンカー喪失"
  # ★★ 2026-08-28 に緑になった 3 件。⚠️ **緑になったものは selftest 2 から 1 へ移す**
  #   （satisfy 側に置いたままだと「もともと緑」を「満たしたから緑」と読み違える）。
  build; sed_i 's/^<!-- o1-retention: set -->$/<!-- o1-retention: unset -->/' "$fix/w/docs/o1-deletion-ledger.md"; expect_red "保管上限が未確定" "保管上限を未確定へ戻す"
  build; rm -f "$fix/w/Form_O1/GSE_O1_Form_Builder.gs";                        expect_red "フォーム類が無い" "フォームビルダーの欠落"
  build; rm -f "$fix/w/Form_O1/o1_form_builder_test.cjs";                      expect_red "ガード検査が無い" "フォームビルダーの検査の欠落"
  # ⚠️★★★ **中身を壊しても赤になること。** ★ 存在するだけで緑になっていた旧版の再発防止。
  build; sed_i 's/^var G1_FORM_IDS_DO_NOT_TOUCH = {$/var G1_FORM_IDS_DO_NOT_TOUCH = {}; var UNUSED_ = {/' "$fix/w/Form_O1/GSE_O1_Form_Builder.gs"; expect_red "フォームビルダーのガード検査が赤" "フォームビルダーの G1 拒否リスト"
  # ⚠️★★ **ビルダーへの直書きが戻ったら赤になること**（2026-08-29・起票 T-18）。
  build; printf %s "
var O1_APP_DOWNLOAD_URL = \"https://drive.google.com/drive/folders/EXAMPLE\";
" >> "$fix/w/$FORM_BUILDER"; expect_red "ID / URL が直書き" "ビルダーへの配備値の直書き"
  build; printf %s "
var PHASE1_MGMT_SHEET_ID = \"FAKE_SHEET_ID_FOR_SELFTEST_00000\";
" >> "$fix/w/$FORM_BUILDER"; expect_red "ID / URL が直書き" "ビルダーへのロスター ID の直書き"
  # ⚠️★ **受け口側も撃つ**（security-checker 指摘・2026-08-29）: 既存の SHARED_SECRET 変異は
  #   旧検査でも赤くなるため、★ 新しい「ID の形」の検査が**受け口を見ているか**は未実測だった。
  # ⚠️★★ **`gate:allow-id` 自体の対照**（code-reviewer MEDIUM・2026-08-29）。
  #   ★ 除外の仕組みを selftest から 1 度も撃っていなかった。
  #   ⚠️ 無制限の自己申告除外は、このゲートが戒めている「黙って緑にする」手段そのものになる。
  #   → ★ (1) 印を外すと赤になること (2) **例外の件数が増えていないこと**を測る。
  build; sed_i 's|// gate:allow-id||g' "$fix/w/$FORM_BUILDER"; expect_red "ID 形" "allow-id を外すと赤になる"
  # ⚠️★★ **散文中の言及を数えない**（2026-08-29 に実測して判明）。
  #   ★ 数えるべきは「**実際に検出を抑えている行**」＝ 検出パターンに当たり、かつ印がある行。
  #   ⚠️ 印という語がコメントに出ただけで上限を超えると、★ 検査が「オオカミ少年」になる。
  allow_n=$(cat Form_O1/*.gs Form_O1/*.cjs Form_O1/*.sh 2>/dev/null \
    | grep -E "['\"][A-Za-z0-9_-]{25,}['\"]|drive\.google\.com/drive/folders/" \
    | grep -c 'gate:allow-id' || true)
  allow_n=${allow_n:-0}
  if [ "$allow_n" -le 8 ]; then
    echo "  ✅ 例外の件数が増えていない: 実効 $allow_n 行（★ 上限 8）"; sp=$((sp+1))
  else
    echo "  ❌ 例外が増えている: 実効 $allow_n 行（★ 上限 8。⚠️ 増やすなら根拠を書いて上限も上げること）"; sf=$((sf+1))
  fi
  build; printf %s "
var FOLDER_ID = \"FAKE_FOLDER_ID_FOR_SELFTEST_0000\";
" >> "$fix/w/$RECEIVER"; expect_red "ID / URL が直書き" "受け口への ID の直書き"
  # ⚠️★ 行は**字下げされている**。`^` で固定すると変異が当たらず、
  #   ★ 「壊したつもりで壊れていない」偽の合格になる（2026-08-28 に実際に踏んだ）。
  build; sed_i 's|: > "$M/o1.mode"|: > "$M/DISABLED"|; s|: > "$W/o1.mode"|: > "$W/DISABLED"|'               "$fix/w/experiments/20260801-controlled-friction-task/make-common-app-zip.sh"; expect_red "o1.mode を置かない" "o1.mode の書き出しの喪失"
  build; rm -f "$fix/w/scripts/sync_session_o1_guard_test.sh";                 expect_red "O1 ガードの検査が無い" "sync ガードの検査の欠落"
  # ⚠️★★ **語だけ残してガードの実体を消しても赤になること**（★ 旧版はここを緑にしていた）。
  build; sed_i 's/^    exit 4$/    return 0/' "$fix/w/scripts/sync-session.sh";  expect_red "弾いていない" "sync ガードが弾かなくなる"

  # ⚠️★★★ **secret の「値」を散文に貼ると赤になること**（2026-08-30 追加）。
  #   ★ これは 2026-08-30 に**私が実際にやった**事故である（`.steering/` の記録に実値 45 文字）。
  #   ⚠️ 既存の 3 本（ファイル名 / endpoint の形 / 未無視）は 1 本も捕まえられなかった。
  #   ★ selftest の中だけで偽の設定を作る（⚠️ 本物の `Form_O1/o1_submit.json` は 1 バイトも読まない）。
  # ⚠️★★ **設定ファイル自身は無視させる**。★ そうしないと既存の (a)(c)
  #   （提出設定のファイル名 / 未無視）が先に発火し、⚠️ **別の理由の赤を
  #   「値の混入を捕まえた」と読み違える**（★ 2026-08-30 に実際にそうなった）。
  # ⚠️★★★ **対照用の secret を 1 つの文字列でソースに書かない**（2026-08-30 実測）。
  #   ★ 書くと、写した `scripts/gate.sh` **自身**が針に一致し、⚠️ 陰性対照が常に赤になる
  #     （= 検査の自己参照。★ 本番では針は実 secret なのでゲートには現れず、起きない）。
  #   → ★ 実行時に連結して作る。⚠️ 連続した 16 文字がソースに存在しない形にする。
  plant_secret () { printf '%s%s%s' 'SELFTEST' 'SECRET01' '23456789abcdef'; }
  plant_config () {
    printf 'Form_O1/o1_submit.json\n' > "$fix/w/.gitignore"
    printf '{"endpoint":"https://script.google.com/macros/s/%s/exec","secret":"%s"}\n' \
      "SELFTESTSELFTESTSELFTESTSELFTESTSELFTESTSELF" "$(plant_secret)" \
      > "$fix/w/Form_O1/o1_submit.json"
  }
  build; plant_config
  printf 'ここに秘密を貼ってしまった: %s\n' "$(plant_secret | cut -c1-16)" > "$fix/w/docs/leaked-note.md"
  expect_red "実 secret の値" "★ secret の値を散文に貼ると赤になる"
  # ⚠️★ 対照: 貼っていなければ緑のまま（★ 検査が常に赤くなる作りになっていないこと）。
  build; plant_config
  expect_green "値の混入も無い" "★ 貼っていなければ緑のまま（陰性対照）"
  # ⚠️★★★ **設定が無い機械では「未判定」と見えること**（cross-review HIGH・2026-08-30）。
  #   ★ 旧版はここで黙って skip し、⚠️ **一括の緑に紛れて見えなくなっていた**。
  #   ⚠️ `plant_config` を呼ばない ＝ CI や新しい clone と同じ状態にする。
  build
  out=$(bash "$fix/w/scripts/gate.sh" 2>&1)
  if printf '%s\n' "$out" | grep -q "実 secret の値が散文に混入していないか"; then
    echo "  ✅ 満たすと緑になる: ★ 設定が無ければ「未判定」と画面に出る"; sp=$((sp+1))
  else
    echo "  ❌ 満たしても赤のまま: ★ 設定が無いのに未判定と出ない（★ 緑に紛れている）"; sf=$((sf+1))
  fi

  # ⚠️★★★ **移植性ゲート自身の変異試験**（2026-08-29 に追加）。
  #   ★ 新しく足した検査に対照を付けないと、⚠️ **それが空回りしても誰も気づかない**。
  #   ⚠️ ★ **`sed_i` を使わない**: 仕込むのは「変数 ＋ 多バイト」であり、
  #     ★ 置換文字列にそれを書くと**このファイル自身が移植性ゲートに引っかかる**。
  #     → 全角括弧を `printf` の引数として渡し、追記する。
  build; printf '\n# %s\necho "$why%s"\n' "仕込み" '）' >> "$fix/w/scripts/sync-session.sh"
  expect_red "壊れる書き方が残っている" "★ 移植性ゲート: 括り忘れを仕込むと赤になる"

  build; rm -f "$fix/w/scripts/check-shell-portability.sh"
  expect_red "シェル移植性ゲートが無い" "★ 移植性ゲート自体が消えたら赤になる"

  echo
  echo "=== selftest 2: 未達を満たすと緑に変わるか（★ 陽性対照）==="
  # ⚠️★★★ **実測の記録とコードの修正が「両方そろって」初めて緑にする。**
  #   ★ 旧版は `grep from_secs(180)` ただ 1 本だったので、**数字を書き換えるだけで緑**になった。
  #   ★ liveness の陽性対照は selftest 1（壊すと赤）へ移した（= repo 側が緑になったため）。
  build; blank_measure; fill_measure; fix_timeout; expect_green "実測にもとづいて見直されている" "送信 timeout（実測 ＋ 修正）"

  # ⚠️★★★ ADR-031: **送出元 ＋ 承認マーカ ＋ 同意の門がそろうと緑**（★ M5 後の正しい姿）。
  build; printf '\nfn wired() { activity_label_answered(); activity_label_allowed(true, true); }\n' >> "$fix/w/$EMITTER"
  printf '\n<!-- o1-esm-consent: approved -->\n' >> "$cons"
  expect_green "同意の ESM 追補が承認済み" "計器と同意の連動（送出元 ＋ 承認）"
  # ⚠️★★★ **送出元があるのに同意の門を通していないと赤**（★ M5 の穴）。
  build; printf '\nfn wired() { activity_label_answered(); }\n' >> "$fix/w/$EMITTER"
  printf '\n<!-- o1-esm-consent: approved -->\n' >> "$cons"
  expect_red "同意の門を通っていない" "送出元はあるが同意の門を通していない"

  # ⚠️★★★ **O1 実装を含むタグを作ると緑に変わること**（2026-08-30 追加）。
  #   ★ 一時ツリーは `git init` しただけでタグが 1 つも無いので、既定では赤い
  #     ＝ 本物の repo と同じ状態である。→ ★ タグを打って緑に変わることを確かめる。
  #   ⚠️ `o1.rs` が**そのタグの中にある**ことまで見ているか（＝ タグの新しさで代用していないか）は
  #     直後の selftest 3 で撃つ。
  build
  mkdir -p "$fix/w/src-tauri/src"
  printf 'pub const MARKER_FILE_NAME: &str = "o1.mode";\n' > "$fix/w/src-tauri/src/o1.rs"
  git -C "$fix/w" add -A > /dev/null 2>&1
  git -C "$fix/w" -c user.email=s@e -c user.name=s commit -qm selftest > /dev/null 2>&1
  git -C "$fix/w" tag v9.9.9 > /dev/null 2>&1
  expect_green "O1 実装を含むリリースタグがある" "★ O1 を含むタグを切ると緑になる"

  echo
  echo "=== selftest 3: 片方だけでは緑にしない（★ 部分的な修正で騙されないか）==="
  # ⚠️★★ Windows が O1 の主ターゲットである。★ `.ps1` だけ壊れていても**必ず赤にする**
  #   （片方だけ見ていると、もう片方の OS から O1 が dataset へ漏れる）。
  build; sed_i 's/gse_o1_/gse_XX_/g' "$fix/w/scripts/sync-session.ps1"; expect_red "sync-session" "ps1 だけ壊しても赤になる"
  build; sed_i 's/gse_o1_/gse_XX_/g' "$fix/w/scripts/sync-session.sh";  expect_red "sync-session" "sh だけ壊しても赤になる"
  # ⚠️★★★ **A-2 の肝**: 片方だけでは緑にしない（★「見えないまま緑」への抜け道を塞ぐ）。
  build; blank_measure; fix_timeout; expect_red "未実測" "コードだけ直しても赤になる（実測が無い）"
  build; blank_measure; fill_measure; expect_red "180 秒固定のまま" "記録だけ埋めても赤になる（コードが古い）"
  # ★「状態」だけ実測済みにして必須欄が空なら赤（⚠️ 中身の無い記録で緑にしない）。
  build; blank_measure_fields; fix_timeout; expect_red "必須欄が埋まっていない" "必須欄が空なら赤になる"
  # ⚠️★★★ **タグの新しさで代用していないこと**（2026-08-30 追加・本セッションの事故そのもの）。
  #   ★ `v0.1.29` は「実在する最新タグ」だったが `o1.rs` を含まなかった。
  #   → ★ **o1.rs を含まないタグ**を打っても赤のままであることを確かめる。
  build
  git -C "$fix/w" add -A > /dev/null 2>&1
  git -C "$fix/w" -c user.email=s@e -c user.name=s commit -qm selftest > /dev/null 2>&1
  git -C "$fix/w" tag v9.9.8 > /dev/null 2>&1
  expect_red "リリースタグが 1 つも無い" "★ o1.rs を含まないタグを打っても赤のまま"

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
