#!/usr/bin/env bash
# ★ `sync-session.*` の **O1 ガードが実際に弾く**ことを実測する。
#
# ⚠️★★★ なぜ要るか（`docs/o1-deletion-ledger.md` §4）:
#   gse-dataset の `metrics/` は git で追跡・push されている（2026-08-28 に 34 件を実測）。
#   ★ O1 は「あとから『この時間帯を消して』と言える」と約束しているので、
#   ⚠️ 一度 push すると、その削除は **git 履歴の書き換え**になる。
#
# ⚠️ ★ 「`gse_o1_` という語がスクリプトに出てくる」は**弾く証拠にならない**
#   （`check-o1-release-readiness.sh` はそこまでしか見ていないと自分で明記している）。
#   ★ 本ファイルが、実際に走らせて exit code を見る役目を持つ。
#
# ★ 陽性対照（通常セッションは弾かない）を必ず含める。
#   ⚠️ 含めないと、**全部弾く実装**でも緑になる。
#
# 使い方: bash scripts/sync_session_o1_guard_test.sh
# 終了コード: 0 = 期待どおり / 1 = 期待と違う

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SH="scripts/sync-session.sh"
PS1F="scripts/sync-session.ps1"
EXIT_O1=4

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ⚠️★ dataset を実在させない。★ ガードは dataset の検査**より前**に効くはずである
#   （効いていなければ「dataset が無い」の exit 1 になり、この検査が気づく）。
export GSE_DATASET="$TMP/no-such-dataset"

META_O1='{"type":"meta","session_start":1000,"hmm_version":"0.5.0","o1_mode":"marker"}'
META_PLAIN='{"type":"meta","session_start":1000,"hmm_version":"0.5.0"}'

mk () { # $1 = ファイル名 / $2 = meta 行
  local f="$TMP/$1"
  printf '%s\n{"type":"feat","t":1000}\n' "$2" > "$f"
  printf '%s' "$f"
}

PASS=0; FAIL=0
check () { # $1 = 説明 / $2 = 期待 exit / $3 = 実際 exit
  if [ "$2" = "$3" ]; then
    echo "  ✅ $1（exit $3）"; PASS=$((PASS+1))
  else
    echo "  ❌ $1（期待 exit $2 / 実際 $3）"; FAIL=$((FAIL+1))
  fi
}

run_sh () { bash "$SH" "$1" --no-commit > /dev/null 2>&1; echo $?; }

echo "=== sync-session.sh ==="

# --- 陰性対照 1: 名前で弾く -----------------------------------------------------
f=$(mk "gse_o1_20260828_120000.ndjson" "$META_PLAIN")
check "名前が gse_o1_ なら弾く" "$EXIT_O1" "$(run_sh "$f")"

# --- 陰性対照 2: 中身で弾く（★ 名前を変えられても中身は変わらない）--------------
f=$(mk "renamed_session.ndjson" "$META_O1")
check "★ 名前を変えても meta の o1_mode で弾く" "$EXIT_O1" "$(run_sh "$f")"

# --- 陰性対照 3: ⚠️ クラウド同期の競合コピー（引き継ぎ §2 #2 の名前）------------
f=$(mk "gse_o1_20260828_120000-DESKTOP-ABC.ndjson" "$META_O1")
check "⚠️ 競合コピー名でも弾く" "$EXIT_O1" "$(run_sh "$f")"

# --- 陰性対照 4: meta 行が 1 行目でなくても弾く ---------------------------------
f="$TMP/late_meta.ndjson"
{ echo '{"type":"feat","t":1}'; echo '{"type":"feat","t":2}'; echo "$META_O1"; } > "$f"
check "★ meta 行が 3 行目でも弾く" "$EXIT_O1" "$(run_sh "$f")"

# --- 陰性対照 5: ⚠️ 大文字（★ PowerShell の -like は元から区別しない）------------
# ★ 区別すると「Windows では弾かれ macOS では通る」＝ 片方の OS だけ漏れる。
f=$(mk "GSE_O1_20260828_120000.ndjson" "$META_PLAIN")
check "⚠️ 大文字の名前でも弾く（2 実装で規則を揃える）" "$EXIT_O1" "$(run_sh "$f")"

# --- 陰性対照 6: ⚠️★★ 大きいファイルでも弾く（SIGPIPE の fail-open 検査）---------
# ★ `head -n 20 | grep -q` だと grep が即座に閉じて head が SIGPIPE で死に、
#   `set -o pipefail` のもとでパイプが 141 を返す → ⚠️ **一致したのに弾かない**。
#   ★ 先頭行が長いほど再現しやすいので、実セッションより大きい行で測る。
f="$TMP/big_o1.ndjson"
{ echo "$META_O1"; head -c 400000 /dev/zero | tr '\0' 'x' | sed 's/^/{"pad":"/;s/$/"}/'; } > "$f"
check "⚠️★★ 大きいファイルでも meta で弾く（SIGPIPE で fail-open しない）" "$EXIT_O1" "$(run_sh "$f")"

