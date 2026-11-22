-- ============================================================================
-- 0012_Market.sql
-- Marché : ordres multi-objets, lignes indépendantes, dépôt en séquestre.
--
-- Dépendances attendues avant cette migration :
--   objets_dispo(objet_id, type, est_empilable, prix_base, prix_marche)
--   stuff(stuff_id, account_id, objet_id, stack_key, quantity, rarete, rang)
--   accounts(account_id)
--   wallets(account_id, balance)
--   equipment(equipment_id, stuff_id, durability, durability_max)
--   equipment_enchantments(equipment_id, enchantment_id, enchantment_level)
--   potions(potion_id, stuff_id, effect, potency, duration)
--   enchanted_books(book_id, stuff_id, book_level)
--   book_enchantments(book_id, enchantment_id, enchantment_level)
--   enchantments(enchantment_id)
--
-- IMPORTANT :
-- - Cette migration ne crée/modifie PAS stuff.visible. Le code Rust devra gérer
--   la visibilité de l'inventaire lors du dépôt, de l'annulation et de la vente.
-- - Les fonds sont réservés/libérés par le serveur dans la même transaction SQL
--   que les modifications du marché et du portefeuille.
-- - Tous les types d'objets sont échangeables (munitions comprises, traitées comme des objets de base).
-- - Les objets de base (minerais, nourriture, matériaux...) n'ont PAS de variante :
--   leurs lignes ont variante_id NULL et s'apparient sur l'objet seul.
--   Armes, équipements, livres enchantés et potions ont une variante.
-- - Une variante est identifiée par objet + attributs + signature canonique.
--   La signature doit être générée côté Rust avec les enchantements triés par
--   enchantment_id et leur niveau. L'ordre d'affichage n'a aucune importance.
-- ============================================================================

CREATE TABLE IF NOT EXISTS variantes_marche (
    variante_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    objet_id          INTEGER NOT NULL,
    rarete            TEXT,
    rang              TEXT,
    book_level        INTEGER,
    signature         TEXT NOT NULL,
    creee_le          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (objet_id) REFERENCES objets_dispo(objet_id) ON DELETE RESTRICT,
    UNIQUE (objet_id, signature),
    UNIQUE (variante_id, objet_id),
    CHECK (length(trim(signature)) > 0),
    CHECK (book_level IS NULL OR book_level BETWEEN 1 AND 6)
);

CREATE TABLE IF NOT EXISTS variante_enchantements (
    variante_id       INTEGER NOT NULL,
    enchantment_id    INTEGER NOT NULL,
    enchantment_level INTEGER NOT NULL,

    PRIMARY KEY (variante_id, enchantment_id),
    FOREIGN KEY (variante_id) REFERENCES variantes_marche(variante_id) ON DELETE CASCADE,
    FOREIGN KEY (enchantment_id) REFERENCES enchantments(enchantment_id) ON DELETE RESTRICT,
    CHECK (enchantment_level BETWEEN 1 AND 6)
);

-- En-têtes : une commande peut contenir plusieurs lignes.
CREATE TABLE IF NOT EXISTS ordres_achat (
    ordre_achat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id     INTEGER NOT NULL,
    statut         TEXT NOT NULL DEFAULT 'actif',
    cree_le        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modifie_le     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    CHECK (statut IN ('actif', 'partiel', 'execute', 'annule'))
);

CREATE TABLE IF NOT EXISTS ordres_vente (
    ordre_vente_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id     INTEGER NOT NULL,
    statut         TEXT NOT NULL DEFAULT 'actif',
    cree_le        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modifie_le     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    CHECK (statut IN ('actif', 'partiel', 'execute', 'annule'))
);

