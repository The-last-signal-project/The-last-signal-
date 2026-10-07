from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    "reports",
    "dashboard",
    "database",
    "target",
    ".venv",
    "venv",
}

def iter_files(pattern: str):
    for path in Path(".").rglob(pattern):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path
