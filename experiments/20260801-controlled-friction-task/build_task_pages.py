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

    ⚠️★★★ **`re.S` が要る**（2026-09-01 に実測して見つけた）。
      ★ `.` は既定で改行に一致しないので、⚠️ **改行をまたぐ `**強調**` が変換されなかった**。
      → `pages/` 208 枚のうち **20 枚**で `**` が生のまま被験者の画面に出ていた。
      ⚠️ しかも見え方は「記号が残る」だけでは済まない ——
        `**A\nB**を述べています。3 本を踏まえて、**C**` のような並びだと
        ★ **1 つ目の `**` と 2 つ目の `**` が別のペアとして結ばれ、強調が接続部へ反転する**。
        → ⚠️ HI の要件（「食い違うこと」「1 つの主張」）から太字が外れていた。
      ★ 実際に壊れていたのは **`topic04_hi` と `topic05_hi` の 2 本**である
        （⚠️ 当初「HI 8 本すべて」と書いたが**誤り**だった。★ 検出に使った式
        `\*\*[^*]*\n[^*]*\*\*` が、**閉じ `**` と次の開き `**` の“隙間”にも当たって**
        いたため。正しくは `\*\*(.+?)\*\*` を `re.S` 付きで見て改行を含むかを問う）。
      ★ 割付は `topic04_HI` 10 ブロック ＋ `topic05_HI` 10 ブロック = **20 枚**で、
        実測した「`**` を含む 20 枚」と一致する。
      ⚠️ **2 本とも HI** なので、**HI 条件にだけ出る = 条件 × 体験の交絡**になりうる
        という帰結は変わらない。
    """
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped, flags=re.S)


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


#: ★ ボタンのラベルが「別のページへ行く」と読める語（2026-08-05・P-1 で実際に踏んだ）。
#   旧ラベル「消去して次のブロックへ」は押しても遷移せず、被験者がそこで止まった。
#   ⚠️ ★ **2026-08-08 に「開始する」をここから外し、下の START_* へ移した。**
#      「開始する」は *別のページへ行く* 約束ではなく *その場で始まる* 約束である。
#      ゲート（押すと課題と記入欄が出て 5 分が走り出す）を入れた時点で、
#      ここに残しておくと **正しく動くボタンを赤にし、遷移コードを足させてしまう**
#      （= §1 D-1「ページが勝手に進んではいけない」を破る直し方を促す）。
#      ★ 検査は弱めていない: 下の START 枝が「始めると名乗って始めない」を捕まえる。
NAV_PROMISE_WORDS = ("次のブロック", "次へ", "進む", "移動")

#: ★ `<button>` を実際に遷移させる書き方。**これが無いのに上の語を名乗ってはいけない。**
#   ⚠️ ★ `<a href>` を入れていた版は**誤りだった**（2026-08-05 の cross-review で判明）:
#      `<button>` は `<a href>` では遷移しない。ページのどこかに無関係なリンクが 1 本
#      増えただけで、約束を破っているボタンが**永久に検出できなくなる**（黙って緑になる）。
#      → ★ **判定はボタン単位で行う**。下の `_button_scope_for()` を参照。
NAV_IMPL_TOKENS = ("location.href", "location.assign", "location.replace",
                   "location =", "window.open", ".submit(", ".requestSubmit(")

#: ★ ボタンのラベルが「押すとその場で始まる」と読める語（2026-08-08 追加）。
#   ゲートのボタン（「課題を表示して始める」）がこれに当たる。
#   ⚠️ ★ **「始まる」の実体はタイマーが走り出すことである。** 課題を表示するだけで
#      5 分が動かないボタン（またはその逆）は、被験者の 5 分を静かに壊す。
#   ⚠️ ★ 旧版の失敗様式そのもの: `setTimeout` が**トップレベル**にあったため
#      「開いた瞬間に始まる」= ボタンの有無と無関係に走っていた（2026-08-08 に修正）。
START_PROMISE_WORDS = ("始める", "開始する", "スタート")

#: ★ その場で始める実装。★ タイマー起動と、隠していたものを出す印の両方を見る。
START_IMPL_TOKENS = ("setTimeout", "BLOCK_MS", "g1-started")


def _strip_html_comments(page: str) -> str:
    """⚠️ ★ コメントの散文を実装と読み違えない（この検査は文言を読む検査なので特に危ない）。

    生成ページでは `strip_comments()` が先に走るので通常は空振りするが、
    ★ **生テンプレートに対して直接呼ばれても正しく動く**ようにここでも落とす。
    """
    return re.sub(r"<!--.*?-->", "", page, flags=re.S)


def _button_scope_for(page: str, button_html: str, button_id: str | None) -> str:
    """★ そのボタンの実装が書かれうる場所**だけ**を集める。

    ⚠️ ページ全体を見てはいけない（無関係なコードで緑になってしまう）。
    見るのは 2 か所だけ:
      1. ボタンタグ自身（`onclick="..."`）
      2. **その id に言及している `<script>`**（このテンプレートの書き方）
    """
    scopes = [button_html]
    if button_id:
        for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", page, re.S):
            if button_id in m.group(1):
                scopes.append(m.group(1))
    return "\n".join(scopes)


def _function_body(page: str, header: str) -> str | None:
    """★ `header`（例: `function startBlock`）で始まる関数の**本体**を波括弧で切り出す。

    ⚠️ ★ **「行の前後関係」で中身を判定してはいけない**（2026-08-08 に実測で踏んだ）。
    `setTimeout` を関数の**後ろ**へ移した壊れ版が、
    「`function startBlock` より後ろにあるから中にある」という判定を**素通り**した。
    ★ 位置は包含の証拠にならない。→ 波括弧を数えて本体そのものを取る。

    ⚠️ 文字列リテラル中の波括弧は数えてしまうが、このテンプレートには無い（実測）。
    ★ 汎用パーサではなく、このテンプレート専用の回帰検査である。
    """
    i = page.find(header)
    if i < 0:
        return None
    j = page.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(page)):
        if page[k] == "{":
            depth += 1
        elif page[k] == "}":
            depth -= 1
            if depth == 0:
                return page[j:k + 1]
    return None


def promise_check(page: str) -> list[str]:
    """★ ボタンのラベルが、そのボタンが**実際にすること**を超えていないか。

    ⚠️ これは漏れ検査 (`leak_check`) ではなく **約束の検査**である。
    分けてあるのは、両者が壊れる理由が違うため
    （漏れ = 課題文の中身、約束 = テンプレート側の文言と実装のズレ）。

    ★ 「遷移を足して緑にする」のは**誤った直し方**である:
      - `protocol.md §1` D-1 = 1 ブロック 1 セッション。ブロック間には 1 分休憩と
        launcher 経由のアプリ再起動が入る（ページが勝手に進むと前ブロックの記録に混ざる）。
      - `preregistration.md §2.13` =「次のブロックのファイルを先に開かない」。
      → 正しい直し方は **ラベルを実装に合わせる**ことである。

    ★ 見る約束は 2 種類ある（2026-08-08 に 2 種目を足した）:
      1. **遷移**の約束（「次へ」等） → `NAV_*`。正しい直し方はラベルを直すこと。
      2. **その場で始まる**約束（「始める」等） → `START_*`。
         ⚠️ ★ こちらは逆で、**実装の側が正しい**ことのほうが多い。
         2026-08-08 まで `setTimeout` がトップレベルにあり、ボタンが無いのに
         「開いた瞬間に 5 分が始まる」状態だった。★ この枝は
         「始めると名乗るボタンが本当にタイマーを起こすか」を見る。

    ⚠️ ★ **この検査の限界**（広げすぎると誤爆するので、あえて狭くしてある）:
      - 対象は `<button>` と `<input type=button|submit>` の 2 つだけ。
        `<a>` をボタンに見せる書き方は見ていない（このテンプレートでは使っていない）。
      - 判定は `NAV_IMPL_TOKENS` / `START_IMPL_TOKENS` の**文字列一致**であり、構文解析ではない。
      - ⚠️ ★ スコープは「その id に言及する `<script>` 全体」なので、
        **同じ script 内に別目的のタイマーがあれば通ってしまう**（粗い）。
        ★ それでも「ラベルだけあって実装がまったく無い」型は確実に捕まえる。
      → ★ **このテンプレート専用の回帰検査**である。記入欄をアプリ側へ移すなど
        ページの作りが変わったら、ここも作り直す（`--selftest` が先に落ちるはず）。
    """
    bad: list[str] = []
    page = _strip_html_comments(page)

    controls: list[tuple[str, str, str | None]] = []
    for m in re.finditer(r"<button\b[^>]*>(.*?)</button>", page, re.S):
        tag = m.group(0)
        label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        id_m = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', tag)
        controls.append((label, tag, id_m.group(1) if id_m else None))
    for m in re.finditer(r'<input\b[^>]*\btype\s*=\s*["\']?(?:button|submit)["\']?[^>]*>',
                         page, re.S | re.I):
        tag = m.group(0)
        v_m = re.search(r'\bvalue\s*=\s*["\']([^"\']*)["\']', tag)
        id_m = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', tag)
        controls.append((v_m.group(1).strip() if v_m else "",
                         tag, id_m.group(1) if id_m else None))

    # (語の一覧, 実装の一覧, 何が無いか, 直し方)
    kinds = (
        (NAV_PROMISE_WORDS, NAV_IMPL_TOKENS, "遷移の実装が無い",
         "★ 遷移を足すのではなく**ラベルを直す**。§1 D-1 / §2.13"),
        (START_PROMISE_WORDS, START_IMPL_TOKENS, "5 分を始める実装が無い",
         "★ ラベルを直すか、押した時に課題を出してタイマーを起こすかのどちらかにする"),
    )
    for label, tag, ctrl_id in controls:
        scope = None
        for words, impls, missing, hint in kinds:
            promised = [w for w in words if w in label]
            if not promised:
                continue
            if scope is None:
                scope = _button_scope_for(page, tag, ctrl_id)
            if any(tok in scope for tok in impls):
                continue
            bad.append(
                f"ボタンのラベル {label!r} が {promised[0]!r} と約束しているのに、"
                f"このボタンには{missing}（{hint}）"
            )
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
        promises = promise_check(page)
        if promises:
            print(f"[NG] ブロック {block}: ラベルが実装より多くを約束している")
            for x in promises:
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

    # ⚠️★★★ **改行をまたぐ強調**（2026-09-01 追加）。
    #   ★ ここを 1 行だけで試していたせいで、`re.S` の欠落を **208 枚中 20 枚**に配ってしまった。
    #   ⚠️ 実材料（HI 8 本すべて）が改行をまたぐ書き方をしているのに、検査は 1 行しか見ていなかった。
    doc_ml = {"meta": {}, "sections": [("教示", "下の資料は、**同じ問いに対して\n食い違うこと**を述べています。")]}
    page_ml = build_page(template, 1, doc_ml)
    if "<strong>同じ問いに対して\n食い違うこと</strong>" not in page_ml:
        fails.append("改行をまたぐ **強調** が変換されていない（re.S が要る）")
    # ★ 生成物に `**` が 1 つも残らないこと（⚠️ 記号が見えること自体が欠陥である）
    if "**" in page_ml:
        fails.append("改行をまたぐ強調の後に `**` が生で残っている")

    # ⚠️★★ **強調の反転**を捕まえる。★ `re.S` が無いと 1 つ目と 2 つ目の `**` が
    #   別のペアとして結ばれ、**強調が接続部へ移る**（＝ 記号が残るだけでは済まない）。
    doc_inv = {"meta": {}, "sections": [("教示", "**A\nB**を述べています。**C**にまとめてください。")]}
    page_inv = build_page(template, 1, doc_inv)
    if "<strong>を述べています。</strong>" in page_inv:
        fails.append("強調が接続部へ反転している（re.S の欠落）")
    if "<strong>C</strong>" not in page_inv:
        fails.append("2 つ目の強調が変換されていない")

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
                 'id="count"', "beforeunload", 'id="start"', "g1-started",
                 # ⚠️★ 「開始後は未入力でも閉じる前に警告する」ガード（2026-08-08 追加）。
                 #   ★ `"beforeunload"` があるだけでは足りない。**条件のほうが本体**である
                 #     （以前は未入力なら黙って閉じられ、残り時間ごと消えていた）。
                 "if (!started && pad.value.length === 0) return;"):
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

    # ★★ 約束の検査（2026-08-05 追加・P-1 で「押しても次へ行かない」を実際に踏んだ）
    doc_lo = parse_material(HERE / "materials" / "topic01_lo.md")
    page_lo = build_page(template, 2, doc_lo)
    if promise_check(page_lo):
        fails.append(f"★ 現行テンプレートが約束超過: {promise_check(page_lo)}")
    # ⚠️ 検査が空回りしていないか: 旧ラベルに戻したページは赤になるはず
    regressed = page_lo.replace(">本文を消去する<", ">消去して次のブロックへ<")
    if regressed == page_lo:
        fails.append("★ 空回り検査を組めない（テンプレートのボタン文言が想定と違う）")
    elif not promise_check(regressed):
        fails.append("★ promise_check が空回りしている（旧ラベルを検出しない）")
    # ⚠️★ **無関係な遷移コードで緑にならないこと**（2026-08-05 cross-review の HIGH 指摘）。
    #   判定はボタン単位なので、ページのどこかにリンクが増えても赤のままでなければならない。
    elif not promise_check(regressed.replace(
            "</footer>", '</footer><script>function other(){location.href="x.html";}</script>')):
        fails.append("★ promise_check がページ全体を見ている"
                     "（そのボタンと無関係な遷移コードで約束違反を見逃す）")
    # ⚠️★ コメントの散文を実装と読み違えないこと。
    #   ★ 注入先は**ボタンの内側**にする。外に置くとスコープ限定のほうが先に効いてしまい、
    #     この検査は**何を壊しても赤にならない**（＝あって無いのと同じ）。2026-08-05 に実測して直した。
    elif not promise_check(regressed.replace(
            "</button>", "<!-- location.href で進めてもよいが進めない --></button>")):
        fails.append("★ promise_check がコメントを実装と読み違えている")
    # ⚠️★ `<input type=button>` の枝も実際に効いていること
    #   （★ 2026-08-05 に「この枝を落としても selftest が緑のまま」だったので足した。
    #     ★ **検査を書いただけでは、その枝を検査したことにならない**）
    if not promise_check(page_lo.replace(
            "</footer>", '<input type="button" value="次のブロックへ"></footer>')):
        fails.append("★ promise_check が <input type=button> を見ていない")

    # ★★ 開始ゲート（2026-08-08 追加）— **開いただけでは何も始まらない**こと。
    #   ⚠️ ★ 旧版は `setTimeout` が**トップレベル**にあり、ファイルを開いた瞬間に 5 分が
    #      走り出していた。受付メールの「目を通しておいて構いません」と正面から食い違い、
    #      ★ **誰も気づかないまま配布物が出来上がっていた**（2026-08-08 に発見）。
    if 'id="start"' not in page_lo:
        fails.append("★ 開始ゲートのボタンが生成ページに無い")
    if "g1-started" not in page_lo:
        fails.append("★ 開始前後を切り替える印（g1-started）が生成ページに無い")
    # ★ 開始前に「課題文」と「記入欄」の**両方**が隠れていること。
    #   ⚠️ 片方だけでは意味が無い（記入欄が先に出ていればそこから打ち始められるし、
    #      課題文が先に出ていれば読む時間だけ 5 分の外に出る）。
    for rule in ("body:not(.g1-started) .task", "body:not(.g1-started) textarea"):
        if rule not in page_lo:
            fails.append(f"★ 開始前に隠す指定が無い: {rule!r}")
    # ⚠️★ タイマーの起動が**ボタンの中**にあること（トップレベルへ戻っていないこと）。
    #   ⚠️ ★ **前後関係で判定してはいけない**。2026-08-08 に、`setTimeout` を
    #      `function startBlock` の**後ろ**へ移した壊れ版を作って試したところ、
    #      「後ろにあるから中にある」という判定は**緑のまま通した**。
    #      → 波括弧で本体を切り出して、その中にあることを見る。
    body = _function_body(page_lo, "function startBlock")
    if body is None:
        fails.append("★ startBlock() が無い（タイマーがボタンの中に入っていない）")
    elif page_lo.count("setTimeout(timeIsUp") != 1:
        fails.append(
            f"★ 5 分タイマーの起動が {page_lo.count('setTimeout(timeIsUp')} か所ある"
            "（1 か所＝ startBlock() の中だけであること）"
        )
    elif "setTimeout(timeIsUp" not in body:
        fails.append("★ setTimeout(timeIsUp) が startBlock() の外にある（開いた瞬間に始まる）")
    # ⚠️★ START 枝が空回りしていないか: 「始める」と名乗るだけのボタンは赤になるはず。
    #   ★ id を付けない = スコープはタグ自身だけ → 実装が見つからない、という組み方にする。
    if not promise_check(page_lo.replace(
            "</footer>", '<button type="button">開始する</button></footer>')):
        fails.append("★ promise_check が「始めると名乗って始めない」ボタンを見ていない")

    # ★ 逆向き: そのボタン自身に遷移実装があるページは**緑**でなければならない（過検出でない）
    honest = page_lo.replace('<button id="clear" type="button">本文を消去する</button>',
                             '<button type="button" onclick="location.href=\'x.html\'">'
                             '次へ進む</button>')
    if promise_check(honest):
        fails.append("★ promise_check が過検出している（実装のあるボタンまで赤にする）")

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
