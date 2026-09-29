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


def recalc(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([soffice(), "--headless", "--norestore", "--calc", "--convert-to", "xlsx", "--outdir", outdir, path],
                   check=True, capture_output=True)
    return openpyxl.load_workbook(os.path.join(outdir, os.path.basename(path)), data_only=True)


def start_values(calc, labels):
    s = calc["★まず読む"]
    got = {}
    for r in range(1, s.max_row + 1):
        label = s.cell(r, 1).value
        if label in labels:
            v = s.cell(r, 3).value
            got[label] = int(v) if isinstance(v, float) and v.is_integer() else v
    return got


def formula_presence(form, labels):
    """★ 数式が定数に置き換わっていないか（Codex 2 巡目: 残っている数式だけを見ると、定数に壊しても通る）。"""
    miss = []
    s = form["★まず読む"]
    rows = {s.cell(r, 1).value: r for r in range(1, s.max_row + 1)}
    miss += [f"★まず読む:{k}" for k in labels if k not in rows or s.cell(rows[k], 3).data_type != "f"]
    m = form["証拠の地図"]
    start = next(r for r in range(1, m.max_row + 1) if str(m.cell(r, 1).value or "").startswith("② 件数"))
    r = start + 2  # 見出しの次の行から『計』の行まで
    while True:
        for c in range(2, m.max_column + 1):
            if m.cell(start + 1, c).value and m.cell(r, c).data_type != "f":
                miss.append(f"証拠の地図:{m.cell(r, c).coordinate}")
        if m.cell(r, 1).value == "計":
            break
        r += 1
    return miss


def main():
    src = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DST
    exp = expected(src)
    tmp = tempfile.mkdtemp(prefix="readable-recalc-")
    try:
        cp = os.path.join(tmp, "in.xlsx")
        shutil.copy2(src, cp)
        calc = recalc(cp, os.path.join(tmp, "out"))
        form = openpyxl.load_workbook(cp)
        nonformula = formula_presence(form, exp)
        # ★ 連動の確認: コピーの『論文ごとの要点』で AF006 のデザインを変え、再計算の値が動くことを見る
        sens = os.path.join(tmp, "sens.xlsx")
        wb2 = openpyxl.load_workbook(cp)
        ws2 = wb2["論文ごとの要点"]
        r6 = next(r for r in range(5, 39) if ws2.cell(r, 1).value == "AF006")
        assert ws2.cell(r6, 13).value == "質的研究", ws2.cell(r6, 13).value
        ws2.cell(r6, 13, "実験・介入")
        wb2.save(sens)
        moved = start_values(recalc(sens, os.path.join(tmp, "out2")), exp)
        k_exp, k_cq = "中心候補のうち実験・介入", "中心候補のうち横断調査・質的研究"
        sens_ok = moved.get(k_exp) == exp[k_exp] + 1 and moved.get(k_cq) == exp[k_cq] - 1
        print(f"formula presence: missing={nonformula[:5]}  sensitivity: 実験・介入 {exp[k_exp]}→{moved.get(k_exp)}, 横断・質的 {exp[k_cq]}→{moved.get(k_cq)} {'OK' if sens_ok else 'NG'}")
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
        got = start_values(calc, exp)
        miss = [k for k in exp if k not in got]
        wrong = [(k, got[k], exp[k]) for k in exp if k in got and got[k] != exp[k]]
        print(f"formulas in new sheets: {n}  errors/empty: {bad[:5]}")
        for k in exp:
            print(f"  {k}: {got.get(k)} (expected {exp[k]}) {'OK' if got.get(k) == exp[k] else 'NG'}")
        if bad or miss or wrong or nonformula or not sens_ok:
            print("FAILED", {"bad": bad[:5], "missing": miss, "wrong": wrong, "not-formula": nonformula[:5], "sensitivity": sens_ok})
            sys.exit(1)
        print("ALL OK")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
