INSERT INTO enchantments (enchantment_name) VALUES
    ('Fire Aura'),
    ('Poison'),
    ('Durability'),
    ('Putrefaction'),
    ('Lightning'),
    ('Critical'),
    ('Cryogenisation'),
    ('Précision'),
    ('Rapidity'),
    ('Respiration'),
    ('Vitality'),
    ('Protection'),
    ('Renvoie'),
    ('Réparation'),
    ('Blindage'),
    ('Tranchant'),
    ('Capturing item'),
    ('luck');
**⚔️ Swords**


- Critical
- Cryogenization
- Accuracy
- Durability
- Repair
- Sharpness
- Item Capture

**🔫 Guns**
- Critical
- Rapidity

**🛡️ Armor**

- Durability
- Respiration
- Protection
- Reflection
- Repair


**Shields**
- Plating
- Vitality

**⛏️ Pickaxes**
- Luck
- Repair

INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'épée'
FROM enchantments
WHERE enchantment_name IN (
    'Fire Aura',
    'Poison',
    'Durability',
    'Putrefaction',
    'Lightning',
    'Critical',
    'Cryogenisation',
    'Réparation',
    'Précision',
    'Tranchant',
    'Capturing item'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'armure'
FROM enchantments
WHERE enchantment_name IN (
    'Respiration',
    'Durability',
    'Vitality',
    'Protection',
    'Réparation',
    'Renvoie'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'shield'
FROM enchantments
WHERE enchantment_name IN ( 
    'Protection',
    'Blindage'
    );
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'armes à feu'
FROM enchantments
WHERE enchantment_name IN (
    'Rapidity',
    'Critical'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'pioche'
FROM enchantments
WHERE enchantment_name IN (
    'luck',
    'Réparation'
    );
INSERT INTO enchantment_levels (
    enchantment_id,
    book_level,
    max_enchantment_level
)
SELECT
    e.enchantment_id,
    niveau.book_level,
    niveau.book_level
FROM enchantments e
CROSS JOIN (
    SELECT 1 AS book_level
    UNION ALL SELECT 2
    UNION ALL SELECT 3
    UNION ALL SELECT 4
    UNION ALL SELECT 5
    UNION ALL SELECT 6
) AS niveau;
