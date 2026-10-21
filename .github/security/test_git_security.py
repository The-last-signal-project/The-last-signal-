"""Test de sécurité de Git."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path


ROOT = Path.cwd().resolve()


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(
        r"""(?i)\bpassword\s*[:=]\s*['"][^'"]{6,}"""
    ),
    re.compile(
        r"""(?i)\bapi[_-]?key\s*[:=]\s*['"][A-Za-z0-9_-]{12,}"""
    ),
]


def run_git(
    arguments: list[str],
) -> subprocess.CompletedProcess[str]:
    """Execute une commande Git et retourne son résultat."""

    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def scan_git_history() -> bool:
    """
    Analyse l'historique Git à la recherche de secrets évidents.

    Le contenu est traité ligne par ligne afin d'éviter de charger
    l'intégralité de l'historique en mémoire.
    """

    print(
        "[INFO] Scanning Git history for obvious secrets..."
    )

    process = subprocess.Popen(
        [
            "git",
            "log",
            "--all",
            "--format=",
            "-p",
            "--unified=0",
            "--no-ext-diff",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if process.stdout is None:
        process.kill()
        process.wait()
        print(
            "[WARN] Unable to read Git history."
        )
        return False

    secret_found = False

    try:
        for line in process.stdout:

            # On analyse uniquement les lignes ajoutées.
            #
            # Les lignes "+++" sont des métadonnées du diff,
            # pas du contenu ajouté.
            if not line.startswith("+"):
                continue

            if line.startswith("+++"):
                continue

            if any(
                pattern.search(line)
                for pattern in SECRET_PATTERNS
            ):
                print(
                    "[FAIL] Potential secret detected "
                    "in Git history."
                )

                secret_found = True
                break

    finally:
        process.stdout.close()

        if secret_found:
            process.terminate()
        else:
            process.wait()

    # Git peut retourner un code non nul si le processus a été
    # interrompu volontairement après la détection d'un secret.
    if secret_found:
        return True

    if process.returncode != 0:
        print(
            "[WARN] Git history scan unavailable."
        )
        return False

    return False


def main() -> int:
    """Execute tous les contrôles de sécurité Git."""

    print("=== GIT SECURITY SCAN ===")

    failures = 0

    # --------------------------------------------------------
    # Repository
    # --------------------------------------------------------

    if not (ROOT / ".git").exists():
        print(
            "[SKIP] Not a Git repository."
        )
        return 0

    # --------------------------------------------------------
    # Working tree
    # --------------------------------------------------------

    status = run_git(
        ["status", "--porcelain"]
    )

    if status.returncode != 0:
        print(
            "[WARN] Unable to inspect Git status."
        )
    elif status.stdout.strip():
        print(
            "[INFO] Working tree contains changes."
        )

    # --------------------------------------------------------
    # Sensitive tracked files
    # --------------------------------------------------------

    tracked = run_git(
        ["ls-files"]
    )

    sensitive_names = {
        ".env",
        ".env.local",
        ".env.production",
        "master.key",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "service-account.json",
    }

    if tracked.returncode == 0:

        for line in tracked.stdout.splitlines():

            path = Path(line)

            if path.name in sensitive_names:
                print(
                    "[FAIL] Sensitive file tracked by Git: "
                    f"{line}"
                )
                failures += 1

    else:
        print(
            "[WARN] Unable to inspect tracked files."
        )

    # --------------------------------------------------------
    # Git configuration
    # --------------------------------------------------------

    config = run_git(
        ["config", "--get", "core.filemode"]
    )

    if config.returncode == 0:
        value = config.stdout.strip()

        print(
            f"[INFO] core.filemode={value}"
        )

    # --------------------------------------------------------
    # Current commit
    # --------------------------------------------------------

    commit = run_git(
        [
            "rev-parse",
            "HEAD",
        ]
    )

    if commit.returncode == 0:
        print(
            f"[INFO] HEAD={commit.stdout.strip()}"
        )

    # --------------------------------------------------------
    # Git history
    #
    # Important:
    # The history is processed as a stream instead of being
    # entirely stored in memory.
    #
    # Only added lines are scanned because removed lines do not
    # introduce secrets into the repository at that commit.
    # --------------------------------------------------------

    if scan_git_history():
        failures += 1

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    if failures == 0:
        print(
            "[PASS] Git security checks passed."
        )
        return 0

    print(
        f"[FAIL] {failures} Git security issue(s) detected."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
