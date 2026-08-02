#!/usr/bin/env python3
"""課題文（materials/）の制約を機械検証する。

検証する制約の出典は preregistration.md §2.2 / §2.7（凍結）。
**本スクリプトは制約を変更しない。** 制約を変えたくなったら preregistration.md 側で
「変えた」と明記すること。

使い方:
    python3 validate_materials.py            # 存在するファイルを検証（パイロット段階）
    python3 validate_materials.py --strict   # 本番用 8 題材 × 2 版が揃っているかも検査

終了コード: 0 = 緑 / 1 = 赤（違反あり）
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import unicodedata

# --- 事前登録から来る定数（変更したら preregistration.md 側にも書くこと） ---
SOURCE_TOTAL_TOLERANCE = 0.05   # §2.2: LO 1 本と HI 3 本の資料総量を「ほぼ等しく」の許容幅
SOURCES_REQUIRED = {"lo": 1, "hi": 3, "copy": 0}
OUTPUT_REQUIREMENT = "300-400"  # §2.2: 産出要求（両条件で共通）
PRODUCTION_TOPICS = 8           # §2.7: 本番は 8 題材 × 2 版

# 教示に必ず現れるべき産出要求の表記ゆれ（どれか 1 つあればよい）
OUTPUT_REQUIREMENT_PATTERNS = [
    r"300\s*[〜~\-–ー]\s*400\s*字",
    r"３００\s*[〜~\-–ー]\s*４００\s*字",
]

FRONT_MATTER_KEYS = ["id", "version", "title", "sources", "output_requirement_chars"]


class Doc:
    """課題文 1 ファイルのパース結果。"""

    def __init__(self, path: pathlib.Path, meta: dict, sections: dict[str, str]):
        self.path = path
        self.meta = meta
        self.sections = sections

    @property
    def version(self) -> str:
        return self.meta.get("version", "")

    @property
    def topic_id(self) -> str:
        return self.meta.get("id", "")

    def source_sections(self) -> list[str]:
        return [k for k in self.sections if re.fullmatch(r"資料\s*\d+", k)]

    def source_chars(self) -> int:
        """資料本文の文字数。空白・改行を数えない（読解量の代理）。"""
        return sum(count_chars(self.sections[k]) for k in self.source_sections())


def count_chars(text: str) -> int:
    """空白・改行・制御文字を除いた文字数。全角空白も除く。"""
    return sum(1 for ch in text if not ch.isspace() and unicodedata.category(ch)[0] != "C")


def parse(path: pathlib.Path) -> tuple[Doc | None, list[str]]:
    """front matter ＋ `## 見出し` セクションに分解する。失敗は errors に積む。"""
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        return None, [f"{path.name}: front matter (--- で囲まれた見出し) が無い"]

    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"{path.name}: front matter の行に ':' が無い -> {line!r}")
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()

    for k in FRONT_MATTER_KEYS:
        if k not in meta:
            errors.append(f"{path.name}: front matter に '{k}' が無い")

    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in m.group(2).splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if current is not None:
                sections[current] = "\n".join(buf)
            current = h.group(1)
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)

    return Doc(path, meta, sections), errors


def check_doc(doc: Doc) -> list[str]:
    """1 ファイル単位の制約。"""
    errs: list[str] = []
    name = doc.path.name
    ver = doc.version

    if ver not in SOURCES_REQUIRED:
        errs.append(f"{name}: version は lo / hi / copy のいずれかであること (実際: {ver!r})")
        return errs

    # 命名と front matter の一致（取り違え防止）
    if ver == "copy":
        if doc.topic_id != "copy" or name != "copy.md":
            errs.append(f"{name}: copy 版は id=copy かつファイル名 copy.md であること")
    else:
        m = re.fullmatch(r"(topic\d{2})_(lo|hi)\.md", name)
        if not m:
            errs.append(f"{name}: ファイル名は topicNN_lo.md / topicNN_hi.md の形であること")
        else:
            if m.group(1) != doc.topic_id:
                errs.append(f"{name}: front matter の id={doc.topic_id!r} がファイル名と一致しない")
            if m.group(2) != ver:
                errs.append(f"{name}: front matter の version={ver!r} がファイル名と一致しない")

    # 教示セクション
    if "教示" not in doc.sections:
        errs.append(f"{name}: '## 教示' セクションが無い")
    elif ver != "copy":
        body = doc.sections["教示"]
        if not any(re.search(p, body) for p in OUTPUT_REQUIREMENT_PATTERNS):
            errs.append(f"{name}: 教示に産出要求 '300〜400 字' の記載が無い (§2.2)")

    # 資料本数（§2.2）
    n_src = len(doc.source_sections())
    want = SOURCES_REQUIRED[ver]
    if n_src != want:
        errs.append(f"{name}: '## 資料 N' が {n_src} 本。version={ver} は {want} 本であること (§2.2)")
    if doc.meta.get("sources") != str(want):
        errs.append(f"{name}: front matter sources={doc.meta.get('sources')!r} が実際の {want} と違う")

    # 産出要求の宣言（front matter）
    if ver == "copy":
        if "原文" not in doc.sections:
            errs.append(f"{name}: copy 版は '## 原文' を持つこと")
        if count_chars(doc.sections.get("原文", "")) < 400:
            errs.append(f"{name}: 原文が短すぎる。5 分で書き切れてしまうと下限が測れない (§2.5)")
    else:
        if doc.meta.get("output_requirement_chars") != OUTPUT_REQUIREMENT:
            errs.append(
                f"{name}: output_requirement_chars は '{OUTPUT_REQUIREMENT}' であること "
                f"(実際: {doc.meta.get('output_requirement_chars')!r}) (§2.2)")
        if doc.source_chars() == 0:
            errs.append(f"{name}: 資料本文が空")

    return errs


def check_topic_pairs(docs: list[Doc], strict: bool) -> tuple[list[str], list[str]]:
    """題材単位の制約（§2.2 の資料総量一致・§2.7 の 2 版そろい）。"""
    errs: list[str] = []
    notes: list[str] = []
    by_topic: dict[str, dict[str, Doc]] = {}
    for d in docs:
        if d.version == "copy":
            continue
        by_topic.setdefault(d.topic_id, {})[d.version] = d

    for topic, versions in sorted(by_topic.items()):
        if "lo" not in versions or "hi" not in versions:
            missing = "hi" if "lo" in versions else "lo"
            errs.append(f"{topic}: {missing} 版が無い。§2.7 は全題材に両版を要求する")
            continue
        lo, hi = versions["lo"], versions["hi"]
        if lo.meta.get("title") != hi.meta.get("title"):
            errs.append(f"{topic}: lo と hi の title が違う。同じ NN は同じ題材であること (§2.7)")
        a, b = lo.source_chars(), hi.source_chars()
        base = max(a, b)
        diff = abs(a - b) / base if base else 1.0
        line = f"{topic}: 資料総文字数 lo={a} hi={b} 差={diff:.1%}"
        if diff > SOURCE_TOTAL_TOLERANCE:
            errs.append(line + f" > 許容 {SOURCE_TOTAL_TOLERANCE:.0%} (§2.2 読解量を揃える)")
        else:
            notes.append(line + f" (許容 {SOURCE_TOTAL_TOLERANCE:.0%} 以内)")

    if strict:
        if len(by_topic) != PRODUCTION_TOPICS:
            errs.append(
                f"--strict: 本番用の題材が {len(by_topic)} 件。§2.7 は {PRODUCTION_TOPICS} 題材 × 2 版を要求する")
    else:
        if len(by_topic) < PRODUCTION_TOPICS:
            notes.append(
                f"題材 {len(by_topic)}/{PRODUCTION_TOPICS} 件（パイロット段階では正常。"
                f"本番前に --strict を通すこと）")
    return errs, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None, help="materials ディレクトリ (既定: 本スクリプトの隣)")
    ap.add_argument("--strict", action="store_true",
                    help="本番用 8 題材 × 2 版が揃っているかも検査する")
    a = ap.parse_args()

    root = pathlib.Path(a.dir) if a.dir else pathlib.Path(__file__).resolve().parent / "materials"
    if not root.is_dir():
        print(f"[NG] materials ディレクトリが無い: {root}")
        return 1

    paths = sorted(p for p in root.glob("*.md") if p.name != "README.md")
    if not paths:
        print(f"[NG] {root} に課題文が 1 つも無い")
        return 1

    errors: list[str] = []
    notes: list[str] = []
    docs: list[Doc] = []
    for p in paths:
        doc, errs = parse(p)
        errors += errs
        if doc is not None:
            docs.append(doc)
            errors += check_doc(doc)

    if not any(d.version == "copy" for d in docs):
        errors.append("copy.md（positive control 用の定型文）が無い (§2.5)")

    pair_errs, pair_notes = check_topic_pairs(docs, a.strict)
    errors += pair_errs
    notes += pair_notes

    print(f"[materials] {len(paths)} ファイルを検証した ({root})")
    for d in docs:
        if d.version == "copy":
            print(f"  - {d.path.name:20s} version=copy 原文={count_chars(d.sections.get('原文', ''))} 字")
        else:
            print(f"  - {d.path.name:20s} version={d.version:3s} 資料{len(d.source_sections())}本 "
                  f"計{d.source_chars()}字")
    for n in notes:
        print(f"  [note] {n}")

    if errors:
        print(f"\n[NG] 違反 {len(errors)} 件:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\n[OK] 課題文の制約はすべて満たされている")
    return 0


if __name__ == "__main__":
    sys.exit(main())
