'''Test d'intégrité'''
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


BASELINE_FILE = ".security-baseline.json"

IGNORED_DIRECTORIES = {
    ".git",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}

IGNORED_FILES = {
    BASELINE_FILE,
}

WATCHED_EXTENSIONS = {
    ".py",
    ".rs",
    ".toml",
    ".lock",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    ".env",
}

WATCHED_SPECIAL_FILES = {
    ".env",
    "Cargo.lock",
    "Cargo.toml",
    "vault.enc",
    "master.key",
}

WATCHED_DIRECTORIES = {
    ".github",
    ".idea",
    "security",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def should_ignore(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)

    if path.name in IGNORED_FILES:
        return True

    return any(
        part in IGNORED_DIRECTORIES
        for part in relative.parts
    )


def is_watched(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)

    if path.name in WATCHED_SPECIAL_FILES:
        return True

    if any(
        part in WATCHED_DIRECTORIES
        for part in relative.parts
    ):
        return True

    return path.suffix.lower() in WATCHED_EXTENSIONS


def scan_repository(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        try:
            if should_ignore(path, root):
                continue

            if not is_watched(path, root):
                continue

            relative = path.relative_to(root).as_posix()

            result[relative] = sha256_file(path)

        except (OSError, ValueError) as error:
            print(
                f"[WARN] Cannot scan {path}: {error}",
                file=sys.stderr,
            )

    return dict(sorted(result.items()))


def save_baseline(
    root: Path,
    baseline: dict[str, str],
) -> None:
    path = root / BASELINE_FILE

    path.write_text(
        json.dumps(
            baseline,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def load_baseline(root: Path) -> dict[str, str]:
    path = root / BASELINE_FILE

    if not path.exists():
        raise FileNotFoundError(
            f"Baseline absente : {path}"
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Format de baseline invalide."
        )

    return {
        str(key): str(value)
        for key, value in data.items()
    }


def compare(
    before: dict[str, str],
    after: dict[str, str],
) -> dict[str, list[str]]:

    before_files = set(before)
    after_files = set(after)

    return {
        "added": sorted(
            after_files - before_files
        ),
        "removed": sorted(
            before_files - after_files
        ),
        "modified": sorted(
            path
            for path in before_files & after_files
            if before[path] != after[path]
        ),
    }


def create(root: Path) -> int:
    print("=== SECURITY BASELINE ===")

    baseline = scan_repository(root)

    save_baseline(
        root,
        baseline,
    )

    print(
        f"Files monitored: {len(baseline)}"
    )

    print(
        f"Baseline: {BASELINE_FILE}"
    )

    return 0


def check(root: Path) -> int:
    print("=== INTEGRITY CHECK ===")

    try:
        before = load_baseline(root)

    except (OSError, ValueError) as error:
        print(
            f"[ERROR] {error}",
            file=sys.stderr,
        )
        return 2

    after = scan_repository(root)

    differences = compare(
        before,
        after,
    )

    added = differences["added"]
    removed = differences["removed"]
    modified = differences["modified"]

    if added:
        print("\n[ADDED]")

        for path in added:
            print(f"  + {path}")

    if removed:
        print("\n[REMOVED]")

        for path in removed:
            print(f"  - {path}")

    if modified:
        print("\n[MODIFIED]")

        for path in modified:
            print(f"  * {path}")

    total = (
        len(added)
        + len(removed)
        + len(modified)
    )

    if total == 0:
        print(
            "\n[PASS] No integrity violation detected."
        )
        return 0

    print(
        f"\n[FAIL] "
        f"{total} integrity violation(s) detected."
    )

    return 1


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python integrity_check.py create\n"
            "  python integrity_check.py check"
        )
        return 2

    root = Path.cwd().resolve()

    if sys.argv[1] == "create":
        return create(root)

    if sys.argv[1] == "check":
        return check(root)

    print(
        f"Unknown command: {sys.argv[1]}"
    )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
