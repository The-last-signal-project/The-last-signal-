from pathlib import Path
import re
from typing import Any
from .problem import add_problem
MAX_SCORE = 50

SCORES = {
    "empty_files": 10,
    "encoding": 7,
    "line_length": 7,
    "trailing_spaces": 6,
    "code_blocks": 5,
    "lists": 5,
    "tables": 5,
    "html": 5,
}

HTML_TAGS = ("font", "center", "marquee")

IGNORED_DIRS = {
    ".git", ".github", ".venv", "venv", "__pycache__",
    "node_modules", "build", "dist", "target",
    "reports", ".pytest_cache", ".mypy_cache","server_rust"
}


import json

MARKDOWNLINT_REPORT = Path("reports/project/markdownlint.json")


def load_markdownlint_report():
    if not MARKDOWNLINT_REPORT.exists():
        return []

    try:
        with MARKDOWNLINT_REPORT.open(
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return []
def get_markdown_files() -> list[Path]:
    files = []
    for f in Path(".").rglob("*.md"):
        if is_ignored(f):
            continue
        files.append(f)
    return files


def is_ignored(path: str | Path) -> bool:
    path = Path(path)
    return any(part in IGNORED_DIRS for part in path.parts)


def check_markdown() -> dict[str, Any]:
    problems = []
    files = get_markdown_files()

    if not files:
        return {
            "score": 0,
            "max_score": MAX_SCORE,
            "results": {},
            "problems": [{
                "file": "",
                "severity": "error",
                "message": "Aucun fichier Markdown trouvé."
            }]
        }
    report = load_markdownlint_report()
    results = {
        "empty_files": check_empty_files(files, problems),
        "encoding": check_encoding(files, problems),
        "line_length": check_line_length(files, problems),
        "trailing_spaces": check_trailing_spaces(files, problems),
        "code_blocks": check_code_blocks(files, problems),
        "lists": check_lists(files, problems,report),
        "tables": check_tables(files, problems,report),
        "html": check_html(files, problems),
    }
    
    return {
        "score": max(0,sum(results.values())),
        "max_score": MAX_SCORE,
        "results": results,
        "problems": problems
    }


def check_empty_files(files, problems):
    empty = 0
    poor = 0
    for file in files:
        try:
            content = file.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            empty += 1
            add_problem(problems, file, "error", "Fichier illisible.")
            continue

        if not content:
            empty += 1
            add_problem(problems, file, "error", "Fichier vide.")
            continue

        lines = [l for l in content.splitlines() if l.strip()]
        if len(content) < 50 or len(lines) < 3:
            poor += 1
            add_problem(problems, file, "warning", "Contenu très faible.")

    penalty = empty + poor * 0.5
    ratio = max(0, 1 - penalty / len(files))
    return round(ratio * SCORES["empty_files"])


def check_encoding(files, problems):
    bad = 0
    for file in files:
        try:
            file.read_text(encoding="utf-8")
        except Exception:
            bad += 1
            add_problem(problems, file, "error", "Encodage UTF-8 invalide.")
    ratio = 1 if not files else max(0, 1 - bad / len(files))
    return round(ratio * SCORES["encoding"])


def check_line_length(files, problems):
    total = errors = 0
    for file in files:
        try:
            lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            total += 1
            if len(line) > 120:
                errors += 1
                add_problem(problems, file, "warning", f"Ligne {i} > 120 caractères.")
    if total == 0:
        return SCORES["line_length"]
    return max(0, round((1-errors/total)*SCORES["line_length"]))


def check_trailing_spaces(files, problems):
    total = errors = 0
    for file in files:
        if is_ignored(file):
            continue
        try:
            lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines,1):
            total += 1
            if line.endswith(" "):
                errors += 1
                add_problem(problems,file,"warning",f"Espace en fin de ligne ({i}).")
    if total==0:
        return SCORES["trailing_spaces"]
    return max(0, round((1-errors/total)*SCORES["trailing_spaces"]))


def check_code_blocks(files, problems):
    bad=0
    for file in files:
        if is_ignored(file):
            continue
        try:
            text=file.read_text(encoding="utf-8",errors="ignore")
        except Exception:
            continue
        if text.count("```") %2:
            bad+=1
            add_problem(problems,file,"error","Bloc de code non fermé.")
    ratio=max(0,1-bad/len(files))
    return round(ratio*SCORES["code_blocks"])


def check_lists(files, problems, report):

    errors = 0

    LIST_RULES = {
        "MD004",
        "MD005",
        "MD006",
        "MD007",
        "MD030",
        "MD032"
    }

    for issue in report:
        

        if is_ignored(issue.get("fileName", "")):
            continue

        rules = set(issue.get("ruleNames", []))

        if rules & LIST_RULES:

            errors += 1

            problems.append({
                "file": issue["fileName"],
                "severity": "warning",
                "message": issue["ruleDescription"]
            })

    if not files:
        return 0

    ratio = max(
        0,
        1 - errors / len(files)
    )

    return round(ratio * SCORES["lists"])


def check_tables(files, problems, report):

    errors = 0

    TABLE_RULES = {
        "MD055"
    }

    for issue in report:
        

        if is_ignored(issue.get("fileName", "")):
            continue

        rules = set(issue.get("ruleNames", []))

        if rules & TABLE_RULES:

            errors += 1

            problems.append({
                "file": issue["fileName"],
                "severity": "warning",
                "message": issue["ruleDescription"]
            })

    if not files:
        return 0

    ratio = max(
        0,
        1 - errors / len(files)
    )

    return round(ratio * SCORES["tables"])


def check_html(files, problems):
    bad=0
    for file in files:
        if is_ignored(file):
            continue
        try:
            text=file.read_text(encoding="utf-8",errors="ignore")
        except Exception:
            continue
        for tag in HTML_TAGS:
            if re.search(fr"<{tag}\b", text):
                bad+=1
                add_problem(problems,file,"warning",f"Balise <{tag}> déconseillée.")
    ratio=max(0,1-bad/len(files))
    return round(ratio*SCORES["html"])

