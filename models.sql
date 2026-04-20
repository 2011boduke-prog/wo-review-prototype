-- models.sql — Reference DDL for work_orders.db (SQLite-compatible)
-- This file is for documentation only; ingest_load.py creates the schema.

CREATE TABLE IF NOT EXISTS work_orders (
    wo           TEXT PRIMARY KEY,          -- Work order number (e.g. WO-1001)
    asset        TEXT,                      -- Asset identifier (e.g. PUMP-A12)
    location     TEXT,                      -- Physical location
    priority     TEXT,                      -- Low | Medium | High | Critical
    status       TEXT,                      -- Open | In Progress | Completed | Pending
    created_date TEXT,                      -- ISO-8601 timestamp
    description  TEXT,                      -- Human-written work description
    technician   TEXT,                      -- Assigned technician name
    raw_text     TEXT,                      -- Verbatim text for NLP input
    extracted    TEXT DEFAULT NULL,         -- JSON extracted entities
    approved     INTEGER NOT NULL DEFAULT 0,-- 0 = unapproved, 1 = approved
    corrections  TEXT DEFAULT NULL          -- JSON corrected fields from reviewer
);

-- Optional FTS virtual table (SQLite FTS5)
-- CREATE VIRTUAL TABLE IF NOT EXISTS wo_fts USING fts5(
--     wo, asset, description, raw_text,
--     content='work_orders', content_rowid='rowid'
-- );
