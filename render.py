#!/usr/bin/env python3
"""Draw the news-image-20261119 front page (26 stories, 19 November 2026).

A single newspaper front page: three lead stories on top, nine more
illustrated stories in two rows below, a world map with numbered pins,
and fourteen further stories as a numbered list. Every story happened
or was first reported on Thursday 19 November 2026; scheduled items
are worded as due, contested claims are marked as claims, and the
footer names the two items left out because they happened earlier.

Runs on system python3 + PIL. Deterministic: no timestamps, no
network, no randomness. Writes entry.png next to this file.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = Path(__file__).resolve().parent
PANELS = BASE / "assets"

PAGE = 1024
EDGE = 14
INNER = PAGE - 2 * EDGE  # 996

# Warm newsprint paper, slate ink, restrained section accents.
PAPER = (247, 241, 227)
INK = (32, 34, 38)
SLATE = (36, 50, 66)
RED = (178, 44, 32)
BLUE = (58, 106, 143)
SKY_LIGHT = (216, 232, 238)
SAND = (233, 220, 192)
LAND_LINE = (190, 175, 140)
GREEN = (74, 128, 84)
OCHRE = (216, 162, 74)
PURPLE = (128, 74, 140)
TEAL = (46, 130, 126)
GREY = (120, 122, 118)
WHITE = (252, 250, 244)

SECTION = {
    "Europe": BLUE,
    "Middle East": OCHRE,
    "Asia": PURPLE,
    "Africa": GREEN,
    "Americas": TEAL,
    "World": GREY,
}

FONTS = "/usr/share/fonts/truetype/liberation"
SERIF_BOLD = f"{FONTS}/LiberationSerif-Bold.ttf"
SERIF_PLAIN = f"{FONTS}/LiberationSerif-Regular.ttf"
SANS_BOLD = f"{FONTS}/LiberationSans-Bold.ttf"
SANS_PLAIN = f"{FONTS}/LiberationSans-Regular.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font_obj, width):
    """Greedy word wrap by measured width; returns the lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font_obj) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, x, y, text, font_obj, fill, width, leading, limit=None):
    lines = wrap_text(draw, text, font_obj, width)
    if limit is not None:
        lines = lines[:limit]
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += leading
    return y


def cropped(path, w, h):
    """Centre-crop an illustration to the panel box."""
    pic = Image.open(path).convert("RGB")
    return ImageOps.fit(pic, (w, h), Image.LANCZOS)


def place_caption(draw, x, y, w, text, height=20, size=11):
    """Dark bar across the foot of an illustration, naming the place."""
    draw.rectangle([x, y, x + w, y + height], fill=SLATE)
    draw.text((x + 6, y + 3), text, font=load(SANS_BOLD, size), fill=WHITE)


# (number, region, kicker, headline, deck, caption, panel file)
LEADS = [
    (1, "Americas", "1 \u00b7 CULTURE \u00b7 VIDEO GAMES",
     "GTA VI rolls out around the world",
     "Rockstar's game unlocks at midnight local time, starting in New "
     "Zealand; after 13 years, Metacritic 99.",
     "NEW ZEALAND \u2014 THE ROLLOUT BEGINS", "panel-01.png"),
    (2, "Asia", "2 \u00b7 ASIA \u00b7 DIPLOMACY",
     "Trump, Xi, Putin due to meet in Shenzhen today",
     "First trilateral of the three sitting presidents, on the APEC "
     "sidelines in Shenzhen; no outcome yet.",
     "SHENZHEN \u2014 DUE TODAY", "panel-02.png"),
    (3, "Middle East", "3 \u00b7 MIDDLE EAST \u00b7 IRAN WAR",
     "Iran fires on US bases in Kuwait and Bahrain",
     "Tehran says it hit US drone and missile sites; Bahrain and Kuwait "
     "say the attacks were intercepted.",
     "GULF \u2014 INTERCEPTORS UP", "panel-03.png"),
]

