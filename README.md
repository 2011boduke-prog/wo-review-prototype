# wo-review-prototype

A minimal work-order review tool: ingest raw WOs, run NLP entity extraction, search & review via a FastAPI backend + React frontend.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, SQLite |
| NLP | spaCy `en_core_web_sm` + custom regex rules |
| Frontend | React (create-react-app), Node 18 |
| CI | GitHub Actions |

---

## One-Command Quick Start (after prerequisites)

```bash
# Clone and enter directory
git clone https://github.com/2011boduke-prog/wo-review-prototype.git
cd wo-review-prototype

# 1. Create Python virtual environment and install deps
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r backend/requirements.txt

# 2. Download spaCy model
python -m spacy download en_core_web_sm

# 3. Ingest sample work orders into SQLite
python backend/ingest_load.py

# 4. Run NLP extraction pipeline
python nlp/ner_pipeline.py

# 5. Start the FastAPI backend (http://localhost:8000)
uvicorn backend.api:app --reload

# 6. In a new terminal — install & start the React frontend (http://localhost:3000)
cd ui
npm install
npm start
```

---

## VS Code Tasks (Ctrl+Shift+P → "Tasks: Run Task")

| Task | What it does |
|------|-------------|
| Create venv | `python -m venv .venv` |
| Install Python deps | `pip install -r backend/requirements.txt` |
| Ingest data | `python backend/ingest_load.py` |
| Run NLP pipeline | `python nlp/ner_pipeline.py` |
| Run Backend | `uvicorn backend.api:app --reload` |
| Run Frontend | `cd ui && npm start` |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search?q=&asset=&wo=&limit=25` | Full-text search across work orders |
| GET | `/work_order/{wo}` | Fetch a single work order |
| POST | `/work_order/{wo}/update` | Persist corrected fields |

---

## Project Structure

```
wo-review-prototype/
├── .github/workflows/ci.yml   # GitHub Actions CI
├── .vscode/                   # VS Code tasks & launch configs
├── data/work_orders.json      # Sample work orders (6 WOs)
├── backend/
│   ├── requirements.txt
│   ├── ingest_load.py         # Load JSON → SQLite
│   └── api.py                 # FastAPI app
├── nlp/
│   ├── ner_pipeline.py        # spaCy + regex entity extraction
│   └── extracted_sample.json  # Extraction output for sample WOs
├── models.sql                 # Reference DDL
├── ui/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js
│       └── components/
│           ├── SearchBar.js
│           ├── ResultsList.js
│           └── WOEditor.js
└── LICENSE
```

---

## License

MIT — see [LICENSE](LICENSE).
