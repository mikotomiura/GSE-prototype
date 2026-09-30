"""S-09 の決定（decisions.md 判断 1）: DB の『尺度・理論』に貼れる理論の文献の xlsx を作る（design.md §4）。

★ 元の DB は書き換えない。元の DB の『文献DB』『研究情報』『書誌・出典』と同じ列名・同じ順の 3 シート＋『はじめに』。
★ 書誌（著者・題名・誌名・巻・号・頁・年・オンラインの日）は Crossref の 1 件の取得から機械で入れる（手で書かない）。
   Crossref の記録は抄録を除いた欄だけを evidence/theory/ に保存する（連絡先を送らない）。
★ 研究情報の要点は、S-09 の事実のファイル（../20260930-ai-fatigue-theory-and-usage/survey-S-09.md）の記述を短くしたもの。

使い方（このディレクトリで）:
  python theory_rows.py fetch --out theory/crossref_2026-10-01.json
  python theory_rows.py build --crossref theory/crossref_2026-10-01.json --out ../archive/AI_fatigue_theory_rows_2026-10-01_claude.xlsx [--copy-to DIR]
"""
import argparse
import hashlib
import html
import json
import re
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
PREV = os.path.join(STEER, "20260929-ai-fatigue-surveys", "evidence")
sys.path.insert(0, PREV)
from common import allowed_url, guarded_opener  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doi_guard import doi_path  # noqa: E402  ★ 判断 17: DOI の . と .. の区切りを拒む

DB_XLSX = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                       "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
DB_SHA = "48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0"  # judge_xlsx.py と同じ固定値
SHEETS = ["文献DB", "研究情報", "書誌・出典"]
CHECK_DATE = "2026-10-01"
UA = {"User-Agent": "protocol-theory-rows/0.1"}
ALLOWED = ["https://api.crossref.org/works/"]
OPENER = guarded_opener(ALLOWED)
KEEP = ["DOI", "type", "title", "container-title", "volume", "issue", "page", "article-number", "author",
        "published-print", "published-online", "issued", "publisher", "relation"]
GROUPS = ("疲労の仕組み", "自動化", "職場のストレス")

