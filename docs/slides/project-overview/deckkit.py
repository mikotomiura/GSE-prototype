"""詳細版・知見版・技術版のデッキに共通の部品（build.py の部品を関数にまとめ直したもの）。

テンプレート tpl.pptx の上に、Klee One の文字と img/ の手描き風の図でスライドを組む。
build.py（概要版）はこのモジュールを使わず、そのまま残してある。"""
import os
import zipfile

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

D = os.path.dirname(os.path.abspath(__file__)) + "/"
IMG = D + "img/"
FONT = "Klee One"

INK = RGBColor(0x33, 0x30, 0x2B)
SUB = RGBColor(0x74, 0x70, 0x6A)
ORANGE = RGBColor(0xC9, 0x7C, 0x4B)
TEAL = RGBColor(0x3E, 0x9C, 0x86)
INDIGO = RGBColor(0x5A, 0x6B, 0xB0)
OLIVE = RGBColor(0x7F, 0x94, 0x63)
PLUM = RGBColor(0x9B, 0x6E, 0x8F)
WHITE = RGBColor(0xFD, 0xFB, 0xF8)

CENTER = PP_ALIGN.CENTER
MIDDLE = MSO_ANCHOR.MIDDLE


class Deck:
    def __init__(self):
        self.prs = Presentation(D + "tpl.pptx")
        self.SW, self.SH = self.prs.slide_width, self.prs.slide_height
        z = zipfile.ZipFile(D + "tpl.pptx")
        open(D + "bg_cover.png", "wb").write(z.read("ppt/media/image2.png"))
        open(D + "bg_section.png", "wb").write(z.read("ppt/media/image1.png"))
        lst = self.prs.slides._sldIdLst
        for sid in list(lst):
            self.prs.part.drop_rel(sid.rId)
            lst.remove(sid)
        self.L_BLANK = self.prs.slide_layouts[6]
        self.L_SECTION = self.prs.slide_layouts[2]
        self.L_TITLE = self.prs.slide_layouts[0]

    # ---- 文字・図
    @staticmethod
    def _font(run, size, color, bold=False):
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        rPr = run._r.get_or_add_rPr()
        for tag in ("a:latin", "a:ea", "a:cs"):
            el = rPr.find(qn(tag))
            if el is None:
                el = etree.SubElement(rPr, qn(tag))
            el.set("typeface", FONT)

    def text(self, s, x, y, w, h, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, spacing=None, name=None):
        """paras: str か、[str | [(text, {size,color,bold})...]] のリスト"""
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.04)
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        tf.vertical_anchor = anchor
        if isinstance(paras, str):
            paras = [paras]
        for i, p in enumerate(paras):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = align
            if spacing:
                para.space_after = Pt(spacing)
            runs = [(p, {})] if isinstance(p, str) else p
            for t, o in runs:
                r = para.add_run()
                r.text = t
                self._font(r, o.get("size", size), o.get("color", color), o.get("bold", bold))
        return tb

    def pic(self, s, name, x, y, w=None, h=None, alt=""):
        kw = {}
        if w is not None:
            kw["width"] = Inches(w)
        if h is not None:
            kw["height"] = Inches(h)
        p = s.shapes.add_picture(IMG + name, Inches(x), Inches(y), **kw)
        p._element.nvPicPr.cNvPr.set("descr", alt)
        return p

    def _bg(self, s, path):
        p = s.shapes.add_picture(path, 0, 0, self.SW, self.SH)
        p._element.nvPicPr.cNvPr.set("descr", "")
        sp = s.shapes._spTree
        sp.remove(p._element)
        sp.insert(2, p._element)

    @staticmethod
    def _clear(s):
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)

    def notes(self, s, t):
        s.notes_slide.notes_text_frame.text = t

    # ---- スライドの型
    def cover(self, kicker, title, subtitle, foot, hero="hero.png", notes=""):
        s = self.prs.slides.add_slide(self.L_TITLE)
        self._clear(s)
        self._bg(s, D + "bg_cover.png")
        self.text(s, 0.75, 1.6, 7.4, 0.6, kicker, size=22, color=SUB)
        self.text(s, 0.75, 2.2, 7.4, 1.3, title, size=66, bold=True)
        self.text(s, 0.75, 3.55, 7.2, 1.4, subtitle, size=24)
        self.text(s, 0.75, 5.3, 7.0, 0.5, foot, size=18, color=SUB)
        self.pic(s, hero, 7.7, 2.3, w=5.2, alt="机でノートパソコンに向かう人")
        if notes:
            self.notes(s, notes)
        return s

    def content(self, title, notes=""):
        s = self.prs.slides.add_slide(self.L_BLANK)
        self._clear(s)
        self.text(s, 0.6, 0.35, 12.1, 0.9, title, size=32, bold=True, anchor=MIDDLE, name="Title")
        if notes:
            self.notes(s, notes)
        return s

    def section(self, num, title, sub, notes=""):
        s = self.prs.slides.add_slide(self.L_SECTION)
        self._clear(s)
        self._bg(s, D + "bg_section.png")
        self.text(s, 0.8, 3.0, 9.0, 1.2, f"{num}.", size=60, color=ORANGE, bold=True)
        self.text(s, 0.8, 4.2, 11.5, 1.0, title, size=40, bold=True)
        self.text(s, 0.8, 5.25, 11.5, 0.7, sub, size=20, color=SUB)
        if notes:
            self.notes(s, notes)
        return s

    def closing(self, title, msgs, notes=""):
        s = self.prs.slides.add_slide(self.L_TITLE)
        self._clear(s)
        self._bg(s, D + "bg_cover.png")
        self.pic(s, "fr_wide.png", 0.55, 1.85, w=12.2, h=5.0, alt="")
        self.text(s, 0.75, 0.75, 11.5, 0.9, title, size=40, bold=True)
        for i, (t, d) in enumerate(msgs):
            y = 2.25 + i * 1.5
            self.pic(s, ["n1.png", "n2.png", "n3.png"][i], 1.0, y, w=0.85, alt="")
            self.text(s, 2.15, y - 0.02, 10.3, 0.6, t, size=24, bold=True)
            self.text(s, 2.15, y + 0.62, 10.3, 0.6, d, size=16, color=SUB)
        if notes:
            self.notes(s, notes)
        return s

    # ---- よく使う組み
    def lead(self, s, runs, y=1.45, size=22):
        """題の下の 1 行の要点（runs は [(text, opts)]）"""
        self.text(s, 0.8, y, 11.8, 0.9, [runs], size=size)

    def cards(self, s, items, y=2.7, h=3.9, icon_h=1.6, desc_size=15):
        """items: [(icon, title, desc, color)] を横に並べる（3〜4 枚）"""
        n = len(items)
        gap = 0.3
        w = (11.9 - gap * (n - 1)) / n
        for i, (im, t, d, col) in enumerate(items):
            x = 0.7 + i * (w + gap)
            self.pic(s, "fr_card.png", x, y, w=w, h=h, alt="")
            if im:
                self.pic(s, im, x + w / 2 - icon_h * 0.6, y + 0.2, h=icon_h, alt=t)
            ty = y + (0.3 + icon_h if im else 0.35)
            self.text(s, x + 0.2, ty, w - 0.4, 0.55, t, size=21, color=col, bold=True, align=CENTER)
            self.text(s, x + 0.25, ty + 0.6, w - 0.5, h - (ty - y) - 0.7, d, size=desc_size)

    def rows(self, s, items, y=1.55, h=5.4, label_w=3.2, size=17, frame="fr_wide.png", step=None):
        """items: [(label, desc, color)] を縦に並べた表"""
        self.pic(s, frame, 0.6, y - 0.1, w=12.1, h=h, alt="")
        step = step or (h - 0.4) / len(items)
        for i, (lab, desc, col) in enumerate(items):
            yy = y + 0.15 + i * step
            self.text(s, 0.95, yy, label_w, step, lab, size=size + 1, color=col, bold=True)
            self.text(s, 0.95 + label_w + 0.2, yy, 11.5 - label_w - 0.4, step, desc, size=size)

    def bullets(self, s, items, x=0.9, y=1.6, w=11.6, size=19, bullet_img="ok.png", step=0.82):
        for i, t in enumerate(items):
            yy = y + i * step
            self.pic(s, bullet_img, x, yy + 0.05, w=0.42, alt="")
            self.text(s, x + 0.6, yy, w - 0.6, step, t, size=size)

    def save(self, name):
        out = D + name
        self.prs.save(out)
        print(out, len(self.prs.slides))
