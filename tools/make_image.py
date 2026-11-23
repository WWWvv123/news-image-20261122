#!/usr/bin/env python3
"""Draw a classic newspaper front page for 22 November 2026.

Every pixel of text on the poster is drawn here with PIL -- no pasted
images, no downloaded photos. Run: python3 tools/make_image.py
Writes entry.png (1024x1024) next to this script's parent directory.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.path.join(ROOT, "entry.png")

WIDTH = 1024
HEIGHT = 1024
MARGIN = 40
CONTENT = WIDTH - 2 * MARGIN

PAPER = (253, 251, 245)
INK = (17, 17, 17)
GREY = (90, 86, 78)
RULE = (30, 30, 30)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap using real measured widths."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, fnt, x, y, fill=INK, leading=None):
    """Draw lines left-aligned; return the y below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.25)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_centered(draw, text, fnt, y, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text(((WIDTH - w) / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.25)


def hrule(draw, y, thickness=2):
    draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + thickness - 1], fill=RULE)
    return y + thickness


def story_block(draw, x, width, y, kicker, headline, body,
                head_size, body_size, head_lines=3, body_lines=4):
    """One story: kicker, headline, body. Returns y below the block."""
    kick_font = font(SANS_BOLD, 15)
    head_font = font(SERIF_BOLD, head_size)
    body_font = font(SANS, body_size)
    y = draw_lines(draw, wrap(draw, kicker, kick_font, width),
                   kick_font, x, y, fill=GREY, leading=20)
    y += 4
    head = wrap(draw, headline, head_font, width)[:head_lines]
    y = draw_lines(draw, head, head_font, x, y,
                   leading=int(head_size * 1.18))
    y += 4
    body = wrap(draw, body, body_font, width)[:body_lines]
    y = draw_lines(draw, body, body_font, x, y,
                   leading=int(body_size * 1.3))
    return y


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)

    # --- Masthead -------------------------------------------------------
    y = 26
    y = hrule(draw, y, 3)
    y += 10
    mast_font = font(SERIF_BOLD, 74)
    name = "THE WORLD HERALD"
    w = draw.textlength(name, font=mast_font)
    draw.text(((WIDTH - w) / 2, y), name, font=mast_font, fill=INK)
    y += 92
    y = draw_centered(draw, "Sunday, 22 November 2026",
                      font(SERIF_BOLD, 24), y)
    y = draw_centered(
        draw, "WORLD NEWS IN ONE PAGE  \u2022  SIX STORIES FROM AROUND THE GLOBE",
        font(SANS, 15), y, fill=GREY)
    y += 6
    y = hrule(draw, y, 3)
    y = hrule(draw, y + 4, 1)
    y += 12

    # --- Lead story (full width) ----------------------------------------
    y = story_block(
        draw, MARGIN, CONTENT, y,
        "CLIMATE  \u2022  ANTALYA, TURKEY",
        "Climate talks collapse with no deal at all",
        "The COP31 summit in Antalya, Turkey, ended on Sunday without "
        "a political agreement, after the EU and others rejected a final "
        "draft that made no mention of fossil fuels.",
        head_size=46, body_size=20, head_lines=2, body_lines=3)
    y += 10
    y = hrule(draw, y, 2)
    y += 14

    # --- Row 2: two stories ----------------------------------------------
    col_w = (CONTENT - 40) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 40
    top2 = y
    end_left = story_block(
        draw, left_x, col_w, top2,
        "CONFLICT  \u2022  BAHRAIN",
        "Iran strikes Bahrain site as Gulf tensions rise",
        "Bahrain said Iranian projectiles hit an industrial site, "
        "injuring two people. Gulf states condemned the attack as "
        "regional tensions widened.",
        head_size=30, body_size=18, head_lines=3, body_lines=4)
    end_right = story_block(
        draw, right_x, col_w, top2,
        "WAR  \u2022  UKRAINE",
        "Russian drone hits flats near Kyiv; 14 missing",
        "A Russian drone struck a five-storey apartment block in Dymer, "
        "north of Kyiv, on Sunday. Rescuers said 14 people may be "
        "trapped in the rubble.",
        head_size=30, body_size=18, head_lines=3, body_lines=4)
    y = max(end_left, end_right)
    # vertical divider between the two columns
    draw.rectangle([MARGIN + col_w + 19, top2,
                    MARGIN + col_w + 20, y - 6], fill=(180, 175, 165))
    y += 10
    y = hrule(draw, y, 2)
    y += 14

    # --- Row 3: three stories --------------------------------------------
    col3 = (CONTENT - 2 * 32) // 3
    xs = [MARGIN,
          MARGIN + col3 + 32,
          MARGIN + 2 * (col3 + 32)]
    top3 = y
    ends = []
    ends.append(story_block(
        draw, xs[0], col3, top3,
        "CRIME  \u2022  SINALOA, MEXICO",
        "Mexico captures cartel boss \u2018El Chapo Isidro\u2019",
        "Special forces captured Fausto Isidro Meza Flores in Sinaloa "
        "on Saturday. Eleven people were killed in the raid, including "
        "four soldiers.",
        head_size=26, body_size=17, head_lines=3, body_lines=5))
    ends.append(story_block(
        draw, xs[1], col3, top3,
        "DISASTER  \u2022  BANTEN, INDONESIA",
        "Three dead in Indonesia candy factory fire",
        "A fire at a candy factory in Cikande killed three workers on "
        "Sunday. Dozens more were still missing as rescuers searched "
        "the ruins.",
        head_size=26, body_size=17, head_lines=3, body_lines=5))
    ends.append(story_block(
        draw, xs[2], col3, top3,
        "SPACE  \u2022  MERCURY",
        "BepiColombo reaches Mercury after eight years",
        "The European-Japanese spacecraft slipped into orbit around "
        "Mercury on Saturday. ESA reported a thruster glitch but said "
        "the craft is safe.",
        head_size=26, body_size=17, head_lines=3, body_lines=5))
    y = max(ends)
    for i in (1, 2):
        dx = xs[i] - 17
        draw.rectangle([dx, top3, dx + 1, y - 6], fill=(180, 175, 165))
    y += 12
    y = hrule(draw, y, 3)
    y += 10

    # --- Footer -----------------------------------------------------------
    foot_font = font(SANS, 13)
    y = draw_centered(
        draw,
        "Sources: Reuters, Associated Press, AFP, The Straits Times",
        foot_font, y, fill=GREY)
    draw_centered(
        draw,
        "All six stories were first reported on Sunday, 22 November 2026.",
        foot_font, y, fill=GREY)

    img.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({img.size[0]}x{img.size[1]}, {size} bytes)")
    if size > 1048576:
        raise SystemExit("entry.png is over 1 MiB")


if __name__ == "__main__":
    main()
