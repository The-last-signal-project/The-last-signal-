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
