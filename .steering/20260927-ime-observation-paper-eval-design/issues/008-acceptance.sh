#!/usr/bin/env bash
# issue 008 acceptance — 参照入力欄 Windows (a) IMM 互換
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os windows
D="${K}/refinput-windows"; M="${D}/Cargo.toml"; CORE="${D}/src/core.rs"; BINSRC="${D}/src/bin/refinput_imm.rs"

echo "[008] 参照入力欄 Windows (a) IMM"
for f in "${M}" "${D}/Cargo.lock" "${CORE}" "${BINSRC}" "${D}/README.md"; do need_file "${f}"; done

# AC1 / AC2
run_ok "AC1 cargo test が緑" cargo test --manifest-path "${M}"
run_ok "AC2 cargo build --release --bin refinput_imm が緑" cargo build --release --manifest-path "${M}" --bin refinput_imm
BIN="${D}/target/release/refinput_imm.exe"; [ -f "${BIN}" ] || BIN="${D}/target/release/refinput_imm"

# AC3
run_ok "AC3 --selftest が緑" "${BIN}" --selftest --out "${TMP}/gt.jsonl"
run_ok "AC3 selftest の出力が gt/1 の検査を通る" "${PY}" "${K}/formats/validate_logs.py" --kind gt "${TMP}/gt.jsonl"

# AC4 / AC5: ソースの構造検査（コメントを除いて見る）
cat > "${TMP}/inspect.py" <<'EOF'
import re, sys
def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(l.split("//")[0] for l in src.splitlines())
def body_of(src, head):
    i = src.find(head)
    if i < 0:
        return None
    j = src.find("{", i); depth = 0
    for k in range(j, len(src)):
        if src[k] == "{": depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[j:k + 1]
    return None
def call_args(src, name):
    out = []
    for m in re.finditer(name + r"\s*\(", src):
        k = m.end(); depth = 1; start = k; args = []; cur = start
        while k < len(src) and depth > 0:
            c = src[k]
            if c in "([{": depth += 1
            elif c in ")]}":
                depth -= 1
                if depth == 0:
                    args.append(src[cur:k]); break
            elif c == "," and depth == 1:
                args.append(src[cur:k]); cur = k + 1
            k += 1
        out.append([a.strip() for a in args])
    return out
core = strip_comments(open(sys.argv[1], encoding="utf-8").read())
binsrc = strip_comments(open(sys.argv[2], encoding="utf-8").read())
fails = []
body = body_of(core, "enum Ev")
if body is None:
    fails.append("core.rs に enum Ev が無い")
elif re.search(r"\bString\b|&\s*'?\w*\s*str\b|\bchar\b", body):
    fails.append("enum Ev が文字列型を持つ")
calls = call_args(binsrc, "ImmGetCompositionStringW")
if not calls:
    fails.append("ImmGetCompositionStringW の呼び出しが無い（長さを取っていない）")
for a in calls:
    if len(a) < 4 or not re.fullmatch(r"None|(std::|core::)?ptr::null(_mut)?\(\)|null(_mut)?\(\)", a[2]) or a[3] not in ("0", "0u32"):
        fails.append("ImmGetCompositionStringW の第 3・第 4 引数が NULL・0 でない: %r" % (a,))
if re.search(r"\bWM_IME_CHAR\b|\bWM_CHAR\b", binsrc):
    fails.append("WM_IME_CHAR / WM_CHAR を扱っている（文字を運ぶメッセージ）")
for f in fails:
    print("NG:", f)
sys.exit(1 if fails else 0)
EOF
run_ok "AC4/AC5 Ev が文字列を持たず、文字列を取得しない" "${PY}" "${TMP}/inspect.py" "${CORE}" "${BINSRC}"

# AC6
for f in "${CORE}" "${BINSRC}"; do
  forbid_grep "${f}" '\bwinapi\b|println!|eprintln!|SetWindowsHookEx' "AC6 禁止の API・出力が無い: ${f}"
done
forbid_grep "${M}" '^(serde|serde_json|winapi)' "AC6 windows 以外の依存を足していない"

# AC7
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/refinput-windows/(Cargo\.toml|Cargo\.lock|README\.md|src/core\.rs|src/bin/refinput_imm\.rs)$'
finish
