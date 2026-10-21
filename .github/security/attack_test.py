''' Red Team File Integrity'''
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


'''
============================================================
                  Configuration GitHub
============================================================
'''

REPOSITORY = os.environ.get(
    "GITHUB_REPOSITORY",
    "",
)

SHA = os.environ.get(
    "GITHUB_SHA",
    "",
)

GITHUB_SERVER = os.environ.get(
    "GITHUB_SERVER_URL",
    "https://github.com",
).rstrip("/")


SCRIPT_DIRECTORY = (
    Path(__file__).resolve().parent
)

INTEGRITY_CHECKER = (
    SCRIPT_DIRECTORY
    / "integrity_check.py"
)


'''
============================================================
                 Command execution
============================================================
'''


def run(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:

    print(
        f"[CMD] {' '.join(command)}"
    )

    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


'''
============================================================
                       SHA-256
============================================================
'''


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


'''
============================================================
                         Git
============================================================
'''


def clone_repository(
    destination: Path,
) -> None:

    if not REPOSITORY:
        raise RuntimeError(
            "GITHUB_REPOSITORY est absent."
        )

    if not SHA:
        raise RuntimeError(
            "GITHUB_SHA est absent."
        )

    repository_url = (
        f"{GITHUB_SERVER}/"
        f"{REPOSITORY}.git"
    )

    print("\n=== RED TEAM CLONE ===")

    print(
        f"Repository : {repository_url}"
    )

    print(
        f"SHA        : {SHA}"
    )

    run(
        [
            "git",
            "clone",
            "--no-tags",
            "--filter=blob:none",
            repository_url,
            str(destination),
        ]
    )

    run(
        [
            "git",
            "fetch",
            "--depth=1",
            "origin",
            SHA,
        ],
        cwd=destination,
    )

    run(
        [
            "git",
            "checkout",
            "--detach",
            SHA,
        ],
        cwd=destination,
    )

    actual_sha = run(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd=destination,
    ).stdout.strip()

    if actual_sha != SHA:
        raise RuntimeError(
            "Le clone ne correspond pas au SHA attendu.\n"
            f"Expected: {SHA}\n"
            f"Actual:   {actual_sha}"
        )

    print(
      f"[PASS] Exact commit verified: {actual_sha}"
    )


'''
============================================================
                      Laboratoire
============================================================
'''


def create_test_environment_files(
    repository: Path,
) -> None:

    print(
        "\n=== CREATING SECURITY LAB ==="
    )

    env_file = repository / ".env"

    if not env_file.exists():
        env_file.write_text(
            "# TEST ONLY\n"
            "TEST_SECRET=FAKE_TEST_SECRET\n"
            "API_KEY=FAKE_API_KEY\n",
            encoding="utf-8",
        )

    idea = repository / ".idea"
    idea.mkdir(
        parents=True,
        exist_ok=True,
    )

    workspace = (
        idea / "workspace.xml"
    )

    if not workspace.exists():
        workspace.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
    <component name="SecurityTest">
        <option name="test" value="original" />
    </component>
</project>
""",
            encoding="utf-8",
        )

    vault = repository / "vault.enc"

    if not vault.exists():
        vault.write_bytes(
            b"FAKE_ENCRYPTED_VAULT_SECURITY_TEST"
        )

    print(
        "[PASS] Laboratory created."
    )


'''
===========================================================
                  Attaques
===========================================================
'''


def attack_cargo_lock(
    repository: Path,
) -> None:

    target = repository / "Cargo.lock"

    if not target.exists():
        raise FileNotFoundError(
            "Cargo.lock absent."
        )

    target.write_bytes(
        target.read_bytes()
        + b"\n# RED TEAM INTEGRITY TEST\n"
    )

    print(
        "[ATTACK] Cargo.lock modified."
    )


def attack_env(
    repository: Path,
) -> None:

    target = repository / ".env"

    if not target.exists():
        raise FileNotFoundError(
            ".env absent."
        )

    target.write_text(
        target.read_text(
            encoding="utf-8"
        )
        + "\nATTACK_TEST_MODIFICATION=TRUE\n",
        encoding="utf-8",
    )

    print(
        "[ATTACK] .env modified."
    )


def attack_idea(
    repository: Path,
) -> None:

    target = (
        repository
        / ".idea"
        / "workspace.xml"
    )

    if not target.exists():
        raise FileNotFoundError(
            "workspace.xml absent."
        )

    content = target.read_text(
        encoding="utf-8"
    )

    content = content.replace(
        'value="original"',
        'value="attacker-modified"',
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    print(
        "[ATTACK] .idea/workspace.xml modified."
    )


def find_security_file(
    repository: Path,
) -> Path | None:

    candidates: list[Path] = []

    for directory in (
        repository / "security",
        repository / "tests" / "security",
    ):

        if not directory.exists():
            continue

        for path in directory.rglob("*"):

            if not path.is_file():
                continue

            if path.name in {
                "attack_test.py",
                "integrity_check.py",
            }:
                continue

            candidates.append(path)

    if not candidates:
        return None

    return sorted(candidates)[0]


def attack_security_file(
    repository: Path,
) -> None:

    target = find_security_file(
        repository
    )

    if target is None:
        raise RuntimeError(
            "Aucun fichier security disponible."
        )

    target.write_bytes(
        target.read_bytes()
        + b"\n# RED TEAM INTEGRITY TEST\n"
    )

    print(
        "[ATTACK] Security file modified:"
        f" {target.relative_to(repository)}"
    )


def attack_vault(
    repository: Path,
) -> None:

    target = repository / "vault.enc"

    if not target.exists():
        raise FileNotFoundError(
            "vault.enc absent."
        )

    original = bytearray(
        target.read_bytes()
    )

    if not original:
        raise RuntimeError(
            "vault.enc est vide."
        )

    positions = {
        0,
        len(original) // 2,
        len(original) - 1,
    }

    for position in positions:
        original[position] ^= 0xFF

    target.write_bytes(
        bytes(original)
    )

    print(
        "[ATTACK] vault.enc corrupted."
    )


def attack_master_key_discovery(
    repository: Path,
) -> bool:

    found = []

    for path in repository.rglob("master.key"):

        try:
            relative = path.relative_to(
                repository
            )
        except ValueError:
            continue

        if ".git" in relative.parts:
            continue

        found.append(relative)

    if not found:
        print(
            "[PASS] No master.key exposed."
        )
        return True

    print(
        "[FAIL] master.key exposed:"
    )

    for path in found:
        print(f"  ! {path}")

    return False


# ============================================================
# Integrity
# ============================================================

def run_integrity_check(
    repository: Path,
) -> bool:

    result = run(
        [
            sys.executable,
            str(INTEGRITY_CHECKER),
            "check",
        ],
        cwd=repository,
        check=False,
    )

    print(result.stdout)

    return result.returncode == 1


def execute_integrity_attack(
    name: str,
    repository: Path,
    attack: Callable[[Path], None],
) -> bool:

    print("\n" + "=" * 70)
    print(f" ATTACK: {name}")
    print("=" * 70)

    run(
        [
            sys.executable,
            str(INTEGRITY_CHECKER),
            "create",
        ],
        cwd=repository,
    )

    baseline = (
        repository
        / ".security-baseline.json"
    )

    try:
        attack(repository)

        detected = run_integrity_check(
            repository
        )

        if not detected:
            print(
                "[FAIL] Attack was NOT detected."
            )
            return False

        print(
            "[PASS] Attack detected."
        )

        return True

    finally:
        baseline.unlink(
            missing_ok=True
        )


# ============================================================
# Git final
# ============================================================

def verify_git_clean(
    repository: Path,
) -> bool:

    print(
        "\n=== FINAL GIT STATE ==="
    )

    status = run(
        [
            "git",
            "status",
            "--porcelain",
        ],
        cwd=repository,
        check=False,
    )

    if status.stdout.strip():
        print(status.stdout)

    # Le laboratoire contient volontairement des fichiers
    # non suivis. Nous vérifions donc spécifiquement les
    # modifications des fichiers suivis.
    diff = run(
        [
            "git",
            "diff",
            "--exit-code",
        ],
        cwd=repository,
        check=False,
    )

    if diff.returncode != 0:
        print(
            "[FAIL] Tracked files remain modified."
        )
        return False

    print(
        "[PASS] No tracked files modified."
    )

    return True


# ============================================================
# Main
# ============================================================

def main() -> int:

    print("=" * 70)
    print(
        "THE LAST SIGNAL - "
        "RED TEAM FILE INTEGRITY TEST V2"
    )
    print("=" * 70)

    if not REPOSITORY:
        print(
            "[ERROR] GITHUB_REPOSITORY missing."
        )
        return 2

    if not SHA:
        print(
            "[ERROR] GITHUB_SHA missing."
        )
        return 2

    if not INTEGRITY_CHECKER.exists():
        print(
            "[ERROR] integrity_check.py missing:"
        )
        print(INTEGRITY_CHECKER)
        return 2

    results: list[tuple[str, bool]] = []

    with tempfile.TemporaryDirectory(
        prefix="security_red_team_"
    ) as temporary_directory:

        repository = (
            Path(temporary_directory)
            / "repository"
        )

        clone_repository(
            repository
        )

        create_test_environment_files(
            repository
        )

        # ----------------------------------------------------
        # Cargo.lock
        # ----------------------------------------------------

        if (repository / "Cargo.lock").exists():

            results.append(
                (
                    "Cargo.lock tampering",
                    execute_integrity_attack(
                        "Cargo.lock tampering",
                        repository,
                        attack_cargo_lock,
                    ),
                )
            )

        # ----------------------------------------------------
        # .env
        # ----------------------------------------------------

        results.append(
            (
                ".env tampering",
                execute_integrity_attack(
                    ".env tampering",
                    repository,
                    attack_env,
                ),
            )
        )

        # ----------------------------------------------------
        # .idea
        # ----------------------------------------------------

        results.append(
            (
                ".idea tampering",
                execute_integrity_attack(
                    ".idea tampering",
                    repository,
                    attack_idea,
                ),
            )
        )

        # ----------------------------------------------------
        # security/
        # ----------------------------------------------------

        security_file = find_security_file(
            repository
        )

        if security_file is not None:

            results.append(
                (
                    "security tampering",
                    execute_integrity_attack(
                        "security file tampering",
                        repository,
                        attack_security_file,
                    ),
                )
            )
        else:
            print(
                "[SKIP] No security file."
            )

        # ----------------------------------------------------
        # vault.enc
        # ----------------------------------------------------

        results.append(
            (
                "vault.enc tampering",
                execute_integrity_attack(
                    "vault.enc corruption",
                    repository,
                    attack_vault,
                ),
            )
        )

        # ----------------------------------------------------
        # master.key
        # ----------------------------------------------------

        results.append(
            (
                "master.key exposure",
                attack_master_key_discovery(
                    repository
                ),
            )
        )

        # ----------------------------------------------------
        # Git
        # ----------------------------------------------------

        git_ok = verify_git_clean(
            repository
        )

    # ========================================================
    # Résultat
    # ========================================================

    print("\n" + "=" * 70)
    print(" FINAL RED TEAM RESULT")
    print("=" * 70)

    passed = 0

    for name, result in results:

        status = (
            "PASS"
            if result
            else "FAIL"
        )

        print(
            f"{status:>5} | {name}"
        )

        if result:
            passed += 1

    total = len(results)

    print()
    print(
        f"Security scenarios: {passed}/{total}"
    )

    print(
        "Git integrity: "
        f"{'PASS' if git_ok else 'FAIL'}"
    )

    if passed == total and git_ok:

        print(
            "\n[PASS] "
            "RED TEAM TEST PASSED."
        )

        return 0

    print(
        "\n[FAIL] "
        "RED TEAM TEST FAILED."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
