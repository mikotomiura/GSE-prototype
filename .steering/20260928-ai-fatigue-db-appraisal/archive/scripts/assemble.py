"""評価データからシート定義（claude_eval.json）を組み立てる。"""
import json
import openpyxl
from data_b import R
from data_c import CHECKS, GSE_EXTRA, SG_BY_DOI, CHASE

import os
HERE = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.dirname(HERE)
SP = HERE
SRC = os.path.join(ARCH, "input", "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")

wb = openpyxl.load_workbook(SRC)
IDS = [wb["文献DB"].cell(r, 1).value for r in range(5, 39)]
TITLE = {wb["文献DB"].cell(r, 1).value: wb["文献DB"].cell(r, 5).value for r in range(5, 39)}
DBCLS = {wb["文献DB"].cell(r, 1).value: wb["文献DB"].cell(r, 2).value for r in range(5, 39)}
GPT = {wb["AI適格性評価"].cell(r, 1).value: wb["AI適格性評価"].cell(r, 4).value for r in range(5, 39)}
assert set(IDS) == set(R), set(IDS) ^ set(R)

S = []  # シート定義

# ---------- Claude適格性評価（元 AI適格性評価 と同じ列順＋右端に追加列） ----------
rows = []
for i in IDS:
    x = R[i]
    rows.append([i, TITLE[i], DBCLS[i], x["use"], x["scope"], x["level"], x["state"], x["next"], x["url"], x["loc"],
                 x["tier"], x["basis"], x["route"], GPT[i]])
S.append(dict(name="Claude適格性評価", title="Claude適格性評価｜34 件の用途・中心範囲の段・保留点",
    subtitle="元の『AI適格性評価』と同じ列順（A〜J）。右端に、中心範囲の段（プロトコル §2）・判定根拠・確認経路・GPT の用途判定を追加。中心候補は全文採択の確定ではない。AI の予備判定であり、人間 2 名の独立判定の代わりにならない。",
    headers=["ID", "論文タイトル", "元DB分類", "AI用途判定（Claude）", "概念の範囲", "原文確認レベル", "評価状態", "次の確認・作業",
             "主な参照URL", "原文箇所", "中心範囲の段", "判定根拠（プロトコル §2）", "確認経路", "GPTの用途判定（参考）"],
    widths=[9, 40, 13, 14, 32, 18, 18, 42, 36, 40, 14, 46, 32, 14], rows=rows))

# ---------- Claude方法論評価 ----------
rows = []
for i in IDS:
    x = R[i]
    rows.append([i, TITLE[i], x["strengths"], x["concerns"], x["cite"], x["need"], x["url"], x["url2"], x["loc"],
                 x["design"], x["n"], x["jbi"], x["diff"]])
S.append(dict(name="Claude方法論評価", title="Claude方法論評価｜強み・限界・引用できる範囲",
    subtitle="元の『AI方法論評価』と同じ列順（A〜I）。右端に、一次で確認した研究デザインと N、JBI／COSMIN の項目に準拠した AI 予備判定（Y=Yes, N=No, U=Unclear, NA=非該当・項目番号で表示）、既存 AI 評価との差分を追加。合計点・総合格付けは付けない。全文未取得は低品質を意味しない。",
    headers=["ID", "論文タイトル", "評価できる点", "懸念・限界", "引用に適した範囲", "必要な追加確認", "主な参照URL", "補助・訂正URL", "原文箇所",
             "研究デザイン（一次で確認）", "N（一次で確認・単位を明記）", "JBI・COSMIN 項目（AI予備）", "既存AI評価（GPT）との差分"],
    widths=[9, 36, 44, 56, 40, 32, 34, 30, 36, 34, 36, 34, 46], rows=rows))

# ---------- Claude領域別評価（中心候補のみ） ----------
central = [i for i in IDS if R[i]["tier"].startswith("中心")]
rows = []
for i in central:
    x, d = R[i], R[i]["dom"]
    rows.append([i, x["design"], d["sel"], d["mea"], d["tim"], d["con"], d["ana"], d["tra"], d["cite"], x["url"], d["summ"], x["tier"]])
