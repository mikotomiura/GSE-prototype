"""手跡の整理と設計案のデッキ（GSE_handmark_design.pptx）の図とグラフ（sketch.py の手描き風の線で描く）。

出どころ: ADR-048・ADR-050・ADR-051・analysis/handmark/trace.rs（半減 0.7 秒・0.9 秒・8 秒で 0）・
S-CX（docs/literature/20261120-handmark-coexistence-concept.md）・
.steering/20261120-handmark-coexistence-design/design-proposal.md。
Roomba の数は Sung ら 2010 [P612] の本文（30 世帯・6 か月）から写した。
実行: python3 figs3.py（img/ に fig_hm_*.png と chart_hm_*.png を書く）"""
import math
import random

from figs import PALE, node, harrow
from sketch import Sk, INK, ORANGE, TEAL, INDIGO, OLIVE, PLUM, GRAY, WHITE, OUT, laptop


def tag(sk, x, y, w, h, label, col, size=22):
    sk.rect(x, y, w, h, col, 3, fill=PALE.get(col, WHITE))
    sk.text(x + w / 2, y + h / 2, label, size, INK, "mm")


# ---------------------------------------------------------------- 役割
def role():
    """打鍵とポインタから、推定（返さない）と手跡（行為の性質だけ返す）へ"""
    sk = Sk(1500, 600, 301)
    node(sk, 30, 110, 210, 110, "打鍵", INK, 28, sub="種類と時刻だけ", sub_size=18, fill=False)
    node(sk, 30, 390, 210, 110, "ポインタ", INK, 28, sub="記録しない", sub_size=18, fill=False)
    # 上: 推定（打鍵だけ）
    node(sk, 340, 70, 420, 150, "推定器", INDIGO, 30, sub="停滞の確率・状態（系の判断）", sub_size=20)
    harrow(sk, 250, 165, 330)
    node(sk, 880, 70, 300, 150, "保留", GRAY, 30, sub="系が判断しない所", sub_size=20)
    harrow(sk, 770, 145, 870)
    sk.cross(1230, 145, 26, ORANGE, 6)
    sk.text(1270, 145, "手跡には返さない", 24, ORANGE, "lm")
    # 下: 手跡（打鍵とポインタ）
    node(sk, 340, 360, 420, 160, "行為の性質", TEAL, 30, sub="速さ・リズム・止まり・カーソルの動き", sub_size=20)
    sk.arrow(250, 190, 335, 400, GRAY, 4, 16)
    harrow(sk, 250, 445, 330)
    sk.text(20, 560, "ポインタは推定に入れない（ADR-050 D2）", 19, GRAY, "lm")
    harrow(sk, 770, 440, 870)
    node(sk, 880, 360, 300, 160, "手跡", ORANGE, 32, sub="背景の窓と下の縁の帯", sub_size=20)
    harrow(sk, 1190, 440, 1260)
    sk.text(1280, 420, "本人が", 24, INK, "lm")
    sk.text(1280, 458, "感じ取る", 24, INK, "lm")
    sk.text(1000, 565, "保留の裏側の柱: 系が黙っている所に、判断の代わりに手の跡を置く（ADR-048）", 20, GRAY, "mm")
    sk.save(OUT + "fig_hm_role.png")