-- Une ligne d'achat porte son propre prix plafond et ses propres critères.
-- Armes, équipements, livres et potions : variante_id + objet_id identifient la variante.
-- Objets de base : variante_id est NULL.
-- Les critères de potion (effet, puissance, durée) filtrent en plus de la variante.
CREATE TABLE IF NOT EXISTS lignes_achat (
    ligne_achat_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ordre_achat_id          INTEGER NOT NULL,
    objet_id                INTEGER NOT NULL,
    variante_id             INTEGER,
    quantite_initiale       INTEGER NOT NULL,
    quantite_restante       INTEGER NOT NULL,
    prix_unitaire_max       INTEGER NOT NULL,
    montant_reserve_initial INTEGER NOT NULL,
    montant_reserve_restant INTEGER NOT NULL,

    -- Critères facultatifs réservés aux potions (filtres en plus de la variante).
    potion_effect           TEXT,
    potency_exact           INTEGER,
    potency_min             INTEGER,
    duration_exact          INTEGER,
    duration_min            INTEGER,

    -- Filtres de durabilité pour les armes et équipements (hors identité de variante).
    durability_min           INTEGER,
    durability_max           INTEGER,

    statut                  TEXT NOT NULL DEFAULT 'actif',
    creee_le                TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ordre_achat_id) REFERENCES ordres_achat(ordre_achat_id) ON DELETE CASCADE,
    FOREIGN KEY (objet_id) REFERENCES objets_dispo(objet_id) ON DELETE RESTRICT,
    FOREIGN KEY (variante_id, objet_id)
        REFERENCES variantes_marche(variante_id, objet_id) ON DELETE RESTRICT,

    CHECK (quantite_initiale > 0),
    CHECK (quantite_restante BETWEEN 0 AND quantite_initiale),
    CHECK (prix_unitaire_max > 0),
    CHECK (montant_reserve_initial = quantite_initiale * prix_unitaire_max),
    CHECK (montant_reserve_restant BETWEEN 0 AND montant_reserve_initial),
    CHECK (potency_exact IS NULL OR potency_exact >= 0),
    CHECK (potency_min IS NULL OR potency_min >= 0),
    CHECK (duration_exact IS NULL OR duration_exact >= 0),
    CHECK (duration_min IS NULL OR duration_min >= 0),
    CHECK (durability_min IS NULL OR durability_min >= 0),
    CHECK (durability_max IS NULL OR durability_max >= 0),
    CHECK (durability_min IS NULL OR durability_max IS NULL OR durability_min <= durability_max),
    CHECK (potency_exact IS NULL OR potency_min IS NULL),
    CHECK (duration_exact IS NULL OR duration_min IS NULL),
    CHECK (statut IN ('actif', 'partiel', 'execute', 'annule'))
);

-- Stock déposé : chaque exemplaire non empilable possède sa propre ligne.
-- Pour un objet empilable, stuff.quantity représente la quantité encore en stock.
CREATE TABLE IF NOT EXISTS stock_marche (
    stock_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stuff_id          INTEGER NOT NULL UNIQUE,
    vendeur_id        INTEGER NOT NULL,
    quantite_deposee  INTEGER NOT NULL,
    quantite_restante INTEGER NOT NULL,
    statut            TEXT NOT NULL DEFAULT 'disponible',
    depose_le         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modifie_le        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stuff_id) REFERENCES stuff(stuff_id) ON DELETE RESTRICT,
    FOREIGN KEY (vendeur_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    CHECK (quantite_deposee > 0),
    CHECK (quantite_restante BETWEEN 0 AND quantite_deposee),
    CHECK (statut IN ('disponible', 'partiel', 'vendu', 'annule'))
);

-- Une ligne de vente correspond à un dépôt précis et possède son propre prix.
-- Pour les objets non empilables, le dépôt et la ligne ont une quantité de 1.
CREATE TABLE IF NOT EXISTS lignes_vente (
    ligne_vente_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    ordre_vente_id    INTEGER NOT NULL,
    stock_id          INTEGER NOT NULL UNIQUE,
    objet_id          INTEGER NOT NULL,
    variante_id       INTEGER,
    quantite_initiale INTEGER NOT NULL,
    quantite_restante INTEGER NOT NULL,
    prix_unitaire     INTEGER NOT NULL,
    statut            TEXT NOT NULL DEFAULT 'actif',
    creee_le          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ordre_vente_id) REFERENCES ordres_vente(ordre_vente_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stock_marche(stock_id) ON DELETE RESTRICT,
    FOREIGN KEY (objet_id) REFERENCES objets_dispo(objet_id) ON DELETE RESTRICT,
    FOREIGN KEY (variante_id, objet_id)
        REFERENCES variantes_marche(variante_id, objet_id) ON DELETE RESTRICT,

    CHECK (quantite_initiale > 0),
    CHECK (quantite_restante BETWEEN 0 AND quantite_initiale),
    CHECK (prix_unitaire > 0),
    CHECK (statut IN ('actif', 'partiel', 'execute', 'annule'))
);

