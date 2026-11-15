"""テンプレート（tpl.pptx = deck_temp_template-original.pptx の写し）の上に GSE のプロジェクト概要のデッキを組む。

使い方は同じフォルダの README.md。"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

import os
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

prs = Presentation(D + "tpl.pptx")
SW, SH = prs.slide_width, prs.slide_height

# 背景画像（テンプレートの表紙と区切りの画像）をテンプレートの slide から取り出しておく
import zipfile
z = zipfile.ZipFile(D + "tpl.pptx")
open(D + "bg_cover.png", "wb").write(z.read("ppt/media/image2.png"))
open(D + "bg_section.png", "wb").write(z.read("ppt/media/image1.png"))

# 元の 7 枚を外す
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)

L_BLANK = prs.slide_layouts[6]  # クリームの地
L_SECTION = prs.slide_layouts[2]
L_TITLE = prs.slide_layouts[0]


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


def text(slide, x, y, w, h, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=None, name=None):
    """paras: str か、[str | [(text, {size,color,bold})...]] のリスト"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
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
            _font(r, o.get("size", size), o.get("color", color), o.get("bold", bold))
    return tb


def pic(slide, name, x, y, w=None, h=None, alt=""):
    kw = {}
    if w is not None:
        kw["width"] = Inches(w)
    if h is not None:
        kw["height"] = Inches(h)
    p = slide.shapes.add_picture(IMG + name if not name.startswith("/") else name, Inches(x), Inches(y), **kw)
    p._element.nvPicPr.cNvPr.set("descr", alt)
    return p


def bg(slide, path):
    p = slide.shapes.add_picture(path, 0, 0, SW, SH)
    p._element.nvPicPr.cNvPr.set("descr", "")
    # 一番後ろへ
    sp = slide.shapes._spTree
    sp.remove(p._element)
    sp.insert(2, p._element)


def clear_placeholders(slide):
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)


def content(title_text, notes=""):
    s = prs.slides.add_slide(L_BLANK)
    clear_placeholders(s)
    text(s, 0.6, 0.35, 12.1, 0.9, title_text, size=34, bold=True, anchor=MSO_ANCHOR.MIDDLE, name="Title")
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def section(num, title_text, sub, notes=""):
    s = prs.slides.add_slide(L_SECTION)
    clear_placeholders(s)
    bg(s, D + "bg_section.png")
    text(s, 0.8, 3.0, 9.0, 1.2, f"{num}.", size=60, color=ORANGE, bold=True)
    text(s, 0.8, 4.2, 11.0, 1.0, title_text, size=44, bold=True)
    text(s, 0.8, 5.25, 11.0, 0.7, sub, size=20, color=SUB)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


# ======================================================================
# 1 表紙
s = prs.slides.add_slide(L_TITLE)
clear_placeholders(s)
bg(s, D + "bg_cover.png")
text(s, 0.75, 1.6, 7.4, 0.6, "Generative Struggle Engine", size=22, color=SUB)
text(s, 0.75, 2.2, 7.4, 1.3, "GSE", size=80, bold=True)
text(s, 0.75, 3.55, 7.2, 1.4, "書いた中身を見ない観測で、パソコン作業の「止まり」について何が言えるかを確かめる研究", size=26)
text(s, 0.75, 5.3, 7.0, 0.5, "プロジェクト概要 ・ 2026 年 11 月", size=18, color=SUB)
pic(s, "hero.png", 7.7, 2.3, w=5.2, alt="机でノートパソコンに向かう人。画面に打鍵のリズムの棒、横に考え中の吹き出し")
s.notes_slide.notes_text_frame.text = ("GSE は、パソコンで作業しているときの「止まり」を、書いた中身を見ずに観測し、その観測から何が言えて何が言えないかを確かめる研究です。"
                                       "今日は、何をしている研究か、これまでに分かったこと、これからの設計の 3 つを話します。")

# 2 目次
s = content("今日のお話", "3 つの順に話します。")
items = [("n1.png", "GSE ってなに？", "何を見て、何を見ないか"),
         ("n2.png", "これまでに分かったこと", "公開データで確かめた結果と、問いの変え方"),
         ("n3.png", "これからの設計と今の状況", "段 1・手跡・段 2 と、どこまで進んだか")]
