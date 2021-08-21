greenhouse_schema = """
CREATE TABLE IF NOT EXISTS greenhouse (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    serial TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uk_greenhouse_serial ON greenhouse(serial);
"""

sample_schema = """
CREATE TABLE IF NOT EXISTS sample (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    humidity REAL NOT NULL CHECK(humidity >= 0),
    temperature REAL NOT NULL CHECK(temperature >= 0),
    humidifier_state INTEGER NOT NULL,
    fan_state INTEGER NOT NULL,
    lights_state INTEGER NOT NULL,
    greenhouse_id INTEGER NOT NULL,
    FOREIGN KEY(greenhouse_id) REFERENCES greenhouse(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_sample_created ON sample(created);
CREATE INDEX IF NOT EXISTS fk_sample_greenhouse_id ON sample(greenhouse_id);
"""

schemas = (
    greenhouse_schema,
    sample_schema
)