-- Historique : chaque transaction relie une ligne d'achat à une ligne de vente.
-- stuff_id conserve la trace de l'exemplaire transféré (ou de l'exemplaire source
-- pour une pile partiellement divisée). Les détails de la transaction restent
-- disponibles même si l'objet est ensuite consommé/supprimé.
CREATE TABLE IF NOT EXISTS transactions_marche (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ligne_achat_id INTEGER NOT NULL,
    ligne_vente_id INTEGER NOT NULL,
    stuff_id       INTEGER,
    acheteur_id    INTEGER NOT NULL,
    vendeur_id     INTEGER NOT NULL,
    objet_id       INTEGER NOT NULL,
    variante_id    INTEGER,
    quantite       INTEGER NOT NULL,
    prix_unitaire  INTEGER NOT NULL,
    prix_total     INTEGER NOT NULL,
    effectuee_le   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ligne_achat_id) REFERENCES lignes_achat(ligne_achat_id) ON DELETE RESTRICT,
    FOREIGN KEY (ligne_vente_id) REFERENCES lignes_vente(ligne_vente_id) ON DELETE RESTRICT,
    FOREIGN KEY (stuff_id) REFERENCES stuff(stuff_id) ON DELETE SET NULL,
    FOREIGN KEY (acheteur_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    FOREIGN KEY (vendeur_id) REFERENCES accounts(account_id) ON DELETE RESTRICT,
    FOREIGN KEY (objet_id) REFERENCES objets_dispo(objet_id) ON DELETE RESTRICT,
    FOREIGN KEY (variante_id, objet_id)
        REFERENCES variantes_marche(variante_id, objet_id) ON DELETE RESTRICT,

    CHECK (quantite > 0),
    CHECK (prix_unitaire > 0),
    CHECK (prix_total = quantite * prix_unitaire)
);

-- ============================================================================
-- Contrôles à l'insertion
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS verifier_variante_marche_insert
BEFORE INSERT ON variantes_marche
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type IN ('armes', 'equipment', 'enchanted_book', 'potion')
        )
        THEN RAISE(ABORT, 'Type objet interdit ou non compatible avec une variante de marché')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type = 'enchanted_book'
              AND (NEW.book_level IS NULL OR NEW.rarete IS NOT NULL OR NEW.rang IS NOT NULL)
        )
        THEN RAISE(ABORT, 'Une variante de livre doit avoir book_level et aucune rarete/rang')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type <> 'enchanted_book'
              AND NEW.book_level IS NOT NULL
        )
        THEN RAISE(ABORT, 'book_level est réservé aux livres enchantés')
    END;
END;

CREATE TRIGGER IF NOT EXISTS verifier_ligne_achat_insert
BEFORE INSERT ON lignes_achat
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
        )
        THEN RAISE(ABORT, 'Objet inconnu')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type IN ('armes', 'equipment', 'enchanted_book', 'potion')
        ) AND NEW.variante_id IS NULL
        THEN RAISE(ABORT, 'Une ligne d achat doit préciser sa variante')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type NOT IN ('armes', 'equipment', 'enchanted_book', 'potion')
        ) AND NEW.variante_id IS NOT NULL
        THEN RAISE(ABORT, 'Les objets de base n ont pas de variante')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type <> 'potion'
              AND (NEW.potion_effect IS NOT NULL
                   OR NEW.potency_exact IS NOT NULL OR NEW.potency_min IS NOT NULL
                   OR NEW.duration_exact IS NOT NULL OR NEW.duration_min IS NOT NULL)
        )
        THEN RAISE(ABORT, 'Les critères de potion sont réservés aux potions')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM objets_dispo o
            WHERE o.objet_id = NEW.objet_id
              AND o.type NOT IN ('armes', 'equipment')
              AND (NEW.durability_min IS NOT NULL OR NEW.durability_max IS NOT NULL)
        )
        THEN RAISE(ABORT, 'Les filtres de durabilité sont réservés aux armes et équipements')
    END;
END;

CREATE TRIGGER IF NOT EXISTS verifier_stock_marche_insert
BEFORE INSERT ON stock_marche
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE s.stuff_id = NEW.stuff_id
              AND s.account_id = NEW.vendeur_id
              AND s.quantity = NEW.quantite_deposee
        )
        THEN RAISE(ABORT, 'Dépôt invalide : propriétaire ou quantité incorrecte')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE s.stuff_id = NEW.stuff_id
              AND o.est_empilable = 0
              AND NEW.quantite_deposee <> 1
        )
        THEN RAISE(ABORT, 'Un objet non empilable doit être déposé individuellement')
    END;
