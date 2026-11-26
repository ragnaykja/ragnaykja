#!/usr/bin/env python3
"""Generates the aurora-themed SVG assets for the profile README.

Run from the repo root:  python3 tools/build_assets.py
"""
import base64
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ── palette ───────────────────────────────────────────────────────────
BG0, BG1, BG2 = "#050816", "#0a1128", "#0f1d3a"
INK, MUTED, DIM = "#eef2ff", "#a5b4d4", "#6b7a9c"
MINT, TEAL, CYAN, VIOLET, PINK = "#7dfcc6", "#2dd4bf", "#22d3ee", "#8b5cf6", "#ec4899"

FONT = ('text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif}'
        '.mono{font-family:ui-monospace,SFMono-Regular,"JetBrains Mono",Menlo,Consolas,monospace}')

AURORA_GRAD = f'''<linearGradient id="ag" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{MINT}"/><stop offset=".35" stop-color="{TEAL}"/>
<stop offset=".7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>'''

GLOW = '''<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
<feGaussianBlur stdDeviation="5" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''

PAW = ('<symbol id="paw" viewBox="-16 -18 32 32"><ellipse cx="0" cy="5" rx="9" ry="7.5"/>'
       '<ellipse cx="-10" cy="-4" rx="3.6" ry="4.6" transform="rotate(-20 -10 -4)"/>'
       '<ellipse cx="-3.8" cy="-11" rx="3.6" ry="4.8"/><ellipse cx="3.8" cy="-11" rx="3.6" ry="4.8"/>'
       '<ellipse cx="10" cy="-4" rx="3.6" ry="4.6" transform="rotate(20 10 -4)"/></symbol>')

# Howling wolf silhouette, sitting, facing left. Local box ~ 0..100 x 0..100.
WOLF = ('<symbol id="wolf" viewBox="0 0 100 100"><path d="'
        'M3 9 Q12 7 20 10 L24 9 L26 0 L30 7 L34 1 L36 11 Q41 16 45 24 '
        'Q48 31 53 38 Q60 50 68 57 Q83 63 83 82 Q89 89 98 82 Q100 97 86 100 '
        'L36 100 Q31 99 35 96 Q37 84 34 70 Q31 56 27 44 Q24 38 21 33 Q18 28 15 23 '
        'L12 19 Q7 17 2 15 Q6 13 9 12 Z"/></symbol>')

KEYFRAMES = '''
.s{fill:#e8f0ff;animation:tw 3s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.95}50%{opacity:.25}}
.a1{animation:d1 16s ease-in-out infinite}.a2{animation:d2 20s ease-in-out infinite}.a3{animation:d1 24s ease-in-out infinite reverse}
@keyframes d1{0%,100%{transform:translateX(0) skewX(0)}50%{transform:translateX(-80px) skewX(-8deg)}}
@keyframes d2{0%,100%{transform:translateX(0)}50%{transform:translateX(90px)}}
.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
'''

random.seed(42)


def stars(n, w, h, avoid=None):
    out = []
    for _ in range(n):
        x, y = random.uniform(4, w - 4), random.uniform(4, h - 4)
        if avoid and avoid(x, y):
            continue
        r = random.choice([.6, .8, 1, 1.2, 1.6])
        out.append(f'<circle class="s" cx="{x:.0f}" cy="{y:.0f}" r="{r}" '
                   f'style="animation-delay:{random.uniform(0, 4):.2f}s;animation-duration:{random.uniform(2.5, 5.5):.2f}s"/>')
    return "".join(out)


def aurora_bands(w, h, y0, blur=22, opacity=1.0):
    s = w / 1200
    def P(d):  # scale x coordinates of a simple path template
        return d
    return f'''<defs>
<linearGradient id="b1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset=".55" stop-color="{MINT}" stop-opacity=".55"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>
<linearGradient id="b2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".5" stop-color="{VIOLET}" stop-opacity=".55"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
<linearGradient id="b3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".6" stop-color="{CYAN}" stop-opacity=".4"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="{blur}"/></filter></defs>
<g filter="url(#blur)" opacity="{opacity}" transform="translate(0 {y0}) scale({s} 1)">
<path class="a1" d="M-100 110 C150 0 330 170 560 70 S900 -30 1300 80 L1300 170 C950 60 800 220 560 150 S150 90 -100 200Z" fill="url(#b1)"/>
<path class="a2" d="M-100 50 C200 -30 420 120 700 30 S1050 0 1300 20 L1300 100 C1050 80 900 130 700 100 S220 30 -100 130Z" fill="url(#b2)"/>
<path class="a3" d="M200 160 C400 80 600 220 850 130 S1100 80 1300 140 L1300 220 C1100 160 950 260 820 210 S450 170 200 240Z" fill="url(#b3)"/>
</g>'''


def ridge(w, base, amp, step, color, opacity=1.0, seed=0):
    rnd = random.Random(seed)
    pts, x = [f"0,{base}"], 0
    while x < w:
        x += step * rnd.uniform(.6, 1.3)
        pts.append(f"{min(x, w):.0f},{base - rnd.uniform(0, amp):.0f}")
    return f'<polygon points="0,{base + 400} {" ".join(pts)} {w},{base + 400}" fill="{color}" opacity="{opacity}"/>'


def svg(w, h, body, defs="", style="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><defs>{defs}</defs><style>{FONT}{KEYFRAMES}{style}</style>{body}</svg>')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name:<22} {len(content.encode()) / 1024:6.1f} KB")


# ── hero ──────────────────────────────────────────────────────────────
def hero():
    W, H = 1200, 440
    av = base64.b64encode((OUT / "avatar.jpg").read_bytes()).decode()
    paws = "".join(
        f'<use href="#paw" class="p" style="animation-delay:{i * .32:.2f}s" x="{x - 9}" y="{y - 9}" width="18" height="18" transform="rotate(90 {x} {y})"/>'
        for i, (x, y) in enumerate((392 + i * 46, 398 + (-7 if i % 2 else 7)) for i in range(9)))
    defs = f'''{AURORA_GRAD}{GLOW}{PAW}{WOLF}
<clipPath id="frame"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="avc"><circle cx="200" cy="205" r="112"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset=".65" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<radialGradient id="moon" cx=".5" cy=".5" r=".5"><stop offset=".55" stop-color="#f8fafc"/><stop offset=".7" stop-color="#dbeafe" stop-opacity=".5"/><stop offset="1" stop-color="#dbeafe" stop-opacity="0"/></radialGradient>
<linearGradient id="pill" x1="0" x2="1"><stop offset="0" stop-color="{MINT}" stop-opacity=".16"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".16"/></linearGradient>'''
    style = f'''
.p{{fill:{MINT};opacity:.2;animation:step 4s ease-in-out infinite}}
@keyframes step{{0%{{opacity:.12}}10%,50%{{opacity:.9}}85%,100%{{opacity:.12}}}}
.ring{{transform-origin:200px 205px;animation:spin 10s linear infinite}}@keyframes spin{{to{{transform:rotate(360deg)}}}}
.dot{{animation:pulse 2s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.howl{{transform-origin:1010px 300px;animation:howl 7s ease-in-out infinite}}
@keyframes howl{{0%,60%,100%{{transform:rotate(0)}}70%,85%{{transform:rotate(-3deg)}}}}
.wave{{fill:none;stroke:{MINT};stroke-width:2;opacity:0;animation:wave 7s ease-out infinite}}
@keyframes wave{{0%,68%{{opacity:0;transform:scale(.6)}}75%{{opacity:.7}}95%,100%{{opacity:0;transform:scale(1.4)}}}}'''
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g>{stars(170, W, 300)}</g>
{aurora_bands(W, H, 10)}
<circle cx="1080" cy="80" r="58" fill="url(#moon)"/>
<g transform="translate(1080 80)"><circle class="wave" r="70" style="transform-origin:0 0"/></g>
{ridge(W, 360, 50, 70, "#0b1633", 1, 3)}
{ridge(W, 400, 34, 55, "#060b1d", 1, 9)}
<g class="howl"><use href="#wolf" x="958" y="236" width="118" height="118" fill="#040816" stroke="{MINT}" stroke-opacity=".45" stroke-width="1"/></g>
<path d="M944 440 L950 384 Q958 360 990 357 L1045 355 Q1076 357 1086 382 L1094 440Z" fill="#040816" stroke="{MINT}" stroke-opacity=".25"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="url(#ag)" stroke-opacity=".45"/>
<circle class="ring" cx="200" cy="205" r="122" fill="none" stroke="url(#ag)" stroke-width="6" stroke-dasharray="560 60 40 60" stroke-linecap="round" filter="url(#glow)"/>
<circle cx="200" cy="205" r="115" fill="{BG1}"/>
<image clip-path="url(#avc)" x="88" y="93" width="224" height="224" href="data:image/jpeg;base64,{av}"/>
<rect x="378" y="96" width="318" height="34" rx="17" fill="url(#pill)" stroke="{MINT}" stroke-opacity=".35"/>
<circle class="dot" cx="398" cy="113" r="5" fill="{MINT}"/>
<text x="412" y="119" font-size="15" fill="{INK}" class="mono">building Foundry VTT modules</text>
<text x="374" y="214" font-size="92" font-weight="800" letter-spacing="-3" fill="url(#ag)" filter="url(#glow)">Ragna</text>
<text x="378" y="262" font-size="26" font-weight="600" fill="{INK}">Developer · GIS · Automation</text>
<text x="378" y="300" font-size="18" fill="{MUTED}">Turning repetitive workflows into software —</text>
<text x="378" y="326" font-size="18" fill="{MUTED}">one script, one plugin, one map layer at a time.</text>
'''
    write("hero.svg", svg(W, H, body, defs, style, "Ragna – Developer, GIS, Automation"))


# ── section title ─────────────────────────────────────────────────────
def section(num, title, sub):
    W, H = 1200, 70
    body = f'''<text x="2" y="44" font-size="15" class="mono" fill="{MINT}">{num}</text>
<text x="40" y="46" font-size="30" font-weight="700" fill="url(#ag)">{escape(title)}</text>
<text x="{56 + len(title) * 19:.0f}" y="45" font-size="15" class="mono" fill="{DIM}">{escape(sub)}</text>
<rect x="2" y="62" width="1196" height="2" rx="1" fill="url(#fade)"/>'''
    defs = AURORA_GRAD + f'''<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{MINT}" stop-opacity=".8"/>
<stop offset=".5" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>'''
    write(f"section-{num}.svg", svg(W, H, body, defs, "", f"{num} {title}"))


# ── terminal / about ──────────────────────────────────────────────────
def terminal():
    W = 1200
    lines = [
        ("cmd", "whoami"),
        ("out", [(INK, "Ragna"), (MUTED, " — developer from Germany, lone wolf in the terminal, pack animal in open source")]),
        ("cmd", "cat focus.txt"),
        ("out", [(MINT, "automation"), (DIM, "  ·  "), (CYAN, "spatial data & GIS"), (DIM, "  ·  "),
                 (VIOLET, "self-hosting"), (DIM, "  ·  "), (PINK, "tabletop tooling")]),
        ("cmd", "cat stack.txt"),
        ("out", [(INK, "TypeScript · React · Node.js · PostgreSQL/PostGIS · QGIS · Docker · Linux")]),
        ("cmd", "echo $MOTTO"),
        ("out", [(MUTED, "\"If I have to do it twice, I'm going to automate it.\"")]),
    ]
    top, lh = 92, 34
    H = top + lh * (len(lines) + 1) + 10
    rows = []
    for i, (kind, val) in enumerate(lines):
        y = top + i * lh
        d = f"animation-delay:{.25 + i * .35:.2f}s"
        if kind == "cmd":
            rows.append(f'<g class="ln" style="{d}"><text x="44" y="{y}" font-size="19" class="mono">'
                        f'<tspan fill="{MINT}">ragna</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{CYAN}">den</tspan>'
                        f'<tspan fill="{DIM}">:~$ </tspan><tspan fill="{INK}">{escape(val)}</tspan></text></g>')
        else:
            spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for c, t in val)
            rows.append(f'<g class="ln" style="{d}"><text x="44" y="{y}" font-size="19" class="mono">'
                        f'<tspan fill="{DIM}">› </tspan>{spans}</text></g>')
    y = top + len(lines) * lh
    rows.append(f'<text x="44" y="{y}" font-size="19" class="mono"><tspan fill="{MINT}">ragna</tspan><tspan fill="{DIM}">@</tspan>'
                f'<tspan fill="{CYAN}">den</tspan><tspan fill="{DIM}">:~$ </tspan><tspan class="cur" fill="{MINT}">▋</tspan></text>')
    defs = AURORA_GRAD + f'''<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
<radialGradient id="g1" cx=".9" cy="0" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx=".05" cy="1" r=".6"><stop offset="0" stop-color="{MINT}" stop-opacity=".14"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>'''
    style = '.ln{animation:in .5s ease-out backwards}@media (prefers-reduced-motion:reduce){.ln{animation:none}}@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}'
    body = f'''<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#card)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#g1)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#g2)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="url(#ag)" stroke-opacity=".5" stroke-width="1.5"/>
<line x1="1" y1="48" x2="{W - 1}" y2="48" stroke="#ffffff" stroke-opacity=".07"/>
<circle cx="30" cy="25" r="7" fill="#ff5f57"/><circle cx="54" cy="25" r="7" fill="#febc2e"/><circle cx="78" cy="25" r="7" fill="#28c840"/>
<text x="{W / 2}" y="31" text-anchor="middle" font-size="15" class="mono" fill="{DIM}">ragna@den — zsh</text>
{"".join(rows)}'''
    write("about.svg", svg(W, H, body, defs, style, "About Ragna"))


# ── project cards ─────────────────────────────────────────────────────
ICONS = {
    "sync": f'<g fill="none" stroke="url(#ag)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M-14 -4 A15 15 0 0 1 12 -10"/><path d="M12 -18 L12 -10 L4 -10"/>'
            f'<path d="M14 4 A15 15 0 0 1 -12 10"/><path d="M-12 18 L-12 10 L-4 10"/></g>',
    "sword": f'<g fill="none" stroke="url(#ag)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M-15 -15 L8 8 L12 4 L-11 -19 Z"/><path d="M4 14 L14 4"/><path d="M10 10 L17 17"/>'
             f'<path d="M15 -15 L-8 8"/><path d="M-4 14 L-14 4"/><path d="M-10 10 L-17 17"/></g>',
    "eye": f'<g fill="none" stroke="url(#ag)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
           f'<path d="M-18 0 Q0 -18 18 0 Q0 18 -18 0Z"/><circle r="5"/><path d="M-16 16 L16 -16"/></g>',
    "cloud": f'<g fill="none" stroke="url(#ag)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M-12 6 A8 8 0 0 1 -10 -9 A11 11 0 0 1 10 -10 A8 8 0 0 1 12 6 Z"/>'
             f'<path d="M-6 12 L-8 18"/><path d="M1 12 L-1 18"/><path d="M8 12 L6 18"/></g>',
}
LANG = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a"}


def card(slug, title, desc_lines, lang, icon, tag):
    W, H = 590, 210
    desc = "".join(f'<text x="34" y="{122 + i * 26}" font-size="17" fill="{MUTED}">{escape(l)}</text>'
                   for i, l in enumerate(desc_lines))
    defs = AURORA_GRAD + f'''<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
<radialGradient id="gl" cx="1" cy="0" r=".9"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<linearGradient id="ib" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{MINT}" stop-opacity=".14"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".14"/></linearGradient>'''
    style = '.sh{animation:sh 6s ease-in-out infinite}@keyframes sh{0%,100%{stroke-opacity:.35}50%{stroke-opacity:.8}}'
    body = f'''<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#card)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#gl)"/>
<rect class="sh" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="url(#ag)" stroke-width="1.5"/>
<rect x="30" y="28" width="56" height="56" rx="16" fill="url(#ib)" stroke="#ffffff" stroke-opacity=".08"/>
<g transform="translate(58 56)">{ICONS[icon]}</g>
<text x="104" y="54" font-size="26" font-weight="700" fill="{INK}">{escape(title)}</text>
<text x="105" y="78" font-size="14" class="mono" fill="{MINT}">{escape(tag)}</text>
<text x="{W - 34}" y="54" text-anchor="end" font-size="22" fill="{DIM}">↗</text>
{desc}
<circle cx="40" cy="{H - 30}" r="6" fill="{LANG[lang]}"/>
<text x="54" y="{H - 25}" font-size="14" fill="{DIM}">{lang}</text>
<text x="{W - 34}" y="{H - 25}" text-anchor="end" font-size="14" class="mono" fill="{DIM}">ragnaykja/{escape(slug)}</text>'''
    write(f"card-{slug}.svg", svg(W, H, body, defs, style, title))


# ── footer ────────────────────────────────────────────────────────────
def footer():
    W, H = 1200, 230
    defs = f'''{AURORA_GRAD}{GLOW}{WOLF}<clipPath id="frame"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>'''
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g>{stars(80, W, 160)}</g>
{aurora_bands(W, H, -40, 18, .9)}
{ridge(W, 200, 30, 60, "#0b1633", 1, 21)}
{ridge(W, 220, 18, 45, "#060b1d", 1, 5)}
<use href="#wolf" x="562" y="134" width="74" height="74" fill="#040816" stroke="{MINT}" stroke-opacity=".45" stroke-width="1.2"/>
<path d="M545 212 Q600 190 660 212 L660 230 L540 230Z" fill="#040816"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="url(#ag)" stroke-opacity=".45"/>
<text x="{W / 2}" y="58" text-anchor="middle" font-size="24" font-weight="700" fill="{INK}">Build things. Break things. Learn why they broke.</text>
<text x="{W / 2}" y="88" text-anchor="middle" font-size="15" class="mono" fill="{MUTED}">thanks for wandering into the den  ·  see you around the campfire</text>'''
    write("footer.svg", svg(W, H, body, defs, "", "Build things. Break things. Learn why they broke."))


if __name__ == "__main__":
    print("building assets →", OUT)
    hero()
    section("01", "whoami", "// a little about me")
    section("02", "projects", "// things I've built")
    section("03", "toolbox", "// what I hunt with")
    section("04", "activity", "// tracks in the snow")
    terminal()
    card("propsync", "PropSync", ["Obsidian plugin that syncs properties across", "notes by group — without overwriting anything."],
         "TypeScript", "sync", "obsidian plugin")
    card("foundry-better-combat-cards", "Better Combat Cards", ["Cleaner, prettier and more readable combat", "chat cards for Foundry VTT."],
         "JavaScript", "sword", "foundry vtt module")
    card("foundry-hide-groupbars", "Hide Group Bars", ["A tiny Foundry VTT module with exactly one job:", "hide the stuff you don't need."],
         "JavaScript", "eye", "foundry vtt module")
    card("foundry-esay-weather", "Easy Weather", ["Weather tooling for Foundry VTT — because even", "imaginary worlds need a forecast."],
         "JavaScript", "cloud", "foundry vtt module")
    footer()
