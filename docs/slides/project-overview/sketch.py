"""手描き風（ラフな線）のイラストを PIL で描く小さなライブラリと、デッキ用の図一式。"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont

INK = (51, 48, 43)
ORANGE = (201, 124, 75)
TEAL = (62, 156, 134)
INDIGO = (90, 107, 176)
OLIVE = (127, 148, 99)
PLUM = (155, 110, 143)
GRAY = (116, 112, 106)
CREAM = (247, 240, 230)
WHITE = (253, 251, 248)

FONT = os.environ.get("GSE_DECK_FONT", os.path.expanduser("~/Library/Fonts/KleeOne-SemiBold.ttf"))
S = 2  # 描画の倍率（最後に縮める）


def font(px):
    return ImageFont.truetype(FONT, int(px * S))


class Sk:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.r = random.Random(seed)

    # ---- 基本
    def _j(self, a):
        return self.r.uniform(-a, a)

    def _poly(self, pts, color, width):
        pts = [(x * S, y * S) for x, y in pts]
        self.d.line(pts, fill=color, width=int(width * S), joint="curve")
        r = width * S / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=color)

    def line(self, x1, y1, x2, y2, color=INK, width=3, jit=1.6, passes=2):
        for p in range(passes):
            n = max(6, int(math.hypot(x2 - x1, y2 - y1) / 14))
            bow = self._j(jit * 1.5)
            pts = []
            for i in range(n + 1):
                t = i / n
                nx, ny = -(y2 - y1), (x2 - x1)
                L = math.hypot(nx, ny) or 1
                off = math.sin(t * math.pi) * bow + self._j(jit * 0.35)
                pts.append((x1 + (x2 - x1) * t + nx / L * off + self._j(0.4),
                            y1 + (y2 - y1) * t + ny / L * off + self._j(0.4)))
            self._poly(pts, color, width if p == 0 else width * 0.55)

    def path(self, pts, color=INK, width=3, jit=1.2):
        for a, b in zip(pts, pts[1:]):
            self.line(*a, *b, color=color, width=width, jit=jit, passes=1)

    def curve(self, pts, color=INK, width=3, jit=0.8, closed=False):
        # Catmull-Rom で滑らかに
        P = list(pts)
        if closed:
            P = [P[-1]] + P + P[:2]
        else:
            P = [P[0]] + P + [P[-1]]
        out = []
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            for k in range(12):
                t = k / 12
                t2, t3 = t * t, t * t * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                out.append((x + self._j(jit * 0.3), y + self._j(jit * 0.3)))
        out.append(P[-2])
        self._poly(out, color, width)

    def rect(self, x, y, w, h, color=INK, width=3, fill=None, jit=1.6):
        if fill:
            self.blob_rect(x, y, w, h, fill)
        o = 4
        self.line(x - o, y, x + w + o * 0.5, y + self._j(1), color, width, jit)
        self.line(x + w, y - o, x + w + self._j(1), y + h + o * 0.5, color, width, jit)
        self.line(x + w + o * 0.5, y + h, x - o * 0.5, y + h + self._j(1), color, width, jit)
        self.line(x, y + h + o * 0.5, x + self._j(1), y - o * 0.5, color, width, jit)

    def blob_rect(self, x, y, w, h, fill, alpha=255):
        c = fill + (alpha,) if len(fill) == 3 else fill
        pts = []
        for (px, py) in [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]:
            pts.append(((px + self._j(3)) * S, (py + self._j(3)) * S))
        self.d.polygon(pts, fill=c)

    def ellipse(self, cx, cy, rx, ry, color=INK, width=3, fill=None, jit=1.5, turns=1.08):
        if fill:
            c = fill + (255,) if len(fill) == 3 else fill
            self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=c)
        n = 40
        a0 = self.r.uniform(0, 2 * math.pi)
        pts = []
        for i in range(int(n * turns) + 1):
            a = a0 + 2 * math.pi * i / n
            k = 1 + self._j(0.03)
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        self._poly(pts, color, width)

    def arrow(self, x1, y1, x2, y2, color=INK, width=3, head=14, curved=0):
        if curved:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = -(y2 - y1), (x2 - x1)
            L = math.hypot(nx, ny) or 1
            c = (mx + nx / L * curved, my + ny / L * curved)
            pts = [((1 - t) ** 2 * x1 + 2 * (1 - t) * t * c[0] + t * t * x2,
                    (1 - t) ** 2 * y1 + 2 * (1 - t) * t * c[1] + t * t * y2) for t in [i / 20 for i in range(21)]]
            self._poly(pts, color, width)
            ex, ey = pts[-2]
        else:
            self.line(x1, y1, x2, y2, color, width, passes=1)
            ex, ey = x1, y1
        a = math.atan2(y2 - ey, x2 - ex)
        for s in (-1, 1):
            b = a + math.pi + s * 0.45
            self.line(x2, y2, x2 + head * math.cos(b), y2 + head * math.sin(b), color, width, jit=0.6, passes=1)

    def hatch(self, x, y, w, h, color, gap=9, width=2, angle=1.0):
        # 斜線の塗り（矩形の中）
        im2 = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        d2 = ImageDraw.Draw(im2)
        k = -1
        while True:
            k += 1
            off = k * gap
            if off > w + h:
                break
            xa, ya = x + off, y
            xb, yb = x + off - h * angle, y + h
            d2.line([(xa * S + self._j(2), ya * S), (xb * S + self._j(2), yb * S)], fill=color + (190,), width=int(width * S))
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=255)
        self.im.paste(im2, (0, 0), Image.composite(im2.split()[3], Image.new("L", self.im.size, 0), mask))

    def text(self, x, y, s, size=22, color=INK, anchor="la"):
        self.d.text((x * S, y * S), s, font=font(size), fill=color, anchor=anchor)

    def check(self, x, y, s=20, color=TEAL, width=4):
        self.path([(x, y), (x + s * 0.4, y + s * 0.45), (x + s, y - s * 0.55)], color, width)

    def cross(self, x, y, s=18, color=ORANGE, width=4):
        self.line(x - s / 2, y - s / 2, x + s / 2, y + s / 2, color, width)
        self.line(x + s / 2, y - s / 2, x - s / 2, y + s / 2, color, width)

    def dots(self, x, y, n=3, gap=14, r=3.5, color=INK):
        for i in range(n):
            cx = x + i * gap
            self.d.ellipse([(cx - r) * S, (y - r) * S, (cx + r) * S, (y + r) * S], fill=color)

    def save(self, path):
        self.im.resize((self.w, self.h), Image.LANCZOS).save(path)


# ---- 部品
def person(sk, x, y, sc=1.0, color=INK, arms="type", fill=None):
    """机に向かう人（x,y = 頭の中心）"""
    r = 22 * sc
    sk.ellipse(x, y, r, r, color, 3, fill=fill or WHITE)
    sk.curve([(x - 2 * sc, y + r), (x - 6 * sc, y + 45 * sc), (x - 4 * sc, y + 80 * sc)], color, 3)
    if arms == "type":
        sk.curve([(x - 4 * sc, y + 40 * sc), (x + 30 * sc, y + 58 * sc), (x + 62 * sc, y + 56 * sc)], color, 3)
    elif arms == "up":
        sk.curve([(x - 4 * sc, y + 38 * sc), (x - 30 * sc, y + 5 * sc), (x - 36 * sc, y - 30 * sc)], color, 3)
        sk.curve([(x - 2 * sc, y + 38 * sc), (x + 28 * sc, y + 5 * sc), (x + 34 * sc, y - 30 * sc)], color, 3)
    elif arms == "chin":
        sk.curve([(x - 4 * sc, y + 40 * sc), (x + 20 * sc, y + 50 * sc), (x + 14 * sc, y + 18 * sc)], color, 3)


def laptop(sk, x, y, w=150, color=INK, screen=None):
    h = w * 0.62
    sk.rect(x, y - h, w, h, color, 3, fill=screen or WHITE)
    sk.line(x - 18, y + 4, x + w + 18, y + 4, color, 4)
    return (x, y - h, w, h)


def desk(sk, x1, x2, y, color=INK):
    sk.line(x1, y, x2, y, color, 4)
    sk.line(x1 + 25, y, x1 + 25, y + 70, color, 3)
    sk.line(x2 - 25, y, x2 - 25, y + 70, color, 3)


def cloud(sk, cx, cy, w, h, color=INK, fill=WHITE):
    pts = []
    n = 9
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = 1 + (0.18 if i % 2 else -0.05)
        pts.append((cx + w / 2 * rr * math.cos(a), cy + h / 2 * rr * math.sin(a)))
    sk.d.ellipse([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S], fill=fill + (255,))
    sk.curve(pts, color, 3, closed=True)


# ======================================================================
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img") + "/"


def hero():
    sk = Sk(620, 460, 3)
    desk(sk, 40, 580, 330)
    person(sk, 150, 190, 1.25, fill=CREAM)
    scr = laptop(sk, 250, 326, 190, screen=WHITE)
    # 画面の中: 打鍵のリズム（縦棒）
    for i, hh in enumerate([22, 34, 16, 40, 28, 10, 8, 30, 36, 18]):
        x = scr[0] + 18 + i * 16
        col = TEAL if i not in (5, 6) else ORANGE
        sk.line(x, scr[1] + scr[3] - 20, x, scr[1] + scr[3] - 20 - hh, col, 5, jit=0.5, passes=1)
    # 止まりの吹き出し
    cloud(sk, 470, 110, 150, 90)
    sk.dots(448, 110, 3, 20, 5)
    sk.arrow(420, 150, 390, 200, GRAY, 2, 10, curved=-14)
    # マグカップ
    sk.rect(500, 285, 34, 42, INK, 3, fill=ORANGE)
    sk.ellipse(542, 304, 9, 12, INK, 3)
    for k in range(2):
        sk.curve([(510 + k * 12, 275), (505 + k * 12, 262), (512 + k * 12, 248)], GRAY, 2)
    sk.save(OUT + "hero.png")


def observe():
    sk = Sk(380, 330, 5)
    sk.rect(30, 170, 320, 130, INK, 3, fill=WHITE)
    for r_ in range(3):
        for c in range(7):
            sk.rect(50 + c * 42, 186 + r_ * 36, 32, 26, GRAY, 2, jit=0.8)
    sk.rect(112, 186 + 3 * 36 - 4, 160, 8, GRAY, 2, jit=0.5)
    sk.line(30, 90, 350, 90, INK, 3)
    xs = [40, 58, 70, 95, 104, 118, 210, 225, 234, 320, 334]
    for x in xs:
        sk.line(x, 70, x, 110, TEAL, 4, jit=0.5, passes=1)
    sk.path([(128, 128), (200, 128)], ORANGE, 3)
    sk.ellipse(165, 128, 6, 6, ORANGE, 2, fill=ORANGE)
    sk.save(OUT + "observe.png")


def notsaved():
    sk = Sk(400, 340, 7)
    sk.rect(50, 30, 230, 280, INK, 3, fill=WHITE)
    for i in range(8):
        w = 170 - (i % 3) * 30
        sk.line(75, 70 + i * 28, 75 + w, 70 + i * 28, GRAY, 3, jit=1.5, passes=1)
    sk.line(40, 50, 290, 290, ORANGE, 7)
    sk.line(290, 50, 40, 290, ORANGE, 7)
    sk.rect(290, 220, 80, 62, INK, 3, fill=TEAL)
    sk.curve([(306, 220), (306, 186), (330, 176), (354, 186), (354, 220)], INK, 4)
    sk.ellipse(330, 248, 7, 7, WHITE, 3, fill=WHITE)
    sk.save(OUT + "notsaved.png")


def stall_icons():
    cols = [ORANGE, INDIGO, TEAL, OLIVE, PLUM]
    for i, col in enumerate(cols):
        sk = Sk(200, 170, 11 + i)
        cx, cy = 100, 85
        if i == 0:
            pts = [(cx - 60 + 120 * a, cy - 50 + 100 * b) for a, b in
                   [(0, .5), (.3, .1), (.6, .7), (.2, .9), (.5, .3), (.9, .6), (.7, .1), (1, .8)]]
            sk.curve(pts, col, 5)
        elif i == 1:
            cloud(sk, cx, cy, 150, 100, col, WHITE)
            sk.text(cx, cy - 2, "?", 52, col, "mm")
        elif i == 2:
            sk.rect(cx - 70, cy - 55, 66, 100, col, 3, fill=WHITE)
            sk.rect(cx + 4, cy - 55, 66, 100, col, 3, fill=WHITE)
            for k in range(4):
                sk.line(cx - 58, cy - 32 + k * 20, cx - 16, cy - 32 + k * 20, GRAY, 2, passes=1)
                sk.line(cx + 16, cy - 32 + k * 20, cx + 58, cy - 32 + k * 20, GRAY, 2, passes=1)
        elif i == 3:
            cloud(sk, cx - 26, cy - 24, 100, 64, col, WHITE)
            cloud(sk, cx + 32, cy + 26, 100, 64, col, WHITE)
            sk.dots(cx - 44, cy - 24, 3, 18, 5, col)
            sk.dots(cx + 14, cy + 26, 3, 18, 5, col)
        else:
            sk.path([(cx - 34, cy - 62), (cx - 34, cy + 20), (cx + 40, cy + 20)], col, 5)
            sk.line(cx - 34, cy + 20, cx - 34, cy + 64, col, 5)
            sk.line(cx + 34, cy + 20, cx + 34, cy + 64, col, 5)
        sk.save(OUT + f"st{i}.png")


def frame(name, w, h, color=INK, fill=WHITE, width=3, seed=3):
    sk = Sk(w, h, seed)
    sk.rect(8, 8, w - 16, h - 16, color, width, fill=fill, jit=1.8)
    sk.save(OUT + name)


def arrow_img(name, w=200, h=120, color=INK, curved=-24, seed=5):
    sk = Sk(w, h, seed)
    sk.arrow(12, h / 2 + 10, w - 14, h / 2, color, 5, 22, curved=curved)
    sk.save(OUT + name)


def probecard():
    sk = Sk(420, 360, 9)
    sk.rect(20, 20, 380, 320, INK, 3, fill=WHITE)
    for row in range(2):
        y = 70 + row * 70
        sk.line(48, y, 200, y, GRAY, 3, passes=1)
        for k in range(5):
            x = 230 + k * 32
            sk.ellipse(x, y, 11, 11, TEAL if (row, k) in [(0, 3), (1, 1)] else GRAY, 3,
                       fill=TEAL if (row, k) in [(0, 3), (1, 1)] else None)
    for k in range(6):
        x = 48 + (k % 3) * 116
        y = 220 + (k // 3) * 54
        sel = k == 2
        sk.rect(x, y, 100, 38, ORANGE if sel else GRAY, 3, fill=(244, 222, 204) if sel else None, jit=1.0)
    sk.save(OUT + "probecard.png")


def roadmap():
    sk = Sk(1180, 200, 29)
    cols = [ORANGE, INDIGO, TEAL, OLIVE, PLUM]
    pts = [(90 + i * 250, 100 + (22 if i % 2 else -8)) for i in range(5)]
    for a, b in zip(pts, pts[1:]):
        sk.curve([(a[0] + 40, a[1]), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 26), (b[0] - 40, b[1])], GRAY, 3)
    for i, ((x, y), col) in enumerate(zip(pts, cols)):
        sk.ellipse(x, y, 40, 40, INK, 3, fill=col)
        sk.text(x, y, str(i + 1), 36, WHITE, "mm")
    sk.save(OUT + "roadmap.png")


def coin():
    sk = Sk(360, 320, 13)
    sk.ellipse(180, 170, 110, 110, INK, 4, fill=(234, 214, 180))
    sk.ellipse(180, 170, 88, 88, (180, 150, 100), 3)
    sk.text(180, 168, "0.5", 56, INK, "mm")
    for a in [-150, -120, -60, -30]:
        r1, r2 = 125, 150
        ar = math.radians(a)
        sk.line(180 + r1 * math.cos(ar), 170 + r1 * math.sin(ar), 180 + r2 * math.cos(ar), 170 + r2 * math.sin(ar), ORANGE, 3)
    sk.save(OUT + "coin.png")


def stopwatch():
    sk = Sk(300, 320, 17)
    sk.ellipse(150, 180, 110, 110, INK, 4, fill=WHITE)
    sk.rect(130, 40, 40, 26, INK, 3, fill=ORANGE)
    sk.line(150, 66, 150, 72, INK, 4)
    # 扇（十数秒）
    sk.d.pieslice([(150 - 92) * S, (180 - 92) * S, (150 + 92) * S, (180 + 92) * S], -90, -15, fill=TEAL + (150,))
    sk.line(150, 180, 150, 98, INK, 4)
    sk.line(150, 180, 214, 158, INK, 4)
    sk.ellipse(150, 180, 7, 7, INK, 3, fill=INK)
    sk.save(OUT + "stopwatch.png")


def bell():
    sk = Sk(300, 320, 19)
    # たくさん鳴る通知
    for i in range(12):
        x = 40 + (i % 4) * 66
        y = 50 + (i // 4) * 84
        col = ORANGE if i not in (5,) else TEAL
        sk.curve([(x, y + 40), (x + 6, y + 6), (x + 22, y - 6), (x + 38, y + 6), (x + 44, y + 40)], col, 3)
        sk.line(x - 4, y + 40, x + 48, y + 40, col, 3, passes=1)
        sk.ellipse(x + 22, y + 48, 5, 5, col, 2, fill=col)
    sk.save(OUT + "bell.png")


def handmark():
    sk = Sk(640, 380, 31)
    sk.rect(40, 30, 560, 330, INK, 4, fill=(232, 238, 228))
    # 霧
    for i in range(6):
        sk.d.ellipse([(80 + i * 85) * S, (70 + (i % 2) * 30) * S, (190 + i * 85) * S, (130 + (i % 2) * 30) * S], fill=(255, 255, 255, 120))
    # 草（打鍵でなびく）
    for i in range(34):
        x = 60 + i * 16
        lean = 18 if 180 < x < 380 else 4
        h = 60 + (i * 37 % 40)
        sk.curve([(x, 345), (x + lean * 0.4, 345 - h * 0.5), (x + lean, 345 - h)], OLIVE if i % 3 else TEAL, 3)
    # 粒
    for i in range(18):
        x = 120 + (i * 53 % 420)
        y = 150 + (i * 31 % 110)
        sk.ellipse(x, y, 4, 4, ORANGE, 2, fill=ORANGE)
    # 下の縁の帯
    sk.blob_rect(42, 340, 556, 16, ORANGE, 170)
    sk.save(OUT + "handmark.png")


def invite():
    sk = Sk(620, 370, 37)
    sk.rect(30, 30, 380, 250, INK, 4, fill=WHITE)
    for i in range(6):
        sk.line(60, 80 + i * 28, 60 + 220 - (i % 2) * 60, 80 + i * 28, GRAY, 3, passes=1)
    # 右上の小さな印
    sk.ellipse(370, 66, 20, 20, TEAL, 3, fill=(210, 236, 228))
    sk.curve([(362, 70), (368, 58), (376, 62), (380, 72)], TEAL, 3)
    # 伸びをする人
    person(sk, 520, 250, 1.1, arms="up", fill=CREAM)
    sk.line(470, 345, 590, 345, INK, 3)
    sk.save(OUT + "invite.png")


def icon_lock():
    sk = Sk(160, 160, 41)
    sk.rect(36, 70, 88, 66, INK, 3, fill=TEAL)
    sk.curve([(52, 70), (52, 36), (80, 24), (108, 36), (108, 70)], INK, 4)
    sk.ellipse(80, 100, 7, 9, WHITE, 3, fill=WHITE)
    sk.save(OUT + "i_lock.png")


def icon_hand():
    sk = Sk(160, 160, 43)
    sk.ellipse(80, 80, 62, 62, ORANGE, 3, fill=(244, 222, 204))
    # 手のひら（止まれ）
    for i, h in enumerate([40, 50, 52, 46]):
        x = 56 + i * 15
        sk.line(x, 92, x, 92 - h, INK, 7, jit=0.6, passes=1)
    sk.curve([(52, 88), (54, 118), (80, 128), (106, 116), (112, 96), (124, 80)], INK, 6)
    sk.save(OUT + "i_hand.png")


def icon_noscore():
    sk = Sk(160, 160, 47)
    sk.rect(30, 34, 100, 92, INK, 3, fill=WHITE)
    sk.text(80, 80, "100", 34, GRAY, "mm")
    sk.ellipse(80, 80, 62, 62, PLUM, 4)
    sk.line(36, 124, 124, 36, PLUM, 5)
    sk.save(OUT + "i_noscore.png")


def icon_person():
    sk = Sk(160, 160, 53)
    person(sk, 62, 52, 0.9, arms="chin", fill=CREAM)
    sk.ellipse(112, 104, 26, 26, INDIGO, 4)
    sk.line(130, 122, 150, 144, INDIGO, 6)
    sk.save(OUT + "i_person.png")


def icon_num(n, col, name):
    sk = Sk(160, 160, 59 + n)
    sk.ellipse(80, 80, 60, 60, INK, 3, fill=col)
    sk.text(80, 78, str(n), 64, WHITE, "mm")
    sk.save(OUT + name)


def mini_check(name, ok=True, col=TEAL):
    sk = Sk(80, 80, 61 if ok else 62)
    sk.ellipse(40, 40, 30, 30, col, 3, fill=WHITE)
    if ok:
        sk.check(26, 42, 30, col, 5)
    else:
        sk.dots(24, 42, 3, 15, 4, col)
    sk.save(OUT + name)


def magnifier_data():
    sk = Sk(380, 320, 67)
    # 3 つのデータの紙
    cols = [INDIGO, TEAL, OLIVE]
    for i, c in enumerate(cols):
        sk.rect(40 + i * 46, 60 + i * 30, 150, 190, INK, 3, fill=WHITE)
        for k in range(5):
            sk.line(58 + i * 46, 96 + i * 30 + k * 26, 170 + i * 46, 96 + i * 30 + k * 26, c, 3, passes=1)
    sk.ellipse(270, 150, 62, 62, INK, 5, fill=(255, 255, 255, 140))
    sk.line(314, 196, 354, 246, INK, 9)
    sk.save(OUT + "data.png")


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    stall_icons(); probecard()
    frame("fr_gray.png", 640, 380, GRAY, WHITE); frame("fr_teal.png", 640, 380, TEAL, WHITE, 4, 4)
    frame("fr_card.png", 520, 560, INK, WHITE, 3, 6); frame("fr_wide.png", 1200, 300, GRAY, WHITE, 3, 8)
    frame("fr_small.png", 560, 260, INK, WHITE, 3, 10)
    arrow_img("arrow.png"); arrow_img("arrow_small.png", 120, 80, GRAY, -10, 7)
    for f in [hero, observe, notsaved, coin, stopwatch, bell, roadmap, handmark, invite,
              icon_lock, icon_hand, icon_noscore, icon_person, magnifier_data]:
        f()
    icon_num(1, ORANGE, "n1.png"); icon_num(2, TEAL, "n2.png"); icon_num(3, INDIGO, "n3.png")
    mini_check("ok.png", True, TEAL); mini_check("wip.png", False, ORANGE); mini_check("todo.png", False, GRAY)
    print("ok")
