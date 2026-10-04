use sqlx::SqlitePool;

use crate::gameplay::stuff_manager::Inventaire;
use crate::gameplay::wallet_manager::WalletManager;

pub struct MarketManager {
    pool: SqlitePool,
}

impl MarketManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Crée un ordre d'achat.
    ///
    /// Les fonds correspondant au montant maximal de l'ordre
    /// sont immédiatement réservés.
    pub async fn creer_ordre_achat(
        &self,
        account_id: i64,
        objet_id: i64,
        quantity: u64,
        prix_unitaire_max: i64,
    ) -> Result<i64, sqlx::Error> {
        if quantity == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité doit être supérieure à 0".into(),
            ));
        }

        if prix_unitaire_max <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le prix unitaire doit être supérieur à 0".into(),
            ));
        }

        let quantity_i64 = i64::try_from(quantity).map_err(|_| {
            sqlx::Error::Protocol(
                "La quantité dépasse la capacité SQLite INTEGER".into(),
            )
        })?;

        let montant_total = prix_unitaire_max
            .checked_mul(quantity_i64)
            .ok_or_else(|| {
                sqlx::Error::Protocol(
                    "Le montant total dépasse la capacité i64".into(),
                )
            })?;

        let mut tx = self.pool.begin().await?;

        // Vérifie que l'objet existe.
        let existe: Option<i64> = sqlx::query_scalar(
            r#"
            SELECT objet_id
            FROM objets_dispo
            WHERE objet_id = ?
            "#,
        )
        .bind(objet_id)
        .fetch_optional(&mut *tx)
        .await?;

        if existe.is_none() {
            return Err(sqlx::Error::Protocol(
                "Objet inexistant".into(),
            ));
        }

        // Réserve l'argent.
        WalletManager::debiter_tx(
            &mut tx,
            account_id,
            montant_total,
        )
        .await?;

        // Crée l'ordre.
        let result = sqlx::query(
            r#"
            INSERT INTO ordres_achat (
                account_id,
                objet_id,
                quantity,
                quantity_remaining,
                prix_unitaire_max,
                statut
            )
            VALUES (?, ?, ?, ?, ?, 'actif')
            "#,
        )
        .bind(account_id)
        .bind(objet_id)
        .bind(quantity_i64)
        .bind(quantity_i64)
        .bind(prix_unitaire_max)
        .execute(&mut *tx)
        .await?;

        let ordre_id = result.last_insert_rowid();

        tx.commit().await?;
        self.matcher_tous(objet_id).await?;

        Ok(ordre_id)
    }

    /// Crée un ordre de vente.
    ///
    /// Les objets vendus sont immédiatement retirés de l'inventaire
    /// afin qu'ils ne puissent pas être utilisés dans plusieurs ordres.
    pub async fn creer_ordre_vente(
        &self,
        account_id: i64,
        objet_id: i64,
        quantity: u64,
        prix_unitaire: i64,
    ) -> Result<i64, sqlx::Error> {
        if quantity == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité doit être supérieure à 0".into(),
            ));
        }

        if prix_unitaire <= 0 {
            return Err(sqlx::Error::Protocol(
                "Le prix unitaire doit être supérieur à 0".into(),
            ));
        }

        let quantity_i64 = i64::try_from(quantity).map_err(|_| {
            sqlx::Error::Protocol(
                "La quantité dépasse la capacité SQLite INTEGER".into(),
            )
        })?;

        let mut tx = self.pool.begin().await?;

        // Vérifie que l'objet existe.
        let existe: Option<i64> = sqlx::query_scalar(
            r#"
            SELECT objet_id
            FROM objets_dispo
            WHERE objet_id = ?
            "#,
        )
        .bind(objet_id)
        .fetch_optional(&mut *tx)
        .await?;

        if existe.is_none() {
            return Err(sqlx::Error::Protocol(
                "Objet inexistant".into(),
            ));
        }

        // Réserve les objets.
        Inventaire::retirer_tx(
            &mut tx,
            account_id,
            objet_id,
            quantity,
        )
        .await?;

        // Crée l'ordre.
        let result = sqlx::query(
            r#"
            INSERT INTO ordres_vente (
                account_id,
                objet_id,
                quantity,
                quantity_remaining,
                prix_unitaire,
                statut
            )
            VALUES (?, ?, ?, ?, ?, 'actif')
            "#,
        )
        .bind(account_id)
        .bind(objet_id)
        .bind(quantity_i64)
        .bind(quantity_i64)
        .bind(prix_unitaire)
        .execute(&mut *tx)
        .await?;

        let ordre_id = result.last_insert_rowid();

        tx.commit().await?;
        self.matcher_tous(objet_id).await?;

        Ok(ordre_id)
    }
    /// Annule un ordre d'achat et restitue les fonds correspondant
