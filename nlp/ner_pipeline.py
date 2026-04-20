"""
ner_pipeline.py — spaCy + regex entity extraction for work orders.

Reads rows from work_orders.db, extracts entities, writes JSON back to the
`extracted` column, and also writes nlp/extracted_sample.json.

Usage:
    python nlp/ner_pipeline.py
"""

import json
import re
import sqlite3
from pathlib import Path

import spacy

DB_PATH = Path(__file__).parent.parent / "work_orders.db"
OUTPUT_PATHS = [
    Path(__file__).parent / "extracted_sample.json",
    Path(__file__).parent.parent / "backend" / "nlp" / "extracted_sample.json",
]

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
PART_RE = re.compile(
    r"\b([A-Z]{2,6}-[A-Z0-9]+-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b"
)
MEASUREMENT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mm|cm|m|in|ft|inH2O|PSI|psi|Nm|ft-lbs?|ml|L|"
    r"rpm|kPa|bar|°C|°F|%)\b",
    re.IGNORECASE,
)
FAILURE_CODE_RE = re.compile(r"\b(FC-[A-Z]+-\d+)\b")
ACTION_KEYWORDS = {
    "replace", "inspect", "clean", "lubricate", "check", "tighten",
    "install", "remove", "verify", "align", "repair", "test", "adjust",
    "upgrade", "drain", "flush", "calibrate",
}
SPECIAL_INST_RE = re.compile(
    r"(?:CAUTION|WARNING|NOTE|IMPORTANT)\s*:\s*([^.!?]+[.!?]?)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Extraction logic
# ---------------------------------------------------------------------------

def extract_entities(text: str, nlp) -> dict:
    doc = nlp(text)

    parts = [m.group(1) for m in PART_RE.finditer(text)]

    measurements = [
        {"value": m.group(1), "unit": m.group(2)}
        for m in MEASUREMENT_RE.finditer(text)
    ]

    failure_codes = [m.group(1) for m in FAILURE_CODE_RE.finditer(text)]

    actions = []
    for token in doc:
        lemma = token.lemma_.lower()
        if lemma in ACTION_KEYWORDS and token.pos_ == "VERB":
            actions.append(token.text.lower())

    special_instructions = [
        m.group(0).strip() for m in SPECIAL_INST_RE.finditer(text)
    ]

    spacy_entities = [
        {"text": ent.text, "label": ent.label_}
        for ent in doc.ents
    ]

    return {
        "parts": [{"value": p, "confidence": "medium"} for p in parts],
        "measurements": [
            {**m, "confidence": "medium"} for m in measurements
        ],
        "failure_codes": [
            {"value": fc, "confidence": "high"} for fc in failure_codes
        ],
        "actions": [
            {"value": a, "confidence": "low"} for a in sorted(set(actions))
        ],
        "special_instructions": [
            {"value": si, "confidence": "high"} for si in special_instructions
        ],
        "spacy_entities": spacy_entities,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_pipeline():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run backend/ingest_load.py first."
        )

    nlp = spacy.load("en_core_web_sm")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT wo, raw_text FROM work_orders").fetchall()
    results = []

    for row in rows:
        wo_id = row["wo"]
        raw_text = row["raw_text"] or ""
        entities = extract_entities(raw_text, nlp)
        extracted_json = json.dumps(entities)

        conn.execute(
            "UPDATE work_orders SET extracted = ? WHERE wo = ?",
            (extracted_json, wo_id),
        )

        results.append({"wo": wo_id, "raw_text": raw_text, "extracted": entities})
        print(f"  Processed {wo_id}: {len(entities['parts'])} parts, "
              f"{len(entities['measurements'])} measurements, "
              f"{len(entities['failure_codes'])} failure codes")

    conn.commit()
    conn.close()

    payload = json.dumps(results, indent=2)
    for output_path in OUTPUT_PATHS:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")

    print(f"\nExtraction complete. {len(results)} WOs processed.")
    for output_path in OUTPUT_PATHS:
        print(f"Results written to {output_path}")


if __name__ == "__main__":
    run_pipeline()