# ---- 行のデータ（id・DOI・群・関連 ID・研究情報の欄）。要点は survey-S-09.md の §2・§4 の記述を短くしたもの ----
NA = "該当なし（理論）"
UNK = "未確認"
ROWS = [
    dict(id="TH01", doi="10.1017/S0140525X12003196", group="疲労の仕組み", role="機会費用", related=["TH02"],
         design="理論（論文）", result="努力の不快さと成績の低下を、消耗する資源ではなく、実行機能を目の前の課題に使うことの機会費用（次に良い使い道）の信号として説明する。努力の感じは費用と便益の計算の出力とする。",
         limits="抄録の範囲の要点（本文は PMC に無料の版があるが読んでいない）。", abstract=True),
    dict(id="TH02", doi="10.1037/rev0000309", group="疲労の仕組み", role="機会費用の時間の定式化", related=["TH01"],
         design="理論（計算の分析）", result="認知的疲労と退屈を、時間を通じた機会費用を追う合理的な制御で説明する。主観の努力の感じを、資源の消耗ではなく機会費用の測度の現れとみる。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH03", doi="10.1016/S0301-0511(96)05223-4", group="疲労の仕組み", role="補償的制御", related=[],
         design="理論（認知・エネルギーの枠組み）", result="ストレスと高い作業負荷の下で、資源を足して遂行を守ると主観の努力と行動・生理の費用が増え、目標を下げれば費用なしに安定を保てるとする 2 段のモデル。主課題に低下が見えなくても潜在的な低下が現れうる。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH04", doi="10.1037/0022-3514.74.5.1252", group="疲労の仕組み", role="自己制御の強度モデルの原典",
         related=["TH05", "TH06", "TH07", "TH08", "TH09", "TH10", "TH11"],
         design="実験（4 本）", result="自己制御の行為の後に、別の課題での粘りが下がった（実験 1 など）。能動的な意志の力は限られた共通の資源に依るとする。",
         limits="★ 必ず追試・メタ分析（関連 ID の TH05〜TH09）と併記する。多施設の追試での効果はほぼ零か小さい。グルコース説への反証は TH10・TH11。", abstract=True),
    dict(id="TH05", doi="10.1177/1745691616652873", group="疲労の仕組み", role="強度モデルの多施設の追試", related=["TH04", "TH06", "TH07"],
         design="事前登録の多施設の追試（Registered Replication Report）", n=2141, n_note="k = 23・N = 2,141",
         result="自我消耗の効果は d = 0.04（95% CI −0.07〜0.15）で、信頼区間が 0 を含んだ。", limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH06", doi="10.1037/xge0000083", group="疲労の仕組み", role="強度モデルのメタ分析", related=["TH04", "TH05", "TH07"],
         design="メタ分析の一連の検定", result="実験室でよく使われる方法で測る限り、消耗の効果が実在する証拠はほとんど無いとする。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH07", doi="10.1177/0956797621989733", group="疲労の仕組み", role="強度モデルの多施設の検定", related=["TH04", "TH05", "TH06"],
         design="事前登録の多施設の検定", n=3531, n_note="k = 36・N = 3,531",
         result="確認の検定は有意でなく d = 0.06。ベイズのメタ分析では、データは帰無仮説の下で 4 倍起こりやすかった。探索の分析では d = 0.08 で有意で、疲労を多く報告した参加者で効果が大きかった。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH08", doi="10.1177/1948550619887702", group="疲労の仕組み", role="強度モデルの多施設の追試（小さな効果）", related=["TH04", "TH09"],
         design="事前登録の多施設の追試（12 施設）", n=1775, n_note="12 施設・N = 1,775",
         result="小さく有意な自我消耗の効果 d = 0.10。結果の課題で無作為に回答した可能性のある参加者を除くと d = 0.16。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH09", doi="10.1177/1088868318762183", group="疲労の仕組み", role="強度モデルの証拠の論証の分析", related=["TH04", "TH08"],
         design="論証の分析（総説）", result="数百の研究が出ていても、証拠は決着していないとする。", limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH10", doi="10.1177/0956797616654911", group="疲労の仕組み", role="グルコース説への反証", related=["TH04", "TH11"],
         design="p-curve 分析", result="グルコース説の実験の効果量は出版・報告の偏りの影響を受けている可能性があり、有意な結果の研究の中でも証拠の価値は弱いとする。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH11", doi="10.1027/1864-9335/a000376", group="疲労の仕組み", role="グルコース説への反証", related=["TH04", "TH10"],
         design="実験", result="血糖値が自己制御に影響する、または自己制御に影響される証拠は見つからなかった。", limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH12", doi="10.1111/psyp.12339", group="疲労の仕組み", role="関与の低下と、その戻り", related=["TH13"],
         design="実験（n-back 課題・主観・成績・P3・瞳孔径）", measure="主観の疲労・成績・P3 の振幅・瞳孔径",
         result="疲労と課題の時間が増えると成績・P3 の振幅・瞳孔径が下がり、2 時間の後に報酬を上げるとすべてが戻った。著者は課題からの離脱と精神的疲労の結びつきを支持すると解釈する。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH13", doi="10.1177/0956797620904990", group="疲労の仕組み", role="関与の低下と、その戻り", related=["TH12"],
         design="事前登録の参加者内の 4 研究・拡散モデル", n=686, n_note="4 研究の計 N = 686",
         result="負荷の高い課題の後、反応の慎重さは下がったが、情報処理の速さと抑制の制御は下がらなかった。努力の後に人は離脱し、さらに努力することへの関心が下がるとする。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH14", doi="10.1207/s15516709cog1202_4", group="疲労の仕組み", role="認知負荷理論の原典（処理の容量）", related=[],
         design="理論と実験", result="手段－目標分析による問題解決は処理の容量を多く使い、そのぶんスキーマの獲得に回せないとする。抄録に疲労の語は無い。",
         limits="学習の理論。3 群への割り当ては案（貼るときに研究者が決める）。", abstract=True),
    dict(id="TH15", doi="10.1201/b12791-3.1", group="自動化", role="能動的／受動的疲労の区別の原典", related=["TH16", "TH17"],
         design="理論（書籍の章）", result="疲労を、持続的な知覚運動の調整から生じる能動的疲労と、応答の要求がほぼ無い系の監視から生じる受動的疲労に分ける。受動的疲労は覚醒の維持と近い。",
         limits="抄録は OpenAlex の記録。", abstract=True),
    dict(id="TH16", doi="10.1037/a0034386", group="自動化", role="能動的と受動的の実験的な区別", related=["TH15", "TH17"],
         design="実験（運転シミュレータの 2 研究）", population="学部生", n_note="研究 1 N = 108・研究 2 N = 168（合計しない）",
         ai_env="完全な自動運転（シミュレータ）", measure="主観の状態・緊急時の制動と操舵の速さ（尺度の名は抄録の範囲で未確認）",
         result="横風で能動的疲労を、完全な自動運転で受動的疲労を誘発した。受動的疲労は課題への関与の大きな低下を伴い、研究 2 では受動的疲労だけが緊急時の反応を遅らせ、衝突の確率を上げた。",
         limits="抄録の範囲の要点（機関リポジトリに無料の版があるが読んでいない）。", abstract=True),
    dict(id="TH17", doi="10.1016/j.aap.2018.04.004", group="自動化", role="自動化と受動的疲労のまとめ", related=["TH15", "TH16"],
         design="総説（著者自身のシミュレーションの研究のまとめ）", ai_env="自動運転",
         result="能動的疲労は認知の能力の過負荷による状態、受動的疲労は過小負荷と単調さで生じ、関与と覚醒の低下を伴う。自動運転は受動的疲労の主観の症状と、手動への引き継ぎの後も続く覚醒の低下を生むとする。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH18", doi="10.1177/0018720810376055", group="自動化", role="自動化への慢心と自動化バイアスの統合", related=[],
         design="総説（統合のモデル）", ai_env="自動化・決定支援",
         result="自動化への慢心は複数の課題の負荷の下で注意の奪い合いから生じ、自動化バイアスは不完全な決定支援での見落としと誤った採用として現れる。両者を注意を中心に重なる現象の別の現れとする。抄録に疲労の語は無い。",
         limits="抄録の範囲の要点（注意の理論）。", abstract=True),
    dict(id="TH19", doi="10.1037/0021-9010.86.3.499", group="職場のストレス", role="JD-R の原著", related=["TH20", "TH22"],
         design="調査（3 つの職業群）", n=374, n_note="3 つの職業群の計 N = 374", measure="Oldenburg Burnout Inventory（消耗・離脱）",
         result="労働条件を仕事の要求と資源に分けた。仕事の要求は燃え尽きの消耗と、資源の欠けは離脱と主に関係した。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH20", doi="10.1108/02683940710733115", group="職場のストレス", role="JD-R の総説", related=["TH19"],
         design="総説", result="JD-R モデルの前提と研究の証拠をまとめ、要求－統制モデルと努力－報酬の不均衡モデルと比べる。否定と肯定の両方の指標を扱う。",
         limits="抄録の範囲の要点。", abstract=True),
    dict(id="TH21", doi="10.1037/0003-066X.44.3.513", group="職場のストレス", role="資源保存理論の原典", related=["TH22"],
         design="理論", result="抄録が取れず、本文は読んでいない。",
         limits="抄録が無料の情報源に無い。資源保存理論の原則は一次で確かめていない。", abstract=False),
    dict(id="TH22", doi="10.1146/annurev-orgpsych-032117-104640", group="職場のストレス", role="資源保存理論の総説", related=["TH21", "TH19"],
         design="総説", result="資源保存理論は燃え尽きから外傷的ストレスまでの領域で使われ、職場のストレスの JD-R モデルの基礎になっているとする。理論の原則と系は本文にあり、抄録には書かれていない。",
         limits="抄録の範囲の要点（本文は読んでいない）。", abstract=True),
    dict(id="TH23", doi="10.2753/MIS0742-1222240109", group="職場のストレス", role="テクノストレスの原著", related=["AF027"],
         design="調査（構造方程式モデル）", n_note="223 組織の利用者（人数は抄録の範囲で未確認）", ai_env="情報通信技術（AI に限らない）",
         result="テクノストレスは生産性と負に、役割ストレスと正に関係した。テクノストレスを生む要因を識別したとする。",
         limits="抄録の範囲の要点。元の DB の AF027（テクノストレスの尺度）と対。", abstract=True),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


# ---- Crossref の記録から値を作る（検査器も同じ関数を使わず、別に書いた関数で確かめる） ----
def _date(parts):
    dp = (parts or {}).get("date-parts") or [[]]
    return [int(x) for x in dp[0]] if dp and dp[0] else []


def _text(s):
    """Crossref の文字列の HTML の実体参照（&amp; など）とタグ（<i> など）を外す。"""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(s or ""))).strip()


