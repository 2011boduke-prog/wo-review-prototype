"""
api.py — FastAPI application for work-order search and review.

Run:
    uvicorn backend.api:app --reload
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = Path(__file__).parent.parent / "work_orders.db"

app = FastAPI(title="WO Review API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Database not found. Run backend/ingest_load.py first.",
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for field in ("extracted", "corrections"):
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except json.JSONDecodeError:
                pass
    return d


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UpdatePayload(BaseModel):
    corrected_fields: Optional[dict] = None
    approved: Optional[bool] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
def search(
    q: str = Query("", description="Free-text search"),
    asset: str = Query("", description="Filter by asset ID"),
    wo: str = Query("", description="Filter by WO number"),
    limit: int = Query(25, ge=1, le=200),
) -> List[dict]:
    """Search work orders by free text, asset, or WO number."""
    conn = _get_conn()
    try:
        clauses = []
        params: list = []

        if q:
            pattern = f"%{q}%"
            clauses.append(
                "(wo LIKE ? OR asset LIKE ? OR description LIKE ? "
                "OR raw_text LIKE ? OR technician LIKE ? OR location LIKE ?)"
            )
            params.extend([pattern] * 6)

        if asset:
            clauses.append("asset LIKE ?")
            params.append(f"%{asset}%")

        if wo:
            clauses.append("wo LIKE ?")
            params.append(f"%{wo}%")

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM work_orders {where} LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/work_order/{wo_id}")
def get_work_order(wo_id: str) -> dict:
    """Fetch a single work order by WO number."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM work_orders WHERE wo = ?", (wo_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"WO {wo_id!r} not found")
        return _row_to_dict(row)
    finally:
        conn.close()


@app.post("/work_order/{wo_id}/update")
def update_work_order(wo_id: str, payload: UpdatePayload) -> dict:
    """Persist corrected fields or approval status for a work order."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT wo FROM work_orders WHERE wo = ?", (wo_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"WO {wo_id!r} not found")

        updates = {}
        if payload.corrected_fields is not None:
            updates["corrections"] = json.dumps(payload.corrected_fields)
        if payload.approved is not None:
            updates["approved"] = 1 if payload.approved else 0

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE work_orders SET {set_clause} WHERE wo = ?",
                list(updates.values()) + [wo_id],
            )
            conn.commit()

        updated = conn.execute(
            "SELECT * FROM work_orders WHERE wo = ?", (wo_id,)
        ).fetchone()
        return _row_to_dict(updated)
    finally:
        conn.close()
