"""判定者用ファイルの『追加候補』のデータ（design.md「判定者用ファイル」2・decisions.md 判断 2・7）。

★ ここに要点の文を書かない。要点は judge_xlsx.py が事実のファイルの該当の行・節から機械的に抜き出す。
  ここに書くのは「どの事実のファイルの、どの節の、どの行（または節）か」の目印と、DOI・題名の出どころだけ。
★ 判定の語・評価の語を書かない（ここの文字列は判定者用ファイルに出ないが、出る要点・表記は check_judge_xlsx.py が確かめる）。

各候補:
  cid   : 候補番号（判定者用ファイルの行の鍵。変えない・使い回さない）
  refs  : [(事実のファイル, 節の見出しの先頭, 行の目印)]。行の目印が "### #n " で始まるときは S-02 の節（箇条書き）。
          それ以外は、その節の表の中で目印を含む行がちょうど 1 行あること（judge_xlsx.py が確かめる）。
  doi   : None なら refs の最初の行から取る。与えるときは doi_from に出どころを書く。
"""

PREV = "../20260929-ai-fatigue-surveys"

S02 = [dict(cid=f"S02-{n:02d}", refs=[(f"{PREV}/survey-S-02.md", "§2 #%d" % n, "### #%d " % n)],  # 2 つ目は出どころの表記だけに使う
            bib=(f"{PREV}/survey-S-02.md", "## 1.", "| %d |" % n)) for n in range(1, 12)]
# S-02 #8（Nobles 2026）の採択研究のうち、0 段目を通った一次研究（S-02 §7・decisions.md 判断 15・2026-09-30）
S02X = [
    dict(cid="S02-12", refs=[(f"{PREV}/survey-S-02.md", "## 7.", "Alkhatib ほか 2026")]),
    dict(cid="S02-13", refs=[(f"{PREV}/survey-S-02.md", "## 7.", "Liu 2026")]),
]

S12 = [
    dict(cid="S12-01", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "AI-Echo RCT"), (f"{PREV}/survey-S-04.md", "### 2.1", "AI-Echo RCT")]),
    dict(cid="S12-02", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "Effects of Long-Term Chatbot System Use")]),
    dict(cid="S12-03", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "Technostress and English Language Learning")]),
    dict(cid="S12-04", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "Crafting TBL Prompts")]),
    dict(cid="S12-05", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "ImNavi")]),
    dict(cid="S12-06", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "Wu Y. 2026")]),
    dict(cid="S12-07", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "Liu H ほか 2024"), (f"{PREV}/survey-S-04.md", "## 5.", "Liu ほか 2024")]),
    dict(cid="S12-08", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "Duong CD ほか 2024")]),
    dict(cid="S12-09", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "Hashem R ほか 2023")]),
]

_S04_ROWS = [
    ("### 2.1", ["Lukac ほか 2025", "Afshar ほか 2025", "小児の専門医の AI 記録支援", "2 種の記録支援の無作為化クロスオーバー",
                 "EHR 組み込みの生成 AI のカルテ要約", "放射線科の LLM チャットボット", "歯学生への AI のフィードバック",
                 "アルゴリズムの意思決定支援"]),
    ("### 2.2", ["教員の AI 教育技術", "アラビア語学習者の AI 支援", "大学の講師の ChatGPT の使い方", "児童の生成 AI の音声の読書",
                 "生成 AI の情報の伝え方", "従業員と AI の協働"]),
    ("### 2.3", ["Olson ほか 2025", "MGB・Emory", "アイオワの試行", "Garcia ほか 2024", "Shah ほか 2024", "小児の医療者の AI 記録支援",
                 "外科の外来の試行", "産婦人科の下書き返信", "遺伝カウンセラー", "家庭医療の研修医", "AI の記録支援と満足・会話",
                 "評価者のない試行", "北カリフォルニアの試行", "ハワイの試行", "繰り返しの調査", "前後の評価（AMIA 2026 の抄録）",
                 "入院の試行", "臨床薬剤師", "開発者の休憩の予定づけ"]),
]
S04 = []
for sec, marks in _S04_ROWS:
    for m in marks:
        S04.append(dict(cid=f"S04-{len(S04) + 1:02d}", refs=[(f"{PREV}/survey-S-04.md", sec, m)]))
