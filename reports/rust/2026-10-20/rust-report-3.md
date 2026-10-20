# Rust Report

Run : 2786
Branch : main
Commit : 03f57a5997a18af42ab622b114c48de0ef546a0a
Date : Tue Oct 20 15:06:14 UTC 2026


## Cargo fmt
error: expected expression, found `,`
   --> /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/packet.rs:251:85
    |
251 |         assert_eq!(PacketType::from_u16(19), Some(PacketType::AccountListResponse));,
    |                                                                                     ^ expected expression

Error writing files: failed to resolve mod `packet`: cannot parse /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/packet.rs
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:1:
-use the_last_signal_server::database::{
-    database_manager::DatabaseManager,
-    migrations,
-};
 use log::info;
 #[allow(dead_code)]
 use sqlx::Row;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:8:
+use the_last_signal_server::database::{database_manager::DatabaseManager, migrations};
 #[allow(dead_code)]
-use the_last_signal_server::gameplay::{
-    stuff_manager::Inventaire,
-    tresor::Tresor,
-};
+use the_last_signal_server::gameplay::{stuff_manager::Inventaire, tresor::Tresor};
 use the_last_signal_server::network::server::Server;
 use the_last_signal_server::utils::logger::logger::ServerLogger;
 #[allow(dead_code)]
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:17:
 #[allow(dead_code)]
 const NOMBRE_CONFIGURATIONS: u32 = 12 * 2 * 2; // niveaux × admin × militaire
 
-
 #[allow(dead_code)]
 #[tokio::main]
 async fn main() -> Result<(), Box<dyn std::error::Error>> {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:26:
     let database_url = std::env::var("DATABASE_URL")?;
     let database_path = std::env::var("DATABASE_PATH")?;
 
-    let database =
-        DatabaseManager::new(&database_path, &database_url)
-            .await?;
+    let database = DatabaseManager::new(&database_path, &database_url).await?;
 
     database.ping().await?;
     migrations::run(&database.pool()).await?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:37:
 
     ServerLogger::set_database(database.pool().clone());
 
-    let server =
-        Server::new("127.0.0.1:5000", database)
-            .await?;
+    let server = Server::new("127.0.0.1:5000", database).await?;
 
     server.start().await;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:46:
     Ok(())
 }
 
-
 #[cfg(test)]
 mod tests {
     use super::*;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:59:
         let database_url = std::env::var("DATABASE_URL")?;
         let database_path = std::env::var("DATABASE_PATH")?;
 
-        let database =
-            DatabaseManager::new(&database_path, &database_url)
-                .await?;
+        let database = DatabaseManager::new(&database_path, &database_url).await?;
 
         database.ping().await?;
         migrations::run(&database.pool()).await?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:82:
          * 1.9
          * 2.0
          */
-        let coefficients: Vec<f64> = (10..=20)
-            .map(|i| f64::from(i) / 10.0)
-            .collect();
+        let coefficients: Vec<f64> = (10..=20).map(|i| f64::from(i) / 10.0).collect();
 
         println!();
         println!("========================================");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:98:
         );
         println!(
             "Nombre total d'ouvertures : {}",
-            NOMBRE_REPETITIONS
-                * NOMBRE_CONFIGURATIONS
-                * coefficients.len() as u32
+            NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS * coefficients.len() as u32
         );
         println!("========================================");
         println!();
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:129:
              * account_id = 1 doit être réservé aux tests.
              */
 
-            sqlx::query(
-                "DELETE FROM echecs_objets WHERE account_id = ?",
-            )
-            .bind(account_id)
-            .execute(database.pool())
-            .await?;
+            sqlx::query("DELETE FROM echecs_objets WHERE account_id = ?")
+                .bind(account_id)
+                .execute(database.pool())
+                .await?;
 
-            sqlx::query(
-                "DELETE FROM echecs_sous_categories WHERE account_id = ?",
-            )
-            .bind(account_id)
-            .execute(database.pool())
-            .await?;
+            sqlx::query("DELETE FROM echecs_sous_categories WHERE account_id = ?")
+                .bind(account_id)
+                .execute(database.pool())
+                .await?;
 
