-- 0018_inventory_integrity.sql
-- Améliorations du stockage des équipements, potions et livres.
-- Cette migration complète les tables de 0010_create_saves_tables.sql.

-- ------------------------------------------------------------
-- Durabilité des équipements
-- ------------------------------------------------------------

ALTER TABLE equipment
ADD COLUMN durability_max INTEGER NOT NULL DEFAULT 100
CHECK (durability_max >= durability);

CREATE TRIGGER IF NOT EXISTS check_equipment_durability_insert
BEFORE INSERT ON equipment
FOR EACH ROW
WHEN NEW.durability > NEW.durability_max
BEGIN
    SELECT RAISE(ABORT, 'La durabilite actuelle depasse la durabilite maximale');
END;

CREATE TRIGGER IF NOT EXISTS check_equipment_durability_update
BEFORE UPDATE OF durability, durability_max ON equipment
FOR EACH ROW
WHEN NEW.durability > NEW.durability_max
BEGIN
    SELECT RAISE(ABORT, 'La durabilite actuelle depasse la durabilite maximale');
END;

-- ------------------------------------------------------------
-- Enchantements associés aux équipements
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS equipment_enchantments (
    equipment_id INTEGER NOT NULL,
    enchantment_id INTEGER NOT NULL,
    enchantment_level INTEGER NOT NULL,

    PRIMARY KEY (equipment_id, enchantment_id),

    FOREIGN KEY (equipment_id)
        REFERENCES equipment(equipment_id)
        ON DELETE CASCADE,

    FOREIGN KEY (enchantment_id)
        REFERENCES enchantments(enchantment_id)
        ON DELETE RESTRICT,

    CHECK (enchantment_level BETWEEN 1 AND 6)
);

CREATE INDEX IF NOT EXISTS idx_equipment_enchantments_enchantment
ON equipment_enchantments(enchantment_id);

-- Un équipement ne peut recevoir qu'un enchantement compatible avec
-- son equipment_type. La clé primaire interdit les doublons.
CREATE TRIGGER IF NOT EXISTS check_equipment_enchantment_compatibility
BEFORE INSERT ON equipment_enchantments
FOR EACH ROW
WHEN NOT EXISTS (
    SELECT 1
    FROM equipment eq
    JOIN enchantment_types et
      ON et.equipment_type = eq.equipment_type
    WHERE eq.equipment_id = NEW.equipment_id
      AND et.enchantment_id = NEW.enchantment_id
)
BEGIN
    SELECT RAISE(ABORT, 'Enchantement incompatible avec cet equipement');
END;

CREATE TRIGGER IF NOT EXISTS check_equipment_enchantment_compatibility_update
BEFORE UPDATE OF equipment_id, enchantment_id ON equipment_enchantments
FOR EACH ROW
WHEN NOT EXISTS (
    SELECT 1
    FROM equipment eq
    JOIN enchantment_types et
      ON et.equipment_type = eq.equipment_type
    WHERE eq.equipment_id = NEW.equipment_id
      AND et.enchantment_id = NEW.enchantment_id
)
BEGIN
    SELECT RAISE(ABORT, 'Enchantement incompatible avec cet equipement');
END;

-- ------------------------------------------------------------
-- Livres : maximum d'enchantements égal au niveau du livre
-- ------------------------------------------------------------

DROP TRIGGER IF EXISTS limit_book_enchantments;

CREATE TRIGGER limit_book_enchantments
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
    SELECT RAISE(ABORT, 'Le livre a atteint sa limite d enchantements');
END;

CREATE TRIGGER IF NOT EXISTS limit_book_enchantments_update
BEFORE UPDATE OF book_id, enchantment_id ON book_enchantments
FOR EACH ROW
WHEN (
    NEW.book_id <> OLD.book_id
    AND (
        SELECT COUNT(*)
        FROM book_enchantments
        WHERE book_id = NEW.book_id
    ) >= (
        SELECT book_level
        FROM enchanted_books
        WHERE book_id = NEW.book_id
    )
    OR NOT EXISTS (
        SELECT 1
        FROM enchanted_books
        WHERE book_id = NEW.book_id
    )
)
BEGIN
    SELECT RAISE(ABORT, 'Le livre a atteint sa limite d enchantements');
END;

-- Les livres ne possèdent ni rareté ni rang.
-- Le déclencheur s'exécute après leur création dans enchanted_books.
CREATE TRIGGER IF NOT EXISTS clear_book_rarity_and_rank
AFTER INSERT ON enchanted_books
FOR EACH ROW
BEGIN
    UPDATE stuff
    SET rarete = NULL,
        rang = NULL
    WHERE stuff_id = NEW.stuff_id;
END;

-- ------------------------------------------------------------
-- Potions : un exemplaire par ligne d'inventaire
-- ------------------------------------------------------------

-- La clé stack_key de chaque potion doit être unique (UUID côté Rust).
-- Ces déclencheurs garantissent qu'une ligne potion ne représente
-- jamais plusieurs exemplaires empilés.
CREATE TRIGGER IF NOT EXISTS potion_quantity_one_after_insert
AFTER INSERT ON potions
FOR EACH ROW
BEGIN
    UPDATE stuff
    SET quantity = 1
    WHERE stuff_id = NEW.stuff_id;
END;

CREATE TRIGGER IF NOT EXISTS potion_quantity_one_before_update
BEFORE UPDATE OF quantity ON stuff
FOR EACH ROW
WHEN EXISTS (
    SELECT 1
    FROM potions
    WHERE stuff_id = OLD.stuff_id
) AND NEW.quantity <> 1
BEGIN
    SELECT RAISE(ABORT, 'Une potion doit avoir une quantite egale a 1');
END;
