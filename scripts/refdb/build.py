#!/usr/bin/env python3
"""文献 DB を作り直す（.steering/20261018-literature-db/）。

正本は各枝の docs/references.md（判断 1）。それを key でまとめ、精読カードでの記述と
要約（docs/literature/refdb/summaries.json）を重ね、シートの「一覧」へ貼る CSV・
検索のページ・CSL-JSON・.bib 2 本を作る。シートで人が書いた列（読んだ・メモ）は
--keep で渡すと key で結び直す。

    python3 scripts/refdb/build.py [--out DIR] [--keep SHEET.csv|SHEET.json] [--fetch]

ネットに出るのは --fetch のときだけ（判断 7）。手順の全体は scripts/refdb/README.md。
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import os
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_CACHE = Path.home() / ".cache" / "gse-refdb"

COLUMNS = [
    "ID", "番号の衝突", "名前空間", "著者・題", "出典", "年", "研究の筋", "要約", "特徴",
    "要約の材料", "カードでの記述", "接地（全文）", "カード", "カード外の引用元", "状態", "枝",
    "key", "URL",
]
NO_SUMMARY_UNCITED = "（要約なし: カードから引かれていない）"
NO_SUMMARY_CITED = "（要約なし: まだ書いていない）"
OFF_CARD = "カード外"
UNCITED = "未引用"
ORPHAN_STATE = "正本に無い"

FORMULA_LEAD = ("=", "+", "-", "@")


def output_names(name: str) -> list[str]:
    return [f"{name}.csv", f"{name}.html", f"{name}.csl.json", f"{name}_biblatex.bib", f"{name}_bibtex.bib",
            f"{name}.xlsx", "missing_summaries.json", "manifest.json"]


# --deliver で「文献DB」へ渡すもの（作業の名前 → 渡し先の日付なしの名前・判断 17）
DELIVER = {"{name}.xlsx": "GSE文献DB.xlsx", "{name}_bibtex.bib": "GSE文献DB.bib"}
SHEET_URL = "https://docs.google.com/spreadsheets/d/1v7frJm2a6BkXzepEpglB62AT_2c3t0NzJ2mNA8UfRFw/edit"
PAGE_URL = "https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA"


EXIT_ORPHANS = 3  # 読んだ・メモが黙って消えうるので止めた（消えた key・空の key・重なり）

ROW_RE = re.compile(r"^\| \[([PV]\d+)\] \| ")
CITE_RE = re.compile(r"\[([PV]\d+)\]")
# 票（3-0 など）は日付（2026-03-04）の中に当てない。「確定した」「否決された」の動詞にも当てない
TEMP_RE = re.compile(
    r"(確定(?![しさす])|PLAUSIBLE BUT UNPROVEN|判定不能|否決(?![しさす])|confirmed|refuted"
    r"|(?<![\d-])(?:3-0|2-1|1-2|0-3)(?![\d-]))"
)
# references.md の重複の列は「—」か、番号で始まる短い印（→P430・=V9・[P270]・→ **[P116] が正**・[V187] と同じ主題…）
DUP_RE = re.compile(r"^(—|[→←=]?\s*(?:\*\*)?\[?[PV]\d+.{0,60})$")
# 頁（pp.1851–1860・7:2072）・論文番号（e2013097118）・範囲の後ろ側（2023–2026）は年にしない
YEAR_RE = re.compile(r"(?<![0-9A-Za-z./–-])(1[89]\d\d|20[0-4]\d)(?!\d|\.\d)")
MARKS_RE = re.compile(r"[★⚠️]+")
ANGLE_URL_RE = re.compile(r"<(https?://[^>\s]+)>")


# ---------------------------------------------------------------- 読む元


class GitSource:
    """`git show <枝>:<path>` で読む。作業ツリーは切り替えない。"""

    def __init__(self, repo: Path = REPO):
        self.repo = repo

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True)

    def read(self, branch: str, path: str) -> str | None:
        r = self._git("show", f"{branch}:{path}")
        return r.stdout if r.returncode == 0 else None

    def ls(self, branch: str, prefix: str, recursive: bool) -> list[str]:
        # -z: 日本語のパスを引用符と 8 進のエスケープで返させない
        args = ["ls-tree", "-z", "--name-only"] + (["-r"] if recursive else []) + [branch, "--", prefix]
        r = self._git(*args)
        if r.returncode != 0:
            raise RuntimeError(f"枝を読めない: {branch}（{r.stderr.strip()}）")
        return [x for x in r.stdout.split("\0") if x]

    def commit(self, branch: str) -> str:
        r = self._git("rev-parse", branch)
        if r.returncode != 0:
            raise RuntimeError(f"枝が無い: {branch}（git fetch を先に）")
        return r.stdout.strip()


class PinnedSource:
    """枝の名前はそのままに、決めた commit を読む（--pin・実データの照合で 2026-10-18 の時点を読むため）。"""

    def __init__(self, source, pins: dict[str, str]):
        self.source, self.pins = source, pins

    def read(self, branch: str, path: str) -> str | None:
        return self.source.read(self.pins.get(branch, branch), path)

    def ls(self, branch: str, prefix: str, recursive: bool) -> list[str]:
        return self.source.ls(self.pins.get(branch, branch), prefix, recursive)

    def commit(self, branch: str) -> str:
        return self.source.commit(self.pins.get(branch, branch))


class DirSource:
    """テスト用。<root>/<枝の / を __ にした名前>/ を枝の中身として読む。"""

    def __init__(self, root: Path):
        self.root = Path(root)

    def _dir(self, branch: str) -> Path:
        return self.root / branch.replace("/", "__")

    def read(self, branch: str, path: str) -> str | None:
        p = self._dir(branch) / path
        return p.read_text(encoding="utf-8") if p.is_file() else None

    def ls(self, branch: str, prefix: str, recursive: bool) -> list[str]:
        base = self._dir(branch)
        if not base.is_dir():
            raise RuntimeError(f"枝を読めない: {branch}")
        top = base / prefix
        if not top.exists():
            return []
        it = top.rglob("*") if recursive else top.iterdir()
        return sorted(str(p.relative_to(base)) for p in it if p.is_file())

    def commit(self, branch: str) -> str:
        return "fixture"


# ---------------------------------------------------------------- 1. 書誌と引用


def clean(s: str) -> str:
    s = MARKS_RE.sub("", s).replace("**", "")
    s = ANGLE_URL_RE.sub(r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_ref_line(line: str) -> dict | None:
    """references.md の 1 行。8 列（重複の列あり）と 7 列（なし）を扱い、接地の中の ' | ' は接地に戻す。"""
    if not ROW_RE.match(line):
        return None
    c = [x.strip() for x in line.strip().strip("|").split(" | ")]
    if len(c) < 7:
        return None
    if len(c) >= 8 and DUP_RE.match(c[-2]):
        note, dup, st = " | ".join(c[5:-2]), c[-2], c[-1]
    else:  # 7 列（重複の列が無い）。接地に ' | ' があれば接地に戻す
        note, dup, st = " | ".join(c[5:-1]), "—", c[-1]
    return {
        "id": c[0].strip("[]"), "key": c[1], "at": c[2], "src": c[3],
        "url": c[4].strip("<>"), "note": note, "dup": dup, "st": st,
    }


def collect(source, branches: list[str]) -> dict:
    works: dict[str, dict] = {}
    idmap: dict[tuple[str, str], str] = {}
    skipped: list[str] = []
    for b in branches:
        text = source.read(b, "docs/references.md")
        if text is None:
            raise RuntimeError(f"{b} に docs/references.md が無い")
        for line in text.split("\n"):
            if not ROW_RE.match(line):
                continue
            r = parse_ref_line(line)
            if r is None:
                skipped.append(f"{b}: {line[:80]}")
                continue
            idmap[(b, r["id"])] = r["key"]
            w = works.setdefault(r["key"], {
                "key": r["key"], "ids": {}, "at": r["at"], "src": r["src"], "url": r["url"],
                "note": r["note"], "st": r["st"], "branches": [],
            })
            w["ids"].setdefault(r["id"], []).append(b)
            if b not in w["branches"]:
                w["branches"].append(b)
    cite: dict[str, set] = collections.defaultdict(set)
    other: dict[str, set] = collections.defaultdict(set)
    for b in branches:
        files = source.ls(b, "docs", True) + source.ls(b, "experiments", True)
        for f in files:
            if not f.endswith(".md") or f == "docs/references.md":
                continue
            text = source.read(b, f) or ""
            for i in set(CITE_RE.findall(text)):
                k = idmap.get((b, i))
                if not k:
                    continue
                if is_card_path(f):
                    cite[k].add(f.split("/")[-1])
                else:
                    other[k].add(f)
    # 同じ番号が枝によって別の文献を指す（番号の衝突）
    by_id: dict[str, set] = collections.defaultdict(set)
    for (b, i), k in idmap.items():
        by_id[i].add(k)
    collided = {i for i, ks in by_id.items() if len(ks) > 1}
    return {
        "works": works, "idmap": idmap, "skipped": skipped, "collided": collided,
        "cite": {k: sorted(v) for k, v in cite.items()},
        "other": {k: sorted(v) for k, v in other.items()},
    }


def is_card_path(f: str) -> bool:
    return f.startswith("docs/literature/") and not f.endswith("_index.md")


# ---------------------------------------------------------------- 2. カードでの記述


def collect_claims(source, branches: list[str], idmap: dict) -> dict[str, list[dict]]:
    out: dict[str, dict] = collections.defaultdict(dict)
    for b in branches:
        for f in source.ls(b, "docs/literature/", False):
            fn = f.split("/")[-1]
            if not fn.endswith(".md") or fn.startswith("_") or "template" in fn:
                continue
            for line in (source.read(b, f) or "").split("\n"):
                if not (line.startswith("|") or line.startswith("### ")):
                    continue
                ids = set(CITE_RE.findall(line))
                if not ids:
                    continue
                if line.startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if all(set(c) <= set("-: ") for c in cells):
                        continue
                    txt = max(cells, key=len)
                else:
                    txt = line[4:]
                t = TEMP_RE.findall(line)
                temp = t[-1] if t else ""
                txt = clean(CITE_RE.sub("", txt).replace("`", ""))[:220]
                for i in ids:
                    k = idmap.get((b, i))
                    if k:
                        out[k][(fn[:8], txt)] = temp
    return {k: [{"d": d, "t": t, "temp": tp} for (d, t), tp in v.items()] for k, v in out.items()}


def card_labels(source, branches: list[str]) -> dict[str, str]:
    """カードのファイル名 → _index.md の題（60 字まで）。最初に見つけた枝のもの。"""
    labels: dict[str, str] = {}
    for b in branches:
        for line in (source.read(b, "docs/literature/_index.md") or "").split("\n"):
            m = re.match(r"^\|[^|]*\| ([^|]*) \| \[[^\]]*\]\(([^)]+\.md)\)", line)
            if m and m.group(2) not in labels:
                labels[m.group(2)] = clean(m.group(1).replace("`", ""))[:60]
    return labels


# ---------------------------------------------------------------- 4. 行


def year_of(src: str) -> int | None:
    """出典の年。注記（最初の「（」から後）より前の最後の年を採る（頁の 1936–1962 や e2013… を年にしない）。
    前に無ければ全体の最初の年。"""
    head = YEAR_RE.findall(re.split(r"（| \(", src, maxsplit=1)[0])
    if head:
        return int(head[-1])
    m = YEAR_RE.findall(src)
    return int(m[0]) if m else None


def fill_url(url: str, key: str) -> str:
    if url and url != "—":
        return url
    t, _, v = key.partition(":")
    if t == "doi":
        return "https://doi.org/" + v
    if t == "arXiv":
        return "https://arxiv.org/abs/" + v
    return "" if url == "—" else url


def strands_of(cards: list[str], strand_map: list[dict]) -> list[str]:
    got = []
    for s in strand_map:
        if any(any(p in c for p in s["patterns"]) for c in cards):
            got.append(s["name"])
    return got


def build_rows(data: dict, claims: dict, summaries: dict, labels: dict, cfg: dict) -> list[dict]:
    short = cfg.get("branch_names", {})
    rows = []
    for k, w in data["works"].items():
        ids = list(w["ids"])
        cards = data["cite"].get(k, [])
        other = data["other"].get(k, [])
        if cards:
            strands = strands_of(cards, cfg["strands"]) or ["未分類"]
        else:
            strands = [OFF_CARD] if other else [UNCITED]
        s = summaries.get(k)
        if s:
            basis = s.get("basis", "")
        else:
            basis = NO_SUMMARY_CITED if cards else NO_SUMMARY_UNCITED
        cc = claims.get(k, [])
        # 番号が文献の枝の一部にしか無いときは、どの枝の番号かを添える
        id_labels = [
            i if len(ids) == 1 or w["ids"][i] == w["branches"]
            else f"{i}（{', '.join(short.get(b, b) for b in w['ids'][i])}）"
            for i in ids
        ]
        rows.append({
            "ID": "; ".join(id_labels),
            "番号の衝突": "あり" if any(i in data["collided"] for i in ids) else "",
            "名前空間": "".join(sorted({i[0] for i in ids}, key="PV".index)),
            "著者・題": clean(w["at"]),
            "出典": clean(w["src"]),
            "年": year_of(w["src"]) or "",
            "研究の筋": " / ".join(strands),
            "要約": s.get("summary", "") if s else "",
            "特徴": s.get("features", "") if s else "",
            "要約の材料": basis,
            "カードでの記述": " ／ ".join(
                f"{c['d']}・{c['temp']}: {c['t']}" if c["temp"] else f"{c['d']}: {c['t']}" for c in cc
            ),
            "接地（全文）": clean(w["note"]),
            "カード": " / ".join(f"{labels.get(c, c[9:-3])}（{c[:8]}）" for c in cards),
            "カード外の引用元": " / ".join(o.removeprefix("docs/") for o in other),
            "状態": clean(w["st"]),
            "枝": ", ".join(short.get(b, b) for b in w["branches"]),
            "key": k,
            "URL": fill_url(w["url"], k),
            "_cards": cards, "_cc": cc, "_strands": strands, "_other": other,
        })
    return rows


# ---------------------------------------------------------------- 読んだ・メモの結び直し


class OrphanError(Exception):
    def __init__(self, orphans: list[dict]):
        super().__init__(f"正本に無い key に読んだ・メモが {len(orphans)} 件ある")
        self.orphans = orphans


class KeepConflict(Exception):
    """読んだ・メモを 1 行に結び直せない（空の key・同じ key の 2 行・付け替え先の重なり）。"""

    def __init__(self, problems: list[str]):
        super().__init__(f"読んだ・メモを結び直せない行が {len(problems)} 件ある")
        self.problems = problems


def read_keep(path: Path) -> list[list[str]]:
    """シートの「一覧」。CSV か、Sheets の get_values の返り値（2 次元の配列・{"values": …} も可）。"""
    text = path.read_text(encoding="utf-8-sig")
    # 拡張子でなく中身で見る（Sheets の MCP は大きな返り値を .txt に保存する・2026-10-18 に実測）
    if path.suffix.lower() == ".json" or text.lstrip()[:1] in ("{", "["):
        try:
            j = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"--keep を JSON として読めない（先頭が {{ か [ なので JSON とみなした）: {e}") from e
        if isinstance(j, dict):
            if "values" not in j:
                raise ValueError(f"--keep の JSON に values が無い（キー: {sorted(j)}）。get_values の返り値か確かめる")
            j = j["values"]
        if not isinstance(j, list) or not all(isinstance(r, list) for r in j):
            raise ValueError("--keep の JSON が 2 次元の配列でない")
        return [[("" if c is None else str(c)) for c in r] for r in j]
    return list(csv.reader(io.StringIO(text)))


def has_content(vals: dict) -> bool:
    return any(v.strip() for v in vals.values())


def keep_map(table: list[list[str]], human: list[str], checkbox: list[str]) -> dict[str, dict]:
    """key → 人が書いた列の値。表の形が違えば ValueError、1 行に結び直せなければ KeepConflict で止める。"""
    if not table:
        raise ValueError("--keep の表が空（見出しの行も無い）")
    h = [c.strip() for c in table[0]]
    lacking = [c for c in ["key", *human] if c not in h]
    if lacking:
        raise ValueError(f"--keep の表に {lacking} の列が無い（見出し: {h}）")
    doubled = [c for c in ["key", *human] if h.count(c) > 1]
    if doubled:
        raise ValueError(f"--keep の表に {doubled} の列が 2 つ以上ある（どちらを読むか決められない）")
    ki = h.index("key")
    cols = [(c, h.index(c)) for c in human]
    out: dict[str, dict] = {}
    problems = []
    for n, r in enumerate(table[1:], start=2):
        vals = {c: (r[i] if i < len(r) else "") for c, i in cols}
        # チェックボックスの列は、付けていない行が FALSE で返る。それは書いた内容に数えない
        vals = {c: ("" if c in checkbox and v.strip().upper() == "FALSE" else v) for c, v in vals.items()}
        key = r[ki].strip() if ki < len(r) else ""
        if not has_content(vals):
            continue
        if not key:
            problems.append(f"{n} 行目: key が空なのに書いた内容がある {vals}")
        elif key in out and out[key] != vals:
            problems.append(f"{n} 行目: key {key} の行が 2 つあり、書いた内容が違う {out[key]} / {vals}")
        else:
            out[key] = vals
    if problems:
        raise KeepConflict(problems)
    return out


def rejoin(rows: list[dict], kept: dict[str, dict], human: list[str],
           rekey: dict[str, str], keep_orphans: bool) -> dict:
    by_key = {r["key"]: r for r in rows}
    for r in rows:
        for c in human:
            r[c] = ""
    placed: dict[str, str] = {}  # 付け替え先の key → 元の key
    problems, orphans = [], []
    for k, vals in kept.items():
        new = rekey.get(k, k)
        if by_key.get(new) is None:
            orphans.append({"key": k, **vals})
            continue
        if new in placed:
            problems.append(f"{placed[new]} と {k} が同じ key {new} に入る（--rekey を確かめる）")
            continue
        placed[new] = k
    if problems:
        raise KeepConflict(problems)
    if orphans and not keep_orphans:
        raise OrphanError(orphans)
    for new, k in placed.items():
        for c in human:
            by_key[new][c] = kept[k].get(c, "")
    for o in orphans:
        r = {c: "" for c in COLUMNS}
        r.update({"ID": "—", "key": o["key"], "状態": ORPHAN_STATE, "_cards": [], "_cc": [], "_strands": [], "_other": []})
        for c in human:
            r[c] = o.get(c, "")
        rows.append(r)
    return {"joined": len(placed), "orphans": len(orphans)}


# ---------------------------------------------------------------- 5. CSV・ページ・CSL


def write_csv(rows: list[dict], human: list[str], path: Path) -> None:
    cols = COLUMNS + human
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerow(cols)
        for r in rows:
            wr.writerow([r.get(c, "") for c in cols])


def page_data(rows: list[dict], data: dict, summaries: dict, labels: dict) -> list[dict]:
    out = []
    for r in rows:
        k = r["key"]
        w = data["works"].get(k)
        s = summaries.get(k, {})
        out.append({
            "id": r["ID"], "coll": r["番号の衝突"] == "あり", "ns": r["名前空間"],
            "at": r["著者・題"], "src": r["出典"], "yr": r["年"] or None, "strands": r["_strands"],
            "cards": [{"t": labels.get(c, c[9:-3]), "f": c} for c in r["_cards"]],
            "other": r["_other"], "st": r["状態"], "br": r["枝"], "key": k, "url": r["URL"],
            "note": r["接地（全文）"] if w else "", "sum": s.get("summary", ""),
            "feat": s.get("features", ""), "basis": s.get("basis", ""), "cc": r["_cc"],
        })
    return out


def write_page(rows, data, summaries, labels, cfg, sub: str, path: Path) -> None:
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    # <script> の中に置くので < をすべて \u003c にする（</script> も <!-- も作らせない）
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("<", "\\u003c")  # noqa: E731
    strands = [s["name"] for s in cfg["strands"]] + [OFF_CARD, UNCITED]
    for ph in ("__DATA__", "__STRANDS__", "__SUB__"):
        if ph not in tpl:
            raise RuntimeError(f"template.html に {ph} が無い")
    html = (tpl.replace("__SUB__", sub)
            .replace("__STRANDS__", js(strands))
            .replace("__DATA__", js(page_data(rows, data, summaries, labels))))
    path.write_text(html, encoding="utf-8")


CSL_KEEP = ["type", "title", "author", "editor", "container-title", "volume", "issue", "page",
            "issued", "DOI", "URL", "publisher", "ISBN", "event", "collection-title", "number"]
CSL_STR = ["title", "container-title", "volume", "issue", "page", "DOI", "URL", "publisher",
           "ISBN", "event", "collection-title", "number"]


def first_str(v):
    """DataCite 経由で配列や数で来る欄を、先頭の要素の文字列にする。"""
    while isinstance(v, list):
        if not v:
            return None
        v = v[0]
    if isinstance(v, dict):
        return None
    return None if v is None else str(v)


# doi.org は Crossref の型名で返すことがある。CSL の型名に直さないと pandoc がすべて @misc にする
CROSSREF_TYPES = {
    "journal-article": "article-journal", "proceedings-article": "paper-conference",
    "book-chapter": "chapter", "posted-content": "article", "edited-book": "book",
    "monograph": "book", "reference-entry": "entry", "dissertation": "thesis",
}
NAME_PARTS = ["family", "given", "literal", "suffix", "non-dropping-particle", "dropping-particle"]


def name_of(a) -> dict | None:
    """人名は名前の部分だけ残す（Crossref の affiliation・role の入れ子を pandoc に渡さない）。"""
    if not isinstance(a, dict):
        return None
    n = {k: first_str(a[k]) for k in NAME_PARTS if k in a and first_str(a[k])}
    return n or None


def fix_issued(v) -> dict | None:
    """date-parts の null や文字を外し、数だけ残す。空なら None（欄ごと外す）。"""
    if not isinstance(v, dict):
        return None
    parts = []
    for dp in v.get("date-parts") or []:
        if not isinstance(dp, list):
            continue
        nums = []
        for x in dp:
            if isinstance(x, bool):
                break
            if isinstance(x, int):
                nums.append(x)
            elif isinstance(x, str) and x.strip().isdigit():
                nums.append(int(x))
            else:
                break
        if nums:
            parts.append(nums)
    return {"date-parts": parts} if parts else None


def csl_item(r: dict, raw: dict | None, cite_key: str, summary: str) -> tuple[dict, bool]:
    item: dict = {"id": cite_key}
    from_cache = bool(raw) and "_err" not in raw
    if from_cache:
        for f in CSL_KEEP:
            if f not in raw:
                continue
            v = raw[f]
            if f == "type":
                v = first_str(v)
                v = CROSSREF_TYPES.get(v, v)
            elif f in CSL_STR:
                v = first_str(v)
            elif f == "issued":
                v = fix_issued(v)
            elif f in ("author", "editor"):
                v = [n for n in (name_of(a) for a in v) if n] if isinstance(v, list) else None
            if v:
                item[f] = v
    if "title" not in item:
        at = r["著者・題"]
        item["title"] = at.split(" — ", 1)[1] if " — " in at else at
        if " — " in at:
            item.setdefault("author", [{"literal": at.split(" — ", 1)[0]}])
        if r["出典"]:
            item.setdefault("container-title", r["出典"])
        if r["年"]:
            item.setdefault("issued", {"date-parts": [[int(r["年"])]]})
        if r["URL"]:
            item.setdefault("URL", r["URL"])
        if r["key"].startswith("doi:"):
            item.setdefault("DOI", r["key"][4:])
        item.setdefault("type", "document")
    item.setdefault("type", "document")
    if r["研究の筋"]:
        item["keyword"] = r["研究の筋"].replace(" / ", ", ")
    item["note"] = f"GSE {r['ID']}" + (f" ｜ {summary}" if summary else "")
    return item, from_cache


def build_csl(rows: list[dict], csl_raw: dict, summaries: dict) -> tuple[list[dict], dict]:
    items, used, n_cache = [], set(), 0
    for r in rows:
        if r["状態"] == ORPHAN_STATE:
            continue
        ck = r["ID"].split("; ")[0].split("（")[0]
        if ck in used:
            ck = ck + "_" + re.sub(r"[^A-Za-z0-9]", "", r["key"])[-8:]
        base, k = ck, 2
        while ck in used:  # 末尾を足しても重なるときは番号を足す
            ck, k = f"{base}_{k}", k + 1
        used.add(ck)
        it, hit = csl_item(r, csl_raw.get(r["key"]), ck, summaries.get(r["key"], {}).get("summary", ""))
        n_cache += hit
        items.append(it)
    return items, {"csl_from_cache": n_cache, "csl_minimal": len(items) - n_cache}


def write_bib(csl_path: Path, out_base: Path) -> dict:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc が無い（brew install pandoc・または --no-bib）")
    counts = {}
    for fmt in ("biblatex", "bibtex"):
        p = out_base.parent / f"{out_base.name}_{fmt}.bib"
        r = subprocess.run([pandoc, "-f", "csljson", "-t", fmt, str(csl_path), "-o", str(p)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"pandoc（{fmt}）が失敗: {r.stderr.strip()[:300]}")
        counts[fmt] = len(re.findall(r"^@\w+\{", p.read_text(encoding="utf-8"), re.M))
    return counts


# ---------------------------------------------------------------- xlsx（一覧・書誌・説明を 1 つに）


def bib_entries(text: str) -> dict[str, str]:
    """pandoc が書いた .bib を、引用キー → 項目の全文に分ける。"""
    out = {}
    for ent in re.split(r"\n(?=@)", text.strip()):
        m = re.match(r"@\w+\{([^,]+),", ent)
        if m:
            out[m.group(1)] = ent.strip()
    return out


XLSX_CELL_MAX = 32767  # Excel のセルの上限。openpyxl は超えた分を黙って切る（2026-10-18 に再現）
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")  # xlsx に書けない制御文字（openpyxl は例外で全体を落とす）


def put(ws, row: int, col: int, v, stats: dict | None = None) -> None:
    """値を書く。= で始まる文字列は数式にせず文字列のまま置く。制御文字は外して数え、上限を超える文字列は止める。"""
    if isinstance(v, str):
        v, n = CONTROL_RE.subn("", v)
        if stats is not None:
            stats["xlsx_removed_control_chars"] = stats.get("xlsx_removed_control_chars", 0) + n
        if len(v) > XLSX_CELL_MAX:
            head = ws.cell(row=1, column=col).value
            raise RuntimeError(f"xlsx のセルが上限 {XLSX_CELL_MAX} 字を超える（シート {ws.title}・{row} 行目・列 {head}・{len(v)} 字）")
    c = ws.cell(row=row, column=col, value=v)
    if isinstance(v, str) and v.startswith("="):
        c.data_type = "s"


def write_xlsx(rows: list[dict], human: list[str], items: list[dict], bibtex: str, info: dict, path: Path) -> dict:
    try:
        from openpyxl import Workbook  # noqa: PLC0415  無いときは --no-xlsx で外せる
        from openpyxl.styles import Font
    except ImportError as e:
        raise RuntimeError("openpyxl が無い（~/.venvs/gse-provision/bin/python で回すか、--no-xlsx）") from e
    stats: dict = {"xlsx_removed_control_chars": 0}
    # xlsx のバイト列は回すたびに変わる（openpyxl が保存の時刻を書き、zip の各項目にも時刻が入る）。
    # 同じ入力かどうかは、xlsx のハッシュではなく CSV のハッシュで見る
    wb = Workbook()
    readme = wb.active
    readme.title = "説明"
    lines = [
        ("GSE 文献DB（xlsx の写し）", ""),
        ("本体", f"Google スプレッドシート「GSE 文献DB」 {SHEET_URL}（読んだ・メモはそちらに書く。この xlsx に書いても作り直しで戻らない）"),
        ("検索のページ", PAGE_URL),
        ("作った日", info["date"]),
        ("文献", info["works"]),
        ("要約", info["summaries"]),
        ("カードでの記述", f"{info['claims_works']} 件（{info['claims_lines']} 行）"),
        ("番号の衝突", info["collided_ids"]),
        ("書誌の正本", "各枝の docs/references.md（作り方は repo の scripts/refdb/README.md）"),
    ] + [(f"枝 {b}", c) for b, c in info["branches"].items()]
    for i, (k, v) in enumerate(lines, 1):
        put(readme, i, 1, k, stats)
        put(readme, i, 2, str(v), stats)  # 数は右寄せになり広い列の右端へ隠れるので、説明では文字で置く
    readme["A1"].font = Font(bold=True, size=14)
    readme.column_dimensions["A"].width = 48
    readme.column_dimensions["B"].width = 110

    ws = wb.create_sheet("一覧")
    cols = COLUMNS + human
    for j, c in enumerate(cols, 1):
        put(ws, 1, j, c, stats)
        ws.cell(row=1, column=j).font = Font(bold=True)
    for i, r in enumerate(rows, 2):
        for j, c in enumerate(cols, 1):
            put(ws, i, j, r.get(c, ""), stats)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    widths = {"ID": 14, "著者・題": 60, "出典": 36, "年": 7, "研究の筋": 30, "要約": 60, "特徴": 50, "key": 32, "URL": 40}
    for j, c in enumerate(cols, 1):
        ws.column_dimensions[ws.cell(row=1, column=j).column_letter].width = widths.get(c, 18)

    bs = wb.create_sheet("書誌")
    entries = bib_entries(bibtex)
    for j, c in enumerate(["引用キー", "ID", "key", "種類", "BibTeX"], 1):
        put(bs, 1, j, c, stats)
        bs.cell(row=1, column=j).font = Font(bold=True)
    for i, (it, r) in enumerate(zip(items, [r for r in rows if r["状態"] != ORPHAN_STATE]), 2):
        for j, v in enumerate([it["id"], r["ID"], r["key"], it.get("type", ""), entries.get(it["id"], "")], 1):
            put(bs, i, j, v, stats)
    bs.freeze_panes = "B2"
    bs.auto_filter.ref = bs.dimensions
    for col, w in zip("ABCDE", (16, 14, 32, 16, 100)):
        bs.column_dimensions[col].width = w
    wb.save(path)
    return stats


def deliver(out: Path, name: str, to: Path) -> list[str]:
    """作業の成果物のうち xlsx と BibTeX を、渡し先へ日付なしの名前で写す（上書き）。
    両方を一時の名前で写し終えてから入れ替える。入れ替えの途中で止まったら、前の版を戻す（新旧を混ぜない）。
    片方でも無ければ何も写さずに止める。"""
    srcs = {dst: out / src.format(name=name) for src, dst in DELIVER.items()}
    lacking = [str(p) for p in srcs.values() if not p.exists()]
    if lacking:
        raise RuntimeError(f"--deliver で渡すものが無い: {lacking}（何も写していない）")
    to.mkdir(parents=True, exist_ok=True)
    tmps: dict[str, Path] = {}
    backups: dict[str, Path] = {}  # 入れ替える前の版（止まったら戻す）
    placed: list[str] = []
    try:
        for dst, p in srcs.items():
            fd, t = tempfile.mkstemp(prefix=f".{dst}.", suffix=".tmp", dir=to)
            os.close(fd)
            tmps[dst] = Path(t)  # 写す前に覚える（写す途中で止まっても消せるように）
            shutil.copyfile(p, t)
        try:
            for dst in srcs:
                if (to / dst).exists():
                    b = to / f".{dst}.prev"
                    (to / dst).replace(b)
                    backups[dst] = b
                tmps[dst].replace(to / dst)
                placed.append(dst)
        except BaseException:
            for dst in placed:
                (to / dst).unlink(missing_ok=True)
            for dst, b in backups.items():
                b.replace(to / dst)
            backups.clear()
            raise
    finally:
        for t in tmps.values():
            t.unlink(missing_ok=True)
        for b in backups.values():
            b.unlink(missing_ok=True)
    return list(srcs)


# ---------------------------------------------------------------- 要約が無いもの


def missing_summaries(rows: list[dict], data: dict, summaries: dict, abstracts: dict) -> list[dict]:
    out = []
    for r in rows:
        k = r["key"]
        if not r["_cards"] or k in summaries:
            continue
        a = abstracts.get(k, {}) or {}
        out.append({
            "key": k, "id": r["ID"], "title": r["著者・題"], "venue": r["出典"],
            "abstract": (a.get("abs") or "")[:3000], "gse_note": r["接地（全文）"][:700],
        })
    return out


# ---------------------------------------------------------------- 全体


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def parse_rekey(pairs: list[str]) -> dict[str, str]:
    """--rekey 旧=新 の並び。同じ旧 key に違う新 key が 2 つあれば止める（後勝ちでメモを別の文献へ移さない）。"""
    out: dict[str, str] = {}
    for x in pairs:
        if "=" not in x:
            raise ValueError(f"--rekey は 旧=新 の形で渡す: {x}")
        old, new = (y.strip() for y in x.split("=", 1))
        if out.get(old, new) != new:
            raise ValueError(f"--rekey で {old} の付け替え先が 2 つある（{out[old]} / {new}）")
        out[old] = new
    return out


def run(args, source=None) -> int:
    if args.deliver and (args.no_xlsx or args.no_bib):
        raise ValueError("--deliver は xlsx と .bib の両方を渡す。--no-xlsx / --no-bib とは一緒に使えない（前の回のものが残って新旧が混ざる）")
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    branches = args.branches.split(",") if args.branches else cfg["branches"]
    human = cfg.get("human_columns", ["読んだ", "メモ"])
    source = source or GitSource()
    pins = dict(x.split("=", 1) for x in (args.pin or []))
    if pins:
        source = PinnedSource(source, pins)
    cache = Path(args.cache).expanduser()
    today = args.date or dt.date.today().isoformat()
    out = Path(args.out).expanduser() if args.out else cache / "out" / today
    summaries_path = Path(args.summaries)

    # シートの値は、ネットに出る前・何かを書く前に読んで形を確かめる（ここで止まれば何も書かない）
    kept = None
    if args.keep:
        kept = keep_map(read_keep(Path(args.keep).expanduser()), human, cfg.get("checkbox_columns", ["読んだ"]))

    data = collect(source, branches)
    summaries = load_json(summaries_path, {})
    if args.fetch:
        import fetch  # noqa: PLC0415  ネットに出るのはここだけ
        cited = [k for k in data["works"] if k in data["cite"]]
        fetch.fetch_abstracts(cited, cache / "abstracts.json")
        fetch.fetch_csl(list(data["works"]), cache / "csl_raw.json")
    abstracts = load_json(cache / "abstracts.json", {})
    csl_raw = load_json(cache / "csl_raw.json", {})

    claims = collect_claims(source, branches, data["idmap"])
    labels = card_labels(source, branches)
    rows = build_rows(data, claims, summaries, labels, cfg)

    rekey = parse_rekey(args.rekey or [])
    rj = {"joined": 0, "orphans": 0}
    if kept is not None:
        rj = rejoin(rows, kept, human, rekey, args.keep_orphans)
    else:
        for r in rows:
            for c in human:
                r[c] = ""

    # 一時のフォルダに全部作ってから出力先へ移す。途中で止まったら出力先は前の回のまま（新旧が混ざらない）
    out.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".refdb-", dir=out))
    try:
        name = f"GSE文献DB_{today}"
        write_csv(rows, human, stage / f"{name}.csv")
        n = sum(1 for r in rows if r["状態"] != ORPHAN_STATE)
        sub = f"{len(branches)} 枝の docs/references.md を key でまとめた {n} 件・{today} 時点の写し"
        write_page(rows, data, summaries, labels, cfg, sub, stage / f"{name}.html")
        items, csl_counts = build_csl(rows, csl_raw, summaries)
        csl_path = stage / f"{name}.csl.json"
        csl_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        bib = {} if args.no_bib else write_bib(csl_path, stage / name)
        missing = missing_summaries(rows, data, summaries, abstracts)
        (stage / "missing_summaries.json").write_text(json.dumps(missing, ensure_ascii=False, indent=1), encoding="utf-8")
        formula_cells = sum(1 for r in rows for c in COLUMNS + human if str(r.get(c, ""))[:1] in FORMULA_LEAD)
        manifest = {
            "date": today,
            "branches": {b: source.commit(b) for b in branches},
            "works": n,
            "card_cited": sum(1 for r in rows if r["_cards"]),
            "summaries": sum(1 for r in rows if r["key"] in summaries),
            "claims_works": sum(1 for r in rows if r["_cc"]),
            "claims_lines": sum(len(r["_cc"]) for r in rows),
            "collided_ids": len(data["collided"]),
            "missing_summaries": len(missing),
            "formula_like_cells": formula_cells,
            "skipped_lines": data["skipped"],
            **csl_counts, "bib": bib, "kept": rj,
        }
        # 成果物の SHA-256 を manifest に持たせ、manifest は最後に移す。
        # 移す段で止まっても、manifest が古いままか、ハッシュが合わないことで分かる
        if not args.no_xlsx:
            bibtex = "" if args.no_bib else (stage / f"{name}_bibtex.bib").read_text(encoding="utf-8")
            manifest.update(write_xlsx(rows, human, items, bibtex, manifest, stage / f"{name}.xlsx"))
        manifest["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.iterdir())}
        (stage / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        produced = {p.name for p in stage.iterdir()}
        for old in output_names(name):
            if old not in produced and (out / old).exists():
                (out / old).unlink()  # 今回作らなかったもの（--no-bib の .bib）を前の回から残さない
        for p in sorted(stage.iterdir(), key=lambda p: (p.name == "manifest.json", p.name)):
            p.replace(out / p.name)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    delivered = deliver(out, name, Path(args.deliver).expanduser()) if args.deliver else []

    print(f"出力: {out}")
    if delivered:
        print(f"渡した: {args.deliver} に {'・'.join(delivered)}")
    print(f"文献 {n}・要約 {manifest['summaries']}・カードでの記述 {manifest['claims_works']} 件"
          f"（{manifest['claims_lines']} 行）・番号の衝突 {manifest['collided_ids']}・要約が無いカード引用 {len(missing)}")
    print(f"CSL: キャッシュから {csl_counts['csl_from_cache']}・最小限で作った {csl_counts['csl_minimal']}"
          + (f"・.bib {bib}" if bib else ""))
    if args.keep:
        print(f"読んだ・メモ: {rj['joined']} 件を結び直した・正本に無い {rj['orphans']} 件")
    if formula_cells:
        print(f"注意: = + - @ で始まるセルが {formula_cells} 個ある。シートで数式として読まれないか確かめる", file=sys.stderr)
    if data["skipped"]:
        print(f"読めなかった行 {len(data['skipped'])} 件（manifest.json の skipped_lines）", file=sys.stderr)
    return 0


def verify(out: Path) -> list[str]:
    """出力先の成果物が manifest.json の SHA-256 と合うか。合わないもの・無いものを返す（空なら揃っている）。"""
    mp = out / "manifest.json"
    if not mp.exists():
        return ["manifest.json が無い"]
    hashes = json.loads(mp.read_text(encoding="utf-8")).get("sha256") or {}
    if not hashes:
        return ["manifest.json に sha256 が無い"]
    bad = []
    for name, h in sorted(hashes.items()):
        p = out / name
        if not p.exists():
            bad.append(f"{name} が無い")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(f"{name} が manifest と合わない（前の回のものが残っている）")
    return bad


def main(argv=None, source=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["--verify"]:
        if len(argv) != 2:
            print("使い方: build.py --verify <出力先>", file=sys.stderr)
            return 2
        bad = verify(Path(argv[1]).expanduser())
        for b in bad:
            print("不一致: " + b, file=sys.stderr)
        print("揃っている" if not bad else f"{len(bad)} 件が合わない。回し直す")
        return 0 if not bad else 1
    try:
        return run(parse_args(argv), source=source)
    except OrphanError as e:
        print(f"止めた: {e}。--rekey 旧=新 で対応を渡すか、--keep-orphans で末尾に残す。何も書いていない。", file=sys.stderr)
        for o in e.orphans:
            print("  " + json.dumps(o, ensure_ascii=False), file=sys.stderr)
        return EXIT_ORPHANS
    except KeepConflict as e:
        print(f"止めた: {e}。シートを直してから読み直す。何も書いていない。", file=sys.stderr)
        for x in e.problems:
            print("  " + x, file=sys.stderr)
        return EXIT_ORPHANS
    except (RuntimeError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 2


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="文献 DB を作り直す（scripts/refdb/README.md）")
    p.add_argument("--config", default=str(HERE / "config.json"))
    p.add_argument("--branches", help="読む枝をカンマ区切りで（設定を上書き）")
    p.add_argument("--pin", action="append", metavar="枝=commit", help="その枝を決めた commit で読む（何度でも）")
    p.add_argument("--out", help="出力先（既定 ~/.cache/gse-refdb/out/<日付>/）")
    p.add_argument("--date", help="ファイル名と manifest の日付（既定は今日）")
    p.add_argument("--keep", help="シートの「一覧」（CSV か get_values の JSON）。読んだ・メモを key で結び直す")
    p.add_argument("--rekey", action="append", metavar="旧=新", help="消えた key の付け替え（何度でも）")
    p.add_argument("--keep-orphans", action="store_true", help="正本に無い key のメモを末尾に残す")
    p.add_argument("--fetch", action="store_true", help="抄録と CSL を足りない分だけ取りに行く（ネットに出る）")
    p.add_argument("--cache", default=str(DEFAULT_CACHE))
    p.add_argument("--summaries", default=str(REPO / "docs" / "literature" / "refdb" / "summaries.json"))
    p.add_argument("--no-bib", action="store_true", help=".bib を作らない（pandoc が無いとき）")
    p.add_argument("--no-xlsx", action="store_true", help=".xlsx を作らない（openpyxl が無いとき）")
    p.add_argument("--deliver", help="xlsx と BibTeX を日付なしの名前（GSE文献DB.xlsx・GSE文献DB.bib）で写す先（Drive の「文献DB」）")
    return p.parse_args(argv)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main())
