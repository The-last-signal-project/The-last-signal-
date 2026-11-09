CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'CONNECTED',
    pseudo TEXT 
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT
);
CREATE TRIGGER IF NOT EXISTS set_default_pseudo
AFTER INSERT ON users
FOR EACH ROW
WHEN NEW.pseudo IS NULL OR NEW.pseudo = ''
BEGIN
    UPDATE users
    SET pseudo = NEW.email
    WHERE user_id = NEW.user_id;
END;