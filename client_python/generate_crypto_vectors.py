
from pathlib import Path

from crypto import encrypt

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "tests" / "crypto_reference_vectors.txt"


def main():
    key = bytes(range(64))
    plaintext = bytes(range(16))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Vecteurs de reference Python : packet_type:chiffre_hex"
    ]

    for packet_type in range(1, 23):
        ciphertext = encrypt(key, packet_type, plaintext)
        lines.append(f"{packet_type}:{ciphertext.hex()}")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii")

    print(f"22 vecteurs ecrits dans : {OUTPUT}")
    print("\n".join(lines[1:]))


if __name__ == "__main__":
    main()
