#!/usr/bin/env python3
"""Turns tools/avatar.jpg into a coloured ASCII grid (tools/portrait.json).

Only needed when the avatar changes. Requires Pillow:
    pip install pillow && python3 tools/build_portrait.py
"""
import json
from collections import deque
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
COLS = ROWS = 46
RAMP = " .:-=+*#%@"          # light → dense; on a dark sky, bright = dense


def main():
    img = Image.open(HERE / "avatar.jpg").convert("RGB").resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()

    # flood-fill the paper background from the border so only the character remains
    bg = [px[0, 0], px[COLS - 1, 0], px[0, ROWS - 1], px[COLS - 1, ROWS - 1]]
    bgc = tuple(sum(c[i] for c in bg) // 4 for i in range(3))

    def is_bg(c):
        return sum(abs(c[i] - bgc[i]) for i in range(3)) < 46

    mask = [[False] * COLS for _ in range(ROWS)]
    q = deque((x, y) for x in range(COLS) for y in (0, ROWS - 1))
    q.extend((x, y) for y in range(ROWS) for x in (0, COLS - 1))
    while q:
        x, y = q.popleft()
        if not (0 <= x < COLS and 0 <= y < ROWS) or mask[y][x] or not is_bg(px[x, y]):
            continue
        mask[y][x] = True
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    # keep only the largest connected shape (drops the little speech bubble)
    seen, best = set(), set()
    for sy in range(ROWS):
        for sx in range(COLS):
            if mask[sy][sx] or (sx, sy) in seen:
                continue
            comp, q2 = set(), deque([(sx, sy)])
            while q2:
                x, y = q2.popleft()
                if not (0 <= x < COLS and 0 <= y < ROWS) or mask[y][x] or (x, y) in comp:
                    continue
                comp.add((x, y))
                q2.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            seen |= comp
            if len(comp) > len(best):
                best = comp
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) not in best:
                mask[y][x] = True

    rows = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            if mask[y][x]:
                row.append(None)
                continue
            r, g, b = px[x, y]
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            ch = RAMP[max(1, min(len(RAMP) - 1, round(lum * (len(RAMP) - 1))))]
            # lift dark ink so it still reads on a night sky
            k = 0.42 if lum < 0.45 else 0.18
            r, g, b = (round(c + (255 - c) * k) for c in (r, g, b))
            row.append([ch, f"#{r:02x}{g:02x}{b:02x}"])
        rows.append(row)
    (HERE / "portrait.json").write_text(json.dumps({"cols": COLS, "rows": ROWS, "grid": rows}, separators=(",", ":")))
    print("portrait.json written", sum(1 for r in rows for c in r if c), "glyphs")


if __name__ == "__main__":
    main()
