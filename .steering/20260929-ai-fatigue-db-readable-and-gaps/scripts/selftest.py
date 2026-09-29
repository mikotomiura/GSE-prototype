"""build_readable.py の検算が空回りしていないことを確かめる試験（2026-09-29 のレビューへの対応）。

1. 変異試験: 5 種の変異（cell / order / structure / readback / refs）のそれぞれで、
   - 終了コードが 0 でない
   - 期待した検査の言葉で止まる（別の理由で落ちていない）
   - 出力も一時ファイルも残らない
2. 記入欄の引き継ぎ: 記入したファイルを --carry-from に渡すと、状態・メモ・送付の記録が新しい出力に残る
3. 複製先の保護: --copy-to の先に同名のファイルがあれば止まり、中身が変わらない。--force-copy なら置き換わる

★ archive/ の成果物と issues.md は触らない（すべて一時ディレクトリの --out に出す）。
使い方: python selftest.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build_readable.py")
BASENAME = "AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx"
EXPECT = {  # 変異 → 止まるときの言葉（build_readable.py の sys.exit の文言）
    "cell": "既存シートのセル値が変わった",
    "order": "シートの並びが想定と違う",
    "structure": "既存シートの構成",
    "readback": "追加シートに書いた値が読み戻せない",
    "refs": "存在しない issue 番号への参照",
}


def run(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, BUILD, *args], capture_output=True, text=True, encoding="utf-8", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    fails = []
    tmp = tempfile.mkdtemp(prefix="readable-selftest-")
    try:
        # 1. 変異試験
        for kind, word in EXPECT.items():
            out = os.path.join(tmp, f"mut-{kind}.xlsx")
            rc, log = run("--mutate-test", kind, "--out", out)
            left = [n for n in os.listdir(tmp) if n.startswith(".tmp-")]
            ok = rc != 0 and word in log and not os.path.exists(out) and not left
            print(f"[mutate {kind}] rc={rc} word={'yes' if word in log else 'NO'} out={'exists' if os.path.exists(out) else 'none'} tmp-left={len(left)} -> {'OK' if ok else 'FAIL'}")
            if not ok:
                fails.append((kind, log[-400:]))

        # 2. 記入欄の引き継ぎ
        base = os.path.join(tmp, "base.xlsx")
        rc, log = run("--out", base)
        if rc != 0:
            fails.append(("base build", log[-400:]))
        else:
            wb = openpyxl.load_workbook(base)
            ws = wb["調査不足とissue"]
            head = {ws.cell(4, c).value: c for c in range(1, ws.max_column + 1)}
            row = next(r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == "S-01")
            ws.cell(row, head["状態（記入欄）"], "完了")
            ws.cell(row, head["メモ（記入欄）"], "引き継ぎ試験のメモ")
            wq = wb["照会の下書き"]
            hq = {wq.cell(4, c).value: c for c in range(1, wq.max_column + 1)}
            rq = next(r for r in range(5, wq.max_row + 1) if wq.cell(r, hq["対象論文（鍵）"]).value == "AF004")
            wq.cell(rq, hq["送付の記録（記入欄）"], "2026-09-30 送付（試験）")
            edited = os.path.join(tmp, "edited.xlsx")
            wb.save(edited)
            second = os.path.join(tmp, "second.xlsx")
            rc, log = run("--out", second, "--carry-from", edited)
            if rc != 0:
                fails.append(("carry build", log[-400:]))
            else:
                w2 = openpyxl.load_workbook(second)
                s2 = w2["調査不足とissue"]
                h2 = {s2.cell(4, c).value: c for c in range(1, s2.max_column + 1)}
                r2 = next(r for r in range(5, s2.max_row + 1) if s2.cell(r, 1).value == "S-01")
                q2 = w2["照会の下書き"]
                hq2 = {q2.cell(4, c).value: c for c in range(1, q2.max_column + 1)}
                rq2 = next(r for r in range(5, q2.max_row + 1) if q2.cell(r, hq2["対象論文（鍵）"]).value == "AF004")
                got = (s2.cell(r2, h2["状態（記入欄）"]).value, s2.cell(r2, h2["メモ（記入欄）"]).value, q2.cell(rq2, hq2["送付の記録（記入欄）"]).value)
                ok = got == ("完了", "引き継ぎ試験のメモ", "2026-09-30 送付（試験）")
                others = [s2.cell(r, h2["状態（記入欄）"]).value for r in range(5, s2.max_row + 1) if s2.cell(r, 1).value not in (None, "S-01")]
                ok = ok and all(v == "未着手" for v in others)
                print(f"[carry] got={got} others-untouched={all(v == '未着手' for v in others)} -> {'OK' if ok else 'FAIL'}")
                if not ok:
                    fails.append(("carry", str(got)))

            # 2b. 引き継ぎの守り（Codex 2 巡目）: 止まって、出力を作らないこと
            def must_stop(label, word, *args):
                o = os.path.join(tmp, f"{label}.xlsx")
                rc, log = run("--out", o, *args)
                ok = rc != 0 and word in log and not os.path.exists(o)
                print(f"[{label}] rc={rc} word={'yes' if word in log else 'NO'} out={'exists' if os.path.exists(o) else 'none'} -> {'OK' if ok else 'FAIL'}")
                if not ok:
                    fails.append((label, log[-400:]))

            must_stop("carry-missing", "引き継ぎ元が見つからない", "--carry-from", os.path.join(tmp, "typo-no-such-file.xlsx"))
            # 旧版（鍵の列が無い）に送付の記録がある → 黙って捨てずに止まる
            wo = openpyxl.load_workbook(edited)
            q = wo["照会の下書き"]
            hk = {q.cell(4, c).value: c for c in range(1, q.max_column + 1)}
            q.cell(4, hk["対象論文（鍵）"], "旧版の列")
            old = os.path.join(tmp, "old-layout.xlsx")
            wo.save(old)
            must_stop("carry-oldlayout", "記入を引き継げない", "--carry-from", old)
            # 今の版に無い issue に記入がある → 引き継ぐと消えるので止まる
            wr = openpyxl.load_workbook(edited)
            s = wr["調査不足とissue"]
            hs = {s.cell(4, c).value: c for c in range(1, s.max_column + 1)}
            s.cell(s.max_row + 1, 1, "S-99")
            s.cell(s.max_row, hs["状態（記入欄）"], "完了")
            orphan = os.path.join(tmp, "orphan.xlsx")
            wr.save(orphan)
            must_stop("carry-orphan", "今の版に無い issue・照会に記入がある", "--carry-from", orphan)

        # 3. 複製先の保護
        cdir = os.path.join(tmp, "copydir")
        os.makedirs(cdir)
        target = os.path.join(cdir, BASENAME)
        with open(target, "wb") as fp:
            fp.write(b"researcher-edited-placeholder")
        before = sha(target)
        rc, log = run("--out", os.path.join(tmp, "third.xlsx"), "--copy-to", cdir)
        ok = rc != 0 and "複製先に同名のファイルがある" in log and sha(target) == before and not os.path.exists(os.path.join(tmp, "third.xlsx"))
        print(f"[copy-protect] rc={rc} target-unchanged={sha(target) == before} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(("copy-protect", log[-400:]))
        rc, log = run("--out", os.path.join(tmp, "fourth.xlsx"), "--copy-to", cdir, "--force-copy")
        ok = rc == 0 and sha(target) != before and sha(target) == sha(os.path.join(tmp, "fourth.xlsx"))
        print(f"[copy-force] rc={rc} replaced={sha(target) != before} -> {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(("copy-force", log[-400:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("FAILED:", fails)
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()
