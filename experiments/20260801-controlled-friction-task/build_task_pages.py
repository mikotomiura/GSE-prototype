#!/usr/bin/env python3
"""★ 課題文と記入欄を 1 画面にしたブロックページを生成する（研究者判断 2026-08-03）。

紙で 1 枚ずつ配る運用を置き換える。被験者は **URL（file://）を開いて、そのまま書く**。

## なぜブロックごとに 1 ファイルなのか（★ 先読み防止）

全題材を 1 つの HTML に入れると、**ソースを表示すれば全部読める**。
`protocol.md §2.3-2`（開始直前に 1 枚だけ渡す）が防いでいたのは正にそれである。
→ **1 ブロック = 1 ファイル**にし、実験者がブロック開始時にそのファイルだけを開く。

## 出力に条件を出さない

- ファイル名は `block01.html`（★ `hi` / `lo` / 題材 ID を出さない）。
- `<title>` も「G1 ブロック 3」まで。**条件も題材名も出さない**
  （タブに出ると被験者に見える。`make-handouts.sh` が .docx で front matter を落とすのと同じ理由）。

## 生成物は repo に置かない

`pages/` は `.gitignore` 済み。**割付（どのブロックがどの条件か）が入る**ので、
`blocks/*.json` と同じ扱いにする。

使い方:
    python3 build_task_pages.py --subject PILOT-win
    python3 build_task_pages.py --subject PILOT-mac
    python3 build_task_pages.py --selftest
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "writing-pad.html"
SLOT = "<!--G1_TASK_PANEL_SLOT-->"


def count_chars(text: str) -> int:
    """validate_materials.py の count_chars と同じ規則（空白・カテゴリ C を数えない）。"""
    return sum(1 for ch in text if not ch.isspace() and unicodedata.category(ch)[0] != "C")


def parse_material(path: pathlib.Path) -> dict:
    """課題文 .md を front matter とセクションに分解する。"""
    if not path.is_file():
        raise SystemExit(f"[NG] 課題文が無い: {path}")
    text = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    body = text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = text[m.end():]

    sections: list[tuple[str, str]] = []
    current = None
    buf: list[str] = []
    for line in body.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if current is not None:
                sections.append((current, "\n".join(buf).strip()))
            current = h.group(1)
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections.append((current, "\n".join(buf).strip()))
    return {"meta": meta, "sections": sections}


def md_inline(text: str) -> str:
    """★ 最小限のインライン変換。**強調** だけを見て、それ以外はエスケープする。

    課題文は自前で書いたものしか通さないので、汎用 Markdown 実装は要らない。
    ⚠️ エスケープしてから強調を戻す順序にする（HTML 注入を作らない）。
    """
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def render_task_panel(block: int, doc: dict) -> str:
    """課題文パネルの HTML。★ 条件（lo/hi）も題材 ID も出さない。"""
    parts = [f'<section class="task" aria-label="課題">']
    parts.append(f"<h2>ブロック {block}</h2>")
    for name, body in doc["sections"]:
        if not body:
            continue
        # ★ 「教示」だけは見出しを出さない（紙と同じ見え方にする）
        if name != "教示":
            parts.append(f"<h3>{html.escape(name)}</h3>")
        for para in re.split(r"\n\s*\n", body):
            para = para.strip()
            if not para:
                continue
            cls = ' class="fiction"' if para.startswith("※") else ""
            parts.append(f"<p{cls}>{md_inline(para)}</p>")
    parts.append("</section>")
    return "\n".join(parts)


def strip_comments(page: str) -> str:
    """★★ 生成ページからコメントを落とす（2026-08-04 に外部レビューで発見）。

    ⚠️ `writing-pad.html` の設計コメントには `bs_rate` / `FS-B` / `統制` /
       `preregistration.md §2.2 / §3.5` など **構成概念と判定の手がかり**が入っている。
       `§2.13` の論拠自体が「**ソースを表示すれば全部読める**」を脅威に挙げており、
       `§2.12` は仮説・判定基準・構成概念を**非開示**と凍結している。
    ⚠️ ★ **描画されないから安全、ではない。** 被験者は Ctrl+U でソースを見られる。

    ★ 落とすのは 3 種:
      1. HTML コメント `<!-- -->`
      2. CSS / JS のブロックコメント `/* */`
      3. JS の**行頭**行コメント `//`（⚠️ 行頭に限る。URL の `//` を壊さないため。
         実測: このテンプレートに `://` は 0 件、行頭以外の `//` も 0 件）
    """
    page = re.sub(r"<!--.*?-->", "", page, flags=re.S)
    page = re.sub(r"/\*.*?\*/", "", page, flags=re.S)
    page = re.sub(r"^[ \t]*//.*$", "", page, flags=re.M)
    # 連続する空行を 1 行に畳む（コメント除去で穴だらけになるため）
    return re.sub(r"\n{3,}", "\n\n", page)


def build_page(template: str, block: int, doc: dict) -> str:
    panel = render_task_panel(block, doc)
    # ★ window.G1_BLOCK を先に置く。writing-pad.html 側がこれを見てブロック番号を固定する。
    injected = f'<script>window.G1_BLOCK = "{block}";</script>\n{panel}'
    if SLOT not in template:
        raise SystemExit(
            f"[NG] {TEMPLATE.name} に {SLOT} が無い。"
            "★ テンプレートを書き換えたら、このスロットを残すこと"
        )
    page = template.replace(SLOT, injected)
    # ★ タブに条件・題材が出ないよう、タイトルはブロック番号までにする。
    page = page.replace("<title>G1 記入パッド</title>", f"<title>G1 ブロック {block}</title>")
    # ★★ HTML コメントを落とす（2026-08-04 に外部レビューで発見）。
    #   ⚠️ writing-pad.html の設計コメントには `bs_rate` / `FS-B` / `統制` /
    #      `preregistration.md §2.2 / §3.5` など **構成概念と判定の手がかり**が入っている。
    #      §2.13 の論拠自体が「**ソースを表示すれば全部読める**」を脅威に挙げており、
    #      §2.12 は仮説・判定基準・構成概念を**非開示**と凍結している。
    #   ⚠️ 描画されないから安全、ではない。被験者は Ctrl+U でソースを見られる。
    page = strip_comments(page)
    return page


def leak_check(page: str, doc: dict, block: int) -> list[str]:
    """★ 生成ページに、被験者へ出してはいけないものが混ざっていないか。

    `make-handouts.sh` の配布事故チェックと同じ思想（front matter / 条件名を出さない）。
    """
    bad: list[str] = []
    # ★★ 構成概念・判定の手がかりがソースに残っていないか（2026-08-04 追加）。
    #   ⚠️ 「描画されないから良い」ではない。**ソース表示で読める**（§2.13 の論拠そのもの）。
    for token in ("bs_rate", "FS-B", "preregistration", "統制", "判定基準", "仮説", "摩擦",
                  "positive control", "external_paste_chars"):
        if token in page:
            bad.append(f"非開示語がソースに残っている: {token!r}（§2.12 / §2.13）")
    meta = doc["meta"]
    for key in ("id", "version", "sources", "output_requirement_chars", "title"):
        if key in meta and f"{key}:" in page:
            bad.append(f"front matter の {key}: が残っている")
    for token in ("_hi", "_lo", "topic0", "materials/"):
        if token in page:
            bad.append(f"条件・題材が露出している: {token!r}")
    # ★ 題材名は**本文中には自然に出る**（教示に「図書館の開館時間を延ばすべきか」と書いてある）。
    #   紙で配っていたときも本文には出ていて、落としていたのは front matter だけである。
    #   ⚠️ 問題になるのは **<title>（ブラウザのタブに出る）** に題材名が入ることなので、そこだけ見る。
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    title_text = m.group(1) if m else ""
    if meta.get("title") and meta["title"] in title_text:
        bad.append(f"題材名 {meta['title']!r} が <title> に出ている（タブで被験者に見える）")
    return bad


def build_for_subject(subject: str, blocks_dir: pathlib.Path, out_root: pathlib.Path) -> int:
    spec_path = blocks_dir / f"{subject}.json"
    if not spec_path.is_file():
        raise SystemExit(
            f"[NG] 割付ファイルが無い: {spec_path}\n"
            f"     先に python3 assign.py ... --json > blocks/{subject}.json を作る"
        )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")

    out_dir = out_root / subject
    out_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for b in spec["blocks"]:
        block = int(b["block"])
        doc = parse_material(HERE / b["material"])
        page = build_page(template, block, doc)
        leaks = leak_check(page, doc, block)
        if leaks:
            print(f"[NG] ブロック {block}: 出してはいけないものが混ざっている")
            for x in leaks:
                print(f"  - {x}")
            return 1
        (out_dir / f"block{block:02d}.html").write_text(page, encoding="utf-8")
        made += 1

    print(f"[OK] {subject}: {made} ブロック分のページを生成した")
    print(f"     {out_dir}")
    print("  ★ ブロック開始時に block0N.html を 1 つだけ開く（先に次のファイルを開かない）。")
    print("  ⚠️ pages/ は .gitignore 済み。**コミットしない**（割付が入っている）。")
    return 0


def selftest() -> int:
    fails: list[str] = []
    template = TEMPLATE.read_text(encoding="utf-8")
    if SLOT not in template:
        fails.append(f"{TEMPLATE.name} に {SLOT} が無い")

    # ★ 実物の課題文で組み、条件が漏れないことを見る（hi / lo の両方）
    for name in ("topic01_hi.md", "topic01_lo.md", "copy.md"):
        doc = parse_material(HERE / "materials" / name)
        page = build_page(template, 3, doc)
        leaks = leak_check(page, doc, 3)
        if leaks:
            fails.append(f"{name}: 漏れ {leaks}")
        if "課題" not in page:
            fails.append(f"{name}: 課題パネルが入っていない")
        if 'window.G1_BLOCK = "3"' not in page:
            fails.append(f"{name}: G1_BLOCK が入っていない")
        # ★ 検査が空回りしていないか: 資料本文がちゃんと載っていること
        first_src = next((b for n, b in doc["sections"] if n.startswith(("資料", "原文"))), "")
        if first_src:
            head = html.escape(first_src.strip().splitlines()[0][:20])
            if head not in page:
                fails.append(f"{name}: 資料本文がページに載っていない（{head!r}）")

    # ★ HTML 注入が起きないこと（課題文は自前だが、エスケープ順序の回帰を見る）
    doc = {"meta": {}, "sections": [("教示", "<script>alert(1)</script> と **強調**")]}
    page = build_page(template, 1, doc)
    if "<script>alert(1)</script>" in page:
        fails.append("課題文中の HTML がエスケープされていない")
    if "<strong>強調</strong>" not in page:
        fails.append("**強調** が変換されていない")

    # ★★ HTML コメントが生成物に残っていないこと（2026-08-04 追加）
    doc_c = parse_material(HERE / "materials" / "topic01_lo.md")
    page_c = build_page(template, 2, doc_c)
    if "<!--" in page_c:
        fails.append("★ 生成ページに HTML コメントが残っている（ソース表示で読める）")
    for token in ("bs_rate", "FS-B", "preregistration", "統制"):
        if token in page_c:
            fails.append(f"★ 非開示語 {token!r} が生成ページに残っている")
    # ★ 落としすぎて壊れていないこと（機能が生きているか）
    for must in ('window.G1_BLOCK = "2"', "countChars", "user-select: none", 'id="pad"',
                 'id="count"', "beforeunload"):
        if must not in page_c:
            fails.append(f"★ コメント除去で機能が壊れた: {must!r} が消えている")
    # ★ その検査が空回りしていないか: 非開示語を残したページは赤になるはず
    if not leak_check(template.replace(SLOT, "x"), doc_c, 2):
        fails.append("★ leak_check が非開示語を検出しない（空回り）")

    # ★ leak_check 自体が空回りしていないか（わざと壊して赤くなるか）
    broken = {"meta": {"version": "hi", "title": "町立図書館の開館時間"},
              "sections": [("教示", "materials/topic01_hi.md を読む")]}
    if not leak_check(build_page(template, 1, broken), broken, 1):
        fails.append("★ leak_check が空回りしている（条件が露出しても検出しない）")

    if fails:
        print("[NG] build_task_pages.py selftest 失敗:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("[OK] build_task_pages.py --selftest 緑")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", help="被験者 ID（blocks/<ID>.json を読む）")
    ap.add_argument("--blocks-dir", default=str(HERE / "blocks"))
    ap.add_argument("--out", default=str(HERE / "pages"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.subject:
        ap.error("--subject か --selftest が要る")
        return 2
    return build_for_subject(a.subject, pathlib.Path(a.blocks_dir), pathlib.Path(a.out))


if __name__ == "__main__":
    sys.exit(main())
