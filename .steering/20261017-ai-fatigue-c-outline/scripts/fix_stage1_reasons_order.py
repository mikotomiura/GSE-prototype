# Align author 1's proposals with the registered order of exclusion codes (GSRR-36, attachment 6) and add the
# order and the meanings of E3 and stage-1 E2 to the criteria sheet. Prints the new memos; saves only with --save.
import sys, openpyxl
src, dst = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src)
ws = wb["除外理由"]
h = [c.value for c in ws[1]]
P, M = h.index("提案する理由") + 1, h.index("提案の根拠") + 1
E3_END = "人が AI の系を使う・監督する・評価する研究ではないため E3（疲労を測っていない E2 にも当たるが、理由が 2 つ当たるときは E3 が先）。"
FIVE = {
 "CS10710": ("E4", "英語抄録は作家の作品によるインド知識体系の継承を論じる文学の論考で、人から集めたデータの分析は無い。一次研究でないため E4（AI の利用と関係がない E3 にも当たるが、E4 が先）。exhausted は思想体系の比喩。"),
 "CS00694": ("E4", "英語抄録はメンタルヘルスへの AI とチャットボットの応用の概説で、人から集めたデータの分析は無い。一次研究でないため E4（E2 にも当たるが、E4 が先）。digital exhaust は端末・SNS から得る行動データで、人の消耗ではない。"),
 "CS08212": ("E4", "英語抄録は LLM へのプロンプト構造の枠組みと防御の設計の提案で、観察はモデルの挙動であり、人から集めたデータの分析は無い。一次研究でないため E4（人が AI を使う研究でない E3 にも当たるが、E4 が先）。attention saturation はモデル側の概念。"),
 "CS05171": ("E4", "英語抄録が、貢献は概念と方法に限り、8 名の実演は手順の例示と設計の材料にすぎないと明言する。方法論の論文として E4（fatigue は固定順序の交絡要因として挙がるだけ）。"),
 "CS06192": ("E2", "英語抄録は放射線科医単独と AI 併用の診断成績を独自に比較した一次研究で、E4 も E3 も当たらない。burnout の軽減は期待として述べるだけで、疲労を測った結果は示されないため E2。注: 題名・抄録の段の E2 は、疲労を測っていないと明言するときだけなので（登録の Q4）、厳密にはこの記録は E2 に当たらない。2 人とも除外にしたため、最終は除外の理由の中から選ぶ。"),
}
changed = []
for r in range(2, ws.max_row + 1):
    rid, pair, prop, memo = ws.cell(r, 1).value, ws.cell(r, 5).value, ws.cell(r, P).value, ws.cell(r, M).value
    if rid in FIVE:
        new = FIVE[rid]
    elif pair == "E2 / E3" and prop == "E2":
        parts = [s for s in memo.split("。") if s]
        keep = parts[:2] if parts[0].startswith("題名のみ") else parts[:1]
        keep[-1] = keep[-1].split("ためE2")[0]   # the old conclusion, if the kept sentence carries it
        if keep[-1].endswith("、人の疲労測定は示されない") or keep[-1].endswith("示されない"):
            pass
        new = ("E3", "。".join(keep) + "。" + ("題名だけからの暫定の提案。" if parts[0].startswith("題名のみ") else "") + E3_END)
    else:
        continue
    if (prop, memo) != new:
        changed.append((rid, prop, new[0]))
        ws.cell(r, P).value, ws.cell(r, M).value = new
        print(rid, prop, "->", new[0], "|", new[1])
cr = wb["判定基準"]
add = [
 ("理由が 2 つ以上当たるとき", "先のものを 1 つ選ぶ。題名・抄録の段の順は E4、E1、E3、E2、E7。"),
 ("E3 の補足", "参加者が AI の系を使う・監督する・評価する研究でない（AI の利用を導入・操作・比較する研究でもない）とき、または疲労がその AI の利用と関係づけられていないとき。論文が手法として AI を使っているかどうかではない。"),
 ("E2 の補足（題名・抄録の段）", "題名・抄録が、疲労を測っていない・分析していないと述べるときだけ E2 にする。測定や結果の一覧に疲労が無いだけなら不明とし、E2 にしない。"),
]
have = {cr.cell(r, 1).value for r in range(1, cr.max_row + 1)}
from copy import copy
last = cr.max_row
for k, v in add:
    if k in have:
        continue
    cr.append([k, v]); r = cr.max_row
    for col in (1, 2):
        s, d = cr.cell(last, col), cr.cell(r, col)
        d.font, d.border, d.alignment, d.fill = copy(s.font), copy(s.border), copy(s.alignment), copy(s.fill)
    cr.row_dimensions[r].height = 34
print(len(changed), "changed")
if "--save" in sys.argv:
    wb.save(dst); print("saved", dst)
