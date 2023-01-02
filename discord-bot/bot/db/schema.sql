-- Sqlite3 schema for the bot
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT NOT NULL PRIMARY KEY,
    log_channel_id BIGINT
);

CREATE TABLE IF NOT EXISTS perf_info (
    id INTEGER PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    uptime TEXT,
    cpu_time TEXT,
    mem_usage REAL,
    mem_total REAL,
    pct_mem_usage REAL,
    api_calls INTEGER
);
