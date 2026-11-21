"""Draw an illustrated daily news edition using only the standard library."""

import os
from pathlib import Path
import struct
import zlib
from math import isqrt

SIZE = 1024
# Indexed colors keep the press-style artwork compact.
COLORS = (
    "f3e8d1", "14262c", "d9cbb0", "e97556", "29434b", "41616a",
    "87aeb3", "f6bf68", "af4936", "266d67", "c6d7c6", "fff2d8",
    "493233", "eea283", "b7d8d6", "67766c",
)
PAPER, INK, RULE, CORAL, NIGHT, SLATE, MIST, GOLD, RUST, TEAL, SAGE, WHITE, PLUM, PEACH, ICE, GRAY = range(len(COLORS))

# Each digit encodes one five-dot row of the hand-drawn display alphabet.
GLYPHS = dict(zip(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-%./",
    """
    ehhhhhe  uhuhhhu ehggghe uhhhhhu vgguggv vgguggg
    ehgnhhf hhhvhhh v44444v 72222ic hikokih ggggggv hrllhhh
    hpljhhh ehhhhhe uhuhggg ehhhlid uhhukih fgge11u
    v444444 hhhhhhe hhhhha4 hhhllrh hha4ahh hha4444 v1248gv
    ehjjlhe 4c4444e eh1248v u11e11u 26aiv22 vggu11u egguhhe
    v122488 ehhehhe ehhf11e 000v000 pi48ib0 0000004 112488g
    """.split(),
    strict=True,
))
GLYPHS[" "] = "0000000"

pixels = bytearray(SIZE * SIZE)


def box(x, y, width, height, color):
    assert 0 <= x <= x + width <= SIZE and 0 <= y <= y + height <= SIZE
    span = bytes([color]) * width
    for row in range(y, y + height):
        begin = row * SIZE + x
        pixels[begin:begin + width] = span


def disc(x, y, radius, color):
    for dy in range(-radius, radius + 1):
        dx = isqrt(radius * radius - dy * dy)
        box(x - dx, y + dy, 2 * dx + 1, 1, color)