END;

CREATE TRIGGER IF NOT EXISTS verifier_ligne_vente_insert
BEFORE INSERT ON lignes_vente
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM stock_marche sm
            JOIN stuff s ON s.stuff_id = sm.stuff_id
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE sm.stock_id = NEW.stock_id
              AND sm.vendeur_id = (
                  SELECT ov.account_id FROM ordres_vente ov
                  WHERE ov.ordre_vente_id = NEW.ordre_vente_id
              )
              AND s.objet_id = NEW.objet_id
              AND sm.statut = 'disponible'
              AND sm.quantite_restante = NEW.quantite_initiale
              AND s.quantity = NEW.quantite_initiale
        )
        THEN RAISE(ABORT, 'Ligne de vente incompatible avec le dépôt ou le vendeur')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            JOIN stock_marche sm ON sm.stuff_id = s.stuff_id
            WHERE sm.stock_id = NEW.stock_id
              AND o.type NOT IN ('armes', 'equipment', 'enchanted_book', 'potion')
              AND NEW.variante_id IS NOT NULL
        )
        THEN RAISE(ABORT, 'Les objets de base n ont pas de variante')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            JOIN stock_marche sm ON sm.stuff_id = s.stuff_id
            WHERE sm.stock_id = NEW.stock_id
              AND o.type IN ('armes', 'equipment', 'enchanted_book', 'potion')
              AND NEW.variante_id IS NULL
        )
        THEN RAISE(ABORT, 'Une vente doit préciser sa variante (hors objets de base)')
    END;

    SELECT CASE
        WHEN NEW.variante_id IS NOT NULL
         AND NOT EXISTS (
            SELECT 1
            FROM stock_marche sm
            JOIN stuff s ON s.stuff_id = sm.stuff_id
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            JOIN variantes_marche vm ON vm.variante_id = NEW.variante_id
            WHERE sm.stock_id = NEW.stock_id
              AND vm.objet_id = s.objet_id
              AND vm.rarete IS s.rarete
              AND vm.rang IS s.rang
              AND (
                  (o.type = 'enchanted_book'
                   AND vm.book_level = (SELECT eb.book_level FROM enchanted_books eb WHERE eb.stuff_id = s.stuff_id)
                   AND NOT EXISTS (
                       SELECT 1 FROM variante_enchantements ve
                       LEFT JOIN enchanted_books eb ON eb.stuff_id = s.stuff_id
                       LEFT JOIN book_enchantments be
                         ON be.book_id = eb.book_id
                        AND be.enchantment_id = ve.enchantment_id
                       WHERE ve.variante_id = vm.variante_id
                         AND (be.enchantment_id IS NULL OR be.enchantment_level <> ve.enchantment_level)
                   )
                   AND NOT EXISTS (
                       SELECT 1 FROM enchanted_books eb
                       JOIN book_enchantments be ON be.book_id = eb.book_id
                       LEFT JOIN variante_enchantements ve
                         ON ve.variante_id = vm.variante_id
                        AND ve.enchantment_id = be.enchantment_id
                       WHERE eb.stuff_id = s.stuff_id
                         AND (ve.enchantment_id IS NULL OR ve.enchantment_level <> be.enchantment_level)
                   ))
                  OR
                  (o.type IN ('equipment', 'armes')
                   AND EXISTS (SELECT 1 FROM equipment e WHERE e.stuff_id = s.stuff_id)
                   AND NOT EXISTS (
                       SELECT 1 FROM variante_enchantements ve
                       JOIN equipment e ON e.stuff_id = s.stuff_id
                       LEFT JOIN equipment_enchantments ee
                         ON ee.equipment_id = e.equipment_id
                        AND ee.enchantment_id = ve.enchantment_id
                       WHERE ve.variante_id = vm.variante_id
                         AND (ee.enchantment_id IS NULL OR ee.enchantment_level <> ve.enchantment_level)
                   )
                   AND NOT EXISTS (
                       SELECT 1 FROM equipment e
                       JOIN equipment_enchantments ee ON ee.equipment_id = e.equipment_id
                       LEFT JOIN variante_enchantements ve
                         ON ve.variante_id = vm.variante_id
                        AND ve.enchantment_id = ee.enchantment_id
                       WHERE e.stuff_id = s.stuff_id
                         AND (ve.enchantment_id IS NULL OR ve.enchantment_level <> ee.enchantment_level)
                   ))
                  OR
                  (o.type NOT IN ('enchanted_book', 'equipment', 'armes')
                   AND vm.book_level IS NULL
                   AND NOT EXISTS (SELECT 1 FROM variante_enchantements ve WHERE ve.variante_id = vm.variante_id))
              )
         )
        THEN RAISE(ABORT, 'La variante ne correspond pas aux attributs ou enchantements de l exemplaire')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM stock_marche sm
            JOIN stuff s ON s.stuff_id = sm.stuff_id
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE sm.stock_id = NEW.stock_id
              AND o.est_empilable = 0
              AND NEW.quantite_initiale <> 1
        )
        THEN RAISE(ABORT, 'Un objet non empilable doit avoir une ligne de vente de quantité 1')
    END;
