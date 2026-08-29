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
#   ⚠️★ **`bash -n` では捕まらない**（実測: 違反ファイルに対し rc=0）。
#     ★ 構文は正しく、**実行時に unbound variable になる**ので構文検査の管轄外である。
#
# ★ 規約: **`$name` の直後に多バイト文字が来るなら `${name}` と括る。**
#   ★ `${` を見た bash は閉じ `}` まで変数名として読むので、⚠️ **後続バイトの解釈に依存しない**
#     （bash 3.2 / 5.x / git-bash / zsh で同じ結果になる）。
#
# ⚠️★ **1 箇所直して終わりにしない**ためのゲートである:
#   ★ `experiments/…/prepare-subjects.sh` には**この罠を踏んだ実測コメントが既にあった**のに、
#     リポジトリ全体では **17 箇所**生きていた（★ 対策が 1 つの真実源の中でしか効いていなかった）。
#
# ⚠️★★★ **いま見ているのは「1 型」だけである**（★ Codex /cross-review 指摘・2026-08-29）:
#   ★ 検査するのは **`$name` の直後に多バイト文字が来る**ケースだけ。
#   ⚠️ 名前は "shell-portability" だが、以下は **見ていない**（★ 見ていないことを隠さない）:
#     - `$name_suffix` のように**後続が英数字/アンダースコア**で変数名が伸びる誤展開
#     - 配列・位置パラメータ・`${!var}` 等の bash 版差
#     - `echo -e` / `local` / `declare` などの組み込みの実装差
#     - BSD と GNU のコマンド差（★ `od` / `sed -i` / `tr` / `grep`。⚠️ 実際に 4 件踏んでいる）
#     - `.ps1`（★ PowerShell に同じ罠があるかは**この Mac では検証不能**）
#   ★ 型を足すときは、**必ず陽性対照と陰性対照を一緒に足す**こと。
#
# Usage: bash scripts/check-shell-portability.sh
# Exit:  0 = 緑 / 1 = 違反あり / 2 = ⚠️★ **検査できなかった**（★ 違反 0 件と区別する）
#
# 関連: .steering/20260829-macos-shell-portability/

set -euo pipefail

cd "$(dirname "$0")/.."

PASS=0
FAIL=0
BROKEN=0        # ★ 「検査できなかった」件数。⚠️ 違反件数とは別に数える
ok ()     { echo "  ✅ $1"; PASS=$((PASS + 1)); }
ng ()     { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }
broken () { echo "  ❌ ⚠️ 検査できなかった: $1"; FAIL=$((FAIL + 1)); BROKEN=$((BROKEN + 1)); }

# ⚠️★★ **途中で死んでも理由が残るようにする**（code-reviewer MEDIUM・2026-08-29）:
#   ★ `set -euo pipefail` 下で mktemp や python が落ちると、
#     ⚠️ **要約も ❌ も出ないまま終わり、CI ログ上は「理由の無い赤」**になる
#     （memory `silent-failure-in-guard-scripts` と同型）。
CTL_BAD=""; CTL_OK=""; CTL_SHEBANG=""; FINISHED=0
cleanup () {
  local rc=$?
  rm -f "${CTL_BAD:-}" "${CTL_OK:-}" "${CTL_SHEBANG:-}"
  if [ "${FINISHED}" -eq 0 ]; then
    echo "  ❌ ⚠️★ ゲート自身が途中で終了した（rc=${rc}）。★ 緑として扱わないこと。"
  fi
}
trap cleanup EXIT

echo "=== シェル移植性ゲート（bash 3.2 の変数名パース）==="

# ⚠️★ **grep に頼らない。** ★ 実装差が大きすぎる（2026-08-29 実測: この Mac の `grep` は
#   ugrep 7.8.4 で、`LC_ALL=C grep -E '…[^[:print:][:space:]]'` が **1 件も拾わなかった**）。
#   → ★ バイト列を自分で読む。⚠️ python3 が無いなら**検査できないので赤にする**（fail-closed）。
if ! command -v python3 > /dev/null 2>&1; then
  broken "python3 が無いので走査できない（★ 検査できないことを緑にしない）"
  echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
  FINISHED=1
  exit 2
fi

SCAN_PY="$(
  cat << 'PY'
import re, subprocess, sys

