use rand::{Rng, RngExt};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ============================================================
//  RARETÉ (Commun -> Légendaire)
// ============================================================
#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
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
    pub const TOUTES: [Rarete; 7] = [
        Rarete::Commun,
        Rarete::PeuCommun,
        Rarete::Rare,
        Rarete::SuperRare,
        Rarete::Epique,
        Rarete::Legendaire,
        Rarete::Mythique,
    ];

    pub fn label(&self) -> &'static str {
        match self {
            Rarete::Commun => "Commun",
            Rarete::PeuCommun => "Peu commun",
            Rarete::Rare => "Rare",
            Rarete::SuperRare => "Super rare",
            Rarete::Epique => "Épique",
            Rarete::Legendaire => "Légendaire",
            Rarete::Mythique => "Mythique"
        }
    }

    /// Poids de tirage (modifiables). Total = 1000 => pour mille.
    pub fn poids(&self) -> u32 {
        match self {
            Rarete::Commun => 600,
            Rarete::PeuCommun => 250,
            Rarete::Rare => 100,
            Rarete::SuperRare => 30,
            Rarete::Epique => 15,
            Rarete::Legendaire => 5,
            Rarete::Mythique => 3,
        }
    }

    pub fn tirer<R: Rng>(rng: &mut R) -> Rarete {
        let table: Vec<(Rarete, u32)> =
            Self::TOUTES.iter().map(|r| (*r, r.poids())).collect();
        tirer_pondere(&table, rng)
    }
}

// ============================================================
//  RANK (G -> SSS)
// ============================================================
#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
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

    pub fn label(&self) -> &'static str {
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

    /// Poids de tirage du rank selon la rareté (plus l'objet est rare,
    /// plus le rank est élevé en moyenne).
    /// Ordre des colonnes : G, F, E, D, C, B, A, S, SS, SSS.
    /// Pour un rank indépendant de la rareté, mets la même ligne partout.
    fn poids_pour(rarete: Rarete) -> [u32; 10] {
        match rarete {
            Rarete::Commun => [35, 28, 18, 10, 6, 2, 1, 0, 0, 0],
            Rarete::PeuCommun => [15, 22, 22, 18, 12, 7, 3, 1, 0, 0],
            Rarete::Rare => [5, 10, 16, 22, 20, 14, 8, 4, 1, 0],
            Rarete::SuperRare => [2, 5, 10, 16, 22, 20, 14, 8, 3, 0],
            Rarete::Epique => [1, 3, 6, 12, 20, 24, 18, 10, 5, 1],
            Rarete::Legendaire => [0, 0, 1, 3, 8, 15, 25, 25, 16, 7],
            Rarete::Mythique => [0, 0, 0, 5, 8, 14, 22, 25, 16, 10],
        }
    }

    pub fn tirer<R: Rng>(rarete: Rarete, rng: &mut R) -> Rank {
        let poids = Self::poids_pour(rarete);
        let table: Vec<(Rank, u32)> = Self::TOUS
            .iter()
            .zip(poids.iter())
            .map(|(r, p)| (*r, *p))
            .collect();
        tirer_pondere(&table, rng)
    }
}

/// Tirage au sort pondéré générique.
fn tirer_pondere<T: Copy, R: Rng>(table: &[(T, u32)], rng: &mut R) -> T {
    let total: u32 = table.iter().map(|(_, p)| *p).sum();
    let mut tirage = rng.random_range(0..total);
    for (item, poids) in table {
        if tirage < *poids {
            return *item;
        }
        tirage -= *poids;
    }
    table[0].0 // jamais atteint si total > 0
}

// ============================================================
//  TRAITS
// ============================================================

