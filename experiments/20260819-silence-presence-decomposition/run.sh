#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20260819-silence-presence-decomposition
# `reproducibility-discipline` ルール 4。
#
# 使い方:
#   export GSE_PHASE1_NDJSON=<Phase1 生 NDJSON を置いたディレクトリ>   # ★ repo 外
#   bash run.sh
#
# ⚠️★★ Windows コンソールは cp932。PYTHONIOENCODING / PYTHONUTF8 を必ず立てる。
# ⚠️★★★ 入力パスはリポジトリに書かない（OS ユーザー名を含むため・S5C-D8 / security-checker M1）。
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

PY="${PYTHON:-python}"

# ★ 上流実験と同じ入力であることの検査（`data.md` に凍結した値）。
EXPECTED_MANIFEST="120e1a5e16447449c52c1313a2fa058b99949cc055d42354a3760b26ae50fa3b"

if [ -z "${GSE_PHASE1_NDJSON:-}" ] || [ ! -d "${GSE_PHASE1_NDJSON}" ]; then
  echo "!! GSE_PHASE1_NDJSON が未設定 / 不在。本実験は生 NDJSON が要る（repo 外）。" >&2
  exit 1
fi

# ⚠️ git は空ディレクトリを保持しない。★ `results/` が消えた clone でも動くようにする
#   （codex cross-review 高）。
mkdir -p results

echo "== 自己検査（★ 本解析より先に回す。落ちたら結果を書かない）=="
"$PY" scripts/selftest.py

echo
echo "== 抽出（沈黙ギャップ ＋ 5 分窓の時間内訳）=="
"$PY" scripts/extract.py \
  --flat-dir "${GSE_PHASE1_NDJSON}" \
  --config config.json \
  --out results/extract.json

echo
echo "== 入力の来歴を検査（上流と同じデータを見ているか）=="
"$PY" - "$EXPECTED_MANIFEST" <<'PYEOF'
import json, sys
expected = sys.argv[1]
got = json.load(open("results/extract.json", encoding="utf-8"))["input_manifest"]["manifest_sha256"]
if got != expected:
    print(f"!! manifest 不一致: expected={expected} got={got}", file=sys.stderr)
    print("   ★ 上流実験 (expression-power / cv-gate-null) と別のデータを見ている。", file=sys.stderr)
    raise SystemExit(3)
print(f"ok manifest={got}")
PYEOF

echo
echo "== L1 / L2 記述（★ model-free）=="
"$PY" scripts/describe.py --extract results/extract.json --out results/describe.json

echo
echo "== L3 離散時間ハザードの ablation（2 基線・上下界・120 秒副解析）=="
"$PY" scripts/analyze.py \
  --extract results/extract.json \
  --config config.json \
  --out results/analyze.json

echo
echo "== S5 決定性（★ 事前登録 §8）: 抽出を 2 回走らせて byte-equal を確認 =="
"$PY" scripts/extract.py   --flat-dir "${GSE_PHASE1_NDJSON}"   --config config.json   --out results/.extract_rerun.json >/dev/null
if cmp -s results/extract.json results/.extract_rerun.json; then
  rm -f results/.extract_rerun.json
  echo "ok 決定的（byte-equal）"
else
  echo "!! 決定性が壊れている: results/extract.json と再実行結果が一致しない" >&2
  exit 4
fi

echo
echo "== 漏洩検査（★ 実験ディレクトリだけでなく .steering/ と docs/adr/ も走査）=="
"$PY" scripts/leakcheck.py   --root .   --root ../../.steering/20260819-low-typing-window-discrimination   --root ../../docs/adr

echo
echo "== 完了。results/ を見ること。=="