def bib(m):
    au = m.get("author") or []
    names = ["{} {}".format(a.get("given", "").strip(), a.get("family", "").strip()).strip() or a.get("name", "")
             for a in au]
    online = _date(m.get("published-online"))
    printed = _date(m.get("published-print"))
    issued = _date(m.get("issued"))
    return {
        "巻号年": (printed or issued or [None])[0],
        "論文タイトル": _text((m.get("title") or [""])[0]),
        "著者（短縮表示）": (names[0] + (" et al." if len(names) > 1 else "")) if names else UNK,
        "掲載誌・媒体": _text((m.get("container-title") or [UNK])[0]),
        "DOI": m["DOI"].lower(),
        "公表区分": {"journal-article": "学術誌論文", "book-chapter": "書籍の章"}.get(m.get("type"), m.get("type")),
        "オンライン公開日": "-".join(f"{x:02d}" if i else str(x) for i, x in enumerate(online)) if len(online) == 3 else UNK,
        "巻号年月": f"{printed[0]}-{printed[1]:02d}" if len(printed) >= 2 else UNK,
        "著者リスト": "; ".join(names) if names else UNK,
        "巻": m.get("volume"),
        "号": m.get("issue"),
        "頁・論文番号": m.get("page") or m.get("article-number"),
    }


