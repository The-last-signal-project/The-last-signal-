CREATE TABLE IF NOT EXISTS objets_dispo (
    objet_id INTEGER PRIMARY KEY AUTOINCREMENT,

    nom TEXT NOT NULL UNIQUE,

    type TEXT NOT NULL,

    image_path TEXT,

    prix_base INTEGER NOT NULL DEFAULT 0,

    prix_marche INTEGER NOT NULL DEFAULT 0,

    CHECK (type IN (
        'equipment',
        'potion',
        'enchanted_book',
        'consumable',
        'material',
        'armes',
        'basic',
        'muni',
        'mineral'
    )),

    CHECK (prix_base >= 0),
    CHECK (prix_marche >= 0)
);
CREATE TABLE IF NOT EXISTS ordres_achat (
    ordre_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,
    objet_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    quantity_remaining INTEGER NOT NULL,

    prix_unitaire_max INTEGER NOT NULL,

    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut TEXT NOT NULL DEFAULT 'actif',

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id)
        ON DELETE RESTRICT,

    CHECK (quantity > 0),
    CHECK (quantity_remaining >= 0),
    CHECK (quantity_remaining <= quantity),
    CHECK (prix_unitaire_max > 0),

    CHECK (statut IN (
        'actif',
        'execute',
        'annule'
    ))
);
CREATE TABLE IF NOT EXISTS ordres_vente (
    ordre_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,
    objet_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    quantity_remaining INTEGER NOT NULL,

    prix_unitaire INTEGER NOT NULL,

    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut TEXT NOT NULL DEFAULT 'actif',

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id)
        ON DELETE RESTRICT,

    CHECK (quantity > 0),
    CHECK (quantity_remaining >= 0),
    CHECK (quantity_remaining <= quantity),
    CHECK (prix_unitaire > 0),

    CHECK (statut IN (
        'actif',
        'execute',
        'annule'
    ))
);
CREATE TABLE IF NOT EXISTS transactions_marche (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    objet_id INTEGER NOT NULL,

    ordre_achat_id INTEGER NOT NULL,
    ordre_vente_id INTEGER NOT NULL,

    acheteur_id INTEGER NOT NULL,
    vendeur_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    prix_unitaire INTEGER NOT NULL,
    montant_total INTEGER NOT NULL,

    date_transaction DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id),

    CHECK (quantity > 0),
    CHECK (prix_unitaire > 0),
    CHECK (montant_total > 0)
);
CREATE INDEX IF NOT EXISTS idx_ordres_achat_matching
ON ordres_achat (
    objet_id,
    statut,
    prix_unitaire_max DESC,
    date_creation ASC
);

CREATE INDEX IF NOT EXISTS idx_ordres_vente_matching
ON ordres_vente (
    objet_id,
    statut,
    prix_unitaire ASC,
    date_creation ASC
);

CREATE INDEX IF NOT EXISTS idx_transactions_marche_objet
ON transactions_marche (
    objet_id,
    date_transaction
);
