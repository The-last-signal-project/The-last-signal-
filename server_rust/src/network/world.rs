use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::{broadcast, Mutex};
use uuid::Uuid;

use crate::network::packet::{Packet, PacketType};

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

#[derive(Clone)]
pub struct World {
    pub positions: Arc<Mutex<HashMap<Uuid, Position>>>,
    pub tx: broadcast::Sender<Packet>,
}

impl World {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(256);

        Self {
            positions: Arc::new(Mutex::new(HashMap::new())),
            tx,
        }
    }

    pub fn subscribe(&self) -> broadcast::Receiver<Packet> {
        self.tx.subscribe()
    }

    pub fn sender(&self) -> broadcast::Sender<Packet> {
        self.tx.clone()
    }

    pub async fn set_position(&self, player_id: Uuid, position: Position) {
        let mut positions = self.positions.lock().await;
        positions.insert(player_id, position);
    }

    pub async fn remove_player(&self, player_id: Uuid) {
        let mut positions = self.positions.lock().await;
        positions.remove(&player_id);
    }

    pub async fn get_position(&self, player_id: Uuid) -> Option<Position> {
        let positions = self.positions.lock().await;
        positions.get(&player_id).copied()
    }

    pub async fn snapshot(&self) -> Vec<(Uuid, Position)> {
        let positions = self.positions.lock().await;

        positions
            .iter()
            .map(|(id, position)| (*id, *position))
            .collect()
    }

    pub fn broadcast_player_state(
        &self,
        player_id: Uuid,
        position: Position,
    ) {
        let mut payload = Vec::with_capacity(28);

        payload.extend_from_slice(player_id.as_bytes());
        payload.extend_from_slice(&position.x.to_be_bytes());
        payload.extend_from_slice(&position.y.to_be_bytes());
        payload.extend_from_slice(&position.z.to_be_bytes());

        let packet = Packet::new(
            PacketType::PlayerState,
            payload,
        );

        let _ = self.tx.send(packet);
    }

    pub fn broadcast_player_remove(&self, player_id: Uuid) {
        let packet = Packet::new(
            PacketType::PlayerRemove,
            player_id.as_bytes().to_vec(),
        );

        let _ = self.tx.send(packet);
    }
}

impl Default for World {
    fn default() -> Self {
        Self::new()
    }
}