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

PAW = ('<symbol id="paw" viewBox="-16 -18 32 32"><ellipse cx="0" cy="5" rx="8.5" ry="7"/>'
       '<ellipse cx="-10" cy="-4" rx="3.4" ry="4.4" transform="rotate(-20 -10 -4)"/>'
       '<ellipse cx="-3.8" cy="-11" rx="3.4" ry="4.6"/><ellipse cx="3.8" cy="-11" rx="3.4" ry="4.6"/>'
       '<ellipse cx="10" cy="-4" rx="3.4" ry="4.4" transform="rotate(20 10 -4)"/></symbol>')

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


# ── hero: dusk, the trail begins ──────────────────────────────────────
def hero():
    W, H = 1200, 420
    rnd = random.Random(7)
    v1d, v1 = veil("v1", 480, 20, 800, 190, [SAGE, TEAL, LAVENDER], 28, .45, "veil")
    v2d, v2 = veil("v2", 380, 70, 700, 120, [LAVENDER, ROSE], 34, .24, "veil2")
    defs = f'''{v1d}{v2d}
<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{NIGHT0}"/><stop offset=".45" stop-color="{NIGHT1}"/>
<stop offset=".72" stop-color="{NIGHT2}"/><stop offset="1" stop-color="{DUSK}"/></linearGradient>
<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SNOW_HI}"/><stop offset="1" stop-color="{SNOW_LO}"/></linearGradient>
<linearGradient id="snow2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9b5cd"/><stop offset="1" stop-color="#8794b2"/></linearGradient>'''
    f = bezier((40, 470), (420, 360), (760, 345), (960, 312))
    tracks = trail(f, 22, lambda l: 30 - 24 * l, SNOW_SH, .9, t0=.08, ease=1.6,
                   stride=lambda l: 13 - 10 * l, fade=lambda l: 1 - .45 * l)
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(rnd, 70, 0, W, 0, 250)}
<circle cx="1085" cy="74" r="17" fill="#eef1f7" opacity=".9"/><circle cx="1093" cy="68" r="15" fill="{NIGHT0}"/>
{v2}{v1}
<path d="M0 300 C140 268 260 292 400 278 S700 250 860 272 S1080 262 1200 280 L1200 420 L0 420Z" fill="{HILL_FAR}" opacity=".75"/>
<path d="M0 330 C180 300 340 326 520 312 S840 292 1000 308 S1140 300 1200 306 L1200 420 L0 420Z" fill="url(#snow2)"/>
<path d="M0 360 C220 334 420 352 640 340 S1000 326 1200 338 L1200 420 L0 420Z" fill="url(#snow)"/>
{tracks}
</g>
<text x="72" y="140" class="serif" font-size="78" fill="{INK}" letter-spacing="-1">Ragna</text>
<text x="76" y="180" class="sans" font-size="14" fill="{MUTED}" letter-spacing="4.5">DEVELOPER  ·  GIS  ·  AUTOMATION</text>
<text x="76" y="226" class="serif" font-size="19" font-style="italic" fill="{MUTED}">quiet tools that do a loud amount of work.</text>'''
    write("hero.svg", svg(W, H, body, defs, "", "Ragna – developer, GIS, automation"))


# ── chapter dividers: the trail continues ─────────────────────────────
def chapter(num, title, sub, seed):
    W, H = 1200, 120
    rnd = random.Random(seed)
    a = rnd.uniform(-14, 14)
    f = bezier((420, 76 + a), (640, 36 - a), (880, 106 + a), (1180, 62 - a))
    tracks = trail(f, 12, 24, SLATE, .5, stride=10)
    body = f'''<text x="4" y="58" class="serif" font-size="17" font-style="italic" fill="{SLATE}">{escape(num)}</text>
<text x="4" y="92" class="serif" font-size="40" fill="{SLATE}">{escape(title)}</text>
<text x="6" y="114" class="sans" font-size="13" letter-spacing="2" fill="{SLATE}" opacity=".8">{escape(sub.upper())}</text>
{tracks}'''
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
    print("building assets →", OUT)
    hero()
    chapter("I", "the den", "who I am", 1)
    chapter("II", "the trail", "things I've built", 2)
    chapter("III", "tracks in the snow", "a year of commits", 3)
    footer()