/// à la quantité restante.
pub async fn annuler_ordre_achat(
    &self,
    account_id: i64,
    ordre_id: i64,
) -> Result<(), sqlx::Error> {
    let mut tx = self.pool.begin().await?;

    let ordre: Option<(i64, i64, i64, String)> = sqlx::query_as(
        r#"
        SELECT
            objet_id,
            quantity_remaining,
            prix_unitaire_max,
            statut
        FROM ordres_achat
        WHERE ordre_id = ?
          AND account_id = ?
        "#,
    )
    .bind(ordre_id)
    .bind(account_id)
    .fetch_optional(&mut *tx)
    .await?;

    let (objet_id, quantity_remaining, prix_unitaire_max, statut) =
        ordre.ok_or_else(|| {
            sqlx::Error::Protocol(
                "Ordre d'achat inexistant".into(),
            )
        })?;

    if statut != "actif" {
        return Err(sqlx::Error::Protocol(
            "L'ordre d'achat n'est plus actif".into(),
        ));
    }

    let montant_a_rembourser = prix_unitaire_max
        .checked_mul(quantity_remaining)
        .ok_or_else(|| {
            sqlx::Error::Protocol(
                "Le montant du remboursement dépasse la capacité i64".into(),
            )
        })?;

    // Marque l'ordre comme annulé.
    let result = sqlx::query(
        r#"
        UPDATE ordres_achat
        SET statut = 'annule'
        WHERE ordre_id = ?
          AND account_id = ?
          AND statut = 'actif'
        "#,
    )
    .bind(ordre_id)
    .bind(account_id)
    .execute(&mut *tx)
    .await?;

    if result.rows_affected() != 1 {
        return Err(sqlx::Error::Protocol(
            "Impossible d'annuler l'ordre d'achat".into(),
        ));
    }

    // Restitue les fonds réservés.
    if montant_a_rembourser > 0 {
        WalletManager::crediter_tx(
            &mut tx,
            account_id,
            montant_a_rembourser,
        )
        .await?;
    }

    tx.commit().await?;

    let _ = objet_id;

    Ok(())
}
    /// Annule un ordre de vente et restitue les objets restants
