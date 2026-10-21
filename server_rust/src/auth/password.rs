use argon2::{
password_hash::{
PasswordHasher,
PasswordVerifier,
phc::PasswordHash,
},
Argon2,
};

/// Hash un mot de passe.
///
/// Le résultat contient également le sel et les paramètres
/// nécessaires pour vérifier le mot de passe plus tard.
pub fn hash_password(password: &str) -> Result<String, String> {
Argon2::default()
.hash_password(password.as_bytes())
.map(|hash| hash.to_string())
.map_err(|e| format!("Erreur lors du hash du mot de passe : {e}"))
}

/// Vérifie un mot de passe avec un hash existant.
pub fn verify_password(
password: &str,
password_hash: &str,
) -> bool {
let parsed_hash = match PasswordHash::new(password_hash) {
Ok(hash) => hash,
Err(_) => return false,
};


Argon2::default()
    .verify_password(password.as_bytes(), &parsed_hash)
    .is_ok()

}
