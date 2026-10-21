import argparse
import csv
import json
import sqlite3
from pathlib import Path
import os


conn = sqlite3.connect("database/client_logs.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM logs")
print("Nombre de lignes :", cursor.fetchone()[0])

cursor.execute("""
SELECT id, timestamp, level, message
FROM logs
ORDER BY id DESC
LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()

print("Database utilisée :", os.path.abspath("database/client_logs.db"))

DEFAULT_DATABASE = "database/client_logs.db"
DEFAULT_TABLE = None
DEFAULT_SEARCH = ""


def rechercher(database, recherche, table=None):
    """Recherche un texte dans une ou plusieurs tables."""

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Si aucune table n'est précisée, on les récupère toutes
    if table is None:
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [t[0] for t in cursor.fetchall()]
    else:
        tables = [table]

    resultats = []

    for table in tables:

        cursor.execute(f"PRAGMA table_info({table})")
        colonnes = [c[1] for c in cursor.fetchall()]

        for colonne in colonnes:

            try:
                cursor.execute(
                    f"""
                    SELECT rowid, *
                    FROM {table}
                    WHERE CAST({colonne} AS TEXT) LIKE ?
                    """,
                    (f"%{recherche}%",)
                )

                lignes = cursor.fetchall()

                for ligne in lignes:
                    resultat = {
                        "table": table,
                        "column": colonne,
                        "row": ligne,
                    }

                    resultats.append(resultat)

                    print(
                        f"[{table}] "
                        f"[{colonne}] "
                        f"{ligne}"
                    )

            except sqlite3.Error:
                pass

    conn.close()

    return resultats


def ecrire_fichier(resultats, fichier, fmt):

    fichier = Path(fichier)

    if fmt == "txt":

        with fichier.open("w", encoding="utf-8") as f:

            if not resultats:
                f.write("Aucun résultat trouvé.\n")

            for r in resultats:
                f.write(
                    f"[{r['table']}] "
                    f"[{r['column']}] "
                    f"{r['row']}\n"
                )

    elif fmt == "md":

        with fichier.open("w", encoding="utf-8") as f:

            f.write("# Rapport de recherche\n\n")

            if not resultats:
                f.write("Aucun résultat trouvé.\n")

            for r in resultats:

                f.write(
                    f"## {r['table']}\n\n"
                    f"- **Colonne :** {r['column']}\n"
                    f"- **Valeur :** `{r['row']}`\n\n"
                )

    elif fmt == "json":

        with fichier.open("w", encoding="utf-8") as f:

            json.dump(
                resultats,
                f,
                indent=4,
                ensure_ascii=False,
                default=str
            )

    elif fmt == "csv":

        with fichier.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow(
                [
                    "table",
                    "column",
                    "row"
                ]
            )

            for r in resultats:

                writer.writerow(
                    [
                        r["table"],
                        r["column"],
                        r["row"]
                    ]
                )

    print(f"\nRapport enregistré dans : {fichier}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--database")
    parser.add_argument("-t", "--table")
    parser.add_argument("-s", "--search")
    parser.add_argument("-o", "--output")
    parser.add_argument(
        "-f",
        "--format",
        choices=["txt", "md", "json", "csv"],
        default="txt",
    )

    args = parser.parse_args()

    # Mode ligne de commande
    if args.database or args.search or args.table:

        database = args.database or DEFAULT_DATABASE
        table = args.table or DEFAULT_TABLE
        recherche = args.search
        output = args.output
        fmt = args.format
        

    # Mode interactif
    else:

        database = (
            input(f"Database [{DEFAULT_DATABASE}] : ")
            or DEFAULT_DATABASE
        )

        table = (
            input("Table (Entrée = toutes) : ")
            or DEFAULT_TABLE
        )

        recherche = (
            input("Recherche : ")
            or DEFAULT_SEARCH
        )

        output = input(
            "Fichier de sortie (Entrée = aucun) : "
        ).strip()

        if output == "":
            output = None
            fmt = "txt"
        else:
            fmt = (
                input(
                    "Format (txt/md/json/csv) [txt] : "
                ).strip().lower()
                or "txt"
            )

    resultats = rechercher(
        database,
        recherche,
        table
    )

    if output:
        ecrire_fichier(
            resultats,
            output,
            fmt
        )
    else:
        print(resultats)


if __name__ == "__main__":
    main()
