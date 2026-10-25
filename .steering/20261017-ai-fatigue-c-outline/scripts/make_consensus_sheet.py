"""The sheet on which author 1 and author 2 decide together the records of a run of batches: '段2' holds the
records differences --stage 2 names, '段3' the records both humans included whose centres they decide together
(the records differences --stage 3 will name among them). The entries ('最終', '最終の除外理由', '最終の中心',
'同じ標本の相手（E5）') are copied to the database afterwards. Author 1's values are the tool's (after the re-check)
with the notes of the database; author 2's are the tool's with the notes of the returned workbooks (h1, h2: their
records do not overlap, so b37 to b39, which mix the two, read both).
Usage: make_consensus_sheet.py <db.xlsx> <diff dir> <out.xlsx> <first batch> <last batch> <returned book.xlsx>...
(decision 103: b01 b22 with the centre-cleared h1; decision 111: b23 b39 with that h1 and the returned h2;
decision 112: both remade with author 1's proposal and author 2's answer to it before the finals)"""
import csv, glob, os, re, sys, argparse
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from openpyxl import Workbook, load_workbook
import c_screening as c
import make_trace_db as db
import trace_style as st

DB, DIFF, OUT, FIRST, LAST = sys.argv[1:6]
BOOKS = sys.argv[6:]
BATCHES = [f"b{n:02d}" for n in range(int(FIRST[1:]), int(LAST[1:]) + 1)]
SPAN = f"{BATCHES[0]}〜{BATCHES[-1]}"
STALE_E5 = {"S04-21", "CS05713"}   # withdrawn in author 1's re-check; cleared when the sheet is copied (decision 103)
a = argparse.Namespace(**{k: v.expanduser() for k, v in c.DEFAULTS.items()})
a.stage = 2
D = os.path.expanduser("~/Documents/TRACE"); data = f"{D}/data"; ft = f"{D}/fulltext"
recs = {r["id"]: r for r in db.load_records(data)}
meta = db.load(f"{data}/meta.json", {}); chrome = db.load(f"{data}/chrome_status.json", {})
ja = db.load(f"{data}/ja.json", {}); drive = db.load(f"{data}/drive_links.json", {})
DEC = {v: k for k, v in c.JA_DECISION.items() if v and v != "unresolved"}
CEN = {v: k for k, v in c.JA_CENTRE.items() if v and v != "unresolved"}


def sheet(path, name, cols):
    rows = list(load_workbook(path, read_only=True, data_only=True)[name].iter_rows(values_only=True))
    head = [str(x) if x is not None else "" for x in rows[0]]
    return {str(d["ID"]).strip(): {k: "" if d.get(k) is None else str(d[k]).strip() for k in cols}
            for d in (dict(zip(head, r)) for r in rows[1:]) if d.get("ID")}


VALS = ["判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"]
# author 1's proposal and author 2's answer to it (decision 112): the two decide together (GSRR-33); a proposal
# cannot be "合意できない", which only the two can reach
PROP_DECISION = "含める,除外,保留"
PROP_CENTRE = "中心-A,中心-B"
AGREE_CHOICES = "同意する,同意しない"
s1 = sheet(DB, "段2・3", VALS + ["最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）"])
s2 = {}
for path in BOOKS:
    got = sheet(path, "段2・3", VALS)
    if set(got) & set(s2):
        raise SystemExit(f"{path}: records already read from another workbook")
    s2.update(got)
A = c.author1_rows(a, 2)


def ja_vals(x2, x3):
    return [DEC[x2[0]], x2[1], CEN[x3[0]] if x3 else ""]


def check(i, who, got, x2, x3):
    """The sheet's values are the tool's: the notes are read from the sheet, the decisions from the tool."""
    want = ja_vals(x2, x3)
    have = [got["判定"], got["除外理由"], "" if got["中心"] in ("", "未判定") else got["中心"]]
    if have != want:
        raise SystemExit(f"{i}: {who}'s sheet {have} differs from the tool {want}")


