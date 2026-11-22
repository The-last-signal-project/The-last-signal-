
use crate::auth::account_manager::AccountManager;
use crate::auth::password::verify_password;
use crate::auth::user_manager::UserManager;
use crate::gameplay::market_manager::MarketManager;
use crate::gameplay::objets::NomAffiche;
use crate::gameplay::stuff_manager::{Inventaire, ObjetInventaire};
use crate::gameplay::tresor::Tresor;
use crate::gameplay::wallet_manager::WalletManager;
use crate::auth::session_manager::SessionManager;
use crate::network::{
    client::Client,
    packet::{ClientLog, LogLevel, Packet, PacketType},
    parser::{parse_login_payload, parse_signup_with_pseudo_payload},
};
use crate::world::world::{Position, World};

use log::{debug, error, info, trace, warn};
use serde::Deserialize;
use sqlx::{Row, SqlitePool};

// ============================================================
// Structures
// ============================================================

#[allow(dead_code)]
pub struct User {
    user_id: String,
    password_hash: String,
}

#[allow(dead_code)]
struct LoginData {
    user_id: String,
    password_hash: String,
    is_banned_perm: bool,
    is_banned_temp: bool,
}

/// Structure DTO pour désérialiser la création de compte,
/// incluant la classe choisie par le joueur.
#[derive(Debug, Deserialize)]
pub struct AccountCreatePayload {
    pub account_name: String,
    pub class_name: String,
}

#[allow(dead_code)]
pub enum HandlerResult {
    Response(Packet),
    Disconnect,
    Nothing,
}

pub struct PacketHandler;

// ============================================================
// Packet Handler
// ============================================================

impl PacketHandler {
    // =============================================================
    // INVENTAIRE ET ARGENT
    // =============================================================


    async fn inventory_packet(
        client: &Client,
        pool: &SqlitePool,
    ) -> Packet {
        let erreur = |message: &str| {
            Packet::new(
                PacketType::InventoryResponse,
                serde_json::json!({
                    "ok": false,
                    "message": message,
                })
                .to_string()
                .into_bytes(),
            )
        };

        let session = match SessionManager::new(pool.clone())
            .account_of(&client.session_id().to_string())
            .await
        {
            Ok(Some(session)) => session,

            Ok(None) => {
                warn!(
                    "Inventaire demandé sans session de compte [{}]",
                    client.session_id()
                );

                return erreur("Session introuvable");
            }

            Err(e) => {
                error!("Lecture de la session impossible : {}", e);

                return erreur("Erreur serveur");
            }
        };

        let balance = match WalletManager::new(pool.clone(), session.account_id)
            .get_balance()
            .await
        {
            Ok(balance) => Some(balance),

            Err(e) => {
                error!(
                    "Portefeuille illisible (compte {}) : {}",
                    session.account_id,
                    e
                );

                None
            }
        };

        let inventaire = match Inventaire::new(pool.clone(), session.account_id).await {
            Ok(inventaire) => inventaire,

            Err(e) => {
                error!(
                    "Inventaire illisible (compte {}) : {}",
                    session.account_id,
                    e
                );

                return erreur("Inventaire indisponible");
            }
        };

        let mut items: Vec<serde_json::Value> = inventaire
            .objets()
            .values()
            .map(|objet| {
                let mut item = serde_json::json!({
                    "nom": objet.nom_affiche(),
                    "quantite": objet.objet().quantite,
                    "rarete": objet.rarete(),
                    "rang": objet.rank(),
                });

                match objet {


                    // Un livre enchanté n'a ni rareté ni rank (même si la base
                    // en contenait) : niveau du livre + liste de ses
                    // enchantements (« Poison III », « Foudre II »...).

                    ObjetInventaire::Livre(livre) => {
                        item["rarete"] = serde_json::Value::Null;
                        item["rang"] = serde_json::Value::Null;
                        item["niveau"] = serde_json::json!(livre.niv);
                        item["enchantements"] = serde_json::json!(
                            livre.enchantements.clone().unwrap_or_default()
                        );
                    }


                    // Équipement / arme : enchantements seulement s'il y en a.

                    ObjetInventaire::Equipement(equipement) => {
                        if !equipement.enchantements.is_empty() {
                            item["enchantements"] =
                                serde_json::json!(equipement.enchantements);
                        }
                    }

                    ObjetInventaire::Arme(arme) => {
                        if !arme.equipement.enchantements.is_empty() {
                            item["enchantements"] =
                                serde_json::json!(arme.equipement.enchantements);
                        }
                    }


                    ObjetInventaire::Base(_) => {
                        item["rarete"] = serde_json::Value::Null;
                        item["rang"] = serde_json::Value::Null;
                    }


                    _ => {}
                }

                item
            })
            .collect();

        items.sort_by(|a, b| {
            a["nom"]
                .as_str()
                .unwrap_or_default()
                .cmp(b["nom"].as_str().unwrap_or_default())
        });

        Packet::new(
            PacketType::InventoryResponse,
            serde_json::json!({
                "ok": true,
                "account_id": session.account_id,
                "role": session.role_name,
                "admin": session.is_admin(),
                "balance": balance,
                "items": items,
            })
            .to_string()
            .into_bytes(),
        )
    }

