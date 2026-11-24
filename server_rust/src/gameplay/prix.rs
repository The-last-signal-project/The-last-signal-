//! Valeur d'un exemplaire sur le marché.
//!
//! Le prix d'un objet se décompose en deux parties :
//!
//! ```text
//! prix = prix de référence de l'objet  ×  facteur de qualité de l'exemplaire
//! ```
//!
//! - **Prix de référence** : le prix d'un exemplaire « standard » (facteur 1).
//!   C'est `objets_dispo.prix_marche` quand des ventes ont eu lieu, sinon
//!   `objets_dispo.prix_base` (le catalogue).
//! - **Facteur de qualité** (armes et équipements uniquement) :
//!   `multiplicateur de rareté × multiplicateur de rang × durabilité / durabilité max`.
//!   Les autres objets (objets de base, livres, potions) valent toujours 1.
//!
//! Les ventes passées sont ramenées au prix de référence en divisant leur
//! prix par le facteur de l'exemplaire vendu : une épée rang S à moitié usée
//! vendue 600 pèse donc comme un prix de référence de 600 / (rareté × 6 × 0,5),
//! et non comme une épée standard.
//!
//! Les multiplicateurs de rang sont ceux de `Rank::multiplicateur` (ceux des
//! statistiques). Ceux de rareté sont définis ici : ils sont à ajuster.

use crate::gameplay::objets::{Rank, Rarete};
use crate::gameplay::variantes;

/// Un exemplaire cassé ne vaut jamais 0 : le prix est au minimum 1 % du
/// prix de référence (et le prix d'une ligne de marché doit rester > 0).
const FACTEUR_MIN: f64 = 0.01;

/// Multiplicateur de prix de la rareté (à ajuster à ta convenance).
pub fn multiplicateur_rarete(rarete: Rarete) -> f64 {
    match rarete {
            Rarete::Commun => 1.0,
            Rarete::PeuCommun => 1.1,
            Rarete::Rare => 1.25,
            Rarete::SuperRare => 1.5,
            Rarete::Epique => 1.75,
            Rarete::Legendaire => 2.0,
            Rarete::Mythique => 2.5,
        }
}

/// Part de durabilité restante (1.0 = neuf). Sans durabilité connue : 1.0.
pub fn ratio_durabilite(durabilite: Option<i64>, durabilite_max: Option<i64>) -> f64 {
    match (durabilite, durabilite_max) {
        (Some(courante), Some(maximale)) if maximale > 0 => {
            courante.clamp(0, maximale) as f64 / maximale as f64
        }
        _ => 1.0,
    }
}

/// Facteur de qualité d'un exemplaire (voir la documentation du module).
///
/// Une rareté ou un rang inconnu compte pour 1.
pub fn facteur_qualite(
    type_objet: &str,
    rarete: Option<&str>,
    rang: Option<&str>,
    durabilite: Option<i64>,
    durabilite_max: Option<i64>,
) -> f64 {
    // Seuls les armes et équipements ont une qualité.
    if !variantes::type_a_fiche_equipement(type_objet) {
        return 1.0;
    }

    let mut facteur = 1.0;

    if let Some(rarete) = rarete.and_then(Rarete::depuis_label) {
        facteur *= multiplicateur_rarete(rarete);
    }

    if let Some(rang) = rang.and_then(Rank::depuis_label) {
        facteur *= rang.multiplicateur();
    }

    facteur *= ratio_durabilite(durabilite, durabilite_max);

    facteur.max(FACTEUR_MIN)
}

/// Prix d'un exemplaire : prix de référence × facteur, arrondi, au moins 1.
pub fn prix_estime(prix_reference: i64, facteur: f64) -> i64 {
    ((prix_reference as f64 * facteur).round() as i64).max(1)
}

/// Prix de référence d'un objet : le prix du marché s'il existe (des ventes
/// ont eu lieu), sinon le prix du catalogue.
pub fn prix_reference(prix_base: i64, prix_marche: i64) -> i64 {
    if prix_marche > 0 { prix_marche } else { prix_base }
}

/// Prix d'un exemplaire précis, rareté, rang et durabilité compris.
#[allow(clippy::too_many_arguments)]
pub fn prix_exemplaire(
    type_objet: &str,
    rarete: Option<&str>,
    rang: Option<&str>,
    durabilite: Option<i64>,
    durabilite_max: Option<i64>,
    prix_base: i64,
    prix_marche: i64,
) -> i64 {
    prix_estime(
        prix_reference(prix_base, prix_marche),
        facteur_qualite(type_objet, rarete, rang, durabilite, durabilite_max),
    )
}

