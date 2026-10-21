CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,

    user_id TEXT NOT NULL,
    account_id INTEGER,

    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT,
    disconnect_reason TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE SET NULL
);