# --- ⚠️★ 境界を隠さない: meta が 21 行目だと **見逃す** -------------------------
# ★ ガードは先頭 20 行しか見ない。⚠️ これは**設計上の限界**であり、
#   ここで「見逃す」ことを**わざと固定する**（★ 直したくなったら本ケースを直す）。
#   ⚠️ 実運用では `meta` は必ず先頭付近に来る（`logger.rs` が最初に書く）。
#   ★ 名前が `gse_o1_*` なら第 1 の根拠で弾けるので、実害は「改名 ＋ meta が 21 行目以降」に限る。
f="$TMP/meta_line21.ndjson"
{ for i in $(seq 1 20); do echo "{\"type\":\"feat\",\"t\":$i}"; done; echo "$META_O1"; } > "$f"
rc=$(run_sh "$f")
if [ "$rc" = "$EXIT_O1" ]; then
  echo "  ✅ ★ meta が 21 行目でも弾けた（★ 期待より強い。本ケースを更新すること）"; PASS=$((PASS+1))
else
  echo "  ✅ ⚠️ meta が 21 行目だと見逃す（★ 設計上の限界として固定・exit ${rc}）"; PASS=$((PASS+1))
fi

# --- ⚠️ 読めないファイル: ★ ここで判定せず下流に任せる ---------------------------
f="$TMP/missing.ndjson"   # ★ 作らない
rc=$(run_sh "$f")
if [ "$rc" = "$EXIT_O1" ]; then
  echo "  ❌ 存在しないファイルを O1 として弾いている（exit ${rc}）"; FAIL=$((FAIL+1))
else
  echo "  ✅ ★ 読めないファイルはここで判定しない（下流に任せる・exit ${rc}）"; PASS=$((PASS+1))
fi

# --- 陽性対照: 通常セッションは **弾かない** ------------------------------------
# ⚠️★ ここで exit 4 が返ったら「全部弾く実装」である。
#   ★ dataset が無いので exit 1 になるのが正しい（＝ ガードを通り抜けて先へ進んだ証拠）。
f=$(mk "gse_20260828_120000.ndjson" "$META_PLAIN")
rc=$(run_sh "$f")
if [ "$rc" = "$EXIT_O1" ]; then
  echo "  ❌ ★ 陽性対照: 通常セッションまで弾いている（exit ${rc}）"; FAIL=$((FAIL+1))
else
  echo "  ✅ ★ 陽性対照: 通常セッションは弾かれず先へ進む（exit ${rc}）"; PASS=$((PASS+1))
fi

# --- ⚠️ ガードが dataset の検査より前にあること --------------------------------
# ★ 上の陰性対照が exit 4 を返せている時点で示されている（dataset は実在しない）。
#   ⚠️ ここでは「そのことを明示的に 1 件数える」だけにする。
f=$(mk "gse_o1_ordering.ndjson" "$META_PLAIN")
check "★ dataset が無くても弾ける（＝ 検査順が正しい）" "$EXIT_O1" "$(run_sh "$f")"

echo
echo "=== sync-session.ps1 ==="
# ⚠️★ PowerShell が無い機械（CI の macOS 等）では**実行できない**。
#   ★ そのときは「実行できなかった」と出して**緑にしない**（飛ばしたことを隠さない）。
# ⚠️★★★ **見つかった実行系を「全部」走らせる**（2026-08-30 に方針変更）:
#   ★ `pwsh`（PowerShell 7+ = **Core**）と `powershell.exe`（Windows PowerShell 5.1 = **Desktop**）は
#     **別物**である。⚠️ 5.1 は BOM 無しスクリプトを `[Text.Encoding]::Default`（CP932）で読むため、
#     ★ **日本語のバイト列で parse が壊れる**（`docs/development-guidelines.md` §10.2 に実害の記録）。
#     `sync-session.ps1` は日本語コメントを多く含むので、まさにこの差が効く。
#   ⚠️★★ **旧版は「最初に見つかった 1 つ」だけを使っていた**（`pwsh` 優先）。
#     → ★ **pwsh を入れた Windows 機では 5.1 が永久に検証されない**ことになる。
#     ⚠️ このリポジトリが繰り返し踏んでいる「片方だけ緑で安心する」型そのもの。
#   ★ 機械可読マーカ `PS1_VERIFIED:` に**検証できたエディションを列挙**する
#     （`check-o1-release-readiness.sh` が読む。⚠️ 文言だけ変えないこと）。
PS_FOUND=""
for c in pwsh powershell; do
  command -v "$c" > /dev/null 2>&1 && PS_FOUND="${PS_FOUND} ${c}"
done