rows2, rows3, n_tool = [], [], {}
for b in BATCHES:
    for i in c.batch_ids(a, 2, b):
        co = c.coauthor_round(a, i, 2, c.round_window(a, i, b))
        x2, y2 = c.value(A[i][1], 2), c.value(co, 2)
        x3, y3 = c.value(A[i][1], 3), c.value(co, 3)
        check(i, "author 1", s1[i], x2, x3)
        check(i, "author 2", s2[i], y2, y3)
        if any(s1[i][k] not in ("", "未判定") for k in ("最終", "最終の除外理由", "最終の中心")):
            raise SystemExit(f"{i}: the database has a '最終…' value already")
        # the partners author 1 withdrew in the re-check stay in the database until the copy clears them
        if s1[i]["同じ標本の相手（E5）"] and i not in STALE_E5:
            raise SystemExit(f"{i}: the database has a '同じ標本の相手（E5）' value already")
        f = db.fulltext_file(i, ft)
        base = [b, i, recs[i]["title"], (ja.get(i) or {}).get("title_ja", ""),
                db.fulltext_status(i, meta, chrome, ft)[0], f]
        if c.settled(2, x2, y2) is None:
            n_tool[b] = n_tool.get(b, 0) + 1
            if x2[0] == y2[0] == "exclude":
                note = "2 人とも除外で、除外理由が違う。『最終』は除外とし、『最終の除外理由』を決める。"
            elif x2[0] == y2[0] == "pending":
                note = "2 人とも理由のない保留（全文を読んでも決まらない）。"
            elif "include" in (x2[0], y2[0]):
                note = "一方が含めた。『最終』を含めるにするときは『最終の中心』も書く。"
            elif "E6" in (x2[1], y2[1]):
                note = ("一方が除外、他方が無料の全文が見つからない保留（E6）。全文があるかを確かめて決める。全文があれば全文で"
                        "決め、無ければ『最終』を保留、『最終の除外理由』を E6 とする。")
            else:
                note = "一方が除外、他方が理由のない保留。"
            if "E5" in (x2[1], y2[1]):
                note += ("除外・E5 にするときは『同じ標本の相手（E5）』に相手の記録の ID を書く。付録 6 の Q7 は、全文自身が"
                         "別の記録と同じ標本の重複・二次の報告だと述べるときだけ yes になる。")
            if i in STALE_E5:
                note += ("著者 1 は見直しで E5 を撤回したが、DB の『同じ標本の相手（E5）』に見直しの前の値が残っていた。"
                         "DB に写すときは、この表の値で置き換える。")
            rows2.append(base + ja_vals(x2, x3) + [s1[i]["根拠メモ"]] + ja_vals(y2, y3) + [s2[i]["根拠メモ"]]
                         + ["", "", "", "", "", ""] + ["未判定", "", "", "", note])
        elif x2[0] == y2[0] == "include" and not (x3 and y3 and x3[0] == y3[0] and x3[0] != "boundary"):
            note = "どちらかが境界（保留）。" if "boundary" in (x3[0], y3[0]) else "2 人の中心が違う。"
            rows3.append(base + [CEN[x3[0]], s1[i]["根拠メモ"], CEN[y3[0]], s2[i]["根拠メモ"], "", "", "", "", "", note])

# the records named here are those the tool named (differences --stage 2, run batch by batch into DIFF)
for b in BATCHES:
    s = open(f"{DIFF}/{b}.out", encoding="utf-8").read()
    named = re.findall(r"(\S+) \(author 1 \(", s)
    mine = [r[1] for r in rows2 if r[0] == b]
    if named != mine:
        raise SystemExit(f"{b}: the tool named {named}, the sheet has {mine}")

ids = [r[1] for r in rows2] + [r[1] for r in rows3]
bib_row = {i: n + 2 for n, i in enumerate(ids)}
wb = Workbook()
st.intro(wb.active, f"2 人で決める記録（段 2・3・束 {SPAN}）",
         f"段 2 は {len(rows2)} 件、段 3 は {len(rows3)} 件", [
    ("この表", ["2 人の判定が違う記録、または 2 人とも理由のない保留の記録を『段2』に、2 人とも含めて中心が違う記録、"
               "またはどちらかが境界（保留）の記録を『段3』に並べた。2 人で全文を見て決めた値を、青い欄に書く。",
               "書く順: 第一著者が全文を読み直して『著者 1 の案…』と『著者 1 の案の理由』を書く。共著者が案を読み、"
               "『著者 2 の同意』に同意する・同意しないを、同意しないときは『著者 2 のコメント』に別の値と理由を書く。"
               "そのあと 2 人で話して決めた値を『最終…』の欄に書く（同意した記録は案の値をそのまま書く）。",
               "ID を押すと『文献DB』のその記録の抄録へ飛ぶ。全文は「ファイル」のリンクから Google Drive で開く。",
               "書き終えた値は、第一著者が DB の『段2・3』の同じ行へ写し、束ごとに書き出す。"]),
    ("『段2』の書き方", ["『最終』に含める・除外・保留のどれかを書く。除外なら『最終の除外理由』も書く。",
                      "2 人とも除外で除外理由だけが違う記録は、『最終』を除外とし、『最終の除外理由』を決める。",
                      "理由が 2 つ以上当たるときは、付録 6 の順（E4、E1、E3、E2、E5、E7）で先のものを 1 つ選ぶ。",
                      "『最終』を含めるにした記録は、『最終の中心』（中心-A か中心-B）も書く。",
                      "除外・E5 にするときは『同じ標本の相手（E5）』に相手の記録の ID を書く。",
                      "全文を読んでも決まらない記録は保留（除外理由なし）とする。",
                      "一方が無料の全文が見つからない保留（E6）の記録は、全文があるかを確かめる。全文があれば全文で決め、"
                      "無ければ保留・E6 とする。",
                      "2 人で話しても合意できない記録は『最終』に「合意できない」と書き、ほかの『最終…』の欄は空のままにする。"]),
    ("『段2』の案と同意", ["『著者 1 の案』に含める・除外・保留のどれかを書き、除外なら『著者 1 の案の除外理由』、含めるなら"
                        "『著者 1 の案の中心』も書く。保留・E6 の案は『著者 1 の案の除外理由』を E6 とする。",
                        "除外・E5 の案は、相手の記録の ID を『著者 1 の案の理由』に書く。",
                        "『著者 2 の同意』は、案の値すべて（判定・除外理由・中心）に同意するときだけ同意するとする。"]),
    ("『段3』の書き方", ["『著者 1 の案の中心』と『著者 1 の案の理由』を書き、共著者が『著者 2 の同意』と"
                      "『著者 2 のコメント』を書く。",
                      "『最終の中心』に中心-A か中心-B を書く。2 人で話しても合意できない記録は「合意できない」と書く。"]),
    ("判定基準", ["『判定基準』のシートは DB と同じ。"])])