S.append(dict(name="Claude領域別評価", title=f"Claude領域別評価｜中心候補 {len(central)} 件（中心-A と中心-B）",
    subtitle="元の『AI領域別評価』と同じ 6 領域。各セルの先頭に段階（低懸念／一部懸念／高懸念／判定不能／非該当）。段階の要約は ○=低懸念 △=一部懸念 ×=高懸念 ?=判定不能 －=非該当。正式な JBI・RoB・COSMIN の判定ではない。GPT 版の 12 件に、プロトコル §2 で中心-B とした AF019 を加えた。",
    headers=["ID", "研究デザイン", "選択・標本", "測定・構成概念", "時間順序・因果", "交絡・文脈", "解析・整合性", "透明性・版管理", "引用時の判断", "参照URL", "段階の要約", "中心範囲の段"],
    widths=[9, 30, 40, 42, 36, 34, 44, 38, 36, 34, 26, 13], rows=rows))

# ---------- Claude照合事項 ----------
S.append(dict(name="Claude照合事項", title=f"Claude照合事項｜既存 15 件の再照合と新規 {sum(1 for c in CHECKS if c[0].startswith('C'))} 件",
    subtitle="R-I01〜R-I15 は既存『AI照合事項』I01〜I15 を一次資料で再照合した結果。C01 以降は本評価で新たに見つけた事項。元 DB を自動修正・除外しない。不整合の指摘は研究不正の認定を意味しない。確認者の『メイン一次』はメインが一次資料を自分で開いて確かめたもの。",
    headers=["番号", "対象ID", "扱い", "論点", "確認された内容", "推奨する対応", "解釈の注意", "根拠URL", "原文箇所", "再照合の結果", "確認者"],
    widths=[8, 14, 16, 22, 70, 44, 40, 36, 28, 20, 30], rows=CHECKS))

# ---------- Claudeスクリーニング案（元 スクリーニング と同じ列構成） ----------
rows = []
for i in IDS:
    x = R[i]
    rows.append([i, TITLE[i], DBCLS[i], x["ta"], x["ft"], x["final"], x["reason"], x["ftstat"], x["qa"], x["memo"], x["tier"]])
S.append(dict(name="Claudeスクリーニング案", title="Claudeスクリーニング案｜題名・抄録段と全文段の AI 予備判定",
    subtitle="元の『スクリーニング』と同じ列構成・同じ選択肢（含める／除外／保留、全文確認: 未完了／進行中／完了／入手不可／対象外）。★ 判定者列の見出しは『Claude 予備判定』とし、人間の判定者欄とは区別する（元シートの判定者 1・2・最終判定は未判定のまま）。除外は証拠集合からの除外で、DB からは削除しない（E2・E4 は背景として保持）。『全文確認・抽出』の進行中は、AI が全文から抽出済みで人間の点検待ちの意味。",
    headers=["ID", "論文タイトル", "暫定分類", "Claude予備判定（題名・抄録段）", "Claude予備判定（全文段）", "Claude案（最終）", "除外理由", "全文確認・抽出", "品質評価（AI予備）", "自由記入", "中心範囲の段"],
    widths=[9, 44, 13, 16, 18, 14, 36, 14, 22, 50, 14], rows=rows))

# ---------- Claude×GPT比較 ----------
rows = []
for k, i in enumerate(IDS, 5):
    x = R[i]
    rows.append([i, TITLE[i], GPT[i], x["use"], x["tier"], f'=IF(C{k}=D{k},"一致","相違")', x["diff"], x["route"]])
S.append(dict(name="Claude×GPT比較", title="Claude×GPT比較｜用途判定と一次で食い違った点",
    subtitle="GPT（元ファイルの『AI適格性評価』）と Claude の用途判定の一致は、分類の一致だけを示す（品質評価の一致や κ ではない）。★ 2 つの AI の比較であり、人間の独立判定との比較（元の『AI判定比較』シート）は研究者が別に行う。",
    headers=["ID", "論文タイトル", "GPTの用途判定", "Claudeの用途判定", "Claudeの中心範囲の段", "用途判定の一致", "既存評価の記載で一次と食い違った点・補ったこと", "Claude の確認経路"],
    widths=[9, 40, 14, 14, 16, 12, 70, 34], rows=rows, formula_cols=[6]))

