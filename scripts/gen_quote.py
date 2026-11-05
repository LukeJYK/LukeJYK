"""Render the LOTR quote as pure-path SVG (no font needed at view time).

Usage: python3 scripts/gen_quote.py path/to/ringbearer.ttf
"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TEXT = "Not all those who wander are lost."
COLOR = "#C9A227"
SIZE = 44  # px

font = TTFont(sys.argv[1])
cmap, gs = font.getBestCmap(), font.getGlyphSet()
upm = font["head"].unitsPerEm
scale = SIZE / upm
asc = font["hhea"].ascent
desc = -font["hhea"].descent
hmtx = font["hmtx"]

paths, x = [], 0
for ch in TEXT:
    name = cmap.get(ord(ch)) or ".notdef"
    pen = SVGPathPen(gs)
    gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x * scale, asc * scale)))
    d = pen.getCommands()
    if d:
        paths.append(d)
    x += hmtx[name][0]

w, h = x * scale + 20, (asc + desc) * scale + 10
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
       f'viewBox="-10 -5 {w:.0f} {h:.0f}"><title>{TEXT}</title>'
       f'<path fill="{COLOR}" d="{" ".join(paths)}"/></svg>')
out = os.path.join(os.path.dirname(__file__), "..", "assets", "quote.svg")
open(out, "w").write(svg)
print("wrote", os.path.abspath(out))
