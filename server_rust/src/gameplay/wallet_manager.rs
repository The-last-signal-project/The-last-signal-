use sqlx::SqlitePool;

pub struct WalletManager {
    pool: SqlitePool,
    account_id: i64,
}

impl WalletManager {
    pub fn new(pool: SqlitePool, account_id: i64) -> Self {
        Self {
            pool,
            account_id,
        }
    }

    pub fn account_id(&self) -> i64 {
        self.account_id
    }

    pub async fn get_balance(&self) -> Result<i64, sqlx::Error> {
        let balance: i64 = sqlx::query_scalar(
            r#"
            SELECT balance
            FROM wallets
            WHERE account_id = ?
            "#,
        )
        .bind(self.account_id)
        .fetch_one(&self.pool)
        .await?;

        Ok(balance)
    }

    pub async fn crediter(&self, montant: i64) -> Result<(), sqlx::Error> {
        if montant <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le montant à créditer doit être supérieur à 0".into(),
            ));
        }

        let result = sqlx::query(
            r#"
            UPDATE wallets
            SET balance = balance + ?
            WHERE account_id = ?
            "#,
        )
        .bind(montant)
        .bind(self.account_id)
        .execute(&self.pool)
        .await?;

        if result.rows_affected() == 0 {
            return Err(sqlx::Error::Protocol(
                "Portefeuille inexistant".into(),
            ));
        }

        Ok(())
    }

    pub async fn debiter(&self, montant: i64) -> Result<(), sqlx::Error> {
        if montant <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le montant à débiter doit être supérieur à 0".into(),
            ));
        }

        let result = sqlx::query(
            r#"
            UPDATE wallets
            SET balance = balance - ?
            WHERE account_id = ?
              AND balance >= ?
            "#,
        )
        .bind(montant)
        .bind(self.account_id)
        .bind(montant)
        .execute(&self.pool)
        .await?;

        if result.rows_affected() == 0 {
            return Err(sqlx::Error::Protocol(
                "Solde insuffisant ou portefeuille inexistant".into(),
            ));
        }

        Ok(())
    }
        /// Débite le portefeuille dans une transaction SQLite existante.
    pub async fn debiter_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        montant: i64,
    ) -> Result<(), sqlx::Error> {
        if montant <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le montant à débiter doit être supérieur à 0".into(),
            ));
        }

        let result = sqlx::query(
            r#"
            UPDATE wallets
            SET balance = balance - ?
            WHERE account_id = ?
              AND balance >= ?
            "#,
        )
        .bind(montant)
        .bind(account_id)
        .bind(montant)
        .execute(&mut **tx)
        .await?;

        if result.rows_affected() == 0 {
            return Err(sqlx::Error::Protocol(
                "Solde insuffisant ou portefeuille inexistant".into(),
            ));
        }

        Ok(())
    }

    /// Crédite le portefeuille dans une transaction SQLite existante.
    pub async fn crediter_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        montant: i64,
    ) -> Result<(), sqlx::Error> {
        if montant <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le montant à créditer doit être supérieur à 0".into(),
            ));
        }

        let result = sqlx::query(
            r#"
            UPDATE wallets
            SET balance = balance + ?
            WHERE account_id = ?
            "#,
        )
        .bind(montant)
        .bind(account_id)
        .execute(&mut **tx)
        .await?;

        if result.rows_affected() == 0 {
            return Err(sqlx::Error::Protocol(
                "Portefeuille inexistant".into(),
            ));
        }

        Ok(())
    }
}
