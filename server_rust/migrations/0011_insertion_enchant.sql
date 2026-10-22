INSERT INTO enchantments (enchantment_name) VALUES
    ('Fire Aura'),
    ('Poison'),
    ('Durability'),
    ('Putrefaction'),
    ('Lightning'),
    ('Critical'),
    ('Cryogenization'),
    ('Accuracy'),
    ('Rapidity'),
    ('Respiration'),
    ('Vitality'),
    ('Protection'),
    ('Reflection'),
    ('Repair'),
    ('Plating'),
    ('Sharpness'),
    ('Item Capture'),
    ('luck');

 



INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'Swords'
FROM enchantments
WHERE enchantment_name IN (
    'Fire Aura',
    'Poison',
    'Durability',
    'Putrefaction',
    'Lightning',
    'Critical',
    'Cryogenization',
    'Repair',
    'Accuracy',
    'Sharpness',
    'Item Capture'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'Armors'
FROM enchantments
WHERE enchantment_name IN (
    'Respiration',
    'Durability',
    'Vitality',
    'Protection',
    'Repair',
    'Reflection'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'shields'
FROM enchantments
WHERE enchantment_name IN ( 
    'Protection',
    'Plating'
    );
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'Guns'
FROM enchantments
WHERE enchantment_name IN (
    'Rapidity',
    'Critical'
);
INSERT INTO enchantment_types (enchantment_id, equipment_type)
SELECT enchantment_id, 'Pickaxes'
FROM enchantments
WHERE enchantment_name IN (
    'luck',
    'Repair'
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
