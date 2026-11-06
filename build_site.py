"""Builds the Spearheaded static site: src/pages/*.html bodies + shared partials -> dist/."""
import html
import json
import math
import re
import shutil
from pathlib import Path

import importlib.util

_spec = importlib.util.spec_from_file_location("film", str(Path(__file__).parent / "tools" / "film.py"))
film_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(film_mod)
FILM = film_mod.film("desktop", site=True) + "\n" + film_mod.film("phone", site=True)

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
SITE = "https://spearheaded.ca"

FONTS = (
    "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600"
    "&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400"
    "&family=Jost:wght@300;400;500&display=swap"
)

SEAL = (
    '<svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
    '<circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" stroke-width="1"></circle>'
    '<circle cx="32" cy="32" r="26" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.7"></circle>'
    '<polyline points="13,45 24,33 30,38 38,22 51,45" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"></polyline>'
    '<line x1="38" y1="22" x2="38" y2="14" stroke="currentColor" stroke-width="1"></line>'
    '<polygon points="38,7 40.6,13.5 38,16.5 35.4,13.5" fill="currentColor"></polygon></svg>'
)

# --- engraved mountain line art -------------------------------------------
CX = 330


def _h(x):
    p1 = max(0.0, 1 - abs(x - CX) / 270) ** 1.45
    p2 = 0.62 * max(0.0, 1 - abs(x - 140) / 190) ** 1.3
    p3 = 0.48 * max(0.0, 1 - abs(x - 505) / 165) ** 1.3
    base = max(p1, p2, p3)
    rug = 0.018 * math.sin(x / 6.5) + 0.012 * math.sin(x / 2.9 + 1.3)
    return max(0.0, base + rug * base)


def art_lines(animated):
    out = []
    for i in range(20):
        yb, amp = 360 + i * 18, 260 * (1 - i * 0.035)
        pts = " ".join(f"{x},{yb - amp * _h(x):.1f}" for x in range(0, 601, 5))
        op = round(max(0.12, 0.95 - i * 0.042), 2)
        extra = f' pathLength="1" style="animation-delay:{0.15 + i * 0.06:.2f}s"' if animated else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="currentColor" stroke-width="0.8" opacity="{op}"{extra}></polyline>')
    spear = (
        '<line x1="330" y1="95" x2="330" y2="44" stroke="currentColor" stroke-width="1"></line>'
        '<polygon points="330,2 337,28 330,44 323,28" fill="currentColor"></polygon>'
    )
    return "\n".join(out) + spear


ART = (
    '<svg class="art" viewBox="0 0 600 720" aria-hidden="true" focusable="false" style="overflow:visible">'
    '<circle cx="330" cy="250" r="214" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.22"></circle>'
    '<circle cx="330" cy="250" r="226" fill="none" stroke="currentColor" stroke-width="0.4" opacity="0.14"></circle>'
    + art_lines(True) + "</svg>"
)
ART_STATIC = '<svg class="bg-art" viewBox="0 0 600 720" aria-hidden="true" focusable="false">' + art_lines(False) + "</svg>"
GRAIN = (
    '<svg class="grain" aria-hidden="true" focusable="false"><filter id="grain"><feTurbulence type="fractalNoise" '
    'baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"></feTurbulence></filter>'
    '<rect width="100%" height="100%" filter="url(#grain)"></rect></svg>'
)

# --- partials ----------------------------------------------------------------
NAV = [("approach", "Approach", "index.html#approach"), ("practice", "Practice", "practice.html"), ("about", "The Firm", "about.html")]


