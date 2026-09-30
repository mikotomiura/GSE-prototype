"""内容の群の全件の確かめ（design.md §7.7・判断 9・2026-10-01 固定）。

  bundle : 独立の読み手に渡す束（scratchpad・repo の外）を 3 つ作る。機械の値・メインの直しは入れない。
  compare: 読み手の値（scratchpad の JSON）を検め、値だけを repo に書き、機械の値との食い違いを scratchpad の md に並べる。
  apply  : 一致した記録と、メインの裁定（MAIN）を当てて、確かめた値を書く。

★ 抄録・要点・読み手の根拠の文は repo に写さない（repo には鍵と 4 軸の値だけ）。範囲の判断（E1〜E3）はしない。
使い方（このディレクトリで）:
  uv run --with openpyxl python content_groups_check.py bundle --abs <抄録の JSON> --outdir <scratchpad の dir>
  uv run python content_groups_check.py compare --reader <r1.json> <r2.json> <r3.json> --out dedup/content_groups_2026-10-01_reader.json \
      --abs <抄録の JSON> --report <scratchpad の md>
  uv run python content_groups_check.py apply --reader dedup/content_groups_2026-10-01_reader.json --out dedup/content_groups_2026-10-01_checked.json
"""
import argparse
import datetime
import json
import os
import random
import sys

import content_groups as C
import dedup as D

MACHINE = os.path.join(D.HERE, "dedup", "content_groups_2026-09-30_final.json")
KINDS = ["一次研究", "レビュー等"]
POPS = ["医療者", "教員・研究者", "学生・学習者", "働く人（医療・教育の外）", "消費者・一般の利用者", "不明"]
AIS = ["記録支援・下書き", "意思決定支援・警報・予測", "生成 AI・対話", "AI 一般・導入", "不明"]
DESIGNS = ["無作為化", "比較（非無作為化・前後）", "縦断", "尺度開発", "質的", "実験・模擬", "横断調査", "不明"]
AXES = ("kind", "pop", "ai", "design")
SPLIT = (87, 86, 86)
SEED = 20261001
N_SAMPLE = 20

P, REV = "一次研究", dict(kind="レビュー等", pop="—", ai="—", design="—")
MED, EDU, STU, WRK, CON, UPOP = POPS
DOC, DSS, GEN, GAI, UAI = AIS
RCT, CMP, LON, SCL, QUA, EXP, CRS, UDES = DESIGNS


def v(pop, ai, design):
    return dict(kind=P, pop=pop, ai=ai, design=design)