# ---------------------------------------------------------------- 場と減衰
def field():
    """左: カーソルの周りで草が倒れ粒が寄る / 右: 倒れと寄せが戻る時間"""
    sk = Sk(1500, 640, 302)
    sk.rect(30, 40, 640, 520, INK, 3, fill=WHITE)
    sk.text(350, 600, "画面の背景（16ms の刻みで動く）", 22, GRAY, "mm")
    rnd = random.Random(7)
    cx, cy = 400, 300
    for gx in range(70, 650, 34):
        for gy in range(110, 540, 62):
            x = gx + rnd.uniform(-6, 6)
            y = gy + rnd.uniform(-6, 6)
            d = math.hypot(x - cx, y - cy)
            bend = max(0.0, 1 - d / 190) * 0.9
            ang = -math.pi / 2 + bend * (1.0 if x > cx else -1.0)
            ln = 34
            col = TEAL if bend > 0.05 else OLIVE
            sk.line(x, y, x + ln * math.cos(ang), y + ln * math.sin(ang), col, 3, jit=0.6, passes=1)
    for k in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(20, 120)
        sk.ellipse(cx + r * math.cos(a), cy + r * math.sin(a), 5, 5, ORANGE, 2, fill=ORANGE, jit=0.3)
    # カーソル
    sk.path([(cx, cy), (cx, cy + 44), (cx + 12, cy + 33), (cx + 24, cy + 52), (cx + 32, cy + 47),
             (cx + 20, cy + 28), (cx + 36, cy + 28), (cx, cy)], INK, 3)
    sk.rect(70, 470, 400, 56, GRAY, 2, fill=WHITE)
    sk.text(270, 498, "動いた所の草が倒れ、粒が寄る", 22, INK, "mm")
    sk.arrow(270, 465, cx - 10, cy + 20, GRAY, 3, 12, curved=-30)
    # 右: 減衰
    ox, oy, w, h = 790, 500, 660, 380
    sk.line(ox, oy, ox + w, oy, INK, 3)
    sk.line(ox, oy, ox, oy - h, INK, 3)
    sk.text(ox + w / 2, oy + 50, "最後の入力からの時間（秒）", 22, GRAY, "mm")
    sk.text(ox - 20, oy - h - 20, "跡の量", 22, GRAY, "la")
    tmax = 9.0

    def px(t):
        return ox + t / tmax * w

    def py(v):
        return oy - v * (h - 40)
    pts_b = [(px(t / 10), py(0.5 ** ((t / 10) / 0.7))) for t in range(0, 81)]
    pts_p = [(px(t / 10), py(0.5 ** ((t / 10) / 0.9))) for t in range(0, 81)]
    sk.curve(pts_b, TEAL, 4)
    sk.curve(pts_p, ORANGE, 4)
    sk.line(px(0.7), oy, px(0.7), py(0.5), TEAL, 2, passes=1)
    sk.line(px(0.9), oy, px(0.9), py(0.5), ORANGE, 2, passes=1)
    sk.text(px(0.7) - 6, oy + 20, "0.7", 20, TEAL, "mm")
    sk.text(px(0.9) + 26, oy + 20, "0.9", 20, ORANGE, "mm")
    sk.line(px(8), oy, px(8), oy - 60, INK, 3, passes=1)
    sk.text(px(8), oy + 20, "8", 20, INK, "mm")
    sk.text(px(8) - 10, oy - 80, "ここで 0 に", 20, INK, "rm")
    sk.text(px(2.0), py(0.85), "草の倒れ（半減 0.7 秒）", 22, TEAL, "la")
    sk.text(px(2.0), py(0.68), "粒の寄せ（半減 0.9 秒）", 22, ORANGE, "la")
    sk.text(px(2.0), py(0.45), "育たない・溜まらない", 22, INK, "la")
    sk.save(OUT + "fig_hm_field.png")


# ---------------------------------------------------------------- 漏れの確かめ
def leak():
    sk = Sk(1500, 560, 303)
    node(sk, 30, 200, 220, 140, "記録", GRAY, 30, sub="打鍵の時刻・推定", sub_size=19)
    harrow(sk, 260, 270, 330)
    node(sk, 340, 200, 220, 140, "描き直す", PLUM, 28, sub="同じ種・同じ刻み", sub_size=19)
    sk.arrow(570, 250, 650, 130, GRAY, 4, 16)
    sk.arrow(570, 290, 650, 410, GRAY, 4, 16)
    node(sk, 660, 60, 420, 140, "予測器 A", TEAL, 28, sub="行為の量（打鍵＋ポインタの 1 秒の量）", sub_size=19)
    node(sk, 660, 340, 420, 140, "予測器 B", ORANGE, 28, sub="手跡の見た目（画素）", sub_size=20)
    sk.arrow(1090, 130, 1170, 250, GRAY, 4, 16)
    sk.arrow(1090, 410, 1170, 290, GRAY, 4, 16)
    node(sk, 1180, 190, 300, 160, "系の判断を当てる", INDIGO, 24, sub="停滞の確率 0.60 以上・3 状態", sub_size=18)
    sk.text(750, 510, "B が A を許す幅を超えて上回らないかを見る（区間推定・天井つき・ADR-051 D3）", 22, INK, "mm")
    sk.text(750, 545, "ポインタは記録しないので 1 秒の量からの近似。「判断は一切読めない」とは主張しない", 19, GRAY, "mm")
    sk.save(OUT + "fig_hm_leak.png")


