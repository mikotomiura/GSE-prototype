#!/usr/bin/env bash
# experiments/20260906-p321-resumption-baseline/run.sh
#
# ★ [P321] Alaboudi & LaToza (2021) の公開データから「受領なし再開」ベースライン
#   (R0 / R1 / R0') を実測する。規約の SSOT: docs/experiment-tracking.md。
#
# ⚠️★★★ **Step 0 (capabilities_gate.py) は本実験では *適用外* である。**
#   ★ 「消した」のではない。★ ADR-013 のゲートは「**GSE が収集した信号**を使う解析は、
#     最初に `capabilities` を機械判定する」規約であり、
#     ⚠️ 本実験は **GSE の NDJSON を 1 行も読まない** (読むのは [P321] の公開データだけ)。
#   → ★ 代わりに **Step 0' = 入力の SHA-256 照合** を置く。★ 「入力が本当に想定のものか」を
#     人の手順ではなくコードで検査する、という *同じ役割* を果たさせる。
#   → ★ 読み替えの一覧は `notes.md` §5。

set -euo pipefail

EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="$EXP_DIR/raw"
PKG="$RAW_DIR/replication_package_FSE2021.zip"
ROWDATA="$RAW_DIR/replication_package_FSE2021/rowData.json"

# ★ data.md に固定した来歴 (figshare article 14068802 / file 26553647)
PKG_SHA256="6f506cba88ef30a7027b367967a6d92628c84e90d80b4a1a343190e1083d04b2"
ROWDATA_SHA256="497df0b4da398c39cc0fd8b28544d4ac1d61c728708f4f9cdaa32469acda78b9"

# ⚠️★ `python` は macOS に無いことがあり、`python3` は Windows の一部環境に無い。
PY="${PYTHON:-$(command -v python3 || command -v python)}"
: "${PY:?python が見つかりません (python3 / python のどちらも無い)}"

# ⚠️★★ **macOS には `sha256sum` が無い** (`shasum -a 256` である)。
#   ★ 不在のまま `|| { ...一致しない... }` に落ちると、⚠️★★★ **「SHA-256 が一致しない」という
#     *嘘の理由* で止まる**。→ ★ ここで 1 度だけ解決し、無ければそう言って止まる
#   (code-reviewer M-1)。
if command -v sha256sum > /dev/null 2>&1; then
  sha256_of() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum > /dev/null 2>&1; then
  sha256_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  echo "⚠️ sha256sum も shasum も見つかりません。入力の照合ができないので止まります。" >&2
  exit 1
fi

mkdir -p "$EXP_DIR/results" "$RAW_DIR"

# ---------------------------------------------------------------------------
# Step 0': 入力の取得と SHA-256 照合 (★ capabilities gate の読み替え)
# ---------------------------------------------------------------------------
#
# ⚠️★★★ **自動ダウンロードはできない。** ★ 2026-09-06 に実測:
#   figshare は `curl` に対し bot チャレンジを返す
#   (`https://figshare.com/s/<token>` → HTTP 202 / 0 バイト、
#    `/ndownloader/files/26553647?private_link=<token>` → HTTP 403)。
#   ★ 実ブラウザのセッションでは通る。→ 取得手順は `data.md` §2 に逐語で書いた。
# ⚠️ かつ論文が案内する **もう一方の配布元 `observe-dev.online` は消滅している**
#   (NXDOMAIN。★ ローカル resolver と Cloudflare DoH の両方で確認)。→ `data.md` §3。

if [ ! -f "$PKG" ]; then
  cat >&2 <<'MSG'
⚠️ 入力が無い: raw/replication_package_FSE2021.zip

★ 取得手順 (data.md §2 と同じ):
  1. ブラウザで https://figshare.com/s/6c4026a941db49ea3de3 を開く
     (⚠️ figshare の bot チャレンジがあるため curl / wget では取れない)
  2. replication_package_FSE2021.zip (178.03 kB) をダウンロードする
  3. experiments/20260906-p321-resumption-baseline/raw/ に置く
  4. この run.sh をもう一度実行する (SHA-256 が照合される)
