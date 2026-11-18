
use serde::{Deserialize, Serialize};
use rand::{Rng, RngExt};
use std::collections::HashMap;

// ============================================================
// TYPES D'OBJETS
// ============================================================

#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
pub enum TypeObjet {
    DeBase,
    Equipement,
    Arme,
    Potion,
    Livre,
}

// ============================================================
// RARETÉ
// ============================================================

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
    pub const TOUTES: [Rarete; 7] = [
        Rarete::Commun,
        Rarete::PeuCommun,
        Rarete::Rare,
        Rarete::SuperRare,
        Rarete::Epique,
        Rarete::Legendaire,
        Rarete::Mythique,
    ];

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

    pub fn depuis_label(label: &str) -> Option<Self> {
        Self::TOUTES
            .into_iter()
            .find(|rarete| rarete.label() == label)
    }

    /// Multiplicateur économique de la rareté.
    pub fn multiplicateur(self) -> f64 {
        match self {
            Rarete::Commun => 1.0,
            Rarete::PeuCommun => 1.5,
            Rarete::Rare => 2.0,
            Rarete::SuperRare => 3.0,
            Rarete::Epique => 5.0,
            Rarete::Legendaire => 8.0,
            Rarete::Mythique => 12.0,
        }
    }
}

// ============================================================
// RANK
// ============================================================

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
        Self::TOUS
            .into_iter()
            .find(|rank| rank.label() == label)
    }

    /// Multiplicateur du rang.
    pub fn multiplicateur(self) -> f64 {
        match self {
            Rank::G => 0.5,
            Rank::F => 0.75,
            Rank::E => 1.0,
            Rank::D => 1.5,
            Rank::C => 2.0,
            Rank::B => 3.0,
            Rank::A => 4.0,
            Rank::S => 6.0,
            Rank::SS => 8.0,
            Rank::SSS => 10.0,
        }
    }

    /// Poids de tirage des rangs selon la rareté.
    fn poids(rarete: Rarete) -> [u32; 10] {
        //                       G   F   E   D   C   B   A   S  SS SSS
        match rarete {
            Rarete::Commun     => [50, 30, 15, 5, 0, 0, 0, 0, 0, 0],
            Rarete::PeuCommun  => [0, 30, 35, 25, 10, 0, 0, 0, 0, 0],
            Rarete::Rare       => [0, 0, 25, 35, 25, 15, 0, 0, 0, 0],
            Rarete::SuperRare  => [0, 0, 0, 20, 35, 30, 15, 0, 0, 0],
            Rarete::Epique     => [0, 0, 0, 0, 20, 40, 30, 10, 0, 0],
            Rarete::Legendaire => [0, 0, 0, 0, 0, 15, 40, 35, 10, 0],
            Rarete::Mythique   => [0, 0, 0, 0, 0, 0, 20, 40, 30, 10],
        }
    }

    /// Tire un rang au hasard selon la rareté.
    pub fn tirer(rarete: Rarete, rng: &mut impl Rng) -> Rank {
        let poids = Self::poids(rarete);
        let total: u32 = poids.iter().sum();

        // Toutes les distributions définies ci-dessus ont un poids total positif.
        let mut tirage = rng.random_range(0..total);

        for (rank, poids) in Self::TOUS.iter().zip(poids) {
            if tirage < poids {
                return *rank;
            }

            tirage -= poids;
        }

        // Sécurité : ce cas ne devrait jamais être atteint.
        Rank::G
    }
}

// ============================================================
// TRAITS
// ============================================================

pub trait NomAffiche {
    fn nom_affiche(&self) -> String;
}

pub trait AjouterRetirer {
    fn ajouter(&mut self, qte: u64);
    fn retirer(&mut self, qte: u64);
}

