use fernet::Fernet;
use serde_json::Value;
use std::fs;

pub fn decrypt_vault() -> Result<Value, Box<dyn std::error::Error>> {
    let key = match std::env::var("VAULT_KEY") {
        Ok(key) => key,
        Err(_) => fs::read_to_string("../security/master.key")?,
    };

    let cipher = Fernet::new(key.trim())
        .ok_or("Clé Fernet invalide")?;

    let encrypted = fs::read_to_string("../security/vault.enc")?;

    let decrypted = cipher.decrypt(encrypted.trim())?;

    let vault: Value = serde_json::from_slice(&decrypted)?;

    Ok(vault)
}



/// Extrait les mots de passe du vault.
pub fn extract_passwords() -> Result<(String, String), Box<dyn std::error::Error>> {
    let master_key = Path::new(env!("CARGO_MANIFEST_DIR")).join("../security/master.key");

    if master_key.exists() || std::env::var("VAULT_KEY").is_ok() {
        let vault = decrypt_vault()?;
    

    let password1 = vault["user1_password"]
        .as_str()
        .ok_or("Mot de passe user1 absent")?
        .to_string();

    let password2 = vault["user2_password"]
        .as_str()
        .ok_or("Mot de passe user2 absent")?
        .to_string();

    Ok((password1, password2))
}
else {
        log::warn!(
            "master.key introuvable ({}) et VAULT_KEY absente : \
             les comptes spéciaux ne pourront pas êtres créés.",
            master_key.display()
        );
    }
}