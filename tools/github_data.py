"""Fetches the public GitHub data the assets are built from (no token required;
GITHUB_TOKEN is used when present to avoid rate limits)."""
import datetime as dt
import json
import os
import re
import urllib.request

UA = {"User-Agent": "profile-readme-builder"}


def _get(url, api=False):
    headers = dict(UA)
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read().decode("utf-8")


def repos(user):
    """Public, non-fork, non-archived repos – without the profile repo itself."""
    data = json.loads(_get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner", api=True))
    out = [r for r in data if not r["fork"] and not r["archived"] and r["name"].lower() != user.lower()]
    return sorted(out, key=lambda r: r["pushed_at"], reverse=True)


def profile(user):
    return json.loads(_get(f"https://api.github.com/users/{user}", api=True))


def contributions(user):
    """[(date, level 0-4, count)] for the last year, from the public calendar."""
    page = _get(f"https://github.com/users/{user}/contributions")
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', page):
        n = re.match(r"\s*([\d,]+) contribution", m.group(2))
        counts[m.group(1)] = int(n.group(1).replace(",", "")) if n else 0
    days = []
    for m in re.finditer(r"<td[^>]*ContributionCalendar-day[^>]*>", page):
        tag = m.group(0)
        date = re.search(r'data-date="([\d-]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        cid = re.search(r'id="([^"]+)"', tag)
        if date and level:
            days.append((dt.date.fromisoformat(date.group(1)), int(level.group(1)),
                         counts.get(cid.group(1), 0) if cid else 0))
    if not days:
        raise SystemExit("no contribution data found – page layout may have changed")
    return sorted(days)


def release_stats(user, repo_list):
    """{repo: (release_count, package_downloads)}. Manifest files (module.json /
    manifest.json) are skipped: Foundry and Obsidian fetch them on every update
    check, so only real packages (zip, main.js, …) are counted as downloads."""
    out = {}
    for r in repo_list:
        rels = json.loads(_get(f"https://api.github.com/repos/{user}/{r['name']}/releases?per_page=100", api=True))
        out[r["name"]] = (len(rels), sum(a["download_count"] for rel in rels for a in rel.get("assets", [])
                                         if not a["name"].lower().endswith(".json")))
    return out


def downloads(user, repo_list):
    return sum(d for _, d in release_stats(user, repo_list).values())
