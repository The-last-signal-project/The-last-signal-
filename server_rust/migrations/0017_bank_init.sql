-- Banque : prêts et investissements.
--
-- Les montants "illimités" (dette restante, capital investi) sont stockés en
-- TEXT sous forme de nombre décimal (ex: '184467440737095516150').
-- SQLite INTEGER est limité à i64 ; le TEXT n'a aucune limite de taille.
-- Les calculs se font en Rust avec num-bigint (BigUint).
-- Le CHECK garantit que le texte ne contient que des chiffres.

CREATE TABLE IF NOT EXISTS loans (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id   INTEGER NOT NULL,
    -- Montant reçu lors de l'emprunt (toujours <= i64::MAX : le wallet est en i64).
    principal    INTEGER NOT NULL CHECK (principal > 0),
    rate_percent INTEGER NOT NULL,
    -- Reste à payer (capital + intérêts) : illimité.
    amount_due   TEXT    NOT NULL
        CHECK (amount_due <> '' AND amount_due NOT GLOB '*[^0-9]*'),
    created_at   INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_loans_account
    ON loans (account_id);

CREATE TABLE IF NOT EXISTS investments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    -- Capital investi : illimité.
    principal  TEXT    NOT NULL
        CHECK (principal <> '' AND principal NOT GLOB '*[^0-9]*' AND principal <> '0'),
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    closed_at  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_investments_account
    ON investments (account_id);