def fetch(out):
    if os.path.exists(out):
        sys.exit(f"既にある（上書きしない）: {out}")
    recs = {}
    for r in ROWS:
        u = "https://api.crossref.org/works/" + doi_path(r["doi"], safe="/()")
        if not allowed_url(u, ALLOWED):
            raise ValueError(u)
        with OPENER.open(urllib.request.Request(u, headers=UA), timeout=60) as resp:
            m = json.loads(resp.read().decode("utf-8"))["message"]
        recs[r["doi"].lower()] = {k: m[k] for k in KEEP if k in m}  # ★ 抄録の欄（abstract）は保存しない
        time.sleep(0.4)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=time.strftime("%Y-%m-%dT%H:%M:%S+09:00"), records=recs), f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("書誌", len(recs), out)


def headers():
    import openpyxl
    if sha256(DB_XLSX) != DB_SHA:
        sys.exit(f"元の DB の SHA-256 が固定値と違う: {DB_XLSX}")
    wb = openpyxl.load_workbook(DB_XLSX, read_only=True)
    return {s: [c for c in next(wb[s].iter_rows(min_row=4, max_row=4, values_only=True)) if c is not None] for s in SHEETS}


def _is_theory(design):
    """理論・総説・論証の分析は、対象集団と測定の欄を「該当なし（理論）」にする（標本を持たないため）。"""
    return any(w in design for w in ("理論", "総説", "論証"))


def sheet_values(crossref):
    """3 シートの行（列名 → 値）を返す。"""
    recs = crossref["records"]
    out = {s: [] for s in SHEETS}
    for r in ROWS:
        b = bib(recs[r["doi"].lower()])
        url = "https://doi.org/" + r["doi"].lower()
        level = "Crossref の書誌・抄録確認" if r["abstract"] else "Crossref の書誌確認（抄録なし）"
        rel = "・".join(r["related"]) or None
        first = b["著者リスト"].split("; ")[0] if b["著者リスト"] != UNK else UNK
        out["文献DB"].append({
            "ID": r["id"], "分類": "尺度・理論", "優先度": None, "巻号年": b["巻号年"], "論文タイトル": b["論文タイトル"],
            "著者（短縮表示）": b["著者（短縮表示）"], "掲載誌・媒体": b["掲載誌・媒体"], "DOI": b["DOI"], "公表区分": b["公表区分"],
            "確認レベル": level, "一次情報URL": url, "オンライン公開日": b["オンライン公開日"], "巻号年月": b["巻号年月"], "関連ID": rel})
        out["研究情報"].append({
            "ID": r["id"], "文献ラベル": f"{first} ({b['巻号年']})", "研究デザイン": r["design"],
            "対象集団": r.get("population", NA if _is_theory(r["design"]) else UNK),
            "N（単一値）": r.get("n"), "標本・研究数の注記": r.get("n_note"),
            "AI・利用環境": r.get("ai_env", "該当なし（AI に限らない理論）"), "測定尺度・指標": r.get("measure", NA if _is_theory(r["design"]) else UNK),
            "主要結果（日本語要約）": r["result"], "限界・要確認点": r["limits"],
            "レビューでの位置づけ": f"理論｜{r['group']}（{r['role']}）", "確認レベル": level, "一次情報URL": url})
        out["書誌・出典"].append({
            "ID": r["id"], "著者リスト": b["著者リスト"], "巻": b["巻"], "号": b["号"], "頁・論文番号": b["頁・論文番号"],
            "DOI": b["DOI"], "一次情報URL": url, "補助情報URL": None, "確認レベル": level,
            "版・訂正・書誌の注意": "AF 番号は研究者が貼るときに付ける（TH は仮の ID）。", "関連ID": rel,
            "検索・確認日": CHECK_DATE, "関連検索ID": "S-09"})
    return out


