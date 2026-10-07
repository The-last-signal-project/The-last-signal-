import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import traceback

REPORT_DIR = Path("reports/project")


def generate_problems_md():
    problems_file = REPORT_DIR / "problems.json"

    if not problems_file.exists():
        return

    problems = json.loads(problems_file.read_text(encoding="utf-8"))

    errors = sum(1 for p in problems if p["severity"] == "error")
    warnings = sum(1 for p in problems if p["severity"] == "warning")

    by_file = defaultdict(list)

    for p in problems:
        by_file[p["file"]].append(p)

    md = []

    md.append("# Documentation Problems\n\n")
    md.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")

    md.append("## Summary\n\n")
    md.append("|Type|Count|\n")
    md.append("|---|---:|\n")
    md.append(f"|Errors|{errors}|\n")
    md.append(f"|Warnings|{warnings}|\n")
    md.append(f"|**Total**|**{len(problems)}**|\n\n")

    md.append("---\n\n")

    for filename in sorted(by_file):

        md.append(f"# {filename}\n\n")

        for p in by_file[filename]:

            

            md.append(f"## {p['severity'].capitalize()}\n\n")
            md.append(f"- **Module :** {p['module']}\n")
            md.append(f"- **Message :** {p['message']}\n")

            extras = {
                k: v
                for k, v in p.items()
                if k not in ("file", "severity", "module", "message")
            }

            for key, value in extras.items():
                md.append(f"- **{key} :** {value}\n")

            md.append("\n")

        md.append("---\n\n")
        

    (REPORT_DIR / "problems.md").write_text(
        "".join(md),
        encoding="utf-8",
    )
    print("fichier md généré")
    

try:
    generate_problems_md()
except Exception:
    print(traceback.format_exc())
