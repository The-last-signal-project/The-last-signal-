'''Test de sécurité rust'''
from __future__ import annotations
import re
from pathlib import Path


ROOT = Path.cwd().resolve()

IGNORED_DIRECTORIES = {
    ".git",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
}


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "unsafe block/function",
        re.compile(
            r"\bunsafe\b"
        ),
    ),
    (
        "Command execution",
        re.compile(
            r"\b(?:Command|std::process::Command)::"
        ),
    ),
    (
        "Shell invocation",
        re.compile(
            r"(?i)\b(?:sh|bash|cmd|powershell)\b"
        ),
    ),
    (
        "Potential dynamic SQL",
        re.compile(
            r"(?i)\b(?:execute|query|query_as|prepare)\s*\("
        ),
    ),
    (
        "Potential unwrap",
        re.compile(
            r"\.unwrap\s*\("
        ),
    ),
    (
        "Potential expect",
        re.compile(
            r"\.expect\s*\("
        ),
    ),
]


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    return any(
        part in IGNORED_DIRECTORIES
        for part in relative.parts
    )


def scan_file(
    path: Path,
) -> list[tuple[int, str]]:

    try:
        text = path.read_text(
            encoding="utf-8"
        )

    except (
        UnicodeDecodeError,
        OSError,
    ):
        return []

    findings: list[tuple[int, str]] = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):

        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith("//")
        ):
            continue

        for name, pattern in PATTERNS:

            if pattern.search(line):
                findings.append(
                    (
                        line_number,
                        name,
                    )
                )

    return findings


def main() -> int:
    print("=== RUST SECURITY SCAN ===")

    files = 0
    findings = 0

    for path in ROOT.rglob("*.rs"):

        if should_ignore(path):
            continue

        files += 1

        for line, name in scan_file(path):

            relative = path.relative_to(ROOT)

            print(
                f"[WARN] {relative}:{line} - {name}"
            )

            findings += 1

    print()
    print(
        f"Rust files inspected: {files}"
    )

    if findings == 0:
        print(
            "[PASS] No configured Rust security "
            "patterns detected."
        )
        return 0

    print(
        f"[WARN] {findings} Rust security "
        "review point(s) detected."
    )

    # Ce scanner produit des points de revue.
    # cargo-audit / CodeQL / cargo-deny sont les
    # mécanismes qui doivent déterminer les vulnérabilités
    # critiques de dépendances.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
