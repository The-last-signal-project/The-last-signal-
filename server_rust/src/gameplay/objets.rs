use serde::{Deserialize, Serialize};
use rand::{Rng, RngExt};
use std::collections::HashMap;

// Enum pour les types d'objets
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum TypeObjet {
    DeBase,
    Equipement,
    Arme,
    Potion,
    Livre,
}

// ============================================================
// RARETÉ ET RANK
// ============================================================

/// Rareté d'un artéfact (celle de la catégorie dans laquelle il est tiré).
#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Rarete {
    Commun,
    PeuCommun,
    Rare,
    SuperRare,
    Epique,
    Legendaire,
    Mythique,
}

impl Rarete {
    pub fn label(self) -> &'static str {
        match self {
            Rarete::Commun => "Commun",
            Rarete::PeuCommun => "Peu commun",
            Rarete::Rare => "Rare",
            Rarete::SuperRare => "Super rare",
            Rarete::Epique => "Épique",
            Rarete::Legendaire => "Légendaire",
            Rarete::Mythique => "Mythique",
        }
    }

    /// Multiplicateur de stats lié à la rareté (à ajuster à ta convenance).
    /// Il se combine avec celui du rank : stat = base x rank x rareté.
    pub fn multiplicateur(self) -> f64 {
        match self {
            Rarete::Commun => 1.0,
            Rarete::PeuCommun => 1.1,
            Rarete::Rare => 1.25,
            Rarete::SuperRare => 1.5,
            Rarete::Epique => 1.75,
            Rarete::Legendaire => 2.0,
            Rarete::Mythique => 2.5,
        }
    }

    pub fn depuis_label(label: &str) -> Option<Self> {
        [
            Rarete::Commun,
            Rarete::PeuCommun,
            Rarete::Rare,
            Rarete::SuperRare,
            Rarete::Epique,
            Rarete::Legendaire,
            Rarete::Mythique,
        ]
        .into_iter()
        .find(|r| r.label() == label)
    }
}

/// Rank d'un objet, du plus faible (G) au plus fort (SSS).
#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Rank {
    G,
    F,
    E,
    D,
    C,
    B,
    A,
    S,
    SS,
    SSS,
}

impl Rank {
    pub const TOUS: [Rank; 10] = [
        Rank::G,
        Rank::F,
        Rank::E,
        Rank::D,
        Rank::C,
        Rank::B,
        Rank::A,
        Rank::S,
        Rank::SS,
        Rank::SSS,
    ];

    pub fn label(self) -> &'static str {
        match self {
            Rank::G => "G",
            Rank::F => "F",
            Rank::E => "E",
            Rank::D => "D",
            Rank::C => "C",
            Rank::B => "B",
            Rank::A => "A",
            Rank::S => "S",
            Rank::SS => "SS",
            Rank::SSS => "SSS",
        }
    }

    pub fn depuis_label(label: &str) -> Option<Self> {
        Self::TOUS.into_iter().find(|r| r.label() == label)
    }

    /// Multiplicateur de stats (à ajuster à ta convenance).
    pub fn multiplicateur(self) -> f64 {
        match self {
            Rank::G => 0.6,
            Rank::F => 0.8,
            Rank::E => 1.0,
            Rank::D => 1.5,
            Rank::C => 2.0,
            Rank::B => 3.0,
            Rank::A => 4.0,
            Rank::S => 10.0,
            Rank::SS => 15.0,
            Rank::SSS => 20.0,
        }
    }

    /// Poids de tirage de chaque rank (dans l'ordre de `TOUS`)
    /// selon la rareté. Plus la rareté est haute, plus les ranks élevés
    /// sont probables.
    fn poids(rarete: Rarete) -> [f32; 10] {
        //                       G   F   E   D   C   B   A   S  SS SSS
        match rarete {
            Rarete::Commun     => [50.0, 30.0, 15.0, 4.0, 0.9, 0.09, 0.009, 0.0009, 0.00009, 0.00001],
            Rarete::PeuCommun  => [45.0, 25.0, 14.0, 7.0, 5.8, 3.18, 0.018, 0.0018, 0.00018, 0.00002],
            Rarete::Rare       => [35.0, 20.0, 13.0, 11.0, 10.8, 5.18, 4.018, 1.0018, 0.00018, 0.00002],
            Rarete::SuperRare  => [25.0, 10.0, 7.0, 9.0, 19.6, 13.36, 10.036, 6.0036, 0.00036, 0.00004],
            Rarete::Epique     => [20.0, 10.0, 7.0, 8.0, 17.5, 12.45, 12.045, 7.0045, 4.00045, 2.00005],
            Rarete::Legendaire => [15.0, 8.0, 7.0, 6.0, 15.5, 12.45, 14.045, 10.0045, 8.00045, 4.00005],
            Rarete::Mythique   => [5.0, 6.0, 4.0, 6.0, 15.5, 12.45, 15.045, 20.0045, 9.00045, 8.00005],
        }
    }

    /// Tire un rank au hasard selon la rareté.
    pub fn tirer(rarete: Rarete, rng: &mut impl Rng) -> Rank {
    let poids = Self::poids(rarete);

    let total: f32 = poids.iter().sum();

    let mut tirage = rng.random_range(0.0..total);

    for (rank, p) in Self::TOUS.iter().zip(poids) {
        if tirage < p {
            return *rank;
        }

        tirage -= p;
    }

    Rank::G
}
}