# メインの裁定（2026-10-01・食い違い 98 件を束の題名・抄録・要点・DB の欄で読んだ）: 鍵 → (軸の値, 理由)。★ 理由は短く、抄録を引用しない。
# 読み方（§7.7 の定義の当て方・判断 10）: AI を研究者が分析にだけ使い、参加者が使っていなければ AI の種類は不明。疲労・燃え尽きを検知・予測する AI は
# 意思決定支援・警報・予測。模擬の場面で条件を比べる研究は実験・模擬、現場で群・前後を比べる研究は比較。デザインはデータの集め方で決める（計算の実験は数えない）。
MAIN = {
    "AF001": (v(CON, GAI, SCL), "4 研究・717 名の尺度の開発（題名の framework は研究の中の概念の枠組み）。AI は特定の道具でない"),
    "AF006": (v(STU, GAI, QUA), "学習での AI 一般（記録支援の道具ではない）"),
    "AF007": (v(STU, GAI, QUA), "自由記述の grounded theory（尺度の開発は今後の課題と書く）"),
    "AF009": (v(STU, GAI, SCL), "29 項目の探索的因子分析と信頼性が主な分析"),
    "AF021": (v(STU, GEN, RCT), "看護学生（医療系の学生は学生・学習者）"),
    "AF023": (v(WRK, GEN, CRS), "調査の量的な分析と自由記述の混合（量的の設計を採る）"),
    "AF024": (v(STU, GEN, CMP), "学生 143 名の調査と授業の介入・2 回の調査"),
    "S02-13": (v(STU, GAI, CRS), "調査の EFA と SEM（尺度の開発が主目的ではない）"),
    "S12-01": (v(MED, DSS, RCT), "心エコーの AI の自動計測（画像の解析の支援）"),
    "S12-02": (v(MED, GEN, RCT), "8 名を無作為に 2 群に割り付けた"),
    "S12-03": (v(STU, GEN, CRS), "学習者 100 名の質問紙（尺度と自由記述の混合）"),
    "S12-04": (v(STU, GEN, UDES), "授業で学習者が ChatGPT を使う実践の報告（測定の記述なし）"),
    "S12-07": (v(MED, DSS, CRS), "放射線科の AI（読影の検出・診断の支援）"),
    "S12-09": (v(EDU, GEN, EXP), "教科ごとの問い合わせで ChatGPT を試した（参加者の調査の記述なし）"),
    "S04-06": (v(MED, GEN, RCT), "微調整した LLM の対話ボット（意思決定支援ではない）"),
    "S04-07": (v(STU, DSS, RCT), "歯学部の学生・AI が形成の誤りを検出して示す"),
    "S04-08": (v(WRK, DSS, RCT), "アルゴリズムの意思決定支援の道具"),
    "S04-09": (v(EDU, GAI, CMP), "対照群と実験群の t 検定（無作為と書かない）"),
    "S04-11": (v(EDU, GEN, CMP), "単一事例の AB-AB（無作為の割り付けなし）"),
    "S04-12": (v(STU, GEN, CMP), "記録の後ろ向きの 2 群の比較"),
    "S04-20": (v(MED, DOC, CMP), "前後の比較と中断時系列（テーマ分析は補足）"),
    "S04-28": (v(MED, DOC, CMP), "試行の前と途中の調査（前向きの前後）"),
    "S04-33": (v(WRK, GAI, CMP), "遺伝的アルゴリズムの予定づけ（LLM は初期値にだけ使う）"),
    "S04-36": (v(WRK, GEN, LON), "題名が生成 AI の導入と書く"),
    "S04-42": (v(MED, DOC, CMP), "AI・人・なしの 3 群の後ろ向きの比較"),
    "S04-50": (v(MED, DOC, CMP), "基準・6 週・3 か月の調査と面接の混合（量的の前後を採る）"),
    "S04-52": (v(MED, DOC, CMP), "試行の前と後の調査"),
    "S04-54": (v(MED, GAI, RCT), "機械学習は集めたデータの分析に使っただけ（道具は質問のプラットフォーム）"),
    "S04-56": (v(MED, DOC, CMP), "同じ臨床医の使う・使わないの観察の比較"),
    "S04-59": (v(MED, DOC, CMP), "AI 群と従来群の前向きのコホートの比較"),
    "S04-62": (v(MED, DOC, CMP), "試行群と非試行群の比較"),
    "S04-63": (v(MED, DOC, CMP), "保健所の担当者・模擬と現場の 2 段（現場は通常の業務と比較）"),
    "S04-71": (v(MED, UAI, CMP), "LLM は記録の分類の分析に使っただけ（看護師は AI を使っていない）・方針の前後の自然実験"),
    "S04-73": (v(MED, DOC, CMP), "利用開始の前後と中断時系列（要約の qualitative の語は方法と合わない）"),
    "S04-75": (v(MED, DOC, EXP), "模擬の救急外来の台本の場面で、同じ参加者が両方を使った"),
    "S04-77": (v(MED, UAI, CMP), "AI は研究者が訓練の前後の動画の分析に使った（医師は AI を使っていない）"),
    "S04-78": (v(MED, DOC, CMP), "AI スクライブと口述の比較（PDSA・2 名）"),
    "S04-82": (v(MED, DOC, RCT), "先に使う段と対照の段に無作為に割り付けた"),
    "S04-85": (v(STU, GAI, CMP), "学部生・AI の学習の環境（意思決定支援ではない）・授業の場の対照群と実験群（無作為と書かない）"),
    "S04-86": (v(MED, DSS, CMP), "論文が意思決定支援の系と書く（予測モデルを含む）"),
    "S05-01": (v(CON, GEN, EXP), "テストコースの実験（面接は補足）"),
    "S05-02": (v(CON, GEN, EXP), "運転の監視の実験の参加者・AI との会話"),
    "S05-03": (v(CON, DSS, EXP), "模擬の点検の実験の参加者（職業の記述なし）・AI の検出の支援"),
    "S05-04": (v(CON, DSS, EXP), "決定支援の利用者の 2 つの研究（利用者の実験）"),
    "S05-05": (v(UPOP, GAI, EXP), "模擬の追跡の課題の実験"),
    "S05-06": (v(MED, DOC, EXP), "模擬の訓練の中での評価（共同設計の面接は補足）"),
    "S15-03": (v(STU, GAI, CRS), "AI 一般への依存（特定の生成 AI と書かない）"),
    "S15-07": (v(STU, GEN, CRS), "AI アシスタント（会話型）への依存"),
    "S15-10": (v(CON, DSS, EXP), "アルゴリズムの示唆による自動化バイアスの実験"),
    "S15-13": (v(EDU, GEN, QUA), "研修中の振り返りと自由記述を SWOT で分析"),
    "S15-14": (v(STU, GAI, QUA), "学生・AI の書く支援・機械翻訳・オンラインの基盤（技術の全般）"),
    "S15-15": (v(STU, GEN, QUA), "大学生への面接"),
    "S15-17": (v(STU, GEN, CMP), "英語教育専攻の学生"),
    "S14-03": (v(EDU, GAI, CRS), "AI への不安（一般の構成概念）"),
    "S14-06": (v(STU, GEN, CRS), "横断の調査（PLS-SEM）"),
    "S14-19": (v(WRK, GEN, UDES), "上司が AI でメールを書く（生成 AI）"),
    "S14-24": (v(EDU, GAI, CRS), "高等教育の教員と事務の職員（上の順で教員・研究者）"),
    "S14-31": (v(EDU, GAI, QUA), "高等教育での AI の導入の全般"),
    "S14-32": (v(WRK, GAI, QUA), "公共部門の職員"),
    "S14-33": (v(STU, GAI, QUA), "大学院生"),
    "S13-01": (v(EDU, GAI, CRS), "アルゴリズムによる評価・管理（臨床の意思決定支援ではない）"),
    "S13-02": (v(EDU, GAI, CRS), "面接と PLS-SEM の調査の混合（量的を採る）"),
    "S13-04": (v(WRK, GAI, LON), "多時点の現場の調査と場面の実験（上の順で縦断）"),
    "S13-05": (v(WRK, GAI, CRS), "調査 500 と面接 30 の混合（量的を採る）"),
    "S13-09": (v(MED, GAI, QUA), "記録の生成・意思決定支援・治療の支援など複数の技術の全般"),
    "S13-12": (v(MED, DSS, CRS), "面接と記述の調査の混合（尺度の開発ではない）"),
    "S13-13": (v(WRK, GAI, UDES), "抄録は研究で明らかにしたと書き、開発者と QA の経験を挙げる（方法の記述なし）"),
    "S15-18": (v(STU, GAI, CRS), "看護学生・AI 一般への依存の尺度・調査と面接の混合（量的を採る）"),
    "S15-19": (v(WRK, DSS, CRS), "製品管理職 174 名の調査"),
    "S15-20": (v(EDU, GEN, CRS), "質問紙と面接の混合（量的を採る）"),
    "S15-22": (v(STU, GEN, CRS), "学習の疲労と利用の関係を報告（方法の記述は乏しい）"),
    "S15-23": (REV, "対象と方法の記述が無く、著者の議論が中心"),
    "S14-35": (v(MED, GAI, RCT), "AI は介入の内容を選ぶ推薦の算法（参加者の判断を支える道具ではない）"),
    "S14-36": (v(MED, GAI, RCT), "AI は介入の内容を選ぶ推薦の算法（S14-35 と同じ読み方）"),
    "S14-37": (v(MED, GAI, CMP), "AI は介入の内容を選ぶ推薦の算法（S14-35 と同じ読み方）"),
    "S14-38": (v(MED, GEN, CMP), "事例の系列の交代のデザイン（ABCABC・無作為の割り付けなし）"),
    "S14-39": (v(CON, GEN, CRS), "ChatGPT の利用者の調査によるモデルの検証"),
    "S14-42": (v(WRK, GAI, CRS), "労働者の調査と二次資料の混合（量的を採る）"),
    "S14-44": (v(STU, DSS, QUA), "燃え尽きを早期に検知する AI"),
    "S13-16": (v(WRK, DSS, CRS), "既存の調査のデータで予測モデルを作った（題名の framework は研究の中の手法）"),
    "S13-17": (v(WRK, DSS, CRS), "人事のデータで、燃え尽きの代わりの欠勤を予測するモデル"),
    "S13-18": (v(WRK, DSS, CRS), "燃え尽きを検知する仕組み（検知・予測の AI）・自己申告の調査"),
    "S13-19": (v(EDU, DSS, UDES), "ストレスを診断する AI（ファジィ論理）・設計の記述なし"),
    "S13-20": (REV, "抄録なし。題名は経営の視点の論説"),
    "S04-40": (v(EDU, GEN, CMP), "学校のカウンセラー（教育の場の職員）・実験群と対照群（無作為と書かない）"),
    "S08-02": (v(CON, GEN, EXP), "12 名の予備の評価（画面の利用の評価）"),
    "S08-03": (REV, "抄録なし。題名は設計の方法の提案"),
    "S12-12": (v(MED, UAI, QUA), "ChatGPT は面接の分析の道具（看護師は AI を使っていない）"),
    "S12-13": (v(WRK, GAI, CMP), "非無作為化のクロスオーバー"),
    "S12-14": (v(MED, DSS, EXP), "看護職 4 名と入居者の実地の実験（通知の系の評価）"),
    "S12-17": (v(UPOP, DSS, UDES), "疲労の検知（LLM の例の選び方）・データの集め方の記述なし"),
    "S12-18": (v(UPOP, DSS, UDES), "抄録なし。題名は疲労の検知"),
    "S12-19": (REV, "研究の計画（将来形・結果なし）"),
    "S12-21": (v(EDU, GEN, UDES), "LLM による判定と人の判定の比較（臨床の意思決定支援ではない）"),
    "S12-22": (v(UPOP, DSS, UDES), "抄録なし。題名は筋疲労度を判定する AI"),
    "S12-23": (REV, "抄録なし。題名は可能性の検討（論説）"),
    "S12-24": (v(CON, DSS, CRS), "患者の音声から状態を分類するモデル"),
    "S12-25": (v(CON, DSS, CRS), "患者 51 名の音声の資料と分類の基準値"),
}
# 一致した記録の抜き取り（seed 20261001・20 件）で、メインが誤りと分かったもの（鍵 → (軸の値, 理由)）。★ 20 件とも正しかった
SAMPLE_FIX = {}
# ★ 抜き取りの外で、裁定の中で見つけた一致した記録の誤り（§7.7 からの逸脱・判断 10）
AGREED_FIX = {
    "S12-11": (v(MED, UAI, QUA), "同じ研究の S12-12 と同じ読み方（ChatGPT は面接の分析の道具・看護師は AI を使っていない）"),
}


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def group_name(v):
    return "レビュー等" if v["kind"] == "レビュー等" else f"{v['pop']}｜{v['ai']}｜{v['design']}"


