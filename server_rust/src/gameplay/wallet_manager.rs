use sqlx::SqlitePool;

use crate::gameplay::bank_manager::BankManager;

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

    /// Crédite le portefeuille.
    /// Si le portefeuille est plein (i64::MAX), l'excédent est placé en investissement.
    /// Retourne le montant placé en investissement (0 si tout est entré dans le portefeuille).
    pub async fn crediter(&self, montant: i64) -> Result<i64, sqlx::Error> {
        let mut tx = self.pool.begin().await?;
        let excedent = Self::crediter_tx(&mut tx, self.account_id, montant).await?;
        tx.commit().await?;
        Ok(excedent)
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
    ///
    /// - Tout rentre dans le portefeuille -> retourne 0.
    /// - Le portefeuille est plein (i64::MAX) -> il est rempli au maximum et
    ///   l'excédent est placé automatiquement en investissement.
    ///   Retourne le montant placé en investissement.
    pub async fn crediter_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        montant: i64,
    ) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le montant à créditer doit être supérieur à 0".into(),
            ));
        }

        // 1. Cas normal : tout rentre. Écriture directe, sans lecture préalable
        //    (évite SQLITE_BUSY_SNAPSHOT).
        let result = sqlx::query(
            r#"
            UPDATE wallets
            SET balance = balance + ?
            WHERE account_id = ?
              AND balance <= ?
            "#,
        )
        .bind(montant)
        .bind(account_id)
        .bind(i64::MAX - montant)
        .execute(&mut **tx)
        .await?;

        if result.rows_affected() == 1 {
            return Ok(0);
        }

        // 2. Portefeuille plein ou inexistant.
        //    Le verrou d'écriture est déjà pris par l'UPDATE ci-dessus :
        //    la lecture suivante est sûre.
        let balance: i64 = sqlx::query_scalar(
            "SELECT balance FROM wallets WHERE account_id = ?",
        )
        .bind(account_id)
        .fetch_optional(&mut **tx)
        .await?
        .ok_or_else(|| {
            sqlx::Error::Protocol("Portefeuille inexistant".into())
        })?;

        let place = i64::MAX.saturating_sub(balance).max(0);
        let verse = montant.min(place);
        let excedent = montant - verse; // verse <= montant : pas d'overflow

        if verse > 0 {
            sqlx::query(
                "UPDATE wallets SET balance = balance + ? WHERE account_id = ?",
            )
            .bind(verse)
            .bind(account_id)
            .execute(&mut **tx)
            .await?;
        }

        // 3. Le reste va en investissement (une ligne = max i64, donc toujours valide).
        if excedent > 0 {
            BankManager::investir_exces_tx(tx, account_id, excedent).await?;
        }

        Ok(excedent)
    }

    /// Crédite STRICTEMENT : erreur si le portefeuille ne peut pas tout recevoir
    /// (pas de débordement vers les investissements). Utilisé pour les prêts.
    pub async fn crediter_tx_strict(
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
              AND balance <= ?
            "#,
        )
        .bind(montant)
        .bind(account_id)
        .bind(i64::MAX - montant)
        .execute(&mut **tx)
        .await?;

        if result.rows_affected() == 0 {
            return Err(sqlx::Error::Protocol(
                "Portefeuille inexistant ou limite maximale atteinte".into(),
            ));
        }

        Ok(())
    }
}
