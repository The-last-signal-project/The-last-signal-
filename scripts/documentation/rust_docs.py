import os
import re
from pathlib import Path
from typing import Any, Dict, List


max_score = 30


def check_rust_docs() -> Dict[str, Any]:
    """
    Vérifie la qualité de la documentation dans les fichiers Rust.

    Returns:
        Dict avec:
        - score: Note globale
        - max_score: Score maximum possible
        - results: Détails par fichier
        - problems: Liste des problèmes trouvés
    """

    rust_files = []
    base_dir = Path.cwd()

    exclude_dirs = {
        "target",
        ".git",
        "__pycache__",
        "venv",
        "vendor"
    }

    # Trouve tous les fichiers .rs
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [
            d for d in dirs
            if d not in exclude_dirs
        ]

        for file in files:
            if file.endswith(".rs"):
                rust_files.append(
                    os.path.join(root, file)
                )

    print("fichier:")
    print(rust_files)

    if not rust_files:
        return {
            "score": 0,
            "max_score": max_score,
            "results": {"files_checked": 0},
            "problems": [],
        }

    problems: List[Dict[str, Any]] = []
    total_issues = 0
    total_elements = 0

    # Détection des éléments Rust.
    #
    # pub
    # pub(crate)
    # pub(super)
    # pub(self)
    # pub(in crate::module)
    #
    # async est également pris en charge pour les fonctions.
    patterns = {
        "function": (
            r"^\s*"
            r"(?:pub(?:\([^)]*\))?\s+)?"
            r"(?:async\s+)?"
            r"fn\s+(\w+)"
        ),
        "struct": (
            r"^\s*"
            r"(?:pub(?:\([^)]*\))?\s+)?"
            r"struct\s+(\w+)"
        ),
        "enum": (
            r"^\s*"
            r"(?:pub(?:\([^)]*\))?\s+)?"
            r"enum\s+(\w+)"
        ),
        "impl": (
            r"^\s*"
            r"impl\s+([\w<>=, ]+)"
        ),
        "mod": (
            r"^\s*"
            r"(?:pub(?:\([^)]*\))?\s+)?"
            r"mod\s+(\w+)"
        ),
        "trait": (
            r"^\s*"
            r"(?:pub(?:\([^)]*\))?\s+)?"
            r"trait\s+(\w+)"
        ),
    }

    score = max_score

    for file_path in rust_files:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            content = f.read()

        lines = content.split("\n")
        file_problems = []
        file_elements = 0

        # Analyse chaque ligne
        for i, line in enumerate(lines):

            line = line.strip()

            if not line:
                continue

            for element_type, pattern in patterns.items():

                match = re.match(pattern, line)

                if not match:
                    continue

                # Le nom de l'élément est dans le groupe 1.
                element_name = match.group(1)

                total_elements += 1
                file_elements += 1

                has_doc = False

                # Vérifie la ligne précédente
                if i > 0:

                    prev_line = lines[i - 1].strip()

                    if (
                        prev_line.startswith("///")
                        or prev_line.startswith("/**")
                        or prev_line.startswith("/*!")
                    ):
                        has_doc = True

                if not has_doc:

                    total_issues += 1
                    score -= 1

                    problems.append(
                        {
                            "file": file_path,
                            "line": i + 1,
                            "severity": "warning",
                            "message": (
                                f"{element_type.capitalize()} "
                                f"'{element_name}' "
                                "sans documentation"
                            ),
                            "suggestion": (
                                f"Ajoutez /// avant cette "
                                f"{element_type}"
                            ),
                        }
                    )

                break

        if file_problems:
            problems.extend(file_problems)

    # Calcul du score en pourcentage (0-20)
    if score < 0:
        score = 0
    return {
        "score": int(score),
        "max_score": max_score,
        "results": {
            "files_checked": len(rust_files),
            "total_elements": total_elements,
            "elements_without_docs": total_issues,
        },
        "problems": problems,
    }