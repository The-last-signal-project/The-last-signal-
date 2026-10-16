# Rust Report

Run : 2447
Branch : main
Commit : 5aa517f7118e422b6d3bf6e74f1267026d0e73ac
Date : Thu Oct 15 19:13:14 UTC 2026


## Cargo fmt
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/auth/password.rs:1:
 use argon2::{
-password_hash::{
-PasswordHasher,
-PasswordVerifier,
-phc::PasswordHash,
-},
-Argon2,
+    Argon2,
+    password_hash::{PasswordHasher, PasswordVerifier, phc::PasswordHash},
 };
 
 /// Hash un mot de passe.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/auth/password.rs:12:
 /// Le résultat contient également le sel et les paramètres
 /// nécessaires pour vérifier le mot de passe plus tard.
 pub fn hash_password(password: &str) -> Result<String, String> {
-Argon2::default()
-.hash_password(password.as_bytes())
-.map(|hash| hash.to_string())
-.map_err(|e| format!("Erreur lors du hash du mot de passe : {e}"))
+    Argon2::default()
+        .hash_password(password.as_bytes())
+        .map(|hash| hash.to_string())
+        .map_err(|e| format!("Erreur lors du hash du mot de passe : {e}"))
 }
 
 /// Vérifie un mot de passe avec un hash existant.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/auth/password.rs:22:
