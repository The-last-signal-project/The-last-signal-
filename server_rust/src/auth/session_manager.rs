//! Sessions de connexion (table `sessions`).
//!
//! Une session relie une connexion TCP (`session_id`) à un utilisateur et,
//! une fois choisi, à un compte de jeu. C'est la source de vérité pour
//! retrouver le compte d'un joueur (inventaire, argent, rôle...).
//!
//! Cycle de vie :
//! - `bind_account`  : à la sélection du compte (ACCOUNT_SELECT réussi),
//! - `account_of`    : pour retrouver le compte et son rôle,
//! - `close`         : à la déconnexion,
//! - `close_all_open`: au démarrage du serveur (sessions restées ouvertes
//!                     après un arrêt brutal).

use sqlx::{Row, SqlitePool};

/// Rôles (`roles.role_name`) considérés comme administrateurs.
/// La comparaison ignore la casse : `admin`, `Dev`, `SuperDev`.
const ADMIN_ROLES: [&str; 3] = ["admin", "dev", "superdev"];

/// Vrai si le rôle donne les droits d'administrateur
/// (accès au loot admin des coffres, etc.).
pub fn is_admin_role(role_name: &str) -> bool {
    ADMIN_ROLES
        .iter()
        .any(|admin| role_name.eq_ignore_ascii_case(admin))
}

/// Compte rattaché à une session ouverte.
#[derive(Debug, Clone)]
pub struct SessionAccount {
    pub account_id: i64,
    pub role_name: String,
}

impl SessionAccount {
    pub fn is_admin(&self) -> bool {
        is_admin_role(&self.role_name)
    }
}

pub struct SessionManager {
    pool: SqlitePool,
}

impl SessionManager {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Enregistre (ou met à jour) la session avec son compte.
    /// À appeler une fois que le compte a été vérifié comme appartenant
    /// à l'utilisateur.
    pub async fn bind_account(
        &self,
        session_id: &str,
        user_id: &str,
        account_id: i64,
    ) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            INSERT INTO sessions (session_id, user_id, account_id)
            VALUES (?, ?, ?)
            ON CONFLICT (session_id) DO UPDATE SET
                user_id = excluded.user_id,
                account_id = excluded.account_id,
                ended_at = NULL,
                disconnect_reason = NULL
            "#,
        )
        .bind(session_id)
        .bind(user_id)
        .bind(account_id)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Compte et rôle d'une session encore ouverte, s'il y en a un.
    pub async fn account_of(
        &self,
        session_id: &str,
    ) -> Result<Option<SessionAccount>, sqlx::Error> {
        let row = sqlx::query(
            r#"
            SELECT s.account_id, r.role_name
            FROM sessions AS s
            JOIN accounts AS a ON a.account_id = s.account_id
            JOIN roles AS r ON r.role_id = a.role_id
            WHERE s.session_id = ?
              AND s.ended_at IS NULL
            "#,
        )
        .bind(session_id)
        .fetch_optional(&self.pool)
        .await?;

        Ok(row.map(|row| SessionAccount {
            account_id: row.get("account_id"),
            role_name: row.get("role_name"),
        }))
    }

    /// Termine la session (sans effet si elle est déjà terminée).
    pub async fn close(
        &self,
        session_id: &str,
        reason: &str,
    ) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE sessions
            SET ended_at = CURRENT_TIMESTAMP,
                disconnect_reason = ?
            WHERE session_id = ?
              AND ended_at IS NULL
            "#,
        )
        .bind(reason)
        .bind(session_id)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Termine toutes les sessions restées ouvertes (au démarrage du serveur).
    /// Retourne le nombre de sessions fermées.
    pub async fn close_all_open(
        pool: &SqlitePool,
        reason: &str,
    ) -> Result<u64, sqlx::Error> {
        let result = sqlx::query(
            r#"
            UPDATE sessions
            SET ended_at = CURRENT_TIMESTAMP,
                disconnect_reason = ?
            WHERE ended_at IS NULL
            "#,
        )
        .bind(reason)
        .execute(pool)
        .await?;

        Ok(result.rows_affected())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn admin_dev_and_superdev_are_admins() {
        for role in ["admin", "Admin", "ADMIN", "Dev", "dev", "SuperDev", "superdev"] {
            assert!(is_admin_role(role), "{role} devrait être admin");
        }
    }

    #[test]
    fn other_roles_are_not_admins() {
        for role in ["joueur", "modo", "", "administrator", "developer", "super dev"] {
            assert!(!is_admin_role(role), "{role} ne devrait pas être admin");
        }
    }

    #[test]
    fn session_account_uses_the_role() {
        let admin = SessionAccount { account_id: 1, role_name: "SuperDev".into() };
        let player = SessionAccount { account_id: 2, role_name: "joueur".into() };

        assert!(admin.is_admin());
        assert!(!player.is_admin());
    }
}