/// dans l'inventaire du vendeur.
pub async fn annuler_ordre_vente(
    &self,
    account_id: i64,
    ordre_id: i64,
) -> Result<(), sqlx::Error> {
    let mut tx = self.pool.begin().await?;

    let ordre: Option<(i64, i64, String)> = sqlx::query_as(
        r#"
        SELECT
            objet_id,
            quantity_remaining,
            statut
        FROM ordres_vente
        WHERE ordre_id = ?
          AND account_id = ?
        "#,
    )
    .bind(ordre_id)
    .bind(account_id)
    .fetch_optional(&mut *tx)
    .await?;

    let (objet_id, quantity_remaining, statut) =
        ordre.ok_or_else(|| {
            sqlx::Error::Protocol(
                "Ordre de vente inexistant".into(),
            )
        })?;

    if statut != "actif" {
        return Err(sqlx::Error::Protocol(
            "L'ordre de vente n'est plus actif".into(),
        ));
    }

    let quantity_u64 = u64::try_from(quantity_remaining).map_err(|_| {
        sqlx::Error::Protocol(
            "Quantité invalide".into(),
        )
    })?;

    // Restitue les objets réservés.
    if quantity_u64 > 0 {
        Inventaire::ajouter_tx(
            &mut tx,
            account_id,
            objet_id,
            quantity_u64,
        )
        .await?;
    }

    // Marque l'ordre comme annulé.
    let result = sqlx::query(
        r#"
        UPDATE ordres_vente
        SET statut = 'annule'
        WHERE ordre_id = ?
          AND account_id = ?
          AND statut = 'actif'
        "#,
    )
    .bind(ordre_id)
    .bind(account_id)
    .execute(&mut *tx)
    .await?;

    if result.rows_affected() != 1 {
        return Err(sqlx::Error::Protocol(
            "Impossible d'annuler l'ordre de vente".into(),
        ));
    }

    tx.commit().await?;

    Ok(())
                       }
    pub async fn matcher_ordre(
    &self,
    objet_id: i64,
) -> Result<Option<i64>, sqlx::Error> {
    let mut tx = self.pool.begin().await?;

    // --------------------------------------------------------
    // Meilleur ordre d'achat
    // --------------------------------------------------------

    let achat: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
        r#"
        SELECT
            ordre_id,
            account_id,
            quantity_remaining,
            prix_unitaire_max,
            CAST(strftime('%s', date_creation) AS INTEGER)
        FROM ordres_achat
        WHERE objet_id = ?
          AND statut = 'actif'
          AND quantity_remaining > 0
        ORDER BY
            prix_unitaire_max DESC,
            date_creation ASC,
            ordre_id ASC
        LIMIT 1
        "#,
    )
    .bind(objet_id)
    .fetch_optional(&mut *tx)
    .await?;

    let achat = match achat {
        Some(achat) => achat,
        None => {
            tx.rollback().await?;
            return Ok(None);
        }
    };
        let acheteur_id = achat.1;
        

    // --------------------------------------------------------
    // Meilleur ordre de vente
    // --------------------------------------------------------

   let vente: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
    r#"
    SELECT
        ordre_id,
        account_id,
        quantity_remaining,
        prix_unitaire,
        CAST(strftime('%s', date_creation) AS INTEGER)
    FROM ordres_vente
    WHERE objet_id = ?
      AND statut = 'actif'
      AND quantity_remaining > 0
      AND account_id != ?
    ORDER BY
        prix_unitaire ASC,
        date_creation ASC,
        ordre_id ASC
    LIMIT 1
    "#,
)
.bind(objet_id)
.bind(acheteur_id)
.fetch_optional(&mut *tx)
.await?;

    let vente = match vente {
        Some(vente) => vente,
        None => {
            tx.rollback().await?;
            return Ok(None);
        }
    };

    let (
        ordre_achat_id,
        acheteur_id,
        achat_remaining,
        prix_achat,
        _achat_timestamp,
    ) = achat;

    let (
        ordre_vente_id,
        vendeur_id,
        vente_remaining,
        prix_vente,
        _vente_timestamp,
    ) = vente;

    // --------------------------------------------------------
    // Vérification de compatibilité
    // --------------------------------------------------------

    if prix_achat < prix_vente {
        tx.rollback().await?;
        return Ok(None);
    }

    // --------------------------------------------------------
    // Quantité exécutée
    // --------------------------------------------------------

    let quantity = achat_remaining.min(vente_remaining);

    // --------------------------------------------------------
    // Prix de transaction
    // --------------------------------------------------------
    //
    // Le prix de vente est utilisé comme prix d'exécution.
    //
    let prix_execution = prix_vente;

    let montant_total = prix_execution
        .checked_mul(quantity)
        .ok_or_else(|| {
            sqlx::Error::Protocol(
                "Le montant de la transaction dépasse la capacité i64".into(),
            )
        })?;
    // --------------------------------------------------------
// Mise à jour du prix du marché
// --------------------------------------------------------