// ============================================================
// STATS D'UNE ARME / D'UN ÉQUIPEMENT (rank + rareté)
// ============================================================

/// Stats de base d'une arme ou d'une armure, avant multiplicateurs.
pub const STAT_BASE: f64 = 10.0;
pub const DURABILITE_BASE: f64 = 100.0;

/// Stats calculées à la création d'un exemplaire.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StatsEquipement {
    pub attaque: i64,
    pub defense: i64,
    pub durabilite: i64,
}

impl StatsEquipement {
    /// Calcule les stats selon le rank ET la rareté :
    ///
    ///   stat       = 10  x mult(rank) x mult(rareté)   (attaque OU défense)
    ///   durabilité = 100 x mult(rank) x mult(rareté)
    ///
    /// Un facteur absent compte pour x1. Sans rank ni rareté, on retrouve
    /// les anciennes valeurs : 0 / 0 / 100.
    pub fn calculer(
        rarete: Option<Rarete>,
        rank: Option<Rank>,
        est_arme: bool,
    ) -> Self {
        if rarete.is_none() && rank.is_none() {
            return Self {
                attaque: 0,
                defense: 0,
                durabilite: DURABILITE_BASE as i64,
            };
        }

        let m = rank.map_or(1.0, Rank::multiplicateur)
            * rarete.map_or(1.0, Rarete::multiplicateur);

        // Au moins 1 : la base de données impose durability_max > 0.
        let stat = ((STAT_BASE * m).round() as i64).max(1);
        let durabilite = ((DURABILITE_BASE * m).round() as i64).max(1);

        Self {
            attaque: if est_arme { stat } else { 0 },
            defense: if est_arme { 0 } else { stat },
            durabilite,
        }
    }
}

#[cfg(test)]
mod tests_stats {
    use super::*;

    #[test]
    fn sans_marque_on_garde_les_anciennes_valeurs() {
        let s = StatsEquipement::calculer(None, None, true);
        assert_eq!((s.attaque, s.defense, s.durabilite), (0, 0, 100));
    }

    #[test]
    fn rank_et_rarete_se_multiplient() {
        // Rank C (x2.0) + Légendaire (x2.0) => x4.0
        let s = StatsEquipement::calculer(
            Some(Rarete::Legendaire),
            Some(Rank::C),
            true,
        );
        assert_eq!((s.attaque, s.defense, s.durabilite), (40, 0, 400));
    }

    #[test]
    fn une_armure_donne_de_la_defense() {
        // Rank E (x1.0) + Rare (x1.25) => x1.25
        let s = StatsEquipement::calculer(
            Some(Rarete::Rare),
            Some(Rank::E),
            false,
        );
        assert_eq!((s.attaque, s.defense, s.durabilite), (0, 13, 125));
    }

    #[test]
    fn la_rarete_change_les_stats_a_rank_egal() {
        let commun = StatsEquipement::calculer(Some(Rarete::Commun), Some(Rank::B), true);
        let mythique = StatsEquipement::calculer(Some(Rarete::Mythique), Some(Rank::B), true);
        assert!(mythique.attaque > commun.attaque);
        assert!(mythique.durabilite > commun.durabilite);
    }

    #[test]
    fn jamais_de_durabilite_nulle() {
        let s = StatsEquipement::calculer(Some(Rarete::Commun), Some(Rank::G), true);
        assert!(s.durabilite >= 1 && s.attaque >= 1);
    }
}

// Trait pour les noms personnalisés
pub trait NomAffiche {
    fn nom_affiche(&self) -> String;
}

// Trait pour ajouter/retirer des objets
pub trait AjouterRetirer {
    fn ajouter(&mut self, qte: u64);
    fn retirer(&mut self, qte: u64);
}