MEDIUM_TOP = [
    (4, "Europe", "4 \u00b7 EUROPE \u00b7 UKRAINE",
     "EU proposes \u20ac45bn loan for Ukraine",
     "\u20ac20bn budget aid, \u20ac25bn military; repaid only once Russia pays "
     "reparations.",
     "BRUSSELS \u2014 \u20ac45BN PLAN", "panel-04.png"),
    (5, "Americas", "5 \u00b7 US \u00b7 BUSINESS",
     "Nvidia rules out Huang return; sales double",
     "Board will not reinstate the founder, who quit amid security "
     "concerns.",
     "SANTA CLARA \u2014 $115.8BN QUARTER", "panel-05.png"),
    (6, "Americas", "6 \u00b7 US \u00b7 POLITICS",
     "Democrats nominate Jeffries for Speaker, 251\u201311",
     "He would be the first Black Speaker if the full House elects him "
     "on 3 Jan.",
     "WASHINGTON \u2014 251\u201311", "panel-06.png"),
    (7, "World", "7 \u00b7 WORLD \u00b7 RELIGION",
     "Pew: Islam to pass Christianity by 2035",
     "Pew projects 2.57bn Muslims vs 2.52bn Christians by 2035; both "
     "still growing.",
     "WORLD \u2014 2.57BN BY 2035", "panel-07.png"),
    (8, "Americas", "8 \u00b7 SPACE \u00b7 SCIENCE",
     "Voyager 1 reaches one light-day from Earth",
     "NASA says the probe crossed about 16.1bn miles on 18 Nov; "
     "briefing today.",
     "DEEP SPACE \u2014 16.1BN MILES", "panel-08.png"),
]

MEDIUM_BOTTOM = [
    (9, "Asia", "9 \u00b7 ASIA \u00b7 WEATHER",
     "Cyclone Akvan bears down on India's east coast",
     "Very severe storm forecast to cross Andhra Pradesh on Friday; "
     "winds 120\u2013130 km/h.",
     "BAY OF BENGAL \u2014 LANDFALL FRIDAY", "panel-09.png"),
    (10, "Middle East", "10 \u00b7 MIDDLE EAST \u00b7 GAZA",
     "Gaza's winter shelters fail in the rain",
     "UN says tens of thousands of shelters were damaged by the first "
     "winter rains.",
     "GAZA \u2014 46,000 HOMES FLOODED", "panel-10.png"),
    (11, "Middle East", "11 \u00b7 MIDDLE EAST \u00b7 YEMEN",
     "Houthis close on Aden as army pulls back",
     "Sources say fighters are about 60 km from the city after "
     "government forces left.",
     "BAB EL-MANDEB \u2014 60 KM FROM ADEN", "panel-11.png"),
    (12, "Americas", "12 \u00b7 US \u00b7 ECONOMY",
     "Fed minutes point to more rate rises",
     "Most officials expect further hikes if inflation and jobs stay "
     "hot, minutes show.",
     "WASHINGTON \u2014 RATES STILL RISING", "panel-12.png"),
]

ALSO = [
    (13, "Zelensky urges the US to lift Starshield limits, saying they hinder drone defence."),
    (14, "Scotland beat Denmark 4\u20132 to reach a first World Cup in 28 years."),
    (15, "Canada adjusts China ties; Carney seeks the right deal with the US."),
    (16, "US senators warn AI cyber threats are outpacing defences."),
    (17, "France: justice minister says M\u00e9lenchon could win the presidency."),
    (18, "Saudi Arabia says the danger has passed in three southern cities."),
    (19, "Libya seizes cocaine and millions of pills in the east, officials say."),
    (20, "Amazon pledges $7bn for renewables in India by 2030."),
    (21, "India and Japan to review defence ties in 2+2 talks."),
    (22, "Modi meets the Prince and Princess of Wales, talks UK\u2013India ties."),
    (23, "Kyiv: Russia hit the capital's Dnipro bridges; Ukraine claims a new Crimea bridge strike."),
    (24, "Tankers hit in the Strait of Hormuz, reports say; Iran claims mine strikes."),
    (25, "Board of Peace warns the Gaza truce could collapse without steps."),
    (26, "Somalia accuses the UAE of secretly building bases on its soil."),
]

KEY_NUMBERS = [
    ("16m", "GTA VI copies pre-sold"),
    ("\u20ac45bn", "EU loan for Ukraine, 2027"),
    ("251\u201311", "Jeffries nomination vote"),
    ("$115.8bn", "Nvidia quarterly sales"),
    ("16.1bn", "Voyager 1 miles from Earth"),
    ("120\u2013130", "Akvan landfall winds km/h"),
]