for i, (ic, t, sub) in enumerate(items):
    y = 1.75 + i * 1.65
    pic(s, ic, 1.2, y, w=1.15, alt=f"番号 {i + 1}")
    text(s, 2.65, y + 0.12, 8.5, 0.6, t, size=28, bold=True)
    text(s, 2.65, y + 0.72, 8.5, 0.5, sub, size=18, color=SUB)
pic(s, "data.png", 9.6, 2.2, w=3.0, alt="書類と虫眼鏡")

# 3 区切り 1
section(1, "GSE ってなに？", "何を見て、何を見ないか")

# 4 ひとことで
s = content("ひとことで言うと",
            "GSE は、キーを打った時刻と種類などから作業の止まりを観測します。その観測から言えることを、3 つの検査で確かめます。"
            "前もって当てられるか、数え方を変えても結論が残るか、書いていないはずの中身がもれないか、の 3 つです。")
text(s, 0.8, 1.55, 11.8, 1.2,
     [[("書いた中身を見ない観測で、止まりについて", {}), ("どこまで言えるかを 3 つの検査で確かめる", {"color": TEAL, "bold": True})]],
     size=26)
cards = [("observe.png", "予測", "止まりを前もって当てられるか", ORANGE),
         ("data.png", "定義", "止まりの数え方を変えても、結論が残るか", INDIGO),
         ("i_lock.png", "漏れ", "保存していない中身が、観測からもれないか", TEAL)]
for i, (im, t, d, col) in enumerate(cards):
    x = 0.8 + i * 4.05
    pic(s, "fr_card.png", x, 2.95, w=3.7, h=3.95, alt="")
    pic(s, im, x + 0.85, 3.15, h=1.9, alt=t)
    text(s, x + 0.3, 5.1, 3.1, 0.55, t, size=24, color=col, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.35, 5.7, 3.0, 1.0, d, size=15, color=INK)

# 5 見るもの・見ないもの
s = content("見ているもの・見ないもの",
            "見ているのは、いつ・どの種類のキーを押したか、前面のアプリが替わった時刻、ポインタの動きの量、貼り付けた文字数です。"
            "打った文字や貼り付けた本文、ウィンドウの名前、URL は記録しません。")
pic(s, "fr_card.png", 0.7, 1.45, w=5.9, h=5.55, alt="")
pic(s, "fr_card.png", 6.85, 1.45, w=5.8, h=5.55, alt="")
text(s, 1.0, 1.65, 5.3, 0.6, "見ているもの", size=26, color=TEAL, bold=True)
pic(s, "observe.png", 1.2, 2.3, w=3.4, alt="キーボードと、打鍵の時刻の目盛り")
for i, t in enumerate(["いつ・どの種類のキーを押したか", "前面のアプリが替わった時刻", "ポインタの動きの量（1 秒ごと）", "貼り付けた文字数"]):
    y = 5.05 + i * 0.45
    pic(s, "ok.png", 1.05, y, w=0.38, alt="")
    text(s, 1.55, y - 0.02, 4.9, 0.45, t, size=17)
text(s, 7.15, 1.65, 5.2, 0.6, "見ないもの", size=26, color=ORANGE, bold=True)
pic(s, "notsaved.png", 7.6, 2.3, w=3.3, alt="文字の書かれた紙にばつ印と鍵")
for i, t in enumerate(["打った文字そのもの", "貼り付けた本文", "ウィンドウの名前・URL", "どのアプリを使ったか"]):
    y = 5.05 + i * 0.45
    pic(s, "todo.png", 7.2, y, w=0.38, alt="")
    text(s, 7.7, y - 0.02, 4.8, 0.45, t, size=17)

# 6 止まりの中身
s = content("ひとつの「止まり」の中身はいろいろ",
            "キーが止まっているとき、人は詰まっていることもあれば、考えている、資料を読んでいる、話している、席を外していることもあります。"
            "止まり＝悪い、ではありません。GSE はこの中身をどこまで見分けられるかを確かめます。")
