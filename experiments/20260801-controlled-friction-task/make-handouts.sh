#!/usr/bin/env bash
# 配布用 .docx を markdown から再生成する。
# ★ 出力は handouts/（.gitignore 済み）。**markdown が正**なので編集は .md 側で行う。
# ⚠️ 被験者に渡すものは、実験者向けの注記と front matter を切り落としてから変換する。
set -euo pipefail
cd "$(dirname "$0")"
M=../../scripts/md2docx.py
mkdir -p handouts handouts/materials

# --- 1. 被験者に渡す説明類 ---------------------------------------------------
python3 "$M" participant-guide.md "handouts/G1_参加のご案内.docx" \
  "--from=# 今日の進め方"

python3 "$M" consent.md "handouts/G1_説明・同意文書.docx" \
  "--from=## 1. 研究の目的" "--until=## 実験者向けの注記" \
  "--title=説明・同意文書（キーボードの打ち方に関する研究）"

# --- 2. 課題文（ブロック開始直前に 1 枚ずつ渡す紙） --------------------------
# ★ `--frontmatter-title` が front matter を落とす。
#   ⚠️ `version: lo|hi` / `sources:` を印刷すると**条件が被験者に見える**（操作チェックが死ぬ）。
for f in materials/topic*.md materials/copy.md; do
  base=$(basename "$f" .md)
  python3 "$M" "$f" "handouts/materials/${base}.docx" --frontmatter-title
done

# --- 3. ★ 課題文の合本（実験者用・準備と封入のため）------------------------
# ⚠️ **被験者には渡さない。** 被験者に渡すのは上の 1 枚ずつ（handouts/materials/）である。
#   理由: §2.7-2「1 人は 1 題材につき 1 版しか見ない」／
#         protocol.md §2.3-2「開始直前に 1 枚だけ渡す（先読みと取り違えの防止）」
COMBINED=$(mktemp -t g1combined).md
{
  echo "# 課題文 全題材（実験者用）"
  echo
  echo "> ## ⚠️ この冊子は実験者用である。**被験者には渡さない。**"
  echo "> 被験者に渡すのは \`handouts/materials/\` の **1 枚ずつ**である"
  echo "> （§2.7-2: 1 人は 1 題材につき 1 版しか見ない ／"
  echo ">  protocol.md §2.3-2: 開始直前に 1 枚だけ渡す）。"
  echo "> 用途は**印刷・封入の準備と内容の確認**に限る。"
  echo
  echo "---"
  echo
  for n in 01 02 03 04 05 06 07 08; do
    for v in lo hi; do
      f="materials/topic${n}_${v}.md"
      [ -f "$f" ] || continue
      title=$(sed -n 's/^title: //p' "$f" | head -1)
      echo "## topic${n} — ${title} ／ 版: $(echo "$v" | tr '[:lower:]' '[:upper:]')"
      echo
      sed '1,/^---$/d' "$f" | sed 's/^## /### /'
      echo
      echo "---"
      echo
    done
  done
  echo "## copy — 書き写し（全被験者共通・位置固定）"
  echo
  sed '1,/^---$/d' materials/copy.md | sed 's/^## /### /'
} > "$COMBINED"
python3 "$M" "$COMBINED" "handouts/G1_課題文_全題材_実験者用.docx"
rm -f "$COMBINED"

# --- 4. 第三者・共同研究者向けの解説（★ 被験者には渡さない） ----------------
python3 "$M" README.md "handouts/G1_実験の解説.docx"

# --- 5. 配布事故の機械チェック ----------------------------------------------
echo
echo "[check] 被験者に渡すものに、渡してはいけない語が入っていないか"
python3 - <<'PY'
import pathlib
import re
import sys
import zipfile


def text_of(p: pathlib.Path) -> str:
    doc = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", "", doc)


bad = False

# 説明類: 実験者向けの注記や設計語が漏れていないか
NG_DOC = ("実験者向け", "被験者には渡さない", "HI", "LO", "摩擦", "仮説", "判定基準",
          "positive control", "雛形")
for n in ("G1_参加のご案内.docx", "G1_説明・同意文書.docx"):
    leak = [w for w in NG_DOC if w in text_of(pathlib.Path("handouts") / n)]
    print(f"  {n}: {'OK' if not leak else '★NG ' + str(leak)}")
    bad |= bool(leak)

# ★ 課題文: front matter が落ちているか（条件の露出を防ぐ）＋ 研究用語が載っていないか
#   ⚠️ front matter の `title` はそのまま見出しになるので、NG_DOC 相当も必ず見る
#      （実例: copy.md の title が「書き写し課題（positive control）」で漏れた）
NG_MAT = ("version", "sources", "output_requirement_chars", "id:") + NG_DOC
n_mat = 0
for p in sorted(pathlib.Path("handouts/materials").glob("*.docx")):
    leak = [w for w in NG_MAT if w in text_of(p)]
    if leak:
        print(f"  materials/{p.name}: ★NG {leak}")
        bad = True
    n_mat += 1
print(f"  materials/*.docx: {n_mat} 件 {'OK（front matter なし）' if not bad else ''}")

sys.exit(1 if bad else 0)
PY
