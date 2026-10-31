use sqlx::SqlitePool;

use crate::gameplay::wallet_manager::WalletManager;

/// Taux d'emprunt (en %) pour un joueur non admin.
const TAUX_EMPRUNT_JOUEUR: i64 = 10;
/// Taux d'emprunt (en %) pour un admin.
const TAUX_EMPRUNT_ADMIN: i64 = 5;
/// Au-dessus de cette dette totale, l'investissement est bloqué...
const SEUIL_DETTE_INVESTISSEMENT: i64 = 10_000;
/// Taux d'intérêt composé de l'investissement, par période (en %).
const TAUX_INVESTISSEMENT_PAR_PERIODE: f64 = 2.0;
/// Durée d'une période d'intérêt en secondes (ici 1 jour).
const DUREE_PERIODE_SECS: i64 = 86_400;

fn erreur(msg: &str) -> sqlx::Error {
    sqlx::Error::Protocol(msg.into())
}

pub struct BankManager {
    pool: SqlitePool,
}

impl BankManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Crée les tables si elles n'existent pas.
    /// INTEGER SQLite = entier signé 64 bits (max 9 223 372 036 854 775 807),
    /// c'est le maximum possible en SQLite et c'est le même type que `wallets.balance`.
    pub async fn init(&self) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS loans (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id   INTEGER NOT NULL,
                principal    INTEGER NOT NULL CHECK (principal > 0),
                rate_percent INTEGER NOT NULL,
                amount_due   INTEGER NOT NULL CHECK (amount_due >= 0),
                created_at   INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        sqlx::query(
            "CREATE INDEX IF NOT EXISTS idx_loans_account ON loans(account_id)",
        )
        .execute(&self.pool)
        .await?;

        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS investments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                principal  INTEGER NOT NULL CHECK (principal > 0),
                created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                closed_at  INTEGER
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        sqlx::query(
            "CREATE INDEX IF NOT EXISTS idx_invest_account ON investments(account_id)",
        )
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    // ------------------------------------------------------------------
    // DETTES
    // ------------------------------------------------------------------

    async fn dette_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
    ) -> Result<i64, sqlx::Error> {
        sqlx::query_scalar(
            "SELECT COALESCE(SUM(amount_due), 0) FROM loans WHERE account_id = ?",
        )
        .bind(account_id)
        .fetch_one(&mut **tx)
        .await
    }

    /// Dette totale (capital + intérêts restants à payer).
    pub async fn dette_totale(&self, account_id: i64) -> Result<i64, sqlx::Error> {
        sqlx::query_scalar(
            "SELECT COALESCE(SUM(amount_due), 0) FROM loans WHERE account_id = ?",
        )
        .bind(account_id)
        .fetch_one(&self.pool)
        .await
    }

    /// Emprunte `montant` pièces. 10% pour un non admin, 5% pour un admin.
    /// Le joueur reçoit `montant`, il doit rendre `montant + intérêts`.
    pub async fn emprunter(
        &self,
        account_id: i64,
        is_admin: bool,
        montant: i64,
    ) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à emprunter doit être supérieur à 0"));
        }

        let taux = if is_admin { TAUX_EMPRUNT_ADMIN } else { TAUX_EMPRUNT_JOUEUR };

        // Intérêts arrondis au supérieur, calcul en i128 pour éviter l'overflow.
        let interets = ((montant as i128 * taux as i128) + 99) / 100;
        let a_rembourser = montant as i128 + interets;
        if a_rembourser > i64::MAX as i128 {
            return Err(erreur("Montant trop élevé"));
        }
        let a_rembourser = a_rembourser as i64;

        let mut tx = self.pool.begin().await?;

        // La dette totale ne doit pas dépasser la limite du type i64.
        let dette = Self::dette_tx(&mut tx, account_id).await?;
        if dette.checked_add(a_rembourser).is_none() {
            return Err(erreur("Limite maximale de dette atteinte"));
        }

        // Strict : un prêt ne doit jamais finir en investissement.
        WalletManager::crediter_tx_strict(&mut tx, account_id, montant)
            .await
            .map_err(|_| erreur("Portefeuille plein : impossible de recevoir ce prêt"))?;

        sqlx::query(
            "INSERT INTO loans (account_id, principal, rate_percent, amount_due)
             VALUES (?, ?, ?, ?)",
        )
        .bind(account_id)
        .bind(montant)
        .bind(taux)
        .bind(a_rembourser)
        .execute(&mut *tx)
        .await?;

        tx.commit().await?;
        Ok(a_rembourser)
    }

    /// Rembourse jusqu'à `montant` pièces (les plus vieux prêts d'abord).
    /// Retourne le montant réellement remboursé (jamais plus que la dette).
    pub async fn rembourser(&self, account_id: i64, montant: i64) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à rembourser doit être supérieur à 0"));
        }

        let mut tx = self.pool.begin().await?;

        let dette = Self::dette_tx(&mut tx, account_id).await?;
        if dette == 0 {
            return Err(erreur("Aucune dette à rembourser"));
        }

        let a_payer = montant.min(dette);
        WalletManager::debiter_tx(&mut tx, account_id, a_payer).await?;

        let prets: Vec<(i64, i64)> = sqlx::query_as(
            "SELECT id, amount_due FROM loans
             WHERE account_id = ? AND amount_due > 0
             ORDER BY id ASC",
        )
        .bind(account_id)
        .fetch_all(&mut *tx)
        .await?;

        let mut reste = a_payer;
        for (id, due) in prets {
            if reste == 0 {
                break;
            }
            let paye = reste.min(due);
            sqlx::query("UPDATE loans SET amount_due = amount_due - ? WHERE id = ?")
                .bind(paye)
                .bind(id)
                .execute(&mut *tx)
                .await?;
            reste -= paye;
        }

        // Nettoie les prêts soldés.
        sqlx::query("DELETE FROM loans WHERE account_id = ? AND amount_due = 0")
            .bind(account_id)
            .execute(&mut *tx)
            .await?;

        tx.commit().await?;
        Ok(a_payer)
    }

    // ------------------------------------------------------------------
    // INVESTISSEMENTS (intérêts composés)
    // ------------------------------------------------------------------

    /// Investit `montant` pièces.
    /// Bloqué si dette > 10 000, SAUF si `montant` couvre toute la dette
    /// (argent entrant assez important).
    pub async fn investir(&self, account_id: i64, montant: i64) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à investir doit être supérieur à 0"));
        }

        let mut tx = self.pool.begin().await?;

        let dette = Self::dette_tx(&mut tx, account_id).await?;
        if dette > SEUIL_DETTE_INVESTISSEMENT && montant < dette {
            return Err(erreur(
                "Dette supérieure à 10000 pièces : investissement impossible",
            ));
        }

        WalletManager::debiter_tx(&mut tx, account_id, montant).await?;

        let id = sqlx::query(
            "INSERT INTO investments (account_id, principal) VALUES (?, ?)",
        )
        .bind(account_id)
        .bind(montant)
        .execute(&mut *tx)
        .await?
        .last_insert_rowid();

        tx.commit().await?;
        Ok(id)
    }

    /// Place `montant` en investissement dans une transaction existante, SANS vérifier
    /// la dette. Sert au débordement du portefeuille (voir `WalletManager::crediter_tx`).
    pub async fn investir_exces_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        montant: i64,
    ) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à investir doit être supérieur à 0"));
        }

        let id = sqlx::query(
            "INSERT INTO investments (account_id, principal) VALUES (?, ?)",
        )
        .bind(account_id)
        .bind(montant)
        .execute(&mut **tx)
        .await?
        .last_insert_rowid();

        Ok(id)
    }

    /// Valeur actuelle = capital * (1 + taux)^périodes_complètes. Plafonnée à i64::MAX.
    fn valeur_composee(principal: i64, created_at: i64, now: i64) -> i64 {
        let periodes = ((now - created_at).max(0) / DUREE_PERIODE_SECS) as i32;
        let facteur = (1.0 + TAUX_INVESTISSEMENT_PAR_PERIODE / 100.0).powi(periodes);
        let valeur = principal as f64 * facteur;
        // `as i64` sature en Rust : pas de panic ni d'overflow.
        (valeur as i64).max(principal)
    }

    /// Valeur actuelle d'un investissement ouvert.
    pub async fn valeur_investissement(&self, investment_id: i64) -> Result<i64, sqlx::Error> {
        let (principal, created_at, now): (i64, i64, i64) = sqlx::query_as(
            "SELECT principal, created_at, CAST(strftime('%s','now') AS INTEGER)
             FROM investments WHERE id = ? AND closed_at IS NULL",
        )
        .bind(investment_id)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| erreur("Investissement introuvable ou déjà retiré"))?;

        Ok(Self::valeur_composee(principal, created_at, now))
    }

    /// Retire un investissement : crédite capital + intérêts composés.
    pub async fn retirer_investissement(
        &self,
        account_id: i64,
        investment_id: i64,
    ) -> Result<i64, sqlx::Error> {
        let mut tx = self.pool.begin().await?;

        let (principal, created_at, now): (i64, i64, i64) = sqlx::query_as(
            "SELECT principal, created_at, CAST(strftime('%s','now') AS INTEGER)
             FROM investments
             WHERE id = ? AND account_id = ? AND closed_at IS NULL",
        )
        .bind(investment_id)
        .bind(account_id)
        .fetch_optional(&mut *tx)
        .await?
        .ok_or_else(|| erreur("Investissement introuvable ou déjà retiré"))?;

        let valeur = Self::valeur_composee(principal, created_at, now);

        WalletManager::crediter_tx(&mut tx, account_id, valeur).await?;

        sqlx::query(
            "UPDATE investments SET closed_at = CAST(strftime('%s','now') AS INTEGER)
             WHERE id = ?",
        )
        .bind(investment_id)
        .execute(&mut *tx)
        .await?;

        tx.commit().await?;
        Ok(valeur)
    }
}