-pub fn verify_password(
-password: &str,
-password_hash: &str,
-) -> bool {
-let parsed_hash = match PasswordHash::new(password_hash) {
-Ok(hash) => hash,
-Err(_) => return false,
-};
+pub fn verify_password(password: &str, password_hash: &str) -> bool {
+    let parsed_hash = match PasswordHash::new(password_hash) {
+        Ok(hash) => hash,
+        Err(_) => return false,
+    };
 
-
-Argon2::default()
-    .verify_password(password.as_bytes(), &parsed_hash)
-    .is_ok()
-
+    Argon2::default()
+        .verify_password(password.as_bytes(), &parsed_hash)
+        .is_ok()
 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:20:
     }
 
     /// Vérifie si une base SQLite existante est corrompue.
-    pub async fn is_database_corrupted(
-        database_url: &str,
-    ) -> Result<bool, sqlx::Error> {
-        let options = SqliteConnectOptions::from_str(database_url)?
-            .create_if_missing(false);
+    pub async fn is_database_corrupted(database_url: &str) -> Result<bool, sqlx::Error> {
+        let options = SqliteConnectOptions::from_str(database_url)?.create_if_missing(false);
 
         let pool = match SqlitePoolOptions::new()
             .max_connections(1)
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:37:
             Err(e) => return Err(e),
         };
 
-        let result: Result<String, sqlx::Error> =
-            sqlx::query_scalar("PRAGMA integrity_check")
-                .fetch_one(&pool)
-                .await;
+        let result: Result<String, sqlx::Error> = sqlx::query_scalar("PRAGMA integrity_check")
+            .fetch_one(&pool)
+            .await;
 
         pool.close().await;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:52:
     }
 
     /// Crée ou ouvre la base SQLite.
-    pub async fn create_database(
-        database_url: &str,
-    ) -> Result<SqlitePool, sqlx::Error> {
-        let options = SqliteConnectOptions::from_str(database_url)?
-            .create_if_missing(true);
+    pub async fn create_database(database_url: &str) -> Result<SqlitePool, sqlx::Error> {
+        let options = SqliteConnectOptions::from_str(database_url)?.create_if_missing(true);
 
         let pool = SqlitePoolOptions::new()
             .max_connections(5)
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:104:
         Ok(())
     }
 
-    pub async fn new(
-        database_path: &str,
-        database_url: &str,
-    ) -> Result<Self, sqlx::Error> {
+    pub async fn new(database_path: &str, database_url: &str) -> Result<Self, sqlx::Error> {
         let path = database_path
             .strip_prefix("sqlite:")
             .unwrap_or(database_path);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:114:
 
-        let database_file = database_url
-            .strip_prefix("sqlite:")
-            .unwrap_or(database_url);
+        let database_file = database_url.strip_prefix("sqlite:").unwrap_or(database_url);
 
         std::fs::create_dir_all(path).map_err(sqlx::Error::Io)?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/database_manager.rs:127:
                          Suppression et recréation..."
                     );
 
-                    std::fs::remove_file(database_file)
-                        .map_err(sqlx::Error::Io)?;
+                    std::fs::remove_file(database_file).map_err(sqlx::Error::Io)?;
                     let _ = std::fs::remove_file(format!("{database_file}-wal"));
                     let _ = std::fs::remove_file(format!("{database_file}-shm"));
                 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/migrations.rs:1:
-use log::debug;
-use sqlx::SqlitePool;
-use crate::utils::vault::decrypt_vault;
 use crate::auth::password::hash_password;
 use crate::utils::special_account_creator::create_account;
+use crate::utils::vault::decrypt_vault;
+use log::debug;
+use sqlx::SqlitePool;
 /// Exécute toutes les migrations SQL non encore appliquées.
 pub async fn run(pool: &SqlitePool) -> Result<(), Box<dyn std::error::Error>> {
     sqlx::query(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/migrations.rs:23:
     let vault = decrypt_vault()?;
 
     let password1 = vault["user1_password"]
-    .as_str()
-    .ok_or("Mot de passe user1 absent")?;
-    let password1_hash = hash_password(password1)
-    .map_err(|e| sqlx::Error::Protocol(e))?;
+        .as_str()
+        .ok_or("Mot de passe user1 absent")?;
+    let password1_hash = hash_password(password1).map_err(|e| sqlx::Error::Protocol(e))?;
 
     let password2 = vault["user2_password"]
-    .as_str()
-    .ok_or("Mot de passe user2 absent")?;
-    let password2_hash = hash_password(password2)
-    .map_err(|e| sqlx::Error::Protocol(e))?;
-    
-    
-    sqlx::migrate!("./migrations")
-        .run(pool)
-        .await?;
+        .as_str()
+        .ok_or("Mot de passe user2 absent")?;
+    let password2_hash = hash_password(password2).map_err(|e| sqlx::Error::Protocol(e))?;
 
+    sqlx::migrate!("./migrations").run(pool).await?;
+
     debug!("Migrations SQLite appliquées.");
     create_account(
-    pool,
-    "Admin@gmail.com",
-    &password1_hash,
+        pool,
+        "Admin@gmail.com",
+        &password1_hash,
         "Cyril",
         "Dev",
         Some("DISCONNECTED"),
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/migrations.rs:50:
-)
-.await?;
+    )
+    .await?;
 
-create_account(
-    pool,
-    "thelastsignalfr@gmail.com",
-    &password2_hash,
-    "Morgan",
-    "SuperDev",
-    Some("DISCONNECTED"),
-)
-.await?;
+    create_account(
+        pool,
+        "thelastsignalfr@gmail.com",
+        &password2_hash,
+        "Morgan",
+        "SuperDev",
+        Some("DISCONNECTED"),
+    )
+    .await?;
 
     Ok(())
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/migrations.rs:65:
-
-
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/database/mod.rs:1:
 pub mod database_manager;
 pub mod migrations;
-
-
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/dice.rs:3:
 pub fn jet_de_des(face: u32, nb: u32) -> u32 {
     let mut rng = rand::rng();
 
-    (0..nb)
-        .map(|_| rng.random_range(1..=face))
-        .sum()
+    (0..nb).map(|_| rng.random_range(1..=face)).sum()
 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:36:
         }
 
         let quantity_i64 = i64::try_from(quantity).map_err(|_| {
-            sqlx::Error::Protocol(
-                "La quantité dépasse la capacité SQLite INTEGER".into(),
-            )
+            sqlx::Error::Protocol("La quantité dépasse la capacité SQLite INTEGER".into())
         })?;
 
-        let montant_total = prix_unitaire_max
-            .checked_mul(quantity_i64)
-            .ok_or_else(|| {
-                sqlx::Error::Protocol(
-                    "Le montant total dépasse la capacité i64".into(),
-                )
-            })?;
+        let montant_total = prix_unitaire_max.checked_mul(quantity_i64).ok_or_else(|| {
+            sqlx::Error::Protocol("Le montant total dépasse la capacité i64".into())
+        })?;
 
         let mut tx = self.pool.begin().await?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:64:
         .await?;
 
         if existe.is_none() {
-            return Err(sqlx::Error::Protocol(
-                "Objet inexistant".into(),
-            ));
+            return Err(sqlx::Error::Protocol("Objet inexistant".into()));
         }
 
         // Réserve l'argent.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:73:
-        WalletManager::debiter_tx(
-            &mut tx,
-            account_id,
-            montant_total,
-        )
-        .await?;
+        WalletManager::debiter_tx(&mut tx, account_id, montant_total).await?;
 
         // Crée l'ordre.
         let result = sqlx::query(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:131:
         }
 
         let quantity_i64 = i64::try_from(quantity).map_err(|_| {
-            sqlx::Error::Protocol(
-                "La quantité dépasse la capacité SQLite INTEGER".into(),
-            )
+            sqlx::Error::Protocol("La quantité dépasse la capacité SQLite INTEGER".into())
         })?;
 
         let mut tx = self.pool.begin().await?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:151:
         .await?;
 
         if existe.is_none() {
-            return Err(sqlx::Error::Protocol(
-                "Objet inexistant".into(),
-            ));
+            return Err(sqlx::Error::Protocol("Objet inexistant".into()));
         }
 
         // Réserve les objets.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:160:
-        Inventaire::retirer_tx(
-            &mut tx,
-            account_id,
-            objet_id,
-            quantity,
-        )
-        .await?;
+        Inventaire::retirer_tx(&mut tx, account_id, objet_id, quantity).await?;
 
         // Crée l'ordre.
         let result = sqlx::query(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:195:
         Ok(ordre_id)
     }
     /// Annule un ordre d'achat et restitue les fonds correspondant
-/// à la quantité restante.
-pub async fn annuler_ordre_achat(
-    &self,
-    account_id: i64,
-    ordre_id: i64,
-) -> Result<(), sqlx::Error> {
-    let mut tx = self.pool.begin().await?;
+    /// à la quantité restante.
+    pub async fn annuler_ordre_achat(
+        &self,
+        account_id: i64,
+        ordre_id: i64,
+    ) -> Result<(), sqlx::Error> {
+        let mut tx = self.pool.begin().await?;
 
-    let ordre: Option<(i64, i64, i64, String)> = sqlx::query_as(
-        r#"
+        let ordre: Option<(i64, i64, i64, String)> = sqlx::query_as(
+            r#"
         SELECT
             objet_id,
             quantity_remaining,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:214:
         WHERE ordre_id = ?
           AND account_id = ?
         "#,
-    )
-    .bind(ordre_id)
-    .bind(account_id)
-    .fetch_optional(&mut *tx)
-    .await?;
+        )
+        .bind(ordre_id)
+        .bind(account_id)
+        .fetch_optional(&mut *tx)
+        .await?;
 
-    let (objet_id, quantity_remaining, prix_unitaire_max, statut) =
-        ordre.ok_or_else(|| {
-            sqlx::Error::Protocol(
-                "Ordre d'achat inexistant".into(),
-            )
-        })?;
+        let (objet_id, quantity_remaining, prix_unitaire_max, statut) =
+            ordre.ok_or_else(|| sqlx::Error::Protocol("Ordre d'achat inexistant".into()))?;
 
-    if statut != "actif" {
-        return Err(sqlx::Error::Protocol(
-            "L'ordre d'achat n'est plus actif".into(),
-        ));
-    }
+        if statut != "actif" {
+            return Err(sqlx::Error::Protocol(
+                "L'ordre d'achat n'est plus actif".into(),
+            ));
+        }
 
-    let montant_a_rembourser = prix_unitaire_max
-        .checked_mul(quantity_remaining)
-        .ok_or_else(|| {
-            sqlx::Error::Protocol(
-                "Le montant du remboursement dépasse la capacité i64".into(),
-            )
-        })?;
+        let montant_a_rembourser = prix_unitaire_max
+            .checked_mul(quantity_remaining)
+            .ok_or_else(|| {
+                sqlx::Error::Protocol("Le montant du remboursement dépasse la capacité i64".into())
+            })?;
 
-    // Marque l'ordre comme annulé.
-    let result = sqlx::query(
-        r#"
+        // Marque l'ordre comme annulé.
+        let result = sqlx::query(
+            r#"
         UPDATE ordres_achat
         SET statut = 'annule'
         WHERE ordre_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:250:
           AND account_id = ?
           AND statut = 'actif'
         "#,
-    )
-    .bind(ordre_id)
-    .bind(account_id)
-    .execute(&mut *tx)
-    .await?;
-
-    if result.rows_affected() != 1 {
-        return Err(sqlx::Error::Protocol(
-            "Impossible d'annuler l'ordre d'achat".into(),
-        ));
-    }
-
-    // Restitue les fonds réservés.
-    if montant_a_rembourser > 0 {
-        WalletManager::crediter_tx(
-            &mut tx,
-            account_id,
-            montant_a_rembourser,
         )
+        .bind(ordre_id)
+        .bind(account_id)
+        .execute(&mut *tx)
         .await?;
-    }
 
-    tx.commit().await?;
+        if result.rows_affected() != 1 {
+            return Err(sqlx::Error::Protocol(
+                "Impossible d'annuler l'ordre d'achat".into(),
+            ));
+        }
 
-    let _ = objet_id;
+        // Restitue les fonds réservés.
+        if montant_a_rembourser > 0 {
+            WalletManager::crediter_tx(&mut tx, account_id, montant_a_rembourser).await?;
+        }
 
-    Ok(())
-}
+        tx.commit().await?;
+
+        let _ = objet_id;
+
+        Ok(())
+    }
     /// Annule un ordre de vente et restitue les objets restants
-/// dans l'inventaire du vendeur.
-pub async fn annuler_ordre_vente(
-    &self,
-    account_id: i64,
-    ordre_id: i64,
-) -> Result<(), sqlx::Error> {
-    let mut tx = self.pool.begin().await?;
+    /// dans l'inventaire du vendeur.
+    pub async fn annuler_ordre_vente(
+        &self,
+        account_id: i64,
+        ordre_id: i64,
+    ) -> Result<(), sqlx::Error> {
+        let mut tx = self.pool.begin().await?;
 
-    let ordre: Option<(i64, i64, String)> = sqlx::query_as(
-        r#"
+        let ordre: Option<(i64, i64, String)> = sqlx::query_as(
+            r#"
         SELECT
             objet_id,
             quantity_remaining,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:297:
         WHERE ordre_id = ?
           AND account_id = ?
         "#,
-    )
-    .bind(ordre_id)
-    .bind(account_id)
-    .fetch_optional(&mut *tx)
-    .await?;
+        )
+        .bind(ordre_id)
+        .bind(account_id)
+        .fetch_optional(&mut *tx)
+        .await?;
 
-    let (objet_id, quantity_remaining, statut) =
-        ordre.ok_or_else(|| {
-            sqlx::Error::Protocol(
-                "Ordre de vente inexistant".into(),
-            )
-        })?;
+        let (objet_id, quantity_remaining, statut) =
+            ordre.ok_or_else(|| sqlx::Error::Protocol("Ordre de vente inexistant".into()))?;
 
-    if statut != "actif" {
-        return Err(sqlx::Error::Protocol(
-            "L'ordre de vente n'est plus actif".into(),
-        ));
-    }
+        if statut != "actif" {
+            return Err(sqlx::Error::Protocol(
+                "L'ordre de vente n'est plus actif".into(),
+            ));
+        }
 
-    let quantity_u64 = u64::try_from(quantity_remaining).map_err(|_| {
-        sqlx::Error::Protocol(
-            "Quantité invalide".into(),
-        )
-    })?;
+        let quantity_u64 = u64::try_from(quantity_remaining)
+            .map_err(|_| sqlx::Error::Protocol("Quantité invalide".into()))?;
 
-    // Restitue les objets réservés.
-    if quantity_u64 > 0 {
-        Inventaire::ajouter_tx(
-            &mut tx,
-            account_id,
-            objet_id,
-            quantity_u64,
-        )
-        .await?;
-    }
+        // Restitue les objets réservés.
+        if quantity_u64 > 0 {
+            Inventaire::ajouter_tx(&mut tx, account_id, objet_id, quantity_u64).await?;
+        }
 
-    // Marque l'ordre comme annulé.
-    let result = sqlx::query(
-        r#"
+        // Marque l'ordre comme annulé.
+        let result = sqlx::query(
+            r#"
         UPDATE ordres_vente
         SET statut = 'annule'
         WHERE ordre_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:342:
           AND account_id = ?
           AND statut = 'actif'
         "#,
-    )
-    .bind(ordre_id)
-    .bind(account_id)
-    .execute(&mut *tx)
-    .await?;
+        )
+        .bind(ordre_id)
+        .bind(account_id)
+        .execute(&mut *tx)
+        .await?;
 
-    if result.rows_affected() != 1 {
-        return Err(sqlx::Error::Protocol(
-            "Impossible d'annuler l'ordre de vente".into(),
-        ));
-    }
+        if result.rows_affected() != 1 {
+            return Err(sqlx::Error::Protocol(
+                "Impossible d'annuler l'ordre de vente".into(),
+            ));
+        }
 
-    tx.commit().await?;
+        tx.commit().await?;
 
-    Ok(())
-                       }
-    pub async fn matcher_ordre(
-    &self,
-    objet_id: i64,
-) -> Result<Option<i64>, sqlx::Error> {
-    let mut tx = self.pool.begin().await?;
+        Ok(())
+    }
+    pub async fn matcher_ordre(&self, objet_id: i64) -> Result<Option<i64>, sqlx::Error> {
+        let mut tx = self.pool.begin().await?;
 
-    // --------------------------------------------------------
-    // Meilleur ordre d'achat
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Meilleur ordre d'achat
+        // --------------------------------------------------------
 
-    let achat: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
-        r#"
+        let achat: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
+            r#"
         SELECT
             ordre_id,
             account_id,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:386:
             ordre_id ASC
         LIMIT 1
         "#,
-    )
-    .bind(objet_id)
-    .fetch_optional(&mut *tx)
-    .await?;
+        )
+        .bind(objet_id)
+        .fetch_optional(&mut *tx)
+        .await?;
 
-    let achat = match achat {
-        Some(achat) => achat,
-        None => {
-            tx.rollback().await?;
-            return Ok(None);
-        }
-    };
+        let achat = match achat {
+            Some(achat) => achat,
+            None => {
+                tx.rollback().await?;
+                return Ok(None);
+            }
+        };
         let acheteur_id = achat.1;
-        
 
-    // --------------------------------------------------------
-    // Meilleur ordre de vente
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Meilleur ordre de vente
+        // --------------------------------------------------------
 
-   let vente: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
-    r#"
+        let vente: Option<(i64, i64, i64, i64, i64)> = sqlx::query_as(
+            r#"
     SELECT
         ordre_id,
         account_id,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:424:
         ordre_id ASC
     LIMIT 1
     "#,
-)
-.bind(objet_id)
-.bind(acheteur_id)
-.fetch_optional(&mut *tx)
-.await?;
+        )
+        .bind(objet_id)
+        .bind(acheteur_id)
+        .fetch_optional(&mut *tx)
+        .await?;
 
-    let vente = match vente {
-        Some(vente) => vente,
-        None => {
-            tx.rollback().await?;
-            return Ok(None);
-        }
-    };
+        let vente = match vente {
+            Some(vente) => vente,
+            None => {
+                tx.rollback().await?;
+                return Ok(None);
+            }
+        };
 
-    let (
-        ordre_achat_id,
-        acheteur_id,
-        achat_remaining,
-        prix_achat,
-        _achat_timestamp,
-    ) = achat;
+        let (ordre_achat_id, acheteur_id, achat_remaining, prix_achat, _achat_timestamp) = achat;
 
-    let (
-        ordre_vente_id,
-        vendeur_id,
-        vente_remaining,
-        prix_vente,
-        _vente_timestamp,
-    ) = vente;
+        let (ordre_vente_id, vendeur_id, vente_remaining, prix_vente, _vente_timestamp) = vente;
 
-    // --------------------------------------------------------
-    // Vérification de compatibilité
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Vérification de compatibilité
+        // --------------------------------------------------------
 
-    if prix_achat < prix_vente {
-        tx.rollback().await?;
-        return Ok(None);
-    }
+        if prix_achat < prix_vente {
+            tx.rollback().await?;
+            return Ok(None);
+        }
 
-    // --------------------------------------------------------
-    // Quantité exécutée
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Quantité exécutée
+        // --------------------------------------------------------
 
-    let quantity = achat_remaining.min(vente_remaining);
+        let quantity = achat_remaining.min(vente_remaining);
 
-    // --------------------------------------------------------
-    // Prix de transaction
-    // --------------------------------------------------------
-    //
-    // Le prix de vente est utilisé comme prix d'exécution.
-    //
-    let prix_execution = prix_vente;
+        // --------------------------------------------------------
+        // Prix de transaction
+        // --------------------------------------------------------
+        //
+        // Le prix de vente est utilisé comme prix d'exécution.
+        //
+        let prix_execution = prix_vente;
 
-    let montant_total = prix_execution
-        .checked_mul(quantity)
-        .ok_or_else(|| {
-            sqlx::Error::Protocol(
-                "Le montant de la transaction dépasse la capacité i64".into(),
-            )
+        let montant_total = prix_execution.checked_mul(quantity).ok_or_else(|| {
+            sqlx::Error::Protocol("Le montant de la transaction dépasse la capacité i64".into())
         })?;
-    // --------------------------------------------------------
-// Mise à jour du prix du marché
-// --------------------------------------------------------
+        // --------------------------------------------------------
+        // Mise à jour du prix du marché
+        // --------------------------------------------------------
 
-sqlx::query(
-    r#"
+        sqlx::query(
+            r#"
     UPDATE objets_dispo
     SET prix_marche = ?
     WHERE objet_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:496:
     "#,
-)
-.bind(prix_execution)
-.bind(objet_id)
-.execute(&mut *tx)
-.await?;
+        )
+        .bind(prix_execution)
+        .bind(objet_id)
+        .execute(&mut *tx)
+        .await?;
 
+        // --------------------------------------------------------
+        // Remboursement de la différence pour l'acheteur
+        // --------------------------------------------------------
+        //
+        // L'acheteur avait réservé :
+        //
+        //     prix_achat × quantity
+        //
+        // mais paie réellement :
+        //
+        //     prix_execution × quantity
+        //
+        // La différence lui revient immédiatement.
+        //
 
-    // --------------------------------------------------------
-    // Remboursement de la différence pour l'acheteur
-    // --------------------------------------------------------
-    //
-    // L'acheteur avait réservé :
-    //
-    //     prix_achat × quantity
-    //
-    // mais paie réellement :
-    //
-    //     prix_execution × quantity
-    //
-    // La différence lui revient immédiatement.
-    //
+        let difference_unitaire = prix_achat - prix_execution;
 
-    let difference_unitaire = prix_achat - prix_execution;
-
-    let remboursement = difference_unitaire
-        .checked_mul(quantity)
-        .ok_or_else(|| {
-            sqlx::Error::Protocol(
-                "Le remboursement dépasse la capacité i64".into(),
-            )
+        let remboursement = difference_unitaire.checked_mul(quantity).ok_or_else(|| {
+            sqlx::Error::Protocol("Le remboursement dépasse la capacité i64".into())
         })?;
 
-    // --------------------------------------------------------
-    // Crédit du vendeur
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Crédit du vendeur
+        // --------------------------------------------------------
 
-    WalletManager::crediter_tx(
-        &mut tx,
-        vendeur_id,
-        montant_total,
-    )
-    .await?;
+        WalletManager::crediter_tx(&mut tx, vendeur_id, montant_total).await?;
 
-    // --------------------------------------------------------
-    // Remboursement de l'acheteur
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Remboursement de l'acheteur
+        // --------------------------------------------------------
 
-    if remboursement > 0 {
-        WalletManager::crediter_tx(
+        if remboursement > 0 {
+            WalletManager::crediter_tx(&mut tx, acheteur_id, remboursement).await?;
+        }
+
+        // --------------------------------------------------------
+        // Transfert des objets
+        // --------------------------------------------------------
+
+        Inventaire::ajouter_tx(
             &mut tx,
             acheteur_id,
-            remboursement,
+            objet_id,
+            u64::try_from(quantity)
+                .map_err(|_| sqlx::Error::Protocol("Quantité invalide".into()))?,
         )
         .await?;
-    }
 
-    // --------------------------------------------------------
-    // Transfert des objets
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Mise à jour de l'ordre d'achat
+        // --------------------------------------------------------
 
-    Inventaire::ajouter_tx(
-        &mut tx,
-        acheteur_id,
-        objet_id,
-        u64::try_from(quantity).map_err(|_| {
-            sqlx::Error::Protocol(
-                "Quantité invalide".into(),
-            )
-        })?,
-    )
-    .await?;
+        let nouveau_remaining_achat = achat_remaining - quantity;
 
-    // --------------------------------------------------------
-    // Mise à jour de l'ordre d'achat
-    // --------------------------------------------------------
+        let statut_achat = if nouveau_remaining_achat == 0 {
+            "execute"
+        } else {
+            "actif"
+        };
 
-    let nouveau_remaining_achat = achat_remaining - quantity;
-
-    let statut_achat = if nouveau_remaining_achat == 0 {
-        "execute"
-    } else {
-        "actif"
-    };
-
-    sqlx::query(
-        r#"
+        sqlx::query(
+            r#"
         UPDATE ordres_achat
         SET
             quantity_remaining = ?,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:587:
         WHERE ordre_id = ?
           AND statut = 'actif'
         "#,
-    )
-    .bind(nouveau_remaining_achat)
-    .bind(statut_achat)
-    .bind(ordre_achat_id)
-    .execute(&mut *tx)
-    .await?;
+        )
+        .bind(nouveau_remaining_achat)
+        .bind(statut_achat)
+        .bind(ordre_achat_id)
+        .execute(&mut *tx)
+        .await?;
 
-    // --------------------------------------------------------
-    // Mise à jour de l'ordre de vente
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Mise à jour de l'ordre de vente
+        // --------------------------------------------------------
 
-    let nouveau_remaining_vente = vente_remaining - quantity;
+        let nouveau_remaining_vente = vente_remaining - quantity;
 
-    let statut_vente = if nouveau_remaining_vente == 0 {
-        "execute"
-    } else {
-        "actif"
-    };
+        let statut_vente = if nouveau_remaining_vente == 0 {
+            "execute"
+        } else {
+            "actif"
+        };
 
-    sqlx::query(
-        r#"
+        sqlx::query(
+            r#"
         UPDATE ordres_vente
         SET
             quantity_remaining = ?,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:615:
         WHERE ordre_id = ?
           AND statut = 'actif'
         "#,
-    )
-    .bind(nouveau_remaining_vente)
-    .bind(statut_vente)
-    .bind(ordre_vente_id)
-    .execute(&mut *tx)
-    .await?;
+        )
+        .bind(nouveau_remaining_vente)
+        .bind(statut_vente)
+        .bind(ordre_vente_id)
+        .execute(&mut *tx)
+        .await?;
 
-    // --------------------------------------------------------
-    // Historique
-    // --------------------------------------------------------
+        // --------------------------------------------------------
+        // Historique
+        // --------------------------------------------------------
 
-    let result = sqlx::query(
-        r#"
+        let result = sqlx::query(
+            r#"
         INSERT INTO transactions_marche (
             objet_id,
             ordre_achat_id,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/market_manager.rs:640:
         )
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
         "#,
-    )
-    .bind(objet_id)
-    .bind(ordre_achat_id)
-    .bind(ordre_vente_id)
-    .bind(acheteur_id)
-    .bind(vendeur_id)
-    .bind(quantity)
-    .bind(prix_execution)
-    .bind(montant_total)
-    .execute(&mut *tx)
-    .await?;
+        )
+        .bind(objet_id)
+        .bind(ordre_achat_id)
+        .bind(ordre_vente_id)
+        .bind(acheteur_id)
+        .bind(vendeur_id)
+        .bind(quantity)
+        .bind(prix_execution)
+        .bind(montant_total)
+        .execute(&mut *tx)
+        .await?;
 
-    let transaction_id = result.last_insert_rowid();
+        let transaction_id = result.last_insert_rowid();
 
-    tx.commit().await?;
+        tx.commit().await?;
 
-    Ok(Some(transaction_id))
-}
-    pub async fn matcher_tous(
-    &self,
-    objet_id: i64,
-) -> Result<u64, sqlx::Error> {
-    let mut nombre_transactions = 0u64;
+        Ok(Some(transaction_id))
+    }
+    pub async fn matcher_tous(&self, objet_id: i64) -> Result<u64, sqlx::Error> {
+        let mut nombre_transactions = 0u64;
 
-    loop {
-        match self.matcher_ordre(objet_id).await? {
-            Some(_) => {
-                nombre_transactions += 1;
+        loop {
+            match self.matcher_ordre(objet_id).await? {
+                Some(_) => {
+                    nombre_transactions += 1;
+                }
+                None => {
+                    break;
+                }
             }
-            None => {
-                break;
-            }
         }
-    }
 
-    Ok(nombre_transactions)
-}
+        Ok(nombre_transactions)
+    }
 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/mod.rs:1:
 pub mod dice;
+pub mod market_manager;
 pub mod objets;
-pub mod tresor;
 pub mod stuff_manager;
+pub mod tresor;
 pub mod wallet_manager;
-pub mod market_manager;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:1:
-use serde::{Serialize, Deserialize};
+use serde::{Deserialize, Serialize};
 use std::collections::HashMap;
 
 // Enum pour les types d'objets
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:34:
 }
 
 impl Objet {
-    pub fn new(
-        nom: &str,
-        image: Option<&str>,
-        quantite: u64,
-        type_objet: TypeObjet,
-    ) -> Self {
+    pub fn new(nom: &str, image: Option<&str>, quantite: u64, type_objet: TypeObjet) -> Self {
         Self {
             nom_base: nom.replace(" ", "_"),
             quantite,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:117:
         bonus: i32,
         enchantements: Vec<String>,
     ) -> Self {
-        let  objet = Objet::new(nom, image, quantite, TypeObjet::Equipement);
+        let objet = Objet::new(nom, image, quantite, TypeObjet::Equipement);
         let parts: Vec<&str> = nom.split_whitespace().collect();
         let category = parts.get(0).unwrap_or(&"").to_string();
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:218:
         write!(
             f,
             "{} [Niveau {} | bonus : {} | enchantements : {:?} | dura : {}/{}]",
-            self.equipement.objet.quantite, self.equipement.niv, self.equipement.bonus,
-            self.equipement.enchantements, self.durabilite, self.durabilite_max
+            self.equipement.objet.quantite,
+            self.equipement.niv,
+            self.equipement.bonus,
+            self.equipement.enchantements,
+            self.durabilite,
+            self.durabilite_max
         )
     }
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:232:
 }
 
 impl Potion {
-    pub fn new(
-        nom: &str,
-        image: Option<&str>,
-        quantite: u64,
-        effet: Option<&str>,
-    ) -> Self {
+    pub fn new(nom: &str, image: Option<&str>, quantite: u64, effet: Option<&str>) -> Self {
         let objet = Objet::new(nom, image, quantite, TypeObjet::Potion);
         Self {
             objet,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:307:
     }
 
     /// Ajoute un enchantement en respectant la règle : niveau N du livre => N enchantements max.
-    pub fn ajouter_enchantement(&mut self, nom_enchantement: &str, niveau_enchant: u32) -> Result<(), String> {
+    pub fn ajouter_enchantement(
+        &mut self,
+        nom_enchantement: &str,
+        niveau_enchant: u32,
+    ) -> Result<(), String> {
         let max_enchants = self.niv as usize;
         let enchants = self.enchantements.get_or_insert_with(Vec::new);
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:318:
             ));
         }
 
-        enchants.push(format!("{} {}", nom_enchantement, Self::niv_to_roman(niveau_enchant)));
+        enchants.push(format!(
+            "{} {}",
+            nom_enchantement,
+            Self::niv_to_roman(niveau_enchant)
+        ));
         Ok(())
     }
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/objets.rs:352:
         )
     }
 }
-
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1:
-use sqlx::SqlitePool;
 use serde::{Deserialize, Serialize};
+use sqlx::SqlitePool;
 use std::collections::HashMap;
 use uuid::Uuid;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:6:
 use crate::gameplay::objets::{
-    AjouterRetirer,
-    Arme,
-    Equipement,
-    Livre,
-    NomAffiche,
-    Objet,
-    Potion,
-    TypeObjet,
+    AjouterRetirer, Arme, Equipement, Livre, NomAffiche, Objet, Potion, TypeObjet,
 };
 
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:124:
     // CONSTRUCTEUR
     // ========================================================
 
-    pub async fn new(
-        pool: SqlitePool,
-        account_id: i64,
-    ) -> Result<Self, sqlx::Error> {
+    pub async fn new(pool: SqlitePool, account_id: i64) -> Result<Self, sqlx::Error> {
         let objets = Self::charger_objets(&pool, account_id).await?;
 
         Ok(Self {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:187:
     ) -> Result<ObjetInventaire, sqlx::Error> {
         let quantite = u64::try_from(row.quantity).map_err(|_| {
             sqlx::Error::Protocol(
-                format!(
-                    "Quantité invalide pour {} : {}",
-                    row.nom,
-                    row.quantity
-                )
-                .into(),
+                format!("Quantité invalide pour {} : {}", row.nom, row.quantity).into(),
             )
         })?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:202:
             // ------------------------------------------------
             // ÉQUIPEMENT / ARME
             // ------------------------------------------------
-
             "equipment" | "armes" => {
                 let eq: EquipmentRow = sqlx::query_as(
                     r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:220:
                 .await?
                 .ok_or_else(|| {
                     sqlx::Error::Protocol(
-                        format!(
-                            "Équipement manquant pour stuff_id={}",
-                            row.stuff_id
-                        )
-                        .into(),
+                        format!("Équipement manquant pour stuff_id={}", row.stuff_id).into(),
                     )
                 })?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:231:
                 if eq.equipment_type == "weapon" {
-                    ObjetInventaire::Arme(
-                        Arme::new(
-                            &row.nom,
-                            image,
-                            quantite,
-                            1,
-                            u32::try_from(eq.durability).unwrap_or(0),
-                            i32::try_from(eq.attack).unwrap_or(0),
-                            Vec::new(),
-                        ),
-                    )
+                    ObjetInventaire::Arme(Arme::new(
+                        &row.nom,
+                        image,
+                        quantite,
+                        1,
+                        u32::try_from(eq.durability).unwrap_or(0),
+                        i32::try_from(eq.attack).unwrap_or(0),
+                        Vec::new(),
+                    ))
                 } else {
-                    ObjetInventaire::Equipement(
-                        Equipement::new(
-                            &row.nom,
-                            image,
-                            quantite,
-                            1,
-                            i32::try_from(eq.defense).unwrap_or(0),
-                            Vec::new(),
-                        ),
-                    )
+                    ObjetInventaire::Equipement(Equipement::new(
+                        &row.nom,
+                        image,
+                        quantite,
+                        1,
+                        i32::try_from(eq.defense).unwrap_or(0),
+                        Vec::new(),
+                    ))
                 }
             }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:257:
             // ------------------------------------------------
             // POTION
             // ------------------------------------------------
-
             "potion" => {
                 let potion: PotionRow = sqlx::query_as(
                     r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:271:
                 .await?
                 .ok_or_else(|| {
                     sqlx::Error::Protocol(
-                        format!(
-                            "Potion manquante pour stuff_id={}",
-                            row.stuff_id
-                        )
-                        .into(),
+                        format!("Potion manquante pour stuff_id={}", row.stuff_id).into(),
                     )
                 })?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:282:
-                ObjetInventaire::Potion(
-                    Potion::new(
-                        &row.nom,
-                        image,
-                        quantite,
-                        Some(&potion.effect),
-                    ),
-                )
+                ObjetInventaire::Potion(Potion::new(
+                    &row.nom,
+                    image,
+                    quantite,
+                    Some(&potion.effect),
+                ))
             }
 
             // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:293:
             // LIVRE ENCHANTÉ
             // ------------------------------------------------
-
             "enchanted_book" => {
                 let book: BookRow = sqlx::query_as(
                     r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:308:
                 .await?
                 .ok_or_else(|| {
                     sqlx::Error::Protocol(
-                        format!(
-                            "Livre manquant pour stuff_id={}",
-                            row.stuff_id
-                        )
-                        .into(),
+                        format!("Livre manquant pour stuff_id={}", row.stuff_id).into(),
                     )
                 })?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:319:
-                let enchant_rows: Vec<EnchantRow> =
-                    sqlx::query_as(
-                        r#"
+                let enchant_rows: Vec<EnchantRow> = sqlx::query_as(
+                    r#"
                         SELECT
                             e.enchantment_name,
                             be.enchantment_level
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:329:
                         WHERE be.book_id = ?
                         ORDER BY e.enchantment_name
                         "#,
-                    )
-                    .bind(book.book_id)
-                    .fetch_all(pool)
-                    .await?;
+                )
+                .bind(book.book_id)
+                .fetch_all(pool)
+                .await?;
 
-                let enchantements: Vec<String> =
-                    enchant_rows
-                        .into_iter()
-                        .map(|e| {
-                            format!(
-                                "{} {}",
-                                e.enchantment_name,
-                                Livre::niv_to_roman(
-                                    u32::try_from(
-                                        e.enchantment_level
-                                    )
-                                    .unwrap_or(0),
-                                )
-                            )
-                        })
-                        .collect();
+                let enchantements: Vec<String> = enchant_rows
+                    .into_iter()
+                    .map(|e| {
+                        format!(
+                            "{} {}",
+                            e.enchantment_name,
+                            Livre::niv_to_roman(u32::try_from(e.enchantment_level).unwrap_or(0),)
+                        )
+                    })
+                    .collect();
 
-                ObjetInventaire::Livre(
-                    Livre::new(
-                        &row.nom,
-                        image,
-                        quantite,
-                        None,
-                        Some(enchantements),
-                        u32::try_from(book.book_level)
-                            .unwrap_or(0),
-                    ),
-                )
+                ObjetInventaire::Livre(Livre::new(
+                    &row.nom,
+                    image,
+                    quantite,
+                    None,
+                    Some(enchantements),
+                    u32::try_from(book.book_level).unwrap_or(0),
+                ))
             }
 
             // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:368:
             // OBJET DE BASE
             // ------------------------------------------------
-
-            _ => ObjetInventaire::Base(
-                Objet::new(
-                    &row.nom,
-                    image,
-                    quantite,
-                    TypeObjet::DeBase,
-                ),
-            ),
+            _ => ObjetInventaire::Base(Objet::new(&row.nom, image, quantite, TypeObjet::DeBase)),
         };
 
         Ok(result)
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:385:
     // AJOUT D'UN OBJET
     // ========================================================
 
-    pub async fn ajouter_objet(
-        &mut self,
-        nom: &str,
-        quantite: u64,
-    ) -> Result<(), sqlx::Error> {
+    pub async fn ajouter_objet(&mut self, nom: &str, quantite: u64) -> Result<(), sqlx::Error> {
         if quantite == 0 {
             return Err(sqlx::Error::Protocol(
-                "La quantité à ajouter doit être supérieure à 0"
-                    .into(),
+                "La quantité à ajouter doit être supérieure à 0".into(),
             ));
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:410:
         .fetch_optional(&self.pool)
         .await?
         .ok_or_else(|| {
-            sqlx::Error::Protocol(
-                format!("Objet absent de objets_dispo : {nom}")
-                    .into(),
-            )
+            sqlx::Error::Protocol(format!("Objet absent de objets_dispo : {nom}").into())
         })?;
 
         let objet_id = objet.0;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:421:
 
         match type_objet.as_str() {
             "equipment" | "armes" => {
-                self.ajouter_non_stackable(
-                    objet_id,
-                    &type_objet,
-                    quantite,
-                )
-                .await?;
+                self.ajouter_non_stackable(objet_id, &type_objet, quantite)
+                    .await?;
             }
 
             "potion" => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:433:
-                self.ajouter_potion(
-                    objet_id,
-                    nom,
-                    quantite,
-                )
-                .await?;
+                self.ajouter_potion(objet_id, nom, quantite).await?;
             }
 
             "enchanted_book" => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:442:
-                self.ajouter_livre(
-                    objet_id,
-                    nom,
-                    quantite,
-                )
-                .await?;
+                self.ajouter_livre(objet_id, nom, quantite).await?;
             }
 
             _ => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:451:
-                self.ajouter_objet_base(
-                    objet_id,
-                    quantite,
-                )
-                .await?;
+                self.ajouter_objet_base(objet_id, quantite).await?;
             }
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:467:
     // AJOUT OBJET DE BASE
     // ========================================================
 
-    async fn ajouter_objet_base(
-        &self,
-        objet_id: i64,
-        quantite: u64,
-    ) -> Result<(), sqlx::Error> {
+    async fn ajouter_objet_base(&self, objet_id: i64, quantite: u64) -> Result<(), sqlx::Error> {
         let quantite = Self::quantite_sqlite(quantite)?;
 
         sqlx::query(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:592:
     // EFFET DES POTIONS
     // ========================================================
 
-    fn effet_potion(
-        nom: &str,
-    ) -> Result<String, sqlx::Error> {
+    fn effet_potion(nom: &str) -> Result<String, sqlx::Error> {
         let effet = match nom {
             "potion de soin léger" => "soin_leger",
             "potion de soin modéré" => "soin_modere",
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:630:
         };
 
         for _ in 0..quantite {
-            let stack_key =
-                format!("unique:{}", Uuid::new_v4());
+            let stack_key = format!("unique:{}", Uuid::new_v4());
 
             let stuff_id: i64 = sqlx::query_scalar(
                 r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:674:
         Ok(())
     }
 
-    
     // ========================================================
     // AJOUT LIVRE ENCHANTÉ
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:688:
         let niveau = Self::niveau_livre(nom)?;
 
         for _ in 0..quantite {
-            self.ajouter_un_livre(
-                objet_id,
-                niveau,
-            )
-            .await?;
+            self.ajouter_un_livre(objet_id, niveau).await?;
         }
 
         Ok(())
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:719:
     //
     // ========================================================
 
-    async fn ajouter_un_livre(
-        &self,
-        objet_id: i64,
-        niveau: u32,
-    ) -> Result<(), sqlx::Error> {
+    async fn ajouter_un_livre(&self, objet_id: i64, niveau: u32) -> Result<(), sqlx::Error> {
         // ----------------------------------------------------
         // 1. Chercher les catégories disponibles
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:730:
 
-        let categories: Vec<String> =
-            sqlx::query_scalar(
-                r#"
+        let categories: Vec<String> = sqlx::query_scalar(
+            r#"
                 SELECT DISTINCT equipment_type
                 FROM enchantment_types
                 ORDER BY RANDOM()
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:737:
                 "#,
-            )
-            .fetch_all(&self.pool)
-            .await?;
+        )
+        .fetch_all(&self.pool)
+        .await?;
 
         if categories.is_empty() {
             return Err(sqlx::Error::Protocol(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:752:
         //    d'enchantements pour le niveau demandé
         // ----------------------------------------------------
 
-        let mut categorie_selectionnee: Option<String> =
-            None;
+        let mut categorie_selectionnee: Option<String> = None;
 
         for categorie in &categories {
-            let count: i64 =
-                sqlx::query_scalar(
-                    r#"
+            let count: i64 = sqlx::query_scalar(
+                r#"
                     SELECT COUNT(DISTINCT et.enchantment_id)
                     FROM enchantment_types et
                     JOIN enchantment_levels el
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:767:
                     WHERE et.equipment_type = ?
                       AND el.book_level = ?
                     "#,
-                )
-                .bind(categorie)
-                .bind(i64::from(niveau))
-                .fetch_one(&self.pool)
-                .await?;
+            )
+            .bind(categorie)
+            .bind(i64::from(niveau))
+            .fetch_one(&self.pool)
+            .await?;
 
             if count >= i64::from(niveau) {
-                categorie_selectionnee =
-                    Some(categorie.clone());
+                categorie_selectionnee = Some(categorie.clone());
 
                 break;
             }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:785:
         // 3. Choisir une catégorie de secours si nécessaire
         // ----------------------------------------------------
 
-        let categorie =
-            categorie_selectionnee
-                .or_else(|| categories.first().cloned())
-                .ok_or_else(|| {
-                    sqlx::Error::Protocol(
-                        "Impossible de sélectionner une \
+        let categorie = categorie_selectionnee
+            .or_else(|| categories.first().cloned())
+            .ok_or_else(|| {
+                sqlx::Error::Protocol(
+                    "Impossible de sélectionner une \
                          catégorie d'enchantement"
-                            .into(),
-                    )
-                })?;
+                        .into(),
+                )
+            })?;
 
         // ----------------------------------------------------
         // 4. Sélectionner les enchantements
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:801:
         // ----------------------------------------------------
 
-        let enchantements: Vec<GeneratedEnchant> =
-            sqlx::query_as(
-                r#"
+        let enchantements: Vec<GeneratedEnchant> = sqlx::query_as(
+            r#"
                 SELECT DISTINCT
                     et.enchantment_id,
                     el.max_enchantment_level AS max_level
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:815:
                 ORDER BY RANDOM()
                 LIMIT ?
                 "#,
-            )
-            .bind(&categorie)
-            .bind(i64::from(niveau))
-            .bind(i64::from(niveau))
-            .fetch_all(&self.pool)
-            .await?;
+        )
+        .bind(&categorie)
+        .bind(i64::from(niveau))
+        .bind(i64::from(niveau))
+        .fetch_all(&self.pool)
+        .await?;
 
         if enchantements.is_empty() {
             return Err(sqlx::Error::Protocol(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:836:
         // 5. Générer le niveau de chaque enchantement
         // ----------------------------------------------------
 
-        let mut enchantement_data: Vec<(i64, i64)> =
-            Vec::with_capacity(enchantements.len());
+        let mut enchantement_data: Vec<(i64, i64)> = Vec::with_capacity(enchantements.len());
 
         for enchantement in enchantements {
-            let maximum =
-                std::cmp::min(
-                    i64::from(niveau),
-                    enchantement.max_level,
-                );
+            let maximum = std::cmp::min(i64::from(niveau), enchantement.max_level);
 
             if maximum <= 0 {
                 return Err(sqlx::Error::Protocol(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:857:
                 ));
             }
 
-            let niveau_enchantement: i64 =
-                sqlx::query_scalar(
-                    r#"
+            let niveau_enchantement: i64 = sqlx::query_scalar(
+                r#"
                     SELECT
                         1 + (
                             abs(random()) % ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:866:
                         )
                     "#,
-                )
-                .bind(maximum)
-                .fetch_one(&self.pool)
-                .await?;
+            )
+            .bind(maximum)
+            .fetch_one(&self.pool)
+            .await?;
 
-            enchantement_data.push((
-                enchantement.enchantment_id,
-                niveau_enchantement,
-            ));
+            enchantement_data.push((enchantement.enchantment_id, niveau_enchantement));
         }
 
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:883:
         // l'identité du livre.
         // ----------------------------------------------------
 
-        enchantement_data.sort_by_key(
-            |(enchantment_id, level)| {
-                (*enchantment_id, *level)
-            },
-        );
+        enchantement_data.sort_by_key(|(enchantment_id, level)| (*enchantment_id, *level));
 
         // ----------------------------------------------------
         // 7. Générer la stack_key canonique
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:895:
 
         let contenu = enchantement_data
             .iter()
-            .map(|(id, level)| {
-                format!("{id}:{level}")
-            })
+            .map(|(id, level)| format!("{id}:{level}"))
             .collect::<Vec<_>>()
             .join("|");
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:904:
-        let stack_key =
-            format!("book:{niveau}:{contenu}");
+        let stack_key = format!("book:{niveau}:{contenu}");
 
         // ====================================================
         // 8. TRANSACTION D'ÉCRITURE
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:924:
         // 9. Créer le stack ou augmenter sa quantité
         // ----------------------------------------------------
 
-        let stuff_id: i64 =
-            sqlx::query_scalar(
-                r#"
+        let stuff_id: i64 = sqlx::query_scalar(
+            r#"
                 INSERT INTO stuff (
                     account_id,
                     objet_id,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:946:
 
                 RETURNING stuff_id
                 "#,
-            )
-            .bind(self.account_id)
-            .bind(objet_id)
-            .bind(&stack_key)
-            .fetch_one(&mut *tx)
-            .await?;
+        )
+        .bind(self.account_id)
+        .bind(objet_id)
+        .bind(&stack_key)
+        .fetch_one(&mut *tx)
+        .await?;
 
         // ----------------------------------------------------
         // 10. Vérifier si le livre existe déjà
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:958:
         // ----------------------------------------------------
 
-        let book_id: Option<i64> =
-            sqlx::query_scalar(
-                r#"
+        let book_id: Option<i64> = sqlx::query_scalar(
+            r#"
                 SELECT book_id
                 FROM enchanted_books
                 WHERE stuff_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:966:
                 "#,
-            )
-            .bind(stuff_id)
-            .fetch_optional(&mut *tx)
-            .await?;
+        )
+        .bind(stuff_id)
+        .fetch_optional(&mut *tx)
+        .await?;
 
         // ----------------------------------------------------
         // Le livre existait déjà.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:985:
         // 11. Créer le livre
         // ----------------------------------------------------
 
-        let book_id: i64 =
-            sqlx::query_scalar(
-                r#"
+        let book_id: i64 = sqlx::query_scalar(
+            r#"
                 INSERT INTO enchanted_books (
                     stuff_id,
                     book_level
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:995:
                 VALUES (?, ?)
                 RETURNING book_id
                 "#,
-            )
-            .bind(stuff_id)
-            .bind(i64::from(niveau))
-            .fetch_one(&mut *tx)
-            .await?;
+        )
+        .bind(stuff_id)
+        .bind(i64::from(niveau))
+        .fetch_one(&mut *tx)
+        .await?;
 
         // ----------------------------------------------------
         // 12. Insérer les enchantements
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1006:
         // ----------------------------------------------------
 
-        for (
-            enchantment_id,
-            enchantment_level,
-        ) in enchantement_data
-        {
+        for (enchantment_id, enchantment_level) in enchantement_data {
             sqlx::query(
                 r#"
                 INSERT INTO book_enchantments (
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1040:
     // EXTRACTION DU NIVEAU DU LIVRE
     // ========================================================
 
-    fn niveau_livre(
-        nom: &str,
-    ) -> Result<u32, sqlx::Error> {
+    fn niveau_livre(nom: &str) -> Result<u32, sqlx::Error> {
         let prefix = "livre enchant niv ";
 
         let niveau = nom
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1049:
             .strip_prefix(prefix)
-            .ok_or_else(|| {
-                sqlx::Error::Protocol(
-                    format!(
-                        "Nom de livre invalide : {nom}"
-                    )
-                    .into(),
-                )
-            })?
+            .ok_or_else(|| sqlx::Error::Protocol(format!("Nom de livre invalide : {nom}").into()))?
             .parse::<u32>()
             .map_err(|_| {
-                sqlx::Error::Protocol(
-                    format!(
-                        "Niveau de livre invalide : {nom}"
-                    )
-                    .into(),
-                )
+                sqlx::Error::Protocol(format!("Niveau de livre invalide : {nom}").into())
             })?;
 
         if !(1..=6).contains(&niveau) {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1069:
             return Err(sqlx::Error::Protocol(
-                format!(
-                    "Niveau de livre hors limites : {niveau}"
-                )
-                .into(),
+                format!("Niveau de livre hors limites : {niveau}").into(),
             ));
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1081:
     // RETRAIT D'UN OBJET
     // ========================================================
 
-    pub async fn retirer_objet(
-        &mut self,
-        stuff_id: i64,
-        quantite: u64,
-    ) -> Result<(), sqlx::Error> {
+    pub async fn retirer_objet(&mut self, stuff_id: i64, quantite: u64) -> Result<(), sqlx::Error> {
         if quantite == 0 {
             return Err(sqlx::Error::Protocol(
-                "La quantité à retirer doit être supérieure à 0"
-                    .into(),
+                "La quantité à retirer doit être supérieure à 0".into(),
             ));
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1096:
-        let quantite_i64 =
-            Self::quantite_sqlite(quantite)?;
+        let quantite_i64 = Self::quantite_sqlite(quantite)?;
 
         // ----------------------------------------------------
         // Vérification mémoire
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1124:
         .await?
         .ok_or(sqlx::Error::RowNotFound)?;
 
-        let quantite_actuelle = u64::try_from(quantite_db)
-            .map_err(|_| {
-                sqlx::Error::Protocol(
-                    format!(
-                        "Quantité invalide pour stuff_id={stuff_id}"
-                    )
-                    .into(),
-                )
-            })?;
+        let quantite_actuelle = u64::try_from(quantite_db).map_err(|_| {
+            sqlx::Error::Protocol(format!("Quantité invalide pour stuff_id={stuff_id}").into())
+        })?;
 
         if quantite > quantite_actuelle {
             return Err(sqlx::Error::Protocol(
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1139:
                 format!(
                     "Quantité insuffisante : possède {}, \
                      demande {}",
-                    quantite_actuelle,
-                    quantite
+                    quantite_actuelle, quantite
                 )
                 .into(),
             ));
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1202:
 
         if quantite == quantite_actuelle {
             self.objets.remove(&stuff_id);
-        } else if let Some(objet) =
-            self.objets.get_mut(&stuff_id)
-        {
+        } else if let Some(objet) = self.objets.get_mut(&stuff_id) {
             objet.retirer(quantite);
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1223:
     ) -> Result<(), sqlx::Error> {
         if quantite == 0 {
             return Err(sqlx::Error::Protocol(
-                "La quantité à retirer doit être supérieure à 0"
-                    .into(),
+                "La quantité à retirer doit être supérieure à 0".into(),
             ));
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1231:
-        let quantite_i64 =
-            Self::quantite_sqlite(quantite)?;
+        let quantite_i64 = Self::quantite_sqlite(quantite)?;
 
-        let quantity: Option<i64> =
-            sqlx::query_scalar(
-                r#"
+        let quantity: Option<i64> = sqlx::query_scalar(
+            r#"
                 SELECT quantity
                 FROM stuff
                 WHERE account_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1240:
                   AND objet_id = ?
                   AND stack_key = 'base'
                 "#,
-            )
-            .bind(account_id)
-            .bind(objet_id)
-            .fetch_optional(&mut **tx)
-            .await?;
+        )
+        .bind(account_id)
+        .bind(objet_id)
+        .fetch_optional(&mut **tx)
+        .await?;
 
-        let quantity =
-            quantity.unwrap_or(0);
+        let quantity = quantity.unwrap_or(0);
 
         if quantity < quantite_i64 {
-            return Err(sqlx::Error::Protocol(
-                "Quantité insuffisante".into(),
-            ));
+            return Err(sqlx::Error::Protocol("Quantité insuffisante".into()));
         }
 
         if quantity == quantite_i64 {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1302:
     ) -> Result<(), sqlx::Error> {
         if quantite == 0 {
             return Err(sqlx::Error::Protocol(
-                "La quantité à ajouter doit être supérieure à 0"
-                    .into(),
+                "La quantité à ajouter doit être supérieure à 0".into(),
             ));
         }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1310:
-        let quantite_i64 =
-            Self::quantite_sqlite(quantite)?;
+        let quantite_i64 = Self::quantite_sqlite(quantite)?;
 
         sqlx::query(
             r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1343:
     // QUANTITÉ TOTALE D'UN OBJET PAR NOM
     // ========================================================
 
-    pub async fn get_quantity(
-        &self,
-        nom: &str,
-    ) -> Result<u64, sqlx::Error> {
-        let quantity: i64 =
-            sqlx::query_scalar(
-                r#"
+    pub async fn get_quantity(&self, nom: &str) -> Result<u64, sqlx::Error> {
+        let quantity: i64 = sqlx::query_scalar(
+            r#"
                 SELECT COALESCE(
                     SUM(s.quantity),
                     0
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1360:
                 WHERE s.account_id = ?
                   AND o.nom = ?
                 "#,
-            )
-            .bind(self.account_id)
-            .bind(nom)
-            .fetch_one(&self.pool)
-            .await?;
+        )
+        .bind(self.account_id)
+        .bind(nom)
+        .fetch_one(&self.pool)
+        .await?;
 
         u64::try_from(quantity)
-            .map_err(|_| {
-                sqlx::Error::Protocol(
-                    format!(
-                        "Quantité invalide pour {nom}"
-                    )
-                    .into(),
-                )
-            })
+            .map_err(|_| sqlx::Error::Protocol(format!("Quantité invalide pour {nom}").into()))
     }
 
-    
     // ========================================================
     // CONVERSION QUANTITÉ SQLITE
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1394:
         })
     }
 
-    
-
     // ========================================================
     // ACCÈS À L'INVENTAIRE
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/stuff_manager.rs:1413:
     // ========================================================
 
     pub async fn recharger(&mut self) -> Result<(), sqlx::Error> {
-        self.objets = Self::charger_objets(
-            &self.pool,
-            self.account_id,
-        )
-        .await?;
+        self.objets = Self::charger_objets(&self.pool, self.account_id).await?;
 
         Ok(())
     }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1:
-use rand::{Rng,RngExt};
-use sqlx::SqlitePool;
-use std::collections::HashMap;
 use crate::gameplay::dice::jet_de_des;
 use log::{debug, error, info};
+use rand::{Rng, RngExt};
+use sqlx::SqlitePool;
+use std::collections::HashMap;
 
 const PA: u32 = 1;
 const PO: u32 = PA * 10;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:22:
 
 #[derive(Debug, Clone)]
 pub struct Tresor {
-    
     pub loot_par_niveau: HashMap<u32, Loot>,
 
     pub objets_garantis: HashMap<u32, HashMap<String, u32>>,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:34:
     pub seuil_artefact_rare: HashMap<u32, u32>,
     pub seuil_artefact_super_rare: HashMap<u32, u32>,
     pub sous_loot: HashMap<String, HashMap<String, f64>>,
-    
+
     pub sous_loot_livre_normal: HashMap<String, f64>,
     pub sous_loot_livre_admin: HashMap<String, f64>,
-    
+
     pub coeff_loot: f64,
 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:172:
                 militaire: 2,
             },
         );
-         loot_par_niveau.insert(
+        loot_par_niveau.insert(
             10,
             Loot {
                 commun: 2,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:247:
         // Niveau 1
         let mut niveau_1 = HashMap::new();
 
-        niveau_1.insert(
-            "argent".to_string(),
-            jet_de_des(6, 2) * PA,
-        );
+        niveau_1.insert("argent".to_string(), jet_de_des(6, 2) * PA);
 
         niveau_1.insert("torche".to_string(), 2);
         niveau_1.insert("sac".to_string(), 3);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:263:
 
         // 17 chances sur 20 : pain
         if jet_de_des(20, 1) >= 4 {
-            niveau_1.insert(
-                "pain".to_string(),
-                rng.random_range(3..=5),
-            );
+            niveau_1.insert("pain".to_string(), rng.random_range(3..=5));
         }
 
         objets_garantis.insert(1, niveau_1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:274:
         // Niveau 2
         let mut niveau_2 = HashMap::new();
 
-        niveau_2.insert(
-            "argent".to_string(),
-            jet_de_des(6, 4) * PA,
-        );
+        niveau_2.insert("argent".to_string(), jet_de_des(6, 4) * PA);
 
         niveau_2.insert("torche".to_string(), 1);
         niveau_2.insert("sac".to_string(), 2);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:292:
         // Niveau 3
         let mut niveau_3 = HashMap::new();
 
-        niveau_3.insert(
-            "argent".to_string(),
-            jet_de_des(6, 1) * 10 * PA,
-        );
+        niveau_3.insert("argent".to_string(), jet_de_des(6, 1) * 10 * PA);
 
         niveau_3.insert("torche".to_string(), 2);
         niveau_3.insert("sac".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:310:
         // Niveau 4
         let mut niveau_4 = HashMap::new();
 
-        niveau_4.insert(
-            "argent".to_string(),
-            jet_de_des(6, 2) * 10 * PA,
-        );
+        niveau_4.insert("argent".to_string(), jet_de_des(6, 2) * 10 * PA);
 
         if jet_de_des(20, 1) >= 12 {
             niveau_4.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:324:
         // Niveau 5
         let mut niveau_5 = HashMap::new();
 
-        niveau_5.insert(
-            "argent".to_string(),
-            jet_de_des(6, 3) * 10 * PA,
-        );
+        niveau_5.insert("argent".to_string(), jet_de_des(6, 3) * 10 * PA);
 
         if jet_de_des(20, 1) >= 10 {
             niveau_5.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:336:
         objets_garantis.insert(5, niveau_5);
         let mut niveau_6 = HashMap::new();
 
-        niveau_6.insert(
-            "argent".to_string(),
-            jet_de_des(6, 4) * 10 * PA,
-        );
+        niveau_6.insert("argent".to_string(), jet_de_des(6, 4) * 10 * PA);
 
         if jet_de_des(20, 1) >= 8 {
             niveau_6.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:348:
         objets_garantis.insert(6, niveau_6);
         let mut niveau_7 = HashMap::new();
 
-        niveau_7.insert(
-            "argent".to_string(),
-            jet_de_des(6, 5) * 10 * PA,
-        );
+        niveau_7.insert("argent".to_string(), jet_de_des(6, 5) * 10 * PA);
 
         if jet_de_des(20, 1) >= 6 {
             niveau_7.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:360:
         objets_garantis.insert(7, niveau_7);
         let mut niveau_8 = HashMap::new();
 
-        niveau_8.insert(
-            "argent".to_string(),
-            jet_de_des(6, 1) * 100 * PA,
-        );
+        niveau_8.insert("argent".to_string(), jet_de_des(6, 1) * 100 * PA);
 
         if jet_de_des(20, 1) >= 4 {
             niveau_8.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:372:
         objets_garantis.insert(8, niveau_8);
         let mut niveau_9 = HashMap::new();
 
-        niveau_9.insert(
-            "argent".to_string(),
-            jet_de_des(6, 2) * 100 * PA,
-        );
+        niveau_9.insert("argent".to_string(), jet_de_des(6, 2) * 100 * PA);
 
         if jet_de_des(20, 1) >= 2 {
             niveau_9.insert("gemmes".to_string(), 1);
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:384:
         objets_garantis.insert(9, niveau_9);
         let mut niveau_10 = HashMap::new();
 
-        niveau_10.insert(
-            "argent".to_string(),
-            jet_de_des(6, 3) * 100 * PA,
-        );
+        niveau_10.insert("argent".to_string(), jet_de_des(6, 3) * 100 * PA);
         niveau_10.insert("gemmes".to_string(), 1);
-        
+
         objets_garantis.insert(10, niveau_10);
         let mut niveau_11 = HashMap::new();
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:396:
-        niveau_11.insert(
-            "argent".to_string(),
-            jet_de_des(6, 4) * 100 * PA,
-        );
+        niveau_11.insert("argent".to_string(), jet_de_des(6, 4) * 100 * PA);
         niveau_11.insert("gemmes".to_string(), 1);
-        
+
         objets_garantis.insert(11, niveau_11);
         let mut niveau_12 = HashMap::new();
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:405:
-        niveau_12.insert(
-            "argent".to_string(),
-            jet_de_des(6, 5) * 100 * PA,
-        );
+        niveau_12.insert("argent".to_string(), jet_de_des(6, 5) * 100 * PA);
         niveau_12.insert("gemmes".to_string(), 1);
-        
+
         objets_garantis.insert(12, niveau_12);
         let mut niveau_13 = HashMap::new();
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:414:
-        niveau_13.insert(
-            "argent".to_string(),
-            jet_de_des(6, 1) * 100 * PO,
-        );
+        niveau_13.insert("argent".to_string(), jet_de_des(6, 1) * 100 * PO);
         niveau_13.insert("gemmes".to_string(), 1);
-        
+
         objets_garantis.insert(13, niveau_13);
         let mut niveau_14 = HashMap::new();
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:423:
-        niveau_14.insert(
-            "argent".to_string(),
-            jet_de_des(6, 2) * 100 * PO,
-        );
+        niveau_14.insert("argent".to_string(), jet_de_des(6, 2) * 100 * PO);
         niveau_14.insert("gemmes".to_string(), 1);
-        
+
         objets_garantis.insert(14, niveau_14);
 
-        
-
         // -------------------------------------------------
         // QUANTITÉS DES OBJETS
         // -------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:454:
             "flèches épiques",
             "flèches légendaires",
         ] {
-            quantite_objets.insert(
-                objet.to_string(),
-                rng.random_range(2..=9),
-            );
+            quantite_objets.insert(objet.to_string(), rng.random_range(2..=9));
         }
-        let mut sous_loot: HashMap<String, HashMap<String, f64>> =
-    HashMap::new();
+        let mut sous_loot: HashMap<String, HashMap<String, f64>> = HashMap::new();
         sous_loot.insert(
-    "Artefact commun".to_string(),
-    HashMap::from([
-        ("food".to_string(), 80.0),
-        ("minerais".to_string(), 19.0),
-        ("équi".to_string(), 1.0),
-    ]),
-);
+            "Artefact commun".to_string(),
+            HashMap::from([
+                ("food".to_string(), 80.0),
+                ("minerais".to_string(), 19.0),
+                ("équi".to_string(), 1.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact peu commun".to_string(),
-    HashMap::from([
-        ("food".to_string(), 50.0),
-        ("minerais".to_string(), 40.0),
-        ("équi".to_string(), 10.0),
-    ]),
-);
+            "Artefact peu commun".to_string(),
+            HashMap::from([
+                ("food".to_string(), 50.0),
+                ("minerais".to_string(), 40.0),
+                ("équi".to_string(), 10.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact rare".to_string(),
-    HashMap::from([
-        ("minerais".to_string(), 50.0),
-        ("équi".to_string(), 25.0),
-        ("potion".to_string(), 25.0),
-    ]),
-);
+            "Artefact rare".to_string(),
+            HashMap::from([
+                ("minerais".to_string(), 50.0),
+                ("équi".to_string(), 25.0),
+                ("potion".to_string(), 25.0),
+            ]),
+        );
         sous_loot.insert(
-    "food".to_string(),
-    HashMap::from([
-        ("viande".to_string(), 10.0),
-        ("pain".to_string(), 70.0),
-        ("fruit et légumes".to_string(), 10.0),
-        ("herbes et racines".to_string(), 10.0),
-        ("tacos".to_string(), 10.0),
-        ("burger".to_string(), 10.0),
-        ("sushi".to_string(), 10.0),
-        ("boulette de riz".to_string(), 10.0),
-        ("sucrerie".to_string(), 10.0),
-        
-    ]),
-);  
+            "food".to_string(),
+            HashMap::from([
+                ("viande".to_string(), 10.0),
+                ("pain".to_string(), 70.0),
+                ("fruit et légumes".to_string(), 10.0),
+                ("herbes et racines".to_string(), 10.0),
+                ("tacos".to_string(), 10.0),
+                ("burger".to_string(), 10.0),
+                ("sushi".to_string(), 10.0),
+                ("boulette de riz".to_string(), 10.0),
+                ("sucrerie".to_string(), 10.0),
+            ]),
+        );
         // La liste de viande pourra être extendue
         sous_loot.insert(
-    "viande".to_string(),
-    HashMap::from([
-        ("mouton".to_string(), 10.0),
-        ("cerf".to_string(), 3.0),
-        ("sanglier".to_string(), 2.0),
-        ("pigeon".to_string(), 4.0),
-        ("poulet".to_string(), 10.0),
-        ("porc".to_string(), 10.0),
-        ("boeuf".to_string(), 10.0),
-        ("agneau".to_string(), 10.0),
-        ("veau".to_string(), 10.0),
-        ("karage".to_string(), 10.0),
-        ("calamar".to_string(), 10.0),
-        ("morue".to_string(), 10.0),
-        ("crabe".to_string(), 10.0),
-        ("saumon".to_string(), 10.0),
-        ("thon".to_string(), 10.0),
-        ("fugu".to_string(), 10.0),
-        ("poisson globe".to_string(), 10.0),
-        ("sashimi".to_string(), 10.0),
-
-        
-    ]),
-);
+            "viande".to_string(),
+            HashMap::from([
+                ("mouton".to_string(), 10.0),
+                ("cerf".to_string(), 3.0),
+                ("sanglier".to_string(), 2.0),
+                ("pigeon".to_string(), 4.0),
+                ("poulet".to_string(), 10.0),
+                ("porc".to_string(), 10.0),
+                ("boeuf".to_string(), 10.0),
+                ("agneau".to_string(), 10.0),
+                ("veau".to_string(), 10.0),
+                ("karage".to_string(), 10.0),
+                ("calamar".to_string(), 10.0),
+                ("morue".to_string(), 10.0),
+                ("crabe".to_string(), 10.0),
+                ("saumon".to_string(), 10.0),
+                ("thon".to_string(), 10.0),
+                ("fugu".to_string(), 10.0),
+                ("poisson globe".to_string(), 10.0),
+                ("sashimi".to_string(), 10.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact super rare".to_string(),
-    HashMap::from([
-        ("potion".to_string(), 50.0),
-        ("équi".to_string(), 40.0),
-        ("minerais".to_string(), 9.9),
-        ("livre enchant".to_string(), 0.1),
-    ]),
-);
+            "Artefact super rare".to_string(),
+            HashMap::from([
+                ("potion".to_string(), 50.0),
+                ("équi".to_string(), 40.0),
+                ("minerais".to_string(), 9.9),
+                ("livre enchant".to_string(), 0.1),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact epique".to_string(),
-    HashMap::from([
-        ("potion".to_string(), 15.0),
-        ("équi".to_string(), 75.0),
-        ("livre enchant".to_string(), 10.0),
-        
-    ]),
-);
+            "Artefact epique".to_string(),
+            HashMap::from([
+                ("potion".to_string(), 15.0),
+                ("équi".to_string(), 75.0),
+                ("livre enchant".to_string(), 10.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact legendaire".to_string(),
-    HashMap::from([
-        ("potion".to_string(), 5.0),
-        ("équi".to_string(), 75.0),
-        ("livre enchant".to_string(), 20.0),
-        
-    ]),
-);
+            "Artefact legendaire".to_string(),
+            HashMap::from([
+                ("potion".to_string(), 5.0),
+                ("équi".to_string(), 75.0),
+                ("livre enchant".to_string(), 20.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact militaire".to_string(),
-    HashMap::from([
-        ("matos".to_string(), 5.0),
-        ("parachute".to_string(), 5.0),
-        ("equi".to_string(), 5.0),
-        ("ogive".to_string(), 5.0),
-        ("combinaison anti g".to_string(), 5.0),
-        
-        
-    ]),
-);
+            "Artefact militaire".to_string(),
+            HashMap::from([
+                ("matos".to_string(), 5.0),
+                ("parachute".to_string(), 5.0),
+                ("equi".to_string(), 5.0),
+                ("ogive".to_string(), 5.0),
+                ("combinaison anti g".to_string(), 5.0),
+            ]),
+        );
         sous_loot.insert(
-    "Artefact admin".to_string(),
-    HashMap::from([
-        ("livre enchant".to_string(), 100.0),
-        
-    ]),
-);
+            "Artefact admin".to_string(),
+            HashMap::from([("livre enchant".to_string(), 100.0)]),
+        );
         sous_loot.insert(
-    "équi".to_string(),
-    HashMap::from([
-        ("armes".to_string(), 20.0),
-        ("outils".to_string(), 20.0),
-        ("armure".to_string(), 20.0),
-        ("véhicules".to_string(), 20.0),
-        ("batiments".to_string(), 20.0),
-        ("combinaisons".to_string(), 3.0),
-        
-        
-        
-    ]),
-);
-sous_loot.insert(
-    "armes".to_string(),
-    HashMap::from([
-        ("armes de contact".to_string(), 20.0),
-        ("armes explosives".to_string(), 20.0),
-        ("armes à distance".to_string(), 20.0),
-        ("armes à feux".to_string(), 20.0),
-        ("armes magiques".to_string(), 20.0),
-        
-        
-        
-        
-    ]),
-);
-           sous_loot.insert(
-    "véhicules".to_string(),
-    HashMap::from([
-        ("avions".to_string(), 20.0),
-        ("bus T2C".to_string(), 20.0),
-        ("sous-marin".to_string(), 20.0),
-        ("drones".to_string(), 20.0),
-        ("voitures".to_string(), 20.0),
-        ("tanks".to_string(), 20.0),
-        ("bateaux".to_string(), 20.0),
-        
-        
-    ]),
-); 
+            "équi".to_string(),
+            HashMap::from([
+                ("armes".to_string(), 20.0),
+                ("outils".to_string(), 20.0),
+                ("armure".to_string(), 20.0),
+                ("véhicules".to_string(), 20.0),
+                ("batiments".to_string(), 20.0),
+                ("combinaisons".to_string(), 3.0),
+            ]),
+        );
+        sous_loot.insert(
+            "armes".to_string(),
+            HashMap::from([
+                ("armes de contact".to_string(), 20.0),
+                ("armes explosives".to_string(), 20.0),
+                ("armes à distance".to_string(), 20.0),
+                ("armes à feux".to_string(), 20.0),
+                ("armes magiques".to_string(), 20.0),
+            ]),
+        );
+        sous_loot.insert(
+            "véhicules".to_string(),
+            HashMap::from([
+                ("avions".to_string(), 20.0),
+                ("bus T2C".to_string(), 20.0),
+                ("sous-marin".to_string(), 20.0),
+                ("drones".to_string(), 20.0),
+                ("voitures".to_string(), 20.0),
+                ("tanks".to_string(), 20.0),
+                ("bateaux".to_string(), 20.0),
+            ]),
+        );
 
-            
         let seuil_artefact_commun: HashMap<u32, u32> = HashMap::from([
-    (2, 20),
-    (3, 19),
-    (4, 17),
-    (5, 15),
-    (6, 15),
-    (7, 14),
-    (8, 13),
-    (9, 12),
-    (10,11),
-    (11,10),
-    (12,10),
-    (13,9),
-    (14,8),
-]);
+            (2, 20),
+            (3, 19),
+            (4, 17),
+            (5, 15),
+            (6, 15),
+            (7, 14),
+            (8, 13),
+            (9, 12),
+            (10, 11),
+            (11, 10),
+            (12, 10),
+            (13, 9),
+            (14, 8),
+        ]);
         let seuil_artefact_peu_commun: HashMap<u32, u32> = HashMap::from([
-    (6, 20),
-    (7, 19),
-    (8,17),
-    (9, 15),
-    (10,15),
-    (11,14),
-    (12,13),
-    (13,12),
-    (14,11),
-
-
-]);
-        let seuil_artefact_rare: HashMap<u32, u32> = HashMap::from([
-    (10, 20),
-    (11,19),
-    (12,17),
-    (13,15),
-    (14,15),
-
-]);
-let seuil_artefact_super_rare: HashMap<u32, u32> = HashMap::from([
-    (14, 20),
-    
-
-]);
+            (6, 20),
+            (7, 19),
+            (8, 17),
+            (9, 15),
+            (10, 15),
+            (11, 14),
+            (12, 13),
+            (13, 12),
+            (14, 11),
+        ]);
+        let seuil_artefact_rare: HashMap<u32, u32> =
+            HashMap::from([(10, 20), (11, 19), (12, 17), (13, 15), (14, 15)]);
+        let seuil_artefact_super_rare: HashMap<u32, u32> = HashMap::from([(14, 20)]);
         let sous_loot_livre_normal = HashMap::from([
-    ("livre enchant niv 1".to_string(), 70.0),
-    ("livre enchant niv 2".to_string(), 20.0),
-    ("livre enchant niv 3".to_string(), 5.0),
-    ("livre enchant niv 4".to_string(), 3.0),
-    ("livre enchant niv 5".to_string(), 1.5),
-    ("livre enchant niv 6".to_string(), 0.5),
-]);
+            ("livre enchant niv 1".to_string(), 70.0),
+            ("livre enchant niv 2".to_string(), 20.0),
+            ("livre enchant niv 3".to_string(), 5.0),
+            ("livre enchant niv 4".to_string(), 3.0),
+            ("livre enchant niv 5".to_string(), 1.5),
+            ("livre enchant niv 6".to_string(), 0.5),
+        ]);
 
-let sous_loot_livre_admin = HashMap::from([
-    ("livre enchant niv 1".to_string(), 45.0),
-    ("livre enchant niv 2".to_string(), 15.0),
-    ("livre enchant niv 3".to_string(), 13.0),
-    ("livre enchant niv 4".to_string(), 12.0),
-    ("livre enchant niv 5".to_string(), 8.0),
-    ("livre enchant niv 6".to_string(), 7.0),
-]);
-        
+        let sous_loot_livre_admin = HashMap::from([
+            ("livre enchant niv 1".to_string(), 45.0),
+            ("livre enchant niv 2".to_string(), 15.0),
+            ("livre enchant niv 3".to_string(), 13.0),
+            ("livre enchant niv 4".to_string(), 12.0),
+            ("livre enchant niv 5".to_string(), 8.0),
+            ("livre enchant niv 6".to_string(), 7.0),
+        ]);
 
         Self {
             loot_par_niveau,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:688:
             sous_loot_livre_normal,
             sous_loot_livre_admin,
             coeff_loot: 1.0,
-        
         }
     }
-    
-      pub async fn ouvrir(
-    &mut self,
-    pool: &SqlitePool,
-    account_id: i64,
-    niveau: u32,
-    is_admin: bool,
-    is_militaire: bool,
-    coeff_loot: Option<f64>,
-) -> Result<HashMap<String, u32>, sqlx::Error> {
-    // Mise à jour du coefficient de loot avec valeur par défaut 1.0
-    self.coeff_loot = coeff_loot.unwrap_or(1.0);
-    
-    let mut rng = rand::rng();
 
-    let loot = self
-        .loot_par_niveau
-        .get(&niveau)
-        .cloned()
-        .expect("Niveau de coffre invalide");
+    pub async fn ouvrir(
+        &mut self,
+        pool: &SqlitePool,
+        account_id: i64,
+        niveau: u32,
+        is_admin: bool,
+        is_militaire: bool,
+        coeff_loot: Option<f64>,
+    ) -> Result<HashMap<String, u32>, sqlx::Error> {
+        // Mise à jour du coefficient de loot avec valeur par défaut 1.0
+        self.coeff_loot = coeff_loot.unwrap_or(1.0);
 
-    let mut objets = HashMap::new();
+        let mut rng = rand::rng();
 
-    // ==========================================
-    // OBJETS GARANTIS
-    // ==========================================
+        let loot = self
+            .loot_par_niveau
+            .get(&niveau)
+            .cloned()
+            .expect("Niveau de coffre invalide");
 
-    if let Some(garantis) = self.objets_garantis.get(&niveau) {
-        for (objet, quantite) in garantis {
-            *objets.entry(objet.clone()).or_insert(0) += *quantite;
+        let mut objets = HashMap::new();
+
+        // ==========================================
+        // OBJETS GARANTIS
+        // ==========================================
+
+        if let Some(garantis) = self.objets_garantis.get(&niveau) {
+            for (objet, quantite) in garantis {
+                *objets.entry(objet.clone()).or_insert(0) += *quantite;
+            }
         }
-    }
 
-    // ==========================================
-    // OBJETS COMMUNS
-    // ==========================================
+        // ==========================================
+        // OBJETS COMMUNS
+        // ==========================================
 
-    for _ in 0..loot.commun {
-        let seuil = self
-            .seuil_artefact_commun
-            .get(&niveau)
-            .copied()
-            .unwrap_or(20);
+        for _ in 0..loot.commun {
+            let seuil = self
+                .seuil_artefact_commun
+                .get(&niveau)
+                .copied()
+                .unwrap_or(20);
 
-        // Application du coefficient au seuil
-        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
-        let jet = rng.random_range(1..=20);
+            // Application du coefficient au seuil
+            let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
+            let jet = rng.random_range(1..=20);
 
-        if jet >= seuil_ajuste {
-            let objet = self
-                .tirer_objet(
-                    pool,
-                    account_id,
-                    "Artefact commun",
-                    &mut rng,
-                    is_admin,
-                    
-                )
-                .await?;
+            if jet >= seuil_ajuste {
+                let objet = self
+                    .tirer_objet(pool, account_id, "Artefact commun", &mut rng, is_admin)
+                    .await?;
 
-            let quantite = self
-                .quantite_objets
-                .get(&objet)
-                .copied()
-                .unwrap_or(1);
+                let quantite = self.quantite_objets.get(&objet).copied().unwrap_or(1);
 
-            *objets.entry(objet).or_insert(0) += quantite;
+                *objets.entry(objet).or_insert(0) += quantite;
+            }
         }
-    }
-          for _ in 0..loot.peu_commun {
-        let seuil = self
-            .seuil_artefact_peu_commun
-            .get(&niveau)
-            .copied()
-            .unwrap_or(20);
+        for _ in 0..loot.peu_commun {
+            let seuil = self
+                .seuil_artefact_peu_commun
+                .get(&niveau)
+                .copied()
+                .unwrap_or(20);
 
-        // Application du coefficient au seuil
-        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
-        let jet = rng.random_range(1..=20);
+            // Application du coefficient au seuil
+            let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
+            let jet = rng.random_range(1..=20);
 
-        if jet >= seuil_ajuste {
-            let objet = self
-                .tirer_objet(
-                    pool,
-                    account_id,
-                    "Artefact peu commun",
-                    &mut rng,
-                    is_admin,
-                    
-                )
-                .await?;
+            if jet >= seuil_ajuste {
+                let objet = self
+                    .tirer_objet(pool, account_id, "Artefact peu commun", &mut rng, is_admin)
+                    .await?;
 
-            let quantite = self
-                .quantite_objets
-                .get(&objet)
-                .copied()
-                .unwrap_or(1);
+                let quantite = self.quantite_objets.get(&objet).copied().unwrap_or(1);
 
-            *objets.entry(objet).or_insert(0) += quantite;
+                *objets.entry(objet).or_insert(0) += quantite;
+            }
         }
-          }
-          for _ in 0..loot.rare {
-        let seuil = self
-            .seuil_artefact_rare
-            .get(&niveau)
-            .copied()
-            .unwrap_or(20);
+        for _ in 0..loot.rare {
+            let seuil = self.seuil_artefact_rare.get(&niveau).copied().unwrap_or(20);
 
-        // Application du coefficient au seuil
-        let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
-        let jet = rng.random_range(1..=20);
+            // Application du coefficient au seuil
+            let seuil_ajuste = (seuil as f64 * (1.0 / self.coeff_loot).max(0.1)) as u32;
+            let jet = rng.random_range(1..=20);
 
-        if jet >= seuil_ajuste {
-            let objet = self
-                .tirer_objet(
-                    pool,
-                    account_id,
-                    "Artefact rare",
-                    &mut rng,
-                    is_admin,
-                    
-                )
-                .await?;
+            if jet >= seuil_ajuste {
+                let objet = self
+                    .tirer_objet(pool, account_id, "Artefact rare", &mut rng, is_admin)
+                    .await?;
 
-            let quantite = self
-                .quantite_objets
-                .get(&objet)
-                .copied()
-                .unwrap_or(1);
+                let quantite = self.quantite_objets.get(&objet).copied().unwrap_or(1);
 
-            *objets.entry(objet).or_insert(0) += quantite;
+                *objets.entry(objet).or_insert(0) += quantite;
+            }
         }
-          }
 
-    // ==========================================
-    // LOOT ADMIN
-    // ==========================================
+        // ==========================================
+        // LOOT ADMIN
+        // ==========================================
 
-    if is_admin {
-        for _ in 0..loot.admin {
-            let objet = self
-                .tirer_objet(
-                    pool,
-                    account_id,
-                    "Artefact admin",
-                    &mut rng,
-                    is_admin,
-                    
-                )
-                .await?;
+        if is_admin {
+            for _ in 0..loot.admin {
+                let objet = self
+                    .tirer_objet(pool, account_id, "Artefact admin", &mut rng, is_admin)
+                    .await?;
 
-            let quantite = self
-                .quantite_objets
-                .get(&objet)
-                .copied()
-                .unwrap_or(1);
+                let quantite = self.quantite_objets.get(&objet).copied().unwrap_or(1);
 
-            *objets.entry(objet).or_insert(0) += quantite;
+                *objets.entry(objet).or_insert(0) += quantite;
+            }
         }
-    }
-          if is_admin || is_militaire {
-        for _ in 0..loot.militaire {
-            let objet = self
-                .tirer_objet(
-                    pool,
-                    account_id,
-                    "Artefact militaire",
-                    &mut rng,
-                    is_admin,
-                    
-                )
-                .await?;
+        if is_admin || is_militaire {
+            for _ in 0..loot.militaire {
+                let objet = self
+                    .tirer_objet(pool, account_id, "Artefact militaire", &mut rng, is_admin)
+                    .await?;
 
-            let quantite = self
-                .quantite_objets
-                .get(&objet)
-                .copied()
-                .unwrap_or(1);
+                let quantite = self.quantite_objets.get(&objet).copied().unwrap_or(1);
 
-            *objets.entry(objet).or_insert(0) += quantite;
+                *objets.entry(objet).or_insert(0) += quantite;
+            }
         }
-          }
 
-    Ok(objets)
-                }  
-            
-        
-            
+        Ok(objets)
+    }
 
-        
+    pub fn tirer_pondere(table: &HashMap<String, f64>, rng: &mut impl Rng) -> String {
+        let total: f64 = table.values().sum();
 
-            
-    
+        if total <= 0.0 {
+            panic!("Table de loot vide");
+        }
 
-            
-        pub fn tirer_pondere(
-    table: &HashMap<String, f64>,
-    rng: &mut impl Rng,
-) -> String {
-    let total: f64 = table.values().sum();
+        let tirage = rng.random_range(0.0..total);
 
-    if total <= 0.0 {
-        panic!("Table de loot vide");
-    }
+        let mut cumul = 0.0;
 
-    let tirage = rng.random_range(0.0..total);
+        for (objet, poids) in table {
+            cumul += poids;
 
-    let mut cumul = 0.0;
-
-    for (objet, poids) in table {
-        cumul += poids;
-
-        if tirage < cumul {
-            return objet.clone();
+            if tirage < cumul {
+                return objet.clone();
+            }
         }
+
+        unreachable!("Le tirage n'a trouvé aucun résultat")
     }
 
-    unreachable!("Le tirage n'a trouvé aucun résultat")
-}
-
-    
     pub async fn tirer_objet(
-    &mut self,
-    pool: &SqlitePool,
-    account_id: i64,
-    categorie: &str,
-    rng: &mut impl Rng,
-    is_admin: bool,
-) -> Result<String, sqlx::Error> {
+        &mut self,
+        pool: &SqlitePool,
+        account_id: i64,
+        categorie: &str,
+        rng: &mut impl Rng,
+        is_admin: bool,
+    ) -> Result<String, sqlx::Error> {
+        // Catégorie principale du tirage.
+        // Exemple : "Artefact rare"
+        let categorie_racine = categorie.to_string();
 
-    // Catégorie principale du tirage.
-    // Exemple : "Artefact rare"
-    let categorie_racine = categorie.to_string();
+        // Catégorie actuellement parcourue.
+        // Elle change lorsqu'on descend dans les sous-catégories.
+        let mut categorie_actuelle = categorie.to_string();
 
-    // Catégorie actuellement parcourue.
-    // Elle change lorsqu'on descend dans les sous-catégories.
-    let mut categorie_actuelle = categorie.to_string();
+        loop {
+            // ==========================================
+            // RÉCUPÉRATION DE LA TABLE ACTUELLE
+            // ==========================================
 
-    loop {
-        // ==========================================
-        // RÉCUPÉRATION DE LA TABLE ACTUELLE
-        // ==========================================
+            let table_originale = self
+                .sous_loot
+                .get(&categorie_actuelle)
+                .cloned()
+                .unwrap_or_else(|| {
+                    panic!("Catégorie de loot inconnue : {:?}", categorie_actuelle);
+                });
 
-        let table_originale = self
-            .sous_loot
-            .get(&categorie_actuelle)
-            .cloned()
-            .unwrap_or_else(|| {
-                panic!(
-                    "Catégorie de loot inconnue : {:?}",
-                    categorie_actuelle
-                );
-            });
+            let total: f64 = table_originale.values().sum();
 
-        let total: f64 = table_originale.values().sum();
+            if total <= 0.0 {
+                panic!("Table de loot vide");
+            }
 
-        if total <= 0.0 {
-            panic!("Table de loot vide");
-        }
+            // ==========================================
+            // CALCUL DES POIDS AVEC PITY
+            // ==========================================
 
-        // ==========================================
-        // CALCUL DES POIDS AVEC PITY
-        // ==========================================
+            let mut table_ajustee = HashMap::new();
 
-        let mut table_ajustee = HashMap::new();
+            for (nom, poids) in &table_originale {
+                let probabilite = poids / total;
 
-        for (nom, poids) in &table_originale {
+                // Est-ce que cette entrée est une
+                // sous-catégorie ?
+                let est_sous_categorie = self.sous_loot.contains_key(nom);
 
-            let probabilite = poids / total;
+                let echecs: i64;
 
-            // Est-ce que cette entrée est une
-            // sous-catégorie ?
-            let est_sous_categorie =
-                self.sous_loot.contains_key(nom);
+                if est_sous_categorie {
+                    // ==================================
+                    // PITY SOUS-CATÉGORIE
+                    // ==================================
 
-            let echecs: i64;
-
-            if est_sous_categorie {
-
-                // ==================================
-                // PITY SOUS-CATÉGORIE
-                // ==================================
-
-                echecs = sqlx::query_scalar(
-                    r#"
+                    echecs = sqlx::query_scalar(
+                        r#"
                     SELECT nombre
                     FROM echecs_sous_categories
                     WHERE account_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:982:
                       AND categorie = ?
                       AND sous_categorie = ?
                     "#,
-                )
-                .bind(account_id)
-                .bind(&categorie_actuelle)
-                .bind(nom)
-                .fetch_optional(pool)
-                .await?
-                .unwrap_or(0);
+                    )
+                    .bind(account_id)
+                    .bind(&categorie_actuelle)
+                    .bind(nom)
+                    .fetch_optional(pool)
+                    .await?
+                    .unwrap_or(0);
+                } else {
+                    // ==================================
+                    // PITY OBJET
+                    // ==================================
 
-            } else {
-
-                // ==================================
-                // PITY OBJET
-                // ==================================
-
-                let objet_id: Option<i64> = sqlx::query_scalar(
-                    r#"
+                    let objet_id: Option<i64> = sqlx::query_scalar(
+                        r#"
                     SELECT objet_id
                     FROM objets_dispo
                     WHERE nom = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1004:
                     "#,
-                )
-                .bind(nom)
-                .fetch_optional(pool)
-                .await?;
+                    )
+                    .bind(nom)
+                    .fetch_optional(pool)
+                    .await?;
 
-                // Si l'objet n'existe pas encore dans
-                // objets_dispo, il n'a simplement pas
-                // encore de pity.
-                echecs = match objet_id {
-                    Some(objet_id) => {
-                        sqlx::query_scalar(
+                    // Si l'objet n'existe pas encore dans
+                    // objets_dispo, il n'a simplement pas
+                    // encore de pity.
+                    echecs = match objet_id {
+                        Some(objet_id) => sqlx::query_scalar(
                             r#"
                             SELECT nombre
                             FROM echecs_objets
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1028:
                         .bind(objet_id)
                         .fetch_optional(pool)
                         .await?
-                        .unwrap_or(0)
-                    }
+                        .unwrap_or(0),
 
-                    None => 0,
-                };
-            }
+                        None => 0,
+                    };
+                }
 
-            // ==================================
-            // APPLICATION DU PITY
-            // ==================================
+                // ==================================
+                // APPLICATION DU PITY
+                // ==================================
 
-            /*
-             * Le pity s'applique uniquement aux
-             * résultats ayant une probabilité
-             * originale strictement inférieure à 3 %.
-             *
-             * Chaque échec ajoute +7,5 % du poids
-             * original.
-             *
-             * Le coefficient de loot est également
-             * appliqué.
-             */
+                /*
+                 * Le pity s'applique uniquement aux
+                 * résultats ayant une probabilité
+                 * originale strictement inférieure à 3 %.
+                 *
+                 * Chaque échec ajoute +7,5 % du poids
+                 * original.
+                 *
+                 * Le coefficient de loot est également
+                 * appliqué.
+                 */
 
-            let poids_ajuste = if probabilite < 0.03 {
-                *poids
-                    * self.coeff_loot
-                    * (1.0 + 0.075 * echecs as f64)
-            } else {
-                *poids * self.coeff_loot
-            };
+                let poids_ajuste = if probabilite < 0.03 {
+                    *poids * self.coeff_loot * (1.0 + 0.075 * echecs as f64)
+                } else {
+                    *poids * self.coeff_loot
+                };
 
-            table_ajustee.insert(
-                nom.clone(),
-                poids_ajuste,
-            );
-        }
+                table_ajustee.insert(nom.clone(), poids_ajuste);
+            }
 
-        // ==========================================
-        // TIRAGE
-        // ==========================================
+            // ==========================================
+            // TIRAGE
+            // ==========================================
 
-        let resultat = Self::tirer_pondere(
-            &table_ajustee,
-            rng,
-        );
+            let resultat = Self::tirer_pondere(&table_ajustee, rng);
 
-        // ==========================================
-        // LE RÉSULTAT EST-IL UNE SOUS-CATÉGORIE ?
-        // ==========================================
+            // ==========================================
+            // LE RÉSULTAT EST-IL UNE SOUS-CATÉGORIE ?
+            // ==========================================
 
-        let resultat_est_sous_categorie =
-            self.sous_loot.contains_key(&resultat);
+            let resultat_est_sous_categorie = self.sous_loot.contains_key(&resultat);
 
-        // ==========================================
-        // MISE À JOUR DU PITY
-        // ==========================================
+            // ==========================================
+            // MISE À JOUR DU PITY
+            // ==========================================
 
-        for (nom, poids) in &table_originale {
+            for (nom, poids) in &table_originale {
+                let probabilite = poids / total;
 
-            let probabilite = poids / total;
+                // Pas de pity pour les probabilités >= 3 %.
+                if probabilite >= 0.03 {
+                    continue;
+                }
 
-            // Pas de pity pour les probabilités >= 3 %.
-            if probabilite >= 0.03 {
-                continue;
-            }
+                // ======================================
+                // SOUS-CATÉGORIE
+                // ======================================
 
-            // ======================================
-            // SOUS-CATÉGORIE
-            // ======================================
+                if self.sous_loot.contains_key(nom) {
+                    if nom == &resultat {
+                        // ------------------------------
+                        // SOUS-CATÉGORIE OBTENUE
+                        // → RESET
+                        // ------------------------------
 
-            if self.sous_loot.contains_key(nom) {
-
-                if nom == &resultat {
-
-                    // ------------------------------
-                    // SOUS-CATÉGORIE OBTENUE
-                    // → RESET
-                    // ------------------------------
-
-                    sqlx::query(
-                        r#"
+                        sqlx::query(
+                            r#"
                         INSERT INTO echecs_sous_categories (
                             account_id,
                             categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1125:
                         DO UPDATE SET
                             nombre = 0
                         "#,
-                    )
-                    .bind(account_id)
-                    .bind(&categorie_actuelle)
-                    .bind(nom)
-                    .execute(pool)
-                    .await?;
+                        )
+                        .bind(account_id)
+                        .bind(&categorie_actuelle)
+                        .bind(nom)
+                        .execute(pool)
+                        .await?;
+                    } else {
+                        // ------------------------------
+                        // SOUS-CATÉGORIE NON OBTENUE
+                        // → +1 ÉCHEC
+                        // ------------------------------
 
-                } else {
-
-                    // ------------------------------
-                    // SOUS-CATÉGORIE NON OBTENUE
-                    // → +1 ÉCHEC
-                    // ------------------------------
-
-                    sqlx::query(
-                        r#"
+                        sqlx::query(
+                            r#"
                         INSERT INTO echecs_sous_categories (
                             account_id,
                             categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1157:
                         DO UPDATE SET
                             nombre = nombre + 1
                         "#,
-                    )
-                    .bind(account_id)
-                    .bind(&categorie_actuelle)
-                    .bind(nom)
-                    .execute(pool)
-                    .await?;
-                }
+                        )
+                        .bind(account_id)
+                        .bind(&categorie_actuelle)
+                        .bind(nom)
+                        .execute(pool)
+                        .await?;
+                    }
 
-            // ======================================
-            // OBJET FINAL
-            // ======================================
-
-            } else {
-
-                let objet_id: Option<i64> = sqlx::query_scalar(
-                    r#"
+                // ======================================
+                // OBJET FINAL
+                // ======================================
+                } else {
+                    let objet_id: Option<i64> = sqlx::query_scalar(
+                        r#"
                     SELECT objet_id
                     FROM objets_dispo
                     WHERE nom = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1179:
                     "#,
-                )
-                .bind(nom)
-                .fetch_optional(pool)
-                .await?;
+                    )
+                    .bind(nom)
+                    .fetch_optional(pool)
+                    .await?;
 
-                // Si l'objet n'existe pas dans
-                // objets_dispo, on ne peut pas
-                // enregistrer son pity.
-                let Some(objet_id) = objet_id else {
-                    continue;
-                };
+                    // Si l'objet n'existe pas dans
+                    // objets_dispo, on ne peut pas
+                    // enregistrer son pity.
+                    let Some(objet_id) = objet_id else {
+                        continue;
+                    };
 
-                if nom == &resultat {
+                    if nom == &resultat {
+                        // ------------------------------
+                        // OBJET OBTENU
+                        // → RESET
+                        // ------------------------------
 
-                    // ------------------------------
-                    // OBJET OBTENU
-                    // → RESET
-                    // ------------------------------
-
-                    sqlx::query(
-                        r#"
+                        sqlx::query(
+                            r#"
                         INSERT INTO echecs_objets (
                             account_id,
                             categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1216:
                         DO UPDATE SET
                             nombre = 0
                         "#,
-                    )
-                    .bind(account_id)
-                    .bind(&categorie_racine)
-                    .bind(&categorie_actuelle)
-                    .bind(objet_id)
-                    .execute(pool)
-                    .await?;
+                        )
+                        .bind(account_id)
+                        .bind(&categorie_racine)
+                        .bind(&categorie_actuelle)
+                        .bind(objet_id)
+                        .execute(pool)
+                        .await?;
+                    } else {
+                        // ------------------------------
+                        // OBJET NON OBTENU
+                        // → +1 ÉCHEC
+                        // ------------------------------
 
-                } else {
-
-                    // ------------------------------
-                    // OBJET NON OBTENU
-                    // → +1 ÉCHEC
-                    // ------------------------------
-
-                    sqlx::query(
-                        r#"
+                        sqlx::query(
+                            r#"
                         INSERT INTO echecs_objets (
                             account_id,
                             categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1251:
                         DO UPDATE SET
                             nombre = nombre + 1
                         "#,
-                    )
-                    .bind(account_id)
-                    .bind(&categorie_racine)
-                    .bind(&categorie_actuelle)
-                    .bind(objet_id)
-                    .execute(pool)
-                    .await?;
+                        )
+                        .bind(account_id)
+                        .bind(&categorie_racine)
+                        .bind(&categorie_actuelle)
+                        .bind(objet_id)
+                        .execute(pool)
+                        .await?;
+                    }
                 }
             }
-        }
 
-        // ==========================================
-        // LIVRE ENCHANTÉ
-        // ==========================================
+            // ==========================================
+            // LIVRE ENCHANTÉ
+            // ==========================================
 
-        if resultat == "livre enchant" {
-            return self
-                .tirer_livre(
-                    pool,
-                    account_id,
-                    rng,
-                    is_admin,
-                )
-                .await;
-        }
+            if resultat == "livre enchant" {
+                return self.tirer_livre(pool, account_id, rng, is_admin).await;
+            }
 
-        // ==========================================
-        // DESCENTE DANS UNE SOUS-CATÉGORIE
-        // ==========================================
+            // ==========================================
+            // DESCENTE DANS UNE SOUS-CATÉGORIE
+            // ==========================================
 
-        if resultat_est_sous_categorie {
-            categorie_actuelle = resultat;
-            continue;
-        }
+            if resultat_est_sous_categorie {
+                categorie_actuelle = resultat;
+                continue;
+            }
 
-        // ==========================================
-        // OBJET FINAL
-        // ==========================================
+            // ==========================================
+            // OBJET FINAL
+            // ==========================================
 
-        return Ok(resultat);
+            return Ok(resultat);
+        }
     }
-}
     pub async fn tirer_livre(
-    &mut self,
-    pool: &SqlitePool,
-    account_id: i64,
-    rng: &mut impl Rng,
-    is_admin: bool,
-) -> Result<String, sqlx::Error> {
-    let categorie = if is_admin {
-        "livre enchant admin"
-    } else {
-        "livre enchant normal"
-    };
+        &mut self,
+        pool: &SqlitePool,
+        account_id: i64,
+        rng: &mut impl Rng,
+        is_admin: bool,
+    ) -> Result<String, sqlx::Error> {
+        let categorie = if is_admin {
+            "livre enchant admin"
+        } else {
+            "livre enchant normal"
+        };
 
-    let table_originale = if is_admin {
-        self.sous_loot_livre_admin.clone()
-    } else {
-        self.sous_loot_livre_normal.clone()
-    };
+        let table_originale = if is_admin {
+            self.sous_loot_livre_admin.clone()
+        } else {
+            self.sous_loot_livre_normal.clone()
+        };
 
-    let total: f64 = table_originale.values().sum();
+        let total: f64 = table_originale.values().sum();
 
-    if total <= 0.0 {
-        panic!("Table de loot des livres vide");
-    }
+        if total <= 0.0 {
+            panic!("Table de loot des livres vide");
+        }
 
-    // ==========================================
-    // CALCUL DES POIDS AVEC PITY
-    // ==========================================
+        // ==========================================
+        // CALCUL DES POIDS AVEC PITY
+        // ==========================================
 
-    let mut table_ajustee = HashMap::new();
+        let mut table_ajustee = HashMap::new();
 
-    for (objet, poids) in &table_originale {
-        let probabilite = poids / total;
+        for (objet, poids) in &table_originale {
+            let probabilite = poids / total;
 
-        let objet_id: Option<i64> = sqlx::query_scalar(
-            r#"
+            let objet_id: Option<i64> = sqlx::query_scalar(
+                r#"
             SELECT objet_id
             FROM objets_dispo
             WHERE nom = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1335:
             "#,
-        )
-        .bind(objet)
-        .fetch_optional(pool)
-        .await?;
+            )
+            .bind(objet)
+            .fetch_optional(pool)
+            .await?;
 
-        let echecs = match objet_id {
-            Some(objet_id) => {
-                sqlx::query_scalar(
+            let echecs = match objet_id {
+                Some(objet_id) => sqlx::query_scalar(
                     r#"
                     SELECT nombre
                     FROM echecs_objets
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1356:
                 .bind(objet_id)
                 .fetch_optional(pool)
                 .await?
-                .unwrap_or(0)
-            }
+                .unwrap_or(0),
 
-            None => {
-                error!(
-                    "Livre absent de objets_dispo : {:?}",
-                    objet
-                );
+                None => {
+                    error!("Livre absent de objets_dispo : {:?}", objet);
 
-                0
-            }
-        };
+                    0
+                }
+            };
 
-        let poids_ajuste = if probabilite < 0.03 {
-            *poids
-                * self.coeff_loot
-                * (1.0 + 0.075 * echecs as f64)
-        } else {
-            *poids * self.coeff_loot
-        };
+            let poids_ajuste = if probabilite < 0.03 {
+                *poids * self.coeff_loot * (1.0 + 0.075 * echecs as f64)
+            } else {
+                *poids * self.coeff_loot
+            };
 
-        table_ajustee.insert(
-            objet.clone(),
-            poids_ajuste,
-        );
-    }
+            table_ajustee.insert(objet.clone(), poids_ajuste);
+        }
 
-    // ==========================================
-    // TIRAGE
-    // ==========================================
+        // ==========================================
+        // TIRAGE
+        // ==========================================
 
-    let resultat = Self::tirer_pondere(
-        &table_ajustee,
-        rng,
-    );
+        let resultat = Self::tirer_pondere(&table_ajustee, rng);
 
-    // ==========================================
-    // MISE À JOUR DES ÉCHECS
-    // ==========================================
+        // ==========================================
+        // MISE À JOUR DES ÉCHECS
+        // ==========================================
 
-    for (objet, poids) in &table_originale {
-        let probabilite = poids / total;
+        for (objet, poids) in &table_originale {
+            let probabilite = poids / total;
 
-        if probabilite >= 0.03 {
-            continue;
-        }
+            if probabilite >= 0.03 {
+                continue;
+            }
 
-        let objet_id: Option<i64> = sqlx::query_scalar(
-            r#"
+            let objet_id: Option<i64> = sqlx::query_scalar(
+                r#"
             SELECT objet_id
             FROM objets_dispo
             WHERE nom = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1411:
             "#,
-        )
-        .bind(objet)
-        .fetch_optional(pool)
-        .await?;
+            )
+            .bind(objet)
+            .fetch_optional(pool)
+            .await?;
 
-        let Some(objet_id) = objet_id else {
-            error!(
-                "Impossible de mettre à jour la pity : \
+            let Some(objet_id) = objet_id else {
+                error!(
+                    "Impossible de mettre à jour la pity : \
                  livre absent de objets_dispo : {:?}",
-                objet
-            );
-            continue;
-        };
+                    objet
+                );
+                continue;
+            };
 
-        if objet == &resultat {
-            // ==================================
-            // OBTENU → RESET
-            // ==================================
+            if objet == &resultat {
+                // ==================================
+                // OBTENU → RESET
+                // ==================================
 
-            sqlx::query(
-                r#"
+                sqlx::query(
+                    r#"
                 INSERT INTO echecs_objets (
                     account_id,
                     categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1448:
                 DO UPDATE SET
                     nombre = 0
                 "#,
-            )
-            .bind(account_id)
-            .bind(categorie)
-            .bind(categorie)
-            .bind(objet_id)
-            .execute(pool)
-            .await?;
+                )
+                .bind(account_id)
+                .bind(categorie)
+                .bind(categorie)
+                .bind(objet_id)
+                .execute(pool)
+                .await?;
+            } else {
+                // ==================================
+                // PAS OBTENU → +1
+                // ==================================
 
-        } else {
-            // ==================================
-            // PAS OBTENU → +1
-            // ==================================
-
-            sqlx::query(
-                r#"
+                sqlx::query(
+                    r#"
                 INSERT INTO echecs_objets (
                     account_id,
                     categorie,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/tresor.rs:1481:
                 DO UPDATE SET
                     nombre = nombre + 1
                 "#,
-            )
-            .bind(account_id)
-            .bind(categorie)
-            .bind(categorie)
-            .bind(objet_id)
-            .execute(pool)
-            .await?;
+                )
+                .bind(account_id)
+                .bind(categorie)
+                .bind(categorie)
+                .bind(objet_id)
+                .execute(pool)
+                .await?;
+            }
         }
-    }
 
-    Ok(resultat)
+        Ok(resultat)
+    }
 }
-}
-   
-
-
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/wallet_manager.rs:7:
 
 impl WalletManager {
     pub fn new(pool: SqlitePool, account_id: i64) -> Self {
-        Self {
-            pool,
-            account_id,
-        }
+        Self { pool, account_id }
     }
 
     pub fn account_id(&self) -> i64 {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/wallet_manager.rs:52:
         .await?;
 
         if result.rows_affected() == 0 {
-            return Err(sqlx::Error::Protocol(
-                "Portefeuille inexistant".into(),
-            ));
+            return Err(sqlx::Error::Protocol("Portefeuille inexistant".into()));
         }
 
         Ok(())
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/wallet_manager.rs:89:
 
         Ok(())
     }
-        /// Débite le portefeuille dans une transaction SQLite existante.
+    /// Débite le portefeuille dans une transaction SQLite existante.
     pub async fn debiter_tx(
         tx: &mut sqlx::Transaction<'_, sqlx::Sqlite>,
         account_id: i64,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/gameplay/wallet_manager.rs:149:
         .await?;
 
         if result.rows_affected() == 0 {
-            return Err(sqlx::Error::Protocol(
-                "Portefeuille inexistant".into(),
-            ));
+            return Err(sqlx::Error::Protocol("Portefeuille inexistant".into()));
         }
 
         Ok(())
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/lib.rs:1:
+pub mod auth;
 pub mod database;
-pub mod network;
-pub mod utils;
 pub mod gameplay;
+pub mod network;
 pub mod security;
-pub mod auth;
+pub mod utils;
 pub mod world;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:1:
 use tokio::{
     io::AsyncWriteExt,
     net::TcpStream,
-    time::{interval, Duration},
     sync::broadcast,
+    time::{Duration, interval},
 };
 
 use sqlx::SqlitePool;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:9:
 use uuid::Uuid;
 
-use log::{
-    debug,
-    error,
-    info,
-};
+use crate::network::handler::{HandlerResult, PacketHandler};
+use crate::network::packet::{BanInfo, BanType, Packet, PacketType, receive_packet, send_packet};
+use crate::world::world::{Position, World};
+use log::{debug, error, info};
 use rand::RngExt;
-use crate::network::handler::{PacketHandler,HandlerResult};
-use crate::world::world::{World,Position};
-use crate::network::packet::{
-    receive_packet,
-    send_packet,
-    BanInfo,
-    BanType,
-    Packet,
-    PacketType,
-};
 
-
 pub struct Client {
-
     stream: TcpStream,
 
     pool: SqlitePool,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:42:
     world: World,
 }
 
-
 impl Client {
-
     // ============================================================
     // CONSTRUCTEUR
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:51:
 
-    pub fn new(
-        stream: TcpStream,
-        pool: SqlitePool,
-        world: World,
-    ) -> Self {
-
+    pub fn new(stream: TcpStream, pool: SqlitePool, world: World) -> Self {
         Self {
             stream,
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:71:
         }
     }
 
-
     // ============================================================
     // BOUCLE PRINCIPALE
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:78:
 
     pub async fn run(&mut self) {
-
         let peer = self
             .stream
             .peer_addr()
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:84:
             .map(|addr| addr.to_string())
             .unwrap_or_else(|_| "adresse inconnue".to_string());
 
+        info!("Client connecté : {} ", peer,);
+        let mut world_rx = self.world.subscribe();
+        let session_packet = Packet::new(PacketType::Session, self.session_id.as_bytes().to_vec());
 
-        info!(
-            "Client connecté : {} ",
-            peer,
-            
-        );
-        let mut world_rx =
-         self.world.subscribe();
-         let session_packet = Packet::new(
-    PacketType::Session,
-    self.session_id.as_bytes().to_vec(),
-);
+        if let Err(e) = send_packet(&mut self.stream, &session_packet).await {
+            error!("Impossible d'envoyer le paquet SESSION: {}", e);
+            self.world.remove_player(self.session_id).await;
 
-if let Err(e) = send_packet(
-    &mut self.stream,
-    &session_packet,
-).await {
-    error!(
-        "Impossible d'envoyer le paquet SESSION: {}",
-        
-        e
-    );
-    self.world
-    .remove_player(self.session_id)
-    .await;
+            self.world.broadcast_player_remove(self.session_id);
+            self.disconnect().await;
+            return;
+        }
 
-self.world
-    .broadcast_player_remove(self.session_id);
-    self.disconnect().await;
-    return;
-}
+        info!("Paquet SESSION envoyé");
+        let spawn_position = {
+            let mut rng = rand::rng();
 
-info!(
-    "Paquet SESSION envoyé"
-);
-let spawn_position = {
-    let mut rng = rand::rng();
+            Position::new(rng.random_range(0..100), rng.random_range(0..100), 0)
+        };
+        let snapshot = self.world.snapshot().await;
+        info!(" Synchronisation initiale : {} joueur(s)", snapshot.len());
+        for (player_id, position) in snapshot {
+            let packet = World::player_state_packet(player_id, position);
 
-    Position::new(
-        rng.random_range(0..100),
-        rng.random_range(0..100),
-        0,
-    )
-};
-let snapshot = self.world.snapshot().await;
-info!(
-    " Synchronisation initiale : {} joueur(s)",
-    
-    snapshot.len()
-);
-for (player_id, position) in snapshot {
-    let packet = World::player_state_packet(
-        player_id,
-        position,
-    );
-
-    if let Err(e) = send_packet(
-        &mut self.stream,
-        &packet,
-    ).await {
-        error!(
-            "[{}] Erreur lors de l'envoi du snapshot \
+            if let Err(e) = send_packet(&mut self.stream, &packet).await {
+                error!(
+                    "[{}] Erreur lors de l'envoi du snapshot \
              du joueur : {}",
-            
-            player_id,
-            e
-        );
+                    player_id, e
+                );
 
-        return;
-    }
-}
+                return;
+            }
+        }
 
-self.world.set_position(
-    self.session_id,
-    spawn_position,
-).await;
+        self.world
+            .set_position(self.session_id, spawn_position)
+            .await;
 
-self.world.broadcast_player_state(
-    self.session_id,
-    spawn_position,
-);
+        self.world
+            .broadcast_player_state(self.session_id, spawn_position);
 
-
-         
-
-
-
-
-
-    
-
-
         // --------------------------------------------------------
         // Timer de vérification du ban
         // --------------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:182:
 
-        let mut ban_checker =
-            interval(Duration::from_secs(1));
+        let mut ban_checker = interval(Duration::from_secs(1));
 
-
         // interval() déclenche immédiatement son premier tick.
         //
         // On le consomme donc ici pour que la première véritable
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:190:
         // vérification ait lieu après 1 seconde.
         ban_checker.tick().await;
 
-
         // ========================================================
         // BOUCLE
         // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:197:
 
         loop {
-
             tokio::select! {
 
-                // =================================================
-                // RÉCEPTION DES PAQUETS
-                // =================================================
+                            // =================================================
+                            // RÉCEPTION DES PAQUETS
+                            // =================================================
 
-                packet = receive_packet(
-                    &mut self.stream
-                ) => {
+                            packet = receive_packet(
+                                &mut self.stream
+                            ) => {
 
-                    match packet {
+                                match packet {
 
-                        Ok(packet) => {
+                                    Ok(packet) => {
 
-                            debug!(
-                                "[{}] Paquet reçu : {:?}",
-                                self.session_id,
-                                packet.packet_type
-                            );
+                                        debug!(
+                                            "[{}] Paquet reçu : {:?}",
+                                            self.session_id,
+                                            packet.packet_type
+                                        );
 
 
-                            debug!(
-                                "[{}] Payload : {}",
-                                self.session_id,
-                                String::from_utf8_lossy(
-                                    &packet.payload
-                                )
-                            );
+                                        debug!(
+                                            "[{}] Payload : {}",
+                                            self.session_id,
+                                            String::from_utf8_lossy(
+                                                &packet.payload
+                                            )
+                                        );
 
 
-                            // -----------------------------------------
-                            // Traitement du paquet
-                            // -----------------------------------------
-                            match PacketHandler::handle(
-    self,
-    packet,
-    self.pool.clone(),
-    self.world.clone(),
-).await {
+                                        // -----------------------------------------
+                                        // Traitement du paquet
+                                        // -----------------------------------------
+                                        match PacketHandler::handle(
+                self,
+                packet,
+                self.pool.clone(),
+                self.world.clone(),
+            ).await {
 
-    HandlerResult::Response(response) => {
+                HandlerResult::Response(response) => {
 
-        if let Err(e) =
-            send_packet(
-                &mut self.stream,
-                &response
-            ).await
-        {
-            error!(
-                "Erreur d'envoi  : {}",
-                
-                e
-            );
+                    if let Err(e) =
+                        send_packet(
+                            &mut self.stream,
+                            &response
+                        ).await
+                    {
+                        error!(
+                            "Erreur d'envoi  : {}",
 
-            break;
-        }
-    }
+                            e
+                        );
 
-    HandlerResult::Disconnect => {
+                        break;
+                    }
+                }
 
-        self.disconnect().await;
+                HandlerResult::Disconnect => {
 
-        break;
-    }
+                    self.disconnect().await;
 
-    HandlerResult::Nothing => {
-        // Aucun paquet de réponse.
-    }
-}
-                            
-                        }
+                    break;
+                }
 
+                HandlerResult::Nothing => {
+                    // Aucun paquet de réponse.
+                }
+            }
 
-                        // ---------------------------------------------
-                        // Erreur / déconnexion du client
-                        // ---------------------------------------------
+                                    }
 
-                        Err(e) => {
-                            self.world.remove_player(self.session_id).await;
 
-self.world
-    .broadcast_player_remove(self.session_id);
-                            debug!(
-                                "Déconnexion du client [{}] : {}",
-                                self.session_id,
-                                e
-                            );
+                                    // ---------------------------------------------
+                                    // Erreur / déconnexion du client
+                                    // ---------------------------------------------
 
-                            break;
-                        }
-                    }
-                }
+                                    Err(e) => {
+                                        self.world.remove_player(self.session_id).await;
 
+            self.world
+                .broadcast_player_remove(self.session_id);
+                                        debug!(
+                                            "Déconnexion du client [{}] : {}",
+                                            self.session_id,
+                                            e
+                                        );
 
-                // =================================================
-                // VÉRIFICATION DU BAN
-                // =================================================
+                                        break;
+                                    }
+                                }
+                            }
 
-                _ = ban_checker.tick() => {
 
-                    // ---------------------------------------------
-                    // Aucun utilisateur authentifié
-                    // ---------------------------------------------
-                    //
-                    // Il n'y a aucun intérêt à vérifier les bans
-                    // si le client n'est pas encore connecté.
-                    //
-                    // ---------------------------------------------
+                            // =================================================
+                            // VÉRIFICATION DU BAN
+                            // =================================================
 
-                    if self.user_id.is_none() {
-                        continue;
-                    }
+                            _ = ban_checker.tick() => {
 
+                                // ---------------------------------------------
+                                // Aucun utilisateur authentifié
+                                // ---------------------------------------------
+                                //
+                                // Il n'y a aucun intérêt à vérifier les bans
+                                // si le client n'est pas encore connecté.
+                                //
+                                // ---------------------------------------------
 
-                    // ---------------------------------------------
-                    // Recherche d'un ban actif
-                    // ---------------------------------------------
+                                if self.user_id.is_none() {
+                                    continue;
+                                }
 
-                    match self.get_ban_info().await {
 
-                        Ok(Some(ban)) => {
+                                // ---------------------------------------------
+                                // Recherche d'un ban actif
+                                // ---------------------------------------------
 
-                            info!(
-                                "Ban détecté [{}] | Type : {:?} | Raison : {}",
-                                self.session_id,
-                                ban.ban_type,
-                                ban.reason
-                            );
+                                match self.get_ban_info().await {
 
+                                    Ok(Some(ban)) => {
 
-                            // -----------------------------------------
-                            // Création du paquet BAN
-                            // -----------------------------------------
+                                        info!(
+                                            "Ban détecté [{}] | Type : {:?} | Raison : {}",
+                                            self.session_id,
+                                            ban.ban_type,
+                                            ban.reason
+                                        );
 
-                            let payload =
-                                Self::encode_ban_payload(
-                                    &ban
-                                );
 
+                                        // -----------------------------------------
+                                        // Création du paquet BAN
+                                        // -----------------------------------------
 
-                            let packet =
-                                Packet::new(
-                                    PacketType::BAN,
-                                    payload
-                                );
+                                        let payload =
+                                            Self::encode_ban_payload(
+                                                &ban
+                                            );
 
 
-                            // -----------------------------------------
-                            // Envoi du BAN
-                            // -----------------------------------------
+                                        let packet =
+                                            Packet::new(
+                                                PacketType::BAN,
+                                                payload
+                                            );
 
-                            match send_packet(
-                                &mut self.stream,
-                                &packet
-                            ).await {
 
-                                Ok(()) => {
+                                        // -----------------------------------------
+                                        // Envoi du BAN
+                                        // -----------------------------------------
 
-                                    info!(
-                                        "Paquet BAN envoyé [{}]",
-                                        self.session_id
-                                    );
-                                }
+                                        match send_packet(
+                                            &mut self.stream,
+                                            &packet
+                                        ).await {
 
+                                            Ok(()) => {
 
-                                Err(e) => {
+                                                info!(
+                                                    "Paquet BAN envoyé [{}]",
+                                                    self.session_id
+                                                );
+                                            }
 
-                                    error!(
-                                        "Impossible d'envoyer le BAN [{}] : {}",
-                                        self.session_id,
-                                        e
-                                    );
-                                }
-                            }
 
+                                            Err(e) => {
 
-                            // -----------------------------------------
-                            // Déconnexion
-                            // -----------------------------------------
-                            self.world
-    .remove_player(self.session_id)
-    .await;
+                                                error!(
+                                                    "Impossible d'envoyer le BAN [{}] : {}",
+                                                    self.session_id,
+                                                    e
+                                                );
+                                            }
+                                        }
 
-self.world
-    .broadcast_player_remove(self.session_id);
 
-                            self.disconnect().await;
+                                        // -----------------------------------------
+                                        // Déconnexion
+                                        // -----------------------------------------
+                                        self.world
+                .remove_player(self.session_id)
+                .await;
 
-                            break;
-                        }
+            self.world
+                .broadcast_player_remove(self.session_id);
 
+                                        self.disconnect().await;
 
-                        // ---------------------------------------------
-                        // Aucun ban
-                        // ---------------------------------------------
+                                        break;
+                                    }
 
-                        Ok(None) => {
 
-                            // Rien à faire.
-                        }
+                                    // ---------------------------------------------
+                                    // Aucun ban
+                                    // ---------------------------------------------
 
+                                    Ok(None) => {
 
-                        // ---------------------------------------------
-                        // Erreur SQL
-                        // ---------------------------------------------
+                                        // Rien à faire.
+                                    }
 
-                        Err(e) => {
 
+                                    // ---------------------------------------------
+                                    // Erreur SQL
+                                    // ---------------------------------------------
+
+                                    Err(e) => {
+
+                                        error!(
+                                            "Erreur lors de la vérification du ban : {}",
+
+                                            e
+                                        );
+
+                                        break;
+                                    }
+                                }
+                            }
+                            packet = world_rx.recv() => {
+
+                match packet {
+
+                    Ok(packet) => {
+
+                        if let Err(e) =
+                            send_packet(
+                                &mut self.stream,
+                                &packet
+                            ).await
+                        {
+
                             error!(
-                                "Erreur lors de la vérification du ban : {}",
-                                
+                                "Erreur d'envoi du paquet monde : {}",
+
                                 e
                             );
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:414:
                             break;
                         }
                     }
-                }
-                packet = world_rx.recv() => {
 
-    match packet {
+                    Err(
+                        broadcast::error::RecvError::Lagged(
+                            count
+                        )
+                    ) => {
 
-        Ok(packet) => {
+                        debug!(
+                            "Client en retard de {} paquets monde",
 
-            if let Err(e) =
-                send_packet(
-                    &mut self.stream,
-                    &packet
-                ).await
-            {
+                            count
+                        );
+                    }
 
-                error!(
-                    "Erreur d'envoi du paquet monde : {}",
-                    
-                    e
-                );
+                    Err(
+                        broadcast::error::RecvError::Closed
+                    ) => {
 
-                break;
-            }
-        }
+                        error!(
+                            "Canal monde fermé"
+                        );
 
-        Err(
-            broadcast::error::RecvError::Lagged(
-                count
-            )
-        ) => {
-
-            debug!(
-                "Client en retard de {} paquets monde",
-                
-                count
-            );
-        }
-
-        Err(
-            broadcast::error::RecvError::Closed
-        ) => {
-
-            error!(
-                "Canal monde fermé"
-            );
-
-            break;
-        }
-    }
-}
+                        break;
+                    }
+                }
             }
+                        }
         }
 
-
         // ========================================================
         // FIN DE SESSION
         // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:473:
-        self.world
-    .remove_player(self.session_id)
-    .await;
+        self.world.remove_player(self.session_id).await;
 
-self.world
-    .broadcast_player_remove(self.session_id);
+        self.world.broadcast_player_remove(self.session_id);
         self.mark_disconnected().await;
 
-
-        info!(
-            "Fin de session : {}",
-            self.session_id
-        );
+        info!("Fin de session : {}", self.session_id);
     }
 
-
     // ============================================================
     // RÉCUPÉRATION DES INFORMATIONS DE BAN
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:492:
 
-    pub async fn get_ban_info(
-        &self,
-    ) -> Result<Option<BanInfo>, sqlx::Error> {
+    pub async fn get_ban_info(&self) -> Result<Option<BanInfo>, sqlx::Error> {
+        let user_id = match self.user_id() {
+            Some(id) => id,
 
-        let user_id =
-            match self.user_id() {
+            None => {
+                return Ok(None);
+            }
+        };
 
-                Some(id) => id,
-
-                None => {
-                    return Ok(None);
-                }
-            };
-
-
         // ========================================================
         // BAN PERMANENT
         // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:511:
 
-        if let Some((reason,)) =
-            sqlx::query_as::<_, (Option<String>,)>(
-                r#"
+        if let Some((reason,)) = sqlx::query_as::<_, (Option<String>,)>(
+            r#"
                 SELECT raison
                 FROM bansperm
                 WHERE user_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:518:
                 LIMIT 1
-                "#
-            )
-            .bind(user_id)
-            .fetch_optional(&self.pool)
-            .await?
+                "#,
+        )
+        .bind(user_id)
+        .fetch_optional(&self.pool)
+        .await?
         {
+            return Ok(Some(BanInfo {
+                ban_type: BanType::Permanent,
 
-            return Ok(Some(
-                BanInfo {
+                reason: reason.unwrap_or_else(|| "Aucune raison fournie".to_string()),
 
-                    ban_type:
-                        BanType::Permanent,
-
-                    reason:
-                        reason.unwrap_or_else(
-                            || "Aucune raison fournie".to_string()
-                        ),
-
-                    date_deban:
-                        None,
-                }
-            ));
+                date_deban: None,
+            }));
         }
 
-
         // ========================================================
         // BAN TEMPORAIRE
         // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:547:
 
-        if let Some((reason, date_deban)) =
-            sqlx::query_as::<_, (Option<String>, String)>(
-                r#"
+        if let Some((reason, date_deban)) = sqlx::query_as::<_, (Option<String>, String)>(
+            r#"
                 SELECT
                     raison,
                     date_deban
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:560:
                       > CURRENT_TIMESTAMP
 
                 LIMIT 1
-                "#
-            )
-            .bind(user_id)
-            .fetch_optional(&self.pool)
-            .await?
+                "#,
+        )
+        .bind(user_id)
+        .fetch_optional(&self.pool)
+        .await?
         {
+            return Ok(Some(BanInfo {
+                ban_type: BanType::Temporary,
 
-            return Ok(Some(
-                BanInfo {
+                reason: reason.unwrap_or_else(|| "Aucune raison fournie".to_string()),
 
-                    ban_type:
-                        BanType::Temporary,
-
-                    reason:
-                        reason.unwrap_or_else(
-                            || "Aucune raison fournie".to_string()
-                        ),
-
-                    date_deban:
-                        Some(date_deban),
-                }
-            ));
+                date_deban: Some(date_deban),
+            }));
         }
 
-
         // ========================================================
         // PAS DE BAN
         // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:592:
         Ok(None)
     }
 
-
     // ============================================================
     // ENCODAGE DU PAQUET BAN
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:599:
 
-    fn encode_ban_payload(
-        ban: &BanInfo,
-    ) -> Vec<u8> {
-
+    fn encode_ban_payload(ban: &BanInfo) -> Vec<u8> {
         format!(
             "{}\0{}\0{}",
             ban.ban_type as u8,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:607:
-
             ban.reason,
-
-            ban.date_deban
-                .as_deref()
-                .unwrap_or("")
+            ban.date_deban.as_deref().unwrap_or("")
         )
         .into_bytes()
     }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:616:
 
-
     // ============================================================
     // MARQUER COMME DÉCONNECTÉ
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:621:
 
-    async fn mark_disconnected(
-        &self,
-    ) {
+    async fn mark_disconnected(&self) {
+        let user_id = match self.user_id() {
+            Some(id) => id,
 
-        let user_id =
-            match self.user_id() {
+            None => return,
+        };
 
-                Some(id) => id,
-
-                None => return,
-            };
-
-
-        if let Err(e) =
-            sqlx::query(
-                r#"
+        if let Err(e) = sqlx::query(
+            r#"
                 UPDATE users
 
                 SET status = 'DISCONNECTED'
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:642:
                 WHERE user_id = ?
 
                   AND status = 'CONNECTED'
-                "#
-            )
-            .bind(user_id)
-            .execute(&self.pool)
-            .await
+                "#,
+        )
+        .bind(user_id)
+        .execute(&self.pool)
+        .await
         {
-
             error!(
                 "Impossible de mettre le joueur {} en DISCONNECTED [{}] : {}",
-                user_id,
-                self.session_id,
-                e
+                user_id, self.session_id, e
             );
 
             return;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:660:
         }
 
-
         debug!(
             "Utilisateur {} marqué comme DISCONNECTED [{}]",
-            user_id,
-            self.session_id
+            user_id, self.session_id
         );
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:670:
-
     // ============================================================
     // SET USER ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:674:
 
-    pub fn set_user_id(
-        &mut self,
-        id: Option<String>,
-    ) {
-
+    pub fn set_user_id(&mut self, id: Option<String>) {
         self.user_id = id;
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:683:
-
     // ============================================================
     // GET USER ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:687:
 
-    pub fn user_id(
-        &self,
-    ) -> Option<&str> {
-
-        self.user_id
-            .as_deref()
+    pub fn user_id(&self) -> Option<&str> {
+        self.user_id.as_deref()
     }
 
-
     // ============================================================
     // SET CLIENT ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:700:
 
-    pub fn set_client_id(
-        &mut self,
-        id: Option<i64>,
-    ) {
-
+    pub fn set_client_id(&mut self, id: Option<i64>) {
         self.client_id = id;
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:709:
-
     // ============================================================
     // GET CLIENT ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:713:
 
-    pub fn client_id(
-        &self,
-    ) -> Option<i64> {
-
+    pub fn client_id(&self) -> Option<i64> {
         self.client_id
     }
-    pub fn session_id(
-    &self,
-) -> Uuid {
+    pub fn session_id(&self) -> Uuid {
+        self.session_id
+    }
 
-    self.session_id
-}
-
-
     // ============================================================
     // SET ACCOUNT ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:731:
 
-    pub fn set_account_id(
-        &mut self,
-        id: Option<i64>,
-    ) {
-
+    pub fn set_account_id(&mut self, id: Option<i64>) {
         self.account_id = id;
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:740:
-
     // ============================================================
     // GET ACCOUNT ID
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:744:
 
-    pub fn account_id(
-        &self,
-    ) -> Option<i64> {
-
+    pub fn account_id(&self) -> Option<i64> {
         self.account_id
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:752:
-
     // ============================================================
     // DÉCONNEXION
     // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:756:
 
-    pub async fn disconnect(
-        &mut self,
-    ) {
-
+    pub async fn disconnect(&mut self) {
         // --------------------------------------------------------
         // Mettre le compte hors ligne AVANT de fermer le socket
         // --------------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:764:
 
         self.mark_disconnected().await;
 
-
         // --------------------------------------------------------
         // Fermeture du socket
         // --------------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/client.rs:771:
 
-        if let Err(e) =
-            self.stream.shutdown().await
-        {
-
-            error!(
-                "Erreur lors de la déconnexion : {}",
-                
-                e
-            );
-        }
-        else {
-
-            info!(
-                "Client déconnecté",
-                
-            );
+        if let Err(e) = self.stream.shutdown().await {
+            error!("Erreur lors de la déconnexion : {}", e);
+        } else {
+            info!("Client déconnecté",);
         }
     }
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1:
-use crate::network::{parser::{
-    parse_login_payload,
-    parse_signup_payload,},packet::{
-    Packet,
-    PacketType,
-    LogLevel,
-    ClientLog,},client::Client
-    
+use crate::network::{
+    client::Client,
+    packet::{ClientLog, LogLevel, Packet, PacketType},
+    parser::{parse_login_payload, parse_signup_payload},
 };
 
-use crate::world::world::{World,Position};
 use crate::gameplay::market_manager::MarketManager;
+use crate::world::world::{Position, World};
 
+use crate::auth::password::{hash_password, verify_password};
 
-use crate::auth::password::{
-    verify_password,
-    hash_password,
-};
+use log::{debug, error, info, trace, warn};
 
-use log::{
-    trace,
-    debug,
-    info,
-    warn,
-    error,
-};
+use sqlx::{Row, SqlitePool};
 
-use sqlx::{
-    SqlitePool,
-    Row,
-};
-
 use uuid::Uuid;
 
-
 // ============================================================
 // Structures
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:42:
     password_hash: String,
 }
 
-
 struct LoginData {
     user_id: String,
     password_hash: String,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:57:
 }
 pub struct PacketHandler;
 
-
 // ============================================================
 // Packet Handler
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:64:
 
 impl PacketHandler {
-    fn read_i64(
-    payload: &[u8],
-    start: usize,
-) -> Option<i64> {
+    fn read_i64(payload: &[u8], start: usize) -> Option<i64> {
+        let bytes = payload.get(start..start + 8)?;
 
-    let bytes =
-        payload.get(start..start + 8)?;
+        Some(i64::from_be_bytes(bytes.try_into().ok()?))
+    }
 
-    Some(
-        i64::from_be_bytes(
-            bytes.try_into().ok()?
-        )
-    )
-}
+    fn read_u64(payload: &[u8], start: usize) -> Option<u64> {
+        let bytes = payload.get(start..start + 8)?;
 
+        Some(u64::from_be_bytes(bytes.try_into().ok()?))
+    }
 
-fn read_u64(
-    payload: &[u8],
-    start: usize,
-) -> Option<u64> {
-
-    let bytes =
-        payload.get(start..start + 8)?;
-
-    Some(
-        u64::from_be_bytes(
-            bytes.try_into().ok()?
-        )
-    )
-}
-
     pub async fn handle(
         client: &mut Client,
         packet: Packet,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:100:
         pool: SqlitePool,
-        world : World,
+        world: World,
     ) -> HandlerResult {
-
         match packet.packet_type {
-
             // =================================================
             // LOG
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:109:
-
             PacketType::Log => {
+                let log = match serde_json::from_slice::<ClientLog>(&packet.payload) {
+                    Ok(log) => log,
 
-                let log =
-                    match serde_json::from_slice::<ClientLog>(
-                        &packet.payload
-                    ) {
+                    Err(e) => {
+                        error!("Impossible de décoder le paquet LOG : {}", e);
 
-                        Ok(log) => log,
+                        return HandlerResult::Nothing;
+                    }
+                };
 
-                        Err(e) => {
-
-                            error!(
-                                "Impossible de décoder le paquet LOG : {}",
-                                e
-                            );
-
-                            return HandlerResult::Nothing;
-                        }
-                    };
-
-
                 match log.level {
-
                     LogLevel::TRACE => {
-                        trace!(
-                            "[CLIENT] [{}:{}] {}",
-                            log.file,
-                            log.line,
-                            log.message
-                        );
+                        trace!("[CLIENT] [{}:{}] {}", log.file, log.line, log.message);
                     }
 
                     LogLevel::DEBUG => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:143:
-                        debug!(
-                            "[CLIENT] [{}:{}] {}",
-                            log.file,
-                            log.line,
-                            log.message
-                        );
+                        debug!("[CLIENT] [{}:{}] {}", log.file, log.line, log.message);
                     }
 
                     LogLevel::INFO => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:152:
-                        info!(
-                            "[CLIENT] [{}:{}] {}",
-                            log.file,
-                            log.line,
-                            log.message
-                        );
+                        info!("[CLIENT] [{}:{}] {}", log.file, log.line, log.message);
                     }
 
                     LogLevel::WARNING => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:161:
-                        warn!(
-                            "[CLIENT] [{}:{}] {}",
-                            log.file,
-                            log.line,
-                            log.message
-                        );
+                        warn!("[CLIENT] [{}:{}] {}", log.file, log.line, log.message);
                     }
 
                     LogLevel::ERROR => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:170:
-                        error!(
-                            "[CLIENT] [{}:{}] {}",
-                            log.file,
-                            log.line,
-                            log.message
-                        );
+                        error!("[CLIENT] [{}:{}] {}", log.file, log.line, log.message);
                     }
                 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:179:
-
                 HandlerResult::Nothing
             }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:183:
-
             // =================================================
             // PING
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:187:
-
             PacketType::Ping => {
-
                 debug!("Ping reçu");
 
-                HandlerResult::Response(
-                    Packet::new(
-                        PacketType::Ping,
-                        b"PONG".to_vec(),
-                    )
-                )
+                HandlerResult::Response(Packet::new(PacketType::Ping, b"PONG".to_vec()))
             }
 
-
             // =================================================
             // BAN
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:204:
-
             PacketType::BAN => {
+                debug!("Packet BAN reçu depuis le client : ignoré");
 
-                debug!(
-                    "Packet BAN reçu depuis le client : ignoré"
-                );
-
                 HandlerResult::Nothing
             }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:214:
-
             // =================================================
             // SIGN UP
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:218:
-
             PacketType::SignUp => {
-
                 // ------------------------------------------------
                 // Parser
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:224:
 
-                let (email, password) =
-                    match parse_signup_payload(
-                        &packet.payload
-                    ) {
+                let (email, password) = match parse_signup_payload(&packet.payload) {
+                    Ok(signup) => signup,
 
-                        Ok(signup) => signup,
+                    Err(error) => {
+                        debug!("SIGN_UP invalide : {}", error);
 
-                        Err(error) => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::SignUpResponse,
+                            b"SIGN_UP invalide".to_vec(),
+                        ));
+                    }
+                };
 
-                            debug!(
-                                "SIGN_UP invalide : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::SignUpResponse,
-                                    b"SIGN_UP invalide".to_vec(),
-                                )
-                            );
-                        }
-                    };
-
-
                 // ------------------------------------------------
                 // Hash Argon2
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:252:
 
-                let password_hash =
-                    match hash_password(&password) {
+                let password_hash = match hash_password(&password) {
+                    Ok(hash) => hash,
 
-                        Ok(hash) => hash,
+                    Err(error) => {
+                        error!("Erreur lors du hash du mot de passe : {}", error);
 
-                        Err(error) => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::SignUpResponse,
+                            b"Erreur serveur".to_vec(),
+                        ));
+                    }
+                };
 
-                            error!(
-                                "Erreur lors du hash du mot de passe : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::SignUpResponse,
-                                    b"Erreur serveur".to_vec(),
-                                )
-                            );
-                        }
-                    };
-
-
                 // ------------------------------------------------
                 // UUID
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:278:
 
-                let user_id =
-                    Uuid::new_v4().to_string();
+                let user_id = Uuid::new_v4().to_string();
 
-
                 // ------------------------------------------------
                 // Création utilisateur
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:300:
                 .execute(&pool)
                 .await
                 {
-
                     Ok(_) => {
+                        debug!("Nouvel utilisateur créé : {}", email);
 
-                        debug!(
-                            "Nouvel utilisateur créé : {}",
-                            email
-                        );
+                        client.set_user_id(Some(user_id.clone()));
 
-                        client.set_user_id(
-                            Some(user_id.clone())
-                        );
-
-                        HandlerResult::Response(
-                            Packet::new(
-                                PacketType::SignUpResponse,
-                                b"Utilisateur cree avec succes".to_vec(),
-                            )
-                        )
+                        HandlerResult::Response(Packet::new(
+                            PacketType::SignUpResponse,
+                            b"Utilisateur cree avec succes".to_vec(),
+                        ))
                     }
 
-
                     Err(error) => {
+                        let error_msg = error.to_string();
 
-                        let error_msg =
-                            error.to_string();
+                        if error_msg.contains("UNIQUE constraint failed") {
+                            debug!("SIGN_UP refusé : email déjà utilisé");
 
-
-                        if error_msg.contains(
-                            "UNIQUE constraint failed"
-                        ) {
-
-                            debug!(
-                                "SIGN_UP refusé : email déjà utilisé"
-                            );
-
-                            HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::SignUpResponse,
-                                    b"Email deja utilise".to_vec(),
-                                )
-                            )
-
+                            HandlerResult::Response(Packet::new(
+                                PacketType::SignUpResponse,
+                                b"Email deja utilise".to_vec(),
+                            ))
                         } else {
+                            error!("Erreur lors de la création du user : {}", error);
 
-                            error!(
-                                "Erreur lors de la création du user : {}",
-                                error
-                            );
-
-                            HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::SignUpResponse,
-                                    b"Erreur serveur".to_vec(),
-                                )
-                            )
+                            HandlerResult::Response(Packet::new(
+                                PacketType::SignUpResponse,
+                                b"Erreur serveur".to_vec(),
+                            ))
                         }
                     }
                 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:361:
             }
 
-
             // =================================================
             // LOGIN
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:367:
-
             PacketType::Login => {
-
                 // ------------------------------------------------
                 // Parser LOGIN
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:373:
 
-                let (email, password) =
-                    match parse_login_payload(
-                        &packet.payload
-                    ) {
+                let (email, password) = match parse_login_payload(&packet.payload) {
+                    Ok(login) => login,
 
-                        Ok(login) => login,
+                    Err(error) => {
+                        debug!("LOGIN invalide : {}", error);
 
-                        Err(error) => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::LoginResponse,
+                            b"LOGIN invalide".to_vec(),
+                        ));
+                    }
+                };
 
-                            debug!(
-                                "LOGIN invalide : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::LoginResponse,
-                                    b"LOGIN invalide".to_vec(),
-                                )
-                            );
-                        }
-                    };
-
-
                 // ------------------------------------------------
                 // Récupération utilisateur + bans
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:401:
 
-                let login_data =
-                    match sqlx::query(
-                        r#"
+                let login_data = match sqlx::query(
+                    r#"
                         SELECT
                             u.user_id,
                             u.password_hash,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:434:
 
                         WHERE u.email = ?
                         "#,
-                    )
-                    .bind(&email)
-                    .fetch_optional(&pool)
-                    .await
-                    {
+                )
+                .bind(&email)
+                .fetch_optional(&pool)
+                .await
+                {
+                    Ok(Some(row)) => LoginData {
+                        user_id: row.get::<String, _>("user_id"),
 
-                        Ok(Some(row)) => {
+                        password_hash: row.get::<String, _>("password_hash"),
 
-                            LoginData {
+                        is_banned_perm: row.get::<i64, _>("is_banned_perm") != 0,
 
-                                user_id:
-                                    row.get::<String, _>(
-                                        "user_id"
-                                    ),
+                        is_banned_temp: row.get::<i64, _>("is_banned_temp") != 0,
+                    },
 
-                                password_hash:
-                                    row.get::<String, _>(
-                                        "password_hash"
-                                    ),
+                    Ok(None) => {
+                        debug!("Tentative de connexion avec un utilisateur inexistant");
 
-                                is_banned_perm:
-                                    row.get::<i64, _>(
-                                        "is_banned_perm"
-                                    ) != 0,
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::LoginResponse,
+                            b"Identifiants invalides".to_vec(),
+                        ));
+                    }
 
-                                is_banned_temp:
-                                    row.get::<i64, _>(
-                                        "is_banned_temp"
-                                    ) != 0,
-                            }
-                        }
+                    Err(error) => {
+                        error!("Erreur lors de la recherche de l'utilisateur : {}", error);
 
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::LoginResponse,
+                            b"Erreur serveur".to_vec(),
+                        ));
+                    }
+                };
 
-                        Ok(None) => {
-
-                            debug!(
-                                "Tentative de connexion avec un utilisateur inexistant"
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::LoginResponse,
-                                    b"Identifiants invalides".to_vec(),
-                                )
-                            );
-                        }
-
-
-                        Err(error) => {
-
-                            error!(
-                                "Erreur lors de la recherche de l'utilisateur : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::LoginResponse,
-                                    b"Erreur serveur".to_vec(),
-                                )
-                            );
-                        }
-                    };
-
-
                 // ------------------------------------------------
                 // BAN PERMANENT
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:505:
 
                 if login_data.is_banned_perm {
+                    debug!("Connexion refusée : utilisateur banni définitivement");
 
-                    debug!(
-                        "Connexion refusée : utilisateur banni définitivement"
-                    );
-
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Compte banni definitivement".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Compte banni definitivement".to_vec(),
+                    ));
                 }
 
-
                 // ------------------------------------------------
                 // BAN FERME
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:524:
 
                 if login_data.is_banned_temp {
+                    debug!("Connexion refusée : utilisateur temporairement banni");
 
-                    debug!(
-                        "Connexion refusée : utilisateur temporairement banni"
-                    );
-
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Compte temporairement banni".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Compte temporairement banni".to_vec(),
+                    ));
                 }
 
-
                 // ------------------------------------------------
                 // Vérification mot de passe
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:543:
 
-                let password_valid =
-                    verify_password(
-                        &password,
-                        &login_data.password_hash,
-                    );
+                let password_valid = verify_password(&password, &login_data.password_hash);
 
-
                 // =================================================
                 // MOT DE PASSE INCORRECT
                 // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:554:
 
                 if !password_valid {
-
                     // --------------------------------------------
                     // Compteur de tentatives
                     // --------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:560:
 
-                    let attempts =
-                        match sqlx::query_scalar::<_, i64>(
-                            r#"
+                    let attempts = match sqlx::query_scalar::<_, i64>(
+                        r#"
                             INSERT INTO login_attempts (
                                 user_id,
                                 failed_attempts,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:583:
 
                             RETURNING failed_attempts
                             "#,
-                        )
-                        .bind(&login_data.user_id)
-                        .fetch_one(&pool)
-                        .await
-                        {
+                    )
+                    .bind(&login_data.user_id)
+                    .fetch_one(&pool)
+                    .await
+                    {
+                        Ok(value) => value,
 
-                            Ok(value) => value,
+                        Err(error) => {
+                            error!(
+                                "Erreur lors de l'enregistrement de la tentative : {}",
+                                error
+                            );
 
-                            Err(error) => {
+                            return HandlerResult::Response(Packet::new(
+                                PacketType::LoginResponse,
+                                b"Erreur serveur".to_vec(),
+                            ));
+                        }
+                    };
 
-                                error!(
-                                    "Erreur lors de l'enregistrement de la tentative : {}",
-                                    error
-                                );
-
-                                return HandlerResult::Response(
-                                    Packet::new(
-                                        PacketType::LoginResponse,
-                                        b"Erreur serveur".to_vec(),
-                                    )
-                                );
-                            }
-                        };
-
-
                     debug!(
                         "Mot de passe incorrect pour {} : tentative {}",
-                        email,
-                        attempts
+                        email, attempts
                     );
 
-
                     // =================================================
                     // 3 ÉCHECS
                     // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:621:
-                    
-                    if attempts >= 3 {
 
+                    if attempts >= 3 {
                         // --------------------------------------------
                         // Recherche du sursis
                         // --------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:627:
                         debug!(
-    "DEBUG BAN : création du ban pour user_id={}, tentatives={}",
-    login_data.user_id,
-    attempts
-);
-                        let sursis_jours =
-                            match sqlx::query_scalar::<_, i64>(
-                                r#"
+                            "DEBUG BAN : création du ban pour user_id={}, tentatives={}",
+                            login_data.user_id, attempts
+                        );
+                        let sursis_jours = match sqlx::query_scalar::<_, i64>(
+                            r#"
                                 SELECT sursis
 
                                 FROM banssursis
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:640:
 
                                 LIMIT 1
                                 "#,
-                            )
-                            .bind(&login_data.user_id)
-                            .fetch_optional(&pool)
-                            .await
-                            {
+                        )
+                        .bind(&login_data.user_id)
+                        .fetch_optional(&pool)
+                        .await
+                        {
+                            Ok(value) => value,
 
-                                Ok(value) => value,
+                            Err(error) => {
+                                error!("Erreur lors de la vérification du sursis : {}", error);
 
-                                Err(error) => {
+                                return HandlerResult::Response(Packet::new(
+                                    PacketType::LoginResponse,
+                                    b"Erreur serveur".to_vec(),
+                                ));
+                            }
+                        };
 
-                                    error!(
-                                        "Erreur lors de la vérification du sursis : {}",
-                                        error
-                                    );
-
-                                    return HandlerResult::Response(
-                                        Packet::new(
-                                            PacketType::LoginResponse,
-                                            b"Erreur serveur".to_vec(),
-                                        )
-                                    );
-                                }
-                            };
-
-
                         // =================================================
                         // SURsis EXISTANT
                         // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:671:
 
-                        if let Some(jours) =
-                            sursis_jours
-                        {
-
+                        if let Some(jours) = sursis_jours {
                             // ----------------------------------------
                             // Validation
                             // ----------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:679:
 
                             if jours <= 0 {
+                                error!("Sursis invalide pour {} : {} jour(s)", email, jours);
 
-                                error!(
-                                    "Sursis invalide pour {} : {} jour(s)",
-                                    email,
-                                    jours
-                                );
-
-                                return HandlerResult::Response(
-                                    Packet::new(
-                                        PacketType::LoginResponse,
-                                        b"Erreur serveur".to_vec(),
-                                    )
-                                );
+                                return HandlerResult::Response(Packet::new(
+                                    PacketType::LoginResponse,
+                                    b"Erreur serveur".to_vec(),
+                                ));
                             }
 
+                            debug!("Activation du sursis pour {} : {} jour(s)", email, jours);
 
-                            debug!(
-                                "Activation du sursis pour {} : {} jour(s)",
-                                email,
-                                jours
-                            );
-
-
                             // ----------------------------------------
                             // Ajouter le sursis au ban ferme
                             //
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:720:
                             // ----------------------------------------
 
                             let result = sqlx::query(
-    r#"
+                                r#"
     INSERT INTO bansferme (
         user_id,
         auteur,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:773:
             )
         END
     "#,
-)
-.bind(&login_data.user_id)
-.bind(jours)
-.bind(jours)
-.bind(jours)
-.execute(&pool)
-.await;
+                            )
+                            .bind(&login_data.user_id)
+                            .bind(jours)
+                            .bind(jours)
+                            .bind(jours)
+                            .execute(&pool)
+                            .await;
 
-                            if let Err(error) =
-                                result
-                            {
+                            if let Err(error) = result {
+                                error!("Impossible d'activer le sursis pour {} : {}", email, error);
 
-                                error!(
-                                    "Impossible d'activer le sursis pour {} : {}",
-                                    email,
-                                    error
-                                );
-
-                                return HandlerResult::Response(
-                                    Packet::new(
-                                        PacketType::LoginResponse,
-                                        b"Erreur serveur".to_vec(),
-                                    )
-                                );
+                                return HandlerResult::Response(Packet::new(
+                                    PacketType::LoginResponse,
+                                    b"Erreur serveur".to_vec(),
+                                ));
                             }
 
-
                             // ----------------------------------------
                             // Supprimer le sursis consommé
                             // ----------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:806:
 
-                            if let Err(error) =
-                                sqlx::query(
-                                    r#"
+                            if let Err(error) = sqlx::query(
+                                r#"
                                     DELETE FROM banssursis
 
                                     WHERE user_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:813:
                                     "#,
-                                )
-                                .bind(&login_data.user_id)
-                                .execute(&pool)
-                                .await
+                            )
+                            .bind(&login_data.user_id)
+                            .execute(&pool)
+                            .await
                             {
+                                error!("Impossible de supprimer le sursis consommé : {}", error);
 
-                                error!(
-                                    "Impossible de supprimer le sursis consommé : {}",
-                                    error
-                                );
-
-                                return HandlerResult::Response(
-                                    Packet::new(
-                                        PacketType::LoginResponse,
-                                        b"Erreur serveur".to_vec(),
-                                    )
-                                );
+                                return HandlerResult::Response(Packet::new(
+                                    PacketType::LoginResponse,
+                                    b"Erreur serveur".to_vec(),
+                                ));
                             }
 
-
-                            debug!(
-                                "Sursis de {} jour(s) activé pour {}",
-                                jours,
-                                email
-                            );
+                            debug!("Sursis de {} jour(s) activé pour {}", jours, email);
                         }
-
-
                         // =================================================
                         // PAS DE SURsis
                         // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:845:
-
                         else {
+                            debug!("Aucun sursis pour {}", email);
 
-                            debug!(
-                                "Aucun sursis pour {}",
-                                email
-                            );
-
-
                             // --------------------------------------------
                             // Ban automatique de 10 minutes
                             // --------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:978:
                                 .execute(&pool)
                                 .await;
 
+                            if let Err(error) = result {
+                                error!("Impossible de créer le ban temporaire : {}", error);
 
-                            if let Err(error) =
-                                result
-                            {
-
-                                error!(
-                                    "Impossible de créer le ban temporaire : {}",
-                                    error
-                                );
-
-                                return HandlerResult::Response(
-                                    Packet::new(
-                                        PacketType::LoginResponse,
-                                        b"Erreur serveur".to_vec(),
-                                    )
-                                );
+                                return HandlerResult::Response(Packet::new(
+                                    PacketType::LoginResponse,
+                                    b"Erreur serveur".to_vec(),
+                                ));
                             }
                         }
-                        debug!(
-    "DEBUG BAN : INSERT terminé pour {}",
-    login_data.user_id
-);
+                        debug!("DEBUG BAN : INSERT terminé pour {}", login_data.user_id);
 
                         // =================================================
                         // RESET DES TENTATIVES
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1006:
                         // =================================================
 
-                        if let Err(error) =
-                            sqlx::query(
-                                r#"
+                        if let Err(error) = sqlx::query(
+                            r#"
                                 DELETE FROM login_attempts
 
                                 WHERE user_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1014:
                                 "#,
-                            )
-                            .bind(&login_data.user_id)
-                            .execute(&pool)
-                            .await
+                        )
+                        .bind(&login_data.user_id)
+                        .execute(&pool)
+                        .await
                         {
+                            error!("Impossible de supprimer le compteur : {}", error);
 
-                            error!(
-                                "Impossible de supprimer le compteur : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::LoginResponse,
-                                    b"Erreur serveur".to_vec(),
-                                )
-                            );
+                            return HandlerResult::Response(Packet::new(
+                                PacketType::LoginResponse,
+                                b"Erreur serveur".to_vec(),
+                            ));
                         }
 
-
                         // =================================================
                         // RÉPONSE
                         // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1038:
                         info!("Utilisateur banni");
-                        return HandlerResult::Response(
-                            Packet::new(
-                                PacketType::LoginResponse,
-                                b"Trop de tentatives. Compte bloque temporairement.".to_vec(),
-                            )
-                        );
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::LoginResponse,
+                            b"Trop de tentatives. Compte bloque temporairement.".to_vec(),
+                        ));
                     }
 
-
                     // ------------------------------------------------
                     // Moins de 3 tentatives
                     // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1051:
 
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Identifiants invalides".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Identifiants invalides".to_vec(),
+                    ));
                 }
 
-
                 // =================================================
                 // MOT DE PASSE CORRECT
                 // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1066:
                 // Vérifier si déjà connecté
                 // ------------------------------------------------
 
-                let is_already_connected =
-                    match sqlx::query_scalar::<_, i64>(
-                        r#"
+                let is_already_connected = match sqlx::query_scalar::<_, i64>(
+                    r#"
                         SELECT EXISTS(
                             SELECT 1
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1079:
                               AND status = 'CONNECTED'
                         )
                         "#,
-                    )
-                    .bind(&login_data.user_id)
-                    .fetch_one(&pool)
-                    .await
-                    {
+                )
+                .bind(&login_data.user_id)
+                .fetch_one(&pool)
+                .await
+                {
+                    Ok(value) => value != 0,
 
-                        Ok(value) =>
-                            value != 0,
+                    Err(error) => {
+                        error!("Erreur lors de la vérification de connexion : {}", error);
 
-                        Err(error) => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::LoginResponse,
+                            b"Erreur serveur".to_vec(),
+                        ));
+                    }
+                };
 
-                            error!(
-                                "Erreur lors de la vérification de connexion : {}",
-                                error
-                            );
-
-                            return HandlerResult::Response(
-                                Packet::new(
-                                    PacketType::LoginResponse,
-                                    b"Erreur serveur".to_vec(),
-                                )
-                            );
-                        }
-                    };
-
-
                 if is_already_connected {
+                    debug!("Tentative de connexion avec un compte déjà connecté");
 
-                    debug!(
-                        "Tentative de connexion avec un compte déjà connecté"
-                    );
-
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Ce compte est deja connecte".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Ce compte est deja connecte".to_vec(),
+                    ));
                 }
 
-
                 // ------------------------------------------------
                 // CONNECTED
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1126:
 
-                if let Err(error) =
-                    sqlx::query(
-                        r#"
+                if let Err(error) = sqlx::query(
+                    r#"
                         UPDATE users
 
                         SET status = 'CONNECTED'
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1133:
 
                         WHERE user_id = ?
                         "#,
-                    )
-                    .bind(&login_data.user_id)
-                    .execute(&pool)
-                    .await
+                )
+                .bind(&login_data.user_id)
+                .execute(&pool)
+                .await
                 {
+                    error!("Erreur lors de la connexion du joueur : {}", error);
 
-                    error!(
-                        "Erreur lors de la connexion du joueur : {}",
-                        error
-                    );
-
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Erreur serveur".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Erreur serveur".to_vec(),
+                    ));
                 }
 
-
                 // ------------------------------------------------
                 // Reset login attempts
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1159:
 
-                if let Err(error) =
-                    sqlx::query(
-                        r#"
+                if let Err(error) = sqlx::query(
+                    r#"
                         DELETE FROM login_attempts
 
                         WHERE user_id = ?
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1166:
                         "#,
-                    )
-                    .bind(&login_data.user_id)
-                    .execute(&pool)
-                    .await
+                )
+                .bind(&login_data.user_id)
+                .execute(&pool)
+                .await
                 {
+                    error!("Impossible de réinitialiser les tentatives : {}", error);
 
-                    error!(
-                        "Impossible de réinitialiser les tentatives : {}",
-                        error
-                    );
-
-                    return HandlerResult::Response(
-                        Packet::new(
-                            PacketType::LoginResponse,
-                            b"Erreur serveur".to_vec(),
-                        )
-                    );
+                    return HandlerResult::Response(Packet::new(
+                        PacketType::LoginResponse,
+                        b"Erreur serveur".to_vec(),
+                    ));
                 }
 
-
                 // ------------------------------------------------
                 // Login réussi
                 // ------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1190:
 
-                debug!(
-                    "Utilisateur authentifié : {}",
-                    email
-                );
+                debug!("Utilisateur authentifié : {}", email);
 
+                client.set_user_id(Some(login_data.user_id.clone()));
 
-                client.set_user_id(
-                    Some(
-                        login_data.user_id.clone()
-                    )
-                );
-
-
-                HandlerResult::Response(
-                    Packet::new(
-                        PacketType::LoginResponse,
-                        format!(
-                            "Utilisateur {} authentifié",
-                            email
-                        )
-                        .into_bytes(),
-                    )
-                )
+                HandlerResult::Response(Packet::new(
+                    PacketType::LoginResponse,
+                    format!("Utilisateur {} authentifié", email).into_bytes(),
+                ))
             }
 
-
             // =================================================
             // CHAT
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1220:
-
             PacketType::Chat => {
+                debug!("Message : {}", String::from_utf8_lossy(&packet.payload));
 
-                debug!(
-                    "Message : {}",
-                    String::from_utf8_lossy(
-                        &packet.payload
-                    )
-                );
-
-                HandlerResult::Response(
-                    Packet::new(
-                        PacketType::Chat,
-                        packet.payload,
-                    )
-                )
+                HandlerResult::Response(Packet::new(PacketType::Chat, packet.payload))
             }
 
-
             // =================================================
             // MOVE
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1242:
+            PacketType::Move => {
+                if packet.payload.len() != 12 {
+                    warn!("Paquet Move invalide : {} octets", packet.payload.len());
 
-           PacketType::Move => {
-    if packet.payload.len() != 12 {
-        warn!(
-            "Paquet Move invalide : {} octets",
-            packet.payload.len()
-        );
+                    return HandlerResult::Nothing;
+                }
 
-        return HandlerResult::Nothing;
-    }
+                let x = i32::from_be_bytes([
+                    packet.payload[0],
+                    packet.payload[1],
+                    packet.payload[2],
+                    packet.payload[3],
+                ]);
 
-    let x = i32::from_be_bytes([
-        packet.payload[0],
-        packet.payload[1],
-        packet.payload[2],
-        packet.payload[3],
-    ]);
+                let y = i32::from_be_bytes([
+                    packet.payload[4],
+                    packet.payload[5],
+                    packet.payload[6],
+                    packet.payload[7],
+                ]);
 
-    let y = i32::from_be_bytes([
-        packet.payload[4],
-        packet.payload[5],
-        packet.payload[6],
-        packet.payload[7],
-    ]);
+                let z = i32::from_be_bytes([
+                    packet.payload[8],
+                    packet.payload[9],
+                    packet.payload[10],
+                    packet.payload[11],
+                ]);
 
-    let z = i32::from_be_bytes([
-        packet.payload[8],
-        packet.payload[9],
-        packet.payload[10],
-        packet.payload[11],
-    ]);
+                let player_id = client.session_id();
 
-    let player_id = client.session_id();
+                let position = Position::new(x, y, z);
 
-    let position = Position::new(x, y, z);
+                world.set_position(player_id, position).await;
 
-    world
-        .set_position(player_id, position)
-        .await;
+                world.broadcast_player_state(player_id, position);
 
-    world.broadcast_player_state(
-        player_id,
-        position,
-    );
-
-    HandlerResult::Nothing
-}
+                HandlerResult::Nothing
+            }
             PacketType::DECO => {
+                info!("Demande de déconnexion reçue");
 
-    info!(
-        "Demande de déconnexion reçue"
-    );
-
-    HandlerResult::Disconnect
-}
-PacketType::MarketBuy => {
-
-    if packet.payload.len() != 24 {
-
-        error!(
-            "MARKET_BUY : payload invalide ({} octets)",
-            packet.payload.len()
-        );
-
-        return HandlerResult::Response(
-            Packet::new(
-                PacketType::MarketBuy,
-                b"MARKET_BUY invalide".to_vec(),
-            )
-        );
-    }
-
-
-    let objet_id =
-        match Self::read_i64(
-            &packet.payload,
-            0,
-        ) {
-            Some(value) => value,
-
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketBuy,
-                        b"MARKET_BUY invalide".to_vec(),
-                    )
-                );
+                HandlerResult::Disconnect
             }
-        };
+            PacketType::MarketBuy => {
+                if packet.payload.len() != 24 {
+                    error!(
+                        "MARKET_BUY : payload invalide ({} octets)",
+                        packet.payload.len()
+                    );
 
-
-    let quantity =
-        match Self::read_u64(
-            &packet.payload,
-            8,
-        ) {
-            Some(value) => value,
-
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
+                    return HandlerResult::Response(Packet::new(
                         PacketType::MarketBuy,
                         b"MARKET_BUY invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                    ));
+                }
 
+                let objet_id = match Self::read_i64(&packet.payload, 0) {
+                    Some(value) => value,
 
-    let prix_unitaire_max =
-        match Self::read_i64(
-            &packet.payload,
-            16,
-        ) {
-            Some(value) => value,
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            b"MARKET_BUY invalide".to_vec(),
+                        ));
+                    }
+                };
 
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketBuy,
-                        b"MARKET_BUY invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                let quantity = match Self::read_u64(&packet.payload, 8) {
+                    Some(value) => value,
 
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            b"MARKET_BUY invalide".to_vec(),
+                        ));
+                    }
+                };
 
-    let account_id =
-        match client.account_id() {
+                let prix_unitaire_max = match Self::read_i64(&packet.payload, 16) {
+                    Some(value) => value,
 
-            Some(id) => id,
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            b"MARKET_BUY invalide".to_vec(),
+                        ));
+                    }
+                };
 
-            None => {
+                let account_id = match client.account_id() {
+                    Some(id) => id,
 
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketBuy,
-                        b"Compte non selectionne".to_vec(),
-                    )
-                );
-            }
-        };
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            b"Compte non selectionne".to_vec(),
+                        ));
+                    }
+                };
 
+                let market = MarketManager::new(pool.clone());
 
-    let market =
-        MarketManager::new(
-            pool.clone()
-        );
+                match market
+                    .creer_ordre_achat(account_id, objet_id, quantity, prix_unitaire_max)
+                    .await
+                {
+                    Ok(ordre_id) => {
+                        info!(
+                            "Ordre d'achat {} créé |objet={} quantité={} prix_max={}",
+                            ordre_id, objet_id, quantity, prix_unitaire_max
+                        );
 
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            ordre_id.to_be_bytes().to_vec(),
+                        ))
+                    }
 
-    match market.creer_ordre_achat(
-        account_id,
-        objet_id,
-        quantity,
-        prix_unitaire_max,
-    ).await {
+                    Err(e) => {
+                        error!("Erreur création ordre d'achat : {}", e);
 
-        Ok(ordre_id) => {
-
-            info!(
-                "Ordre d'achat {} créé |objet={} quantité={} prix_max={}",
-                ordre_id,
-                objet_id,
-                quantity,
-                prix_unitaire_max
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketBuy,
-                    ordre_id
-                        .to_be_bytes()
-                        .to_vec(),
-                )
-            )
-        }
-
-
-        Err(e) => {
-
-            error!(
-                "Erreur création ordre d'achat : {}",
-                e
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketBuy,
-                    format!(
-                        "Erreur: {}",
-                        e
-                    )
-                    .into_bytes(),
-                )
-            )
-        }
-    }
-}
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketBuy,
+                            format!("Erreur: {}", e).into_bytes(),
+                        ))
+                    }
+                }
+            }
             PacketType::MarketSell => {
+                if packet.payload.len() != 24 {
+                    error!(
+                        "MARKET_SELL : payload invalide ({} octets)",
+                        packet.payload.len()
+                    );
 
-    if packet.payload.len() != 24 {
-
-        error!(
-            "MARKET_SELL : payload invalide ({} octets)",
-            packet.payload.len()
-        );
-
-        return HandlerResult::Response(
-            Packet::new(
-                PacketType::MarketSell,
-                b"MARKET_SELL invalide".to_vec(),
-            )
-        );
-    }
-
-
-    let objet_id =
-        match Self::read_i64(
-            &packet.payload,
-            0,
-        ) {
-            Some(value) => value,
-
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
+                    return HandlerResult::Response(Packet::new(
                         PacketType::MarketSell,
                         b"MARKET_SELL invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                    ));
+                }
 
+                let objet_id = match Self::read_i64(&packet.payload, 0) {
+                    Some(value) => value,
 
-    let quantity =
-        match Self::read_u64(
-            &packet.payload,
-            8,
-        ) {
-            Some(value) => value,
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            b"MARKET_SELL invalide".to_vec(),
+                        ));
+                    }
+                };
 
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketSell,
-                        b"MARKET_SELL invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                let quantity = match Self::read_u64(&packet.payload, 8) {
+                    Some(value) => value,
 
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            b"MARKET_SELL invalide".to_vec(),
+                        ));
+                    }
+                };
 
-    let prix_unitaire =
-        match Self::read_i64(
-            &packet.payload,
-            16,
-        ) {
-            Some(value) => value,
+                let prix_unitaire = match Self::read_i64(&packet.payload, 16) {
+                    Some(value) => value,
 
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketSell,
-                        b"MARKET_SELL invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            b"MARKET_SELL invalide".to_vec(),
+                        ));
+                    }
+                };
 
+                let account_id = match client.account_id() {
+                    Some(id) => id,
 
-    let account_id =
-        match client.account_id() {
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            b"Compte non selectionne".to_vec(),
+                        ));
+                    }
+                };
 
-            Some(id) => id,
+                let market = MarketManager::new(pool.clone());
 
-            None => {
+                match market
+                    .creer_ordre_vente(account_id, objet_id, quantity, prix_unitaire)
+                    .await
+                {
+                    Ok(ordre_id) => {
+                        info!(
+                            "Ordre de vente {} créé | objet={} quantité={} prix={}",
+                            ordre_id, objet_id, quantity, prix_unitaire
+                        );
 
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketSell,
-                        b"Compte non selectionne".to_vec(),
-                    )
-                );
-            }
-        };
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            ordre_id.to_be_bytes().to_vec(),
+                        ))
+                    }
 
+                    Err(e) => {
+                        error!("Erreur création ordre de vente : {}", e);
 
-    let market =
-        MarketManager::new(
-            pool.clone()
-        );
-
-
-    match market.creer_ordre_vente(
-        account_id,
-        objet_id,
-        quantity,
-        prix_unitaire,
-    ).await {
-
-        Ok(ordre_id) => {
-
-            info!(
-                "Ordre de vente {} créé | objet={} quantité={} prix={}",
-                ordre_id,
-                objet_id,
-                quantity,
-                prix_unitaire
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketSell,
-                    ordre_id
-                        .to_be_bytes()
-                        .to_vec(),
-                )
-            )
-        }
-
-
-        Err(e) => {
-
-            error!(
-                "Erreur création ordre de vente : {}",
-                e
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketSell,
-                    format!(
-                        "Erreur: {}",
-                        e
-                    )
-                    .into_bytes(),
-                )
-            )
-        }
-    }
-}
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketSell,
+                            format!("Erreur: {}", e).into_bytes(),
+                        ))
+                    }
+                }
+            }
             PacketType::MarketCancelBuy => {
-
-    if packet.payload.len() != 8 {
-
-        return HandlerResult::Response(
-            Packet::new(
-                PacketType::MarketCancelBuy,
-                b"MARKET_CANCEL_BUY invalide".to_vec(),
-            )
-        );
-    }
-
-
-    let ordre_id =
-        match Self::read_i64(
-            &packet.payload,
-            0,
-        ) {
-            Some(value) => value,
-
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
+                if packet.payload.len() != 8 {
+                    return HandlerResult::Response(Packet::new(
                         PacketType::MarketCancelBuy,
                         b"MARKET_CANCEL_BUY invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                    ));
+                }
 
+                let ordre_id = match Self::read_i64(&packet.payload, 0) {
+                    Some(value) => value,
 
-    let account_id =
-        match client.account_id() {
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelBuy,
+                            b"MARKET_CANCEL_BUY invalide".to_vec(),
+                        ));
+                    }
+                };
 
-            Some(id) => id,
+                let account_id = match client.account_id() {
+                    Some(id) => id,
 
-            None => {
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelBuy,
+                            b"Compte non selectionne".to_vec(),
+                        ));
+                    }
+                };
 
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketCancelBuy,
-                        b"Compte non selectionne".to_vec(),
-                    )
-                );
-            }
-        };
+                let market = MarketManager::new(pool.clone());
 
+                match market.annuler_ordre_achat(account_id, ordre_id).await {
+                    Ok(()) => {
+                        info!("Ordre d'achat {} annulé", ordre_id);
 
-    let market =
-        MarketManager::new(
-            pool.clone()
-        );
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelBuy,
+                            ordre_id.to_be_bytes().to_vec(),
+                        ))
+                    }
 
+                    Err(e) => {
+                        error!("Erreur annulation ordre d'achat {} : {}", ordre_id, e);
 
-    match market.annuler_ordre_achat(
-        account_id,
-        ordre_id,
-    ).await {
-
-        Ok(()) => {
-
-            info!(
-                "Ordre d'achat {} annulé",
-                ordre_id
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketCancelBuy,
-                    ordre_id
-                        .to_be_bytes()
-                        .to_vec(),
-                )
-            )
-        }
-
-
-        Err(e) => {
-
-            error!(
-                "Erreur annulation ordre d'achat {} : {}",
-                ordre_id,
-                e
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketCancelBuy,
-                    format!(
-                        "Erreur: {}",
-                        e
-                    )
-                    .into_bytes(),
-                )
-            )
-        }
-    }
-}
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelBuy,
+                            format!("Erreur: {}", e).into_bytes(),
+                        ))
+                    }
+                }
+            }
             PacketType::MarketCancelSell => {
-
-    if packet.payload.len() != 8 {
-
-        return HandlerResult::Response(
-            Packet::new(
-                PacketType::MarketCancelSell,
-                b"MARKET_CANCEL_SELL invalide".to_vec(),
-            )
-        );
-    }
-
-
-    let ordre_id =
-        match Self::read_i64(
-            &packet.payload,
-            0,
-        ) {
-            Some(value) => value,
-
-            None => {
-                return HandlerResult::Response(
-                    Packet::new(
+                if packet.payload.len() != 8 {
+                    return HandlerResult::Response(Packet::new(
                         PacketType::MarketCancelSell,
                         b"MARKET_CANCEL_SELL invalide".to_vec(),
-                    )
-                );
-            }
-        };
+                    ));
+                }
 
+                let ordre_id = match Self::read_i64(&packet.payload, 0) {
+                    Some(value) => value,
 
-    let account_id =
-        match client.account_id() {
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelSell,
+                            b"MARKET_CANCEL_SELL invalide".to_vec(),
+                        ));
+                    }
+                };
 
-            Some(id) => id,
+                let account_id = match client.account_id() {
+                    Some(id) => id,
 
-            None => {
+                    None => {
+                        return HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelSell,
+                            b"Compte non selectionne".to_vec(),
+                        ));
+                    }
+                };
 
-                return HandlerResult::Response(
-                    Packet::new(
-                        PacketType::MarketCancelSell,
-                        b"Compte non selectionne".to_vec(),
-                    )
-                );
-            }
-        };
+                let market = MarketManager::new(pool.clone());
 
+                match market.annuler_ordre_vente(account_id, ordre_id).await {
+                    Ok(()) => {
+                        info!("Ordre de vente {} annulé", ordre_id);
 
-    let market =
-        MarketManager::new(
-            pool.clone()
-        );
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelSell,
+                            ordre_id.to_be_bytes().to_vec(),
+                        ))
+                    }
 
+                    Err(e) => {
+                        error!("Erreur annulation ordre de vente {} : {}", ordre_id, e);
 
-    match market.annuler_ordre_vente(
-        account_id,
-        ordre_id,
-    ).await {
+                        HandlerResult::Response(Packet::new(
+                            PacketType::MarketCancelSell,
+                            format!("Erreur: {}", e).into_bytes(),
+                        ))
+                    }
+                }
+            }
 
-        Ok(()) => {
-
-            info!(
-                "Ordre de vente {} annulé",
-                ordre_id
-                
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketCancelSell,
-                    ordre_id
-                        .to_be_bytes()
-                        .to_vec(),
-                )
-            )
-        }
-
-
-        Err(e) => {
-
-            error!(
-                "Erreur annulation ordre de vente {} : {}",
-                ordre_id,
-                e
-            );
-
-
-            HandlerResult::Response(
-                Packet::new(
-                    PacketType::MarketCancelSell,
-                    format!(
-                        "Erreur: {}",
-                        e
-                    )
-                    .into_bytes(),
-                )
-            )
-        }
-    }
-}
-
             // =================================================
             // Réponses interdites venant du client
             // =================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/handler.rs:1792:
-
             PacketType::LoginResponse
-            | PacketType::SignUpResponse 
-            | PacketType::PlayerState 
+            | PacketType::SignUpResponse
+            | PacketType::PlayerState
             | PacketType::PlayerRemove
-             | PacketType::Session => {
-
+            | PacketType::Session => {
                 error!(
                     "Réponse reçue du client alors qu'elle doit être envoyée par le serveur : {:?}",
                     packet.packet_type
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/mod.rs:1:
-pub mod packet;
 pub mod client;
-pub mod server;
 pub mod handler;
+pub mod packet;
 pub mod parser;
-
-
-
+pub mod server;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/server.rs:1:
-use tokio::net::TcpListener;
-use tokio::task;
-use log::{
-    info,
-    error,
-    debug,
-};
 use crate::database::database_manager::DatabaseManager;
 use crate::network::client::Client;
 use crate::world::world::World;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/server.rs:11:
+use log::{debug, error, info};
+use tokio::net::TcpListener;
+use tokio::task;
 pub struct Server {
     listener: TcpListener,
     database: DatabaseManager,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/server.rs:15:
 }
 
 impl Server {
-    pub async fn new(
-        address: &str,
-        database: DatabaseManager,
-    ) -> std::io::Result<Self>  {
-
+    pub async fn new(address: &str, database: DatabaseManager) -> std::io::Result<Self> {
         let listener = TcpListener::bind(address)
-    .await
-    .inspect_err(|e| error!("Impossible de démarrer le serveur : {}", e))?;
-         let world = World::new();
+            .await
+            .inspect_err(|e| error!("Impossible de démarrer le serveur : {}", e))?;
+        let world = World::new();
 
         Ok(Self {
-        listener,
-        database,
-        world,
-    })
+            listener,
+            database,
+            world,
+        })
     }
 
     pub async fn start(&self) {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/server.rs:36:
-
         debug!("==================================");
         debug!("The Last Signal Server");
         debug!("==================================");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/network/server.rs:40:
 
-        debug!(
-            "Listening on {}",
-            self.listener.local_addr().unwrap()
-        );
+        debug!("Listening on {}", self.listener.local_addr().unwrap());
 
         loop {
-
             match self.listener.accept().await {
-
                 Ok((stream, address)) => {
-    info!("TCP ACCEPT : connexion reçue de {}", address);
+                    info!("TCP ACCEPT : connexion reçue de {}", address);
 
-    let pool = self.database.pool().clone();
-    let world = self.world.clone();
+                    let pool = self.database.pool().clone();
+                    let world = self.world.clone();
 
-    task::spawn(async move {
-        info!("TCP CLIENT : démarrage de Client::run()");
+                    task::spawn(async move {
+                        info!("TCP CLIENT : démarrage de Client::run()");
 
-        let mut client = Client::new(
-            stream,
-            pool,
-            world,
-        );
+                        let mut client = Client::new(stream, pool, world);
 
-        info!("TCP CLIENT : Client::new() terminé");
+                        info!("TCP CLIENT : Client::new() terminé");
 
-        client.run().await;
+                        client.run().await;
 
-        info!("TCP CLIENT : Client::run() terminé");
-    });
-}
+                        info!("TCP CLIENT : Client::run() terminé");
+                    });
+                }
 
                 Err(e) => {
-
-                error!(
-                        "Erreur d'acceptation : {}",
-                        e
-                    );
-
+                    error!("Erreur d'acceptation : {}", e);
                 }
-
             }
-
         }
-
     }
 }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:5:
 const ROTOR_DOMAIN: &[u8] = b"TheLastSignal-Rotor-v1";
 const ROTOR_SIZE: usize = 256;
 
-
 pub struct SplitMix64 {
     state: u64,
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:18:
     }
 
     pub fn next(&mut self) -> u64 {
-        self.state = self
-            .state
-            .wrapping_add(0x9E37_79B9_7F4A_7C15);
+        self.state = self.state.wrapping_add(0x9E37_79B9_7F4A_7C15);
 
         let mut z = self.state;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:27:
-        z = (z ^ (z >> 30))
-            .wrapping_mul(0xBF58_476D_1CE4_E5B9);
+        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
 
-        z = (z ^ (z >> 27))
-            .wrapping_mul(0x94D0_49BB_1331_11EB);
+        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
 
         z ^= z >> 31;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:36:
     }
 }
 
-
-pub fn derive_rotor_seed(
-    communication_key: &[u8],
-    rotor_id: u8,
-) -> Result<u64, &'static str> {
+pub fn derive_rotor_seed(communication_key: &[u8], rotor_id: u8) -> Result<u64, &'static str> {
     if communication_key.len() != COMMUNICATION_KEY_SIZE {
         return Err("Communication_key must be exactly 64 bytes");
     }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:122:
     fn splitmix64_zero_seed() {
         let mut rng = SplitMix64::new(0);
 
-        assert_eq!(
-            rng.next(),
-            0xE220_A839_7B1D_CDAFu64
-        );
+        assert_eq!(rng.next(), 0xE220_A839_7B1D_CDAFu64);
     }
 
     #[test]
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/security/crypto.rs:138:
         assert_ne!(first, second);
     }
     #[test]
-fn derive_rotor_seed_rejects_invalid_key_length() {
-    let key = [0u8; 63];
+    fn derive_rotor_seed_rejects_invalid_key_length() {
+        let key = [0u8; 63];
 
-    assert!(
-        derive_rotor_seed(&key, 1).is_err()
-    );
-}
+        assert!(derive_rotor_seed(&key, 1).is_err());
+    }
 
-#[test]
-fn derive_rotor_seed_rejects_invalid_rotor_id() {
-    let key = [0u8; 64];
+    #[test]
+    fn derive_rotor_seed_rejects_invalid_rotor_id() {
+        let key = [0u8; 64];
 
-    assert!(
-        derive_rotor_seed(&key, 0).is_err()
-    );
+        assert!(derive_rotor_seed(&key, 0).is_err());
 
-    assert!(
-        derive_rotor_seed(&key, 17).is_err()
-    );
-}
+        assert!(derive_rotor_seed(&key, 17).is_err());
+    }
 
-#[test]
-fn derive_rotor_seed_is_deterministic() {
-    let key = [0u8; 64];
+    #[test]
+    fn derive_rotor_seed_is_deterministic() {
+        let key = [0u8; 64];
 
-    let seed1 = derive_rotor_seed(&key, 1).unwrap();
-    let seed2 = derive_rotor_seed(&key, 1).unwrap();
+        let seed1 = derive_rotor_seed(&key, 1).unwrap();
+        let seed2 = derive_rotor_seed(&key, 1).unwrap();
 
-    assert_eq!(seed1, seed2);
-}
+        assert_eq!(seed1, seed2);
+    }
 
-#[test]
-fn derive_rotor_seed_differs_between_rotors() {
-    let key = [0u8; 64];
+    #[test]
+    fn derive_rotor_seed_differs_between_rotors() {
+        let key = [0u8; 64];
 
-    let seed1 = derive_rotor_seed(&key, 1).unwrap();
-    let seed2 = derive_rotor_seed(&key, 2).unwrap();
+        let seed1 = derive_rotor_seed(&key, 1).unwrap();
+        let seed2 = derive_rotor_seed(&key, 2).unwrap();
 
-    assert_ne!(seed1, seed2);
-}
+        assert_ne!(seed1, seed2);
+    }
     #[test]
-fn fisher_yates_contains_all_values() {
-    let rotor = fisher_yates(0);
+    fn fisher_yates_contains_all_values() {
+        let rotor = fisher_yates(0);
 
-    let mut sorted = rotor;
+        let mut sorted = rotor;
 
-    sorted.sort_unstable();
+        sorted.sort_unstable();
 
-    let expected: [u8; ROTOR_SIZE] =
-        core::array::from_fn(|i| i as u8);
+        let expected: [u8; ROTOR_SIZE] = core::array::from_fn(|i| i as u8);
 
-    assert_eq!(sorted, expected);
-}
+        assert_eq!(sorted, expected);
+    }
 
-#[test]
-fn fisher_yates_is_deterministic() {
-    let rotor1 = fisher_yates(123456789);
-    let rotor2 = fisher_yates(123456789);
+    #[test]
+    fn fisher_yates_is_deterministic() {
+        let rotor1 = fisher_yates(123456789);
+        let rotor2 = fisher_yates(123456789);
 
-    assert_eq!(rotor1, rotor2);
-}
+        assert_eq!(rotor1, rotor2);
+    }
 
-#[test]
-fn fisher_yates_changes_with_seed() {
-    let rotor1 = fisher_yates(0);
-    let rotor2 = fisher_yates(1);
+    #[test]
+    fn fisher_yates_changes_with_seed() {
+        let rotor1 = fisher_yates(0);
+        let rotor2 = fisher_yates(1);
 
-    assert_ne!(rotor1, rotor2);
+        assert_ne!(rotor1, rotor2);
+    }
 }
-}
-
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:1:
-use flate2::{
-    write::GzEncoder,
-    Compression,
-};
+use flate2::{Compression, write::GzEncoder};
 use log::info;
 
