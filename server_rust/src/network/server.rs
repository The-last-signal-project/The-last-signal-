use tokio::net::TcpListener;
use tokio::task;
use log::{
    info,
    error,
    debug,
};
use crate::auth::user_manager::UserManager;
use crate::database::database_manager::DatabaseManager;
use crate::network::client::Client;
use crate::world::world::World;
pub struct Server {
    listener: TcpListener,
    database: DatabaseManager,
    world: World,
}

impl Server {
    pub async fn new(
        address: &str,
        database: DatabaseManager,
    ) -> std::io::Result<Self>  {

        let listener = TcpListener::bind(address)
    .await
    .inspect_err(|e| error!("Impossible de démarrer le serveur : {}", e))?;
        // Schéma (pseudo) puis remise à zéro des statuts : aucun client n'est encore connecté.
        let pool = database.pool().clone();

        

        match UserManager::reset_connected_users(&pool).await {
            Ok(0) => {}
            Ok(count) => info!(
                "{} compte(s) resté(s) CONNECTED remis à DISCONNECTED",
                count
            ),
            Err(e) => error!("{}", e),
        }

        let world = World::new();

        Ok(Self {
        listener,
        database,
        world,
    })
    }

    pub async fn start(&self) {

        debug!("==================================");
        debug!("The Last Signal Server");
        debug!("==================================");

        debug!(
            "Listening on {}",
            self.listener.local_addr().unwrap()
        );

        loop {

            match self.listener.accept().await {

                Ok((stream, address)) => {
    info!("TCP ACCEPT : connexion reçue de {}", address);

    let pool = self.database.pool().clone();
    let world = self.world.clone();

    task::spawn(async move {
        info!("TCP CLIENT : démarrage de Client::run()");

        let mut client = Client::new(
            stream,
            pool,
            world,
        );

        info!("TCP CLIENT : Client::new() terminé");

        client.run().await;

        info!("TCP CLIENT : Client::run() terminé");
    });
}

                Err(e) => {

                error!(
                        "Erreur d'acceptation : {}",
                        e
                    );

                }

            }

        }

    }
}
