"""詳細版・知見版・技術版で使う図とグラフ（sketch.py の手描き風の線で描く）。

図の中の数値は、research-positioning §1.4・core-and-edge-material（と補足）・IME 論文・
Zenodo の API（2026-11-15 に取得）から写した。例の値（変換の長さなど）は「例」と書いた。
実行: python3 figs.py（img/ に fig_*.png と chart_*.png を書く）"""
import math

from sketch import (Sk, INK, ORANGE, TEAL, INDIGO, OLIVE, PLUM, GRAY, CREAM, WHITE, OUT, cloud)

PALE = {ORANGE: (247, 228, 214), TEAL: (214, 237, 230), INDIGO: (222, 226, 242),
        OLIVE: (228, 234, 219), PLUM: (238, 226, 235), GRAY: (236, 233, 228)}


def node(sk, x, y, w, h, label, col, size=28, sub=None, sub_size=21, fill=True):
    sk.rect(x, y, w, h, col, 3, fill=PALE.get(col, WHITE) if fill else WHITE)
    if sub:
        sk.text(x + w / 2, y + h / 2 - sub_size * 0.75, label, size, INK, "mm")
        sk.text(x + w / 2, y + h / 2 + size * 0.7, sub, sub_size, GRAY, "mm")
    else:
        sk.text(x + w / 2, y + h / 2, label, size, INK, "mm")


def key(sk, x, y, s, label, col=INK, size=24, w=None):
    w = w or s
    sk.rect(x, y, w, s, col, 3, fill=WHITE, jit=0.8)
    sk.text(x + w / 2, y + s / 2, label, size, col, "mm")


def harrow(sk, x1, y, x2, col=GRAY, width=4):
    sk.arrow(x1, y, x2, y, col, width, 16)


# ---------------------------------------------------------------- IME
def ime_flow():
    """1 回の変換で、画面に出ることと GSE が書くこと"""
    sk = Sk(1500, 660, 101)
    sk.text(20, 30, "画面で起きること", 30, INDIGO)
    keys = list("nihongo")
    x = 30
    for k in keys:
        key(sk, x, 80, 62, k, INK, 28)
        x += 72
    harrow(sk, x + 6, 111, x + 66)
    sk.text(x + 150, 92, "にほんご", 36, INK, "mm")
    sk.line(x + 82, 122, x + 218, 122, INDIGO, 3, passes=1)
    sk.text(x + 150, 150, "読み（未確定）", 20, GRAY, "mm")
    x2 = x + 240
    key(sk, x2, 80, 62, "Space", ORANGE, 19, w=110)
    harrow(sk, x2 + 118, 111, x2 + 168)
    sk.rect(x2 + 178, 62, 160, 120, INDIGO, 3, fill=WHITE)
    sk.text(x2 + 258, 92, "日本語", 28, INK, "mm")
    sk.line(x2 + 200, 130, x2 + 318, 130, GRAY, 3, passes=1)
    sk.line(x2 + 200, 156, x2 + 300, 156, GRAY, 3, passes=1)
    sk.text(x2 + 258, 200, "候補", 20, GRAY, "mm")
    harrow(sk, x2 + 348, 111, x2 + 398)
    key(sk, x2 + 408, 80, 62, "Enter", TEAL, 19, w=110)
    sk.text(x2 + 463, 172, "確定", 20, GRAY, "mm")

    # GSE が書くこと
    sk.text(20, 236, "GSE が書くこと", 30, TEAL)
    y0 = 400
    sk.line(30, y0, 1460, y0, INK, 3)
    xs = [60 + i * 72 for i in range(7)]
    for xx in xs:
        sk.line(xx, y0 - 46, xx, y0, TEAL, 5, jit=0.4, passes=1)
    sk.text(xs[3], y0 - 74, "文字のキー ×7（種類と時刻だけ）", 22, INK, "mm")
    xs_sp = x2 + 55
    xs_en = x2 + 463
    sk.line(xs_sp, y0 - 46, xs_sp, y0, ORANGE, 5, jit=0.4, passes=1)
    sk.text(xs_sp, y0 - 74, "変換のキー", 22, INK, "mm")
    sk.line(xs_en, y0 - 46, xs_en, y0, TEAL, 5, jit=0.4, passes=1)
    sk.text(xs_en, y0 - 74, "確定のキー", 22, INK, "mm")
    # 変換の区間
    sk.rect(xs[0], y0 + 34, xs_en - xs[0], 54, INDIGO, 3, fill=PALE[INDIGO])
    sk.text((xs[0] + xs_en) / 2, y0 + 61, "変換 1 回 = 1 行: 長さ・矢印キーの回数・取り消したか", 24, INK, "mm")
    sk.text((xs[0] + xs_en) / 2, y0 + 118, "（Windows は IME の窓の表示と隠れ、macOS は打鍵から区間を決める）", 20, GRAY, "mm")
    # 書かないもの
    bx, by = 1260, 470
    sk.rect(bx, by, 210, 120, ORANGE, 3, fill=WHITE)
    sk.text(bx + 105, by + 38, "にほんご", 26, GRAY, "mm")
    sk.text(bx + 105, by + 82, "日本語", 26, GRAY, "mm")
    sk.line(bx + 14, by + 12, bx + 196, by + 108, ORANGE, 6)
    sk.line(bx + 196, by + 12, bx + 14, by + 108, ORANGE, 6)
    sk.text(bx + 105, by + 150, "読みも結果も書かない", 21, ORANGE, "mm")
    sk.save(OUT + "fig_ime_flow.png")


