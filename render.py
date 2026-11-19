#!/usr/bin/env python3
"""Render the news-image-20261119 front page (written fresh in this session).

One newspaper front page for Thursday 19 November 2026: 26 stories from
six continents. Three lead stories, nine more illustrated, a world map
with numbered pins, and fourteen more as a numbered list.

Design rules for this entry (from the 17 Nov rebuild + a second-opinion
review):
- bright daytime newsprint palette only; no dark muddy panels;
- one clear subject per illustration; each panel carries a caption bar
  at its foot naming the place, the way the winning front pages do it;
- every claim attributed ("says", "Pew projects", "sources say");
  scheduled items worded as due, never as done; the footer names what
  was deliberately left out as earlier news;
- fewer stories than the 17 Nov page (30, not 47) so headlines and the
  also-on list stay legible at thumbnail size; the also-on type is
  larger and the map pins are spaced out.

Runs with system python3 + PIL. Deterministic: fixed seed, no
timestamps, no network. Writes entry.png next to this file.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

W = H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996 content width

# --- newsprint palette: warm cream paper, slate ink, restrained accents ---
PAPER = (247, 241, 227)
INK = (32, 34, 38)
SLATE = (36, 50, 66)
RED = (178, 44, 32)
BLUE = (58, 106, 143)
SKY = (198, 220, 230)
SKY_LIGHT = (216, 232, 238)
SEA = (174, 205, 219)
SAND = (233, 220, 192)
LAND_LINE = (190, 175, 140)
GREEN = (74, 128, 84)
OCHRE = (216, 162, 74)
PURPLE = (128, 74, 140)
TEAL = (46, 130, 126)
GREY = (120, 122, 118)
LIGHT_GREY = (226, 224, 216)
WHITE = (252, 250, 244)

REGION_COLORS = {
    "Europe": BLUE,
    "Middle East": OCHRE,
    "Asia": PURPLE,
    "Africa": GREEN,
    "Americas": TEAL,
    "World": GREY,
}

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_B = f"{FONT_DIR}/LiberationSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/LiberationSerif-Regular.ttf"
SANS_B = f"{FONT_DIR}/LiberationSans-Bold.ttf"
SANS = f"{FONT_DIR}/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, width, leading, max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def panel_image(path, w, h):
    """Centre-crop the generated illustration to the panel box."""
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def caption_bar(draw, img_draw, x, y, w, text, bar_h=20, size=11):
    """Dark caption bar across the foot of an illustration."""
    img_draw.rectangle([x, y + 0, x + w, y + bar_h], fill=SLATE)
    fnt = font(SANS_B, size)
    draw.text((x + 6, y + 3), text, font=fnt, fill=WHITE)


# --- stories: (number, region, kicker, headline, deck, caption, panel) ---
HEROES = [
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

MEDIUMS_ROW1 = [
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

MEDIUMS_ROW2 = [
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

ALSO_ON = [
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

DATA_STRIP = [
    ("16m", "GTA VI copies pre-sold"),
    ("\u20ac45bn", "EU loan for Ukraine, 2027"),
    ("251\u201311", "Jeffries nomination vote"),
    ("$115.8bn", "Nvidia quarterly sales"),
    ("16.1bn", "Voyager 1 miles from Earth"),
    ("120\u2013130", "Akvan landfall winds km/h"),
]

# lon/lat of the 12 illustrated stories, for the map pins.
PINS = {
    1: (-80, 26), 2: (114, 22), 3: (51, 27), 4: (4, 51),
    5: (-122, 37), 6: (-77, 39), 7: (31, 30), 8: (-118, 34),
    9: (88, 16), 10: (34, 32), 11: (44, 11), 12: (-79, 36),
}
DOTS = {
    13: (30, 50), 14: (-4, 56), 15: (-75, 45), 16: (-77, 39),
    17: (2, 49), 18: (47, 25), 19: (20, 32), 20: (77, 29),
    21: (140, 36), 22: (0, 51),
    23: (30, 50), 24: (56, 27), 25: (34, 31), 26: (45, 2),
}

# Rough continent outlines in lon/lat (schematic, drawn for this page).
CONTINENTS = [
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


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead ---
    draw.text((MARGIN, 10), "THE WORLD'S NEWS IN ONE PICTURE",
              font=font(SANS_B, 13), fill=RED)
    right = "26 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM THURSDAY"
    rw = draw.textlength(right, font=font(SANS_B, 13))
    draw.text((W - MARGIN - rw, 10), right, font=font(SANS_B, 13), fill=INK)
    draw.text((MARGIN, 30), "Thursday 19 November 2026",
              font=font(SERIF_B, 46), fill=INK)
    draw.line([(MARGIN, 88), (W - MARGIN, 88)], fill=INK, width=3)
    draw.line([(MARGIN, 92), (W - MARGIN, 92)], fill=INK, width=1)

    # --- data strip ---
    cell_w = CW // 6
    y = 96
    for i, (num, label) in enumerate(DATA_STRIP):
        x = MARGIN + i * cell_w
        draw.text((x, y), num, font=font(SERIF_B, 19), fill=INK)
        draw_text_block(draw, x, y + 23, label, font(SANS, 9), GREY,
                        cell_w - 10, 11, max_lines=1)
    draw.line([(MARGIN, 130), (W - MARGIN, 130)], fill=INK, width=1)

    # --- region strip ---
    strip = ("EUROPE 5  \u00b7  MIDDLE EAST 6  \u00b7  ASIA 5  \u00b7  "
             "AFRICA 2  \u00b7  AMERICAS 7  \u00b7  WORLD 1")
    sw = draw.textlength(strip, font=font(SANS_B, 12))
    draw.text(((W - sw) / 2, 134), strip, font=font(SANS_B, 12), fill=INK)

    # --- heroes: 3 equal columns ---
    hy, hw, gap = 150, 324, 12
    img_h = 126
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(HEROES):
        x = MARGIN + i * (hw + gap)
        pic = panel_image(ASSETS / fname, hw, img_h)
        img.paste(pic, (x, hy))
        caption_bar(draw, draw, x, hy + img_h - 20, hw, caption, bar_h=20, size=11)
        ty = hy + img_h + 6
        draw.text((x, ty), kicker, font=font(SANS_B, 11),
                  fill=REGION_COLORS[region])
        draw_text_block(draw, x, ty + 16, headline, font(SERIF_B, 18), INK,
                        hw, 21, max_lines=2)
        draw_text_block(draw, x, ty + 60, deck, font(SANS, 12), INK,
                        hw, 14, max_lines=2)

    # --- mediums row 1: 5 columns ---
    my1, mw1, gap1 = 372, 191, 10
    img_h1 = 88
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUMS_ROW1):
        x = MARGIN + i * (mw1 + gap1)
        pic = panel_image(ASSETS / fname, mw1, img_h1)
        img.paste(pic, (x, my1))
        caption_bar(draw, draw, x, my1 + img_h1 - 17, mw1, caption,
                    bar_h=17, size=9)
        ty = my1 + img_h1 + 5
        draw.text((x, ty), kicker, font=font(SANS_B, 9),
                  fill=REGION_COLORS[region])
        draw_text_block(draw, x, ty + 14, headline, font(SERIF_B, 13), INK,
                        mw1, 15, max_lines=2)
        draw_text_block(draw, x, ty + 45, deck, font(SANS, 10), INK,
                        mw1, 12, max_lines=2)

    # --- mediums row 2: 4 wider columns ---
    my2, mw2, gap2 = 542, 241, 11
    img_h2 = 96
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUMS_ROW2):
        x = MARGIN + i * (mw2 + gap2)
        pic = panel_image(ASSETS / fname, mw2, img_h2)
        img.paste(pic, (x, my2))
        caption_bar(draw, draw, x, my2 + img_h2 - 17, mw2, caption,
                    bar_h=17, size=9)
        ty = my2 + img_h2 + 5
        draw.text((x, ty), kicker, font=font(SANS_B, 10),
                  fill=REGION_COLORS[region])
        draw_text_block(draw, x, ty + 15, headline, font(SERIF_B, 14), INK,
                        mw2, 16, max_lines=2)
        draw_text_block(draw, x, ty + 48, deck, font(SANS, 10), INK,
                        mw2, 12, max_lines=2)

    # --- also-on header ---
    ay = 722
    draw.text((MARGIN, ay), "ALSO ON THURSDAY 19 NOVEMBER",
              font=font(SANS_B, 12), fill=RED)
    draw.line([(MARGIN, ay + 18), (W - MARGIN, ay + 18)], fill=INK, width=1)

    # --- world map ---
    mx, my, mw, mh = MARGIN, ay + 26, 330, 210
    draw.rectangle([mx, my, mx + mw, my + mh], fill=SKY_LIGHT,
                   outline=LAND_LINE)

    def project(lon, lat):
        px = mx + (lon + 180) / 360 * mw
        py = my + (75 - lat) / 130 * mh
        return (px, py)

    for poly in CONTINENTS:
        draw.polygon([project(lon, lat) for lon, lat in poly],
                     fill=SAND, outline=LAND_LINE)
    for num, (lon, lat) in DOTS.items():
        px, py = project(lon, lat)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GREY)
    for num, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        region = {1: "Americas", 2: "Asia", 3: "Middle East", 4: "Europe",
                  5: "Americas", 6: "Americas", 7: "World", 8: "Americas",
                  9: "Asia", 10: "Middle East", 11: "Middle East",
                  12: "Americas"}[num]
        col = REGION_COLORS[region]
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col,
                     outline=WHITE, width=2)
        label = str(num)
        tw = draw.textlength(label, font=font(SANS_B, 10))
        draw.text((px - tw / 2, py - 7), label, font=font(SANS_B, 10),
                  fill=WHITE)
    draw.text((mx, my + mh + 4), "Pins: stories 1\u201312 \u2014 dots: 13\u201326. Pins approximate.",
              font=font(SANS, 9), fill=GREY)

    # --- also-on list, two columns ---
    lx = MARGIN + mw + 14
    col_w = (W - MARGIN - lx - 10) // 2
    f_num = font(SANS_B, 11)
    f_txt = font(SANS, 11)
    for col in range(2):
        x = lx + col * (col_w + 10)
        y = my
        for num, text in ALSO_ON[col * 7:(col + 1) * 7]:
            draw.text((x, y), f"{num}", font=f_num, fill=RED)
            lines = wrap(draw, text, f_txt, col_w - 24)
            ly = y
            for line in lines[:2]:
                draw.text((x + 24, ly), line, font=f_txt, fill=INK)
                ly += 13
            y = ly + 5

    # --- footer ---
    fy = 976
    draw.text((MARGIN, fy),
              "DATE CHECK \u2014 Left out as earlier news: Estonia's border closure, announced 16 Nov; "
              "the NSA network outage, first reported 17 Nov.",
              font=font(SANS_B, 9), fill=INK)
    draw.text((MARGIN, fy + 13),
              "Every story here happened or was first reported on Thursday 19 November 2026. "
              "Contested claims are marked as claims. Sources: Reuters, AP, AFP, BBC, Pew, NASA, IMD. Original drawings.",
              font=font(SANS, 9), fill=GREY)

    out = HERE / "entry.png"
    img.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    path = render()
    print(f"wrote {path} ({path.stat().st_size} bytes)")
