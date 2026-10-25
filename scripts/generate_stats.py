#!/usr/bin/env python3
"""Generate assets/stats-dark.svg and assets/stats-light.svg for Mayur Pagote's profile README.

Zero external dependencies - runs purely on Python standard library (3.10+).
Fetches live contributions from GitHub and open-source merged PRs via GitHub Search API.
"""

import math
import os
import re
import json
import urllib.request
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
USERNAME = "Mayur-Pagote"
LOCAL_TZ = "Asia/Kolkata"

# 5x7 bitmapped font matrix
FONT = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#", "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.", "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####", "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####", "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "###|.#.|.#.|.#.|.#.|.#.|###", "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.", "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.", "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.", "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.", "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####", "3": "#####|...#.|..#..|...#.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.", "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.", "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    ",": "..|..|..|..|.#|.#|#.", ".": ".|.|.|.|.|.|#", " ": "...|...|...|...|...|...|...",
    "-": "....|....|....|####|....|....|....", "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    ":": ".|#|.|.|.|#|.", "!": "#|#|#|#|#|.|#", "'": "#|#|.|.|.|.|.", "_": ".....|.....|.....|.....|.....|.....|#####",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....", "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "&": ".##..|#..#.|.##..|.#...|#.#.#|#..#.|.##.#", "~": ".....|.....|.#...|#.#.#|...#.|.....|.....",
}
GL = {k: v.split("|") for k, v in FONT.items()}

def glyph(ch):
    return GL.get(ch) or GL.get(ch.upper()) or GL["?"]

def px_width(text, s):
    w = 0
    for ch in text:
        w += len(glyph(ch)[0]) + 1
    return max(0, w - 1) * s

def _n(v):
    if isinstance(v, int):
        return str(v)
    f = float(v)
    if f.is_integer():
        return str(int(f))
    return f"{f:.2f}".rstrip('0').rstrip('.')

def jsround(v):
    return math.floor(v + 0.5)

def esc(v):
    return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def runs(rows, x, y, s, ch="#"):
    d = []
    for r, row in enumerate(rows):
        c = 0
        n = len(row)
        while c < n:
            if row[c] != ch:
                c += 1
                continue
            e = c
            while e < n and row[e] == ch:
                e += 1
            d.append(f"M{_n(x + c * s)} {_n(y + r * s)}h{_n((e - c) * s)}v{_n(s)}h{_n(-(e - c) * s)}z")
            c = e
    return "".join(d)

def px_path(text, x, y, s):
    d = []
    cx = x
    for ch in text:
        g = glyph(ch)
        d.append(runs(g, cx, y, s))
        cx += (len(g[0]) + 1) * s
    return "".join(d)

def px_text(text, x, y, s, fill, shadow=None):
    d = px_path(text, x, y, s)
    out = ""
    if shadow:
        out += f'<path fill="{shadow}" transform="translate({_n(s)} {_n(s)})" d="{d}"/>'
    return out + f'<path fill="{fill}" d="{d}"/>'

def rect(x, y, w, h, fill, inner=""):
    return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" fill="{fill}">{inner}</rect>' if inner \
        else f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" fill="{fill}"/>'

def T(x, y, text, size=12, fill=None, anchor="start", weight=400):
    w = f' font-weight="{weight}"' if weight != 400 else ""
    return (
        f'<text x="{_n(x)}" y="{_n(y)}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}"{w}>{esc(text)}</text>'
    )

def head(x, label, extra, p):
    tail = f'<tspan fill="{p.dim}" letter-spacing="0">  ·  {esc(extra)}</tspan>' if extra else ""
    return (
        f'<text x="{_n(x)}" y="24" font-family="{MONO}" font-size="12" letter-spacing=".6" '
        f'fill="{p.mid}">{esc(label)}{tail}</text>'
    )

def stars_fmt(n):
    if n >= 1000:
        return f"{n/1000:.1f}k★"
    return f"{n}★"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

DARK_PALETTE = SimpleNamespace(
    ink="#ededed", mid="#a3a3a3", dim="#5f5f5f",
    faint="#2a2a2a", track="#151515", tick="#cdcdcd", shadow="#4d4d4d",
)

