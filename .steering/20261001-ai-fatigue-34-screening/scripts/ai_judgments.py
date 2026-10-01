"""2 回目の問いに見せる AI の判定（GPT 版・Claude 版）を件ごとに 1 つの JSON に集める（design.md §3）。

★ 1 回目の問いには使わない。出力は repo の外（scratchpad）に置く（判定者 1 が 1 回目の前に見ないため）。
使い方: python ai_judgments.py <出力 JSON（repo の外）>
"""
import json
import os
import sys

import openpyxl

# repo（この worktree）の根。ここより下には書かない
C_TASK_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

GPT = r"C:\Users\johnd\Downloads\AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx"
CLAUDE = r"C:\Users\johnd\Downloads\AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx"


def main(out):
    # ★ 絶対パスに直して小文字で比べる（相対パス・c:\wt\ の書き方でも repo の中に書かない・2026-10-02 のレビュー）
    p = os.path.abspath(out).replace("\\", "/").lower()
    if "gse-prototype" in p or p.startswith("c:/wt/") or p.startswith(os.path.abspath(C_TASK_ROOT).replace("\\", "/").lower()):
        sys.exit("出力は repo の外に置く")
    g = openpyxl.load_workbook(GPT, read_only=True, data_only=True)
    c = openpyxl.load_workbook(CLAUDE, read_only=True, data_only=True)
    res = {}
    for r in g["AI適格性評価"].iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).startswith("AF"):
            res[r[0]] = {"gpt": {"用途": r[3], "概念の範囲": r[4], "評価状態": r[6]}}
    for r in c["Claude適格性評価"].iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).startswith("AF"):
            res[r[0]]["claude"] = {"用途": r[3], "概念の範囲": r[4], "中心範囲の段": r[10], "判定根拠": r[11]}
    for r in c["Claudeスクリーニング案"].iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).startswith("AF"):
            res[r[0]]["claude"].update({"全文段": r[4], "案（最終）": r[5], "除外理由": r[6]})
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("ok", len(res))


if __name__ == "__main__":
    main(sys.argv[1])
