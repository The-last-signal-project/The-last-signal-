CREATE TABLE IF NOT EXISTS bansferme (
    user_id TEXT NOT NULL PRIMARY KEY,
    auteur TEXT,
    raison TEXT,
    date_ban TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_deban TEXT NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);
