use rand::RngExt;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
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
    Rank,
    TypeObjet,
};
use crate::gameplay::tresor::{ArtefactTire, ResultatOuverture, Tresor};

// ============================================================
// ENUM UNIFIÉ POUR LE HASHMAP D'INVENTAIRE
// ============================================================
//
// Chaque entrée de l'inventaire contient l'objet LUI-MÊME
// (Objet / Equipement / Arme / Potion / Livre), avec sa rareté
// (`objet().rarety`) et son rank (`objet().rank`).

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum ObjetInventaire {
    Base(Objet),
    Equipement(Equipement),
    Arme(Arme),
    Potion(Potion),
    Livre(Livre),
}

impl ObjetInventaire {
    /// L'`Objet` de base contenu dans n'importe quelle variante.
    pub fn objet(&self) -> &Objet {
        match self {
            ObjetInventaire::Base(o) => o,
            ObjetInventaire::Equipement(e) => &e.objet,
            ObjetInventaire::Arme(a) => &a.equipement.objet,
            ObjetInventaire::Potion(p) => &p.objet,
            ObjetInventaire::Livre(l) => &l.objet,
        }
    }

    pub fn objet_mut(&mut self) -> &mut Objet {
        match self {
            ObjetInventaire::Base(o) => o,
            ObjetInventaire::Equipement(e) => &mut e.objet,
            ObjetInventaire::Arme(a) => &mut a.equipement.objet,
            ObjetInventaire::Potion(p) => &mut p.objet,
            ObjetInventaire::Livre(l) => &mut l.objet,
        }
    }

    /// Rareté de l'objet ("Commun", "Rare", ...), si elle existe.
    pub fn rarete(&self) -> Option<&str> {
        self.objet().rarety.as_deref()
    }

    /// Rank de l'objet ("G" ... "SSS"), s'il existe.
    pub fn rank(&self) -> Option<&str> {
        self.objet().rank.as_deref()
    }
}

impl NomAffiche for ObjetInventaire {
    fn nom_affiche(&self) -> String {
        match self {
            ObjetInventaire::Base(o) => o.nom_affiche(),
            ObjetInventaire::Equipement(e) => e.nom_affiche(),
            ObjetInventaire::Arme(a) => a.nom_affiche(),
            ObjetInventaire::Potion(p) => p.nom_affiche(),
            ObjetInventaire::Livre(l) => l.nom_affiche(),
        }
    }
}

impl AjouterRetirer for ObjetInventaire {
    fn ajouter(&mut self, qte: u64) {
        self.objet_mut().ajouter(qte);
    }

    fn retirer(&mut self, qte: u64) {
        self.objet_mut().retirer(qte);
    }
}

// ============================================================
// MARQUE (rareté + rank) D'UN OBJET À AJOUTER
// ============================================================
//
// La marque fait partie de la `stack_key` : deux objets identiques
// de rank différent ne sont PAS fusionnés dans le même stack.
// Une marque vide donne la même stack_key qu'avant ("base", ...).

#[derive(Debug, Clone, Default)]
struct Marque {
    rarete: Option<String>,
    rang: Option<String>,
}

impl Marque {
    fn depuis(artefact: &ArtefactTire) -> Self {
        Self {
            rarete: artefact.rarete.map(|r| r.label().to_string()),
            rang: artefact.rank.map(|r| r.label().to_string()),
        }
    }

    /// Suffixe ajouté à la stack_key ("" si aucune marque).
    fn suffixe(&self) -> String {
        if self.rarete.is_none() && self.rang.is_none() {
            return String::new();
        }

        format!(
            ":{}:{}",
            self.rarete.as_deref().unwrap_or("-"),
            self.rang.as_deref().unwrap_or("-"),
        )
    }
}

// ============================================================
// ÉCRITURES PRÉPARÉES
// ============================================================
//
// Toute la préparation (lectures, génération aléatoire des livres)
// est faite AVANT d'ouvrir la transaction. L'écriture se fait ensuite
// en une seule transaction courte, sans aucune lecture dedans
// (pas de SQLITE_BUSY_SNAPSHOT).

