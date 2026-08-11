#!/usr/bin/env bash
# Step 0 の主張を検査する再現スクリプト（verify-before-claiming ルール 6）。
#
# ★ 設計上の要点: toeexpand の終了コードは「成功=1 / 失敗=0」に反転している。
#    したがって本スクリプトは **一度も終了コードで expand の成否を判定しない**。
#    判定は必ず「出力に expanded into directory が出たか」＋「.dir / .toc が実在するか」で行う。
#
# 使い方:
#   bash .steering/20260811-expression-prototype-step0/scripts/step0-verify.sh [作業ディレクトリ]
#
# 終了コード: 0 = 全 CHECK PASS / 1 = 1 件以上 FAIL

set -u

TD_ROOT="${TD_ROOT:-/c/Program Files/Derivative/TouchDesigner}"
TOEEXPAND="$TD_ROOT/bin/toeexpand.exe"
TOECOLLAPSE="$TD_ROOT/bin/toecollapse.exe"
TEMPLATE="$TD_ROOT/Samples/Setup/Base/NewProject.toe"
SAMPLE_TOX="$TD_ROOT/Samples/Palette/Mapping/stoner.tox"

# ⚠️ 作業ディレクトリは毎回 **新しく作る**。
#    既存ディレクトリをそのまま使い回すと (a) 前回の tree_before の中に入れ子コピーが積まれ、
#    後段の diff -r が偽 FAIL を出す、(b) 引数に渡された既存ディレクトリの中身を無確認で上書きする。
#    → mktemp -d で衝突しない新規ディレクトリを掘る（第 1 引数はその「親」として扱う）。
WORK_PARENT="${1:-${TMPDIR:-/tmp}}"
mkdir -p "$WORK_PARENT" || exit 1
WORK="$(mktemp -d "$WORK_PARENT/gse-step0-verify-XXXXXX")" || exit 1
printf 'work dir: %s\n' "$WORK"

# ⚠️ 後始末: 1 回の実行で .tox 側だけで 1,542 ファイル・計 35 MB 程度を展開するので、
#   既定では終了時に消す。中身を見たいときは KEEP_WORK=1 を付ける。
if [ "${KEEP_WORK:-0}" = "1" ]; then
  trap 'printf "work dir を残しました: %s\n" "$WORK"' EXIT
else
  trap 'rm -rf "$WORK"' EXIT
fi

PASS=0
FAIL=0
ok()   { PASS=$((PASS + 1)); printf '  [PASS] %s\n' "$1"; }
bad()  { FAIL=$((FAIL + 1)); printf '  [FAIL] %s\n' "$1"; }
head_() { printf '\n== %s ==\n' "$1"; }

# --- expand を「出力で」判定するラッパ（★ 終了コードを見ない） ---
# 使い方: expand_ok <dir> <file>  → 成功なら 0 を返す
expand_ok() {
  local d="$1" f="$2" out
  out="$(cd "$d" && "$TOEEXPAND" "$f" 2>&1)"
  case "$out" in
    *"expanded into directory"*) ;;
    *) return 1 ;;
  esac
  [ -d "$d/$f.dir" ] && [ -f "$d/$f.toc" ]
}

# --- collapse は exit 0 かつ "moved to" かつ **警告が無いこと** を要求する ---
#
# ⚠️★★★ ここが本スクリプト最大の落とし穴だった（security-checker の指摘・2026-08-11 に実測で確認）:
#   ツリーからファイルが 1 つ欠けていても、toecollapse は
#     exit=0 / "N.toe moved to N.toe.bkp1" / "Warning. Unable to find file N.toe.dir/perform.parm"
#   を返し、**欠損したまま別内容の .toe を書き出す**。
#   → 「exit 0 かつ moved to」だけを見る判定は **欠損を成功として通してしまう**（silent pass）。
#   ★ したがって出力に Warning / Unable to find が出たら **FAIL にする**。
collapse_ok() {
  local d="$1" f="$2" out rc
  out="$(cd "$d" && "$TOECOLLAPSE" "$f.dir" 2>&1)"; rc=$?
  [ "$rc" -eq 0 ] || return 1
  # ★ 警告の検出を "moved to" の確認より先に行う（順序を変えない）
  case "$out" in
    *"Warning"*|*"Unable to find"*) return 1 ;;
  esac
  case "$out" in *"moved to"*) return 0 ;; *) return 1 ;; esac
}