# ---------- GSE照合 ----------
rows = []
for i in IDS:
    g = R[i]["gse"]
    rows.append(["DB収録", i, TITLE[i], g["reg"], g["use"], g["check"], g["impl"], "なし（採否に使っていない）"])
for e in GSE_EXTRA:
    rows.append(["GSE由来の追加候補", e[0], e[1], e[2], e[3], e[4], e[5], "なし（追加の提案のみ）"])
S.append(dict(name="GSE照合", title="GSE照合｜GSE の既存調査・理論文書との突き合わせ",
    subtitle="GSE の docs/references.md（中央書誌）・生成的返権論 §6.3・理論ロードマップ §5.7・GR-H12・文献カード・2026-09-19 の体系的レビューと照合。★ プロトコル §7 により、GSE にとって有用かどうかで採否を変えていない（全行『採否への影響: なし』）。GSE で引用するときは citation-ssot で [Pn] を登録する。",
    headers=["区分", "ID・候補", "題名", "GSE の中央書誌（references.md）", "GSE 文書での使われ方", "一次照合で分かったこと（GSE 側の記述との一致・差）", "GSE にとっての含意", "採否への影響"],
    widths=[16, 22, 40, 26, 44, 56, 60, 18], rows=rows))

# ---------- 検索漏れ候補 ----------
an = json.load(open(os.path.join(ARCH, "evidence", "searchgap-analysis.json"), encoding="utf-8"))
hits = [c for c in an["candidates"] if c.get("prelim_hit") and not c.get("exclude_terms")]
assert {c['doi'] for c in hits} == set(SG_BY_DOI) and len(hits) == len(SG_BY_DOI), 'DOI の集合が判定と一致しない'
rows = []
for k, c in enumerate(hits, 1):
    j, code, cls, memo = SG_BY_DOI[c['doi']]
    q = ",".join(str(v) for v in c.get("queries", []))
    rows.append([k, f"API 検索（クエリ {q}）", c["doi"], c["title"], c.get("year") or "", c.get("type") or "", c.get("venue") or "", j, code, f"{cls}｜{memo}"])
for n, (doi, t, v, j, memo) in enumerate(CHASE, len(hits) + 1):
    rows.append([n, "AF017 の引用追跡", doi, t, 2024, "journal-article", v, j, "", memo])
n_sg = len(rows)
S.append(dict(name="検索漏れ候補", title=f"検索漏れ候補｜DB に無い {len(rows)} 件の題名段の予備判定",
    subtitle="OpenAlex と Crossref で 11 クエリ（各上位 50 件）を 2026-09-28 に実行。OpenAlex の検索件数（クエリ文字列どおりの自由語検索）: 『“AI fatigue”』158・『“AI-induced fatigue”』4・『“AI technostress” fatigue』21（Crossref の件数は関連度検索で意味を持たない）。機械的な予備ふるい（疲労語 AND AI 利用語、除外語なし）に当たった 141 件と、AF017 からの引用追跡 4 件。★ 判定は題名と機械抽出の根拠語だけによる（抄録は未読）。Europe PMC と日本語文献の検索は未実行。DB には行を追加していない（提案のみ）。★ 印は中心的に見える候補。",
    headers=["No", "出典", "DOI", "題名", "年", "文献種別", "収録先", "Claude予備判定（題名段）", "除外理由", "想定区分｜メモ"],
    widths=[6, 20, 34, 60, 8, 16, 26, 14, 10, 60], rows=rows))

