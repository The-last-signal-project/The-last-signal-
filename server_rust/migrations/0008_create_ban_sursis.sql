CREATE TABLE IF NOT EXISTS banssursis (
    user_id TEXT NOT NULL PRIMARY KEY,
    auteur TEXT,
    raison TEXT,
    date_ban TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sursis INTEGER NOT NULL CHECK (sursis > 0),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);