END;

-- Vérifie qu'une transaction est possible avant de l'inscrire à l'historique.
CREATE TRIGGER IF NOT EXISTS verifier_transaction_marche
BEFORE INSERT ON transactions_marche
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM lignes_achat la
            JOIN ordres_achat oa ON oa.ordre_achat_id = la.ordre_achat_id
            JOIN lignes_vente lv ON lv.ligne_vente_id = NEW.ligne_vente_id
            JOIN ordres_vente ov ON ov.ordre_vente_id = lv.ordre_vente_id
            JOIN stock_marche sm ON sm.stock_id = lv.stock_id
            JOIN stuff s ON s.stuff_id = sm.stuff_id
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            LEFT JOIN variantes_marche vm_achat ON vm_achat.variante_id = la.variante_id
            LEFT JOIN variantes_marche vm_vente ON vm_vente.variante_id = lv.variante_id
            WHERE la.ligne_achat_id = NEW.ligne_achat_id
              AND oa.statut IN ('actif', 'partiel')
              AND ov.statut IN ('actif', 'partiel')
              AND la.statut IN ('actif', 'partiel')
              AND lv.statut IN ('actif', 'partiel')
              AND sm.statut IN ('disponible', 'partiel')
              AND la.quantite_restante >= NEW.quantite
              AND lv.quantite_restante >= NEW.quantite
              AND la.prix_unitaire_max >= NEW.prix_unitaire
              AND NEW.prix_total = NEW.quantite * NEW.prix_unitaire
              AND NEW.acheteur_id = oa.account_id
              AND NEW.vendeur_id = ov.account_id
              AND NEW.vendeur_id = sm.vendeur_id
              AND NEW.objet_id = s.objet_id
              AND NEW.objet_id = la.objet_id
              AND NEW.stuff_id = s.stuff_id
              AND (
                    -- Objet de base : aucune variante, appariement sur l'objet.
                    (o.type NOT IN ('armes', 'equipment', 'enchanted_book', 'potion')
                     AND la.variante_id IS NULL
                     AND lv.variante_id IS NULL
                     AND NEW.variante_id IS NULL)
                    OR
                    -- Armes, équipements, livres, potions : même variante.
                    (o.type IN ('armes', 'equipment', 'enchanted_book', 'potion')
                     AND la.variante_id IS NOT NULL
                     AND lv.variante_id IS NOT NULL
                     AND la.variante_id = lv.variante_id
                     AND NEW.variante_id = lv.variante_id
                     AND vm_achat.objet_id = NEW.objet_id
                     AND vm_vente.objet_id = NEW.objet_id
                     AND (o.type <> 'potion' OR (
                         EXISTS (SELECT 1 FROM potions p WHERE p.stuff_id = s.stuff_id)
                         AND (la.potion_effect IS NULL OR la.potion_effect = (
                             SELECT p.effect FROM potions p WHERE p.stuff_id = s.stuff_id
                         ))
                         AND (la.potency_exact IS NULL OR la.potency_exact = (
                             SELECT p.potency FROM potions p WHERE p.stuff_id = s.stuff_id
                         ))
                         AND (la.potency_min IS NULL OR (
                             SELECT p.potency FROM potions p WHERE p.stuff_id = s.stuff_id
                         ) >= la.potency_min)
                         AND (la.duration_exact IS NULL OR la.duration_exact = (
                             SELECT p.duration FROM potions p WHERE p.stuff_id = s.stuff_id
                         ))
                         AND (la.duration_min IS NULL OR (
                             SELECT p.duration FROM potions p WHERE p.stuff_id = s.stuff_id
                         ) >= la.duration_min)))
                     AND (o.type NOT IN ('equipment', 'armes') OR EXISTS (
                         SELECT 1 FROM equipment e
                         WHERE e.stuff_id = s.stuff_id
                           AND (la.durability_min IS NULL OR e.durability >= la.durability_min)
                           AND (la.durability_max IS NULL OR e.durability <= la.durability_max)
                     )))
              )
        )
        THEN RAISE(ABORT, 'Transaction de marché incompatible avec les lignes ou critères')
    END;

    SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM stuff s
            JOIN objets_dispo o ON o.objet_id = s.objet_id
            WHERE s.stuff_id = NEW.stuff_id
              AND o.est_empilable = 0
              AND NEW.quantite <> 1
        )
        THEN RAISE(ABORT, 'Un exemplaire non empilable se vend par unité')
    END;
