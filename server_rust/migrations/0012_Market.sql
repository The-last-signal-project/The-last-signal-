
-- ============================================================
-- 0012 - MARCHE
-- Catalogue, variantes, ordres et transactions
-- ============================================================

-- ------------------------------------------------------------
-- 1. CATALOGUE
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS objets_dispo (
    objet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    image_path TEXT,

    prix_base INTEGER NOT NULL DEFAULT 0,
    prix_marche INTEGER NOT NULL DEFAULT 0,

    est_empilable INTEGER NOT NULL DEFAULT 1,

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
    CHECK (prix_marche >= 0),
    CHECK (est_empilable IN (0, 1))
);

-- ------------------------------------------------------------
-- 2. VARIANTES
-- Une variante correspond à un objet et à une combinaison
-- précise de caractéristiques.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS variantes_marche (
    variante_id INTEGER PRIMARY KEY AUTOINCREMENT,

    objet_id INTEGER NOT NULL,

    niveau INTEGER NOT NULL DEFAULT 0,
    rarete TEXT,
    rang TEXT,

    signature TEXT NOT NULL,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id)
        ON DELETE RESTRICT,

    UNIQUE (objet_id, signature),

    CHECK (niveau >= 0),

    CHECK (
        rarete IS NULL OR rarete IN (
            'Commun',
            'Peu commun',
            'Rare',
            'Super rare',
            'Épique',
            'Légendaire',
            'Mythique'
        )
    ),

    CHECK (
        rang IS NULL OR rang IN (
            'G', 'F', 'E', 'D', 'C',
            'B', 'A', 'S', 'SS', 'SSS'
        )
    )
);

CREATE TABLE IF NOT EXISTS variante_enchantements (
    variante_id INTEGER NOT NULL,
    enchantment_id INTEGER NOT NULL,
    niveau INTEGER NOT NULL,

    PRIMARY KEY (variante_id, enchantment_id),

    FOREIGN KEY (variante_id)
        REFERENCES variantes_marche(variante_id)
        ON DELETE CASCADE,

    FOREIGN KEY (enchantment_id)
        REFERENCES enchantments(enchantment_id)
        ON DELETE RESTRICT,

    CHECK (niveau > 0)
);

-- ------------------------------------------------------------
-- 3. ORDRES D'ACHAT
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ordres_achat (
    ordre_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,
    variante_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    quantity_remaining INTEGER NOT NULL,

    prix_unitaire_max INTEGER NOT NULL,

    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut TEXT NOT NULL DEFAULT 'actif',

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (variante_id)
        REFERENCES variantes_marche(variante_id)
        ON DELETE RESTRICT,

    CHECK (quantity > 0),
    CHECK (quantity_remaining >= 0),
    CHECK (quantity_remaining <= quantity),
    CHECK (prix_unitaire_max > 0),

    CHECK (statut IN ('actif', 'execute', 'annule'))
);

-- ------------------------------------------------------------
-- 4. ORDRES DE VENTE
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ordres_vente (
    ordre_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,
    variante_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    quantity_remaining INTEGER NOT NULL,

    prix_unitaire INTEGER NOT NULL,

    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut TEXT NOT NULL DEFAULT 'actif',

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (variante_id)
        REFERENCES variantes_marche(variante_id)
        ON DELETE RESTRICT,

    CHECK (quantity > 0),
    CHECK (quantity_remaining >= 0),
    CHECK (quantity_remaining <= quantity),
    CHECK (prix_unitaire > 0),

    CHECK (statut IN ('actif', 'execute', 'annule'))
);

