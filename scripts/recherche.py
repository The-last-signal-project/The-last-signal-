
import argparse
import csv
import json
import sqlite3
from pathlib import Path


DEFAULT_DATABASE = "database/the_last_signal.db"
DEFAULT_TABLE = None
DEFAULT_SEARCH = None


def identifier(nom):
    """Protège un nom de table ou de colonne SQLite."""
    return '"' + nom.replace('"', '""') + '"'


def rechercher(database, recherche=None, table=None):
    """Affiche ou recherche dans une ou plusieurs tables."""

    resultats = []

    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()

        # Récupération des tables
        if table is None:
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name COLLATE NOCASE
            """)
            tables = [t[0] for t in cursor.fetchall()]
        else:
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = ?
            """, (table,))

            if cursor.fetchone() is None:
                raise ValueError(f"Table inexistante : {table}")

            tables = [table]

        # Parcours des tables
        for nom_table in tables:

            table_sql = identifier(nom_table)

            cursor.execute(
                f"PRAGMA table_info({table_sql})"
            )

            infos = cursor.fetchall()
            colonnes = [c[1] for c in infos]

            # Récupération des clés primaires
            cles_primaires = sorted(
                [c for c in infos if c[5] > 0],
                key=lambda c: c[5]
            )

            if not recherche:
                # MODE AFFICHAGE COMPLET

                print(f"\n{'=' * 70}")
                print(f"TABLE : {nom_table}")
                print("=" * 70)

                print("Colonnes :", ", ".join(colonnes))

                # Tri par clé primaire si disponible
                if cles_primaires:
                    ordre = ", ".join(
                        identifier(c[1])
                        for c in cles_primaires
                    )
                    requete = (
                        f"SELECT * FROM {table_sql} "
                        f"ORDER BY {ordre}"
                    )
                else:
                    requete = (
                        f"SELECT * FROM {table_sql} "
                        f"ORDER BY rowid"
                    )

                try:
                    cursor.execute(requete)
                except sqlite3.OperationalError:
                    # Cas d'une table sans rowid
                    cursor.execute(
                        f"SELECT * FROM {table_sql}"
                    )

                lignes = cursor.fetchall()

                print(f"Nombre de lignes : {len(lignes)}")

                for ligne in lignes:
                    resultat = {
                        "table": nom_table,
                        "column": "*",
                        "row": ligne,
                    }

                    resultats.append(resultat)
                    print(ligne)

            else:
                # MODE RECHERCHE

                for colonne in colonnes:

                    try:
                        cursor.execute(
                            f"""
                            SELECT *
                            FROM {table_sql}
                            WHERE CAST(
                                {identifier(colonne)} AS TEXT
                            ) LIKE ?
                            """,
                            (f"%{recherche}%",)
                        )

                        lignes = cursor.fetchall()

                        for ligne in lignes:
                            resultats.append({
                                "table": nom_table,
                                "column": colonne,
                                "row": ligne,
                            })

                    except sqlite3.Error as erreur:
                        print(
                            f"Erreur dans {nom_table}.{colonne} : "
                            f"{erreur}"
                        )

    if recherche:
        print(f"\nRecherche : {recherche}")
        print(f"Résultats : {len(resultats)}")

        for r in resultats:
            print(
                f"[{r['table']}] "
                f"[{r['column']}] "
                f"{r['row']}"
            )

    return resultats


def ecrire_fichier(resultats, fichier, fmt):

    fichier = Path(fichier)

    if fmt == "txt":
        with fichier.open("w", encoding="utf-8") as f:
            for r in resultats:
                f.write(
                    f"[{r['table']}] "
                    f"[{r['column']}] "
                    f"{r['row']}\n"
                )

    elif fmt == "md":
        with fichier.open("w", encoding="utf-8") as f:
            f.write("# Rapport de recherche\n\n")

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

            writer.writerow(["table", "column", "row"])

            for r in resultats:
                writer.writerow([
                    r["table"],
                    r["column"],
                    r["row"]
                ])

    print(f"\nRapport enregistré dans : {fichier}")


def main():

    parser = argparse.ArgumentParser(
        description="Explorateur et moteur de recherche SQLite"
    )

    parser.add_argument(
        "-d", "--database",
        default=DEFAULT_DATABASE
    )

    parser.add_argument(
        "-t", "--table"
    )

    parser.add_argument(
        "-s", "--search"
    )

    parser.add_argument(
        "-o", "--output"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["txt", "md", "json", "csv"],
        default="txt"
    )

    args = parser.parse_args()

    database = args.database
    table = args.table
    recherche = args.search

    print(f"Database utilisée : {Path(database).resolve()}")

    if not Path(database).is_file():
        parser.error(f"Base de données introuvable : {database}")

    resultats = rechercher(
        database,
        recherche,
        table
    )

    if args.output:
        ecrire_fichier(
            resultats,
            args.output,
            args.format
        )


if __name__ == "__main__":
    main()
