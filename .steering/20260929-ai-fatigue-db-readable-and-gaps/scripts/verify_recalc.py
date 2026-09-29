"""LibreOffice でコピーを再計算し、追加シートの数式の値を、データ（papers_plain / issues_data）から独立に数えた期待値と照合する。

openpyxl は数式の計算済みの値を書かないため、build_readable.py の中では値を確かめられない（2026-09-29 のレビュー: 期待値を表示するだけだった）。
使い方: python verify_recalc.py [xlsx]   # 既定は archive/ の成果物。元のファイルは変更しない（一時ディレクトリのコピーを変換する）
"""
import os
import shutil
import subprocess
import sys
import tempfile

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import papers_plain as PP  # noqa: E402
import issues_data as ID  # noqa: E402

DST = os.path.join(os.path.dirname(HERE), "archive", "AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx")
NEW = ["★まず読む", "論文ごとの要点", "証拠の地図", "調査不足とissue", "件数の目安と種文献", "照会の下書き", "用語の読み替え"]


def soffice():
    for c in (shutil.which("soffice"), r"C:\Program Files\LibreOffice\program\soffice.exe", "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if c and os.path.exists(c):
            return c
    sys.exit("LibreOffice（soffice）が見つからない")


def expected(path):
    central = [p for p in PP.PAPERS if p["group"] in ("A", "B", "?")]
    status = openpyxl.load_workbook(path)["調査不足とissue"]
    done = sum(1 for r in range(5, status.max_row + 1) if status.cell(r, 13).value == "完了")
    nt = {t: sum(1 for i in ID.ISSUES if i["type"] == t) for t in ID.TYPES}
    npri = [sum(1 for i in ID.ISSUES if i["priority"] == p) for p in ID.PRIORITIES]
    return {
        "登録文献": len(PP.PAPERS),
        "中心-A（AI に向けた疲労）": sum(p["group"] == "A" for p in PP.PAPERS),
        "中心（A/B 未確定）": sum(p["group"] == "?" for p in PP.PAPERS),
        "中心-B（一般的な疲労 × AI）": sum(p["group"] == "B" for p in PP.PAPERS),
        "中心-A のうち大学生": sum(p["group"] == "A" and p["pop"] == "大学生・学習者" for p in PP.PAPERS),
        "中心候補のうち横断調査・質的研究": sum(p["design"] in ("横断調査", "質的研究") for p in central),
        "中心候補のうちデザイン未確認の調査": sum(p["design"] == "調査（デザイン未確認）" for p in central),
        "中心候補のうち時間差・縦断（確認済み）": sum(p["design"] == "時間差・縦断" for p in central),
        "中心候補のうち実験・介入": sum(p["design"] == "実験・介入" for p in central),
        "中心候補のうちフィリピン／中国": f"{sum(p['country'].startswith('フィリピン') for p in central)} / {sum(p['country'].startswith('中国') for p in central)}",
        "中心候補（地図の計）": len(central),
        "issue の数（サーヴェイ / アイディア / 通常）": f"{nt['サーヴェイ']} / {nt['アイディア']} / {nt['通常']}",
        "issue の優先度（高 / 中 / 低）": " / ".join(map(str, npri)),
        "issue の完了 / 全体": f"{done} / {len(ID.ISSUES)}",
    }


def main():
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DST
    exp = expected(src)
    tmp = tempfile.mkdtemp(prefix="readable-recalc-")
    try:
        cp = os.path.join(tmp, "in.xlsx")
        shutil.copy2(src, cp)
        outdir = os.path.join(tmp, "out")
        os.makedirs(outdir)
        subprocess.run([soffice(), "--headless", "--norestore", "--calc", "--convert-to", "xlsx", "--outdir", outdir, cp],
                       check=True, capture_output=True)
        calc = openpyxl.load_workbook(os.path.join(outdir, "in.xlsx"), data_only=True)
        form = openpyxl.load_workbook(cp)
        bad = []
        n = 0
        for name in NEW:
            for row in form[name].iter_rows():
                for c in row:
                    if c.data_type == "f":
                        n += 1
                        v = calc[name][c.coordinate].value
                        if v is None or (isinstance(v, str) and v.startswith("#")):
                            bad.append((name, c.coordinate, v))
        s = calc["★まず読む"]
        got = {}
        for r in range(1, s.max_row + 1):
            label = s.cell(r, 1).value
            if label in exp:
                v = s.cell(r, 3).value
                got[label] = int(v) if isinstance(v, float) and v.is_integer() else v
        miss = [k for k in exp if k not in got]
        wrong = [(k, got[k], exp[k]) for k in exp if k in got and got[k] != exp[k]]
        print(f"formulas in new sheets: {n}  errors/empty: {bad[:5]}")
        for k in exp:
            print(f"  {k}: {got.get(k)} (expected {exp[k]}) {'OK' if got.get(k) == exp[k] else 'NG'}")
        if bad or miss or wrong:
            print("FAILED", {"bad": bad[:5], "missing": miss, "wrong": wrong})
            sys.exit(1)
        print("ALL OK")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
