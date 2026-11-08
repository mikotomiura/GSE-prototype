#!/usr/bin/env python3
"""Draw the README figure of the stall--score association, from the paper's figure data.

Usage:
  python3 -I tools/readme_media.py            writes docs/media/score.svg
  python3 -I tools/readme_media.py --check    checks that the SVG on disk is the one this script draws
Reads only paper/figdata/score.csv (aggregate values per definition: Spearman's rho of the stall rate and the
KLiCKe holistic score with its 95% interval, unadjusted and given essay and observation length).
No number of the paper comes from this script. Exit code: 0 = written or checked / 1 = a mismatch.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "paper/figdata/score.csv")
OUT = os.path.join(ROOT, "docs/media/score.svg")
SURF, INK, MUTED, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#eeeeea"
QUANT, FIXED = "#2a78d6", "#eb6834"   # categorical slots 1 and 2
W, PH, ML, MR, MT, GAP = 760, 210, 64, 16, 56, 64
Y0, Y1 = -0.35, 0.20


def read():
    lines = open(DATA, encoding="utf-8").read().split("\n")
    head = lines[0].split()
    rows = [dict(zip(head, map(float, x.split()))) for x in lines[1:] if x.strip()]
    return sorted(rows, key=lambda r: r["i"])


def panel(rows, top, keys, title):
    v, lo, hi = keys
    n = len(rows)
    sx = lambda i: ML + (i + 0.5) * (W - ML - MR) / n
    sy = lambda y: top + (Y1 - y) / (Y1 - Y0) * PH
    out = ['<text x="%d" y="%d" font-size="13" fill="%s">%s</text>' % (ML, top - 10, INK, title),
           '<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (ML, sy(0.1), W - ML - MR, sy(-0.1) - sy(0.1), BAND)]
    for t in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2):
        out.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"/>'
                   % (ML, W - MR, sy(t), sy(t), MUTED if t == 0 else GRID, "1" if t == 0 else "0.6"))
        out.append('<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end">%+.1f</text>'
                   % (ML - 6, sy(t) + 4, MUTED, t) if t else
                   '<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end">0</text>' % (ML - 6, sy(t) + 4, MUTED))
    for k, r in enumerate(rows):
        c = QUANT if r["fam"] == 1 else FIXED
        x = sx(k)
        out.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="2" stroke-opacity="0.45"/>'
                   % (x, x, sy(r[hi]), sy(r[lo]), c))
        if r["b0"] == 1:
            out.append('<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s" stroke="%s" stroke-width="2"/>' % (x, sy(r[v]), INK, SURF))
        else:
            out.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s" stroke="%s" stroke-width="1"/>' % (x, sy(r[v]), c, SURF))
    return out


def draw():
    rows = read()
    h = MT + 2 * PH + GAP + 40
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'font-family="Helvetica, Arial, sans-serif" role="img" aria-label="Stall rate and essay score across 90 '
         'definitions, unadjusted and given length">' % (W, h, W, h),
         '<rect width="100%%" height="100%%" fill="%s"/>' % SURF,
         '<text x="%d" y="22" font-size="14" font-weight="bold" fill="%s">Spearman correlation of the stall rate with '
         'the essay score (KLiCKe), 90 definitions</text>' % (ML, INK)]
    lx = ML
    for c, label in ((QUANT, "writer-quantile threshold (54)"), (FIXED, "fixed threshold (36)"), (INK, "baseline")):
        s.append('<circle cx="%d" cy="38" r="4" fill="%s"/>' % (lx + 4, c))
        s.append('<text x="%d" y="42" font-size="12" fill="%s">%s</text>' % (lx + 13, MUTED, label))
        lx += 13 + 7 * len(label) + 24
    s.append('<rect x="%d" y="32" width="14" height="10" fill="%s"/>' % (lx, BAND))
    s.append('<text x="%d" y="42" font-size="12" fill="%s">within &#177;0.1</text>' % (lx + 19, MUTED))
    s += panel(rows, MT + 20, ("rho", "lo", "hi"), "(a) Unadjusted, definitions ordered by the correlation")
    s += panel(rows, MT + 20 + PH + GAP, ("ln", "llo", "lhi"), "(b) Given essay length and length of observation, same order")
    s.append('<text x="%d" y="%d" font-size="11" fill="%s">Bars: 95%% intervals from 2,000 resamples of writers. '
             'Source: paper/figdata/score.csv.</text>' % (ML, h - 10, MUTED))
    s.append("</svg>")
    return "\n".join(s) + "\n"


def main(argv):
    svg = draw()
    if argv == ["--check"]:
        ok = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == svg
        print("readme figure: " + ("matches" if ok else "differs from the script"))
        return 0 if ok else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print("wrote " + OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
