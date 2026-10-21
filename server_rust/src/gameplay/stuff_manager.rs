use sqlx::SqlitePool;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

use crate::gameplay::objets::{
    AjouterRetirer,
    Arme,
    Equipement,
    Livre,
    NomAffiche,
    Objet,
    Potion,
    TypeObjet,
};

// ============================================================
// ENUM UNIFIÉ POUR LE HASHMAP D'INVENTAIRE
// ============================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum ObjetInventaire {
    Base(Objet),
    Equipement(Equipement),
    Arme(Arme),
    Potion(Potion),
    Livre(Livre),
}

impl NomAffiche for ObjetInventaire {
    fn nom_affiche(&self) -> String {
        match self {
            ObjetInventaire::Base(o) => o.nom_affiche(),
            ObjetInventaire::Equipement(e) => e.objet.nom_affiche(),
            ObjetInventaire::Arme(a) => a.equipement.objet.nom_affiche(),
            ObjetInventaire::Potion(p) => p.objet.nom_affiche(),
            ObjetInventaire::Livre(l) => l.objet.nom_affiche(),
        }
    }
}

impl AjouterRetirer for ObjetInventaire {
    fn ajouter(&mut self, qte: u64) {
        match self {
            ObjetInventaire::Base(o) => o.ajouter(qte),
            ObjetInventaire::Equipement(e) => e.objet.ajouter(qte),
            ObjetInventaire::Arme(a) => a.equipement.objet.ajouter(qte),
            ObjetInventaire::Potion(p) => p.objet.ajouter(qte),
            ObjetInventaire::Livre(l) => l.objet.ajouter(qte),
        }
    }

    fn retirer(&mut self, qte: u64) {
        match self {
            ObjetInventaire::Base(o) => o.retirer(qte),
            ObjetInventaire::Equipement(e) => e.objet.retirer(qte),
            ObjetInventaire::Arme(a) => a.equipement.objet.retirer(qte),
            ObjetInventaire::Potion(p) => p.objet.retirer(qte),
            ObjetInventaire::Livre(l) => l.objet.retirer(qte),
        }
    }
}

// ============================================================
// STRUCT INVENTAIRE
// ============================================================

pub struct Inventaire {
    pool: SqlitePool,
    account_id: i64,
    objets: HashMap<i64, ObjetInventaire>,
}

// ============================================================
// STRUCTURES SQL
// ============================================================

#[derive(sqlx::FromRow)]
struct StuffRow {
    stuff_id: i64,
    quantity: i64,
    nom: String,
    type_objet: String,
    image_path: Option<String>,
}

#[derive(sqlx::FromRow)]
struct EquipmentRow {
    equipment_type: String,
    attack: i64,
    defense: i64,
    durability: i64,
}

#[derive(sqlx::FromRow)]
struct PotionRow {
    effect: String,
}

#[derive(sqlx::FromRow)]
struct BookRow {
    book_id: i64,
    book_level: i64,
}

#[derive(sqlx::FromRow)]
struct EnchantRow {
    enchantment_name: String,
    enchantment_level: i64,
}

#[derive(sqlx::FromRow)]
struct GeneratedEnchant {
    enchantment_id: i64,
    max_level: i64,
}

// ============================================================
// INVENTAIRE
// ============================================================

impl Inventaire {
    // ========================================================
    // CONSTRUCTEUR
    // ========================================================

    pub async fn new(
        pool: SqlitePool,
        account_id: i64,
    ) -> Result<Self, sqlx::Error> {
        let objets = Self::charger_objets(&pool, account_id).await?;

        Ok(Self {
            pool,
            account_id,
            objets,
        })
    }

    // ========================================================
    // CHARGEMENT DE L'INVENTAIRE
    // ========================================================

