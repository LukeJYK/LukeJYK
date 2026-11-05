"""Generate assets/stats.svg: GitHub stats (left) + language usage (right).

Usage: python3 scripts/gen_card.py   (set GITHUB_TOKEN to avoid rate limits)
"""
import json, os, urllib.request
from xml.sax.saxutils import escape

USER = "LukeJYK"
EXCLUDE = {"Jupyter Notebook", "HTML", "CSS"}  # notebooks/markup skew byte counts
TOP_N = 6
GOLD, TEXT, MUTED = "#6A8CAF", "#8B949E", "#8B949E"
COLORS = {  # muted palette
    "JavaScript": "#8FA8C8", "Python": "#4F6D8F", "Verilog": "#9BB5A6",
    "C#": "#7D9C8A", "VHDL": "#B4A9C6", "Shell": "#A8B8C9", "C": "#6B7785",
    "C++": "#B88A9A", "TypeScript": "#5E86A8", "Cuda": "#7A8F7A", "Go": "#7FB2C4",
    "Rust": "#C2A28C", "Java": "#A68B6E", "Makefile": "#8C9A7A",
}

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-card"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def search_count(kind, q):
    return get(f"https://api.github.com/search/{kind}?q={q}&per_page=1")["total_count"]

user = get(f"https://api.github.com/users/{USER}")
repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]

stats = [
    ("Commits", search_count("commits", f"author:{USER}")),
    ("Pull Requests", search_count("issues", f"author:{USER}+type:pr")),
    ("Issues", search_count("issues", f"author:{USER}+type:issue")),
    ("Stars Earned", sum(r["stargazers_count"] for r in repos)),
    ("Public Repos", user["public_repos"]),
    ("Followers", user["followers"]),
]

totals = {}
for r in repos:
    for lang, n in get(r["languages_url"]).items():
        if lang not in EXCLUDE:
            totals[lang] = totals.get(lang, 0) + n
top = sorted(totals.items(), key=lambda x: -x[1])[:TOP_N]
s = sum(n for _, n in top) or 1
langs = [(l, n / s * 100) for l, n in top]

W, H = 840, 190
LX, RX, PANEL = 20, 450, 370   # left/right panel x, right panel width
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<style>.t{{font:700 17px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:{GOLD}}}'
       f'.l{{font:500 14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:{TEXT}}}'
       f'.v{{font:700 14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:{TEXT}}}</style>',
       f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{MUTED}" stroke-opacity="0.3"/>',
       f'<line x1="{W/2 + 10}" y1="20" x2="{W/2 + 10}" y2="{H-20}" stroke="{MUTED}" stroke-opacity="0.3"/>']

# Left: stats
svg.append(f'<text class="t" x="{LX}" y="34">GitHub Stats</text>')
for i, (k, v) in enumerate(stats):
    y = 64 + i * 22
    svg.append(f'<text class="l" x="{LX}" y="{y}">{escape(k)}</text>')
    svg.append(f'<text class="v" x="{LX + 380}" y="{y}" text-anchor="end">{v:,}</text>')

# Right: languages
svg.append(f'<text class="t" x="{RX}" y="34">Most Used Languages</text>')
svg.append(f'<clipPath id="c"><rect x="{RX}" y="50" width="{PANEL}" height="10" rx="5"/></clipPath><g clip-path="url(#c)">')
x = RX
for l, p in langs:
    w = PANEL * p / 100
    svg.append(f'<rect x="{x:.2f}" y="50" width="{w + 0.5:.2f}" height="10" fill="{COLORS.get(l, GOLD)}"/>')
    x += w
svg.append("</g>")
for i, (l, p) in enumerate(langs):
    cx, cy = RX + (i % 2) * (PANEL / 2), 100 + (i // 2) * 32
    svg.append(f'<circle cx="{cx + 5}" cy="{cy - 5}" r="5" fill="{COLORS.get(l, GOLD)}"/>')
    svg.append(f'<text class="l" x="{cx + 16}" y="{cy}">{escape(l)} <tspan class="v">{p:.1f}%</tspan></text>')
svg.append("</svg>")

out = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")
open(out, "w").write("\n".join(svg))
print(stats); print(langs)
