#!/usr/bin/env bash
# experiments/20260801-signal-diagnostics/acceptance.sh
# 本実験の受け入れゲート。
#
#   GSE_DATASET=/path/to/gse-dataset ./experiments/20260801-signal-diagnostics/acceptance.sh
#
# なぜ要るか: 本実験は Rust に触らないので `cargo test` / clippy / tsc は
# **無条件に緑**になる。つまり通常の CI 系検査は本実験について何も言っていない。
# 実験の健全性 (決定性・φ 等価性・notes と results の整合・PII) を確認するのは
# このスクリプトだけであり、これが唯一の実質的なゲートになる。
#
# 検査 (7 項目):
#   1.  run.sh が exit 0
#   2.  同一 seed の 2 回実行で results/diagnostics.json / metrics.json が byte-equal
#   2b. 入力が data.md で固定した確証カットと同一 (dataset commit + 被験者別 sha256)
#   3.  φ 等価性検査が PASS、かつ**閾値が緩められていない**
#   4.  probe_variants.py が exit 0 かつ 2 回実行で byte-equal
#   5.  notes.md / metrics.json が results/diagnostics.json と整合 (check_notes.py)
#   6.  results/ 配下の**全ファイル** + metrics.json に PII が無い
#       (各スクリプト内の assert_no_pii は「書き出す直前の dict」しか見ていないので、
#        ここでは書き出された**ファイル**を raw text として走査する)
#
# 注意: 本スクリプトは run.sh を 2 回回すので、**追跡済みの results/ と metrics.json を
# 上書きする**。別入力で回して差し替わるのを 2b が止める。
#
# exit code: 0=全項目 PASS / 1=1 項目でも FAIL

set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[acceptance] FAILED: python not found" >&2
  exit 1
fi

# dataset の指し先はここで 1 回だけ解決して run.sh とも共有する。
# 各所で ${GSE_DATASET:-...} を書くと、片方だけ変えたときに検査ごとに別データを見る。
GSE_DATASET="${GSE_DATASET:-$HOME/gse-dataset}"
export GSE_DATASET
echo "[acceptance] GSE_DATASET=$GSE_DATASET"

FAILED=0
pass() { echo "[acceptance] PASS: $*"; }
fail() { echo "[acceptance] FAIL: $*" >&2; FAILED=$((FAILED + 1)); }

TMP=$(mktemp -d) || { echo "[acceptance] FAILED: mktemp" >&2; exit 1; }
trap 'rm -rf "$TMP"' EXIT

# ---------------------------------------------------------------- 1. run.sh
echo "[acceptance] 1/7 run.sh (1 回目)"
if "$HERE/run.sh" >"$TMP/run1.log" 2>&1; then
  pass "run.sh exit 0"
else
  fail "run.sh が非ゼロ終了 (末尾):"
  tail -20 "$TMP/run1.log" >&2
  # 入力が無い等でここが落ちると以降は全て無意味なので即座に止める
  echo "[acceptance] 結果: FAIL ($FAILED 件)" >&2
  exit 1
fi
cp "$HERE/results/diagnostics.json" "$TMP/diagnostics.1.json"
cp "$HERE/metrics.json" "$TMP/metrics.1.json"

# ---------------------------------------------------------------- 2. 決定性
echo "[acceptance] 2/7 run.sh (2 回目・決定性)"
if "$HERE/run.sh" >"$TMP/run2.log" 2>&1; then
  if cmp -s "$TMP/diagnostics.1.json" "$HERE/results/diagnostics.json"; then
    pass "同一 seed の 2 回実行で results/diagnostics.json が byte-equal"
  else
    fail "results/diagnostics.json が 2 回の実行で一致しない (決定性が壊れている)"
    diff <("$PYTHON" -m json.tool "$TMP/diagnostics.1.json") \
         <("$PYTHON" -m json.tool "$HERE/results/diagnostics.json") | head -20 >&2
  fi
  if cmp -s "$TMP/metrics.1.json" "$HERE/metrics.json"; then
    pass "metrics.json も byte-equal"
  else
    fail "metrics.json が 2 回の実行で一致しない"
  fi
else
  fail "run.sh (2 回目) が非ゼロ終了"
  tail -20 "$TMP/run2.log" >&2
fi

