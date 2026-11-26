"""詳細版・知見版・技術版の図の 2 巻目（文字だけだったスライドを図にする）。

数の出どころ:
- chart_multiverse: 論文 2 の原稿の図の数（data/paper2_score.csv。原稿 figdata/score.csv の写し）
- chart_learners・chart_stall・chart_alarm・chart_enja・chart_ime・chart_person: スライドの本文にある
  論文 1・論文 2・IME 論文・加工と照合の原稿・論文 3 の outline の値（findings 版の本文と同じ値）
- 図（fig_*）: ADR-039・043・046・052・054 と docs/project-outputs.md の内容
実行: python3 figs2.py（img/ に書く）"""
import csv
import os

from sketch import Sk, INK, ORANGE, TEAL, INDIGO, OLIVE, PLUM, GRAY, CREAM, WHITE, OUT, laptop, cloud
from figs import PALE, node, harrow

HERE = os.path.dirname(os.path.abspath(__file__))


def chip(sk, x, y, label, col, size=18, h=34):
    w = len(label) * size * 0.95 + 28
    sk.rect(x, y, w, h, col, 2, fill=PALE.get(col, WHITE), jit=0.8)
    sk.text(x + w / 2, y + h / 2, label, size, INK, "mm")
    return w


# ---------------------------------------------------------------- 地図
def fig_map():
    """4 つの面の地図と、系での使い方"""
    sk = Sk(1500, 620, 201)
    faces = [("読める所", TEAL, "観測から確かに言えること", "今: 止まりについては無い（未決）", "判断に使える"),
             ("読めない所", ORANGE, "今の推定器・窓・定義では見分けられない", "今: 推定器の上がりで手前を見分ける", "招待の時機に使わない"),
             ("漏れる所", PLUM, "保存していない中身が観測から推測される", "今: キーの種類の列からの照合", "記録の粒度を制約する"),
             ("定義しだいの所", INDIGO, "数え方と分析の選び方で結論が動く", "今: 止まりの率と作文の点の向き", "割付の時点の決め方にだけ")]
    w, h, gap = 735, 295, 15
    for i, (n, c, mean, ex, use) in enumerate(faces):
        x = 8 + (i % 2) * (w + gap)
        y = 8 + (i // 2) * (h + gap)
        sk.rect(x, y, w, h, c, 3, fill=PALE[c])
        sk.text(x + 28, y + 44, n, 38, c, "lm")
        sk.text(x + 28, y + 108, mean, 27, INK, "lm")
        sk.text(x + 28, y + 155, ex, 25, GRAY, "lm")
        sk.rect(x + 28, y + 200, w - 56, 66, c, 2, fill=WHITE, jit=0.8)
        sk.text(x + w / 2, y + 233, "系では → " + use, 28, INK, "mm")
    sk.save(OUT + "fig_map.png")


# ---------------------------------------------------------------- 出し方
def fig_outlets():
    sk = Sk(1500, 530, 203)
    left = [("道具", ORANGE, "3 つの検査と地図の出力"), ("評価一式", TEAL, "条件・集計・再現の手順"),
            ("論文", INDIGO, "予測・定義・漏れの結果")]
    right = [("GitHub", "コード（オープンソース）"), ("Zenodo", "版ごとの寄託と DOI"), ("OSF", "値を見る前の事前登録")]
    for i, (n, c, d) in enumerate(left):
        node(sk, 10, 10 + i * 140, 470, 122, n, c, 36, d, 26)
        harrow(sk, 485, 71 + i * 140, 690, GRAY)
    sk.line(700, 71, 700, 351, GRAY, 4)
    for j, (n, d) in enumerate(right):
        y = 10 + j * 140
        harrow(sk, 700, y + 61, 925, GRAY)
        sk.rect(935, y, 555, 122, GRAY, 3, fill=CREAM)
        sk.text(1212, y + 40, n, 36, INK, "mm")
        sk.text(1212, y + 90, d, 26, GRAY, "mm")
    sk.rect(10, 440, 1480, 82, OLIVE, 3, fill=PALE[OLIVE])
    sk.text(750, 481, "報告の型: 4 つの面の地図を、作る前に何が言え何が漏れるかを示す型として出す", 28, INK, "mm")
    sk.save(OUT + "fig_outlets.png")


# ---------------------------------------------------------------- 段の順番
def fig_order():
    sk = Sk(1500, 500, 205)
    sk.arrow(10, 445, 1490, 445, INK, 4, 16)
    for x, lab in [(250, "応募の前から"), (800, "期間中"), (1320, "期間の後")]:
        sk.text(x, 480, lab, 26, GRAY, "mm")
    sk.text(10, 26, "段 1", 32, ORANGE, "lm")
    steps = [("本人で試す", "約 1 週間"), ("事前登録を凍結", "値を見る前に"), ("本人以外 3 名", "確認として")]
    for i, (n, s) in enumerate(steps):
        x = 10 + i * 345
        node(sk, x, 55, 310, 130, n, ORANGE, 32, s, 24)
        if i < 2:
            harrow(sk, x + 312, 120, x + 343, ORANGE)
    sk.text(480, 225, "道具", 32, TEAL, "lm")
    node(sk, 480, 255, 420, 130, "3 つの検査と地図", TEAL, 32, "道具を作る", 24)
    harrow(sk, 905, 320, 950, TEAL)
    node(sk, 955, 255, 420, 130, "当てる", TEAL, 32, "GSE の記録・今の 3 つの結果", 22)
    sk.text(1100, 26, "段 2", 32, INDIGO, "lm")
    node(sk, 1100, 55, 390, 130, "招待の有無", INDIGO, 32, "無作為に割り付け・1 人ずつ", 22)
    sk.arrow(1045, 120, 1095, 120, GRAY, 3, 12)
    sk.save(OUT + "fig_order.png")


# ---------------------------------------------------------------- 計算機
def fig_machines():
    sk = Sk(1500, 330, 207)
    laptop(sk, 55, 190, 220, INK, screen=PALE[INDIGO])
    sk.text(165, 240, "Mac", 32, INK, "mm")
    sk.text(165, 290, "開発の主", 25, GRAY, "mm")
    sk.rect(470, 30, 110, 165, INK, 3, fill=PALE[ORANGE])
    sk.ellipse(525, 70, 14, 14, INK, 2)
    sk.line(490, 120, 560, 120, INK, 2, passes=1)
    sk.line(490, 145, 560, 145, INK, 2, passes=1)
    sk.text(525, 240, "G-GEAR", 32, INK, "mm")
    sk.text(525, 290, "Windows の主・重い計算", 25, GRAY, "mm")
    sk.rect(840, 90, 150, 100, INK, 3, fill=WHITE)
    sk.line(830, 194, 1000, 194, INK, 3)
    sk.text(915, 240, "Surface Pro 8", 30, INK, "mm")
    sk.text(915, 290, "ごく稀に", 25, GRAY, "mm")
    cloud(sk, 1300, 115, 240, 130, INK, fill=PALE[TEAL])
    sk.text(1300, 115, "CI", 34, INK, "mm")
    sk.text(1300, 240, "両 OS の CI", 30, INK, "mm")
    sk.text(1300, 290, "push ごとに検査", 25, GRAY, "mm")
    sk.save(OUT + "fig_machines.png")


# ---------------------------------------------------------------- 実績の数
def fig_stats():
    sk = Sk(1500, 330, 209)
    tiles = [("2 OS", ["Windows と macOS", "記録から再生まで"], ORANGE),
             ("13 本", ["公開データの分析", "結果を原稿に"], TEAL),
             ("54 本", ["設計の判断の記録", "（ADR）"], INDIGO),
             ("約 2%", ["8 時間の負荷の CPU", "両 OS で測った"], OLIVE)]
    w, gap = 350, 20
    for i, (big, d, c) in enumerate(tiles):
        x = 10 + i * (w + gap)
        sk.rect(x, 10, w, 310, c, 3, fill=PALE[c])
        sk.text(x + w / 2, 105, big, 72, c, "mm")
        for k, line in enumerate(d):
            sk.text(x + w / 2, 215 + k * 42, line, 27, INK, "mm")
    sk.save(OUT + "fig_stats.png")


def _wrap(s, n):
    out, cur = [], ""
    for ch in s:
        cur += ch
        if len(cur) >= n and ch in "、。・）で":
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- 公開物の表
def fig_public():
    sk = Sk(1500, 500, 211)
    cols = ["コード", "寄託", "事前登録", "プレプリント"]
    subs = ["GitHub", "Zenodo", "OSF", ""]
    rows = [("IME の観測", INDIGO, [1, 1, 1, 1]), ("論文 1（予測）", TEAL, [1, 1, 1, 1]),
            ("論文 2（定義）", OLIVE, [1, 1, 0, 0]), ("加工と照合（原稿）", PLUM, [0, 0, 0, 0])]
    x0, cw = 400, 272
    for j, c in enumerate(cols):
        sk.text(x0 + j * cw + cw / 2, 26, c, 28, INK, "mm")
        sk.text(x0 + j * cw + cw / 2, 62, subs[j], 22, GRAY, "mm")
    for i, (n, c, v) in enumerate(rows):
        y = 90 + i * 92
        sk.rect(8, y, 1484, 80, c, 2, fill=PALE[c], jit=0.8)
        sk.text(28, y + 40, n, 30, INK, "lm")
        for j, ok in enumerate(v):
            cx = x0 + j * cw + cw / 2
            if ok:
                sk.check(cx - 16, y + 40, 26, TEAL, 6)
            else:
                sk.text(cx, y + 40, "—", 30, GRAY, "mm")
    sk.text(750, 480, "GSE の本体と本人の記録（O1）は公開していない", 26, GRAY, "mm")
    sk.save(OUT + "fig_public.png")


# ---------------------------------------------------------------- 5 つの柱
def fig_outputs():
    sk = Sk(1500, 640, 213)
    ST = {"公開済み": TEAL, "原稿": INDIGO, "設計": OLIVE, "これから": GRAY, "内部用": ORANGE}
    pillars = [("観測", INDIGO, [("観測の方法", "公開済み"), ("ロガー", "公開済み"), ("合成入力の記録", "公開済み")]),
               ("推定と定義", TEAL, [("論文 1（予測）", "公開済み"), ("論文 2（定義）", "公開済み"),
                                ("1 人ごとの学習", "原稿"), ("自己解決の指標", "原稿")]),
               ("公開と保護", PLUM, [("加工と照合", "原稿"), ("公開前の関門", "設計"), ("IME 打鍵データ", "これから")]),
               ("本体と介入", ORANGE, [("記録のアプリ", "内部用"), ("再生の道具", "内部用"), ("手跡の層", "内部用"), ("段 1 の手順", "内部用")]),
               ("束ねるもの", OLIVE, [("3 つの検査の道具", "これから"), ("設計の記録", "内部用")])]
    w, gap = 290, 7
    for i, (n, c, items) in enumerate(pillars):
        x = 6 + i * (w + gap)
        sk.rect(x, 6, w, 560, c, 3, fill=WHITE)
        sk.rect(x, 6, w, 76, c, 3, fill=PALE[c])
        sk.text(x + w / 2, 44, n, 30, INK, "mm")
        for k, (it, st) in enumerate(items):
            y = 120 + k * 112
            sk.text(x + w / 2, y, it, 26, INK, "mm")
            cw = len(st) * 23 + 30
            sk.rect(x + w / 2 - cw / 2, y + 26, cw, 40, ST[st], 2, fill=PALE[ST[st]], jit=0.6)
            sk.text(x + w / 2, y + 46, st, 23, INK, "mm")
    sk.save(OUT + "fig_outputs.png")


# ---------------------------------------------------------------- 見込み
def fig_feasibility():
    sk = Sk(1500, 470, 215)
    bands = [("高い", TEAL, ["加工と照合の論文", "3 つの検査の道具", "本体の公開"]),
             ("中くらい", INDIGO, ["論文 3（1 人ごとの学習）", "集計値の公開"]),
             ("低い・不明", ORANGE, ["推定器が門を通るか", "記録を守る加工の形", "人のデータセット"])]
    for i, (n, c, items) in enumerate(bands):
        y = 6 + i * 125
        sk.rect(6, y, 1488, 112, c, 3, fill=PALE[c])
        sk.text(30, y + 56, n, 34, c, "lm")
        x = 235
        for it in items:
            w = len(it) * 27 + 36
            sk.rect(x, y + 22, w, 68, c, 2, fill=WHITE, jit=0.8)
            sk.text(x + w / 2, y + 56, it, 27, INK, "mm")
            x += w + 18
    sk.text(1490, 435, "否定の結果も、地図の「読めない所」「漏れる所」として残る", 28, INK, "rm")
    sk.save(OUT + "fig_feasibility.png")


# ---------------------------------------------------------------- 材料と検査
def fig_data():
    """材料 × 検査の表"""
    sk = Sk(1500, 640, 217)
    data = [("CoAuthor", "AI の提案つきの共同執筆"), ("KLiCKe", "英語の議論文の作文"), ("CS1 2019/2021", "プログラミングの授業"),
            ("ENJA15", "日本語 IME の翻訳"), ("本人の記録", "自然な作業・日本語 IME"), ("合成入力", "IME の観測の評価")]
    checks = [("予測", INDIGO), ("定義", OLIVE), ("漏れ", PLUM), ("止まり", TEAL), ("IME", INDIGO), ("個人", ORANGE)]
    marks = {0: [0, 1, 3, 5], 1: [0, 1, 2, 3], 2: [0, 1], 3: [2], 4: [0, 3, 4], 5: [2, 4]}
    x0, cw = 560, 155
    for j, (n, c) in enumerate(checks):
        sk.rect(x0 + j * cw + 5, 6, cw - 10, 66, c, 2, fill=PALE[c], jit=0.6)
        sk.text(x0 + j * cw + cw / 2, 39, n, 28, INK, "mm")
    for i, (n, d) in enumerate(data):
        y = 84 + i * 92
        sk.rect(6, y, 1488, 82, GRAY, 2, fill=CREAM if i % 2 == 0 else WHITE, jit=0.5)
        sk.text(26, y + 27, n, 29, INK, "lm")
        sk.text(26, y + 62, d, 22, GRAY, "lm")
        for j in marks[i]:
            sk.check(x0 + j * cw + cw / 2 - 16, y + 41, 26, checks[j][1], 6)
    sk.save(OUT + "fig_data.png")


# ---------------------------------------------------------------- グラフ
def chart_multiverse():
    """論文 2: 止まりの率と作文の点の相関、定義 89 通り＋基準（KLiCKe 4,908 人）"""
    rows = list(csv.DictReader(open(os.path.join(HERE, "data", "paper2_score.csv")), delimiter=" "))
    sk = Sk(1500, 640, 219)
    lo_v, hi_v = -0.33, 0.20

    def panel(y0, y1, key, klo, khi, title):
        def Y(v):
            return y1 - (v - lo_v) / (hi_v - lo_v) * (y1 - y0)
        x0, x1 = 100, 1490

        def X(i):
            return x0 + (i - 0.5) / len(rows) * (x1 - x0)
        sk.line(x0, Y(0), x1, Y(0), INK, 2, passes=1)
        for v in [-0.3, -0.1, 0.1]:
            sk.line(x0, Y(v), x1, Y(v), (215, 210, 200), 1, jit=0.2, passes=1)
            sk.text(x0 - 10, Y(v), f"{v:+.1f}", 22, GRAY, "rm")
        sk.text(x0 - 10, Y(0), "0", 22, GRAY, "rm")
        sk.text(x0, y0 - 22, title, 28, INK, "lm")
        for k, r in enumerate(rows):
            v, a, b = float(r[key]), float(r[klo]), float(r[khi])
            c = TEAL if a > 0 else (ORANGE if b < 0 else GRAY)
            x = X(k + 1)
            sk.line(x, Y(a), x, Y(b), c, 3, jit=0.1, passes=1)
            sk.ellipse(x, Y(v), 5, 5, c, 2, fill=c, jit=0.2)
    panel(50, 300, "rho", "lo", "hi", "そのまま: 正 10・負 73・0 をまたぐ 7")
    panel(390, 610, "ln", "llo", "lhi", "作文の長さと観測の長さで調整: 負は 0")
    sk.text(1490, 632, "横: 90 の定義（上の値の順）・縦線は 95% 区間", 22, GRAY, "rm")
    sk.save(OUT + "chart_multiverse.png")


def chart_learners():
    sk = Sk(1500, 560, 221)
    x0, x1 = 30, 760
    lo, hi = 0.45, 0.60

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    sk.text(x0, 24, "止まりの手前を見分けるか（AUC）", 30, INK, "lm")
    sk.line(X(0.5), 70, X(0.5), 440, GRAY, 2, passes=1)
    items = [("推定器の信号 1（CS1）", 0.489, None, INDIGO), ("推定器の信号 2（CS1）", 0.487, None, INDIGO),
             ("前の打鍵の量で学んだ学習器", 0.54, 0.57, ORANGE)]
    for i, (n, a, b, c) in enumerate(items):
        y = 140 + i * 115
        sk.text(x0, y - 38, n, 26, INK, "lm")
        if b:
            sk.rect(X(a), y - 14, X(b) - X(a), 28, c, 2, fill=PALE[c])
            sk.text(X(b) + 14, y, "0.54〜0.57", 26, c, "lm")
        else:
            sk.ellipse(X(a), y, 12, 12, c, 3, fill=c)
            sk.text(X(0.5) + 14, y, f"{a:.3f}", 26, c, "lm")
    sk.line(x0, 470, x1, 470, INK, 3)
    for v in [0.45, 0.50, 0.55, 0.60]:
        sk.text(X(v), 502, f"{v:.2f}", 24, INK, "mm")
    sk.text(X(0.5), 545, "0.5 = 見分けない", 24, GRAY, "mm")
    bx = 840
    sk.text(bx, 24, "止まりの確率の分かれ方（CoAuthor）", 30, INK, "lm")
    bars = [("0.015 未満", 75.0, TEAL), ("その間", 20.2, GRAY), ("0.6 以上", 4.8, ORANGE)]
    base = 450
    for i, (n, v, c) in enumerate(bars):
        x = bx + 20 + i * 215
        h = v / 80 * 330
        sk.rect(x, base - h, 160, h, c, 3, fill=PALE[c])
        sk.text(x + 80, base - h - 28, f"{v:g}%", 30, c, "mm")
        sk.text(x + 80, base + 32, n, 26, INK, "mm")
    sk.line(bx, base, 1490, base, INK, 3)
    sk.text(1170, 535, "二つの山・二値に近い量", 26, GRAY, "mm")
    sk.save(OUT + "chart_learners.png")


def chart_stall():
    sk = Sk(1500, 480, 223)
    sk.text(10, 26, "止まりから再開までの中央値", 30, INK, "lm")
    bars = [("CoAuthor", 6.5, PLUM), ("KLiCKe", 14.5, OLIVE), ("本人の記録", 90.0, ORANGE)]
    x0, x1 = 330, 1250

    def W(v):
        return v / 100 * (x1 - x0)
    for i, (n, v, c) in enumerate(bars):
        y = 70 + i * 100
        sk.text(x0 - 20, y + 34, n, 30, INK, "rm")
        sk.rect(x0, y, W(v), 68, c, 3, fill=PALE[c])
        sk.text(x0 + W(v) + 18, y + 34, f"{v:g} 秒", 32, c, "lm")
    sk.line(x0, 55, x0, 375, INK, 3)
    y = 400
    sk.text(x0 - 20, y + 32, "沈黙だけの止まり", 28, INK, "rm")
    sk.rect(x0, y, 1160, 64, GRAY, 2, fill=WHITE)
    sk.rect(x0, y, 1160 * 0.62, 64, TEAL, 3, fill=PALE[TEAL])
    sk.text(x0 + 1160 * 0.31, y + 32, "62% は最中に操作が入る（KLiCKe）", 28, INK, "mm")
    sk.save(OUT + "chart_stall.png")


def chart_alarm():
    sk = Sk(1500, 400, 225)
    sk.text(10, 26, "知らせ 100 回のうち、本当に止まりになったもの（KLiCKe）", 30, INK, "lm")
    for k in range(100):
        r, cidx = divmod(k, 25)
        x = 30 + cidx * 42
        y = 100 + r * 66
        if k < 6:
            sk.ellipse(x, y, 17, 17, ORANGE, 3, fill=ORANGE)
        elif k < 9:
            sk.ellipse(x, y, 17, 17, ORANGE, 3, fill=PALE[ORANGE])
        else:
            sk.ellipse(x, y, 17, 17, GRAY, 2, fill=WHITE, jit=0.6)
    sk.text(1300, 125, "6.3〜9.1 回", 44, ORANGE, "mm")
    sk.text(1300, 185, "残りは空振り", 32, GRAY, "mm")
    sk.text(1300, 260, "1 時間に", 28, INK, "mm")
    sk.text(1300, 305, "124〜182 回鳴る", 32, INK, "mm")
    sk.text(10, 380, "休止が本人の基準の 0.5・0.75 倍に届いた時点で知らせる案", 26, GRAY, "lm")
    sk.save(OUT + "chart_alarm.png")


def chart_enja():
    sk = Sk(1500, 380, 227)
    x0, x1 = 400, 1120

    def X(v):
        return x0 + v / 70 * (x1 - x0)
    bars = [("事象の種類で照合", 51.6, (39.3, 63.5), PLUM), ("全体の長さだけ", 11.9, None, INDIGO),
            ("偶然", 7.9, None, GRAY)]
    for i, (n, v, ci, c) in enumerate(bars):
        y = 20 + i * 105
        sk.text(x0 - 20, y + 36, n, 30, INK, "rm")
        sk.rect(x0, y, X(v) - x0, 72, c, 3, fill=PALE[c])
        if ci:
            sk.line(X(ci[0]), y + 36, X(ci[1]), y + 36, INK, 3, jit=0.2, passes=1)
            sk.line(X(ci[0]), y + 20, X(ci[0]), y + 52, INK, 3, passes=1)
            sk.line(X(ci[1]), y + 20, X(ci[1]), y + 52, INK, 3, passes=1)
            sk.text(X(ci[1]) + 18, y + 20, f"{v}%", 36, c, "lm")
            sk.text(X(ci[1]) + 18, y + 58, f"区間 {ci[0]}〜{ci[1]}%", 24, c, "lm")
        else:
            sk.text(X(v) + 18, y + 36, f"{v}%", 32, c, "lm")
    sk.line(x0, 10, x0, 330, INK, 3)
    sk.text(x0, 362, "12〜13 個の候補から本物の訳を当てた割合（文字列はすべて除いた）", 25, GRAY, "lm")
    sk.save(OUT + "chart_enja.png")


def chart_ime():
    sk = Sk(1500, 440, 229)
    base, top = 350, 60

    def H(v):
        return v * (base - top)
    groups = [("Windows", [("recall", 0.89, "約 0.89"), ("precision", 0.76, "0.76")]),
              ("macOS", [("recall", 0.905, "約 0.90〜0.91"), ("precision", 0.91, "約 0.91")])]
    x = 60
    for g, bars in groups:
        for k, (n, v, lab) in enumerate(bars):
            c = INDIGO if n == "recall" else TEAL
            sk.rect(x, base - H(v), 170, H(v), c, 3, fill=PALE[c])
            sk.text(x + 85, base - H(v) - 26, lab, 26, c, "mm")
            sk.text(x + 85, base + 28, n, 24, INK, "mm")
            x += 195
        sk.text(x - 195 - 12, base + 70, g, 30, INK, "mm")
        x += 110
    sk.line(30, base, 1000, base, INK, 3)
    sk.text(1050, 140, "変換の区間を", 34, INK, "lm")
    sk.text(1050, 190, "約 9 割拾った", 34, INK, "lm")
    sk.text(1050, 260, "合成入力・事前登録", 26, GRAY, "lm")
    sk.text(1050, 300, "人の打鍵では未検査", 26, GRAY, "lm")
    sk.save(OUT + "chart_ime.png")


def chart_person():
    sk = Sk(1500, 330, 231)
    sk.text(10, 26, "本人に合わせた学習の上積み（共通の学習との差・nats/記号）", 30, INK, "lm")
    x0, x1 = 400, 1180

    def X(v):
        return x0 + v / 0.22 * (x1 - x0)
    sk.text(x0 - 20, 125, "ふつうの HMM", 30, INK, "rm")
    sk.rect(x0, 90, X(0.14) - x0, 70, ORANGE, 3, fill=PALE[ORANGE])
    sk.hatch(X(0.14), 90, X(0.19) - X(0.14), 70, ORANGE, 10, 2)
    sk.rect(X(0.14), 90, X(0.19) - X(0.14), 70, ORANGE, 2)
    sk.text(X(0.19) + 18, 125, "+0.14〜+0.19", 32, ORANGE, "lm")
    sk.text(x0 - 20, 245, "前の記号を入れた構造", 30, INK, "rm")
    sk.rect(x0, 210, max(X(0.006) - x0, 6), 70, TEAL, 3, fill=PALE[TEAL])
    sk.text(X(0.006) + 24, 245, "0.006 以下（ほぼ消えた）", 32, TEAL, "lm")
    sk.line(x0, 70, x0, 300, INK, 3)
    sk.save(OUT + "chart_person.png")


# ---------------------------------------------------------------- 先行
def fig_prior():
    """既にあることと見つからなかったことを、どの検査の組み合わせかで並べる"""
    sk = Sk(1500, 640, 233)
    cols = [("予測", INDIGO), ("定義", OLIVE), ("漏れ", PLUM)]
    items = [("状態の推定と本人・属性の推測を並べる評価", [0, 2], True),
             ("有用性と漏れで粒度を選ぶ道具", [0, 2], True),
             ("休止の閾値で有意性が変わること", [1], True),
             ("中身の照合を状態の推定と並べる", [0, 2], False),
             ("打鍵の止まりの定義を振った外部の研究", [1], False),
             ("3 つの検査を同じ観測で行う手順", [0, 1, 2], False)]
    x0, cw = 840, 110
    for j, (n, c) in enumerate(cols):
        sk.text(x0 + j * cw + cw / 2, 28, n, 28, c, "mm")
    for i, (n, on, known) in enumerate(items):
        y = 62 + i * 96
        c = GRAY if known else TEAL
        sk.rect(6, y, 1488, 84, c, 2, fill=CREAM if known else PALE[TEAL], jit=0.5)
        sk.text(26, y + 42, n, 28, INK, "lm")
        for j in range(3):
            cx = x0 + j * cw + cw / 2
            if j in on:
                sk.ellipse(cx, y + 42, 17, 17, cols[j][1], 3, fill=cols[j][1])
            else:
                sk.ellipse(cx, y + 42, 17, 17, GRAY, 2, fill=WHITE, jit=0.5)
        sk.text(1475, y + 42, "既にある" if known else "見つからなかった", 27, GRAY if known else TEAL, "rm")
    sk.save(OUT + "fig_prior.png")


# ---------------------------------------------------------------- 技術スタック
def fig_stack():
    sk = Sk(1500, 420, 235)
    layers = [("画面", "React 19・TypeScript 5.8・Vite 7", PLUM),
              ("アプリの枠", "Tauri 2.0・capabilities・IPC", INDIGO),
              ("分析と記録", "Rust・tracing・anyhow・crossbeam", TEAL),
              ("入力（OS ごと）", "windows crate ／ core-graphics", ORANGE)]
    for i, (n, d, c) in enumerate(layers):
        y = 6 + i * 102
        sk.rect(6, y, 1120, 92, c, 3, fill=PALE[c])
        sk.text(30, y + 46, n, 30, INK, "lm")
        sk.text(1100, y + 46, d, 27, INK, "rm")
    sk.rect(1145, 6, 349, 398, OLIVE, 3, fill=PALE[OLIVE])
    sk.text(1320, 70, "Python", 34, INK, "mm")
    sk.text(1320, 140, "公開データの分析", 26, INK, "mm")
    sk.text(1320, 185, "推定の改良の試験", 26, INK, "mm")
    sk.text(1320, 300, "アプリの外で回す", 24, GRAY, "mm")
    sk.save(OUT + "fig_stack.png")


def fig_ime_keep():
    """変換の間も推定を止めず、変換の区間は別の行に書く"""
    sk = Sk(1500, 470, 237)
    import random
    r = random.Random(7)
    conv = [(330, 560), (820, 1010), (1180, 1330)]
    sk.text(10, 30, "打鍵", 30, INK, "lm")
    sk.line(170, 80, 1490, 80, INK, 3)
    for a, b in conv:
        sk.blob_rect(a, 45, b - a, 70, PALE[INDIGO])
    x = 180
    while x < 1480:
        sk.line(x, 55, x, 80, INK, 3, jit=0.3, passes=1)
        x += r.choice([18, 22, 26, 30, 40, 55])
    sk.text(445, 135, "変換の区間（例）", 24, INDIGO, "mm")
    sk.text(10, 215, "推定", 30, INK, "lm")
    for k in range(0, 33):
        xx = 180 + k * 40
        sk.rect(xx, 190, 30, 50, TEAL, 2, fill=PALE[TEAL], jit=0.5)
    sk.text(830, 275, "1 秒ごとの推定は、変換の間も止めない（外すと日本語の窓の約 56〜60% が消える）", 26, TEAL, "mm")
    sk.text(10, 370, "区間の行", 30, INK, "lm")
    for i, (a, b) in enumerate(conv):
        sk.rect(a, 335, b - a, 70, INDIGO, 3, fill=WHITE)
        sk.text((a + b) / 2, 370, "1 回 = 1 行", 24, INK, "mm")
    sk.text(830, 445, "長さ・矢印キーの回数・取り消したか。後から変換の間だけを除いた集計もできる", 25, GRAY, "mm")
    sk.save(OUT + "fig_ime_keep.png")


ALL = [fig_map, fig_outlets, fig_order, fig_machines, fig_stats, fig_public, fig_outputs, fig_feasibility,
       fig_data, chart_multiverse, chart_learners, chart_stall, chart_alarm, chart_enja, chart_ime, chart_person,
       fig_prior, fig_stack, fig_ime_keep]

if __name__ == "__main__":
    for f in ALL:
        f()
    print("ok", len(ALL))