MSG
  exit 1
fi

echo "Step 0': 入力の SHA-256 を照合する"
GOT="$(sha256_of "$PKG")"
[ "$GOT" = "$PKG_SHA256" ] || {
  echo "⚠️★★★ zip の SHA-256 が data.md と一致しない。止まる。" >&2
  echo "   期待: $PKG_SHA256" >&2
  echo "   実測: $GOT" >&2
  exit 1
}

if [ ! -f "$ROWDATA" ]; then
  PYTHONUTF8=1 "$PY" -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" \
    "$PKG" "$RAW_DIR"
fi
[ -f "$ROWDATA" ] || {
  echo "⚠️ zip は正しいのに rowData.json が展開されていない: $ROWDATA" >&2; exit 1; }
GOT="$(sha256_of "$ROWDATA")"
[ "$GOT" = "$ROWDATA_SHA256" ] || {
  echo "⚠️★★★ rowData.json の SHA-256 が data.md と一致しない。止まる。" >&2
  echo "   期待: $ROWDATA_SHA256" >&2
  echo "   実測: $GOT" >&2
  exit 1
}
echo "Step 0' OK"

# ---------------------------------------------------------------------------
# Step 1: 再現性アンカーを刻む
# ---------------------------------------------------------------------------
# ⚠️★★★ HMM_VERSION は **適用外** (★ HMM を 1 度も通さないため)。
#   → ★ 代わりに **[P321] の版 (arXiv v1) と抽出スクリプトの hash** を刻む。
{
  echo "p321_version=arXiv:2105.02162v1"
  echo "figshare_article=14068802"
  echo "figshare_file=26553647"
  echo "package_sha256=${PKG_SHA256}"
  echo "rowdata_sha256=${ROWDATA_SHA256}"
  echo "analyze_sha256=$(sha256_of "$EXP_DIR/analyze_p321.py")"
  echo "hmm_version=N/A (本実験は HMM を通さない)"
  echo "seed=N/A (乱数要素なし)"
} > "$EXP_DIR/results/provenance.txt"
cat "$EXP_DIR/results/provenance.txt"

# ---------------------------------------------------------------------------
# Step 2: 検算ゲート自体の検査 (正常 / 不在 / 壊れている)
# ---------------------------------------------------------------------------
# ⚠️★★★ `verify-before-claiming` ルール 5b。★ 「正常なら緑」だけ試して満足しない。
echo
echo "Step 2: selftest (検算ゲートが空回りしていないか)"
PYTHONUTF8=1 "$PY" "$EXP_DIR/analyze_p321.py" --input "$ROWDATA" --selftest

# ---------------------------------------------------------------------------
# Step 3: 本体 (検算 A -> R0 / R1 / R0')
# ---------------------------------------------------------------------------
# ⚠️★★★ **`| tail` にパイプしないこと** —— `$?` が tail のものになり赤を見落とす
#   (.steering/20260819-g1-reboot-and-instrument-fix/blockers.md B-3)。
echo
echo "Step 3: 本体"
# ⚠️★★★ `set -e` の下では、失敗したコマンドの **次の行 (`RC=$?`) は実行されない**。
#   ★ 素直に書くと「赤のときだけ report.txt が表示されない」という
#     silent failure になる (★ 本セッションの code review 前に自分で踏んだ)。
#   → ★ `|| RC=$?` で受けてから、明示的に判定する。
RC=0
PYTHONUTF8=1 "$PY" "$EXP_DIR/analyze_p321.py" \
  --input "$ROWDATA" --out "$EXP_DIR/results" > "$EXP_DIR/results/report.txt" 2>&1 || RC=$?
cat "$EXP_DIR/results/report.txt"
if [ "$RC" -ne 0 ]; then
  echo "⚠️★★★ 検算 A が赤。R0 / R1 を信用しない (notes.md §2)。" >&2
  exit "$RC"
fi

echo
echo "完了: results/metrics.json / results/report.txt / results/provenance.txt"