LIGHT_PALETTE = SimpleNamespace(
    ink="#1f2328", mid="#57606a", dim="#8c959f",
    faint="#d0d7de", track="#eaeef2", tick="#424a53", shadow="#afb8c1",
)

def make_defs(uid, p):
    cells = {"d25": [(0, 0)], "d50": [(0, 0), (1, 1)], "d75": [(0, 0), (1, 0), (0, 1)]}
    o = []
    for c in (2, 3):
        for k, cs in cells.items():
            anim = (
                f'<animateTransform attributeName="patternTransform" type="translate" values="0 0;{c} 0" '
                f'dur="1.2s" calcMode="discrete" repeatCount="indefinite"/>'
            ) if k == "d50" and c == 3 else ""
            cells_svg = "".join(
                f'<rect x="{x * c}" y="{y * c}" width="{c}" height="{c}" fill="{p.ink}"/>' for x, y in cs
            )
            o.append(
                f'<pattern id="{uid}-{k}-{c}" width="{2 * c}" height="{2 * c}" patternUnits="userSpaceOnUse">'
                f"{cells_svg}{anim}</pattern>"
            )
    o.append(
        f'<pattern id="{uid}-sh" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="2" height="2" fill="{p.shadow}"/><rect x="2" y="2" width="2" height="2" fill="{p.shadow}"/></pattern>'
    )
    return "".join(o)

def make_bar(x, y, w, h, frac, uid, p):
    frac = max(0, min(1, frac))
    c = 3
    o = [rect(x, y, w, h, p.track)]
    for i in range(1, 10):
        tx = jsround(x + w * i / 10)
        o.append(rect(tx, y + h - 3, 1, 3, p.faint))
    fw = jsround(frac * w / c) * c
    if fw <= 0:
        return "".join(o)
    solid = max(0, fw - 2 * c)
    o.append(rect(x, y, solid, h, p.ink))
    for i in range(1, 10):
        tx = jsround(x + w * i / 10)
        if tx < x + solid - 1:
            o.append(rect(tx, y, 1, h, p.tick))
    for i, k in enumerate(("d75", "d50", "d25")):
        fx = x + solid + i * c
        if fx >= x + w:
            continue
        o.append(rect(fx, y, min(c, x + w - fx), h, f"url(#{uid}-{k}-3)"))
    return "".join(o)

def make_chart(x, y, w, h, data, uid, p):
    n = len(data)
    col_w = w / n
    bw = max(2, math.floor(col_w) - 3)
    mx = max(data) if max(data) > 0 else 1
    c = 3
    rows = math.floor(h / c)
    o = []
    max_label = ""
    for i, v in enumerate(data):
        bx = jsround(x + i * col_w)
        k = max(1, jsround(v / mx * rows)) if v > 0 else 0
        if not k:
            o.append(rect(bx, y + h - 2, bw, 2, p.faint))
            continue
        top = y + h - k * c
        if k > 1:
            o.append(rect(bx, top + c, bw, (k - 1) * c, p.ink))
        o.append(rect(bx, top, bw, c, f"url(#{uid}-{'d50' if k > 1 else 'd75'}-3)"))
        if v == mx and not max_label:
            max_label = T(bx + bw / 2, top - 6, str(v), size=10, fill=p.mid, anchor="middle")
    steps = 8
    ys, hs = [], []
    for i in range(steps + 1):
        hh = jsround(h * i / steps)
        ys.append(y + h - hh)
        hs.append(hh)
    reveal = (
        f'<animate attributeName="y" values="{";".join(map(_n, ys))}" dur=".8s" calcMode="discrete" fill="freeze"/>'
        f'<animate attributeName="height" values="{";".join(map(_n, hs))}" dur=".8s" calcMode="discrete" fill="freeze"/>'
    )
    return (
        f'<clipPath id="{uid}-rev"><rect x="{_n(x - 2)}" y="{_n(y)}" width="{_n(w + 4)}" height="{_n(h)}">{reveal}</rect></clipPath>'
        f'<line x1="{_n(x)}" x2="{_n(x + w - 3)}" y1="{_n(y + h + 4.5)}" y2="{_n(y + h + 4.5)}" stroke="{p.faint}" stroke-dasharray="3 3"/>'
        f'<g clip-path="url(#{uid}-rev)">{"".join(o)}</g>{max_label}'
    )