def db_info():
    """元の DB の『研究情報』の 3 欄（研究デザイン・対象集団・AI・利用環境）と『文献DB』の分類（DB 34 件）。"""
    import openpyxl
    wb = openpyxl.load_workbook(C.DB_XLSX, read_only=True, data_only=True)
    cls = {r[0]: r[1] for r in wb["文献DB"].iter_rows(min_row=5, values_only=True) if r[0]}
    out = {}
    for r in wb["研究情報"].iter_rows(min_row=5, values_only=True):
        if r[0]:
            out[r[0]] = dict(design=r[2] or "", pop=r[3] or "", ai=r[6] or "", cls=cls.get(r[0]) or "")
    return out


WRAP = 800  # ★ 読み手の Read は 2,000 字を超える行を切るので、値を折り返す（2026-10-01 に最大 1 万字の行があった）


def wrap(label, text):
    """『- 見出し: 値』を、WRAP 字ごとに空白の位置で折り返す（続きの行は 2 字下げ）。"""
    words, lines, cur = " ".join(str(text).split()).split(" "), [], f"- {label}:"
    for w in words:
        if len(cur) + 1 + len(w) > WRAP and cur.strip():
            lines.append(cur)
            cur = "  " + w
        else:
            cur += " " + w
    lines.append(cur)
    return lines


