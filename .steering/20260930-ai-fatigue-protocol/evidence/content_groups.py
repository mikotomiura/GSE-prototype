"""259 件に「内容の群」（対象｜AI の種類｜デザイン）を機械で付ける（design.md §7.6・2026-09-30 固定）。

★ 並べ替えのための分類で、判定の材料ではない。範囲の判断はしない。
★ 抄録・要点は repo に写さない（repo には鍵と 3 軸の値だけ）。
使い方: uv run --with openpyxl python content_groups.py --abs <抄録の JSON> --out dedup/content_groups_2026-09-30.json
"""
import argparse
import datetime
import json
import os
import re
import sys

import dedup as D

DB_XLSX = os.path.join(D.STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                       "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")

REVIEW = r"\breview|meta-analy|scoping|systematic review|guideline|checklist|corrigendum|erratum|\bcorrection\b|protocol for|framework"
POP = [
    ("医療者", r"physician|clinician|nurse|nursing|doctor|radiolog|resident|surgeon|pharmacist|health ?care worker|healthcare professional|"
             r"health professional|medical staff|general practitioner|\bproviders?\b|看護|医師"),
    ("教員・研究者", r"teacher|faculty|educator|instructor|academic staff|researcher|lecturer|教員"),
    ("学生・学習者", r"student|learner|undergraduate|pupil|\bEFL\b|学生"),
    ("働く人（医療・教育の外）", r"employee|worker|\bstaff\b|manager|developer|programmer|professional|accountant|banker|従業員|労働"),
    ("消費者・一般の利用者", r"consumer|customer|\busers?\b|\badults?\b|\bpublic\b|citizen"),
]
AI = [
    ("記録支援・下書き", r"scribe|ambient|documentation|draft repl|draft respon|inbox|chart summar"),
    # 判断 6: 単独の predict・diagnos を外した（統計の「予測する」に当たるため）
    ("意思決定支援・警報・予測", r"decision support|\bCDSS?\b|AI-DSS|\balerts?\b|alarm|prediction model|predictive model|risk prediction|"
                              r"early warning|diagnostic AI|AI-assisted diagnos|computer-aided|triage"),
    ("生成 AI・対話", r"generative|ChatGPT|\bLLMs?\b|large language model|chatbot|conversational|\bGPT|Copilot|GenAI"),
    ("AI 一般・導入", r"artificial intelligence|\bAI\b|automation|robot|algorithm"),
]
DESIGN = [
    ("無作為化", r"randomi[sz]ed|\bRCT\b|crossover trial"),
    # 判断 6: presurvey・postsurvey・前後の実装・前後の介入の語を足した
    ("比較（非無作為化・前後）", r"pre-?post|pre- and post|before and after|before-after|pre-?intervention|post-?intervention|"
                               r"pre-?survey|post-?survey|pre-?implementation|post-?implementation|quasi-experiment|controlled trial|comparative"),
    ("縦断", r"longitudinal|time-lagged|three-wave|two-wave|\bpanel\b|cohort|diary|experience sampling"),
    ("尺度開発", r"scale development|validation|psychometric|factor analysis"),
    ("質的", r"qualitative|interview|focus group|thematic|grounded theory|content analysis"),
    ("実験・模擬", r"experiment|simulation"),
    ("横断調査", r"cross-sectional|survey|questionnaire|structural equation|\bSEM\b|\bPLS\b|regression"),
]


def first(rules, text):
    for name, pat in rules:
        if re.search(pat, text or "", flags=re.I):
            return name
    return "不明"


def classify(title, text):
    """題名（レビュー等の判定）と、題名＋抄録＋要点の文（3 軸）から群を返す。"""
    if re.search(REVIEW, title or "", flags=re.I):
        return dict(kind="レビュー等", pop="—", ai="—", design="—", group="レビュー等")
    pop, ai, des = first(POP, text), first(AI, text), first(DESIGN, text)
    return dict(kind="一次研究", pop=pop, ai=ai, design=des, group=f"{pop}｜{ai}｜{des}")


def db_fields():
    """元の DB の『研究情報』の研究デザイン・対象集団・AI・利用環境（DB 34 件）。"""
    import openpyxl
    ws = openpyxl.load_workbook(DB_XLSX, read_only=True, data_only=True)["研究情報"]
    out = {}
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[0]:
            out[r[0]] = " ".join(str(x) for x in (r[2], r[3], r[6]) if x)
    return out


def points():
    """判定者用ファイルの archive の写しの『追加候補』の要点の欄。"""
    import openpyxl
    ws = openpyxl.load_workbook(D.JUDGE_XLSX, read_only=True, data_only=True)["追加候補"]
    return {r[0]: r[8] or "" for r in ws.iter_rows(min_row=5, values_only=True) if r[0]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--abs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    recs = D.load_259()
    abstracts = D.load_abstracts(a.abs)
    dbf, pts = db_fields(), points()
    out = {}
    for r in recs:
        k = r["key"]
        text = " ".join([r["title"], abstracts.get(k) or "", dbf.get(k, ""), pts.get(k, "")])
        out[k] = classify(r["title"], text)
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds"),
                       rule="design.md §7.6", n=len(out), groups=out), f, ensure_ascii=False, indent=1)
        f.write("\n")
    from collections import Counter
    print("不明を含む", sum(1 for v in out.values() if "不明" in v["group"]))
    for g, n in Counter(v["group"] for v in out.values()).most_common(15):
        print(n, g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