# ⚠️★★ `-RepoRoot` に実在しないパスを渡す。★ 渡さないと既定が本物の repo になり、
#   **陽性対照が本物の `cargo run` を走らせる**（実測: ビルドが新しければ約 1 秒だが、
#   古ければ数分。⚠️ 本テストはゲートから 1 回のゲート実行ごとに呼ばれるので、
#   そこに実ビルドをぶら下げてはいけない）。
#   ★ 陽性対照が見たいのは「exit 4 でないこと」だけであり、cargo を走らせる必要は無い。
run_ps () { # $1 = 実行系 / $2 = セッションパス
  "$1" -NoProfile -ExecutionPolicy Bypass -File "$PS1F" \
    -SessionPath "$2" -DatasetRoot "$GSE_DATASET" -RepoRoot "$TMP/no-such-repo" -NoCommit \
    > /dev/null 2>&1
  echo $?
}

PS_EDITIONS=""     # ★ 実際に**全ケース緑**になったエディションだけを積む
if [ -z "${PS_FOUND# }" ]; then
  echo "  ⚠️ pwsh / powershell が無いので .ps1 は実行できませんでした（★ 飛ばしています）"
  echo "  ⚠️ ★ Windows は O1 の主ターゲットです。★ Windows 上で必ず 1 回は走らせること。"
  SKIPPED=1
else
  SKIPPED=0
  for PS in ${PS_FOUND}; do
    ed="$("$PS" -NoProfile -Command '$PSVersionTable.PSEdition' 2>/dev/null | tr -d '\r\n ')"
    ver="$("$PS" -NoProfile -Command '$PSVersionTable.PSVersion.ToString()' 2>/dev/null | tr -d '\r\n ')"
    echo "  --- 実行系: ${PS}（${ed:-エディション不明} ${ver:-版不明}）"
    before_fail=$FAIL

    f=$(mk "gse_o1_ps_name_${PS}.ndjson" "$META_PLAIN")
    check "[${ed:-?}] 名前が gse_o1_ なら弾く" "$EXIT_O1" "$(run_ps "$PS" "$f")"

    f=$(mk "renamed_ps_${PS}.ndjson" "$META_O1")
    check "[${ed:-?}] ★ 名前を変えても meta の o1_mode で弾く" "$EXIT_O1" "$(run_ps "$PS" "$f")"

    f=$(mk "gse_20260828_ps_${PS}.ndjson" "$META_PLAIN")
    rc=$(run_ps "$PS" "$f")
    if [ "$rc" = "$EXIT_O1" ]; then
      echo "  ❌ [${ed:-?}] ★ 陽性対照: 通常セッションまで弾いている（exit ${rc}）"; FAIL=$((FAIL+1))
    else
      echo "  ✅ [${ed:-?}] ★ 陽性対照: 通常セッションは弾かれず先へ進む（exit ${rc}）"; PASS=$((PASS+1))
    fi

    # ★ その実行系で 1 件も落ちなかったときだけ「検証できた」と数える。
    if [ "$FAIL" -eq "$before_fail" ] && [ -n "${ed}" ]; then
      PS_EDITIONS="${PS_EDITIONS} $(printf '%s' "${ed}" | tr '[:upper:]' '[:lower:]')/${ver}"
    fi
  done
fi

echo
echo "────────────────────────────────────────"
echo "  通過 $PASS 件 / 失敗 $FAIL 件"

# ★ 機械可読マーカ（⚠️ `check-o1-release-readiness.sh` が読む。文言だけ変えないこと）。
#   ★ 値は**全ケース緑になったエディションの列挙**（例: `core/7.6.5`, `desktop/5.1.x core/7.4.0`）。
#   ⚠️ `none` = 1 度も走らせていない。
PS1_LIST="${PS_EDITIONS# }"
if [ "${SKIPPED:-0}" -eq 1 ] || [ -z "${PS1_LIST}" ]; then
  echo "PS1_VERIFIED: none"
else
  echo "PS1_VERIFIED: ${PS1_LIST}"
fi

if [ "$FAIL" -eq 0 ]; then
  if [ "${SKIPPED:-0}" -eq 1 ]; then
    echo "  ⚠️ sh は緑。★ ただし .ps1 は**未実行**（PowerShell が無い）。"
  elif printf '%s' "${PS1_LIST}" | grep -q 'desktop/'; then
    echo "  ✅ 両方のガードが実際に弾いている（★ 検証した実行系: ${PS1_LIST}）。"
    echo "     ★ Windows PowerShell (Desktop) を含む ＝ 研究者が Windows で実際に使う実行系。"
  else
    echo "  ✅ .ps1 のガードも弾いている（★ 検証した実行系: ${PS1_LIST}）。"
    echo "  ⚠️★★ ただし **Windows PowerShell 5.1 (Desktop) は未検証**である。"
    echo "     ★ 5.1 は BOM 無しを CP932 で読むので、日本語コメントで parse が壊れる型がある"
    echo "       (docs/development-guidelines.md §10.2)。⚠️ O1 の主ターゲットは Windows。"
    echo "     ★ Windows で作業するとき、ついでに本スクリプトを 1 回走らせること:"
    echo "       bash scripts/sync_session_o1_guard_test.sh   （★ git-bash から）"
  fi
  exit 0
fi
echo "  ❌ 上の ❌ を直すこと。"
exit 1
