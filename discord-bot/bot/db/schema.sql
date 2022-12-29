-- Sqlite3 schema for the bot
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT NOT NULL PRIMARY KEY,
    log_channel_id BIGINT
);

CREATE TABLE IF NOT EXISTS example (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL
);