    async fn charger_objets(
        pool: &SqlitePool,
        account_id: i64,
    ) -> Result<HashMap<i64, ObjetInventaire>, sqlx::Error> {
        let rows = sqlx::query_as::<_, StuffRow>(
            r#"
            SELECT
                s.stuff_id,
                s.quantity,
                o.nom,
                o.type AS type_objet,
                o.image_path
            FROM stuff s
            JOIN objets_dispo o
                ON s.objet_id = o.objet_id
            WHERE s.account_id = ?
            ORDER BY s.stuff_id
            "#,
        )
        .bind(account_id)
        .fetch_all(pool)
        .await?;

        let mut inventaire = HashMap::with_capacity(rows.len());

        for row in rows {
            let stuff_id = row.stuff_id;

            let objet = Self::construire_objet(pool, &row).await?;

            inventaire.insert(stuff_id, objet);
        }

        Ok(inventaire)
    }

    // ========================================================
    // CONSTRUCTION D'UN OBJET DEPUIS SQLITE
    // ========================================================

    async fn construire_objet(
        pool: &SqlitePool,
        row: &StuffRow,
    ) -> Result<ObjetInventaire, sqlx::Error> {
        let quantite = u64::try_from(row.quantity).map_err(|_| {
            sqlx::Error::Protocol(
                format!(
                    "Quantité invalide pour {} : {}",
                    row.nom,
                    row.quantity
                )
                .into(),
            )
        })?;

        let image = row.image_path.as_deref();

        let result = match row.type_objet.as_str() {
            // ------------------------------------------------
            // ÉQUIPEMENT / ARME
            // ------------------------------------------------

            "equipment" | "armes" => {
                let eq: EquipmentRow = sqlx::query_as(
                    r#"
                    SELECT
                        equipment_type,
                        attack,
                        defense,
                        durability
                    FROM equipment
                    WHERE stuff_id = ?
                    "#,
                )
                .bind(row.stuff_id)
                .fetch_optional(pool)
                .await?
                .ok_or_else(|| {
                    sqlx::Error::Protocol(
                        format!(
                            "Équipement manquant pour stuff_id={}",
                            row.stuff_id
                        )
                        .into(),
                    )
                })?;

                if eq.equipment_type == "weapon" {
                    ObjetInventaire::Arme(
                        Arme::new(
                            &row.nom,
                            image,
                            quantite,
                            1,
                            u32::try_from(eq.durability).unwrap_or(0),
                            i32::try_from(eq.attack).unwrap_or(0),
                            Vec::new(),
                        ),
                    )
                } else {
                    ObjetInventaire::Equipement(
                        Equipement::new(
                            &row.nom,
                            image,
                            quantite,
                            1,
                            i32::try_from(eq.defense).unwrap_or(0),
                            Vec::new(),
                        ),
                    )
                }
            }

            // ------------------------------------------------
            // POTION
            // ------------------------------------------------

            "potion" => {
                let potion: PotionRow = sqlx::query_as(
                    r#"
                    SELECT effect
                    FROM potions
                    WHERE stuff_id = ?
                    "#,
                )
                .bind(row.stuff_id)
                .fetch_optional(pool)
                .await?
                .ok_or_else(|| {
                    sqlx::Error::Protocol(
                        format!(
                            "Potion manquante pour stuff_id={}",
                            row.stuff_id
                        )
                        .into(),
                    )
                })?;

                ObjetInventaire::Potion(
                    Potion::new(
                        &row.nom,
                        image,
                        quantite,
                        Some(&potion.effect),
                    ),
                )
            }

            // ------------------------------------------------
            // LIVRE ENCHANTÉ
            // ------------------------------------------------

            "enchanted_book" => {
                let book: BookRow = sqlx::query_as(
                    r#"
                    SELECT
                        book_id,
                        book_level
                    FROM enchanted_books
                    WHERE stuff_id = ?
                    "#,
                )
                .bind(row.stuff_id)
                .fetch_optional(pool)
                .await?
                .ok_or_else(|| {
                    sqlx::Error::Protocol(
                        format!(
                            "Livre manquant pour stuff_id={}",
                            row.stuff_id
                        )
                        .into(),
                    )
                })?;

                let enchant_rows: Vec<EnchantRow> =
                    sqlx::query_as(
                        r#"
                        SELECT
                            e.enchantment_name,
                            be.enchantment_level
                        FROM book_enchantments be
                        JOIN enchantments e
                            ON e.enchantment_id =
                               be.enchantment_id
                        WHERE be.book_id = ?
                        ORDER BY e.enchantment_name
                        "#,
                    )
                    .bind(book.book_id)
                    .fetch_all(pool)
                    .await?;

                let enchantements: Vec<String> =
                    enchant_rows
                        .into_iter()
                        .map(|e| {
                            format!(
                                "{} {}",
                                e.enchantment_name,
                                Livre::niv_to_roman(
                                    u32::try_from(
                                        e.enchantment_level
                                    )
                                    .unwrap_or(0),
                                )
                            )
                        })
                        .collect();

                ObjetInventaire::Livre(
                    Livre::new(
                        &row.nom,
                        image,
                        quantite,
                        None,
                        Some(enchantements),
                        u32::try_from(book.book_level)
                            .unwrap_or(0),
                    ),
                )
            }

            // ------------------------------------------------
            // OBJET DE BASE
            // ------------------------------------------------

            _ => ObjetInventaire::Base(
                Objet::new(
                    &row.nom,
                    image,
                    quantite,
                    TypeObjet::DeBase,
                ),
            ),
        };

        Ok(result)
    }