// ============================================================
// OBJET DE BASE
// ============================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Objet {
    pub nom_base: String,
    pub quantite: u64,
    pub type_objet: TypeObjet,

    /// Rareté de l'objet.
    /// Les livres n'ont jamais de rareté.
    pub rarety: Option<String>,

    /// Rang de l'objet ("G" à "SSS").
    /// Les livres n'ont jamais de rang.
    #[serde(default)]
    pub rank: Option<String>,

    pub nom_image: Option<String>,

    #[serde(default)]
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
        // Un livre ne peut avoir ni rareté ni rang.
        let rarety = if type_objet == TypeObjet::Livre {
            None
        } else {
            rarety
        };

        Self {
            nom_base: nom.replace(' ', "_"),
            quantite,
            type_objet,
            rarety: rarety.map(str::to_string),
            rank: None,
            nom_image: image.map(str::to_string),
            attributs: HashMap::new(),
        }
    }

    pub fn set_attribut(
        &mut self,
        key: &str,
        value: serde_json::Value,
    ) {
        self.attributs.insert(key.to_string(), value);
    }

    pub fn supprimer_attribut(&mut self, key: &str) {
        self.attributs.remove(key);
    }

    pub fn attribut_superieur_a_un(&self, nom_attribut: &str) -> bool {
        let Some(value) = self.attributs.get(nom_attribut) else {
            return false;
        };

        if let Some(array) = value.as_array() {
            return !array.is_empty();
        }

        if let Some(object) = value.as_object() {
            return !object.is_empty();
        }

        if let Some(string) = value.as_str() {
            return !string.is_empty();
        }

        !value.is_null()
    }

    pub fn definir_rank(&mut self, rank: Option<Rank>) {
        if self.type_objet == TypeObjet::Livre {
            self.rank = None;
            return;
        }

        self.rank = rank.map(|r| r.label().to_string());
    }

    pub fn definir_rarete(&mut self, rarete: Option<Rarete>) {
        if self.type_objet == TypeObjet::Livre {
            self.rarety = None;
            return;
        }

        self.rarety = rarete.map(|r| r.label().to_string());
    }

    pub fn multiplicateur_rarete(&self) -> f64 {
        self.rarety
            .as_deref()
            .and_then(Rarete::depuis_label)
            .map(Rarete::multiplicateur)
            .unwrap_or(1.0)
    }

    pub fn multiplicateur_rank(&self) -> f64 {
        self.rank
            .as_deref()
            .and_then(Rank::depuis_label)
            .map(Rank::multiplicateur)
            .unwrap_or(1.0)
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
            (true, Some(rarete)) => {
                format!("{} {} enchanté(e)", base, rarete)
            }
            (true, None) => {
                format!("{} enchanté(e)", base)
            }
            (false, Some(rarete)) => {
                format!("{} {}", base, rarete)
            }
            (false, None) => base,
        }
    }
}