def entry(r, abstracts, pts, dbi):
    lines = [f"## {r['key']}"] + wrap("題名", r["title"]) + wrap("抄録", abstracts.get(r["key"]) or "（抄録なし）")
    if r["key"] in pts and pts[r["key"]]:
        lines += wrap("要点", pts[r["key"]])
    if r["key"] in dbi:
        d = dbi[r["key"]]
        lines += wrap("DB の研究情報", f"研究デザイン={d['design']}／対象集団={d['pop']}／AI・利用環境={d['ai']}")
        lines.append(f"- DB の分類: {d['cls']}")
    return "\n".join(lines)


def cmd_bundle(a):
    D.ensure_outside_repo(a.outdir)
    recs = D.load_259()
    abstracts = D.load_abstracts(a.abs)
    pts, dbi = C.points(), db_info()
    i = 0
    for n, size in enumerate(SPLIT, 1):
        part = recs[i:i + size]
        i += size
        p = os.path.join(a.outdir, f"cg_bundle_{n}.md")
        with open(p, "x", encoding="utf-8", newline="\n") as f:
            f.write(f"# 束 {n}（{len(part)} 件: {part[0]['key']} 〜 {part[-1]['key']}）\n\n")
            f.write("\n\n".join(entry(r, abstracts, pts, dbi) for r in part) + "\n")
        print(p, len(part))
    if i != len(recs):
        sys.exit(f"束の件数の合計が {i}（259 件ではない）")
    return 0