-            sqlx::query(
-                "DELETE FROM stuff WHERE account_id = ?",
-            )
-            .bind(account_id)
-            .execute(database.pool())
-            .await?;
+            sqlx::query("DELETE FROM stuff WHERE account_id = ?")
+                .bind(account_id)
+                .execute(database.pool())
+                .await?;
 
             /*
              * Nouveau trésor pour ce coefficient.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:158:
             /*
              * Nouvel inventaire connecté à la même base.
              */
-            let mut inventaire =
-                Inventaire::new(
-                    database.pool().clone(),
-                    account_id,
-                )
-                .await?;
+            let mut inventaire = Inventaire::new(database.pool().clone(), account_id).await?;
 
-            let total_ouvertures =
-                NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS;
+            let total_ouvertures = NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS;
 
             let mut ouvertures_effectuees: u32 = 0;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:187:
                 for niveau in 1..=12 {
                     for is_admin in [false, true] {
                         for is_militaire in [false, true] {
-
                             let objets = tresor
                                 .ouvrir(
                                     database.pool(),
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:208:
                             for (nom_objet, quantite) in objets {
                                 if nom_objet.contains("livre enchant") {
                                     inventaire
-                                        .ajouter_objet(
-                                            &nom_objet,
-                                            u64::from(quantite),
-                                        )
+                                        .ajouter_objet(&nom_objet, u64::from(quantite))
                                         .await?;
                                 }
                             }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:292:
             /*
              * Nombre de livres distincts selon leur stack_key.
              */
-            let mut livres_uniques =
-                std::collections::HashSet::<String>::new();
+            let mut livres_uniques = std::collections::HashSet::<String>::new();
 
             /*
              * Quantité totale de livres.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:302:
              * Il faut donc éviter de compter plusieurs fois
              * le même stuff_id.
              */
-            let mut livres_comptes =
-                std::collections::HashSet::<i64>::new();
+            let mut livres_comptes = std::collections::HashSet::<i64>::new();
 
             /*
              * Pour afficher les combinaisons réellement générées.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:310:
              */
-            let mut details_livres:
-                std::collections::HashMap<
-                    i64,
-                    (
-                        String,
-                        i64,
-                        i64,
-                        Vec<(String, i64)>,
-                    ),
-                > = std::collections::HashMap::new();
+            let mut details_livres: std::collections::HashMap<
+                i64,
+                (String, i64, i64, Vec<(String, i64)>),
+            > = std::collections::HashMap::new();
 
             for row in rows {
                 let stuff_id: i64 = row.try_get("stuff_id")?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:324:
                 let stack_key: String = row.try_get("stack_key")?;
                 let quantity: i64 = row.try_get("quantity")?;
                 let book_level: i64 = row.try_get("book_level")?;
-                let enchantment_name: String =
-                    row.try_get("enchantment_name")?;
-                let enchantment_level: i64 =
-                    row.try_get("enchantment_level")?;
+                let enchantment_name: String = row.try_get("enchantment_name")?;
+                let enchantment_level: i64 = row.try_get("enchantment_level")?;
 
                 /*
                  * Chaque stuff_id représente un livre exact.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:334:
                  */
                 if livres_comptes.insert(stuff_id) {
                     if (1..=6).contains(&book_level) {
-                        livres_par_niveau[(book_level - 1) as usize]
-                            += quantity;
+                        livres_par_niveau[(book_level - 1) as usize] += quantity;
                     }
 
                     livres_uniques.insert(stack_key.clone());
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:346:
                  */
                 details_livres
                     .entry(stuff_id)
-                    .or_insert_with(|| {
-                        (
-                            stack_key.clone(),
-                            quantity,
-                            book_level,
-                            Vec::new(),
-                        )
-                    })
+                    .or_insert_with(|| (stack_key.clone(), quantity, book_level, Vec::new()))
                     .3
-                    .push((
-                        enchantment_name,
-                        enchantment_level,
-                    ));
+                    .push((enchantment_name, enchantment_level));
             }
 
             /*
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:365:
              * Quantité totale de livres.
              */
-            let total_livres: i64 =
-                livres_par_niveau.iter().sum();
+            let total_livres: i64 = livres_par_niveau.iter().sum();
 
             /*
              * ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:375:
 
             println!();
             println!("----------------------------------------");
-            println!(
-                "RÉSULTATS — coefficient {coefficient:.1}"
-            );
+            println!("RÉSULTATS — coefficient {coefficient:.1}");
             println!("----------------------------------------");
 
             println!("Ouvertures : {ouvertures_effectuees}");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:384:
             println!("Livres générés : {total_livres}");
-            println!(
-                "Combinaisons uniques : {}",
-                livres_uniques.len()
-            );
+            println!("Combinaisons uniques : {}", livres_uniques.len());
 
             println!();
             println!("Répartition des niveaux :");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:392:
 
             for niveau in 1..=6 {
-                let nombre =
-                    livres_par_niveau[(niveau - 1) as usize];
+                let nombre = livres_par_niveau[(niveau - 1) as usize];
 
                 let pourcentage = if total_livres > 0 {
                     nombre as f64 * 100.0 / total_livres as f64
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:421:
 
             let mut livres_affiches = 0usize;
 
-            for (
-                stuff_id,
-                (
-                    stack_key,
-                    quantity,
-                    book_level,
-                    enchantments,
-                ),
-            ) in &details_livres
-            {
+            for (stuff_id, (stack_key, quantity, book_level, enchantments)) in &details_livres {
                 if livres_affiches >= 50 {
                     break;
                 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:444:
 
                 println!("    stack_key : {stack_key}");
 
-                for (
-                    enchantment_name,
-                    enchantment_level,
-                ) in enchantments
-                {
+                for (enchantment_name, enchantment_level) in enchantments {
                     println!(
                         "    - {enchantment_name} \
                          niveau {enchantment_level}"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:467:
             }
 
             println!();
-            println!(
-                "✓ Rapport du coefficient {coefficient:.1} terminé."
-            );
+            println!("✓ Rapport du coefficient {coefficient:.1} terminé.");
         }
 
         println!();
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:476:
         println!("========================================");
         println!("       BENCHMARK TERMINÉ");
         println!("========================================");
+        println!("Coefficients testés : {}", coefficients.len());
         println!(
-            "Coefficients testés : {}",
-            coefficients.len()
-        );
-        println!(
             "Répétitions/configuration : \
              {NOMBRE_REPETITIONS}"
         );
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:490:
         );
         println!(
             "Ouvertures totales : {}",
-            NOMBRE_REPETITIONS
-                * NOMBRE_CONFIGURATIONS
-                * coefficients.len() as u32
+            NOMBRE_REPETITIONS * NOMBRE_CONFIGURATIONS * coefficients.len() as u32
         );
         println!("========================================");
 
⚠️ cargo fmt --check failed

## Cargo clippy

## Cargo test
   Compiling cfg-if v1.0.5
   Compiling libc v0.2.191
   Compiling stable_deref_trait v1.2.1
   Compiling zerofrom v0.1.8
   Compiling pin-project-lite v0.2.17
   Compiling typenum v1.20.1
   Compiling yoke v0.8.3
   Compiling futures-core v0.3.34
   Compiling memchr v2.8.3
   Compiling zerovec v0.11.8
   Compiling tinystr v0.8.4
   Compiling litemap v0.8.3
   Compiling smallvec v1.16.3
   Compiling writeable v0.6.4
   Compiling potential_utf v0.1.6
   Compiling zerotrie v0.2.5
   Compiling utf8_iter v1.0.4
   Compiling scopeguard v1.2.0
   Compiling icu_locale_core v2.3.0
   Compiling icu_collections v2.3.0
   Compiling lock_api v0.4.14
   Compiling icu_properties_data v2.3.0
   Compiling icu_normalizer_data v2.3.0
   Compiling socket2 v0.6.5
   Compiling mio v1.2.4
   Compiling bytes v1.12.1
   Compiling futures-sink v0.3.34
   Compiling serde_core v1.0.229
   Compiling equivalent v1.0.3
   Compiling icu_provider v2.3.1
   Compiling icu_properties v2.3.0
   Compiling icu_normalizer v2.3.0
   Compiling once_cell v1.21.4
   Compiling rand_core v0.10.1
   Compiling generic-array v0.14.9
   Compiling tracing-core v0.1.36
   Compiling parking_lot_core v0.9.12
   Compiling idna_adapter v1.2.2
   Compiling futures-task v0.3.34
   Compiling foldhash v0.2.0
   Compiling futures-io v0.3.34
   Compiling cpufeatures v0.2.17
   Compiling percent-encoding v2.3.2
   Compiling allocator-api2 v0.2.21
   Compiling slab v0.4.12
   Compiling form_urlencoded v1.2.2
   Compiling futures-util v0.3.34
   Compiling idna v1.1.0
   Compiling hashbrown v0.16.1
   Compiling serde v1.0.229
   Compiling num-traits v0.2.19
   Compiling parking_lot v0.12.5
   Compiling zmij v1.0.23
   Compiling getrandom v0.4.3
   Compiling crossbeam-utils v0.8.23
   Compiling crc-catalog v2.5.0
   Compiling hashbrown v0.17.1
   Compiling itoa v1.0.18
   Compiling parking v2.2.1
   Compiling event-listener v5.4.2
   Compiling serde_json v1.0.154
   Compiling crossbeam-queue v0.3.14
   Compiling indexmap v2.14.2
   Compiling crc v3.4.0
   Compiling futures-intrusive v0.5.0
   Compiling either v1.19.0
   Compiling hashlink v0.11.1
   Compiling url v2.5.8
   Compiling block-buffer v0.10.4
   Compiling crypto-common v0.1.6
   Compiling cmov v0.5.4
   Compiling ctutils v0.4.3
   Compiling digest v0.10.7
   Compiling tokio v1.54.0
   Compiling spin v0.9.9
   Compiling hybrid-array v0.4.15
   Compiling tracing v0.1.44
   Compiling flume v0.12.0
   Compiling sha2 v0.10.9
   Compiling futures-executor v0.3.34
   Compiling atoi v2.0.0
   Compiling futures-channel v0.3.34
   Compiling log v0.4.34
   Compiling crypto-common v0.2.2
   Compiling block-buffer v0.12.1
   Compiling thiserror v2.0.21
   Compiling base64 v0.22.1
   Compiling const-oid v0.10.2
   Compiling cpufeatures v0.3.1
   Compiling digest v0.11.3
   Compiling uuid v1.28.0
   Compiling aho-corasick v1.1.5
   Compiling foreign-types-shared v0.1.1
   Compiling regex-syntax v0.8.11
   Compiling tokio-stream v0.1.19
   Compiling sqlx-core v0.9.0
   Compiling base64ct v1.8.3
   Compiling phc v0.6.1
   Compiling regex-automata v0.4.18
   Compiling sqlx-sqlite v0.9.0
   Compiling foreign-types v0.3.2
   Compiling libsqlite3-sys v0.37.0
   Compiling openssl-sys v0.9.117
   Compiling sqlx-macros-core v0.9.0
   Compiling bitflags v2.13.2
   Compiling simd-adler32 v0.3.10
   Compiling iana-time-zone v0.1.65
   Compiling adler2 v2.0.1
   Compiling miniz_oxide v0.9.1
   Compiling chrono v0.4.45
   Compiling openssl v0.10.81
   Compiling zeroize v1.9.1
   Compiling sqlx-macros v0.9.0
   Compiling regex v1.13.1
   Compiling crc32fast v1.5.2
   Compiling password-hash v0.6.1
   Compiling blake2 v0.11.0
   Compiling chacha20 v0.10.2
   Compiling getrandom v0.2.17
   Compiling byteorder v1.5.0
   Compiling nu-ansi-term v0.50.3
   Compiling argon2 v0.6.0
   Compiling flexi_logger v0.31.10
   Compiling fernet v0.2.2
   Compiling sqlx v0.9.0
   Compiling rand v0.10.3
   Compiling flate2 v1.1.10
   Compiling sha2 v0.11.1
   Compiling the-last-signal-server v1.0.15 (/home/runner/work/The-last-signal-/The-last-signal-/server_rust)
error: expected expression, found `,`
   --> src/network/packet.rs:251:85
    |
251 |         assert_eq!(PacketType::from_u16(19), Some(PacketType::AccountListResponse));,
    |                                                                                     ^ expected expression

error: could not compile `the-last-signal-server` (lib) due to 1 previous error
warning: build failed, waiting for other jobs to finish...
error: could not compile `the-last-signal-server` (lib test) due to 1 previous error