// Objet de base
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Objet {
    pub nom_base: String,
    pub quantite: u64,
    pub type_objet: TypeObjet,
    pub rarety: Option<String>,
    /// Rank ("G" ... "SSS"), s'il existe.
    #[serde(default)]
    pub rank: Option<String>,
    pub nom_image: Option<String>,
    pub attributs: HashMap<String, serde_json::Value>,
}

impl Objet {
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        type_objet: TypeObjet,
        rarety: Option<&str>,
    ) -> Self {
        Self {
            nom_base: nom.replace(" ", "_"),
            quantite,
            type_objet,
            rarety: rarety.map(|s| s.to_string()),
            rank: None,
            nom_image: image.map(|s| s.to_string()),
            attributs: HashMap::new(),
        }
    }

    pub fn set_attribut(&mut self, key: &str, value: serde_json::Value) {
        self.attributs.insert(key.to_string(), value);
    }

    pub fn attribut_superieur_a_un(&self, nom_attribut: &str) -> bool {
        if let Some(value) = self.attributs.get(nom_attribut) {
            if let Some(array) = value.as_array() {
                return !array.is_empty();
            } else if let Some(obj) = value.as_object() {
                return !obj.is_empty();
            } else if let Some(s) = value.as_str() {
                return !s.is_empty();
            }
            return true;
        }
        false
    }
}

impl NomAffiche for Objet {
    fn nom_affiche(&self) -> String {
        let base = self.nom_base.clone();

        if self.type_objet == TypeObjet::Livre {
            return base;
        }

        let est_enchante =
            self.attribut_superieur_a_un("enchantements");

        match (est_enchante, self.rarety.as_ref()) {
            (true, Some(rarety)) => {
                format!("{} {} enchanté(e)", base, rarety)
            }
            (true, None) => {
                format!("{} enchanté(e)", base)
            }
            (false, Some(rarety)) => {
                format!("{} {}", base, rarety)
            }
            (false, None) => base,
        }
    }
}

impl AjouterRetirer for Objet {
    fn ajouter(&mut self, qte: u64) {
        self.quantite += qte;
    }

    fn retirer(&mut self, qte: u64) {
        self.quantite = self.quantite.saturating_sub(qte);
    }
}

impl std::fmt::Display for Objet {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} ", self.quantite)
    }
}

// Equipement
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Equipement {
    pub objet: Objet,
    pub niv: u32,
    pub bonus: i32,
    pub category: String,
    pub enchantements: Vec<String>,
    pub durabilite: u32,
    pub durabilite_max: u32,
}

impl Equipement {
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        niv: u32,
        bonus: i32,
        enchantements: Vec<String>,
        rarety: Option<&str>,
    ) -> Self {
        Self::new_avec_durabilite(
            nom,
            image,
            quantite,
            niv,
            bonus,
            enchantements,
            rarety,
            100,
        )
    }

    pub fn new_avec_durabilite(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        niv: u32,
        bonus: i32,
        enchantements: Vec<String>,
        rarety: Option<&str>,
        durabilite_max: u32,
    ) -> Self {
        let objet = Objet::new(
            nom,
            image,
            quantite,
            TypeObjet::Equipement,
            rarety,
        );

        let parts: Vec<&str> = nom.split_whitespace().collect();
        let category = parts.first().unwrap_or(&"").to_string();

        Self {
            objet,
            niv,
            bonus,
            category,
            enchantements,
            durabilite: durabilite_max,
            durabilite_max,
        }
    }

    pub fn enchanter(&mut self, enc: Vec<String>) {
        self.enchantements = enc;
    }
}

impl NomAffiche for Equipement {
    fn nom_affiche(&self) -> String {
        let base = self.objet.nom_base.clone();

        if self.enchantements.is_empty() {
            return self.objet.nom_affiche();
        }

        match &self.objet.rarety {
            Some(rarety) => {
                format!("{} {} enchanté(e)", base, rarety)
            }
            None => {
                format!("{} enchanté(e)", base)
            }
        }
    }
}

impl AjouterRetirer for Equipement {
    fn ajouter(&mut self, qte: u64) {
        self.objet.ajouter(qte);
    }

    fn retirer(&mut self, qte: u64) {
        self.objet.retirer(qte);
    }
}

impl std::fmt::Display for Equipement {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{} [Niveau {} | bonus : {} | enchantements : {:?}]",
            self.objet.quantite,
            self.niv,
            self.bonus,
            self.enchantements
        )
    }
}

