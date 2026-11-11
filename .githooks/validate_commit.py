
#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

EMAILS = {
    "252053530+ddcoder23@users.noreply.github.com",
    "ddcoder23@users.noreply.github.com",
}

TYPES = (
    "feat", "fix", "docs", "test", "refactor",
    "perf", "build", "ci", "chore"
)

PATTERN = re.compile(
    r"^(feat|fix|docs|test|refactor|perf|build|ci|chore)"
    r"\(([a-z0-9][a-z0-9._/-]*)\): ([a-z][^\r\n]*)$"
)


def git(*args):
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()


def is_merge_commit(sha):
    parents = git("rev-list", "--parents", "-n", "1", sha).split()
    return len(parents) > 2


def is_our_commit(sha):
    fields = git(
        "show", "-s", "--format=%ae%x00%ce", sha
    ).split("\0")

    return any(email.strip().lower() in EMAILS
           for email in fields)


def validate_subject(subject, sha=""):
    if not PATTERN.fullmatch(subject) or subject.endswith("."):
        print("\nCommit non conforme à Conventional Commits.")
        if sha:
            print(f"Commit : {sha}")
        print(f"Message : {subject}")
        print("\nFormat obligatoire : type(scope): description")
        print("Exemple : feat(inventory): add item stacking")
        print(f"Types autorisés : {', '.join(TYPES)}")
        print("Le scope est obligatoire.")
        print("La description doit commencer par une minuscule.")
        print("La description ne doit pas finir par un point.")
        return False



    return True


def commit_msg(message_file):
    # Un merge en cours est exempté.
    if subprocess.run(
        ["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ).returncode == 0:
        return 0

    identities = []
    for variable in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        result = subprocess.run(
            ["git", "var", variable],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Impossible de vérifier {variable}.")
            return 1
        match = re.search(r"<([^<>]+)>", result.stdout)
        if match:
            identities.append(match.group(1).lower())

    if not EMAILS.intersection(identities):
        return 0

    try:
        subject = Path(message_file).read_text(
            encoding="utf-8"
        ).splitlines()[0]
    except (OSError, IndexError):
        print("Impossible de lire le message du commit.")
        return 1

    return 0 if validate_subject(subject) else 1

def pre_push():
    try:
        ref_dir = Path(
            git(
                "rev-parse",
                "--git-path",
                "commit-validation/references"
            )
        )

        updates = sys.stdin.read().splitlines()

        for update in updates:
            fields = update.split()

            if not fields:
                continue

            if len(fields) != 4:
                print("Erreur : format de mise à jour Git invalide.")
                return 1

            local_ref, local_sha, remote_ref, remote_sha = fields

            # Ne contrôler que les branches locales.
            if not local_ref.startswith("refs/heads/"):
                continue

            # Ignorer les suppressions de branches.
            if set(local_sha) == {"0"}:
                continue

            branch = local_ref[len("refs/heads/"):]
            reference_file = ref_dir / branch

            # Vérifier la présence de la référence.
            try:
                reference = reference_file.read_text(
                    encoding="ascii"
                ).strip()
            except OSError:
                print(
                    f"Push bloqué : référence absente pour {branch}."
                )
                return 1

            # Vérifier le format du SHA.
            if not re.fullmatch(r"[0-9a-fA-F]{40,64}", reference):
                print(
                    f"Push bloqué : référence invalide pour {branch}."
                )
                return 1

            # Vérifier que les commits existent.
            git("cat-file", "-e", reference + "^{commit}")
            git("cat-file", "-e", local_sha + "^{commit}")

            # Vérifier que la référence est un ancêtre de la branche.
            try:
                git(
                    "merge-base",
                    "--is-ancestor",
                    reference,
                    local_sha
                )
            except subprocess.CalledProcessError:
                print(
                    f"Push bloqué : {branch} ne descend pas "
                    "de son commit de référence."
                )
                return 1

            # Commencer par les commits postérieurs à la référence.
            rev_args = [
                "rev-list",
                local_sha,
                "^" + reference
            ]

            # Exclure les commits déjà présents sur le serveur
            # lorsque leur SHA existe dans le dépôt local.
            if set(remote_sha) != {"0"}:
                try:
                    git(
                        "cat-file",
                        "-e",
                        remote_sha + "^{commit}"
                    )
                    rev_args.append("^" + remote_sha)
                except subprocess.CalledProcessError:
                    pass

            commits = git(*rev_args).splitlines()

            for sha in commits:
                if is_merge_commit(sha):
                    continue

                if not is_our_commit(sha):
                    continue

                subject = git(
                    "show",
                    "-s",
                    "--format=%s",
                    sha
                )

                if not validate_subject(subject, sha):
                    print(f"Branche concernée : {branch}")
                    print(f"Branche distante : {remote_ref}")
                    return 1

    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Erreur de validation du push : {error}")
        return 1

    return 0


def main():
    if len(sys.argv) < 2:
        print("Mode de validation manquant.")
        return 1

    try:
        if sys.argv[1] == "commit-msg" and len(sys.argv) == 3:
            return commit_msg(sys.argv[2])

        if sys.argv[1] == "pre-push":
            return pre_push()

        print("Mode de validation inconnu.")
        return 1

    except (subprocess.CalledProcessError, OSError) as error:
        print(f"Erreur de validation : {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
