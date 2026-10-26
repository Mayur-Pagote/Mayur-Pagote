#!/usr/bin/env python3
"""Fetch live view counts across LeetCode, Instructables, YouTube, and GitHub."""

import json
import os
import re
import subprocess
import sys
import urllib.request

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

GIST_ID = os.environ.get("VIEWS_GIST_ID")
GH_TOKEN = os.environ.get("GH_GIST_TOKEN")

def get_leetcode_views():
    try:
        data = json.dumps({
            'query': 'query userPublicProfile($username: String!) { matchedUser(username: $username) { profile { postViewCount } } }',
            'variables': {'username': 'mayurpagote'}
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://leetcode.com/graphql',
            data=data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode('utf-8'))
        return int(res['data']['matchedUser']['profile']['postViewCount'])
    except Exception:
        return 872639

def get_instructables_views():
    try:
        cmd = ["curl", "-s", "-k", "--ssl-no-revoke", "https://www.instructables.com/member/mayurpagote/"]
        if os.name == 'nt':
            cmd[0] = "curl.exe"
        out = subprocess.check_output(cmd, timeout=15).decode('utf-8', errors='ignore')
        # Target the author's grand total views
        m = re.search(r'"screenName"\s*:\s*"mayurpagote"[^}]*"views"\s*:\s*(\d+)', out)
        if m:
            return int(m.group(1))
        views = [int(v) for v in re.findall(r'"views":(\d+)', out)]
        if views:
            return max(views)
    except Exception:
        pass
    return 14657

def get_youtube_views():
    try:
        cmd = ["curl", "-s", "-L", "-A", "Mozilla/5.0", "https://www.youtube.com/@IU-Studies/about"]
        if os.name == 'nt':
            cmd[0] = "curl.exe"
        out = subprocess.check_output(cmd, timeout=15).decode('utf-8', errors='ignore')
        m = re.findall(r'(\d[\d,]*)\s+views', out)
        for v in reversed(m):
            val = int(v.replace(',', ''))
            if val > 1000:
                return val
    except Exception:
        pass
    return 10273

def get_github_views():
    try:
        req = urllib.request.Request(
            'https://komarev.com/ghpvc/?username=Mayur-Pagote',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            svg = resp.read().decode('utf-8')
        m = re.findall(r'>(\d[\d,]+)<', svg)
        if m:
            return int(m[0].replace(',', ''))
    except Exception:
        pass
    return 7461

def generate_content():
    lc = get_leetcode_views()
    inst = get_instructables_views()
    yt = get_youtube_views()
    gh = get_github_views()

    lines = [
        "─────────────── Platform Views ───────────────",
        f"LeetCode                      {lc:>8,} views",
        f"Instructables               {inst:>8,} views",
        f"YouTube                       {yt:>8,} views",
        f"GitHub                        {gh:>8,} views"
    ]
    return "\n".join(lines) + "\n"

def update_gist(gist_id, token, content):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Platform-Views-Gist-Updater"
    }

    get_req = urllib.request.Request(f"https://api.github.com/gists/{gist_id}", headers=headers)
    with urllib.request.urlopen(get_req) as resp:
        gist_data = json.loads(resp.read().decode("utf-8"))

    files = gist_data.get("files", {})
    filename = list(files.keys())[0] if files else "👁️ Platform Views"

    patch_body = json.dumps({
        "description": "👁️ Platform Views",
        "files": {
            filename: {
                "content": content
            }
        }
    }).encode("utf-8")

    patch_req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        data=patch_body,
        headers=headers,
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req) as resp:
        print(f"Successfully updated Platform Views in '{filename}'")

def main():
    content = generate_content()
    print("Generated Platform Views Content:")
    print(content)

    if not GIST_ID or not GH_TOKEN:
        print("VIEWS_GIST_ID or GH_GIST_TOKEN not set. Skipping update.")
        return

    update_gist(GIST_ID, GH_TOKEN, content)

if __name__ == "__main__":
    main()