# ★ 走査対象の集め方。
#   ⚠️ **拡張子だけに頼らない**（★ shebang しか手がかりの無いファイルを取りこぼす）。
#   ⚠️★★ **未追跡のファイルも見る**（2026-08-29 実測: `git ls-files` だけだと
#     ★ **新しく足したスクリプトがコミットされるまで素通りする**。書いた直後こそ捕まえたい）。
EXTS = (".sh", ".bash", ".command")

# ★ shebang のインタプリタ名で判定する（code-reviewer MEDIUM・2026-08-29）。
#   ⚠️ 旧実装は `b"bash" in first or b"/bin/sh" in first` で、
#     ★ `#!/usr/bin/env sh` / `#!/bin/dash` / `#!/bin/zsh` を**取りこぼしていた**。
#   ⚠️★ macOS の `/bin/sh` は **bash 3.2 の実体**なので、`env sh` も同じ罠を踏む。
SHELLS = {"sh", "bash", "dash", "ksh", "mksh", "zsh", "ash"}


def is_shell_by_shebang(first_line):
    if not first_line.startswith(b"#!"):
        return False
    parts = first_line[2:].strip().split()
    if not parts:
        return False
    interp = parts[0]
    # ★ `#!/usr/bin/env bash` は 2 トークン目が本体
    if interp.rsplit(b"/", 1)[-1] == b"env" and len(parts) > 1:
        interp = parts[1]
    name = interp.rsplit(b"/", 1)[-1].decode("ascii", "replace")
    return name in SHELLS


#   ⚠️★★★ **`git` の rc を必ず見る**（code-reviewer HIGH ＋ security-checker HIGH・
#     2026-08-29 に**両者が独立に実測で再現**、私も再現した）:
#     ★ 非 git ディレクトリで走らせると `git ls-files` は **rc=128 / stdout 空**を返す。
#     ⚠️ rc を見ないと **走査 0 件 → 違反 0 件 → 緑 (exit 0)** になり、
#       ★ 冒頭が掲げている fail-closed が**成立しなくなる**（実測: 5/5 緑で通った）。
#     ⚠️ 陽性/陰性対照はこれを捕まえられない（★ 対照は明示パスを渡すので repo 走査が
#       空回りしても必ず通る）。→ ★ **走査経路そのものに対照を立てる**（下記 `targets` モード）。
def targets():
    tracked, untracked = [], []
    for flag, bucket in ((["--cached"], tracked), (["--others", "--exclude-standard"], untracked)):
        r = subprocess.run(["git", "ls-files"] + flag, capture_output=True, text=True)
        if r.returncode != 0:
            print("git ls-files %s が失敗 (rc=%d)。★ git リポジトリの中で実行すること。"
                  % (" ".join(flag), r.returncode), file=sys.stderr)
            sys.exit(2)          # ★ 2 = 走査できなかった（⚠️ 違反 0 件と区別する）
        for f in r.stdout.split("\n"):
            if not f:
                continue
            if f.endswith(EXTS):
                bucket.append(f)
                continue
            # ⚠️★ 拡張子以外は shebang を見るため先頭 256 バイトだけ開く。
            #   ★ 走査も出力もしないので漏洩経路ではないが、開く対象は最小限にしている。
            try:
                with open(f, "rb") as fh:
                    first = fh.read(256).split(b"\n")[0]
            except OSError:
                continue
            if is_shell_by_shebang(first):
                bucket.append(f)
    return tracked, untracked


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
                # ⚠️★ **行全文は出さない**（security-checker LOW・2026-08-29）:
                #   ★ 未追跡スクリプトの当該行に秘密があると CI ログへ出てしまう。
                hits.append((f, i, m.group().decode("utf-8", "replace")))
    return hits


mode = sys.argv[1]

if mode == "repo":
    tracked, untracked = targets()
    allf = tracked + untracked
    # ⚠️★★ **0 本走査を「違反なし」と言わせない。**
    if not allf:
        print("走査対象のシェルスクリプトが 1 本も見つからない（★ 収集が壊れている）",
              file=sys.stderr)
        sys.exit(2)
    print("SCANNED %d %d" % (len(tracked), len(untracked)))
    hits = scan(allf)
    for f, i, frag in hits:
        mark = "追跡" if f in tracked else "未追跡"
        print("VIOL %s:%d: %s  [%s]" % (f, i, frag, mark))
    sys.exit(1 if hits else 0)

