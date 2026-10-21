use flexi_logger::{
    Cleanup,
    Criterion,
    DeferredNow,
    Duplicate,
    FileSpec,
    Logger,
    Naming,
    Record,
    writers::LogWriter,
};



use sqlx::SqlitePool;

use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};

use tokio::sync::mpsc;

use crate::utils::logger::compressor::LogCompressor;


// ============================================================
// LOG DESTINÉ À SQLITE
// ============================================================

#[derive(Debug)]
struct DatabaseLog {
    level: String,
    module: String,
    message: String,
}


// ============================================================
// COMMANDES DU WORKER DATABASE
// ============================================================

enum DatabaseCommand {
    SetPool(SqlitePool),
    Log(DatabaseLog),
}


// ============================================================
// WRITER SQLITE
// ============================================================

struct DatabaseWriter {
    sender: mpsc::UnboundedSender<DatabaseCommand>,
}

impl DatabaseWriter {
    fn new(
        sender: mpsc::UnboundedSender<DatabaseCommand>,
    ) -> Self {
        Self { sender }
    }
}

impl LogWriter for DatabaseWriter {

    fn write(
        &self,
        _now: &mut DeferredNow,
        record: &Record<'_>,
    ) -> std::io::Result<()> {

        let module = record
            .module_path()
            .unwrap_or_else(|| record.target())
            .to_string();

        let log = DatabaseLog {
            level: record.level().to_string(),
            module,
            message: format!("{}", record.args()),
        };

        // On envoie le log au worker SQLite.
        //
        // Le logger ne bloque donc pas en attendant SQLite.
        let _ = self.sender.send(
            DatabaseCommand::Log(log)
        );

        Ok(())
    }

    fn flush(&self) -> std::io::Result<()> {
        Ok(())
    }
}


// ============================================================
// FORMAT DU FICHIER LOG
// ============================================================

fn log_format(
    w: &mut dyn Write,
    now: &mut DeferredNow,
    record: &Record<'_>,
) -> std::io::Result<()> {

    let file = record
        .file()
        .and_then(|f| Path::new(f).file_name())
        .and_then(|f| f.to_str())
        .unwrap_or("unknown");

    write!(
        w,
        "[{}] [{}] [{}:{}] {}",
        now.format("%Y-%m-%d %H:%M:%S"),
        record.level(),
        file,
        record.line().unwrap_or(0),
        record.args()
    )
}


// ============================================================
// LOGGER
// ============================================================

pub struct ServerLogger;

impl ServerLogger {

    // ========================================================
    // INITIALISATION
    // ========================================================