pic(s, "fr_wide.png", 0.6, 1.6, w=12.1, h=3.6, alt="")
labs = [("詰まり", ORANGE), ("考えている", INDIGO), ("資料を読む", TEAL), ("話している", OLIVE), ("席を外す", PLUM)]
for i, (t, col) in enumerate(labs):
    x = 0.95 + i * 2.37
    pic(s, f"st{i}.png", x, 2.0, w=2.0, alt=t)
    text(s, x - 0.1, 3.95, 2.2, 0.6, t, size=22, color=col, bold=True, align=PP_ALIGN.CENTER)
text(s, 0.8, 5.55, 11.8, 1.3,
     [[("止まり＝悪い、ではない。", {"bold": True}), ("考える・調べる・話すのも止まりの一部。", {})],
      [("GSE は、この中身を", {}), ("どこまで見分けられるか", {"color": TEAL, "bold": True}), ("を確かめる。", {})]],
     size=22, spacing=6)

# 7 区切り 2
section(2, "これまでに分かったこと", "公開データで確かめた結果と、問いの変え方")

# 8 公開データ
s = content("まず、公開されている打鍵のデータで確かめた",
            "人を集める前に、研究用に公開されている打鍵の記録 3 種で、止まりを前もって当てられるかを確かめました。"
            "AI と一緒に文章を書く課題、学生の作文、プログラミングの授業の記録です。")
pic(s, "data.png", 0.9, 1.7, w=4.6, alt="3 枚の書類と虫眼鏡")
rows = [("AI と一緒に文章を書く課題", "CoAuthor", INDIGO), ("学生の作文", "KLiCKe", TEAL), ("プログラミングの授業", "CS1", OLIVE)]
for i, (t, nm, col) in enumerate(rows):
    y = 1.8 + i * 1.25
    pic(s, "fr_small.png", 6.0, y, w=6.6, h=1.05, alt="")
    text(s, 6.35, y + 0.18, 4.4, 0.7, t, size=22, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 10.6, y + 0.18, 1.8, 0.7, nm, size=18, color=col, anchor=MSO_ANCHOR.MIDDLE)
text(s, 6.0, 5.75, 6.7, 1.0,
     [[("問い: ", {"bold": True}), ("止まりや AI への頼みごとの", {}), ("手前 30 秒", {"color": ORANGE, "bold": True}), ("に、前ぶれは見えるか", {})]],
     size=20)

# 9 結果1
s = content("結果 1 ・ 今の推定器では、前もって当てられなかった",
            "今の推定器の当てる力を表す AUC は 0.49〜0.52 でした。0.5 は当てずっぽうと同じです。単純な学習器は 0.54〜0.57 で、小さな手がかりがあるかどうかまでは否定できません。"
            "止まりの長さで知らせる案も試しましたが、1 時間に 124〜182 回も鳴り、本当に長い止まりに至るのは 6.3〜9.1% でした。")
pic(s, "coin.png", 0.9, 1.7, w=3.6, alt="0.5 と書かれたコイン")
text(s, 4.9, 1.75, 7.8, 1.2, "0.49〜0.52", size=66, color=ORANGE, bold=True)
text(s, 4.95, 3.0, 7.6, 1.0, "当てる力（AUC）。0.5 は当てずっぽうと同じ", size=20, color=INK)
text(s, 4.95, 3.55, 7.6, 0.6, "※ 単純な学習器は 0.54〜0.57。小さな手がかりは否定できない", size=15, color=SUB)
pic(s, "bell.png", 1.3, 4.9, w=1.9, alt="たくさんの通知のベル")
text(s, 4.9, 4.75, 7.8, 0.8, [[("124〜182 回 / 時", {"size": 40, "color": ORANGE, "bold": True})]])
text(s, 4.95, 5.6, 7.6, 1.0, "止まりの長さで知らせると、こんなに鳴る。本当に長い止まりに至るのは 6.3〜9.1%", size=18)