# Lon/lat of the 12 illustrated stories, for the map pins.
PIN_POS = {
    1: (-80, 26), 2: (114, 22), 3: (51, 27), 4: (4, 51),
    5: (-122, 37), 6: (-77, 39), 7: (31, 30), 8: (-118, 34),
    9: (88, 16), 10: (34, 32), 11: (44, 11), 12: (-79, 36),
}
DOT_POS = {
    13: (30, 50), 14: (-4, 56), 15: (-75, 45), 16: (-77, 39),
    17: (2, 49), 18: (47, 25), 19: (20, 32), 20: (77, 29),
    21: (140, 36), 22: (0, 51),
    23: (30, 50), 24: (56, 27), 25: (34, 31), 26: (45, 2),
}
PIN_REGION = {
    1: "Americas", 2: "Asia", 3: "Middle East", 4: "Europe",
    5: "Americas", 6: "Americas", 7: "World", 8: "Americas",
    9: "Asia", 10: "Middle East", 11: "Middle East", 12: "Americas",
}

# Schematic continent outlines in lon/lat.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-58, 64), (-45, 60), (-40, 70), (-55, 76), (-65, 75)],
    [(-80, 10), (-72, 12), (-62, 10), (-52, 5), (-50, -5), (-40, -10),
     (-35, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -55),
     (-73, -40), (-72, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (-5, 58), (-10, 52)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (43, 11), (48, 11), (51, 12), (44, 0), (40, -10), (35, -20),
     (32, -29), (26, -34), (20, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-13, 8)],
    [(30, 36), (35, 36), (42, 41), (50, 40), (55, 45), (60, 50), (70, 55),
     (80, 60), (90, 65), (100, 70), (110, 73), (130, 72), (160, 70),
     (178, 66), (170, 60), (160, 55), (155, 50), (142, 45), (140, 38),
     (130, 33), (127, 35), (122, 30), (120, 23), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 15), (75, 8), (70, 25),
     (65, 25), (60, 25), (55, 26), (50, 29), (45, 30), (40, 35)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (136, -12), (132, -11), (126, -14),
     (122, -17), (118, -20)],
]


