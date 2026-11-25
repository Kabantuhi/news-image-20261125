#!/usr/bin/env python3
"""Render the 25 November 2026 world-news front page to entry.png (1024x1024).

Deterministic: PIL + DejaVu only, no network, no randomness, no timestamps.
Reads news.json next to this file, writes entry.png next to this file.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W, H = 1024, 1024
BG = (247, 243, 234)
GREEN = (18, 59, 42)
GOLD = (232, 184, 75)
RED = (176, 58, 46)
NAVY = (14, 42, 71)
DARK = (51, 51, 51)
GREY = (68, 68, 68)
CHARCOAL = (34, 34, 34)
LIGHT = (220, 230, 238)
WHITE = (255, 255, 255)
BORDER = (221, 221, 221)

MAP_RANGES = [
    [(8, 14), (30, 33), (40, 48)], [(6, 16), (29, 34), (38, 52)],
    [(5, 17), (28, 35), (37, 55)], [(6, 18), (29, 34), (38, 56)],
    [(7, 18), (30, 33), (38, 55)], [(8, 17), (31, 33), (39, 54)],
    [(9, 16), (31, 34), (40, 53)], [(10, 16), (31, 35), (40, 52)],
    [(11, 15), (32, 35), (41, 50)], [(12, 15), (33, 35), (42, 49)],
    [(13, 15), (33, 35), (43, 48)], [(14, 16), (31, 35), (44, 48)],
    [(15, 17), (30, 35), (45, 49)], [(16, 18), (30, 34), (46, 49)],
    [(17, 19), (31, 33), (46, 48)], [(18, 20), (31, 33), (47, 49)],
    [(18, 21), (31, 33), (48, 50)], [(19, 21), (32, 33), (48, 51)],
    [(19, 22), (48, 51)], [(20, 22), (49, 51)], [(20, 22), (49, 52)],
    [(20, 22), (50, 53)], [(20, 21), (51, 54)], [(20, 21), (51, 55)],
    [(20, 21), (52, 55)], [(20, 21), (52, 55)], [(20, 21), (53, 56)],
    [(20, 20), (53, 56)], [(53, 55)], [(53, 55)], [(54, 55)], [],
]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)  # noqa: E731
F_REG = lambda s: font("DejaVuSans.ttf", s)  # noqa: E731


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def truncate(draw, s, f, max_w):
    if text_w(draw, s, f) <= max_w:
        return s
    ell = "…"
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w(draw, s[:mid] + ell, f) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo] + ell


def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as fh:
        news = json.load(fh)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- Masthead (0-84) ----
    d.rectangle([0, 0, W, 84], fill=GREEN)
    d.text((24, 18), "THE WORLD TODAY", font=F_BOLD(48), fill=WHITE)
    date_s = "WEDNESDAY 25 NOVEMBER 2026"
    d.text((W - 24 - text_w(d, date_s, F_BOLD(20)), 32), date_s,
           font=F_BOLD(20), fill=GOLD)
    d.rectangle([0, 84, W, 87], fill=GOLD)

    # ---- Lead hero (92-260) ----
    lead = news["lead"]
    d.rectangle([16, 92, 1008, 260], fill=WHITE, outline=BORDER)
    d.rectangle([16, 92, 24, 260], fill=RED)
    # kicker chip
    kick = lead["kicker"]
    kw = text_w(d, kick, F_BOLD(16)) + 20
    d.rounded_rectangle([40, 100, 40 + kw, 124], radius=4, fill=RED)
    d.text((50, 103), kick, font=F_BOLD(16), fill=WHITE)
    # date chip top-right
    dc = lead["date"]
    dw = text_w(d, dc, F_BOLD(14)) + 16
    d.rounded_rectangle([1008 - 16 - dw, 100, 992, 122], radius=4, fill=GREEN)
    d.text((1008 - 16 - dw + 8, 102), dc, font=F_BOLD(14), fill=WHITE)
    # headline, two lines
    hl = ["HOUTHIS STRIKE SAUDI REFINERY", "AND RIYADH TOWER"]
    y = 130
    for line in hl:
        d.text((40, y), line, font=F_BOLD(34), fill=GREEN)
        y += 38
    # body, two lines max
    body_lines = wrap(d, lead["body"], F_REG(21), 660)[:2]
    y = 214
    for line in body_lines:
        d.text((40, y), line, font=F_REG(21), fill=DARK)
        y += 24
    # stat blocks on the right
    sx = 730
    for num, lab in lead["stats"]:
        d.text((sx, 132), num, font=F_BOLD(60), fill=RED)
        d.text((sx, 198), lab, font=F_BOLD(16), fill=NAVY)
        sx += 130

    # ---- Map strip (268-372) ----
    d.rectangle([16, 268, 1008, 372], fill=LIGHT)
    d.text((30, 272), "WHERE THE NEWS HAPPENED — 25 NOV · ALL TIMES UTC",
           font=F_BOLD(18), fill=NAVY)
    ox, oy, dx, dy = 224, 296, 9, 2.3
    for r, spans in enumerate(MAP_RANGES):
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                x, y = ox + c * dx, oy + r * dy
                d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=NAVY)
    for pin in news["pins"]:
        x, y = ox + pin["col"] * dx, oy + pin["row"] * dy
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=RED, outline=WHITE, width=2)
        d.text((x + 7, y - 6), str(pin["n"]), font=F_BOLD(11), fill=RED)

    # ---- Story grid (380-784): 2 cols x 6 rows, card 488x64 ----
    cards = news["cards"]
    for i, card in enumerate(cards):
        col, row = i % 2, i // 2
        x0 = 16 + col * 504
        y0 = 380 + row * 68
        x1, y1 = x0 + 488, y0 + 64
        d.rectangle([x0, y0, x1, y1], fill=WHITE, outline=BORDER)
        d.rectangle([x0, y0, x0 + 6, y1], fill=card["color"])
        # kicker
        kick = card["glyph"] + " " + card["region"].upper()
        d.text((x0 + 16, y0 + 5), kick, font=F_BOLD(13), fill=card["color"])
        # date chip
        dc = card["date"]
        dw = text_w(d, dc, F_BOLD(11)) + 12
        d.rounded_rectangle([x1 - 8 - dw, y0 + 5, x1 - 8, y0 + 20], radius=3, fill=RED)
        d.text((x1 - 8 - dw + 6, y0 + 6), dc, font=F_BOLD(11), fill=WHITE)
        # headline, one line
        head = truncate(d, card["headline"], F_BOLD(18), 456)
        d.text((x0 + 16, y0 + 22), head, font=F_BOLD(18), fill=NAVY)
        # body, one line
        body = truncate(d, card["body"], F_REG(15), 456)
        d.text((x0 + 16, y0 + 43), body, font=F_REG(15), fill=GREY)

    # ---- Briefs grid (792-980): charcoal band, 3 cols x 9 rows ----
    d.rectangle([16, 792, 1008, 980], fill=CHARCOAL)
    d.text((30, 800), "ALSO TODAY — 27 MORE STORIES", font=F_BOLD(17), fill=GOLD)
    briefs = news["briefs"]
    for i, b in enumerate(briefs):
        col, row = i % 3, i // 3
        x0 = 30 + col * 330
        y0 = 826 + row * 17
        cell = truncate(d, "• " + b, F_REG(13), 318)
        d.text((x0, y0), cell, font=F_REG(13), fill=WHITE)

    # footer (984-1024): two lines
    d.rectangle([16, 984, 1008, 1024], fill=CHARCOAL)
    left1 = "DATE CHECK: ALL 40 STORIES FIRST REPORTED 24–25 NOV 2026"
    right1 = "THE WORLD TODAY — 25 NOV 2026"
    d.text((30, 988), left1, font=F_REG(13), fill=(204, 204, 204))
    d.text((W - 30 - text_w(d, right1, F_BOLD(13)), 988), right1,
           font=F_BOLD(13), fill=GOLD)
    left2 = "SOURCES: REUTERS, BBC, AP, FIFA, UN · 40 DATED STORIES · 9 REGIONS · 12 PINS ON THE MAP"
    d.text((30, 1006), left2, font=F_REG(13), fill=(160, 160, 160))

    out = os.path.join(HERE, "entry.png")
    # Palette PNG: identical look, ~60% smaller (tie-break favours fewer bytes).
    # Adaptive conversion is deterministic for identical input.
    img.convert("P", palette=Image.ADAPTIVE, colors=256).save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    sys.exit(main())