def render_stats_svg(data, palette, uid):
    p = palette
    W = 1024
    H = 180
    o = []

    o.append(f'<defs>{make_defs(uid, p)}</defs>')

    # Equal Spacing Coordinates:
    # Left Margin: 24
    # Col 1: width 300 (x: 24 to 324)
    # Gap 1: 48 (x: 324 to 372)
    # Col 2: width 250 (x: 372 to 622)
    # Gap 2: 48 (x: 622 to 670)
    # Col 3: width 330 (x: 670 to 1000)
    # Right Margin: 24 (1024 - 1000 = 24)

    # 1. Left section: CONTRIBUTIONS (x: 24 to 324, width 300)
    c1_x = 24
    c1_w = 300
    days = data['days']
    total_31 = sum(days)
    chart_h = 100
    top_y = 44
    o.append(head(c1_x, "CONTRIBUTIONS", f"{total_31:,} in the last {len(days)} days", p))
    o.append(make_chart(c1_x, top_y, c1_w, chart_h, days, uid, p))
    o.append(T(c1_x, top_y + chart_h + 23, data['days_from'], size=11, fill=p.dim))
    o.append(T(c1_x + c1_w, top_y + chart_h + 23, "today", size=11, fill=p.dim, anchor="end"))

    # 2. Middle section: TOTALS (x: 372 to 622, width 250)
    c2_x = 372
    c2_w = 250
    o.append(head(c2_x, "TOTALS", "", p))
    total_str = f"{data['total']:,}"
    streak_str = str(data['streak'])
    best_str = str(data['best'])

    # Big numbers at 372
    o.append(px_text(total_str, c2_x, top_y - 2, 3, p.ink))
    lx = c2_x + 88
    o.append(T(lx, top_y + 14, "contributions", size=12, fill=p.mid))

    o.append(px_text(streak_str, c2_x, top_y + 28, 3, p.ink))
    o.append(T(lx, top_y + 44, "day streak, current", size=12, fill=p.mid))

    o.append(px_text(best_str, c2_x, top_y + 58, 3, p.ink))
    o.append(T(lx, top_y + 74, "day streak, best", size=12, fill=p.mid))

    # Streak bar
    bar_y = top_y + 92
    bar_w = 175
    frac = data['streak'] / data['best'] if data['best'] else 1.0
    o.append(make_bar(c2_x, bar_y, bar_w, 14, frac, uid, p))
    o.append(T(c2_x + c2_w, bar_y + 13, f"{data['streak']}/{data['best']}", size=15, fill=p.ink, weight=700, anchor="end"))

    # 3. Right section: OPEN SOURCE (x: 670 to 1000, width 330)
    c3_x = 670
    o.append(head(c3_x, "OPEN SOURCE", "merged prs", p))
    total_prs_str = str(data['total_prs'])
    o.append(px_text(total_prs_str, c3_x, top_y - 4, 4, p.ink, f"url(#{uid}-sh)"))
    plx = c3_x + px_width(total_prs_str, 4) + 16
    o.append(T(plx, top_y + 9, "merged pull requests", size=12, fill=p.mid))
    o.append(T(plx, top_y + 24, f"{data['total_repos']} public repos, top 7 below", size=11, fill=p.dim))

    # OSS Repos List (top 7)
    row_y = top_y + 42
    for i, (repo, stars_cnt, prs_cnt) in enumerate(data['oss'][:7]):
        ry = row_y + i * 14.5
        parts = repo.split("/", 1)
        owner = parts[0] + "/"
        rname = parts[1] if len(parts) > 1 else ""
        if len(owner) + len(rname) > 33:
            rname = rname[:30 - len(owner)] + "…"
        
        o.append(
            f'<text x="{c3_x}" y="{_n(ry)}" font-family="{MONO}" font-size="11" fill="{p.dim}">{esc(owner)}'
            f'<tspan fill="{p.mid}">{esc(rname)}</tspan></text>'
        )
        o.append(T(970, ry, stars_fmt(stars_cnt), size=11, fill=p.dim, anchor="end"))
        o.append(T(1000, ry, str(prs_cnt), size=11, fill=p.ink, anchor="end"))

    body = "".join(o)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">\n'
        f'{body}\n'
        f'</svg>'
    )

