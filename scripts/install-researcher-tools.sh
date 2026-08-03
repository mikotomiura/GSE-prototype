#!/usr/bin/env bash
# 研究者専用 CLI を **この workspace の bin/ に install** する。
#
#   bash scripts/install-researcher-tools.sh            # gse-unpack を入れる
#   bash scripts/install-researcher-tools.sh --with-package   # gse-package も入れる
#   bash scripts/install-researcher-tools.sh --check    # 入っているかだけ見る（ビルドしない）
#
# ★ なぜ要るか
#   gse-unpack (age 復号) は **被験者配布物から意図的に除外**されている
#   (.github/workflows/ci.yml の macOS 再署名ステップが .app から strip する)。
#   したがって研究者は別経路で入手する必要があり、従来は GitHub Release の
#   アセットがその経路だった。★ **リリースは被験者向けに絞りたい**ので、
#   研究者は手元でビルドして workspace に置く運用にする。
#
# ★ 置き場所を bin/ に固定する理由
#   `src-tauri/target/release/` は `cargo clean` や toolchain 更新で消えるうえ、
#   パスが長くて手順書に書きにくい。bin/ に固定すれば
#   `./bin/gse-unpack --input ... --identity ...` と一定の書き方で案内できる。
#   ⚠️ bin/ は .gitignore 済み。**バイナリをコミットしない**
#      (本リポジトリは一時 public にする運用がある)。
set -euo pipefail
cd "$(dirname "$0")/.."

BIN_DIR="bin"
TOOLS=(gse-unpack)
CHECK_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --with-package) TOOLS+=(gse-package) ;;
    --check) CHECK_ONLY=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "[NG] 不明な引数: $arg (使えるのは --with-package / --check)" >&2; exit 2 ;;
  esac
done

ok()   { printf '  [ OK ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; }
note() { printf '  [note] %s\n' "$1"; }

echo "=============================================================="
echo " 研究者専用 CLI の install (${TOOLS[*]})"
echo "=============================================================="

# --- --check: 現状を見るだけ -------------------------------------------------
if [ "$CHECK_ONLY" = "1" ]; then
  FAIL=0
  for t in "${TOOLS[@]}"; do
    # ⚠️ --version は実装されていない (unknown arg 扱い)。存在と起動可否だけを見る。
    # ⚠️ ★ **パイプで判定しない。** `--help` は exit 1 で終わるので、`set -o pipefail` 下では
    #    `cmd --help | grep -q ...` が **grep 成功でもパイプライン全体 1** になり、
    #    正常なバイナリを不合格にする。出力を変数に取ってから中身を見る ([3] と同じ方式)。
    if [ -x "$BIN_DIR/$t" ]; then
      OUT=$("$BIN_DIR/$t" --help 2>&1 || true)
    else
      OUT=""
    fi
    if [ -x "$BIN_DIR/$t" ] && [ "${OUT#*usage:}" != "$OUT" ]; then
      ok "$BIN_DIR/$t (起動確認済み)"
    elif [ -x "$BIN_DIR/$t" ]; then
      bad "$BIN_DIR/$t はあるが起動できない → 引数なしで本スクリプトを実行して入れ直す"
      FAIL=$((FAIL + 1))
    else
      bad "$BIN_DIR/$t が無い → 引数なしで本スクリプトを実行する"
      FAIL=$((FAIL + 1))
    fi
  done
  [ "$FAIL" = "0" ] || exit 1
  exit 0
fi

# --- 前提コマンド (不在を素通りさせない) --------------------------------------
CARGO_BIN=$(command -v cargo || echo "$HOME/.cargo/bin/cargo")
if [ ! -x "$CARGO_BIN" ]; then
  bad "cargo が見つからない ($CARGO_BIN)。Rust toolchain を入れてから再実行する"
  exit 1
fi
ok "cargo = $("$CARGO_BIN" --version)"

# --- ビルド ------------------------------------------------------------------
# ⚠️ `--features package` が要る。gse-unpack / gse-package は
#    Cargo.toml で required-features = ["package"] に隔離されており、
#    既定ビルドでは age crate をリンクしない設計 (アプリ本体を軽く保つ)。
echo
echo "[1] ビルド (--features package)"
BUILD_ARGS=()
for t in "${TOOLS[@]}"; do BUILD_ARGS+=(--bin "$t"); done
( cd src-tauri && "$CARGO_BIN" build --release --features package "${BUILD_ARGS[@]}" )
ok "cargo build 完了"

# --- 配置 --------------------------------------------------------------------
echo
echo "[2] $BIN_DIR/ へ配置"
mkdir -p "$BIN_DIR"
EXE_SUFFIX=""
case "$(uname -s 2>/dev/null || echo unknown)" in
  MINGW*|MSYS*|CYGWIN*) EXE_SUFFIX=".exe" ;;
esac
for t in "${TOOLS[@]}"; do
  SRC="src-tauri/target/release/${t}${EXE_SUFFIX}"
  if [ ! -f "$SRC" ]; then
    bad "$SRC が生成されていない (ビルドは成功したのに成果物が無い)"
    exit 1
  fi
  cp "$SRC" "$BIN_DIR/${t}${EXE_SUFFIX}"
  chmod +x "$BIN_DIR/${t}${EXE_SUFFIX}"
  ok "$BIN_DIR/${t}${EXE_SUFFIX}"
done

# --- ★ 動作確認 (置いただけで満足しない) --------------------------------------
# 「コピーはできたが実行できない」(署名・実行ビット・アーキ違い) を here で捕まえる。
#
# ⚠️ ★ **exit code では判定できない。** gse-unpack / gse-package は clap 非依存の素朴な
#    パーサで、`--help` は usage を stderr に出して **ExitCode::from(1)** を返す
#    (src-tauri/src/bin/unpack.rs の main)。引数不足も同じく 1 なので、
#    「exit 0 なら OK」にすると **正常なバイナリを不合格にする**。
#    → **usage が実際に出力されたか**を見る。実行できない場合 (アーキ違い等) は
#      シェル/OS 側のエラーになり usage は出ないので、これで区別できる。
echo
echo "[3] 動作確認"
for t in "${TOOLS[@]}"; do
  OUT=$("$BIN_DIR/${t}${EXE_SUFFIX}" --help 2>&1 || true)
  case "$OUT" in
    *"usage:"*)
      ok "$t が起動し usage を出した"
      ;;
    *)
      bad "$t を配置したが起動できない (usage が出ない)。アーキテクチャ/実行権限を確認する"
      printf '        出力: %s\n' "${OUT:-（出力なし）}"
      exit 1
      ;;
  esac
done

echo
echo "=============================================================="
echo " [GREEN] install 完了"
echo "   復号の例 (docs/pilot-runbook.md §受領):"
echo "     ./$BIN_DIR/gse-unpack --input P0xx_gse_*.age \\"
echo "         --identity ~/.gse/age-identity.txt --out ./inbox"
echo "   ⚠️ 秘密鍵 (~/.gse/age-identity.txt) は共有・コミット厳禁。"
echo "   ⚠️ $BIN_DIR/ は .gitignore 済み。バイナリをコミットしないこと。"
echo "=============================================================="
