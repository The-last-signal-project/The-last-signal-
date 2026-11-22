//! Variantes de marché.
//!
//! Une variante est l'identité échangeable d'un exemplaire :
//! objet + rareté + rang + niveau de livre + enchantements.
//!
//! Elle est créée **au moment de l'obtention** de l'objet (voir
//! `stuff_manager`) puis réutilisée par le marché pour apparier les lignes
//! d'achat et de vente. La durabilité n'en fait pas partie : c'est un filtre
//! de la ligne d'achat, pas une identité.
//!
//! - Armes, équipements, livres enchantés et potions ont une variante.
//! - Les objets de base n'en ont pas : ils s'échangent sur l'objet seul.
//! - Les munitions sont des objets de base comme les autres.
//!
//! La signature est canonique : l'ordre dans lequel les enchantements sont
//! fournis n'a aucune importance (ils sont triés par `enchantment_id`).

use sqlx::{Sqlite, SqlitePool, Transaction};

fn erreur(message: impl Into<String>) -> sqlx::Error {
    sqlx::Error::Protocol(message.into())
}

/// Les objets de ce type possèdent des variantes de marché.
/// Tout le reste (minerais, nourriture, matériaux...) est un objet de base.
pub fn type_a_variante(type_objet: &str) -> bool {
    matches!(
        type_objet,
        "armes" | "equipment" | "enchanted_book" | "potion"
    )
}

/// Les armes et équipements portent une fiche `equipment` (durabilité).
pub fn type_a_fiche_equipement(type_objet: &str) -> bool {
    matches!(type_objet, "armes" | "equipment")
}

// ============================================================
// SPÉCIFICATION D'UNE VARIANTE
// ============================================================

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VarianteSpec {
    pub objet_id: i64,
    pub rarete: Option<String>,
    pub rang: Option<String>,
    /// Renseigné uniquement pour les livres enchantés.
    pub book_level: Option<i64>,
    /// (enchantment_id, enchantment_level), dans n'importe quel ordre.
    pub enchantements: Vec<(i64, i64)>,
}

impl VarianteSpec {
    /// Arme, équipement sans enchantement ou potion.
    pub fn simple(
        objet_id: i64,
        rarete: Option<&str>,
        rang: Option<&str>,
    ) -> Self {
        Self {
            objet_id,
            rarete: rarete.map(str::to_string),
            rang: rang.map(str::to_string),
            book_level: None,
            enchantements: Vec::new(),
        }
    }

    /// Livre enchanté : niveau de livre + enchantements, ni rareté ni rang.
    pub fn livre(
        objet_id: i64,
        book_level: i64,
        enchantements: &[(i64, i64)],
    ) -> Self {
        Self {
            objet_id,
            rarete: None,
            rang: None,
            book_level: Some(book_level),
            enchantements: enchantements.to_vec(),
        }
    }

    /// Ajoute des enchantements (équipements enchantés).
    pub fn avec_enchantements(mut self, enchantements: &[(i64, i64)]) -> Self {
        self.enchantements = enchantements.to_vec();
        self
    }

    fn enchantements_tries(&self) -> Vec<(i64, i64)> {
        let mut tries = self.enchantements.clone();
        tries.sort_unstable();
        tries
    }

    /// Signature canonique, unique pour un objet donné.
    pub fn signature(&self) -> String {
        let enchantements = self.enchantements_tries();

        let enchantements = if enchantements.is_empty() {
            "-".to_string()
        } else {
            enchantements
                .iter()
                .map(|(id, niveau)| format!("{id}:{niveau}"))
                .collect::<Vec<_>>()
                .join(",")
        };

        format!(
            "r={};g={};b={};e={}",
            self.rarete.as_deref().unwrap_or("-"),
            self.rang.as_deref().unwrap_or("-"),
            self.book_level
                .map(|niveau| niveau.to_string())
                .unwrap_or_else(|| "-".to_string()),
            enchantements,
        )
    }
}

// ============================================================
// CRÉATION / RECHERCHE
// ============================================================

