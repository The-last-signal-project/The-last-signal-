from pathlib import Path
def add_problem(problems: list[dict], file: Path | str, severity: str, message: str):
    problems.append({
        "file": file.as_posix(),
        "severity": severity,
        "message": message
    })
