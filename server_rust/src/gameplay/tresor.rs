use rand::{Rng,RngExt};
use sqlx::SqlitePool;
use std::collections::HashMap;
use crate::gameplay::dice::jet_de_des;
use log::{debug, error, info};

const PA: u32 = 1;
const PO: u32 = PA * 10;
const PP: u32 = PO * 10;

#[derive(Debug, Clone)]
pub struct Loot {
    pub commun: u32,
    pub peu_commun: u32,
    pub rare: u32,
    pub super_rare: u32,
    pub epique: u32,
    pub legendaire: u32,
    pub admin: u32,
    pub militaire: u32,
}

#[derive(Debug, Clone)]
pub struct Tresor {
    
    pub loot_par_niveau: HashMap<u32, Loot>,

    pub objets_garantis: HashMap<u32, HashMap<String, u32>>,

    pub quantite_objets: HashMap<String, u32>,

    pub seuil_artefact_commun: HashMap<u32, u32>,
    pub seuil_artefact_peu_commun: HashMap<u32, u32>,
    pub seuil_artefact_rare: HashMap<u32, u32>,
    pub sous_loot: HashMap<String, HashMap<String, f64>>,
    
    pub sous_loot_livre_normal: HashMap<String, f64>,
    pub sous_loot_livre_admin: HashMap<String, f64>,
    
