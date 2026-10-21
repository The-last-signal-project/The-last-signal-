import os
from typing import Dict, Any
from pathlib import Path
def check_organization() -> Dict[str, Any]:
    base_dir = Path.cwd()
    print("Base dir :", base_dir)
    print("Existe .github :", os.path.isdir(os.path.join(base_dir, ".github")))
    print("Existe .gitignore :", os.path.isfile(os.path.join(base_dir, ".gitignore")))

    score = 100
    problems = []

    expected_dirs = [
        "docs",
        "tests",
        ".github",
    ]

    expected_files = [
        "README.md",
        ".gitignore",
        "requirements.txt",
        ".markdownlint-cli2.jsonc",
        ".python-version",
        "pytest.ini",
        "README_ENG.md",
    ]

    bonus_files = [
        "LICENSE",
        "CONTRIBUTING.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "CODING_RULES.md",
        "SECURITY.md",
    ]

    ignore_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "target",
        "venv",
        ".venv",
        "server_rust",
    }

    # ------------------------
    # Dossiers importants
    # ------------------------

    for folder in expected_dirs:
        if not os.path.isdir(os.path.join(base_dir, folder)):
            score -= 5
            problems.append({
                "file": folder,
                "severity": "warning",
                "message": f"Dossier '{folder}' absent",
                "suggestion": f"Créer le dossier '{folder}'."
            })

    # ------------------------
    # Fichiers importants
    # ------------------------

    for file in expected_files:
        if not os.path.isfile(os.path.join(base_dir, file)):
            score -= 8
            problems.append({
                "file": file,
                "severity": "warning",
                "message": f"Fichier '{file}' absent",
                "suggestion": f"Créer le fichier '{file}'."
            })

    # ------------------------
    # Bonus documentation
    # ------------------------

    bonus = 0

    for file in bonus_files:
        if os.path.isfile(os.path.join(base_dir, file)):
            bonus += 1

    score += bonus
    score = min(score, 100)

    # ------------------------
    # Racine encombrée
    # ------------------------

    root_files = [
        f for f in os.listdir(base_dir)
        if not f.startswith(".")
    ]

    if len(root_files) > 25:
        score -= 5
        problems.append({
            "file": "",
            "severity": "info",
            "message": "La racine contient beaucoup de fichiers.",
            "suggestion": "Créer des dossiers pour mieux organiser le projet."
        })

    # ------------------------
    # Dossiers vides
    # ------------------------

    for root, dirs, files in os.walk(base_dir):

        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        if not dirs and not files:
            score -= 1

            problems.append({
                "file": root,
                "severity": "info",
                "message": "Dossier vide.",
                "suggestion": "Supprimer ou utiliser ce dossier."
            })

    # ------------------------
    # Fichiers temporaires
    # ------------------------

    temp_ext = (
        ".tmp",
        ".bak",
        ".old",
        ".orig",
    )

    for root, dirs, files in os.walk(base_dir):

        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:

            if file.endswith(temp_ext):

                score -= 1

                problems.append({
                    "file": os.path.join(root, file),
                    "severity": "warning",
                    "message": "Fichier temporaire trouvé.",
                    "suggestion": "Supprimer ce fichier."
                })

    score = max(0, score)

    return {
        "score": score,
        "max_score": 100,
        "results": {
            "bonus": bonus,
            "problems": len(problems)
        },
        "problems": problems,
      }
