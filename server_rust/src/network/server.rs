use tokio::net::TcpListener;
use tokio::task;
use log::{
    info,
    error,
    debug,
};
use crate::database::database_manager::DatabaseManager;
use crate::network::client::Client;
use crate::network::world::World;
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

        Ok(Self {
        listener,
        database,
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

                    info!("Client connecté : {}", address);

                    let pool = self.database.pool().clone();
                    let world = self.world.clone();

                    task::spawn(async move {

                        let mut client =
                            Client::new(stream, pool,world,);

                        client.run().await;

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
