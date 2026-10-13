"""Builds the سرد wordmark and icon: Thmanyah Serif Display with kashida, the harakat in rubric red.

The red is drawn by layering: the full word (with harakat) in red, then the same word without harakat in ink on top,
so only the harakat stay red and the Arabic shaping is never split. Outputs SVG (live text), PNG, and outlined SVG.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LIGHT = dict(ink="#1E1A16", paper="#F6F1E7", rubric="#A33B2B")
DARK = dict(ink="#F6F1E7", paper="#1E1A16", rubric="#E07A62")

def word(text_marked, text_bare, x, y, size, weight, c):
    t = f'x="{x}" y="{y}" text-anchor="middle" direction="rtl" font-family="Thmanyah Serif Display" font-weight="{weight}" font-size="{size}"'
    return (f'<text {t} fill="{c["rubric"]}">{text_marked}</text>'
            f'<text {t} fill="{c["ink"]}" stroke="{c["ink"]}" stroke-width="0.6">{text_bare}</text>')

def svg(w, h, vb, body, c, rx=0):
    x, y, vw, vh = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {vw} {vh}">'
            f'<rect x="{x}" y="{y}" width="{vw}" height="{vh}" rx="{rx}" fill="{c["paper"]}"/>{body}</svg>')

LOGO = ("سَــــــرْد", "ســــــرد")   # long kashida for the wordmark
ICON = ("سَـرْد", "سـرد")           # compact form for the square icon

variants = {
    "sard-logo":       (1800, 600, (0, 0, 900, 300), word(*LOGO, 450, 192, 230, 700, LIGHT), LIGHT, 0),
    "sard-logo-dark":  (1800, 600, (0, 0, 900, 300), word(*LOGO, 450, 192, 230, 700, DARK), DARK, 0),
    "sard-logo-email": (480, 160, (0, 0, 900, 300), word(*LOGO, 450, 192, 230, 700, LIGHT), LIGHT, 0),
    "sard-icon":       (1024, 1024, (0, 0, 400, 400), word(*ICON, 200, 232, 165, 900, LIGHT), LIGHT, 88),
    "sard-icon-dark":  (1024, 1024, (0, 0, 400, 400), word(*ICON, 200, 232, 165, 900, DARK), DARK, 88),
}

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for name, (w, h, vb, body, c, rx) in variants.items():
    s = svg(w, h, vb, body, c, rx)
    open(os.path.join(HERE, f"{name}.svg"), "w", encoding="utf-8").write(s)
    page = os.path.join(HERE, f".{name}.html")
    open(page, "w", encoding="utf-8").write(
        f'<!doctype html><meta charset="utf-8"><style>@page{{size:{w}px {h}px;margin:0}}html,body{{margin:0;background:transparent}}svg{{display:block}}</style>{s}')
    run(CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
        "--default-background-color=00000000", f"--screenshot={os.path.join(HERE, name + '.png')}", "file://" + page)
    pdf = os.path.join(HERE, f".{name}.pdf")
    run(CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + page)
    run("pdftocairo", "-svg", pdf, os.path.join(HERE, f"{name}-outlined.svg"))
    os.remove(page); os.remove(pdf)
    print("built", name)