head_ "0. 実体の存在"
for p in "$TOEEXPAND" "$TOECOLLAPSE" "$TEMPLATE"; do
  if [ -f "$p" ]; then ok "exists: $(basename "$p")"; else bad "MISSING: $p"; fi
done
[ -f "$TOEEXPAND" ] || { echo "toeexpand が無いので中断"; exit 1; }

head_ "1. ★ toeexpand の終了コードが反転していること（成功=1 / 失敗=0）"
mkdir -p "$WORK/ec"; cd "$WORK/ec" || exit 1
cp "$TEMPLATE" ok.toe
printf 'not a toe\n' > junk.toe

"$TOEEXPAND" >/dev/null 2>&1; rc_usage=$?
"$TOEEXPAND" nosuch.toe >/dev/null 2>&1; rc_missing=$?
"$TOEEXPAND" ok.toe >/dev/null 2>&1; rc_success=$?
"$TOEEXPAND" junk.toe >/dev/null 2>&1; rc_junk=$?

[ "$rc_success" -eq 1 ] && ok "成功時 exit=1 (反転を確認)" || bad "成功時 exit=$rc_success (期待 1)"
[ "$rc_missing" -eq 0 ] && ok "不在ファイルで exit=0 (反転を確認)" || bad "不在時 exit=$rc_missing (期待 0)"
[ "$rc_junk" -eq 0 ]    && ok "壊れたファイルで exit=0 (反転を確認)" || bad "壊れ時 exit=$rc_junk (期待 0)"
[ "$rc_usage" -eq 1 ]   && ok "引数なし exit=1" || bad "引数なし exit=$rc_usage (期待 1)"
# ★ 失敗が本当に失敗であること（dir を作っていないこと）を中身で確認する
[ ! -d nosuch.toe.dir ] && [ ! -d junk.toe.dir ] && ok "失敗ケースは .dir を作っていない" \
  || bad "失敗のはずのケースが .dir を作っている"

head_ "2. (a) 展開ツリーがテキストか"
mkdir -p "$WORK/a"; cd "$WORK/a" || exit 1
cp "$TEMPLATE" NewProject.toe
if expand_ok "$WORK/a" NewProject.toe; then
  ok "expand 成功 (出力で判定)"
  n_all=$(find NewProject.toe.dir -type f | wc -l)
  n_txt=$(find NewProject.toe.dir -type f -print0 | xargs -0 grep -lI '' 2>/dev/null | wc -l)
  [ "$n_all" -gt 0 ] && ok "展開ファイル数: $n_all" || bad "展開ファイルが 0"
  [ "$n_txt" -eq "$n_all" ] && ok "全 $n_all ファイルがテキスト" || bad "テキストは $n_txt/$n_all"
  grep -q '^COMP:container' NewProject.toe.dir/project1.n \
    && ok "project1.n が期待どおりのテキスト構造" || bad "project1.n の中身が想定と違う"
else
  bad "expand に失敗"
fi

head_ "3. (b) 素の往復でツリーが保存されるか"
# ⚠️★★ ここは以前 silent pass を持っていた（code-reviewer の指摘）:
#   collapse が失敗すると .toe は原本のまま残るので、再 expand したツリーは当然 tree_before と
#   一致し、「往復後の展開ツリーが完全一致」が**往復していないのに PASS** してしまっていた。
#   → collapse 成功を入れ子の条件にし、**collapse が新しくファイルを書いた証拠**を要求する。
#   ⚠️ 証拠に「.toe の sha256 が変わったこと」は使えない —— この空テンプレートは
#      **往復しても byte 一致する**（実測: 9079fb72b6e9 -> 9079fb72b6e9）ので、
#      変化を要求すると正しい往復を FAIL にしてしまう。
#      → 代わりに **`.bkp*` が新規に作られたこと**（＝原本を退避して書き直したこと）を要求する。
cp -r NewProject.toe.dir "$WORK/a/tree_before"
sha_before="$(sha256sum NewProject.toe | cut -d' ' -f1)"
[ -e NewProject.toe.bkp1 ] && bad "テスト開始前に .bkp1 が存在する（証拠として使えない）"
if collapse_ok "$WORK/a" NewProject.toe; then
  ok "collapse 成功 (exit 0 + 'moved to' + 警告なし)"
  # ★ 往復が実際に起きた証拠: バックアップが**新規に**作られたこと
  if [ -e NewProject.toe.bkp1 ]; then
    ok "往復の証拠: バックアップ (.bkp1) が新規に作られた"
  else
    bad "collapse は成功と言うがバックアップが無い（往復していない疑い）"
  fi
  sha_after="$(sha256sum NewProject.toe | cut -d' ' -f1)"
  printf '  (参考) .toe sha256: %s -> %s （このテンプレートは byte 一致が正常）\n' \
    "${sha_before:0:12}" "${sha_after:0:12}"

  mkdir -p "$WORK/a2"; cp NewProject.toe "$WORK/a2/NewProject.toe"
  if expand_ok "$WORK/a2" NewProject.toe; then
    if diff -r "$WORK/a/tree_before" "$WORK/a2/NewProject.toe.dir" >/dev/null 2>&1; then
      ok "往復後の展開ツリーが完全一致"
    else
      bad "往復でツリーに差分が出た"
    fi
  else
    bad "往復後の再 expand に失敗"
  fi