END;

-- ============================================================================
-- Mise à jour des quantités et transfert de propriété après transaction.
-- La visibilité de l'inventaire n'est volontairement pas touchée ici.
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS maj_marche_apres_transaction
AFTER INSERT ON transactions_marche
BEGIN
    UPDATE lignes_achat
       SET quantite_restante = quantite_restante - NEW.quantite,
           montant_reserve_restant = montant_reserve_restant
               - (NEW.quantite * prix_unitaire_max),
           statut = CASE
               WHEN quantite_restante - NEW.quantite = 0 THEN 'execute'
               ELSE 'partiel'
           END
     WHERE ligne_achat_id = NEW.ligne_achat_id;

    UPDATE lignes_vente
       SET quantite_restante = quantite_restante - NEW.quantite,
           statut = CASE
               WHEN quantite_restante - NEW.quantite = 0 THEN 'execute'
               ELSE 'partiel'
           END
     WHERE ligne_vente_id = NEW.ligne_vente_id;

    UPDATE stock_marche
       SET quantite_restante = quantite_restante - NEW.quantite,
           statut = CASE
               WHEN quantite_restante - NEW.quantite = 0 THEN 'vendu'
               ELSE 'partiel'
           END,
           modifie_le = CURRENT_TIMESTAMP
     WHERE stock_id = (
         SELECT stock_id FROM lignes_vente WHERE ligne_vente_id = NEW.ligne_vente_id
     );

    -- Si toute la pile est vendue, ou si l'objet est non empilable, on
    -- transfère d'abord l'exemplaire existant sans recréer ses sous-types.
    -- Cet ordre est important : le test porte sur la quantité AVANT transfert.
    UPDATE stuff
       SET account_id = NEW.acheteur_id,
           stack_key = 'market-tx-' || NEW.transaction_id
     WHERE stuff_id = NEW.stuff_id
       AND (
           quantity = NEW.quantite
           OR EXISTS (
               SELECT 1 FROM objets_dispo o
               WHERE o.objet_id = stuff.objet_id
                 AND o.est_empilable = 0
           )
       );

    -- Pile partiellement vendue : crée une nouvelle ligne d'inventaire chez
    -- l'acheteur et réduit la pile restée en séquestre.
    -- Après le transfert complet ci-dessus, cette condition n'est vraie que
    -- pour une pile dont une partie reste encore en stock.
    INSERT INTO stuff (account_id, objet_id, stack_key, quantity, rarete, rang)
    SELECT NEW.acheteur_id,
           s.objet_id,
           'market-tx-' || NEW.transaction_id,
           NEW.quantite,
           s.rarete,
           s.rang
      FROM stuff s
      JOIN objets_dispo o ON o.objet_id = s.objet_id
     WHERE s.stuff_id = NEW.stuff_id
       AND o.est_empilable = 1
       AND s.quantity > NEW.quantite;

    UPDATE stuff
       SET quantity = quantity - NEW.quantite
     WHERE stuff_id = NEW.stuff_id
       AND EXISTS (
           SELECT 1 FROM objets_dispo o
           WHERE o.objet_id = stuff.objet_id
             AND o.est_empilable = 1
       )
       AND quantity > NEW.quantite;

    UPDATE ordres_achat
       SET statut = CASE
           WHEN NOT EXISTS (
               SELECT 1 FROM lignes_achat la
               WHERE la.ordre_achat_id = ordres_achat.ordre_achat_id
                 AND la.quantite_restante > 0
                 AND la.statut <> 'annule'
           ) THEN 'execute'
           WHEN EXISTS (
               SELECT 1 FROM lignes_achat la
               WHERE la.ordre_achat_id = ordres_achat.ordre_achat_id
                 AND la.quantite_restante < la.quantite_initiale
           ) THEN 'partiel'
           ELSE 'actif'
       END,
       modifie_le = CURRENT_TIMESTAMP
     WHERE ordre_achat_id = (
         SELECT ordre_achat_id FROM lignes_achat WHERE ligne_achat_id = NEW.ligne_achat_id
     );

    UPDATE ordres_vente
       SET statut = CASE
           WHEN NOT EXISTS (
               SELECT 1 FROM lignes_vente lv
               WHERE lv.ordre_vente_id = ordres_vente.ordre_vente_id
                 AND lv.quantite_restante > 0
                 AND lv.statut <> 'annule'
           ) THEN 'execute'
           WHEN EXISTS (
               SELECT 1 FROM lignes_vente lv
               WHERE lv.ordre_vente_id = ordres_vente.ordre_vente_id
                 AND lv.quantite_restante < lv.quantite_initiale
           ) THEN 'partiel'
           ELSE 'actif'
       END,
       modifie_le = CURRENT_TIMESTAMP
     WHERE ordre_vente_id = (
         SELECT ordre_vente_id FROM lignes_vente WHERE ligne_vente_id = NEW.ligne_vente_id
     );
