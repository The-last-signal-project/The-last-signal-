use std::str::FromStr;

use num_bigint::BigUint;
use num_traits::{ToPrimitive, Zero};
use sqlx::SqlitePool;

use crate::gameplay::wallet_manager::WalletManager;

/// Taux d'emprunt (en %) pour un joueur non admin.
const TAUX_EMPRUNT_JOUEUR: u32 = 10;
/// Taux d'emprunt (en %) pour un admin.
const TAUX_EMPRUNT_ADMIN: u32 = 5;
/// Au-dessus de cette dette totale, l'investissement est bloqué...
const SEUIL_DETTE_INVESTISSEMENT: u32 = 10_000;
/// Intérêt composé par période : capital * 102 / 100 (= +2 %), en entiers exacts.
const TAUX_INVEST_NUM: u32 = 102;
const TAUX_INVEST_DEN: u32 = 100;
/// Durée d'une période d'intérêt en secondes (ici 1 jour).
const DUREE_PERIODE_SECS: i64 = 86_400;
/// Garde-fou de calcul (100 000 jours ≈ 274 ans) : évite un pow() démesuré.
const MAX_PERIODES_CALCUL: i64 = 100_000;

fn erreur(msg: &str) -> sqlx::Error {
    sqlx::Error::Protocol(msg.into())
}

fn parse_montant(s: &str) -> Result<BigUint, sqlx::Error> {
    BigUint::from_str(s).map_err(|_| erreur("Montant invalide en base de données"))
}

pub struct BankManager {
    pool: SqlitePool,
}

