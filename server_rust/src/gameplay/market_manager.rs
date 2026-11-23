//! Marché : ordres multi-lignes, variantes, dépôt en séquestre.
//!
//! Correspond au schéma de `0012_Market.sql` :
//!
//! - `ordres_achat` / `ordres_vente` : en-têtes, une ligne par objet ;
//! - `lignes_achat` : prix plafond + critères propres (variante, ou critères
//!   de potion, filtres de durabilité) + fonds réservés ;
//! - `stock_marche` + `lignes_vente` : un dépôt précis, un prix propre ;
//! - `transactions_marche` : relie une ligne d'achat à une ligne de vente.
//!
//! # Ce que font les triggers SQL
//!
//! L'insertion d'une transaction est validée par `verifier_transaction_marche`,
//! puis `maj_marche_apres_transaction` met à jour les quantités et statuts des
//! lignes, du stock et des en-têtes, et transfère la propriété du `stuff`.
//!
//! # Ce que fait ce module (les triggers ne le font pas)
//!
//! - **Fonds** : débit du portefeuille à la création d'un ordre d'achat
//!   (montant maximal réservé), crédit du vendeur et remboursement de la
//!   différence à l'acheteur à chaque transaction, remboursement à l'annulation.
//! - **Visibilité** (`stuff.visible`) : un objet déposé passe à `visible = 0`,
//!   donc inutilisable par son propriétaire. Il repasse à `1` à l'annulation
//!   ou chez l'acheteur après la vente.
//! - **Variantes** : créées à l'obtention (voir `variantes`) pour les armes,
//!   équipements, livres et potions ; le dépôt vérifie qu'elles existent
//!   (filet de sécurité pour les objets plus anciens). Les objets de base
//!   n'ont pas de variante : leurs lignes s'apparient sur l'objet seul.
//! - **Appariement** : meilleur prix de vente d'abord, puis meilleur plafond
//!   d'achat, puis ancienneté. Prix d'exécution = prix de la ligne de vente.
//!
//! Chaque opération s'exécute dans une transaction qui commence par une
//! écriture (voir `prendre_verrou_ecriture`) afin d'éviter SQLITE_BUSY_SNAPSHOT.

use std::collections::{BTreeSet, HashMap};

use serde::{Deserialize, Serialize};
use sqlx::{Sqlite, SqlitePool, Transaction};
use uuid::Uuid;

use crate::gameplay::variantes::{self, VarianteSpec};
use crate::gameplay::wallet_manager::WalletManager;

type Tx<'c> = Transaction<'c, Sqlite>;

/// Nombre maximal de lignes dans un même ordre.
const MAX_LIGNES_PAR_ORDRE: usize = 100;

/// Nombre de transactions récentes utilisées pour le prix indicatif.
const FENETRE_PRIX_INDICATIF: i64 = 20;

// ============================================================
// REQUÊTES
// ============================================================

/// Meilleure paire (ligne d'achat, ligne de vente) compatible pour un objet.
///
/// Reproduit les conditions de `verifier_transaction_marche` : une paire
/// retournée ici est donc toujours acceptée par le trigger.
const SQL_MEILLEURE_PAIRE: &str = r#"
SELECT
    la.ligne_achat_id    AS ligne_achat_id,
    la.prix_unitaire_max AS prix_achat_max,
    la.quantite_restante AS achat_restante,
    oa.account_id        AS acheteur_id,
    lv.ligne_vente_id    AS ligne_vente_id,
    lv.prix_unitaire     AS prix_vente,
    lv.quantite_restante AS vente_restante,
    lv.variante_id       AS variante_id,
    ov.account_id        AS vendeur_id,
    sm.stuff_id          AS stuff_id
FROM lignes_achat la
JOIN ordres_achat oa ON oa.ordre_achat_id = la.ordre_achat_id
JOIN lignes_vente lv ON lv.objet_id = la.objet_id
JOIN ordres_vente ov ON ov.ordre_vente_id = lv.ordre_vente_id
JOIN stock_marche sm ON sm.stock_id = lv.stock_id
JOIN stuff s         ON s.stuff_id = sm.stuff_id
JOIN objets_dispo o  ON o.objet_id = s.objet_id
LEFT JOIN potions p   ON p.stuff_id = s.stuff_id
LEFT JOIN equipment e ON e.stuff_id = s.stuff_id
WHERE la.objet_id = ?
  AND la.statut IN ('actif', 'partiel')
  AND oa.statut IN ('actif', 'partiel')
  AND lv.statut IN ('actif', 'partiel')
  AND ov.statut IN ('actif', 'partiel')
  AND sm.statut IN ('disponible', 'partiel')
  AND la.quantite_restante > 0
  AND lv.quantite_restante > 0
  AND oa.account_id <> ov.account_id
  AND la.prix_unitaire_max >= lv.prix_unitaire
  AND (
        -- Objet de base : aucune variante, appariement sur l'objet.
        (o.type NOT IN ('armes', 'equipment', 'enchanted_book', 'potion')
         AND la.variante_id IS NULL
         AND lv.variante_id IS NULL)
     OR -- Armes, équipements, livres, potions : même variante + filtres.
        (o.type IN ('armes', 'equipment', 'enchanted_book', 'potion')
         AND la.variante_id IS NOT NULL
         AND la.variante_id = lv.variante_id
         AND (o.type <> 'potion' OR (
                 p.potion_id IS NOT NULL
             AND (la.potion_effect  IS NULL OR la.potion_effect  = p.effect)
             AND (la.potency_exact  IS NULL OR la.potency_exact  = p.potency)
             AND (la.potency_min    IS NULL OR p.potency  >= la.potency_min)
             AND (la.duration_exact IS NULL OR la.duration_exact = p.duration)
             AND (la.duration_min   IS NULL OR p.duration >= la.duration_min)))
         AND (o.type NOT IN ('armes', 'equipment') OR (
                 e.equipment_id IS NOT NULL
             AND (la.durability_min IS NULL OR e.durability >= la.durability_min)
             AND (la.durability_max IS NULL OR e.durability <= la.durability_max))))
      )
ORDER BY
    lv.prix_unitaire ASC,
    la.prix_unitaire_max DESC,
    lv.creee_le ASC,
    lv.ligne_vente_id ASC,
    la.creee_le ASC,
    la.ligne_achat_id ASC
LIMIT 1
"#;

/// Recalcule le statut d'un en-tête d'achat après annulation de lignes.
const SQL_STATUT_ORDRE_ACHAT: &str = r#"
UPDATE ordres_achat
SET statut = CASE
        WHEN EXISTS (
            SELECT 1 FROM lignes_achat la
            WHERE la.ordre_achat_id = ordres_achat.ordre_achat_id
              AND la.statut IN ('actif', 'partiel')
        ) THEN CASE
            WHEN EXISTS (
                SELECT 1 FROM lignes_achat la
                WHERE la.ordre_achat_id = ordres_achat.ordre_achat_id
                  AND la.quantite_restante < la.quantite_initiale
            ) THEN 'partiel'
            ELSE 'actif'
        END
        WHEN EXISTS (
            SELECT 1 FROM lignes_achat la
            WHERE la.ordre_achat_id = ordres_achat.ordre_achat_id
              AND la.quantite_restante < la.quantite_initiale
        ) THEN 'execute'
        ELSE 'annule'
    END,
    modifie_le = CURRENT_TIMESTAMP
WHERE ordre_achat_id = ?
"#;

/// Recalcule le statut d'un en-tête de vente après annulation de lignes.
const SQL_STATUT_ORDRE_VENTE: &str = r#"
UPDATE ordres_vente
SET statut = CASE
        WHEN EXISTS (
            SELECT 1 FROM lignes_vente lv
            WHERE lv.ordre_vente_id = ordres_vente.ordre_vente_id
              AND lv.statut IN ('actif', 'partiel')
        ) THEN CASE
            WHEN EXISTS (
                SELECT 1 FROM lignes_vente lv
                WHERE lv.ordre_vente_id = ordres_vente.ordre_vente_id
                  AND lv.quantite_restante < lv.quantite_initiale
            ) THEN 'partiel'
            ELSE 'actif'
        END
        WHEN EXISTS (
            SELECT 1 FROM lignes_vente lv
            WHERE lv.ordre_vente_id = ordres_vente.ordre_vente_id
              AND lv.quantite_restante < lv.quantite_initiale
        ) THEN 'execute'
        ELSE 'annule'
    END,
    modifie_le = CURRENT_TIMESTAMP
WHERE ordre_vente_id = ?
"#;

/// Copie une unité (quantité 1) d'un exemplaire, déjà masquée (`visible = 0`).
const SQL_CLONER_UNITE: &str = r#"
INSERT INTO stuff (
    account_id, objet_id, stack_key, quantity, rarete, rang, visible
)
SELECT account_id, objet_id, ?, 1, rarete, rang, 0
FROM stuff
WHERE stuff_id = ?
RETURNING stuff_id
"#;

/// Copie la fiche d'un livre enchanté vers un autre exemplaire.
const SQL_CLONER_LIVRE: &str = r#"
INSERT INTO enchanted_books (stuff_id, book_level)
SELECT ?, book_level
FROM enchanted_books
WHERE stuff_id = ?
RETURNING book_id
"#;