enum Ecriture {
    Base {
        objet_id: i64,
        quantite: i64,
        stack_key: String,
        marque: Marque,
    },
    Potion {
        objet_id: i64,
        quantite: i64,
        effet: String,
        stack_key: String,
        marque: Marque,
    },
    Unique {
        objet_id: i64,
        equipment_type: &'static str,
        marque: Marque,
    },
    Livre {
        objet_id: i64,
        niveau: u32,
        stack_key: String,
        enchants: Vec<(i64, i64)>,
        marque: Marque,
    },
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
    rarete: Option<String>,
    rang: Option<String>,
}

#[derive(sqlx::FromRow)]
struct EquipmentRow {
    stuff_id: i64,
    equipment_type: String,
    attack: i64,
    defense: i64,
    durability: i64,
}

#[derive(sqlx::FromRow)]
struct PotionRow {
    stuff_id: i64,
    effect: String,
}

#[derive(sqlx::FromRow)]
struct BookRow {
    stuff_id: i64,
    book_id: i64,
    book_level: i64,
}

#[derive(sqlx::FromRow)]
struct EnchantRow {
    book_id: i64,
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
        Self::migrer_schema(&pool).await?;

        let objets = Self::charger_objets(&pool, account_id).await?;

        Ok(Self {
            pool,
            account_id,
            objets,
        })
    }

    // ========================================================
    // MIGRATION : COLONNES RARETÉ / RANK DE LA TABLE stuff
    // ========================================================
    //
    // Idempotente : ne fait rien si les colonnes existent déjà.

    pub async fn migrer_schema(
        pool: &SqlitePool,
    ) -> Result<(), sqlx::Error> {
        let colonnes: Vec<String> = sqlx::query_scalar(
            "SELECT name FROM pragma_table_info('stuff')",
        )
        .fetch_all(pool)
        .await?;

        if !colonnes.iter().any(|c| c == "rarete") {
            sqlx::query("ALTER TABLE stuff ADD COLUMN rarete TEXT")
                .execute(pool)
                .await?;
        }

        if !colonnes.iter().any(|c| c == "rang") {
            sqlx::query("ALTER TABLE stuff ADD COLUMN rang TEXT")
                .execute(pool)
                .await?;
        }

        Ok(())
    }

    // ========================================================
    // CHARGEMENT DE L'INVENTAIRE
    // ========================================================
    //
    // 5 requêtes au total, quel que soit le nombre d'objets
    // (avant : 1 à 3 requêtes PAR objet).

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
                o.image_path,
                s.rarete,
                s.rang
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

        let equipements: HashMap<i64, EquipmentRow> =
            sqlx::query_as::<_, EquipmentRow>(
                r#"
                SELECT
                    eq.stuff_id,
                    eq.equipment_type,
                    eq.attack,
                    eq.defense,
                    eq.durability
                FROM equipment eq
                JOIN stuff s ON s.stuff_id = eq.stuff_id
                WHERE s.account_id = ?
                "#,
            )
            .bind(account_id)
            .fetch_all(pool)
            .await?
            .into_iter()
            .map(|e| (e.stuff_id, e))
            .collect();

        let potions: HashMap<i64, PotionRow> =
            sqlx::query_as::<_, PotionRow>(
                r#"
                SELECT p.stuff_id, p.effect
                FROM potions p
                JOIN stuff s ON s.stuff_id = p.stuff_id
                WHERE s.account_id = ?
                "#,
            )
            .bind(account_id)
            .fetch_all(pool)
            .await?
            .into_iter()
            .map(|p| (p.stuff_id, p))
            .collect();

        let livres: HashMap<i64, BookRow> =
            sqlx::query_as::<_, BookRow>(
                r#"
                SELECT b.stuff_id, b.book_id, b.book_level
                FROM enchanted_books b
                JOIN stuff s ON s.stuff_id = b.stuff_id
                WHERE s.account_id = ?
                "#,
            )
            .bind(account_id)
            .fetch_all(pool)
            .await?
            .into_iter()
            .map(|b| (b.stuff_id, b))
            .collect();

        let mut enchants: HashMap<i64, Vec<EnchantRow>> =
            HashMap::new();

        let enchant_rows = sqlx::query_as::<_, EnchantRow>(
            r#"
            SELECT
                be.book_id,
                e.enchantment_name,
                be.enchantment_level
            FROM book_enchantments be
            JOIN enchantments e
                ON e.enchantment_id = be.enchantment_id
            JOIN enchanted_books b
                ON b.book_id = be.book_id
            JOIN stuff s
                ON s.stuff_id = b.stuff_id
            WHERE s.account_id = ?
            ORDER BY e.enchantment_name
            "#,
        )
        .bind(account_id)
        .fetch_all(pool)
        .await?;

        for e in enchant_rows {
            enchants.entry(e.book_id).or_default().push(e);
        }

        let mut inventaire = HashMap::with_capacity(rows.len());

        for row in &rows {
            let objet = Self::construire_objet(
                row,
                &equipements,
                &potions,
                &livres,
                &enchants,
            )?;

            inventaire.insert(row.stuff_id, objet);
        }

        Ok(inventaire)
    }

    // ========================================================
    // CONSTRUCTION D'UN OBJET (rareté et rank inclus)
    // ========================================================

    fn construire_objet(
        row: &StuffRow,
        equipements: &HashMap<i64, EquipmentRow>,
        potions: &HashMap<i64, PotionRow>,
        livres: &HashMap<i64, BookRow>,
        enchants: &HashMap<i64, Vec<EnchantRow>>,
    ) -> Result<ObjetInventaire, sqlx::Error> {
        let manquant = |quoi: &str| {
            sqlx::Error::Protocol(
                format!("{quoi} manquant(e) pour stuff_id={}", row.stuff_id)
                    .into(),
            )
        };

        let quantite = u64::try_from(row.quantity).map_err(|_| {
            sqlx::Error::Protocol(
                format!(
                    "Quantité invalide pour {} : {}",
                    row.nom, row.quantity
                )
                .into(),
            )
        })?;

        let image = row.image_path.as_deref();
        let rarete = row.rarete.as_deref();

        let mut result = match row.type_objet.as_str() {
            // ------------------------------------------------
            // ÉQUIPEMENT / ARME
            // ------------------------------------------------
            "equipment" | "armes" => {
                let eq = equipements
                    .get(&row.stuff_id)
                    .ok_or_else(|| manquant("Équipement"))?;

                if eq.equipment_type == "weapon" {
                    ObjetInventaire::Arme(Arme::new(
                        &row.nom,
                        image,
                        quantite,
                        1,
                        u32::try_from(eq.durability).unwrap_or(0),
                        i32::try_from(eq.attack).unwrap_or(0),
                        Vec::new(),
                        rarete,
                    ))
                } else {
                    ObjetInventaire::Equipement(Equipement::new(
                        &row.nom,
                        image,
                        quantite,
                        1,
                        i32::try_from(eq.defense).unwrap_or(0),
                        Vec::new(),
                        rarete,
                    ))
                }
            }

            // ------------------------------------------------
            // POTION
            // ------------------------------------------------
            "potion" => {
                let potion = potions
                    .get(&row.stuff_id)
                    .ok_or_else(|| manquant("Potion"))?;

                ObjetInventaire::Potion(Potion::new(
                    &row.nom,
                    image,
                    quantite,
                    Some(&potion.effect),
                    rarete,
                ))
            }

            // ------------------------------------------------
            // LIVRE ENCHANTÉ
            // ------------------------------------------------
            "enchanted_book" => {
                let book = livres
                    .get(&row.stuff_id)
                    .ok_or_else(|| manquant("Livre"))?;

                let enchantements: Vec<String> = enchants
                    .get(&book.book_id)
                    .map(|liste| {
                        liste
                            .iter()
                            .map(|e| {
                                format!(
                                    "{} {}",
                                    e.enchantment_name,
                                    Livre::niv_to_roman(
                                        u32::try_from(e.enchantment_level)
                                            .unwrap_or(0),
                                    )
                                )
                            })
                            .collect()
                    })
                    .unwrap_or_default();

                ObjetInventaire::Livre(Livre::new(
                    &row.nom,
                    image,
                    quantite,
                    None,
                    Some(enchantements),
                    rarete,
                    u32::try_from(book.book_level).unwrap_or(0),
                ))
            }

            // ------------------------------------------------
            // OBJET DE BASE
            // ------------------------------------------------
            _ => ObjetInventaire::Base(Objet::new(
                &row.nom,
                image,
                quantite,
                TypeObjet::DeBase,
                rarete,
            )),
        };

        // Le rank n'est pas un paramètre des constructeurs.
        result.objet_mut().rank = row.rang.clone();

        Ok(result)
    }

    // ========================================================
    // AJOUT D'UN OBJET SANS RARETÉ NI RANK (API conservée)
    // ========================================================

    pub async fn ajouter_objet(
        &mut self,
        nom: &str,
        quantite: u64,
    ) -> Result<(), sqlx::Error> {
        if quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à ajouter doit être supérieure à 0".into(),
            ));
        }

        self.ajouter_lot(vec![(
            nom.to_string(),
            quantite,
            Marque::default(),
        )])
        .await
    }

    // ========================================================
    // AJOUT D'UN ARTÉFACT TIRÉ (rareté + rank conservés)
    // ========================================================

    pub async fn ajouter_artefact(
        &mut self,
        artefact: &ArtefactTire,
    ) -> Result<(), sqlx::Error> {
        if artefact.quantite == 0 {
            return Err(sqlx::Error::Protocol(
                "La quantité à ajouter doit être supérieure à 0".into(),
            ));
        }

        self.ajouter_lot(vec![(
            artefact.nom.clone(),
            u64::from(artefact.quantite),
            Marque::depuis(artefact),
        )])
        .await
    }

    // ========================================================
    // AJOUT DU RÉSULTAT COMPLET D'UN COFFRE
    // ========================================================
    //
    // Prend exactement ce que renvoie `Tresor::ouvrir`.
    // Tout est écrit dans UNE seule transaction (tout ou rien),
    // puis l'inventaire est rechargé UNE seule fois.

    pub async fn ajouter_resultat(
        &mut self,
        resultat: &ResultatOuverture,
    ) -> Result<(), sqlx::Error> {
        let mut lot: Vec<(String, u64, Marque)> =
            Vec::with_capacity(
                resultat.objets.len() + resultat.artefacts.len(),
            );

        for (nom, quantite) in &resultat.objets {
            if *quantite > 0 {
                lot.push((
                    nom.clone(),
                    u64::from(*quantite),
                    Marque::default(),
                ));
            }
        }

        for artefact in &resultat.artefacts {
            if artefact.quantite > 0 {
                lot.push((
                    artefact.nom.clone(),
                    u64::from(artefact.quantite),
                    Marque::depuis(artefact),
                ));
            }
        }

        if lot.is_empty() {
            return Ok(());
        }

        self.ajouter_lot(lot).await
    }

    // ========================================================
    // OUVRIR UN COFFRE ET RANGER LE CONTENU
    // ========================================================
    //
    // Mêmes paramètres que `Tresor::ouvrir`, sans `pool` ni
    // `account_id` (l'inventaire les possède déjà).

    pub async fn ouvrir_coffre(
        &mut self,
        tresor: &mut Tresor,
        niveau: u32,
        is_admin: bool,
        is_militaire: bool,
        coeff_loot: Option<f64>,
    ) -> Result<ResultatOuverture, sqlx::Error> {
        let resultat = tresor
            .ouvrir(
                &self.pool,
                self.account_id,
                niveau,
                is_admin,
                is_militaire,
                coeff_loot,
            )
            .await?;

        self.ajouter_resultat(&resultat).await?;

        Ok(resultat)
    }

    // ========================================================
    // AJOUT D'UN LOT : PRÉPARATION -> UNE TRANSACTION -> RECHARGE
    // ========================================================

    async fn ajouter_lot(
        &mut self,
        lot: Vec<(String, u64, Marque)>,
    ) -> Result<(), sqlx::Error> {
        // 1 seule requête pour résoudre tous les noms.
        let catalogue = self.charger_catalogue().await?;

        // Lectures + génération aléatoire (avant la transaction).
        let mut ecritures: Vec<Ecriture> = Vec::new();

        for (nom, quantite, marque) in &lot {
            let mut prevues = self
                .preparer(nom, *quantite, marque, &catalogue)
                .await?;

            ecritures.append(&mut prevues);
        }

        // Transaction d'écriture unique et courte.
        let mut tx = self.pool.begin().await?;

        for ecriture in &ecritures {
            Self::executer(&mut tx, self.account_id, ecriture).await?;
        }

        tx.commit().await?;

        // Recharge une seule fois, après toute l'écriture.
        self.recharger().await?;

        Ok(())
    }

    // ========================================================
    // CATALOGUE : nom -> (objet_id, type)
    // ========================================================

    async fn charger_catalogue(
        &self,
    ) -> Result<HashMap<String, (i64, String)>, sqlx::Error> {
        let rows: Vec<(String, i64, String)> = sqlx::query_as(
            "SELECT nom, objet_id, type FROM objets_dispo",
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(rows
            .into_iter()
            .map(|(nom, id, type_objet)| (nom, (id, type_objet)))
            .collect())
    }

    // ========================================================
    // PRÉPARATION DES ÉCRITURES D'UN OBJET
    // ========================================================

    async fn preparer(
        &self,
        nom: &str,
        quantite: u64,
        marque: &Marque,
        catalogue: &HashMap<String, (i64, String)>,
    ) -> Result<Vec<Ecriture>, sqlx::Error> {
        let (objet_id, type_objet) = catalogue
            .get(nom)
            .cloned()
            .ok_or_else(|| {
                sqlx::Error::Protocol(
                    format!("Objet absent de objets_dispo : {nom}")
                        .into(),
                )
            })?;

        let suffixe = marque.suffixe();

        match type_objet.as_str() {
            // ------------------------------------------------
            // ÉQUIPEMENT / ARME : 1 ligne par exemplaire
            // ------------------------------------------------
            "equipment" | "armes" => {
                let equipment_type = if type_objet == "armes" {
                    "weapon"
                } else {
                    "armor"
                };

                Ok((0..quantite)
                    .map(|_| Ecriture::Unique {
                        objet_id,
                        equipment_type,
                        marque: marque.clone(),
                    })
                    .collect())
            }

            // ------------------------------------------------
            // POTION
            // ------------------------------------------------
            "potion" => {
                let effet = Self::effet_potion(nom)?;
                let stack_key = format!("potion:{effet}{suffixe}");

                Ok(vec![Ecriture::Potion {
                    objet_id,
                    quantite: Self::quantite_sqlite(quantite)?,
                    effet,
                    stack_key,
                    marque: marque.clone(),
                }])
            }

            // ------------------------------------------------
            // LIVRE ENCHANTÉ : enchantements aléatoires par livre
            // ------------------------------------------------
            "enchanted_book" => {
                let niveau = Self::niveau_livre(nom)?;
                let mut ecritures =
                    Vec::with_capacity(quantite as usize);

                for _ in 0..quantite {
                    ecritures.push(
                        self.preparer_livre(objet_id, niveau, marque)
                            .await?,
                    );
                }

                Ok(ecritures)
            }

            // ------------------------------------------------
            // OBJET DE BASE
            // ------------------------------------------------
            _ => Ok(vec![Ecriture::Base {
                objet_id,
                quantite: Self::quantite_sqlite(quantite)?,
                stack_key: format!("base{suffixe}"),
                marque: marque.clone(),
            }]),
        }
    }

    // ========================================================
    // EXÉCUTION D'UNE ÉCRITURE (dans la transaction)
    // ========================================================

    async fn executer(
        tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
        account_id: i64,
        ecriture: &Ecriture,
    ) -> Result<(), sqlx::Error> {
        match ecriture {
            // ------------------------------------------------
            Ecriture::Base {
                objet_id,
                quantite,
                stack_key,
                marque,
            } => {
                sqlx::query(
                    r#"
                    INSERT INTO stuff (
                        account_id,
                        objet_id,
                        quantity,
                        stack_key,
                        rarete,
                        rang
                    )
                    VALUES (?, ?, ?, ?, ?, ?)

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
                .bind(quantite)
                .bind(stack_key)
                .bind(marque.rarete.as_deref())
                .bind(marque.rang.as_deref())
                .execute(&mut **tx)
                .await?;
            }

            // ------------------------------------------------
            Ecriture::Potion {
                objet_id,
                quantite,
                effet,
                stack_key,
                marque,
            } => {
                let stuff_id: i64 = sqlx::query_scalar(
                    r#"
                    INSERT INTO stuff (
                        account_id,
                        objet_id,
                        quantity,
                        stack_key,
                        rarete,
                        rang
                    )
                    VALUES (?, ?, ?, ?, ?, ?)

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
                .bind(account_id)
                .bind(objet_id)
                .bind(quantite)
                .bind(stack_key)
                .bind(marque.rarete.as_deref())
                .bind(marque.rang.as_deref())
                .fetch_one(&mut **tx)
                .await?;

                // Si le stack existait déjà, la ligne potions existe
                // aussi : INSERT OR IGNORE évite toute collision.
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
                .bind(effet)
                .execute(&mut **tx)
                .await?;
            }

            // ------------------------------------------------
            Ecriture::Unique {
                objet_id,
                equipment_type,
                marque,
            } => {
                let stack_key = format!("unique:{}", Uuid::new_v4());

                // Stats selon le rank. Sans rank : 0 / 0 / 100 comme avant.
                // Avec rank : 10 x multiplicateur (attaque pour une arme,
                // défense pour une armure) et 100 x multiplicateur (durabilité).
                let multiplicateur = marque
                    .rang
                    .as_deref()
                    .and_then(Rank::depuis_label)
                    .map(|r| r.multiplicateur());

                let (attack, defense, durability): (i64, i64, i64) =
                    match multiplicateur {
                        Some(m) => {
                            let stat = (10.0 * m).round() as i64;
                            let est_arme = *equipment_type == "weapon";

                            (
                                if est_arme { stat } else { 0 },
                                if est_arme { 0 } else { stat },
                                (100.0 * m).round() as i64,
                            )
                        }
                        None => (0, 0, 100),
                    };

                let stuff_id: i64 = sqlx::query_scalar(
                    r#"
                    INSERT INTO stuff (
                        account_id,
                        objet_id,
                        quantity,
                        stack_key,
                        rarete,
                        rang
                    )
                    VALUES (?, ?, 1, ?, ?, ?)
                    RETURNING stuff_id
                    "#,
                )
                .bind(account_id)
                .bind(objet_id)
                .bind(&stack_key)
                .bind(marque.rarete.as_deref())
                .bind(marque.rang.as_deref())
                .fetch_one(&mut **tx)
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
                    VALUES (?, ?, ?, ?, ?)
                    "#,
                )
                .bind(stuff_id)
                .bind(equipment_type)
                .bind(attack)
                .bind(defense)
                .bind(durability)
                .execute(&mut **tx)
                .await?;
            }

            // ------------------------------------------------
            Ecriture::Livre {
                objet_id,
                niveau,
                stack_key,
                enchants,
                marque,
            } => {
                let stuff_id: i64 = sqlx::query_scalar(
                    r#"
                    INSERT INTO stuff (
                        account_id,
                        objet_id,
                        quantity,
                        stack_key,
                        rarete,
                        rang
                    )
                    VALUES (?, ?, 1, ?, ?, ?)

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
                .bind(account_id)
                .bind(objet_id)
                .bind(stack_key)
                .bind(marque.rarete.as_deref())
                .bind(marque.rang.as_deref())
                .fetch_one(&mut **tx)
                .await?;

                // Le livre existe déjà ? Alors l'UPSERT a seulement
                // augmenté la quantité : rien d'autre à créer.
                let book_id: Option<i64> = sqlx::query_scalar(
                    r#"
                    SELECT book_id
                    FROM enchanted_books
                    WHERE stuff_id = ?
                    "#,
                )
                .bind(stuff_id)
                .fetch_optional(&mut **tx)
                .await?;

                if book_id.is_some() {
                    return Ok(());
                }

                let book_id: i64 = sqlx::query_scalar(
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
                .bind(i64::from(*niveau))
                .fetch_one(&mut **tx)
                .await?;

                for (enchantment_id, enchantment_level) in enchants {
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
                    .execute(&mut **tx)
                    .await?;
                }
            }
        }

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
    // GÉNÉRATION D'UN LIVRE ENCHANTÉ (lectures uniquement)
    // ========================================================
    //
    // Toute la génération est faite AVANT la transaction
    // d'écriture. Les niveaux d'enchantement sont tirés en Rust
    // (avant : une requête SQL `random()` par enchantement).

    async fn preparer_livre(
        &self,
        objet_id: i64,
        niveau: u32,
        marque: &Marque,
    ) -> Result<Ecriture, sqlx::Error> {
        // ----------------------------------------------------
        // 1. Catégories disponibles
        // ----------------------------------------------------

        let categories: Vec<String> = sqlx::query_scalar(
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
        // 2. Catégorie ayant assez d'enchantements pour le niveau
        // ----------------------------------------------------

        let mut categorie_selectionnee: Option<String> = None;

        for categorie in &categories {
            let count: i64 = sqlx::query_scalar(
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
                categorie_selectionnee = Some(categorie.clone());
                break;
            }
        }

        // ----------------------------------------------------
        // 3. Catégorie de secours si nécessaire
        // ----------------------------------------------------

        let categorie = categorie_selectionnee
            .or_else(|| categories.first().cloned())
            .ok_or_else(|| {
                sqlx::Error::Protocol(
                    "Impossible de sélectionner une \
                     catégorie d'enchantement"
                        .into(),
                )
            })?;

        // ----------------------------------------------------
        // 4. Sélection des enchantements
        // ----------------------------------------------------

        let enchantements: Vec<GeneratedEnchant> = sqlx::query_as(
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
        // 5. Niveau de chaque enchantement (tirage en Rust)
        // ----------------------------------------------------

        let mut bornes: Vec<(i64, i64)> =
            Vec::with_capacity(enchantements.len());

        for enchantement in &enchantements {
            let maximum = std::cmp::min(
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

            bornes.push((enchantement.enchantment_id, maximum));
        }

        // Le RNG est créé et détruit sans traverser de `.await`.
        let mut enchantement_data: Vec<(i64, i64)> = {
            let mut rng = rand::rng();

            bornes
                .into_iter()
                .map(|(id, maximum)| {
                    (id, rng.random_range(1..=maximum))
                })
                .collect()
        };

        // ----------------------------------------------------
        // 6. Tri : l'ordre ne modifie pas l'identité du livre
        // ----------------------------------------------------

        enchantement_data
            .sort_by_key(|(id, level)| (*id, *level));

        // ----------------------------------------------------
        // 7. stack_key canonique (+ rareté / rank)
        // ----------------------------------------------------

        let contenu = enchantement_data
            .iter()
            .map(|(id, level)| format!("{id}:{level}"))
            .collect::<Vec<_>>()
            .join("|");

        let stack_key = format!(
            "book:{niveau}:{contenu}{}",
            marque.suffixe()
        );

        Ok(Ecriture::Livre {
            objet_id,
            niveau,
            stack_key,
            enchants: enchantement_data,
            marque: marque.clone(),
        })
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
                    format!("Nom de livre invalide : {nom}").into(),
                )
            })?
            .parse::<u32>()
            .map_err(|_| {
                sqlx::Error::Protocol(
                    format!("Niveau de livre invalide : {nom}").into(),
                )
            })?;

        if !(1..=6).contains(&niveau) {
            return Err(sqlx::Error::Protocol(
                format!("Niveau de livre hors limites : {niveau}")
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

        let quantite_i64 = Self::quantite_sqlite(quantite)?;

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
                    quantite_actuelle, quantite
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
        } else if let Some(objet) = self.objets.get_mut(&stuff_id) {
            objet.retirer(quantite);
        }

        Ok(())
    }

    // ========================================================
    // RETRAIT DANS UNE TRANSACTION EXISTANTE
    // (objets de base sans rareté ni rank uniquement)
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

        let quantite_i64 = Self::quantite_sqlite(quantite)?;

        let quantity: Option<i64> = sqlx::query_scalar(
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

        let quantity = quantity.unwrap_or(0);

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
    // (objets de base sans rareté ni rank uniquement)
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

        let quantite_i64 = Self::quantite_sqlite(quantite)?;

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
        let quantity: i64 = sqlx::query_scalar(
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

        u64::try_from(quantity).map_err(|_| {
            sqlx::Error::Protocol(
                format!("Quantité invalide pour {nom}").into(),
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