impl AjouterRetirer for Objet {
    fn ajouter(&mut self, qte: u64) {
        self.quantite = self.quantite.saturating_add(qte);
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
// ÉQUIPEMENT
// ============================================================

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

        let category = nom
            .split_whitespace()
            .next()
            .unwrap_or("")
            .to_string();

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

    pub fn ajouter_enchantement(&mut self, enchantement: String) {
        self.enchantements.push(enchantement);
    }

    pub fn retirer_enchantement(&mut self, enchantement: &str) -> bool {
        let Some(index) = self
            .enchantements
            .iter()
            .position(|e| e == enchantement)
        else {
            return false;
        };

        self.enchantements.remove(index);
        true
    }

    pub fn est_enchante(&self) -> bool {
        !self.enchantements.is_empty()
    }
}

impl NomAffiche for Equipement {
    fn nom_affiche(&self) -> String {
        let base = self.objet.nom_base.clone();

        if !self.est_enchante() {
            return self.objet.nom_affiche();
        }

        match &self.objet.rarety {
            Some(rarete) => {
                format!("{} {} enchanté(e)", base, rarete)
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

// ============================================================
// SECTION ARME
// ============================================================

// Cette section reste inchangée par rapport à ton fichier.

// ============================================================
// POTION
// ============================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Potion {
    pub objet: Objet,
    pub effet: Option<String>,

    /// Puissance de l'effet.
    /// 0 indique une ancienne donnée non encore renseignée.
    #[serde(default)]
    pub puissance: u32,

    /// Durée de l'effet en secondes.
    /// 0 indique une ancienne donnée non encore renseignée.
    #[serde(default)]
    pub duree: u32,
}

impl Potion {
    /// Constructeur historique conservé pour compatibilité.
    ///
    /// Les valeurs de puissance et de durée sont temporairement à 0.
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
            effet: effet.map(str::to_string),
            puissance: 0,
            duree: 0,
        }
    }

    /// Constructeur destiné aux nouvelles potions.
    ///
    /// La puissance et la durée doivent être strictement positives.
    pub fn new_avec_proprietes(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        effet: Option<&str>,
        rarety: Option<&str>,
        puissance: u32,
        duree: u32,
    ) -> Result<Self, String> {
        if puissance == 0 {
            return Err(
                "La puissance doit être supérieure à 0".to_string()
            );
        }

        if duree == 0 {
            return Err(
                "La durée doit être supérieure à 0 seconde".to_string()
            );
        }

        let mut potion = Self::new(
            nom,
            image,
            quantite,
            effet,
            rarety,
        );

        potion.puissance = puissance;
        potion.duree = duree;

        Ok(potion)
    }

    pub fn appliquer_effet(&self) {
        println!("Effet appliqué : {:?}", self.effet);
    }

    pub fn definir_puissance(&mut self, puissance: u32) -> Result<(), String> {
        if puissance == 0 {
            return Err("La puissance doit être supérieure à 0".to_string());
        }

        self.puissance = puissance;
        Ok(())
    }

    pub fn definir_duree(&mut self, duree: u32) -> Result<(), String> {
        if duree == 0 {
            return Err("La durée doit être supérieure à 0 seconde".to_string());
        }

        self.duree = duree;
        Ok(())
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
// LIVRE
// ============================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Livre {
    pub objet: Objet,
    pub category: Option<String>,
    pub enchantements: Option<Vec<String>>,
    pub niv: u32,
}

impl Livre {
    /// Le paramètre rarety est conservé pour compatibilité.
    /// Il est volontairement ignoré : un livre n'a ni rareté ni rang.
    pub fn new(
        nom: &str,
        image: Option<&str>,
        quantite: u64,
        category: Option<&str>,
        enchantements: Option<Vec<String>>,
        _rarety: Option<&str>,
        niv: u32,
    ) -> Self {
        let objet = Objet::new(
            nom,
            image,
            quantite,
            TypeObjet::Livre,
            None,
        );

        Self {
            objet,
            category: category.map(str::to_string),
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
        if !(1..=6).contains(&self.niv) {
            return Err(
                "Le niveau du livre doit être compris entre 1 et 6".to_string()
            );
        }

        if !(1..=6).contains(&niveau_enchant) {
            return Err(
                "Le niveau d'enchantement doit être compris entre 1 et 6".to_string()
            );
        }

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

    pub fn retirer_enchantement(&mut self, nom_enchantement: &str) -> bool {
        let Some(enchants) = self.enchantements.as_mut() else {
            return false;
        };

        let Some(index) = enchants
            .iter()
            .position(|e| e == nom_enchantement)
        else {
            return false;
        };

        enchants.remove(index);

        if enchants.is_empty() {
            self.enchantements = None;
        }

        true
    }

    pub fn nombre_enchantements(&self) -> usize {
        self.enchantements
            .as_ref()
            .map_or(0, Vec::len)
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
            Some(enchants) if !enchants.is_empty() => enchants.join("|"),
            _ => "Aucun".to_string(),
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



// ============================================================
// TESTS
// ============================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn multiplicateurs_rarete_corrects() {
        assert_eq!(Rarete::Commun.multiplicateur(), 1.0);
        assert_eq!(Rarete::PeuCommun.multiplicateur(), 1.5);
        assert_eq!(Rarete::Rare.multiplicateur(), 2.0);
        assert_eq!(Rarete::SuperRare.multiplicateur(), 3.0);
        assert_eq!(Rarete::Epique.multiplicateur(), 5.0);
        assert_eq!(Rarete::Legendaire.multiplicateur(), 8.0);
        assert_eq!(Rarete::Mythique.multiplicateur(), 12.0);
    }

    #[test]
    fn multiplicateurs_rank_corrects() {
        assert_eq!(Rank::G.multiplicateur(), 0.5);
        assert_eq!(Rank::F.multiplicateur(), 0.75);
        assert_eq!(Rank::E.multiplicateur(), 1.0);
        assert_eq!(Rank::D.multiplicateur(), 1.5);
        assert_eq!(Rank::C.multiplicateur(), 2.0);
        assert_eq!(Rank::B.multiplicateur(), 3.0);
        assert_eq!(Rank::A.multiplicateur(), 4.0);
        assert_eq!(Rank::S.multiplicateur(), 6.0);
        assert_eq!(Rank::SS.multiplicateur(), 8.0);
        assert_eq!(Rank::SSS.multiplicateur(), 10.0);
    }

    #[test]
    fn livre_ne_possede_ni_rarete_ni_rank() {
        let mut livre = Livre::new(
            "livre enchant niv 1",
            None,
            1,
            None,
            None,
            Some("Légendaire"),
            1,
        );

        livre.objet.definir_rank(Some(Rank::SSS));
        livre.objet.definir_rarete(Some(Rarete::Mythique));

        assert!(livre.objet.rarety.is_none());
        assert!(livre.objet.rank.is_none());
    }

    #[test]
    fn potion_avec_proprietes_est_valide() {
        let potion = Potion::new_avec_proprietes(
            "potion de soin",
            None,
            1,
            Some("soin"),
            None,
            25,
            30,
        )
        .unwrap();

        assert_eq!(potion.puissance, 25);
        assert_eq!(potion.duree, 30);
    }

    #[test]
    fn potion_refuse_puissance_nulle() {
        assert!(
            Potion::new_avec_proprietes(
                "potion de soin",
                None,
                1,
                Some("soin"),
                None,
                0,
                30,
            )
            .is_err()
        );
    }

    #[test]
    fn potion_refuse_duree_nulle() {
        assert!(
            Potion::new_avec_proprietes(
                "potion de soin",
                None,
                1,
                Some("soin"),
                None,
                25,
                0,
            )
            .is_err()
        );
    }

    #[test]
    fn livre_limite_le_nombre_enchantements() {
        let mut livre = Livre::new(
            "livre enchant niv 1",
            None,
            1,
            None,
            None,
            None,
            1,
        );

        assert!(
            livre.ajouter_enchantement("Protection", 1).is_ok()
        );

        assert!(
            livre.ajouter_enchantement("Vitesse", 1).is_err()
        );
    }

    #[test]
    fn retrait_enchantement_fonctionne() {
        let mut livre = Livre::new(
            "livre enchant niv 2",
            None,
            1,
            None,
            Some(vec![
                "Protection I".to_string(),
                "Vitesse II".to_string(),
            ]),
            None,
            2,
        );

        assert!(livre.retirer_enchantement("Protection I"));
        assert_eq!(livre.nombre_enchantements(), 1);
    }
}



