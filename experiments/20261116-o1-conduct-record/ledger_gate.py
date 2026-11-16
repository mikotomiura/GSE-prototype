"""R1 の門: 削除台帳 §6 の実施記録が 0 件か（標準入力に台帳の全文）。0 件なら終了コード 0、それ以外は 1。

表の行（行頭の空白を許す・区切りの行と、最初の行＝見出しを除く）が「（まだ 1 件も無い）」の見本の 1 行だけのときに 0 件とみなす。
見本の行を消さずに実施の行を足した場合も、見本の行を消した場合も 1 を返す。
usage: ledger_gate.py < docs/o1-deletion-ledger.md | ledger_gate.py --selftest
"""
import re
import sys

SEP = re.compile(r"^\|[\s:|-]+\|?$")
PLACEHOLDER = "（まだ 1 件も無い）"


def no_records(text):
    a = text.index("## §6")
    b = text.find("\n## ", a + 1)
    sec = text[a:b if b >= 0 else len(text)]
    lines = [ln.strip() for ln in sec.splitlines()]
    rows = [ln for ln in lines if ln.startswith("|") and not SEP.match(ln)]
    data = rows[1:]  # 表の最初の行は見出し（位置で見分ける・本文に「受付日」がある実施の行を外さない）
    return len(data) == 1 and PLACEHOLDER in data[0]


def selftest():
    base = "# x\n## §6 実施記録\n\n| 受付日 | P-ID |\n|---|---|\n| （まだ 1 件も無い） | |\n\n### 記入の仕方\n| a |\n\n## §7 次\n| z |\n"
    assert no_records(base) is False  # 「記入の仕方」の下の表も §6 に入るので 1 を返す側に倒れる → 下で本物の形を確かめる
    real = "# x\n## §6 実施記録\n\n| 受付日 | P-ID |\n|---|---|\n| （まだ 1 件も無い） | |\n\n### 記入の仕方\n- 受付日\n\n## §7 次\n| z |\n"
    assert no_records(real) is True
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "| （まだ 1 件も無い） | |\n| 2026-11-16 | P999 |\n")) is False
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "| 2026-11-16 | P999 |\n")) is False
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "")) is False
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "| （まだ 1 件も無い） | |\n   | 2026-11-16 | P999 |\n")) is False
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "| （まだ 1 件も無い） | |\n| 受付日の翌日 | P999 |\n")) is False
    assert no_records(real.replace("| （まだ 1 件も無い） | |\n", "  | （まだ 1 件も無い） | |\n")) is True
    print("ledger_gate selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        sys.exit(0 if no_records(sys.stdin.read()) else 1)
