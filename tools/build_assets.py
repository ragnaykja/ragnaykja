#!/usr/bin/env python3
"""Generates the SVG assets for the profile README.

Concept: the profile is one night walk. A trail of paw prints starts in the
snow at dusk (hero), wanders through every chapter divider and ends at a wolf
sitting under the northern lights (footer).

Run from the repo root:  python3 tools/build_assets.py
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ── palette: soft, pastel night ───────────────────────────────────────
NIGHT0, NIGHT1, NIGHT2 = "#0e1424", "#18203a", "#2a2f4f"
DUSK = "#55496b"
SNOW_HI, SNOW_LO, SNOW_SH = "#c3cde0", "#97a4c0", "#7a87a6"
HILL_FAR = "#2b3354"
INK, MUTED = "#eef1f7", "#aab4cb"
SLATE = "#8592ad"                 # mid-tone: readable on GitHub light *and* dark
SAGE, TEAL, LAVENDER, ROSE = "#9fd8bf", "#8cc7c4", "#b4a7e0", "#dcb3c9"

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
BASE_CSS = f".serif{{font-family:{SERIF}}}.sans{{font-family:{SANS}}}"

# Wolf track (front foot), pointing up: oval outline, two-lobed heel pad,
# four toes – the inner pair forward and close together – with claw marks.
PAW = ('<symbol id="paw" viewBox="-20 -20 40 40">'
       '<path d="M-7.4 9.5 C-8.2 4.4 -4.6 2.4 -2 3.6 Q0 4.4 2 3.6 C4.6 2.4 8.2 4.4 7.4 9.5 '
       'C6.9 14.4 4 16.4 1.8 15.2 Q0 14.2 -1.8 15.2 C-4 16.4 -6.9 14.4 -7.4 9.5Z"/>'
       '<ellipse cx="-3.1" cy="-8.4" rx="2.8" ry="4.6" transform="rotate(-5 -3.1 -8.4)"/>'
       '<ellipse cx="3.1" cy="-8.4" rx="2.8" ry="4.6" transform="rotate(5 3.1 -8.4)"/>'
       '<ellipse cx="-8.2" cy="-2.2" rx="2.6" ry="3.9" transform="rotate(-20 -8.2 -2.2)"/>'
       '<ellipse cx="8.2" cy="-2.2" rx="2.6" ry="3.9" transform="rotate(20 8.2 -2.2)"/>'
       '<path d="M-4.2 -12.6 L-3.5 -16 L-2.5 -12.8Z M4.2 -12.6 L3.5 -16 L2.5 -12.8Z '
       'M-10.4 -5.4 L-11 -8.6 L-8.9 -6.1Z M10.4 -5.4 L11 -8.6 L8.9 -6.1Z"/></symbol>')

# Sitting wolf, head raised towards the sky, facing left. Box 0..100.
WOLF = ('<symbol id="wolf" viewBox="0 0 100 100"><path d="'
        'M3 9 Q12 7 20 10 L24 9 L26 0 L30 7 L34 1 L36 11 Q41 16 45 24 '
        'Q48 31 53 38 Q60 50 68 57 Q83 63 83 82 Q89 89 98 82 Q100 97 86 100 '
        'L36 100 Q31 99 35 96 Q37 84 34 70 Q31 56 27 44 Q24 38 21 33 Q18 28 15 23 '
        'L12 19 Q7 17 2 15 Q6 13 9 12 Z"/></symbol>')

ANIM = '''
.s{animation:tw 6s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.8}50%{opacity:.3}}
.veil{animation:drift 40s ease-in-out infinite}.veil2{animation:drift 55s ease-in-out infinite reverse}
@keyframes drift{0%,100%{transform:translateX(0)}50%{transform:translateX(-60px)}}
@media (prefers-reduced-motion:reduce){.s,.veil,.veil2{animation:none}}
'''


def svg(w, h, body, defs="", css="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{PAW}{WOLF}{defs}</defs>'
            f'<style>{BASE_CSS}{ANIM}{css}</style>{body}</svg>')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:<20} {len(content.encode()) / 1024:6.1f} KB")


def stars(rnd, n, x0, x1, y0, y1, max_r=1.2):
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice([.5, .6, .8, 1.0, max_r])
        out.append(f'<circle class="s" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#f1f4ff" '
                   f'style="animation-delay:{rnd.uniform(0, 6):.1f}s"/>')
    return "".join(out)


def bezier(p0, p1, p2, p3):
    def f(t):
        u = 1 - t
        return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])
    return f


def trail(f, n, size, color, opacity=1.0, t0=0.0, t1=1.0, ease=1.0, stride=None, fade=None):
    """Alternating left/right paw prints along curve f(t)."""
    out = []
    for i in range(n):
        lin = i / (n - 1)
        t = t0 + (t1 - t0) * (1 - (1 - lin) ** ease)
        x, y = f(t)
        xa, ya = f(max(t - 1e-3, 0))
        xb, yb = f(min(t + 1e-3, 1))
        ang = math.atan2(yb - ya, xb - xa)
        s = size(lin) if callable(size) else size
        side = (stride(lin) if callable(stride) else (stride or s * .55)) * (1 if i % 2 else -1)
        px, py = x - math.sin(ang) * side, y + math.cos(ang) * side
        op = opacity * (fade(lin) if fade else 1)
        out.append(f'<use href="#paw" x="{px - s / 2:.1f}" y="{py - s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" '
                   f'transform="rotate({math.degrees(ang) + 90:.1f} {px:.1f} {py:.1f})" opacity="{op:.2f}"/>')
    return f'<g fill="{color}">{"".join(out)}</g>'


def veil(gid, x, y, w, h, colors, blur, opacity, cls):
    stops = "".join(f'<stop offset="{i / (len(colors) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(colors))
    d = (f"M{x} {y + h * .55} C{x + w * .25} {y + h * .1} {x + w * .45} {y + h * .9} {x + w * .7} {y + h * .35} "
         f"S{x + w * .95} {y} {x + w} {y + h * .2} L{x + w} {y + h * .55} "
         f"C{x + w * .8} {y + h * .45} {x + w * .65} {y + h} {x + w * .45} {y + h * .75} "
         f"S{x + w * .15} {y + h * .6} {x} {y + h}Z")
    return (f'<linearGradient id="{gid}" x1="0" x2="1">{stops}</linearGradient>'
            f'<filter id="{gid}b" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="{blur}"/></filter>',
            f'<g filter="url(#{gid}b)" opacity="{opacity}"><path class="{cls}" d="{d}" fill="url(#{gid})"/></g>')


# ── ascii portrait (from tools/portrait.json) ─────────────────────────
def portrait(cx, cy, r):
    import json
    data = json.loads((Path(__file__).resolve().parent / "portrait.json").read_text())
    cols, grid = data["cols"], data["grid"]
    cell = 2 * r / cols
    x0, y0 = cx - r, cy - r
    lines = []
    for j, row in enumerate(grid):
        runs, cur, xs, chars = [], None, [], []
        for i, c in enumerate(row + [None]):
            col = None
            if c is not None:
                h = c[1].lstrip("#")
                col = "#" + "".join(f"{min(255, round(int(h[k:k + 2], 16) / 24) * 24):02x}" for k in (0, 2, 4))
            if col != cur and chars:
                runs.append((cur, xs, chars))
                xs, chars = [], []
            cur = col
            if c is not None:
                xs.append(f"{x0 + i * cell:.1f}")
                chars.append(escape(c[0]))
        if runs:
            y = y0 + (j + 1) * cell
            spans = "".join(f'<tspan x="{" ".join(x)}" fill="{c}">{"".join(ch)}</tspan>' for c, x, ch in runs)
            lines.append(f'<text y="{y:.1f}">{spans}</text>')
    return (f'<g class="ascii" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
            f'font-size="{cell * 1.18:.1f}" font-weight="600">{"".join(lines)}</g>')


# ── hero: dusk, the trail begins, the portrait rises like a moon ─────
def hero(stats):
    W, H = 1200, 480
    CX, CY, R = 905, 205, 168
    rnd = random.Random(7)
    v1d, v1 = veil("v1", 380, 20, 900, 200, [SAGE, TEAL, LAVENDER], 30, .38, "veil")
    v2d, v2 = veil("v2", 300, 80, 700, 120, [LAVENDER, ROSE], 34, .2, "veil2")
    defs = f'''{v1d}{v2d}
<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="moon"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset=".55" stop-color="{LAVENDER}" stop-opacity=".16"/><stop offset="1" stop-color="{LAVENDER}" stop-opacity="0"/></radialGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SAGE}" stop-opacity="0"/><stop offset=".5" stop-color="{SAGE}" stop-opacity=".14"/><stop offset="1" stop-color="{SAGE}" stop-opacity="0"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{NIGHT0}"/><stop offset=".45" stop-color="{NIGHT1}"/>
<stop offset=".72" stop-color="{NIGHT2}"/><stop offset="1" stop-color="{DUSK}"/></linearGradient>
<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SNOW_HI}"/><stop offset="1" stop-color="{SNOW_LO}"/></linearGradient>
<linearGradient id="snow2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9b5cd"/><stop offset="1" stop-color="#8794b2"/></linearGradient>'''
    css = f'''
.ascii{{animation:breathe 7s ease-in-out infinite}}@keyframes breathe{{0%,100%{{opacity:.95}}50%{{opacity:.78}}}}
.scanbar{{animation:scan 9s ease-in-out infinite}}@keyframes scan{{0%{{transform:translateY(-60px);opacity:0}}10%{{opacity:1}}55%{{opacity:1}}70%,100%{{transform:translateY({2 * R + 40}px);opacity:0}}}}
.orbit{{transform-origin:{CX}px {CY}px;animation:orbit 60s linear infinite}}@keyframes orbit{{to{{transform:rotate(360deg)}}}}
@media (prefers-reduced-motion:reduce){{.ascii,.scanbar,.orbit{{animation:none}}}}'''
    f = bezier((30, 530), (380, 420), (700, 400), (905, 366))
    tracks = trail(f, 22, lambda l: 30 - 24 * l, SNOW_SH, .9, t0=.1, ease=1.6,
                   stride=lambda l: 13 - 10 * l, fade=lambda l: 1 - .45 * l)
    cols = [(str(stats["projects"]), "projects"), (str(stats["contributions"]), "contributions this year"),
            (str(stats["languages"]), "languages"), (str(stats["since"]), "on github since")]
    stat_svg, x = [], 76
    for num, label in cols:
        stat_svg.append(f'<text x="{x}" y="312" class="serif" font-size="34" fill="{INK}">{escape(num)}</text>'
                        f'<text x="{x + 1}" y="334" class="sans" font-size="10.5" letter-spacing="2.2" fill="{MUTED}">{escape(label.upper())}</text>')
        x += max(110, len(label) * 8.6 + 40)
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(rnd, 80, 0, W, 0, 330)}
{v2}{v1}
<circle cx="{CX}" cy="{CY}" r="{R + 46}" fill="url(#halo)"/>
<circle cx="{CX}" cy="{CY}" r="{R + 2}" fill="{NIGHT0}" opacity=".7"/>
<g clip-path="url(#moon)">{portrait(CX, CY, R)}<rect class="scanbar" x="{CX - R}" y="{CY - R - 30}" width="{2 * R}" height="60" fill="url(#scan)"/></g>
<g class="orbit"><circle cx="{CX}" cy="{CY}" r="{R + 16}" fill="none" stroke="{MUTED}" stroke-opacity=".35" stroke-dasharray="2 7"/>
<circle cx="{CX + R + 16}" cy="{CY}" r="3" fill="{SAGE}"/></g>
<path d="M0 352 C140 328 260 348 420 336 S700 318 860 340 S1080 330 1200 344 L1200 {H} L0 {H}Z" fill="{HILL_FAR}" opacity=".92"/>
<path d="M0 384 C180 360 340 380 520 368 S840 350 1000 364 S1140 358 1200 362 L1200 {H} L0 {H}Z" fill="url(#snow2)"/>
<path d="M0 414 C220 392 420 408 640 398 S1000 386 1200 396 L1200 {H} L0 {H}Z" fill="url(#snow)"/>
{tracks}
</g>
<text x="72" y="128" class="serif" font-size="80" fill="{INK}" letter-spacing="-1">Ragna</text>
<text x="76" y="168" class="sans" font-size="14" fill="{MUTED}" letter-spacing="4.5">DEVELOPER  ·  GIS  ·  AUTOMATION</text>
<text x="76" y="212" class="serif" font-size="19" font-style="italic" fill="{MUTED}">quiet tools that do a loud amount of work.</text>
<line x1="76" x2="600" y1="256" y2="256" stroke="{MUTED}" stroke-opacity=".22"/>
{"".join(stat_svg)}'''
    write("hero.svg", svg(W, H, body, defs, css, "Ragna – developer, GIS, automation"))


def poly_trail(points, size, step, color, offset=3.5, base_op=.55, wave=None):
    """Wolf prints walking along a polyline. `wave` = (delay0, delay_step) adds a
    soft brightening that travels along the trail like someone walking it."""
    segs, total = [], 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        segs.append((x1, y1, x2, y2, L, total))
        total += L
    out, k, d = [], 0, step / 2
    while d < total - step / 3:
        for x1, y1, x2, y2, L, s0 in segs:
            if s0 <= d <= s0 + L:
                u = (d - s0) / L
                x, y = x1 + (x2 - x1) * u, y1 + (y2 - y1) * u
                ang = math.atan2(y2 - y1, x2 - x1)
                break
        side = offset * (1 if k % 2 else -1)
        px, py = x - math.sin(ang) * side, y + math.cos(ang) * side
        anim = ""
        if wave:
            anim = f' class="wk" style="animation-delay:{wave[0] + k * wave[1]:.2f}s"'
        out.append(f'<use href="#paw"{anim} x="{px - size / 2:.1f}" y="{py - size / 2:.1f}" width="{size}" height="{size}" '
                   f'transform="rotate({math.degrees(ang) + 90:.1f} {px:.1f} {py:.1f})" opacity="{base_op}"/>')
        d += step
        k += 1
    return f'<g fill="{color}">{"".join(out)}</g>', k


# ── trail map: every path is a language, every stop a project ────────
TRAIL_COLORS = {"TypeScript": "#8798dc", "JavaScript": "#c9a865", "Python": "#6fb89c",
                "Rust": "#d0977a", "Go": "#6cb8c8", "Shell": "#9fb07a", "CSS": "#b08ad8", "HTML": "#d98b8b"}
FALLBACK_COLORS = ["#a08ad6", "#d08aa8", "#5fb3b3", "#c9a26b"]


def trailmap(repos):
    groups = {}
    for r in repos:
        groups.setdefault(r["language"] or "Other", []).append(r)
    langs = sorted(groups, key=lambda l: (-len(groups[l]), l))
    n = len(langs)
    W, gap, top = 1200, 100, 64
    H = top + (n - 1) * gap + 104
    DX, DY = 1080, top + (n - 1) * gap / 2 + 8        # the den
    trails, stops, labels = [], [], []
    for i, lang in enumerate(langs):
        color = TRAIL_COLORS.get(lang) or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        y = top + i * gap
        ey = DY + (i - (n - 1) / 2) * 14
        bend = DX - 80 - abs(y - ey)
        pts = [(190, y), (bend, y), (DX - 80, ey), (DX - 44, ey)]
        g, _ = poly_trail(pts, 26, 34, color, offset=4, base_op=.55, wave=(1 + i * .7, .12))
        trails.append(g)
        labels.append(f'<text x="20" y="{y + 5}" class="sans" font-size="13" font-weight="600" letter-spacing="2" fill="{color}">{escape(lang.upper())}</text>')
        items = groups[lang]
        span = bend - 290
        for k, r in enumerate(items):
            sx = 290 + span * (k + .5) / len(items)
            above = k % 2 == 0
            name = r["name"] if len(r["name"]) <= 30 else r["name"][:29] + "…"
            stops.append(f'<circle cx="{sx:.0f}" cy="{y}" r="10" fill="{color}" fill-opacity=".18"/>'
                         f'<circle cx="{sx:.0f}" cy="{y}" r="5" fill="{color}"/>'
                         f'<text x="{sx:.0f}" y="{y - 22 if above else y + 34}" text-anchor="middle" class="sans" font-size="15" fill="{SLATE}">{escape(name)}</text>')
    import base64
    av = base64.b64encode((Path(__file__).resolve().parent / "avatar.jpg").read_bytes()).decode()
    defs = f'<clipPath id="den"><circle cx="{DX}" cy="{DY}" r="34"/></clipPath>'
    css = '''
.wk{animation:wk 9s ease-in-out infinite}@keyframes wk{0%%{opacity:.5}4%%{opacity:1}14%%,100%%{opacity:.5}}
.ring{animation:ring 3.6s ease-out infinite;transform-origin:%dpx %dpx}@keyframes ring{0%%{opacity:.5;transform:scale(1)}100%%{opacity:0;transform:scale(1.6)}}
@media (prefers-reduced-motion:reduce){.wk,.ring{animation:none}}''' % (DX, DY)
    body = f'''{"".join(trails)}
<circle class="ring" cx="{DX}" cy="{DY}" r="40" fill="none" stroke="{SLATE}" stroke-width="1.2"/>
<circle cx="{DX}" cy="{DY}" r="39" fill="none" stroke="{SLATE}" stroke-opacity=".5" stroke-width="1.5"/>
<image clip-path="url(#den)" x="{DX - 34}" y="{DY - 34}" width="68" height="68" href="data:image/jpeg;base64,{av}"/>
<text x="{DX}" y="{DY + 64}" text-anchor="middle" class="serif" font-size="17" font-style="italic" fill="{SLATE}">the den</text>
{"".join(labels)}
{"".join(stops)}
<text x="20" y="{H - 12}" class="serif" font-size="16" font-style="italic" fill="{SLATE}">every path is a language, every stop a project.</text>'''
    write("trailmap.svg", svg(W, H, body, defs, css, "Projects as a trail map, one path per language"))


# ── chapter dividers: the trail starts small and walks towards you ───
def chapter(num, title, sub, seed):
    W, H = 1200, 178
    rnd = random.Random(seed)
    a = rnd.uniform(-10, 10)
    f = bezier((16, 132), (360, 158 + a), (760, 118 - a), (1160, 120 + a))
    out, n = [], 17
    for i in range(n):
        lin = i / (n - 1)
        t = lin ** 1.45                      # tight steps far away, long strides up close
        x, y = f(t)
        xa, ya = f(max(t - 1e-3, 0))
        xb, yb = f(min(t + 1e-3, 1))
        ang = math.atan2(yb - ya, xb - xa)
        s = 12 + 46 * lin ** 1.25
        side = s * .3 * (1 if i % 2 else -1)
        px, py = x - math.sin(ang) * side, y + math.cos(ang) * side
        out.append(f'<use href="#paw" x="{px - s / 2:.1f}" y="{py - s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" '
                   f'transform="rotate({math.degrees(ang) + 90:.1f} {px:.1f} {py:.1f})" opacity="{.35 + .4 * lin:.2f}"/>')
    body = f'''<text x="4" y="40" class="serif" font-size="17" font-style="italic" fill="{SLATE}">{escape(num)}</text>
<text x="4" y="76" class="serif" font-size="40" fill="{SLATE}">{escape(title)}</text>
<text x="6" y="100" class="sans" font-size="13" letter-spacing="2" fill="{SLATE}" opacity=".8">{escape(sub.upper())}</text>
<g fill="{SLATE}">{"".join(out)}</g>'''
    write(f"chapter-{seed}.svg", svg(W, H, body, "", "", f"{num} – {title}"))


# ── footer: the trail ends at the wolf, under the aurora ──────────────
def footer():
    W, H = 1200, 340
    rnd = random.Random(21)
    v1d, v1 = veil("f1", -80, 10, 1360, 190, [SAGE, TEAL, LAVENDER, ROSE], 26, .5, "veil")
    v2d, v2 = veil("f2", 100, 40, 1000, 130, [TEAL, SAGE], 30, .28, "veil2")
    defs = f'''{v1d}{v2d}<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NIGHT0}"/><stop offset=".7" stop-color="{NIGHT1}"/><stop offset="1" stop-color="{NIGHT2}"/></linearGradient>
<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#aab6ce"/><stop offset="1" stop-color="#7f8cab"/></linearGradient>'''
    f = bezier((-20, 330), (300, 300), (620, 312), (846, 262))
    tracks = trail(f, 20, lambda l: 20 - 7 * l, "#6d7a99", .9, t0=.04, t1=.97, stride=lambda l: 9 - 3 * l)
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(rnd, 90, 0, W, 0, 230)}
{v2}{v1}
<path d="M0 270 C200 250 380 268 560 258 S900 236 1200 252 L1200 340 L0 340Z" fill="{HILL_FAR}" opacity=".8"/>
<path d="M0 304 C260 286 520 300 760 270 Q860 252 930 250 Q1040 252 1200 280 L1200 340 L0 340Z" fill="url(#snow)"/>
{tracks}
<use href="#wolf" x="838" y="142" width="116" height="116" fill="{NIGHT0}"/>
</g>
<text x="72" y="96" class="serif" font-size="30" fill="{INK}">Build things. Break things.</text>
<text x="72" y="134" class="serif" font-size="30" font-style="italic" fill="{INK}">Learn why they broke.</text>
<text x="74" y="172" class="sans" font-size="13" letter-spacing="2.5" fill="{MUTED}">THANKS FOR WALKING A BIT OF THE WAY</text>'''
    write("footer.svg", svg(W, H, body, defs, "", "Build things. Break things. Learn why they broke."))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from github_data import contributions, profile, repos

    user = sys.argv[1] if len(sys.argv) > 1 else "ragnaykja"
    rs = repos(user)
    stats = {
        "projects": len(rs),
        "contributions": sum(n for _, _, n in contributions(user)),
        "languages": len({r["language"] for r in rs if r["language"]}),
        "since": profile(user)["created_at"][:4],
    }
    print("building assets →", OUT, stats)
    hero(stats)
    chapter("I", "the den", "who I am", 1)
    chapter("II", "the trail", "things I've built", 2)
    chapter("III", "tracks in the snow", "a year of commits", 3)
    trailmap(rs)
    footer()