else
  bad "collapse に失敗（往復検査は実行しない）"
fi

head_ "4. ★ 編集が往復に耐えるか（長さを変える編集）"
mkdir -p "$WORK/e"; cd "$WORK/e" || exit 1
cp "$TEMPLATE" Edited.toe
if expand_ok "$WORK/e" Edited.toe; then
  # コメント行を「元より長い」文字列へ書き換える
  sed -i 's/^comment "Perform Mode configuration:.*$/comment "GSE-STEP0-EDIT-MARKER-deliberately-longer-than-the-original-comment-line"/' \
    Edited.toe.dir/perform.n
  grep -q 'GSE-STEP0-EDIT-MARKER' Edited.toe.dir/perform.n \
    && ok "編集を適用した" || bad "編集の適用に失敗（sed パターン不一致）"
  if collapse_ok "$WORK/e" Edited.toe; then
    mkdir -p "$WORK/e2"; cp Edited.toe "$WORK/e2/Edited.toe"
    if expand_ok "$WORK/e2" Edited.toe; then
      grep -q 'GSE-STEP0-EDIT-MARKER' "$WORK/e2/Edited.toe.dir/perform.n" \
        && ok "★ 編集が往復後も生きている" || bad "★ 編集が往復で失われた"
      if diff -r Edited.toe.dir "$WORK/e2/Edited.toe.dir" >/dev/null 2>&1; then
        ok "編集箇所以外に副作用なし"
      else
        bad "編集箇所以外に差分が出た"
      fi
    else bad "編集後の再 expand に失敗"; fi
  else bad "編集後の collapse に失敗"; fi
else
  bad "編集テストの expand に失敗"
fi

head_ "5. ★ .toc が無いと collapse は失敗する（かつ .toe を壊さない）"
mkdir -p "$WORK/t" || exit 1
cd "$WORK/t" || exit 1
cp "$TEMPLATE" NoToc.toe
if expand_ok "$WORK/t" NoToc.toe; then
  before="$(sha256sum NoToc.toe | cut -d' ' -f1)"
  mv NoToc.toe.toc NoToc.toc.hidden
  out="$("$TOECOLLAPSE" NoToc.toe.dir 2>&1)"; rc=$?
  after="$(sha256sum NoToc.toe | cut -d' ' -f1)"
  [ "$rc" -ne 0 ] && ok ".toc 不在で collapse がエラーを返す (exit=$rc)" || bad ".toc 不在なのに exit 0"
  case "$out" in *"requires"*) ok "エラー内容が .toc 要求である" ;; *) bad "想定外のエラー: $out" ;; esac
  [ "$before" = "$after" ] && ok "失敗しても元の .toe を壊さない" || bad "失敗時に .toe が書き換わった"
else
  bad ".toc テストの expand に失敗"
fi

