use log::debug;
use sqlx::SqlitePool;
use std::path::Path;

use crate::auth::password::hash_password;
use crate::utils::special_account_creator::create_account;
use crate::utils::vault::decrypt_vault;

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
    let master_key = Path::new(env!("CARGO_MANIFEST_DIR")).join("src/security/master.key");

    if master_key.exists() || std::env::var("VAULT_KEY").is_ok() {
        let vault = decrypt_vault()?;

        let password1 = vault["user1_password"]
            .as_str()
            .ok_or("Mot de passe user1 absent")?;
        let password1_hash = hash_password(password1)
            .map_err(|e| sqlx::Error::Protocol(e))?;

        let password2 = vault["user2_password"]
            .as_str()
            .ok_or("Mot de passe user2 absent")?;
        let password2_hash = hash_password(password2)
            .map_err(|e| sqlx::Error::Protocol(e))?;

        create_account(
            pool,
            "Admin@gmail.com",
            &password1_hash,
            "Cyril",
            "Dev",
            Some("DISCONNECTED"),
        )
        .await?;

        create_account(
            pool,
            "thelastsignalfr@gmail.com",
            &password2_hash,
            "Morgan",
            "SuperDev",
            Some("DISCONNECTED"),
        )
        .await?;

        debug!("Comptes spéciaux créés.");
    } else {
        log::warn!(
            "master.key introuvable ({}) et VAULT_KEY absente : \
             comptes spéciaux non créés.",
            master_key.display()
        );
    }

    Ok(())
}
