#!/usr/bin/env bash
# 配布用 .docx を markdown から再生成する。
# ★ 出力は handouts/（.gitignore 済み）。**markdown が正**なので編集は .md 側で行う。
# ⚠️ 被験者に渡す 2 本は、実験者向けの注記を切り落としてから変換する（--from / --until）。
set -euo pipefail
cd "$(dirname "$0")"
M=../../scripts/md2docx.py
mkdir -p handouts

python3 "$M" participant-guide.md "handouts/G1_参加のご案内.docx" \
  "--from=# 今日の進め方"

python3 "$M" consent.md "handouts/G1_説明・同意文書.docx" \
  "--from=## 1. 研究の目的" "--until=## 実験者向けの注記" \
  "--title=説明・同意文書（キーボードの打ち方に関する研究）"

# ★ 解説は第三者・共同研究者向け。**被験者には渡さない。**
python3 "$M" README.md "handouts/G1_実験の解説.docx"

echo
echo "[check] 被験者に渡す 2 本に、渡してはいけない語が入っていないか"
python3 - <<'PY'
import pathlib
import re
import sys
import zipfile

NG = ("実験者向け", "被験者には渡さない", "HI", "LO", "摩擦", "仮説", "判定基準",
      "positive control", "雛形")
bad = False
for n in ("G1_参加のご案内.docx", "G1_説明・同意文書.docx"):
    t = re.sub(r"<[^>]+>", "", zipfile.ZipFile(pathlib.Path("handouts") / n)
               .read("word/document.xml").decode("utf-8"))
    leak = [w for w in NG if w in t]
    print(f"  {n}: {'OK' if not leak else '★NG ' + str(leak)}")
    bad |= bool(leak)
sys.exit(1 if bad else 0)
PY