def fetch_data():
    today_str = datetime.now(ZoneInfo(LOCAL_TZ)).strftime("%Y-%m-%d")

    def fetch_contributions_html(year=None):
        if year:
            url = f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31"
        else:
            url = f"https://github.com/users/{USERNAME}/contributions"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")

    days_map = {}
    current_year = datetime.now(ZoneInfo(LOCAL_TZ)).year
    for year in range(2024, current_year + 1):
        try:
            html = fetch_contributions_html(year)
            for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})".*?<tool-tip[^>]*>(.*?)</tool-tip>', html, re.S):
                date_str = m.group(1)
                tip = m.group(2).strip()
                count_match = re.search(r'(\d+)\s+contribution', tip)
                count = int(count_match.group(1)) if count_match else 0
                if date_str <= today_str:
                    days_map[date_str] = count
        except Exception as e:
            print(f"Warning fetching year {year}: {e}")

    sorted_days = sorted(days_map.items())
    last_31_days = sorted_days[-31:]
    days_from_dt = datetime.fromisoformat(last_31_days[0][0])
    days_from = f"{days_from_dt:%b} {days_from_dt.day}".lower()
    days_counts = [c for _, c in last_31_days]
    total_contribs = sum(c for _, c in sorted_days)

    # Streak
    curr_streak = 0
    start_idx = len(sorted_days) - 1
    if sorted_days[-1][1] == 0:
        start_idx = len(sorted_days) - 2

    for i in range(start_idx, -1, -1):
        if sorted_days[i][1] > 0:
            curr_streak += 1
        else:
            break

    best_streak = 0
    temp = 0
    for d, c in sorted_days:
        if c > 0:
            temp += 1
            if temp > best_streak:
                best_streak = temp
        else:
            temp = 0

    # PRs
    pr_url = f"https://api.github.com/search/issues?q=is:pr+is:merged+author:{USERNAME}+-user:{USERNAME}&per_page=100"
    pr_req = urllib.request.Request(pr_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pr_req) as resp:
        pr_data = json.loads(resp.read().decode("utf-8"))

    total_prs = pr_data.get("total_count", 0)
    items = pr_data.get("items", [])

    repo_counts = {}
    repo_stars = {}
    for it in items:
        repo_url = it.get("repository_url", "")
        repo_name = repo_url.replace("https://api.github.com/repos/", "")
        repo_counts[repo_name] = repo_counts.get(repo_name, 0) + 1

    headers = {"User-Agent": "Mozilla/5.0"}
    for repo in sorted(repo_counts.keys(), key=lambda r: -repo_counts[r])[:10]:
        try:
            r_req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers)
            with urllib.request.urlopen(r_req) as resp:
                r_info = json.loads(resp.read().decode("utf-8"))
                repo_stars[repo] = r_info.get("stargazers_count", 0)
        except Exception:
            repo_stars[repo] = 0

    ranked_repos = sorted(repo_counts.keys(), key=lambda r: (-repo_counts[r], -repo_stars.get(r, 0)))[:7]
    oss = [(r, repo_stars.get(r, 0), repo_counts[r]) for r in ranked_repos]

    return {
        'total': total_contribs,
        'streak': curr_streak,
        'best': best_streak,
        'days_from': days_from,
        'days': days_counts,
        'total_prs': total_prs,
        'total_repos': len(repo_counts),
        'oss': oss
    }


def main():
    print("Fetching live GitHub data for Mayur Pagote...")
    data = fetch_data()
    print(f"Data summary: {data['total']} contributions, {data['streak']} streak, {data['total_prs']} merged PRs")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    dark_svg = render_stats_svg(data, DARK_PALETTE, "sd")
    light_svg = render_stats_svg(data, LIGHT_PALETTE, "sl")

    (ASSETS_DIR / "stats-dark.svg").write_text(dark_svg, encoding="utf-8")
    (ASSETS_DIR / "stats-light.svg").write_text(light_svg, encoding="utf-8")
    print(f"Updated {ASSETS_DIR / 'stats-dark.svg'}")
    print(f"Updated {ASSETS_DIR / 'stats-light.svg'}")

if __name__ == "__main__":
    main()
