from __future__ import annotations

import shutil
import socket
import sys
import tempfile
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import time
import zstandard


HOST = "127.0.0.1"
DEFAULT_PORT = 8000
ARCHIVE_EXTENSION = ".tar.zst"

# Type de rapport utilisé automatiquement
REPORT_TYPE = "python"


# ============================================================
# AFFICHAGE
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_error(message: str) -> None:
    print()
    print(f"[ERREUR] {message}")


def print_info(message: str) -> None:
    print(f"[INFO] {message}")


# ============================================================
# RACINE DU PROJET
# ============================================================

def find_project_root() -> Path:
    """
    Détecte automatiquement la racine du projet
    à partir de l'emplacement du script/exécutable.
    """

    if getattr(sys, "frozen", False):
        current = Path(sys.executable).resolve().parent
    else:
        current = Path(__file__).resolve().parent

    for directory in [current, *current.parents]:
        if (directory / "reports").is_dir():
            return directory

    raise RuntimeError(
        "Impossible de trouver la racine du projet "
        "(dossier reports introuvable)."
    )


def find_reports_root(git_root: Path) -> Path:
    """
    Trouve le dossier reports du projet.
    """

    reports_root = git_root / "reports"

    if not reports_root.is_dir():
        raise RuntimeError(
            f"Le dossier reports est introuvable : {reports_root}"
        )

    return reports_root


# ============================================================
# DATE
# ============================================================

def ask_report_date() -> str:
    """
    Demande la date du rapport au format YYYY-MM-DD.
    """

    while True:
        value = input(
            "\nDate du rapport (YYYY-MM-DD) : "
        ).strip()

        try:
            date = datetime.strptime(
                value,
                "%Y-%m-%d",
            )

            return date.strftime("%Y-%m-%d")

        except ValueError:
            print(
                "Date invalide. Utilisez le format YYYY-MM-DD."
            )


# ============================================================
# RAPPORTS PYTHON
# ============================================================

def get_python_report_directory(
    reports_root: Path,
    report_date: str,
) -> Path:
    """
    Retourne le dossier des rapports Python pour une date donnée.

    Exemple :
        reports/python/2026-09-10/
    """

    return (
        reports_root
        / REPORT_TYPE
        / report_date
    )


def find_available_html_reports(
    report_directory: Path,
) -> list[Path]:
    """
    Retourne tous les fichiers HTML disponibles
    dans le dossier d'une date.
    """

    if not report_directory.is_dir():
        return []

    reports = [
        path
        for path in report_directory.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".html"
    ]

    return sorted(
        reports,
        key=lambda path: path.name.lower(),
    )


def choose_html_report(
    reports: list[Path],
) -> Path:
    """
    Affiche les rapports disponibles et demande
    lequel ouvrir.
    """

    print_header("RAPPORTS PYTHON DISPONIBLES")

    for index, report in enumerate(reports, start=1):
        print(f"{index}. {report.name}")

    while True:
        choice = input(
            "\nChoisissez un rapport : "
        ).strip()

        try:
            index = int(choice)

            if 1 <= index <= len(reports):
                return reports[index - 1]

        except ValueError:
            pass

        print(
            "Choix invalide. Entrez le numéro correspondant."
        )


# ============================================================
# ARCHIVES
# ============================================================

def find_archive_member(
    archive_path: Path,
    expected_members: list[str],
) -> bytes | None:
    """
    Recherche et extrait uniquement les fichiers demandés
    depuis une archive .tar.zst.
    """

    try:
        with archive_path.open("rb") as compressed_file:

            decompressor = zstandard.ZstdDecompressor()

            with decompressor.stream_reader(
                compressed_file
            ) as reader:

                import tarfile

                with tarfile.open(
                    fileobj=reader,
                    mode="r|",
                ) as archive:

                    for member in archive:

                        if member.name not in expected_members:
                            continue

                        if not member.isfile():
                            continue

                        extracted = archive.extractfile(member)

                        if extracted is None:
                            return None

                        return extracted.read()

    except Exception as exc:
        print_info(
            f"Impossible de lire {archive_path.name} : {exc}"
        )

    return None