# ---------- Claude評価基準 ----------
crit = [
 ["評価の対象", "元 DB の AF001–AF034（34 件）。新しい検索の候補は『検索漏れ候補』に分けた（DB の件数には加えない）。", ""],
 ["評価日・評価主体", "2026-09-28。判定: Claude Opus 5.5（メイン）。一次資料からの事実抽出と検索: Claude Sonnet のサブエージェント 7 本（6 群＋検索 1）。", "温度などの実行設定は取得していない。"],
 ["盲検性", "盲検ではない: メインは判定前に元 DB と既存 AI 評価（GPT-6 Astra Pro）の全シートを読んだ。緩和策: 抽出担当には題名・DOI・URL のみを渡し、元 DB の値と既存評価の結論を渡していない。判定規則は抽出結果を読む前に固定した。", "判定規則: repo の .steering/20260928-ai-fatigue-db-appraisal/design.md（プロトコル v1.0）。"],
 ["人間の判定との関係", "AI の予備判定であり、人間 2 名の独立判定の代わりにならない。元の『スクリーニング』（判定者 1・2・最終判定）と『AI判定比較』の人間用欄は変更していない（機械で確認）。", "元ワークブック逐語: 判定者1・2は独立した人間の担当者を想定し、AIの予備整理を独立判定に数えません。"],
 ["中心-A（AI 特異）", "一次研究で、疲労の構成概念が AI に帰属させて定義・測定されている（項目文・定義・質問文に AI が明示される、または AI 疲労としての語りを分析する）。", "★ 抄録だけで AI 帰属が確かめられない件は『中心（A/B 未確定）』とし、A にも B にも数えない（全文で AI 帰属と分かった AF004・AF019 が中心-B だった先例による）。"],
 ["境界（保留）", "P と C のどちらかが規則だけでは閉じない件（AF024: GenAI に帰属した過負荷・関心の低下を学習バーンアウトの代理として測るが、情緒的消耗の項目はない）。", "範囲の判断を人間の判定者に委ねる。E コードは付けない。"],
 ["中心-B（AI 文脈）", "一次研究で、疲労・消耗・バーンアウトを測定または質的に分析しているが、構成概念は一般的（AI を項目に含まない）で、AI の利用・AI 由来の要求を説明変数・文脈・標本定義として関係づけている。", "中心-A と別集計。中心-B の結果を『AI 疲労』の証拠として合算しない。"],
 ["背景（E2）", "疲労を測っていない一次研究（認知負荷・不安・過信・批判的思考・利用量のみ）。", "証拠集合の外。DB からは削除しない。"],
 ["背景（E4）・方法論・訂正", "既存レビュー・尺度の原著・理論（背景）、報告指針・方法論（方法論保持）、訂正通知（訂正連結）。", "証拠集合の外で別枠保持。"],
 ["除外理由コード", "E1 AI が疲労を検出・予測する道具であるだけ／E2 疲労を定義・測定・質的分析していない／E3 疲労を測るが AI の利用・監督と関係づけていない／E4 一次研究でない／E5 重複出版・同一標本・版違い（検索漏れ候補では、プレプリント・データ保管庫の版違いが確定した場合にも使う。未確定なら保留）／E6 全文入手不可で全文段は判定不能（→保留）。", "この表にない理由で除外しない。質の低さは除外理由にしない（引用の範囲で扱う）。"],
 ["題名・抄録段と全文段", "題名・抄録段: P と C に当たる可能性のある一次研究は『含める』（迷ったら含める）。全文段: 全文を読めたものだけ判定し、読めなかったものは『保留』（全文確認=入手不可）。", ""],
 ["方法論評価", "JBI チェックリストの項目文に準拠（横断 8／質的 10／RCT 13／レビュー 11）、尺度は COSMIN の測定特性。各項目 Y／N／U／NA。全文未取得は全項目 U。", "合計点・総合格付けは付けない（JBI も合計点での除外を推奨しない）。★ 横断の項目 5・6 の規則: 共変量・交絡候補を名指し → 5=Y、名指しなし → 5=N、統計的に統制 → 6=Y、統制なし → 6=N、確認できない → U。"],
 ["品質評価欄・全文確認欄", "品質評価: 全文で JBI／COSMIN の項目を埋めた件＝完了（AI予備）、抄録のみ＝進行中、方法論・訂正＝対象外。全文確認・抽出: AI が全文から抽出済み（人間の点検待ち）＝進行中、全文に届かない＝入手不可、方法論・訂正＝対象外。", "背景（E2・E4）も同じ規則（証拠集合の外でも評価は実施した）。"],
 ["領域別評価の段階", "低懸念: 具体的な手当てがあり主張の強さと釣り合う／一部懸念: 手当ての一部が欠ける、または主張がデザインを少し超える／高懸念: 引用する主張を直接損なう問題を一次で確認／判定不能: 全文未取得・判断材料なし／非該当: 質的研究の時間順序など。", "時間順序・因果は『因果解釈に使う場合』の懸念を評価。★ 『非該当』は design §5 に無い値で、時間的な主張をしない質的研究（AF006・AF010）の時間順序に使った（段階モデルを主張する AF007 は一部懸念）。質的研究の交絡・文脈には研究者の位置・反例の扱いを書いた。"],
 ["照合事項の再照合の値", "一次で支持／一部支持／一次で否定／判定不能に加え、保留を閉じた件は『解消』（R-I06・R-I11）と書いた（design §6 に無い値）。", ""],
 ["確認経路", "メイン一次: メインが一次資料を自分で開いて確認。サブエージェント抽出: サブエージェントが一次資料から逐語で抽出し、メインは要点を照合。WebFetch 要約経由: 要約モデルを介した抽出（AF005・AF016 ほか）。★ 検証担当（反証役・偽の主張 1 件を混入）がサブエージェント由来の 10 主張を一次で再照合し、偽の主張は否定・9 件は支持（うち AF005 の項目文は言い換えだったため逐語に修正、AF017 は表現を精密化）。", ""],
 ["一次資料への到達手段", "API（Crossref・OpenAlex・Europe PMC・Semantic Scholar・Unpaywall・DOI handle）、出版社・著者公開の PDF、Wayback Machine の保存版（AF012・AF024）、研究者の許可のもとブラウザ経由の出版社ページ（AF002〜AF004・AF015・AF019・AF034）、研究者が所蔵する AF001 の出版社版 PDF。", ""],
 ["全文に到達できなかった件", "AF002・AF003・AF009・AF015・AF021・AF025・AF027・AF028・AF031（抄録・書誌まで）。AF019 は全文の一部（方法・限界）を読解。", "未到達は低品質を意味しない。"],
 ["GSE 照合の位置付け", "GSE の既存調査・理論文書との照合は別シートに置き、採否に使っていない。", "プロトコル §7。"],
 ["検索漏れ点検", "OpenAlex と Crossref で 11 クエリ（各上位 50 件）。予備ふるいは正規表現。題名と根拠語だけで予備判定。Europe PMC と日本語文献は未実行。", "PRISMA の件数には使えない（上位 50 件に限った点検）。"],
 ["数値の照合", "AF011 の Pearson 検定の再計算、AF006 の百分率の分母、AF004 の間接効果、AF008 の対数尤度の逆算は、報告値だけを使った算術の照合であり、原データは使っていない。", "誤りの場所・原因は断定しない。"],
 ["保存", "本ファイルと抽出ノート・検索ログは GSE リポジトリの .steering/20260928-ai-fatigue-db-appraisal/archive/ に保管（研究者の依頼）。", "元ファイルは上書きしていない。"],
 ["方法論の参照", "JBI critical appraisal tools https://jbi.global/critical-appraisal-tools ／ PRISMA-ScR https://www.prisma-statement.org/scoping ／ COSMIN（Prinsen et al. 2018）https://link.springer.com/article/10.1007/s11136-018-1798-3", "正式判定とは称さない。"],
]
S.append(dict(name="Claude評価基準", title="Claude評価基準｜範囲・手順・限界",
    subtitle="今回の評価で用いた操作的基準。事前登録済みのプロトコルではないが、抽出結果を読む前に固定した（repo の steering に記録）。",
    headers=["項目", "規則・説明", "備考"], widths=[22, 100, 60], rows=crit))

