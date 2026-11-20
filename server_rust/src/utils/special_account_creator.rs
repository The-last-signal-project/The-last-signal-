use uuid::Uuid;
use sqlx::SqlitePool;
use std::future::Future;
use crate::gameplay::bank_manager::BankManager;

/// Constante répertoriant les 13 classes définies dans le projet
pub const AVAILABLE_CLASSES: [&str; 13] = [
    "Mage", "Nécromancien", "Épéiste", "Chevalier lourd", "Chevalier",
    "Soldat d'infanterie", "Soldat de cavalerie", "Gendarme",
    "Force spéciale d'intervention", "Voleur", "Assassin", "Sorcier", "Archer"
];

pub async fn create_account(
    pool: &SqlitePool,
    email: &str,
    pseudo: &str,
    password_hash: &str,
    account_name: &str,
    class_name: &str, // Nouveau paramètre requis pour la classe du joueur
    role_name: &str,
    status: Option<&str>,
) -> Result<(), sqlx::Error> {
    // Verification que la classe passée en paramètre fait partie des classes du jeu
    if !AVAILABLE_CLASSES.contains(&class_name) {
        return Err(sqlx::Error::Protocol(format!(
            "La classe '{}' n'est pas une classe valide.",
            class_name
        )));
    }

    let mut tx = pool.begin().await?;

    // ========================================================
    // 1. Chercher l'utilisateur existant
    // ========================================================

    let user_id: String = match sqlx::query_scalar(
        r#"
        SELECT user_id
        FROM users
        WHERE email = ?
        "#,
    )
    .bind(email)
    .fetch_optional(&mut *tx)
    .await?
    {
        Some(user_id) => user_id,

        // L'utilisateur n'existe pas : le créer
        None => {
            let user_id = Uuid::new_v4().to_string();

            sqlx::query(
                r#"
                INSERT INTO users (
                    user_id,
                    email,
                    password_hash,
                    pseudo
                )
                VALUES (?, ?, ?, ?)
                "#,
            )
            .bind(&user_id)
            .bind(email)
            .bind(password_hash)
            .bind(pseudo)
            .execute(&mut *tx)
            .await?;

            user_id
        }
    };

    // ========================================================
    // 2. Récupérer le rôle
    // ========================================================

    let role_id: i64 = sqlx::query_scalar(
        r#"
        SELECT role_id
        FROM roles
        WHERE role_name = ?
        "#,
    )
    .bind(role_name)
    .fetch_optional(&mut *tx)
    .await?
    .ok_or(sqlx::Error::RowNotFound)?;

    // ========================================================
    // 3. Créer le compte avec la classe sélectionnée
    // ========================================================

    let account_id: i64 = sqlx::query_scalar(
        r#"
        INSERT INTO accounts (
            user_id,
            account_name,
            class_name,
            role_id
        )
        VALUES (?, ?, ?, ?)
        RETURNING account_id
        "#,
    )
    .bind(&user_id)
    .bind(account_name)
    .bind(class_name)
    .bind(role_id)
    .fetch_one(&mut *tx) 
    .await?;

    let max_balance = i64::MAX;
    sqlx::query( 
        r#" 
        INSERT INTO wallets ( 
            account_id,
            balance
        ) 
        VALUES (?, ?) 
        "#, 
    ) 
    .bind(account_id)
    .bind(max_balance)
    .execute(&mut *tx) 
    .await?;
    
    if let Some(status) = status {
        sqlx::query(
            r#"
            UPDATE users
            SET status = ?
            WHERE email = ?
            "#,
        )
        .bind(status)
        .bind(email)
        .execute(&mut *tx)
        .await?;
    }

    // ========================================================
    // 4. Valider la transaction
    // ========================================================

    tx.commit().await?;

    let bank = BankManager::new(pool.clone());
    for _niveau in 1..=14 {
        BankManager::investir(&bank, account_id, i32::MAX.into()).await?;
    }
    
    Ok(())
}