/// Retourne l'id de la variante, en la créant si elle n'existe pas encore.
///
/// La première requête est une écriture (INSERT ... DO NOTHING) : le verrou
/// d'écriture est pris avant toute lecture, ce qui évite SQLITE_BUSY_SNAPSHOT
/// quand cette fonction ouvre la suite d'une transaction.
pub async fn assurer_variante_tx(
    tx: &mut Transaction<'_, Sqlite>,
    spec: &VarianteSpec,
) -> Result<i64, sqlx::Error> {
    let signature = spec.signature();

    let resultat = sqlx::query(
        r#"
        INSERT INTO variantes_marche (
            objet_id,
            rarete,
            rang,
            book_level,
            signature
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (objet_id, signature) DO NOTHING
        "#,
    )
    .bind(spec.objet_id)
    .bind(spec.rarete.as_deref())
    .bind(spec.rang.as_deref())
    .bind(spec.book_level)
    .bind(&signature)
    .execute(&mut **tx)
    .await?;

    // Variante nouvellement créée : on lui attache ses enchantements.
    if resultat.rows_affected() == 1 {
        let variante_id = resultat.last_insert_rowid();

        for (enchantment_id, niveau) in spec.enchantements_tries() {
            sqlx::query(
                r#"
                INSERT OR IGNORE INTO variante_enchantements (
                    variante_id,
                    enchantment_id,
                    enchantment_level
                )
                VALUES (?, ?, ?)
                "#,
            )
            .bind(variante_id)
            .bind(enchantment_id)
            .bind(niveau)
            .execute(&mut **tx)
            .await?;
        }

        return Ok(variante_id);
    }

    let variante_id: i64 = sqlx::query_scalar(
        r#"
        SELECT variante_id
        FROM variantes_marche
        WHERE objet_id = ?
          AND signature = ?
        "#,
    )
    .bind(spec.objet_id)
    .bind(&signature)
    .fetch_one(&mut **tx)
    .await?;

    Ok(variante_id)
}

/// Variante d'un exemplaire de `stuff`, créée si nécessaire.
///
/// Relit l'exemplaire (rareté, rang, livre, enchantements). Retourne `None`
/// pour les objets de base, qui n'ont pas de variante.
/// Sert à l'obtention (enchantement d'un équipement) et de filet de sécurité
/// au dépôt sur le marché pour les exemplaires antérieurs aux variantes.
pub async fn assurer_variante_pour_stuff_tx(
    tx: &mut Transaction<'_, Sqlite>,
    stuff_id: i64,
) -> Result<Option<i64>, sqlx::Error> {
    let ligne: Option<(i64, String, Option<String>, Option<String>)> =
        sqlx::query_as(
            r#"
            SELECT s.objet_id, o.type, s.rarete, s.rang
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE s.stuff_id = ?
            "#,
        )
        .bind(stuff_id)
        .fetch_optional(&mut **tx)
        .await?;

    let (objet_id, type_objet, rarete, rang) =
        ligne.ok_or(sqlx::Error::RowNotFound)?;

    if !type_a_variante(&type_objet) {
        return Ok(None);
    }

    let spec = match type_objet.as_str() {
        "enchanted_book" => {
            let livre: Option<(i64, i64)> = sqlx::query_as(
                r#"
                SELECT book_id, book_level
                FROM enchanted_books
                WHERE stuff_id = ?
                "#,
            )
            .bind(stuff_id)
            .fetch_optional(&mut **tx)
            .await?;

            let (book_id, book_level) = livre.ok_or_else(|| {
                erreur(format!("Livre incomplet pour stuff_id={stuff_id}"))
            })?;

            let enchantements: Vec<(i64, i64)> = sqlx::query_as(
                r#"
                SELECT enchantment_id, enchantment_level
                FROM book_enchantments
                WHERE book_id = ?
                "#,
            )
            .bind(book_id)
            .fetch_all(&mut **tx)
            .await?;

            VarianteSpec::livre(objet_id, book_level, &enchantements)
        }

        "equipment" | "armes" => {
            let enchantements: Vec<(i64, i64)> = sqlx::query_as(
                r#"
                SELECT ee.enchantment_id, ee.enchantment_level
                FROM equipment eq
                JOIN equipment_enchantments ee
                    ON ee.equipment_id = eq.equipment_id
                WHERE eq.stuff_id = ?
                "#,
            )
            .bind(stuff_id)
            .fetch_all(&mut **tx)
            .await?;

            VarianteSpec::simple(
                objet_id,
                rarete.as_deref(),
                rang.as_deref(),
            )
            .avec_enchantements(&enchantements)
        }

        _ => VarianteSpec::simple(
            objet_id,
            rarete.as_deref(),
            rang.as_deref(),
        ),
    };

    assurer_variante_tx(tx, &spec).await.map(Some)
}

/// Id d'une variante existante (sans la créer).
pub async fn variante_id(
    pool: &SqlitePool,
    spec: &VarianteSpec,
) -> Result<Option<i64>, sqlx::Error> {
    sqlx::query_scalar(
        r#"
        SELECT variante_id
        FROM variantes_marche
        WHERE objet_id = ?
          AND signature = ?
        "#,
    )
    .bind(spec.objet_id)
    .bind(spec.signature())
    .fetch_optional(pool)
    .await
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn la_signature_ignore_l_ordre_des_enchantements() {
        let a = VarianteSpec::livre(7, 3, &[(5, 2), (1, 3), (9, 1)]);
        let b = VarianteSpec::livre(7, 3, &[(9, 1), (5, 2), (1, 3)]);

        assert_eq!(a.signature(), b.signature());
        assert_eq!(a.signature(), "r=-;g=-;b=3;e=1:3,5:2,9:1");
    }

    #[test]
    fn la_signature_distingue_rarete_rang_et_niveau() {
        let base = VarianteSpec::simple(1, None, None);
        let rare = VarianteSpec::simple(1, Some("Rare"), Some("B"));
        let autre_rang = VarianteSpec::simple(1, Some("Rare"), Some("A"));

        assert_eq!(base.signature(), "r=-;g=-;b=-;e=-");
        assert_ne!(base.signature(), rare.signature());
        assert_ne!(rare.signature(), autre_rang.signature());

        let niveau_2 = VarianteSpec::livre(2, 2, &[(1, 1)]);
        let niveau_3 = VarianteSpec::livre(2, 3, &[(1, 1)]);
        assert_ne!(niveau_2.signature(), niveau_3.signature());
    }

    #[test]
    fn les_types_exclus_ou_sans_variante() {
        for type_objet in ["armes", "equipment", "enchanted_book", "potion"] {
            assert!(type_a_variante(type_objet), "{type_objet}");
        }

        for type_objet in ["mineral", "consumable", "material", "basic", "muni"] {
            assert!(!type_a_variante(type_objet), "{type_objet}");
        }

        assert!(type_a_fiche_equipement("armes"));
        assert!(type_a_fiche_equipement("equipment"));
        assert!(!type_a_fiche_equipement("potion"));
    }
}