# ---------- Claude評価概要（数式で他シートを数える） ----------
nC = len(CHECKS)
A = "'Claude適格性評価'!"; SCR = "'Claudeスクリーニング案'!"; DOM = "'Claude領域別評価'!"; CMP = "'Claude×GPT比較'!"; CHK = "'Claude照合事項'!"; SGS = "'検索漏れ候補'!"
nd = 4 + len(central); nsg = 4 + n_sg; nck = 4 + nC
ov = [
 ["評価レコード", f"=COUNTA({A}A5:A38)", "元 DB の 34 件。"],
 ["中心-A（AI 特異）", f'=COUNTIF({A}K5:K38,"中心-A")', "AF001・AF005〜AF008・AF010・AF011。"],
 ["中心（A/B 未確定・抄録のみ）", f'=COUNTIF({A}K5:K38,"中心（*")', "AF002・AF003・AF009。全文で項目を確かめて A か B に振り分ける。"],
 ["中心-B（AI 文脈の一般的疲労）", f'=COUNTIF({A}K5:K38,"中心-B")', "AF004・AF012・AF019。中心-A と別集計。"],
 ["背景（E2・疲労未測定の一次研究）", f'=COUNTIF({A}K5:K38,"背景（E2）")', "AF020〜AF023。"],
 ["境界（保留）", f'=COUNTIF({A}K5:K38,"境界*")', "AF024。範囲の判断を人間に委ねる。"],
 ["背景（E4・レビュー・尺度・理論）", f'=COUNTIF({A}K5:K38,"背景（E4）")', "AF013〜AF018・AF025〜AF029。"],
 ["方法論 / 訂正", f'=COUNTIF({A}K5:K38,"方法論*")&" / "&COUNTIF({A}K5:K38,"訂正*")', "AF030〜AF033 / AF034。"],
 ["スクリーニング案: 含める", f'=COUNTIF({SCR}F5:F38,"含める")', "全文段まで含めた Claude 案。"],
 ["スクリーニング案: 保留（全文入手不可・境界例）", f'=COUNTIF({SCR}F5:F38,"保留")', "AF002・AF003・AF009 は機関アクセスで全文を取得して判定。AF024 は範囲の判断待ち。"],
 ["スクリーニング案: 除外（背景として保持）", f'=COUNTIF({SCR}F5:F38,"除外")', "E2・E4。DB からは削除しない。"],
 ["本文関連箇所まで確認", f'=COUNTIF({A}F5:F38,"本文関連箇所確認")', "全文（または方法・結果の該当節）を読んだ件。"],
 ["抄録・公開要約まで", f'=COUNTIF({A}F5:F38,"抄録・公開要約確認")', ""],
 ["メインが一次で確認した件", f'=COUNTIF({A}M5:M38,"*メイン*")', "他はサブエージェントの抽出（逐語）に依拠。"],
 ["領域別で高懸念を含む中心候補", f'=COUNTIF({DOM}K5:K{nd},"*×*")&" / "&COUNTA({DOM}A5:A{nd})', "AF004・AF006・AF008・AF011（透明性の懸念は §5 の規則で一部懸念にとどめた）。"],
 ["GPT と用途判定が一致 / 相違", f'=COUNTIF({CMP}F5:F38,"一致")&" / "&COUNTIF({CMP}F5:F38,"相違")', "相違は AF019（背景保持→中心候補）と AF024（背景保持→保留）。"],
 ["照合事項: 既存の再照合 / 新規", f'=COUNTIF({CHK}A5:A{nck},"R-I*")&" / "&COUNTIF({CHK}A5:A{nck},"C*")', ""],
 ["検索漏れ候補: 含める / 保留 / 除外", f'=COUNTIF({SGS}H5:H{nsg},"含める")&" / "&COUNTIF({SGS}H5:H{nsg},"保留")&" / "&COUNTIF({SGS}H5:H{nsg},"除外")', "題名段の予備判定。★ 印の中心的な候補は『想定区分』列を参照。"],
 ["主な所見 1", "AF006 と AF007", "AF006 の Table 3 の百分率は分母 1054（AF007 の N）で一致し、表記の N=1000 と合わない。統合時は同一標本の可能性として 1 つに数える（C01）。"],
 ["主な所見 2", "AF004", "交互作用の向きが論文内で逆（抄録・§4.3『増幅』／§3.4・§4.1『緩和』）。訂正通知 AF034 は参考文献 2 件のみで、この点は未訂正（C02・R-I06）。"],
 ["主な所見 3", "AF008", "疲労の定義は AI に帰属（中心-A）。本文 36 項目・表 24 項目の食い違い、k=4・k=9 の解は最大尤度解でない（対数尤度の逆算）（C04・C05）。"],
 ["主な所見 4", "AF011", "図の注が『個々の調査項目』と明記し、p=.053 は N=6 の検定と一致。数値は引用しない（R-I01）。"],
 ["主な所見 5", "AF012・AF014", "AF012 は倫理承認の記載が本文と宣言で矛盾（R-I03）。AF014 は採択件数 22／30、PDF の DOI は未登録で DB の DOI が正しい（C07）。"],
 ["主な所見 6", "AF019・AF024", "同じ規則で AF019 は中心-B（MBI-GS の消耗を測定）。AF024 は GenAI に帰属した過負荷・関心の低下を代理として測るが情緒的消耗の項目がなく、境界例として保留（R-I11・C11）。"],
 ["主な所見 7", "AF020（GSE 由来）", "著者は知覚された使いやすさの低下を限界に挙げ（DB の要約と一致）、条件間で有意だったのはシステムの複雑さのみ。2026 年の関連報告（本文未照合）の追記を提案（C15）。"],
 ["主な所見 8", "検索漏れ", "中心的に見える未収録の候補が複数（査読論文: JEIM 2026 の意思決定疲労・Sci Rep 2026・Acta Psychologica 2026・AI & Society 2025、AF017 の引用追跡 3 件。非査読: 既存のシステマティックレビュー 1 件（Zenodo））。"],
 ["読む順番", "Claude適格性評価 → Claude方法論評価 → Claude領域別評価 / Claude照合事項 → Claudeスクリーニング案", "Claude×GPT比較・GSE照合・検索漏れ候補は補助。基準は Claude評価基準。"],
 ["限界", "盲検ではない／全文未到達 9 件／一部は WebFetch 要約経由／検索漏れは題名段のみ／正式な JBI・COSMIN 判定ではない", "詳細は Claude評価基準。"],
]
S.insert(0, dict(name="Claude評価概要", title="AI 疲労 文献 DB｜Claude による再評価（2026-09-28）",
    subtitle="元の 16 シートは変更せず、Claude の評価を追加した。★ 人間の独立判定の代わりではない（AI の予備判定）。数字の列は各シートを数える数式で、シートを編集すると更新される。",
    headers=["項目", "値", "説明"], widths=[34, 34, 100], rows=ov, subtitle_height=40, formula_cols=[2]))