# ---------------------------------------------------------------- 2b. 入力の来歴
echo "[acceptance] 2b/7 入力の来歴 (data.md ⇔ provenance.json)"
# 本スクリプトは run.sh を回して**追跡済みの results/ と metrics.json を上書きする**。
# 別の GSE_DATASET を指したまま回すと、追跡ファイルが黙って別入力の結果に差し替わる。
# data.md が固定している dataset commit と被験者別 sha256 と突き合わせて止める。
if "$PYTHON" - "$HERE/data.md" "$HERE/results/provenance.json" <<'PY'
import json, re, sys
data_md = open(sys.argv[1], encoding="utf-8").read()
pv = json.load(open(sys.argv[2], encoding="utf-8"))
bad = []

m = re.search(r"gse-dataset commit \| `([0-9a-f]{40})`", data_md)
if not m:
    bad.append("data.md から gse-dataset commit を読めない")
elif pv["dataset_commit"] not in ("unknown", m.group(1)):
    bad.append(f"dataset commit が data.md と違う: "
               f"provenance={pv['dataset_commit'][:12]} / data.md={m.group(1)[:12]}")

skipped = []
for pid, v in sorted(pv["input_per_subject"].items()):
    if v["files"] == 0:
        # raw/ に空ディレクトリが置かれていることがある (例: P000)。
        # 0 ファイルは集計に一切寄与しないので data.md との突合対象から外す。
        # ファイルが 1 件でもある想定外の被験者は下の分岐で必ず落ちる。
        skipped.append(pid)
        continue
    row = re.search(r"\| %s \| (\d+) \|.*?`([0-9a-f]{16})`" % pid, data_md)
    if not row:
        bad.append(f"{pid}: data.md に行が無い (raw/ に想定外の被験者が混ざっている)")
        continue
    if int(row.group(1)) != v["files"]:
        bad.append(f"{pid}: files={v['files']} ≠ data.md {row.group(1)}")
    if not v["concat_sha256"].startswith(row.group(2)):
        bad.append(f"{pid}: 連結 sha256 が data.md と違う "
                   f"({v['concat_sha256'][:16]} ≠ {row.group(2)})")

used = {p for p, v in pv["input_per_subject"].items() if v["files"] > 0}
missing = set(re.findall(r"\| (P0\d\d) \| \d+ \|", data_md)) - used
if missing:
    bad.append(f"data.md にあるが入力に無い被験者: {sorted(missing)}")

if bad:
    print(" / ".join(bad), file=sys.stderr)
    sys.exit(1)
note = f" (0 ファイルのため対象外: {skipped})" if skipped else ""
print(f"dataset commit + 被験者 {len(used)} 名の連結 sha256 が data.md と一致{note}")
PY
then
  pass "入力が data.md で固定した確証カットと同一"
else
  fail "入力が data.md と違う (GSE_DATASET の指し先を確認すること)"
fi

# ---------------------------------------------------------------- 3. φ 等価性
echo "[acceptance] 3/7 φ 等価性検査"
# run.sh 側でも fail-closed だが、閾値ごと消される変更を捕まえるためここでも独立に見る。
if "$PYTHON" - "$HERE/results/diagnostics.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
c = d.get("phi_equivalence_check")
if not c or not c.get("passed"):
    print("phi_equivalence_check が無い / passed でない", file=sys.stderr); sys.exit(1)
t, o = c["thresholds"], c["observed"]
bad = []
if o["pearson_r"] < t["pearson_r_min"]:
    bad.append(f"r={o['pearson_r']} < {t['pearson_r_min']}")
if o["residual_median"] > t["residual_median_max"]:
    bad.append(f"中央値={o['residual_median']} > {t['residual_median_max']}")
if o["gt_0_01_pct"] > t["gt_0_01_pct_max"]:
    bad.append(f">0.01={o['gt_0_01_pct']}% > {t['gt_0_01_pct_max']}%")
# 閾値そのものが緩められていないかも見る (ゲートを消す変更の検知)
if t["pearson_r_min"] < 0.999 or t["residual_median_max"] > 1e-3 or t["gt_0_01_pct_max"] > 0.5:
    bad.append(f"閾値が緩められている: {t}")
if bad:
    print(" / ".join(bad), file=sys.stderr); sys.exit(1)
