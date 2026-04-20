"""
ingest_load.py — Read data/work_orders.json and upsert records into SQLite.

Usage:
    python backend/ingest_load.py
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "work_orders.db"
DATA_PATH = Path(__file__).parent.parent / "data" / "work_orders.json"

DDL = """
CREATE TABLE IF NOT EXISTS work_orders (
    wo          TEXT PRIMARY KEY,
    asset       TEXT,
    location    TEXT,
    priority    TEXT,
    status      TEXT,
    created_date TEXT,
    description TEXT,
    technician  TEXT,
    raw_text    TEXT,
    extracted   TEXT DEFAULT NULL,
    approved    INTEGER NOT NULL DEFAULT 0,
    corrections TEXT DEFAULT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ingest():
    with open(DATA_PATH, encoding="utf-8") as fh:
        records = json.load(fh)

    conn = get_connection()
    try:
        conn.execute(DDL)
        conn.commit()

        upsert_sql = """
            INSERT INTO work_orders
                (wo, asset, location, priority, status, created_date,
                 description, technician, raw_text)
            VALUES
                (:wo, :asset, :location, :priority, :status, :created_date,
                 :description, :technician, :raw_text)
            ON CONFLICT(wo) DO UPDATE SET
                asset        = excluded.asset,
                location     = excluded.location,
                priority     = excluded.priority,
                status       = excluded.status,
                created_date = excluded.created_date,
                description  = excluded.description,
                technician   = excluded.technician,
                raw_text     = excluded.raw_text
        """

        for rec in records:
            conn.execute(upsert_sql, rec)

        conn.commit()
        print(f"Ingested {len(records)} work orders into {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    ingest()