# ★ 事実のファイルの行に DOI が無いものは、抽出の表（evidence/S-04 の TSV）の番号で与える
_S04_DOI = {
    "前後の評価（AMIA 2026 の抄録）": (None, "S-04 の抽出の表 R127（DOI の記録なし）"),
    "開発者の休憩の予定づけ": ("10.1109/ICARAI70085.2026.11635386", "S-04 の抽出の表 R250"),
}
for c in S04:
    mark = c["refs"][0][2]
    if mark in _S04_DOI:
        c["doi"], c["doi_from"] = _S04_DOI[mark]
        if mark.startswith("前後の評価"):
            c["tsv_id"] = "R127"

S04X = [
    dict(cid="S04-35", refs=[(f"{PREV}/survey-S-04.md", "## 5.", "皮膚科の生成 AI")],
         doi="10.3389/fmed.2026.1875075", doi_from="S-04 の抽出の表 R194"),
    dict(cid="S04-36", refs=[(f"{PREV}/survey-S-04.md", "## 5.", "Gallup のパネル")],
         doi="10.65864/zpxksxfkfk", doi_from="S-04 の抽出の表 R262"),
    dict(cid="S04-37", refs=[(f"{PREV}/survey-S-04.md", "## 5.", "学習者の AI 疲労の SEM")],
         doi="10.3389/fpsyg.2026.1859401", doi_from="S-04 の抽出の表 R193"),
    dict(cid="S04-38", refs=[(f"{PREV}/survey-S-04.md", "## 5.", "インドネシアの 5 万人")],
         doi="10.62712/juktisi.v5i2.1366", doi_from="S-04 の抽出の表 R239"),
]

S05 = [dict(cid=f"S05-{i + 1:02d}", refs=[(f"{PREV}/survey-S-05.md", "## 6.", m)]) for i, m in enumerate([
    "LLM の会話エージェントと受動的疲労", "Chatting with AI", "AI 支援の橋梁点検", "意思決定支援と知識の慢心", "自律エージェントとの慢心の測定",
    "周術期の引き継ぎの AI 記録支援", "胸部 X 線の優先づけの AI", "会計の AI の作業圧力と情動の鈍麻", "専門職の AI の利用の面接"])]

# 本タスクのサーヴェイ（S-15・S-14・S-13）の候補。行の目印は DOI（節の中で一意）。
# ★ 事実の表（§2・§3）の一次研究のうち、AI・機械学習の系のものだけ（decisions.md 判断 2 (b)）。
def _new(prefix, path, sec, dois, start=1):
    out = []
    for i, d in enumerate(dois, start):
        c = dict(cid=f"{prefix}-{i:02d}", refs=[(path, sec, d)])
        if "(" in d:  # DOI_RE は括弧で止まるので、括弧を含む DOI は与える
            c["doi"], c["doi_from"] = d, "事実のファイルの表記"
        out.append(c)
    return out


S15_DOIS_2 = ["10.3390/ejihpe16090130", "10.1186/s40359-026-04911-w", "10.3389/fcomp.2026.1756441", "10.3791/69637",
              "10.3390/healthcare14142063", "10.47067/ramss.v8i1.458", "10.35814/asiimetrik.v8i2.9876",
              "10.31305/rrijm.2026.v11.n07.009", "10.3390/data11090215", "10.1155/hbe2/9977058", "10.1145/3706599.3719875"]
S15_DOIS_3 = ["10.23887/ijee.v10i2.115254", "10.1002/nse2.70003", "10.37859/ijetl.v1i1.10836",
              "10.37497/rev.artif.intell.educ.v7ii.1413", "10.63056/academia.5.3(a).2026.1672", "10.5539/hes.v16n2p430"]
