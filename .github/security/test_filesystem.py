'''Test des fichiers système'''
from __future__ import annotations
import stat
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
}

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "master.key",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "service-account.json",
}

MAX_SCAN_FILES = 100_000


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    return any(
        part in IGNORED_DIRECTORIES
        for part in relative.parts
    )


def is_world_writable(mode: int) -> bool:
    return bool(
        mode & stat.S_IWOTH
    )


def is_group_writable(mode: int) -> bool:
    return bool(
        mode & stat.S_IWGRP
    )


def is_world_executable(mode: int) -> bool:
    return bool(
        mode & stat.S_IXOTH
    )


def main() -> int:
    print("=== FILESYSTEM SECURITY SCAN ===")

    failures = 0
    scanned = 0

    for path in ROOT.rglob("*"):

        if scanned >= MAX_SCAN_FILES:
            print(
                "[WARN] Scan limit reached."
            )
            break

        if should_ignore(path):
            continue

        try:
            information = path.lstat()
        except OSError as error:
            print(
                f"[WARN] Cannot stat {path}: {error}"
            )
            continue

        scanned += 1

        mode = information.st_mode
        relative = path.relative_to(ROOT)

        if is_world_writable(mode):
            print(
                f"[FAIL] World-writable: {relative}"
            )
            failures += 1

        if (
            path.is_file()
            and is_group_writable(mode)
            and path.name in {
                "master.key",
                "credentials.json",
                "service-account.json",
            }
        ):
            print(
                f"[FAIL] Sensitive file group-writable: "
                f"{relative}"
            )
            failures += 1

        if (
            path.is_file()
            and path.name in SENSITIVE_FILES
        ):
            print(
                f"[WARN] Sensitive file present: "
                f"{relative}"
            )

        if (
            path.is_file()
            and is_world_executable(mode)
            and path.suffix in {
                ".py",
                ".sh",
            }
        ):
            print(
                f"[WARN] World-executable script: "
                f"{relative}"
            )

    print()
    print(
        f"Files/objects inspected: {scanned}"
    )

    if failures == 0:
        print(
            "[PASS] No dangerous filesystem permissions detected."
        )
        return 0

    print(
        f"[FAIL] {failures} dangerous permission(s) detected."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
