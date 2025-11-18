-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS ideas;
DROP TABLE IF EXISTS missions;

CREATE TABLE ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  goal TEXT NOT NULL
);

CREATE TABLE missions (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    clarified_goal TEXT,
    status TEXT NOT NULL,
    plan TEXT, -- Stored as a JSON string
    report TEXT
);