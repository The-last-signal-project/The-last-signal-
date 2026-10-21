'''Vérification des secrets'''
from __future__ import annotations
import re
from pathlib import Path


ROOT = Path.cwd().resolve()

IGNORED_DIRECTORIES = {
    ".git",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "reports",
}

IGNORED_FILES = {
    ".security-baseline.json",
}

MAX_FILE_SIZE = 2 * 1024 * 1024


PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "Private key",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
        ),
    ),
    (
        "AWS access key",
        re.compile(
            r"\bAKIA[0-9A-Z]{16}\b"
        ),
    ),
    (
        "GitHub token",
        re.compile(
            r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"
        ),
    ),
    (
        "Generic API key",
        re.compile(
            r"(?i)\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
        ),
    ),
    (
        "Generic secret",
        re.compile(
            r"(?i)\b(?:secret|client_secret|app_secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"
        ),
    ),
    (
        "Password assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]"
        ),
    ),
    (
        "Bearer token",
        re.compile(
            r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}"
        ),
    ),
    (
        "JWT",
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"
        ),
    ),
    (
        "Database credential URL",
        re.compile(
            r"(?i)\b(?:postgres|postgresql|mysql|mongodb|redis)://[^/\s:@]+:[^@\s]+@"
        ),
    ),
]


SAFE_TEST_VALUES = {
    "FAKE_TEST_SECRET",
    "FAKE_API_KEY",
    "TEST_SECRET",
    "YOUR_API_KEY",
    "YOUR_SECRET",
    "CHANGE_ME",
    "CHANGEME",
    "EXAMPLE",
    "EXAMPLE_KEY",
    "EXAMPLE_SECRET",
}


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    if path.name in IGNORED_FILES:
        return True

    return any(
        part in IGNORED_DIRECTORIES
        for part in relative.parts
    )


def looks_textual(data: bytes) -> bool:
    if b"\x00" in data:
        return False

    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def mask(value: str) -> str:
    if len(value) <= 8:
        return "***"

    return (
        value[:3]
        + "***"
        + value[-3:]
    )


def scan_file(path: Path) -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []

    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return findings

        data = path.read_bytes()

        if not looks_textual(data):
            return findings

        text = data.decode("utf-8", errors="replace")

    except OSError:
        return findings

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        stripped = line.strip()

        if not stripped:
            continue

        for name, pattern in PATTERNS:

            match = pattern.search(line)

            if not match:
                continue

            matched = match.group(0)

            if any(
                safe.lower() in matched.lower()
                for safe in SAFE_TEST_VALUES
            ):
                continue

            findings.append(
                (
                    name,
                    line_number,
                    mask(matched),
                )
            )

    return findings


def main() -> int:
    print("=== SECRET SECURITY SCAN ===")

    total = 0

    for path in ROOT.rglob("*"):

        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        findings = scan_file(path)

        if not findings:
            continue

        relative = path.relative_to(ROOT)

        for name, line_number, masked in findings:
            print(
                f"[FAIL] {name}: "
                f"{relative}:{line_number} "
                f"[{masked}]"
            )

            total += 1

    if total == 0:
        print(
            "[PASS] No obvious hard-coded secrets detected."
        )
        return 0

    print()
    print(
        f"[FAIL] {total} potential secret(s) detected."
    )
    print(
        "[INFO] Secret values were intentionally masked."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
