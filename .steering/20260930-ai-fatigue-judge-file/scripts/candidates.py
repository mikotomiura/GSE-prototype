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

CANDIDATES = S02 + S02X + S12 + S04 + S04X + S05 + NEW
