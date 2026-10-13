import json
import os
import subprocess
import urllib.error
import urllib.request
import xml.sax.saxutils as saxutils

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNER = "The-last-signal-project"
REPO = "The-last-signal-"

API = f"https://api.github.com/repos/{OWNER}/{REPO}"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path("stats/repository-stats.svg")


# --------------------------------------------------
# GIT
# --------------------------------------------------

def git(*args):
    """Execute une commande Git dans le dépôt courant."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_git_stats():
    """Calcule les statistiques depuis l'historique Git."""

    now = datetime.now(timezone.utc)
    start = now - timedelta(weeks=52)

    since = start.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # Tous les commits des 52 dernières semaines.
    commit_dates = git(
        "log",
        f"--since={since}",
        "--format=%cI",
    ).splitlines()

    # Répartition des commits par semaine.
    weekly = [0] * 52

    for date_string in commit_dates:
        try:
            date = datetime.fromisoformat(
                date_string.replace("Z", "+00:00")
            )
            weeks_ago = (now - date).days // 7

            if 0 <= weeks_ago < 52:
                weekly[51 - weeks_ago] += 1
        except ValueError:
            continue

    # Ajouts et suppressions sur la même période.
    numstat = git(
        "log",
        f"--since={since}",
        "--numstat",
        "--format=",
    )

    additions = 0
    deletions = 0

    for line in numstat.splitlines():
        fields = line.split("\t")

        if len(fields) != 3:
            continue

        added, deleted, _filename = fields

        # Les fichiers binaires ne possèdent pas de numstat numérique.
        if added.isdigit() and deleted.isdigit():
            additions += int(added)
            deletions += int(deleted)

    # Contributeurs uniques sur tout l'historique disponible.
    author_names = git(
        "log",
        "--format=%aN",
    ).splitlines()

    contributors = {
        name.strip()
        for name in author_names
        if name.strip()
    }

    return {
        "commits": len(commit_dates),
        "weekly": weekly,
        "additions": additions,
        "deletions": deletions,
        "contributors": len(contributors),
    }


# --------------------------------------------------
# API GITHUB : INFORMATIONS DU DEPOT
# --------------------------------------------------

def get_repo_info():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "The-Last-Signal-Stats",
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(API, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        raise RuntimeError(
            f"Impossible de récupérer les informations du dépôt : {error}"
        ) from error


# --------------------------------------------------
# SVG
# --------------------------------------------------

def esc(value):
    return saxutils.escape(str(value))


def text(x, y, value, size=12, color="#c9d1d9",
         weight="normal", anchor="start"):
    return (
        f'<text x="{x}" y="{y}" '
        f'fill="{color}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" '
        f'font-weight="{weight}" '
        f'text-anchor="{anchor}">'
        f'{esc(value)}</text>'
    )


def rect(x, y, width, height, fill, radius=10, stroke=None):
    border = f' stroke="{stroke}"' if stroke else ""

    return (
        f'<rect x="{x}" y="{y}" '
        f'width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}"{border}/>'
    )


def fmt(value):
    return f"{value:,}"


def generate_svg(stats, repo):
    width, height = 920, 450

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<title>The Last Signal — Repository Statistics</title>',
        '<desc>Statistiques du dépôt uniquement.</desc>',
        rect(0, 0, width, height, "#0d1117", 18),

        text(30, 42, "The Last Signal", 25, "#f0f6fc", "bold"),
        text(30, 64, "REPOSITORY ANALYTICS", 11, "#8b949e"),
        text(
            890, 42, f"{OWNER}/{REPO}",
            10, "#8b949e", anchor="end"
        ),
    ]

    cards = [
        ("COMMITS · 52 WEEKS", fmt(stats["commits"]), "#58a6ff"),
        ("CONTRIBUTORS", fmt(stats["contributors"]), "#3fb950"),
        ("LINES ADDED · 52 WEEKS", fmt(stats["additions"]), "#3fb950"),
        ("LINES DELETED · 52 WEEKS", fmt(stats["deletions"]), "#f85149"),
        ("STARS", fmt(repo.get("stargazers_count", 0)), "#d29922"),
        ("FORKS", fmt(repo.get("forks_count", 0)), "#bc8cff"),
    ]

    card_width = 276
    card_height = 72
    start_x = 24
    start_y = 82
    gap_x = 22
    gap_y = 12

    for index, (label, value, color) in enumerate(cards):
        col = index % 3
        row = index // 3

        x = start_x + col * (card_width + gap_x)
        y = start_y + row * (card_height + gap_y)

        parts.append(rect(
            x, y, card_width, card_height,
            "#161b22", 10, "#30363d"
        ))

        parts.append(text(
            x + 15, y + 23, label,
            10, "#8b949e", "bold"
        ))

        parts.append(text(
            x + 15, y + 53, value,
            22, color, "bold"
        ))

    # Activité des 12 dernières semaines.
    parts.append(text(
        30, 265, "Weekly commits · last 12 weeks",
        14, "#c9d1d9", "bold"
    ))

    bars = stats["weekly"][-12:]
    max_bar = max(bars, default=0) or 1

    bar_width = 45
    gap = 25
    base_y = 370

    for index, value in enumerate(bars):
        x = 38 + index * (bar_width + gap)
        bar_height = max(2, int(68 * value / max_bar))
        y = base_y - bar_height

        parts.append(rect(
            x, y, bar_width, bar_height,
            "#388bfd", 5
        ))

        parts.append(text(
            x + bar_width / 2,
            y - 6,
            value,
            10,
            "#c9d1d9",
            anchor="middle",
        ))

    language = repo.get("language") or "Not detected"
    issues = repo.get("open_issues_count", 0)

    parts.append(text(
        30, 408,
        f"Main language: {language}",
        11, "#8b949e"
    ))

    parts.append(text(
        890, 408,
        f"Open issues: {issues}",
        11, "#8b949e", anchor="end"
    ))

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    parts.append(text(
        30, 432,
        f"Updated: {updated}",
        10, "#8b949e"
    ))

    parts.append(text(
        890, 432,
        "Data from Git history + GitHub API",
        10, "#8b949e", anchor="end"
    ))

    parts.append("</svg>")

    return "\n".join(parts)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    print(f"Repository: {OWNER}/{REPO}")

    # Vérifie que l'on est bien dans un dépôt Git.
    git("rev-parse", "--is-inside-work-tree")

    stats = get_git_stats()
    repo = get_repo_info()

    print("Commits (52 weeks):", stats["commits"])
    print("Contributors (all history):", stats["contributors"])
    print("Lines added (52 weeks):", stats["additions"])
    print("Lines deleted (52 weeks):", stats["deletions"])
    print("Stars:", repo.get("stargazers_count", 0))
    print("Forks:", repo.get("forks_count", 0))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(generate_svg(stats, repo), encoding="utf-8")

    print(f"SVG generated: {OUT}")


if __name__ == "__main__":
    main()
