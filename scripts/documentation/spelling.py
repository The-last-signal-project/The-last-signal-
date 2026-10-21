from pathlib import Path
import re

def check_spelling():
    """
    Analyse le fichier produit par CSpell.
    Retourne un score, les détails et les problèmes détectés.
    """

    report = Path("reports/docs/cspell.txt")

    result = {
        "score": 10,
        "max_score": 10,
        "results": {},
        "problems": [],
    }

    if not report.exists():
        result["results"]["status"] = "Aucun rapport CSpell"
        return result

    lines = report.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    regex = re.compile(
        r"^(.*?):(\d+):(\d+)\s*-\s*Unknown word\s*\((.*?)\)"
    )

    for line in lines:

        m = regex.match(line.strip())

        if not m:
            continue

        file, row, col, word = m.groups()

        result["problems"].append({
            "file": file,
            "severity": "warning",
            "module": "spelling",
            "message": f"Mot inconnu : '{word}'",
            "line": int(row),
            "column": int(col),
            "word": word,
        })

    nb = len(result["problems"])

    result["results"]["unknown_words"] = nb

    # -1 point par faute jusqu'à 10
    result["score"] = max(0, 10 - nb)

    return result
