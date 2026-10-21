import os
import json
import base64
import argparse
from cryptography.fernet import Fernet


KEY_FILE = "security/master.key"
VAULT_FILE = "security/vault.enc"


def create_key():
    """
    Crée une clé maître si elle n'existe pas.
    """
    if os.getenv("VAULT_KEY"):
        with open(KEY_FILE, "wb") as f:
            f.write(os.getenv("VAULT_KEY").encode())
        
    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)

        print("Nouvelle clé créée.")


def load_key():
    if os.getenv("VAULT_KEY"):

        return os.getenv("VAULT_KEY").encode()
        

    with open(KEY_FILE, "rb") as f:
        return f.read()


def encrypt_vault(data):

    key = load_key()

    cipher = Fernet(key)

    encrypted = cipher.encrypt(
        json.dumps(data).encode()
    )

    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)


def decrypt_vault():

    key = load_key()

    cipher = Fernet(key)

    with open(VAULT_FILE, "rb") as f:
        encrypted = f.read()

    decrypted = cipher.decrypt(encrypted)

    return json.loads(decrypted)


def add_secret(name, value):

    if os.path.exists(VAULT_FILE):
        secrets = decrypt_vault()
    else:
        secrets = {}

    secrets[name] = value

    encrypt_vault(secrets)

def get_secret(name):
    """
    Récupère un secret depuis le Vault.

    Retourne None si le secret n'existe pas.
    """

    if not os.path.exists(VAULT_FILE):
        return None

    secrets = decrypt_vault()

    return secrets.get(name)


def generate_communication_key():
    """
    Génère une clé de communication aléatoire
    de 64 octets (512 bits).
    """

    return os.urandom(64)


def get_or_create_communication_key():
    """
    Récupère COMMUNICATION_KEY depuis le Vault.

    Si elle n'existe pas, une nouvelle clé de 64 octets
    est générée, encodée en Base64 puis enregistrée
    dans le Vault.

    Retourne la clé sous forme de bytes.
    """

    secret = get_secret("COMMUNICATION_KEY")

    if secret is not None:

        key = base64.b64decode(secret)

        if len(key) != 64:
            raise ValueError(
                "COMMUNICATION_KEY doit faire exactement 64 octets."
            )

        return key

    key = generate_communication_key()

    add_secret(
        "COMMUNICATION_KEY",
        base64.b64encode(key).decode("ascii")
    )

    return key

if __name__ == "__main__":

    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--name",
        required=True,
        help="Nom du secret"
    )

    parser.add_argument(
        "--value",
        required=True,
        help="Valeur du secret"
    )

    args = parser.parse_args()

    os.makedirs("security", exist_ok=True)

    create_key()

    add_secret(
        args.name,
        args.value
    )

    print(f"Secret ajouté : {args.name}")

    
