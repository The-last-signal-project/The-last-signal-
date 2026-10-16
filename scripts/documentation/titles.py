import re
from .problem import add_problem
from utils.file_chercheur import iter_files
MAX_SCORE = 15

SCORES = {
    "single_h1": 3,
    "heading_order": 3,
    "heading_spacing": 2,
    "empty_titles": 2,
    "title_length": 2,
    "duplicate_titles": 3,
}


def check_titles():

    files = list(iter_files("*.md"))

    if not files:
        return {
            "score": 0,
            "max_score": MAX_SCORE,
            "results": {},
            "problems": [{
                "file": file,
                "severity": "warning",
                "message": "Aucun fichier Markdown trouvé."
            }]
        }

    problems = []
    results = {}

    results["single_h1"] = check_single_h1(files, problems)
    results["heading_order"] = check_heading_order(files, problems)
    results["heading_spacing"] = check_heading_spacing(files, problems)
    results["empty_titles"] = check_empty_titles(files, problems)
    results["title_length"] = check_title_length(files, problems)
    results["duplicate_titles"] = check_duplicate_titles(files, problems)
    score = sum(results.values())
    if score < 0:
        score = 0
    return {
        "score": score,
        "max_score": MAX_SCORE,
        "results": results,
        "problems": problems
    }



def check_single_h1(files, problems):
    score = SCORES["single_h1"]

    for file in files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        h1 = len(re.findall(r"^#\s+", text, flags=re.MULTILINE))

        if h1 != 1:
            add_problem (problems,file,"error",f"{file}: contient {h1} titres H1 (1 attendu).")
            
            score = 0

    return score


def check_heading_order(files, problems):
    score = SCORES["heading_order"]

    for file in files:
        previous = 0

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1
        ):
            if not line.startswith("#"):
                continue

            level = len(line) - len(line.lstrip("#"))

            if previous and level > previous + 1:
                add_problem (problems,file,"warning",f"{file}:{line_no} saut de niveau H{previous} → H{level}.")
                score = 0

            previous = level

    return score


def check_heading_spacing(files, problems):
    score = SCORES["heading_spacing"]

    for file in files:
        lines = file.read_text(
            encoding="utf-8",
            errors="ignore"
        ).splitlines()

        for i, line in enumerate(lines):

            if line.startswith("#"):

                if i > 0 and lines[i - 1].strip() != "":
                    add_problem (problems,file,"warning",f"{file}:{i+1} titre sans ligne vide avant.")
                    score = 0

                if i < len(lines) - 1 and lines[i + 1].strip() == "":
                    continue

    return score


def check_empty_titles(files, problems):
    score = SCORES["empty_titles"]

    for file in files:

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1
        ):

            if re.match(r"^#+\s*$", line):
                add_problem (problems,file,"error",f"{file}:{line_no} titre vide.")
                
                score = 0

    return score


def check_title_length(files, problems):
    score = SCORES["title_length"]

    for file in files:

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1
        ):

            if line.startswith("#"):

                title = re.sub(r"^#+\s*", "", line)

                if len(title) > 80:
                    add_problem (problems,file,"warning",f"{file}:{line_no} titre très long ({len(title)} caractères).")
                    
                    score = 0

    return score


def check_duplicate_titles(files, problems):
    score = SCORES["duplicate_titles"]

    titles = {}

    for file in files:

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1
        ):

            if line.startswith("#"):

                title = re.sub(r"^#+\s*", "", line).strip().lower()

                if title in titles:
                    add_problem (problems,file,"warning",f"{file}:{line_no} titre dupliqué (déjà présent dans {titles[title]}).")
                    
                    score = 0

                else:
                    titles[title] = f"{file}:{line_no}"

    return score