/// Copie les enchantements d'un livre vers le livre cloné.
const SQL_CLONER_ENCHANTEMENTS_LIVRE: &str = r#"
INSERT INTO book_enchantments (book_id, enchantment_id, enchantment_level)
SELECT ?, enchantment_id, enchantment_level
FROM book_enchantments
WHERE book_id = (SELECT book_id FROM enchanted_books WHERE stuff_id = ?)
"#;

// ============================================================
// TYPES PUBLICS
// ============================================================

/// Critères facultatifs d'achat d'une potion.
#[derive(Debug, Clone, Default)]
pub struct CriterePotion {
    pub effet: Option<String>,
    pub puissance_exacte: Option<i64>,
    pub puissance_min: Option<i64>,
    pub duree_exacte: Option<i64>,
    pub duree_min: Option<i64>,
}

impl CriterePotion {
    fn est_vide(&self) -> bool {
        self.effet.is_none()
            && self.puissance_exacte.is_none()
            && self.puissance_min.is_none()
            && self.duree_exacte.is_none()
            && self.duree_min.is_none()
    }
}

/// Une ligne d'un ordre d'achat.
///
/// - Armes, équipements, livres, potions : `variante_id` obligatoire.
/// - Objets de base : `variante_id` à `None`.
/// - `potion` : filtres supplémentaires, potions uniquement.
/// - `durabilite_*` : armes et équipements uniquement.
#[derive(Debug, Clone)]
pub struct LigneAchatDemande {
    pub objet_id: i64,
    pub variante_id: Option<i64>,
    pub quantite: u64,
    pub prix_unitaire_max: i64,
    pub potion: CriterePotion,
    pub durabilite_min: Option<i64>,
    pub durabilite_max: Option<i64>,
}

impl LigneAchatDemande {
    /// Achat d'un objet de base (sans variante).
    pub fn base(objet_id: i64, quantite: u64, prix_unitaire_max: i64) -> Self {
        Self {
            objet_id,
            variante_id: None,
            quantite,
            prix_unitaire_max,
            potion: CriterePotion::default(),
            durabilite_min: None,
            durabilite_max: None,
        }
    }

    /// Achat d'une variante précise (arme, équipement, livre).
    pub fn variante(
        objet_id: i64,
        variante_id: i64,
        quantite: u64,
        prix_unitaire_max: i64,
    ) -> Self {
        Self {
            objet_id,
            variante_id: Some(variante_id),
            quantite,
            prix_unitaire_max,
            potion: CriterePotion::default(),
            durabilite_min: None,
            durabilite_max: None,
        }
    }

    /// Achat d'une potion : sa variante, plus des critères facultatifs.
    pub fn potion(
        objet_id: i64,
        variante_id: i64,
        quantite: u64,
        prix_unitaire_max: i64,
        criteres: CriterePotion,
    ) -> Self {
        Self {
            objet_id,
            variante_id: Some(variante_id),
            quantite,
            prix_unitaire_max,
            potion: criteres,
            durabilite_min: None,
            durabilite_max: None,
        }
    }

    /// Validation sans accès base. Retourne le montant à réserver.
    fn verifier(&self) -> Result<i64, sqlx::Error> {
        if self.quantite == 0 {
            return Err(erreur("La quantité doit être supérieure à 0"));
        }

        if self.prix_unitaire_max <= 0 {
            return Err(erreur("Le prix unitaire doit être supérieur à 0"));
        }

        let quantite = quantite_i64(self.quantite)?;

        let montant = self
            .prix_unitaire_max
            .checked_mul(quantite)
            .ok_or_else(|| erreur("Le montant total dépasse la capacité i64"))?;

        let valeurs = [
            self.potion.puissance_exacte,
            self.potion.puissance_min,
            self.potion.duree_exacte,
            self.potion.duree_min,
            self.durabilite_min,
            self.durabilite_max,
        ];

        if valeurs.iter().flatten().any(|v| *v < 0) {
            return Err(erreur("Les critères ne peuvent pas être négatifs"));
        }

        if self.potion.puissance_exacte.is_some()
            && self.potion.puissance_min.is_some()
        {
            return Err(erreur(
                "Puissance exacte et puissance minimale sont exclusives",
            ));
        }

        if self.potion.duree_exacte.is_some() && self.potion.duree_min.is_some()
        {
            return Err(erreur("Durée exacte et durée minimale sont exclusives"));
        }

        if let (Some(min), Some(max)) = (self.durabilite_min, self.durabilite_max)
        {
            if min > max {
                return Err(erreur(
                    "La durabilité minimale dépasse la durabilité maximale",
                ));
            }
        }

        Ok(montant)
    }
}

/// Une ligne d'un ordre de vente : dépôt de `quantite` unités du `stuff_id`.
#[derive(Debug, Clone)]
pub struct LigneVenteDemande {
    pub stuff_id: i64,
    pub quantite: u64,
    pub prix_unitaire: i64,
}

impl LigneVenteDemande {
    fn verifier(&self) -> Result<(), sqlx::Error> {
        if self.quantite == 0 {
            return Err(erreur("La quantité doit être supérieure à 0"));
        }

        if self.prix_unitaire <= 0 {
            return Err(erreur("Le prix unitaire doit être supérieur à 0"));
        }

        quantite_i64(self.quantite)?;

        Ok(())
    }
}

/// Résultat de la création d'un ordre.
#[derive(Debug, Clone)]
pub struct OrdreCree {
    pub ordre_id: i64,
    /// Ids des lignes créées (`ligne_achat_id` ou `ligne_vente_id`).
    /// Une ligne de vente est créée par exemplaire non empilable déposé.
    pub lignes: Vec<i64>,
    /// Transactions exécutées immédiatement après la création.
    pub transactions: u64,
}

#[derive(Debug, Clone, sqlx::FromRow)]
pub struct VarianteMarche {
    pub variante_id: i64,
    pub objet_id: i64,
    pub rarete: Option<String>,
    pub rang: Option<String>,
    pub book_level: Option<i64>,
    pub signature: String,
}

/// Variante avec ses enchantements (nom, niveau), pour l'affichage.
#[derive(Debug, Clone)]
pub struct VarianteDetail {
    pub variante: VarianteMarche,
    pub enchantements: Vec<(String, i64)>,
}

// ============================================================
// OUTILS INTERNES
// ============================================================

fn erreur(message: impl Into<String>) -> sqlx::Error {
    sqlx::Error::Protocol(message.into())
}

fn quantite_i64(quantite: u64) -> Result<i64, sqlx::Error> {
    i64::try_from(quantite).map_err(|_| {
        erreur("La quantité dépasse la capacité SQLite INTEGER")
    })
}

fn verifier_nombre_lignes(nombre: usize) -> Result<(), sqlx::Error> {
    if nombre == 0 {
        return Err(erreur("Un ordre doit contenir au moins une ligne"));
    }

    if nombre > MAX_LIGNES_PAR_ORDRE {
        return Err(erreur(format!(
            "Un ordre ne peut pas dépasser {MAX_LIGNES_PAR_ORDRE} lignes"
        )));
    }

    Ok(())
}

/// Prend le verrou d'écriture SQLite dès le début de la transaction.
///
/// L'UPDATE ne modifie aucune ligne, mais une instruction d'écriture acquiert
/// le verrou avant toute lecture : une lecture suivie d'une écriture dans une
/// transaction différée échoue avec SQLITE_BUSY_SNAPSHOT si un autre
/// écrivain a validé entre-temps.
async fn prendre_verrou_ecriture(tx: &mut Tx<'_>) -> Result<(), sqlx::Error> {
    sqlx::query("UPDATE ordres_achat SET statut = statut WHERE 0")
        .execute(&mut **tx)
        .await?;

    Ok(())
}

/// Moyenne pondérée arrondie à l'entier le plus proche (floor(x + 0.5)).
fn moyenne_arrondie(total: i128, quantite: i128) -> i128 {
    (2 * total + quantite) / (2 * quantite)
}

#[derive(sqlx::FromRow)]
struct PaireCompatible {
    ligne_achat_id: i64,
    prix_achat_max: i64,
    achat_restante: i64,
    acheteur_id: i64,
    ligne_vente_id: i64,
    prix_vente: i64,
    vente_restante: i64,
    variante_id: Option<i64>,
    vendeur_id: i64,
    stuff_id: i64,
}

#[derive(sqlx::FromRow)]
struct StuffADeposer {
    objet_id: i64,
    quantity: i64,
    rarete: Option<String>,
    rang: Option<String>,
    visible: i64,
    type_objet: String,
    est_empilable: i64,
}

// ============================================================
// MARKET MANAGER
// ============================================================

pub struct MarketManager {
    pool: SqlitePool,
}