S14_DOIS_2 = ["10.1016/j.actpsy.2026.107428", "10.3390/bs15040401", "10.3389/fpsyg.2026.1828689", "10.3389/fpubh.2026.1695066",
              "10.3390/healthcare14080996", "10.1038/s41598-026-47683-4", "10.1016/j.actpsy.2026.107517", "10.1016/j.actpsy.2025.105487",
              "10.1016/j.actpsy.2025.105650", "10.3390/ijerph20065147", "10.3389/fpubh.2024.1449561", "10.1016/j.acra.2026.03.037",
              "10.1108/ijoa-09-2024-4847", "10.1108/IJCHM-07-2020-0789", "10.1109/AIMV66517.2025.11203345", "10.1108/md-08-2024-1820",
              "10.3390/su172210338", "10.55214/25768484.v9i6.8184", "10.1080/08824096.2025.2578439", "10.1177/21582440261462225",
              "10.1111/1744-7941.70072", "10.3389/fpsyg.2026.1943409", "10.1108/ijchm-02-2023-0240", "10.24250/jpe/si/2026/gsv/lrm/",
              "10.1177/21582440251400532", "10.1109/IC4e69618.2026.11631530", "10.31306/s.67.2.4", "10.62836/emi.v5i2.0014",
              "10.1108/ijwhm-09-2025-0252", "10.21203/rs.3.rs-10628079/v1"]
S14_DOIS_3 = ["10.1177/10482911261474923", "10.69889/sr7m0r83", "10.1108/he-06-2025-0101", "10.29140/9780648184485-17"]

S13_DOIS_2 = ["10.3389/fpsyg.2026.1901039", "10.1016/j.actpsy.2026.107840", "10.1155/jonm/4386800", "10.1186/s40359-026-04706-z",
              "10.20944/preprints202410.0106.v1", "10.55493/5007.v16i2.5810"]
S13_DOIS_3 = ["10.3389/fpubh.2026.1866364", "10.1016/j.outlook.2025.102484", "10.1186/s12913-025-13876-2", "10.34140/bjbv8n1-016",
              "10.61838/kman.hn.3.3.12", "10.2196/45032", "10.26756/th.2023.814", "10.54536/ajet.v5i1.6407", "10.38124/ijisrt/25oct658"]

NEW = (_new("S15", "survey-S-15.md", "## 2.", S15_DOIS_2)
       + _new("S15", "survey-S-15.md", "## 3.", S15_DOIS_3, start=len(S15_DOIS_2) + 1)
       + _new("S14", "survey-S-14.md", "## 2.", S14_DOIS_2)
       + _new("S14", "survey-S-14.md", "## 3.", S14_DOIS_3, start=len(S14_DOIS_2) + 1)
       + _new("S13", "survey-S-13.md", "## 2.", S13_DOIS_2)
       + _new("S13", "survey-S-13.md", "## 3.", S13_DOIS_3, start=len(S13_DOIS_2) + 1))

# ★ S-13 §2 の Gallup のパネルは既存の追加候補 S04-36 と同じ研究（同じ DOI）→ 出どころを足す（行は増やさない）
for _c in S04X:
    if _c["cid"] == "S04-36":
        _c["refs"].append(("survey-S-13.md", "## 2.", "10.65864/zpxksxfkfk"))

# ★ レビュー（code-reviewer HIGH・decisions.md 判断 13）の後に足した候補:
#   各サーヴェイの「表に載せなかった」行・AI を燃え尽きの対策に使う介入のうち、論文が AI と書く一次研究はすべて足す。
#   外すのは AI でない系（範囲の決定 (b)・P）と一次研究でないものだけ（AI の見立て〈E1〜E3〉で候補を絞らない）。
S14_DOIS_4 = ["10.2196/85986", "10.1111/wvn.70003", "10.2196/54029", "10.3389/fdgth.2025.1665457"]
S14_DOIS_5 = ["10.1080/10447318.2024.2429889", "10.1109/IC4e69618.2026.11631611", "10.1109/iraset64571.2025.11008039",
              "10.34190/ecie.20.1.3863", "10.1007/s12144-026-09580-x", "10.47233/jsit.v5i3.3711"]
S15_DOIS_4 = ["10.1097/ajn.0000000000000364", "10.47672/ajdikm.2865", "10.61838/japes.254", "10.1007/s44163-026-01678-2",
              "10.18421/tem153-85", "10.54941/ahfe1007464"]
S13_DOIS_4 = ["10.21203/rs.3.rs-9540650/v1", "10.3389/fpsyg.2026.1792200", "10.22541/au.172114373.32212020/v1",
              "10.20944/preprints202407.2277.v1", "10.68159/j612488059"]