INTRO = [
    ["このファイル", "元の DB（AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx）の『尺度・理論』に貼るための、理論の文献の行（S-09 の決定・2026-09-30）。元の DB は書き換えていない。"],
    ["作った者", "AI（Claude）。書誌は Crossref の記録（2026-10-01 に 1 件ずつ取得）から機械で入れた。研究情報の要点は、S-09 のサーヴェイの事実のファイル（文献の抄録に書いてあること）を短くしたもの。"],
    ["シート", "『文献DB』『研究情報』『書誌・出典』は、元の DB の同じ名のシートと同じ列名・同じ順。行をそのまま元の DB の表の末尾に貼れる。"],
    ["ID", "TH01〜は仮の ID。AF 番号は研究者が貼るときに付ける（『関連ID』の TH も同じ番号に置き換える）。TH23 の関連 ID の AF027 は元の DB の行。"],
    ["理論の区分と 3 群", "「理論」の区分と 3 つの群（疲労の仕組み・自動化・職場のストレス）は、元の DB に列を足さずに持たせるため、『研究情報』の「レビューでの位置づけ」の先頭に「理論｜群（役割）」の形で書いた。列を足すかは研究者が貼るときに決める。群の割り当ては、S-09 の提案の表の「役割」からの案。"],
    ["自我消耗の原典の併記", "TH04（強度モデルの原典）は、追試・メタ分析（TH05〜TH09）と必ず併記する（原典だけを引くと誤読される）。関連 ID で結んだ。"],
    ["優先度", "空にした（元の DB の作成者の分類なので、研究者が付ける）。"],
    ["確認レベル", "「Crossref の書誌・抄録確認」＝書誌を Crossref で、要点を抄録で確かめた。TH21 は抄録が無料の情報源に無く、本文も読んでいない。"],
]


def build(crossref_path, out, copy_to=None):
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    if os.path.exists(out):
        sys.exit(f"既にある（上書きしない）: {out}")
    crossref = json.load(open(crossref_path, encoding="utf-8"))
    heads = headers()
    vals = sheet_values(crossref)
    wb = openpyxl.Workbook()
    font, bold = Font(name="Noto Sans CJK JP", size=10), Font(name="Noto Sans CJK JP", size=10, bold=True, color="FFFFFFFF")
    fill = PatternFill("solid", fgColor="FF0C786E")
    wrap = Alignment(wrap_text=True, vertical="top")
    ws = wb.active
    ws.title = "はじめに"
    ws.append(["理論の文献の貼れる行（S-09）", None])
    for row in INTRO:
        ws.append(row)
    for r in ws.iter_rows():
        for c in r:
            c.font, c.alignment = font, wrap
    ws["A1"].font = Font(name="Noto Sans CJK JP", size=12, bold=True)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 22, 110
    for s in SHEETS:
        w = wb.create_sheet(s)
        w.append(heads[s])
        for c in w[1]:
            c.font, c.fill, c.alignment = bold, fill, wrap
        for rec in vals[s]:
            w.append([rec[h] for h in heads[s]])
        for r in w.iter_rows(min_row=2):
            for c in r:
                c.font, c.alignment = font, wrap
                if isinstance(c.value, str) and c.value.startswith("="):
                    c.data_type = "s"  # 数式として保存しない
        for i, _h in enumerate(heads[s], 1):
            w.column_dimensions[openpyxl.utils.get_column_letter(i)].width = 18 if i > 1 else 8
        w.freeze_panes = "B2"
    # ★ 判断 17（security-checker L-3）: 一時ファイルは一意の名で作り、最後の置き場は排他的に作る（確かめた後にできた
    #   ファイルを上書きしない）
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(os.path.abspath(out)))
    os.close(fd)
    try:
        wb.save(tmp)
        with open(tmp, "rb") as src, open(out, "xb") as dst:
            shutil.copyfileobj(src, dst)
    finally:
        os.remove(tmp)
    print("作った", out, sha256(out))
    if copy_to:
        dst = os.path.join(copy_to, os.path.basename(out))
        if os.path.exists(dst):
            sys.exit(f"写し先に既にある（上書きしない）: {dst}")
        with open(out, "rb") as src, open(dst, "xb") as f:  # 排他的に作る
            shutil.copyfileobj(src, f)
        print("写した", dst, sha256(dst))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "build"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--crossref")
    ap.add_argument("--copy-to")
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        fetch(a.out)
    else:
        build(a.crossref, a.out, a.copy_to)
    return 0


if __name__ == "__main__":
    sys.exit(main())