def ime_why():
    """英語と日本語 IME の打鍵の列の違い"""
    sk = Sk(1500, 620, 103)
    rows = [("英語の打鍵", INDIGO, [0, 30, 55, 85, 110, 150, 175, 200, 260, 285, 310, 340, 365, 400], []),
            ("日本語 IME の打鍵", ORANGE, [0, 28, 52, 78, 102, 126, 150], [(176, "Space", ORANGE), (420, "Enter", TEAL)])]
    for r, (lab, col, ts, spec) in enumerate(rows):
        y = 150 + r * 250
        sk.text(20, y - 120, lab, 30, col)
        sk.line(40, y, 1460, y, INK, 3)
        for t in ts:
            xx = 60 + t * 2.2
            sk.line(xx, y - 40, xx, y, col, 5, jit=0.4, passes=1)
        for t, name, c2 in spec:
            xx = 60 + t * 2.2
            sk.line(xx, y - 40, xx, y, c2, 7, jit=0.4, passes=1)
            sk.text(xx, y + 30, name, 20, c2, "mm")
        if r == 1:
            a, b = 60 + 180 * 2.2, 60 + 415 * 2.2
            sk.hatch(a, y - 70, b - a, 60, INDIGO, gap=14, width=2)
            sk.text((a + b) / 2, y - 90, "候補を選ぶ間（打鍵が止まる）", 24, INDIGO, "mm")
            for t in [440, 466, 490, 514]:
                xx = 60 + t * 2.2
                sk.line(xx, y - 40, xx, y, col, 5, jit=0.4, passes=1)
    sk.text(40, 530, "打鍵の列だけを見ると、変換の間の休止と、作業の止まりの休止は区別がつかない。", 26, INK)
    sk.text(40, 575, "Space と Enter も、英語では空白と改行、日本語 IME では変換と確定になる。", 26, INK)
    sk.save(OUT + "fig_ime_why.png")


