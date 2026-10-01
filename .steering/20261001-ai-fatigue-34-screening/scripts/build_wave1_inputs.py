"""波 1 の入力（束 X1〜X5）を作る（design.md §5）。

★ 渡すのは書誌・リンク・無料の版の URL・『AI適格性評価』の「次の確認・作業」と『確認事項』の逐語だけ。
  用途の判定（GPT 版・Claude 版）とユーザーの判定は渡さない。用途の語が混ざった行は止まる。
使い方: python build_wave1_inputs.py <出力ディレクトリ（repo の外）>
"""
import glob
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
DB = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                  "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
OA_GLOB = os.path.join(STEER, "20260930-ai-fatigue-judge-file", "evidence", "oa_2026-09-30*.json")

BUNDLES = {
    "X1": ["AF001", "AF002", "AF003", "AF004", "AF034", "AF005"],
    "X2": ["AF006", "AF007", "AF008", "AF009", "AF010", "AF011", "AF012"],
    "X3": ["AF019", "AF020", "AF021", "AF022", "AF023", "AF024"],
    "X4": ["AF013", "AF014", "AF015", "AF016", "AF017", "AF018"],
    "X5": ["AF025", "AF026", "AF027", "AF028", "AF029", "AF030", "AF031", "AF032", "AF033"],
}
# 用途の判定の語（渡す文に混ざっていたら止まる）
BANNED = ["中心候補", "背景保持", "方法論保持", "訂正連結", "中心-A", "中心-B", "含める", "除外"]


def rows(ws, key_col=1, first=5):
    out = {}
    hdr = [c.value for c in ws[4]]
    for r in ws.iter_rows(min_row=first, values_only=True):
        if r[0] and str(r[0]).startswith("AF"):
            out[str(r[0])] = dict(zip(hdr, r))
    return out


def main(outdir):
    if os.path.abspath(outdir).lower().startswith(os.path.abspath(os.path.dirname(STEER)).lower()):
        sys.exit("出力先は repo の外にする")
    os.makedirs(outdir, exist_ok=True)
    wb = openpyxl.load_workbook(DB, read_only=True, data_only=True)
    lit = rows(wb["文献DB"])
    bib = rows(wb["書誌・出典"])
    elig = rows(wb["AI適格性評価"])
    issues = [r for r in wb["確認事項"].iter_rows(min_row=5, values_only=True) if r[0]]
    oa = {}
    for p in sorted(glob.glob(OA_GLOB)):
        oa.update(json.load(open(p, encoding="utf-8"))["records"])
    for b, ids in BUNDLES.items():
        lines = [f"# 束 {b} の入力（{len(ids)} 件）", ""]
        for i in ids:
            L, B, E = lit[i], bib.get(i, {}), elig[i]
            doi = next((str(v) for k, v in L.items() if k and "DOI" in str(k) and v), "")
            nxt = str(E.get("次の確認・作業") or "")
            for w in BANNED:
                if w in nxt.replace("適用除外", ""):  # 倫理の「適用除外理由」は用途の語ではない
                    sys.exit(f"{i}: 次の確認・作業に用途の語「{w}」がある（渡す前に止まる）")
            o = oa.get(doi.lower(), oa.get(doi, {}))
            for r in issues:  # ★ 『確認事項』の行にも同じ検査をかける（2026-10-02 のレビュー・今の行には用途の語は 0 件）
                if any(w in " ".join(str(v or "") for v in r[1:4]).replace("適用除外", "") for w in BANNED):
                    sys.exit(f"『確認事項』{r[0]} に用途の語がある（渡す前に止まる）")
            lines += [f"## {i}", f"- 題名: {L.get('論文タイトル') or L.get('タイトル')}",
                      f"- DOI: {doi or 'なし'}",
                      f"- 一次情報 URL（DB）: {E.get('主な参照URL') or ''}",
                      f"- 無料の版（OpenAlex・2026-09-30）: {o.get('oa_status', '記録なし')} {o.get('oa_url', '')}",
                      f"- 『AI適格性評価』の「次の確認・作業」（逐語）: {nxt}"]
            for r in issues:
                if i in str(r[0]) or (i in ("AF006", "AF007", "AF008", "AF009") and "AF006–AF009" in str(r[0])) \
                        or (i in ("AF004", "AF034") and "AF034" in str(r[0])):
                    lines.append(f"- 『確認事項』（逐語）: 対象 {r[0]}｜{r[1]}｜現在: {r[2]}｜次: {r[3]}")
            lines.append("")
        open(os.path.join(outdir, f"input-{b}.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("ok", outdir)


if __name__ == "__main__":
    main(sys.argv[1])