def check_values(key, v):
    errs = []
    if v.get("kind") not in KINDS:
        errs.append(f"{key}: kind『{v.get('kind')}』")
    elif v["kind"] == "レビュー等":
        if any(v.get(x) != "—" for x in ("pop", "ai", "design")):
            errs.append(f"{key}: レビュー等なのに軸の値がある")
    else:
        for ax, allowed in (("pop", POPS), ("ai", AIS), ("design", DESIGNS)):
            if v.get(ax) not in allowed:
                errs.append(f"{key}: {ax}『{v.get(ax)}』")
    return errs


# ★ 2026-10-01: 束 1 の読み手が AI の種類の値の半角の空白を落とした（意味は一意）。この 2 つだけを表の表記に直し、ほかの表記ゆれは止める（判断 10）
NORMALIZE = {"ai": {"生成AI・対話": "生成 AI・対話", "AI一般・導入": "AI 一般・導入"}}


def normalize(v):
    """読み手の値の表記ゆれ（NORMALIZE にあるものだけ）を直す。直した軸の数も返す。"""
    v, n = dict(v), 0
    for ax, table in NORMALIZE.items():
        if v.get(ax) in table:
            v[ax] = table[v[ax]]
            n += 1
    return v, n


def load_reader(paths):
    out, fixed = {}, 0
    for p in paths:
        for k, v in json.load(open(p, encoding="utf-8")).items():
            if k in out:
                sys.exit(f"読み手の値に鍵が 2 回ある: {k}")
            out[k], n = normalize(v)
            fixed += n
    print("表記を直した値", fixed)
    return out


def diff_axes(m, r):
    return [ax for ax in AXES if m[ax] != r[ax]]