def ime_os():
    """Windows と macOS で変換の区間をどう決めるか"""
    sk = Sk(1500, 600, 105)
    # Windows
    sk.text(30, 40, "Windows: IME の窓の表示と隠れを追う", 30, INDIGO)
    sk.rect(60, 100, 300, 210, INK, 3, fill=WHITE)
    sk.text(210, 140, "アプリの窓", 22, GRAY, "mm")
    sk.rect(150, 180, 170, 110, INDIGO, 3, fill=PALE[INDIGO])
    for k in range(3):
        sk.line(170, 210 + k * 26, 296, 210 + k * 26, GRAY, 3, passes=1)
    sk.text(235, 330, "IME の候補の窓", 20, INDIGO, "mm")
    harrow(sk, 380, 200, 470, INDIGO)
    node(sk, 480, 140, 230, 120, "WinEvent", INDIGO, 28, "プロセスの外で受ける", 19)
    sk.text(370, 410, "表示", 22, TEAL, "mm")
    sk.text(650, 410, "隠れ", 22, ORANGE, "mm")
    sk.line(60, 460, 720, 460, INK, 3)
    sk.arrow(370, 440, 370, 470, TEAL, 5, 12)
    sk.arrow(650, 470, 650, 440, ORANGE, 5, 12)
    sk.rect(370, 480, 280, 44, INDIGO, 3, fill=PALE[INDIGO])
    sk.text(510, 502, "変換の区間", 22, INK, "mm")
    sk.text(390, 565, "コールバックの引数に文字列が無い", 22, GRAY, "mm")

    # macOS
    sk.line(760, 40, 760, 570, GRAY, 2, passes=1)
    sk.text(790, 40, "macOS: 打鍵から推す（状態機械）", 30, TEAL)
    st = [(800, 120, "直接入力"), (1130, 120, "読みの入力"), (1130, 330, "候補の表示"), (800, 330, "確定・取り消し")]
    for x, y, lab in st:
        node(sk, x, y, 250, 100, lab, TEAL, 26)
    sk.arrow(1055, 170, 1125, 170, INK, 4, 14)
    sk.text(1090, 140, "文字", 20, GRAY, "mm")
    sk.arrow(1255, 225, 1255, 325, INK, 4, 14)
    sk.text(1320, 275, "Space", 20, GRAY, "mm")
    sk.arrow(1125, 380, 1055, 380, INK, 4, 14)
    sk.text(1090, 452, "Enter・Esc", 20, GRAY, "mm")
    sk.arrow(925, 325, 925, 225, INK, 4, 14)
    sk.text(860, 275, "次の文字", 20, GRAY, "mm")
    sk.arrow(1150, 225, 1060, 325, INK, 3, 12)
    sk.text(1150, 290, "Enter", 18, GRAY, "mm")
    sk.text(790, 480, "OS に変換を知らせる口が見つかっていないため。", 22, GRAY)
    sk.text(790, 520, "マウスで候補を選んだ変換は、次の変換と 1 行にまとまる。", 22, GRAY)
    sk.save(OUT + "fig_ime_os.png")


# ---------------------------------------------------------------- 全体・スレッド
def threads():
    sk = Sk(1500, 600, 107)
    node(sk, 20, 40, 250, 110, "Hook", ORANGE, 30, "押下の時刻と種類", 18)
    node(sk, 20, 250, 250, 110, "IME", INDIGO, 30, "変換の区間", 18)
    # 打鍵の channel
    sk.rect(330, 55, 180, 80, GRAY, 3, fill=CREAM)
    sk.text(420, 95, "channel", 24, INK, "mm")
    harrow(sk, 275, 95, 325, ORANGE)
    harrow(sk, 515, 95, 600, ORANGE)
    node(sk, 610, 30, 290, 130, "Analysis", TEAL, 30, "1 秒ごとに特徴量と推定", 18)
    sk.arrow(275, 290, 600, 130, INDIGO, 4, 14)
    harrow(sk, 905, 95, 1000, TEAL)
    node(sk, 1010, 30, 240, 130, "FeatSnapshot", TEAL, 26, "最新の推定", 18)
    harrow(sk, 1255, 95, 1310, PLUM)
    node(sk, 1320, 30, 160, 130, "画面", PLUM, 28, "IPC", 18)
    # 記録の channel
    sk.rect(560, 330, 400, 90, GRAY, 3, fill=CREAM)
    sk.text(760, 375, "記録の channel（上限 512）", 24, INK, "mm")
    sk.arrow(755, 165, 755, 325, TEAL, 4, 14)
    sk.arrow(275, 320, 555, 370, INDIGO, 4, 14)
    harrow(sk, 965, 375, 1060, OLIVE)
    node(sk, 1070, 310, 200, 130, "Logger", OLIVE, 30, "5 秒ごとに書く", 18)
    harrow(sk, 1275, 375, 1320, OLIVE)
    node(sk, 1325, 310, 160, 130, "NDJSON", OLIVE, 24, "手元", 18)
    sk.text(20, 520, "フックの中では Atomic の操作と channel への送信だけ（重い仕事をしない）。", 24, INK, "ls")
    sk.text(20, 570, "IME の区間は分析と記録の両方へ。推定は変換の間も止めない。", 24, GRAY, "ls")
    sk.save(OUT + "fig_threads.png")