# ---------------------------------------------------------------- 名前の衝突
def collision():
    sk = Sk(1500, 760, 304)
    sk.ellipse(750, 300, 250, 120, ORANGE, 4, fill=PALE[ORANGE])
    sk.text(750, 270, "共存感覚", 34, INK, "mm")
    sk.text(750, 318, "自分の手から生まれ、", 21, INK, "mm")
    sk.text(750, 348, "自分ではないものとしてそばにいる", 21, INK, "mm")
    items = [
        (40, 40, "digital companion species", "Lupton 2016 ・ 理論", "衝突", ORANGE),
        (40, 250, "data doppelganger", "Seberger 2025 ・ 概念分析", "重なる", INDIGO),
        (40, 460, "data double（本人側）", "Ruckenstein 2014 ・ 判断を運ぶ", "重なる", INDIGO),
        (1060, 40, "他者への主体の帰属の錯覚", "Nomura 2019 ・ 実験室", "重なる", TEAL),
        (1060, 250, "誰かがいる感じ", "Blanke 2014 ・ 実験室", "重なる", TEAL),
        (1060, 460, "data double（監視）", "Haggerty 2000 ・ 第三者の像", "隣接", GRAY),
    ]
    for x, y, t, s, j, c in items:
        sk.rect(x, y, 400, 150, c, 3, fill=WHITE)
        sk.text(x + 200, y + 42, t, 23, INK, "mm")
        sk.text(x + 200, y + 84, s, 19, GRAY, "mm")
        sk.text(x + 200, y + 122, j, 22, c, "mm")
        ex = x + 400 if x < 700 else x
        sk.line(ex, y + 75, 750 + (-250 if x < 700 else 250) * 0.95, 300, GRAY, 2, passes=1)
    sk.text(750, 470, "理論（左）と心理（右）に、同じ形がある", 22, INK, "mm")
    sk.text(750, 520, "→ 新しい概念とは名乗れない", 24, ORANGE, "mm")
    sk.text(750, 680, "見つからなかったもの: 作業中にそばで動く表示の経験として測ったもの", 22, GRAY, "mm")
    sk.text(750, 720, "判断を運ばない表示で測ったもの ・ 自他を動かす変数を比べたもの", 22, GRAY, "mm")
    sk.save(OUT + "fig_hm_collision.png")


# ---------------------------------------------------------------- 変数の向き
def variables():
    sk = Sk(1500, 600, 305)
    cols = [("遅れ", INDIGO, ["視覚の帰属では弱い", "Farrer 2008 ・ Kim 2024", "", "自己接触の輪では", "誰かがいる感じ", "Blanke 2014"], "課題で異なる"),
            ("慣性", GRAY, ["慣性そのものを振った", "研究は見つからない", "（この探索の範囲）", "遅れの結果からは", "決められない", ""], "未検証"),
            ("予測可能性", TEAL, ["応答の予測可能性に", "ちょうどよい所があり", "そこで生き物と感じる", "", "Bernardet 2017", ""], "効きがある"),
            ("空間のずれ", ORANGE, ["他者への帰属は", "空間のずれが", "大きいときに起きる", "", "Farrer 2008", ""], "効きがある")]
    w, gap = 340, 26
    for i, (t, c, lines, verdict) in enumerate(cols):
        x = 30 + i * (w + gap)
        sk.rect(x, 30, w, 440, c, 3, fill=PALE.get(c, WHITE))
        sk.text(x + w / 2, 80, t, 32, INK, "mm")
        for k, ln in enumerate(lines):
            if ln:
                sk.text(x + w / 2, 150 + k * 38, ln, 20, INK if "20" not in ln else GRAY, "mm")
        sk.rect(x + 40, 395, w - 80, 56, c, 3, fill=WHITE)
        sk.text(x + w / 2, 423, verdict, 23, c, "mm")
    sk.text(750, 530, "どの変数でも「自分のもの」と「別の存在」の両方を測ったものは、この探索の範囲で見つからない → 自前で比べる", 21, INK, "mm")
    sk.save(OUT + "fig_hm_vars.png")