// Arme
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Arme {
    pub equipement: Equipement,
    pub durabilite: u32,
    pub durabilite_max: u32,
}

impl Arme {
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        niv: u32,
        durabilite: u32,
        bonus: i32,
        enchantements: Vec<String>,
        rarety: Option<&str>,
    ) -> Self {
        let equipement = Equipement::new(
            nom,
            image,
            quantite,
            niv,
            bonus,
            enchantements,
            rarety,
        );

        Self {
            equipement,
            durabilite,
            durabilite_max: durabilite,
        }
    }

    pub fn taux_de_critique(&self) -> f32 {
        self.equipement.bonus as f32 / 100.0
    }

    pub fn enchanter(&mut self, enc: Vec<String>) {
        self.equipement.enchanter(enc);
    }
}

impl NomAffiche for Arme {
    fn nom_affiche(&self) -> String {
        self.equipement.nom_affiche()
    }
}

impl AjouterRetirer for Arme {
    fn ajouter(&mut self, qte: u64) {
        self.equipement.ajouter(qte);
    }

    fn retirer(&mut self, qte: u64) {
        self.equipement.retirer(qte);
    }
}

impl std::fmt::Display for Arme {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{} [Niveau {} | bonus : {} | enchantements : {:?} | dura : {}/{}]",
            self.equipement.objet.quantite,
            self.equipement.niv,
            self.equipement.bonus,
            self.equipement.enchantements,
            self.durabilite,
            self.durabilite_max
        )
    }
}

// Potion
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Potion {
    pub objet: Objet,
    pub effet: Option<String>,
}

impl Potion {
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        effet: Option<&str>,
        rarety: Option<&str>,
    ) -> Self {
        let objet = Objet::new(
            nom,
            image,
            quantite,
            TypeObjet::Potion,
            rarety,
        );

        Self {
            objet,
            effet: effet.map(|s| s.to_string()),
        }
    }

    pub fn appliquer_effet(&self) {
        println!("Effet appliqué : {:?}", self.effet);
    }
}

impl NomAffiche for Potion {
    fn nom_affiche(&self) -> String {
        self.objet.nom_affiche()
    }
}

impl AjouterRetirer for Potion {
    fn ajouter(&mut self, qte: u64) {
        self.objet.ajouter(qte);
    }

    fn retirer(&mut self, qte: u64) {
        self.objet.retirer(qte);
    }
}

// Livre
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Livre {
    pub objet: Objet,
    pub category: Option<String>,
    pub enchantements: Option<Vec<String>>,
    pub niv: u32,
}

impl Livre {
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        category: Option<&str>,
        enchantements: Option<Vec<String>>,
        rarety: Option<&str>,
        niv: u32,
    ) -> Self {
        let objet = Objet::new(
            nom,
            image,
            quantite,
            TypeObjet::Livre,
            rarety,
        );

        Self {
            objet,
            category: category.map(|s| s.to_string()),
            enchantements,
            niv,
        }
    }

    pub fn niv_to_roman(niv: u32) -> &'static str {
        match niv {
            1 => "I",
            2 => "II",
            3 => "III",
            4 => "IV",
            5 => "V",
            6 => "VI",
            _ => "?",
        }
    }

    pub fn ajouter_enchantement(
        &mut self,
        nom_enchantement: &str,
        niveau_enchant: u32,
    ) -> Result<(), String> {
        let max_enchants = self.niv as usize;
        let enchants = self.enchantements.get_or_insert_with(Vec::new);

        if enchants.len() >= max_enchants {
            return Err(format!(
                "Un livre de niveau {} ne peut pas avoir plus de {} enchantement(s)",
                self.niv,
                max_enchants
            ));
        }

        enchants.push(format!(
            "{} {}",
            nom_enchantement,
            Self::niv_to_roman(niveau_enchant)
        ));

        Ok(())
    }
}

impl NomAffiche for Livre {
    fn nom_affiche(&self) -> String {
        self.objet.nom_affiche()
    }
}

impl AjouterRetirer for Livre {
    fn ajouter(&mut self, qte: u64) {
        self.objet.ajouter(qte);
    }

    fn retirer(&mut self, qte: u64) {
        self.objet.retirer(qte);
    }
}

impl std::fmt::Display for Livre {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let enchants_str = match &self.enchantements {
            Some(enchants) => enchants.join("|"),
            None => "Aucun".to_string(),
        };

        write!(
            f,
            "{} [Niveau {} | {}]",
            self.objet.quantite,
            self.niv,
            enchants_str
        )
    }
}
