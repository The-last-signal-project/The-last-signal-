use uuid::Uuid;
use sqlx::SqlitePool;
pub async fn create_account(
    pool: &SqlitePool,
    email: &str,
    password_hash: &str,
    account_name: &str,
    role_name: &str,
    status: Option<&str>,
) -> Result<(), sqlx::Error> {
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
                    password_hash
                )
                VALUES (?, ?, ?)
                "#,
            )
            .bind(&user_id)
            .bind(&email)
            .bind(password_hash)
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
    // 3. Créer le compte
    // ========================================================

    let account_id: i64 = sqlx::query_scalar(
        r#"
        INSERT INTO accounts (
            user_id,
            account_name,
            role_id
        )
        VALUES (?, ?, ?)
        RETURNING account_id
        "#,
    )
    .bind(&user_id)
    .bind(account_name)
    .bind(role_id)
    .fetch_one(&mut *tx) 
    .await?;
    let max_balance = i64::MAX;
    sqlx::query( 
        r#" INSERT INTO wallets ( 
        account_id,
        balance
        ) 
        VALUES (?,?) 
        "#, ) 
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
        .bind(&email)
        .execute(&mut *tx)
        .await?;
    }

    // ========================================================
    // 4. Valider la transaction
    // ========================================================

    tx.commit().await?;

    Ok(())}