# ---------------------------------------------------------------- 慣れ（Roomba）
def chart_roomba():
    """Sung ら 2010: 30 世帯・6 か月。会話する世帯 19 → 6 か月目 12"""
    sk = Sk(1100, 600, 306)
    ox, oy, h = 160, 480, 380
    sk.line(ox, oy, 1040, oy, INK, 3)
    sk.line(ox, oy, ox, oy - h, INK, 3)
    for v in (0, 10, 20, 30):
        y = oy - v / 30 * h
        sk.text(ox - 18, y, str(v), 20, GRAY, "rm")
        if v:
            sk.line(ox, y, 1040, y, (225, 220, 212), 1, passes=1)
    sk.text(ox - 18, oy - h - 34, "世帯", 20, GRAY, "rm")
    bars = [(230, 19, "6 か月の間に", TEAL), (450, 12, "6 か月目", ORANGE)]
    for x, v, lab, c in bars:
        y = oy - v / 30 * h
        sk.rect(x, y, 150, oy - y, c, 3, fill=PALE[c])
        sk.text(x + 75, y - 28, f"{v}", 28, INK, "mm")
        sk.text(x + 75, oy + 32, lab, 21, INK, "mm")
    sk.text(415, 70, "ロボットに話しかけた世帯（30 世帯中）", 23, INK, "mm")
    sk.arrow(390, 230, 455, 300, GRAY, 3, 12)
    sk.text(700, 175, "名前を付けたのは最初の 2 週で", 21, INK, "la")
    sk.text(700, 210, "13 世帯（その後の新しい名前は 6）", 21, INK, "la")
    sk.text(700, 260, "どれも適応の時期にいちばん盛ん", 21, GRAY, "la")
    sk.text(700, 350, "減るが、消えない", 26, ORANGE, "la")
    sk.text(550, 565, "出典: Sung, Grinter & Christensen 2010（家庭の Roomba・30 世帯・6 か月）", 18, GRAY, "mm")
    sk.save(OUT + "chart_hm_roomba.png")


# ---------------------------------------------------------------- 3 つの層
def layers():
    sk = Sk(1500, 640, 307)
    rows = [("層 3  守り", INDIGO, "足した部分を系の状態に依存させない（日の種）・漏れの検査を同じ手順で回す・真似にしない・育てない"),
            ("層 2  他者性のつまみ", ORANGE, "新しく足す候補（決めていない）: A 慣性 ・ B 自律の基層 ・ C 空間のずれ を比べる"),
            ("層 1  由来", TEAL, "今のまま: カーソルの周りの倒れと寄せ、打鍵の速さ・リズム・止まり（即時の応答）")]
    for i, (t, c, d) in enumerate(rows):
        y = 40 + i * 190
        sk.rect(60 + i * 30, y, 1380 - i * 60, 160, c, 4, fill=PALE[c])
        sk.text(110 + i * 30, y + 50, t, 32, INK, "lm")
        sk.text(110 + i * 30, y + 110, d, 22, INK, "lm")
    sk.save(OUT + "fig_hm_layers.png")


# ---------------------------------------------------------------- つまみ 3 案
def knobs():
    sk = Sk(1500, 600, 308)
    w, gap = 460, 30
    titles = [("A 慣性", GRAY, ["戻りの半減と速さの平滑を", "遅い側へ振る"]),
              ("B 自律の基層", TEAL, ["入力と無関係にゆっくり動く層に", "応答を部分的に重ねる"]),
              ("C 空間のずれ", ORANGE, ["応答の中心を", "カーソルの真下から少しずらす"])]
    for i, (t, c, cap) in enumerate(titles):
        x = 30 + i * (w + gap)
        sk.rect(x, 30, w, 400, c, 3, fill=WHITE)
        sk.text(x + w / 2, 70, t, 30, c, "mm")
        sk.text(x + w / 2, 480, cap[0], 21, INK, "mm")
        sk.text(x + w / 2, 515, cap[1], 21, INK, "mm")
        cx, cy = x + w / 2, 260
        if i == 0:
            path = [(x + 60 + k * 34, cy + 60 * math.sin(k / 2.2)) for k in range(11)]
            sk.curve(path, INK, 3)
            lag = [(px + 0, py + 0) for px, py in [(x + 40 + k * 34, cy + 40 * math.sin((k - 1.5) / 2.2) + 30) for k in range(11)]]
            sk.curve(lag, GRAY, 5)
            sk.text(x + w / 2, 380, "手（黒）に遅れてついてくる（灰）", 19, GRAY, "mm")
        elif i == 1:
            for k in range(4):
                pts = [(x + 30 + j * 40, cy - 90 + k * 55 + 18 * math.sin(j / 1.6 + k)) for j in range(11)]
                sk.curve(pts, OLIVE, 3)
            sk.ellipse(cx + 40, cy + 10, 60, 45, TEAL, 4, fill=None)
            sk.text(x + w / 2, 380, "基層（緑）の上に、手の応答（円）", 19, GRAY, "mm")
        else:
            sk.path([(cx - 70, cy - 10), (cx - 70, cy + 30), (cx - 59, cy + 20), (cx - 49, cy + 38), (cx - 42, cy + 33),
                     (cx - 52, cy + 16), (cx - 38, cy + 16), (cx - 70, cy - 10)], INK, 3)
            sk.ellipse(cx + 70, cy - 30, 55, 55, ORANGE, 4, fill=PALE[ORANGE])
            sk.arrow(cx - 40, cy + 5, cx + 20, cy - 20, GRAY, 3, 12)
            sk.text(x + w / 2, 380, "カーソル（黒）からずれた所に応答", 19, GRAY, "mm")
    sk.text(750, 575, "文献の見立てでは B がいちばん「同居者」らしい見込み（確かめていない）", 22, INK, "mm")
    sk.save(OUT + "fig_hm_knobs.png")


