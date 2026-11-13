use rand::{Rng,RngExt};
use sqlx::SqlitePool;
use std::collections::{HashMap, HashSet};
use crate::gameplay::dice::jet_de_des;
use log::error;
use crate::gameplay::objets::{Rank, Rarete};

const PA: u32 = 1;
const PO: u32 = PA * 10;
#[allow(dead_code)]
const PP: u32 = PO * 10;
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct Loot {
    pub commun: u32,
    pub peu_commun: u32,
    pub rare: u32,
    pub super_rare: u32,
    pub epique: u32,
    pub legendaire: u32,
    pub mythique: u32,
    pub admin: u32,
    pub militaire: u32,
}
/// Artéfact tiré à l'ouverture d'un coffre, avec sa rareté et son rank.
/// `rarete` / `rank` valent `None` pour les artéfacts admin et militaires.
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct ArtefactTire {
    pub nom: String,
    pub quantite: u32,
    pub rarete: Option<Rarete>,
    pub rank: Option<Rank>,
}

impl std::fmt::Display for ArtefactTire {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} x{}", self.nom, self.quantite)?;
        if let Some(r) = self.rarete {
            write!(f, " [{}", r.label())?;
            if let Some(rank) = self.rank {
                write!(f, " - rank {}", rank.label())?;
            }
            write!(f, "]")?;
        }
        Ok(())
    }
}

/// Contenu complet d'un coffre ouvert.
#[allow(dead_code)]
#[derive(Debug, Clone, Default)]
pub struct ResultatOuverture {
    /// Objets garantis (argent, torches, ...), sans rareté ni rank.
    pub objets: HashMap<String, u32>,
    /// Artéfacts tirés, chacun avec sa rareté et son rank.
    pub artefacts: Vec<ArtefactTire>,
}

impl ResultatOuverture {
    /// Ancien format de `ouvrir` : noms et quantités fusionnés,
    /// sans rareté ni rank. Pratique pour adapter un ancien appelant.
    pub fn en_hashmap(&self) -> HashMap<String, u32> {
        let mut objets = self.objets.clone();
        for artefact in &self.artefacts {
            *objets.entry(artefact.nom.clone()).or_insert(0) += artefact.quantite;
        }
        objets
    }
}

// ============================================================
//  CACHE DE PITY
// ============================================================
//
// Avant : chaque tirage faisait 1 à 2 SELECT par entrée de table, puis
// un INSERT ... ON CONFLICT par entrée (un commit SQLite chacun).
//
// Maintenant : tout le pity du compte est lu UNE fois au début de
// l'ouverture, les tirages se font en mémoire, et seules les lignes
// modifiées sont écrites, dans UNE seule transaction à la fin.
// (Aucune lecture n'a lieu dans la transaction d'écriture : pas de
// risque de SQLITE_BUSY_SNAPSHOT.)

#[derive(Default)]
struct PityCache {
    /// nom d'objet -> objet_id (table objets_dispo)
    objet_ids: HashMap<String, i64>,
    /// (categorie racine, sous-catégorie, objet_id) -> nombre d'échecs
    echecs_objets: HashMap<(String, String, i64), i64>,
    /// (catégorie, sous-catégorie) -> nombre d'échecs
    echecs_sous: HashMap<(String, String), i64>,
    modifies_objets: HashSet<(String, String, i64)>,
    modifies_sous: HashSet<(String, String)>,
}

impl PityCache {
    async fn charger(pool: &SqlitePool, account_id: i64) -> Result<Self, sqlx::Error> {
        let ids: Vec<(String, i64)> =
            sqlx::query_as("SELECT nom, objet_id FROM objets_dispo")
                .fetch_all(pool)
                .await?;

        let objets: Vec<(String, String, i64, i64)> = sqlx::query_as(
            r#"
            SELECT categorie, sous_categorie, objet_id, nombre
            FROM echecs_objets
            WHERE account_id = ?
            "#,
        )
        .bind(account_id)
        .fetch_all(pool)
        .await?;

        let sous: Vec<(String, String, i64)> = sqlx::query_as(
            r#"
            SELECT categorie, sous_categorie, nombre
            FROM echecs_sous_categories
            WHERE account_id = ?
            "#,
        )
        .bind(account_id)
        .fetch_all(pool)
        .await?;

        Ok(Self {
            objet_ids: ids.into_iter().collect(),
            echecs_objets: objets
                .into_iter()
                .map(|(c, sc, id, n)| ((c, sc, id), n))
                .collect(),
            echecs_sous: sous
                .into_iter()
                .map(|(c, sc, n)| ((c, sc), n))
                .collect(),
            modifies_objets: HashSet::new(),
            modifies_sous: HashSet::new(),
        })
    }

