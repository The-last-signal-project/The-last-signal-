use crate::network::{parser::{
    parse_login_payload,
    parse_signup_payload,},packet::{
    Packet,
    PacketType,
    LogLevel,
    ClientLog,},client::Client
    
};

use crate::network::world::World;
use crate::gameplay::market_manager::MarketManager;


use crate::auth::password::{
    verify_password,
    hash_password,
};

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

use uuid::Uuid;


// ============================================================
// Structures
// ============================================================

pub struct User {
    user_id: String,
    password_hash: String,
}


struct LoginData {
    user_id: String,
    password_hash: String,
    is_banned_perm: bool,
    is_banned_temp: bool,
}

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

                // ------------------------------------------------
                // Parser
                // ------------------------------------------------

                let (email, password) =
                    match parse_signup_payload(
                        &packet.payload
                    ) {

                        Ok(signup) => signup,

                        Err(error) => {

                            debug!(
                                "SIGN_UP invalide : {}",
                                error
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::SignUpResponse,
                                    b"SIGN_UP invalide".to_vec(),
                                )
                            );
                        }
                    };


                // ------------------------------------------------
                // Hash Argon2
                // ------------------------------------------------

                let password_hash =
                    match hash_password(&password) {

                        Ok(hash) => hash,

                        Err(error) => {

                            error!(
                                "Erreur lors du hash du mot de passe : {}",
                                error
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::SignUpResponse,
                                    b"Erreur serveur".to_vec(),
                                )
                            );
                        }
                    };


                // ------------------------------------------------
                // UUID
                // ------------------------------------------------

                let user_id =
                    Uuid::new_v4().to_string();


                // ------------------------------------------------
                // Création utilisateur
                // ------------------------------------------------

                match sqlx::query(
                    r#"
                    INSERT INTO users (
                        user_id,
                        email,
                        password_hash
                    )
                    VALUES (?, ?, ?)
                    "#,
                )
                .bind(&user_id)
                .bind(&email)
                .bind(&password_hash)
                .execute(&pool)
                .await
                {

                    Ok(_) => {

                        debug!(
                            "Nouvel utilisateur créé : {}",
                            email
                        );

                        client.set_user_id(
                            Some(user_id.clone())
                        );

                        HandlerResult::Response(
                            Packet::new(
                                PacketType::SignUpResponse,
                                b"Utilisateur cree avec succes".to_vec(),
                            )
                        )
                    }


                    Err(error) => {

                        let error_msg =
                            error.to_string();


                        if error_msg.contains(
                            "UNIQUE constraint failed"
                        ) {

                            debug!(
                                "SIGN_UP refusé : email déjà utilisé"
                            );

                            HandlerResult::Response(
                                Packet::new(
                                    PacketType::SignUpResponse,
                                    b"Email deja utilise".to_vec(),
                                )
                            )

                        } else {

                            error!(
                                "Erreur lors de la création du user : {}",
                                error
                            );

                            HandlerResult::Response(
                                Packet::new(
                                    PacketType::SignUpResponse,
                                    b"Erreur serveur".to_vec(),
                                )
                            )
                        }
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
                // Récupération utilisateur + bans
                // ------------------------------------------------

                let login_data =
                    match sqlx::query(
                        r#"
                        SELECT
                            u.user_id,
                            u.password_hash,

                            COALESCE(
                                (
                                    SELECT EXISTS(
                                        SELECT 1
                                        FROM bansperm
                                        WHERE user_id = u.user_id
                                    )
                                ),
                                0
                            ) AS is_banned_perm,

                            COALESCE(
                                (
                                    SELECT EXISTS(
                                        SELECT 1
                                        FROM bansferme
                                        WHERE user_id = u.user_id
                                          AND datetime(date_deban)
                                              > CURRENT_TIMESTAMP
                                    )
                                ),
                                0
                            ) AS is_banned_temp

                        FROM users u

                        WHERE u.email = ?
                        "#,
                    )
                    .bind(&email)
                    .fetch_optional(&pool)
                    .await
                    {

                        Ok(Some(row)) => {

                            LoginData {

                                user_id:
                                    row.get::<String, _>(
                                        "user_id"
                                    ),

                                password_hash:
                                    row.get::<String, _>(
                                        "password_hash"
                                    ),

                                is_banned_perm:
                                    row.get::<i64, _>(
                                        "is_banned_perm"
                                    ) != 0,

                                is_banned_temp:
                                    row.get::<i64, _>(
                                        "is_banned_temp"
                                    ) != 0,
                            }
                        }


                        Ok(None) => {

                            debug!(
                                "Tentative de connexion avec un utilisateur inexistant"
                            );

                            return HandlerResult::Response(
                                Packet::new(
                                    PacketType::LoginResponse,
                                    b"Identifiants invalides".to_vec(),
                                )
                            );
                        }


                        Err(error) => {

                            error!(
                                "Erreur lors de la recherche de l'utilisateur : {}",
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

                if let Err(error) =
                    sqlx::query(
                        r#"
                        UPDATE users

                        SET status = 'CONNECTED'

                        WHERE user_id = ?
                        "#,
                    )
                    .bind(&login_data.user_id)
                    .execute(&pool)
                    .await
                {

                    error!(
                        "Erreur lors de la connexion du joueur : {}",
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

        error!(
            "MOVE invalide : {} octets",
            packet.payload.len()
        );

        return HandlerResult::Nothing;
    }


    let x =
        i32::from_be_bytes(
            packet.payload[0..4]
                .try_into()
                .unwrap()
        );

    let y =
        i32::from_be_bytes(
            packet.payload[4..8]
                .try_into()
                .unwrap()
        );

    let z =
        i32::from_be_bytes(
            packet.payload[8..12]
                .try_into()
                .unwrap()
        );


    let player_id =
        client.session_id();


    debug!(
        "Déplacement [{}] : ({}, {}, {})",
        player_id,
        x,
        y,
        z
    );


    world
        .set_position(
            player_id,
            x,
            y,
            z,
        )
        .await;


    let mut payload =
        Vec::with_capacity(28);


    payload.extend_from_slice(
        player_id
            .as_bytes()
    );

    payload.extend_from_slice(
        &x.to_be_bytes()
    );

    payload.extend_from_slice(
        &y.to_be_bytes()
    );

    payload.extend_from_slice(
        &z.to_be_bytes()
    );


    world.broadcast(
        Packet::new(
            PacketType::PlayerState,
            payload,
        )
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
            | PacketType::SignUpResponse => {

                error!(
                    "Réponse reçue du client alors qu'elle doit être envoyée par le serveur : {:?}",
                    packet.packet_type
                );

                HandlerResult::Nothing
            }
        }
    }
}
