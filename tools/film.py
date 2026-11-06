"""Generates the 'Generations' hero film: layered sky, clouds, weather and the engraved summit."""
import math
import random

W, H = 1600, 700
ART_X, ART_Y, ART_S = 472, 60, 1.6
CX = 330


def h(x):
    p1 = max(0.0, 1 - abs(x - CX) / 270) ** 1.45
    p2 = 0.62 * max(0.0, 1 - abs(x - 140) / 190) ** 1.3
    p3 = 0.48 * max(0.0, 1 - abs(x - 505) / 165) ** 1.3
    base = max(p1, p2, p3)
    rug = 0.018 * math.sin(x / 6.5) + 0.012 * math.sin(x / 2.9 + 1.3)
    return max(0.0, base + rug * base)


def art_lines(count=20, step=5):
    out = []
    for i in range(count):
        yb = 360 + i * 18
        amp = 260 * (1 - i * 0.035)
        pts = " ".join(f"{x},{yb - amp * h(x):.1f}" for x in range(0, 601, step))
        op = round(max(0.14, 0.95 - i * 0.042), 2)
        out.append(
            f'<polyline points="{pts}" pathLength="1" fill="none" stroke="currentColor" stroke-width="0.8" '
            f'opacity="{op}" style="animation-delay: {0.2 + i * 0.06:.2f}s"></polyline>'
        )
    return "\n".join(out)


def top_line_pts(step=5):
    return [(x, 360 - 260 * h(x)) for x in range(0, 601, step)]


def near_silhouette():
    pts = [(ART_X + ART_S * x, ART_Y + ART_S * y) for x, y in top_line_pts()]
    # Foothills slope gently down to the frame's bottom edge instead of ending in a vertical cliff.
    pts = [(ART_X - 300, H)] + pts + [(ART_X + ART_S * 600 + 300, H)]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def ridge(base, amps, freqs, phases, rough, step=8):
    pts = []
    for x in range(-20, W + 21, step):
        y = base
        for a, f, p in zip(amps, freqs, phases):
            y -= a * math.sin(x / f + p)
        y -= rough * abs(math.sin(x / 19.0)) + rough * 0.5 * abs(math.sin(x / 7.3 + 0.7))
        pts.append((x, y))
    pts += [(W + 20, H), (-20, H)]
    return " ".join(f"{x},{y:.1f}" for x, y in pts)


def stars(n=80, seed=11):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.uniform(0, W)
        y = rnd.uniform(10, 380)
        r = rnd.choice([0.7, 0.8, 0.9, 1.1, 1.3, 1.6])
        o = round(rnd.uniform(0.35, 1.0), 2)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#F3EEE5" opacity="{o}"></circle>')
    return "".join(out)


def cloud_tile(fid, freq, octaves, seed, rgb, a_mul, a_off):
    r, g, b = rgb
    return (
        f'<svg aria-hidden="true" preserveAspectRatio="none" style="display: block; width: 50%; height: 100%; flex: none">'
        f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="{octaves}" seed="{seed}" stitchTiles="stitch"></feTurbulence>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  0 0 0 {a_mul} {a_off}"></feColorMatrix>'
        f'</filter><rect width="100%" height="100%" filter="url(#{fid})"></rect></svg>'
    )


def cloud_layer(key, cls, top, height, freq, octaves, seed, rgb, a_mul, a_off, opacity):
    tiles = cloud_tile(f"{key}a", freq, octaves, seed, rgb, a_mul, a_off) + cloud_tile(f"{key}b", freq, octaves, seed, rgb, a_mul, a_off)
    return (
        f'<div aria-hidden="true" style="position: absolute; left: 0; top: {top}; width: 100%; height: {height}; overflow: hidden; '
        f'-webkit-mask-image: linear-gradient(to bottom, #000 45%, transparent 100%); mask-image: linear-gradient(to bottom, #000 45%, transparent 100%)">'
        f'<div class="{cls}" style="display: flex; width: 200%; height: 100%; opacity: {opacity}; will-change: transform">{tiles}</div></div>'
    )


