"""Author 1's stage-2 judging sheet for batches b23 to b39 (the same input columns and choices as the database's
'段2・3'); the entries are copied to the database afterwards. Usage: make_judge_sheet.py <db.xlsx> <out.xlsx>"""
import csv, json, os, sys, datetime
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from openpyxl import Workbook, load_workbook
import make_trace_db as db
import trace_style as st
D = os.path.expanduser("~/Documents/TRACE"); data = f"{D}/data"; ft = f"{D}/fulltext"
recs = {r["id"]: r for r in db.load_records(data)}
meta = db.load(f"{data}/meta.json", {}); chrome = db.load(f"{data}/chrome_status.json", {})
ja = db.load(f"{data}/ja.json", {}); drive = db.load(f"{data}/drive_links.json", {})
batch = [(r["batch"], r["record_id"]) for r in csv.DictReader(open(os.path.expanduser("~/TRACE/screening/batches.csv")))
         if r["stage"] == "2" and "b23" <= r["batch"] <= "b39"]
INPUTS = ["判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"]
s2 = load_workbook(sys.argv[1])["段2・3"]
hdr = [c.value for c in s2[1]]
cur = {row[0].value: {h: row[hdr.index(h)].value for h in INPUTS} for row in s2.iter_rows(min_row=2)}
note = {"CS03205": "DB に「保留・E7」が入っていた（下の欄に引き継いだ）。段 2 の保留に付けられる理由は E6 か理由なし。",
        "CS02953": "10-21 の判定（保留・本文未確認）を引き継いだ。今回、全文が取れた。",
        "CS04223": "10-21 の判定（保留・E6）を引き継いだ。",
        "CS04589": "記録は予稿。予稿の PDF が開けず、予稿のページが示す最終版（JMIR Human Factors 2025）を全文として置いた。",
        "CS09148": "データセット。公開のファイルは表だけで、表を PDF に変えて置いた（元の .xlsx も同じフォルダにある）。"}
order = [i for _, i in batch]
bib_row = {i: n + 2 for n, i in enumerate(order)}
rows = []
for b, i in batch:
    r, c = recs[i], cur[i]
    f = db.fulltext_file(i, ft)
    stt = db.fulltext_status(i, meta, chrome, ft)[0]
    rows.append([b, i, r["title"], (ja.get(i) or {}).get("title_ja", ""), stt, f,
                 c["判定"] or "未判定", c["除外理由"] or "", c["中心"] or "未判定", c["読んだ範囲"] or "", c["根拠メモ"] or "",
                 note.get(i, "")])
n_ft = sum(r[4] == "あり" for r in rows)
wb = Workbook()
st.intro(wb.active, "段 2・3 の判定（束 b23〜b39）",
         f"作成 {datetime.date.today().isoformat()}・{len(rows)} 件（全文あり {n_ft}・全文なし {len(rows) - n_ft}）", [
    ("書き方", ["『判定』のシートの青い欄（判定・除外理由・中心・読んだ範囲・根拠メモ）に書く。選び肢は DB の『段2・3』と同じ。",
               "含める記録には中心も付ける。全文は「ファイル」のリンクから Google Drive で開く。ID を押すと『文献DB』のその記録の抄録へ飛ぶ。",
               "書き終えたら、この表の判定を DB の『段2・3』の同じ行へ写し、束ごとに書き出す。それまで DB の『段2・3』のこの 149 行には書かない。"]),
    ("全文の無い記録", ["無料の全文がない記録の決まりで判定する（E6 の保留・読んだ範囲は抄録か題名のみ）。"]),
    ("注意のある記録", [f"{k}: {v}" for k, v in note.items()]),
    ("判定基準", ["『判定基準』のシートは DB と同じ。"])])
ws = wb.create_sheet("判定")
cols = ["束", "ID", "論文タイトル", "題名（日本語・機械訳）", "全文", "ファイル"] + INPUTS + ["注意"]
st.table(ws, cols, [6, 10, 46, 34, 14, 14, 11, 10, 13, 11, 30, 34], rows, inputs=set(INPUTS),
         wrap={"論文タイトル", "題名（日本語・機械訳）", "根拠メモ", "注意"},
         links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[1]]}", v[1]),
                "ファイル": lambda v: db.drive_link(v[5], drive) if v[5] else None},
         tab="0D9488", height=lambda v: st.text_height((v[2], 46), (v[3], 34), (v[11], 34)))
st.choices(ws, cols, [("判定", db.STAGE_CHOICES), ("除外理由", db.CODE_CHOICES), ("中心", db.CENTRE_CHOICES),
                      ("読んだ範囲", db.READ_CHOICES)])
bib = wb.create_sheet("文献DB")
bcols = ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体", "DOI"]
brows = []
for i in order:
    r, m = recs[i], meta.get(i, {})
    doi = str(r.get("doi") or ""); doi = doi if doi.startswith("10.") else ""
    ab = (m.get("abstract") or "").strip()
    brows.append([i, r["title"], (ja.get(i) or {}).get("title_ja", ""),
                  ab or "（抄録なし: どの出どころにも見つからなかった。題名だけで判定する）",
                  (ja.get(i) or {}).get("abstract_ja", ""), m.get("authors", ""), r.get("year"), r.get("journal"), doi])
st.table(bib, bcols, [10, 36, 30, 70, 60, 24, 6, 22, 24], brows,
         wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体"},
         links={"DOI": lambda v: db.link_cell("https://doi.org/" + v[8] if v[8] else "", v[8])},
         tab="64748B", height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))
cr = wb.create_sheet("判定基準")
st.table(cr, ["項目", "内容"], [22, 120], [list(x) for x in db.CRITERIA], wrap={"内容"}, tab="64748B",
         height=lambda v: st.text_height((v[1], 120)))
wb.save(sys.argv[2]); print(sys.argv[2], len(rows), n_ft)