    // =============================================================
    // TRÉSOR : OUVERTURE DU COFFRE
    // =============================================================

    async fn open_treasure(
        client: &Client,
        pool: &SqlitePool,
        niveau: u32,
    ) -> Packet {
        let echec = |message: &str| {
            Packet::new(
                PacketType::TreasureReward,
                serde_json::json!({
                    "ok": false,
                    "niveau": niveau,
                    "message": message,
                })
                .to_string()
                .into_bytes(),
            )
        };

        let session = match SessionManager::new(pool.clone())
            .account_of(&client.session_id().to_string())
            .await
        {
            Ok(Some(session)) => session,

            Ok(None) => {
                warn!("Trésor pris sans session de compte valide");

                return echec("Session introuvable");
            }

            Err(e) => {
                error!("Lecture de la session impossible : {}", e);

                return echec("Erreur serveur");
            }
        };

        let account_id = session.account_id;
        let is_admin = session.is_admin();

        let mut inventaire = match Inventaire::new(pool.clone(), account_id).await {
            Ok(inventaire) => inventaire,

            Err(e) => {
                error!(
                    "Inventaire indisponible (compte {}) : {}",
                    account_id,
                    e
                );

                return echec("Inventaire indisponible");
            }
        };

        let mut tresor = Tresor::new();

        match inventaire
            .ouvrir_coffre(&mut tresor, niveau, is_admin, false, None)
            .await
        {
            Ok(resultat) => {
                let mut items: Vec<String> = resultat
                    .objets
                    .iter()
                    .filter(|(_, quantite)| **quantite > 0)
                    .map(|(nom, quantite)| format!("{} x{}", nom, quantite))
                    .collect();

                items.sort();

                items.extend(
                    resultat
                        .artefacts
                        .iter()
                        .map(|artefact| artefact.to_string()),
                );

                info!(
                    "Trésor niveau {} ouvert (compte {}, rôle {:?}, admin={}) : {}",
                    niveau,
                    account_id,

                    session.role_name,
                    is_admin,
                    items.join(", ")
                );

                Packet::new(
                    PacketType::TreasureReward,
                    serde_json::json!({
                        "ok": true,
                        "niveau": niveau,
                        "role": session.role_name,
                        "admin": is_admin,
                        "items": items,
                    })
                    .to_string()
                    .into_bytes(),
                )
            }

            Err(e) => {
                error!(
                    "Ouverture du coffre niveau {} impossible (compte {}) : {}",
                    niveau,
                    account_id,
                    e
                );

                echec("Erreur lors de l'ouverture du coffre")
            }
        }
    }

    // =============================================================
    // LECTURE DES PAYLOADS BINAIRES
    // =============================================================

    fn read_i64(payload: &[u8], start: usize) -> Option<i64> {
        let bytes = payload.get(start..start + 8)?;

        Some(i64::from_be_bytes(bytes.try_into().ok()?))
    }

    fn read_u64(payload: &[u8], start: usize) -> Option<u64> {
        let bytes = payload.get(start..start + 8)?;

        Some(u64::from_be_bytes(bytes.try_into().ok()?))
    }

    // =============================================================
    // GESTIONNAIRE PRINCIPAL
    // =============================================================