    // ========================================================
    // AJOUT D'UN OBJET
    // ========================================================

    pub async fn ajouter_objet(
        &mut self,
        nom: &str,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        if quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à ajouter doit être supérieure à 0"
                    .into(),
            ));
        }

        let objet = sqlx::query_as::<_, (i64, String)>(
            r#"
            SELECT
                objet_id,
                type
            FROM objets_dispo
            WHERE nom = ?
            "#,
        )
        .bind(nom)
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| {
            sqlx::Error::Protocol(
                format!("Objet absent de objets_dispo : {nom}")
                    .into(),
            )
        })?;

        let objet_id = objet.0;
        let type_objet = objet.1;

        match type_objet.as_str() {
            "equipment" | "armes" => {
                self.ajouter_non_stackable(
                    objet_id,
                    &type_objet,
                    quantite,
                )
                .await?;
            }

            "potion" => {
                self.ajouter_potion(
                    objet_id,
                    nom,
                    quantite,
                )
                .await?;
            }

            "enchanted_book" => {
                self.ajouter_livre(
                    objet_id,
                    nom,
                    quantite,
                )
                .await?;
            }

            _ => {
                self.ajouter_objet_base(
                    objet_id,
                    quantite,
                )
                .await?;
            }
        }

        // Recharge une seule fois, après la totalité de
        // l'opération d'écriture.
        self.recharger().await?;

        Ok(())
    }

    // ========================================================
    // AJOUT OBJET DE BASE
    // ========================================================

    async fn ajouter_objet_base(
        &self,
        objet_id: i64,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        let quantite = Self::quantite_sqlite(quantite)?;

        sqlx::query(
            r#"
            INSERT INTO stuff (
                account_id,
                objet_id,
                quantity,
                stack_key
            )
            VALUES (?, ?, ?, 'base')

            ON CONFLICT (
                account_id,
                objet_id,
                stack_key
            )
            DO UPDATE SET
                quantity =
                    quantity + excluded.quantity
            "#,
        )
        .bind(self.account_id)
        .bind(objet_id)
        .bind(quantite)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    // ========================================================
    // AJOUT POTION
    // ========================================================
    //
    // IMPORTANT :
    //
    // Ancienne version :
    //
    // BEGIN
    // SELECT
    // UPDATE
    // COMMIT
    //
    // Cette structure était exposée à SQLITE_BUSY_SNAPSHOT.
    //
    // Nouvelle version :
    //
    // INSERT ... ON CONFLICT DO UPDATE
    //
    // Il n'y a plus de lecture préalable dans une transaction
    // avant l'écriture.
    // ========================================================

    async fn ajouter_potion(
        &self,
        objet_id: i64,
        nom: &str,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        let effet = Self::effet_potion(nom)?;
        let stack_key = format!("potion:{effet}");
        let quantite = Self::quantite_sqlite(quantite)?;

        let mut tx = self.pool.begin().await?;

        let stuff_id: i64 = sqlx::query_scalar(
            r#"
            INSERT INTO stuff (
                account_id,
                objet_id,
                quantity,
                stack_key
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT (
                account_id,
                objet_id,
                stack_key
            )
            DO UPDATE SET
                quantity =
                    quantity + excluded.quantity

            RETURNING stuff_id
            "#,
        )
        .bind(self.account_id)
        .bind(objet_id)
        .bind(quantite)
        .bind(&stack_key)
        .fetch_one(&mut *tx)
        .await?;

        // Si la ligne existait déjà, la ligne potions existe
        // également. INSERT OR IGNORE évite donc toute collision.
        sqlx::query(
            r#"
            INSERT OR IGNORE INTO potions (
                stuff_id,
                effect
            )
            VALUES (?, ?)
            "#,
        )
        .bind(stuff_id)
        .bind(&effet)
        .execute(&mut *tx)
        .await?;

        tx.commit().await?;

        Ok(())
    }

    // ========================================================
    // EFFET DES POTIONS
    // ========================================================

    fn effet_potion(
        nom: &str,
    ) -> Result<String, sqlx::Error> {
        let effet = match nom {
            "potion de soin léger" => "soin_leger",
            "potion de soin modéré" => "soin_modere",
            "potion de délivrance" => "delivrance",
            "potion de mana" => "mana",

            _ => {
                return Err(sqlx::Error::Protocol(
                    format!("Potion inconnue : {nom}").into(),
                ));
            }
        };

        Ok(effet.to_string())
    }

    // ========================================================
    // AJOUT ÉQUIPEMENT / ARME
    // ========================================================

    async fn ajouter_non_stackable(
        &self,
        objet_id: i64,
        type_objet: &str,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        let mut tx = self.pool.begin().await?;

        let equipment_type = if type_objet == "armes" {
            "weapon"
        } else {
            "armor"
        };

        for _ in 0..quantite {
            let stack_key =
                format!("unique:{}", Uuid::new_v4());

            let stuff_id: i64 = sqlx::query_scalar(
                r#"
                INSERT INTO stuff (
                    account_id,
                    objet_id,
                    quantity,
                    stack_key
                )
                VALUES (?, ?, 1, ?)
                RETURNING stuff_id
                "#,
            )
            .bind(self.account_id)
            .bind(objet_id)
            .bind(&stack_key)
            .fetch_one(&mut *tx)
            .await?;

            sqlx::query(
                r#"
                INSERT INTO equipment (
                    stuff_id,
                    equipment_type,
                    attack,
                    defense,
                    durability
                )
                VALUES (?, ?, 0, 0, 100)
                "#,
            )
            .bind(stuff_id)
            .bind(equipment_type)
            .execute(&mut *tx)
            .await?;
        }

        tx.commit().await?;

        Ok(())
    }

    
    // ========================================================
    // AJOUT LIVRE ENCHANTÉ
    // ========================================================

    async fn ajouter_livre(
        &self,
        objet_id: i64,
        nom: &str,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        let niveau = Self::niveau_livre(nom)?;

        for _ in 0..quantite {
            self.ajouter_un_livre(
                objet_id,
                niveau,
            )
            .await?;
        }

        Ok(())
    }

    // ========================================================
    // AJOUT D'UN SEUL LIVRE
    // ========================================================
    //
    // IMPORTANT :
    //
    // Toute la génération du livre est effectuée AVANT
    // l'ouverture de la transaction d'écriture.
    //
    // Cela évite :
    //
    // BEGIN
    // SELECT ...
    // autre transaction COMMIT
    // INSERT
    // -> SQLITE_BUSY_SNAPSHOT (517)
    //
    // La transaction est donc volontairement très courte.
    //
    // ========================================================

    async fn ajouter_un_livre(
        &self,
        objet_id: i64,
        niveau: u32,
    ) -> Result<(), sqlx::Error> {
        // ----------------------------------------------------
        // 1. Chercher les catégories disponibles
        // ----------------------------------------------------

        let categories: Vec<String> =
            sqlx::query_scalar(
                r#"
                SELECT DISTINCT equipment_type
                FROM enchantment_types
                ORDER BY RANDOM()
                "#,
            )
            .fetch_all(&self.pool)
            .await?;

        if categories.is_empty() {
            return Err(sqlx::Error::Protocol(
                "Aucune catégorie d'équipement disponible \
                 pour générer un livre"
                    .into(),
            ));
        }

        // ----------------------------------------------------
        // 2. Chercher une catégorie ayant suffisamment
        //    d'enchantements pour le niveau demandé
        // ----------------------------------------------------

        let mut categorie_selectionnee: Option<String> =
            None;

        for categorie in &categories {
            let count: i64 =
                sqlx::query_scalar(
                    r#"
                    SELECT COUNT(DISTINCT et.enchantment_id)
                    FROM enchantment_types et
                    JOIN enchantment_levels el
                        ON el.enchantment_id =
                           et.enchantment_id
                    WHERE et.equipment_type = ?
                      AND el.book_level = ?
                    "#,
                )
                .bind(categorie)
                .bind(i64::from(niveau))
                .fetch_one(&self.pool)
                .await?;

            if count >= i64::from(niveau) {
                categorie_selectionnee =
                    Some(categorie.clone());

                break;
            }
        }

        // ----------------------------------------------------
        // 3. Choisir une catégorie de secours si nécessaire
        // ----------------------------------------------------

        let categorie =
            categorie_selectionnee
                .or_else(|| categories.first().cloned())
                .ok_or_else(|| {
                    sqlx::Error::Protocol(
                        "Impossible de sélectionner une \
                         catégorie d'enchantement"
                            .into(),
                    )
                })?;

        // ----------------------------------------------------
        // 4. Sélectionner les enchantements
        // ----------------------------------------------------

        let enchantements: Vec<GeneratedEnchant> =
            sqlx::query_as(
                r#"
                SELECT DISTINCT
                    et.enchantment_id,
                    el.max_enchantment_level AS max_level
                FROM enchantment_types et
                JOIN enchantment_levels el
                    ON el.enchantment_id =
                       et.enchantment_id
                WHERE et.equipment_type = ?
                  AND el.book_level = ?
                ORDER BY RANDOM()
                LIMIT ?
                "#,
            )
            .bind(&categorie)
            .bind(i64::from(niveau))
            .bind(i64::from(niveau))
            .fetch_all(&self.pool)
            .await?;

        if enchantements.is_empty() {
            return Err(sqlx::Error::Protocol(
                format!(
                    "Aucun enchantement compatible avec \
                     la catégorie {categorie}"
                )
                .into(),
            ));
        }

        // ----------------------------------------------------
        // 5. Générer le niveau de chaque enchantement
        // ----------------------------------------------------

        let mut enchantement_data: Vec<(i64, i64)> =
            Vec::with_capacity(enchantements.len());

        for enchantement in enchantements {
            let maximum =
                std::cmp::min(
                    i64::from(niveau),
                    enchantement.max_level,
                );

            if maximum <= 0 {
                return Err(sqlx::Error::Protocol(
                    format!(
                        "Niveau maximal invalide pour \
                         enchantement_id={}",
                        enchantement.enchantment_id
                    )
                    .into(),
                ));
            }

            let niveau_enchantement: i64 =
                sqlx::query_scalar(
                    r#"
                    SELECT
                        1 + (
                            abs(random()) % ?
                        )
                    "#,
                )
                .bind(maximum)
                .fetch_one(&self.pool)
                .await?;

            enchantement_data.push((
                enchantement.enchantment_id,
                niveau_enchantement,
            ));
        }

        // ----------------------------------------------------
        // 6. Trier les enchantements
        //
        // L'ordre des enchantements ne doit pas modifier
        // l'identité du livre.
        // ----------------------------------------------------

        enchantement_data.sort_by_key(
            |(enchantment_id, level)| {
                (*enchantment_id, *level)
            },
        );

        // ----------------------------------------------------
        // 7. Générer la stack_key canonique
        // ----------------------------------------------------

        let contenu = enchantement_data
            .iter()
            .map(|(id, level)| {
                format!("{id}:{level}")
            })
            .collect::<Vec<_>>()
            .join("|");

        let stack_key =
            format!("book:{niveau}:{contenu}");

        // ====================================================
        // 8. TRANSACTION D'ÉCRITURE
        // ====================================================
        //
        // IMPORTANT :
        //
        // Toutes les lectures/générations précédentes sont
        // terminées avant BEGIN.
        //
        // La transaction ne contient maintenant que les
        // opérations nécessaires à l'écriture.
        //
        // ====================================================

        let mut tx = self.pool.begin().await?;

        // ----------------------------------------------------
        // 9. Créer le stack ou augmenter sa quantité
        // ----------------------------------------------------

        let stuff_id: i64 =
            sqlx::query_scalar(
                r#"
                INSERT INTO stuff (
                    account_id,
                    objet_id,
                    quantity,
                    stack_key
                )
                VALUES (?, ?, 1, ?)

                ON CONFLICT (
                    account_id,
                    objet_id,
                    stack_key
                )
                DO UPDATE SET
                    quantity =
                        quantity + 1

                RETURNING stuff_id
                "#,
            )
            .bind(self.account_id)
            .bind(objet_id)
            .bind(&stack_key)
            .fetch_one(&mut *tx)
            .await?;

        // ----------------------------------------------------
        // 10. Vérifier si le livre existe déjà
        // ----------------------------------------------------

        let book_id: Option<i64> =
            sqlx::query_scalar(
                r#"
                SELECT book_id
                FROM enchanted_books
                WHERE stuff_id = ?
                "#,
            )
            .bind(stuff_id)
            .fetch_optional(&mut *tx)
            .await?;

        // ----------------------------------------------------
        // Le livre existait déjà.
        //
        // L'UPSERT précédent a déjà augmenté quantity.
        // Il n'y a donc rien d'autre à créer.
        // ----------------------------------------------------

        if book_id.is_some() {
            tx.commit().await?;
            return Ok(());
        }

        // ----------------------------------------------------
        // 11. Créer le livre
        // ----------------------------------------------------

        let book_id: i64 =
            sqlx::query_scalar(
                r#"
                INSERT INTO enchanted_books (
                    stuff_id,
                    book_level
                )
                VALUES (?, ?)
                RETURNING book_id
                "#,
            )
            .bind(stuff_id)
            .bind(i64::from(niveau))
            .fetch_one(&mut *tx)
            .await?;

        // ----------------------------------------------------
        // 12. Insérer les enchantements
        // ----------------------------------------------------

        for (
            enchantment_id,
            enchantment_level,
        ) in enchantement_data
        {
            sqlx::query(
                r#"
                INSERT INTO book_enchantments (
                    book_id,
                    enchantment_id,
                    enchantment_level
                )
                VALUES (?, ?, ?)
                "#,
            )
            .bind(book_id)
            .bind(enchantment_id)
            .bind(enchantment_level)
            .execute(&mut *tx)
            .await?;
        }

        // ----------------------------------------------------
        // 13. Validation
        // ----------------------------------------------------

        tx.commit().await?;

        Ok(())
    }

    // ========================================================
    // EXTRACTION DU NIVEAU DU LIVRE
    // ========================================================

    fn niveau_livre(
        nom: &str,
    ) -> Result<u32, sqlx::Error> {
        let prefix = "livre enchant niv ";

        let niveau = nom
            .strip_prefix(prefix)
            .ok_or_else(|| {
                sqlx::Error::Protocol(
                    format!(
                        "Nom de livre invalide : {nom}"
                    )
                    .into(),
                )
            })?
            .parse::<u32>()
            .map_err(|_| {
                sqlx::Error::Protocol(
                    format!(
                        "Niveau de livre invalide : {nom}"
                    )
                    .into(),
                )
            })?;

        if !(1..=6).contains(&niveau) {
            return Err(sqlx::Error::Protocol(
                format!(
                    "Niveau de livre hors limites : {niveau}"
                )
                .into(),
            ));
        }

        Ok(niveau)
    }

    // ========================================================
    // RETRAIT D'UN OBJET
    // ========================================================

    pub async fn retirer_objet(
        &mut self,
        stuff_id: i64,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        if quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à retirer doit être supérieure à 0"
                    .into(),
            ));
        }

        let quantite_i64 =
            Self::quantite_sqlite(quantite)?;

        // ----------------------------------------------------
        // Vérification mémoire
        // ----------------------------------------------------

        if !self.objets.contains_key(&stuff_id) {
            return Err(sqlx::Error::Protocol(
                format!(
                    "Objet absent de l'inventaire : \
                     stuff_id={stuff_id}"
                )
                .into(),
            ));
        }

        let quantite_db: i64 = sqlx::query_scalar(
            r#"
            SELECT quantity
            FROM stuff
            WHERE stuff_id = ?
              AND account_id = ?
            "#,
        )
        .bind(stuff_id)
        .bind(self.account_id)
        .fetch_optional(&self.pool)
        .await?
        .ok_or(sqlx::Error::RowNotFound)?;

        let quantite_actuelle = u64::try_from(quantite_db)
            .map_err(|_| {
                sqlx::Error::Protocol(
                    format!(
                        "Quantité invalide pour stuff_id={stuff_id}"
                    )
                    .into(),
                )
            })?;

        if quantite > quantite_actuelle {
            return Err(sqlx::Error::Protocol(
                format!(
                    "Quantité insuffisante : possède {}, \
                     demande {}",
                    quantite_actuelle,
                    quantite
                )
                .into(),
            ));
        }

        // ----------------------------------------------------
        // Transaction d'écriture
        // ----------------------------------------------------

        let mut tx = self.pool.begin().await?;

        if quantite == quantite_actuelle {
            let result = sqlx::query(
                r#"
                DELETE FROM stuff
                WHERE stuff_id = ?
                  AND account_id = ?
                "#,
            )
            .bind(stuff_id)
            .bind(self.account_id)
            .execute(&mut *tx)
            .await?;

            if result.rows_affected() == 0 {
                tx.rollback().await?;

                return Err(sqlx::Error::RowNotFound);
            }
        } else {
            let result = sqlx::query(
                r#"
                UPDATE stuff
                SET quantity = quantity - ?
                WHERE stuff_id = ?
                  AND account_id = ?
                  AND quantity >= ?
                "#,
            )
            .bind(quantite_i64)
            .bind(stuff_id)
            .bind(self.account_id)
            .bind(quantite_i64)
            .execute(&mut *tx)
            .await?;

            if result.rows_affected() == 0 {
                tx.rollback().await?;

                return Err(sqlx::Error::RowNotFound);
            }
        }

        tx.commit().await?;

        // ----------------------------------------------------
        // Mise à jour mémoire
        // ----------------------------------------------------

        if quantite == quantite_actuelle {
            self.objets.remove(&stuff_id);
        } else if let Some(objet) =
            self.objets.get_mut(&stuff_id)
        {
            objet.retirer(quantite);
        }

        Ok(())
    }

    // ========================================================
    // RETRAIT DANS UNE TRANSACTION EXISTANTE
    // ========================================================

    pub async fn retirer_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        objet_id: i64,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        if quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à retirer doit être supérieure à 0"
                    .into(),
            ));
        }

        let quantite_i64 =
            Self::quantite_sqlite(quantite)?;

        let quantity: Option<i64> =
            sqlx::query_scalar(
                r#"
                SELECT quantity
                FROM stuff
                WHERE account_id = ?
                  AND objet_id = ?
                  AND stack_key = 'base'
                "#,
            )
            .bind(account_id)
            .bind(objet_id)
            .fetch_optional(&mut **tx)
            .await?;

        let quantity =
            quantity.unwrap_or(0);

        if quantity < quantite_i64 {
            return Err(sqlx::Error::Protocol(
                "Quantité insuffisante".into(),
            ));
        }

        if quantity == quantite_i64 {
            sqlx::query(
                r#"
                DELETE FROM stuff
                WHERE account_id = ?
                  AND objet_id = ?
                  AND stack_key = 'base'
                "#,
            )
            .bind(account_id)
            .bind(objet_id)
            .execute(&mut **tx)
            .await?;
        } else {
            sqlx::query(
                r#"
                UPDATE stuff
                SET quantity = quantity - ?
                WHERE account_id = ?
                  AND objet_id = ?
                  AND stack_key = 'base'
                  AND quantity >= ?
                "#,
            )
            .bind(quantite_i64)
            .bind(account_id)
            .bind(objet_id)
            .bind(quantite_i64)
            .execute(&mut **tx)
            .await?;
        }

        Ok(())
    }

    // ========================================================
    // AJOUT DANS UNE TRANSACTION EXISTANTE
    // ========================================================

    pub async fn ajouter_tx(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        objet_id: i64,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        if quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à ajouter doit être supérieure à 0"
                    .into(),
            ));
        }

        let quantite_i64 =
            Self::quantite_sqlite(quantite)?;

        sqlx::query(
            r#"
            INSERT INTO stuff (
                account_id,
                objet_id,
                quantity,
                stack_key
            )
            VALUES (?, ?, ?, 'base')

            ON CONFLICT (
                account_id,
                objet_id,
                stack_key
            )
            DO UPDATE SET
                quantity =
                    quantity + excluded.quantity
            "#,
        )
        .bind(account_id)
        .bind(objet_id)
        .bind(quantite_i64)
        .execute(&mut **tx)
        .await?;

        Ok(())
    }

    // ========================================================
    // QUANTITÉ TOTALE D'UN OBJET PAR NOM
    // ========================================================

    pub async fn get_quantity(
        &self,
        nom: &str,
    ) -> Result<u64, sqlx::Error> {
        let quantity: i64 =
            sqlx::query_scalar(
                r#"
                SELECT COALESCE(
                    SUM(s.quantity),
                    0
                )
                FROM stuff s
                JOIN objets_dispo o
                    ON s.objet_id = o.objet_id
                WHERE s.account_id = ?
                  AND o.nom = ?
                "#,
            )
            .bind(self.account_id)
            .bind(nom)
            .fetch_one(&self.pool)
            .await?;

        u64::try_from(quantity)
            .map_err(|_| {
                sqlx::Error::Protocol(
                    format!(
                        "Quantité invalide pour {nom}"
                    )
                    .into(),
                )
            })
    }

    
    // ========================================================
    // CONVERSION QUANTITÉ SQLITE
    // ========================================================

    fn quantite_sqlite(quantite: u64) -> Result<i64, sqlx::Error> {
        i64::try_from(quantite).map_err(|_| {
            sqlx::Error::Protocol(
                format!(
                    "La quantité {} dépasse la capacité d'un INTEGER SQLite",
                    quantite
                )
                .into(),
            )
        })
    }

    

    // ========================================================
    // ACCÈS À L'INVENTAIRE
    // ========================================================

    pub fn objets(&self) -> &HashMap<i64, ObjetInventaire> {
        &self.objets
    }

    pub fn objets_mut(&mut self) -> &mut HashMap<i64, ObjetInventaire> {
        &mut self.objets
    }

    // ========================================================
    // RECHARGEMENT
    // ========================================================

    pub async fn recharger(&mut self) -> Result<(), sqlx::Error> {
        self.objets = Self::charger_objets(
            &self.pool,
            self.account_id,
        )
        .await?;

        Ok(())
    }

    // ========================================================
    // ACCOUNT ID
    // ========================================================

    pub fn account_id(&self) -> i64 {
        self.account_id
    }
}