// Enum pour les types d'objets
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum TypeObjet {
    DeBase,
    Equipement,
    Arme,
    Potion,
    Livre,
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

/// Trait à appeler à l'ouverture d'un trésor : donne une rareté
/// et un rank aléatoires à l'artéfact.
pub trait Rarifiable {
    fn objet_mut(&mut self) -> &mut Objet;

    /// Rareté DÉJÀ connue (ex. catégorie du coffre) : on tire seulement le rank.
    fn attribuer_rank_pour(&mut self, rarete: Rarete) {
        let mut rng = rand::rng();
        let rank = Rank::tirer(rarete, &mut rng);
        let objet = self.objet_mut();
        objet.set_rarete(rarete);
        objet.set_rank(rank);
    }

    /// Tire la rareté puis le rank (dépendant de la rareté).
    fn attribuer_rarete_et_rank(&mut self) {
        let mut rng = rand::rng();
        let rarete = Rarete::tirer(&mut rng);
        let rank = Rank::tirer(rarete, &mut rng);
        let objet = self.objet_mut();
        objet.set_rarete(rarete);
        objet.set_rank(rank);
    }
}

// ============================================================
//  OBJET DE BASE
// ============================================================
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Objet {
    pub nom_base: String,
    pub quantite: u64,
    pub type_objet: TypeObjet,
    pub rarety: Option<String>,
    /// Rank de G à SSS (None tant que non attribué)
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

    pub fn set_rarete(&mut self, rarete: Rarete) {
        self.rarety = Some(rarete.label().to_string());
    }

    pub fn set_rank(&mut self, rank: Rank) {
        self.rank = Some(rank.label().to_string());
    }

    /// Suffixe d'affichage du rank, ex. " [S]"
    fn suffixe_rank(&self) -> String {
        match &self.rank {
            Some(r) => format!(" [{}]", r),
            None => String::new(),
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

impl Rarifiable for Objet {
    fn objet_mut(&mut self) -> &mut Objet {
        self
    }
}

impl NomAffiche for Objet {
    fn nom_affiche(&self) -> String {
        let base = self.nom_base.clone();

        if self.type_objet == TypeObjet::Livre {
            return base;
        }

        let est_enchante = self.attribut_superieur_a_un("enchantements");

        let nom = match (est_enchante, self.rarety.as_ref()) {
            (true, Some(rarety)) => format!("{} {} enchanté(e)", base, rarety),
            (true, None) => format!("{} enchanté(e)", base),
            (false, Some(rarety)) => format!("{} {}", base, rarety),
            (false, None) => base,
        };

        format!("{}{}", nom, self.suffixe_rank())
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

// ============================================================
//  EQUIPEMENT
// ============================================================
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Equipement {
    pub objet: Objet,
    pub niv: u32,
    pub bonus: i32,
    pub category: String,
    pub enchantements: Vec<String>,
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
        let objet = Objet::new(nom, image, quantite, TypeObjet::Equipement, rarety);

        let parts: Vec<&str> = nom.split_whitespace().collect();
        let category = parts.first().unwrap_or(&"").to_string();

        Self {
            objet,
            niv,
            bonus,
            category,
            enchantements,
        }
    }

    pub fn enchanter(&mut self, enc: Vec<String>) {
        self.enchantements = enc;
    }
}

impl Rarifiable for Equipement {
    fn objet_mut(&mut self) -> &mut Objet {
        &mut self.objet
    }
}

impl NomAffiche for Equipement {
    fn nom_affiche(&self) -> String {
        let base = self.objet.nom_base.clone();

        if self.enchantements.is_empty() {
            return self.objet.nom_affiche();
        }

        let nom = match &self.objet.rarety {
            Some(rarety) => format!("{} {} enchanté(e)", base, rarety),
            None => format!("{} enchanté(e)", base),
        };

        format!("{}{}", nom, self.objet.suffixe_rank())
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
            self.objet.quantite, self.niv, self.bonus, self.enchantements
        )
    }
}

// ============================================================
//  ARME
// ============================================================
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
        let equipement =
            Equipement::new(nom, image, quantite, niv, bonus, enchantements, rarety);

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

impl Rarifiable for Arme {
    fn objet_mut(&mut self) -> &mut Objet {
        &mut self.equipement.objet
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

// ============================================================
//  POTION
// ============================================================
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
        let objet = Objet::new(nom, image, quantite, TypeObjet::Potion, rarety);

        Self {
            objet,
            effet: effet.map(|s| s.to_string()),
        }
    }

    pub fn appliquer_effet(&self) {
        println!("Effet appliqué : {:?}", self.effet);
    }
}

impl Rarifiable for Potion {
    fn objet_mut(&mut self) -> &mut Objet {
        &mut self.objet
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

// ============================================================
//  LIVRE
// ============================================================
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
        let objet = Objet::new(nom, image, quantite, TypeObjet::Livre, rarety);

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
                self.niv, max_enchants
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

impl Rarifiable for Livre {
    fn objet_mut(&mut self) -> &mut Objet {
        &mut self.objet
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
            self.objet.quantite, self.niv, enchants_str
        )
    }
}

// ============================================================
//  TESTS
// ============================================================
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn attribution_donne_rarete_et_rank() {
        let mut arme = Arme::new("Epee longue", None, 1, 1, 100, 5, vec![], None);
        arme.attribuer_rarete_et_rank();
        assert!(arme.equipement.objet.rarety.is_some());
        assert!(arme.equipement.objet.rank.is_some());
    }

    #[test]
    fn commun_ne_donne_jamais_sss() {
        let mut rng = rand::rng();
        for _ in 0..10_000 {
            assert!(Rank::tirer(Rarete::Commun, &mut rng) < Rank::S);
        }
    }
}
