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

# Paw print, pointing up: soft triangular heel pad and four egg-shaped toes in an arc.
PAW = ('<symbol id="paw" viewBox="-20 -20 40 40"><path filter="url(#rough)" d="M0 0.6 C2.6 0.6 5.2 3.4 8.4 7.6 C11.4 11.4 11.6 15.6 8.2 16.8 C5.6 17.7 3.2 15.9 0 15.9 C-3.2 15.9 -5.6 17.7 -8.2 16.8 C-11.6 15.6 -11.4 11.4 -8.4 7.6 C-5.2 3.4 -2.6 0.6 0 0.6Z M-9.53 -5.00 L-9.06 -3.69 L-8.79 -2.34 L-8.70 -1.07 L-8.77 0.01 L-9.02 0.85 L-9.46 1.42 L-10.12 1.71 L-10.99 1.75 L-12.06 1.56 L-13.27 1.16 L-14.51 0.57 L-15.67 -0.20 L-16.38 -1.32 L-16.83 -2.53 L-16.99 -3.74 L-16.86 -4.88 L-16.43 -5.86 L-15.74 -6.62 L-14.84 -7.10 L-13.78 -7.28 L-12.65 -7.14 L-11.51 -6.69 L-10.44 -5.96Z M-0.89 -11.27 L-1.06 -9.76 L-1.43 -8.30 L-1.93 -7.00 L-2.51 -5.97 L-3.14 -5.27 L-3.84 -4.92 L-4.61 -4.95 L-5.48 -5.34 L-6.42 -6.05 L-7.41 -7.03 L-8.34 -8.21 L-9.11 -9.53 L-9.27 -10.97 L-9.14 -12.38 L-8.73 -13.66 L-8.06 -14.71 L-7.19 -15.46 L-6.16 -15.88 L-5.06 -15.92 L-3.95 -15.58 L-2.92 -14.89 L-2.02 -13.90 L-1.33 -12.66Z M9.11 -9.53 L8.34 -8.21 L7.41 -7.03 L6.42 -6.05 L5.48 -5.34 L4.61 -4.95 L3.84 -4.92 L3.14 -5.27 L2.51 -5.97 L1.93 -7.00 L1.43 -8.30 L1.06 -9.76 L0.89 -11.27 L1.33 -12.66 L2.02 -13.90 L2.92 -14.89 L3.95 -15.58 L5.06 -15.92 L6.16 -15.88 L7.19 -15.46 L8.06 -14.71 L8.73 -13.66 L9.14 -12.38 L9.27 -10.97Z M15.67 -0.20 L14.51 0.57 L13.27 1.16 L12.06 1.56 L10.99 1.75 L10.12 1.71 L9.46 1.42 L9.02 0.85 L8.77 0.01 L8.70 -1.07 L8.79 -2.34 L9.06 -3.69 L9.53 -5.00 L10.44 -5.96 L11.51 -6.69 L12.65 -7.14 L13.78 -7.28 L14.84 -7.10 L15.74 -6.62 L16.43 -5.86 L16.86 -4.88 L16.99 -3.74 L16.83 -2.53 L16.38 -1.32Z"/></symbol>')

ROUGH = ('<filter id="rough" x="-10%" y="-10%" width="120%" height="120%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
         '<feDisplacementMap in="SourceGraphic" scale="1.1"/></filter>')

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
            f'role="img" aria-label="{escape(label)}"><defs>{ROUGH}{PAW}{WOLF}{defs}</defs>'
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
    BAND = 110
    import base64
    av = base64.b64encode((Path(__file__).resolve().parent / "avatar.jpg").read_bytes()).decode()
    rnd = random.Random(7)
    v1d, v1 = veil("v1", 380, 20, 900, 200, [SAGE, TEAL, LAVENDER], 30, .38, "veil")
    v2d, v2 = veil("v2", 300, 80, 700, 120, [LAVENDER, ROSE], 34, .2, "veil2")
    defs = f'''{v1d}{v2d}
<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="moon"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset=".55" stop-color="{LAVENDER}" stop-opacity=".16"/><stop offset="1" stop-color="{LAVENDER}" stop-opacity="0"/></radialGradient>
<linearGradient id="bW" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".3" stop-color="#fff"/><stop offset=".7" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<linearGradient id="bB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="#000"/><stop offset=".7" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="mImg" maskUnits="userSpaceOnUse" x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}"><rect x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}" fill="#fff"/><rect class="band" x="{CX - R}" y="{CY - R - BAND}" width="{2 * R}" height="{BAND}" fill="url(#bB)"/></mask>
<mask id="mAsc" maskUnits="userSpaceOnUse" x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}"><rect class="band" x="{CX - R}" y="{CY - R - BAND}" width="{2 * R}" height="{BAND}" fill="url(#bW)"/></mask>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{NIGHT0}"/><stop offset=".45" stop-color="{NIGHT1}"/>
<stop offset=".72" stop-color="{NIGHT2}"/><stop offset="1" stop-color="{DUSK}"/></linearGradient>
<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SNOW_HI}"/><stop offset="1" stop-color="{SNOW_LO}"/></linearGradient>
<linearGradient id="snow2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9b5cd"/><stop offset="1" stop-color="#8794b2"/></linearGradient>'''
    css = f'''
.ascii{{animation:breathe 7s ease-in-out infinite}}@keyframes breathe{{0%,100%{{opacity:.95}}50%{{opacity:.78}}}}
.band{{animation:band 12s ease-in-out infinite}}@keyframes band{{0%,15%{{transform:translateY(0)}}70%,100%{{transform:translateY({2 * R + BAND}px)}}}}
.orbit{{transform-origin:{CX}px {CY}px;animation:orbit 60s linear infinite}}@keyframes orbit{{to{{transform:rotate(360deg)}}}}
@media (prefers-reduced-motion:reduce){{.ascii,.band,.orbit{{animation:none}}}}'''
    f = bezier((30, 530), (380, 420), (700, 400), (905, 366))
    tracks = trail(f, 22, lambda l: 30 - 24 * l, SNOW_SH, .9, t0=.1, ease=1.6,
                   stride=lambda l: 13 - 10 * l, fade=lambda l: 1 - .45 * l)
    cols = [(str(stats["projects"]), "projects"), (str(stats["contributions"]), "contributions this year"),
            (f"{stats['downloads']:,}", "downloads"), (str(stats["since"]), "on github since")]
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
<g clip-path="url(#moon)">
<image mask="url(#mImg)" x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}" href="data:image/jpeg;base64,{av}"/>
<circle cx="{CX}" cy="{CY}" r="{R}" fill="{NIGHT1}" opacity=".16" mask="url(#mImg)"/>
<g mask="url(#mAsc)"><rect x="{CX - R}" y="{CY - R}" width="{2 * R}" height="{2 * R}" fill="{NIGHT0}"/>{portrait(CX, CY, R)}</g>
</g>
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


