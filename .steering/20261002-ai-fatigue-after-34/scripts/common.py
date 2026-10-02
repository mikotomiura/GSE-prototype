"""本タスクの道具で共通の定数（パス・元の資料の SHA-256）。

★ 判定の対応表（答え → 表の値）はここに置かない。書き込み（build_candidates.py）と検査
  （check_candidates.py）がそれぞれ独立に持つ（片方から消えても、もう片方の固定の期待で赤になる）。
★ 前のタスクの道具（34 件）は import するだけで変えない。
"""
import getpass
import hashlib
import os
import re
import sys
import unicodedata
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")  # ★ ユーザー名を repo に書かない（security-checker・判断 11）

# 前のタスク（34 件）の道具。stage1_banned などを import する
PREV_SCRIPTS = os.path.join(STEER, "20261001-ai-fatigue-34-screening", "scripts")
if PREV_SCRIPTS not in sys.path:
    sys.path.insert(0, PREV_SCRIPTS)

# 元の資料（★ どれも本タスクで変えない）
ORIGINAL = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                        "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
ORIGINAL_SHA256 = "48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0"
JUDGE_FILE = os.path.join(STEER, "20260930-ai-fatigue-judge-file", "archive", "judge",
                          "AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx")
JUDGE_FILE_SHA256 = "10107fcf6b6b72d136188a6aa5d8d2c356ccab9b86b1e082776eedbb9333b586"
APPRAISAL = os.path.join(STEER, "20260930-ai-fatigue-candidates-appraisal", "archive",
                         "AI_fatigue_candidates_AI_appraisal_2026-09-30_claude.xlsx")
APPRAISAL_SHA256 = "ed788f53462a918c8b0292711fe37d498581449b6652f10957fee55c20c7421b"
COPY34_ARCHIVE = os.path.join(STEER, "20261001-ai-fatigue-34-screening", "archive",
                              "AI_fatigue_database_2026-09-18_judge1.xlsx")
COPY34_SHA_RECORD = os.path.join(STEER, "20261001-ai-fatigue-34-screening", "archive", "copy-sha256.txt")

# 本タスクの成果物
CAND_NAME = "AI_fatigue_additional_candidates_judge1.xlsx"
CAND_ARCHIVE = os.path.join(TASK, "archive", CAND_NAME)
CAND_DOWNLOADS = os.path.join(DOWNLOADS, CAND_NAME)
CAND_SHA_RECORD = os.path.join(TASK, "archive", "candidates-sha256.txt")
LOG = os.path.join(TASK, "screening-log.jsonl")
DATA = os.path.join(TASK, "data")
EXTRA_RECORDS = os.path.join(DATA, "extra-records.json")    # X01〜（判定者用ファイルに無い記録）
EXTRACT_ROWS = os.path.join(DATA, "extract-rows.json")      # 全文抽出（判定した記録）
QUALITY_ROWS = os.path.join(DATA, "quality-rows.json")      # 品質評価（含める一次研究）
SEARCH_RUNS = os.path.join(DATA, "search-runs.json")        # 探索の検索式
SEARCH_RECORDS = os.path.join(DATA, "search-records.json")  # 探索の一覧（抄録なし）

# 判定者用ファイル『追加候補』の形（4 行目が見出し・5 行目から 220 行）
JUDGE_SHEET = "追加候補"
JUDGE_HEADER_ROW = 4
N_CANDIDATES = 220


def _user_names():
    """この機のユーザー名（★ repo に直書きしない・実行時に組む・security-checker・判断 12）。"""
    names = set()
    try:
        names.add(getpass.getuser())
    except Exception:
        pass
    names.add(os.path.basename(os.path.expanduser("~")))
    return sorted(n for n in names if n and len(n) >= 3)


_USERS = "|".join(re.escape(n) for n in _user_names())
# ★ 研究者に渡すものに入れない形（判断 11・12）。NFKC で全角を半角に寄せてから当てる（＼・：・＠・ｊｏｈｎｄ）。
#   ドライブ文字（前が英字でない・区切りは \ / ¥）・UNC・環境変数・~・git-bash のドライブ（/c/…）・macOS と Linux のホーム・
#   Downloads のフォルダ（大文字の D・区切りに挟まれたときだけ。URL の /downloads/ に当てない）・メールアドレス（@ と %40・
#   ドメインの末尾が英字 2 字以上。Recall@0.5・ASE@ICSE.2024・Scholarship@Western に当てない）・この機のユーザー名
LOCAL_RE = re.compile(
    r"(?<![A-Za-z])[A-Za-z]:[\\/¥]"
    r"|\\\\[\w.$-]+\\"
    r"|%[A-Za-z_]+%"
    r"|(?<![\w.])~[\\/¥]"
    r"|(?<![\w.:/])/[a-z]/"
    r"|(?<![\w.])/(?:Users|home)/"
    r"|[\\/¥](?-i:Downloads)[\\/¥]"
    r"|[\w.+-]+(?:@|%40)[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}"
    + (rf"|(?<![A-Za-z0-9])(?:{_USERS})(?![A-Za-z0-9])" if _USERS else ""),
    re.I)


def find_local(s):
    """手元のパス・ユーザー名・メールアドレスの形を探す（無ければ None）。"""
    return LOCAL_RE.search(unicodedata.normalize("NFKC", s or ""))


def scan_package(path):
    """xlsx・docx（zip）の XML の部品をすべて見て、手元の形と外へのリンクを返す（属性・コメント・リンク先・入力規則の文も含む）。"""
    out = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.endswith((".xml", ".rels")):
                t = z.read(n).decode("utf-8", "replace")
                m = find_local(t)
                if m:
                    out.append(f"{n}: {m.group(0)}")
                if 'TargetMode="External"' in t:
                    out.append(f"{n}: 外へのリンク")
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def is_cand_id(i):
    """候補番号（S..-..）か、本タスクで足した記録（X01〜）。"""
    import re
    return bool(re.fullmatch(r"S\d\d-\d\d|X\d\d", i or ""))
