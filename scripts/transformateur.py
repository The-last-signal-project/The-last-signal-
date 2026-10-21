from pathlib import Path

# Extensions à corriger
EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".rs",
}

corriges = 0

for fichier in Path(".").rglob("*"):
    if not fichier.is_file():
        continue

    if fichier.suffix.lower() not in EXTENSIONS:
        continue

    try:
        data = fichier.read_bytes()

        # UTF-8 BOM
        if data.startswith(b"\xef\xbb\xbf"):
            texte = data.decode("utf-8-sig")
            fichier.write_text(texte, encoding="utf-8")

            print(f"✅ BOM supprimé : {fichier}")
            corriges += 1

    except Exception as e:
        print(f"⚠ Impossible de traiter {fichier} : {e}")

print()
print(f"🎉 {corriges} fichier(s) corrigé(s).")