# ── trail map: every path is a language, every stop a project ────────
TRAIL_COLORS = {"TypeScript": "#7f9be0", "JavaScript": "#d4b45c", "Python": "#6fb89c",
                "Rust": "#d0977a", "Go": "#6cb8c8", "Shell": "#9fb07a", "CSS": "#b08ad8", "HTML": "#d98b8b"}
FALLBACK_COLORS = ["#a08ad6", "#d08aa8", "#5fb3b3", "#c9a26b"]


def trailmap(repos):
    groups = {}
    for r in repos:
        groups.setdefault(r["language"] or "Other", []).append(r)
    langs = sorted(groups, key=lambda l: (-len(groups[l]), l))
    n = len(langs)
    W = 1200
    gap = 96
    top = 70
    H = top + (n - 1) * gap + 110
    DX, DY = 1080, top + (n - 1) * gap / 2 + 8        # the den
    paths, stops, labels, walkers = [], [], [], []
    for i, lang in enumerate(langs):
        color = TRAIL_COLORS.get(lang) or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        y = top + i * gap
        ey = DY + (i - (n - 1) / 2) * 9
        bend = DX - 70 - abs(y - ey)
        d = f"M190 {y} H{bend:.0f} L{DX - 70} {ey:.0f} H{DX - 34}"
        pid = f"t{i}"
        paths.append(f'<path id="{pid}" class="draw" style="animation-delay:{i * .25:.2f}s" d="{d}" pathLength="1" '
                     f'fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        labels.append(f'<rect x="20" y="{y - 15}" width="150" height="30" rx="15" fill="{color}" fill-opacity=".16" stroke="{color}" stroke-opacity=".55"/>'
                      f'<circle cx="40" cy="{y}" r="5" fill="{color}"/>'
                      f'<text x="54" y="{y + 5}" class="sans" font-size="13" font-weight="600" letter-spacing="1.5" fill="{SLATE}">{escape(lang.upper())}</text>')
        items = groups[lang]
        span = bend - 280
        for k, r in enumerate(items):
            sx = 280 + span * (k + .5) / len(items)
            above = k % 2 == 0
            name = r["name"] if len(r["name"]) <= 30 else r["name"][:29] + "…"
            stops.append(f'<circle class="pop" style="animation-delay:{.6 + i * .25 + k * .15:.2f}s;transform-origin:{sx:.0f}px {y}px" '
                         f'cx="{sx:.0f}" cy="{y}" r="9" fill="#f4f6fb" stroke="{color}" stroke-width="4"/>'
                         f'<text x="{sx:.0f}" y="{y - 20 if above else y + 32}" text-anchor="middle" class="sans" font-size="15" fill="{SLATE}">{escape(name)}</text>')
        walkers.append(f'<circle r="4.5" fill="#f4f6fb" stroke="{color}" stroke-width="2" opacity=".95">'
                       f'<animateMotion dur="{9 + i * 2}s" begin="{2 + i}s" repeatCount="indefinite" rotate="auto"><mpath href="#{pid}"/></animateMotion></circle>')
    import base64
    av = base64.b64encode((Path(__file__).resolve().parent / "avatar.jpg").read_bytes()).decode()
    defs = f'<clipPath id="den"><circle cx="{DX}" cy="{DY}" r="34"/></clipPath>'
    css = '''
.draw{animation:draw 1.6s ease-out backwards}@keyframes draw{from{stroke-dasharray:1;stroke-dashoffset:1}to{stroke-dasharray:1;stroke-dashoffset:0}}
.pop{animation:pop .5s ease-out backwards}@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}
.ring{animation:ring 3.2s ease-out infinite;transform-origin:%dpx %dpx}@keyframes ring{0%%{opacity:.6;transform:scale(1)}100%%{opacity:0;transform:scale(1.7)}}
@media (prefers-reduced-motion:reduce){.draw,.pop,.ring{animation:none}}''' % (DX, DY)
    body = f'''{"".join(paths)}
<circle class="ring" cx="{DX}" cy="{DY}" r="40" fill="none" stroke="{SLATE}" stroke-width="1.5"/>
<circle cx="{DX}" cy="{DY}" r="40" fill="#f4f6fb" stroke="{SLATE}" stroke-opacity=".6" stroke-width="2"/>
<image clip-path="url(#den)" x="{DX - 34}" y="{DY - 34}" width="68" height="68" href="data:image/jpeg;base64,{av}"/>
<text x="{DX}" y="{DY + 66}" text-anchor="middle" class="serif" font-size="17" font-style="italic" fill="{SLATE}">the den</text>
{"".join(labels)}
{"".join(stops)}
{"".join(walkers)}
<text x="20" y="{H - 14}" class="serif" font-size="16" font-style="italic" fill="{SLATE}">every path is a language, every stop a project.</text>'''
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


