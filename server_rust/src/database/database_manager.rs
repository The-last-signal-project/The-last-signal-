use std::path::Path;
use std::str::FromStr;
use std::time::Duration;

use sqlx::sqlite::{SqliteConnectOptions, SqlitePool, SqlitePoolOptions};

pub struct DatabaseManager {
    pool: SqlitePool,
}

impl DatabaseManager {
    /// 26 = SQLITE_NOTADB, 11 = SQLITE_CORRUPT
    fn is_corruption_error(error: &sqlx::Error) -> bool {
        match error {
            sqlx::Error::Database(e) => {
                matches!(e.code().as_deref(), Some("26") | Some("11"))
            }
            _ => false,
        }
    }

    /// Vérifie si une base SQLite existante est corrompue.
    pub async fn is_database_corrupted(
        database_url: &str,
    ) -> Result<bool, sqlx::Error> {
        let options = SqliteConnectOptions::from_str(database_url)?
            .create_if_missing(false);

        let pool = match SqlitePoolOptions::new()
            .max_connections(1)
            .acquire_timeout(Duration::from_secs(30))
            .connect_with(options)
            .await
        {
            Ok(pool) => pool,
            Err(e) if Self::is_corruption_error(&e) => return Ok(true),
            Err(e) => return Err(e),
        };

        let result: Result<String, sqlx::Error> =
            sqlx::query_scalar("PRAGMA integrity_check")
                .fetch_one(&pool)
                .await;

        pool.close().await;

        match result {
            Ok(integrity) => Ok(integrity.trim() != "ok"),
            Err(e) if Self::is_corruption_error(&e) => Ok(true),
            Err(e) => Err(e),
        }
    }

    /// Crée ou ouvre la base SQLite.
    pub async fn create_database(
        database_url: &str,
    ) -> Result<SqlitePool, sqlx::Error> {
        let options = SqliteConnectOptions::from_str(database_url)?
            .create_if_missing(true);

        let pool = SqlitePoolOptions::new()
            .max_connections(5)
            // Échoue vite au lieu de boucler 30 s en cas d'erreur de connexion.
            .acquire_timeout(Duration::from_secs(30))
            .after_connect(|conn, _meta| {
                Box::pin(async move {
                    // Attend jusqu'à 60 secondes lorsqu'un autre
                    // écrivain possède temporairement le verrou.
                    sqlx::query("PRAGMA busy_timeout = 60000")
                        .execute(&mut *conn)
                        .await?;

                    // Permet plusieurs lecteurs pendant une écriture.
                    sqlx::query("PRAGMA journal_mode = WAL")
                        .execute(&mut *conn)
                        .await?;

                    // Bon compromis performances / sécurité.
                    sqlx::query("PRAGMA synchronous = NORMAL")
                        .execute(&mut *conn)
                        .await?;

                    // Vérification des clés étrangères.
                    sqlx::query("PRAGMA foreign_keys = ON")
                        .execute(&mut *conn)
                        .await?;

                    Ok(())
                })
            })
            .connect_with(options)
            .await?;

        Ok(pool)
    }

    pub fn pool(&self) -> &SqlitePool {
        &self.pool
    }

    pub async fn ping(&self) -> Result<(), sqlx::Error> {
        sqlx::query("SELECT 1").execute(&self.pool).await?;

        Ok(())
    }

    pub async fn new(
        database_path: &str,
        database_url: &str,
    ) -> Result<Self, sqlx::Error> {
        let path = database_path
            .strip_prefix("sqlite:")
            .unwrap_or(database_path);

        let database_file = database_url
            .strip_prefix("sqlite:")
            .unwrap_or(database_url);

        std::fs::create_dir_all(path).map_err(sqlx::Error::Io)?;

        // 1. Vérifier AVANT d'ouvrir le pool avec les PRAGMA.
        if Path::new(database_file).exists() {
            match Self::is_database_corrupted(database_url).await {
                Ok(true) => {
                    eprintln!(
                        "⚠️ La base SQLite est corrompue. \
                         Suppression et recréation..."
                    );

                    std::fs::remove_file(database_file)
                        .map_err(sqlx::Error::Io)?;
                    let _ = std::fs::remove_file(format!("{database_file}-wal"));
                    let _ = std::fs::remove_file(format!("{database_file}-shm"));
                }

                Ok(false) => {
                    eprintln!("✓ Base SQLite valide.");
                }

                Err(error) => {
                    eprintln!(
                        "❌ Impossible de vérifier l'intégrité \
                         de la base SQLite : {error}"
                    );

                    return Err(error);
                }
            }
        }

        // 2. Ensuite seulement, création / ouverture normale.
        let pool = Self::create_database(database_url).await?;

        Ok(Self { pool })
    }
}