def cmd_compare(a):
    D.ensure_outside_repo(a.report)
    keys = [r["key"] for r in D.load_259()]
    reader = load_reader(a.reader)
    if set(reader) != set(keys):
        sys.exit(f"読み手の鍵が 259 件と違う: 足りない {sorted(set(keys) - set(reader))[:10]}・余分 {sorted(set(reader) - set(keys))[:10]}")
    errs = [e for k in keys for e in check_values(k, reader[k])]
    if errs:
        sys.exit("値が定義の外: " + "; ".join(errs[:20]))
    vals = {k: {ax: reader[k][ax] for ax in AXES} for k in keys}
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=now(), rule="design.md §7.7・判断 9", reader="general-purpose（sonnet）3 本", n=len(vals), values=vals),
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    machine = json.load(open(MACHINE, encoding="utf-8"))["groups"]
    diffs = {k: diff_axes(machine[k], vals[k]) for k in keys}
    bad = [k for k in keys if diffs[k]]
    agreed = [k for k in keys if not diffs[k]]
    sample = sorted(random.Random(SEED).sample(agreed, min(N_SAMPLE, len(agreed))), key=keys.index)
    recs = {r["key"]: r for r in D.load_259()}
    abstracts, pts, dbi = D.load_abstracts(a.abs), C.points(), db_info()
    with open(a.report, "x", encoding="utf-8", newline="\n") as f:
        f.write(f"# 食い違い {len(bad)} 件（一致 {len(agreed)} 件）\n\n")
        for k in bad:
            m, r = machine[k], reader[k]
            f.write(entry(recs[k], abstracts, pts, dbi) + "\n")
            f.write(f"- 違う軸: {'・'.join(diffs[k])}\n- 機械: {group_name(m) if m['kind'] == '一次研究' else 'レビュー等'}\n")
            f.write(f"- 読み手: {group_name(r)}（根拠: {r.get('why', '')}）\n\n")
        f.write(f"\n# 一致した記録の抜き取り {len(sample)} 件（seed {SEED}）\n\n")
        for k in sample:
            f.write(entry(recs[k], abstracts, pts, dbi) + f"\n- 一致した値: {group_name(vals[k])}\n\n")
    from collections import Counter
    print("一致", len(agreed), "食い違い", len(bad))
    print("軸ごとの食い違い", dict(Counter(ax for k in bad for ax in diffs[k])))
    print("抜き取り", sample)
    return 0


def cmd_apply(a):
    keys = [r["key"] for r in D.load_259()]
    reader = json.load(open(a.reader, encoding="utf-8"))["values"]
    machine = json.load(open(MACHINE, encoding="utf-8"))["groups"]
    out = {}
    for k in keys:
        m, r = {ax: machine[k][ax] for ax in AXES}, reader[k]
        agreed = not diff_axes(m, r)
        if k in MAIN:
            if agreed:
                sys.exit(f"{k}: 一致した記録に MAIN の裁定がある（一致した記録は SAMPLE_FIX か AGREED_FIX に書く）")
            (val, why), src = MAIN[k], "メインの裁定"
        elif k in SAMPLE_FIX or k in AGREED_FIX:
            if not agreed:
                sys.exit(f"{k}: 食い違いの記録が SAMPLE_FIX・AGREED_FIX にある（MAIN に書く）")
            (val, why), src = (SAMPLE_FIX.get(k) or AGREED_FIX[k]), ("メインの裁定（一致した記録の抜き取り）" if k in SAMPLE_FIX
                                                                    else "メインの裁定（一致した記録・裁定の中で見つけた誤り）")
        elif agreed:
            val, why, src = r, "", "一致"
        else:
            sys.exit(f"{k}: 食い違いにメインの裁定が無い")
        errs = check_values(k, val)
        if errs:
            sys.exit("; ".join(errs))
        out[k] = dict({ax: val[ax] for ax in AXES}, group=group_name(val), how=src, **({"why": why} if why else {}))
    extra = set(MAIN) | set(SAMPLE_FIX) | set(AGREED_FIX)
    if extra - set(keys):
        sys.exit(f"裁定の鍵が 259 件に無い: {sorted(extra - set(keys))}")
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=now(), rule="design.md §7.7・判断 9", machine=os.path.basename(MACHINE),
                       reader=os.path.basename(a.reader), n=len(out), groups=out), f, ensure_ascii=False, indent=1)
        f.write("\n")
    from collections import Counter
    print(Counter(v["how"] for v in out.values()))
    print("不明を含む", sum(1 for v in out.values() if "不明" in v["group"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bundle")
    b.add_argument("--abs", required=True)
    b.add_argument("--outdir", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--reader", nargs="+", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--abs", required=True)
    c.add_argument("--report", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--reader", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"bundle": cmd_bundle, "compare": cmd_compare, "apply": cmd_apply}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
