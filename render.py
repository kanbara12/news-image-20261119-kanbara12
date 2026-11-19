#!/usr/bin/env python3
"""Render the news-image-20261119 front page, rebuilt from scratch.

One newspaper front page for Thursday 19 November 2026: 21 stories
from six continents. One dominant lead (GTA VI), two secondary leads,
nine more illustrated stories, a world map with numbered pins, and
nine more as a numbered list.

Design rules for this rebuild (from a second-opinion review of the
first version):
- fewer stories (21, not 26) so every headline and brief stays
  legible at thumbnail size; the also-on type is larger (12pt);
- one dominant hero, not three equals: the GTA lead is the widest
  column with the tallest picture, the other two leads are narrower;
- every claim attributed ("says", "reportedly", "sources say");
  scheduled items worded as due, never as done; no unverified
  numbers (no 251-11 vote count, no Metacritic 99, no Pew 2035
  projection); the footer names what was deliberately left out as
  earlier news;
- bright daytime newsprint palette only; no dark muddy panels;
- one clear subject per illustration; each panel carries a caption
  bar at its foot naming the place; no text inside the illustrations
  themselves;
- map pins are nudged a few degrees where the true locations would
  collide at thumbnail size (pins are approximate, as the map note
  says).

Runs with system python3 + PIL. Deterministic: no timestamps, no
network, no randomness. Writes entry.png next to this file.
"""

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
SKY_LIGHT = (216, 232, 238)
SAND = (233, 220, 192)
LAND_LINE = (190, 175, 140)
GREEN = (74, 128, 84)
OCHRE = (216, 162, 74)
PURPLE = (128, 74, 140)
TEAL = (46, 130, 126)
GREY = (120, 122, 118)
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


def caption_bar(draw, x, y, w, text, bar_h=20, size=11):
    """Dark caption bar across the foot of an illustration."""
    draw.rectangle([x, y, x + w, y + bar_h], fill=SLATE)
    fnt = font(SANS_B, size)
    draw.text((x + 6, y + 3), text, font=fnt, fill=WHITE)