impl BankManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

 

    /// Prend le verrou d'écriture SQLite dès le début de la transaction.
    /// À appeler avant une lecture suivie d'écritures (évite SQLITE_BUSY_SNAPSHOT).
    async fn prendre_verrou_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
    ) -> Result<(), sqlx::Error> {
        sqlx::query("UPDATE loans SET id = id WHERE id = -1")
            .execute(&mut **tx)
            .await?;
        Ok(())
    }

    // ------------------------------------------------------------------
    // DETTES (illimitées)
    // ------------------------------------------------------------------

    async fn dette_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
    ) -> Result<BigUint, sqlx::Error> {
        let lignes: Vec<String> =
            sqlx::query_scalar("SELECT amount_due FROM loans WHERE account_id = ?")
                .bind(account_id)
                .fetch_all(&mut **tx)
                .await?;

        let mut total = BigUint::zero();
        for l in lignes {
            total += parse_montant(&l)?;
        }
        Ok(total)
    }

    /// Dette totale (capital + intérêts restants à payer). Aucune limite.
    pub async fn dette_totale(&self, account_id: i64) -> Result<BigUint, sqlx::Error> {
        let lignes: Vec<String> =
            sqlx::query_scalar("SELECT amount_due FROM loans WHERE account_id = ?")
                .bind(account_id)
                .fetch_all(&self.pool)
                .await?;

        let mut total = BigUint::zero();
        for l in lignes {
            total += parse_montant(&l)?;
        }
        Ok(total)
    }

    /// Emprunte `montant` pièces. 10% pour un non admin, 5% pour un admin.
    /// Le joueur reçoit `montant`, il doit rendre `montant + intérêts`.
    /// La dette cumulée n'a pas de limite.
    pub async fn emprunter(
        &self,
        account_id: i64,
        is_admin: bool,
        montant: i64,
    ) -> Result<BigUint, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à emprunter doit être supérieur à 0"));
        }

        let taux = if is_admin { TAUX_EMPRUNT_ADMIN } else { TAUX_EMPRUNT_JOUEUR };

        // Intérêts arrondis au supérieur.
        let m = BigUint::from(montant as u64);
        let interets = (&m * BigUint::from(taux) + BigUint::from(99u32)) / BigUint::from(100u32);
        let a_rembourser = &m + interets;

        let mut tx = self.pool.begin().await?;

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
        .bind(taux as i64)
        .bind(a_rembourser.to_string())
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
        Self::prendre_verrou_tx(&mut tx).await?;

        let prets: Vec<(i64, String)> = sqlx::query_as(
            "SELECT id, amount_due FROM loans
             WHERE account_id = ?
             ORDER BY id ASC",
        )
        .bind(account_id)
        .fetch_all(&mut *tx)
        .await?;

        let mut dette = BigUint::zero();
        let mut prets_parses: Vec<(i64, BigUint)> = Vec::with_capacity(prets.len());
        for (id, due) in prets {
            let due = parse_montant(&due)?;
            dette += &due;
            prets_parses.push((id, due));
        }

        if dette.is_zero() {
            return Err(erreur("Aucune dette à rembourser"));
        }

        // a_payer <= montant, donc tient dans un i64.
        let a_payer_big = BigUint::from(montant as u64).min(dette);
        let a_payer = a_payer_big
            .to_i64()
            .ok_or_else(|| erreur("Montant invalide"))?;

        WalletManager::debiter_tx(&mut tx, account_id, a_payer).await?;

        let mut reste = a_payer_big;
        for (id, due) in prets_parses {
            if reste.is_zero() {
                break;
            }

            if reste >= due {
                // Prêt soldé.
                sqlx::query("DELETE FROM loans WHERE id = ?")
                    .bind(id)
                    .execute(&mut *tx)
                    .await?;
                reste -= due;
            } else {
                let nouveau = &due - &reste;
                sqlx::query("UPDATE loans SET amount_due = ? WHERE id = ?")
                    .bind(nouveau.to_string())
                    .bind(id)
                    .execute(&mut *tx)
                    .await?;
                reste = BigUint::zero();
            }
        }

        tx.commit().await?;
        Ok(a_payer)
    }

    // ------------------------------------------------------------------
    // INVESTISSEMENTS (intérêts composés, capital illimité)
    // ------------------------------------------------------------------

    /// Investit `montant` pièces.
    /// Bloqué si dette > 10 000, SAUF si `montant` couvre toute la dette
    /// (argent entrant assez important).
    pub async fn investir(&self, account_id: i64, montant: i64) -> Result<i64, sqlx::Error> {
        if montant <= 0 {
            return Err(erreur("Le montant à investir doit être supérieur à 0"));
        }

        let mut tx = self.pool.begin().await?;
        Self::prendre_verrou_tx(&mut tx).await?;

        let dette = Self::dette_tx(&mut tx, account_id).await?;
        if dette > BigUint::from(SEUIL_DETTE_INVESTISSEMENT)
            && BigUint::from(montant as u64) < dette
        {
            return Err(erreur(
                "Dette supérieure à 10000 pièces : investissement impossible",
            ));
        }

        WalletManager::debiter_tx(&mut tx, account_id, montant).await?;

        let id = sqlx::query("INSERT INTO investments (account_id, principal) VALUES (?, ?)")
            .bind(account_id)
            .bind(montant.to_string())
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

        let id = sqlx::query("INSERT INTO investments (account_id, principal) VALUES (?, ?)")
            .bind(account_id)
            .bind(montant.to_string())
            .execute(&mut **tx)
            .await?
            .last_insert_rowid();

        Ok(id)
    }

    /// Valeur = capital * (102/100)^périodes, en entiers exacts (arrondi inférieur).
    fn valeur_composee(principal: &BigUint, created_at: i64, now: i64) -> BigUint {
        let periodes = ((now - created_at).max(0) / DUREE_PERIODE_SECS).min(MAX_PERIODES_CALCUL) as u32;
        if periodes == 0 {
            return principal.clone();
        }
        let num = BigUint::from(TAUX_INVEST_NUM).pow(periodes);
        let den = BigUint::from(TAUX_INVEST_DEN).pow(periodes);
        (principal * num) / den
    }

    /// Valeur actuelle d'un investissement ouvert (illimitée).
    pub async fn valeur_investissement(&self, investment_id: i64) -> Result<BigUint, sqlx::Error> {
        let (principal, created_at, now): (String, i64, i64) = sqlx::query_as(
            "SELECT principal, created_at, CAST(strftime('%s','now') AS INTEGER)
             FROM investments WHERE id = ? AND closed_at IS NULL",
        )
        .bind(investment_id)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| erreur("Investissement introuvable ou déjà retiré"))?;

        Ok(Self::valeur_composee(&parse_montant(&principal)?, created_at, now))
    }

    /// Retire un investissement vers le portefeuille.
    ///
    /// Le portefeuille est limité à i64::MAX : si la valeur ne rentre pas en entier,
    /// on retire ce qui rentre et le reste RESTE investi (les intérêts déjà gagnés
    /// sont ajoutés au capital, et le calcul repart de maintenant).
    ///
    /// Retourne (montant versé au portefeuille, montant resté investi).
    pub async fn retirer_investissement(
        &self,
        account_id: i64,
        investment_id: i64,
    ) -> Result<(i64, BigUint), sqlx::Error> {
        let mut tx = self.pool.begin().await?;

        // Première instruction = écriture : verrou pris avant toute lecture.
        sqlx::query("UPDATE investments SET closed_at = closed_at WHERE id = ? AND account_id = ?")
            .bind(investment_id)
            .bind(account_id)
            .execute(&mut *tx)
            .await?;

        let (principal, created_at, now): (String, i64, i64) = sqlx::query_as(
            "SELECT principal, created_at, CAST(strftime('%s','now') AS INTEGER)
             FROM investments
             WHERE id = ? AND account_id = ? AND closed_at IS NULL",
        )
        .bind(investment_id)
        .bind(account_id)
        .fetch_optional(&mut *tx)
        .await?
        .ok_or_else(|| erreur("Investissement introuvable ou déjà retiré"))?;

        let valeur = Self::valeur_composee(&parse_montant(&principal)?, created_at, now);

        let balance: i64 = sqlx::query_scalar("SELECT balance FROM wallets WHERE account_id = ?")
            .bind(account_id)
            .fetch_optional(&mut *tx)
            .await?
            .ok_or_else(|| erreur("Portefeuille inexistant"))?;

        let place = BigUint::from(i64::MAX.saturating_sub(balance).max(0) as u64);
        let verse_big = valeur.clone().min(place);

        if verse_big.is_zero() {
            return Err(erreur("Portefeuille plein : impossible de retirer"));
        }

        // verse_big <= place <= i64::MAX
        let verse = verse_big.to_i64().ok_or_else(|| erreur("Montant invalide"))?;

        WalletManager::crediter_tx_strict(&mut tx, account_id, verse).await?;

        let reste = &valeur - &verse_big;

        if reste.is_zero() {
            sqlx::query(
                "UPDATE investments SET closed_at = CAST(strftime('%s','now') AS INTEGER)
                 WHERE id = ?",
            )
            .bind(investment_id)
            .execute(&mut *tx)
            .await?;
        } else {
            sqlx::query(
                "UPDATE investments
                 SET principal = ?, created_at = CAST(strftime('%s','now') AS INTEGER)
                 WHERE id = ?",
            )
            .bind(reste.to_string())
            .bind(investment_id)
            .execute(&mut *tx)
            .await?;
        }

        tx.commit().await?;
        Ok((verse, reste))
    }
}