def head(meta, prefix):
    title = meta["title"]
    desc = meta["description"]
    url = SITE + meta["path"]
    jsonld = ""
    if meta["path"] == "/":
        data = {
            "@context": "https://schema.org",
            "@type": "InsuranceAgency",
            "name": "Spearheaded",
            "url": SITE + "/",
            "description": desc,
            "areaServed": "Greater Toronto Area, Ontario, Canada",
            "founder": {"@type": "Person", "name": "Sajad Moshkelgosha"},
        }
        jsonld = f'<script type="application/ld+json">{json.dumps(data)}</script>\n'
    robots = '<meta name="robots" content="noindex">\n' if meta.get("noindex") else ""
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Spearheaded">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#0E0D0B">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS.replace('&', '&amp;')}">
<link rel="stylesheet" href="{prefix}assets/styles.css">
{jsonld}</head>
<body>
"""


def header(active, prefix):
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{prefix}{href}"{cur}>{label}</a>')
    mobile = "".join(f'<a href="{prefix}{href}">{label}</a>' for _, label, href in NAV)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
<a class="brand" href="{prefix}index.html" aria-label="Spearheaded, home">{SEAL}<span class="brand-word">SPEARHEADED</span></a>
<nav class="nav" aria-label="Primary">{''.join(links)}</nav>
<a class="btn btn-line header-cta" href="{prefix}consultation.html">Private consultation</a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu"><span class="menu-label">Menu</span><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="1.2"></line><line x1="3" y1="15" x2="21" y2="15" stroke="currentColor" stroke-width="1.2"></line></svg></button>
<div class="mobile-menu" id="mobile-menu">{mobile}<a class="btn btn-gold" href="{prefix}consultation.html">Request a private consultation</a></div>
</header>
"""


def footer(prefix):
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">
<div class="footer-col">
<a class="brand" href="{prefix}index.html" aria-label="Spearheaded, home">{SEAL}<span class="brand-word">SPEARHEADED</span></a>
<p>Private client planning<br>Greater Toronto Area</p>
</div>
<nav class="footer-col" aria-label="Practice">
<span class="footer-head">PRACTICE</span>
<a href="{prefix}practice.html#estate">Estate preservation</a>
<a href="{prefix}practice.html#corporate">Corporate wealth strategies</a>
<a href="{prefix}practice.html#protection">Income &amp; enterprise protection</a>
<a href="{prefix}practice.html#retirement">Retirement income design</a>
</nav>
<nav class="footer-col" aria-label="The firm">
<span class="footer-head">THE FIRM</span>
<a href="{prefix}index.html#approach">Approach</a>
<a href="{prefix}about.html">Founder</a>
<a href="{prefix}consultation.html">Private consultation</a>
</nav>
<div class="footer-col">
<span class="footer-head">CONTACT</span>
<span>By appointment only</span>
<span>[PHONE]</span>
<span>[EMAIL]</span>
</div>
</div>
<div class="footer-legal">
<p>[REGULATORY DISCLOSURE — licensing and agency wording to be confirmed with WFGIA compliance before launch.]</p>
<p>The information on this website is general in nature and is not tax, legal or investment advice. Any strategy depends on your circumstances and should be reviewed with your accountant and lawyer.</p>
<div class="row"><span>© <span data-year>2026</span> Spearheaded. All rights reserved.</span><div class="links"><a href="{prefix}privacy.html">Privacy</a></div></div>
</div>
</div>
</footer>
<script src="{prefix}assets/site.js" defer></script>
</body>
</html>
"""


def parse(page):
    text = page.read_text()
    m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    meta["noindex"] = meta.get("noindex") == "true"
    return meta, text[m.end():]


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    with open(DIST / "assets" / "styles.css", "a") as css:
        css.write("\n/* Hero film (generated) */\n" + film_mod.FILM_CSS.strip() + "\n")
    for f in (SRC / "static").iterdir():
        shutil.copy(f, DIST / f.name)
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(page)
        prefix = "/" if page.stem == "404" else ""
        body = body.replace("@@ART@@", ART).replace("@@ART_STATIC@@", ART_STATIC).replace("@@SEAL@@", SEAL).replace("@@GRAIN@@", GRAIN).replace("@@FILM@@", FILM)
        assert "@@" not in body, page.name
        out = head(meta, prefix) + header(meta.get("active", ""), prefix) + '<main id="main">\n' + body + "</main>\n" + footer(prefix)
        (DIST / page.name).write_text(out)
        print(f"{page.name:20s} {len(out):>7,d} bytes")


if __name__ == "__main__":
    build()