head_ "5b. ★★ ツリーが欠けた collapse を PASS にしないか（silent pass の検出）"
# ⚠️ toecollapse は欠損があっても exit 0 + "moved to" を返し、壊れた .toe を書く（実測）。
#    collapse_ok() がそれを FAIL にできることを、実際に壊して確かめる。
mkdir -p "$WORK/miss"; cd "$WORK/miss" || exit 1
cp "$TEMPLATE" Miss.toe
if expand_ok "$WORK/miss" Miss.toe; then
  before_miss="$(sha256sum Miss.toe | cut -d' ' -f1)"
  mv Miss.toe.dir/perform.parm "$WORK/miss/perform.parm.hidden"   # ★ 1 ファイルだけ欠けさせる
  raw="$("$TOECOLLAPSE" Miss.toe.dir 2>&1)"; raw_rc=$?
  after_miss="$(sha256sum Miss.toe | cut -d' ' -f1)"
  # まず「素朴な判定なら通ってしまう」ことを固定する（検査の前提が崩れたら気づけるように）
  if [ "$raw_rc" -eq 0 ] && printf '%s' "$raw" | grep -q "moved to"; then
    ok "前提確認: 欠損しても exit 0 + 'moved to' が返る（素朴な判定は騙される）"
  else
    bad "前提が変わった: 欠損時の挙動が exit=$raw_rc / '$raw'"
  fi
  printf '%s' "$raw" | grep -qE "Warning|Unable to find" \
    && ok "欠損は Warning として出力に現れる" || bad "欠損しても Warning が出ない"
  [ "$before_miss" != "$after_miss" ] \
    && ok "欠損したまま別内容の .toe が書かれる（＝見逃すと壊れる）" \
    || bad "欠損しても .toe が変わらない（前提が違う）"
  # ★ 本題: collapse_ok() はこれを FAIL にしなければならない
  mkdir -p "$WORK/miss2"; cd "$WORK/miss2" || exit 1
  cp "$TEMPLATE" Miss2.toe
  if expand_ok "$WORK/miss2" Miss2.toe; then
    mv Miss2.toe.dir/perform.parm "$WORK/miss2/perform.parm.hidden"
    # ⚠️★★★ 引数は **拡張子込み** で渡すこと（collapse_ok は "$f.dir" を組み立てる）。
    #   初版は `collapse_ok ... Miss2` と書いており、`Miss2.dir` を探して
    #   **「パス不在」で落ちていた** —— つまり Warning 検出が一度も試されないまま PASS していた。
    #   ★ これは本節が検出しようとしている silent pass そのものが、検査側に出た例である
    #     (2 回目のレビューで発見・実測で確認)。
    if collapse_ok "$WORK/miss2" Miss2.toe; then
      bad "★ collapse_ok() が欠損を PASS にした（silent pass が残っている）"
    else
      ok "★ collapse_ok() が欠損を FAIL にした"
    fi
    # ★★ 「FAIL の理由が Warning 検出であること」を確かめる（パス不在などで落ちていないか）。
    #    これを入れないと、検査が別の理由で落ちて通ってしまう（初版がまさにそれだった）。
    raw2="$(cd "$WORK/miss2" && "$TOECOLLAPSE" "Miss2.toe.dir" 2>&1)"; raw2_rc=$?
    if [ "$raw2_rc" -eq 0 ] && printf '%s' "$raw2" | grep -qE "Warning|Unable to find"; then
      ok "★ FAIL の理由が Warning 検出である（exit 0 なのに Warning が出る状態を捕まえている）"
    else
      bad "FAIL の理由が Warning ではない（exit=$raw2_rc / 出力: $(printf '%s' "$raw2" | head -1)）"
    fi
  else
    bad "silent pass テストの expand に失敗"
  fi
else
  bad "silent pass テストの expand に失敗"
fi

head_ "6. .tox でも同じことが成り立つか"
if [ -f "$SAMPLE_TOX" ]; then
  mkdir -p "$WORK/x"; cd "$WORK/x" || exit 1
  cp "$SAMPLE_TOX" s.tox
  if expand_ok "$WORK/x" s.tox; then
    ok ".tox の expand 成功"
    cp -r s.tox.dir tree_before
    if collapse_ok "$WORK/x" s.tox; then
      mkdir -p "$WORK/x2"; cp s.tox "$WORK/x2/s.tox"
      if expand_ok "$WORK/x2" s.tox && diff -r tree_before "$WORK/x2/s.tox.dir" >/dev/null 2>&1; then
        ok "★ .tox の往復でツリーが完全一致"
      else
        bad ".tox の往復でツリーに差分"
      fi
    else bad ".tox の collapse 失敗"; fi
  else bad ".tox の expand 失敗"; fi
else
  printf '  [SKIP] サンプル .tox が無い: %s\n' "$SAMPLE_TOX"
fi

head_ "結果"
printf '  PASS=%s  FAIL=%s\n' "$PASS" "$FAIL"
# ★ 空回り検出: 1 件も検査していないなら赤にする（verify-before-claiming ルール 6）
if [ "$((PASS + FAIL))" -eq 0 ]; then
  echo "  [FAIL] 検査が 1 件も実行されていない（空回り）"
  exit 1
fi
[ "$FAIL" -eq 0 ] && { echo "  → Step 0 の主張は再現した"; exit 0; }
echo "  → 再現しなかった主張がある"
exit 1