elif mode == "targets":
    # ★ 収集経路の対照: 集まったファイル一覧をそのまま出す。
    tracked, untracked = targets()
    for f in tracked + untracked:
        print(f)
    sys.exit(0)

elif mode == "shebang":
    # ★ shebang 判定だけを単体で試す（★ この分岐は repo 走査では 1 度も通っていなかった）。
    for p in sys.argv[2:]:
        with open(p, "rb") as fh:
            first = fh.read(256).split(b"\n")[0]
        print("%s %s" % ("YES" if is_shell_by_shebang(first) else "NO", p))
    sys.exit(0)

else:  # ctl: 対照。引数のファイルだけを見る
    print(len(scan(sys.argv[2:])))
    sys.exit(0)
PY
)"

# --- 1. ★ リポジトリ全体に違反が無いか ------------------------------------------
#   ⚠️★★ **「違反あり」と「走査器が落ちた」を同じ赤にしない**（code-reviewer HIGH）:
#     ★ 旧版は両方 exit 1 で、⚠️ python が traceback で死ぬと
#       「違反がある」と言いながら**明細を 1 行も出さない**（★ 運用者が存在しない違反を探す）。
scan_rc=0
SCAN_OUT="$(python3 -c "${SCAN_PY}" repo 2> /tmp/.shellport.err)" || scan_rc=$?
SCAN_ERR="$(cat /tmp/.shellport.err 2> /dev/null || true)"
rm -f /tmp/.shellport.err

case "${scan_rc}" in
  0)
    ok "\$name の直後に多バイト文字を置いている箇所が無い（$(printf '%s' "${SCAN_OUT}" | awk '/^SCANNED/{print "追跡 "$2" 本 / 未追跡 "$3" 本"}')・★ この 1 型のみ）"
    ;;
  1)
    ng "★ \$name を括らずに多バイト文字を続けている箇所がある（★ \${name} と括ること）:"
    printf '%s\n' "${SCAN_OUT}" | grep '^VIOL ' | sed 's/^VIOL /       /'
    ;;
  *)
    broken "走査そのものが成立しなかった（rc=${scan_rc}）"
    [ -n "${SCAN_ERR}" ] && printf '%s\n' "${SCAN_ERR}" | sed 's/^/       /'
    ;;
esac

# --- 2. ⚠️★★★ 収集経路の陽性対照 -------------------------------------------------
#   ★ 上の「0 件」が **走査が空振りしたのではない**ことを、
#     ⚠️ **既知のファイルが実際に集まっているか**で確かめる（★ 明示パスの対照では代替できない）。
tgt_rc=0
TGT="$(python3 -c "${SCAN_PY}" targets 2> /dev/null)" || tgt_rc=$?
if [ "${tgt_rc}" -ne 0 ]; then
  broken "収集経路が動かない（rc=${tgt_rc}）"
elif printf '%s\n' "${TGT}" | grep -qx 'scripts/sync-session.sh'; then
  ok "★ 収集経路の対照: 既知のスクリプトが実際に集まっている（$(printf '%s\n' "${TGT}" | wc -l | tr -d ' ') 本）"
else
  broken "★ 収集経路が空振りしている（scripts/sync-session.sh すら集まらない）"
fi

# --- 3. ⚠️★★ 陽性対照: **わざと違反したファイルを必ず捕まえる** ------------------
CTL_BAD="$(mktemp)"
CTL_OK="$(mktemp)"
CTL_SHEBANG="$(mktemp)"
# ⚠️★ **全角括弧を別の引数として渡して組み立てる。**
#   ★ ここに違反そのものを直接書くと、⚠️ **この検査が自分の対照フィクスチャを違反と数える**
#     （2026-08-29 に実際にそうなった）。→ ★ 生成されるファイルの中身は同じまま、
#     **ソース上に「変数 ＋ 多バイト」が並ばない**ようにする。
printf 'set -u\nv=OK\necho "A: $v%s"\n' '）' > "${CTL_BAD}"
printf 'set -u\nv=OK\necho "A: ${v}%s"\n' '）' > "${CTL_OK}"
# ★ 拡張子が無く shebang だけのファイル（★ 下の 5 で使う）
printf '#!/usr/bin/env sh\nset -u\nv=OK\necho "A: $v%s"\n' '）' > "${CTL_SHEBANG}"

n_bad="$(python3 -c "${SCAN_PY}" ctl "${CTL_BAD}")"
n_ok="$(python3 -c "${SCAN_PY}" ctl "${CTL_OK}")"