print(f"r={o['pearson_r']} 中央値={o['residual_median']} >0.01={o['gt_0_01_pct']}%")
PY
then
  pass "φ 等価性 (Python φ ⇔ Rust φ) と閾値が維持されている"
else
  fail "φ 等価性検査"
fi

# ---------------------------------------------------------------- 4. probe_variants
echo "[acceptance] 4/7 probe_variants.py (総当たり調査・決定性)"
if "$PYTHON" "$HERE/probe_variants.py" "$GSE_DATASET/raw" \
     "$HERE/constants.json" "$HERE/results" >"$TMP/probe1.log" 2>&1; then
  cp "$HERE/results/probe_variants.json" "$TMP/probe.1.json"
  cp "$HERE/results/probe_variants.txt" "$TMP/probe.1.txt"
  if "$PYTHON" "$HERE/probe_variants.py" "$GSE_DATASET/raw" \
       "$HERE/constants.json" "$HERE/results" >"$TMP/probe2.log" 2>&1; then
    if cmp -s "$TMP/probe.1.json" "$HERE/results/probe_variants.json" \
       && cmp -s "$TMP/probe.1.txt" "$HERE/results/probe_variants.txt"; then
      pass "probe_variants.py exit 0・2 回実行で json/txt とも byte-equal"
    else
      fail "probe_variants.json / .txt が 2 回の実行で一致しない"
    fi
  else
    fail "probe_variants.py (2 回目) が非ゼロ終了"
    tail -20 "$TMP/probe2.log" >&2
  fi
else
  fail "probe_variants.py が非ゼロ終了"
  tail -20 "$TMP/probe1.log" >&2
fi

# ---------------------------------------------------------------- 5. notes 整合
echo "[acceptance] 5/7 notes.md / metrics.json ⇔ results/diagnostics.json"
if "$PYTHON" "$HERE/check_notes.py" "$HERE/notes.md" \
     "$HERE/results/diagnostics.json" "$HERE/metrics.json" \
     "$HERE/results/probe_variants.json"; then
  pass "notes.md / metrics.json が results と整合"
else
  fail "notes.md / metrics.json が results と整合しない"
fi

# ---------------------------------------------------------------- 6. PII
echo "[acceptance] 6/7 出力の PII 走査"
# diagnostics.py / probe_variants.py の内部でも fail-closed だが、
# それは「書き出す直前の dict」に対する検査であって**ファイル**は見ていない。
# results/*.txt は render() が dict から導いているので現状は安全だが、
# render() が引数の生データやパスを触るように変わった瞬間に無検査で通る。
# ここでは results/ 配下の**全ファイル**を raw text として走査する。
if "$PYTHON" - "$HERE/results" "$HERE/metrics.json" <<'PY'
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
import diagnostics as D

res_dir, metrics = sys.argv[1], sys.argv[2]
targets = [os.path.join(res_dir, p) for p in sorted(os.listdir(res_dir))
           if os.path.isfile(os.path.join(res_dir, p))]
targets.append(metrics)

bad = []
for t in targets:
    name = os.path.basename(t)
    blob = open(t, encoding="utf-8", errors="replace").read()
    # (a) raw text に対するパターン走査 (.txt もここで初めて検査される)
    for pat, what in D._PII_PATTERNS:
        m = re.search(pat, blob)
        if m:
            bad.append(f"{name}: {what} ({m.group(0)!r})")
    # (b) JSON は絶対 epoch らしき整数の走査も通す (assert_no_pii は fail-closed)
    if name.endswith(".json"):
        D.assert_no_pii(json.loads(blob))
if bad:
    print("PII らしきものを検出: " + " / ".join(bad), file=sys.stderr)
    sys.exit(1)
print(f"走査 {len(targets)} ファイル (json {sum(1 for t in targets if t.endswith('.json'))} / "
      f"その他 {sum(1 for t in targets if not t.endswith('.json'))}): PII なし")
PY
then
  pass "results/ 配下の全ファイル (.txt 含む) と metrics.json に PII なし"
else
  fail "出力に PII らしきものがある"
fi

# ----------------------------------------------------------------
echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "[acceptance] 結果: 全項目 PASS"
  exit 0
fi
echo "[acceptance] 結果: FAIL ($FAILED 件)" >&2
exit 1
