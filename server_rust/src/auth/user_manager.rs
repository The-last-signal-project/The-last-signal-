
use sqlx::{Row, SqlitePool};
use uuid::Uuid;

use crate::utils::password::hash_password;

/// Informations utilisateur pouvant être renvoyées à l'application.
#[derive(Debug, Clone)]
pub struct UserSummary {
    pub user_id: String,
    pub email: String,
    pub status: String,
    pub created_at: String,
    pub last_login: Option<String>,
}

/// Informations internes nécessaires à l'authentification.
/// Ne jamais envoyer password_hash au client.
#[derive(Debug, Clone)]
pub struct UserCredentials {
    pub user_id: String,
    pub email: String,
    pub password_hash: String,
}

pub struct UserManager {
    pool: SqlitePool,
}

impl UserManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Inscrit un utilisateur normal.
    /// Le mot de passe est haché avant d'être stocké.
    pub async fn create_user(
        &self,
        email: &str,
        password: &str,
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

        let password_hash = hash_password(password)?;

        let user_id = Uuid::new_v4().to_string();

        sqlx::query(
            r#"
            INSERT INTO users (user_id, email, password_hash)
            VALUES (?, ?, ?)
            "#,
        )
        .bind(&user_id)
        .bind(&email)
        .bind(&password_hash)
        .execute(&self.pool)
        .await
        .map_err(|e| {
            if e.to_string().contains("UNIQUE constraint failed") {
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
            SELECT user_id, email, status, created_at, last_login
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
            created_at: row.get("created_at"),
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
            SELECT user_id, email, password_hash
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