def build():
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)

    # --- masthead ---
    draw.text((EDGE, 10), "THE WORLD'S NEWS IN ONE PICTURE",
              font=load(SANS_BOLD, 13), fill=RED)
    right = "26 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM THURSDAY"
    rw = draw.textlength(right, font=load(SANS_BOLD, 13))
    draw.text((PAGE - EDGE - rw, 10), right, font=load(SANS_BOLD, 13), fill=INK)
    draw.text((EDGE, 30), "Thursday 19 November 2026",
              font=load(SERIF_BOLD, 46), fill=INK)
    draw.line([(EDGE, 88), (PAGE - EDGE, 88)], fill=INK, width=3)
    draw.line([(EDGE, 92), (PAGE - EDGE, 92)], fill=INK, width=1)

    # --- key numbers strip ---
    cell = INNER // 6
    y = 96
    for i, (num, label) in enumerate(KEY_NUMBERS):
        x = EDGE + i * cell
        draw.text((x, y), num, font=load(SERIF_BOLD, 19), fill=INK)
        text_block(draw, x, y + 23, label, load(SANS_PLAIN, 9), GREY,
                   cell - 10, 11, limit=1)
    draw.line([(EDGE, 130), (PAGE - EDGE, 130)], fill=INK, width=1)

    # --- region strip ---
    strip = ("EUROPE 5  \u00b7  MIDDLE EAST 6  \u00b7  ASIA 5  \u00b7  "
             "AFRICA 2  \u00b7  AMERICAS 7  \u00b7  WORLD 1")
    sw = draw.textlength(strip, font=load(SANS_BOLD, 12))
    draw.text(((PAGE - sw) / 2, 134), strip, font=load(SANS_BOLD, 12), fill=INK)

    # --- leads: three equal columns ---
    hy, hw, gap = 150, 324, 12
    pic_h = 126
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(LEADS):
        x = EDGE + i * (hw + gap)
        pic = cropped(PANELS / fname, hw, pic_h)
        page.paste(pic, (x, hy))
        place_caption(draw, x, hy + pic_h - 20, hw, caption, height=20, size=11)
        ty = hy + pic_h + 6
        draw.text((x, ty), kicker, font=load(SANS_BOLD, 11),
                  fill=SECTION[region])
        text_block(draw, x, ty + 16, headline, load(SERIF_BOLD, 18), INK,
                   hw, 21, limit=2)
        text_block(draw, x, ty + 60, deck, load(SANS_PLAIN, 12), INK,
                   hw, 14, limit=2)

    # --- mediums, top row: five columns ---
    my1, mw1, gap1 = 372, 191, 10
    pic_h1 = 88
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUM_TOP):
        x = EDGE + i * (mw1 + gap1)
        pic = cropped(PANELS / fname, mw1, pic_h1)
        page.paste(pic, (x, my1))
        place_caption(draw, x, my1 + pic_h1 - 17, mw1, caption,
                      height=17, size=9)
        ty = my1 + pic_h1 + 5
        draw.text((x, ty), kicker, font=load(SANS_BOLD, 9),
                  fill=SECTION[region])
        text_block(draw, x, ty + 14, headline, load(SERIF_BOLD, 13), INK,
                   mw1, 15, limit=2)
        text_block(draw, x, ty + 45, deck, load(SANS_PLAIN, 10), INK,
                   mw1, 12, limit=2)

    # --- mediums, bottom row: four wider columns ---
    my2, mw2, gap2 = 542, 241, 11
    pic_h2 = 96
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUM_BOTTOM):
        x = EDGE + i * (mw2 + gap2)
        pic = cropped(PANELS / fname, mw2, pic_h2)
        page.paste(pic, (x, my2))
        place_caption(draw, x, my2 + pic_h2 - 17, mw2, caption,
                      height=17, size=9)
        ty = my2 + pic_h2 + 5
        draw.text((x, ty), kicker, font=load(SANS_BOLD, 10),
                  fill=SECTION[region])
        text_block(draw, x, ty + 15, headline, load(SERIF_BOLD, 14), INK,
                   mw2, 16, limit=2)
        text_block(draw, x, ty + 48, deck, load(SANS_PLAIN, 10), INK,
                   mw2, 12, limit=2)

    # --- also-on header ---
    ay = 722
    draw.text((EDGE, ay), "ALSO ON THURSDAY 19 NOVEMBER",
              font=load(SANS_BOLD, 12), fill=RED)
    draw.line([(EDGE, ay + 18), (PAGE - EDGE, ay + 18)], fill=INK, width=1)

    # --- world map ---
    mx, my, mw, mh = EDGE, ay + 26, 330, 210
    draw.rectangle([mx, my, mx + mw, my + mh], fill=SKY_LIGHT,
                   outline=LAND_LINE)

    def project(lon, lat):
        px = mx + (lon + 180) / 360 * mw
        py = my + (75 - lat) / 130 * mh
        return (px, py)

    for poly in LAND:
        draw.polygon([project(lon, lat) for lon, lat in poly],
                     fill=SAND, outline=LAND_LINE)
    for num, (lon, lat) in DOT_POS.items():
        px, py = project(lon, lat)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GREY)
    for num, (lon, lat) in PIN_POS.items():
        px, py = project(lon, lat)
        col = SECTION[PIN_REGION[num]]
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col,
                     outline=WHITE, width=2)
        label = str(num)
        tw = draw.textlength(label, font=load(SANS_BOLD, 10))
        draw.text((px - tw / 2, py - 7), label, font=load(SANS_BOLD, 10),
                  fill=WHITE)
    draw.text((mx, my + mh + 4),
              "Pins: stories 1\u201312 \u2014 dots: 13\u201326. Pins approximate.",
              font=load(SANS_PLAIN, 9), fill=GREY)

    # --- also-on list, two columns ---
    lx = EDGE + mw + 14
    col_w = (PAGE - EDGE - lx - 10) // 2
    num_font = load(SANS_BOLD, 11)
    txt_font = load(SANS_PLAIN, 11)
    for col in range(2):
        x = lx + col * (col_w + 10)
        y = my
        for num, text in ALSO[col * 7:(col + 1) * 7]:
            draw.text((x, y), f"{num}", font=num_font, fill=RED)
            lines = wrap_text(draw, text, txt_font, col_w - 24)
            ly = y
            for line in lines[:2]:
                draw.text((x + 24, ly), line, font=txt_font, fill=INK)
                ly += 13
            y = ly + 5

    # --- footer ---
    fy = 976
    draw.text((EDGE, fy),
              "DATE CHECK \u2014 Left out as earlier news: Estonia's border closure, announced 16 Nov; "
              "the NSA network outage, first reported 17 Nov.",
              font=load(SANS_BOLD, 9), fill=INK)
    draw.text((EDGE, fy + 13),
              "Every story here happened or was first reported on Thursday 19 November 2026. "
              "Contested claims are marked as claims. Sources: Reuters, AP, AFP, BBC, Pew, NASA, IMD. Original drawings.",
              font=load(SANS_PLAIN, 9), fill=GREY)

    out = BASE / "entry.png"
    page.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size} bytes)")
