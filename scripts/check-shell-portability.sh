#!/usr/bin/env bash
# ★ シェルスクリプトの移植性ゲート。
#
# ⚠️★★★ **何を止めるためにあるのか**（2026-08-29 に macOS 実機で実害が出た）:
#   ★ macOS 標準の bash は **3.2**（2007 年）で、⚠️ **多バイト文字を変数名の一部として読む**。
#     → 変数 `why` を括らずに書き、その**直後に全角括弧**を置くと、bash は
#       「why ＋ 括弧のバイト」を 1 つの変数名として読む。⚠️ そんな変数は無いので `set -u` で落ちる。
#   ⚠️ 実害: `scripts/sync-session.sh` の **O1 ガードが `exit 4` に到達できず `exit 1` を返していた**
#     （★ O1 セッションを gse-dataset へ出さないための番人。`docs/o1-deletion-ledger.md` §4）。
#     ★ 同期自体は非 0 で止まる（fail-closed）が、⚠️ **exit code の契約が壊れ、検査 6 件が全部赤**だった。
#
# ★ 規約: **`$name` の直後に多バイト文字が来るなら `${name}` と括る。**
#   ★ `${` を見た bash は閉じ `}` まで変数名として読むので、⚠️ **後続バイトの解釈に依存しない**
#     （bash 3.2 / 5.x / git-bash / zsh で同じ結果になる）。
#
# ⚠️★ **1 箇所直して終わりにしない**ためのゲートである:
#   ★ `experiments/…/prepare-subjects.sh` には**この罠を踏んだ実測コメントが既にあった**のに、
#     リポジトリ全体では **17 箇所**生きていた（★ 対策が 1 つの真実源の中でしか効いていなかった）。
#
# Usage: bash scripts/check-shell-portability.sh
# Exit:  0 = 緑 / 1 = 違反あり or 検査できなかった（★ fail-closed）
#
# 関連: .steering/20260829-macos-shell-portability/

set -euo pipefail

cd "$(dirname "$0")/.."

PASS=0
FAIL=0
ok () { echo "  ✅ $1"; PASS=$((PASS + 1)); }
ng () { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }

echo "=== シェル移植性ゲート（bash 3.2 の変数名パース）==="

# ⚠️★ **grep に頼らない。** ★ 実装差が大きすぎる（2026-08-29 実測: この Mac の `grep` は
#   ugrep 7.8.4 で、`LC_ALL=C grep -E '…[^[:print:][:space:]]'` が **1 件も拾わなかった**）。
#   → ★ バイト列を自分で読む。⚠️ python3 が無いなら**検査できないので赤にする**（fail-closed）。
if ! command -v python3 > /dev/null 2>&1; then
  ng "python3 が無いので走査できない（★ 検査できないことを緑にしない）"
  echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
  exit 1
fi

SCAN_PY="$(
  cat << 'PY'
import re, subprocess, sys

# ★ 走査対象: 追跡されているシェルスクリプト。
#   ⚠️ **拡張子だけに頼らない**（★ shebang しか手がかりの無いファイルを取りこぼす）。
#   ⚠️★★ **未追跡のファイルも見る**（2026-08-29 実測: `git ls-files` だけだと
#     ★ **新しく足したスクリプトがコミットされるまで素通りする**。書いた直後こそ捕まえたい）。
def targets():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True).stdout.split("\n")
    for f in out:
        if not f:
            continue
        if f.endswith((".sh", ".bash", ".command")):
            yield f
            continue
        try:
            with open(f, "rb") as fh:
                first = fh.read(80).split(b"\n")[0]
            if first.startswith(b"#!") and (b"bash" in first or b"/bin/sh" in first):
                yield f
        except OSError:
            pass

# ★ `$name` の直後が非 ASCII バイト。⚠️ `${name}` は `$` の次が `{` なので当たらない（＝ 直した形）。
PAT = re.compile(rb"\$[A-Za-z_][A-Za-z0-9_]*[\x80-\xff]")

def scan(paths):
    hits = []
    for f in paths:
        try:
            with open(f, "rb") as fh:
                data = fh.read()
        except OSError:
            continue
        for i, line in enumerate(data.split(b"\n"), 1):
            for m in PAT.finditer(line):
                hits.append((f, i, m.group().decode("utf-8", "replace"),
                             line.decode("utf-8", "replace").strip()[:100]))
    return hits

