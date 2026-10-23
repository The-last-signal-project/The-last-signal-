
use sqlx::{Row, SqlitePool};
use uuid::Uuid;

use crate::auth::password::hash_password;

/// Informations utilisateur pouvant être renvoyées à l'application.
#[derive(Debug, Clone)]
pub struct UserSummary {
    pub user_id: String,
    pub email: String,
    pub status: String,
    pub last_login: Option<String>,
}

/// Informations internes nécessaires à l'authentification.
/// Ne jamais envoyer password_hash au client.
#[derive(Debug, Clone)]
pub struct UserCredentials {
    pub user_id: String,
    pub email: String,
    pub password_hash: String,
    /// Pseudo affiché à la place de l'e-mail (absent pour les anciens comptes).
    pub pseudo: Option<String>,
}

pub struct UserManager {
    pool: SqlitePool,
}

impl UserManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Vérifie un pseudo : 3 à 20 caractères, lettres / chiffres / `_` / `-`.
    pub fn validate_pseudo(pseudo: &str) -> Result<String, String> {
        let pseudo = pseudo.trim();
        let len = pseudo.chars().count();

        if !(3..=20).contains(&len) {
            return Err("Pseudo invalide : 3 à 20 caractères.".into());
        }

        if !pseudo
            .chars()
            .all(|c| c.is_alphanumeric() || c == '_' || c == '-')
        {
            return Err("Pseudo invalide : lettres, chiffres, _ et - uniquement.".into());
        }

        Ok(pseudo.to_string())
    }

    
    

    /// Au démarrage, plus aucun client n'est connecté : remet à DISCONNECTED les comptes
    /// restés CONNECTED après un arrêt brutal (sinon « Ce compte est déjà connecté » à vie).
    pub async fn reset_connected_users(pool: &SqlitePool) -> Result<u64, String> {
        let result = sqlx::query(
            "UPDATE users SET status = 'DISCONNECTED' WHERE status = 'CONNECTED'",
        )
        .execute(pool)
        .await
        .map_err(|e| format!("Impossible de réinitialiser les statuts : {e}"))?;

        Ok(result.rows_affected())
    }

    /// Inscrit un utilisateur sans pseudo (conservé pour compatibilité).
    pub async fn create_user(
        &self,
        email: &str,
        password: &str,
    ) -> Result<UserSummary, String> {
        self.create_user_inner(email, password, None).await
    }

    /// Inscrit un utilisateur avec son pseudo.
    /// Le mot de passe est haché avant d'être stocké.
    pub async fn create_user_with_pseudo(
        &self,
        email: &str,
        password: &str,
        pseudo: &str,
    ) -> Result<UserSummary, String> {
        let pseudo = Self::validate_pseudo(pseudo)?;
        self.create_user_inner(email, password, Some(pseudo)).await
    }

    async fn create_user_inner(
        &self,
        email: &str,
        password: &str,
        pseudo: Option<String>,
    ) -> Result<UserSummary, String> {
        let email = email.trim().to_lowercase();

        if email.is_empty() || !email.contains('@') {
            return Err("Adresse e-mail invalide.".into());
        }

        if password.len() < 8 {
            return Err(
                "Le mot de passe doit contenir au moins 8 caractères.".into(),
            );
        }

        // Argon2 est volontairement lent : on le sort du thread asynchrone pour ne pas
        // bloquer le serveur (et les autres joueurs) pendant l'inscription.
        let password_owned = password.to_string();
        let password_hash =
            tokio::task::spawn_blocking(move || hash_password(&password_owned))
                .await
                .map_err(|e| format!("Erreur lors du hash du mot de passe : {e}"))??;

        let user_id = Uuid::new_v4().to_string();

        sqlx::query(
    r#"
    INSERT INTO users (user_id, email, password_hash, status, pseudo)
    VALUES (?, ?, ?, 'DISCONNECTED', ?)
    "#
)
.bind(&user_id)
.bind(&email)
.bind(&password_hash)
.bind(&pseudo)
.execute(&self.pool)
.await
.map_err(|e| {
    let text = e.to_string();
    if text.contains("UNIQUE constraint failed") && text.contains("pseudo") {
        "Ce pseudo est déjà utilisé.".to_string()
    } else if text.contains("UNIQUE constraint failed") {
        "Cette adresse e-mail est déjà utilisée.".to_string()
    } else {
        format!("Impossible de créer l'utilisateur : {e}")
    }
})?;

        self.get_user_by_id(&user_id)
            .await?
            .ok_or_else(|| {
                "Utilisateur créé mais impossible à récupérer.".into()
            })
    }

    /// Récupère les informations publiques d'un utilisateur.
    pub async fn get_user_by_id(
        &self,
        user_id: &str,
    ) -> Result<Option<UserSummary>, String> {
        let row = sqlx::query(
            r#"
            SELECT user_id, email, status,  last_login
            FROM users
            WHERE user_id = ?
            "#,
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| format!("Erreur de recherche utilisateur : {e}"))?;

        Ok(row.map(|row| UserSummary {
            user_id: row.get("user_id"),
            email: row.get("email"),
            status: row.get("status"),
            last_login: row.get("last_login"),
        }))
    }

    /// Récupère les identifiants nécessaires à la vérification
    /// du mot de passe côté serveur.
    pub async fn get_credentials_by_email(
        &self,
        email: &str,
    ) -> Result<Option<UserCredentials>, String> {
        let email = email.trim().to_lowercase();

        let row = sqlx::query(
            r#"
            SELECT user_id, email, password_hash, pseudo
            FROM users
            WHERE email = ?
            "#,
        )
        .bind(&email)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| format!("Erreur de recherche des identifiants : {e}"))?;

        Ok(row.map(|row| UserCredentials {
            user_id: row.get("user_id"),
            email: row.get("email"),
            password_hash: row.get("password_hash"),
            pseudo: row.get("pseudo"),
        }))
    }

    /// Met à jour le statut d'un utilisateur.
    /// À appeler uniquement depuis une logique serveur autorisée.
    pub async fn set_status(
        &self,
        user_id: &str,
        status: &str,
    ) -> Result<bool, String> {
        if !matches!(
            status,
            "CONNECTED" | "DISCONNECTED" | "BANNED"
        ) {
            return Err("Statut utilisateur invalide.".into());
        }

        let result = sqlx::query(
            "UPDATE users SET status = ? WHERE user_id = ?",
        )
        .bind(status)
        .bind(user_id)
        .execute(&self.pool)
        .await
        .map_err(|e| format!("Impossible de modifier le statut : {e}"))?;

        Ok(result.rows_affected() > 0)
    }

    /// Enregistre la date de dernière connexion.
    pub async fn record_login(
        &self,
        user_id: &str,
    ) -> Result<bool, String> {
        let result = sqlx::query(
            r#"
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = ?
            "#,
        )
        .bind(user_id)
        .execute(&self.pool)
        .await
        .map_err(|e| format!("Impossible d'enregistrer la connexion : {e}"))?;

        Ok(result.rows_affected() > 0)
    }
}