/// Prix de référence que révèlent des transactions récentes.
///
/// Chaque élément est `(prix_total, quantite, facteur de l'exemplaire)`.
/// Moyenne pondérée par la quantité des prix ramenés au facteur 1, arrondie
/// à l'entier le plus proche. `None` s'il n'y a aucune transaction.
pub fn prix_reference_moyen(transactions: &[(i64, i64, f64)]) -> Option<i64> {
    let mut total_normalise = 0.0_f64;
    let mut quantite_totale = 0.0_f64;

    for &(prix_total, quantite, facteur) in transactions {
        if quantite <= 0 || facteur <= 0.0 {
            continue;
        }

        total_normalise += prix_total as f64 / facteur;
        quantite_totale += quantite as f64;
    }

    if quantite_totale <= 0.0 {
        return None;
    }

    Some(((total_normalise / quantite_totale).round() as i64).max(1))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn proche(a: f64, b: f64) -> bool {
        (a - b).abs() < 1e-9
    }

    #[test]
    fn un_exemplaire_standard_vaut_le_prix_de_reference() {
        // Commun, rang E (x1), neuf.
        let f = facteur_qualite("armes", Some("Commun"), Some("E"), Some(100), Some(100));
        assert!(proche(f, 1.0));
        assert_eq!(prix_estime(60, f), 60);
    }
    #[test]
    fn la_rarete_et_le_rang_multiplient_le_prix() {
        let rare = multiplicateur_rarete(Rarete::Rare);

        // Rare et rang B (x4), neuf : rare x 4.
        let f = facteur_qualite("equipment", Some("Rare"), Some("B"), Some(300), Some(300));
        assert!(proche(f, rare * 4.0));
        assert_eq!(prix_estime(100, f), (100.0 * rare * 4.0).round() as i64);

        // Seul le rang compte quand la rareté est absente (S = x13).
        let f = facteur_qualite("armes", None, Some("S"), Some(600), Some(600));
        assert!(proche(f, 13.0));

        // Un rang G ramène le prix à 60 % (x0,6).
        let f = facteur_qualite("armes", Some("Commun"), Some("G"), Some(50), Some(50));
        assert!(proche(f, 0.6));
        assert_eq!(prix_estime(60, f), 36);
    }

    #[test]
    fn la_perte_de_durabilite_baisse_le_prix() {
        let rare = multiplicateur_rarete(Rarete::Rare);

        let neuf = facteur_qualite("armes", Some("Rare"), Some("B"), Some(300), Some(300));
        let moitie = facteur_qualite("armes", Some("Rare"), Some("B"), Some(150), Some(300));

        assert!(proche(moitie, neuf / 2.0));
        assert_eq!(prix_estime(100, moitie), (100.0 * rare * 4.0 / 2.0).round() as i64);

        // Une durabilité supérieure au max est ramenée au max.
        let trop = facteur_qualite("armes", Some("Rare"), Some("B"), Some(999), Some(300));
        assert!(proche(trop, neuf));
    }

    #[test]
    fn le_prix_initial_applique_deja_rarete_rang_et_durabilite() {
        let rare = multiplicateur_rarete(Rarete::Rare);

        // Aucune vente (prix_marche = 0) : on part du catalogue, soit 60.
        // Épée Rare, rang C (x2), à 40 % de durabilité : 60 x rare x 2 x 0,4.
        let prix = prix_exemplaire("armes", Some("Rare"), Some("C"), Some(80), Some(200), 60, 0);
        assert_eq!(prix, (60.0 * rare * 2.0 * 0.4).round() as i64);

        // Même épée neuve : 60 x rare x 2.
        let neuf = prix_exemplaire("armes", Some("Rare"), Some("C"), Some(200), Some(200), 60, 0);
        assert_eq!(neuf, (60.0 * rare * 2.0).round() as i64);

        // Une fois le marché connu (référence 100), il remplace le catalogue.
        let marche = prix_exemplaire("armes", Some("Rare"), Some("C"), Some(200), Some(200), 60, 100);
        assert_eq!(marche, (100.0 * rare * 2.0).round() as i64);

        // Objet de base : ni rareté ni rang ni durabilité.
        assert_eq!(prix_exemplaire("mineral", None, None, None, None, 7, 0), 7);
        assert_eq!(prix_exemplaire("mineral", None, None, None, None, 7, 9), 9);
    }


    #[test]
    fn un_exemplaire_casse_ne_vaut_jamais_zero() {
        let f = facteur_qualite("armes", Some("Commun"), Some("E"), Some(0), Some(100));
        assert!(proche(f, FACTEUR_MIN));
        assert_eq!(prix_estime(30, f), 1);
        assert_eq!(prix_estime(0, 5.0), 1);
    }

    #[test]
    fn les_autres_objets_n_ont_pas_de_qualite() {
        // Même avec une marque ou une durabilité résiduelle dans la base.
        for type_objet in ["mineral", "consumable", "enchanted_book", "potion", "military_equipment"] {
            let f = facteur_qualite(type_objet, Some("Mythique"), Some("SSS"), Some(1), Some(100));
            assert!(proche(f, 1.0), "{type_objet}");
        }
    }

    #[test]
    fn rarete_ou_rang_inconnus_valent_un() {
        let f = facteur_qualite("armes", Some("Divin"), Some("ZZ"), Some(100), Some(100));
        assert!(proche(f, 1.0));
    }

    #[test]
    fn la_durabilite_inconnue_ne_penalise_pas() {
        assert!(proche(ratio_durabilite(None, None), 1.0));
        assert!(proche(ratio_durabilite(Some(5), None), 1.0));
        assert!(proche(ratio_durabilite(Some(5), Some(0)), 1.0));
    }

   
    #[test]
    fn les_ventes_passees_sont_ramenees_au_prix_de_reference() {
        // Épée rang S (x6) neuve vendue 600 : référence 100.
        assert_eq!(prix_reference_moyen(&[(600, 1, 6.0)]), Some(100));

        // Épée rang S à moitié usée (x3) vendue 300 : même référence.
        assert_eq!(prix_reference_moyen(&[(300, 1, 3.0)]), Some(100));

        // Moyenne pondérée : 3 x 10 puis 1 x 20 -> 12,5 -> 13.
        assert_eq!(prix_reference_moyen(&[(30, 3, 1.0), (20, 1, 1.0)]), Some(13));

        // Rien à moyenner.
        assert_eq!(prix_reference_moyen(&[]), None);
    }
}