    fn objet_id(&self, nom: &str) -> Option<i64> {
        self.objet_ids.get(nom).copied()
    }

    fn echecs_objet(&self, racine: &str, categorie: &str, objet_id: i64) -> i64 {
        self.echecs_objets
            .get(&(racine.to_string(), categorie.to_string(), objet_id))
            .copied()
            .unwrap_or(0)
    }

    fn echecs_sous(&self, categorie: &str, sous_categorie: &str) -> i64 {
        self.echecs_sous
            .get(&(categorie.to_string(), sous_categorie.to_string()))
            .copied()
            .unwrap_or(0)
    }

    /// Obtenu -> reset à 0, sinon +1. N'écrit que si la valeur change.
    fn maj_echecs_objet(&mut self, racine: &str, categorie: &str, objet_id: i64, obtenu: bool) {
        let cle = (racine.to_string(), categorie.to_string(), objet_id);
        let ancien = self.echecs_objets.get(&cle).copied().unwrap_or(0);
        let nouveau = if obtenu { 0 } else { ancien + 1 };

        if nouveau != ancien {
            self.echecs_objets.insert(cle.clone(), nouveau);
            self.modifies_objets.insert(cle);
        }
    }

    fn maj_echecs_sous(&mut self, categorie: &str, sous_categorie: &str, obtenu: bool) {
        let cle = (categorie.to_string(), sous_categorie.to_string());
        let ancien = self.echecs_sous.get(&cle).copied().unwrap_or(0);
        let nouveau = if obtenu { 0 } else { ancien + 1 };

        if nouveau != ancien {
            self.echecs_sous.insert(cle.clone(), nouveau);
            self.modifies_sous.insert(cle);
        }
    }

