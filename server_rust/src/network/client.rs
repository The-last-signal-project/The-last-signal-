use tokio::{
    io::AsyncWriteExt,
    net::TcpStream,
    time::{interval, Duration},
};

use sqlx::SqlitePool;
use uuid::Uuid;

use log::{
    debug,
    error,
    info,
};

use crate::network::handler::{PacketHandler,HandlerResult};

use crate::network::packet::{
    receive_packet,
    send_packet,
    BanInfo,
    BanType,
    Packet,
    PacketType,
};


pub struct Client {

    stream: TcpStream,

    pool: SqlitePool,

    session_id: Uuid,

    client_id: Option<i64>,

    user_id: Option<String>,

    account_id: Option<i64>,
}


impl Client {

    // ============================================================
    // CONSTRUCTEUR
    // ============================================================

    pub fn new(
        stream: TcpStream,
        pool: SqlitePool,
    ) -> Self {

        Self {
            stream,

            pool,

            session_id: Uuid::new_v4(),

            client_id: None,

            user_id: None,

            account_id: None,
        }
    }


    // ============================================================
    // BOUCLE PRINCIPALE
    // ============================================================

    pub async fn run(&mut self) {

        let peer = self
            .stream
            .peer_addr()
            .map(|addr| addr.to_string())
            .unwrap_or_else(|_| "adresse inconnue".to_string());


        info!(
            "Client connecté : {} | Session : {}",
            peer,
            self.session_id
        );


        // --------------------------------------------------------
        // Timer de vérification du ban
        // --------------------------------------------------------

        let mut ban_checker =
            interval(Duration::from_secs(1));


        // interval() déclenche immédiatement son premier tick.
        //
        // On le consomme donc ici pour que la première véritable
        // vérification ait lieu après 1 seconde.
        ban_checker.tick().await;


        // ========================================================
        // BOUCLE
        // ========================================================

        loop {

            tokio::select! {

                // =================================================
                // RÉCEPTION DES PAQUETS
                // =================================================

                packet = receive_packet(
                    &mut self.stream
                ) => {

                    match packet {

                        Ok(packet) => {

                            debug!(
                                "[{}] Paquet reçu : {:?}",
                                self.session_id,
                                packet.packet_type
                            );


                            debug!(
                                "[{}] Payload : {}",
                                self.session_id,
                                String::from_utf8_lossy(
                                    &packet.payload
                                )
                            );


                            // -----------------------------------------
                            // Traitement du paquet
                            // -----------------------------------------
                            match PacketHandler::handle(
    self,
    packet,
    self.pool.clone()
).await {

    HandlerResult::Response(response) => {

        if let Err(e) =
            send_packet(
                &mut self.stream,
                &response
            ).await
        {
            error!(
                "Erreur d'envoi  : {}",
                
                e
            );

            break;
        }
    }

    HandlerResult::Disconnect => {

        self.disconnect().await;

        break;
    }

    HandlerResult::Nothing => {
        // Aucun paquet de réponse.
    }
}
                            
                        }


                        // ---------------------------------------------
                        // Erreur / déconnexion du client
                        // ---------------------------------------------

                        Err(e) => {

                            debug!(
                                "Déconnexion du client [{}] : {}",
                                self.session_id,
                                e
                            );

                            break;
                        }
                    }
                }


                // =================================================
                // VÉRIFICATION DU BAN
                // =================================================

                _ = ban_checker.tick() => {

                    // ---------------------------------------------
                    // Aucun utilisateur authentifié
                    // ---------------------------------------------
                    //
                    // Il n'y a aucun intérêt à vérifier les bans
                    // si le client n'est pas encore connecté.
                    //
                    // ---------------------------------------------

                    if self.user_id.is_none() {
                        continue;
                    }


                    // ---------------------------------------------
                    // Recherche d'un ban actif
                    // ---------------------------------------------

                    match self.get_ban_info().await {

                        Ok(Some(ban)) => {

                            info!(
                                "Ban détecté [{}] | Type : {:?} | Raison : {}",
                                self.session_id,
                                ban.ban_type,
                                ban.reason
                            );


                            // -----------------------------------------
                            // Création du paquet BAN
                            // -----------------------------------------

                            let payload =
                                Self::encode_ban_payload(
                                    &ban
                                );


                            let packet =
                                Packet::new(
                                    PacketType::BAN,
                                    payload
                                );


                            // -----------------------------------------
                            // Envoi du BAN
                            // -----------------------------------------

                            match send_packet(
                                &mut self.stream,
                                &packet
                            ).await {

                                Ok(()) => {

                                    info!(
                                        "Paquet BAN envoyé [{}]",
                                        self.session_id
                                    );
                                }


                                Err(e) => {

                                    error!(
                                        "Impossible d'envoyer le BAN [{}] : {}",
                                        self.session_id,
                                        e
                                    );
                                }
                            }


                            // -----------------------------------------
                            // Déconnexion
                            // -----------------------------------------

                            self.disconnect().await;

                            break;
                        }


                        // ---------------------------------------------
                        // Aucun ban
                        // ---------------------------------------------

                        Ok(None) => {

                            // Rien à faire.
                        }


                        // ---------------------------------------------
                        // Erreur SQL
                        // ---------------------------------------------

                        Err(e) => {

                            error!(
                                "Erreur lors de la vérification du ban [{}] : {}",
                                self.session_id,
                                e
                            );

                            break;
                        }
                    }
                }
            }
        }


        // ========================================================
        // FIN DE SESSION
        // ========================================================

        self.mark_disconnected().await;


        info!(
            "Fin de session : {}",
            self.session_id
        );
    }


