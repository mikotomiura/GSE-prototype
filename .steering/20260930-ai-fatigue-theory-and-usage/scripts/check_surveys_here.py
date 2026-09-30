"""本タスクのサーヴェイ（S-09・S-11）の成果物に、前タスクの検査器（check_survey_files.py）を当てる（design.md §0.1）。

前タスクの検査器の `run()` を本タスクのディレクトリに当てるだけで、規則は前タスクの SSOT のまま（語の一覧を複製しない）。
使い方: python check_surveys_here.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
PREV_SCRIPTS = os.path.join(os.path.dirname(TASK), "20260929-ai-fatigue-surveys", "scripts")
sys.path.insert(0, PREV_SCRIPTS)
import check_survey_files as C  # noqa: E402


def main():
    errs, n_fact, n_judg = C.run(TASK)
    for e in errs:
        print("NG", e)
    print(f"事実のファイル {n_fact} 本・判定案のファイル {n_judg} 本・違反 {len(errs)} 件")
    return 1 if errs or n_fact == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
