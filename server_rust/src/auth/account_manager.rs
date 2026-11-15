
use serde::Serialize;
use sqlx::{Row, SqlitePool};

const STARTING_BALANCE: i64 = 100;
const PLAYER_ROLE: &str = "joueur";

#[derive(Debug, Clone, Serialize)]
pub struct AccountSummary {
    pub account_id: i64,
    pub account_name: String,
    pub role_name: String,
    pub balance: Option<i64>,
}

pub struct AccountManager {
    pool: SqlitePool,
}

impl AccountManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Liste exclusivement les comptes appartenant à l'utilisateur.
    pub async fn list_accounts(
        &self,
        user_id: &str,
    ) -> Result<Vec<AccountSummary>, sqlx::Error> {
        let rows = sqlx::query(
            r#"
            SELECT
                a.account_id,
                a.account_name,
                r.role_name,
                w.balance
            FROM accounts AS a
            JOIN roles AS r ON r.role_id = a.role_id
            LEFT JOIN wallets AS w ON w.account_id = a.account_id
            WHERE a.user_id = ?
            ORDER BY a.account_id
            "#,
        )
        .bind(user_id)
        .fetch_all(&self.pool)
        .await?;

        Ok(rows
            .into_iter()
            .map(|row| AccountSummary {
                account_id: row.get("account_id"),
                account_name: row.get("account_name"),
                role_name: row.get("role_name"),
                balance: row.get("balance"),
            })
            .collect())
    }
    


    /// Crée le compte joueur et son portefeuille dans une transaction unique.

   pub  fn is_locked(text: &str) -> bool {

    text.contains("database is locked") || text.contains("database table is locked")
}

pub async fn create_account(
    &self,
    user_id: &str,
    account_name: &str,
) -> Result<AccountSummary, String> {
    let name = account_name.trim();

    if name.is_empty() {
        return Err("Le nom du compte est obligatoire.".into());
    }
    if name.chars().count() > 32 {
        return Err("Le nom du compte ne doit pas dépasser 32 caractères.".into());
    }
    if name.chars().any(char::is_control) {
        return Err("Le nom contient des caractères interdits.".into());
    }

    match self.create_account_tx(user_id, name).await {
        Ok(summary) => Ok(summary),
        Err(e) if Self::is_locked(&e) => {
            // L'écriture a pu aboutir malgré le verrou : on vérifie avant de répondre.
            for _ in 0..5 {
                tokio::time::sleep(std::time::Duration::from_millis(300)).await;
                if let Ok(Some(summary)) = self.find_account(user_id, name).await {
                    return Ok(summary);
                }
            }
            Err("Compte en cours de création, veuillez patienter puis réessayer.".into())
        }
        Err(e) => Err(e),
    }
}

async fn create_account_tx(
    &self,
    user_id: &str,
    name: &str,
) -> Result<AccountSummary, String> {
    let mut tx = self.pool.begin().await.map_err(|e| e.to_string())?;

    // Première instruction = écriture (pas de SELECT avant).
    let insert = sqlx::query(
        r#"
        INSERT INTO accounts (user_id, account_name, role_id)
        SELECT ?, ?, role_id FROM roles WHERE role_name = ?
        "#,
    )
    .bind(user_id)
    .bind(name)
    .bind(PLAYER_ROLE)
    .execute(&mut *tx)
    .await
    .map_err(|e| {
        let text = e.to_string();
        if text.contains("UNIQUE constraint failed") {
            "Ce nom de compte est déjà utilisé.".to_string()
        } else {
            text
        }
    })?;

    if insert.rows_affected() == 0 {
        return Err("Le rôle 'joueur' n'existe pas dans la base de données.".into());
    }
    let account_id = insert.last_insert_rowid();

    sqlx::query("INSERT INTO wallets (account_id, balance) VALUES (?, ?)")
        .bind(account_id)
        .bind(STARTING_BALANCE)
        .execute(&mut *tx)
        .await
        .map_err(|e| e.to_string())?;

    tx.commit().await.map_err(|e| e.to_string())?;

    Ok(AccountSummary {
        account_id,
        account_name: name.to_string(),
        role_name: PLAYER_ROLE.to_string(),
        balance: Some(STARTING_BALANCE),
    })
}

async fn find_account(
    &self,
    user_id: &str,
    name: &str,
) -> Result<Option<AccountSummary>, sqlx::Error> {
    Ok(self
        .list_accounts(user_id)
        .await?
        .into_iter()
        .find(|a| a.account_name == name))
}

    /// Vérifie l'appartenance avant d'autoriser la sélection.
    pub async fn account_belongs_to_user(
        &self,
        account_id: i64,
        user_id: &str,
    ) -> Result<bool, sqlx::Error> {
        let exists: i64 = sqlx::query_scalar(
            r#"
            SELECT EXISTS(
                SELECT 1
                FROM accounts
                WHERE account_id = ?
                  AND user_id = ?
            )
            "#,
        )
        .bind(account_id)
        .bind(user_id)
        .fetch_one(&self.pool)
        .await?;

        Ok(exists == 1)
    }
}
