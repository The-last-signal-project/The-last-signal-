from .markdown import check_markdown
from .titles import check_titles
from .spelling import check_spelling
from .links import check_links
from .python_docs import check_python_docs
from .rust_docs import check_rust_docs
from .organization import check_organization

from .report import generate_report
import traceback
def generate_score():
    checks = {
    "markdown": check_markdown,
    "titles": check_titles,
    "spelling": check_spelling,
    "links": check_links,
    "python": check_python_docs,
    "rust": check_rust_docs,
    "organization": check_organization,

}

    scores = {}
    details = {}
    all_problems = []
    total={}

    for name, check in checks.items():
        try:
            result = check()
            if not isinstance(result, dict):
                raise TypeError(f"result doit être un dict, reçu {type(result).__name__}")
        except Exception as e:
            result={
            "score": 0,
            "max_score": 1,
            "results": {},
            "problems": [{
                "file": "",
                "severity": "error",
                "message": traceback.format_exc()
            }]}
        finally:
            scores[name] = result["score"]
            details[name] = result
            total[name]=result["max_score"]
            for problem in result["problems"]:
                problem["module"] = name

            all_problems.extend(result["problems"])
            import json
            for name, result in details.items():
                size = len(json.dumps(result, default=str))
                print(f"{name}: {size / 1024:.1f} KiB")
            print(f"Nombre total de problèmes : {len(all_problems)}")
    total_obtenu = sum(scores.values())/sum(total.values()) if sum(total.values())!=0 else sum(scores.values())/1
    total_obtenu*=100
    total_obtenu= int(round(total_obtenu))
    generate_report(total_obtenu,scores,details,all_problems)
    
    return total