def find_archived_report(
    report_type: Path,
    report_date: str,
    filename: str,
    temp_directory: Path,
) -> Path | None:
    """
    Recherche le rapport dans :

    1. l'archive quotidienne :
       YYYY-MM-DD.tar.zst

    2. l'archive mensuelle :
       MM-YYYY.tar.zst

    3. les autres archives en dernier recours.
    """

    month_year = datetime.strptime(
        report_date,
        "%Y-%m-%d",
    ).strftime("%m-%Y")

    daily_archive = (
        report_type
        / f"{report_date}.tar.zst"
    )

    monthly_archive = (
        report_type
        / f"{month_year}.tar.zst"
    )

    archives: list[tuple[Path, list[str]]] = []

    # --------------------------------------------------------
    # Archive quotidienne
    # --------------------------------------------------------

    if daily_archive.is_file():
        archives.append(
            (
                daily_archive,
                [
                    f"{report_date}/{filename}",
                    filename,
                ],
            )
        )

    # --------------------------------------------------------
    # Archive mensuelle
    # --------------------------------------------------------

    if monthly_archive.is_file():
        archives.append(
            (
                monthly_archive,
                [
                    f"{month_year}/{report_date}/{filename}",
                    f"{report_date}/{filename}",
                    filename,
                ],
            )
        )

    # --------------------------------------------------------
    # Autres archives
    # --------------------------------------------------------

    already_checked = {
        archive.resolve()
        for archive, _ in archives
    }

    for archive in sorted(
        report_type.glob(
            f"*{ARCHIVE_EXTENSION}"
        )
    ):
        if archive.resolve() in already_checked:
            continue

        archives.append(
            (
                archive,
                [
                    f"{report_date}/{filename}",
                    f"{month_year}/{report_date}/{filename}",
                    filename,
                ],
            )
        )

    # --------------------------------------------------------
    # Recherche
    # --------------------------------------------------------

    for archive_path, expected_members in archives:

        print_info(
            f"Recherche dans l'archive : "
            f"{archive_path.name}"
        )

        data = find_archive_member(
            archive_path,
            expected_members,
        )

        if data is None:
            continue

        output_directory = (
            temp_directory
            / report_type.name
            / report_date
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_directory
            / filename
        )

        output_file.write_bytes(data)

        print_info(
            f"Rapport extrait depuis : "
            f"{archive_path.name}"
        )

        return output_file

    return None


# ============================================================
# RECHERCHE DES RAPPORTS DANS LES ARCHIVES
# ============================================================

def find_available_archived_reports(
    report_type: Path,
    report_date: str,
) -> list[str]:
    """
    Recherche les noms des rapports HTML présents
    dans les archives correspondant à une date.

    Cette fonction permet d'afficher les rapports disponibles
    avant de demander lequel extraire.
    """

    month_year = datetime.strptime(
        report_date,
        "%Y-%m-%d",
    ).strftime("%m-%Y")

    daily_archive = (
        report_type
        / f"{report_date}.tar.zst"
    )

    monthly_archive = (
        report_type
        / f"{month_year}.tar.zst"
    )

    archives: list[Path] = []

    if daily_archive.is_file():
        archives.append(daily_archive)

    if monthly_archive.is_file():
        archives.append(monthly_archive)

    already_checked = {
        archive.resolve()
        for archive in archives
    }

    for archive in sorted(
        report_type.glob(
            f"*{ARCHIVE_EXTENSION}"
        )
    ):
        if archive.resolve() not in already_checked:
            archives.append(archive)

    found: set[str] = set()

    import tarfile

    for archive_path in archives:

        print_info(
            f"Inspection de l'archive : "
            f"{archive_path.name}"
        )

        try:
            with archive_path.open("rb") as compressed_file:

                decompressor = zstandard.ZstdDecompressor()

                with decompressor.stream_reader(
                    compressed_file
                ) as reader:

                    with tarfile.open(
                        fileobj=reader,
                        mode="r|",
                    ) as archive:

                        for member in archive:

                            if not member.isfile():
                                continue

                            if not member.name.lower().endswith(
                                ".html"
                            ):
                                continue

                            filename = Path(
                                member.name
                            ).name

                            # On vérifie que le fichier
                            # appartient bien à la date demandée.
                            if (
                                f"/{report_date}/"
                                in f"/{member.name}"
                                or member.name.startswith(
                                    f"{report_date}/"
                                )
                            ):
                                found.add(filename)

        except Exception as exc:
            print_info(
                f"Impossible d'inspecter "
                f"{archive_path.name} : {exc}"
            )

    return sorted(
        found,
        key=str.lower,
    )


# ============================================================
# SERVEUR HTTP
# ============================================================

def find_free_port(
    host: str = HOST,
    start_port: int = DEFAULT_PORT,
) -> int:
    """
    Trouve automatiquement un port libre.
    """

    for port in range(
        start_port,
        start_port + 100,
    ):

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:

            try:
                sock.bind(
                    (host, port)
                )

                return port

            except OSError:
                continue

    raise RuntimeError(
        "Impossible de trouver un port libre."
    )


