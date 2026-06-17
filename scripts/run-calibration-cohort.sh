#!/usr/bin/env bash
# run-calibration-cohort.sh — v0.3 較正パイプライン helper (git-bash 前提)
#
# raw/P*/ の被験者別 NDJSON を gse-replay --calibration で解析し
# metrics/Pxxx/<os>/Pxxx.calib.json を生成 → gse-cohort で被験者横断判定 (Go/Kill/
# INCONCLUSIVE/DataInsufficient) を出力する。NDJSON は読むだけ (移動・コミットしない)。
#
# 使い方:
#   GSE_DATASET=C:/gse-dataset ./scripts/run-calibration-cohort.sh
#   ./scripts/run-calibration-cohort.sh --root /c/gse-dataset
#   ./scripts/run-calibration-cohort.sh --dry-run         # コマンドを表示のみ
#   ./scripts/run-calibration-cohort.sh --no-cohort       # calib.json 生成まで
#   ./scripts/run-calibration-cohort.sh --os windows      # <os> サブディレクトリ名を明示
#
# 前提: gse-dataset レイアウト  <root>/raw/P000/gse_*.ndjson (logger は P000 固定。多人数は
#       収集後に P001/P002/... へ手動整理する。docs/calibration-smoke-runbook.md 参照)
# プライバシー: NDJSON 生ログは共有しない。共有は metrics/ と cohort/ の集計 JSON のみ (§10)。
set -euo pipefail

ROOT="${GSE_DATASET:-C:/gse-dataset}"
RUN_COHORT=1
DRY_RUN=0
OS_OVERRIDE=""

usage() {
  cat >&2 <<'USAGE'
run-calibration-cohort.sh — v0.3 較正パイプライン (replay --calibration → cohort)

USAGE:
  run-calibration-cohort.sh [--root <dataset>] [--os <macos|windows|linux>]
                            [--no-cohort] [--dry-run] [-h|--help]

OPTIONS:
  --root <path>   gse-dataset ルート (既定: $GSE_DATASET → なければ C:/gse-dataset)
  --os <name>     metrics/Pxxx/<os>/ の <os> 名を明示 (既定: uname から自動判定)
  --no-cohort     被験者別 calib.json 生成までで停止 (gse-cohort を実行しない)
  --dry-run       生成せず実行予定コマンドを表示
  -h, --help      このヘルプ
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:?--root requires a path}"; shift 2 ;;
    --os) OS_OVERRIDE="${2:?--os requires a name}"; shift 2 ;;
    --no-cohort) RUN_COHORT=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

detect_os() {
  if [ -n "$OS_OVERRIDE" ]; then echo "$OS_OVERRIDE"; return; fi
  case "$(uname -s)" in
    Darwin) echo "macos" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    Linux) echo "linux" ;;
    *) echo "unknown" ;;
  esac
}
OSDIR="$(detect_os)"
if [ "$OSDIR" = "unknown" ]; then
  echo "WARN: could not detect OS from uname; using metrics/Pxxx/unknown/. Pass --os <macos|windows> to override." >&2
fi
# gse-replay --calibration が受け付ける 1 被験者あたりのセッション数上限 (replay 側 MAX_CALIBRATION_FILES と一致)。
MAX_CALIBRATION_FILES=64

# REPO_ROOT はスクリプト位置基準で決める (gse-dataset 側から実行されても GSE repo を指す・review LOW)。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RAW="$ROOT/raw"
if [ ! -d "$RAW" ]; then
  echo "raw directory not found: $RAW (set GSE_DATASET or --root)" >&2
  exit 3
fi

REPLAY="$REPO_ROOT/src-tauri/target/release/gse-replay"
COHORT="$REPO_ROOT/src-tauri/target/release/gse-cohort"
if [ "$OSDIR" = "windows" ]; then
  REPLAY="$REPLAY.exe"
  COHORT="$COHORT.exe"
fi

# バイナリを 1 回ビルド (dry-run 時は省略)。
if [ "$DRY_RUN" -eq 0 ]; then
  ( cd "$REPO_ROOT/src-tauri" && cargo build --release --bin gse-replay --bin gse-cohort )
fi

shopt -s nullglob
found=0
failed=0
for subj_dir in "$RAW"/P*/; do
  [ -d "$subj_dir" ] || continue
  subj="$(basename "$subj_dir")"
  # 純 glob で展開。gse_YYYYMMDD_HHMMSS.ndjson は辞書順=時刻順で calibration の時刻順前提と一致。
  ndjson=( "$subj_dir"*.ndjson )
  if [ "${#ndjson[@]}" -eq 0 ]; then
    echo "[$subj] no .ndjson, skip" >&2
    continue
  fi
  if [ "${#ndjson[@]}" -gt "$MAX_CALIBRATION_FILES" ]; then
    echo "[$subj] ${#ndjson[@]} files exceed gse-replay limit ($MAX_CALIBRATION_FILES), skip" >&2
    failed=1
    continue
  fi
  found=1
  out_dir="$ROOT/metrics/$subj/$OSDIR"
  out_file="$out_dir/$subj.calib.json"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $REPLAY ${ndjson[*]} --calibration --json > $out_file"
    continue
  fi
  mkdir -p "$out_dir"
  echo "[$subj] ${#ndjson[@]} session(s) -> $out_file" >&2
  # atomic write: 一時ファイルに書き成功時のみ確定 (失敗で空/壊れた calib.json を残さない・review H1)。
  # 1 被験者の失敗で batch 全体を止めない (set -e を一時退避し warn+continue)。
  tmp="$out_file.tmp.$$"
  if ( set +e; "$REPLAY" "${ndjson[@]}" --calibration --json > "$tmp" ); then
    mv -f "$tmp" "$out_file"
  else
    rm -f "$tmp"
    echo "[$subj] gse-replay --calibration failed, skip (calib.json unchanged)" >&2
    failed=1
  fi
done

if [ "$found" -eq 0 ]; then
  echo "no subject NDJSON found under $RAW (expected raw/P*/gse_*.ndjson)" >&2
  exit 3
fi

if [ "$RUN_COHORT" -eq 1 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $COHORT $ROOT"
  else
    cohort_dir="$ROOT/cohort"
    mkdir -p "$cohort_dir"
    stamp="$(date +%Y%m%d_%H%M%S)"
    out="$cohort_dir/cohort_$stamp.json"
    # gse-cohort は全 verdict (go/kill/inconclusive/data_insufficient) で exit 0 を返す
    # (判定は JSON の overall フィールドで表現)。非ゼロは I/O/parse エラー時のみ。
    "$COHORT" "$ROOT" | tee "$out"
    echo "cohort report -> $out" >&2
  fi
fi

if [ "$failed" -ne 0 ]; then
  echo "WARN: 一部の被験者で calib.json 生成に失敗/スキップしました (上記ログ参照)。cohort は成功分のみで判定しています。" >&2
fi