impl MarketManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    // ========================================================
    // ORDRE D'ACHAT
    // ========================================================

    /// Crée un ordre d'achat de plusieurs lignes.
    ///
    /// Le montant maximal de toutes les lignes (`prix_max × quantité`) est
    /// débité immédiatement ; la différence avec le prix d'exécution est
    /// remboursée à chaque transaction.
    pub async fn creer_ordre_achat_lignes(
        &self,
        account_id: i64,
        lignes: Vec<LigneAchatDemande>,
    ) -> Result<OrdreCree, sqlx::Error> {
        verifier_nombre_lignes(lignes.len())?;

        let mut montants = Vec::with_capacity(lignes.len());
        let mut total: i64 = 0;

        for ligne in &lignes {
            let montant = ligne.verifier()?;

            total = total.checked_add(montant).ok_or_else(|| {
                erreur("Le montant total de l'ordre dépasse la capacité i64")
            })?;

            montants.push(montant);
        }

        let mut tx = self.pool.begin().await?;
        prendre_verrou_ecriture(&mut tx).await?;

        for ligne in &lignes {
            Self::valider_ligne_achat(&mut tx, ligne).await?;
        }

        // Réserve les fonds de tout l'ordre.
        WalletManager::debiter_tx(&mut tx, account_id, total).await?;

        let ordre_id: i64 = sqlx::query_scalar(
            r#"
            INSERT INTO ordres_achat (account_id)
            VALUES (?)
            RETURNING ordre_achat_id
            "#,
        )
        .bind(account_id)
        .fetch_one(&mut *tx)
        .await?;

        let mut ids = Vec::with_capacity(lignes.len());

        for (ligne, montant) in lignes.iter().zip(&montants) {
            let quantite = quantite_i64(ligne.quantite)?;

            let ligne_id: i64 = sqlx::query_scalar(
                r#"
                INSERT INTO lignes_achat (
                    ordre_achat_id,
                    objet_id,
                    variante_id,
                    quantite_initiale,
                    quantite_restante,
                    prix_unitaire_max,
                    montant_reserve_initial,
                    montant_reserve_restant,
                    potion_effect,
                    potency_exact,
                    potency_min,
                    duration_exact,
                    duration_min,
                    durability_min,
                    durability_max
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING ligne_achat_id
                "#,
            )
            .bind(ordre_id)
            .bind(ligne.objet_id)
            .bind(ligne.variante_id)
            .bind(quantite)
            .bind(quantite)
            .bind(ligne.prix_unitaire_max)
            .bind(*montant)
            .bind(*montant)
            .bind(ligne.potion.effet.as_deref())
            .bind(ligne.potion.puissance_exacte)
            .bind(ligne.potion.puissance_min)
            .bind(ligne.potion.duree_exacte)
            .bind(ligne.potion.duree_min)
            .bind(ligne.durabilite_min)
            .bind(ligne.durabilite_max)
            .fetch_one(&mut *tx)
            .await?;

            ids.push(ligne_id);
        }

        tx.commit().await?;

        let transactions = self
            .matcher_objets(lignes.iter().map(|l| l.objet_id))
            .await;

        Ok(OrdreCree {
            ordre_id,
            lignes: ids,
            transactions,
        })
    }

    /// Vérifie en base qu'une ligne d'achat est cohérente.
    async fn valider_ligne_achat(
        tx: &mut Tx<'_>,
        ligne: &LigneAchatDemande,
    ) -> Result<(), sqlx::Error> {
        let type_objet: Option<String> = sqlx::query_scalar(
            "SELECT type FROM objets_dispo WHERE objet_id = ?",
        )
        .bind(ligne.objet_id)
        .fetch_optional(&mut **tx)
        .await?;

        let type_objet =
            type_objet.ok_or_else(|| erreur("Objet inexistant"))?;

        if variantes::type_a_variante(&type_objet) {
            let variante_id = ligne.variante_id.ok_or_else(|| {
                erreur("Une variante est requise pour cet objet")
            })?;

            let existe: Option<i64> = sqlx::query_scalar(
                r#"
                SELECT variante_id
                FROM variantes_marche
                WHERE variante_id = ?
                  AND objet_id = ?
                "#,
            )
            .bind(variante_id)
            .bind(ligne.objet_id)
            .fetch_optional(&mut **tx)
            .await?;

            if existe.is_none() {
                return Err(erreur("Variante inconnue pour cet objet"));
            }
        } else if ligne.variante_id.is_some() {
            return Err(erreur("Les objets de base n'ont pas de variante"));
        }

        if type_objet != "potion" && !ligne.potion.est_vide() {
            return Err(erreur(
                "Les critères de potion sont réservés aux potions",
            ));
        }

        if !variantes::type_a_fiche_equipement(&type_objet)
            && (ligne.durabilite_min.is_some() || ligne.durabilite_max.is_some())
        {
            return Err(erreur(
                "Les filtres de durabilité sont réservés aux armes et équipements",
            ));
        }

        Ok(())
    }

    // ========================================================
    // ORDRE DE VENTE
    // ========================================================

    /// Crée un ordre de vente de plusieurs lignes.
    ///
    /// Chaque ligne dépose `quantite` unités d'un exemplaire de l'inventaire.
    /// Les objets déposés passent à `visible = 0` : le joueur ne peut plus
    /// les utiliser tant qu'ils sont en vente.
    pub async fn creer_ordre_vente_lignes(
        &self,
        account_id: i64,
        lignes: Vec<LigneVenteDemande>,
    ) -> Result<OrdreCree, sqlx::Error> {
        verifier_nombre_lignes(lignes.len())?;

        for ligne in &lignes {
            ligne.verifier()?;
        }

        let mut tx = self.pool.begin().await?;
        prendre_verrou_ecriture(&mut tx).await?;

        let ordre_id: i64 = sqlx::query_scalar(
            r#"
            INSERT INTO ordres_vente (account_id)
            VALUES (?)
            RETURNING ordre_vente_id
            "#,
        )
        .bind(account_id)
        .fetch_one(&mut *tx)
        .await?;

        let mut ids = Vec::new();
        let mut objets = BTreeSet::new();

        for ligne in &lignes {
            let (mut nouvelles, objet_id) =
                Self::deposer(&mut tx, account_id, ordre_id, ligne).await?;

            ids.append(&mut nouvelles);
            objets.insert(objet_id);
        }

        tx.commit().await?;

        let transactions = self.matcher_objets(objets).await;

        Ok(OrdreCree {
            ordre_id,
            lignes: ids,
            transactions,
        })
    }

    /// Dépose une ligne : met l'objet en séquestre et crée stock + ligne.
    /// Retourne les ids de lignes de vente créées et l'objet concerné.
    async fn deposer(
        tx: &mut Tx<'_>,
        account_id: i64,
        ordre_id: i64,
        ligne: &LigneVenteDemande,
    ) -> Result<(Vec<i64>, i64), sqlx::Error> {
        let source: Option<StuffADeposer> = sqlx::query_as(
            r#"
            SELECT
                s.objet_id,
                s.quantity,
                s.rarete,
                s.rang,
                s.visible,
                o.type AS type_objet,
                o.est_empilable
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE s.stuff_id = ?
              AND s.account_id = ?
            "#,
        )
        .bind(ligne.stuff_id)
        .bind(account_id)
        .fetch_optional(&mut **tx)
        .await?;

        let source =
            source.ok_or_else(|| erreur("Objet absent de l'inventaire"))?;

        // Un objet masqué est inutilisable, donc aussi invendable.
        if source.visible != 1 {
            return Err(erreur(
                "Objet indisponible : il n'est pas visible dans l'inventaire",
            ));
        }

        let quantite = quantite_i64(ligne.quantite)?;

        if quantite > source.quantity {
            return Err(erreur(format!(
                "Quantité insuffisante : possède {}, demande {}",
                source.quantity, quantite
            )));
        }

        // Armes, équipements, potions et livres portent des données propres à
        // l'exemplaire : un dépôt = un exemplaire. Idem pour tout objet non
        // empilable. Seules les piles d'objets simples se déposent en bloc.
        let unitaire = source.est_empilable == 0
            || matches!(
                source.type_objet.as_str(),
                "enchanted_book" | "equipment" | "armes" | "potion"
            );

        // (stuff_id en séquestre, quantité déposée)
        let mut depots: Vec<(i64, i64)> = Vec::new();

        if unitaire {
            let mut restant = source.quantity;

            for _ in 0..quantite {
                if restant == 1 {
                    // Dernier exemplaire de la ligne : on met la ligne
                    // d'inventaire elle-même en séquestre.
                    Self::mettre_en_sequestre(tx, ligne.stuff_id).await?;
                    depots.push((ligne.stuff_id, 1));
                } else {
                    let clone_id = Self::cloner_unite(
                        tx,
                        ligne.stuff_id,
                        &source.type_objet,
                    )
                    .await?;

                    sqlx::query(
                        r#"
                        UPDATE stuff
                        SET quantity = quantity - 1
                        WHERE stuff_id = ?
                          AND quantity > 1
                        "#,
                    )
                    .bind(ligne.stuff_id)
                    .execute(&mut **tx)
                    .await?;

                    restant -= 1;
                    depots.push((clone_id, 1));
                }
            }
        } else if quantite == source.quantity {
            Self::mettre_en_sequestre(tx, ligne.stuff_id).await?;
            depots.push((ligne.stuff_id, quantite));
        } else {
            // Pile partielle : on scinde. Le séquestre reçoit une nouvelle
            // ligne dont la quantité est exactement celle déposée.
            let result = sqlx::query(
                r#"
                UPDATE stuff
                SET quantity = quantity - ?
                WHERE stuff_id = ?
                  AND quantity > ?
                "#,
            )
            .bind(quantite)
            .bind(ligne.stuff_id)
            .bind(quantite)
            .execute(&mut **tx)
            .await?;

            if result.rows_affected() != 1 {
                return Err(erreur("Impossible de scinder la pile"));
            }

            let nouveau_id: i64 = sqlx::query_scalar(
                r#"
                INSERT INTO stuff (
                    account_id, objet_id, stack_key,
                    quantity, rarete, rang, visible
                )
                VALUES (?, ?, ?, ?, ?, ?, 0)
                RETURNING stuff_id
                "#,
            )
            .bind(account_id)
            .bind(source.objet_id)
            .bind(format!("market-dep-{}", Uuid::new_v4()))
            .bind(quantite)
            .bind(source.rarete.as_deref())
            .bind(source.rang.as_deref())
            .fetch_one(&mut **tx)
            .await?;

            depots.push((nouveau_id, quantite));
        }

        let mut lignes_creees = Vec::with_capacity(depots.len());

        for (stuff_id, quantite_depot) in depots {
            // Variante normalement créée à l'obtention ; ceci ne fait que
            // couvrir les exemplaires obtenus avant l'existence des variantes.
            let variante_id =
                variantes::assurer_variante_pour_stuff_tx(tx, stuff_id).await?;

            let stock_id: i64 = sqlx::query_scalar(
                r#"
                INSERT INTO stock_marche (
                    stuff_id,
                    vendeur_id,
                    quantite_deposee,
                    quantite_restante
                )
                VALUES (?, ?, ?, ?)
                RETURNING stock_id
                "#,
            )
            .bind(stuff_id)
            .bind(account_id)
            .bind(quantite_depot)
            .bind(quantite_depot)
            .fetch_one(&mut **tx)
            .await?;

            let ligne_id: i64 = sqlx::query_scalar(
                r#"
                INSERT INTO lignes_vente (
                    ordre_vente_id,
                    stock_id,
                    objet_id,
                    variante_id,
                    quantite_initiale,
                    quantite_restante,
                    prix_unitaire
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING ligne_vente_id
                "#,
            )
            .bind(ordre_id)
            .bind(stock_id)
            .bind(source.objet_id)
            .bind(variante_id)
            .bind(quantite_depot)
            .bind(quantite_depot)
            .bind(ligne.prix_unitaire)
            .fetch_one(&mut **tx)
            .await?;

            lignes_creees.push(ligne_id);
        }

        Ok((lignes_creees, source.objet_id))
    }

    /// Masque la ligne d'inventaire et libère sa `stack_key`.
    ///
    /// La clé est remplacée par une clé unique : une nouvelle obtention du
    /// même objet recrée normalement sa pile, sans jamais toucher au séquestre.
    async fn mettre_en_sequestre(
        tx: &mut Tx<'_>,
        stuff_id: i64,
    ) -> Result<(), sqlx::Error> {
        let result = sqlx::query(
            r#"
            UPDATE stuff
            SET visible = 0,
                stack_key = ?
            WHERE stuff_id = ?
              AND visible = 1
            "#,
        )
        .bind(format!("market-dep-{}", Uuid::new_v4()))
        .bind(stuff_id)
        .execute(&mut **tx)
        .await?;

        if result.rows_affected() != 1 {
            return Err(erreur("Impossible de mettre l'objet en séquestre"));
        }

        Ok(())
    }

    /// Crée une unité masquée à partir d'une pile (livres compris : la fiche
    /// et les enchantements sont copiés, sinon l'acheteur recevrait un livre
    /// sans contenu).
    async fn cloner_unite(
        tx: &mut Tx<'_>,
        source_id: i64,
        type_objet: &str,
    ) -> Result<i64, sqlx::Error> {
        if matches!(type_objet, "equipment" | "armes" | "potion") {
            return Err(erreur(
                "Exemplaire unique attendu : quantité incohérente",
            ));
        }

        let clone_id: i64 = sqlx::query_scalar(SQL_CLONER_UNITE)
            .bind(format!("market-dep-{}", Uuid::new_v4()))
            .bind(source_id)
            .fetch_one(&mut **tx)
            .await?;

        if type_objet == "enchanted_book" {
            let book_id: i64 = sqlx::query_scalar(SQL_CLONER_LIVRE)
                .bind(clone_id)
                .bind(source_id)
                .fetch_one(&mut **tx)
                .await?;

            sqlx::query(SQL_CLONER_ENCHANTEMENTS_LIVRE)
                .bind(book_id)
                .bind(source_id)
                .execute(&mut **tx)
                .await?;
        }

        Ok(clone_id)
    }

    // ========================================================
    // ANNULATIONS
    // ========================================================

    /// Annule toutes les lignes encore actives d'un ordre d'achat et rend les
    /// fonds réservés restants.
    pub async fn annuler_ordre_achat(
        &self,
        account_id: i64,
        ordre_id: i64,
    ) -> Result<(), sqlx::Error> {
        self.annuler_lignes_achat(account_id, ordre_id, None).await
    }

    /// Annule une seule ligne d'un ordre d'achat.
    pub async fn annuler_ligne_achat(
        &self,
        account_id: i64,
        ordre_id: i64,
        ligne_achat_id: i64,
    ) -> Result<(), sqlx::Error> {
        self.annuler_lignes_achat(account_id, ordre_id, Some(ligne_achat_id))
            .await
    }

    async fn annuler_lignes_achat(
        &self,
        account_id: i64,
        ordre_id: i64,
        ligne_id: Option<i64>,
    ) -> Result<(), sqlx::Error> {
        let mut tx = self.pool.begin().await?;
        prendre_verrou_ecriture(&mut tx).await?;

        let lignes: Vec<(i64, i64)> = sqlx::query_as(
            r#"
            SELECT la.ligne_achat_id, la.montant_reserve_restant
            FROM lignes_achat la
            JOIN ordres_achat oa
                ON oa.ordre_achat_id = la.ordre_achat_id
            WHERE oa.ordre_achat_id = ?
              AND oa.account_id = ?
              AND la.statut IN ('actif', 'partiel')
              AND (? IS NULL OR la.ligne_achat_id = ?)
            "#,
        )
        .bind(ordre_id)
        .bind(account_id)
        .bind(ligne_id)
        .bind(ligne_id)
        .fetch_all(&mut *tx)
        .await?;

        if lignes.is_empty() {
            return Err(erreur(if ligne_id.is_some() {
                "Ligne d'achat inexistante ou plus active"
            } else {
                "Ordre d'achat inexistant ou plus actif"
            }));
        }

        let mut remboursement: i64 = 0;

        for (ligne_achat_id, montant) in &lignes {
            remboursement =
                remboursement.checked_add(*montant).ok_or_else(|| {
                    erreur("Le remboursement dépasse la capacité i64")
                })?;

            let result = sqlx::query(
                r#"
                UPDATE lignes_achat
                SET statut = 'annule',
                    montant_reserve_restant = 0
                WHERE ligne_achat_id = ?
                  AND statut IN ('actif', 'partiel')
                "#,
            )
            .bind(ligne_achat_id)
            .execute(&mut *tx)
            .await?;

            if result.rows_affected() != 1 {
                return Err(erreur("Impossible d'annuler la ligne d'achat"));
            }
        }

        if ligne_id.is_none() {
            // Annulation de l'ordre entier.
            sqlx::query(
                r#"
                UPDATE ordres_achat
                SET statut = 'annule',
                    modifie_le = CURRENT_TIMESTAMP
                WHERE ordre_achat_id = ?
                "#,
            )
            .bind(ordre_id)
            .execute(&mut *tx)
            .await?;
        } else {
            sqlx::query(SQL_STATUT_ORDRE_ACHAT)
                .bind(ordre_id)
                .execute(&mut *tx)
                .await?;
        }

        if remboursement > 0 {
            WalletManager::crediter_tx(&mut tx, account_id, remboursement)
                .await?;
        }

        tx.commit().await?;

        Ok(())
    }

    /// Annule toutes les lignes encore actives d'un ordre de vente et rend
    /// les objets restants (ils redeviennent visibles).
    pub async fn annuler_ordre_vente(
        &self,
        account_id: i64,
        ordre_id: i64,
    ) -> Result<(), sqlx::Error> {
        self.annuler_lignes_vente(account_id, ordre_id, None).await
    }

    /// Annule une seule ligne d'un ordre de vente.
    pub async fn annuler_ligne_vente(
        &self,
        account_id: i64,
        ordre_id: i64,
        ligne_vente_id: i64,
    ) -> Result<(), sqlx::Error> {
        self.annuler_lignes_vente(account_id, ordre_id, Some(ligne_vente_id))
            .await
    }

    async fn annuler_lignes_vente(
        &self,
        account_id: i64,
        ordre_id: i64,
        ligne_id: Option<i64>,
    ) -> Result<(), sqlx::Error> {
        let mut tx = self.pool.begin().await?;
        prendre_verrou_ecriture(&mut tx).await?;

        // (ligne_vente_id, stock_id, stuff_id du séquestre)
        let lignes: Vec<(i64, i64, i64)> = sqlx::query_as(
            r#"
            SELECT lv.ligne_vente_id, lv.stock_id, sm.stuff_id
            FROM lignes_vente lv
            JOIN stock_marche sm ON sm.stock_id = lv.stock_id
            JOIN ordres_vente ov ON ov.ordre_vente_id = lv.ordre_vente_id
            WHERE ov.ordre_vente_id = ?
              AND ov.account_id = ?
              AND lv.statut IN ('actif', 'partiel')
              AND sm.statut IN ('disponible', 'partiel')
              AND (? IS NULL OR lv.ligne_vente_id = ?)
            "#,
        )
        .bind(ordre_id)
        .bind(account_id)
        .bind(ligne_id)
        .bind(ligne_id)
        .fetch_all(&mut *tx)
        .await?;

        if lignes.is_empty() {
            return Err(erreur(if ligne_id.is_some() {
                "Ligne de vente inexistante ou plus active"
            } else {
                "Ordre de vente inexistant ou plus actif"
            }));
        }

        for (ligne_vente_id, stock_id, stuff_id) in &lignes {
            sqlx::query(
                r#"
                UPDATE lignes_vente
                SET statut = 'annule'
                WHERE ligne_vente_id = ?
                "#,
            )
            .bind(ligne_vente_id)
            .execute(&mut *tx)
            .await?;

            sqlx::query(
                r#"
                UPDATE stock_marche
                SET statut = 'annule',
                    modifie_le = CURRENT_TIMESTAMP
                WHERE stock_id = ?
                "#,
            )
            .bind(stock_id)
            .execute(&mut *tx)
            .await?;

            // La quantité du stuff a déjà été réduite par le trigger lors des
            // ventes partielles : il ne reste qu'à le rendre visible.
            let result = sqlx::query(
                r#"
                UPDATE stuff
                SET visible = 1
                WHERE stuff_id = ?
                  AND account_id = ?
                "#,
            )
            .bind(stuff_id)
            .bind(account_id)
            .execute(&mut *tx)
            .await?;

            if result.rows_affected() != 1 {
                return Err(erreur("Impossible de restituer l'objet"));
            }
        }

        if ligne_id.is_none() {
            sqlx::query(
                r#"
                UPDATE ordres_vente
                SET statut = 'annule',
                    modifie_le = CURRENT_TIMESTAMP
                WHERE ordre_vente_id = ?
                "#,
            )
            .bind(ordre_id)
            .execute(&mut *tx)
            .await?;
        } else {
            sqlx::query(SQL_STATUT_ORDRE_VENTE)
                .bind(ordre_id)
                .execute(&mut *tx)
                .await?;
        }

        tx.commit().await?;

        Ok(())
    }

    // ========================================================
    // APPARIEMENT
    // ========================================================

    /// Exécute au plus une transaction pour l'objet.
    /// Retourne l'id de la transaction, ou `None` s'il n'y a plus de paire.
    pub async fn matcher_ordre(
        &self,
        objet_id: i64,
    ) -> Result<Option<i64>, sqlx::Error> {
        let mut tx = self.pool.begin().await?;
        prendre_verrou_ecriture(&mut tx).await?;

        let paire: Option<PaireCompatible> =
            sqlx::query_as(SQL_MEILLEURE_PAIRE)
                .bind(objet_id)
                .fetch_optional(&mut *tx)
                .await?;

        let paire = match paire {
            Some(paire) => paire,
            None => {
                tx.rollback().await?;
                return Ok(None);
            }
        };

        let quantite = paire.achat_restante.min(paire.vente_restante);

        // Prix d'exécution : celui de la ligne de vente.
        let prix_execution = paire.prix_vente;

        let montant_total =
            prix_execution.checked_mul(quantite).ok_or_else(|| {
                erreur("Le montant de la transaction dépasse la capacité i64")
            })?;

        // L'acheteur avait réservé prix_max × quantité : la différence
        // avec le prix réellement payé lui revient tout de suite.
        let remboursement = (paire.prix_achat_max - prix_execution)
            .checked_mul(quantite)
            .ok_or_else(|| {
                erreur("Le remboursement dépasse la capacité i64")
            })?;

        // Les triggers valident la paire, mettent à jour lignes, stock et
        // en-têtes, et transfèrent le stuff à l'acheteur.
        let transaction_id: i64 = sqlx::query_scalar(
            r#"
            INSERT INTO transactions_marche (
                ligne_achat_id,
                ligne_vente_id,
                stuff_id,
                acheteur_id,
                vendeur_id,
                objet_id,
                variante_id,
                quantite,
                prix_unitaire,
                prix_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING transaction_id
            "#,
        )
        .bind(paire.ligne_achat_id)
        .bind(paire.ligne_vente_id)
        .bind(paire.stuff_id)
        .bind(paire.acheteur_id)
        .bind(paire.vendeur_id)
        .bind(objet_id)
        .bind(paire.variante_id)
        .bind(quantite)
        .bind(prix_execution)
        .bind(montant_total)
        .fetch_one(&mut *tx)
        .await?;

        WalletManager::crediter_tx(&mut tx, paire.vendeur_id, montant_total)
            .await?;

        if remboursement > 0 {
            WalletManager::crediter_tx(
                &mut tx,
                paire.acheteur_id,
                remboursement,
            )
            .await?;
        }

        // Le trigger range le stuff de l'acheteur sous la clé
        // 'market-tx-<id>'. Un exemplaire transféré en entier garde son
        // `visible = 0` de séquestre : on le rend visible à l'acheteur.
        sqlx::query(
            r#"
            UPDATE stuff
            SET visible = 1
            WHERE account_id = ?
              AND stack_key = ?
            "#,
        )
        .bind(paire.acheteur_id)
        .bind(format!("market-tx-{transaction_id}"))
        .execute(&mut *tx)
        .await?;

        tx.commit().await?;

        Ok(Some(transaction_id))
    }

    /// Exécute toutes les transactions possibles pour un objet.
    pub async fn matcher_tous(
        &self,
        objet_id: i64,
    ) -> Result<u64, sqlx::Error> {
        let mut nombre_transactions = 0u64;

        while self.matcher_ordre(objet_id).await?.is_some() {
            nombre_transactions += 1;
        }

        Ok(nombre_transactions)
    }

    /// Apparie plusieurs objets après la création d'un ordre.
    ///
    /// L'ordre est déjà validé : une erreur d'appariement n'annule donc pas
    /// sa création, elle est simplement journalisée.
    async fn matcher_objets(
        &self,
        objets: impl IntoIterator<Item = i64>,
    ) -> u64 {
        let objets: BTreeSet<i64> = objets.into_iter().collect();
        let mut total = 0u64;

        for objet_id in objets {
            match self.matcher_tous(objet_id).await {
                Ok(nombre) => total += nombre,
                Err(e) => log::warn!(
                    "Appariement du marché interrompu pour objet_id={} : {}",
                    objet_id,
                    e
                ),
            }
        }

        total
    }

    // ========================================================
    // CONSULTATION
    // ========================================================

    /// Variantes existantes d'un objet, avec leurs enchantements.
    pub async fn variantes_objet(
        &self,
        objet_id: i64,
    ) -> Result<Vec<VarianteDetail>, sqlx::Error> {
        let variantes: Vec<VarianteMarche> = sqlx::query_as(
            r#"
            SELECT variante_id, objet_id, rarete, rang, book_level, signature
            FROM variantes_marche
            WHERE objet_id = ?
            ORDER BY variante_id
            "#,
        )
        .bind(objet_id)
        .fetch_all(&self.pool)
        .await?;

        let enchantements: Vec<(i64, String, i64)> = sqlx::query_as(
            r#"
            SELECT ve.variante_id, e.enchantment_name, ve.enchantment_level
            FROM variante_enchantements ve
            JOIN variantes_marche vm ON vm.variante_id = ve.variante_id
            JOIN enchantments e ON e.enchantment_id = ve.enchantment_id
            WHERE vm.objet_id = ?
            ORDER BY ve.variante_id, e.enchantment_name
            "#,
        )
        .bind(objet_id)
        .fetch_all(&self.pool)
        .await?;

        let mut par_variante: HashMap<i64, Vec<(String, i64)>> = HashMap::new();

        for (variante_id, nom, niveau) in enchantements {
            par_variante
                .entry(variante_id)
                .or_default()
                .push((nom, niveau));
        }

        Ok(variantes
            .into_iter()
            .map(|variante| {
                let enchantements = par_variante
                    .remove(&variante.variante_id)
                    .unwrap_or_default();

                VarianteDetail {
                    variante,
                    enchantements,
                }
            })
            .collect())
    }

    /// Prix indicatif : moyenne pondérée par la quantité des dernières
    /// transactions (arrondie à l'entier le plus proche). Sans vente, valeur
    /// de base du catalogue.
    pub async fn prix_indicatif(
        &self,
        objet_id: i64,
        variante_id: Option<i64>,
    ) -> Result<i64, sqlx::Error> {
        let recentes: Vec<(i64, i64)> = sqlx::query_as(
            r#"
            SELECT prix_total, quantite
            FROM transactions_marche
            WHERE objet_id = ?
              AND (? IS NULL OR variante_id = ?)
            ORDER BY transaction_id DESC
            LIMIT ?
            "#,
        )
        .bind(objet_id)
        .bind(variante_id)
        .bind(variante_id)
        .bind(FENETRE_PRIX_INDICATIF)
        .fetch_all(&self.pool)
        .await?;

        if !recentes.is_empty() {
            let total: i128 = recentes.iter().map(|(p, _)| i128::from(*p)).sum();
            let quantite: i128 =
                recentes.iter().map(|(_, q)| i128::from(*q)).sum();

            return i64::try_from(moyenne_arrondie(total, quantite))
                .map_err(|_| erreur("Le prix indicatif dépasse la capacité i64"));
        }

        let prix_base: Option<i64> = sqlx::query_scalar(
            "SELECT prix_base FROM objets_dispo WHERE objet_id = ?",
        )
        .bind(objet_id)
        .fetch_optional(&self.pool)
        .await?;

        prix_base.ok_or_else(|| erreur("Objet inexistant"))
    }

    // ========================================================
    // COMPATIBILITÉ AVEC LE PROTOCOLE ACTUEL (objet, quantité, prix)
    // ========================================================
    //
    // Les paquets MARKET_BUY / MARKET_SELL de `handler.rs` ne transportent ni
    // variante ni stuff_id. Ces méthodes les couvrent pour les objets
    // « standard » (sans rareté, rang ni enchantement) :
    //
    // - achat : objet de base, ou variante standard (potions, armes,
    //   équipements) ;
    // - vente : pile 'base' visible, ou premières potions visibles.
    //
    // Pour le reste (livres, équipements, rareté, rang…), utiliser
    // `creer_ordre_achat_lignes` / `creer_ordre_vente_lignes`.

    pub async fn creer_ordre_achat(
        &self,
        account_id: i64,
        objet_id: i64,
        quantity: u64,
        prix_unitaire_max: i64,
    ) -> Result<i64, sqlx::Error> {
        let type_objet = self.type_objet(objet_id).await?;

        let ligne = if variantes::type_a_variante(&type_objet) {
            let spec = VarianteSpec::simple(objet_id, None, None);

            let variante_id = variantes::variante_id(&self.pool, &spec)
                .await?
                .ok_or_else(|| {
                    erreur(
                        "Aucune variante standard pour cet objet : \
                         précisez une variante",
                    )
                })?;

            if type_objet == "potion" {
                LigneAchatDemande::potion(
                    objet_id,
                    variante_id,
                    quantity,
                    prix_unitaire_max,
                    CriterePotion::default(),
                )
            } else {
                LigneAchatDemande::variante(
                    objet_id,
                    variante_id,
                    quantity,
                    prix_unitaire_max,
                )
            }
        } else {
            LigneAchatDemande::base(objet_id, quantity, prix_unitaire_max)
        };

        Ok(self
            .creer_ordre_achat_lignes(account_id, vec![ligne])
            .await?
            .ordre_id)
    }

    pub async fn creer_ordre_vente(
        &self,
        account_id: i64,
        objet_id: i64,
        quantity: u64,
        prix_unitaire: i64,
    ) -> Result<i64, sqlx::Error> {
        if quantity == 0 {
            return Err(erreur("La quantité doit être supérieure à 0"));
        }

        let type_objet = self.type_objet(objet_id).await?;

        let lignes = if type_objet == "potion" {
            let limite = quantite_i64(quantity)?;

            let ids: Vec<i64> = sqlx::query_scalar(
                r#"
                SELECT stuff_id
                FROM stuff
                WHERE account_id = ?
                  AND objet_id = ?
                  AND visible = 1
                ORDER BY stuff_id
                LIMIT ?
                "#,
            )
            .bind(account_id)
            .bind(objet_id)
            .bind(limite)
            .fetch_all(&self.pool)
            .await?;

            if (ids.len() as u64) < quantity {
                return Err(erreur("Quantité insuffisante"));
            }

            ids.into_iter()
                .map(|stuff_id| LigneVenteDemande {
                    stuff_id,
                    quantite: 1,
                    prix_unitaire,
                })
                .collect()
        } else {
            let stuff_id: Option<i64> = sqlx::query_scalar(
                r#"
                SELECT stuff_id
                FROM stuff
                WHERE account_id = ?
                  AND objet_id = ?
                  AND stack_key = 'base'
                  AND visible = 1
                "#,
            )
            .bind(account_id)
            .bind(objet_id)
            .fetch_optional(&self.pool)
            .await?;

            let stuff_id = stuff_id.ok_or_else(|| {
                erreur(
                    "Aucun exemplaire standard disponible : \
                     indiquez le stuff_id à vendre",
                )
            })?;

            vec![LigneVenteDemande {
                stuff_id,
                quantite: quantity,
                prix_unitaire,
            }]
        };

        Ok(self
            .creer_ordre_vente_lignes(account_id, lignes)
            .await?
            .ordre_id)
    }

    async fn type_objet(&self, objet_id: i64) -> Result<String, sqlx::Error> {
        let type_objet: Option<String> = sqlx::query_scalar(
            "SELECT type FROM objets_dispo WHERE objet_id = ?",
        )
        .bind(objet_id)
        .fetch_optional(&self.pool)
        .await?;

        type_objet.ok_or_else(|| erreur("Objet inexistant"))
    }
}

// ============================================================
// RECHERCHE, INVENTAIRE VENDABLE ET ACHAT IMMÉDIAT
// (interface client : voir `network/market_api.rs`)
// ============================================================

const LIMITE_RECHERCHE_DEFAUT: i64 = 200;
const LIMITE_RECHERCHE_MAX: i64 = 500;

/// Lignes de vente actives, avec tout ce qu'il faut pour les afficher.
///
/// ?1 compte demandeur, ?2 mode (0 = marché : on exclut ses propres
/// ventes ; 1 = « mes ventes »), ?3.. filtres (NULL = pas de filtre).
/// L'ORDER BY et la LIMIT (?15) sont ajoutés par `lister_ventes`.
const SQL_VENTES: &str = r#"
SELECT
    lv.ligne_vente_id    AS ligne_vente_id,
    lv.ordre_vente_id    AS ordre_vente_id,
    lv.objet_id          AS objet_id,
    o.nom                AS nom,
    o.type               AS type_objet,
    lv.variante_id       AS variante_id,
    lv.quantite_restante AS quantite,
    lv.prix_unitaire     AS prix_unitaire,
    vm.rarete            AS rarete,
    vm.rang              AS rang,
    vm.book_level        AS niveau_livre,
    e.durability         AS durabilite,
    e.durability_max     AS durabilite_max,
    p.effect             AS effet,
    p.potency            AS puissance,
    p.duration           AS duree,
    a.account_name       AS vendeur
FROM lignes_vente lv
JOIN ordres_vente ov ON ov.ordre_vente_id = lv.ordre_vente_id
JOIN stock_marche sm ON sm.stock_id = lv.stock_id
JOIN stuff s         ON s.stuff_id = sm.stuff_id
JOIN objets_dispo o  ON o.objet_id = lv.objet_id
JOIN accounts a      ON a.account_id = ov.account_id
LEFT JOIN variantes_marche vm ON vm.variante_id = lv.variante_id
LEFT JOIN equipment e ON e.stuff_id = s.stuff_id
LEFT JOIN potions p   ON p.stuff_id = s.stuff_id
WHERE lv.statut IN ('actif', 'partiel')
  AND ov.statut IN ('actif', 'partiel')
  AND sm.statut IN ('disponible', 'partiel')
  AND lv.quantite_restante > 0
  AND ((?2 = 0 AND ov.account_id <> ?1) OR (?2 = 1 AND ov.account_id = ?1))
  AND (?3  IS NULL OR instr(lower(o.nom), lower(?3)) > 0)
  AND (?4  IS NULL OR o.type = ?4)
  AND (?5  IS NULL OR vm.rarete = ?5)
  AND (?6  IS NULL OR vm.rang = ?6)
  AND (?7  IS NULL OR lv.prix_unitaire >= ?7)
  AND (?8  IS NULL OR lv.prix_unitaire <= ?8)
  AND (?9  IS NULL OR e.durability >= ?9)
  AND (?10 IS NULL OR e.durability <= ?10)
  AND (?11 IS NULL OR EXISTS (
        SELECT 1
        FROM variante_enchantements ve
        JOIN enchantments en ON en.enchantment_id = ve.enchantment_id
        WHERE ve.variante_id = lv.variante_id
          AND instr(lower(en.enchantment_name), lower(?11)) > 0))
  AND (?12 IS NULL OR instr(lower(p.effect), lower(?12)) > 0)
  AND (?13 IS NULL OR p.potency >= ?13)
  AND (?14 IS NULL OR p.duration >= ?14)
"#;

/// Enchantements des variantes listées (?1 = tableau JSON d'ids).
const SQL_ENCHANTEMENTS_VARIANTES: &str = r#"
SELECT ve.variante_id, en.enchantment_name, ve.enchantment_level
FROM variante_enchantements ve
JOIN enchantments en ON en.enchantment_id = ve.enchantment_id
WHERE ve.variante_id IN (SELECT value FROM json_each(?1))
ORDER BY ve.variante_id, en.enchantment_name
"#;

/// Inventaire vendable : uniquement les objets VISIBLES du compte (?1).
const SQL_INVENTAIRE_VENDABLE: &str = r#"
SELECT
    s.stuff_id       AS stuff_id,
    s.objet_id       AS objet_id,
    o.nom            AS nom,
    o.type           AS type_objet,
    s.quantity       AS quantite,
    s.rarete         AS rarete,
    s.rang           AS rang,
    eb.book_level    AS niveau_livre,
    eq.durability    AS durabilite,
    eq.durability_max AS durabilite_max,
    p.effect         AS effet,
    p.potency        AS puissance,
    p.duration       AS duree,
    o.prix_base      AS prix_base
FROM stuff s
JOIN objets_dispo o ON o.objet_id = s.objet_id
LEFT JOIN equipment eq       ON eq.stuff_id = s.stuff_id
LEFT JOIN potions p          ON p.stuff_id = s.stuff_id
LEFT JOIN enchanted_books eb ON eb.stuff_id = s.stuff_id
WHERE s.account_id = ?1
  AND s.visible = 1
ORDER BY o.nom, s.stuff_id
"#;

/// Enchantements des livres et équipements visibles du compte (?1).
const SQL_ENCHANTEMENTS_INVENTAIRE: &str = r#"
SELECT s.stuff_id, en.enchantment_name, be.enchantment_level
FROM stuff s
JOIN enchanted_books eb      ON eb.stuff_id = s.stuff_id
JOIN book_enchantments be    ON be.book_id = eb.book_id
JOIN enchantments en         ON en.enchantment_id = be.enchantment_id
WHERE s.account_id = ?1 AND s.visible = 1
UNION ALL
SELECT s.stuff_id, en.enchantment_name, ee.enchantment_level
FROM stuff s
JOIN equipment eq            ON eq.stuff_id = s.stuff_id
JOIN equipment_enchantments ee ON ee.equipment_id = eq.equipment_id
JOIN enchantments en         ON en.enchantment_id = ee.enchantment_id
WHERE s.account_id = ?1 AND s.visible = 1
ORDER BY 1, 2
"#;

/// Une vente encore active, avec ses caractéristiques (?1 = ligne_vente_id).
const SQL_LIGNE_A_ACHETER: &str = r#"
SELECT
    lv.objet_id          AS objet_id,
    lv.variante_id       AS variante_id,
    lv.prix_unitaire     AS prix_unitaire,
    lv.quantite_restante AS quantite_restante,
    ov.account_id        AS vendeur_id,
    o.type               AS type_objet,
    e.durability         AS durabilite,
    p.effect             AS effet,
    p.potency            AS puissance,
    p.duration           AS duree
FROM lignes_vente lv
JOIN ordres_vente ov ON ov.ordre_vente_id = lv.ordre_vente_id
JOIN stock_marche sm ON sm.stock_id = lv.stock_id
JOIN stuff s         ON s.stuff_id = sm.stuff_id
JOIN objets_dispo o  ON o.objet_id = lv.objet_id
LEFT JOIN equipment e ON e.stuff_id = s.stuff_id
LEFT JOIN potions p   ON p.stuff_id = s.stuff_id
WHERE lv.ligne_vente_id = ?1
  AND lv.statut IN ('actif', 'partiel')
  AND ov.statut IN ('actif', 'partiel')
  AND sm.statut IN ('disponible', 'partiel')
  AND lv.quantite_restante > 0
"#;

/// Critères de recherche du marché (tous facultatifs).
#[derive(Debug, Clone, Default, Deserialize)]
#[serde(default)]
pub struct FiltreRecherche {
    /// Morceau du nom, sans tenir compte de la casse.
    pub nom: Option<String>,
    #[serde(rename = "type")]
    pub type_objet: Option<String>,
    pub rarete: Option<String>,
    pub rang: Option<String>,
    pub prix_min: Option<i64>,
    pub prix_max: Option<i64>,
    /// Armes et équipements uniquement.
    pub durabilite_min: Option<i64>,
    pub durabilite_max: Option<i64>,
    /// Morceau du nom d'un enchantement.
    pub enchantement: Option<String>,
    pub effet: Option<String>,
    pub puissance_min: Option<i64>,
    pub duree_min: Option<i64>,
    /// "prix_asc" (défaut), "prix_desc", "nom", "durabilite_desc".
    pub tri: Option<String>,
    pub limite: Option<i64>,
}

fn vide_en_none(texte: Option<String>) -> Option<String> {
    texte
        .map(|t| t.trim().to_string())
        .filter(|t| !t.is_empty())
}

impl FiltreRecherche {
    /// Les champs texte vides (formulaire non rempli) valent « pas de filtre ».
    fn normaliser(mut self) -> Self {
        self.nom = vide_en_none(self.nom);
        self.type_objet = vide_en_none(self.type_objet);
        self.rarete = vide_en_none(self.rarete);
        self.rang = vide_en_none(self.rang);
        self.enchantement = vide_en_none(self.enchantement);
        self.effet = vide_en_none(self.effet);
        self
    }

    /// Clause ORDER BY choisie dans une liste fermée (jamais du texte client).
    fn ordre_sql(&self) -> &'static str {
        match self.tri.as_deref() {
            Some("prix_desc") => "lv.prix_unitaire DESC, lv.ligne_vente_id ASC",
            Some("nom") => {
                "o.nom ASC, lv.prix_unitaire ASC, lv.ligne_vente_id ASC"
            }
            Some("durabilite_desc") => {
                "e.durability DESC, lv.prix_unitaire ASC, lv.ligne_vente_id ASC"
            }
            _ => "lv.prix_unitaire ASC, lv.ligne_vente_id ASC",
        }
    }
}

/// Une vente affichée dans l'onglet « Acheter » (ou « Mes ventes »).
#[derive(Debug, Clone, Serialize, sqlx::FromRow)]
pub struct VenteListee {
    pub ligne_vente_id: i64,
    pub ordre_vente_id: i64,
    pub objet_id: i64,
    pub nom: String,
    #[serde(rename = "type")]
    pub type_objet: String,
    pub variante_id: Option<i64>,
    pub quantite: i64,
    pub prix_unitaire: i64,
    pub rarete: Option<String>,
    pub rang: Option<String>,
    pub niveau_livre: Option<i64>,
    pub durabilite: Option<i64>,
    pub durabilite_max: Option<i64>,
    pub effet: Option<String>,
    pub puissance: Option<i64>,
    pub duree: Option<i64>,
    pub vendeur: String,
    /// Ex. « Tranchant 3 ».
    #[sqlx(skip)]
    pub enchantements: Vec<String>,
}

/// Un exemplaire de l'inventaire proposé dans l'onglet « Vendre ».
#[derive(Debug, Clone, Serialize, sqlx::FromRow)]
pub struct ObjetVendable {
    pub stuff_id: i64,
    pub objet_id: i64,
    pub nom: String,
    #[serde(rename = "type")]
    pub type_objet: String,
    pub quantite: i64,
    pub rarete: Option<String>,
    pub rang: Option<String>,
    pub niveau_livre: Option<i64>,
    pub durabilite: Option<i64>,
    pub durabilite_max: Option<i64>,
    pub effet: Option<String>,
    pub puissance: Option<i64>,
    pub duree: Option<i64>,
    /// Prix du catalogue, proposé comme prix de départ.
    pub prix_base: i64,
    #[sqlx(skip)]
    pub enchantements: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct ResultatAchat {
    pub ordre_id: i64,
    pub quantite_demandee: i64,
    pub quantite_achetee: i64,
    pub depense_totale: i64,
}

#[derive(sqlx::FromRow)]
struct LigneAAcheter {
    objet_id: i64,
    variante_id: Option<i64>,
    prix_unitaire: i64,
    quantite_restante: i64,
    vendeur_id: i64,
    type_objet: String,
    durabilite: Option<i64>,
    effet: Option<String>,
    puissance: Option<i64>,
    duree: Option<i64>,
}

fn grouper_enchantements(
    lignes: Vec<(i64, String, i64)>,
) -> HashMap<i64, Vec<String>> {
    let mut par_cle: HashMap<i64, Vec<String>> = HashMap::new();

    for (cle, nom, niveau) in lignes {
        par_cle
            .entry(cle)
            .or_default()
            .push(format!("{nom} {niveau}"));
    }

    par_cle
}

impl MarketManager {
    /// Ventes des autres joueurs correspondant aux critères.
    pub async fn rechercher_ventes(
        &self,
        account_id: i64,
        filtre: FiltreRecherche,
    ) -> Result<Vec<VenteListee>, sqlx::Error> {
        self.lister_ventes(account_id, 0, filtre).await
    }

    /// Ventes en cours du joueur (annulables).
    pub async fn mes_ventes(
        &self,
        account_id: i64,
    ) -> Result<Vec<VenteListee>, sqlx::Error> {
        self.lister_ventes(account_id, 1, FiltreRecherche::default())
            .await
    }

    async fn lister_ventes(
        &self,
        account_id: i64,
        mode: i64,
        filtre: FiltreRecherche,
    ) -> Result<Vec<VenteListee>, sqlx::Error> {
        let filtre = filtre.normaliser();

        let limite = filtre
            .limite
            .unwrap_or(LIMITE_RECHERCHE_DEFAUT)
            .clamp(1, LIMITE_RECHERCHE_MAX);

        let sql = format!(
            "{SQL_VENTES}\nORDER BY {}\nLIMIT ?15",
            filtre.ordre_sql()
        );

        let mut ventes: Vec<VenteListee> = sqlx::query_as::<_, VenteListee>(sqlx::AssertSqlSafe(sql))
            .bind(account_id)
            .bind(mode)
            .bind(filtre.nom.as_deref())
            .bind(filtre.type_objet.as_deref())
            .bind(filtre.rarete.as_deref())
            .bind(filtre.rang.as_deref())
            .bind(filtre.prix_min)
            .bind(filtre.prix_max)
            .bind(filtre.durabilite_min)
            .bind(filtre.durabilite_max)
            .bind(filtre.enchantement.as_deref())
            .bind(filtre.effet.as_deref())
            .bind(filtre.puissance_min)
            .bind(filtre.duree_min)
            .bind(limite)
            .fetch_all(&self.pool)
            .await?;

        let variantes: BTreeSet<i64> =
            ventes.iter().filter_map(|v| v.variante_id).collect();

        if !variantes.is_empty() {
            let ids = serde_json::to_string(
                &variantes.into_iter().collect::<Vec<_>>(),
            )
            .map_err(|e| erreur(e.to_string()))?;

            let lignes: Vec<(i64, String, i64)> =
                sqlx::query_as(SQL_ENCHANTEMENTS_VARIANTES)
                    .bind(ids)
                    .fetch_all(&self.pool)
                    .await?;

            let par_variante = grouper_enchantements(lignes);

            for vente in &mut ventes {
                if let Some(liste) = vente
                    .variante_id
                    .and_then(|id| par_variante.get(&id))
                {
                    vente.enchantements = liste.clone();
                }
            }
        }

        Ok(ventes)
    }

    /// Objets du joueur que l'on peut mettre en vente : seulement les
    /// objets visibles (un objet masqué est inutilisable, donc invendable).
    pub async fn inventaire_vendable(
        &self,
        account_id: i64,
    ) -> Result<Vec<ObjetVendable>, sqlx::Error> {
        let mut objets: Vec<ObjetVendable> =
            sqlx::query_as(SQL_INVENTAIRE_VENDABLE)
                .bind(account_id)
                .fetch_all(&self.pool)
                .await?;

        let lignes: Vec<(i64, String, i64)> =
            sqlx::query_as(SQL_ENCHANTEMENTS_INVENTAIRE)
                .bind(account_id)
                .fetch_all(&self.pool)
                .await?;

        let par_stuff = grouper_enchantements(lignes);

        for objet in &mut objets {
            if let Some(liste) = par_stuff.get(&objet.stuff_id) {
                objet.enchantements = liste.clone();
            }
        }

        Ok(objets)
    }

    /// Achète tout de suite `quantite` unités d'une vente affichée.
    ///
    /// Crée un ordre d'achat dont le prix plafond est le prix affiché et
    /// dont les critères reprennent ceux de la vente (variante, durabilité
    /// exacte, caractéristiques exactes de la potion). Ce qui n'a pas pu être
    /// acheté est annulé et remboursé : aucun ordre ne reste ouvert.
    pub async fn acheter_ligne(
        &self,
        account_id: i64,
        ligne_vente_id: i64,
        quantite: u64,
    ) -> Result<ResultatAchat, sqlx::Error> {
        if quantite == 0 {
            return Err(erreur("La quantité doit être supérieure à 0"));
        }

        let demandee = quantite_i64(quantite)?;

        let vente: LigneAAcheter = sqlx::query_as(SQL_LIGNE_A_ACHETER)
            .bind(ligne_vente_id)
            .fetch_optional(&self.pool)
            .await?
            .ok_or_else(|| erreur("Cette vente n'est plus disponible"))?;

        if vente.vendeur_id == account_id {
            return Err(erreur(
                "Vous ne pouvez pas acheter vos propres objets",
            ));
        }

        if demandee > vente.quantite_restante {
            return Err(erreur(format!(
                "Quantité disponible : {}",
                vente.quantite_restante
            )));
        }

        let mut ligne = if variantes::type_a_variante(&vente.type_objet) {
            let variante_id = vente.variante_id.ok_or_else(|| {
                erreur("Vente sans variante : impossible d'acheter")
            })?;

            LigneAchatDemande::variante(
                vente.objet_id,
                variante_id,
                quantite,
                vente.prix_unitaire,
            )
        } else {
            LigneAchatDemande::base(
                vente.objet_id,
                quantite,
                vente.prix_unitaire,
            )
        };

        if variantes::type_a_fiche_equipement(&vente.type_objet) {
            ligne.durabilite_min = vente.durabilite;
            ligne.durabilite_max = vente.durabilite;
        }

        if vente.type_objet == "potion" {
            ligne.potion = CriterePotion {
                effet: vente.effet.clone(),
                puissance_exacte: vente.puissance,
                puissance_min: None,
                duree_exacte: vente.duree,
                duree_min: None,
            };
        }

        let ordre = self
            .creer_ordre_achat_lignes(account_id, vec![ligne])
            .await?;

        let ligne_achat_id = ordre.lignes[0];

        let (initiale, restante): (i64, i64) = sqlx::query_as(
            r#"
            SELECT quantite_initiale, quantite_restante
            FROM lignes_achat
            WHERE ligne_achat_id = ?
            "#,
        )
        .bind(ligne_achat_id)
        .fetch_one(&self.pool)
        .await?;

        let depense_totale: i64 = sqlx::query_scalar(
            r#"
            SELECT COALESCE(SUM(prix_total), 0)
            FROM transactions_marche
            WHERE ligne_achat_id = ?
            "#,
        )
        .bind(ligne_achat_id)
        .fetch_one(&self.pool)
        .await?;

        // Achat immédiat : le reste (vente prise entre-temps) est annulé
        // et les fonds réservés sont rendus.
        if restante > 0 {
            self.annuler_ordre_achat(account_id, ordre.ordre_id).await?;
        }

        Ok(ResultatAchat {
            ordre_id: ordre.ordre_id,
            quantite_demandee: demandee,
            quantite_achetee: initiale - restante,
            depense_totale,
        })
    }

    /// Annule une vente à partir de sa ligne (l'ordre est retrouvé ici).
    pub async fn annuler_vente_par_ligne(
        &self,
        account_id: i64,
        ligne_vente_id: i64,
    ) -> Result<(), sqlx::Error> {
        let ordre_id: Option<i64> = sqlx::query_scalar(
            "SELECT ordre_vente_id FROM lignes_vente WHERE ligne_vente_id = ?",
        )
        .bind(ligne_vente_id)
        .fetch_optional(&self.pool)
        .await?;

        let ordre_id =
            ordre_id.ok_or_else(|| erreur("Vente inexistante"))?;

        self.annuler_ligne_vente(account_id, ordre_id, ligne_vente_id)
            .await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn la_moyenne_est_arrondie_a_l_entier_le_plus_proche() {
        assert_eq!(moyenne_arrondie(10, 4), 3); // 2,5 -> 3
        assert_eq!(moyenne_arrondie(9, 4), 2); // 2,25 -> 2
        assert_eq!(moyenne_arrondie(11, 4), 3); // 2,75 -> 3
        assert_eq!(moyenne_arrondie(100, 1), 100);
    }

    #[test]
    fn une_ligne_d_achat_invalide_est_refusee() {
        let ligne = LigneAchatDemande::variante(1, 1, 0, 10);
        assert!(ligne.verifier().is_err());

        let ligne = LigneAchatDemande::base(1, 2, 10);
        assert_eq!(ligne.verifier().unwrap(), 20);

        let ligne = LigneAchatDemande::variante(1, 1, 1, 0);
        assert!(ligne.verifier().is_err());

        let ligne = LigneAchatDemande::variante(1, 1, u64::MAX, 10);
        assert!(ligne.verifier().is_err());

        let mut ligne = LigneAchatDemande::variante(1, 1, 2, 10);
        ligne.durabilite_min = Some(50);
        ligne.durabilite_max = Some(10);
        assert!(ligne.verifier().is_err());

        let mut ligne = LigneAchatDemande::variante(1, 1, 2, 10);
        ligne.potion.puissance_exacte = Some(3);
        ligne.potion.puissance_min = Some(2);
        assert!(ligne.verifier().is_err());
    }

    #[test]
    fn le_montant_reserve_est_prix_fois_quantite() {
        let ligne = LigneAchatDemande::variante(1, 1, 3, 25);
        assert_eq!(ligne.verifier().unwrap(), 75);
    }
}