if [ "${n_bad}" -ge 1 ]; then
  ok "★ 陽性対照: わざと括らずに書いた行を捕まえた（${n_bad} 件）"
else
  ng "★ 走査が空回りしている（違反を仕込んだのに 0 件）"
fi

# --- 4. ⚠️★ 陰性対照: **直した形は捕まえない**（★ 直し方が有効である証拠）----------
if [ "${n_ok}" -eq 0 ]; then
  ok "★ 陰性対照: \${name} と括った行は捕まえない"
else
  ng "★ 括った形まで違反と言っている（${n_ok} 件）＝ 直しようが無くなる"
fi

# --- 5. ⚠️★★ shebang 判定の対照（★ この分岐は repo 走査では 1 度も通っていなかった）---
#     ★ 実測（2026-08-29）: 収集された 56 本は**全部が拡張子由来**で、
#       ⚠️ shebang 分岐は **0 回**しか通っていなかった＝**正しさが未検証のまま**置かれていた。
sb="$(python3 -c "${SCAN_PY}" shebang "${CTL_SHEBANG}" | awk '{print $1}')"
if [ "${sb}" = "YES" ]; then
  ok "★ shebang だけのファイル（#!/usr/bin/env sh）を拾える"
else
  ng "★ shebang 判定が拾えていない（⚠️ macOS の /bin/sh は bash 3.2 の実体＝同じ罠を踏む）"
fi

# --- 6. ⚠️★★★ **この規約が必要な理由そのもの**を実演する --------------------------
#     ⚠️★ **`${BASH}` で差し替えようとしない**（code-reviewer MEDIUM・実測）:
#       ★ bash は起動時に `BASH` を**自分自身のパスで上書きする**ので、
#         環境変数からは差し替えられない（⚠️ 旧版の `${BASH:-/bin/bash}` は
#         `:-` 側に**到達しない**）。→ ★ **測りたい bash を明示的に並べて走らせる。**
#     ⚠️★ 旧版は両分岐とも `ok` を呼んでおり、**構造上ぜったいに赤にならなかった**
#       （★ 「通過 5 件」の 1 件は何も測っていなかった）。
bash_report () {
  local path="$1" label="$2" ver
  [ -x "${path}" ] || { echo "  ⚠️ ${label} が無いので測れない: ${path}"; return 0; }
  ver="$("${path}" --version 2> /dev/null | head -1 | sed 's/.*version //;s/ .*//')"
  if "${path}" "${CTL_BAD}" > /dev/null 2>&1; then
    # ★ 落ちなかった。⚠️ bash 3.x なら**規約の前提が崩れている**ので赤にする。
    case "${ver}" in
      3.*) ng "★ ${label}（${ver}）で再現しない ＝ 規約の前提が変わった（★ この検査を見直すこと）" ;;
      *)   ok "⚠️ ${label}（${ver}）では再現しない。★ 規約は macOS 既定の bash 3.2 のために要る" ;;
    esac
  else
    ok "★ ${label}（${ver}）では実際に落ちた ＝ 規約は実害の予防である"
  fi
  if "${path}" "${CTL_OK}" > /dev/null 2>&1; then
    ok "★ ${label}: 括った形は落ちない（★ 直し方が有効）"
  else
    ng "★ ${label}: 括った形まで落ちる ＝ 直し方が間違っている"
  fi
}

bash_report /bin/bash "システム既定の bash"
# ★ PATH 上の bash が別物なら、そちらでも測る（⚠️ 同じなら二度測らない）。
PATH_BASH="$(command -v bash || true)"
if [ -n "${PATH_BASH}" ] && [ "${PATH_BASH}" != "/bin/bash" ]; then
  bash_report "${PATH_BASH}" "PATH 上の bash"
fi

echo "────────────────────────────────────────"
echo "  通過 ${PASS} 件 / 未達 ${FAIL} 件"
FINISHED=1
if [ "${FAIL}" -eq 0 ]; then
  echo "  ✅ シェル移植性は健全"
  exit 0
fi
if [ "${BROKEN}" -gt 0 ]; then
  echo "  ❌ ⚠️★ **検査できなかった項目がある**（★ 違反 0 件と混同しないこと）"
  exit 2
fi
echo "  ❌ 上の ❌ を直すこと"
exit 1
