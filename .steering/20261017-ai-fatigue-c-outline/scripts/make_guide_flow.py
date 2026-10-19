"""Draw the order of the work for the co-author guide (coauthor-guide.md, section 0).

Run: uv run --with matplotlib python make_guide_flow.py <out.png>

The co-author's three rounds are filled; the researcher's steps are outlined. No dates.
"""
import sys

import matplotlib
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

for path in ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"):
    font_manager.fontManager.addfont(path)
plt.rcParams["font.family"] = "Hiragino Sans"

# (who, title, detail); who = "me" (researcher) or "co" (co-author)
STEPS = [
    ("co", "いま", "名前・所属\nできる範囲"),
    ("me", "登録", "役割を書いて\nOSF に登録"),
    ("co", "1 回目", "題名と抄録\n113 件"),
    ("co", "2 回目", "全文の段\n回った全部"),
    ("co", "3 回目", "符号化\n30 本ほど"),
    ("co", "原稿", "原稿を読む\n投稿を承認"),
]
CO, ME, LINE = "#2f5f8a", "#ffffff", "#2f5f8a"


def main(out: str) -> None:
    w, h, gap = 2.6, 1.5, 0.45
    fig, ax = plt.subplots(figsize=(len(STEPS) * (w + gap) * 0.40, 1.55))
    for i, (who, title, detail) in enumerate(STEPS):
        x = i * (w + gap)
        fill = CO if who == "co" else ME
        text = "#ffffff" if who == "co" else "#1f2a36"
        ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=fill, edgecolor=LINE, linewidth=1.4))
        ax.text(x + w / 2, h * 0.72, title, ha="center", va="center", fontsize=10, weight="bold", color=text)
        ax.text(x + w / 2, h * 0.32, detail, ha="center", va="center", fontsize=8, color=text, linespacing=1.4)
        if i < len(STEPS) - 1:
            ax.annotate("", xy=(x + w + gap - 0.05, h / 2), xytext=(x + w + 0.05, h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=LINE, lw=1.4))
    total = len(STEPS) * (w + gap) - gap
    ax.add_patch(FancyBboxPatch((0, -0.62), 0.3, 0.22, boxstyle="round,pad=0.01", facecolor=CO, edgecolor=LINE))
    ax.text(0.4, -0.51, "共著者にお願いするところ（各回の後に、食い違いを一緒に決める話し合い）", va="center",
            fontsize=8, color="#1f2a36")
    ax.set_xlim(-0.1, total + 0.1)
    ax.set_ylim(-0.75, h + 0.1)
    ax.axis("off")
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.05)


if __name__ == "__main__":
    main(sys.argv[1])