ADDED = (_new("S15", "survey-S-15.md", "## 4.", S15_DOIS_4, start=len(S15_DOIS_2) + len(S15_DOIS_3) + 1)
         + _new("S14", "survey-S-14.md", "## 4.", S14_DOIS_4, start=len(S14_DOIS_2) + len(S14_DOIS_3) + 1)
         + _new("S14", "survey-S-14.md", "## 5.", S14_DOIS_5, start=len(S14_DOIS_2) + len(S14_DOIS_3) + len(S14_DOIS_4) + 1)
         + _new("S13", "survey-S-13.md", "## 4.", S13_DOIS_4, start=len(S13_DOIS_2) + len(S13_DOIS_3) + 1))
# S-14 §4 の 2 件は前タスクの S-04 §4 と同じ研究 → 出どころを足す
for _c in ADDED:
    mark = _c["refs"][0][2]
    if mark == "10.2196/85986":
        _c["refs"].append((f"{PREV}/survey-S-04.md", "## 4.", "AI が選ぶ CBT のモバイル"))
    if mark == "10.1111/wvn.70003":
        _c["refs"].append((f"{PREV}/survey-S-04.md", "## 4.", "AI による看護師向けの個別の介入"))
# S-04 §4 の残りの AI の介入（事実のファイルに DOI が無いので、抽出の表の番号で与える）
ADDED += [
    dict(cid="S04-39", refs=[(f"{PREV}/survey-S-04.md", "## 4.", "Vitalk")],
         doi="10.1371/journal.pone.0303370", doi_from="S-04 の抽出の表 R042"),
    dict(cid="S04-40", refs=[(f"{PREV}/survey-S-04.md", "## 4.", "生成 AI 支援のマインドフル・セルフコンパッション")],
         doi="10.35510/jer.2026.48.2.5", doi_from="S-04 の抽出の表 R220"),
]
# ★ S-14 §2 の 1 行に 3 件の記録（同じ n・同じ割合）。1 行にまとめるのは E5 の判断にあたるので、記録ごとに候補を分ける
ADDED += [
    dict(cid="S14-51", refs=[("survey-S-14.md", "## 2.", "10.3390/bs15040401")],
         doi="10.21203/rs.3.rs-9220394/v1", doi_from="事実のファイルの同じ行の 2 件目の記録"),
    dict(cid="S14-52", refs=[("survey-S-14.md", "## 2.", "10.3390/bs15040401")],
         doi="10.70301/jour/sbs-jabr/2026/14/3/2", doi_from="事実のファイルの同じ行の 3 件目の記録"),
]
NEW += ADDED

# S-04 §3.1: 作業負荷・時間だけを測った比較研究（研究者の決定・decisions.md 判断 17・2026-09-30）。目印は各行の DOI。
# ★ R080 は §4 の行と同じ研究（既に候補）、R001 は論文が AI と書かない従来の自動化（範囲の決定 (b)）なので §3.1 に載っていない
_S04_S3_DOIS = [
    "10.64898/2025.12.06.25341757", "10.1016/j.annemergmed.2026.04.022", "10.1016/j.surge.2025.10.008", "10.1101/2024.08.12.24311883",
    "10.1101/2025.09.21.25336260", "10.1093/jamia/ocae304", "10.1055/a-2647-1142", "10.3233/shti250921", "10.1093/jamiaopen/ooaf013",
    "10.1016/j.msksp.2025.103333", "10.1055/a-2559-5791", "10.1093/jamiaopen/ooaf159", "10.1055/a-2576-0579", "10.1177/19322968231183436",
    "10.2196/89996", "10.2196/85580", "10.1002/jac5.70242", "10.1093/jamia/ocaf180", "10.1016/j.artd.2026.102095", "10.1055/a-2818-1706",
    "10.1038/s41746-026-02454-3", "10.2196/92364", "10.3233/shti260257", "10.64898/2026.02.19.26346634", "10.1007/s11606-026-10448-w",
    "10.1093/jamiaopen/ooag155", "10.5435/jaaos-d-24-01321", "10.1016/j.surg.2025.109700", "10.1016/j.jclinane.2026.112163", "10.2196/94140",
    "10.64898/2026.06.23.26355993", "10.7759/cureus.109247", "10.1001/jamanetworkopen.2026.15762", "10.1016/j.mcpdig.2024.100193",
]
S04Z = [dict(cid=f"S04-{41 + i:02d}", refs=[(f"{PREV}/survey-S-04.md", "### 3.1", d)]) for i, d in enumerate(_S04_S3_DOIS)]
# S-04 §3.2: 抽出の表の分類の外から同じ種類として足したもの（抄録で確かめた 12 件と種文献の Tai-Seale ほか 2024・判断 20）
_S04_S32_DOIS = [
    "10.1007/s43678-026-01141-2", "10.1016/j.medcli.2026.107541", "10.1136/bmjopen-2022-065477", "10.3390/healthcare13172118",
    "10.1101/2025.10.30.25339135", "10.64898/2026.01.12.26343538", "10.5435/jaaos-d-25-01245", "10.1200/op-25-00612",
    "10.1016/j.arth.2026.03.069", "10.1053/j.gastro.2025.12.020", "10.21203/rs.3.rs-9820618/v1", "10.2196/94450",
    "10.1001/jamanetworkopen.2024.6565",
]
S04Y = [dict(cid=f"S04-{41 + len(S04Z) + i:02d}", refs=[(f"{PREV}/survey-S-04.md", "### 3.2", d)]) for i, d in enumerate(_S04_S32_DOIS)]