    pub fn init() {

        let log_dir = PathBuf::from("../logs");

        // ----------------------------------------------------
        // Canal entre flexi_logger et le worker SQLite
        // ----------------------------------------------------

        let (sender, mut receiver) =
            mpsc::unbounded_channel::<DatabaseCommand>();


        // ----------------------------------------------------
        // Worker SQLite
        // ----------------------------------------------------

        tokio::spawn(async move {

            let mut pool: Option<SqlitePool> = None;

            // Logs produits avant que la DB soit disponible.
            //
            // On les conserve temporairement.
            let mut pending_logs: Vec<DatabaseLog> = Vec::new();

            // Limite de sécurité pour éviter une consommation
            // mémoire infinie si la DB ne devient jamais disponible.
            const MAX_PENDING_LOGS: usize = 1000;


            while let Some(command) = receiver.recv().await {

                match command {

                    // ----------------------------------------
                    // Base de données disponible
                    // ----------------------------------------

                    DatabaseCommand::SetPool(new_pool) => {

                        pool = Some(new_pool);


                        // ------------------------------------
                        // Écriture des logs en attente
                        // ------------------------------------

                        if let Some(pool) = &pool {

                            for log in pending_logs.drain(..) {

                                if let Err(error) =
                                    Self::insert_log(
                                        pool,
                                        &log,
                                    )
                                    .await
                                {
                                    eprintln!(
                                        "Erreur écriture log SQLite : {}",
                                        error
                                    );
                                }
                            }
                        }
                    }


                    // ----------------------------------------
                    // Nouveau log
                    // ----------------------------------------

                    DatabaseCommand::Log(log) => {

                        match &pool {

                            // DB disponible
                            Some(pool) => {

                                if let Err(error) =
                                    Self::insert_log(
                                        pool,
                                        &log,
                                    )
                                    .await
                                {
                                    eprintln!(
                                        "Erreur écriture log SQLite : {}",
                                        error
                                    );
                                }
                            }


                            // DB pas encore disponible
                            None => {

                                if pending_logs.len()
                                    >= MAX_PENDING_LOGS
                                {
                                    // On supprime le plus ancien
                                    // pour éviter une croissance
                                    // infinie.
                                    pending_logs.remove(0);
                                }

                                pending_logs.push(log);
                            }
                        }
                    }
                }
            }
        });


        // ----------------------------------------------------
        // Writer SQLite
        // ----------------------------------------------------

        let database_writer =
            DatabaseWriter::new(sender.clone());


        // ----------------------------------------------------
        // Flexi logger
        // ----------------------------------------------------

        Logger::try_with_str("trace,sqlx=warn")
            .unwrap()

            // Fichier + SQLite
            .log_to_file_and_writer(
                FileSpec::default()
                    .directory(log_dir)
                    .basename("the_last_signal"),

                Box::new(database_writer),
            )

            // stdout
            .duplicate_to_stdout(Duplicate::All)

            // Format du fichier
            .format(log_format)

            // Rotation à 10 MB
            .rotate(
                Criterion::Size(10_000_000),
                Naming::Numbers,
                Cleanup::KeepLogFiles(100),
            )

            // Ajouter aux fichiers existants
            .append()

            // Démarrage
            .start()
            .unwrap();


        // ----------------------------------------------------
        // Compression
        // ----------------------------------------------------

        Self::compress();


        // ----------------------------------------------------
        // Stockage du sender
        // ----------------------------------------------------

        //
        // Le sender doit pouvoir être récupéré par
        // set_database().
        //
        DatabaseSender::set(sender);
    }


    // ========================================================
    // CONNEXION À LA DATABASE
    // ========================================================

    pub fn set_database(
        pool: SqlitePool,
    ) {

        if let Some(sender) =
            DatabaseSender::get()
        {
            let _ = sender.send(
                DatabaseCommand::SetPool(pool)
            );
        }
        else {

            eprintln!(
                "Impossible de connecter le logger à SQLite : \
                 ServerLogger::init() n'a pas été appelé."
            );
        }
    }


    // ========================================================
    // INSERTION SQLITE
    // ========================================================

    async fn insert_log(
        pool: &SqlitePool,
        log: &DatabaseLog,
    ) -> Result<(), sqlx::Error> {

        sqlx::query(
            r#"
            INSERT INTO logs (
                level,
                module,
                message
            )
            VALUES (?, ?, ?)
            "#,
        )
        .bind(&log.level)
        .bind(&log.module)
        .bind(&log.message)
        .execute(pool)
        .await?;

        Ok(())
    }


    // ========================================================
    // COMPRESSION
    // ========================================================

    pub fn compress() {

        if let Err(error) =
            LogCompressor::compress_old_logs(
                "logs",
                10,
            )
        {
            eprintln!(
                "Compression impossible : {}",
                error
            );
        }
    }
}


// ============================================================
// STOCKAGE GLOBAL DU SENDER
// ============================================================

struct DatabaseSender;

static SENDER:
    std::sync::OnceLock<
        Arc<RwLock<
            Option<mpsc::UnboundedSender<DatabaseCommand>>
        >>
    >
    = std::sync::OnceLock::new();


impl DatabaseSender {

    fn set(
        sender: mpsc::UnboundedSender<DatabaseCommand>,
    ) {

        let storage =
            Arc::new(
                RwLock::new(Some(sender))
            );

        let _ = SENDER.set(storage);
    }


    fn get()
        -> Option<
            mpsc::UnboundedSender<DatabaseCommand>
        >
    {
        SENDER
            .get()
            .and_then(|storage| {
                storage
                    .read()
                    .ok()
                    .and_then(|guard| guard.clone())
            })
    }
            }
