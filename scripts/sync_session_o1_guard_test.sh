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

# --- 陽性対照: 通常セッションは **弾かない** ------------------------------------
# ⚠️★ ここで exit 4 が返ったら「全部弾く実装」である。
#   ★ dataset が無いので exit 1 になるのが正しい（＝ ガードを通り抜けて先へ進んだ証拠）。
f=$(mk "gse_20260828_120000.ndjson" "$META_PLAIN")
rc=$(run_sh "$f")
if [ "$rc" = "$EXIT_O1" ]; then
  echo "  ❌ ★ 陽性対照: 通常セッションまで弾いている（exit $rc）"; FAIL=$((FAIL+1))
else
  echo "  ✅ ★ 陽性対照: 通常セッションは弾かれず先へ進む（exit $rc）"; PASS=$((PASS+1))
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
PWSH=""
for c in pwsh powershell; do command -v "$c" > /dev/null 2>&1 && { PWSH="$c"; break; }; done

if [ -z "$PWSH" ]; then
  echo "  ⚠️ pwsh / powershell が無いので .ps1 は実行できませんでした（★ 飛ばしています）"
  echo "  ⚠️ ★ Windows は O1 の主ターゲットです。★ Windows 上で必ず 1 回は走らせること。"
  SKIPPED=1
else
  SKIPPED=0
  # ⚠️★★ `-RepoRoot` に実在しないパスを渡す。★ 渡さないと既定が本物の repo になり、
  #   **陽性対照が本物の `cargo run` を走らせる**（実測: ビルドが新しければ約 1 秒だが、
  #   古ければ数分。⚠️ 本テストはゲートから 1 回のゲート実行ごとに呼ばれるので、
  #   そこに実ビルドをぶら下げてはいけない）。
  #   ★ 陽性対照が見たいのは「exit 4 でないこと」だけであり、cargo を走らせる必要は無い。
  run_ps () {
    "$PWSH" -NoProfile -ExecutionPolicy Bypass -File "$PS1F" \
      -SessionPath "$1" -DatasetRoot "$GSE_DATASET" -RepoRoot "$TMP/no-such-repo" -NoCommit \
      > /dev/null 2>&1
    echo $?
  }
  f=$(mk "gse_o1_ps_name.ndjson" "$META_PLAIN")
  check "名前が gse_o1_ なら弾く" "$EXIT_O1" "$(run_ps "$f")"

  f=$(mk "renamed_ps.ndjson" "$META_O1")
  check "★ 名前を変えても meta の o1_mode で弾く" "$EXIT_O1" "$(run_ps "$f")"

  f=$(mk "gse_20260828_ps.ndjson" "$META_PLAIN")
  rc=$(run_ps "$f")
  if [ "$rc" = "$EXIT_O1" ]; then
    echo "  ❌ ★ 陽性対照: 通常セッションまで弾いている（exit $rc）"; FAIL=$((FAIL+1))
  else
    echo "  ✅ ★ 陽性対照: 通常セッションは弾かれず先へ進む（exit $rc）"; PASS=$((PASS+1))
  fi
fi

echo
echo "────────────────────────────────────────"
echo "  通過 $PASS 件 / 失敗 $FAIL 件"
if [ "$FAIL" -eq 0 ]; then
  if [ "${SKIPPED:-0}" -eq 1 ]; then
    echo "  ⚠️ sh は緑。★ ただし .ps1 は**未実行**（PowerShell が無い）。"
  else
    echo "  ✅ 両方のガードが実際に弾いている。"
  fi
  exit 0
fi
echo "  ❌ 上の ❌ を直すこと。"
exit 1
