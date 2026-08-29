#!/usr/bin/env python3
"""Refresh in-repo stats SVGs from the GitHub API. No third-party widgets."""
import json, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
USER = os.environ.get("USER_NAME", "forge-aidd")

def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-profile",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def card(path, theme, title, rows):
    bg, text, key, value, rule = theme
    pad_x, pad_y, line_h = 28, 22, 22
    width = 360
    height = pad_y + 26 + 16 + len(rows) * line_h + pad_y
    y0 = pad_y + 18
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        f'<rect width="100%" height="100%" rx="8" fill="{bg}"/>',
        f'<text x="{pad_x}" y="{y0}" fill="{text}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15" font-weight="600">{esc(title)}</text>',
        f'<line x1="{pad_x}" y1="{y0+10}" x2="{width-pad_x}" y2="{y0+10}" stroke="{rule}" stroke-width="1"/>',
    ]
    y = y0 + 34
    for k, v in rows:
        parts.append(
            f'<text x="{pad_x}" y="{y}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="14">'
            f'<tspan fill="{key}">{esc(k)}:</tspan>'
            f'<tspan fill="{rule}"> · </tspan>'
            f'<tspan fill="{value}">{esc(v)}</tspan></text>'
        )
        y += line_h
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts) + "\n")

user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
owned = [r for r in repos if not r.get("fork")]
try:
    commits = api(f"/search/commits?q=author:{USER}&per_page=1")
    commit_count = commits.get("total_count", 0)
except Exception:
    commit_count = "n/a"
rows = [
    ("Repos", user.get("public_repos", 0)),
    ("Stars", sum(r.get("stargazers_count", 0) for r in owned)),
    ("Commits", commit_count),
    ("Followers", user.get("followers", 0)),
]
card(ROOT / "stats_dark.svg", ("#161b22", "#c9d1d9", "#ffa657", "#a5d6ff", "#616e7f"), "github stats", rows)
card(ROOT / "stats_light.svg", ("#ffffff", "#24292f", "#953800", "#0a3069", "#57606a"), "github stats", rows)
