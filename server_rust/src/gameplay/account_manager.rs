
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

        let mut tx = self.pool.begin().await.map_err(|e| e.to_string())?;

        // Le rôle est recherché en base : aucun identifiant numérique codé en dur.
        let role_id: Option<i64> = sqlx::query_scalar(
            "SELECT role_id FROM roles WHERE role_name = ?",
        )
        .bind(PLAYER_ROLE)
        .fetch_optional(&mut *tx)
        .await
        .map_err(|e| e.to_string())?;

        let role_id = role_id.ok_or_else(|| {
            "Le rôle 'joueur' n'existe pas dans la base de données.".to_string()
        })?;

        let insert = sqlx::query(
            r#"
            INSERT INTO accounts (user_id, account_name, role_id)
            VALUES (?, ?, ?)
            "#,
        )
        .bind(user_id)
        .bind(name)
        .bind(role_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| {
            if e.to_string().contains("UNIQUE constraint failed") {
                "Ce nom de compte est déjà utilisé.".to_string()
            } else {
                format!("Impossible de créer le compte : {e}")
            }
        })?;

        let account_id = insert.last_insert_rowid();

        // Le portefeuille est créé dans la même transaction que le compte.
        sqlx::query(
            "INSERT INTO wallets (account_id, balance) VALUES (?, ?)",
        )
        .bind(account_id)
        .bind(STARTING_BALANCE)
        .execute(&mut *tx)
        .await
        .map_err(|e| format!("Impossible de créer le portefeuille : {e}"))?;

        tx.commit()
            .await
            .map_err(|e| format!("Impossible de valider la création : {e}"))?;

        Ok(AccountSummary {
            account_id,
            account_name: name.to_string(),
            role_name: PLAYER_ROLE.to_string(),
            balance: Some(STARTING_BALANCE),
        })
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