# ★ 2026-09-30（../20260930-ai-fatigue-candidates-appraisal/decisions.md 判断 2・3・研究者の決定）:
#   追加候補に入っていなかった記録を足す。S-08 の一次研究（§5 の 1 件・§6 の 2 件）と、S-12 の記録に判断 13 の規則
#   （論文が AI と書く一次研究は AI の見立てで絞らない）を当てたもの。既存の cid は変えない（末尾に足す）。
S08N = [
    dict(cid="S08-01", refs=[(f"{PREV}/survey-S-08.md", "## 8.", "mind-mri-143-20259")]),
    dict(cid="S08-02", refs=[(f"{PREV}/survey-S-08.md", "## 8.", "arxiv.2609.00506")]),
    dict(cid="S08-03", refs=[(f"{PREV}/survey-S-08.md", "## 8.", "Anti-Design")]),
]
S12N = [
    dict(cid="S12-10", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "Omon")]),
    dict(cid="S12-11", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "s12912-024-02655-9")]),
    dict(cid="S12-12", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "s12912-024-02655-9")],
         doi="10.21203/rs.3.rs-4505331/v1", doi_from="事実のファイルの同じ行の 2 件目の記録（前刷り）"),
    dict(cid="S12-13", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "jsr.70144")]),
    dict(cid="S12-14", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "s25216560")]),
    dict(cid="S12-15", refs=[(f"{PREV}/survey-S-12.md", "### 4.2", "RAMS50514.2026.11424510")]),
    dict(cid="S12-16", refs=[(f"{PREV}/survey-S-12.md", "### 4.1", "ImNavi")],
         doi="10.1101/2024.08.05.24310603", doi_from="事実のファイルの同じ行の 2 件目の記録（medRxiv の版）"),
    dict(cid="S12-17", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "s25113324")]),
    dict(cid="S12-18", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "ijabc.18")]),
    dict(cid="S12-19", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "BRUCEE-LI")]),
    dict(cid="S12-20", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "isase.2026-C000057")]),
    dict(cid="S12-21", refs=[(f"{PREV}/survey-S-12.md", "### 3.3", "mededjapan.57.3_195")]),
    dict(cid="S12-22", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "descente.47.0_155")]),
    dict(cid="S12-23", refs=[(f"{PREV}/survey-S-12.md", "### 3.2", "AI音声解析")],
         doi=None, doi_from="DOI の記録なし（CiNii Research crid 1520867819566779776）", bib_key="crid:1520867819566779776"),
    dict(cid="S12-24", refs=[(f"{PREV}/survey-S-12.md", "### 4.3", "PPR268625")],
         doi=None, doi_from="DOI の記録なし（Europe PMC の前刷りの記録 PPR268625）", bib_key="PPR:PPR268625"),
    dict(cid="S12-25", refs=[(f"{PREV}/survey-S-12.md", "### 4.3", "jiot.2021.3067605")]),
]

CANDIDATES = S02 + S02X + S12 + S04 + S04X + S04Z + S04Y + S05 + NEW + S08N + S12N