def film(variant, accent_hole="{{accent}}", site=False):
    """variant: 'desktop' or 'phone'. site=True emits plain HTML for the live website (no canvas bindings)."""
    k = "d" if variant == "desktop" else "p"
    if site:
        accent_hole = "#C9B183"
    if variant == "desktop":
        aspect = "16 / 7"
        vb = f"0 0 {W} {H}"
    else:
        aspect = "4 / 5"
        vb = f"700 0 560 {H}"

    sky = (
        '<div aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(180deg, #34312B 0%, #4B463D 50%, #625A4B 100%)"></div>'
        '<div class="f-storm" aria-hidden="true" style="position: absolute; inset: 0; opacity: 0; background: linear-gradient(180deg, #0C0D0F 0%, #1A1B1E 55%, #2A2A2A 100%)"></div>'
        '<div class="f-night" aria-hidden="true" style="position: absolute; inset: 0; opacity: 0; background: linear-gradient(180deg, #05060A 0%, #0D1017 55%, #191B20 100%)"></div>'
        '<div class="f-dawn" aria-hidden="true" style="position: absolute; inset: 0; opacity: 1; background: linear-gradient(180deg, #2E2922 0%, #6F5B40 38%, #B9976A 66%, #E2C79A 86%, #F0DDB8 100%)"></div>'
        '<div class="f-dawn" aria-hidden="true" style="position: absolute; inset: 0; opacity: 1; background: radial-gradient(circle at 62% 46%, rgba(246,224,178,0.75) 0%, rgba(246,224,178,0.18) 18%, rgba(246,224,178,0) 40%)"></div>'
    )
    star_layer = (
        f'<svg class="f-stars" aria-hidden="true" viewBox="{vb}" preserveAspectRatio="xMidYMax slice" '
        f'style="position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0">{stars()}</svg>'
    )
    flash = '<div class="f-flash" aria-hidden="true" style="position: absolute; inset: 0; opacity: 0; background: radial-gradient(ellipse at 30% 20%, #F4F3FF 0%, #BFC3D6 45%, #6E7180 100%)"></div>'

    clouds = (
        cloud_layer(f"cl{k}1", "f-drift-slow", "0", "70%", "0.0032 0.012", 4, 7, (0.90, 0.87, 0.82), 2.2, -0.98, 0.55)
        + '<div class="f-stormcl" aria-hidden="true" style="position: absolute; inset: 0; opacity: 0">'
        + cloud_layer(f"cl{k}2", "f-drift-fast", "0", "78%", "0.0028 0.010", 4, 23, (0.13, 0.13, 0.15), 3.0, -1.0, 1)
        + "</div>"
    )

    far = ridge(470, [38, 24, 12], [260.0, 113.0, 47.0], [0.6, 1.9, 0.3], 9)
    mid = ridge(560, [30, 18, 9], [190.0, 77.0, 33.0], [2.2, 0.4, 1.1], 7)
    near = near_silhouette()
    top = " ".join(f"{x},{y:.1f}" for x, y in top_line_pts())

    mountains = (
        f'<svg aria-hidden="true" viewBox="{vb}" preserveAspectRatio="xMidYMax slice" style="position: absolute; inset: 0; width: 100%; height: 100%; color: {accent_hole}">'
        f'<defs><radialGradient id="gl{k}"><stop offset="0" stop-color="#FFF4DC" stop-opacity="1"></stop><stop offset="0.35" stop-color="#F2D9A6" stop-opacity="0.55"></stop><stop offset="1" stop-color="#F2D9A6" stop-opacity="0"></stop></radialGradient>'
        f'<filter id="rim{k}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.4"></feGaussianBlur></filter></defs>'
        f'<polygon points="{far}" fill="#4A4338" opacity="0.72"></polygon>'
        f'<polygon points="{mid}" fill="#2A2620" opacity="0.92"></polygon>'
        f'<polygon points="{near}" fill="#0E0D0B"></polygon>'
        f'<g transform="translate({ART_X} {ART_Y}) scale({ART_S})">'
        f'<polyline class="f-rim" points="{top}" fill="none" stroke="#F2D9A6" stroke-width="2.2" filter="url(#rim{k})" opacity="0.9"></polyline>'
        f'<g class="art">{art_lines()}</g>'
        f'<line x1="330" y1="95" x2="330" y2="44" stroke="currentColor" stroke-width="1"></line>'
        f'<polygon points="330,2 337,28 330,44 323,28" fill="currentColor"></polygon>'
        f'<circle class="f-glint" cx="330" cy="14" r="26" fill="url(#gl{k})" opacity="0"></circle>'
        f'</g></svg>'
    )
    mist = cloud_layer(f"cl{k}3", "f-drift-mist", "58%", "30%", "0.006 0.03", 3, 41, (0.86, 0.84, 0.80), 1.5, -0.72, 0.4)
    rain = (
        '<div class="f-rainwrap" aria-hidden="true" style="position: absolute; inset: 0; opacity: 0; pointer-events: none">'
        '<div class="f-rain" style="position: absolute; inset: 0; background-image: repeating-linear-gradient(101deg, rgba(214,218,228,0) 0px, rgba(214,218,228,0) 11px, rgba(214,218,228,0.26) 11px, rgba(214,218,228,0.26) 12px); background-size: 140px 260px"></div></div>'
    )
    finish = (
        '<div aria-hidden="true" style="position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse 80% 75% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.38) 100%)"></div>'
        f'<svg aria-hidden="true" style="position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0.09; mix-blend-mode: overlay; pointer-events: none">'
        f'<filter id="gr{k}"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"></feTurbulence></filter>'
        f'<rect width="100%" height="100%" filter="url(#gr{k})"></rect></svg>'
    )
    control = (
        '<button type="button" onClick="{{togglePlay}}" aria-label="{{playLabel}}" '
        'style="position: absolute; right: 18px; bottom: 16px; display: inline-flex; align-items: center; gap: 10px; min-height: 44px; padding: 0 14px; '
        'background: rgba(14,13,11,0.42); border: 1px solid rgba(243,238,229,0.28); color: #F3EEE5; font: inherit; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; cursor: pointer; backdrop-filter: blur(4px)">'
        '<sc-if value="{{playing}}" hint-placeholder-val="{{ true }}"><svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><rect x="3" y="2" width="3" height="12" fill="currentColor"></rect><rect x="10" y="2" width="3" height="12" fill="currentColor"></rect></svg></sc-if>'
        '<sc-if value="{{paused}}" hint-placeholder-val="{{ false }}"><svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><polygon points="4,2 14,8 4,14" fill="currentColor"></polygon></svg></sc-if>'
        '<span>{{playText}}</span></button>'
    )
    if site:
        control = (
            '<button class="film-toggle" type="button" aria-label="Pause the film" '
            'style="position: absolute; right: 18px; bottom: 16px; display: inline-flex; align-items: center; gap: 10px; min-height: 44px; padding: 0 14px; '
            'background: rgba(14,13,11,0.42); border: 1px solid rgba(243,238,229,0.28); color: #F3EEE5; font: inherit; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; cursor: pointer; backdrop-filter: blur(4px)">'
            '<svg class="i-pause" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true" focusable="false"><rect x="3" y="2" width="3" height="12" fill="currentColor"></rect><rect x="10" y="2" width="3" height="12" fill="currentColor"></rect></svg>'
            '<svg class="i-play" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true" focusable="false"><polygon points="4,2 14,8 4,14" fill="currentColor"></polygon></svg>'
            '<span class="film-toggle-text">Pause</span></button>'
        )
        fig_class = f"film film-{variant}"
    else:
        fig_class = "film {{filmState}}"
    return (
        f'<figure class="{fig_class}" style="position: relative; margin: 0; width: 100%; aspect-ratio: {aspect}; overflow: hidden; background: #2A2620">'
        f"{sky}{star_layer}{flash}{clouds}{mountains}{mist}{rain}{finish}{control}"
        f'<figcaption style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0)">A looping film: an engraved mountain summit in golden light, a storm passing over it, a clear night of stars, and dawn returning to the summit.</figcaption>'
        f"</figure>"
    )