    /// Écrit toutes les lignes modifiées en une seule transaction.
    async fn sauvegarder(&self, pool: &SqlitePool, account_id: i64) -> Result<(), sqlx::Error> {
        if self.modifies_objets.is_empty() && self.modifies_sous.is_empty() {
            return Ok(());
        }

        let mut tx = pool.begin().await?;

        for cle in &self.modifies_sous {
            let nombre = self.echecs_sous.get(cle).copied().unwrap_or(0);

            sqlx::query(
                r#"
                INSERT INTO echecs_sous_categories (
                    account_id, categorie, sous_categorie, nombre
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT (account_id, categorie, sous_categorie)
                DO UPDATE SET nombre = excluded.nombre
                "#,
            )
            .bind(account_id)
            .bind(&cle.0)
            .bind(&cle.1)
            .bind(nombre)
            .execute(&mut *tx)
            .await?;
        }

        for cle in &self.modifies_objets {
            let nombre = self.echecs_objets.get(cle).copied().unwrap_or(0);

            sqlx::query(
                r#"
                INSERT INTO echecs_objets (
                    account_id, categorie, sous_categorie, objet_id, nombre
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (account_id, categorie, sous_categorie, objet_id)
                DO UPDATE SET nombre = excluded.nombre
                "#,
            )
            .bind(account_id)
            .bind(&cle.0)
            .bind(&cle.1)
            .bind(cle.2)
            .bind(nombre)
            .execute(&mut *tx)
            .await?;
        }

        tx.commit().await?;

        Ok(())
    }
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct Tresor {
    
    pub loot_par_niveau: HashMap<u32, Loot>,

    pub objets_garantis: HashMap<u32, HashMap<String, u32>>,

    pub quantite_objets: HashMap<String, u32>,

    pub seuil_artefact_commun: HashMap<u32, u32>,
    pub seuil_artefact_peu_commun: HashMap<u32, u32>,
    pub seuil_artefact_rare: HashMap<u32, u32>,
    pub seuil_artefact_super_rare: HashMap<u32, u32>,
    pub sous_loot: HashMap<String, HashMap<String, f64>>,
    
    pub sous_loot_livre_normal: HashMap<String, f64>,
    pub sous_loot_livre_admin: HashMap<String, f64>,
    
    pub coeff_loot: f64,
}
#[allow(dead_code)]
impl Tresor {
    pub fn new() -> Self {
        let mut rng = rand::rng();

        // -------------------------------------------------
        // LOOT PAR NIVEAU
        // -------------------------------------------------

        let mut loot_par_niveau = HashMap::new();

        loot_par_niveau.insert(
            1,
            Loot {
                commun: 0,
                peu_commun: 0,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 1,
                militaire: 1,
            },
        );

        loot_par_niveau.insert(
            2,
            Loot {
                commun: 1,
                peu_commun: 0,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 1,
                militaire: 1,
            },
        );

        loot_par_niveau.insert(
            3,
            Loot {
                commun: 1,
                peu_commun: 0,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 1,
                militaire: 1,
            },
        );

        loot_par_niveau.insert(
            4,
            Loot {
                commun: 1,
                peu_commun: 0,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 1,
                militaire: 1,
            },
        );

        loot_par_niveau.insert(
            5,
            Loot {
                commun: 1,
                peu_commun: 0,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 1,
                militaire: 1,
            },
        );
        loot_par_niveau.insert(
            6,
            Loot {
                commun: 2,
                peu_commun: 1,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 2,
                militaire: 2,
            },
        );
        loot_par_niveau.insert(
            7,
            Loot {
                commun: 2,
                peu_commun: 1,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 2,
                militaire: 2,
            },
        );
        loot_par_niveau.insert(
            8,
            Loot {
                commun: 2,
                peu_commun: 1,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 2,
                militaire: 2,
            },
        );
        loot_par_niveau.insert(
            9,
            Loot {
                commun: 2,
                peu_commun: 1,
                rare: 0,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 2,
                militaire: 2,
            },
        );
         loot_par_niveau.insert(
            10,
            Loot {
                commun: 2,
                peu_commun: 2,
                rare: 1,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 2,
                militaire: 2,
            },
        );
        loot_par_niveau.insert(
            11,
            Loot {
                commun: 2,
                peu_commun: 2,
                rare: 1,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 3,
                militaire: 3,
            },
        );
        loot_par_niveau.insert(
            12,
            Loot {
                commun: 3,
                peu_commun: 2,
                rare: 1,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 3,
                militaire: 3,
            },
        );
        loot_par_niveau.insert(
            13,
            Loot {
                commun: 3,
                peu_commun: 2,
                rare: 1,
                super_rare: 0,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 3,
                militaire: 3,
            },
        );
        loot_par_niveau.insert(
            14,
            Loot {
                commun: 3,
                peu_commun: 2,
                rare: 2,
                super_rare: 1,
                epique: 0,
                legendaire: 0,
                mythique: 0,
                admin: 3,
                militaire: 3,
            },
        );

        // -------------------------------------------------
        // OBJETS GARANTIS
        // -------------------------------------------------

        let mut objets_garantis = HashMap::new();

        // Niveau 1
        let mut niveau_1 = HashMap::new();

        niveau_1.insert(
            "argent".to_string(),
            jet_de_des(6, 2) * PA,
        );

        niveau_1.insert("torche".to_string(), 2);
        niveau_1.insert("sac".to_string(), 3);
        niveau_1.insert("épée de bois".to_string(), 3);

        // 1 chance sur 20 : gemme
        if jet_de_des(20, 1) >= 18 {
            niveau_1.insert("gemmes".to_string(), 1);
        }

        // 17 chances sur 20 : pain
        if jet_de_des(20, 1) >= 4 {
            niveau_1.insert(
                "pain".to_string(),
                rng.random_range(3..=5),
            );
        }

        objets_garantis.insert(1, niveau_1);

        // Niveau 2
        let mut niveau_2 = HashMap::new();

        niveau_2.insert(
            "argent".to_string(),
            jet_de_des(6, 4) * PA,
        );

        niveau_2.insert("torche".to_string(), 1);
        niveau_2.insert("sac".to_string(), 2);
        niveau_2.insert("épée de pierre".to_string(), 1);

        if jet_de_des(20, 1) >= 16 {
            niveau_2.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(2, niveau_2);

        // Niveau 3
        let mut niveau_3 = HashMap::new();

        niveau_3.insert(
            "argent".to_string(),
            jet_de_des(6, 1) * 10 * PA,
        );

        niveau_3.insert("torche".to_string(), 2);
        niveau_3.insert("sac".to_string(), 1);
        niveau_3.insert("épée de pierre".to_string(), 1);

        if jet_de_des(20, 1) >= 14 {
            niveau_3.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(3, niveau_3);

        // Niveau 4
        let mut niveau_4 = HashMap::new();

        niveau_4.insert(
            "argent".to_string(),
            jet_de_des(6, 2) * 10 * PA,
        );

        if jet_de_des(20, 1) >= 12 {
            niveau_4.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(4, niveau_4);

        // Niveau 5
        let mut niveau_5 = HashMap::new();

        niveau_5.insert(
            "argent".to_string(),
            jet_de_des(6, 3) * 10 * PA,
        );

        if jet_de_des(20, 1) >= 10 {
            niveau_5.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(5, niveau_5);
        let mut niveau_6 = HashMap::new();

        niveau_6.insert(
            "argent".to_string(),
            jet_de_des(6, 4) * 10 * PA,
        );

        if jet_de_des(20, 1) >= 8 {
            niveau_6.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(6, niveau_6);
        let mut niveau_7 = HashMap::new();

        niveau_7.insert(
            "argent".to_string(),
            jet_de_des(6, 5) * 10 * PA,
        );

        if jet_de_des(20, 1) >= 6 {
            niveau_7.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(7, niveau_7);
        let mut niveau_8 = HashMap::new();

        niveau_8.insert(
            "argent".to_string(),
            jet_de_des(6, 1) * 100 * PA,
        );

        if jet_de_des(20, 1) >= 4 {
            niveau_8.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(8, niveau_8);
        let mut niveau_9 = HashMap::new();

        niveau_9.insert(
            "argent".to_string(),
            jet_de_des(6, 2) * 100 * PA,
        );

        if jet_de_des(20, 1) >= 2 {
            niveau_9.insert("gemmes".to_string(), 1);
        }

        objets_garantis.insert(9, niveau_9);
        let mut niveau_10 = HashMap::new();

        niveau_10.insert(
            "argent".to_string(),
            jet_de_des(6, 3) * 100 * PA,
        );
        niveau_10.insert("gemmes".to_string(), 1);
        
        objets_garantis.insert(10, niveau_10);
        let mut niveau_11 = HashMap::new();

        niveau_11.insert(
            "argent".to_string(),
            jet_de_des(6, 4) * 100 * PA,
        );
        niveau_11.insert("gemmes".to_string(), 1);
        
        objets_garantis.insert(11, niveau_11);
        let mut niveau_12 = HashMap::new();

        niveau_12.insert(
            "argent".to_string(),
            jet_de_des(6, 5) * 100 * PA,
        );
        niveau_12.insert("gemmes".to_string(), 1);
        
        objets_garantis.insert(12, niveau_12);
        let mut niveau_13 = HashMap::new();

        niveau_13.insert(
            "argent".to_string(),
            jet_de_des(6, 1) * 100 * PO,
        );
        niveau_13.insert("gemmes".to_string(), 1);
        
        objets_garantis.insert(13, niveau_13);
        let mut niveau_14 = HashMap::new();

        niveau_14.insert(
            "argent".to_string(),
            jet_de_des(6, 2) * 100 * PO,
        );
        niveau_14.insert("gemmes".to_string(), 1);
        
        objets_garantis.insert(14, niveau_14);

        

        // -------------------------------------------------
        // QUANTITÉS DES OBJETS
        // -------------------------------------------------

        let mut quantite_objets = HashMap::new();

        for objet in [
            "cuivre",
            "fer",
            "lapiz",
            "or",
            "rougite",
            "Re",
            "diam",
            "balles",
            "carreau d'arbalète",
            "flèches communes",
            "flèches peu rares",
            "flèches rares",
            "flèches super rares",
            "flèches exotiques",
            "flèches épiques",
            "flèches légendaires",
        ] {
            quantite_objets.insert(
                objet.to_string(),
                rng.random_range(2..=9),
            );
        }
        let mut sous_loot: HashMap<String, HashMap<String, f64>> =
    HashMap::new();
        sous_loot.insert(
    "Artefact commun".to_string(),
    HashMap::from([
        ("food".to_string(), 80.0),
        ("minerais".to_string(), 19.0),
        ("équi".to_string(), 1.0),
    ]),
);
        sous_loot.insert(
    "Artefact peu commun".to_string(),
    HashMap::from([
        ("food".to_string(), 50.0),
        ("minerais".to_string(), 40.0),
        ("équi".to_string(), 10.0),
    ]),
);
        sous_loot.insert(
    "Artefact rare".to_string(),
    HashMap::from([
        ("minerais".to_string(), 50.0),
        ("équi".to_string(), 25.0),
        ("potion".to_string(), 25.0),
    ]),
);
        sous_loot.insert(
    "food".to_string(),
    HashMap::from([
        ("viande".to_string(), 10.0),
        ("pain".to_string(), 70.0),
        ("fruit et légumes".to_string(), 10.0),
        ("herbes et racines".to_string(), 10.0),
        ("tacos".to_string(), 10.0),
        ("burger".to_string(), 10.0),
        ("sushi".to_string(), 10.0),
        ("boulette de riz".to_string(), 10.0),
        ("sucrerie".to_string(), 10.0),
        
    ]),
);  
        // La liste de viande pourra être extendue
        sous_loot.insert(
    "viande".to_string(),
    HashMap::from([
        ("mouton".to_string(), 10.0),
        ("cerf".to_string(), 3.0),
        ("sanglier".to_string(), 2.0),
        ("pigeon".to_string(), 4.0),
        ("poulet".to_string(), 10.0),
        ("porc".to_string(), 10.0),
        ("boeuf".to_string(), 10.0),
        ("agneau".to_string(), 10.0),
        ("veau".to_string(), 10.0),
        ("karage".to_string(), 10.0),
        ("calamar".to_string(), 10.0),
        ("morue".to_string(), 10.0),
        ("crabe".to_string(), 10.0),
        ("saumon".to_string(), 10.0),
        ("thon".to_string(), 10.0),
        ("fugu".to_string(), 10.0),
        ("poisson globe".to_string(), 10.0),
        ("sashimi".to_string(), 10.0),

        
    ]),
);
        sous_loot.insert(
    "Artefact super rare".to_string(),
    HashMap::from([
        ("potion".to_string(), 50.0),
        ("équi".to_string(), 40.0),
        ("minerais".to_string(), 9.9),
        ("livre enchant".to_string(), 0.1),
    ]),
);
        sous_loot.insert(
    "Artefact epique".to_string(),
    HashMap::from([
        ("potion".to_string(), 15.0),
        ("équi".to_string(), 75.0),
        ("livre enchant".to_string(), 10.0),
        
    ]),
);
        sous_loot.insert(
    "Artefact legendaire".to_string(),
    HashMap::from([
        ("potion".to_string(), 5.0),
        ("équi".to_string(), 75.0),
        ("livre enchant".to_string(), 20.0),
        
    ]),
);
        // À ajuster : table de loot des artéfacts mythiques.
        sous_loot.insert(
    "Artefact mythique".to_string(),
    HashMap::from([
        ("potion".to_string(), 2.0),
        ("équi".to_string(), 78.0),
        ("livre enchant".to_string(), 20.0),
    ]),
);
        sous_loot.insert(
    "Artefact militaire".to_string(),
    HashMap::from([
        ("matos".to_string(), 5.0),
        ("parachute".to_string(), 5.0),
        ("equi".to_string(), 5.0),
        ("ogive".to_string(), 5.0),
        ("combinaison anti g".to_string(), 5.0),
        
        
    ]),
);
        sous_loot.insert(
    "Artefact admin".to_string(),
    HashMap::from([
        ("livre enchant".to_string(), 100.0),
        
    ]),
);
        sous_loot.insert(
    "équi".to_string(),
    HashMap::from([
        ("armes".to_string(), 20.0),
        ("outils".to_string(), 20.0),
        ("armure".to_string(), 20.0),
        ("véhicules".to_string(), 20.0),
        ("batiments".to_string(), 20.0),
        ("combinaisons".to_string(), 3.0),
        
        
        
    ]),
);
sous_loot.insert(
    "armes".to_string(),
    HashMap::from([
        ("armes de contact".to_string(), 20.0),
        ("armes explosives".to_string(), 20.0),
        ("armes à distance".to_string(), 20.0),
        ("armes à feux".to_string(), 20.0),
        ("armes magiques".to_string(), 20.0),
        
        
        
        
    ]),
);
           sous_loot.insert(
    "véhicules".to_string(),
    HashMap::from([
        ("avions".to_string(), 20.0),
        ("bus T2C".to_string(), 20.0),
        ("sous-marin".to_string(), 20.0),
        ("drones".to_string(), 20.0),
        ("voitures".to_string(), 20.0),
        ("tanks".to_string(), 20.0),
        ("bateaux".to_string(), 20.0),
        
        
    ]),
); 

            
        let seuil_artefact_commun: HashMap<u32, u32> = HashMap::from([
    (2, 20),
    (3, 19),
    (4, 17),
    (5, 15),
    (6, 15),
    (7, 14),
    (8, 13),
    (9, 12),
    (10,11),
    (11,10),
    (12,10),
    (13,9),
    (14,8),
]);
        let seuil_artefact_peu_commun: HashMap<u32, u32> = HashMap::from([
    (6, 20),
    (7, 19),
    (8,17),
    (9, 15),
    (10,15),
    (11,14),
    (12,13),
    (13,12),
    (14,11),


]);
        let seuil_artefact_rare: HashMap<u32, u32> = HashMap::from([
    (10, 20),
    (11,19),
    (12,17),
    (13,15),
    (14,15),

]);
let seuil_artefact_super_rare: HashMap<u32, u32> = HashMap::from([
    (14, 20),
    

]);
        let sous_loot_livre_normal = HashMap::from([
    ("livre enchant niv 1".to_string(), 70.0),
    ("livre enchant niv 2".to_string(), 20.0),
    ("livre enchant niv 3".to_string(), 5.0),
    ("livre enchant niv 4".to_string(), 3.0),
    ("livre enchant niv 5".to_string(), 1.5),
    ("livre enchant niv 6".to_string(), 0.5),
]);

let sous_loot_livre_admin = HashMap::from([
    ("livre enchant niv 1".to_string(), 45.0),
    ("livre enchant niv 2".to_string(), 15.0),
    ("livre enchant niv 3".to_string(), 13.0),
    ("livre enchant niv 4".to_string(), 12.0),
    ("livre enchant niv 5".to_string(), 8.0),
    ("livre enchant niv 6".to_string(), 7.0),
]);
        

        Self {
            loot_par_niveau,
            objets_garantis,
            quantite_objets,
            sous_loot,
            seuil_artefact_commun,
            seuil_artefact_peu_commun,
            seuil_artefact_rare,
            seuil_artefact_super_rare,
            sous_loot_livre_normal,
            sous_loot_livre_admin,
            coeff_loot: 1.0,
        
        }
    }
    
    /// Ouvre un coffre : chaque artéfact reçoit sa rareté (celle de la
    /// catégorie dans laquelle il a été tiré) et un rank de G à SSS.
    ///
    /// Accès base de données : 3 lectures au début (uniquement s'il y a au
    /// moins un artéfact à tirer) + 1 transaction d'écriture à la fin.
    pub async fn ouvrir(
        &mut self,
        pool: &SqlitePool,
        account_id: i64,
        niveau: u32,
        is_admin: bool,
        is_militaire: bool,
        coeff_loot: Option<f64>,
    ) -> Result<ResultatOuverture, sqlx::Error> {
        // Mise à jour du coefficient de loot avec valeur par défaut 1.0
        self.coeff_loot = coeff_loot.unwrap_or(1.0);

        let loot = self
            .loot_par_niveau
            .get(&niveau)
            .cloned()
            .expect("Niveau de coffre invalide");

        let mut resultat = ResultatOuverture::default();

        // ==========================================
        // OBJETS GARANTIS
        // ==========================================

        if let Some(garantis) = self.objets_garantis.get(&niveau) {
            for (objet, quantite) in garantis {
                *resultat.objets.entry(objet.clone()).or_insert(0) += *quantite;
            }
        }

        // ==========================================
        // PHASE 1 : JETS DE DÉS (aucun accès base)
        //
        // On détermine d'abord combien de tirages réussissent, pour ne
        // toucher à la base que s'il y en a au moins un.
        // Il n'existe pas de seuil épique/légendaire : 20 par défaut.
        // ==========================================

        let tirages: Vec<(&'static str, Option<Rarete>)> = {
            let mut rng = rand::rng();
            let mut tirages = Vec::new();

            let categories = [
                (
                    loot.commun,
                    self.seuil_artefact_commun.get(&niveau).copied().unwrap_or(20),
                    "Artefact commun",
                    Rarete::Commun,
                ),
                (
                    loot.peu_commun,
                    self.seuil_artefact_peu_commun.get(&niveau).copied().unwrap_or(20),
                    "Artefact peu commun",
                    Rarete::PeuCommun,
                ),
                (
                    loot.rare,
                    self.seuil_artefact_rare.get(&niveau).copied().unwrap_or(20),
                    "Artefact rare",
                    Rarete::Rare,
                ),
                (
                    loot.super_rare,
                    self.seuil_artefact_super_rare.get(&niveau).copied().unwrap_or(20),
                    "Artefact super rare",
                    Rarete::SuperRare,
                ),
                (loot.epique, 20, "Artefact epique", Rarete::Epique),
                (loot.legendaire, 20, "Artefact legendaire", Rarete::Legendaire),
                (loot.mythique, 20, "Artefact mythique", Rarete::Mythique),
            ];

            for (nombre, seuil, categorie, rarete) in categories {
                // Application du coefficient au seuil
                let seuil_ajuste =
                    (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;

                for _ in 0..nombre {
                    let jet = rng.random_range(1..=20);

                    if jet >= seuil_ajuste {
                        tirages.push((categorie, Some(rarete)));
                    }
                }
            }

            // Loot admin / militaire : pas de jet, pas de rareté ni de rank
            if is_admin {
                for _ in 0..loot.admin {
                    tirages.push(("Artefact admin", None));
                }
            }

            if is_admin || is_militaire {
                for _ in 0..loot.militaire {
                    tirages.push(("Artefact militaire", None));
                }
            }

            tirages
        };

        if tirages.is_empty() {
            return Ok(resultat);
        }

        // ==========================================
        // PHASE 2 : LECTURE UNIQUE DU PITY DU COMPTE
        // ==========================================

        let mut cache = PityCache::charger(pool, account_id).await?;

        // ==========================================
        // PHASE 3 : TIRAGES EN MÉMOIRE
        // ==========================================

        {
            let mut rng = rand::rng();

            resultat.artefacts.reserve(tirages.len());

            for (categorie, rarete) in tirages {
                let nom = self.tirer_objet_cache(&mut cache, categorie, &mut rng, is_admin);
                let quantite = self.quantite_objets.get(&nom).copied().unwrap_or(1);
                let rank = rarete.map(|r| Rank::tirer(r, &mut rng));

                resultat.artefacts.push(ArtefactTire {
                    nom,
                    quantite,
                    rarete,
                    rank,
                });
            }
        }

        // ==========================================
        // PHASE 4 : ÉCRITURE UNIQUE DU PITY
        // ==========================================

        cache.sauvegarder(pool, account_id).await?;

        Ok(resultat)
    }

    /// Tirage pondéré sur un slice (sans allocation de HashMap).
    fn tirer_pondere_slice<'a>(
        table: &[(&'a str, f64)],
        rng: &mut impl Rng,
    ) -> &'a str {
        let total: f64 = table.iter().map(|(_, p)| *p).sum();

        if total <= 0.0 {
            panic!("Table de loot vide");
        }

        let tirage = rng.random_range(0.0..total);

        let mut cumul = 0.0;

        for (nom, poids) in table {
            cumul += *poids;

            if tirage < cumul {
                return *nom;
            }
        }

        // Filet de sécurité contre les erreurs d'arrondi flottant.
        table[table.len() - 1].0
    }

    /// Version publique conservée pour compatibilité.
    pub fn tirer_pondere(
        table: &HashMap<String, f64>,
        rng: &mut impl Rng,
    ) -> String {
        let poids: Vec<(&str, f64)> =
            table.iter().map(|(n, p)| (n.as_str(), *p)).collect();

        Self::tirer_pondere_slice(&poids, rng).to_string()
    }

    /// Tirage d'un objet dans une catégorie, entièrement en mémoire.
    /// Le pity est lu et mis à jour dans `cache` (écrit plus tard).
    fn tirer_objet_cache(
        &self,
        cache: &mut PityCache,
        categorie: &str,
        rng: &mut impl Rng,
        is_admin: bool,
    ) -> String {
        // Catégorie principale du tirage. Exemple : "Artefact rare"
        let categorie_racine = categorie;

        // Catégorie actuellement parcourue.
        // Elle change lorsqu'on descend dans les sous-catégories.
        let mut categorie_actuelle = categorie.to_string();

        loop {
            let table = self
                .sous_loot
                .get(&categorie_actuelle)
                .unwrap_or_else(|| {
                    panic!("Catégorie de loot inconnue : {:?}", categorie_actuelle);
                });

            let total: f64 = table.values().sum();

            if total <= 0.0 {
                panic!("Table de loot vide");
            }

            // ======================================
            // CALCUL DES POIDS AVEC PITY
            //
            // Le pity s'applique uniquement aux résultats ayant une
            // probabilité originale < 3 %. Chaque échec ajoute +7,5 %
            // du poids original. Le coefficient de loot est appliqué.
            // ======================================

            let mut poids_ajustes: Vec<(&str, f64)> = Vec::with_capacity(table.len());

            for (nom, poids) in table {
                let probabilite = poids / total;

                let echecs = if self.sous_loot.contains_key(nom) {
                    cache.echecs_sous(&categorie_actuelle, nom)
                } else {
                    match cache.objet_id(nom) {
                        Some(objet_id) => {
                            cache.echecs_objet(categorie_racine, &categorie_actuelle, objet_id)
                        }
                        // Objet absent de objets_dispo : pas encore de pity.
                        None => 0,
                    }
                };

                let poids_ajuste = if probabilite < 0.03 {
                    *poids * self.coeff_loot * (1.0 + 0.075 * echecs as f64)
                } else {
                    *poids * self.coeff_loot
                };

                poids_ajustes.push((nom.as_str(), poids_ajuste));
            }

            // ======================================
            // TIRAGE
            // ======================================

            let resultat: String =
                Self::tirer_pondere_slice(&poids_ajustes, rng).to_string();

            let resultat_est_sous_categorie = self.sous_loot.contains_key(&resultat);

            // ======================================
            // MISE À JOUR DU PITY (en mémoire)
            // ======================================

            for (nom, poids) in table {
                // Pas de pity pour les probabilités >= 3 %.
                if poids / total >= 0.03 {
                    continue;
                }

                let obtenu = nom == &resultat;

                if self.sous_loot.contains_key(nom) {
                    cache.maj_echecs_sous(&categorie_actuelle, nom, obtenu);
                } else if let Some(objet_id) = cache.objet_id(nom) {
                    // Si l'objet n'existe pas dans objets_dispo, on ne
                    // peut pas enregistrer son pity.
                    cache.maj_echecs_objet(
                        categorie_racine,
                        &categorie_actuelle,
                        objet_id,
                        obtenu,
                    );
                }
            }

            // ======================================
            // LIVRE ENCHANTÉ
            // ======================================

            if resultat == "livre enchant" {
                return self.tirer_livre_cache(cache, rng, is_admin);
            }

            // ======================================
            // DESCENTE DANS UNE SOUS-CATÉGORIE
            // ======================================

            if resultat_est_sous_categorie {
                categorie_actuelle = resultat;
                continue;
            }

            // ======================================
            // OBJET FINAL
            // ======================================

            return resultat;
        }
    }

    /// Tirage d'un livre enchanté, entièrement en mémoire.
    fn tirer_livre_cache(
        &self,
        cache: &mut PityCache,
        rng: &mut impl Rng,
        is_admin: bool,
    ) -> String {
        let categorie = if is_admin {
            "livre enchant admin"
        } else {
            "livre enchant normal"
        };

        let table = if is_admin {
            &self.sous_loot_livre_admin
        } else {
            &self.sous_loot_livre_normal
        };

        let total: f64 = table.values().sum();

        if total <= 0.0 {
            panic!("Table de loot des livres vide");
        }

        let mut poids_ajustes: Vec<(&str, f64)> = Vec::with_capacity(table.len());

        for (objet, poids) in table {
            let probabilite = poids / total;

            let echecs = match cache.objet_id(objet) {
                Some(objet_id) => cache.echecs_objet(categorie, categorie, objet_id),
                None => {
                    error!("Livre absent de objets_dispo : {:?}", objet);
                    0
                }
            };

            let poids_ajuste = if probabilite < 0.03 {
                *poids * self.coeff_loot * (1.0 + 0.075 * echecs as f64)
            } else {
                *poids * self.coeff_loot
            };

            poids_ajustes.push((objet.as_str(), poids_ajuste));
        }

        let resultat: String = Self::tirer_pondere_slice(&poids_ajustes, rng).to_string();

        for (objet, poids) in table {
            if poids / total >= 0.03 {
                continue;
            }

            let Some(objet_id) = cache.objet_id(objet) else {
                error!(
                    "Impossible de mettre à jour la pity : \
                     livre absent de objets_dispo : {:?}",
                    objet
                );
                continue;
            };

            cache.maj_echecs_objet(categorie, categorie, objet_id, objet == &resultat);
        }

        resultat
    }

    /// Tire un objet dans une catégorie (API publique conservée).
    /// Pour plusieurs tirages, préfère `ouvrir` qui ne fait qu'une
    /// lecture et qu'une écriture pour tout le coffre.
    pub async fn tirer_objet(
        &mut self,
        pool: &SqlitePool,
        account_id: i64,
        categorie: &str,
        rng: &mut impl Rng,
        is_admin: bool,
    ) -> Result<String, sqlx::Error> {
        let mut cache = PityCache::charger(pool, account_id).await?;
        let resultat = self.tirer_objet_cache(&mut cache, categorie, rng, is_admin);
        cache.sauvegarder(pool, account_id).await?;
        Ok(resultat)
    }

    /// Tire un livre enchanté (API publique conservée).
    pub async fn tirer_livre(
        &mut self,
        pool: &SqlitePool,
        account_id: i64,
        rng: &mut impl Rng,
        is_admin: bool,
    ) -> Result<String, sqlx::Error> {
        let mut cache = PityCache::charger(pool, account_id).await?;
        let resultat = self.tirer_livre_cache(&mut cache, rng, is_admin);
        cache.sauvegarder(pool, account_id).await?;
        Ok(resultat)
    }
}
