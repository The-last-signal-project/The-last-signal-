use std::collections::HashMap;
use std::sync::Arc;

use log::{error, info};
use tokio::sync::{broadcast, Mutex};
use uuid::Uuid;

use crate::network::packet::{Packet, PacketType};
use crate::world::treasure_zone::{move_allowed, Rect, ZoneState};

#[derive(Debug, Clone, Copy)]
pub struct Position {
    pub x: i32,
    pub y: i32,
    pub z: i32,
}

impl Position {
    pub fn new(x: i32, y: i32, z: i32) -> Self {
        Self { x, y, z }
    }
}

/// Résultat d'un déplacement accepté par `World::try_move`.
#[derive(Debug, Clone, Copy)]
pub struct MoveAccepted {
    pub position: Position,
    /// Niveau (1 à 5) du coffre à ouvrir si le joueur vient de prendre le trésor.
    pub treasure_won: Option<u32>,
}

#[derive(Clone)]
pub struct World {
    pub positions: Arc<Mutex<HashMap<Uuid, Position>>>,
    pub tx: broadcast::Sender<Packet>,
    /// Clé, porte et trésor (état partagé, autoritaire).
    pub zone: Arc<Mutex<ZoneState>>,
}

impl World {
    // =============================================================
    // CRÉATION
    // =============================================================

    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(256);

        Self {
            positions: Arc::new(Mutex::new(HashMap::new())),
            tx,
            zone: Arc::new(Mutex::new(ZoneState::new())),
        }
    }

    // =============================================================
    // BROADCAST
    // =============================================================

    pub fn subscribe(&self) -> broadcast::Receiver<Packet> {
        self.tx.subscribe()
    }

    pub fn sender(&self) -> broadcast::Sender<Packet> {
        self.tx.clone()
    }

    // =============================================================
    // POSITIONS
    // =============================================================

    pub async fn set_position(
        &self,
        player_id: Uuid,
        position: Position,
    ) {
        let mut positions = self.positions.lock().await;

        positions.insert(
            player_id,
            position,
        );

        info!(
            "WORLD: position enregistrée | \
             x={} y={} z={}",
            
            position.x,
            position.y,
            position.z
        );
    }

    pub async fn remove_player(
        &self,
        player_id: Uuid,
    ) {
        {
            let mut positions = self.positions.lock().await;

            if positions.remove(&player_id).is_some() {
                info!(
                    "WORLD: joueur supprimé"
                );
            }
        }

        // Si le joueur portait la clé (ou le trésor), la manche repart.
        // Le verrou des positions est relâché avant de prendre celui de la zone.
        let zone_packet = {
            let mut zone = self.zone.lock().await;

            if zone.on_player_left(player_id) {
                Some(zone.packet())
            } else {
                None
            }
        };

        if let Some(packet) = zone_packet {
            let _ = self.tx.send(packet);
        }
    }

    // =============================================================
    // DÉPLACEMENT VALIDÉ + CLÉ / TRÉSOR
    // =============================================================

    /// Valide un MOVE (limites, murs, porte, pas de téléportation).
    ///
    /// - `Ok(MoveAccepted)` : accepté, enregistré et diffusé (ainsi que le
    ///   nouvel état de la zone si une clé/un trésor a été pris).
    ///   `treasure_won` contient le niveau du coffre à ouvrir pour ce joueur
    ///   s'il vient de prendre le trésor (à traiter APRÈS, sans verrou).
    /// - `Err(position)` : refusé ; c'est la dernière position valide,
    ///   à renvoyer au seul joueur fautif pour qu'il se recale.
    ///
    /// Ordre des verrous : zone, puis positions (jamais l'inverse).
    pub async fn try_move(
        &self,
        player_id: Uuid,
        requested: Position,
    ) -> Result<MoveAccepted, Position> {
        let mut zone = self.zone.lock().await;

        let previous = self.get_position(player_id).await;

        if !move_allowed(&zone, player_id, previous, requested) {
            return Err(previous.unwrap_or(Position::new(0, 0, 0)));
        }

        self.set_position(player_id, requested).await;

        let rect = Rect::player(requested);

        let effect = zone.apply_move(player_id, rect, requested);

        let zone_packet = if effect.changed {
            Some(zone.packet())
        } else {
            None
        };

        drop(zone);

        self.broadcast_player_state(player_id, requested);

        if let Some(packet) = zone_packet {
            let _ = self.tx.send(packet);
        }

        Ok(MoveAccepted {
            position: requested,
            treasure_won: effect.treasure_won,
        })
    }

    /// État courant de la zone (envoyé à un joueur qui se connecte).
    pub async fn zone_state_packet(&self) -> Packet {
        self.zone.lock().await.packet()
    }

    pub async fn get_position(
        &self,
        player_id: Uuid,
    ) -> Option<Position> {
        let positions = self.positions.lock().await;

        positions
            .get(&player_id)
            .copied()
    }

    pub async fn snapshot(
        &self,
    ) -> Vec<(Uuid, Position)> {
        let positions = self.positions.lock().await;

        positions
            .iter()
            .map(|(id, position)| {
                (*id, *position)
            })
            .collect()
    }

    // =============================================================
    // PACKET PLAYER_STATE
    // =============================================================

    pub fn player_state_packet(
        player_id: Uuid,
        position: Position,
    ) -> Packet {
        let mut payload = Vec::with_capacity(28);

        // UUID = 16 octets
        payload.extend_from_slice(
            player_id.as_bytes()
        );

        // x = 4 octets
        payload.extend_from_slice(
            &position.x.to_be_bytes()
        );

        // y = 4 octets
        payload.extend_from_slice(
            &position.y.to_be_bytes()
        );

        // z = 4 octets
        payload.extend_from_slice(
            &position.z.to_be_bytes()
        );

        debug_assert_eq!(
            payload.len(),
            28
        );

        Packet::new(
            PacketType::PlayerState,
            payload,
        )
    }

    // =============================================================
    // BROADCAST PLAYER_STATE
    // =============================================================

    pub fn broadcast_player_state(
        &self,
        player_id: Uuid,
        position: Position,
    ) {
        let packet = Self::player_state_packet(
            player_id,
            position,
        );

        match self.tx.send(packet) {
            Ok(receiver_count) => {
                info!(
                    "WORLD: PLAYER_STATE broadcasté | \
                      x={} y={} z={} | \
                     récepteurs={}",
                    
                    position.x,
                    position.y,
                    position.z,
                    receiver_count
                );
            }

            Err(error) => {
                error!(
                    "WORLD: échec du broadcast PLAYER_STATE | \
                      erreur={}",
                    
                    error
                );
            }
        }
    }

    // =============================================================
    // PACKET PLAYER_REMOVE
    // =============================================================

    pub fn player_remove_packet(
        player_id: Uuid,
    ) -> Packet {
        Packet::new(
            PacketType::PlayerRemove,
            player_id.as_bytes().to_vec(),
        )
    }

    // =============================================================
    // BROADCAST PLAYER_REMOVE
    // =============================================================

    pub fn broadcast_player_remove(
        &self,
        player_id: Uuid,
    ) {
        let packet = Self::player_remove_packet(
            player_id
        );

        match self.tx.send(packet) {
            Ok(receiver_count) => {
                info!(
                    "WORLD: PLAYER_REMOVE broadcasté | \
                     récepteurs={}",
                    receiver_count
                );
            }

            Err(error) => {
                error!(
                    "WORLD: échec du broadcast PLAYER_REMOVE | \
                     erreur={}",
                    error
                );
            }
        }
    }
}

impl Default for World {
    fn default() -> Self {
        Self::new()
    }
}
