use crate::network::{parser::{
    parse_login_payload,
    parse_signup_payload,},packet::{
    Packet,
    PacketType,
    LogLevel,
    ClientLog,},client::Client
    
};

use crate::world::world::{World,Position};
use crate::gameplay::market_manager::MarketManager;
use crate::auth::user_manager::UserManager;
use crate::auth::account_manager::AccountManager;
use crate::auth::password::verify_password;

use log::{
    trace,
    debug,
    info,
    warn,
    error,
};

use sqlx::{
    SqlitePool,
    Row,
};




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
#[allow(dead_code)]
pub enum HandlerResult {
    Response(Packet),
    Disconnect,
    Nothing,
}
#[allow(dead_code)]
pub struct PacketHandler;


// ============================================================
// Packet Handler
// ============================================================
#[allow(dead_code)]
impl PacketHandler {
    fn read_i64(
    payload: &[u8],
    start: usize,
) -> Option<i64> {

    let bytes =
        payload.get(start..start + 8)?;

    Some(
        i64::from_be_bytes(
            bytes.try_into().ok()?
        )
    )
}

#[allow(dead_code)]
fn read_u64(
    payload: &[u8],
    start: usize,
) -> Option<u64> {

    let bytes =
        payload.get(start..start + 8)?;

    Some(
        u64::from_be_bytes(
            bytes.try_into().ok()?
        )
    )
}
    #[allow(dead_code)]
    pub async fn handle(
        client: &mut Client,
        packet: Packet,
        pool: SqlitePool,
        world : World,
    ) -> HandlerResult {

        match packet.packet_type {

            // =================================================
            // LOG
            // =================================================

            PacketType::Log => {

                let log =
                    match serde_json::from_slice::<ClientLog>(
                        &packet.payload
                    ) {

                        Ok(log) => log,

                        Err(e) => {

                            error!(
                                "Impossible de décoder le paquet LOG : {}",
                                e
                            );

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

                HandlerResult::Response(
                    Packet::new(
                        PacketType::Ping,
                        b"PONG".to_vec(),
                    )
                )
            }


            // =================================================
            // BAN
            // =================================================

            PacketType::BAN => {

                debug!(
                    "Packet BAN reçu depuis le client : ignoré"
                );

                HandlerResult::Nothing
            }


            // =================================================
            // SIGN UP
            // =================================================

            
PacketType::SignUp => {
    let (email, password) =
        match parse_signup_payload(&packet.payload) {
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

    match manager.create_user(&email, &password).await {
    Ok(user) => {
        // Connecter automatiquement le nouvel utilisateur.
        match manager.set_status(&user.user_id, "CONNECTED").await {
            Ok(true) => {
                client.set_user_id(Some(user.user_id.clone()));

                info!("Inscription et connexion réussies : {}", user.email);

                HandlerResult::Response(Packet::new(
                    PacketType::SignUpResponse,
                    b"Utilisateur cree avec succes".to_vec(),
                ))
            }
            Ok(false) => {
                error!(
                    "Utilisateur créé mais statut introuvable : {}",
                    user.user_id
                );

                HandlerResult::Response(Packet::new(
                    PacketType::SignUpResponse,
                    b"Erreur serveur".to_vec(),
                ))
            }
            Err(e) => {
                error!("Impossible de connecter le nouvel utilisateur : {}", e);

                HandlerResult::Response(Packet::new(
                    PacketType::SignUpResponse,
                    b"Erreur serveur".to_vec(),
                ))
            }
        }
    }
    Err(message) => {
        debug!("Inscription refusée : {}", message);

        let response = if message.contains("déjà utilisée") {
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
            response.to_vec(),
        ))
    }
}

        
}



            // =================================================
            // LOGIN
            // =================================================

            PacketType::Login => {

                // ------------------------------------------------
                // Parser LOGIN
                // ------------------------------------------------

                let (email, password) =
                    match parse_login_payload(
                        &packet.payload
                    ) {

                        Ok(login) => login,

                        Err(error) => {

                            debug!(
                                "LOGIN invalide : {}",
                                error
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::LoginResponse,
                                    b"LOGIN invalide".to_vec(),
                                )
                            );
                        }
                    };


                

// ------------------------------------------------
// Récupération utilisateur via UserManager
// + vérification des bannissements
// ------------------------------------------------

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

let ban_row = match sqlx::query(
    r#"
    SELECT
        EXISTS(
            SELECT 1 FROM bansperm WHERE user_id = ?
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


                // ------------------------------------------------
                // BAN PERMANENT
                // ------------------------------------------------

                if login_data.is_banned_perm {

                    debug!(
                        "Connexion refusée : utilisateur banni définitivement"
                    );

                    return HandlerResult::Response(
                        Packet::new(
                            PacketType::LoginResponse,
                            b"Compte banni definitivement".to_vec(),
                        )
                    );
                }


                // ------------------------------------------------
                // BAN FERME
                // ------------------------------------------------

                if login_data.is_banned_temp {

                    debug!(
                        "Connexion refusée : utilisateur temporairement banni"
                    );

                    return HandlerResult::Response(
                        Packet::new(
                            PacketType::LoginResponse,
                            b"Compte temporairement banni".to_vec(),
                        )
                    );
                }


                // ------------------------------------------------
                // Vérification mot de passe
                // ------------------------------------------------

                let password_valid =
                    verify_password(
                        &password,
                        &login_data.password_hash,
                    );


                // =================================================
                // MOT DE PASSE INCORRECT
                // =================================================

                if !password_valid {

                    // --------------------------------------------
                    // Compteur de tentatives
                    // --------------------------------------------

                    let attempts =
                        match sqlx::query_scalar::<_, i64>(
                            r#"
                            INSERT INTO login_attempts (
                                user_id,
                                failed_attempts,
                                last_attempt
                            )
                            VALUES (
                                ?,
                                1,
                                CURRENT_TIMESTAMP
                            )

                            ON CONFLICT(user_id)

                            DO UPDATE SET
                                failed_attempts =
                                    failed_attempts + 1,

                                last_attempt =
                                    CURRENT_TIMESTAMP

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

                                return HandlerResult::Response(
                                    Packet::new(
                                        PacketType::LoginResponse,
                                        b"Erreur serveur".to_vec(),
                                    )
                                );
                            }
                        };


                    debug!(
                        "Mot de passe incorrect pour {} : tentative {}",
                        email,
                        attempts
                    );


                    // =================================================
                    // 3 ÉCHECS
                    // =================================================
                    
                    if attempts >= 3 {

                        // --------------------------------------------
                        // Recherche du sursis
                        // --------------------------------------------
                        debug!(
    "DEBUG BAN : création du ban pour user_id={}, tentatives={}",
    login_data.user_id,
    attempts
);
                        let sursis_jours =
                            match sqlx::query_scalar::<_, i64>(
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

                                    return HandlerResult::Response(
                                        Packet::new(
                                            PacketType::LoginResponse,
                                            b"Erreur serveur".to_vec(),
                                        )
                                    );
                                }
                            };


                        // =================================================
                        // SURsis EXISTANT
                        // =================================================

                        if let Some(jours) =
                            sursis_jours
                        {

                            // ----------------------------------------
                            // Validation
                            // ----------------------------------------

                            if jours <= 0 {

                                error!(
                                    "Sursis invalide pour {} : {} jour(s)",
                                    email,
                                    jours
                                );

                                return HandlerResult::Response(
                                    Packet::new(
                                        PacketType::LoginResponse,
                                        b"Erreur serveur".to_vec(),
                                    )
                                );
                            }


                            debug!(
                                "Activation du sursis pour {} : {} jour(s)",
                                email,
                                jours
                            );


                            // ----------------------------------------
                            // Ajouter le sursis au ban ferme
                            //
                            // SI le ban est encore actif :
                            //
                            //     ancienne date_deban
                            //         +
                            //     sursis_jours
                            //
                            // SINON :
                            //
                            //     maintenant
                            //         +
                            //     sursis_jours
                            //         +
                            //     10 minutes
                            // ----------------------------------------

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
        datetime(CURRENT_TIMESTAMP, '+' || ? || ' days', '+10 minutes')
    )
    ON CONFLICT(user_id) DO UPDATE SET

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

            WHEN instr(bansferme.raison, 'Activation du sursis') = 0
                THEN bansferme.raison || ' | Activation du sursis'

            ELSE bansferme.raison
        END,

        date_ban = CURRENT_TIMESTAMP,

        date_deban = CASE
            WHEN datetime(bansferme.date_deban) > CURRENT_TIMESTAMP
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

                            if let Err(error) =
                                result
                            {

                                error!(
                                    "Impossible d'activer le sursis pour {} : {}",
                                    email,
                                    error
                                );

                                return HandlerResult::Response(
                                    Packet::new(
                                        PacketType::LoginResponse,
                                        b"Erreur serveur".to_vec(),
                                    )
                                );
                            }


                            // ----------------------------------------
                            // Supprimer le sursis consommé
                            // ----------------------------------------

                            if let Err(error) =
                                sqlx::query(
                                    r#"
                                    DELETE FROM banssursis

                                    WHERE user_id = ?
                                    "#,
                                )
                                .bind(&login_data.user_id)
                                .execute(&pool)
                                .await
                            {

                                error!(
                                    "Impossible de supprimer le sursis consommé : {}",
                                    error
                                );

                                return HandlerResult::Response(
                                    Packet::new(
                                        PacketType::LoginResponse,
                                        b"Erreur serveur".to_vec(),
                                    )
                                );
                            }


                            debug!(
                                "Sursis de {} jour(s) activé pour {}",
                                jours,
                                email
                            );
                        }


                        // =================================================
                        // PAS DE SURsis
                        // =================================================

                        else {

                            debug!(
                                "Aucun sursis pour {}",
                                email
                            );


                            // --------------------------------------------
                            // Ban automatique de 10 minutes
                            // --------------------------------------------

                            let result =
                                sqlx::query(
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
                                        datetime(
                                            CURRENT_TIMESTAMP,
                                            '+10 minutes'
                                        )
                                    )

                                    ON CONFLICT(user_id)

                                    DO UPDATE SET

                                        auteur =
                                            CASE

                                                WHEN instr(
                                                    COALESCE(
                                                        bansferme.auteur,
                                                        ''
                                                    ),
                                                    'system'
                                                ) = 0

                                                THEN
                                                    CASE

                                                        WHEN COALESCE(
                                                            bansferme.auteur,
                                                            ''
                                                        ) = ''

                                                        THEN 'system'

                                                        ELSE
                                                            bansferme.auteur
                                                            || ', system'

                                                    END

                                                ELSE
                                                    bansferme.auteur

                                            END,


                                        raison =
                                            CASE

                                                WHEN instr(
                                                    COALESCE(
                                                        bansferme.raison,
                                                        ''
                                                    ),
                                                    'Trop de tentatives de connexion échouées'
                                                ) = 0

                                                THEN
                                                    CASE

                                                        WHEN COALESCE(
                                                            bansferme.raison,
                                                            ''
                                                        ) = ''

                                                        THEN
                                                            'Trop de tentatives de connexion échouées'

                                                        ELSE
                                                            bansferme.raison
                                                            || ' | Trop de tentatives de connexion échouées'

                                                    END

                                                ELSE
                                                    bansferme.raison

                                            END,


                                        date_ban =
                                            CURRENT_TIMESTAMP,


                                        date_deban =
                                            CASE

                                                WHEN datetime(
                                                    bansferme.date_deban
                                                ) > CURRENT_TIMESTAMP

                                                THEN
                                                    datetime(
                                                        bansferme.date_deban,
                                                        '+10 minutes'
                                                    )

                                                ELSE
                                                    datetime(
                                                        CURRENT_TIMESTAMP,
                                                        '+10 minutes'
                                                    )

                                            END
                                    "#,
                                )
                                .bind(&login_data.user_id)
                                .execute(&pool)
                                .await;


                            if let Err(error) =
                                result
                            {

                                error!(
                                    "Impossible de créer le ban temporaire : {}",
                                    error
                                );

                                return HandlerResult::Response(
                                    Packet::new(
                                        PacketType::LoginResponse,
                                        b"Erreur serveur".to_vec(),
                                    )
                                );
                            }
                        }
                        debug!(
    "DEBUG BAN : INSERT terminé pour {}",
    login_data.user_id
);

                        // =================================================
                        // RESET DES TENTATIVES
                        // =================================================

                        if let Err(error) =
                            sqlx::query(
                                r#"
                                DELETE FROM login_attempts

                                WHERE user_id = ?
                                "#,
                            )
                            .bind(&login_data.user_id)
                            .execute(&pool)
                            .await
                        {

                            error!(
                                "Impossible de supprimer le compteur : {}",
                                error
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                )
                            );
                        }


                        // =================================================
                        // RÉPONSE
                        // =================================================
                        info!("Utilisateur banni");
                        return HandlerResult::Response(
                            Packet::new(
                                PacketType::LoginResponse,
                                b"Trop de tentatives. Compte bloque temporairement.".to_vec(),
                            )
                        );
                    }


                    // ------------------------------------------------
                    // Moins de 3 tentatives
                    // ------------------------------------------------

                    return HandlerResult::Response(
                        Packet::new(
                            PacketType::LoginResponse,
                            b"Identifiants invalides".to_vec(),
                        )
                    );
                }


                // =================================================
                // MOT DE PASSE CORRECT
                // =================================================

                // ------------------------------------------------
                // Vérifier si déjà connecté
                // ------------------------------------------------

                let is_already_connected =
                    match sqlx::query_scalar::<_, i64>(
                        r#"
                        SELECT EXISTS(
                            SELECT 1

                            FROM users

                            WHERE user_id = ?

                              AND status = 'CONNECTED'
                        )
                        "#,
                    )
                    .bind(&login_data.user_id)
                    .fetch_one(&pool)
                    .await
                    {

                        Ok(value) =>
                            value != 0,

                        Err(error) => {

                            error!(
                                "Erreur lors de la vérification de connexion : {}",
                                error
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::LoginResponse,
                                    b"Erreur serveur".to_vec(),
                                )
                            );
                        }
                    };