-- ------------------------------------------------------------
-- 5. TRANSACTIONS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS transactions_marche (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    variante_id INTEGER NOT NULL,

    ordre_achat_id INTEGER NOT NULL,
    ordre_vente_id INTEGER NOT NULL,

    acheteur_id INTEGER NOT NULL,
    vendeur_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    prix_unitaire INTEGER NOT NULL,
    montant_total INTEGER NOT NULL,

    date_transaction DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (variante_id)
        REFERENCES variantes_marche(variante_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (ordre_achat_id)
        REFERENCES ordres_achat(ordre_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (ordre_vente_id)
        REFERENCES ordres_vente(ordre_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (acheteur_id)
        REFERENCES accounts(account_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (vendeur_id)
        REFERENCES accounts(account_id)
        ON DELETE RESTRICT,

    CHECK (acheteur_id != vendeur_id),
    CHECK (quantity > 0),
    CHECK (prix_unitaire > 0),
    CHECK (montant_total > 0),
    CHECK (montant_total = quantity * prix_unitaire)
);

-- ------------------------------------------------------------
-- 6. VALIDATION DES TRANSACTIONS
-- Le prix d'exécution est celui de l'ordre de vente.
-- ------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS verifier_transaction_marche
BEFORE INSERT ON transactions_marche
BEGIN

    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM ordres_achat a
            JOIN ordres_vente v
              ON v.ordre_id = NEW.ordre_vente_id
            WHERE a.ordre_id = NEW.ordre_achat_id
              AND a.statut = 'actif'
              AND v.statut = 'actif'
              AND a.variante_id = NEW.variante_id
              AND v.variante_id = NEW.variante_id
              AND a.account_id = NEW.acheteur_id
              AND v.account_id = NEW.vendeur_id
              AND a.account_id != v.account_id
              AND NEW.quantity <= a.quantity_remaining
              AND NEW.quantity <= v.quantity_remaining
              AND NEW.prix_unitaire = v.prix_unitaire
              AND NEW.prix_unitaire <= a.prix_unitaire_max
        )
        THEN RAISE(ABORT, 'Transaction de marche invalide')
    END;

    SELECT CASE
        WHEN (
            SELECT type
            FROM objets_dispo
            WHERE objet_id = (
                SELECT objet_id
                FROM variantes_marche
                WHERE variante_id = NEW.variante_id
            )
        ) IN ('equipment', 'armes', 'muni')
        THEN RAISE(ABORT, 'Categorie non disponible sur ce marche')
    END;

END;

-- ------------------------------------------------------------
-- 7. MISE A JOUR AUTOMATIQUE DES QUANTITES
-- ------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS maj_ordres_apres_transaction
AFTER INSERT ON transactions_marche
BEGIN

    UPDATE ordres_achat
    SET
        quantity_remaining = quantity_remaining - NEW.quantity,
        statut = CASE
            WHEN quantity_remaining - NEW.quantity = 0
            THEN 'execute'
            ELSE 'actif'
        END
    WHERE ordre_id = NEW.ordre_achat_id;

    UPDATE ordres_vente
    SET
        quantity_remaining = quantity_remaining - NEW.quantity,
        statut = CASE
            WHEN quantity_remaining - NEW.quantity = 0
            THEN 'execute'
            ELSE 'actif'
        END
    WHERE ordre_id = NEW.ordre_vente_id;

END;

-- ------------------------------------------------------------
-- 8. INDEX
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_variantes_objet
ON variantes_marche(objet_id);

CREATE INDEX IF NOT EXISTS idx_ordres_achat_matching
ON ordres_achat(
    variante_id,
    statut,
    prix_unitaire_max DESC,
    date_creation ASC
);

CREATE INDEX IF NOT EXISTS idx_ordres_vente_matching
ON ordres_vente(
    variante_id,
    statut,
    prix_unitaire ASC,
    date_creation ASC
);

CREATE INDEX IF NOT EXISTS idx_transactions_variante
ON transactions_marche(
    variante_id,
    date_transaction
);

CREATE INDEX IF NOT EXISTS idx_transactions_vendeur
ON transactions_marche(vendeur_id, date_transaction);

CREATE INDEX IF NOT EXISTS idx_transactions_acheteur
ON transactions_marche(acheteur_id, date_transaction);