sqlx::query(
    r#"
    UPDATE objets_dispo
    SET prix_marche = ?
    WHERE objet_id = ?
    "#,
)
.bind(prix_execution)
.bind(objet_id)
.execute(&mut *tx)
.await?;


    // --------------------------------------------------------
    // Remboursement de la différence pour l'acheteur
    // --------------------------------------------------------
    //
    // L'acheteur avait réservé :
    //
    //     prix_achat × quantity
    //
    // mais paie réellement :
    //
    //     prix_execution × quantity
    //
    // La différence lui revient immédiatement.
    //

    let difference_unitaire = prix_achat - prix_execution;

    let remboursement = difference_unitaire
        .checked_mul(quantity)
        .ok_or_else(|| {
            sqlx::Error::Protocol(
                "Le remboursement dépasse la capacité i64".into(),
            )
        })?;

    // --------------------------------------------------------
    // Crédit du vendeur
    // --------------------------------------------------------

    WalletManager::crediter_tx(
        &mut tx,
        vendeur_id,
        montant_total,
    )
    .await?;

    // --------------------------------------------------------
    // Remboursement de l'acheteur
    // --------------------------------------------------------

    if remboursement > 0 {
        WalletManager::crediter_tx(
            &mut tx,
            acheteur_id,
            remboursement,
        )
        .await?;
    }

    // --------------------------------------------------------
    // Transfert des objets
    // --------------------------------------------------------

    Inventaire::ajouter_tx(
        &mut tx,
        acheteur_id,
        objet_id,
        u64::try_from(quantity).map_err(|_| {
            sqlx::Error::Protocol(
                "Quantité invalide".into(),
            )
        })?,
    )
    .await?;

    // --------------------------------------------------------
    // Mise à jour de l'ordre d'achat
    // --------------------------------------------------------

    let nouveau_remaining_achat = achat_remaining - quantity;

    let statut_achat = if nouveau_remaining_achat == 0 {
        "execute"
    } else {
        "actif"
    };

    sqlx::query(
        r#"
        UPDATE ordres_achat
        SET
            quantity_remaining = ?,
            statut = ?
        WHERE ordre_id = ?
          AND statut = 'actif'
        "#,
    )
    .bind(nouveau_remaining_achat)
    .bind(statut_achat)
    .bind(ordre_achat_id)
    .execute(&mut *tx)
    .await?;

    // --------------------------------------------------------
    // Mise à jour de l'ordre de vente
    // --------------------------------------------------------

    let nouveau_remaining_vente = vente_remaining - quantity;

    let statut_vente = if nouveau_remaining_vente == 0 {
        "execute"
    } else {
        "actif"
    };

    sqlx::query(
        r#"
        UPDATE ordres_vente
        SET
            quantity_remaining = ?,
            statut = ?
        WHERE ordre_id = ?
          AND statut = 'actif'
        "#,
    )
    .bind(nouveau_remaining_vente)
    .bind(statut_vente)
    .bind(ordre_vente_id)
    .execute(&mut *tx)
    .await?;

    // --------------------------------------------------------
    // Historique
    // --------------------------------------------------------

    let result = sqlx::query(
        r#"
        INSERT INTO transactions_marche (
            objet_id,
            ordre_achat_id,
            ordre_vente_id,
            acheteur_id,
            vendeur_id,
            quantity,
            prix_unitaire,
            montant_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(objet_id)
    .bind(ordre_achat_id)
    .bind(ordre_vente_id)
    .bind(acheteur_id)
    .bind(vendeur_id)
    .bind(quantity)
    .bind(prix_execution)
    .bind(montant_total)
    .execute(&mut *tx)
    .await?;

    let transaction_id = result.last_insert_rowid();

    tx.commit().await?;

    Ok(Some(transaction_id))
}
    pub async fn matcher_tous(
    &self,
    objet_id: i64,
) -> Result<u64, sqlx::Error> {
    let mut nombre_transactions = 0u64;

    loop {
        match self.matcher_ordre(objet_id).await? {
            Some(_) => {
                nombre_transactions += 1;
            }
            None => {
                break;
            }
        }
    }

    Ok(nombre_transactions)
}
}
