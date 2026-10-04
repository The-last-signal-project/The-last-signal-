use the_last_signal_server::database::{
    database_manager::DatabaseManager,
    migrations,
};
use log::info;
use sqlx::Row;

use the_last_signal_server::network::server::Server;
use the_last_signal_server::gameplay::{
    stuff_manager::Inventaire,
    tresor::Tresor,
};

use the_last_signal_server::utils::logger::logger::ServerLogger;

const NOMBRE_REPETITIONS: u32 = 10000;
const NOMBRE_CONFIGURATIONS: u32 = 10 * 2 * 2; // niveaux × admin × militaire


#[allow(dead_code)]
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let _guard = ServerLogger::init();

    let database_url = std::env::var("DATABASE_URL")?;
    let database_path = std::env::var("DATABASE_PATH")?;

    let database =
        DatabaseManager::new(&database_path, &database_url)
            .await?;

    database.ping().await?;
    migrations::run(&database.pool()).await?;

    info!("Base SQLite prête.");

    ServerLogger::set_database(database.pool().clone());

    let server =
        Server::new("127.0.0.1:5000", database)
            .await?;

    server.start().await;

    Ok(())
}


#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_tresor() -> Result<(), Box<dyn std::error::Error>> {
        let _guard = ServerLogger::init();

        let database_url = std::env::var("DATABASE_URL")?;
        let database_path = std::env::var("DATABASE_PATH")?;

        let database =
            DatabaseManager::new(&database_path, &database_url)
                .await?;

        database.ping().await?;
        migrations::run(&database.pool()).await?;

        info!("Base SQLite prête.");

        ServerLogger::set_database(database.pool().clone());

        let account_id: i64 = 1;

        /*
         * Coefficients testés :
         *
         * 1.0
         * 1.1
         * 1.2
         * ...
         * 1.9
         * 2.0
         */
        let coefficients: Vec<f64> = (10..=20)
            .map(|i| f64::from(i) / 10.0)
            .collect();

        println!();
        println!("========================================");
        println!("     BENCHMARK DES TRÉSORS");
        println!("========================================");
        println!("Répétitions par configuration : {NOMBRE_REPETITIONS}");
        println!("Configurations par coefficient : {NOMBRE_CONFIGURATIONS}");
        println!(
            "Ouvertures par coefficient : {}",
            NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS
        );
        println!(
            "Nombre total d'ouvertures : {}",
            NOMBRE_REPETITIONS
                * NOMBRE_CONFIGURATIONS
                * coefficients.len() as u32
        );
        println!("========================================");
        println!();

        /*
         * Chaque coefficient est testé indépendamment.
         *
         * On utilise un nouveau Tresor pour chaque coefficient afin
         * d'éviter qu'un éventuel état interne du Tresor ne passe
         * d'un coefficient au suivant.
         */
        for coefficient in &coefficients {
            println!();
            println!("########################################");
            println!("COEFFICIENT : {coefficient:.1}");
            println!("########################################");

            /*
             * Nettoyage des données de test du compte 1.
             *
             * Les tables dépendantes de `stuff` utilisent ON DELETE
             * CASCADE, donc supprimer les lignes de `stuff` supprime
             * également les livres enchantés associés.
             *
             * IMPORTANT :
             * account_id = 1 doit être réservé aux tests.
             */

            sqlx::query(
                "DELETE FROM echecs_objets WHERE account_id = ?",
            )
            .bind(account_id)
            .execute(database.pool())
            .await?;

            sqlx::query(
                "DELETE FROM echecs_sous_categories WHERE account_id = ?",
            )
            .bind(account_id)
            .execute(database.pool())
            .await?;

            sqlx::query(
                "DELETE FROM stuff WHERE account_id = ?",
            )
            .bind(account_id)
            .execute(database.pool())
            .await?;

            /*
             * Nouveau trésor pour ce coefficient.
             */
            let mut tresor = Tresor::new();

            /*
             * Nouvel inventaire connecté à la même base.
             */
            let mut inventaire =
                Inventaire::new(
                    database.pool().clone(),
                    account_id,
                )
                .await?;

            let total_ouvertures =
                NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS;

            let mut ouvertures_effectuees: u32 = 0;

            /*
             * 1 000 répétitions de chaque configuration.
             *
             * Une configuration =
             *
             * niveau 1..=10
             * × admin false/true
             * × militaire false/true
             *
             * Soit :
             *
             * 10 × 2 × 2 = 40 configurations.
             */
            for _repetition in 0..NOMBRE_REPETITIONS {
                for niveau in 1..=10 {
                    for is_admin in [false, true] {
                        for is_militaire in [false, true] {

                            let objets = tresor
                                .ouvrir(
                                    database.pool(),
                                    account_id,
                                    niveau,
                                    is_admin,
                                    is_militaire,
                                    Some(*coefficient),
                                )
                                .await?;

                            /*
                             * On ajoute les livres dans l'inventaire.
                             *
                             * La génération réelle des enchantements
                             * est donc faite par le système normal du jeu.
                             */
                            for (nom_objet, quantite) in objets {
                                if nom_objet.contains("livre enchant") {
                                    inventaire
                                        .ajouter_objet(
                                            &nom_objet,
                                            u64::from(quantite),
                                        )
                                        .await?;
                                }
                            }

                            ouvertures_effectuees += 1;

                            /*
                             * Affichage de progression toutes les
                             * 10 000 ouvertures.
                             */
                            if ouvertures_effectuees % 10_000 == 0 {
                                println!(
                                    "[coeff {coefficient:.1}] \
                                     {ouvertures_effectuees}/{total_ouvertures} \
                                     ouvertures"
                                );
                            }
                        }
                    }
                }
            }

            println!();
            println!(
                "✓ Coefficient {coefficient:.1} terminé : \
                 {ouvertures_effectuees} ouvertures"
            );

            /*
             * ========================================================
             * LECTURE DES VRAIS LIVRES CRÉÉS DANS SQLITE
             * ========================================================
             *
             * On ne recrée PAS les enchantements dans le benchmark.
             *
             * On lit directement ce que Inventaire::ajouter_objet()
             * a réellement créé.
             */

            let rows = sqlx::query(
                r#"
                SELECT
                    s.stuff_id,
                    s.stack_key,
                    s.quantity,
                    eb.book_level,
                    e.enchantment_name,
                    be.enchantment_level
                FROM stuff s
                INNER JOIN enchanted_books eb
                    ON eb.stuff_id = s.stuff_id
                INNER JOIN book_enchantments be
                    ON be.book_id = eb.book_id
                INNER JOIN enchantments e
                    ON e.enchantment_id = be.enchantment_id
                WHERE s.account_id = ?
                ORDER BY
                    eb.book_level,
                    s.stuff_id,
                    e.enchantment_id
                "#,
            )
            .bind(account_id)
            .fetch_all(database.pool())
            .await?;

            /*
             * Statistiques par niveau de livre.
             *
             * Index :
             * 0 = niveau 1
             * 1 = niveau 2
             * ...
             * 5 = niveau 6
             */
            let mut livres_par_niveau = [0_i64; 6];

            /*
             * Nombre de livres distincts selon leur stack_key.
             */
            let mut livres_uniques =
                std::collections::HashSet::<String>::new();

            /*
             * Quantité totale de livres.
             *
             * Une ligne SQL correspond à un enchantement.
             * Il faut donc éviter de compter plusieurs fois
             * le même stuff_id.
             */
            let mut livres_comptes =
                std::collections::HashSet::<i64>::new();

            /*
             * Pour afficher les combinaisons réellement générées.
             */
            let mut details_livres:
                std::collections::HashMap<
                    i64,
                    (
                        String,
                        i64,
                        i64,
                        Vec<(String, i64)>,
                    ),
                > = std::collections::HashMap::new();

            for row in rows {
                let stuff_id: i64 = row.try_get("stuff_id")?;
                let stack_key: String = row.try_get("stack_key")?;
                let quantity: i64 = row.try_get("quantity")?;
                let book_level: i64 = row.try_get("book_level")?;
                let enchantment_name: String =
                    row.try_get("enchantment_name")?;
                let enchantment_level: i64 =
                    row.try_get("enchantment_level")?;

                /*
                 * Chaque stuff_id représente un livre exact.
                 */
                if livres_comptes.insert(stuff_id) {
                    if (1..=6).contains(&book_level) {
                        livres_par_niveau[(book_level - 1) as usize]
                            += quantity;
                    }

                    livres_uniques.insert(stack_key.clone());
                }

                /*
                 * On regroupe les enchantements du livre.
                 */
                details_livres
                    .entry(stuff_id)
                    .or_insert_with(|| {
                        (
                            stack_key.clone(),
                            quantity,
                            book_level,
                            Vec::new(),
                        )
                    })
                    .3
                    .push((
                        enchantment_name,
                        enchantment_level,
                    ));
            }

            /*
             * Quantité totale de livres.
             */
            let total_livres: i64 =
                livres_par_niveau.iter().sum();

            /*
             * ========================================================
             * RAPPORT
             * ========================================================
             */

            println!();
            println!("----------------------------------------");
            println!(
                "RÉSULTATS — coefficient {coefficient:.1}"
            );
            println!("----------------------------------------");

            println!("Ouvertures : {ouvertures_effectuees}");
            println!("Livres générés : {total_livres}");
            println!(
                "Combinaisons uniques : {}",
                livres_uniques.len()
            );

            println!();
            println!("Répartition des niveaux :");

            for niveau in 1..=6 {
                let nombre =
                    livres_par_niveau[(niveau - 1) as usize];

                let pourcentage = if total_livres > 0 {
                    nombre as f64 * 100.0 / total_livres as f64
                } else {
                    0.0
                };

                println!(
                    "  Niveau {niveau} : \
                     {nombre:>8} \
                     ({pourcentage:>6.2} %)"
                );
            }

            /*
             * Affichage des livres réellement générés.
             *
             * On limite volontairement l'affichage à 50 livres
             * pour éviter d'exploser les logs GitHub Actions.
             */
            println!();
            println!(
                "Premiers livres générés \
                 (maximum 50) :"
            );

            let mut livres_affiches = 0usize;

            for (
                stuff_id,
                (
                    stack_key,
                    quantity,
                    book_level,
                    enchantments,
                ),
            ) in &details_livres
            {
                if livres_affiches >= 50 {
                    break;
                }

                println!();
                println!(
                    "  Livre #{stuff_id} \
                     | niveau {book_level} \
                     | quantité {quantity}"
                );

                println!("    stack_key : {stack_key}");

                for (
                    enchantment_name,
                    enchantment_level,
                ) in enchantments
                {
                    println!(
                        "    - {enchantment_name} \
                         niveau {enchantment_level}"
                    );
                }

                livres_affiches += 1;
            }

            if details_livres.len() > 50 {
                println!();
                println!(
                    "... {} autres livres non affichés.",
                    details_livres.len() - 50
                );
            }

            println!();
            println!(
                "✓ Rapport du coefficient {coefficient:.1} terminé."
            );
        }

        println!();
        println!("========================================");
        println!("       BENCHMARK TERMINÉ");
        println!("========================================");
        println!(
            "Coefficients testés : {}",
            coefficients.len()
        );
        println!(
            "Répétitions/configuration : \
             {NOMBRE_REPETITIONS}"
        );
        println!(
            "Ouvertures/coefficient : {}",
            NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS
        );
        println!(
            "Ouvertures totales : {}",
            NOMBRE_REPETITIONS
                * NOMBRE_CONFIGURATIONS
                * coefficients.len() as u32
        );
        println!("========================================");

        Ok(())
    }
}
