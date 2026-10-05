use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::{
    broadcast,
    RwLock,
};

use uuid::Uuid;

use crate::network::packet::Packet;

#[derive(Clone)]
pub struct PlayerState {

    pub position: (i32, i32, i32),
}


#[derive(Clone)]
pub struct World {

    players:
        Arc<RwLock<HashMap<Uuid, PlayerState>>>,

    broadcast:
        broadcast::Sender<Packet>,
}


impl World {

    pub fn new() -> Self {

        let (broadcast, _) =
            broadcast::channel(256);

        Self {

            players:
                Arc::new(
                    RwLock::new(
                        HashMap::new()
                    )
                ),

            broadcast,
        }
    }


    pub fn subscribe(
        &self,
    ) -> broadcast::Receiver<Packet> {

        self.broadcast.subscribe()
    }


    pub fn sender(
        &self,
    ) -> broadcast::Sender<Packet> {

        self.broadcast.clone()
    }


    pub async fn set_position(
        &self,
        player_id: Uuid,
        x: i32,
        y: i32,
        z: i32,
    ) {

        let mut players =
            self.players.write().await;

        players.insert(
            player_id,
            PlayerState {
                position: (x, y, z),
            },
        );
    }


    pub async fn remove_player(
        &self,
        player_id: Uuid,
    ) {

        let mut players =
            self.players.write().await;

        players.remove(&player_id);
    }


    pub async fn snapshot(
        &self,
    ) -> Vec<(Uuid, PlayerState)> {

        let players =
            self.players.read().await;

        players
            .iter()
            .map(
                |(id, state)| {
                    (*id, state.clone())
                }
            )
            .collect()
    }


    pub fn broadcast(
        &self,
        packet: Packet,
    ) {

        let _ =
            self.broadcast.send(packet);
    }
}