def features():
    sk = Sk(1500, 520, 109)
    sk.text(20, 30, "30 秒の窓", 28, ORANGE)
    sk.line(30, 170, 700, 170, INK, 3)
    import random
    r = random.Random(4)
    t = 40
    while t < 690:
        sk.line(t, 135, t, 170, INK, 3, jit=0.3, passes=1)
        t += r.choice([10, 12, 14, 18, 22, 60, 12, 10, 90])
    sk.rect(300, 105, 380, 90, ORANGE, 4)
    sk.text(490, 225, "← 1 秒ずつ進める", 22, GRAY, "mm")
    fl = ["間隔の中央値", "修正の率", "バーストの長さ", "2 秒以上の休止", "削除の後の休止"]
    for i, f in enumerate(fl):
        sk.rect(40 + (i % 3) * 225, 280 + (i // 3) * 80, 210, 60, ORANGE, 3, fill=PALE[ORANGE])
        sk.text(145 + (i % 3) * 225, 310 + (i // 3) * 80, f, 21, INK, "mm")
    sk.arrow(720, 330, 800, 330, GRAY, 5, 16)
    # 2 軸
    ox, oy = 840, 460
    sk.arrow(ox, oy, ox + 330, oy, INK, 3, 12)
    sk.arrow(ox, oy, ox, oy - 360, INK, 3, 12)
    sk.text(ox + 300, oy + 32, "摩擦", 22, INK, "mm")
    sk.text(ox - 34, oy - 330, "前進", 22, INK, "mm")
    for k in range(1, 5):
        sk.line(ox + k * 62, oy, ox + k * 62, oy - 320, GRAY, 1, passes=1)
        sk.line(ox, oy - k * 62, ox + 310, oy - k * 62, GRAY, 1, passes=1)
    sk.ellipse(ox + 160, oy - 210, 12, 12, TEAL, 3, fill=TEAL)
    sk.text(ox + 165, 50, "2 つの軸 → 26 のビン", 24, TEAL, "mm")
    sk.arrow(1200, 300, 1270, 300, GRAY, 5, 16)
    node(sk, 1280, 220, 200, 160, "HMM", INDIGO, 32, "前向きの計算", 19)
    sk.save(OUT + "fig_features.png")


def record_flow():
    sk = Sk(1500, 470, 111)
    steps = [("打鍵", ORANGE, "時刻と種類"), ("NDJSON", TEAL, "手元・本人だけ"), ("48 時間の猶予", INDIGO, "削除が効く"),
             ("匿名化", OLIVE, ""), ("age で暗号化", PLUM, "提出")]
    x = 20
    for i, (n, c, d) in enumerate(steps):
        node(sk, x, 60, 245, 120, n, c, 27, d or None, 19)
        if i < len(steps) - 1:
            harrow(sk, x + 250, 120, x + 295)
        x += 300
    # 一時停止・削除
    sk.text(560, 230, "本人がいつでも一時停止・区間の削除", 22, GRAY, "lm")
    # 集計
    sk.arrow(345, 185, 345, 330, TEAL, 4, 14)
    node(sk, 200, 340, 290, 110, "gse-replay", TEAL, 27, "集計（metrics.json）", 19)
    harrow(sk, 495, 395, 600, TEAL)
    node(sk, 610, 340, 330, 110, "共有するのは集計だけ", TEAL, 25, "データの repo（非公開）", 19)
    sk.rect(1010, 330, 460, 130, ORANGE, 3, fill=WHITE)
    sk.text(1240, 365, "外に出さない", 26, ORANGE, "mm")
    sk.text(1240, 410, "NDJSON・キーの種類の列", 22, INK, "mm")
    sk.text(1240, 440, "外部の LLM にも送らない", 20, GRAY, "mm")
    sk.save(OUT + "fig_record.png")


def replay():
    sk = Sk(1500, 420, 113)
    node(sk, 20, 140, 260, 140, "ゴールデンの記録", ORANGE, 25, "固定した NDJSON", 19)
    harrow(sk, 290, 210, 380)
    node(sk, 390, 140, 260, 140, "gse-replay", TEAL, 28, "記録を再生", 19)
    harrow(sk, 660, 210, 750)
    sk.rect(760, 110, 300, 200, INDIGO, 3, fill=WHITE)
    for k in range(5):
        sk.line(785, 150 + k * 32, 1035, 150 + k * 32, INDIGO, 3, passes=1)
    sk.text(910, 335, "1 秒ごとの推定の列", 21, INDIGO, "mm")
    sk.text(1130, 210, "=", 60, INK, "mm")
    sk.rect(1190, 110, 290, 200, GRAY, 3, fill=WHITE)
    for k in range(5):
        sk.line(1215, 150 + k * 32, 1455, 150 + k * 32, GRAY, 3, passes=1)
    sk.text(1335, 335, "保存した値", 21, GRAY, "mm")
    sk.text(1125, 80, "byte で一致", 22, TEAL, "mm")
    sk.text(20, 395, "推定を変えたら HMM の版を上げ、ゴールデンを作り直して差が意図どおりかを記録する。", 22, GRAY, "ls")
    sk.save(OUT + "fig_replay.png")


def stage1():
    sk = Sk(1500, 420, 115)
    steps = [("無作為の枠", ORANGE), ("層化の枠", TEAL), ("日の問い", INDIGO)]
    x = 40
    for i, (n, c) in enumerate(steps):
        node(sk, x, 120, 250, 110, n, c, 28)
        harrow(sk, x + 255, 175, x + 310)
        x += 320
    sk.rect(x, 90, 300, 170, PLUM, 3, fill=WHITE)
    sk.text(x + 150, 135, "問いのカード", 26, PLUM, "mm")
    sk.text(x + 150, 185, "1〜5 と 6 択", 22, INK, "mm")
    sk.text(x + 150, 225, "答えなくてよい", 20, GRAY, "mm")
    # 推定は入れない
    node(sk, 360, 300, 330, 90, "推定の出力", GRAY, 26, fill=False)
    sk.arrow(525, 296, 525, 240, GRAY, 4, 14)
    sk.cross(525, 270, 40, ORANGE, 6)
    sk.text(720, 345, "調停器は推定の出力を入力に持たない（純粋な関数・1 秒ごと）", 22, INK, "lm")
    sk.save(OUT + "fig_stage1.png")


def tool():
    sk = Sk(1500, 600, 117)
    node(sk, 20, 190, 260, 170, "同じ記録", ORANGE, 30, "時刻とキーの種類", 20)
    checks = [("予測", INDIGO, "同等の帯と区間"), ("定義", OLIVE, "定義と調整を振る"), ("漏れ", PLUM, "候補の照合")]
    for i, (n, c, d) in enumerate(checks):
        y = 40 + i * 170
        sk.arrow(285, 275, 400, y + 60, GRAY, 4, 14)
        node(sk, 410, y, 300, 120, n, c, 30, d, 20)
        sk.arrow(715, y + 60, 830, 275, GRAY, 4, 14)
    # 4 面の地図
    mx, my, s = 850, 60, 230
    faces = [("読める所", TEAL), ("読めない所", ORANGE), ("漏れる所", PLUM), ("定義しだいの所", INDIGO)]
    for i, (n, c) in enumerate(faces):
        x = mx + (i % 2) * (s + 20)
        y = my + (i // 2) * (s + 20)
        sk.rect(x, y, s, s, c, 3, fill=PALE[c])
        sk.text(x + s / 2, y + s / 2, n, 26, INK, "mm")
    sk.text(mx + s + 10, 585, "4 つの面の地図（足りない面は「判定不能」）", 22, GRAY, "mb")
    sk.save(OUT + "fig_tool.png")


# ---------------------------------------------------------------- グラフ
def chart_auc():
    """推定器の上がりの AUC（点と区間）・同等の帯"""
    sk = Sk(1500, 560, 119)
    x0, x1 = 300, 1440
    lo, hi = 0.40, 0.60

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    top, bot = 40, 470
    sk.blob_rect(X(0.45), top, X(0.55) - X(0.45), bot - top, PALE[TEAL])
    sk.text(X(0.50), top + 22, "同等の帯 0.45〜0.55（CS1 で事前登録）", 22, TEAL, "mm")
    sk.line(X(0.5), top + 40, X(0.5), bot, GRAY, 2, passes=1)
    rows = [("CS1（事前登録）", [(0.489, 0.479, 0.4995), (0.487, 0.476, 0.497)], INDIGO),
            ("KLiCKe", [(0.512, None, None), (0.518, None, None)], OLIVE),
            ("CoAuthor", [(0.503, None, None), (0.493, None, None)], PLUM)]
    for i, (lab, pts, c) in enumerate(rows):
        y = 120 + i * 120
        sk.text(30, y + 18, lab, 26, INK, "lm")
        for j, (v, a, b) in enumerate(pts):
            yy = y + j * 40
            if a is not None:
                sk.line(X(a), yy, X(b), yy, c, 4, jit=0.3, passes=1)
            sk.ellipse(X(v), yy, 10, 10, c, 3, fill=c)
            sk.text(max(X(v), X(b) if b else 0) + 24, yy, f"{v:.3f}", 20, c, "lm")
    sk.line(x0, bot, x1, bot, INK, 3)
    for v in [0.40, 0.45, 0.50, 0.55, 0.60]:
        sk.line(X(v), bot, X(v), bot + 12, INK, 3, passes=1)
        sk.text(X(v), bot + 34, f"{v:.2f}", 20, INK, "mm")
    sk.text((x0 + x1) / 2, bot + 72, "AUC（0.5 は見分けない）。各データの 2 点は推定器の 2 つの信号。CS1 の線は 95% 区間", 22, GRAY, "mm")
    sk.save(OUT + "chart_auc.png")


def chart_match():
    """キーの種類の列からの候補の照合"""
    sk = Sk(1500, 560, 121)
    base, top = 470, 70

    def H(v):
        return (base - top) * v
    groups = [("10 個の候補", [(0.902, "macOS（オフ）・Windows", ORANGE), (0.907, "macOS（オン）", PLUM), (0.10, "偶然", GRAY)]),
              ("100 個の候補", [(0.421, "macOS（オフ）・Windows", ORANGE), (0.435, "macOS（オン）", PLUM), (0.01, "偶然", GRAY)])]
    x = 120
    for g, bars in groups:
        for v, lab, c in bars:
            h = max(H(v), 4)
            sk.rect(x, base - h, 150, h, c, 3, fill=PALE.get(c, WHITE))
            sk.text(x + 75, base - h - 26, f"{v:.3f}" if v > 0.2 else f"{v:.2f}", 24, c, "mm")
            x += 175
        sk.text(x - 175 * 2 + 75 - 175 / 2 + 87, base + 40, g, 26, INK, "mm")
        x += 120
    sk.line(80, base, 1440, base, INK, 3)
    sk.text(80, 30, "正しく当てた割合", 22, GRAY, "lm")
    # 凡例
    lx = 1260
    for i, (lab, c) in enumerate([("macOS オフ・Win", ORANGE), ("macOS オン", PLUM), ("偶然の水準", GRAY)]):
        sk.rect(lx - 10, 110 + i * 50, 28, 28, c, 2, fill=PALE.get(c, WHITE))
        sk.text(lx + 30, 124 + i * 50, lab, 20, INK, "lm")
    sk.save(OUT + "chart_match.png")


ZENODO = [  # (名前, 種類, 一意の閲覧, 一意のダウンロード) 2026-11-15 に Zenodo の API で取得
    ("IME の観測: 合成入力の記録", "データ", 24, 159),
    ("IME の観測: プレプリント", "論文", 8, 7),
    ("論文 1: プレプリント", "論文", 5, 8),
    ("論文 1: コードと集計", "コード", 13, 4),
    ("論文 2: コードと集計", "コード", 3, 1),
    ("IME の観測: ロガーと検証キット", "コード", 28, 0),
]


def chart_zenodo():
    """Zenodo の一意の閲覧と一意のダウンロード（横棒は閲覧とダウンロードを並べる）"""
    sk = Sk(1500, 600, 123)
    x0, x1 = 600, 1380
    vmax = 160
    sk.text(x0, 24, "■ 一意の閲覧", 22, GRAY, "lm")
    sk.text(x0 + 220, 24, "■ 一意のダウンロード", 22, TEAL, "lm")
    for i, (n, kind, uv, ud) in enumerate(ZENODO):
        y = 60 + i * 84
        sk.text(30, y + 30, f"{n}（{kind}）", 23, INK, "lm")
        for k, (v, c) in enumerate([(uv, GRAY), (ud, TEAL)]):
            yy = y + k * 30
            w = max((x1 - x0) * v / vmax, 3)
            sk.blob_rect(x0, yy, w, 24, PALE[c])
            sk.line(x0 + w, yy, x0 + w, yy + 24, c, 3, passes=1)
            sk.text(x0 + w + 14, yy + 12, f"{v}", 22, c, "lm")
    sk.line(x0, 50, x0, 570, INK, 3)
    sk.text(30, 585, "2026-11-15 時点・Zenodo の集計のまま。合成入力の記録は 38 個のファイルからなる。", 21, GRAY, "lm")
    sk.save(OUT + "chart_zenodo.png")


RELEASE = [  # (名前, 指標の中央の相関 ρ, 最も強い攻撃の正答・偶然の何倍か N=1,000, 札の向き) 加工と照合の論文の原稿 Table 4(a)
    ("文字と数字を隠す（公開で使われた形）", 1.00, 1000, "u"),
    ("キーの種類だけ", 0.92, 867, "d"),
    ("時刻を 1 秒に丸める", 0.09, 867, "r"),
    ("区切りをまとめる", 0.63, 360, "l"),
    ("押下を 10% 間引く", 0.85, 702, "l2"),
    ("25% 間引く", 0.81, 143, "l"),
    ("50% 間引く", 0.70, 22, "l"),
    ("まとまりの値だけ（粗さ 1）", 0.0, 405, "r"),
    ("粗さ 2", 0.0, 44, "r"),
    ("粗さ 4", 0.0, 3.5, "r"),
    ("粗さ 8", 0.0, 1.4, "r"),
]


def chart_release():
    """公開の前の加工: 指標が残るか（横）と当たる率（縦・偶然の何倍かの対数）"""
    sk = Sk(1500, 640, 125)
    x0, x1, y0, y1 = 220, 1320, 540, 60

    def X(v):
        return x0 + v * (x1 - x0)

    def Y(m):
        return y0 - math.log10(m) / 3 * (y0 - y1)
    sk.line(x0, y0, x1, y0, INK, 3)
    sk.line(x0, y0, x0, y1, INK, 3)
    for m, lab in [(1, "偶然"), (10, "10 倍"), (100, "100 倍"), (1000, "1,000 倍")]:
        sk.text(x0 - 16, Y(m), lab, 20, INK, "rm")
    sk.line(x0, Y(4), x1, Y(4), TEAL, 2, passes=1)
    sk.text(x1, Y(4) - 22, "偶然の 4 倍（論文の目安）", 20, TEAL, "rm")
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        sk.text(X(v), y0 + 28, f"{v:g}", 20, INK, "mm")
    sk.text((x0 + x1) / 2, y0 + 66, "書く過程の 10 の指標が元の値とどれだけ合うか（中央の相関）", 22, GRAY, "mm")
    sk.text(x0 - 10, y1 - 34, "1,000 個の候補から本物の文章が当たる率（偶然の何倍か）", 22, GRAY, "lm")
    for name, rho, m, side in RELEASE:
        c = ORANGE if m > 100 else (INDIGO if m > 4 else PLUM)
        sk.ellipse(X(rho), Y(m), 11, 11, c, 3, fill=c)
        if side == "r":
            sk.text(X(rho) + 22, Y(m), name, 20, INK, "lm")
        elif side == "u":
            sk.text(X(rho) - 10, Y(m) - 30, name, 20, INK, "rm")
        elif side == "d":
            sk.text(X(rho) + 10, Y(m) + 34, name, 20, INK, "mm")
        elif side == "l2":
            sk.text(X(rho) - 22, Y(m) + 26, name, 20, INK, "rm")
        else:
            sk.text(X(rho) - 22, Y(m), name, 20, INK, "rm")
    sk.save(OUT + "chart_release.png")


if __name__ == "__main__":
    for f in [ime_flow, ime_why, ime_os, threads, features, record_flow, replay, stage1, tool,
              chart_auc, chart_match, chart_zenodo, chart_release]:
        f()
    print("ok")