                if is_already_connected {

                    debug!(
                        "Tentative de connexion avec un compte déjà connecté"
                    );

                    return HandlerResult::Response(
                        Packet::new(
                            PacketType::LoginResponse,
                            b"Ce compte est deja connecte".to_vec(),
                        )
                    );
                }


                // ------------------------------------------------
                // CONNECTED
                // ------------------------------------------------

                // ------------------------------------------------
// CONNECTED via UserManager
// ------------------------------------------------

match manager
    .set_status(&login_data.user_id, "CONNECTED")
    .await
{
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

// Enregistrer la date de dernière connexion.
if let Err(e) = manager.record_login(&login_data.user_id).await {
    error!("Impossible d'enregistrer la dernière connexion : {}", e);

    // Éviter de laisser l'utilisateur marqué comme connecté.
    if let Err(reset_error) = manager
        .set_status(&login_data.user_id, "DISCONNECTED")
        .await
    {
        error!(
            "Impossible de rétablir le statut DISCONNECTED : {}",
            reset_error
        );
    }

    return HandlerResult::Response(Packet::new(
        PacketType::LoginResponse,
        b"Erreur serveur".to_vec(),
    ));
}


                // ------------------------------------------------
                // Reset login attempts
                // ------------------------------------------------

                if let Err(error) =
                    sqlx::query(
                        r#"
                        DELETE FROM login_attempts

                        WHERE user_id = ?
                        "#,
                    )
                    .bind(&login_data.user_id)
                    .execute(&pool)
                    .await
                {

                    error!(
                        "Impossible de réinitialiser les tentatives : {}",
                        error
                    );

                    return HandlerResult::Response(
                        Packet::new(
                            PacketType::LoginResponse,
                            b"Erreur serveur".to_vec(),
                        )
                    );
                }


                // ------------------------------------------------
                // Login réussi
                // ------------------------------------------------

                debug!(
                    "Utilisateur authentifié : {}",
                    email
                );


                client.set_user_id(
                    Some(
                        login_data.user_id.clone()
                    )
                );


                HandlerResult::Response(
                    Packet::new(
                        PacketType::LoginResponse,
                        format!(
                            "Utilisateur {} authentifié",
                            email
                        )
                        .into_bytes(),
                    )
                )
            }


