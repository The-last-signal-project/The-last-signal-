from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from collections import defaultdict

REPORT_DIR=Path("reports/project")
REPORT_DIR.mkdir(parents=True,exist_ok=True)

def _status(score: int) -> str:
    if score >= 90:
        return "Optimal"
    if score >= 80:
        return "Excellent"
    if score >= 70:
        return "Satisfaisant"
    if score >= 60:
        return "Bon"
    if score >= 50:
        return "Assez bon"
    if score >= 40:
        return "Médiocre"
    if score >= 30:
        return "Décevant"
    if score >= 20:
        return "Très décevant"
    if score >= 10:
        return "Mauvais"
    return "Très mauvais"



def generate_report(total:int,scores:dict[str,int],details:dict[str,Any],problems:list)->None:
    REPORT_DIR.mkdir(parents=True,exist_ok=True)
    
    summary={"generated":datetime.now().isoformat(),"score":total,"status":_status(total),"scores":scores,"problem_count":len(problems)}
    (REPORT_DIR/"score.txt").write_text(str(total),encoding="utf-8")
    (REPORT_DIR/"summary.json").write_text(json.dumps(summary,indent=4,ensure_ascii=False),encoding="utf-8")
    
    (REPORT_DIR/"score.json").write_text(json.dumps({**summary,"details":details},indent=4,ensure_ascii=False,default=str),encoding="utf-8")
    (REPORT_DIR/"problems.json").write_text(json.dumps(problems,indent=4,ensure_ascii=False,default=str),encoding="utf-8")
    md = [
    "Documentation Quality Report\n\n",
    f"**Date :** {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
    f"# {total}/100\n\n",
    f"**Statut :** {_status(total)}\n\n",
    "## Résultats\n"
    "|Module|Score|\n"
    "|---|---:|\n",]
    for k, v in scores.items():
        md.append(f"|{k}|**{v}**|\n")
        md.append("\n## Problèmes\n")
    par_fichier = defaultdict(list)


    
    if problems:
        for i,problem in enumerate(problems):
            if not isinstance(problem, dict):
                raise TypeError(f"Élément {i} n'est pas un dict : {problem!r}")

            if "file" not in problem:
                raise KeyError(
            f"Élément {i} ne contient pas 'file'. "
            f"Clés présentes : {list(problem.keys())}. "
            f"Valeur : {problem!r}"
        )

            
        for problem in problems:
            par_fichier[str(problem["file"])].append(problem)
        for fichier, erreurs in sorted(par_fichier.items()):
            md.append(f"# 📄 {fichier}\n\n")
            for erreur in erreurs:
                icone = "❌" if erreur["severity"] == "error" else "⚠️"
                md.append(f"## {icone} {erreur['severity'].capitalize()}\n")
                md.append(f"- **Module :** {erreur['module']}\n")
                md.append(f"- **Message :** {erreur['message']}\n\n")
                for key, value in erreur.items():
                    if key in ("file", "severity", "message"):
                        continue
                    md.append(f"- **{key} :** {value}\n")
                    md.append("\n")


    else:
        md.append("Aucun problème détecté.\n")
    (REPORT_DIR/"score.md").write_text("".join(md),encoding="utf-8")
