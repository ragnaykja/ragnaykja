#!/usr/bin/env python3
"""Renders the contribution heatmap ("tracks in the snow") as assets/heatmap.svg.

Reads the public contribution calendar, so no token is needed.
Run from the repo root:  python3 tools/build_heatmap.py [username]
"""
import datetime as dt
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_assets import OUT, PAW, SAGE, TEAL, LAVENDER, SLATE, SERIF, SANS  # noqa: E402
from github_data import contributions  # noqa: E402

USER = sys.argv[1] if len(sys.argv) > 1 else "ragnaykja"


def render(days):
    cell, gap = 17, 4.5
    step = cell + gap
    left, top = 40, 34
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)   # week starts on Sunday
    weeks = ((days[-1][0] - start).days // 7) + 1
    W = int(left + weeks * step + 10)
    H = int(top + 7 * step + 50)

    def mix(c1, c2, u):
        a, b = int(c1[1:], 16), int(c2[1:], 16)
        return "#" + "".join(f"{round(((a >> s) & 255) * (1 - u) + ((b >> s) & 255) * u):02x}" for s in (16, 8, 0))

    def aurora(x):
        u = (x - left) / (W - left)
        return mix(SAGE, TEAL, u * 2) if u < .5 else mix(TEAL, LAVENDER, (u - .5) * 2)

    size = {1: 20, 2: 23, 3: 26, 4: 29}
    alpha = {1: .6, 2: .75, 3: .9, 4: 1}

    def paw(cx, cy, s, color, op, title=""):
        t = f"<title>{title}</title>" if title else ""
        return (f'<use href="#paw" x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" width="{s}" height="{s}" fill="{color}" '
                f'opacity="{op}" transform="rotate(90 {cx:.1f} {cy:.1f})">{t}</use>')

    rects, months, last_month = [], [], None
    for d, level, n in days:
        idx = (d - start).days
        wk, wd = idx // 7, idx % 7
        cx, cy = left + wk * step + cell / 2, top + wd * step + cell / 2
        if level:
            rects.append(paw(cx, cy, size[level], aurora(cx), alpha[level], f"{n} contributions on {d:%b %-d, %Y}"))
        else:
            rects.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.7" fill="{SLATE}" opacity=".35"/>')
        if d.day <= 7 and wd == 0 and d.month != last_month:
            months.append(f'<text x="{left + wk * step:.1f}" y="{top - 12}" font-size="13">{d:%b}</text>')
            last_month = d.month
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        months.append(f'<text x="{left - 8}" y="{top + wd * step + cell - 4:.1f}" font-size="11" text-anchor="end">{name}</text>')

    total = sum(n for _, _, n in days)
    active = sum(1 for _, lv, _ in days if lv)
    caption = (f"{total} contributions · {active} days out on the trail"
               if total else "fresh snow — no tracks yet this year")
    legend_x = W - 210
    legend = [f'<text x="{legend_x}" y="{H - 14}" font-size="12">quiet</text>',
              f'<circle cx="{legend_x + 48}" cy="{H - 18}" r="1.7" fill="{SLATE}" opacity=".35"/>']
    for i, lv in enumerate((1, 2, 3, 4)):
        legend.append(paw(legend_x + 70 + i * 24, H - 18, size[lv], aurora(W - 120 + i * 20), alpha[lv]))
    legend.append(f'<text x="{legend_x + 70 + 4 * 24 + 2}" y="{H - 14}" font-size="12">busy</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(caption)}">
<defs>{PAW}<linearGradient id="aur" gradientUnits="userSpaceOnUse" x1="{left}" y1="0" x2="{W}" y2="0">
<stop offset="0" stop-color="{SAGE}"/><stop offset=".5" stop-color="{TEAL}"/><stop offset="1" stop-color="{LAVENDER}"/></linearGradient></defs>
<style>text{{font-family:{SANS};fill:{SLATE}}}.serif{{font-family:{SERIF}}}</style>
<g>{"".join(months)}</g>
<g>{"".join(rects)}</g>
<text x="{left}" y="{H - 14}" class="serif" font-size="16" font-style="italic">{html.escape(caption)}</text>
<g>{"".join(legend)}</g>
</svg>'''


if __name__ == "__main__":
    days = contributions(USER)
    svg = render(days)
    (OUT / "heatmap.svg").write_text(svg, encoding="utf-8")
    print(f"  heatmap.svg  {len(days)} days, {len(svg) / 1024:.1f} KB")