    // ============================================================
    // RÉCUPÉRATION DES INFORMATIONS DE BAN
    // ============================================================

    pub async fn get_ban_info(
        &self,
    ) -> Result<Option<BanInfo>, sqlx::Error> {

        let user_id =
            match self.user_id() {

                Some(id) => id,

                None => {
                    return Ok(None);
                }
            };


        // ========================================================
        // BAN PERMANENT
        // ========================================================

        if let Some((reason,)) =
            sqlx::query_as::<_, (Option<String>,)>(
                r#"
                SELECT raison
                FROM bansperm
                WHERE user_id = ?
                LIMIT 1
                "#
            )
            .bind(user_id)
            .fetch_optional(&self.pool)
            .await?
        {

            return Ok(Some(
                BanInfo {

                    ban_type:
                        BanType::Permanent,

                    reason:
                        reason.unwrap_or_else(
                            || "Aucune raison fournie".to_string()
                        ),

                    date_deban:
                        None,
                }
            ));
        }


        // ========================================================
        // BAN TEMPORAIRE
        // ========================================================

        if let Some((reason, date_deban)) =
            sqlx::query_as::<_, (Option<String>, String)>(
                r#"
                SELECT
                    raison,
                    date_deban

                FROM bansferme

                WHERE user_id = ?

                  AND datetime(date_deban)
                      > CURRENT_TIMESTAMP

                LIMIT 1
                "#
            )
            .bind(user_id)
            .fetch_optional(&self.pool)
            .await?
        {

            return Ok(Some(
                BanInfo {

                    ban_type:
                        BanType::Temporary,

                    reason:
                        reason.unwrap_or_else(
                            || "Aucune raison fournie".to_string()
                        ),

                    date_deban:
                        Some(date_deban),
                }
            ));
        }


        // ========================================================
        // PAS DE BAN
        // ========================================================

        Ok(None)
    }


    // ============================================================
    // ENCODAGE DU PAQUET BAN
    // ============================================================

    fn encode_ban_payload(
        ban: &BanInfo,
    ) -> Vec<u8> {

        format!(
            "{}\0{}\0{}",
            ban.ban_type as u8,

            ban.reason,

            ban.date_deban
                .as_deref()
                .unwrap_or("")
        )
        .into_bytes()
    }


    // ============================================================
    // MARQUER COMME DÉCONNECTÉ
    // ============================================================

    async fn mark_disconnected(
        &self,
    ) {

        let user_id =
            match self.user_id() {

                Some(id) => id,

                None => return,
            };


        if let Err(e) =
            sqlx::query(
                r#"
                UPDATE users

                SET status = 'DISCONNECTED'

                WHERE user_id = ?

                  AND status = 'CONNECTED'
                "#
            )
            .bind(user_id)
            .execute(&self.pool)
            .await
        {

            error!(
                "Impossible de mettre le joueur {} en DISCONNECTED [{}] : {}",
                user_id,
                self.session_id,
                e
            );

            return;
        }


        debug!(
            "Utilisateur {} marqué comme DISCONNECTED [{}]",
            user_id,
            self.session_id
        );
    }


    // ============================================================
    // SET USER ID
    // ============================================================

    pub fn set_user_id(
        &mut self,
        id: Option<String>,
    ) {

        self.user_id = id;
    }


    // ============================================================
    // GET USER ID
    // ============================================================

    pub fn user_id(
        &self,
    ) -> Option<&str> {

        self.user_id
            .as_deref()
    }


    // ============================================================
    // SET CLIENT ID
    // ============================================================

    pub fn set_client_id(
        &mut self,
        id: Option<i64>,
    ) {

        self.client_id = id;
    }


    // ============================================================
    // GET CLIENT ID
    // ============================================================

    pub fn client_id(
        &self,
    ) -> Option<i64> {

        self.client_id
    }


    // ============================================================
    // SET ACCOUNT ID
    // ============================================================

    pub fn set_account_id(
        &mut self,
        id: Option<i64>,
    ) {

        self.account_id = id;
    }


    // ============================================================
    // GET ACCOUNT ID
    // ============================================================

    pub fn account_id(
        &self,
    ) -> Option<i64> {

        self.account_id
    }


    // ============================================================
    // DÉCONNEXION
    // ============================================================

    pub async fn disconnect(
        &mut self,
    ) {

        // --------------------------------------------------------
        // Mettre le compte hors ligne AVANT de fermer le socket
        // --------------------------------------------------------

        self.mark_disconnected().await;


        // --------------------------------------------------------
        // Fermeture du socket
        // --------------------------------------------------------

        if let Err(e) =
            self.stream.shutdown().await
        {

            error!(
                "Erreur lors de la déconnexion : {}",
                
                e
            );
        }
        else {

            info!(
                "Client déconnecté",
                
            );
        }
    }
}