mode = sys.argv[1]
if mode == "repo":
    hits = scan(targets())
    for f, i, frag, line in hits:
        print(f"{f}:{i}: {frag}  ||  {line}")
    sys.exit(1 if hits else 0)
else:  # 対照: 引数のファイルだけを見る
    hits = scan(sys.argv[2:])
    print(len(hits))
PY
)"

# --- 1. ★ リポジトリ全体に違反が無いか ------------------------------------------
if VIOL="$(python3 -c "${SCAN_PY}" repo)"; then
  ok "\$name の直後に多バイト文字を置いている箇所が無い"
else
  ng "★ \$name を括らずに多バイト文字を続けている箇所がある（★ \${name} と括ること）:"
  echo "${VIOL}" | sed 's/^/       /'
fi

# --- 2. ⚠️★★ 陽性対照: **わざと違反したファイルを必ず捕まえる** ------------------
#     ★ これが無いと「0 件」が「走査が空振りした」のと区別できない
#       （memory: silent-failure-in-guard-scripts / measurement-instrument-false-positives）。
CTL_BAD="$(mktemp)"
CTL_OK="$(mktemp)"
# ⚠️★ **全角括弧を別の引数として渡して組み立てる。**
#   ★ ここに違反そのものを直接書くと、⚠️ **この検査が自分の対照フィクスチャを違反と数える**
#     （2026-08-29 に実際にそうなった）。→ ★ 生成されるファイルの中身は同じまま、
#     **ソース上に「変数 ＋ 多バイト」が並ばない**ようにする。
printf 'set -u\nv=OK\necho "A: $v%s"\n' '）' > "${CTL_BAD}"
printf 'set -u\nv=OK\necho "A: ${v}%s"\n' '）' > "${CTL_OK}"

n_bad="$(python3 -c "${SCAN_PY}" ctl "${CTL_BAD}")"
n_ok="$(python3 -c "${SCAN_PY}" ctl "${CTL_OK}")"

if [ "${n_bad}" -ge 1 ]; then
  ok "★ 陽性対照: わざと括らずに書いた行を捕まえた（${n_bad} 件）"
else
  ng "★ 走査が空回りしている（違反を仕込んだのに 0 件）"
fi

# --- 3. ⚠️★ 陰性対照: **直した形は捕まえない**（★ 直し方が有効である証拠）----------
if [ "${n_ok}" -eq 0 ]; then
  ok "★ 陰性対照: \${name} と括った行は捕まえない"
else
  ng "★ 括った形まで違反と言っている（${n_ok} 件）＝ 直しようが無くなる"
fi

# --- 4. ⚠️★★★ **この規約が必要な理由そのもの**を実演する --------------------------
#     ★ 「bash 3.2 だと本当に落ちるのか」を**その場の bash で測る**。
#     ⚠️ bash 5 系では落ちない。★ そのときは「この bash では再現しない」と**明示**する
#       （⚠️ 落ちないことを「規約が不要」と読ませない。macOS の既定は 3.2 のままである）。
if "${BASH:-/bin/bash}" "${CTL_BAD}" > /dev/null 2>&1; then
  ok "⚠️ この bash（$("${BASH:-/bin/bash}" --version | head -1 | sed 's/.*version //;s/ .*//')）では再現しない。★ 規約は macOS 既定 bash 3.2 のために要る"
else
  ok "★ この bash（$("${BASH:-/bin/bash}" --version | head -1 | sed 's/.*version //;s/ .*//')）では実際に落ちた ＝ 規約は実害の予防である"
fi
if ! "${BASH:-/bin/bash}" "${CTL_OK}" > /dev/null 2>&1; then
  ng "★ 括った形まで落ちる ＝ 直し方が間違っている"
else
  ok "★ 括った形はどの bash でも落ちない"
fi

rm -f "${CTL_BAD}" "${CTL_OK}"

echo "────────────────────────────────────────"
echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
if [ "${FAIL}" -eq 0 ]; then
  echo "  ✅ シェル移植性は健全"
  exit 0
fi
echo "  ❌ 上の ❌ を直すこと"
exit 1