FILM_CSS = """
.film.is-paused, .film.is-paused *{animation-play-state:paused !important}
.film .f-dawn{animation:k-dawn 28s ease-in-out infinite}
.film .f-rim{animation:k-dawn 28s ease-in-out infinite}
.film .f-storm{animation:k-storm 28s ease-in-out infinite}
.film .f-stormcl{animation:k-stormcl 28s ease-in-out infinite}
.film .f-night{animation:k-night 28s ease-in-out infinite}
.film .f-stars{animation:k-stars 28s ease-in-out infinite}
.film .f-rainwrap{animation:k-rainwrap 28s ease-in-out infinite}
.film .f-rain{animation:k-rainfall .42s linear infinite}
.film .f-flash{animation:k-flash 28s linear infinite}
.film .f-glint{animation:k-glint 28s ease-in-out infinite}
.film .f-drift-slow{animation:k-drift 120s linear infinite}
.film .f-drift-fast{animation:k-drift 46s linear infinite}
.film .f-drift-mist{animation:k-drift 90s linear infinite reverse}
@keyframes k-drift{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes k-dawn{0%,12%{opacity:1}24%,58%{opacity:0}74%,100%{opacity:1}}
@keyframes k-storm{0%,18%{opacity:0}30%,44%{opacity:1}54%,100%{opacity:0}}
@keyframes k-stormcl{0%,16%{opacity:0}30%,46%{opacity:.95}56%,100%{opacity:0}}
@keyframes k-night{0%,44%{opacity:0}52%,60%{opacity:1}70%,100%{opacity:0}}
@keyframes k-stars{0%,48%{opacity:0}55%,62%{opacity:.9}70%,100%{opacity:0}}
@keyframes k-rainwrap{0%,26%{opacity:0}32%,44%{opacity:.75}50%,100%{opacity:0}}
@keyframes k-rainfall{from{background-position:0 0}to{background-position:-46px 260px}}
@keyframes k-flash{0%,31.9%{opacity:0}32.1%{opacity:.55}32.5%{opacity:.06}32.9%{opacity:.42}33.6%{opacity:0}40%{opacity:0}40.2%{opacity:.3}40.9%,100%{opacity:0}}
@keyframes k-glint{0%,68%{opacity:0}73%{opacity:1}79%,100%{opacity:0}}
@media (prefers-reduced-motion: reduce){.film *{animation:none !important}}
"""
