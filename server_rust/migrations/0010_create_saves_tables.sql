
-- ============================================================
-- ÉCHECS DE LOOT / PITY
-- ============================================================

CREATE TABLE IF NOT EXISTS echecs_sous_categories (
    echec_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,

    categorie TEXT NOT NULL,

    sous_categorie TEXT NOT NULL,

    nombre INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    UNIQUE (
        account_id,
        categorie,
        sous_categorie
    ),

    CHECK (nombre >= 0)
);

CREATE TABLE IF NOT EXISTS echecs_objets (
    echec_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,

    categorie TEXT NOT NULL,

    sous_categorie TEXT NOT NULL,

    objet_id INTEGER NOT NULL,

    nombre INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    UNIQUE (
        account_id,
        categorie,
        sous_categorie,
        objet_id
    ),

    CHECK (nombre >= 0)
);
-- ============================================================
-- STUFF DU JOUEUR
-- ============================================================

CREATE TABLE IF NOT EXISTS stuff (
    stuff_id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,
    objet_id INTEGER NOT NULL,
    stack_key TEXT NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id)
        ON DELETE RESTRICT,

    UNIQUE (account_id, objet_id,
        stack_key),

    CHECK (quantity > 0)
);
-- ============================================================
-- ÉQUIPEMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    stuff_id INTEGER NOT NULL UNIQUE,

    equipment_type TEXT NOT NULL,

    attack INTEGER NOT NULL DEFAULT 0,

    defense INTEGER NOT NULL DEFAULT 0,

    durability INTEGER NOT NULL DEFAULT 100,

    FOREIGN KEY (stuff_id)
        REFERENCES stuff(stuff_id)
        ON DELETE CASCADE,

    CHECK (attack >= 0),
    CHECK (defense >= 0),
    CHECK (durability >= 0)
);


-- ============================================================
-- POTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS potions (
    potion_id INTEGER PRIMARY KEY AUTOINCREMENT,

    stuff_id INTEGER NOT NULL UNIQUE,

    effect TEXT NOT NULL,

    potency INTEGER NOT NULL DEFAULT 0,

    duration INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (stuff_id)
        REFERENCES stuff(stuff_id)
        ON DELETE CASCADE,

    CHECK (potency >= 0),
    CHECK (duration >= 0)
);


-- ============================================================
-- LIVRES ENCHANTÉS
-- ============================================================

CREATE TABLE IF NOT EXISTS enchanted_books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,

    stuff_id INTEGER NOT NULL UNIQUE,

    book_level INTEGER NOT NULL,

    CHECK (book_level BETWEEN 1 AND 6),

    FOREIGN KEY (stuff_id)
        REFERENCES stuff(stuff_id)
        ON DELETE CASCADE
);


-- ============================================================
-- ENCHANTEMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS enchantments (
    enchantment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    enchantment_name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- TYPES D'ÉQUIPEMENTS COMPATIBLES AVEC LES ENCHANTEMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS enchantment_types (
    enchantment_id INTEGER NOT NULL,

    equipment_type TEXT NOT NULL,

    PRIMARY KEY (enchantment_id, equipment_type),

    FOREIGN KEY (enchantment_id)
        REFERENCES enchantments(enchantment_id)
        ON DELETE CASCADE
);


-- ============================================================
-- NIVEAUX D'ENCHANTEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS enchantment_levels (
    enchantment_id INTEGER NOT NULL,

    book_level INTEGER NOT NULL,

    max_enchantment_level INTEGER NOT NULL,

    PRIMARY KEY (enchantment_id, book_level),

    FOREIGN KEY (enchantment_id)
        REFERENCES enchantments(enchantment_id)
        ON DELETE CASCADE,

    CHECK (book_level BETWEEN 1 AND 6),

    CHECK (max_enchantment_level BETWEEN 1 AND 6)
);


-- ============================================================
-- ENCHANTEMENTS DES LIVRES
-- ============================================================

CREATE TABLE IF NOT EXISTS book_enchantments (
    book_id INTEGER NOT NULL,

    enchantment_id INTEGER NOT NULL,

    enchantment_level INTEGER NOT NULL,

    PRIMARY KEY (book_id, enchantment_id),

    FOREIGN KEY (book_id)
        REFERENCES enchanted_books(book_id)
        ON DELETE CASCADE,

    FOREIGN KEY (enchantment_id)
        REFERENCES enchantments(enchantment_id)
        ON DELETE CASCADE,

    CHECK (enchantment_level BETWEEN 1 AND 6)
);


-- ============================================================
-- MAXIMUM 6 ENCHANTEMENTS PAR LIVRE
-- ============================================================

CREATE TRIGGER IF NOT EXISTS limit_book_enchantments
BEFORE INSERT ON book_enchantments
FOR EACH ROW
WHEN (
    SELECT COUNT(*)
    FROM book_enchantments
    WHERE book_id = NEW.book_id
) >= 6
BEGIN
    SELECT RAISE(
        ABORT,
        'Un livre ne peut pas avoir plus de 6 enchantements'
    );
END;