END;

-- Empêche de modifier les quantités d'une ligne autrement que par le mécanisme
-- de transaction (l'application peut toujours annuler explicitement une ligne).
CREATE TRIGGER IF NOT EXISTS verifier_quantite_ligne_achat_update
BEFORE UPDATE OF quantite_restante ON lignes_achat
WHEN NEW.quantite_restante > OLD.quantite_restante
BEGIN
    SELECT RAISE(ABORT, 'La quantité restante d achat ne peut pas augmenter');
END;

CREATE TRIGGER IF NOT EXISTS verifier_quantite_ligne_vente_update
BEFORE UPDATE OF quantite_restante ON lignes_vente
WHEN NEW.quantite_restante > OLD.quantite_restante
BEGIN
    SELECT RAISE(ABORT, 'La quantité restante de vente ne peut pas augmenter');
END;

-- ============================================================================
-- Index utiles aux recherches et au rapprochement des ordres.
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_variantes_marche_objet
    ON variantes_marche(objet_id);

CREATE INDEX IF NOT EXISTS idx_variante_enchantements_enchantement
    ON variante_enchantements(enchantment_id);

CREATE INDEX IF NOT EXISTS idx_lignes_achat_recherche
    ON lignes_achat(objet_id, variante_id, durability_min, durability_max,
                    prix_unitaire_max DESC, creee_le)
    WHERE statut IN ('actif', 'partiel');

CREATE INDEX IF NOT EXISTS idx_lignes_achat_potions
    ON lignes_achat(objet_id, potion_effect, potency_exact, potency_min,
                    duration_exact, duration_min)
    WHERE statut IN ('actif', 'partiel');

CREATE INDEX IF NOT EXISTS idx_lignes_vente_recherche
    ON lignes_vente(objet_id, variante_id, prix_unitaire ASC, creee_le)
    WHERE statut IN ('actif', 'partiel');

CREATE INDEX IF NOT EXISTS idx_stock_marche_vendeur_statut
    ON stock_marche(vendeur_id, statut);

CREATE INDEX IF NOT EXISTS idx_transactions_marche_date
    ON transactions_marche(effectuee_le DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_marche_objet_date
    ON transactions_marche(objet_id, effectuee_le DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_marche_lignes
    ON transactions_marche(ligne_achat_id, ligne_vente_id);

-- Note pour Rust : le prix indicatif pourra être calculé à partir des
-- transactions récentes (moyenne pondérée par quantite). En l'absence de ventes,
-- utiliser la valeur théorique du catalogue. L'arrondi mathématique doit être
-- appliqué côté Rust : floor(moyenne + 0.5) pour des montants positifs.