            // =================================================
            // CHAT
            // =================================================

            PacketType::Chat => {

                debug!(
                    "Message : {}",
                    String::from_utf8_lossy(
                        &packet.payload
                    )
                );

                HandlerResult::Response(
                    Packet::new(
                        PacketType::Chat,
                        packet.payload,
                    )
                )
            }


            // =================================================
            // MOVE
            // =================================================

           PacketType::Move => {
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

    world
        .set_position(player_id, position)
        .await;

    world.broadcast_player_state(
        player_id,
        position,
    );

    HandlerResult::Nothing
}
            PacketType::DECO => {

    info!(
        "Demande de déconnexion reçue"
    );

    HandlerResult::Disconnect
}
PacketType::MarketBuy => {

    if packet.payload.len() != 24 {

        error!(
            "MARKET_BUY : payload invalide ({} octets)",
            packet.payload.len()
        );

        return HandlerResult::Response(
            Packet::new(
                PacketType::MarketBuy,
                b"MARKET_BUY invalide".to_vec(),
            )
        );
    }


    let objet_id =
        match Self::read_i64(
            &packet.payload,
            0,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketBuy,
                        b"MARKET_BUY invalide".to_vec(),
                    )
                );
            }
        };


    let quantity =
        match Self::read_u64(
            &packet.payload,
            8,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketBuy,
                        b"MARKET_BUY invalide".to_vec(),
                    )
                );
            }
        };


    let prix_unitaire_max =
        match Self::read_i64(
            &packet.payload,
            16,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketBuy,
                        b"MARKET_BUY invalide".to_vec(),
                    )
                );
            }
        };


    let account_id =
        match client.account_id() {

            Some(id) => id,

            None => {

                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketBuy,
                        b"Compte non selectionne".to_vec(),
                    )
                );
            }
        };


    let market =
        MarketManager::new(
            pool.clone()
        );


    match market.creer_ordre_achat(
        account_id,
        objet_id,
        quantity,
        prix_unitaire_max,
    ).await {

        Ok(ordre_id) => {

            info!(
                "Ordre d'achat {} créé |objet={} quantité={} prix_max={}",
                ordre_id,
                objet_id,
                quantity,
                prix_unitaire_max
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketBuy,
                    ordre_id
                        .to_be_bytes()
                        .to_vec(),
                )
            )
        }


        Err(e) => {

            error!(
                "Erreur création ordre d'achat : {}",
                e
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketBuy,
                    format!(
                        "Erreur: {}",
                        e
                    )
                    .into_bytes(),
                )
            )
        }
    }
}

            // ================================================
            // LISTE DES COMPTES
            // ================================================
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
                        let payload =
                            serde_json::to_vec(&accounts).unwrap_or_else(|_| b"[]".to_vec());

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

            // ================================================
            // CRÉATION D'UN COMPTE JOUEUR
            // ================================================
            PacketType::AccountCreate => {
                let user_id = match client.user_id() {
                    Some(id) => id.to_string(),
                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{"ok":false,"message":"Utilisateur non authentifie"}"#.to_vec(),
                        ));
                    }
                };

                let account_name = match std::str::from_utf8(&packet.payload) {
                    Ok(name) => name,
                    Err(_) => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{"ok":false,"message":"Nom de compte invalide"}"#.to_vec(),
                        ));
                    }
                };

                let manager = AccountManager::new(pool.clone());

                match manager.create_account(&user_id, account_name).await {
                    Ok(account) => {
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

            // ================================================
            // SÉLECTION D'UN COMPTE
            // ================================================
            PacketType::AccountSelect => {
                if packet.payload.len() != 8 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::AccountResult,
                        br#"{"ok":false,"message":"Identifiant invalide"}"#.to_vec(),
                    ));
                }

                let account_id = i64::from_be_bytes(
                    packet.payload[..8].try_into().unwrap()
                );

                if account_id <= 0 {
                    return HandlerResult::Response(Packet::new(
                        PacketType::AccountResult,
                        br#"{"ok":false,"message":"Identifiant invalide"}"#.to_vec(),
                    ));
                }

                let user_id = match client.user_id() {
                    Some(id) => id.to_string(),
                    None => {
                        return HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{"ok":false,"message":"Utilisateur non authentifie"}"#.to_vec(),
                        ));
                    }
                };

                let manager = AccountManager::new(pool.clone());

                match manager.account_belongs_to_user(account_id, &user_id).await {
                    Ok(true) => {
                        client.set_account_id(Some(account_id));

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
                            r#"{"ok":false,"message":"Compte introuvable ou non autorisé"}"#.as_bytes().to_vec(),
                        ))
                    }
                    Err(e) => {
                        error!("Erreur de vérification du compte : {}", e);

                        HandlerResult::Response(Packet::new(
                            PacketType::AccountResult,
                            br#"{"ok":false,"message":"Erreur serveur"}"#.to_vec(),
                        ))
                    }
                }
            }

            PacketType::MarketSell => {

    if packet.payload.len() != 24 {

        error!(
            "MARKET_SELL : payload invalide ({} octets)",
            packet.payload.len()
        );

        return HandlerResult::Response(
            Packet::new(
                PacketType::MarketSell,
                b"MARKET_SELL invalide".to_vec(),
            )
        );
    }


    let objet_id =
        match Self::read_i64(
            &packet.payload,
            0,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketSell,
                        b"MARKET_SELL invalide".to_vec(),
                    )
                );
            }
        };


    let quantity =
        match Self::read_u64(
            &packet.payload,
            8,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketSell,
                        b"MARKET_SELL invalide".to_vec(),
                    )
                );
            }
        };


    let prix_unitaire =
        match Self::read_i64(
            &packet.payload,
            16,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketSell,
                        b"MARKET_SELL invalide".to_vec(),
                    )
                );
            }
        };


    let account_id =
        match client.account_id() {

            Some(id) => id,

            None => {

                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketSell,
                        b"Compte non selectionne".to_vec(),
                    )
                );
            }
        };


    let market =
        MarketManager::new(
            pool.clone()
        );


    match market.creer_ordre_vente(
        account_id,
        objet_id,
        quantity,
        prix_unitaire,
    ).await {

        Ok(ordre_id) => {

            info!(
                "Ordre de vente {} créé | objet={} quantité={} prix={}",
                ordre_id,
                objet_id,
                quantity,
                prix_unitaire
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketSell,
                    ordre_id
                        .to_be_bytes()
                        .to_vec(),
                )
            )
        }


        Err(e) => {

            error!(
                "Erreur création ordre de vente : {}",
                e
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketSell,
                    format!(
                        "Erreur: {}",
                        e
                    )
                    .into_bytes(),
                )
            )
        }
    }
}
            PacketType::MarketCancelBuy => {

    if packet.payload.len() != 8 {

        return HandlerResult::Response(
            Packet::new(
                PacketType::MarketCancelBuy,
                b"MARKET_CANCEL_BUY invalide".to_vec(),
            )
        );
    }


    let ordre_id =
        match Self::read_i64(
            &packet.payload,
            0,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketCancelBuy,
                        b"MARKET_CANCEL_BUY invalide".to_vec(),
                    )
                );
            }
        };


    let account_id =
        match client.account_id() {

            Some(id) => id,

            None => {

                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketCancelBuy,
                        b"Compte non selectionne".to_vec(),
                    )
                );
            }
        };


    let market =
        MarketManager::new(
            pool.clone()
        );


    match market.annuler_ordre_achat(
        account_id,
        ordre_id,
    ).await {

        Ok(()) => {

            info!(
                "Ordre d'achat {} annulé",
                ordre_id
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketCancelBuy,
                    ordre_id
                        .to_be_bytes()
                        .to_vec(),
                )
            )
        }


        Err(e) => {

            error!(
                "Erreur annulation ordre d'achat {} : {}",
                ordre_id,
                e
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketCancelBuy,
                    format!(
                        "Erreur: {}",
                        e
                    )
                    .into_bytes(),
                )
            )
        }
    }
}
            PacketType::MarketCancelSell => {

    if packet.payload.len() != 8 {

        return HandlerResult::Response(
            Packet::new(
                PacketType::MarketCancelSell,
                b"MARKET_CANCEL_SELL invalide".to_vec(),
            )
        );
    }


    let ordre_id =
        match Self::read_i64(
            &packet.payload,
            0,
        ) {
            Some(value) => value,

            None => {
                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketCancelSell,
                        b"MARKET_CANCEL_SELL invalide".to_vec(),
                    )
                );
            }
        };


    let account_id =
        match client.account_id() {

            Some(id) => id,

            None => {

                return HandlerResult::Response(
                    Packet::new(
                        PacketType::MarketCancelSell,
                        b"Compte non selectionne".to_vec(),
                    )
                );
            }
        };


    let market =
        MarketManager::new(
            pool.clone()
        );


    match market.annuler_ordre_vente(
        account_id,
        ordre_id,
    ).await {

        Ok(()) => {

            info!(
                "Ordre de vente {} annulé",
                ordre_id
                
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketCancelSell,
                    ordre_id
                        .to_be_bytes()
                        .to_vec(),
                )
            )
        }


        Err(e) => {

            error!(
                "Erreur annulation ordre de vente {} : {}",
                ordre_id,
                e
            );


            HandlerResult::Response(
                Packet::new(
                    PacketType::MarketCancelSell,
                    format!(
                        "Erreur: {}",
                        e
                    )
                    .into_bytes(),
                )
            )
        }
    }
}

            // =================================================
            // Réponses interdites venant du client
            // =================================================

            PacketType::LoginResponse
            | PacketType::SignUpResponse 
            | PacketType::PlayerState 
            | PacketType::PlayerRemove
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