def stroke(points, width, color):
    for (x, y), (end_x, end_y) in zip(points, points[1:]):
        steps = max(abs(end_x - x), abs(end_y - y), 1)
        for step in range(steps + 1):
            disc(x + (end_x - x) * step // steps,
                 y + (end_y - y) * step // steps, width, color)


def label(x, y, words, scale, color=INK):
    for character in words:
        for row, pattern in enumerate(GLYPHS[character]):
            bits = int(pattern, 32)
            for column in range(5):
                if bits & (16 >> column):
                    box(x + column * scale, y + row * scale, scale, scale, color)
        x += scale * 6


def grain(x, y, width, height, color):
    for row in range(y, y + height, 4):
        for column in range(x + (row * 17 % 7), x + width, 9):
            if (column * column + row * 71 + column * row) % 13 < 5:
                box(column, row, 1, 1, color)


def city():
    box(52, 176, 920, 346, NIGHT)
    disc(756, 339, 127, SLATE)
    disc(756, 339, 103, NIGHT)
    grain(600, 206, 327, 274, MIST)
    # A schematic transmission pylon represents the electricity sites hit.
    stroke([(619, 347), (661, 368), (716, 368)], 2, MIST)
    stroke([(796, 368), (850, 368), (901, 347)], 2, MIST)
    stroke([(713, 461), (755, 274), (798, 461)], 3, GOLD)
    stroke([(720, 430), (783, 404), (730, 404), (791, 430)], 2, GOLD)
    stroke([(716, 369), (755, 347), (796, 369), (716, 369)], 2, GOLD)
    stroke([(729, 335), (755, 319), (782, 335), (729, 335)], 2, GOLD)
    for number, (x, y, w) in enumerate([
        (588, 446, 48), (642, 418, 42), (686, 455, 39), (726, 422, 52),
        (780, 445, 33), (815, 414, 51), (868, 455, 44), (913, 435, 38),
    ]):
        box(x, y, w, 522 - y, INK)
        box(x + 3, y, w - 3, 2, MIST)
        for window_x in range(x + 9, x + w - 4, 12):
            for window_y in range(y + 11, 510, 13):
                if (window_x + window_y + number) % 11 < 4:
                    box(window_x, window_y, 4, 3, GOLD)


def icon(kind, x, y):
    if kind == "court":
        stroke([(x-27, y-8), (x, y-24), (x+27, y-8), (x-27, y-8)], 2, WHITE)
        for offset in [-18, 0, 18]:
            box(x+offset-2, y-1, 5, 20, WHITE)
        box(x-28, y+22, 56, 5, WHITE)
    elif kind == "market":
        path = [(x-25, y-18), (x-11, y-7), (x+1, y-12),
                (x+10, y+5), (x+25, y+18)]
        stroke(path, 3, WHITE)
        stroke([(x+25, y+4), (x+25, y+18), (x+10, y+18)], 3, WHITE)
    elif kind == "health":
        box(x-7, y-24, 14, 48, WHITE)
        box(x-24, y-7, 48, 14, WHITE)
    elif kind == "climate":
        stroke([(x-20, y+18), (x-14, y-2), (x+2, y-17),
                (x+23, y-22), (x+17, y+2), (x+2, y+16),
                (x-20, y+18), (x+12, y-10)], 2, WHITE)
    elif kind == "storm":
        for offset in (-16, 0, 16):
            stroke([(x-24, y+offset), (x+15, y+offset),
                    (x+23, y+offset-6)], 2, WHITE)
    elif kind == "talks":
        for dx, dy in [(-20, 13), (0, -19), (20, 13)]:
            disc(x+dx, y+dy, 6, WHITE)
        stroke([(x-18, y+6), (x, y-13), (x+18, y+6),
                (x+12, y+17), (x-12, y+17), (x-18, y+6)], 2, WHITE)


def edition():
    box(0, 0, SIZE, SIZE, PAPER)
    box(52, 47, 920, 5, INK)
    label(52, 73, "WORLD NEWS", 11)
    label(737, 78, "FRIDAY", 4, RUST)
    label(737, 110, "20 NOV 2026", 3)
    box(52, 155, 920, 2, RULE)

    city()
    box(77, 211, 9, 19, CORAL)
    label(101, 211, "EUROPE / WAR", 3, GOLD)
    label(77, 256, "RUSSIA HITS", 7, WHITE)
    label(77, 317, "UKRAINE", 10, WHITE)
    label(77, 414, "STRIKES HIT POWER SITES", 3, ICE)
    label(77, 447, "MISSILES FALL IN POLAND", 3, ICE)

    stories = (
        ("court", PLUM, "MYANMAR / ROHINGYA", "MYANMAR REJECTS", "ICJ GENOCIDE RULING"),
        ("market", RUST, "US / MARKETS", "NASDAQ FALLS 5%", "IN TECH SELL-OFF"),
        ("health", TEAL, "DR CONGO / HEALTH", "WHO REPORTS MORE", "EBOLA CASES"),
        ("climate", SLATE, "TURKEY / CLIMATE", "COP31 DRAFT MAPS", "FINANCE ROADMAP"),
        ("storm", NIGHT, "BRAZIL / WEATHER", "SUPERCELL HITS", "SOUTHERN BRAZIL"),
        ("talks", PLUM, "CHINA / DIPLOMACY", "TRUMP HAILS TALKS", "WITH XI AND PUTIN"),
    )
    for index, (kind, color, location, first, second) in enumerate(stories):
        x = 52 + (index % 2) * 469
        y = 550 + (index // 2) * 137
        box(x, y, 451, 2, RULE)
        box(x, y+18, 76, 76, color)
        icon(kind, x+38, y+56)
        label(x+94, y+20, location, 2, RUST)
        label(x+94, y+47, first, 3)
        label(x+94, y+77, second, 3)
    box(511, 550, 2, 377, RULE)
    box(52, 968, 920, 2, INK)
    label(52, 982, "REPORTING / AP  REUTERS  WHO  THE GUARDIAN", 2, GRAY)


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data)))


def main():
    edition()
    scanlines = b"".join(
        b"\0" + pixels[offset:offset + SIZE]
        for offset in range(0, len(pixels), SIZE)
    )
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 3, 0, 0, 0))
           + chunk(b"PLTE", bytes.fromhex("".join(COLORS)))
           + chunk(b"IDAT", zlib.compress(scanlines, 9))
           + chunk(b"IEND", b""))
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output.mkdir(parents=True, exist_ok=True)
    (output / "entry.png").write_bytes(png)


if __name__ == "__main__":
    main()
