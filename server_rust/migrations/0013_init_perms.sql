INSERT INTO roles (role_name, description)
VALUES
    ('joueur', 'Joueur normal'),
    ('modo', 'Modérateur'),
    ('admin', 'Administrateur'),
    ('Dev', 'Développeur'),
    ('SuperDev', 'Développeur avec plus de perms');
  INSERT INTO permissions (permission_name, description)
VALUES
    ('accounts.read', 'Lire les comptes'),
    ('accounts.write', 'Modifier les comptes'),
    ('accounts.delete', 'delete accounts'),
    ('permissions.read', 'Lire les permissions'),
    ('permissions.write', 'Modifier les permissions'),
    ('roles.read', 'Lire les rôles'),
    ('roles.write', 'Modifier les rôles'),
    ('objets_dispo.read', 'Lire les objets disponibles'),
    ('objets_dispo.write', 'Modifier les objets disponible'),
    ('chat.acces', 'accès au chat'),
    ('chat.moderation', 'moderation du chat'),
    ('ban.proposition', 'proposition de ban'),
    ('ban.banir', 'bannissement d''un joueur'),
    ('signalement', 'signalement d''un joueur'),
    ('log.search', 'recherche dans les logs');

INSERT OR IGNORE INTO role_inheritance (
    role_id,
    parent_role_id
)
SELECT child.role_id, parent.role_id
FROM roles child
JOIN roles parent
WHERE child.role_name = 'modo'
  AND parent.role_name = 'joueur';

INSERT OR IGNORE INTO role_inheritance (
    role_id,
    parent_role_id
)
SELECT child.role_id, parent.role_id
FROM roles child
JOIN roles parent
WHERE child.role_name = 'admin'
  AND parent.role_name = 'modo';

INSERT OR IGNORE INTO role_inheritance (
    role_id,
    parent_role_id
)
SELECT child.role_id, parent.role_id
FROM roles child
JOIN roles parent
WHERE child.role_name = 'Dev'
  AND parent.role_name = 'admin';

INSERT OR IGNORE INTO role_inheritance (
    role_id,
    parent_role_id
)
SELECT child.role_id, parent.role_id
FROM roles child
JOIN roles parent
WHERE child.role_name = 'SuperDev'
  AND parent.role_name = 'Dev';
INSERT OR IGNORE INTO role_permissions (
    role_id,
    permission_id
)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p
WHERE r.role_name = 'joueur'
  AND p.permission_name IN (
      'chat.acces',
      'signalement'
  );
INSERT OR IGNORE INTO role_permissions (
    role_id,
    permission_id
)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p
WHERE r.role_name = 'modo'
  AND p.permission_name IN (
      'chat.moderation',
      'ban.proposition');
INSERT OR IGNORE INTO role_permissions (
    role_id,
    permission_id
)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p
WHERE r.role_name = 'admin'
  AND p.permission_name IN (
      'accounts.read',
      'accounts.write',
      'accounts.delete',
      'permissions.read',
      'permissions.write',
      'roles.read',
      'roles.write',
      'objets_dispo.read',
      'objets_dispo.write'
  );
INSERT OR IGNORE INTO role_permissions (
    role_id,
    permission_id
)
SELECT r.role_id, p.permission_id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'SuperDev';
INSERT OR IGNORE INTO role_permissions (
    role_id,
    permission_id
)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p
WHERE r.role_name = 'Dev'
  AND p.permission_name NOT IN (
      'accounts.delete',
      'roles.write',
      'log.search'
      
  );
CREATE VIEW IF NOT EXISTS effective_role_permissions AS

WITH RECURSIVE role_tree (
    role_id,
    inherited_role_id
) AS (

    -- Le rôle lui-même
    SELECT
        role_id,
        role_id
    FROM roles

    UNION

    -- Tous les parents, grands-parents, etc.
    SELECT
        rt.role_id,
        ri.parent_role_id
    FROM role_tree rt
    JOIN role_inheritance ri
        ON ri.role_id = rt.inherited_role_id
)

SELECT DISTINCT
    rt.role_id,
    p.permission_id,
    p.permission_name
FROM role_tree rt
JOIN role_permissions rp
    ON rp.role_id = rt.inherited_role_id
JOIN permissions p
    ON p.permission_id = rp.permission_id;