# ---------------------------------------------------------------- 日の終わりの問い
def daycard():
    sk = Sk(1400, 700, 309)
    sk.rect(330, 30, 1040, 580, INK, 3, fill=WHITE)
    sk.text(370, 75, "今日の作業について（手跡ありの日だけ足す項目の案）", 24, INK, "lm")
    items = [("由来の判断", TEAL, "今日の手跡の動きは、自分の作業から生まれたものだと思う"),
             ("感じ", ORANGE, "手跡が、そばにいる別の何かのように感じた"),
             ("反証（候補）", PLUM, "見張られているように感じた"),
             ("反証（候補）", PLUM, "手跡が煩わしかった")]
    sk.text(700, 660, "中心は上の 2 つ。日の問いは 2〜3 項目・10 秒ほど（ADR-048 D3）なので数を絞る。5 段の丸は例", 20, GRAY, "mm")
    for i, (lab, c, q) in enumerate(items):
        y = 140 + i * 115
        tag(sk, 30, y, 260, 70, lab, c, 24)
        sk.arrow(295, y + 35, 340, y + 35, GRAY, 3, 10)
        sk.text(370, y + 20, q, 22, INK, "lm")
        for k in range(5):
            sk.ellipse(400 + k * 70, y + 62, 14, 14, GRAY, 2, fill=WHITE)
        sk.text(400 + 5 * 70 + 10, y + 62, "あてはまらない ← → あてはまる", 17, GRAY, "lm")
    sk.save(OUT + "fig_hm_daycard.png")


# ---------------------------------------------------------------- 進める順
def steps():
    sk = Sk(1500, 420, 310)
    st = [("1", "回 1 の結果を見る", "守りが成り立つか", INDIGO),
          ("2", "机上で A・B・C", "記録から描き直し、漏れを検査", TEAL),
          ("3", "研究者自身で試す", "数日ずつ切り替え、問いに答える", OLIVE),
          ("4", "段 1 の問いに足す", "ADR-051 D6 の変更", ORANGE)]
    w, gap = 320, 50
    for i, (n, t, d, c) in enumerate(st):
        x = 30 + i * (w + gap)
        sk.rect(x, 60, w, 280, c, 3, fill=PALE[c])
        sk.ellipse(x + 50, 110, 30, 30, c, 3, fill=WHITE)
        sk.text(x + 50, 110, n, 28, c, "mm")
        sk.text(x + w / 2, 190, t, 26, INK, "mm")
        sk.text(x + w / 2, 260, d, 19, GRAY, "mm")
        if i < 3:
            harrow(sk, x + w + 6, 200, x + w + gap - 6)
    sk.text(750, 390, "2 と 3 は新しい被験者が要らない。4 で初めて参加者の画面が変わる", 21, INK, "mm")
    sk.save(OUT + "fig_hm_steps.png")


