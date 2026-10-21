CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id TEXT NOT NULL,

    account_name TEXT NOT NULL UNIQUE,

    role_id INTEGER NOT NULL,
    
    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS wallets (
    account_id INTEGER PRIMARY KEY,

    balance INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    CHECK (balance >= 0)
);