# 10 結果2
s = content("結果 2 ・ 止まりは短く、ありふれ、混ざる",
            "止まりの半分は十数秒以内に終わります。手の操作や貼り付けも混ざっています。"
            "3 つのデータで同じ向きに出たのは、前が沈黙だけの止まりは長引く、ということだけでした。"
            "今の推定がどれだけ止まりらしいと言うかは、データによって 2.2%〜26% と大きく違いました。")
stats = [("stopwatch.png", "半分は", "十数秒以内", "止まりの多くはすぐ終わる", TEAL),
         ("st0.png", "手の動きも", "混ざる", "クリックや貼り付けを含む止まりも多い", ORANGE),
         ("coin.png", "推定の水準は", "2.2%〜26%", "データによって桁で違う（較正されていない）", INDIGO)]
for i, (im, a, big, d, col) in enumerate(stats):
    x = 0.7 + i * 4.15
    pic(s, "fr_card.png", x, 1.5, w=3.85, h=5.4, alt="")
    pic(s, im, x + 1.0, 1.75, h=1.85, alt=big)
    text(s, x + 0.3, 3.8, 3.25, 0.5, a, size=18, color=SUB, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, 4.25, 3.45, 0.9, big, size=34, color=col, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.35, 5.3, 3.15, 1.3, d, size=16)

# 11 問いを変えた
s = content("だから、問いを変えた",
            "はじめは、推定で止まりを当てて、止まる前に手を出すことを目指していました。前ぶれが見えず、数え方で結論が動き、中身がもれうることも分かったので、"
            "推定を磨く前に、この観測で何が言えて何が言えないかを、3 つの検査で確かめる問いに変えました。")
pic(s, "fr_gray.png", 0.6, 1.55, w=5.4, h=3.6, alt="")
text(s, 0.95, 1.8, 4.7, 0.5, "はじめの問い", size=20, color=SUB, bold=True)
text(s, 0.95, 2.45, 4.7, 1.5, ["推定で止まりを当てて", "「詰まる前に」手を出す"], size=26, color=SUB)
text(s, 0.95, 4.15, 4.7, 0.6, "→ 前ぶれは見えなかった", size=18, color=ORANGE)
pic(s, "arrow.png", 6.05, 2.75, w=1.3, alt="右向きの矢印")
pic(s, "fr_teal.png", 7.35, 1.55, w=5.4, h=3.6, alt="")
text(s, 7.7, 1.8, 4.7, 0.5, "いまの問い", size=20, color=TEAL, bold=True)
text(s, 7.7, 2.45, 4.8, 1.5, ["中身を見ない観測で、", "何が言えて何が言えないか"], size=26)
text(s, 7.7, 4.15, 4.7, 0.6, "→ 予測・定義・漏れの 3 つの検査", size=18, color=TEAL)
text(s, 0.8, 5.55, 11.8, 1.3,
     [[("「当てられない」ことも結果。", {"bold": True}), ("検査の結果で、系が判断に使う量と使わない量を決める。", {})]],
     size=22)

# 12 区切り 3
section(3, "これからの設計と今の状況", "段 1 ・ 手跡 ・ 段 2")

# 13 段1
s = content("段 1 ・ 何も出さずに、本人に聞く",
            "段 1 では介入を何も出さず、本人に聞きます。決まった時刻ではなく無作為な時刻に、"
            "摩擦・前進の 2 問と、直前 30 秒に何をしていたかの 6 択を聞きます。日の終わりにも 1 問だけ聞きます。"
            "答えなくても構いません。")
pic(s, "probecard.png", 0.8, 1.6, w=4.9, alt="2 つの 5 段階の問いと 6 択のカード")
steps = [("無作為な時刻に、画面の隅に 3 問", "摩擦と前進（1〜5）、直前 30 秒の中身（6 択）"),
         ("日の終わりに 1 問", "今日の作業について、1〜5 で 1 つだけ"),
         ("答えなくてよい・理由は聞かない", "一時停止・区間の削除・やめることはいつでも")]
for i, (t, d) in enumerate(steps):
    y = 1.75 + i * 1.6
    pic(s, ["n1.png", "n2.png", "n3.png"][i], 6.2, y, w=0.75, alt="")
    text(s, 7.15, y - 0.02, 5.6, 0.6, t, size=22, bold=True)
    text(s, 7.15, y + 0.6, 5.6, 0.8, d, size=16, color=SUB)

