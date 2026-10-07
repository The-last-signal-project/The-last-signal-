import sqlite3
import sys
from pathlib import Path


SENSITIVE_COLUMNS = {
    "password_hash",
    "password",
    "token",
    "secret",
}


def afficher_database(database):
    database = Path(database)

    if not database.exists():
        print(f"Database not found: {database}")
        return 1

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)

    tables = [row[0] for row in cursor.fetchall()]

    print("=== TABLES ===")

    for table in tables:
        print(f"- {table}")

    print("\n=== DATABASE CONTENT ===")

    for table in tables:
        print(f"\n--- {table} ---")

        cursor.execute(f'SELECT * FROM "{table}"')

        rows = cursor.fetchall()

        if not rows:
            print("(empty)")
            continue

        columns = [
            description[0]
            for description in cursor.description
        ]

        # Affichage des colonnes
        print(" | ".join(columns))

        # Affichage des lignes
        for row in rows:
            values = []

            for column, value in zip(columns, row):
                if column.lower() in SENSITIVE_COLUMNS:
                    value = "[HIDDEN]"

                if value is None:
                    value = "NULL"

                values.append(str(value))

            print(" | ".join(values))

    connection.close()

    return 0


if __name__ == "__main__":
    database = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "database/the_last_signal.db"
    )

    sys.exit(afficher_database(database))
