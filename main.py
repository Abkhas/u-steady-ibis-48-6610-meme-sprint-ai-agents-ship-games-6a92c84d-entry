#!/usr/bin/env python3
"""Meme Sprint: AI Agents Ship Games -- "This is fine" meme entry.

Writes one 1024x1024 PNG meme to /output/entry.png (or $MAKEFUN_OUTPUT_DIR,
falling back to ./out). Pure Python standard library: no fonts, no assets,
no network. Every pixel comes from the drawing primitives and the 5x7
bitmap font defined below, so the program runs unchanged in the grader
sandbox.

The joke: a dog sits calmly at a laptop while the room burns around it.
Top text: MY AI AGENT / SHIPPED MY GAME. Bottom text: IT HAS 47 BUGS /
BUT THE DEMO IS IN 5 MINUTES. The agent shipped it, it is on fire, the
demo is in five minutes, and the dog is fine with it.
"""
import os
import struct
import sys
import zlib

W = H = 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, rows are "0"/"1" strings. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '(': ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ')': ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "10110", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10100", "10000", "01110"),
    '*': ("00000", "10001", "01010", "11111", "01010", "10001", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    """Pixel width of s at the given integer scale (5px glyph + 1px gap)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w=W, h=H, bg=(255, 255, 255)):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        r = max(1, t // 2)
        while True:
            self.circle(x, y, r, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
        (ya, xa), (yb, xb), (yc, xc) = ys
        if yc == ya:
            return
        for y in range(max(0, ya), min(self.h, yc + 1)):
            if y < yb:
                xa_y = xa + (xb - xa) * (y - ya) / float(yb - ya or 1)
                xc_y = xc + (xa - xc) * (y - ya) / float(yc - ya or 1)
            else:
                xa_y = xb + (xc - xb) * (y - yb) / float(yc - yb or 1)
                xc_y = xc + (xa - xc) * (y - ya) / float(yc - ya or 1)
            lo, hi = sorted([int(xa_y), int(xc_y)])
            self.fill_rect(lo, y, hi - lo + 1, 1, c)


# ---------------------------------------------------------------- text ----
def draw_glyph(cv, ch, x, y, scale, color):
    g = FONT.get(ch)
    if g is None:
        return
    for r, row in enumerate(g):
        for col, bit in enumerate(row):
            if bit == '1':
                cv.fill_rect(x + col * scale, y + r * scale, scale, scale, color)


def draw_text(cv, s, cx, y, scale, color):
    """Draw s centred on cx, top edge at y."""
    w = text_width(s, scale)
    x = cx - w // 2
    for ch in s:
        draw_glyph(cv, ch, x, y, scale, color)
        x += 6 * scale


# ------------------------------------------------------------------ png ----
def write_png(cv, path):
    raw = b"".join(
        b"\x00" + bytes(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
        for y in range(cv.h))
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------ the meme ----
def flame(cv, x, y, s):
    """One flame tongue: red base, orange middle, yellow core."""
    w = int(s * 1.4)
    cv.tri(x, y, x + w, y, x + w // 2, y - int(s * 1.2), (226, 59, 46))
    cv.tri(x + int(w * 0.22), y, x + int(w * 0.78), y,
           x + w // 2, y - int(s * 0.85), (244, 124, 32))
    cv.tri(x + int(w * 0.36), y, x + int(w * 0.64), y,
           x + w // 2, y - int(s * 0.45), (255, 210, 63))


def draw_meme(cv):
    # top + bottom text bands
    cv.fill_rect(0, 0, W, 210, (255, 255, 255))
    cv.fill_rect(0, 830, W, H - 830, (255, 255, 255))
    draw_text(cv, "MY AI AGENT", 512, 22, 9, (0, 0, 0))
    draw_text(cv, "SHIPPED MY GAME", 512, 112, 9, (0, 0, 0))
    draw_text(cv, "IT HAS 47 BUGS", 512, 848, 6, (0, 0, 0))
    draw_text(cv, "BUT THE DEMO IS IN 5 MINUTES", 512, 922, 6, (0, 0, 0))
    # room: orange wall + darker floor
    cv.fill_rect(0, 210, W, 490, (242, 169, 59))
    cv.fill_rect(0, 700, W, 130, (201, 123, 45))
    # framed picture on the wall
    cv.fill_rect(110, 260, 170, 130, (90, 50, 20))
    cv.fill_rect(122, 272, 146, 106, (255, 233, 168))
    cv.tri(150, 360, 195, 300, 240, 360, (120, 170, 90))
    cv.circle(235, 300, 16, (255, 210, 63))
    # flames along both edges and the floor line
    for (fx, fy, fs) in ((18, 700, 64), (10, 560, 80), (60, 420, 70),
                         (940, 700, 64), (930, 540, 84), (880, 400, 66),
                         (300, 830, 56), (660, 830, 60), (150, 830, 48),
                         (820, 830, 50), (470, 830, 54), (30, 830, 44)):
        flame(cv, fx, fy, fs)
    # dog: body, head, ears, muzzle, eyes, nose
    cv.ellipse(512, 610, 150, 115, (160, 102, 44))
    cv.tri(420, 425, 468, 358, 455, 475, (122, 74, 31))
    cv.tri(604, 425, 556, 358, 569, 475, (122, 74, 31))
    cv.circle(512, 470, 95, (160, 102, 44))
    cv.ellipse(512, 505, 48, 32, (217, 160, 102))
    cv.circle(478, 448, 9, (0, 0, 0))
    cv.circle(546, 448, 9, (0, 0, 0))
    cv.circle(512, 488, 13, (0, 0, 0))
    cv.line(482, 522, 512, 532, (60, 35, 15), 5)
    cv.line(512, 532, 542, 522, (60, 35, 15), 5)
    # table in front of the dog
    cv.fill_rect(120, 640, 784, 190, (123, 75, 42))
    cv.fill_rect(120, 640, 784, 14, (150, 95, 55))
    # paws on the table
    cv.ellipse(440, 648, 36, 18, (160, 102, 44))
    cv.ellipse(584, 648, 36, 18, (160, 102, 44))
    # laptop: glowing screen with a tiny game on it
    cv.fill_rect(445, 545, 134, 95, (43, 43, 43))
    cv.fill_rect(455, 555, 114, 75, (154, 209, 255))
    cv.fill_rect(470, 600, 84, 10, (90, 160, 90))
    cv.fill_rect(500, 575, 24, 24, (226, 59, 46))
    cv.fill_rect(430, 640, 164, 12, (43, 43, 43))
    # coffee mug
    cv.fill_rect(648, 596, 44, 44, (226, 59, 46))
    cv.line(692, 606, 706, 606, (226, 59, 46), 6)
    cv.line(706, 606, 706, 630, (226, 59, 46), 6)
    cv.line(692, 630, 706, 630, (226, 59, 46), 6)


# ---------------------------------------------------------- entrypoint ----
def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas()
    draw_meme(cv)
    path = os.path.join(out_dir, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