# 14 進め方
s = content("段 1 の進め方",
            "まず研究者本人が macOS で試します。問題がなければ、結果を見る前に解析の約束を固め（事前登録の凍結）、"
            "本人以外の 3 名で確かめます。審査を通した後の群では、同じ約束のまま再現を見ます。その後に段 2 に進みます。")
pic(s, "roadmap.png", 0.6, 1.9, w=12.1, alt="1 から 5 の番号の円を結ぶ道")
labels = [("本人で試す", "macOS で前期→後期"), ("約束を固める", "事前登録の凍結"),
          ("3 名で確かめる", "両 OS・作業の様式が違う"), ("審査の後に再現", "同じ約束のまま"), ("段 2", "招待の効果を見る")]
for i, (t, d) in enumerate(labels):
    cx = 0.6 + (90 + i * 250) / 1180 * 12.1
    text(s, cx - 1.2, 3.95, 2.4, 0.6, t, size=20, bold=True, align=PP_ALIGN.CENTER)
    text(s, cx - 1.2, 4.5, 2.4, 0.8, d, size=14, color=SUB, align=PP_ALIGN.CENTER)
text(s, 2.05, 2.05, 2.0, 0.5, "← いまここ", size=18, color=ORANGE, bold=True)
text(s, 0.8, 5.6, 11.8, 1.2,
     [[("人数より、", {}), ("1 人を長く深く見る", {"color": TEAL, "bold": True}), ("。主張は「その人の中で何が起きたか」と、人をまたいだ再現まで。", {})]],
     size=20)

# 15 手跡
s = content("手跡 ・ 判断しない所では、手の跡だけを返す",
            "系が判断を控える所でも、本人の手の跡は返します。画面の背景の草や霧と、画面の下の縁が、自分の打鍵やポインタの動きでゆれます。"
            "返すのは速さ・リズム・止まりといった行為の性質だけで、系の判断や数字は返しません。段 1 の後半に、日ごとに無作為に出します。")
pic(s, "handmark.png", 0.7, 1.55, w=6.2, alt="草と霧の背景が、打鍵でなびいている画面")
text(s, 7.3, 1.65, 5.4, 0.6, "返すもの", size=24, color=TEAL, bold=True)
for i, t in enumerate(["打つ速さ", "リズム", "止まり"]):
    y = 2.35 + i * 0.5
    pic(s, "ok.png", 7.35, y, w=0.38, alt="")
    text(s, 7.85, y - 0.02, 4.8, 0.45, t, size=19)
text(s, 7.3, 4.05, 5.4, 0.6, "返さないもの", size=24, color=ORANGE, bold=True)
for i, t in enumerate(["系の判断（止まりの中身の推定など）", "数字・点数・順位・累計"]):
    y = 4.75 + i * 0.5
    pic(s, "todo.png", 7.35, y, w=0.38, alt="")
    text(s, 7.85, y - 0.02, 4.8, 0.45, t, size=19)
text(s, 7.3, 5.95, 5.4, 0.9, "カーソルの位置などは、絵を動かすだけで記録しない", size=15, color=SUB)

# 16 段2
s = content("段 2 ・ 止まりの中で、そっと誘う",
            "段 2 では、止まりの中のふさわしい時点ごとに、招待を出すか出さないかを無作為に決め、1 人ずつ効果を見ます。"
            "招待は画面の隅の、文字のない小さな印です。離れるのも続けるのも自由で、系は点数を付けず、完了も測りません。")
pic(s, "invite.png", 0.6, 1.6, w=6.0, alt="画面の隅の小さな印と、伸びをする人")
pts = [("出す・出さないを無作為に", "止まりの中のふさわしい時点ごとに決める"),
       ("1 人ずつ効果を見る", "その人の中で、出した時と出さない時を比べる"),
       ("採点しない", "離れるのも続けるのも自由。完了も測らない")]