# ---------------------------------------------------------------- 価値: 2 つの読める度合い
def quadrant():
    """横 = 自分のものと分かる・縦 = 系の判断が読める（許した行為の量を超えて）。手跡は右下を狙う"""
    sk = Sk(1500, 720, 307)
    ox, oy, w, h = 230, 640, 1180, 580
    sk.arrow(ox, oy, ox + w, oy, INK, 3, 16)
    sk.arrow(ox, oy, ox, oy - h, INK, 3, 16)
    sk.text(ox + w / 2, oy + 45, "自分の手のものと分かる →", 24, INK, "mm")
    sk.text(ox - 25, oy - h + 10, "系の判断が", 22, INK, "rm")
    sk.text(ox - 25, oy - h + 42, "読める ↑", 22, INK, "rm")
    mx, my = ox + w / 2, oy - h / 2
    sk.line(mx, oy - 10, mx, oy - h + 20, GRAY, 2, passes=1)
    sk.line(ox + 10, my, ox + w - 20, my, GRAY, 2, passes=1)
    cells = [
        (ox + 30, oy - h + 40, "状態を映す周辺表示", ["天気の比喩で情報を映す（WeatherTank）", "誰の手かは問わない"], GRAY),
        (mx + 30, oy - h + 40, "自己追跡のグラフ・data double", ["自分のものと分かり、状態も読める", "系の判断の色に「外の人の意見」を期待（Ruckenstein 2014）"], INDIGO),
        (ox + 30, my + 30, "装飾の壁紙・生成の作品", ["どちらも読めない"], GRAY),
    ]
    for x, y, t, lines, c in cells:
        sk.text(x, y, t, 25, c, "la")
        for k, ln in enumerate(lines):
            sk.text(x, y + 44 + k * 34, ln, 19, GRAY, "la")
    sk.rect(mx + 20, my + 20, w / 2 - 50, h / 2 - 45, ORANGE, 4, fill=PALE[ORANGE])
    sk.text(mx + 45, my + 55, "手跡が狙う所", 28, ORANGE, "la")
    sk.text(mx + 45, my + 100, "自分の手と分かるが、系の判断としては読めない", 21, INK, "la")
    sk.text(mx + 45, my + 132, "（行為の量から読める分は、許した漏れ）", 18, GRAY, "la")
    sk.text(mx + 45, my + 166, "両方を同じ研究で測ったもの: 2 ラウンド 0 件", 19, INK, "la")
    sk.text(mx + 45, my + 194, "（S-TN・S-TN2・この探索の範囲）", 17, GRAY, "la")
    sk.text(mx + 45, my + 230, "この中で、由来と他者性のあいだを動かす（層 2）", 19, TEAL, "la")
    sk.save(OUT + "fig_hm_quadrant.png")


# ---------------------------------------------------------------- 価値: 近い系譜と向きが逆
def reverse():
    sk = Sk(1500, 720, 308)
    sk.text(330, 30, "近い系譜（既にある）", 25, INDIGO, "mm")
    sk.text(1130, 30, "手跡（向きが逆）", 25, ORANGE, "mm")
    rows = [("データ肖像", "推定をより正確にする・確かめて満足する", "Viégas 2004 ・ Viégas 2006（Themail）",
             "系は判断を保留し、推定を見せない"),
            ("personal informatics", "長く溜めて、振り返る", "Li 2010 ・ Elsden 2016",
             "溜めない・8 秒で消える・育たない"),
            ("状態の周辺表示・data double", "状態や判断を映す", "WeatherTank ・ Ruckenstein 2014",
             "行為だけを映す・判断を運ばない"),
            ("判断を返さない表現", "解釈を開く。読めるかの検査は見つからない", "Affective Diary ・ Boehner 2005",
             "読めるかを、漏れの検査で測る")]
    for i, (t, d, src, ours) in enumerate(rows):
        y = 70 + i * 150
        sk.rect(30, y, 600, 128, INDIGO, 3, fill=WHITE)
        sk.text(330, y + 32, t, 24, INK, "mm")
        sk.text(330, y + 70, d, 20, INK, "mm")
        sk.text(330, y + 104, src, 17, GRAY, "mm")
        harrow(sk, 650, y + 64, 820)
        sk.rect(840, y, 620, 128, ORANGE, 3, fill=PALE[ORANGE])
        sk.text(1150, y + 64, ours, 23, INK, "mm")
    sk.text(750, 690, "差は「空白」ではなく「向きが逆」（S4）。近い系譜があることを先に書く", 22, INK, "mm")
    sk.save(OUT + "fig_hm_reverse.png")


if __name__ == "__main__":
    for f in [role, field, leak, collision, variables, chart_roomba, layers, knobs, daycard, steps,
              quadrant, reverse]:
        f()
    print("ok")