    pub coeff_loot: f64,
}

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
]);
        let seuil_artefact_peu_commun: HashMap<u32, u32> = HashMap::from([
    (6, 20),
    (7, 19),
    (8,17),
    (9, 15),
    (10,15),
    (11,14),
    (12,13),

]);
        let seuil_artefact_rare: HashMap<u32, u32> = HashMap::from([
    (10, 20),
    (11,19),
    (12,17),
    

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
            sous_loot_livre_normal,
            sous_loot_livre_admin,
            coeff_loot: 1.0,
        
        }
    }
    
      pub async fn ouvrir(
    &mut self,
    pool: &SqlitePool,
    account_id: i64,
    niveau: u32,
    is_admin: bool,
    is_militaire: bool,
    coeff_loot: Option<f64>,
) -> Result<HashMap<String, u32>, sqlx::Error> {
    // Mise à jour du coefficient de loot avec valeur par défaut 1.0
    self.coeff_loot = coeff_loot.unwrap_or(1.0);
    
    let mut rng = rand::rng();

    let loot = self
        .loot_par_niveau
        .get(&niveau)
        .cloned()
        .expect("Niveau de coffre invalide");

    let mut objets = HashMap::new();

    // ==========================================
    // OBJETS GARANTIS
    // ==========================================

    if let Some(garantis) = self.objets_garantis.get(&niveau) {
        for (objet, quantite) in garantis {
            *objets.entry(objet.clone()).or_insert(0) += *quantite;
        }
    }

    // ==========================================
    // OBJETS COMMUNS
    // ==========================================

    for _ in 0..loot.commun {
        let seuil = self
            .seuil_artefact_commun
            .get(&niveau)
            .copied()
            .unwrap_or(20);

        // Application du coefficient au seuil
        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
        let jet = rng.random_range(1..=20);

        if jet >= seuil_ajuste {
            let objet = self
                .tirer_objet(
                    pool,
                    account_id,
                    "Artefact commun",
                    &mut rng,
                    is_admin,
                    
                )
                .await?;

            let quantite = self
                .quantite_objets
                .get(&objet)
                .copied()
                .unwrap_or(1);

            *objets.entry(objet).or_insert(0) += quantite;
        }
    }
          for _ in 0..loot.peu_commun {
        let seuil = self
            .seuil_artefact_peu_commun
            .get(&niveau)
            .copied()
            .unwrap_or(20);

        // Application du coefficient au seuil
        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
        let jet = rng.random_range(1..=20);

        if jet >= seuil_ajuste {
            let objet = self
                .tirer_objet(
                    pool,
                    account_id,
                    "Artefact peu commun",
                    &mut rng,
                    is_admin,
                    
                )
                .await?;

            let quantite = self
                .quantite_objets
                .get(&objet)
                .copied()
                .unwrap_or(1);

            *objets.entry(objet).or_insert(0) += quantite;
        }
          }
          for _ in 0..loot.rare {
        let seuil = self
            .seuil_artefact_rare
            .get(&niveau)
            .copied()
            .unwrap_or(20);

        // Application du coefficient au seuil
        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
        let jet = rng.random_range(1..=20);

        if jet >= seuil_ajuste {
            let objet = self
                .tirer_objet(
                    pool,
                    account_id,
                    "Artefact rare",
                    &mut rng,
                    is_admin,
                    
                )
                .await?;

            let quantite = self
                .quantite_objets
                .get(&objet)
                .copied()
                .unwrap_or(1);

            *objets.entry(objet).or_insert(0) += quantite;
        }
          }

    // ==========================================
    // LOOT ADMIN
    // ==========================================

    if is_admin {
        for _ in 0..loot.admin {
            let objet = self
                .tirer_objet(
                    pool,
                    account_id,
                    "Artefact admin",
                    &mut rng,
                    is_admin,
                    
                )
                .await?;

            let quantite = self
                .quantite_objets
                .get(&objet)
                .copied()
                .unwrap_or(1);

            *objets.entry(objet).or_insert(0) += quantite;
        }
    }
          if is_admin || is_militaire {
        for _ in 0..loot.militaire {
            let objet = self
                .tirer_objet(
                    pool,
                    account_id,
                    "Artefact militaire",
                    &mut rng,
                    is_admin,
                    
                )
                .await?;

            let quantite = self
                .quantite_objets
                .get(&objet)
                .copied()
                .unwrap_or(1);

            *objets.entry(objet).or_insert(0) += quantite;
        }
          }

    Ok(objets)
                }  
            
        
            

        

            
    

            
        pub fn tirer_pondere(
    table: &HashMap<String, f64>,
    rng: &mut impl Rng,
) -> String {
    let total: f64 = table.values().sum();

    if total <= 0.0 {
        panic!("Table de loot vide");
    }

    let tirage = rng.random_range(0.0..total);

    let mut cumul = 0.0;

    for (objet, poids) in table {
        cumul += poids;

        if tirage < cumul {
            return objet.clone();
        }
    }

    unreachable!("Le tirage n'a trouvé aucun résultat")
}

    
    pub async fn tirer_objet(
    &mut self,
    pool: &SqlitePool,
    account_id: i64,
    categorie: &str,
    rng: &mut impl Rng,
    is_admin: bool,
) -> Result<String, sqlx::Error> {

    // Catégorie principale du tirage.
    // Exemple : "Artefact rare"
    let categorie_racine = categorie.to_string();

    // Catégorie actuellement parcourue.
    // Elle change lorsqu'on descend dans les sous-catégories.
    let mut categorie_actuelle = categorie.to_string();

    loop {
        // ==========================================
        // RÉCUPÉRATION DE LA TABLE ACTUELLE
        // ==========================================

        let table_originale = self
            .sous_loot
            .get(&categorie_actuelle)
            .cloned()
            .unwrap_or_else(|| {
                panic!(
                    "Catégorie de loot inconnue : {:?}",
                    categorie_actuelle
                );
            });

        let total: f64 = table_originale.values().sum();

        if total <= 0.0 {
            panic!("Table de loot vide");
        }

        // ==========================================
        // CALCUL DES POIDS AVEC PITY
        // ==========================================

        let mut table_ajustee = HashMap::new();

        for (nom, poids) in &table_originale {

            let probabilite = poids / total;

            // Est-ce que cette entrée est une
            // sous-catégorie ?
            let est_sous_categorie =
                self.sous_loot.contains_key(nom);

            let echecs: i64;

            if est_sous_categorie {

                // ==================================
                // PITY SOUS-CATÉGORIE
                // ==================================

                echecs = sqlx::query_scalar(
                    r#"
                    SELECT nombre
                    FROM echecs_sous_categories
                    WHERE account_id = ?
                      AND categorie = ?
                      AND sous_categorie = ?
                    "#,
                )
                .bind(account_id)
                .bind(&categorie_actuelle)
                .bind(nom)
                .fetch_optional(pool)
                .await?
                .unwrap_or(0);

            } else {

                // ==================================
                // PITY OBJET
                // ==================================

                let objet_id: Option<i64> = sqlx::query_scalar(
                    r#"
                    SELECT objet_id
                    FROM objets_dispo
                    WHERE nom = ?
                    "#,
                )
                .bind(nom)
                .fetch_optional(pool)
                .await?;

                // Si l'objet n'existe pas encore dans
                // objets_dispo, il n'a simplement pas
                // encore de pity.
                echecs = match objet_id {
                    Some(objet_id) => {
                        sqlx::query_scalar(
                            r#"
                            SELECT nombre
                            FROM echecs_objets
                            WHERE account_id = ?
                              AND categorie = ?
                              AND sous_categorie = ?
                              AND objet_id = ?
                            "#,
                        )
                        .bind(account_id)
                        .bind(&categorie_racine)
                        .bind(&categorie_actuelle)
                        .bind(objet_id)
                        .fetch_optional(pool)
                        .await?
                        .unwrap_or(0)
                    }

                    None => 0,
                };
            }

            // ==================================
            // APPLICATION DU PITY
            // ==================================

            /*
             * Le pity s'applique uniquement aux
             * résultats ayant une probabilité
             * originale strictement inférieure à 3 %.
             *
             * Chaque échec ajoute +7,5 % du poids
             * original.
             *
             * Le coefficient de loot est également
             * appliqué.
             */

            let poids_ajuste = if probabilite < 0.03 {
                *poids
                    * self.coeff_loot
                    * (1.0 + 0.075 * echecs as f64)
            } else {
                *poids * self.coeff_loot
            };

            table_ajustee.insert(
                nom.clone(),
                poids_ajuste,
            );
        }

        // ==========================================
        // TIRAGE
        // ==========================================

        let resultat = Self::tirer_pondere(
            &table_ajustee,
            rng,
        );

        // ==========================================
        // LE RÉSULTAT EST-IL UNE SOUS-CATÉGORIE ?
        // ==========================================

        let resultat_est_sous_categorie =
            self.sous_loot.contains_key(&resultat);

        // ==========================================
        // MISE À JOUR DU PITY
        // ==========================================

        for (nom, poids) in &table_originale {

            let probabilite = poids / total;

            // Pas de pity pour les probabilités >= 3 %.
            if probabilite >= 0.03 {
                continue;
            }

            // ======================================
            // SOUS-CATÉGORIE
            // ======================================

            if self.sous_loot.contains_key(nom) {

                if nom == &resultat {

                    // ------------------------------
                    // SOUS-CATÉGORIE OBTENUE
                    // → RESET
                    // ------------------------------

                    sqlx::query(
                        r#"
                        INSERT INTO echecs_sous_categories (
                            account_id,
                            categorie,
                            sous_categorie,
                            nombre
                        )
                        VALUES (?, ?, ?, 0)

                        ON CONFLICT (
                            account_id,
                            categorie,
                            sous_categorie
                        )
                        DO UPDATE SET
                            nombre = 0
                        "#,
                    )
                    .bind(account_id)
                    .bind(&categorie_actuelle)
                    .bind(nom)
                    .execute(pool)
                    .await?;

                } else {

                    // ------------------------------
                    // SOUS-CATÉGORIE NON OBTENUE
                    // → +1 ÉCHEC
                    // ------------------------------

                    sqlx::query(
                        r#"
                        INSERT INTO echecs_sous_categories (
                            account_id,
                            categorie,
                            sous_categorie,
                            nombre
                        )
                        VALUES (?, ?, ?, 1)

                        ON CONFLICT (
                            account_id,
                            categorie,
                            sous_categorie
                        )
                        DO UPDATE SET
                            nombre = nombre + 1
                        "#,
                    )
                    .bind(account_id)
                    .bind(&categorie_actuelle)
                    .bind(nom)
                    .execute(pool)
                    .await?;
                }

            // ======================================
            // OBJET FINAL
            // ======================================

            } else {

                let objet_id: Option<i64> = sqlx::query_scalar(
                    r#"
                    SELECT objet_id
                    FROM objets_dispo
                    WHERE nom = ?
                    "#,
                )
                .bind(nom)
                .fetch_optional(pool)
                .await?;

                // Si l'objet n'existe pas dans
                // objets_dispo, on ne peut pas
                // enregistrer son pity.
                let Some(objet_id) = objet_id else {
                    continue;
                };

                if nom == &resultat {

                    // ------------------------------
                    // OBJET OBTENU
                    // → RESET
                    // ------------------------------

                    sqlx::query(
                        r#"
                        INSERT INTO echecs_objets (
                            account_id,
                            categorie,
                            sous_categorie,
                            objet_id,
                            nombre
                        )
                        VALUES (?, ?, ?, ?, 0)

                        ON CONFLICT (
                            account_id,
                            categorie,
                            sous_categorie,
                            objet_id
                        )
                        DO UPDATE SET
                            nombre = 0
                        "#,
                    )
                    .bind(account_id)
                    .bind(&categorie_racine)
                    .bind(&categorie_actuelle)
                    .bind(objet_id)
                    .execute(pool)
                    .await?;

                } else {

                    // ------------------------------
                    // OBJET NON OBTENU
                    // → +1 ÉCHEC
                    // ------------------------------

                    sqlx::query(
                        r#"
                        INSERT INTO echecs_objets (
                            account_id,
                            categorie,
                            sous_categorie,
                            objet_id,
                            nombre
                        )
                        VALUES (?, ?, ?, ?, 1)

                        ON CONFLICT (
                            account_id,
                            categorie,
                            sous_categorie,
                            objet_id
                        )
                        DO UPDATE SET
                            nombre = nombre + 1
                        "#,
                    )
                    .bind(account_id)
                    .bind(&categorie_racine)
                    .bind(&categorie_actuelle)
                    .bind(objet_id)
                    .execute(pool)
                    .await?;
                }
            }
        }

        // ==========================================
        // LIVRE ENCHANTÉ
        // ==========================================

        if resultat == "livre enchant" {
            return self
                .tirer_livre(
                    pool,
                    account_id,
                    rng,
                    is_admin,
                )
                .await;
        }

        // ==========================================
        // DESCENTE DANS UNE SOUS-CATÉGORIE
        // ==========================================

        if resultat_est_sous_categorie {
            categorie_actuelle = resultat;
            continue;
        }

        // ==========================================
        // OBJET FINAL
        // ==========================================

        return Ok(resultat);
    }
}
    pub async fn tirer_livre(
    &mut self,
    pool: &SqlitePool,
    account_id: i64,
    rng: &mut impl Rng,
    is_admin: bool,
) -> Result<String, sqlx::Error> {
    let categorie = if is_admin {
        "livre enchant admin"
    } else {
        "livre enchant normal"
    };

    let table_originale = if is_admin {
        self.sous_loot_livre_admin.clone()
    } else {
        self.sous_loot_livre_normal.clone()
    };

    let total: f64 = table_originale.values().sum();

    if total <= 0.0 {
        panic!("Table de loot des livres vide");
    }

    // ==========================================
    // CALCUL DES POIDS AVEC PITY
    // ==========================================

    let mut table_ajustee = HashMap::new();

    for (objet, poids) in &table_originale {
        let probabilite = poids / total;

        let objet_id: Option<i64> = sqlx::query_scalar(
            r#"
            SELECT objet_id
            FROM objets_dispo
            WHERE nom = ?
            "#,
        )
        .bind(objet)
        .fetch_optional(pool)
        .await?;

        let echecs = match objet_id {
            Some(objet_id) => {
                sqlx::query_scalar(
                    r#"
                    SELECT nombre
                    FROM echecs_objets
                    WHERE account_id = ?
                      AND categorie = ?
                      AND sous_categorie = ?
                      AND objet_id = ?
                    "#,
                )
                .bind(account_id)
                .bind(categorie)
                .bind(categorie)
                .bind(objet_id)
                .fetch_optional(pool)
                .await?
                .unwrap_or(0)
            }

            None => {
                error!(
                    "Livre absent de objets_dispo : {:?}",
                    objet
                );

                0
            }
        };

        let poids_ajuste = if probabilite < 0.03 {
            *poids
                * self.coeff_loot
                * (1.0 + 0.075 * echecs as f64)
        } else {
            *poids * self.coeff_loot
        };

        table_ajustee.insert(
            objet.clone(),
            poids_ajuste,
        );
    }

    // ==========================================
    // TIRAGE
    // ==========================================

    let resultat = Self::tirer_pondere(
        &table_ajustee,
        rng,
    );

    // ==========================================
    // MISE À JOUR DES ÉCHECS
    // ==========================================

    for (objet, poids) in &table_originale {
        let probabilite = poids / total;

        if probabilite >= 0.03 {
            continue;
        }

        let objet_id: Option<i64> = sqlx::query_scalar(
            r#"
            SELECT objet_id
            FROM objets_dispo
            WHERE nom = ?
            "#,
        )
        .bind(objet)
        .fetch_optional(pool)
        .await?;

        let Some(objet_id) = objet_id else {
            error!(
                "Impossible de mettre à jour la pity : \
                 livre absent de objets_dispo : {:?}",
                objet
            );
            continue;
        };

        if objet == &resultat {
            // ==================================
            // OBTENU → RESET
            // ==================================

            sqlx::query(
                r#"
                INSERT INTO echecs_objets (
                    account_id,
                    categorie,
                    sous_categorie,
                    objet_id,
                    nombre
                )
                VALUES (?, ?, ?, ?, 0)

                ON CONFLICT (
                    account_id,
                    categorie,
                    sous_categorie,
                    objet_id
                )
                DO UPDATE SET
                    nombre = 0
                "#,
            )
            .bind(account_id)
            .bind(categorie)
            .bind(categorie)
            .bind(objet_id)
            .execute(pool)
            .await?;

        } else {
            // ==================================
            // PAS OBTENU → +1
            // ==================================

            sqlx::query(
                r#"
                INSERT INTO echecs_objets (
                    account_id,
                    categorie,
                    sous_categorie,
                    objet_id,
                    nombre
                )
                VALUES (?, ?, ?, ?, 1)

                ON CONFLICT (
                    account_id,
                    categorie,
                    sous_categorie,
                    objet_id
                )
                DO UPDATE SET
                    nombre = nombre + 1
                "#,
            )
            .bind(account_id)
            .bind(categorie)
            .bind(categorie)
            .bind(objet_id)
            .execute(pool)
            .await?;
        }
    }

    Ok(resultat)
}
}
   


