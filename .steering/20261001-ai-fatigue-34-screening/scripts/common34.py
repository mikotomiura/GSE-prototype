"""本タスクの道具で共通の定数（パス・元のファイルの SHA-256・入力欄）。

★ 判定の対応表（答え → 写しの値）はここに置かない。書き込み（write_workbook.py）と検査
  （check_workbook.py）がそれぞれ独立に持つ（片方から消えても、もう片方の固定の期待で赤になる）。
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)

ORIGINAL = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                        "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
ORIGINAL_DOWNLOADS = r"C:\Users\johnd\Downloads\AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx"
ORIGINAL_SHA256 = "48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0"

COPY_NAME = "AI_fatigue_database_2026-09-18_judge1.xlsx"
COPY_ARCHIVE = os.path.join(TASK, "archive", COPY_NAME)
COPY_DOWNLOADS = os.path.join(r"C:\Users\johnd\Downloads", COPY_NAME)
COPY_SHA_RECORD = os.path.join(TASK, "archive", "copy-sha256.txt")  # 最後に書いた写しの SHA-256

LOG = os.path.join(TASK, "screening-log.jsonl")

IDS = [f"AF{i:03d}" for i in range(1, 35)]
FIRST_ROW = 5  # 『スクリーニング』『AI判定比較』の AF001 の行

# 元のシートで書いてよいセル（design.md §2.1）
INPUT_COLS = {
    "スクリーニング": ["D", "G", "H", "I", "J"],
    "AI判定比較": ["D", "F", "G"],
}
ADDED_PREFIX = "判定者1_"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