def start_server(
    directory: Path,
    filename: str,
) -> None:
    """
    Lance le serveur HTTP local et ouvre
    directement le fichier HTML demandé.
    """

    port = find_free_port()

    handler = lambda *args, **kwargs: (
        SimpleHTTPRequestHandler(
            *args,
            directory=str(directory),
            **kwargs,
        )
    )

    server = ThreadingHTTPServer(
        (HOST, port),
        handler,
    )

    url = (
        f"http://{HOST}:{port}/"
        f"{filename}"
    )

    print_header("SERVEUR HTTP")

    print(f"Répertoire : {directory}")
    print(f"Adresse    : {url}")
    print()
    print(
        "Le rapport va être ouvert "
        "dans votre navigateur."
    )
    print(
        "Appuyez sur Ctrl+C pour arrêter "
        "le serveur."
    )

    webbrowser.open(url)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print(
            "\nArrêt du serveur..."
        )

    finally:
        server.server_close()


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main() -> int:

    print_header("OPEN PYTHON REPORT")

    # --------------------------------------------------------
    # Racine du projet
    # --------------------------------------------------------

    try:
        project_root = find_project_root()

    except RuntimeError as exc:
        print_error(str(exc))
        time.sleep(3)
        return 1

    print_info(
        f"Racine : {project_root}"
    )

    # --------------------------------------------------------
    # Dossier reports
    # --------------------------------------------------------

    try:
        reports_root = find_reports_root(
            project_root
        )

    except RuntimeError as exc:
        print_error(str(exc))
        return 1

    print_info(
        f"Dossier reports : {reports_root}"
    )

    # --------------------------------------------------------
    # Type de rapport automatique
    # --------------------------------------------------------

    report_type = (
        reports_root
        / REPORT_TYPE
    )

    if not report_type.is_dir():
        print_error(
            f"Le dossier des rapports Python "
            f"est introuvable : {report_type}"
        )
        return 1

    print_info(
        f"Type de rapport : {REPORT_TYPE}"
    )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    report_date = ask_report_date()

    print_info(
        f"Date sélectionnée : {report_date}"
    )

    # --------------------------------------------------------
    # Dossier de la date
    # --------------------------------------------------------

    report_directory = (
        report_type
        / report_date
    )

    # --------------------------------------------------------
    # Recherche des fichiers non archivés
    # --------------------------------------------------------

    available_reports = (
        find_available_html_reports(
            report_directory
        )
    )

    # --------------------------------------------------------
    # Si aucun fichier direct,
    # recherche dans les archives
    # --------------------------------------------------------

    if not available_reports:

        print_info(
            "Aucun fichier HTML non archivé trouvé."
        )

        print_info(
            "Recherche des rapports dans les archives..."
        )

        archived_filenames = (
            find_available_archived_reports(
                report_type,
                report_date,
            )
        )

        if not archived_filenames:
            print_error(
                f"Aucun rapport Python trouvé "
                f"pour le {report_date}."
            )

            return 1

        print_header(
            "RAPPORTS PYTHON DISPONIBLES"
        )

        for index, filename in enumerate(
            archived_filenames,
            start=1,
        ):
            print(
                f"{index}. {filename}"
            )

        while True:

            choice = input(
                "\nChoisissez un rapport : "
            ).strip()

            try:
                index = int(choice)

                if 1 <= index <= len(
                    archived_filenames
                ):
                    filename = (
                        archived_filenames[
                            index - 1
                        ]
                    )
                    break

            except ValueError:
                pass

            print(
                "Choix invalide. "
                "Entrez le numéro correspondant."
            )

        # ----------------------------------------------------
        # Extraction
        # ----------------------------------------------------

        temporary_directory = Path(
            tempfile.mkdtemp(
                prefix="open-report-"
            )
        )

        try:

            report_path = find_archived_report(
                report_type,
                report_date,
                filename,
                temporary_directory,
            )

            if report_path is None:
                print_error(
                    f"Impossible d'extraire "
                    f"{filename}."
                )
                return 1

            server_directory = (
                report_path.parent
            )

            start_server(
                server_directory,
                report_path.name,
            )

        finally:

            shutil.rmtree(
                temporary_directory,
                ignore_errors=True,
            )

            print_info(
                "Répertoire temporaire supprimé."
            )

    else:

        # ----------------------------------------------------
        # Affichage des rapports disponibles
        # ----------------------------------------------------

        report_path = choose_html_report(
            available_reports
        )

        print()
        print_info(
            f"Rapport sélectionné : "
            f"{report_path.name}"
        )

        # ----------------------------------------------------
        # Serveur
        # ----------------------------------------------------

        start_server(
            report_path.parent,
            report_path.name,
        )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(main())
