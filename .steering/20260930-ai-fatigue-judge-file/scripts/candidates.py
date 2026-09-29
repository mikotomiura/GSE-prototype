"""判定者用ファイルの『追加候補』のデータ（design.md「判定者用ファイル」2・decisions.md 判断 2・7）。

★ ここに要点の文を書かない。要点は judge_xlsx.py が事実のファイルの該当の行・節から機械的に抜き出す。
  ここに書くのは「どの事実のファイルの、どの節の、どの行（または節）か」の目印と、DOI・題名の出どころだけ。
★ 判定の語・評価の語を書かない（check_judge_xlsx.py がこのファイルの文字列にも当てる）。

各候補:
  cid   : 候補番号（判定者用ファイルの行の鍵。変えない・使い回さない）
  refs  : [(事実のファイル, 節の見出しの先頭, 行の目印)]。行の目印が "### #n " で始まるときは S-02 の節（箇条書き）。
          それ以外は、その節の表の中で目印を含む行がちょうど 1 行あること（judge_xlsx.py が確かめる）。
  doi   : None なら refs の最初の行から取る。与えるときは doi_from に出どころを書く。
"""

PREV = "../20260929-ai-fatigue-surveys"

S02 = [dict(cid=f"S02-{n:02d}", refs=[(f"{PREV}/survey-S-02.md", "### #%d " % n, "### #%d " % n)],
            bib=(f"{PREV}/survey-S-02.md", "## 1.", "| %d |" % n)) for n in range(1, 12)]

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

# 本タスクのサーヴェイ（S-15・S-14・S-13）の候補は、事実のファイルができたら足す
NEW = []

CANDIDATES = S02 + S12 + S04 + S04X + S05 + NEW
