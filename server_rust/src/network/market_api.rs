//! Interface JSON du marché pour le client.
//!
//! Le client envoie un paquet `MarketRequest` dont le corps est un JSON
//! `{"action": ..., ...}` ; le serveur répond par un paquet `MarketResponse`
//! contenant un JSON `{"action": ..., "ok": bool, "message"?: ..., ...}`.
//!
//! Actions :
//!
//! | action      | paramètres                               | réponse                        |
//! |-------------|-------------------------------------------|--------------------------------|
//! | `search`    | `filtres` (voir `FiltreRecherche`)        | `ventes`, `balance`            |
//! | `inventory` | -                                         | `items`, `balance`             |
//! | `my_sales`  | -                                         | `ventes`                       |
//! | `buy`       | `ligne_vente_id`, `quantite`              | `achete`, `demande`, `depense` |
//! | `sell`      | `lignes` : `[{stuff_id, quantite, prix}]` | `lignes`, `transactions`       |
//! | `cancel_sale` | `ligne_vente_id`                        | -                              |
//!
//! Le compte est toujours celui de la connexion : le client ne choisit
//! jamais l'identité sous laquelle il agit.

use log::{debug, error};
use serde::Deserialize;
use serde_json::{Value, json};
use sqlx::SqlitePool;

use crate::gameplay::market_manager::{
    FiltreRecherche, LigneVenteDemande, MarketManager,
};
use crate::gameplay::wallet_manager::WalletManager;

/// Nombre maximal de lignes dans un ordre de vente envoyé par le client.
const MAX_LIGNES_VENTE: usize = 100;

#[derive(Debug, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
enum Requete {
    Search {
        #[serde(default)]
        filtres: FiltreRecherche,
    },
    Inventory,
    MySales,
    Buy {
        ligne_vente_id: i64,
        quantite: u64,
    },
    Sell {
        lignes: Vec<LigneVenteRequete>,
    },
    CancelSale {
        ligne_vente_id: i64,
    },
}

#[derive(Debug, Deserialize)]
struct LigneVenteRequete {
    stuff_id: i64,
    quantite: u64,
    prix: i64,
}

/// Traite une requête et retourne le corps JSON de la réponse.
pub async fn traiter(
    pool: SqlitePool,
    account_id: i64,
    payload: &[u8],
) -> Vec<u8> {
    let reponse = match serde_json::from_slice::<Requete>(payload) {
        Ok(requete) => executer(pool, account_id, requete).await,
        Err(e) => {
            debug!("Requête de marché invalide : {}", e);
            echec("inconnue", "Requête invalide")
        }
    };

    serde_json::to_vec(&reponse).unwrap_or_else(|_| {
        br#"{"ok":false,"message":"Erreur serveur"}"#.to_vec()
    })
}

