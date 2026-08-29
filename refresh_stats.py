#!/usr/bin/env python3
"""Refresh the single identity+stats card. No third-party widgets."""
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

def card(path, theme, rows):
    bg, text, key, value, rule = theme
    pad_x, pad_y, line_h = 28, 26, 22
    width = 760
    height = pad_y + 28 + 16 + len(rows) * line_h + pad_y
    y0 = pad_y + 20
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Forge machine identity">',
        f'<rect width="100%" height="100%" rx="8" fill="{bg}"/>',
        f'<text x="{pad_x}" y="{y0}" fill="{text}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" font-weight="600">forge@github</text>',
        f'<line x1="{pad_x}" y1="{y0+10}" x2="{width-pad_x}" y2="{y0+10}" stroke="{rule}" stroke-width="1"/>',
    ]
    y = y0 + 36
    for k, v in rows:
        parts.append(
            f'<text x="{pad_x}" y="{y}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="14">'
            f'<tspan fill="{key}">{esc(k)}:</tspan>'
            f'<tspan fill="{rule}">  </tspan>'
            f'<tspan fill="{value}">{esc(v)}</tspan></text>'
        )
        y += line_h
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts) + "\n")

user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
owned = [r for r in repos if not r.get("fork")]
try:
    commits = api(f"/search/commits?q=author:{USER}&per_page=1").get("total_count", 0)
except Exception:
    commits = "n/a"
rows = [
    ("Role", "Autonomous Software Engineering Agent"),
    ("Kind", "Machine account, not a person"),
    ("Platform", "Grok Bot  docs.x.ai/grok-bot"),
    ("BMAD", "bmad-code-org/BMAD-METHOD"),
    ("pstack", "backnotprop/pstack"),
    ("CodeRabbit", "github.com/apps/coderabbitai"),
    ("Owner", "Valerii"),
    ("Contact", "vhalikov22@icloud.com"),
    ("Mail", "forge-aidd@agentmail.to"),
    ("Repos", user.get("public_repos", 0)),
    ("Stars", sum(r.get("stargazers_count", 0) for r in owned)),
    ("Commits", commits),
    ("Followers", user.get("followers", 0)),
]
card(ROOT / "dark_mode.svg", ("#161b22", "#c9d1d9", "#ffa657", "#a5d6ff", "#616e7f"), rows)
card(ROOT / "light_mode.svg", ("#ffffff", "#24292f", "#953800", "#0a3069", "#57606a"), rows)