for i, (t, d) in enumerate(pts):
    y = 1.75 + i * 1.6
    pic(s, ["n1.png", "n2.png", "n3.png"][i], 7.0, y, w=0.7, alt="")
    text(s, 7.85, y - 0.02, 4.9, 0.6, t, size=22, bold=True)
    text(s, 7.85, y + 0.6, 4.9, 0.8, d, size=16, color=SUB)

# 17 大切にしていること
s = content("大切にしていること",
            "本文を保存しないこと、言えない所の量は判断に使わないこと、数字で採点しないこと、1 人を長く深く見ることの 4 つです。")
vals = [("i_lock.png", "本文を保存しない", "打った文字・貼り付けた中身は記録も送信もしない", TEAL),
        ("i_hand.png", "判断を控える", "言えない所の量は、系の判断に使わない", ORANGE),
        ("i_noscore.png", "数字で採点しない", "点数・順位・達成度を本人に返さない", PLUM),
        ("i_person.png", "1 人を長く深く", "少ない人数でも、その人の中の変化を丁寧に見る", INDIGO)]
for i, (im, t, d, col) in enumerate(vals):
    x = 0.7 + (i % 2) * 6.1
    y = 1.5 + (i // 2) * 2.75
    pic(s, "fr_small.png", x, y, w=5.8, h=2.5, alt="")
    pic(s, im, x + 0.3, y + 0.45, w=1.6, alt=t)
    text(s, x + 2.1, y + 0.45, 3.5, 0.6, t, size=24, color=col, bold=True)
    text(s, x + 2.1, y + 1.1, 3.45, 1.1, d, size=16)

# 18 今の状況
s = content("今の状況（2026 年 11 月）",
            "記録の基盤と公開データの分析は済みました。段 1 の準備と手跡の macOS 版が進行中で、3 名での確認と段 2 はこれからです。")
rows = [("ok.png", "記録の基盤（両 OS・本文を保存しない・削除と提出）", "できた", TEAL),
        ("ok.png", "公開データでの分析（13 本）", "できた", TEAL),
        ("wip.png", "段 1 の準備（問いの仕組み・事前登録の値）", "進行中", ORANGE),
        ("wip.png", "手跡（macOS）", "進行中", ORANGE),
        ("todo.png", "手跡（Windows）・3 名での確認", "これから", SUB),
        ("todo.png", "段 2（招待の効果）", "これから", SUB)]
pic(s, "fr_wide.png", 0.6, 1.45, w=12.1, h=5.5, alt="")
for i, (im, t, st, col) in enumerate(rows):
    y = 1.85 + i * 0.8
    pic(s, im, 1.0, y, w=0.5, alt=st)
    text(s, 1.75, y + 0.02, 8.3, 0.5, t, size=20)
    text(s, 10.3, y + 0.02, 2.1, 0.5, st, size=20, color=col, bold=True)

# 19 まとめ
s = prs.slides.add_slide(L_TITLE)
clear_placeholders(s)
bg(s, D + "bg_cover.png")
pic(s, "fr_wide.png", 0.55, 1.85, w=12.2, h=5.0, alt="")
text(s, 0.75, 0.75, 11.5, 0.9, "まとめ", size=40, bold=True)
msgs = [("中身を見ない観測で、止まりについて何が言えるかを確かめる", "当てるのは難しく、数え方で結論が動き、中身はもれうると分かった"),
        ("言えない所の量は、系の判断に使わない", "判断の代わりに手の跡だけを返す（手跡）。記録は集計だけを外に出す"),
        ("次は検査の道具を作り、本人で試してから 3 名で確かめる", "その後、止まりの中の招待の効果を見る（段 2）")]
for i, (t, d) in enumerate(msgs):
    y = 2.25 + i * 1.5
    pic(s, ["n1.png", "n2.png", "n3.png"][i], 1.0, y, w=0.85, alt="")
    text(s, 2.15, y - 0.02, 10.3, 0.6, t, size=26, bold=True)
    text(s, 2.15, y + 0.62, 10.3, 0.6, d, size=18, color=SUB)
s.notes_slide.notes_text_frame.text = "3 つにまとめます。ご質問をどうぞ。"

out = D + "GSE_project_overview.pptx"
prs.save(out)
print(out, len(prs.slides))
