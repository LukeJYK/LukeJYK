"""Generate assets/langs.svg: language usage (by bytes) across LukeJYK's own public repos."""
import json, os, urllib.request

USER = "LukeJYK"
EXCLUDE = {"Jupyter Notebook", "HTML", "CSS"}  # notebooks/markup skew byte counts
TOP_N = 6
COLORS = {
    "Python": "#3572A5", "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Verilog": "#b2b7f8",
    "Shell": "#89e051", "Cuda": "#3A4E3A", "Go": "#00ADD8", "Rust": "#dea584",
    "Java": "#b07219", "Makefile": "#427819",
}

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-langs"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
totals = {}
for r in repos:
    if r["fork"]:
        continue
    for lang, n in get(r["languages_url"]).items():
        if lang not in EXCLUDE:
            totals[lang] = totals.get(lang, 0) + n

top = sorted(totals.items(), key=lambda x: -x[1])[:TOP_N]
s = sum(n for _, n in top)
items = [(l, n / s * 100) for l, n in top]

W, PAD = 420, 20
bar_w = W - 2 * PAD
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{60 + 24 * ((len(items) + 1) // 2)}" viewBox="0 0 {W} {60 + 24 * ((len(items) + 1) // 2)}">',
         '<style>text{font:600 13px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#8B949E}</style>',
         f'<clipPath id="c"><rect x="{PAD}" y="14" width="{bar_w}" height="10" rx="5"/></clipPath><g clip-path="url(#c)">']
x = PAD
for l, p in items:
    w = bar_w * p / 100
    parts.append(f'<rect x="{x:.2f}" y="14" width="{w + 0.5:.2f}" height="10" fill="{COLORS.get(l, "#C9A227")}"/>')
    x += w
parts.append("</g>")
for i, (l, p) in enumerate(items):
    cx = PAD + (i % 2) * (bar_w / 2)
    cy = 52 + (i // 2) * 24
    parts.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS.get(l, "#C9A227")}"/>')
    parts.append(f'<text x="{cx + 16}" y="{cy}">{l} {p:.1f}%</text>')
parts.append("</svg>")

out = os.path.join(os.path.dirname(__file__), "..", "assets", "langs.svg")
with open(out, "w") as f:
    f.write("\n".join(parts))
for l, p in items:
    print(f"{l:12s} {p:5.1f}%")