    pub async fn handle(
        client: &mut Client,
        packet: Packet,
        pool: SqlitePool,
        world: World,
    ) -> HandlerResult {
        match packet.packet_type {
            // =================================================
            // LOG
            // =================================================

            PacketType::Log => {
                let log = match serde_json::from_slice::<ClientLog>(&packet.payload) {
                    Ok(log) => log,

                    Err(e) => {
                        error!("Impossible de décoder le paquet LOG : {}", e);

                        return HandlerResult::Nothing;
                    }
                };

                match log.level {
                    LogLevel::TRACE => {
                        trace!(
                            "[CLIENT] [{}:{}] {}",
                            log.file,
                            log.line,
                            log.message
                        );
                    }

                    LogLevel::DEBUG => {
                        debug!(
                            "[CLIENT] [{}:{}] {}",
                            log.file,
                            log.line,
                            log.message
                        );
                    }

                    LogLevel::INFO => {
                        info!(
                            "[CLIENT] [{}:{}] {}",
                            log.file,
                            log.line,
                            log.message
                        );
                    }

                    LogLevel::WARNING => {
                        warn!(
                            "[CLIENT] [{}:{}] {}",
                            log.file,
                            log.line,
                            log.message
                        );
                    }

                    LogLevel::ERROR => {
                        error!(
                            "[CLIENT] [{}:{}] {}",
                            log.file,
                            log.line,
                            log.message
                        );
                    }
                }

                HandlerResult::Nothing
            }

            // =================================================
            // PING
            // =================================================

            PacketType::Ping => {
                debug!("Ping reçu");

                HandlerResult::Response(Packet::new(
                    PacketType::Ping,
                    b"PONG".to_vec(),
                ))
            }

            // =================================================
            // BAN
            // =================================================

            PacketType::BAN => {
                debug!("Packet BAN reçu depuis le client : ignoré");

                HandlerResult::Nothing
            }

            // =================================================
            // INSCRIPTION
            // =================================================

            PacketType::SignUp => {
                if client.user_id().is_some() {
                    return HandlerResult::Response(Packet::new(
                        PacketType::SignUpResponse,
                        b"Deja authentifie".to_vec(),
                    ));
                }

                let (email, password, pseudo) =
                    match parse_signup_with_pseudo_payload(&packet.payload) {
                        Ok(signup) => signup,

                        Err(e) => {
                            debug!("SIGN_UP invalide : {}", e);

                            return HandlerResult::Response(Packet::new(
                                PacketType::SignUpResponse,
                                b"SIGN_UP invalide".to_vec(),
                            ));
                        }
                    };

                let manager = UserManager::new(pool.clone());

                match manager
                    .create_user_with_pseudo(&email, &password, &pseudo)
                    .await
                {
                    Ok(user) => match manager.set_status(&user.user_id, "CONNECTED").await {
                        Ok(true) => {
                            client.set_user_id(Some(user.user_id.clone()));

                            info!(
                                "Inscription et connexion réussies : {}",
                                user.email
                            );

                            HandlerResult::Response(Packet::new(
                                PacketType::SignUpResponse,
                                b"Utilisateur cree avec succes".to_vec(),
                            ))
                        }

                        Ok(false) => {
                            error!("Utilisateur créé mais statut introuvable");

                            HandlerResult::Response(Packet::new(
                                PacketType::SignUpResponse,
                                b"Erreur serveur".to_vec(),
                            ))
                        }

                        Err(e) => {
                            error!(
                                "Impossible de connecter le nouvel utilisateur : {}",
                                e
                            );

                            HandlerResult::Response(Packet::new(
                                PacketType::SignUpResponse,
                                b"Erreur serveur".to_vec(),
                            ))
                        }
                    },

                    Err(message) => {
                        debug!("Inscription refusée : {}", message);

                        let response = if message.contains("pseudo est déjà utilisé") {
                            b"Pseudo deja utilise".to_vec()
                        } else if message.starts_with("Pseudo invalide") {
                            b"Pseudo invalide".to_vec()
                        } else if message.contains("déjà utilisée") {
                            b"Email deja utilise".to_vec()
                        } else if message.contains("au moins 8 caractères") {
                            b"Mot de passe trop court".to_vec()
                        } else if message.contains("invalide") {
                            b"Email invalide".to_vec()
                        } else {
                            error!("Erreur d'inscription : {}", message);

                            b"Erreur serveur".to_vec()
                        };

                        HandlerResult::Response(Packet::new(
                            PacketType::SignUpResponse,
                            response,
                        ))
                    }
                }
            }

            // =================================================
            // CONNEXION
            // =================================================

            PacketType::Login => {
                if client.user_id().is_some() {
                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Deja authentifie".to_vec(),
                    ));
                }

                let (email, password) = match parse_login_payload(&packet.payload) {
                    Ok(login) => login,

                    Err(error) => {
                        debug!("LOGIN invalide : {}", error);

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"LOGIN invalide".to_vec(),
                        ));
                    }
                };

                let manager = UserManager::new(pool.clone());

                let credentials = match manager.get_credentials_by_email(&email).await {
                    Ok(Some(credentials)) => credentials,

                    Ok(None) => {
                        debug!("Tentative de connexion avec un utilisateur inexistant");

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Identifiants invalides".to_vec(),
                        ));
                    }

                    Err(e) => {
                        error!("Erreur de recherche utilisateur : {}", e);

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Erreur serveur".to_vec(),
                        ));
                    }
                };

                let display_name = credentials
                    .pseudo
                    .clone()
                    .unwrap_or_else(|| credentials.email.clone());

                let ban_row = match sqlx::query(
                    r#"
                    SELECT
                        EXISTS(
                            SELECT 1
                            FROM bansperm
                            WHERE user_id = ?
                        ) AS is_banned_perm,

                        EXISTS(
                            SELECT 1
                            FROM bansferme
                            WHERE user_id = ?
                              AND datetime(date_deban) > CURRENT_TIMESTAMP
                        ) AS is_banned_temp
                    "#,
                )
                .bind(&credentials.user_id)
                .bind(&credentials.user_id)
                .fetch_one(&pool)
                .await
                {
                    Ok(row) => row,

                    Err(e) => {
                        error!("Erreur de vérification des bannissements : {}", e);

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Erreur serveur".to_vec(),
                        ));
                    }
                };

                let login_data = LoginData {
                    user_id: credentials.user_id,
                    password_hash: credentials.password_hash,
                    is_banned_perm: ban_row.get::<i64, _>("is_banned_perm") != 0,
                    is_banned_temp: ban_row.get::<i64, _>("is_banned_temp") != 0,
                };

                if login_data.is_banned_perm {
                    debug!("Connexion refusée : utilisateur banni définitivement");

                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Compte banni definitivement".to_vec(),
                    ));
                }

                if login_data.is_banned_temp {
                    debug!("Connexion refusée : utilisateur temporairement banni");

                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Compte temporairement banni".to_vec(),
                    ));
                }

                let password_valid = {
                    let password = password.clone();
                    let password_hash = login_data.password_hash.clone();

                    tokio::task::spawn_blocking(move || {
                        verify_password(&password, &password_hash)
                    })
                    .await
                    .unwrap_or(false)
                };

                if !password_valid {
                    let attempts = match sqlx::query_scalar::<_, i64>(
                        r#"
                        INSERT INTO login_attempts (
                            user_id,
                            failed_attempts,
                            last_attempt
                        )
                        VALUES (?, 1, CURRENT_TIMESTAMP)

                        ON CONFLICT(user_id)
                        DO UPDATE SET
                            failed_attempts = failed_attempts + 1,
                            last_attempt = CURRENT_TIMESTAMP

                        RETURNING failed_attempts
                        "#,
                    )
                    .bind(&login_data.user_id)
                    .fetch_one(&pool)
                    .await
                    {
                        Ok(value) => value,

                        Err(error) => {
                            error!(
                                "Erreur lors de l'enregistrement de la tentative : {}",
                                error
                            );

                            return HandlerResult::Response(Packet::new(
                                PacketType::LoginResponse,
                                b"Erreur serveur".to_vec(),
                            ));
                        }
                    };

                    debug!(
                        "Mot de passe incorrect pour {} : tentative {}",
                        email,
                        attempts
                    );

                    if attempts >= 3 {
                        let sursis_jours = match sqlx::query_scalar::<_, i64>(
                            r#"
                            SELECT sursis
                            FROM banssursis
                            WHERE user_id = ?
                            LIMIT 1
                            "#,
                        )
                        .bind(&login_data.user_id)
                        .fetch_optional(&pool)
                        .await
                        {
                            Ok(value) => value,

                            Err(error) => {
                                error!(
                                    "Erreur lors de la vérification du sursis : {}",
                                    error
                                );

                                return HandlerResult::Response(Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                ));
                            }
                        };

                        if let Some(jours) = sursis_jours {
                            if jours <= 0 {
                                error!(
                                    "Sursis invalide pour {} : {} jour(s)",
                                    email,
                                    jours
                                );

                                return HandlerResult::Response(Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                ));
                            }

                            debug!(
                                "Activation du sursis pour {} : {} jour(s)",
                                email,
                                jours
                            );

                            let result = sqlx::query(
                                r#"
                                INSERT INTO bansferme (
                                    user_id,
                                    auteur,
                                    raison,
                                    date_ban,
                                    date_deban
                                )
                                VALUES (
                                    ?,
                                    'system',
                                    'Activation du sursis',
                                    CURRENT_TIMESTAMP,
                                    datetime(
                                        CURRENT_TIMESTAMP,
                                        '+' || ? || ' days',
                                        '+10 minutes'
                                    )
                                )

                                ON CONFLICT(user_id)
                                DO UPDATE SET
                                    auteur = CASE
                                        WHEN COALESCE(bansferme.auteur, '') = ''
                                            THEN 'system'

                                        WHEN instr(bansferme.auteur, 'system') = 0
                                            THEN bansferme.auteur || ', system'

                                        ELSE bansferme.auteur
                                    END,

                                    raison = CASE
                                        WHEN COALESCE(bansferme.raison, '') = ''
                                            THEN 'Activation du sursis'

                                        WHEN instr(
                                            bansferme.raison,
                                            'Activation du sursis'
                                        ) = 0
                                            THEN bansferme.raison
                                                || ' | Activation du sursis'

                                        ELSE bansferme.raison
                                    END,

                                    date_ban = CURRENT_TIMESTAMP,

                                    date_deban = CASE
                                        WHEN datetime(bansferme.date_deban)
                                            > CURRENT_TIMESTAMP
                                            THEN datetime(
                                                bansferme.date_deban,
                                                '+' || ? || ' days'
                                            )

                                        ELSE datetime(
                                            CURRENT_TIMESTAMP,
                                            '+' || ? || ' days',
                                            '+10 minutes'
                                        )
                                    END
                                "#,
                            )
                            .bind(&login_data.user_id)
                            .bind(jours)
                            .bind(jours)
                            .bind(jours)
                            .execute(&pool)
                            .await;

                            if let Err(error) = result {
                                error!(
                                    "Impossible d'activer le sursis pour {} : {}",
                                    email,
                                    error
                                );

                                return HandlerResult::Response(Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                ));
                            }

                            let _ = sqlx::query(
                                r#"DELETE FROM banssursis WHERE user_id = ?"#,
                            )
                            .bind(&login_data.user_id)
                            .execute(&pool)
                            .await;
                        } else {
                            debug!("Aucun sursis pour {}", email);

                            let result = sqlx::query(
                                r#"
                                INSERT INTO bansferme (
                                    user_id,
                                    auteur,
                                    raison,
                                    date_ban,
                                    date_deban
                                )
                                VALUES (
                                    ?,
                                    'system',
                                    'Trop de tentatives de connexion échouées',
                                    CURRENT_TIMESTAMP,
                                    datetime(CURRENT_TIMESTAMP, '+10 minutes')
                                )

                                ON CONFLICT(user_id)
                                DO UPDATE SET
                                    auteur = CASE
                                        WHEN COALESCE(bansferme.auteur, '') = ''
                                            THEN 'system'

                                        WHEN instr(bansferme.auteur, 'system') = 0
                                            THEN bansferme.auteur || ', system'

                                        ELSE bansferme.auteur
                                    END,

                                    raison = CASE
                                        WHEN COALESCE(bansferme.raison, '') = ''
                                            THEN 'Trop de tentatives de connexion échouées'

                                        WHEN instr(
                                            bansferme.raison,
                                            'Trop de tentatives de connexion échouées'
                                        ) = 0
                                            THEN bansferme.raison
                                                || ' | Trop de tentatives de connexion échouées'

                                        ELSE bansferme.raison
                                    END,

                                    date_ban = CURRENT_TIMESTAMP,

                                    date_deban = CASE
                                        WHEN datetime(bansferme.date_deban)
                                            > CURRENT_TIMESTAMP
                                            THEN datetime(
                                                bansferme.date_deban,
                                                '+10 minutes'
                                            )

                                        ELSE datetime(
                                            CURRENT_TIMESTAMP,
                                            '+10 minutes'
                                        )
                                    END
                                "#,
                            )
                            .bind(&login_data.user_id)
                            .execute(&pool)
                            .await;

                            if let Err(error) = result {
                                error!(
                                    "Impossible de créer le ban temporaire : {}",
                                    error
                                );

                                return HandlerResult::Response(Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                ));
                            }
                        }

                        let _ = sqlx::query(
                            r#"DELETE FROM login_attempts WHERE user_id = ?"#,
                        )
                        .bind(&login_data.user_id)
                        .execute(&pool)
                        .await;

                        info!("Utilisateur banni");

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Trop de tentatives. Compte bloque temporairement."
                                .to_vec(),
                        ));
                    }

                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Identifiants invalides".to_vec(),
                    ));
                }

                let is_already_connected =
                    match manager.is_connected(&login_data.user_id).await {
                        Ok(connected) => connected,

                        Err(error) => {
                            error!(
                                "Erreur lors de la vérification de connexion : {}",
                                error
                            );

                            return HandlerResult::Response(Packet::new(
                                PacketType::LoginResponse,
                                b"Erreur serveur".to_vec(),
                            ));
                        }
                    };

                if is_already_connected {
                    debug!("Tentative de connexion avec un compte déjà connecté");

                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Ce compte est deja connecte".to_vec(),
                    ));
                }

                match manager.set_status(&login_data.user_id, "CONNECTED").await {
                    Ok(true) => {}

                    Ok(false) => {
                        error!(
                            "Utilisateur introuvable lors de la connexion : {}",
                            login_data.user_id
                        );

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Erreur serveur".to_vec(),
                        ));
                    }

                    Err(e) => {
                        error!("Erreur lors de la connexion du joueur : {}", e);

                        return HandlerResult::Response(Packet::new(
                            PacketType::LoginResponse,
                            b"Erreur serveur".to_vec(),
                        ));
                    }
                }
                

                if let Err(e) = manager.record_login(&login_data.user_id).await {
                    error!("Impossible d'enregistrer la dernière connexion : {}", e);

                    let _ = manager
                        .set_status(&login_data.user_id, "DISCONNECTED")
                        .await;

                    return HandlerResult::Response(Packet::new(
                        PacketType::LoginResponse,
                        b"Erreur serveur".to_vec(),
                    ));
                }

                let _ = sqlx::query(r#"DELETE FROM login_attempts WHERE user_id = ?"#)
                    .bind(&login_data.user_id)
                    .execute(&pool)
                    .await;

                debug!("Utilisateur authentifié : {}", email);

                client.set_user_id(Some(login_data.user_id.clone()));

                HandlerResult::Response(Packet::new(
                    PacketType::LoginResponse,
                    format!("Utilisateur {} authentifié", display_name).into_bytes(),
                ))
            }
            

            // =================================================
            // CHAT
            // =================================================

            PacketType::Chat => {
                debug!(
                    "Message : {}",
                    String::from_utf8_lossy(&packet.payload)
                );

                HandlerResult::Response(Packet::new(
                    PacketType::Chat,
                    packet.payload,
                ))
            }

            // =================================================
            // INVENTAIRE
            // =================================================

            PacketType::InventoryRequest => {
                HandlerResult::Response(
                    Self::inventory_packet(client, &pool).await,
                )
            }

            // =================================================
            // MARCHÉ (interface client, JSON)
            // =================================================

            PacketType::MarketRequest => {
                let account_id = match client.account_id() {
                    Some(id) => id,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketResponse,
                            br#"{"ok":false,"message":"Compte non selectionne"}"#.to_vec(),
                        ));
                    }
                };

                let reponse = crate::network::market_api::traiter(
                    pool.clone(),
                    account_id,
                    &packet.payload,
                )
                .await;

                HandlerResult::Response(Packet::new(
                    PacketType::MarketResponse,
                    reponse,
                ))
            }

            // =================================================
            // DÉPLACEMENT
            // =================================================

            PacketType::Move => {
                if !client.is_spawned() {
                    return HandlerResult::Nothing;
                }

                if packet.payload.len() != 12 {
                    warn!(
                        "Paquet Move invalide : {} octets",
                        packet.payload.len()
                    );

                    return HandlerResult::Nothing;
                }

                let x = i32::from_be_bytes([
                    packet.payload[0],
                    packet.payload[1],
                    packet.payload[2],
                    packet.payload[3],
                ]);

                let y = i32::from_be_bytes([
                    packet.payload[4],
                    packet.payload[5],
                    packet.payload[6],
                    packet.payload[7],
                ]);

                let z = i32::from_be_bytes([
                    packet.payload[8],
                    packet.payload[9],
                    packet.payload[10],
                    packet.payload[11],
                ]);

                let player_id = client.session_id();
                let position = Position::new(x, y, z);

                


    // Le serveur valide le déplacement (limites, murs, porte, clé).
    // Refusé : on recale uniquement ce joueur sur sa dernière position valide.
    match world.try_move(player_id, position).await {
        // Trésor pris : on ouvre le coffre du niveau tiré (1 à 5) et on le
        // range dans l'inventaire du compte. Le verrou de la zone est
        // déjà relâché : la base de données ne bloque personne d'autre.
        Ok(accepted) => match accepted.treasure_won {
            Some(niveau) => {
                info!(
                    "Trésor pris par [{}] : ouverture du coffre niveau {}",
                    player_id, niveau
                );

                HandlerResult::Response(
                    Self::open_treasure(client, &pool, niveau).await,
                )
            }
            None => HandlerResult::Nothing,
        },
        Err(authoritative) => {
            warn!(
                "Déplacement refusé [{}] : ({}, {}) -> retour en ({}, {})",
                player_id,
                x,
                y,
                authoritative.x,
                authoritative.y
            );
             HandlerResult::Nothing
            }
            }
             }

            // =================================================
            // SPAWN
            // =================================================

            PacketType::Spawn => {
                if client.user_id().is_none() || client.account_id().is_none() {
                    warn!(
                        "Spawn refusé : aucun compte sélectionné [{}]",
                        client.session_id()
                    );

                    return HandlerResult::Nothing;
                }

                if client.spawn().await {
                    info!(
                        "Joueur entré dans le monde [{}]",
                        client.session_id()
                    );
                }

                HandlerResult::Nothing
            }

            // =================================================
            // DÉCONNEXION
            // =================================================

            PacketType::DECO => {
                info!("Demande de déconnexion reçue");

                HandlerResult::Disconnect
            }

            // =================================================
            // MARCHÉ : ACHAT
            // =================================================

            PacketType::MarketBuy => {
                if packet.payload.len() != 24 {
                    error!(
                        "MARKET_BUY : payload invalide ({} octets)",
                        packet.payload.len()
                    );

                    return HandlerResult::Response(Packet::new(
                        PacketType::MarketBuy,
                        b"MARKET_BUY invalide".to_vec(),
                    ));
                }

                let objet_id = match Self::read_i64(&packet.payload, 0) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            b"MARKET_BUY invalide".to_vec(),
                        ));
                    }
                };

                let quantity = match Self::read_u64(&packet.payload, 8) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            b"MARKET_BUY invalide".to_vec(),
                        ));
                    }
                };

                let prix_unitaire_max = match Self::read_i64(&packet.payload, 16) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            b"MARKET_BUY invalide".to_vec(),
                        ));
                    }
                };

                let account_id = match client.account_id() {
                    Some(id) => id,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            b"Compte non selectionne".to_vec(),
                        ));
                    }
                };

                let market = MarketManager::new(pool.clone());

                match market
                    .creer_ordre_achat(
                        account_id,
                        objet_id,
                        quantity,
                        prix_unitaire_max,
                    )
                    .await
                {
                    Ok(ordre_id) => {
                        info!(
                            "Ordre d'achat {} créé | objet={} quantité={} prix_max={}",
                            ordre_id,
                            objet_id,
                            quantity,
                            prix_unitaire_max
                        );

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            ordre_id.to_be_bytes().to_vec(),
                        ))
                    }

                    Err(e) => {
                        error!("Erreur création ordre d'achat : {}", e);

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketBuy,
                            format!("Erreur: {}", e).into_bytes(),
                        ))
                    }
                }
            }

            // =================================================
            // LISTE DES COMPTES
            // =================================================

            PacketType::AccountListRequest => {
                if !packet.payload.is_empty() {
                    return HandlerResult::Nothing;
                }

                let user_id = match client.user_id() {
                    Some(id) => id.to_string(),

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountListResponse,
                            b"Utilisateur non authentifie".to_vec(),
                        ));
                    }
                };

                let manager = AccountManager::new(pool.clone());

                match manager.list_accounts(&user_id).await {
                    Ok(accounts) => {
                        let payload = serde_json::to_vec(&accounts)
                            .unwrap_or_else(|_| b"[]".to_vec());

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountListResponse,
                            payload,
                        ))
                    }

                    Err(e) => {
                        error!("Erreur de liste des comptes : {}", e);

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountListResponse,
                            b"Erreur serveur".to_vec(),
                        ))
                    }
                }
            }

            // =================================================
            // CRÉATION D'UN COMPTE JOUEUR
            // =================================================

            PacketType::AccountCreate => {
                let user_id = match client.user_id() {
                    Some(id) => id.to_string(),

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{\"ok\":false,\"message\":\"Utilisateur non authentifie\"}"#
                                .to_vec(),
                        ));
                    }
                };

                let req: AccountCreatePayload =
                    match serde_json::from_slice(&packet.payload) {
                        Ok(payload) => payload,

                        Err(e) => {
                            debug!("Payload AccountCreate invalide : {}", e);

                            return HandlerResult::Response(Packet::new(
                                PacketType::AccountResult,
                                br#"{\"ok\":false,\"message\":\"Format JSON invalide. Champs requis : account_name et class_name\"}"#
                                    .to_vec(),
                            ));
                        }
                    };

                let manager = AccountManager::new(pool.clone());

                match manager
                    .create_account(&user_id, &req.account_name, &req.class_name)
                    .await
                {
                    Ok(account) => {
                        info!(
                            "Compte '{}' (Classe : '{}') créé avec succès pour user_id={}",
                            account.account_name,
                            account.class_name,
                            user_id
                        );

                        let payload = serde_json::json!({
                            "ok": true,
                            "message": "Compte créé",
                            "account": account
                        });

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            serde_json::to_vec(&payload).unwrap_or_default(),
                        ))
                    }

                    Err(message) => {
                        debug!("Échec de création du compte : {}", message);

                        let payload = serde_json::json!({
                            "ok": false,
                            "message": message
                        });

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            serde_json::to_vec(&payload).unwrap_or_default(),
                        ))
                    }
                }
            }

            // =================================================
            // SÉLECTION D'UN COMPTE
            // =================================================

            PacketType::AccountSelect => {
                if packet.payload.len() != 8 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::AccountResult,
                        br#"{\"ok\":false,\"message\":\"Identifiant invalide\"}"#
                            .to_vec(),
                    ));
                }

                let account_id =
                    i64::from_be_bytes(packet.payload[..8].try_into().unwrap());

                if account_id <= 0 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::AccountResult,
                        br#"{\"ok\":false,\"message\":\"Identifiant invalide\"}"#
                            .to_vec(),
                    ));
                }

                let user_id = match client.user_id() {
                    Some(id) => id.to_string(),

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{\"ok\":false,\"message\":\"Utilisateur non authentifie\"}"#
                                .to_vec(),
                        ));
                    }
                };

                let manager = AccountManager::new(pool.clone());

                match manager
                    .account_belongs_to_user(account_id, &user_id)
                    .await
                {
                    Ok(true) => {
                        client.set_account_id(Some(account_id));

                        if let Err(e) = SessionManager::new(pool.clone())
                            .bind_account(
                                &client.session_id().to_string(),
                                &user_id,
                                account_id,
                            )
                            .await
                        {
                            error!(
                                "Impossible d'enregistrer la session [{}] : {}",
                                client.session_id(),
                                e
                            );
                        }

                        let payload = serde_json::json!({
                            "ok": true,
                            "message": "Compte sélectionné",
                            "account_id": account_id
                        });

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            serde_json::to_vec(&payload).unwrap_or_default(),
                        ))
                    }

                    Ok(false) => {
                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            r#"{\"ok\":false,\"message\":\"Compte introuvable ou non autorisé\"}"#
                                .as_bytes()
                                .to_vec(),
                        ))
                    }

                    Err(e) => {
                        error!("Erreur de vérification du compte : {}", e);

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{\"ok\":false,\"message\":\"Erreur serveur\"}"#
                                .to_vec(),
                        ))
                    }
                }
            }

            // =================================================
            // MARCHÉ : VENTE
            // =================================================

            PacketType::MarketSell => {
                if packet.payload.len() != 24 {
                    error!(
                        "MARKET_SELL : payload invalide ({} octets)",
                        packet.payload.len()
                    );

                    return HandlerResult::Response(Packet::new(
                        PacketType::MarketSell,
                        b"MARKET_SELL invalide".to_vec(),
                    ));
                }

                let objet_id = match Self::read_i64(&packet.payload, 0) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            b"MARKET_SELL invalide".to_vec(),
                        ));
                    }
                };

                let quantity = match Self::read_u64(&packet.payload, 8) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            b"MARKET_SELL invalide".to_vec(),
                        ));
                    }
                };

                let prix_unitaire = match Self::read_i64(&packet.payload, 16) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            b"MARKET_SELL invalide".to_vec(),
                        ));
                    }
                };

                let account_id = match client.account_id() {
                    Some(id) => id,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            b"Compte non selectionne".to_vec(),
                        ));
                    }
                };

                let market = MarketManager::new(pool.clone());

                match market
                    .creer_ordre_vente(
                        account_id,
                        objet_id,
                        quantity,
                        prix_unitaire,
                    )
                    .await
                {
                    Ok(ordre_id) => {
                        info!(
                            "Ordre de vente {} créé | objet={} quantité={} prix={}",
                            ordre_id,
                            objet_id,
                            quantity,
                            prix_unitaire
                        );

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            ordre_id.to_be_bytes().to_vec(),
                        ))
                    }

                    Err(e) => {
                        error!("Erreur création ordre de vente : {}", e);

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketSell,
                            format!("Erreur: {}", e).into_bytes(),
                        ))
                    }
                }
            }

            // =================================================
            // MARCHÉ : ANNULATION D'ACHAT
            // =================================================

            PacketType::MarketCancelBuy => {
                if packet.payload.len() != 8 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::MarketCancelBuy,
                        b"MARKET_CANCEL_BUY invalide".to_vec(),
                    ));
                }

                let ordre_id = match Self::read_i64(&packet.payload, 0) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelBuy,
                            b"MARKET_CANCEL_BUY invalide".to_vec(),
                        ));
                    }
                };

                let account_id = match client.account_id() {
                    Some(id) => id,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelBuy,
                            b"Compte non selectionne".to_vec(),
                        ));
                    }
                };

                let market = MarketManager::new(pool.clone());

                match market.annuler_ordre_achat(account_id, ordre_id).await {
                    Ok(()) => {
                        info!("Ordre d'achat {} annulé", ordre_id);

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelBuy,
                            ordre_id.to_be_bytes().to_vec(),
                        ))
                    }

                    Err(e) => {
                        error!(
                            "Erreur annulation ordre d'achat {} : {}",
                            ordre_id,
                            e
                        );

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelBuy,
                            format!("Erreur: {}", e).into_bytes(),
                        ))
                    }
                }
            }

            // =================================================
            // MARCHÉ : ANNULATION DE VENTE
            // =================================================

            PacketType::MarketCancelSell => {
                if packet.payload.len() != 8 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::MarketCancelSell,
                        b"MARKET_CANCEL_SELL invalide".to_vec(),
                    ));
                }

                let ordre_id = match Self::read_i64(&packet.payload, 0) {
                    Some(value) => value,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelSell,
                            b"MARKET_CANCEL_SELL invalide".to_vec(),
                        ));
                    }
                };

                let account_id = match client.account_id() {
                    Some(id) => id,

                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelSell,
                            b"Compte non selectionne".to_vec(),
                        ));
                    }
                };

                let market = MarketManager::new(pool.clone());

                match market.annuler_ordre_vente(account_id, ordre_id).await {
                    Ok(()) => {
                        info!("Ordre de vente {} annulé", ordre_id);

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelSell,
                            ordre_id.to_be_bytes().to_vec(),
                        ))
                    }

                    Err(e) => {
                        error!(
                            "Erreur annulation ordre de vente {} : {}",
                            ordre_id,
                            e
                        );

                        HandlerResult::Response(Packet::new(
                            PacketType::MarketCancelSell,
                            format!("Erreur: {}", e).into_bytes(),
                        ))
                    }
                }
            }

            // =================================================
            // RÉPONSES INTERDITES VENANT DU CLIENT
            // =================================================

            PacketType::LoginResponse
            | PacketType::SignUpResponse
            | PacketType::PlayerState
            | PacketType::PlayerRemove
            | PacketType::ZoneState
            | PacketType::TreasureReward
            | PacketType::InventoryResponse
            | PacketType::MarketResponse
            | PacketType::Session
            | PacketType::AccountListResponse
            | PacketType::AccountResult => {
                error!(
                    "Réponse reçue du client alors qu'elle doit être envoyée par le serveur : {:?}",
                    packet.packet_type
                );

                HandlerResult::Nothing
            }
        }
    }
}