# ── field notes: a few numbers from the walk ───────────────────────
def fieldnotes(notes):
    W, H = 1200, 150
    cols = len(notes)
    colw = W / cols
    items = []
    for i, (num, label, sub) in enumerate(notes):
        x = i * colw + 6
        items.append(f'<text x="{x:.0f}" y="84" class="serif" font-size="42" fill="{SLATE}">{escape(num)}</text>'
                     f'<text x="{x + 2:.0f}" y="108" class="sans" font-size="12" letter-spacing="2.2" fill="{SLATE}">{escape(label.upper())}</text>'
                     f'<text x="{x + 2:.0f}" y="130" class="serif" font-size="15" font-style="italic" fill="{SLATE}" opacity=".75">{escape(sub)}</text>')
        if i:
            items.append(f'<line x1="{i * colw - 22:.0f}" x2="{i * colw - 22:.0f}" y1="50" y2="128" stroke="{SLATE}" stroke-opacity=".25"/>')
    body = f'''<text x="6" y="22" class="sans" font-size="12" letter-spacing="3" fill="{SLATE}">FIELD NOTES</text>
<line x1="120" x2="{W - 6}" y1="18" y2="18" stroke="{SLATE}" stroke-opacity=".25" stroke-dasharray="2 6"/>
{"".join(items)}'''
    write("fieldnotes.svg", svg(W, H, body, "", "", "Field notes: " + ", ".join(f"{n} {l}" for n, l, _ in notes)))


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
    import datetime as dt
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from github_data import contributions, profile, release_stats, repos

    user = sys.argv[1] if len(sys.argv) > 1 else "ragnaykja"
    rs = repos(user)
    days = contributions(user)
    rel = release_stats(user, rs)
    total_dl = sum(d for _, d in rel.values())
    stats = {
        "projects": len(rs),
        "contributions": sum(n for _, _, n in days),
        "downloads": total_dl,
        "since": profile(user)["created_at"][:4],
    }

    # field notes
    active = [d for d, lv, n in days if n]
    streak = best = 0
    prev = None
    for d in active:
        streak = streak + 1 if prev and (d - prev).days == 1 else 1
        best, prev = max(best, streak), d
    today = days[-1][0]
    if active:
        ago = (today - active[-1]).days
        last = "today" if ago == 0 else "yesterday" if ago == 1 else f"{ago} days ago"
    else:
        last = "not yet"
    top = max(rel.items(), key=lambda kv: kv[1][1]) if rel else None
    star_count = sum(r["stargazers_count"] for r in rs)
    notes = [
        (str(sum(c for c, _ in rel.values())), "releases shipped", f"across {sum(1 for c, _ in rel.values() if c)} projects"),
        (f"{top[1][1]:,}" if top else "0", "most downloaded", top[0] if top else "—"),
        (str(len(active)), "days on the trail", "in the last year"),
        (f"{best}", "longest streak", "day in a row" if best == 1 else "days in a row"),
        (last.split()[0] if last[0].isdigit() else last, "last tracks",
         " ".join(last.split()[1:]) + " · fresh snow" if last[0].isdigit() else "fresh snow"),
    ]
    if star_count:
        notes.insert(1, (str(star_count), "stars", "thank you"))
    print("building assets →", OUT, stats)
    hero(stats)
    chapter("I", "the den", "who I am", 1)
    chapter("II", "the trail", "things I've built", 2)
    chapter("III", "tracks in the snow", "a year of commits", 3)
    trailmap(rs)
    fieldnotes(notes)
    footer()