async fn executer(
    pool: SqlitePool,
    account_id: i64,
    requete: Requete,
) -> Value {
    let marche = MarketManager::new(pool.clone());

    match requete {
        Requete::Search { filtres } => {
            match marche.rechercher_ventes(account_id, filtres).await {
                Ok(ventes) => json!({
                    "action": "search",
                    "ok": true,
                    "ventes": ventes,
                    "balance": solde(&pool, account_id).await,
                }),
                Err(e) => echec_sql("search", &e),
            }
        }

        Requete::Inventory => {
            match marche.inventaire_vendable(account_id).await {
                Ok(items) => json!({
                    "action": "inventory",
                    "ok": true,
                    "items": items,
                    "balance": solde(&pool, account_id).await,
                }),
                Err(e) => echec_sql("inventory", &e),
            }
        }

        Requete::MySales => match marche.mes_ventes(account_id).await {
            Ok(ventes) => json!({
                "action": "my_sales",
                "ok": true,
                "ventes": ventes,
            }),
            Err(e) => echec_sql("my_sales", &e),
        },

        Requete::Buy {
            ligne_vente_id,
            quantite,
        } => match marche
            .acheter_ligne(account_id, ligne_vente_id, quantite)
            .await
        {
            Ok(resultat) if resultat.quantite_achetee > 0 => json!({
                "action": "buy",
                "ok": true,
                "message": format!(
                    "{} acheté(s) pour {}",
                    resultat.quantite_achetee, resultat.depense_totale
                ),
                "demande": resultat.quantite_demandee,
                "achete": resultat.quantite_achetee,
                "depense": resultat.depense_totale,
                "balance": solde(&pool, account_id).await,
            }),
            Ok(_) => echec(
                "buy",
                "Cette vente n'est plus disponible : rien n'a été acheté",
            ),
            Err(e) => echec_sql("buy", &e),
        },

        Requete::Sell { lignes } => {
            if lignes.is_empty() || lignes.len() > MAX_LIGNES_VENTE {
                return echec("sell", "Nombre de lignes invalide");
            }

            let lignes: Vec<LigneVenteDemande> = lignes
                .into_iter()
                .map(|l| LigneVenteDemande {
                    stuff_id: l.stuff_id,
                    quantite: l.quantite,
                    prix_unitaire: l.prix,
                })
                .collect();

            match marche.creer_ordre_vente_lignes(account_id, lignes).await {
                Ok(ordre) => json!({
                    "action": "sell",
                    "ok": true,
                    "message": format!(
                        "{} exemplaire(s) mis en vente",
                        ordre.lignes.len()
                    ),
                    "ordre_id": ordre.ordre_id,
                    "lignes": ordre.lignes,
                    "transactions": ordre.transactions,
                }),
                Err(e) => echec_sql("sell", &e),
            }
        }

        Requete::CancelSale { ligne_vente_id } => {
            match marche
                .annuler_vente_par_ligne(account_id, ligne_vente_id)
                .await
            {
                Ok(()) => json!({
                    "action": "cancel_sale",
                    "ok": true,
                    "message": "Vente annulée, objet restitué",
                }),
                Err(e) => echec_sql("cancel_sale", &e),
            }
        }
    }
}

async fn solde(pool: &SqlitePool, account_id: i64) -> Option<i64> {
    WalletManager::new(pool.clone(), account_id)
        .get_balance()
        .await
        .ok()
}

fn echec(action: &str, message: &str) -> Value {
    json!({ "action": action, "ok": false, "message": message })
}

/// Transforme une erreur en message affichable : les erreurs métier et les
/// refus des triggers sont lisibles par le joueur, le reste reste interne.
fn echec_sql(action: &str, e: &sqlx::Error) -> Value {
    let message = match e {
        sqlx::Error::Protocol(message) => message.clone(),
        sqlx::Error::Database(db) => {
            error!("Marché ({}) refusé par la base : {}", action, db.message());
            db.message().to_string()
        }
        autre => {
            error!("Marché ({}) : {}", action, autre);
            "Erreur serveur".to_string()
        }
    };

    echec(action, &message)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn les_requetes_sont_reconnues() {
        let r: Requete = serde_json::from_str(
            r#"{"action":"search","filtres":{"nom":"epee","durabilite_max":50,"type":"armes"}}"#,
        )
        .unwrap();

        match r {
            Requete::Search { filtres } => {
                assert_eq!(filtres.nom.as_deref(), Some("epee"));
                assert_eq!(filtres.durabilite_max, Some(50));
                assert_eq!(filtres.type_objet.as_deref(), Some("armes"));
                assert_eq!(filtres.prix_min, None);
            }
            _ => panic!("search attendu"),
        }

        let r: Requete =
            serde_json::from_str(r#"{"action":"search"}"#).unwrap();
        assert!(matches!(r, Requete::Search { .. }));

        let r: Requete = serde_json::from_str(r#"{"action":"inventory"}"#).unwrap();
        assert!(matches!(r, Requete::Inventory));

        let r: Requete = serde_json::from_str(
            r#"{"action":"sell","lignes":[{"stuff_id":3,"quantite":2,"prix":10}]}"#,
        )
        .unwrap();
        assert!(matches!(r, Requete::Sell { .. }));
    }

    #[test]
    fn une_action_inconnue_est_refusee() {
        assert!(serde_json::from_str::<Requete>(r#"{"action":"hack"}"#).is_err());
        assert!(serde_json::from_str::<Requete>("pas du json").is_err());
    }
}