# --- stories: (number, region, kicker, headline, deck, caption, panel) ---
HEROES = [
    (1, "Americas", "1 \u00b7 CULTURE \u00b7 VIDEO GAMES",
     "GTA VI rolls out around the world",
     "Rockstar's game unlocks at midnight local time, starting in New "
     "Zealand; after 13 years, to near-perfect review scores.",
     "NEW ZEALAND \u2014 THE ROLLOUT BEGINS", "panel-01.png"),
    (2, "Asia", "2 \u00b7 ASIA \u00b7 DIPLOMACY",
     "Trump, Xi, Putin due in Shenzhen today",
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
     "Democrats nominate Jeffries for Speaker",
     "He would be the first Black Speaker if the full House elects him "
     "on 3 Jan.",
     "WASHINGTON \u2014 SPEAKER NOMINEE", "panel-06.png"),
    (7, "Europe", "7 \u00b7 EUROPE \u00b7 SPORT",
     "Scotland reach first World Cup in 28 years",
     "Scotland beat Denmark 4\u20132 to reach a first World Cup in 28 years.",
     "GLASGOW \u2014 4\u20132, WORLD CUP BOUND", "panel-07.png"),
    (8, "World", "8 \u00b7 SPACE \u00b7 SCIENCE",
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
     "Houthis reported near Aden as army pulls back",
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
    (14, "Canada adjusts China ties; Carney seeks the right deal with the US."),
    (15, "US senators warn AI cyber threats are outpacing defences."),
    (16, "Saudi Arabia says the danger has passed in three southern cities."),
    (17, "Libya seizes cocaine and millions of pills in the east, officials say."),
    (18, "Amazon pledges $7bn for renewables in India by 2030."),
    (19, "India and Japan to review defence ties in 2+2 talks."),
    (20, "Modi meets the Prince and Princess of Wales, talks UK\u2013India ties."),
    (21, "Board of Peace warns the Gaza truce could collapse without steps."),
]

DATA_STRIP = [
    ("16m", "GTA VI copies pre-sold"),
    ("\u20ac45bn", "EU loan for Ukraine, 2027"),
    ("4\u20132", "Scotland reach World Cup"),
    ("$115.8bn", "Nvidia quarterly sales"),
    ("16.1bn", "Voyager 1 miles from Earth"),
    ("120\u2013130", "Akvan landfall winds km/h"),
]

# lon/lat of the 12 illustrated stories, for the map pins.
# Three pins are nudged a few degrees so they do not collide at
# thumbnail size (pins are approximate, as the map note says):
# 7 west of Scotland so it clears pin 4 (Brussels),
# 8 east so it clears pin 5 (Santa Clara),
# 12 south-east so it clears pin 6 (Washington).
PINS = {
    1: (174, -41), 2: (114, 22), 3: (51, 27), 4: (4, 51),
    5: (-122, 37), 6: (-77, 39), 7: (-12, 58), 8: (-104, 31),
    9: (88, 16), 10: (34, 32), 11: (44, 11), 12: (-88, 30),
}
PIN_REGIONS = {
    1: "Americas", 2: "Asia", 3: "Middle East", 4: "Europe",
    5: "Americas", 6: "Americas", 7: "Europe", 8: "World",
    9: "Asia", 10: "Middle East", 11: "Middle East", 12: "Americas",
}
DOTS = {
    13: (30, 50), 14: (-75, 45), 15: (-77, 39), 16: (47, 25),
    17: (20, 32), 18: (77, 29), 19: (140, 36), 20: (0, 51),
    21: (34, 31),
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
    right = "21 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM THURSDAY"
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
    strip = ("EUROPE 4  \u00b7  MIDDLE EAST 5  \u00b7  ASIA 4  \u00b7  "
             "AFRICA 1  \u00b7  AMERICAS 6  \u00b7  WORLD 1")
    sw = draw.textlength(strip, font=font(SANS_B, 12))
    draw.text(((W - sw) / 2, 134), strip, font=font(SANS_B, 12), fill=INK)

    # --- heroes: dominant lead (GTA) + two narrower secondaries ---
    hy = 152
    # lead: wide column, tall picture
    lx, lw, img_h = MARGIN, 448, 140
    num, region, kicker, headline, deck, caption, fname = HEROES[0]
    pic = panel_image(ASSETS / fname, lw, img_h)
    img.paste(pic, (lx, hy))
    caption_bar(draw, lx, hy + img_h - 20, lw, caption, bar_h=20, size=11)
    ty = hy + img_h + 6
    draw.text((lx, ty), kicker, font=font(SANS_B, 11),
              fill=REGION_COLORS[region])
    ty = draw_text_block(draw, lx, ty + 16, headline, font(SERIF_B, 20),
                         INK, lw, 22, max_lines=2)
    draw_text_block(draw, lx, ty + 4, deck, font(SANS, 12), INK,
                    lw, 15, max_lines=2)
    # secondaries: narrower columns, shorter pictures
    sw_, sh = 262, 110
    for i in (1, 2):
        num, region, kicker, headline, deck, caption, fname = HEROES[i]
        x = MARGIN + lw + 12 + (i - 1) * (sw_ + 12)
        pic = panel_image(ASSETS / fname, sw_, sh)
        img.paste(pic, (x, hy))
        caption_bar(draw, x, hy + sh - 17, sw_, caption, bar_h=17, size=9)
        ty = hy + sh + 5
        draw.text((x, ty), kicker, font=font(SANS_B, 10),
                  fill=REGION_COLORS[region])
        ty = draw_text_block(draw, x, ty + 15, headline, font(SERIF_B, 16),
                             INK, sw_, 19, max_lines=2)
        draw_text_block(draw, x, ty + 4, deck, font(SANS, 11), INK,
                        sw_, 14, max_lines=2)

    # --- mediums row 1: 5 columns ---
    my1, mw1, gap1 = 400, 191, 10
    img_h1 = 88
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUMS_ROW1):
        x = MARGIN + i * (mw1 + gap1)
        pic = panel_image(ASSETS / fname, mw1, img_h1)
        img.paste(pic, (x, my1))
        caption_bar(draw, x, my1 + img_h1 - 17, mw1, caption,
                    bar_h=17, size=9)
        ty = my1 + img_h1 + 5
        draw.text((x, ty), kicker, font=font(SANS_B, 9),
                  fill=REGION_COLORS[region])
        ty = draw_text_block(draw, x, ty + 14, headline, font(SERIF_B, 13),
                             INK, mw1, 15, max_lines=2)
        draw_text_block(draw, x, ty + 4, deck, font(SANS, 10), INK,
                        mw1, 12, max_lines=2)

    # --- mediums row 2: 4 wider columns ---
    my2, mw2, gap2 = 575, 240, 12
    img_h2 = 96
    for i, (num, region, kicker, headline, deck, caption, fname) in enumerate(MEDIUMS_ROW2):
        x = MARGIN + i * (mw2 + gap2)
        pic = panel_image(ASSETS / fname, mw2, img_h2)
        img.paste(pic, (x, my2))
        caption_bar(draw, x, my2 + img_h2 - 17, mw2, caption,
                    bar_h=17, size=9)
        ty = my2 + img_h2 + 5
        draw.text((x, ty), kicker, font=font(SANS_B, 10),
                  fill=REGION_COLORS[region])
        ty = draw_text_block(draw, x, ty + 15, headline, font(SERIF_B, 14),
                             INK, mw2, 16, max_lines=2)
        draw_text_block(draw, x, ty + 4, deck, font(SANS, 10), INK,
                        mw2, 12, max_lines=2)

    # --- also-on header ---
    ay = 758
    draw.text((MARGIN, ay), "ALSO ON THURSDAY 19 NOVEMBER",
              font=font(SANS_B, 12), fill=RED)
    draw.line([(MARGIN, ay + 18), (W - MARGIN, ay + 18)], fill=INK, width=1)

    # --- world map ---
    mx, my, mw, mh = MARGIN, 784, 330, 162
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
        col = REGION_COLORS[PIN_REGIONS[num]]
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                     outline=WHITE, width=2)
        label = str(num)
        tw = draw.textlength(label, font=font(SANS_B, 9))
        draw.text((px - tw / 2, py - 6), label, font=font(SANS_B, 9),
                  fill=WHITE)
    draw.text((mx, my + mh + 4), "Pins: stories 1\u201312 \u2014 dots: 13\u201321. Pins approximate.",
              font=font(SANS, 9), fill=GREY)

    # --- also-on list, two columns, 12pt type ---
    lx = MARGIN + mw + 14
    col_w = (W - MARGIN - lx - 10) // 2
    f_num = font(SANS_B, 12)
    f_txt = font(SANS, 12)
    for col in range(2):
        x = lx + col * (col_w + 10)
        y = my
        for num, text in ALSO_ON[col * 5:(col + 1) * 5]:
            draw.text((x, y), f"{num}", font=f_num, fill=RED)
            lines = wrap(draw, text, f_txt, col_w - 24)
            ly = y
            for line in lines[:3]:
                draw.text((x + 24, ly), line, font=f_txt, fill=INK)
                ly += 15
            y = ly + 5

    # --- footer ---
    fy = 968
    draw.text((MARGIN, fy),
              "DATE CHECK \u2014 Left out as earlier news: Estonia's border closure, announced 16 Nov; "
              "the NSA network outage, first reported 17 Nov.",
              font=font(SANS_B, 9), fill=INK)
    draw.text((MARGIN, fy + 13),
              "Every story here happened or was first reported on Thursday 19 November 2026. "
              "Contested claims are marked as claims. Sources: Reuters, AP, AFP, BBC, NASA, IMD. Original drawings.",
              font=font(SANS, 9), fill=GREY)

    out = HERE / "entry.png"
    img.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    path = render()
    print(f"wrote {path} ({path.stat().st_size} bytes)")
