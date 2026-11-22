
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

    UNIQUE (account_id, categorie, sous_categorie),

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

    UNIQUE (account_id, categorie, sous_categorie, objet_id),

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

    rarete TEXT,
    rang TEXT,
    visible TEXT NOT NULL DEFAULT 1,
        CHECK(visible IN (0,1)),

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    FOREIGN KEY (objet_id)
        REFERENCES objets_dispo(objet_id)
        ON DELETE RESTRICT,

    UNIQUE (account_id, objet_id, stack_key),

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

    -- Durabilité actuelle
    durability INTEGER NOT NULL DEFAULT 100,

    -- Durabilité maximale définie à la création
    durability_max INTEGER NOT NULL DEFAULT 100,

    FOREIGN KEY (stuff_id)
        REFERENCES stuff(stuff_id)
        ON DELETE CASCADE,

    CHECK (attack >= 0),
    CHECK (defense >= 0),

    CHECK (durability >= 0),
    CHECK (durability_max > 0),
    CHECK (durability <= durability_max)
);


-- La durabilité maximale ne doit pas changer après création.
CREATE TRIGGER IF NOT EXISTS prevent_durability_max_update
BEFORE UPDATE OF durability_max ON equipment
FOR EACH ROW
WHEN NEW.durability_max != OLD.durability_max
BEGIN
    SELECT RAISE(
        ABORT,
        'La durabilité maximale ne peut pas être modifiée'
    );
END;


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

    FOREIGN KEY (stuff_id)
        REFERENCES stuff(stuff_id)
        ON DELETE CASCADE,

    CHECK (book_level BETWEEN 1 AND 6)
);


-- ============================================================
-- ENCHANTEMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS enchantments (
    enchantment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    enchantment_name TEXT NOT NULL UNIQUE,

    -- Valeur de base utilisée dans le calcul du prix théorique.
    base_value INTEGER NOT NULL DEFAULT 0,

    CHECK (base_value >= 0)
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
-- NIVEAUX D'ENCHANTEMENT AUTORISÉS PAR NIVEAU DE LIVRE
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

    -- Un même enchantement ne peut apparaître qu'une fois
    -- dans un même livre.
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
-- LIMITATION DU NOMBRE D'ENCHANTEMENTS PAR LIVRE
-- ============================================================

-- Le nombre d'enchantements ne peut pas dépasser le niveau du livre.
CREATE TRIGGER IF NOT EXISTS limit_book_enchantments
BEFORE INSERT ON book_enchantments
FOR EACH ROW
WHEN (
    SELECT COUNT(*)
    FROM book_enchantments
    WHERE book_id = NEW.book_id
) >= (
    SELECT book_level
    FROM enchanted_books
    WHERE book_id = NEW.book_id
)
BEGIN
    SELECT RAISE(
        ABORT,
        'Le nombre d''enchantements dépasse le niveau du livre'
    );
END;


-- Même vérification lorsqu'un enchantement est déplacé
-- vers un autre livre.
CREATE TRIGGER IF NOT EXISTS limit_book_enchantments_update
BEFORE UPDATE OF book_id, enchantment_id ON book_enchantments
FOR EACH ROW
WHEN (
    SELECT COUNT(*)
    FROM book_enchantments
    WHERE book_id = NEW.book_id
      AND NOT (
          book_id = OLD.book_id
          AND enchantment_id = OLD.enchantment_id
      )
) >= (
    SELECT book_level
    FROM enchanted_books
    WHERE book_id = NEW.book_id
)
BEGIN
    SELECT RAISE(
        ABORT,
        'Le nombre d''enchantements dépasse le niveau du livre'
    );
END;


-- Un livre ne peut pas perdre un niveau si son nombre
-- d'enchantements dépasse alors son nouveau niveau.
CREATE TRIGGER IF NOT EXISTS check_book_level_update
BEFORE UPDATE OF book_level ON enchanted_books
FOR EACH ROW
WHEN NEW.book_level < (
    SELECT COUNT(*)
    FROM book_enchantments
    WHERE book_id = OLD.book_id
)
BEGIN
    SELECT RAISE(
        ABORT,
        'Le niveau du livre est inférieur à son nombre d''enchantements'
    );
END;


-- ============================================================
-- VALIDATION DES NIVEAUX D'ENCHANTEMENT DES LIVRES
-- ============================================================

-- Vérifie que le niveau choisi est autorisé pour le niveau
-- du livre concerné.
CREATE TRIGGER IF NOT EXISTS validate_book_enchantment_level
BEFORE INSERT ON book_enchantments
FOR EACH ROW
WHEN NEW.enchantment_level > COALESCE(
    (
        SELECT el.max_enchantment_level
        FROM enchantment_levels el
        JOIN enchanted_books eb
            ON eb.book_level = el.book_level
        WHERE eb.book_id = NEW.book_id
          AND el.enchantment_id = NEW.enchantment_id
    ),
    0
)
BEGIN
    SELECT RAISE(
        ABORT,
        'Niveau d''enchantement non autorisé pour ce livre'
    );
END;


CREATE TRIGGER IF NOT EXISTS validate_book_enchantment_level_update
BEFORE UPDATE OF book_id, enchantment_id, enchantment_level
ON book_enchantments
FOR EACH ROW
WHEN NEW.enchantment_level > COALESCE(
    (
        SELECT el.max_enchantment_level
        FROM enchantment_levels el
        JOIN enchanted_books eb
            ON eb.book_level = el.book_level
        WHERE eb.book_id = NEW.book_id
          AND el.enchantment_id = NEW.enchantment_id
    ),
    0
)
BEGIN
    SELECT RAISE(
        ABORT,
        'Niveau d''enchantement non autorisé pour ce livre'
    );
END;


-- ============================================================
-- INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_stuff_account
ON stuff(account_id);

CREATE INDEX IF NOT EXISTS idx_stuff_objet
ON stuff(objet_id);

CREATE INDEX IF NOT EXISTS idx_equipment_stuff
ON equipment(stuff_id);

CREATE INDEX IF NOT EXISTS idx_potions_stuff
ON potions(stuff_id);

CREATE INDEX IF NOT EXISTS idx_books_stuff
ON enchanted_books(stuff_id);

CREATE INDEX IF NOT EXISTS idx_book_enchantments_book
ON book_enchantments(book_id);

CREATE INDEX IF NOT EXISTS idx_book_enchantments_enchantment
ON book_enchantments(enchantment_id);

CREATE INDEX IF NOT EXISTS idx_enchantment_types_equipment
ON enchantment_types(equipment_type);

CREATE INDEX IF NOT EXISTS idx_enchantment_levels_book
ON enchantment_levels(book_level);
