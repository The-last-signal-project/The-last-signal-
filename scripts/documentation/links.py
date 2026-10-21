from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
MAX_SCORE = 15

SCORES = {
    "empty_links": 3,
    "local_links": 4,
    "external_links": 2,
    "anchors": 2,
    "images": 2,
    "duplicates": 2,
}


def check_links():
    files = [
        f
        for f in ROOT.rglob("*.md")
        if not any(
            p in {
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                ".mypy_cache",
                ".pytest_cache",
                "reports",
                "database",
                "dashboard",
                "server_rust",
                "vendor",
            }
            for p in f.parts
        )
    ]

    

    if not files:
        return {
            "score": 0,
            "max_score": MAX_SCORE,
            "results": {},
            "problems": [{
                "file": "",
                "severity": "warning",
                "message": "Aucun fichier Markdown trouvé."
            }]
        }

    problems = []
    results = {}

    results["empty_links"] = check_empty_links(files, problems)
    results["local_links"] = check_local_links(files, problems)
    results["external_links"] = check_external_links(files, problems)
    results["anchors"] = check_anchors(files, problems)
    results["images"] = check_images(files, problems)
    results["duplicates"] = check_duplicate_links(files, problems)
    if score < 0:
        score = 0
    return {
        "score": sum(results.values()),
        "max_score": MAX_SCORE,
        "results": results,
        "problems": problems
    }


def extract_links(file):

    text = file.read_text(encoding="utf-8", errors="ignore")

    

    links = []

    for line_number, line in enumerate(text.splitlines(), start=1):

        for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', line):

            links.append((line_number, match.group(1).strip()))

    return links


def check_empty_links(files, problems):

    score = SCORES["empty_links"]

    pattern = re.compile(r'!?\[[^\]]*\]\(\s*\)')

    for file in files:

        text = file.read_text(encoding="utf-8", errors="ignore")

        for line_number, line in enumerate(text.splitlines(), start=1):

            if pattern.search(line):

                problems.append({
                    "file": str(file),
                    "line": line_number,
                    "severity": "error",
                    "message": "Lien vide."
                })

                score = 0

    return score


def check_local_links(files, problems):

    score = SCORES["local_links"]

    for file in files:

        for line_number, link in extract_links(file):

            if (
                link.startswith(("http://", "https://", "#", "mailto:"))
                or link.startswith("data:")
            ):
                continue

            target = (file.parent / link).resolve()

            if not target.exists():

                problems.append({
                    "file": str(file),
                    "line": line_number,
                    "severity": "error",
                    "message": f"Fichier introuvable : {link}"
                })

                score = 0

    return score


def check_external_links(files, problems):

    score = SCORES["external_links"]

    pattern = re.compile(r"^https?://")

    count = 0

    for file in files:

        for _, link in extract_links(file):

            if pattern.match(link):
                count += 1

    if count == 0:

        problems.append({
            "file": "",
            "severity": "warning",
            "message": "Aucun lien externe trouvé."
        })

        score = 0

    return score


def check_anchors(files, problems):

    score = SCORES["anchors"]

    for file in files:

        for line_number, link in extract_links(file):

            if link == "#":

                problems.append({
                    "file": str(file),
                    "line": line_number,
                    "severity": "warning",
                    "message": "Ancre vide."
                })

                score = 0

    return score


def check_images(files, problems):

    score = SCORES["images"]

    pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')

    for file in files:

        text = file.read_text(encoding="utf-8", errors="ignore")

        for line_number, line in enumerate(text.splitlines(), start=1):

            for match in pattern.finditer(line):

                image = match.group(1)

                if image.startswith(("http://", "https://")):
                    continue

                target = (file.parent / image).resolve()

                if not target.exists():

                    problems.append({
                        "file": str(file),
                        "line": line_number,
                        "severity": "warning",
                        "message": f"Image introuvable : {image}"
                    })

                    score = 0

    return score


def check_duplicate_links(files, problems):

    score = SCORES["duplicates"]

    links = {}

    for file in files:

        for line_number, link in extract_links(file):

            if link in links:

                problems.append({
                    "file": str(file),
                    "line": line_number,
                    "severity": "info",
                    "message": f"Lien déjà utilisé dans {links[link]}"
                })

                score = 0

            else:

                links[link] = f"{file}:{line_number}"

    return score
