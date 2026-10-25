#!/usr/bin/env python3
"""Update LeetCode Stats Gist for GitHub Pinned Gist card."""

import json
import os
import sys
import urllib.request

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

USERNAME = "mayurpagote"
GIST_ID = os.environ.get("LEETCODE_GIST_ID")
GH_TOKEN = os.environ.get("GH_GIST_TOKEN")

GRAPHQL_QUERY = """
query userProblemsSolved($username: String!) {
  allQuestionsCount {
    difficulty
    count
  }
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
    }
  }
}
"""

def fetch_leetcode_stats(username):
    req_body = json.dumps({
        "query": GRAPHQL_QUERY,
        "variables": {"username": username}
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=req_body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    
    data = res.get("data", {})
    all_qs = {item["difficulty"]: item["count"] for item in data.get("allQuestionsCount", [])}
    user = data.get("matchedUser", {})
    if not user:
        raise ValueError(f"User {username} not found on LeetCode")
    
    submits = {item["difficulty"]: item["count"] for item in user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])}
    ranking = user.get("profile", {}).get("ranking", 0)
    
    return {
        "all_questions": all_qs,
        "solved": submits,
        "ranking": ranking
    }

def make_bar(percent, bar_len=18):
    filled = round((percent / 100.0) * bar_len)
    filled = max(0, min(bar_len, filled))
    return "█" * filled + "░" * (bar_len - filled)

def generate_content(stats):
    ranking_str = f"Rank #{stats['ranking']:,}" if stats['ranking'] else ""
    header_title = "Problems Solved"
    header_space = 50 - len(header_title) - len(ranking_str)
    header_line = header_title + (" " * max(1, header_space)) + ranking_str

    rows = [header_line]

    categories = [
        ("🟢 Easy",   "   ", "Easy"),
        ("🟡 Medium", " ",   "Medium"),
        ("🔴 Hard",   "   ", "Hard"),
        ("⚪ Total",  "  ",  "All"),
    ]

    for label, pad, key in categories:
        solved = stats["solved"].get(key, 0)
        total = stats["all_questions"].get(key, 1)
        pct = (solved / total * 100.0) if total else 0.0
        bar = make_bar(pct, 18)
        row = f"{label}{pad} {solved:>4} / {total:>4}  {bar}  {pct:>5.1f}%"
        rows.append(row)

    return "\n".join(rows) + "\n"

def update_gist(gist_id, token, content):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "LeetCode-Stats-Gist-Updater"
    }

    # Fetch gist to discover the exact filename
    get_req = urllib.request.Request(f"https://api.github.com/gists/{gist_id}", headers=headers)
    with urllib.request.urlopen(get_req) as resp:
        gist_data = json.loads(resp.read().decode("utf-8"))

    files = gist_data.get("files", {})
    filename = list(files.keys())[0] if files else "LeetCode Stats"

    # Patch the gist
    patch_body = json.dumps({
        "description": "📊 LeetCode Stats (Auto-updated)",
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
        print(f"Successfully updated gist {gist_id} with file '{filename}'")

def main():
    print(f"Fetching LeetCode stats for '{USERNAME}'...")
    stats = fetch_leetcode_stats(USERNAME)
    content = generate_content(stats)
    print("\nGenerated Gist Content:")
    print(content)

    if not GIST_ID or not GH_TOKEN:
        print("LEETCODE_GIST_ID or GH_GIST_TOKEN not set. Skipping update.")
        return

    update_gist(GIST_ID, GH_TOKEN, content)

if __name__ == "__main__":
    main()