link = {"ID": lambda v: (f"#'文献DB'!A{bib_row[v[1]]}", v[1]),
        "ファイル": lambda v: db.drive_link(v[5], drive) if v[5] else None}
head = ["束", "ID", "論文タイトル", "題名（日本語・機械訳）", "全文", "ファイル"]
IN2 = ["最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）"]
PROP2 = ["著者 1 の案", "著者 1 の案の除外理由", "著者 1 の案の中心", "著者 1 の案の理由"]
AGREE = ["著者 2 の同意", "著者 2 のコメント"]
cols2 = head + ["著者 1 の判定", "著者 1 の除外理由", "著者 1 の中心", "著者 1 の根拠メモ",
                "著者 2 の判定", "著者 2 の除外理由", "著者 2 の中心", "著者 2 の根拠メモ"] + PROP2 + AGREE + IN2 + ["注意"]
ws = wb.create_sheet("段2")
st.table(ws, cols2, [6, 10, 40, 30, 12, 12, 10, 9, 11, 34, 10, 9, 11, 34, 11, 11, 11, 30, 11, 30, 11, 11, 11, 13, 30],
         rows2, inputs=set(PROP2 + AGREE + IN2),
         wrap={"論文タイトル", "題名（日本語・機械訳）", "著者 1 の根拠メモ", "著者 2 の根拠メモ", "著者 1 の案の理由",
               "著者 2 のコメント", "注意"},
         links=link, tab="0D9488",
         height=lambda v: st.text_height((v[2], 40), (v[3], 30), (v[9], 34), (v[13], 34), (v[24], 30)))
st.choices(ws, cols2, [("著者 1 の案", PROP_DECISION), ("著者 1 の案の除外理由", db.CODE_CHOICES),
                       ("著者 1 の案の中心", PROP_CENTRE), ("著者 2 の同意", AGREE_CHOICES),
                       ("最終", db.STAGE2_FINAL), ("最終の除外理由", db.CODE_CHOICES), ("最終の中心", db.CENTRE_FINAL)])
cols3 = head + ["著者 1 の中心", "著者 1 の根拠メモ", "著者 2 の中心", "著者 2 の根拠メモ",
                "著者 1 の案の中心", "著者 1 の案の理由"] + AGREE + ["最終の中心", "注意"]
ws = wb.create_sheet("段3")
st.table(ws, cols3, [6, 10, 40, 30, 12, 12, 11, 40, 11, 40, 11, 30, 11, 30, 12, 24], rows3,
         inputs={"著者 1 の案の中心", "著者 1 の案の理由", "著者 2 の同意", "著者 2 のコメント", "最終の中心"},
         wrap={"論文タイトル", "題名（日本語・機械訳）", "著者 1 の根拠メモ", "著者 2 の根拠メモ", "著者 1 の案の理由",
               "著者 2 のコメント", "注意"},
         links=link, tab="0D9488",
         height=lambda v: st.text_height((v[2], 40), (v[3], 30), (v[7], 40), (v[9], 40)))
st.choices(ws, cols3, [("著者 1 の案の中心", PROP_CENTRE), ("著者 2 の同意", AGREE_CHOICES),
                       ("最終の中心", db.CENTRE_FINAL)])
bib = wb.create_sheet("文献DB")
bcols = ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体", "DOI"]
brows = []
for i in ids:
    r, m = recs[i], meta.get(i, {})
    doi = str(r.get("doi") or ""); doi = doi if doi.startswith("10.") else ""
    ab = (m.get("abstract") or "").strip()
    brows.append([i, r["title"], (ja.get(i) or {}).get("title_ja", ""),
                  ab or "（抄録なし: どの出どころにも見つからなかった）",
                  (ja.get(i) or {}).get("abstract_ja", ""), m.get("authors", ""), r.get("year"), r.get("journal"), doi])
st.table(bib, bcols, [10, 36, 30, 70, 60, 24, 6, 22, 24], brows,
         wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体"},
         links={"DOI": lambda v: db.link_cell("https://doi.org/" + v[8] if v[8] else "", v[8])},
         tab="64748B", height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))
cr = wb.create_sheet("判定基準")
st.table(cr, ["項目", "内容"], [22, 120], [list(x) for x in db.CRITERIA], wrap={"内容"}, tab="64748B",
         height=lambda v: st.text_height((v[1], 120)))
wb.save(OUT)
print(OUT, "stage 2", len(rows2), "stage 3", len(rows3), {b: n_tool.get(b, 0) for b in BATCHES})
