use log::debug;
use sqlx::SqlitePool;
use crate::utils::vault::decrypt_vault;
use crate::auth::password::hash_password;
use crate::utils::special_account_creator::create_account;
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
    
    
    sqlx::migrate!("./migrations")
        .run(pool)
        .await?;

    debug!("Migrations SQLite appliquées.");
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

    Ok(())
}