# design §9 の検査（空欄なし・E コードの値域・件数の整合）
import re as _re
TIERS = ("中心-A", "中心（A/B 未確定）", "中心-B", "境界（保留）", "背景（E2）", "背景（E4）", "方法論（E4）", "訂正（E4）")
assert all(R[i]["tier"] in TIERS for i in IDS), [R[i]["tier"] for i in IDS if R[i]["tier"] not in TIERS]
for i in IDS:
    x = R[i]
    for k in ("use", "scope", "level", "state", "url", "loc", "tier", "basis", "route", "ta", "ft", "final", "ftstat", "qa"):
        assert x.get(k), (i, k)
    assert x["final"] in ("含める", "除外", "保留"), (i, x["final"])
    assert (x["final"] == "含める") == (x["reason"] == ""), (i, x["reason"])
    assert x["final"] != "除外" or _re.match(r"^E[1-6]（", x["reason"]), (i, x["reason"])
    assert x["tier"].startswith("中心") == (x["dom"] is not None), i
sg_rows = next(s for s in S if s["name"] == "検索漏れ候補")["rows"]
assert all(r[7] in ("含める", "除外", "保留") for r in sg_rows) and all(r[8] == "" or _re.match(r"^E[1-6]$", r[8]) for r in sg_rows)
assert all((r[7] == "除外") == bool(r[8]) for r in sg_rows), [r[0] for r in sg_rows if (r[7] == "除外") != bool(r[8])]

json.dump(S, open(f"{SP}/claude_eval.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("sheets:", [(s["name"], len(s["rows"])) for s in S])