-
 use std::{
     fs::{self, File},
     io::{self, BufReader},
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:20:
         log_directory: P,
         keep_latest: usize,
     ) -> io::Result<()> {
-
         let log_directory = log_directory.as_ref();
 
         if !log_directory.exists() {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:38:
         });
 
         for file in log_files.into_iter().skip(keep_latest) {
+            let compressed = file.with_extension("log.gz");
 
-            let compressed =
-                file.with_extension("log.gz");
-
             // Déjà compressé
             if compressed.exists() {
                 continue;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:48:
             }
 
-            info!(
-                "[LOGGER] Compression : {}",
-                file.display()
-            );
+            info!("[LOGGER] Compression : {}", file.display());
 
             Self::compress_file(&file, &compressed)?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:60:
         Ok(())
     }
 
-    fn collect_logs(
-        directory: &Path,
-    ) -> io::Result<Vec<PathBuf>> {
-
+    fn collect_logs(directory: &Path) -> io::Result<Vec<PathBuf>> {
         let mut files = Vec::new();
 
         for entry in fs::read_dir(directory)? {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:70:
-
             let entry = entry?;
 
             let path = entry.path();
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:76:
                 continue;
             }
 
-            let Some(name) =
-                path.file_name().and_then(|n| n.to_str())
-            else {
+            let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
                 continue;
             };
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:95:
         Ok(files)
     }
 
-    fn compress_file(
-        input: &Path,
-        output: &Path,
-    ) -> io::Result<()> {
-
+    fn compress_file(input: &Path, output: &Path) -> io::Result<()> {
         let input_file = File::open(input)?;
 
         let output_file = File::create(output)?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:106:
 
-        let mut encoder =
-            GzEncoder::new(
-                output_file,
-                Compression::default(),
-            );
+        let mut encoder = GzEncoder::new(output_file, Compression::default());
 
-        let mut reader =
-            BufReader::new(input_file);
+        let mut reader = BufReader::new(input_file);
 
-        io::copy(
-            &mut reader,
-            &mut encoder,
-        )?;
+        io::copy(&mut reader, &mut encoder)?;
 
         encoder.finish()?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/compressor.rs:123:
         Ok(())
     }
 
-    fn modified(
-        path: &Path,
-    ) -> std::time::SystemTime {
-
+    fn modified(path: &Path) -> std::time::SystemTime {
         fs::metadata(path)
             .and_then(|m| m.modified())
             .unwrap_or(std::time::UNIX_EPOCH)
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:1:
 use flexi_logger::{
-    Cleanup,
-    Criterion,
-    DeferredNow,
-    Duplicate,
-    FileSpec,
-    Logger,
-    Naming,
-    Record,
+    Cleanup, Criterion, DeferredNow, Duplicate, FileSpec, Logger, Naming, Record,
     writers::LogWriter,
 };
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:13:
-
-
 use sqlx::SqlitePool;
 
 use std::io::Write;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:22:
 
 use crate::utils::logger::compressor::LogCompressor;
 
-
 // ============================================================
 // LOG DESTINÉ À SQLITE
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:34:
     message: String,
 }
 
-
 // ============================================================
 // COMMANDES DU WORKER DATABASE
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:44:
     Log(DatabaseLog),
 }
 
-
 // ============================================================
 // WRITER SQLITE
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:54:
 }
 
 impl DatabaseWriter {
-    fn new(
-        sender: mpsc::UnboundedSender<DatabaseCommand>,
-    ) -> Self {
+    fn new(sender: mpsc::UnboundedSender<DatabaseCommand>) -> Self {
         Self { sender }
     }
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:63:
 
 impl LogWriter for DatabaseWriter {
-
-    fn write(
-        &self,
-        _now: &mut DeferredNow,
-        record: &Record<'_>,
-    ) -> std::io::Result<()> {
-
+    fn write(&self, _now: &mut DeferredNow, record: &Record<'_>) -> std::io::Result<()> {
         let module = record
             .module_path()
             .unwrap_or_else(|| record.target())
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:83:
         // On envoie le log au worker SQLite.
         //
         // Le logger ne bloque donc pas en attendant SQLite.
-        let _ = self.sender.send(
-            DatabaseCommand::Log(log)
-        );
+        let _ = self.sender.send(DatabaseCommand::Log(log));
 
         Ok(())
     }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:95:
     }
 }
 
-
 // ============================================================
 // FORMAT DU FICHIER LOG
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:105:
     now: &mut DeferredNow,
     record: &Record<'_>,
 ) -> std::io::Result<()> {
-
     let file = record
         .file()
         .and_then(|f| Path::new(f).file_name())
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:123:
     )
 }
 
-
 // ============================================================
 // LOGGER
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:131:
 pub struct ServerLogger;
 
 impl ServerLogger {
-
     // ========================================================
     // INITIALISATION
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:138:
 
     pub fn init() {
-
         let log_dir = PathBuf::from("../logs");
 
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:144:
         // Canal entre flexi_logger et le worker SQLite
         // ----------------------------------------------------
 
-        let (sender, mut receiver) =
-            mpsc::unbounded_channel::<DatabaseCommand>();
+        let (sender, mut receiver) = mpsc::unbounded_channel::<DatabaseCommand>();
 
-
         // ----------------------------------------------------
         // Worker SQLite
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:154:
 
         tokio::spawn(async move {
-
             let mut pool: Option<SqlitePool> = None;
 
             // Logs produits avant que la DB soit disponible.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:165:
             // mémoire infinie si la DB ne devient jamais disponible.
             const MAX_PENDING_LOGS: usize = 1000;
 
-
             while let Some(command) = receiver.recv().await {
-
                 match command {
-
                     // ----------------------------------------
                     // Base de données disponible
                     // ----------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:176:
-
                     DatabaseCommand::SetPool(new_pool) => {
-
                         pool = Some(new_pool);
 
-
                         // ------------------------------------
                         // Écriture des logs en attente
                         // ------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:185:
 
                         if let Some(pool) = &pool {
-
                             for log in pending_logs.drain(..) {
-
-                                if let Err(error) =
-                                    Self::insert_log(
-                                        pool,
-                                        &log,
-                                    )
-                                    .await
-                                {
-                                    eprintln!(
-                                        "Erreur écriture log SQLite : {}",
-                                        error
-                                    );
+                                if let Err(error) = Self::insert_log(pool, &log).await {
+                                    eprintln!("Erreur écriture log SQLite : {}", error);
                                 }
                             }
                         }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:204:
                     }
 
-
                     // ----------------------------------------
                     // Nouveau log
                     // ----------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:210:
-
                     DatabaseCommand::Log(log) => {
-
                         match &pool {
-
                             // DB disponible
                             Some(pool) => {
-
-                                if let Err(error) =
-                                    Self::insert_log(
-                                        pool,
-                                        &log,
-                                    )
-                                    .await
-                                {
-                                    eprintln!(
-                                        "Erreur écriture log SQLite : {}",
-                                        error
-                                    );
+                                if let Err(error) = Self::insert_log(pool, &log).await {
+                                    eprintln!("Erreur écriture log SQLite : {}", error);
                                 }
                             }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:232:
-
                             // DB pas encore disponible
                             None => {
-
-                                if pending_logs.len()
-                                    >= MAX_PENDING_LOGS
-                                {
+                                if pending_logs.len() >= MAX_PENDING_LOGS {
                                     // On supprime le plus ancien
                                     // pour éviter une croissance
                                     // infinie.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:250:
             }
         });
 
-
         // ----------------------------------------------------
         // Writer SQLite
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:257:
 
-        let database_writer =
-            DatabaseWriter::new(sender.clone());
+        let database_writer = DatabaseWriter::new(sender.clone());
 
-
         // ----------------------------------------------------
         // Flexi logger
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:265:
 
         Logger::try_with_str("trace,sqlx=warn")
             .unwrap()
-
             // Fichier + SQLite
             .log_to_file_and_writer(
                 FileSpec::default()
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:272:
                     .directory(log_dir)
                     .basename("the_last_signal"),
-
                 Box::new(database_writer),
             )
-
             // stdout
             .duplicate_to_stdout(Duplicate::All)
-
             // Format du fichier
             .format(log_format)
-
             // Rotation à 10 MB
             .rotate(
                 Criterion::Size(10_000_000),
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:287:
                 Naming::Numbers,
                 Cleanup::KeepLogFiles(100),
             )
-
             // Ajouter aux fichiers existants
             .append()
-
             // Démarrage
             .start()
             .unwrap();
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:297:
 
-
         // ----------------------------------------------------
         // Compression
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:302:
 
         Self::compress();
 
-
         // ----------------------------------------------------
         // Stockage du sender
         // ----------------------------------------------------
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:314:
         DatabaseSender::set(sender);
     }
 
-
     // ========================================================
     // CONNEXION À LA DATABASE
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:321:
 
-    pub fn set_database(
-        pool: SqlitePool,
-    ) {
-
-        if let Some(sender) =
-            DatabaseSender::get()
-        {
-            let _ = sender.send(
-                DatabaseCommand::SetPool(pool)
-            );
-        }
-        else {
-
+    pub fn set_database(pool: SqlitePool) {
+        if let Some(sender) = DatabaseSender::get() {
+            let _ = sender.send(DatabaseCommand::SetPool(pool));
+        } else {
             eprintln!(
                 "Impossible de connecter le logger à SQLite : \
                  ServerLogger::init() n'a pas été appelé."
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:339:
         }
     }
 
-
     // ========================================================
     // INSERTION SQLITE
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:346:
 
-    async fn insert_log(
-        pool: &SqlitePool,
-        log: &DatabaseLog,
-    ) -> Result<(), sqlx::Error> {
-
+    async fn insert_log(pool: &SqlitePool, log: &DatabaseLog) -> Result<(), sqlx::Error> {
         sqlx::query(
             r#"
             INSERT INTO logs (
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:368:
         Ok(())
     }
 
-
     // ========================================================
     // COMPRESSION
     // ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:375:
 
     pub fn compress() {
-
-        if let Err(error) =
-            LogCompressor::compress_old_logs(
-                "logs",
-                10,
-            )
-        {
-            eprintln!(
-                "Compression impossible : {}",
-                error
-            );
+        if let Err(error) = LogCompressor::compress_old_logs("logs", 10) {
+            eprintln!("Compression impossible : {}", error);
         }
     }
 }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:391:
 
-
 // ============================================================
 // STOCKAGE GLOBAL DU SENDER
 // ============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:396:
 
 struct DatabaseSender;
 
-static SENDER:
-    std::sync::OnceLock<
-        Arc<RwLock<
-            Option<mpsc::UnboundedSender<DatabaseCommand>>
-        >>
-    >
-    = std::sync::OnceLock::new();
+static SENDER: std::sync::OnceLock<Arc<RwLock<Option<mpsc::UnboundedSender<DatabaseCommand>>>>> =
+    std::sync::OnceLock::new();
 
-
 impl DatabaseSender {
+    fn set(sender: mpsc::UnboundedSender<DatabaseCommand>) {
+        let storage = Arc::new(RwLock::new(Some(sender)));
 
-    fn set(
-        sender: mpsc::UnboundedSender<DatabaseCommand>,
-    ) {
-
-        let storage =
-            Arc::new(
-                RwLock::new(Some(sender))
-            );
-
         let _ = SENDER.set(storage);
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/logger.rs:422:
-
-    fn get()
-        -> Option<
-            mpsc::UnboundedSender<DatabaseCommand>
-        >
-    {
+    fn get() -> Option<mpsc::UnboundedSender<DatabaseCommand>> {
         SENDER
             .get()
-            .and_then(|storage| {
-                storage
-                    .read()
-                    .ok()
-                    .and_then(|guard| guard.clone())
-            })
+            .and_then(|storage| storage.read().ok().and_then(|guard| guard.clone()))
     }
-            }
+}
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/logger/mod.rs:1:
-pub mod logger;
-pub mod context;
 pub mod compressor;
+pub mod context;
+pub mod logger;
 pub mod macros;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/mod.rs:1:
 pub mod logger;
-pub mod vault;
 pub mod special_account_creator;
+pub mod vault;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/special_account_creator.rs:1:
-use uuid::Uuid;
 use sqlx::SqlitePool;
+use uuid::Uuid;
 pub async fn create_account(
     pool: &SqlitePool,
     email: &str,
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/special_account_creator.rs:85:
     .bind(&user_id)
     .bind(account_name)
     .bind(role_id)
-    .fetch_one(&mut *tx) 
+    .fetch_one(&mut *tx)
     .await?;
     let max_balance = i64::MAX;
-    sqlx::query( 
+    sqlx::query(
         r#" INSERT INTO wallets ( 
         account_id,
         balance
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/special_account_creator.rs:95:
         ) 
         VALUES (?,?) 
-        "#, ) 
-        .bind(account_id)
-        .bind(max_balance)
-        .execute(&mut *tx) 
-        .await?;
+        "#,
+    )
+    .bind(account_id)
+    .bind(max_balance)
+    .execute(&mut *tx)
+    .await?;
     if let Some(status) = status {
         sqlx::query(
             r#"
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/special_account_creator.rs:119:
 
     tx.commit().await?;
 
-    Ok(())}
+    Ok(())
+}
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/utils/vault.rs:8:
         Err(_) => fs::read_to_string("../security/master.key")?,
     };
 
-    let cipher = Fernet::new(key.trim())
-        .ok_or("Clé Fernet invalide")?;
+    let cipher = Fernet::new(key.trim()).ok_or("Clé Fernet invalide")?;
 
     let encrypted = fs::read_to_string("../security/vault.enc")?;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/mod.rs:1:
 pub mod world;
+
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:2:
 use std::sync::Arc;
 
 use log::{error, info};
-use tokio::sync::{broadcast, Mutex};
+use tokio::sync::{Mutex, broadcast};
 use uuid::Uuid;
 
 use crate::network::packet::{Packet, PacketType};
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:56:
     // POSITIONS
     // =============================================================
 
-    pub async fn set_position(
-        &self,
-        player_id: Uuid,
-        position: Position,
-    ) {
+    pub async fn set_position(&self, player_id: Uuid, position: Position) {
         let mut positions = self.positions.lock().await;
 
-        positions.insert(
-            player_id,
-            position,
-        );
+        positions.insert(player_id, position);
 
         info!(
             "WORLD: position enregistrée | \
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:73:
              x={} y={} z={}",
-            
-            position.x,
-            position.y,
-            position.z
+            position.x, position.y, position.z
         );
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:81:
-    pub async fn remove_player(
-        &self,
-        player_id: Uuid,
-    ) {
+    pub async fn remove_player(&self, player_id: Uuid) {
         let mut positions = self.positions.lock().await;
 
         if positions.remove(&player_id).is_some() {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:88:
-            info!(
-                "WORLD: joueur supprimé"
-            );
+            info!("WORLD: joueur supprimé");
         }
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:94:
-    pub async fn get_position(
-        &self,
-        player_id: Uuid,
-    ) -> Option<Position> {
+    pub async fn get_position(&self, player_id: Uuid) -> Option<Position> {
         let positions = self.positions.lock().await;
 
-        positions
-            .get(&player_id)
-            .copied()
+        positions.get(&player_id).copied()
     }
 
-    pub async fn snapshot(
-        &self,
-    ) -> Vec<(Uuid, Position)> {
+    pub async fn snapshot(&self) -> Vec<(Uuid, Position)> {
         let positions = self.positions.lock().await;
 
         positions
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:111:
             .iter()
-            .map(|(id, position)| {
-                (*id, *position)
-            })
+            .map(|(id, position)| (*id, *position))
             .collect()
     }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:119:
     // PACKET PLAYER_STATE
     // =============================================================
 
-    pub fn player_state_packet(
-        player_id: Uuid,
-        position: Position,
-    ) -> Packet {
+    pub fn player_state_packet(player_id: Uuid, position: Position) -> Packet {
         let mut payload = Vec::with_capacity(28);
 
         // UUID = 16 octets
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:129:
-        payload.extend_from_slice(
-            player_id.as_bytes()
-        );
+        payload.extend_from_slice(player_id.as_bytes());
 
         // x = 4 octets
-        payload.extend_from_slice(
-            &position.x.to_be_bytes()
-        );
+        payload.extend_from_slice(&position.x.to_be_bytes());
 
         // y = 4 octets
-        payload.extend_from_slice(
-            &position.y.to_be_bytes()
-        );
+        payload.extend_from_slice(&position.y.to_be_bytes());
 
         // z = 4 octets
-        payload.extend_from_slice(
-            &position.z.to_be_bytes()
-        );
+        payload.extend_from_slice(&position.z.to_be_bytes());
 
-        debug_assert_eq!(
-            payload.len(),
-            28
-        );
+        debug_assert_eq!(payload.len(), 28);
 
-        Packet::new(
-            PacketType::PlayerState,
-            payload,
-        )
+        Packet::new(PacketType::PlayerState, payload)
     }
 
     // =============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:160:
     // BROADCAST PLAYER_STATE
     // =============================================================
 
-    pub fn broadcast_player_state(
-        &self,
-        player_id: Uuid,
-        position: Position,
-    ) {
-        let packet = Self::player_state_packet(
-            player_id,
-            position,
-        );
+    pub fn broadcast_player_state(&self, player_id: Uuid, position: Position) {
+        let packet = Self::player_state_packet(player_id, position);
 
         match self.tx.send(packet) {
             Ok(receiver_count) => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:176:
                     "WORLD: PLAYER_STATE broadcasté | \
                       x={} y={} z={} | \
                      récepteurs={}",
-                    
-                    position.x,
-                    position.y,
-                    position.z,
-                    receiver_count
+                    position.x, position.y, position.z, receiver_count
                 );
             }
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:188:
                 error!(
                     "WORLD: échec du broadcast PLAYER_STATE | \
                       erreur={}",
-                    
                     error
                 );
             }
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:199:
     // PACKET PLAYER_REMOVE
     // =============================================================
 
-    pub fn player_remove_packet(
-        player_id: Uuid,
-    ) -> Packet {
-        Packet::new(
-            PacketType::PlayerRemove,
-            player_id.as_bytes().to_vec(),
-        )
+    pub fn player_remove_packet(player_id: Uuid) -> Packet {
+        Packet::new(PacketType::PlayerRemove, player_id.as_bytes().to_vec())
     }
 
     // =============================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/world/world.rs:212:
     // BROADCAST PLAYER_REMOVE
     // =============================================================
 
-    pub fn broadcast_player_remove(
-        &self,
-        player_id: Uuid,
-    ) {
-        let packet = Self::player_remove_packet(
-            player_id
-        );
+    pub fn broadcast_player_remove(&self, player_id: Uuid) {
+        let packet = Self::player_remove_packet(player_id);
 
         match self.tx.send(packet) {
             Ok(receiver_count) => {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:1:
-use the_last_signal_server::database::{
-    database_manager::DatabaseManager,
-    migrations,
-};
 use log::info;
 use sqlx::Row;
+use the_last_signal_server::database::{database_manager::DatabaseManager, migrations};
 
+use the_last_signal_server::gameplay::{stuff_manager::Inventaire, tresor::Tresor};
 use the_last_signal_server::network::server::Server;
-use the_last_signal_server::gameplay::{
-    stuff_manager::Inventaire,
-    tresor::Tresor,
-};
 
 use the_last_signal_server::utils::logger::logger::ServerLogger;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:16:
 const NOMBRE_REPETITIONS: u32 = 100;
 const NOMBRE_CONFIGURATIONS: u32 = 12 * 2 * 2; // niveaux × admin × militaire
 
-
 #[allow(dead_code)]
 #[tokio::main]
 async fn main() -> Result<(), Box<dyn std::error::Error>> {
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:25:
     let database_url = std::env::var("DATABASE_URL")?;
     let database_path = std::env::var("DATABASE_PATH")?;
 
-    let database =
-        DatabaseManager::new(&database_path, &database_url)
-            .await?;
+    let database = DatabaseManager::new(&database_path, &database_url).await?;
 
     database.ping().await?;
     migrations::run(&database.pool()).await?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:36:
 
     ServerLogger::set_database(database.pool().clone());
 
-    let server =
-        Server::new("127.0.0.1:5000", database)
-            .await?;
+    let server = Server::new("127.0.0.1:5000", database).await?;
 
     server.start().await;
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:45:
     Ok(())
 }
 
-
 #[cfg(test)]
 mod tests {
     use super::*;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:58:
         let database_url = std::env::var("DATABASE_URL")?;
         let database_path = std::env::var("DATABASE_PATH")?;
 
-        let database =
-            DatabaseManager::new(&database_path, &database_url)
-                .await?;
+        let database = DatabaseManager::new(&database_path, &database_url).await?;
 
         database.ping().await?;
         migrations::run(&database.pool()).await?;
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:81:
          * 1.9
          * 2.0
          */
-        let coefficients: Vec<f64> = (10..=20)
-            .map(|i| f64::from(i) / 10.0)
-            .collect();
+        let coefficients: Vec<f64> = (10..=20).map(|i| f64::from(i) / 10.0).collect();
 
         println!();
         println!("========================================");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:97:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:128:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:157:
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
 
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:186:
                 for niveau in 1..=12 {
                     for is_admin in [false, true] {
                         for is_militaire in [false, true] {
-
                             let objets = tresor
                                 .ouvrir(
                                     database.pool(),
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:207:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:291:
             /*
              * Nombre de livres distincts selon leur stack_key.
              */
-            let mut livres_uniques =
-                std::collections::HashSet::<String>::new();
+            let mut livres_uniques = std::collections::HashSet::<String>::new();
 
             /*
              * Quantité totale de livres.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:301:
              * Il faut donc éviter de compter plusieurs fois
              * le même stuff_id.
              */
-            let mut livres_comptes =
-                std::collections::HashSet::<i64>::new();
+            let mut livres_comptes = std::collections::HashSet::<i64>::new();
 
             /*
              * Pour afficher les combinaisons réellement générées.
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:309:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:323:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:333:
                  */
                 if livres_comptes.insert(stuff_id) {
                     if (1..=6).contains(&book_level) {
-                        livres_par_niveau[(book_level - 1) as usize]
-                            += quantity;
+                        livres_par_niveau[(book_level - 1) as usize] += quantity;
                     }
 
                     livres_uniques.insert(stack_key.clone());
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:345:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:364:
              * Quantité totale de livres.
              */
-            let total_livres: i64 =
-                livres_par_niveau.iter().sum();
+            let total_livres: i64 = livres_par_niveau.iter().sum();
 
             /*
              * ========================================================
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:374:
 
             println!();
             println!("----------------------------------------");
-            println!(
-                "RÉSULTATS — coefficient {coefficient:.1}"
-            );
+            println!("RÉSULTATS — coefficient {coefficient:.1}");
             println!("----------------------------------------");
 
             println!("Ouvertures : {ouvertures_effectuees}");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:383:
             println!("Livres générés : {total_livres}");
-            println!(
-                "Combinaisons uniques : {}",
-                livres_uniques.len()
-            );
+            println!("Combinaisons uniques : {}", livres_uniques.len());
 
             println!();
             println!("Répartition des niveaux :");
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:391:
 
             for niveau in 1..=6 {
-                let nombre =
-                    livres_par_niveau[(niveau - 1) as usize];
+                let nombre = livres_par_niveau[(niveau - 1) as usize];
 
                 let pourcentage = if total_livres > 0 {
                     nombre as f64 * 100.0 / total_livres as f64
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:420:
 
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:443:
 
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:466:
             }
 
             println!();
-            println!(
-                "✓ Rapport du coefficient {coefficient:.1} terminé."
-            );
+            println!("✓ Rapport du coefficient {coefficient:.1} terminé.");
         }
 
         println!();
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:475:
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
Diff in /home/runner/work/The-last-signal-/The-last-signal-/server_rust/src/main.rs:489:
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
   Compiling libc v0.2.190
   Compiling stable_deref_trait v1.2.1
   Compiling zerofrom v0.1.8
   Compiling pin-project-lite v0.2.17
   Compiling typenum v1.20.1
   Compiling yoke v0.8.3
   Compiling writeable v0.6.4
   Compiling zerovec v0.11.8
   Compiling memchr v2.8.3
   Compiling tinystr v0.8.4
   Compiling futures-core v0.3.34
   Compiling litemap v0.8.3
   Compiling smallvec v1.16.3
   Compiling potential_utf v0.1.6
   Compiling zerotrie v0.2.5
   Compiling icu_locale_core v2.3.0
   Compiling utf8_iter v1.0.4
   Compiling scopeguard v1.2.0
   Compiling icu_collections v2.3.0
   Compiling lock_api v0.4.14
   Compiling icu_properties_data v2.3.0
   Compiling icu_normalizer_data v2.3.0
   Compiling mio v1.2.4
   Compiling socket2 v0.6.5
   Compiling bytes v1.12.1
   Compiling futures-sink v0.3.34
   Compiling serde_core v1.0.229
   Compiling equivalent v1.0.3
   Compiling once_cell v1.21.4
   Compiling icu_provider v2.3.1
   Compiling icu_normalizer v2.3.0
   Compiling icu_properties v2.3.0
   Compiling rand_core v0.10.1
   Compiling tracing-core v0.1.36
   Compiling generic-array v0.14.9
   Compiling parking_lot_core v0.9.12
   Compiling futures-task v0.3.34
   Compiling foldhash v0.2.0
   Compiling futures-io v0.3.34
   Compiling idna_adapter v1.2.2
   Compiling cpufeatures v0.2.17
   Compiling percent-encoding v2.3.2
   Compiling allocator-api2 v0.2.21
   Compiling slab v0.4.12
   Compiling form_urlencoded v1.2.2
   Compiling futures-util v0.3.34
   Compiling hashbrown v0.16.1
   Compiling idna v1.1.0
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
   Compiling crossbeam-queue v0.3.14
   Compiling serde_json v1.0.154
   Compiling crc v3.4.0
   Compiling indexmap v2.14.2
   Compiling futures-intrusive v0.5.0
   Compiling either v1.19.0
   Compiling hashlink v0.11.1
   Compiling url v2.5.8
   Compiling block-buffer v0.10.4
   Compiling crypto-common v0.1.6
   Compiling cmov v0.5.4
   Compiling ctutils v0.4.3
   Compiling digest v0.10.7
   Compiling tokio v1.53.3
   Compiling spin v0.9.9
   Compiling hybrid-array v0.4.15
   Compiling tracing v0.1.44
   Compiling flume v0.12.0
   Compiling sha2 v0.10.9
   Compiling futures-executor v0.3.34
   Compiling atoi v2.0.0
   Compiling futures-channel v0.3.34
   Compiling log v0.4.34
   Compiling block-buffer v0.12.1
   Compiling crypto-common v0.2.2
   Compiling thiserror v2.0.21
   Compiling base64 v0.22.1
   Compiling cpufeatures v0.3.1
   Compiling const-oid v0.10.2
   Compiling digest v0.11.3
   Compiling uuid v1.28.0
   Compiling aho-corasick v1.1.5
   Compiling regex-syntax v0.8.11
   Compiling tokio-stream v0.1.19
   Compiling sqlx-core v0.9.0
   Compiling foreign-types-shared v0.1.1
   Compiling base64ct v1.8.3
   Compiling phc v0.6.1
   Compiling foreign-types v0.3.2
   Compiling regex-automata v0.4.18
   Compiling sqlx-sqlite v0.9.0
   Compiling libsqlite3-sys v0.37.0
   Compiling sqlx-macros-core v0.9.0
   Compiling openssl-sys v0.9.117
   Compiling iana-time-zone v0.1.65
   Compiling bitflags v2.13.2
   Compiling simd-adler32 v0.3.10
   Compiling adler2 v2.0.1
   Compiling openssl v0.10.81
   Compiling miniz_oxide v0.9.1
   Compiling chrono v0.4.45
   Compiling sqlx-macros v0.9.0
   Compiling zeroize v1.9.1
   Compiling regex v1.13.1
   Compiling password-hash v0.6.1
   Compiling crc32fast v1.5.2
   Compiling blake2 v0.11.0
   Compiling chacha20 v0.10.2
   Compiling getrandom v0.2.17
   Compiling byteorder v1.5.0
   Compiling nu-ansi-term v0.50.3
   Compiling rand v0.10.3
   Compiling flexi_logger v0.31.10
   Compiling sqlx v0.9.0
   Compiling fernet v0.2.2
   Compiling argon2 v0.6.0
   Compiling flate2 v1.1.10
   Compiling sha2 v0.11.1
   Compiling the-last-signal-server v1.0.14 (/home/runner/work/The-last-signal-/The-last-signal-/server_rust)
warning: unused imports: `debug` and `info`
 --> src/gameplay/tresor.rs:5:11
  |
5 | use log::{debug, error, info};
  |           ^^^^^         ^^^^
  |
  = note: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default

warning: fields `user_id` and `password_hash` are never read
  --> src/network/handler.rs:41:5
   |
40 | pub struct User {
   |            ---- fields in this struct
41 |     user_id: String,
   |     ^^^^^^^
42 |     password_hash: String,
   |     ^^^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: constant `PP` is never used
 --> src/gameplay/tresor.rs:9:7
  |
9 | const PP: u32 = PO * 10;
  |       ^^

warning: `the-last-signal-server` (lib) generated 3 warnings (run `cargo fix --lib -p the-last-signal-server` to apply 1 suggestion)
warning: unused import: `sqlx::Row`
 --> src/main.rs:6:5
  |
6 | use sqlx::Row;
  |     ^^^^^^^^^
  |
  = note: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default

warning: unused imports: `stuff_manager::Inventaire` and `tresor::Tresor`
  --> src/main.rs:10:5
   |
10 |     stuff_manager::Inventaire,
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^
11 |     tresor::Tresor,
   |     ^^^^^^^^^^^^^^

warning: constant `NOMBRE_REPETITIONS` is never used
  --> src/main.rs:16:7
   |
16 | const NOMBRE_REPETITIONS: u32 = 100;
   |       ^^^^^^^^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: constant `NOMBRE_CONFIGURATIONS` is never used
  --> src/main.rs:17:7
   |
17 | const NOMBRE_CONFIGURATIONS: u32 = 12 * 2 * 2; // niveaux × admin × militaire
   |       ^^^^^^^^^^^^^^^^^^^^^

warning: `the-last-signal-server` (bin "the-last-signal-server") generated 4 warnings (run `cargo fix --bin "the-last-signal-server" -p the-last-signal-server` to apply 2 suggestions)
warning: `the-last-signal-server` (lib test) generated 3 warnings (3 duplicates)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 17.67s
     Running unittests src/lib.rs (server_rust/target/debug/deps/the_last_signal_server-63e7f2f90acc9500)

running 74 tests
test network::packet::tests::test_encode_ban_empty_reason ... ok
test network::packet::tests::test_encode_ban_multibyte_utf8 ... ok
test network::packet::tests::test_encode_ban_none_vs_empty_expiration ... ok
test network::packet::tests::test_encode_ban_permanent ... ok
test network::packet::tests::test_encode_ban_reason_with_nul_documents_delimiter_collision ... ok
test network::packet::tests::test_encode_ban_temporary ... ok
test network::packet::tests::test_packet_clone ... ok
test network::packet::tests::test_packet_new_empty_payload ... ok
test network::packet::tests::test_packet_new_non_empty_payload ... ok
test network::packet::tests::test_packet_parse_body_empty_payload ... ok
test network::packet::tests::test_packet_parse_body_too_short ... ok
test network::packet::tests::test_packet_parse_body_unknown_type ... ok
test network::packet::tests::test_packet_parse_body_with_payload ... ok
test network::packet::tests::test_packet_type_from_u16_all_valid ... ok
test network::packet::tests::test_parse_body_all_supported_packet_types_protocol_lock ... ok
test network::packet::tests::test_packet_type_from_u16_invalid_values ... ok
test network::packet::tests::test_parse_body_realistic_move_payload ... ok
test network::packet::tests::test_parse_body_realistic_player_state_payload ... ok
test network::packet::tests::test_parse_body_realistic_session_payload ... ok
test network::packet::tests::test_parse_body_unknown_type_boundary_cases ... ok
test network::packet::tests::test_receive_packet_oversized_header_rejected_without_waiting ... ok
test network::packet::tests::test_receive_packet_exceeds_max_size ... ok
test network::packet::tests::test_receive_packet_size_zero_fails ... ok
test network::packet::tests::test_receive_packet_size_one_fails ... ok
test network::packet::tests::test_receive_packet_truncated_header ... ok
test network::packet::tests::test_receive_packet_truncated_payload ... ok
test network::packet::tests::test_receive_packet_unknown_packet_type ... ok
test network::packet::tests::test_send_and_receive_empty_payload_roundtrip ... ok
test network::packet::tests::test_send_and_receive_roundtrip ... ok
test network::packet::tests::test_send_packet_exceeds_max_size ... ok
test network::parser::tests::test_login_payload_empty ... ok
test network::parser::tests::test_login_payload_empty_strings ... ok
test network::parser::tests::test_login_payload_invalid_email_utf8 ... ok
test network::parser::tests::test_login_payload_invalid_password_utf8 ... ok
test network::parser::tests::test_login_payload_large_u16_length_incomplet ... ok
test network::packet::tests::test_send_packet_wire_format_inspection ... ok
test network::parser::tests::test_login_payload_missing_password_length ... ok
test network::parser::tests::test_login_payload_trailing_bytes_accepted ... ok
test network::parser::tests::test_login_payload_truncated_email_body ... ok
test network::parser::tests::test_login_payload_truncated_email_length ... ok
test network::parser::tests::test_login_payload_truncated_password_body ... ok
test network::parser::tests::test_login_payload_truncated_password_length ... ok
test network::parser::tests::test_parse_credentials_char_count_prefix_misaligns_next_field ... ok
test network::parser::tests::test_parse_credentials_long_strings ... ok
test network::parser::tests::test_login_payload_valid ... ok
test network::parser::tests::test_parse_credentials_mid_codepoint_slice_rejected ... ok
test network::parser::tests::test_parse_credentials_multibyte_utf8_success ... ok
test network::parser::tests::test_parse_credentials_preserves_whitespace ... ok
test network::parser::tests::test_parse_credentials_special_ascii_symbols ... ok
test network::parser::tests::test_signup_payload_empty ... ok
test network::parser::tests::test_signup_payload_invalid_email_utf8 ... ok
test network::parser::tests::test_signup_payload_invalid_password_utf8 ... ok
test network::parser::tests::test_signup_payload_empty_strings ... ok
test network::parser::tests::test_signup_payload_large_u16_length_incomplet ... ok
test network::parser::tests::test_signup_payload_trailing_bytes_accepted ... ok
test network::parser::tests::test_signup_payload_missing_password_length ... ok
test network::parser::tests::test_signup_payload_truncated_email_body ... ok
test network::parser::tests::test_signup_payload_truncated_email_length ... ok
test network::parser::tests::test_signup_payload_truncated_password_body ... ok
test network::parser::tests::test_signup_payload_truncated_password_length ... ok
test network::parser::tests::test_signup_payload_valid ... ok
test security::crypto::tests::derive_rotor_seed_differs_between_rotors ... ok
test security::crypto::tests::derive_rotor_seed_is_deterministic ... ok
test security::crypto::tests::derive_rotor_seed_rejects_invalid_key_length ... ok
test security::crypto::tests::derive_rotor_seed_rejects_invalid_rotor_id ... ok
test security::crypto::tests::fisher_yates_changes_with_seed ... ok
test security::crypto::tests::splitmix64_different_seed_different_sequence ... ok
test security::crypto::tests::fisher_yates_is_deterministic ... ok
test security::crypto::tests::fisher_yates_contains_all_values ... ok
test security::crypto::tests::splitmix64_max_seed ... ok
test security::crypto::tests::splitmix64_same_seed_same_sequence ... ok
test security::crypto::tests::splitmix64_state_changes ... ok
test security::crypto::tests::splitmix64_zero_seed ... ok
test network::packet::tests::test_send_and_receive_exact_max_allowed_boundary ... ok

test result: ok. 74 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.10s

     Running unittests src/main.rs (server_rust/target/debug/deps/the_last_signal_server-b161157131b15abc)

running 1 test
test tests::test_tresor ... ignored

test result: ok. 0 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/integration_test.rs (server_rust/target/debug/deps/integration_test-4acc3e79e9d6f349)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests the_last_signal_server

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

