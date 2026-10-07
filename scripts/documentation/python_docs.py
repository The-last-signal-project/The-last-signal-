from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path.cwd()


def check_python_docs() -> dict:
    """
    Analyse la qualité de la documentation des fichiers Python.

    Vérifications :
        - docstring de module
        - docstring des classes
        - docstring des fonctions publiques
        - annotations de type
        - TODO / FIXME
        - longueur des fonctions
    """

    MAX_SCORE = 30

    problems = []

    python_files = [
        f
        for f in ROOT.rglob("*.py")
        if not any(
            p in {
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                ".mypy_cache",
                ".pytest_cache",
                "vendor"
            }
            for p in f.parts
        )
    ]

    stats = {
        "modules": 0,
        "classes": 0,
        "functions": 0,
        "documented_modules": 0,
        "documented_classes": 0,
        "documented_functions": 0,
        "typed_functions": 0,
        "todo": 0,
        "long_functions": 0,
    }

    score = MAX_SCORE

    for file in python_files:

        stats["modules"] += 1

        try:
            source = file.read_text(encoding="utf-8")
            tree = ast.parse(source)

        except Exception as e:
            problems.append(
                {
                    "file": str(file),
                    "severity": "error",
                    "message": f"Impossible d'analyser le fichier : {e}",
                    "module": "python_docs",
                }
            )
            score -= 2
            continue

        # -----------------------
        # Docstring du module
        # -----------------------

        if ast.get_docstring(tree):
            stats["documented_modules"] += 1
        else:
            problems.append(
                {
                    "file": str(file),
                    "severity": "warning",
                    "message": "Le module ne possède pas de docstring.",
                    "module": "python_docs",
                }
            )
            score -= 0.25

        # -----------------------
        # TODO / FIXME
        # -----------------------

        for word in ("TODO", "FIXME", "XXX", "HACK"):

            if word in source:
                stats["todo"] += 1

                problems.append(
                    {
                        "file": str(file),
                        "severity": "info",
                        "message": f"{word} présent dans le fichier.",
                        "module": "python_docs",
                    }
                )

        # -----------------------
        # Analyse AST
        # -----------------------

        for node in ast.walk(tree):

            # ---------- Classes ----------

            if isinstance(node, ast.ClassDef):

                stats["classes"] += 1

                if ast.get_docstring(node):

                    stats["documented_classes"] += 1

                else:

                    problems.append(
                        {
                            "file": str(file),
                            "severity": "warning",
                            "message": f"La classe '{node.name}' ne possède pas de docstring.",
                            "module": "python_docs",
                        }
                    )

                    score -= 0.10

            # ---------- Fonctions ----------

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                if node.name.startswith("_"):
                    continue

                stats["functions"] += 1

                # Docstring

                if ast.get_docstring(node):

                    stats["documented_functions"] += 1

                else:

                    problems.append(
                        {
                            "file": str(file),
                            "severity": "warning",
                            "message": f"La fonction '{node.name}'ligne {node.lineno} ne possède pas de docstring.",
                            "module": "python_docs",
                        }
                    )

                    score -= 0.10

                # Type hints
                args = (
        node.args.args
        + node.args.posonlyargs
        + node.args.kwonlyargs
    )

    
                has_types = (
                    node.returns is not None
                    and all(arg.annotation is not None for arg in args)
                )

                if has_types:

                    stats["typed_functions"] += 1

                else:

                    problems.append(
                        {
                            "file": str(file),
                            "severity": "warning",
                            "message": f"La fonction '{node.name}' ne possède pas d'annotations de type.",
                            "module": "python_docs",
                        }
                    )

                    score -= 0.05

                # Longueur

                if (
                    hasattr(node, "end_lineno")
                    and node.end_lineno
                    and node.end_lineno - node.lineno > 80
                ):

                    stats["long_functions"] += 1

                    problems.append(
                        {
                            "file": str(file),
                            "severity": "warning",
                            "message": f"La fonction '{node.name}' dépasse 80 lignes.",
                            "module": "python_docs",
                        }
                    )

                    score -= 0.05
    print(f"score python={score}")
    score = max(0, min(MAX_SCORE, round(score)))
    
    return {
        "score": score,
        "max_score": MAX_SCORE,
        "results": stats,
        "problems": problems,
    }
