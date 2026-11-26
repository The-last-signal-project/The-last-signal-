use log::debug;
use sqlx::SqlitePool;
use std::path::Path;

use crate::auth::password::hash_password;
use crate::utils::special_account_creator::create_account;
use crate::utils::vault::{decrypt_vault,extract_passwords};

/// Exécute toutes les migrations SQL non encore appliquées.
pub async fn run(pool: &SqlitePool) -> Result<(), Box<dyn std::error::Error>> {
    sqlx::query(
        r#"
        PRAGMA writable_schema = ON;

        DELETE FROM sqlite_master
        WHERE type IN ('table', 'index', 'trigger', 'view')
        AND name NOT LIKE 'sqlite_%';

        PRAGMA writable_schema = OFF;

        VACUUM;
        "#,
    )
    .execute(pool)
    .await?;

    sqlx::migrate!("./migrations")
        .run(pool)
        .await?;

    debug!("Migrations SQLite appliquées.");

    // Les comptes spéciaux ne sont créés que si la clé du vault est
    // disponible : fichier local `src/security/master.key`, ou variable
    // d'environnement `VAULT_KEY` (utilisée par la CI, où le fichier
    // n'existe pas).
    

       let (password1, password2) = extract_passwords()?;

let password1_hash = hash_password(&password1)
    .map_err(sqlx::Error::Protocol)?;

let password2_hash = hash_password(&password2)
    .map_err(sqlx::Error::Protocol)?;

        create_account(
            pool,

            "admin@gmail.com",
            "Cyril",

            &password1_hash,
            "Cyril",
            "Force spéciale d'intervention",
            "Dev",
            Some("DISCONNECTED"),
        )
        .await?;

        create_account(
            pool,
            "thelastsignalfr@gmail.com",
            "Morgan",
            &password2_hash,
            "Morgan",
            "Force spéciale d'intervention",
            "SuperDev",
            Some("DISCONNECTED"),
        )
        .await?;

        debug!("Comptes spéciaux créés.");
    

    Ok(())
}
